#!/usr/bin/env bash
# Atualização sem supervisão: espera o pipeline principal terminar, regenera
# todos os relatórios a partir dos dados novos, compara as métricas com o
# backup e para no prazo (padrão: 10:00 do dia seguinte).
#
# Uso: scripts/atualizacao_noturna.sh [PID_DO_PIPELINE] [PASTA_BACKUP] ["AAAA-MM-DD HH:MM"]
# Log: logs_atualizacao_noturna/AAAA-MM-DD_HHMM/execucao.log  e  RESUMO.md
# Não faz commit nem push: o resultado fica para revisão humana.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"
PID_PIPELINE="${1:-}"
BACKUP="${2:-}"
PRAZO="${3:-$(date -d 'tomorrow 10:00' '+%Y-%m-%d %H:%M')}"
FIM=$(date -d "$PRAZO" +%s)
DIR="logs_atualizacao_noturna/$(date +%Y-%m-%d_%H%M)"
mkdir -p "$DIR"
LOG="$DIR/execucao.log"
RES="$DIR/RESUMO.md"
exec 9>"$ROOT/logs_atualizacao_noturna/.lock"
flock -n 9 || { echo "Outra atualização noturna já está rodando." >&2; exit 1; }

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
restante() { echo $(( FIM - $(date +%s) )); }

{
  echo "# Atualização noturna — $(date '+%d/%m/%Y %H:%M')"
  echo
  echo "Prazo: $PRAZO · Backup de comparação: \`${BACKUP:-nenhum}\`"
  echo
  echo "| Etapa | Script | Resultado | Duração |"
  echo "|---|---|---|---|"
} > "$RES"

# 1. Espera o pipeline principal (executar_todos_os_scripts.py)
if [ -n "$PID_PIPELINE" ] && kill -0 "$PID_PIPELINE" 2>/dev/null; then
  log "Aguardando o pipeline principal (PID $PID_PIPELINE) terminar..."
  while kill -0 "$PID_PIPELINE" 2>/dev/null; do
    [ "$(restante)" -le 0 ] && { log "Prazo atingido esperando o pipeline."; echo "| — | pipeline principal | prazo atingido | — |" >> "$RES"; exit 0; }
    sleep 30
  done
  rc=$(grep -o 'FIM_PIPELINE rc=[0-9]*' logs_execucao_completa.log 2>/dev/null | tail -1)
  log "Pipeline principal terminou (${rc:-rc desconhecido})."
  echo "| 0 | executar_tudo.sh (pipeline 01–22) | ${rc:-terminado} | — |" >> "$RES"
fi

# 2. Geradores de relatórios, na ordem de dependência
ETAPAS=(
  # dados e resultados derivados
  "scripts/executar_validacao_temporal_5dobras.py"
  "scripts/gerar_figuras_oficiais.py"
  "scripts/gerar_tabela_unica_resultados_oficiais.py"
  "scripts/gerar_blocos_hipoteses.py"
  "scripts/analise_grafos_frotas.py"
  "scripts/gerar_artigo_grafos.py"
  "scripts/gerar_figura_h4_xai.py"
  # LOA/PCA 2026 e execução orçamentária
  "scripts/execucao_orcamentaria_frota.py"
  "scripts/planejamento_loa_pca_2026.py"
  "scripts/gerar_secao_loa_pca_tcc.py"
  # relatórios
  "scripts/gerar_mep_pdf.py"
  "scripts/gerar_apresentacao_sic.py"
  "scripts/gerar_relatorio_qualificacao_pdf.py"
  "scripts/gerar_mapeamento_pesquisa_pdf.py"
  "scripts/gerar_html_conciliacao_expandido.py"
  "scripts/gerar_relatorio_conciliacao_teorico_pratica_pdf.py"
  "scripts/compilar_relatorio_gerencial_frotas.py"
  "scripts/compilar_relatorio_tecnico_processamento_pdf.py"
  "scripts/compilar_documentacao_gestao_frotas_pdf.py"
  "scripts/compilar_readme_sistema_frotas_pdf.py"
  "scripts/compilar_mapa_mental_frotas_pdf.py"
  "scripts/compilar_catalogo_todas_figuras_pdf.py"
  "scripts/gerar_relatorio_figuras_memoria_calculo.py"
  "scripts/gerar_mapeamento_bpm.py"
  # literatura
  "scripts/rsl_prisma.py --sem-rede"
  "scripts/gerar_protocolo_e_relatorio_rsl.py"
  "scripts/gerar_lista_cafe.py"
  # PBS por último (lê os demais) e verificação de frases antigas (só relatório)
  "scripts/gerar_relatorio_pbs.py"
  "scripts/propagar_hipoteses.py"
)
n=0
for etapa in "${ETAPAS[@]}"; do
  n=$((n + 1))
  arq="${etapa%% *}"
  r=$(restante)
  if [ "$r" -le 60 ]; then
    log "Prazo atingido; etapas restantes não executadas a partir de $arq."
    echo "| $n | \`$etapa\` | não executada (prazo) | — |" >> "$RES"
    continue
  fi
  [ -f "$arq" ] || { echo "| $n | \`$etapa\` | arquivo inexistente | — |" >> "$RES"; continue; }
  lim=$(( r < 3600 ? r : 3600 ))
  log ">>> [$n/${#ETAPAS[@]}] $etapa (limite ${lim}s)"
  t0=$(date +%s)
  # shellcheck disable=SC2086
  timeout --kill-after=30 "$lim" "$PY" $etapa </dev/null >>"$LOG" 2>&1
  rc=$?
  dt=$(( $(date +%s) - t0 ))
  case $rc in
    0) st="ok" ;;
    124|137) st="**tempo esgotado**" ;;
    *) st="**falhou (código $rc)**" ;;
  esac
  log "<<< $etapa: $st em ${dt}s"
  echo "| $n | \`$etapa\` | $st | ${dt}s |" >> "$RES"
done

# 3. Comparação das métricas com o backup
for PAR in "resultados/logs:dissertacao_frotas/resultados/logs" "relatorios:relatorios" "resultados_loa_pca_2026:resultados_loa_pca_2026"; do
ANT="$BACKUP/${PAR%%:*}"; DEP="${PAR##*:}"
if [ -n "$BACKUP" ] && [ -d "$ANT" ]; then
  log "Comparando métricas de $DEP com $ANT ..."
  "$PY" - "$ANT" "$DEP" >> "$RES" 2>>"$LOG" <<'EOF'
import json, sys
from pathlib import Path
antes, depois = Path(sys.argv[1]), Path(sys.argv[2])
IGN = ("timestamp", "duracao", "data_", "_em_utc", "generated_at", "tempo_")
def folhas(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from folhas(v, f"{p}.{k}" if p else str(k))
    elif isinstance(o, list) and len(o) <= 50:
        for i, v in enumerate(o):
            yield from folhas(v, f"{p}[{i}]")
    elif isinstance(o, (int, float, bool, str)) and not isinstance(o, str) or (isinstance(o, str) and len(o) < 80):
        yield p, o
print(f"\n## Métricas que mudaram em `{depois}`\n")
print("Comparação campo a campo dos JSONs (carimbos de data e duração ignorados).\n")
total = 0
for fa in sorted(antes.glob("*.json")):
    fd = depois / fa.name
    if not fd.exists():
        print(f"- `{fa.name}`: **não existe mais**"); continue
    try:
        a, d = dict(folhas(json.loads(fa.read_text(encoding="utf-8")))), dict(folhas(json.loads(fd.read_text(encoding="utf-8"))))
    except Exception as e:
        print(f"- `{fa.name}`: não comparável ({e})"); continue
    mud = []
    for k in sorted(set(a) | set(d)):
        if any(x in k.lower() for x in IGN):
            continue
        va, vd = a.get(k, "∅"), d.get(k, "∅")
        if isinstance(va, float) and isinstance(vd, float) and abs(va - vd) <= 1e-9 * max(1, abs(va)):
            continue
        if va != vd:
            mud.append((k, va, vd))
    if mud:
        total += len(mud)
        print(f"\n### `{fa.name}` — {len(mud)} campo(s)\n\n| Campo | Antes | Depois |\n|---|---|---|")
        for k, va, vd in mud[:60]:
            print(f"| `{k}` | {va} | {vd} |")
        if len(mud) > 60:
            print(f"| … | +{len(mud) - 60} campos | |")
for fd in sorted(depois.glob("*.json")):
    if not (antes / fd.name).exists():
        print(f"- `{fd.name}`: **novo**")
print(f"\nTotal de campos alterados: {total}")
EOF
fi
done

log "Fim. Resumo em $RES"
echo -e "\nFim: $(date '+%d/%m/%Y %H:%M'). Nada foi enviado ao GitHub; revisar antes de publicar." >> "$RES"

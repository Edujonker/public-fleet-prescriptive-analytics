#!/usr/bin/env bash
# Atualização diária completa do projeto (chamada pelo timer systemd "busca-artigos").
#
# Etapas executadas, nesta ordem:
#   1. Busca de novos artigos (OpenAlex, Semantic Scholar, Scopus) via buscar_artigos.py
#   2. Regeneração do Protocolo Sigma (gerar_protocolo_sigma_artigos.py)
#   3. Regeneração do PBS.pdf (gerar_relatorio_pbs.py)
#   4. Regeneração da apresentação de qualificação (gerar_apresentacao_qualificacao.py)
#
# PDFs de acesso aberto vão para artigos/ (os já existentes não são baixados de novo).
# Relatórios do dia em artigos/atualizacoes/AAAA-MM-DD/ (novos.csv lista só os inéditos).
# Log em artigos/atualizacoes/logs/AAAA-MM-DD.log (mantém os últimos 90).
#
# Ajustes por variável de ambiente (opcional):
#   MAX_RESULTADOS (padrão 10000 por base)   MAX_PDFS (padrão 10000)   ANO_MIN (padrão 2020)
#   SUFIXO   grava os relatórios em artigos/atualizacoes/AAAA-MM-DD<SUFIXO>/ (ex.: _retomada), sem sobrescrever os da manhã
#   EXTRA    argumentos a mais para buscar_artigos.py (ex.: "--repetir-transitorias --paralelo 3")
#   COFRE_SENHA  senha mestra do cofre de credenciais de API (credenciais_api.bin)
# Não altera a revisão sistemática (revisao_sistematica/), cuja busca tem data fixa.

set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_HORA_AGORA="$(date +'%Y-%m-%d %H:%M')"
DATA_LIMITE="2026-11-25 12:00"

# Trava de encerramento do protocolo: 25/11/2026 às 12:00
if [[ "$DATA_HORA_AGORA" > "$DATA_LIMITE" ]]; then
    echo "$(date '+%F %T') Protocolo de baixa finalizado (prazo estipulado encerrado em 25/11/2026 às 12:00). Nenhuma nova baixa será executada." >> "$RAIZ/artigos/atualizacoes/logs/$(date +%F).log" 2>/dev/null || true
    echo "Prazo final de baixa atingido (25/11/2026 12:00). Operação encerrada."
    exit 0
fi

HOJE="$(date +%F)"
DIR_DIA="$RAIZ/artigos/atualizacoes/$HOJE${SUFIXO:-}"
DIR_LOG="$RAIZ/artigos/atualizacoes/logs"
mkdir -p "$DIR_DIA" "$DIR_LOG"
LOG="$DIR_LOG/$HOJE.log"

exec 9>"$RAIZ/artigos/atualizacoes/.lock"
if ! flock -n 9; then
    echo "$(date '+%F %T') outra busca já está em andamento; saindo." >> "$LOG"
    exit 0
fi

log_etapa() {
    echo "=== $(date '+%F %T') $1 ===" >> "$LOG"
}

{
    log_etapa "início da atualização diária${SUFIXO:+ ($SUFIXO)}${EXTRA:+ · $EXTRA}"
    cd "$RAIZ" || exit 1
    source "$RAIZ/.venv/bin/activate"

    # Carrega chaves das APIs do .env (se existirem) e exporta para o ambiente.
    if [ -f "$RAIZ/.env" ]; then
        for var in OPENALEX_API_KEY OPENALEX_EMAIL UNPAYWALL_EMAIL S2_API_KEY SCOPUS_API_KEY; do
            val="$(grep -m1 "^${var}=" "$RAIZ/.env" | cut -d= -f2- | sed 's/^["'"'"']//; s/["'"'"']$//')"
            if [ -n "$val" ]; then export "$var=$val"; echo "$var: definida"; else echo "$var: não definida"; fi
        done
        unset val
    fi

    # Senha mestra do cofre (se não estiver exportada, tenta ler de COFRE_SENHA_FILE).
    if [ -z "${COFRE_SENHA:-}" ] && [ -f "$RAIZ/artigos/atualizacoes/cofre_senha.txt" ]; then
        export COFRE_SENHA="$(cat "$RAIZ/artigos/atualizacoes/cofre_senha.txt")"
    fi

    # ── Etapa 1: busca de novos artigos ──
    log_etapa "etapa 1: busca de novos artigos"
    python3 -u scripts/buscar_artigos.py \
        --senha-mestra "${COFRE_SENHA:-}" \
        --ordem recentes \
        --ano-min "${ANO_MIN:-2020}" \
        --max-resultados "${MAX_RESULTADOS:-10000}" \
        --max-pdfs "${MAX_PDFS:-10000}" \
        --saida "$DIR_DIA" \
        --pasta-pdf "$RAIZ/artigos" \
        ${EXTRA:-}
    status_busca=$?
    echo "=== $(date '+%F %T') fim busca (código $status_busca) ===" >> "$LOG"

    if [ "$status_busca" -ne 0 ]; then
        echo "ERRO na busca de artigos (código $status_busca); interrompendo etapas seguintes." >> "$LOG"
        exit "$status_busca"
    fi

    # ── Etapa 2: Protocolo Sigma ──
    log_etapa "etapa 2: regeneração do Protocolo Sigma"
    python3 -u scripts/gerar_protocolo_sigma_artigos.py >> "$LOG" 2>&1
    status_sigma=$?
    echo "=== $(date '+%F %T') fim protocolo sigma (código $status_sigma) ===" >> "$LOG"

    # ── Etapa 3: PBS.pdf ──
    log_etapa "etapa 3: regeneração do PBS.pdf"
    python3 -u scripts/gerar_relatorio_pbs.py >> "$LOG" 2>&1
    status_pbs=$?
    echo "=== $(date '+%F %T') fim PBS.pdf (código $status_pbs) ===" >> "$LOG"

    # ── Etapa 4: Apresentação de qualificação ──
    log_etapa "etapa 4: regeneração da apresentação de qualificação"
    python3 -u scripts/gerar_apresentacao_qualificacao.py >> "$LOG" 2>&1
    status_apres=$?
    echo "=== $(date '+%F %T') fim apresentação (código $status_apres) ===" >> "$LOG"

    log_etapa "fim da atualização diária (códigos: busca=$status_busca sigma=$status_sigma pbs=$status_pbs apresent=$status_apres)"
} >> "$LOG" 2>&1

# mantém só os 90 logs mais recentes
ls -1t "$DIR_LOG"/*.log 2>/dev/null | tail -n +91 | xargs -r rm -f

# Código de saída: sucesso se todas as etapas passaram
if [ "${status_busca:-1}" -eq 0 ] && [ "${status_sigma:-1}" -eq 0 ] && [ "${status_pbs:-1}" -eq 0 ] && [ "${status_apres:-1}" -eq 0 ]; then
    exit 0
else
    exit 1
fi

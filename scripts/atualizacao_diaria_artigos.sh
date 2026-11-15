#!/usr/bin/env bash
# Busca diária de artigos novos (chamada pelo timer systemd "busca-artigos").
#
# - Busca os trabalhos mais recentes com a mesma consulta de scripts/buscar_artigos.py
# - PDFs de acesso aberto vão para artigos/ (os já existentes não são baixados de novo)
# - Relatórios do dia em artigos/atualizacoes/AAAA-MM-DD/ (novos.csv lista só os inéditos)
# - Log em artigos/atualizacoes/logs/AAAA-MM-DD.log (mantém os últimos 90)
#
# Ajustes por variável de ambiente (opcional):
#   MAX_RESULTADOS (padrão 300 por base)   MAX_PDFS (padrão 50)   ANO_MIN (padrão 2020)
# Não altera a revisão sistemática (revisao_sistematica/), cuja busca tem data fixa.

set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOJE="$(date +%F)"
DIR_DIA="$RAIZ/artigos/atualizacoes/$HOJE"
DIR_LOG="$RAIZ/artigos/atualizacoes/logs"
mkdir -p "$DIR_DIA" "$DIR_LOG"
LOG="$DIR_LOG/$HOJE.log"

exec 9>"$RAIZ/artigos/atualizacoes/.lock"
if ! flock -n 9; then
    echo "$(date '+%F %T') outra busca já está em andamento; saindo." >> "$LOG"
    exit 0
fi

{
    echo "=== $(date '+%F %T') início da busca diária ==="
    cd "$RAIZ" || exit 1
    # shellcheck disable=SC1091
    source "$RAIZ/.venv/bin/activate"
    python3 -u scripts/buscar_artigos.py \
        --ordem recentes \
        --ano-min "${ANO_MIN:-2020}" \
        --max-resultados "${MAX_RESULTADOS:-300}" \
        --max-pdfs "${MAX_PDFS:-50}" \
        --saida "$DIR_DIA" \
        --pasta-pdf "$RAIZ/artigos"
    status=$?
    echo "=== $(date '+%F %T') fim (código $status) ==="
} >> "$LOG" 2>&1

# mantém só os 90 logs mais recentes
ls -1t "$DIR_LOG"/*.log 2>/dev/null | tail -n +91 | xargs -r rm -f
exit "${status:-1}"

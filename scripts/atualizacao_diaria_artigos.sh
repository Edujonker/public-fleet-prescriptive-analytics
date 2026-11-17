#!/usr/bin/env bash
# Busca diária de artigos novos (chamada pelo timer systemd "busca-artigos").
#
# - Busca os trabalhos mais recentes com a mesma consulta de scripts/buscar_artigos.py
# - PDFs de acesso aberto vão para artigos/ (os já existentes não são baixados de novo)
# - Relatórios do dia em artigos/atualizacoes/AAAA-MM-DD/ (novos.csv lista só os inéditos)
# - Log em artigos/atualizacoes/logs/AAAA-MM-DD.log (mantém os últimos 90)
#
# Ajustes por variável de ambiente (opcional):
#   MAX_RESULTADOS (padrão 10000 por base)   MAX_PDFS (padrão 10000)   ANO_MIN (padrão 2020)
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
    # Chaves e e-mails de contato das APIs, lidos do .env (fora do git). Só estas variáveis são
    # carregadas, e o log registra apenas se cada uma está definida, nunca o valor.
    if [ -f "$RAIZ/.env" ]; then
        for var in OPENALEX_API_KEY OPENALEX_EMAIL UNPAYWALL_EMAIL S2_API_KEY; do
            val="$(grep -m1 "^${var}=" "$RAIZ/.env" | cut -d= -f2- | sed 's/^["'"'"']//; s/["'"'"']$//')"
            if [ -n "$val" ]; then export "$var=$val"; echo "$var: definida"; else echo "$var: não definida"; fi
        done
        unset val
    fi
    python3 -u scripts/buscar_artigos.py \
        --ordem recentes \
        --ano-min "${ANO_MIN:-2020}" \
        --max-resultados "${MAX_RESULTADOS:-10000}" \
        --max-pdfs "${MAX_PDFS:-10000}" \
        --saida "$DIR_DIA" \
        --pasta-pdf "$RAIZ/artigos"
    status=$?
    echo "=== $(date '+%F %T') fim (código $status) ==="
} >> "$LOG" 2>&1

# mantém só os 90 logs mais recentes
ls -1t "$DIR_LOG"/*.log 2>/dev/null | tail -n +91 | xargs -r rm -f
exit "${status:-1}"

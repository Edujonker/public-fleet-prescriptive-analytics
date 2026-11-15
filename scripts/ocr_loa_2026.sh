#!/usr/bin/env bash
# OCR das páginas da LOA 2026 (SC) cujo texto não é extraível (fonte codificada).
# Saída: leis_e_normativas/estaduais_SC/ocr_loa_2026/pagina_NNNN.txt  (uma por página do PDF)
# Uso: scripts/ocr_loa_2026.sh [arquivo_com_lista_de_paginas]
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PDF="$ROOT/leis_e_normativas/estaduais_SC/LOA_2026_SC_Lei_19683_completa.pdf"
OUT="$ROOT/leis_e_normativas/estaduais_SC/ocr_loa_2026"
LISTA="${1:-}"
mkdir -p "$OUT"
if [ -z "$LISTA" ]; then LISTA=$(mktemp); seq 1 "$(pdfinfo "$PDF" | awk '/^Pages/{print $2}')" > "$LISTA"; fi
ocr() {
  p=$1; f=$(printf "%s/pagina_%04d.txt" "$OUT" "$p")
  [ -s "$f" ] && return 0
  tmp=$(mktemp -d)
  pdftoppm -r 300 -gray -png -f "$p" -l "$p" "$PDF" "$tmp/p" && \
  OMP_THREAD_LIMIT=1 tesseract "$tmp"/p-*.png "${f%.txt}" -l por --psm 6 >/dev/null 2>&1
  rm -rf "$tmp"
}
export -f ocr; export PDF OUT
xargs -a "$LISTA" -P "$(( $(nproc) - 2 ))" -I{} bash -c 'ocr {}'
echo "FIM_OCR $(ls "$OUT" | wc -l) páginas"

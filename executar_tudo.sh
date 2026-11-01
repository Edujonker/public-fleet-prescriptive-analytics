#!/usr/bin/env bash
# Script shell para disparar todo o pipeline com um único comando
set -e
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="$ROOT_DIR/.venv/bin/python3"

if [ ! -f "$PYTHON_EXEC" ]; then
    PYTHON_EXEC="python3"
fi

echo "================================================================================"
echo "Iniciando execução integrada da Dissertação de Mestrado PPGCAP/UDESC..."
echo "Interpretador: $PYTHON_EXEC"
echo "================================================================================"

"$PYTHON_EXEC" "$ROOT_DIR/executar_todos_os_scripts.py"

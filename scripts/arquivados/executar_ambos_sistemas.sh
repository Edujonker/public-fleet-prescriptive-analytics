#!/usr/bin/env bash
# ==============================================================================
# PPGCAP / UDESC - EXECUÇÃO PARALELA DE AMBOS OS SISTEMAS (PORTAS 8080 E 8090)
# ==============================================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ -f ".venv/bin/python3" ]; then
    PYTHON_BIN=".venv/bin/python3"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

chmod +x executar_ambos_sistemas.py
$PYTHON_BIN executar_ambos_sistemas.py

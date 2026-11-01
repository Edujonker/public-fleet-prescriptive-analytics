#!/bin/bash
# ==============================================================================
# Script de Inicialização para Linux / macOS - FrotaSaaS Enterprise
# ==============================================================================

DIR_SCRIPT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR_SCRIPT"

echo "----------------------------------------------------------------------"
echo "Iniciando Sistema de Gestão de Frotas & Telemetria IoT..."
echo "----------------------------------------------------------------------"

# Localizar Python
PYTHON_CMD="python3"
if [ -f "$DIR_SCRIPT/../.venv/bin/python" ]; then
    PYTHON_CMD="$DIR_SCRIPT/../.venv/bin/python"
elif [ -f "$DIR_SCRIPT/.venv/bin/python" ]; then
    PYTHON_CMD="$DIR_SCRIPT/.venv/bin/python"
fi

$PYTHON_CMD executar_sistema.py

#!/usr/bin/env bash
# ==============================================================================
# INICIALIZADOR DO APLICATIVO DESKTOP PYQT6 (PPGCAP/UDESC 2026)
# ==============================================================================
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON_EXEC="$DIR/.venv/bin/python"
else
    PYTHON_EXEC="python3"
fi

echo "Iniciando Dashboard Desktop Profissional com Copiloto de IA (PyQt6)..."
exec "$PYTHON_EXEC" "$DIR/scripts/app_dashboard_gui.py" "$@"

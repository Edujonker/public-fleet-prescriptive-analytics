#!/usr/bin/env bash
# ==============================================================================
# ASSISTENTE DE IA VIA PROMPT - PPGCAP/UDESC
# ==============================================================================
# Executa o assistente de IA em modo interativo de prompt ou responde diretamente
# à pergunta passada como argumento na linha de comando.
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Priorizar o interpretador do ambiente virtual .venv
if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$DIR/.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    echo "Erro: Interpretador Python não encontrado."
    exit 1
fi

"$PYTHON_CMD" "$DIR/scripts/assistente_ia_prompt.py" "$@"

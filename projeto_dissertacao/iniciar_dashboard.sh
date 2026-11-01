#!/usr/bin/env bash
# Script para iniciar o dashboard interativo de demonstração de resultados
cd "$(dirname "$0")/.." || exit 1
echo "Iniciando Dashboard da Dissertação em http://localhost:8080/dashboard/ ..."
./.venv/bin/python run_dashboard.py

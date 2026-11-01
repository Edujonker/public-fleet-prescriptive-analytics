#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atalho para auditoria de segurança DevSecOps a partir do backend.
Executa o analisador mestre localizado em scripts/auditoria_seguranca_devsecops.py
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
repo_root = backend_dir.parent.parent

script_path = repo_root / "scripts" / "auditoria_seguranca_devsecops.py"
if script_path.exists():
    import runpy
    sys.argv[0] = str(script_path)
    runpy.run_path(str(script_path), run_name="__main__")
else:
    print(f"Erro: Script não encontrado em {script_path}")

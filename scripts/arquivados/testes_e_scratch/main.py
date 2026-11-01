#!/usr/bin/env python3
"""Executa em sequência os scripts principais do projeto de análise de manutenção."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPT_ORDER = [
    "ler_os.py",
    "ml_os.py",
    "isolation_forest.py",
    "analise_completa.py",
]


def choose_python() -> str:
    venv_python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def run_script(python_executable: str, script_name: str) -> None:
    script_path = ROOT / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Script não encontrado: {script_path}")

    print(f"\n{'=' * 70}")
    print(f"Executando: {script_name}")
    print(f"{'=' * 70}")
    subprocess.run([python_executable, str(script_path)], cwd=str(ROOT), check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa os scripts do pipeline de análise de manutenção em sequência."
    )
    parser.add_argument(
        "--scripts",
        nargs="+",
        choices=SCRIPT_ORDER,
        help="Lista opcional de scripts para executar. Se omitido, executa todos em ordem.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    python_executable = choose_python()
    scripts_to_run = args.scripts if args.scripts else SCRIPT_ORDER

    print(f"Python utilizado: {python_executable}")
    print(f"Diretório do projeto: {ROOT}")

    for script_name in scripts_to_run:
        run_script(python_executable, script_name)

    print("\nPipeline concluído com sucesso.")


if __name__ == "__main__":
    main()

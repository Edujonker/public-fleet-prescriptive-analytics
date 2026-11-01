#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Varre todo o repositório e substitui qualquer ocorrência de Vivian Kremer Kalempa pela
Orientadora Profa. Dra. Vivian Kremer Kalempa (e Coorientador Prof. Dr. Yuri Kaszubowski Lopes onde couber).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", "versao_final_congelada"}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".parquet", ".zip", ".pyc", ".old.pdf"}

REPLACEMENTS = [
    ("Profa. Dra. Vivian Kremer Kalempa", "Profa. Dra. Vivian Kremer Kalempa"),
    ("PROFA. DRA. VIVIAN KREMER KALEMPA", "PROFA. DRA. VIVIAN KREMER KALEMPA"),
    ("Vivian Kremer Kalempa", "Vivian Kremer Kalempa"),
    ("VIVIAN KREMER KALEMPA", "VIVIAN KREMER KALEMPA"),
    ("Kalempa, Vivian Kremer", "Kalempa, Vivian Kremer"),
    ("KALEMPA, VIVIAN KREMER", "KALEMPA, VIVIAN KREMER"),
    ("Kalempa", "Kalempa"),
    ("Orientadora: Vivian Kremer Kalempa", "Orientadora: Vivian Kremer Kalempa"),
    ("orientadora: Vivian Kremer Kalempa", "orientadora: Vivian Kremer Kalempa"),
    ("Orientadora: Profa. Dra. Vivian Kremer Kalempa", "Orientadora: Profa. Dra. Vivian Kremer Kalempa"),
    ("orientadora: Profa. Dra. Vivian Kremer Kalempa", "orientadora: Profa. Dra. Vivian Kremer Kalempa"),
    ("Orientadora e Presidente", "Orientadora e Presidente"),
    ("À minha orientadora, Profa. Dra. Vivian Kremer Kalempa", "À minha orientadora, Profa. Dra. Vivian Kremer Kalempa"),
    ("À minha orientadora, **Profa. Dra. Vivian Kremer Kalempa**", "À minha orientadora, **Profa. Dra. Vivian Kremer Kalempa**"),
    ("À minha orientadora, <strong>Profa. Dra. Vivian Kremer Kalempa</strong>", "À minha orientadora, <strong>Profa. Dra. Vivian Kremer Kalempa</strong>"),
    ("Ao meu orientador, \\textbf{Profa. Dra. Vivian Kremer Kalempa}", "À minha orientadora, \\textbf{Profa. Dra. Vivian Kremer Kalempa}")
]

def process_file(p: Path):
    if p.name == "tcc_eduardo.old.pdf" or p.suffix in EXCLUDE_EXTS:
        return
    try:
        content = p.read_text(encoding="utf-8")
    except Exception:
        return

    orig = content
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)

    if content != orig:
        p.write_text(content, encoding="utf-8")
        print(f"[SUBSTITUÍDO] {p.relative_to(BASE_DIR)}")

def main():
    print("Iniciando varredura e substituição em todo o repositório...")
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            path = Path(root) / f
            process_file(path)
    print("Varredura concluída!")

if __name__ == "__main__":
    main()

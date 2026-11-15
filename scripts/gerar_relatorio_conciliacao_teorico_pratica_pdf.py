#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador do Relatório de Conciliação Teórico-Prática e Resultados Empíricos
Lê o documento estruturado HTML e renderiza o PDF com o motor WeasyPrint.
Gera os arquivos em múltiplos nomes convenientes e cópias espelhadas.
"""

import os
import sys
import shutil
from pathlib import Path
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_FILE = BASE_DIR / "relatorios" / "conciliacao_teorico_pratica.html"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_DIR = BASE_DIR / "Documentos"

for d in [PDF_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def compilar_conciliacao_pdf():
    print("=" * 75)
    print("COMPILAÇÃO DO RELATÓRIO DE CONCILIAÇÃO TEÓRICO-PRÁTICA EM PDF")
    print("Programa de Pós-Graduação em Computação Aplicada (PPGCAP / UDESC)")
    print("Autor: Eduardo Lopes Jonker")
    print("=" * 75)

    if not HTML_FILE.exists():
        print(f"Erro: Arquivo HTML não encontrado em: {HTML_FILE}")
        sys.exit(1)

    print(f"1. Lendo arquivo HTML estruturado: {HTML_FILE.name}...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Nomes dos arquivos de saída
    pdf_longo = BASE_DIR / "conciliacao_teorico_pratica.pdf"
    pdf_relatorios = PDF_DIR / "conciliacao_teorico_pratica.pdf"
    pdf_documentos = DOCS_DIR / "conciliacao_teorico_pratica.pdf"

    print("2. Renderizando PDF com WeasyPrint Engine...")
    weasyprint.HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(str(pdf_longo))
    
    tamanho_mb = pdf_longo.stat().st_size / (1024 * 1024)
    print(f"✓ PDF gerado com sucesso: {pdf_longo.name}")
    print(f"  Tamanho: {tamanho_mb:.2f} MB")

    print("3. Criando cópias espelhadas de segurança e padronização...")
    shutil.copy2(pdf_longo, pdf_relatorios)
    shutil.copy2(pdf_longo, pdf_documentos)
    print(f"✓ Cópia espelhada em: {pdf_relatorios}")
    print(f"✓ Cópia espelhada em: {pdf_documentos}")

    print("=" * 75)
    print("COMPILAÇÃO DO RELATÓRIO DE CONCILIAÇÃO TEÓRICO-PRÁTICA CONCLUÍDA COM 100% DE SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    compilar_conciliacao_pdf()


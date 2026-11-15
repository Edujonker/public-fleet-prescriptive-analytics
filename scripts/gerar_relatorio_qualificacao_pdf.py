#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador do Relatório de Qualificação de Pesquisa em PDF
Lê o documento estruturado HTML e renderiza o PDF com o motor WeasyPrint.
Gera o arquivo 'qualificação de pesquisa.pdf' e cópias padronizadas.
"""

import os
import sys
import shutil
from pathlib import Path
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_FILE = BASE_DIR / "relatorios" / "qualificacao_pesquisa.html"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_DIR = BASE_DIR / "Documentos"

for d in [PDF_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def compilar_pdf():
    print("=" * 75)
    print("COMPILAÇÃO DO RELATÓRIO DE QUALIFICAÇÃO DE PESQUISA EM PDF")
    print("Programa de Pós-Graduação em Computação Aplicada (PPGCAP / UDESC)")
    print("Autor: Eduardo Lopes Jonker")
    print("=" * 75)

    if not HTML_FILE.exists():
        print(f"Erro: Arquivo HTML não encontrado em: {HTML_FILE}")
        sys.exit(1)

    print(f"1. Lendo arquivo HTML estruturado: {HTML_FILE.name}...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Nomes e caminhos de saída
    pdf_solicitado = BASE_DIR / "qualificação de pesquisa.pdf"
    pdf_padrao = BASE_DIR / "qualificacao_de_pesquisa.pdf"
    pdf_relatorios = PDF_DIR / "qualificacao_de_pesquisa.pdf"
    pdf_documentos = DOCS_DIR / "qualificacao_de_pesquisa.pdf"

    print("2. Renderizando PDF com WeasyPrint Engine...")
    weasyprint.HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(str(pdf_solicitado))
    
    tamanho_mb = pdf_solicitado.stat().st_size / (1024 * 1024)
    print(f"✓ PDF gerado com sucesso com nome exato solicitado: {pdf_solicitado.name}")
    print(f"  Tamanho: {tamanho_mb:.2f} MB")

    print("3. Criando cópias espelhadas de segurança e padronização...")
    shutil.copy2(pdf_solicitado, pdf_padrao)
    shutil.copy2(pdf_solicitado, pdf_relatorios)
    shutil.copy2(pdf_solicitado, pdf_documentos)
    print(f"✓ Cópia espelhada em: {pdf_padrao.name}")
    print(f"✓ Cópia espelhada em: {pdf_relatorios}")
    print(f"✓ Cópia espelhada em: {pdf_documentos}")

    print("=" * 75)
    print("COMPILAÇÃO DO RELATÓRIO DE QUALIFICAÇÃO CONCLUÍDA COM 100% DE SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    compilar_pdf()

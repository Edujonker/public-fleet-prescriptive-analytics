#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador do Mapeamento de Processos de Pesquisa (BPM / BPMN 2.0) em PDF
Lê o documento estruturado HTML e renderiza o PDF com o motor WeasyPrint.
Gera o arquivo 'mapeamento_de_pesquisa.pdf' e cópias em relatorios_pdf/ e Documentos/.
"""

import os
import sys
import shutil
from pathlib import Path
import weasyprint

import sys as _sys_ia; from pathlib import Path as _P_ia; _sys_ia.path.insert(0, str(_P_ia(__file__).resolve().parent))
import uso_etico_ia; uso_etico_ia.ativar()  # seção "Uso ético de inteligência artificial" em todo PDF
BASE_DIR = Path(__file__).resolve().parent.parent
HTML_FILE = BASE_DIR / "relatorios" / "mapeamento_pesquisa.html"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_DIR = BASE_DIR / "Documentos"

for d in [PDF_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def compilar_mapeamento_pdf():
    print("=" * 75)
    print("COMPILAÇÃO DO MAPEAMENTO DE PROCESSOS DE PESQUISA (BPM) EM PDF")
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
    pdf_solicitado = BASE_DIR / "mapeamento_de_pesquisa.pdf"
    pdf_relatorios = PDF_DIR / "mapeamento_de_pesquisa.pdf"
    pdf_documentos = DOCS_DIR / "mapeamento_de_pesquisa.pdf"

    print("2. Renderizando PDF com WeasyPrint Engine...")
    weasyprint.HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(str(pdf_solicitado))
    
    tamanho_mb = pdf_solicitado.stat().st_size / (1024 * 1024)
    print(f"✓ PDF gerado com sucesso com nome exato solicitado: {pdf_solicitado.name}")
    print(f"  Tamanho: {tamanho_mb:.2f} MB")

    print("3. Criando cópias espelhadas de segurança e padronização...")
    shutil.copy2(pdf_solicitado, pdf_relatorios)
    shutil.copy2(pdf_solicitado, pdf_documentos)
    print(f"✓ Cópia espelhada em: {pdf_relatorios}")
    print(f"✓ Cópia espelhada em: {pdf_documentos}")

    print("=" * 75)
    print("COMPILAÇÃO DO MAPEAMENTO BPM CONCLUÍDA COM 100% DE SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    compilar_mapeamento_pdf()


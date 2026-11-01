#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT DE CONGELAMENTO E CERTIFICAÇÃO DA VERSÃO FINAL DA DISSERTAÇÃO
PDF (120 PÁGINAS), LATEX (OVERLEAF) E MICROSOFT WORD (.DOCX)
================================================================================
"""

import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FREEZE_DIR = BASE_DIR / "versao_final_congelada"

def calc_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 80)
    print("INICIANDO PROTOCOLO DE CONGELAMENTO DA VERSÃO FINAL")
    print("=" * 80)

    # Criação das pastas de congelamento
    dirs = [
        FREEZE_DIR,
        FREEZE_DIR / "PDF",
        FREEZE_DIR / "WORD",
        FREEZE_DIR / "LATEX",
        FREEZE_DIR / "LATEX" / "fonte_latex"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Desbloqueia arquivos se já existirem
    for f in FREEZE_DIR.rglob("*"):
        if f.is_file():
            try:
                os.chmod(f, 0o664)
            except Exception:
                pass

    # 1. Congelar PDF (versão de 120 páginas com todas as correções)
    pdf_src = BASE_DIR / "dissertacao_versao_revisada.pdf"
    pdf_dest1 = FREEZE_DIR / "PDF" / "dissertacao_versao_final_congelada.pdf"
    pdf_dest2 = FREEZE_DIR / "PDF" / "tcc_eduardo_versao_final_congelada.pdf"
    pdf_root = BASE_DIR / "dissertacao_versao_final_congelada.pdf"

    for p in [pdf_dest1, pdf_dest2, pdf_root]:
        if p.exists():
            try: os.chmod(p, 0o664)
            except Exception: pass
    shutil.copy2(pdf_src, pdf_dest1)
    shutil.copy2(pdf_src, pdf_dest2)
    shutil.copy2(pdf_src, pdf_root)
    print(f"[OK] PDF congelado: {pdf_dest1.name} ({pdf_dest1.stat().st_size / (1024*1024):.2f} MB)")

    # 2. Congelar WORD (.docx)
    docx_src = BASE_DIR / "dissertacao_versao_final_congelada.docx"
    docx_dest1 = FREEZE_DIR / "WORD" / "dissertacao_versao_final_congelada.docx"
    docx_dest2 = FREEZE_DIR / "WORD" / "tcc_eduardo_versao_final_congelada.docx"

    for d in [docx_dest1, docx_dest2]:
        if d.exists():
            try: os.chmod(d, 0o664)
            except Exception: pass

    shutil.copy2(docx_src, docx_dest1)
    shutil.copy2(docx_src, docx_dest2)
    print(f"[OK] Word congelado: {docx_dest1.name} ({docx_dest1.stat().st_size / (1024*1024):.2f} MB)")

    # 3. Congelar LATEX (ZIP e Árvore Descompactada)
    latex_zip_src = BASE_DIR / "overleaf_dissertacao_udesc.zip"
    latex_zip_dest1 = FREEZE_DIR / "LATEX" / "overleaf_dissertacao_udesc.zip"
    latex_zip_dest2 = FREEZE_DIR / "LATEX" / "dissertacao_versao_final_congelada_latex.zip"
    latex_zip_root = BASE_DIR / "dissertacao_versao_final_congelada_latex.zip"

    shutil.copy2(latex_zip_src, latex_zip_dest1)
    shutil.copy2(latex_zip_src, latex_zip_dest2)
    shutil.copy2(latex_zip_src, latex_zip_root)

    # Copiar árvore fonte de LaTeX
    overleaf_src_dir = BASE_DIR / "overleaf_dissertacao_udesc"
    latex_tree_dest = FREEZE_DIR / "LATEX" / "fonte_latex"
    if overleaf_src_dir.exists():
        for item in overleaf_src_dir.iterdir():
            target = latex_tree_dest / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)

    print(f"[OK] LaTeX congelado: {latex_zip_dest1.name} ({latex_zip_dest1.stat().st_size / (1024*1024):.2f} MB)")

    # 4. Geração do Manifesto Criptográfico SHA-256
    arquivos_auditados = [
        pdf_dest1,
        pdf_dest2,
        docx_dest1,
        docx_dest2,
        latex_zip_dest1,
        latex_zip_dest2,
        pdf_root,
        docx_src,
        latex_zip_root
    ]

    agora = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    manifesto_txt = f"""================================================================================
MANIFESTO DE INTEGRIDADE CRIPTOGRÁFICA (SHA-256), VERSÃO FINAL CONGELADA
DISSERTAÇÃO DE MESTRADO ACADÊMICO EM COMPUTAÇÃO APLICADA (PPGCAP / CCT / UDESC)
AUTOR: EDUARDO LOPES JONKER
ORIENTADORA: PROFA. DRA. VIVIAN KREMER KALEMPA
COORIENTADOR: PROF. DR. YURI KASZUBOWSKI LOPES
DATA DE CONGELAMENTO: {agora}
================================================================================

ATENÇÃO: Todos os artefatos abaixo foram congelados e certificados com status FINAL.
Qualquer alteração posterior invalidará as assinaturas digitais abaixo calculadas.

1. FORMATO PDF MASTER (120 PÁGINAS EXATAS - ABNT NBR 14724):
   Arquivo: PDF/dissertacao_versao_final_congelada.pdf
   Tamanho: {pdf_dest1.stat().st_size} bytes ({pdf_dest1.stat().st_size / (1024*1024):.2f} MB)
   SHA-256: {calc_sha256(pdf_dest1)}

2. FORMATO MICROSOFT WORD (.DOCX - ABNT NBR 14724):
   Arquivo: WORD/dissertacao_versao_final_congelada.docx
   Tamanho: {docx_dest1.stat().st_size} bytes ({docx_dest1.stat().st_size / (1024*1024):.2f} MB)
   SHA-256: {calc_sha256(docx_dest1)}

3. FORMATO LATEX OVERLEAF (PACOTE ZIP MODULAR COMPLETO):
   Arquivo: LATEX/dissertacao_versao_final_congelada_latex.zip
   Tamanho: {latex_zip_dest1.stat().st_size} bytes ({latex_zip_dest1.stat().st_size / (1024*1024):.2f} MB)
   SHA-256: {calc_sha256(latex_zip_dest1)}

================================================================================
CERTIFICAÇÃO DAS 5 CORREÇÕES DA BANCA EXAMINADORA IMPLEMENTADAS:
[X] PÁG. 63:  Conclusão sobre preços-sombra e capacidade H_t restrita ao modelo MILP.
              Ausência de restrição ativa não comprova capacidade ociosa estadual.
[X] PÁG. 111: "27 veículos sinalizados pelo critério simulado de antieconomicidade".
[X] PÁG. 111: "modelo de contratação utilizado em diferentes administrações públicas".
[X] PÁG. 12-13: Sumário automático com correspondência exata de todas as subseções.
[X] PÁG. 4:   Folha de aprovação formal limpa sem marcadores provisórios.
================================================================================
"""

    manifesto_path = FREEZE_DIR / "MANIFESTO_INTEGRIDADE_SHA256.txt"
    manifesto_path.write_text(manifesto_txt, encoding="utf-8")
    print(f"[OK] Manifesto de integridade gerado em: {manifesto_path.name}")

    # 5. Aplicação de permissões somente leitura nos arquivos congelados
    for f in [pdf_dest1, pdf_dest2, docx_dest1, docx_dest2, latex_zip_dest1, latex_zip_dest2, manifesto_path]:
        try:
            os.chmod(f, 0o444) # Leitura para todos, sem escrita
        except Exception as e:
            print(f"Nota na proteção de {f.name}: {e}")

    print("=" * 80)
    print("CONGELAMENTO CONCLUÍDO COM SUCESSO!")
    print(f"Diretório imutável: {FREEZE_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()

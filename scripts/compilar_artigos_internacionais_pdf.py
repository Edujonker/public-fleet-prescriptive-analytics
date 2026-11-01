#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador dos Artigos Científicos Internacionais (Elsevier & IEEE Style)
Dissertação de Mestrado, PPGCAP/UDESC
Autor: Eduardo Lopes Jonker
"""

import os
import sys
from pathlib import Path
import markdown
import weasyprint

def compilar_artigo(md_path, pdf_path, journal_tag="ELSEVIER / IEEE", lang="en"):
    base_dir = Path(__file__).resolve().parent.parent
    text = md_path.read_text(encoding="utf-8")
    
    # Converte Markdown para HTML com extensões de tabelas e blocos
    html_body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'toc'])
    
    top_header = f"{journal_tag} • Preprint / Em Revisão" if lang == "pt" else f"{journal_tag} • Preprint Under Review"
    page_counter = 'content: "Página " counter(page) " de " counter(pages);' if lang == "pt" else 'content: "Page " counter(page) " of " counter(pages);'
    
    html_doc = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{md_path.stem}</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 2.5cm 2.2cm 2.5cm 2.2cm;
        @top-right {{
            content: "{top_header}";
            font-size: 8.5pt;
            color: #64748b;
            font-family: 'Liberation Sans', sans-serif;
            font-style: italic;
        }}
        @bottom-right {{
            {page_counter}
            font-size: 8.5pt;
            color: #64748b;
            font-family: 'Liberation Sans', sans-serif;
        }}
        @bottom-left {{
            content: "PPGCAP / UDESC • Jonker et al. (2026)";
            font-size: 8.5pt;
            color: #64748b;
            font-family: 'Liberation Sans', sans-serif;
        }}
    }}
    body {{
        font-family: 'Liberation Serif', 'Times New Roman', serif;
        font-size: 10.5pt;
        line-height: 1.6;
        color: #111827;
        margin: 0;
        padding: 0;
        text-align: justify;
    }}
    h1 {{
        font-family: 'Liberation Sans', Arial, sans-serif;
        font-size: 17pt;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.25;
        margin-bottom: 8px;
        text-align: left;
    }}
    h2 {{
        font-family: 'Liberation Sans', Arial, sans-serif;
        font-size: 11pt;
        font-weight: 700;
        color: #1e3a8a;
        border-bottom: 1.5px solid #cbd5e1;
        padding-bottom: 3px;
        margin-top: 18px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    h3 {{
        font-family: 'Liberation Sans', Arial, sans-serif;
        font-size: 10pt;
        font-weight: 700;
        color: #0f172a;
        margin-top: 14px;
        margin-bottom: 6px;
    }}
    p {{
        margin-bottom: 8px;
        text-indent: 1.2em;
    }}
    p:first-of-type {{
        text-indent: 0;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 8pt;
        margin: 12px 0;
        font-family: 'Liberation Sans', Arial, sans-serif;
        border-top: 1.5pt solid #0f172a;
        border-bottom: 1.5pt solid #0f172a;
    }}
    th {{
        background: transparent;
        color: #0f172a;
        padding: 6px 8px;
        font-weight: 700;
        border: none;
        border-bottom: 1pt solid #0f172a;
        text-align: left;
    }}
    td {{
        padding: 5px 8px;
        border: none;
        border-bottom: 0.5pt solid #e2e8f0;
    }}
    tr:last-child td {{
        border-bottom: none;
    }}
    tr:nth-child(even) td {{
        background: #f8fafc;
    }}
    blockquote {{
        margin: 10px 0 10px 4.0cm;
        padding: 0;
        border: none !important;
        border-left: none !important;
        font-size: 8.5pt;
        line-height: 1.35;
        color: #1e293b;
        text-align: justify;
        text-indent: 0;
    }}
    blockquote p {{
        margin: 0;
        padding: 0;
        text-indent: 0;
    }}
    pre, code {{
        font-family: 'Liberation Mono', monospace;
        font-size: 8pt;
        background: #f1f5f9;
        border: none !important;
        border-left: none !important;
    }}
    pre {{
        padding: 8px;
        border-radius: 4px;
        border: 1px solid #e2e8f0 !important;
        overflow-x: auto;
    }}
    ul, ol {{
        margin: 8px 0 8px 24px;
        padding: 0;
    }}
    li {{
        margin-bottom: 4px;
    }}
    hr {{
        border: none;
        border-top: 1px solid #cbd5e1;
        margin: 16px 0;
    }}
    .formula-box {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 10px 0;
        padding: 6px 14px;
        background: #f8fafc;
        border-left: 3px solid #2563eb;
        border-radius: 3px;
        font-family: 'Liberation Serif', 'Times New Roman', serif;
        font-size: 10pt;
        font-style: italic;
    }}
    .formula-number {{
        font-weight: bold;
        font-style: normal;
        color: #1e3a8a;
        margin-left: 15px;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""
    html = weasyprint.HTML(string=html_doc, base_url=str(base_dir))
    html.write_pdf(target=str(pdf_path))
    print(f"✔ Compilado com sucesso: {pdf_path.name} ({pdf_path.stat().st_size / 1024:.1f} KB)")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    artigos_dir = base_dir / "artigos_internacionais"
    
    print("=" * 80)
    print("COMPILANDO TODOS OS ARTIGOS CIENTÍFICOS EM SUAS RESPECTIVAS SUBPASTAS EM PDF")
    print("=" * 80)
    
    # Busca recursiva de todos os arquivos .md dentro de artigos_internacionais
    md_files = sorted(artigos_dir.glob("*/*.md"))
    
    journal_map = {
        "paper1": ("ELSEVIER • DECISION SUPPORT SYSTEMS", "en"),
        "paper2": ("IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS", "en"),
        "artigo1": ("QUALIS A1 • GESTÃO & PRODUÇÃO / RAC", "pt"),
        "artigo2": ("QUALIS A1 • REVISTA DE ADMINISTRAÇÃO PÚBLICA (RAP)", "pt"),
        "artigo3": ("QUALIS A1 • GESTÃO & PRODUÇÃO / RAC", "pt"),
        "consad": ("CONGRESSO CONSAD DE GESTÃO PÚBLICA • 2026", "pt")
    }
    
    for md_path in md_files:
        pdf_path = md_path.with_suffix(".pdf")
        
        # Identificar tag e idioma
        tag = "ARTIGO CIENTÍFICO QUALIS A1"
        lang = "pt"
        for k, (t, l) in journal_map.items():
            if k in md_path.name.lower():
                tag = t
                lang = l
                break
                
        if "resumo_expandido" in md_path.name.lower():
            tag = "RESUMO EXPANDIDO • PPGCAP / UDESC"
            lang = "pt"
        elif "extended_abstract" in md_path.name.lower():
            tag = "EXTENDED ABSTRACT • PPGCAP / UDESC"
            lang = "en"
                
        print(f"\n[Processando] {md_path.parent.name}/{md_path.name}")
        compilar_artigo(md_path, pdf_path, journal_tag=tag, lang=lang)
        
    print("\n" + "=" * 80)
    print("TODOS OS ARTIGOS NAS SUBPASTAS FORAM COMPILADOS EM PDF COM SUCESSO!")
    print("=" * 80)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
EXPORTADOR DE ARTIGOS CIENTÍFICOS PARA WORD (.DOCX) E LATEX (.TEX)
SISTEMA INTEGRADO DE GESTÃO DE FROTAS PÚBLICAS (PPGCAP/UDESC)
================================================================================
Autor: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes
================================================================================
"""

import os
import re
import html
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIGOS_DIR = BASE_DIR / "artigos_internacionais"

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Define margens internas da célula da tabela no Word."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def markdown_para_docx(md_path: Path, docx_path: Path):
    """Converte arquivo Markdown acadêmico para documento Word (.docx) formatado."""
    text = md_path.read_text(encoding="utf-8")
    doc = docx.Document()

    # Configuração de margens da página A4
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    lines = text.split("\n")
    i = 0
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i].strip()

        # Detecção de fórmulas matemáticas numeradas (.formula-box)
        if '<div class="formula-box">' in line:
            formula_lines = [line]
            while i + 1 < len(lines) and '</div>' not in lines[i]:
                i += 1
                formula_lines.append(lines[i].strip())
            raw_block = " ".join(formula_lines)
            clean_txt = re.sub(r'<[^>]+>', ' ', raw_block)
            clean_txt = html.unescape(clean_txt)
            clean_txt = re.sub(r'\s+', ' ', clean_txt).strip()
            
            m_eq = re.search(r'\(([0-9]+)\)$', clean_txt)
            eq_num = m_eq.group(0) if m_eq else ""
            eq_body = clean_txt[:m_eq.start()].strip() if m_eq else clean_txt

            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.right_indent = Inches(0.5)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            r_body = p.add_run(eq_body)
            r_body.font.name = 'Cambria Math'
            r_body.font.italic = True
            r_body.font.size = Pt(10)
            
            if eq_num:
                r_num = p.add_run(f"    {eq_num}")
                r_num.font.name = 'Arial'
                r_num.font.bold = True
                r_num.font.italic = False
                r_num.font.size = Pt(10)
                r_num.font.color.rgb = RGBColor(30, 58, 138)
            i += 1
            continue

        # Detecção de tabelas Markdown
        if line.startswith("|") and line.endswith("|"):
            in_table = True
            table_rows.append([c.strip() for c in line.split("|")[1:-1]])
            i += 1
            continue
        elif in_table:
            if table_rows:
                dados_tabela = [r for r in table_rows if not all(re.match(r'^:?-+:?$', c) for c in r)]
                if dados_tabela:
                    tabela_word = doc.add_table(rows=len(dados_tabela), cols=len(dados_tabela[0]))
                    tabela_word.alignment = WD_TABLE_ALIGNMENT.CENTER
                    for r_idx, row in enumerate(dados_tabela):
                        for c_idx, cell_value in enumerate(row):
                            cell = tabela_word.cell(r_idx, c_idx)
                            cell.text = cell_value
                            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                            p = cell.paragraphs[0]
                            p.paragraph_format.space_before = Pt(2)
                            p.paragraph_format.space_after = Pt(2)
                            run = p.runs[0] if p.runs else p.add_run()
                            run.font.name = 'Arial'
                            run.font.size = Pt(8.5)
                            if r_idx == 0:
                                run.font.bold = True
                                run.font.color.rgb = RGBColor(15, 23, 42)
            table_rows = []
            in_table = False

        if not line:
            i += 1
            continue

        # Título Nível 1
        if line.startswith("# "):
            p = doc.add_paragraph()
            run = p.add_run(line[2:])
            run.font.name = 'Arial'
            run.font.size = Pt(16)
            run.font.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)

        # Título Nível 2
        elif line.startswith("## "):
            p = doc.add_paragraph()
            run = p.add_run(line[3:])
            run.font.name = 'Arial'
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 58, 138)
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)

        # Título Nível 3
        elif line.startswith("### "):
            p = doc.add_paragraph()
            run = p.add_run(line[4:])
            run.font.name = 'Arial'
            run.font.size = Pt(10.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 41, 59)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)

        # Título Nível 4 (ex: Tabela 1: ...)
        elif line.startswith("#### "):
            p = doc.add_paragraph()
            run = p.add_run(line[5:])
            run.font.name = 'Arial'
            run.font.size = Pt(9.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)

        # Citação Longa (Blockquote >) - Recuo 4cm ABNT sem linha lateral
        elif line.startswith("> "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(1.57)  # 4.0 cm
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(line[2:])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.0)
            run.font.italic = False
            run.font.color.rgb = RGBColor(30, 41, 59)

        # Itens de Lista
        elif line.startswith("- "):
            p = doc.add_paragraph(style='List Bullet')
            run = p.add_run(line[2:])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10.0)
            p.paragraph_format.space_after = Pt(2)

        # Blocos de código / algoritmo
        elif line.startswith("```"):
            i += 1
            code_block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_block.append(lines[i])
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run("\n".join(code_block))
            run.font.name = 'Courier New'
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor(30, 41, 59)

        # Parágrafo Normal
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.3
            p.paragraph_format.first_line_indent = Inches(0.4)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = p.add_run(line)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10.0)
            run.font.color.rgb = RGBColor(17, 24, 39)

        i += 1

    doc.save(str(docx_path))
    print(f"✔ Gerado Word: {docx_path.name} ({docx_path.stat().st_size / 1024:.1f} KB)")


def converter_html_formula_para_latex(raw_block: str) -> str:
    """Converte bloco HTML de fórmula para sintaxe matemática LaTeX."""
    # Extrai o número da equação
    m_num = re.search(r'<span class="formula-number">\s*\(([0-9]+)\)\s*</span>', raw_block)
    eq_num = m_num.group(1) if m_num else "1"

    # Extrai o corpo da fórmula
    m_span = re.search(r'<span>(.*?)</span>', raw_block, re.DOTALL)
    if not m_span:
        return ""
    
    eq = m_span.group(1).strip()
    
    # Substituições de entidades HTML para LaTeX
    subs = [
        (r'&sum;', r'\\sum'),
        (r'&prod;', r'\\prod'),
        (r'&delta;', r'\\delta'),
        (r'&beta;', r'\\beta'),
        (r'&eta;', r'\\eta'),
        (r'&alpha;', r'\\alpha'),
        (r'&theta;', r'\\theta'),
        (r'&tau;', r'\\tau'),
        (r'&sigma;', r'\\sigma'),
        (r'&phi;', r'\\phi'),
        (r'&Omega;', r'\\Omega'),
        (r'&Eopf;', r'\\mathbb{E}'),
        (r'&Lscr;', r'\\mathcal{L}'),
        (r'&isin;', r'\\in'),
        (r'&sube;', r'\\subseteq'),
        (r'&setminus;', r'\\setminus'),
        (r'&cup;', r'\\cup'),
        (r'&cap;', r'\\cap'),
        (r'&ge;', r'\\ge'),
        (r'&le;', r'\\le'),
        (r'&forall;', r'\\forall'),
        (r'&implies;', r'\\implies'),
        (r'&middot;', r'\\cdot'),
        (r'&parallel;', r'\\parallel'),
        (r'&nbsp;', r' '),
        (r'p&#770;', r'\\hat{p}'),
        (r'<sub>(.*?)</sub>', r'_{\1}'),
        (r'<sup>(.*?)</sup>', r'^{\1}')
    ]
    for pattern, repl in subs:
        eq = re.sub(pattern, repl, eq)

    # Limpeza adicional
    eq = re.sub(r'<[^>]+>', '', eq)
    eq = re.sub(r'\s+', ' ', eq).strip()

    return f"\\begin{{equation}}\n{eq} \\label{{eq:{eq_num}}}\n\\end{{equation}}"


def markdown_para_latex(md_path: Path, tex_path: Path):
    """Converte arquivo Markdown acadêmico para documento LaTeX (.tex) completo e compilável."""
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    title = md_path.stem.replace("_", " ").title()
    authors = "Eduardo Lopes Jonker, Vivian Kremer Kalempa, Yuri Kaszubowski Lopes"
    institution = "Universidade do Estado de Santa Catarina (UDESC) -- PPGCAP"

    tex_lines = [
        "\\documentclass[10pt,a4paper,journal]{article}",
        "\\usepackage[utf8]{inputenc}",
        "\\usepackage[brazil]{babel}" if "_pt" in md_path.stem or "artigo" in md_path.stem else "\\usepackage[english]{babel}",
        "\\usepackage[margin=2.2cm]{geometry}",
        "\\usepackage{amsmath,amsfonts,amssymb}",
        "\\usepackage{booktabs}",
        "\\usepackage{microtype}",
        "\\usepackage{hyperref}",
        "\\usepackage{caption}",
        "\\usepackage{setspace}",
        "\\onehalfspacing",
        "",
        f"\\title{{{title}}}",
        f"\\author{{{authors}\\\\ \\small {institution}}}",
        "\\date{2026}",
        "",
        "\\begin{document}",
        "\\maketitle",
        ""
    ]

    in_abstract = False
    in_table = False
    table_rows = []
    i = 0

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # Detecção de fórmulas matemáticas numeradas (.formula-box)
        if '<div class="formula-box">' in s:
            formula_lines = [s]
            while i + 1 < len(lines) and '</div>' not in lines[i]:
                i += 1
                formula_lines.append(lines[i].strip())
            raw_block = " ".join(formula_lines)
            tex_eq = converter_html_formula_para_latex(raw_block)
            if tex_eq:
                tex_lines.append(tex_eq)
            i += 1
            continue

        # Resumo / Abstract
        if s.startswith("## Resumo") or s.startswith("## Abstract"):
            in_abstract = True
            tex_lines.append("\\begin{abstract}")
            i += 1
            continue
        elif in_abstract and s.startswith("## "):
            in_abstract = False
            tex_lines.append("\\end{abstract}\n")

        # Tabelas
        if s.startswith("|") and s.endswith("|"):
            in_table = True
            table_rows.append([c.strip() for c in s.split("|")[1:-1]])
            i += 1
            continue
        elif in_table:
            if table_rows:
                dados_tabela = [r for r in table_rows if not all(re.match(r'^:?-+:?$', c) for c in r)]
                if dados_tabela:
                    ncols = len(dados_tabela[0])
                    col_spec = "l" * ncols
                    tex_lines.append("\\begin{table}[htbp]")
                    tex_lines.append("\\centering")
                    tex_lines.append("\\small")
                    tex_lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
                    tex_lines.append("\\toprule")
                    for r_idx, row in enumerate(dados_tabela):
                        escaped_row = [c.replace("%", "\\%").replace("$", "\\$").replace("_", "\\_").replace("&", "\\&") for c in row]
                        tex_lines.append(" & ".join(escaped_row) + " \\\\")
                        if r_idx == 0:
                            tex_lines.append("\\midrule")
                    tex_lines.append("\\bottomrule")
                    tex_lines.append("\\end{tabular}")
                    tex_lines.append("\\end{table}")
            table_rows = []
            in_table = False

        if not s:
            i += 1
            continue

        # Cabeçalhos
        if s.startswith("# "):
            pass
        elif s.startswith("## "):
            sec_name = s[3:].replace("_", "\\_").replace("&", "\\&")
            tex_lines.append(f"\\section{{{sec_name}}}")
        elif s.startswith("### "):
            subsec_name = s[4:].replace("_", "\\_").replace("&", "\\&")
            tex_lines.append(f"\\subsection{{{subsec_name}}}")
        elif s.startswith("#### "):
            par_name = s[5:].replace("_", "\\_").replace("&", "\\&")
            tex_lines.append(f"\\paragraph{{{par_name}}}")
        elif s.startswith("> "):
            quote_text = s[2:].replace("%", "\\%").replace("$", "\\$").replace("_", "\\_").replace("&", "\\&")
            tex_lines.append(f"\\begin{{quote}}\n\\small {quote_text}\n\\end{{quote}}")
        elif s.startswith("- "):
            item_text = s[2:].replace("%", "\\%").replace("$", "\\$").replace("_", "\\_").replace("&", "\\&")
            tex_lines.append(f"\\begin{{itemize}}\n\\item {item_text}\n\\end{{itemize}}")
        elif s.startswith("```"):
            i += 1
            code_block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_block.append(lines[i].replace("%", "\\%").replace("$", "\\$").replace("_", "\\_"))
                i += 1
            tex_lines.append("\\begin{verbatim}")
            tex_lines.extend(code_block)
            tex_lines.append("\\end{verbatim}")
        else:
            p_text = s.replace("%", "\\%").replace("$", "\\$").replace("_", "\\_").replace("&", "\\&")
            tex_lines.append(f"{p_text}\n")

        i += 1

    tex_lines.append("\\end{document}")

    tex_path.write_text("\n".join(tex_lines), encoding="utf-8")
    print(f"✔ Gerado LaTeX: {tex_path.name} ({tex_path.stat().st_size / 1024:.1f} KB)")


def main():
    print("=" * 80)
    print("CONVERTENDO TODOS OS ARTIGOS CIENTÍFICOS NAS SUBPASTAS PARA WORD (.DOCX) E LATEX (.TEX)")
    print("=" * 80)

    md_files = sorted(ARTIGOS_DIR.glob("*/*.md"))

    for md_file in md_files:
        docx_file = md_file.with_suffix(".docx")
        tex_file = md_file.with_suffix(".tex")
        print(f"\n[Convertendo] {md_file.parent.name}/{md_file.name}")
        markdown_para_docx(md_file, docx_file)
        markdown_para_latex(md_file, tex_file)

    print("\n" + "=" * 80)
    print("EXPORTAÇÃO WORD E LATEX NAS SUBPASTAS CONCLUÍDA COM SUCESSO!")
    print("=" * 80)

if __name__ == "__main__":
    main()

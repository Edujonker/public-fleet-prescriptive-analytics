#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera os arquivos LaTeX (.tex) de todos os artigos na pasta SBC/:
- 4 Artigos Curtos (.tex)
- 4 Artigos Completos (.tex)
E cria o pacote sbc-template.sty para compilação autônoma.
"""

import os, re
from pathlib import Path

SBC_DIR = Path("SBC")

# 1. Criar o arquivo sbc-template.sty oficial da SBC
SBC_STY = r"""\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{sbc-template}[2003/04/24 - SBC style template]

\RequirePackage[a4paper,top=3.5cm,left=3cm,right=3cm,bottom=2.5cm]{geometry}
\RequirePackage{times}
\RequirePackage{url}
\RequirePackage{graphicx}
\RequirePackage{booktabs}
\RequirePackage{amsmath,amssymb}
\RequirePackage{caption}
\RequirePackage{setspace}

\setlength{\parindent}{1.27cm}
\setlength{\parskip}{0.0cm}

\pagestyle{empty}

\newcommand{\email}[1]{\texttt{#1}}

\renewcommand{\section}{\@startsection {section}{1}{\z@}%
  {-3.5ex \@plus -1ex \@minus -.2ex}%
  {2.3ex \@plus.2ex}%
  {\normalfont\bfseries}}

\renewcommand{\subsection}{\@startsection{subsection}{2}{\z@}%
  {-3.25ex\@plus -1ex \@minus -.2ex}%
  {1.5ex \@plus .2ex}%
  {\normalfont\bfseries}}

\renewcommand{\subsubsection}{\@startsection{subsubsection}{3}{\z@}%
  {-3.25ex\@plus -1ex \@minus -.2ex}%
  {1.5ex \@plus .2ex}%
  {\normalfont\bfseries}}

\endinput
"""
(SBC_DIR / "sbc-template.sty").write_text(SBC_STY, encoding="utf-8")
print("[OK] SBC LaTeX package criado: SBC/sbc-template.sty")

def md_table_to_latex(block_lines):
    rows = []
    for line in block_lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        if re.match(r'^\|\s*[\:\-\s\|]+$', line):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    
    num_cols = len(rows[0])
    col_spec = "l" + "r" * (num_cols - 1)
    
    tex = ["\\begin{table}[htbp]", "\\centering", "\\small", f"\\begin{{tabular}}{{{col_spec}}}", "\\toprule"]
    # Header
    tex.append(" & ".join([f"\\textbf{{{c}}}" for c in rows[0]]) + " \\\\")
    tex.append("\\midrule")
    for r in rows[1:]:
        # Escape special latex chars
        escaped_cells = []
        for c in r:
            c = c.replace("%", "\\%").replace("_", "\\_").replace("$", "\\$")
            escaped_cells.append(c)
        tex.append(" & ".join(escaped_cells) + " \\\\")
    tex.append("\\bottomrule")
    tex.append("\\end{tabular}")
    tex.append("\\end{table}\n")
    return "\n".join(tex)

def markdown_to_latex(md_content, is_curto=False):
    lines = md_content.split("\n")
    tex_lines = []
    
    # Extrair título
    titulo = "Artigo Científico"
    for l in lines:
        if l.startswith("# "):
            titulo = l.replace("# ", "").strip()
            break
            
    # Extrair Abstract
    m_abs = re.search(r'##\s*Resumo\s*\n(.*?)(?=\n##|\Z)', md_content, re.DOTALL)
    abstract_text = m_abs.group(1).strip() if m_abs else ""
    abstract_text = abstract_text.replace("%", "\\%").replace("_", "\\_").replace("$", "\\$")
    
    # Extrair Palavras-chave
    m_kw = re.search(r'\*\*Palavras-chaves:\*\*\s*(.*?)(?=\n|\Z)', md_content)
    keywords = m_kw.group(1).strip() if m_kw else ""
    keywords = keywords.replace("%", "\\%").replace("_", "\\_").replace("$", "\\$")

    header_tex = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[brazil]{{babel}}
\\usepackage{{sbc-template}}
\\usepackage{{hyperref}}

\\title{{\\textbf{{{titulo}}}}}

\\author{{Eduardo Lopes Jonker\\inst{{1}}, Vivian Kremer Kalempa\\inst{{1}}, Yuri Kaszubowski Lopes\\inst{{1}}}}

\\address{{Centro de Ciências Tecnológicas (CCT) -- Universidade do Estado de Santa Catarina (UDESC)\\\\
  Joinville -- SC -- Brasil\\\\
  \\email{{eduardo.jonker@edu.udesc.br, vivian.kalempa@udesc.br, yuri.lopes@udesc.br}}
}}

\\begin{{document}}

\\maketitle

\\begin{{resumo}}
{abstract_text}

\\vspace{{0.2cm}}
\\noindent\\textbf{{Palavras-chave:}} {keywords}
\\end{{resumo}}

"""
    tex_lines.append(header_tex)
    
    # Processar seções do corpo
    # Ignorar título, autores, metadados e resumo já processados
    body_md = md_content
    # Pegar da primeira seção "## 1." em diante
    m_start = re.search(r'\n##\s+1\.\s+', body_md)
    if m_start:
        body_md = body_md[m_start.start():]
        
    lines_body = body_md.split("\n")
    idx = 0
    while idx < len(lines_body):
        l = lines_body[idx].strip()
        if not l:
            idx += 1
            continue
            
        # H2 -> section
        if l.startswith("## "):
            sec_title = l.replace("## ", "").strip()
            if "referência" in sec_title.lower() or "reference" in sec_title.lower():
                tex_lines.append("\n\\begin{thebibliography}{99}\n")
                idx += 1
                while idx < len(lines_body):
                    r_line = lines_body[idx].strip()
                    if r_line.startswith("-") or r_line.startswith("*"):
                        ref_txt = r_line.lstrip("-* ").strip()
                        ref_txt = ref_txt.replace("%", "\\%").replace("&", "\\&").replace("_", "\\_").replace("$", "\\$")
                        tex_lines.append(f"\\bibitem{{ref{idx}}} {ref_txt}\n")
                    idx += 1
                tex_lines.append("\\end{thebibliography}\n")
                break
            else:
                clean_sec = re.sub(r'^\d+\.\s*', '', sec_title)
                tex_lines.append(f"\n\\section{{{clean_sec}}}\n")
            idx += 1
            continue
            
        # H3 -> subsection
        if l.startswith("### "):
            sub_title = l.replace("### ", "").strip()
            clean_sub = re.sub(r'^\d+\.\d+\s*', '', sub_title)
            tex_lines.append(f"\n\\subsection{{{clean_sub}}}\n")
            idx += 1
            continue
            
        # H4 -> subsubsection
        if l.startswith("#### "):
            sub3_title = l.replace("#### ", "").strip()
            clean_sub3 = re.sub(r'^\d+\.\d+\.\d+\s*', '', sub3_title)
            tex_lines.append(f"\n\\subsubsection{{{clean_sub3}}}\n")
            idx += 1
            continue
            
        # Citações longas em bloco
        if l.startswith(">"):
            bq_lines = []
            while idx < len(lines_body) and lines_body[idx].strip().startswith(">"):
                bq_lines.append(lines_body[idx].strip().lstrip(">").strip())
                idx += 1
            bq_text = " ".join(bq_lines)
            bq_text = bq_text.replace("%", "\\%").replace("_", "\\_").replace("&", "\\&").replace("$", "\\$")
            tex_lines.append(f"\\begin{{quote}}\n\\small {bq_text}\n\\end{{quote}}\n")
            continue
            
        # Tabelas Markdown
        if l.startswith("|"):
            tbl_lines = []
            while idx < len(lines_body) and lines_body[idx].strip().startswith("|"):
                tbl_lines.append(lines_body[idx])
                idx += 1
            tex_table = md_table_to_latex(tbl_lines)
            tex_lines.append(tex_table)
            continue
            
        # Legendas
        if re.match(r'^\*\*(?:Tabela|Figura)\s*\d+.*?\*\*$', l):
            cap_txt = l.replace("**", "").strip()
            cap_txt = cap_txt.replace("%", "\\%").replace("_", "\\_").replace("&", "\\&").replace("$", "\\$")
            tex_lines.append(f"\n\\captionof{{table}}{{{cap_txt}}}\n")
            idx += 1
            continue
            
        # Parágrafos comuns
        p_text = l.replace("%", "\\%").replace("_", "\\_").replace("&", "\\&").replace("$", "\\$")
        tex_lines.append(f"{p_text}\n")
        idx += 1
        
    tex_lines.append("\n\\end{document}\n")
    return "\n".join(tex_lines)

# Processar todos os arquivos .md da pasta SBC e gerar .tex correspondente
md_files = sorted(SBC_DIR.glob("*.md"))
print(f"\nProcessando {len(md_files)} arquivos Markdown em SBC/ para LaTeX (.tex)...")

for md_p in md_files:
    tex_p = md_p.with_suffix(".tex")
    content = md_p.read_text(encoding="utf-8")
    is_curto = "completo" not in md_p.name
    tex_code = markdown_to_latex(content, is_curto=is_curto)
    tex_p.write_text(tex_code, encoding="utf-8")
    print(f"  [OK] LaTeX gerado: {tex_p} ({tex_p.stat().st_size} bytes)")

print("\nTodos os arquivos LaTeX foram gerados com sucesso na pasta SBC/!")
import sys as _s; from pathlib import Path as _P; _s.path.insert(0, str(_P(__file__).resolve().parent))
import uso_etico_ia; uso_etico_ia.gravar_arquivos()  # repõe a seção de uso ético de IA nos artigos

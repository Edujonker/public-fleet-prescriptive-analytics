#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador oficial do relatório técnico-científico do BiblioNow e PBS em formato Word (.docx):
relatorio.biblionow.docx

Reproduz integralmente o conteúdo técnico-científico do relatório:
- Motivação e cronologia de desenvolvimento
- Especificações do ambiente de hardware e linguagens
- Métricas explicativas de decisão PRISMA 2020 (taxonomia de inclusão e descarte)
- Benchmark competitivo de mercado (Zotero, Elicit, SciSpace, Rayyan, etc.)
- Mapeamento BPMN 2.0 dos processos P03 e P04
- Bases de dados e dicionário de metadados
- Camada de segurança da informação (Fernet AES-128, SSRF, CSRF, DNS Rebinding)
- Fundamentação metodológica tripartite (Gil × Volpato × Ferenhof/SSF)
- Métricas de desempenho e governança

Autor: Eduardo Lopes Jonker (PPGCAP / UDESC)
Data: 24 de novembro de 2026
"""

from __future__ import annotations

import os
from pathlib import Path

import docx
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
SAIDA_DOCX = ROOT / "relatorio.biblionow.docx"


def set_cell_background(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def adicionar_caixa_destaque(doc, titulo, texto, cor_borda="1E3A8A", cor_fundo="F8FAFC"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, cor_fundo)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    # Borda esquerda grossa
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{cor_borda}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(titulo + "\n")
    run_t.bold = True
    run_t.font.name = "Arial"
    run_t.font.size = Pt(9.5)
    run_t.font.color.rgb = RGBColor(15, 41, 66)

    run_txt = p.add_run(texto)
    run_txt.font.name = "Arial"
    run_txt.font.size = Pt(9)
    run_txt.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def formatar_tabela_academica(table, col_widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header
    for i, cell in enumerate(table.rows[0].cells):
        set_cell_background(cell, "0F2942")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.bold = True
                r.font.name = "Arial"
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(255, 255, 255)

    # Linhas de dados
    for r_idx, row in enumerate(table.rows[1:], start=1):
        bg = "F8FAFC" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                for r in p.runs:
                    r.font.name = "Arial"
                    r.font.size = Pt(8)

    # Larguras
    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                if idx < len(row.cells):
                    row.cells[idx].width = width


def gerar_docx():
    print("Iniciando geração de relatorio.biblionow.docx...")
    doc = Document()

    # Configuração de Margens (ABNT / Compacto)
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Estilos padrão
    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Arial"
    style_normal.font.size = Pt(9.5)
    style_normal.font.color.rgb = RGBColor(30, 41, 59)

    # Cabeçalho Institucional
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    r1 = p_inst.add_run(
        "UNIVERSIDADE DO ESTADO DE SANTA CATARINA (UDESC) · CENTRO DE CIÊNCIAS TECNOLÓGICAS (CCT)\n"
        "PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA (PPGCAP)\n"
    )
    r1.bold = True
    r1.font.size = Pt(9)
    r1.font.color.rgb = RGBColor(15, 41, 66)

    r_tit = p_inst.add_run("RELATÓRIO TÉCNICO-CIENTÍFICO DO SISTEMA BIBLIONOW\n")
    r_tit.bold = True
    r_tit.font.size = Pt(13)
    r_tit.font.color.rgb = RGBColor(30, 58, 138)

    r_sub = p_inst.add_run(
        "Plataforma Autônoma de Pesquisa Bibliográfica Sistemática (PBS), Download em Lote, "
        "Fichamento Estruturado, PRISMA 2020 e Governança Criptográfica\n"
    )
    r_sub.font.size = Pt(9.5)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    r_aut = p_inst.add_run(
        "Mestrando: Eduardo Lopes Jonker · Orientadora: Profª. Dra. Vivian K. Kalempa · "
        "Coorientador: Prof. Dr. Yuri K. Lopes · 2026"
    )
    r_aut.bold = True
    r_aut.font.size = Pt(8.5)
    r_aut.font.color.rgb = RGBColor(15, 41, 66)

    # Linha divisória
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(2)
    p_div.paragraph_format.space_after = Pt(8)
    r_div = p_div.add_run("―" * 58)
    r_div.font.color.rgb = RGBColor(203, 213, 225)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 1. MOTIVAÇÃO E CONTEXTO
    h1 = doc.add_heading("1. MOTIVAÇÃO, CONTEXTUALIZAÇÃO E CRONOLOGIA DE DESENVOLVIMENTO", level=1)
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(4)
    for r in h1.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 41, 66)

    p1 = doc.add_paragraph(
        "O BiblioNow (pipeline autônomo de Pesquisa Bibliográfica Sistemática — PBS) é uma solução de software "
        "científico concebida, projetada e implementada integralmente pelo mestrando Eduardo Lopes Jonker no âmbito do "
        "PPGCAP/UDESC. A motivação fundamental para o desenvolvimento do sistema surgiu da identificação de um gargalo "
        "crítico no estado da arte: a fragmentação e o alto custo das ferramentas comerciais e acadêmicas de revisão "
        "de literatura. Enquanto o mercado oferece gerenciadores passivos (Zotero, Mendeley) ou assistentes baseados em "
        "IA com caixas-pretas e baixa sensibilidade (Elicit, SciSpace), nenhuma plataforma unifica, em um único ciclo "
        "reprodutível, local e de custo zero, as etapas de busca, download em lote, extração, fichamento e auditoria."
    )
    p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p1.paragraph_format.space_after = Pt(4)

    adicionar_caixa_destaque(
        doc,
        "Cronologia Formal de Desenvolvimento do BiblioNow (2026):",
        "• 14/04/2026: Concepção do protocolo inicial 5W2H e submissão dos primeiros artigos metodológicos (Revista Cajuína A3 e SBSI 2026);\n"
        "• 17/10/2026 a 01/11/2026: Desenvolvimento do motor de busca booleana em lote e conectores OpenAlex / Semantic Scholar;\n"
        "• 14/11/2026: Registro formal do Protocolo de Pesquisa Bibliográfica Sistemática e módulo rsl_prisma.py;\n"
        "• 17/11/2026: Alinhamento com a orientação sobre uso ético de IA e criação do cofre criptográfico Fernet;\n"
        "• 18/11/2026 a 24/11/2026: Implementação do agendador contínuo com janela móvel (2020–2026), auditoria forense SHA-256 e interface web de validação.",
        cor_borda="1E3A8A",
        cor_fundo="F8FAFC"
    )

    # 2. AMBIENTE DE HARDWARE E LINGUAGEM
    h2 = doc.add_heading("2. AMBIENTE DE DESENVOLVIMENTO, LINGUAGENS E DADOS DA MÁQUINA", level=1)
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(4)
    for r in h2.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 41, 66)

    t_hw = doc.add_table(rows=6, cols=3)
    headers_hw = ["Componente / Camada", "Especificação Técnica Real", "Justificativa / Papel no Sistema"]
    for idx, text in enumerate(headers_hw):
        t_hw.cell(0, idx).paragraphs[0].text = text

    dados_hw = [
        ("Linguagem Primária", "Python 3.14.4 (em ambiente virtual isolado .venv)", "Tipagem estática (PEP 585/604), execução assíncrona, dataclasses e interoperabilidade nativa com WeasyPrint e OpenPyXL."),
        ("Linguagens de Suporte", "HTML5 Semântico, CSS3 (Paged Media), SVG, JavaScript (ES6), LaTeX e BibTeX", "Renderização de relatórios forenses em PDF com suporte a paginação contínua e interface web local."),
        ("Sistema Operacional", "Linux x86_64 (Kernel 7.0.0-14-generic, Glibc 2.43)", "Ambiente operacional de produção auditável com suporte a permissões POSIX estritas (0600) para credenciais."),
        ("Processador (CPU)", "13th Gen Intel(R) Core(TM) i5-1334U (12 núcleos lógicos)", "Processamento paralelo concorrente de downloads via ThreadPoolExecutor (10 threads simultâneas de I/O de rede)."),
        ("Memória RAM", "16 GB DDR4 (15.524.328 kB reconhecidos pelo SO)", "Armazenamento em cache de índices JSON de 5.000+ obras e processamento in-memory de PDFs via Poppler (pdftotext).")
    ]
    for row_idx, row_data in enumerate(dados_hw, start=1):
        for col_idx, val in enumerate(row_data):
            t_hw.cell(row_idx, col_idx).paragraphs[0].text = val

    formatar_tabela_academica(t_hw, [Inches(1.8), Inches(2.3), Inches(2.7)])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # 3. MÉTRICA EXPLICATIVA DO PROTOCOLO PRISMA
    h3 = doc.add_heading("3. MÉTRICA EXPLICATIVA DE DECISÃO PRISMA 2020: TAXONOMIA DE INCLUSÃO E DESCARTE", level=1)
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(4)
    for r in h3.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 41, 66)

    p_prisma = doc.add_paragraph(
        "Para garantir a replicabilidade absoluta segundo o Método Lógico de Volpato, o BiblioNow implementa um "
        "motor determinístico de decisão com justificativa causal explícita para cada artigo processado. Todo artigo "
        "recebe um veredito binário acompanhado de um diagnóstico estruturado registrado no inventário:"
    )
    p_prisma.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_prisma.paragraph_format.space_after = Pt(4)

    t_dec = doc.add_table(rows=9, cols=4)
    headers_dec = ["Fase / Critério", "Veredito Computacional", "Regra Algorítmica de Disparo", "Explicação Epistemológica e Causal"]
    for idx, text in enumerate(headers_dec):
        t_dec.cell(0, idx).paragraphs[0].text = text

    dados_dec = [
        ("Deduplicação (CO1)", "DESCARTADO (3.179 registros)", "DOI_norm(A) == DOI_norm(B) ou Title_slug(A) == Title_slug(B)", "Evitar Dupla Contagem: O mesmo trabalho indexado na Scopus, IEEE e Paperpile é consolidado na primeira ocorrência."),
        ("Critério CO2", "DESCARTADO (19 registros)", "idioma not in ['en', 'pt']", "Incompatibilidade Linguística: Descarte de obras em outros idiomas que impeçam auditoria direta pelo pesquisador."),
        ("Critério CO3", "DESCARTADO (196 registros)", "ano < 2020 or ano > 2027", "Janela Temporal Recente: Foco exclusivo no ciclo recente de consolidação da XAI (pós-TreeSHAP) e diretrizes modernas de governança."),
        ("Critério CO4", "DESCARTADO (568 registros)", "tipo in ['editorial', 'note', 'letter', 'book_chapter', 'review_secondary']", "Falta de Revisão por Pares Primária ou Estudo Secundário: Capítulos de livros, editoriais sem dados empíricos e revisões secundárias."),
        ("Triagem CI1", "DESCARTADO", "regex_CI1.search(texto) is None", "Ausência de Analítica Preditivo-Prescritiva: O artigo não aborda tomada de decisão, otimização ou predição de risco."),
        ("Triagem CI2", "DESCARTADO", "regex_CI2.search(texto) is None", "Ausência de Interpretabilidade/XAI: O artigo aborda apenas algoritmos caixa-preta sem mecanismos de explicação."),
        ("Triagem CI3/CI4", "DESCARTADO", "not (match(CI3) or match(CI4))", "Falta de Aderência Governamental/Auditabilidade: Aplicações exclusivamente fabris/médicas sem conexão pública ou fiscal."),
        ("Elegibilidade (Texto Completo)", "INCLUÍDO (274 portfólio)", "CI1 >= 3 ∧ CI2 >= 5 ∧ (CI3 >= 3 ∨ CI4 >= 3) no texto completo", "XAI Não Incidental e Relevância Substantiva: O artigo discute explicabilidade de forma central (>=5 menções) integrada à decisão pública.")
    ]
    for row_idx, row_data in enumerate(dados_dec, start=1):
        for col_idx, val in enumerate(row_data):
            t_dec.cell(row_idx, col_idx).paragraphs[0].text = val

    formatar_tabela_academica(t_dec, [Inches(1.5), Inches(1.5), Inches(1.8), Inches(2.0)])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # 4. DIFERENCIAIS DE MERCADO
    h4 = doc.add_heading("4. DIFERENCIAIS COMPETITIVOS FRENTE ÀS FERRAMENTAS DE MERCADO", level=1)
    h4.paragraph_format.space_before = Pt(8)
    h4.paragraph_format.space_after = Pt(4)
    for r in h4.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 41, 66)

    t_mkt = doc.add_table(rows=5, cols=4)
    headers_mkt = ["Plataforma", "Pontos Fortes Comerciais", "Vulnerabilidades Críticas", "Diferencial do BiblioNow"]
    for idx, text in enumerate(headers_mkt):
        t_mkt.cell(0, idx).paragraphs[0].text = text

    dados_mkt = [
        ("Zotero / Mendeley", "Excelente biblioteca pessoal, plugins para Word/LibreOffice, sincronização em nuvem.", "Captura manual artigo por artigo. Não executam busca booleana em bases nem download em lote; não geram protocolo PRISMA.", "Automação Massiva: Baixa 1.000 artigos/dia em lote legal, extrai TXT, gera BibTeX e planilha consolidada automaticamente."),
        ("Elicit / Consensus / SciSpace", "Perguntas em linguagem natural, síntese de achados via LLMs comerciais.", "Sensibilidade baixíssima (39,5% vs. 94,5% da busca tradicional) em ensaios clínicos (PMC12483133). Custo de US$ 39–49/mês.", "Reprodutibilidade Estrita: Busca booleana formal imutável, custo zero (APIs abertas) e zero alucinação bibliográfica."),
        ("Rayyan / Covidence", "Excelente suporte à triagem cega por múltiplos avaliadores em revisões sistemáticas.", "Começam depois da busca: exigem importação manual de arquivos RIS/CSV. Não baixam textos completos em lote.", "Ponta a Ponta: Integra a busca direta nas bases, o download do PDF e a montagem do inventário de triagem sem fricção de exportação."),
        ("Google Scholar", "Ampla cobertura e indexação abrangente de literatura cinzenta.", "Não possui API pública oficial. Proíbe raspagem automatizada, impondo CAPTCHAs e bloqueio de IP.", "Conformidade Legal: Opera via APIs autorizadas de OpenAlex (250M+ obras) e Semantic Scholar, com links espelho para conferência manual.")
    ]
    for row_idx, row_data in enumerate(dados_mkt, start=1):
        for col_idx, val in enumerate(row_data):
            t_mkt.cell(row_idx, col_idx).paragraphs[0].text = val

    formatar_tabela_academica(t_mkt, [Inches(1.5), Inches(1.7), Inches(1.8), Inches(1.8)])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # 5. ARQUITETURA E SCRIPTS DO PROGRAMA
    h5 = doc.add_heading("5. ARQUITETURA DO SISTEMA, ESTRUTURA DE SCRIPTS E REPOSITÓRIO", level=1)
    h5.paragraph_format.space_before = Pt(8)
    h5.paragraph_format.space_after = Pt(4)
    for r in h5.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 41, 66)

    t_mod = doc.add_table(rows=10, cols=3)
    headers_mod = ["Módulo Python", "Tamanho", "Responsabilidade Arquitetural e Funcionalidades"]
    for idx, text in enumerate(headers_mod):
        t_mod.cell(0, idx).paragraphs[0].text = text

    dados_mod = [
        ("seguranca.py", "8,5 kB", "Cofre criptográfico Fernet (AES-128-CBC + HMAC-SHA-256), proteção anti-SSRF com validação estrita de IP/DNS, defesa anti-CSRF (X-BiblioNow), proteção contra DNS Rebinding e headers CSP."),
        ("nucleo.py", "41,1 kB", "Motor central de busca e download assíncrono. Gerencia filas multi-thread, normaliza metadados, valida assinaturas de arquivos (%PDF), extrai texto integral e despacha para Unpaywall."),
        ("base.py", "41,2 kB", "Camada de abstração de mecanismos de busca acadêmica (MBA). Gerencia conectores OpenAlex e Semantic Scholar com tratamento de rate-limits (HTTP 429) e backoff exponencial."),
        ("fichamento.py", "22,9 kB", "Gerador da planilha de fichamento analítico (.xlsx) com motor openpyxl. Preserva anotações manuais entre re-execuções e sintetiza o Protocolo Sigma em HTML/PDF."),
        ("app.py", "33,4 kB", "Servidor web local e API REST (FastAPI/Starlette). Endpoints para controle de buscas, consulta a logs, gerenciamento de chaves e visualização de status."),
        ("agendador.py", "5,8 kB", "Serviço de execução periódica (cron embutido) para atualizações diárias, semanais ou mensais, recalculando janelas de tempo móveis (ex.: últimos 5 anos)."),
        ("validacao.py", "14,5 kB", "Módulo de auditoria e cálculo de métricas de cobertura (revocação e sensibilidade) frente a listas padrão-ouro de DOIs conhecidos."),
        ("sugestoes.py", "9,1 kB", "Mecanismo de recomendação heurística de termos correlatos e sinônimos científicos para refinamento de strings de busca booleanas."),
        ("relatorio_baixa.py", "15,6 kB", "Sintetizador estatístico de volumetria, taxas de sucesso de download, falhas por paywall e distribuição de licenças Creative Commons.")
    ]
    for row_idx, row_data in enumerate(dados_mod, start=1):
        for col_idx, val in enumerate(row_data):
            t_mod.cell(row_idx, col_idx).paragraphs[0].text = val

    formatar_tabela_academica(t_mod, [Inches(1.6), Inches(1.0), Inches(4.2)])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # 6. SEGURANÇA E AMBIENTE
    h6 = doc.add_heading("6. SEGURANÇA DA INFORMAÇÃO NO AMBIENTE DE DESENVOLVIMENTO", level=1)
    h6.paragraph_format.space_before = Pt(8)
    h6.paragraph_format.space_after = Pt(4)
    for r in h6.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 41, 66)

    adicionar_caixa_destaque(
        doc,
        "Pilares de Engenharia de Software Seguro no BiblioNow:",
        "1. Cofre Criptográfico Fernet: Chaves de API cifradas em cofre.bin via AES-128-CBC + HMAC-SHA-256 com chave mestra no cofre do SO ou permissão POSIX 0600;\n"
        "2. Proteção Anti-SSRF: Bloqueio automático de IPs privados (RFC 1918), loopback e metadados de nuvem a cada salto de redirecionamento HTTP;\n"
        "3. Isolamento Web Local: Servidor vinculado exclusivamente a 127.0.0.1 com validação de Host (anti-DNS Rebinding), tokens de sessão de 256 bits, cabeçalho X-BiblioNow contra CSRF e CSP restritiva;\n"
        "4. Protocolo Sigma: Registro encadeado imutável com hashes SHA-256 acumulados de cada requisição (cryptographic ledger), garantindo integridade e não-repúdio forense.",
        cor_borda="16A34A",
        cor_fundo="F0FDF4"
    )

    # 7. EPISTEMOLOGIA TRIPARTITE: GIL, VOLPATO E FERENHOF
    h7 = doc.add_heading("7. ANÁLISE METODOLÓGICA E EPISTEMOLÓGICA TRIPARTITE: GIL, VOLPATO E FERENHOF (SSF)", level=1)
    h7.paragraph_format.space_before = Pt(8)
    h7.paragraph_format.space_after = Pt(4)
    for r in h7.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 41, 66)

    p_epi_intro = doc.add_paragraph(
        "A sustentação científica e o rigor do BiblioNow e da Pesquisa Bibliográfica Sistemática (PBS) na dissertação "
        "não decorrem de escolhas operacionais ad-hoc ou conveniência tecnológica, mas de uma Articulação Metodológica Tripartite formal "
        "que harmoniza três grandes escolas metodológicas: a taxonomia clássica de Antônio Carlos Gil, a lógica dedutiva e "
        "falseabilidade de Gilson Luiz Volpato e o fluxo processual de engenharia de busca do SystematicSearchFlow (SSF) "
        "formulado por Hélio Aisenberg Ferenhof e Roberto Fabiano Fernandes (atualizado com IA em 2025)."
    )
    p_epi_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_epi_intro.paragraph_format.space_after = Pt(4)

    adicionar_caixa_destaque(
        doc,
        "1. Antônio Carlos Gil — Delineamento e Classificação da Pesquisa:",
        "• Quanto aos Objetivos: Exploratória (investigação das fronteiras emergentes entre XAI e analítica prescritiva) e Descritiva (distribuição temporal, geográfica e algorítmica);\n"
        "• Quanto à Abordagem: Quantitativa e Qualitativa (Mista), unindo contagens PRISMA com síntese substantiva dos achados;\n"
        "• Quanto aos Procedimentos: Bibliográfica Sistemática baseada em periódicos e anais revisados por pares.\n"
        "Papel: Fornece o enquadramento formal institucional da pesquisa.",
        cor_borda="1E3A8A",
        cor_fundo="F8FAFC"
    )

    adicionar_caixa_destaque(
        doc,
        "2. Gilson Luiz Volpato — Método Lógico, Rigor Dedutivo e Falseabilidade:",
        "• Precedência do Conteúdo sobre a Forma: A escrita deve refletir a lógica interna do experimento, sem artifícios retóricos;\n"
        "• Pré-registro Estrito: Formulação de hipóteses, strings e regras de descarte ANTES da coleta de dados, banindo o p-hacking e o viés de confirmação;\n"
        "• Postura Popperiana: Aceitação transparente da refutação de hipóteses como avanço científico legítimo.\n"
        "Papel: Garante a blindagem ética, a dedução prudente e a robustez lógica do argumento.",
        cor_borda="D97706",
        cor_fundo="FFFBEB"
    )

    adicionar_caixa_destaque(
        doc,
        "3. Hélio Aisenberg Ferenhof & Roberto F. Fernandes — SystematicSearchFlow (SSF):",
        "• Engenharia Operacional da Revisão em 4 Fases e 8 Atividades encadeadas: Protocolo (5W2H) ➔ Busca ➔ Seleção (CO/CI) ➔ Síntese/Escrita;\n"
        "• Integração com IA (Atualização 2025): Suporte instrumental de algoritmos sem delegação do julgamento crítico humano;\n"
        "• Auditoria e Rastreabilidade: Documentação antecipada de todas as decisões que afetam a cobertura do corpus.\n"
        "Papel: Fornece a maquinaria processual que o software BiblioNow executa de forma autônoma.",
        cor_borda="16A34A",
        cor_fundo="F0FDF4"
    )

    t_epi = doc.add_table(rows=7, cols=4)
    headers_epi = ["Dimensão Epistêmica", "Antônio Carlos Gil", "Gilson Luiz Volpato", "Ferenhof & Fernandes (SSF)"]
    for idx, text in enumerate(headers_epi):
        t_epi.cell(0, idx).paragraphs[0].text = text

    dados_epi = [
        ("Objeto Central", "Classificação formal, taxonomia e planejamento estrutural da pesquisa científica.", "Coerência lógica do argumento, método dedutivo e falseabilidade de hipóteses.", "Fluxo operacional de busca, seleção, consolidação e escrita da revisão sistemática."),
        ("Pergunta Guia", "Que tipo de pesquisa será realizada e quais os procedimentos formais?", "A conclusão decorre das premissas e resiste ao falseamento popperiano?", "Como localizar, organizar e sintetizar o corpus bibliográfico com rastreabilidade?"),
        ("Unidade de Análise", "Objetivos (exploratória/descritiva) e procedimentos bibliográficos.", "Problema, hipótese, teste empírico e critérios fixados antes da coleta.", "Protocolo 5W2H, string booleana multibase, critérios CO/CI e portfólio."),
        ("Papel na Dissertação", "Classifica a dissertação como empírica, bibliográfica e explicativa mista.", "Exige embargo temporal de 30 dias e critérios estritos pré-registrados.", "Rege as 4 fases do BiblioNow: Protocolo ➔ Busca ➔ Seleção ➔ Síntese/Escrita."),
        ("Limitação Estrutural", "Pouco detalhamento para automação digital e protocolos de revisão sistemática.", "Não prescreve o passo a passo computacional de coleta em APIs e bancos relacionais.", "Risco de degradação científica caso o pesquisador delegue julgamento crítico à IA."),
        ("Resultado Almejado", "Delineamento Claro e enquadramento institucional irretocável.", "Rigor Epistêmico, honestidade intelectual e falseabilidade popperiana.", "Portfólio Rastreável, auditável e reprodutível segundo PRISMA 2020.")
    ]
    for row_idx, row_data in enumerate(dados_epi, start=1):
        for col_idx, val in enumerate(row_data):
            t_epi.cell(row_idx, col_idx).paragraphs[0].text = val

    formatar_tabela_academica(t_epi, [Inches(1.5), Inches(1.7), Inches(1.8), Inches(1.8)])
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # 8. MÉTRICAS DE EXECUÇÃO E CONCLUSÕES
    h8 = doc.add_heading("8. MÉTRICAS DE DESEMPENHO E CONCLUSÕES TÉCNICAS", level=1)
    h8.paragraph_format.space_before = Pt(8)
    h8.paragraph_format.space_after = Pt(4)
    for r in h8.runs:
        r.font.name = "Arial"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(15, 41, 66)

    p_metr = doc.add_paragraph(
        "• Velocidade de Consulta: Resposta média da API OpenAlex em 420 ms por lote; Semantic Scholar com backoff dinâmico de 1,2 s respeitando limites legais;\n"
        "• Capacidade Operacional: Média de 1.000 PDFs em Acesso Aberto recuperados e validados por dia útil sem bloqueios de IP ou CAPTCHAs;\n"
        "• Taxa de Conversão em Texto Bruto: 99,2% dos PDFs íntegros convertidos com sucesso em .txt pelo utilitário Poppler pdftotext (UTF-8);\n"
        "• Integridade do Protocolo Sigma: 100% dos downloads encadeados com hash SHA-256 verificado, garantindo auditoria forense imediata perante a banca examinadora."
    )
    p_metr.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_metr.paragraph_format.space_after = Pt(6)

    adicionar_caixa_destaque(
        doc,
        "SISTEMA BIBLIONOW · PLATAFORMA DE AUTOMAÇÃO DE PESQUISA BIBLIOGRÁFICA SISTEMÁTICA",
        "Desenvolvido no Centro de Ciências Tecnológicas (CCT/UDESC) — Joinville/SC.\n"
        "Documento oficial emitido e certificado em 24 de novembro de 2026.",
        cor_borda="0F2942",
        cor_fundo="F1F5F9"
    )

    doc.save(str(SAIDA_DOCX))
    print(f"✓ Documento Word gerado com sucesso em: {SAIDA_DOCX}")

    # Espelhamento em pastas
    espelho_docs = ROOT / "Documentos" / "relatorio.biblionow.docx"
    doc.save(str(espelho_docs))
    print(f"✓ Cópia espelhada em: {espelho_docs}")


if __name__ == "__main__":
    gerar_docx()

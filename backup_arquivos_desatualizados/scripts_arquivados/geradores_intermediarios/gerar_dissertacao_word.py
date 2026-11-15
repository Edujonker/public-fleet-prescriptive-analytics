#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
GERADOR DA DISSERTAÇÃO DE MESTRADO EM MICROSOFT WORD (.DOCX) - VERSÃO FINAL CONGELADA
PPGCAP / CCT / UDESC, EDUARDO LOPES JONKER
NORMAS ABNT (NBR 14724, NBR 6024, NBR 6027, NBR 6023)
================================================================================
"""

import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "Documentos"
RELATORIOS_DIR = BASE_DIR / "relatorios"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

OUT_DOCX = BASE_DIR / "dissertacao_versao_final_congelada.docx"

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_dissertation_docx():
    print("Iniciando geração do documento Word (.docx) da Dissertação...")
    doc = docx.Document()

    # Configuração de Margens ABNT (3cm superior e esquerda, 2cm inferior e direita)
    for section in doc.sections:
        section.top_margin = Inches(1.181)     # 3.0 cm
        section.left_margin = Inches(1.181)    # 3.0 cm
        section.bottom_margin = Inches(0.787)  # 2.0 cm
        section.right_margin = Inches(0.787)   # 2.0 cm
        section.page_width = Inches(8.267)     # A4
        section.page_height = Inches(11.692)

    # Configuração de Estilos Básicos
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Arial'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.5
    style_normal.paragraph_format.space_after = Pt(6)
    style_normal.paragraph_format.space_before = Pt(0)

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line=True, bold_prefix="", italic=False):
        p = doc.add_paragraph()
        p.alignment = align
        if first_line:
            p.paragraph_format.first_line_indent = Inches(0.492) # 1.25 cm
        else:
            p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(6)
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
        if text:
            r_t = p.add_run(text)
            r_t.italic = italic
        return p

    def add_h1(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.first_line_indent = Inches(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title.upper())
        r.bold = True
        r.font.size = Pt(12)
        return p

    def add_h2(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(9)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.first_line_indent = Inches(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.size = Pt(12)
        return p

    def add_h3(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(7)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.first_line_indent = Inches(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.italic = True
        r.font.size = Pt(12)
        return p

    def add_box(title, text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)
        r_title = p.add_run(title + "\n")
        r_title.bold = True
        r_title.font.size = Pt(9.5)
        r_title.font.color.rgb = RGBColor(15, 23, 42)
        r_txt = p.add_run(text)
        r_txt.font.size = Pt(9)
        r_txt.font.color.rgb = RGBColor(51, 65, 85)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # =========================================================================
    # 1. ELEMENTOS PRÉ-TEXTUAIS
    # =========================================================================

    # CAPA
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run(
        "UNIVERSIDADE DO ESTADO DE SANTA CATARINA, UDESC\n"
        "CENTRO DE CIÊNCIAS TECNOLÓGICAS, CCT\n"
        "PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA, PPGCAP\n"
        "MESTRADO ACADÊMICO EM COMPUTAÇÃO APLICADA\n"
        "LINHA DE PESQUISA: METODOLOGIA E TÉCNICAS DE COMPUTAÇÃO (MTC)\n\n\n"
        "EDUARDO LOPES JONKER\n\n\n\n"
    )
    r.bold = True
    r.font.size = Pt(11)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tit = p_tit.add_run("ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO\n")
    r_tit.bold = True
    r_tit.font.size = Pt(13)
    r_sub = p_tit.add_run("Estudo Comparativo e Aplicado com Dados de Manutenção, Patrimônio, Abastecimento e Governança Governamental\n\n\n\n\n\n\n\n")
    r_sub.font.size = Pt(11)

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_loc = p_loc.add_run("JOINVILLE, SC\n2026")
    r_loc.bold = True
    r_loc.font.size = Pt(11)

    doc.add_page_break()

    # FOLHA DE ROSTO
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("EDUARDO LOPES JONKER\n\n\n")
    r.bold = True
    r.font.size = Pt(11)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tit = p_tit.add_run("ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO\n")
    r_tit.bold = True
    r_tit.font.size = Pt(13)
    r_sub = p_tit.add_run("Estudo Comparativo e Aplicado com Dados de Manutenção, Patrimônio, Abastecimento e Governança Governamental\n\n")
    r_sub.font.size = Pt(11)

    # Natureza do trabalho (recuo de 8 cm da margem esquerda)
    p_nat = doc.add_paragraph()
    p_nat.paragraph_format.left_indent = Inches(3.15) # 8 cm
    p_nat.paragraph_format.line_spacing = 1.15
    p_nat.paragraph_format.first_line_indent = Inches(0)
    p_nat.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_nat = p_nat.add_run(
        "Dissertação apresentada ao Programa de Pós-Graduação em Computação Aplicada (PPGCAP) "
        "do Centro de Ciências Tecnológicas (CCT) da Universidade do Estado de Santa Catarina (UDESC), "
        "como requisito parcial para a obtenção do grau de Mestre em Computação Aplicada.\n\n"
        "Área de Concentração: Computação Aplicada\n"
        "Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC)\n"
        "Orientadora: Profa. Dra. Vivian Kremer Kalempa\n\n\n\n\n"
    )
    r_nat.font.size = Pt(10)

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_loc = p_loc.add_run("JOINVILLE, SC\n2026")
    r_loc.bold = True
    r_loc.font.size = Pt(11)

    doc.add_page_break()

    # FICHA CATALOGRÁFICA
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(200)

    tbl_ficha = doc.add_table(rows=1, cols=1)
    tbl_ficha.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_f = tbl_ficha.cell(0, 0)
    set_cell_margins(cell_f, top=150, bottom=150, left=200, right=200)
    p_f = cell_f.paragraphs[0]
    p_f.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_f.paragraph_format.line_spacing = 1.2
    p_f.paragraph_format.first_line_indent = Inches(0)
    r_f = p_f.add_run(
        "Jonker, Eduardo Lopes\n"
        "    Analítica Prescritiva, Teoria dos Grafos e Inteligência Artificial Explicável "
        "para a Gestão de Frota Veicular no Setor Público / Eduardo Lopes Jonker., 2026.\n"
        "    120 p. : il. ; 30 cm.\n\n"
        "    Orientadora: Vivian Kremer Kalempa.\n"
        "    Dissertação (Mestrado), Universidade do Estado de Santa Catarina, Centro de "
        "Ciências Tecnológicas, Programa de Pós-Graduação em Computação Aplicada, Joinville, 2026.\n\n"
        "    1. Gestão de frotas públicas. 2. Pesquisa operacional (MILP). 3. Aprendizado de máquina. "
        "4. Teoria dos grafos. 5. Inteligência artificial explicável. I. Kalempa, Vivian Kremer. "
        "II. Universidade do Estado de Santa Catarina. Programa de Pós-Graduação em Computação Aplicada. III. Título."
    )
    r_f.font.size = Pt(9.5)

    doc.add_page_break()

    # FOLHA DE APROVAÇÃO (Composição da Banca Formal UDESC)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("EDUARDO LOPES JONKER\n\n")
    r.bold = True
    r.font.size = Pt(11)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tit = p_tit.add_run("ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO\n\n")
    r_tit.bold = True
    r_tit.font.size = Pt(12)

    p_aprov = doc.add_paragraph()
    p_aprov.paragraph_format.left_indent = Inches(3.15)
    p_aprov.paragraph_format.line_spacing = 1.15
    p_aprov.paragraph_format.first_line_indent = Inches(0)
    p_aprov.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_ap = p_aprov.add_run(
        "Esta Dissertação foi apresentada como requisito parcial para a obtenção do título de "
        "Mestre em Computação Aplicada perante a Comissão Examinadora do Programa de Pós-Graduação "
        "em Computação Aplicada da Universidade do Estado de Santa Catarina.\n\n"
    )
    r_ap.font.size = Pt(10)

    p_data = doc.add_paragraph()
    p_data.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_data.add_run("Joinville, SC, ____ de ______________ de 2026.\n\n\n")

    for nome, cargo in [
        ("Profa. Dra. Vivian Kremer Kalempa", "Orientadora e Presidente da Banca Examinadora, UDESC / CCT"),
        ("Membro Avaliador Interno", "Programa de Pós-Graduação em Computação Aplicada, UDESC / CCT"),
        ("Membro Avaliador Externo", "Comissão Examinadora, Instituição Externa à UDESC")
    ]:
        p_banca = doc.add_paragraph()
        p_banca.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_banca.paragraph_format.line_spacing = 1.15
        p_banca.paragraph_format.first_line_indent = Inches(0)
        p_banca.add_run("_____________________________________________________\n")
        r_n = p_banca.add_run(nome + "\n")
        r_n.bold = True
        r_c = p_banca.add_run(cargo + "\n\n")
        r_c.font.size = Pt(10)

    doc.add_page_break()

    # DEDICATÓRIA E AGRADECIMENTOS
    p_ded = doc.add_paragraph()
    p_ded.paragraph_format.space_before = Pt(300)
    p_ded.paragraph_format.left_indent = Inches(3.5)
    p_ded.paragraph_format.line_spacing = 1.2
    r_ded = p_ded.add_run(
        "Dedicado a todos os servidores públicos estaduais que, com diligência e dedicação diária, "
        "zelam pelo patrimônio público e pela segurança da sociedade catarinense."
    )
    r_ded.italic = True
    r_ded.font.size = Pt(10)

    doc.add_page_break()

    add_h2("AGRADECIMENTOS")
    add_p("À Universidade do Estado de Santa Catarina (UDESC) e aos professores e coordenadores do PPGCAP pelo suporte acadêmico de excelência.")
    add_p("À minha orientadora, Profa. Dra. Vivian Kremer Kalempa, pela condução rigorosa, paciência metodológica e incentivo constante ao aprofundamento científico.")
    add_p("À Diretoria de Gestão Patrimonial da Secretaria de Estado da Administração de Santa Catarina (SEA/SC) e aos servidores da Gerência de Frotas pelo apoio institucional e franqueamento dos dados para esta pesquisa.")
    add_p("Aos meus familiares e amigos pela compreensão durante as incontáveis horas dedicadas a este projeto.")

    doc.add_page_break()

    # RESUMO
    add_h2("RESUMO")
    add_p(
        "A gestão de frotas públicas enfrenta restrições orçamentárias severas, assimetria de informações e dispersão geográfica de ordens de serviço. "
        "Esta dissertação propõe e avalia um arcabouço analítico prescritivo integrado orientado a frotas públicas sob a Lei Federal nº 14.133/2021. "
        "A base empírica compreende 77.867 ordens de serviço (350.737 itens saneados) e 34.280 veículos do Estado de Santa Catarina (2020–2026), "
        "além de dados cadastrais e de abastecimento. A metodologia articula: (i) auditoria e saneamento com isolamento de R$ 60,05 milhões históricos retidos em glosas contratuais; "
        "(ii) detecção não supervisionada de anomalias (Isolation Forest), identificando 662 ordens atípicas (0,85%); (iii) modelagem preditiva multimodal e avaliação em janela expansiva com embargo temporal de 30 dias; "
        "(iv) explicabilidade local e global (SHAP e LIME); (v) modelagem de redes complexas via comunidade Louvain (Q = 0,5646); e (vi) otimização inteira mista (MILP) resolvida via HiGHS. "
        "Os resultados demonstraram convergência para o ótimo global com Gap de 0,0000% e gap de integralidade poliedral quase-nulo de 0,00057% (R$ 248,52), com redução teórica estimada de 17,51% (R$ 9,30 milhões) "
        "no Cenário S0 em relação à política inercial sob os limites orçamentários simulados. Na avaliação epistemológica: a Hipótese H1 foi classificada como Não Sustentada segundo o critério prático de corte (15%), "
        "apesar de significância estatística (p < 10^-6); H2 foi Parcialmente Sustentada; H3 foi Sustentada no cenário simulado; e H4 foi Não Sustentada (concordância Top-5 de Jaccard de 39,29%), "
        "evidenciando a necessidade imperativa de triangulação analítica multimetodológica perante órgãos de controle público."
    )
    p_kw = add_p("Palavras-chave: ", first_line=False)
    p_kw.runs[0].bold = True
    p_kw.add_run("Gestão de frotas públicas. Programação linear inteira mista. Aprendizado de máquina. Teoria dos grafos. Inteligência artificial explicável. Reprodutibilidade científica.")

    doc.add_page_break()

    # ABSTRACT
    add_h2("ABSTRACT")
    add_p(
        "Public fleet management faces severe fiscal constraints, information asymmetry, and geographic dispersion of work orders. "
        "This dissertation proposes and evaluates an integrated prescriptive analytics framework for public fleets under Federal Law 14,133/2021. "
        "The empirical dataset comprises 77,867 work orders (350,737 cleaned items) and 34,280 vehicles from the State of Santa Catarina (2020–2026), "
        "alongside asset registries and fueling logs. The methodology articulates: (i) auditing and data curation with R$ 60.05 million in historical contract disallowances; "
        "(ii) unsupervised anomaly detection (Isolation Forest), identifying 662 atypical orders (0.85%); (iii) multimodal predictive modeling evaluated under an expanding window with a 30-day embargo; "
        "(iv) local and global explainability (SHAP and LIME); (v) complex network modeling via Louvain community detection (Q = 0.5646); and (vi) mixed-integer linear programming (MILP) solved via HiGHS. "
        "Results demonstrated convergence to the global optimum with a 0.0000% optimality gap and near-zero integrality gap of 0.00057% (R$ 248.52), yielding an estimated 17.51% (R$ 9.30 million) theoretical cost reduction "
        "in Scenario S0 relative to inertial baseline under simulated budget caps. Regarding hypotheses: H1 was Not Sustained under practical decision criteria (15% threshold) despite statistical significance (p < 10^-6); "
        "H2 was Partially Sustained; H3 was Sustained under simulated conditions; and H4 was Not Sustained (Top-5 Jaccard similarity of 39.29%), proving the imperative need for multi-methodological triangulation in public governance."
    )
    p_kw = add_p("Keywords: ", first_line=False)
    p_kw.runs[0].bold = True
    p_kw.add_run("Public fleet management. Mixed-integer linear programming. Machine learning. Graph theory. Explainable AI. Computational reproducibility.")

    doc.add_page_break()

    # SUMÁRIO
    add_h2("SUMÁRIO")
    sumario_itens = [
        ("1 INTRODUÇÃO, CONTEXTUALIZAÇÃO E ANTEPROJETO DE PESQUISA", "14"),
        ("2 FUNDAMENTAÇÃO TEÓRICA, MARCO REGULATÓRIO E REVISÃO DA LITERATURA", "15"),
        ("  2.1 Marco Regulatório e Governança da Gestão de Frotas Públicas em Santa Catarina", "15"),
        ("  2.2 Revisão Estruturada da Literatura e Análise Crítica de 40 Trabalhos", "16"),
        ("    2.2.1 Análise Transversal das Obras Selecionadas", "18"),
        ("    2.2.2 Análise de Lacunas e Oportunidades Metodológicas", "24"),
        ("  2.3 Fundamentos Teóricos Estruturantes Complementares", "26"),
        ("3 METODOLOGIA CRISP-DM, BASE EMPÍRICA MULTIMODAL E SANEAMENTO", "27"),
        ("  3.1 Composição da Base Empírica e Estrutura Contábil do Dispêndio", "27"),
        ("  3.2 Distribuição Temporal, Integridade dos Registros e Controle de Vazamento", "28"),
        ("  3.3 Protocolo Exaustivo de Validação Temporal em 5 Dobras Sequenciais (Expanding-Window)", "30"),
        ("  3.4 Protocolo de Anonimização, Pseudonimização e Conformidade com a LGPD", "32"),
        ("  3.5 Plano de Auditoria Metodológica e Resolução dos Critérios de Rigor Científico", "32"),
        ("  3.6 Matriz de Rastreabilidade Científica Integral", "34"),
        ("  3.7 Tabela Única de Resultados Oficiais e Evidências Experimentais Auditadas", "36"),
        ("  3.8 Desenho Experimental Ablativo Multinível (E0 a E5)", "41"),
        ("4 DETECÇÃO NÃO SUPERVISIONADA DE ANOMALIAS E AUDITORIA FISCAL", "44"),
        ("  4.1 Calibração da Taxa de Contaminação e Estabilidade do Isolation Forest", "45"),
        ("5 CLASSIFICAÇÃO NÃO LINEAR DE RISCO OPERACIONAL (HIPÓTESE H2)", "47"),
        ("  5.1 Comparação Pareada de Curvas ROC via Teste de DeLong", "48"),
        ("6 REGRESSÃO NÃO LINEAR DE CUSTOS E CONFRONTO COM SVR-RBF (HIPÓTESE H2)", "51"),
        ("  6.1 Benchmark Comparativo de Regressores e Erro Padrão do MAE", "51"),
        ("  6.2 Teste Não Paramétrico de Wilcoxon Signed-Rank com Correção de Holm", "52"),
        ("  6.3 Estudo Ablativo Multimodal e Avaliação Epistemológica da Hipótese H1", "53"),
        ("  6.4 Regressão Não Paramétrica de Passing-Bablok (1983)", "54"),
        ("7 MODELAGEM TEMPORAL, DECOMPOSIÇÃO E PREVISÃO DE DEMANDA", "56"),
        ("8 INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL (XAI), TRIANGULAÇÃO E CONFIABILIDADE (HIPÓTESE H4)", "58"),
        ("9 OTIMIZAÇÃO PRESCRITIVA (MILP), PROTOCOLO CENÁRIO S0 E DECISÃO SOB RESTRIÇÕES (HIPÓTESE H3)", "60"),
        ("  9.1 Benchmark Experimental das 7 Políticas de Gestão, Cenário de Referência S0", "60"),
        ("  9.2 Análise de Robustez e Sensibilidade Estocástica de Monte Carlo (1.000 Iterações)", "63"),
        ("  9.3 Auditoria Matemática da Relaxação Linear (LP), Gap de Integralidade e Gargalos Ativos", "64"),
        ("  9.4 Curva de Sensibilidade Paramétrica e Fronteira de Saturação Orçamentária", "64"),
        ("10 TEORIA DOS GRAFOS & REDES COMPLEXAS NA GESTÃO DE FROTAS PÚBLICAS", "67"),
        ("11 GOVERNANÇA PÚBLICA, MATRIZ DOS 38 INDICADORES GFI E CARTILHA SEA 2026", "71"),
        ("  11.1 Projeção Orçamentária Trienal (2027–2029) com Inflação Setorial Ponderada", "75"),
        ("12 GALERIA EXAUSTIVA E ANÁLISE EXPLICATIVA DAS FIGURAS DA PESQUISA", "76"),
        ("13 CONCLUSÕES, SUSTENTAÇÃO DAS HIPÓTESES E RECOMENDAÇÕES ACADÊMICAS", "109"),
        ("  13.1 Validade Externa, Condições de Contorno e Generalização da Arquitetura Prescritiva", "111"),
        ("REFERÊNCIAS", "114"),
        ("APÊNDICE A, FORMULAÇÃO MATEMÁTICA COMPLETA E LINEARIZADA DO SOLVER MILP", "117"),
        ("APÊNDICE B, PROTOCOLO DE AUDITORIA E INTEGRIDADE PÚBLICA DA SEA DITI", "118"),
        ("APÊNDICE C, CADERNO METODOLÓGICO DE REPRODUTIBILIDADE E DIRETRIZES ACM/INFORMS", "119"),
        ("  Apêndice C.1, Registro Factual de Execuções e Portabilidade Multiplataforma", "119"),
        ("  Apêndice C.2, Comprovação de Reprodutibilidade via Trilha de Logs e Artefatos Originais", "120"),
    ]

    tbl_sum = doc.add_table(rows=len(sumario_itens), cols=2)
    tbl_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (tit, pag) in enumerate(sumario_itens):
        row = tbl_sum.rows[idx]
        c_tit, c_pag = row.cells[0], row.cells[1]
        c_tit.width = Inches(6.5)
        c_pag.width = Inches(0.8)
        p_t = c_tit.paragraphs[0]
        p_t.paragraph_format.line_spacing = 1.15
        p_t.paragraph_format.space_after = Pt(2)
        p_t.paragraph_format.first_line_indent = Inches(0)
        r_t = p_t.add_run(tit)
        if not tit.startswith("  "):
            r_t.bold = True
        p_p = c_pag.paragraphs[0]
        p_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_p.paragraph_format.line_spacing = 1.15
        p_p.paragraph_format.space_after = Pt(2)
        p_p.paragraph_format.first_line_indent = Inches(0)
        r_p = p_p.add_run(pag)
        if not tit.startswith("  "):
            r_p.bold = True

    doc.add_page_break()

    # =========================================================================
    # 2. ELEMENTOS TEXTUAIS (CAPÍTULOS 1 A 13)
    # =========================================================================

    # CAPÍTULO 1
    add_h1("1 INTRODUÇÃO, CONTEXTUALIZAÇÃO E ANTEPROJETO DE PESQUISA")
    add_p("A gestão de uma frota institucional no setor público exige conciliar disponibilidade física dos veículos, segurança dos servidores e cidadãos, manutenção mecânica, consumo de combustíveis e rigorosos limites orçamentários fixados pela Lei de Responsabilidade Fiscal (LRF) e pela Nova Lei de Licitações (Lei Federal nº 14.133/2021). Essas dimensões deixam vestígios em sistemas administrativos distintos: o cadastro patrimonial identifica características do bem; as ordens de serviço registram peças, mão de obra e falhas; e o módulo de abastecimento informa volume, preço e odômetro.")
    add_p("Historicamente, a fragmentação cadastral e a ausência de modelos analíticos integrados limitaram a gestão a rotinas reativas emergenciais. A literatura aponta que a manutenção preditiva e a analítica prescritiva oferecem meios para antecipar falhas e otimizar recursos, mas enfrentam desafios de qualidade de dados, explicabilidade perante órgãos de controle e formulação sob restrições reais de governo (MAHALE; KOLHAR; MORE, 2025).")
    add_p("As Quatro Hipóteses Centrais de Pesquisa (H1 a H4) e Critérios Formais de Avaliação:", bold_prefix="Hipóteses de Trabalho: ")
    add_p("• Hipótese H1 (Integração Multimodal): Conforme formulada originalmente no anteprojeto de pesquisa, a modelagem preditiva multimodal (integrando manutenção, cadastro patrimonial e abastecimento) propõe que a fusão de bases heterogêneas reduz o erro de predição de custo e eleva o PR-AUC frente a modelos restritos exclusivamente a ordens de serviço. Na avaliação experimental, separa-se a comprovação de significância estatística do teste pareado da sua relevância prática operacional (adotando-se na discussão o patamar referencial de 15,0% de ganho como critério analítico de corte para justificar os custos operacionais de integração contínua de dados legados no setor público).")
    add_p("• Hipótese H2 (Superioridade dos Modelos Não Lineares): Modelos ensemble baseados em árvores (HistGradientBoosting e Extra Trees) superam o regressor vetorial de suporte com núcleo radial (Support Vector Regression - SVR-RBF) e baselines lineares paramétricos em tempo de treinamento computacional e métricas preditivas de erro sob distribuição empírica assimétrica não Gaussiana.")
    add_p("• Hipótese H3 (Eficácia Prescritiva do MILP): A programação linear inteira mista (MILP) orientada por previsões probabilísticas calibradas gera um plano ótimo de intervenções preventivas com custo total esperado estimado como inferior à política inercial em cenário simulado sob os mesmos limites orçamentários, garantindo disponibilidade operacional e cumprimento das revisões obrigatórias.")
    add_p("• Hipótese H4 (Concordância e Auditabilidade da XAI): As atribuições de importância local e global produzidas pelos métodos de inteligência artificial explicável SHAP (valores de Shapley) e LIME (aproximação linear local) exibem convergência estrutural estrita (>85% de similaridade de Jaccard Top-5), viabilizando sua intercambialidade direta e auditabilidade perante órgãos de controle público (TCE-SC).")

    # CAPÍTULO 2
    add_h1("2 FUNDAMENTAÇÃO TEÓRICA, MARCO REGULATÓRIO E REVISÃO DA LITERATURA")
    add_h2("2.1 Marco Regulatório e Governança da Gestão de Frotas Públicas em Santa Catarina")
    add_p("A administração de veículos públicos no Estado de Santa Catarina submete-se a um arcabouço normativo composto pela Lei Federal nº 14.133/2021 (Nova Lei de Licitações), pelos Decretos Estaduais nº 1.488/2008 e nº 2.056/2009 e pelas diretrizes da Secretaria de Estado da Administração (SEA/SC). Esse arcabouço estabelece regras para contratação de manutenção, gestão de abastecimento, controle patrimonial e critérios de antieconomicidade.")
    add_h2("2.2 Revisão Estruturada da Literatura e Análise Crítica de 40 Trabalhos")
    add_p("Realizou-se uma revisão estruturada da literatura contemplando 40 obras científicas de referência (1998–2026), classificadas em: Classe A (Fundamentais, 13 obras, 32,5%), Classe B (Complementares Relevantes, 17 obras, 42,5%) e Classe C (Contextuais, 10 obras, 25,0%).")
    add_box(
        "Ressalva Metodológica sobre o Corpus Bibliográfico:",
        "Em estrito rigor epistemológico, adota-se a denominação 'revisão estruturada da literatura' sob síntese temática e integradora, reunindo pesquisa operacional, aprendizado de máquina e governança pública."
    )

    # CAPÍTULO 3
    add_h1("3 METODOLOGIA CRISP-DM, BASE EMPÍRICA MULTIMODAL E SANEAMENTO")
    add_h2("3.1 Composição da Base Empírica e Estrutura Contábil do Dispêndio")
    add_p("A pesquisa apoia-se em dados administrativos reais de Santa Catarina entre 2020 e 2026: 77.867 ordens de serviço (350.737 itens) correspondendo a R$ 198,81 milhões em dispêndio orçado inicial, dos quais R$ 60,05 milhões representam valores históricos de glosas fiscais e auditorias prévias registradas pela SEA/SC (30,2%) e R$ 138,76 milhões foram efetivamente liquidados (69,8%).")
    add_box(
        "Distinção Contábil entre Glosas Retidas e Economia Realizada:",
        "Ressalta-se que valores de glosas retidas por fiscalização prévia representam contenção de faturamento indevido no fluxo administrativo contratual e não devem ser confundidos com economia líquida realizada de caixa."
    )
    add_h2("3.3 Protocolo Exaustivo de Validação Temporal em 5 Dobras Sequenciais (Expanding-Window)")
    add_p("A avaliação dos modelos preditivos adotou validação cruzada temporal em janela expansiva de 5 dobras sequenciais com embargo temporal de 30 dias entre treino e teste para blindagem contra vazamento de dados (data leakage).")
    add_box(
        "Harmonização Metodológica das Métricas PR-AUC Reportadas:",
        "O valor médio de PR-AUC de 0,8941 ± 0,021 reflete a média das 5 dobras sequenciais na validação temporal cruzada (Protocolo A); o valor pontual de 0,9510 corresponde à partição out-of-time do holdout de teste temporal (Protocolo B)."
    )

    # CAPÍTULOS 4 A 8
    add_h1("4 DETECÇÃO NÃO SUPERVISIONADA DE ANOMALIAS E AUDITORIA FISCAL")
    add_p("O Isolation Forest foi calibrado com taxa de contaminação de 0,85%, isolando 662 ordens de serviço atípicas com desvios superiores a 2 desvios-padrão da mediana regional.")

    add_h1("5 CLASSIFICAÇÃO NÃO LINEAR DE RISCO OPERACIONAL (HIPÓTESE H2)")
    add_p("O modelo HistGradientBoosting atingiu ROC-AUC de 0,8743 e PR-AUC de 0,9510, superando significativamente a regressão logística (DeLong p < 10^-50).")

    add_h1("6 REGRESSÃO NÃO LINEAR DE CUSTOS E CONFRONTO COM SVR-RBF (HIPÓTESE H2)")
    add_p("Os modelos baseados em árvores superaram o SVR-RBF (MAE de R$ 2.236,06 vs R$ 2.569,20; p < 10^-4). O estudo ablativo demonstrou ganho preditivo de 1,13% no teste out-of-time (Wilcoxon p < 10^-6), abaixo do limiar prático de 15%, classificando a Hipótese H1 como Não Sustentada segundo o critério de relevância prática.")

    add_h1("7 MODELAGEM TEMPORAL, DECOMPOSIÇÃO E PREVISÃO DE DEMANDA")
    add_p("A decomposição sazonal STL das séries mensais de manutenção (2020–2026) isolou componentes de tendência, sazonalidade e ruído estocástico, parametrizando as demandas mensais do MILP.")

    add_h1("8 INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL (XAI), TRIANGULAÇÃO E CONFIABILIDADE (HIPÓTESE H4)")
    add_p("A concordância entre SHAP e LIME resultou em índice de Jaccard Top-5 de 39,29% e Spearman rho = 0,3680, rejeitando a Hipótese H4 (>85%) e demonstrando a imperatividade de triangulação metodológica.")

    # CAPÍTULO 9
    add_h1("9 OTIMIZAÇÃO PRESCRITIVA (MILP), PROTOCOLO CENÁRIO S0 E DECISÃO SOB RESTRIÇÕES (HIPÓTESE H3)")
    add_h2("9.1 Benchmark Experimental das 7 Políticas de Gestão, Cenário de Referência S0")
    add_p("A política MILP-1 atingiu custo total ótimo de R$ 43.837.633,31 frente ao custo inercial de R$ 53.139.780,57, propiciando economia teórica simulada de R$ 9.302.147,26 (17,51%), com 95,26% de disponibilidade física e 100% de manutenções mandatórias atendidas.")
    add_h2("9.3 Auditoria Matemática da Relaxação Linear (LP), Gap de Integralidade e Gargalos Ativos")
    add_p("A confrontação entre a solução inteira exata (x_it in {0, 1}) e a relaxação linear (x_it in [0, 1]) revelou um gap de integralidade quase-nulo de 0,00057% (R$ 248,52), confirmando formulação quase-ideal.")
    add_box(
        "Análise de Preços-Sombra (Shadow Prices) e Capacidade de Oficinas:",
        "Os multiplicadores duais foram extraídos da relaxação linear contínua (LP) da instância S0. Ressalva-se que, em problemas inteiros, não há teoria de dualidade forte equivalente: os preços-sombra da LP constituem indicadores aproximados de sensibilidade e não devem ser interpretados como efeitos marginais exatos no problema MILP, cuja resposta a variações orçamentárias é descontínua e deve ser aferida por reotimização paramétrica (Seção 9.4). Por sua vez, a restrição de capacidade das oficinas (H_t) não foi vinculante em nenhum mês da simulação (0,0% dos meses, multiplicador dual nulo). Esse resultado indica apenas que, sob os parâmetros agregados de capacidade adotados no cenário S0, o orçamento antecede a capacidade como restrição limitante; ele não comprova a existência de capacidade ociosa real em toda a rede credenciada catarinense, pois H_t foi parametrizado de forma agregada e não captura gargalos locais, sazonais, de especialidade mecânica ou de distância geográfica entre unidades e oficinas."
    )

    # CAPÍTULOS 10 A 12
    add_h1("10 TEORIA DOS GRAFOS & REDES COMPLEXAS NA GESTÃO DE FROTAS PÚBLICAS")
    add_p("A rede bipartida de 7.291 veículos e 1.039 oficinas credenciadas revelou 18 comunidades Louvain com modularidade Q = 0,5646, orientando fiscalizações periciais.")

    add_h1("11 GOVERNANÇA PÚBLICA, MATRIZ DOS 38 INDICADORES GFI E CARTILHA SEA 2026")
    add_p("Estruturou-se a matriz dos 38 indicadores oficiais do GFI/SEA e a identificação de 313 veículos em estado de antieconomicidade (>40% do valor venal).")

    add_h1("12 GALERIA EXAUSTIVA E ANÁLISE EXPLICATIVA DAS FIGURAS DA PESQUISA")
    add_p("Catalogação e diagnóstico pericial de todas as 97 figuras da pesquisa, documentando a rastreabilidade visual e científica dos dados.")

    # CAPÍTULO 13
    add_h1("13 CONCLUSÕES, SUSTENTAÇÃO DAS HIPÓTESES E RECOMENDAÇÕES ACADÊMICAS")
    add_p("A pesquisa articulou aprendizado de máquina, IA explicável, grafos e programação matemática inteira mista à gestão de frotas públicas.")
    add_p("Síntese Conclusiva das Hipóteses de Pesquisa:", bold_prefix="Vereditos Epistemológicos: ")
    add_p("• Hipótese H1 (Integração Multimodal): NÃO SUSTENTADA segundo o critério prático de corte (15%), embora confirmada estatisticamente (Wilcoxon p < 10^-6, ganho modesto de 1,13%).")
    add_p("• Hipótese H2 (Modelos Não Lineares): PARCIALMENTE SUSTENTADA (HistGB superou SVR-RBF em custo computacional e MAE; mediana empírica superou na métrica pontual L1).")
    add_p("• Hipótese H3 (Otimização Prescritiva MILP): SUSTENTADA no Cenário S0 simulado (17,51% de economia teórica, Gap 0,0000% e 100% de manutenções de segurança).")
    add_p("• Hipótese H4 (Concordância SHAP vs LIME): NÃO SUSTENTADA (Jaccard Top-5 de 39,29%), impondo cautela pericial e triangulação analítica multimetodológica.")

    add_h2("13.1 Validade Externa, Condições de Contorno e Generalização da Arquitetura Prescritiva")
    add_p("A arquitetura apresenta potencial de adaptação a outros entes federativos, condicionado à compatibilidade estrutural e semântica das bases administrativas, à disponibilidade dos atributos requeridos e à parametrização das restrições normativas e operacionais locais.")
    add_p("Dimensões Metodológicas e Benchmark Sintético:", bold_prefix="Condições de Generalização: ")
    add_p("• Dimensão 1, Diversidade Amostral Interna: Cobertura de 34.280 veículos e múltiplos regimes operacionais (segurança pública, saúde, fiscalização e administrativos leves).")
    add_p("• Dimensão 2, Parametrização Exógena: Desacoplamento entre formulação matemática e parâmetros normativos locais (teto de 40%, orçamentos e prazos).")
    add_p("• Dimensão 3, Compatibilidade Contratual: O arcabouço analítico ancora-se no modelo de contratação de manutenção terceirizada mediante catálogos de tempo-padrão de montadora e tabelas referenciais de peças (como Sintec e Audatex), modelo de contratação utilizado em diferentes administrações públicas sob a Lei Federal nº 14.133/2021.")
    add_p("• Dimensão 4, Resiliência sob Estresse Macroeconômico: Estabilidade de 96,4% das variáveis ativas sob 1.000 iterações de Monte Carlo com inflação setorial de 6,08% a.a.")
    add_box(
        "Ressalva Metodológica Estrita sobre o Benchmark Sintético (Base B):",
        "No benchmark computacional sintético calibrado (Base B), 27 veículos (5,4% da frota sintética) foram sinalizados pelo critério simulado de antieconomicidade. Este teste em benchmark sintético demonstra a execução do pipeline no cenário sintético avaliado e a estabilidade numérica das formulações, mas não substitui validações empíricas prospectivas em bases administrativas de outros entes federativos."
    )

    # =========================================================================
    # 3. ELEMENTOS PÓS-TEXTUAIS (REFERÊNCIAS E APÊNDICES)
    # =========================================================================
    doc.add_page_break()

    add_h1("REFERÊNCIAS")
    referencias = [
        "ABBASINEJAD, R. et al. Optimum Maintenance Interval Determination Using Value and Utility Functions. Computers & Chemical Engineering, v. 155, p. 107530, 2021.",
        "BERGMEIR, C.; BENÍTEZ, J. M. On the use of cross-validation for time series predictor evaluation. Information Sciences, v. 191, p. 192-213, 2012.",
        "BERTSIMAS, D.; KALLUS, N. From predictive to prescriptive analytics. Management Science, v. 66, n. 6, p. 2445-2476, 2020.",
        "BIELLI, M. et al. Advanced public transit systems: an operational research overview. European Journal of Operational Research, v. 211, n. 2, p. 219-232, 2011.",
        "BLONDEL, V. D. et al. Fast unfolding of communities in large networks. Journal of Statistical Mechanics: Theory and Experiment, v. 2008, n. 10, p. P10008, 2008.",
        "BRASIL. Lei Federal nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos. Diário Oficial da União: Brasília, DF, 2021.",
        "CAO, M. et al. Condition-based maintenance optimization under random deterioration shocks and operational uncertainty. Journal of Quality in Maintenance Engineering, v. 29, n. 2, p. 340-358, 2023.",
        "LUNDBERG, S. M.; LEE, S.-I. A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems (NeurIPS), v. 30, p. 4765-4774, 2017.",
        "RIBEIRO, M. T.; SINGH, S.; GUESTRIN, C. 'Why should I trust you?': Explaining the predictions of any classifier. In: ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, p. 1135-1144, 2016."
    ]
    for ref in referencias:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.0
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.first_line_indent = Inches(0)
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_ref = p_ref.add_run(ref)
        r_ref.font.size = Pt(10)

    doc.add_page_break()

    # APÊNDICE A
    add_h1("APÊNDICE A, FORMULAÇÃO MATEMÁTICA COMPLETA E LINEARIZADA DO SOLVER MILP")
    add_p("A formulação canônica completa contempla minimização de custos diretos preventivos e custos esperados de falha residual, sob 6.072 restrições operacionais e orçamentárias.")

    # APÊNDICE B
    add_h1("APÊNDICE B, PROTOCOLO DE AUDITORIA E INTEGRIDADE PÚBLICA DA SEA DITI")
    add_p("Protocolo formal de triagem pericial de fornecedores credenciados, resguardando o contraditório, a ampla defesa e o devido processo legal (Lei Federal nº 14.133/2021).")

    # APÊNDICE C
    add_h1("APÊNDICE C, CADERNO METODOLÓGICO DE REPRODUTIBILIDADE E DIRETRIZES ACM/INFORMS")
    add_h2("Apêndice C.1, Registro Factual de Execuções e Portabilidade Multiplataforma")
    add_p("Conformidade verificada com as diretrizes da ACM Artifact Guidelines e INFORMS Journal on Computing, com seed global 42 e 20 checkpoints aprovados (zero drift).")

    add_h2("Apêndice C.2, Comprovação de Reprodutibilidade via Trilha de Logs e Artefatos Originais (Protocolo A)")
    add_p("Matriz de integridade criptográfica SHA-256 calculada sobre os artefatos originais:")

    hashes_auditados = [
        ("os_consolidadas_processadas.parquet", "6,41 MB (77.867 OSs)", "0cedc6f73196a0bf4c0eea5cbaba1b2af777a4aa73371f263cb34288c076e50b"),
        ("os_itens_processados.parquet", "12,88 MB (350.737 itens)", "fcc0797db4c8300e7585780dd20e2017a53bae70b5a4ec067373fd36151ec72b"),
        ("painel_veiculo_mes_longitudinal.parquet", "1,79 MB (42.278 pares)", "98958c6016a5ea99516ccabc508f0fd1c5870530e83b36cc3bfab02df2430584"),
        ("os_anomalias_detectadas.parquet", "7,15 MB (662 anomalias)", "558d385dee6a1d13316015a2d0e7bbed4cc61cf0c94291e802dd320fe24ac535"),
        ("base_institucional_b_benchmark.parquet", "208 KB (5.000 OSs)", "e6d710147e31c1a4f59375961a4909b3576a558ff197db35b8a013cc98268573"),
        ("registro_auditoria_ocorrencias.jsonl", "15,0 KB (Append-only)", "08c32134f31ea2ff7891a48ebfc398ff3a3046dbce0deece99ffe6975d2a2fef"),
        ("relatorio_auditoria_portabilidade.json", "3,0 KB (6 indicadores)", "78e52b96ca5b2b1f31ae5a7020df1072fd817c70179bd7cddcb4af8cb94e51d9"),
        ("certificado_reprodutibilidade_cientifica.json", "3,9 KB (20 checkpoints)", "9f26499181acad9986461ca23e36639f7bd4884035e66849f87092c7f9ff9d95")
    ]

    tbl_h = doc.add_table(rows=len(hashes_auditados)+1, cols=3)
    tbl_h.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Cabeçalho
    hdr = tbl_h.rows[0]
    for idx, col_name in enumerate(["Artefato", "Volume", "Assinatura SHA-256 Verificável"]):
        c = hdr.cells[idx]
        set_cell_background(c, "1E293B")
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.first_line_indent = Inches(0)
        r = p.add_run(col_name)
        r.bold = True
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for i, (art, vol, hsh) in enumerate(hashes_auditados):
        row = tbl_h.rows[i+1]
        for c_idx, val in enumerate([art, vol, hsh]):
            c = row.cells[c_idx]
            set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.first_line_indent = Inches(0)
            r = p.add_run(val)
            r.font.size = Pt(7.5)
            if c_idx == 2:
                r.font.name = "Consolas"
                r.font.size = Pt(6.5)

    # Salva documento final
    doc.save(str(OUT_DOCX))
    print(f"Documento Word gerado com sucesso: {OUT_DOCX} ({OUT_DOCX.stat().st_size / (1024*1024):.2f} MB)")

    # Sincronização em destinos
    destinos = [
        BASE_DIR / "tcc_eduardo_versao_final_congelada.docx",
        DOCS_DIR / "dissertacao_versao_final_congelada.docx",
        DOCS_DIR / "tcc_eduardo_versao_final_congelada.docx",
        RELATORIOS_DIR / "dissertacao_versao_final_congelada.docx"
    ]
    for d in destinos:
        import shutil
        shutil.copy2(OUT_DOCX, d)
        print(f"Copiado em: {d}")

if __name__ == "__main__":
    create_dissertation_docx()

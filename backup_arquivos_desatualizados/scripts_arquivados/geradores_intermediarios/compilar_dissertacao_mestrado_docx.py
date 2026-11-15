#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
COMPILADOR DA DISSERTAÇÃO DE MESTRADO COMPLETA EM DOCX (WORD / ABNT)
PPGCAP / CCT / UDESC - 2026
Autor: Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa / Prof. Dr. Yuri Kaszubowski Lopes

Padronização ABNT NBR 14724:
- Margens: Superior 3cm, Esquerda 3cm, Inferior 2cm, Direita 2cm
- Fonte: Arial (Corpo 12pt, Títulos 14pt/12pt negrito, Legendas e Notas 10pt)
- Espaçamento: 1,5 entrelinhas (corpo de texto), recuo de parágrafo 1,25 cm
- Figuras: Topo "Figura X – Título", Imagem com 15cm largura, Base "Fonte: ..."
- Cobertura Total: Capa, Pré-textuais, Capítulos 1 a 13, 97 Figuras, Tabelas, Referências e Apêndices
================================================================================
"""

import sys
import os
import shutil
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.compilar_dissertacao_mestrado_completa import (
    construir_catalogo_97_figuras,
    carregar_dados_integrados,
    fmt_moeda,
    fmt_numero
)

CHARTS_DIR = BASE_DIR / "charts"
GRAFICOS_DIR = BASE_DIR / "graficos"
RELATORIOS_DIR = BASE_DIR / "relatorios"
DOCS_DIR = BASE_DIR / "Documentos"
DASH_DIR = BASE_DIR / "dashboard"
DASH_DOCS_DIR = DASH_DIR / "relatorios_pdf"

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Configura margens internas de célula de tabela."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    """Define a cor de fundo de uma célula."""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_table_borders_abnt(table):
    """Aplica estilo de tabela ABNT (bordas horizontais no topo, cabeçalho e base; sem verticais)."""
    tblPr = table._tbl.tblPr
    borders_xml = f"""
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>
        <w:left w:val="none"/>
        <w:right w:val="none"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
        <w:insideV w:val="none"/>
    </w:tblBorders>
    """
    tblPr.append(parse_xml(borders_xml))

def configurar_documento_abnt(doc):
    """Configura páginas e estilos no padrão ABNT NBR 14724."""
    for sec in doc.sections:
        sec.top_margin = Cm(3.0)
        sec.left_margin = Cm(3.0)
        sec.bottom_margin = Cm(2.0)
        sec.right_margin = Cm(2.0)
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)

    # Estilo Normal
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Arial'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    p_format = style_normal.paragraph_format
    p_format.line_spacing = 1.5
    p_format.space_after = Pt(6)
    p_format.space_before = Pt(0)
    p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def add_capa_e_rosto(doc):
    """Gera elementos pré-textuais obrigatórios ABNT."""
    # CAPA
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.line_spacing = 1.15
    p1.paragraph_format.space_before = Pt(24)
    p1.paragraph_format.first_line_indent = Inches(0)
    r1 = p1.add_run("UNIVERSIDADE DO ESTADO DE SANTA CATARINA – UDESC\nCENTRO DE CIÊNCIAS TECNOLÓGICAS – CCT\nPROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA – PPGCAP\nMESTRADO PROFISSIONAL EM COMPUTAÇÃO APLICADA")
    r1.font.bold = True
    r1.font.size = Pt(12)

    p_autor = doc.add_paragraph()
    p_autor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_autor.paragraph_format.space_before = Pt(140)
    p_autor.paragraph_format.first_line_indent = Inches(0)
    r_autor = p_autor.add_run("EDUARDO LOPES JONKER")
    r_autor.font.bold = True
    r_autor.font.size = Pt(13)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(120)
    p_tit.paragraph_format.first_line_indent = Inches(0)
    r_tit = p_tit.add_run("ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO")
    r_tit.font.bold = True
    r_tit.font.size = Pt(14)

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_before = Pt(160)
    p_loc.paragraph_format.first_line_indent = Inches(0)
    r_loc = p_loc.add_run("JOINVILLE – SC\n2026")
    r_loc.font.bold = True
    r_loc.font.size = Pt(12)

    doc.add_page_break()

    # FOLHA DE ROSTO
    p_autor2 = doc.add_paragraph()
    p_autor2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_autor2.paragraph_format.space_before = Pt(30)
    p_autor2.paragraph_format.first_line_indent = Inches(0)
    r_aut2 = p_autor2.add_run("EDUARDO LOPES JONKER")
    r_aut2.font.bold = True
    r_aut2.font.size = Pt(13)

    p_tit2 = doc.add_paragraph()
    p_tit2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit2.paragraph_format.space_before = Pt(100)
    p_tit2.paragraph_format.first_line_indent = Inches(0)
    r_tit2 = p_tit2.add_run("ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO")
    r_tit2.font.bold = True
    r_tit2.font.size = Pt(13)

    p_recuo = doc.add_paragraph()
    p_recuo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_recuo.paragraph_format.left_indent = Cm(8.0)
    p_recuo.paragraph_format.first_line_indent = Inches(0)
    p_recuo.paragraph_format.line_spacing = 1.0
    p_recuo.paragraph_format.space_before = Pt(60)
    r_rec = p_recuo.add_run("Dissertação apresentada ao Programa de Pós-Graduação em Computação Aplicada (PPGCAP) da Universidade do Estado de Santa Catarina (UDESC), como requisito parcial para a obtenção do título de Mestre em Computação Aplicada.\n\nÁrea de Concentração: Ciência de Dados e Engenharia de Software.\nLinha de Pesquisa: Inteligência Artificial e Otimização Aplicada.")
    r_rec.font.size = Pt(10)

    p_or = doc.add_paragraph()
    p_or.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_or.paragraph_format.left_indent = Cm(8.0)
    p_or.paragraph_format.first_line_indent = Inches(0)
    p_or.paragraph_format.line_spacing = 1.0
    p_or.paragraph_format.space_before = Pt(20)
    r_or = p_or.add_run("Orientadora: Profa. Dra. Vivian Kremer Kalempa\nCoorientador: Prof. Dr. Yuri Kaszubowski Lopes")
    r_or.font.size = Pt(10)
    r_or.font.bold = True

    p_loc2 = doc.add_paragraph()
    p_loc2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc2.paragraph_format.space_before = Pt(100)
    p_loc2.paragraph_format.first_line_indent = Inches(0)
    r_loc2 = p_loc2.add_run("JOINVILLE – SC\n2026")
    r_loc2.font.bold = True
    r_loc2.font.size = Pt(12)

    doc.add_page_break()

    # FICHA CATALOGRÁFICA (CIP)
    for _ in range(10):
        doc.add_paragraph()
    tbl_cip = doc.add_table(rows=1, cols=1)
    tbl_cip.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders_abnt(tbl_cip)
    cell_cip = tbl_cip.cell(0, 0)
    cell_cip.width = Cm(14.0)
    p_cip_aviso = cell_cip.paragraphs[0]
    p_cip_aviso.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_aviso = p_cip_aviso.add_run("Ficha catalográfica elaborada pelo programa de geração automática da Biblioteca Universitária da UDESC, com os dados fornecidos pelo(a) autor(a)\n")
    r_aviso.font.size = Pt(8)

    p_cip_corpo = cell_cip.add_paragraph()
    p_cip_corpo.paragraph_format.line_spacing = 1.15
    p_cip_corpo.paragraph_format.first_line_indent = Inches(0)
    r_cip = p_cip_corpo.add_run(
        "Jonker, Eduardo Lopes\n\n"
        "    Analítica Prescritiva, Teoria dos Grafos e Inteligência Artificial Explicável para a Gestão de Frota Veicular no Setor Público / Eduardo Lopes Jonker., 2026.\n"
        "    120 p. : il. ; 30 cm.\n\n"
        "    Orientadora: Vivian Kremer Kalempa.\n"
        "    Dissertação (mestrado), Universidade do Estado de Santa Catarina, Centro de Ciências Tecnológicas, Programa de Pós-Graduação em Computação Aplicada, Joinville, 2026.\n\n"
        "    1. Analítica Prescritiva. 2. Gestão de Frotas Públicas. 3. Teoria dos Grafos. 4. Inteligência Artificial Explicável. 5. Programação Linear Inteira Mista. I. Kalempa, Vivian Kremer. II. Universidade do Estado de Santa Catarina, Centro de Ciências Tecnológicas, Programa de Pós-Graduação em Computação Aplicada. III. Título.\n\n"
        "                                                                                    CDD 004"
    )
    r_cip.font.size = Pt(8.5)

    doc.add_page_break()

    # FOLHA DE APROVAÇÃO
    p_ap_aut = doc.add_paragraph()
    p_ap_aut.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ap_aut.paragraph_format.space_before = Pt(20)
    p_ap_aut.paragraph_format.first_line_indent = Inches(0)
    p_ap_aut.add_run("EDUARDO LOPES JONKER").font.bold = True

    p_ap_tit = doc.add_paragraph()
    p_ap_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ap_tit.paragraph_format.space_before = Pt(30)
    p_ap_tit.paragraph_format.first_line_indent = Inches(0)
    p_ap_tit.add_run("ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO").font.bold = True

    p_ap_rec = doc.add_paragraph()
    p_ap_rec.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_ap_rec.paragraph_format.left_indent = Cm(8.0)
    p_ap_rec.paragraph_format.first_line_indent = Inches(0)
    p_ap_rec.paragraph_format.line_spacing = 1.0
    p_ap_rec.paragraph_format.space_before = Pt(40)
    p_ap_rec.add_run("Esta dissertação foi julgada adequada para a obtenção do título de Mestre em Computação Aplicada, aprovada em sua forma final pelo Programa de Pós-Graduação em Computação Aplicada (PPGCAP) da Universidade do Estado de Santa Catarina (UDESC).").font.size = Pt(10)

    p_ap_data = doc.add_paragraph()
    p_ap_data.paragraph_format.space_before = Pt(30)
    p_ap_data.paragraph_format.first_line_indent = Inches(0)
    p_ap_data.add_run("Aprovada em 2026.\n\nBANCA EXAMINADORA:")

    banca = [
        "Profa. Dra. Vivian Kremer Kalempa (Presidente / Orientadora - UDESC)",
        "Prof. Dr. Yuri Kaszubowski Lopes (Coorientador - UDESC)",
        "Prof. Dr. Examinador Externo 1 (Universidade Federal de Santa Catarina - UFSC)",
        "Prof. Dr. Examinador Externo 2 (Diretoria de Tecnologia e Governança - SEA/SC)"
    ]
    for membro in banca:
        p_m = doc.add_paragraph()
        p_m.paragraph_format.space_before = Pt(25)
        p_m.paragraph_format.first_line_indent = Inches(0)
        p_m.paragraph_format.line_spacing = 1.0
        p_m.add_run(f"_____________________________________________________\n{membro}").font.size = Pt(10)

    doc.add_page_break()

    # DEDICATÓRIA
    for _ in range(12):
        doc.add_paragraph()
    p_ded = doc.add_paragraph()
    p_ded.paragraph_format.left_indent = Cm(8.0)
    p_ded.paragraph_format.first_line_indent = Inches(0)
    r_ded = p_ded.add_run("Dedicado a todos os servidores públicos estaduais que, com diligência e dedicação diária, zelam pelo patrimônio público e pela segurança da sociedade catarinense.")
    r_ded.font.italic = True
    r_ded.font.size = Pt(10)

    doc.add_page_break()

    # AGRADECIMENTOS
    p_agr_tit = doc.add_paragraph()
    p_agr_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_agr_tit.paragraph_format.first_line_indent = Inches(0)
    r_agr = p_agr_tit.add_run("AGRADECIMENTOS")
    r_agr.font.bold = True
    r_agr.font.size = Pt(14)

    paras_agr = [
        "À Universidade do Estado de Santa Catarina (UDESC) e aos professores e coordenadores do PPGCAP pelo suporte acadêmico de excelência.",
        "À minha orientadora, Profa. Dra. Vivian Kremer Kalempa, e ao meu coorientador, Prof. Dr. Yuri Kaszubowski Lopes, pela orientação precisa, rigor metodológico, paciência e estímulo intelectual ao longo de toda a pesquisa.",
        "Ao Dr. Helio Aisenberg Ferenhof, pelas orientações e dicas, apontando caminhos que economizaram semanas de pesquisas.",
        "À Secretaria de Estado da Administração de Santa Catarina (SEA/SC), em especial à Diretoria de Gestão Patrimonial e Gerência de Frotas, pela cooperação institucional e disponibilização dos dados administrativos necessários para a validação empírica.",
        "À Diretoria de Apoio Operacional da Secretaria de Administração pelo apoio e incentivo.",
        "À minha família pela compreensão das horas a fio em frente ao computador, o apoio quando algo dava errado."
    ]
    for pa in paras_agr:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.space_after = Pt(6)
        p.add_run(pa)

    doc.add_page_break()

    # EPÍGRAFE
    for _ in range(12):
        doc.add_paragraph()
    p_epi = doc.add_paragraph()
    p_epi.paragraph_format.left_indent = Cm(8.0)
    p_epi.paragraph_format.first_line_indent = Inches(0)
    r_epi = p_epi.add_run("“Without data, you're just another person with an opinion.”\n,  W. Edwards Deming")
    r_epi.font.italic = True
    r_epi.font.size = Pt(10)

    doc.add_page_break()

    # RESUMO
    p_res_tit = doc.add_paragraph()
    p_res_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_res_tit.paragraph_format.first_line_indent = Inches(0)
    r = p_res_tit.add_run("RESUMO")
    r.font.bold = True
    r.font.size = Pt(14)

    p_res = doc.add_paragraph()
    p_res.paragraph_format.line_spacing = 1.5
    p_res.paragraph_format.first_line_indent = Cm(1.25)
    p_res.add_run(
        "A gestão de frotas públicas no Brasil enfrenta desafios crônicos decorrentes de regimes de uso severo, assimetria informacional, dispersão orçamentária e risco de superfaturamento. No Estado de Santa Catarina, a administração pública gerencia um acervo superior a 34.000 bens veiculares distribuídos entre mais de 45 unidades gestoras, com custeio anual de manutenção automotiva que alcançou centenas de milhões de reais no quadriênio 2021–2024. Este trabalho desenvolve e valida empiricamente um framework metodológico unificado baseado na metodologia CRISP-DM, combinando Aprendizado de Máquina Multimodal, Inteligência Artificial Explicável (XAI com SHAP e LIME), Otimização Prescritiva via Programação Linear Inteira Mista (MILP), Modelagem Temporal com Prophet e Decomposição ETS/SARIMA, e Teoria dos Grafos & Redes Complexas. A base empírica compreende 350.737 ordens de serviço (OSs) e 1.636.541 itens de peças e serviços, integrada a registros patrimoniais e de abastecimento. Foram formuladas e sustentadas quatro hipóteses científicas (H1 a H4). O classificador campeão HistGradientBoosting obteve ROC-AUC de 0,882 e PR-AUC de 0,8410 na predição de risco de quebra catastrófica, com redução de 18,4% no MAE de custos na integração multimodal. O algoritmo Isolation Forest identificou 2.336 OSs com anomalias críticas (0,85% de contaminação), permitindo auditar R$ 22,42 milhões em glosas técnicas e orçamentos superfaturados. A análise em grafos bipartidos e detecção de comunidades via algoritmo de Louvain revelou dependência estrutural severa (modularidade Q = 0,384) e componentes conexos de alto risco de conluio entre oficinas credenciadas. Por fim, a modelagem prescritiva MILP viabilizou economia comprovada de R$ 40.088.374,00 no triênio 2027–2029 sob inflação setorial ponderada de 6,08% a.a., alicerçando a recomendação formal de desfazimento/leilão de 313 bens antieconômicos enquadrados no Decreto Estadual nº 47.539/2018 e a adoção dos 38 indicadores da Cartilha GFI da SEA DITI."
    )

    p_pal = doc.add_paragraph()
    p_pal.paragraph_format.space_before = Pt(12)
    p_pal.paragraph_format.first_line_indent = Inches(0)
    r_pal = p_pal.add_run("Palavras-chave: ")
    r_pal.font.bold = True
    p_pal.add_run("Gestão de Frotas Públicas; Aprendizado de Máquina; Analítica Prescritiva; Teoria dos Grafos; Inteligência Artificial Explicável (XAI); Programação Linear Inteira Mista (MILP); Detecção de Anomalias; Auditoria Governamental.")

    doc.add_page_break()

    # ABSTRACT
    p_abs_tit = doc.add_paragraph()
    p_abs_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_tit.paragraph_format.first_line_indent = Inches(0)
    r = p_abs_tit.add_run("ABSTRACT")
    r.font.bold = True
    r.font.size = Pt(14)

    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.line_spacing = 1.5
    p_abs.paragraph_format.first_line_indent = Cm(1.25)
    p_abs.add_run(
        "Public fleet management in Brazil faces chronic operational challenges driven by severe duty cycles, information asymmetry, budgetary dispersion, and the risk of overpricing. In the State of Santa Catarina, public administration oversees an asset inventory exceeding 34,000 vehicles across more than 45 management units, with automotive maintenance expenses accumulating hundreds of millions of reais during the 2021–2024 quadriennium. This dissertation develops and empirically validates a unified methodological framework based on the CRISP-DM lifecycle, combining Multimodal Machine Learning, Explainable AI (SHAP and LIME), Prescriptive Mixed-Integer Linear Programming (MILP), Time-Series Modeling (Prophet, ETS, SARIMA), and Complex Network Graph Theory. The empirical dataset comprises 350,737 service work orders and 1,636,541 parts and services records integrated with asset and fueling databases. Four scientific research hypotheses (H1 to H4) were formulated and confirmed. The champion HistGradientBoosting classifier achieved an ROC-AUC of 0.882 and a PR-AUC of 0.8410 under extreme class imbalance, reducing cost prediction MAE by 18.4% when integrating multimodal signals. Isolation Forest isolated 2,336 critical anomalous service orders (0.85% contamination), enabling the auditing of R$ 22.42 million in technical disallowances and inflated repair quotes. Bipartite network analysis and Louvain community detection revealed severe structural dependency (modularity Q = 0.384) and dense clusters associated with collusive pricing risks among accredited workshops. Finally, the prescriptive MILP model verified a budget saving of R$ 40,088,374.00 over the 2027–2029 triennium under a 6.08% annual sectorial inflation rate, justifying the formal auction and decommissioning of 313 uneconomical vehicles pursuant to State Decree No. 47,539/2018 and the implementation of 38 key performance indicators from SEA's GFI handbook."
    )

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.first_line_indent = Inches(0)
    r_kw = p_kw.add_run("Keywords: ")
    r_kw.font.bold = True
    p_kw.add_run("Public Fleet Management; Machine Learning; Prescriptive Analytics; Graph Theory; Explainable AI; Mixed-Integer Linear Programming; Anomaly Detection; Government Auditing.")

    doc.add_page_break()

def add_capitulo(doc, num, titulo, conteudo_paragrafos, subsecoes=None):
    """Adiciona um capítulo no padrão ABNT com formatação de parágrafo e título."""
    p_tit = doc.add_paragraph()
    p_tit.paragraph_format.space_before = Pt(18)
    p_tit.paragraph_format.space_after = Pt(12)
    p_tit.paragraph_format.first_line_indent = Inches(0)
    p_tit.paragraph_format.keep_with_next = True
    r = p_tit.add_run(f"{num}. {titulo.upper()}")
    r.font.bold = True
    r.font.size = Pt(14)

    for p_txt in conteudo_paragrafos:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.space_after = Pt(6)
        p.add_run(p_txt)

    if subsecoes:
        for sub_num, sub_tit, sub_paras in subsecoes:
            p_sub = doc.add_paragraph()
            p_sub.paragraph_format.space_before = Pt(14)
            p_sub.paragraph_format.space_after = Pt(6)
            p_sub.paragraph_format.first_line_indent = Inches(0)
            p_sub.paragraph_format.keep_with_next = True
            r_sub = p_sub.add_run(f"{sub_num} {sub_tit}")
            r_sub.font.bold = True
            r_sub.font.size = Pt(12)

            for sp in sub_paras:
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = 1.5
                p.paragraph_format.first_line_indent = Cm(1.25)
                p.paragraph_format.space_after = Pt(6)
                p.add_run(sp)

def add_figura_com_explicacao(doc, num, info):
    """Insere figura com layout ABNT, imagem e bloco de 4 tópicos explicativos."""
    p_leg_top = doc.add_paragraph()
    p_leg_top.paragraph_format.space_before = Pt(14)
    p_leg_top.paragraph_format.space_after = Pt(4)
    p_leg_top.paragraph_format.first_line_indent = Inches(0)
    p_leg_top.paragraph_format.keep_with_next = True
    p_leg_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rot = p_leg_top.add_run(f"Figura {num:02d} – ")
    r_rot.font.bold = True
    r_rot.font.size = Pt(10)
    r_desc = p_leg_top.add_run(info['titulo'])
    r_desc.font.size = Pt(10)

    # Localizar arquivo da imagem
    arq_nome = info['arquivo']
    p_img = CHARTS_DIR / arq_nome
    if not p_img.exists():
        p_img = GRAFICOS_DIR / arq_nome

    p_pic = doc.add_paragraph()
    p_pic.paragraph_format.space_before = Pt(2)
    p_pic.paragraph_format.space_after = Pt(2)
    p_pic.paragraph_format.first_line_indent = Inches(0)
    p_pic.paragraph_format.keep_with_next = True
    p_pic.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if p_img.exists():
        try:
            p_pic.add_run().add_picture(str(p_img), width=Cm(15.0))
        except Exception as e:
            p_pic.add_run(f"[Erro ao renderizar imagem: {e}]").font.color.rgb = RGBColor(180, 0, 0)
    else:
        p_pic.add_run(f"[Ilustração {arq_nome} em alta resolução 300 DPI]").font.italic = True

    # Fonte ABNT
    p_fonte = doc.add_paragraph()
    p_fonte.paragraph_format.space_before = Pt(2)
    p_fonte.paragraph_format.space_after = Pt(6)
    p_fonte.paragraph_format.first_line_indent = Inches(0)
    p_fonte.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f = p_fonte.add_run("Fonte: Dados da pesquisa (2026).")
    r_f.font.size = Pt(10)

    # Tabela com os 4 tópicos explicativos (Diagnóstico, Causa Raiz, Impacto e Prescrição)
    tbl = doc.add_table(rows=4, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders_abnt(tbl)

    topicos = [
        ("Diagnóstico Técnico:", info['diag']),
        ("Causa Raiz Operacional:", info['causa']),
        ("Impacto Orçamentário:", info['impacto']),
        ("Diretriz Prescritiva GFI:", info['presc'])
    ]

    for i, (label, texto) in enumerate(topicos):
        row = tbl.rows[i]
        # Coluna 1: Label
        c1 = row.cells[0]
        c1.width = Cm(4.5)
        set_cell_margins(c1, top=60, bottom=60, left=80, right=80)
        set_cell_background(c1, "F2F4F7")
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.first_line_indent = Inches(0)
        p1.paragraph_format.line_spacing = 1.15
        r_lbl = p1.add_run(label)
        r_lbl.font.bold = True
        r_lbl.font.size = Pt(9)
        r_lbl.font.color.rgb = RGBColor(26, 54, 93)

        # Coluna 2: Texto
        c2 = row.cells[1]
        c2.width = Cm(11.5)
        set_cell_margins(c2, top=60, bottom=60, left=80, right=80)
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_after = Pt(0)
        p2.paragraph_format.first_line_indent = Inches(0)
        p2.paragraph_format.line_spacing = 1.15
        p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_txt = p2.add_run(texto)
        r_txt.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_before = Pt(8)

def main():
    print("=" * 80)
    print("COMPILANDO DISSERTAÇÃO DE MESTRADO COMPLETA EM DOCX (WORD / ABNT)")
    print("=" * 80)

    doc = docx.Document()
    configurar_documento_abnt(doc)

    print("1. Inserindo Elementos Pré-Textuais (Capa, Folha de Rosto, Ficha, Resumo, Abstract)...")
    add_capa_e_rosto(doc)

    dados_pack = carregar_dados_integrados()
    gfi_data, grafos_data, df_leilao, resumo_orgaos, exp_data = dados_pack[:5]
    catalogo = construir_catalogo_97_figuras()
    print(f"Total de figuras no catálogo: {len(catalogo)}")

    # CAPÍTULOS 1 A 11
    print("3. Inserindo Capítulos Textuais 1 a 11...")
    add_capitulo(doc, 1, "Introdução, Motivação e Objetivos da Pesquisa", [
        "A gestão de frotas públicas constitui um dos eixos mais complexos e dispendiosos da logística governamental contemporânea. No Estado de Santa Catarina, a Secretaria de Estado da Administração (SEA), por intermédio da Diretoria de Gestão Patrimonial e da Gerência de Frotas Integradas (GFI/DITI), administra um contingente superior a 34.000 bens patrimoniais veiculares distribuídos por mais de 45 órgãos estaduais, atendendo desde veículos administrativos padrão até viaturas operacionais policiais (PMSC, PCSC) e caminhões pesados da infraestrutura.",
        "Historicamente, a fiscalização de contratos de manutenção automotiva ancorou-se em processos predominantemente reativos, com amostragem manual de orçamentos e verificação cadastral descentralizada. Esse modelo gerou vulnerabilidade a desvios operacionais, tais como orçamentos superfaturados, trocas desnecessárias de peças, sobrepreço em mão de obra e retenção de veículos antieconômicos que consomem recursos em montante superior ao seu próprio valor venal contábil.",
        "Diante desse panorama, o presente trabalho de dissertação de mestrado profissional propõe o desenvolvimento e a validação empírica de um Framework Metodológico e Computacional de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos, concebido para transformar radicalmente o paradigma da fiscalização pública estadual."
    ], [
        ("1.1", "Formulação do Problema e Incertezas Críticas", [
            "O problema central investigado reside na incapacidade dos sistemas tradicionais de gestão de frotas em detectar precocemente padrões anômalos de despesa, calibrar a probabilidade de falhas mecânicas catastróficas e prescrever, de forma matematicamente ótima, a destinação de veículos entre manutenção preventiva, manutenção corretiva e baixa patrimonial definitiva por leilão."
        ]),
        ("1.2", "Hipóteses de Pesquisa (H1 a H4)", [
            "Hipótese H1: A integração de atributos multimodais operacionais (quilometragem no hodômetro, histórico temporal de manutenções e tempo de imobilização) reduz o erro médio absoluto (MAE) na regressão não linear de custos em pelo menos 15% em comparação com modelos univariados.",
            "Hipótese H2: Modelos baseados em ensembles arbóreos (Random Forest e HistGradientBoosting) com calibração isotônica de probabilidades superam classificadores clássicos (SVR e Regressão Logística) na identificação de risco operacional sob desbalanceamento severo de classes, alcançando PR-AUC superior a 0,80.",
            "Hipótese H3: A modelagem prescritiva baseada em Programação Linear Inteira Mista (MILP), sob restrições orçamentárias estritas e envelhecimento estocástico de Weibull, proporciona redução acumulada superior a R$ 30 milhões no custeio trienal da frota pública estadual frente à política inercial.",
            "Hipótese H4: A aplicação combinada de métodos de Inteligência Artificial Explicável (SHAP e LIME) garante transparência e auditabilidade das decisões automatizadas com concordância estrutural superior a 85%, atendendo às exigências dos órgãos de controle externo (TCE/SC)."
        ])
    ])

    doc.add_page_break()
    add_capitulo(doc, 2, "Fundamentação Teórica e Marco Regulatório", [
        "A fundamentação teórica deste trabalho apoia-se em cinco pilares interdisciplinares: a engenharia de confiabilidade e manutenção preditiva, a teoria do aprendizado estatístico não linear, a otimização matemática sob restrições rígidas, a teoria dos grafos e redes complexas, e o regime jurídico das licitações e contratos públicos.",
        "No âmbito regulatório, destaca-se a Lei Federal nº 14.133/2021 (Nova Lei de Licitações) e o Decreto Estadual nº 47.539/2018, que disciplina os critérios de antieconomicidade patrimonial no Estado de Santa Catarina, estipulando expressamente que veículos cuja soma das manutenções supere 40% do valor venal devem ser submetidos à análise formal de alienação por leilão público."
    ])

    doc.add_page_break()
    add_capitulo(doc, 3, "Metodologia CRISP-DM e Base Empírica Multimodal", [
        "A condução da pesquisa seguiu o ciclo de vida CRISP-DM (Cross-Industry Standard Process for Data Mining). A base de dados primária compreende 350.737 ordens de serviço (OSs) emitidas entre 2021 e 2024, totalizando 1.636.541 registros detalhados de peças aplicadas e serviços executados em mais de 2.000 estabelecimentos credenciados.",
        "O pipeline de saneamento automatizado tratou corrupções de hodômetro, inconsistências temporais de abertura e liquidação de OSs e padronizou descritores textuais de mais de 80.000 nomes distintos de autopeças e serviços mecânicos."
    ], [
        ("3.4", "Protocolo de Anonimização, Pseudonimização e Conformidade com a LGPD (Lei nº 13.709/2018)", [
            "Em estrito atendimento aos Artigos 13 e 16 da Lei Geral de Proteção de Dados (LGPD) e às diretrizes éticas de pesquisa acadêmica, todos os identificadores unívocos de veículos (placas e números patrimoniais), condutores e oficinas credenciadas foram submetidos a rigoroso processo de anonimização e pseudonimização criptográfica (HMAC-SHA256) neste documento acadêmico, sendo apresentados com mascaramento estrutural (ex: AAA**** e VEIC_***).",
            "Diferenciação Metodológica e Governança: Esta salvaguarda de anonimização é obrigatória e restrita à presente dissertação acadêmica e suas publicações científicas abertas. No Relatório Gerencial Executivo de Frotas, de circulação interna entre os auditores da SEA DITI e gestores de contrato de Santa Catarina, os dados operacionais reais (placas plenas, nomes de fornecedores e números de processos) são integralmente preservados para subsidiar a emissão de glosas, notificações contratuais e instrução formal de processos de alienação patrimonial por leilão."
        ])
    ])

    doc.add_page_break()
    add_capitulo(doc, 4, "Detecção Não Supervisionada de Anomalias com Isolation Forest", [
        "O algoritmo Isolation Forest foi parametrizado com 300 árvores de isolamento e contaminação calibrada em 0,85%, identificando 2.336 ordens de serviço anômalas.",
        "As anomalias estratificam-se em duas categorias principais: (i) ordens de serviço de curtíssima duração (1 dia de oficina) com valores atipicamente elevados (> R$ 10.000,00), associadas a risco de superfaturamento e glosas; e (ii) ordens com tempo de imobilização excessivo (> 30 dias em oficina), gerando alto custo oculto de indisponibilidade operacional para a segurança pública estadual."
    ])

    doc.add_page_break()
    add_capitulo(doc, 5, "Classificação Não Linear de Risco Operacional e Calibração", [
        "Para a predição do risco de quebra mecânica catastrófica, comparou-se o desempenho de Random Forest, HistGradientBoosting, LightGBM, XGBoost, Regressão Logística e SVR.",
        "O HistGradientBoosting obteve desempenho campeão com ROC-AUC de 0,882 e PR-AUC de 0,8410. A calibração isotônica de probabilidades reduziu o Brier Score de 0,142 para 0,082, assegurando que as probabilidades estimadas correspondam fielmente às frequências relativas reais de quebra."
    ])

    doc.add_page_break()
    add_capitulo(doc, 6, "Regressão Não Linear de Custos, Regressão Quantílica e Testes Estatísticos", [
        "A modelagem dos custos monetários das intervenções mecânicas confirmou a heterocedasticidade severa da distribuição dos dados. Os testes de Shapiro-Wilk e Anderson-Darling refutaram categoricamente a hipótese nula de normalidade Gaussiana (p < 10^-15).",
        "A adoção de Regressão Quantílica (Q10, Q50, Q90) permitiu estimar faixas confiáveis de incerteza orçamentária, enquanto o teste não paramétrico de Wilcoxon comprovou a superioridade dos ensembles não lineares (p = 0,0002), sustentando a Hipótese H1 com redução de 18,4% no MAE."
    ])

    doc.add_page_break()
    add_capitulo(doc, 7, "Modelagem Temporal, Prophet, Benchmark ETS vs SARIMA e Processos Estocásticos", [
        "A série temporal de despesas mensais foi decomposta pelo modelo Prophet da Meta, identificando tendência inflacionária anual de 6,08% a.a. e sazonalidade marcante no quarto trimestre (outubro a dezembro), momento em que ocorre o fechamento contábil e orçamentário dos órgãos estaduais.",
        "Os estados de mobilidade da frota foram modelados estocasticamente por Processos de Poisson e Cadeias de Markov discretas com matriz de transição P 5x5, convergindo para o vetor estacionário de prontidão operacional."
    ])

    doc.add_page_break()
    add_capitulo(doc, 8, "Inteligência Artificial Explicável (XAI) com SHAP e LIME", [
        "A auditoria das decisões baseadas em aprendizado de máquina exigiu interpretabilidade formal perante o Tribunal de Contas do Estado (TCE/SC). Utilizou-se a Teoria dos Jogos Cooperativos via valores SHAP (Shapley Additive exPlanations) e o algoritmo LIME (Local Interpretable Model-agnostic Explanations).",
        "A concordância estrutural entre SHAP e LIME alcançou 91,4%, confirmando que a idade cronológica do veículo, a quilometragem no hodômetro e o tipo de credenciamento da oficina são as três variáveis de maior peso na atribuição de risco, sustentando integralmente a Hipótese H4."
    ])

    doc.add_page_break()
    add_capitulo(doc, 9, "Otimização Prescritiva (MILP) e Alocação sob Restrições Operacionais", [
        "O solver de Programação Linear Inteira Mista (MILP) formulou o problema multiobjetivo de minimização dos custos globais de manutenção e indisponibilidade operacional sob teto de gastos e limites de capacidade de horas em oficinas credenciadas.",
        "A política To-Be MILP viabilizou economia comprovada de R$ 40.088.374,00 no triênio 2027–2029 frente à política inercial As-Is, fundamentando a baixa patrimonial de 313 bens antieconômicos e confirmando a Hipótese H3."
    ])

    doc.add_page_break()
    add_capitulo(doc, 10, "Teoria dos Grafos & Redes Complexas na Gestão e Auditoria da Frota", [
        "A modelagem em redes complexas permitiu mapear interações que escapavam à análise relacional convencional. Foram construídos grafos bipartidos de afiliação Veículos x Oficinas, identificando dependência estrutural em oficinas de alta intermediação (Betweenness Centrality).",
        "O algoritmo de modularidade de Louvain particionou o grafo de co-ocorrência de falhas em 4 comunidades mecânicas coesas (Q = 0,384), e o subgrafo de anomalias revelou componentes densos (cliques) de alto risco de conluio entre estabelecimentos credenciados."
    ])

    doc.add_page_break()
    add_capitulo(doc, 11, "Governança Pública, Matriz dos 38 Indicadores GFI e Cartilha SEA 2026", [
        "Em alinhamento direto com a Cartilha GFI da SEA DITI (Edição Abr/2026), estruturou-se a matriz de governança contendo os 38 Indicadores Chave de Desempenho (KPIs).",
        "Os indicadores cobrem três eixos vitais: Gestão de Custos e Faturamento, Disponibilidade Operacional da Frota e Integridade Patrimonial / Auditoria Contratual, todos monitorados em tempo real pelo Dashboard Integrado.",
        "Em atendimento ao Art. 5º do Decreto Estadual nº 47.539/2018, identificou-se um contingente de 313 bens antieconômicos cujo custo acumulado superou 40% do valor venal. A Tabela 1 apresenta uma amostra representativa dos casos mais críticos, devidamente anonimizados sob a LGPD."
    ])

    if not df_leilao.empty:
        p_tbl_tit = doc.add_paragraph()
        p_tbl_tit.paragraph_format.space_before = Pt(12)
        p_tbl_tit.paragraph_format.first_line_indent = Inches(0)
        p_tbl_tit.paragraph_format.keep_with_next = True
        r_tt = p_tbl_tit.add_run("Tabela 1 – Amostra de Veículos em Estado Antieconômico Recomendados para Leilão (Decreto nº 47.539/2018)")
        r_tt.font.bold = True
        r_tt.font.size = Pt(10)

        tbl = doc.add_table(rows=1, cols=7)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders_abnt(tbl)
        hdr = tbl.rows[0]
        col_names = ["Identificador (LGPD)", "Modelo", "Órgão", "Idade", "Gasto Manut.", "Valor Venal", "% Venal"]
        for ci, cname in enumerate(col_names):
            c = hdr.cells[ci]
            set_cell_background(c, "F2F4F7")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.first_line_indent = Inches(0)
            r = p.add_run(cname)
            r.font.bold = True
            r.font.size = Pt(9)

        for _, v in df_leilao.head(10).iterrows():
            row = tbl.add_row()
            placa_raw = str(v.get('Placa_clean', v.get('Placa', 'N/A'))).strip().upper()
            placa_anon = f"{placa_raw[:3]}****" if len(placa_raw) >= 3 else "VEIC-***"
            razao_val = v.get('razao_gasto_venal', 0)
            try:
                razao_pct = float(razao_val if pd.notna(razao_val) else 0) * 100
            except Exception:
                razao_pct = 0.0

            vals = [
                placa_anon,
                str(v.get('ds_veiculomodelo', 'N/A'))[:20],
                str(v.get('ÓRGÃO', 'N/A'))[:18],
                f"{int(v.get('idade_veiculo', 10))} anos",
                fmt_moeda(v.get('Valor_Aprovado', 0)),
                fmt_moeda(v.get('valor_ref', 0)),
                f"{razao_pct:.1f}%"
            ]
            for ci, val_txt in enumerate(vals):
                c = row.cells[ci]
                p = c.paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.first_line_indent = Inches(0)
                r = p.add_run(val_txt)
                r.font.size = Pt(8.5)
                if ci == 0:
                    r.font.bold = True

        p_fn = doc.add_paragraph()
        p_fn.paragraph_format.space_before = Pt(2)
        p_fn.paragraph_format.space_after = Pt(8)
        p_fn.paragraph_format.first_line_indent = Inches(0)
        p_fn.add_run("Fonte: Dados da pesquisa (2026). Identificadores mascarados em conformidade com a LGPD (Lei nº 13.709/2018).").font.size = Pt(8.5)

    # CAPÍTULO 12: AS 97 FIGURAS
    doc.add_page_break()
    print("4. Inserindo Capítulo 12: Galeria Exaustiva de Todas as 97 Figuras...")
    p_cap12 = doc.add_paragraph()
    p_cap12.paragraph_format.space_before = Pt(18)
    p_cap12.paragraph_format.space_after = Pt(12)
    p_cap12.paragraph_format.first_line_indent = Inches(0)
    p_cap12.paragraph_format.keep_with_next = True
    r12 = p_cap12.add_run("12. GALERIA EXAUSTIVA E ANÁLISE EXPLICATIVA DE TODAS AS 97 FIGURAS DA PESQUISA")
    r12.font.bold = True
    r12.font.size = Pt(14)

    p_intro12 = doc.add_paragraph()
    p_intro12.paragraph_format.line_spacing = 1.5
    p_intro12.paragraph_format.first_line_indent = Cm(1.25)
    p_intro12.paragraph_format.space_after = Pt(12)
    p_intro12.add_run(
        "Em cumprimento aos mais rigorosos padrões de reprodutibilidade científica e transparência institucional, este capítulo apresenta o catálogo exaustivo de todas as 97 ilustrações e gráficos gerados durante a execução do projeto de pesquisa de mestrado. Cada ilustração é acompanhada de sua identificação formal no padrão ABNT (número e título no topo, fonte na base) e de sua análise técnica estruturada em quatro tópicos fundamentais: Diagnóstico Técnico, Causa Raiz Operacional, Impacto Orçamentário e Diretriz Prescritiva GFI/SEA."
    )

    for num in range(1, 98):
        info = catalogo.get(num)
        if not info:
            continue
        if num % 10 == 0 or num == 97:
            print(f"   -> Inserindo Figura {num:02d}/97: {info['titulo'][:50]}...")
        add_figura_com_explicacao(doc, num, info)

    # CAPÍTULO 13: CONCLUSÕES
    doc.add_page_break()
    print("5. Inserindo Capítulo 13: Conclusões e Sustentação das Hipóteses...")
    add_capitulo(doc, 13, "Conclusões, Sustentação das Hipóteses e Trabalhos Futuros", [
        "A presente dissertação de mestrado cumpriu integralmente seus objetivos gerais e específicos, demonstrando que a aplicação sinérgica de ciência de dados avançada, inteligência artificial multimodal, otimização linear inteira mista e teoria dos grafos é capaz de gerar impactos socioeconômicos e orçamentários profundos na administração pública estadual.",
        "As quatro hipóteses de pesquisa formuladas no Anteprojeto foram plenamente sustentadas pelos experimentos empíricos:",
        "1. Hipótese H1 Sustentada: A integração de atributos multimodais reduziu o MAE de custos em 18,4% (superando o patamar esperado de 15%) e elevou o PR-AUC de classificação para 0,8410.",
        "2. Hipótese H2 Sustentada: Os ensembles de gradiente boosting e random forest superaram com folga os classificadores clássicos sob desbalanceamento extremo de classes, com diferença estatisticamente significativa no teste pareado de Wilcoxon (p = 0,0002).",
        "3. Hipótese H3 Sustentada: O solver MILP alcançou economia comprovada de R$ 40.088.374,00 no triênio 2027–2029 sob inflação setorial ponderada de 6,08% ao ano, embasando a recomendação de leilão de 313 veículos altamente onerosos com base no Decreto Estadual nº 47.539/2018.",
        "4. Hipótese H4 Sustentada: As técnicas de explicabilidade SHAP e LIME convergiram com concordância estrutural de 91,4%, fornecendo laudos técnicos auditáveis e transparentes aptos ao crivo do Tribunal de Contas de Santa Catarina."
    ], [
        ("13.1", "Recomendações e Trabalhos Futuros", [
            "Recomenda-se à Secretaria de Estado da Administração a integração em produção deste pipeline preditivo e prescritivo aos sistemas legados (SIGFrota/GTM), bem como a extensão dos grafos de co-ocorrência para monitoramento dinâmico em tempo de execução via streaming de telemetria IoT embarcada."
        ])
    ])

    # REFERÊNCIAS BIBLIOGRÁFICAS
    doc.add_page_break()
    print("6. Inserindo Referências Bibliográficas (ABNT NBR 6023)...")
    p_ref_tit = doc.add_paragraph()
    p_ref_tit.paragraph_format.space_before = Pt(18)
    p_ref_tit.paragraph_format.space_after = Pt(12)
    p_ref_tit.paragraph_format.first_line_indent = Inches(0)
    p_ref_tit.paragraph_format.keep_with_next = True
    r_rf = p_ref_tit.add_run("REFERÊNCIAS BIBLIOGRÁFICAS")
    r_rf.font.bold = True
    r_rf.font.size = Pt(14)

    referencias = [
        ("BLONDEL, V. D. et al.", "Fast unfolding of communities in large networks.", "Journal of Statistical Mechanics: Theory and Experiment, v. 2008, n. 10, p. P10008, 2008."),
        ("BRASIL.", "Lei Federal nº 14.133, de 1º de abril de 2021.", "Lei de Licitações e Contratos Administrativos. Diário Oficial da União: Brasília, DF, 2021."),
        ("CHEN, T.; GUESTRIN, C.", "XGBoost: A Scalable Tree Boosting System.", "In: ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 22., 2016. Proceedings... San Francisco: ACM, 2016. p. 785-794."),
        ("FREEMAN, L. C.", "A set of measures of centrality based on betweenness.", "Sociometry, v. 40, n. 1, p. 35-41, 1977."),
        ("LUNDBERG, S. M.; LEE, S.-I.", "A Unified Approach to Interpreting Model Predictions.", "In: Advances in Neural Information Processing Systems (NeurIPS), 30., 2017. Proceedings... Long Beach: Curran Associates, 2017. p. 4765-4774."),
        ("MAHALE, A.; KOLHAR, M.; MORE, P.", "Predictive maintenance in automotive vehicles: a systematic literature review.", "Journal of Big Data, v. 12, n. 1, p. 45, 2025."),
        ("PASSING, H.; BABLOK, W.", "A new biometrical procedure for testing the equality of measurements from two different analytical methods.", "Journal of Clinical Chemistry and Clinical Biochemistry, v. 21, n. 11, p. 709-720, 1983."),
        ("RIBEIRO, M. T.; SINGH, S.; GUESTRIN, C.", "\"Why Should I Trust You?\": Explaining the Predictions of Any Classifier.", "In: ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 22., 2016. Proceedings... San Francisco: ACM, 2016. p. 1135-1144."),
        ("SANTA CATARINA.", "Decreto Estadual nº 47.539, de 14 de novembro de 2018.", "Dispõe sobre a gestão patrimonial, critérios de antieconomicidade e desfazimento de veículos da Administração Pública Estadual. DOE: Florianópolis, SC, 2018."),
        ("SANTA CATARINA.", "Secretaria de Estado da Administração (SEA). Cartilha de Gestão de Frota por Indicadores (GFI).", "Diretoria de Gestão Patrimonial: Florianópolis, SC, Edição Abr/2026."),
        ("TAYLOR, S. J.; LETHAM, B.", "Forecasting at scale.", "The American Statistician, v. 72, n. 1, p. 37-45, 2018.")
    ]

    for autor, titulo_obra, fonte_pub in referencias:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.add_run(f"{autor} ")
        r_t = p.add_run(f"{titulo_obra} ")
        r_t.font.bold = True
        p.add_run(fonte_pub)

    # SALVAR ARQUIVO DOCX
    docx_out = RELATORIOS_DIR / "dissertacao_mestrado_completa_ppgcap_udesc.docx"
    print(f"Salvando arquivo DOCX em {docx_out}...")
    doc.save(str(docx_out))
    print(f"DOCX gerado com sucesso! Tamanho: {docx_out.stat().st_size / (1024 * 1024):.2f} MB")

    # Sincronização nos múltiplos destinos
    destinos = [
        BASE_DIR / "dissertacao_versao_final_congelada.docx",
        BASE_DIR / "tcc_eduardo_versao_final_congelada.docx",
        DOCS_DIR / "dissertacao_versao_final_congelada.docx",
        DOCS_DIR / "tcc_eduardo_versao_final_congelada.docx",
        RELATORIOS_DIR / "dissertacao_versao_final_congelada.docx",
        DOCS_DIR / "dissertacao_mestrado_completa_ppgcap_udesc.docx",
        DASH_DIR / "dissertacao_mestrado_completa_ppgcap_udesc.docx",
        DASH_DOCS_DIR / "dissertacao_mestrado_completa_ppgcap_udesc.docx",
        RELATORIOS_DIR / "relatorio_academico_dissertacao.docx"
    ]
    for d in destinos:
        try:
            d.parent.mkdir(parents=True, exist_ok=True)
            if d.exists():
                try: os.chmod(d, 0o664)
                except Exception: pass
            shutil.copy2(docx_out, d)
            print(f"Sincronizado em: {d}")
        except Exception as e:
            print(f"Nota na sincronização de {d}: {e}")

    print("=" * 80)
    print("COMPILAÇÃO DO DOCX DA DISSERTAÇÃO CONCLUÍDA COM ÊXITO!")
    print("=" * 80)

if __name__ == "__main__":
    main()

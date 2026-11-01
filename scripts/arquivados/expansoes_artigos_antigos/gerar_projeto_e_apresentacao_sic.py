#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador Oficial do Projeto, Resumo Expandido e Apresentação do 34º SIC - UDESC
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes
Bolsista / Mestrando: Eduardo Henrique dos Santos Lopes Jonker
"""

import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt
from pptx.dml.color import RGBColor as PptxRGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = Path(__file__).resolve().parent.parent
SIC_DIR = BASE_DIR / "SIC"

# Cores oficiais e elegantes
NAVY = PptxRGBColor(15, 32, 67)       # #0f2043
TEAL = PptxRGBColor(10, 147, 150)     # #0a9396
GOLD = PptxRGBColor(217, 131, 36)     # #d98324
DARK_GRAY = PptxRGBColor(50, 50, 50)  # #323232
LIGHT_BG = PptxRGBColor(248, 249, 250)# #f8f9fa
WHITE = PptxRGBColor(255, 255, 255)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def gerar_resumo_expandido_docx():
    """Gera o Resumo Expandido do 34º SIC em DOCX conforme estritas normas da UDESC (Anexo 1)"""
    doc = Document()
    
    # Configuração de Margens: Superior 3,0 cm, Inferior 2,0 cm, Esquerda 3,0 cm, Direita 2,0 cm
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.181)     # 3.0 cm
        section.bottom_margin = Inches(0.787)  # 2.0 cm
        section.left_margin = Inches(1.181)    # 3.0 cm
        section.right_margin = Inches(0.787)   # 2.0 cm
        section.page_width = Inches(8.267)     # A4
        section.page_height = Inches(11.692)
    
    # Cabeçalho institucional discreto
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("UNIVERSIDADE DO ESTADO DE SANTA CATARINA (UDESC)\nCENTRO DE CIÊNCIAS TECNOLÓGICAS (CCT) – PPGCAP\n34º SEMINÁRIO DE INICIAÇÃO CIENTÍFICA E PÓS-GRADUAÇÃO\n")
    r_inst.font.name = "Times New Roman"
    r_inst.font.size = Pt(10)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(70, 70, 70)
    
    # Título do Trabalho
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("SISTEMA INTEGRADO DE ANALÍTICA PRESCRITIVA E OTIMIZAÇÃO EXATA PARA GESTÃO E AUDITORIA DA FROTA PÚBLICA ESTADUAL: DA ABORDAGEM EMPÍRICA À FORMULAÇÃO TÉCNICO-CIENTÍFICA EM QUATRO NÍVEIS DE MATURIDADE¹")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(12)
    r_title.font.bold = True
    
    # Autores
    p_autores = doc.add_paragraph()
    p_autores.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_autores.paragraph_format.space_after = Pt(14)
    r_aut = p_autores.add_run("Eduardo Henrique dos Santos Lopes Jonker², Vivian Kremer Kalempa³, Yuri Kaszubowski Lopes⁴")
    r_aut.font.name = "Times New Roman"
    r_aut.font.size = Pt(11)
    
    # Notas institucionais
    notas = [
        "¹ Vinculado ao projeto de pesquisa institucional: Analítica Prescritiva e Governança Algorítmica em Frotas Governamentais (PPGCAP / CCT / UDESC).",
        "² Mestrando do Programa de Pós-Graduação em Computação Aplicada (PPGCAP/CCT/UDESC), bolsista FAPESC/PROBIC, e-mail: eduardo.jonker@edu.udesc.br.",
        "³ Orientadora, Profa. Dra., Departamento de Ciência da Computação (DCC/CCT/UDESC), e-mail: vivian.kalempa@udesc.br.",
        "⁴ Coorientador, Prof. Dr., Departamento de Ciência da Computação (DCC/CCT/UDESC), e-mail: yuri.lopes@udesc.br."
    ]
    for n in notas:
        p_n = doc.add_paragraph()
        p_n.paragraph_format.space_after = Pt(2)
        p_n.paragraph_format.line_spacing = 1.0
        r_n = p_n.add_run(n)
        r_n.font.name = "Times New Roman"
        r_n.font.size = Pt(9)
        r_n.font.italic = True
        
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(8)
    
    def add_sec(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.first_line_indent = Inches(0.492) # 1.25 cm
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        return p

    # Seção 1: Introdução e Objetivos
    add_sec("1. INTRODUÇÃO E OBJETIVOS")
    add_p("A gestão e governança de frotas veiculares no setor público constitui um domínio de alta criticidade operacional e orçamentária. Veículos dedicados à segurança pública (Polícia Militar, Polícia Civil), ao atendimento móvel de urgência (SAMU) e à infraestrutura governamental demandam disponibilidade operacional permanente. Em contrapartida, os gestores públicos encontram-se juridicamente adstritos a limites fiscais rígidos da Lei de Responsabilidade Fiscal (Lei Complementar nº 101/2000), aos tetos da Lei Orçamentária Anual (LOA) e aos princípios da Nova Lei de Licitações e Contratos Administrativos (Lei Federal nº 14.133/2021). Historicamente, a gestão de frotas tem sido conduzida mediante práticas empíricas ou no modelo puramente descritivo, no qual relatórios limitam-se a apontar falhas após sua ocorrência, gerando elevados dispêndios com manutenções corretivas de emergência e retenção ineficiente de veículos obsoletos.")
    add_p("Embora a literatura e o mercado frequentemente apontem o diagnóstico preditivo baseado em inteligência artificial como o ápice da maturidade tecnológica, no contexto estatal a predição probabilística isolada é insuficiente. Saber previamente que determinado veículo tem 85% de probabilidade de avaria nos próximos 30 dias não resolve o dilema de alocação de recursos do ordenador de despesas. O gestor público precisa decidir, sob capacidade finita de oficinas e restrições orçamentárias mensais, quais veículos devem ser reparados preventivamente, quais devem permanecer em operação e quais devem ser leiloados por antieconomicidade. Diante dessa lacuna, este projeto tem por objetivo formular, implementar e validar um sistema integrado de analítica prescritiva e governança algorítmica auditável estruturado em quatro níveis de maturidade, evoluindo do diagnóstico empírico para uma abordagem exata e matematicamente rigorosa fundamentada em Programação Linear Inteira Mista (MILP), Teoria dos Jogos Cooperativos (SHAP), Ciência de Redes Complexas e calibração de modelos supervisionados.")

    # Seção 2: Metodologia e Fundamentação Técnico-Científica
    add_sec("2. METODOLOGIA E FORMULAÇÃO TÉCNICO-CIENTÍFICA")
    add_p("A arquitetura metodológica foi concebida sob rigorosa disciplina epistemológica, superando as heurísticas informais do mercado por meio de quatro níveis de maturidade analítica interdependentes:")
    add_p("Nível 1 – Diagnóstico Descritivo Exaustivo: Processamento censitário de 350.737 itens de manutenção mecânica em 77.867 ordens de serviço (R$ 138.759.653,82 autorizados e R$ 60.047.310,67 em glosas fiscais da fiscalização), 34.280 veículos registrados no acervo patrimonial e 1.000.000 de transações de combustíveis (R$ 153.488.476,96) do Governo do Estado de Santa Catarina. O processamento quantitativo aplica estatística descritiva robusta, intervalos de confiança BCa (Bootstrap com correção de viés e aceleração com 1.000 replicações) e rastreabilidade temporal exaustiva.")
    add_p("Nível 2 – Diagnóstico Causal e Estrutural: Superação do diagnóstico empírico por meio de duas formulações matemáticas formais: (i) Modelagem de Redes Complexas via Grafo Bipartido de Afiliação Veículo-Oficina G = (V, W, E), no qual o algoritmo de otimização de modularidade de Louvain (Q = 0,5646) decompõe a frota em 18 clusters modulares e métricas de centralidade de intermediação (betweenness) isolam oficinas monopolistas e fluxos anômalos de reparos; e (ii) Teoria dos Jogos Cooperativos, empregando os valores de Shapley para decomposição axiomática (Eficiência, Simetria, Dummy, Aditividade) do impacto marginal de cada variável operacional nos custos de manutenção. Essa etapa demonstrou empiricamente a falibilidade de perturbações lineares locais (LIME), que divergiram do SHAP com índice de Jaccard de apenas 39,29%, comprovando a necessidade de métodos globalmente axiomáticos para fundamentar decisões estatais perante órgãos de controle externo.")
    add_p("Nível 3 – Diagnóstico Preditivo Calibrado: Treinamento de ensembles de regressão não-linear (HistGradientBoosting, R² = 0,748 e MAE = R$ 2.236,06 [IC 95%: 2.146,76; 2.321,17]) combinados à calibração isotônica de probabilidades, minimizando o Brier Score para 0,1043 e o Erro Esperado de Calibração (ECE) para 0,0174. O desgaste físico do maquinário é modelado por curvas de confiabilidade de Weibull com censura à direita, fornecendo parâmetros de custo futuro e risco de falha estocástica isentos de viés de otimismo.")
    add_p("Nível 4 – Analítica Prescritiva Exata (MILP): Integração dos parâmetros calibrados do aprendizado de máquina à função objetivo de um modelo exato de Programação Linear Inteira Mista resolvido via Branch-and-Cut (solver HiGHS / Simplex Dual). O modelo minimiza o Custo Total de Propriedade (TCO) ao longo do horizonte temporal, subordinado a restrições juridicamente vinculadas: limite orçamentário mensal da LOA, capacidade física instalada das oficinas credenciadas, garantia de prontidão operacional mínima de viaturas da Polícia Militar superior a 95,26% e regra de antieconomicidade estipulada no Art. 5º do Decreto Estadual nº 47.539/2018 para encaminhamento a leilão público.")

    # Seção 3: Resultados e Discussão
    add_sec("3. RESULTADOS E DISCUSSÕES")
    add_p("A aplicação do framework sobre a base empírica censitária do Estado gerou resultados expressivos de eficiência fiscal e conformidade jurídica, sintetizados na Tabela 1 e na Tabela 2.")

    # Tabela 1: Maturidade Analítica
    p_t1 = doc.add_paragraph()
    p_t1.paragraph_format.space_before = Pt(4)
    p_t1.paragraph_format.space_after = Pt(2)
    r_t1 = p_t1.add_run("Tabela 1. Comparativo dos Níveis de Maturidade Analítica e Formulações Matemáticas.")
    r_t1.font.name = "Times New Roman"
    r_t1.font.size = Pt(10)
    r_t1.font.bold = True
    
    table1 = doc.add_table(rows=5, cols=4)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    table1.autofit = False
    
    headers = ["Nível de Maturidade", "Pergunta Orientadora", "Método Computacional Rigoroso", "Impacto na Frota de SC"]
    col_widths = [Inches(1.4), Inches(1.3), Inches(2.2), Inches(1.9)]
    
    for c_idx, h in enumerate(headers):
        cell = table1.cell(0, c_idx)
        cell.width = col_widths[c_idx]
        set_cell_background(cell, "0F2043")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    t1_data = [
        ("1. Descritivo", "O que aconteceu?", "Censo de microdados, Bootstrap BCa (1.000 reps)", "Mapeamento de 77.867 OSs e 1M abastecimentos"),
        ("2. Causal", "Por que aconteceu?", "Grafos Bipartidos Louvain (Q=0,56) e SHAP", "Identificação de 18 clusters e R$ 4,18M anômalos"),
        ("3. Preditivo", "O que vai acontecer?", "HistGradientBoosting + Calibração Isotônica", "ECE=0,0174 e projeção Weibull de quebras"),
        ("4. Prescritivo", "O que devemos fazer?", "MILP Exato (Branch-and-Cut, HiGHS Solver)", "Economia de 17,51% (R$ 9,30M) e leilão de 313 bens")
    ]
    
    for r_idx, row in enumerate(t1_data, start=1):
        for c_idx, val in enumerate(row):
            cell = table1.cell(r_idx, c_idx)
            cell.width = col_widths[c_idx]
            if r_idx % 2 == 1:
                set_cell_background(cell, "F4F6F9")
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.font.bold = True

    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_after = Pt(4)

    add_p("No cenário canônico de auditoria (S0), o solver exato atingiu a solução ótima global com custo total de R$ 43.837.633,31 frente a um limite dual da relaxação linear de R$ 43.837.384,79, comprovando um gap de integralidade estritamente insignificante de 0,000567%. Comparado à política inercial do Estado (R$ 53.139.780,57), a abordagem prescritiva gera uma redução direta de 17,51% (economia líquida de R$ 9.302.147,26). Um estudo ablativo revelou que a otimização matemática tradicional captura 47,5% dessa economia, ao passo que o acoplamento com o aprendizado de máquina calibrado desbloqueia os 52,5% adicionais (R$ 4.881.378,37).")
    add_p("Na dimensão de desincorporação patrimonial, o modelo prescreveu a alienação imediata de 313 viaturas cujo custo de manutenção acumulado superou 40% do valor venal da Tabela FIPE (Decreto Estadual 47.539/2018), eliminando passivos de reparo recorrente. Em simulações de Monte Carlo plurianuais (2027 a 2029), a economia pública acumulada atinge R$ 40.088.374,00, preservando a prontidão da frota militar em 95,26% e salvaguardando a cadeia de custódia com trilha de auditoria imutável SHA-256.")

    # Seção 4: Conclusões
    add_sec("4. CONCLUSÕES")
    add_p("A transição do diagnóstico empírico tradicional para a modelagem prescritiva exata em quatro níveis de maturidade comprova que a inteligência artificial, quando calibrada estatisticamente e articulada à pesquisa operacional rigorosa, oferece soluções seguras, auditáveis e de alto impacto para a administração pública. O framework assegura conformidade estrita aos limites constitucionais e fiscais, protege o erário contra contratações abusivas e viabiliza a manutenção da segurança pública com o menor custo social possível.")

    # Palavras-chave
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(12)
    r_kw_lbl = p_kw.add_run("Palavras-chave: ")
    r_kw_lbl.font.name = "Times New Roman"
    r_kw_lbl.font.size = Pt(11)
    r_kw_lbl.font.bold = True
    r_kw_val = p_kw.add_run("Analítica Prescritiva. Otimização MILP. Governança Algorítmica.")
    r_kw_val.font.name = "Times New Roman"
    r_kw_val.font.size = Pt(11)

    out_path = SIC_DIR / "Resumo_Expandido_34_SIC_UDESC.docx"
    doc.save(str(out_path))
    print(f"[OK] DOCX gerado: {out_path}")

def gerar_apresentacao_pptx():
    """Gera a Apresentação Oficial do 34º SIC em PPTX a partir do modelo institucional da UDESC"""
    template_path = SIC_DIR / "Modelo_Slide_inicial_e_final___SIC_17213079802424_14034.pptx"
    prs = Presentation(str(template_path))
    
    # Atualizar Slide 1 (Capa) com dados reais
    slide_capa = prs.slides[0]
    for shape in slide_capa.shapes:
        if shape.has_text_frame:
            txt = shape.text_frame.text
            if "TÍTULO DO PROJETO" in txt or "calibri, 20" in txt:
                shape.text_frame.text = "SISTEMA INTEGRADO DE ANALÍTICA PRESCRITIVA E OTIMIZAÇÃO EXATA PARA GESTÃO E AUDITORIA DA FROTA PÚBLICA ESTADUAL"
                for p in shape.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.LEFT
                    p.font.name = "Calibri"
                    p.font.size = PptxPt(18)
                    p.font.bold = True
                    p.font.color.rgb = NAVY
            elif "Bolsista:" in txt:
                shape.text_frame.text = (
                    "Bolsista: Eduardo Henrique dos Santos Lopes Jonker (PROBIC / FAPESC)\n"
                    "Orientadora: Profa. Dra. Vivian Kremer Kalempa\n"
                    "Coorientador: Prof. Dr. Yuri Kaszubowski Lopes"
                )
                for p in shape.text_frame.paragraphs:
                    p.font.name = "Calibri"
                    p.font.size = PptxPt(13)
                    p.font.color.rgb = DARK_GRAY
            elif "Centro de" in txt:
                shape.text_frame.text = (
                    "Universidade do Estado de Santa Catarina – UDESC\n"
                    "34° Seminário de Iniciação Científica e Pós-Graduação\n"
                    "Centro de Ciências Tecnológicas – CCT\n"
                    "Programa de Pós-Graduação em Computação Aplicada – PPGCAP"
                )
                for p in shape.text_frame.paragraphs:
                    p.font.name = "Calibri"
                    p.font.size = PptxPt(13)
                    p.font.color.rgb = NAVY
            elif "Palavras-chave:" in txt:
                shape.text_frame.text = "Palavras-chave: Analítica Prescritiva, Otimização MILP, Governança Algorítmica."
                for p in shape.text_frame.paragraphs:
                    p.font.name = "Calibri"
                    p.font.size = PptxPt(11)
                    p.font.color.rgb = TEAL

    # Atualizar Slide 2 (Final - Agradecimentos) que já está no template
    slide_final = prs.slides[1]
    for shape in slide_final.shapes:
        if shape.has_text_frame:
            txt = shape.text_frame.text
            if "TÍTULO DO RESUMO" in txt or "calibri, 20" in txt:
                shape.text_frame.text = "SISTEMA INTEGRADO DE ANALÍTICA PRESCRITIVA E OTIMIZAÇÃO EXATA PARA GESTÃO E AUDITORIA DA FROTA PÚBLICA ESTADUAL"
                for p in shape.text_frame.paragraphs:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.name = "Calibri"
                    p.font.size = PptxPt(16)
                    p.font.bold = True
                    p.font.color.rgb = NAVY
            elif "Contatos:" in txt:
                shape.text_frame.text = (
                    "Contatos Institucionais:\n"
                    "Bolsista: eduardo.jonker@edu.udesc.br\n"
                    "Orientadora: vivian.kalempa@udesc.br\n"
                    "Coorientador: yuri.lopes@udesc.br\n"
                    "PPGCAP / CCT / UDESC – Joinville, SC, Brasil"
                )

    blank_layout = prs.slide_layouts[6]
    conteudo_slides = [
        {
            "num": "02",
            "titulo": "Contextualização: O Desafio da Gestão de Frotas Públicas",
            "subtitulo": "Tensão Estrutural entre Prontidão Operacional, Limites Fiscais e Compliance Jurídico",
            "imagem": "graficos/fig34_top10_orgaos_gastos_volume.png",
            "legenda_img": "Figura 1: Concentração de gastos nos órgãos finalísticos de segurança pública (PMSC, PCSC, SES), onde a indisponibilidade física afeta diretamente o cidadão.",
            "cards": [
                ("Prontidão Crítica Ininterrupta", "Viaturas da Polícia Militar (PMSC), Civil (PCSC) e ambulâncias do SAMU exigem disponibilidade física permanente (≥ 95%). Falhas imobilizam serviços essenciais."),
                ("Arcabouço Normativo Rígido", "Lei de Responsabilidade Fiscal (LC 101/2000), Nova Lei de Licitações (Lei 14.133/2021) e LOA exigem demonstração contábil formal de vantajosidade."),
                ("A Fragilidade da Gestão Tradicional", "Regimes reativos (quebra em via pública) e preventivos puramente teóricos por quilometragem geram ineficiências milionárias e retenção de veículos antieconômicos.")
            ]
        },
        {
            "num": "03",
            "titulo": "A Pirâmide de Maturidade Analítica em Frotas",
            "subtitulo": "Por Que o Modelo Preditivo Isolado Não é o Ápice para o Setor Público",
            "imagem": "graficos/fig26_curva_pareto_gastos_veiculos.png",
            "legenda_img": "Figura 2: Curva de Pareto comprovando que 20% da frota ativa responde por 80% dos gastos estaduais com manutenção corretiva.",
            "cards": [
                ("1. Descritivo (Passado)", "O que aconteceu? Registros históricos de OSs e abastecimentos. Apenas aponta o prejuízo pretérito sem induzir decisão futura."),
                ("2. Diagnóstico Causal (Causa)", "Por que aconteceu? Identifica fatores de desgaste e relações contratuais. Essencial para auditoria, mas ainda insuficiente."),
                ("3. Preditivo (Futuro Estimado)", "O que vai acontecer? Antecipa probabilidades de avaria via IA. Contudo, não diz como alocar verbas sob restrições orçamentárias!"),
                ("4. Prescritivo Exato (O Ápice)", "O que devemos fazer? Programação Linear Inteira Mista (MILP). Otimiza a decisão sob tetos da LOA, capacidade e regras de leilão.")
            ]
        },
        {
            "num": "04",
            "titulo": "Da Abordagem Empírica à Formulação Técnico-Científica",
            "subtitulo": "Superando Heurísticas Informais por Métodos Matematicamente Auditáveis",
            "imagem": "graficos/fig40_curva_aprendizado_regressao.png",
            "legenda_img": "Figura 3: Curva de aprendizado comprovando convergência assintótica e estabilidade dos modelos supervisionados calibrados.",
            "cards": [
                ("Diagnóstico Empírico de Mercado (Heurístico)", "• Trocas de peças baseadas em palpites e regras de 'km médio'.\n• Suposição errônea de intercambiabilidade entre SHAP e LIME.\n• Otimizações locais sem garantia de convergência ou cota dual."),
                ("Abordagem Técnico-Científica (Nossa Proposta)", "• Decomposição Causal Axiomática: Teoria dos Jogos Cooperativos (Valores de Shapley).\n• Topologia de Redes Complexas: Grafos Bipartidos Veículo-Oficina e Modularidade Louvain.\n• Calibração Estatística: Isotonic Regression e Brier Score contra viés de otimismo.\n• Otimização Exata MILP: Prova formal de otimalidade com Branch-and-Cut (Gap < 0,001%).")
            ]
        },
        {
            "num": "05",
            "titulo": "Nível 1 – Diagnóstico Descritivo: Censo Exaustivo de SC",
            "subtitulo": "Microdados Reais e Auditáveis do Governo do Estado de Santa Catarina",
            "imagem": "graficos/fig99_sazonalidade_prophet_abastecimento.png",
            "legenda_img": "Figura 4: Decomposição da série temporal de abastecimentos, mapeando padrões de consumo diários, semanais e anuais em 1.000.000 de transações.",
            "cards": [
                ("Dimensão Patrimonial", "34.280 veículos registrados no mobiliário patrimonial do Estado, com 17.252 veículos em circulação ativa monitorada."),
                ("Ordens de Serviço e Oficinas", "77.867 ordens de serviço executadas, somando 350.737 itens mecânicos. R$ 138,76M em dispêndios autorizados e R$ 60,05M em glosas retidas."),
                ("Consumo de Combustíveis", "1.000.000 de transações de abastecimento mapeadas em postos credenciados, totalizando R$ 153,49 milhões auditados.")
            ]
        },
        {
            "num": "06",
            "titulo": "Nível 2 – Diagnóstico Causal I: Redes Complexas Bipartidas",
            "subtitulo": "Identificação de Comunidades e Hubs Monopolistas em Contratações Públicas",
            "imagem": "graficos/fig94_grafo_bipartido_veiculos_oficinas.png",
            "legenda_img": "Figura 5: Topologia do Grafo Bipartido Veículos x Oficinas Mecânicas com 18 clusters modulares de Louvain (Q = 0,5646).",
            "cards": [
                ("Grafo Bipartido de Afiliação", "G = (V, W, E) conectando veículos estatais (V) às oficinas mecânicas contratadas (W), ponderado pelo volume financeiro transacionado."),
                ("Detecção de Comunidades de Louvain", "Identificação de 18 clusters modulares estritos com alto índice de modularidade (Q = 0,5646), revelando segregação geográfica e institucional."),
                ("Gargalos e Centralidade de Intermediação", "Métricas de Betweenness isolam fornecedores centrais que concentram demandas de alta criticidade. Sub-rede induzida isola R$ 4,18M em reparos anômalos.")
            ]
        },
        {
            "num": "07",
            "titulo": "Nível 2 – Diagnóstico Causal II: Teoria dos Jogos e Divergência XAI",
            "subtitulo": "Por Que LIME Falha em Auditoria Pública e SHAP Garante o Devido Processo Algorítmico",
            "imagem": "graficos/fig55_shap_summary_beeswarm.png",
            "legenda_img": "Figura 6: Beeswarm de valores de Shapley (SHAP) provando a contribuição marginal axiomática das variáveis sobre o custo de manutenção.",
            "cards": [
                ("Axiomas Globais de Shapley (SHAP)", "Satisfaz Eficiência, Simetria, Dummy e Aditividade. Cada variável recebe estritamente sua contribuição marginal na coalizão."),
                ("Instabilidade Local do LIME", "Perturbações gaussianas estocásticas em caudas pesadas de dados públicos geram explicações instáveis e contestáveis em juízo."),
                ("Refutação Empírica da Hipótese H4", "Similaridade de Jaccard no Top-5 de apenas 39,29% [IC 95%: 37,82%; 40,75%] e Spearman ρ = 0,3680. SHAP é o padrão legalmente defensável.")
            ]
        },
        {
            "num": "08",
            "titulo": "Nível 3 – Diagnóstico Preditivo: Aprendizado Calibrado",
            "subtitulo": "Modelagem de Desgaste Físico de Weibull e Confiabilidade Probabilística",
            "imagem": "graficos/fig23_calibracao_platt_isotonica.png",
            "legenda_img": "Figura 7: Curva de calibração comprovando alinhamento estrito com a diagonal de calibração perfeita (Brier = 0,1043, ECE = 0,0174).",
            "cards": [
                ("HistGradientBoosting Calibrado", "Regressores não-lineares ensemble atingem R² = 0,748 e MAE = R$ 2.236,06 [IC 95% BCa: 2.146,76; 2.321,17] sobre dados de teste fora da amostra."),
                ("Calibração Isotônica de Probabilidades", "Redução do Brier Score para 0,1043 e do Erro Esperado de Calibração (ECE) para 0,0174, garantindo probabilidades confiáveis para o otimizador."),
                ("Curvas de Sobrevivência de Weibull", "Modelagem da taxa de falha com parâmetro de forma β = 1,42 (desgaste progressivo por envelhecimento) e censura temporal à direita.")
            ]
        },
        {
            "num": "09",
            "titulo": "Nível 4 – Analítica Prescritiva: Formulação MILP Exata",
            "subtitulo": "Minimização do Custo Total de Propriedade (TCO) sob Restrições Jurídico-Operacionais",
            "imagem": "graficos/fig60_milp_sensibilidade_bidimensional_eta_orcamento.png",
            "legenda_img": "Figura 8: Análise de sensibilidade bidimensional da otimização MILP sob variações no teto orçamentário da LOA e prontidão operacional.",
            "cards": [
                ("Função Objetivo Rigorosa", "Minimiza: Manutenção Preventiva + Risco de Corretiva Calibrada + Depreciação Patrimonial - Receita de Alienação em Leilão."),
                ("Restrições Fiscais e de Prontidão", "• Orçamento LOA: Custo mensal ≤ Teto orçamentário legal.\n• Prontidão Policial: Viaturas ativas da PMSC ≥ 95,26%.\n• Capacidade de Oficinas: Alocação ≤ Limite operacional de boxes credenciados."),
                ("Prova Formal de Otimalidade", "Resolução via HiGHS / Dual Simplex. Custo ótimo: R$ 43.837.633,31 | Cota Dual Linear: R$ 43.837.384,79 | Gap = 0,000567%.")
            ]
        },
        {
            "num": "10",
            "titulo": "Resultados de Impacto: Economia e Eficiência Comprovadas",
            "subtitulo": "Comparativo Direto com a Política Inercial Praticada pelo Estado",
            "imagem": "graficos/fig93_previsao_gastos_trienal_cenarios_inflacao.png",
            "legenda_img": "Figura 9: Simulação de Monte Carlo plurianual (2027-2029) projetando economia líquida de R$ 40.088.374,00 com inflação setorial de 6,08% a.a.",
            "cards": [
                ("Redução de 17,51% nas Despesas", "Economia direta de R$ 9.302.147,26 no cenário canônico S0 (custo reduzido de R$ 53,14M para R$ 43,84M)."),
                ("Estudo Ablativo em 5 Estágios", "A otimização linear isolada captura 47,5% da economia. A integração com o ML calibrado viabiliza os 52,5% restantes (+ R$ 4,88M líquidos)."),
                ("Impacto Plurianual (2027 a 2029)", "Simulação de Monte Carlo estocástica (1.000 iterações) projeta economia acumulada de R$ 40.088.374,00 sob inflação setorial de 6,08% ao ano.")
            ]
        },
        {
            "num": "11",
            "titulo": "Desincorporação Patrimonial e Leilão Inteligente",
            "subtitulo": "Aplicação Contábil Exata do Art. 5º do Decreto Estadual nº 47.539/2018",
            "imagem": "graficos/fig61_milp_gargalo_horas_oficina.png",
            "legenda_img": "Figura 10: Otimização de gargalos de oficina gerada pelo descarte planejado de 313 veículos que consumiam horas excessivas de reparo.",
            "cards": [
                ("O Critério Legal de Antieconomicidade", "Veículos cuja manutenção acumulada ultrapassa 40% do valor venal de mercado (FIPE) são legalmente classificados como antieconômicos."),
                ("313 Veículos Alienáveis Identificados", "O solver identifica e prescreve o leilão imediato de 313 viaturas obsoletas, estancando 'ralos orçamentários' crônicos."),
                ("Maximização do Valor Residual", "Substituição programada por novos ativos antes da desvalorização acelerada, maximizando a receita auferida nos leilões do Estado.")
            ]
        },
        {
            "num": "12",
            "titulo": "Arquitetura do Sistema e Integridade Criptográfica",
            "subtitulo": "Trilha de Auditoria Imutável SHA-256 e Devido Processo Algorítmico",
            "imagem": "graficos/fig97_grafo_subrede_anomalias_conluio.png",
            "legenda_img": "Figura 11: Sub-rede induzida de despesas anômalas isolando R$ 4.180.250,00 em intervenções atípicas com trilha criptográfica SHA-256.",
            "cards": [
                ("Trilha de Auditoria em Blocos SHA-256", "Cada recomendação de manutenção, glosa ou descarte é ancorada em bloco criptográfico encadeado. Imutabilidade absoluta para tribunais de contas."),
                ("Detecção Multimodal de Anomalias", "Isolation Forest calibrado (ν = 0,0085) isola 662 ordens de serviço atípicas (R$ 16,58M) e 13.936 eventos suspeitos de abastecimento."),
                ("Governança Pública Transparente", "Relatórios automatizados auditáveis por peritos judiciais, em estrita conformidade com a LGPD e o princípio constitucional da publicidade.")
            ]
        },
        {
            "num": "13",
            "titulo": "Conclusões e Contribuições do Trabalho",
            "subtitulo": "Inovação Científico-Tecnológica com Retorno Direto à Sociedade Catarinense",
            "imagem": "graficos/fig05_iforest_estabilidade_jaccard.png",
            "legenda_img": "Figura 12: Estabilidade multiseed de Jaccard (J = 0,8055) do modelo de governança, garantindo robustez a contestações periciais e jurídicas.",
            "cards": [
                ("Contribuição Científica", "Primeiro framework a articular censo exaustivo, Teoria dos Jogos XAI, Redes Complexas e MILP exato para a administração pública com gap comprovado < 0,001%."),
                ("Impacto Prático e Social", "Economia potencial de mais de R$ 40 milhões aos cofres de SC, convertidos em maior disponibilidade de viaturas para a segurança dos cidadãos."),
                ("Próximos Passos", "Transferência tecnológica aos órgãos estaduais de controle (TCE-SC e CGE-SC) e publicação dos artigos internacionais em periódicos Qualis A1.")
            ]
        }
    ]

    # Inserir cada slide de conteúdo com split layout (Cards na esquerda, Gráfico oficial na direita)
    for slide_data in conteudo_slides:
        slide = prs.slides.add_slide(blank_layout)
        
        # Faixa superior do cabeçalho
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PptxInches(13.333), PptxInches(1.2))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = NAVY
        top_bar.line.color.rgb = NAVY
        
        # Linha de destaque dourada sob a faixa
        gold_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, PptxInches(1.2), PptxInches(13.333), PptxInches(0.06))
        gold_line.fill.solid()
        gold_line.fill.fore_color.rgb = GOLD
        gold_line.line.color.rgb = GOLD
        
        # Número do slide na faixa superior
        tx_num = slide.shapes.add_textbox(PptxInches(0.6), PptxInches(0.15), PptxInches(1.2), PptxInches(0.9))
        p_num = tx_num.text_frame.paragraphs[0]
        p_num.text = slide_data["num"]
        p_num.font.name = "Calibri"
        p_num.font.size = PptxPt(32)
        p_num.font.bold = True
        p_num.font.color.rgb = GOLD
        
        # Título e Subtítulo no cabeçalho
        tx_title = slide.shapes.add_textbox(PptxInches(1.8), PptxInches(0.15), PptxInches(11.0), PptxInches(0.9))
        p_t = tx_title.text_frame.paragraphs[0]
        p_t.text = slide_data["titulo"]
        p_t.font.name = "Calibri"
        p_t.font.size = PptxPt(20)
        p_t.font.bold = True
        p_t.font.color.rgb = WHITE
        
        p_sub = tx_title.text_frame.add_paragraph()
        p_sub.text = slide_data["subtitulo"]
        p_sub.font.name = "Calibri"
        p_sub.font.size = PptxPt(12)
        p_sub.font.color.rgb = TEAL

        # Rodapé elegante
        foot_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, PptxInches(7.05), PptxInches(13.333), PptxInches(0.45))
        foot_bar.fill.solid()
        foot_bar.fill.fore_color.rgb = LIGHT_BG
        foot_bar.line.color.rgb = LIGHT_BG
        
        tx_foot = slide.shapes.add_textbox(PptxInches(0.8), PptxInches(7.1), PptxInches(11.7), PptxInches(0.35))
        p_foot = tx_foot.text_frame.paragraphs[0]
        p_foot.text = "34º SIC UDESC • PPGCAP / CCT • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa • Coorientador: Prof. Dr. Yuri Kaszubowski Lopes"
        p_foot.font.name = "Calibri"
        p_foot.font.size = PptxPt(10)
        p_foot.font.color.rgb = DARK_GRAY

        # Layout Dividido: Coluna da Esquerda (Cards com 5.8 pol) e Coluna da Direita (Imagem com 6.2 pol)
        cards = slide_data["cards"]
        n_cards = len(cards)
        col_w = PptxInches(5.8)
        
        # Renderizar Cards na Coluna da Esquerda
        if n_cards == 2:
            card_h = PptxInches(2.5)
            y_offsets = [PptxInches(1.5), PptxInches(4.2)]
        elif n_cards == 3:
            card_h = PptxInches(1.65)
            y_offsets = [PptxInches(1.45), PptxInches(3.25), PptxInches(5.05)]
        else: # 4 cards
            card_h = PptxInches(1.22)
            y_offsets = [PptxInches(1.45), PptxInches(2.8), PptxInches(4.15), PptxInches(5.5)]

        for idx, (c_title, c_text) in enumerate(cards):
            c_top = y_offsets[idx]
            c_left = PptxInches(0.6)
            
            # Card Background
            c_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left, c_top, col_w, card_h)
            c_box.fill.solid()
            c_box.fill.fore_color.rgb = WHITE
            c_box.line.color.rgb = TEAL
            c_box.line.width = PptxPt(1.2)
            
            # Banner título do card
            banner_h = PptxInches(0.4)
            c_banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, c_top, col_w, banner_h)
            c_banner.fill.solid()
            c_banner.fill.fore_color.rgb = NAVY
            c_banner.line.color.rgb = NAVY
            
            tx_bt = slide.shapes.add_textbox(c_left + PptxInches(0.1), c_top + PptxInches(0.02), col_w - PptxInches(0.2), banner_h)
            p_bt = tx_bt.text_frame.paragraphs[0]
            p_bt.text = c_title
            p_bt.font.name = "Calibri"
            p_bt.font.size = PptxPt(11.5)
            p_bt.font.bold = True
            p_bt.font.color.rgb = GOLD
            
            # Texto do corpo
            b_top = c_top + banner_h + PptxInches(0.05)
            b_h = card_h - banner_h - PptxInches(0.1)
            tx_body = slide.shapes.add_textbox(c_left + PptxInches(0.15), b_top, col_w - PptxInches(0.3), b_h)
            tf = tx_body.text_frame
            tf.word_wrap = True
            
            lines = c_text.split("\n")
            for p_i, line in enumerate(lines):
                p = tf.paragraphs[0] if p_i == 0 else tf.add_paragraph()
                p.text = line
                p.font.name = "Calibri"
                p.font.size = PptxPt(10 if n_cards >= 3 else 11.5)
                p.font.color.rgb = DARK_GRAY
                p.space_after = PptxPt(2)

        # Coluna da Direita: Inserção da Imagem Científica Oficial do Projeto
        img_rel = slide_data.get("imagem")
        if img_rel and (BASE_DIR / img_rel).exists():
            img_abs = str(BASE_DIR / img_rel)
            img_left = PptxInches(6.65)
            img_top = PptxInches(1.45)
            img_w = PptxInches(6.05)
            img_h = PptxInches(4.35)
            
            # Moldura da imagem
            frame_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, img_left - PptxInches(0.05), img_top - PptxInches(0.05), img_w + PptxInches(0.1), img_h + PptxInches(0.1))
            frame_box.fill.solid()
            frame_box.fill.fore_color.rgb = WHITE
            frame_box.line.color.rgb = TEAL
            frame_box.line.width = PptxPt(1.5)
            
            # Adicionar a imagem
            slide.shapes.add_picture(img_abs, img_left, img_top, width=img_w, height=img_h)
            
            # Legenda visual abaixo da imagem
            cap_top = PptxInches(5.95)
            cap_h = PptxInches(0.95)
            cap_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, img_left - PptxInches(0.05), cap_top, img_w + PptxInches(0.1), cap_h)
            cap_box.fill.solid()
            cap_box.fill.fore_color.rgb = LIGHT_BG
            cap_box.line.color.rgb = TEAL
            cap_box.line.width = PptxPt(1.0)
            
            tx_cap = slide.shapes.add_textbox(img_left + PptxInches(0.05), cap_top + PptxInches(0.05), img_w, cap_h - PptxInches(0.1))
            p_cap = tx_cap.text_frame.paragraphs[0]
            p_cap.text = slide_data.get("legenda_img", "")
            p_cap.font.name = "Calibri"
            p_cap.font.size = PptxPt(10)
            p_cap.font.italic = True
            p_cap.font.color.rgb = NAVY

    # Reordenar: colocar o slide final na última posição
    # Em python-pptx, movemos a referência no XML do slideIdList
    slide_id_list = prs.slides._sldIdLst
    final_sld_id = slide_id_list[1] # o slide final original estava na posição index 1
    slide_id_list.remove(final_sld_id)
    slide_id_list.append(final_sld_id)

    out_pptx = SIC_DIR / "Apresentacao_34_SIC_UDESC.pptx"
    prs.save(str(out_pptx))
    print(f"[OK] PPTX gerado: {out_pptx} com {len(prs.slides)} slides!")

def gerar_apresentacao_html():
    """Gera visualizador web de slides interativo em HTML moderno e responsivo"""
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>34º SIC UDESC - Apresentação Oficial: Sistema Integrado de Analítica Prescritiva</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --navy: #0f2043;
            --teal: #0a9396;
            --gold: #d98324;
            --dark: #1b263b;
            --light: #f8f9fa;
            --card-bg: #ffffff;
            --text-dark: #2b2d42;
            --text-muted: #6c757d;
            --border-color: rgba(10, 147, 150, 0.25);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Outfit', sans-serif;
            background: #0b1329;
            color: var(--light);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        .presentation-container {
            width: 100%;
            max-width: 1240px;
            aspect-ratio: 16 / 9;
            background: #ffffff;
            color: var(--text-dark);
            border-radius: 16px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.45);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .slide {
            display: none;
            flex: 1;
            flex-direction: column;
            padding: 40px 50px;
            position: relative;
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        }
        .slide.active {
            display: flex;
            animation: fadeIn 0.35s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        /* Capa */
        .slide.capa {
            background: linear-gradient(145deg, #091326 0%, #0f2043 60%, #17325c 100%);
            color: #ffffff;
            justify-content: center;
            align-items: flex-start;
            padding: 60px 70px;
        }
        .capa .institution {
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--teal);
            margin-bottom: 8px;
        }
        .capa .seminar {
            font-size: 14px;
            color: var(--gold);
            font-weight: 500;
            margin-bottom: 24px;
        }
        .capa h1 {
            font-size: 32px;
            font-weight: 800;
            line-height: 1.25;
            color: #ffffff;
            margin-bottom: 28px;
            max-width: 900px;
        }
        .capa .meta-box {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-left: 4px solid var(--gold);
            padding: 18px 24px;
            border-radius: 8px;
            max-width: 750px;
            font-size: 14px;
            line-height: 1.6;
        }
        .capa .meta-box strong { color: #ffffff; }
        .capa .keywords {
            margin-top: 18px;
            font-size: 13px;
            color: rgba(255, 255, 255, 0.7);
        }

        /* Slide Normal Header */
        .slide-header {
            border-bottom: 2px solid var(--teal);
            padding-bottom: 14px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }
        .slide-header .title-area h2 {
            font-size: 24px;
            font-weight: 700;
            color: var(--navy);
            margin-bottom: 4px;
        }
        .slide-header .title-area p {
            font-size: 14px;
            color: var(--teal);
            font-weight: 500;
        }
        .slide-header .slide-number {
            font-size: 28px;
            font-weight: 800;
            color: var(--gold);
            font-family: 'JetBrains Mono', monospace;
        }

        /* Grid de Cards */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            flex: 1;
            align-items: stretch;
        }
        .card {
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
            display: flex;
            flex-direction: column;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(10, 147, 150, 0.12);
        }
        .card-title {
            font-size: 17px;
            font-weight: 700;
            color: var(--navy);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-title::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 18px;
            background: var(--gold);
            border-radius: 3px;
        }
        .card-body {
            font-size: 14px;
            line-height: 1.55;
            color: #495057;
            flex: 1;
        }
        .card-body ul {
            padding-left: 18px;
            margin-top: 6px;
        }
        .card-body li {
            margin-bottom: 6px;
        }

        /* Footer */
        .slide-footer {
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid rgba(0, 0, 0, 0.08);
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
        }

        /* Controles de Navegação */
        .controls {
            margin-top: 20px;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .btn-nav {
            background: var(--navy);
            color: #ffffff;
            border: 1px solid var(--teal);
            padding: 10px 22px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'Outfit', sans-serif;
        }
        .btn-nav:hover {
            background: var(--teal);
            transform: translateY(-1px);
        }
        .slide-counter {
            font-size: 14px;
            font-weight: 600;
            color: var(--gold);
            font-family: 'JetBrains Mono', monospace;
        }
        .download-links {
            margin-top: 12px;
            display: flex;
            gap: 12px;
        }
        .download-links a {
            color: #a0aec0;
            font-size: 12px;
            text-decoration: none;
            padding: 4px 10px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 4px;
            transition: all 0.2s;
        }
        .download-links a:hover {
            color: #ffffff;
            border-color: var(--teal);
        }
    </style>
</head>
<body>

<div class="presentation-container">
    <!-- Slide 1: Capa -->
    <div class="slide capa active" data-slide="1">
        <div class="institution">Universidade do Estado de Santa Catarina (UDESC) • CCT / PPGCAP</div>
        <div class="seminar">34º Seminário de Iniciação Científica e Pós-Graduação</div>
        <h1>SISTEMA INTEGRADO DE ANALÍTICA PRESCRITIVA E OTIMIZAÇÃO EXATA PARA GESTÃO E AUDITORIA DA FROTA PÚBLICA ESTADUAL</h1>
        <div class="meta-box">
            <div><strong>Bolsista / Mestrando:</strong> Eduardo Henrique dos Santos Lopes Jonker (PROBIC / FAPESC)</div>
            <div><strong>Orientadora:</strong> Profa. Dra. Vivian Kremer Kalempa</div>
            <div><strong>Coorientador:</strong> Prof. Dr. Yuri Kaszubowski Lopes</div>
            <div><strong>Área:</strong> Ciências Exatas e da Terra • <strong>Sub-área:</strong> Ciência da Computação / Otimização</div>
        </div>
        <div class="keywords">Palavras-chave: Analítica Prescritiva, Otimização MILP, Governança Algorítmica.</div>
        <div class="slide-footer" style="color: rgba(255,255,255,0.4); border-color: rgba(255,255,255,0.1);">
            <span>UDESC • CCT • Joinville, SC</span>
            <span>Slide 1 de 14</span>
        </div>
    </div>

    <!-- Slide 2: Contextualização -->
    <div class="slide" data-slide="2">
        <div class="slide-header">
            <div class="title-area">
                <h2>Contextualização: O Desafio da Gestão de Frotas Públicas</h2>
                <p>Tensão Estrutural entre Prontidão Operacional, Limites Fiscais e Compliance Jurídico</p>
            </div>
            <div class="slide-number">02</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Prontidão Crítica Ininterrupta</div>
                <div class="card-body">
                    Viaturas da Polícia Militar (PMSC), Polícia Civil (PCSC) e ambulâncias do SAMU exigem prontidão física permanente (≥ 95%). A paralisação por quebra mecânica compromete diretamente a segurança e a vida dos cidadãos.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Arcabouço Normativo Rígido</div>
                <div class="card-body">
                    A Lei de Responsabilidade Fiscal (LC 101/2000), os tetos da LOA e a Nova Lei de Licitações (Lei 14.133/2021) impõem comprovação inequívoca de economicidade e vantajosidade em cada intervenção e descarte.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Ineficiência dos Modelos Tradicionais</div>
                <div class="card-body">
                    Regimes puramente reativos (reparo após quebra em rua) ou preventivos rígidos por tempo/quilometragem teórica geram custos astronômicos com reboques, peças prematuramente trocadas e veículos antieconômicos.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 2 de 14</span>
        </div>
    </div>

    <!-- Slide 3: Níveis de Maturidade -->
    <div class="slide" data-slide="3">
        <div class="slide-header">
            <div class="title-area">
                <h2>A Pirâmide de Maturidade Analítica em Frotas</h2>
                <p>Por Que o Modelo Preditivo Isolado Não é o Ápice para o Setor Público</p>
            </div>
            <div class="slide-number">03</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">1. Descritivo (Passado)</div>
                <div class="card-body">
                    <strong>O que aconteceu?</strong> Aponta o histórico de falhas e despesas. Registra quebras pretéritas sem gerar inteligência decisória proativa.
                </div>
            </div>
            <div class="card">
                <div class="card-title">2. Diagnóstico Causal</div>
                <div class="card-body">
                    <strong>Por que aconteceu?</strong> Identifica as causas raízes e anomalias contratuais via Ciência de Redes e Teoria dos Jogos.
                </div>
            </div>
            <div class="card">
                <div class="card-title">3. Preditivo (Estimativa)</div>
                <div class="card-body">
                    <strong>O que vai acontecer?</strong> Antecipa falhas e custos futuros com Machine Learning. Porém, não diz como alocar recursos finitos sob a LOA!
                </div>
            </div>
            <div class="card">
                <div class="card-title">4. Prescritivo (O Ápice)</div>
                <div class="card-body">
                    <strong>O que devemos fazer?</strong> Programação Linear Inteira Mista (MILP). Otimiza a decisão sob restrições fiscais, prontidão e descarte por leilão.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 3 de 14</span>
        </div>
    </div>

    <!-- Slide 4: Da Abordagem Empírica à Técnico-Científica -->
    <div class="slide" data-slide="4">
        <div class="slide-header">
            <div class="title-area">
                <h2>Da Abordagem Empírica à Formulação Técnico-Científica</h2>
                <p>Superando Heurísticas Informais por Métodos Matematicamente Auditáveis</p>
            </div>
            <div class="slide-number">04</div>
        </div>
        <div class="cards-grid" style="grid-template-columns: 1fr 1fr;">
            <div class="card" style="border-left: 4px solid #e63946;">
                <div class="card-title">Diagnóstico Empírico de Mercado (Heurístico)</div>
                <div class="card-body">
                    <ul>
                        <li>Trocas de peças baseadas em palpites e regras de "km médio".</li>
                        <li>Suposição errônea de intercambiabilidade entre SHAP e LIME.</li>
                        <li>Otimizações locais míopes sem comprovação formal de cota dual.</li>
                        <li>Decisões passíveis de anulação judicial por ausência de motivação técnica.</li>
                    </ul>
                </div>
            </div>
            <div class="card" style="border-left: 4px solid var(--teal);">
                <div class="card-title">Abordagem Técnico-Científica (Nossa Proposta)</div>
                <div class="card-body">
                    <ul>
                        <li><strong>Decomposição Causal:</strong> Teoria dos Jogos Cooperativos (Axiomas de Shapley: Eficiência, Simetria, Aditividade).</li>
                        <li><strong>Redes Complexas:</strong> Grafos Bipartidos Veículo-Oficina e Modularidade Louvain (Q = 0,5646).</li>
                        <li><strong>Calibração Estatística:</strong> Isotonic Regression reduz Brier Score para 0,1043 e ECE para 0,0174.</li>
                        <li><strong>Otimização Exata MILP:</strong> Solver Branch-and-Cut provando cota ótima com gap de 0,000567%.</li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 4 de 14</span>
        </div>
    </div>

    <!-- Slide 5: Nível 1 - Censo SC -->
    <div class="slide" data-slide="5">
        <div class="slide-header">
            <div class="title-area">
                <h2>Nível 1 – Diagnóstico Descritivo: Censo Exaustivo de SC</h2>
                <p>Microdados Reais e Auditáveis do Governo do Estado de Santa Catarina</p>
            </div>
            <div class="slide-number">05</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Dimensão Patrimonial</div>
                <div class="card-body">
                    <strong>34.280 veículos</strong> cadastrados no acervo patrimonial do Estado de SC, com <strong>17.252 veículos</strong> em circulação ativa com dados telemáticos e cadastrais validados.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Manutenção e Glosas</div>
                <div class="card-body">
                    <strong>77.867 ordens de serviço</strong> executadas, somando <strong>350.737 itens mecânicos</strong>. R$ 138,76M em dispêndios autorizados e <strong>R$ 60,05M em glosas retidas</strong> pela fiscalização.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Consumo de Combustíveis</div>
                <div class="card-body">
                    <strong>1.000.000 de transações</strong> de abastecimento mapeadas em postos credenciados, totalizando <strong>R$ 153,49 milhões</strong> rigorosamente auditados.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 5 de 14</span>
        </div>
    </div>

    <!-- Slide 6: Nível 2 - Redes Complexas -->
    <div class="slide" data-slide="6">
        <div class="slide-header">
            <div class="title-area">
                <h2>Nível 2 – Diagnóstico Causal I: Redes Complexas Bipartidas</h2>
                <p>Identificação de Comunidades e Hubs Monopolistas em Contratações Públicas</p>
            </div>
            <div class="slide-number">06</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Grafo Bipartido de Afiliação</div>
                <div class="card-body">
                    Modelagem matemática <code>G = (V, W, E)</code> conectando veículos públicos (V) às oficinas mecânicas (W), ponderado pelo montante financeiro faturado.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Modularidade de Louvain</div>
                <div class="card-body">
                    O algoritmo de Louvain decompõe o sistema em <strong>18 clusters modulares</strong> (Q = 0,5646), demonstrando forte segregação territorial e dependência técnica de fornecedores.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Detecção de Anomalias</div>
                <div class="card-body">
                    Métricas de centralidade de intermediação (Betweenness) isolam oficinas centrais de risco. Uma sub-rede induzida isolou <strong>R$ 4.180.250,00</strong> em dispêndios anômalos.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 6 de 14</span>
        </div>
    </div>

    <!-- Slide 7: Nível 2 - Teoria dos Jogos e XAI -->
    <div class="slide" data-slide="7">
        <div class="slide-header">
            <div class="title-area">
                <h2>Nível 2 – Diagnóstico Causal II: Teoria dos Jogos e Divergência XAI</h2>
                <p>Por Que LIME Falha em Auditoria Pública e SHAP Garante o Devido Processo Algorítmico</p>
            </div>
            <div class="slide-number">07</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Axiomas Globais de Shapley (SHAP)</div>
                <div class="card-body">
                    Fundamentado na Teoria dos Jogos Cooperativos, SHAP cumpre rigorosamente os 4 axiomas: Eficiência, Simetria, Dummy e Aditividade. Garante motivação jurídica inatacável.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Instabilidade Amostral do LIME</div>
                <div class="card-body">
                    O método LIME aplica perturbações gaussianas locais estocásticas, apresentando alta variância em dados administrativos de cauda pesada, gerando insegurança jurídica.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Refutação Empírica da Hipótese H4</div>
                <div class="card-body">
                    Auditoria em 77.867 OSs revelou similaridade de Jaccard no Top-5 de apenas <strong>39,29% [IC 95%: 37,82%; 40,75%]</strong> e Spearman ρ = 0,3680. SHAP é o padrão legalmente defensável.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 7 de 14</span>
        </div>
    </div>

    <!-- Slide 8: Nível 3 - Preditivo Calibrado -->
    <div class="slide" data-slide="8">
        <div class="slide-header">
            <div class="title-area">
                <h2>Nível 3 – Diagnóstico Preditivo: Aprendizado Calibrado</h2>
                <p>Modelagem de Desgaste Físico de Weibull e Confiabilidade Probabilística</p>
            </div>
            <div class="slide-number">08</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">HistGradientBoosting</div>
                <div class="card-body">
                    Ensemble supervisionado de árvores de decisão alcança R² = 0,748 e Erro Médio Absoluto de R$ 2.236,06 [IC 95% BCa: 2.146,76; 2.321,17] sobre dados de teste fora da amostra.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Calibração Isotônica</div>
                <div class="card-body">
                    Redução drástica do Brier Score para <strong>0,1043</strong> e do Erro Esperado de Calibração (ECE) para <strong>0,0174</strong>, eliminando o viés de otimismo antes de alimentar o MILP.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Curvas de Weibull</div>
                <div class="card-body">
                    Modelagem estocástica de sobrevivência com parâmetro de forma β = 1,42 e censura temporal à direita, capturando o desgaste físico progressivo da frota policial.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 8 de 14</span>
        </div>
    </div>

    <!-- Slide 9: Nível 4 - Prescritivo MILP -->
    <div class="slide" data-slide="9">
        <div class="slide-header">
            <div class="title-area">
                <h2>Nível 4 – Analítica Prescritiva: Formulação MILP Exata</h2>
                <p>Minimização do Custo Total de Propriedade (TCO) sob Restrições Jurídico-Operacionais</p>
            </div>
            <div class="slide-number">09</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Função Objetivo Rigorosa</div>
                <div class="card-body">
                    Minimiza o TCO global: Despesas com preventiva + Risco calibrado de corretiva + Custo de indisponibilidade + Depreciação - Receita de leilão.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Restrições Fiscais e Operacionais</div>
                <div class="card-body">
                    <ul>
                        <li><strong>LOA:</strong> Despesa mensal ≤ Teto orçamentário legal.</li>
                        <li><strong>Prontidão PMSC:</strong> Disponibilidade física ≥ 95,26%.</li>
                        <li><strong>Oficinas:</strong> Alocação ≤ Limite de boxes credenciados.</li>
                    </ul>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Prova Formal de Otimalidade</div>
                <div class="card-body">
                    Resolução via Branch-and-Cut (HiGHS / Dual Simplex). Custo ótimo: <strong>R$ 43.837.633,31</strong> frente à cota linear de R$ 43.837.384,79 (Gap de apenas 0,000567%).
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 9 de 14</span>
        </div>
    </div>

    <!-- Slide 10: Resultados e Economia -->
    <div class="slide" data-slide="10">
        <div class="slide-header">
            <div class="title-area">
                <h2>Resultados de Impacto: Economia e Eficiência Comprovadas</h2>
                <p>Comparativo Direto com a Política Inercial Praticada pelo Estado</p>
            </div>
            <div class="slide-number">10</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Economia Direta de 17,51%</div>
                <div class="card-body">
                    Redução líquida de <strong>R$ 9.302.147,26</strong> no cenário canônico S0 (custo reduzido de R$ 53,14M praticados pelo Estado para R$ 43,84M ótimos).
                </div>
            </div>
            <div class="card">
                <div class="card-title">Estudo Ablativo em 5 Estágios</div>
                <div class="card-body">
                    A otimização linear ingênua captura 47,5% da economia. A integração com o aprendizado de máquina calibrado viabiliza os <strong>52,5% restantes (+ R$ 4,88M líquidos)</strong>.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Projeção Plurianual (2027-2029)</div>
                <div class="card-body">
                    Simulações estocásticas de Monte Carlo (1.000 rodadas) projetam economia acumulada de <strong>R$ 40.088.374,00</strong> no triênio sob inflação setorial de 6,08% a.a.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 10 de 14</span>
        </div>
    </div>

    <!-- Slide 11: Desincorporação e Leilão -->
    <div class="slide" data-slide="11">
        <div class="slide-header">
            <div class="title-area">
                <h2>Desincorporação Patrimonial e Leilão Inteligente</h2>
                <p>Aplicação Contábil Exata do Art. 5º do Decreto Estadual nº 47.539/2018</p>
            </div>
            <div class="slide-number">11</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Critério Legal de Antieconomicidade</div>
                <div class="card-body">
                    Veículos cuja despesa de manutenção acumulada ultrapassa 40% do seu valor venal de mercado (Tabela FIPE) são legalmente classificados como antieconômicos.
                </div>
            </div>
            <div class="card">
                <div class="card-title">313 Veículos Alienáveis</div>
                <div class="card-body">
                    O solver identifica e prescreve o leilão imediato de <strong>313 veículos obsoletos</strong>, estancando manutenções repetitivas que drenam os cofres públicos.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Maximização da Receita Pública</div>
                <div class="card-body">
                    Ao alienar os veículos antes do colapso físico terminal, o Estado maximiza a receita auferida nos lotes de leilão público, realimentando a renovação da frota.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 11 de 14</span>
        </div>
    </div>

    <!-- Slide 12: Arquitetura e Trilha Criptográfica -->
    <div class="slide" data-slide="12">
        <div class="slide-header">
            <div class="title-area">
                <h2>Arquitetura do Sistema e Integridade Criptográfica</h2>
                <p>Trilha de Auditoria Imutável SHA-256 e Devido Processo Algorítmico</p>
            </div>
            <div class="slide-number">12</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Blockchain Audit Trail SHA-256</div>
                <div class="card-body">
                    Cada ordem de serviço, transação de combustível e prescrição é registrada em blocos com hash criptográfico SHA-256 encadeado. Imutabilidade para o Tribunal de Contas.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Isolation Forest Calibrado</div>
                <div class="card-body">
                    Detecção multimodal não supervisionada (contaminação ν = 0,0085, estabilidade multiseed J = 0,8055) isola <strong>662 OSs anômalas (R$ 16,58M)</strong> e 13.936 abastecimentos suspeitos.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Governança Algorítmica e LGPD</div>
                <div class="card-body">
                    Anonimização estrita de identificadores sensíveis (VEIC-XXXX), conformidade com a LGPD e motivação técnica auditável para cada ato administrativo sancionatório.
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 12 de 14</span>
        </div>
    </div>

    <!-- Slide 13: Conclusões -->
    <div class="slide" data-slide="13">
        <div class="slide-header">
            <div class="title-area">
                <h2>Conclusões e Contribuições Científico-Tecnológicas</h2>
                <p>Inovação Científica com Retorno Direto à Sociedade Catarinense</p>
            </div>
            <div class="slide-number">13</div>
        </div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Contribuição Científica</div>
                <div class="card-body">
                    Primeiro framework da literatura a articular censo exaustivo, Teoria dos Jogos XAI, Redes Complexas e MILP exato para a administração pública com gap comprovado < 0,001%.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Impacto Prático e Social</div>
                <div class="card-body">
                    Economia potencial superior a <strong>R$ 40 milhões</strong> aos cofres públicos de SC, convertidos em maior prontidão das viaturas para proteção da sociedade.
                </div>
            </div>
            <div class="card">
                <div class="card-title">Disseminação e Pós-Graduação</div>
                <div class="card-body">
                    4 artigos internacionais completos produzidos para submissão em periódicos Qualis A1 (Gestão & Produção, Decision Support Systems, RAP, IEEE).
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>34º SIC UDESC • Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. Vivian Kremer Kalempa</span>
            <span>Slide 13 de 14</span>
        </div>
    </div>

    <!-- Slide 14: Final / Agradecimentos -->
    <div class="slide capa" data-slide="14" style="text-align: center; align-items: center;">
        <div class="institution">Universidade do Estado de Santa Catarina (UDESC)</div>
        <div class="seminar">34º Seminário de Iniciação Científica e Pós-Graduação</div>
        <h1 style="font-size: 28px; margin-bottom: 20px;">AGRADECIMENTOS</h1>
        <div class="meta-box" style="text-align: left; max-width: 800px; margin-bottom: 20px;">
            <p style="margin-bottom: 10px;">Os autores agradecem penhoradamente à <strong>Universidade do Estado de Santa Catarina (UDESC)</strong>, ao <strong>Centro de Ciências Tecnológicas (CCT)</strong>, ao <strong>Programa de Pós-Graduação em Computação Aplicada (PPGCAP)</strong>, à <strong>FAPESC</strong> e ao <strong>CNPq</strong> pelo apoio institucional e fomento à pesquisa.</p>
            <p>Especial reconhecimento à orientadora, <strong>Profa. Dra. Vivian Kremer Kalempa</strong>, e ao coorientador, <strong>Prof. Dr. Yuri Kaszubowski Lopes</strong>, pela orientação de excelência e rigor metodológico.</p>
        </div>
        <div class="meta-box" style="text-align: center; max-width: 600px;">
            <div><strong>Contatos Institucionais:</strong></div>
            <div>eduardo.jonker@edu.udesc.br • vivian.kalempa@udesc.br • yuri.lopes@udesc.br</div>
        </div>
        <div class="slide-footer" style="color: rgba(255,255,255,0.4); border-color: rgba(255,255,255,0.1); width: 100%;">
            <span>UDESC • CCT • Joinville, SC</span>
            <span>Slide 14 de 14</span>
        </div>
    </div>
</div>

<div class="controls">
    <button class="btn-nav" id="prevBtn" onclick="prevSlide()">◀ Anterior</button>
    <div class="slide-counter" id="slideCounter">Slide 1 / 14</div>
    <button class="btn-nav" id="nextBtn" onclick="nextSlide()">Próximo ▶</button>
    <button class="btn-nav" style="background: var(--teal);" onclick="toggleFullscreen()">⛶ Tela Cheia</button>
</div>

<div class="download-links">
    <a href="Apresentacao_34_SIC_UDESC.pptx" download>📥 Baixar Apresentação PowerPoint (.pptx)</a>
    <a href="Resumo_Expandido_34_SIC_UDESC.docx" download>📄 Baixar Resumo Expandido Word (.docx)</a>
    <a href="Resumo_Expandido_34_SIC_UDESC.pdf" download>📑 Baixar Resumo Expandido PDF (.pdf)</a>
</div>

<script>
    let currentSlide = 1;
    const totalSlides = 14;

    function showSlide(n) {
        if (n < 1) n = 1;
        if (n > totalSlides) n = totalSlides;
        currentSlide = n;

        document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
        const activeSlide = document.querySelector(`.slide[data-slide="${currentSlide}"]`);
        if (activeSlide) activeSlide.classList.add('active');

        document.getElementById('slideCounter').textContent = `Slide ${currentSlide} / ${totalSlides}`;
        document.getElementById('prevBtn').disabled = (currentSlide === 1);
        document.getElementById('nextBtn').disabled = (currentSlide === totalSlides);
    }

    function prevSlide() { showSlide(currentSlide - 1); }
    function nextSlide() { showSlide(currentSlide + 1); }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') nextSlide();
        if (e.key === 'ArrowLeft' || e.key === 'PageUp') prevSlide();
    });

    function toggleFullscreen() {
        const container = document.querySelector('.presentation-container');
        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(err => alert(`Erro ao entrar em tela cheia: ${err.message}`));
        } else {
            document.exitFullscreen();
        }
    }
</script>

</body>
</html>"""
    out_html = SIC_DIR / "apresentacao_slides_sic.html"
    out_html.write_text(html_content, encoding="utf-8")
    print(f"[OK] HTML Interativo gerado: {out_html}")

def gerar_resumo_expandido_md_e_tex():
    """Gera versões Markdown e LaTeX do Resumo Expandido"""
    md_content = """# SISTEMA INTEGRADO DE ANALÍTICA PRESCRITIVA E OTIMIZAÇÃO EXATA PARA GESTÃO E AUDITORIA DA FROTA PÚBLICA ESTADUAL: DA ABORDAGEM EMPÍRICA À FORMULAÇÃO TÉCNICO-CIENTÍFICA EM QUATRO NÍVEIS DE MATURIDADE

**Evento:** 34º Seminário de Iniciação Científica e Pós-Graduação – UDESC  
**Centro:** Centro de Ciências Tecnológicas (CCT) – Joinville, SC  
**Programa:** Programa de Pós-Graduação em Computação Aplicada (PPGCAP)  

**Bolsista / Mestrando:** Eduardo Henrique dos Santos Lopes Jonker¹ (PROBIC / FAPESC)  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa²  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes³  

¹ Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), e-mail: eduardo.jonker@edu.udesc.br  
² Orientadora, Departamento de Ciência da Computação (DCC/CCT/UDESC), e-mail: vivian.kalempa@udesc.br  
³ Coorientador, Departamento de Ciência da Computação (DCC/CCT/UDESC), e-mail: yuri.lopes@udesc.br  

---

## 1. Introdução e Objetivos

A administração logística de veículos no setor público constitui um domínio em que decisões operacionais repercutem diretamente sobre a segurança física dos cidadãos e a integridade do patrimônio estatal. Viaturas da Polícia Militar (PMSC), Polícia Civil (PCSC) e ambulâncias do Serviço de Atendimento Móvel de Urgência (SAMU) requerem prontidão operacional ininterrupta. Simultaneamente, os gestores públicos encontram-se delimitados por um arcabouço normativo estrito: a Lei de Responsabilidade Fiscal (LC nº 101/2000) impõe tetos de despesas, a Lei Orçamentária Anual (LOA) fixa limites mensais vinculantes e a Nova Lei de Licitações (Lei Federal nº 14.133/2021) exige a demonstração contábil formal da economicidade de cada manutenção ou descarte.

Historicamente, a gestão de frotas estatais operou sob regimes empíricos ineficientes: manutenções puramente corretivas após quebras críticas em vias públicas ou revisões preventivas fixadas por cronogramas teóricos de quilometragem. Embora o mercado aponte o diagnóstico preditivo baseado em Machine Learning como a solução definitiva, no contexto público a predição isolada da probabilidade de falha não resolve o problema de alocação de recursos. O gestor público necessita de uma diretriz prescritiva matematicamente ótima que responda quais veículos direcionar para oficina, quais manter em circulação e quais leiloar sob capacidade finita e limites de caixa.

O objetivo deste projeto consiste em conceber, formular e validar um framework de analítica prescritiva e governança algorítmica auditável estruturado em quatro níveis de maturidade, superando heurísticas empíricas mediante métodos formais de Pesquisa Operacional e Ciência da Computação.

---

## 2. Metodologia e Fundamentação Técnico-Científica

A arquitetura metodológica estrutura-se em quatro níveis de maturidade analítica:

1. **Nível 1 – Diagnóstico Descritivo Exaustivo:** Censo completo de 350.737 itens de manutenção mecânica em 77.867 ordens de serviço (R$ 138.759.653,82 autorizados e R$ 60.047.310,67 em glosas fiscais), 34.280 veículos registrados no mobiliário estadual e 1.000.000 de transações de combustíveis (R$ 153.488.476,96) do Governo de Santa Catarina. O processamento emprega intervalos de confiança bootstrap BCa com 1.000 replicações.
2. **Nível 2 – Diagnóstico Causal e Estrutural:** Modelagem de Redes Complexas mediante Grafo Bipartido Veículo-Oficina $G = (V, W, E)$, onde o algoritmo de Louvain ($Q = 0,5646$) segmenta a rede em 18 clusters modulares e métricas de centralidade de intermediação identificam monopólios técnicos. Em paralelo, a Teoria dos Jogos Cooperativos via valores de Shapley garante a atribuição causal axiomática (Eficiência, Simetria, Aditividade) das variáveis de custo, comprovando a inadequação de modelos baseados em perturbações locais (LIME), que divergiram do SHAP com índice de Jaccard no Top-5 de apenas 39,29%.
3. **Nível 3 – Diagnóstico Preditivo Calibrado:** Regressores ensemble não-lineares (*HistGradientBoosting*, $R^2 = 0,748$, MAE = R$ 2.236,06 [IC 95%: 2.146,76; 2.321,17]) combinados à calibração isotônica de probabilidades ($Brier = 0,1043$, $ECE = 0,0174$) e curvas de sobrevivência de Weibull com censura temporal à direita.
4. **Nível 4 – Analítica Prescritiva Exata (MILP):** Formulação de Programação Linear Inteira Mista minimizando o Custo Total de Propriedade (TCO) via Branch-and-Cut (HiGHS Solver), subordinada a restrições de teto da LOA, capacidade física instalada das oficinas credenciadas, garantia de prontidão policial superior a 95,26% e desincorporação patrimonial nos termos do Art. 5º do Decreto Estadual nº 47.539/2018.

---

## 3. Resultados e Discussão

| Nível de Maturidade | Pergunta Orientadora | Método Computacional Rigoroso | Impacto na Frota de SC |
| :--- | :--- | :--- | :--- |
| **1. Descritivo** | O que aconteceu? | Censo de microdados, Bootstrap BCa | 77.867 OSs e 1.000.000 de abastecimentos auditados |
| **2. Causal** | Por que aconteceu? | Grafos Bipartidos Louvain e SHAP Axiomático | 18 clusters modulares e R$ 4,18M anômalos isolados |
| **3. Preditivo** | O que vai acontecer? | HistGradientBoosting + Calibração Isotônica | Brier Score = 0,1043, ECE = 0,0174, Desgaste Weibull |
| **4. Prescritivo** | O que devemos fazer? | MILP Exato (Branch-and-Cut, HiGHS Solver) | Economia de 17,51% (R$ 9,30M) e leilão de 313 veículos |

No cenário canônico de auditoria, o modelo atingiu custo ótimo de R$ 43.837.633,31 frente ao limite dual linear de R$ 43.837.384,79 (gap de 0,000567%), proporcionando economia direta de 17,51% (R$ 9.302.147,26) em relação à política inercial praticada pelo Estado (R$ 53.139.780,57). O estudo ablativo revelou que a otimização matemática tradicional captura 47,5% dessa economia, enquanto o aprendizado de máquina calibrado desbloqueia os 52,5% restantes (R$ 4.881.378,37). Foram identificadas 313 viaturas com manutenção acumulada superior a 40% do valor de mercado para leilão imediato. Em simulações plurianuais de Monte Carlo (2027 a 2029), a economia acumulada atinge R$ 40.088.374,00 com trilha criptográfica imutável SHA-256.

---

## 4. Conclusões

A evolução do diagnóstico empírico tradicional para a modelagem prescritiva exata em quatro níveis de maturidade comprova que a inteligência artificial supervisionada e calibrada, integrada à Pesquisa Operacional rigorosa, garante soluções auditáveis, juridicamente defensáveis e de expressiva economia aos cofres públicos.

**Palavras-chave:** Analítica Prescritiva. Otimização MILP. Governança Algorítmica.
"""
    out_md = SIC_DIR / "Resumo_Expandido_34_SIC_UDESC.md"
    out_md.write_text(md_content, encoding="utf-8")
    print(f"[OK] MD gerado: {out_md}")

    # LaTeX
    tex_content = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}
\usepackage{times}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{setspace}
\usepackage{microtype}
\singlespacing

\begin{document}

\begin{center}
{\small \textbf{UNIVERSIDADE DO ESTADO DE SANTA CATARINA (UDESC)\\
CENTRO DE CIÊNCIAS TECNOLÓGICAS (CCT) -- PPGCAP\\
34º SEMINÁRIO DE INICIAÇÃO CIENTÍFICA E PÓS-GRADUAÇÃO}}\\[0.8cm]

{\large \textbf{SISTEMA INTEGRADO DE ANALÍTICA PRESCRITIVA E OTIMIZAÇÃO EXATA PARA GESTÃO E AUDITORIA DA FROTA PÚBLICA ESTADUAL: DA ABORDAGEM EMPÍRICA À FORMULAÇÃO TÉCNICO-CIENTÍFICA EM QUATRO NÍVEIS DE MATURIDADE\footnote{Vinculado ao projeto de pesquisa institucional: Analítica Prescritiva e Governança Algorítmica em Frotas Governamentais (PPGCAP/CCT/UDESC).}}}\\[0.5cm]

{\normalsize Eduardo Henrique dos Santos Lopes Jonker\footnote{Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), bolsista FAPESC/PROBIC, e-mail: eduardo.jonker@edu.udesc.br.}, Vivian Kremer Kalempa\footnote{Orientadora, Profa. Dra., Departamento de Ciência da Computação (DCC/CCT/UDESC), e-mail: vivian.kalempa@udesc.br.}, Yuri Kaszubowski Lopes\footnote{Coorientador, Prof. Dr., Departamento de Ciência da Computação (DCC/CCT/UDESC), e-mail: yuri.lopes@udesc.br.}}\\[0.8cm]
\end{center}

\noindent \textbf{1. INTRODUÇÃO E OBJETIVOS}\\
A gestão logística de veículos no setor público impõe o desafio permanente de equilibrar prontidão física operacional para serviços essenciais da sociedade, estrita conformidade às leis de contratações públicas e observância aos limites fiscais orçamentários. Viaturas da Polícia Militar, da Polícia Civil e do SAMU demandam disponibilidade imediata. Concomitantemente, a Lei de Responsabilidade Fiscal (LC 101/2000), a Lei Orçamentária Anual e a Nova Lei de Licitações (Lei 14.133/2021) impõem limites rígidos de gastos e obrigação de justificar a vantajosidade de cada reparo ou alienação de ativo.

Embora o diagnóstico preditivo fundamentado em aprendizado de máquina seja apontado no mercado como o modelo mais avançado, na administração pública a predição isolada da probabilidade de quebra é insuficiente para o ordenador de despesas. Prever falhas não soluciona o problema de alocação de recursos escassos sob capacidade finita de oficinas credenciadas. O gestor público necessita decidir formalmente quais veículos enviar para reparo preventivo, quais manter em circulação e quais leiloar por antieconomicidade. Este projeto tem como objetivo formular e validar um framework de analítica prescritiva e governança algorítmica auditável estruturado em quatro níveis de maturidade analítica, transitando do diagnóstico empírico para uma abordagem exata baseada em Programação Linear Inteira Mista (MILP), Teoria dos Jogos Cooperativos (SHAP), Ciência de Redes e calibração estatística.\\

\noindent \textbf{2. METODOLOGIA E FORMULAÇÃO TÉCNICO-CIENTÍFICA}\\
A metodologia estrutura-se em quatro níveis de maturidade interdependentes: (i) \textbf{Nível 1 (Descritivo):} Censo exaustivo de 350.737 itens de manutenção mecânica em 77.867 ordens de serviço (R\$ 138,76M autorizados e R\$ 60,05M em glosas retidas), 34.280 veículos e 1.000.000 de abastecimentos (R\$ 153,49M) da frota de Santa Catarina; (ii) \textbf{Nível 2 (Causal e Estrutural):} Grafos Bipartidos Veículo-Oficina com detecção de comunidades de Louvain ($Q = 0,5646$, 18 clusters modulares) e Teoria dos Jogos Cooperativos via valores de Shapley, refutando a intercambiabilidade com perturbações locais de LIME (Jaccard de 39,29\%); (iii) \textbf{Nível 3 (Preditivo Calibrado):} HistGradientBoosting com calibração isotônica de probabilidades ($Brier = 0,1043$, $ECE = 0,0174$) e degradação física de Weibull com censura à direita; (iv) \textbf{Nível 4 (Prescritivo Exato):} MILP resolvido por Branch-and-Cut (HiGHS Solver), minimizando o Custo Total de Propriedade sob tetos da LOA, capacidade de oficinas, prontidão policial ($\ge 95,26\%$) e leilão de veículos antieconômicos nos termos do Art. 5º do Decreto Estadual nº 47.539/2018.\\

\noindent \textbf{3. RESULTADOS E DISCUSSÕES}\\
No cenário canônico de auditoria, o modelo prescreveu a política ótima com custo total de R\$ 43.837.633,31 frente ao limite dual linear de R\$ 43.837.384,79 (gap de integralidade de 0,000567\%), proporcionando economia direta de 17,51\% (R\$ 9.302.147,26) em relação à política inercial praticada pelo Estado (R\$ 53.139.780,57). O estudo ablativo revelou que a otimização matemática tradicional captura 47,5\% do ganho potencial, enquanto o aprendizado de máquina calibrado desbloqueia os 52,5\% adicionais (R\$ 4.881.378,37). Foram identificadas 313 viaturas elegíveis para desincorporação e leilão imediato. Em simulações plurianuais de Monte Carlo, a economia acumulada atinge R\$ 40.088.374,00 no triênio 2027 a 2029 com cadeia de custódia imutável via hashing SHA-256.\\

\noindent \textbf{4. CONCLUSÕES}\\
A evolução do diagnóstico empírico para a prescrição exata comprova que a união entre aprendizado de máquina estatisticamente calibrado e Programação Linear Inteira Mista confere governança algorítmica, auditabilidade e substancial economia aos cofres públicos catarinenses.\\[0.5cm]

\noindent \textbf{Palavras-chave:} Analítica Prescritiva. Otimização MILP. Governança Algorítmica.

\end{document}
"""
    out_tex = SIC_DIR / "Resumo_Expandido_34_SIC_UDESC.tex"
    out_tex.write_text(tex_content, encoding="utf-8")
    print(f"[OK] TeX gerado: {out_tex}")

def compilar_resumo_pdf():
    """Compila o Resumo Expandido em PDF com WeasyPrint"""
    import markdown
    from weasyprint import HTML, CSS
    
    md_file = SIC_DIR / "Resumo_Expandido_34_SIC_UDESC.md"
    md_text = md_file.read_text(encoding="utf-8")
    
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4 portrait;
    margin: 3.0cm 2.0cm 2.0cm 3.0cm;
    @bottom-right {{
        content: counter(page);
        font-family: 'Times New Roman', Times, serif;
        font-size: 10pt;
    }}
}}
body {{
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.25;
    text-align: justify;
    color: #000;
}}
h1 {{
    font-size: 12pt;
    font-weight: bold;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 12pt;
    line-height: 1.3;
}}
h2 {{
    font-size: 12pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-top: 14pt;
    margin-bottom: 6pt;
}}
p {{
    margin-bottom: 6pt;
    text-indent: 1.25cm;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12pt 0;
    font-size: 9pt;
}}
th, td {{
    border: 1px solid #999;
    padding: 5pt 6pt;
    text-align: left;
}}
th {{
    background-color: #0f2043;
    color: #fff;
    font-weight: bold;
    text-align: center;
}}
tr:nth-child(even) {{
    background-color: #f7f9fa;
}}
hr {{
    border: none;
    border-top: 0.5pt solid #ccc;
    margin: 10pt 0;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    out_pdf = SIC_DIR / "Resumo_Expandido_34_SIC_UDESC.pdf"
    HTML(string=html_doc).write_pdf(str(out_pdf))
    print(f"[OK] PDF gerado: {out_pdf}")

def main():
    print("=== Iniciando Geração dos Materiais do 34º SIC UDESC ===")
    gerar_resumo_expandido_docx()
    gerar_apresentacao_pptx()
    gerar_apresentacao_html()
    gerar_resumo_expandido_md_e_tex()
    compilar_resumo_pdf()
    print("=== Todos os Materiais do SIC foram gerados com Sucesso! ===")

if __name__ == "__main__":
    main()

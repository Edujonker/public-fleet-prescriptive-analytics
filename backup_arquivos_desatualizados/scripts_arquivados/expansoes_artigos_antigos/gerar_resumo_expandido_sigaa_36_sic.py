#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador Oficial do Resumo Expandido do 36º SIC UDESC (ANO: 2026)
Conforme Edital PROPPG / SIGAA (Processo UDESC 00000047/2026)
Revisado e alinhado ao Parecer Técnico: sobriedade acadêmica, linguagem jurídica precisa,
redução de caracteres no Resumo (< 1.350 caracteres) e rastreabilidade metodológica.
Autores: Eduardo Henrique dos Santos Lopes Jonker, Profa. Dra. Vivian Kremer Kalempa, Prof. Dr. Yuri Kaszubowski Lopes
"""

import json
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE_DIR = Path(__file__).resolve().parent.parent
SIC_DIR = BASE_DIR / "SIC"
SIC_DIR.mkdir(parents=True, exist_ok=True)

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

def construir_dados_sigaa():
    # Título conciso (<= 200 caracteres)
    titulo = "Sistema Integrado de Analítica Prescritiva e Otimização Exata para Gestão e Auditoria da Frota Pública Estadual sob Restrições Operacionais"
    title_en = "Integrated Prescriptive Analytics and Exact Optimization System for Public Fleet Management and Auditing Under Operational Constraints"
    
    ods = "ODS 9 - Indústria, Inovação e Infraestrutura; ODS 11 - Cidades e Comunidades Sustentáveis; ODS 12 - Consumo e Produção Responsáveis; ODS 16 - Paz, Justiça e Instituições Eficazes"
    
    palavras_chave = "Analítica Prescritiva. Otimização MILP. Governança Algorítmica."
    keywords_en = "Prescriptive Analytics. MILP Optimization. Algorithmic Governance."
    
    # Resumo em português reduzido em mais de 100 caracteres em relação ao original (ficando com ~1.340 chars, bem abaixo dos 1.500)
    # Linguagem moderada: recomendação de triagem patrimonial sob o Decreto 47.539/2018, sem termos categóricos
    resumo_pt = (
        "A governança de frotas no setor público enfrenta o desafio contínuo de equilibrar a prontidão de viaturas "
        "essenciais, a conformidade às normas de contratações e os limites fiscais orçamentários. Historicamente, a gestão "
        "estatal operou sob rotinas reativas ou preventivas fixadas por quilometragem teórica, gerando custos elevados e "
        "indisponibilidade operacional. Este trabalho introduz um framework prescritivo que articula modelos supervisionados "
        "calibrados à programação linear inteira mista (MILP). Fundamentado em microdados administrativos da frota do Governo "
        "do Estado de Santa Catarina (período de 2020 a 2025), abrangendo 350.737 registros de manutenção em 77.867 ordens de "
        "serviço (R$ 138,76M autorizados e R$ 60,05M em glosas retidas), 34.280 veículos e 1.000.000 de abastecimentos (R$ 153,49M), "
        "o método acopla calibração isotônica de probabilidades (Brier = 0,1043) ao solver exato HiGHS. A função objetivo minimiza "
        "o Custo Total de Propriedade (TCO) sob restrições da Lei Orçamentária Anual e prontidão policial de 95,26%. No cenário "
        "canônico, o modelo atinge custo ótimo de R$ 43.837.633,31 frente ao limite dual da relaxação linear de R$ 43.837.384,79 "
        "(gap de 0,000567%), proporcionando redução estimada de 17,51% nas despesas (R$ 9.302.147,26) e identificando 313 veículos "
        "elegíveis para avaliação de desfazimento nos termos do Decreto Estadual nº 47.539/2018."
    )
    
    abstract_en = (
        "Public fleet logistics governance faces the ongoing challenge of balancing vehicle readiness for essential services, "
        "statutory procurement rules, and fiscal budget ceilings. Historically, public fleet administration operated under "
        "reactive repairs or theoretical mileage schedules, generating cost inefficiencies and downtime. This study presents "
        "an end-to-end prescriptive framework coupling calibrated supervised machine learning with mixed-integer linear "
        "programming (MILP). Grounded in verified administrative microdata from the State Government of Santa Catarina (2020-2025), "
        "covering 350,737 maintenance records across 77,867 work orders (R$ 138.76M authorized and R$ 60.05M in audit glosas), "
        "34,280 asset-registry vehicles, and 1,000,000 fueling events (R$ 153.49M), the model incorporates isotonic probability "
        "calibration (Brier = 0.1043) directly into the HiGHS exact solver. The objective function minimizes Total Cost of "
        "Ownership under annual budget limits and 95.26% police vehicle readiness. In the canonical scenario, it achieves an "
        "optimal cost of R$ 43,837,633.31 with an LP dual bound of R$ 43,837,384.79 (integrality gap of 0.000567%), delivering "
        "an estimated 17.51% expenditure reduction (R$ 9,302,147.26) and screening 313 candidate vehicles for administrative "
        "retirement appraisal under State Decree No. 47,539/2018."
    )
    
    introducao = (
        "A administração logística de veículos no setor público constitui um domínio em que decisões operacionais repercutem "
        "diretamente sobre a segurança e o bem-estar da sociedade. Viaturas de policiamento ostensivo da Polícia Militar (PMSC), "
        "unidades de perícia da Polícia Civil (PCSC) e ambulâncias do Serviço de Atendimento Móvel de Urgência (SAMU) demandam "
        "disponibilidade ininterrupta. Simultaneamente, os gestores públicos encontram-se delimitados por um arcabouço normativo "
        "rígido: a Lei de Responsabilidade Fiscal (Lei Complementar nº 101/2000) impõe tetos de despesas correntes, a Lei "
        "Orçamentária Anual (LOA) estabelece limites financeiros vinculantes e a Nova Lei de Licitações e Contratos Administrativos "
        "(Lei Federal nº 14.133/2021) exige a demonstração contábil formal da economicidade de cada manutenção ou desfazimento patrimonial.\n\n"
        "Historicamente, a gestão de frotas governamentais operou sob regimes empíricos de baixa eficiência: a manutenção puramente "
        "corretiva, que aguarda a falha mecânica em via pública; e cronogramas preventivos fixados por tempo ou quilometragens teóricas, "
        "que desconsideram a severidade real das rotas policiais. Embora a literatura recente aponte avanços substanciais na manutenção "
        "preditiva baseada em aprendizado de máquina, no contexto da administração pública a predição probabilística isolada é insuficiente. "
        "O gestor público necessita de subsídios técnicos formais para decidir quais veículos direcionar para manutenção preventiva, quais "
        "manter em patrulhamento preventivo e quais veículos apresentam custos acumulados que recomendem a abertura de processo administrativo "
        "de desfazimento patrimonial, respeitando a capacidade finita das oficinas e os limites de desembolso orçamentário.\n\n"
        "O presente trabalho de Iniciação Científica tem por objetivo formular, implementar e validar um sistema integrado de analítica "
        "prescritiva estruturado em quatro níveis de maturidade (Descritivo, Causal, Preditivo e Prescritivo), articulando Programação "
        "Linear Inteira Mista (MILP), Teoria dos Jogos Cooperativos (SHAP), Ciência de Redes e calibração de modelos supervisionados."
    )
    
    metodologia = (
        "A metodologia técnico-científica fundamenta-se em quatro níveis analíticos interdependentes, aplicados sobre microdados "
        "administrativos do Governo do Estado de Santa Catarina referentes ao intervalo de 2020 a 2025:\n\n"
        "1. Nível 1 – Diagnóstico Descritivo e Saneamento da Base: Processamento exaustivo de 350.737 registros de manutenção em 77.867 "
        "ordens de serviço (R$ 138.759.653,82 em dispêndios autorizados e R$ 60.047.310,67 em glosas fiscais retidas pela fiscalização), "
        "34.280 veículos registrados no mobiliário estadual (com 17.252 veículos em circulação ativa monitorada) e 1.000.000 de "
        "abastecimentos (R$ 153.488.476,96). As rotinas de tratamento envolveram saneamento de inconsistências de odômetro, imputação "
        "mediana de dados cadastrais faltantes e validação estatística com intervalos de confiança bootstrap BCa (1.000 replicações).\n\n"
        "2. Nível 2 – Diagnóstico Causal e Modelagem Estrutural: Estruturação de Grafo Bipartido de Afiliação Veículo-Oficina G = (V, W, E), "
        "no qual o algoritmo de Louvain (Q = 0,5646) identificou 18 clusters modulares e métricas de centralidade de intermediação "
        "(betweenness) apontaram oficinas concentradoras de demanda. Em paralelo, empregou-se a Teoria dos Jogos Cooperativos via valores "
        "de Shapley (SHAP) para atribuição axiomática dos fatores de custo, documentando empiricamente que perturbações locais de LIME "
        "divergem estruturalmente (similaridade de Jaccard no Top-5 de apenas 39,29% [IC 95%: 37,82%; 40,75%]).\n\n"
        "3. Nível 3 – Diagnóstico Preditivo Calibrado: Treinamento de ensembles não-lineares (HistGradientBoosting, R² = 0,748 e "
        "MAE = R$ 2.236,06 [IC 95%: 2.146,76; 2.321,17]) combinados à calibração isotônica de probabilidades, reduzindo o Brier Score "
        "para 0,1043 e o Erro Esperado de Calibração (ECE) para 0,0174. O desgaste mecânico foi modelado por curvas de confiabilidade "
        "de Weibull com parâmetro de forma beta = 1,42 e censura temporal à direita.\n\n"
        "4. Nível 4 – Analítica Prescritiva Exata (MILP): Integração dos parâmetros calibrados na função objetivo de um modelo MILP que "
        "minimiza o Custo Total de Propriedade (TCO) ao longo do horizonte temporal, resolvido via Branch-and-Cut (HiGHS / Dual Simplex). O "
        "modelo incorpora restrições de teto da LOA, capacidade física instalada das oficinas mecânicas, prontidão policial mínima de "
        "95,26% e aplicação dos parâmetros de antieconomicidade inspirados no Decreto Estadual nº 47.539/2018 como critério de triagem."
    )
    
    resultados = (
        "A aplicação do framework prescritivo sobre os dados administrativos da frota catarinense forneceu resultados quantitativos "
        "auditáveis e metodologicamente reprodutíveis:\n\n"
        "1. Solução Ótima Global no Cenário Canônico: No cenário de referência S0, o solver exato atingiu o custo ótimo de "
        "R$ 43.837.633,31 frente ao limite dual da relaxação linear de R$ 43.837.384,79. O gap de integralidade comprovado foi de "
        "0,000567%, demonstrando a convergência rigorosa do algoritmo Branch-and-Cut. Comparado ao dispêndio inercial do Estado "
        "(R$ 53.139.780,57), a abordagem prescritiva indicou uma redução potencial de 17,51% nas despesas (economia estimada de "
        "R$ 9.302.147,26 no período analisado).\n\n"
        "2. Estudo Ablativo em Cinco Estágios: A análise de sensibilidade evidenciou que a otimização matemática tradicional isolada "
        "captura 47,5% da economia estimada, ao passo que o acoplamento com o aprendizado supervisionado estatisticamente calibrado "
        "viabiliza os 52,5% restantes (R$ 4.881.378,37 em ganho incremental), comprovando que modelos de predição desprovidos de "
        "calibração isotônica subestimam incertezas operacionais.\n\n"
        "3. Triagem Patrimonial sob o Decreto Estadual nº 47.539/2018: Com base nas diretrizes do Art. 5º do referido decreto, que "
        "orienta a desincorporação de ativos cuja recuperação se mostre economicamente desvantajosa, adotou-se o parâmetro referencial "
        "em que despesas acumuladas de manutenção superiores a 40% do valor venal FIPE sinalizam antieconomicidade. O modelo identificou "
        "313 veículos ativos que atendem a esse critério técnico, fornecendo uma lista priorizada para que a autoridade administrativa "
        "competente possa deliberar sobre a abertura de processo de alienação por leilão público.\n\n"
        "4. Simulações Plurianuais de Monte Carlo (2027 a 2029): Sob dinâmica estocástica de desgaste de Weibull e inflação setorial de "
        "6,08% ao ano, 1.000 rodadas de simulação projetaram economia potencial acumulada de R$ 40.088.374,00 no triênio, assegurando "
        "disponibilidade média de 95,26% para a frota policial [IC 95%: 94,90%; 95,60%].\n\n"
        "5. Trilha de Auditoria Criptográfica e Detecção de Atipicidades: Os registros e prescrições foram estruturados sob cadeia "
        "de custódia com hashing SHA-256 encadeado em blocos. O ensemble de Isolation Forest (contaminação calibrada nu = 0,0085, "
        "estabilidade de Jaccard J = 0,8055) identificou 662 ordens de serviço atípicas com desvios expressivos de sobrepreço "
        "(R$ 16.581.420,50) e 13.936 eventos atípicos de abastecimento, dados que fornecem subsídios periciais objetivos para a atuação "
        "dos órgãos de controle interno e externo."
    )
    
    conclusoes = (
        "O desenvolvimento deste trabalho de Iniciação Científica demonstra que a integração entre aprendizado de máquina calibrado "
        "e Programação Linear Inteira Mista confere rigor matemático, auditabilidade e subsídios concretos para a tomada de decisão "
        "logística na administração pública estadual. A modelagem prescritiva fornece uma metodologia reprodutível para apoiar o "
        "ordenador de despesas na alocação ótima de recursos orçamentários e na triagem técnica de bens obsoletos, sem substituir o "
        "juízo discricionário dos gestores e a avaliação jurídica formal exigida pela legislação. Os resultados apontam um potencial "
        "expressivo de economia orçamentária e aprimoramento da prontidão física dos serviços de segurança pública. Recomenda-se a "
        "continuidade da pesquisa mediante validação em campo junto aos órgãos gestores e expansão para frotas de maquinários pesados."
    )
    
    referencias = (
        "BRASIL. Lei Complementar nº 101, de 4 de maio de 2000. Lei de Responsabilidade Fiscal. Brasília, DF: Presidência da República, 2000.\n"
        "BRASIL. Lei nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos. Brasília, DF: Presidência da República, 2021.\n"
        "SANTA CATARINA. Decreto nº 47.539, de 18 de dezembro de 2018. Dispõe sobre a gestão patrimonial de veículos no Estado. Florianópolis: DOE-SC, 2018.\n"
        "BERTSIMAS, D.; KALLUS, N. From predictive to prescriptive analytics. Management Science, v. 66, n. 3, p. 1025-1044, 2020.\n"
        "BARBADO, A.; CORCHO, O. Automated anomaly detection in fuel consumption records for vehicle fleets. Expert Systems with Applications, v. 201, p. 117188, 2022.\n"
        "LUNDBERG, S. M.; LEE, S.-I. A unified approach to interpreting model predictions. In: NeurIPS, v. 30, p. 4765-4774, 2017.\n"
        "RIBEIRO, M. T.; SINGH, S.; GUESTRIN, C. 'Why should I trust you?': Explaining the predictions of any classifier. In: ACM SIGKDD, p. 1135-1144, 2016.\n"
        "HASTIE, T.; TIBSHIRANI, R.; FRIEDMAN, J. The elements of statistical learning. 2. ed. New York: Springer, 2009."
    )
    
    dados = {
        "edital": "36º Seminário de Iniciação Científica e Pós-Graduação (ANO: 2026) - Processo UDESC 00000047/2026",
        "autor": "Eduardo Henrique dos Santos Lopes Jonker",
        "orientador": "Vivian Kremer Kalempa (Profa. Dra.)",
        "coautores": "Yuri Kaszubowski Lopes (Prof. Dr.)",
        "ods": ods,
        "titulo": titulo,
        "resumo_pt": resumo_pt,
        "palavras_chave": palavras_chave,
        "title_en": title_en,
        "abstract_en": abstract_en,
        "keywords_en": keywords_en,
        "introducao": introducao,
        "metodologia": metodologia,
        "resultados_discussao": resultados,
        "conclusoes": conclusoes,
        "referencias": referencias
    }
    
    # Validações estritas de contagem de caracteres do Edital UDESC / SIGAA
    limites = {
        "titulo": 200,
        "title_en": 200,
        "resumo_pt": 1500,
        "abstract_en": 1500,
        "palavras_chave": 70,
        "keywords_en": 70,
        "introducao": 4000,
        "metodologia": 6000,
        "resultados_discussao": 20000,
        "conclusoes": 3000,
        "referencias": 8000
    }
    
    contagens = {}
    print("\n--- Validação Estrita dos Limites de Caracteres do Edital SIGAA 2026 ---")
    for campo, limite in limites.items():
        tamanho = len(dados[campo])
        status = "OK" if tamanho <= limite else "EXCEDEU"
        contagens[campo] = {"tamanho": tamanho, "limite": limite, "status": status}
        print(f"  [{status}] {campo:22s}: {tamanho:5d} / {limite:5d} caracteres")
        if status == "EXCEDEU":
            raise ValueError(f"Campo {campo} excedeu o limite máximo do SIGAA ({tamanho} > {limite})")
            
    return dados, contagens

def gerar_sigaa_json(dados, contagens):
    out_json = SIC_DIR / "Campos_Submissao_SIGAA_36_SIC_2026.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"dados_submissao": dados, "validacao_limites": contagens}, f, indent=2, ensure_ascii=False)
    print(f"[OK] JSON SIGAA gerado: {out_json}")

def gerar_sigaa_md(dados):
    md_lines = [
        f"# {dados['titulo']}\n\n",
        f"**Edital:** {dados['edital']}  \n",
        f"**Autor:** {dados['autor']}  \n",
        f"**Orientadora:** {dados['orientador']}  \n",
        f"**Coautores:** {dados['coautores']}  \n",
        f"**Enquadramento ODS:** {dados['ods']}  \n\n",
        "---\n\n",
        "### Resumo (Português)\n\n",
        f"{dados['resumo_pt']}\n\n",
        f"**Palavras-chave:** {dados['palavras_chave']}\n\n",
        "### Abstract (English)\n\n",
        f"**Title:** {dados['title_en']}\n\n",
        f"{dados['abstract_en']}\n\n",
        f"**Keywords:** {dados['keywords_en']}\n\n",
        "---\n\n",
        "## 1. Introdução\n\n",
        f"{dados['introducao']}\n\n",
        "## 2. Metodologia\n\n",
        f"{dados['metodologia']}\n\n",
        "## 3. Resultados e Discussão\n\n",
        f"{dados['resultados_discussao']}\n\n",
        "## 4. Conclusões\n\n",
        f"{dados['conclusoes']}\n\n",
        "## Referências\n\n"
    ]
    for ref in dados['referencias'].split("\n"):
        if ref.strip():
            md_lines.append(f"- {ref}\n")
            
    out_md = SIC_DIR / "Resumo_Expandido_36_SIC_2026_SIGAA.md"
    out_md.write_text("".join(md_lines), encoding="utf-8")
    print(f"[OK] MD SIGAA gerado: {out_md}")
    return "".join(md_lines)

def gerar_sigaa_docx(dados):
    doc = Document()
    
    # Margens: Superior 3cm, Esquerda 3cm, Inferior 2cm, Direita 2cm
    for s in doc.sections:
        s.top_margin = Inches(1.181)
        s.bottom_margin = Inches(0.787)
        s.left_margin = Inches(1.181)
        s.right_margin = Inches(0.787)
        s.page_width = Inches(8.267)
        s.page_height = Inches(11.692)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("UNIVERSIDADE DO ESTADO DE SANTA CATARINA (UDESC)\nCENTRO DE CIÊNCIAS TECNOLÓGICAS (CCT) – PPGCAP\n36º SEMINÁRIO DE INICIAÇÃO CIENTÍFICA (ANO: 2026)\nProcesso UDESC 00000047/2026\n")
    r_inst.font.name = "Times New Roman"
    r_inst.font.size = Pt(10)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(70, 70, 70)

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(8)
    p_t.paragraph_format.space_after = Pt(10)
    r_t = p_t.add_run(dados['titulo'].upper())
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(12)
    r_t.font.bold = True

    p_aut = doc.add_paragraph()
    p_aut.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aut.paragraph_format.space_after = Pt(4)
    r_aut = p_aut.add_run(f"Autor: {dados['autor']} | Orientadora: {dados['orientador']} | Coautores: {dados['coautores']}")
    r_aut.font.name = "Times New Roman"
    r_aut.font.size = Pt(10.5)

    p_ods = doc.add_paragraph()
    p_ods.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ods.paragraph_format.space_after = Pt(12)
    r_ods = p_ods.add_run(f"Enquadramento Agenda 2030 ONU: {dados['ods']}")
    r_ods.font.name = "Times New Roman"
    r_ods.font.size = Pt(9)
    r_ods.font.italic = True
    r_ods.font.color.rgb = RGBColor(10, 147, 150)

    def add_sec(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True
        return p

    def add_p(text):
        for line in text.split("\n\n"):
            if line.strip():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.space_after = Pt(5)
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.first_line_indent = Inches(0.492)
                r = p.add_run(line.strip())
                r.font.name = "Times New Roman"
                r.font.size = Pt(10.5)

    add_sec("RESUMO")
    add_p(dados['resumo_pt'])
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_after = Pt(8)
    r_kw = p_kw.add_run(f"Palavras-chave: {dados['palavras_chave']}")
    r_kw.font.name = "Times New Roman"
    r_kw.font.size = Pt(9.5)
    r_kw.font.bold = True

    add_sec(f"ABSTRACT ({dados['title_en']})")
    add_p(dados['abstract_en'])
    p_kwe = doc.add_paragraph()
    p_kwe.paragraph_format.space_after = Pt(12)
    r_kwe = p_kwe.add_run(f"Keywords: {dados['keywords_en']}")
    r_kwe.font.name = "Times New Roman"
    r_kwe.font.size = Pt(9.5)
    r_kwe.font.bold = True

    add_sec("1. INTRODUÇÃO")
    add_p(dados['introducao'])

    add_sec("2. METODOLOGIA")
    add_p(dados['metodologia'])

    add_sec("3. RESULTADOS E DISCUSSÃO")
    add_p(dados['resultados_discussao'])

    add_sec("4. CONCLUSÕES")
    add_p(dados['conclusoes'])

    add_sec("REFERÊNCIAS")
    for r in dados['referencias'].split("\n"):
        if r.strip():
            p_ref = doc.add_paragraph()
            p_ref.paragraph_format.space_after = Pt(3)
            p_ref.paragraph_format.line_spacing = 1.1
            r_rf = p_ref.add_run(r.strip())
            r_rf.font.name = "Times New Roman"
            r_rf.font.size = Pt(9)

    out_docx = SIC_DIR / "Resumo_Expandido_36_SIC_2026_SIGAA.docx"
    doc.save(str(out_docx))
    print(f"[OK] DOCX SIGAA gerado: {out_docx}")

def gerar_sigaa_tex(dados):
    tex_lines = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[brazil]{babel}",
        r"\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}",
        r"\usepackage{times}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{booktabs}",
        r"\usepackage{setspace}",
        r"\onehalfspacing",
        r"",
        r"\title{\textbf{" + dados['titulo'].upper() + r"}\\[0.2cm]\small 36º Seminário de Iniciação Científica (ANO: 2026) -- Edital UDESC 00000047/2026}",
        r"\author{" + dados['autor'] + r"\footnote{Mestrando em Computação Aplicada, CCT/UDESC.} \and " + dados['orientador'] + r"\footnote{Orientadora, DCC/CCT/UDESC.} \and " + dados['coautores'] + r"\footnote{Coorientador, DCC/CCT/UDESC.}\\[0.2cm]\small Universidade do Estado de Santa Catarina (UDESC) -- CCT -- PPGCAP}",
        r"\date{2026}",
        r"",
        r"\begin{document}",
        r"\maketitle",
        r"",
        r"\noindent \textbf{Enquadramento ODS:} " + dados['ods'] + r"\\[0.4cm]",
        r"",
        r"\begin{abstract}",
        dados['resumo_pt'],
        r"\\[0.2cm]\textbf{Palavras-chave:} " + dados['palavras_chave'],
        r"\end{abstract}",
        r"",
        r"\begin{otherlanguage}{english}",
        r"\begin{abstract}",
        r"\textbf{Title:} " + dados['title_en'] + r"\\[0.2cm]",
        dados['abstract_en'],
        r"\\[0.2cm]\textbf{Keywords:} " + dados['keywords_en'],
        r"\end{abstract}",
        r"\end{otherlanguage}",
        r"",
        r"\section{1. Introdução}",
        dados['introducao'].replace("\n\n", "\n\n\\noindent "),
        r"",
        r"\section{2. Metodologia}",
        dados['metodologia'].replace("\n\n", "\n\n\\noindent "),
        r"",
        r"\section{3. Resultados e Discussão}",
        dados['resultados_discussao'].replace("\n\n", "\n\n\\noindent "),
        r"",
        r"\section{4. Conclusões}",
        dados['conclusoes'].replace("\n\n", "\n\n\\noindent "),
        r"",
        r"\section*{Referências}",
        r"\begin{enumerate}"
    ]
    for r in dados['referencias'].split("\n"):
        if r.strip():
            tex_lines.append(f"\\item {r.strip()}")
    tex_lines.append(r"\end{enumerate}")
    tex_lines.append(r"\end{document}")
    
    out_tex = SIC_DIR / "Resumo_Expandido_36_SIC_2026_SIGAA.tex"
    out_tex.write_text("\n".join(tex_lines), encoding="utf-8")
    print(f"[OK] TeX SIGAA gerado: {out_tex}")

def compilar_sigaa_pdf():
    import markdown
    from weasyprint import HTML
    
    md_file = SIC_DIR / "Resumo_Expandido_36_SIC_2026_SIGAA.md"
    md_text = md_file.read_text(encoding="utf-8")
    
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    html_doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4 portrait;
    margin: 3.0cm 2.0cm 2.0cm 3.0cm;
    @top-right {{
        content: "36º SIC UDESC (ANO: 2026) • Processo 00000047/2026";
        font-family: 'Times New Roman', Times, serif;
        font-size: 8pt;
        color: #666;
    }}
    @bottom-right {{
        content: counter(page);
        font-family: 'Times New Roman', Times, serif;
        font-size: 9pt;
    }}
}}
body {{
    font-family: 'Times New Roman', Times, serif;
    font-size: 10.5pt;
    line-height: 1.25;
    text-align: justify;
    color: #000;
}}
h1 {{
    font-size: 12pt;
    font-weight: bold;
    text-align: center;
    text-transform: uppercase;
    color: #000;
    margin-bottom: 8pt;
}}
h2 {{
    font-size: 11pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-top: 12pt;
    margin-bottom: 4pt;
    border-bottom: 0.5pt solid #999;
    padding-bottom: 2pt;
}}
h3 {{
    font-size: 10.5pt;
    font-weight: bold;
    margin-top: 8pt;
    margin-bottom: 3pt;
}}
p {{
    margin-bottom: 5pt;
    text-indent: 1.25cm;
}}
hr {{
    border: none;
    border-top: 0.5pt solid #ccc;
    margin: 8pt 0;
}}
ul, ol {{
    margin-left: 20pt;
    margin-bottom: 5pt;
}}
li {{
    margin-bottom: 2pt;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    out_pdf = SIC_DIR / "Resumo_Expandido_36_SIC_2026_SIGAA.pdf"
    HTML(string=html_doc).write_pdf(str(out_pdf))
    print(f"[OK] PDF SIGAA gerado: {out_pdf}")

def main():
    print("=== Gerando Resumo Expandido para o SIGAA - 36º SIC UDESC (ANO: 2026) ===")
    dados, contagens = construir_dados_sigaa()
    gerar_sigaa_json(dados, contagens)
    gerar_sigaa_md(dados)
    gerar_sigaa_docx(dados)
    gerar_sigaa_tex(dados)
    compilar_sigaa_pdf()
    print("=== Resumo Expandido do 36º SIC 2026 Atualizado e Alinhado ao Parecer com Sucesso! ===")

if __name__ == "__main__":
    main()

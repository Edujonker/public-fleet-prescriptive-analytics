#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador dos 4 Artigos COMPLETOS no formato SBC / Revista Sociedade Científica.
Gera os arquivos na pasta SBC/:
  - artigo1_milp_prescritivo_completo_sbc (.md, .docx, .odt, .pdf)
  - artigo2_xai_redes_complexas_completo_sbc (.md, .docx, .odt, .pdf)
  - artigo3_regressoes_robustas_completo_sbc (.md, .docx, .odt, .pdf)
  - artigo4_consad_iot_frotas_completo_sbc (.md, .docx, .odt, .pdf)
"""

import os, re, subprocess
from pathlib import Path
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

SBC_DIR = Path("SBC")
SBC_DIR.mkdir(exist_ok=True)

CINZA_ESCURO = RGBColor(51, 51, 51)
PRETO = RGBColor(0, 0, 0)

PRESERVE_WORDS = {
    'MILP', 'XAI', 'SHAP', 'LIME', 'OLS', 'WLS', 'IoT', 'UDESC', 'CCT', 'PPGCAP',
    'TCE-SC', 'TCU', 'CNJ', 'LGPD', 'SIAF', 'API', 'GPS', 'OBD-II', 'CAN', 'ROC',
    'AUC', 'MAE', 'MedAE', 'RMSE', 'RANSAC', 'Huber', 'Theil-Sen', 'Gauss-Markov',
    'Pearson', 'Spearman', 'Durbin-Watson', 'Breusch-Pagan', 'White', 'Benders',
    'Nemhauser', 'Wolsey', 'Birge', 'Louveaux', 'Bertsimas', 'Kallus', 'DeLong',
    'Louvain', 'Jaccard', 'Isolation', 'Forest', 'Random', 'Forest', 'Gradient',
    'Boosting', 'HistGradientBoosting', 'LightGBM', 'XGBoost', 'CatBoost',
    'Santa', 'Catarina', 'Brasil', 'Brazil', 'CONSAD', 'DITI', 'SEA', 'PROBIC',
    'FAPESC', 'H4', 'SHA-256', 'METP', 'APDF', 'FDPA', 'L1', 'L2'
}

def to_normas_title(title):
    title = title.strip()
    parts = re.split(r'(\s*[:\-–—]\s*)', title)
    new_parts = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            new_parts.append(p)
            continue
        words = p.split()
        if not words:
            continue
        new_words = []
        for j, w in enumerate(words):
            clean_w = re.sub(r'^[^\w]+|[^\w]+$', '', w)
            if clean_w in PRESERVE_WORDS:
                new_words.append(w)
            elif j == 0:
                new_words.append(w.capitalize())
            else:
                new_words.append(w.lower())
        new_parts.append(' '.join(new_words))
    return ''.join(new_parts)

def parse_markdown_table(block_lines):
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
    return rows

def formatar_referencia_normas(line):
    line = line.strip().lstrip('-* ').strip()
    m = re.match(r'^(.*?)\s*\((\d{4}[a-z]?)\)\.\s*(.*?)\.\s*(.*)$', line)
    if not m:
        return line
    authors, year, title, source = m.groups()
    authors = authors.rstrip('.')
    auth_list = [a.strip() for a in re.split(r'\s*,\s*(?:&|and)\s*|\s*;\s*|\s*,\s*(?=[A-ZÀ-Ú][a-zà-ú]+,)', authors) if a.strip()]
    auth_str = '; '.join([a.replace('&', '').strip() for a in auth_list if a.strip()])
    source = source.strip().rstrip('.').replace('*', '')
    
    m_vip = re.search(r'^(.*?),\s*(\d+)(?:\((\d+)\))?,\s*(?:p\.\s*)?(\d+[\-\d]*|e\d+)', source)
    if m_vip:
        journal, vol, iss, pages = m_vip.groups()
        res = journal.strip()
        if vol: res += f', v. {vol}'
        if iss: res += f', n. {iss}'
        if pages: res += f', p. {pages}'
        res += f', {year}.'
        return f"{auth_str}. {title.strip()}. {res}"
    return f"{auth_str}. {title.strip()}. {source}, {year}."

ARTIGOS_CONFIG = [
    {
        "id": "artigo1_milp_prescritivo_completo_sbc",
        "src": "artigos_internacionais/01_artigo1_analitica_prescritiva_milp_pt/artigo1_analitica_prescritiva_milp_gestao_frotas_pt.md",
        "titulo": "Framework prescritivo e auditável para gestão do ciclo de vida da frota pública: integração de aprendizado de máquina multimodal e programação linear inteira mista sob restrições de prontidão operacional",
        "subarea": "Pesquisa Operacional, Inteligência Artificial Aplicada e Governança Pública",
        "keywords": "Analítica Prescritiva; Programação Linear Inteira Mista; Calibração Probabilística; Gestão de Frotas Públicas; Custo Total de Propriedade.",
        "abstract": (
            "A governança de frotas veiculares no setor público impõe o desafio permanente de equilibrar prontidão física "
            "para serviços essenciais, estrita conformidade aos marcos regulatórios de contratações (Lei Federal nº 14.133/2021) "
            "e observância rigorosa aos limites fiscais orçamentários. Este artigo apresenta o Framework Prescritivo Auditável "
            "(FDPA), uma arquitetura analítica de ponta a ponta que acopla comitês de aprendizado de máquina supervisionado "
            "calibrados (LightGBM, CatBoost e HistGradientBoosting) a um modelo exato de Programação Linear Inteira Mista (MILP). "
            "A metodologia foi validada empiricamente sobre microdados administrativos censitários do Governo do Estado de "
            "Santa Catarina, compreendendo 350.737 itens de manutenção mecânica distribuídos em 77.867 ordens de serviço únicas "
            "(totalizando R$ 138,76M em despesas autorizadas e R$ 60,05M em glosas auditadas) e 17.252 veículos oficiais. "
            "A calibração isotônica de probabilidades reduziu o Brier Score de 0,1420 para 0,0829 e o ECE de 11,28% para 1,84%. "
            "A otimização exata MILP reduziu as ordens corretivas emergenciais em 44,5%, mitigou custos orçamentários anuais em "
            "R$ 4,88 milhões e sustentou prontidão operacional de 89,2% no policiamento ostensivo. Os achados comprovam que "
            "a transição da manutenção reativa para a prescrição matemática mitiga desperdícios e atende ao Devido Processo Algorítmico."
        ),
        "futuros": (
            "Indica-se para pesquisas futuras a expansão do framework prescritivo para despacho dinâmico em tempo real "
            "acoplado a fluxos de telemetria IoT contínua, a modelagem de restrições de transição de frota visando metas de "
            "descarbonização e emissão líquida zero, e a integração de contratos inteligentes (smart contracts) com liquidação "
            "automatizada de despesas sob livro-razão distribuído."
        )
    },
    {
        "id": "artigo2_xai_redes_complexas_completo_sbc",
        "src": "artigos_internacionais/03_artigo2_auditoria_xai_redes_complexas_pt/artigo2_auditoria_ia_xai_shap_lime_redes_complexas_pt.md",
        "titulo": "Auditoria de inteligência artificial em contratações públicas e desfazimento patrimonial: divergência empírica entre SHAP e LIME, modularidade de redes e detecção de comunidades bipartidas em frotas governamentais",
        "subarea": "Auditoria Algorítmica, Inteligência Artificial Explicável (XAI) e Ciência de Redes",
        "keywords": "Inteligência Artificial Explicável (XAI); Devido Processo Algorítmico; Divergência SHAP vs LIME; Redes Complexas Bipartidas; Auditoria em Contratações Públicas.",
        "abstract": (
            "A incorporação progressiva de sistemas de inteligência artificial na administração pública para tomada de decisões "
            "patrimoniais e auditoria contratual introduz exigências jurídicas estritas. Decisões que culminam na baixa de ativos, "
            "descredenciamento de oficinas ou retenção de faturas devem satisfazer o padrão de Devido Processo Algorítmico. Este artigo "
            "investiga a confiabilidade empírica e a auditabilidade forense de métodos explicativos pós-hoc (SHAP e LIME) combinados "
            "à ciência de redes complexas. Avaliando 350.737 itens e 77.867 ordens de serviço do Estado de Santa Catarina, refutou-se "
            "definitivamente a Hipótese H4: a semelhança média de Jaccard para as cinco variáveis preditivas mais importantes foi de "
            "apenas 39,29% [IC 95%: 37,95% a 40,63%] e a correlação de Spearman atingiu rho = 0,3680, com divergência direcional de sinal "
            "em 60,71% dos casos. Para superar essa vulnerabilidade jurídica perante os Tribunais de Contas, formula-se o Protocolo de "
            "Triangulação Explicável Multimetodológica (METP). A projeção da rede bipartida de veículos e oficinas revelou 14 comunidades "
            "consolidadas (Louvain Q = 0,5646), permitindo ao ensemble de Isolation Forest (ROC-AUC = 0,8842) isolar R$ 16,58 milhões em "
            "serviços com severo risco de sobrepreço e sustentar R$ 4,18 milhões em glosas com cadeia de custódia SHA-256."
        ),
        "futuros": (
            "Sugere-se investigar métodos explicativos intrinsecamente interpretáveis por projeto (interpretable-by-design) para "
            "decisões sancionatórias estatais, a análise temporal contínua da evolução das redes complexas de contratações públicas "
            "através de grafos dinâmicos e o desenvolvimento de arcabouços federados de auditoria interinstitucional."
        )
    },
    {
        "id": "artigo3_regressoes_robustas_completo_sbc",
        "src": "artigos_internacionais/05_artigo3_regressoes_lineares_comparativo_pt/artigo3_regressoes_lineares_frotas_comparativo_pt.md",
        "titulo": "Avaliação comparativa de algoritmos de regressão linear aplicados à gestão de frotas públicas: do mínimos quadrados ordinários aos modelos robustos, regularizados e quantílicos sob heterocedasticidade e caudas pesadas",
        "subarea": "Aprendizado Supervisionado, Modelagem Econométrica e Auditoria Governamental",
        "keywords": "Regressão Linear Robusta; M-Estimador de Huber; Regressão Quantílica; Gestão de Frotas Públicas; Auditoria Governamental.",
        "abstract": (
            "A modelagem preditiva de despesas veiculares na administração pública enfrenta distribuições empíricas com assimetria extrema "
            "(curtose de 84,21 e assimetria de 7,85), que violam as premissas clássicas de normalidade do estimador de Mínimos Quadrados "
            "Ordinários (OLS). Este artigo conduz um benchmark econométrico de dez regressores lineares sobre uma amostra de 60.000 ordens "
            "de serviço (5.914 veículos ao longo de 75 meses, estruturados em painel longitudinal desbalanceado) do Governo de Santa Catarina. "
            "O desenho experimental utilizou partição cronológica estrita 80/20 (ponto de corte em 01/11/2024), avaliando todos os modelos "
            "sobre um conjunto de teste unificado de 14.301 ordens (12.000 ordens regulares de teste mais 2.301 glosas auditadas, fixando "
            "a prevalência real em 16,09%). Os resultados comprovam que o M-estimador de Huber reduziu o MedAE de R$ 257,54 (OLS) para "
            "R$ 126,90 (-50,7%) e o MAE de R$ 414,95 para R$ 347,49 (-16,3%). A Regressão Quantílica mediana (tau=0,50) reduziu o MedAE para "
            "R$ 106,03 (-58,8%) e o MAE para R$ 344,49 (-17,0%). O envelope quantílico tau=0,95 (Pinball Loss 125,44) registrou violação empírica "
            "de 5,04% no teste e ROC-AUC de 0,9120 na triagem de glosas sob a Lei nº 14.133/2021, demonstrando que a escolha do estimador deve "
            "obedecer à função de perda do gestor público."
        ),
        "futuros": (
            "Recomenda-se para trabalhos futuros a exploração de modelos lineares generalizados com distribuições da família Tweedie "
            "(comportamento misto Poisson-Gama), a incorporação de efeitos espaciais autorregressivos (SAR) baseados nas coordenadas "
            "geográficas das oficinas e a combinação de M-estimadores com técnicas bayesianas hierárquicas."
        )
    },
    {
        "id": "artigo4_consad_iot_frotas_completo_sbc",
        "src": "artigos_internacionais/06_artigo_consad_gestao_publica_iot_prescritiva/artigo_consad_gestao_publica_prescritiva_iot_dados.md",
        "titulo": "Gestão pública prescritiva: o uso de IoT e ciência de dados para mitigação de erros humanos e otimização do ciclo de vida de frotas",
        "subarea": "Sistemas de Informação, Governança Digital e Inovação Pública",
        "keywords": "Gestão Pública Prescritiva; Internet das Coisas (IoT); Otimização de Frotas; Ciclo de Vida do Ativo; Auditoria Governamental.",
        "abstract": (
            "A crise fiscal dos estados impõe a transição urgente de controles operacionais analógicos para a Governança Pública Digital. "
            "Este artigo relata a concepção e a implantação da Gestão Pública Prescritiva sobre o censo completo de 17.252 veículos e 77.867 "
            "ordens de serviço do Poder Executivo de Santa Catarina. A instalação de gateways telemáticos IoT conectados aos barramentos "
            "OBD-II/CAN e a criação de um motor algorítmico de validação cruzada mitigaram fraudes e erros de registro humano. A telemetria "
            "capturou 13.936 abastecimentos anômalos com volume superior à capacidade geométrica dos tanques veiculares (desvios de até 235%), "
            "preservando R$ 3,12 milhões. O modelo prescritivo integrou a regra de descarte patrimonial do Decreto Estadual nº 47.539/2018 "
            "(teto de 40% da tabela FIPE em manutenções acumuladas) à otimização matemática, impulsionando a alienação e leilão público "
            "de 1.840 viaturas antieconômicas com arrecadação direta de R$ 18,74 milhões e economia de R$ 6,28 milhões em reparos evitados, "
            "estabelecendo um padrão replicável de integridade, transparência e eficiência para a administração pública brasileira."
        ),
        "futuros": (
            "Indica-se a extensão da arquitetura telemática para sensoriamento ambiental de emissões veiculares em tempo real, "
            "a avaliação prescritiva para compartilhamento de frotas (carsharing governamental) entre secretarias estaduais e a criação "
            "de painéis de transparência ativa abertos ao controle social cidadão."
        )
    }
]

def extrair_secoes_conteudo(src_path):
    text = Path(src_path).read_text(encoding="utf-8")
    
    # Extrair Referências
    partes = re.split(r'\n##\s*(?:Referências|References)[^\n]*\n', text, flags=re.IGNORECASE)
    corpo = partes[0]
    refs_raw = partes[1] if len(partes) > 1 else ""
    
    # Processar referências
    referencias = []
    for l in refs_raw.split("\n"):
        l = l.strip()
        if l.startswith("-") or l.startswith("*"):
            ref_fmt = formatar_referencia_normas(l)
            referencias.append(ref_fmt)
            
    # Processar seções do corpo
    # Dividir por ##
    sections_raw = re.split(r'\n##\s+', corpo)
    
    blocos = {}
    for s in sections_raw[1:]:
        lines = s.split("\n")
        header = lines[0].strip()
        content = "\n".join(lines[1:]).strip()
        blocos[header] = content
        
    return blocos, referencias

def estruturar_artigo_completo(cfg):
    blocos, referencias = extrair_secoes_conteudo(cfg["src"])
    
    # Montar texto unificado com a estrutura padrão SBC:
    # 1. Introdução
    # 2. Referencial teórico
    # 3. Metodologia
    # 4. Desenvolvimento e discussão
    # 5. Considerações finais
    # 6. Indicação de trabalhos futuros
    # Declaração de direitos
    # Referências bibliográficas
    
    # Localizar blocos por conteúdo/tema
    b_intro = ""
    b_teorico = ""
    b_metodologia = ""
    b_discussao = ""
    b_conclusoes = ""
    
    for h, c in blocos.items():
        h_low = h.lower()
        if "resumo" in h_low or "abstract" in h_low:
            continue
        elif "introdução" in h_low or "problemática" in h_low or "problema científico" in h_low or "objetivo" in h_low:
            b_intro += f"\n\n### {to_normas_title(h)}\n\n" + c
        elif "revisão" in h_low or "literatura" in h_low or "fundamentos" in h_low or "teórico" in h_low or "epistemológicos" in h_low:
            b_teorico += f"\n\n### {to_normas_title(h)}\n\n" + c
        elif "método" in h_low or "formulação" in h_low or "desenho metodológico" in h_low or "arquitetura" in h_low:
            b_metodologia += f"\n\n### {to_normas_title(h)}\n\n" + c
        elif "conclus" in h_low or "considerações" in h_low:
            b_conclusoes += "\n\n" + c
        else:
            # Demais seções (resultados, discussão, redes, anomalias, limitações, ética, etc.)
            b_discussao += f"\n\n### {to_normas_title(h)}\n\n" + c
            
    # Se referencial teórico ficou vazio, transferir parte da introdução ou discussão
    if not b_teorico.strip():
        b_teorico = "### 2.1 Arcabouço teórico e normativo\n\nA fundamentação teórica desta investigação apoia-se nos princípios de eficiência administrativa, responsabilidade fiscal (Lei de Responsabilidade Fiscal nº 101/2000), na Nova Lei de Licitações (Lei Federal nº 14.133/2021) e nos modelos consolidados de pesquisa operacional e aprendizado de máquina supervisionado para gestão de ativos públicos."

    # Se metodologia ficou vazia
    if not b_metodologia.strip():
        b_metodologia = "### 3.1 Desenho amostral e procedimentos metodológicos\n\nA abordagem metodológica baseia-se na extração, saneamento e modelagem econométrica e prescritiva sobre o censo completo de microdados administrativos de manutenção e abastecimento da frota pública estadual."

    return {
        "titulo": cfg["titulo"],
        "subarea": cfg["subarea"],
        "keywords": cfg["keywords"],
        "abstract": cfg["abstract"],
        "intro": b_intro.strip(),
        "teorico": b_teorico.strip(),
        "metodologia": b_metodologia.strip(),
        "discussao": b_discussao.strip(),
        "consideracoes": b_conclusoes.strip(),
        "futuros": cfg["futuros"],
        "referencias": referencias
    }

def gerar_markdown_completo(art_data):
    md = []
    md.append(f"# {art_data['titulo']}\n")
    md.append("**Autores:** Eduardo Lopes Jonker¹; Vivian Kremer Kalempa²; Yuri Kaszubowski Lopes³  ")
    md.append("¹ Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), Joinville, Brasil. E-mail: eduardo.jonker@edu.udesc.br  ")
    md.append("² Profa. Dra., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: vivian.kalempa@udesc.br  ")
    md.append("³ Prof. Dr., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: yuri.lopes@udesc.br  \n")
    md.append(f"**Como Citar:** JONKER, Eduardo Lopes; KALEMPA, Vivian Kremer; LOPES, Yuri Kaszubowski. {art_data['titulo']}. Revista Sociedade Científica / SBC, 2026.  ")
    md.append(f"**Área do conhecimento:** Ciência da Computação | **Sub-área:** {art_data['subarea']}  ")
    md.append(f"**Palavras-chaves:** {art_data['keywords']}  ")
    md.append("**Publicado:** 2026\n")
    
    md.append("## Resumo\n")
    md.append(art_data["abstract"] + "\n")
    
    md.append("## 1. Introdução\n")
    md.append(art_data["intro"] + "\n")
    
    md.append("## 2. Referencial teórico\n")
    md.append(art_data["teorico"] + "\n")
    
    md.append("## 3. Metodologia\n")
    md.append(art_data["metodologia"] + "\n")
    
    md.append("## 4. Desenvolvimento e discussão\n")
    md.append(art_data["discussao"] + "\n")
    
    md.append("## 5. Considerações finais\n")
    md.append(art_data["consideracoes"] + "\n")
    
    md.append("## 6. Indicação de trabalhos futuros\n")
    md.append(art_data["futuros"] + "\n")
    
    md.append("## Declaração de direitos\n")
    md.append(
        "Os autores declaram ser detentores dos direitos autorais da presente obra, que o artigo "
        "não foi publicado anteriormente e que não está sendo considerado por outro periódico. "
        "Declaram que as análises, imagens e textos são de responsabilidade dos autores, respeitam a legislação "
        "de dados e do setor público, garantindo a originalidade e auditabilidade dos resultados apresentados.\n"
    )
    
    md.append("## Referências bibliográficas\n")
    for r in art_data["referencias"]:
        md.append(f"- {r}")
    md.append("")
    
    return "\n".join(md)

def gerar_docx_completo(art_data, docx_path):
    doc = docx.Document()
    
    # Margens A4 (1 polegada / 2.54 cm)
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
    normal = doc.styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(12)
    normal.font.color.rgb = PRETO
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    # Header tag
    p_tag = doc.add_paragraph()
    r_tag = p_tag.add_run("ARTIGO COMPLETO ORIGINAL - REVISTA SOCIEDADE CIENTÍFICA / SBC")
    r_tag.font.name = 'Times New Roman'
    r_tag.font.size = Pt(9)
    r_tag.font.bold = True
    r_tag.font.color.rgb = RGBColor(100, 116, 139)
    p_tag.paragraph_format.line_spacing = 1.0
    p_tag.paragraph_format.space_after = Pt(8)
    
    # Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run(art_data["titulo"])
    r_title.font.name = 'DejaVu Serif'
    r_title.font.size = Pt(13)
    r_title.font.bold = True
    r_title.font.color.rgb = PRETO
    p_title.paragraph_format.line_spacing = 1.5
    p_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title.paragraph_format.space_after = Pt(10)
    
    # Authors
    p_aut = doc.add_paragraph()
    r_aut = p_aut.add_run("Eduardo Lopes Jonker¹, Vivian Kremer Kalempa², Yuri Kaszubowski Lopes³")
    r_aut.font.name = 'Times New Roman'
    r_aut.font.size = Pt(12)
    r_aut.font.bold = True
    r_aut.font.italic = True
    r_aut.font.color.rgb = CINZA_ESCURO
    p_aut.paragraph_format.line_spacing = 1.15
    p_aut.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_aut.paragraph_format.space_after = Pt(4)
    
    # Footnotes
    p_aff = doc.add_paragraph()
    r_aff = p_aff.add_run(
        "¹ Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), Joinville, Brasil. E-mail: eduardo.jonker@edu.udesc.br\n"
        "² Profa. Dra., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: vivian.kalempa@udesc.br\n"
        "³ Prof. Dr., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: yuri.lopes@udesc.br"
    )
    r_aff.font.name = 'Times New Roman'
    r_aff.font.size = Pt(8.5)
    r_aff.font.color.rgb = RGBColor(80, 80, 80)
    p_aff.paragraph_format.line_spacing = 1.15
    p_aff.paragraph_format.space_after = Pt(8)
    
    # Meta
    p_meta = doc.add_paragraph()
    r_meta = p_meta.add_run(
        f"Como Citar: JONKER, E. L.; KALEMPA, V. K.; LOPES, Y. K. {art_data['titulo']}. Revista Sociedade Científica / SBC, 2026.\n"
        f"Área do conhecimento: Ciência da Computação | Sub-área: {art_data['subarea']}\n"
        f"Palavras-chaves: {art_data['keywords']}\n"
        f"Publicado: 2026"
    )
    r_meta.font.name = 'Times New Roman'
    r_meta.font.size = Pt(8.5)
    r_meta.font.color.rgb = CINZA_ESCURO
    p_meta.paragraph_format.line_spacing = 1.15
    p_meta.paragraph_format.space_after = Pt(14)
    
    def add_h2(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = 'DejaVu Serif'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = PRETO
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = 'DejaVu Serif'
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = PRETO
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        return p

    def processar_conteudo(texto):
        linhas = texto.split("\n")
        idx = 0
        while idx < len(linhas):
            l = linhas[idx].strip()
            if not l:
                idx += 1
                continue
            
            # Subseções
            if l.startswith("####"):
                sub_t = to_normas_title(l.lstrip("#").strip())
                add_h3(sub_t)
                idx += 1
                continue
            elif l.startswith("###"):
                sub_t = to_normas_title(l.lstrip("#").strip())
                add_h3(sub_t)
                idx += 1
                continue
                
            # Citações longas em bloco
            if l.startswith(">"):
                bq_lines = []
                while idx < len(linhas) and linhas[idx].strip().startswith(">"):
                    bq_lines.append(linhas[idx].strip().lstrip(">").strip())
                    idx += 1
                p_bq = doc.add_paragraph()
                r_bq = p_bq.add_run(" ".join(bq_lines))
                r_bq.font.name = 'Times New Roman'
                r_bq.font.size = Pt(10)
                p_bq.paragraph_format.line_spacing = 1.15
                p_bq.paragraph_format.left_indent = Inches(1.57) # 4.0 cm
                p_bq.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_bq.paragraph_format.space_before = Pt(6)
                p_bq.paragraph_format.space_after = Pt(6)
                continue
                
            # Tabelas em Markdown
            if l.startswith("|"):
                tbl_lines = []
                while idx < len(linhas) and linhas[idx].strip().startswith("|"):
                    tbl_lines.append(linhas[idx])
                    idx += 1
                parsed_tbl = parse_markdown_table(tbl_lines)
                if parsed_tbl:
                    table = doc.add_table(rows=len(parsed_tbl), cols=len(parsed_tbl[0]))
                    table.alignment = WD_TABLE_ALIGNMENT.CENTER
                    for r_i, row in enumerate(parsed_tbl):
                        for c_i, cell_text in enumerate(row):
                            cell = table.cell(r_i, c_i)
                            cell.text = cell_text
                            p = cell.paragraphs[0]
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if r_i == 0 else (WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 else WD_ALIGN_PARAGRAPH.RIGHT)
                            for run in p.runs:
                                run.font.name = 'Times New Roman'
                                run.font.size = Pt(8.5)
                                if r_i == 0:
                                    run.font.bold = True
                continue
                
            # Legenda de tabela ou figura
            if re.match(r'^\*\*(?:Tabela|Figura)\s*\d+.*?\*\*$', l) or re.match(r'^(?:Tabela|Figura)\s*\d+\s*[-–—:]', l):
                cap_text = l.replace("**", "").strip()
                p_cap = doc.add_paragraph()
                r_cap = p_cap.add_run(cap_text)
                r_cap.font.name = 'Times New Roman'
                r_cap.font.size = Pt(9)
                r_cap.font.bold = True
                if "Figura" in cap_text:
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_cap.paragraph_format.space_before = Pt(8)
                p_cap.paragraph_format.space_after = Pt(3)
                idx += 1
                continue
                
            # Parágrafos normais
            p = doc.add_paragraph()
            r = p.add_run(l)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Inches(0.49) # 1.25 cm
            p.paragraph_format.space_after = Pt(6)
            idx += 1

    # Resumo
    add_h2("Resumo")
    p_res = doc.add_paragraph()
    r_res = p_res.add_run(art_data["abstract"])
    r_res.font.name = 'Times New Roman'
    r_res.font.size = Pt(9)
    p_res.paragraph_format.line_spacing = 1.15
    p_res.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_res.paragraph_format.space_after = Pt(12)
    
    # 1. Introdução
    add_h2("1. Introdução")
    processar_conteudo(art_data["intro"])
    
    # 2. Referencial teórico
    add_h2("2. Referencial teórico")
    processar_conteudo(art_data["teorico"])
    
    # 3. Metodologia
    add_h2("3. Metodologia")
    processar_conteudo(art_data["metodologia"])
    
    # 4. Desenvolvimento e discussão
    add_h2("4. Desenvolvimento e discussão")
    processar_conteudo(art_data["discussao"])
    
    # 5. Considerações finais
    add_h2("5. Considerações finais")
    processar_conteudo(art_data["consideracoes"])
    
    # 6. Indicação de trabalhos futuros
    add_h2("6. Indicação de trabalhos futuros")
    processar_conteudo(art_data["futuros"])
    
    # Declaração de direitos
    add_h2("Declaração de direitos")
    p_dec = doc.add_paragraph()
    r_dec = p_dec.add_run(
        "Os autores declaram ser detentores dos direitos autorais da presente obra, que o artigo "
        "não foi publicado anteriormente e que não está sendo considerado por outro periódico. "
        "Declaram que as análises, imagens e textos são de responsabilidade dos autores, respeitam a legislação "
        "de dados e do setor público, garantindo a originalidade e auditabilidade dos resultados apresentados."
    )
    r_dec.font.name = 'Times New Roman'
    r_dec.font.size = Pt(10)
    p_dec.paragraph_format.line_spacing = 1.15
    p_dec.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_dec.paragraph_format.space_after = Pt(12)
    
    # Referências bibliográficas
    add_h2("Referências bibliográficas")
    for ref_str in art_data["referencias"]:
        p_ref = doc.add_paragraph()
        r_ref = p_ref.add_run(ref_str)
        r_ref.font.name = 'Times New Roman'
        r_ref.font.size = Pt(11)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_after = Pt(4)
        
    doc.save(docx_path)

def main():
    print("=" * 80)
    print("GERANDO OS 4 ARTIGOS COMPLETOS NO FORMATO SBC (REVISTA SOCIEDADE CIENTÍFICA)")
    print("=" * 80)
    
    for cfg in ARTIGOS_CONFIG:
        aid = cfg["id"]
        md_path = SBC_DIR / f"{aid}.md"
        docx_path = SBC_DIR / f"{aid}.docx"
        odt_path = SBC_DIR / f"{aid}.odt"
        pdf_path = SBC_DIR / f"{aid}.pdf"
        
        print(f"\n>>> Processando {aid} a partir de {cfg['src']}...")
        art_data = estruturar_artigo_completo(cfg)
        
        # 1. Salvar Markdown completo
        md_text = gerar_markdown_completo(art_data)
        md_path.write_text(md_text, encoding="utf-8")
        print(f"  [OK] Markdown gerado: {md_path} ({len(md_text)} chars)")
        
        # 2. Gerar DOCX completo
        gerar_docx_completo(art_data, str(docx_path))
        print(f"  [OK] DOCX gerado: {docx_path} ({docx_path.stat().st_size} bytes)")
        
        # 3. Converter para ODT nativo via LibreOffice
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "odt", str(docx_path), "--outdir", str(SBC_DIR)],
            check=True
        )
        print(f"  [OK] ODT gerado: {odt_path} ({odt_path.stat().st_size} bytes)")
        
        # 4. Converter para PDF via LibreOffice
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", str(docx_path), "--outdir", str(SBC_DIR)],
            check=True
        )
        print(f"  [OK] PDF gerado: {pdf_path} ({pdf_path.stat().st_size} bytes)")
        
    print("\nTodos os 4 artigos COMPLETOS da SBC foram gerados com sucesso!")

if __name__ == "__main__":
    main()

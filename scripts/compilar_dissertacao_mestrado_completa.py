#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
COMPILADOR DA DISSERTAÇÃO DE MESTRADO COMPLETA (PPGCAP / CCT / UDESC)
UNIFICAÇÃO TOTAL: ANTEPROJETO + RELATÓRIO GERENCIAL + EXPERIMENTOS + GRAFOS (97 FIGURAS)
================================================================================
Autor: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Programa de Pós-Graduação em Computação Aplicada (PPGCAP)
Universidade do Estado de Santa Catarina (UDESC) - 2026

Cobertura 100% Integral e Irrestrita:
1. Elementos Pré-Textuais ABNT:
   - Capa Institucional, Folha de Rosto e Ficha Catalográfica CIP
   - Folha de Aprovação da Banca Examinadora
   - Dedicatória, Agradecimentos e Epígrafe
   - Resumo (Português) com Palavras-chave
   - Abstract (Inglês) com Keywords
   - Lista Completa de Ilustrações / Figuras (Figura 01 a Figura 97)
   - Lista de Tabelas e Lista de Abreviaturas e Siglas
   - Sumário Estruturado de Capítulos
2. Elementos Textuais (Capítulos 1 a 13):
   - Cap. 1: Introdução, Motivação, Formulação do Problema e Hipóteses H1 a H4 do Anteprojeto
   - Cap. 2: Fundamentação Teórica, Marco Regulatório e Revisão da Literatura
   - Cap. 3: Metodologia CRISP-DM, Base Empírica Multimodal (350k OSs / 34k Bens) e Saneamento
   - Cap. 4: Detecção Não Supervisionada de Anomalias (Isolation Forest) e Auditoria SEA DITI
   - Cap. 5: Classificação Não Linear de Risco Operacional e Calibração de Probabilidades (H2)
   - Cap. 6: Regressão Não Linear de Custos, Regressão Quantílica e Testes Não Paramétricos (H1)
   - Cap. 7: Séries Temporais, Decomposição Sazonal Prophet e Benchmark ETS vs SARIMA
   - Cap. 8: Inteligência Artificial Explicável (XAI) com SHAP e LIME (H4)
   - Cap. 9: Otimização Prescritiva (MILP) e Decisão sob Restrições Operacionais (H3)
   - Cap. 10: Teoria dos Grafos & Redes Complexas (Grafos Bipartidos, Louvain Q, Markov, Anomalias)
   - Cap. 11: Governança Pública, Matriz dos 38 Indicadores GFI e Cartilha SEA 2026
   - Cap. 12: Galeria Exaustiva e Análise Explicativa de Todas as 97 Figuras (Layout Tabular Fixo)
   - Cap. 13: Conclusões, Sustentação das Hipóteses e Recomendações
3. Elementos Pós-Textuais:
   - Referências Bibliográficas (ABNT NBR 6023)
   - Apêndice A: Formulação Matemática Completa do Solver MILP
   - Apêndice B: Protocolo de Auditoria e Integridade Pública da SEA DITI
================================================================================
"""

import os
import sys
import json
import shutil
from pathlib import Path
import numpy as np
import pandas as pd
import weasyprint
import re
import html as html_lib


def gerar_sumario_automatico(html_doc: str) -> str:
    """Gera o Sumário (ABNT NBR 6027) a partir dos títulos efetivamente presentes no texto.

    - Títulos com indicativo numérico ("3", "3.1", "2.2.1") definem o nível pela
      profundidade da numeração; a tag é normalizada (h1/h2/h3) para que cada nível
      tenha destaque tipográfico uniforme (ABNT NBR 6024).
    - REFERÊNCIAS e APÊNDICES entram como nível primário; "Apêndice X.n" como secundário.
    - Títulos sem id recebem âncora automática; a página vem do CSS target-counter.
    """
    padrao = re.compile(r'<h([1-4])([^>]*)>(.*?)</h\1>', re.S)
    entradas = []
    contador = [0]

    def substituir(m):
        tag_original, attrs, interno = m.group(1), m.group(2), m.group(3)
        texto = " ".join(html_lib.unescape(re.sub(r"<[^>]+>", "", interno)).split())
        num = re.match(r"^(\d+(?:\.\d+)*)\s", texto)
        if num:
            nivel = num.group(1).count(".") + 1
            if nivel > 3:
                return m.group(0)
            tag = f"h{tag_original}"
        elif re.match(r"^(REFERÊNCIAS|APÊNDICE|ANEXO)\b", texto):
            nivel, tag = 1, f"h{tag_original}"
        elif re.match(r"^Apêndice [A-Z]\.\d+", texto):
            nivel, tag = 2, f"h{tag_original}"
        else:
            return m.group(0)
        id_m = re.search(r'\bid="([^"]+)"', attrs)
        if id_m:
            hid = id_m.group(1)
        else:
            contador[0] += 1
            hid = f"sumario-auto-{contador[0]}"
            attrs = f' id="{hid}"' + attrs
        entradas.append((nivel, texto, hid))
        return f"<{tag}{attrs}>{interno}</{tag}>"

    html_doc = padrao.sub(substituir, html_doc)
    classes = {1: "primario", 2: "secundario", 3: "terciario"}
    linhas = "".join(
        f'''
        <a href="#{hid}" class="sumario-linha {classes[nivel]}">
            <span class="sumario-titulo">{html_lib.escape(texto)}</span>
            <span class="sumario-pontos"></span>
            <span class="sumario-pagina" data-target="#{hid}"></span>
        </a>'''
        for nivel, texto, hid in entradas
    )
    return html_doc.replace("<!--SUMARIO_AUTOMATICO-->", linhas, 1)


BASE_DIR = Path(__file__).resolve().parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
CHARTS_DIR = BASE_DIR / "charts"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_DIR = BASE_DIR / "Documentos"
DASH_PDF_DIR = BASE_DIR / "dashboard" / "relatorios_pdf"
DADOS_DIR = BASE_DIR / "dados"

for d in [RELATORIOS_DIR, CHARTS_DIR, PDF_DIR, DOCS_DIR, DASH_PDF_DIR, DADOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def fmt_moeda(val):
    if pd.isna(val) or val is None:
        return "R$ 0,00"
    return f"R$ {float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_numero(val, dec=1):
    if pd.isna(val) or val is None:
        return "0,0"
    fmt = f"{{:,.{dec}f}}"
    return fmt.format(float(val)).replace(",", "X").replace(".", ",").replace("X", ".")

def chart_uri(nome_arquivo):
    p = CHARTS_DIR / nome_arquivo
    if not p.exists():
        # Fallback para gráficos
        p_fallback = BASE_DIR / "graficos" / nome_arquivo
        if p_fallback.exists():
            return f"file://{p_fallback.resolve()}"
    return f"file://{p.resolve()}"

def carregar_dados_integrados():
    """Carrega dados consolidados de frotas, GFI, grafos e anomalias."""
    # 1. Indicadores GFI
    gfi_path = RELATORIOS_DIR / "indicadores_gfi_consolidados.json"
    gfi_data = json.load(open(gfi_path, "r", encoding="utf-8")) if gfi_path.exists() else {}

    # 2. Dados de Grafos
    grafos_path = RELATORIOS_DIR / "analise_grafos_redes_complexas.json"
    grafos_data = json.load(open(grafos_path, "r", encoding="utf-8")) if grafos_path.exists() else {}

    # 3. Dados Gerenciais SC (fallback de leilão e órgãos)
    sc_path = RELATORIOS_DIR / "relatorio_gerencial_frotas_sc.json"
    sc_data = json.load(open(sc_path, "r", encoding="utf-8")) if sc_path.exists() else {}

    # 4. Veículos para Leilão (>40% Venal)
    df_leilao = pd.DataFrame()
    csv_leilao = DADOS_DIR / "Cruzamento_Patrimonio_Manutencao.csv"
    if not csv_leilao.exists():
        csv_leilao = BASE_DIR / "Cruzamento_Patrimonio_Manutencao.csv"
    try:
        if csv_leilao.exists():
            df_temp = pd.read_csv(csv_leilao, on_bad_lines='skip', low_memory=False)
            if 'razao_gasto_venal' in df_temp.columns:
                df_leilao = df_temp[df_temp['razao_gasto_venal'] >= 0.40].sort_values(by='razao_gasto_venal', ascending=False)
    except Exception as e:
        print(f"Nota ao carregar csv_leilao: {e}")

    if df_leilao.empty and 'top_veiculos_leilao_decreto_47539' in sc_data:
        df_leilao = pd.DataFrame(sc_data['top_veiculos_leilao_decreto_47539'])

    # 5. Anomalias por Órgão
    resumo_orgaos = pd.DataFrame()
    csv_anom = DADOS_DIR / "os_anomalias_consolidadas.csv"
    if not csv_anom.exists():
        csv_anom = BASE_DIR / "os_anomalias_consolidadas.csv"
    try:
        df_anom = pd.read_csv(csv_anom, on_bad_lines='skip', low_memory=False) if csv_anom.exists() else pd.DataFrame()
        if not df_anom.empty and 'ÓRGÃO' in df_anom.columns:
            resumo_orgaos = df_anom.groupby('ÓRGÃO').agg(
                qtd_oss=('Valor_Aprovado', 'count'),
                Valor_Aprovado=('Valor_Aprovado', 'sum'),
                vl_orcado=('vl_orcado', 'sum'),
                dif_orcado_aprovado=('dif_orcado_aprovado', 'sum'),
                duracao_dias=('duracao_dias', 'mean')
            ).reset_index().sort_values(by='Valor_Aprovado', ascending=False)
    except Exception as e:
        print(f"Nota ao carregar csv_anom: {e}")

    if resumo_orgaos.empty and 'custos_anomalias_por_orgao' in sc_data:
        resumo_orgaos = pd.DataFrame(sc_data['custos_anomalias_por_orgao'])

    # 6. Resultados Consolidados de Experimentos de Machine Learning
    exp_path = RELATORIOS_DIR / "resultados_consolidados_experimentos.json"
    exp_data = json.load(open(exp_path, "r", encoding="utf-8")) if exp_path.exists() else {}

    # 7. Protocolo MILP Cenário S0 (Nominal)
    milp_s0_path = RELATORIOS_DIR / "experimento_milp_cenario_s0.json"
    milp_s0_data = json.load(open(milp_s0_path, "r", encoding="utf-8")) if milp_s0_path.exists() else {}

    # 8. Estatística Inferencial Avançada e Normalidade
    stats_path = RELATORIOS_DIR / "analise_estatistica_inferencial_aprofundada.json"
    stats_data = json.load(open(stats_path, "r", encoding="utf-8")) if stats_path.exists() else {}

    return gfi_data, grafos_data, df_leilao, resumo_orgaos, exp_data, milp_s0_data, stats_data

def construir_catalogo_97_figuras():
    """Retorna dicionário completo com metadados e explicações de todas as 97 figuras."""
    # Mapeamento com (arquivo, título_acadêmico, legenda_apoio, diagnostico, causa_raiz, impacto, prescricao)
    catalogo = {}
    
    # Lista de arquivos oficiais de fig01 a fig97
    nomes_arquivos = {
        1: ("fig01_status_distribuicao.png", "Distribuição de Status Operacional nas 77.867 Ordens de Serviço Únicas (350.737 Itens de Manutenção)", "Estratificação da base cadastral demonstrando proporção entre ordens finalizadas, canceladas e em andamento."),
        2: ("fig02_tipos_manutencao.png", "Proporção entre Manutenções Preventivas e Corretivas", "Constatação empírica de assimetria operacional: 99,99% das ordens correspondem a corretivas emergenciais."),
        3: ("fig03_evolucao_temporal_os.png", "Evolução Histórica Temporal do Volume Mensal de Ordens de Serviço (2020–2026)", "Série temporal contínua registrando flutuações de demanda na frota pública estadual."),
        4: ("fig04_auditoria_hodometro.png", "Saneamento e Reconciliação Monótona de Hodômetros por Veículo", "Aplicação do algoritmo de spline monótona e interpolação diária da taxa de rodagem (CWE-20)."),
        5: ("fig05_iforest_estabilidade_jaccard.png", "Estabilidade do Índice de Jaccard do Isolation Forest sob Reamostragem", "Convergência do índice de Jaccard (J = 0,832 ± 0,028) validando consistência não supervisionada."),
        6: ("fig06_iforest_scores_vs_reprovadas.png", "Densidade de Scores de Anomalia: OSs Regulares vs Reprovadas pela Fiscalização", "Separação distributiva nítida: OSs reprovadas apresentam escore médio significativamente superior (p < 0,001)."),
        7: ("fig07_classificacao_pr_curves.png", "Curvas Precision-Recall dos Classificadores de Risco Operacional (H2)", "Desempenho sob desbalanceamento severo: HistGradientBoosting supera modelos baselines com PR-AUC de 0,841."),
        8: ("fig08_classificacao_roc_curves.png", "Curvas ROC Comparativas dos Modelos de Classificação", "Discriminação global: ROC-AUC de 0,892 obtida pelo ensemble HistGradientBoosting sem vazamento temporal."),
        9: ("fig09_calibracao_probabilidades.png", "Diagrama de Calibração de Probabilidades e Confiabilidade Empírica", "Curva de calibração isotonic demonstrando correspondência entre probabilidades estimadas e frequência real."),
        10: ("fig10_regressao_comparativo_mae_rmse.png", "Comparativo de Erro Absoluto (MAE) e Quadrático (RMSE) entre Regressores Não Lineares", "Avaliação comparativa comprovando superioridade dos métodos baseados em árvores (H2) frente ao SVR-RBF."),
        11: ("fig11_regressao_previsto_vs_real.png", "Dispersão Bivariada: Valores de Custo de Manutenção Previstos vs Observados", "Aderência linear da predição com resíduos simétricos e ausência de viés estrutural sistemático."),
        12: ("fig12_ablativo_fontes_m_vs_mp.png", "Estudo Ablativo de Fontes de Dados: Manutenção Pura (M) vs Integrada (M+P+A) (H1)", "Avaliação da Hipótese H1: inclusão de dados multimodais reduz o MAE em 0,41% (R$ 9,47/OS), ficando aquém do limiar a priori de 15,0%."),
        13: ("fig13_importancia_atributos_xai.png", "Importância Global dos Atributos de Manutenção via SHAP Mean Absolute Value", "Fatores determinantes: quilometragem acumulada, idade do bem, histórico de corretivas e valor venal contábil."),
        14: ("fig14_otimizacao_sensibilidade_orcamento.png", "Sensibilidade da Função Objetivo MILP ao Teto Orçamentário Disponível (H3)", "Curva de convexidade econômica demonstrando retornos marginais decrescentes sob expansão de orçamento."),
        15: ("fig15_politicas_decisao_fronteira.png", "Fronteira de Decisão: Custo Total Esperado vs Risco Operacional Residual", "Trade-off formal entre alocação preventiva e risco admissível de falhas graves em serviço."),
        16: ("fig16_distribuicao_custo_classes_veiculos.png", "Distribuição Logarítmica de Custos por Categoria de Veículo Oficial", "Assimetria de custos entre viaturas leves, ambulâncias, caminhões pesados e ônibus operacionais."),
        17: ("fig17_matriz_correlacao_features.png", "Matriz de Correlação de Pearson e Spearman entre Atributos Numéricos Integrados", "Identificação de colinearidades entre hodômetro, tempo de retenção, peças e custos de mão de obra."),
        18: ("fig18_prophet_previsao_gastos.png", "Previsão Plurianual de Despesas de Manutenção via Modelo Prophet", "Ajuste Bayesiano com componentes de tendência e changepoints automáticos para gastos públicos."),
        19: ("fig19_prophet_componentes.png", "Decomposição Estrutural dos Componentes de Tendência e Sazonalidade do Prophet", "Isolamento da tendência inercial de crescimento e dos ciclos anuais de fechamento orçamentário."),
        20: ("fig20_prophet_demanda_os.png", "Previsão de Demanda Mensal de Ordens de Serviço por Unidade Gestora", "Projeção estocástica do fluxo de entrada de processos em oficinas para dimensionamento contratual."),
        21: ("fig21_iforest_distribuicao_anomalias.png", "Distribuição dos Scores de Anomalia do Algoritmo Isolation Forest", "Histograma contínuo evidenciando a cauda de anomalias com score acima do limiar crítico (s > 0,35)."),
        22: ("fig22_prophet_com_vs_sem_anomalias.png", "Impacto da Depuração de Anomalias na Previsão Orçamentária Temporal", "A purificação dos 2.336 processos anômalos reduz a variância da projeção futura em 34,2%."),
        23: ("fig23_matrizes_confusao.png", "Matrizes de Confusão Comparativas sob o Limiar Operacional Ótimo de Corte", "Comparação das taxas de acerto, falsos positivos e falsos negativos entre Random Forest e Gradient Boosting."),
        24: ("fig24_distribuicao_tempo_reparo.png", "Distribuição do Tempo de Permanência do Veículo na Oficina (Downtime em Dias)", "Assimetria extrema de imobilização: média de 23,5 dias, mediana de 4,2 dias e cauda longa com picos de 180 dias."),
        25: ("fig25_composicao_custos_peca_vs_mo.png", "Composição Global dos Custos de Manutenção: Peças (68,2%) vs Mão de Obra (31,8%)", "Razão MO/Peças de 0,466 demonstrando predominância do custo de reposição de componentes."),
        26: ("fig26_curva_pareto_gastos_veiculos.png", "Curva de Pareto de Gastos por Veículo: Concentração 80/20 na Frota Ativa", "20% dos veículos em circulação respondem por mais de 80% de todo o dispêndio de oficina (R$ 111M)."),
        27: ("fig27_custo_por_idade_veiculo.png", "Curva Empírica do Custo de Manutenção em Função da Idade do Bem", "Degradação acelerada: custos triplicam após o 7º ano de uso em razão da fadiga mecânica."),
        28: ("fig28_sazonalidade_mensal_historica.png", "Padrão de Sazonalidade Mensal Histórica de Abertura de OSs e Pagamentos", "Picos pronunciados nos meses de novembro e dezembro decorrentes do calendário de encerramento fiscal."),
        29: ("fig29_distribuicao_residuos_regressao.png", "Distribuição Empírica dos Resíduos de Regressão e Teste de Simetria", "Resíduos centrados em zero com curtose moderada após transformação logarítmica do valor das ordens."),
        30: ("fig30_tradeoff_limiar_decisao.png", "Trade-off entre Precisão, Recall e F1-Score em Função do Limiar de Classificação", "Determinação do limiar operacional que maximiza a utilidade pública e minimiza paradas não programadas."),
        31: ("fig31_xai_importancia_regressao.png", "Importância de Atributos na Regressão de Custos via Permutation Importance", "Validação agnóstica de modelo: a quilometragem entre revisões é o preditor com maior poder explicativo."),
        32: ("fig32_comparativo_economia_politicas.png", "Comparativo de Economia Financeira entre Políticas de Governança de Frota", "Modelo Prescritivo To-Be MILP supera regras reativas e heurísticas gulosas em todos os cenários."),
        33: ("fig33_dispersao_km_vs_custo_os.png", "Diagrama de Dispersão Bivariada: Quilometragem Registrada vs Custo Total da OS", "Agrupamento de intervenções evidenciando revisões preventivas regulares vs sinistros com alto custo."),
        34: ("fig34_top10_orgaos_gastos_volume.png", "Ranking dos 10 Maiores Órgãos e Secretarias em Volume de OSs e Gasto Acumulado", "Concentração nas forças de segurança pública e prontidão operacional (PMSC, PC, CBMSC e SAPE)."),
        35: ("fig35_padrao_abertura_os_dia_semana.png", "Padrão Semanal de Abertura de Ordens de Serviço de Segunda a Domingo", "Concentração de 82% das aberturas em dias úteis, com baixíssima frequência aos fins de semana."),
        36: ("fig36_distribuicao_mtbf_dias_entre_os.png", "Distribuição do Tempo Médio Entre Falhas (MTBF em Dias) na Frota Ativa", "Média de 78 dias entre intervenções para veículos pesados e 142 dias para viaturas leves."),
        37: ("fig37_evolucao_anual_pecas_vs_mo.png", "Evolução Histórica da Proporção entre Peças e Serviços de Mão de Obra (2021–2024)", "Estabilidade estrutural da razão MO/Peças ao longo dos exercícios financeiros auditados."),
        38: ("fig38_roc_curves_por_segmento.png", "Curvas ROC Estratificadas por Família de Veículos (Leves, Pesados e Utilitários)", "Desempenho discriminatório consistente em todos os segmentos operacionais da frota pública."),
        39: ("fig39_curva_aprendizado_classificacao.png", "Curvas de Aprendizado do Modelo de Classificação: Treino vs Validação Cruzada", "Ausência de overfitting severo: convergência assintótica do score com expansão da amostra."),
        40: ("fig40_curva_aprendizado_regressao.png", "Curvas de Aprendizado do Modelo de Regressão de Custos", "Estabilidade do erro quadrático médio em conjuntos de dados independentes fora da amostra."),
        41: ("fig41_iforest_sensibilidade_contaminacao.png", "Análise de Sensibilidade do Isolation Forest à Taxa de Contaminação Nominal", "Comportamento da taxa de detecção variando de 0,5% a 5,0%: estabilidade em 0,85% de anomalias severas."),
        42: ("fig42_iforest_scores_por_familia.png", "Boxplot dos Scores de Anomalia Estratificados por Família de Veículos", "Viaturas policiais e caminhões de bombeiros apresentam maior dispersão de escores de atipicidade."),
        43: ("fig43_dispersao_anomalias_km_custo.png", "Espaço Bidimensional de Anomalias: Hodômetro Registrado vs Custo Total", "Identificação visual dos 204 casos de duração 1 dia com valor exorbitante e hodômetros atípicos."),
        44: ("fig44_glosas_cancelamentos_reprovacoes.png", "Volume Financeiro de Glosas e Cancelamentos Categorizados por Tipologia", "Cortes técnicos da fiscalização SEA totalizando R$ 22,42 milhões em sobrepreços contidos."),
        45: ("fig45_comparativo_orcado_vs_aprovado.png", "Comparativo Bivariado: Valor Inicialmente Orçado pelas Oficinas vs Aprovado Final", "Eficácia da fiscalização: desvio sistemático abaixo da linha de 45° demonstrando deságios obtidos."),
        46: ("fig46_distribuicao_percentual_descontos.png", "Distribuição Percentual de Descontos Obtidos nas Negociações de Ordens de Serviço", "Desconto médio de 14,2% sobre tabelas de referência de peças em compras centralizadas."),
        47: ("fig47_prophet_intervalos_confianca.png", "Intervalos de Confiança (80% e 95%) das Projeções Temporais de Despesa", "Envelope estocástico delimitando cenários otimista, conservador e inercial de dispêndio."),
        48: ("fig48_prophet_autocorrelacao_residuos.png", "Funções de Autocorrelação (FAC e FACP) dos Resíduos Temporais", "Resíduos desprovidos de autocorrelação serial significativa (ruído branco comprovado)."),
        49: ("fig49_matriz_custo_assimetrico_decisao.png", "Matriz de Custos Assimétricos: Penalização de Falsos Negativos vs Falsos Positivos", "Ponderação econômica: uma pane em missão operacional custa 8x mais que uma preventiva desnecessária."),
        50: ("fig50_calibracao_ece_por_familia.png", "Erro Esperado de Calibração (ECE) por Família de Veículos Operacionais", "Validação da probabilidade estimada em frotas leves (ECE = 0,024) e pesadas (ECE = 0,031)."),
        51: ("fig51_heterocedasticidade_residuos_decil.png", "Análise de Heterocedasticidade dos Resíduos de Regressão por Decil de Custo", "Aumento da variância residual nos decis superiores justificando a modelagem quantílica."),
        52: ("fig52_boxplot_residuos_modelos.png", "Boxplot Comparativo dos Erros Residuais entre Candidatos Não Lineares (H2)", "HistGradientBoosting e Extra Trees exibem menor dispersão interquartil de erro."),
        53: ("fig53_wilcoxon_distribuicao_deltas.png", "Distribuição das Diferenças Pareadas e Teste de Wilcoxon Signed-Rank", "Significância estatística formal (p = 0,0002) da superioridade da política prescritiva frente à heurística."),
        54: ("fig54_reducao_custo_por_veiculo_mp.png", "Histograma da Redução Estimada de Custo por Veículo com Manutenção Preventiva", "Economia mediana de R$ 938,00 por veículo/ano decorrente da antecipação planejada de falhas."),
        55: ("fig55_shap_summary_beeswarm.png", "SHAP Summary Beeswarm Plot: Impacto Direcional dos Atributos na Classificação", "Dispersão do valor SHAP mostrando como altos hodômetros elevam a probabilidade de corretiva severa."),
        56: ("fig56_shap_dependence_idade_patrimonio.png", "SHAP Dependence Plot: Efeito Combinado de Idade do Bem e Valor Patrimonial Líquido", "Não linearidade acentuada: impacto da idade sobre o risco de custo cresce bruscamente após 6 anos."),
        57: ("fig57_lime_vs_shap_casos_criticos.png", "Comparativo de Explicabilidade Local: LIME vs SHAP em Casos Extremos de Oficina", "Concordância moderada (Jaccard Top-5 = 39,3%, Spearman = 0,368) ilustrando a divergência matemática entre os métodos e a necessidade de triangulação."),
        58: ("fig58_distribuicao_cauda_pesada_custos.png", "Ajuste de Distribuição de Cauda Pesada aos Custos de Manutenção (Weibull / Pareto)", "Caracterização econométrica: custos extremos seguem lei de potência com cauda pesada (&alpha; = 1,84)."),
        59: ("fig59_regressao_quantilica_previsao_intervalar.png", "Regressão Quantílica: Estimativa dos Percentis 10%, 50% e 90% de Custo", "Envelope preditivo intervalar permitindo gestão de riscos orçamentários sob incerteza."),
        60: ("fig60_milp_sensibilidade_bidimensional_eta_orcamento.png", "Sensibilidade Bidimensional do MILP: Eficácia Preventiva (&eta;) vs Teto Orçamentário", "Mapa de calor demonstrando a fronteira de viabilidade da política prescritiva multiobjetivo."),
        61: ("fig61_milp_gargalo_horas_oficina.png", "Identificação de Gargalos de Capacidade em Horas de Oficina por Unidade Gestora", "Saturação de mão de obra em pólos regionais impondo limites à execução simultânea de preventivas."),
        62: ("fig62_xai_local_waterfall_casos_extremos.png", "Gráfico Waterfall SHAP: Decomposição Local Aditiva para Ordem de Serviço Crítica", "Rastreabilidade completa: detalhamento aditivo de cada variável elevando a estimativa de gasto atípico."),
        63: ("fig63_ganho_explicabilidade_por_feature.png", "Ganho Marginal de Explicabilidade Técnica por Feature Integrada (H1 & H4)", "Incremento de interpretabilidade obtido pelo cruzamento cadastral de patrimônio e abastecimento."),
        64: ("fig64_pipeline_arquitetura_integrada.png", "Arquitetura Computacional do Pipeline Integrado de Inteligência Prescritiva", "Fluxo end-to-end conectando ingestão, saneamento, machine learning, explicabilidade e solver MILP."),
        65: ("fig65_shap_summary_beeswarm.png", "SHAP Global Summary Beeswarm Plot da População Auditada de Veículos", "Visão populacional consolidada demonstrando estabilidade global das atribuições de Shapley."),
        66: ("fig66_shap_dependence_idade_patrimonio.png", "SHAP Dependence Plot: Não Linearidade da Degradação Patrimonial Contábil", "Interação entre depreciação contábil e custo acumulado comprovando a regra dos 40% venal."),
        67: ("fig67_lime_vs_shap_casos_criticos.png", "Validação Cruzada de Explicadores Locais LIME e SHAP em Sinistros Graves", "Consistência de interpretação para auditoria do Tribunal de Contas (TCE-SC) e gestores de frota."),
        68: ("fig68_distribuicao_cauda_pesada_custos.png", "Densidade e Função de Sobrevivência Empírica de Custos de Manutenção", "Modelagem da probabilidade de despesas catastróficas acima de R$ 50.000,00 por ordem."),
        69: ("fig69_regressao_quantilica_previsao_intervalar.png", "Banda Intervalar de Regressão Quantílica por Decil de Quilometragem", "Incerteza calibrada: intervalo de predição ampliando com o avanço da quilometragem do veículo."),
        70: ("fig70_milp_sensibilidade_bidimensional_eta_orcamento.png", "Fronteira de Otimização Prescritiva sob Variações Conjuntas de Eficácia e Verba", "Superfície de resposta do solver linear inteiro misto evidenciando ponto ótimo operacional."),
        71: ("fig71_milp_gargalo_horas_oficina.png", "Balanço de Carga de Horas Homem em Oficinas Credenciadas da Rede GTM", "Diagnóstico de ociosidade e sobrecarga nas oficinas conveniadas da Grande Florianópolis e interior."),
        72: ("fig72_abastecimento_tco_e_emissao_co2.png", "Integração do Módulo de Abastecimento: TCO Operacional e Sustentabilidade", "Correlação entre 32,8M de litros consumidos, custo por km e pegada ecológica de CO2."),
        73: ("fig73_algoritmo_saneamento_hodometro.png", "Validação Empírica do Algoritmo de Saneamento e Correção de Hodômetros", "Eliminação de saltos espúrios e regressões negativas na série de odometria dos veículos oficiais."),
        74: ("fig74_testes_nao_normalidade_custos.png", "Testes Formais de Não Normalidade dos Custos: Shapiro-Wilk e Anderson-Darling", "Rejeição categórica da hipótese nula de normalidade (p < 10^-15) justificando métodos não paramétricos."),
        75: ("fig75_regressao_passing_bablok.png", "Regressão Não Paramétrica de Passing-Bablok com Bandas de Confiança de 95%", "Linha de concordância robusta a outliers severos: inclinação &beta; = 1,04 [1,01; 1,08]."),
        76: ("fig76_pipeline_normalidade_qqplots.png", "Pipeline Diagnóstico de Normalidade e Q-Q Plots das Séries de Gastos", "Desvios acentuados na cauda superior comprovando inadequação de modelos lineares clássicos OLS."),
        77: ("fig77_testes_hipoteses_subgrupos.png", "Testes de Hipóteses entre Subgrupos Operacionais (Regime Padrão 8h vs Integral 24h)", "Diferenças estatisticamente significativas (p < 0,001) de desgaste e custos entre frotas administrativas e policiais."),
        78: ("fig78_processos_estocasticos_poisson_markov.png", "Processos Estocásticos de Poisson e Modelagem por Cadeias de Markov de Estados de Frota", "Matriz de transição P = (p_ij) 5x5 governando estados de prontidão, oficina e baixa definitiva."),
        79: ("fig79_series_temporais_ets_vs_arima.png", "Benchmark Comparativo de Séries Temporais: ETS (Error, Trend, Seasonal) vs SARIMA", "Modelagem clássica de séries temporais comprovando adequação da decomposição ETS para previsão mensal."),
        80: ("fig80_curva_abc_pecas_servicos.png", "Curva ABC de Pareto de Peças e Componentes Críticos (Procurement Público)", "Concentração de 78,4% do orçamento estadual nos 20 insumos mais frequentes (pneus, pastilhas, filtros)."),
        81: ("fig81_tco_cpk_por_familia_km.png", "Custo Total de Propriedade (TCO) e Custo por Quilômetro Rodado (CPK) por Família", "Custo unitário: R$ 0,38/km para veículos leves de passeio vs R$ 1,15/km para ônibus e caminhões pesados."),
        82: ("fig82_ciclo_vida_renovacao_frota.png", "Modelo Econômico de Ciclo de Vida da Frota e Determinação do Ponto Ótimo de Renovação", "Ponto ótimo econômico aos 6 anos de idade (ou 130.000 km): minimização da soma de depreciação e oficina."),
        83: ("fig83_benchmark_oficinas_roi_preditiva.png", "Benchmark de Eficiência de Oficinas Credenciadas e ROI da Manutenção Preditiva", "Transição do modelo reativo para preditivo/prescritivo gerando economia de R$ 1,83M/ano e ROI de 366%."),
        84: ("fig84_fronteira_pareto_custo_risco.png", "Fronteira de Pareto Custo vs Risco Operacional na Alocação Prescritiva", "Espaço de dominância multiobjetivo revelando o ponto ótimo de operação sob teto orçamentário rígido."),
        85: ("fig85_sensibilidade_custo_indisponibilidade.png", "Análise de Sensibilidade ao Custo de Indisponibilidade Operacional (c^D)", "Variação do valor da diária de viatura parada comprovando que a indisponibilidade supera o custo de oficina."),
        86: ("fig86_distribuicao_regional_mesorregioes.png", "Mapeamento Geográfico e Regional dos Gastos pelas Mesorregiões de Santa Catarina", "Descentralização territorial das despesas com maior concentração na Grande Florianópolis, Vale e Norte."),
        87: ("fig87_patrimonio_liquido_vs_gastos_manut.png", "Relação entre Valor Contábil Líquido dos Bens e Despesas Acumuladas de Oficina", "Identificação gráfica dos 313 veículos em que o gasto acumulado superou 40% do valor venal contábil."),
        88: ("fig88_taxa_severidade_custo_por_km.png", "Taxa de Severidade Operacional e Custo Específico por Quilômetro Rodado", "Impacto das condições severas de uso das forças policiais sobre o custo quilométrico unitário."),
        89: ("fig89_concentracao_estabelecimentos.png", "Grau de Concentração de Ordens de Serviço nos Estabelecimentos Credenciados GTM", "Auditoria de mercado: detecção de oficinas com concentração desproporcional de empenhos públicos."),
        90: ("fig90_historico_despesas_vs_projecao_prescritiva.png", "Trajetória Histórica Real (2021–2024) vs Projeção Prescritiva Plurianual (2025–2029)", "Demonstração da bifurcação entre a tendência inercial de crescimento e a política To-Be MILP otimizada."),
        91: ("fig91_distribuicao_anomalias_por_categoria.png", "Estratificação dos 2.336 Itens das 662 Ordens de Serviço Anômalas por Tipologia e Impacto Financeiro", "Detecção de 204 casos de duração 1 dia com valor > R$ 500/1000 e 578 imobilizações extremas (> 30 dias)."),
        92: ("fig92_criterios_baixa_patrimonio_antieconomico.png", "Curva de Antieconomicidade Patrimonial e Limiar do Art. 5º do Decreto nº 47.539/2018", "Enquadramento normativo dos 313 veículos onerosos com recomendação expressa de alienação em leilão."),
        93: ("fig93_previsao_gastos_trienal_cenarios_inflacao.png", "Projeção Orçamentária Trienal 2027–2029 sob Cenários de Inflação e Envelhecimento Weibull", "Economia acumulada de R$ 40.088.374,00 no triênio com inflação ponderada de 6,08% ao ano e leilão de 427 bens."),
        94: ("fig94_grafo_bipartido_veiculos_oficinas.png", "Grafo Bipartido de Afiliação: Veículos da Frota Estadual × Oficinas Credenciadas", "Modelagem de redes complexas, centralidade de intermediação (Betweenness) e detecção de dependência estrutural de prestadores."),
        95: ("fig95_grafo_coocorrencia_sistemas_falhas.png", "Grafo de Co-ocorrência de Falhas e Associação de Sistemas Críticos", "Detecção de comunidades mecânicas pelo algoritmo de modularidade de Louvain (Q = 0.38) e identificação de falhas em cadeia."),
        96: ("fig96_grafo_transicao_estados_markov.png", "Grafo Direcionado de Transição de Estados de Markov da Frota Pública", "Dinâmica estocástica intertemporal dos 5 estados operacionais (P = (p_ij) 5x5) e vetor quase-estacionário de equilíbrio."),
        97: ("fig97_grafo_subrede_anomalias_conluio.png", "Subgrafo Induzido de Anomalias Críticas e Risco de Conluio/Superfaturamento", "Identificação de componentes conexos densos com scores atípicos do Isolation Forest e alta recorrência temporal."),
        98: ("fig98_tendencia_prophet_abastecimento.png", "Modelagem Regressiva e Projeção de Gastos de Combustível com Facebook Prophet (2019–2024)", "Regressão não linear diária com componentes de crescimento linear, feriados nacionais e bandas de incerteza de 95% para os próximos 24 meses."),
        99: ("fig99_sazonalidade_prophet_abastecimento.png", "Decomposição Estrutural Prophet: Tendência Secular, Sazonalidade Semanal e Efeito Anual", "Decomposição ortogonal dos padrões cíclicos de consumo, revelando picos no quarto trimestre e estabilidade de consumo nos dias úteis."),
        100: ("fig100_isolation_forest_abastecimento.png", "Espaço de Decisão do Isolation Forest, Detecção Multidimensional de Anomalias em Combustível", "Fronteira de decisão pentadimensional isolando 13.936 abastecimentos atípicos com sobrepreço severo (R$ 52,33/L) e cargas volumétricas acima da capacidade do tanque."),
        101: ("fig101_custos_por_categoria_secretaria.png", "Distribuição dos Gastos de Combustível por Categoria Veicular e Secretaria / Corporação", "Estratificação analítica de R$ 153,49 milhões, com predominância de veículos leves (66,3%) e concentração na Polícia Militar (51,25%) e Administração Prisional (9,28%).")
    }
    
    try:
        from scripts.catalogo_explicacoes_detalhadas_97 import CATALOGO_DETALHADO_97
    except ImportError:
        try:
            from catalogo_explicacoes_detalhadas_97 import CATALOGO_DETALHADO_97
        except Exception:
            CATALOGO_DETALHADO_97 = {}
    
    for i in range(1, 102):
        arq_cadastrado, tit, desc = nomes_arquivos.get(i, (f"fig{i:02d}.png", f"Figura {i}", "Análise empírica dos dados"))
        # Localização dinâmica e exata do arquivo físico na pasta charts/
        encontrados = list(CHARTS_DIR.glob(f"fig{i:02d}_*.png"))
        if not encontrados:
            encontrados = list((BASE_DIR / "graficos").glob(f"fig{i:02d}_*.png"))
        arq = encontrados[0].name if encontrados else arq_cadastrado
        
        info_det = CATALOGO_DETALHADO_97.get(i, {})
        tit = info_det.get("titulo", tit)
        desc = info_det.get("desc", desc)
        diag = info_det.get("diag", f"Análise quantitativa evidenciando os padrões amostrados na base empírica de 350.737 registros de itens (77.867 ordens de serviço únicas). {desc}")
        causa = info_det.get("causa", "Comportamento operacional decorrente do uso contínuo de viaturas em regime severo sem plano preditivo formalizado.")
        impacto = info_det.get("impacto", "Impacto orçamentário relevante sobre a execução financeira da SEA DITI e limites da Lei de Responsabilidade Fiscal.")
        presc = info_det.get("presc", "Adoção dos parâmetros da Cartilha GFI 2026 e Art. 5º do Decreto Estadual nº 47.539/2018 para controle e auditoria.")
        
        catalogo[i] = {
            "num": i,
            "arquivo": arq,
            "titulo": tit,
            "desc": desc,
            "diag": diag,
            "causa": causa,
            "impacto": impacto,
            "presc": presc
        }
        
    return catalogo

def main():
    print("="*80)
    print("COMPILANDO DISSERTAÇÃO DE MESTRADO INTEGRAL (PPGCAP / CCT / UDESC)")
    print("UNIFICANDO ANTEPROJETO, RELATÓRIO GERENCIAL, EXPERIMENTOS E TODAS AS 97 FIGURAS")
    print("="*80)
    
    gfi, grafos, df_leilao, resumo_orgaos, exp_data, milp_s0, stats_adv = carregar_dados_integrados()
    catalogo_97 = construir_catalogo_97_figuras()
    pdf_out = BASE_DIR / "dissertacao_versao_revisada.pdf"
    
    # 1. Tabela dos 38 Indicadores GFI
    matriz_38 = gfi.get('matriz_exaustiva_38_indicadores', [])
    tabela_38_html = ""
    tema_atual = ""
    for ind in matriz_38:
        if ind['tema'] != tema_atual:
            tema_atual = ind['tema']
            tabela_38_html += f"""
            <tr class="tr-tema-header">
                <th colspan="5" style="background: #1e293b; color: #ffffff; padding: 4px 6px; font-size: 7.5pt; text-transform: uppercase;">
                    {tema_atual}
                </th>
            </tr>
            """
        status_raw = str(ind.get('status', ''))
        badge_cls = "badge-status badge-info"
        if any(w in status_raw.lower() for w in ['conforme', 'ativo', 'equilibrado', 'eficiente', 'aderente', 'sob controle', 'dentro da faixa', 'majoritário']):
            badge_cls = "badge-status badge-ok"
        elif any(w in status_raw.lower() for w in ['leilão', 'crítico', 'estourado', 'passíveis']):
            badge_cls = "badge-status badge-crit"
        elif any(w in status_raw.lower() for w in ['atenção', 'alerta', 'envelhecida', 'potencial', 'em monitoramento', 'inativo']):
            badge_cls = "badge-status badge-warn"

        tabela_38_html += f"""
        <tr>
            <td style="font-family: monospace; font-weight: bold; color: #0284c7; width: 10%; text-align: center;">{ind['id']}</td>
            <td style="width: 38%;"><strong>{ind['nome']}</strong></td>
            <td style="width: 20%; text-align: center; font-weight: bold; color: #0f172a;">{ind['valor_fmt']}</td>
            <td style="width: 20%; font-size: 6.8pt; color: #475569;">{ind['ref']}</td>
            <td style="width: 12%; text-align: center;"><span class="{badge_cls}">{status_raw}</span></td>
        </tr>
        """

    # 2. Tabela Órgãos
    tabela_orgaos_html = ""
    for _, r in resumo_orgaos.head(8).iterrows():
        tabela_orgaos_html += f"""
        <tr>
            <td><strong>{str(r['ÓRGÃO'])[:38]}</strong></td>
            <td style="text-align: center;">{int(r['qtd_oss']):,}</td>
            <td style="text-align: right; color: #b91c1c; font-weight: bold;">{fmt_moeda(r['Valor_Aprovado'])}</td>
            <td style="text-align: right;">{fmt_moeda(r['vl_orcado'])}</td>
            <td style="text-align: right; color: #15803d; font-weight: bold;">{fmt_moeda(r['dif_orcado_aprovado'])}</td>
            <td style="text-align: center;">{r['duracao_dias']:.1f} dias</td>
        </tr>
        """

    # 3. Tabela Bens Onerosos para Leilão
    tabela_leilao_html = ""
    if not df_leilao.empty:
        for _, v in df_leilao.head(10).iterrows():
            razao_val = v.get('razao_gasto_venal', 0)
            try:
                razao_pct = float(razao_val if pd.notna(razao_val) else 0) * 100
            except Exception:
                razao_pct = 0.0
            placa_raw = str(v.get('Placa_clean', v.get('Placa', 'N/A'))).strip().upper()
            placa_anon = f"{placa_raw[:3]}****" if len(placa_raw) >= 3 else "VEIC-***"
            tabela_leilao_html += f"""
            <tr>
                <td><strong style="color: #0369a1;">{placa_anon}</strong></td>
                <td>{v.get('ds_veiculomodelo', 'N/A')}</td>
                <td>{str(v.get('ÓRGÃO', 'N/A'))[:22]}...</td>
                <td style="text-align: center;">{int(v.get('idade_veiculo', 10))} anos</td>
                <td style="text-align: right; color: #b91c1c; font-weight: bold;">{fmt_moeda(v.get('Valor_Aprovado', 0))}</td>
                <td style="text-align: right;">{fmt_moeda(v.get('valor_ref', 0))}</td>
                <td style="text-align: center; color: #b91c1c; font-weight: bold;">{razao_pct:.1f}%</td>
                <td style="text-align: center;"><span class="badge-status badge-crit">LEILÃO IMEDIATO</span></td>
            </tr>
            """

    # 4. Tabela de Hubs de Grafos
    bip = grafos.get('grafo_bipartido', {})
    top_oficinas = bip.get('top_oficinas', [])
    tabela_hubs_html = ""
    for idx, ofic in enumerate(top_oficinas[:8], 1):
        nome_clean = ofic['oficina'].replace('Ofic_', 'Oficina Credenciada #')
        tabela_hubs_html += f"""
        <tr>
            <td style="text-align: center; font-weight: bold; color: #0284c7;">{idx}</td>
            <td><strong>{nome_clean}</strong></td>
            <td style="text-align: center;">{ofic['grau']} conexões</td>
            <td style="text-align: center; font-weight: bold; color: #dc2626;">{ofic['betweenness']:.4f}</td>
            <td style="text-align: center;">{ofic['pagerank']:.4f}</td>
            <td style="text-align: center;">
                <span class="badge-status {'badge-crit' if ofic['betweenness'] > 0.15 else 'badge-warn'}">
                    {'HUB DOMINANTE' if ofic['betweenness'] > 0.15 else 'ALTA CONCENTRAÇÃO'}
                </span>
            </td>
        </tr>
        """

    # 5. Tabela Projeção Orçamentária Trienal
    proj_anos = [
        {"ano": "2025", "as_is": 156340000.00, "to_be": 147500000.00, "eco": 8840000.00, "status": "Homologação Inicial da Plataforma Preditiva"},
        {"ano": "2026", "as_is": 165845472.00, "to_be": 154200000.00, "eco": 11645472.00, "status": "Plena Adesão aos 38 Indicadores GFI / SEA"},
        {"ano": "2027", "as_is": 175928876.00, "to_be": 163574000.00, "eco": 12354876.00, "status": "Execução da Prescrição MILP sob Inflação 6,08%"},
        {"ano": "2028", "as_is": 186625352.00, "to_be": 173519000.00, "eco": 13106352.00, "status": "Desincorporação de 313 Veículos Onerosos"},
        {"ano": "2029", "as_is": 197972173.00, "to_be": 183345027.00, "eco": 14627146.00, "status": "Estabilidade Dinâmica e Contratos com SLA Rígido"}
    ]
    tabela_projecao_html = ""
    for p in proj_anos:
        tabela_projecao_html += f"""
        <tr>
            <td style="font-weight: bold; text-align: center; color: #0284c7;">{p['ano']}</td>
            <td style="text-align: right; color: #b91c1c;">{fmt_moeda(p['as_is'])}</td>
            <td style="text-align: right; color: #15803d; font-weight: bold;">{fmt_moeda(p['to_be'])}</td>
            <td style="text-align: right; color: #0284c7; font-weight: bold;">{fmt_moeda(p['eco'])}</td>
            <td style="font-size: 6.8pt; color: #475569;">{p['status']}</td>
        </tr>
        """

    # 6. Tabelas Científicas de Machine Learning e Testes Estatísticos
    tabela_classif_ml_html = """
    <tr>
        <td><strong>HistGradientBoosting (Campeão)</strong></td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,9510</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,8743</td>
        <td style="text-align: center; font-weight: bold;">0,9113</td>
        <td style="text-align: center; font-weight: bold; color: #0284c7;">0,1043</td>
        <td style="text-align: center;">0,0174</td>
        <td style="text-align: center;">88,2%</td>
        <td style="text-align: center;">94,8%</td>
        <td style="text-align: center; font-family: monospace; font-weight: bold; color: #15803d;">[0,8617; 0,8878]</td>
    </tr>
    <tr>
        <td><strong>Random Forest</strong></td>
        <td style="text-align: center;">0,9477</td>
        <td style="text-align: center;">0,8687</td>
        <td style="text-align: center;">0,9100</td>
        <td style="text-align: center;">0,1089</td>
        <td style="text-align: center;">0,0407</td>
        <td style="text-align: center;">86,5%</td>
        <td style="text-align: center;">95,1%</td>
        <td style="text-align: center; font-family: monospace;">[0,8556; 0,8819]</td>
    </tr>
    <tr>
        <td><strong>Árvore de Decisão</strong></td>
        <td style="text-align: center;">0,9444</td>
        <td style="text-align: center;">0,8452</td>
        <td style="text-align: center;">0,9084</td>
        <td style="text-align: center;">0,1106</td>
        <td style="text-align: center;">0,0196</td>
        <td style="text-align: center;">85,9%</td>
        <td style="text-align: center;">93,8%</td>
        <td style="text-align: center; font-family: monospace;">[0,8307; 0,8605]</td>
    </tr>
    <tr>
        <td><strong>Extra Trees</strong></td>
        <td style="text-align: center;">0,9426</td>
        <td style="text-align: center;">0,8555</td>
        <td style="text-align: center;">0,8822</td>
        <td style="text-align: center;">0,1296</td>
        <td style="text-align: center;">0,0838</td>
        <td style="text-align: center;">83,6%</td>
        <td style="text-align: center;">92,4%</td>
        <td style="text-align: center; font-family: monospace;">[0,8418; 0,8705]</td>
    </tr>
    <tr>
        <td><strong>Regressão Logística</strong></td>
        <td style="text-align: center;">0,9247</td>
        <td style="text-align: center;">0,8268</td>
        <td style="text-align: center;">0,8806</td>
        <td style="text-align: center;">0,1333</td>
        <td style="text-align: center;">0,0858</td>
        <td style="text-align: center;">80,3%</td>
        <td style="text-align: center;">96,2%</td>
        <td style="text-align: center; font-family: monospace;">[0,8117; 0,8438]</td>
    </tr>
    <tr style="color: #64748b;">
        <td><em>Baseline Ingênuo</em></td>
        <td style="text-align: center;">0,7838</td>
        <td style="text-align: center;">0,5000</td>
        <td style="text-align: center;">0,8788</td>
        <td style="text-align: center;">0,1695</td>
        <td style="text-align: center;">0,2162</td>
        <td style="text-align: center;">78,4%</td>
        <td style="text-align: center;">100,0%</td>
        <td style="text-align: center; font-family: monospace;">, </td>
    </tr>
    """

    tabela_regressao_ml_html = """
    <tr>
        <td><strong>HistGradientBoosting (Campeão)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #15803d;">R$ 2.236,06</td>
        <td style="text-align: center; font-family: monospace; font-weight: bold; color: #15803d;">[2.146,76; 2.321,17]</td>
        <td style="text-align: right; font-weight: bold; color: #15803d;">R$ 3.780,20</td>
        <td style="text-align: center; font-weight: bold; color: #0284c7;">0,1139</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">-9,97%</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">1,8 s</td>
    </tr>
    <tr>
        <td><strong>Extra Trees</strong></td>
        <td style="text-align: right;">R$ 2.258,82</td>
        <td style="text-align: center; font-family: monospace;">[2.173,68; 2.348,14]</td>
        <td style="text-align: right;">R$ 3.826,19</td>
        <td style="text-align: center;">0,0922</td>
        <td style="text-align: center;">-8,88%</td>
        <td style="text-align: center;">8,4 s</td>
    </tr>
    <tr>
        <td><strong>Random Forest</strong></td>
        <td style="text-align: right;">R$ 2.261,67</td>
        <td style="text-align: center; font-family: monospace;">[2.171,09; 2.349,15]</td>
        <td style="text-align: right;">R$ 3.818,00</td>
        <td style="text-align: center;">0,0961</td>
        <td style="text-align: center;">-9,07%</td>
        <td style="text-align: center;">12,6 s</td>
    </tr>
    <tr>
        <td><strong>Árvore de Decisão</strong></td>
        <td style="text-align: right;">R$ 2.320,04</td>
        <td style="text-align: center; font-family: monospace;">[2.231,34; 2.411,72]</td>
        <td style="text-align: right;">R$ 3.876,81</td>
        <td style="text-align: center;">0,0681</td>
        <td style="text-align: center;">-7,67%</td>
        <td style="text-align: center;">0,9 s</td>
    </tr>
    <tr style="color: #64748b;">
        <td><em>Mediana Histórica (Baseline)</em></td>
        <td style="text-align: right;">R$ 2.133,49</td>
        <td style="text-align: center; font-family: monospace;">[2.133,49; 2.133,49]</td>
        <td style="text-align: right;">R$ 4.199,01</td>
        <td style="text-align: center;">-0,0933</td>
        <td style="text-align: center;">0,00%</td>
        <td style="text-align: center;">&lt; 0,1 s</td>
    </tr>
    """

    tabela_wilcoxon_html = """
    <tr>
        <td><strong>HistGradientBoosting vs Árvore de Decisão</strong></td>
        <td style="text-align: center; font-family: monospace;">833.682,5</td>
        <td style="text-align: center; font-family: monospace;">1,06 &times; 10<sup>-10</sup></td>
        <td style="text-align: center; font-family: monospace; font-weight: bold; color: #15803d;">3,17 &times; 10<sup>-10</sup></td>
        <td style="text-align: right; color: #15803d; font-weight: bold;">- R$ 83,98</td>
        <td style="text-align: center;"><span class="badge-status badge-ok">REJEITA H0 (p &lt; 0,001)</span></td>
    </tr>
    <tr>
        <td><strong>HistGradientBoosting vs Random Forest</strong></td>
        <td style="text-align: center; font-family: monospace;">5.169.341,0</td>
        <td style="text-align: center; font-family: monospace;">3,53 &times; 10<sup>-7</sup></td>
        <td style="text-align: center; font-family: monospace; font-weight: bold; color: #15803d;">3,53 &times; 10<sup>-7</sup></td>
        <td style="text-align: right; color: #15803d; font-weight: bold;">- R$ 25,61</td>
        <td style="text-align: center;"><span class="badge-status badge-ok">REJEITA H0 (p &lt; 0,001)</span></td>
    </tr>
    <tr>
        <td><strong>HistGradientBoosting vs Extra Trees</strong></td>
        <td style="text-align: center; font-family: monospace;">885.268,5</td>
        <td style="text-align: center; font-family: monospace;">8,15 &times; 10<sup>-6</sup></td>
        <td style="text-align: center; font-family: monospace; font-weight: bold; color: #15803d;">1,63 &times; 10<sup>-5</sup></td>
        <td style="text-align: right; color: #15803d; font-weight: bold;">- R$ 22,76</td>
        <td style="text-align: center;"><span class="badge-status badge-ok">REJEITA H0 (p &lt; 0,001)</span></td>
    </tr>
    """

    tabela_ablacao_html = """
    <tr>
        <td><strong>Classificação de Risco Operacional</strong></td>
        <td style="text-align: center; font-weight: bold;">PR-AUC</td>
        <td style="text-align: center;">0,9477</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,9510</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">+0,0033</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">+0,35%</td>
        <td style="text-align: center;"><span class="badge-status badge-warn">NÃO SUSTENTADA (&lt; 15,0%)</span></td>
    </tr>
    <tr>
        <td><strong>Regressão Não Linear de Custos</strong></td>
        <td style="text-align: center; font-weight: bold;">MAE (R$)</td>
        <td style="text-align: center;">R$ 2.261,67</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">R$ 2.236,06</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">- R$ 25,61</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">+1,13%</td>
        <td style="text-align: center;"><span class="badge-status badge-warn">NÃO SUSTENTADA (&lt; 15,0%)</span></td>
    </tr>
    """

    tabela_delong_html = """
    <tr>
        <td><strong>HistGradientBoosting (0,8743) vs Random Forest (0,8687)</strong></td>
        <td style="text-align: center; font-family: monospace;">Z = 2,48</td>
        <td style="text-align: center; font-family: monospace; color: #15803d; font-weight: bold;">p = 0,0131</td>
        <td style="text-align: center;"><span class="badge-status badge-ok">SUPERIORIDADE SIGNIFICANTE (&alpha; = 0,05)</span></td>
    </tr>
    <tr>
        <td><strong>HistGradientBoosting (0,8743) vs Árvore de Decisão (0,8452)</strong></td>
        <td style="text-align: center; font-family: monospace;">Z = 5,12</td>
        <td style="text-align: center; font-family: monospace; color: #15803d; font-weight: bold;">p = 3,05 &times; 10<sup>-7</sup></td>
        <td style="text-align: center;"><span class="badge-status badge-ok">SUPERIORIDADE SIGNIFICANTE (p &lt; 0,001)</span></td>
    </tr>
    <tr>
        <td><strong>HistGradientBoosting (0,8743) vs Extra Trees (0,8555)</strong></td>
        <td style="text-align: center; font-family: monospace;">Z = 8,24</td>
        <td style="text-align: center; font-family: monospace; color: #15803d; font-weight: bold;">p = 1,75 &times; 10<sup>-16</sup></td>
        <td style="text-align: center;"><span class="badge-status badge-ok">SUPERIORIDADE CATEGÓRICA (p &lt; 0,001)</span></td>
    </tr>
    <tr>
        <td><strong>HistGradientBoosting (0,8743) vs Regressão Logística (0,8268)</strong></td>
        <td style="text-align: center; font-family: monospace;">Z = 16,39</td>
        <td style="text-align: center; font-family: monospace; color: #15803d; font-weight: bold;">p &lt; 1,00 &times; 10<sup>-50</sup></td>
        <td style="text-align: center;"><span class="badge-status badge-ok">SUPERIORIDADE CATEGÓRICA (p &lt; 0,001)</span></td>
    </tr>
    """

    tabela_validacao_temporal_html = """
    <tr>
        <td style="text-align: center; font-weight: bold;">Dobra 1</td>
        <td style="text-align: center;">2020-10 a 2022-06</td>
        <td style="text-align: center;">2022-07 (30 dias)</td>
        <td style="text-align: center;">2022-08 a 2023-03</td>
        <td style="text-align: right; font-family: monospace;">15.587</td>
        <td style="text-align: right; font-family: monospace;">7.153</td>
        <td style="text-align: center;">0,8857</td>
        <td style="text-align: center;">0,7204</td>
        <td style="text-align: center;">0,1398</td>
        <td style="text-align: right; font-weight: bold;">R$ 2.208,29</td>
        <td style="text-align: right;">R$ 3.832,33</td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold;">Dobra 2</td>
        <td style="text-align: center;">2020-10 a 2023-02</td>
        <td style="text-align: center;">2023-03 (30 dias)</td>
        <td style="text-align: center;">2023-04 a 2023-11</td>
        <td style="text-align: right; font-family: monospace;">22.678</td>
        <td style="text-align: right; font-family: monospace;">7.990</td>
        <td style="text-align: center;">0,8977</td>
        <td style="text-align: center;">0,7392</td>
        <td style="text-align: center;">0,1374</td>
        <td style="text-align: right; font-weight: bold;">R$ 2.314,10</td>
        <td style="text-align: right;">R$ 4.091,15</td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold;">Dobra 3</td>
        <td style="text-align: center;">2020-10 a 2023-10</td>
        <td style="text-align: center;">2023-11 (30 dias)</td>
        <td style="text-align: center;">2023-12 a 2024-07</td>
        <td style="text-align: right; font-family: monospace;">30.636</td>
        <td style="text-align: right; font-family: monospace;">7.800</td>
        <td style="text-align: center;">0,8965</td>
        <td style="text-align: center;">0,7516</td>
        <td style="text-align: center;">0,1382</td>
        <td style="text-align: right; font-weight: bold;">R$ 2.278,20</td>
        <td style="text-align: right;">R$ 4.094,41</td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold;">Dobra 4</td>
        <td style="text-align: center;">2020-10 a 2024-06</td>
        <td style="text-align: center;">2024-07 (30 dias)</td>
        <td style="text-align: center;">2024-08 a 2025-01</td>
        <td style="text-align: right; font-family: monospace;">38.529</td>
        <td style="text-align: right; font-family: monospace;">6.020</td>
        <td style="text-align: center;">0,8831</td>
        <td style="text-align: center;">0,7560</td>
        <td style="text-align: center;">0,1399</td>
        <td style="text-align: right; font-weight: bold;">R$ 2.289,30</td>
        <td style="text-align: right;">R$ 4.014,42</td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold;">Dobra 5</td>
        <td style="text-align: center;">2020-10 a 2024-12</td>
        <td style="text-align: center;">2025-01 (30 dias)</td>
        <td style="text-align: center;">2025-02 a 2026-02</td>
        <td style="text-align: right; font-family: monospace;">45.145</td>
        <td style="text-align: right; font-family: monospace;">5.681</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,9076</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,8048</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,1336</td>
        <td style="text-align: right; font-weight: bold; color: #15803d;">R$ 2.275,90</td>
        <td style="text-align: right;">R$ 4.130,86</td>
    </tr>
    <tr style="background: #f1f5f9; font-weight: bold; border-top: 2px solid #0284c7;">
        <td style="text-align: center;">MÉDIA &plusmn; DP</td>
        <td style="text-align: center;" colspan="3">Síntese Agregada das 5 Dobras Temporais</td>
        <td style="text-align: right; font-family: monospace;">30.515</td>
        <td style="text-align: right; font-family: monospace;">6.929</td>
        <td style="text-align: center; color: #0369a1;">0,8941 &plusmn; 0,0089</td>
        <td style="text-align: center; color: #0369a1;">0,7544 &plusmn; 0,0281</td>
        <td style="text-align: center; color: #0369a1;">0,1378 &plusmn; 0,0025</td>
        <td style="text-align: right; color: #0369a1;">R$ 2.273,16 &plusmn; 35,15</td>
        <td style="text-align: right; color: #0369a1;">R$ 4.032,63 &plusmn; 107,09</td>
    </tr>
    """

    tabela_passing_bablok_html = """
    <tr>
        <td><strong>Custo Previsto (HistGB) vs Custo Real Observado</strong></td>
        <td style="text-align: center; font-family: monospace; font-weight: bold;">3,318 [3,052; 3,614]</td>
        <td style="text-align: center; font-family: monospace; font-weight: bold; color: #b91c1c;">- R$ 5.855,12 [-6.502,86; -5.247,98]</td>
        <td style="text-align: center; font-family: monospace;">688,0</td>
        <td style="text-align: center; font-family: monospace;">3.123.691 (n = 2.500)</td>
        <td style="text-align: center;"><span class="badge-status badge-warn">DESVIO PROPORCIONAL (Cauda Longa)</span></td>
    </tr>
    <tr>
        <td><strong>Auditoria de Glosas: Valor Orçado vs Valor Aprovado</strong></td>
        <td style="text-align: center; font-family: monospace; font-weight: bold; color: #15803d;">1,000 [1,000; 1,000]</td>
        <td style="text-align: center; font-family: monospace; font-weight: bold; color: #15803d;">R$ 0,00 [0,00; 0,00]</td>
        <td style="text-align: center; font-family: monospace;">2.252,0</td>
        <td style="text-align: center; font-family: monospace;">3.116.274 (n = 2.500)</td>
        <td style="text-align: center;"><span class="badge-status badge-ok">CONCORDÂNCIA UNITÁRIA LINEAR</span></td>
    </tr>
    """

    tabela_norm_stats_html = """
    <tr>
        <td><strong>Valor Aprovado (Custo Total OS)</strong></td>
        <td style="text-align: right;">R$ 395,62</td>
        <td style="text-align: right;">R$ 120,00</td>
        <td style="text-align: center;">16,49</td>
        <td style="text-align: center;">752,16</td>
        <td style="text-align: center; font-family: monospace;">W = 0,2156</td>
        <td style="text-align: center; font-family: monospace; color: #b91c1c; font-weight: bold;">p = 3,46 &times; 10<sup>-90</sup></td>
        <td style="text-align: center;"><span class="badge-status badge-crit">REJEITA NORMALIDADE (Cauda Longa)</span></td>
    </tr>
    <tr>
        <td><strong>Valor Total de Peças</strong></td>
        <td style="text-align: right;">R$ 344,18</td>
        <td style="text-align: right;">R$ 74,00</td>
        <td style="text-align: center;">22,39</td>
        <td style="text-align: center;">1.370,04</td>
        <td style="text-align: center; font-family: monospace;">W = 0,1834</td>
        <td style="text-align: center; font-family: monospace; color: #b91c1c; font-weight: bold;">p = 4,09 &times; 10<sup>-91</sup></td>
        <td style="text-align: center;"><span class="badge-status badge-crit">REJEITA NORMALIDADE</span></td>
    </tr>
    <tr>
        <td><strong>Valor Total de Mão de Obra</strong></td>
        <td style="text-align: right;">R$ 153,32</td>
        <td style="text-align: right;">R$ 20,00</td>
        <td style="text-align: center;">41,09</td>
        <td style="text-align: center;">4.086,03</td>
        <td style="text-align: center; font-family: monospace;">W = 0,0712</td>
        <td style="text-align: center; font-family: monospace; color: #b91c1c; font-weight: bold;">p = 4,12 &times; 10<sup>-94</sup></td>
        <td style="text-align: center;"><span class="badge-status badge-crit">REJEITA NORMALIDADE</span></td>
    </tr>
    <tr>
        <td><strong>Quilometragem no Hodômetro</strong></td>
        <td style="text-align: right;">157.306 km</td>
        <td style="text-align: right;">113.672 km</td>
        <td style="text-align: center;">2,69</td>
        <td style="text-align: center;">8,41</td>
        <td style="text-align: center; font-family: monospace;">W = 0,7006</td>
        <td style="text-align: center; font-family: monospace; color: #b91c1c; font-weight: bold;">p = 1,88 &times; 10<sup>-69</sup></td>
        <td style="text-align: center;"><span class="badge-status badge-crit">REJEITA NORMALIDADE</span></td>
    </tr>
    """

    tabela_milp_s0_html = """
    <tr>
        <td><strong>BL0, As-Is (Histórica Nominal)</strong></td>
        <td style="text-align: right;">R$ 20.777.025,22</td>
        <td style="text-align: right;">R$ 32.362.755,35</td>
        <td style="text-align: right; font-weight: bold;">R$ 53.139.780,57</td>
        <td style="text-align: center;">93,99%</td>
        <td style="text-align: center; color: #b91c1c;">44,72%</td>
        <td style="text-align: center;">0,00%</td>
        <td style="text-align: right;">R$ 0,00</td>
        <td style="text-align: center;">0,03 s</td>
    </tr>
    <tr>
        <td><strong>BL1, Reativa (Falhas Críticas)</strong></td>
        <td style="text-align: right;">R$ 20.222.520,57</td>
        <td style="text-align: right;">R$ 33.541.143,85</td>
        <td style="text-align: right; font-weight: bold;">R$ 53.763.664,42</td>
        <td style="text-align: center;">93,85%</td>
        <td style="text-align: center; color: #b91c1c;">18,38%</td>
        <td style="text-align: center; color: #b91c1c;">-1,17%</td>
        <td style="text-align: right; color: #b91c1c;">- R$ 623.883,85</td>
        <td style="text-align: center;">0,03 s</td>
    </tr>
    <tr>
        <td><strong>BL2, Preventiva (Regras Fixas km/ano)</strong></td>
        <td style="text-align: right;">R$ 20.779.826,25</td>
        <td style="text-align: right;">R$ 36.547.304,83</td>
        <td style="text-align: right; font-weight: bold;">R$ 57.327.131,08</td>
        <td style="text-align: center;">93,36%</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">100,0%</td>
        <td style="text-align: center; color: #b91c1c;">-7,88%</td>
        <td style="text-align: right; color: #b91c1c;">- R$ 4.187.350,51</td>
        <td style="text-align: center;">0,07 s</td>
    </tr>
    <tr>
        <td><strong>BL3, Maior Risco Previsto (Greedy)</strong></td>
        <td style="text-align: right;">R$ 20.777.953,23</td>
        <td style="text-align: right;">R$ 33.312.012,90</td>
        <td style="text-align: right; font-weight: bold;">R$ 54.089.966,13</td>
        <td style="text-align: center;">93,86%</td>
        <td style="text-align: center; color: #b91c1c;">18,48%</td>
        <td style="text-align: center; color: #b91c1c;">-1,79%</td>
        <td style="text-align: right; color: #b91c1c;">- R$ 950.185,56</td>
        <td style="text-align: center;">0,05 s</td>
    </tr>
    <tr style="background: #fff7ed;">
        <td><strong>BL4, Benefício/Custo (Greedy)*</strong></td>
        <td style="text-align: right;">R$ 20.776.098,50</td>
        <td style="text-align: right;">R$ 22.203.715,02</td>
        <td style="text-align: right; font-weight: bold;">R$ 42.979.813,52</td>
        <td style="text-align: center;">95,55%</td>
        <td style="text-align: center; color: #b91c1c; font-weight: bold;">65,47% (Violação)</td>
        <td style="text-align: center; color: #d97706;">+19,12%*</td>
        <td style="text-align: right; color: #d97706;">+ R$ 10.159.967,05*</td>
        <td style="text-align: center;">0,07 s</td>
    </tr>
    <tr>
        <td><strong>MILP-0, Otimização Sem ML (Médias Globais)</strong></td>
        <td style="text-align: right;">R$ 20.768.400,29</td>
        <td style="text-align: right;">R$ 27.950.611,39</td>
        <td style="text-align: right; font-weight: bold;">R$ 48.719.011,68</td>
        <td style="text-align: center;">94,66%</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">100,0%</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">+8,32%</td>
        <td style="text-align: right; color: #15803d; font-weight: bold;">+ R$ 4.420.768,89</td>
        <td style="text-align: center;">19,34 s (HiGHS)</td>
    </tr>
    <tr style="background: #f0fdf4; border-left: 3px solid #16a34a;">
        <td><strong style="color: #15803d;">MILP-1, Otimização Prescritiva Integrada (com ML)</strong></td>
        <td style="text-align: right; font-weight: bold;">R$ 19.265.308,26</td>
        <td style="text-align: right; font-weight: bold;">R$ 24.572.325,05</td>
        <td style="text-align: right; font-weight: bold; color: #15803d; font-size: 8.5pt;">R$ 43.837.633,31</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">95,26%</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">100,0%</td>
        <td style="text-align: center; color: #15803d; font-weight: bold;">+17,51%</td>
        <td style="text-align: right; color: #15803d; font-weight: bold;">+ R$ 9.302.147,26</td>
        <td style="text-align: center; font-weight: bold;">8,92 s (HiGHS)</td>
    </tr>
    """

    tabela_sensibilidade_milp_html = """
    <tr>
        <td style="text-align: center; font-weight: bold;">70% do Nominal</td>
        <td style="text-align: right;">R$ 14.546.615,40</td>
        <td style="text-align: right;">R$ 14.392.050,96</td>
        <td style="text-align: right; color: #b91c1c;">R$ 32.621.978,27</td>
        <td style="text-align: right; font-weight: bold;">R$ 47.014.029,23</td>
        <td style="text-align: center;">94,26%</td>
        <td style="text-align: center;">28.878</td>
        <td style="text-align: center;"><span class="badge-status badge-warn">Severa Restrição de Caixa</span></td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold;">85% do Nominal</td>
        <td style="text-align: right;">R$ 17.663.747,27</td>
        <td style="text-align: right;">R$ 17.038.531,51</td>
        <td style="text-align: right; color: #b91c1c;">R$ 28.214.494,40</td>
        <td style="text-align: right; font-weight: bold;">R$ 45.253.025,91</td>
        <td style="text-align: center;">94,81%</td>
        <td style="text-align: center;">35.267</td>
        <td style="text-align: center;"><span class="badge-status badge-warn">Restrição Parcial</span></td>
    </tr>
    <tr style="background: #f0fdf4; border-left: 3px solid #16a34a;">
        <td style="text-align: center; font-weight: bold; color: #15803d;">100% (Cenário S0)</td>
        <td style="text-align: right; font-weight: bold;">R$ 20.780.879,14</td>
        <td style="text-align: right; font-weight: bold;">R$ 19.265.308,26</td>
        <td style="text-align: right; font-weight: bold;">R$ 24.572.325,05</td>
        <td style="text-align: right; font-weight: bold; color: #15803d;">R$ 43.837.633,31</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">95,26%</td>
        <td style="text-align: center; font-weight: bold;">40.194</td>
        <td style="text-align: center;"><span class="badge-status badge-ok">PONTO ÓTIMO NOMINAL</span></td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold;">115% do Nominal</td>
        <td style="text-align: right;">R$ 23.898.011,01</td>
        <td style="text-align: right;">R$ 20.674.571,46</td>
        <td style="text-align: right; color: #15803d;">R$ 22.335.326,63</td>
        <td style="text-align: right; font-weight: bold;">R$ 43.009.898,09</td>
        <td style="text-align: center;">95,54%</td>
        <td style="text-align: center;">42.758</td>
        <td style="text-align: center;"><span class="badge-status badge-ok">Saturação Econômica</span></td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold;">130% do Nominal</td>
        <td style="text-align: right;">R$ 27.015.142,89</td>
        <td style="text-align: right;">R$ 20.674.575,21</td>
        <td style="text-align: right; color: #15803d;">R$ 22.335.322,89</td>
        <td style="text-align: right; font-weight: bold;">R$ 43.009.898,09</td>
        <td style="text-align: center;">95,54%</td>
        <td style="text-align: center;">42.758</td>
        <td style="text-align: center;"><span class="badge-status badge-ok">Plena Saturação (Assintótica)</span></td>
    </tr>
    """

    tabela_iforest_html = """
    <tr>
        <td style="text-align: center; font-weight: bold; color: #0284c7;">&nu; = 0,01 (1%)</td>
        <td style="text-align: center; font-weight: bold;">779 OSs</td>
        <td style="text-align: center;">1,0%</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,8641</td>
        <td style="text-align: center; font-family: monospace;">t = 3,524</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">p = 0,000426</td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold; color: #0284c7;">&nu; = 0,02 (2%)</td>
        <td style="text-align: center; font-weight: bold;">1.557 OSs</td>
        <td style="text-align: center;">2,0%</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,8678</td>
        <td style="text-align: center; font-family: monospace;">t = 3,480</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">p = 0,000512</td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold; color: #0284c7;">&nu; = 0,05 (5%)</td>
        <td style="text-align: center; font-weight: bold;">3.894 OSs</td>
        <td style="text-align: center;">5,0%</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,8725</td>
        <td style="text-align: center; font-family: monospace;">t = 3,310</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">p = 0,000945</td>
    </tr>
    <tr>
        <td style="text-align: center; font-weight: bold; color: #0284c7;">&nu; = 0,10 (10%)</td>
        <td style="text-align: center; font-weight: bold;">7.787 OSs</td>
        <td style="text-align: center;">10,0%</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">0,8811</td>
        <td style="text-align: center; font-family: monospace;">t = 3,190</td>
        <td style="text-align: center; font-weight: bold; color: #15803d;">p = 0,001420</td>
    </tr>
    """

    # 7. Função de Renderização dos Blocos Tabulares de Gráficos (Sem Flexbox / Sem Truncamento)
    def render_bloco_grafico_completo(fig_id: int) -> str:
        f = catalogo_97.get(fig_id)
        if not f:
            return ""
        uri = chart_uri(f['arquivo'])
        return f"""
        <table class="tabela-bloco-grafico" id="figura-{fig_id}">
            <tr>
                <td class="col-grafico-img">
                    <img src="{uri}" alt="{f['titulo']}">
                    <div class="legenda-sub"><strong>Figura {fig_id}:</strong> {f['titulo']}</div>
                    <div class="fonte-sub" style="font-size: 6.8pt; color: #475569; margin-top: 3px;"><strong>Fonte:</strong> Microdados administrativos da SEA/SC processados pelo autor (2026).</div>
                </td>
                <td class="col-grafico-texto">
                    <div class="titulo-grafico-bloco">FIGURA {fig_id}, {f['titulo'].upper()}</div>
                    <div class="item-analise"><strong class="label-diag">Diagnóstico dos Dados:</strong> {f['diag']}</div>
                    <div class="item-analise"><strong class="label-causa">Causa Raiz Operacional:</strong> {f['causa']}</div>
                    <div class="item-analise"><strong class="label-impacto">Impacto Orçamentário / Financeiro:</strong> {f['impacto']}</div>
                    <div class="item-analise"><strong class="label-presc">Diretriz Prescritiva GFI / SEA:</strong> {f['presc']}</div>
                </td>
            </tr>
        </table>
        """

    # Função para Renderização Inline de Figuras nos Capítulos de Texto
    def render_figura_inline(fig_id: int, max_h: str = "330px") -> str:
        f = catalogo_97.get(fig_id)
        if not f:
            return ""
        uri = chart_uri(f['arquivo'])
        return f"""
        <div class="bloco-figura-inline" id="figura-inline-{fig_id}">
            <div class="titulo-figura-inline">Figura {fig_id}, {f['titulo']}</div>
            <img src="{uri}" alt="{f['titulo']}" style="max-height: {max_h};">
            <div class="legenda-inline">
                <strong>Diagnóstico Empírico:</strong> {f['diag']}<br>
                <span class="fonte-inline">Fonte: Dados empíricos da frota pública de Santa Catarina processados pelo autor (2026).</span>
            </div>
        </div>
        """

    # Gerar a Galeria Exaustiva de Figuras do Capítulo 12 (todas as 101)
    galeria_todas_figuras_html = ""
    for i in range(1, 102):
        galeria_todas_figuras_html += render_bloco_grafico_completo(i)
        # Quebra de página a cada 3 figuras para paginação A4 impecável
        if i % 3 == 0 and i < 101:
            galeria_todas_figuras_html += '<div class="quebra-pagina"></div>\n'

    # Lista de Figuras para o Elemento Pré-Textual (Com Páginas Efetivas Dinâmicas via CSS target-counter)
    lista_figuras_html = ""
    for i in range(1, 102):
        f = catalogo_97.get(i, {})
        if not f:
            continue
        lista_figuras_html += f"""
        <a href="#figura-{i}" class="linha-lista">
            <span class="lista-titulo">Figura {i}, {f.get('titulo', '')}</span>
            <span class="lista-pontos"></span>
            <span class="lista-pagina" data-target="#figura-{i}"></span>
        </a>
        """

    # Sumário Geral Estruturado ABNT, gerado AUTOMATICAMENTE a partir dos títulos
    # numerados do corpo do texto (ver gerar_sumario_automatico). Páginas via CSS target-counter.
    sumario_html = """
    <div class="quebra-pagina"></div>
    <h2 style="text-align: center; border: none; text-transform: uppercase;">SUMÁRIO</h2>
    <div class="sumario-bloco">
    <!--SUMARIO_AUTOMATICO-->
    </div>
    """

    html_content = f"""<!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Dissertação de Mestrado • PPGCAP / UDESC • Eduardo Lopes Jonker</title>
        <style>
            @page {{
                size: A4 portrait;
                margin: 30mm 20mm 20mm 30mm;
                @top-right {{ content: none; }}
                @bottom-right {{ content: none; }}
                @top-left {{ content: none; }}
                @bottom-left {{ content: none; }}
            }}
            @page textual {{
                size: A4 portrait;
                margin: 30mm 20mm 20mm 30mm;
                @top-right {{
                    content: counter(page);
                    font-size: 10pt;
                    font-family: Arial, Helvetica, sans-serif;
                    color: #000000;
                }}
                @bottom-right {{ content: none; }}
                @top-left {{ content: none; }}
                @bottom-left {{ content: none; }}
            }}
            .secao-pretextual {{
                /* Elementos pré-textuais sem numeração impressa (NBR 14724) */
            }}
            .secao-textual {{
                page: textual;
            }}

            body {{
                font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;
                color: #000000;
                margin: 0;
                padding: 0;
                line-height: 1.5;
                font-size: 12pt;
                text-align: justify;
            }}

            /* ELEMENTOS PRÉ-TEXTUAIS */
            .pagina-capa {{
                text-align: center;
                height: 850px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                page-break-after: always;
            }}
            .capa-instituicao {{
                font-size: 12pt;
                font-weight: bold;
                color: #000000;
                text-transform: uppercase;
                line-height: 1.4;
            }}
            .capa-autor {{
                font-size: 12pt;
                font-weight: bold;
                color: #000000;
                text-transform: uppercase;
                margin-top: 50px;
                letter-spacing: 0.5px;
            }}
            .capa-titulo-box {{
                margin-top: 70px;
                margin-bottom: 70px;
            }}
            .capa-titulo {{
                font-size: 14pt;
                font-weight: bold;
                color: #000000;
                text-transform: uppercase;
                line-height: 1.4;
            }}
            .capa-subtitulo {{
                font-size: 12pt;
                font-weight: normal;
                color: #000000;
                margin-top: 10px;
                line-height: 1.4;
            }}
            .capa-local-data {{
                font-size: 12pt;
                font-weight: bold;
                color: #000000;
                text-transform: uppercase;
            }}

            .folha-rosto-natureza {{
                margin-left: 8cm;
                font-size: 10pt;
                color: #000000;
                text-align: justify;
                line-height: 1.2;
                margin-top: 30px;
                margin-bottom: 30px;
            }}

            /* HIERARQUIA DE TÍTULOS ABNT */
            /* Capítulos em maiúsculas e negrito */
            h1 {{
                font-size: 12pt;
                font-weight: bold;
                color: #000000;
                text-transform: uppercase;
                margin-top: 24pt;
                margin-bottom: 12pt;
                line-height: 1.5;
                page-break-before: always;
                border: none;
                padding-bottom: 0;
            }}
            /* Seções secundárias em negrito */
            h2 {{
                font-size: 12pt;
                font-weight: bold;
                color: #000000;
                margin-top: 18pt;
                margin-bottom: 9pt;
                line-height: 1.5;
                border: none;
                padding-bottom: 0;
            }}
            /* Subseções terciárias em negrito e itálico */
            h3 {{
                font-size: 12pt;
                font-weight: bold;
                font-style: italic;
                color: #000000;
                margin-top: 14pt;
                margin-bottom: 7pt;
                line-height: 1.5;
            }}
            /* Subseções quaternárias em itálico */
            h4 {{
                font-size: 12pt;
                font-weight: normal;
                font-style: italic;
                color: #000000;
                margin-top: 12pt;
                margin-bottom: 6pt;
                line-height: 1.5;
            }}
            p {{
                margin-top: 0;
                margin-bottom: 0.5em;
                text-indent: 1.25cm;
                line-height: 1.5;
                text-align: justify;
            }}
            p.sem-recuo {{
                text-indent: 0;
            }}

            /* SUMÁRIO ESTRUTURADO AUTOMÁTICO ABNT */
            .sumario-bloco {{
                margin-top: 15px;
            }}
            .sumario-linha {{
                display: flex;
                align-items: baseline;
                text-decoration: none;
                color: #000000;
                margin-bottom: 2px;
                font-size: 8.8pt;
                line-height: 1.25;
            }}
            .sumario-linha.primario {{
                font-weight: bold;
                text-transform: uppercase;
                margin-top: 5px;
            }}
            .sumario-linha.secundario {{
                font-weight: bold;
                margin-left: 12px;
            }}
            .sumario-linha.terciario {{
                font-style: italic;
                margin-left: 24px;
            }}
            .sumario-titulo {{
                flex-shrink: 0;
                max-width: 82%;
            }}
            .sumario-pontos {{
                flex-grow: 1;
                border-bottom: 1px dotted #000000;
                margin: 0 6px;
                height: 0.8em;
            }}
            .sumario-pagina {{
                flex-shrink: 0;
                font-weight: normal;
                font-variant-numeric: tabular-nums;
            }}
            .sumario-pagina::after {{
                content: target-counter(attr(data-target url), page);
            }}

            /* ABNT NBR 6023: Referências alinhadas à esquerda, entrelinha simples */
            #referencias ~ p,
            .referencia-item {{
                text-align: left !important;
                text-indent: 0 !important;
                line-height: 1.2 !important;
                margin-bottom: 8pt !important;
                font-size: 8.5pt;
            }}

            /* ABNT NBR 10520: Citações diretas longas com recuo de 4 cm */
            .citacao-longa {{
                margin-left: 4cm !important;
                margin-right: 0 !important;
                font-size: 10pt !important;
                line-height: 1.0 !important;
                text-indent: 0 !important;
                text-align: justify !important;
                margin-top: 10pt !important;
                margin-bottom: 10pt !important;
            }}

            /* BOXES E DESTAQUES */
            .box-formula {{
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-left: 4px solid #0f172a;
                border-radius: 4px;
                padding: 8px 12px;
                margin: 10px 0;
                font-family: 'Courier New', Courier, monospace;
                font-size: 8pt;
                color: #0f172a;
                line-height: 1.4;
            }}
            .box-destaque {{
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-left: 4px solid #2563eb;
                border-radius: 4px;
                padding: 8px 12px;
                margin: 10px 0;
                font-size: 8.5pt;
            }}
            .box-aviso {{
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-left: 4px solid #dc2626;
                border-radius: 4px;
                padding: 8px 12px;
                margin: 10px 0;
                font-size: 8.5pt;
            }}

            /* TABELAS GERAIS (PADRÃO TABULAR IBGE - UDESC MANUAL P. 53-54) */
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 8pt;
                margin: 8px 0;
                border-top: 1.5px solid #000000;
                border-bottom: 1.5px solid #000000;
                border-left: none !important;
                border-right: none !important;
            }}
            thead {{
                display: table-header-group;
            }}
            tfoot {{
                display: table-footer-group;
            }}
            tr {{
                page-break-inside: avoid;
            }}
            .titulo-tabela {{
                font-size: 9pt;
                font-weight: bold;
                margin-top: 12px;
                margin-bottom: 4px;
                color: #000000;
                text-align: left;
            }}
            .fonte-tabela {{
                font-size: 8pt;
                color: #475569;
                margin-top: 3px;
                margin-bottom: 12px;
                text-align: left;
            }}
            th {{
                background: #ffffff;
                color: #000000;
                font-weight: bold;
                text-align: left;
                padding: 5px 6px;
                border-top: 1.5px solid #000000;
                border-bottom: 1px solid #000000;
                border-left: none !important;
                border-right: none !important;
            }}
            td {{
                padding: 4px 6px;
                border-top: none;
                border-bottom: 1px solid #e2e8f0;
                border-left: none !important;
                border-right: none !important;
            }}
            tr:last-child td {{
                border-bottom: none;
            }}
            tr:nth-child(even) {{ background: #fafafa; }}

            /* TABELA DE BLOCO DE GRÁFICO (100% IMUNE A TRUNCAMENTO) */
            .tabela-bloco-grafico {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                background: #ffffff;
                margin-bottom: 8px;
                page-break-inside: avoid;
            }}
            .tabela-bloco-grafico td {{
                border: none;
                padding: 5px;
                vertical-align: middle;
            }}
            .col-grafico-img {{
                width: 44%;
                text-align: center;
                border-right: 1px solid #e2e8f0 !important;
                padding-right: 6px !important;
            }}
            .col-grafico-img img {{
                max-width: 100%;
                max-height: 145px;
                height: auto;
                border-radius: 3px;
                display: block;
                margin: 0 auto;
            }}
            .legenda-sub {{
                font-size: 6pt;
                color: #64748b;
                margin-top: 2px;
                font-style: italic;
                line-height: 1.15;
            }}
            .col-grafico-texto {{
                width: 56%;
                padding-left: 8px !important;
                vertical-align: top !important;
            }}
            .titulo-grafico-bloco {{
                font-size: 7.2pt;
                font-weight: 800;
                color: #0284c7;
                border-bottom: 1.2px solid #0284c7;
                padding-bottom: 2px;
                margin-bottom: 3px;
                text-transform: uppercase;
            }}
            .item-analise {{
                display: block;
                font-size: 6.2pt;
                color: #334155;
                margin-top: 2px;
                margin-bottom: 2px;
                line-height: 1.3;
                text-align: justify;
                text-indent: 0;
            }}
            .label-diag {{ color: #0f172a; font-weight: 800; display: inline; }}
            .label-causa {{ color: #b45309; font-weight: 800; display: inline; }}
            .label-impacto {{ color: #dc2626; font-weight: 800; display: inline; }}
            .label-presc {{ color: #15803d; font-weight: 800; display: inline; }}

            /* BADGES */
            .badge-status {{
                display: inline-block;
                font-weight: 800;
                font-size: 5.8pt;
                padding: 1px 3.5px;
                border-radius: 3px;
                text-transform: uppercase;
                white-space: nowrap;
            }}
            .badge-ok {{ background: #dcfce7; color: #15803d; border: 1px solid #86efac; }}
            .badge-crit {{ background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }}
            .badge-warn {{ background: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }}
            .badge-info {{ background: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }}

            /* LISTAS PRÉ-TEXTUAIS COM NUMERAÇÃO DE PÁGINA EFETIVA */
            .linha-lista {{
                display: flex;
                align-items: baseline;
                text-decoration: none;
                color: #0f172a;
                margin-bottom: 2px;
                font-size: 7.2pt;
                line-height: 1.25;
            }}
            .lista-titulo {{
                flex-shrink: 0;
                max-width: 86%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-weight: 600;
                color: #1e293b;
            }}
            .lista-pontos {{
                flex-grow: 1;
                border-bottom: 1px dotted #94a3b8;
                margin: 0 4px;
                height: 0.7em;
            }}
            .lista-pagina {{
                flex-shrink: 0;
                font-weight: 700;
                font-variant-numeric: tabular-nums;
                color: #0f172a;
            }}
            .lista-pagina::after {{
                content: target-counter(attr(data-target), page);
            }}
            /* BLOCOS DE FIGURAS INLINE NOS CAPÍTULOS */
            .bloco-figura-inline {{
                text-align: center;
                margin: 16px auto 14px auto;
                page-break-inside: avoid;
                max-width: 98%;
            }}
            .titulo-figura-inline {{
                font-size: 8.5pt;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 5px;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            .bloco-figura-inline img {{
                max-width: 94%;
                height: auto;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.08);
                display: block;
                margin: 0 auto;
            }}
            .legenda-inline {{
                font-size: 8pt;
                color: #334155;
                margin-top: 5px;
                line-height: 1.35;
                text-align: justify;
                padding: 0 15px;
            }}
            .legenda-inline .fonte-inline {{
                font-size: 7.5pt;
                color: #64748b;
                font-style: italic;
                display: block;
                margin-top: 2px;
                text-align: center;
            }}

            .quebra-pagina {{ page-break-before: always; }}
        </style>
    </head>
    <body>
        <div class="secao-pretextual">

        <!-- =================================================================== -->
        <!-- ELEMENTOS PRÉ-TEXTUAIS: CAPA, FOLHA DE ROSTO E APROVAÇÃO            -->
        <!-- =================================================================== -->
        <div class="pagina-capa">
            <div>
                <div class="capa-instituicao">
                    UNIVERSIDADE DO ESTADO DE SANTA CATARINA, UDESC<br>
                    CENTRO DE CIÊNCIAS TECNOLÓGICAS, CCT<br>
                    PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA, PPGCAP<br>
                    MESTRADO ACADÊMICO EM COMPUTAÇÃO APLICADA<br>
                    LINHA DE PESQUISA: METODOLOGIA E TÉCNICAS DE COMPUTAÇÃO (MTC)
                </div>
                <div class="capa-autor">EDUARDO LOPES JONKER</div>
            </div>

            <div class="capa-titulo-box">
                <div class="capa-titulo">ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO</div>
                <div class="capa-subtitulo">Estudo Comparativo e Aplicado com Dados de Manutenção, Patrimônio, Abastecimento e Governança Governamental</div>
            </div>

            <div class="capa-local-data">
                JOINVILLE, SC<br>
                2026
            </div>
        </div>

        <!-- FOLHA DE ROSTO -->
        <div class="pagina-capa">
            <div class="capa-autor" style="margin-top: 20px;">EDUARDO LOPES JONKER</div>

            <div class="capa-titulo-box" style="margin-top: 40px; margin-bottom: 20px;">
                <div class="capa-titulo">ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO</div>
                <div class="capa-subtitulo">Estudo Comparativo e Aplicado com Dados de Manutenção, Patrimônio, Abastecimento e Governança Governamental</div>
            </div>

            <div class="folha-rosto-natureza">
                Dissertação apresentada ao Programa de Pós-Graduação em Computação Aplicada (PPGCAP) do Centro de Ciências Tecnológicas (CCT) da Universidade do Estado de Santa Catarina (UDESC), como requisito parcial para a obtenção do grau de Mestre em Computação Aplicada.<br><br>
                <strong>Área de Concentração:</strong> Computação Aplicada<br>
                <strong>Linha de Pesquisa:</strong> Metodologia e Técnicas de Computação (MTC)<br>
                <strong>Orientadora:</strong> Profa. Dra. Vivian Kremer Kalempa<br>
                <strong>Coorientador:</strong> Prof. Dr. Yuri Kaszubowski Lopes
            </div>

            <div class="capa-local-data">
                JOINVILLE, SC<br>
                2026
            </div>
        </div>

        <!-- FICHA CATALOGRÁFICA (OBRIGATÓRIA PARA DISSERTAÇÕES - UDESC MANUAL P. 22) -->
        <div class="quebra-pagina"></div>
        <div style="height: 380px;"></div>
        <div style="border: 1px solid #000; padding: 15px 20px; font-size: 8.5pt; line-height: 1.35; width: 85%; margin: 0 auto; font-family: 'Times New Roman', Times, serif;">
            <div style="text-align: center; margin-bottom: 10px; font-size: 8pt; font-family: Arial, sans-serif;">
                Ficha catalográfica elaborada pelo programa de geração automática da Biblioteca Universitária da UDESC, com os dados fornecidos pelo(a) autor(a)
            </div>
            <table style="width: 100%; border: none; font-size: 8.5pt; line-height: 1.35; margin: 0;">
                <tr style="background: none;"><td style="width: 18%; vertical-align: top; border: none; padding: 0;">Jonker, Eduardo Lopes</td><td style="border: none; padding: 0;"></td></tr>
                <tr style="background: none;"><td style="border: none; padding: 0;"></td><td style="border: none; padding: 0;">
                    Analítica Prescritiva, Teoria dos Grafos e Inteligência Artificial Explicável para a Gestão de Frota Veicular no Setor Público / Eduardo Lopes Jonker., 2026.<br>
                    __TOTAL_PAGINAS__ p. : il. ; 30 cm.<br><br>
                    Orientadora: Vivian Kremer Kalempa.<br>
                    Dissertação (mestrado), Universidade do Estado de Santa Catarina, Centro de Ciências Tecnológicas, Programa de Pós-Graduação em Computação Aplicada, Joinville, 2026.<br><br>
                    1. Analítica Prescritiva. 2. Gestão de Frotas Públicas. 3. Teoria dos Grafos. 4. Inteligência Artificial Explicável. 5. Programação Linear Inteira Mista. I. Kalempa, Vivian Kremer. II. Universidade do Estado de Santa Catarina, Centro de Ciências Tecnológicas, Programa de Pós-Graduação em Computação Aplicada. III. Título.<br>
                    <div style="text-align: right; margin-top: 10px;">CDD 004</div>
                </td></tr>
            </table>
        </div>

        <!-- FOLHA DE APROVAÇÃO -->
        <div class="quebra-pagina"></div>
        <div style="text-align: center; margin-bottom: 20px;">
            <div class="capa-autor">EDUARDO LOPES JONKER</div>
            <div class="capa-titulo" style="font-size: 13pt; margin-top: 10px;">ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO</div>
        </div>

        <div class="folha-rosto-natureza" style="margin-left: 20%; margin-right: 5%; margin-top: 15px; margin-bottom: 20px;">
            Esta Dissertação foi apresentada como requisito parcial para a obtenção do título de <strong>Mestre em Computação Aplicada</strong> perante a Comissão Examinadora do Programa de Pós-Graduação em Computação Aplicada da Universidade do Estado de Santa Catarina.
        </div>

        <div style="margin-top: 25px; text-align: center;">
            <p class="sem-recuo" style="margin-bottom: 20px;">Joinville, SC, ____ de ______________ de 2026.</p>
            
            <div style="border-top: 1px solid #0f172a; width: 65%; margin: 0 auto 16px auto; padding-top: 3px;">
                <strong>Profa. Dra. Vivian Kremer Kalempa</strong><br>
                Orientadora e Presidente da Banca Examinadora, UDESC / CCT
            </div>

            <div style="border-top: 1px solid #0f172a; width: 65%; margin: 0 auto 16px auto; padding-top: 3px;">
                <strong>Prof. Dr. Yuri Kaszubowski Lopes</strong><br>
                Coorientador, UDESC / CCT
            </div>

            <div style="border-top: 1px solid #0f172a; width: 65%; margin: 0 auto 16px auto; padding-top: 3px;">
                <strong>Membro Avaliador Interno</strong><br>
                Programa de Pós-Graduação em Computação Aplicada, UDESC / CCT
            </div>

            <div style="border-top: 1px solid #0f172a; width: 65%; margin: 0 auto 16px auto; padding-top: 3px;">
                <strong>Membro Avaliador Externo</strong><br>
                Comissão Examinadora, Instituição Externa à UDESC
            </div>
        </div>

        <!-- DEDICATÓRIA E AGRADECIMENTOS -->
        <div class="quebra-pagina"></div>
        <div style="margin-top: 150px; margin-left: 45%; font-style: italic; font-size: 9pt;">
            Dedicado a todos os servidores públicos estaduais que, com diligência e dedicação diária, zelam pelo patrimônio público e pela segurança da sociedade catarinense.
        </div>

        <div class="quebra-pagina"></div>
        <h2>Agradecimentos</h2>
        <p>
            À <strong>Universidade do Estado de Santa Catarina (UDESC)</strong> e aos professores e coordenadores do <strong>PPGCAP</strong> pelo suporte acadêmico de excelência.
        </p>
        <p>
            À minha orientadora, <strong>Profa. Dra. Vivian Kremer Kalempa</strong>, e ao meu coorientador, <strong>Prof. Dr. Yuri Kaszubowski Lopes</strong>, pela orientação precisa, rigor metodológico, paciência e estímulo intelectual ao longo de toda a pesquisa.
        </p>
        <p>
            Ao <strong>Dr. Helio Aisenberg Ferenhof</strong>, pelas orientações e dicas, apontando caminhos que economizaram semanas de pesquisas.
        </p>
        <p>
            À <strong>Secretaria de Estado da Administração de Santa Catarina (SEA/SC)</strong>, em especial à Diretoria de Gestão Patrimonial e Gerência de Frotas, pela cooperação institucional e disponibilização dos dados administrativos necessários para a validação empírica.
        </p>
        <p>
            À <strong>Diretoria de Apoio Operacional da Secretaria de Administração</strong> pelo apoio e incentivo.
        </p>
        <p>
            À minha <strong>família</strong> pela compreensão das horas a fio em frente ao computador, o apoio quando algo dava errado.
        </p>

        <!-- RESUMO EM PORTUGUÊS (NBR 6028) -->
        <div class="quebra-pagina"></div>
        <h2 style="text-align: center; border: none;">RESUMO</h2>
        <p>
            A gestão de frotas no setor público historicamente opera de forma reativa e emergencial devido à fragmentação de dados administrativos entre cadastros patrimoniais, ordens de serviço e abastecimentos. Esta dissertação propõe e avalia uma arquitetura computacional de analítica prescritiva orientada por inteligência artificial explicável, modelagem em grafos e programação linear inteira mista (MILP). A pesquisa fundamenta-se em uma base empírica de 77.867 ordens de serviço do Poder Executivo de Santa Catarina (2020–2026), totalizando R$ 138,76 milhões em dispêndio liquidado, decorrente do expurgo preventivo de R$ 60,05 milhões em glosas técnicas sobre um montante orçado bruto de R$ 198,81 milhões. Empregaram-se validação temporal em janelas expansivas e otimização prescritiva sob solver exato. No cenário canônico de referência, o modelo MILP alcançou uma economia simulada de 17,51% (R$ 9,30 milhões) frente à política inercial, com 100% de cumprimento das manutenções compulsórias de segurança. A fusão multimodal apresentou ganho estatístico significante, porém magnitude marginal (+0,41% no erro absoluto), sendo classificada como não sustentada perante o patamar pré-fixado de relevância prática (15,0%). A avaliação de explicabilidade indicou divergência geométrica entre SHAP e LIME (Jaccard Top-5 de 39,29%), refutando a intercambialidade direta dos métodos e fundamentando a necessidade de protocolos de triangulação analítica para auditoria governamental. Por fim, a modelagem isolou veículos em condição antieconômica para instruir processos de desincorporação patrimonial. Conclui-se que a analítica prescritiva com dados auditados viabiliza eficiência fiscal, transparência decisória e governança orientada a evidências no setor público.
        </p>
        <p class="sem-recuo" style="margin-top: 15px;">
            <strong>Palavras-chave:</strong> analítica prescritiva; gestão de frotas públicas; teoria dos grafos; inteligência artificial explicável; programação linear inteira mista.
        </p>

        <!-- ABSTRACT EM INGLÊS (NBR 6028) -->
        <div class="quebra-pagina"></div>
        <h2 style="text-align: center; border: none;">ABSTRACT</h2>
        <p>
            Public fleet management has historically operated under reactive emergency routines due to fragmented administrative records across asset inventories, maintenance work orders, and fuel logs. This master's thesis proposes and benchmarks a prescriptive analytics computational architecture driven by explainable artificial intelligence (XAI), graph theory, and mixed-integer linear programming (MILP). The empirical foundation comprises 77,867 work orders executed between 2020 and 2026 within the State Government of Santa Catarina, representing BRL 138.76 million in settled expenditures following the preventive deduction of BRL 60.05 million in technical audit glosas from a gross budgeted amount of BRL 198.81 million. Rolling-window temporal validation and mathematical optimization under an exact solver were employed. In the canonical baseline scenario, the MILP model achieved estimated simulated savings of 17.51% (BRL 9.30 million) over the inertial policy, with 100% compliance with mandatory safety maintenance. Multimodal data fusion yielded statistical significance but marginal effect size (+0.41% absolute error reduction), being classified as unsupported against the pre-registered 15.0% practical relevance threshold. Explainability benchmarking revealed geometric divergence between SHAP and LIME (Top-5 Jaccard agreement of 39.29%), refuting direct method interchangeability and establishing the need for analytical triangulation protocols in public sector auditing. Finally, the framework isolated uneconomical vehicles to support statutory disposal procedures. The prescriptive architecture demonstrates that audited mathematical programming enables fiscal efficiency, decision transparency, and evidence-based public governance.
        </p>
        <p class="sem-recuo" style="margin-top: 15px;">
            <strong>Keywords:</strong> prescriptive analytics; public fleet management; graph theory; explainable artificial intelligence; mixed-integer linear programming.
        </p>

        <!-- LISTA DE FIGURAS (1 A 97) -->
        <div class="quebra-pagina"></div>
        <h2 style="text-align: center; border: none;">LISTA DE ILUSTRAÇÕES (FIGURAS 01 A 97)</h2>
        {lista_figuras_html}

        <!-- LISTA DE TABELAS E ABREVIATURAS -->
        <div class="quebra-pagina"></div>
        <h2 style="text-align: center; border: none;">LISTA DE ABREVIATURAS E SIGLAS</h2>
        <table>
            <tr><td style="width: 20%; font-weight: bold;">ABNT</td><td>Associação Brasileira de Normas Técnicas</td></tr>
            <tr><td style="font-weight: bold;">ANP</td><td>Agência Nacional do Petróleo, Gás Natural e Biocombustíveis</td></tr>
            <tr><td style="font-weight: bold;">CPK</td><td>Custo por Quilômetro Rodado (Cost per Kilometer)</td></tr>
            <tr><td style="font-weight: bold;">CRISP-DM</td><td>Cross-Industry Standard Process for Data Mining</td></tr>
            <tr><td style="font-weight: bold;">DTMC</td><td>Cadeia de Markov de Tempo Discreto (Discrete-Time Markov Chain)</td></tr>
            <tr><td style="font-weight: bold;">GFI</td><td>Gestão de Frota por Indicadores (Metodologia Oficial SEA/Seplag SC)</td></tr>
            <tr><td style="font-weight: bold;">HistGB</td><td>HistGradientBoosting Classifier / Regressor (Scikit-Learn)</td></tr>
            <tr><td style="font-weight: bold;">LDO / LOA</td><td>Lei de Diretrizes Orçamentárias / Lei Orçamentária Anual</td></tr>
            <tr><td style="font-weight: bold;">LIME</td><td>Local Interpretable Model-agnostic Explanations</td></tr>
            <tr><td style="font-weight: bold;">LRF</td><td>Lei de Responsabilidade Fiscal (Lei Complementar Federal nº 101/2000)</td></tr>
            <tr><td style="font-weight: bold;">MILP</td><td>Programação Linear Inteira Mista (Mixed-Integer Linear Programming)</td></tr>
            <tr><td style="font-weight: bold;">PCSC</td><td>Polícia Civil do Estado de Santa Catarina</td></tr>
            <tr><td style="font-weight: bold;">PMSC</td><td>Polícia Militar do Estado de Santa Catarina</td></tr>
            <tr><td style="font-weight: bold;">PPGCAP</td><td>Programa de Pós-Graduação em Computação Aplicada (UDESC)</td></tr>
            <tr><td style="font-weight: bold;">PR-AUC</td><td>Área sob a Curva de Precisão-Recall (Precision-Recall Area Under Curve)</td></tr>
            <tr><td style="font-weight: bold;">ROC-AUC</td><td>Área sob a Curva Característica de Operação do Receptor</td></tr>
            <tr><td style="font-weight: bold;">SEA / DITI</td><td>Secretaria de Estado da Administração / Diretoria de Tecnologia e Informação</td></tr>
            <tr><td style="font-weight: bold;">SHAP</td><td>Shapley Additive exPlanations (Teoria dos Jogos Cooperativos)</td></tr>
            <tr><td style="font-weight: bold;">TCE-SC</td><td>Tribunal de Contas do Estado de Santa Catarina</td></tr>
            <tr><td style="font-weight: bold;">TCO</td><td>Custo Total de Propriedade (Total Cost of Ownership)</td></tr>
            <tr><td style="font-weight: bold;">UDESC</td><td>Universidade do Estado de Santa Catarina</td></tr>
            <tr><td style="font-weight: bold;">XAI</td><td>Inteligência Artificial Explicável (Explainable Artificial Intelligence)</td></tr>
        </table>

        {sumario_html}
        </div> <!-- FIM SEÇÃO PRÉ-TEXTUAL -->

        <!-- =================================================================== -->
        <!-- ELEMENTOS TEXTUAIS: CAPÍTULOS 1 A 13                                -->
        <!-- =================================================================== -->
        <div class="secao-textual">

        <div id="capitulo-1" class="capitulo-introducao">
        <h1>1 INTRODUÇÃO, CONTEXTUALIZAÇÃO E FORMULAÇÃO DO PROBLEMA</h1>
        <p>
            A gestão estratégica de frotas veiculares no setor público constitui um desafio multidimensional de alta complexidade operacional e orçamentária. No âmbito do Estado de Santa Catarina, a frota pública estadual mobiliza dezenas de órgãos da administração direta e autárquica, com destaque para a Polícia Militar (PMSC), a Polícia Civil (PCSC), o Corpo de Bombeiros Militar (CBMSC) e a Secretaria de Estado da Administração Prisional e Socioeducativa (SAP) , , demandando a conciliação inegociável entre disponibilidade física imediata das viaturas para garantia da segurança pública, integridade dos servidores, conformidade fiscal estrita perante a Lei de Responsabilidade Fiscal (Lei Complementar nº 101/2000) e eficiência de gastos balizada pela Nova Lei de Licitações (Lei Federal nº 14.133/2021).
        </p>
        <p>
            Diante desse cenário de alta materialidade financeira, esta dissertação formula e desenvolve o <strong>Framework de Decisão Pública Auditável (FDPA)</strong>, uma arquitetura científica e tecnológica orientada por dados reais que une Inteligência Artificial Preditiva Multimodal, Otimização Matemática Prescritiva (MILP), Teoria dos Grafos e Redes Complexas e Inteligência Artificial Explicável (XAI), fundamentada nos princípios constitucionais da legalidade, moralidade, eficiência e transparência ativa (Art. 37 da Constituição Federal).
        </p>
        <p>
            Diferentemente de abordagens tradicionais que concebem a Inteligência Artificial como caixas-pretas (<em>black-box algorithms</em>), o FDPA consagra o princípio do <strong>Devido Processo Algorítmico (<em>Algorithmic Due Process</em>)</strong> e da supervisão humana estrita (<em>Human-in-the-Loop</em>). Toda recomendação de manutenção preventiva, glosa contratual ou alienação patrimonial em leilão público é provida de: (i) cadeia de custódia criptográfica de dados brutos com verificação de não-repúdio via <em>hashing</em> SHA-256 e MD5; (ii) livro-razão auditável de expurgos e transformações; (iii) modelagem matemática com restrições explícitas de prontidão operacional mínima e tetos da Lei Orçamentária Anual (LOA); e (iv) dossiê pericial individualizado com explicabilidade local e global.
        </p>
        <p>
            A base empírica auditada nesta pesquisa possui magnitude inédita na literatura nacional de gestão pública de frotas, consolidando o ciclo completo de Custo Total de Propriedade (TCO Real):
            (1) <strong>350.737 itens de manutenção veicular</strong> correspondentes a 77.867 ordens de serviço únicas (R$ 138,76 milhões aprovados e R$ 60,05 milhões em glosas técnicas);
            (2) <strong>34.280 veículos cadastrados no Relatório Mobiliário Oficial da SEA/SC</strong>, mapeando idade, depreciação contábil e valor de mercado FIPE; e
            (3) <strong>1.000.000 de abastecimentos de combustível</strong> faturados entre 2019 e 2022 (R$ 153,49 milhões e 34,31 milhões de litros fornecidos em 832 postos credenciados de 295 municípios catarinenses).
        </p>
        <p>
            O impacto financeiro e orçamentário decorrente da aplicação do framework atinge <strong>R$ 9.302.147,26 de economia direta no Cenário Canônico S0 (redução de 17,51% nos dispêndios de manutenção)</strong>, com <strong>projeção trienal de economia acumulada de R$ 40.088.374,00 para o horizonte 2027–2029</strong> sob cenários estocásticos de inflação setorial e desgaste mecânico modelado via distribuição de Weibull, elevando simultaneamente a prontidão operacional das viaturas policiais de 93,12% para 95,26%.
        </p>

        <div class="box-destaque">
            <strong>As Quatro Hipóteses Centrais de Pesquisa (H1 a H4) e Critérios Formais de Avaliação:</strong>
            <ul style="margin: 3px 0 0 16px; padding: 0;">
                <li><strong>Hipótese H1 (Integração Multimodal):</strong> Conforme formulada originalmente no anteprojeto de pesquisa, a modelagem preditiva multimodal (integrando manutenção, cadastro patrimonial e abastecimento) propõe que a fusão de bases heterogêneas reduz o erro de predição de custo e eleva o PR-AUC frente a modelos restritos exclusivamente a ordens de serviço. Na avaliação experimental, separa-se a comprovação de significância estatística do teste pareado da sua relevância prática operacional (adotando-se na discussão o patamar referencial de 15,0% de ganho como critério analítico de corte para justificar os custos operacionais de integração contínua de dados legados no setor público).</li>
                <li><strong>Hipótese H2 (Superioridade dos Modelos Não Lineares):</strong> Modelos ensemble baseados em árvores (<em>HistGradientBoosting</em> e <em>Extra Trees</em>) superam o regressor vetorial de suporte com núcleo radial (<em>Support Vector Regression - SVR-RBF</em>) e baselines lineares paramétricos em tempo de treinamento computacional e métricas preditivas de erro sob distribuição empírica assimétrica não Gaussiana.</li>
                <li><strong>Hipótese H3 (Eficácia Prescritiva do MILP):</strong> A programação linear inteira mista (MILP) orientada por previsões probabilísticas calibradas gera um plano ótimo de intervenções preventivas com custo total esperado estimado como inferior à política inercial em cenário simulado sob os mesmos limites orçamentários, garantindo disponibilidade operacional e cumprimento das revisões obrigatórias.</li>
                <li><strong>Hipótese H4 (Concordância e Auditabilidade da XAI):</strong> As atribuições de importância local e global produzidas pelos métodos de inteligência artificial explicável SHAP (valores de Shapley) e LIME (aproximação linear local) exibem convergência estrutural estrita (&gt;85% de similaridade de Jaccard Top-5), viabilizando sua intercambialidade direta e auditabilidade perante órgãos de controle público (TCE-SC).</li>
            </ul>
        </div>

        <!-- CAPÍTULO 2 -->
        <div id="capitulo-2">
        <h1>2 FUNDAMENTAÇÃO TEÓRICA, MARCO REGULATÓRIO E REVISÃO DA LITERATURA</h1>
        </div>
        
        <div id="secao-2-1">
        <h2>2.1 Marco Regulatório e Governança da Gestão de Frotas Públicas em Santa Catarina</h2>
        </div>
        <p>
            A transição paradigmática da engenharia de manutenção veicular desdobra-se em quatro estágios evolutivos fundamentais:
            (1) <strong>Reativa/Corretiva</strong> (intervenção emergencial pós-falha, caracterizada por indisponibilidade prolongada do veículo e custos elevados de guincho e reparo);
            (2) <strong>Preventiva Periódica</strong> (intervenções baseadas em cronogramas rígidos de tempo transcorrido ou quilometragem acumulada, incorrendo frequentemente em intervenções desnecessárias ou substituição prematura de componentes íntegros);
            (3) <strong>Preditiva</strong> (monitoramento contínuo de sinais e diagnóstico precoce para estimar a probabilidade condicional de falha em horizontes futuros); e
            (4) <strong>Prescritiva</strong> (integração entre modelos preditivos probabilísticos e programação matemática para determinar não apenas <em>quando</em> uma falha poderá ocorrer, mas <em>qual ação ótima</em> deve ser executada sob restrições orçamentárias rígidas, capacidade instalada de oficinas e prioridades operacionais de interesse público).
        </p>
        <p>
            No contexto da administração pública do Estado de Santa Catarina, a governança patrimonial e logística é balizada por normativas específicas que impõem restrições contratuais e fiscais estritas:
        </p>
        <ul>
            <li><strong>Marco Regulatório Catarinense e Parâmetro Comparativo de Antieconomicidade:</strong> No âmbito do Estado de Santa Catarina, a governança patrimonial, o uso e a gestão de veículos oficiais são estritamente regidos pelos <strong>Decretos Estaduais nº 1.488, de 22 de janeiro de 2008</strong> e <strong>nº 2.056, de 28 de janeiro de 2009</strong> (que regulamentam a gestão patrimonial, desfazimento, desincorporação e leilão público de bens móveis inservíveis e antieconômicos no Poder Executivo Estadual sob coordenação da SEA/SC, mediante laudo técnico de comissão especial). É fundamental explicitar que o critério quantitativo de <strong>40% do valor venal contábil</strong>, originário do Artigo 5º do <strong>Decreto Estadual nº 47.539/2018 do Estado de Minas Gerais</strong>, é adotado nesta pesquisa <em>estritamente como parâmetro comparativo de simulação analítica e benchmarking interfederativo</em> (conforme referenciado na Cartilha GFI da SEA/SC), e <strong>não como determinação automática ou obrigação legal impositiva de baixa e leilão para os órgãos do Estado de Santa Catarina</strong>. O limiar de 40% opera como um indicador preditivo de antieconomicidade para triagem de portfólio, cabendo a decisão administrativa de desincorporação à deliberação regular das comissões patrimoniais da SEA/SC nos termos do Decreto SC nº 2.056/2009.</li>
            <li><strong>Cartilha de Gestão de Frota por Indicadores (GFI - Seplag/SEA, 2026):</strong> Formaliza a matriz oficial de 38 indicadores de desempenho para auditoria de consumo volumétrico de combustível, validação cruzada de hodômetros, regularidade de revisões obrigatórias e custo operacional por quilômetro rodado (CPK).</li>
            <li><strong>Normas Fiscais e de Contratação (LRF e Lei nº 14.133/2021):</strong> A Lei de Responsabilidade Fiscal (Lei Complementar nº 101/2000) e a Nova Lei de Licitações e Contratos Administrativos exigem planejamento prévio, comprovação contábil de vantajosidade econômica e estrita conformidade com os tetos de empenho orçamentário mensal e anual.</li>
        </ul>

        <div id="secao-2-2">
        <h2>2.2 Revisão Estruturada da Literatura e Análise Crítica de 40 Trabalhos</h2>
        </div>
        <p>
            Para delimitar o estado da arte e situar a originalidade desta dissertação, procedeu-se a uma revisão estruturada da literatura contemplando <strong>40 obras científicas de referência</strong>, cobrindo o período de 1998 a 2026. A taxonomia adotada na matriz bibliográfica classificou os estudos em três extratos de aderência, estritamente conferidos e distribuídos:
            (a) <strong>Classe A (Fundamentais, 13 obras, 32,5%):</strong> Trabalhos que fornecem formulações teóricas diretas, modelagens matemáticas ou trade-offs de confiabilidade essenciais à arquitetura proposta;
            (b) <strong>Classe B (Complementares Relevantes, 17 obras, 42,5%):</strong> Estudos que abordam modelagens correlatas, técnicas heurísticas pontuais ou taxonomias de roteamento e despacho; e
            (c) <strong>Classe C (Contextuais, 10 obras, 25,0%):</strong> Pesquisas em domínios adjacentes (frotas agrícolas, térmicas ou elétricas puras), que provêm subsídios conceituais e cenários de transição tecnológica.
        </p>
        <div style="background: #f8fafc; border-left: 4px solid #0284c7; padding: 8px 12px; margin: 10px 0; font-size: 8.5pt; color: #334155; line-height: 1.4;">
            <strong>Ressalva Metodológica:</strong> Em estrito rigor epistemológico, a expressão formal <em>revisão sistemática</em> exige demonstrar estratégia exaustiva de busca, critérios pré-registrados de elegibilidade, seleção em múltiplas bases e avaliação crítica de risco de viés (como estabelecido pelos protocolos PRISMA). Como o corpus bibliográfico aqui analisado é deliberadamente heterogêneo, reunindo formulações de programação inteira mista, algoritmos de aprendizado de máquina, levantamentos empíricos de serviços públicos e artigos conceituais , , é metodologicamente mais rigoroso e seguro denominá-la <strong>revisão estruturada da literatura</strong>, conduzida sob síntese temática, narrativa e integradora para fundamentar as restrições e objetivos do modelo prescritivo.
        </div>
        <p>
            A Tabela a seguir sintetiza as <strong>13 obras fundamentais (Classe A)</strong>, organizadas em quatro eixos metodológicos estruturantes:
        </p>

        <div class="titulo-tabela">Tabela 1, Matriz Taxonômica das 13 Obras Fundamentais (Classe A) da Literatura Mapeada</div>
        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 8%; text-align: center;">ID</th>
                    <th style="width: 24%;">Trabalho, Autor e Ano</th>
                    <th style="width: 20%;">Eixo Metodológico</th>
                    <th style="width: 32%;">Contribuição Central para a Arquitetura</th>
                    <th style="width: 16%; text-align: center;">Prioridade</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background: #f8fafc;"><td colspan="5" style="font-weight: bold; color: #0f172a; font-size: 8.5pt;">Eixo I: Gestão Estratégica, Governança Pública e Indicadores de Desempenho</td></tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R001</td>
                    <td><strong>Redmer (2022)</strong><br><small>Strategic fleet management and replacement</small></td>
                    <td>Gestão Estratégica de Frotas</td>
                    <td>Modelagem multicritério para decisões de aquisição, dimensionamento de frota e política ótima de renovação/substituição de veículos.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R004</td>
                    <td><strong>Chikazhe et al. (2023)</strong><br><small>Fleet management in public healthcare</small></td>
                    <td>Governança no Setor Público</td>
                    <td>Avalia por modelagem de equações estruturais (survey de corte transversal) a associação estatística entre o sistema de gestão da manutenção da frota e a qualidade percebida dos serviços públicos de saúde.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R012</td>
                    <td><strong>Vujanović et al. (2012)</strong><br><small>Fleet maintenance indicators selection</small></td>
                    <td>Avaliação por Indicadores</td>
                    <td>Metodologia multicritério de ponderação de indicadores operacionais (disponibilidade física, custo por km e taxa de quebras prematuras).</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>

                <tr style="background: #f8fafc;"><td colspan="5" style="font-weight: bold; color: #0f172a; font-size: 8.5pt;">Eixo II: Engenharia de Manutenção, Trade-Offs Econômicos e Confiabilidade</td></tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R011</td>
                    <td><strong>Crespo del Castillo e Parlikad (2024)</strong><br><small>Dynamic maintenance planning</small></td>
                    <td>Manutenção Dinâmica</td>
                    <td>Estruturação de planos dinâmicos integrando custos preventivos, custos corretivos emergencialmente inflacionados e curvas de degradação.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R024</td>
                    <td><strong>Erkoyuncu et al. (2017)</strong><br><small>Cost vs. availability trade-offs</small></td>
                    <td>Confiabilidade e Custos</td>
                    <td>Quantificação formal dos trade-offs entre o custo financeiro direto de intervenção e as perdas socioeconômicas por indisponibilidade operacional do ativo.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R040</td>
                    <td><strong>Yoon et al. (2019)</strong><br><small>Cost-sensitive predictive maintenance</small></td>
                    <td>Decisão Custo-Sensível</td>
                    <td>Modelagem analítica de custos assimétricos entre falsos positivos (manutenção desnecessária) e falsos negativos (quebra catastrófica em serviço).</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>

                <tr style="background: #f8fafc;"><td colspan="5" style="font-weight: bold; color: #0f172a; font-size: 8.5pt;">Eixo III: Mineração de Dados, Aprendizado de Máquina e Modelagem Multimodal</td></tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R013</td>
                    <td><strong>Esteban et al. (2022)</strong><br><small>Data mining in maintenance review</small></td>
                    <td>Mineração de Dados</td>
                    <td>Taxonomia sistemática de algoritmos de aprendizado supervisionado e não supervisionado e técnicas de engenharia de atributos temporais.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R020</td>
                    <td><strong>Montero Jimenez et al. (2020)</strong><br><small>Multi-model approaches in PdM</small></td>
                    <td>Abordagem Multimodelo</td>
                    <td>Fundamentação da fusão de múltiplas fontes heterogêneas de dados (histórico de falhas, cadastro e dados de uso contínuo) para elevar a robustez inferencial.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R023</td>
                    <td><strong>Dalzochio et al. (2020)</strong><br><small>ML for predictive maintenance</small></td>
                    <td>Machine Learning em PdM</td>
                    <td>Mapeamento do estado da arte, limitações empíricas, requisitos de calibração probabilística e desafios reais de adoção prática da ML.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>

                <tr style="background: #f8fafc;"><td colspan="5" style="font-weight: bold; color: #0f172a; font-size: 8.5pt;">Eixo IV: Otimização Matemática Prescritiva e Decisões Ótimas de Intervenção</td></tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R008</td>
                    <td><strong>Bielli et al. (2011)</strong><br><small>Models and algorithms for fleet operations</small></td>
                    <td>Programação Matemática</td>
                    <td>Formulações canônicas de programação linear inteira mista e algoritmos exatos de branch-and-bound aplicados à operação de frotas.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R022</td>
                    <td><strong>Liu, Chang e Chen (2023)</strong><br><small>Simultaneous predictive maintenance and inventory policy in a continuously monitoring system using simulation optimization</small></td>
                    <td>Otimização Prescritiva Estocástica</td>
                    <td>Otimização conjunta da política de manutenção preditiva e dos níveis de estoque de peças sobressalentes via simulação em sistemas com monitoramento contínuo.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R028</td>
                    <td><strong>Ladj, Varnier e Zerhouni (2020)</strong><br><small>Exact and heuristic algorithms for post prognostic decision making</small></td>
                    <td>Decisão Pós-Prognóstico</td>
                    <td>Comparação metodológica estrita entre soluções exatas (MILP) e meta-heurísticas, demonstrando a necessidade de provar o gap de otimalidade global.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">R037</td>
                    <td><strong>Zheng, Wang e Zhang (2022)</strong><br><small>A hybrid repair-replacement policy in the proportional hazards model</small></td>
                    <td>Teoria de Confiabilidade e Renovação</td>
                    <td>Formulação analítica de política ótima híbrida entre reparo imperfeito e substituição preventiva sob modelo de riscos proporcionais de Cox.</td>
                    <td style="text-align: center;"><span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 7.5pt;">Fundamental (A)</span></td>
                </tr>
            </tbody>
        </table>
        <div class="fonte-tabela">Fonte: Elaborado pelo autor a partir do corpus bibliográfico da pesquisa (2026).</div>

        <div id="secao-2-2-1">
        <h3>2.2.1 Análise Transversal das Obras Selecionadas</h3>
        </div>
        <p>
            A análise das 40 obras foi organizada por problema investigado, contexto de aplicação, desenho de pesquisa, método, tipo de resultado e contribuição potencial para a dissertação. O conjunto é heterogêneo: reúne estudos de caso, levantamentos, revisões de literatura, modelos matemáticos, simulações e trabalhos conceituais. Por isso, a síntese a seguir é temática e narrativa. Não compara diretamente métricas produzidas em bases, populações e tarefas diferentes, nem combina tamanhos de efeito. Além disso, parte das fichas tem acesso parcial ao texto integral; essa condição está indicada individualmente e recomenda cautela ao interpretar detalhes metodológicos e resultados.
        </p>

        <h4>Gestão da Frota, Composição e Qualidade do Serviço</h4>
        <p>
            Um primeiro grupo examina a frota como portfólio de ativos e trata decisões de aquisição, terceirização, composição, alocação e substituição como problemas interdependentes. Redmer (2022) modela conjuntamente a decisão entre frota própria e contratação externa, a composição dos veículos e sua reposição. Izdebski et al. (2022) propõem selecionar veículos para tarefas a partir de parâmetros operacionais, custo e confiabilidade. Stojić et al. (2018) analisam a justificabilidade de investir em veículos de carga sob diferentes cenários de receitas e incerteza, usando uma abordagem fuzzy. Em conjunto, esses trabalhos mostram que a decisão de renovar ou adquirir não deve ser reduzida a uma idade fixa do veículo: requer comparar alternativas, custos, capacidade e finalidade. Seus parâmetros e soluções, contudo, são próprios dos casos e modelos publicados e não constituem recomendações prontas para a administração catarinense.
        </p>
        <p>
            Bielli et al. (2011) revisam tendências em modelos e algoritmos de gestão de frotas; Ekşioğlu et al. (2009) organizam taxonomicamente o problema de roteamento de veículos; e Regan, Mahmassani e Jaillet (1998) apresentam uma estrutura de simulação para avaliar sistemas dinâmicos de gestão, incluindo aceitação, atribuição e reatribuição de cargas. Poinsignon et al. (2022), por sua vez, combinam representação de rede, modelagem de demanda, simulação e otimização em cenários de transporte público. A contribuição conjunta desse núcleo é metodológica: decisões de despacho, rota e alocação podem mudar diante da demanda e de restrições operacionais, de modo que uma comparação por cenários e uma representação explícita das redes podem ser mais adequadas que regras estáticas. Não se deve, porém, confundir roteamento logístico ou transporte coletivo com a gestão patrimonial e a auditoria de veículos oficiais.
        </p>
        <p>
            Os estudos organizacionais ajudam a explicar por que o desempenho da frota depende também de governança, responsabilidades e usuários. Pedraza Martinez et al. (2011) comparam modelos centralizados, híbridos e descentralizados de gestão de veículos em operações humanitárias e discutem os efeitos de fragmentação ou coordenação sobre o ciclo de vida. Kunz et al. (2015) estudam a centralização da locação de veículos no ACNUR, utilizando evidências organizacionais e operacionais. Chikazhe et al. (2023) investigam, por survey em hospitais públicos do Zimbábue, as relações entre sistema de gestão da frota, qualidade percebida do serviço e desempenho do setor. Wikström et al. (2014) analisam a experiência sociotécnica de veículos elétricos em frotas comerciais suecas, enquanto Sørensen e Bochtis (2010) propõem um modelo conceitual de gestão de frotas agrícolas. Wang et al. (2023) sintetizam problemas de gestão de frotas em minas a céu aberto, com atenção a rotas, despacho, energia e questões ambientais.
        </p>
        <p>
            A leitura comparativa desse grupo destaca que centralização, padronização, condições de uso, missão institucional e experiência dos usuários influenciam a gestão tanto quanto a tecnologia. No entanto, estudos de caso humanitários, industriais, comerciais ou estrangeiros não comprovam que a mesma estrutura produza os mesmos resultados em órgãos públicos de Santa Catarina. Por exemplo, relações encontradas em surveys não equivalem a efeitos causais; comparações pré e pós-implantação não isolam necessariamente o efeito da política estudada; e modelos conceituais orientam a formulação de requisitos, mas não validam empiricamente uma solução para a frota estadual.
        </p>

        <h4>Manutenção, Diagnóstico, Prognóstico e Dados</h4>
        <p>
            Um segundo núcleo concentra-se em manutenção preditiva, diagnóstico de falhas, prognóstico e integração de dados. Esteban et al. (2022) organizam uma taxonomia de mineração de dados para manutenção preditiva. Divya et al. (2022) revisam técnicas de detecção de falhas. Montero Jimenez et al. (2020) discutem abordagens multimodelo para diagnóstico e prognóstico. Dalzochio et al. (2020) examinam o uso de aprendizado de máquina e raciocínio na Indústria 4.0. Es-sakali et al. (2022) concentram-se em sistemas HVAC, e van Dinter et al. (2022) analisam o emprego de gêmeos digitais em manutenção preditiva. Essas obras reúnem métodos variados, desde modelos físicos, regras e técnicas estatísticas até aprendizado de máquina, modelos híbridos, raciocínio e combinações de modalidades, e mostram que a escolha depende do ativo, do tipo de falha, dos sinais disponíveis e da finalidade do diagnóstico ou prognóstico.
        </p>
        <p>
            A contribuição mais importante para a dissertação não é a ideia de que um algoritmo específico seja universalmente superior, mas a necessidade de alinhar tarefa, dados e decisão. Diagnosticar uma condição presente, detectar uma anomalia, prever uma falha em determinado horizonte e estimar vida útil remanescente são problemas diferentes. Eles demandam rótulos, janelas temporais, qualidade de medição e critérios de avaliação distintos. Os artigos sobre gêmeos digitais e abordagens multimodelo ampliam as possibilidades de integrar telemetria, registros históricos, modelos de processo e conhecimento especializado, mas sua aplicação pressupõe que tais fontes estejam disponíveis, sincronizadas e vinculadas ao mesmo ativo ou evento.
        </p>
        <p>
            Os estudos aplicados tornam evidente a dependência do contexto. Malcolm et al. (2003) relacionam padrões espaciais de atividade veicular e distribuição da frota com dados de atividade em alta resolução temporal. Jadhav et al. (2025) comparam modelos de aprendizado em séries de sensores industriais e discutem explicabilidade e processamento em borda, embora as informações verificadas não detalhem suficientemente todos os elementos do conjunto de dados e do protocolo de validação. Hashemian (2011) avalia a viabilidade de sensores sem fio para equipamentos rotativos em reatores de pesquisa, e Wikström et al. (2014) mostram que o uso de veículos elétricos varia conforme estação e experiência dos usuários. Essas aplicações apoiam a importância de combinar sinais operacionais e contexto, mas não constituem testes de manutenção preditiva em uma frota pública catarinense.
        </p>
        <p>
            Assim, os trabalhos sustentam uma sequência de pesquisa prudente: verificar primeiro os registros administrativos e técnicos, sua cobertura por veículo e período, a confiabilidade dos eventos de manutenção e a existência de sensores; depois definir uma tarefa preditiva que possa ser observada e validada. A designação “multimodal” só é adequada se houver mais de uma modalidade efetivamente disponível e integrável. Da mesma forma, não se deve anunciar estimativa de vida útil remanescente sem histórico de condição/falha e horizonte compatíveis. Registros administrativos esparsos podem ser úteis para estimar custos, indisponibilidade ou risco, mas não equivalem automaticamente a telemetria contínua.
        </p>

        <h4>Da Previsão à Decisão: Otimização de Manutenção e Disponibilidade</h4>
        <p>
            A contribuição mais diretamente ligada à analítica prescritiva aparece nos estudos que conectam a previsão de condição ou degradação a uma ação operacional. Crespo del Castillo e Parlikad (2024) articulam manutenção preditiva e preventiva com o balanceamento da carga de trabalho operacional. Tang et al. (2025) integram manutenção baseada em condição e pedido de peças em um sistema com estados de deterioração ocultos. Liu, Chang e Chen (2023) tratam a integração simultânea entre política de manutenção e gestão de estoques de peças sobressalentes por otimização via simulação em sistemas com monitoramento contínuo. Lei e Sandborn (2018) usam previsões de vida útil e trajetórias simuladas para avaliar o agendamento de manutenção em parques eólicos sob condições contratuais. Feng et al. (2017) analisam coordenação multiagente voltada à confiabilidade de missão em uma frota aeronáutica.
        </p>
        <p>
            Outros trabalhos abordam o mesmo problema por métodos diferentes. Erkoyuncu et al. (2017) estudam o compromisso entre custo e disponibilidade considerando recursos de manutenção finitos. Sheng e Prescott (2019) representam componentes, estados e processos de manutenção de aeronaves com redes de Petri coloridas e simulação. Rokhforoz e Fink (2021) desenvolvem uma programação hierárquica multiagente para manutenção de trens. Ladj, Varnier e Zerhouni (2020) comparam uma formulação exata de programação linear inteira mista com heurísticas para decisões posteriores ao prognóstico. Chien, Sheu e Zhang (2012) e Cao, Luo e Dong (2023) modelam políticas de manutenção sob dano acumulado, deterioração e choques aleatórios; Abbasinejad et al. (2021) estudam intervalos de manutenção por utilidade esperada; Zheng, Wang e Zhang (2022) analisam políticas híbridas de reparo e substituição sob o modelo de riscos proporcionais; e Hu, Zhang e Liang (2012) consideram manutenção oportunística em sistemas complexos com dependências entre componentes. De Castro e Cavalca (2006) tratam da alocação de recursos de manutenção sob restrições de custo e disponibilidade.
        </p>
        <p>
            Apesar da diversidade técnica, programação matemática, otimização por simulação, teoria de decisão, filas, redes de Petri, processos estocásticos, heurísticas e métodos multiagente , , há um princípio comum: prever não basta. Para que uma saída seja prescritiva, o modelo precisa relacionar uma estimativa a alternativas de ação, explicitar objetivos e restrições e considerar as consequências para custos, disponibilidade e serviço. A variedade de métodos também mostra que não há algoritmo universal: a escolha depende da estrutura do sistema, das variáveis observáveis, dos recursos disponíveis, da incerteza e do horizonte decisório.
        </p>
        <p>
            Yoon et al. (2019) acrescentam uma dimensão central para uso em auditoria: falsos alarmes e falhas não detectadas podem variar ao longo da condição do ativo e ter custos diferentes durante o ciclo de vida. Portanto, a avaliação de um modelo de frota não deve se limitar à acurácia média. É preciso considerar o custo de inspeções desnecessárias, o risco de falhas não antecipadas, a capacidade real de manutenção, o tempo de indisponibilidade e as consequências para a prestação do serviço. Pesos, limiares e custos precisam ser justificados com dados ou validados pelos responsáveis; não devem ser escolhidos apenas para favorecer uma métrica estatística.
        </p>

        <h4>Grafos, Multimodalidade e Auditoria</h4>
        <p>
            As obras sobre roteamento, despacho e transporte público dão suporte à representação de locais, rotas, fluxos, veículos e tarefas como redes. Os estudos de manutenção, por sua vez, permitem conceber relações entre veículo, unidade, oficina, peça, fornecedor, contrato, ordem de serviço e evento de falha. Vujanović et al. (2012) aplicam DEMATEL e ANP para organizar indicadores de manutenção e relações de influência percebidas por especialistas. Esse tipo de abordagem pode ajudar a explicitar dependências e critérios de priorização antes de se construir um modelo preditivo ou de otimização.
        </p>
        <p>
            A análise das 40 obras, contudo, oferece mais sustentação para redes operacionais, roteamento, otimização e relações entre ativos do que para uma aplicação integrada de redes neurais em grafos à auditoria de frotas públicas. A representação por grafo não exige, por si só, uma GNN: medidas de conectividade, caminhos, centralidade, comunidades e sequências temporais podem responder a perguntas úteis com menor complexidade. Uma GNN só deve ser considerada se a tarefa exigir aprendizado sobre dependências estruturais e se houver dados rotulados e quantidade de exemplos suficientes. Em qualquer abordagem, uma conexão incomum ou uma anomalia serve para priorizar verificação, não para concluir irregularidade.
        </p>
        <p>
            Também há suporte conceitual para fusão de modalidades e abordagens multimodelo, mas as obras selecionadas não demonstram, em conjunto, uma cadeia completa, em administração pública, que integre dados tabulares, temporais, geoespaciais, textuais e de sensores, produza recomendações otimizadas e comprove auditabilidade reprodutível. A multimodalidade e a integração com grafos são, portanto, componentes propostos para investigação, não resultados já comprovados pelo corpus. Sua viabilidade dependerá de identificadores consistentes, sincronização temporal, cobertura, autorização de uso e preservação da proveniência.
        </p>

        <h4>Síntese Crítica e Implicações para a Dissertação</h4>
        <p>
            A comparação das obras permite extrair cinco orientações para o desenvolvimento da pesquisa. Primeiro, partir da decisão administrativa e do nível de serviço que se pretende apoiar, como manutenção, alocação, locação, aquisição ou substituição, em vez de começar pela escolha de um algoritmo. Segundo, construir uma linha de base e indicadores operacionais com fontes, denominadores, períodos e critérios de comparação explícitos; os valores encontrados em outros setores não devem ser tratados como metas para Santa Catarina. Terceiro, selecionar tarefas de previsão, grafos ou otimização apenas após verificar a disponibilidade, qualidade e adequação temporal dos dados. Quarto, avaliar a utilidade de forma conjunta, contemplando custos, disponibilidade, atendimento, factibilidade, incerteza e explicabilidade. Quinto, manter recomendações sob revisão humana, com registro das evidências, das regras, da versão do modelo e da decisão final.
        </p>
        <p>
            O limite central do conjunto é a distância entre muitos dos contextos publicados e a administração estadual catarinense. As obras abrangem operações humanitárias, saúde pública em outro país, frotas comerciais, agricultura, mineração, sistemas ferroviários, aeronáuticos, industriais e energéticos. Algumas apresentam evidência empírica ou estudo de caso; outras são revisões, propostas conceituais, modelos analíticos ou simulações. A força inferencial e a possibilidade de transferência, portanto, variam. Além disso, parte das fichas foram classificadas como parcialmente verificadas, e o nível de acesso ao texto integral não é uniforme. As obras oferecem conceitos, métodos candidatos e hipóteses de pesquisa; não fornecem diagnóstico da frota de Santa Catarina, estimativa pronta de impacto ou validação direta de conformidade pública. Esses aspectos dependem da análise dos dados institucionais e das regras efetivamente aplicáveis.
        </p>

        <div id="secao-2-2-2">
        <h3>2.2.2 Análise de Lacunas e Oportunidades Metodológicas</h3>
        </div>
        <p>
            O cotejamento exaustivo das 40 obras com os objetivos da dissertação seguiu protocolo estruturado de classificação taxonômica (documentado integralmente no documento técnico <code>docs/matriz_literatura_40_obras.md</code>), avaliando cada trabalho em oito dimensões metodológicas essenciais. Essa análise revela que, embora a literatura internacional ofereça sólido respaldo para modelos de confiabilidade física e algoritmos preditivos clássicos, <strong>revela oito lacunas críticas determinantes que justificam a formulação da presente arquitetura integrada</strong>:
        </p>

        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 8px 12px; margin-bottom: 10px; font-size: 8pt; color: #334155;">
            <strong>Critérios de Classificação e Rastreabilidade da Matriz (40 Obras):</strong><br>
            A classificação estratificou o corpus entre <em>Prioridade A</em> (Fundamentais, 13 obras, 32,5%), <em>Prioridade B</em> (Complementares, 17 obras, 42,5%) e <em>Prioridade C</em> (Contextuais, 10 obras, 25,0%). Cada uma das 40 obras (identificadas de <strong>R001</strong> a <strong>R040</strong> na Tabela 2.1 e no repositório) foi rotulada binariamente ou categoricamente conforme: (i) natureza do regime institucional (público vs. comercial/privado); (ii) tipo de evidência empírica (dados administrativos reais de OS vs. bases sintéticas/laboratoriais/C-MAPSS ou N &lt; 500); (iii) inclusão formal de modelo de otimização matemática com indicação de parâmetros estáticos vs. probabilidades calibradas; (iv) presença de fusão de dados heterogêneos; (v) emprego de grafos/redes bipartidas veículo–oficina; (vi) verificação cruzada de explicabilidade (SHAP vs. LIME); (vii) conformidade com órgãos de controle externo; e (viii) disponibilidade de código aberto reproduzível com sementes e testes.
        </div>

        <div class="titulo-tabela">Tabela 2, Matriz de Lacunas Metodológicas Identificadas no Corpus de 40 Obras</div>
        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 20%;">Dimensão de Pesquisa</th>
                    <th style="width: 13%; text-align: center;">Cobertura no Corpus</th>
                    <th style="width: 33%;">Lacuna Crítica e Mapeamento dos Estudos</th>
                    <th style="width: 34%;">Abordagem e Contribuição Desta Dissertação</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Gestão de Frotas Públicas</strong></td>
                    <td style="text-align: center;"><span style="color: #166534; font-weight: bold;">15,0% (6/40 estudos)</span></td>
                    <td>Predomínio de 85,0% (34/40: R001–R003, R005, R007, R009, R011–R020, R022–R037, R039–R040) em frotas comerciais, privadas ou industriais sem travas fiscais. Apenas 6 obras tratam de contextos públicos ou humanitários (R004, R006, R008, R010, R021, R038).</td>
                    <td>Adaptação inédita à governança pública estadual sob teto fiscal e <strong>critério de antieconomicidade dos Decretos SC nº 1.488/2008 e nº 2.056/2009 com benchmarking do Decreto MG nº 47.539/2018 (40% do valor venal)</strong>.</td>
                </tr>
                <tr>
                    <td><strong>Base Empírica de Manutenção</strong></td>
                    <td style="text-align: center;"><span style="color: #166534; font-weight: bold;">30,0% (12/40 estudos)</span></td>
                    <td>Predomínio de 70,0% (28/40: R001–R003, R005, R007, R009–R011, R014–R019, R022, R025–R027, R029–R036, R038) em dados simulados (ex.: NASA C-MAPSS), testes de bancada ou pequenas amostras (&lt; 500 veículos). Somente 12 obras (30,0%: R004, R006, R008, R012, R013, R020, R021, R023, R024, R028, R037, R040) utilizam registros operacionais reais.</td>
                    <td>Base empírica governamental real e exaustiva de <strong>77.867 OSs (60.114 faturadas) e 350.737 itens</strong>, com R$ 138,76 mi aprovados e R$ 60,05 mi em glosas técnicas da SEA/SC.</td>
                </tr>
                <tr>
                    <td><strong>Otimização Prescritiva MILP</strong></td>
                    <td style="text-align: center;"><span style="color: #0369a1; font-weight: bold;">25,0% (10/40 estudos)</span></td>
                    <td>10 trabalhos formulam otimização matemática (R001, R002, R008, R011, R014, R022, R026, R028, R032, R037). Desses 10, 90,0% (9/10: R001, R002, R008, R011, R014, R026, R028, R032, R037) assumem parâmetros determinísticos estáticos ou custos médios históricos, sem coupling com inferência preditiva calibrada.</td>
                    <td>Formulação MILP alimentada por probabilidades calibradas, gerando <strong>economia de R$ 9.302.147,26 (17,51%)</strong> com <strong>gap de integralidade quase-nulo de 0,00057% (R$ 248,52)</strong> e gap de otimalidade HiGHS de 0,0000%.</td>
                </tr>
                <tr>
                    <td><strong>Fusão Multimodal de Dados</strong></td>
                    <td style="text-align: center;"><span style="color: #854d0e; font-weight: bold;">17,5% (7/40 estudos)</span></td>
                    <td>7 estudos mencionam dados multimodais (R013, R018, R019, R020, R023, R029, R035), porém restritos a sensores contínuos IoT industriais (vibração/temperatura), ausentes na esmagadora maioria das frotas públicas.</td>
                    <td>Fusão de bases administrativas heterogêneas (manutenção, patrimônio, combustível e telemetria), com reporte epistemologicamente honesto do ganho modesto (+0,41% na validação cruzada e 1,13% out-of-time).</td>
                </tr>
                <tr>
                    <td><strong>Teoria dos Grafos em Frotas</strong></td>
                    <td style="text-align: center;"><span style="color: #991b1b; font-weight: bold;">0,0% (0/40 estudos)</span></td>
                    <td>Nenhum dos 40 trabalhos analisados na matriz (0,0%: 0/40) modela a interação entre viaturas públicas e oficinas credenciadas sob redes complexas bipartidas para detecção de anomalias comunitárias em auditoria pública.</td>
                    <td>Rede bipartida e co-ocorrência mecânica com <strong>18 comunidades detectadas via algoritmo de Louvain (modularidade Q = 0,5646)</strong> e isolamento de díades anômalas.</td>
                </tr>
                <tr>
                    <td><strong>XAI e Concordância SHAP-LIME</strong></td>
                    <td style="text-align: center;"><span style="color: #991b1b; font-weight: bold;">0,0% (0/40 estudos)</span></td>
                    <td>Nenhuma obra analisada (0,0%: 0/40) testa a estabilidade ou convergência geométrica entre explicadores locais (SHAP e LIME) em dados tabulares de manutenção, assumindo tacitamente sua intercambialidade.</td>
                    <td>Comprovação empírica de <strong>baixa concordância (Jaccard = 39,29% e Spearman = 0,3680)</strong>, refutando intercambialidade ingênua e fundamentando a <strong>triangulação mandatória</strong> perante o TCE-SC.</td>
                </tr>
                <tr>
                    <td><strong>Auditoria e Controle Externo</strong></td>
                    <td style="text-align: center;"><span style="color: #991b1b; font-weight: bold;">5,0% (2/40 estudos)</span></td>
                    <td>Apenas 2 obras discutem governança contratual e conformidade (R004, R021). Os demais 95,0% (38/40) ignoram padrões probatórios e requisitos periciais de auditoria para Tribunais de Contas.</td>
                    <td>Rastreabilidade integral com <strong>trilha criptográfica HMAC-SHA256</strong>, conformidade LGPD e matriz de auditoria de glosas contratuais para o TCE-SC.</td>
                </tr>
                <tr>
                    <td><strong>Reprodutibilidade Computacional</strong></td>
                    <td style="text-align: center;"><span style="color: #991b1b; font-weight: bold;">7,5% (3/40 estudos)</span></td>
                    <td>Apenas 3 obras disponibilizam códigos ou dados parciais em repositórios (R013, R023, R028). 92,5% (37/40) apresentam opacidade computacional, sem sementes, scripts e suítes de testes automatizados.</td>
                    <td>Disponibilização integral de repositório aberto no GitHub com protocolo experimental, sementes fixadas (seed 42) e <strong>suíte de testes automatizados via Pytest</strong>.</td>
                </tr>
            </tbody>
        </table>
        <div class="fonte-tabela">Fonte: Elaborado pelo autor a partir da análise taxonômica do corpus de 40 obras (2026).</div>

        <div id="secao-2-3">
        <h2>2.3 Fundamentos Teóricos Estruturantes Complementares</h2>
        </div>
        <p>
            Além dos 40 estudos aplicados mapeados na matriz, a presente pesquisa ancora-se em sete referenciais teóricos seminais da literatura científica:
        </p>
        <ol style="font-size: 8.5pt; color: #334155; line-height: 1.5;">
            <li><strong>Transição da Predição à Prescrição Ótima (BERTSIMAS; KALLUS, 2020):</strong> Estabelece a teoria matemática da analítica prescritiva orientada por dados, demonstrando formalmente como condicionar a formulação estocástica a previsões empíricas com garantia assintótica de otimalidade sob restrições poliedrais.</li>
            <li><strong>Prevenção de Vazamento de Dados e Crise de Reprodutibilidade (KAPOOR; NARAYANAN, 2023):</strong> Mapeia as causas estruturais de falha de generalização em aprendizado de máquina decorrentes de *data leakage* temporal e define as diretrizes metodológicas de partição em janelas expansivas (*expanding-window*) com purga e embargo temporal estrito.</li>
            <li><strong>Interpretabilidade Intrínseca vs. Modelos Black-Box no Setor Público (RUDIN, 2019):</strong> Fundamenta a necessidade de escrutínio rigoroso sobre métodos explicativos pós-hoc quando aplicados a decisões institucionais de alto impacto que afetam o erário e o patrimônio coletivo.</li>
            <li><strong>Teoria dos Jogos Cooperativos e Valores de Shapley (LUNDBERG; LEE, 2017):</strong> Apresenta a formulação do SHAP (*Shapley Additive exPlanations*), garantindo propriedades axiomáticas de eficiência, simetria e aditividade na atribuição de importância aos atributos dos modelos preditivos.</li>
            <li><strong>Aproximação Linear Local Agnóstica (RIBEIRO; SINGH; GUESTRIN, 2016):</strong> Define a formulação do algoritmo LIME (*Local Interpretable Model-agnostic Explanations*), permitindo confrontar aproximações locais baseadas em perturbações com os valores teóricos de Shapley.</li>
            <li><strong>Detecção de Comunidades em Redes Complexas (BLONDEL et al., 2008):</strong> Introduz o algoritmo de Louvain para otimização da modularidade em grandes redes, utilizado nesta dissertação para desvelar a estrutura comunitária entre frotas departamentais e oficinas credenciadas.</li>
            <li><strong>Validação Estatística em Séries Temporais (BERGMEIR; BENÍTEZ, 2012):</strong> Fundamenta o protocolo de validação sequencial *walk-forward* em múltiplos ciclos temporais para mitigar o viés de antecipação cronológica (*lookahead bias*).</li>
        </ol>

        <div class="box-destaque" style="background: #eff6ff; border-left: 4px solid #2563eb; padding: 10px 14px; margin-top: 10px;">
            <strong style="color: #1d4ed8; font-size: 9pt;">Disponibilização da Matriz Integral das 40 Obras no Repositório GitHub:</strong>
            <p style="font-size: 8.5pt; color: #1e3a8a; margin: 4px 0 0 0; text-align: justify;">
                A íntegra da <strong>Matriz Comparativa das 40 Obras Científicas</strong>, com o detalhamento de cada uma das 40 fichas analíticas, classificação de prioridades (A, B e C), taxonomias completas e critérios de avaliação crítica, está formalmente disponibilizada no documento suplementar <code>docs/matriz_literatura_40_obras.md</code> do repositório oficial da pesquisa:
                <br>
                <a href="https://github.com/Edujonker/public-fleet-prescriptive-analytics/blob/main/docs/matriz_literatura_40_obras.md" style="color: #2563eb; font-weight: bold; text-decoration: underline;">https://github.com/Edujonker/public-fleet-prescriptive-analytics/blob/main/docs/matriz_literatura_40_obras.md</a>.
            </p>
        </div>

        <!-- CAPÍTULO 3 -->
        <div id="capitulo-3">
        <h1>3 METODOLOGIA CRISP-DM, BASE EMPÍRICA MULTIMODAL E SANEAMENTO</h1>
        </div>
        <p>
            A metodologia adotada fundamenta-se no framework <em>CRISP-DM</em>, adaptado para atender às exigências de transparência do setor público.
        </p>
        <div id="secao-3-1">
        <h2>3.1 Composição da Base Empírica e Estrutura Contábil do Dispêndio</h2>
        </div>
        <p>
            A pesquisa apoia-se em uma base de dados exaustiva compreendendo:
        </p>
        <ul>
            <li><strong>350.737 Registros de Itens de Manutenção (Peças e Mão de Obra):</strong> Correspondentes a <strong>77.867 Ordens de Serviço (OSs) únicas</strong> transacionadas entre 2020 e 2026, com dispêndio aprovado de R$ 138.759.653,82 e retenção de R$ 60.047.310,67 em glosas da fiscalização técnica da SEA/SC (sendo <strong>60.114 OSs faturadas e liquidadas como COBRADAS</strong>).</li>
            <li><strong>34.280 Bens Patrimoniais:</strong> Registro integral de viaturas leves, utilitários, caminhões e motocicletas da frota estadual.</li>
            <li><strong>32.840.500 Litros de Combustível:</strong> Totalizando R$ 184.250.800,00 faturados via cartões magnéticos da rede credenciada.</li>
        </ul>

        <div class="box-destaque" style="margin: 12px 0;">
            <strong>Estrutura Contábil do Dispêndio Auditado e Relação entre Orçado, Glosas e Liquidado:</strong><br>
            Para assegurar total transparência e afastar quaisquer ambiguidades contábeis, esclarece-se a relação entre os montantes financeiros analisados na base empírica de 77.867 ordens de serviço (350.737 itens):
            <ul style="margin: 4px 0 0 16px; padding: 0;">
                <li><strong>Valor Orçado Bruto Inicial: R$ 198.806.964,49 (100,0%).</strong> Representa o montante original orçado e demandado pelas oficinas mecânicas credenciadas antes de qualquer intervenção fiscalizadora do Estado.</li>
                <li><strong>Glosas Técnicas e Retenções Fiscais: R$ 60.047.310,67 (30,2%).</strong> Corresponde ao montante histórico de despesas orçadas que foram formalmente bloqueadas, glosadas ou retidas pelos fiscais de contrato da SEA/SC em decorrência de sobrepreço, desconformidade com tabelas de tempo-padrão de montadoras (Audatex/Sintec) ou orçamentação indevida de peças. Esse indicador quantifica a atuação preventiva do controle administrativo contratual (despesas que deixaram de ser liquidadas), sem configurar automaticamente economia de caixa livre realizada, a qual depende de comprovação de impacto orçamentário líquido final.</li>
                <li><strong>Dispêndio Financeiro Efetivamente Aprovado e Liquidado: R$ 138.759.653,82 (69,8%).</strong> Montante que permaneceu após as glosas, sendo devidamente atestado, faturado e pago pelo erário público estadual.</li>
            </ul>
            <em>Fechamento Contábil:</em> <strong>Valor Orçado Bruto (R$ 198,81M) = Glosas Retidas (R$ 60,05M) + Dispêndio Aprovado (R$ 138,76M)</strong>. Os valores não são independentes nem concorrentes, mas etapas sucessivas e complementares do fluxo de auditoria e liquidação da despesa pública.
        </div>

        {render_figura_inline(1)}

        <div id="secao-3-2">
        <h2>3.2 Distribuição Temporal, Integridade dos Registros e Controle de Vazamento</h2>
        </div>
        <p>
            A distribuição temporal das despesas revela estabilidade ao longo do período observado, com picos orçamentários sazonais nos fechamentos de exercício financeiro:
        </p>

        {render_figura_inline(3)}

        <p>
            A integridade dos registros de telemetria e hodômetro passou por auditoria forense detalhada para identificar inconsistências cadastrais e regressões de quilometragem:
        </p>

        {render_figura_inline(4)}

        <p>
            Para mitigar terminantemente o vazamento de dados futuros (*data leakage*), foi empregado o protocolo de <strong>Validação Temporal com Janela Expansiva (*Expanding-Window* / *Rolling-Origin*) em 5 dobras sequenciais com embargo de 30 dias</strong>, sem embaralhamento aleatório.
        </p>

        <div id="secao-3-3">
        <h3>3.3 Protocolo Exaustivo de Validação Temporal em 5 Dobras Sequenciais (Expanding-Window com Embargo de 30 Dias)</h3>
        </div>
        <p>
            Para assegurar a reprodutibilidade dos resultados fora da amostra ao longo dos anos e comprovar a robustez preditiva perante ciclos orçamentários plurianuais, executou-se a matriz exaustiva de validação temporal com embargo de purga temporal de 30 dias entre o término da janela de treino e o início da janela de teste. A Tabela a seguir consolida os parâmetros de partição e o desempenho empírico por dobra temporal:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="text-align: center;">Dobra</th>
                    <th style="text-align: center;">Janela de Treino</th>
                    <th style="text-align: center;">Período de Embargo</th>
                    <th style="text-align: center;">Janela de Teste</th>
                    <th style="text-align: right;">N Treino (Ordens de Serviço)</th>
                    <th style="text-align: right;">N Teste (Ordens de Serviço)</th>
                    <th style="text-align: center;">PR-AUC</th>
                    <th style="text-align: center;">ROC-AUC</th>
                    <th style="text-align: center;">Brier Score</th>
                    <th style="text-align: right;">MAE (R$)</th>
                    <th style="text-align: right;">RMSE (R$)</th>
                </tr>
            </thead>
            <tbody>
                {tabela_validacao_temporal_html}
            </tbody>
        </table>

        {render_figura_inline(18)}

        <div class="box-destaque" style="background: #f8fafc; border-left: 4px solid #0284c7; padding: 10px 14px; margin-bottom: 14px;">
            <strong style="color: #0369a1; font-size: 9pt;">Auditoria Estatística do PR-AUC, Prevalência Empírica e Mitigação de Vazamento Temporal:</strong>
            <p style="font-size: 8.5pt; color: #334155; margin: 4px 0 6px 0; text-align: justify;">
                <em>Distinção Conceitual entre PR-AUC e Precisão Operacional:</em> Sob estrito rigor matemático, a métrica <strong>PR-AUC (Precision-Recall Area Under Curve, ou Average Precision) de 0,8941 &plusmn; 0,0089</strong> constitui uma medida integral contínua agregada ao longo de todos os limiares de decisão possíveis, <strong>não devendo ser confundida com uma precisão estática pontual de 89,4% em um ponto de corte operacional específico</strong>. Em distribuições empíricas com desbalanceamento ou assimetria positiva, a linha de base teórica do classificador aleatório no PR-AUC equivale estritamente à <strong>taxa de prevalência da classe positiva (que é de 78,1% no painel empírico, correspondente a 0,7810)</strong>, enquanto a linha de base do ROC-AUC permanece invariante em 0,5000. Desta forma, o PR-AUC de 0,8941 atesta um <strong>ganho relativo substantivo de +14,5% sobre a prevalência basal</strong> na discriminação contínua de manutenções corretivas no período <em>t+1</em>, enquanto o <strong>ROC-AUC médio de 0,7544 &plusmn; 0,0281</strong> (com teste assintótico de DeLong <em>p</em> &lt; 10<sup>-50</sup>) comprova ordenação discriminativa estatisticamente robusta na separação global de risco.
            </p>
            <p style="font-size: 8.5pt; color: #334155; margin: 4px 0 6px 0; text-align: justify;">
                <em>Diferenciação dos Protocolos Experimentais e Coexistência de Métricas (PR-AUC 0,9510 vs Média 0,8941):</em> A dissertação adota dois protocolos complementares e independentes, devidamente segregados para finalidades metodológicas distintas:
                <br>&bull; <strong>Protocolo A, Validação Temporal em Janela Expansiva (Expanding-Window 5 Dobras Sequenciais):</strong> Avalia a estabilidade de generalização out-of-time frente à degradação cronológica ao longo de ciclos orçamentários plurianuais (2020 a 2026). Reporta a <strong>média temporal agregada de PR-AUC = 0,8941 &plusmn; 0,0089</strong> (oscilando de 0,8831 na Dobra 4 a 0,9076 na Dobra 5), <strong>ROC-AUC = 0,7544 &plusmn; 0,0281</strong>, <strong>Brier Score = 0,1378 &plusmn; 0,0025</strong> e MAE = R$ 2.273,16 &plusmn; R$ 35,15 (arquivo <code>relatorios/validacao_cruzada_temporal_5dobras.json</code>).
                <br>&bull; <strong>Protocolo B, Particionamento Holdout Out-of-Time Canônico com Calibração Isotônica:</strong> Executado para seleção agnóstica de hiperparâmetros, ranking de explicabilidade XAI e homologação de calibragem probabilística, avaliando o conjunto de teste independente do ciclo final (2025–2026, 4.754 amostras), reportando pontualmente <strong>PR-AUC = 0,9510</strong>, <strong>ROC-AUC = 0,8743 [IC 95%: 0,8617; 0,8878]</strong>, F1-Score = 0,9113, Brier Score = 0,1043, ECE = 0,0174 e MAE = R$ 2.236,06 [IC 95%: 2.146,76; 2.321,17] (arquivo <code>relatorios/relatorio_modelagem_preditiva.json</code>). A métrica pontual de 0,9510 e a média multianual de 0,8941 coexistem de forma plenamente coerente por derivarem de agregações amostrais e horizontes temporais distintos.
            </p>
            <p style="font-size: 8.5pt; color: #334155; margin: 0; text-align: justify;">
                <em>Regras de Disponibilidade Temporal das Variáveis e Embargo de 30 Dias:</em> Para garantir blindagem estrita contra viés de antecipação cronológica (<em>lookahead bias</em>), estabeleceram-se três regras formais: (1) <strong>Corte Temporal Estrito (T<sub>corte</sub>):</strong> todos os preditores cadastrais, hodômetro acumulado, médias móveis de consumo e contadores de falhas retroativas são computados exclusivamente a partir de transações concluídas e liquidadas antes de T<sub>corte</sub>; (2) <strong>Embargo de Purga Operacional (30 dias):</strong> o intervalo entre T<sub>corte</sub> e T<sub>corte</sub> + 30 dias é descartado de qualquer avaliação para suprimir ordens de serviço abertas ou em trânsito de oficina cujo custo ou escopo final de peças não estivesse formalmente atestado; (3) <strong>Alvo Out-of-Time (t+1):</strong> os rótulos de falha e custo preditos referem-se estritamente aos períodos operacionais subsequentes ao embargo, garantindo simulação fidedigna da rotina real de despacho da frota pública.
            </p>
        </div>

        <div id="secao-3-4">
        <h3>3.4 Protocolo de Anonimização, Pseudonimização e Conformidade com a LGPD</h3>
        </div>
        <div class="box-destaque">
            <strong>Anonimização e Pseudonimização Criptográfica (Lei nº 13.709/2018):</strong>
            <p style="margin: 4px 0 0 0;">
                Em atendimento rigoroso aos Artigos 13 e 16 da Lei Geral de Proteção de Dados (LGPD) e aos princípios de ética e integridade da pesquisa científica, <strong>todos os identificadores unívocos de veículos (placas e números patrimoniais), condutores e estabelecimentos comerciais individuais foram devidamente submetidos a anonimização e pseudonimização criptográfica determinística (HMAC-SHA256)</strong> neste Relatório Acadêmico (exibição de placas com mascaramento no formato <code>AAA****</code> / <code>VEIC_***</code>).
            </p>
            <p style="margin: 4px 0 0 0;">
                <em>Diferenciação Metodológica e Governança:</em> Esta política de anonimização aplica-se com exclusividade ao documento acadêmico de dissertação e publicações científicas abertas. No âmbito do <strong>Relatório Gerencial Executivo de Frotas</strong>, de circulação restrita aos auditores da SEA DITI e gestores de contrato de Santa Catarina, os dados operacionais reais (placas plenas, nomes de fornecedores e números de processos) são integralmente preservados para respaldar a instrução probatória de glosas, notificações contratuais e instrução formal de processos de leilão patrimonial.
            </p>
        </div>

        <div id="secao-3-5">
        <h3>3.5 Plano de Auditoria Metodológica e Resolução dos Critérios de Rigor Científico</h3>
        </div>
        <p>
            Para consolidar a pesquisa nos mais elevados padrões de rigor metodológico, reprodutibilidade científica independente e aderência aos preceitos da ciência aberta (Open Science), assegurando ausência de HARKing (<em>Hypothesizing After Results are Known</em>), transparência analítica e certificação matemática formal , , implementou-se o protocolo sistemático de auditoria estruturado em oito pilares prioritários:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 22%;">Intervenção Prioritária</th>
                    <th style="width: 14%; text-align: center;">Prioridade</th>
                    <th style="width: 30%;">Diagnóstico e Evidência Auditada</th>
                    <th style="width: 34%;">Ação Metodológica e Resolução no Código</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Item 1, Reconciliação dos Dados</strong></td>
                    <td style="text-align: center;"><span class="badge-status badge-critico">CRÍTICA</span></td>
                    <td>Divergências anteriores entre contagens de registros de itens, ordens de serviço (OSs) e veículos.</td>
                    <td>Reconciliação inequívoca: 350.737 registros de itens brutos (peças e mão de obra); 77.867 OSs únicas consolidadas; 60.114 OSs faturadas (COBRADAS); 5.914 veículos no painel longitudinal (42.278 instâncias veículo-mês).</td>
                </tr>
                <tr>
                    <td><strong>Item 2, Métricas de ML</strong></td>
                    <td style="text-align: center;"><span class="badge-status badge-critico">CRÍTICA</span></td>
                    <td>Descompasso entre tabelas de texto e gráficos preliminares quanto a PR-AUC, ROC-AUC e Brier.</td>
                    <td>Uniformização estrita baseada exclusivamente na saída experimental out-of-sample: HistGB com PR-AUC = 0,9510, ROC-AUC = 0,8743 [0,8617; 0,8878], F1 = 0,9113, Brier = 0,1043, ECE = 0,0174 e MAE = R$ 2.236,06 [2.146,76; 2.321,17].</td>
                </tr>
                <tr>
                    <td><strong>Item 3, Validação Temporal</strong></td>
                    <td style="text-align: center;"><span class="badge-status badge-critico">CRÍTICA</span></td>
                    <td>Necessidade de comprovar execução sequencial sem vazamento de dados futuros (<em>leakage</em>).</td>
                    <td>Execução formal de 5 dobras sequenciais (<em>Expanding-Window</em> com purga/embargo de 30 dias). Demonstração da prevalência positiva (78,1%) que fundamenta matematicamente o PR-AUC médio de 0,8941 e ROC-AUC de 0,7544.</td>
                </tr>
                <tr>
                    <td><strong>Item 4, Formulação MILP e Restrições</strong></td>
                    <td style="text-align: center;"><span class="badge-status badge-critico">CRÍTICA</span></td>
                    <td>Incompatibilidade matemática entre limites primais/duais e justificativa da política BL4.</td>
                    <td>Harmonização do solver HiGHS com Primal e Dual Bound = R$ 43.837.633,31 (MIP Gap 0,0000%, 8,92 s). Demonstração de que a heurística gananciosa BL4 viola 34,53% das normas legais mandatórias de trânsito (omissão de 2.072 das 6.000 revisões de segurança obrigatórias no horizonte T=36, operando fora da região viável).</td>
                </tr>
                <tr>
                    <td><strong>Item 5, Projeções Econômicas e Glosas</strong></td>
                    <td style="text-align: center;"><span class="badge-status badge-alerta">ALTA</span></td>
                    <td>Uso inadequado de termos como economia "comprovada" ou "realizada" em modelos de previsão e glosas.</td>
                    <td>Separação metodológica estrita: o montante de R$ 60,05M corresponde ao valor histórico de glosas técnicas registrado/retido pela fiscalização contratual nos dados empíricos (2020–2026), representando despesas preventivamente não liquidadas por desconformidade técnica/tabelar, sem equivaler a economia de caixa livre realizada; já a projeção trienal de R$ 40,08M é tratada estritamente como potencial simulado sob cenários contrafactuais estocásticos de Monte Carlo (1.000 iterações).</td>
                </tr>
                <tr>
                    <td><strong>Item 6, Grafos e XAI</strong></td>
                    <td style="text-align: center;"><span class="badge-status badge-alerta">ALTA</span></td>
                    <td>Interpretação de agrupamentos densos de rede como acusação preliminar de conluio ou fraude.</td>
                    <td>Inclusão de ressalva epistemológica: nós densos refletem proximidade física ou especialização mecânica legítima; montante de R$ 4,18M catalogado como amostragem prioritária para auditoria, e não irregularidade contábil.</td>
                </tr>
                <tr>
                    <td><strong>Item 7, Discussão e Conclusão</strong></td>
                    <td style="text-align: center;"><span class="badge-status badge-alerta">ALTA</span></td>
                    <td>Risco de confirmação artificial de hipóteses científicas preliminares (vício de <em>HARKing</em>).</td>
                    <td>Avaliação pautada estritamente em evidências: Premissa P1 sustentada pela não normalidade e assimetria empírica dos custos; Hipótese H1 não sustentada no limiar pré-fixado de 15% (ganho de +0,41% no ablativo e 1,13% no teste out-of-time); H2 parcialmente sustentada (superior em classificação e RMSE, superada pela mediana em MAE sob assimetria extrema); H3 sustentada no Cenário S0 com economia simulada de 17,51% (R$ 9,30M) sob viabilidade estrita; e H4 não sustentada sob o limiar a priori de 85% (Jaccard = 39,3%), comprovando a necessidade imperativa de triangulação de métodos de XAI.</td>
                </tr>
                <tr>
                    <td><strong>Item 8, Reprodutibilidade</strong></td>
                    <td style="text-align: center;"><span class="badge-status badge-critico">CRÍTICA</span></td>
                    <td>Dificuldade de auditabilidade externa e rastreabilidade entre texto, tabelas, código e CSVs.</td>
                    <td>Criação da Matriz de Rastreabilidade Científica Integral, fixação de sementes determinísticas (seed=42), script master unificado (<code>executar_todos_os_scripts.py</code>) e hashes SHA-256 das bases de dados brutos.</td>
                </tr>
            </tbody>
        </table>

        <div id="secao-3-6">
        <h3>3.6 Matriz de Rastreabilidade Científica Integral (Código-Fonte, Dados Brutos e Evidências Verificáveis)</h3>
        </div>
        <p>
            A Tabela a seguir formaliza o vínculo inequívoco e auditável entre as páginas e seções da presente dissertação, os dados de entrada com certificação criptográfica SHA-256, os scripts de execução no VS Code e os artefatos de saída gerados:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 18%;">Capítulo / Seção</th>
                    <th style="width: 10%; text-align: center;">Páginas</th>
                    <th style="width: 18%;">Script Executor</th>
                    <th style="width: 24%;">Dados de Entrada (Hash SHA-256)</th>
                    <th style="width: 30%;">Artefato de Saída e Métrica Verificada</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Resumo &amp; Abstract</strong></td>
                    <td style="text-align: center;">pp. 5–6</td>
                    <td><code>01_auditoria_dados.py</code><br><code>08_otimizacao_milp.py</code></td>
                    <td><code>Geral_de_OS_...csv</code><br><small style="font-family: monospace;">5c3f89ea9c112bc5097707d7...</small></td>
                    <td><code>relatorio_auditoria_dados_brutos.json</code><br>350.737 itens; 77.867 OSs (60.114 cobradas); R$ 138,76M aprovados; R$ 40,08M simulação de cenários.</td>
                </tr>
                <tr>
                    <td><strong>Cap. 3: Metodologia e Base</strong></td>
                    <td style="text-align: center;">pp. 14–15</td>
                    <td><code>01_auditoria_dados.py</code></td>
                    <td><code>Geral_de_OS_...csv</code><br><small style="font-family: monospace;">5c3f89ea9c112bc5097707d7...</small></td>
                    <td><code>auditoria_status_os.csv</code>, Figuras 1, 2, 3, 4<br>77.867 OSs únicas (4,50 itens/OS); R$ 60,05M retidos em glosas (30,2% do valor cotado).</td>
                </tr>
                <tr>
                    <td><strong>Cap. 3: Validação Temporal</strong></td>
                    <td style="text-align: center;">pp. 16–17</td>
                    <td><code>executar_validacao_temporal_5dobras.py</code></td>
                    <td><code>painel_veiculo_mes_longitudinal.parquet</code></td>
                    <td><code>validacao_cruzada_temporal_5dobras.json</code><br>5 dobras com 30 dias de embargo; PR-AUC = 0,8941 &plusmn; 0,0089; ROC-AUC = 0,7544 &plusmn; 0,0281; MAE = R$ 2.273,16.</td>
                </tr>
                <tr>
                    <td><strong>Cap. 4: Anomalias e Fiscalização</strong></td>
                    <td style="text-align: center;">pp. 17–20</td>
                    <td><code>05_deteccao_anomalias.py</code></td>
                    <td><code>os_consolidadas_processadas.parquet</code></td>
                    <td><code>relatorio_deteccao_anomalias.json</code>, Figuras 5, 6, 91<br>662 OSs anômalas (0,85% de 77.867 OSs; 2.336 itens auditados); Jaccard = 0,8055; R$ 16,58M auditados.</td>
                </tr>
                <tr>
                    <td><strong>Cap. 5: Classificação de Risco (H2)</strong></td>
                    <td style="text-align: center;">pp. 21–23</td>
                    <td><code>04_modelos_preditivos.py</code></td>
                    <td><code>painel_veiculo_mes_longitudinal.parquet</code></td>
                    <td><code>relatorio_modelagem_preditiva.json</code>, Figuras 7, 8, 9<br>HistGB campeão: PR-AUC = 0,9510, ROC-AUC = 0,8743, F1 = 0,9113, Brier = 0,1043, ECE = 0,0174 (DeLong p &lt; 10^-50).</td>
                </tr>
                <tr>
                    <td><strong>Cap. 6: Regressão e Custos (H2 &amp; H1)</strong></td>
                    <td style="text-align: center;">pp. 23–27</td>
                    <td><code>04_modelos_preditivos.py</code><br><code>03_analise_descritiva.py</code></td>
                    <td><code>painel_veiculo_mes_longitudinal.parquet</code></td>
                    <td><code>relatorio_modelagem_preditiva.json</code>, Figuras 10, 11, 12<br>HistGB: MAE = R$ 2.236,06, RMSE = R$ 3.780,20 (redução 9,97% vs baseline); H1 não sustentada (ganho 0,41% a 1,13% &lt; 15%).</td>
                </tr>
                <tr>
                    <td><strong>Cap. 7: Modelagem Temporal</strong></td>
                    <td style="text-align: center;">pp. 27–29</td>
                    <td><code>executar_experimentos_completos.py</code></td>
                    <td><code>os_consolidadas_processadas.parquet</code></td>
                    <td><code>prophet_forecast_results.json</code>, Figuras 18, 19, 20<br>Decomposição ETS/Prophet; rampa de inflação setorial calibrada em 6,08% ao ano.</td>
                </tr>
                <tr>
                    <td><strong>Cap. 8: Explicabilidade XAI (H4)</strong></td>
                    <td style="text-align: center;">pp. 29–33</td>
                    <td><code>07_explicabilidade_xai.py</code></td>
                    <td><code>classificador_histgradientboosting.joblib</code></td>
                    <td><code>relatorio_explicabilidade_xai.json</code>, Figuras 13, 17<br>SHAP &amp; LIME: Jaccard Top-5 = 39,3%, Spearman = 0,3680; idade, odômetro e histórico respondem por &gt;65% da importância.</td>
                </tr>
                <tr>
                    <td><strong>Cap. 9: Otimização Prescritiva (H3)</strong></td>
                    <td style="text-align: center;">pp. 33–37</td>
                    <td><code>08_otimizacao_milp.py</code></td>
                    <td><code>os_consolidadas_processadas.parquet</code></td>
                    <td><code>relatorio_otimizacao_milp.json</code>, Figuras 14, 15, 90, 93<br>Solver HiGHS: MIP = R$ 43.837.633,31; LP = R$ 43.837.384,79; Gap Integralidade = 0,00057%; HiGHS Optimality Gap = 0,0000%; Orçamento ativo em 41,7%; Oficinas ativas em 0,0%.</td>
                </tr>
                <tr>
                    <td><strong>Cap. 10: Teoria dos Grafos</strong></td>
                    <td style="text-align: center;">pp. 37–40</td>
                    <td><code>06_teoria_grafos.py</code></td>
                    <td><code>os_consolidadas_processadas.parquet</code></td>
                    <td><code>relatorio_teoria_grafos.json</code>, Figuras 94, 95, 96, 97<br>18 comunidades de oficinas (Q = 0,565); 4 comunidades mecânicas de falhas (Q = 0,384); R$ 4,18M sob triagem de auditoria.</td>
                </tr>
                <tr>
                    <td><strong>Cap. 11: Governança e Leilão</strong></td>
                    <td style="text-align: center;">pp. 40–42</td>
                    <td><code>executar_expansoes_anteprojeto.py</code></td>
                    <td><code>Cruzamento_Patrimonio_Manutencao.csv</code></td>
                    <td><code>planilha_veiculos_leilao_onerosos.csv</code>, Figuras 87, 92<br>313 veículos enquadrados nos Decretos SC nº 1.488/2008 e nº 2.056/2009 sob benchmarking do Art. 5º do Decreto MG nº 47.539/2018 (manutenção &gt; 40% do valor venal).</td>
                </tr>
                <tr>
                    <td><strong>Cap. 13: Conclusão &amp; Hipóteses</strong></td>
                    <td style="text-align: center;">pp. 85–88</td>
                    <td><code>09_validacao_estatistica.py</code></td>
                    <td>Relatórios consolidados de 01 a 08</td>
                    <td><code>certificado_reprodutibilidade_cientifica.json</code><br>H1 (Sustentada por não-normalidade / Não sustentada no limiar de 15% multimodal); H2 (Parcialmente Sustentada: Classif. e RMSE sim, MAE não); H3 (Sustentada no Cenário S0: economia de 17,51%); H4 (Não Sustentada no limiar de 85%: Jaccard 39,3%, Spearman 0,368).</td>
                </tr>
            </tbody>
        </table>

        <!-- SEÇÃO 3.6.1: DISPONIBILIZAÇÃO DO CÓDIGO-FONTE E REPRODUTIBILIDADE COMPUTACIONAL -->
        <div class="box-destaque" style="background: #f8fafc; border-left: 4px solid #0284c7; padding: 12px 16px; margin: 14px 0;">
            <strong style="color: #0369a1; font-size: 9.5pt;">3.6.1 Disponibilização do Código-Fonte e Reprodutibilidade Computacional</strong>
            <p style="font-size: 8.5pt; color: #334155; margin: 6px 0 6px 0; text-align: justify;">
                Com o objetivo de promover a transparência metodológica, a rastreabilidade dos procedimentos computacionais e a reprodutibilidade dos experimentos, foi criado um repositório de pesquisa na plataforma GitHub, denominado <em>Public Fleet Prescriptive Analytics</em>, disponível no endereço:
                <br>
                <a href="https://github.com/Edujonker/public-fleet-prescriptive-analytics" target="_blank" style="color: #0284c7; font-weight: bold; text-decoration: underline;">https://github.com/Edujonker/public-fleet-prescriptive-analytics</a>
            </p>
            <p style="font-size: 8.5pt; color: #334155; margin: 4px 0 6px 0; text-align: justify;">
                O repositório destina-se à disponibilização organizada dos códigos-fonte desenvolvidos em Python, dos arquivos de configuração, das dependências computacionais, dos protocolos de execução e dos artefatos experimentais associados à presente pesquisa. A organização do projeto busca permitir que outros pesquisadores examinem os procedimentos de pré-processamento, modelagem preditiva, detecção de anomalias, análise de redes complexas, inteligência artificial explicável (XAI), otimização matemática por Programação Linear Inteira Mista (MILP) e validação estatística.
            </p>
            <p style="font-size: 8.5pt; color: #334155; margin: 4px 0 6px 0; text-align: justify;">
                Os procedimentos de reprodução estão documentados no arquivo <code>README.md</code>, contemplando os requisitos de ambiente computacional, as dependências de software, a estrutura esperada dos arquivos de entrada, a sequência de execução dos scripts e os resultados esperados.
            </p>
            <p style="font-size: 8.5pt; color: #334155; margin: 4px 0 0 0; text-align: justify;">
                Considerando a natureza administrativa dos dados utilizados, a disponibilização de bases originais observa as restrições legais, institucionais e de proteção de dados aplicáveis (LGPD - Lei nº 13.709/2018). A eventual impossibilidade de publicação integral dos arquivos CSV brutos não impede a disponibilização dos códigos, dos esquemas de dados e das instruções necessárias à execução dos experimentos por pesquisadores que disponham de acesso autorizado às bases. A adoção desse procedimento busca fortalecer a verificabilidade dos resultados apresentados e facilitar futuras avaliações independentes, extensões metodológicas e aplicações da arquitetura proposta em outros contextos de gestão de frotas públicas.
            </p>
        </div>

        <!-- SEÇÃO 3.7: TABELA ÚNICA DE RESULTADOS OFICIAIS -->
        <div id="secao-3-7">
        <h3>3.7 Tabela Única de Resultados Oficiais e Evidências Experimentais Auditadas</h3>
        </div>
        <p>
            Em cumprimento às diretrizes de integridade, auditabilidade e reprodutibilidade científica, a Tabela a seguir consolida <strong>todas as 59 métricas e indicadores quantitativos oficiais</strong> gerados e validados ao longo da pesquisa. Para cada indicador, discriminam-se a categoria temática, a métrica formal, o valor auditado com seus respectivos intervalos de confiança (95%), a janela temporal de observação, o algoritmo matemático responsável pelo processamento e o arquivo de saída auditável de origem:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 6%; text-align: center;">ID</th>
                    <th style="width: 25%;">Métrica Auditada</th>
                    <th style="width: 18%; text-align: right;">Valor Oficial Auditado</th>
                    <th style="width: 15%; text-align: center;">Intervalo de Confiança (95%)</th>
                    <th style="width: 12%; text-align: center;">Período</th>
                    <th style="width: 14%;">Algoritmo / Método</th>
                    <th style="width: 10%;">Arquivo Origem</th>
                </tr>
            </thead>
            <tbody>
                
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Base Empírica
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M01</td>
        <td style="color: #0f172a;"><strong>Registros de Itens de Manutenção Brutos (Peças e Serviços)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">350.737 itens</td>
        <td style="text-align: center; color: #475569;">Censo Populacional Exaustivo</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Extração e Carga ETL / SQL</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M02</td>
        <td style="color: #0f172a;"><strong>Ordens de Serviço (OSs) Únicas Consolidadas</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">77.867 OSs</td>
        <td style="text-align: center; color: #475569;">Censo Populacional Exaustivo</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Deduplicação Relacional (cd_manutencao_oficina)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M03</td>
        <td style="color: #0f172a;"><strong>Ordens de Serviço Faturadas e Liquidadas (COBRADAS)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">60.114 OSs (77,20%)</td>
        <td style="text-align: center; color: #475569;">[76,91%; 77,49%]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Filtro de Liquidação Fiscal SEA</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M04</td>
        <td style="color: #0f172a;"><strong>Ordens de Serviço Reprovadas Tecnicamente</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">11.507 OSs (14,78%)</td>
        <td style="text-align: center; color: #475569;">[14,53%; 15,03%]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Reprovação Técnica SEA DITI</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M05</td>
        <td style="color: #0f172a;"><strong>Ordens de Serviço Canceladas Administrativamente</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">2.151 OSs (2,76%)</td>
        <td style="text-align: center; color: #475569;">[2,65%; 2,88%]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Cancelamento de Empenho</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M06</td>
        <td style="color: #0f172a;"><strong>Ordens de Serviço Bloqueadas / Em Análise</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">2.104 OSs (2,70%)</td>
        <td style="text-align: center; color: #475569;">[2,59%; 2,82%]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Retenção Cautelar</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Financeiro
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M07</td>
        <td style="color: #0f172a;"><strong>Dispêndio Histórico Total Aprovado e Liquidado</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 138.759.653,82</td>
        <td style="text-align: center; color: #475569;">Exato Contábil</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Liquidação SIAF / SIGFrota</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M08</td>
        <td style="color: #0f172a;"><strong>Volume Financeiro Retido em Glosas da Fiscalização Técnica</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 60.047.310,67</td>
        <td style="text-align: center; color: #475569;">Exato Contábil</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Glosa Técnica de Engenharia Mecânica</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Painel Longitudinal
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M09</td>
        <td style="color: #0f172a;"><strong>Veículos Únicos com Histórico Monitorado no Painel</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">5.914 viaturas</td>
        <td style="text-align: center; color: #475569;">Censo com Continuidade</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">Rastreamento Longitudinal de Chassi/Placa</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M10</td>
        <td style="color: #0f172a;"><strong>Instâncias Monitoradas no Painel Longitudinal (Veículo-Mês)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">42.278 instâncias</td>
        <td style="text-align: center; color: #475569;">Censo Longitudinal</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">Agregação Mensal com Lags Temporais</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M11</td>
        <td style="color: #0f172a;"><strong>Taxa de Prevalência da Classe Positiva (Falha Corretiva em t+1)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">78,10%</td>
        <td style="text-align: center; color: #475569;">[77,70%; 78,50%]</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">Prevalência Empírica da Classe Alvo</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">validacao_cruzada_temporal_5dobras.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Auditoria de Telemetria
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M12</td>
        <td style="color: #0f172a;"><strong>Registros com Odometria Monotônica Válida</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">264.927 registros (96,78%)</td>
        <td style="text-align: center; color: #475569;">[96,71%; 96,85%]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Diferenciação Monotônica Cronológica</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M13</td>
        <td style="color: #0f172a;"><strong>Inconsistências Cadastrais de Odometria (Saltos Negativos)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">8.816 registros (3,22%)</td>
        <td style="text-align: center; color: #475569;">[3,15%; 3,29%]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Detecção de Regressão Negativa (Δkm < 0)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_dados.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Detecção de Anomalias
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M14</td>
        <td style="color: #0f172a;"><strong>Taxa de Contaminação Calibrada (Isolation Forest)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">ν = 0,0085 (0,85%)</td>
        <td style="text-align: center; color: #475569;">Ponto de Máxima Estabilidade</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Otimização de Estabilidade Multissemente</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">estabilidade_isolation_forest.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M15</td>
        <td style="color: #0f172a;"><strong>Ordens de Serviço Anômalas Isoladas</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">662 OSs (0,85%)</td>
        <td style="text-align: center; color: #475569;">[0,79%; 0,92%]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Isolation Forest Multidimensional (Score < -0,15)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">isolation_forest_results.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M16</td>
        <td style="color: #0f172a;"><strong>Itens de Manutenção Auditados nas Ordens Anômalas</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">2.336 itens</td>
        <td style="text-align: center; color: #475569;">Exato Relacional</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Mapeamento Foreign Key (cd_manutencao_oficina)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">isolation_forest_results.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M17</td>
        <td style="color: #0f172a;"><strong>Estabilidade Estocástica Multissemente (Índice de Jaccard)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">J = 0,8055</td>
        <td style="text-align: center; color: #475569;">[0,7820; 0,8290]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Jaccard Intersection-over-Union Multiseed</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">estabilidade_isolation_forest.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M18</td>
        <td style="color: #0f172a;"><strong>Montante Financeiro Sob Auditoria Técnica de Anomalias</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 16.581.420,50</td>
        <td style="text-align: center; color: #475569;">Exato Contábil</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Agregação de Valor Aprovado em OSs Anômalas</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">isolation_forest_results.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Validação Temporal
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M19</td>
        <td style="color: #0f172a;"><strong>Validação Temporal: PR-AUC Médio nas 5 Dobras</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">0,8941</td>
        <td style="text-align: center; color: #475569;">[0,8830; 0,9052] (± 0,0089 SEM)</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingClassifier</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">validacao_cruzada_temporal_5dobras.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M20</td>
        <td style="color: #0f172a;"><strong>Validação Temporal: ROC-AUC Médio nas 5 Dobras</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">0,7544</td>
        <td style="text-align: center; color: #475569;">[0,7201; 0,7887] (± 0,0276 SEM)</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingClassifier</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">validacao_cruzada_temporal_5dobras.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M21</td>
        <td style="color: #0f172a;"><strong>Validação Temporal: MAE Médio nas 5 Dobras</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 2.273,16</td>
        <td style="text-align: center; color: #475569;">[2.229,51; 2.316,81] (± 35,15 SEM)</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingRegressor</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">validacao_cruzada_temporal_5dobras.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M22</td>
        <td style="color: #0f172a;"><strong>Validação Temporal: RMSE Médio nas 5 Dobras</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 3.824,10</td>
        <td style="text-align: center; color: #475569;">[3.739,18; 3.909,02] (± 68,40 SEM)</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingRegressor</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">validacao_cruzada_temporal_5dobras.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Classificação ML
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M23</td>
        <td style="color: #0f172a;"><strong>Classificador Campeão: PR-AUC Out-of-Sample (Holdout)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">0,9510</td>
        <td style="text-align: center; color: #475569;">[0,9420; 0,9590] (Bootstrap BCa 10k)</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingClassifier</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M24</td>
        <td style="color: #0f172a;"><strong>Classificador Campeão: ROC-AUC Out-of-Sample (Holdout)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">0,8743</td>
        <td style="text-align: center; color: #475569;">[0,8617; 0,8878] (Bootstrap BCa 10k)</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingClassifier</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M25</td>
        <td style="color: #0f172a;"><strong>Classificador Campeão: F1-Score Máximo</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">0,9113</td>
        <td style="text-align: center; color: #475569;">[0,9020; 0,9200]</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingClassifier</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M26</td>
        <td style="color: #0f172a;"><strong>Classificador Campeão: Brier Score Pós-Calibração</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">0,1043</td>
        <td style="text-align: center; color: #475569;">[0,0980; 0,1110]</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">CalibratedClassifierCV (Regressão Isotônica)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M27</td>
        <td style="color: #0f172a;"><strong>Classificador Campeão: Erro Esperado de Calibração (ECE)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">0,0174</td>
        <td style="text-align: center; color: #475569;">[0,0140; 0,0210]</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">Expected Calibration Error (10 bins)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Significância Estatística
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M28</td>
        <td style="color: #0f172a;"><strong>Teste Não Paramétrico de DeLong: HistGB vs Regressão Logística</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">Z = 16,39; p < 10^-50</td>
        <td style="text-align: center; color: #475569;">p-valor Assintótico Exato</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">Teste de DeLong et al. (1988)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Regressão ML
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M29</td>
        <td style="color: #0f172a;"><strong>Regressores: MAE do HistGradientBoosting</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 2.236,06</td>
        <td style="text-align: center; color: #475569;">[2.146,76; 2.321,17] (Bootstrap BCa 10k)</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingRegressor</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M30</td>
        <td style="color: #0f172a;"><strong>Regressores: RMSE do HistGradientBoosting</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 3.780,20</td>
        <td style="text-align: center; color: #475569;">[3.642,10; 3.918,30]</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">HistGradientBoostingRegressor</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M31</td>
        <td style="color: #0f172a;"><strong>Redução no Erro Quadrático Médio (RMSE) vs Baseline Histórico</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">9,97% de redução</td>
        <td style="text-align: center; color: #475569;">vs Mediana (R$ 4.199,01)</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">HistGB vs Estimador Mediana</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M32</td>
        <td style="color: #0f172a;"><strong>Confronto H2: MAE HistGB vs SVR-RBF</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 2.236,06 vs R$ 2.569,20</td>
        <td style="text-align: center; color: #475569;">Δ = -R$ 333,14 por OS</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">HistGB vs SVR com Kernel RBF</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Eficiência Computacional
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M33</td>
        <td style="color: #0f172a;"><strong>Confronto H2: Tempo de Treino HistGB vs SVR-RBF</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">1,8 s vs 184,6 s</td>
        <td style="text-align: center; color: #475569;">Aceleração de 102,5x</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2024-12</td>
        <td style="color: #334155;">HistGB O(N) vs SVR-RBF O(N²)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Significância Estatística
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M34</td>
        <td style="color: #0f172a;"><strong>Teste Pareado de Wilcoxon com Holm: HistGB vs SVR-RBF</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">W = 1.482.910; p < 10^-15</td>
        <td style="text-align: center; color: #475569;">Significante após Correção de Holm</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">Wilcoxon Signed-Rank Test</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Estudo Ablativo (H1)
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M35</td>
        <td style="color: #0f172a;"><strong>MAE da Fonte Isolada de Manutenção (M)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 2.321,28</td>
        <td style="text-align: center; color: #475569;">[2.298,15; 2.344,41]</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">HistGB com Atributos Exclusivos de OS (M)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M36</td>
        <td style="color: #0f172a;"><strong>MAE da Fonte Integrada Multimodal (M+P)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 2.311,82</td>
        <td style="text-align: center; color: #475569;">[2.288,76; 2.334,88]</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">HistGB com Manutenção + Patrimônio + Combustível</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M37</td>
        <td style="color: #0f172a;"><strong>Ganho Relativo no MAE com Fusão Multimodal</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">+0,41%</td>
        <td style="text-align: center; color: #475569;">[0,28%; 0,54%] (Δ = R$ 9,47/OS)</td>
        <td style="text-align: center; color: #475569;">2020-10 a 2026-03</td>
        <td style="color: #334155;">Comparativo Pareado de Dobras Temporais</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_modelagem_preditiva.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Deliberação Científica
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M38</td>
        <td style="color: #0f172a;"><strong>Status Epistemológico da Hipótese H1 (Meta ≥ 15,0%)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">NÃO SUSTENTADA</td>
        <td style="text-align: center; color: #475569;">Sem HARKing retrospectivo</td>
        <td style="text-align: center; color: #475569;">2026</td>
        <td style="color: #334155;">Critério Rígido Pré-Fixado (15,0%)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">certificado_reprodutibilidade_cientifica.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Concordância Analítica
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M39</td>
        <td style="color: #0f172a;"><strong>Regressão Não Paramétrica de Passing-Bablok (Custos)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">β = 3,318; α = -R$ 5.855,12</td>
        <td style="text-align: center; color: #475569;">β: [3,052; 3,614] | α: [-6.502,86; -5.247,98]</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">Passing & Bablok (1983) com Kendall Score</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">analise_estatistica_inferencial_aprofundada.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Modelagem Temporal
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M40</td>
        <td style="color: #0f172a;"><strong>Rampa de Tendência Inflacionária Setorial (Prophet)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">+6,08% ao ano</td>
        <td style="text-align: center; color: #475569;">[5,72%; 6,44%]</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Prophet Trend Linear Piecewise</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">prophet_forecast_results.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M41</td>
        <td style="color: #0f172a;"><strong>Repique Sazonal no 4º Trimestre (Fechamento LOA)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">+34,5% a +43,8% no volume/gastos</td>
        <td style="text-align: center; color: #475569;">Pico Sazonal Recorrente</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Prophet Yearly Seasonality Fourier</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">prophet_forecast_results.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Explicabilidade (XAI)
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M42</td>
        <td style="color: #0f172a;"><strong>Concordância Top-5 (Jaccard) / Spearman SHAP vs LIME</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">39,29% (Jaccard) | 0,3680 (&rho;)</td>
        <td style="text-align: center; color: #475569;">Divergência Geométrica</td>
        <td style="text-align: center; color: #475569;">2025-01 a 2026-03</td>
        <td style="color: #334155;">Jaccard Top-5 / Spearman Rank Correlation</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">relatorio_explicabilidade_xai.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Otimização Prescritiva
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M43</td>
        <td style="color: #0f172a;"><strong>MILP Cenário S0: Custo Total Ótimo (MILP-1)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 43.837.633,31</td>
        <td style="text-align: center; color: #475569;">Ótimo Global Comprovado</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">HiGHS Simplex Dual / Branch-and-Cut</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">experimento_milp_cenario_s0.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M44</td>
        <td style="color: #0f172a;"><strong>MILP Cenário S0: Limite Dual (Relaxação Linear LP)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 43.837.384,79</td>
        <td style="text-align: center; color: #475569;">Dual Bound <= Primal Bound</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">HiGHS Dual Simplex Continuous</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_matematica_milp_avancada.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M45</td>
        <td style="color: #0f172a;"><strong>MILP Cenário S0: Gap de Integralidade (MIP vs LP)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">0,000567% (R$ 248,52)</td>
        <td style="text-align: center; color: #475569;">Gap Quase-Nulo</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">(Primal - Dual) / Dual * 100</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_matematica_milp_avancada.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M46</td>
        <td style="color: #0f172a;"><strong>MILP Cenário S0: Tempo de Solução do Solver HiGHS</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">8,92 segundos</td>
        <td style="text-align: center; color: #475569;">0,25 s / período mensal</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">HiGHS C++ Interior Point / Dual Simplex</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">experimento_milp_cenario_s0.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M47</td>
        <td style="color: #0f172a;"><strong>MILP Cenário S0: Disponibilidade Operacional Média da Frota</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">95,26%</td>
        <td style="text-align: center; color: #475569;">[94,90%; 95,60%]</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">Fórmula Canônica de Prontidão A_t</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">experimento_milp_cenario_s0.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M48</td>
        <td style="color: #0f172a;"><strong>MILP Cenário S0: Cumprimento de Manutenções Mandatórias</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">100,00%</td>
        <td style="text-align: center; color: #475569;">Zero Violações de Segurança</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">Restrição x_it >= m_it</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">experimento_milp_cenario_s0.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M49</td>
        <td style="color: #0f172a;"><strong>MILP Cenário S0: Economia Relativa vs Baseline As-Is (BL0)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">17,51% (R$ 9.302.147,26)</td>
        <td style="text-align: center; color: #475569;">vs BL0 (R$ 53.139.780,57)</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">(Custo_BL0 - Custo_MILP1) / Custo_BL0</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">experimento_milp_cenario_s0.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M50</td>
        <td style="color: #0f172a;"><strong>MILP Cenário S0: Valor Incremental do ML (MILP-1 vs MILP-0)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 4.881.378,37 líquidos</td>
        <td style="text-align: center; color: #475569;">Economia Adicional por ML</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">MILP-1 (com ML) vs MILP-0 (médias)</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">experimento_milp_cenario_s0.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M51</td>
        <td style="color: #0f172a;"><strong>Baseline Guloso BL4 (Benefício/Custo): Diagnóstico</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">Inviável (Viola 34,53% das obrigatoriedades)</td>
        <td style="text-align: center; color: #475569;">Atendimento Obrigatório: 65,47%</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">Heurística Gulosa Risco/Custo</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">experimento_milp_cenario_s0.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M52</td>
        <td style="color: #0f172a;"><strong>Gargalo Ativo Primário: Restrição Orçamentária Mensal (B_t)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">Ativa em 41,7% a 66,7% dos meses</td>
        <td style="text-align: center; color: #475569;">Multiplicadores Duais LP > 0</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">Variáveis Duais HiGHS</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_matematica_milp_avancada.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M53</td>
        <td style="color: #0f172a;"><strong>Restrição Não Vinculante na Simulação S0: Capacidade de Oficinas em Horas (H_t)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">Ativa em 0,0% dos meses</td>
        <td style="text-align: center; color: #475569;">Multiplicadores Duais LP = 0</td>
        <td style="text-align: center; color: #475569;">Horizonte 36 Meses</td>
        <td style="color: #334155;">Variáveis Duais HiGHS</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">auditoria_matematica_milp_avancada.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Projeção Econômica
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M54</td>
        <td style="color: #0f172a;"><strong>Economia Plurianual Estimada por Simulação de Cenários</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 40.088.374,00</td>
        <td style="text-align: center; color: #475569;">Sob Cenário Inflacionário de 6,08%</td>
        <td style="text-align: center; color: #475569;">Triênio 2027–2029</td>
        <td style="color: #334155;">Modelo Prescritivo To-Be MILP</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">previsao_orcamentaria_trienal_inflacao.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M55</td>
        <td style="color: #0f172a;"><strong>Simulação Estocástica de Monte Carlo (1.000 iterações)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 40,19 Milhões</td>
        <td style="text-align: center; color: #475569;">[R$ 37,02M a R$ 43,44M] (IC 95%)</td>
        <td style="text-align: center; color: #475569;">Triênio 2027–2029</td>
        <td style="color: #334155;">Perturbação Estocástica de Custos e Risco</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">resultados_consolidados_experimentos.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Teoria dos Grafos
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M56</td>
        <td style="color: #0f172a;"><strong>Rede Bipartida Veículos-Oficinas: Comunidades de Louvain</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">18 comunidades (Q = 0,5646)</td>
        <td style="text-align: center; color: #475569;">Modularidade Forte (Q > 0,4)</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Louvain Community Detection</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">analise_grafos_redes_complexas.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M57</td>
        <td style="color: #0f172a;"><strong>Grafo de Co-ocorrência de Falhas: Comunidades Mecânicas</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">4 comunidades (Q = 0,384)</td>
        <td style="text-align: center; color: #475569;">Estrutura Mecânica Coesa</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Louvain Community Detection</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">analise_grafos_redes_complexas.json</td>
    </tr>
    
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M58</td>
        <td style="color: #0f172a;"><strong>Subrede de Anomalias Concentradas: Triagem de Auditoria</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">R$ 4.180.250,00</td>
        <td style="text-align: center; color: #475569;">Triagem para Fiscalização Dirigida</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Subgrafo Induzido de Alta Densidade</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">analise_grafos_redes_complexas.json</td>
    </tr>
    
        <tr style="background: #1e293b; color: #ffffff;">
            <th colspan="7" style="padding: 4px 6px; font-size: 7.2pt; text-align: left; text-transform: uppercase; letter-spacing: 0.5px;">
                &bull; Categoria: Governança Patrimonial
            </th>
        </tr>
        
    <tr style="font-size: 6.8pt; border-bottom: 1px solid #e2e8f0;">
        <td style="font-weight: bold; font-family: monospace; text-align: center; color: #0284c7;">M59</td>
        <td style="color: #0f172a;"><strong>Veículos Onerosos Aptos para Baixa e Leilão (Decretos SC / Benchmarking Dec. 47.539)</strong></td>
        <td style="text-align: right; font-weight: bold; color: #1e3a8a;">313 veículos</td>
        <td style="text-align: center; color: #475569;">Manutenção > 40% do Valor Venal</td>
        <td style="text-align: center; color: #475569;">2020-01 a 2026-03</td>
        <td style="color: #334155;">Decretos SC nº 1.488/2008, 2.056/2009 e Benchmarking MG 47.539/2018</td>
        <td style="font-family: monospace; font-size: 6.5pt; color: #64748b;">indicadores_gfi_consolidados.json</td>
    </tr>
    
            </tbody>
        </table>

        <!-- SEÇÃO 3.8: EXPERIMENTOS ABLATIVOS -->
        <div id="secao-3-8">
        <h3>3.8 Desenho Experimental Ablativo Multinível (E0 a E5) e Isolamento de Contribuição Marginal</h3>
        </div>
        <p>
            Para responder com rigor de padrão internacional à pergunta central da pesquisa, <em>&ldquo;Em que condições a integração de modelos preditivos calibrados, análise de redes e otimização inteira mista melhora a alocação de recursos de manutenção em frotas públicas, comparativamente a políticas convencionais, considerando restrições de segurança, orçamento e incerteza?&rdquo;</em> , , estruturou-se um protocolo experimental ablativo em <strong>seis configurações controladas e progressivas (E0 a E5)</strong>. Esse protocolo isola a contribuição marginal específica de cada camada tecnológica na qualidade da decisão prescritiva:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 6%; text-align: center;">Nível</th>
                    <th style="width: 18%;">Configuração Experimental</th>
                    <th style="width: 12%; text-align: center;">Fontes</th>
                    <th style="width: 14%; text-align: right;">Custo S0 (R$)</th>
                    <th style="width: 10%; text-align: center;">Disp. Frota</th>
                    <th style="width: 10%; text-align: center;">Atend. Seg.</th>
                    <th style="width: 14%; text-align: right;">Econ. vs E0 (R$)</th>
                    <th style="width: 16%;">Contribuição Marginal e Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="text-align: center; font-weight: bold;">E0</td>
                    <td><strong>Política Inercial Histórica (BL0)</strong></td>
                    <td style="text-align: center;">M (Reativo)</td>
                    <td style="text-align: right; font-weight: bold;">R$ 53.139.780,57</td>
                    <td style="text-align: center;">91,40%</td>
                    <td style="text-align: center;">100,0%</td>
                    <td style="text-align: right;">R$ 0,00 (0,0%)</td>
                    <td><em>Linha de Base Operacional:</em> Gestão reativa convencional sujeita a quebras emergenciais frequentes.</td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">E1</td>
                    <td><strong>Preditivo Unimodal (Manutenção M)</strong></td>
                    <td style="text-align: center;">M (OSs)</td>
                    <td style="text-align: right;">MAE R$ 2.245,53</td>
                    <td style="text-align: center;">N/A (Predição)</td>
                    <td style="text-align: center;">N/A</td>
                    <td style="text-align: right;">-9,60% RMSE</td>
                    <td><strong>Hipótese H2 Sustentada:</strong> HistGB supera baseline histórico (PR-AUC = 0,8898; ROC-AUC = 0,7490; DeLong p &lt; 10^-50).</td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">E2</td>
                    <td><strong>Preditivo Bimodal (M + Patrimônio P)</strong></td>
                    <td style="text-align: center;">M + P</td>
                    <td style="text-align: right;">MAE R$ 2.236,06</td>
                    <td style="text-align: center;">N/A (Predição)</td>
                    <td style="text-align: center;">N/A</td>
                    <td style="text-align: right;">+R$ 9,47 (-0,41%)</td>
                    <td><strong>Hipótese H1 Não Sustentada:</strong> Ganho preditivo marginal de 0,41% não atinge o limiar prévio estipulado de 15%.</td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">E3</td>
                    <td><strong>Multimodal Completo (M + P + Abastecimento A)</strong></td>
                    <td style="text-align: center;">M + P + A</td>
                    <td style="text-align: right;">MAE R$ 2.236,06</td>
                    <td style="text-align: center;">N/A (Saneamento)</td>
                    <td style="text-align: center;">N/A</td>
                    <td style="text-align: right;">+18,2% R² XAI</td>
                    <td><strong>Avaliação H4 (XAI):</strong> Saneamento de 8.816 hodômetros corrompidos; concordância SHAP vs LIME (Jaccard Top-5 = 39,3%, Spearman = 0,368) refuta equivalência estrita (&gt;85%) e fundamenta necessidade de triangulação.</td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold;">E4</td>
                    <td><strong>Otimização MILP sem ML (Médias Históricas MILP-0)</strong></td>
                    <td style="text-align: center;">M (Médias)</td>
                    <td style="text-align: right;">R$ 48.719.011,68</td>
                    <td style="text-align: center;">93,12%</td>
                    <td style="text-align: center;">100,0%</td>
                    <td style="text-align: right; color: #15803d;">R$ 4.420.768,89 (8,32%)</td>
                    <td><em>Otimização Ingênua:</em> Otimização matemática captura economia por respeito a restrições de orçamento, mas ignora risco dinâmico de falha.</td>
                </tr>
                <tr>
                    <td style="text-align: center; font-weight: bold; background: #eff6ff; color: #1d4ed8;">E5</td>
                    <td><strong>Arquitetura Prescritiva Integrada Plena (MILP-1)</strong></td>
                    <td style="text-align: center; background: #eff6ff;">M + P + A + ML</td>
                    <td style="text-align: right; font-weight: bold; color: #15803d; background: #eff6ff;">R$ 43.837.633,31</td>
                    <td style="text-align: center; font-weight: bold; background: #eff6ff;">95,26%</td>
                    <td style="text-align: center; font-weight: bold; color: #15803d; background: #eff6ff;">100,0%</td>
                    <td style="text-align: right; font-weight: bold; color: #15803d; background: #eff6ff;">R$ 9.302.147,26 (17,51%)</td>
                    <td style="background: #eff6ff;"><strong>Hipótese H3 Sustentada:</strong> MILP-1 agrega <strong>R$ 4.881.378,37 adicionais sobre E4</strong>, demonstrando analiticamente, no horizonte simulado sob restrições contrafactuais auditadas, o ganho econômico incremental aportado pela calibração probabilística do risco frente à otimização matemática ingênua.</td>
                </tr>
            </tbody>
        </table>

        <p style="font-size: 8.5pt; color: #334155; margin-top: 6px; text-align: justify;">
            <em>Conclusão Ablativa e Delimitação Epistemológica:</em> O confronto ablativo revela que <strong>a otimização linear simples sem aprendizado de máquina (E4) captura 47,5% da economia potencial, enquanto a integração com modelos supervisionados calibrados e estimativas de risco residual (E5) viabiliza os 52,5% restantes (R$ 4,88M adicionais)</strong>, elevando simultaneamente a prontidão operacional de 93,12% para 95,26%. Esse resultado evidencia que o valor econômico medido reflete a modelagem conjunta de decisão sob restrições públicas contrafactuais auditadas, não devendo ser extrapolado como garantia macroeconômica irrestrita fora das condições de contorno paramétricas estabelecidas.
        </p>

        <h2>3.4 ESTRATIFICAÇÃO DOS CUSTOS DE ABASTECIMENTO POR CATEGORIA VEICULAR E SECRETARIA</h2>
        <p>
            Em complemento aos dispêndios de manutenção mecânica, a pesquisa realizou a ingestão integral da base de <strong>1.000.000 de abastecimentos de combustível (2019 a 2022)</strong> fornecida pelo Estado de Santa Catarina, totalizando <strong>R$ 153.488.476,96</strong> e <strong>34.311.319 litros</strong> distribuídos em 12.291 veículos públicos ativos.
        </p>

        {render_figura_inline(101)}

        <p>
            Conforme demonstrado na Figura 101, os <strong>automóveis e viaturas leves de patrulhamento</strong> absorveram R$ 101,77 milhões (66,3% do total e 22,43 milhões de litros em 697.419 transações), seguidos pelas <strong>camionetes e pickups</strong> com R$ 22,32 milhões (14,5% e 5,12 milhões de litros). Sob a perspectiva institucional, a <strong>Polícia Militar de Santa Catarina (PMSC)</strong> lidera o consumo com R$ 78,67 milhões (51,25% de todo o combustível da frota estadual, em 571.268 transações), seguida pela <strong>Secretaria de Estado da Administração Prisional e Socioeducativa (SAP)</strong> com R$ 14,25 milhões (9,28%) e pela <strong>Polícia Civil (PCSC)</strong> com R$ 4,54 milhões. A integração analítica dessas duas dimensões (Combustível + Manutenção) permite quantificar o Custo Total de Propriedade (TCO) real da frota pública, subsidiando políticas de renovação e desincorporação patrimonial.
        </p>

        <!-- CAPÍTULO 4 -->
        <div id="capitulo-4">
        <h1>4 DETECÇÃO NÃO SUPERVISIONADA DE ANOMALIAS E AUDITORIA FISCAL</h1>
        </div>
        <p>
            O algoritmo <em>Isolation Forest</em> isolou atipicidades multidimensionais no espaço contínuo composto por custo aprovado, valor orçado, duração de reparo, quilometragem, idade veicular e quantidade de itens. Com parâmetro de contaminação calibrado em &nu; = 0,0085 (0,85%) sobre o universo de <strong>77.867 Ordens de Serviço consolidadas</strong>, foram isoladas <strong>662 ordens de serviço anômalas</strong> (com índice de similaridade de Jaccard multissemente certificado em 0,8055), que concentraram R$ 17,10 milhões em orçamentos cotados pelas oficinas e R$ 16,58 milhões em dispêndio aprovado. Frente à massa total de <strong>350.737 itens de manutenção</strong>, as atipicidades multidimensionais isoladas pelo algoritmo incidem sobre <strong>2.336 itens vinculados a essas ordens atípicas</strong>. Sob o prisma do rigor epistemológico e da governança pública, ressalta-se enfaticamente que o <em>Isolation Forest</em> detecta atipicidades estatísticas multivariadas no espaço contínuo de custo, downtime, hodômetro e idade veicular, funcionando como instrumento analítico de triagem prioritária para auditoria humana e perícia técnica, não constituindo, por si só, comprovação documental ou jurídica autônoma de superfaturamento, conluio ou dolo.
        </p>

        {render_figura_inline(5)}
        {render_figura_inline(6)}

        <table>
            <thead>
                <tr>
                    <th>Órgão Governamental</th>
                    <th style="text-align: center;">OSs Auditadas</th>
                    <th style="text-align: right;">Gasto Aprovado</th>
                    <th style="text-align: right;">Valor Orçado Inicial</th>
                    <th style="text-align: right;">Glosa Técnica (Economia)</th>
                    <th style="text-align: center;">Downtime Médio</th>
                </tr>
            </thead>
            <tbody>
                {tabela_orgaos_html}
            </tbody>
        </table>

        <h3>4.1 Calibração da Taxa de Contaminação e Estabilidade do Isolation Forest</h3>
        <p>
            A detecção de anomalias multidimensionais operou sobre um espaço vetorial composto pelo custo total aprovado, duração do serviço (dias imobilizados), quilometragem do hodômetro e idade do veículo. Para assegurar a robustez do particionamento estocástico, avaliou-se a estabilidade das árvores de isolamento sob múltiplos níveis de contaminação pré-fixada &nu; &isin; &#123;1%, 2%, 5%, 10%&#125; sobre o <strong>universo empírico consolidado (<em>N</em> = 77.867 OSs únicas)</strong> através do Índice de Similaridade de Jaccard médio em reamostragens independentes (onde 1% = 779 OSs, 2% = 1.557 OSs, 5% = 3.894 OSs e 10% = 7.787 OSs, e em &nu; = 0,85% isolam-se 662 OSs anômalas, correspondendo a 2.336 itens auditados):
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="text-align: center;">Taxa Contaminação (&nu;)</th>
                    <th style="text-align: center;">Anomalias Isoladas</th>
                    <th style="text-align: center;">Proporção Amostral</th>
                    <th style="text-align: center;">Similaridade Jaccard Média</th>
                    <th style="text-align: center;">Teste t Pareado (Reprovadas)</th>
                    <th style="text-align: center;">Significância (p-valor)</th>
                </tr>
            </thead>
            <tbody>
                {tabela_iforest_html}
            </tbody>
        </table>

        {render_figura_inline(91)}

        <p>
            O teste t de Student bicaudal revelou diferença estatisticamente significante (t = 3,524; p = 0,000426) entre os escores de anomalia atribuídos às ordens aprovadas (&mu; = -0,4150) e às ordens previamente glosadas/reprovadas (&mu; = -0,4122), comprovando a sensibilidade intrínseca do algoritmo em capturar desvios contratuais antes mesmo da intervenção dos auditores humanos.
        </p>

        <h2>4.2 DETECÇÃO MULTIDIMENSIONAL DE ANOMALIAS EM ABASTECIMENTOS COM ISOLATION FOREST</h2>
        <p>
            Empregando o mesmo rigor metodológico de detecção não supervisionada, treinou-se uma instância do algoritmo <em>Isolation Forest</em> (150 estimadores, taxa de contaminação pré-fixada &nu; = 0,015) sobre a base de 1.000.000 de abastecimentos. A matriz de atributos incluiu as variáveis contínuas de <strong>volume faturado (litros)</strong>, <strong>preço unitário (R$/L)</strong>, <strong>valor total do cupom (R$)</strong>, <strong>eficiência calculada (km/L)</strong> e <strong>quilometragem rodada entre abastecimentos</strong>.
        </p>

        {render_figura_inline(100)}

        <p>
            O modelo isolou categoricamente <strong>13.936 transações atípicas (1,39%)</strong>. Conforme ilustrado na Figura 100, a fronteira de decisão isolou dois agrupamentos fundamentais de irregularidades:
        </p>
        <p>
            1. <em>Sobrepreço Severo e Erro de Preenchimento:</em> Enquanto a operação regular registrou preço médio de R$ 5,41/L, o grupo isolado exibiu preço médio de R$ 52,33/L decorrente de inconsistências de digitação nos terminais POS ou cobranças fora da tabela de preços contratada com a rede de postos credenciados.<br>
            2. <em>Volume Hiper-Atípico:</em> Registros com mais de 90 a 150 litros abastecidos em automóveis compactos e viaturas policiais leves cujo tanque físico não ultrapassa 50 a 60 litros (média de 153,19 L no cluster atípico vs. 32,63 L no regime normal). Essa explicabilidade permite à equipe de controle interno e auditoria da SEA/SC acionar travas automatizadas no sistema de autorização de combustível.
        </p>

        <!-- CAPÍTULO 5 -->
        <div id="capitulo-5">
        <h1>5 CLASSIFICAÇÃO NÃO LINEAR DE RISCO OPERACIONAL, ACURÁCIA E CALIBRAÇÃO (HIPÓTESE H2, COMPONENTE DE RISCO)</h1>
        </div>
        <p>
            A modelagem de risco operacional tem por objetivo antecipar viaturas com alta probabilidade de colapso mecânico severo no horizonte t+1. Considerando o desbalanceamento de classes inerente ao setor público (onde 78,38% das observações na partição de teste temporal operam em regime de manutenção preventiva rotineira sem falha corretiva imediata), a métrica primária de seleção do classificador campeão foi a Área sob a Curva de Precisão-Recall (PR-AUC), complementada pela Área sob a Curva ROC (ROC-AUC), F1-Score Máximo (F1-Max), Brier Score e Erro Esperado de Calibração (ECE - <em>Expected Calibration Error</em>).
        </p>
        <p>
            Para mitigar categoricamente qualquer risco de vazamento temporal (<em>data leakage</em>), a validação cruzada adotou o protocolo de <strong>Validação Temporal com Janela Deslizante (Rolling-Window Cross-Validation)</strong> em K = 5 dobras sequenciais cronológicas. A dispersão amostral entre as dobras foi quantificada através do <strong>Erro Padrão da Média (Standard Error of the Mean - SEM)</strong>:
        </p>

        <div class="box-formula">
            <strong>Cálculo do Erro Padrão da Média (SEM) e Intervalo de Confiança de 95%:</strong><br>
            SEM = s / &radic;K = &radic;[ (1 / (K(K - 1))) &sum;_(k=1)^K (x_k - x&#772;)&sup2; ] &nbsp;|&nbsp; IC_95% = x&#772; &plusmn; t_(K-1; 0,025) &times; SEM
        </div>

        <p>
            A Tabela a seguir consolida o desempenho comparativo dos seis classificadores investigados, com seus respectivos parâmetros de erro padrão:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Classificador Avaliado</th>
                    <th style="text-align: center;">PR-AUC</th>
                    <th style="text-align: center;">ROC-AUC</th>
                    <th style="text-align: center;">F1-Max</th>
                    <th style="text-align: center;">Brier Score</th>
                    <th style="text-align: center;">ECE</th>
                    <th style="text-align: center;">Precisão</th>
                    <th style="text-align: center;">Recall</th>
                    <th style="text-align: center;">Erro Padrão (SEM)</th>
                </tr>
            </thead>
            <tbody>
                {tabela_classif_ml_html}
            </tbody>
        </table>

        <p>
            O modelo <em>HistGradientBoosting</em> sagrou-se campeão absoluto na classificação de risco com PR-AUC de <strong>0,9510</strong> na partição de teste independente do Protocolo B (coexistindo harmonicamente com a média temporal multianual de 0,8941 &plusmn; 0,0089 reportada no Protocolo A de 5 dobras com embargo), ROC-AUC de <strong>0,8743</strong> [IC 95%: 0,8617; 0,8878], F1-Score de <strong>0,9113</strong> e baixíssimo ECE de <strong>0,0174</strong>, refletindo estabilidade extrema nas predições sob severo desbalanceamento amostral. A calibração de probabilidades reduziu o Brier Score de 0,1695 (baseline ingênuo) para 0,1043, garantindo probabilidades verossímeis e seguras para alimentar a parametrização de risco do solver MILP.
        </p>

        <h3>5.1 Comparação Pareada de Curvas ROC via Teste de DeLong</h3>
        <p>
            Para verificar a superioridade estatística do modelo <em>HistGradientBoosting</em> em relação aos concorrentes, aplicou-se o teste não paramétrico de <strong>DeLong et al. (1988)</strong> sobre as matrizes de covariância das curvas ROC:
        </p>
        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Contraste Pareado de Classificadores</th>
                    <th style="text-align: center;">Estatística Z</th>
                    <th style="text-align: center;">p-valor Assintótico</th>
                    <th style="text-align: center;">Decisão Estatística (&alpha; = 0,05)</th>
                </tr>
            </thead>
            <tbody>
                {tabela_delong_html}
            </tbody>
        </table>
        <p>
            A simulação Bootstrap não paramétrica (10.000 iterações com método BCa) estabeleceu os intervalos de confiança de 95% rigorosamente centrados nos estimadores pontuais do modelo campeão <em>HistGradientBoosting</em>: <strong>PR-AUC = 0,9510 [IC 95%: 0,9420; 0,9590]</strong>, <strong>ROC-AUC = 0,8743 [IC 95%: 0,8617; 0,8878]</strong>, <strong>Brier Score = 0,1043 [IC 95%: 0,0980; 0,1110]</strong> e <strong>ECE = 0,0174 [IC 95%: 0,0140; 0,0210]</strong>. A calibração isotônica de probabilidades reduziu o Brier Score para 0,1043 e o Erro Esperado de Calibração (ECE) para 0,0174, assegurando verossimilhança probabilística empírica para alimentar as taxas de falha estocásticas e o custo de risco residual da programação linear inteira mista.
        </p>

        {render_figura_inline(7)}
        {render_figura_inline(8)}
        {render_figura_inline(9)}

        <!-- CAPÍTULO 6 -->
        <div id="capitulo-6">
        <h1>6 REGRESSÃO NÃO LINEAR DE CUSTOS, CONFRONTO COM SVR-RBF E SUSTENTAÇÃO INTEGRAL DA HIPÓTESE H2</h1>
        </div>
        <p>
            A previsão do valor financeiro das ordens de serviço envolve variáveis heterogêneas com distribuição assimétrica e cauda pesada. Conforme exigência epistemológica do método científico, realizou-se a bateria diagnóstica de testes de normalidade e assimetria sobre o universo empírico:
        </p>
        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Variável Operacional</th>
                    <th style="text-align: right;">Média</th>
                    <th style="text-align: right;">Mediana</th>
                    <th style="text-align: center;">Assimetria</th>
                    <th style="text-align: center;">Curtose</th>
                    <th style="text-align: center;">Shapiro-Wilk</th>
                    <th style="text-align: center;">p-valor</th>
                    <th style="text-align: center;">Diagnóstico Distribucional</th>
                </tr>
            </thead>
            <tbody>
                {tabela_norm_stats_html}
            </tbody>
        </table>
        <p>
            O teste de <strong>Mann-Whitney U</strong> confirmou a disparidade estrutural entre manutenções corretivas (mediana R$ 135,00) e preventivas (mediana R$ 100,00) com Z = 39,95 (p &lt; 10^-15; tamanho de efeito r = 0,0675). O teste de <strong>Kruskal-Wallis</strong> ratificou diferenças altamente significantes entre famílias veiculares (H = 1.732,12; gl = 4; p &lt; 10^-15). Na modelagem de confiabilidade por Máxima Verossimilhança (MLE), a distribuição <strong>Weibull Biparamétrica</strong> obteve o melhor ajuste (AIC = 252.856,1) com parâmetro de forma <strong>k = 1,458</strong> (k &gt; 1 comprova aumento progressivo da taxa de falhas por desgaste mecânico e idade, refutando modelos exponenciais de taxa constante).
        </p>

        <h3>6.1 Benchmark Comparativo de Regressores e Erro Padrão do MAE</h3>
        <p>
            Avaliaram-se múltiplos regressores ensemble não lineares frente à mediana histórica de custos:
        </p>
        <p style="font-size: 8.5pt; color: #334155;">
            <em>Nota Epistemológica sobre Critério de Seleção do Regressor Campeão:</em> Conforme demonstrado na Tabela a seguir, a mediana histórica apresenta menor MAE pontual (R$ 2.133,49) devido a uma propriedade matemática estrita (a mediana amostral é o estimador ótimo que minimiza a função de perda L1 por definição teórica). No entanto, a mediana é incapaz de capturar a heterogeneidade e a severidade financeira de reparos complexos, gerando elevado erro quadrático (RMSE de R$ 4.199,01 com R&sup2; negativo de -0,0933). O modelo <strong>HistGradientBoosting</strong> sagrou-se o regressor campeão por apresentar a melhor capacidade de generalização e discriminação de cauda: menor RMSE (R$ 3.780,20, redução de 9,97% frente ao baseline), menor MAE entre os ensembles (R$ 2.236,06) e R&sup2; ajustado positivo de 0,1139, com tempo de treinamento altamente eficiente de 1,8 segundos frente à inviabilidade computacional do SVR.
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Modelo de Regressão</th>
                    <th style="text-align: right;">MAE (R$)</th>
                    <th style="text-align: center;">Erro Padrão (SEM)</th>
                    <th style="text-align: right;">RMSE (R$)</th>
                    <th style="text-align: center;">R&sup2; Ajustado</th>
                    <th style="text-align: center;">sMAPE (%)</th>
                    <th style="text-align: center;">Tempo Treino</th>
                </tr>
            </thead>
            <tbody>
                {tabela_regressao_ml_html}
            </tbody>
        </table>

        {render_figura_inline(10)}

        <h3>6.2 Teste Não Paramétrico de Wilcoxon Signed-Rank com Correção de Holm</h3>
        <p>
            Para comprovar que a superioridade dos modelos ensemble baseados em árvores (<em>HistGradientBoosting</em> e <em>Extra Trees</em>) em relação ao <em>Support Vector Regression (SVR-RBF)</em> e aos demais concorrentes não decorreu de flutuações aleatórias, aplicou-se o teste não paramétrico de postos sinalizados de Wilcoxon pareado em nível de significância &alpha; = 0,05, submetido à correção conservadora de Holm-Bonferroni para comparações múltiplas:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Contraste Pareado de Modelos</th>
                    <th style="text-align: center;">W Estatístico</th>
                    <th style="text-align: center;">p-valor Bruto</th>
                    <th style="text-align: center;">p-valor Holm</th>
                    <th style="text-align: right;">&Delta; Médio MAE</th>
                    <th style="text-align: center;">Decisão (&alpha; = 0,05)</th>
                </tr>
            </thead>
            <tbody>
                {tabela_wilcoxon_html}
            </tbody>
        </table>

        <p>
            Todos os contrastes pareados exibiram p-valores inferiores a 10^-4 após correção de Holm-Bonferroni, refutando a hipótese nula de equivalência estocástica e <strong>sustentando formalmente a Hipótese H2</strong> quanto à superioridade dos ensembles de árvores frente ao SVR-RBF tanto em precisão preditiva (MAE de R$ 2.311,82 vs R$ 2.569,20) quanto em eficiência e viabilidade computacional (1,8s vs escala inviável O(N&sup2;)).
        </p>

        <div id="secao-6-3">
        <h3>6.3 Estudo Ablativo Multimodal e Avaliação Epistemológica da Hipótese H1</h3>
        </div>
        <p>
            O estudo ablativo confrontou modelos treinados exclusivamente com a base transacional de ordens de serviço (M) contra modelos integrados multimodais contendo variáveis de cadastro patrimonial e abastecimento (M+P), avaliados sob validação cruzada temporal em 5 dobras sequenciais (<em>Rolling-Window</em> com embargo de 30 dias):
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Tarefa Analítica</th>
                    <th style="text-align: center;">Métrica</th>
                    <th style="text-align: center;">Manutenção Isolada (M)</th>
                    <th style="text-align: center;">Multimodal (M+P)</th>
                    <th style="text-align: center;">Ganho Absoluto (&Delta;)</th>
                    <th style="text-align: center;">Ganho Relativo (%)</th>
                    <th style="text-align: center;">Status Hipótese H1</th>
                </tr>
            </thead>
            <tbody>
                {tabela_ablacao_html}
            </tbody>
        </table>

        {render_figura_inline(12)}

        <div class="box-aviso">
            <strong>Deliberação Epistemológica Rigorosa sobre a Hipótese H1:</strong><br>
            A inclusão das variáveis multimodais de patrimônio e abastecimento reduziu o Erro Médio Absoluto (MAE) de R$ 2.321,28 [IC 95%: 2.298,15; 2.344,41] para R$ 2.311,82 [IC 95%: 2.288,76; 2.334,88], representando uma redução absoluta de R$ 9,47 por ordem de serviço (ganho relativo de <strong>+0,41% [IC 95%: 0,28%; 0,54%]</strong>) e elevou o PR-AUC de 0,9060 para <strong>0,9099 (+0,43%)</strong>. Embora ambos os ganhos possuam significância estatística extrema (Wilcoxon pareado p &lt; 10^-15), o ganho relativo (+0,41%) ficou substancialmente aquém do limiar rígido de 15,0% fixado a priori no anteprojeto de pesquisa. Em estrita observância às diretrizes internacionais de integridade metodológica e ciência aberta, vedando terminantemente qualquer flexibilização retrospectiva do critério (vício metodológico de <em>HARKing</em>), <strong>a Hipótese H1 é formalmente classificada e declarada como NÃO SUSTENTADA</strong> no limiar pré-registrado.
        </div>

        <div id="secao-6-4">
        <h3>6.4 Regressão Não Paramétrica de Passing-Bablok (1983) e Diagnóstico de Linearidade</h3>
        </div>
        <p>
            Para avaliar a concordância analítica entre valores preditos e reais sem incorrer nos vieses do método paramétrico de mínimos quadrados ordinários (OLS) frente a distribuições de cauda pesada e heterocedásticas, empregou-se a <strong>Regressão Não Paramétrica de Passing &amp; Bablok (1983)</strong> com estimação de intervalos de confiança de 95% via variância do escore de Kendall e teste CUSUM de linearidade:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Contraste Metodológico</th>
                    <th style="text-align: center;">Inclinação (&beta;) [IC 95%]</th>
                    <th style="text-align: center;">Intercepto (&alpha;) [IC 95%]</th>
                    <th style="text-align: center;">Estatística CUSUM</th>
                    <th style="text-align: center;">Pares Avaliados</th>
                    <th style="text-align: center;">Diagnóstico Metodológico</th>
                </tr>
            </thead>
            <tbody>
                {tabela_passing_bablok_html}
            </tbody>
        </table>

        {render_figura_inline(11)}

        <p style="font-size: 8.5pt; color: #334155; margin-bottom: 12px;">
            <em>Interpretação e Implicações Metodológicas:</em> No contraste entre o custo previsto pelo <em>HistGradientBoosting</em> e o custo real observado ($n = 2.500$, com 3.123.691 pares angulares avaliados), a inclinação &beta; = 3,318 [IC 95%: 3,052; 3,614] difere de 1,0 e o intercepto &alpha; = -R$ 5.855,12 [IC 95%: -6.502,86; -5.247,98] não contém o zero, comprovando a presença de erro proporcional decorrente da extrema assimetria à direita dos custos de manutenção veicular. Esse resultado justifica formalmente o emprego de algoritmos ensemble de árvores e regressão quantílica, refutando o uso ingênuo de modelos lineares paramétricos (OLS). Já no contraste de auditoria fiscal entre Valor Orçado Inicial e Valor Aprovado nas OSs, a regressão de Passing-Bablok reportou &beta; = 1,000 [IC 95%: 1,000; 1,000] e &alpha; = R$ 0,00 [IC 95%: 0,00; 0,00], atestando perfeita concordância linear nos itens em conformidade e isolando as discrepâncias exclusivamente nas ordens anômalas com glosa técnica.
        </p>

        <!-- CAPÍTULO 7 -->
        <div id="capitulo-7">
        <h1>7 MODELAGEM TEMPORAL, DECOMPOSIÇÃO E PREVISÃO DE DEMANDA</h1>
        </div>
        <p>
            A modelagem de séries temporais via <em>Prophet</em> isolou a componente de tendência secular, sazonalidade anual (picos em novembro/dezembro) e semanal. O benchmark clássico confirmou a superioridade da decomposição ETS (Error, Trend, Seasonal) frente ao modelo SARIMA em termos de estabilidade computacional e aderência à curva orçamentária do Estado.
        </p>

        {render_figura_inline(19)}
        {render_figura_inline(20)}

        <h2>7.1 MODELAGEM REGRESSIVA LINEAR E PREVISÃO DE ABASTECIMENTOS COM FACEBOOK PROPHET</h2>
        <p>
            A modelagem de séries temporais foi estendida para a base de abastecimentos diários (2019 a 2022). Empregou-se o modelo <em>Facebook Prophet</em> com crescimento linear, feriados nacionais brasileiros e decomposição de sazonalidade anual e semanal para isolar a tendência estrutural dos custos de combustível da frota estadual catarinense.
        </p>

        {render_figura_inline(98)}

        <p>
            A Figura 98 retrata a trajetória do dispêndio diário de combustível com os pontos reais observados, a curva de tendência ŷ estimada e o intervalo de incerteza empírica de 95% estendido para os 24 meses subsequentes. O modelo capta categoricamente o choque de recomposição de preços no pós-pandemia (2021), quando o preço médio ponderado se elevou em mais de 37,8% no Estado.
        </p>

        {render_figura_inline(99)}

        <p>
            A decomposição estrutural apresentada na Figura 99 evidencia: (i) a inclinação positiva da tendência secular; (ii) a sazonalidade semanal com pico de abastecimentos nas sextas-feiras e manutenção de consumo essencial no final de semana pelas viaturas operacionais de emergência; e (iii) a sazonalidade anual, caracterizada pela elevação sistemática de consumo nos meses de novembro a janeiro, correspondendo ao deslocamento de efetivo policial e viaturas para a Operação Veraneio na faixa litorânea.
        </p>

        <!-- CAPÍTULO 8 -->
        <div id="capitulo-8">
        <h1>8 INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL (XAI), TRIANGULAÇÃO E CONFIABILIDADE (HIPÓTESE H4)</h1>
        </div>
        <p>
            A explicabilidade dos modelos preditivos foi fundamentada na teoria dos jogos cooperativos via valores de Shapley (SHAP TreeExplainer) e em aproximações locais lineares interpretáveis (LIME). As variáveis de quilometragem acumulada no hodômetro, idade do veículo e histórico de intervenções responderam conjuntamente por mais de 65% da importância preditiva global. Contudo, ao confrontar os rankings de relevância atribuídos por SHAP e LIME sobre as instâncias auditadas, observou-se <strong>índice de similaridade de Jaccard Top-5 de 39,29% (39,3%)</strong> e <strong>coeficiente de correlação de postos de Spearman &rho; = 0,3680</strong>. Em decorrência dessa divergência geométrica intrínseca entre os fundamentos aditivos globais de coalizões de Shapley e a regressão linear local sob perturbações gaussianas do LIME, a <strong>Hipótese H4 NÃO FOI SUSTENTADA sob o limiar a priori de alta concordância (&gt; 85%)</strong>.
        </p>
        <p>
            <em>Contribuição Metodológica e Governança Pública:</em> Longe de representar uma debilidade analítica, a refutação da intercambialidade cega entre SHAP e LIME constitui um achado epistemológico de grande relevância para a administração pública e o controle externo: comprova que auditores da SEA DITI e do Tribunal de Contas do Estado (TCE-SC) não podem acolher acriticamente explicações algorítmicas baseadas em um único framework isolado. Torna-se imperativo o emprego de um <strong>protocolo formal de triangulação explicativa multimetodológica</strong> associado à perícia técnica humana para fundamentar decisões administrativas, glosas ou processos de desincorporação patrimonial.
        </p>

        {render_figura_inline(13)}
        {render_figura_inline(17)}

        <!-- CAPÍTULO 9 -->
        <div id="capitulo-9">
        <h1>9 OTIMIZAÇÃO PRESCRITIVA (MILP), PROTOCOLO CENÁRIO S0 E DECISÃO SOB RESTRIÇÕES (HIPÓTESE H3)</h1>
        </div>
        <p>
            A formulação canônica de Programação Linear Inteira Mista (MILP) converte probabilidades de falha calibradas e custos previstos por aprendizado de máquina em decisões ótimas de intervenção binária:
        </p>

        <div class="box-formula">
            <strong>Formulação Canônica Corrigida do Modelo Prescritivo MILP:</strong><br>
            min &sum;_(t=1)^T &sum;_(i=1)^N [ &alpha; &middot; c_it x_it + &beta; &middot; r_it (1 - x_it) ]<br>
            Sujeito a: &sum;_(i=1)^N c_it x_it &le; B_t &nbsp;|&nbsp; &sum;_(i=1)^N h_it x_it &le; H_t &nbsp;|&nbsp; x_it &ge; m_it &nbsp;|&nbsp; x_it &isin; &#123;0, 1&#125;
        </div>
        <p style="font-size: 8pt; color: #475569; margin-top: -6px;">
            <em>Nota Técnica de Correção Metodológica:</em> A literatura preliminar continha formulação defeituosa em que a penalidade de risco multiplicava a variável de decisão de manutenção (&beta; &middot; r_it x_it), o que gerava penalização pela execução do reparo e colapsava a solução para a inação trivial (x_it = 0). O modelo canônico acima associa corretamente a penalidade de risco de indisponibilidade e colapso à não intervenção (1 - x_it).
        </p>
        <p style="font-size: 8.5pt;">
            <strong>Mapeamento de Parâmetros e Função de Disponibilidade Operacional:</strong> A probabilidade de falha <em>P(Falha<sub>it</sub>)</em> provém do classificador calibrado <em>HistGradientBoosting</em>; o custo preventivo <em>c<sub>it</sub></em> é estimado pelo regressor; o custo de risco residual é parametrizado por <em>r<sub>it</sub> = P(Falha<sub>it</sub>) &times; C<sup>corr</sup><sub>it</sub></em>, onde <em>C<sup>corr</sup><sub>it</sub></em> denota o custo esperado do reparo emergencial pós-quebra. As horas de imobilização em oficina <em>h<sub>it</sub></em> alimentam a taxa de disponibilidade operacional média da frota no período:
            <em>A<sub>t</sub> = 1 - [&sum;<sub>i=1</sub><sup>N</sup> (h<sub>it</sub> x<sub>it</sub> + h<sup>quebra</sup><sub>it</sub> (1 - x<sub>it</sub>) P(Falha<sub>it</sub>))] / (N &times; 720h)</em>.
        </p>

        <div id="secao-9-1">
        <h3>9.1 Benchmark Experimental das 7 Políticas de Gestão, Cenário de Referência S0 (Nominal)</h3>
        </div>
        <p>
            O experimento computacional avaliou uma frota representativa de N = 2.000 veículos ao longo de um horizonte trienal de T = 36 meses discretos (totalizando 72.000 variáveis de decisão binárias) sob 7 políticas concorrentes, resolvidas com o solver <strong>HiGHS (Simplex Dual / Branch-and-Cut)</strong> sob tolerância de otimalidade de 10<sup>-7</sup>:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Política de Gestão Operacional</th>
                    <th style="text-align: right;">Custo Direto (R$)</th>
                    <th style="text-align: right;">Risco Residual (R$)</th>
                    <th style="text-align: right;">Custo Total (R$)</th>
                    <th style="text-align: center;">Disp. Frota</th>
                    <th style="text-align: center;">Atend. Obrig.</th>
                    <th style="text-align: center;">Econ. vs BL0</th>
                    <th style="text-align: right;">Economia Líquida</th>
                    <th style="text-align: center;">Tempo Solver</th>
                </tr>
            </thead>
            <tbody>
                {tabela_milp_s0_html}
            </tbody>
        </table>

        {render_figura_inline(15)}

        <p style="font-size: 8.5pt; color: #1e293b; background: #f8fafc; border-left: 3px solid #2563eb; padding: 6px 10px; margin: 8px 0;">
            <strong>Certificação Computacional do Solver HiGHS e Registro de Execução Auditada:</strong><br>
            A convergência exata da política <em>MILP-1</em> foi certificada computacionalmente pelo solver <strong>HiGHS (v1.7.0, Simplex Dual / Branch-and-Cut em C++)</strong>, com parâmetros e limites duais gravados de forma auditável nos artefatos <code>public-fleet-prescriptive-analytics/results/solver_logs/relatorio_otimizacao_milp.json</code> (timestamp <code>2026-10-22T21:23:42.525894</code>) e <code>relatorios/auditoria_matematica_milp_avancada.json</code>. O tempo de processamento totalizou <strong>8,92 segundos</strong> (média de 0,25 s/período em CPU commodity x86_64), com <strong>Dual Bound = R$ 43.837.633,31</strong> estritamente coincidente com o <strong>Primal Bound viável</strong> sob tolerância absoluta e relativa de 10<sup>-7</sup>.<br><br>
            <strong>Distinção Matemática Mandatória para a Defesa:</strong><br>
            É imperativo preservar a distinção entre dois conceitos teóricos complementares frequentemente confundidos em bancas examinadoras:
            (1) <em>Gap Relativo de Otimalidade do Solver (MIP Gap = 0,0000%):</em> Atesta que o algoritmo branch-and-cut encerrou a busca com prova matemática de que nenhuma outra solução inteira viável (x_it &isin; {0, 1}) possui custo inferior a R$ 43.837.633,31, garantindo o <em>ótimo global do problema inteiro</em>;
            (2) <em>Gap de Integralidade Poliedral LP–MIP (0,00057% ou R$ 248,52):</em> Confronta o custo inteiro (Z<sub>MIP</sub> = R$ 43.837.633,31) com a relaxação linear contínua (Z<sub>LP</sub> = R$ 43.837.384,79, onde x_it &isin; [0, 1]). A quase-nulidade desse gap (menos de seis partes por milhão) prova que o envoltório convexo das soluções inteiras quase coincide com o poliedro contínuo, demonstrando que a formulação canônica formulada no Capítulo 9 é poliedralmente quase-ideal.<br><br>
            <em>Inviabilidade Operacional do Baseline Ganancioso BL4 e Demonstração do Percentual de 34,53%:</em><br>
            Para assegurar rigor analítico e responder com exatidão às exigências de controle público, decompõe-se a origem de cada uma das restrições do modelo e a demonstração formal de inviabilidade da heurística gananciosa <em>BL4 (Benefício/Custo)</em>:
            <ul style="margin: 4px 0 0 16px; padding: 0;">
                <li><strong>1. Restrição Legal / Regulatória (Mandatória):</strong> Fundamentada no Código de Trânsito Brasileiro (CTB, Lei Federal nº 9.503/1997, art. 104, inspeção técnica veicular) e no Decreto Estadual SC nº 2.056/2009. Estabelece a compulsoriedade da revisão de segurança periódica (sistema de freios, suspensão, direção e iluminação) no mínimo anual (<em>m<sub>it</sub> = 1</em>). No horizonte de <em>T = 36</em> meses para os <em>N = 2.000</em> veículos do Cenário S0, foram computadas exatamente <strong>6.000 intervenções obrigatórias</strong>. Formulação no MILP: <em>x<sub>it</sub> &ge; m<sub>it</sub>, &forall; (i, t) &isin; M</em>.</li>
                <li><strong>2. Restrição Operacional de Capacidade:</strong> Limite físico mensal de horas disponíveis de mão de obra especializada da rede credenciada de oficinas (<em>H<sub>t</sub></em>), modelando a restrição física de atendimento na macrorregião. Formulação: <em>&sum;<sub>i</sub> h<sub>it</sub> x<sub>it</sub> &le; H<sub>t</sub>, &forall; t</em>.</li>
                <li><strong>3. Restrição Orçamentária / Fiscal de Cenário:</strong> Escolha paramétrica do Cenário S0 que emula o teto mensal de liquidação programada na Lei Orçamentária Anual (LOA). Formulação: <em>&sum;<sub>i</sub> c<sub>it</sub> x<sub>it</sub> &le; B<sub>t</sub>, &forall; t</em>.</li>
            </ul>
            <strong>Demonstração do Cálculo de 34,53% de Violação em BL4:</strong><br>
            A heurística gananciosa BL4 ordena as intervenções estritamente pelo índice benefício/custo (<em>r<sub>it</sub> / c<sub>it</sub></em>) e aloca até esgotar o orçamento, omitindo a restrição regulatória <em>x<sub>it</sub> &ge; m<sub>it</sub></em>. Como resultado, executou apenas 3.928 revisões obrigatórias (atendimento de 65,47%), <strong>deixando de atender 2.072 intervenções compulsórias de segurança</strong>. A taxa de violação é obtida diretamente por:
            <div style="text-align: center; margin: 4px 0; font-weight: bold;">
                Taxa de Violação Legal (BL4) = (6.000 &minus; 3.928) / 6.000 = 2.072 / 6.000 = 34,53%
            </div>
            O custo nominal ligeiramente menor reportado por BL4 (R$ 42,98M vs R$ 43,84M do MILP-1) é uma <strong>ilusão contábil provocada pela operação fora da região viável</strong>. Na administração pública, a circulação de veículos oficiais com inspeções compulsórias vencidas infringe a legislação de trânsito e gera responsabilidade civil e administrativa ao gestor. Portanto, <strong>no espaço das soluções viáveis (com 100,0% de conformidade legal), o MILP-1 é o ótimo global absoluto</strong>.
        </p>

        <p>
            Sob o protocolo experimental do Cenário S0, os resultados proporcionam evidências formais sobre as três sub-hipóteses de otimização:
        </p>
        <ul style="margin-left: 20px; font-size: 8.5pt;">
            <li><strong>Hipótese H-M1 (Eficiência Econômica): SUSTENTADA (no Cenário S0).</strong> A política integrada <em>MILP-1</em> alcançou menor custo total viável (R$ 43,84M), gerando <strong>17,51% de economia líquida (R$ 9,30 milhões poupados)</strong> em relação à política inercial BL0, com garantia estrita de cumprimento orçamentário.</li>
            <li><strong>Hipótese H-M2 (Desempenho Operacional): SUSTENTADA (no Cenário S0).</strong> O <em>MILP-1</em> garantiu disponibilidade operacional média de <strong>95,26%</strong> com estrito cumprimento de <strong>100,0% das manutenções mandatórias</strong> de segurança e garantias contratuais de fábrica.</li>
            <li><strong>Hipótese H-M3 (Valor Incremental da Predição por ML): SUSTENTADA (no Cenário S0).</strong> O <em>MILP-1</em> superou a otimização matemática ingênua baseada em médias históricas sem ML (MILP-0) em <strong>R$ 4.881.378,37</strong>, isolando rigorosamente o valor financeiro agregado pela acurácia dos modelos supervisionados na prescrição.</li>
        </ul>

        {render_figura_inline(90)}

        <div id="secao-9-2">
        <h3>9.2 Análise de Robustez e Sensibilidade Estocástica de Monte Carlo (1.000 Iterações)</h3>
        </div>
        <p>
            Submetendo os parâmetros de custos e probabilidades a 1.000 perturbações aleatórias estocásticas (&plusmn;20% no orçamento e &plusmn;25% nos custos de falha), a economia trienal simulada para o conjunto da frota convergiu para <strong>R$ 40,19 Milhões [IC 95%: R$ 37,02M a R$ 43,44M]</strong>, com 100% de probabilidade de economia superior a R$ 30,0 Milhões, sustentando formalmente a <strong>Hipótese H3</strong>.
        </p>

        <div id="secao-9-3">
        <h3>9.3 Auditoria Matemática da Relaxação Linear (LP), Gap de Integralidade e Gargalos Ativos</h3>
        </div>
        <p>
            Em atendimento estrito aos critérios de rigor matemático da pesquisa operacional, investigou-se a qualidade poliedral da formulação canônica através do confronto entre a solução inteira exata (x_it &isin; &#123;0, 1&#125;) e sua respectiva <strong>Relaxação Linear Contínua (x_it &isin; [0, 1])</strong> resolvida pelo algoritmo Dual Simplex do solver HiGHS:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th>Métrica de Auditoria Matemática</th>
                    <th style="text-align: right;">Solução Inteira (MIP)</th>
                    <th style="text-align: right;">Relaxação Linear (LP)</th>
                    <th style="text-align: center;">Gap de Integralidade</th>
                    <th style="text-align: center;">Diagnóstico Poliedral</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Custo Total Objetivo (Cenário S0)</strong></td>
                    <td style="text-align: right; font-weight: bold;">R$ 43.837.633,31</td>
                    <td style="text-align: right; font-family: monospace;">R$ 43.837.384,79</td>
                    <td style="text-align: center; font-weight: bold; color: #15803d;">0,00057% (R$ 248,52)</td>
                    <td style="text-align: center;"><span class="badge-status badge-ok">FORMULAÇÃO QUASE-IDEAL</span></td>
                </tr>
                <tr>
                    <td><strong>Cenário de Estresse Poliedral (Instância Não Restrita)</strong></td>
                    <td style="text-align: right; font-weight: bold;">R$ 144.655.151,14</td>
                    <td style="text-align: right; font-family: monospace;">R$ 144.654.664,37</td>
                    <td style="text-align: center; font-weight: bold; color: #15803d;">0,00033% (R$ 486,77)</td>
                    <td style="text-align: center;"><span class="badge-status badge-ok">GAP QUASE-NULO</span></td>
                </tr>
                <tr>
                    <td><strong>Tempo de Processamento do Solver HiGHS</strong></td>
                    <td style="text-align: right;">8,92 segundos</td>
                    <td style="text-align: right;">0,56 segundos</td>
                    <td style="text-align: center;">&Delta; = 8,36s</td>
                    <td style="text-align: center;"><span class="badge-status badge-ok">CONVERGÊNCIA INSTANTÂNEA</span></td>
                </tr>
            </tbody>
        </table>

        <p style="font-size: 8.5pt; color: #334155; margin-top: 8px;">
            <em>Análise de Preços-Sombra (Shadow Prices) e Gargalos Operacionais:</em> Os multiplicadores duais foram extraídos da <strong>relaxação linear contínua (LP)</strong> da instância S0. Nessa relaxação, a <strong>restrição orçamentária mensal ($B_t$) mostrou-se ativa em 41,7% a 66,7% dos períodos</strong>, com multiplicadores duais positivos de até 2,10 (isto é, na relaxação LP, cada R$ 1,00 adicional em $B_t$ reduziria localmente o objetivo em até R$ 2,10 em penalidades de risco residual). Ressalva-se que, em problemas inteiros, <strong>não há teoria de dualidade forte equivalente</strong>: os preços-sombra da LP constituem indicadores aproximados de sensibilidade e <em>não devem ser interpretados como efeitos marginais exatos no problema MILP</em>, cuja resposta a variações orçamentárias é descontínua e deve ser aferida por reotimização paramétrica (Seção 9.4). Por sua vez, a restrição de capacidade das oficinas ($H_t$) não foi vinculante em nenhum mês da simulação (<strong>0,0% dos meses</strong>, multiplicador dual nulo). Esse resultado indica apenas que, <em>sob os parâmetros agregados de capacidade adotados no cenário S0</em>, o orçamento antecede a capacidade como restrição limitante; ele <strong>não comprova a existência de capacidade ociosa real em toda a rede credenciada catarinense</strong>, pois $H_t$ foi parametrizado de forma agregada e não captura gargalos locais, sazonais, de especialidade mecânica ou de distância geográfica entre unidades e oficinas.
        </p>

        <p style="font-size: 8pt; color: #475569; background: #f8fafc; border-left: 3px solid #64748b; padding: 6px 10px; margin: 8px 0;">
            <strong>Moderação Metodológica das Conclusões Operacionais:</strong> Os ganhos de eficiência prescritiva estimados não devem ser interpretados como economia contábil automática e infalível, mas como o limite superior de otimização teórica sob perfeita execução dos planos preditivos. No setor público real, a materialização desses benefícios é condicionada à tempestividade dos empenhos orçamentários mensais, ao cumprimento dos cronogramas preventivos pelos órgãos setoriais e à mitigação de gargalos logísticos locais.
        </p>

        <div id="secao-9-4">
        <h3>9.4 Curva de Sensibilidade Paramétrica e Fronteira de Saturação Orçamentária</h3>
        </div>
        <p>
            Avaliou-se a resposta da política ótima sob choques orçamentários variando de 70% a 130% do orçamento nominal de referência $B_t$:
        </p>

        <table>
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="text-align: center;">Nível Orçamentário</th>
                    <th style="text-align: right;">Teto Trienal Alocado</th>
                    <th style="text-align: right;">Custo Direto (R$)</th>
                    <th style="text-align: right;">Risco Residual (R$)</th>
                    <th style="text-align: right;">Custo Total (R$)</th>
                    <th style="text-align: center;">Disp. Frota</th>
                    <th style="text-align: center;">Intervenções</th>
                    <th style="text-align: center;">Comportamento Decisório</th>
                </tr>
            </thead>
            <tbody>
                {tabela_sensibilidade_milp_html}
            </tbody>
        </table>

        {render_figura_inline(14)}
        {render_figura_inline(93)}

        <p style="font-size: 8.5pt; color: #334155; margin-bottom: 12px;">
            <em>Ponto de Saturação Econômica e Estabilidade Assintótica:</em> Observa-se que acréscimos orçamentários acima de 115% do nominal conduzem à plena saturação (estabilização em 42.758 intervenções e disponibilidade de 95,54%), indicando que todo o passivo de intervenções com retorno sobre o investimento positivo já foi exaurido, demonstrando a racionalidade econômica estrita da política prescritiva.
        </p>

        <!-- CAPÍTULO 10 -->
        <div id="capitulo-10">
        <h1>10 TEORIA DOS GRAFOS & REDES COMPLEXAS NA GESTÃO DE FROTAS PÚBLICAS</h1>
        </div>
        <p>
            A modelagem de redes complexas articulou duas camadas topológicas complementares: (1) a <strong>rede bipartida de afiliação e fluxo financeiro entre 7.291 veículos e 1.039 estabelecimentos credenciados</strong>, na qual o algoritmo de Louvain detectou <strong>18 comunidades regionais de oficinas com modularidade Q = 0,5646</strong> (Figura 94), revelando a estruturação territorial dos serviços de manutenção; e (2) o <strong>grafo de co-ocorrência mecânica de falhas e sistemas críticos</strong>, que particionou os defeitos em <strong>4 comunidades físicas coesas com modularidade Q = 0,384</strong> (Figura 95), mapeando como o colapso na transmissão e suspensão transmite vibrações que induzem quebras subsequentes no subsistema de freios. Adicionalmente, avaliou-se a dinâmica estocástica de estados operacionais de Markov (Figura 96) e o subgrafo induzido de anomalias críticas para triagem de auditoria (Figura 97).
        </p>

        {render_figura_inline(94)}
        {render_figura_inline(95)}
        {render_figura_inline(96)}
        {render_figura_inline(97)}

        <div class="box-destaque" style="margin-top: 10px; margin-bottom: 12px; font-size: 8.5pt;">
            <strong>Ressalva Epistemológica sobre Análise de Redes e Suspeitas de Conluio (Figura 97):</strong>
            <p style="margin: 4px 0 0 0;">
                A identificação de componentes conexos densos (cliques) ou agrupamentos fortemente conectados entre veículos e estabelecimentos mecânicos constitui um <strong>instrumento analítico de triagem investigativa</strong>, mas <em>não demonstra, isoladamente, a existência de conluio, cartelização ou superfaturamento</em>. No setor público estadual, padrões de concentração transacional decorrem comumente de variáveis operacionais legítimas, tais como a proximidade geográfica entre batalhões/delegacias e as oficinas credenciadas locais, a exclusividade técnica de concessionárias autorizadas para determinadas marcas ou a especialização em tipos específicos de reparo (ex: retífica pesada ou blindagem).
            </p>
            <p style="margin: 4px 0 0 0;">
                Portanto, <strong>o montante financeiro de R$ 4,18 milhões associado a esses agrupamentos representa o volume total transacionado sob priorização de auditoria amostral</strong>, e não deve ser interpretado como irregularidade financeira, dano ao erário ou superfaturamento comprovado. A teoria dos grafos opera estritamente como suporte à fiscalização dirigida da SEA/SC e do Tribunal de Contas (TCE-SC), cuja confirmação probatória depende invariavelmente de perícia documental e verificação contextual in loco.
            </p>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width: 6%; text-align: center;">Pos.</th>
                    <th style="width: 36%;">Estabelecimento Mecânico Credenciado</th>
                    <th style="width: 18%; text-align: center;">Grau de Conexão (k)</th>
                    <th style="width: 15%; text-align: center;">Betweenness (CB)</th>
                    <th style="width: 12%; text-align: center;">PageRank</th>
                    <th style="width: 13%; text-align: center;">Diagnóstico</th>
                </tr>
            </thead>
            <tbody>
                {tabela_hubs_html}
            </tbody>
        </table>

        <!-- CAPÍTULO 11 -->
        <div id="capitulo-11">
        <h1>11 GOVERNANÇA PÚBLICA, MATRIZ DOS 38 INDICADORES GFI E CARTILHA SEA 2026</h1>
        </div>
        <p>
            Apresenta-se a matriz exaustiva completa dos 38 indicadores oficiais da Cartilha GFI da SEA/SC e a relação dos 313 veículos sinalizados pelo critério comparativo de antieconomicidade (&gt;40% do valor venal contábil), que concentram R$ 11,69 milhões em despesas históricas de oficina. A eventual desincorporação depende de laudo e deliberação da comissão patrimonial (Decreto SC nº 2.056/2009); o montante não representa economia realizada.
        </p>

        <table>
            <thead>
                <tr>
                    <th style="width: 10%; text-align: center;">Código</th>
                    <th style="width: 38%;">Indicador Oficial Monitorado</th>
                    <th style="width: 20%; text-align: center;">Valor Apurado</th>
                    <th style="width: 20%;">Parâmetro Normativo de Referência</th>
                    <th style="width: 12%; text-align: center;">Diagnóstico</th>
                </tr>
            </thead>
            <tbody>
                {tabela_38_html}
            </tbody>
        </table>

        <div class="box-aviso">
            <strong>Critério Normativo de Antieconomicidade (Decretos SC nº 1.488/2008 e nº 2.056/2009; Benchmarking Dec. MG nº 47.539/2018, Art. 5º):</strong><br>
            Abaixo são destacados os 10 veículos mais críticos dentre os <strong>313 identificados em estado antieconômico</strong>, cuja despesa acumulada de manutenção supera 40% do valor venal contábil:
        </div>

        <table>
            <thead>
                <tr>
                    <th>Identificador do Bem (Anonimizado - LGPD)</th>
                    <th>Modelo</th>
                    <th>Órgão</th>
                    <th style="text-align: center;">Idade</th>
                    <th style="text-align: right;">Gasto Acumulado</th>
                    <th style="text-align: right;">Valor Venal</th>
                    <th style="text-align: center;">% Venal</th>
                    <th style="text-align: center;">Decisão</th>
                </tr>
            </thead>
            <tbody>
                {tabela_leilao_html}
            </tbody>
        </table>

        {render_figura_inline(87)}
        {render_figura_inline(92)}

        <h3>11.1 Projeção Orçamentária Trienal (2027–2029) com Inflação Setorial Ponderada (6,08% a.a.)</h3>
        <table>
            <thead>
                <tr>
                    <th style="text-align: center;">Exercício</th>
                    <th style="text-align: right;">Cenário Inercial (As-Is)</th>
                    <th style="text-align: right;">Prescritivo Otimizado (To-Be)</th>
                    <th style="text-align: right;">Economia Líquida Anual</th>
                    <th>Status e Premissas Normativas</th>
                </tr>
            </thead>
            <tbody>
                {tabela_projecao_html}
            </tbody>
        </table>

        <!-- CAPÍTULO 12: GALERIA COMPLETA DE TODAS AS 97 FIGURAS -->
        <div id="capitulo-12">
        <h1>12 GALERIA EXAUSTIVA E ANÁLISE EXPLICATIVA DE TODAS AS 97 FIGURAS DA PESQUISA</h1>
        </div>
        <p>
            Em atendimento estrito aos princípios de reprodutibilidade científica e transparência gerencial, este capítulo apresenta o rol exaustivo de <strong>todas as 97 ilustrações geradas no projeto de pesquisa</strong>. Cada figura é apresentada em alta definição (300 DPI) em layout tabular fixo, acompanhada dos quatro tópicos estruturais de diagnóstico, causa raiz, impacto orçamentário e diretriz prescritiva GFI/SEA:
        </p>

        {galeria_todas_figuras_html}

        <!-- CAPÍTULO 13 -->
        <div id="capitulo-13">
        <h1>13 CONCLUSÕES, SUSTENTAÇÃO DAS HIPÓTESES E RECOMENDAÇÕES ACADÊMICAS</h1>
        </div>
        <p>
            A presente dissertação investigou a aplicação integrada de técnicas de aprendizado de máquina, inteligência artificial explicável, teoria dos grafos e programação matemática à gestão de frotas públicas. Os experimentos permitiram avaliar as quatro hipóteses formuladas, identificando resultados favoráveis à otimização prescritiva no cenário simulado, ganhos preditivos modestos decorrentes da integração de bases administrativas e limitações na concordância entre métodos de explicabilidade. Os resultados devem ser interpretados à luz das condições experimentais, das características dos dados utilizados e da ausência de validação prospectiva da economia projetada.
        </p>

        <div class="box-destaque">
            <strong>Síntese da Sustentação das 4 Hipóteses Centrais de Pesquisa e Discussão Epistemológica:</strong>
            <ol style="margin: 3px 0 0 16px; padding: 0;">
                <li><strong>Hipótese H1, NÃO SUSTENTADA SEGUNDO O CRITÉRIO DE RELEVÂNCIA PRÁTICA (apesar de ganho estatístico significante com p &lt; 10^-6):</strong>
                    <br><em>Classificação epistemológica:</em> Sob a ótica puramente inferencial/estatística, a hipótese de ganho preditivo foi formalmente confirmada (Wilcoxon pareado p &lt; 10^-6). Contudo, sob o critério analítico de corte adotado na discussão (patamar referencial de 15,0% de ganho como exigência de relevância prática para justificar os custos operacionais e a sobrecarga de governança na integração contínua de bases heterogêneas no setor público), a hipótese H1 classifica-se formal e conclusivamente como <strong>NÃO SUSTENTADA</strong> (ganho observado de apenas 1,13% no teste out-of-time e 0,41% no estudo ablativo).
                    <br><em>O que foi observado:</em> No conjunto final de teste temporal out-of-time, a incorporação de variáveis multimodais de cadastro patrimonial e abastecimento reduziu o MAE de R$ 2.261,67 para R$ 2.236,06 (redução absoluta de R$ 25,61, correspondendo a aproximadamente <strong>1,13%</strong>), enquanto no estudo ablativo de dobras temporais a redução foi de R$ 2.321,28 para R$ 2.311,82 (Δ = R$ 9,47/OS, correspondendo a <strong>+0,41% [IC 95%: 0,28%; 0,54%]</strong>, com elevação do PR-AUC de 0,9477 para 0,9510, ou +0,35%).
                    <br><em>Por que ocorreu:</em> A base transacional de ordens de serviço já concentra a maior parcela da variância explicável do desgaste mecânico a curto e médio prazos (sistemas afetados, itens substituídos e frequência recente de intervenções). Os atributos de patrimônio e abastecimento trazem sinal complementar, porém atenuado por ruídos cadastrais históricos e pela periodicidade espaçada dos abastecimentos.
                    <br><em>Limitação da interpretação:</em> O ganho modesto restringe-se às fontes administrativas indiretas disponíveis; não se pode inferir que telemetria física contínua (ex.: sensores IoT via CAN bus em alta frequência) produziria o mesmo comportamento marginal.
                    <br><em>Consequência prática e metodológica:</em> A comprovação de ganho estatístico sem relevância prática operacional demonstra que modelos focados exclusivamente no histórico de OSs oferecem excelente custo-benefício, desaconselhando investimentos vultosos em fusão contínua de bases heterogêneas legadas sem telemetria em tempo real.
                </li>
                <li style="margin-top: 8px;"><strong>Hipótese H2, PARCIALMENTE SUSTENTADA:</strong>
                    <br><em>O que foi observado:</em> Os modelos ensemble baseados em árvores (<em>HistGradientBoosting</em> e <em>Extra Trees</em>) superaram categoricamente o regressor vetorial de suporte (<em>SVR-RBF</em>) em precisão preditiva (MAE de R$ 2.236,06 vs R$ 2.569,20, teste pareado de Wilcoxon p &lt; 10^-4) e em viabilidade computacional de treinamento (1,8s para o HistGB vs escala assintótica $O(N^2)$ do SVR-RBF em 77.867 registros, que se tornou proibitiva para re-treinamento contínuo em produção). Na tarefa de classificação de risco operacional, o HistGB superou amplamente a Regressão Logística (ROC-AUC de 0,8743 vs 0,8268, teste de DeLong Z = 16,39; p &lt; 10^-50; PR-AUC de 0,9510 vs 0,8837). Contudo, na regressão de custos contra o baseline ingênuo de mediana amostral, o HistGB (MAE de R$ 2.236,06) não superou a mediana (R$ 2.133,49, variação de -4,81%), embora tenha superado a mediana com folga na métrica de dispersão quadrática RMSE (R$ 3.780,20 vs R$ 4.199,01, redução de 9,97%).
                    <br><em>Por que ocorreu:</em> A distribuição empírica dos custos de ordens de serviço exibe assimetria positiva severa (skewness &gt; 9,8 e curtose elevada), caracterizada por grande volume de intervenções rotineiras de baixo custo e uma cauda longa de reformas estruturais e manutenções pesadas de alto valor. Matematicamente, a mediana amostral é o minimizador teórico ótimo da perda $L_1$ (MAE), ao passo que regressores treinados sob perda quadrática minimizam a média condicional ($L_2$). Ao ser avaliado em MAE, o modelo ensemble é penalizado pelas previsões influenciadas pela cauda direita da distribuição.
                    <br><em>Limitação da interpretação:</em> Esse resultado não indica ineficácia da modelagem ensemble, mas explicita a tensão matemática fundamental entre funções de perda em distribuições assimétricas com caudas pesadas.
                    <br><em>Consequência prática e metodológica:</em> A sofisticação algorítmica não substitui a reflexão sobre o objetivo de negócio do gestor público. Para projeções orçamentárias agregadas e controle de risco fiscal (onde desvios extremos geram rombos orçamentários), o HistGB é a escolha metodológica correta por minimizar a variância total (RMSE 9,97% menor); para a precificação de ordens rotineiras individuais no dia a dia das oficinas, estimadores robustos baseados na mediana constituem uma heurística operacional sólida. Em frentes analíticas complementares, o <em>Isolation Forest</em> isolou <strong>662 OSs anômalas</strong> (0,85%) e a modelagem em grafos detectou 18 comunidades de fornecedores (Louvain Q = 0,565), operando como suporte eficaz à triagem fiscal.
                </li>
                <li style="margin-top: 8px;"><strong>Hipótese H3, SUSTENTADA NO CENÁRIO S0 E SIMULAÇÃO TRIENAL:</strong>
                    <br><em>O que foi observado:</em> O modelo prescritivo canônico MILP convergiu para o ótimo global com <strong>Gap de Otimalidade certificado pelo solver HiGHS de 0,0000%</strong> e diferença relativa para a relaxação linear de <strong>0,00057% (R$ 248,52)</strong> no Cenário S0 (2.000 veículos monitorados mensalmente ao longo de 36 períodos, triênio 2027–2029). O custo To-Be obtido foi de <strong>R$ 43.837.633,31</strong> frente à linha de base inercial de R$ 53.139.780,57, propiciando uma <strong>economia líquida estimada no cenário simulado S0 de R$ 9.302.147,26 (17,51% sobre a linha de base inercial)</strong>, com 95,26% de disponibilidade média e 100% de cumprimento compulsório das manutenções mandatórias. A extrapolação contrafactual via simulação estocástica de Monte Carlo projeta potencial de contenção de despesas de até <strong>R$ 40.088.374,00 no triênio 2027–2029</strong> sob rampa inflacionária setorial de 6,08% a.a.
                    <br><em>Por que ocorreu:</em> O solver explora janelas temporais de agrupamento de serviços e antecipa intervenções preventivas de custo moderado antes que falhas severas imponham custos de guincho, horas paradas e substituições de grandes conjuntos mecânicos.
                    <br><em>Limitação da interpretação:</em> Os resultados representam uma simulação prescritiva contrafactual baseada em parâmetros calibrados na instância S0; a materialização efetiva da economia na prática depende da tempestividade na liberação de empenhos orçamentários pelos órgãos setoriais e da adesão estrita dos gestores aos planos gerados.
                    <br><em>Consequência prática e metodológica:</em> A pesquisa comprova a viabilidade matemática e computacional de solvers exatos de código aberto para frotas públicas de grande porte, assegurando fechamento aritmético auditável centavo a centavo.
                </li>
                <li style="margin-top: 8px;"><strong>Hipótese H4, NÃO SUSTENTADA NO LIMIAR A PRIORI (&gt; 85%):</strong>
                    <br>A hipótese H4 não foi sustentada segundo o limiar de concordância previamente estabelecido. A comparação entre as atribuições explicativas de SHAP e LIME apresentou <strong>similaridade de Jaccard Top-5 de 39,29% (39,3%)</strong> e <strong>correlação de postos de Spearman de &rho; = 0,3680</strong>, valores inferiores ao critério de 85% definido para a hipótese.
                    <br>Os resultados indicam divergência relevante entre as explicações produzidas pelos dois métodos nas condições experimentais avaliadas. Entretanto, não permitem concluir que SHAP e LIME sejam universalmente incompatíveis ou que um dos métodos seja necessariamente superior ao outro.
                    <br>Do ponto de vista da gestão pública, essa divergência recomenda cautela na utilização de explicações algorítmicas como fundamento exclusivo para decisões administrativas. A adoção de mecanismos de triangulação, avaliação da estabilidade das explicações e supervisão humana especializada constitui uma direção metodológica pertinente para aplicações futuras.
                </li>
            </ol>
        </div>

        <div id="secao-13-1">
        <h2>13.1 Validade Externa, Condições de Contorno e Generalização da Arquitetura Prescritiva</h2>
        </div>
        <p>
            A arquitetura apresenta potencial de adaptação a outros entes federativos, condicionado à compatibilidade estrutural e semântica das bases administrativas, à disponibilidade dos atributos requeridos e à parametrização das restrições normativas e operacionais locais. Conforme as características dos sistemas institucionais, poderão ser necessárias adaptações nas rotinas de ingestão, integração, processamento e validação dos dados.
        </p>
        <p>
            Essa dimensão foi estruturada sobre quatro pilares metodológicos centrais, complementados por um teste computacional de portabilidade algorítmica sobre benchmark sintético calibrado (Base B):
        </p>
        <p>
            <strong>Dimensão 1, Diversidade Amostral e Heterogeneidade Operacional Interna:</strong> Os 34.280 veículos e 77.867 ordens de serviço catalogados no Estado de Santa Catarina contemplam múltiplos regimes de severidade operacional pública: frotas de alta exigência mecânica contínua (viaturas da Polícia Militar e Polícia Civil, sujeitas a acelerações severas e desgaste prematuro de freios e suspensão), frotas logísticas de saúde e transporte de pacientes, fiscalização agropecuária e veículos administrativos leves da SEA/SC. Essa amplitude empírica interna enriquece a variabilidade dos dados e evita o sobreajuste a um único perfil institucional. Ressalta-se, contudo, que tal diversidade interna opera como condição facilitadora de robustez estatística, <em>não constituindo garantia formal de validade externa interfederativa</em>, a qual demanda averiguação em outras unidades jurisdicionadas.
        </p>
        <p>
            <strong>Dimensão 2, Parametrização Exógena e Portabilidade Normativa Interfederativa:</strong> O pipeline analítico e a modelagem MILP foram construídos sob estrito desacoplamento entre formulação matemática e parâmetros normativos locais. O teto de antieconomicidade de 40% (utilizado nesta pesquisa como parâmetro comparativo e benchmarking de simulação, inspirado no Art. 5º do Decreto MG nº 47.539/2018), os prazos de desincorporação patrimonial (Decretos SC nº 1.488/2008 e nº 2.056/2009), o orçamento disponível ($B_t$) e os limites de capacidade técnica ingressam como parâmetros exógenos configuráveis. A arquitetura apresenta potencial de adaptação a outros entes federativos, condicionado à compatibilidade estrutural e semântica das bases administrativas, à disponibilidade dos atributos requeridos e à parametrização das restrições normativas e operacionais locais. Conforme as características dos sistemas institucionais, poderão ser necessárias adaptações nas rotinas de ingestão, integração, processamento e validação dos dados.
        </p>
        <p>
            <strong>Dimensão 3, Compatibilidade com Contratos Baseados em Tabelas Padronizadas:</strong> O arcabouço analítico ancora-se no modelo de contratação de manutenção terceirizada mediante catálogos de tempo-padrão de montadora e tabelas referenciais de peças (como Sintec e Audatex), modelo de contratação utilizado em diferentes administrações públicas sob a Lei Federal nº 14.133/2021. Assim, os algoritmos de detecção de anomalias (Isolation Forest) e os filtros de conferência de itens integram-se de forma nativa aos sistemas de gestão de frotas comumente licitados pelas administrações públicas brasileiras.
        </p>
        <p>
            <strong>Dimensão 4, Resiliência Prescritiva sob Estresse Macroeconômico:</strong> Em 1.000 iterações estocásticas de Monte Carlo sob rampa inflacionária setorial de 6,08% a.a., a estrutura da base de variáveis ativas de decisão do solver HiGHS permaneceu estável em 96,4% dos cenários, indicando solidez estrutural do poliedro frente à volatilidade econômica conjuntural.
        </p>

        <div class="box-aviso" style="margin-top: 14px;">
            <strong style="font-size: 9pt; color: #0f172a;">Diferenciação Epistemológica, Origem e Protocolo Experimental do Benchmark Sintético (Base B):</strong><br>
            Para garantir transparência científica estrita perante a banca examinadora, distinguem-se rigorosamente as três categorias de dados do projeto:
            <ul style="margin: 4px 0 0 16px; padding: 0; line-height: 1.45;">
                <li><strong>Nível 1, Base Empírica Primária Governamental (Santa Catarina):</strong> Conjunto de dados primários reais exaustivos de 77.867 ordens de serviço (350.737 itens) e 34.280 bens patrimoniais transacionados entre 2020 e 2026 no Poder Executivo Catarinense (SEA/SC), sobre o qual todos os modelos estatísticos, grafos Louvain e a política canônica MILP-1 foram treinados e auditados.</li>
                <li><strong>Nível 2, Benchmark Computacional Sintético de Portabilidade Algorítmica (Base B):</strong>
                    <br><em>Origem e Natureza Sintética:</em> Trata-se estritamente de um <strong>benchmark computacional sintético calibrado</strong>, gerado com gerador pseudo-aleatório determinístico (seed 42 fixada em NumPy/Pandas) para modelar um cenário governamental regional autônomo (5.000 ordens de serviço distribuídas entre 500 veículos de operações de saúde e resgate emergencial). <em>A Base B não constitui validação empírica externa nem base institucional real</em>, não compartilhando nenhum identificador, oficina, histórico ou parâmetro com os dados da SEA/SC, assegurando independência amostral completa e ausência de vazamento de dados (<em>zero data leakage</em>) para testar o comportamento do código em outro contexto operacional.
                    <br><em>Protocolo de Avaliação Automatizado:</em> A execução é conduzida pelo script auditado <code>public-fleet-prescriptive-analytics/scripts/10_validacao_externa_institucional.py</code>, com certificação registrada em <code>results/metrics/relatorio_validacao_externa_institucional.json</code> e na trilha de auditoria <code>results/audit/registro_auditoria_ocorrencias.jsonl</code>.
                    <br><em>Métricas Atestadas no Benchmark Sintético (Base B):</em> (i) Capacidade preditiva: <strong>ROC-AUC = 0,8579</strong> e <strong>PR-AUC = 0,9125</strong> na predição out-of-time de falhas graves; (ii) Otimização prescritiva: o solver HiGHS convergiu para o ótimo global com <strong>42,32% de redução no custo total esperado</strong> sob restrições orçamentárias externas e 100,0% de manutenções mandatórias cumpridas; (iii) Verificação da Hipótese H4: replicou-se a divergência entre explicadores locais, com <strong>Jaccard = 33,33%</strong> e <strong>Spearman = 0,3120</strong>, onde observou-se novamente baixa concordância entre os métodos nas condições do benchmark sintético; (iv) Parâmetro de Antieconomicidade dos 40%: <strong>27 veículos (5,4% da frota sintética)</strong> foram sinalizados pelo critério simulado de antieconomicidade.
                    <br><em>Ressalva Metodológica Estrita:</em> Este teste em benchmark sintético demonstra a execução do pipeline no cenário sintético avaliado e a estabilidade numérica das formulações, mas <strong>não substitui validações empíricas prospectivas em bases administrativas de outros entes federativos</strong>, cuja consecução depende de futuros acordos interinstitucionais de cooperação técnica.</li>
                <li><strong>Nível 3, Cenários Contrafactuais Simulados:</strong> Projeções financeiras trienais de Monte Carlo (1.000 iterações estocásticas) que avaliam a resiliência do poliedro frente a choques inflacionários setoriais (6,08% a.a.) e volatilidade de custos mecânicos.</li>
            </ul>
        </div>

        <!-- REFERÊNCIAS (ABNT NBR 6023) -->
        <div class="quebra-pagina"></div>
        <div id="referencias">
        <h1>REFERÊNCIAS</h1>
        </div>

        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            ABBASINEJAD, R. et al. Optimum Maintenance Interval Determination Using Value and Utility Functions. <strong>Computers &amp; Chemical Engineering</strong>, v. 155, p. 107530, 2021.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            BERGMEIR, C.; BENÍTEZ, J. M. On the use of cross-validation for time series predictor evaluation. <strong>Information Sciences</strong>, v. 191, p. 192-213, 2012.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            BERTSIMAS, D.; KALLUS, N. From predictive to prescriptive analytics. <strong>Management Science</strong>, v. 66, n. 6, p. 2445-2476, 2020.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            BIELLI, M. et al. Advanced public transit systems: an operational research overview. <strong>European Journal of Operational Research</strong>, v. 211, n. 2, p. 219-232, 2011.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            BLONDEL, V. D. et al. Fast unfolding of communities in large networks. <strong>Journal of Statistical Mechanics: Theory and Experiment</strong>, v. 2008, n. 10, p. P10008, 2008.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            BRASIL. <strong>Lei Federal nº 14.133, de 1º de abril de 2021</strong>. Lei de Licitações e Contratos Administrativos. Diário Oficial da União: Brasília, DF, 2021.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            CAO, M. et al. Condition-based maintenance optimization under random deterioration shocks and operational uncertainty. <strong>Journal of Quality in Maintenance Engineering</strong>, v. 29, n. 2, p. 340-358, 2023.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            CAO, Y.; LUO, J.; DONG, W. Optimization of condition-based maintenance for multi-state deterioration systems under random shock. <strong>Applied Mathematical Modelling</strong>, v. 115, p. 80-99, 2023. DOI: 10.1016/j.apm.2022.10.036.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            CHEN, T.; GUESTRIN, C. XGBoost: A Scalable Tree Boosting System. In: <strong>ACM SIGKDD International Conference on Knowledge Discovery and Data Mining</strong>, 22., 2016. Proceedings... San Francisco: ACM, 2016. p. 785-794.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            CHIEN, Y.-H.; SHEU, S.-H.; ZHANG, Z. G. Optimal maintenance policy for a system subject to cumulative damage and deterioration shocks. <strong>Reliability Engineering &amp; System Safety</strong>, v. 106, p. 13-22, 2012.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            CHIKAZHE, L. et al. Fleet management system, perceived service quality and public healthcare logistics performance. <strong>International Journal of Logistics Management</strong>, v. 34, n. 4, p. 1024-1048, 2023.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            CRESPO DEL CASTILLO, A.; PARLIKAD, A. K. Dynamic fleet management: Integrating predictive and preventive maintenance with operational workload balancing. <strong>Reliability Engineering &amp; System Safety</strong>, v. 244, p. 109968, 2024.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            DALZOCHIO, J. et al. Machine learning and reasoning for predictive maintenance in Industry 4.0: Current status and challenges. <strong>Computers in Industry</strong>, v. 123, p. 103298, 2020.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            DE CASTRO, H. F.; CAVALCA, K. L. Maintenance resources optimization applied to a fleet of vehicles under budget constraints. <strong>Reliability Engineering &amp; System Safety</strong>, v. 91, n. 4, p. 413-424, 2006.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            DELONG, E. R.; DELONG, D. M.; CLARKE-PEARSON, D. L. Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. <strong>Biometrics</strong>, v. 44, n. 3, p. 837-845, 1988.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            DIVYA, D.; MARATH, B.; MOHANDAS, K. Review of fault detection techniques for automotive vehicle fleets. <strong>Journal of Quality in Maintenance Engineering</strong>, v. 28, n. 3, p. 574-596, 2022.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            EKŞIOĞLU, B.; VOß, S.; HIRSCH, P. Fifty years of vehicle routing: An overview of taxonomies and heuristic solution methods. <strong>Computers &amp; Industrial Engineering</strong>, v. 57, n. 3, p. 627-638, 2009.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            ERKOYUNCU, J. A. et al. Perspectives on trading cost and availability for service delivery after-market. <strong>Reliability Engineering &amp; System Safety</strong>, v. 168, p. 272-286, 2017.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            ES-SAKALI, N. et al. Review of predictive maintenance algorithms applied to thermal HVAC systems. <strong>Energy Reports</strong>, v. 8, p. 112-124, 2022.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            ESTEBAN, A. et al. Data mining in predictive maintenance systems: A systematic taxonomy and review. <strong>Wiley Interdisciplinary Reviews: Data Mining and Knowledge Discovery</strong>, v. 12, n. 5, p. e1462, 2022.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            FENG, Y. et al. Multi-agent reinforcement learning for maintenance and mission reliability in fleet operations. <strong>Reliability Engineering &amp; System Safety</strong>, v. 165, p. 182-194, 2017.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            FREEMAN, L. C. A set of measures of centrality based on betweenness. <strong>Sociometry</strong>, v. 40, n. 1, p. 35-41, 1977.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            HASHEMIAN, H. M. Wireless sensors for predictive maintenance of critical equipment. <strong>Annals of Nuclear Energy</strong>, v. 38, n. 2-3, p. 665-680, 2011.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            HU, C.; ZHANG, L.; LIANG, W. Opportunistic maintenance policies for systems subject to component dependencies. <strong>IEEE Transactions on Reliability</strong>, v. 61, n. 2, p. 531-541, 2012.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            IZDEBSKI, M. et al. Selection of a fleet of vehicles for transport tasks using genetic algorithms and heuristic search. <strong>Eksploatacja i Niezawodnosc – Maintenance and Reliability</strong>, v. 24, n. 3, p. 450-461, 2022.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            JADHAV, S. et al. Artificial intelligence and data science applications in engineering maintenance: A modern review. <strong>Journal of Industrial Information Integration</strong>, v. 43, p. 100654, 2025.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            KAPOOR, S.; NARAYANAN, A. Leakage and the reproducibility crisis in machine-learning-based science. <strong>Patterns</strong>, v. 4, n. 9, p. 100804, 2023.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            KUNZ, N.; VAN WASSENHOVE, L. N.; BESIOU, M. Centralized vehicle leasing in humanitarian operations: Economic and operational trade-offs. <strong>Journal of Humanitarian Logistics and Supply Chain Management</strong>, v. 5, n. 1, p. 4-23, 2015.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            LADJ, A.; VARNIER, C.; ZERHOUNI, N. Exact and heuristic algorithms for post prognostic decision making: A joint scheduling and maintenance problem. <strong>International Journal of Production Research</strong>, v. 58, n. 11, p. 3432-3450, 2020.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            LEI, Y.; SANDBORN, P. Maintenance scheduling of offshore wind farms based on remaining useful life estimation. <strong>Renewable Energy</strong>, v. 125, p. 770-781, 2018.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            LIU, Y.-Y.; CHANG, K.-H.; CHEN, Y.-Y. Simultaneous predictive maintenance and inventory policy in a continuously monitoring system using simulation optimization. <strong>Computers &amp; Operations Research</strong>, v. 153, p. 106146, 2023. DOI: 10.1016/j.cor.2023.106146.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            LUNDBERG, S. M.; LEE, S.-I. A Unified Approach to Interpreting Model Predictions. In: <strong>Advances in Neural Information Processing Systems (NeurIPS)</strong>, 30., 2017. Proceedings... Long Beach: Curran Associates, 2017. p. 4765-4774.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            MAHALE, A.; KOLHAR, M.; MORE, P. Predictive maintenance in automotive vehicles: a systematic literature review. <strong>Journal of Big Data</strong>, v. 12, n. 1, p. 45, 2025.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            MALCOLM, C. et al. Mobile-Source Emissions: Analysis of Spatial Patterns of Vehicle Usage and Trip Generation. <strong>Transportation Research Record</strong>, v. 1842, n. 1, p. 69-78, 2003.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            MINAS GERAIS. <strong>Decreto Estadual nº 47.539, de 14 de novembro de 2018</strong>. Dispõe sobre a gestão de veículos oficiais e critérios de antieconomicidade para desfazimento e leilão no âmbito da Administração Pública Estadual. Belo Horizonte: Diário Oficial de Minas Gerais, 2018.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            MONTERO JIMENEZ, J. J. et al. Towards multi-model approaches to predictive maintenance: A systematic review and data fusion perspective. <strong>Journal of Manufacturing Systems</strong>, v. 56, p. 539-557, 2020.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            PASSING, H.; BABLOK, W. A new biometrical procedure for testing the equality of measurements from two different analytical methods. <strong>Journal of Clinical Chemistry and Clinical Biochemistry</strong>, v. 21, n. 11, p. 709-720, 1983.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            PEDRAZA MARTINEZ, A. J. et al. Field vehicle fleet management in humanitarian operations. <strong>Journal of Operations Management</strong>, v. 29, n. 5, p. 404-421, 2011.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            POINSIGNON, M. et al. Operational scenarios for public transit electrification: Total cost of ownership and operational simulation. <strong>Transportation Research Part D: Transport and Environment</strong>, v. 104, p. 103195, 2022.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            REDMER, A. Strategic vehicle fleet management–a joint replacement and sizing problem. <strong>Journal of Quality in Maintenance Engineering</strong>, v. 28, n. 1, p. 156-180, 2022.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            REGAN, A. C.; MAHMASSANI, H. S.; JAILLET, P. Evaluation of Dynamic Fleet Management Systems: A Simulation Framework. <strong>Transportation Research Record</strong>, v. 1645, n. 1, p. 38-44, 1998.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            REN, Z. Machine learning and system reliability: Statistical modeling and predictive analytics. <strong>Reliability Engineering &amp; System Safety</strong>, v. 209, p. 107458, 2021.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            RIBEIRO, M. T.; SINGH, S.; GUESTRIN, C. "Why Should I Trust You?": Explaining the Predictions of Any Classifier. In: <strong>ACM SIGKDD International Conference on Knowledge Discovery and Data Mining</strong>, 22., 2016. Proceedings... San Francisco: ACM, 2016. p. 1135-1144.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            ROKHFOROZ, P.; FINK, O. Hierarchical multi-agent predictive maintenance scheduling for railway infrastructure. <strong>Computers &amp; Industrial Engineering</strong>, v. 156, p. 107250, 2021.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            RUDIN, C. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. <strong>Nature Machine Intelligence</strong>, v. 1, n. 5, p. 206-215, 2019.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            SANTA CATARINA. <strong>Decreto Estadual nº 1.488, de 22 de janeiro de 2008</strong>. Dispõe sobre o uso, circulação, abastecimento, controle e conservação de veículos oficiais do Poder Executivo Estadual. Florianópolis: Diário Oficial do Estado de Santa Catarina (DOE/SC), 2008.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            SANTA CATARINA. <strong>Decreto Estadual nº 2.056, de 28 de janeiro de 2009</strong>. Regulamenta o processo de desfazimento, alienação e leilão de veículos e bens inservíveis e antieconômicos no âmbito da Administração Pública Estadual. Florianópolis: Diário Oficial do Estado de Santa Catarina (DOE/SC), 2009.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            SANTA CATARINA. Secretaria de Estado da Administração (SEA). <strong>Cartilha de Gestão de Frota por Indicadores (GFI)</strong>. Diretoria de Gestão Patrimonial: Florianópolis, SC, Edição Abr/2026.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            SHENG, J.; PRESCOTT, D. A colored Petri net model for aircraft fleet maintenance scheduling and logistics. <strong>Reliability Engineering &amp; System Safety</strong>, v. 189, p. 67-86, 2019.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            SØRENSEN, C. G.; BOCHTIS, D. D. Conceptual model of fleet management in agricultural operations. <strong>Biosystems Engineering</strong>, v. 105, n. 1, p. 41-50, 2010.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            STOJIĆ, G. et al. A fuzzy model for determining the justification of investment in road freight transport fleets. <strong>Operational Research in Engineering Sciences: Theory and Applications</strong>, v. 1, n. 1, p. 47-59, 2018.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            TANG, J. et al. Joint condition-based maintenance and spare parts ordering policy under hidden deterioration states. <strong>Annals of Operations Research</strong>, v. 332, p. 415-438, 2025.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            TAYLOR, S. J.; LETHAM, B. Forecasting at scale. <strong>The American Statistician</strong>, v. 72, n. 1, p. 37-45, 2018.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            VAN DINTER, R. et al. Predictive maintenance using digital twins: A systematic literature review. <strong>Information and Software Technology</strong>, v. 151, p. 107008, 2022.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            VUJANOVIĆ, D. et al. Evaluation of vehicle fleet maintenance management using DEMATEL-ANP multicriteria approach. <strong>Expert Systems with Applications</strong>, v. 39, n. 12, p. 10990-11003, 2012.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            WANG, F. et al. Surface mining haul fleet management: Operational optimization and carbon emissions abatement. <strong>Resources Policy</strong>, v. 89, p. 104523, 2024.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            WIKSTRÖM, M. et al. Socio-technical experiences from electric vehicle adoption in commercial fleets. <strong>Applied Energy</strong>, v. 123, p. 82-93, 2014.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            YOON, J. T. et al. Cost-sensitive predictive maintenance under asymmetric misclassification costs. <strong>Reliability Engineering &amp; System Safety</strong>, v. 188, p. 208-220, 2019.
        </p>
        <p class="sem-recuo" style="font-size: 8pt; margin-bottom: 6px;">
            ZHENG, R.; WANG, J.; ZHANG, Y. A hybrid repair-replacement policy in the proportional hazards model. <strong>European Journal of Operational Research</strong>, v. 304, n. 3, p. 1011-1021, 2022. DOI: 10.1016/j.ejor.2022.05.020.
        </p>

        <!-- APÊNDICE A: FORMULAÇÃO MILP -->
        <div id="apendice-a">
        <h1>APÊNDICE A, FORMULAÇÃO MATEMÁTICA COMPLETA E LINEARIZADA DO SOLVER MILP</h1>
        </div>
        <p>
            O problema de alocação ótima e escalonamento de manutenções com restrição de capacidade e orçamento para a frota do Estado de Santa Catarina é formulado canonicamente como segue:
        </p>
        <div class="box-formula">
            <strong>Função Objetivo Canônica:</strong><br>
            min &sum;_(t=1)^T &sum;_(i=1)^N [ &alpha; &middot; c_it x_it + &beta; &middot; r_it (1 - x_it) ]<br><br>
            <strong>Restrições Operacionais e Orçamentárias:</strong><br>
            1. Teto Orçamentário Mensal: &sum;_(i=1)^N c_it x_it &le; B_t, &nbsp; &forall; t &isin; &#123;1, ..., T&#125;<br>
            2. Capacidade Operacional de Oficinas (Horas): &sum;_(i=1)^N h_it x_it &le; H_t, &nbsp; &forall; t &isin; &#123;1, ..., T&#125;<br>
            3. Manutenções Mandatórias de Segurança: x_it &ge; m_it, &nbsp; &forall; (i, t) | m_it = 1<br>
            4. Integralidade e Domínio: x_it &isin; &#123;0, 1&#125;, &nbsp; &forall; i &isin; &#123;1, ..., N&#125;, &forall; t &isin; &#123;1, ..., T&#125;
        </div>
        <p style="font-size: 8.5pt; color: #334155; margin-top: 8px;">
            <strong>Métricas Poliedrais e Complexidade Computacional da Instância S0:</strong><br>
            A instância canônica S0 contempla 72.000 variáveis binárias de decisão, correspondentes a 2.000 veículos avaliados ao longo de 36 períodos mensais. O modelo apresenta 6.072 restrições lineares reportadas, compreendendo limites orçamentários, capacidades operacionais e exigências de manutenção mandatória. A quantidade de restrições efetivamente ativas na solução ótima deverá ser determinada a partir dos resultados do solver, não podendo ser inferida exclusivamente da formulação matemática.
        </p>

        <!-- APÊNDICE B: AUDITORIA E INTEGRIDADE PÚBLICA -->
        <div id="apendice-b">
        <h1>APÊNDICE B, PROTOCOLO DE AUDITORIA E INTEGRIDADE PÚBLICA DA SEA DITI</h1>
        </div>
        <p>
            Em estrita conformidade com a Lei Federal nº 14.133/2021, com os princípios constitucionais do devido processo legal e com a Instrução Normativa nº 05/2024 da SEA/SC, o protocolo de auditoria preventiva sobre fornecedores mecânicos compreende:
        </p>
        <ul style="margin-left: 20px; font-size: 8.5pt;">
            <li>Triagem técnica preventiva e solicitação formal de justificativa circunstanciada à oficina credenciada para itens orçados com divergência superior a 2 desvios-padrão da mediana histórica regional, assegurando o contraditório, a ampla defesa e a manifestação pericial do fiscal do contrato antes de qualquer eventual aplicação de glosa definitiva;</li>
            <li>Triagem exploratória e direcionamento de fiscalização pericial presencial para estabelecimentos credenciados agrupados em comunidades de alta densidade financeira e suspeição estrutural (Louvain Q &gt; 0,35), resguardando o contraditório, a ampla defesa e o devido processo administrativo legal (Lei Federal nº 14.133/2021);</li>
            <li>Comunicação formal ao Tribunal de Contas de Santa Catarina (TCE-SC) das ordens atípicas isoladas pelo Isolation Forest para subsidiar auditorias periciais analíticas.</li>
        </ul>

        <!-- APÊNDICE C: REPRODUTIBILIDADE CIENTÍFICA -->
        <div id="apendice-c">
        <h1 style="margin-top: 8pt; margin-bottom: 4pt;">APÊNDICE C, CADERNO METODOLÓGICO DE REPRODUTIBILIDADE E ADERÊNCIA ÀS DIRETRIZES DA ACM E INFORMS</h1>
        </div>
        <p style="font-size: 7.8pt; margin-bottom: 2px;">
            Em alinhamento conceitual com as diretrizes e boas práticas de reprodutibilidade computacional preconizadas pela <strong>Association for Computing Machinery (ACM Artifact Guidelines)</strong> e pela <strong>INFORMS Journal on Computing</strong>, o framework disponibiliza os seguintes artefatos de rastreabilidade:
        </p>
        <ul style="margin-left: 18px; font-size: 7.5pt; margin-top: 2px; margin-bottom: 2px; line-height: 1.2;">
            <li><strong>Semente Aleatória Global:</strong> Seed 42 fixada em todos os componentes estocásticos (particionamento, bootstrapping e validação cruzada) para viabilizar replicação idêntica;</li>
            <li><strong>Dicionário de Variáveis e Linhagem de Dados:</strong> Mapeamento transparente dos 350.737 registros de itens brutos, 274.823 itens saneados (correspondentes a 60.114 OSs cobradas e 77.867 OSs brutas) e da amostra focal de 2.000 veículos monitorados por 36 meses;</li>
            <li><strong>Código Aberto e Solvers Auditáveis:</strong> Emprego exclusivo dos solvers HiGHS e CBC sob formulações matemáticas lineares puras, sem dependência de bibliotecas proprietárias de caixa-preta;</li>
            <li><strong>Rastreamento Experimental:</strong> Suíte automatizada de testes com verificação de invariantes numéricos e integridade de artefatos.</li>
        </ul>

        <h2 style="margin-top: 4px; margin-bottom: 2px; font-size: 9pt;">Apêndice C.1, Registro Factual de Execuções e Portabilidade Multiplataforma</h2>
        <p style="font-size: 7.5pt; margin-bottom: 2px;">
            A tabela a seguir consolida o histórico factual de execuções independentes do pipeline, registrando o ambiente computacional, as entradas fornecidas, os códigos de saída, eventuais falhas e intervenções manuais:
        </p>
        <table style="font-size: 6.5pt; line-height: 1.15; margin-bottom: 2px;">
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 32%; padding: 1px 3px;">Dimensão / Checkpoint Auditado</th>
                    <th style="width: 17%; text-align: center; padding: 1px 3px;">Linux V1</th>
                    <th style="width: 17%; text-align: center; padding: 1px 3px;">Linux V2 (Limpa)</th>
                    <th style="width: 17%; text-align: center; padding: 1px 3px;">Windows 11 (V3)</th>
                    <th style="width: 17%; text-align: center; padding: 1px 3px;">Status de Congruência</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Dimensão Base Processada (OSs / Itens)</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">77.867 / 350.737</td>
                    <td style="text-align: center; padding: 1px 3px;">77.867 / 350.737</td>
                    <td style="text-align: center; padding: 1px 3px;">77.867 / 350.737</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (100% Idêntico)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Painel Longitudinal Veículo-Mês</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">42.278 linhas</td>
                    <td style="text-align: center; padding: 1px 3px;">42.278 linhas</td>
                    <td style="text-align: center; padding: 1px 3px;">42.278 linhas</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (100% Idêntico)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Anomalias Isoladas (Isolation Forest)</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">662 OSs (0,85%)</td>
                    <td style="text-align: center; padding: 1px 3px;">662 OSs (0,85%)</td>
                    <td style="text-align: center; padding: 1px 3px;">662 OSs (0,85%)</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (100% Idêntico)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Economia Cenário S0 MILP (Valor Exato)</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">R$ 9.302.147,26</td>
                    <td style="text-align: center; padding: 1px 3px;">R$ 9.302.147,26</td>
                    <td style="text-align: center; padding: 1px 3px;">R$ 9.302.147,26</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (Diff R$ 0,00)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Solução Inteira Ótima MIP (HiGHS)</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">R$ 43.837.633,31</td>
                    <td style="text-align: center; padding: 1px 3px;">R$ 43.837.633,31</td>
                    <td style="text-align: center; padding: 1px 3px;">R$ 43.837.633,31</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (100% Idêntico)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Gap de Otimalidade do Solver HiGHS</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">0,0000%</td>
                    <td style="text-align: center; padding: 1px 3px;">0,0000%</td>
                    <td style="text-align: center; padding: 1px 3px;">0,0000%</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (Zero Drift)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Gap de Integralidade Poliedral (MIP - LP) / LP</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">0,00057% (R$ 248,52)</td>
                    <td style="text-align: center; padding: 1px 3px;">0,00057% (R$ 248,52)</td>
                    <td style="text-align: center; padding: 1px 3px;">0,00057% (R$ 248,52)</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (100% Idêntico)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>ROC-AUC Validação Temporal (5 Dobras)</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">0,7544 ± 0,0281</td>
                    <td style="text-align: center; padding: 1px 3px;">0,7544 ± 0,0281</td>
                    <td style="text-align: center; padding: 1px 3px;">0,7544 ± 0,0281</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (100% Idêntico)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Verdictos Epistemológicos H1 a H4</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">H1 Não / H2 Parcial<br>H3 Sim / H4 Não</td>
                    <td style="text-align: center; padding: 1px 3px;">H1 Não / H2 Parcial<br>H3 Sim / H4 Não</td>
                    <td style="text-align: center; padding: 1px 3px;">H1 Não / H2 Parcial<br>H3 Sim / H4 Não</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">PASS (Sem HARKing)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Total de Checkpoints Aprovados (Suíte)</strong></td>
                    <td style="text-align: center; padding: 1px 3px;">20 / 20 PASS</td>
                    <td style="text-align: center; padding: 1px 3px;">20 / 20 PASS</td>
                    <td style="text-align: center; padding: 1px 3px;">20 / 20 PASS</td>
                    <td style="text-align: center; color: #15803d; font-weight: bold; padding: 1px 3px;">100% REPRODUTÍVEL</td>
                </tr>
            </tbody>
        </table>
        <div style="background: #f8fafc; border-left: 3px solid #0284c7; padding: 3px 6px; margin: 3px 0; font-size: 7.2pt; color: #334155; line-height: 1.2;">
            <strong>Delimitação Metodológica entre Protocolo A e Protocolo B na Portabilidade Multiplataforma:</strong><br>
            A auditoria experimental estabelece uma distinção rigorosa entre dois protocolos de reprodução:
            <ul style="margin: 2px 0 0 14px; padding: 0;">
                <li><strong>Protocolo A (Base Processada em Parquet com Hashes SHA-256 e Anonimização LGPD):</strong> Apresenta portabilidade plenamente verificada e congruência matemática absoluta entre os ambientes Linux e Windows 11 (zero drift e diferença de R$ 0,00 no fechamento aritmético do solver HiGHS, com 20 de 20 checkpoints aprovados);</li>
                <li><strong>Protocolo B (Ingestão Primária a partir do CSV Bruto de 1,2 GB):</strong> O código de saída 1 observado no script preliminar <code>01_auditoria_dados.py</code> no ambiente Windows decorreu exclusivamente da supressão deliberada do arquivo CSV desanonimizado (<code>Geral_de_OS_23439885_202609110934.csv</code>), retido por imperativo de segurança da informação e proteção de dados pessoais (LGPD). Portanto, o Protocolo B permanece <em>condicionado à disponibilização e custódia institucional dos dados brutos</em>, razão pela qual a portabilidade da pesquisa é demonstrada como plenamente verificada no Protocolo A, não cabendo afirmar portabilidade integral e irrestrita no Protocolo B sem a posse do arquivo primário restrito.</li>
            </ul>
        </div>

        <h3 style="margin-top: 4px; margin-bottom: 2px; font-size: 8.5pt; color: #0f172a;">Indicadores Oficiais de Auditoria e Portabilidade Experimental (Multi-OS)</h3>
        <table style="font-size: 6.5pt; line-height: 1.15; margin-bottom: 2px;">
            <thead>
                <tr style="background: #334155; color: #ffffff;">
                    <th style="width: 28%; padding: 1px 3px;">Indicador de Qualidade</th>
                    <th style="width: 32%; padding: 1px 3px;">Significado Metodológico</th>
                    <th style="width: 18%; text-align: center; padding: 1px 3px;">Valor Mensurado</th>
                    <th style="width: 22%; padding: 1px 3px;">Diagnóstico Técnico</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Taxa de instalação bem-sucedida</strong></td>
                    <td style="padding: 1px 3px;">Capacidade de reconstruir o ambiente computacional e dependências</td>
                    <td style="text-align: center; font-weight: bold; color: #15803d; padding: 1px 3px;">100,0%</td>
                    <td style="padding: 1px 3px;">143 pacotes instalados com êxito em Linux e Windows</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Taxa de execução integral</strong></td>
                    <td style="padding: 1px 3px;">Capacidade de concluir todas as etapas do pipeline analítico</td>
                    <td style="text-align: center; font-weight: bold; color: #15803d; padding: 1px 3px;">100,0% (Prot. A)</td>
                    <td style="padding: 1px 3px;">Conclusão integral no Protocolo A; Protocolo B condicionado à posse do CSV bruto</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Taxa de equivalência numérica</strong></td>
                    <td style="padding: 1px 3px;">Consistência e congruência dos resultados científicos publicados</td>
                    <td style="text-align: center; font-weight: bold; color: #15803d; padding: 1px 3px;">100,0%</td>
                    <td style="padding: 1px 3px;">20 de 20 checkpoints idênticos (zero drift, diff R$ 0,00)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Frequência de falhas</strong></td>
                    <td style="padding: 1px 3px;">Robustez operacional frente a interrupções imprevistas</td>
                    <td style="text-align: center; font-weight: bold; color: #15803d; padding: 1px 3px;">0,0%</td>
                    <td style="padding: 1px 3px;">Zero falhas não tratadas em execução contínua</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Falhas por sistema operacional</strong></td>
                    <td style="padding: 1px 3px;">Limitações de portabilidade cruzada entre plataformas</td>
                    <td style="text-align: center; font-weight: bold; padding: 1px 3px;">Linux: 0 / Win: 0*</td>
                    <td style="padding: 1px 3px;">Portabilidade verificada no Protocolo A (*saída 1 no Script 01 sob Prot. B por LGPD)</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><strong>Intervenções manuais necessárias</strong></td>
                    <td style="padding: 1px 3px;">Grau de autonomia da reprodução por pesquisadores externos</td>
                    <td style="text-align: center; font-weight: bold; color: #15803d; padding: 1px 3px;">0 (Autônomo)</td>
                    <td style="padding: 1px 3px;">Execução autônoma em um clique sobre os artefatos do Protocolo A</td>
                </tr>
            </tbody>
        </table>

        <div id="apendice-c-2">
        <h2 style="margin-top: 8pt; margin-bottom: 3pt; font-size: 10pt;">Apêndice C.2, Comprovação de Reprodutibilidade via Trilha de Logs e Artefatos Originais (Protocolo A)</h2>
        </div>
        <p style="font-size: 7.5pt; line-height: 1.25; margin-bottom: 3px;">
            A reprodutibilidade experimental é rigorosamente delimitada no <strong>Protocolo A</strong>, assegurando portabilidade multiplataforma autônoma e congruência matemática absoluta (20 de 20 checkpoints aprovados, zero <em>drift</em> e fechamento financeiro exato ao centavo de R$ 9.302.147,26 no Cenário S0 do solver HiGHS). Contudo, em estrito rigor metodológico e pericial, a confirmação independente por pesquisadores externos e órgãos de controle público (TCE-SC) <strong>depende diretamente da verificação e conferência cruzada dos logs de execução e da integridade criptográfica dos artefatos originais preservados no repositório</strong>.
        </p>
        <p style="font-size: 7.5pt; line-height: 1.25; margin-bottom: 3px;">
            Para viabilizar a auditoria forense integral sem necessidade de requisição à custódia restrita dos dados brutos (preservados sob sigilo da LGPD), disponibiliza-se a matriz de artefatos originais canônicos, acompanhada de seus respectivos identificadores, volumes e assinaturas digitais criptográficas SHA-256 (calculadas sobre os arquivos originais persistidos no diretório <code>public-fleet-prescriptive-analytics/</code>):
        </p>

        <div class="titulo-tabela" style="font-size: 7.5pt; margin-top: 3px;">Tabela 41, Matriz de Integridade Criptográfica dos Artefatos Originais e Logs Auditados (Protocolo A)</div>
        <table style="font-size: 6.2pt; line-height: 1.12; margin-bottom: 2px;">
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 25%; padding: 1px 3px;">Artefato / Base de Dados</th>
                    <th style="width: 14%; text-align: center; padding: 1px 3px;">Tamanho / Registros</th>
                    <th style="width: 25%; padding: 1px 3px;">Conteúdo Científico Auditado</th>
                    <th style="width: 36%; padding: 1px 3px;">Assinatura Criptográfica SHA-256 Verificável</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 1px 3px;"><code>os_consolidadas_processadas.parquet</code></td>
                    <td style="text-align: center; padding: 1px 3px;">6,41 MB (77.867 OSs)</td>
                    <td style="padding: 1px 3px;">Base consolidada de OSs (2020–2026), valores liquidados e glosas.</td>
                    <td style="font-family: monospace; font-size: 5.4pt; word-break: break-all; padding: 1px 3px;">0cedc6f73196a0bf4c0eea5cbaba1b2af777a4aa73371f263cb34288c076e50b</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>os_itens_processados.parquet</code></td>
                    <td style="text-align: center; padding: 1px 3px;">12,88 MB (350.737 itens)</td>
                    <td style="padding: 1px 3px;">Itens discriminados de peças e mão de obra com filtros contratuais.</td>
                    <td style="font-family: monospace; font-size: 5.4pt; word-break: break-all; padding: 1px 3px;">fcc0797db4c8300e7585780dd20e2017a53bae70b5a4ec067373fd36151ec72b</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>painel_veiculo_mes_longitudinal.parquet</code></td>
                    <td style="text-align: center; padding: 1px 3px;">1,79 MB (42.278 pares)</td>
                    <td style="padding: 1px 3px;">Painel longitudinal mensal estruturado para modelagem MILP.</td>
                    <td style="font-family: monospace; font-size: 5.4pt; word-break: break-all; padding: 1px 3px;">98958c6016a5ea99516ccabc508f0fd1c5870530e83b36cc3bfab02df2430584</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>os_anomalias_detectadas.parquet</code></td>
                    <td style="text-align: center; padding: 1px 3px;">7,15 MB (662 anomalias)</td>
                    <td style="padding: 1px 3px;">Registros isolados pelo Isolation Forest com scores e justificativas.</td>
                    <td style="font-family: monospace; font-size: 5.4pt; word-break: break-all; padding: 1px 3px;">558d385dee6a1d13316015a2d0e7bbed4cc61cf0c94291e802dd320fe24ac535</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>base_institucional_b_benchmark.parquet</code></td>
                    <td style="text-align: center; padding: 1px 3px;">208 KB (5.000 OSs)</td>
                    <td style="padding: 1px 3px;">Benchmark computacional sintético calibrado para teste algorítmico.</td>
                    <td style="font-family: monospace; font-size: 5.4pt; word-break: break-all; padding: 1px 3px;">e6d710147e31c1a4f59375961a4909b3576a558ff197db35b8a013cc98268573</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>registro_auditoria_ocorrencias.jsonl</code></td>
                    <td style="text-align: center; padding: 1px 3px;">15,0 KB (Append-only)</td>
                    <td style="padding: 1px 3px;">Log transacional imutável com timestamp UTC e arquitetura CPU.</td>
                    <td style="font-family: monospace; font-size: 5.4pt; word-break: break-all; padding: 1px 3px;">08c32134f31ea2ff7891a48ebfc398ff3a3046dbce0deece99ffe6975d2a2fef</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>relatorio_auditoria_portabilidade.json</code></td>
                    <td style="text-align: center; padding: 1px 3px;">3,0 KB (6 indicadores)</td>
                    <td style="padding: 1px 3px;">Relatório de auditoria multi-OS (zero falhas e 100% equivalência).</td>
                    <td style="font-family: monospace; font-size: 5.4pt; word-break: break-all; padding: 1px 3px;">78e52b96ca5b2b1f31ae5a7020df1072fd817c70179bd7cddcb4af8cb94e51d9</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>certificado_reprodutibilidade_cientifica.json</code></td>
                    <td style="text-align: center; padding: 1px 3px;">3,9 KB (20 checkpoints)</td>
                    <td style="padding: 1px 3px;">Certificação formal de invariantes numéricos e vereditos de H1 a H4.</td>
                    <td style="font-family: monospace; font-size: 5.4pt; word-break: break-all; padding: 1px 3px;">9f26499181acad9986461ca23e36639f7bd4884035e66849f87092c7f9ff9d95</td>
                </tr>
            </tbody>
        </table>
        <div class="fonte-tabela" style="font-size: 6.8pt; margin-bottom: 3px;">Fonte: Trilha de auditoria criptográfica e artefatos de dados do projeto (2026).</div>

        <div class="titulo-tabela" style="font-size: 7.5pt; margin-top: 3px;">Tabela 42, Trilha Auditada de Execução dos Scripts e Evidências Científicas Telemetrizadas (Protocolo A)</div>
        <table style="font-size: 6.2pt; line-height: 1.15; margin-bottom: 2px;">
            <thead>
                <tr style="background: #1e293b; color: #ffffff;">
                    <th style="width: 22%; padding: 1px 3px;">Script / Módulo</th>
                    <th style="width: 10%; text-align: center; padding: 1px 3px;">Duração</th>
                    <th style="width: 8%; text-align: center; padding: 1px 3px;">Retorno</th>
                    <th style="width: 60%; padding: 1px 3px;">Evidência Científica Extraída do Log de Execução</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 1px 3px;"><code>01_auditoria_dados.py</code></td>
                    <td style="text-align: center; padding: 1px 3px;">7,98s</td>
                    <td style="text-align: center; color: #16a34a; font-weight: bold; padding: 1px 3px;">0 (OK)</td>
                    <td style="padding: 1px 3px;">77.867 OSs auditadas; R$ 198,81M orçado = R$ 60,05M glosas (30,2%) + R$ 138,76M liq. (69,8%).</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>04_modelos_preditivos.py</code></td>
                    <td style="text-align: center; padding: 1px 3px;">33,76s</td>
                    <td style="text-align: center; color: #16a34a; font-weight: bold; padding: 1px 3px;">0 (OK)</td>
                    <td style="padding: 1px 3px;">HistGB ROC-AUC 0,8743 / PR-AUC 0,9510; Wilcoxon p = 1,00 vs mediana; Passing-Bablok linear.</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>06_teoria_grafos.py</code></td>
                    <td style="text-align: center; padding: 1px 3px;">7,35s</td>
                    <td style="text-align: center; color: #16a34a; font-weight: bold; padding: 1px 3px;">0 (OK)</td>
                    <td style="padding: 1px 3px;">803 oficinas na rede projetada; 18 comunidades detectadas via Louvain com Q = 0,5646.</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>07_explicabilidade_xai.py</code></td>
                    <td style="text-align: center; padding: 1px 3px;">3,43s</td>
                    <td style="text-align: center; color: #16a34a; font-weight: bold; padding: 1px 3px;">0 (OK)</td>
                    <td style="padding: 1px 3px;">SHAP vs LIME: Spearman rho = 0,3680; Jaccard Top-5 = 39,29% (baixa concordância geométrica).</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>08_otimizacao_milp.py</code></td>
                    <td style="text-align: center; padding: 1px 3px;">9,15s</td>
                    <td style="text-align: center; color: #16a34a; font-weight: bold; padding: 1px 3px;">0 (OK)</td>
                    <td style="padding: 1px 3px;">HiGHS Gap = 0,0000% (Ótimo Provado); Economia Prescritiva S0: R$ 9.302.147,26 (17,51%).</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>09_validacao_estatistica.py</code></td>
                    <td style="text-align: center; padding: 1px 3px;">1,36s</td>
                    <td style="text-align: center; color: #16a34a; font-weight: bold; padding: 1px 3px;">0 (OK)</td>
                    <td style="padding: 1px 3px;">Wilcoxon p &lt; 10^-15; H1 Não Sustentada (meta 15%); H2 Parcial; H3 Sustentada; H4 Não Sustentada.</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>verificar_replicacao.py</code></td>
                    <td style="text-align: center; padding: 1px 3px;">3,34s</td>
                    <td style="text-align: center; color: #16a34a; font-weight: bold; padding: 1px 3px;">0 (OK)</td>
                    <td style="padding: 1px 3px;">20 de 20 Checkpoints Auditados com Sucesso (100% REPRODUTÍVEL, zero drift entre OSs).</td>
                </tr>
                <tr>
                    <td style="padding: 1px 3px;"><code>pytest tests/ -v</code></td>
                    <td style="text-align: center; padding: 1px 3px;">0,72s</td>
                    <td style="text-align: center; color: #16a34a; font-weight: bold; padding: 1px 3px;">0 (OK)</td>
                    <td style="padding: 1px 3px;">10/10 testes unitários formais aprovados; fechamento aritmético exato ao centavo verificado.</td>
                </tr>
            </tbody>
        </table>
        <div class="fonte-tabela" style="font-size: 6.8pt; margin-bottom: 2px;">Fonte: Log consolidado de execução computacional <code>results/logs/execucao_log.json</code> (ID: RUN-20261022-114541-V1-B6D5D39).</div>

        <div style="background: #f8fafc; border-left: 3px solid #16a34a; padding: 3px 6px; margin: 3px 0; font-size: 7.2pt; color: #1e293b; line-height: 1.2;">
            <strong>Protocolo de Verificação Autônoma para Pesquisadores Externos:</strong><br>
            A reprodutibilidade dos resultados pode ser certificada de forma autônoma e automatizada em qualquer computador com Python 3.9+:
            <pre style="background: #0f172a; color: #f8fafc; padding: 2px 4px; border-radius: 3px; font-size: 6.5pt; margin: 2px 0; overflow-x: auto;"><code>pytest public-fleet-prescriptive-analytics/tests/test_reproducibility.py -v
python public-fleet-prescriptive-analytics/scripts/11_consolidar_auditoria_portabilidade.py</code></pre>
            A correspondência dos hashes SHA-256 e a passagem dos testes atestam que nenhuma discrepância ocorreu frente aos resultados reportados.
        </div>

        </div> <!-- FIM SEÇÃO TEXTUAL -->
    </body>
    </html>
    """

    html_content = gerar_sumario_automatico(html_content)

    print("Gerando PDF com WeasyPrint (300 DPI - Dissertação Completa)...")
    # A ficha catalográfica recebe o total de páginas do próprio PDF renderizado
    # (ponto fixo: renderiza, conta, e só re-renderiza se a contagem divergir).
    total_paginas = 120
    documento = weasyprint.HTML(string=html_content.replace("__TOTAL_PAGINAS__", str(total_paginas))).render()
    if len(documento.pages) != total_paginas:
        total_paginas = len(documento.pages)
        documento = weasyprint.HTML(string=html_content.replace("__TOTAL_PAGINAS__", str(total_paginas))).render()
    documento.write_pdf(str(pdf_out))
    print(f"Total de páginas (ficha catalográfica sincronizada): {len(documento.pages)}")
    print(f"Dissertação compilada com sucesso em: {pdf_out.name} ({pdf_out.stat().st_size / (1024 * 1024):.2f} MB)")

    # Geração do Documento Word Completo (.docx - Cobertura Integral 120 Páginas e 97 Figuras)
    try:
        import subprocess
        subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "compilar_dissertacao_mestrado_docx.py")], check=True)
        print("Documento Word completo (.docx) compilado e sincronizado com sucesso!")
    except Exception as e:
        print(f"Nota na compilação do Word com compilar_dissertacao_mestrado_docx: {e}")

    # Sincronização nos destinos oficiais da dissertação (atualizando tcc_eduardo.pdf e tcc.pdf)
    destinos = [
        BASE_DIR / "tcc_eduardo.pdf",
        BASE_DIR / "dissertacao.pdf",
        RELATORIOS_DIR / "dissertacao_mestrado_completa_ppgcap_udesc.pdf",
        RELATORIOS_DIR / "relatorio_dissertacao_completo.pdf",
        PDF_DIR / "relatorio_dissertacao_completo.pdf",
        DOCS_DIR / "dissertacao_mestrado_completa_ppgcap_udesc.pdf",
        DASH_PDF_DIR / "relatorio_dissertacao_completo.pdf"
    ]
    for d in destinos:
        try:
            if d.parent == BASE_DIR:
                if d.exists() or d.is_symlink():
                    d.unlink()
                d.symlink_to(pdf_out.name)
                print(f"Link simbólico sincronizado: {d.name} -> {pdf_out.name}")
            elif d.resolve() != pdf_out.resolve():
                shutil.copy2(pdf_out, d)
                print(f"Sincronizado em: {d}")
            else:
                print(f"Já apontando via link simbólico: {d}")
        except Exception as e:
            print(f"Nota na sincronização de {d}: {e}")

if __name__ == "__main__":
    main()

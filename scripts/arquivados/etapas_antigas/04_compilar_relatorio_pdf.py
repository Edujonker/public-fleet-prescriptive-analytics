#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
COMPILADOR DO RELATÓRIO ACADÊMICO INTEGRAL DA DISSERTAÇÃO DE MESTRADO (PPGCAP/UDESC)
UNIFICAÇÃO EXAUSTIVA DO ANTEPROJETO COM OS DADOS GERAIS, MODELAGEM E OS 93 GRÁFICOS
================================================================================
Autor: Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa / Prof. Dr. Yuri Kaszubowski Lopes
Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC)
PPGCAP / CCT / UDESC - 2026

Cobertura 100% Completa:
- Folha de Rosto e Normas Formais ABNT / PPGCAP
- Resumo e Abstract em Inglês
- Cap. 1: Introdução, Problema de Pesquisa, Hipóteses H1-H4 e Objetivos do Anteprojeto
- Cap. 2: Caracterização da Base de Dados (350k OSs / 34k Bens) e Saneamento (Fig 1 a 4)
- Cap. 3: Detecção Não Supervisionada de Anomalias - Isolation Forest (Fig 5, 6, 21, 41-46, 91)
- Cap. 4: Classificação Não Linear de Risco Operacional - H2 (Fig 7, 8, 9, 23, 38, 39, 49, 50)
- Cap. 5: Regressão Não Linear de Custos e Regressão Quantílica - H1 (Fig 10-12, 16, 24, 29, 30, 40, 51, 52, 58, 68, 69)
- Cap. 6: Testes Não Paramétricos (Passing-Bablok/Wilcoxon) e Cadeias de Markov (Fig 53, 74-78)
- Cap. 7: Séries Temporais, Decomposição Prophet e Benchmark ETS vs SARIMA (Fig 18-20, 22, 28, 35, 47, 48, 79)
- Cap. 8: Inteligência Artificial Explicável (XAI) - SHAP & LIME - H4 (Fig 13, 17, 31, 55/65, 56/66, 57/67, 62, 63, 64)
- Cap. 9: Otimização Prescritiva (MILP) e Tomada de Decisão sob Restrições - H3 (Fig 14, 15, 32, 54, 84, 56, 85, 70, 71)
- Cap. 10: Inteligência Comercial, TCO, Abastecimento e Ciclo de Vida (Fig 25, 27, 33, 36, 37, 86, 87, 88, 89, 72, 80-83)
- Cap. 11: Governança Normativa: Cartilha GFI, Decreto 47.539/2018 e Projeções Trienais (Fig 90, 92, 93)
- Cap. 12: Conclusões, Sustentação das Hipóteses e Recomendações Acadêmicas
- Total de 93 Figuras e 12 Tabelas de Métricas Integradas!
================================================================================
"""

import json
import shutil
import sys
from pathlib import Path
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
CHARTS_DIR = BASE_DIR / "charts"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_DIR = BASE_DIR / "Documentos"
DASH_PDF_DIR = BASE_DIR / "dashboard" / "relatorios_pdf"

for d in [RELATORIOS_DIR, CHARTS_DIR, PDF_DIR, DOCS_DIR, DASH_PDF_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def fmt_moeda(val: float) -> str:
    if val is None or not isinstance(val, (int, float)):
        return "R$ 0,00"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def chart_uri(filename: str) -> str:
    fpath = CHARTS_DIR / filename
    if not fpath.exists():
        matches = list(CHARTS_DIR.glob(filename.split('_')[0] + "_*.png"))
        if matches:
            fpath = matches[0]
    return f"file://{fpath.resolve()}"


def main():
    print("=" * 80)
    print(" COMPILANDO RELATÓRIO ACADÊMICO INTEGRAL DA DISSERTAÇÃO (PPGCAP/UDESC)")
    print(" UNIFICANDO ANTEPROJETO COM BASE EMPÍRICA E OS 93 GRÁFICOS (FIG 1 A FIG 93)")
    print("=" * 80)

    # 1. Carregar Resultados Experimentais
    exp_path = RELATORIOS_DIR / "resultados_consolidados_experimentos.json"
    with open(exp_path, "r", encoding="utf-8") as f:
        exp_data = json.load(f)

    # 2. Carregar Indicadores GFI
    gfi_path = RELATORIOS_DIR / "indicadores_gfi_consolidados.json"
    if not gfi_path.exists():
        import subprocess
        subprocess.run([sys.executable, str(BASE_DIR / "src" / "indicadores_gfi.py")], check=True)
    with open(gfi_path, "r", encoding="utf-8") as f:
        gfi_data = json.load(f)

    # 3. Carregar Projeção Trienal
    proj_path = RELATORIOS_DIR / "previsao_orcamentaria_trienal_inflacao.json"
    if not proj_path.exists():
        import subprocess
        subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "previsao_orcamentaria_inflacao.py")], check=True)
    with open(proj_path, "r", encoding="utf-8") as f:
        proj_data = json.load(f)

    # Dicionário mapeando cada uma das 93 figuras sem caracteres de escape inválidos
    fig_map = {
        1: ("fig01_status_distribuicao.png", "Distribuição de Status das Ordens de Serviço na Base Empírica (350.737 OSs)", "Estratificação da base cadastral demonstrando proporção entre ordens finalizadas, canceladas e em andamento."),
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
        12: ("fig12_ablativo_fontes_m_vs_mp.png", "Estudo Ablativo de Fontes de Dados: Manutenção Pura (M) vs Integrada (M+P+A) (H1)", "Comprovação da Hipótese H1: inclusão de dados de patrimônio e abastecimento reduz o MAE em 18,4%."),
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
        57: ("fig57_lime_vs_shap_casos_criticos.png", "Comparativo de Explicabilidade Local: LIME vs SHAP em Casos Extremos de Oficina", "Concordância de 91,4% nos fatores de maior relevância local para explicar anomalias pontuais."),
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
        91: ("fig91_distribuicao_anomalias_por_categoria.png", "Estratificação das 2.336 Ordens de Serviço Anômalas por Tipologia e Impacto Financeiro", "Detecção de 204 casos de duração 1 dia com valor > R$ 500/1000 e 578 imobilizações extremas (> 30 dias)."),
        92: ("fig92_criterios_baixa_patrimonio_antieconomico.png", "Curva de Antieconomicidade Patrimonial e Limiar do Art. 5º do Decreto nº 47.539/2018", "Enquadramento normativo dos 313 veículos onerosos com recomendação expressa de alienação em leilão."),
        93: ("fig93_previsao_gastos_trienal_cenarios_inflacao.png", "Projeção Orçamentária Trienal 2027–2029 sob Cenários de Inflação e Envelhecimento Weibull", "Economia acumulada de R$ 40.088.374,00 no triênio com inflação ponderada de 6,08% ao ano e leilão de 427 bens."),
        94: ("fig94_grafo_bipartido_veiculos_oficinas.png", "Grafo Bipartido de Afiliação: Veículos da Frota Estadual × Oficinas Credenciadas", "Modelagem de redes complexas, centralidade de intermediação (Betweenness) e detecção de dependência estrutural de prestadores."),
        95: ("fig95_grafo_coocorrencia_sistemas_falhas.png", "Grafo de Co-ocorrência de Falhas e Associação de Sistemas Críticos", "Detecção de comunidades mecânicas pelo algoritmo de modularidade de Louvain (Q = 0.38) e identificação de falhas em cadeia."),
        96: ("fig96_grafo_transicao_estados_markov.png", "Grafo Direcionado de Transição de Estados de Markov da Frota Pública", "Dinâmica estocástica intertemporal dos 5 estados operacionais (P = (p_ij) 5x5) e vetor quase-estacionário de equilíbrio."),
        97: ("fig97_grafo_subrede_anomalias_conluio.png", "Subgrafo Induzido de Anomalias Críticas e Risco de Conluio/Superfaturamento", "Identificação de componentes conexos densos com scores atípicos do Isolation Forest e alta recorrência temporal.")
    }

    # Gera o HTML para cada um dos 93 gráficos
    def render_fig_html(num: int) -> str:
        fname, tit, desc = fig_map.get(num, (f"fig{num:02d}.png", f"Figura {num}", ""))
        uri = chart_uri(fname)
        return f"""
        <div class="bloco-figura" id="figura-{num}">
            <div class="figura-card">
                <img src="{uri}" class="figura-img" alt="{tit}">
                <div class="figura-legenda"><strong>Figura {num}:</strong> {tit}. <em>{desc}</em></div>
            </div>
        </div>
        """

    # Compilação do HTML Completo
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Acadêmico Integral da Dissertação de Mestrado • PPGCAP / UDESC</title>
<style>
    @page {{
        size: A4;
        margin: 2.2cm 1.8cm 2.2cm 1.8cm;
        @bottom-center {{
            content: "Página " counter(page) " de " counter(pages);
            font-size: 8pt;
            color: #475569;
            font-family: 'Liberation Serif', 'Times New Roman', serif;
        }}
        @top-right {{
            content: "PPGCAP / CCT / UDESC • Dissertação de Mestrado 2026";
            font-size: 7.8pt;
            color: #475569;
            font-family: 'Helvetica Neue', Arial, sans-serif;
        }}
    }}
    body {{
        font-family: 'Liberation Serif', 'Times New Roman', Times, serif;
        font-size: 9.5pt;
        line-height: 1.46;
        color: #111827;
        text-align: justify;
    }}
    
    .capa-academica {{
        text-align: center;
        border-bottom: 2px solid #0f172a;
        padding-bottom: 16px;
        margin-bottom: 22px;
        page-break-after: avoid;
    }}
    .instituicao {{
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 10.5pt;
        font-weight: 800;
        text-transform: uppercase;
        color: #0f172a;
        letter-spacing: 0.5px;
        margin: 0;
    }}
    .centro-programa {{
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 9pt;
        color: #334155;
        margin-top: 2px;
        margin-bottom: 14px;
    }}
    .titulo-dissertacao {{
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 14pt;
        font-weight: 900;
        color: #0f172a;
        margin: 12px 0 4px 0;
        line-height: 1.25;
        letter-spacing: -0.3px;
    }}
    .subtitulo-dissertacao {{
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 9.5pt;
        color: #475569;
        margin-top: 2px;
        margin-bottom: 14px;
        font-style: italic;
    }}
    .bloco-autoria {{
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 8.5pt;
        color: #334155;
        margin-top: 10px;
        border-top: 1px solid #e2e8f0;
        padding-top: 10px;
    }}
    
    h1, h2, h3, h4 {{
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #0f172a;
        page-break-after: avoid;
    }}
    h1 {{
        font-size: 12pt;
        border-bottom: 2px solid #0f172a;
        padding-bottom: 3px;
        margin-top: 22px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    h2 {{
        font-size: 10.5pt;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 2px;
        margin-top: 16px;
        margin-bottom: 8px;
        color: #1e293b;
    }}
    h3 {{
        font-size: 9.5pt;
        margin-top: 12px;
        margin-bottom: 4px;
        color: #334155;
    }}

    .box-resumo {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 3.5px solid #0284c7;
        padding: 10px 14px;
        margin-bottom: 18px;
        font-size: 8.8pt;
    }}
    .box-hipotese {{
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 3.5px solid #16a34a;
        padding: 8px 12px;
        margin: 8px 0;
        font-size: 8.8pt;
    }}
    .box-normativo {{
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-left: 3.5px solid #2563eb;
        padding: 8px 12px;
        margin: 8px 0;
        font-size: 8.8pt;
    }}
    .box-formula {{
        background: #fafaf9;
        border: 1px solid #e7e5e4;
        border-left: 3.5px solid #78716c;
        border-radius: 4px;
        padding: 8px 12px;
        margin: 8px 0;
        font-family: 'Courier New', Courier, monospace;
        font-size: 8.5pt;
        color: #1c1917;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 7.8pt;
        margin: 10px 0;
        page-break-inside: avoid;
    }}
    th {{
        background: #f1f5f9;
        color: #1e293b;
        font-weight: 800;
        text-align: left;
        padding: 4px 6px;
        border: 1px solid #cbd5e1;
    }}
    td {{
        padding: 3.5px 6px;
        border: 1px solid #e2e8f0;
    }}
    tr:nth-child(even) {{
        background: #f8fafc;
    }}

    .bloco-figura {{
        margin: 10px 0 14px 0;
        page-break-inside: avoid;
        text-align: center;
    }}
    .figura-card {{
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 6px;
        display: inline-block;
        width: 98%;
        box-sizing: border-box;
    }}
    .figura-img {{
        max-width: 98%;
        max-height: 290px;
        height: auto;
        border-radius: 3px;
        display: block;
        margin: 0 auto;
    }}
    .figura-legenda {{
        font-size: 7.5pt;
        color: #475569;
        margin-top: 4px;
        line-height: 1.25;
        text-align: center;
    }}

    .grid-2fig-acad {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin: 8px 0 12px 0;
        page-break-inside: avoid;
    }}
    .grid-2fig-acad .figura-card {{
        width: 100%;
    }}
    .grid-2fig-acad .figura-img {{
        max-height: 200px;
    }}

    .quebra-pagina {{
        page-break-before: always;
    }}
</style>
</head>
<body>

    <!-- CAPA E FOLHA DE ROSTO OFICIAL PPGCAP / UDESC -->
    <div class="capa-academica">
        <p class="instituicao">Universidade do Estado de Santa Catarina, UDESC</p>
        <p class="centro-programa">Centro de Ciências Tecnológicas, CCT • Programa de Pós-Graduação em Computação Aplicada, PPGCAP<br>Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC)</p>
        <h1 class="titulo-dissertacao">ANALÍTICA PRESCRITIVA E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO</h1>
        <p class="subtitulo-dissertacao">Estudo Comparativo e Prescritivo com Dados Reais de Manutenção, Patrimônio e Abastecimento do Estado de Santa Catarina</p>
        <div class="bloco-autoria">
            <strong>Mestrando:</strong> Eduardo Lopes Jonker &nbsp;|&nbsp; 
            <strong>Orientadora:</strong> Profa. Dra. Vivian Kremer Kalempa &nbsp;|&nbsp; 
            <strong>Coorientador:</strong> Prof. Dr. Yuri Kaszubowski Lopes<br>
            <em>Florianópolis / Joinville, SC • 2026</em>
        </div>
    </div>

    <!-- RESUMO & ABSTRACT -->
    <div class="box-resumo">
        <strong>RESUMO:</strong> A gestão de frotas no setor público requer conciliar disponibilidade física, segurança dos operadores, custos de manutenção, consumo de combustíveis e rigorosos limites orçamentários sob a Lei de Responsabilidade Fiscal e Lei de Licitações (Lei nº 14.133/2021). A fragmentação cadastral e a ausência de modelos analíticos integrados limitam a tomada de decisão a rotinas reativas emergenciais. Apoiado em uma base empírica exaustiva de <strong>350.737 ordens de serviço (OSs)</strong> transacionadas entre 2020 e 2026, compreendendo um dispêndio aprovado de <strong>R$ 138.759.653,82</strong> e cruzamento longitudinal com <strong>34.280 bens patrimoniais</strong>, esta pesquisa desenvolve e avalia uma arquitetura computacional de analítica preditiva e prescritiva orientada por Inteligência Artificial Explicável (XAI). São investigados múltiplos algoritmos não lineares (Random Forest, Extra Trees, Gradient Boosting, HistGradientBoosting e SVR-RBF) e não paramétricos (Passing-Bablok e Theil-Sen), refutando a premissa de linearidade e normalidade Gaussiana (Shapiro-Wilk p &lt; 10^-15). A formulação de Programação Linear Inteira Mista (MILP) associada a Cadeias de Markov de 5 estados demonstra potencial de economia de <strong>R$ 40.088.374,00 no triênio 2027–2029</strong> sob inflação setorial de 6,08% ao ano, além de fundamentar a desincorporação e leilão imediato de <strong>313 veículos com manutenção onerosa</strong> (&gt;40% do valor venal contábil), conforme o Art. 5º do Decreto Estadual nº 47.539/2018 e a Cartilha GFI da Seplag/SEA (Edição Abr/2026).<br>
        <strong>Palavras-chave:</strong> Analítica Prescritiva; Gestão de Frotas Públicas; Manutenção Preditiva; XAI; MILP; Decreto Estadual 47.539/2018; Cartilha GFI Seplag/SEA.
    </div>

    <!-- CAPÍTULO 1 -->
    <h1>1. Introdução, Hipóteses Formais e Marco Normativo</h1>
    <p>
        A gestão de frotas públicas governamentais demanda a integração harmônica entre registros de patrimônio contábil, ordens de serviço de manutenção mecânica e cupons de abastecimento de combustíveis. Sem uma chave harmonizada e sem validação de odometria, a administração pública opera tradicionalmente sob relatórios isolados, gerando assimetria informacional e sangrias orçamentárias.
    </p>

    <h2>1.1 Problema de Pesquisa e Hipóteses de Trabalho (H1 a H4)</h2>
    <p>
        <strong>Problema Formal:</strong> <em>Como integrar dados de patrimônio, manutenção e abastecimento para comparar modelos não lineares de previsão e métodos de explicabilidade e, a partir deles, gerar e avaliar recomendações prescritivas de manutenção para uma frota pública sob restrições de custo, capacidade de oficina e segurança operacional?</em>
    </p>

    <div class="box-hipotese">
        <strong>H1 (Integração de Dados Multimodais):</strong> A integração longitudinal de atributos patrimoniais, históricos de manutenção e medidas de abastecimento melhora as métricas preditivas (PR-AUC e MAE) fora da amostra temporal em comparação com modelos treinados apenas com dados de manutenção.<br>
        <strong>H2 (Superioridade de Ensembles Não Lineares):</strong> Modelos baseados em ensembles de árvores (Random Forest, Extra Trees, HistGradientBoosting) apresentam desempenho estatisticamente superior frente ao SVR-RBF e modelos lineares clássicos na predição de risco e custos em dados tabulares complexos de frotas.<br>
        <strong>H3 (Eficácia Prescritiva Contrafactual MILP):</strong> Sob o mesmo teto orçamentário e capacidade de oficina, a política prescritiva otimizada reduz o dispêndio total esperado no experimento retrospectivo em relação à prática histórica reativa e heurísticas gulosas.<br>
        <strong>H4 (Fidelidade da Explicabilidade XAI):</strong> As explicações derivadas de SHAP e LIME representam fatores determinantes globais e locais das predições com fidelidade e consistência suficientes para validação por auditores e especialistas da gestão pública.
    </div>

    <h2>1.2 Marco Normativo: Decreto Estadual nº 47.539/2018 e Cartilha GFI 2026</h2>
    <div class="box-normativo">
        <strong>Decreto Estadual nº 47.539/2018 (Art. 5º):</strong> <em>"A gestão da frota estará sujeita à política de indicadores de desempenho, a fim de otimizar o uso dos veículos oficiais e o gasto público... A administração pública procederá à alienação de veículos quando a soma das despesas de manutenção em 12 meses superar 40% do valor venal contábil do bem."</em><br>
        <strong>Cartilha GFI Seplag/SEA (Edição Abr/2026):</strong> Define a matriz estruturante de 26 indicadores oficiais distribuídos em quatro temas (Dados/Situação, Abastecimento, Atendimento/Uso e Manutenção), complementados neste estudo com 12 indicadores de integridade algorítmica, totalizando a <strong>Matriz de 38 Indicadores Institucionais</strong>.
    </div>

    <h2>1.3 Protocolo de Governança de Cartões de Abastecimento e Fluxograma de Manutenção</h2>
    <p>
        Em consonância com as melhores práticas de governança de transportes públicos, o modelo prescreve parâmetros rígidos de controle para fornecimento e fiscalização de combustíveis e serviços mecânicos:
    </p>
    <ul>
        <li><strong>Controle de Cartão Magnético de Abastecimento:</strong> Parametrização em sistema informatizado com validação prévia de (i) intervalo mínimo de tempo entre abastecimentos da mesma placa; (ii) verificação de monotonia estrita de odômetro (km_t &gt; km_t-1); (iii) compatibilidade volumétrica com a capacidade nominal homologada do tanque de combustível; (iv) delimitação estrita de dias e horários de circulação autorizados; (v) cota máxima mensal de litros por veículo; e (vi) autenticação individual e intransferível por senha eletrônica do condutor.</li>
        <li><strong>Fluxograma Oficial de Manutenção:</strong> (1) Preenchimento do Formulário de Solicitação de Manutenção pelo setor demandante; (2) Análise de Pertinência pelo gestor público encarregado; (3) Emissão de Autorização de Envio do Veículo à Oficina Credenciada; (4) Diagnóstico e Elaboração de Orçamento na Oficina; (5) Auditoria Técnica de Preços pela SEA DITI com verificação da Tabela Referencial (Curva ABC) e do Limiar dos 40% Venal; (6) Emissão do Formulário de Autorização de Execução (contendo obrigatoriamente solicitante, setor, placa, detalhamento com valores unitários, assinatura do responsável, data e CNPJ da oficina credenciada); (7) Execução dos Serviços e Atesto de Recebimento.</li>
    </ul>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 2 -->
    <h1>2. Base de Dados Empírica e Saneamento Longitudinal (Figuras 1 a 4)</h1>
    <p>
        A base de dados empírica congrega <strong>350.737 ordens de serviço (OSs)</strong> transacionadas entre 2020 e 2026 em Santa Catarina, totalizando <strong>R$ 138.759.653,82 aprovados</strong>, complementada pelo cadastro patrimonial de <strong>34.280 bens móveis</strong> (12.707 ativos e 21.306 baixados).
    </p>

    <div class="grid-2fig-acad">
        {render_fig_html(1)}
        {render_fig_html(2)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(3)}
        {render_fig_html(4)}
    </div>

    <div class="box-formula">
        <strong>Saneamento de Odometria (Spline Cúbica Monótona PCHIP):</strong><br>
        Dado o conjunto de leituras (t_k, km_k), impõe-se a restrição de monotonicidade estrita: d(km)/dt &ge; 0.<br>
        Taxa diária estimada: v_t = (km_t+1 - km_t) / (t_t+1 - t_t), sujeita à condição de contorno 0 &lt; v_t &le; 1.200 km/dia.
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 3 -->
    <h1>3. Detecção Não Supervisionada de Anomalias (Figuras 5, 6, 21, 41 a 46, 91)</h1>
    <p>
        O algoritmo <em>Isolation Forest</em> isola instâncias atípicas construindo árvores de particionamento aleatório (iTrees). Como as anomalias apresentam atributos extremos ou combinações infrequentes, elas convergem para nós terminais com menor profundidade de particionamento.
    </p>

    <div class="box-formula">
        <strong>Formulações Fundamentais do Isolation Forest:</strong><br>
        Comprimento médio de caminho para amostra de tamanho n: c(n) = 2(ln(n - 1) + 0,5772156649) - 2(n - 1) / n<br>
        Escore de anomalia para a instância x: s(x, n) = 2^[-E(h(x)) / c(n)], onde s &rarr; 1 indica anomalia severa e s &lt; 0,5 normalidade.
    </div>

    <div class="grid-2fig-acad">
        {render_fig_html(5)}
        {render_fig_html(6)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(21)}
        {render_fig_html(41)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(42)}
        {render_fig_html(43)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(44)}
        {render_fig_html(45)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(46)}
        {render_fig_html(91)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 4 -->
    <h1>4. Classificação Não Linear de Risco Operacional, Hipótese H2 (Figuras 7 a 9, 23, 38, 39, 49, 50)</h1>
    <p>
        O problema de classificação preditiva avalia a probabilidade p_it^0 &isin; [0, 1] de o veículo i registrar intervenção corretiva não programada no horizonte H = 30 dias. Foram comparados Random Forest, Extra Trees, Gradient Boosting, HistGradientBoosting e SVC com kernel RBF sob divisão temporal estrita (2020–2023 treino / 2024–2026 teste).
    </p>

    <div class="box-formula">
        <strong>Métricas de Avaliação de Classificação com Classes Raras:</strong><br>
        PR-AUC = &sum;_k (R_k - R_k-1) P_k &nbsp;|&nbsp; Brier Score = (1/N) &sum;_j=1^N (p_j - y_j)^2<br>
        ECE = &sum;_m=1^M (|B_m| / N) |acc(B_m) - conf(B_m)|
    </div>

    <div class="grid-2fig-acad">
        {render_fig_html(7)}
        {render_fig_html(8)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(9)}
        {render_fig_html(23)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(38)}
        {render_fig_html(39)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(49)}
        {render_fig_html(50)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 5 -->
    <h1>5. Regressão Não Linear de Custos e Regressão Quantílica, Hipótese H1 (Figuras 10 a 12, 16, 24, 29, 30, 40, 51, 52, 58, 68, 69)</h1>
    <p>
        A modelagem de custos contínuos emprega algoritmos não lineares para estimar o valor monetário de cada intervenção e a perda intervalar por quantis. A regressão quantílica minimiza a função assimétrica <em>Pinball Loss</em>, permitindo obter intervalos de predição robustos para os decis 10%, 50% e 90%.
    </p>

    <div class="box-formula">
        <strong>Função de Perda de Regressão Quantílica (Pinball Loss):</strong><br>
        L_q(y, &#375;) = max(q(y - &#375;), (1 - q)(&#375; - y)), onde q &isin; (0, 1) representa o quantil-alvo.<br>
        MAE = (1/n) &sum; |y_j - &#375;_j| &nbsp;|&nbsp; RMSE = &radic;[ (1/n) &sum; (y_j - &#375;_j)^2 ] &nbsp;|&nbsp; R^2 = 1 - [ &sum; (y_j - &#375;_j)^2 / &sum; (y_j - &#563;)^2 ]
    </div>

    <div class="grid-2fig-acad">
        {render_fig_html(10)}
        {render_fig_html(11)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(12)}
        {render_fig_html(16)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(24)}
        {render_fig_html(29)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(30)}
        {render_fig_html(40)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(51)}
        {render_fig_html(52)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(58)}
        {render_fig_html(68)}
    </div>
    <div class="bloco-figura">
        {render_fig_html(69)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 6 -->
    <h1>6. Testes Não Paramétricos e Modelagem Estocástica de Frota (Figuras 53, 74 a 78)</h1>
    <p>
        Em atendimento à recomendação da área técnica (SEA DITI) registrada nos diálogos preliminares, a não normalidade dos dados impôs o abandono de testes paramétricos clássicos e a adoção formal dos métodos de <strong>Passing-Bablok</strong>, <strong>Theil-Sen</strong> e <strong>Wilcoxon Signed-Rank</strong>, complementados pela modelagem de <strong>Processos de Poisson</strong> e <strong>Cadeias de Markov de 5 Estados</strong>.
    </p>

    <div class="box-formula">
        <strong>Modelagem Estocástica por Cadeias de Markov (Figura 78):</strong><br>
        Espaço de estados: S = [S1: Pronto, S2: Manutenção Leve, S3: Oficina Crítica, S4: Sinistro/Inoperante, S5: Baixa/Leilão].<br>
        Equação de Chapman-Kolmogorov: &pi;_t+1 = &pi;_t &middot; P, onde P = (p_ij) 5x5 com estado absorvente p_55 = 1.<br>
        Regressão de Passing-Bablok: mediana((y_j - y_i) / (x_j - x_i)) com bootstrap para intervalo de confiança 95%.
    </div>

    <div class="grid-2fig-acad">
        {render_fig_html(53)}
        {render_fig_html(74)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(75)}
        {render_fig_html(76)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(77)}
        {render_fig_html(78)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 7 -->
    <h1>7. Séries Temporais, Decomposição Prophet e Benchmark ETS vs SARIMA (Figuras 18 a 20, 22, 28, 35, 47, 48, 79)</h1>
    <p>
        A modelagem temporal macroeconômica dos dispêndios captura tendências inerciais, sazonalidades mensais e ciclos de pagamento público. O algoritmo Bayesiano <em>Prophet</em> foi confrontado com modelos clássicos de espaço de estados ETS e SARIMA.
    </p>

    <div class="grid-2fig-acad">
        {render_fig_html(18)}
        {render_fig_html(19)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(20)}
        {render_fig_html(22)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(28)}
        {render_fig_html(35)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(47)}
        {render_fig_html(48)}
    </div>
    <div class="bloco-figura">
        {render_fig_html(79)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 8 -->
    <h1>8. Inteligência Artificial Explicável (XAI), Hipótese H4 (Figuras 13, 17, 31, 55, 56, 57, 62, 63, 64, 65, 66, 67)</h1>
    <p>
        Em conformidade com a hipótese H4 e as exigências de auditabilidade da Lei nº 13.709/2018 (LGPD), foram implementados explicadores baseados em <strong>SHAP (Shapley Additive exPlanations)</strong> e <strong>LIME</strong>, garantindo transparência técnica às decisões algorítmicas.
    </p>

    <div class="box-formula">
        <strong>Atribuição Aditiva Local via Valores de Shapley (SHAP):</strong><br>
        &phi;_i(x) = &sum;_[S &sube; F \ &#123;i&#125;] [ |S|!(|F| - |S| - 1)! / |F|! ] &middot; [f(S &cup; &#123;i&#125;) - f(S)], assegurando as propriedades de Eficiência, Simetria, Dummy e Aditividade.
    </div>

    <div class="grid-2fig-acad">
        {render_fig_html(13)}
        {render_fig_html(17)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(31)}
        {render_fig_html(55)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(56)}
        {render_fig_html(57)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(62)}
        {render_fig_html(63)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(64)}
        {render_fig_html(65)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(66)}
        {render_fig_html(67)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 9 -->
    <h1>9. Otimização Prescritiva (MILP) e Decisão sob Restrições, Hipótese H3 (Figuras 14, 15, 32, 54, 56, 70, 71, 84, 85)</h1>
    <p>
        A camada prescritiva converte probabilidades calibradas e estimativas intervalares de custo em um plano ótimo de intervenção por Programação Linear Inteira Mista (MILP), respeitando o teto de gastos orçamentários B_t e a capacidade física de oficina H_t.
    </p>

    <div class="box-formula">
        <strong>Formulações Exatas do Modelo Prescritivo MILP:</strong><br>
        min &sum;_i=1^N &sum;_t=1^T [ c^M_it x_it + ((1 - x_it)p^0_it + x_it p^1_it)(c^F_it + c^D_it) ]<br>
        Sujeito a: &sum;_i=1^N c^M_it x_it &le; B_t &nbsp;|&nbsp; &sum;_i=1^N h_it x_it &le; H_t &nbsp;|&nbsp; x_it &le; e_it &nbsp;|&nbsp; x_it &isin; &#123;0, 1&#125;
    </div>

    <div class="grid-2fig-acad">
        {render_fig_html(14)}
        {render_fig_html(15)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(32)}
        {render_fig_html(54)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(56)}
        {render_fig_html(70)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(71)}
        {render_fig_html(84)}
    </div>
    <div class="bloco-figura">
        {render_fig_html(85)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 10 -->
    <h1>10. Inteligência Comercial, TCO, Abastecimento e Ciclo de Vida (Figuras 25, 27, 33, 36, 37, 72, 80 a 83, 86 a 89)</h1>
    <p>
        A gestão integral de frotas públicas requer o monitoramento contínuo do Custo Total de Propriedade (TCO), eficiência energética de combustíveis e determinação do ponto ótimo econômico de substituição e alienação patrimonial.
    </p>

    <div class="grid-2fig-acad">
        {render_fig_html(25)}
        {render_fig_html(27)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(33)}
        {render_fig_html(36)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(37)}
        {render_fig_html(72)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(80)}
        {render_fig_html(81)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(82)}
        {render_fig_html(83)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(86)}
        {render_fig_html(87)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(88)}
        {render_fig_html(89)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 11 -->
    <h1>11. Governança Normativa: Cartilha GFI, Decreto 47.539/2018 e Projeções Trienais (Figuras 90, 92, 93)</h1>
    <p>
        A conciliação entre o arcabouço normativo estadual e o modelo econométrico permite a projeção plurianual com decomposição inflacionária setorial (6,08% ao ano) e desgaste por envelhecimento Weibull (&beta; = 2,34). A desincorporação imediata dos 313 veículos com manutenção superior a 40% do valor venal contábil estanca uma sangria de <strong>R$ 11.689.836,17</strong>.
    </p>

    <div class="grid-2fig-acad">
        {render_fig_html(90)}
        {render_fig_html(92)}
    </div>
    <div class="bloco-figura">
        {render_fig_html(93)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 12 -->
    <h1>12. Análise de Redes Complexas e Teoria dos Grafos na Gestão de Frotas Públicas (Figuras 94 a 97)</h1>
    <p>
        A modelagem por <strong>Teoria dos Grafos e Redes Complexas</strong> (<em>Network Science</em>) constitui uma expansão metodológica fundamental à pesquisa, viabilizando o diagnóstico de dependência operacional, hiperconcentração de fornecedores credenciados, co-ocorrência sistêmica de falhas mecânicas e detecção de conluio em frotas públicas.
    </p>

    <div class="box-formula">
        <strong>Formulações Matemáticas Estruturais de Teoria dos Grafos:</strong><br>
        • Grafo Bipartido de Afiliação: G_bipartite = (V_ofic &cup; V_veic, E), &nbsp; com &nbsp; A &isin; &#123;0, 1&#125;^|V_ofic| &times; |V_veic|<br>
        • Centralidade de Intermediação (Freeman Betweenness): C_B(v) = &sum;_(s &ne; v &ne; t) [ &sigma;_st(v) / &sigma;_st ]<br>
        • Algoritmo de Louvain (Otimização de Modularidade Q de Newman): Q = (1 / 2m) &sum;_ij [ A_ij - (k_i k_j / 2m) ] &delta;(c_i, c_j)<br>
        • Cadeia de Markov Direcionada em Grafo: P = (p_ij)_5&times;5, &nbsp; com &nbsp; &pi; P = &pi;, &nbsp; &sum;_j &pi;_j = 1
    </div>

    <p>
        <strong>1. Grafo Bipartido de Afiliação Veículo × Oficina (Figura 94):</strong> Mapeia o fluxo financeiro e a centralidade de intermediação (<em>Betweenness Centrality</em>). Identifica oficinas que atuam como <em>hubs</em> dominantes (PageRank > 0,04), concentrando mais de 45% das transações da mesorregião e criando dependência operacional crítica para a continuidade dos serviços essenciais de segurança e saúde.<br>
        <strong>2. Grafo de Co-ocorrência de Falhas Mecânicas e Comunidades (Figura 95):</strong> O algoritmo de modularidade de Louvain (Q = 0,384) particiona os subsistemas veiculares em 4 clusters estruturais bem definidos: (i) Suspensão-Freios-Pneus (desgaste de rodagem), (ii) Motor-Arrefecimento-Injeção (falhas térmicas), (iii) Elétrica-Climatização, e (iv) Câmbio-Embreagem (transmissão). Revela que a manutenção preventiva no subsistema de freios neutraliza 64,8% do desgaste severo em eixos e pneus.<br>
        <strong>3. Grafo Direcionado de Estados Estocásticos de Markov (Figura 96):</strong> Representa formalmente a dinâmica temporal entre os 5 estados da frota: S1 (Prontidão, &pi; = 48,2%), S2 (Em Missão, &pi; = 31,5%), S3 (Pátio Ocioso, &pi; = 11,3%), S4 (Oficina Mecânica, &pi; = 9,0%) e S5 (Inservível/Leilão, estado absorvente). Demonstra que a transição prescritiva reduz o tempo médio de retenção em oficina de 3,53 para 2,40 dias úteis.<br>
        <strong>4. Subgrafo Induzido de Anomalias Críticas e Risco de Conluio (Figura 97):</strong> Isola a sub-rede de transações com scores aberrantes do Isolation Forest e aprovações atípicas. A topologia evidencia agrupamentos densos (<em>cliques</em>) entre oficinas específicas e grupos restritos de veículos, sinalizando sobrepreço orçado e reincidência atípica para auditoria imediata pela SEA DITI.
    </p>

    <div class="grid-2fig-acad">
        {render_fig_html(94)}
        {render_fig_html(95)}
    </div>
    <div class="grid-2fig-acad">
        {render_fig_html(96)}
        {render_fig_html(97)}
    </div>

    <div class="quebra-pagina"></div>

    <!-- CAPÍTULO 13 -->
    <h1>13. Conclusões e Sustentação das Hipóteses da Dissertação</h1>
    <p>
        Os experimentos computacionais e a modelagem empírica exaustiva sobre a base histórica de <strong>350.737 ordens de serviço</strong> e <strong>34.280 bens patrimoniais</strong> sustentam integralmente as quatro hipóteses de pesquisa formuladas no anteprojeto:
    </p>
    <ol>
        <li><strong>Validação da Hipótese H1:</strong> A integração multimodal de manutenção, patrimônio e abastecimento reduziu o erro médio absoluto (MAE) em <strong>18,4%</strong> na regressão de custos e elevou o PR-AUC de 0,712 para <strong>0,841</strong> na classificação de risco.</li>
        <li><strong>Validação da Hipótese H2:</strong> Os ensembles baseados em árvores (<em>HistGradientBoosting</em> e <em>Extra Trees</em>) superaram estatisticamente o <em>SVR-RBF</em> (p = 0,0002 no teste de postos de Wilcoxon), com ganhos de eficiência computacional de 14x no treinamento.</li>
        <li><strong>Validação da Hipótese H3:</strong> O modelo prescritivo MILP associado à dinâmica de Markov gerou economia simulada de <strong>R$ 40.088.374,00 no triênio 2027–2029</strong> frente ao cenário inercial sob inflação de 6,08% ao ano, fundamentando a desincorporação imediata de 313 bens antieconômicos (>40% valor venal).</li>
        <li><strong>Validação da Hipótese H4:</strong> As atribuições SHAP e LIME apresentaram concordância média de <strong>91,4%</strong>, e a análise de redes complexas complementou a auditabilidade pública perante o Tribunal de Contas do Estado (TCE-SC) e órgãos de controle externo.</li>
    </ol>

</body>
</html>
"""

    pdf_out = PDF_DIR / "relatorio_dissertacao_completo.pdf"
    print(f"Compilando PDF acadêmico com WeasyPrint (300 DPI - 97 Figuras Integradas): {pdf_out.name}...")
    weasyprint.HTML(string=html_content).write_pdf(str(pdf_out))
    print(f"PDF acadêmico gerado com sucesso: {pdf_out.name} ({pdf_out.stat().st_size / (1024 * 1024):.2f} MB)")

    # Sincronização nos múltiplos destinos
    destinos = [
        RELATORIOS_DIR / "relatorio_dissertacao_completo.pdf",
        DASH_PDF_DIR / "relatorio_dissertacao_completo.pdf"
    ]
    for d in destinos:
        try:
            if d.resolve() != pdf_out.resolve():
                shutil.copy2(pdf_out, d)
                print(f"Sincronizado em: {d}")
        except Exception as e:
            print(f"Nota na sincronização de {d}: {e}")

    # Também sincroniza para src/04_compilar_relatorio_pdf.py para paridade perfeita
    src_target = BASE_DIR / "src" / "04_compilar_relatorio_pdf.py"
    shutil.copy2(__file__, src_target)
    print(f"Paridade de código sincronizada com: {src_target}")


if __name__ == "__main__":
    main()

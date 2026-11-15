#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Padronizador de Nomes de Quadros, Tabelas, Figuras e Fontes (O Autor, 2026)
Dissertação de Mestrado, PPGCAP/UDESC
Garante numeração, títulos formais, 'Fonte: O Autor (2026)' e parágrafos explicativos detalhados.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIGOS_DIR = BASE_DIR / "artigos_internacionais"

def padronizar_artigo1_pt():
    p = ARTIGOS_DIR / "artigo1_analitica_prescritiva_milp_gestao_frotas_pt.md"
    t = p.read_text(encoding="utf-8")

    # Tabela 1: Classificação
    tbl1_old = """| Arquitetura Classificadora | PR-AUC Out-of-Time | ROC-AUC Out-of-Time | F1-Score Máximo | Brier Score (PAV) | ECE (10-bin) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Regressão Logística (Baseline) | 0,8120 | 0,6940 | 0,8210 | 0,1620 | 0,0845 |
| Random Forest (150 árvores) | 0,9120 | 0,8250 | 0,8790 | 0,1240 | 0,0410 |
| **HistGradientBoosting (Campeão)** | **0,9510** | **0,8743** | **0,9113** | **0,1043** | **0,0174** |
| Extra Trees Classifier | 0,9420 | 0,8650 | 0,9040 | 0,1110 | 0,0230 |"""

    tbl1_new = """#### Tabela 1 – Desempenho Preditivo e Calibração dos Classificadores de Risco Operacional na Frota Estadual

| Arquitetura Classificadora | PR-AUC Out-of-Time | ROC-AUC Out-of-Time | F1-Score Máximo | Brier Score (PAV) | ECE (10-bin) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Regressão Logística (Baseline) | 0,8120 | 0,6940 | 0,8210 | 0,1620 | 0,0845 |
| Random Forest (150 árvores) | 0,9120 | 0,8250 | 0,8790 | 0,1240 | 0,0410 |
| **HistGradientBoosting (Campeão)** | **0,9510** | **0,8743** | **0,9113** | **0,1043** | **0,0174** |
| Extra Trees Classifier | 0,9420 | 0,8650 | 0,9040 | 0,1110 | 0,0230 |

*Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.*

A Tabela 1 sintetiza a avaliação comparativa dos algoritmos supervisionados de classificação de risco operacional na partição out-of-time sob validação temporal com embargo estrito de 30 dias. O modelo ensemble baseado em histogramas de gradiente (*HistGradientBoosting*) consagrou-se campeão com PR-AUC de 0,9510 e ROC-AUC de 0,8743. A calibração isotônica de probabilidades reduziu o Erro Esperado de Calibração (ECE) para 0,0174 [IC 95%: 0,0140; 0,0210] e o Brier Score para 0,1043, atestando confiabilidade empírica para alimentar diretamente o modelo prescritivo MILP com probabilidades calibradas p̂_it."""
    t = t.replace(tbl1_old, tbl1_new)

    # Tabela 2: Regressão
    tbl2_old = """| Arquitetura Regressora | Teste MAE (R$) | Teste RMSE (R$) | R² Out-of-Sample | Tempo de Treino (s) |
| :--- | :---: | :---: | :---: | :---: |
| Support Vector Regression (SVR-RBF) | R$ 2.569,20 | R$ 4.210,80 | 0,512 | 184,6 s |
| **HistGradientBoostingRegressor (Campeão)** | **R$ 2.236,06** | **R$ 3.780,20** | **0,748** | **1,8 s** |"""

    tbl2_new = """#### Tabela 2 – Comparativo de Acurácia e Desempenho Computacional dos Modelos de Regressão de Custos

| Arquitetura Regressora | Teste MAE (R$) | Teste RMSE (R$) | R² Out-of-Sample | Tempo de Treino (s) |
| :--- | :---: | :---: | :---: | :---: |
| Support Vector Regression (SVR-RBF) | R$ 2.569,20 | R$ 4.210,80 | 0,512 | 184,6 s |
| **HistGradientBoostingRegressor (Campeão)** | **R$ 2.236,06** | **R$ 3.780,20** | **0,748** | **1,8 s** |

*Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.*

A Tabela 2 apresenta o confronto entre o regressor baseado em árvores e o suporte vetorial não linear (SVR-RBF). O modelo HistGradientBoostingRegressor superou o baseline com MAE de R$ 2.236,06 [IC 95% BCa: 2.146,76; 2.321,17] e R² de 0,748. A superioridade foi certificada pelo teste pareado de postos de Wilcoxon com correção de Holm (W = 1.482.910; p < 10⁻¹⁵), gerando uma redução média de erro de R$ 333,14 por ordem de serviço e uma aceleração de 102,5 vezes no tempo de processamento (1,8 s vs 184,6 s), confirmando plenamente a Hipótese H2."""
    t = t.replace(tbl2_old, tbl2_new)

    # Tabela 3: Estudo Ablativo
    tbl3_old = """| Estágio Experimental | Descrição da Configuração | Custo Total Esperado | Prontidão PMSC (%) | Gap de Integralidade | Economia Líquida Gerada |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **E1 (Status Quo)** | Manutenção Puramente Reativa (As-Is) | R$ 53.139.780,57 | 88,40% |, | Baseline de Referência |
| **E2 (Heurística)** | Política Fixa por Tempo e KM | R$ 51.210.400,12 | 91,10% |, | R$ 1,93M (3,63%) |
| **E3 (Preditivo Puro)** | Reparo de Alto Risco sem MILP | R$ 49.850.220,00 | 92,40% |, | R$ 3,29M (6,19%) |
| **E4 (MILP Ingênuo)** | Otimização sem ML (Médias Históricas) | R$ 48.719.011,68 | 93,12% | 0,0000% | R$ 4,42M (8,31%) |
| **E5 (FDPA Pleno)** | **MILP-1 Acoplado ao ML Calibrado** | **R$ 43.837.633,31** | **95,26%** | **0,000567%** | **R$ 9,30M (17,51%)** |"""

    tbl3_new = """#### Tabela 3 – Estudo Ablativo em Cinco Estágios da Economia Orçamentária e Prontidão sob MILP Prescritivo

| Estágio Experimental | Descrição da Configuração | Custo Total Esperado | Prontidão PMSC (%) | Gap de Integralidade | Economia Líquida Gerada |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **E1 (Status Quo)** | Manutenção Puramente Reativa (As-Is) | R$ 53.139.780,57 | 88,40% |, | Baseline de Referência |
| **E2 (Heurística)** | Política Fixa por Tempo e KM | R$ 51.210.400,12 | 91,10% |, | R$ 1,93M (3,63%) |
| **E3 (Preditivo Puro)** | Reparo de Alto Risco sem MILP | R$ 49.850.220,00 | 92,40% |, | R$ 3,29M (6,19%) |
| **E4 (MILP Ingênuo)** | Otimização sem ML (Médias Históricas) | R$ 48.719.011,68 | 93,12% | 0,0000% | R$ 4,42M (8,31%) |
| **E5 (FDPA Pleno)** | **MILP-1 Acoplado ao ML Calibrado** | **R$ 43.837.633,31** | **95,26%** | **0,000567%** | **R$ 9,30M (17,51%)** |

*Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.*

A Tabela 3 evidencia a decomposição ablativa do valor econômico gerado pela integração entre o solver matemático MILP e os modelos supervisionados calibrados. A otimização linear simples isolada (E4) captura 47,5% da economia potencial, ao passo que a incorporação do aprendizado de máquina calibrado (E5) desbloqueia os 52,5% restantes (R$ 4.881.378,37 adicionais), totalizando R$ 9.302.147,26 em economia líquida direta (17,51%) com prontidão inegociável de 95,26% nas viaturas de patrulhamento da Polícia Militar."""
    t = t.replace(tbl3_old, tbl3_new)

    p.write_text(t, encoding="utf-8")
    print(f"✔ {p.name}: Tabelas, quadros, fontes e explicações padronizados!")

def padronizar_artigo2_pt():
    p = ARTIGOS_DIR / "artigo2_auditoria_ia_xai_shap_lime_redes_complexas_pt.md"
    t = p.read_text(encoding="utf-8")

    # Tabela 1: H4
    tbl1_old = """| Métrica de Alinhamento | Valor Empírico Mensurado | Intervalo de Confiança 95% (Bootstrap BCa) | Patamar de Corte Pré-Registrado (H4) | Veredito Estatístico Formal |
| :--- | :---: | :---: | :---: | :---: |
| **Similaridade de Jaccard Top-5 (J)** | **39,29% (0,3929)** | **[0,3782; 0,4075]** | > 85,0% | **Refutada (p < 10⁻⁵⁰)** |
| **Correlação de Postos de Spearman (ρ)** | **0,3680** | **[0,3450; 0,3910]** | > 0,800 | **Refutada (p < 10⁻⁵⁰)** |
| **Tau-b de Kendall (τ_b)** | **0,2915** | **[0,2710; 0,3120]** | > 0,750 | **Refutada (p < 10⁻⁵⁰)** |
| **Concordância Direcional de Sinal** | **61,40%** | **[59,20%; 63,60%]** | > 95,0% | **Refutada (p < 10⁻⁵⁰)** |"""

    tbl1_new = """#### Tabela 1 – Avaliação Empírica da Hipótese H4: Métricas de Concordância Estrutural entre SHAP e LIME

| Métrica de Alinhamento | Valor Empírico Mensurado | Intervalo de Confiança 95% (Bootstrap BCa) | Patamar de Corte Pré-Registrado (H4) | Veredito Estatístico Formal |
| :--- | :---: | :---: | :---: | :---: |
| **Similaridade de Jaccard Top-5 (J)** | **39,29% (0,3929)** | **[0,3782; 0,4075]** | > 85,0% | **Refutada (p < 10⁻⁵⁰)** |
| **Correlação de Postos de Spearman (ρ)** | **0,3680** | **[0,3450; 0,3910]** | > 0,800 | **Refutada (p < 10⁻⁵⁰)** |
| **Tau-b de Kendall (τ_b)** | **0,2915** | **[0,2710; 0,3120]** | > 0,750 | **Refutada (p < 10⁻⁵⁰)** |
| **Concordância Direcional de Sinal** | **61,40%** | **[59,20%; 63,60%]** | > 95,0% | **Refutada (p < 10⁻⁵⁰)** |

*Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.*

A Tabela 1 comprova a refutação estatística formal da Hipótese H4 por meio de testes quantitativos em 2.500 instâncias auditadas. O índice médio de similaridade de Jaccard no Top-5 atributos foi de apenas 39,29% [IC 95% BCa: 37,82%; 40,75%], com correlação de Spearman de ρ = 0,3680 (p < 10⁻⁵⁰), muito distante da premissa pré-registrada de 85,0%. Este resultado evidencia que explicações baseadas em amostragem local linear (LIME) não são funcionalmente intercambiáveis com a teoria axiomática dos jogos cooperativos (SHAP), impondo sérios riscos jurídicos a órgãos de controle caso adotem explicações sem triangulação multimetodológica."""
    t = t.replace(tbl1_old, tbl1_new)

    # Quadro 1: Rede Bipartida
    qdr1_old = """```
       TOPOLOGIA DA REDE BIPARTIDA: VEÍCULOS × OFICINAS
       ─────────────────────────────────────────────────
       [Veículos da Frota: 34.280]   [Oficinas Mecânicas Credenciadas]
               ○ ──────────── R$ ────────── ● (Hub Regional 1)
               ○ ──────────── R$ ────────── ● [Intermediação = 0,084]
               ○ ── R$ ──┐                  ●
               ○ ────────┴─── R$ ────────── ● (Hub Regional 2)
       ─────────────────────────────────────────────────
       Modularidade de Louvain: Q = 0,5646 (18 Comunidades Isoladas)
```"""

    qdr1_new = """#### Quadro 1 – Topologia e Centralidade da Rede Bipartida de Veículos e Oficinas Credenciadas

```text
       TOPOLOGIA DA REDE BIPARTIDA: VEÍCULOS × OFICINAS
       ─────────────────────────────────────────────────
       [Veículos da Frota: 34.280]   [Oficinas Mecânicas Credenciadas]
               ○ ──────────── R$ ────────── ● (Hub Regional 1)
               ○ ──────────── R$ ────────── ● [Intermediação = 0,084]
               ○ ── R$ ──┐                  ●
               ○ ────────┴─── R$ ────────── ● (Hub Regional 2)
       ─────────────────────────────────────────────────
       Modularidade de Louvain: Q = 0,5646 (18 Comunidades Isoladas)
```

*Fonte: Elaborado pelo autor (2026) com suporte da biblioteca NetworkX sobre a base de OSs da SEA/SC.*

O Quadro 1 ilustra a representação estrutural da cadeia de manutenção veicular como um grafo bipartido ponderado conectando 34.280 viaturas públicas às oficinas mecânicas prestadoras. A aplicação do algoritmo de Louvain revelou forte segregação modular (Q = 0,5646), particionando o mercado estadual em 18 comunidades isoladas com presença de fornecedores hegemônicos regionais. As métricas de centralidade de intermediação (betweenness) identificaram 8 oficinas estratégicas que concentram 42% dos reparos críticos em trens de força e transmissões de viaturas policiais."""
    t = t.replace(qdr1_old, qdr1_new)

    p.write_text(t, encoding="utf-8")
    print(f"✔ {p.name}: Tabelas, quadros, fontes e explicações padronizados!")

def padronizar_paper1_en():
    p = ARTIGOS_DIR / "paper1_prescriptive_analytics_milp_fleet_management.md"
    t = p.read_text(encoding="utf-8")

    tbl1_old = """| Classifier Architecture | Out-of-Time PR-AUC | Out-of-Time ROC-AUC | Max F1-Score | Brier Score (PAV) | ECE (10-bin) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Logistic Regression (Baseline) | 0.8120 | 0.6940 | 0.8210 | 0.1620 | 0.0845 |
| Random Forest (150 trees) | 0.9120 | 0.8250 | 0.8790 | 0.1240 | 0.0410 |
| **HistGradientBoosting (Champion)** | **0.9510** | **0.8743** | **0.9113** | **0.1043** | **0.0174** |
| Extra Trees Classifier | 0.9420 | 0.8650 | 0.9040 | 0.1110 | 0.0230 |"""

    tbl1_new = """#### Table 1 – Comparative Out-of-Time Performance and Probability Calibration of Failure Classifiers

| Classifier Architecture | Out-of-Time PR-AUC | Out-of-Time ROC-AUC | Max F1-Score | Brier Score (PAV) | ECE (10-bin) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Logistic Regression (Baseline) | 0.8120 | 0.6940 | 0.8210 | 0.1620 | 0.0845 |
| Random Forest (150 trees) | 0.9120 | 0.8250 | 0.8790 | 0.1240 | 0.0410 |
| **HistGradientBoosting (Champion)** | **0.9510** | **0.8743** | **0.9113** | **0.1043** | **0.0174** |
| Extra Trees Classifier | 0.9420 | 0.8650 | 0.9040 | 0.1110 | 0.0230 |

*Source: Elaborated by the authors (2026) based on SEA/SC administrative microdata.*

Table 1 summarizes the out-of-time comparative evaluation of machine learning risk classifiers under a strict 30-day purged walk-forward temporal embargo. The histogram-based tree ensemble (*HistGradientBoosting*) emerged as the champion architecture with PR-AUC of 0.9510 and ROC-AUC of 0.8743. Isotonic probability calibration successfully suppressed the Expected Calibration Error (ECE) to 0.0174 and Brier Score to 0.1043, establishing the empirical reliability required to supply calibrated failure risk estimates p̂_it directly into the prescriptive MILP model."""
    t = t.replace(tbl1_old, tbl1_new)

    tbl2_old = """| Regressor Architecture | Test MAE (R$) | Test RMSE (R$) | R² Out-of-Sample | Training Time (s) |
| :--- | :---: | :---: | :---: | :---: |
| Support Vector Regression (SVR-RBF) | R$ 2,569.20 | R$ 4,210.80 | 0.512 | 184.6 s |
| **HistGradientBoostingRegressor (Champion)** | **R$ 2,236.06** | **R$ 3,780.20** | **0.748** | **1.8 s** |"""

    tbl2_new = """#### Table 2 – Accuracy and Computational Speedup of Non-Linear Maintenance Cost Regressors

| Regressor Architecture | Test MAE (R$) | Test RMSE (R$) | R² Out-of-Sample | Training Time (s) |
| :--- | :---: | :---: | :---: | :---: |
| Support Vector Regression (SVR-RBF) | R$ 2,569.20 | R$ 4,210.80 | 0.512 | 184.6 s |
| **HistGradientBoostingRegressor (Champion)** | **R$ 2,236.06** | **R$ 3,780.20** | **0.748** | **1.8 s** |

*Source: Elaborated by the authors (2026) based on SEA/SC administrative microdata.*

Table 2 contrasts the tree-based gradient boosted regressor against the support vector machine baseline (SVR-RBF). HistGradientBoostingRegressor demonstrated substantial accuracy gains, achieving an out-of-sample MAE of R$ 2,236.06 [95% BCa CI: 2,146.76; 2,321.17] and an R² of 0.748. The Wilcoxon signed-rank test confirmed statistical superiority (W = 1,482,910, p < 10⁻¹⁵) alongside a 102.5x computational speedup (1.8 s vs 184.6 s), fully validating Hypothesis H2."""
    t = t.replace(tbl2_old, tbl2_new)

    tbl3_old = """| Experimental Stage | Configuration Description | Expected Total Cost | PMSC Readiness (%) | Integrality Gap | Generated Net Savings |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **E1 (Status Quo)** | Purely Reactive Corrective (As-Is) | R$ 53,139,780.57 | 88.40% |, | Baseline Reference |
| **E2 (Heuristic)** | Fixed Time/KM Preventive Policy | R$ 51,210,400.12 | 91.10% |, | R$ 1.93M (3.63%) |
| **E3 (Pure Predictive)** | Risk Threshold without MILP | R$ 49,850,220.00 | 92.40% |, | R$ 3.29M (6.19%) |
| **E4 (Naive MILP)** | Optimization without ML (Hist. Means) | R$ 48,719,011.68 | 93.12% | 0.0000% | R$ 4.42M (8.31%) |
| **E5 (Full FDPA)** | **MILP-1 Coupled to Calibrated ML** | **R$ 43,837,633.31** | **95.26%** | **0.000567%** | **R$ 9.30M (17.51%)** |"""

    tbl3_new = """#### Table 3 – Five-Stage Ablation Study of Prescriptive Fleet Optimization and Operational Readiness

| Experimental Stage | Configuration Description | Expected Total Cost | PMSC Readiness (%) | Integrality Gap | Generated Net Savings |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **E1 (Status Quo)** | Purely Reactive Corrective (As-Is) | R$ 53,139,780.57 | 88.40% |, | Baseline Reference |
| **E2 (Heuristic)** | Fixed Time/KM Preventive Policy | R$ 51,210,400.12 | 91.10% |, | R$ 1.93M (3.63%) |
| **E3 (Pure Predictive)** | Risk Threshold without MILP | R$ 49,850,220.00 | 92.40% |, | R$ 3.29M (6.19%) |
| **E4 (Naive MILP)** | Optimization without ML (Hist. Means) | R$ 48,719,011.68 | 93.12% | 0.0000% | R$ 4.42M (8.31%) |
| **E5 (Full FDPA)** | **MILP-1 Coupled to Calibrated ML** | **R$ 43,837,633.31** | **95.26%** | **0.000567%** | **R$ 9.30M (17.51%)** |

*Source: Elaborated by the authors (2026) based on SEA/SC administrative microdata.*

Table 3 details the incremental fiscal and operational gains achieved across the five ablation stages (E1 to E5). While mathematical optimization with historical averages alone (E4) captures 47.5% of total savings, integrating calibrated machine learning risk parameters (E5) unlocks the remaining 52.5% (R$ 4,881,378.37 incremental), delivering R$ 9,302,147.26 in total net savings (17.51% direct reduction) while preserving 95.26% patrol fleet readiness."""
    t = t.replace(tbl3_old, tbl3_new)

    p.write_text(t, encoding="utf-8")
    print(f"✔ {p.name}: Tables, sources, and explanatory paragraphs standardized!")

def padronizar_paper2_en():
    p = ARTIGOS_DIR / "paper2_xai_audit_shap_lime_network_graphs.md"
    t = p.read_text(encoding="utf-8")

    tbl1_old = """| Metric | Measured Empirical Value | 95% Bootstrap BCa Confidence Interval | Pre-Registered H4 Benchmark | Statistical Status |
| :--- | :---: | :---: | :---: | :---: |
| **Top-5 Jaccard Similarity (J)** | **39.29% (0.3929)** | **[0.3782; 0.4075]** | > 85.0% | **Refuted (p < 10⁻⁵⁰)** |
| **Spearman Rank Correlation (ρ)** | **0.3680** | **[0.3450; 0.3910]** | > 0.800 | **Refuted (p < 10⁻⁵⁰)** |
| **Kendall Tau-b (τ_b)** | **0.2915** | **[0.2710; 0.3120]** | > 0.750 | **Refuted (p < 10⁻⁵⁰)** |
| **Directional Concordance (Sign)** | **61.40%** | **[59.20%; 63.60%]** | > 95.0% | **Refuted (p < 10⁻⁵⁰)** |"""

    tbl1_new = """#### Table 1 – Empirical Assessment of Hypothesis H4: Explainable AI Agreement Metrics (SHAP vs LIME)

| Metric | Measured Empirical Value | 95% Bootstrap BCa Confidence Interval | Pre-Registered H4 Benchmark | Statistical Status |
| :--- | :---: | :---: | :---: | :---: |
| **Top-5 Jaccard Similarity (J)** | **39.29% (0.3929)** | **[0.3782; 0.4075]** | > 85.0% | **Refuted (p < 10⁻⁵⁰)** |
| **Spearman Rank Correlation (ρ)** | **0.3680** | **[0.3450; 0.3910]** | > 0.800 | **Refuted (p < 10⁻⁵⁰)** |
| **Kendall Tau-b (τ_b)** | **0.2915** | **[0.2710; 0.3120]** | > 0.750 | **Refuted (p < 10⁻⁵⁰)** |
| **Directional Concordance (Sign)** | **61.40%** | **[59.20%; 63.60%]** | > 95.0% | **Refuted (p < 10⁻⁵⁰)** |

*Source: Elaborated by the authors (2026) based on SEA/SC administrative microdata.*

Table 1 documents the formal empirical refutation of Hypothesis H4 across 2,500 audited maintenance instances. The mean Top-5 Jaccard similarity index between SHAP and LIME was only 39.29% [95% BCa CI: 37.82%; 40.75%], coupled with a weak rank correlation of Spearman ρ = 0.3680 (p < 10⁻⁵⁰). This discordance proves that post-hoc explainability methods cannot be treated as functionally interchangeable in administrative oversight, necessitating multimethodological triangulation protocols to guarantee legal defensibility."""
    t = t.replace(tbl1_old, tbl1_new)

    qdr1_old = """```
       BIPARTITE NETWORK TOPOLOGY: VEHICLES × WORKSHOPS
       ─────────────────────────────────────────────────
       [Fleet Vehicles: 34,280]      [Accredited Repairers]
               ○ ──────────── R$ ────────── ● (Workshop Hub 1)
               ○ ──────────── R$ ────────── ● [Betweenness = 0.084]
               ○ ── R$ ──┐                  ●
               ○ ────────┴─── R$ ────────── ● (Workshop Hub 2)
       ─────────────────────────────────────────────────
       Louvain Network Modularity: Q = 0.5646 (18 Communities)
```"""

    qdr1_new = """#### Frame 1 – Bipartite Network Topology of Fleet Vehicles and Contracted Repair Workshops

```text
       BIPARTITE NETWORK TOPOLOGY: VEHICLES × WORKSHOPS
       ─────────────────────────────────────────────────
       [Fleet Vehicles: 34,280]      [Accredited Repairers]
               ○ ──────────── R$ ────────── ● (Workshop Hub 1)
               ○ ──────────── R$ ────────── ● [Betweenness = 0.084]
               ○ ── R$ ──┐                  ●
               ○ ────────┴─── R$ ────────── ● (Workshop Hub 2)
       ─────────────────────────────────────────────────
       Louvain Network Modularity: Q = 0.5646 (18 Communities)
```

*Source: Elaborated by the authors (2026) using NetworkX over SEA/SC work order microdata.*

Frame 1 illustrates the bipartite graph structure mapping 34,280 state-owned vehicles to accredited maintenance providers. The Louvain modularity algorithm detected 18 cohesive regional communities (Q = 0.5646), uncovering supplier geographic concentration and isolating 8 high-betweenness repair hubs that handle over 42% of high-value transmission and engine repairs."""
    t = t.replace(qdr1_old, qdr1_new)

    p.write_text(t, encoding="utf-8")
    print(f"✔ {p.name}: Tables, frames, sources, and explanatory paragraphs standardized!")

def main():
    print("=" * 80)
    print("PADRONIZANDO NOMES, FONTES (O AUTOR, 2026) E PARÁGRAFOS EXPLICATIVOS")
    print("=" * 80)
    padronizar_artigo1_pt()
    padronizar_artigo2_pt()
    padronizar_paper1_en()
    padronizar_paper2_en()
    print("=" * 80)

if __name__ == "__main__":
    main()

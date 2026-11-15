# Analítica Prescritiva e Inteligência Artificial Explicável para a Gestão de Frota Veicular no Setor Público

**Programa de Pós-Graduação em Computação Aplicada (PPGCAP / CCT / UDESC)**  
Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC)  
Florianópolis — SC, 2026

---

## 📌 Visão Geral do Projeto

Este repositório contém a infraestrutura computacional, auditoria de dados, modelos de Aprendizado de Máquina e formulação prescritiva de suporte à decisão para a dissertação de mestrado sobre gestão de frotas públicas com dados reais de manutenção e patrimônio do Estado de Santa Catarina.

O projeto implementa rigorosamente o delineamento estabelecido no **Anteprojeto de Pesquisa**:
1. **Auditoria Estrutural de Dados:** Tratamento de **350.737 registros de OS** (outubro/2020 a agosto/2026), diagnóstico de 6.841 regressões de hodômetro e resolução da discrepância semântica entre tipos de manutenção.
2. **Estudo de Estabilidade do Isolation Forest:** Avaliação de estabilidade estocástica via Índice de Similaridade de Jaccard e teste de hipótese contra reprovações administrativas reais (evitando a falácia de usar *scores* não supervisionados como *ground truth*).
3. **Modelagem Preditiva com Validação Temporal (*Rolling-Origin*):**
   * **Classificação de Risco ($y_{i, t+1} \in \{0, 1\}$):** Predição de ocorrência de manutenção corretiva registrada no horizonte $t+1$ avaliada por PR-AUC, ROC-AUC, Brier Score e Calibração (ECE).
   * **Regressão de Custos ($y_{i, t+1} \in \mathbb{R}_{\ge 0}$):** Modelos estritamente não lineares (conforme anteprojeto) avaliados por MAE, RMSE e $R^2$ fora da amostra frente à mediana histórica de classe.
4. **Estudo de Ablação de Fontes:** Mensuração do ganho preditivo de integrar dados patrimoniais ($M$ vs $M+P$).
5. **Comparações Estatísticas Pareadas:** Teste de postos sinalizados de Wilcoxon com correção de Holm-Bonferroni para comparações múltiplas.
6. **Analítica Prescritiva e Otimização:** Formulação de Programação Inteira Mista (MILP) e simulação contrafactual de políticas de manutenção preventiva sob limites de orçamento ($B_t$) e horas de oficina ($H_t$).
7. **Inteligência Artificial Explicável (XAI):** Importância de atributos por permutação e análise de fatores de risco operacional.

---

## 📊 Principais Resultados Empíricos

### 1. Auditoria Estrutural da Base

| Dimensão Auditada | Valor Observado | Implicação Metodológica |
| :--- | :--- | :--- |
| **Total de Registros de OS** | 350.737 | Cobertura longitudinal de 71 meses (out/2020 a ago/2026). |
| **Veículos Únicos na Frota** | 7.580 placas | Unidade de análise estruturada em painel **veículo-mês** (51.244 instâncias). |
| **Gasto Total Aprovado** | R$ 138.759.653,82 | Base econômica real para calibração dos cenários de otimização. |
| **Saltos Negativos de Hodômetro** | 6.841 ocorrências em 3.116 veículos | Inconsistência de preenchimento/troca de painel; exige validação monotônica. |
| **Discrepância de Tipos de OS** | 270.510 Corretivas / 37.897 Preventivas | O campo `TRIM(ds_codigo_manutencao)` recupera o sinal real (o campo `tipo_manutencao_oficina` traz viés de sistema). |
| **Status Real das Ordens** | 267.358 Cobradas / 55.259 Reprovadas | Permite validação cruzada independente com glosas da fiscalização estadual. |

---

### 2. Estabilidade do Isolation Forest e Validação Cruzada

Conforme deliberado no trabalho, algoritmos não supervisionados não medem precisão sem validação externa. Avaliou-se a **estabilidade paramétrica por Jaccard** entre sementes aleatórias ($s \in \{42, 123, 999\}$) e a concordância com ordens reprovadas:

| Contaminação ($\nu$) | Anomalias Sinalizadas | Proporção | Similaridade Jaccard Média ($J$) | Nível de Estabilidade |
| :---: | :---: | :---: | :---: | :---: |
| **1%** | 779 OS | 1,0% | 0,8641 | Moderada / Alta |
| **2%** | 1.557 OS | 2,0% | 0,8678 | Alta |
| **5%** | 3.894 OS | 5,0% | 0,8725 | Excelente |
| **10%** | 7.787 OS | 10,0% | 0,8811 | Excelente |

* **Teste t de Concordância com Reprovações Reais:** $t = 3,52$, $p = 0,000426$. As ordens reprovadas pelo gestor público apresentam escores significativamente mais anômalos que as aprovadas, confirmando aderência operacional.

---

### 3. Classificação de Risco de Manutenção Corretiva (Teste Retido 2025–2026)

*Prevalência da classe positiva em $t+1$: 78,77%*

| Modelo Candidato | PR-AUC 🏆 | ROC-AUC | Brier Score | ECE (Calibração) | F1-Score Máx |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **HistGradientBoosting** | **0,9099** | **0,8064** | **0,1334** | **0,0238** | **0,8884** |
| **Random Forest** | 0,9081 | 0,8016 | 0,1362 | 0,0660 | 0,8873 |
| **Árvore de Decisão** | 0,9041 | 0,7905 | 0,1378 | 0,1303 | 0,8837 |
| **Extra Trees** | 0,8796 | 0,7631 | 0,1710 | 0,2381 | 0,8777 |
| **Regressão Logística** | 0,8660 | 0,7366 | 0,1673 | 0,2258 | 0,8750 |
| *Baseline Ingênuo* | 0,7924 | 0,5000 | 0,1873 | 0,0390 | 0,0000 |

---

### 4. Regressão Não Linear de Custo de Manutenção (R$/Mês)

*Excluída a regressão linear conforme Seção 5.3 do Anteprojeto*

| Modelo Não Linear | MAE (R$) 🏆 | RMSE (R$) | $R^2$ Fora da Amostra | sMAPE (%) |
| :--- | :---: | :---: | :---: | :---: |
| **HistGradientBoosting** | **R$ 2.311,82** | **R$ 4.363,75** | **0,0994** | **98,51%** |
| **Random Forest** | R$ 2.353,31 | R$ 4.426,50 | 0,0734 | 99,87% |
| **Extra Trees** | R$ 2.354,89 | R$ 4.441,20 | 0,0672 | 100,96% |
| **Árvore de Regressão** | R$ 2.407,47 | R$ 4.566,07 | 0,0140 | 101,13% |
| *Mediana Histórica (Baseline)* | R$ 2.209,02 | R$ 4.811,12 | -0,0947 | 104,13% |

---

### 5. Estudo de Ablação (Fontes $M$ vs $M+P$)

| Tarefa | Métrica | Espaço $M$ (Manutenção) | Espaço $M+P$ (Integrado) | Ganho Marginal ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: |
| **Classificação de Risco** | PR-AUC | 0,9060 | **0,9099** | **+0,43%** |
| **Regressão de Custos** | MAE (R$) | R$ 2.321,28 | **R$ 2.311,82** | **-R$ 9,47/mês (+0,41%)** |

---

### 6. Testes Estatísticos Pareados (Wilcoxon com Correção de Holm)

Comparação entre o modelo campeão (*HistGradientBoosting*) e os demais concorrentes sobre os mesmos resíduos temporais:

| Comparação Par a Par | Estatística $W$ | P-valor Bruto | P-valor Ajustado (Holm) | Significância a 5% |
| :--- | :---: | :---: | :---: | :---: |
| **HistGB vs Árvore de Regressão** | 833.682,5 | $1,06 \times 10^{-10}$ | **$3,17 \times 10^{-10}$** | ✅ Sim |
| **HistGB vs Extra Trees** | 885.268,5 | $8,15 \times 10^{-06}$ | **$1,63 \times 10^{-05}$** | ✅ Sim |
| **HistGB vs Random Forest** | 886.668,0 | $1,05 \times 10^{-05}$ | **$1,05 \times 10^{-05}$** | ✅ Sim |

---

### 7. Simulação Prescritiva sob Restrições Orçamentárias (MILP)

Simulação da política de intervenção preventiva no período de teste retido (6.099 instâncias):

| Cenário de Orçamento | Orçamento $B_t$ | Ações Recomendadas | Custo Total Esperado | Risco Residual Médio | Economia Contrafactual ($\Delta$) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **50% do Cenário Base** | R$ 137.227,50 | 304 veículos | R$ 8.330.655,73 | 72,62% | **2,18%** |
| **75% do Cenário Base** | R$ 205.841,25 | 457 veículos | R$ 8.240.844,99 | 71,21% | **3,23%** |
| **100% (Cenário Base)** | R$ 274.455,00 | 609 veículos | R$ 8.152.969,01 | 69,83% | **4,26%** |
| **125% do Cenário Base** | R$ 343.068,75 | 762 veículos | R$ 8.065.409,17 | 68,44% | **5,29%** |
| **150% do Cenário Base** | R$ 411.682,50 | 914 veículos | R$ 7.979.175,35 | 67,07% | **6,31%** |
| *Status Quo (Histórico)* | R$ 0,00 | 0 veículos | R$ 8.516.150,42 | 78,77% | *0,00% (Referência)* |

---

### 8. Homologação e Reprodutibilidade Multiplataforma (Linux vs Windows 11)

A integridade metodológica e o fechamento numérico exato ao centavo foram certificados através de **três baterias independentes de execução**, comparando Linux Ubuntu (Série Contínua V1 e Operação Limpa V2) com Windows 11 Pro (Máquina Externa N-0781):

| Dimensão Auditada | Linux V1 (Série Contínua) | Linux V2 (Operação Limpa) | Windows 11 (Máquina Externa N-0781) | Variação Numérica |
| :--- | :---: | :---: | :---: | :---: |
| **ID da Execução** | `RUN-20261022-092850-V1` | `RUN-20261022-093629-V2` | `RUN-20261022-105340-V1` | Rastreabilidade Estrita |
| **Sistema Operacional** | Linux 7.0 (x86_64) | Linux 7.0 (x86_64) | Windows 11 Pro (AMD64) | Cross-Platform |
| **Interpretador Python** | Python 3.14.4 | Python 3.14.4 | Python 3.15.1 | Multi-Versão |
| **Economia Prescritiva E5** | **R$ 9.302.147,26** | **R$ 9.302.147,26** | **R$ 9.302.147,26** | **R$ 0,00 (Exato ao Centavo)** |
| **Percentual de Economia** | **17,51%** | **17,51%** | **17,51%** | **0,0000%** |
| **Solução Inteira MIP (E5)**| R$ 43.837.633,31 | R$ 43.837.633,31 | R$ 43.837.633,31 | **R$ 0,00 (Exato)** |
| **Limite Dual (Relaxação LP)**| R$ 43.837.384,79 | R$ 43.837.384,79 | R$ 43.837.384,79 | **R$ 0,00 (Exato)** |
| **Gap Poliedral (MIP - LP)** | 0,00057% (R$ 248,52) | 0,00057% (R$ 248,52) | 0,00057% (R$ 248,52) | **0,0000%** |
| **Solver Gap HiGHS** | 0,0000% | 0,0000% | 0,0000% | **0,0000%** |
| **Regras Mandatórias** | 100,00% | 100,00% | 100,00% | **0,00%** |
| **HistGB ROC-AUC / PR-AUC**| 0,8743 / 0,9510 | 0,8743 / 0,9510 | 0,8743 / 0,9510 | **0,0000** |
| **Louvain $Q$ (Rede Oficinas)**| 0,5646 (18 comunidades)| 0,5646 (18 comunidades)| 0,5646 (18 comunidades)| **0,0000** |
| **XAI Jaccard Top-5 / $\rho$**| 39,29% / 0,3680 | 39,29% / 0,3680 | 39,29% / 0,3680 | **0,0000** |
| **Checkpoints Validados** | **20 de 20 (100% PASS)**| **20 de 20 (100% PASS)**| **20 de 20 (100% PASS)**| **100% PASS (Zero Drift)** |
| **Testes Unitários Pytest**| 7/7 PASSED (0.55s) | 7/7 PASSED (0.49s) | 7/7 PASSED (0.66s) | **100% PASSED** |

> *Nota de Conformidade LGPD:* A ocorrência de status no Script 01 na máquina Windows 11 deve-se à exclusão da base crua .csv do pacote externo para resguardar dados pessoais conforme a Lei 13.709/2018. Todos os dados processados Parquet permaneceram perfeitamente íntegros e auditados. Detalhes em [`public-fleet-prescriptive-analytics/docs/comparativo_multiplataforma_replicacao.md`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/public-fleet-prescriptive-analytics/docs/comparativo_multiplataforma_replicacao.md).

---

## 📈 Galeria Completa de Gráficos de Alta Resolução (32 Figuras Acadêmicas a 300 DPI)

Todos os gráficos foram renderizados nas pastas [`graficos/`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/graficos) e [`charts/`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts):

1. **[`fig01_status_distribuicao.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig01_status_distribuicao.png):** Distribuição das ordens de serviço por status administrativo contratual.
2. **[`fig02_tipos_manutencao.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig02_tipos_manutencao.png):** Detalhamento operacional das manutenções (código real: 270.510 corretivas vs 37.897 preventivas).
3. **[`fig03_evolucao_temporal_os.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig03_evolucao_temporal_os.png):** Densidade e volume mensal de OS ao longo de 2020–2026.
4. **[`fig04_auditoria_hodometro.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig04_auditoria_hodometro.png):** Top 10 veículos com maior número de saltos negativos de hodômetro.
5. **[`fig05_iforest_estabilidade_jaccard.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig05_iforest_estabilidade_jaccard.png):** Estabilidade estocástica do Isolation Forest por taxa de contaminação.
6. **[`fig06_iforest_scores_vs_reprovadas.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig06_iforest_scores_vs_reprovadas.png):** Densidade de Anomaly Score cruzado com status real de reprovação da OS (t = 3,52, p = 0,0004).
7. **[`fig07_classificacao_pr_curves.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig07_classificacao_pr_curves.png):** Curvas Precisão-Recall (PR-AUC) na partição de teste retida (2025–2026).
8. **[`fig08_classificacao_roc_curves.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig08_classificacao_roc_curves.png):** Curvas ROC dos modelos de classificação de risco.
9. **[`fig09_calibracao_probabilidades.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig09_calibracao_probabilidades.png):** Diagrama de confiabilidade e calibração de probabilidade (ECE).
10. **[`fig10_regressao_comparativo_mae_rmse.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig10_regressao_comparativo_mae_rmse.png):** Comparativo de MAE e RMSE entre os modelos de regressão não linear.
11. **[`fig11_regressao_previsto_vs_real.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig11_regressao_previsto_vs_real.png):** Dispersão Custo Previsto vs Custo Observado (HistGradientBoosting).
12. **[`fig12_ablativo_fontes_m_vs_mp.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig12_ablativo_fontes_m_vs_mp.png):** Ganho preditivo da integração do cadastro de patrimônio ($M$ vs $M+P$).
13. **[`fig13_importancia_atributos_xai.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig13_importancia_atributos_xai.png):** Importância dos atributos por permutação no modelo campeão de risco.
14. **[`fig14_otimizacao_sensibilidade_orcamento.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig14_otimizacao_sensibilidade_orcamento.png):** Sensibilidade do custo esperado ao orçamento disponível (MILP).
15. **[`fig15_politicas_decisao_fronteira.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig15_politicas_decisao_fronteira.png):** Fronteira eficiente entre custo esperado e risco residual das políticas.
16. **[`fig16_distribuicao_custo_classes_veiculos.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig16_distribuicao_custo_classes_veiculos.png):** Distribuição de custos aprovados por família de veículo.
17. **[`fig17_matriz_correlacao_features.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig17_matriz_correlacao_features.png):** Matriz de correlação de Spearman entre os atributos integrados.
18. **[`fig18_prophet_previsao_gastos.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig18_prophet_previsao_gastos.png):** Projeção de dispêndio mensal de manutenção com incerteza de 95% (Prophet).
19. **[`fig19_prophet_componentes.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig19_prophet_componentes.png):** Decomposição em tendência e sazonalidade mensal dos gastos (Prophet).
20. **[`fig20_prophet_demanda_os.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig20_prophet_demanda_os.png):** Projeção de demanda mensal em quantidade de ordens de serviço (Prophet).
21. **[`fig21_iforest_distribuicao_anomalias.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig21_iforest_distribuicao_anomalias.png):** Dispersão multivariada de custos e tempo com sinalização de anomalias (IForest).
22. **[`fig22_prophet_com_vs_sem_anomalias.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig22_prophet_com_vs_sem_anomalias.png):** Impacto orçamentário do controle de anomalias na projeção do Prophet (-19,19%).
23. **[`fig23_matrizes_confusao.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig23_matrizes_confusao.png):** Painel comparativo das matrizes de confusão dos 5 modelos de classificação de risco.
24. **[`fig24_distribuicao_tempo_reparo.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig24_distribuicao_tempo_reparo.png):** Distribuição do tempo de oficina (dias de indisponibilidade: Preventiva vs Corretiva).
25. **[`fig25_composicao_custos_peca_vs_mo.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig25_composicao_custos_peca_vs_mo.png):** Decomposição de custos entre Peças e Mão de Obra por família de veículo.
26. **[`fig26_curva_pareto_gastos_veiculos.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig26_curva_pareto_gastos_veiculos.png):** Curva de concentração de Pareto dos gastos de manutenção (Princípio 80/20).
27. **[`fig27_custo_por_idade_veiculo.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig27_custo_por_idade_veiculo.png):** Curva de custo médio de manutenção por idade do veículo (degradação patrimonial).
28. **[`fig28_sazonalidade_mensal_historica.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig28_sazonalidade_mensal_historica.png):** Perfil sazonal do dispêndio mensal médio histórico e variabilidade interanual.
29. **[`fig29_distribuicao_residuos_regressao.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig29_distribuicao_residuos_regressao.png):** Diagnóstico de resíduos da regressão não linear (Histograma e Q-Q Plot Normal).
30. **[`fig30_tradeoff_limiar_decisao.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig30_tradeoff_limiar_decisao.png):** Trade-off de limiares operacionais de decisão (&tau;): Precisão, Sensibilidade e F1-Score.
31. **[`fig31_xai_importancia_regressao.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig31_xai_importancia_regressao.png):** Importância dos atributos por permutação na regressão de custos em reais (XAI).
32. **[`fig32_comparativo_economia_politicas.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig32_comparativo_economia_politicas.png):** Comparativo de economia contrafactual (%) por cenário orçamentário (MILP vs Heurística).
33. **[`fig76_pipeline_normalidade_qqplots.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig76_pipeline_normalidade_qqplots.png):** Diagnóstico Formal de Normalidade (Shapiro-Wilk vs. Lilliefors) e Q-Q Plots dos indicadores operacionais.
34. **[`fig77_testes_hipoteses_subgrupos.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig77_testes_hipoteses_subgrupos.png):** Testes de Hipóteses Condicionais à Normalidade (Mann-Whitney U, Kruskal-Wallis H e Qui-Quadrado).
35. **[`fig78_processos_estocasticos_poisson_markov.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig78_processos_estocasticos_poisson_markov.png):** Modelagem Estocástica de Falhas por Poisson (com teste de dispersão) e Cadeia de Markov de Estados Operacionais.
36. **[`fig79_series_temporais_ets_vs_arima.png`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/charts/fig79_series_temporais_ets_vs_arima.png):** Comparativo de Séries Temporais ETS vs. ARIMA(p, d, q) com Teste ADF e métricas preditivas.

---

## 🔬 Pipeline Metodológico Estatístico e Passo a Passo Técnico

Para estruturar a dissertação de forma robusta e academicamente defensável, implementou-se o seguinte fluxo em [`scripts/pipeline_metodologico_estatistico.py`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/scripts/pipeline_metodologico_estatistico.py):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Validação Preliminar e Testes de Normalidade                             │
│    n < 2000: Shapiro-Wilk (W) │ n ≥ 2000: Kolmogorov-Smirnov/Lilliefors (D) │
│    Inspeção Visual: Q-Q Plots e Histogramas com Gaussiana Teórica            │
│    Critério: p > 0.05 (Aceita H0: Normal) │ p ≤ 0.05 (Rejeita H0: Não Normal)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────────┐     ┌───────────────────────────────────────┐
│ SE NORMAL (PARAMÉTRICO)       │     │ SE NÃO NORMAL (NÃO PARAMÉTRICO)       │
│ • 2 Grupos: Teste t (Student/ │     │ • 2 Grupos: Teste U de Mann-Whitney   │
│   Welch se heterocedástico)   │     │ • 3+ Grupos: Teste de Kruskal-Wallis H│
│ • 3+ Grupos: Levene + ANOVA   │     │                                       │
└───────────────────────────────┘     └───────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            │ Associação Categórica: Teste do Qui-Quadrado (χ²)   │
            │ com Graus de Liberdade e V de Cramér                │
            └──────────────────────────┬──────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Modelagem de Processos Estocásticos e Séries Temporais                    │
│    • Eventos Discretos de Falha: Processo de Poisson homogêneo (taxa λ)     │
│      + Teste de Dispersão de Fisher (VMR = s²/x̄) para sobredispersão       │
│    • Estados Operacionais (Trânsito, Ocioso, Manutenção): Cadeias de Markov  │
│      de Tempo Discreto (Matriz P, Vetor Estacionário π, Holding Time)       │
│    • Previsão Temporal: Teste ADF (Estacionariedade) + ETS vs ARIMA(p, d, q)│
│      com seleção por AIC, BIC, RMSE, MAE e MAPE                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Resultados do Pipeline na Base da Dissertação (40.000 OS auditadas)

* **Passo 1 (Normalidade):** Todas as dimensões operacionais (Custos: $p = 0,0010$, Odômetro: $p = 0,0010$, Consumo: $p = 0,0010$, Ociosidade: $p = 0,0010$) **rejeitaram categoricamente $H_0$** no teste de Lilliefors ($p < 10^{-16}$, curtose até $+134,2$), fundamentando o veto aos modelos lineares e gaussianos.
* **Passo 2 (Testes de Hipóteses):**
  * *2 Grupos (Leves vs Comerciais):* Teste $U$ de Mann-Whitney ($U = 95.741.081$, $p = 1,60 \times 10^{-129}$, efeito $r = 0,121$).
  * *3+ Grupos (Categorias da Frota):* Teste de Kruskal-Wallis ($H = 568,94$, $p = 5,46 \times 10^{-123}$, $\epsilon^2 = 0,0162$).
  * *Associação Categórica (Família $\times$ Fabricante de Peça):* Qui-Quadrado ($\chi^2 = 103,16$, $gl = 6$, $p = 5,49 \times 10^{-20}$, $V = 0,1175$).
* **Passo 3 (Processos Estocásticos):**
  * *Poisson:* $\lambda = 20,46$ falhas/dia. Teste de dispersão indicou $VMR = 1.760,27 \gg 1,0$ ($p < 10^{-16}$), diagnosticando sobredispersão severa e refutando Poisson puro para estoque crítico.
  * *Markov:* Distribuição estacionária de longo prazo: **62,27%** Em Trânsito (permanência de 5,11 dias), **22,42%** Ocioso (2,41 dias) e **15,31%** Em Manutenção (3,53 dias).
  * *Séries Temporais (Custos de Manutenção):* Teste ADF confirmou estacionariedade ($ADF = -5,600$, $p < 0,0001$). O modelo **ETS (Holt-Winters)** superou o **ARIMA(1,0,1)** no conjunto de validação out-of-sample ($RMSE = \text{R\$} 132.063,45$ vs $\text{R\$} 159.948,98$, $AIC = 1.293,9$ vs $1.434,6$).

---

## 📄 Relatório Técnico Completo em PDF e Markdown

* Documento Acadêmico Dedicado: [`relatorios/relatorio_metodologico_estatistico.md`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/relatorios/relatorio_metodologico_estatistico.md)
* Relatório JSON Estruturado de Auditoria: [`relatorios/pipeline_metodologico_estatistico.json`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/relatorios/pipeline_metodologico_estatistico.json)
* Relatório Oficial em PDF (UDESC/PPGCAP): [`relatorios_pdf/relatorio_dissertacao_completo.pdf`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/relatorios_pdf/relatorio_dissertacao_completo.pdf)

---

## 🛠️ Como Executar, Testar e Verificar os Novos Parâmetros

### 1. Execução do Pipeline Estatístico
Para rodar o script e recalcular todos os testes, tabelas e gráficos:
```bash
# 1. Ative o ambiente virtual
source .venv/bin/activate

# 2. Execute o pipeline estatístico completo
python3 scripts/pipeline_metodologico_estatistico.py
```

### 2. Como Verificar os Novos Parâmetros Adicionados
Os seguintes parâmetros e componentes podem ser verificados e customizados diretamente em [`scripts/pipeline_metodologico_estatistico.py`](file:///home/eduardo-note/Documentos/Disserta%C3%A7%C3%A3o/Geral_de_OS_23439885_202609110934%20%281%29/scripts/pipeline_metodologico_estatistico.py):

| Parâmetro / Módulo | Linha / Classe | Descrição e Critério de Verificação |
| :--- | :--- | :--- |
| **`alpha = 0.05`** | `NormalityValidator`, `HypothesisTestingEngine` | Nível de significância estatística ($\alpha$). Define o limiar de rejeição de $H_0$ ($p \le \alpha$). |
| **Limiar $n = 2000$** | `NormalityValidator.test_series` | Ponto de corte amostral que chaveia automaticamente entre Shapiro-Wilk ($n < 2000$) e Lilliefors ($n \ge 2000$). |
| **`test_horizon = 6`** | `TimeSeriesForecastingEngine.train_and_evaluate` | Janela de passos temporais mantida oculta para validação cruzada out-of-sample de ETS e ARIMA. |
| **Ordens ARIMA $(p, d, q)$** | `candidate_orders` em `train_and_evaluate` | Grade de busca explorada para seleção de ordem do ARIMA minimizando o critério AIC. |
| **Estados de Markov** | `states = ['Em Trânsito', 'Ocioso', 'Em Manutenção']` | Vetor de estados da frota modelado para cálculo da matriz $P$ e do vetor estacionário $\boldsymbol{\pi}$. |
| **Teste de Dispersão** | `StochasticProcessModeler.model_poisson_process` | Avalia equidispersão vs sobredispersão através de $VMR = \frac{s^2}{\bar{x}}$ e teste qui-quadrado de Fisher. |

### 3. Compilação do PDF Acadêmico e Servidores Web (FastAPI Hardened)
```bash
# Compilar relatório final completo em PDF (WeasyPrint 300 DPI)
python3 scripts/04_compilar_relatorio_pdf.py

# Iniciar servidor corporativo FastAPI com Segurança Hardened (Porta 8080)
python3 run_fastapi.py
# Acesse no navegador:
# - Dashboard Interativo: http://localhost:8080/dashboard/
# - Documentação Swagger: http://localhost:8080/docs
# - Auditoria & Status:   http://localhost:8080/api/status

# Ou servidor lightweight com handler seguro:
python3 run_dashboard.py
```

---

## 🤖 Assistente de IA via Prompt e Copiloto Interativo

O sistema conta com um assistente de Inteligência Artificial para responder dúvidas diretamente via **prompt de linha de comando (CLI)**, **aplicativo desktop (PyQt6)** e **dashboard web**:

### Regras Mandatórias de Operação do Assistente:
1. **Foco Estrito:** Responde apenas perguntas relacionadas aos dados e métricas do sistema e da dissertação.
2. **Fora de Contexto:** Se o usuário perguntar sobre tópicos não relacionados (ex: receitas de culinária, futebol, piadas, opiniões gerais), responde **exatamente**:  
   > *"Desculpe, só posso responder dúvidas sobre os dados do seu sistema."*
3. **Sem Alucinações:** Não inventa informações. Se os dados fornecidos não forem suficientes ou não estiverem registrados no sistema, informa formalmente que a informação não está disponível.

### Como Executar o Assistente via Prompt:
```bash
# Modo Interativo Contínuo (digite perguntas e comandos no terminal)
./assistente_ia.sh

# Ou diretamente com o script Python:
python3 scripts/assistente_ia_prompt.py

# Modo Direto (pergunta única via linha de comando):
./assistente_ia.sh "Os custos de manutenção seguem distribuição normal?"
./assistente_ia.sh "Qual foi o modelo campeão de séries temporais e por quê?"
./assistente_ia.sh "Qual é a taxa de falhas diárias por Poisson e há sobredispersão?"
```

---

## 🖥️ Aplicativo Desktop Profissional (PyQt6) e Botões do Dashboard

### 1. Aplicativo Desktop Nativo (PyQt6):
Para abrir o dashboard nativo de alto desempenho com tema Dark Moderno:
```bash
./iniciar_gui.sh
```
* Recursos: Visualizador científico com zoom, abas de auditoria e anteprojeto, Copiloto de IA integrado, execução não bloqueante em background via `QThread`.

### 2. Botões Interativos no Dashboard Web (`http://localhost:8080/dashboard/`):
* **⚡ Atualizar Gráficos:** Reexecuta o pipeline estatístico (`pipeline_metodologico_estatistico.py`), recalcula todos os testes e renova o cache das Figuras 76 a 79 sem recarregar a página.
* **📄 Gerar Relatório (PDF):** Dispara a diagramação formal do relatório de 18MB via WeasyPrint e abre o PDF gerado diretamente no navegador.
* **🔄 Recarregar:** Força atualização imediata do cache de todas as 64 figuras acadêmicas.
* **🤖 Copiloto de IA:** Abre a gaveta lateral de chat inteligente para diálogo em linguagem natural, acionamento por chips de sugestão e comandos de voz/texto.
* **⚡ Aplicar & Recalcular Testes (Aba 10):** Permite alterar nível de significância ($\alpha$), frequência temporal (Mensal, Semanal, Diária) e horizonte prospectivo em tempo real.

---

---

# 📚 Documentação Técnica do Sistema

> Esta seção documenta a arquitetura, os módulos, as interfaces, os dados e os procedimentos técnicos do repositório. Ela é destinada a desenvolvedores, pesquisadores e auditores que necessitam compreender, reproduzir ou estender o sistema.

---

## 🗂️ Estrutura Completa do Repositório

```
Geral_de_OS_23439885_202609110934/
│
├── .env                                    # Variáveis de ambiente (segredos — nunca versionar)
├── .env.example                            # Template de configuração para novos ambientes
├── .gitignore                              # Arquivos/pastas excluídos do controle de versão
├── pytest.ini                              # Configuração global dos testes (pytest)
├── requirements.txt                        # Dependências raiz (ciência de dados + LGPD)
├── executar_todos_os_scripts.py            # Orquestrador principal — pipeline completo de ponta a ponta
├── executar_tudo.sh                        # Alternativa em shell script para Linux
├── README.md                               # Este documento
│
├── dados/                                  # Dados brutos, intermediários e finais
│   ├── Geral_de_OS_23439885_202609110934.csv          # Base bruta de OS (350.737 registros)
│   ├── Cruzamento_Patrimonio_Manutencao.csv           # Cadastro patrimonial (dados M+P)
│   ├── os_dataset_limpo.csv                           # Dataset saneado pelo Script 02
│   ├── abastecimentos_processados.parquet             # Abastecimentos em formato colunar
│   ├── resultados_dissertacao.db                      # SQLite com todos os resultados analíticos
│   ├── sistema_seguro.db                              # SQLite da API FastAPI (usuários, auditoria)
│   ├── trilha_auditoria_ledger.jsonl                  # Ledger append-only de auditoria imutável
│   ├── dicionario_de_dados_banco.md                   # Dicionário formal dos campos e tabelas
│   ├── os_anomalias.csv                               # Anomalias detectadas pelo Isolation Forest
│   ├── anomalias_consolidadas_manutencao_e_combustivel.csv
│   ├── abastecimentos_kpis.json                       # KPIs de abastecimento
│   ├── abastecimentos_ml_analise.json                 # Resultados ML de abastecimentos
│   ├── backups_dr/                                    # Backups de recuperação de desastre
│   ├── nosql_store/                                   # Armazenamento NoSQL (Mongita)
│   └── object_store/                                  # Armazenamento de objetos binários
│
├── src/                                    # Código-fonte principal
│   ├── api/                                # API REST FastAPI (porta 8080)
│   │   ├── main.py                         # Instância FastAPI, middlewares, rotas e assets estáticos
│   │   ├── config.py                       # Configurações via Pydantic Settings V2 (.env)
│   │   ├── database.py                     # SQLAlchemy 2.0 Async + inicialização de banco e seed
│   │   ├── models.py                       # Modelos ORM: User, AuditLog, QueryRecord
│   │   ├── schemas.py                      # Schemas Pydantic V2 de entrada/saída
│   │   ├── security.py                     # JWT HS256, OAuth2, Argon2id, RBAC (RequireRole)
│   │   ├── middlewares.py                  # SecurityHeadersMiddleware, LimitUploadSizeMiddleware
│   │   └── routes/
│   │       ├── auth.py                     # Endpoints de autenticação (token, login, register, me)
│   │       └── assistant.py               # Endpoints do Copiloto de IA e pipeline analítico
│   ├── enterprise/                         # Camada de infraestrutura corporativa
│   │   ├── fleet_engine.py                 # Motor CRUD SQLite WAL para gestão operacional
│   │   ├── iam.py                          # Identity & Access Management
│   │   ├── audit_trail.py                  # Trilha de auditoria imutável
│   │   ├── compliance.py                   # Conformidade LGPD / ISO 27001 / ISO 25010
│   │   ├── gateway.py                      # API Gateway
│   │   ├── reporting_bi.py                 # Business Intelligence e relatórios analíticos
│   │   ├── observability.py                # Observabilidade, métricas e monitoramento
│   │   ├── messaging.py                    # Mensageria assíncrona
│   │   ├── storage.py                      # Abstração de armazenamento (local/object store)
│   │   └── i18n.py                         # Internacionalização (PT-BR / EN)
│   ├── ai_assistant.py                     # Motor do Copiloto de IA (FleetAIAssistant)
│   ├── anonimizacao_lgpd.py               # Anonimização de PII via Microsoft Presidio
│   ├── indicadores_gfi.py                  # Indicadores GFI (Gestão de Frotas e Indicadores)
│   └── analises_comerciais.py              # Análises comerciais (TCO, CPK, Pareto ABC, ROI)
│
├── dissertacao_frotas/                     # Pipeline científico da dissertação
│   ├── requirements.txt                    # Dependências específicas do pipeline científico
│   ├── main.py                             # Ponto de entrada alternativo do pipeline
│   └── src/
│       ├── 01_auditoria_dados.py           # Auditoria forense SHA-256 e validação de integridade
│       ├── 02_preprocessamento.py          # Saneamento, exclusões rastreáveis e feature engineering
│       ├── 03_analise_descritiva.py        # Estatística descritiva e testes não paramétricos
│       ├── 04_modelos_preditivos.py        # ML supervisionado com validação temporal Rolling-Origin
│       ├── 05_deteccao_anomalias.py        # Isolation Forest com estabilidade Jaccard
│       ├── 06_teoria_grafos.py             # Redes bipartidas e comunidades Louvain
│       ├── 07_explicabilidade_xai.py       # SHAP TreeExplainer + LIME + importância por permutação
│       ├── 08_otimizacao_milp.py           # MILP (PuLP + HiGHS) — 5 cenários orçamentários
│       └── 09_validacao_estatistica.py     # Wilcoxon + DeLong + Holm-Bonferroni
│
├── sistema_gestao_frotas/                  # Sistema operacional completo de gestão de frotas
│   ├── executar_sistema.py                 # Inicializador do sistema operacional
│   ├── simulador_e_teste_completo_frota.py # Simulador end-to-end com 20 testes de integração
│   ├── testar_sistema.py                   # Suite de testes unitários (15 testes)
│   ├── iniciar_linux.sh / iniciar_windows.bat
│   ├── backend/
│   │   └── app/
│   │       ├── main.py                     # FastAPI v2.0.0 com 10 routers e middlewares
│   │       ├── config.py                   # Configurações do sistema operacional
│   │       ├── database.py                 # Persistência via Mongita (MongoDB-compatible)
│   │       ├── seed_data.py                # Dados de demonstração para validação
│   │       ├── routes/                     # 10 routers: auth, assets, telemetry, maintenance,
│   │       │                               #   fuel, trip, compliance, report, ai, contract_sc
│   │       ├── services/                   # Camada de serviço por domínio funcional
│   │       └── models/schemas.py           # Schemas Pydantic dos domínios operacionais
│   └── frontend/
│       ├── index.html                      # SPA principal do sistema operacional
│       ├── js/ (api.js, app.js, map.js)    # Client da API, lógica e geolocalização
│       └── css/                            # Estilos da interface
│
├── public-fleet-prescriptive-analytics/   # Sub-repositório git público e replicável
│   ├── src/
│   │   ├── anomaly/                        # Módulo de detecção de anomalias (Isolation Forest)
│   │   ├── explainability/                 # XAI (SHAP + LIME)
│   │   ├── graphs/                         # Teoria dos grafos (NetworkX + Louvain)
│   │   ├── optimization/                   # Otimização MILP (PuLP + HiGHS)
│   │   ├── predictive/                     # Modelos preditivos supervisionados
│   │   └── preprocessing/                  # Pré-processamento e feature engineering
│   ├── scripts/                            # Scripts 01–11 numerados e executáveis
│   ├── config/                             # Configurações YAML do pipeline
│   ├── requirements.txt                    # Dependências completas do sub-repositório
│   ├── environment.yml                     # Ambiente Conda
│   ├── CITATION.cff                        # Metadados de citação científica
│   └── executar_tudo.py / .sh / .bat / .ps1
│
├── scripts/                                # Scripts auxiliares (40+ arquivos)
│   ├── pipeline_metodologico_estatistico.py  # Pipeline estatístico completo
│   ├── compilar_dissertacao_mestrado_completa.py
│   ├── compilar_artigos_internacionais_pdf.py
│   ├── gerar_relatorio_auditoria_pdf.py
│   ├── gerar_relatorio_abastecimentos_pdf.py
│   ├── auditoria_seguranca_devsecops.py
│   ├── criar_tabela_veiculos_consolidada.py
│   ├── gerar_dicionario_dados.py
│   ├── processar_abastecimentos.py
│   └── ...
│
├── charts/                                 # 36+ gráficos científicos (PNG, 300 DPI)
├── dashboard/                              # Dashboard web estático (HTML/CSS/JS)
├── relatorios/                             # Relatórios Markdown e JSON
├── relatorios_pdf/                         # PDFs gerados (dissertação, artigos, auditoria)
├── docs/                                   # Documentação complementar
├── tests/                                  # Testes pytest do módulo enterprise
│   └── test_enterprise_platform.py
├── resultados/                             # Outputs analíticos dos scripts
├── resultados_modelagem/                   # Outputs dos modelos ML e MILP
└── versao_final_congelada/                 # Snapshot imutável da versão final da dissertação
```

---

## 🏗️ Arquitetura do Sistema

O sistema é composto por **quatro camadas arquiteturais** independentes que compartilham a mesma base de dados e infraestrutura:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                   CAMADA 1 — PIPELINE CIENTÍFICO                             │
│         dissertacao_frotas/src/01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09  │
│   CSV Brutos → Auditoria → ML → Anomalias → Grafos → MILP → XAI → Validação │
│                              ↓ gera                                          │
│           Parquet · SQLite · CSVs · JSONs · Figuras PNG 300 DPI              │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │ lê resultados
┌──────────────────────────────────▼───────────────────────────────────────────┐
│               CAMADA 2 — API FASTAPI DE PESQUISA (src/api/)                  │
│     OAuth2/JWT · RBAC · Copiloto IA · Dashboard Estático · Porta 8080        │
│       GET /api/status  POST /api/chat  POST /api/atualizar-graficos          │
│       POST /api/gerar-relatorio  GET /api/relatorio/download                │
│       POST /api/auth/token  POST /api/auth/login  GET /api/auth/me          │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │ compartilha dados
┌──────────────────────────────────▼───────────────────────────────────────────┐
│         CAMADA 3 — SISTEMA OPERACIONAL DE FROTAS (sistema_gestao_frotas/)    │
│     10 Routers FastAPI · MongoDB-compatible · Frontend HTML/JS · Porta 8000  │
│   /api/assets  /api/maintenance  /api/fuel  /api/telemetry  /api/compliance  │
│   /api/trip  /api/report  /api/ai  /api/contract_sc  /api/auth               │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │ serviços transversais
┌──────────────────────────────────▼───────────────────────────────────────────┐
│              CAMADA 4 — MÓDULO ENTERPRISE (src/enterprise/)                  │
│   FleetEngine · IAM · AuditTrail · Compliance · Gateway · BI · Observability │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Módulos e Componentes Detalhados

### Camada 1 — Pipeline Científico (`dissertacao_frotas/src/`)

Cada script é **autossuficiente**, **idempotente** e produz artefatos rastreáveis em `dados/` e `charts/`.

| Script | Descrição | Principais Saídas |
|:---|:---|:---|
| `01_auditoria_dados.py` | Verificação de integridade SHA-256 da base bruta, diagnóstico de 6.841 regressões de hodômetro, estatísticas de completude e geração de relatório forense | `dados/os_dataset_limpo.csv`, relatório de auditoria |
| `02_preprocessamento.py` | Saneamento de valores nulos, outliers e inconsistências semânticas; construção do painel veículo-mês (51.244 instâncias); feature engineering (hodômetro acumulado, razão peça/MO, etc.) | `dados/os_dataset_limpo.csv` enriquecido, Parquet intermediários |
| `03_analise_descritiva.py` | Estatística descritiva completa, testes de normalidade (Shapiro-Wilk / Lilliefors), diagnóstico de não-gaussianidade e fundação para modelos não-lineares | Figuras `fig01–fig04`, tabelas de distribuição |
| `04_modelos_preditivos.py` | Validação temporal Rolling-Origin; Classificação de Risco (HistGB, RF, ET, DT, LR) com PR-AUC / ROC-AUC / Brier / ECE; Regressão de Custo não-linear com MAE / RMSE / R²; Estudo de ablação M vs M+P | Modelos serializados, tabelas comparativas, Figuras `fig07–fig12` |
| `05_deteccao_anomalias.py` | Isolation Forest calibrado com 3 sementes; Índice de Jaccard por taxa de contaminação (1%–10%); teste t de concordância com reprovações reais | `dados/os_anomalias.csv`, Figuras `fig05–fig06`, `fig21` |
| `06_teoria_grafos.py` | Rede bipartida veículos ↔ oficinas (NetworkX); algoritmo de Louvain para detecção de comunidades (Q=0,5646, 18 comunidades); centralidade de grau e betweenness | Grafo serializado, `fig22` equivalente |
| `07_explicabilidade_xai.py` | SHAP TreeExplainer (valores globais e locais); LIME (explicações por perturbação local); importância por permutação em classificação e regressão | Figuras `fig13`, `fig31`, relatório XAI |
| `08_otimizacao_milp.py` | Formulação MILP via PuLP; solver HiGHS (Dual Simplex + B&B); 5 cenários orçamentários (50%–150% do cenário base); preços-sombra e análise de sensibilidade | Figuras `fig14–fig15`, `fig32`, relatório prescritivo |
| `09_validacao_estatistica.py` | Teste de Wilcoxon por pares (HistGB vs outros modelos); correção de Holm-Bonferroni; teste DeLong para comparação de AUCs; significância estatística a 5% | Tabela de p-valores ajustados, relatório de hipóteses |

---

### Camada 2 — API FastAPI de Pesquisa (`src/api/`)

**Porta padrão:** `8080`  
**Framework:** FastAPI 0.100+ com Pydantic V2 e SQLAlchemy 2.0 Async  
**Banco de dados:** SQLite assíncrono (`dados/sistema_seguro.db`)

#### Endpoints Disponíveis

**Autenticação** (`/api/auth/`)

| Método | Rota | Autenticação | Papel Mínimo | Descrição |
|:---:|:---|:---:|:---:|:---|
| `POST` | `/api/auth/token` | ❌ Público | — | OAuth2 Password Flow — retorna JWT |
| `POST` | `/api/auth/login` | ❌ Público | — | Login via JSON estrito (Pydantic V2) |
| `POST` | `/api/auth/register` | ✅ Bearer | `admin` | Cadastra novo usuário |
| `GET` | `/api/auth/me` | ✅ Bearer | qualquer | Retorna dados do usuário autenticado |

**Copiloto e Análises** (`/api/`)

| Método | Rota | Autenticação | Papel Mínimo | Descrição |
|:---:|:---|:---:|:---:|:---|
| `GET` | `/api/status` | ❌ Público | — | Status operacional da API e do motor de IA |
| `POST` | `/api/chat` | ❌ Público | — | Consulta em linguagem natural ao Copiloto de IA |
| `POST` | `/api/atualizar-graficos` | ✅ Bearer | `pesquisador` | Recalcula pipeline estatístico com parâmetros customizados |
| `POST` | `/api/gerar-relatorio` | ✅ Bearer | `auditor` | Compila dissertação em PDF via WeasyPrint |
| `GET` | `/api/relatorio/download` | ❌ Público | — | Download do PDF compilado (proteção CWE-22) |
| `GET` | `/api/comercial/resumo` | ❌ Público | — | KPIs comerciais consolidados (TCO, ABC, ROI) |
| `GET` | `/api/comercial/detalhes` | ❌ Público | — | Payload completo das análises comerciais |

**Interfaces Web (StaticFiles)**

| URL | Conteúdo |
|:---|:---|
| `http://localhost:8080/dashboard/` | Dashboard interativo (HTML/CSS/JS) |
| `http://localhost:8080/charts/` | Galeria de 36+ figuras científicas |
| `http://localhost:8080/graficos/` | Figuras alternativas |
| `http://localhost:8080/relatorios_pdf/` | PDFs gerados |
| `http://localhost:8080/docs` | Swagger UI (OpenAPI 3.1) |
| `http://localhost:8080/redoc` | ReDoc (documentação alternativa) |

#### Modelos de Dados ORM

```python
# usuarios_seguros
User(id, username, email, hashed_password, role, is_active, created_at)
# role ∈ {"admin", "auditor", "pesquisador"}

# trilha_auditoria
AuditLog(id, username, action, details, ip_address, timestamp)

# historico_consultas_ia
QueryRecord(id, username, pergunta, categoria, sucesso, timestamp)
```

---

### Camada 3 — Sistema Operacional de Frotas (`sistema_gestao_frotas/`)

**Porta padrão:** `8000`  
**Framework:** FastAPI 2.0.0  
**Banco de dados:** Mongita (MongoDB-compatible, sem servidor externo)

#### Routers Disponíveis

| Router | Prefixo | Domínio Funcional |
|:---|:---|:---|
| `auth_router` | `/api/auth` | Autenticação e gestão de usuários do sistema operacional |
| `assets_router` | `/api/assets` | CRUD de ativos veiculares (patrimônio, ficha cadastral, ciclo de vida) |
| `telemetry_router` | `/api/telemetry` | Rastreamento GPS e telemetria IoT em tempo real |
| `maintenance_router` | `/api/maintenance` | Ordens de serviço (preventiva, corretiva, preditiva) |
| `fuel_router` | `/api/fuel` | Controle de abastecimentos e detecção de fraudes em cartão combustível |
| `trip_router` | `/api/trip` | Despacho de viagens, checklist pré/pós e diário de bordo |
| `compliance_router` | `/api/compliance` | Conformidade legal (Decreto Estadual nº 47.539/2018) |
| `report_router` | `/api/report` | Geração de relatórios gerenciais e executivos |
| `ai_router` | `/api/ai` | Analítica prescritiva e recomendações de manutenção com IA |
| `contract_sc_router` | `/api/contract_sc` | Contratos de manutenção do Estado de Santa Catarina |

#### Dashboards do Sistema Operacional

| URL | Painel |
|:---|:---|
| `http://localhost:8000/` | SPA principal do sistema de gestão |
| `http://localhost:8000/dashboard/` | Painel analítico de frotas |
| `http://localhost:8000/anomalias` | Painel executivo de triagem de anomalias |
| `http://localhost:8000/dashboard/abastecimentos` | Relatório interativo de combustíveis |
| `http://localhost:8000/simulador` | Ambiente de testes e simulação da frota |
| `http://localhost:8000/slides` | Apresentação SIC (slides HTML) |
| `http://localhost:8000/api/health` | Liveness/readiness check |
| `http://localhost:8000/api/docs` | Swagger UI do sistema operacional |

---

### Camada 4 — Módulo Enterprise (`src/enterprise/`)

Infraestrutura corporativa transversal, consumida tanto pela API FastAPI quanto pelo sistema operacional.

| Módulo | Classe / Função Principal | Responsabilidade |
|:---|:---|:---|
| `fleet_engine.py` | `FleetManagementEngine` | CRUD de veículos, motoristas, viagens, OS e abastecimentos via SQLite WAL |
| `iam.py` | `IdentityAccessManager` | Controle de acesso baseado em papéis (RBAC), sessões e permissões granulares |
| `audit_trail.py` | `AuditTrailManager` | Ledger JSONL append-only para rastreabilidade de todas as operações críticas |
| `compliance.py` | `ComplianceEngine` | Verificações LGPD (Lei 13.709/2018), ISO 27001 e ISO 25010 |
| `gateway.py` | `APIGateway` | Rate limiting, roteamento e interceptação de requisições |
| `reporting_bi.py` | `BIReportingEngine` | Geração de relatórios analíticos, KPIs e exportações Excel/PDF |
| `observability.py` | `ObservabilityModule` | Métricas de performance, alertas e monitoramento operacional |
| `messaging.py` | `MessagingBus` | Mensageria assíncrona entre módulos (evento/observador) |
| `storage.py` | `StorageAdapter` | Abstração de armazenamento (local, object store, NoSQL) |
| `i18n.py` | `I18nManager` | Internacionalização PT-BR / EN para textos e relatórios |

---

## 🔐 Segurança — Security-by-Design

O sistema implementa um modelo de segurança em profundidade com conformidade explícita a **OWASP Top 10** e **CWE**.

### Autenticação e Autorização

| Mecanismo | Implementação | Referência |
|:---|:---|:---|
| Hash de senhas | Argon2id (`argon2-cffi`: time_cost=3, memory_cost=64MB, parallelism=4) | OWASP A02 |
| Token de acesso | JWT HS256 com `exp`, `iat`, `nbf` e `sub` | OWASP A07 |
| Controle de acesso | RBAC com `RequireRole` injetável via `Depends()` | OWASP A01 |
| Fluxo OAuth2 | OAuth2 Password Bearer compatível com Swagger UI | RFC 6749 |
| Consultas SQL | SQLAlchemy 2.0 com bind parameters — nunca concatenação | CWE-89 |

### Papéis e Permissões (RBAC)

| Papel | Permissões |
|:---|:---|
| `admin` | Acesso total: criação de usuários, geração de relatórios, execução de pipelines, auditoria |
| `auditor` | Geração de relatórios PDF, leitura de trilhas de auditoria, consultas analíticas |
| `pesquisador` | Execução de pipelines, consultas ao Copiloto de IA, leitura de dados analíticos |

### Headers HTTP de Segurança (Middleware)

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; ...
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

### Outras Proteções

| Proteção | Implementação |
|:---|:---|
| Anti-DoS | Limite de payload HTTP: 1 MB (API pesquisa) / 10 MB (sistema operacional) |
| Path Traversal | Validação canônica de caminhos antes de servir arquivos (`CWE-22`) |
| Data Leakage | Exceptions globais não expõem stack traces ao cliente (`CWE-209`) |
| Imutabilidade dos dados brutos | Hash SHA-256 verificado no Script 01 antes de qualquer processamento |
| Ledger de auditoria | JSONL append-only em `dados/trilha_auditoria_ledger.jsonl` |
| Anonimização PII | Microsoft Presidio Analyzer + Anonymizer com modelos spaCy PT/EN |
| CORS | Lista explícita de origens — nunca wildcard `*` em produção (`CWE-942`) |

---

## 💾 Modelo de Dados

### Banco de Dados Analítico (`dados/resultados_dissertacao.db`)

Banco SQLite criado e gerenciado pelo `FleetManagementEngine` (modo WAL para alta concorrência).

| Tabela | Descrição |
|:---|:---|
| `motoristas_autorizados` | Cadastro de condutores: CNH, categoria, validade, pontos e vínculo institucional |
| `veiculos_frota` | Ficha patrimonial: placa, chassi, modelo, ano, hodômetro, status operacional |
| `viagens` | Diário de bordo: origem, destino, hodômetro inicial/final, motorista, veículo |
| `ordens_servico` | OS de manutenção: tipo (preventiva/corretiva/preditiva), peças, custos, oficina |
| `abastecimentos` | Registros de combustível: tanque, km/L, cartão, bandeira de fraude |

### Banco de Dados da API (`dados/sistema_seguro.db`)

| Tabela | Descrição |
|:---|:---|
| `usuarios_seguros` | Usuários do sistema: credenciais Argon2id, papel RBAC, status |
| `trilha_auditoria` | Log de ações sensíveis: login, criação de usuários, execução de pipelines |
| `historico_consultas_ia` | Registro de todas as consultas ao Copiloto de IA |

---

## 🧪 Testes

O projeto mantém duas suites de testes, configuradas em `pytest.ini`:

```ini
[pytest]
testpaths = tests public-fleet-prescriptive-analytics/tests
pythonpath = . public-fleet-prescriptive-analytics
```

### Execução

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Executar todos os testes (7 unitários + testes do sub-repositório)
pytest

# Execução com output detalhado
pytest -v

# Executar apenas testes enterprise
pytest tests/test_enterprise_platform.py -v

# Executar apenas testes do sub-repositório público
pytest public-fleet-prescriptive-analytics/tests/ -v
```

### Resultados Certificados (Homologação Cross-Platform)

| Suite | Testes | Status | Tempo |
|:---:|:---:|:---:|:---:|
| Enterprise Platform | 7/7 | ✅ PASSED | ~0,50s |
| Sub-repositório Público | Passados | ✅ PASSED | — |
| Sistema de Gestão de Frotas | 15 testes | ✅ PASSED | — |
| Simulador End-to-End | 20 testes | ✅ PASSED | — |

---

## 🚀 Guia de Instalação e Execução

### Pré-requisitos

- Python 3.10+ (homologado em 3.10, 3.11, 3.12, 3.14 no Linux; 3.15 no Windows 11)
- ~4 GB de espaço em disco (dados + modelos + PDFs)
- ~4 GB de RAM (pipeline ML com datasets completos)

### 1. Clonar e Configurar o Ambiente

```bash
# Clonar o repositório
git clone <url-do-repositório>
cd "Geral_de_OS_23439885_202609110934 (1)"

# Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instalar dependências (camada de ciência de dados)
pip install -r requirements.txt

# Instalar dependências completas (pipeline científico + API + sistema operacional)
pip install -r dissertacao_frotas/requirements.txt
pip install -r public-fleet-prescriptive-analytics/requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env com sua SECRET_KEY (mínimo 32 caracteres)
# Nunca use a chave padrão em produção
nano .env
```

Variáveis obrigatórias:

| Variável | Valor Padrão | Descrição |
|:---|:---|:---|
| `SECRET_KEY` | *(obrigatório)* | Chave HMAC-SHA256 ≥ 32 chars de alta entropia |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Tempo de vida do token JWT |
| `DATABASE_URL` | `sqlite+aiosqlite:///./dados/sistema_seguro.db` | String de conexão assíncrona |
| `ALLOWED_ORIGINS` | `["http://localhost:8080"]` | Lista de origens CORS permitidas |
| `ENVIRONMENT` | `production` | Ambiente de execução |
| `ADMIN_DEFAULT_USERNAME` | `admin_seguro` | Username do admin inicial |
| `ADMIN_DEFAULT_EMAIL` | `admin@udesc.br` | E-mail do admin inicial |
| `ADMIN_DEFAULT_PASSWORD` | *(ver .env)* | Senha do admin (Argon2id) |

### 3. Executar o Pipeline Científico Completo

```bash
# Pipeline de ponta a ponta (20+ etapas: ~15–30 min com dataset completo)
python3 executar_todos_os_scripts.py

# Ou individualmente (recomendado para depuração)
python3 dissertacao_frotas/src/01_auditoria_dados.py
python3 dissertacao_frotas/src/02_preprocessamento.py
# ... e assim por diante
```

### 4. Iniciar a API FastAPI (Pesquisa + Dashboard)

```bash
# Servidor FastAPI hardened (porta 8080)
python3 run_fastapi.py

# Acessar no navegador:
# Dashboard:   http://localhost:8080/dashboard/
# Swagger UI:  http://localhost:8080/docs
# ReDoc:       http://localhost:8080/redoc
# Status:      http://localhost:8080/api/status
```

### 5. Iniciar o Sistema Operacional de Gestão de Frotas

```bash
# A partir da raiz do repositório
python3 sistema_gestao_frotas/executar_sistema.py

# Ou diretamente pelo shell script:
cd sistema_gestao_frotas && ./iniciar_linux.sh

# Acessar no navegador:
# Sistema:     http://localhost:8000/
# Dashboard:   http://localhost:8000/dashboard/
# Swagger UI:  http://localhost:8000/api/docs
# Health:      http://localhost:8000/api/health
```

### 6. Iniciar o Copiloto de IA via CLI

```bash
# Modo interativo
./assistente_ia.sh

# Consulta única
./assistente_ia.sh "Qual foi o modelo campeão de classificação?"
python3 scripts/assistente_ia_prompt.py
```

### 7. Abrir o Aplicativo Desktop (PyQt6)

```bash
./iniciar_gui.sh
```

### 8. Executar o Sub-repositório Público Standalone

```bash
cd public-fleet-prescriptive-analytics

# Linux/macOS
./executar_tudo.sh

# Windows
executar_tudo.bat
# ou
python executar_tudo.py
```

---

## 📦 Dependências por Camada

### Dependências Científicas (`dissertacao_frotas/requirements.txt`)

| Pacote | Versão Mín. | Uso |
|:---|:---:|:---|
| `pandas` | 2.2.0 | Manipulação de dados e painel veículo-mês |
| `numpy` | 1.26.0 | Computação numérica vetorizada |
| `scikit-learn` | 1.4.0 | Modelos ML, métricas, Rolling-Origin CV, Isolation Forest |
| `scipy` | 1.12.0 | Testes estatísticos (Wilcoxon, Mann-Whitney, Kruskal-Wallis) |
| `pulp` | 2.8.0 | Formulação de problemas MILP |
| `highspy` | 1.7.0 | Solver HiGHS (Dual Simplex + Branch-and-Bound) |
| `shap` | 0.45.0 | TreeExplainer para SHAP values (XAI) |
| `lime` | 0.2.0 | Explicações locais por perturbação (XAI) |
| `networkx` | 3.2.0 | Redes bipartidas e algoritmo de Louvain |
| `matplotlib` | 3.8.0 | 36 figuras científicas a 300 DPI |
| `seaborn` | 0.13.0 | Visualizações estatísticas |
| `statsmodels` | 0.14.0 | ARIMA, ETS, teste ADF |
| `pyarrow` | 15.0.0 | Armazenamento colunar Parquet |
| `pytest` | 8.0.0 | Testes unitários e de integração |

### Dependências da API FastAPI (`src/api/` — inferidas do código)

| Pacote | Uso |
|:---|:---|
| `fastapi` | Framework web assíncrono |
| `uvicorn` | Servidor ASGI de produção |
| `sqlalchemy[asyncio]` ≥ 2.0 | ORM assíncrono |
| `aiosqlite` | Driver SQLite assíncrono |
| `pydantic-settings` ≥ 2 | Gerenciamento de configurações via `.env` |
| `python-jose[cryptography]` | Codificação/decodificação JWT |
| `argon2-cffi` | Hash Argon2id para senhas |
| `passlib` | Fallback de verificação de senhas |

### Dependências de Conformidade LGPD (`requirements.txt` raiz)

| Pacote | Versão Mín. | Uso |
|:---|:---:|:---|
| `presidio-analyzer` | 2.2.364 | Detecção de PII (CPF, nome, e-mail, placa) |
| `presidio-anonymizer` | 2.2.364 | Substituição de PII por tokens anônimos |
| `faker` | 40.43.0 | Geração de dados sintéticos para testes |
| `spacy` | 3.8.16 | Modelos NLP para reconhecimento de entidades |
| `cryptography` | 48.0.1 | Criptografia geral (chaves, assinaturas) |
| `weasyprint` | 70.0 | Geração de PDFs acadêmicos a 300 DPI |

---

## 📊 Artefatos Gerados pelo Sistema

Após a execução completa do pipeline, os seguintes artefatos são produzidos:

### Modelos e Dados Analíticos

| Artefato | Localização | Descrição |
|:---|:---|:---|
| Dataset saneado | `dados/os_dataset_limpo.csv` | 350.737 OS após auditoria e saneamento |
| Painel veículo-mês | `dados/` (Parquet) | 51.244 instâncias para modelagem preditiva |
| Anomalias OS | `dados/os_anomalias.csv` | Ordens sinalizadas pelo Isolation Forest |
| Anomalias consolidadas | `dados/anomalias_consolidadas_manutencao_e_combustivel.csv` | Manutenção + abastecimentos |
| Banco analítico | `dados/resultados_dissertacao.db` | Todos os resultados em SQLite |
| Ledger de auditoria | `dados/trilha_auditoria_ledger.jsonl` | Registro imutável de operações |

### Figuras Científicas (`charts/`, 300 DPI)

| Intervalo | Conteúdo |
|:---|:---|
| `fig01–fig04` | Auditoria e análise descritiva |
| `fig05–fig06` | Estabilidade do Isolation Forest e validação cruzada |
| `fig07–fig12` | Modelos preditivos (classificação e regressão) e ablação |
| `fig13–fig15` | XAI, sensibilidade MILP e fronteira eficiente |
| `fig16–fig20` | Distribuições, correlações e séries temporais Prophet |
| `fig21–fig32` | Anomalias, composição de custos, Pareto, sazonalidade e diagnósticos |
| `fig76–fig79` | Pipeline estatístico: normalidade, hipóteses, Poisson/Markov, ETS vs ARIMA |

### Documentos PDF (`relatorios_pdf/`)

| Documento | Descrição |
|:---|:---|
| `relatorio_dissertacao_completo.pdf` | Dissertação completa com figuras inline |
| `relatorio_gerencial_frotas.pdf` | Relatório executivo de gestão |
| `relatorio_auditoria.pdf` | Laudo forense de auditoria científica |
| `relatorio_seguranca_normas.pdf` | Conformidade DevSecOps / OWASP / ISO |
| `artigos_internacionais.pdf` | 4 artigos Qualis A1 (PT e EN) |
| `relatorio_anomalias_detalhado.pdf` | Anomalias por secretaria estadual |
| `dicionario_dados.pdf` | Dicionário de dados do banco |
| `relatorio_abastecimentos.pdf` | Análise de combustíveis e fraudes |

---

## 🔄 Fluxo de Dados End-to-End

```
[Dados Brutos]
     │
     ▼
dados/Geral_de_OS_*.csv  +  dados/Cruzamento_Patrimonio*.csv
     │
     ▼  Script 01 (SHA-256 + Diagnóstico)
[Base Auditada]  →  dados/os_dataset_limpo.csv
     │
     ▼  Script 02 (Saneamento + Feature Engineering)
[Painel Veículo-Mês 51.244 instâncias]
     │
     ├──▶ Script 03  →  Estatística Descritiva + Normalidade  →  charts/fig01-04, fig76
     │
     ├──▶ Script 04  →  ML Supervisionado (Rolling-Origin)    →  charts/fig07-12
     │                   HistGB PR-AUC=0,9099 | MAE=R$2.311,82
     │
     ├──▶ Script 05  →  Isolation Forest (Jaccard=0,8811)     →  dados/os_anomalias.csv
     │
     ├──▶ Script 06  →  Redes Bipartidas (Louvain Q=0,5646)   →  charts/fig22
     │
     ├──▶ Script 07  →  XAI (SHAP + LIME + Permutação)        →  charts/fig13, fig31
     │
     ├──▶ Script 08  →  MILP (HiGHS) — Economia 17,51%        →  charts/fig14-15, fig32
     │
     └──▶ Script 09  →  Wilcoxon + Holm-Bonferroni            →  Tabela de p-valores
              │
              ▼
     [dados/resultados_dissertacao.db]
              │
              ├──▶ API FastAPI (porta 8080)   →  /dashboard/  /api/chat  /docs
              │
              └──▶ Sistema Operacional (8000) →  /  /api/assets  /api/maintenance
```

---

## 📖 Convenções de Código

- **Estilo:** PEP 8 com docstrings em português (contexto acadêmico)
- **Tipagem:** Anotações de tipo completas em toda a API FastAPI e módulos enterprise
- **Comentários de Segurança:** Referências explícitas a CWE e OWASP em código sensível
- **Nomes de Variáveis:** Snake_case; nomes descritivos em português para variáveis de domínio
- **Idempotência:** Todo script do pipeline pode ser reexecutado sem efeitos colaterais destrutivos
- **Rastreabilidade:** Toda exclusão de registro gera entrada explicativa no log de auditoria
- **Sem Hardcode de Segredos:** Todos os segredos são carregados via `.env` por `pydantic-settings`

---

## 🗺️ Roteiro de Execução Recomendado

Para reproduzir os resultados da dissertação do zero:

```
1. Instalar dependências              →  pip install -r requirements.txt (+ dissertacao_frotas/)
2. Configurar .env                    →  cp .env.example .env && editar SECRET_KEY
3. Script 01 — Auditoria              →  python3 dissertacao_frotas/src/01_auditoria_dados.py
4. Script 02 — Pré-processamento      →  python3 dissertacao_frotas/src/02_preprocessamento.py
5. Script 03 — Análise Descritiva     →  python3 dissertacao_frotas/src/03_analise_descritiva.py
6. Script 04 — Modelos Preditivos     →  python3 dissertacao_frotas/src/04_modelos_preditivos.py
7. Script 05 — Anomalias              →  python3 dissertacao_frotas/src/05_deteccao_anomalias.py
8. Script 06 — Grafos                 →  python3 dissertacao_frotas/src/06_teoria_grafos.py
9. Script 07 — XAI                    →  python3 dissertacao_frotas/src/07_explicabilidade_xai.py
10. Script 08 — MILP                  →  python3 dissertacao_frotas/src/08_otimizacao_milp.py
11. Script 09 — Validação Estatística →  python3 dissertacao_frotas/src/09_validacao_estatistica.py
12. Pipeline Estatístico              →  python3 scripts/pipeline_metodologico_estatistico.py
13. Testes                            →  pytest -v
14. API FastAPI                       →  python3 run_fastapi.py
```

Ou simplesmente:
```bash
python3 executar_todos_os_scripts.py
```

---

## 📬 Citação

Se este repositório foi útil para sua pesquisa, por favor cite:

```bibtex
@mastersthesis{jonker2026prescritiva,
  author  = {Eduardo Lopes Jonker},
  title   = {Analítica Prescritiva e Inteligência Artificial Explicável
             para a Gestão de Frota Veicular no Setor Público},
  school  = {Universidade do Estado de Santa Catarina (UDESC) —
             Programa de Pós-Graduação em Computação Aplicada (PPGCAP/CCT)},
  year    = {2026},
  address = {Florianópolis, SC, Brasil},
  note    = {Repositório público: public-fleet-prescriptive-analytics}
}
```

---

*Documentação técnica gerada automaticamente a partir da análise do código-fonte. Última atualização: novembro de 2026.*

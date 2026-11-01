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
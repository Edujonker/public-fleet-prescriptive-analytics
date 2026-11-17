# Pré-registro: estudo de robustez com 100 repetições

**Autor:** Eduardo Lopes Jonker · **Programa:** PPGCAP/UDESC
**Data do registro:** 16/11/2026 08:10, antes de qualquer execução do estudo.
**Script:** `scripts/estudo_robustez_100.py` · **Saídas:** `resultados_robustez_100/`

## Objetivo

Medir se as decisões de H1–H4, tomadas numa execução única do protocolo (sementes fixas), se mantêm quando os dados de treino, as sementes dos modelos e a instância do MILP variam. Este estudo é uma **análise de sensibilidade**. Ele não substitui o protocolo nem muda o enunciado ou o critério de nenhuma hipótese.

## O que não muda

- Enunciados de H1–H4 e P1, critérios do anteprojeto e limiares da qualificação (`docs/hipoteses/desvios_do_protocolo.md`).
- Decisões oficiais: as da etapa 09 (`certificado_reprodutibilidade_cientifica.json`).
- Corte temporal: treino até 2024-12, teste a partir de 2025-01. O conjunto de teste é o mesmo em todas as repetições.

## Repetições

- r = 1, …, 100; semente da repetição s_r = 1000 + r.
- Em cada repetição, o treino é uma **amostra bootstrap** do conjunto de treino (mesmo tamanho, com reposição, semente s_r). Os modelos usam `random_state = s_r` e os mesmos hiperparâmetros da etapa 04.

## Medidas por repetição

1. **Matriz de desempenho.** Classificadores (HistGradientBoosting, RandomForest, ExtraTrees, DecisionTree, LogisticRegression): ROC-AUC, PR-AUC, F1, acurácia, acurácia balanceada, precisão e sensibilidade com limiar 0,5, Brier e ECE (10 faixas, mesma função da etapa 04). Regressores (HistGradientBoosting, RandomForest, ExtraTrees, DecisionTree e mediana do treino): MAE, RMSE e R².
2. **H1.** HistGradientBoosting com atributos M e com M+P na mesma amostra bootstrap. Δ ROC-AUC = M+P − M; ganho no MAE = (MAE_M − MAE_M+P) / MAE_M.
3. **H2.** Subamostra de 12.000 linhas do treino (semente s_r), como na etapa 04c. SVR-RBF e SVC-RBF contra HistGradientBoosting, RandomForest e ExtraTrees. Diferença relativa do MAE e diferença de ROC-AUC.
4. **H3.** Instância S0 gerada com a semente s_r (sorteio dos 2.000 veículos e fatores aleatórios), mesmas fórmulas e limites da etapa 08. Custos do MILP, da prática reconstruída (BL0) e da heurística gulosa.
5. **H4.** HistGradientBoosting treinado na amostra bootstrap r; 25 instâncias de maior risco no teste; SHAP (TreeExplainer) e LIME (semente s_r). Spearman médio e Jaccard médio do top-5 entre SHAP e LIME; R² médio do modelo local do LIME (F2); erro aditivo máximo do SHAP (F1). As medidas de estabilidade E1 e E2 não são repetidas, porque já são medidas entre sementes.

## Critérios sob reamostragem (fixados agora)

P2,5 e P97,5 são os percentis das 100 repetições.

| Hipótese | Critério do anteprojeto sob reamostragem | Limiar da qualificação sob reamostragem |
|---|---|---|
| H1 | P2,5 de Δ ROC-AUC > 0 **ou** P2,5 do ganho no MAE > 0 | mediana do ganho no MAE ≥ 15% |
| H2 | algum ensemble com P97,5 da diferença relativa do MAE ≤ +5% **e** P2,5 da diferença de AUC ≥ −0,02 | — |
| H3 | MILP < BL0 e MILP < heurística em ≥ 95 das 100 repetições | P2,5 da economia sobre BL0 > 10% |
| H4 | P2,5 do R² do LIME ≥ 0,50 e erro aditivo do SHAP ≤ 0,001 em todas as repetições | P2,5 do Spearman > 0,85 e P2,5 do Jaccard > 0,85 |

**Robustez da decisão oficial.** Para cada critério, conta-se em quantas repetições o resultado (atende / não atende), calculado só com aquela repetição, coincide com o da decisão oficial. A decisão é **robusta** se coincidir em ≥ 95 das 100 repetições e **instável** caso contrário.

## Como o resultado será usado

- Decisão oficial robusta: registrada como reforço da evidência.
- Decisão oficial instável ou divergente do critério sob reamostragem: registrada como ressalva na matriz de hipóteses e em `desvios_do_protocolo.md`. A decisão oficial **não** é trocada.
- Nenhuma hipótese nova é criada a partir destes resultados. Ideias novas vão para o pré-registro exploratório e só são testadas na extração de 2026 da SEA/SC.

## Integridade

O hash SHA-256 deste arquivo fica em `docs/hipoteses/preregistro_estudo_100_repeticoes.sha256`, gerado antes da primeira execução.

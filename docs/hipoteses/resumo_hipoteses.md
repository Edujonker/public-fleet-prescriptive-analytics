# Resultado das hipóteses

_Gerado por `scripts/gerar_blocos_hipoteses.py`; regra de decisão e desvios em `docs/hipoteses/desvios_do_protocolo.md`._

|  | Hipótese | Critério do anteprojeto | Atende | Limiar pré-registrado | Atende | Decisão |
|---|---|---|---|---|---|---|
| P1 | Não normalidade dos custos | — | — | KS p < 0,05 e assimetria em módulo > 1 | sim | SUSTENTADA |
| H1 | Fusão de manutenção e patrimônio (M+P) | M+P melhora ao menos uma métrica principal (IC95 exclui zero) | sim | ganho no MAE >= 15% | não | PARCIALMENTE SUSTENTADA |
| H2 | Ensembles competitivos frente a SVR-RBF | algum ensemble não inferior ao SVR (margem 5% no MAE; −0,02 na AUC) nas duas tarefas | não | — | — | NÃO SUSTENTADA |
| H3 | Política MILP reduz o custo esperado | custo MILP < prática reconstruída e < heurística | sim | economia > 10% sobre a prática reconstruída | sim | SUSTENTADA |
| H4 | Explicações SHAP e LIME fiéis e estáveis | fidelidade e estabilidade suficientes (F1, F2, E1, E2) | não | concordância SHAP×LIME > 0,85 | não | NÃO SUSTENTADA |

- P1 (não normalidade dos custos) foi sustentada: KS = 0,2905 (p < 1e-15); assimetria 9,83; curtose 228,75.
- H1 foi parcialmente sustentada: incluir o patrimônio melhora a ROC-AUC em +0,0095 (IC 95% 0,0045 a 0,0146), mas reduz o MAE em apenas 0,62% (IC 95% -0,26% a 1,52%), abaixo da meta de 15%.
- H2 não foi sustentada: os ensembles superam o SVC-RBF na classificação (AUC +0,0463), mas erram 8,65% a mais que o SVR-RBF na regressão de custos (IC 95% 6,83% a 10,52%).
- H3 foi sustentada no cenário S0: a política MILP custa R$ 44.190.120,51, 13,66% (R$ 6,99 mi) menos que a prática reconstruída (R$ 51.180.733,62); a heurística gulosa chega praticamente ao mesmo custo (diferença de R$ 764,29), e a instância é semissintética.
- H4 não foi sustentada: o SHAP é exato e estável (estabilidade 0,979), mas o LIME é pouco fiel ao modelo (R² local 0,243) e a concordância SHAP × LIME fica em Spearman 0,2869 e Jaccard 45,48%, abaixo de 0,85.

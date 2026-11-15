# Desvios do protocolo e correções de execução

**Registro:** 15/11/2026 · **Autor:** Eduardo Lopes Jonker

Este documento lista o que mudou entre o planejado (anteprojeto e qualificação) e o executado, e por quê. Os resultados vêm de `dissertacao_frotas/resultados/logs/certificado_reprodutibilidade_cientifica.json`.

## 1. Regra de decisão das hipóteses

- **Planejado:** H1 a H4 descritas no anteprojeto e limiares numéricos na qualificação (H1 ≥ 15% no MAE; H3 > 10% de economia; H4 > 0,85 de concordância SHAP × LIME).
- **Executado:** cada hipótese é avaliada pelos dois critérios.
  - **SUSTENTADA:** atende os dois.
  - **PARCIALMENTE SUSTENTADA:** atende um.
  - **NÃO SUSTENTADA:** não atende nenhum.
- **Operacionalização:** o texto do anteprojeto foi transformado em teste nos scripts 04b, 04c, 07b e 08. O critério foi gravado no código antes da primeira execução de cada um.
- **Motivo:** o anteprojeto não traz limiares numéricos, e o código anterior usava só os limiares. Com isso, H2 era testada contra a regressão logística, e não contra o SVR-RBF previsto.

## 2. Testes que faltavam

| Hipótese | Previsto no anteprojeto | Situação anterior | Correção |
|---|---|---|---|
| H1 | M+P+A (manutenção, patrimônio, abastecimento) | ganho de +0,41% digitado, sem código que o gerasse | etapa 04b calcula MAE e ROC-AUC com IC 95%. O abastecimento não pôde ser testado: a base cobre jan/2019–fev/2022 e não se sobrepõe ao teste (2025–2026) |
| H2 | ensembles frente a SVR-RBF | comparação com regressão logística e mediana | etapa 04c compara com SVR-RBF e SVC-RBF, não inferioridade com margem de 5% no MAE e −0,02 na AUC |
| H3 | frente à prática reconstruída e a heurísticas | custos substituídos por constantes no script 08 | custos calculados pelo HiGHS; linha de base = só manutenções obrigatórias; heurística gulosa benefício/custo |
| H4 | fidelidade e estabilidade | apenas concordância SHAP × LIME | etapa 07b mede fidelidade do SHAP (aditividade) e do LIME (R² local), estabilidade do LIME entre sementes e do SHAP entre modelos |

## 3. Erros corrigidos que afetaram resultados

1. **Patrimônio:** a etapa 02 lia "R$ 48,010.00" como R$ 48,01. Os valores patrimoniais do painel estavam cerca de mil vezes menores.
2. **XAI:** a figura local "SHAP × LIME" desenhava valores SHAP multiplicados por um fator aleatório (`lime_mock`). Além disso, o JSON da etapa 07 declarava H4 sustentada com limiares de 0,70 e 0,60, diferentes do pré-registrado (0,85).
3. **Etapa 09:**
   - lia uma chave inexistente e usava valores digitados (ROC da regressão logística de 0,7366; o real é 0,8292);
   - tinha os textos de H1 e H2 escritos à mão;
   - lia uma cópia antiga do resultado do MILP.
4. **Subamostras:** as do Passing-Bablok e do gráfico de dispersão não tinham semente fixa.

## 4. Efeito nas conclusões

| | Antes | Agora |
|---|---|---|
| H1 | não sustentada (+0,41%) | **parcialmente sustentada**: ROC-AUC melhora com IC que exclui zero; MAE +0,62% (IC inclui zero), abaixo de 15% |
| H2 | parcialmente sustentada | **não sustentada**: competitiva só na classificação; na regressão o SVR-RBF erra 8,65% menos |
| H3 | sustentada (17,51%; R$ 9,30 mi) | **sustentada**: 13,66% (R$ 6,99 mi) sobre a prática reconstruída, em instância semissintética. Ressalva: a heurística gulosa chega ao mesmo custo (diferença de R$ 764) |
| H4 | não sustentada (Jaccard 39,29%) | **não sustentada**: SHAP fiel e estável, LIME estável mas pouco fiel (R² 0,24); concordância Spearman 0,287, Jaccard 45,5% |

## 5. Pendências

- **Comparação com a regressão logística:** usa erro-padrão constante, não o teste de DeLong exato. Hoje é descritiva.
- **Teste KS de P1:** usa as 5.000 primeiras OS do arquivo, não uma amostra aleatória.
- **MILP:** a instância é semissintética, com custos e probabilidades de falha gerados por fórmula. A economia é um contrafactual simulado.
- **Revisão sistemática:** a triagem é automática e precisa da validação humana dos 274 estudos.

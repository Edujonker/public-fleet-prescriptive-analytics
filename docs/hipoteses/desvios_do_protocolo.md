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
5. **Etapa 07, instâncias de H4 (corrigido em 16/11/2026):** a comparação SHAP × LIME usava `np.argsort(prob)[-50:][:25]`, isto é, as instâncias da 26ª à 50ª de maior risco, e não as 25 de maior risco previstas no protocolo e usadas na etapa 07b.
6. **Etapa 07, pesos do LIME (corrigido em 16/11/2026):** os pesos eram associados aos atributos procurando o nome do atributo dentro do texto da regra do LIME (`if f in k`). Nomes contidos em outros (por exemplo `custo_mes` dentro de regras de outros atributos de custo) podiam receber o peso errado. Agora o peso vem do índice do atributo (`as_map`), como na etapa 07b. Com as correções 5 e 6, a concordância passou de Spearman 0,287 e Jaccard 45,5% para **Spearman 0,448 e Jaccard 42,9%**. Os dois continuam abaixo de 0,85; a decisão de H4 não muda.
7. **Etapa 08, limite de tempo do solver (corrigido em 16/11/2026):** cada um dos 36 problemas mensais tinha limite de 2 s (`time_limit`). Com a máquina ocupada, o limite podia interromper o HiGHS antes da otimalidade, e o custo variava entre execuções (R$ 44.190.100,47 contra R$ 44.190.036,47 numa repetição de controle). O limite foi retirado; a tolerância `mip_rel_gap = 0,0001` foi mantida. Sem o limite, duas execuções deram o mesmo custo (R$ 44.190.036,47) em cerca de 7,5 s. O valor oficial não muda.
8. **Valores de reserva nas etapas 07 e 09 (corrigido em 16/11/2026):** se um JSON faltasse, as etapas usavam números digitados (Spearman 0,884; Jaccard 0,800; economia 17,51%; R$ 9.302.147,26; gap 0,0000057; Spearman 0,3680; Jaccard 0,3929). Agora a falta de dado interrompe a etapa. Nas execuções registradas os JSON existiam, então os resultados não foram afetados.

## 4. Efeito nas conclusões

| | Antes | Agora |
|---|---|---|
| H1 | não sustentada (+0,41%) | **parcialmente sustentada**: ROC-AUC melhora com IC que exclui zero; MAE +0,62% (IC inclui zero), abaixo de 15% |
| H2 | parcialmente sustentada | **não sustentada**: competitiva só na classificação; na regressão o SVR-RBF erra 8,65% menos |
| H3 | sustentada (17,51%; R$ 9,30 mi) | **sustentada**: 13,66% (R$ 6,99 mi) sobre a prática reconstruída, em instância semissintética. Ressalva: a heurística gulosa chega ao mesmo custo (diferença de R$ 848,32) |
| H4 | não sustentada (Jaccard 39,29%) | **não sustentada**: SHAP fiel e estável, LIME estável mas pouco fiel (R² 0,24); concordância Spearman 0,448, Jaccard 42,9% (após as correções 5 e 6; antes 0,287 e 45,5%) |

## 5. Pendências

- **Comparação com a regressão logística:** usa erro-padrão constante, não o teste de DeLong exato. Hoje é descritiva.
- **Teste KS de P1:** usa as 5.000 primeiras OS do arquivo, não uma amostra aleatória.
- **MILP:** a instância é semissintética, com custos e probabilidades de falha gerados por fórmula. A economia é um contrafactual simulado.
- **Revisão sistemática:** a triagem é automática e precisa da validação humana dos 274 estudos.

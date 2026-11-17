# Aditivo 01 ao pré-registro do estudo de robustez

**Documento alterado:** `docs/hipoteses/preregistro_estudo_100_repeticoes.md` (SHA-256 53200664f899485b18c98249cc6750f677c92c52833923ab896697d9269987e0, que continua válido e não foi editado).
**Data do aditivo:** 16/11/2026, antes de qualquer repetição bootstrap.

## O que já tinha sido executado

Só a repetição de controle r = 0 das três partes. Ela é a configuração oficial (treino completo, semente 42) e serve para conferir se o estudo reproduz as etapas 04, 04b, 04c, 07b e 08. Nenhuma repetição r ≥ 1 foi executada, então a decisão deste aditivo não depende de resultados do estudo.

O controle encontrou três diferenças, que levaram a correções registradas em `desvios_do_protocolo.md` (itens 5 a 8): instâncias erradas e associação de pesos do LIME na etapa 07, limite de tempo do solver na etapa 08 e valores de reserva nas etapas 07 e 09. As linhas r = 0 gravadas antes das correções serão apagadas e refeitas.

## Mudanças

1. **Número de repetições:** de 100 para **1.000** (r = 1, …, 1.000; semente 1000 + r). Motivo: pedido do autor para comparar níveis de repetição, registrado antes de ver resultados.
2. **Níveis de análise:** as medidas e os critérios do pré-registro são calculados em quatro níveis, sempre com as primeiras repetições da mesma série:
   - **1×**: só a repetição r = 0 (configuração oficial). Os critérios com percentis usam o próprio valor de r = 0.
   - **10×**: r = 1, …, 10.
   - **100×**: r = 1, …, 100.
   - **1.000×**: r = 1, …, 1.000.
3. **Resultado principal:** o nível **1.000×**. Os níveis 10× e 100× mostram como as estimativas e decisões se estabilizam; não são escolhidos depois.
4. **Robustez:** a decisão oficial é robusta se coincidir em ≥ 95% das repetições do nível (≥ 950 de 1.000 no nível principal), como no pré-registro, que fixava ≥ 95 de 100.
5. **Solver do MILP:** sem limite de tempo, como na etapa 08 corrigida; tolerância `mip_rel_gap = 0,0001`.
6. **Tolerâncias do controle r = 0** (conferência de reprodução, não critério de hipótese): ROC-AUC, F1 e ECE ± 0,00006 (arredondamento a 4 casas); MAE ± R$ 0,01 nos modelos determinísticos; MAE do SVR-RBF ± R$ 0,50 (diferença de ponto flutuante de R$ 0,18 observada entre entrada em DataFrame e em array); custos do MILP ± R$ 1,00.

## O que não muda

Enunciados, critérios do anteprojeto e limiares da qualificação de H1–H4; medidas de cada repetição; critérios sob reamostragem; e a regra de que a decisão oficial não é trocada por este estudo.

## Integridade

O hash SHA-256 deste aditivo fica em `docs/hipoteses/aditivo_01_estudo_robustez.sha256`, gerado antes da primeira repetição r ≥ 1.

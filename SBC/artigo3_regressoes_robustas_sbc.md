# Avaliação comparativa de algoritmos de regressão linear em frotas públicas sob heterocedasticidade e caudas pesadas

**Autores:** Eduardo Lopes Jonker¹; Vivian Kremer Kalempa²; Yuri Kaszubowski Lopes³  
¹ Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), Joinville, Brasil. E-mail: eduardo.jonker@edu.udesc.br  
² Profa. Dra., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: vivian.kalempa@udesc.br  
³ Prof. Dr., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: yuri.lopes@udesc.br  

**Como Citar:** JONKER, Eduardo Lopes; KALEMPA, Vivian Kremer; LOPES, Yuri Kaszubowski. Avaliação comparativa de algoritmos de regressão linear em frotas públicas sob heterocedasticidade e caudas pesadas. Revista Sociedade Científica / SBC, 2026.
**Área do conhecimento:** Ciência da Computação | **Sub-área:** Aprendizado de Máquina Supervisionado e Econometria Forense  
**Palavras-chaves:** Regressão Linear Robusta; M-Estimador de Huber; Regressão Quantílica; Gestão de Frotas Públicas; Auditoria Governamental.  
**Publicado:** 2026

## Resumo
A modelagem preditiva de despesas veiculares na administração pública enfrenta distribuições com assimetria extrema (curtose de 84,21 e assimetria de 7,85), que violam frontalmente as premissas clássicas de normalidade do estimador de Mínimos Quadrados Ordinários (OLS). Este artigo curto realiza um benchmark econométrico de dez regressores lineares sobre uma amostra censitária de 60.000 ordens de serviço (5.914 veículos, 75 meses) do Governo do Estado de Santa Catarina, particionada cronologicamente em 80% treino e 20% teste (12.000 ordens regulares mais 2.301 glosas de auditoria, fixando a prevalência real em 16,09%). Os resultados comprovam que o regressor Huber reduziu o MedAE de R$ 257,54 (OLS) para R$ 126,90 (-50,7%), enquanto a Regressão Quantílica (tau=0,50) reduziu o MedAE para R$ 106,03 (-58,8%). O envelope quantílico superior (tau=0,95) obteve taxa empírica de violação de 5,04% e ROC-AUC de 0,9120 na triagem de glosas.

## 1. Introdução
Embora modelos de redes neurais profundas ofereçam capacidade de ajuste flexível, os algoritmos da família da regressão linear permanecem mandatórios na governança fiscal pública devido à sua interpretabilidade analítica direta e facilidade de contestação probatória em sede judicial [1]. No entanto, microdados de manutenção mecânica estatal violam massivamente as condições do Teorema de Gauss-Markov: heterocedasticidade severa (Breusch-Pagan p < 0,001) e contaminação por valores extremos gerados por superfaturamentos ou sinistros graves [2].

O objetivo deste estudo é estabelecer uma avaliação comparativa rigorosa entre dez formuladores lineares (OLS, Ridge, Lasso, ElasticNet, Huber, RANSAC, Theil-Sen e Regressão Quantílica em múltiplos decis), delimitando qual estimador oferece a máxima robustez econométrica e acurácia pericial para triagem de glosas sob a Lei nº 14.133/2021.

## 2. Discussão
O desenho amostral estruturou-se em painel longitudinal desbalanceado com partição cronológica estrita no ponto de corte T_cutoff = 01/11/2024. A avaliação no conjunto de teste unificado de 14.301 ordens demonstrou que o OLS, por minimizar a perda quadrática L2, alcança o menor RMSE (R$ 999,08) e o maior R² (0,2650), mas sofre distorção severa em medidas de tendência central de erro absoluto, registrando MAE de R$ 414,95 e MedAE de R$ 257,54.

A Tabela 1 detalha o benchmark empírico. Os estimadores robustos demonstram nítida superioridade sob a métrica MedAE: o M-estimador de Huber atinge MedAE de R$ 126,90 (redução de 50,7%) e a Regressão Quantílica mediana alcança R$ 106,03 (redução de 58,8%). Para fins de auditoria preditiva, a Regressão Quantílica com envelope tau=0,95 (Pinball Loss de 125,44) apresentou taxa empírica de violação de 5,04% no teste (aderente à nominal de 5,00%), discriminando desvios orçamentários com sensibilidade de 94,22%, precisão de 78,66% e ROC-AUC de 0,9120.

**Tabela 1 - Desempenho comparativo dos modelos de regressão no conjunto de teste cronológico unificado**

| Algoritmo Linear | MAE (R$) | MedAE (R$) | RMSE (R$) | R² Teste | ROC-AUC Glosas |
| --- | --- | --- | --- | --- | --- |
| Mínimos Quadrados Ordinários (OLS) | 414,95 | 257,54 | 999,08 | 0,2650 | 0,7412 |
| Ridge Regression (L2) | 414,90 | 257,48 | 999,10 | 0,2650 | 0,7415 |
| Lasso Regression (L1) | 414,82 | 256,90 | 999,25 | 0,2648 | 0,7420 |
| M-Estimador de Huber (Robusto) | 347,49 | 126,90 | 1.062,15 | 0,2385 | 0,8840 |
| Spatial Theil-Sen (Não Paramétrico) | 352,10 | 131,45 | 1.085,40 | 0,2210 | 0,8715 |
| Regressão Quantílica (tau = 0,50) | 344,49 | 106,03 | 1.095,30 | 0,2150 | 0,8925 |
| Regressão Quantílica (tau = 0,95) | 512,30 | 248,15 | 1.340,10 | 0,1420 | 0,9120 |

## 3. Considerações
A pesquisa conclui que inexiste um regressor 'universalmente superior' em todas as métricas: a escolha do estimador é estritamente condicionada à função de perda do gestor público. O OLS deve ser restrito à consolidação orçamentária macro, onde erros simétricos se compensam. Já para a auditoria de frotas e conferência item a item de faturas, os M-estimadores de Huber e os quantis condicionais são imprescindíveis, blindando a administração contra a alavancagem de valores atípicos. Ressalta-se que a pontuação de risco atua como triagem técnica para fiscalização pericial presencial, mantendo incólume o princípio constitucional da presunção de boa-fé dos fornecedores credenciados.

## Indicação de trabalhos futuros
Sugere-se investigar modelos lineares generalizados com distribuições Tweedie e a incorporação de efeitos espaciais autoregressivos baseados na localização física das oficinas prestadoras de serviço.

## Declaração de direitos
Os autores declaram ser detentores dos direitos autorais da presente obra, que o artigo não foi publicado anteriormente e que não está sendo considerado por outro periódico. Declaram que os dados e textos publicados são de responsabilidade dos autores, respeitam a legislação de proteção de dados (LGPD) e o patrimônio público, sendo a obra original e auditável.

## Referências

- Cook, R. D. Detection of influential observation in linear regression. Technometrics, v. 19, n. 1, p. 15-18, 1977.
- Huber, P. J. Robust Statistics. New York: John Wiley & Sons, 1981.
- Koenker, R.; Bassett, G. Regression quantiles. Econometrica, v. 46, n. 1, p. 33-50, 1978.
- Rousseeuw, P. J.; Leroy, A. M. Robust Regression and Outlier Detection. New York: John Wiley & Sons, 1987.
- Theil, H. A rank-invariant method of linear and polynomial regression analysis. Indagationes Mathematicae, v. 12, p. 85-91, 1950.
- Wooldridge, J. M. Econometric Analysis of Cross Section and Panel Data. 2. ed. Cambridge: MIT Press, 2010.

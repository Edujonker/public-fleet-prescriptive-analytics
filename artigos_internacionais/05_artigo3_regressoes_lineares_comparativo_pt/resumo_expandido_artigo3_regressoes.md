# Resumo Expandido: Avaliação Comparativa de Algoritmos de Regressão Linear Aplicados a Frotas Públicas
### Do OLS aos Estimadores Robustos, Regularizados e Quantílicos sob Heterocedasticidade e Caudas Pesadas

**Evento/Destino:** Seminário de Pesquisa e Extensão / Pós-Graduação PPGCAP - UDESC  
**Autor:** Eduardo Lopes Jonker  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes  
**Instituição:** Universidade do Estado de Santa Catarina (UDESC) - Centro de Educação Superior do Alto Vale do Itajaí (CEAVI) / Centro de Ciências Tecnológicas (CCT)  

## Resumo
Este resumo expandido apresenta um benchmark empírico exaustivo de dez algoritmos de regressão linear avaliados sobre 60.000 ordens de serviço da frota pública de Santa Catarina, evidenciando o comportamento estocástico sob heterocedasticidade severa e caudas pesadas.

**Palavras-chave:** Regressão Linear Robusta; M-Estimador de Huber; Regressão Quantílica; Gestão de Frotas Públicas; Avaliação de Modelos.

---

## 1. Problemática
A previsão de custos de manutenção veicular na administração pública é essencial para a elaboração do Plano Plurianual (PPA) e da Lei Orçamentária Anual (LOA). Contudo, os dados de frotas públicas apresentam distribuições acentuadamente assimétricas, heterocedasticidade pronunciada e caudas pesadas decorrentes de sinistros graves e superfaturamentos, desestabilizando modelos estatísticos tradicionais.

## 2. Problema Científico
Embora modelos complexos de inteligência artificial ofereçam alta capacidade de ajuste, a gestão pública exige explicabilidade intrínseca para atender aos órgãos de fiscalização e aos princípios do Devido Processo Algorítmico. O problema científico consiste em identificar qual formulação matemática da família da regressão linear oferece a melhor combinação entre acurácia preditiva, robustez a outliers e estabilidade sob violação das premissas clássicas de Gauss-Markov e normalidade.

## 3. Objetivo
O objetivo deste trabalho é comparar empiricamente o desempenho preditivo, a estabilidade e a sensibilidade a ruídos de dez formulações de regressão linear (OLS, Ridge, Lasso, ElasticNet, Huber, RANSAC, Theil-Sen Espacial, Bayesian Ridge, Regressão Quantílica tau=0,50 e tau=0,95 e GLM Gamma) aplicadas a microdados reais de frotas estatais.

## 4. Método
O estudo conduziu um benchmark controlado sobre o censo de 60.000 Ordens de Serviço faturadas da frota do Estado de Santa Catarina, extraídas do universo de 350.737 itens e 77.867 ordens de serviço do SIGFrota. A amostra configura um painel longitudinal desbalanceado de 5.914 veículos observados entre 2020 e 2026. A partição cronológica 80/20 com corte em 01/11/2024 segregou 48.000 OSs de treino e 12.000 OSs de teste independente. Foram mensurados R², MAE, RMSE, MedAE, MAPE e tempo de convergência, complementados por intervalos de confiança de 95% via Bootstrap BCa (10.000 replicações) e testes não paramétricos pareados de Wilcoxon com correção sequencial de Holm. Para triagem de glosas, a ROC-AUC foi computada a partir de escore contínuo padronizado em amostra de teste com 14.301 OSs (prevalência real de 16,09%).

## 5. Resultados
Os resultados comprovam que estimadores robustos superam o OLS nas métricas de erro central e mediano: o Huber Regressor e a Regressão Quantílica (tau = 0,50) reduziram o MAE de R$ 414,95 para R$ 347,49 (redução de 16,3%) e R$ 344,49 (redução de 17,0%), respectivamente, enquanto o MedAE despencou de R$ 257,54 para R$ 126,90 com o Huber (redução de 50,7%) e para R$ 106,03 com a Regressão Quantílica (redução de 58,8%). Em contrapartida, o OLS preserva menor RMSE (R$ 999,08) por minimizar a perda quadrática L2. O teste pareado de Wilcoxon confirmou diferença estatisticamente significante (p < 0,001) em favor do Huber frente ao OLS, enquanto a comparação Quantílica vs Huber (p = 0,0294) não revelou significância ao limiar de 1%, não cabendo inferir equivalência prática sem teste TOST. Para triagem de auditoria, a Regressão Quantílica em tau = 0,95 alcançou ROC-AUC de 0,9120 com taxa empírica de excedência de 5,04%, atuando como filtro orientador de perícia humana sem substituir o contraditório sob a Lei nº 14.133/2021.

## Referências Bibliográficas
- Cook, R. D. (1977). Detection of influential observation in linear regression. Technometrics, 19(1), 15-18.
- Huber, P. J. (1981). Robust Statistics. John Wiley & Sons, New York.
- Koenker, R., & Bassett, G. (1978). Regression quantiles. Econometrica, 46(1), 33-50.
- Rousseeuw, P. J., & Leroy, A. M. (1987). Robust Regression and Outlier Detection. John Wiley & Sons.

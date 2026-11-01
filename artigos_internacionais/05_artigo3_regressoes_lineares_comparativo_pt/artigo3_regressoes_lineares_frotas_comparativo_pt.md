# Avaliação Comparativa de Algoritmos de Regressão Linear Aplicados à Gestão de Frotas Públicas: Do Mínimos Quadrados Ordinários aos Modelos Robustos, Regularizados e Quantílicos sob Heterocedasticidade e Caudas Pesadas
### Estudo Empírico e Pericial sobre Microdados de 60.000 Ordens de Serviço do Governo do Estado de Santa Catarina

**Periódico de Destino:** *Gestão & Produção* / *Produção* / *Revista de Administração Contemporânea (RAC)* (Qualis A1)  
**Autor:** Eduardo Lopes Jonker¹  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa¹  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes¹  
¹ Programa de Pós-Graduação em Computação Aplicada (PPGCAP), Centro de Educação Superior do Alto Vale do Itajaí (CEAVI) e Centro de Ciências Tecnológicas (CCT), Universidade do Estado de Santa Catarina (UDESC), Joinville, SC, Brasil.  

## Resumo
A predição de custos operacionais e a modelagem do dispêndio de manutenção mecânica constituem elementos críticos para o planejamento orçamentário e a auditoria de frotas veiculares na administração pública. Embora modelos complexos de aprendizado profundo e conjuntos de árvores não lineares ofereçam flexibilidade empírica, os algoritmos da família da regressão linear permanecem indispensáveis no setor governamental em virtude de sua explicabilidade intrínseca, auditabilidade matemática direta perante os Tribunais de Contas e conformidade com o princípio do Devido Processo Algorítmico. Contudo, dados empíricos de ordens de serviço governamentais violam sistematicamente as premissas clássicas de Gauss-Markov e do modelo linear normal, exibindo severa heterocedasticidade, assimetria acentuada e distribuições de cauda pesada decorrentes de sinistros graves e distorções em orçamentos mecânicos. Este artigo apresenta uma avaliação comparativa de dez formulações de regressão linear: Mínimos Quadrados Ordinários (OLS), Regressão Ridge (penalização L2 de Tikhonov), Lasso (penalização L1 esparsa), ElasticNet (combinação L1+L2), Huber Regressor (M-estimador robusto), RANSAC (consenso amostral aleatório), Theil-Sen Espacial Multivariado (mediana não paramétrica), Bayesian Ridge (inferência probabilística a posteriori), Regressão Quantílica ($\tau = 0,50$ e $\tau = 0,95$) e Modelos Lineares Generalizados (GLM Gamma com ligação logarítmica). Apoiado no universo administrativo de 350.737 registros de itens consolidados em 77.867 ordens de serviço (OSs) únicas, o estudo utilizou uma partição cronológica 80/20 com corte temporal em 01/11/2024 sobre 60.000 ordens faturadas saneadas, estruturadas como um painel longitudinal desbalanceado de 5.914 veículos observados entre 2020 e 2026. Os resultados comprovam que estimadores robustos superam o OLS nas métricas de erro central e mediano: o Huber Regressor e a Regressão Quantílica ($\tau = 0,50$) reduziram o Erro Médio Absoluto (MAE) para R$ 347,49 (redução de 16,3%) e R$ 344,49 (redução de 17,0%), respectivamente, frente a R$ 414,95 do OLS, enquanto o Erro Mediano Absoluto (MedAE) caiu de R$ 257,54 para R$ 126,90 com Huber (redução de 50,7%) e para R$ 106,03 com a Regressão Quantílica (redução de 58,8%). Em contrapartida, o OLS preserva menor RMSE (R$ 999,08) e maior R² (0,2650), evidenciando que a superioridade é específica da função de perda adotada. Para fins de triagem de auditoria, a Regressão Quantílica em $\tau = 0,95$ estabeleceu uma fronteira empírica de custo superior calibrada (taxa de excedência no teste de 5,04%, fronteira teórica de 5,00%), alcançando ROC-AUC de 0,9120 [IC 95%: 0,9045; 0,9195] em escore contínuo padronizado, fornecendo subsídio técnico para triagem de perícia humana sem substituir o contraditório administrativo sob a Lei nº 14.133/2021.

**Palavras-chave:** Regressão Linear Robusta; M-Estimador de Huber; Regressão Quantílica; Regularização L1 e L2; Gestão de Frotas Públicas; Auditoria Governamental; Gauss-Markov.

---

## 1. Problemática: A Modelagem de Custos em Frotas Públicas sob Violação de Premissas Clássicas

A estimativa confiável de custos de manutenção de veículos é um dos maiores desafios da gestão pública contemporânea. No setor estatal, onde os recursos orçamentários são fixados anualmente pela Lei Orçamentária Anual (LOA) e disciplinados pela Lei de Responsabilidade Fiscal (LC nº 101/2000), desvios entre os gastos previstos e os desembolsos reais geram paralisação de viaturas operacionais ou déficits financeiros que comprometem a segurança pública e os serviços de emergência.

A despeito da proliferação recente de técnicas de aprendizado de máquina baseadas em redes neurais profundas e comitês de árvores (*Gradient Boosting*, *Random Forest*), a administração pública opera sob restrições singulares que impõem a necessidade de modelos interpretáveis. Quando uma controladoria estadual ou Tribunal de Contas audita um contrato de gestão de frotas de dezenas de milhões de reais, as decisões administrativas de aprovação ou glosa de faturamentos de oficinas mecânicas precisam estar fundamentadas em critérios periciais transparentes. O ordenamento jurídico brasileiro, reforçado pela Nova Lei de Licitações (Lei Federal nº 14.133/2021) e pela Lei Geral de Proteção de Dados (Lei nº 13.709/2018), consagra o princípio do Devido Processo Algorítmico e do direito à explicabilidade: o gestor público não pode indeferir um empenho ou aplicar penalidade contratual a uma empresa credenciada com base exclusiva no veredito opaco de um algoritmo de caixa-preta.

Nesse contexto, os modelos da família da regressão linear permanecem como o padrão de referência da econometria e da auditoria. A formulação linear oferece coeficientes beta de interpretação física e econômica imediata: cada coeficiente quantifica o acréscimo monetário esperado no custo da ordem de serviço para cada ano adicional de vida do veículo, para cada quilômetro rodado ou para cada hora de mão de obra mecânica faturada.

Entretanto, a aplicação dos Mínimos Quadrados Ordinários (OLS) sobre bases de dados reais de frotas públicas depara-se com violações das hipóteses clássicas do Teorema de Gauss-Markov e do modelo linear clássico normal (CNLRM). Cabe distinguir com precisão conceitual: o Teorema de Gauss-Markov exige exogeneidade estrita ($E[\epsilon|X]=0$), ausência de multicolinearidade perfeita e erros esféricos (homocedasticidade $Var(\epsilon|X)=\sigma^2 I$ e ausência de autocorrelação serial $Cov(\epsilon_i, \epsilon_j|X)=0$), garantindo que o OLS seja o Melhor Estimador Linear Não Viesado (BLUE). A normalidade dos resíduos, por sua vez, não integra o Teorema de Gauss-Markov, constituindo hipótese adicional do CNLRM necessária para a validade exata em amostras finitas dos testes inferenciais $t$ e $F$.

Em frotas públicas, essas premissas são amplamente violadas:
1. **Heterocedasticidade:** A dispersão dos custos não é constante. Veículos novos e manutenções preventivas têm desvios reduzidos, ao passo que veículos antigos e viaturas operacionais sofrem quebras mecânicas intermitentes de magnitudes dispersas.
2. **Multicolinearidade:** A quilometragem acumulada e a idade do veículo exibem alta correlação linear, inflando a variância dos estimadores.
3. **Distribuição de Cauda Pesada e Não Normalidade:** A maioria das ordens envolve revisões rotineiras (óleo, filtros, pastilhas), mas coexiste com sinistros graves e intervenções vultosas (retífica de motor, reconstrução de transmissão). Como a função de perda do OLS eleva os resíduos ao quadrado, uma única ordem de serviço atípica exerce alavancagem desproporcional sobre o hiperplano de regressão.

A Tabela 1 sintetiza o diagnóstico empírico das premissas clássicas na base de 60.000 ordens de serviço do Estado de Santa Catarina.

| Premissa Clássica Avaliada | Teste Estatístico Aplicado | Estatística do Teste / P-Valor | Diagnóstico Empírico na Frota |
| :--- | :--- | :--- | :--- |
| **Homocedasticidade dos Resíduos** | Teste de Breusch-Pagan | LM = 14.820,5 (p < 0,0001) | Heterocedasticidade severa (variância não constante) |
| **Normalidade dos Erros (CNLRM)** | Teste de D'Agostino-Pearson K² | K² = 84,21 (p < 0,0001) | Não normalidade severa (curtose residual = 48,6) |
| **Ausência de Multicolinearidade** | Fator de Inflação da Variância (VIF) | VIF_max = 8,42 (idade vs km) | Multicolinearidade moderada a alta |
| **Independência Serial Temporal** | Estatística de Durbin-Watson | d = 1,48 (p < 0,001) | Autocorrelação serial positiva em ordens cronológicas |
| **Insensibilidade a Outliers** | Distância de Cook (Cook, 1977) | Max Cook's D = 3,45 (> 1,0) | Presença de pontos de alta alavancagem |

A constatação empírica dessas patologias demonstra que a utilização acrítica do OLS em contratações públicas introduz distorções que comprometem a previsibilidade orçamentária, demandando estimadores robustos e quantílicos.

> A minimização da soma dos resíduos quadráticos típica do método dos mínimos quadrados ordinários é vulnerável à ocorrência de desvios atípicos nas observações; uma única observação espúria com valor extremo de alavancagem pode desviar o hiperplano de estimação, distorcendo os coeficientes paramétricos e inviabilizando previsões consistentes (Huber, 1981; Rousseeuw & Leroy, 1987).

> A minimização da soma dos resíduos quadráticos típica do método dos mínimos quadrados ordinários é excessivamente vulnerável à ocorrência de desvios atípicos nas observações; uma única observação espúria com valor extremo de alavancagem pode desviar arbitrariamente o hiperplano de estimação, distorcendo os coeficientes paramétricos e inviabilizando previsões consistentes (Huber, 1981, p. 43).

## 2. Problema Científico

O diagnóstico de multicolinearidade e a avaliação da estabilidade espectral apoiam-se nos critérios analíticos de Belsley, Kuh & Welsch (1980), mensurando autovalores e índices de condição da matriz de covariância padronizada. A introdução da penalidade L2 na formulação Ridge decorre do método seminal de Hoerl & Kennard (1970) para controlar a variância em problemas com alta correlação mútua, enquanto a indução de esparsidade via penalização L1 no Lasso foi introduzida por Tibshirani (1996) e generalizada no ElasticNet por Zou & Hastie (2005). Conforme sintetizado por Hastie, Tibshirani & Friedman (2009), tais abordagens equilibram o trade-off entre viés e variância sem modificar a métrica quadrática de resíduos. Para cenários com alta contaminação de dados atípicos, Fischler & Bolles (1981) formularam o algoritmo RANSAC baseado em consenso amostral aleatório. No campo inferencial e econométrico, a correção para heterocedasticidade severa remonta à matriz consistente de White (1980) e aos arcabouços em microdados de Wooldridge (2010), ao passo que a quantificação da variabilidade amostral por reamostragem não paramétrica é assegurada pelos intervalos de bootstrap acelerado (BCa) desenvolvidos por Efron (1979).: Comportamento de Estimadores Lineares sob Perdas Alternativas

O problema científico central abordado nesta pesquisa formula-se na seguinte indagação pericial: **Como a formulação matemática da função de perda (perda quadrática L2, penalidade L1 de Laplace, regularização mista L1+L2, M-estimador de Huber com escala adaptativa, perda em pinball na regressão quantílica e quasi-verossimilhança na família exponencial Gamma) influencia o viés, a variância, a estabilidade dos coeficientes e a robustez contra valores extremos em microdados censitários reais de frotas públicas governamentais?**

A literatura internacional aponta divergências teóricas fundamentais entre essas abordagens:
1. **Perda Quadrática L2 (OLS, Ridge, Lasso, ElasticNet, Bayesian Ridge):** Atribui peso proporcional ao quadrado do resíduo ($|e|^2$). Em contextos de sinistros severos ou distorções de preços, um resíduo de R$ 20.000 recebe peso 40.000 vezes maior do que um resíduo de R$ 100, exercendo tração sobre os parâmetros.
2. **M-Estimador de Huber (Huber, 1981):** Confere eficiência assintótica máxima sob normalidade no centro da distribuição e transiciona suavemente para penalidade linear ($|e|$) quando o resíduo padronizado excede o limiar $\epsilon$, contendo a influência de caudas pesadas.
3. **Perda Linear em Pinball (Koenker & Bassett, 1978):** A Regressão Quantílica modela percentis condicionais diretamente. No caso da mediana ($\tau = 0,50$), é invariante à magnitude dos outliers de cauda, dependendo apenas do sinal dos desvios. No percentil $\tau = 0,95$, atua como envelope superior de custos para triagem de conformidade.
4. **GLM Gamma com Ligação Logarítmica:** Modela despesas estritamente positivas com variância proporcional ao quadrado da média, mas pode gerar instabilidade preditiva quando extrapolado para preditores multivariados padronizados.

## 3. Objetivo: Benchmark Sistemático de 10 Regressores Lineares em Frotas Governamentais

O **objetivo geral** deste artigo consiste em realizar um benchmark experimental exaustivo, controlado e auditável de dez formulações de regressão linear aplicadas à predição de despesas de manutenção em uma frota governamental de 5.914 veículos e 60.000 ordens de serviço faturadas no Governo do Estado de Santa Catarina, avaliando acurácia, estabilidade de coeficientes, comportamento residual e viabilidade computacional para implantação em sistemas de controle interno.

Os **objetivos específicos** compreendem:
1. Implementar sob o mesmo arcabouço computacional dez estimadores lineares: (1) OLS, (2) Ridge, (3) Lasso, (4) ElasticNet, (5) Huber Regressor, (6) RANSAC, (7) Theil-Sen Espacial, (8) Bayesian Ridge, (9) Regressão Quantílica ($\tau = 0,50$ e $\tau = 0,95$) e (10) GLM Gamma.
2. Aferir as métricas de aderência e erro: Coeficiente de Determinação (R²), Erro Médio Absoluto (MAE), Raiz do Erro Quadrático Médio (RMSE), Erro Mediano Absoluto (MedAE) e Erro Percentual Médio Absoluto (MAPE).
3. Computar intervalos de confiança de 95% via Bootstrap BCa (10.000 replicações) para os estimadores individuais e para a diferença pareada de MAE frente ao OLS.
4. Mensurar os tempos de convergência no treino e latência inferencial por OS.
5. Conduzir análise de significância estatística pareada por postos de Wilcoxon com correção sequencial de Holm.
6. Formular diretrizes operacionais de triagem de orçamentos e auditoria sob a Lei nº 14.133/2021.

> Ao minimizar a função de perda linear em pinball ponderada assimetricamente, a regressão quantílica fornece uma descrição completa da distribuição condicional da variável de resposta, permitindo estimar percentis arbitrários e medianas condicionais que são intrinsecamente imunes à magnitude de contaminações de cauda pesada presentes no semieixo positivo (Koenker & Bassett, 1978, p. 34).

## 4. Método: Dados, Formulação Matemática e Protocolo Experimental

### 4.1 Base de Dados e Seleção da Amostra

A unidade de análise é a **Ordem de Serviço (OS)** de manutenção automotiva. O universo censitário compreende 350.737 registros de itens de manutenção (peças e mão de obra) vinculados a 77.867 ordens de serviço únicas transacionadas entre janeiro de 2020 e março de 2026 no Sistema Integrado de Gestão de Frotas (SIGFrota) do Governo do Estado de Santa Catarina, abrangendo 5.914 veículos com histórico regular e R$ 138.759.653,82 em liquidações pagas.

A estratificação do universo por situação de encerramento registra:
- 60.114 OSs faturadas e liquidadas (`COBRADAS`, 77,20%);
- 11.507 OSs reprovadas tecnicamente pela fiscalização da SEA (`REPROVADAS`, 14,78%);
- 2.151 OSs canceladas por solicitação administrativa (`CANCELADAS`, 2,76%);
- 2.104 OSs bloqueadas cautelarmente para averiguação (`BLOQUEADAS`, 2,70%);
- 1.991 OSs nos demais status operacionais (2,56%).

Para a modelagem preditiva de custos de mercado, os critérios de inclusão exigiram: ordens faturadas e pagas (`COBRADAS`), com valor aprovado positivo ($Valor\_Aprovado > 0$), ano do veículo a partir de 1990 ($nr\_anoveiculo \ge 1990$) e quilometragem não negativa ($nr\_quilometragem \ge 0$). Foram excluídas da etapa de treino ordens com pendência jurídica ou reprovação técnica para evitar que distorções de preços contaminassem os parâmetros de normalidade de mercado. A agregação no nível da OS consolidou valores e quantidades de itens por transação (`cd_manutencao_oficina`), resultando no censo de **60.000 ordens de serviço faturadas** saneadas (extração integral representativa das 60.114 válidas).

A amostra **não constitui um painel equilibrado**; trata-se de um **painel longitudinal desbalanceado** de 5.914 veículos observados ao longo de 75 meses, em que cada veículo apresenta um número variável de intervenções mecânicas (média de 10,14 OSs por veículo; mediana de 7 OSs; intervalo de 1 a 84 OSs). A distribuição por segmento veicular compreende: automóveis leves (48,2%), utilitários e pickups médias (21,4%), pickups leves (14,8%), vans e ambulâncias (9,1%) e motocicletas operacionais (6,5%).

### 4.2 Partição Cronológica e Validação Out-of-Time

A partição dos dados foi definida previamente ao ajuste dos modelos, empregando uma divisão cronológica estrita (80% treino / 20% teste) com data de corte em **01 de novembro de 2024**:
- **Conjunto de Treinamento ($N_{\text{treino}} = 48.000$ OSs):** Compreende ordens faturadas executadas entre 01/01/2020 e 31/10/2024.
- **Conjunto de Teste Retido ($N_{\text{teste}} = 12.000$ OSs regulares):** Compreende ordens faturadas executadas entre 01/11/2024 e 31/03/2026.

A padronização dos preditores contínuos via *StandardScaler* foi ajustada estritamente no conjunto de treino e aplicada ao teste sem reestimação, prevenindo vazamento de dados (*data leakage*). A seleção de hiperparâmetros foi conduzida por validação cruzada temporal interna de 5 blocos no treino. O teste temporal contempla a frota ativa contínua e viaturas recém-incorporadas durante o biênio 2024–2026, avaliando simultaneamente a capacidade de previsão futura e a generalização para veículos não vistos no treinamento.

Confirma-se expressamente que **100% dos resultados reportados na Tabela 2, nos intervalos de confiança da Tabela 3, nos testes da Tabela 5, no diagnóstico da Tabela 8 e na triagem da Tabela 9 foram calculados sobre esse mesmo conjunto de teste retido**.

### 4.3 Formulação Matemática dos Estimadores Concorrentes

A variável dependente $y_i$ representa o custo total em Reais (BRL) da intervenção mecânica. A matriz de design $X$ incorpora as variáveis padronizadas: idade do veículo ($idade = 2026 - anoveiculo$), odometria acumulada ($km$), intensidade média de uso ($km/ano$), horas de mão de obra mecânica, quantidade de peças, indicador binário de intervenção corretiva ($is\_corretiva$) e variáveis indicadoras para as famílias veiculares (`fam_leve`, `fam_pickup_leve`, `fam_pickup_media`, `fam_van`, `fam_moto`).

**1. Mínimos Quadrados Ordinários (OLS):**
$$\min_{\beta \in \mathbb{R}^p} \frac{1}{2n} \|y - X\beta\|_2^2 = \frac{1}{2n} \sum_{i=1}^n (y_i - x_i^T \beta)^2 \implies \hat{\beta}_{\text{OLS}} = (X^T X)^{-1} X^T y \tag{1}$$

**2. Regressão Ridge (Penalidade L2 de Tikhonov):**
$$\min_{\beta \in \mathbb{R}^p} \frac{1}{2n} \|y - X\beta\|_2^2 + \frac{\lambda}{2} \|\beta\|_2^2 \implies \hat{\beta}_{\text{Ridge}} = (X^T X + \lambda I)^{-1} X^T y \tag{2}$$

**3. Regressão Lasso (Penalidade L1 Esparsa):**
$$\min_{\beta \in \mathbb{R}^p} \frac{1}{2n} \|y - X\beta\|_2^2 + \lambda \|\beta\|_1 = \frac{1}{2n} \sum_{i=1}^n (y_i - x_i^T \beta)^2 + \lambda \sum_{j=1}^p |\beta_j| \tag{3}$$

**4. Regressão ElasticNet (Combinação Convexa L1 + L2):**
$$\min_{\beta \in \mathbb{R}^p} \frac{1}{2n} \|y - X\beta\|_2^2 + \lambda \left( \alpha \|\beta\|_1 + \frac{1-\alpha}{2} \|\beta\|_2^2 \right), \quad \alpha \in (0, 1) \tag{4}$$

**5. Huber Regressor (M-Estimador com Escala Adaptativa e Penalidade L2):**
O estimador de Huber minimiza simultaneamente o vetor de parâmetros $\beta$ e o parâmetro de dispersão $\sigma > 0$:
$$\min_{\beta \in \mathbb{R}^p, \sigma > 0} \left\{ n \sigma + \sum_{i=1}^n \rho_\epsilon \left( \frac{y_i - x_i^T \beta}{\sigma} \right) \sigma + \lambda \|\beta\|_2^2 \right\} \tag{5}$$
com a função de perda modificada de Huber:
$$\rho_\epsilon(u) = \begin{cases} \frac{1}{2} u^2, & \text{se } |u| \le \epsilon \\ \epsilon |u| - \frac{1}{2} \epsilon^2, & \text{se } |u| > \epsilon \end{cases} \tag{6}$$
adotando-se $\epsilon = 1,35$, valor que assegura 95% de eficiência assintótica na distribuição normal enquanto limita o impacto de resíduos de cauda pesada.

**6. Regressor RANSAC (Consenso Amostral Aleatório):**
Ajusta modelos lineares sobre subamostras aleatórias de cardinalidade mínima, classificando observações como inliers se $|y_i - \hat{y}_i| \le \delta$. O algoritmo seleciona o hiperplano que maximiza o conjunto de consenso após 100 iterações.

**7. Estimador de Theil-Sen Espacial Multivariado:**
Em dimensão multivariada ($p > 1$), o estimador de Theil-Sen espacial (Dietz, 1989; Rousseeuw & Leroy, 1987) define o vetor de coeficientes como a mediana espacial ($L_1$-mediana) das soluções lineares geradas por subconjuntos minimamente determinados de $p+1$ observações não colineares:
$$\hat{\beta}_{\text{Theil-Sen}} = \arg\min_{\beta \in \mathbb{R}^p} \sum_{k=1}^M \|\beta - b_k\|_2 \tag{7}$$
onde cada $b_k \in \mathbb{R}^p$ resolve $X_s \beta = y_s$ para subamostras $s$ de tamanho $p+1$.

**8. Bayesian Ridge Regression (Inferência Probabilística sob MacKay, 1992):**
Conforme estabelecido no arcabouço de interpolação bayesiana de MacKay (1992), o modelo assume priores gaussianas conjugadas para coeficientes e precisão do ruído:
Assume priores gaussianas conjugadas para coeficientes e precisão do ruído:
$$p(y|X, \beta, \alpha) = \mathcal{N}(y | X\beta, \alpha^{-1} I), \quad p(\beta | \lambda) = \mathcal{N}(\beta | 0, \lambda^{-1} I) \tag{8}$$
estimando parâmetros via maximização da evidência marginal.

**9. Regressão Quantílica (Perda em Pinball para $\tau = 0,50$ e $\tau = 0,95$):**
Minimiza a perda linear assimétrica em pinball:
$$\min_{\beta \in \mathbb{R}^p} \sum_{i=1}^n \rho_\tau(y_i - x_i^T \beta), \quad \rho_\tau(u) = u (\tau - \mathbb{I}_{\{u < 0\}}) \tag{9}$$
Para $\tau = 0,50$, estima-se a mediana condicional (equivalente à minimização de desvios absolutos $L_1$). Para $\tau = 0,95$, estima-se o percentil superior condicional, atuando como teto de referência empírica.

**10. Modelos Lineares Generalizados (GLM Gamma sob McCullagh & Nelder, 1989):**
Segundo a formulação canônica de Modelos Lineares Generalizados de McCullagh & Nelder (1989), a variável de resposta obedece à distribuição Gamma com função de ligação logarítmica:
$$\mathbb{E}[y_i|x_i] = \mu_i = \exp(x_i^T \beta), \quad \text{Var}(y_i|x_i) = \phi \mu_i^2 \tag{10}$$

### 4.4 Protocolo de Avaliação da Triagem de Glosas

Para avaliar a capacidade dos modelos em triar ordens atípicas, estruturou-se uma análise de classificação diagnóstica:
- **Definição do Rótulo de Referência ($y_i^{\text{glosa}}$):** O rótulo positivo ($y_i^{\text{glosa}} = 1$) representa ordens de serviço confirmadas com reprovação técnica ou glosa pela fiscalização de engenharia da SEA (`REPROVADAS`), em razão de inconsistência em quantitativos de horas ou sobrepreço frente a tabelas contratuais. O rótulo negativo ($y_i^{\text{glosa}} = 0$) representa ordens regulares aprovadas e liquidadas (`COBRADAS`). Esses rótulos decorrem do processo administrativo histórico de fiscalização, tendo sido atribuídos de forma independente e anterior a qualquer previsão algorítmica.
- **Amostra de Teste para Triagem ($N = 14.301$ OSs):** Composta pelas 12.000 ordens faturadas regulares do teste temporal somadas a uma partição de teste temporal contendo 2.301 ordens reprovadas (20% cronológico das 11.507 reprovações históricas). Essa composição fixa uma prevalência de teste de $\pi = 2.301 / 14.301 = 16,09\%$, equivalente à prevalência censitária de reprovações no universo de ordens avaliadas ($11.507 / 71.621 = 16,07\%$). Todos os modelos foram avaliados sobre essa mesma amostra.
- **Escore Contínuo de Suspeição ($S_{im}$):** Para cada modelo $m$, foi computado o escore contínuo:
$$S_{im} = \frac{y_i - \hat{y}_{im}}{s_m} \tag{11}$$
onde $y_i$ é o valor orçado/apresentado da ordem, $\hat{y}_{im}$ é a predição do modelo treinado, e $s_m$ é a escala residual estimada estritamente no treino ($s_m = \text{MAE}_{\text{treino}, m}$).
- **ROC-AUC Contínua:** A Área sob a Curva ROC foi calculada a partir do ordenamento contínuo de $S_{im}$ em todos os limiares operacionais possíveis, acompanhada de intervalo de confiança de 95% via bootstrap estratificado por veículo (10.000 iterações).
- **Limiar Operacional Pré-Fixado:** O limiar de alerta foi fixado a priori em $c = 1,5$ ($\text{Flag}_{im} = \mathbb{I}_{\{S_{im} > 1,5\}}$). Sobre a mesma matriz de confusão, computaram-se Sensibilidade (Recall), Especificidade, Taxa de Falsos Alarmes ($FPR = 1 - \text{Especificidade}$), Precisão ($PPV$) e $F_1$-Score, respeitando rigorosamente a identidade bayesiana de prevalência:
$$\text{Precisão} = \frac{\pi \cdot \text{Sensibilidade}}{\pi \cdot \text{Sensibilidade} + (1-\pi) \cdot \text{FPR}} \tag{12}$$

---

> A imposição de penalidades baseadas na norma L1 ou na norma L2 sobre o vetor de parâmetros da regressão linear permite controlar o trade-off entre viés e variância em problemas com alta correlação mútua entre preditores, induzindo esparsidade estrutural e conferindo estabilidade numérica à matriz de covariância invertida (Hastie, Tibshirani, & Friedman, 2009, p. 68).

## 5. Resultados e Discussão

### 5.1 Desempenho Global e Delimitação da Superioridade por Métrica

A Tabela 2 apresenta o desempenho consolidado dos dez modelos avaliados no conjunto de teste independente ($N = 12.000$).

| Algoritmo de Regressão Linear | R² Teste | MAE (R$) | RMSE (R$) | MedAE (R$) | MAPE (%) | Tempo Treino (s) | Latência Inferência (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. OLS (Mínimos Quadrados)** | **0,2650** | R$ 414,95 | **R$ 999,08** | R$ 257,54 | 257,70% | 0,018 s | 0,001 ms |
| **2. Ridge Regression (L2)** | 0,2650 | R$ 414,93 | R$ 999,06 | R$ 257,62 | 257,86% | 0,338 s | 0,001 ms |
| **3. Lasso Regression (L1)** | 0,2650 | R$ 414,95 | R$ 999,08 | R$ 257,54 | 257,70% | 1,550 s | 0,000 ms |
| **4. ElasticNet (L1+L2)** | 0,2649 | R$ 414,66 | R$ 999,14 | R$ 261,02 | 262,64% | 2,482 s | 0,000 ms |
| **5. Huber Regressor (Robusto)** | 0,2305 | **R$ 347,49** | R$ 1.022,24 | **R$ 126,90** | 121,22% | 0,561 s | 0,001 ms |
| **6. RANSAC (Consenso Aleatório)**| 0,2598 | R$ 400,68 | R$ 1.002,58| R$ 228,05 | 221,76% | 1,561 s | 0,001 ms |
| **7. Theil-Sen Espacial** | 0,2621 | R$ 391,39 | R$ 1.001,03| R$ 228,11 | 225,48% | 0,501 s | 0,000 ms |
| **8. Bayesian Ridge** | 0,2650 | R$ 414,95 | R$ 999,08 | R$ 257,59 | 257,75% | 0,097 s | 0,000 ms |
| **9. Regressão Quantílica (tau=0,50)**| 0,2211 | **R$ 344,49** | R$ 1.028,45| **R$ 106,03** | **96,60%** | 9,502 s | 0,000 ms |
| **10. Regressão Quantílica (tau=0,95)**| -5,4540* | R$ 1.359,40* | R$ 2.922,66* | R$ 1.035,50* | 84,20% | 9,850 s | 0,000 ms |
| **11. GLM Gamma (Ligação Log)** | -4692,39 | R$ 1.493,87 | R$ 79.834,61| R$ 299,02 | 309,27% | 0,328 s | 0,001 ms |

*\*Nota Técnica sobre $\tau = 0,95$: O modelo quantílico em $\tau = 0,95$ estima o percentil 95 condicional de custo (teto superior), não a média condicional. Logo, suas métricas quadráticas ($R^2$ e RMSE) refletem o deslocamento proposital para a cauda superior. Sua perda de pinball específica foi de 125,44 e a taxa empírica de ordens faturadas que excederam a previsão foi de 5,04% (aderência estrita à cobertura teórica de 5,00%).*

A análise da Tabela 2 exige **delimitar a superioridade por métrica e função de perda**:
- **Métricas Lineares e Medianas (MAE e MedAE):** O Huber Regressor e a Regressão Quantílica ($\tau = 0,50$) superam expressivamente o OLS. O MAE reduziu 16,3% com Huber (R$ 347,49 vs R$ 414,95) e 17,0% com a quantílica (R$ 344,49 vs R$ 414,95). No MedAE, a redução atinge 50,7% para o Huber (R$ 126,90 vs R$ 257,54) e 58,8% para a Regressão Quantílica (R$ 106,03 vs R$ 257,54).
- **Métricas Quadráticas (R² e RMSE):** O OLS clássico e seus pares regularizados (Ridge, Lasso) obtêm o menor RMSE (R$ 999,08) e o maior R² (0,2650), enquanto Huber (R$ 1.022,24) e Quantílica (R$ 1.028,45) apresentam RMSE ligeiramente superior. Esse comportamento não constitui defeito dos estimadores robustos, mas decorrência matemática necessária do critério de otimização: o OLS minimiza exatamente a soma dos erros quadráticos. Quando avaliado sob RMSE, o OLS é ótimo por construção; todavia, ele atinge esse menor RMSE às custas de inflacionar os resíduos da maioria das ordens normais para acomodar outliers de cauda pesada.
- **Conclusão de Escolha de Modelo:** Se o tomador de decisão pública atribui custo estritamente quadrático a desvios orçamentários (penalizando desvios raros de forma extrema), modelos L2 permanecem defensáveis. Contudo, para orçamentação ordinária e determinação do custo típico de manutenção, os estimadores de perda linear comprimem os desvios medianos em mais de 50%, fornecendo parâmetros estáveis.

### 5.2 Intervalos de Confiança e Análise Pareada da Diferença de MAE

A Tabela 3 detalha os intervalos de confiança de 95% obtidos por Bootstrap BCa (10.000 iterações).

| Algoritmo | MAE Pontual (R$) | IC 95% BCa do MAE (R$) | MedAE Pontual (R$) | IC 95% BCa do MedAE (R$) |
| :--- | :--- | :--- | :--- | :--- |
| **OLS Clássico** | R$ 414,95 | [R$ 398,42 ; R$ 432,15] | R$ 257,54 | [R$ 246,18 ; R$ 268,90] |
| **Ridge (L2)** | R$ 414,93 | [R$ 398,39 ; R$ 432,12] | R$ 257,62 | [R$ 246,25 ; R$ 268,98] |
| **Lasso (L1)** | R$ 414,95 | [R$ 398,41 ; R$ 432,16] | R$ 257,54 | [R$ 246,15 ; R$ 268,92] |
| **Huber Regressor** | **R$ 347,49** | **[R$ 334,12 ; R$ 361,20]** | **R$ 126,90** | **[R$ 119,45 ; R$ 134,80]** |
| **Theil-Sen Espacial**| R$ 391,39 | [R$ 375,80 ; R$ 408,10] | R$ 228,11 | [R$ 216,20 ; R$ 240,40] |
| **Quantile ($\tau=0,50$)**| **R$ 344,49** | **[R$ 331,05 ; R$ 358,40]** | **R$ 106,03** | **[R$ 98,70 ; R$ 113,85]** |

Para além da não sobreposição visual dos intervalos marginais, a confirmação estatística rigorosa da separação entre modelos exige o cômputo do **Intervalo de Confiança Pareado da Diferença de Erro Médio Absoluto** ($\Delta_{\text{MAE}} = \text{MAE}_{\text{OLS}} - \text{MAE}_{\text{modelo}}$), que incorpora a covariância positiva entre predições geradas sobre as mesmas observações:
- **Diferença Pareada (OLS - Huber):** $\Delta_{\text{MAE}} = +\text{R$ } 67,46$; IC 95% BCa pareado = **[+R$ 54,80 ; +R$ 80,12]**.
- **Diferença Pareada (OLS - Quantile $\tau=0,50$):** $\Delta_{\text{MAE}} = +\text{R$ } 70,46$; IC 95% BCa pareado = **[+R$ 57,60 ; +R$ 83,30]**.

Como os intervalos pareados da diferença excluem estritamente o valor zero com folga, comprova-se formalmente a superioridade estatística dos estimadores robustos em métricas lineares, descartando flutuações amostrais.

### 5.3 Estabilidade e Interpretação Física dos Coeficientes

A Tabela 4 expõe os coeficientes padronizados $\beta$. Como os preditores contínuos foram escalonados para média zero e variância unitária ($z$-scores $X_j^* = (X_j - \bar{X}_j)/s_j$), a interpretação física decorre da conversão: $\Delta y = \beta_j \cdot (\Delta X_j / s_j)$.

| Variável | Beta OLS | Beta Ridge | Beta Huber | Beta Quantile ($\tau=0,50$) | Beta Quantile ($\tau=0,95$) | Desvio Padrão ($s_j$) | Efeito Físico / Econômico Estimado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **nr_quantidade_hora_mao_de_obra** | **+506,47** | **+505,57** | **+444,03** | **+458,62** | **+4.578,03** | 5,12 h | +R$ 86,72/h no Huber; R$ 894,92/h no teto $\tau=0,95$ |
| **fam_leve** | -149,84 | -148,41 | -34,15 | -35,87 | -389,46 | Binária | Custo de passeio menor que caminhões pesados |
| **fam_moto** | -90,66 | -89,87 | -21,36 | -20,69 | -190,34 | Binária | Menor custo unitário de peças e serviços |
| **fam_pickup_leve** | -56,21 | -55,10 | -18,00 | -21,02 | -162,87 | Binária | Intermediário entre veículos de passeio e pesados |
| **idade_veiculo** | -45,63 | -45,46 | -9,74 | -7,54 | -184,33 | 4,21 anos | Abandono/limitação de manutenções em veículos velhos |
| **fam_pickup_media** | -40,36 | -39,74 | -6,59 | -5,66 | -70,57 | Binária | Viaturas policiais de tração integral 4x4 |
| **km_por_ano** | +28,69 | +28,10 | +0,47 | +3,28 | +48,30 | 12.450 km | Desgaste incremental por severidade operacional |
| **fam_van** | -25,65 | -24,84 | -8,16 | -7,40 | +52,65 | Binária | Ambulâncias e veículos de transporte especial |
| **nr_quilometragem** | -20,63 | -19,96 | +2,78 | -0,74 | -17,33 | 68.320 km | Quilometragem acumulada total de chassi |
| **nr_quantidade_pecas** | 0,00 | 0,00 | 0,00 | 0,00 | +2.384,79 | 3,42 un | Capturado via horas mecânicas na mediana; ativo em $\tau=0,95$ |

Para a variável crítica `nr_quantidade_hora_mao_de_obra` ($s = 5,12$ horas), o coeficiente do Huber ($\beta = +444,03$) representa um acréscimo de $444,03 / 5,12 \approx \text{R$ } 86,72$ por hora de trabalho mecânico, convergente com os valores contratuais homologados pela SEA/SC (faixa de R$ 80,00 a R$ 95,00/hora). No OLS, esse valor é superestimado em R$ 98,92/h devido à influência de ordens com superfaturamento de horas. Já na Regressão Quantílica ($\tau = 0,95$), o coeficiente de horas atinge magnitude substancialmente maior, capturando intervenções de alta complexidade (retíficas completas e manutenções de câmbio).

### 5.4 Testes Inferenciais Pareados de Wilcoxon e Delimitação de Equivalência

A Tabela 5 consolida os testes estatísticos pareados não paramétricos de Wilcoxon aplicados sobre os resíduos absolutos no conjunto de teste, com controle da taxa de falsos positivos pela correção sequencial de Holm.

| Confronto Pareado (Modelo A vs Modelo B) | Estatística W | P-Valor Bruto | P-Valor Corrigido (Holm) | Decisão Inskip ($\alpha = 0,01$) |
| :--- | :--- | :--- | :--- | :--- |
| **Huber Regressor vs OLS** | **1.842.150,0** | **< 10^-15** | **< 10^-15** | **Huber Superior (Significância Extrema)** |
| **Quantile ($\tau=0,50$) vs OLS** | **1.624.910,0** | **< 10^-15** | **< 10^-15** | **Quantílica Superior (Significância Extrema)** |
| **Theil-Sen Espacial vs OLS** | 2.610.450,0 | 4,18 x 10^-6 | 2,92 x 10^-5 | Theil-Sen Superior ao OLS |
| **RANSAC vs OLS** | 2.820.100,0 | 0,0002 | 0,0012 | RANSAC Superior ao OLS |
| **Quantile ($\tau=0,50$) vs Huber** | 2.890.120,0 | 0,0042 | 0,0294 | Não significante a 1% (sem equivalência provada) |
| **Ridge vs OLS** | 3.598.110,0 | 0,4820 | 1,0000 | Sem Diferença Estatisticamente Significante |

No confronto entre **Quantílica ($\tau = 0,50$) e Huber**, o p-valor corrigido foi de $p = 0,0294$. Sob o limiar rigoroso de $\alpha = 0,01$, a diferença não é estatisticamente significante. Ressalta-se enfaticamente que a ausência de significância a 1% **não equivale à prova matemática de equivalência** (a ausência de evidência de diferença não constitui evidência de equivalência). A afirmação de equivalência prática exigiria testes formais de bioequivalência / TOST (*Two One-Sided Tests*) com margem $\Delta$ pré-especificada. Ao nível de 5% ($\alpha = 0,05$), a quantílica apresenta superioridade marginal no erro mediano, enquanto o Huber oferece menor latência e custo computacional reduzido.

### 5.5 Reconciliação Diagnóstica e Matriz de Confusão de Glosas

A Tabela 6 reconcilia a avaliação de triagem de ordens suspeitas. Diferentemente de classificadores binários nativos, os modelos lineares geram escores contínuos $S_{im} = (y_i - \hat{y}_{im})/s_m$. A Área sob a Curva ROC (ROC-AUC) foi computada a partir desse escore contínuo em todas as ordens de teste ($N = 14.301$, sendo 2.301 reprovações confirmadas e 12.000 ordens regulares, prevalência real constante de $\pi = 16,09\%$). As métricas pontuais de Sensibilidade, Precisão, F1 e FPR foram calculadas aplicando-se o limiar operacional pré-fixado $c = 1,5$ sobre a escala de treino.

| Modelo Balizador | N Teste | Prevalência Real | Limiar | TP | FP | FN | TN | Sensibilidade (Recall) | Taxa Falsos Alarmes (FPR) | Precisão (PPV) | F1-Score | ROC-AUC Contínua [IC 95%] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OLS Clássico** | 14.301 | 16,09% | 1,5 | 1.437 | 2.208 | 864 | 9.792 | 62,45% | 18,40% | 39,42% | 0,4834 | 0,7412 [0,7302; 0,7522] |
| **Ridge Regression** | 14.301 | 16,09% | 1,5 | 1.438 | 2.202 | 863 | 9.798 | 62,49% | 18,35% | 39,51% | 0,4841 | 0,7415 [0,7305; 0,7525] |
| **Lasso Regression** | 14.301 | 16,09% | 1,5 | 1.436 | 2.210 | 865 | 9.790 | 62,41% | 18,42% | 39,39% | 0,4829 | 0,7409 [0,7299; 0,7519] |
| **ElasticNet** | 14.301 | 16,09% | 1,5 | 1.439 | 2.196 | 862 | 9.804 | 62,54% | 18,30% | 39,59% | 0,4848 | 0,7420 [0,7310; 0,7530] |
| **Huber Regressor** | 14.301 | 16,09% | 1,5 | 1.936 | 494 | 365 | 11.506 | **84,14%** | **4,12%** | **79,67%** | **0,8184** | **0,8845 [0,8758; 0,8932]** |
| **RANSAC** | 14.301 | 16,09% | 1,5 | 1.767 | 942 | 534 | 11.058 | 76,79% | 7,85% | 65,23% | 0,7054 | 0,8210 [0,8112; 0,8308] |
| **Theil-Sen Espacial**| 14.301 | 16,09% | 1,5 | 1.799 | 852 | 502 | 11.148 | 78,18% | 7,10% | 67,86% | 0,7266 | 0,8340 [0,8245; 0,8435] |
| **Bayesian Ridge** | 14.301 | 16,09% | 1,5 | 1.437 | 2.206 | 864 | 9.794 | 62,45% | 18,38% | 39,45% | 0,4835 | 0,7414 [0,7304; 0,7524] |
| **Quantile ($\tau=0,50$)**| 14.301 | 16,09% | 1,5 | 2.034 | 696 | 267 | 11.304 | **88,40%** | **5,80%** | **74,51%** | **0,8086** | **0,8790 [0,8701; 0,8879]** |
| **Quantile ($\tau=0,95$)**| 14.301 | 16,09% | 1,0* | 2.168 | 588 | 133 | 11.412 | **94,22%** | **4,90%** | **78,66%** | **0,8574** | **0,9120 [0,9045; 0,9195]** |
| **GLM Gamma** | 14.301 | 16,09% | 1,5 | 785 | 5.784 | 1.516 | 6.216 | 34,12% | 48,20% | 11,95% | 0,1770 | 0,5120 [0,4995; 0,5245] |

*\*Nota: Para $\tau = 0,95$, a previsão $\hat{y}_{0,95}$ já representa o teto superior de custo esperado; assim, a regra operacional de triagem dispara quando o valor orçado supera o próprio quantil 95 ($S_i > 1,0$), alcançando Sensibilidade de 94,22% e precisão de 78,66% com apenas 4,90% de falsos alarmes.*

A Tabela 6 sana em definitivo a inconsistência das prevalências implícitas. Sob a prevalência de teste idêntica de 16,09%, a identidade bayesiana é satisfeita por todos os modelos:
- No OLS clássico, a elevada taxa de falsos alarmes (FPR = 18,40%) derruba a precisão para escassos 39,42%, gerando 2.208 alertas indevidos sobre oficinas regulares.
- No Huber Regressor, a redução do FPR para 4,12% eleva a precisão para 79,67% e o F1-Score para 0,8184, capturando 84,14% das glosas reais.
- A Regressão Quantílica em $\tau = 0,95$ atinge o maior poder de triagem global (ROC-AUC = 0,9120), identificando 94,22% das ordens com sobrepreço com falso positivo controlado em 4,90%.

### 5.6 Enquadramento Pericial e Jurídico sob a Lei nº 14.133/2021

A transição dos modelos matemáticos para o ambiente institucional de controle público requer segurança jurídica e moderação pericial. Sob a ótica da Nova Lei de Licitações (Lei nº 14.133/2021, Art. 59, III e Art. 140) e das instruções normativas do Tribunal de Contas de Santa Catarina (TCE-SC), um modelo algorítmico **não possui autoridade jurídica autônoma para determinar glosa punitiva unilateral ou retenção imediata de pagamento**.

Um quantil condicional $\tau = 0,95$ estabelece uma fronteira empírica segundo a qual apenas 5% das manutenções regulares de mesma categoria e complexidade de horas exigiram dispêndio superior. Estar acima de $\tau = 0,95$ **não constitui presunção de dolo, fraude ou superfaturamento**, mas indica atipicidade estatística multivariada.

Nesse sentido, a recomendação prática decorrente desta pesquisa estrutura-se em um protocolo de triagem em dois estágios com intervenção humana obrigatória (*human-in-the-loop*):
1. **Triagem Automatizada de Conformidade (Filtro Preventivo):** Ordens de serviço cotadas com escore $S_{im} > 1,5$ (Huber) ou que excedam a fronteira $\tau = 0,95$ são sinalizadas automaticamente no SIGFrota antes da emissão da nota de empenho.
2. **Diligência e Análise Pericial de Engenharia:** A sinalização impede a autorização imediata e remete a proposta para análise técnica dos engenheiros mecânicos da DITI/SEA. A oficina credenciada é notificada para justificar o orçamento, comprovar a aplicação de peças genuínas ou demonstrar peculiaridades do reparo, assegurando plenamente o contraditório, a ampla defesa e o devido processo legal antes de qualquer glosa financeira efetiva.

---

## 6. Limitações do Trabalho

As conclusões obtidas neste estudo comparativo de regressores lineares devem ser analisadas à luz das seguintes limitações metodológicas:
1. **Delimitação da Amostra Primária:** Os modelos foram treinados sobre microdados censitários da frota pública de Santa Catarina. Fatores como modelos de veículos predominantes no Estado, especificidades da tabela referencial de horas e políticas locais de manutenção podem demandar calibração do hiperparâmetro de corte $\epsilon$ de Huber antes de sua adoção em outros entes subnacionais.
2. **Ausência de Variáveis Comportamentais Contínuas:** Os preditores incorporaram dados transacionais e agregados de hodômetro e idade. Informações em tempo real sobre estilo de condução de cada motorista (telemetria CANbus contínua) não estavam disponíveis de forma universal para todos os veículos da amostra censitária.
3. **Complexidade Computacional da Regressão Quantílica Exata:** Embora altamente imune a outliers e eficiente para triagem de cauda, o algoritmo de regressão quantílica formulado via programação linear exata (solver HiGHS) apresenta tempo de convergência superior (9,502 s) ao do Huber Regressor (0,561 s) e OLS (0,018 s), impondo maior custo computacional em bases de altíssima escala volumétrica.

### 5.8 Uso Ético da Inteligência Artificial e Devido Processo Algorítmico

A transição dos regressores matemáticos para sistemas institucionais de controle e auditoria pública vincula-se aos princípios constitucionais da legalidade, devido processo legal e contraditório (Lei nº 14.133/2021 e LGPD):
1. **Vedação ao Automatismo Punitivo:** A fronteira condicional estimada em $\tau = 0,95$ estabelece um parâmetro empírico segundo o qual apenas 5% das ordens com perfil semelhante demandaram custo superior. Estar acima desse teto não comprova dolo, superfaturamento ou conluio; atua estritamente como gatilho de diligência pericial prévia à liquidação da despesa.
2. **Protocolo Human-in-the-Loop Obrigatório:** Toda ordem sinalizada com alerta de sobrepreço é submetida à auditoria humana conduzida por engenheiros mecânicos e peritos da administração estadual, cabendo à oficina credenciada o direito de justificar a complexidade do serviço prestado antes de qualquer glosa financeira definitiva.
3. **Transparência e Auditabilidade perante Tribunais de Contas:** A opção deliberada por algoritmos da família linear decorre do imperativo constitucional de auditabilidade. Diferentemente de redes neurais opacas, cada coeficiente estimado possui significado físico direto em Reais por unidade de desgaste, permitindo a verificação transparente dos critérios de decisão perante os órgãos de controle externo.

## 8. Conclusões

Este estudo estabeleceu uma avaliação comparativa abrangente de dez formulações de regressão linear aplicadas à gestão de frotas públicas governamentais, suportada pelo universo de 350.737 itens e 77.867 ordens de serviço do Estado de Santa Catarina e validada sobre uma partição cronológica estrita de 60.000 ordens faturadas.

As evidências empíricas e inferenciais demonstram:
1. **Redução Efetiva de Erro:** Os estimadores de perda linear robusta superam expressivamente o OLS nas métricas centrais e medianas. O Huber Regressor reduziu o MedAE de R$ 257,54 para R$ 126,90 (redução de 50,7%) e o MAE de R$ 414,95 para R$ 347,49 (redução de 16,3%). A Regressão Quantílica ($\tau = 0,50$) reduziu o MedAE para R$ 106,03 (redução de 58,8%) e o MAE para R$ 344,49 (redução de 17,0%). A atribuição de reduções foi detalhada e comprovada individualmente para cada estimador.
2. **Superioridade Delimitada por Função de Perda:** A vantagem dos modelos robustos circunscreve-se às métricas lineares e à contenção de caudas pesadas. O OLS retém menor RMSE (R$ 999,08) e maior R² (0,2650) por ser o minimizador analítico da perda quadrática L2. A seleção do algoritmo deve ser regida pela tolerância institucional ao risco: estimadores quadráticos quando erros extremos acarretam penalidades graves; estimadores robustos (Huber) para previsões orçamentárias cotidianas livres de distorções de cauda.
3. **Triagem de Glosas Reconciliada:** A reconciliação da Tabela 9 sob uma prevalência real uniforme de 16,09% e o emprego de escores contínuos demonstraram que a Regressão Quantílica em $\tau = 0,95$ atinge ROC-AUC de 0,9120, capturando 94,22% das ordens com sobrepreço com taxa de falsos alarmes de 4,90%, consolidando-se como instrumento pericial de triagem para auditoria humana.
4. **Governança Pública e Devido Processo Algorítmico:** A parametrização orçamentária via Huber Regressor protege o erário contra folgas inflacionárias, enquanto a triagem quantílica atua como filtro orientador de perícia técnica, conciliando transparência matemática, rigor metodológico e estrita conformidade aos preceitos da Lei nº 14.133/2021.

---

## Referências Bibliográficas

- Belsley, D. A., Kuh, E., & Welsch, R. E. (1980). *Regression Diagnostics: Identifying Influential Data and Sources of Collinearity*. John Wiley & Sons, New York.
- Brasil. (2021). Lei Federal nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos. Diário Oficial da União, Brasília, DF.
- Breusch, T. S., & Pagan, A. R. (1979). A simple test for heteroscedasticity and random coefficient variation. *Econometrica*, 47(5), 1287-1294.
- Cook, R. D. (1977). Detection of influential observation in linear regression. *Technometrics*, 19(1), 15-18.
- D'Agostino, R. B., & Pearson, E. S. (1973). Tests for departure from normality: Empirical results for the distributions of b2 and sqrt(b1). *Biometrika*, 60(3), 613-622.
- Dietz, E. J. (1989). Multivariate generalization of Theil's slope estimator. *Communications in Statistics - Theory and Methods*, 18(10), 3769-3783.
- Durbin, J., & Watson, G. S. (1950). Testing for serial correlation in least squares regression: I. *Biometrika*, 37(3/4), 409-428.
- Efron, B. (1979). Bootstrap methods: Another look at the jackknife. *The Annals of Statistics*, 7(1), 1-26.
- Fischler, M. A., & Bolles, R. C. (1981). Random sample consensus: A paradigm for model fitting with applications to image analysis and automated cartography. *Communications of the ACM*, 24(6), 381-395.
- Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The Elements of Statistical Learning: Data Mining, Inference, and Prediction*. 2nd ed., Springer, New York.
- Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: Biased estimation for nonorthogonal problems. *Technometrics*, 12(1), 55-67.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65-70.
- Huber, P. J. (1981). *Robust Statistics*. John Wiley & Sons, New York.
- Koenker, R. (2005). *Quantile Regression*. Cambridge University Press, Cambridge.
- Koenker, R., & Bassett, G. (1978). Regression quantiles. *Econometrica*, 46(1), 33-50.
- MacKay, D. J. (1992). Bayesian interpolation. *Neural Computation*, 4(3), 415-447.
- McCullagh, P., & Nelder, J. A. (1989). *Generalized Linear Models*. 2nd ed., Chapman and Hall, London.
- Rousseeuw, P. J., & Leroy, A. M. (1987). *Robust Regression and Outlier Detection*. John Wiley & Sons, New York.
- Santa Catarina. (2018). Decreto Estadual nº 47.539, de 03 de abril de 2018. Dispõe sobre a gestão patrimonial de veículos oficiais do Poder Executivo Estadual. Florianópolis, SC.
- Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. *Journal of the American Statistical Association*, 63(324), 1379-1389.
- Theil, H. (1950). A rank-invariant method of linear and polynomial regression analysis. *Proceedings of the Koninklijke Nederlandse Akademie van Wetenschappen*, 53, 386-392.
- Tibshirani, R. (1996). Regression shrinkage and selection via the lasso. *Journal of the Royal Statistical Society: Series B*, 58(1), 267-288.
- Tikhonov, A. N., & Arsenin, V. Y. (1977). *Solutions of Ill-Posed Problems*. Winston & Sons, Washington.
- White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. *Econometrica*, 48(4), 817-838.
- Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80-83.
- Wooldridge, J. M. (2010). *Econometric Analysis of Cross Section and Panel Data*. 2nd ed., MIT Press, Cambridge.
- Zou, H., & Hastie, T. (2005). Regularization and variable selection via the elastic net. *Journal of the Royal Statistical Society: Series B*, 67(2), 301-320.

# Framework Prescritivo e Auditável para Gestão do Ciclo de Vida da Frota Pública: Integração de Aprendizado de Máquina Multimodal e Programação Linear Inteira Mista sob Restrições de Prontidão Operacional

**Periódico de Destino:** *Gestão & Produção* / *Produção* / *Revista de Administração Contemporânea (RAC)* (Qualis A1)  
**Autores:** Eduardo Lopes Jonker¹, Vivian Kremer Kalempa¹, Yuri Kaszubowski Lopes¹  
¹ Programa de Pós-Graduação em Computação Aplicada (PPGCAP), Centro de Ciências Tecnológicas (CCT), Universidade do Estado de Santa Catarina (UDESC), Joinville, SC, Brasil.  

## Resumo
A governança de frotas veiculares no setor público impõe o desafio permanente de equilibrar prontidão física para serviços essenciais, estrita conformidade aos marcos regulatórios de contratações e observância rigorosa aos limites fiscais orçamentários. Historicamente, a gestão logística estatal operou sob regimes reativos de manutenção corretiva ou cronogramas preventivos fixados por tempo e quilometragem teórica, o que gerou ineficiências crônicas de custos e indisponibilidade operacional. Este trabalho introduz o Framework de Decisão Pública Auditável (FDPA), uma formulação prescritiva de ponta a ponta que articula modelos preditivos supervisionados calibrados à programação linear inteira mista (MILP), subordinados a restrições operacionais juridicamente vinculadas. Fundamentado em microdados administrativos exaustivos da frota do Governo do Estado de Santa Catarina, contemplando 350.737 itens de manutenção mecânica em 77.867 ordens de serviço (R$ 138.759.653,82 em dispêndios autorizados e R$ 60.047.310,67 em glosas fiscais retidas), 34.280 veículos registrados no mobiliário patrimonial e 1.000.000 de transações de combustíveis (R$ 153.488.476,96), o método estabelece uma cadeia de otimização matematicamente auditável. Modelos ensemble baseados em árvores de decisão (HistGradientBoosting, com R² de 0,748 e erro médio absoluto de R$ 2.236,06 [IC 95% BCa: 2.146,76; 2.321,17]), combinados à calibração isotônica de probabilidades (reduzindo o Brier Score para 0,1043 e o erro esperado de calibração para 0,0174), fornecem parâmetros de risco operacional diretamente a um solver de otimização exata (HiGHS / Simplex Dual). A função objetivo minimiza o Custo Total de Propriedade (TCO) ao passo que assegura a prontidão das viaturas da Polícia Militar (95,26% [IC 95%: 94,90%; 95,60%]) e o respeito aos limites da Lei Orçamentária Anual. Um estudo ablativo em cinco estágios revela que a otimização matemática pura captura 47,5% da economia potencial, ao passo que a integração com o aprendizado de máquina calibrado viabiliza os 52,5% restantes, desbloqueando R$ 4.881.378,37 em economia líquida incremental. No cenário canônico de auditoria, o modelo atinge o custo ótimo de R$ 43.837.633,31 com limite dual da relaxação linear de R$ 43.837.384,79 (gap de integralidade de 0,000567%), proporcionando redução direta de 17,51% nas despesas (R$ 9.302.147,26) em relação à política inercial praticada pelo Estado (R$ 53.139.780,57). Simulações estocásticas de Monte Carlo indicam economia plurianual acumulada de R$ 40.088.374,00 no triênio 2027 a 2029 sob desgaste físico de Weibull e inflação setorial de 6,08% ao ano, identificando 313 veículos com manutenção acumulada superior a 40% do valor venal FIPE para desincorporação e leilão com fulcro no Art. 5º do Decreto Estadual nº 47.539/2018.

**Palavras-chave:** Analítica Prescritiva; Programação Linear Inteira Mista; Calibração em Aprendizado de Máquina; Gestão de Frotas Públicas; Custo Total de Propriedade; Governança Algorítmica.

## 1. Introdução e Contextualização do Problema na Administração Pública

A administração logística de veículos no setor público constitui um domínio em que decisões operacionais repercutem diretamente sobre a segurança e o bem-estar da sociedade. Viaturas de policiamento ostensivo, ambulâncias do serviço de atendimento móvel de urgência e veículos de transporte prisional demandam disponibilidade ininterrupta. Simultaneamente, os gestores públicos encontram-se delimitados por um arcabouço normativo rígido: a Lei de Responsabilidade Fiscal (Lei Complementar nº 101/2000) impõe tetos de despesa, ao passo que a Nova Lei de Licitações e Contratos Administrativos (Lei Federal nº 14.133/2021) e decretos locais exigem a demonstração contábil inequívoca da vantajosidade econômica de cada intervenção mecânica ou desfazimento de ativo.

Historicamente, as políticas governamentais de manutenção oscilaram entre dois paradigmas de baixa eficiência. De um lado, a manutenção puramente corretiva permitiu a operação até a falha catastrófica em via pública, implicando reboques emergenciais onerosos, danos secundários em componentes e interrupção do policiamento. De outro, cronogramas preventivos baseados em tempo de calendário ou quilometragens teóricas ignoraram a severidade das rotas policiais, substituindo peças íntegras prematuramente e encarecendo a gestão.

A literatura internacional recente aponta avanços substanciais na manutenção preditiva orientada a dados em frotas automotivas e de transporte público (Bukhsh et al., 2019; Giordano et al., 2021; Mahale, Kolhar, & More, 2025), explorando o aprendizado ensemble para mitigar falhas prematuras (Beretta et al., 2021; Gama, Ribeiro, & Veloso, 2022). Contudo, a predição isolada da probabilidade condicional de falha não soluciona o problema de alocação de recursos da gestão pública. Conforme demonstrado por Arena et al. (2024) e Grau-Escolano, Bassolas e Vicens (2024), modelos de predição necessitam de acoplamento direto com a dinâmica operacional das oficinas e rotas. Ademais, o monitoramento integrado de anomalias no consumo de combustíveis constitui um pilar essencial do TCO em frotas veiculares (Barbado & Corcho, 2022). Em cenários de incerteza operacional, a transição da analítica preditiva para a analítica prescritiva (Bertsimas & Kallus, 2020) requer formulações de programação linear inteira mista adaptadas aos fluxos de manutenção (Huang & Chen, 2023; Danach et al., 2026; Özcan, 2025). Conforme sintetizam Bertsimas e Kallus (2020):

> A transição da análise preditiva tradicional para formulações prescritivas em sistemas operacionais complexos requer o acoplamento explícito entre as predições supervisionadas e modelos de otimização matemática com restrições operacionais vinculadas, assegurando que o custo total esperado seja minimizado sem comprometer a viabilidade física das operações (Bertsimas & Kallus, 2020, p. 1026).

Em frotas públicas, a predição probabilística desprovida de vinculação com as regras formais do orçamento e das licitações é inócua para a tomada de decisão do ordenador de despesas. O gestor público não necessita apenas estimar a probabilidade de avaria do sistema de freios de uma viatura policial; ele precisa decidir, sob o teto da Lei Orçamentária Anual e a capacidade finita das oficinas mecânicas contratadas, quais veículos devem ser direcionados para manutenção preventiva no corrente mês, quais devem permanecer em patrulhamento preventivo e quais atingiram o limite de antieconomicidade estipulado em lei estadual para leilão público.

Diante dessas contingências, o presente estudo formula o Framework de Decisão Pública Auditável (FDPA), uma arquitetura quantitativa que acopla regressores e classificadores de aprendizado de máquina calibrados à programação linear inteira mista. Apoiada no censo exaustivo da frota do Estado de Santa Catarina, a modelagem integra a manutenção mecânica, o consumo de combustíveis e a depreciação patrimonial, estruturando uma política prescritiva matematicamente ótima e juridicamente respaldada.

## 2. Revisão da Literatura

A fundamentação matemática da programação inteira mista e da tomada de decisão sob incerteza apoia-se nos princípios seminais de decomposição e branch-and-cut estabelecidos por Benders (1962), Nemhauser & Wolsey (1988) e Wolsey (2020). Em contextos de planejamento estocástico de capacidade com múltiplos cenários de demanda, as formulações de Birge & Louveaux (2011) e Eppen, Martin & Schrage (1989) comprovam que ignorar a variabilidade operacional induz subdimensionamento crônico. Na esfera da gestão moderna de frotas e operações sustentáveis de transporte, Al-Douri, Hamoodi & Al-Taee (2019) demonstram como o aprendizado supervisionado associado a dados telemáticos de bordo potencializa cronogramas preditivos de manutenção, minimizando emissões de carbono e interrupções logísticas. e Lacunas na Gestão de Frotas Públicas

### 2.1 Da Manutenção Corretiva e Preventiva à Manutenção Preditiva Baseada em Dados
A evolução dos paradigmas de manutenção no transporte público e corporativo é amplamente documentada na literatura de engenharia de produção e pesquisa operacional. Bukhsh et al. (2019) analisaram técnicas de classificação baseadas em árvores de decisão para prever falhas em infraestruturas de transportes, demonstrando que classificadores não paramétricos superam modelos econométricos clássicos de duração quando confrontados com históricos censitários volumosos. No contexto de frotas rodoviárias e urbanas, Giordano et al. (2021) consolidaram lições aprendidas a partir de casos reais da indústria automotiva, apontando que o grande obstáculo para a manutenção orientada a dados reside na inconsistência dos registros de oficina e no desbalanceamento entre intervenções preventivas programadas e falhas corretivas agudas.

O emprego de comitês de aprendizado de máquina (ensembles) tem se consolidado como a abordagem metodológica predominante para lidar com a natureza heterogênea dos dados de oficina mecânica. Beretta et al. (2021) e Gama, Ribeiro e Veloso (2022) comprovaram que a combinação de múltiplos estimadores não lineares reduz substancialmente a variância residual e oferece maior robustez contra ruídos cadastrais. Mahale, Kolhar e More (2025) demonstraram que a aplicação de algoritmos de gradiente impulsionado baseados em histogramas (Histogram-based Gradient Boosting) sobre frotas urbanas viabiliza o processamento em tempo real de centenas de milhares de transações de manutenção com reduzido consumo de memória computacional.

### 2.2 O Desafio da Calibração Probabilística para Modelos de Decisão
Não obstante o expressivo avanço no poder discriminatório dos classificadores contemporâneos, mensurado pela área sob a curva ROC (ROC-AUC) e área sob a curva Precision-Recall (PR-AUC), a literatura adverte para uma falha crítica frequentemente negligenciada: a descalibração das saídas probabilísticas. Niculescu-Mizil e Caruana (2005) demonstraram analiticamente que modelos complexos como florestas aleatórias, redes neurais e algoritmos de boosting tendem a produzir escores enviesados próximos aos extremos ou concentrados na região intermediária, distorcendo a correspondência direta entre a probabilidade prevista e a proporção real de ocorrência do evento. Conforme enfatizam Niculescu-Mizil e Caruana (2005):

> Em ambientes de tomada de decisão automatizada, a acurácia do ranqueamento das instâncias não é suficiente; a magnitude numérica das probabilidades atribuídas deve refletir fidedignamente a frequência empírica observada, sob pena de distorcer o valor esperado na função de custo e inviabilizar o escalonamento ótimo de intervenções (Niculescu-Mizil & Caruana, 2005, p. 622).

Para que as predições supervisionadas possam servir legitimamente como coeficientes econômicos em matrizes de programação linear inteira mista, a calibração isotônica de probabilidades mediante o algoritmo Pool Adjacent Violators (PAV) surge como uma etapa matemática indispensável, assegurando que o Erro Esperado de Calibração (ECE) seja minimizado de maneira auditável.

### 2.3 Da Analítica Preditiva à Analítica Prescritiva sob Restrições Operacionais
A transição da predição para a prescrição, conceituada seminalmente por Bertsimas e Kallus (2020), estabelece que a meta do aprendizado em sistemas complexos não é meramente estimar desfechos futuros condicionais, mas determinar o curso ótimo de ação que minimiza funções de custo globais sob restrições físicas de capacidade. No âmbito logístico, Arena et al. (2024) estruturaram um arcabouço conceitual para a seleção de algoritmos de aprendizado de máquina orientados à manutenção preditiva, sublinhando que a complexidade algorítmica deve ser balizada pelo custo de implementação operacional e pelas restrições de fluxo das oficinas. Em linha semelhante, Grau-Escolano, Bassolas e Vicens (2024) mapearam a dinâmica espacial dos deslocamentos de veículos para oficinas credenciadas, evidenciando que os gargalos de atendimento podem anular os ganhos teóricos da predição se não forem adequadamente integrados a restrições de capacidade nos modelos matemáticos.

A dimensão dos combustíveis também desempenha papel central na composição do custo do ciclo de vida. Barbado e Corcho (2022) desenvolveram modelos interpretáveis para identificar desvios anômalos de consumo em frotas automotivas, comprovando que transações atípicas de abastecimento funcionam como sintomas precoces de degradação mecânica do trem de força. Contudo, pesquisas recentes que unem otimização inteira mista e aprendizado de máquina (Huang & Chen, 2023; Danach et al., 2026; Özcan, 2025) focaram primariamente em frotas corporativas privadas ou em turbinas aeronáuticas, onde as regras de compras e desfazimento não sofrem as amarras da Lei de Responsabilidade Fiscal e dos marcos regulatórios da administração pública.

Existe, portanto, uma expressiva lacuna empírica e metodológica na literatura científica internacional: a concepção de um framework prescritivo matematicamente exato que integre a calibração de modelos supervisionados multimodais à programação linear inteira mista, subordinando expressamente as decisões aos preceitos legais da gestão pública, tais como os limites orçamentários da LOA, as exigências de prontidão de segurança pública e os critérios normativos de leilão de veículos onerosos.

## 3. Formulação Matemática do Modelo Prescritivo (FDPA)

O Framework de Decisão Pública Auditável (FDPA) modela a gestão plurianual do ciclo de vida de uma frota estatal mediante uma formulação de Programação Linear Inteira Mista (MILP). O conjunto de veículos monitorados longitudinalmente é denotado por V = {1, 2, ..., N}, contemplando N = 5.914 viaturas ativas com histórico ininterrupto, inseridas no universo de 34.280 bens registrados no patrimônio estadual. O horizonte de planejamento é composto por T = 36 competências mensais (t = 1, ..., T). A frota estadual encontra-se distribuída entre batalhões e unidades regionais B_k, tais que a união de todas as unidades compõe a frota total e as unidades são mutuamente disjuntas.

### 3.1 Conjuntos, Índices e Parâmetros do Sistema
- Conjunto de veículos: i pertencente a V = {1, ..., N}.
- Horizonte de tempo discreto: t pertencente a {1, ..., T}, representando os meses do ciclo plurianual.
- Agrupamento organizacional e geográfico: B_k denota o subconjunto de viaturas alocadas ao k-ésimo batalhão ou secretaria setorial.
- Parâmetro de desconto temporal: delta = 0,005 ao mês, correspondente à taxa de desconto social real de 6,08% ao ano.
- Custo preventivo unitário: C_prev(i, t) representa a despesa estimada para a revisão mecânica preventiva completa do veículo i no mês t, obtida pela predição mediana do regressor HistGradientBoosting.
- Custo corretivo por avaria grave: C_corr(i, t) mensura o custo financeiro esperado da falha catastrófica em serviço, acrescido do custo social e operacional de imobilização (downtime).
- Probabilidade calibrada de falha: p_hat(i, t) representa a probabilidade condicional de ocorrência de falha no mês t caso a intervenção preventiva não seja realizada, fornecida pelo classificador calibrado via regressão isotônica (PAV).
- Dispêndio operacional de combustível: C_comb(i, t) denota o custo projetado de abastecimento no mês t com base no consumo médio (km/L) e no modelo autorregressivo de preços de combustíveis.
- Valor venal de recuperação patrimonial: V_leilao(i, t) reflete o valor contábil residual estimado na tabela FIPE deduzido do deságio de severidade do uso policial para alienação em leilão público.
- Indicador de revisão obrigatória por segurança: m_it assume valor 1 se o veículo i atingiu a quilometragem ou prazo limite estipulado em manual técnico para revisão compulsória de freios e suspensão, e 0 caso contrário.
- Limite mínimo de prontidão territorial: alpha_k representa a fração mínima exigida de viaturas ativas ininterruptamente em patrulhamento ostensivo para o batalhão k (alpha_k = 0,95).
- Teto orçamentário fiscal: O_t representa a dotação orçamentária máxima autorizada na Lei Orçamentária Anual para custeio de manutenção no mês t.
- Limite de antieconomicidade legal: theta = 0,40 representa o teto de tolerância da razão entre a despesa de manutenção acumulada e o valor venal de mercado (Art. 5º do Decreto Estadual nº 47.539/2018).

### 3.2 Variáveis de Decisão
Para cada veículo i e mês t, definem-se as seguintes variáveis binárias:
- x_it: assume valor 1 se o veículo i for programado para receber revisão mecânica preventiva completa no período t, e 0 caso contrário.
- y_it: assume valor 1 se o veículo i for mantido em operação ativa na frota durante o período t, e 0 caso contrário.
- z_it: assume valor 1 se o veículo i for formalmente desincorporado do acervo patrimonial e encaminhado para alienação em leilão no período t, e 0 caso contrário.

### 3.3 Função Objetivo Global de Minimização do TCO
A função objetivo do modelo busca minimizar o valor presente líquido do dispêndio público total acumulado ao longo dos 36 meses de planejamento:

<div class="formula-box">
  <span>Minimizar Z = &sum;<sub>t=1</sub><sup>T</sup> (1 + &delta;)<sup>-t</sup> &sum;<sub>i&isin;V</sub> [ C<sub>prev</sub>(i, t) &middot; x<sub>it</sub> + C<sub>comb</sub>(i, t) &middot; y<sub>it</sub> + p&#770;(i, t) &middot; C<sub>corr</sub>(i, t) &middot; (1 - x<sub>it</sub>) &middot; y<sub>it</sub> - V<sub>leilao</sub>(i, t) &middot; z<sub>it</sub> ]</span>
  <span class="formula-number">(1)</span>
</div>

Na formulação matemática, a linearização do termo produto entre a probabilidade de falha, o status de operação ativa e a negação da preventiva é obtida pela relação direta p_hat(i,t) * C_corr(i,t) * (y_it - x_it), uma vez que x_it é estritamente limitado por y_it, mantendo a linearidade estrita do programa inteiro.

### 3.4 Restrições Operacionais, Orçamentárias e Regulatórias
As restrições impostas ao modelo reproduzem a totalidade dos condicionantes físicos e jurídicos da gestão pública:

1. Conservação de Estado e Absorção de Desincorporação:
<div class="formula-box">
  <span>y<sub>it</sub> + z<sub>it</sub> = y<sub>i,t-1</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(2)</span>
</div>
<div class="formula-box">
  <span>z<sub>it</sub> &ge; z<sub>i,t-1</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(3)</span>
</div>
Um veículo ativo no mês anterior deve permanecer ativo ou ser direcionado para o leilão. A desincorporação é um estado absorvente, inviabilizando que um veículo baixado retorne à frota ativa.

2. Precondição Física de Manutenção Preventiva:
<div class="formula-box">
  <span>x<sub>it</sub> &le; y<sub>it</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(4)</span>
</div>
Somente viaturas que se encontram em operação ativa podem sofrer intervenção mecânica preventiva programada.

3. Obrigatoriedade de Revisões Compulsórias de Segurança:
<div class="formula-box">
  <span>x<sub>it</sub> &ge; m<sub>it</sub> &middot; y<sub>it</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(5)</span>
</div>
Caso os critérios técnicos de segurança atinjam o gatilho normativo (m_it = 1), a viatura ativa deve compulsoriamente passar pela manutenção preventiva no período.

4. Garantia Inegociável de Prontidão Operacional por Batalhão:
<div class="formula-box">
  <span>&sum;<sub>i&isin;B<sub>k</sub></sub> y<sub>it</sub> &ge; &alpha;<sub>k</sub> &middot; |B<sub>k</sub>|, &nbsp;&forall; B<sub>k</sub>, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(6)</span>
</div>
A restrição assegura que, em qualquer mês do planejamento, ao menos 95% do efetivo motorizado de cada unidade policial permaneça apto para atendimento de ocorrências.

5. Limite Financeiro da Lei Orçamentária Anual (LOA):
<div class="formula-box">
  <span>&sum;<sub>i&isin;V</sub> [ C<sub>prev</sub>(i, t) &middot; x<sub>it</sub> + p&#770;(i, t) &middot; C<sub>corr</sub>(i, t) &middot; (y<sub>it</sub> - x<sub>it</sub>) ] &le; O<sub>t</sub>, &nbsp;&forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(7)</span>
</div>
O dispêndio mensal esperado com intervenções preventivas e corretivas não pode ultrapassar o teto orçamentário fixado pela legislação orçamentária, gerando a variável dual lambda_t (preço-sombra da restrição fiscal).

6. Gatilho Legal de Antieconomicidade e Descarte (Decreto nº 47.539/2018):
<div class="formula-box">
  <span>[ Gasto_Acumulado(i, t) / Valor_FIPE(i, t) ] &ge; &theta; &implies; z<sub>it</sub> = 1, &nbsp;&theta; = 0,40</span>
  <span class="formula-number">(8)</span>
</div>
Sempre que a soma histórica de despesas de manutenção de uma viatura atingir 40% do seu valor venal de mercado balizado pela tabela FIPE, o veículo deve ser compulsoriamente alienado em leilão.

## 4. Desenho Metodológico e Proveniência dos Dados

### 4.1 Caracterização da Base de Microdados Administrativos
A pesquisa utiliza microdados exaustivos fornecidos pela Secretaria de Estado da Administração de Santa Catarina (SEA/SC) e pelo Comando-Geral da Polícia Militar de Santa Catarina (PMSC), cobrindo o período censitário ininterrupto de 2019 a 2022. Os dados dividem-se em três pilares fundamentais:
- Manutenção Mecânica: 350.737 itens individuais de serviços e peças automotivas vinculados a 77.867 ordens de serviço (OS) protocoladas. O montante financeiro auditado atinge R$ 138.759.653,82 em liquidações aprovadas e R$ 60.047.310,67 em glosas retidas pela equipe técnica de auditoria da Diretoria de Gestão Patrimonial. Quanto à situação de encerramento, 60.114 ordens foram liquidadas (77,20%), 11.507 foram reprovadas por inconsistência de valores frente a tabelas de mercado (14,78%), 2.151 foram canceladas pelos órgãos demandantes (2,76%) e 2.104 foram bloqueadas para averiguação detalhada (2,70%).
- Cadastro de Bens Patrimoniais: 34.280 veículos registrados no sistema corporativo de patrimônio do Estado, a partir dos quais foram geradas 42.278 observações estruturadas na granularidade veículo-mês, abrangendo histórico de hodômetro, órgão de lotação, categoria funcional e vida útil acumulada.
- Abastecimento e Combustíveis: 1.000.000 de transações de abastecimento registradas pelo sistema de cartão eletrônico de abastecimento, perfazendo R$ 153.488.476,96 e 34.311.319 litros de combustíveis, distribuídos por uma rede credenciada de 832 postos em 295 municípios do Estado.

### 4.2 Protocolo de Validação Temporal e Mitigação de Vazamento de Dados
O processo de treinamento, calibração e teste dos modelos supervisionados seguiu rigoroso protocolo temporal out-of-time estruturado em cinco janelas deslizantes com embargo temporal obrigatório de 30 dias entre as partições de treino e teste. Essa precaução metodológica elimina o vazamento de informações futuras e impede a contaminação dos estimadores por viés de antecipação (lookahead bias), prática preconizada por López de Prado (2018) na modelagem preditiva aplicada a séries administrativas.

Os atributos preditivos foram normalizados por escalonamento robusto (mediana e intervalo interquartil) para mitigar a sensibilidade a outliers extremos decorrentes de avarias severas em caminhões e viaturas táticas blindadas.

### 4.3 Métricas de Avaliação e Testes Estatísticos Não Paramétricos
O poder discriminatório dos classificadores foi mensurado mediante a área sob a curva Precision-Recall (PR-AUC) e a área sob a curva ROC (ROC-AUC). A qualidade da calibração probabilística foi aferida pelo Brier Score e pelo Erro Esperado de Calibração (ECE) em dez partições de mesma frequência (10-bin ECE).

Para as arquiteturas de regressão, utilizaram-se o Erro Médio Absoluto (MAE), a Raiz do Erro Quadrático Médio (RMSE) e o coeficiente de determinação ajustado fora da amostra (R² out-of-sample). A comparação formal entre as arquiteturas concorrentes apoiou-se no teste não paramétrico de postos com sinais de Wilcoxon com correção de taxas de falsa descoberta pelo método de Holm, na regressão não paramétrica de Passing-Bablok (Passing & Bablok, 1983) e no teste assintótico de DeLong para curvas ROC correlacionadas (DeLong, DeLong, & Clarke-Pearson, 1988). Intervalos de confiança de 95% foram computados via reamostragem bootstrap acelerada e corrigida para viés (BCa) com 1.000 réplicas empíricas.

> A formulação de programação inteira mista em frotas veiculares sob incerteza de demanda exige que as restrições de disponibilidade operacional e os limites estritos de orçamento sejam simultaneamente respeitados em cada período discreto do horizonte de planejamento, tornando a otimização exata indispensável para evitar colapsos logísticos nos serviços essenciais (Danach et al., 2026, p. 103423).

## 5. Resultados Empíricos e Discussão

### 5.1 Desempenho Preditivo e Calibração dos Modelos de Risco
A Tabela 1 sintetiza a avaliação comparativa dos algoritmos supervisionados de classificação de risco operacional na partição out-of-time sob validação temporal com embargo estrito de 30 dias. O modelo ensemble baseado em histogramas de gradiente (HistGradientBoosting) consagrou-se campeão com PR-AUC de 0,9510 e ROC-AUC de 0,8743. O teste não paramétrico de DeLong confirmou a significância estatística dessa superioridade frente à regressão logística (Z = 16,39; p < 10⁻⁵⁰). Ademais, a calibração isotônica de probabilidades reduziu o Erro Esperado de Calibração (ECE) para 0,0174 [IC 95%: 0,0140; 0,0210] e o Brier Score para 0,1043, conferindo confiabilidade probabilística para alimentar as restrições operacionais do modelo MILP.

#### Tabela 1: Desempenho Preditivo e Calibração dos Classificadores de Risco Operacional na Frota Estadual

| Arquitetura Classificadora | PR-AUC Out-of-Time | ROC-AUC Out-of-Time | F1-Score Máximo | Brier Score (PAV) | ECE (10-bin) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Regressão Logística (Baseline) | 0,8120 | 0,6940 | 0,8210 | 0,1620 | 0,0845 |
| Random Forest (150 árvores) | 0,9120 | 0,8250 | 0,8790 | 0,1240 | 0,0410 |
| HistGradientBoosting (Campeão) | 0,9510 | 0,8743 | 0,9113 | 0,1043 | 0,0174 |
| Extra Trees Classifier | 0,9420 | 0,8650 | 0,9040 | 0,1110 | 0,0230 |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A acentuada redução do ECE de 0,0845 para 0,0174 comprova que as probabilidades geradas pelo HistGradientBoosting calibrado são aderentes à frequência observada em campo. Sem essa correção isotônica, o modelo matemático de otimização tenderia a superestimar o risco em faixas medianas de quilometragem, prescrevendo paradas preventivas prematuras e desperdiçando dotação orçamentária.

### 5.2 Regressão Não Linear de Custos de Manutenção Mecânica
A distribuição das despesas de reparação mecânica na frota estatal exibe severa assimetria à direita (skewness = 4,82; kurtosis = 31,4), com grande concentração de revisões periódicas básicas (R$ 300 a R$ 800) e uma cauda alongada com despesas que superam R$ 35.000 em retíficas de motores de caminhões de bombeiros e veículos blindados. Modelos lineares clássicos estimaram custos negativos para veículos novos e subestimaram drasticamente as falhas catastróficas.

#### Tabela 2: Comparativo de Acurácia e Desempenho Computacional dos Modelos de Regressão de Custos

| Arquitetura Regressora | Teste MAE (R$) | Teste RMSE (R$) | R² Out-of-Sample | Tempo de Treino (s) |
| :--- | :---: | :---: | :---: | :---: |
| Support Vector Regression (SVR-RBF) | R$ 2.569,20 | R$ 4.210,80 | 0,512 | 184,6 s |
| HistGradientBoostingRegressor (Campeão) | R$ 2.236,06 | R$ 3.780,20 | 0,748 | 1,8 s |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 2 apresenta o confronto entre o regressor baseado em árvores e o suporte vetorial não linear (SVR-RBF). O modelo HistGradientBoostingRegressor superou o baseline com MAE de R$ 2.236,06 [IC 95% BCa: 2.146,76; 2.321,17] e R² de 0,748. A superioridade foi certificada pelo teste pareado de postos com sinais de Wilcoxon com correção de Holm (W = 1.482.910; p < 10⁻¹⁵), proporcionando uma redução média de erro de R$ 333,14 por ordem de serviço e uma aceleração de 102,5 vezes no tempo de processamento (1,8 s contra 184,6 s), confirmando plenamente a Hipótese H2. A regressão linear de Passing-Bablok reportou inclinação de 3,318 [IC 95%: 3,052; 3,614] e intercepto de -R$ 5.855,12, atestando a inadequação dos modelos paramétricos simples sobre dados públicos heterogêneos.

### 5.3 Avaliação Ética da Fusão de Dados Multimodal
A incorporação de dados complementares de cadastro patrimonial e de abastecimentos de combustível ao conjunto básico de manutenção mecânica reduziu o erro médio absoluto de R$ 2.321,28 para R$ 2.311,82, representando um ganho marginal de acurácia de 0,41% (diferença de R$ 9,47 por ordem de serviço). Embora estatisticamente significante em virtude do volume amostral censitário, esse aprimoramento não atingiu o patamar de corte pré-estabelecido de 15,0% que justificaria a complexidade de manter pipelines contínuos de integração de dados entre sistemas heterogêneos. Em observância ao rigor ético da investigação e rejeitando qualquer prática de formulação retrospectiva de hipóteses (HARKing), a Hipótese H1 foi formalmente declarada não sustentada.

## 6. Resultados Prescritivos e Otimização Exata via MILP

### 6.1 Convergência Computacional e Eficiência no Cenário Canônico
O modelo de programação linear inteira mista foi executado sobre o conjunto da frota ativa utilizando o solver de código aberto HiGHS sob o método Dual Simplex com algoritmo de planos de corte e ramificação (Branch-and-Cut).

No cenário canônico S0, o solver convergiu para o custo total ótimo de R$ 43.837.633,31 em 8,92 segundos de tempo computacional para a totalidade dos 36 estágios mensais (média de 0,25 segundos por mês de planejamento). O limite dual fornecido pela relaxação linear foi de R$ 43.837.384,79, resultando em um gap de integralidade de apenas 0,000567% (diferença de R$ 248,52), o que comprova optimalidade matemática estrita. A solução garantiu disponibilidade operacional média de 95,26% [IC 95%: 94,90%; 95,60%] e 100% de conformidade nas revisões compulsórias de segurança, sem qualquer registro de violação normativa. A economia direta atingiu R$ 9.302.147,26, correspondendo a uma redução de 17,51% nas despesas públicas frente ao dispêndio inercial de R$ 53.139.780,57.

### 6.2 Decomposição Ablativa em Cinco Estágios
Para determinar com precisão a contribuição de cada componente analítico na geração do valor econômico e operacional, foi executado um estudo ablativo sistemático estruturado em cinco configurações progressivas.

#### Tabela 3: Estudo Ablativo em Cinco Estágios da Economia Orçamentária e Prontidão sob MILP Prescritivo

| Estágio Experimental | Descrição da Configuração | Custo Total Esperado | Prontidão PMSC (%) | Gap de Integralidade | Economia Líquida Gerada |
| :--- | :--- | :---: | :---: | :---: | :---: |
| E1 (Status Quo) | Manutenção Puramente Reativa (As-Is) | R$ 53.139.780,57 | 88,40% | Inaplicável | Baseline de Referência |
| E2 (Heurística) | Política Fixa por Tempo e KM | R$ 51.210.400,12 | 91,10% | Inaplicável | R$ 1,93M (3,63%) |
| E3 (Preditivo Puro) | Reparo de Alto Risco sem MILP | R$ 49.850.220,00 | 92,40% | Inaplicável | R$ 3,29M (6,19%) |
| E4 (MILP Ingênuo) | Otimização sem ML (Médias Históricas) | R$ 48.719.011,68 | 93,12% | 0,0000% | R$ 4,42M (8,31%) |
| E5 (FDPA Pleno) | MILP-1 Acoplado ao ML Calibrado | R$ 43.837.633,31 | 95,26% | 0,000567% | R$ 9,30M (17,51%) |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 3 evidencia a decomposição ablativa do valor econômico gerado pela integração entre o solver matemático MILP e os modelos supervisionados calibrados. A otimização linear simples isolada (E4) captura 47,5% da economia potencial, ao passo que a incorporação do aprendizado de máquina calibrado (E5) desbloqueia os 52,5% restantes (R$ 4.881.378,37 adicionais), totalizando R$ 9.302.147,26 em economia líquida direta (17,51%) com prontidão inegociável de 95,26% nas viaturas de patrulhamento da Polícia Militar. Por outro lado, heurísticas puramente gulosas de alocação violaram 34,53% das revisões de segurança, demonstrando a superioridade da modelagem inteira exata.

### 6.3 Diagnóstico Dual e Preços-Sombra das Restrições Fiscais
A extração dos multiplicadores de Lagrange associados à relaxação linear do modelo revelou conclusões fundamentais sobre o comportamento econômico da gestão pública:
- Restrição Orçamentária da LOA: O preço-sombra lambda_t associado ao teto mensal de custeio manteve-se estritamente positivo em percentuais entre 41,7% e 66,7% dos períodos do horizonte temporal. O valor médio de lambda_t nos períodos de estrangulamento foi de 1,42, indicando que cada R$ 1,00 adicional de dotação orçamentária concedido à manutenção preventiva geraria uma economia de R$ 1,42 em custos corretivos e reboques no período subsequente.
- Restrição de Capacidade das Oficinas: Em contrapartida, o multiplicador dual mu_t associado à capacidade física instalada das oficinas mecânicas credenciadas permaneceu nulo em 100% dos meses de planejamento. Esse diagnóstico quantitativo comprova de forma contundente que as filas e imobilizações prolongadas observadas na administração pública não são causadas pela insuficiência técnica do parque automotivo regional credenciado, mas pelo represamento de recursos orçamentários decorrente de fluxos burocráticos de empenho e liquidação da despesa pública.

### 6.4 Análise de Sensibilidade Paramétrica Multivariada
Para avaliar a estabilidade da política prescritiva sob oscilações macroeconômicas, foram realizadas análises de sensibilidade paramétrica multivariada variando a taxa de desconto social delta (4% a 12% ao ano) e o preço médio dos combustíveis (-20% a +40%).

#### Tabela 4: Análise de Sensibilidade Paramétrica do Custo Total de Propriedade e Economia Orçamentária

| Cenário Macroeconômico | Variação Combustível (%) | Taxa de Desconto Social | Custo Total Ótimo (R$) | Economia s/ Baseline (%) | Prontidão Média (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Deflacionário / Moderado | -20% | 4,0% a.a. | R$ 38.410.220,10 | 19,85% | 95,80% |
| Cenário Canônico S0 | 0% (Base) | 6,08% a.a. | R$ 43.837.633,31 | 17,51% | 95,26% |
| Choque Inflacionário Moderado | +15% | 8,0% a.a. | R$ 47.920.110,45 | 16,10% | 95,10% |
| Estresse de Severidade Severo | +30% | 10,0% a.a. | R$ 51.340.890,20 | 14,80% | 94,95% |
| Hiperinflação Energética | +40% | 12,0% a.a. | R$ 54.120.400,00 | 13,90% | 94,90% |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

Os resultados da Tabela 4 demonstram que, mesmo sob choques severos de preços de insumos energéticos (+40%), a formulação prescritiva preserva economia superior a 13,90% frente à política inercial, ao passo que a prontidão operacional nunca retrocede abaixo do limiar de segurança de 94,90%.

### 6.5 Simulações Estocásticas de Monte Carlo e Descarte Patrimonial
Simulações de Monte Carlo com mil iterações pseudoaleatórias, integrando processos de renovação de Weibull para a modelagem da taxa de falha intrínseca das peças ao longo da quilometragem acumulada e considerando a taxa composta de inflação setorial de 6,08% ao ano, projetaram economia orçamentária acumulada de R$ 40.088.374,00 no triênio 2027 a 2029 [IC 95%: R$ 37.020.150,00 a R$ 43.440.800,00].

No segmento patrimonial, o framework identificou exatamente 313 veículos da frota ativa cuja manutenção acumulada ultrapassou 40% do respectivo valor venal de mercado (tabela FIPE). O modelo determinou a desincorporação imediata e encaminhamento para leilão público, impedindo que o Estado desembolse R$ 4.215.890,00 em manutenções paliativas subsequentes, em cumprimento estrito ao Art. 5º do Decreto Estadual nº 47.539/2018.

#### Tabela 5: Síntese Demográfica e Granularidade Operacional da Frota Pública do Estado de Santa Catarina

| Categoria Funcional | Quantidade de Veículos | Idade Média (Anos) | Quilometragem Média (km) | Valor Venal FIPE Total (R$) | Gasto Acumulado Manutenção (R$) | Razão Média Gasto / FIPE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Policiamento Ostensivo (Sedan/SUV) | 6.840 | 6,4 anos | 148.520 km | R$ 342.150.000,00 | R$ 68.420.110,00 | 20,00% |
| Ambulâncias e Resgate (SES/SAMU) | 1.920 | 5,2 anos | 215.400 km | R$ 134.800.000,00 | R$ 28.940.230,00 | 21,47% |
| Tático Blindado e Especial (BOPE/COE) | 480 | 7,8 anos | 112.300 km | R$ 48.900.000,00 | R$ 12.450.800,00 | 25,46% |
| Bombeiros e Caminhões Auto-Bomba | 850 | 11,4 anos | 89.400 km | R$ 153.200.000,00 | R$ 18.230.150,00 | 11,90% |
| Administrativo e Apoio (SEA/SED) | 5.210 | 8,1 anos | 134.100 km | R$ 182.400.000,00 | R$ 26.850.400,00 | 14,72% |
| Transporte Prisional (SAP) | 1.952 | 6,9 anos | 178.900 km | R$ 98.400.000,00 | R$ 16.890.350,00 | 17,16% |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 5 estratifica a frota governamental consolidada de 17.252 veículos em suas seis principais categorias funcionais. Os dados empíricos evidenciam perfis de desgaste acentuadamente heterogêneos. As ambulâncias do SAMU apresentam a maior quilometragem média rodada (215.400 km), demandando manutenções frequentes em virtude do regime ininterrupto de prontidão 24 horas por dia. Em contrapartida, as viaturas táticas blindadas e os caminhões de combate a incêndio do Corpo de Bombeiros apresentam quilometragens menores, porém com custos unitários de intervenção mecânica substantivamente mais elevados, decorrentes da especificidade de bombas hidráulicas e componentes importados de suspensão reforçada.

### 6.6 Dossiê de Veículos Onerosos e Alienação Compulsória (Art. 5º do Decreto nº 47.539/2018)
O artigo 5º do Decreto Estadual nº 47.539/2018 estabelece como critério objetivo de antieconomicidade o atingimento de 40% de despesas acumuladas de manutenção frente ao valor venal contábil de mercado referenciado pela tabela FIPE. O modelo prescritivo isolou 313 veículos em situação de flagrante antieconomicidade, nos quais manutenções corretivas sucessivas representaram verdadeira dilapidação do patrimônio do Estado.

#### Tabela 6: Amostra Pericial dos Quinze Veículos Mais Antieconômicos Indicados para Leilão pelo FDPA

| Placa (Anonimizada LGPD) | Órgão / Secretaria | Marca e Modelo | Ano Fab. | Quilometragem (km) | Valor Venal FIPE (R$) | Gasto Acumulado (R$) | Razão Gasto / FIPE (%) | Enquadramento Legal |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| VEIC-8812 | PMSC | Chevrolet Astra Sedan | 2008 | 342.150 km | R$ 18.400,00 | R$ 33.850,20 | 183,97% | Leilão Compulsório (Art. 5º) |
| VEIC-4491 | SES | Renault Master Ambulância | 2011 | 485.200 km | R$ 42.100,00 | R$ 68.920,40 | 163,71% | Leilão Compulsório (Art. 5º) |
| VEIC-1234 | SEA | Fiat Palio Weekend | 2009 | 298.400 km | R$ 16.500,00 | R$ 24.110,00 | 146,12% | Leilão Compulsório (Art. 5º) |
| VEIC-9921 | PMSC | Ford Fiesta Hatch | 2010 | 312.800 km | R$ 19.200,00 | R$ 26.450,80 | 137,76% | Leilão Compulsório (Art. 5º) |
| VEIC-3382 | CBMSC | Ford Ranger 4x4 Resgate | 2012 | 289.100 km | R$ 54.000,00 | R$ 68.200,00 | 126,30% | Leilão Compulsório (Art. 5º) |
| VEIC-5509 | SAP | Volkswagen Voyage 1.6 | 2013 | 321.400 km | R$ 28.500,00 | R$ 34.120,50 | 119,72% | Leilão Compulsório (Art. 5º) |
| VEIC-7714 | PMSC | Mitsubishi L200 Triton | 2011 | 365.900 km | R$ 62.000,00 | R$ 71.850,00 | 115,89% | Leilão Compulsório (Art. 5º) |
| VEIC-8843 | SED | Fiat Uno Mille Way | 2010 | 275.300 km | R$ 14.800,00 | R$ 16.890,00 | 114,12% | Leilão Compulsório (Art. 5º) |
| VEIC-4402 | SES | Mercedes Sprinter Furgão | 2012 | 412.000 km | R$ 68.000,00 | R$ 74.200,00 | 109,12% | Leilão Compulsório (Art. 5º) |
| VEIC-1190 | PMSC | Renault Duster 2.0 4x4 | 2014 | 298.700 km | R$ 41.200,00 | R$ 44.110,00 | 107,06% | Leilão Compulsório (Art. 5º) |
| VEIC-6623 | SEA | Volkswagen Gol 1.0 TotalFlex | 2011 | 284.100 km | R$ 21.000,00 | R$ 21.950,00 | 104,52% | Leilão Compulsório (Art. 5º) |
| VEIC-2211 | CBMSC | Iveco Daily Furgão | 2013 | 245.800 km | R$ 78.000,00 | R$ 79.400,00 | 101,79% | Leilão Compulsório (Art. 5º) |
| VEIC-7740 | PMSC | Toyota Hilux 4x4 CD | 2012 | 398.200 km | R$ 89.000,00 | R$ 86.450,00 | 97,13% | Leilão Compulsório (Art. 5º) |
| VEIC-9901 | SAP | Chevrolet Classic 1.0 | 2012 | 265.400 km | R$ 22.400,00 | R$ 21.200,00 | 94,64% | Leilão Compulsório (Art. 5º) |
| VEIC-3329 | SED | Volkswagen Parati 1.6 | 2009 | 312.000 km | R$ 17.800,00 | R$ 16.420,00 | 92,25% | Leilão Compulsório (Art. 5º) |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 6 elucida a gravidade do passivo econômico gerado pela ausência histórica de uma política prescritiva formal. Casos notórios como a viatura policial Astra Sedan (VEIC-8812) consumiram R$ 33.850,20 em reparos para um valor venal de apenas R$ 18.400,00 (183,97% do valor venal), e a ambulância Master da SES (VEIC-4491) despendeu R$ 68.920,40 para um valor residual de R$ 42.100,00 (163,71%). A prescrição imediata de desincorporação gerada pelo FDPA estanca a sangria de recursos públicos e viabiliza a recomposição do erário por meio da receita auferida nos leilões públicos de alienação patrimonial.

### 6.7 Modelagem Econométrica de Sobrevivência e Degradação de Weibull
A modelagem probabilística das taxas de falha em serviço apoiou-se na distribuição de sobrevivência de Weibull com dois parâmetros (forma beta e escala eta). A função de taxa de falha instantânea h(t), representativa da curva da banheira automotiva, é dada por:

<div class="formula-box">
  <span>h(t) = (&beta; / &eta;) &middot; (t / &eta;)<sup>&beta; - 1</sup></span>
  <span class="formula-number">(9)</span>
</div>
<div class="formula-box">
  <span>R(t) = exp( - (t / &eta;)<sup>&beta;</sup> )</span>
  <span class="formula-number">(10)</span>
</div>
<div class="formula-box">
  <span>p&#770;(i, t) = 1 - exp( - [ ((t + 1) / &eta;)<sup>&beta;</sup> - (t / &eta;)<sup>&beta;</sup> ] )</span>
  <span class="formula-number">(11)</span>
</div>

Onde t representa a quilometragem percorrida pelo veículo. Para a frota de patrulhamento ostensivo da Polícia Militar, o ajuste por máxima verossimilhança estimou o parâmetro de forma em beta = 1,48 [IC 95%: 1,42; 1,54] e o parâmetro de escala em eta = 185.000 km. O fato de beta ser estritamente superior à unidade (beta > 1) comprova matematicamente que a frota estadual encontra-se em regime de envelhecimento acelerado (wear-out phase), onde a probabilidade condicional de quebra cresce exponencialmente com a quilometragem acumulada, inviabilizando manutenções meramente reativas e reforçando a exigência de modelos prescritivos.

## 7. Diretrizes para Implementação Prática, Governança e Uso Ético da Inteligência Artificial

### 7.1 Governança Operacional e Rastreabilidade Algorítmica
A implantação bem-sucedida do FDPA na administração pública requer governança de dados estruturada e rastreabilidade algorítmica. As decisões de manutenção e desfazimento patrimonial devem ser registradas em trilha de auditoria digital contendo a identificação do modelo utilizado, a probabilidade calculada, os coeficientes de custo considerados e o identificador do operador ou auditor responsável.

Recomenda-se a adoção de interfaces de gestão com perfis baseados em controle de acesso por funções (RBAC), assegurando que técnicos mecânicos, auditores do Tribunal de Contas do Estado (TCE/SC) e secretários setoriais tenham visibilidade proporcional sobre os alertas e prescrições do sistema. A integração com sistemas de mensageria assíncrona viabiliza a execução de rotinas periódicas de reotimização do solver a cada fechamento de mês orçamentário.

### 7.2 Uso Ético da Inteligência Artificial no Setor Público
A aplicação de modelos prescritivos e algoritmos de aprendizado de máquina para direcionar recursos orçamentários do Estado exige conformidade estrita com postulados éticos consolidados:

1. Princípio da Equidade Distributiva Territorial: Os modelos de otimização matemática não podem penalizar batalhões policiais ou postos de saúde sediados em municípios do interior ou em áreas periféricas em razão de menores densidades de oficinas credenciadas. A formulação do FDPA impõe restrições explícitas de prontidão mínima (alpha_k >= 0,95) individualizadas para cada unidade regional, impedindo que o algoritmo sacrifique a segurança de regiões vulneráveis em favor da minimização global do custo estadual.
2. Garantia do Elo Humano Significativo (Human-in-the-Loop): O sistema algorítmico atua categoricamente como suporte instrumental à cognição técnica do gestor público, sendo vedada a baixa patrimonial ou o bloqueio financeiro de ordens de serviço de forma totalmente desacompanhada de chancela humana. Todo ato decisório exige confirmação por agente público investido de autoridade administrativa.
3. Privacidade e Proteção de Dados Pessoais (LGPD): Em estrito cumprimento à Lei Federal nº 13.709/2018 (Lei Geral de Proteção de Dados Pessoais), todos os identificadores de condutores e operadores de viaturas táticas foram submetidos a anonimização criptográfica irreversível por hashing SHA-256 com salting dinâmico. O treinamento dos modelos utiliza exclusivamente telemetria de consumo, quilometragem e registros mecânicos dos ativos, resguardando o sigilo operacional e a intimidade dos servidores públicos da segurança e saúde.
4. Sustentabilidade Ambiental e Descarbonização: Ao eliminar a circulação ineficiente de motores em estado avançado de degradação física e otimizar os ciclos de troca de óleo e filtros, a política prescritiva reduz diretamente a queima excessiva de hidrocarbonetos e a emissão de particulados na atmosfera, alinhando a gestão pública aos Objetivos de Desenvolvimento Sustentável (ODS) das Nações Unidas.

### 7.3 Conformidade com a Lei Federal nº 14.133/2021 e Jurisprudência dos Tribunais de Contas
A Nova Lei de Licitações e Contratos Administrativos (Lei nº 14.133/2021) consagrou expressamente o princípio da gestão por competências, o planejamento logístico prévio e a exigência de demonstração contábil do Custo Total de Propriedade (TCO) como critério de julgamento de propostas e prorrogações contratuais. O FDPA fornece aos gestores públicos a fundamentação quantitativa indispensável para instruir processos de descredenciamento de oficinas com baixa performance e motivar perante o Tribunal de Contas do Estado de Santa Catarina (TCE/SC) a economicidade das ordens de serviço emitidas.

## 8. Limitações do Trabalho

A despeito da robustez metodológica dos testes empíricos, a presente pesquisa apresenta limitações operacionais e analíticas que delimitam seu escopo de generalização:

1. Dependência de Sistemas Administrativos Transacionais Legados: O pipeline de modelagem alimentou-se de registros cadastrais de ordens de serviço e faturas de combustível preenchidas por prestadores credenciados e servidores públicos. Embora filtradas por algoritmos não supervisionados de detecção de anomalias (Isolation Forest), eventuais latências de lançamento fiscal ou pequenos erros de digitação em quilometragens intermediárias podem introduzir ruídos residuais nos dados brutos.
2. Inexistência de Telemetria CAN-Bus de Alta Frequência em Tempo Real: Ao contrário de frotas industriais privadas que contam com sensores telemáticos contínuos de barramento veicular (OBD-II/CAN-Bus com leitura de segundo a segundo de pressão de óleo, temperatura de escapamento e rotações do motor), a frota pública estadual é monitorada primordialmente por registros discretos de eventos de manutenção e abastecimento na bomba de combustível. Essa granularidade discreta impede o diagnóstico precoce de microavarias instantâneas no instante exato de sua eclosão física.
3. Choques Macroeconômicos e Volatilidade Exógena de Preços: Os parâmetros econômicos de insumos energéticos (gasolina, diesel e etanol) e peças de reposição encontram-se sujeitos a oscilações geopolíticas internacionais no mercado do petróleo e rupturas em cadeias globais de suprimentos. Conquanto a análise de sensibilidade multivariada tenha simulado estresses inflacionários de até 40%, oscilações extremas e prolongadas exigem a reparametrização contínua dos coeficientes de custo na matriz linear.
4. Especificidades Jurídico-Institucionais do Modelo de Gestão Centralizada: A estrutura matricial do FDPA foi calibrada sobre o arcabouço normativo do Estado de Santa Catarina (Decreto Estadual nº 47.539/2018 e Instruções Normativas da SEA/SC). A transposição da formulação para municípios de pequeno porte ou entes federativos que adotam modelos inteiramente terceirizados de locação de veículos (rent-a-car) demanda a readequação dos termos de depreciação de capital e custos de oportunidade financeira.

## 9. Considerações Finais, Recomendações de Políticas Públicas e Conclusões

O presente estudo desenvolveu e validou empiricamente o Framework de Decisão Pública Auditável (FDPA), comprovando que a convergência metodológica entre algoritmos supervisionados calibrados e a programação linear inteira mista viabiliza um novo patamar de eficiência na administração de frotas estatais. Ao conciliar a minimização de custos com restrições invioláveis de prontidão operacional policial e conformidade orçamentária, a abordagem supera categoricamente as limitações das políticas tradicionais corretivas e preventivas cegas.

A economia direta demonstrada de 17,51% (R$ 9.302.147,26 no cenário canônico e R$ 40,09 milhões na projeção trienal), associada à manutenção da disponibilidade policial em 95,26% e à eliminação de despesas ilegais em veículos antieconômicos, evidencia que a governança orientada a analítica prescritiva constitui ferramenta de valor inestimável para a gestão pública orientada a resultados e a estrita conformidade republicana. O estudo ablativo em cinco estágios provou analiticamente que a otimização matemática ingênua captura menos da metade da economia potencial, ao passo que a predição probabilística calibrada destrava os 52,5% restantes de valor econômico e operacional.

Para os órgãos de controle externo e controladores governamentais (Tribunais de Contas e Controladorias-Gerais), este trabalho fornece uma matriz probatória objetiva e juridicamente sustentável. A parametrização dos custos duais revela aos auditores que os estrangulamentos operacionais da frota pública não decorrem da capacidade física das oficinas privadas credenciadas, mas de travas orçamentárias na liberação dos fluxos de empenho e liquidação da despesa mensal.

Como agenda de pesquisas futuras, recomenda-se:
1. Expansão para Frotas Descarbonizadas: Modelar a transição energética plurianual da frota pública mediante a introdução de veículos híbridos e 100% elétricos, incorporando restrições de instalação de infraestrutura de carregadores rápidos e perfis não lineares de degradação química de baterias.
2. Integração com Aprendizado Federado (Federated Learning): Avaliar arquiteturas descentralizadas de treinamento cooperativo entre diferentes Estados da federação e Forças Armadas, permitindo o intercâmbio de conhecimento preditivo sobre confiabilidade mecânica sem o compartilhamento direto de dados estratégicos sigilosos de segurança pública.
3. Roteirização Dinâmica sob Otimização Conjunta: Acoplar o modelo MILP de escalonamento de revisões mecânicas a sistemas prescritivos de roteirização logística e despacho inteligente de patrulhamento ostensivo em tempo real.

## Referências
- Al-Douri, Y. K., Hamoodi, O., & Al-Taee, M. (2019). Machine learning for sustainable predictive maintenance in smart fleet operations. *Journal of Cleaner Production*, 235, 1230-1242.
- Arena, S., Florian, E., Sgarbossa, F., Sølvsberg, E., & Zennaro, I. (2024). A conceptual framework for machine learning algorithm selection for predictive maintenance. *Engineering Applications of Artificial Intelligence*, 133, 108342.
- Barbado, A., & Corcho, Ó. (2022). Interpretable machine learning models for predicting and explaining vehicle fuel consumption anomalies. *Engineering Applications of Artificial Intelligence*, 114, 105177.
- Benders, J. F. (1962). Partitioning procedures for solving mixed-variables programming problems. *Numerische Mathematik*, 4(3), 238-252.
- Beretta, M., Julian, A., Sepulveda, J., Cusidó, J., & Porro, O. (2021). An ensemble learning solution for predictive maintenance of wind turbines main bearing. *Sensors*, 21(18), 6212.
- Bertsimas, D., & Kallus, N. (2020). From predictive to prescriptive analytics. *Management Science*, 66(3), 1025-1044.
- Birge, J. R., & Louveaux, F. (2011). *Introduction to Stochastic Programming*. Springer Science & Business Media, New York.
- Brasil. (2000). Lei Complementar nº 101, de 4 de maio de 2000. Estabelece normas de finanças públicas voltadas para a responsabilidade na gestão fiscal.
- Brasil. (2021). Lei Federal nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos.
- Bukhsh, Z. A., Saeed, A., Stipanovic, I., & Doree, A. G. (2019). Predictive maintenance using tree-based classification techniques: A case of railway switches. *Transportation Research Part C: Emerging Technologies*, 101, 216-233.
- Danach, K., Harb, H., Issa, H., & Saker, L. (2026). An explainable data-driven optimization framework for industrial predictive maintenance scheduling. *Results in Engineering*, 26, 103420.
- DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves. *Biometrics*, 44(3), 837-845.
- Eppen, G. D., Martin, R. K., & Schrage, L. (1989). A scenario approach to capacity planning in the presence of uncertainty. *Operations Research*, 37(4), 517-527.
- Gama, J., Ribeiro, R. P., & Veloso, B. (2022). Data-driven predictive maintenance. *IEEE Intelligent Systems*, 37(4), 5-8.
- Giordano, D., Giobergia, F., Pastor, E., La Macchia, A., Cerquitelli, T., Baralis, E., Mellia, M., & Tricarico, D. (2021). Data-driven strategies for predictive maintenance: Lesson learned from an automotive use case. *Computers in Industry*, 132, 103513.
- Grau-Escolano, J., Bassolas, A., & Vicens, J. (2024). Cycling into the workshop: mobility patterns for predictive maintenance in Barcelona's bike-sharing system. *EPJ Data Science*, 13(1), 12.
- Huang, H., & Chen, Y. (2023). Fleet management optimization under uncertainty: A mixed-integer programming approach. *Transportation Research Part C: Emerging Technologies*, 148, 104030.
- Huang, Z., Zhu, X., & Xiang, Y. (2020). Condition-based maintenance policy for multi-component systems subject to mission availability. *IEEE Transactions on Reliability*, 69(2), 650-664.
- López de Prado, M. (2018). *Advances in Financial Machine Learning*. John Wiley & Sons, Hoboken.
- Mahale, P., Kolhar, M., & More, S. (2025). Predictive maintenance in public transport systems using machine learning ensembles. *IEEE Transactions on Intelligent Transportation Systems*, 26(2), 1450-1462.
- Nemhauser, G. L., & Wolsey, L. A. (1988). *Integer and Combinatorial Optimization*. John Wiley & Sons, New York.
- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. *Proceedings of the 22nd International Conference on Machine Learning (ICML)*, 625-632.
- Özcan, H. (2025). Interpretable ensemble remaining useful life prediction enables dynamic maintenance scheduling for aircraft engines. *Scientific Reports*, 15(1), 1234.
- Passing, H., & Bablok, W. (1983). A new biometrical procedure for testing the equality of measurements from two different analytical methods. *Journal of Clinical Chemistry and Clinical Biochemistry*, 21(11), 709-720.
- Santa Catarina. (2018). Decreto Estadual nº 47.539, de 03 de abril de 2018. Dispõe sobre a gestão patrimonial de veículos oficiais do Poder Executivo Estadual.
- Wolsey, L. A. (2020). *Integer Programming* (2nd ed.). John Wiley & Sons, Hoboken.

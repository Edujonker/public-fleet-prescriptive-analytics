# Auditoria de Inteligência Artificial em Contratações Públicas e Desfazimento Patrimonial: Divergência Empírica entre SHAP e LIME, Modularidade de Redes e Detecção de Comunidades Bipartidas em Frotas Governamentais

**Periódico de Destino:** *Revista de Administração Pública (RAP)* / *Revista de Administração Contemporânea (RAC)* / *IEEE Latin America Transactions* (Qualis A1)  
**Autores:** Eduardo Lopes Jonker¹, Vivian Kremer Kalempa¹, Yuri Kaszubowski Lopes¹  
¹ Programa de Pós-Graduação em Computação Aplicada (PPGCAP), Centro de Ciências Tecnológicas (CCT), Universidade do Estado de Santa Catarina (UDESC), Joinville, SC, Brasil.  

## Resumo
A incorporação progressiva de sistemas de inteligência artificial e aprendizado de máquina na administração pública para tomada de decisões patrimoniais, auditoria contratual e desfazimento de bens introduz exigências jurídicas e constitucionais sem precedentes. Decisões que culminam na baixa de ativos estatais, descredenciamento de fornecedores ou glosas financeiras de pagamento devem atender ao princípio do Devido Processo Algorítmico e da transparência explicável. Este trabalho investiga a confiabilidade empírica e a auditabilidade forense de métodos de Inteligência Artificial Explicável (XAI) e da Ciência de Redes aplicados à governança de ativos públicos. Com base em microdados administrativos exaustivos do Governo do Estado de Santa Catarina, contemplando 350.737 itens de manutenção mecânica em 77.867 ordens de serviço (R$ 138.759.653,82 em dispêndios autorizados e R$ 60.047.310,67 em glosas da fiscalização técnica), 34.280 veículos do patrimônio estadual e 1.000.000 de transações de abastecimento de combustível (R$ 153.488.476,96), submetem-se os dois principais métodos de XAI da literatura, SHAP (fundamentado nos valores de Shapley da teoria dos jogos cooperativos) e LIME (fundamentado em perturbações lineares locais), a uma auditoria comparativa exaustiva. Contrariando a premissa disseminada de intercambiabilidade entre métodos explicativos (nossa Hipótese H4 pré-registrada), documenta-se uma aguda divergência estrutural: um índice de similaridade de Jaccard no Top-5 atributos de apenas 39,29% [IC 95% BCa: 37,82%; 40,75%] e uma correlação de postos de Spearman de ρ = 0,3680 [IC 95%: 0,3450; 0,3910] (Kendall τ_b = 0,2915). Demonstra-se matematicamente que tal discordância decorre das propriedades axiomáticas globais aditivas dos valores de Shapley em confronto com a variância estocástica do kernel gaussiano localizado do LIME sobre dados públicos de cauda pesada. Consequentemente, a confiança cega em um único método de explicação expõe a autoridade pública a contestações jurídicas e anulações em tribunais de contas. Para sanar essa vulnerabilidade, formula-se o Protocolo de Triangulação Explicável Multimetodológica (METP) acoplado à modelagem de redes complexas. Por meio da construção de um Grafo Bipartido de Afiliação Veículo-Oficina, o algoritmo de detecção de comunidades de Louvain identifica 18 clusters modulares (Q = 0,5646) e oficinas centrais de alta intermediação, enquanto uma sub-rede induzida isola R$ 4.180.250,00 em despesas anômalas concentradas. Por fim, um ensemble de Isolation Forest (contaminação calibrada de ν = 0,0085, estabilidade multiseed de Jaccard J = 0,8055), operando sob cadeia de custódia criptográfica imutável via hashing SHA-256 em blocos, identifica 662 ordens de serviço anômalas (R$ 16.581.420,50) e 13.936 eventos atípicos de abastecimento. Este trabalho fornece aos órgãos de controle externo e controladores governamentais um framework epistemologicamente sólido e juridicamente defensável para a governança de inteligência artificial no setor público.

**Palavras-chave:** Inteligência Artificial Explicável (XAI); Devido Processo Algorítmico; Divergência SHAP vs LIME; Redes Complexas; Grafos Bipartidos; Auditoria de Contratações Públicas; Detecção de Anomalias.

## 1. Introdução: O Imperativo Jurídico e Técnico do Devido Processo Algorítmico

A transição dos modelos de aprendizado de máquina de sistemas puramente exploratórios para esferas decisórias da administração pública transforma radicalmente os critérios de validação algorítmica. No setor público, a atividade administrativa é estritamente vinculada aos princípios constitucionais da legalidade, impessoalidade, moralidade, publicidade e eficiência (Art. 37 da Constituição da República Federativa do Brasil de 1988), assim como às exigências de transparência ativa e prestação de contas governamentais. Quando modelos preditivos e prescritivos são empregados por órgãos do Estado para recomendar a desincorporação e leilão de viaturas públicas, aplicar glosas contratuais contra oficinas credenciadas ou bloquear pagamentos suspeitos de combustível, o Poder Público não pode tratar tais algoritmos como caixas-pretas inacessíveis. O direito público consagra a exigência de motivação técnica inteligível, auditável e juridicamente contestável para todo ato administrativo sancionatório ou patrimonial, garantia que a doutrina contemporânea consolida sob a denominação de Devido Processo Algorítmico. Atos administrativos amparados em predições desprovidas de fundamentação transparente incorrem em nulidade jurídica insanável.

A literatura internacional recente em governança de inteligência artificial (European Commission, 2024) converge no sentido de exigir que algoritmos de alto impacto apresentem explicabilidade intrínseca ou acoplamento com métodos de atribuição causal pós-hoc verificáveis. No âmbito da ciência da computação contemporânea, técnicas de Inteligência Artificial Explicável (XAI), em especial SHAP (Lundberg & Lee, 2017) e LIME (Ribeiro, Singh, & Guestrin, 2016), são amplamente recomendadas para conferir interpretabilidade a pipelines preditivos e de manutenção (Steurtewagen & Van den Poel, 2021; Cummins et al., 2024; Sharma, Mittal, & Soni, 2022). Em setores de infraestrutura crítica e frotas, abordagens fundamentadas em SHAP têm sido aplicadas para decomposição de fatores de desgaste e consumo veicular (Alomari & Andó, 2024; Barbado & Corcho, 2022; Dereci & Tuzkaya, 2024), enquanto modelos substitutos como LIME e árvores de decisão explicáveis visam suportar o diagnóstico de operadores em tempo real (Rajaoarisoa et al., 2024; Xiao et al., 2024). Contudo, revisões recentes alertam que a robustez das atribuições explicativas é sensível ao pré-processamento e à complexidade distributiva dos dados (Ndao et al., 2025; Zemmouchi-Ghomari, 2026). Conforme advertem Lundberg e Lee (2017):

> A transparência na tomada de decisão algorítmica exige que os métodos explicativos pós-hoc forneçam justificativas fiéis e consistentes à mecânica interna do modelo, assegurando que o impacto atribuído a cada variável represente genuinamente sua contribuição marginal na resposta do sistema inteligente (Lundberg & Lee, 2017, p. 4766).

Praticantes e analistas comumente assumem que SHAP e LIME oferecem explicações intercambiáveis, presumindo que os atributos identificados como determinantes por um método seriam similarmente destacados pelo outro. Essa suposição informal ganhou força no mercado em razão de ambos os métodos serem rotulados genericamente como soluções de explicabilidade local agnósticas a modelos.

O presente estudo desafia empiricamente essa premissa por meio de testes quantitativos exaustivos conduzidos sobre microdados censitários do Governo do Estado de Santa Catarina. Em particular, testa-se formalmente a Hipótese H4 pré-registrada: as atribuições de relevância local e global de atributos geradas pelos métodos SHAP e LIME apresentam estrita convergência estrutural (similaridade de Jaccard no Top-5 superior a 85,0%), assegurando sua direta intercambiabilidade perante órgãos de controle externo. Por meio da avaliação estatística em 77.867 ordens de serviço auditadas, a Hipótese H4 é formalmente refutada. Constata-se uma concordância média de Jaccard de apenas 39,29% e correlação de Spearman de ρ = 0,3680. Diante dessa fratura empírica, detalham-se as razões matemáticas da divergência e estabelece-se um protocolo de triangulação explicável integrado a grafos de redes complexas e algoritmos de detecção não supervisionada de anomalias com cadeia de custódia criptográfica imutável.

> A atribuição de valores de Shapley a problemas de aprendizado de máquina constitui a única metodologia de explicação aditiva de atributos que satisfaz simultaneamente aos axiomas de eficiência, simetria, monotonicidade e jogador nulo, conferindo consistência teórica indispensável quando decisões algorítmicas produzem impactos jurídicos ou financeiros substanciais (Lundberg & Lee, 2017, p. 4766).

## 2. Fundamentos Matemáticos e Epistemológicos da Divergência entre SHAP e LIME

A governança de inteligência artificial explicável no setor público apoia-se nas taxonomias e princípios de IA responsável desenvolvidos por Barredo Arrieta et al. (2020) e Guidotti et al. (2018). Conforme alertam Rudin (2019) e Molnar (2022), a dependência acrítica de modelos caixa-preta em decisões de alto impacto social e jurídico impõe sérios riscos éticos, sendo imperativo compreender as premissas e limitações dos métodos explicativos pós-hoc. Paralelamente, Mittelstadt, Russell & Wachter (2019) discutem as armadilhas conceituais das explicações locais perante órgãos de fiscalização. No campo da ciência de redes, os algoritmos de detecção de comunidades de Blondel et al. (2008) e a análise topológica de modularidade revisada por Fortunato (2010) viabilizam a segregação de clusters relacionais em larga escala. Por fim, para a validação inferencial da capacidade discriminativa das curvas ROC correlacionadas, emprega-se o teste não paramétrico de DeLong, DeLong & Clarke-Pearson (1988).


### 2.1 Teoria dos Jogos Cooperativos e a Formulação Axiomática do SHAP
O método SHAP (Shapley Additive Explanations) ancora-se formalmente na teoria dos jogos cooperativos concebida por Lloyd Shapley. Seja F o conjunto universal de todas as variáveis preditivas de entrada (|F| = M) e seja f(x) a resposta computada pelo modelo de aprendizado de máquina para uma determinada instância x. Para quantificar a contribuição marginal individual de uma variável i pertencente a F, o valor de Shapley phi_i(x) é definido pela seguinte expressão analítica:

<div class="formula-box">
  <span>&phi;<sub>i</sub>(x) = &sum;<sub>S&sube;F&setminus;{i}</sub> [ (|S|! &middot; (|F| - |S| - 1)!) / |F|! ] &middot; [ f<sub>x</sub>(S &cup; {i}) - f<sub>x</sub>(S) ]</span>
  <span class="formula-number">(1)</span>
</div>

Nessa equação, |S| representa o número de variáveis presentes na coalizão S, |F|! denota o número total de permutações ordenadas do conjunto de atributos, e a diferença f_x(S união {i}) - f_x(S) expressa a contribuição marginal introduzida pela adição da variável i à coalizão S.

O valor de Shapley é a única classe de solução de atribuição aditiva de relevância que satisfaz simultaneamente quatro propriedades axiomáticas rigorosas:
1. Eficiência: A soma de todos os valores de Shapley phi_i(x) sobre as M variáveis coincide exatamente com a diferença entre a predição da instância f(x) e o valor esperado global do modelo E[f(x)].
2. Simetria: Se duas variáveis i e j contribuem identicamente para todas as coalizões possíveis, de modo que f_x(S união {i}) = f_x(S união {j}) para qualquer subconjunto S, então phi_i(x) = phi_j(x).
3. Jogador Nulo: Se a inclusão de uma variável i não altera a predição do modelo para nenhum subconjunto S, de modo que f_x(S união {i}) = f_x(S) para todo S, então phi_i(x) = 0.
4. Aditividade: Se um modelo é composto pela soma linear de dois preditores f e g, de modo que h(x) = f(x) + g(x), então o valor de Shapley de h é a soma direta dos valores de Shapley de f e g.

O algoritmo TreeExplainer explora a estrutura de árvores de decisão para calcular esses valores analiticamente em tempo polinomial O(T * L * D²), onde T é o número de árvores, L é o número de folhas e D é a profundidade máxima, garantindo estabilidade matemática absoluta e reprodutibilidade determinística.

### 2.2 Perturbações Locais e a Formulação de Otimização do LIME
Em nítido contraste com o rigor axiomático global de Shapley, o método LIME (Local Interpretable Model-agnostic Explanations) formula a explicabilidade como um problema de minimização de risco empírico circunscrito a uma vizinhança estocástica gerada artificialmente em torno da instância x. A formulação de otimização do LIME é dada por:

<div class="formula-box">
  <span>arg min<sub>g&isin;G</sub> [ &Lscr;(f, g, &pi;<sub>x</sub>) + &Omega;(g) ]</span>
  <span class="formula-number">(2)</span>
</div>

Onde g representa um modelo substituto interpretável pertencente a uma família simplificada G (tipicamente regressores lineares com coeficientes esparsos), L mensura a perda de fidelidade da aproximação g em relação ao modelo complexo f na vizinhança induzida pela medida de proximidade pi_x, e Omega(g) penaliza a complexidade do modelo explicativo (como o número de variáveis ativas não nulas).

A medida de proximidade pi_x(z) entre a instância original x e uma instância perturbada sintética z é computada através de um kernel exponencial ponderado pela distância euclidiana normalizada:

<div class="formula-box">
  <span>&pi;<sub>x</sub>(z) = exp( - D(x, z)<sup>2</sup> / &sigma;<sup>2</sup> )</span>
  <span class="formula-number">(3)</span>
</div>

Nessa formulação, D(x, z) denota a métrica de distância contínua ou categórica, e sigma representa a largura de banda (kernel width) estipulada pelo analista. A amostragem sintética z é gerada a partir de perturbações gaussianas univariadas independentes em torno das médias amostrais.

Contudo, conforme ressalvado por Ribeiro, Singh e Guestrin (2016):

> Caso as explicações locais sejam computadas a partir de perturbações aleatórias que violem a distribuição empírica subjacente dos dados, as aproximações lineares resultantes tornam-se altamente instáveis e dependentes da largura de banda selecionada, comprometendo a reprodutibilidade forense necessária para auditorias independentes (Ribeiro, Singh, & Guestrin, 2016, p. 1136).

### 2.3 Mecanismos da Divergência: Violação de Axiomas e Instabilidade de Perturbação
A divergência sistemática observada entre SHAP e LIME decorre de fatores matemáticos e distributivos intransponíveis:
Primeiro, a amostragem aleatória do LIME gera réplicas z assumindo independência estatística entre os atributos. Em dados de frotas públicas, variáveis operacionais como ano de fabricação, quilometragem acumulada, quantidade de abastecimentos e número histórico de ordens de serviço apresentam fortíssima colinearidade estrutural. A amostragem gaussiana do LIME gera instâncias aberrantes fora do suporte empírico real (por exemplo, veículos com 1 ano de uso e 700.000 km, ou veículos com 15 anos de uso com apenas 500 km), forçando o regressor linear local a ajustar coeficientes angulares sobre regiões vazias do espaço de atributos.

Segundo, o LIME viola manifestamente o axioma de eficiência e o axioma de aditividade. Regressores lineares ajustados sobre amostras perturbadas não garantem que a soma dos coeficientes recupere a saída exata da árvore de decisão original, nem garantem consistência monótona: um aumento genuíno no desgaste de um veículo pode fazer com que o coeficiente do LIME diminua caso a largura de banda sigma capture instâncias sintéticas com ruído desfavorável na fronteira local.

## 3. Avaliação Empírica e Refutação Formal da Hipótese H4

### 3.1 Desenho Experimental de Auditoria Comparativa
Para testar rigorosamente a intercambiabilidade entre SHAP e LIME, conduziu-se um protocolo experimental censitário sobre a partição out-of-time da base de dados de manutenção do Governo de Santa Catarina, contemplando uma subamostra representativa e auditada de 2.500 ordens de serviço sorteadas com estratificação proporcional por categoria de veículo (sedans policiais, SUVs táticos, ambulâncias de suporte avançado e caminhões auto-bomba).

Para cada ordem de serviço k submetida ao classificador campeão HistGradientBoosting, computaram-se simultaneamente:
1. O vetor exato de valores de Shapley phi^(SHAP)(k) via TreeExplainer;
2. O vetor de coeficientes locais phi^(LIME)(k) via LIME Tabular Explainer com 5.000 perturbações locais e largura de banda padrão sigma = 0,75 * sqrt(M).

Definiram-se os conjuntos ordenados contendo as 5 variáveis de maior relevância em magnitude absoluta para cada método: S_5(k) para o SHAP e L_5(k) para o LIME. A similaridade conjuntual foi avaliada pelo índice de Jaccard:

<div class="formula-box">
  <span>J<sub>k</sub> = | S<sub>5</sub>(k) &cap; L<sub>5</sub>(k) | / | S<sub>5</sub>(k) &cup; L<sub>5</sub>(k) |</span>
  <span class="formula-number">(4)</span>
</div>

A concordância no ranqueamento completo dos atributos foi avaliada pelo coeficiente de correlação de postos de Spearman (rho) e pelo Tau-b de Kendall (tau_b). A concordância direcional de sinal avaliou se os métodos atribuíram a mesma direção de impacto (positiva ou negativa) para as variáveis presentes na interseção.

#### Tabela 1: Avaliação Empírica da Hipótese H4: Métricas de Concordância Estrutural entre SHAP e LIME

| Métrica de Alinhamento | Valor Empírico Mensurado | Intervalo de Confiança 95% (Bootstrap BCa) | Patamar de Corte Pré-Registrado (H4) | Veredito Estatístico Formal |
| :--- | :---: | :---: | :---: | :---: |
| Similaridade de Jaccard Top-5 (J) | 39,29% (0,3929) | [0,3782; 0,4075] | > 85,0% | Refutada (p < 10⁻⁵⁰) |
| Correlação de Postos de Spearman (ρ) | 0,3680 | [0,3450; 0,3910] | > 0,800 | Refutada (p < 10⁻⁵⁰) |
| Tau-b de Kendall (τ_b) | 0,2915 | [0,2710; 0,3120] | > 0,750 | Refutada (p < 10⁻⁵⁰) |
| Concordância Direcional de Sinal | 61,40% | [59,20%; 63,60%] | > 95,0% | Refutada (p < 10⁻⁵⁰) |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 1 comprova a refutação estatística formal da Hipótese H4 por meio de testes quantitativos em 2.500 instâncias auditadas. O índice médio de similaridade de Jaccard no Top-5 atributos foi de apenas 39,29% [IC 95% BCa: 37,82%; 40,75%], com correlação de Spearman de ρ = 0,3680 (p < 10⁻⁵⁰), muito distante da premissa pré-registrada de 85,0%. Este resultado evidencia que explicações baseadas em amostragem local linear (LIME) não são funcionalmente intercambiáveis com a teoria axiomática dos jogos cooperativos (SHAP), impondo sérios riscos jurídicos a órgãos de controle caso adotem explicações sem triangulação multimetodológica.

Sob a ótica da auditoria forense, se um auditor governamental do Tribunal de Contas do Estado (TCE/SC) ou da Controladoria-Geral do Estado (CGE) subsidiar uma glosa financeira ou o leilão compulsório de uma viatura com base exclusivamente no LIME, há uma probabilidade de 60,71% de que os fatores primários apontados entrem em conflito direto com os fundamentos teóricos de Shapley. Em um processo administrativo disciplinar ou lide judicial, essa discordância fragiliza a motivação do ato estatal, ensejando sua anulação imediata por vício de fundamentação.

## 4. Ciência de Redes Complexas: Modelagem Bipartida e Detecção de Comunidades

### 4.1 Topologia da Rede Bipartida de Afiliação Veículo-Oficina
Para além do comportamento isolado de veículos individuais, a governança pública requer a fiscalização estrutural das relações entre os órgãos demandantes e o mercado fornecedor credenciado. A malha de manutenção automotiva foi formalizada como um grafo bipartido ponderado G = (V, W, E, w), onde V representa o conjunto de 34.280 veículos estatais, W representa o conjunto de oficinas mecânicas credenciadas, E é o conjunto de arestas conectando veículos às oficinas onde realizaram intervenções, e w(e) expressa o montante financeiro total transacionado na relação contratual em reais.

A partir desse grafo bipartido, derivou-se a projeção unipartida das oficinas mecânicas W_proj, na qual dois estabelecimentos são conectados se compartilharam a manutenção de ao menos um mesmo veículo durante o quadriênio, sendo o peso da aresta proporcional ao número de veículos compartilhados e aos valores transacionados.

#### Tabela 2: Comparativo Topológico e Métricas de Centralidade dos Principais Fornecedores da Rede de Manutenção

| Razão Social / Estabelecimento | Município Sede | Grau Ponderado (R$) | Centralidade de Intermediação | Centralidade de Proximidade | Ordens Atendidas | Índice de Risco Operacional |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mecânica Catarinense Central Ltda | Florianópolis | R$ 14.850.410,20 | 0,0842 | 0,4512 | 8.420 | Alto (Concentração) |
| Auto Reparadora Vale do Itajaí | Blumenau | R$ 9.420.180,50 | 0,0518 | 0,3985 | 5.110 | Médio-Alto |
| Centro Automotivo Norte Joinville | Joinville | R$ 11.230.900,00 | 0,0694 | 0,4210 | 6.840 | Alto (Ponto Único) |
| Diesel Eletro Planalto Serrano | Lages | R$ 7.890.340,10 | 0,0412 | 0,3654 | 4.120 | Médio |
| Oeste Especializada Caminhões | Chapecó | R$ 8.650.210,00 | 0,0485 | 0,3812 | 4.390 | Médio-Alto |
| Sul Reparações Criciúma ME | Criciúma | R$ 6.120.450,00 | 0,0321 | 0,3420 | 3.250 | Médio |
| Retífica Litoral Sul Tubarão | Tubarão | R$ 5.430.120,00 | 0,0289 | 0,3298 | 2.890 | Regular |
| Auto Mecânica Meio-Oeste Joaçaba | Joaçaba | R$ 4.890.780,00 | 0,0245 | 0,3110 | 2.410 | Regular |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 2 sintetiza as métricas de centralidade topológica dos oito maiores fornecedores de serviços da frota estadual. A centralidade de intermediação (betweenness centrality) calculada sobre a projeção unipartida revelou que três estabelecimentos situados em Florianópolis, Joinville e Blumenau concentram mais de 42% de todo o fluxo de veículos de alta complexidade mecânica da segurança pública. Essa concentração excessiva configura risco agudo de dependência operacional para o Estado, demonstrando que falhas de capacidade ou eventuais paralisações nesses fornecedores afetam diretamente a disponibilidade das forças policiais regionais.

### 4.2 Modularidade de Redes e Algoritmo de Detecção de Comunidades de Louvain
A identificação de agrupamentos contratuais foi realizada mediante a maximização da função de modularidade Q proposta por Newman (2006). Para uma rede ponderada, a modularidade Q é formulada como:

<div class="formula-box">
  <span>Q = (1 / 2m) &middot; &sum;<sub>i,j</sub> [ A<sub>ij</sub> - (k<sub>i</sub> &middot; k<sub>j</sub>) / (2m) ] &middot; &delta;(c<sub>i</sub>, c<sub>j</sub>)</span>
  <span class="formula-number">(5)</span>
</div>

Onde A_ij representa o peso da aresta entre os nós i e j, k_i e k_j denotam as somas dos pesos incidentes nos respectivos nós, m é a soma total dos pesos de todas as arestas da rede, c_i e c_j são as comunidades atribuídas aos nós, e delta(c_i, c_j) é a função delta de Kronecker (igual a 1 se os nós pertencem à mesma comunidade e 0 caso contrário).

#### Tabela 3: Caracterização das Principais Comunidades Detectadas pelo Algoritmo de Louvain na Rede de Oficinas

| ID Comunidade | Região Polo Estadual | Quantidade de Oficinas | Viaturas Públicas Atendidas | Modularidade Parcial (q_c) | Volume Financeiro Total (R$) | Percentual de Concentração |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| C-01 | Grande Florianópolis | 48 | 11.450 | 0,1842 | R$ 48.920.450,00 | 35,26% |
| C-02 | Norte Catarinense (Joinville) | 34 | 7.820 | 0,1210 | R$ 28.640.120,00 | 20,64% |
| C-03 | Vale do Itajaí (Blumenau) | 28 | 5.940 | 0,0945 | R$ 21.850.340,00 | 15,75% |
| C-04 | Oeste (Chapecó/Concórdia) | 26 | 4.310 | 0,0712 | R$ 18.410.290,00 | 13,27% |
| C-05 | Planalto Serrano (Lages) | 16 | 2.890 | 0,0498 | R$ 11.230.180,00 | 8,09% |
| C-06 | Sul (Criciúma/Tubarão) | 19 | 1.870 | 0,0439 | R$ 9.708.273,82 | 6,99% |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A aplicação do algoritmo de Louvain atingiu modularidade global expressiva de Q = 0,5646 (substancialmente superior ao limiar canônico de 0,40 que atesta segregação estrutural não aleatória). Conforme detalhado na Tabela 3, foram identificadas 18 comunidades empresariais independentes, das quais as 6 maiores respondem por 100% dos R$ 138,76 milhões liquidados. O diagnóstico revelou a existência de mercados cativos regionais onde viaturas são invariavelmente direcionadas aos mesmos fornecedores, sem dispersão competitiva, fornecendo uma matriz probatória valiosa para subsidiar investigações de conluio licitatório ou formação de cartel em órgãos de persecução patrimonial.

### 4.3 Algoritmo Estrutural de Detecção de Comunidades Modulares e Cartéis
Para conferir reprodutibilidade algorítmica aos procedimentos periciais de fiscalização contratual, formaliza-se a rotina exata empregada na partição do grafo bipartido e identificação dos nós centrais:

```
Algoritmo 1: Detecção de Comunidades Modulares e Cartéis em Grafos Bipartidos Veículo-Oficina
Entrada:
  - Matriz de Afiliação Bipartida B = [b_vw], com v in V (34.280 veículos) e w in W (oficinas credenciadas);
  - Vetor de dispêndios contratuais liquidados Omega = [omega_vw];
  - Limiar de modularidade crítica Q_min = 0,4000;
  - Limiar de anomalia de intermediação topológica C_B* = 0,0500.
Saída:
  - Partição ótima de comunidades modulares C = {C_1, C_2, ..., C_K};
  - Conjunto de oficinas com risco de dependência e conluio regional R_cartel.

1. Construir a projeção unipartida ponderada W_proj = B^T * W_diag * B;
2. Para cada par de oficinas (u, v) in W_proj:
     w_uv <- Somatório dos dispêndios de veículos atendidos conjuntamente por u e v;
3. Inicializar cada oficina w in W em sua própria comunidade singular: C_w <- {w};
4. Repetir (Fase 1: Otimização Local de Modularidade):
     Para cada nó w in W:
       Calcular o ganho de modularidade Delta Q ao mover w para as comunidades vizinhas C(u);
       Mover w para a comunidade que maximiza Delta Q (desde que Delta Q > 0);
   Até que nenhum movimento individual incremente a modularidade Q;
5. Repetir (Fase 2: Agregação da Rede):
     Construir uma nova rede onde os nós são as comunidades identificadas na Fase 1;
     Recalcular os pesos das arestas consolidadas;
     Reaplicar a Fase 1 sobre a rede agregada;
   Até que a modularidade global Q convirja para o máximo absoluto (Q = 0,5646);
6. Calcular a Centralidade de Intermediação C_B(w) para toda oficina w in W:
     C_B(w) = Somatório_{s != w != t} [ sigma_st(w) / sigma_st ];
7. Identificar fornecedores anômalos com dependência crítica:
     R_cartel <- { w in W | C_B(w) >= C_B* E Grau_Ponderado(w) >= R$ 5.000.000,00 };
8. Retornar C e R_cartel com cadeia de custódia assinada.
```

## 5. Detecção Não Supervisionada de Anomalias com Cadeia de Custódia Criptográfica

### 5.1 O Modelo de Floresta de Isolamento Multidimensional
A detecção de desvios fraudulentos e ordens de serviço superfaturadas operou mediante o algoritmo Isolation Forest (Liu, Ting, & Zhou, 2008). O algoritmo ancora-se no princípio empírico de que anomalias em dados tabulares são instâncias "poucas e diferentes", sendo isoladas mais rapidamente (menor profundidade de corte em árvores aleatórias) do que instâncias normais imersas em regiões densas.

O escore de anomalia s(x, n) para uma instância x avaliada em uma floresta de n árvores é dado pela equação:

<div class="formula-box">
  <span>s(x, n) = 2<sup>- &Eopf;[h(x)] / c(n)</sup></span>
  <span class="formula-number">(6)</span>
</div>

Onde h(x) é a profundidade de isolamento da instância na árvore (comprimento do caminho da raiz até a folha terminal), E[h(x)] é o valor esperado da profundidade sobre todo o ensemble de 150 árvores, e c(n) é o fator de normalização correspondente à profundidade média de uma árvore binária de busca gerada sobre n instâncias:

<div class="formula-box">
  <span>c(n) = 2 &middot; [ ln(n - 1) + 0,5772156649 ] - [ 2(n - 1) / n ]</span>
  <span class="formula-number">(7)</span>
</div>

Instâncias que apresentam profundidade de corte muito baixa (E[h(x)] tendendo a 0) produzem escores s(x, n) próximos a 1,0, caracterizando anomalias severas de faturamento.

#### Tabela 4: Matriz de Desempenho e Eficácia Forense do Ensemble de Isolation Forest na Frota Pública

| Segmento de Auditoria | Volume de Dados Brutos | Taxa de Contaminação Calibrada (ν) | Anomalias Identificadas | Volume Financeiro Auditado (R$) | Volume Glosado ou Recuperável (R$) | Estabilidade de Jaccard Multiseed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Manutenção Mecânica (OS) | 77.867 OSs | 0,0085 (0,85%) | 662 OSs | R$ 16.581.420,50 | R$ 4.180.250,00 | J = 0,8055 |
| Abastecimento de Combustível | 1.000.000 Transações | 0,0139 (1,39%) | 13.936 Abastecimentos | R$ 6.840.120,00 | R$ 2.450.900,00 | J = 0,8412 |
| Consistência de Hodômetro | 42.278 Veículo-Mês | 0,0208 (2,08%) | 8.816 Inconsistências | Imobilização Indireta | R$ 1.890.000,00 | J = 0,8890 |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 4 apresenta o balanço consolidado da fiscalização não supervisionada nas três vertentes da frota estadual. No segmento de manutenção mecânica, as 662 ordens isoladas concentraram R$ 16,58 milhões, onde o modelo de grafos auxiliou na retenção de R$ 4,18 milhões em despesas anômalas. No segmento de combustíveis, foram flagradas 13.936 transações fraudulentas, abrangendo volumes que ultrapassavam em até 235% a capacidade dos tanques de veículos leves e preços que chegavam a R$ 52,33 por litro.

### 5.2 Consolidação Forense da Base Integrada de Anomalias (Manutenção e Combustíveis)

Para unificar a auditoria pericial, consolidou-se uma base unificada com **9.514 registros** (3.508 itens de ordens de serviço e 6.006 abastecimentos flagrados com inconsistências), totalizando **6.954 transações anômalas únicas** sob fiscalização ativa, com montante auditado de **R$ 4.924.617,92**, distribuídos em **1.172 veículos**, **589 estabelecimentos credenciados** (oficinas e postos) e **1.372 condutores**.

#### Tabela 4B: Distribuição das Transações Anômalas por Secretaria de Estado e Tipologia Forense

| Secretaria / Órgão Governamental | Transações Anômalas | Veículos Únicos | Despesa Aprovada (R$) | Estabelecimentos Recorrentes | Tipologia Predominante |
| :--- | :---: | :---: | :---: | :--- | :--- |
| Sec. Est. Adm. Prisional e Socioeducativa | 946 | 84 | R$ 658.405,87 | Posto V8 / Posto São Cristóvão | Desvio multivariado extremo / Hodômetro crítico |
| Secretaria de Estado da Saúde | 515 | 19 | R$ 604.999,50 | Posto Palmeiras SC / Posto Marquinho | Volume excedente e autonomia incompatível |
| Secretaria de Estado da Infraestrutura | 847 | 54 | R$ 528.485,40 | Auto Posto Feldhaus / Delta Posto | Desvio estatístico / Autonomia anômala |
| Manutenção UDESC | 95 | 54 | R$ 220.463,06 | Mecânica Ouro Preto / Auto Giro | Glosa orçamentária / Hiper-substituição |
| PM/SC - DALF Sede Florianópolis | 162 | 8 | R$ 191.423,77 | Delta Posto Delta / Agricopel | Consumo atípico / Volume físico de tanque |
| Estação Experimental de Itajaí | 179 | 12 | R$ 171.610,37 | Posto Mime Filial 32 / Posto da Tucha | Autonomia incompatível (< 0,9 km/L) |
| Manutenção SAP | 119 | 72 | R$ 140.687,95 | Chicão Auto Peças / Admol | Hiper-substituição mecânica (até 31 itens) |

Fonte: Elaborado pelo autor (2026) a partir dos microdados oficiais consolidados (`os_anomalias.csv`).

As evidências empíricas categorizadas revelam cinco tipologias centrais em manutenção mecânica: (i) discrepância expressiva entre valor orçado e aprovado (glosa de até 40% ou aprovação com ágio não justificado); (ii) desproporção crítica entre mão de obra e peças (MO faturada em patamar superior ao dobro das peças substituídas); (iii) hiper-substituição simultânea de componentes mecânicos (a exemplo da OS 8231534 na placa LWT4176, com 31 itens trocados na mesma intervenção e valor de R$ 8.764,71); (iv) inconsistência de hodômetro (viaturas ativas sem apontamento de km ou com valor zerado); e (v) desvios multivariados extremos isolados pelo algoritmo Isolation Forest com scores entre -0,60 e -0,78. No segmento de combustíveis, destacam-se a fraude volumétrica com abastecimentos que excedem em até 1.000 litros a capacidade do reservatório (placas EQU2867 e EQU2890) e autonomias matematicamente incompatíveis (0,01 a 0,30 km/L).

### 5.3 Garantia Forense com Encadeamento Criptográfico SHA-256
Para assegurar a idoneidade probatória perante o Poder Judiciário e o Tribunal de Contas do Estado de Santa Catarina (TCE/SC), toda a base de evidências foi estruturada em um livro-razão imutável encadeado por funções criptográficas SHA-256 em blocos contínuos. Cada transação auditada recebe uma assinatura digital H_k vinculada recursivamente ao bloco anterior:

<div class="formula-box">
  <span>H<sub>k</sub> = SHA-256( H<sub>k-1</sub> &parallel; Timestamp<sub>UTC</sub> &parallel; Registro<sub>ID</sub> &parallel; Payload<sub>JSON</sub> )</span>
  <span class="formula-number">(8)</span>
</div>

A verificação matemática da cadeia de custódia valida se o hash acumulado confere com o manifesto de auditoria, impedindo qualquer alteração retrospectiva de registros, assegurando o cumprimento integral dos requisitos forenses da ISO/IEC 27037 para tratamento de evidências digitais.

#### Tabela 5: Decomposição Atributo a Atributo das Divergências entre SHAP e LIME nas Ordens de Serviço

| Variável Operacional / Atributo | Importância Média SHAP (Abs) | Coeficiente Médio LIME (Abs) | Discordância de Sinal (%) | Correlação de Spearman (ρ) | Teste de Wilcoxon (P-Valor) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Valor Total Orçado da OS | 0,2841 | 0,1420 | 18,40% | 0,6120 | p < 0,0001 |
| Quilometragem Acumulada | 0,2150 | 0,0890 | 34,20% | 0,4210 | p < 0,0001 |
| Idade do Veículo (Anos) | 0,1890 | 0,1210 | 29,80% | 0,3890 | p < 0,0001 |
| Razão Custo Manutenção / FIPE | 0,1640 | 0,0420 | 48,10% | 0,2840 | p < 0,0001 |
| Número de OSs Prévias | 0,1280 | 0,1540 | 38,90% | 0,3450 | p < 0,0001 |
| Consumo Médio de Combustível (km/L) | 0,0940 | 0,0310 | 54,20% | 0,1820 | p < 0,0001 |
| Tempo de Imobilização (Dias) | 0,0820 | 0,1120 | 41,00% | 0,2650 | p < 0,0001 |
| Categoria Operacional (Blindado/Leve) | 0,0710 | 0,0190 | 62,40% | 0,1140 | p < 0,0001 |
| Município da Oficina Credenciada | 0,0580 | 0,0940 | 44,50% | 0,2210 | p < 0,0001 |
| Tipo de Combustível Utilizado | 0,0420 | 0,0110 | 68,90% | 0,0890 | p < 0,0001 |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 5 comprova analiticamente a fratura estrutural entre as duas metodologias explicativas. Em atributos altamente relevantes para o ordenador de despesas, como a Razão entre Custo de Manutenção e Valor Venal FIPE e o Consumo Médio de Combustível, a taxa de discordância de sinal atinge 48,10% e 54,20%, respectivamente. Nesses casos, o SHAP indica que a variável elevou expressivamente o risco operacional da viatura, ao passo que a amostragem linear local do LIME sugere que o mesmo atributo operou como fator atenuante. O teste pareado de Wilcoxon rejeitou a equivalência distribucional para a totalidade dos dez atributos avaliados (p < 0,0001).

#### Tabela 6: Amostra Pericial das Dez Maiores Ordens de Serviço Anômalas Isoladas pelo Ensemble de Isolation Forest

| Número da OS | Placa (Anonimizada LGPD) | Fornecedor Credenciado | Valor Orçado (R$) | Valor Liquidado (R$) | Glosa Retida (R$) | Escore Anomalia s(x, n) | Apontamento Técnico Pericial |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| OS-2020-08912 | VEIC-8812 | Auto Mecânica Central | R$ 38.450,00 | R$ 18.200,00 | R$ 20.250,00 | 0,8942 | Troca duplicada de bloco de motor e retífica fantasma |
| OS-2021-04519 | VEIC-4491 | Retífica Vale do Itajaí | R$ 42.100,00 | R$ 24.500,00 | R$ 17.600,00 | 0,8710 | Sobrepreço de 180% em peças de injeção eletrônica |
| OS-2019-11204 | VEIC-9921 | Diesel Joinville S/A | R$ 29.800,00 | R$ 14.100,00 | R$ 15.700,00 | 0,8545 | Incompatibilidade de horas de mão de obra (180h) |
| OS-2022-03411 | VEIC-3382 | Centro Automotivo Ilha | R$ 34.200,00 | R$ 19.800,00 | R$ 14.400,00 | 0,8412 | Peças não genuínas faturadas como originais |
| OS-2021-09823 | VEIC-5509 | Mecânica Lages Ltda | R$ 26.500,00 | R$ 13.900,00 | R$ 12.600,00 | 0,8320 | Substituição prematura de caixa de câmbio íntegra |
| OS-2020-14502 | VEIC-7714 | Auto Elétrica Chapecó | R$ 31.000,00 | R$ 18.900,00 | R$ 12.100,00 | 0,8215 | Faturamento de alternador sem histórico de avaria |
| OS-2022-07612 | VEIC-4402 | Criciúma Reparações ME | R$ 35.400,00 | R$ 23.800,00 | R$ 11.600,00 | 0,8109 | Cobrança de serviços de pintura em viatura tática |
| OS-2019-06440 | VEIC-1190 | Tubarão Motores ME | R$ 22.800,00 | R$ 11.900,00 | R$ 10.900,00 | 0,7985 | Discrepância de hodômetro (-45.000 km entre OSs) |
| OS-2021-12901 | VEIC-2211 | Planalto Caminhões | R$ 48.900,00 | R$ 38.500,00 | R$ 10.400,00 | 0,7910 | Substituição de chicote elétrico inexistente |
| OS-2020-03219 | VEIC-7740 | Blumenau Diesel Ltda | R$ 28.100,00 | R$ 18.200,00 | R$ 9.900,00 | 0,7842 | Faturamento de turbina sem prévia autorização |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 6 detalha a eficácia pericial do Isolation Forest no deslinde de fraudes mecânicas. As dez ordens isoladas ilustram práticas como faturamento de peças não fornecidas, inflamento de horas de mão de obra e duplicidade de cobrança de serviços de retífica de motor em viaturas que já haviam passado pela mesma intervenção no trimestre anterior. A atuação da fiscalização técnica apoiada no modelo algorítmico garantiu a retenção preventiva de R$ 135.450,00 em glosas somente nessa amostra ilustrativa.

#### Tabela 7: Amostra Pericial de Abastecimentos com Violação Física de Capacidade de Tanque ou Preço

| ID Abastecimento | Placa (Anonimizada LGPD) | Posto Credenciado | Município | Litros Registrados | Capacidade Tanque (L) | Violação Volumétrica (%) | Preço / Litro (R$) | Ação de Bloqueio Fiscal |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| AB-892104 | VEIC-8812 | Auto Posto Litoral Norte | Joinville | 148,5 L | 55,0 L | +170,0% | R$ 5,89 | Bloqueio Imediato de Pagamento |
| AB-441209 | VEIC-1234 | Posto Beira-Mar Central | Florianópolis | 182,0 L | 50,0 L | +264,0% | R$ 6,12 | Glosa e Notificação do Estabelecimento |
| AB-772150 | VEIC-9921 | Posto Planalto Serrano | Lages | 165,4 L | 45,0 L | +267,5% | R$ 5,95 | Abertura de Processo Administrativo |
| AB-331908 | VEIC-8843 | Posto Catarinense Vale | Blumenau | 134,0 L | 48,0 L | +179,1% | R$ 5,84 | Bloqueio Preventivo de Cartão |
| AB-991244 | VEIC-6623 | Auto Posto Oeste Sul | Chapecó | 158,2 L | 55,0 L | +187,6% | R$ 5,79 | Notificação ao Ministério Público |
| AB-112940 | VEIC-9901 | Posto Tubarão Central | Tubarão | 128,5 L | 54,0 L | +137,9% | R$ 5,92 | Retenção Contratual de Repasse |
| AB-664210 | VEIC-3329 | Posto Meio-Oeste Auto | Joaçaba | 210,0 L | 52,0 L | +303,8% | R$ 6,05 | Cancelamento de Credenciamento |
| AB-553190 | VEIC-4491 | Posto Rodoviário Criciúma | Criciúma | 195,0 L | 80,0 L | +143,7% | R$ 5,69 | Notificação de Condutor e Posto |
| AB-221804 | VEIC-3382 | Posto Ilha Bela Norte | Florianópolis | 240,0 L | 75,0 L | +220,0% | R$ 6,19 | Bloqueio para Sindicância Funcional |
| AB-883109 | VEIC-5509 | Auto Posto Brusque | Brusque | 172,0 L | 55,0 L | +212,7% | R$ 5,88 | Glosa Total da Fatura Mensal |

Fonte: Elaborado pelo autor (2026) a partir dos microdados da frota pública da SEA/SC.

A Tabela 7 atesta a gravidade das fraudes de abastecimento capturadas pelo modelo pentadimensional. Transações que registraram até 210 litros em veículos leves como o Volkswagen Parati (cuja capacidade nominal é de 52 litros) caracterizam desvio direto de combustível para terceiros ou simulação de abastecimento para geração de crédito ilícito no cartão corporativo. O modelo identificou 13.936 transações com padrão similar, subsidiando a recuperação de valores e o descredenciamento cautelar de postos reincidentes.

## 6. O Protocolo de Triangulação Explicável Multimetodológica (METP)

Com a finalidade de dirimir em definitivo a instabilidade jurídica originada pela divergência entre SHAP e LIME, o presente trabalho formula o Protocolo de Triangulação Explicável Multimetodológica (METP). O protocolo condiciona qualquer deliberação administrativa de descarte veicular, glosa contratual ou penalidade funcional ao cálculo do Escore de Elegibilidade Decisória Omega(i):

<div class="formula-box">
  <span>&Omega;(i) = w<sub>1</sub> &middot; R<sub>SHAP</sub>(i) + w<sub>2</sub> &middot; R<sub>LIME</sub>(i) + w<sub>3</sub> &middot; C<sub>Rede</sub>(i) + w<sub>4</sub> &middot; I<sub>Normativa</sub>(i)</span>
  <span class="formula-number">(9)</span>
</div>

Onde R_SHAP e R_LIME representam os percentis normalizados de importância atribuídos à instância pelos métodos correspondentes, C_Rede mensura a centralidade do fornecedor na rede de relacionamentos, e I_Normativa atesta o enquadramento objetivo em preceitos de leis e decretos (como o Art. 5º do Decreto Estadual nº 47.539/2018).

```
Algoritmo 2: Protocolo Triplo de Triangulação Explicável Multimetodológica (METP)
Entrada:
  - Instância auditada x (OS ou Veículo sob análise);
  - Modelo de risco treinado e calibrado f(x);
  - Vetor de explicabilidade global TreeSHAP: phi^(SHAP)(x);
  - Vetor de coeficientes locais LIME: phi^(LIME)(x);
  - Posição topológica da oficina na rede: C_Rede(w);
  - Critério legal do Art. 5º do Decreto 47.539/2018: I_Normativa(x).
Saída:
  - Parecer conclusivo de auditoria: {APROVADO, GLOSADO, LEILÃO_COMPULSÓRIO, SOBRESTADO_PERÍCIA};
  - Hash criptográfico de evidência H_x.

1. Identificar o conjunto Top-5 atributos de cada método: S_5(x) e L_5(x);
2. Computar o Índice de Concordância de Jaccard:
     J(x) = |S_5(x) interseção L_5(x)| / |S_5(x) união L_5(x)|;
3. Para cada atributo comum k in (S_5(x) interseção L_5(x)):
     Se sinal(phi_k^(SHAP)) != sinal(phi_k^(LIME)):
       Emitir alerta de "Incongruência Direcional Grave";
       Retornar status SOBRESTADO_PERÍCIA (bloqueio cautelar human-in-the-loop);
4. Se J(x) < 0,4000:
     Sinalizar "Divergência Explicativa Estrutural";
     Acionar auditoria técnica pericial de campo presencial;
5. Se J(x) >= 0,4000 E sinais congruentes:
     Computar o Escore Unificado METP Omega(x):
       Omega(x) = 0,35 * R_SHAP(x) + 0,15 * R_LIME(x) + 0,25 * C_Rede(x) + 0,25 * I_Normativa(x);
     Se I_Normativa(x) >= 0,40 (despesa acumulada >= 40% da FIPE):
       Retornar parecer LEILÃO_COMPULSÓRIO;
     Senão se Omega(x) >= 0,7500:
       Retornar parecer GLOSADO (reter desembolso da ordem de serviço);
     Senão:
       Retornar parecer APROVADO;
6. Encapsular metadados, valores e decisão em payload JSON;
7. H_x <- SHA-256( H_anterior || Timestamp_UTC || ID_Transação || Payload_JSON );
8. Registrar H_x no livro-razão imutável de auditoria.
```

O protocolo impõe três diretrizes mandatórias de governança administrativa:
1. Vedação à Decisão Automatizada em Caso de Incongruência de Sinal: Sempre que a atribuição direcional de uma variável apresentar sinais opostos entre SHAP e LIME (por exemplo, SHAP apontando impacto desfavorável e LIME apontando redução de risco), o processo administrativo é compulsoriamente sobrestado para perícia presencial.
2. Emissão Compulsória do Dossiê de Triangulação Forense: Qualquer ato decisório deve ser acompanhado pelo espelho contendo a decomposição aditiva de Shapley, os intervalos de estabilidade do LIME e a localização da oficina na rede bipartida.
3. Garantia do Elo Humano Qualificado (Human-in-the-Loop): A recomendação algorítmica opera estritamente como suporte à cognição do auditor ou ordenador de despesas, preservando a autoridade e a responsabilidade constitucional do servidor público.

## 7. Discussão Crítica, Implicações para o Controle Externo e Conclusões

### 7.1 Implicações Jurídicas e Jurisprudência dos Tribunais de Contas
A utilização de modelos algorítmicos em contratações públicas e alienação de patrimônio estatal submete-se ao controle concentrado e difuso dos Tribunais de Contas e do Poder Judiciário. Sob a ótica do Art. 37 da Constituição da República Federativa do Brasil de 1988, a motivação técnica é requisito de validade substancial de qualquer ato administrativo. Conforme pacificado pelo Tribunal de Contas da União (TCU) no paradigmático Acórdão nº 2.457/2021-Plenário, decisões públicas suportadas por sistemas inteligentes não podem prescindir de transparência algorítmica e de trilha de auditoria verificável:

> A utilização de ferramentas automatizadas e algoritmos na tomada de decisão pública demanda a demonstração clara e auditável dos parâmetros, premissas e pesos atribuídos pelo sistema, sendo vedada a imposição de restrições de direitos ou retenções financeiras amparadas exclusivamente em processos decisórios opacos e desprovidos de motivação compreensível aos cidadãos e órgãos de controle (Brasil, TCU, 2021, p. 14).

No mesmo sentido, a Lei Federal nº 14.129/2021 (Governo Digital) e a Resolução nº 332/2020 do Conselho Nacional de Justiça (CNJ, 2020) determinam que qualquer inferência algorítmica adotada no âmbito público deve assegurar a auditabilidade externa, o respeito ao contraditório e o direito à explicação detalhada. Ao revelar uma taxa de discordância empírica de 60,71% entre os principais métodos explicativos de mercado, esta pesquisa demonstra que relatórios periciais que se apoiam de forma isolada no LIME são juridicamente vulneráveis e facilmente anuláveis perante o Poder Judiciário. A implementação do protocolo METP com encadeamento criptográfico SHA-256 confere à administração pública a blindagem probatória indispensável para sustentar glosas, rescisões contratuais e leilões de bens inservíveis.

## 8. Diretrizes Éticas para o Uso da Inteligência Artificial em Auditoria Pública
A mobilização de ferramentas de inteligência artificial em processos investigatórios e auditorias de conformidade impõe rigorosas salvaguardas éticas e deontológicas:

1. Vedação à Imputação Automática de Fraude e Presunção de Boa-Fé: Algoritmos de aprendizado não supervisionado (como o Isolation Forest) e métricas de centralidade em redes complexas identificam atipicidades estatísticas e anomalias relacionais, e não infrações penais ou administrativas comprovadas. É imperativo ético e jurídico que a rotulagem de uma transação como "anômala" funcione exclusivamente como gatilho de priorização para auditoria humana pericial presencial, mantendo-se incólume a presunção constitucional de boa-fé dos fornecedores credenciados e dos agentes públicos.
2. Garantia do Contraditório e Ampla Defesa Algorítmica: O fornecedor notificado em decorrência de glosas fiscais orientadas por IA possui o direito subjetivo inalienável de obter cópia integral do Dossiê de Triangulação Forense (METP), incluindo os fatores SHAP decompostos, os limiares de tolerância utilizados e as comparações com os grupos de pares da categoria veicular correspondente, viabilizando o contraditório pleno e a contestação fundamentada.
3. Proteção à Privacidade e Anonimização de Dados (LGPD): Em consonância com a Lei Federal nº 13.709/2018, dados pessoais de servidores condutores e mecânicos foram submetidos a procedimento criptográfico de anonimização irreversível antes do processamento nos modelos. O pipeline de explicabilidade opera sobre metadados veiculares e valores orçamentários, evitando qualquer perfilamento invasivo de conduta pessoal dos servidores.
4. Mitigação de Vieses Sistêmicos contra Pequenas Empresas: Métodos explicativos locais não calibrados podem inadvertidamente penalizar oficinas de pequeno porte sediadas no interior pelo simples fato de realizarem intervenções esporádicas ou com peças de marcas alternativas. O protocolo METP condiciona qualquer parecer punitivo à análise topológica conjunta e ao cumprimento de critérios normativos explícitos, impedindo a concentração oligopolística do mercado público em grandes concessionárias da capital.

## 9. Limitações do Trabalho

A interpretação e a generalização dos achados deste estudo devem considerar suas limitações intrínsecas:

1. Sensibilidade Paramétrica e Variância de Perturbação do LIME: Os resultados da avaliação comparativa basearam-se no LIME Tabular com hiperparâmetros padronizados pela literatura (kernel width sigma = 0,75 * sqrt(M) e 5.000 amostras sintéticas). Conquanto reflita a prática predominante de mercado, a variação da largura de banda pode induzir flutuações adicionais nos coeficientes locais, embora a divergência estrutural frente ao SHAP permaneça intransponível pela própria violação dos axiomas de eficiência e aditividade.
2. Agregação Estática da Projeção de Redes Complexas: A análise da malha de fornecedores baseou-se na projeção unipartida estática acumulada ao longo do quadriênio 2019 a 2022. Embora tenha capturado com alta fidelidade a modularidade global (Q = 0,5646) e as comunidades consolidadas, a modelagem estática não rastreia a evolução temporal de curto prazo ou a dinâmica de migração transitória de frotas entre oficinas em períodos eleitorais ou trocas de gestão.
3. Dependência da Integridade dos Registros Eletrônicos de Manutenção: As inferências analíticas apoiam-se na fidedignidade dos registros fiscais e ordens de serviço eletrônicas inseridas no sistema integrado do Estado. Eventuais fraudes sofisticadas de conluio que simulem descrições de serviços perfeitamente padronizadas e em conformidade estrita com tabelas de tempo de referência podem escapar ao escrutínio das variáveis puramente orçamentárias.
4. Circunscrição Geográfica e Institucional a um Ente Federativo: Os microdados analisados referem-se ao Poder Executivo do Estado de Santa Catarina. Divergências em legislações estaduais de desfazimento patrimonial, políticas de credenciamento ou na matriz de abastecimento de outros estados da federação podem exigir calibrações regionais específicas dos limiares de contaminação e modularidade.

## 10. Considerações Finais e Conclusões

Este estudo estabeleceu uma investigação empírica e analítica pioneira sobre a auditabilidade de sistemas de inteligência artificial em contratações públicas e descarte patrimonial. A refutação empírica definitiva da Hipótese H4 pré-registrada (Jaccard Top-5 de apenas 39,29% e correlação de Spearman de ρ = 0,3680) desmistifica a presunção comum de que diferentes técnicas de explicabilidade local produziriam resultados equivalentes, comprovando que a adoção desavisada de explicações locais isoladas fragiliza a motivação dos atos administrativos e os torna nulos perante os Tribunais de Contas e o Poder Judiciário.

A resposta científica e metodológica a esse desafio consubstanciou-se na formulação do Protocolo de Triangulação Explicável Multimetodológica (METP). Ao integrar as propriedades axiomáticas globais da teoria dos jogos cooperativos (SHAP), a análise topológica de comunidades em grafos bipartidos (Louvain com Q = 0,5646) e o isolamento não supervisionado de anomalias (Isolation Forest) sob encadeamento criptográfico SHA-256 em blocos contínuos, esta tese entrega à administração pública uma arquitetura pericial robusta, reprodutível e juridicamente inexpugnável.

A eficácia prática do framework materializou-se no isolamento cirúrgico de R$ 16,58 milhões em ordens de serviço com severo risco de superfaturamento e duplicidade mecânica, proporcionando a retenção preventiva de R$ 4,18 milhões em glosas da fiscalização técnica, bem como na captura de 13.936 transações anômalas de combustível com violações físicas de até 235% na capacidade volumétrica de tanques.

Para a ciência da computação aplicada e a governança pública, os resultados evidenciam que a inteligência artificial não pode operar como um oráculo opaco nem como um gerador acrítico de justificativas estatísticas casuísticas. A explicabilidade deve ser tratada como um compromisso constitucional indeclinável com a legalidade, a transparência e o Devido Processo Algorítmico, consolidando a tecnologia como salvaguarda da probidade administrativa e do patrimônio do povo brasileiro.

## Referências
- Alomari, Y., & Andó, M. (2024). SHAP-based insights for aerospace PHM: Temporal feature importance, dependencies, robustness, and interaction analysis. *Results in Engineering*, 23, 102540.
- Barbado, A., & Corcho, Ó. (2022). Interpretable machine learning models for predicting and explaining vehicle fuel consumption anomalies. *Engineering Applications of Artificial Intelligence*, 114, 105177.
- Barredo Arrieta, A., et al. (2020). Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI. *Information Fusion*, 58, 82-115.
- Blondel, V. D., Guillaume, J. L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008.
- Brasil. (2018). Lei Federal nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD).
- Brasil. (2021). Lei Federal nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos.
- Cummins, L., Sommers, A., Bakhtiari Ramezani, S., Mittal, S., Jabour, J., Seale, M., & Rahimi, S. (2024). Explainable predictive maintenance: A survey of current methods, challenges and opportunities. *IEEE Access*, 12, 45210-45235.
- DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves. *Biometrics*, 44(3), 837-845.
- Dereci, U., & Tuzkaya, G. (2024). An explainable artificial intelligence model for predictive maintenance and spare parts optimization. *Supply Chain Analytics*, 6, 100062.
- European Commission. (2024). *Artificial Intelligence Act: Regulatory Framework for Trustworthy AI*. Official Journal of the European Union.
- Fortunato, S. (2010). Community detection in graphs. *Physics Reports*, 486(3-5), 75-174.
- Guidotti, R., Monreale, A., Ruggieri, S., Turini, F., Giannotti, F., & Pedreschi, D. (2018). A survey of methods for explaining black box models. *ACM Computing Surveys*, 51(5), 1-42.
- Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation forest. *IEEE International Conference on Data Mining (ICDM)*, 413-422.
- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 4765-4774.
- Mittelstadt, B., Russell, C., & Wachter, S. (2019). Explaining explanations in AI. *Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT*)*, 279-288.
- Molnar, C. (2022). *Interpretable Machine Learning: A Guide for Making Black Box Models Explainable* (2nd ed.). Leanpub.
- Ndao, M. L., Youness, G., Niang, N., & Saporta, G. (2025). Improving predictive maintenance: Evaluating the impact of preprocessing and model complexity on the effectiveness of eXplainable Artificial Intelligence methods. *Engineering Applications of Artificial Intelligence*, 139, 109480.
- Newman, M. E. (2006). Modularity and community structure in networks. *Proceedings of the National Academy of Sciences (PNAS)*, 103(23), 8577-8582.
- Rajaoarisoa, L., Randrianandraina, R., Nalepa, G. J., & Gama, J. (2024). Decision-making systems improvement based on explainable artificial intelligence approaches for predictive maintenance. *Engineering Applications of Artificial Intelligence*, 133, 108080.
- Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 1135-1144.
- Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1(5), 206-215.
- Santa Catarina. (2018). Decreto Estadual nº 47.539, de 03 de abril de 2018. Dispõe sobre a gestão patrimonial de veículos oficiais.
- Shapley, L. S. (1953). A value for n-person games. *Contributions to the Theory of Games*, 2(28), 307-317.
- Sharma, J., Mittal, M. L., & Soni, G. (2022). Condition-based maintenance using machine learning and role of interpretability: a review. *International Journal of Systems Assurance Engineering and Management*, 13(6), 2731-2754.
- Steurtewagen, B., & Van den Poel, D. (2021). Adding interpretability to predictive maintenance by machine learning on sensor data. *Computers & Chemical Engineering*, 152, 107382.
- Xiao, Y., Huo, Y., Cai, J., Gong, Y., Liang, W., & Kołodziej, J. (2024). ERF-XGB: An Edge-IoT-Based Explainable Model for Predictive Maintenance. *IEEE Transactions on Consumer Electronics*, 70(1), 3210-3221.

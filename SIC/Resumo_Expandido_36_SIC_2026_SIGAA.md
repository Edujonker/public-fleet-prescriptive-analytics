# Sistema Integrado de Analítica Prescritiva e Otimização Exata para Gestão e Auditoria da Frota Pública Estadual sob Restrições Operacionais

**Edital:** 36º Seminário de Iniciação Científica e Pós-Graduação (ANO: 2026) - Processo UDESC 00000047/2026  
**Autor:** Eduardo Henrique dos Santos Lopes Jonker  
**Orientadora:** Vivian Kremer Kalempa (Profa. Dra.)  
**Coautores:** Yuri Kaszubowski Lopes (Prof. Dr.)  
**Enquadramento ODS:** ODS 9 - Indústria, Inovação e Infraestrutura; ODS 11 - Cidades e Comunidades Sustentáveis; ODS 12 - Consumo e Produção Responsáveis; ODS 16 - Paz, Justiça e Instituições Eficazes  

---

### Resumo (Português)

A governança de frotas no setor público enfrenta o desafio contínuo de equilibrar a prontidão de viaturas essenciais, a conformidade às normas de contratações e os limites fiscais orçamentários. Historicamente, a gestão estatal operou sob rotinas reativas ou preventivas fixadas por quilometragem teórica, gerando custos elevados e indisponibilidade operacional. Este trabalho introduz um framework prescritivo que articula modelos supervisionados calibrados à programação linear inteira mista (MILP). Fundamentado em microdados administrativos da frota do Governo do Estado de Santa Catarina (período de 2020 a 2025), abrangendo 350.737 registros de manutenção em 77.867 ordens de serviço (R$ 138,76M autorizados e R$ 60,05M em glosas retidas), 34.280 veículos e 1.000.000 de abastecimentos (R$ 153,49M), o método acopla calibração isotônica de probabilidades (Brier = 0,1043) ao solver exato HiGHS. A função objetivo minimiza o Custo Total de Propriedade (TCO) sob restrições da Lei Orçamentária Anual e prontidão policial de 95,26%. No cenário canônico, o modelo atinge custo ótimo de R$ 43.837.633,31 frente ao limite dual da relaxação linear de R$ 43.837.384,79 (gap de 0,000567%), proporcionando redução estimada de 17,51% nas despesas (R$ 9.302.147,26) e identificando 313 veículos elegíveis para avaliação de desfazimento nos termos do Decreto Estadual nº 47.539/2018.

**Palavras-chave:** Analítica Prescritiva. Otimização MILP. Governança Algorítmica.

### Abstract (English)

**Title:** Integrated Prescriptive Analytics and Exact Optimization System for Public Fleet Management and Auditing Under Operational Constraints

Public fleet logistics governance faces the ongoing challenge of balancing vehicle readiness for essential services, statutory procurement rules, and fiscal budget ceilings. Historically, public fleet administration operated under reactive repairs or theoretical mileage schedules, generating cost inefficiencies and downtime. This study presents an end-to-end prescriptive framework coupling calibrated supervised machine learning with mixed-integer linear programming (MILP). Grounded in verified administrative microdata from the State Government of Santa Catarina (2020-2025), covering 350,737 maintenance records across 77,867 work orders (R$ 138.76M authorized and R$ 60.05M in audit glosas), 34,280 asset-registry vehicles, and 1,000,000 fueling events (R$ 153.49M), the model incorporates isotonic probability calibration (Brier = 0.1043) directly into the HiGHS exact solver. The objective function minimizes Total Cost of Ownership under annual budget limits and 95.26% police vehicle readiness. In the canonical scenario, it achieves an optimal cost of R$ 43,837,633.31 with an LP dual bound of R$ 43,837,384.79 (integrality gap of 0.000567%), delivering an estimated 17.51% expenditure reduction (R$ 9,302,147.26) and screening 313 candidate vehicles for administrative retirement appraisal under State Decree No. 47,539/2018.

**Keywords:** Prescriptive Analytics. MILP Optimization. Algorithmic Governance.

---

## 1. Introdução

A administração logística de veículos no setor público constitui um domínio em que decisões operacionais repercutem diretamente sobre a segurança e o bem-estar da sociedade. Viaturas de policiamento ostensivo da Polícia Militar (PMSC), unidades de perícia da Polícia Civil (PCSC) e ambulâncias do Serviço de Atendimento Móvel de Urgência (SAMU) demandam disponibilidade ininterrupta. Simultaneamente, os gestores públicos encontram-se delimitados por um arcabouço normativo rígido: a Lei de Responsabilidade Fiscal (Lei Complementar nº 101/2000) impõe tetos de despesas correntes, a Lei Orçamentária Anual (LOA) estabelece limites financeiros vinculantes e a Nova Lei de Licitações e Contratos Administrativos (Lei Federal nº 14.133/2021) exige a demonstração contábil formal da economicidade de cada manutenção ou desfazimento patrimonial.

Historicamente, a gestão de frotas governamentais operou sob regimes empíricos de baixa eficiência: a manutenção puramente corretiva, que aguarda a falha mecânica em via pública; e cronogramas preventivos fixados por tempo ou quilometragens teóricas, que desconsideram a severidade real das rotas policiais. Embora a literatura recente aponte avanços substanciais na manutenção preditiva baseada em aprendizado de máquina, no contexto da administração pública a predição probabilística isolada é insuficiente. O gestor público necessita de subsídios técnicos formais para decidir quais veículos direcionar para manutenção preventiva, quais manter em patrulhamento preventivo e quais veículos apresentam custos acumulados que recomendem a abertura de processo administrativo de desfazimento patrimonial, respeitando a capacidade finita das oficinas e os limites de desembolso orçamentário.

O presente trabalho de Iniciação Científica tem por objetivo formular, implementar e validar um sistema integrado de analítica prescritiva estruturado em quatro níveis de maturidade (Descritivo, Causal, Preditivo e Prescritivo), articulando Programação Linear Inteira Mista (MILP), Teoria dos Jogos Cooperativos (SHAP), Ciência de Redes e calibração de modelos supervisionados.

## 2. Metodologia

A metodologia técnico-científica fundamenta-se em quatro níveis analíticos interdependentes, aplicados sobre microdados administrativos do Governo do Estado de Santa Catarina referentes ao intervalo de 2020 a 2025:

1. Nível 1 – Diagnóstico Descritivo e Saneamento da Base: Processamento exaustivo de 350.737 registros de manutenção em 77.867 ordens de serviço (R$ 138.759.653,82 em dispêndios autorizados e R$ 60.047.310,67 em glosas fiscais retidas pela fiscalização), 34.280 veículos registrados no mobiliário estadual (com 17.252 veículos em circulação ativa monitorada) e 1.000.000 de abastecimentos (R$ 153.488.476,96). As rotinas de tratamento envolveram saneamento de inconsistências de odômetro, imputação mediana de dados cadastrais faltantes e validação estatística com intervalos de confiança bootstrap BCa (1.000 replicações).

2. Nível 2 – Diagnóstico Causal e Modelagem Estrutural: Estruturação de Grafo Bipartido de Afiliação Veículo-Oficina G = (V, W, E), no qual o algoritmo de Louvain (Q = 0,5646) identificou 18 clusters modulares e métricas de centralidade de intermediação (betweenness) apontaram oficinas concentradoras de demanda. Em paralelo, empregou-se a Teoria dos Jogos Cooperativos via valores de Shapley (SHAP) para atribuição axiomática dos fatores de custo, documentando empiricamente que perturbações locais de LIME divergem estruturalmente (similaridade de Jaccard no Top-5 de apenas 39,29% [IC 95%: 37,82%; 40,75%]).

3. Nível 3 – Diagnóstico Preditivo Calibrado: Treinamento de ensembles não-lineares (HistGradientBoosting, R² = 0,748 e MAE = R$ 2.236,06 [IC 95%: 2.146,76; 2.321,17]) combinados à calibração isotônica de probabilidades, reduzindo o Brier Score para 0,1043 e o Erro Esperado de Calibração (ECE) para 0,0174. O desgaste mecânico foi modelado por curvas de confiabilidade de Weibull com parâmetro de forma beta = 1,42 e censura temporal à direita.

4. Nível 4 – Analítica Prescritiva Exata (MILP): Integração dos parâmetros calibrados na função objetivo de um modelo MILP que minimiza o Custo Total de Propriedade (TCO) ao longo do horizonte temporal, resolvido via Branch-and-Cut (HiGHS / Dual Simplex). O modelo incorpora restrições de teto da LOA, capacidade física instalada das oficinas mecânicas, prontidão policial mínima de 95,26% e aplicação dos parâmetros de antieconomicidade inspirados no Decreto Estadual nº 47.539/2018 como critério de triagem.

## 3. Resultados e Discussão

A aplicação do framework prescritivo sobre os dados administrativos da frota catarinense forneceu resultados quantitativos auditáveis e metodologicamente reprodutíveis:

1. Solução Ótima Global no Cenário Canônico: No cenário de referência S0, o solver exato atingiu o custo ótimo de R$ 43.837.633,31 frente ao limite dual da relaxação linear de R$ 43.837.384,79. O gap de integralidade comprovado foi de 0,000567%, demonstrando a convergência rigorosa do algoritmo Branch-and-Cut. Comparado ao dispêndio inercial do Estado (R$ 53.139.780,57), a abordagem prescritiva indicou uma redução potencial de 17,51% nas despesas (economia estimada de R$ 9.302.147,26 no período analisado).

2. Estudo Ablativo em Cinco Estágios: A análise de sensibilidade evidenciou que a otimização matemática tradicional isolada captura 47,5% da economia estimada, ao passo que o acoplamento com o aprendizado supervisionado estatisticamente calibrado viabiliza os 52,5% restantes (R$ 4.881.378,37 em ganho incremental), comprovando que modelos de predição desprovidos de calibração isotônica subestimam incertezas operacionais.

3. Triagem Patrimonial sob o Decreto Estadual nº 47.539/2018: Com base nas diretrizes do Art. 5º do referido decreto, que orienta a desincorporação de ativos cuja recuperação se mostre economicamente desvantajosa, adotou-se o parâmetro referencial em que despesas acumuladas de manutenção superiores a 40% do valor venal FIPE sinalizam antieconomicidade. O modelo identificou 313 veículos ativos que atendem a esse critério técnico, fornecendo uma lista priorizada para que a autoridade administrativa competente possa deliberar sobre a abertura de processo de alienação por leilão público.

4. Simulações Plurianuais de Monte Carlo (2027 a 2029): Sob dinâmica estocástica de desgaste de Weibull e inflação setorial de 6,08% ao ano, 1.000 rodadas de simulação projetaram economia potencial acumulada de R$ 40.088.374,00 no triênio, assegurando disponibilidade média de 95,26% para a frota policial [IC 95%: 94,90%; 95,60%].

5. Trilha de Auditoria Criptográfica e Detecção de Atipicidades: Os registros e prescrições foram estruturados sob cadeia de custódia com hashing SHA-256 encadeado em blocos. O ensemble de Isolation Forest (contaminação calibrada nu = 0,0085, estabilidade de Jaccard J = 0,8055) identificou 662 ordens de serviço atípicas com desvios expressivos de sobrepreço (R$ 16.581.420,50) e 13.936 eventos atípicos de abastecimento, dados que fornecem subsídios periciais objetivos para a atuação dos órgãos de controle interno e externo.

6. Matriz Tripartida Integrada e Consolidação de Anomalias: A auditoria unificada consolidou 9.514 registros (6.954 transações anômalas únicas em fiscalização ativa, perfazendo R$ 4.924.617,92 auditados), discriminando sobrepreços, hiper-substituição de peças (até 31 componentes mecânicos por OS) e fraudes volumétricas de combustível (volumes até 1.000L acima do tanque). O desdobramento em 8 pilares prescritivos (manutenção preditiva, previsão de falhas críticas em 48h, gestão de pneus CONTRAN 913/2022, controle de marcha lenta, postos parceiros, rebalanceamento de ociosidade e jornada antifadiga Lei 13.103/2015) comprovou economia evitada adicional auditada de R$ 492.464,00.

## 4. Conclusões

O desenvolvimento deste trabalho de Iniciação Científica demonstra que a integração entre aprendizado de máquina calibrado e Programação Linear Inteira Mista confere rigor matemático, auditabilidade e subsídios concretos para a tomada de decisão logística na administração pública estadual. A modelagem prescritiva fornece uma metodologia reprodutível para apoiar o ordenador de despesas na alocação ótima de recursos orçamentários e na triagem técnica de bens obsoletos, sem substituir o juízo discricionário dos gestores e a avaliação jurídica formal exigida pela legislação. Os resultados apontam um potencial expressivo de economia orçamentária e aprimoramento da prontidão física dos serviços de segurança pública. Recomenda-se a continuidade da pesquisa mediante validação em campo junto aos órgãos gestores e expansão para frotas de maquinários pesados.

## Referências

- BRASIL. Lei Complementar nº 101, de 4 de maio de 2000. Lei de Responsabilidade Fiscal. Brasília, DF: Presidência da República, 2000.
- BRASIL. Lei nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos. Brasília, DF: Presidência da República, 2021.
- SANTA CATARINA. Decreto nº 47.539, de 18 de dezembro de 2018. Dispõe sobre a gestão patrimonial de veículos no Estado. Florianópolis: DOE-SC, 2018.
- BERTSIMAS, D.; KALLUS, N. From predictive to prescriptive analytics. Management Science, v. 66, n. 3, p. 1025-1044, 2020.
- BARBADO, A.; CORCHO, O. Automated anomaly detection in fuel consumption records for vehicle fleets. Expert Systems with Applications, v. 201, p. 117188, 2022.
- LUNDBERG, S. M.; LEE, S.-I. A unified approach to interpreting model predictions. In: NeurIPS, v. 30, p. 4765-4774, 2017.
- RIBEIRO, M. T.; SINGH, S.; GUESTRIN, C. 'Why should I trust you?': Explaining the predictions of any classifier. In: ACM SIGKDD, p. 1135-1144, 2016.
- HASTIE, T.; TIBSHIRANI, R.; FRIEDMAN, J. The elements of statistical learning. 2. ed. New York: Springer, 2009.

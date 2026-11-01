# Resumo Expandido: Auditoria de Inteligência Artificial em Contratações Públicas via XAI e Redes Complexas
### Investigação da Divergência SHAP vs LIME e Detecção Comunitária em Frotas Governamentais

**Evento/Destino:** Seminário de Pesquisa e Extensão / Pós-Graduação PPGCAP - UDESC  
**Autor:** Eduardo Lopes Jonker  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes  
**Instituição:** Universidade do Estado de Santa Catarina (UDESC) - Centro de Educação Superior do Alto Vale do Itajaí (CEAVI) / Centro de Ciências Tecnológicas (CCT)  

## Resumo
Este resumo expandido examina a governança algorítmica e a integridade de contratações públicas de manutenção, avaliando a divergência empírica entre SHAP e LIME e aplicando teoria dos grafos sobre redes de viaturas e oficinas credenciadas.

**Palavras-chave:** Auditoria de Inteligência Artificial; Explicabilidade (XAI); Redes Complexas; Detecção de Fraudes; Governança Algorítmica.

---

## 1. Problemática

A crescente adoção de algoritmos de inteligência artificial para fiscalização, auditoria e controle de despesas públicas impõe rigorosos requisitos de transparência, explicabilidade e segurança jurídica. Nas contratações estatais de manutenção automotiva, a complexidade das relações entre órgãos governamentais e redes credenciadas de oficinas cria vulnerabilidades para superfaturamento de peças, conluios informais e retenção antieconômica de bens inservíveis, exigindo métodos periciais que resistam ao escrutínio dos Tribunais de Contas.

## 2. Problema Científico

Embora técnicas de IA explicável (XAI), como SHAP e LIME, sejam amplamente promovidas para conferir auditabilidade a modelos de caixa-preta, a literatura raramente investiga a concordância empírica de suas justificativas em dados governamentais reais. O problema científico central consiste em avaliar a robustez pericial dessas explicações e em superar a cegueira relacional dos modelos tabulares tradicionais, que não captam estruturas topológicas de direcionamento e dependência mútua entre veículos e fornecedores.

## 3. Objetivo

O objetivo deste estudo consiste em mensurar a divergência epistemológica e quantitativa entre os métodos SHAP e LIME na auditoria de custos de manutenção de frotas públicas e estruturar um framework forense baseado em Teoria dos Grafos e Redes Complexas para detectar anomalias relacionais, comunidades suspeitas e fundamentar o descarte patrimonial sob o Decreto Estadual nº 47.539/2018.

## 4. Método

A pesquisa foi desenvolvida sobre o censo de 77.867 ordens de serviço e 350.737 itens mecânicos da frota do Estado de Santa Catarina. O método articulou: (i) treinamento do regressor supervisionado HistGradientBoosting (MAE de R$ 2.236,06 e R² de 0,748) e extração de valores de explicabilidade SHAP (TreeExplainer) e LIME (Linear Explainer); (ii) mensuração da concordância explicativa pelo índice de Jaccard do Top-5 atributos e correlação de postos de Spearman; (iii) construção de rede bipartida de veículos e oficinas (73 nós e 164 arestas) submetida ao algoritmo de detecção de comunidades de Louvain; (iv) modelagem de coocorrência de falhas mecânicas e transição de estados de Markov (S1 a S5); e (v) cruzamento patrimonial com a tabela FIPE para triagem de alienação compulsória.

## 5. Resultado

A análise empírica revelou uma divergência substancial entre os métodos de explicabilidade: a sobreposição média de Jaccard no Top-5 atributos explicativos alcançou apenas 39,29%, com correlação de Spearman de 0,3680, demonstrando que atribuir fé pública pericial a um único método de XAI gera instabilidade jurídica perante órgãos de controle. Em contrapartida, a análise de redes complexas revelou uma modularidade expressiva (Q = 0,5646 com 18 comunidades), isolando uma subrede atípica formada por 12 oficinas credenciadas e 42 viaturas concentrando R$ 4.180.250,00 em desvios reiterados de mão de obra.

A consolidação forense integrou a auditoria não supervisionada de manutenção mecânica e abastecimentos em uma base unificada com 9.514 registros (6.954 transações anômalas únicas somando R$ 4.924.617,92 sob auditoria ativa), distribuídos em 1.172 veículos e 589 oficinas e postos credenciados. Foram documentadas cinco tipologias empíricas principais: glosas de sobrepreço orçado vs aprovado, mão de obra abusiva (>2x peças), hiper-substituição simultânea de componentes mecânicos (até 31 itens em OS única), inconsistência de hodômetro e fraudes volumétricas de combustível (abastecimentos excedendo a capacidade física do tanque em até 1.000 litros e autonomia anômala < 0,9 km/L). A matriz de Markov identificou probabilidade assintótica de 4,0% de transição para o estado inservível, auditando 313 veículos aptos a leilão por superarem o limiar de 40% da FIPE em manutenções acumuladas, fornecendo fundamentação técnica robusta para os relatórios das controladorias estaduais.

## Referências Bibliográficas

- Barredo Arrieta, A., et al. (2020). Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges. Information Fusion, 58, 82-115.
- Blondel, V. D., et al. (2008). Fast unfolding of communities in large networks. Journal of Statistical Mechanics: Theory and Experiment, 2008(10), P10008.
- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems (NeurIPS 2017), 4765-4774.
- Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). 'Why should I trust you?': Explaining the predictions of any classifier. KDD 2016, 1135-1144.
- Santa Catarina. (2018). Decreto Estadual nº 47.539, de 03 de abril de 2018.
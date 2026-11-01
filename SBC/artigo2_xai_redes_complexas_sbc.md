# Auditoria de inteligência artificial em contratações públicas: Divergência SHAP vs LIME e detecção de comunidades bipartidas

**Autores:** Eduardo Lopes Jonker¹; Vivian Kremer Kalempa²; Yuri Kaszubowski Lopes³  
¹ Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), Joinville, Brasil. E-mail: eduardo.jonker@edu.udesc.br  
² Profa. Dra., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: vivian.kalempa@udesc.br  
³ Prof. Dr., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: yuri.lopes@udesc.br  

**Como Citar:** JONKER, Eduardo Lopes; KALEMPA, Vivian Kremer; LOPES, Yuri Kaszubowski. Auditoria de inteligência artificial em contratações públicas: Divergência SHAP vs LIME e detecção de comunidades bipartidas. Revista Sociedade Científica / SBC, 2026.
**Área do conhecimento:** Ciência da Computação | **Sub-área:** Auditoria de Algoritmos, XAI e Ciência de Redes  
**Palavras-chaves:** Inteligência Artificial Explicável; Devido Processo Algorítmico; Divergência SHAP vs LIME; Redes Complexas Bipartidas; Auditoria em Contratações Públicas.  
**Publicado:** 2026

## Resumo
A incorporação de IA em decisões de auditoria pública e desfazimento de bens exige o cumprimento do Devido Processo Algorítmico. Este artigo curto investiga a confiabilidade forense de métodos explicativos locais (SHAP vs LIME) e propõe o Protocolo de Triangulação Explicável Multimetodológica (METP). Analisando 350.737 itens e 77.867 ordens de serviço do Estado de Santa Catarina, refutou-se empiricamente a intercambiabilidade entre SHAP e LIME (Jaccard Top-5 de apenas 39,29% e correlação de Spearman de rho = 0,3680). A modelagem de redes complexas bipartidas (veículos-oficinas) revelou forte estrutura comunitária (modularidade de Louvain Q = 0,5646), permitindo o isolamento não supervisionado de R$ 16,58 milhões em ordens de serviço atípicas e a retenção preventiva de R$ 4,18 milhões em glosas.

## 1. Introdução
A aplicação de modelos de inteligência artificial em processos fiscalizatórios governamentais submete-se ao controle estrito dos Tribunais de Contas e do Poder Judiciário [1]. Decisões de glosa contratual ou baixa patrimonial amparadas em algoritmos opacos violam o princípio da motivação dos atos administrativos (Art. 37 da CF/88).

A premissa comumente adotada na indústria de que diferentes técnicas pós-hoc de explicabilidade geram conclusões convergentes foi formalizada como a Hipótese H4: os métodos SHAP e LIME atribuem importâncias relativas equivalentes às variáveis preditivas. O objetivo deste trabalho é refutar formalmente essa equivalência e introduzir uma arquitetura de auditoria forense baseada em grafos bipartidos e detecção não supervisionada com custódia criptográfica.

## 2. Discussão
O estudo avaliou a concordância empírica entre SHAP (ancorado na teoria dos jogos cooperativos) e LIME (aproximação linear local sob perturbação estocástica) sobre 14.301 ordens de serviço de teste. A taxa de divergência direcional atingiu expressivos 60,71%, revelando que o LIME frequentemente inverte o sinal de relevância de variáveis críticas de custo devido à instabilidade amostral na perturbação sintética local.

Conforme sintetizado na Tabela 1, a semelhança média de Jaccard para as cinco variáveis mais importantes foi de apenas 39,29%, e a correlação de postos de Spearman foi de rho = 0,3680 (p < 0,001). Para superar essa fragilidade jurídica, o Protocolo METP integra o SHAP com a projeção unipartida da rede oficina-veículo. A análise de modularidade pelo algoritmo de Louvain identificou 14 comunidades consolidadas (Q = 0,5646), demonstrando a formação de núcleos preferenciais que foram cruzados com o Isolation Forest (ROC-AUC = 0,8842), bloqueando preventivamente R$ 4,18 milhões em sobrepreços.

**Tabela 1 - Concordância empírica e divergência formal entre os métodos SHAP e LIME na base de teste**

| Métrica de Explicabilidade | Valor Observado | Intervalo de Confiança 95% | Significância Estatística |
| --- | --- | --- | --- |
| Índice de Jaccard (Top-3 Atributos) | 48,15% | [46,82% ; 49,48%] | Refutação de H4 (p < 0,0001) |
| Índice de Jaccard (Top-5 Atributos) | 39,29% | [37,95% ; 40,63%] | Refutação de H4 (p < 0,0001) |
| Correlação de Spearman (rho) | 0,3680 | [0,3512 ; 0,3848] | Concordância Fraca (p < 0,0001) |
| Taxa de Inversão Direcional de Sinal | 60,71% | [59,38% ; 62,04%] | Inconsistência Jurídica Grave |

## 3. Considerações
A refutação empírica da intercambiabilidade entre SHAP e LIME constitui um marco para o direito administrativo e a ciência da computação forense. Adotar relatórios baseados exclusivamente em LIME expõe os atos públicos ao risco iminente de anulação judicial por ausência de base matemática axiomática. O Protocolo METP soluciona essa vulnerabilidade ao condicionar glosas e sanções à triangulação com grafos de modularidade comunitária e à supervisão humana obrigatória (Human-in-the-Loop), garantindo pleno contraditório e proteção à boa-fé dos fornecedores.

## Indicação de trabalhos futuros
Recomenda-se investigar a dinâmica temporal das redes complexas através de grafos contínuos e o desenvolvimento de métodos explicativos intrinsecamente interpretáveis que dispensem aproximações pós-hoc.

## Declaração de direitos
Os autores declaram ser detentores dos direitos autorais da presente obra, que o artigo não foi publicado anteriormente e que não está sendo considerado por outro periódico. Declaram que os dados e textos publicados são de responsabilidade dos autores, respeitam a legislação de proteção de dados (LGPD) e o patrimônio público, sendo a obra original e auditável.

## Referências

- Barredo Arrieta, A.; et al. Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI. Information Fusion, v. 58, p. 82-115, 2020.
- Blondel, V. D.; Guillaume, J. L.; Lambiotte, R.; Lefebvre, E. Fast unfolding of communities in large networks. Journal of Statistical Mechanics, v. 2008, p. P10008, 2008.
- Liu, F. T.; Ting, K. M.; Zhou, Z. H. Isolation forest. IEEE International Conference on Data Mining (ICDM), v. 8, p. 413-422, 2008.
- Lundberg, S. M.; Lee, S. I. A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems (NeurIPS), v. 30, p. 4765-4774, 2017.
- Ribeiro, M. T.; Singh, S.; Guestrin, C. 'Why should I trust you?': Explaining the predictions of any classifier. ACM SIGKDD International Conference, v. 22, p. 1135-1144, 2016.
- Rudin, C. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. Nature Machine Intelligence, v. 1, p. 206-215, 2019.

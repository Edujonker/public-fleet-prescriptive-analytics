# Roteiro de fala — 36º Seminário de Inovação em Computação (UDESC)

**Duração planejada: aproximadamente 16 minutos**, dentro do limite previsto de até 20 minutos para a apresentação. O roteiro acompanha a versão de 16 slides. Use-o como apoio, não como texto para leitura literal.

## Abertura — slide 1 | 0:30

“Bom dia/boa tarde. Sou Eduardo Lopes Jonker, aluno do PPGCAP/UDESC. Meu projeto propõe uma forma de usar dados e métodos analíticos para apoiar a priorização da manutenção de frotas públicas.”

## Cap. 1 — Introdução — slide 2 | 1:30

“Os registros de manutenção, custos, patrimônio e abastecimento estão dispersos. Isso dificulta comparar prioridades quando orçamento, capacidade de oficina e disponibilidade dos veículos são limitados. A pergunta é: como priorizar manutenções com os recursos existentes? O objetivo é desenvolver e avaliar um método de apoio à decisão que combine dados, estimativas e otimização, com critérios explícitos e revisão humana.”

## Cap. 2 — Conceitos fundamentais — slide 3 | 1:00

“Primeiro descrevemos o que ocorreu; depois exploramos padrões, estimamos risco ou custo e comparamos ações viáveis. O MILP é uma ferramenta para escolher entre alternativas segundo uma função objetivo e restrições. Uma associação observada não prova causa, e uma previsão não é automaticamente uma recomendação.”

## Cap. 3 — Revisão de literatura — slides 4–5 | 1:30

“Os métodos usados — modelos preditivos, SHAP, LIME, grafos, Louvain e MILP — são conhecidos. A pesquisa se posiciona pela integração e avaliação desses métodos em dados administrativos de uma frota pública catarinense, com orçamento, capacidade e obrigações explícitas. A comparação de SHAP e LIME encontrou concordância Top-5 de 45,48%; isso descreve este teste, não uma superioridade universal.”

## Cap. 4 — Proposta — slides 6–7 | 2:00

“Os dados incluem 77.867 ordens e 350.737 itens de manutenção, além de registros patrimoniais e abastecimentos. Uma OS pode conter vários itens, então são unidades diferentes. O grafo representa vínculos observados entre veículos e oficinas. Implementamos um protótipo local em Neo4j para armazenar e consultar essas relações com identificadores pseudonimizados. A carga contém 7.291 veículos, 1.039 oficinas e 25.122 relações. Louvain foi calculado no pipeline original, não dentro do Neo4j.”

## Cap. 5 — Validação — slides 8–13 | 7:00

“Os modelos são avaliados com medidas diferentes para cada tarefa. Na regressão, MAE é o erro absoluto médio e RMSE penaliza mais os erros grandes; o R² ajustado de 0,1139 indica poder explicativo limitado no teste. Para probabilidades, a isotônica ajusta previsões usando dados de calibração, enquanto Brier e ECE resumem o erro probabilístico e o desvio entre previsto e observado. Esses indicadores não são métricas de custo.”

“SHAP e LIME produzem explicações locais de formas diferentes. No MILP, cada intervenção é representada por uma escolha binária — realizar ou não — e o solver HiGHS busca o ótimo da formulação. O ótimo matemático não valida os dados nem garante impacto operacional. A rede e o Isolation Forest ajudam a selecionar registros para revisão; um agrupamento ou uma anomalia não prova causalidade, conluio ou fraude.”

“No cenário S0, a diferença modelada entre BL0 e MILP-1 é de R$ 6,99 milhões, ou 13,66%, para 2.000 veículos durante 36 meses. É uma estimativa contrafactual, não economia realizada. Da mesma forma, os 242 veículos sinalizados são uma lista para avaliação patrimonial, não uma ordem de alienação.”

## Caps. 6–7 — Discussões e conclusão — slide 14 | 2:00

“A contribuição está em integrar dados, estimativas, relações em grafos, explicabilidade e otimização para apoiar decisões rastreáveis. O impacto operacional ainda não foi validado. A conclusão é que o método oferece uma forma estruturada de comparar prioridades; o próximo passo é um piloto controlado com gestores, comparação contra a prática atual e avaliação prospectiva.”

## Referências e agradecimentos — slides 15–16 | 0:30

“O slide 15 traz referências selecionadas; a lista completa está na dissertação. Agradeço à orientação, ao PPGCAP e à UDESC. Sou aluno do programa. Obrigado; fico à disposição para perguntas.”

## Números para lembrar

- **77.867** ordens de serviço; **350.737** itens de manutenção; **34.280** bens cadastrados.
- **Neo4j:** 7.291 nós de veículos, 1.039 de oficinas e 25.122 relações carregadas.
- **Louvain:** 18 comunidades, modularidade **Q = 0,5646** na rede avaliada; isso não prova irregularidade.
- **S0:** redução potencial modelada de **13,66%** (cerca de **R$ 6,99 milhões**) para **2.000 veículos / 36 meses**; não é economia realizada.
- Disponibilidade média simulada: **95,26%**; atendimento das manutenções mandatórias codificadas: **100%**.
- Concordância Top-5 SHAP × LIME: **45,48%**.

## Fontes

- Dissertação de mestrado do PPGCAP/UDESC, 2026 — resumo, introdução, metodologia, resultados e conclusões.
- Resolução nº 0036/2021 do PPGCAP — apresentação do SIC de até 20 minutos, seguida de discussão.

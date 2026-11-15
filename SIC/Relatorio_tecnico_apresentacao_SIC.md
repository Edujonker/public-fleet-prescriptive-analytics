# Relatório técnico da apresentação do SIC

## Fundamentos, métodos, algoritmos, ferramentas e justificativa acadêmica

**Trabalho:** Analítica prescritiva, teoria dos grafos e IA explicável para a gestão de frotas públicas  
**Aluno:** Eduardo Lopes Jonker  
**Instituição:** Universidade do Estado de Santa Catarina (UDESC) — CCT/PPGCAP  
**Finalidade:** material de estudo e apoio para apresentação e arguição no Seminário de Inovação em Computação  
**Escopo:** versão de 19 slides organizada pelos capítulos da dissertação

---

## Resumo executivo

Este relatório explica em profundidade os conceitos e métodos apresentados no seminário. O problema que conecta a pesquisa é prático: **como usar dados da frota para decidir prioridades de manutenção quando orçamento, tempo e capacidade de oficina são limitados?**

A resposta proposta não é “deixar a inteligência artificial decidir”. O trabalho organiza registros administrativos de manutenção, patrimônio e abastecimento; descreve relações entre veículos e oficinas; estima riscos e custos; compara explicações de modelos; e formula uma otimização matemática para comparar alternativas sob restrições explicitadas. Os resultados servem para apoiar análise e triagem, mantendo a avaliação e a decisão administrativa com pessoas responsáveis.

Os principais métodos cobertos são:

1. análise descritiva e preparação de dados administrativos;
2. avaliação temporal de modelos para evitar olhar o futuro no treinamento;
3. classificação e regressão com HistGradientBoosting;
4. calibração isotônica, Brier Score e Expected Calibration Error;
5. análise de sobrevivência com distribuição de Weibull;
6. representação de relações por grafos bipartidos, métricas de rede e comunidades de Louvain;
7. explicabilidade local por SHAP e LIME, comparada com Jaccard e Spearman;
8. otimização por programação linear inteira mista (MILP), resolvida com HiGHS;
9. simulação e comparação contrafactual de custos;
10. triagem patrimonial por critério econômico;
11. detecção não supervisionada de atipicidades com Isolation Forest;
12. hash SHA-256 como verificação de integridade de arquivos.

As cifras econômicas da apresentação devem ser descritas como **diferenças entre custos modelados no cenário S0**, sob premissas definidas. A estimativa de 13,66%, aproximadamente R$ 6,99 milhões, não é economia observada nem comprovação de impacto já obtido pelo Estado. De modo semelhante, agrupamentos em grafos e observações atípicas são sinais para exame, não provas de fraude, conluio ou causalidade.

**Sumário**

[TOC]

---

## 1. Como ler este relatório

### 1.1 Convenções epistemológicas

Para evitar que uma descrição técnica seja entendida como uma afirmação mais forte do que os dados permitem, este documento distingue:

- **Registro observado:** dado existente na base administrativa, com a qualidade e cobertura próprias da fonte.
- **Estatística descritiva:** resumo calculado a partir dos registros. Descreve a amostra, mas não explica automaticamente por que o padrão surgiu.
- **Estimativa preditiva:** saída de um modelo treinado para antecipar um resultado; depende do alvo, das variáveis e do protocolo de validação.
- **Sinal de triagem:** observação, grupo ou caso que pode merecer verificação adicional.
- **Resultado de otimização:** solução de uma formulação matemática, condicional à função objetivo, aos dados e às restrições codificadas.
- **Resultado de simulação:** consequência calculada para um cenário especificado; não significa que o cenário ocorreu na operação.
- **Impacto observado:** mudança verificada em uma implantação real, comparada a uma referência adequada. O estudo apresentado ainda requer avaliação prospectiva para demonstrar esse impacto.

Essas categorias não são intercambiáveis. Em especial, **custo modelado menor não é sinônimo de dinheiro economizado**, e uma previsão não é uma explicação causal.

### 1.2 Vocabulário mínimo

- **Frota:** conjunto de veículos sob gestão de uma organização.
- **OS (ordem de serviço):** registro administrativo que agrupa uma solicitação ou execução de manutenção. Uma OS pode conter mais de um item.
- **Item de manutenção:** registro de serviço, peça ou atividade associada a uma ordem, conforme a estrutura da base.
- **Nó e aresta:** elementos de um grafo; nós representam entidades e arestas representam relações observadas.
- **Modelo supervisionado:** algoritmo ajustado com exemplos que incluem o resultado-alvo conhecido.
- **Classificação:** previsão de uma classe ou probabilidade de ocorrência de evento.
- **Regressão:** previsão de valor numérico, por exemplo, um custo.
- **Calibração:** avaliação/ajuste da correspondência entre probabilidades previstas e frequências observadas.
- **TCO (Total Cost of Ownership):** custo total de propriedade ou operação definido para o horizonte e os componentes incluídos na formulação.
- **MILP:** problema de otimização linear com variáveis contínuas e inteiras/binárias.
- **Solver:** software que procura uma solução para um problema matemático de otimização e, conforme opções e tolerâncias, fornece limites e certificados numéricos.

---

## 2. A pergunta da pesquisa e sua lógica

O gestor de frota precisa decidir quais situações merecem atenção primeiro, levando em conta a disponibilidade necessária, os recursos financeiros, o tempo de oficina e obrigações administrativas. Os dados usados para tomar essa decisão podem estar distribuídos por sistemas ou tabelas diferentes: manutenção, patrimônio e abastecimento.

O raciocínio do estudo pode ser apresentado como uma cadeia de apoio:

**registros administrativos → preparação e descrição → estimativas e análise de relações → comparação de explicações → otimização sob restrições → revisão humana.**

Essa sequência representa um framework metodológico, não necessariamente um pipeline em que cada método passa diretamente sua saída ao próximo. A rede veículo–oficina, por exemplo, descreve relações e pode orientar triagem; não se deve afirmar que os agrupamentos de Louvain são automaticamente entradas do MILP, a menos que essa ligação esteja demonstrada no código e na validação.

### 2.1 Por que não basta prever?

Uma previsão pode estimar a chance de uma falha ou o custo esperado, mas não responde sozinha:

- qual veículo deve receber atendimento primeiro;
- quantos serviços cabem no orçamento;
- se há capacidade de oficina para executar as intervenções;
- quais manutenções são mandatórias;
- como equilibrar risco, custo e disponibilidade.

Essas perguntas dependem de objetivos e restrições. A analítica prescritiva procura comparar ações possíveis, dado um modelo de consequências e um conjunto explícito de condições.

### 2.2 Por que não basta otimizar?

Um otimizador escolhe alternativas segundo aquilo que foi codificado. Se custos, riscos, capacidade ou restrições estiverem errados ou incompletos, uma solução matematicamente correta pode ser operacionalmente inadequada. Por isso:

1. dados e parâmetros devem ser auditados;
2. previsões precisam ser avaliadas;
3. a função objetivo deve representar o problema com transparência;
4. restrições precisam corresponder ao cenário real;
5. recomendações devem ser revistas por pessoas responsáveis.

---

## 3. Base empírica e preparação dos dados

### 3.1 Volumes citados na apresentação

Os slides apresentam, para o recorte administrativo considerado:

- **77.867 ordens de serviço**;
- **350.737 itens ou registros de manutenção**;
- **34.280 veículos cadastrados no patrimônio**;
- cerca de **1.000.000 de transações de abastecimento**, conforme cobertura e período analisados;
- **R$ 138,76 milhões aprovados** e **R$ 60,05 milhões em glosas técnicas**, segundo as categorias financeiras reportadas.

Esses totais não são unidades equivalentes. Uma ordem pode agrupar múltiplos itens; um cadastro patrimonial não garante que o veículo esteve ativo durante todo o período; e o número de abastecimentos depende da janela temporal e das fontes incluídas. Ao apresentar essas quantidades, diga o que está sendo contado.

### 3.2 Por que a preparação é metodologicamente importante?

Modelos aprendem relações que estão nos dados, inclusive erros, duplicações ou vieses de cobertura. A preparação pode envolver:

- verificar formatos, unidades e chaves de ligação;
- identificar valores faltantes e suas causas;
- conferir continuidade e plausibilidade de hodômetros;
- distinguir valores orçados, autorizados, glosados e efetivamente pagos;
- garantir que as datas correspondam ao momento em que a informação estaria disponível;
- registrar transformações para permitir reprodução.

Não se deve substituir uma incerteza documental por uma suposição silenciosa. Por exemplo, imputar um valor faltante pode facilitar o cálculo, mas o relatório do estudo deve registrar a regra, a proporção de registros afetados e os efeitos potenciais.

### 3.3 Agregação e granularidade

A análise pode ser feita por OS, item, veículo, oficina, veículo-mês ou outra unidade. Cada escolha responde a uma pergunta diferente. Uma tabela com itens não pode ser comparada diretamente a uma contagem de OS sem explicitar que uma OS pode conter vários itens. A agregação também pode mudar a rede: várias relações veículo–oficina podem ser representadas por uma aresta ponderada.

### 3.4 Limite de generalização

Resultados calculados com registros do Poder Executivo de Santa Catarina não se transferem automaticamente para outro estado, órgão, classe de veículo ou período. Diferenças em contratos, geografia, credenciamento, perfil de uso, disponibilidade de dados e rotina de manutenção podem alterar distribuições e relações.

---

## 4. Níveis de análise: do resumo à recomendação

### 4.1 Análise descritiva

Responde: **“O que aparece nos registros?”** Pode resumir despesas, tipos de serviço, quantidades por órgão ou tendências temporais. Gráficos de concentração, como curvas de Lorenz, mostram como os valores se distribuem na amostra.

Uma curva de concentração não estabelece uma lei universal. Uma observação de que uma fração dos veículos concentra determinada fração dos gastos vale para a população, período e definição utilizados; não deve ser tratada como regra invariável 80/20.

### 4.2 Análise diagnóstica e estrutural

Examina relações e padrões associados, como concentração de vínculos entre oficinas e veículos. “Diagnóstico”, neste contexto, não equivale automaticamente a diagnóstico causal. Para afirmar que um fator causou outro, seriam necessários desenho causal, identificação de confundidores, hipótese de intervenção e estratégia de validação apropriada.

### 4.3 Análise preditiva

Responde: **“O que pode ocorrer em dados ainda não observados?”** A resposta é uma estimativa condicionada a exemplos históricos, variáveis, alvo e período. Não é uma garantia.

### 4.4 Análise prescritiva

Responde: **“Qual alternativa atende melhor ao objetivo, dadas as restrições?”** A recomendação só é válida para a função objetivo e as premissas especificadas. O MILP pode produzir uma solução ótima para a instância matemática, não uma decisão automaticamente correta sob todas as considerações humanas, legais ou operacionais.

---

## 5. Avaliação temporal: como evitar olhar o futuro

### 5.1 O problema do embaralhamento aleatório

Em dados temporais, registros próximos podem compartilhar contexto e informação. Se linhas de uma mesma janela forem distribuídas aleatoriamente entre treino e teste, o treinamento pode receber informação de períodos posteriores ao teste. Essa contaminação é chamada **vazamento temporal** e pode produzir métricas excessivamente otimistas.

### 5.2 Divisão cronológica

Uma avaliação temporal imita a ordem de uso:

1. ajusta-se o modelo com observações do passado;
2. avalia-se em uma janela posterior;
3. avança-se a janela e repete-se;
4. agregam-se resultados de várias janelas, sem perder a cronologia.

A dissertação e os materiais de apoio descrevem partições cronológicas; o guia também registra cinco dobras temporais e um embargo de 30 dias. Um embargo cria um intervalo de separação para reduzir dependências ou vazamentos próximos à fronteira entre treino e teste.

### 5.3 Por que é apropriado?

O uso pretendido é apoiar decisões futuras. Por isso, a questão relevante não é apenas “o modelo ajusta os dados históricos?”, mas “como se comporta ao prever um período que ainda não participou do ajuste?”. Essa escolha aproxima a avaliação retrospectiva do cenário de implantação.

### 5.4 Limitações

Mesmo uma avaliação temporal retrospectiva:

- não equivale a experimento prospectivo;
- não garante que políticas, preços ou padrões futuros permaneçam estáveis;
- não controla automaticamente mudanças de sistema ou de cobertura;
- não demonstra que o uso da previsão melhora decisões ou resultados.

### 5.5 Vazamento de dados

Vazamento ocorre quando o modelo recebe, direta ou indiretamente, informação que não estaria disponível no instante da decisão. Um exemplo genérico seria usar o custo final de uma OS para estimar um risco antes de a OS ser aberta. A prevenção exige construir variáveis apenas com dados disponíveis no tempo de previsão e verificar a linhagem de cada coluna.

**Justificativa acadêmica:** a avaliação deve corresponder ao processo de geração dos dados e à pergunta de pesquisa. Para previsão temporal, a dependência da ordem torna a validação aleatória inadequada como único critério. Bergmeir e Benítez (2012) discutem procedimentos de validação cruzada para séries temporais; a decisão de usar partições cronológicas é coerente com esse princípio.

---

## 6. Aprendizado supervisionado: HistGradientBoosting

### 6.1 O que é aprendizado supervisionado?

O algoritmo recebe exemplos históricos representados por atributos e um resultado-alvo conhecido. Durante o treinamento, ajusta uma função que relaciona atributos de entrada a esse resultado.

- Em **classificação**, o resultado é uma classe, como presença/ausência de evento. Um modelo probabilístico também pode produzir uma probabilidade estimada.
- Em **regressão**, o resultado é numérico, como o custo de manutenção.

No trabalho, a apresentação distingue classificação de risco e regressão de custos. Métricas de uma tarefa não devem ser apresentadas como se avaliassem a outra.

### 6.2 Como funciona o gradient boosting com árvores?

Gradient boosting constrói um conjunto de modelos fracos, normalmente árvores pequenas, de forma sequencial. Em cada etapa, o novo componente é ajustado para reduzir uma função de perda associada aos erros residuais do conjunto já construído. Em termos intuitivos:

1. começa-se com uma estimativa simples;
2. identifica-se onde ela erra segundo a função de perda;
3. ajusta-se uma nova árvore para representar parte do erro;
4. soma-se essa correção ao modelo;
5. repete-se o processo, controlando a complexidade.

O **HistGradientBoosting** é uma implementação de boosting por histogramas: valores de atributos numéricos são agrupados em intervalos, o que permite procurar divisões das árvores com menor custo computacional em conjuntos maiores. O algoritmo pode representar relações não lineares e interações sem exigir que cada relação seja linear.

### 6.3 Por que usar?

É uma opção apropriada para dados tabulares com relações potencialmente não lineares e interações entre variáveis. A escolha deve ser justificada por comparação com baselines e por desempenho em dados separados temporalmente, não apenas por popularidade do algoritmo.

### 6.4 O que ele não garante?

- Não garante causalidade.
- Não garante boa calibração de probabilidades.
- Não garante desempenho fora da distribuição de treinamento.
- Não elimina viés de registro ou de seleção.
- Uma importância alta de atributo não significa que intervir nesse atributo mudará o resultado.

### 6.5 Regressão: MAE, RMSE e R² ajustado

O slide reporta, para o protocolo indicado no capítulo de regressão, MAE de **R$ 2.236,06**, RMSE de **R$ 3.780,20** e R² ajustado de **0,1139**. A leitura correta é condicionada ao alvo, à amostra e à partição usada.

- **MAE — Mean Absolute Error:** média do módulo entre valor previsto e observado. Tem a mesma unidade do alvo. MAE de R$ 2.236 não significa que cada previsão errou exatamente R$ 2.236.
- **RMSE — Root Mean Squared Error:** raiz da média dos erros ao quadrado. Erros grandes pesam mais do que no MAE.
- **R²:** compara o erro do modelo ao erro de uma referência baseada na média. O valor não é “porcentagem de acerto”. Um R² baixo indica que, na avaliação, a variação capturada pelo modelo foi limitada em relação à variabilidade total.
- **R² ajustado:** penaliza o R² pelo número de preditores e pelo tamanho amostral segundo uma fórmula específica. Não resolve sozinho seleção de modelo nem validação externa.

Como o MAE e o RMSE respondem a perdas diferentes, devem ser lidos em conjunto. Uma distribuição de custos assimétrica, com poucos reparos muito caros, pode elevar o RMSE mais do que o MAE.

### 6.6 Classificação e probabilidades

O slide reporta Brier = **0,1043** e ECE = **0,0174** para a calibração do classificador no protocolo indicado. Esses números não são métricas de regressão de custos e não devem ser comparados diretamente aos valores em reais.

---

## 7. Calibração isotônica e confiabilidade probabilística

### 7.1 Discriminação e calibração são diferentes

Um classificador pode ordenar corretamente casos de maior e menor risco, mas atribuir probabilidades excessivas. **Discriminação** mede, em essência, a capacidade de separar ou ordenar classes; **calibração** pergunta se previsões como 0,7 correspondem a eventos em cerca de 70% dos casos comparáveis.

### 7.2 Calibração isotônica

A calibração isotônica ajusta uma função não decrescente entre o escore original e a frequência empírica dos eventos. A restrição de monotonicidade preserva a ordem dos escores, mas não impõe forma linear. É útil quando há dados de calibração suficientes e não se quer assumir uma transformação sigmoide específica.

O ajuste do calibrador deve ser feito com dados separados dos usados para a avaliação final ou dentro de validação cruzada aninhada. Caso contrário, o resultado pode parecer mais confiável do que será em dados novos.

### 7.3 Brier Score

Para probabilidades pᵢ e resultados binários yᵢ ∈ {0,1}, o Brier Score é a média de (pᵢ − yᵢ)². Ele combina aspectos de calibração e discriminação. Menor valor indica menor erro quadrático probabilístico na amostra, mas a interpretação depende da prevalência e do protocolo.

### 7.4 Expected Calibration Error (ECE)

O ECE divide previsões em grupos de confiança e agrega a diferença absoluta entre a confiança média e a frequência observada em cada grupo, ponderada pelo tamanho do grupo. A escolha do número e da forma dos intervalos afeta o resultado; por isso, ECE não é uma medida independente de decisões de implementação.

### 7.5 Por que calibração importa para otimização?

Se a função objetivo usa risco esperado de uma falha para valorar o custo de não intervir, probabilidades mal calibradas podem distorcer esse custo. Calibrar melhora a coerência probabilística dentro do conjunto avaliado. Não prova que o modelo esteja bem calibrado em outra frota, período ou órgão.

**Formulação segura:** “No protocolo avaliado, a calibração isotônica produziu Brier 0,1043 e ECE 0,0174. Isso descreve confiabilidade probabilística retrospectiva; não é garantia de acerto individual nem de desempenho futuro.”

---

## 8. Confiabilidade e distribuição de Weibull

### 8.1 O que é análise de sobrevivência?

Análise de sobrevivência estuda o tempo até um evento, por exemplo, a ocorrência de uma falha ou a necessidade de manutenção. Um desafio comum é que nem todos os veículos apresentam o evento durante o período observado. Quando o evento ainda não foi registrado até o fim da observação, o tempo é **censurado à direita**: sabe-se que o tempo até o evento excede o período observado, mas não se conhece sua duração completa.

### 8.2 Distribuição de Weibull

A distribuição de Weibull é uma família flexível para modelar tempos até falha. Uma parametrização comum usa escala η > 0 e forma k > 0:

- confiabilidade: R(t) = exp[−(t/η)ᵏ];
- risco instantâneo: h(t) = (k/η)(t/η)ᵏ⁻¹.

O parâmetro de forma orienta a forma do risco:

- k < 1: risco decrescente ao longo do tempo, sob esse modelo;
- k = 1: risco constante, caso exponencial;
- k > 1: risco crescente, sob esse modelo.

O material de apoio registra valor de forma próximo de 1,42; um slide traz outra notação/valor no texto principal e alerta para confirmar a divergência com a figura. **Antes de afirmar o valor final, deve-se conferir a versão autoritativa da dissertação e a legenda do gráfico.** O significado geral de k > 1 deve ser apresentado como interpretação do ajuste, não lei mecânica universal.

### 8.3 Por que usar?

Manutenção envolve tempo até evento, e a censura é comum quando registros terminam antes de ocorrer falha. Modelar sobrevivência permite utilizar observações incompletas sem tratá-las como se o evento tivesse ocorrido ou como se o tempo fosse conhecido integralmente.

### 8.4 Limites

A distribuição escolhida é uma hipótese estatística. O ajuste depende da definição de falha, qualidade das datas, dependência entre veículos, heterogeneidade de uso e censura. Uma curva de Weibull ajustada não demonstra a causa do desgaste nem substitui inspeção mecânica.

---

## 9. Teoria dos grafos e estrutura das relações

### 9.1 Conceito de grafo

Um grafo G = (V,E) possui:

- V: conjunto de vértices ou nós;
- E: conjunto de arestas ou ligações entre pares de nós.

Nos dados relacionais, os nós podem representar entidades — veículos, oficinas, órgãos, contratos — e as arestas relações registradas entre elas. Um grafo pode ser dirigido ou não dirigido, ponderado ou não ponderado, simples ou multigrafo, conforme o problema e a forma como se agregam eventos.

### 9.2 Rede bipartida veículo–oficina

Um grafo bipartido separa os vértices em dois conjuntos disjuntos, V e W, e permite arestas entre um conjunto e o outro. Neste estudo:

- V representa veículos;
- W representa oficinas credenciadas;
- uma aresta veículo–oficina representa um serviço/transação observada;
- um peso pode representar volume de serviços ou valor, desde que a definição seja explícita.

A característica central é que uma aresta liga tipos diferentes de entidade. Isso modela naturalmente a relação “este veículo teve serviço registrado nesta oficina”.

### 9.3 Tabela versus grafo

O grafo não substitui a tabela de origem nem os documentos. A tabela é adequada para filtros, agregações e auditoria linha a linha; o grafo torna visível a topologia das relações e pode revelar concentração, intermediação e agrupamentos. A forma mais adequada depende da pergunta.

### 9.4 Métricas de rede

#### Grau

O grau de um nó é o número de conexões incidentes. Em uma rede bipartida veículo–oficina, o grau de uma oficina pode contar quantos veículos se conectam a ela dentro da rede e período definidos. Grau alto indica muitas conexões; não significa automaticamente risco ou irregularidade.

#### Centralidade de intermediação (betweenness)

Uma forma clássica de betweenness de um nó v é:

CB(v) = Σ₍s≠v≠t₎ σₛₜ(v) / σₛₜ,

em que σₛₜ é o número de caminhos mínimos entre s e t e σₛₜ(v) é o número desses caminhos que passam por v. A métrica descreve posição estrutural como intermediário. O valor depende do tipo de grafo e de como se definem os caminhos; não é uma medida direta de poder, ilegalidade ou causalidade.

Em uma rede bipartida, interpretar caminhos exige cuidado: alguns nós podem ficar em posições centrais por geografia, credenciamento, especialização ou disponibilidade regional.

### 9.5 Comunidades e algoritmo de Louvain

Uma comunidade é um grupo com mais conexões internas do que seria esperado sob uma referência probabilística ou modelo nulo. O algoritmo de Louvain (Blondel et al., 2008) procura uma partição que maximize a **modularidade** em etapas heurísticas:

1. inicia cada nó em sua própria comunidade;
2. move nós para comunidades vizinhas quando a mudança aumenta modularidade;
3. comprime comunidades em supernós;
4. repete até que não haja melhoria segundo a regra do algoritmo.

O processo é eficiente em redes grandes, mas é heurístico: pode produzir soluções diferentes conforme ordem, implementação, semente, ponderação e estrutura da rede. A modularidade tem limitações, inclusive resolução de comunidades de diferentes escalas.

### 9.6 Modularidade Q

Q compara a fração de ligações observadas dentro das comunidades com a fração esperada sob um modelo nulo, frequentemente baseado em graus. Em termos intuitivos, mede quão mais concentradas estão as ligações dentro dos grupos do que se esperaria ao acaso sob essa referência.

O estudo reporta **18 comunidades e Q = 0,5646** na rede e configuração avaliadas. Isso não significa “56,46% de certeza”, não quantifica fraude e não prova que exista uma divisão natural única. A interpretação depende da rede, peso, período, população e algoritmo.

### 9.7 Segunda representação: coocorrência de falhas

Além da rede bipartida veículo–oficina, a dissertação menciona um grafo de coocorrência de falhas/sistemas:

- os nós representam categorias de falha ou sistemas;
- uma aresta representa ocorrência conjunta segundo regra de construção adotada;
- grupos podem indicar componentes que aparecem juntos nos registros.

A apresentação/relatório da dissertação reporta quatro comunidades e Q = 0,384 nessa representação. Esse resultado é distinto das 18 comunidades da rede veículo–oficina. Coocorrência não prova que uma falha causa outra: pode refletir dependência mecânica, padrões de registro, manutenção simultânea ou outros fatores.

### 9.8 Como os grafos entram no projeto

1. Os registros administrativos identificam entidades e serviços.
2. Veículos e oficinas tornam-se dois tipos de nós.
3. Relações observadas de serviço geram arestas.
4. Atributos podem registrar data, tipo, volume ou valor.
5. Métricas e comunidades descrevem a estrutura e ajudam a selecionar perguntas para triagem.
6. A verificação substantiva requer voltar aos registros/documentos e ao contexto da operação.

### 9.9 Justificativa acadêmica

Grafos são adequados quando a relação entre entidades é parte da pergunta. Uma tabela plana pode armazenar vínculos, mas é menos direta para examinar padrões topológicos em redes complexas. A escolha não decorre de uma norma do TCU para manutenção de frota. Estudos de Garcia (2019) no ISC/TCU exploraram Neo4j como ferramenta potencial de Data Analytics para auditoria governamental; Soares (2020) estudou padrões topológicos em dados relacionados a compras públicas. São precedentes metodológicos de análise relacional, não validação desta aplicação às frotas.

### 9.10 Neo4j: banco de grafos implementado no protótipo

Neo4j é um sistema de gerenciamento de banco de dados orientado a grafos. Em vez de representar relações apenas por chaves estrangeiras e junções relacionais, armazena nós, relacionamentos e propriedades de forma explícita, permitindo percorrer conexões. A linguagem Cypher expressa padrões de nós e relações (Robinson, Webber e Eifrem, 2015).

O projeto agora conta com um protótipo local em Neo4j Community 5.26, executado em Docker e acessível somente por `127.0.0.1`. Ele carrega dados de manutenção processados e cria dois tipos de nós — `FleetVehicle` e `FleetWorkshop` — conectados por `SERVICED_AT`. Cada aresta agrega registros do par veículo–oficina, valor aprovado e datas disponíveis. Uma segunda relação, `SHARES_VEHICLE`, conecta oficinas que compartilharam pelo menos dois veículos, conforme a regra de projeção usada na análise.

Na execução verificada, a fonte processada continha 77.867 registros; 60.114 registros cobrados e identificados foram considerados, com soma de valores aprovados de R$ 131.506.578,94. O valor é um agregado da fonte, não economia ou impacto. O banco apresentou 7.291 nós de veículos, 1.039 nós de oficinas e 25.122 arestas bipartidas. A projeção resultou em 803 oficinas participantes e 6.937 arestas entre oficinas. O carregador comparou esses totais com consultas executadas diretamente no banco. O relatório agregado da carga está em `dissertacao_frotas/resultados/logs/relatorio_neo4j_grafo.json`; a configuração, o modelo, as consultas Cypher e os passos para reproduzir estão em `graphdb/`.

Para reduzir exposição de dados, os códigos de origem de veículos e estabelecimentos são transformados por HMAC-SHA-256 com segredo local, e não são gravados no grafo. O protótipo não carrega placa, nome, CPF/CNPJ, texto livre nem dados de abastecimento. Essa proteção reduz a exposição direta, mas não equivale a anonimização irreversível; o segredo deve permanecer protegido e o uso dos dados continua sujeito às regras institucionais.

O Louvain reportado na dissertação — 18 comunidades e Q = 0,5646 — continua associado ao pipeline original de análise de redes. **A carga no Neo4j não executou Louvain**, e os números da implementação não devem ser apresentados como nova validação do algoritmo nem como prova de irregularidade. O protótipo materializa e permite consultar a rede; uma futura execução por Neo4j Graph Data Science exigiria validação separada de projeção, pesos, versão e parâmetros.

O trabalho citado de Garcia (2019) explorou Neo4j como ferramenta potencial de Data Analytics em auditoria governamental. Essa referência oferece um precedente acadêmico, não prova implantação permanente nem chancela do TCU para o método de manutenção de frotas deste projeto.

**Como dizer à banca:** “Além da análise de grafos, implementamos um protótipo local em Neo4j para armazenar e consultar relações entre veículos e oficinas. Os identificadores foram pseudonimizados e o banco não contém placas nem nomes. As comunidades de Louvain apresentadas continuam vindo do pipeline original; não afirmamos que foram recalculadas pelo Neo4j nem que indiquem irregularidade.”

---

## 10. Explicabilidade: SHAP e LIME

### 10.1 Por que explicar previsões?

Em uma decisão pública, pode ser necessário compreender quais atributos contribuíram para uma previsão, comparar explicações e investigar divergências. Explicabilidade pode apoiar entendimento e auditoria, mas uma explicação pós-hoc não transforma o modelo em causal nem garante que a razão matemática corresponda a um mecanismo real.

### 10.2 SHAP: valores de Shapley

SHAP (SHapley Additive exPlanations) adapta valores de Shapley, da teoria dos jogos cooperativos, à atribuição de contribuição de atributos para uma previsão. Uma previsão é comparada a um valor de referência (baseline); a diferença é distribuída entre os atributos segundo médias de contribuições marginais ao considerar coalizões de atributos.

Na formulação de Shapley para o atributo i:

φᵢ = Σ₍S⊆F\\{i}₎ [|S|!(M−|S|−1)! / M!] · [f(S∪{i}) − f(S)],

onde F é o conjunto de atributos, S uma coalizão sem i e f(S) a previsão associada à coalizão segundo uma regra de integração/ausência. SHAP fornece propriedades formais desejáveis para uma classe de explicações aditivas, mas o significado depende do baseline, da dependência entre atributos, da aproximação computacional e do modelo.

**Interpretação:** um valor positivo pode indicar que a contribuição atribuída ao atributo elevou a previsão em relação ao baseline na instância e convenção analisadas. Não significa que alterar o atributo causará a mudança.

### 10.3 LIME: explicação local por aproximação

LIME (Local Interpretable Model-agnostic Explanations) aproxima o comportamento de um modelo complexo perto de uma instância:

1. seleciona-se uma observação a explicar;
2. criam-se perturbações sintéticas ao redor dela;
3. consulta-se o modelo original nessas perturbações;
4. ponderam-se amostras conforme proximidade à instância;
5. ajusta-se um modelo simples e interpretável na vizinhança;
6. os coeficientes do modelo local servem como explicação aproximada.

LIME é agnóstico ao modelo, mas depende de como perturba dados, define proximidade, amostra vizinhanças e escolhe a complexidade do substituto. Em atributos correlacionados ou dados tabulares com combinações impossíveis, perturbações podem gerar instâncias pouco plausíveis.

### 10.4 Comparar SHAP e LIME

Os métodos têm definições e premissas distintas. A pesquisa compara os atributos mais importantes em cada explicação:

- **Jaccard Top-5 = 45,48%:** compara sobreposição entre conjuntos das cinco principais variáveis.
- **Spearman ρ = 0,2869:** mede associação entre rankings, levando em conta posições.

Um Jaccard baixo mostra pouca sobreposição dos conjuntos Top-5 na comparação realizada. Spearman de 0,2869 indica concordância positiva limitada/modesta entre ordenações, conforme amostra e procedimento reportados. Esses valores não demonstram superioridade universal de um método, não significam que 45,48% das explicações são verdadeiras e não constituem prova de causalidade.

### 10.5 Por que a comparação é importante?

Se métodos distintos atribuem importância a conjuntos diferentes, o analista não deve tratar uma única explicação como verdade indiscutível. A divergência:

- expõe sensibilidade a definições;
- motiva revisar dados e a instância;
- orienta testes de estabilidade e plausibilidade;
- recomenda documentar o método e o baseline;
- reforça que a decisão deve continuar sujeita a revisão.

### 10.6 Limites de SHAP e LIME

- Importância local não equivale a efeito causal.
- Explicação local não explica necessariamente o comportamento global.
- Atributos correlacionados dificultam atribuição única.
- Baselines e distribuição de referência afetam valores.
- LIME pode variar com perturbações e amostragem.
- SHAP aproximado pode depender do algoritmo e orçamento computacional.
- Uma explicação plausível pode acompanhar uma previsão incorreta.

**Justificativa acadêmica:** SHAP e LIME são métodos consolidados para interpretar previsões, com pressupostos diferentes. Compará-los no mesmo caso empírico investiga concordância das explicações, não cria novo algoritmo. Rudin (2019) alerta para limitações de explicações pós-hoc em decisões de alto impacto e recomenda considerar modelos interpretáveis quando viáveis.

---

## 11. Otimização por MILP

### 11.1 O que é otimização matemática?

Otimização formaliza uma escolha como:

**minimizar ou maximizar uma função objetivo, respeitando restrições.**

No caso da manutenção, as alternativas podem incluir intervir ou não intervir em um veículo durante certo período, respeitando orçamento, capacidade agregada e obrigações mandatórias codificadas.

### 11.2 Variáveis, parâmetros e restrições

- **Variável de decisão:** representa uma escolha controlável, por exemplo, selecionar uma intervenção (binária: 1 = selecionada; 0 = não selecionada).
- **Parâmetro:** valor considerado conhecido na instância, como custo preventivo, risco estimado ou limite de capacidade.
- **Função objetivo:** expressa o critério matemático que se quer otimizar.
- **Restrição:** define alternativas admissíveis.

Uma formulação simplificada — apenas para explicar o conceito, não reprodução literal completa da implementação — pode usar xᵢₜ ∈ {0,1}, indicando se uma intervenção no veículo i é selecionada no período t. Uma parte da função objetivo pode ser escrita como:

min Σᵢₜ [cᵢₜ xᵢₜ + rᵢₜ(1−xᵢₜ)],

onde cᵢₜ é custo modelado da intervenção e rᵢₜ é custo ou risco residual modelado quando não se intervém. Outras parcelas entram somente se estiverem definidas no modelo real.

Exemplos de restrições:

- orçamento: Σᵢ cᵢₜxᵢₜ ≤ Bₜ;
- capacidade agregada: Σᵢ hᵢₜxᵢₜ ≤ Hₜ;
- obrigação: xᵢₜ = 1 para intervenção mandatória representada;
- vínculo lógico: limites que conectam decisões entre veículos, períodos ou condições.

### 11.3 Por que “inteira” e “mista”?

“Inteira” significa que algumas variáveis só podem assumir valores inteiros; em decisões de seleção, são frequentemente binárias. “Mista” significa que outras variáveis podem ser contínuas, por exemplo, quantidade ou custo auxiliar. “Linear” significa que função objetivo e restrições são expressas por combinações lineares das variáveis na formulação.

### 11.4 Por que usar MILP?

O problema contém decisões discretas (“fazer ou não fazer”) e recursos concorrentes. MILP permite representar essas decisões e encontrar uma combinação viável que otimize o objetivo especificado. É particularmente útil quando uma regra gulosa local pode ignorar o efeito da alocação conjunta.

### 11.5 O que significa “ótimo”?

Um ótimo é relativo a:

- os dados da instância;
- a função objetivo;
- as restrições;
- os parâmetros;
- a tolerância e condições do solver.

Não significa que o plano seja universalmente ótimo, juridicamente autorizado ou operacionalmente superior a qualquer alternativa real. A adequação externa exige validar as premissas e comparar com políticas de referência.

### 11.6 Restrições apresentadas

Os slides mencionam:

- teto de orçamento por período;
- capacidade agregada de oficina, em horas disponíveis;
- manutenção mandatória, que não deve ser omitida se estiver codificada como obrigação.

O relatório do projeto também menciona cenário de prontidão policial de 95,26%, mas o próprio slide alerta que esse valor é disponibilidade resultante e não piso formal, salvo comprovação de que uma restrição correspondente foi efetivamente codificada na instância. Não apresente resultado como requisito matemático sem evidência do modelo executado.

### 11.7 HiGHS como solver

HiGHS é um solver de otimização matemática de código aberto para programação linear, programação linear inteira-mista e problemas relacionados. Para MILP, solvers costumam combinar:

- relaxação linear, que permite temporariamente valores fracionários nas variáveis inteiras;
- branch-and-bound, que divide o problema em subproblemas impondo decisões inteiras;
- cortes, que adicionam desigualdades válidas para eliminar soluções fracionárias sem eliminar soluções inteiras admissíveis;
- heurísticas que tentam encontrar incumbentes inteiros;
- limites primal e dual que delimitam qualidade/otimalidade.

O relatório da pesquisa cita HiGHS e branch-and-cut. A implementação específica e versão do solver devem ser conferidas no registro técnico se a banca solicitar opções, tolerâncias e certificados.

### 11.8 Gap de integralidade e tolerância

O slide reporta cenário S0 com custo R$ 44.190.120,51 e MIP gap do solver de 0,0000%, além de gap LP–MIP de 0,00063%. Esses valores não são idênticos:

- **MIP gap do solver** é a diferença relativa entre solução inteira incumbente e melhor limite conhecido segundo o solver e tolerâncias configuradas.
- **Gap LP–MIP** compara valor da relaxação linear/limite dual e solução inteira reportados no material do estudo.

Em qualquer caso, um gap pequeno sugere que o solver fechou a instância matemática até a tolerância reportada. Não valida a qualidade dos dados ou a validade substantiva da função objetivo.

### 11.9 Verificações acadêmicas recomendáveis

Para reproduzir ou defender o MILP, documentar:

1. conjunto de veículos e períodos;
2. variáveis e domínios;
3. função objetivo completa e unidades;
4. fonte e transformação de cada parâmetro;
5. orçamento e unidade de capacidade;
6. quais intervenções são obrigatórias e como foram codificadas;
7. versão do HiGHS, parâmetros e tolerâncias;
8. status da solução e limites;
9. comparação com baselines;
10. análise de sensibilidade.

---

## 12. Custos modelados e cenário S0

### 12.1 Diferença observada no modelo

O slide apresenta:

- BL0: **R$ 53,14 milhões**;
- MILP-1: **R$ 43,84 milhões**;
- diferença modelada: **R$ 6,99 milhões**;
- redução potencial calculada: **13,66%**.

O cálculo percentual é aproximadamente:

(53,14 − 43,84) / 53,14 × 100% ≈ 13,66%.

O cenário considera **2.000 veículos** e **36 meses**, conforme o slide. O material de dissertação também lista valores mais precisos, mas a apresentação arredonda para fins de comunicação.

### 12.2 Por que dizer “potencial estimado”?

Os valores de BL0 e MILP-1 são custos modelados sob premissas. A diferença entre eles representa potencial estimado para aquele cenário, não uma observação de gasto evitado em operação. O contrafactual responde “o que o modelo calcula sob essas regras?”, não “quanto o Estado efetivamente poupou?”.

### 12.3 Comparação MILP-0 e MILP-1

O slide também reporta custos modelados de R$ 48,72 milhões e R$ 43,84 milhões, com diferença estimada de R$ 4,88 milhões. Essa diferença **não isola efeito causal do aprendizado de máquina**. Para atribuir causalmente a diferença a um componente, seria necessário desenho ablativo controlado, mantendo os demais fatores constantes e definindo claramente o que muda entre instâncias.

### 12.4 Monte Carlo e projeção

O slide diz que projeção 2027–2029 e análise Monte Carlo dependem de premissas distintas e são estimativas de cenário. Monte Carlo consiste em repetir cálculos sob valores amostrados de variáveis incertas segundo distribuições especificadas. O resultado depende de:

- distribuições escolhidas;
- parâmetros e correlações;
- número de simulações;
- hipóteses sobre inflação, falhas e disponibilidade;
- horizonte e regra de atualização.

Uma distribuição de resultados simulados não se torna previsão garantida. Se um intervalo de confiança ou faixa simulada for apresentado, deve ficar claro se é intervalo de incerteza do modelo, intervalo amostral ou intervalo de previsão.

### 12.5 Comparação com baseline

Um baseline é uma política de referência com a qual comparar o método. Deve representar uma alternativa plausível — por exemplo, política inercial/histórica, regra fixa ou heurística simples. Se o baseline não for definido de forma reprodutível, a “melhoria” pode ser consequência da escolha da referência.

### 12.6 Avaliação prospectiva necessária

Para estimar impacto real, um piloto poderia:

1. selecionar unidades ou período de implementação com protocolo aprovado;
2. definir previamente indicadores de custo, disponibilidade, falhas e carga operacional;
3. comparar com uma prática de referência;
4. registrar exceções e decisões humanas;
5. medir efeitos e incerteza;
6. analisar viés de seleção e fatores externos;
7. interromper ou ajustar se houver riscos operacionais.

---

## 13. Triagem patrimonial e avaliação de antieconomicidade

O slide 14 descreve um indicador: custos acumulados de manutenção acima de 40% de um valor de referência adotado sinalizam veículos para avaliação patrimonial. O relatório enfatiza que isso é **um critério de triagem**, não uma regra automática de alienação.

Antes de qualquer decisão, pode ser necessário verificar:

- qual valor de referência foi usado e em que data;
- se o valor é venal, contábil, FIPE ou outra referência;
- custos relevantes e sua janela temporal;
- estado, idade, quilometragem e condição operacional;
- custo de manter em comparação com substituir;
- exigências administrativas e jurídicas aplicáveis;
- laudo técnico e competência decisória.

O slide informa **242 veículos sinalizados** para avaliação, não 313 bens destinados a leilão. O indicador ajuda a organizar uma análise, mas não substitui processo administrativo, avaliação patrimonial ou deliberação de autoridade competente.

---

## 14. Isolation Forest: detecção de atipicidades

### 14.1 Ideia do algoritmo

Isolation Forest identifica observações que parecem diferentes das demais. A intuição é que pontos raros podem ser separados do conjunto com poucas divisões aleatórias:

1. selecionam-se amostras de dados;
2. constroem-se árvores que particionam atributos por cortes aleatórios;
3. mede-se o comprimento médio do caminho necessário para isolar cada observação;
4. caminhos curtos indicam pontos mais fáceis de isolar e, portanto, potencialmente atípicos.

O método não aprende a definição de fraude, porque não recebe necessariamente rótulos confiáveis de fraude.

### 14.2 Parâmetro ν/contaminação

O slide reporta **ν = 0,85%** (notação usada no material) e 662 OS e 13.936 abastecimentos atípicos. Em implementações, o parâmetro de contaminação costuma controlar um limiar ou expectativa de proporção de observações sinalizadas. Ele **não é taxa de fraude** e não prova que cada caso seja irregular.

### 14.3 Por que usar?

Quando não há rótulos completos e confiáveis de irregularidade, detecção não supervisionada pode servir como triagem exploratória para priorizar revisão. O resultado é uma lista de observações incomuns segundo atributos e configuração escolhidos.

### 14.4 Limitações

- O algoritmo depende dos atributos e escalas apresentados.
- A raridade não implica erro ou irregularidade.
- Casos legítimos podem ser raros (especialidade, urgência, geografia).
- Anomalias comuns podem não ser detectadas.
- O limiar altera o volume de sinalizações.
- A métrica precisa ser validada contra revisão humana e documentação.

### 14.5 Índice de Jaccard para estabilidade

Para duas listas de sinalizações A e B:

J(A,B) = |A∩B| / |A∪B|.

J = 1 significa listas idênticas; J = 0 significa nenhuma observação em comum. O valor mede sobreposição entre listas construídas sob execuções ou condições comparadas. Não mede precisão jurídica, taxa de fraude nem validade da anomalia.

---

## 15. SHA-256 e rastreabilidade

### 15.1 O que é hash?

Uma função hash criptográfica mapeia uma mensagem de tamanho variável para uma sequência de tamanho fixo. SHA-256, da família SHA-2, produz 256 bits. Uma alteração no arquivo geralmente muda o hash, permitindo comparar o conteúdo atual com um valor de referência armazenado anteriormente.

### 15.2 O que hash pode e não pode provar?

Com uma referência confiável, SHA-256 ajuda a detectar que o conteúdo mudou. Sozinho, não prova:

- que o dado original era verdadeiro;
- quem criou ou alterou o arquivo;
- quando a alteração ocorreu;
- que a referência foi armazenada de modo seguro;
- que o processo inteiro é imutável;
- que o tratamento está em conformidade com a LGPD.

Uma cadeia de hashes pode ligar registros ou blocos de forma que alterações posteriores sejam detectáveis se referências e chaves forem protegidas. Sem controle de acesso, registros de auditoria, gestão de chaves, política de retenção e armazenamento confiável, a garantia é limitada.

### 15.3 Justificativa

Hash é uma ferramenta leve para verificar integridade de artefatos e apoiar trilha de auditoria. Seu papel é complementar. Deve-se distinguir integridade criptográfica de autenticidade, proveniência e validade semântica.

### 15.4 Proteção e governança

O uso de registros administrativos exige finalidade clara, minimização de dados pessoais, controle de acesso, retenção apropriada e avaliação institucional. Hashing não anonimiza automaticamente dados e não garante conformidade com a LGPD.

---

## 16. Neo4j e os precedentes de auditoria pública

### 16.1 O que é Neo4j?

Neo4j é um banco de dados orientado a grafos. Em seu modelo, nós guardam entidades, relacionamentos conectam nós e propriedades descrevem atributos. Isso favorece consultas que percorrem relações em várias etapas, em vez de montar repetidas junções de tabelas.

### 16.2 O que o precedente sustenta

Garcia (2019), em estudo de pós-graduação do ISC/TCU, explorou o Neo4j como **ferramenta potencial de Data Analytics para auditoria governamental**. Esse trabalho sustenta que bancos de grafos podem ser explorados em análises de relações para auditoria; não prova por si só implantação institucional permanente, adoção normativa ou eficácia em manutenção de frotas.

Soares (2020) estudou padrões topológicos em relações no contexto de vínculos de compras públicas e priorização de casos de auditoria. É um paralelo metodológico: relações complexas podem ser examinadas para direcionar atenção. Não se trata de estudo de manutenção veicular.

### 16.3 Como apresentar o paralelo com precisão

Use:

> “O grafo foi escolhido porque a pergunta envolve relações entre veículos e oficinas. Há precedentes acadêmicos do ISC/TCU que exploraram Neo4j e padrões topológicos como ferramentas potenciais de Data Analytics em auditoria pública. Eles são paralelos metodológicos, não uma norma nem validação do nosso modelo para frotas.”

Evite:

- “O TCU exige grafos para manutenção de frota.”
- “O TCU validou nosso algoritmo.”
- “Uma comunidade detectada é prova de conluio.”

---

## 17. Encadeamento metodológico e justificativa acadêmica

| Componente | Pergunta respondida | Razão de uso | Resultado produzido | Limite principal |
|---|---|---|---|---|
| Análise descritiva | O que aparece nos registros? | Entender dimensão, distribuição e cobertura | Tabelas e resumos | Não explica causa |
| Validação temporal | Como o modelo se comporta em período posterior? | Evitar usar futuro no treino | Métricas retrospectivas | Não substitui piloto |
| HistGradientBoosting | Que risco/custo pode ser estimado? | Aprender relações tabulares não lineares | Escore, probabilidade ou valor | Dependente da distribuição |
| Calibração isotônica | Probabilidades correspondem a frequências? | Melhorar confiabilidade probabilística | Probabilidades calibradas no protocolo | Pode degradar fora do domínio |
| Weibull | Como varia o tempo até falha? | Modelar tempo e censura | Curva de sobrevivência/risco | Hipótese de distribuição |
| Grafo bipartido | Quem se relaciona com quem? | Representar vínculos veículo–oficina | Rede e métricas | Relação não prova irregularidade |
| Louvain | Há grupos densos na rede? | Explorar comunidades | Partição e modularidade | Heurística e escala dependente |
| SHAP/LIME | Quais atributos influenciam a previsão local? | Tornar previsões examináveis | Atribuições/rankings | Não causalidade; divergências |
| MILP/HiGHS | Qual plano minimiza o objetivo sob limites? | Formalizar escolhas discretas e recursos | Plano ótimo da instância | Correto só para formulação |
| Monte Carlo | Como varia o resultado sob incerteza? | Propagar cenários aleatórios definidos | Distribuição de saídas | Depende das premissas |
| Isolation Forest | Quais registros são raros? | Triagem sem rótulo completo | Lista de atipicidades | Raro não é fraude |
| SHA-256 | O arquivo mudou? | Verificar integridade contra referência | Hash comparável | Não prova veracidade/autoria |

### 17.1 Complementaridade, não substituição

Os métodos têm papéis diferentes. A previsão estima; o grafo descreve relações; SHAP/LIME explicam aspectos de uma previsão; o MILP compara ações; detecção de anomalias sinaliza casos; hash verifica alteração. A cadeia só é defensável se cada saída for usada dentro de seu escopo.

### 17.2 Rastreabilidade necessária

Para uma recomendação ser examinável, idealmente é possível recuperar:

- dados usados e período;
- transformação de cada variável;
- versão do modelo;
- alvo e horizonte;
- probabilidades ou custos estimados;
- explicação e suas premissas;
- parâmetros da otimização;
- restrições e objetivo;
- solução do solver e gap;
- decisão humana final e justificativa.

---

## 18. Leitura acadêmica dos resultados apresentados

### 18.1 Rede veículo–oficina

**Resultado do slide:** 18 comunidades, Q = 0,5646; R$ 4,18 milhões em transações priorizadas para possível revisão.

**Leitura cuidadosa:** comunidades e centralidade descrevem a estrutura da rede. O valor transacionado identificado é volume associado a uma seleção de triagem, não irregularidade financeira, superfaturamento ou dano ao erário comprovado. A interpretação exige contexto operacional, documentos e verificação competente.

### 18.2 Explicabilidade

**Resultado do slide:** Jaccard Top-5 = 45,48%; Spearman ρ = 0,2869.

**Leitura cuidadosa:** a concordância entre rankings SHAP e LIME foi limitada segundo os indicadores e a configuração avaliados. A hipótese de alta concordância não foi sustentada nesse teste. Isso recomenda cautela com intercambialidade; não prova que um método seja sempre melhor.

### 18.3 Modelo preditivo

**Resultado do slide:** regressão de custo reporta MAE R$ 2.236,06, RMSE R$ 3.780,20 e R² ajustado 0,1139; classificação reporta Brier 0,1043 e ECE 0,0174; sobrevivência de Weibull tem divergência de forma/notação a confirmar.

**Leitura cuidadosa:** cada métrica corresponde a uma tarefa diferente. R² ajustado do regressor não é acurácia classificatória; Brier/ECE são sobre probabilidades. O valor de Weibull deve ser conferido antes da apresentação oral devido à inconsistência apontada.

### 18.4 Otimização e disponibilidade

**Resultado do slide:** custo S0 R$ 44.190.120,51; MIP gap do solver 0,0000%; gap LP–MIP 0,00063%; disponibilidade média 95,26%.

**Leitura cuidadosa:** o gap descreve a resolução da instância, não a validade dos dados. 95,26% é resultado de disponibilidade no cenário, não meta legal nem restrição formal, salvo evidência de codificação dessa meta.

### 18.5 Comparação econômica

**Resultado do slide:** BL0 R$ 53,14 milhões; MILP-1 R$ 43,84 milhões; diferença R$ 6,99 milhões ou 13,66%.

**Leitura cuidadosa:** são custos modelados no S0 para 2.000 veículos durante 36 meses. A diferença é potencial estimado sob premissas e não economia realizada.

### 18.6 Patrimônio

**Resultado do slide:** 242 veículos sinalizados pelo indicador econômico.

**Leitura cuidadosa:** trata-se de candidatos à avaliação; não de decisão automática de desfazimento, leilão ou alienação.

### 18.7 Anomalias e integridade

**Resultado do slide:** 662 OS e 13.936 abastecimentos sinalizados como atípicos, com ν = 0,85%; uso de SHA-256.

**Leitura cuidadosa:** atipicidade é resultado relativo ao modelo e aos atributos. Hash detecta mudança perante referência; não valida a origem ou o conteúdo.

---

## 19. Roteiro técnico de apresentação por capítulo

### Cap. 1 — Introdução

Comece pela necessidade pública: manter veículos disponíveis com recursos limitados. Apresente a pergunta prática, o objetivo e o escopo. Evite iniciar com siglas ou algoritmos antes de a banca compreender o problema.

### Cap. 2 — Conceitos fundamentais

Explique a diferença entre descrever o passado, estimar um resultado futuro e comparar ações. Diga que previsão não escolhe sozinha a ação e que uma recomendação depende de custos, objetivos e restrições.

### Cap. 3 — Revisão de literatura

Mostre que os métodos têm fundamentos publicados. A contribuição não é reivindicar que HistGradientBoosting, SHAP, LIME, Louvain ou MILP tenham sido inventados pelo trabalho; é a integração e avaliação no recorte público de dados estudado, com limites explicitados.

### Cap. 4 — Proposta

Apresente as fontes e unidades: OS, itens, veículos e abastecimentos. Explique o fluxo metodológico sem afirmar que cada método transfere automaticamente seu resultado ao seguinte.

### Cap. 5 — Validação

Diga qual pergunta cada método responde. Ao mostrar números, informe tarefa, protocolo, cenário, unidade e período. Separe previsões, métricas, resultados do solver e estimativas econômicas.

### Cap. 6 — Discussões

Retorne à pergunta central. Diga o que os resultados permitem afirmar e o que não permitem. Diferencie sinal de triagem, associação, previsão, solução matemática e impacto de campo.

### Cap. 7 — Concluir

Resuma a contribuição integrada e o próximo passo: validação prospectiva, comparação com prática de referência, análise por gestores e monitoramento operacional.

---

## 20. Perguntas prováveis da banca e respostas fundamentadas

### “Por que usar grafos?”

Porque os dados incluem relações entre dois tipos de entidade — veículos e oficinas — e a estrutura dos vínculos é parte da pergunta. O grafo torna possível examinar conectividade e concentração. A análise orienta triagem, não prova irregularidade.

### “O que o Neo4j acrescenta?”

Neo4j é um banco orientado a grafos que permite armazenar e consultar nós, relações e propriedades. Garcia (2019) explorou-o como ferramenta potencial de Data Analytics para auditoria governamental. Esse precedente é metodológico, não uma norma ou validação de nosso caso.

### “Uma oficina central é suspeita?”

Não por si só. Centralidade pode resultar de localização, credenciamento, marca, especialização ou disponibilidade. É um indicador estrutural para escolher casos para revisão contextual.

### “O que significa Q = 0,5646?”

É modularidade calculada para a partição da rede e o modelo nulo empregados. Indica estrutura de comunidades segundo aquela configuração; não é porcentagem de certeza nem prova de conluio.

### “Por que HistGradientBoosting?”

É um método de árvores em ensemble capaz de capturar relações não lineares em dados tabulares. A justificativa deve ser o desempenho comparativo no protocolo temporal adotado e a adequação ao alvo, não uma superioridade universal.

### “Por que calibrar as probabilidades?”

Porque o otimizador usa riscos/probabilidades para comparar custos esperados. Um modelo que ordena casos pode ainda produzir probabilidades exageradas. Calibração busca aproximar probabilidades previstas das frequências observadas no conjunto avaliado.

### “O que significa Brier 0,1043?”

É um erro quadrático médio probabilístico no protocolo de classificação. Menor tende a ser melhor, mas a interpretação depende da prevalência, baseline e dados avaliados. Não significa 89,57% de acurácia.

### “SHAP e LIME discordaram; qual está certo?”

Eles fazem aproximações diferentes e dependem de premissas distintas. A divergência mostra que as explicações não devem ser tratadas como equivalentes. Não há conclusão universal de que um método esteja sempre certo.

### “O MILP encontrou o melhor plano real?”

Encontrou a melhor solução para a função objetivo, dados e restrições da instância dentro da tolerância do solver. A adequação para operação precisa de validação dos parâmetros, das capacidades e das regras.

### “A economia de R$ 6,99 milhões ocorreu?”

Não. É uma diferença de custos modelados no cenário S0, equivalente a potencial estimado de 13,66% sob premissas. Não é economia observada.

### “95,26% era uma meta obrigatória?”

Nos slides, 95,26% é disponibilidade média resultante do cenário. Não deve ser chamada de restrição formal sem confirmar que foi codificada como tal na instância do MILP.

### “242 veículos serão leiloados?”

Não. São veículos sinalizados para avaliação patrimonial pelo critério adotado. Alienação depende de confirmação de valores, laudo e rito administrativo.

### “O Isolation Forest detectou fraude?”

Não. Sinalizou registros atípicos relativamente às variáveis e ao parâmetro usados. Cada sinal precisa de verificação documental e humana.

### “SHA-256 prova que a base é verdadeira?”

Não. Ajuda a detectar alteração em relação a um hash de referência protegido. Não prova que a informação original era verdadeira, quem a criou ou que o tratamento está em conformidade legal.

### “O TCU aprovou essa aplicação?”

Não se afirma isso. Os trabalhos do ISC/TCU citados são precedentes acadêmicos de análise de grafos/Data Analytics em auditoria, em contextos distintos. Não são aprovação da aplicação de manutenção de frotas.

### “Como demonstrar impacto real?”

Com piloto prospectivo e protocolo de comparação, indicadores definidos previamente, acompanhamento de custos e disponibilidade, análise de capacidade, registro de exceções e revisão humana. Só então será possível estimar efeitos operacionais observados.

---

## 21. Recomendações para uma defesa responsável

1. Comece pela pergunta prática e pela contribuição, depois apresente algoritmos.
2. Defina siglas na primeira ocorrência: OS, MILP, SHAP, LIME, ECE.
3. Para cada métrica, diga a tarefa, o conjunto de teste e a unidade.
4. Use “estima”, “sinaliza”, “descreve”, “compara” e “apoia” com precisão.
5. Não diga “prova fraude”, “garante legalidade” ou “economia realizada”.
6. Mostre o TCU/ISC como paralelo metodológico restrito ao escopo das fontes.
7. Explique que SHAP/LIME não são explicações causais.
8. Separe o grafo de prestadores do grafo de coocorrência de falhas.
9. Apresente o ótimo do MILP como ótimo da formulação, não como decisão universal.
10. Declare a necessidade de validação prospectiva e revisão humana.

---

## 22. Referências acadêmicas e técnicas

As referências abaixo fundamentam os conceitos e métodos descritos. A referência completa e a versão final citada devem ser conferidas na dissertação e na bibliografia institucional antes de submissão formal.

### Analítica prescritiva e manutenção

- BERTSIMAS, D.; KALLUS, N. From predictive to prescriptive analytics. *Management Science*, 66(3), 1025–1044, 2020.
- DE CASTRO, H. F.; CAVALCA, K. L. Maintenance resources optimization applied to a fleet of vehicles under budget constraints. *Reliability Engineering & System Safety*, 91(4), 413–424, 2006.
- CRESPO DEL CASTILLO, A.; PARLIKAD, A. K. Dynamic fleet management: Integrating predictive and preventive maintenance with operational workload balancing. *Reliability Engineering & System Safety*, 244, 109968, 2024.
- DALZOCHIO, J. et al. Machine learning and reasoning for predictive maintenance in Industry 4.0: Current status and challenges. *Computers in Industry*, 123, 103298, 2020.

### Validação e aprendizado de máquina

- BERGMEIR, C.; BENÍTEZ, J. M. On the use of cross-validation for time series predictor evaluation. *Information Sciences*, 191, 192–213, 2012.
- FRIEDMAN, J. H. Greedy function approximation: A gradient boosting machine. *The Annals of Statistics*, 29(5), 1189–1232, 2001.
- HASTIE, T.; TIBSHIRANI, R.; FRIEDMAN, J. *The Elements of Statistical Learning*. 2. ed. Springer, 2009.
- BRIER, G. W. Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3, 1950.
- ZADROZNY, B.; ELKAN, C. Transforming classifier scores into accurate multiclass probability estimates. In: *Proceedings of KDD*, 2002.
- GUO, C. et al. On calibration of modern neural networks. In: *Proceedings of ICML*, 2017.

### Sobrevivência, grafos e redes

- WEIBULL, W. A statistical distribution function of wide applicability. *Journal of Applied Mechanics*, 18, 293–297, 1951.
- BLONDEL, V. D. et al. Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008, 2008.
- FREEMAN, L. C. A set of measures of centrality based on betweenness. *Sociometry*, 40(1), 35–41, 1977.
- ROBINSON, I.; WEBBER, J.; EIFREM, E. *Graph Databases: New Opportunities for Connected Data*. 2. ed. O'Reilly Media, 2015.
- KRAWCZYK, H.; BELLARE, M.; CANETTI, R. [HMAC: Keyed-Hashing for Message Authentication](https://www.rfc-editor.org/rfc/rfc2104). RFC 2104, 1997.
- GARCIA, Leonardo Marques. [*O uso de ferramentas de Data Analytics pelo Auditor Governamental*](https://sites.tcu.gov.br/recursos/trabalhos-pos-graduacao/pdfs/O%20uso%20de%20ferramentas%20de%20Data%20Analytics%20pelo%20Auditor%20Governamental.pdf). Coletânea de Pós-Graduação, v. 1, n. 7, Auditoria Financeira. Brasília: Tribunal de Contas da União, Instituto Serzedello Corrêa, 2019.
- SOARES, Claudio Augusto Grünewald. [*Identificação de indícios de irregularidade por meio de padrões topológicos em grafos: aplicação ao banco de vínculos da CGU*](https://sites.tcu.gov.br/recursos/trabalhos-pos-graduacao/pdfs/Identifica%C3%A7%C3%A3o%20de%20ind%C3%ADcios%20de%20irregularidade%20por%20meio%20de%20padr%C3%B5es%20topol%C3%B3gicos%20em%20grafos_%20aplica%C3%A7%C3%A3o.pdf). Trabalho de Conclusão de Curso (Especialização em Análise de Dados para o Controle) – Escola Superior do Tribunal de Contas da União, Instituto Serzedello Corrêa, Brasília, 2020.

### Explicabilidade e auditoria

- LUNDBERG, S. M.; LEE, S.-I. A unified approach to interpreting model predictions. In: *Advances in Neural Information Processing Systems*, 30, 4765–4774, 2017.
- RIBEIRO, M. T.; SINGH, S.; GUESTRIN, C. “Why should I trust you?”: Explaining the predictions of any classifier. In: *Proceedings of ACM SIGKDD*, 1135–1144, 2016.
- RUDIN, C. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1, 206–215, 2019.
- JACCARD, P. The distribution of the flora in the alpine zone. *New Phytologist*, 11(2), 37–50, 1912.
- SPEARMAN, C. The proof and measurement of association between two things. *The American Journal of Psychology*, 15(1), 72–101, 1904.

### Otimização, anomalias e integridade

- HUANGFU, Q.; HALL, J. A. J. Parallelizing the dual revised simplex method. *Mathematical Programming Computation*, 10, 119–142, 2018.
- LIU, F. T.; TING, K. M.; ZHOU, Z.-H. Isolation Forest. In: *Proceedings of IEEE International Conference on Data Mining*, 413–422, 2008.
- NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. *FIPS PUB 180-4: Secure Hash Standard (SHS)*. 2015.
- WILLIAMS, H. P. *Model Building in Mathematical Programming*. 5. ed. Wiley, 2013.

---

## 23. Síntese final

O argumento acadêmico da pesquisa pode ser resumido em quatro afirmações proporcionais às evidências:

1. **Problema:** decisões de manutenção precisam conciliar disponibilidade, recursos limitados e dados administrativos heterogêneos.
2. **Proposta:** articular análise preditiva, análise relacional, explicabilidade e otimização matemática como apoio à decisão.
3. **Evidência:** os métodos foram avaliados em registros e cenários delimitados; há resultados descritivos, preditivos e de otimização condicionais às premissas.
4. **Limite e próximo passo:** os resultados não demonstram impacto real nem substituem decisão administrativa; validação prospectiva e revisão humana são necessárias.

Essa formulação comunica a contribuição sem exagerar novidade, causalidade, conformidade ou economia realizada.

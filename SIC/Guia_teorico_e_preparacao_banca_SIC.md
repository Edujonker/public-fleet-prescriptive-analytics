# Guia teórico e preparação para a banca

## Apresentação do 36º SIC — UDESC

Este guia acompanha a versão revisada para o 36º SIC, com 16 slides [Apresentacao_36_SIC_UDESC_com_bibliografia.pptx](./Apresentacao_36_SIC_UDESC_com_bibliografia.pptx), e serve para preparar o aluno a explicar o projeto, justificar escolhas metodológicas e responder a perguntas da banca. As versões anteriores foram preservadas. O texto foi conferido com a dissertação [dissertacao.pdf](../dissertacao.pdf), especialmente os capítulos de metodologia, resultados, revisão da literatura e conclusões.

> **Regra de ouro da defesa:** diferencie sempre (1) dado observado, (2) estimativa do modelo, (3) resultado de simulação e (4) impacto já realizado na administração. A diferença de custos de R$ 6,99 milhões é uma estimativa teórica do cenário simulado S0; não significa que essa economia tenha sido obtida pelo Estado.

---

## 1. O projeto em uma explicação curta

Uma frota pública precisa manter veículos disponíveis, mas as decisões de manutenção competem por orçamento, horas de oficina e atenção dos gestores. Os registros de manutenção, patrimônio e abastecimento são históricos e não estão necessariamente integrados.

O projeto organiza esses dados, estima risco e custo, examina padrões e usa otimização matemática para comparar planos de intervenção sob restrições. As recomendações devem ser rastreáveis e explicáveis; a decisão final continua com as pessoas responsáveis.

### A linha de raciocínio

**Dados administrativos → auditoria e preparação → análises complementares (previsão, relações em grafos e explicações) → otimização sob restrições → revisão humana.**

Esses componentes se articulam no framework, mas não são todos entradas diretas uns dos outros. Em particular, a rede descreve relações e ajuda a orientar triagem; não se deve afirmar que seus agrupamentos alimentam automaticamente o MILP, a menos que essa ligação esteja explicitamente implementada e validada.

### Organização e linguagem da apresentação

O percurso identifica explicitamente os sete capítulos: Cap. 1 — Introdução (slide 2); Cap. 2 — Conceitos fundamentais (slide 3); Cap. 3 — Revisão de literatura (slides 4–5); Cap. 4 — Proposta (slides 6–7); Cap. 5 — Validação (slides 8–13); Caps. 6 e 7 — Discussões e Concluir (slide 14). Os slides 15–16 trazem referências e agradecimentos. Os Caps. 2 e 3 formam a “literatura passada”. O slide 2 explicita o problema, a relevância, a pergunta e o objetivo; não usa mais o antigo mapa SIC/QUAL.

Mantenha frases diretas, use poucas citações no slide e reserve os detalhes bibliográficos para a dissertação e o slide de referências. Ao resumir a pesquisa, organize a fala em contexto, objetivo, métodos, resultados e conclusão. A capa identifica o apresentador como aluno e resume os métodos em linguagem simples.

### O que é inovação neste trabalho

Não é simplesmente “usar inteligência artificial”. A contribuição proposta é conectar métodos que normalmente aparecem isolados:

1. preparação e auditoria dos registros;
2. aprendizado de máquina para estimar resultados futuros;
3. análise de anomalias e de relações em redes, como linhas complementares de investigação e triagem;
4. explicabilidade para examinar as previsões;
5. programação matemática para converter estimativas em prioridades;
6. supervisão humana e documentação para uso público responsável.

Chame essa contribuição de **arquitetura/framework de apoio à decisão**. Evite dizer que é o primeiro sistema do tipo ou que já está implantado em produção, a menos que haja uma revisão bibliográfica e uma implantação que sustentem essas afirmações.

### Como posicionar a pesquisa frente à literatura

A versão ampliada dos slides acrescenta um quadro de diálogo bibliográfico e um slide de referências selecionadas. O argumento não é que os autores citados tenham deixado de considerar otimização. Ao contrário: eles fundamentam componentes importantes do projeto. O contraste defensável está no **contexto, na integração e na evidência**:

1. **Analítica prescritiva e manutenção:** Bertsimas e Kallus (2020) fundamentam a passagem geral de previsão para decisão. De Castro e Cavalca (2006) estudam otimização de recursos de manutenção para frotas sob orçamento. Crespo del Castillo e Parlikad (2024) integram manutenção preditiva/preventiva e carga operacional. Esta pesquisa situa essa família de ideias em dados administrativos estaduais e compara planos no cenário S0.
2. **Explicabilidade:** Lundberg e Lee (2017) apresentam SHAP; Ribeiro, Singh e Guestrin (2016), LIME; Rudin (2019), a cautela sobre explicações pós-hoc em decisões de alto impacto. A contribuição empírica é comparar as explicações nos dados e reportar baixa concordância no teste feito — não propor um método novo nem provar superioridade universal.
3. **Validação temporal:** Bergmeir e Benítez (2012) fundamentam a avaliação de previsores em séries temporais. O estudo usa partições cronológicas para reduzir uma avaliação otimista por mistura do futuro no treino.
4. **Redes:** Blondel et al. (2008) apresentam Louvain; a dissertação aplica o método à rede veículo–oficina. A aplicação é descritiva e de triagem, não prova causalidade nem ilícito.

**Frase para a banca:** “A pesquisa não reivindica novidade para SHAP, LIME, Louvain, validação temporal ou MILP. O posicionamento é integrar e avaliar esses métodos no contexto da gestão pública de frota catarinense, com orçamento e obrigações explícitas, e reportar também os limites e a divergência das explicações. O resultado de economia permanece contrafactual.”

**Limite do contraste:** a dissertação reúne referências e linhas de pesquisa, mas não descreve uma revisão sistemática comparativa completa de todos os sistemas de gestão de frota. Prefira “o estudo se diferencia pelo recorte e pela integração avaliados” a “a literatura não faz isso” ou “é o primeiro”.

---

## 2. Conceitos e métodos — explicação de sala de aula

### 2.1 CRISP-DM: estruturar o trabalho analítico

CRISP-DM é um processo de mineração de dados organizado em ciclos. Suas etapas clássicas são:

1. **Compreensão do negócio:** entender a decisão que se quer apoiar e o que significa sucesso.
2. **Compreensão dos dados:** conhecer fontes, cobertura, qualidade, unidades e limitações.
3. **Preparação dos dados:** integrar, corrigir, transformar e documentar os dados.
4. **Modelagem:** treinar e comparar métodos.
5. **Avaliação:** verificar se os resultados respondem ao problema e se generalizam.
6. **Implantação:** colocar os resultados em uso, com monitoramento e governança.

As etapas não são uma cascata rígida: os resultados de uma fase podem obrigar a voltar a uma anterior. No projeto, CRISP-DM oferece uma estrutura para ligar a necessidade de gestão à preparação, à análise e à avaliação técnica.

**Como dizer:** “Usei CRISP-DM para organizar o ciclo analítico, começando pelo problema de decisão e não pela escolha de um algoritmo.”

**Ressalva:** seguir CRISP-DM não prova, por si só, a validade do modelo. A validade depende dos dados, do desenho de avaliação e da adequação à decisão.

### 2.2 Auditoria e preparação de dados

Antes de modelar, é necessário saber o que cada linha representa, de onde veio e quais transformações recebeu. Uma ordem de serviço (OS) pode conter vários itens de manutenção; portanto, **350.737 itens não são 350.737 ordens**. A dissertação informa 350.737 itens agrupados em 77.867 OS únicas.

A auditoria também busca:

- duplicatas e identificadores inconsistentes;
- dados ausentes ou categorias com significado ambíguo;
- unidades diferentes para a mesma variável;
- registros de hodômetro impossíveis ou regressivos;
- divergência entre valor orçado, glosa e valor aprovado;
- informação que só estaria disponível depois do momento da previsão.

Uma transformação deve ser reproduzível: registrar regra, versão, entrada e resultado. Excluir ou corrigir um dado sem registrar o motivo pode mudar o resultado de forma impossível de auditar.

**Como dizer:** “A etapa de dados é parte do método, não um detalhe anterior à pesquisa. Ela determina o que o modelo consegue aprender e quais conclusões são legítimas.”

**Distinção financeira essencial:** o valor bruto orçado, as glosas e o valor aprovado são etapas relacionadas do processo. A dissertação explicita R$ 198,81 milhões orçados, R$ 60,05 milhões glosados e R$ 138,76 milhões aprovados. Glosa não deve ser automaticamente chamada de economia de caixa realizada.

### 2.3 Validação temporal e vazamento de dados

Em dados de frota, o futuro não pode ser usado para prever o passado. Uma divisão aleatória de linhas pode misturar observações de meses futuros no treino e meses anteriores no teste. Isso costuma produzir uma avaliação otimista.

Na validação temporal:

1. o modelo é treinado em períodos anteriores;
2. é avaliado em um período posterior;
3. a janela avança em ordem cronológica;
4. repete-se o procedimento em várias janelas.

A dissertação descreve cinco dobras temporais e um embargo de 30 dias. O embargo deixa um intervalo entre treino e teste para reduzir contaminação por registros próximos ou informação operacional que atravesse a fronteira temporal.

**Vazamento temporal (data leakage)** ocorre quando uma variável de entrada contém, direta ou indiretamente, informação que não estaria disponível no instante real da decisão. Um exemplo seria usar o custo final de uma OS para prever o risco de uma falha que ocorreu antes.

**Como dizer:** “O teste simula uma implantação retrospectiva: em cada dobra, treino com o passado e avalio no futuro. Isso é mais coerente com a previsão operacional do que embaralhar os registros.”

**Limite:** validação temporal melhora a avaliação retrospectiva, mas não equivale a um piloto prospectivo nem garante que os padrões permanecerão iguais no futuro.

### 2.4 Aprendizado supervisionado: classificação e regressão

O aprendizado supervisionado usa exemplos históricos com uma variável-alvo conhecida.

- **Classificação:** estima uma classe ou probabilidade, como risco de manutenção corretiva no horizonte definido.
- **Regressão:** estima um valor numérico, como custo de manutenção.

O **HistGradientBoosting** é um ensemble de árvores. Em termos simples, constrói uma sequência de árvores pequenas; cada nova árvore tenta corrigir erros que as anteriores ainda cometem. O resultado consegue representar relações não lineares e interações entre atributos, sem exigir que a relação entre cada variável e o resultado seja uma linha reta.

Um modelo mais complexo não é automaticamente melhor. Ele deve ser comparado a baselines simples e avaliado em dados que não participaram do treinamento.

#### Métricas que podem aparecer na banca

- **MAE (erro absoluto médio):** média do tamanho dos erros, na mesma unidade do alvo. Se o MAE é R$ 2.236, isso não significa que toda previsão erra exatamente esse valor.
- **RMSE (raiz do erro quadrático médio):** penaliza mais fortemente os erros grandes; é útil quando erros extremos têm custo especial.
- **R²:** mede quanto da variação do alvo é explicada pelo modelo em relação a um baseline de média, no conjunto avaliado. Pode ser baixo ou negativo e não deve ser confundido com AUC.
- **PR-AUC:** resume a curva precisão-revocação, especialmente informativa quando a classe positiva é rara ou quando os custos de falsos positivos e falsos negativos importam.
- **ROC-AUC:** mede a capacidade de ordenar positivos acima de negativos em diferentes limiares. Uma ROC-AUC de 0,5 corresponde, em expectativa, a ordenação aleatória.
- **F1:** média harmônica entre precisão e revocação para um limiar específico. O resultado depende da escolha desse limiar.

Para a classificação, escolher PR-AUC como métrica principal é defensável em cenários desbalanceados. A linha de base de uma curva precisão-revocação depende da prevalência da classe positiva; por isso, PR-AUC deve ser interpretada junto com a prevalência e outras métricas.

**Como dizer:** “Não escolhi o modelo olhando apenas uma métrica. Avaliei discriminação, erro e qualidade das probabilidades, com divisão temporal.”

#### Regressão e distribuição assimétrica

Custos de manutenção costumam ter muitos valores pequenos e poucos reparos muito caros. Essa distribuição assimétrica pode fazer MAE e RMSE contarem histórias diferentes:

- MAE dá o mesmo peso linear a cada real de erro;
- RMSE aumenta o peso de erros grandes;
- a mediana histórica pode ser um baseline forte para MAE, pois a mediana minimiza a perda absoluta;
- um modelo pode ser útil para capturar caudas ou reduzir RMSE sem vencer a mediana em MAE.

Não descreva um regressor como “melhor em tudo” sem explicitar a métrica e o conjunto de teste.

### 2.5 Calibração de probabilidades

Um classificador pode ordenar corretamente casos de maior e menor risco, mas ainda produzir probabilidades exageradas ou tímidas. Um modelo está calibrado se, entre os casos aos quais atribui aproximadamente 70% de risco, a frequência observada de eventos fica próxima de 70%.

A **calibração isotônica** ajusta uma função monotônica entre os escores do modelo e as frequências empíricas. Ela não precisa ser uma reta, mas pressupõe que a ordem dos escores seja útil. A calibração deve ser ajustada em dados apropriados e não no conjunto final usado para avaliação.

- **Brier Score:** erro quadrático médio entre probabilidades previstas e resultados 0/1; menor costuma ser melhor.
- **ECE (Expected Calibration Error):** agrega diferenças entre probabilidade média prevista e frequência observada em grupos de risco; depende da forma de agrupar os casos.

**Por que isso importa no projeto?** O otimizador usa probabilidades de falha para estimar risco residual. Se essas probabilidades forem mal calibradas, o custo esperado de não intervir pode ficar distorcido.

**Ressalva:** boa calibração no teste avaliado não garante calibração em outros órgãos, períodos ou populações. Deve-se monitorar e recalibrar se houver mudança de padrão.

### 2.6 Detecção não supervisionada de anomalias: Isolation Forest

Métodos não supervisionados procuram padrões incomuns sem depender de um rótulo confiável de “fraude” ou “erro”. O **Isolation Forest** parte da ideia de que pontos raros tendem a ser separados do restante do conjunto com poucas divisões aleatórias. Quanto mais fácil isolar uma observação, mais atípica pode ser.

No trabalho, a análise usa combinações de atributos operacionais, como custo, tempo de imobilização, hodômetro e idade. O parâmetro de contaminação define quantos pontos o algoritmo espera sinalizar como atípicos; ele **não é a taxa verdadeira de irregularidade**.

O estudo também compara listas de anomalias entre execuções. O índice de **Jaccard** entre dois conjuntos é:

`J(A,B) = |A ∩ B| / |A ∪ B|`

Valor alto indica maior sobreposição entre as listas sob as execuções avaliadas. Isso mede estabilidade de seleção, não precisão jurídica ou taxa de fraude.

**Interpretação correta:** “Foram sinalizadas observações para triagem humana.”

**Interpretação incorreta:** “O modelo provou superfaturamento” ou “o percentual de contaminação é o percentual de fraude.”

### 2.7 Teoria dos grafos, rede bipartida e Louvain

Um grafo é formado por **nós** e **arestas**. No grafo bipartido veículo–oficina:

- um conjunto de nós representa veículos;
- o outro conjunto representa oficinas;
- uma aresta representa uma relação observada, por exemplo, um serviço prestado;
- a aresta pode receber um peso, como número de serviços ou valor transacionado.

Esse formato é apropriado porque a relação liga dois tipos distintos de entidade. Ele ajuda a descrever concentração, conectividade e agrupamentos.

- **Grau:** número de ligações de um nó.
- **Centralidade de intermediação (betweenness):** frequência com que um nó aparece em caminhos mínimos entre outros nós; pode indicar posição estrutural importante na rede.
- **Modularidade Q:** compara a densidade de ligações dentro de grupos com a esperada em uma rede de referência. O algoritmo de Louvain procura partições com modularidade elevada.
- **Comunidade:** grupo de nós mais interligados entre si que com o restante da rede, segundo a estrutura e os parâmetros analisados.

Uma comunidade regional pode refletir distância, especialidade, regras de credenciamento ou distribuição da frota. **Não prova conluio, cartel, monopólio nem causalidade.** Betweenness alta também não é, isoladamente, evidência de irregularidade.

**Como dizer:** “A rede identifica concentração e relações que podem orientar uma auditoria. Para determinar se essa concentração é irregular, é preciso contexto operacional e prova documental.”

#### Como o grafo é construído e usado neste projeto

O grafo não é uma nova fonte de dados: é uma representação relacional derivada dos registros administrativos já existentes. A transformação conceitual é:

1. **Selecionar entidades:** na rede bipartida, um conjunto de nós representa veículos e o outro representa oficinas credenciadas.
2. **Definir a relação:** cria-se uma aresta quando os registros indicam uma relação de serviço/transação entre um veículo e uma oficina. Cada aresta deve corresponder a um vínculo sustentado pelos dados, e não a uma associação presumida.
3. **Acrescentar atributos:** quando disponíveis e apropriados, os registros associados podem descrever data, tipo de serviço, volume de ocorrências ou valor. Um peso pode resumir volume ou valor, mas sua definição precisa ser explícita; aresta mais pesada significa apenas mais da grandeza escolhida, não maior risco de irregularidade.
4. **Analisar a estrutura:** grau descreve quantas conexões um nó tem; betweenness descreve sua posição em caminhos da rede; Louvain procura grupos mais densamente conectados segundo a estrutura observada.
5. **Usar como triagem:** concentração, posição central ou comunidades podem ajudar a priorizar perguntas e amostras para análise documental. A rede não decide sanções, não comprova irregularidade e não substitui a inspeção dos registros originais.

Na dissertação, a rede bipartida veículo–oficina contém 7.291 nós de veículos e 1.039 estabelecimentos credenciados. A análise original projetou os vínculos em uma rede de oficinas e identificou 18 comunidades, com modularidade Q = 0,5646, na configuração reportada. Esses números descrevem a rede e o método usados, não a proporção de transações irregulares nem uma medida de desempenho preditivo.

O trabalho também descreve uma **segunda representação**, distinta da rede veículo–oficina: um grafo de coocorrência de falhas/sistemas, em que os nós são categorias de falha e as conexões representam ocorrências conjuntas nos registros. Louvain identificou quatro comunidades nessa análise (Q = 0,384). O resultado resume padrões de coocorrência; não comprova que uma falha causou outra. Não misture os nós, as arestas ou os resultados desse grafo com os da rede bipartida.

**Exemplo para ensinar:** se um registro válido associa o veículo V-12 à oficina O-4, há uma aresta V-12–O-4. Se houver mais registros desse vínculo, uma agregação pode representar essa repetição por peso, desde que a regra esteja declarada. A rede permite perguntar “quais oficinas concentram vínculos?” ou “que grupos aparecem na estrutura observada?”; não permite concluir, sozinha, “por que isso ocorreu?” ou “houve fraude?”.

#### Por que grafos neste problema?

O motivo principal é metodológico: a pergunta envolve **relações** entre dois tipos de entidade — veículos e oficinas — e não apenas atributos isolados de cada veículo. A representação bipartida deixa explícito quem se relaciona com quem por meio dos serviços registrados. Isso facilita examinar concentração, conectividade, posição de intermediação e agrupamentos, além de ajudar a selecionar casos para revisão humana.

Uma tabela ainda é necessária para auditoria e análise estatística; o grafo não a substitui. Ele é uma representação complementar, escolhida porque torna a estrutura relacional mais direta de consultar. No framework, seus resultados apoiam leitura estrutural e triagem; não são automaticamente uma variável ou restrição da otimização. Os resultados dependem da definição da aresta, da agregação, da cobertura dos registros e do método de comunidade.

#### O que as referências do TCU sustentam — e o que não sustentam

- **Garcia (2019), trabalho de pós-graduação do ISC/TCU:** explorou o Neo4j — um banco de dados em grafos — como ferramenta potencial de Data Analytics para auditoria governamental. A ideia é organizar entidades e suas relações para facilitar consultas e análises de vínculos. É um estudo acadêmico/exploratório; não demonstra por si só implantação institucional permanente.
- **Soares (2020), trabalho de especialização do ISC/TCU:** aplica padrões topológicos a relações do banco de vínculos da CGU, no contexto de processos de compras, e discute priorização de casos para auditoria. É um precedente metodológico em controle público, mas **não é estudo de manutenção de frotas**.
- **Portal IA no TCU:** descreve salvaguardas das iniciativas do próprio Tribunal, como revisões periódicas, registros auditáveis e ausência de decisão automatizada sobre cidadãos. É uma referência de governança institucional; não deve ser apresentada como norma geral que, por si só, imponha esses requisitos a todo projeto acadêmico ou órgão público.
- Os Acórdãos 2.493/2024 e 2.591/2024, citados em análise secundária, discutem uso/possibilidade de tecnologia e IA em contextos distintos — Proagro/sensoriamento remoto e qualidade de dados previdenciários. **Não validam um sistema preditivo de manutenção de frota**, nem são evidência de que o TCU prescreva grafos para essa finalidade.

**Implementação no projeto:** além da análise com NetworkX, foi criado um protótipo local em Neo4j Community 5.26. A carga considerou 60.114 registros cobrados com identificadores preenchidos e confirmou no banco 7.291 nós de veículos, 1.039 nós de oficinas e 25.122 relações veículo–oficina. A soma dos valores aprovados nesses registros é R$ 131.506.578,94; não é economia, impacto nem indicação de irregularidade. A projeção de oficinas contém 803 nós participantes e 6.937 relações, conforme o limiar de dois veículos compartilhados. Esses totais validam a carga do grafo, não a interpretação causal dos vínculos.

Os identificadores de origem são pseudonimizados por HMAC-SHA-256 com segredo local. O protótipo não armazena placas, nomes, CPF/CNPJ, notas livres ou registros de abastecimento; também não é uma implantação de produção. As consultas Cypher permitem explorar e verificar relações, mas **não foi executado Louvain dentro do Neo4j**: Q = 0,5646 e as 18 comunidades continuam sendo resultados do pipeline original. O relatório agregado e as instruções reprodutíveis estão em `dissertacao_frotas/resultados/logs/relatorio_neo4j_grafo.json` e `graphdb/README.md`.

**Conclusão defensável:** “Usamos grafos porque a estrutura relacional veículo–oficina é central à pergunta. Criamos também um protótipo local Neo4j para persistir e consultar essa rede, usando identificadores pseudonimizados. Os trabalhos do ISC/TCU são precedentes acadêmicos de grafos e Data Analytics em auditoria; não afirmamos que o TCU determinou ou validou esta aplicação à manutenção de frotas.”

**Resposta curta se perguntarem ‘o Neo4j calculou o Louvain?’:** “Não. O Neo4j está implementado como banco para persistir e consultar as relações. O resultado de Louvain apresentado veio do pipeline de análise de redes já descrito na dissertação; não atribuímos esse cálculo ao banco.”

### 2.8 Explicabilidade: SHAP, LIME e concordância

Explicabilidade busca tornar mais compreensível a relação entre atributos e uma previsão. Ela não transforma automaticamente uma associação preditiva em explicação causal.

#### SHAP

SHAP distribui a diferença entre uma previsão e um valor de referência entre as variáveis. A inspiração são os valores de Shapley da teoria dos jogos: cada variável é tratada como participante de uma coalizão, e sua contribuição média é calculada em diferentes combinações.

SHAP possui propriedades teóricas úteis sob suas definições e hipóteses, mas os valores dependem da escolha do baseline, do modelo, do método de cálculo e do tratamento de dependências entre atributos.

#### LIME

LIME explica uma previsão específica ajustando um modelo simples e interpretável nas proximidades daquela observação. O modelo local aproxima o comportamento do modelo complexo em uma vizinhança artificialmente construída.

Essa explicação pode depender da definição de proximidade, das perturbações amostradas, da escala das variáveis e do tamanho da vizinhança. LIME não é “sempre instável”, assim como SHAP não é automaticamente “a verdade”.

#### Comparar as explicações

- **Jaccard Top-5** compara a sobreposição dos cinco atributos mais importantes em dois rankings.
- **Spearman ρ** compara a ordem dos rankings; ρ próximo de 1 significa ordenação semelhante, 0 pouca associação monotônica e -1 ordenação inversa.

A dissertação informa concordância Top-5 de 45,48% e Spearman ρ = 0,2869 nas condições avaliadas. Isso sustenta a conclusão de que **a hipótese de alta concordância não foi sustentada nesse experimento**. Não sustenta que os métodos são universalmente incompatíveis, que SHAP é sempre superior ou que um deles seja legalmente válido por definição.

**Como dizer:** “A divergência é um resultado do estudo e um alerta metodológico. Recomenda comparar explicações, testar estabilidade e manter avaliação humana.”

### 2.9 Confiabilidade e distribuição Weibull

A análise de sobrevivência estuda o tempo até um evento, como falha, permitindo lidar com observações cujo evento ainda não ocorreu até o fim do período observado.

Uma observação é **censurada à direita** quando sabemos que o veículo permaneceu sem falhar pelo menos até determinado momento, mas não observamos sua falha durante o estudo. Descartar esses casos pode enviesar a análise.

A distribuição Weibull é flexível e inclui um parâmetro de forma `k`:

- `k < 1`: taxa de falha tende a diminuir com o tempo;
- `k = 1`: caso exponencial, com taxa constante;
- `k > 1`: taxa de falha tende a aumentar com o tempo.

No texto principal da dissertação, o parâmetro informado é aproximadamente `k = 1,458`; o slide registra `β = 1,42`. Confirme qual ajuste e qual notação correspondem à figura que será apresentada. Um parâmetro maior que 1 é compatível com risco crescente no modelo ajustado, mas não demonstra sozinho que envelhecimento é a causa da falha.

### 2.10 Séries temporais: tendência, sazonalidade e Prophet

Uma série temporal é uma sequência de observações ordenadas no tempo. A decomposição procura separar:

- **tendência:** movimento de longo prazo;
- **sazonalidade:** padrão que se repete em períodos, como meses ou dias da semana;
- **resíduo:** variação não explicada pelos componentes escolhidos.

Prophet representa a série como combinação de tendência, sazonalidades e, quando apropriado, feriados ou eventos. SARIMA e ETS são famílias de métodos de séries temporais que podem servir como benchmarks.

Uma projeção para frente depende da estabilidade dos padrões históricos e das hipóteses do modelo. Sazonalidade ou crescimento passado não são garantia de que o mesmo padrão se repetirá.

**Na apresentação:** se o gráfico de série temporal não for o foco da pergunta, explique apenas o que a análise adiciona ao planejamento de demanda e capacidade. Não confunda a taxa estimada de crescimento nominal com inflação causal ou com economia do MILP.

### 2.11 Otimização prescritiva: Programação Linear Inteira Mista

O MILP transforma o problema de decisão em variáveis, função objetivo e restrições. “Linear” significa que objetivo e restrições são expressos por combinações lineares das variáveis; “inteira” significa que algumas variáveis só podem assumir valores inteiros; “mista” significa que também pode haver variáveis contínuas.

Na formulação simplificada da dissertação:

- `x_it = 1` se a intervenção planejada para veículo `i` no período `t` é selecionada; caso contrário, `x_it = 0`;
- `c_it` representa o custo preventivo associado à intervenção;
- `r_it` representa o custo esperado do risco se não houver intervenção;
- `B_t` é o orçamento disponível no período;
- `H_t` é a capacidade de horas/oficina;
- `m_it` indica se uma manutenção mandatória precisa ser realizada.

Uma forma simplificada da função objetivo é:

`min Σ[c_it x_it + r_it(1 − x_it)]`

O termo `c_it x_it` contabiliza o custo de intervir; `r_it(1 − x_it)` contabiliza o risco residual quando a intervenção não é selecionada. Entre as restrições estão orçamento, capacidade e `x_it ≥ m_it` para garantir intervenções mandatórias.

**Por que é prescritivo?** O classificador estima riscos e o regressor estima custos; o MILP combina essas estimativas e escolhe ações viáveis segundo o objetivo e as restrições definidos.

#### HiGHS, branch-and-cut e gap

HiGHS é um solver de otimização. Em problemas inteiros, métodos de branch-and-bound/branch-and-cut exploram e descartam regiões de soluções usando limites matemáticos até provar otimalidade ou atingir uma tolerância.

Não confunda:

- **MIP gap do solver:** diferença relativa entre a melhor solução inteira viável conhecida e o melhor limite global conhecido. Um gap reportado como 0,0000% indica convergência dentro da tolerância do solver para aquele modelo.
- **Gap de integralidade LP–MIP:** diferença entre a solução do modelo inteiro e a solução da relaxação linear, onde uma variável binária pode assumir valores fracionários entre 0 e 1. Na dissertação, a diferença indicada é cerca de 0,00063%.

Um ótimo computacional significa “ótimo para a formulação, parâmetros e dados fornecidos”, não “melhor decisão possível no mundo real”. O solver não corrige uma função objetivo inadequada, dados enviesados ou restrições incompletas.

### 2.12 Políticas de comparação e fronteira de Pareto

O modelo deve ser comparado a políticas de referência, como política histórica, regra fixa, seleção por maior risco ou heurística de benefício/custo. O propósito é evitar concluir que o MILP é útil apenas porque ele próprio encontrou uma solução.

Uma heurística gulosa escolhe uma alternativa de cada vez por uma regra local. Pode ser rápida, mas não garante que o conjunto final seja globalmente ótimo nem que todas as restrições sejam respeitadas. A comparação deve separar **custo**, **disponibilidade** e **conformidade obrigatória**.

Uma fronteira de Pareto mostra alternativas em que melhorar um objetivo pode piorar outro. Uma solução domina outra se é pelo menos tão boa em todos os objetivos e melhor em pelo menos um. Na gestão de frotas, uma solução mais barata que viola manutenção obrigatória não é uma alternativa aceitável só por seu custo.

### 2.13 Simulação de Monte Carlo e incerteza

Monte Carlo repete um cálculo muitas vezes, sorteando entradas de acordo com distribuições ou intervalos assumidos. O conjunto de resultados mostra como a saída varia sob as incertezas representadas.

No projeto, a análise perturba parâmetros como orçamento e custos de falha para estimar como a diferença entre custos modelados varia no horizonte simulado. Isso é uma **análise de sensibilidade probabilística**, não observação de economias futuras nem garantia de que o intervalo contenha o resultado real.

Para responder sobre as projeções de aproximadamente R$ 40 milhões, especifique:

1. horizonte temporal;
2. parâmetros que variaram;
3. distribuições e amplitudes usadas;
4. número de simulações;
5. intervalo e medida reportados;
6. cenário de referência.

O texto apresenta pelo menos dois resultados que devem ser distinguidos: uma projeção nominal para 2027–2029 de R$ 40,088 milhões, associada a um cenário de inflação setorial de 6,08% a.a.; e uma análise de sensibilidade Monte Carlo de aproximadamente R$ 40,19 milhões, com intervalo de 95% de R$ 37,02M a R$ 43,44M, sob perturbações especificadas de orçamento e custo de falha. Eles podem representar protocolos distintos; descreva-os como estimativas de cenários, não como valores economizados. Antes de citar Monte Carlo, confira o relatório executado e o intervalo correspondente.

### 2.14 Desincorporação patrimonial

O critério econômico compara despesas de manutenção acumuladas com o valor venal ou patrimonial do veículo. A razão ajuda a identificar bens que merecem avaliação para eventual substituição ou alienação.

Um limiar analítico não é, por si só, uma ordem automática de leilão. A decisão exige verificar o dispositivo normativo aplicável, a base de valor correta (venal, FIPE ou contábil, conforme a regra), a condição do bem, custos de substituição, laudo e aprovação das instâncias competentes.

**Como dizer:** “O modelo sinaliza veículos que podem merecer avaliação de antieconomicidade. A alienação depende de procedimento e decisão administrativa.”

### 2.15 Hash SHA-256, cadeia de auditoria e proteção de dados

Uma função hash converte dados de tamanho variável em um resumo digital de tamanho fixo. SHA-256 é usada para comparar a integridade de arquivos: se o conteúdo mudar, o hash provavelmente muda.

Uma cadeia de hashes pode tornar alterações posteriores detectáveis se os hashes de referência forem armazenados e protegidos. Porém:

- hash não prova que o dado original era verdadeiro;
- não prova sozinho quem o produziu nem quando;
- não garante imutabilidade absoluta;
- não substitui assinatura, controle de acesso, backup, registro de eventos e governança;
- não é, isoladamente, conformidade com a LGPD.

MD5 tem fragilidades conhecidas para resistência a colisões e não deve ser apresentado como mecanismo criptográfico forte de integridade contra um agente malicioso.

**Como dizer:** “A trilha de hashes pode ajudar a detectar alteração do arquivo em relação a uma referência preservada. Ela complementa controles de auditoria, mas não substitui controles de segurança ou validação da origem.”

---

## 3. Guia de fala seguindo os capítulos

A versão do 36º SIC tem 16 slides. Os Caps. 2 e 3 compõem a literatura passada; os demais capítulos seguem o percurso problema → conceitos → estudos anteriores → proposta → validação → discussão e conclusão. Use as falas como apoio, não como texto para leitura literal.

| Capítulo | Slides | Ideia principal |
|---|---:|---|
| 1 — Introdução | 2 | Problema, relevância pública, pergunta e objetivo. |
| 2 — Conceitos fundamentais | 3 | Do histórico à previsão e à comparação de ações. |
| 3 — Revisão de literatura | 4–5 | Métodos existentes e posicionamento do estudo. |
| 4 — Proposta | 6–7 | Dados, grafo veículo–oficina e protótipo Neo4j. |
| 5 — Validação | 8–13 | Explicabilidade, modelos, otimização, cenários e triagem. |
| 6 — Discussões | 14 | Inovação, contribuição e limites da evidência. |
| 7 — Concluir | 14 | Síntese e próximo passo: piloto controlado. |
| Referências e agradecimentos | 15–16 | Fontes selecionadas e encerramento. |

### Slide 1 — Capa

“Este projeto estuda como dados administrativos, métodos analíticos e otimização podem apoiar a priorização de manutenção em frotas públicas. Sou aluno do PPGCAP/UDESC; a decisão final permanece com os gestores.”

### Cap. 1 — Introdução | Slide 2 — Problema e objetivo

“Os registros de manutenção, custos, patrimônio e abastecimento estão dispersos. Isso dificulta comparar prioridades quando orçamento, capacidade de oficina e disponibilidade dos veículos são limitados. A pergunta é: como priorizar manutenções com os recursos existentes? O objetivo é desenvolver e avaliar um método de apoio à decisão que combine dados, estimativas e otimização, com critérios explícitos e revisão humana.”

### Cap. 2 — Conceitos fundamentais | Slide 3 — Do histórico à decisão

“Primeiro descrevemos o que ocorreu; depois exploramos padrões, estimamos risco ou custo e comparamos ações viáveis. O MILP é uma ferramenta para escolher entre alternativas segundo uma função objetivo e restrições. Uma associação observada não prova causa, e uma previsão não é automaticamente uma recomendação.”

### Cap. 3 — Revisão de literatura | Slides 4–5

“Os métodos usados — modelos preditivos, SHAP, LIME, grafos, Louvain e MILP — são conhecidos. A pesquisa se posiciona pela integração e avaliação desses métodos em dados administrativos de uma frota pública catarinense, com orçamento, capacidade e obrigações explícitas. A comparação de SHAP e LIME encontrou concordância Top-5 de 45,48%; isso descreve este teste, não uma superioridade universal.”

### Cap. 4 — Proposta | Slides 6–7

“Os dados incluem 77.867 ordens e 350.737 itens de manutenção, além de registros patrimoniais e abastecimentos. Uma OS pode conter vários itens, então são unidades diferentes. O grafo representa vínculos observados entre veículos e oficinas. Implementamos um protótipo local em Neo4j para armazenar e consultar essas relações com identificadores pseudonimizados. Louvain foi calculado no pipeline original, não dentro do Neo4j.”

### Cap. 5 — Validação | Slides 8–13

“A validação avalia métodos distintos com métricas adequadas a cada tarefa. SHAP e LIME produzem explicações locais de formas diferentes; modelos estimam risco e custo; e o MILP compara alternativas sujeitas às regras codificadas. Os resultados de grafo e de anomalia ajudam a selecionar registros para revisão, mas não provam causalidade, conluio ou fraude.”

“No cenário S0, a diferença modelada entre BL0 e MILP-1 é de R$ 6,99 milhões, ou 13,66%, para 2.000 veículos durante 36 meses. É uma estimativa contrafactual, não economia realizada. Da mesma forma, os 242 veículos sinalizados são uma lista para avaliação patrimonial, não uma ordem de alienação.”

### Caps. 6–7 — Discussões e conclusão | Slide 14

“A contribuição está em integrar dados, estimativas, relações em grafos, explicabilidade e otimização para apoiar decisões rastreáveis. O impacto operacional ainda não foi validado. A conclusão é que o método oferece uma forma estruturada de comparar prioridades; o próximo passo é um piloto controlado com gestores, comparação contra a prática atual e avaliação prospectiva.”

### Slides 15–16 — Referências e agradecimentos

“O slide 15 traz referências selecionadas; a lista completa está na dissertação. No encerramento, agradeço à orientação, ao PPGCAP e à UDESC. Sou aluno do programa.”

---

## 4. Pontos da apresentação que merecem correção ou ressalva

Use esta lista para revisar a fala e, idealmente, os slides antes da banca.

| Slide | Formulação atual ou risco | Formulação mais defensável |
|---|---|---|
| 3 | “Disponibilidade ≥ 95%” pode soar como exigência geral ou legal. | Diga de onde vem a meta e se é premissa, parâmetro operacional ou resultado. O S0 reporta disponibilidade média de 95,26%. |
| 4, 9–11 | “Causal”, “monopolista”, “conluio” podem sugerir prova causal ou jurídica. | Use “padrão associado”, “concentração”, “posição na rede” e “sinal para triagem”. |
| 5 | O slide pode dar a entender que a pesquisa inventou métodos de manutenção ou XAI. | Cite autores e diga que a contribuição é integração/aplicação e avaliação no recorte estudado. |
| 6 | O trabalho do ISC/TCU pode ser apresentado como validação ou norma para frotas. | Chame-o de precedente acadêmico de grafos/Data Analytics em auditoria; deixe explícito que não estuda manutenção de frotas. |
| 11 | “Por que LIME falha” e “SHAP garante devido processo” são afirmações universais. | Os métodos divergiram neste estudo; nenhum método, isoladamente, garante legalidade ou devido processo. |
| 10 | `R² = 0,748` não coincide com o resultado de regressão no capítulo 6. | O capítulo 6 reporta `R² ajustado = 0,1139`, MAE de R$ 2.236,06 e RMSE de R$ 3.780,20. |
| 10 | Weibull `β = 1,42` diverge ligeiramente do `k = 1,458` do texto. | Confirmar fonte, variável e notação da figura. |
| 12 | 95,26% aparece como piso obrigatório. | O capítulo 9 apresenta 95,26% como saída média do cenário S0; não confundir saída com restrição. |
| 13 | “Economia direta” e projeção de R$ 40 milhões podem soar realizadas/garantidas. | Diga “potencial de redução de custos estimado pela análise teórica”. Diferencie a projeção nominal da análise Monte Carlo e informe premissas. |
| 14 | “Leilão imediato” ou “classificação legal automática”. | Diga “sinalização para avaliação patrimonial”; alienação exige rito e decisão da autoridade competente. |
| 15 | Hash como imutabilidade absoluta ou conformidade LGPD automática. | Hash ajuda a detectar mudança perante uma referência protegida; não substitui controles de segurança e governança. |
| 17 | “Primeiro framework”, economia como impacto e publicação Qualis A1 como certeza. | Apresente contribuição delimitada, estimativa de cenário e objetivos futuros verificáveis. |

### Inconsistências metodológicas que a banca pode perceber

1. **Unidade de análise:** manter sempre clara a diferença entre itens de manutenção, ordens de serviço, veículos e abastecimentos.
2. **Protocolos e métricas:** a dissertação contém resultados de validação temporal multianual e de teste retido; não misture métricas sem dizer qual protocolo, alvo e período correspondem.
3. **Classificação versus regressão:** `ROC-AUC`, `PR-AUC` e `R²` medem aspectos diferentes. AUC não é R².
4. **Valor bruto, glosa e valor aprovado:** são componentes do fluxo orçamentário e não três economias independentes.
5. **Simulação versus operação:** nem a otimização exata nem Monte Carlo provam, sem implantação, que a economia será realizada.

---

## 5. Perguntas prováveis da banca — respostas para treinar

### 1. Qual é a pergunta central da pesquisa?

“Como integrar dados administrativos, estimativas de risco e custo e otimização para apoiar a priorização de manutenção em frotas públicas, respeitando restrições e mantendo rastreabilidade.”

### 2. Onde está a inovação?

“Na integração entre a camada preditiva e a prescritiva, com regras explícitas, avaliação de explicações e preocupação com auditabilidade. O sistema não só estima risco; também compara planos de ação viáveis.”

### 3. Por que usar CRISP-DM?

“Porque oferece um ciclo conhecido para relacionar problema, dados, preparação, modelagem, avaliação e uso. Foi uma estrutura de processo; a validade vem dos protocolos de avaliação e das evidências, não do nome do framework.”

### 4. Por que não dividir aleatoriamente os dados?

“Porque a decisão é temporal. Treinar com registros de meses futuros e testar em meses passados criaria vazamento e uma avaliação irrealista. A validação cronológica aproxima melhor o uso pretendido.”

### 5. Como vocês definiram a variável de risco?

Explique a definição exata do alvo, horizonte `t+1`, regra para identificar evento positivo e disponibilidade das variáveis no instante da previsão. **Treine essa resposta com o pipeline e o protocolo correspondentes**; não basta dizer “falha mecânica” genericamente.

### 6. Por que usar PR-AUC?

“Porque a distribuição das classes é desigual e a curva precisão-revocação permite observar o compromisso entre precisão e revocação para a classe positiva. Reporto junto a prevalência, calibração e outras métricas, pois PR-AUC depende do equilíbrio de classes.”

### 7. Por que HistGradientBoosting?

“Foi comparado com outros candidatos. No protocolo de classificação citado, apresentou desempenho competitivo/superior e calibração útil para o otimizador. A escolha depende do protocolo e da métrica; não afirmo superioridade universal.”

### 8. O que quer dizer calibrar uma probabilidade?

“Significa alinhar a frequência observada à probabilidade prevista: entre casos previstos perto de 70%, esperar que aproximadamente 70% apresentem o evento, no domínio avaliado. Isso é diferente de apenas ordenar corretamente os casos.”

### 9. O Isolation Forest prova fraude?

“Não. Ele detecta observações raras segundo as variáveis e a configuração usadas. O parâmetro de contaminação controla quantas observações são sinalizadas; não é uma estimativa de fraude. Os casos precisam de auditoria documental.”

### 10. Por que usar grafo bipartido?

“Um grafo bipartido separa dois conjuntos de nós e conecta elementos de conjuntos distintos. Neste caso, os conjuntos são veículos e oficinas, e a aresta corresponde a um vínculo de serviço registrado. Isso permite analisar a estrutura dos vínculos e identificar concentração ou grupos. O resultado orienta triagem; não demonstra causalidade ou ilícito.”

### 11. O que significa modularidade Q = 0,5646?

“É uma medida de qualidade relativa de uma partição da rede: compara a concentração de ligações dentro das comunidades com a esperada sob uma rede de referência. O valor não é uma porcentagem de certeza e depende da rede e do método.”

### 12. Os hubs indicam monopólio ou conluio?

“Não, não por si só. Centralidade indica posição na rede. Pode haver explicações legítimas, como geografia, especialização ou credenciamento. É uma indicação de onde investigar, não uma conclusão.”

### 13. Por que SHAP e LIME discordaram?

“Eles respondem a perguntas próximas, mas usam construções diferentes. SHAP distribui contribuição segundo coalizões e um baseline; LIME aproxima localmente o modelo em uma vizinhança amostrada. A discordância pode refletir essas escolhas, o modelo e a instância. Nosso resultado indica que não devemos assumir intercambialidade.”

### 14. Então qual método de explicabilidade é correto?

“Não existe uma resposta universal. Depende do objetivo, da população, das propriedades desejadas e da estabilidade. O estudo recomenda comparação e triangulação, em vez de selecionar um método como verdade automática.”

### 15. O `R² = 0,748` do slide original é o resultado da regressão?

**Resposta na versão revisada:** esse valor foi retirado porque não corresponde ao resultado principal do capítulo 6. “O capítulo de regressão reporta MAE de R$ 2.236,06, RMSE de R$ 3.780,20 e R² ajustado de 0,1139 no protocolo correspondente.”

Se a banca perguntar antes da correção, reconheça a divergência em vez de tentar justificá-la sem evidência.

### 16. O que é um MILP?

“É um problema de otimização com função objetivo e restrições lineares, no qual pelo menos algumas decisões são inteiras. Neste caso, a decisão de intervir é representada por variável binária. Isso permite escolher combinações sob limites de orçamento, capacidade e obrigações.”

### 17. O que significa ótimo global?

“Significa que o solver provou que, para os dados, parâmetros, função objetivo e restrições codificados, nenhuma outra solução viável do modelo tem objetivo melhor dentro da tolerância reportada. Não significa que a formulação represente perfeitamente o mundo real.”

### 18. O gap de 0,0000% é o mesmo que o gap LP–MIP de 0,00063%?

“Não. O primeiro é o gap do solver entre o incumbente inteiro e o limite global durante a busca. O segundo compara a solução inteira com a relaxação linear que permite valores fracionários. São comparações diferentes.”

### 19. Os R$ 6,99 milhões foram economizados?

“Não há evidência de que esse valor tenha sido efetivamente economizado. Os R$ 6,99 milhões representam uma diferença estimada entre custos modelados no cenário contrafactual para a frota e o horizonte simulados. Um eventual efeito real dependeria da execução do plano, orçamento, capacidade operacional e desempenho em condições reais.”

### 20. Por que o otimizador escolheu uma solução com disponibilidade de 95,26%?

“Esse é o valor reportado como saída média do cenário S0. Preciso distinguir esse resultado de um piso formal: a formulação publicada no capítulo descreve orçamento, capacidade e manutenções mandatórias; não devo dizer que 95,26% foi uma restrição mínima sem confirmar que isso está codificado na instância executada.”

### 21. Como interpretar os R$ 40 milhões de Monte Carlo?

“É uma projeção de cenários com perturbações probabilísticas, condicionada às distribuições, amplitudes e parâmetros definidos. Não é uma economia garantida nem realizada. Também há diferença entre valores apresentados no texto; usaria a projeção apenas depois de reconciliar o relatório oficial.”

### 22. O critério de 40% obriga a vender o veículo?

“Não posso afirmar isso só com o indicador. Ele é usado para sinalizar possível antieconomicidade e apoiar uma avaliação. A alienação exige confirmar o valor de referência, a norma aplicável, laudo e deliberação administrativa.”

### 23. O SHA-256 garante que os dados são verdadeiros?

“Não. Ele ajuda a verificar se o conteúdo corresponde a uma referência previamente armazenada. Não atesta a veracidade da origem, a identidade do autor ou a conformidade legal do tratamento.”

### 24. O que seria necessário antes de implantar o sistema?

“Piloto prospectivo, revisão das regras de negócio com gestores, validação das definições de custo e risco, proteção e governança dos dados, monitoramento de calibração e desempenho, registro de exceções e comparação com a política atual.”

### 25. Qual é a principal limitação?

“A principal é a distância entre resultado simulado e impacto operacional observado. Também há dependência da qualidade e da compatibilidade dos registros e necessidade de validação externa em outros órgãos e períodos.”

---

## 6. Um jeito seguro de responder quando não souber

1. **Delimite:** “No protocolo avaliado, o resultado foi…”
2. **Diferencie:** “Isso é associação/predição/simulação, não prova causal/economia realizada.”
3. **Reconheça a condição:** “Esse resultado depende das premissas e do conjunto de dados usados.”
4. **Indique como verificaria:** “Eu confirmaria no artefato de execução/tabela oficial antes de generalizar.”

Uma resposta honesta e bem delimitada demonstra domínio científico. Não improvise uma explicação para valores inconsistentes entre slides e dissertação.

---

## 7. Checklist de preparação

### Antes da apresentação

- [ ] Confirmar que a versão revisada apresenta MAE de R$ 2.236,06, RMSE de R$ 3.780,20 e R² ajustado de 0,1139 no slide de regressão.
- [ ] Confirmar se o parâmetro Weibull correto é `β = 1,42` ou `k = 1,458`.
- [ ] Conferir no slide 10 a distinção entre disponibilidade observada no cenário e restrição formal do MILP.
- [ ] Diferenciar a projeção nominal de R$ 40,088 milhões da análise Monte Carlo de aproximadamente R$ 40,19 milhões; citar cada uma apenas com protocolo e premissas.
- [ ] Confirmar que a versão revisada evita “LIME falha”, “SHAP garante devido processo” e “imutabilidade absoluta”.
- [ ] Conferir se o critério patrimonial usa FIPE, valor venal ou valor venal contábil e identificar a norma aplicável.
- [ ] Treinar a distinção entre 77.867 OS, 350.737 itens, veículos e abastecimentos.
- [ ] Preparar uma explicação de 30 segundos sobre o contraste com De Castro e Cavalca (2006), Bertsimas e Kallus (2020) e Crespo del Castillo e Parlikad (2024).
- [ ] Explicar que grafos foram escolhidos por causa da estrutura relacional veículo–oficina, e não porque o TCU imponha essa técnica.
- [ ] Distinguir os estudos acadêmicos do ISC/TCU sobre grafos e compras/auditoria de uma aplicação operacional ou normativa em manutenção de frotas.
- [ ] Não dizer que os Acórdãos 2.493/2024 e 2.591/2024 validaram IA preditiva de manutenção veicular; tratam de contextos distintos.
- [ ] Apresentar o Portal IA no TCU como exemplo de governança institucional do próprio órgão, não como norma geral automática.
- [ ] Deixar claro que SHAP, LIME, Louvain, CRISP-DM e MILP são métodos existentes, não invenções desta pesquisa.
- [ ] Evitar “primeiro”, “inédito” ou “a literatura não aborda” sem revisão comparativa sistemática que sustente a afirmação.
- [ ] Memorizar os limites da simulação S0: 2.000 veículos, 36 meses, premissas de custo/risco/capacidade.
- [ ] Explicar, sem fórmulas, o que representam a variável binária, o custo preventivo, o risco residual e as restrições.
- [ ] Confirmar duração da fala, formato e orientações com a organização e com a orientação.

### Durante a apresentação

- [ ] Explique a pergunta e a contribuição antes de apresentar métricas.
- [ ] Defina siglas na primeira vez: OS, MILP, PR-AUC, SHAP, LIME.
- [ ] Apresente números sempre junto de cenário, unidade e período.
- [ ] Use “estima”, “simula”, “sinaliza” e “apoia” onde for adequado.
- [ ] Evite “prova fraude”, “garante legalidade”, “economia direta realizada” e “ótimo do mundo real”.
- [ ] Termine com limitações e próximo passo: validação prospectiva com gestores.

---

## 8. Referências internas para revisão

- [Apresentação revisada para o 36º SIC — versão atual, 16 slides](./Apresentacao_36_SIC_UDESC_com_bibliografia.pptx).
- [PDF da apresentação revisada para o 36º SIC](./Apresentacao_36_SIC_UDESC_com_bibliografia.pdf).
- [Versão anterior com contraste bibliográfico e análise do TCU](./Apresentacao_34_SIC_UDESC_com_TCU.pptx).
- [Apresentação revisada com contraste bibliográfico](./Apresentacao_34_SIC_UDESC_com_bibliografia.pptx).
- [Apresentação revisada anterior](./Apresentacao_34_SIC_UDESC_corrigida.pptx).
- [Apresentação original preservada](./Apresentacao_34_SIC_UDESC.pptx).
- [Dissertação](../dissertacao.pdf): metodologia e base empírica, cap. 3, pp. 28–45; detecção de anomalias, cap. 4, pp. 46–50; classificação, cap. 5, pp. 51–54; regressão, cap. 6, pp. 55–59; séries temporais, cap. 7, pp. 60–63; XAI, cap. 8, pp. 64–65; MILP e Monte Carlo, cap. 9, pp. 66–72; grafos, cap. 10, pp. 73–76; conclusões, cap. 13, pp. 116–118.
- [Garcia (2019), estudo do ISC/TCU sobre Data Analytics e Neo4j em auditoria](https://sites.tcu.gov.br/recursos/trabalhos-pos-graduacao/pdfs/O%20uso%20de%20ferramentas%20de%20Data%20Analytics%20pelo%20Auditor%20Governamental.pdf).
- [Soares (2020), estudo do ISC/TCU sobre padrões topológicos em vínculos da CGU e compras públicas](https://sites.tcu.gov.br/recursos/trabalhos-pos-graduacao/pdfs/Identifica%C3%A7%C3%A3o%20de%20ind%C3%ADcios%20de%20irregularidade%20por%20meio%20de%20padr%C3%B5es%20topol%C3%B3gicos%20em%20grafos_%20aplica%C3%A7%C3%A3o.pdf).
- [Portal IA no TCU](https://ia.tcu.gov.br/): transparência e salvaguardas descritas para iniciativas do próprio Tribunal.
- [Análise secundária dos Acórdãos 2.493/2024 e 2.591/2024](https://zenite.blog.br/tcu-valida-o-uso-da-inteligencia-artificial-ia-na-gestao-e-fiscalizacao-em-diversos-setores-dos-orgaos-publicos/): usada apenas para identificar os contextos distintos citados; não é evidência de validação de IA preditiva para frotas.
- [Resolução do Seminário de Inovação em Computação](./Resolu__o_036_2021_Semin_rio_de_Inova__o_em_Computa__o_16200596831296_5837.pdf): estabelece até 20 minutos para a apresentação, seguidos de discussão.

---

## 9. Aprofundamento metodológico para estudo

Esta seção é para preparar respostas além do que cabe nos slides. A meta não é decorar definições: é conseguir explicar **por que o método foi usado, o que recebe, o que produz, quais são as hipóteses e o que ele não permite concluir**.

### 9.1 Desenho do estudo e unidades de análise

O trabalho é uma investigação empírica retrospectiva com dados administrativos, seguida por experimentos computacionais e simulações de decisão. A base principal tem várias unidades:

| Unidade | O que representa | Uso típico |
|---|---|---|
| Item de manutenção | Peça ou serviço registrado em uma OS | Descrever composição e custo detalhado |
| Ordem de serviço (OS) | Solicitação/registro de manutenção agregado | Auditoria, classificação e análise de custo |
| Veículo | Bem patrimonial ao qual histórico e atributos podem ser associados | Painel longitudinal e análise de risco |
| Abastecimento | Transação de combustível | Análise de consumo, preço e atipicidade |
| Mês-veículo | Observação de um veículo em um período | Modelagem longitudinal e planejamento |

Uma resposta metodológica deve nomear a unidade da métrica. Por exemplo, “662 OS” não significa “662 veículos”, e “350.737 itens” não significa “350.737 eventos independentes”. O agrupamento e a dependência entre observações importam para intervalos de confiança e testes estatísticos.

#### Perguntas que precisam de resposta precisa

- Qual é a unidade do alvo de classificação: OS, veículo-mês ou outra?
- Como se define uma manutenção corretiva positiva?
- Qual é o horizonte temporal exato de `t+1`?
- Quais variáveis estavam disponíveis no momento de prever?
- Como OS canceladas, reprovadas, glosadas ou sem custo foram tratadas?
- Como foram conciliados identificadores de veículo entre manutenção, patrimônio e combustível?

Esses detalhes devem ser respondidos consultando o script e o relatório de execução correspondentes; não devem ser inferidos só do slide.

### 9.2 Baselines e comparação justa

Um baseline é uma política ou modelo simples usado como referência. Ele responde: “O método complexo acrescenta valor em relação a quê?”

Para a classificação, o baseline ingênuo pode refletir a prevalência da classe. Para regressão, a mediana histórica é relevante porque minimiza a soma dos erros absolutos. Para decisão, políticas históricas ou regras simples ajudam a comparar o MILP.

Uma comparação só é justa se mantém constantes:

- universo de teste;
- definição da variável-alvo;
- horizonte de previsão;
- atributos disponíveis;
- função de custo;
- restrições e regras mandatórias;
- período de referência.

Se um modelo é avaliado em uma janela diferente de outro, uma diferença de métrica pode refletir o período e não o algoritmo. Explique qual protocolo sustenta cada número e evite combinar média de validação cruzada com resultado de um único teste retido.

### 9.3 Fórmulas das principais métricas

Considere verdadeiro positivo (VP), falso positivo (FP), verdadeiro negativo (VN) e falso negativo (FN).

#### Classificação

- **Precisão:** `VP / (VP + FP)`. Dos casos sinalizados como positivos, quantos eram positivos?
- **Revocação/recall:** `VP / (VP + FN)`. Dos positivos reais, quantos foram encontrados?
- **F1:** `2 × precisão × recall / (precisão + recall)`. Resume precisão e recall num limiar escolhido, mas oculta o trade-off.
- **ROC-AUC:** área sob a curva de taxa de verdadeiros positivos contra taxa de falsos positivos ao variar o limiar.
- **PR-AUC:** área sob precisão contra revocação ao variar o limiar. A linha de base depende da prevalência de positivos.

Uma boa AUC não escolhe o limiar operacional. O limiar deve levar em conta a capacidade de oficina, custo de inspeções, custo de falhas perdidas e custo de alarmes desnecessários.

#### Regressão

Com observado `y_i`, previsto `ŷ_i` e `n` observações:

- `MAE = (1/n) Σ |y_i − ŷ_i|`.
- `RMSE = sqrt[(1/n) Σ (y_i − ŷ_i)²]`.
- `R² = 1 − Σ(y_i − ŷ_i)² / Σ(y_i − ȳ)²`.

O MAE é interpretável na unidade monetária. O RMSE penaliza mais erros grandes. R² depende da variabilidade do conjunto de teste e pode ser negativo se o modelo errar mais que o baseline de média. **R² não é percentual de acerto**.

#### Calibração

- `Brier = (1/n) Σ (p_i − y_i)²`, com `y_i ∈ {0,1}`.
- Uma forma comum de ECE agrupa observações em faixas e calcula a média ponderada da diferença entre probabilidade média e frequência observada em cada faixa.

Brier combina aspectos de calibração e discriminação e depende da prevalência. ECE depende do número e dos limites dos grupos. Por isso, não descreva nenhum deles como uma verdade completa sobre o modelo.

#### Concordância de listas e rankings

- `Jaccard(A,B) = |A∩B| / |A∪B|`: concordância de conjuntos.
- `Spearman ρ`: concordância da ordenação dos postos, não da magnitude das importâncias.

Se o Jaccard Top-5 for 0,3929, a leitura é “há sobreposição limitada entre os conjuntos de cinco variáveis nas condições comparadas”. Não significa que 45,48% das explicações estão certas.

### 9.4 Calibração: o que dizer com rigor

Imagine dez veículos com risco previsto de 0,8. Se o modelo é bem calibrado nesse grupo, em média cerca de oito devem apresentar o evento definido, na população e período avaliados. Isso não significa que o modelo sabe com certeza qual veículo específico falhará.

A regressão isotônica ordena os escores e encontra uma transformação monotônica para aproximá-los às frequências observadas. Para evitar otimismo:

1. treinar o classificador no conjunto de treino;
2. ajustar o calibrador em dados de calibração independentes ou dentro da validação;
3. avaliar calibração no teste retido sem reutilizá-lo para ajuste;
4. verificar se a distribuição do teste é representativa.

Se a calibração foi treinada/avaliada no mesmo conjunto ou se o teste teve inspeção repetida durante desenvolvimento, isso deve ser explicitado como limitação. A banca pode perguntar especificamente se o procedimento de calibração respeitou a separação temporal.

### 9.5 Testes estatísticos presentes no trabalho

Um p-valor pequeno não mede a importância prática de um resultado, nem a probabilidade de a hipótese ser verdadeira. Ele é interpretado dentro de um teste e de suas premissas.

- **Mann–Whitney U:** compara posições/distribuições de dois grupos independentes; não é simplesmente “teste de diferença entre médias”.
- **Kruskal–Wallis:** compara grupos independentes em extensão ao caso de dois grupos.
- **Wilcoxon signed-rank:** compara diferenças pareadas, por exemplo, erros de dois modelos nas mesmas observações.
- **Correção de Holm:** ajusta p-valores quando há comparações múltiplas, controlando o erro familiar de forma sequencial.
- **DeLong:** compara AUCs ROC correlacionadas, como dois modelos testados nos mesmos casos.
- **Bootstrap BCa:** reamostra observações para estimar intervalos de confiança, corrigindo viés e assimetria conforme o método BCa.
- **Teste t:** compara médias sob pressupostos sobre a distribuição das diferenças; a interpretação depende da independência e da forma do desenho.

**Resposta pronta:** “O teste estatístico ajuda a avaliar se a diferença observada é compatível com variação amostral sob a hipótese nula. A magnitude e a utilidade operacional são questões separadas, avaliadas por tamanho de efeito, intervalos e critérios definidos.”

### 9.6 Isolation Forest: leitura detalhada do resultado

O Isolation Forest cria árvores aleatórias que particionam o espaço de atributos. Observações isoladas após poucas divisões recebem score mais anômalo. O método é especialmente útil para triagem quando não há rótulo completo e confiável.

Dois cuidados:

1. **Contaminação `ν`:** define a fração esperada/sinalizada segundo a configuração. `ν = 0,85%` não quer dizer que 0,85% das OS são irregulares.
2. **Escala e qualidade dos atributos:** custo, duração, idade e hodômetro têm unidades e distribuições diferentes. Verifique o pré-processamento utilizado e se valores extremos refletem erros de registro ou eventos legítimos.

A comparação com reprovações/glosas é uma validação externa parcial: se registros reprovados aparecem mais na cauda anômala, isso sugere alinhamento entre sinal e auditoria existente. Ainda assim, não permite calcular automaticamente sensibilidade e especificidade jurídicas se os rótulos são incompletos ou enviesados.

O Jaccard entre sementes avalia se o conjunto de casos sinalizados muda muito ao alterar a aleatoriedade. Um modelo pode ser estável e estar errado; estabilidade é propriedade necessária para confiança operacional, mas não suficiente.

### 9.7 Redes: perguntas que ajudam a interpretar o gráfico

Antes de narrar um grafo, esclareça:

1. O que cada nó representa?
2. O que significa uma aresta?
3. A aresta é direcionada ou não?
4. É ponderada? Qual é o peso?
5. Qual é a janela temporal?
6. Que filtros foram aplicados?
7. Qual algoritmo gerou as comunidades e com quais parâmetros?

No grafo bipartido veículo–oficina, não se deve criar arestas veículo–veículo ou oficina–oficina na rede original sem especificar uma projeção. Ao projetar a rede, pode surgir uma ligação entre dois veículos que passaram pela mesma oficina, mas essa ligação é derivada e pode criar viés por oficinas de grande volume.

Modularidade é uma medida relativa à estrutura e ao modelo nulo utilizado. Louvain é heurístico: pode encontrar partições diferentes em execuções distintas e tem limitações conhecidas em redes de tamanhos/desigualdades diferentes. Portanto, “18 comunidades” é resultado da rede e configuração adotadas, não uma divisão natural e única do Estado.

Centralidade de intermediação é estrutural: um nó pode estar em muitos caminhos mínimos. Não significa que a entidade tenha autoridade, culpa, exclusividade legal ou intenção de coordenar outras.

### 9.8 XAI: explicação, causalidade e limites

Há três níveis que não devem ser confundidos:

1. **Descrição:** quais variáveis o modelo utiliza ou considera importantes?
2. **Explicação preditiva:** como a alteração de atributos participa da previsão deste modelo e deste caso?
3. **Causalidade:** o que mudaria no resultado se uma variável fosse intervinda, mantendo outras condições adequadas?

SHAP e LIME pertencem principalmente ao segundo nível. Para afirmar causalidade, seriam necessários desenho causal, identificação de confundidores, pressupostos causais e, idealmente, evidência de intervenção. Um gráfico SHAP não mostra que aumentar quilometragem causará mecanicamente a falha; mostra como o modelo associa esse atributo com sua previsão nos dados analisados.

Um SHAP beeswarm geralmente mostra:

- eixo vertical: atributos ordenados por importância global;
- cada ponto: uma observação;
- posição horizontal: contribuição SHAP positiva ou negativa na saída do modelo;
- cor: valor do atributo, frequentemente baixo/alto.

O valor SHAP deve ser interpretado na escala da saída do modelo (por exemplo, margem/log-odds ou saída transformada) e depende do explainer. Verifique no gráfico se a escala é probabilidade, log-odds ou custo.

Para defender uma explicação, pergunte:

- Qual foi o valor de referência?
- Qual explainer e background dataset foram usados?
- As explicações são estáveis a reamostragem?
- Como a correlação entre atributos foi tratada?
- A explicação local vale só para a observação ou foi agregada como importância global?
- Houve teste com usuários/gestores para saber se a explicação é compreensível?

### 9.9 Weibull e sobrevivência: interpretação sem exagero

A função de sobrevivência de Weibull pode ser escrita como:

`S(t) = exp[−(t/λ)^k]`

onde `λ > 0` é parâmetro de escala e `k > 0` é parâmetro de forma. A taxa instantânea de falha é:

`h(t) = (k/λ)(t/λ)^(k−1)`.

Assim, `k > 1` faz a função de risco crescer com o tempo dentro dessa distribuição. Isso é compatível com desgaste crescente, mas a conclusão depende da variável de tempo, da forma de censura, da qualidade dos eventos e do ajuste. `k > 1` não demonstra que idade é a única causa nem exclui uso severo, tipo de veículo ou qualidade da manutenção.

**Censura à direita:** o veículo não teve evento observado até o fim do período; sabemos apenas que sobreviveu até ali. Esses veículos contribuem para a análise até o último momento em que foram observados.

### 9.10 Formulação do MILP e responsabilidade sobre parâmetros

Uma notação pedagógica é:

`x_it ∈ {0,1}`: executar intervenção no veículo `i` no período `t`;

`p_it`: probabilidade calibrada de falha;

`C^corr_it`: custo esperado de uma corretiva/emergência;

`r_it = p_it × C^corr_it`: risco financeiro residual simplificado;

`c_it`: custo da intervenção preventiva;

`B_t`: limite de orçamento; `H_t`: capacidade; `m_it`: obrigação mandatória.

Então, em forma simplificada:

`min Σ_it [c_it x_it + r_it(1 − x_it)]`

sujeito a:

`Σ_i c_it x_it ≤ B_t`

`Σ_i h_it x_it ≤ H_t`

`x_it ≥ m_it`

`x_it ∈ {0,1}`.

A interpretação do objetivo é um trade-off parametrizado: se intervém, paga o custo preventivo; se não intervém, assume o risco residual modelado. Há vários pontos de auditoria:

- A probabilidade `p_it` é calibrada na população relevante?
- `C^corr_it` representa custo de peça, mão de obra, guincho, indisponibilidade ou uma combinação?
- Existe risco de contar o mesmo custo duas vezes?
- `B_t` e `H_t` são dados observados, parâmetros agregados ou cenários?
- As obrigações mandatórias estão codificadas, ou apenas comparadas depois?
- Como se modela que uma preventiva reduz a probabilidade de falha?
- A disponibilidade é calculada a partir de horas observadas ou aproximada?

Essas perguntas não invalidam o MILP; revelam que a validade da recomendação depende de como os coeficientes representam o problema real.

#### Por que a posição do termo de risco importa?

Se o objetivo é reduzir custos, a penalidade por falha deve estar associada à não intervenção, isto é, a `(1 − x_it)`. Se fosse associada a `x_it`, o modelo poderia interpretar que intervir aumenta o custo de falha e escolher a inação. A dissertação registra a correção dessa formulação. Uma banca pode perguntar como foi verificado que a codificação e o sinal dos termos estavam corretos.

#### Ótimo versus decisão recomendável

O solver encontra uma solução ótima **para o modelo**. O gestor ainda pode não recomendá-la se:

- os dados estão desatualizados;
- um veículo tem criticidade não representada;
- uma oficina não tem capacidade específica;
- há restrição logística ou de segurança não codificada;
- uma premissa de custo ou risco não se aplica ao caso;
- os requisitos legais mudaram.

O sistema deve permitir registrar exceções justificadas, em vez de tratar o ótimo matemático como ordem automática.

### 9.11 Sensibilidade, preço-sombra e cenários

Análise de sensibilidade varia parâmetros e observa a mudança na solução. Isso ajuda a responder “o que acontece se o orçamento cair?” ou “quando a capacidade se torna limitante?”

Em programação linear contínua, preço-sombra pode estimar a variação local do objetivo para um pequeno aumento de um recurso, dentro de uma faixa em que a base ótima não muda. Em MILP, a solução inteira pode mudar em saltos; os preços-sombra da relaxação linear são indicadores e **não necessariamente efeitos marginais exatos do problema inteiro**.

Uma conclusão como “orçamento é o gargalo” vale para os parâmetros agregados de S0. Não demonstra que nenhuma oficina real tenha fila, especialidade escassa ou restrição geográfica.

### 9.12 Auditoria do resultado financeiro

Para explicar a diferença estimada de R$ 9,302 milhões entre os custos modelados, apresente a subtração e a referência:

`R$ 51.180.733,62 (BL0) − R$ 44.190.120,51 (MILP-1) = R$ 6.990.613,11`.

`R$ 6.990.613,11 / R$ 51.180.733,62 ≈ 13,66%`.

Em seguida, diga que a análise considera uma frota representativa de 2.000 veículos, horizonte de 36 meses e parâmetros do cenário S0. Isso é mais rigoroso do que falar “o Estado economizará 13,66%”. Uma formulação adequada é “sob as premissas do cenário, o modelo estima potencial de redução de custos de 13,66%”.

O valor de R$ 4,881 milhões compara os custos de duas políticas de otimização sob as mesmas premissas do cenário reportado:

`R$ 48.719.011,68 (MILP-0) − R$ 44.190.120,51 (MILP-1) = R$ 4.881.378,37`.

É uma diferença de custo **entre políticas no modelo e na simulação**. Não isola causalmente o efeito do ML nem demonstra que a mesma diferença ocorreria em operação real.

### 9.13 Hipóteses centrais e como apresentá-las

| Hipótese | Resultado na dissertação | Fala equilibrada |
|---|---|---|
| H1 — integração multimodal melhora a predição em magnitude útil | Ganho estatístico, mas magnitude abaixo do critério prático definido; não sustentada pelo critério de relevância | “Detectamos ganho, mas ele foi pequeno frente ao limiar prático adotado; a integração precisa justificar seus custos.” |
| H2 — modelos não lineares superam alternativas | Parcialmente sustentada; classificação e algumas métricas favorecem ensembles, mas baselines podem vencer em MAE | “Superioridade depende da tarefa e da métrica; não é uma vitória universal de um algoritmo.” |
| H3 — MILP melhora a decisão sob restrições | Sustentada no cenário simulado S0 | “Há evidência computacional no cenário S0; falta validação prospectiva para demonstrar impacto operacional.” |
| H4 — SHAP e LIME concordam fortemente | Não sustentada: 45,48% Top-5 e `ρ = 0,2869` | “As explicações divergiram nas condições avaliadas; isso recomenda triangulação e cautela.” |

A banca tende a valorizar uma hipótese não sustentada quando a conclusão é assumida com clareza. Não esconda resultados negativos nem os apresente como se fossem confirmação.

---

## 10. Simulação de apresentação e postura diante da banca

### 10.1 Versão de 30 segundos

“Minha pesquisa combina auditoria de registros de frota, modelos preditivos, análise de grafos e otimização para apoiar a priorização de manutenção. Usei grafos porque a relação entre veículos e oficinas é central à análise. Estudos do ISC/TCU mostram paralelos metodológicos em auditoria pública, mas não tratam de manutenção de frotas nem validam este modelo. Na análise teórica do cenário S0, as premissas permitem estimar potencial de redução de custos de 13,66%. Esse valor não corresponde a economia realizada e precisaria de validação prospectiva.”

### 10.2 Versão de 2 minutos

1. **Problema:** dados de manutenção, patrimônio e abastecimento são fragmentados, enquanto disponibilidade e orçamento precisam ser conciliados.
2. **Proposta:** auditar dados, estimar risco/custo e usar MILP para escolher intervenções viáveis.
3. **Métodos:** validação temporal, modelos de classificação/regressão, calibração, anomalias, grafos, XAI e otimização. Os grafos foram escolhidos pela estrutura relacional veículo–oficina; os estudos do ISC/TCU citados são paralelos metodológicos de auditoria, não validação para frotas.
4. **Resultado:** a análise teórica do cenário S0 estima potencial de redução de custos de R$ 6,99 milhões/13,66% para 2.000 veículos por 36 meses; o cenário também reporta 95,26% de disponibilidade média e atendimento das obrigações codificadas.
5. **Limite:** são resultados de simulação baseados em premissas, não impacto observado nem economia realizada.
6. **Próximo passo:** piloto prospectivo, monitoramento e avaliação externa.

### 10.3 Ritmo possível para 20 minutos

| Bloco | Slides | Tempo |
|---|---:|---:|
| Abertura | 1 | 0,5 min |
| Cap. 1 — Introdução | 2 | 1,5 min |
| Cap. 2 — Conceitos fundamentais | 3 | 1 min |
| Cap. 3 — Revisão de literatura | 4–5 | 1,5 min |
| Cap. 4 — Proposta | 6–7 | 2 min |
| Cap. 5 — Validação | 8–13 | 7 min |
| Caps. 6–7 — Discussões e conclusão | 14 | 2 min |
| Referências e agradecimentos | 15–16 | 1 min |

O plano soma aproximadamente 18 minutos, deixando margem para pausas e transições. As perguntas e a discussão vêm depois do tempo de apresentação previsto na resolução.

### 10.4 Como responder sem se perder

- **Responda primeiro em uma frase.** Só depois desenvolva.
- **Cite o protocolo.** “No teste retido…” ou “na validação temporal em cinco dobras…”
- **Nomeie a unidade.** “Por OS”, “por veículo-mês”, “na simulação de 36 meses”.
- **Distinga significância de relevância prática.**
- **Admita limites e erros de slide.** Se uma cifra não puder ser rastreada, diga que ela está sendo corrigida.
- **Não especule sobre uma estatística.** Peça para conferir o artefato e explique o que seria necessário para responder.

Uma boa forma de responder a uma pergunta muito ampla é: “Posso responder por três ângulos: definição do método, resultado observado e limitação da interpretação.”

---

## 11. Perguntas adicionais para treino

### O que significa “multimodal” neste estudo?

“Refere-se à combinação de fontes administrativas diferentes, como manutenção, patrimônio e abastecimento. Não significa necessariamente sensores de telemetria em tempo real.”

### Qual é a diferença entre auditoria de dados e auditoria de modelo?

“Auditoria de dados verifica origem, unidade, consistência, transformações e vieses da base. Auditoria de modelo verifica objetivo, atributos, métricas, validação, calibração, estabilidade, explicações e comportamento da decisão.”

### Por que validar em mais de uma janela temporal?

“Uma única janela pode ser atípica. Múltiplas origens temporais mostram como o desempenho varia entre períodos. A média não elimina a necessidade de examinar a dispersão e os períodos em que o modelo piora.”

### Como lidar com o desbalanceamento de classes?

“Reportar prevalência, priorizar métricas coerentes como PR-AUC, estudar limiares e custos de erro, e não tomar acurácia isolada como evidência. Qualquer reamostragem deve ocorrer somente no conjunto de treino para não vazar informação.”

### Qual erro é mais grave: falso positivo ou falso negativo?

“Depende da decisão. Um falso negativo pode deixar uma falha relevante passar; um falso positivo pode ocupar orçamento e capacidade que seriam usados em outro veículo. A escolha de limiar deve refletir custos e regras operacionais validados com gestores.”

### Por que usar modelo não linear se o resultado de regressão ainda tem erro alto?

“Não linearidade é uma hipótese de modelagem, não promessa de erro baixo. O modelo deve ser comparado a baselines e avaliado por métricas apropriadas. Os resultados da dissertação indicam capacidade de reduzir alguns erros em relação aos concorrentes, mas não tornam cada previsão individual precisa.”

### A feature importance informa o que o gestor deve mudar?

“Não diretamente. Importância informa como atributos se relacionam com a previsão do modelo. Uma decisão de intervenção requer análise de causalidade, custo, viabilidade e evidências externas.”

### Se o MILP é ótimo, por que ainda fazer piloto?

“A prova de otimalidade é condicional ao modelo. O piloto testa se dados, custos, capacidade, comportamento operacional e premissas representam a realidade e se a execução produz o resultado esperado.”

### Como avaliar o piloto?

“Definir previamente população e período, grupo ou política de comparação, indicadores e critérios de segurança; registrar adesão e exceções; acompanhar custo, disponibilidade, falhas, tempo parado, manutenção mandatória e calibração; e avaliar diferenças sem atribuir causalidade além do desenho.”

### O que significa 100% de cumprimento obrigatório?

“No resultado S0, todas as intervenções marcadas como mandatórias pela formulação foram selecionadas. Isso não prova que o cadastro de obrigações é completo nem que toda exigência real foi representada no código.”

### Os 242 veículos já devem ser vendidos?

“Não. O resultado é triagem para exame patrimonial. É preciso confirmar estado, valor de referência, custo futuro de manter/substituir, norma aplicável, laudo e aprovação.”

### Como a LGPD se relaciona com o projeto?

“A análise deve limitar dados ao necessário, controlar acesso, definir finalidade e retenção e avaliar risco de reidentificação. A existência de dados agregados ou hashes não elimina obrigações de proteção. A conformidade precisa ser avaliada pela instituição responsável.”

---

## 12. Glossário rápido

| Termo | Explicação direta |
|---|---|
| Atributo/feature | Variável usada como entrada do modelo |
| Alvo/target | Resultado que o modelo tenta prever |
| Baseline | Referência simples para comparar o método |
| Calibração | Correspondência entre probabilidades previstas e frequências observadas |
| Censura | Evento de interesse não observado até o fim do acompanhamento |
| Contrafactual | Resultado alternativo estimado sob uma política diferente da observada |
| Data leakage | Uso indevido de informação que não estaria disponível no momento da previsão |
| Ensemble | Combinação de vários modelos-base |
| Glosa | Valor recusado/reduzido na auditoria ou medição segundo regras aplicáveis |
| MILP | Otimização linear com variáveis inteiras e, possivelmente, contínuas |
| Modelo preditivo | Estima resultado ou risco futuro a partir de padrões de dados |
| Modelo prescritivo | Seleciona ações segundo objetivo, restrições e parâmetros |
| MIP gap | Distância relativa entre solução viável inteira e limite do solver |
| Relaxação LP | Versão contínua do problema que permite valores fracionários às variáveis inteiras |
| Sazonalidade | Padrão recorrente ligado a um calendário |
| TCO | Custo total de propriedade ao longo do ciclo de vida; só inclui componentes modelados |
| Triangulação | Comparação de evidências ou métodos diferentes, sem supor que um único método seja infalível |
| Validação externa | Teste em contexto, população, órgão ou período diferente do desenvolvimento |
| XAI | Métodos para tornar aspectos das previsões mais interpretáveis |

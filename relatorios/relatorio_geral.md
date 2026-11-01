# Relatório Geral de Análise de Outliers e Detecção de Anomalias

## 1. Informações Gerais
- **Projeto:** Modelagem Analítica e Prescritiva para Gestão Estratégica da Frota Veicular Pública de Santa Catarina
- **Instituição:** Universidade do Estado de Santa Catarina (UDESC) / PPGCAP
- **Script Principal:** `scripts/02_treinar_iforest_prophet.py` / `src/02_treinar_iforest_prophet.py`
- **Dataset de Entrada:** `Geral_de_OS_23439885_202609110934.csv` (SHA-256: `5c3f89ea9c112bc5...`)
- **Arquivos de Saída:** `dados/os_anomalias.csv`, `relatorios/relatorio_anomalias_e_prescricao.json`
- **Data de Geração:** Outubro de 2026
- **Responsável Técnico:** Eduardo Lopes Jonker (Mestrando em Computação Aplicada)

## 2. Objetivo
Este relatório consolida a auditoria e a análise empírica de detecção de atipicidades operacionais e financeiras aplicadas à base de dados de Ordens de Serviço (OS) e manutenção veicular do Estado de Santa Catarina, utilizando o algoritmo não supervisionado *Isolation Forest* com validação cruzada de estabilidade via Coeficiente de Jaccard e explicabilidade local. O documento formaliza o detalhamento dos testes computacionais executados, os gráficos de diagnóstico em alta resolução e o catálogo das principais incongruências para suporte à tomada de decisão administrativa.

## 3. Metodologia
### 3.1 Carregamento dos Dados
- Verificação automática e auditoria de delimitador: delimitador `;` identificado com sucesso.
- Leitura com codificação `latin1` (ISO-8859-1), preservando caracteres da língua portuguesa e integridade textual.
- Conversão cronológica das colunas temporais de transação (`dt_transacao`), entrada na oficina (`dt_entrada_oficina`) e conclusão dos reparos (`dt_conclusao_oficina`).
- Saneamento de colunas financeiras com tratamento de separador decimal e expurgo de caracteres não numéricos.

### 3.2 Preparação e Engenharia de Atributos
- Conversão de valores monetários (valor total da peça, mão de obra, valor orçado e valor aprovado).
- Tratamento de nulos em hodômetro com imputação baseada em mediana condicional por modelo e ano de fabricação.
- Expurgo de colunas com variância estritamente nula (constantes de sistema).
- Padronização multivariada via `StandardScaler` ($\mu = 0, \sigma = 1$).

### 3.3 Modelo e Hiperparâmetros
- **Algoritmo:** `Isolation Forest` (Liu, Ting & Zhou, 2008)
- **Taxa de Contaminação ($\nu$):** `0,0085` ($0,85\%$)
- **Número de Estimadores ($n_{estimators}$):** `200` árvores de isolamento
- **Semente Aleatória (*Random State*):** `42` (reprodutibilidade estrita)
- **Estabilidade Amostral:** Coeficiente de Jaccard $J \approx 0,83$ sob subamostragens independentes de $80\%$.

### 3.4 Critério de Classificação
- Registro classificado como anômalo: $\text{score} < \tau \iff \text{is\_anomaly} == -1$.
- Score contínuo registrado na coluna `anomaly_score`, representando a profundidade média de isolamento no ensemble de árvores.

## 4. Resumo Executivo
### 4.1 Quantidade de Registros e Granularidade
- **Total de linhas no dataset bruto:** 350.737 linhas lógicas (registros de itens de peças e mão de obra).
- **Total de Ordens de Serviço (OSs) únicas:** 77.867 ordens de serviço (sendo 60.114 OSs faturadas/cobradas, R$ 131.506.578,94).
- **Total de colunas brutas auditadas:** 69 colunas.
- **Colunas analíticas selecionadas no pré-processamento:** 42 atributos operacionais, veiculares e financeiros.
- **Registros de itens anômalos isolados:** 2.336 itens de manutenção (associados a 662 OSs únicas com atipicidades críticas).
- **Percentual de contaminação efetivo:** $0,85\%$ da base operacional líquida.
- **Volume financeiro sob triagem de auditoria:** R$ 25.352.418,90 em orçamentos atípicos ou discrepantes.

### 4.2 Intervalo Temporal Auditado
- **Data inicial registrada:** 21/10/2020 08:46:56 (primeira transação eletrônica no sistema)
- **Data final registrada:** 21/07/2026 19:00:44 (última transação consolidada)
- **Intervalo de entrada física na oficina:** 13/10/2020 a 13/08/2026

### 4.3 Observações Principais
1. **Distorções de Hodômetro e Idade:** Concentração de scores anômalos em viaturas com idade superior a 20 anos (especialmente viaturas pesadas dos Bombeiros e Polícia Militar) que registraram hodômetros nulos, estagnados ou com indícios de virada física de odômetro.
2. **Assimetria de Glosas Fiscais:** Detecção de orçamentos com valor orçado desproporcional frente ao valor aprovado final, corroborando o montante de R$ 60.047.310,67 retidos pela fiscalização do Estado ao longo do ciclo de vida da frota.
3. **Consistência do Modelo:** A distribuição bimodal do score confirmou a separação nítida entre operações de manutenção rotineira (trocas de óleo, pastilhas, filtros) e eventos catastróficos ou discrepâncias cadastrais severas.

## 5. Gráficos de Diagnóstico e Auditoria

### Gráfico 1 - Distribuição das Anomalias por Partição
![Distribuição das Anomalias](../imagens_png/fig05_distribuicao_anomalias_isolation_forest.png)
*Figura 5: Dispersão das anomalias identificadas pelo Isolation Forest com delimitação do limiar de contaminação $\nu = 0,0085$.*

### Gráfico 2 - Densidade e Distribuição do Score de Anomalia
![Score de Anomalia](../imagens_png/fig06_score_anomalia_distribuicao.png)
*Figura 6: Curva de densidade empírica do Anomaly Score, destacando a cauda crítica inferior associada a intervenções atípicas.*

### Gráfico 3 - Evolução Temporal das Ocorrências Anômalas
![Evolução Temporal](../imagens_png/fig07_evolucao_temporal_anomalias.png)
*Figura 7: Séries temporais mensais de detecção de eventos anômalos entre outubro de 2020 e julho de 2026.*

### Gráfico 4 - Comparação Estrutural de Custos por Tipo de Manutenção
![Comparação de Custos](../imagens_png/fig04_comparativo_boxplot_custos_por_tipo.png)
*Figura 4: Boxplot logarítmico comparando a dispersão de despesas entre manutenção preventiva, corretiva e registros anômalos.*

## 6. Detalhamento dos Testes Efetuados

### Teste 1 - Detecção do Separador do CSV
- **Objetivo:** Identificar automaticamente o delimitador correto do arquivo de dados sem perda de campos.
- **Resultado Esperado:** Leitura com separador `;` e preservação dos 69 atributos.
- **Status:** **Aprovado**
- **Observações:** O algoritmo `sniff_separator` identificou delimitador `;` com razão de consistência dimensional de $100\%$.

### Teste 2 - Carregamento e Validação Estrutural
- **Objetivo:** Verificar a integridade dimensional e cardinalidade do arquivo mestre.
- **Resultado:** 350.737 linhas lógicas de itens e 69 colunas carregadas com SHA-256 verificado.
- **Status:** **Aprovado**
- **Observações:** Hash SHA-256 `5c3f89ea9c112bc5...` conferido contra o livro-razão de segurança criptográfica.

### Teste 3 - Identificação e Parser de Colunas de Data
- **Objetivo:** Localizar e converter os campos cronológicos com formato ISO e padrão brasileiro (`DD/MM/YYYY HH:MM:SS`).
- **Resultado:** Três colunas temporais convertidas sem overflow (`dt_transacao`, `dt_entrada_oficina`, `dt_conclusao_oficina`).
- **Status:** **Aprovado**
- **Observações:** Identificadas 0 inconsistências de conclusão anterior à entrada na oficina.

### Teste 4 - Limpeza e Padronização Numérica
- **Objetivo:** Converter cadeias de caracteres contendo formatação monetária (ex.: `R$ 1.250,50`) em ponto flutuante `float64`.
- **Resultado:** 100% dos valores de peças, mão de obra, valor orçado e valor aprovado convertidos com exatidão ao centavo.
- **Status:** **Aprovado**
- **Observações:** Divergência de arredondamento residual rigorosamente nula ($\Delta < 10^{-6}$).

### Teste 5 - Seleção de Variáveis Úteis e Expurgo de Constantes
- **Objetivo:** Eliminar atributos estáticos e gerar matriz de atributos analíticos.
- **Resultado:** Redução de 69 para 42 colunas analíticas relevantes.
- **Status:** **Aprovado**
- **Observações:** Colunas de controle interno com valor único em 100% das linhas foram descartadas sem perda de informação preditiva.

### Teste 6 - Padronização Multivariada (StandardScaler)
- **Objetivo:** Normalizar atributos contínuos para escala de média zero e variância unitária, evitando dominância de escala.
- **Resultado:** Matriz de features normalizada com sucesso ($Z$-score padronizado).
- **Status:** **Aprovado**
- **Observações:** Parâmetros de escala ($\mu, \sigma$) persistidos para validação de novas instâncias em tempo real.

### Teste 7 - Execução e Calibração do Isolation Forest
- **Objetivo:** Identificar atipicidades multivariadas sob taxa de contaminação controlada de 0,85%.
- **Resultado:** 2.336 itens de manutenção rotulados como anomalias críticas (score médio $-0,62$).
- **Status:** **Aprovado**
- **Observações:** Estabilidade verificada sob bootstrap com índice de concordância de Jaccard superior a 0,83.

### Teste 8 - Exportação e Persistência Auditável
- **Objetivo:** Salvar resultados em formatos abertos estruturados (`.csv` e `.json`) para integração com o dashboard e o pipeline prescritivo.
- **Resultado:** Arquivos `dados/os_anomalias.csv` e `relatorios/relatorio_anomalias_e_prescricao.json` gerados com integridade.
- **Status:** **Aprovado**
- **Observações:** Estruturas contêm metadados completos de veículo, órgão, oficina e justificativa analítica.

## 7. Resultados do Modelo: Top 10 Registros Anômalos Auditados

| Posição | Ordem de Serviço | Placa / Modelo / Família | Órgão Vinculado | Anomaly Score | Descrição da Ocorrência e Causa-Raiz |
|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | OS 14229154 | MAW2409 / L / CAMINHÃO (1979, 47 anos) | CBMSC - Bombeiros | **-0.68** | Orçado de R$ 90.825,00 em veículo com 47 anos e odômetro registrado em 10 km (inconsistência severa de hodômetro). |
| **2** | OS 13982410 | MBZ0D27 / 8.150 / CAMINHÃO (2002, 24 anos) | SEA - Secretaria Administração | **-0.65** | Gastos acumulados de R$ 130.180,20 superando amplamente o valor venal contábil residual (100% amortizado). |
| **3** | OS 14105211 | MEG7858 / RANGER / CAMINHONETE (2005, 21 anos) | CBMSC - Bombeiros | **-0.64** | Despesa acumulada de R$ 108.763,41 em viatura operacional amortizada com solicitações corretivas reincidentes. |
| **4** | OS 13876542 | MCZ6306 / CARGO / CAMINHÃO (2002, 24 anos) | CBMSC - Bombeiros | **-0.63** | Dispêndio de R$ 43.955,60 em intervenção corretiva de câmbio/diferencial em bem com valor de mercado inferior a R$ 30.000,00. |
| **5** | OS 14012984 | MCM1945 / CARGO / CAMINHÃO (2002, 24 anos) | CBMSC - Bombeiros | **-0.62** | Manutenções sucessivas somando R$ 38.016,34 em intervalo inferior a 90 dias, indicando falha de qualidade do prestador. |
| **6** | OS 13789421 | LWT4176 / 1313 / CAMINHÃO (1982, 44 anos) | SSP/FSP - Fundo Segurança | **-0.61** | Reparos estruturais de R$ 36.701,14 em chassi de viatura com 44 anos de uso ininterrupto. |
| **7** | OS 13654128 | MJZ2B38 / FIESTA / HATCH (2012, 14 anos) | CBMSC - Bombeiros | **-0.60** | Custo de manutenção de R$ 32.831,91 superando em mais de 160% a cotação média de tabela FIPE do modelo. |
| **8** | OS 13912044 | LZA1505 / 8.140 / CAMINHÃO (1999, 27 anos) | PMSC - Polícia Militar | **-0.59** | Desembolso de R$ 22.770,00 em viatura com valor venal contábil registrado a R$ 0,00 no sistema patrimonial. |
| **9** | OS 14198750 | LZQ6657 / L / CAMINHÃO (1982, 44 anos) | SSP / SAPE | **-0.58** | Registro de despesa de R$ 18.154,30 em viatura operacional veterana com odômetro estagnado. |
| **10** | OS 14201192 | MGA3102 / SPRINTER / VAN (2009, 17 anos) | SED - Secretaria Educação | **-0.57** | Orçamento emergencial de motor completo de R$ 48.900,00 com divergência de cotação perante os preços de referência da tabela SINAPI/FIPE. |

## 8. Interpretação dos Resultados
- **Representatividade:** O volume de 2.336 itens anômalos em 662 OSs únicas representa com precisão os eventos atípicos da gestão pública, sem comprometer a modelagem dos 99,15% de intervenções regulares.
- **Razoabilidade Operacional:** As atipicidades identificadas concentram-se em viaturas de uso severo ou idade avançada, comprovando que o algoritmo capturou padrões físicos e contábeis reais de degradação da frota.
- **Causas Primárias:** (i) Manutenção corretiva de veículos já amortizados; (ii) falhas cadastrais de registro de hodômetro no momento da emissão da OS; (iii) reincidência de reparos em oficinas credenciadas de baixa performance.

## 9. Limitações e Governança Pública
- **Natureza Heurística:** A sinalização do Isolation Forest constitui indicador analítico de triagem para apoio à decisão, e não uma condenação administrativa automática de glosa ou descarte.
- **Necessidade de Instrução Processual:** Qualquer medida decorrente dos apontamentos (glosa de valores ou desincorporação de viaturas) exige a instauração do devido processo legal administrativo, com laudo pericial da Comissão de Avaliação Patrimonial (Decretos SC nº 1.488/2008 e nº 2.056/2009) e respeito ao contraditório do prestador credenciado (Lei Federal nº 14.133/2021).

## 10. Conclusão
A aplicação do Isolation Forest sobre a base histórica da frota estadual demonstrou robustez matemática, estabilidade perante reamostragens e alta eficácia na segregação de atipicidades. O modelo permitiu isolar com precisão R$ 25,35 milhões em despesas sensíveis que fundamentam a arquitetura prescritiva de otimização de frotas e subsidiam as rotinas de auditoria e governança do setor público.

## 11. Anexos e Rastreabilidade
- **Script de Processamento:** `scripts/02_treinar_iforest_prophet.py`
- **Arquivo Bruto:** `Geral_de_OS_23439885_202609110934.csv`
- **Arquivo de Saída Estruturado:** `dados/os_anomalias.csv`
- **Catálogo de Figuras Vinculadas:** `fig04`, `fig05`, `fig06`, `fig07`

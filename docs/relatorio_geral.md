# Relatório Geral de Análise de Outliers

## 1. Informações gerais
- Projeto: Análise de Ordem de Serviço (OS)
- Script principal: `isolation_forest.py`
- Dataset de entrada: `Geral_de_OS_23439885_202609110934.csv`
- Arquivo de saída de anomalias: `os_anomalias.csv`
- Data de geração: preencher manualmente
- Responsável: preencher manualmente

## 2. Objetivo
Este relatório consolida a análise de detecção de anomalias aplicada ao conjunto de dados de Ordem de Serviço, utilizando o algoritmo Isolation Forest. O documento tem como finalidade apresentar os gráficos gerados, o resumo do processamento e o detalhamento dos testes executados.

## 3. Metodologia
### 3.1 Carregamento dos dados
- Verificação automática do separador do CSV (`;`, `,`, `\t`, `|`)
- Leitura do arquivo com codificação `latin1`
- Identificação da coluna de data, quando presente
- Padronização e limpeza das colunas numéricas

### 3.2 Preparação dos dados
- Conversão de valores monetários e numéricos para representação numérica
- Tratamento de valores vazios e não numéricos
- Remoção de colunas sem variabilidade
- Normalização via `StandardScaler`

### 3.3 Modelo aplicado
- Algoritmo: `Isolation Forest`
- Contaminação: `0.01`
- Número de estimadores: `200`
- Seed aleatória: `42`

### 3.4 Critério de classificação
- Registro classificado como anomalia: `is_anomaly == -1`
- Score de anomalia registrado em `anomaly_score`

## 4. Resumo executivo
### 4.1 Quantidade de registros
- Total de linhas no dataset: inserir valor
- Total de colunas: inserir valor
- Registros anômalos identificados: inserir valor
- Percentual de anomalias: inserir valor %

### 4.2 Intervalo temporal
- Data inicial: inserir valor
- Data final: inserir valor

### 4.3 Observações principais
- Descrever tendências observadas
- Relatar se os registros anômalos estão concentrados em determinados períodos ou tipos de ocorrência
- Comentar sobre a consistência da amostra e possíveis limitações do modelo

## 5. Gráficos
> Inserir as imagens geradas durante a análise no espaço abaixo.

### Gráfico 1 - Distribuição das anomalias
![Inserir gráfico 1](./grafico_1.png)

### Gráfico 2 - Score de anomalia por registro
![Inserir gráfico 2](./grafico_2.png)

### Gráfico 3 - Evolução temporal das ocorrências anômalas
![Inserir gráfico 3](./grafico_3.png)

### Gráfico 4 - Comparação entre registros normais e anômalos
![Inserir gráfico 4](./grafico_4.png)

## 6. Detalhamento dos testes efetuados

### Teste 1 - Detecção do separador do CSV
- Objetivo: identificar o delimitador correto do arquivo de entrada
- Resultado esperado: leitura correta do dataset
- Status: aprovado / reprovado
- Observações: inserir detalhes

### Teste 2 - Carregamento e validação do dataset
- Objetivo: verificar se o arquivo foi lido com sucesso
- Resultado: número de linhas e colunas carregadas
- Status: aprovado / reprovado
- Observações: inserir detalhes

### Teste 3 - Identificação da coluna de data
- Objetivo: localizar a coluna temporal relevante para análise
- Resultado: inserir nome da coluna identificada
- Status: aprovado / reprovado
- Observações: inserir detalhes

### Teste 4 - Limpeza e conversão numérica
- Objetivo: transformar valores inconsistentes em formato numérico válido
- Resultado: colunas limpas e convertidas
- Status: aprovado / reprovado
- Observações: inserir detalhes

### Teste 5 - Seleção de variáveis úteis
- Objetivo: remover colunas sem variabilidade e manter atributos relevantes
- Resultado: número de colunas finais utilizadas
- Status: aprovado / reprovado
- Observações: inserir detalhes

### Teste 6 - Padronização dos dados
- Objetivo: aplicar `StandardScaler` para que o modelo trabalhe em escala comparável
- Resultado: matriz escalada com sucesso
- Status: aprovado / reprovado
- Observações: inserir detalhes

### Teste 7 - Execução do Isolation Forest
- Objetivo: detectar registros atípicos no conjunto
- Resultado: número de anomalias identificadas
- Status: aprovado / reprovado
- Observações: inserir detalhes sobre contaminação e sensibilidade

### Teste 8 - Exportação dos resultados
- Objetivo: salvar os registros anômalos em arquivo CSV
- Resultado: arquivo `os_anomalias.csv` gerado com sucesso
- Status: aprovado / reprovado
- Observações: inserir detalhes

## 7. Resultados do modelo
### 7.1 Top 10 registros anômalos
| Posição | Registro | Score de anomalia | Observação |
|--------|----------|-------------------|------------|
| 1 | inserir | inserir | inserir |
| 2 | inserir | inserir | inserir |
| 3 | inserir | inserir | inserir |
| 4 | inserir | inserir | inserir |
| 5 | inserir | inserir | inserir |
| 6 | inserir | inserir | inserir |
| 7 | inserir | inserir | inserir |
| 8 | inserir | inserir | inserir |
| 9 | inserir | inserir | inserir |
| 10 | inserir | inserir | inserir |

## 8. Interpretação dos resultados
- Comentar se a quantidade de anomalias é representativa
- Verificar se as ocorrências fora do padrão fazem sentido no contexto operacional
- Discutir possíveis causas de comportamento atípico
- Sinalizar se há necessidade de refinamento do modelo ou ajustes de parâmetro

## 9. Limitações
- Dependência da qualidade dos dados de entrada
- Sensibilidade à configuração de contaminação
- Possibilidade de falsos positivos em registros com valores extremos, mas válidos
- Necessidade de validação com contexto de negócio para confirmar cada anomalia

## 10. Conclusão
Apresentar a conclusão geral da análise, destacando se o algoritmo conseguiu identificar anomalias relevantes, se os resultados foram consistentes e se a metodologia adotada é adequada para apoio à decisão.

## 11. Anexos
- Script de processamento: `isolation_forest.py`
- Arquivo de dados de entrada: `Geral_de_OS_23439885_202609110934.csv`
- Arquivo de saída: `os_anomalias.csv`
- Gráficos e imagens produzidas: inserir lista final

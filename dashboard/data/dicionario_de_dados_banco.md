# Dicionário de Dados do Banco Relacional da Dissertação

**Base de Dados:** `dados/resultados_dissertacao.db` (SQLite 3)  
**Projeto:** Framework de Decisão Pública Auditável (FDPA) para Gestão de Frotas  
**Programa:** Pós-Graduação em Computação Aplicada (PPGCAP), Universidade do Estado de Santa Catarina (UDESC)  
**Autor:** Eduardo Lopes Jonker  
**Orientação:** Vivian Kremer Kalempa | **Coorientação:** Yuri Kaszubowski Lopes  

---

## 1. Visão Geral do Banco de Dados

O banco de dados relacional `dados/resultados_dissertacao.db` centraliza todos os microdados administrativos, modelos de aprendizado de máquina, projeções prescritivas e auditorias contábeis desenvolvidas nesta dissertação de mestrado. Ele integra:

1. **Módulo de Abastecimentos de Combustíveis:** 1.000.000 de lançamentos detalhados (R$ 153.488.476,96 e 34.311.319 L) higienizados, anonimizados conforme a LGPD e auditados por modelos de *Isolation Forest* e decomposição temporal *Prophet*.
2. **Módulo de Manutenção Veicular:** 223.819 itens limpos de ordens de serviço contemplando peças, serviços mecânicos, glosas técnicas e tempos de imobilização (*downtime*).
3. **Módulo de Inteligência Artificial e Governança:** Experimentos de acurácia, calibração (*Brier Score*, ECE), métricas de redes complexas bipartidas (*Louvain Modularity*), catálogo de 101 figuras e veículos antieconômicos elegíveis a leilão público (Decreto Estadual nº 47.539/2018).

### Sumário das Tabelas Catalogadas

| Tabela | Finalidade Semântica | Volume de Dados | Origem Primária |
| :--- | :--- | :---: | :--- |
| [`abastecimentos`](#tabela-abastecimentos) | Microdados transacionais exaustivos de 1.000.000 de abastecimentos de combustível da frota pública de Santa Catarina (2019-2022). | 1.000.000 registros | 2161_abastecimentos_pg0001.xlsb (Higienizado e Anonimizado) |
| [`abastecimentos_ano`](#tabela-abastecimentos-ano) | Estatísticas anuais consolidadas de consumo e dispêndio de combustível. | 4 registros (2019 a 2022) | Agregação da tabela abastecimentos |
| [`abastecimentos_categoria`](#tabela-abastecimentos-categoria) | Distribuição agregada de despesas e volume de combustível por categoria veicular. | 8 registros | Agregação da tabela abastecimentos por tipo_veiculo |
| [`abastecimentos_secretaria`](#tabela-abastecimentos-secretaria) | Consolidação dos gastos e volumes de combustíveis por Secretaria de Estado e Órgão setorial. | 10 registros | Agregação da tabela abastecimentos por secretaria gestora |
| [`abastecimentos_projecao_prophet`](#tabela-abastecimentos-projecao-prophet) | Projeções preditivas mensais de gastos de combustível obtidas pelo modelo Facebook Prophet. | 25 registros (competências futuras até 2025) | Modelo Prophet treinado sobre a série temporal de abastecimentos (2019-2022) |
| [`manutencao_itens`](#tabela-manutencao-itens) | Microdados de itens de peças e mão de obra de ordens de serviço de manutenção mecânica da frota estadual. | 223.819 registros | os_dataset_limpo.csv (Base higienizada para modelagem e auditoria) |
| [`kpis_gerenciais`](#tabela-kpis-gerenciais) | Indicadores de Governança e Gestão de Frota e Informação (GFI) catalogados e monitorados. | 38 registros | indicadores_gfi_consolidados.json |
| [`experimentos_modelos`](#tabela-experimentos-modelos) | Resultados de acurácia, calibração e tempo computacional dos modelos preditivos de ML avaliados. | 28 registros | Pipeline de treinamento e validação walk-forward (scripts/treinar_*.py) |
| [`veiculos_leilao`](#tabela-veiculos-leilao) | Veículos antieconômicos identificados para desincorporação e leilão com fulcro no Decreto Estadual nº 47.539/2018. | 30 registros (Amostra dos 313 veículos auditados) | relatorio_gerencial_frotas_sc.json (Critério: custo acumulado > 40% do valor venal FIPE) |
| [`auditoria_orgaos`](#tabela-auditoria-orgaos) | Estatísticas de fiscalização, gastos autorizados e valores glosados por órgão do Governo de Santa Catarina. | 38 registros | Agregação da base de ordens de serviço por unidade orçamentária |
| [`grafos_centralidade`](#tabela-grafos-centralidade) | Métricas de centralidade e topologia da rede complexa bipartida de oficinas mecânicas credenciadas. | 10 registros (Top estabelecimentos de maior intermediação) | Modelagem de grafos com NetworkX e algoritmo de Louvain |
| [`projecao_trienal`](#tabela-projecao-trienal) | Projeções orçamentárias plurianuais de manutenção comparando o modelo inercial ao prescritivo MILP. | 5 registros | Simulação de Monte Carlo com desgaste de Weibull e solver HiGHS (2027-2029) |
| [`catalogo_figuras`](#tabela-catalogo-figuras) | Catálogo analítico exaustivo das 101 figuras gráficas geradas na dissertação. | 101 registros | scripts/gerar_todas_as_figuras.py e scripts/analise_abastecimentos_ml_prophet.py |
| [`resumo_executivo`](#tabela-resumo-executivo) | Principais métricas e indicadores globais certificados da dissertação de mestrado. | 17 registros | tabela_unica_resultados_oficiais.json e abastecimentos_kpis.json |

---

## 2. Especificação Detalhada das Tabelas e Atributos

### Tabela: `abastecimentos`
**Descrição:** Microdados transacionais exaustivos de 1.000.000 de abastecimentos de combustível da frota pública de Santa Catarina (2019-2022).  
**Origem do Dado:** 2161_abastecimentos_pg0001.xlsb (Higienizado e Anonimizado)  
**Volume Registrado:** 1.000.000 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `cod_venda` | `REAL` | PK | Não | Código numérico identificador único da transação no terminal eletrônico / POS do posto. | `678912.0` |
| `horario` | `TEXT` | - | Sim | Horário do registro da transação no formato HH:MM:SS. | `14:35:10` |
| `prefixo` | `TEXT` | - | Sim | Prefixo operacional ou código de identificação interno da viatura no batalhão. | `PM 5853` |
| `placa` | `TEXT` | PK | Não | Placa identificadora do veículo padronizada no padrão Mercosul/Nacional. | `QIJ8944` |
| `unidade` | `TEXT` | - | Sim | Secretaria de Estado ou Órgão gestor principal responsável pelo bem. | `PMSC/CAEPM 1904 - 899` |
| `subunidade` | `TEXT` | - | Sim | Batalhão regional, delegacia, diretoria ou comarca usuária da viatura. | `PMSC/CAEPM/CHOQUE` |
| `combustivel` | `TEXT` | - | Sim | Tipo de combustível faturado (GASOLINA, DIESEL S10, ETANOL, GNV). | `GASOLINA` |
| `posto` | `TEXT` | - | Sim | Nome fantasia do estabelecimento credenciado que realizou o fornecimento. | `POSTO AGRICOPEL MIME` |
| `uf_posto` | `TEXT` | - | Sim | Unidade Federativa onde está situado o estabelecimento revendedor. | `SC` |
| `cidade_posto` | `TEXT` | - | Sim | Município catarinense em que ocorreu o abastecimento. | `FLORIANOPOLIS` |
| `tipo_frota` | `TEXT` | - | Sim | Natureza da frota (PROPRIA, LOCADA, CONCEDIDA). | `PROPRIA` |
| `marca` | `TEXT` | - | Sim | Fabricante ou montadora do veículo. | `YAMAHA / FIAT / CHEVROLET` |
| `modelo` | `TEXT` | - | Sim | Descrição comercial do modelo do veículo. | `XT 660R / WEEKEND ADVENTURE` |
| `tipo_veiculo` | `TEXT` | - | Sim | Classificação funcional do bem (MOTO, VIATURA, CAMINHAO, AMBULANCIA). | `MOTO / VIATURA` |
| `ano_veiculo` | `TEXT` | - | Sim | Ano de fabricação e modelo do veículo cadastrado no sistema. | `2017/2018` |
| `cnpj_posto` | `TEXT` | - | Sim | Cadastro Nacional da Pessoa Jurídica (CNPJ) do estabelecimento abastecedor. | `83.488.882/0054-15` |
| `odometro` | `REAL` | - | Sim | Quilometragem informada no hodômetro no ato do abastecimento. | `12899.0` |
| `litros` | `REAL` | - | Sim | Volume de combustível fornecido em litros. | `11.74` |
| `preco_unitario` | `REAL` | - | Sim | Valor monetário faturado por litro de combustível (R$/L). | `3.85` |
| `valor_total` | `REAL` | - | Sim | Valor total financeiro liquidado na operação (R$). | `45.21` |
| `km_l_sistema` | `REAL` | - | Sim | Consumo médio calculado entre abastecimentos consecutivos (km/L). | `14.2` |
| `km_rodados_sistema` | `REAL` | - | Sim | Distância percorrida desde o abastecimento anterior registrada. | `250.0` |
| `tipo_venda` | `TEXT` | - | Sim | Meio tecnológico de autorização e liquidação da transação (POS/TEF). | `POS/TEF` |
| `data` | `TIMESTAMP` | - | Sim | Data e hora formal da realização do abastecimento. | `2019-01-01 00:00:00` |
| `ano` | `INTEGER` | - | Sim | Ano civil extraído da data do abastecimento para particionamento analítico. | `2019` |
| `mes_ano` | `TEXT` | - | Sim | Competência mensal no formato YYYY-MM para séries temporais. | `2019-01` |
| `condutor_anon` | `TEXT` | - | Sim | Hash criptográfico SHA-256 anonimizado do condutor (Conformidade com LGPD). | `COND_61E948ABEB64` |
| `flag_anomalia_volume` | `INTEGER` | - | Sim | Flag binária indicadora de volume atípico superior à capacidade do tanque (1=Sim, 0=Não). | `0 ou 1` |
| `flag_anomalia_kml` | `INTEGER` | - | Sim | Flag binária de consumo de combustível inverossímil (<1,5 ou >40 km/L) (1=Sim, 0=Não). | `0 ou 1` |
| `flag_preco_discrepante` | `INTEGER` | - | Sim | Flag binária indicadora de preço unitário excessivo ou inconsistente (1=Sim, 0=Não). | `0 ou 1` |

---

### Tabela: `abastecimentos_ano`
**Descrição:** Estatísticas anuais consolidadas de consumo e dispêndio de combustível.  
**Origem do Dado:** Agregação da tabela abastecimentos  
**Volume Registrado:** 4 registros (2019 a 2022)  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `ano` | `INTEGER` | - | Sim | Ano do exercício financeiro analisado. | `2021` |
| `gasto_total` | `REAL` | - | Sim | Somatório financeiro liquidado em combustíveis no exercício (R$). | `41520140.22` |
| `litros_total` | `REAL` | - | Sim | Volume total em litros de combustível faturado no exercício. | `9120400.10` |
| `preco_medio` | `REAL` | - | Sim | Preço médio ponderado por litro no respectivo exercício (R$/L). | `4.55` |
| `transacoes` | `INTEGER` | - | Sim | Quantidade total de operações de abastecimento registradas no ano. | `275410` |
| `veiculos_unicos` | `INTEGER` | - | Sim | Quantidade de veículos distintos abastecidos no ano. | `7120` |

---

### Tabela: `abastecimentos_categoria`
**Descrição:** Distribuição agregada de despesas e volume de combustível por categoria veicular.  
**Origem do Dado:** Agregação da tabela abastecimentos por tipo_veiculo  
**Volume Registrado:** 8 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `categoria_veiculo` | `TEXT` | - | Sim | Segmento veicular (AMBULANCIA, CAMINHAO, HATCH, MOTO, ONIBUS, SEDAN, SUV, UTILITARIO). | `SEDAN / SUV` |
| `gasto_total` | `REAL` | - | Sim | Dispêndio total aprovado para o segmento veicular (R$). | `51240890.10` |
| `litros_total` | `REAL` | - | Sim | Volume total abastecido pelo segmento veicular (L). | `11400200.00` |
| `transacoes` | `INTEGER` | - | Sim | Número de abastecimentos realizados por veículos dessa categoria. | `340120` |
| `veiculos_unicos` | `INTEGER` | - | Sim | Total de placas distintas pertencentes a essa categoria. | `3250` |
| `preco_medio` | `REAL` | - | Sim | Preço médio por litro praticado nas operações dessa categoria (R$/L). | `4.49` |
| `percentual_gasto` | `REAL` | - | Sim | Participação percentual da categoria sobre o dispêndio total estadual (%). | `33.38` |

---

### Tabela: `abastecimentos_secretaria`
**Descrição:** Consolidação dos gastos e volumes de combustíveis por Secretaria de Estado e Órgão setorial.  
**Origem do Dado:** Agregação da tabela abastecimentos por secretaria gestora  
**Volume Registrado:** 10 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `secretaria` | `TEXT` | - | Sim | Identificação da Pasta Governamental (PMSC, PCSC, SES, SAP, CBMSC, SED, etc.). | `PMSC / PCSC / SES` |
| `gasto_total` | `REAL` | - | Sim | Montante financeiro liquidado pela pasta em combustíveis (R$). | `74020150.80` |
| `litros_total` | `REAL` | - | Sim | Litros totais de combustíveis alocados à pasta. | `16540100.00` |
| `transacoes` | `INTEGER` | - | Sim | Total de abastecimentos efetuados por viaturas da pasta. | `495000` |
| `veiculos_unicos` | `INTEGER` | - | Sim | Frota ativa da pasta com abastecimentos registrados. | `5840` |
| `preco_medio` | `REAL` | - | Sim | Custo médio do combustível faturado para a secretaria (R$/L). | `4.47` |
| `percentual_gasto` | `REAL` | - | Sim | Proporção dos dispêndios da pasta frente ao gasto global do Estado (%). | `48.22` |

---

### Tabela: `abastecimentos_projecao_prophet`
**Descrição:** Projeções preditivas mensais de gastos de combustível obtidas pelo modelo Facebook Prophet.  
**Origem do Dado:** Modelo Prophet treinado sobre a série temporal de abastecimentos (2019-2022)  
**Volume Registrado:** 25 registros (competências futuras até 2025)  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `ano_mes` | `TEXT` | - | Sim | Competência mensal projetada no formato YYYY-MM. | `2024-06` |
| `projecao_gasto` | `REAL` | - | Sim | Valor pontual central estimado de gasto para o mês (R$). | `4620100.50` |
| `projecao_min` | `REAL` | - | Sim | Limite inferior do intervalo de incerteza preditiva de 95% (R$). | `4150000.00` |
| `projecao_max` | `REAL` | - | Sim | Limite superior do intervalo de incerteza preditiva de 95% (R$). | `5090200.00` |

---

### Tabela: `manutencao_itens`
**Descrição:** Microdados de itens de peças e mão de obra de ordens de serviço de manutenção mecânica da frota estadual.  
**Origem do Dado:** os_dataset_limpo.csv (Base higienizada para modelagem e auditoria)  
**Volume Registrado:** 223.819 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `veiculo_id` | `TEXT` | - | Sim | Identificador unificado do veículo no cadastro patrimonial. | `VEIC_1042` |
| `ds_veiculomodelo` | `TEXT` | - | Sim | Descrição do modelo do veículo objeto do reparo. | `COROLLA GLI 1.8` |
| `ds_familia` | `TEXT` | - | Sim | Família da frota (POLICIA MILITAR, CIVIL, SAUDE, ADMINISTRATIVA). | `SEGURANCA PUBLICA` |
| `nr_anoveiculo` | `REAL` | - | Sim | Ano de fabricação do veículo. | `2018.0` |
| `nr_quilometragem` | `REAL` | - | Sim | Hodômetro registrado na abertura da ordem de serviço. | `115400.0` |
| `cd_manutencao_oficina` | `TEXT` | - | Sim | Código identificador da ordem de serviço na oficina credenciada. | `OS_99420` |
| `tipo_manutencao_oficina` | `TEXT` | - | Sim | Classificação da manutenção (PREVENTIVA ou CORRETIVA). | `CORRETIVA` |
| `cd_estabelecimento` | `TEXT` | - | Sim | Código cadastral do estabelecimento/oficina mecânica. | `OFIC_320` |
| `ds_tipoestabelecimento` | `TEXT` | - | Sim | Tipo de credenciamento da oficina (MECANICA GERAL, AUTO ELETRICA, CONCESSIONARIA). | `MECANICA` |
| `ds_os_status` | `TEXT` | - | Sim | Situação cadastral da OS (PAGO, REPROVADO, CANCELADO, BLOQUEADO). | `PAGO` |
| `ds_peca` | `TEXT` | - | Sim | Descrição padronizada do componente mecânico substituído. | `DISCO DE FREIO DIANTEIRO` |
| `ds_fabricante_peca` | `TEXT` | - | Sim | Fabricante ou marca da peça automotiva aplicada. | `TRW / BOSCH` |
| `ds_complemento_peca` | `TEXT` | - | Sim | Informações técnicas adicionais sobre a peça. | `VENTILADO ORIGINAL` |
| `ds_mao_de_obra` | `TEXT` | - | Sim | Descrição do serviço de mão de obra executado pelo mecânico. | `SUBSTITUICAO DE PASTILHAS E DISCOS` |
| `nr_quantidade_pecas` | `REAL` | - | Sim | Quantidade de unidades da peça aplicadas no serviço. | `2.0` |
| `valor_peca_orcado` | `REAL` | - | Sim | Valor orçado inicialmente pelo fornecedor para a peça (R$). | `450.00` |
| `Valor_Aprovado_Peca` | `REAL` | - | Sim | Valor formalmente aprovado e liquidado pela fiscalização para a peça (R$). | `380.00` |
| `vl_total_mao_de_obra` | `REAL` | - | Sim | Valor total aprovado de mão de obra para o item (R$). | `180.00` |
| `valor_mo_orcado` | `REAL` | - | Sim | Valor orçado inicialmente pelo mecânico para a mão de obra (R$). | `240.00` |
| `Valor_Aprovado_MaoDeObra` | `REAL` | - | Sim | Valor de mão de obra liquidado após fiscalização técnica (R$). | `180.00` |
| `vl_orcado` | `REAL` | - | Sim | Somatório orçado inicial de peça + mão de obra (R$). | `690.00` |
| `Valor_Aprovado` | `REAL` | - | Sim | Somatório final liquidado de peça + mão de obra (R$). | `560.00` |
| `vl_total_peca` | `REAL` | - | Sim | Valor total de peças multiplicado pela quantidade (R$). | `380.00` |
| `vl_unitario_peca` | `REAL` | - | Sim | Preço unitário aprovado por componente mecânico (R$). | `190.00` |
| `vl_unitario_mao_de_obra` | `REAL` | - | Sim | Preço hora da mão de obra aprovada (R$/h). | `90.00` |
| `nr_quantidade_hora_mao_de_obra` | `REAL` | - | Sim | Quantidade de horas técnicas autorizadas para o serviço. | `2.0` |
| `dt_aprovacao_item` | `TEXT` | - | Sim | Data em que a fiscalização técnica aprovou o item. | `2021-03-15` |
| `dt_reprovacao_item` | `TEXT` | - | Sim | Data em que o item foi formalmente glosado/reprovado. | `NULL` |
| `dt_cancelamento_item` | `TEXT` | - | Sim | Data de cancelamento do item por perda de objeto. | `NULL` |
| `dt_transacao` | `TEXT` | - | Sim | Data de registro da transação no sistema de gestão de frota. | `2021-03-12` |
| `dt_envio_orcamento` | `TEXT` | - | Sim | Data em que a oficina submeteu o orçamento à DITI/SEA. | `2021-03-13` |
| `dt_entrada_veiculo_oficina` | `TEXT` | - | Sim | Data de entrada física da viatura no pátio da oficina. | `2021-03-12` |
| `dt_aprovacao_os` | `TEXT` | - | Sim | Data de autorização formal da ordem de serviço pela diretoria. | `2021-03-15` |
| `dt_conclusao_servico` | `TEXT` | - | Sim | Data de finalização dos serviços mecânicos. | `2021-03-18` |
| `dt_retirada_veiculo` | `TEXT` | - | Sim | Data de saída da viatura para retorno à prontidão operacional. | `2021-03-19` |
| `dt_reprovacao_os` | `TEXT` | - | Sim | Data de reprovação integral da ordem de serviço. | `NULL` |
| `relato_gestor_auto` | `TEXT` | - | Sim | Parecer descritivo emitido pelo fiscal técnico estadual. | `AUTORIZADO CONFORME TABELA REFERENCIAL` |
| `fl_aprovacao_atipica` | `REAL` | - | Sim | Indicador booleano de aprovação sob regime extraordinário. | `0.0` |
| `ds_uf` | `TEXT` | - | Sim | Unidade Federativa da execução da manutenção. | `SC` |
| `ds_tipofrota` | `TEXT` | - | Sim | Segmento de frota do veículo atendido. | `PROPRIA` |
| `ds_complemento` | `TEXT` | - | Sim | Anotações cadastrais complementares do veículo. | `CHASSI CONFIRMADO` |
| `ds_informacao_adicional1` | `TEXT` | - | Sim | Metadado técnico adicional de auditoria 1. | `TEXTO_LIVRE` |
| `ds_informacao_adicional2` | `TEXT` | - | Sim | Metadado técnico adicional de auditoria 2. | `TEXTO_LIVRE` |
| `ds_informacao_adicional3` | `TEXT` | - | Sim | Metadado técnico adicional de auditoria 3. | `TEXTO_LIVRE` |
| `ds_informacao_adicional4` | `TEXT` | - | Sim | Metadado técnico adicional de auditoria 4. | `TEXTO_LIVRE` |
| `ds_informacao_adicional5` | `TEXT` | - | Sim | Metadado técnico adicional de auditoria 5. | `TEXTO_LIVRE` |

---

### Tabela: `kpis_gerenciais`
**Descrição:** Indicadores de Governança e Gestão de Frota e Informação (GFI) catalogados e monitorados.  
**Origem do Dado:** indicadores_gfi_consolidados.json  
**Volume Registrado:** 38 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `id_indicador` | `TEXT` | PK | Não | Identificador padronizado do indicador no modelo GFI (ex: GFI-01 a GFI-38). | `GFI-01` |
| `tema` | `TEXT` | - | Sim | Dimensão temática de gestão (Custos, Disponibilidade, Conformidade, etc.). | `Controle de Custos` |
| `nome_indicador` | `TEXT` | - | Sim | Nome técnico do indicador de desempenho monitorado. | `Taxa de Glosa Técnica` |
| `valor_apurado` | `TEXT` | - | Sim | Valor numérico ou percentual medido nos dados da frota estadual. | `46,93%` |
| `parametro_referencia` | `TEXT` | - | Sim | Meta ou limite normativo aceitável estabelecido pelos órgãos de controle. | `< 15,0%` |
| `status_conformidade` | `TEXT` | - | Sim | Veredito da auditoria técnica sobre o indicador. | `CRÍTICO - FORA DA META` |
| `criticidade` | `TEXT` | - | Sim | Grau de criticidade para tomada de decisão (NORMAL, ALERTA, CRITICA). | `CRITICA` |

---

### Tabela: `experimentos_modelos`
**Descrição:** Resultados de acurácia, calibração e tempo computacional dos modelos preditivos de ML avaliados.  
**Origem do Dado:** Pipeline de treinamento e validação walk-forward (scripts/treinar_*.py)  
**Volume Registrado:** 28 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `id` | `INTEGER` | PK | Não | Identificador numérico sequencial do experimento de aprendizado de máquina. | `1` |
| `tarefa` | `TEXT` | - | Sim | Tipo de problema supervisionado (classificacao_risco, regressao_custo, series_temporais). | `classificacao_risco` |
| `modelo` | `TEXT` | - | Sim | Nome do algoritmo testado (HistGradientBoosting, Random Forest, SVR, etc.). | `HistGradientBoosting` |
| `features` | `TEXT` | - | Sim | Subconjunto de variáveis empregadas (Multimodal M+P+A, Restrito M, etc.). | `Multimodal (M+P+A)` |
| `roc_auc` | `REAL` | - | Sim | Área sob a Curva ROC obtida na partição out-of-time. | `0.8743` |
| `pr_auc` | `REAL` | - | Sim | Área sob a Curva Precision-Recall (métrica primária em dados desbalanceados). | `0.9510` |
| `brier_score` | `REAL` | - | Sim | Escore de Brier mensurando calibração probabilística (menor é melhor). | `0.1043` |
| `f1_score` | `REAL` | - | Sim | F1-Score máximo alcançado no ponto de corte ótimo. | `0.9113` |
| `mae` | `REAL` | - | Sim | Erro Médio Absoluto em reais nas tarefas de regressão (R$). | `2236.06` |
| `rmse` | `REAL` | - | Sim | Raiz do Erro Quadrático Médio em reais nas tarefas de regressão (R$). | `3780.20` |
| `r2` | `REAL` | - | Sim | Coeficiente de Determinação out-of-sample. | `0.748` |
| `tempo_treinamento_s` | `REAL` | - | Sim | Tempo computacional de treinamento e calibração em segundos. | `1.8` |
| `observacao` | `TEXT` | - | Sim | Comentários técnicos e veredito do modelo (Campeão, Baseline, etc.). | `Modelo Campeão` |

---

### Tabela: `veiculos_leilao`
**Descrição:** Veículos antieconômicos identificados para desincorporação e leilão com fulcro no Decreto Estadual nº 47.539/2018.  
**Origem do Dado:** relatorio_gerencial_frotas_sc.json (Critério: custo acumulado > 40% do valor venal FIPE)  
**Volume Registrado:** 30 registros (Amostra dos 313 veículos auditados)  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `placa` | `TEXT` | PK | Não | Placa identificadora do veículo público antieconômico. | `MIR7280` |
| `modelo` | `TEXT` | - | Sim | Modelo do veículo classificado para baixa patrimonial. | `FORD CARGO 815` |
| `familia` | `TEXT` | - | Sim | Segmento administrativo do bem patrimonial. | `PESADOS / SEGURANCA` |
| `orgao` | `TEXT` | - | Sim | Secretaria proprietária do bem. | `POLICIA MILITAR` |
| `idade_anos` | `INTEGER` | - | Sim | Idade cronológica do bem em anos desde a fabricação. | `14` |
| `quilometragem` | `INTEGER` | - | Sim | Quilometragem total acumulada no hodômetro. | `380450` |
| `valor_venal` | `REAL` | - | Sim | Valor de mercado do veículo balizado pela Tabela FIPE (R$). | `45000.00` |
| `gasto_acumulado` | `REAL` | - | Sim | Somatório histórico de gastos com manutenção mecânica e peças (R$). | `38400.00` |
| `razao_gasto_venal` | `REAL` | - | Sim | Razão entre o gasto de manutenção e o valor venal (Gasto/FIPE). | `0.853` |
| `status_decreto` | `TEXT` | - | Sim | Enquadramento legal no Art. 5º do Decreto 47.539/2018. | `SUPERIOR A 40% DO VENAL` |
| `decisao` | `TEXT` | - | Sim | Diretriz prescritiva gerada pelo algoritmo de auditoria. | `ALIENACAO IMEDIATA EM LEILAO` |

---

### Tabela: `auditoria_orgaos`
**Descrição:** Estatísticas de fiscalização, gastos autorizados e valores glosados por órgão do Governo de Santa Catarina.  
**Origem do Dado:** Agregação da base de ordens de serviço por unidade orçamentária  
**Volume Registrado:** 38 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `orgao` | `TEXT` | - | Sim | Nome do Órgão Governamental ou Secretaria de Estado. | `SECRETARIA DE ESTADO DA SAUDE` |
| `qtd_oss_auditadas` | `INTEGER` | - | Sim | Total de ordens de serviço emitidas e fiscalizadas para o órgão. | `14210` |
| `gasto_aprovado` | `REAL` | - | Sim | Montante financeiro de manutenção efetivamente aprovado e liquidado (R$). | `28500400.00` |
| `valor_orcado_inicial` | `REAL` | - | Sim | Montante originalmente orçado pelas oficinas credenciadas (R$). | `42100800.00` |
| `glosa_tecnica_economia` | `REAL` | - | Sim | Economia pública proporcionada pela glosa de itens abusivos (R$). | `13600400.00` |
| `pct_glosa` | `REAL` | - | Sim | Percentual médio de redução obtido pela fiscalização técnica (%). | `32.30` |
| `downtime_medio_dias` | `REAL` | - | Sim | Tempo médio de paralisação das viaturas em oficinas (dias de imobilização). | `5.4` |

---

### Tabela: `grafos_centralidade`
**Descrição:** Métricas de centralidade e topologia da rede complexa bipartida de oficinas mecânicas credenciadas.  
**Origem do Dado:** Modelagem de grafos com NetworkX e algoritmo de Louvain  
**Volume Registrado:** 10 registros (Top estabelecimentos de maior intermediação)  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `id_estabelecimento` | `TEXT` | PK | Não | Código identificador único do estabelecimento fornecedor no cadastro estadual. | `OFIC_042` |
| `nome_estabelecimento` | `TEXT` | - | Sim | Razão social ou nome de fachada da oficina credenciada. | `AUTO MECANICA CENTRAL LTDA` |
| `grau_conexoes` | `INTEGER` | - | Sim | Grau do nó (Degree): número de veículos distintos atendidos pelo estabelecimento. | `840` |
| `betweenness_centrality` | `REAL` | - | Sim | Centralidade de Intermediação: proporção de menores caminhos que cruzam a oficina. | `0.0842` |
| `pagerank` | `REAL` | - | Sim | Escore de autoridade e influência estrutural na rede pelo algoritmo PageRank. | `0.0125` |
| `comunidade_louvain` | `INTEGER` | - | Sim | Identificador numérico da comunidade modular detectada pelo algoritmo Louvain. | `4` |
| `diagnostico_risco` | `TEXT` | - | Sim | Classificação forense de dependência estrutural e risco de gargalo operacional. | `HUB CRITICO REGIONAL` |

---

### Tabela: `projecao_trienal`
**Descrição:** Projeções orçamentárias plurianuais de manutenção comparando o modelo inercial ao prescritivo MILP.  
**Origem do Dado:** Simulação de Monte Carlo com desgaste de Weibull e solver HiGHS (2027-2029)  
**Volume Registrado:** 5 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `exercicio` | `INTEGER` | PK | Não | Ano civil do exercício fiscal orçado. | `2027` |
| `cenario_inercial` | `REAL` | - | Sim | Gasto público projetado sob a manutenção reativa tradicional As-Is (R$). | `56300400.00` |
| `prescritivo_milp` | `REAL` | - | Sim | Dispêndio ótimo calculado pelo modelo prescritivo sob restrições (R$). | `44120800.00` |
| `economia_anual` | `REAL` | - | Sim | Redução líquida anual de despesas gerada pela otimização (R$). | `12179600.00` |
| `inflacao_setorial_pct` | `REAL` | - | Sim | Taxa de inflação de insumos automotivos incorporada no modelo (%). | `6.08` |
| `premissas_normativas` | `TEXT` | - | Sim | Parâmetros legais e limites vinculados (LOA, Prontidão >= 95%, etc.). | `Prontidão PMSC >= 95%` |

---

### Tabela: `catalogo_figuras`
**Descrição:** Catálogo analítico exaustivo das 101 figuras gráficas geradas na dissertação.  
**Origem do Dado:** scripts/gerar_todas_as_figuras.py e scripts/analise_abastecimentos_ml_prophet.py  
**Volume Registrado:** 101 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `numero` | `INTEGER` | PK | Não | Número ordinal da figura na dissertação de mestrado (1 a 101). | `98` |
| `arquivo_imagem` | `TEXT` | - | Sim | Nome físico do arquivo PNG da figura salvo no diretório charts/. | `fig98_tendencia_prophet_abastecimento.png` |
| `titulo` | `TEXT` | - | Sim | Título técnico oficial da ilustração. | `Decomposição Temporal e Projeção Prophet` |
| `legenda_resumida` | `TEXT` | - | Sim | Descrição sintética do gráfico para o índice da dissertação. | `Projeção temporal de gastos mensais` |
| `diagnostico` | `TEXT` | - | Sim | Conclusão analítica extraída da evidência visual. | `Tendência de crescimento nos dispêndios` |
| `causa_raiz` | `TEXT` | - | Sim | Fator gerador ou etiologia do fenômeno identificado. | `Variação de preços de combustíveis` |
| `impacto_financeiro` | `TEXT` | - | Sim | Magnitude orçamentária associada ao fenômeno analisado. | `R$ 153.488.476,96 em dispêndio` |
| `diretriz_prescritiva` | `TEXT` | - | Sim | Ação governamental prescrita para mitigar o problema. | `Adotar compras programadas com preço teto` |

---

### Tabela: `resumo_executivo`
**Descrição:** Principais métricas e indicadores globais certificados da dissertação de mestrado.  
**Origem do Dado:** tabela_unica_resultados_oficiais.json e abastecimentos_kpis.json  
**Volume Registrado:** 17 registros  

| Coluna | Tipo SQL | Chave | Permite Nulo | Descrição Semântica do Atributo | Exemplo de Valor |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `chave` | `TEXT` | PK | Não | Identificador mnemônico da métrica no sistema de controle. | `total_dispendio_combustivel` |
| `valor_numerico` | `REAL` | - | Sim | Valor numérico em ponto flutuante para cômputos analíticos. | `153488476.96` |
| `valor_formatado` | `TEXT` | - | Sim | Valor formatado com pontuação nacional e unidades monetárias/litros. | `R$ 153.488.476,96` |
| `descricao` | `TEXT` | - | Sim | Explicação contextualizada do indicador certificado. | `Valor financeiro total liquidado em combustíveis` |

---

## 3. Integridade Referencial e Relações entre Entidades

```
        DIAGRAMA DE RELACIONAMENTOS DO BANCO DE DADOS (ER)
        ───────────────────────────────────────────────────
         [veiculos_leilao]               [abastecimentos]
              │ placa                          │ placa
              │                                │
              ▼                                ▼
        ┌───────────────┐               ┌───────────────┐
        │  VEÍCULOS DO  │◄─────────────►│ MANUTENÇÃO DE │
        │  PATRIMÔNIO   │   veiculo_id  │     ITENS     │
        └───────┬───────┘               └───┬───────────┘
                │ orgao                     │ cd_estabelecimento
                ▼                           ▼
        [auditoria_orgaos]              [grafos_centralidade]
        ───────────────────────────────────────────────────
```

1. **Chave de Intersecção Veicular (`placa` / `veiculo_id`):** Articula os 1.000.000 de lançamentos de abastecimentos, as 223.819 ordens de manutenção e os veículos indicados para desfazimento em leilão.
2. **Chave Institucional (`orgao` / `secretaria` / `unidade`):** Agrupa os custos por Unidade Gestora Orçamentária vinculada à LOA e ao Decreto Estadual nº 47.539/2018.
3. **Chave de Prestador de Serviço (`cd_estabelecimento` / `id_estabelecimento`):** Conecta os itens de manutenção autorizados aos nós da rede complexa de oficinas para cálculo de modularidade de Louvain ($Q = 0,5646$) e centralidade de intermediação.

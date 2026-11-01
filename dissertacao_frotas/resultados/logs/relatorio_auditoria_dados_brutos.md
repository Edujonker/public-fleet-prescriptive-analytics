# Relatório de Auditoria Técnico-Científica dos Dados Brutos

**Data e Hora de Execução:** 01/11/2026 13:58:05  
**Duração da Execução:** 8.16 segundos  
**Ambiente:** Python 3.12 (Linux x86_64) | Pandas 3.0.6  
**Instituição:** PPGCAP / CCT / UDESC — Mestrado Acadêmico em Computação Aplicada  

---

## 1. Princípio de Imutabilidade e Proveniência Criptográfica

Para atender à **Exigência 1 de Rigor Científico (Imutabilidade)**, os arquivos recebidos da Secretaria de Estado da Administração de Santa Catarina (SEA/SC) foram auditados em modo de leitura estrita (*read-only*), gerando suas assinaturas criptográficas para certificar a proveniência e integridade forense:

| Arquivo Bruto | Tamanho (MB) | Somente Leitura | Assinatura SHA-256 |
| :--- | :---: | :---: | :--- |
| `Geral_de_OS_23439885_202609110934.csv` | 265.65 MB | SIM | `5c3f89ea9c112bc5097707d770dbf5804be5a604245cdd169430462eff34c1e2` |
| `Memorias_Calculo_por_OS.csv` | 28.0 MB | SIM | `b117bbddbada6afe8af5aea7211207ce2b94dc651474fd459d8560b67fdbeb9f` |
| `Cruzamento_Patrimonio_Manutencao.csv` | 406.15 MB | SIM | `71cde68dc7af53562b71d8fd34bbfffe6a5313e117bb6f721f9c9a0a7d1c0683` |
| `RelatorioVeiculosMobiliario (2).xlsx` | 2.73 MB | SIM | `46c71526c4513d02834c1a2a7631b0f637d60b702b91c471d535370b35884e0f` |

---

## 2. Granularidade, Dimensões e Reconciliação Amostral

A auditoria esclarece de forma definitiva a divergência histórica entre "350.737 OSs" e "77.867 OSs":

- **Universo de Registros Tabulares (Itens de Manutenção):** **350,737 linhas**.  
  Cada linha no arquivo bruto `Geral_de_OS_...` corresponde a um **item de peça ou serviço de mão de obra** associado a uma ordem de serviço (`cd_manutencao_oficina_item`).
- **Ordens de Serviço Únicas (`cd_manutencao_oficina`):** **77,867 OSs**.
- **Relação de Agrupamento:** Cada Ordem de Serviço possui em média **4.50 itens** (mediana: 3; amplitude: 1 a 86 itens).
- **Veículos Monitorados (`ds_placa`):** **7,580 placas distintas**.
- **Rede de Oficinas Credenciadas (`cd_estabelecimento`):** **1,120 oficinas**.
- **Órgãos Públicos Clientes (`cd_cliente`):** **35 órgãos estaduais**.

> **Nota Metodológica Crucial:** Na dissertação anterior, a menção a 350.737 "ordens de serviço" referia-se, com imprecisão terminológica, a **350.737 itens de ordens de serviço**. A unidade de agregação gerencial e física para a modelagem MILP e regressão temporal é a **Ordem de Serviço (77.867 OSs brutas)**.

---

## 3. Distribuição de Ordens de Serviço por Status Operacional

| Status da OS (`ds_os_status`) | Quantidade de OSs | % do Universo | Valor Aprovado (R$) |
| :--- | :---: | :---: | :---: |
| `COBRADAS` | 60,114 | 77.20% | R$ 131,506,578.94 |
| `REPROVADAS` | 11,507 | 14.78% | R$ 1,591,516.64 |
| `CANCELADAS` | 2,151 | 2.76% | R$ 2,043,749.30 |
| `BLOQUEADAS` | 2,104 | 2.70% | R$ 828,830.95 |
| `NAO ENVIADAS AO CLIENTE` | 865 | 1.11% | R$ 76,512.44 |
| `SUBSTITUIDAS` | 817 | 1.05% | R$ 2,516,481.13 |
| `APROVADAS E NAO INICIADAS` | 205 | 0.26% | R$ 155,175.16 |
| `EM REVISAO` | 78 | 0.10% | R$ 0.00 |
| `CONCLUIDAS E NAO COBRADAS` | 20 | 0.03% | R$ 23,922.26 |
| `INICIADAS` | 5 | 0.01% | R$ 4,612.00 |
| `APROVADAS PARCIALMENTE` | 1 | 0.00% | R$ 12,275.00 |

### Análise de Elegibilidade para Modelagem:
1. **Ordens Efetivamente Faturadas e Liquidadas (`COBRADAS`):** Totalizam **60,114 OSs** (77,20% das OSs), congregando **R$ 131,506,578.94** (94,77% do total aprovado).
2. **Ordens Reprovadas / Canceladas / Bloqueadas:** Totalizam **15,762 OSs**. Estas não constituem despesa efetiva da frota, mas representam amostras vitais para o classificador de risco de reprovação e auditoria de anomalias.

---

## 4. Reconciliação Contábil e Glosas da Fiscalização

- **Montante Bruto Cotado pelas Oficinas:** R$ 198,806,964.49
- **Montante Bruto Efetivamente Aprovado:** **R$ 138,759,653.82** (exatamente o volume macro de **R$ 138,76 Milhões** documentado na dissertação)
- **Subtotal de Peças Aprovadas:** R$ 94,647,192.74 (68.21%)
- **Subtotal de Serviços de Mão de Obra Aprovados:** R$ 44,112,461.08 (31.79%)
- **Glosas e Reprovações Administrativas (SEA/SC):** **R$ 60,047,310.67** (30.20% de retenção orçamentária).

---

## 5. Cobertura Cronológica e Integridade Temporal

- **Período de Transações Registrado:** `2020-10-21 08:46:56` até `2026-07-21 19:00:44` (~5,8 anos de dados contínuos).
- **Data de Entrada na Oficina:** `2020-10-13 10:15:00` até `2026-08-13 16:08:00`.
- **Inconsistências Temporais de Entrada/Saída:**
  - Registros com data de conclusão informada anterior à data de entrada física: **0**.
  - Registros com aprovação de OS informada anterior à entrada física: **5946**.
  *(Essas inconsistências exigem tratamento explícito na etapa de pré-processamento via saneamento auditável).*

### Distribuição Anual de OSs:
| Ano da Transação | Quantidade de OSs | Valor Aprovado Total (R$) |
| :---: | :---: | :---: |
| 2020 | 287 | R$ 637,075.74 |
| 2021 | 9,869 | R$ 18,366,270.06 |
| 2022 | 13,047 | R$ 27,480,901.11 |
| 2023 | 12,474 | R$ 29,134,600.55 |
| 2024 | 13,974 | R$ 32,361,276.79 |
| 2025 | 10,447 | R$ 23,457,958.33 |
| 2026 | 18 | R$ 83,436.55 |

---

## 6. Parecer Conclusivo para a Etapa 02 (Pré-processamento)

1. **Imutabilidade Certificada:** A integridade física e criptográfica dos dados originais está preservada.
2. **Definição Clara da Granularidade:** O próximo script (`02_preprocessamento.py`) deve manter **duas visões formalmente conectadas**:
   - Visão Item-Level: preservando os 350.737 itens com tipologia de peça e serviço para explicabilidade granular.
   - Visão OS-Level: consolidando as 77.867 OSs com métricas financeiras, duração e odometria para regressão e otimização MILP.
3. **Rastreabilidade de Exclusões:** Todo filtro (ex: remoção de cancelamentos sem execução física, tratamento de odometria negativa/zero ou remoção de ruídos cronológicos) terá log formal registrando o número exato de linhas excluídas, percentual e justificativa técnica.

---
*Relatório gerado automaticamente pelo script `01_auditoria_dados.py`.*

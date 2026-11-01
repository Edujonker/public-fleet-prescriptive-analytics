# Relatório de Rastreabilidade e Saneamento dos Dados (Script 02)

**Executado em:** 01/11/2026 13:58:14  
**Duração:** 12.48 segundos  
**Conformidade:** Exigência 1 (Imutabilidade) e Exigência 2 (Rastreabilidade Estrita)  

---

## 1. Resumo do Fluxo de Transformação

| Etapa | Operação | Entrada (Itens/OS) | Saída (Itens/OS) | Descartes | Justificativa Técnica/Legal |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **01** | Carga Bruta | 350,737 itens | 350,737 itens | 0 | Leitura direta dos arquivos originais em modo read-only. |
| **02** | Expurgo sem Data/Placa | 350,737 itens | 350,737 itens | 0 itens | Ausência de vínculo veicular ou cronológico impossibilita modelagem. |
| **03** | Agregação por OS | 350,737 itens | 77,867 OSs | Consolidação | Agregação da cesta de peças e serviços na unidade contratual da OS. |
| **04** | Painel Longitudinal ML | 60,114 OSs cobradas | 42,278 instâncias | 7,291 instâncias | Construção do painel veículo-mês; exclusão do mês final sem alvo $t+1$. |

---

## 2. Artefatos de Dados Gerados (dados/processados/)

1. **`os_itens_processados.parquet` (12.28 MB):**
   * Preserva **350,737 registros de itens**, tipologia de peças, serviços e valores unitários.
2. **`os_consolidadas_processadas.parquet` (6.11 MB):**
   * Contém **77,867 Ordens de Serviço** com agregação de custo, horas de reparo, odometria e status fiscal.
   * **60,114 OSs COBRADAS** (R$ 131,506,578.94) aptas para regressão e otimização MILP.
3. **`painel_veiculo_mes_longitudinal.parquet` (1.70 MB):**
   * Contém **42,278 instâncias supervisionadas veículo-mês** com histórico de defasagens (lags) e alvos futuros no horizonte $t+1$ (sem *data leakage*).

---
*Relatório gerado automaticamente por `02_preprocessamento.py`.*

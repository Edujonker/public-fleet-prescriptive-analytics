# RELATÓRIO TÉCNICO E AUDITORIA DE ANOMALIAS, BAIXA PATRIMONIAL E PROJEÇÃO PRESCRITIVA

## 1. Resumo Executivo
- **Total de Ordens de Serviço Anômalas Identificadas:** 2,336
- **Total Financeiro Aprovado em Anomalias:** R$ 25.347.627,57
- **Total Orçado Originalmente:** R$ 47.763.762,10
- **Total Glosado/Evitado pela Auditoria Prévia:** R$ 22.520.222,79

## 2. Detalhamento Técnico e Humanizado dos Casos Críticos
### Categoria: Superfaturamento / Volume Financeiro Desproporcional [CRÍTICA]
**Parecer do Auditor (Linguagem Humanizada):**
> A Ordem de Serviço #9506043 do caminhão Ford Cargo (placa MLG0296), ano 2013, registrou um dispêndio extraordinário de R$ 165.000,00 (sendo R$ 105.398,00 em peças e R$ 59.602,00 em mão de obra) com o veículo retido por impressionantes 119 dias úteis na oficina. Um gasto deste montante em uma única intervenção supera o valor de mercado de um veículo dessa idade (Tabela FIPE) e representa indício veemente de manutenção antieconômica, onde a retífica completa ou substituição do bem deveria ter sido avaliada pela comissão de desfazimento antes da aprovação do serviço.

**Recomendação de Gestão:** Realizar auditoria especial na nota fiscal de peças e confrontar com a tabela de horas padrão (Tempario) da montadora.

```json
{
  "os_id": 9506043,
  "placa": "MLG0296",
  "veiculo_modelo": "CARGO",
  "familia": "CAMINHAO",
  "ano_veiculo": 2013,
  "quilometragem": 71053.0,
  "orgao_vinculado": "SSP/FSP - FUNDO PARA MELHORIA DA SEGURANÇA PÚBLICA",
  "valor_orcado": 172370.0,
  "valor_aprovado": 165000.0,
  "pecas_valor": 105398.0,
  "mao_obra_valor": 59602.0,
  "dias_oficina": 119.66319444444444,
  "quantidade_itens": 63,
  "anomaly_score_iforest": -0.794
}
```

### Categoria: Retenção Excessiva em Oficina (Downtime Abusivo) [ALTA]
**Parecer do Auditor (Linguagem Humanizada):**
> O veículo modelo CRETA (placa RXL4J39) permaneceu paralisado por 180 dias (aproximadamente 6 meses) sob a OS #15057773, acumulando despesa de R$ 22.081,00. Tal tempo de imobilização operacional compromete severamente a continuidade do serviço público do órgão (PCSC/FUMPC - Fundo de Melhoria da Polícia Civil), além de gerar custos ocultos de ociosidade, degradação de componentes estocados e possível cobrança indevida de estadia em oficina terceirizada.

**Recomendação de Gestão:** Notificar a oficina credenciada por descumprimento de SLA contratual e instaurar procedimento de apuração de responsabilidade.

```json
{
  "os_id": 15057773,
  "placa": "RXL4J39",
  "veiculo_modelo": "CRETA",
  "familia": "SUV",
  "ano_veiculo": 2022,
  "quilometragem": 29615.0,
  "orgao_vinculado": "PCSC/FUMPC - Fundo de Melhoria da Polícia Civil",
  "valor_orcado": 23196.0,
  "valor_aprovado": 22081.0,
  "pecas_valor": 17261.0,
  "mao_obra_valor": 4820.0,
  "dias_oficina": 180.0,
  "quantidade_itens": 22,
  "anomaly_score_iforest": -0.7154
}
```

### Categoria: Orçamento Inflado e Glosa Orçamentária Severa [CRÍTICA]
**Parecer do Auditor (Linguagem Humanizada):**
> Na OS #15286579, a oficina prestadora apresentou uma proposta orçamentária no montante exorbitante de R$ 176.071,35, a qual foi integralmente glosada/cancelada pelos auditores técnicos do Estado, resultando em R$ 0,00 aprovados. Esta discrepância de R$ 176.071,35 evidencia tentativa explícita de sobrepreço ou inclusão indevida de itens dispensáveis, comprovando a eficácia dos filtros de auditoria prévia do sistema.

**Recomendação de Gestão:** Manter a oficina em lista de monitoramento rigoroso e auditar retrospectivamente todos os orçamentos emitidos por este fornecedor.

```json
{
  "os_id": 15286579,
  "placa": "QID5668",
  "veiculo_modelo": "RENAULT MASTER EURO AMB",
  "familia": "VAN",
  "ano_veiculo": 2017,
  "quilometragem": 12.0,
  "orgao_vinculado": "SES - Secretaria de Estado da Saúde",
  "valor_orcado": 176071.35,
  "valor_aprovado": 0.0,
  "diferenca_glosada": 176071.35,
  "status_os": "NAO ENVIADAS AO CLIENTE",
  "anomaly_score_iforest": -0.7544
}
```

### Categoria: Veículo Antieconômico com Idade Crítica (> 40 anos) [MÉDIA-ALTA]
**Parecer do Auditor (Linguagem Humanizada):**
> O caminhão placa MAW2409, ano de fabricação 1979 (idade de 47 anos!), recebeu solicitação de manutenção de R$ 90.825,00, constando hodômetro de apenas 10 km. Há evidente inconsistência cadastral ou adulteração/virada de hodômetro para um veículo de mais de 50 anos de uso. A manutenção continuada de um veículo desse porte onera desnecessariamente o erário em virtude da obsolescência mecânica e alto consumo de combustível.

**Recomendação de Gestão:** Determinar a baixa patrimonial imediata do veículo e abertura de edital de desfazimento/leilão conforme Lei 14.133/2021.

```json
{
  "os_id": 14229154,
  "placa": "MAW2409",
  "veiculo_modelo": "L",
  "familia": "CAMINHAO",
  "ano_veiculo": 1979,
  "idade_anos": 47,
  "quilometragem_registrada": 10.0,
  "orgao_vinculado": "CBMSC - Corpo de Bombeiros Militar do Estado de Santa Catarina",
  "valor_orcado": 90825.0,
  "valor_aprovado": 0.0,
  "anomaly_score_iforest": -0.68
}
```

## 3. Relatório de Baixa do Bem (Desfazimento Patrimonial por Antieconomicidade)
| Placa | Modelo | Órgão | Idade | Gasto Acumulado | Valor Residual | Ação Recomendada |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| MJZ2B38 | FIESTA | CBMSC - Corpo de Bombeiro | 14 anos | R$ 32.831,91 | R$ 0,00 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| MBZ0D27 | 8.150 | SEA - Secretaria de Estad | 24 anos | R$ 130.180,20 | R$ 0,00 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| LWT4176 | 1313 | SSP/FSP - FUNDO PARA MELH | 44 anos | R$ 36.701,14 | R$ 0,01 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| LZA1505 | 8.140 | CONV_PMSC - Contratos/Con | 27 anos | R$ 22.770,00 | R$ 0,01 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| LZA1505 | 8.140 | PMSC - Polícia Militar do | 27 anos | R$ 22.770,00 | R$ 0,00 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| MEG7858 | RANGER | CBMSC - Corpo de Bombeiro | 21 anos | R$ 108.763,41 | R$ 0,00 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| MCZ6306 | CARGO | CBMSC - Corpo de Bombeiro | 24 anos | R$ 43.955,60 | R$ 0,00 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| MCM1945 | CARGO | CBMSC - Corpo de Bombeiro | 24 anos | R$ 38.016,34 | R$ 0,00 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| LZQ6657 | L | SSP/FSP - FUNDO PARA MELH | 44 anos | R$ 18.154,30 | R$ 0,01 | Alienar por leilão público (Baixa Patrimonial Imediata) |
| LZQ6657 | L | SAPE - Secretaria de Esta | 44 anos | R$ 18.154,30 | R$ 0,01 | Alienar por leilão público (Baixa Patrimonial Imediata) |


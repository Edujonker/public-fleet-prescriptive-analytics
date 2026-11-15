# Pré-registro das hipóteses exploratórias E1–E3 (teste confirmatório na extração de 2026)

**Autor:** Eduardo Lopes Jonker · **Programa:** PPGCAP/UDESC
**Data do registro:** 15/11/2026
**Situação dos dados de teste:** a extração da SEA/SC com o ano de 2026 completo ainda **não foi recebida**. Nenhum resultado com esses dados foi visto antes deste registro.

## Por que estas hipóteses existem

E1, E2 e E3 **não** fazem parte do anteprojeto. Elas foram formuladas depois de analisar a base atual (out/2020 a set/2025) e, nessa base, são **exploratórias**. Elas passam a ser **confirmatórias** só quando testadas numa base que o autor ainda não viu: a nova extração da SEA/SC com 2026. Este documento fixa, antes de receber esses dados, o enunciado, a medida, o teste e o critério de decisão de cada uma.

Integridade do registro:
- O hash SHA-256 deste arquivo fica em `docs/hipoteses/preregistro_hipoteses_exploratorias_2026.sha256`.
- O arquivo deve ser incluído num commit do repositório público antes da chegada dos dados. A data do commit serve de prova.
- Qualquer mudança posterior precisa ser registrada como desvio, com data e motivo.

## Dados de teste

- **Fonte:** nova extração geral de OS da SEA/SC.
- **Período:** jan/2026 a dez/2026.
- **Recorte:** OS com situação COBRADAS. Mesmo pré-processamento da etapa 02 e o código do repositório no commit deste registro.
- **Período incompleto:** se a extração trouxer menos de 12 meses completos, cada hipótese é testada apenas nos meses completos, e a regra de corte é a do script `planejamento_loa_pca_2026.py`.

## E1 – Estrutura de comunidades no mercado de manutenção

- **Enunciado:** a rede de oficinas que compartilham veículos em 2026 tem estrutura de comunidades maior que a esperada ao acaso, e o gasto permanece concentrado.
- **Medida:**
  - Rede oficina–oficina construída como em `scripts/analise_grafos_frotas.py`, com arestas de peso ≥ 2.
  - Modularidade de Louvain Q (semente 42), comparada com 30 redes nulas obtidas por troca dupla de arestas.
  - Participação dos 10% de oficinas de maior gasto no valor aprovado.
- **Critério:** E1 é confirmada se as duas condições valerem:
  - Q observado for maior que o Q de todas as 30 redes nulas;
  - os 10% maiores concentrarem mais de 50% do gasto.

## E2 – O detector de anomalias não captura o que a fiscalização glosa

- **Enunciado:** em 2026, o escore do Isolation Forest (ν = 0,0085, semente 42, atributos da etapa 05) não separa as OS glosadas das não glosadas.
- **Medida:**
  - Área sob a curva ROC do escore invertido (−score) para prever `teve_glosa` (orçado − aprovado > R$ 0,05).
  - IC 95% por 1.000 reamostragens bootstrap.
- **Critério:** E2 é confirmada se o IC 95% da AUC estiver inteiramente entre 0,40 e 0,60.

## E3 – Precisão da projeção orçamentária de 2026

- **Enunciado:** o total realizado em 2026 fica a menos de 10% da proposta de LOA calculada pelo experimento.
- **Medida:**
  - Proposta registrada: **R$ 33.594.176,58**, do modelo SARIMA (log), gravada em `resultados_loa_pca_2026/resultado_experimento.json` em 15/11/2026.
  - Realizado: soma do valor aprovado das OS COBRADAS com transação em 2026.
  - Se o ano estiver incompleto, a comparação é feita mês a mês, com a soma das previsões mensais desses mesmos meses.
- **Critério:** E3 é confirmada se |realizado − previsto| ÷ realizado < 0,10.

## O que não muda

H1 a H4 continuam definidas pelo anteprojeto e pelos limiares da qualificação. E1–E3 não as substituem e serão apresentadas em seção separada, como hipóteses exploratórias com teste confirmatório.

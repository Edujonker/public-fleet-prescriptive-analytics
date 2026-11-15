#!/usr/bin/env python3
"""
Gera o artigo "Redes veículo–oficina na gestão de frotas públicas" a partir de
dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json.

Saídas:
  SBC/artigo5_grafos_gestao_frotas_sbc.tex   modelo SBC (compilar no Overleaf com sbc-template.sty)
  SBC/artigo5_grafos_gestao_frotas_sbc.pdf   versão de leitura (WeasyPrint)

Todos os números vêm do JSON da análise ou do relatório de carga do Neo4j.
Rodar antes: .venv/bin/python scripts/analise_grafos_frotas.py
"""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

import weasyprint

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "dissertacao_frotas/resultados/logs"
FIGS = ROOT / "dissertacao_frotas/resultados/figuras"
OUT = ROOT / "SBC"
NOME = "artigo5_grafos_gestao_frotas_sbc"

R = json.loads((LOGS / "relatorio_analise_grafos_neo4j.json").read_text(encoding="utf-8"))
C = json.loads((LOGS / "relatorio_neo4j_grafo.json").read_text(encoding="utf-8"))
T, A = R["testes"], R["analises"]
cnt = C["verified_neo4j_counts"]
src = C["source_counts"]


def br(x, nd=0):
    s = f"{x:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, nd=1):
    return br(100 * x, nd) + "%"


sp = A["A4_centralidade_vs_auditoria"]["spearman"]
a1, a2, a3, a5 = A["A1_estabilidade_louvain"], A["A2_modelo_nulo"], A["A3_concentracao"], A["A5_dispersao_veiculo"]
kw = A["A4_centralidade_vs_auditoria"]["kruskal_glosa_entre_comunidades"]
t3 = T["T3_reproducao_etapa06"]
G_ = A["graus_bipartido"]
n_of30 = A["A4_centralidade_vs_auditoria"]["oficinas"]


def rho(k):
    return br(sp[k]["rho"], 3)


def pval(k):
    p = sp[k]["p"]
    return "< 0,001" if p < 0.001 else br(p, 3)


TITULO = ("Redes veículo–oficina na gestão de frotas públicas: persistência em grafo, "
          "validação estatística de comunidades e indicadores para auditoria")
AUTORES = [("Eduardo Lopes Jonker", "eduardo.jonker@edu.udesc.br"),
           ("Vivian Kremer Kalempa", "vivian.kalempa@udesc.br"),
           ("Yuri Kaszubowski Lopes", "yuri.lopes@udesc.br")]
AFIL = "Programa de Pós-Graduação em Computação Aplicada (PPGCAP) – Universidade do Estado de Santa Catarina (UDESC), Joinville – SC – Brasil"

RESUMO = (
    f"Órgãos que gerenciam frotas públicas por meio de redes credenciadas de oficinas acumulam registros de manutenção "
    f"que podem ser lidos como um grafo entre veículos e estabelecimentos. Este artigo constrói esse grafo com dados reais "
    f"da frota do Poder Executivo de Santa Catarina ({br(src['charged_rows_with_both_ids'])} registros cobrados, "
    f"{br(cnt['vehicle_count'])} veículos e {br(cnt['workshop_count'])} estabelecimentos, R$ {br(src['approved_value_total_reais'] / 1e6, 1)} milhões aprovados), "
    f"persiste-o em Neo4j com identificadores pseudonimizados e submete-o a três testes de consistência e a cinco análises. "
    f"A projeção entre oficinas que atendem os mesmos veículos tem modularidade de Louvain Q = {br(a2['Q_observado'], 3)}, "
    f"contra {br(a2['Q_nulo_media'], 3)} ± {br(a2['Q_nulo_dp'], 3)} em {a2['redes_nulas']} redes nulas com a mesma sequência de graus (z = {br(a2['z'], 1)}); "
    f"a partição é estável entre sementes (ARI médio = {br(a1['ARI_vs_seed42_media'], 3)}). Os {pct(0.10, 0)} de oficinas com maior gasto concentram "
    f"{pct(a3['participacao_top10pct_oficinas'])} do valor aprovado (Gini = {br(a3['gini_gasto'], 2)}). A centralidade da oficina tem associação fraca e positiva "
    f"com a taxa de anomalias (ρ = {rho('intermediacao~taxa_anomalia')}) e com a proporção glosada do orçamento (ρ = {rho('intermediacao~glosa_sobre_orcado')}), "
    f"mas não com a frequência de glosas, e as comunidades não diferem quanto a glosas (Kruskal–Wallis, p = {br(kw['p'], 2)}). "
    f"O grafo serve para descrever a estrutura do mercado de manutenção e para priorizar amostras de auditoria, não para identificar irregularidades por si só."
)
PALAVRAS = "grafos; gestão de frotas públicas; detecção de comunidades; Neo4j; auditoria"
ABSTRACT = (
    f"Public fleets serviced through accredited workshop networks generate maintenance records that can be modeled as a "
    f"vehicle–workshop graph. Using real data from the Santa Catarina State Executive fleet ({br(cnt['vehicle_count'])} vehicles, "
    f"{br(cnt['workshop_count'])} workshops), we persist the graph in Neo4j with pseudonymized identifiers, run three consistency tests and five analyses. "
    f"The workshop projection has Louvain modularity Q = {a2['Q_observado']:.3f} versus {a2['Q_nulo_media']:.3f} in degree-preserving null networks "
    f"(z = {a2['z']:.1f}), with a stable partition (mean ARI = {a1['ARI_vs_seed42_media']:.3f}). The top 10% of workshops receive "
    f"{100 * a3['participacao_top10pct_oficinas']:.1f}% of approved spending. Workshop centrality is weakly associated with anomaly rates "
    f"and the share of the budget cut in review, but communities do not differ in review cuts. The graph describes market structure and "
    f"supports audit sampling; it does not, by itself, identify wrongdoing."
)

# ---------------------------------------------------------------------------
# Corpo do artigo. Elementos: ("h", título), ("p", texto), ("tab", legenda, cabeçalho, linhas, fonte),
# ("fig", arquivo, legenda, fonte), ("ul", [itens]).
CORPO = [
    ("h", "Introdução"),
    ("p", "A manutenção de frotas públicas no Brasil é frequentemente executada por redes de estabelecimentos credenciados, "
          "intermediadas por um sistema de gestão que registra orçamentos, aprovações e pagamentos. Em Santa Catarina, a "
          "Secretaria de Estado da Administração (SEA/SC) gerencia a frota do Poder Executivo e os contratos de gerenciamento "
          "de manutenção. Cada ordem de serviço liga um veículo a um estabelecimento, de modo que o histórico inteiro forma um "
          "grafo bipartido. Esse grafo responde a perguntas de gestão que as tabelas isoladas não respondem bem: quantas "
          "oficinas cada veículo usa, quão concentrado é o gasto, se há grupos de oficinas que atendem os mesmos veículos e se a "
          "posição de uma oficina na rede tem relação com os sinais que a fiscalização já produz."),
    ("p", "A ciência de redes tem sido usada para estudar riscos em compras públicas, a partir de indicadores objetivos "
          "construídos com dados de contratação (Fazekas e Kocsis, 2020) e da estrutura das redes entre compradores e fornecedores "
          "(Wachs, Fazekas e Kertész, 2021). A aplicação ao pós-contrato, isto é, à execução da manutenção veicular, é menos "
          "explorada. Há também uma questão de método: algoritmos de maximização de modularidade, como o de Louvain (Blondel et al., 2008), "
          "encontram partições com modularidade alta mesmo em grafos aleatórios (Guimerà, Sales-Pardo e Amaral, 2004; Good, "
          "de Montjoye e Clauset, 2010). Sem comparação com um modelo nulo, um valor como Q = 0,56 não informa, sozinho, se há "
          "estrutura de comunidades."),
    ("p", "Este artigo tem três objetivos: (i) materializar o grafo veículo–oficina em um banco orientado a grafos, com proteção de "
          "identificadores, e verificar que a persistência preserva a rede; (ii) testar a estrutura de comunidades contra modelos nulos "
          "e quanto à estabilidade; e (iii) medir indicadores de gestão derivados do grafo (concentração do gasto, fidelidade do veículo "
          "à oficina, centralidade) e sua associação com glosas e anomalias. O trabalho é parte de uma dissertação sobre analítica "
          "prescritiva para frotas públicas."),

    ("h", "Trabalhos relacionados"),
    ("p", "A modularidade mede quanto as arestas internas de uma partição excedem o esperado em um grafo aleatório com os mesmos graus "
          "(Newman, 2006). O método de Louvain a maximiza de forma gulosa em duas fases (Blondel et al., 2008) e é o mais usado na "
          "prática; o método de Leiden corrige comunidades mal conectadas que o Louvain pode produzir (Traag, Waltman e van Eck, 2019). "
          "Fortunato (2010) revisa as limitações da modularidade, entre elas o limite de resolução e a degenerescência de soluções "
          "quase ótimas, que tornam importante verificar a estabilidade das partições. Para avaliar significância, a randomização por "
          "troca dupla de arestas preserva a sequência de graus (Maslov e Sneppen, 2002); a concordância entre partições é medida pelo "
          "índice de Rand ajustado (Hubert e Arabie, 1985)."),
    ("p", "Em compras públicas, Fazekas e Kocsis (2020) propõem indicadores objetivos de risco de corrupção, como propostas únicas e "
          "procedimentos não competitivos, e Wachs, Fazekas e Kertész (2021) mostram que mercados de contratação podem ser lidos como redes "
          "entre compradores e fornecedores, nas quais a estrutura de comunidades se associa ao risco. Bancos orientados a grafos representam "
          "nós, relações e propriedades explicitamente e favorecem consultas centradas em conexões (Robinson, Webber e Eifrem, 2015). "
          "Este trabalho transpõe essa leitura para a execução de contratos de manutenção, em que a unidade é o par veículo–oficina."),

    ("h", "Dados e método"),
    ("p", f"A fonte é a base processada de ordens de serviço da frota do Poder Executivo de Santa Catarina, com transações entre outubro de 2020 e "
          f"julho de 2026. Foram usados os {br(src['charged_rows_with_both_ids'])} registros com situação COBRADAS e identificadores de veículo e de "
          f"estabelecimento preenchidos, de um total de {br(src['rows_read'])} lidos. O grafo bipartido tem um nó por veículo, um por estabelecimento e "
          f"uma aresta por par veículo–oficina, com o número de registros e o valor aprovado. A projeção liga duas oficinas quando atendem "
          f"pelo menos dois veículos em comum, com peso igual ao número de veículos compartilhados; o limiar de dois remove coincidências isoladas."),
    ("p", "Os identificadores de origem são substituídos por HMAC-SHA-256 com um segredo local (Krawczyk, Bellare e Canetti, 1997); placas, nomes, "
          "CPF/CNPJ, textos livres e abastecimentos não entram no grafo. O grafo é persistido em Neo4j Community 5.26, em contêiner ligado apenas "
          "ao endereço local. As análises leem as arestas do Neo4j e usam NetworkX 3.7; os indicadores por oficina (glosa e anomalia) são ligados "
          "ao grafo pela mesma pseudonimização, sem gravar identificadores originais."),
    ("p", "A glosa é a redução entre o valor orçado e o valor aprovado de uma ordem de serviço (registro com glosa quando a diferença "
          "excede R$ 0,05). A anomalia é a marcação de um Isolation Forest treinado na etapa de detecção de anomalias da dissertação. Os testes e as análises são:"),
    ("ul", [
        "T1 – integridade: contagens lidas do Neo4j iguais às do relatório de carga;",
        "T2 – projeção: rede entre oficinas recalculada a partir das arestas bipartidas igual à projeção gravada, aresta a aresta e peso a peso;",
        "T3 – reprodução: Louvain (semente 42) na projeção persistida comparado ao resultado do pipeline original;",
        f"A1 – estabilidade: Louvain com {a1['sementes']} sementes, com média e desvio de Q, número de comunidades e ARI/NMI contra a semente 42;",
        f"A2 – significância: Q observado contra {a2['redes_nulas']} redes nulas obtidas por troca dupla de arestas (cinco trocas por aresta) com permutação dos pesos;",
        "A3 – concentração: participação das oficinas no gasto, índice de Gini, índice Herfindahl–Hirschman (HHI) e participação da oficina principal no gasto de cada veículo;",
        f"A4 – auditoria: correlação de Spearman entre centralidade (grau ponderado, intermediação aproximada com 400 pivôs e número de veículos) e taxa de glosa, "
        f"proporção glosada do orçamento e taxa de anomalia, para as {br(n_of30)} oficinas da projeção com pelo menos 30 registros, e teste de Kruskal–Wallis da taxa de glosa entre as comunidades com dez ou mais dessas oficinas;",
        "A5 – dispersão do veículo: correlação de Spearman entre o número de oficinas distintas e o custo por registro, e entre o número de oficinas e o número de registros.",
    ]),

    ("h", "Resultados"),
    ("tab", "Testes de consistência do grafo persistido",
     ["Teste", "Esperado", "Observado no Neo4j", "Resultado"],
     [["T1 – integridade",
       f"{br(cnt['vehicle_count'])} veículos; {br(cnt['workshop_count'])} oficinas; {br(cnt['service_edge_count'])} arestas",
       f"{br(T['T1_integridade']['observado']['vehicle_count'])}; {br(T['T1_integridade']['observado']['workshop_count'])}; {br(T['T1_integridade']['observado']['service_edge_count'])}",
       "aprovado" if T["T1_integridade"]["aprovado"] else "reprovado"],
      ["T2 – projeção", f"{br(T['T2_projecao']['arestas_gravadas'])} arestas gravadas",
       f"{br(T['T2_projecao']['arestas_recalculadas'])} recalculadas; {T['T2_projecao']['pesos_divergentes']} pesos divergentes",
       "aprovado" if T["T2_projecao"]["aprovado"] else "reprovado"],
      ["T3 – reprodução", f"Q = {br(t3['etapa06']['modularidade_louvain_q'], 4)}; {t3['etapa06']['total_comunidades']} comunidades",
       f"Q = {br(t3['neo4j']['modularidade_louvain_q'], 4)}; {t3['neo4j']['total_comunidades']} comunidades",
       "aprovado" if t3["aprovado"] else "reprovado"]],
     "Elaborado pelos autores."),
    ("p", f"Os três testes foram aprovados. A projeção recalculada coincide com a gravada em todas as {br(T['T2_projecao']['arestas_gravadas'])} arestas. "
          f"Densidade ({br(t3['neo4j']['densidade'], 5)}) e coeficiente de agrupamento ({br(t3['neo4j']['coeficiente_clustering'], 4)}) são iguais aos do pipeline. "
          f"O Louvain produziu {t3['neo4j']['total_comunidades']} comunidades, contra {t3['etapa06']['total_comunidades']} no pipeline, com a mesma modularidade "
          f"até a terceira casa decimal: a rede é a mesma, mas a ordem dos nós muda com as chaves pseudonimizadas, e o algoritmo é sensível a essa ordem."),
    ("p", f"O grafo bipartido mostra veículos que usam poucas oficinas e oficinas muito desiguais. A mediana é de {br(G_['oficinas_por_veiculo']['mediana'])} oficinas por veículo (máximo de {G_['oficinas_por_veiculo']['max']}); "
          f"{pct(a3['fidelidade_veiculo']['veiculos_com_uma_oficina_pct'])} dos veículos usaram uma única oficina, e a oficina principal responde, "
          f"na mediana, por {pct(a3['fidelidade_veiculo']['mediana_participacao_oficina_principal'])} do gasto do veículo. Do lado das oficinas, a mediana é "
          f"de {br(G_['veiculos_por_oficina']['mediana'])} veículos atendidos, o percentil 90 é de {br(G_['veiculos_por_oficina']['p90'])} e o máximo é de "
          f"{br(G_['veiculos_por_oficina']['max'])}. Das {br(cnt['workshop_count'])} oficinas, "
          f"{br(cnt['workshop_count'] - cnt['projected_workshop_count'])} não compartilham dois veículos com nenhuma outra e ficam fora da projeção."),
    ("tab", "Estrutura de comunidades da projeção oficina–oficina",
     ["Medida", "Valor"],
     [["Modularidade observada (semente 42)", br(a2["Q_observado"], 4)],
      [f"Modularidade em {a1['sementes']} sementes (média ± dp)", f"{br(a1['Q_media'], 4)} ± {br(a1['Q_dp'], 4)}"],
      ["Comunidades (mín.–máx.; moda)", f"{a1['comunidades_min']}–{a1['comunidades_max']}; {a1['comunidades_moda']}"],
      ["ARI / NMI médios contra a semente 42", f"{br(a1['ARI_vs_seed42_media'], 3)} / {br(a1['NMI_vs_seed42_media'], 3)}"],
      [f"Modularidade em {a2['redes_nulas']} redes nulas (média ± dp; máx.)", f"{br(a2['Q_nulo_media'], 4)} ± {br(a2['Q_nulo_dp'], 4)}; {br(a2['Q_nulo_max'], 4)}"],
      ["Escore z do observado contra o nulo", br(a2["z"], 1)]],
     "Elaborado pelos autores."),
    ("p", f"As redes nulas, com os mesmos graus, atingem Q ≈ {br(a2['Q_nulo_media'], 2)}, o que confirma que modularidade alta não é, por si só, evidência de "
          f"estrutura. O valor observado, porém, supera todas as {a2['redes_nulas']} redes nulas por uma margem de {br(a2['z'], 0)} desvios-padrão: há agrupamento "
          f"de oficinas por veículos compartilhados além do que os graus explicam. A partição é estável (ARI médio de {br(a1['ARI_vs_seed42_media'], 3)}), e "
          f"o número de comunidades varia entre {a1['comunidades_min']} e {a1['comunidades_max']} conforme a semente. As cinco maiores comunidades "
          f"da semente 42 têm {', '.join(str(x) for x in a1['tamanhos_seed42'][:5])} oficinas; "
          f"{sum(1 for x in a1['tamanhos_seed42'] if x < 5)} comunidades têm menos de cinco oficinas."),
    ("fig", "grafos_modelo_nulo_e_concentracao.png",
     "Modularidade observada contra as redes nulas (esquerda) e curva de concentração do gasto aprovado por oficina (direita)",
     "Elaborado pelos autores a partir dos dados da SEA/SC."),
    ("p", f"O gasto é desigual entre oficinas: os {pct(0.10, 0)} com maior gasto concentram {pct(a3['participacao_top10pct_oficinas'])} do valor aprovado, as 20 maiores "
          f"concentram {pct(a3['participacao_top20_oficinas'])} e o índice de Gini é {br(a3['gini_gasto'], 2)}. O HHI do conjunto, de {br(a3['hhi'], 0)} pontos, é baixo "
          f"porque há mais de mil estabelecimentos. Esse valor não descreve mercados locais: como o grafo não tem localização, a concentração por município ou região não pôde ser medida."),
    ("tab", f"Correlação de Spearman entre centralidade e indicadores de fiscalização (n = {br(n_of30)} oficinas)",
     ["Centralidade", "Taxa de glosa", "Proporção glosada do orçamento", "Taxa de anomalia"],
     [[nome] + [f"{rho(f'{x}~{y}')} (p {pval(f'{x}~{y}')})".replace("p <", "p<")
                for y in ("taxa_glosa", "glosa_sobre_orcado", "taxa_anomalia")]
      for nome, x in (("Grau ponderado", "grau_ponderado"), ("Intermediação", "intermediacao"), ("Veículos atendidos", "veiculos"))],
     "Elaborado pelos autores. Oficinas da projeção com pelo menos 30 registros cobrados."),
    ("p", f"As associações são fracas. Oficinas mais centrais têm proporção um pouco maior de registros marcados como anômalos "
          f"(ρ entre {rho('veiculos~taxa_anomalia')} e {rho('intermediacao~taxa_anomalia')}) e uma fração um pouco maior do orçamento glosada "
          f"(ρ entre {rho('grau_ponderado~glosa_sobre_orcado')} e {rho('intermediacao~glosa_sobre_orcado')}), mas não têm glosas mais frequentes "
          f"(ρ ≤ {rho('intermediacao~taxa_glosa')}, p ≥ {pval('intermediacao~taxa_glosa')}). A taxa de glosa também não difere entre as {kw['comunidades']} "
          f"comunidades analisadas (H = {br(kw['H'], 2)}, p = {br(kw['p'], 2)})."),
    ("fig", "grafos_centralidade_vs_glosa.png",
     "Grau ponderado na projeção e percentual de ordens de serviço com glosa por oficina",
     "Elaborado pelos autores a partir dos dados da SEA/SC."),
    ("p", f"No nível do veículo, o número de oficinas cresce com o uso (ρ = {br(a5['spearman_oficinas_registros']['rho'], 3)} com o número de registros) e tem "
          f"associação fraca com o custo por registro (ρ = {br(a5['spearman_oficinas_custo_por_registro']['rho'], 3)}). Veículos que passam por mais oficinas "
          f"tendem a ter serviços um pouco mais caros, mas o tipo de serviço e a família do veículo, não controlados aqui, podem explicar essa diferença."),

    ("h", "Discussão"),
    ("p", "Os resultados indicam três usos do grafo na gestão da frota. O primeiro é descritivo: a concentração do gasto e a fidelidade do veículo "
          "à oficina principal são indicadores de mercado que o gestor pode acompanhar ao longo do tempo e por órgão. O segundo é a amostragem para "
          "auditoria: comunidades estáveis e significativas delimitam grupos de oficinas que compartilham veículos e podem ser inspecionados em "
          "conjunto, e a associação fraca entre centralidade e anomalias sugere usar a centralidade como critério auxiliar de priorização, não como "
          "critério principal. O terceiro é operacional: o Neo4j torna essas relações consultáveis em Cypher pelo pessoal de controle, com identificadores protegidos."),
    ("p", "O resultado negativo também é informativo. As comunidades não diferem quanto à frequência de glosas, e a centralidade não se associa a ela. "
          "Para o controle, isso significa que a estrutura da rede não substitui os indicadores de fiscalização e que agrupamentos densos não devem "
          "ser tratados como sinal de conluio. A leitura é compatível com a literatura de compras públicas, em que a estrutura da rede é um entre "
          "vários indicadores de risco (Fazekas e Kocsis, 2020; Wachs, Fazekas e Kertész, 2021)."),
    ("p", "O estudo tem limitações. A análise usa apenas registros cobrados, então orçamentos recusados não entram na rede. A glosa depende da "
          "fiscalização, que não é aleatória: oficinas maiores recebem mais ordens e mais revisão, e isso pode produzir parte da associação observada. "
          "A anomalia vem de um modelo não supervisionado com cerca de 1% de marcações. A intermediação foi aproximada por amostragem de pivôs. O grafo "
          "agrega todo o período, sem dinâmica temporal, e não tem localização das oficinas. O Louvain foi usado para manter a comparação com o pipeline "
          "original; o método de Leiden (Traag, Waltman e van Eck, 2019) é a alternativa a testar."),

    ("h", "Conclusão"),
    ("p", f"O grafo veículo–oficina da frota de Santa Catarina foi persistido em Neo4j sem perda: contagens, projeção e modularidade conferem com o pipeline "
          f"original. A estrutura de comunidades é real, e não um artefato do algoritmo: Q = {br(a2['Q_observado'], 3)} contra {br(a2['Q_nulo_media'], 3)} nas redes nulas, "
          f"com partição estável entre sementes. O gasto é concentrado em poucas oficinas, e cada veículo tende a depender de uma oficina principal. A "
          f"centralidade se associa fracamente a anomalias e à proporção glosada, e não à frequência de glosas. Os próximos passos são incluir localização e "
          f"tempo no grafo, comparar Louvain e Leiden e avaliar com a equipe da SEA/SC se as comunidades ajudam a montar amostras de auditoria."),
]

REFERENCIAS = [
    "BLONDEL, V. D.; GUILLAUME, J.-L.; LAMBIOTTE, R.; LEFEBVRE, E. Fast unfolding of communities in large networks. Journal of Statistical Mechanics: Theory and Experiment, v. 2008, P10008, 2008. DOI: 10.1088/1742-5468/2008/10/P10008.",
    "FAZEKAS, M.; KOCSIS, G. Uncovering high-level corruption: cross-national objective corruption risk indicators using public procurement data. British Journal of Political Science, v. 50, n. 1, p. 155-164, 2020. DOI: 10.1017/S0007123417000461.",
    "FORTUNATO, S. Community detection in graphs. Physics Reports, v. 486, p. 75-174, 2010. DOI: 10.1016/j.physrep.2009.11.002.",
    "GOOD, B. H.; DE MONTJOYE, Y.-A.; CLAUSET, A. Performance of modularity maximization in practical contexts. Physical Review E, v. 81, 046106, 2010. DOI: 10.1103/PhysRevE.81.046106.",
    "GUIMERÀ, R.; SALES-PARDO, M.; AMARAL, L. A. N. Modularity from fluctuations in random graphs and complex networks. Physical Review E, v. 70, 025101, 2004. DOI: 10.1103/PhysRevE.70.025101.",
    "HUBERT, L.; ARABIE, P. Comparing partitions. Journal of Classification, v. 2, p. 193-218, 1985. DOI: 10.1007/BF01908075.",
    "KRAWCZYK, H.; BELLARE, M.; CANETTI, R. HMAC: keyed-hashing for message authentication. RFC 2104. IETF, 1997. DOI: 10.17487/RFC2104.",
    "MASLOV, S.; SNEPPEN, K. Specificity and stability in topology of protein networks. Science, v. 296, p. 910-913, 2002. DOI: 10.1126/science.1065103.",
    "NEWMAN, M. E. J. Modularity and community structure in networks. Proceedings of the National Academy of Sciences, v. 103, p. 8577-8582, 2006. DOI: 10.1073/pnas.0601602103.",
    "ROBINSON, I.; WEBBER, J.; EIFREM, E. Graph databases: new opportunities for connected data. 2. ed. Sebastopol: O'Reilly Media, 2015.",
    "TRAAG, V. A.; WALTMAN, L.; VAN ECK, N. J. From Louvain to Leiden: guaranteeing well-connected communities. Scientific Reports, v. 9, 5233, 2019. DOI: 10.1038/s41598-019-41695-z.",
    "WACHS, J.; FAZEKAS, M.; KERTÉSZ, J. Corruption risk in contracting markets: a network science perspective. International Journal of Data Science and Analytics, v. 12, p. 45-60, 2021. DOI: 10.1007/s41060-019-00204-1.",
]


# ---------------------------------------------------------------- LaTeX
TEX_MAP = [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
           ("ρ", r"$\rho$"), ("≥", r"$\geq$"), ("≤", r"$\leq$"), ("≈", r"$\approx$"), ("±", r"$\pm$"),
           ("×", r"$\times$"), ("−", "-"), ("à", "à")]


def tex(s: str) -> str:
    for a, b in TEX_MAP:
        s = s.replace(a, b)
    return s


def gerar_tex() -> str:
    autores = ", ".join(f"{tex(n)}\\inst{{1}}" for n, _ in AUTORES)
    emails = ", ".join(e for _, e in AUTORES)
    L = [r"\documentclass[12pt,a4paper]{article}", r"\usepackage[utf8]{inputenc}", r"\usepackage[T1]{fontenc}",
         r"\usepackage[brazil]{babel}", r"\usepackage{sbc-template}", r"\usepackage{graphicx}", r"\usepackage{url}",
         r"\usepackage{hyperref}", "",
         f"\\title{{{tex(TITULO)}}}", f"\\author{{{autores}}}",
         f"\\address{{{tex(AFIL)}\\\\ \\email{{{emails}}}}}", "", r"\begin{document}", r"\maketitle", "",
         r"\begin{abstract}", tex(ABSTRACT), r"\end{abstract}", "",
         r"\begin{resumo}", tex(RESUMO), "", f"\\noindent\\textbf{{Palavras-chave:}} {tex(PALAVRAS)}.", r"\end{resumo}", ""]
    nt = nf = 0
    for el in CORPO:
        k = el[0]
        if k == "h":
            L.append(f"\\section{{{tex(el[1])}}}")
        elif k == "p":
            L += [tex(el[1]), ""]
        elif k == "ul":
            L.append(r"\begin{itemize}")
            L += [f"  \\item {tex(i)}" for i in el[1]]
            L += [r"\end{itemize}", ""]
        elif k == "tab":
            nt += 1
            _, leg, cab, linhas, fonte = el
            cols = "l" + "p{%.2f\\linewidth}" % (0.72 / (len(cab) - 1)) * (len(cab) - 1)
            L += [r"\begin{table}[ht]", r"\centering\small", f"\\caption{{{tex(leg)}}}", f"\\label{{tab:t{nt}}}",
                  f"\\begin{{tabular}}{{{cols}}}", r"\hline", " & ".join(f"\\textbf{{{tex(c)}}}" for c in cab) + r" \\ \hline"]
            L += [" & ".join(tex(str(c)) for c in l) + r" \\" for l in linhas]
            L += [r"\hline", r"\end{tabular}", f"\\par\\smallskip\\footnotesize Fonte: {tex(fonte)}", r"\end{table}", ""]
        elif k == "fig":
            nf += 1
            _, arq, leg, fonte = el
            L += [r"\begin{figure}[ht]", r"\centering", f"\\includegraphics[width=\\linewidth]{{{arq}}}",
                  f"\\caption{{{tex(leg)}}}", f"\\label{{fig:f{nf}}}", f"\\par\\footnotesize Fonte: {tex(fonte)}", r"\end{figure}", ""]
    L += [r"\section*{Referências}", r"\begin{small}"]
    L += [tex(r) + r"\par\smallskip" for r in REFERENCIAS]
    L += [r"\end{small}", r"\end{document}", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- HTML/PDF
CSS = """
@page { size: A4; margin: 3cm 3cm 2cm 3cm; @bottom-center { content: counter(page); font: 10pt 'Times New Roman', serif; } }
body { font-family: 'Times New Roman', 'Liberation Serif', serif; font-size: 12pt; line-height: 1.3; text-align: justify; }
h1.t { font-family: Helvetica, Arial, sans-serif; font-size: 16pt; text-align: center; margin: 0 0 12pt; }
.aut { text-align:center; font-family: Helvetica, Arial, sans-serif; font-size: 12pt; font-weight:bold; }
.afi { text-align:center; font-size: 11pt; margin-bottom: 4pt; }
.mail { text-align:center; font-family: 'DejaVu Sans Mono', monospace; font-size: 9.5pt; margin-bottom: 16pt; }
.abs { font-style: italic; margin: 0 0.8cm 10pt; font-size: 12pt; }
.abs b { font-style: normal; }
h2 { font-family: Helvetica, Arial, sans-serif; font-size: 13pt; margin: 14pt 0 4pt; }
p { margin: 0 0 6pt; text-indent: 1.27cm; }
.abs p, td p { text-indent: 0; }
ul { margin: 0 0 6pt 0.8cm; padding: 0; } li { margin: 2pt 0; }
table { border-collapse: collapse; margin: 4pt auto 2pt; font-size: 10pt; width: 100%; }
th { border-top: 1pt solid #000; border-bottom: 0.6pt solid #000; padding: 3pt 4pt; text-align: left; font-family: Helvetica, Arial, sans-serif; font-size: 9.5pt; }
td { padding: 2.5pt 4pt; vertical-align: top; }
tr:last-child td { border-bottom: 1pt solid #000; }
.cap { text-align: center; font-family: Helvetica, Arial, sans-serif; font-size: 10pt; font-weight: bold; margin: 10pt 0 2pt; }
.fon { font-size: 9.5pt; margin: 2pt 0 10pt; text-indent: 0; }
figure { margin: 8pt 0; page-break-inside: avoid; } figure img { width: 100%; }
.ref p { text-indent: 0; text-align: left; font-size: 11pt; margin-bottom: 5pt; }
.tab { page-break-inside: avoid; }
"""


def gerar_html() -> str:
    e = html.escape
    H = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>",
         f"<h1 class='t'>{e(TITULO)}</h1>",
         "<div class='aut'>" + ", ".join(f"{e(n)}<sup>1</sup>" for n, _ in AUTORES) + "</div>",
         f"<div class='afi'><sup>1</sup>{e(AFIL)}</div>",
         "<div class='mail'>" + ", ".join(m for _, m in AUTORES) + "</div>",
         f"<div class='abs'><p><b>Abstract.</b> {e(ABSTRACT)}</p></div>",
         f"<div class='abs'><p><b>Resumo.</b> {e(RESUMO)}</p><p><b>Palavras-chave:</b> {e(PALAVRAS)}.</p></div>"]
    ns = nt = nf = 0
    for el in CORPO:
        k = el[0]
        if k == "h":
            ns += 1
            H.append(f"<h2>{ns}. {e(el[1])}</h2>")
        elif k == "p":
            H.append(f"<p>{e(el[1])}</p>")
        elif k == "ul":
            H.append("<ul>" + "".join(f"<li>{e(i)}</li>" for i in el[1]) + "</ul>")
        elif k == "tab":
            nt += 1
            _, leg, cab, linhas, fonte = el
            H.append(f"<div class='tab'><div class='cap'>Tabela {nt}. {e(leg)}</div><table><tr>"
                     + "".join(f"<th>{e(c)}</th>" for c in cab) + "</tr>"
                     + "".join("<tr>" + "".join(f"<td>{e(str(c))}</td>" for c in l) + "</tr>" for l in linhas)
                     + f"</table><p class='fon'>Fonte: {e(fonte)}</p></div>")
        elif k == "fig":
            nf += 1
            _, arq, leg, fonte = el
            H.append(f"<figure><div class='cap'>Figura {nf}. {e(leg)}</div><img src='{(FIGS / arq).as_uri()}'>"
                     f"<p class='fon'>Fonte: {e(fonte)}</p></figure>")
    H.append("<h2>Referências</h2><div class='ref'>" + "".join(f"<p>{e(r)}</p>" for r in REFERENCIAS) + "</div></body></html>")
    return "\n".join(H)


SECAO = Path(ROOT / "overleaf_dissertacao_udesc/Textuais/Secao10_TesteGrafos.tex")


def gerar_secao_dissertacao() -> str:
    """Seção do Capítulo 10 (formato abnTeX2 da dissertação), com os mesmos números do artigo."""
    t = tex
    tab1 = CORPO[[i for i, e in enumerate(CORPO) if e[0] == "tab"][0]]
    tab3 = CORPO[[i for i, e in enumerate(CORPO) if e[0] == "tab"][2]]

    def tabela(el, rot):
        _, leg, cab, linhas, fonte = el
        cols = "l" + "p{%.2f\\textwidth}" % (0.70 / (len(cab) - 1)) * (len(cab) - 1)
        L = [r"\begin{table}[H]", r"\centering\small", f"\\caption{{{t(leg)}}}", f"\\label{{{rot}}}",
             f"\\begin{{tabular}}{{{cols}}}", r"\hline", " & ".join(f"\\textbf{{{t(c)}}}" for c in cab) + r" \\ \hline"]
        L += [" & ".join(t(str(c)) for c in l) + r" \\" for l in linhas]
        L += [r"\hline", r"\end{tabular}", f"\\fonte{{{t(fonte)}}}", r"\end{table}"]
        return "\n".join(L)

    def figura(arq, leg, rot):
        return "\n".join([r"\begin{figure}[H]", r"\centering", f"\\caption{{{t(leg)}}}",
                          f"\\includegraphics[width=0.95\\textwidth]{{figuras/{arq}}}",
                          r"\fonte{Dados da frota pública de Santa Catarina processados pelo autor (2026).}",
                          f"\\label{{{rot}}}", r"\end{figure}"])

    P = [
        "% Gerado por scripts/gerar_artigo_grafos.py a partir de",
        "% dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json. Não editar à mão.",
        r"\section{Teste e análise do grafo persistido}", r"\label{sec:grafos-teste}",
        t("O grafo persistido no Neo4j foi lido de volta e submetido a três testes de consistência e a cinco análises "
          "(script scripts/analise_grafos_frotas.py). Os indicadores por oficina — glosa, entendida como a redução entre o valor "
          "orçado e o aprovado, e a marcação de anomalia do Isolation Forest do Capítulo 4 — foram ligados ao grafo pela mesma "
          "pseudonimização HMAC da carga, sem gravar identificadores originais."),
        "", r"\subsection{Testes de consistência}", "",
        t(f"Os três testes foram aprovados (Tabela~") + r"\ref{tab:grafos-testes}" + t(
          f"). A projeção entre oficinas recalculada a partir das arestas veículo–oficina coincide com a gravada em todas as "
          f"{br(T['T2_projecao']['arestas_gravadas'])} arestas, com {T['T2_projecao']['pesos_divergentes']} pesos divergentes. "
          f"O Louvain com semente 42 sobre o grafo persistido obteve Q = {br(t3['neo4j']['modularidade_louvain_q'], 4)} e "
          f"{t3['neo4j']['total_comunidades']} comunidades, contra Q = {br(t3['etapa06']['modularidade_louvain_q'], 4)} e "
          f"{t3['etapa06']['total_comunidades']} comunidades no pipeline: a rede é a mesma, mas a ordem dos nós muda com as chaves "
          f"pseudonimizadas, e o algoritmo é sensível a essa ordem."),
        "", tabela(tab1, "tab:grafos-testes"), "",
        r"\subsection{Significância e estabilidade das comunidades}", "",
        t(f"Algoritmos de maximização de modularidade encontram valores altos mesmo em grafos aleatórios (GUIMERÀ; SALES-PARDO; AMARAL, 2004). "
          f"Por isso, o Q observado foi comparado com {a2['redes_nulas']} redes nulas com a mesma sequência de graus, obtidas por troca dupla de arestas "
          f"(MASLOV; SNEPPEN, 2002). As redes nulas atingem Q = {br(a2['Q_nulo_media'], 4)} ± {br(a2['Q_nulo_dp'], 4)} (máximo de {br(a2['Q_nulo_max'], 4)}); "
          f"o valor observado, {br(a2['Q_observado'], 4)}, fica {br(a2['z'], 1)} desvios-padrão acima da média nula e supera todas as redes nulas "
          f"(Figura~") + r"\ref{fig:grafos-nulo}" + t(
          f"). Em {a1['sementes']} sementes, Q variou de {br(a1['Q_min'], 4)} a {br(a1['Q_max'], 4)}, o número de comunidades de "
          f"{a1['comunidades_min']} a {a1['comunidades_max']}, e o índice de Rand ajustado médio contra a semente 42 foi {br(a1['ARI_vs_seed42_media'], 3)}. "
          f"A estrutura de comunidades é, portanto, significativa e estável, o que sustenta o resultado do pipeline original com um teste que ele não fazia."),
        "", figura("grafos_modelo_nulo_e_concentracao.png",
                   "Modularidade observada contra redes nulas e concentração do gasto aprovado por oficina", "fig:grafos-nulo"), "",
        r"\subsection{Indicadores de gestão derivados do grafo}", "",
        t(f"O gasto é concentrado: os 10% de oficinas com maior gasto recebem {pct(a3['participacao_top10pct_oficinas'])} do valor aprovado "
          f"(Gini = {br(a3['gini_gasto'], 2)}). O HHI do conjunto ({br(a3['hhi'], 0)} pontos) é baixo porque há mais de mil estabelecimentos, e o grafo não "
          f"tem localização para medir mercados locais. Cada veículo usa, na mediana, {br(G_['oficinas_por_veiculo']['mediana'])} oficinas; "
          f"{pct(a3['fidelidade_veiculo']['veiculos_com_uma_oficina_pct'])} usaram uma só, e a oficina principal responde, na mediana, por "
          f"{pct(a3['fidelidade_veiculo']['mediana_participacao_oficina_principal'])} do gasto do veículo."),
        "",
        t(f"A Tabela~") + r"\ref{tab:grafos-spearman}" + t(
          f" relaciona a centralidade das {br(n_of30)} oficinas com pelo menos 30 registros aos indicadores de fiscalização. As associações são "
          f"fracas: positivas com a taxa de anomalia e com a proporção glosada do orçamento, e nulas com a frequência de glosas. A taxa de glosa não "
          f"difere entre as {kw['comunidades']} maiores comunidades (Kruskal–Wallis, H = {br(kw['H'], 2)}, p = {br(kw['p'], 2)})."),
        "", tabela(tab3, "tab:grafos-spearman"), "",
        r"\subsection{Implicações e limites}", "",
        t("O grafo é útil para descrever o mercado de manutenção e para montar amostras de auditoria por comunidade, e a centralidade pode ser um "
          "critério auxiliar de priorização. Ele não identifica irregularidades por si só: agrupamentos densos não diferem quanto a glosas, e a "
          "associação com a centralidade pode refletir o fato de oficinas maiores receberem mais ordens e mais revisão. A análise usa apenas "
          "registros cobrados, agrega todo o período, não tem localização das oficinas e aproxima a intermediação por amostragem de 400 pivôs. "
          "A comparação com o método de Leiden (TRAAG; WALTMAN; VAN ECK, 2019) fica como trabalho futuro. Esses resultados são o objeto do artigo "
          "SBC/artigo5_grafos_gestao_frotas_sbc.tex."),
        "",
    ]
    s = "\n".join(P)
    for txt, key in (("(GUIMERÀ; SALES-PARDO; AMARAL, 2004)", "guimera2004"), ("(MASLOV; SNEPPEN, 2002)", "maslov2002"),
                     ("(TRAAG; WALTMAN; VAN ECK, 2019)", "traag2019")):
        s = s.replace(txt, f"\\cite{{{key}}}")
    return s


def main():
    OUT.mkdir(exist_ok=True)
    SECAO.write_text(gerar_secao_dissertacao(), encoding="utf-8")
    print("OK:", SECAO.relative_to(ROOT))
    (OUT / f"{NOME}.tex").write_text(gerar_tex(), encoding="utf-8")
    for el in CORPO:
        if el[0] == "fig":
            shutil.copy2(FIGS / el[1], OUT / el[1])
    weasyprint.HTML(string=gerar_html(), base_url=str(ROOT)).write_pdf(OUT / f"{NOME}.pdf")
    print("OK:", OUT / f"{NOME}.tex", "|", OUT / f"{NOME}.pdf")


if __name__ == "__main__":
    main()

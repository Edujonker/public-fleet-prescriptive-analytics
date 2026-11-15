#!/usr/bin/env python3
"""
Teste e análise do grafo veículo–oficina persistido no Neo4j (graphdb/).

Etapas:
  T1  Integridade: o grafo lido do Neo4j confere com o relatório de carga.
  T2  Projeção: a rede oficina–oficina recalculada a partir das arestas
      SERVICED_AT lidas do Neo4j é idêntica às arestas SHARES_VEHICLE gravadas.
  T3  Reprodução: Louvain (seed 42) na projeção reproduz a etapa 06 do pipeline.
  A1  Estabilidade: Louvain com 30 sementes (Q, nº de comunidades, ARI/NMI).
  A2  Significância: Q observado contra 30 redes nulas com a mesma sequência
      de graus (troca dupla de arestas).
  A3  Concentração: participação das oficinas no gasto e índice HHI.
  A4  Gestão: centralidade da oficina × taxa de glosa e de anomalia
      (Spearman), e glosa por comunidade (Kruskal–Wallis).
  A5  Veículo: nº de oficinas distintas × custo por registro (Spearman).

Os indicadores por oficina (glosa, anomalia) vêm da base processada e são
ligados ao grafo pela mesma pseudonimização HMAC do carregador; nenhum
identificador original é gravado nas saídas.

Saídas:
  dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json
  dissertacao_frotas/resultados/figuras/grafos_*.png

Uso:  .venv/bin/python scripts/analise_grafos_frotas.py
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms.community import louvain_communities, modularity
from scipy import stats
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))  # append: a pasta neo4j/ da raiz não pode ocultar o driver
from graphdb.load_graph import _source_id, load_env_file, pseudonym  # noqa: E402

FONTE = ROOT / "dissertacao_frotas/dados/processados/os_anomalias_detectadas.parquet"
REL_CARGA = ROOT / "dissertacao_frotas/resultados/logs/relatorio_neo4j_grafo.json"
REL_06 = ROOT / "dissertacao_frotas/resultados/logs/relatorio_teoria_grafos.json"
SAIDA = ROOT / "dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json"
FIG = ROOT / "dissertacao_frotas/resultados/figuras"
N_SEMENTES = 30
N_NULOS = 30


def ler_neo4j():
    from neo4j import GraphDatabase
    load_env_file()
    uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    if not any(h in uri for h in ("127.0.0.1", "localhost")):
        raise SystemExit("Recusado: NEO4J_URI não é local.")
    drv = GraphDatabase.driver(uri, auth=(os.getenv("NEO4J_USER", "neo4j"), os.environ["NEO4J_PASSWORD"]))
    with drv.session() as s:
        bip = pd.DataFrame([dict(r) for r in s.run(
            "MATCH (v:FleetVehicle)-[r:SERVICED_AT]->(w:FleetWorkshop) "
            "RETURN v.key AS v, v.family AS familia, w.key AS w, w.kind AS tipo, "
            "r.service_records AS registros, r.approved_value AS valor")])
        proj = pd.DataFrame([dict(r) for r in s.run(
            "MATCH (a:FleetWorkshop)-[r:SHARES_VEHICLE]->(b:FleetWorkshop) "
            "RETURN a.key AS a, b.key AS b, r.shared_vehicle_count AS peso")])
        n_w = s.run("MATCH (w:FleetWorkshop) RETURN count(w) AS n").single()["n"]
    drv.close()
    return bip, proj, n_w


def indicadores_oficina(salt: str) -> pd.DataFrame:
    cols = ["ds_os_status", "cd_estabelecimento", "flag_anomalia", "teve_glosa",
            "vl_glosa_fiscal", "vl_orcado_total", "vl_aprovado_total", "veiculo_id"]
    d = pd.read_parquet(FONTE, columns=cols)
    d = d[d.ds_os_status.astype("string").str.upper().eq("COBRADAS")].copy()
    d["w"] = d.cd_estabelecimento.map(_source_id)
    d = d[d.w.notna() & d.veiculo_id.map(_source_id).notna()]
    d["w"] = d.w.map(lambda x: pseudonym("workshop", x, salt))
    g = d.groupby("w").agg(registros=("flag_anomalia", "size"),
                           taxa_anomalia=("flag_anomalia", "mean"),
                           taxa_glosa=("teve_glosa", "mean"),
                           glosa=("vl_glosa_fiscal", "sum"),
                           orcado=("vl_orcado_total", "sum"))
    g["glosa_sobre_orcado"] = g.glosa / g.orcado.replace(0, np.nan)
    return g


def projetar(bip: pd.DataFrame) -> Counter:
    pares = Counter()
    for _, ws in bip.groupby("v")["w"]:
        for a, b in combinations(sorted(set(ws)), 2):
            pares[(a, b)] += 1
    return Counter({k: c for k, c in pares.items() if c >= 2})


def gini(x) -> float:
    x = np.sort(np.asarray(x, float))
    n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


def main():
    t0 = datetime.now(timezone.utc)
    FIG.mkdir(parents=True, exist_ok=True)
    bip, proj, n_w_total = ler_neo4j()
    carga = json.loads(REL_CARGA.read_text(encoding="utf-8"))["verified_neo4j_counts"]
    r06 = json.loads(REL_06.read_text(encoding="utf-8"))["topologia_rede"]
    out = {"gerado_em_utc": t0.isoformat(), "fonte_grafo": "Neo4j local (graphdb/)", "testes": {}, "analises": {}}

    # T1 integridade
    obs = {"vehicle_count": bip.v.nunique(), "workshop_count": int(n_w_total),
           "service_edge_count": len(bip), "shared_workshop_edge_count": len(proj),
           "projected_workshop_count": len(set(proj.a) | set(proj.b))}
    out["testes"]["T1_integridade"] = {"esperado": carga, "observado": obs,
                                       "aprovado": all(int(obs[k]) == int(carga[k]) for k in obs)}

    # T2 projeção recalculada
    rec = projetar(bip)
    grav = Counter({tuple(sorted((r.a, r.b))): int(r.peso) for r in proj.itertuples()})
    out["testes"]["T2_projecao"] = {"arestas_recalculadas": len(rec), "arestas_gravadas": len(grav),
                                    "pesos_divergentes": sum(1 for k in rec if rec[k] != grav.get(k)),
                                    "aprovado": rec == grav}

    G = nx.Graph()
    for (a, b), p in grav.items():
        G.add_edge(a, b, weight=p)

    # T3 reprodução da etapa 06
    com42 = louvain_communities(G, weight="weight", seed=42)
    q42 = modularity(G, com42, weight="weight")
    dens = nx.density(G)
    clus = nx.average_clustering(G, weight="weight")
    out["testes"]["T3_reproducao_etapa06"] = {
        "etapa06": {k: r06[k] for k in ("nos_oficinas", "arestas", "densidade", "coeficiente_clustering",
                                        "modularidade_louvain_q", "total_comunidades")},
        "neo4j": {"nos_oficinas": G.number_of_nodes(), "arestas": G.number_of_edges(),
                  "densidade": round(dens, 5), "coeficiente_clustering": round(clus, 4),
                  "modularidade_louvain_q": round(q42, 4), "total_comunidades": len(com42)},
    }
    t3 = out["testes"]["T3_reproducao_etapa06"]
    t3["aprovado"] = (t3["etapa06"]["nos_oficinas"] == t3["neo4j"]["nos_oficinas"]
                      and t3["etapa06"]["arestas"] == t3["neo4j"]["arestas"]
                      and abs(t3["etapa06"]["modularidade_louvain_q"] - t3["neo4j"]["modularidade_louvain_q"]) < 0.01)
    t3["nota"] = ("Mesma rede e mesmo algoritmo; a ordem dos nós difere (chaves pseudonimizadas), "
                  "então o Louvain pode convergir para uma partição ligeiramente diferente.")

    # A1 estabilidade
    nos = sorted(G.nodes())
    def rotulos(c):
        m = {n: i for i, s in enumerate(c) for n in s}
        return [m[n] for n in nos]
    ref = rotulos(com42)
    qs, ks, aris, nmis = [], [], [], []
    for s in range(N_SEMENTES):
        c = louvain_communities(G, weight="weight", seed=s)
        qs.append(modularity(G, c, weight="weight")); ks.append(len(c))
        lab = rotulos(c); aris.append(adjusted_rand_score(ref, lab)); nmis.append(normalized_mutual_info_score(ref, lab))
    out["analises"]["A1_estabilidade_louvain"] = {
        "sementes": N_SEMENTES, "Q_media": round(np.mean(qs), 4), "Q_dp": round(np.std(qs, ddof=1), 4),
        "Q_min": round(min(qs), 4), "Q_max": round(max(qs), 4),
        "comunidades_min": min(ks), "comunidades_max": max(ks), "comunidades_moda": Counter(ks).most_common(1)[0][0],
        "ARI_vs_seed42_media": round(np.mean(aris), 3), "NMI_vs_seed42_media": round(np.mean(nmis), 3)}

    # A2 modelo nulo (mesma sequência de graus; pesos permutados entre arestas)
    rng = random.Random(7)
    pesos = [d["weight"] for *_, d in G.edges(data=True)]
    qn = []
    for i in range(N_NULOS):
        H = nx.Graph(G)
        nx.double_edge_swap(H, nswap=5 * H.number_of_edges(), max_tries=100 * H.number_of_edges(), seed=1000 + i)
        pw = pesos[:]; rng.shuffle(pw)
        for (u, v), w in zip(H.edges(), pw):
            H[u][v]["weight"] = w
        qn.append(modularity(H, louvain_communities(H, weight="weight", seed=42), weight="weight"))
    z = (q42 - np.mean(qn)) / np.std(qn, ddof=1)
    out["analises"]["A2_modelo_nulo"] = {
        "redes_nulas": N_NULOS, "metodo": "troca dupla de arestas (graus preservados) + permutação de pesos",
        "Q_observado": round(q42, 4), "Q_nulo_media": round(np.mean(qn), 4), "Q_nulo_dp": round(np.std(qn, ddof=1), 4),
        "Q_nulo_max": round(max(qn), 4), "z": round(float(z), 1),
        "p_empirico": f"< {1 / (N_NULOS + 1):.3f}" if q42 > max(qn) else "não significativo"}

    # A3 concentração do gasto
    gw = bip.groupby("w").valor.sum().sort_values(ascending=False)
    part = gw / gw.sum()
    k10 = max(1, int(round(0.10 * len(gw))))
    out["analises"]["A3_concentracao"] = {
        "oficinas_com_gasto": len(gw), "gasto_total": round(float(gw.sum()), 2),
        "participacao_top10pct_oficinas": round(float(part.iloc[:k10].sum()), 4),
        "participacao_top20_oficinas": round(float(part.iloc[:20].sum()), 4),
        "hhi": round(float((part ** 2).sum() * 10000), 1), "gini_gasto": round(gini(gw.values), 3),
        "nota_hhi": "HHI em pontos (0–10.000); abaixo de 1.500 indica mercado pouco concentrado no conjunto."}
    # concentração por veículo: participação da oficina principal no gasto do veículo
    gv = bip.groupby("v").valor.agg(["sum", "max", "size"])
    gv = gv[gv["sum"] > 0]
    out["analises"]["A3_concentracao"]["fidelidade_veiculo"] = {
        "mediana_participacao_oficina_principal": round(float((gv["max"] / gv["sum"]).median()), 3),
        "veiculos_com_uma_oficina_pct": round(float((gv["size"] == 1).mean()), 3)}

    # A4 centralidade × glosa / anomalia
    salt = os.environ["GRAPH_ID_SALT"]
    ind = indicadores_oficina(salt)
    grau = dict(G.degree(weight="weight"))
    btw = nx.betweenness_centrality(G, weight=None, k=min(400, G.number_of_nodes()), seed=42)
    nveic = bip.groupby("w").v.nunique()
    df = pd.DataFrame({"grau_ponderado": pd.Series(grau), "intermediacao": pd.Series(btw)})
    df["comunidade"] = pd.Series({n: i for i, s in enumerate(com42) for n in s})
    df = df.join(ind, how="left").join(nveic.rename("veiculos"), how="left")
    df30 = df[df.registros >= 30]
    corr = {}
    for x in ("grau_ponderado", "intermediacao", "veiculos"):
        for y in ("taxa_glosa", "taxa_anomalia", "glosa_sobre_orcado"):
            sub = df30[[x, y]].dropna()
            rho, p = stats.spearmanr(sub[x], sub[y])
            corr[f"{x}~{y}"] = {"rho": round(float(rho), 3), "p": float(f"{p:.2g}"), "n": len(sub)}
    grandes = [c for c, n in df30.comunidade.value_counts().items() if n >= 10]
    grupos = [df30.loc[df30.comunidade == c, "taxa_glosa"].dropna().values for c in grandes]
    kw = stats.kruskal(*grupos) if len(grupos) >= 2 else None
    glosa_com = (df30[df30.comunidade.isin(grandes)].groupby("comunidade")
                 .agg(oficinas=("taxa_glosa", "size"), taxa_glosa_mediana=("taxa_glosa", "median"))
                 .sort_values("oficinas", ascending=False))
    out["analises"]["A4_centralidade_vs_auditoria"] = {
        "criterio": "oficinas da projeção com >= 30 registros cobrados", "oficinas": len(df30),
        "spearman": corr,
        "kruskal_glosa_entre_comunidades": ({"H": round(float(kw.statistic), 2), "p": float(f"{kw.pvalue:.2g}"),
                                             "comunidades": len(grandes)} if kw else None),
        "glosa_por_comunidade": {int(k): {"oficinas": int(v.oficinas), "taxa_glosa_mediana": round(float(v.taxa_glosa_mediana), 4)}
                                 for k, v in glosa_com.iterrows()},
        "intermediacao": "aproximada por amostragem de 400 pivôs (seed 42), sem pesos",
        "nota": "Associação, não causalidade: oficinas maiores recebem mais OS e mais fiscalização."}

    # A5 dispersão do veículo
    bv = bip.groupby("v").agg(oficinas=("w", "nunique"), registros=("registros", "sum"), valor=("valor", "sum"))
    bv = bv[bv.registros > 0]
    bv["custo_por_registro"] = bv.valor / bv.registros
    r1 = stats.spearmanr(bv.oficinas, bv.custo_por_registro)
    r2 = stats.spearmanr(bv.oficinas, bv.registros)
    out["analises"]["A5_dispersao_veiculo"] = {
        "veiculos": len(bv), "oficinas_por_veiculo_mediana": float(bv.oficinas.median()),
        "spearman_oficinas_custo_por_registro": {"rho": round(float(r1.statistic), 3), "p": float(f"{r1.pvalue:.2g}")},
        "spearman_oficinas_registros": {"rho": round(float(r2.statistic), 3), "p": float(f"{r2.pvalue:.2g}")},
        "nota": "O número de oficinas cresce com o uso do veículo; a correlação com registros controla essa leitura."}

    gv_ = bip.groupby("v").w.nunique(); gw_ = bip.groupby("w").v.nunique()
    out["analises"]["graus_bipartido"] = {
        "oficinas_por_veiculo": {"mediana": float(gv_.median()), "p90": float(gv_.quantile(.9)), "max": int(gv_.max())},
        "veiculos_por_oficina": {"mediana": float(gw_.median()), "p90": float(gw_.quantile(.9)), "max": int(gw_.max())}}
    tam = sorted((len(c) for c in com42), reverse=True)
    out["analises"]["A1_estabilidade_louvain"]["tamanhos_seed42"] = tam

    tipos = bip.drop_duplicates("w").tipo.value_counts().head(8)
    out["analises"]["tipos_estabelecimento"] = {str(k): int(v) for k, v in tipos.items()}

    # figuras
    plt.rcParams.update({"font.size": 10})
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].hist(qn, bins=12, color="#9bb7a8", label="redes nulas")
    ax[0].axvline(q42, color="#00693e", lw=2.5, label=f"observado Q={q42:.3f}")
    ax[0].set_xlabel("Modularidade Q"); ax[0].set_ylabel("Frequência"); ax[0].legend(fontsize=8)
    ax[0].set_title("Estrutura de comunidades × modelo nulo")
    ax[1].plot(np.arange(1, len(part) + 1) / len(part) * 100, part.cumsum().values * 100, color="#00693e")
    ax[1].plot([0, 100], [0, 100], "--", color="#999")
    ax[1].set_xlabel("% de oficinas (ordenadas por gasto)"); ax[1].set_ylabel("% do gasto aprovado")
    ax[1].set_title("Concentração do gasto")
    fig.tight_layout(); fig.savefig(FIG / "grafos_modelo_nulo_e_concentracao.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    ax.scatter(df30.grau_ponderado, df30.taxa_glosa * 100, s=10, alpha=.5, color="#00693e")
    ax.set_xscale("log"); ax.set_xlabel("Grau ponderado na projeção (log)"); ax.set_ylabel("OS com glosa (%)")
    c = corr["grau_ponderado~taxa_glosa"]
    ax.set_title(f"Centralidade × glosa (Spearman ρ={c['rho']}, n={c['n']})", fontsize=9.5)
    fig.tight_layout(); fig.savefig(FIG / "grafos_centralidade_vs_glosa.png", dpi=200); plt.close(fig)
    out["figuras"] = ["grafos_modelo_nulo_e_concentracao.png", "grafos_centralidade_vs_glosa.png"]

    out["duracao_s"] = round((datetime.now(timezone.utc) - t0).total_seconds(), 1)
    out["todos_testes_aprovados"] = all(t["aprovado"] for t in out["testes"].values())
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf-8")
    for k, t in out["testes"].items():
        print(f"{k}: {'APROVADO' if t['aprovado'] else 'REPROVADO'}")
    print(json.dumps(out["analises"], ensure_ascii=False, indent=1, default=str)[:4000])
    print("->", SAIDA.relative_to(ROOT))


if __name__ == "__main__":
    main()

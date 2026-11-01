#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 06: Modelagem de Redes Complexas, Teoria dos Grafos e Detecção de Comunidades
Framework de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos
Dissertação de Mestrado - PPGCAP / CCT / UDESC
Autor: Eduardo Henrique dos Santos
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Diretrizes:
- Construção do grafo bipartido Veículo-Oficina e projeção monopartita da rede de oficinas.
- Cálculo de métricas de centralidade (Grau, Intermediação/Betweenness, Proximidade).
- Detecção de comunidades pelo Algoritmo de Louvain e cálculo da Modularidade Q.
- Geração de figuras e tabelas automáticas sem hardcoding.
"""

import sys
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from networkx.algorithms.community import louvain_communities, modularity

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 300


def executar_teoria_grafos():
    inicio_exec = datetime.now()
    print("=" * 85)
    print("INICIANDO SCRIPT 06: MODELAGEM DE GRAFOS E COMUNIDADES MECÂNICAS")
    print(f"Timestamp: {inicio_exec.isoformat()}")
    print("=" * 85)

    base_dir = Path(__file__).resolve().parent.parent
    dados_proc_dir = base_dir / "dados" / "processados"
    res_tabelas = base_dir / "resultados" / "tabelas"
    res_figuras = base_dir / "resultados" / "figuras"
    res_logs = base_dir / "resultados" / "logs"

    path_os_parquet = dados_proc_dir / "os_consolidadas_processadas.parquet"
    if not path_os_parquet.exists():
        print(f"[ERRO] Dataset de OSs não encontrado: {path_os_parquet}")
        sys.exit(1)

    print("\n[1/5] Carregando dataset consolidado de Ordens de Serviço...")
    df_os = pd.read_parquet(path_os_parquet)
    # Consideramos as ordens faturadas (COBRADAS) que representam a rede ativa
    cobradas = df_os[df_os["ds_os_status"] == "COBRADAS"].copy()
    print(f"  -> Ordens cobradas ativas na rede: {len(cobradas):,}")

    # 1. CONSTRUÇÃO DO GRAFO BIPARTIDO (VEÍCULO - OFICINA)
    print("\n[2/5] Construindo o grafo bipartido Veículo-Oficina e projetando na rede de prestadores...")
    # Agrupar arestas com peso = contagem de OS e soma de valor aprovado
    arestas_bipartidas = cobradas.groupby(["veiculo_id", "cd_estabelecimento"]).agg(
        peso_os=("cd_manutencao_oficina", "count"),
        peso_valor=("vl_aprovado_total", "sum")
    ).reset_index()

    n_veiculos_rede = arestas_bipartidas["veiculo_id"].nunique()
    n_oficinas_rede = arestas_bipartidas["cd_estabelecimento"].nunique()
    total_arestas_bipartidas = len(arestas_bipartidas)

    print(f"  -> Nós de Veículos: {n_veiculos_rede:,}")
    print(f"  -> Nós de Oficinas Credenciadas: {n_oficinas_rede:,}")
    print(f"  -> Arestas Bipartidas (Interações): {total_arestas_bipartidas:,}")

    # 2. PROJEÇÃO MONOPARTITA DA REDE DE OFICINAS
    # Duas oficinas conectadas se atenderam veículos em comum
    print("\n[3/5] Calculando projeção e métricas topológicas da rede de oficinas...")
    # Para eficiência e relevância analítica, unimos oficinas com veículos compartilhados
    veiculo_oficinas = arestas_bipartidas.groupby("veiculo_id")["cd_estabelecimento"].apply(list)
    
    edge_weights = {}
    for oficinas in veiculo_oficinas:
        if len(oficinas) > 1:
            oficinas_unicas = sorted(list(set(oficinas)))
            for i in range(len(oficinas_unicas)):
                for j in range(i + 1, len(oficinas_unicas)):
                    par = (oficinas_unicas[i], oficinas_unicas[j])
                    edge_weights[par] = edge_weights.get(par, 0) + 1

    G_oficinas = nx.Graph()
    for (u, v), w in edge_weights.items():
        if w >= 2:  # Filtro de ruído: ao menos 2 veículos compartilhados
            G_oficinas.add_edge(u, v, weight=w)

    n_nos_proj = G_oficinas.number_of_nodes()
    n_arestas_proj = G_oficinas.number_of_edges()
    densidade_rede = nx.density(G_oficinas)
    
    # Componente gigante
    componentes = list(nx.connected_components(G_oficinas))
    maior_comp = max(componentes, key=len) if componentes else set()
    sub_giant = G_oficinas.subgraph(maior_comp)
    
    coef_clustering = nx.average_clustering(G_oficinas, weight="weight")
    
    print(f"  -> Rede de Oficinas Filtrada: {n_nos_proj} nós, {n_arestas_proj} arestas.")
    print(f"  -> Densidade da Rede: {densidade_rede:.4f}")
    print(f"  -> Coeficiente Médio de Agrupamento (Clustering): {coef_clustering:.4f}")
    print(f"  -> Tamanho do Componente Gigante: {len(maior_comp)} nós ({(len(maior_comp)/max(1, n_nos_proj))*100:.1f}%)")

    # Centralidades
    graus = dict(G_oficinas.degree())
    graus_ponderados = dict(G_oficinas.degree(weight="weight"))
    betweenness = nx.betweenness_centrality(G_oficinas, weight="weight")
    
    # 3. DETECÇÃO DE COMUNIDADES PELO ALGORITMO DE LOUVAIN
    print("\n[4/5] Executando Algoritmo de Louvain e calculando a Modularidade Q...")
    comunidades_louvain = louvain_communities(G_oficinas, weight="weight", seed=42)
    mod_q = modularity(G_oficinas, comunidades_louvain, weight="weight")
    n_comunidades = len(comunidades_louvain)

    # Atribuir comunidade a cada nó
    node_to_comm = {}
    for idx_comm, comm in enumerate(comunidades_louvain):
        for node in comm:
            node_to_comm[node] = idx_comm

    nx.set_node_attributes(G_oficinas, node_to_comm, "comunidade")

    print(f"  -> Total de Comunidades Detectadas: {n_comunidades}")
    print(f"  -> Modularidade de Louvain Q = {mod_q:.4f} (Estrutura Comunitária Significativa: {mod_q >= 0.3})")

    # Distribuição das 6 maiores comunidades
    tamanho_comunidades = [len(c) for c in comunidades_louvain]
    tamanho_comunidades.sort(reverse=True)
    print(f"  -> Tamanho das maiores comunidades: {tamanho_comunidades[:6]}")

    # Top Oficinas por Centralidade
    oficina_nomes = cobradas.groupby("cd_estabelecimento")["ds_tipoestabelecimento"].first().to_dict()
    oficina_gastos = cobradas.groupby("cd_estabelecimento")["vl_aprovado_total"].sum().to_dict()
    
    top_oficinas_list = []
    for node in sorted(graus_ponderados, key=graus_ponderados.get, reverse=True)[:50]:
        top_oficinas_list.append({
            "cd_estabelecimento": node,
            "tipo_estabelecimento": oficina_nomes.get(node, "OFICINA"),
            "grau_conexoes": graus.get(node, 0),
            "grau_ponderado_veiculos": graus_ponderados.get(node, 0),
            "betweenness_centrality": round(float(betweenness.get(node, 0.0)), 5),
            "comunidade_louvain": node_to_comm.get(node, -1),
            "faturamento_aprovado_reais": round(float(oficina_gastos.get(node, 0.0)), 2)
        })

    df_top_oficinas = pd.DataFrame(top_oficinas_list)
    df_top_oficinas.to_csv(res_tabelas / "top_oficinas_centralidade.csv", index=False, sep=";", encoding="utf-8")

    # Tabela resumo de métricas de rede
    resumo_rede = [{
        "metrica": "Nós de Oficinas (Grafo Monopartito)",
        "valor": n_nos_proj
    }, {
        "metrica": "Arestas de Compartilhamento Veicular",
        "valor": n_arestas_proj
    }, {
        "metrica": "Densidade da Rede",
        "valor": round(densidade_rede, 5)
    }, {
        "metrica": "Coeficiente Médio de Clustering",
        "valor": round(coef_clustering, 4)
    }, {
        "metrica": "Modularidade de Louvain Q",
        "valor": round(mod_q, 4)
    }, {
        "metrica": "Total de Comunidades Identificadas",
        "valor": n_comunidades
    }]
    pd.DataFrame(resumo_rede).to_csv(res_tabelas / "metricas_rede_grafos_oficinas.csv", index=False, sep=";", encoding="utf-8")

    # 4. GERAÇÃO AUTOMÁTICA DE FIGURAS
    print("\n[5/5] Gerando figuras científicas da topologia da rede...")
    
    # Figura 1: Distribuição de Graus (Lei de Potência / Scale-Free check)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    grau_vals = list(graus.values())
    sns.histplot(grau_vals, bins=30, kde=True, color="#1f77b4", ax=ax)
    ax.set_title("Distribuição de Conectividade das Oficinas (Grau de Compartilhamento)")
    ax.set_xlabel("Grau k (Número de Oficinas Conectadas)")
    ax.set_ylabel("Frequência de Oficinas")
    plt.tight_layout()
    fig1_path = res_figuras / "distribuicao_graus_lei_potencia.png"
    plt.savefig(fig1_path, dpi=300)
    plt.close()

    # Figura 2: Visualização da Rede de Oficinas com Cores por Comunidade Louvain
    fig, ax = plt.subplots(figsize=(10, 8))
    # Subgrafo com nós do componente gigante para visualização limpa
    pos = nx.spring_layout(sub_giant, seed=42, k=0.15)
    node_colors = [node_to_comm.get(n, 0) for n in sub_giant.nodes()]
    node_sizes = [min(300, max(20, graus.get(n, 1) * 3)) for n in sub_giant.nodes()]
    
    nx.draw_networkx_nodes(sub_giant, pos, node_color=node_colors, cmap=plt.cm.tab10, node_size=node_sizes, alpha=0.85, ax=ax)
    nx.draw_networkx_edges(sub_giant, pos, alpha=0.15, edge_color="gray", ax=ax)
    ax.set_title(f"Rede de Oficinas Credenciadas (Louvain Q = {mod_q:.3f})")
    ax.axis("off")
    plt.tight_layout()
    fig2_path = res_figuras / "rede_oficinas_comunidades_louvain.png"
    plt.savefig(fig2_path, dpi=300)
    plt.close()

    fim_exec = datetime.now()
    duracao_seg = (fim_exec - inicio_exec).total_seconds()

    log_grafos = {
        "metadados": {
            "script": "06_teoria_grafos.py",
            "timestamp_inicio": inicio_exec.isoformat(),
            "timestamp_fim": fim_exec.isoformat(),
            "duracao_segundos": round(duracao_seg, 2),
            "status": "SUCESSO"
        },
        "topologia_rede": {
            "nos_oficinas": n_nos_proj,
            "arestas": n_arestas_proj,
            "densidade": round(densidade_rede, 5),
            "coeficiente_clustering": round(coef_clustering, 4),
            "modularidade_louvain_q": round(mod_q, 4),
            "total_comunidades": n_comunidades,
            "maiores_comunidades_tamanho": tamanho_comunidades[:6]
        },
        "figuras_geradas": [str(fig1_path.name), str(fig2_path.name)]
    }

    with open(res_logs / "relatorio_teoria_grafos.json", "w", encoding="utf-8") as f:
        json.dump(log_grafos, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Script 06 finalizado com êxito em {duracao_seg:.2f}s!")
    print(f"  -> JSON: {res_logs / 'relatorio_teoria_grafos.json'}")


if __name__ == "__main__":
    executar_teoria_grafos()

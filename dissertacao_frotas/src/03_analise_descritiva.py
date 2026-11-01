#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 03: Análise Descritiva Profunda, Testes de Normalidade e Visualização
Framework de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos
Dissertação de Mestrado - PPGCAP / CCT / UDESC
Autor: Eduardo Henrique dos Santos
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Diretriz: Exigência 5 (Resultados Automáticos - Tabelas e Figuras geradas por código).
Este script realiza a caracterização estatística das variáveis contínuas, executa testes de
normalidade (Shapiro-Wilk, D'Agostino), comparações não paramétricas (Mann-Whitney U) e
gera gráficos vetoriais/alta resolução (300 DPI) para o documento acadêmico.
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
from scipy import stats

# Configurações de plotagem acadêmica
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["figure.dpi"] = 300


def calcular_estatisticas_completas(series: pd.Series, nome: str) -> dict:
    s = series.dropna()
    q25 = float(np.percentile(s, 25))
    q50 = float(np.median(s))
    q75 = float(np.percentile(s, 75))
    return {
        "variavel": nome,
        "n_observacoes": int(len(s)),
        "media": round(float(np.mean(s)), 2),
        "desvio_padrao": round(float(np.std(s, ddof=1)), 2),
        "minimo": round(float(np.min(s)), 2),
        "q25": round(q25, 2),
        "mediana": round(q50, 2),
        "q75": round(q75, 2),
        "iqr": round(q75 - q25, 2),
        "maximo": round(float(np.max(s)), 2),
        "assimetria_skewness": round(float(stats.skew(s)), 3),
        "curtose": round(float(stats.kurtosis(s)), 3)
    }


def executar_analise_descritiva():
    inicio_exec = datetime.now()
    print("=" * 85)
    print("INICIANDO SCRIPT 03: ANÁLISE DESCRITIVA E TESTES NÃO PARAMÉTRICOS")
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
    cobradas = df_os[df_os["ds_os_status"] == "COBRADAS"].copy()
    print(f"  -> Total de OSs carregadas: {len(df_os):,} (Cobradas: {len(cobradas):,})")

    # 1. ESTATÍSTICAS DESCRITIVAS DE VARIÁVEIS CONTÍNUAS
    print("\n[2/5] Calculando momentos estatísticos e medidas de dispersão robustas...")
    variaveis = [
        ("vl_aprovado_total", "Valor Aprovado por OS (R$)"),
        ("vl_orcado_total", "Valor Orçado por OS (R$)"),
        ("vl_aprovado_pecas", "Subtotal Peças Aprovadas (R$)"),
        ("vl_aprovado_mo", "Subtotal Mão de Obra Aprovada (R$)"),
        ("qtd_itens_os", "Quantidade de Itens por OS"),
        ("nr_quilometragem", "Hodômetro Registrado (km)"),
        ("duracao_reparo_horas", "Duração de Reparo (horas)"),
        ("idade_veiculo", "Idade do Veículo (anos)")
    ]

    tabela_descritiva = []
    for col, label in variaveis:
        if col in cobradas.columns:
            stats_dict = calcular_estatisticas_completas(cobradas[col], label)
            tabela_descritiva.append(stats_dict)

    df_descritiva = pd.DataFrame(tabela_descritiva)
    df_descritiva.to_csv(res_tabelas / "estatistica_descritiva_geral.csv", index=False, sep=";", encoding="utf-8")
    print("  -> Tabela de estatísticas descritivas salva.")

    # 2. TESTES FORMAIS DE NORMALIDADE (SHAPIRO-WILK E D'AGOSTINO)
    print("\n[3/5] Executando testes de normalidade...")
    resultados_normalidade = []
    np.random.seed(42)

    for col, label in [("vl_aprovado_total", "Valor Aprovado"), ("duracao_reparo_horas", "Duração Reparo"), ("nr_quilometragem", "Hodômetro")]:
        sample = np.random.choice(cobradas[col].dropna(), size=min(5000, len(cobradas)), replace=False)
        shapiro_stat, shapiro_p = stats.shapiro(sample)
        dagostino_stat, dagostino_p = stats.normaltest(sample)
        
        resultados_normalidade.append({
            "variavel": label,
            "tamanho_amostra_teste": len(sample),
            "shapiro_wilk_w": round(float(shapiro_stat), 5),
            "shapiro_wilk_p_value": float(shapiro_p),
            "dagostino_k2": round(float(dagostino_stat), 5),
            "dagostino_p_value": float(dagostino_p),
            "hipotese_gaussiana_rejeitada": bool(shapiro_p < 0.05)
        })
        print(f"  -> {label:<20}: Shapiro W={shapiro_stat:.4f} (p={shapiro_p:.2e}) | Normalidade Rejeitada: {shapiro_p < 0.05}")

    df_normalidade = pd.DataFrame(resultados_normalidade)
    df_normalidade.to_csv(res_tabelas / "testes_normalidade_shapiro.csv", index=False, sep=";", encoding="utf-8")

    # 3. COMPARAÇÕES NÃO PARAMÉTRICAS (MANN-WHITNEY U)
    print("\n[4/5] Executando testes não paramétricos de Mann-Whitney U...")
    comparacoes = []

    # Comparação A: Preventiva vs Corretiva
    prev = cobradas[cobradas["tipo_manutencao_codigo"] == "PREVENTIVA"]["vl_aprovado_total"].dropna()
    corr = cobradas[cobradas["tipo_manutencao_codigo"] == "CORRETIVA"]["vl_aprovado_total"].dropna()
    u_stat, u_p = stats.mannwhitneyu(corr, prev, alternative="two-sided")
    comparacoes.append({
        "comparacao": "Corretiva vs Preventiva (Custo Aprovado)",
        "grupo_1": "Corretiva",
        "n1": len(corr),
        "mediana_1": round(float(corr.median()), 2),
        "grupo_2": "Preventiva",
        "n2": len(prev),
        "mediana_2": round(float(prev.median()), 2),
        "u_statistic": float(u_stat),
        "p_value": float(u_p),
        "diferenca_estatisticamente_significativa": bool(u_p < 0.05)
    })

    # Comparação B: Veículos Leves vs Pesados
    leves = cobradas[cobradas["ds_familia"] == "LEVE"]["vl_aprovado_total"].dropna()
    pesados = cobradas[cobradas["ds_familia"].isin(["CAMINHAO", "ONIBUS", "MICRO ONIBUS", "EQUIPAMENTO"])]["vl_aprovado_total"].dropna()
    u_stat_f, u_p_f = stats.mannwhitneyu(pesados, leves, alternative="two-sided")
    comparacoes.append({
        "comparacao": "Pesados vs Leves (Custo Aprovado)",
        "grupo_1": "Pesados/Equipamentos",
        "n1": len(pesados),
        "mediana_1": round(float(pesados.median()), 2),
        "grupo_2": "Leves",
        "n2": len(leves),
        "mediana_2": round(float(leves.median()), 2),
        "u_statistic": float(u_stat_f),
        "p_value": float(u_p_f),
        "diferenca_estatisticamente_significativa": bool(u_p_f < 0.05)
    })

    df_mannwhitney = pd.DataFrame(comparacoes)
    df_mannwhitney.to_csv(res_tabelas / "comparacao_nao_parametrica_mannwhitney.csv", index=False, sep=";", encoding="utf-8")

    # 4. GERAÇÃO AUTOMÁTICA DE GRÁFICOS EM ALTA RESOLUÇÃO (300 DPI)
    print("\n[5/5] Gerando figuras científicas em alta resolução...")
    
    # Figura 1: Distribuição de Custos com Escala Logarítmica e Boxplot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    custos_positivos = cobradas[cobradas["vl_aprovado_total"] > 0]["vl_aprovado_total"]
    
    sns.histplot(custos_positivos, log_scale=True, kde=True, color="#1f77b4", ax=ax1, bins=40)
    ax1.set_title("Distribuição do Valor Aprovado (Escala Log)")
    ax1.set_xlabel("Valor Aprovado (R$) - Escala Log")
    ax1.set_ylabel("Densidade / Contagem")
    ax1.axvline(custos_positivos.median(), color="red", linestyle="--", label=f"Mediana: R$ {custos_positivos.median():,.2f}")
    ax1.legend()

    sns.boxplot(x="tipo_manutencao_codigo", y="vl_aprovado_total", data=cobradas[cobradas["tipo_manutencao_codigo"].isin(["CORRETIVA", "PREVENTIVA"])], ax=ax2, palette="Set2")
    ax2.set_yscale("log")
    ax2.set_title("Dispersão: Corretiva vs Preventiva")
    ax2.set_xlabel("Tipo de Manutenção")
    ax2.set_ylabel("Valor Aprovado (R$) - Escala Log")
    
    plt.tight_layout()
    fig1_path = res_figuras / "distribuicao_custos_log_boxplot.png"
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    print(f"  -> Figura 1 salva: {fig1_path.name}")

    # Figura 2: Evolução Temporal Mensal das Despesas de Manutenção
    cobradas["mes_dt"] = pd.to_datetime(cobradas["ano_mes"].astype(str), format="%Y-%m")
    serie_mensal = cobradas.groupby("mes_dt")["vl_aprovado_total"].sum() / 1e6
    
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(serie_mensal.index, serie_mensal.values, marker="o", color="#2ca02c", linewidth=2, markersize=4)
    ax.set_title("Evolução Histórica do Dispêndio Mensal em Manutenção (2020–2026)")
    ax.set_xlabel("Período Mensal")
    ax.set_ylabel("Valor Aprovado (Milhões de R$)")
    ax.grid(True, linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    fig2_path = res_figuras / "serie_temporal_mensal_despesas.png"
    plt.savefig(fig2_path, dpi=300)
    plt.close()
    print(f"  -> Figura 2 salva: {fig2_path.name}")

    fim_exec = datetime.now()
    duracao_seg = (fim_exec - inicio_exec).total_seconds()

    log_descritivo = {
        "metadados": {
            "script": "03_analise_descritiva.py",
            "timestamp_inicio": inicio_exec.isoformat(),
            "timestamp_fim": fim_exec.isoformat(),
            "duracao_segundos": round(duracao_seg, 2),
            "status": "SUCESSO"
        },
        "estatisticas_gerais": tabela_descritiva,
        "testes_normalidade": resultados_normalidade,
        "comparacoes_mann_whitney": comparacoes,
        "figuras_geradas": [str(fig1_path.name), str(fig2_path.name)]
    }

    with open(res_logs / "relatorio_analise_descritiva.json", "w", encoding="utf-8") as f:
        json.dump(log_descritivo, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Script 03 finalizado em {duracao_seg:.2f}s!")
    print(f"  -> JSON: {res_logs / 'relatorio_analise_descritiva.json'}")


if __name__ == "__main__":
    executar_analise_descritiva()

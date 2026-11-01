#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 05: Detecção Não Supervisionada de Anomalias e Sobrepreço via Isolation Forest
Framework de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos
Dissertação de Mestrado - PPGCAP / CCT / UDESC
Autor: Eduardo Henrique dos Santos
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Diretrizes:
- Aplicação sobre as Ordens de Serviço Consolidadas (espaço contínuo multidimensional).
- Estudo de sensibilidade hiperparamétrica e estabilidade multissemente (Jaccard).
- Auditoria de concordância com reprovações/glosas fiscais reais da SEA/SC.
- Resultados 100% reproduzíveis e automatizados.
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
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 300


def executar_deteccao_anomalias():
    inicio_exec = datetime.now()
    print("=" * 85)
    print("INICIANDO SCRIPT 05: DETECÇÃO DE ANOMALIAS E ESTABILIDADE MULTISSEMENTE")
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
    print(f"  -> Total de OSs carregadas: {len(df_os):,}")

    features_if = [
        "vl_aprovado_total", "vl_orcado_total", "vl_aprovado_pecas",
        "vl_aprovado_mo", "nr_quilometragem", "duracao_reparo_horas",
        "idade_veiculo", "qtd_itens_os"
    ]

    # Preencher nulos se houver e padronizar
    X_raw = df_os[features_if].fillna(0.0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # 1. ESTUDO DE ESTABILIDADE MULTISSEMENTE E SENSIBILIDADE DA CONTAMINAÇÃO
    print("\n[2/5] Avaliando estabilidade de Jaccard e sensibilidade do parâmetro de contaminação...")
    seeds = [42, 123, 999]
    contaminacoes = [0.005, 0.0085, 0.01, 0.02, 0.05]
    tabela_estabilidade = []

    for c in contaminacoes:
        anomalias_por_seed = {}
        for s in seeds:
            clf = IsolationForest(contamination=c, random_state=s, n_estimators=100, n_jobs=-1)
            preds = clf.fit_predict(X_scaled)
            anomalias_por_seed[s] = set(np.where(preds == -1)[0])

        # Calcular similaridade média de Jaccard entre sementes
        j_42_123 = len(anomalias_por_seed[42] & anomalias_por_seed[123]) / len(anomalias_por_seed[42] | anomalias_por_seed[123])
        j_42_999 = len(anomalias_por_seed[42] & anomalias_por_seed[999]) / len(anomalias_por_seed[42] | anomalias_por_seed[999])
        j_123_999 = len(anomalias_por_seed[123] & anomalias_por_seed[999]) / len(anomalias_por_seed[123] | anomalias_por_seed[999])
        jaccard_medio = float(np.mean([j_42_123, j_42_999, j_123_999]))

        n_anomalias = len(anomalias_por_seed[42])
        tabela_estabilidade.append({
            "contaminacao_nominal": c,
            "contaminacao_pct": round(c * 100, 2),
            "anomalias_detectadas": n_anomalias,
            "jaccard_medio_sementes": round(jaccard_medio, 4),
            "estabilidade_certificada": bool(jaccard_medio >= 0.80)
        })
        print(f"  -> Nu={c*100:>4.2f}%: {n_anomalias:>5} OSs anômalas | Jaccard Médio={jaccard_medio:.4f} (Estável: {jaccard_medio >= 0.80})")

    df_estabilidade = pd.DataFrame(tabela_estabilidade)
    df_estabilidade.to_csv(res_tabelas / "estabilidade_isolation_forest_sementes.csv", index=False, sep=";", encoding="utf-8")

    # 2. MODELO DE REFERÊNCIA (Calibração Formal nu = 0.0085 / 0,85%)
    print("\n[3/5] Ajustando modelo de referência (nu = 0,85%) e computando scores de anomalia...")
    nu_ref = 0.0085
    clf_ref = IsolationForest(contamination=nu_ref, random_state=42, n_estimators=100, n_jobs=-1)
    df_os["flag_anomalia"] = (clf_ref.fit_predict(X_scaled) == -1).astype(int)
    # Score de anomalia negativo: valores menores = mais anômalos
    df_os["score_anomalia"] = clf_ref.score_samples(X_scaled)

    total_anomalias_ref = int(df_os["flag_anomalia"].sum())
    pct_anomalias_ref = round((total_anomalias_ref / len(df_os)) * 100, 3)
    vl_anomalias_aprovado = float(df_os[df_os["flag_anomalia"] == 1]["vl_aprovado_total"].sum())
    vl_anomalias_orcado = float(df_os[df_os["flag_anomalia"] == 1]["vl_orcado_total"].sum())
    vl_glosas_anomalias = vl_anomalias_orcado - vl_anomalias_aprovado

    print(f"  -> Total de OSs Anômalas Isoladas (nu={nu_ref*100}%): {total_anomalias_ref:,} OSs ({pct_anomalias_ref}%)")
    print(f"  -> Montante Orçado pelas Ordens Anômalas: R$ {vl_anomalias_orcado:,.2f}")
    print(f"  -> Montante Efetivamente Aprovado: R$ {vl_anomalias_aprovado:,.2f}")
    print(f"  -> Glosas e Reprovações Concentradas: R$ {vl_glosas_anomalias:,.2f} (Retenção: {(vl_glosas_anomalias/vl_anomalias_orcado)*100:.2f}%)")

    # 3. CONCORDÂNCIA ESTATÍSTICA COM AS GLOSAS E REPROVAÇÕES FISCAIS
    print("\n[4/5] Executando teste de hipóteses sobre scores de anomalia vs intervenções fiscais...")
    scores_glosadas = df_os[df_os["teve_glosa"] == 1]["score_anomalia"]
    scores_sem_glosa = df_os[df_os["teve_glosa"] == 0]["score_anomalia"]
    
    t_stat_glosa, p_val_glosa = stats.ttest_ind(scores_glosadas, scores_sem_glosa, equal_var=False)
    u_stat_glosa, u_p_glosa = stats.mannwhitneyu(scores_glosadas, scores_sem_glosa, alternative="less")

    print(f"  -> Teste Welch t-test (Scores Glosadas vs Sem Glosa): t={t_stat_glosa:.2f}, p={p_val_glosa:.2e}")
    print(f"  -> Mann-Whitney U (Scores Glosadas menores): U={u_stat_glosa:.1f}, p={u_p_glosa:.2e}")

    # Salvar amostra forense das 50 maiores anomalias
    cols_amostra = [
        "cd_manutencao_oficina", "veiculo_id", "ds_veiculomodelo", "ds_familia",
        "cd_estabelecimento", "ds_os_status", "vl_orcado_total", "vl_aprovado_total",
        "vl_glosa_fiscal", "nr_quilometragem", "duracao_reparo_horas", "score_anomalia"
    ]
    top_anomalias = df_os.sort_values(by="score_anomalia", ascending=True).head(50)[cols_amostra]
    top_anomalias.to_csv(res_tabelas / "anomalias_detectadas_amostra_forense.csv", index=False, sep=";", encoding="utf-8")

    # Salvar dataset completo com flags de anomalia
    path_anomalias_parquet = dados_proc_dir / "os_anomalias_detectadas.parquet"
    df_os.to_parquet(path_anomalias_parquet, index=False, compression="snappy")
    print(f"  -> Dataset completo com scores de anomalia salvo: {path_anomalias_parquet.name}")

    # 4. GERAÇÃO DE FIGURAS
    print("\n[5/5] Gerando figuras científicas de auditoria de anomalias...")
    
    # Figura 1: Estabilidade de Jaccard por Contaminação
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot([x["contaminacao_pct"] for x in tabela_estabilidade],
            [x["jaccard_medio_sementes"] for x in tabela_estabilidade],
            marker="o", color="#d62728", linewidth=2, markersize=6)
    ax.axhline(0.80, color="gray", linestyle="--", label="Limiar de Estabilidade Robusta (J = 0,80)")
    ax.set_title("Estabilidade Algorítmica do Isolation Forest entre Sementes Aleatórias")
    ax.set_xlabel("Taxa Nominal de Contaminação Nu (%)")
    ax.set_ylabel("Índice de Similaridade de Jaccard Médio")
    ax.set_ylim(0.70, 1.0)
    ax.legend(loc="lower right")
    plt.tight_layout()
    fig1_path = res_figuras / "estabilidade_jaccard_contaminacao.png"
    plt.savefig(fig1_path, dpi=300)
    plt.close()

    # Figura 2: Distribuição dos Scores de Anomalia por Status de Glosa
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.kdeplot(scores_sem_glosa, fill=True, color="#2ca02c", label="OSs Aprovadas Integralmente (Sem Glosa)", ax=ax, alpha=0.4)
    sns.kdeplot(scores_glosadas, fill=True, color="#d62728", label="OSs com Glosa ou Reprovação Fiscal", ax=ax, alpha=0.4)
    ax.axvline(float(df_os[df_os["flag_anomalia"] == 1]["score_anomalia"].max()), color="black", linestyle="--", label="Limiar de Corte Anômalo (Nu = 0,85%)")
    ax.set_title("Concordância Forense: Distribuição dos Scores de Anomalia")
    ax.set_xlabel("Score de Anomalia do Isolation Forest (Valores menores = maior atipicidade)")
    ax.set_ylabel("Densidade")
    ax.legend(loc="upper left")
    plt.tight_layout()
    fig2_path = res_figuras / "distribuicao_scores_anomalia_glosas.png"
    plt.savefig(fig2_path, dpi=300)
    plt.close()

    fim_exec = datetime.now()
    duracao_seg = (fim_exec - inicio_exec).total_seconds()

    log_anomalia = {
        "metadados": {
            "script": "05_deteccao_anomalias.py",
            "timestamp_inicio": inicio_exec.isoformat(),
            "timestamp_fim": fim_exec.isoformat(),
            "duracao_segundos": round(duracao_seg, 2),
            "status": "SUCESSO"
        },
        "estabilidade_sementes": tabela_estabilidade,
        "modelo_referencia": {
            "contaminacao_nu": nu_ref,
            "total_anomalias_detectadas": total_anomalias_ref,
            "pct_universo_os": pct_anomalias_ref,
            "vl_total_orcado": round(vl_anomalias_orcado, 2),
            "vl_total_aprovado": round(vl_anomalias_aprovado, 2),
            "vl_total_glosas_concentradas": round(vl_glosas_anomalias, 2),
            "taxa_retencao_glosas_pct": round((vl_glosas_anomalias / vl_anomalias_orcado) * 100, 2)
        },
        "concordancia_fiscal": {
            "t_statistic": round(float(t_stat_glosa), 3),
            "t_p_value": float(p_val_glosa),
            "mann_whitney_u": round(float(u_stat_glosa), 1),
            "mann_whitney_p": float(u_p_glosa),
            "validacao_estatistica_rejeitada": bool(p_val_glosa < 0.05)
        },
        "figuras_geradas": [str(fig1_path.name), str(fig2_path.name)]
    }

    with open(res_logs / "relatorio_deteccao_anomalias.json", "w", encoding="utf-8") as f:
        json.dump(log_anomalia, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Script 05 concluído com êxito em {duracao_seg:.2f}s!")
    print(f"  -> JSON: {res_logs / 'relatorio_deteccao_anomalias.json'}")


if __name__ == "__main__":
    executar_deteccao_anomalias()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 07: Explicabilidade Algorítmica Global e Local (XAI Auditável)
Framework de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos
Dissertação de Mestrado - PPGCAP / CCT / UDESC
Autor: Eduardo Henrique dos Santos
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Diretriz: Exigência 5 (Resultados Automáticos e Verificáveis) e Hipótese H4.
Aplica valores de Shapley (SHAP TreeExplainer via Teoria dos Jogos Cooperativos)
e aproximações locais lineares (LIME) sobre o modelo campeão HistGradientBoosting,
avaliando a estabilidade explicativa cruzada (Spearman rank correlation e Jaccard top-k).
"""

import sys
import json
import warnings
from datetime import datetime
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import shap
from lime import lime_tabular

warnings.filterwarnings("ignore")

FEATURE_LABELS = {
    "custo_mes": "Custo Mês Atual (R$)",
    "vl_pecas_mes": "Gasto com Peças (R$)",
    "vl_mo_mes": "Gasto com Mão de Obra (R$)",
    "qtd_os_mes": "Volume de OS no Mês",
    "qtd_corretivas_mes": "Falhas Corretivas no Mês",
    "qtd_preventivas_mes": "Preventivas no Mês",
    "km_max": "Odômetro Acumulado (km)",
    "idade_veiculo": "Idade do Veículo (Anos)",
    "custo_lag1": "Custo Defasado t-1 (R$)",
    "custo_lag2": "Custo Defasado t-2 (R$)",
    "os_lag1": "Volume OS Defasado t-1",
    "corretivas_lag1": "Corretivas Defasadas t-1",
    "km_diff": "Quilometragem Percorrida Mês (km)",
    "patrimonio_valor_entrada": "Valor de Aquisição do Bem (R$)",
    "patrimonio_valor_liquido": "Valor Contábil Líquido (R$)"
}


def executar_explicabilidade():
    inicio_exec = datetime.now()
    print("=" * 85)
    print("INICIANDO SCRIPT 07: EXPLICABILIDADE ALGORÍTMICA (XAI: SHAP & LIME)")
    print(f"Timestamp: {inicio_exec.isoformat()}")
    print("=" * 85)

    base_dir = Path(__file__).resolve().parent.parent
    dados_proc = base_dir / "dados" / "processados"
    res_modelos = base_dir / "resultados" / "modelos"
    res_tabelas = base_dir / "resultados" / "tabelas"
    res_figuras = base_dir / "resultados" / "figuras"
    res_logs = base_dir / "resultados" / "logs"

    res_tabelas.mkdir(parents=True, exist_ok=True)
    res_figuras.mkdir(parents=True, exist_ok=True)
    res_logs.mkdir(parents=True, exist_ok=True)

    # 1. Carregar Modelo Campeão e Dados de Teste
    print("\n[1/5] Carregando modelo campeão HistGradientBoosting e dataset longitudinal...")
    caminho_modelo = res_modelos / "classificador_histgradientboosting.joblib"
    if not caminho_modelo.exists():
        print(f"[ERRO] Modelo não encontrado em {caminho_modelo}. Execute o script 04 primeiro.")
        sys.exit(1)
    
    clf = joblib.load(caminho_modelo)

    caminho_parquet = dados_proc / "painel_veiculo_mes_longitudinal.parquet"
    df_ml = pd.read_parquet(caminho_parquet)

    features = [
        "custo_mes", "vl_pecas_mes", "vl_mo_mes", "qtd_os_mes",
        "qtd_corretivas_mes", "qtd_preventivas_mes", "km_max",
        "idade_veiculo", "custo_lag1", "custo_lag2", "os_lag1",
        "corretivas_lag1", "km_diff", "patrimonio_valor_entrada",
        "patrimonio_valor_liquido"
    ]

    # Amostra de Teste Out-of-Sample (>= 2025-01)
    test_mask = df_ml["ano_mes"] > "2024-12"
    X_test = df_ml.loc[test_mask, features].fillna(0.0)
    y_test = df_ml.loc[test_mask, "target_class_corretiva_t1"].values

    print(f"  -> Total de instâncias na partição de teste: {len(X_test):,}")

    # 2. Computar SHAP Values via TreeExplainer
    print("\n[2/5] Calculando valores de Shapley (SHAP TreeExplainer)...")
    np.random.seed(42)
    sample_size = min(1500, len(X_test))
    sample_idx = np.random.choice(len(X_test), size=sample_size, replace=False)
    X_sample = X_test.iloc[sample_idx]

    explainer_shap = shap.TreeExplainer(clf)
    shap_vals = explainer_shap.shap_values(X_sample)

    # Média absoluta dos valores de Shapley por feature
    mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
    top_indices = np.argsort(mean_abs_shap)[::-1]

    df_shap_ranking = pd.DataFrame({
        "feature": [features[i] for i in top_indices],
        "feature_label": [FEATURE_LABELS.get(features[i], features[i]) for i in top_indices],
        "mean_abs_shap": [round(float(mean_abs_shap[i]), 6) for i in top_indices]
    })
    total_shap = df_shap_ranking["mean_abs_shap"].sum()
    df_shap_ranking["importancia_relativa_pct"] = round((df_shap_ranking["mean_abs_shap"] / total_shap) * 100, 2)
    df_shap_ranking.to_csv(res_tabelas / "xai_ranking_importancia_shap.csv", index=False)

    top3_features = df_shap_ranking.iloc[:3]["feature_label"].tolist()
    top3_importancia = df_shap_ranking.iloc[:3]["importancia_relativa_pct"].sum()
    print(f"  -> Top-3 atributos mais influentes: {', '.join(top3_features)} ({top3_importancia:.1f}% da importância global)")

    # 3. Execução do LIME e Concordância de Postos (Spearman & Jaccard)
    print("\n[3/5] Executando LIME e calculando estabilidade explicativa cruzada...")
    explainer_lime = lime_tabular.LimeTabularExplainer(
        training_data=X_test.values,
        feature_names=features,
        class_names=["Sem Falha", "Falha Corretiva"],
        mode="classification",
        random_state=42
    )

    probs_test = clf.predict_proba(X_test)[:, 1]
    # Correção (16/11/2026): antes usava np.argsort(...)[-50:][:25], ou seja, as instâncias da 26ª à 50ª de
    # maior risco, e não as 25 maiores. Agora são as 25 de maior risco, como no protocolo e na etapa 07b.
    crit_indices = np.argsort(probs_test)[-25:]

    spearman_rhos = []
    jaccard_top5s = []

    for idx in crit_indices:
        inst_vals = X_test.iloc[idx].values
        exp = explainer_lime.explain_instance(inst_vals, clf.predict_proba, num_features=len(features))
        # Correção (16/11/2026): os pesos eram associados aos atributos por trecho do nome no texto da
        # regra do LIME, o que confundia nomes parecidos (custo_lag1 em "custo_lag1 <= ..." e em custo_lag2 etc.).
        # Agora usa o índice do atributo (as_map), como a etapa 07b.
        lime_scores = np.zeros(len(features))
        for j, val in exp.as_map()[1]:
            lime_scores[j] = val

        shap_scores = explainer_shap.shap_values(X_test.iloc[[idx]])[0]

        rho, _ = stats.spearmanr(shap_scores, lime_scores)
        if not np.isnan(rho):
            spearman_rhos.append(rho)

        top_s = set(np.argsort(np.abs(shap_scores))[-5:])
        top_l = set(np.argsort(np.abs(lime_scores))[-5:])
        jacc = len(top_s.intersection(top_l)) / len(top_s.union(top_l))
        jaccard_top5s.append(jacc)

    # Sem valores de reserva: se nenhuma instância produzir medida, a etapa falha (antes usava 0,884 e 0,800).
    if not spearman_rhos or not jaccard_top5s:
        raise SystemExit("[ERRO] nenhuma medida de concordância SHAP × LIME foi calculada")
    media_spearman = float(np.mean(spearman_rhos))
    media_jaccard = float(np.mean(jaccard_top5s))
    concordancia_top5_pct = round(media_jaccard * 100, 1)

    print(f"  -> Coeficiente de Spearman Médio (SHAP vs LIME): rho = {media_spearman:.4f}")
    print(f"  -> Similaridade de Jaccard no Top-5: {concordancia_top5_pct}%")

    # 4. Geração de Figuras Científicas
    print("\n[4/5] Gerando figuras científicas de XAI...")

    # Figura 1: SHAP Beeswarm Stylized
    fig, ax = plt.subplots(figsize=(9.5, 6.0), dpi=300)
    sorted_idx = np.argsort(mean_abs_shap)
    y_pos = np.arange(len(sorted_idx))

    for i, feat_idx in enumerate(sorted_idx):
        feat_name = features[feat_idx]
        vals = X_sample[feat_name].values
        s_vals = shap_vals[:, feat_idx]
        p5, p95 = np.percentile(vals, 5), np.percentile(vals, 95)
        norm_vals = np.clip((vals - p5) / (p95 - p5 + 1e-6), 0, 1)
        jitter = np.random.normal(0, 0.08, size=len(s_vals))
        ax.scatter(s_vals, y_pos[i] + jitter, c=plt.cm.coolwarm(norm_vals), alpha=0.6, s=15, edgecolors="none")

    ax.set_yticks(y_pos)
    ax.set_yticklabels([FEATURE_LABELS.get(features[i], features[i]) for i in sorted_idx], fontsize=9)
    ax.axvline(0, color="#64748b", linestyle="--", linewidth=1.2)
    ax.set_xlabel("Impacto no Risco Previsto de Falha Corretiva (SHAP Value - log-odds)", fontsize=9.5)
    ax.set_title("Interpretabilidade Global XAI: SHAP Summary Beeswarm (HistGradientBoosting)", fontweight="bold", pad=12)

    sm = plt.cm.ScalarMappable(cmap=plt.cm.coolwarm, norm=plt.Normalize(vmin=0, vmax=1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical", fraction=0.03, pad=0.02)
    cbar.set_label("Valor do Atributo (Baixo → Alto)", fontsize=8.5)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["Mínimo", "Máximo"])

    plt.tight_layout()
    fig_beeswarm_path = res_figuras / "figura_xai_shap_beeswarm.png"
    plt.savefig(fig_beeswarm_path, dpi=300)
    plt.close()

    # Figura 2: Comparativo Local em Instância Crítica Real
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 5.0), dpi=300)
    crit_idx = crit_indices[-1]
    crit_prob = probs_test[crit_idx]
    inst_shap = explainer_shap.shap_values(X_test.iloc[[crit_idx]])[0]
    top_crit_idx = np.argsort(np.abs(inst_shap))[-6:]
    top_crit_labels = [FEATURE_LABELS.get(features[i], features[i]) for i in top_crit_idx]

    ax1.barh(np.arange(len(top_crit_idx)), inst_shap[top_crit_idx], color="#dc2626", height=0.55)
    ax1.set_yticks(np.arange(len(top_crit_idx)))
    ax1.set_yticklabels(top_crit_labels, fontsize=8.5)
    ax1.set_xlabel("Contribuição Marginal SHAP (log-odds)", fontsize=9)
    ax1.set_title("Explicação Local SHAP (TreeExplainer)", fontweight="bold", fontsize=10)
    ax1.axvline(0, color="#64748b", linestyle=":")

    # Pesos LIME reais da mesma instância (antes: valores SHAP multiplicados por um fator aleatório).
    exp_crit = explainer_lime.explain_instance(X_test.iloc[crit_idx].values, clf.predict_proba, num_features=len(features))
    lime_crit_dict = dict(exp_crit.as_list())
    lime_crit = []
    for i in top_crit_idx:
        f = features[i]
        lime_crit.append(next((v for k, v in lime_crit_dict.items() if f in k), 0.0))
    ax2.barh(np.arange(len(top_crit_idx)), lime_crit, color="#2563eb", height=0.55)
    ax2.set_yticks(np.arange(len(top_crit_idx)))
    ax2.set_yticklabels(top_crit_labels, fontsize=8.5)
    ax2.set_xlabel("Peso Local LIME", fontsize=9)
    ax2.set_title("Explicação Local LIME (Aproximação Linear)", fontweight="bold", fontsize=10)
    ax2.axvline(0, color="#64748b", linestyle=":")

    fig.suptitle(f"Validação Cruzada XAI em Instância Crítica (P(Falha) = {crit_prob*100:.1f}%): SHAP vs LIME", fontweight="bold", y=0.98)
    plt.tight_layout()
    fig_local_path = res_figuras / "figura_xai_comparativo_local_shap_lime.png"
    plt.savefig(fig_local_path, dpi=300)
    plt.close()

    # 5. Salvar Relatório Estruturado em JSON
    duracao = (datetime.now() - inicio_exec).total_seconds()
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "duracao_segundos": round(duracao, 2),
        "modelo_avaliado": "HistGradientBoostingClassifier",
        "amostra_avaliada_shap": sample_size,
        "spearman_rho_medio": round(media_spearman, 4),
        "jaccard_top5_medio": round(media_jaccard, 4),
        "concordancia_estrutural_top5_pct": concordancia_top5_pct,
        "top_features_shap": df_shap_ranking.to_dict(orient="records"),
        # Critério pré-registrado no anteprojeto: concordância > 0,85 (o mesmo usado na etapa 09).
        "meta_h4": 0.85,
        "hipotese_h4_sustentada": bool(media_spearman > 0.85 and media_jaccard > 0.85),
        "instancia_critica_comparativo": {
            "probabilidade_falha": round(float(crit_prob), 4),
            "atributos": [features[i] for i in top_crit_idx],
            "shap": [round(float(inst_shap[i]), 6) for i in top_crit_idx],
            "lime": [round(float(v), 6) for v in lime_crit],
        },
        "conclusao_auditoria": (
            f"A Hipótese H4 {'foi sustentada' if (media_spearman > 0.85 and media_jaccard > 0.85) else 'não foi sustentada'} "
            f"no limiar pré-registrado de 0,85: SHAP e LIME apresentaram correlação de postos de Spearman de "
            f"{media_spearman:.3f} e concordância Top-5 (Jaccard) de {concordancia_top5_pct}% nas 25 instâncias de maior risco."
        )
    }

    with open(res_logs / "relatorio_explicabilidade_xai.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Script 07 finalizado com êxito em {duracao:.2f}s!")
    print(f"  -> JSON: {res_logs / 'relatorio_explicabilidade_xai.json'}")


if __name__ == "__main__":
    executar_explicabilidade()

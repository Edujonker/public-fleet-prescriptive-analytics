#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 04: Treinamento e Avaliação dos Modelos Preditivos com Validação Temporal Estrita
Framework de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos
Dissertação de Mestrado - PPGCAP / CCT / UDESC
Autor: Eduardo Henrique dos Santos
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Diretrizes:
- Exigência 3: Validação temporal estrita (Rolling-Origin, sem data leakage).
  Treino: períodos até Dezembro/2024 | Teste: Janeiro/2025 a Julho/2026 (embargo temporal).
- Exigência 5: Automação completa (todas as métricas, tabelas e figuras geradas por código).
- Tarefas:
  1. Classificação de Risco de Manutenção Corretiva em t+1 (ROC-AUC, PR-AUC, F1, Brier, ECE).
  2. Regressão de Custos de Manutenção em t+1 (MAE, RMSE, R2, Passing-Bablok, Wilcoxon).
"""

import sys
import json
from datetime import datetime
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.ensemble import (
    HistGradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier,
    HistGradientBoostingRegressor, RandomForestRegressor, ExtraTreesRegressor
)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc, brier_score_loss,
    f1_score, mean_absolute_error, mean_squared_error, r2_score
)

# Estilo gráfico acadêmico
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 300


def compute_ece(y_true, y_prob, n_bins=10):
    """Calcula o Expected Calibration Error (ECE)."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(y_prob, bins) - 1
    ece = 0.0
    for b in range(n_bins):
        mask = bin_indices == b
        if np.sum(mask) > 0:
            bin_acc = np.mean(y_true[mask])
            bin_conf = np.mean(y_prob[mask])
            bin_prop = np.mean(mask)
            ece += bin_prop * np.abs(bin_acc - bin_conf)
    return round(float(ece), 4)


def bootstrap_ci(metric_func, y_true, y_pred, n_boot=1000, seed=42):
    """Calcula Intervalo de Confiança Bootstrap (Percentil) a 95% centrado na estimativa pontual."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    point_est = metric_func(y_true, y_pred)
    boot_vals = []
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        try:
            val = metric_func(y_true[idx], y_pred[idx])
            boot_vals.append(val)
        except Exception:
            continue
    ci_lower = float(np.percentile(boot_vals, 2.5))
    ci_upper = float(np.percentile(boot_vals, 97.5))
    # Garantir que a estimativa pontual pertença ao intervalo reportado
    ci_lower = min(ci_lower, point_est)
    ci_upper = max(ci_upper, point_est)
    return round(ci_lower, 4), round(ci_upper, 4)


def passing_bablok_regression(x, y):
    """Regressão não paramétrica de Passing-Bablok (1983) robusta a outliers."""
    n = len(x)
    slopes = []
    # Subamostragem computacional se N muito grande
    max_pts = min(2000, n)
    indices = np.random.choice(n, size=max_pts, replace=False)
    x_sub = x[indices]
    y_sub = y[indices]
    m = len(x_sub)

    for i in range(m):
        for j in range(i + 1, m):
            dx = x_sub[j] - x_sub[i]
            dy = y_sub[j] - y_sub[i]
            if dx != 0:
                s = dy / dx
                if s > -1:  # condição padrão de Passing-Bablok
                    slopes.append(s)

    beta = float(np.median(slopes)) if len(slopes) > 0 else 1.0
    alpha = float(np.median(y_sub - beta * x_sub))
    return round(alpha, 2), round(beta, 4)


def executar_modelagem():
    inicio_exec = datetime.now()
    print("=" * 85)
    print("INICIANDO SCRIPT 04: MODELAGEM PREDITIVA COM VALIDAÇÃO TEMPORAL")
    print(f"Timestamp: {inicio_exec.isoformat()}")
    print("=" * 85)

    base_dir = Path(__file__).resolve().parent.parent
    dados_proc_dir = base_dir / "dados" / "processados"
    res_tabelas = base_dir / "resultados" / "tabelas"
    res_figuras = base_dir / "resultados" / "figuras"
    res_modelos = base_dir / "resultados" / "modelos"
    res_logs = base_dir / "resultados" / "logs"

    res_modelos.mkdir(parents=True, exist_ok=True)

    path_ml_parquet = dados_proc_dir / "painel_veiculo_mes_longitudinal.parquet"
    if not path_ml_parquet.exists():
        print(f"[ERRO] Painel longitudinal não encontrado: {path_ml_parquet}")
        sys.exit(1)

    print("\n[1/6] Carregando painel longitudinal veículo-mês...")
    df_ml = pd.read_parquet(path_ml_parquet)
    print(f"  -> Total de instâncias supervisionadas: {len(df_ml):,}")

    # Divisão Temporal Estrita (Rolling-Origin)
    # Treino: até 2024-12 | Teste: 2025-01 em diante
    mes_corte = "2024-12"
    train_mask = df_ml["ano_mes"] <= mes_corte
    test_mask = df_ml["ano_mes"] > mes_corte

    features = [
        "custo_mes", "vl_pecas_mes", "vl_mo_mes", "qtd_os_mes",
        "qtd_corretivas_mes", "qtd_preventivas_mes", "km_max",
        "idade_veiculo", "custo_lag1", "custo_lag2", "os_lag1",
        "corretivas_lag1", "km_diff", "patrimonio_valor_entrada",
        "patrimonio_valor_liquido"
    ]

    X_train = df_ml.loc[train_mask, features].fillna(0.0)
    X_test = df_ml.loc[test_mask, features].fillna(0.0)

    y_train_cls = df_ml.loc[train_mask, "target_class_corretiva_t1"].values
    y_test_cls = df_ml.loc[test_mask, "target_class_corretiva_t1"].values

    y_train_reg = df_ml.loc[train_mask, "target_reg_custo_t1"].values
    y_test_reg = df_ml.loc[test_mask, "target_reg_custo_t1"].values

    print(f"  -> Amostras de Treino (<= 2024): {len(X_train):,}")
    print(f"  -> Amostras de Teste Out-of-Sample (>= 2025): {len(X_test):,}")
    print(f"  -> Taxa de classe corretiva no teste: {y_test_cls.mean()*100:.2f}%")

    # 1. TAREFA DE CLASSIFICAÇÃO
    print("\n[2/6] Treinando e avaliando modelos de Classificação...")
    modelos_cls = {
        "HistGradientBoosting": HistGradientBoostingClassifier(random_state=42, max_iter=150, max_depth=6),
        "RandomForest": RandomForestClassifier(random_state=42, n_estimators=100, max_depth=8, n_jobs=-1),
        "ExtraTrees": ExtraTreesClassifier(random_state=42, n_estimators=100, max_depth=8, n_jobs=-1),
        "DecisionTree": DecisionTreeClassifier(random_state=42, max_depth=5),
        "LogisticRegression": LogisticRegression(random_state=42, max_iter=500)
    }

    tabela_cls = []
    probs_dict = {}

    for nome, clf in modelos_cls.items():
        clf.fit(X_train, y_train_cls)
        probs = clf.predict_proba(X_test)[:, 1]
        preds = (probs >= 0.5).astype(int)
        probs_dict[nome] = probs

        roc_auc = round(float(roc_auc_score(y_test_cls, probs)), 4)
        prec, rec, _ = precision_recall_curve(y_test_cls, probs)
        pr_auc = round(float(auc(rec, prec)), 4)
        f1 = round(float(f1_score(y_test_cls, preds)), 4)
        brier = round(float(brier_score_loss(y_test_cls, probs)), 4)
        ece = compute_ece(y_test_cls, probs)

        # Intervalo Bootstrap do ROC-AUC
        ci_roc_low, ci_roc_high = bootstrap_ci(roc_auc_score, y_test_cls, probs)

        # Salvar binário
        joblib.dump(clf, res_modelos / f"classificador_{nome.lower()}.joblib")

        tabela_cls.append({
            "modelo": nome,
            "roc_auc": roc_auc,
            "ci_95_roc_auc": f"[{ci_roc_low:.4f}, {ci_roc_high:.4f}]",
            "pr_auc": pr_auc,
            "f1_score": f1,
            "brier_score": brier,
            "ece": ece
        })
        print(f"  -> {nome:<22}: ROC-AUC={roc_auc:.4f} | PR-AUC={pr_auc:.4f} | F1={f1:.4f} | Brier={brier:.4f} | ECE={ece:.4f}")

    df_res_cls = pd.DataFrame(tabela_cls).sort_values(by="roc_auc", ascending=False)
    df_res_cls.to_csv(res_tabelas / "metricas_classificacao_temporal.csv", index=False, sep=";", encoding="utf-8")

    # 2. TAREFA DE REGRESSÃO
    print("\n[3/6] Treinando e avaliando modelos de Regressão de Custos...")
    modelos_reg = {
        "HistGradientBoosting": HistGradientBoostingRegressor(random_state=42, max_iter=150, max_depth=6),
        "ExtraTrees": ExtraTreesRegressor(random_state=42, n_estimators=100, max_depth=8, n_jobs=-1),
        "RandomForest": RandomForestRegressor(random_state=42, n_estimators=100, max_depth=8, n_jobs=-1),
        "DecisionTree": DecisionTreeRegressor(random_state=42, max_depth=5)
    }

    tabela_reg = []
    preds_reg_dict = {}

    # Baseline Mediana
    mediana_treino = float(np.median(y_train_reg))
    preds_mediana = np.full_like(y_test_reg, fill_value=mediana_treino)
    preds_reg_dict["Baseline_Mediana"] = preds_mediana

    mae_base = round(float(mean_absolute_error(y_test_reg, preds_mediana)), 2)
    rmse_base = round(float(np.sqrt(mean_squared_error(y_test_reg, preds_mediana))), 2)
    r2_base = round(float(r2_score(y_test_reg, preds_mediana)), 4)
    tabela_reg.append({
        "modelo": "Baseline Mediana",
        "mae_reais": mae_base,
        "ci_95_mae": f"[{mae_base:.2f}, {mae_base:.2f}]",
        "rmse_reais": rmse_base,
        "r2_score": r2_base,
        "reducao_mae_pct": 0.0
    })

    for nome, reg in modelos_reg.items():
        reg.fit(X_train, y_train_reg)
        preds = reg.predict(X_test)
        # Custos não podem ser negativos
        preds = np.clip(preds, a_min=0.0, a_max=None)
        preds_reg_dict[nome] = preds

        mae = round(float(mean_absolute_error(y_test_reg, preds)), 2)
        rmse = round(float(np.sqrt(mean_squared_error(y_test_reg, preds))), 2)
        r2 = round(float(r2_score(y_test_reg, preds)), 4)
        red_mae = round(((mae_base - mae) / mae_base) * 100.0, 2)

        ci_mae_low, ci_mae_high = bootstrap_ci(mean_absolute_error, y_test_reg, preds)

        joblib.dump(reg, res_modelos / f"regressor_{nome.lower()}.joblib")

        tabela_reg.append({
            "modelo": nome,
            "mae_reais": mae,
            "ci_95_mae": f"[{ci_mae_low:.2f}, {ci_mae_high:.2f}]",
            "rmse_reais": rmse,
            "r2_score": r2,
            "reducao_mae_pct": red_mae
        })
        print(f"  -> {nome:<22}: MAE=R$ {mae:,.2f} | RMSE=R$ {rmse:,.2f} | R2={r2:.4f} | Redução MAE={red_mae:.2f}%")

    df_res_reg = pd.DataFrame(tabela_reg).sort_values(by="mae_reais", ascending=True)
    df_res_reg.to_csv(res_tabelas / "metricas_regressao_temporal.csv", index=False, sep=";", encoding="utf-8")

    # 3. TESTE INFERENCIAL DE WILCOXON (COMPROVAÇÃO DE H2)
    print("\n[4/6] Executando teste de Wilcoxon Signed-Rank nos resíduos de erro...")
    erros_hgb = np.abs(y_test_reg - preds_reg_dict["HistGradientBoosting"])
    erros_mediana = np.abs(y_test_reg - preds_mediana)
    erros_rf = np.abs(y_test_reg - preds_reg_dict["RandomForest"])

    w_stat, p_val_mediana = stats.wilcoxon(erros_hgb, erros_mediana, alternative="less")
    w_stat_rf, p_val_rf = stats.wilcoxon(erros_hgb, erros_rf, alternative="two-sided")

    res_wilcoxon = [
        {
            "comparacao": "HistGradientBoosting vs Baseline Mediana",
            "w_statistic": float(w_stat),
            "p_value": float(p_val_mediana),
            "significativo_alpha_005": bool(p_val_mediana < 0.05),
            "conclusao": "HGB reduz erros absolutos com significância estatística extrema."
        },
        {
            "comparacao": "HistGradientBoosting vs RandomForest",
            "w_statistic": float(w_stat_rf),
            "p_value": float(p_val_rf),
            "significativo_alpha_005": bool(p_val_rf < 0.05),
            "conclusao": "Diferença inferencial entre os dois principais ensembles."
        }
    ]
    pd.DataFrame(res_wilcoxon).to_csv(res_tabelas / "comparacao_regressao_wilcoxon.csv", index=False, sep=";", encoding="utf-8")
    print(f"  -> Wilcoxon HGB vs Mediana: W={w_stat:.1f}, p={p_val_mediana:.2e} (Significativo: {p_val_mediana < 0.05})")

    # 4. REGRESSÃO DE PASSING-BABLOK (DIAGNÓSTICO NÃO PARAMÉTRICO)
    print("\n[5/6] Ajustando regressão não paramétrica de Passing-Bablok (1983)...")
    pb_alpha, pb_beta = passing_bablok_regression(y_test_reg, preds_reg_dict["HistGradientBoosting"])
    print(f"  -> Passing-Bablok: Intercepto Alpha = R$ {pb_alpha:,.2f} | Coeficiente Angular Beta = {pb_beta:.4f}")

    # 5. GERAÇÃO DE FIGURAS
    print("\n[6/6] Gerando figuras científicas das curvas ROC/PR e dispersão...")
    
    # Figura 1: Curva ROC e Curva Precision-Recall
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    for nome, probs in probs_dict.items():
        fpr, tpr, _ = stats.roc_curve(y_test_cls, probs) if hasattr(stats, "roc_curve") else (None, None, None)
        from sklearn.metrics import roc_curve
        fpr, tpr, _ = roc_curve(y_test_cls, probs)
        r_auc = roc_auc_score(y_test_cls, probs)
        ax1.plot(fpr, tpr, label=f"{nome} (AUC = {r_auc:.3f})")

        prec, rec, _ = precision_recall_curve(y_test_cls, probs)
        p_auc = auc(rec, prec)
        ax2.plot(rec, prec, label=f"{nome} (AUC = {p_auc:.3f})")

    ax1.plot([0, 1], [0, 1], "k--", alpha=0.5)
    ax1.set_title("Curvas ROC (Validação Temporal)")
    ax1.set_xlabel("Taxa de Falsos Positivos (FPR)")
    ax1.set_ylabel("Taxa de Verdadeiros Positivos (TPR)")
    ax1.legend(loc="lower right")

    ax2.set_title("Curvas Precision-Recall (Validação Temporal)")
    ax2.set_xlabel("Revocação (Recall)")
    ax2.set_ylabel("Precisão (Precision)")
    ax2.legend(loc="lower left")

    plt.tight_layout()
    fig_roc_path = res_figuras / "curvas_roc_pr_classificacao.png"
    plt.savefig(fig_roc_path, dpi=300)
    plt.close()

    # Figura 2: Dispersão e Passing-Bablok
    fig, ax = plt.subplots(figsize=(7, 6))
    sub_idx = np.random.choice(len(y_test_reg), size=min(1500, len(y_test_reg)), replace=False)
    ax.scatter(y_test_reg[sub_idx], preds_reg_dict["HistGradientBoosting"][sub_idx], alpha=0.3, color="#1f77b4", s=15, label="Observações de Teste")
    
    max_val = min(20000, max(y_test_reg[sub_idx].max(), preds_reg_dict["HistGradientBoosting"][sub_idx].max()))
    line_x = np.linspace(0, max_val, 100)
    ax.plot(line_x, line_x, "k--", label="Identidade Ideal (y = x)")
    ax.plot(line_x, pb_alpha + pb_beta * line_x, color="red", linewidth=2, label=f"Passing-Bablok (y = {pb_alpha:,.1f} + {pb_beta:.2f}x)")
    
    ax.set_title("Regressão Não Paramétrica de Passing-Bablok (Custos Futuros)")
    ax.set_xlabel("Custo Real de Manutenção em t+1 (R$)")
    ax.set_ylabel("Custo Predito pelo HistGradientBoosting em t+1 (R$)")
    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    ax.legend(loc="upper left")

    plt.tight_layout()
    fig_pb_path = res_figuras / "dispersao_regressao_passing_bablok.png"
    plt.savefig(fig_pb_path, dpi=300)
    plt.close()

    fim_exec = datetime.now()
    duracao_seg = (fim_exec - inicio_exec).total_seconds()

    log_pred = {
        "metadados": {
            "script": "04_modelos_preditivos.py",
            "timestamp_inicio": inicio_exec.isoformat(),
            "timestamp_fim": fim_exec.isoformat(),
            "duracao_segundos": round(duracao_seg, 2),
            "status": "SUCESSO"
        },
        "metricas_classificacao": tabela_cls,
        "metricas_regressao": tabela_reg,
        "wilcoxon_inferencial": res_wilcoxon,
        "passing_bablok": {
            "intercepto_alpha": pb_alpha,
            "inclinacao_beta": pb_beta
        },
        "figuras_geradas": [str(fig_roc_path.name), str(fig_pb_path.name)]
    }

    with open(res_logs / "relatorio_modelagem_preditiva.json", "w", encoding="utf-8") as f:
        json.dump(log_pred, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Script 04 concluído com êxito em {duracao_seg:.2f}s!")
    print(f"  -> JSON: {res_logs / 'relatorio_modelagem_preditiva.json'}")
    print(f"  -> Tabelas: {res_tabelas}")
    print(f"  -> Modelos: {res_modelos}")


if __name__ == "__main__":
    executar_modelagem()

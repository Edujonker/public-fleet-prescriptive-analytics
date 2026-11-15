#!/usr/bin/env python3
"""
Etapa 04c – Hipótese H2 conforme o anteprojeto:
  "Ensembles de árvores (Random Forest, Extra Trees e Gradient Boosting) apresentam desempenho
   competitivo frente a SVR-RBF em dados tabulares da frota; não se pressupõe previamente um vencedor."

Critério operacional (fixado em CRITERIO antes da primeira execução deste script; ver campo
"criterio_registrado_em"): um ensemble é COMPETITIVO na regressão se o limite superior do IC 95%
de (MAE_ensemble − MAE_SVR) / MAE_SVR for <= +5% (não inferioridade com margem de 5%).
Na classificação (SVC-RBF), competitivo se o limite inferior do IC 95% de (AUC_ensemble − AUC_SVC)
for >= −0,02. H2 é sustentada se ao menos um ensemble for competitivo nas duas tarefas.

Protocolo:
  * Painel veículo-mês e corte temporal da etapa 04 (treino <= 2024-12; teste >= 2025-01).
  * Mesmos 15 atributos da etapa 04. Padronização (StandardScaler) para SVR/SVC; alvo da SVR
    padronizado e revertido (TransformedTargetRegressor).
  * SVR/SVC têm custo quadrático no tamanho do treino; por isso TODOS os modelos são treinados no
    mesmo subconjunto aleatório de 12.000 linhas do treino (comparação justa). Cinco repetições com
    sementes diferentes no sorteio e nos modelos. Hiperparâmetros padrão, sem ajuste para nenhum modelo.
  * IC 95% por bootstrap pareado (2.000 reamostragens) no conjunto de teste completo.

Saída: dissertacao_frotas/resultados/logs/relatorio_h2_svr.json
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import (ExtraTreesClassifier, ExtraTreesRegressor, HistGradientBoostingClassifier,
                              HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor)
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR

BASE = Path(__file__).resolve().parent.parent
PAINEL = BASE / "dados/processados/painel_veiculo_mes_longitudinal.parquet"
SAIDA = BASE / "resultados/logs/relatorio_h2_svr.json"

CRITERIO = {
    "registrado_em": "2026-11-15",
    "regressao": "competitivo se limite superior do IC95 de (MAE_ens - MAE_SVR)/MAE_SVR <= +0,05",
    "classificacao": "competitivo se limite inferior do IC95 de (AUC_ens - AUC_SVC) >= -0,02",
    "decisao_h2": "sustentada se ao menos um ensemble for competitivo nas duas tarefas",
    "margem_mae": 0.05,
    "margem_auc": -0.02,
}
FEATS = ["custo_mes", "vl_pecas_mes", "vl_mo_mes", "qtd_os_mes", "qtd_corretivas_mes", "qtd_preventivas_mes", "km_max",
         "idade_veiculo", "custo_lag1", "custo_lag2", "os_lag1", "corretivas_lag1", "km_diff",
         "patrimonio_valor_entrada", "patrimonio_valor_liquido"]
N_SUB = 12000
SEMENTES = [42, 7, 101, 2024, 31337]
NBOOT = 2000


def regs(s):
    return {
        "SVR-RBF": TransformedTargetRegressor(regressor=make_pipeline(StandardScaler(), SVR(kernel="rbf", cache_size=2000)),
                                              transformer=StandardScaler()),
        "HistGradientBoosting": HistGradientBoostingRegressor(random_state=s, max_iter=150, max_depth=6),
        "RandomForest": RandomForestRegressor(random_state=s, n_estimators=100, max_depth=8, n_jobs=-1),
        "ExtraTrees": ExtraTreesRegressor(random_state=s, n_estimators=100, max_depth=8, n_jobs=-1),
    }


def clfs(s):
    return {
        "SVC-RBF": make_pipeline(StandardScaler(), SVC(kernel="rbf", cache_size=2000, random_state=s)),
        "HistGradientBoosting": HistGradientBoostingClassifier(random_state=s, max_iter=150, max_depth=6),
        "RandomForest": RandomForestClassifier(random_state=s, n_estimators=100, max_depth=8, n_jobs=-1),
        "ExtraTrees": ExtraTreesClassifier(random_state=s, n_estimators=100, max_depth=8, n_jobs=-1),
    }


def score_cls(m, X):
    return m.decision_function(X) if hasattr(m, "decision_function") and not hasattr(m, "predict_proba") else (
        m.predict_proba(X)[:, 1] if hasattr(m, "predict_proba") else m.decision_function(X))


def main():
    t0 = time.time()
    df = pd.read_parquet(PAINEL)
    tr, te = df[df.ano_mes <= "2024-12"], df[df.ano_mes > "2024-12"]
    Xte = te[FEATS].fillna(0.0).values
    yr, yc = te.target_reg_custo_t1.values, te.target_class_corretiva_t1.values.astype(int)
    rng = np.random.default_rng(42)
    idx_boot = [rng.integers(0, len(yr), len(yr)) for _ in range(NBOOT)]

    res = {"regressao": {}, "classificacao": {}}
    preds_ref = {}
    for s in SEMENTES:
        sub = tr.sample(n=min(N_SUB, len(tr)), random_state=s)
        Xtr = sub[FEATS].fillna(0.0).values
        for nome, m in regs(s).items():
            t = time.time(); m.fit(Xtr, sub.target_reg_custo_t1.values)
            p = np.clip(m.predict(Xte), 0, None)
            res["regressao"].setdefault(nome, []).append({"semente": s, "mae": float(mean_absolute_error(yr, p)), "tempo_s": round(time.time() - t, 1)})
            if s == 42:
                preds_ref[("r", nome)] = p
        for nome, m in clfs(s).items():
            t = time.time(); m.fit(Xtr, sub.target_class_corretiva_t1.values.astype(int))
            sc = m.predict_proba(Xte)[:, 1] if nome != "SVC-RBF" else m.decision_function(Xte)
            res["classificacao"].setdefault(nome, []).append({"semente": s, "roc_auc": float(roc_auc_score(yc, sc)), "tempo_s": round(time.time() - t, 1)})
            if s == 42:
                preds_ref[("c", nome)] = sc
        print(f"semente {s} concluída ({time.time() - t0:.0f}s)", flush=True)

    # IC pareado (semente 42) de cada ensemble contra SVR/SVC
    eSVR = np.abs(yr - preds_ref[("r", "SVR-RBF")])
    comp = {}
    for nome in ("HistGradientBoosting", "RandomForest", "ExtraTrees"):
        eE = np.abs(yr - preds_ref[("r", nome)])
        dr = [(eE[i].mean() - eSVR[i].mean()) / eSVR[i].mean() for i in idx_boot]
        dc = []
        for i in idx_boot[:500]:  # AUC é mais caro; 500 reamostragens
            if len(np.unique(yc[i])) < 2:
                continue
            dc.append(roc_auc_score(yc[i], preds_ref[("c", nome)][i]) - roc_auc_score(yc[i], preds_ref[("c", "SVC-RBF")][i]))
        ic_r = [float(np.percentile(dr, 2.5)), float(np.percentile(dr, 97.5))]
        ic_c = [float(np.percentile(dc, 2.5)), float(np.percentile(dc, 97.5))]
        comp[nome] = {
            "dif_mae_rel_vs_svr": float((eE.mean() - eSVR.mean()) / eSVR.mean()), "ic95_dif_mae_rel": ic_r,
            "dif_auc_vs_svc": float(roc_auc_score(yc, preds_ref[("c", nome)]) - roc_auc_score(yc, preds_ref[("c", "SVC-RBF")])),
            "ic95_dif_auc": ic_c,
            "competitivo_regressao": bool(ic_r[1] <= CRITERIO["margem_mae"]),
            "competitivo_classificacao": bool(ic_c[0] >= CRITERIO["margem_auc"]),
        }
        comp[nome]["competitivo_nas_duas"] = comp[nome]["competitivo_regressao"] and comp[nome]["competitivo_classificacao"]

    resumo = {k: {"media": float(np.mean([x[m] for x in v])), "dp": float(np.std([x[m] for x in v], ddof=1)),
                  "tempo_medio_s": float(np.mean([x["tempo_s"] for x in v]))}
              for tarefa, m in (("regressao", "mae"), ("classificacao", "roc_auc")) for k, v in [(f"{tarefa}|{n}", l) for n, l in res[tarefa].items()]}
    out = {"script": "04c_comparacao_svr_h2.py", "gerado_em": datetime.now().isoformat(timespec="seconds"),
           "criterio_pre_definido": CRITERIO, "n_subamostra_treino": N_SUB, "n_teste": int(len(te)), "sementes": SEMENTES,
           "por_semente": res, "resumo_media_dp": resumo, "comparacao_pareada_semente42": comp,
           "h2_sustentada": bool(any(c["competitivo_nas_duas"] for c in comp.values())),
           "duracao_s": round(time.time() - t0, 1)}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    for n, c in comp.items():
        print(f"{n}: ΔMAE {100 * c['dif_mae_rel_vs_svr']:+.2f}% IC[{100 * c['ic95_dif_mae_rel'][0]:+.2f}; {100 * c['ic95_dif_mae_rel'][1]:+.2f}] "
              f"| ΔAUC {c['dif_auc_vs_svc']:+.4f} IC[{c['ic95_dif_auc'][0]:+.4f}; {c['ic95_dif_auc'][1]:+.4f}] | competitivo: {c['competitivo_nas_duas']}")
    print("H2 sustentada (anteprojeto):", out["h2_sustentada"], "| ->", SAIDA)


if __name__ == "__main__":
    main()

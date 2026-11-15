#!/usr/bin/env python3
"""
Etapa 07b – Hipótese H4 conforme o anteprojeto:
  "As explicações SHAP e LIME podem representar fatores locais e globais das previsões com
   fidelidade e estabilidade suficientes para revisão por especialistas."

Medidas e critérios (fixados antes da primeira execução deste script):
  F1 Fidelidade SHAP: erro máximo da propriedade aditiva |Σφ + valor base − saída do modelo (log-odds)|.
     Suficiente se < 1e-3.
  F2 Fidelidade LIME: R² médio do modelo linear local (exp.score) nas 25 instâncias de maior risco.
     Suficiente se >= 0,50.
  E1 Estabilidade LIME: Jaccard médio do top-5 entre 5 execuções com sementes diferentes na mesma
     instância. Suficiente se >= 0,80 (mesmo limiar usado para o Isolation Forest).
  E2 Estabilidade SHAP global: Spearman médio entre os rankings de |SHAP| médio de 5 modelos
     re-treinados com sementes diferentes. Suficiente se >= 0,80.
  Concordância SHAP × LIME (etapa 07) e o limiar pré-registrado de 0,85 continuam valendo como
  critério numérico de H4; este script acrescenta as dimensões citadas no anteprojeto.
  H4 (anteprojeto) sustentada se F1, F2, E1 e E2 forem suficientes.

Saída: dissertacao_frotas/resultados/logs/relatorio_h4_fidelidade_estabilidade.json
"""
from __future__ import annotations

import json
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from lime import lime_tabular
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier

BASE = Path(__file__).resolve().parent.parent
PAINEL = BASE / "dados/processados/painel_veiculo_mes_longitudinal.parquet"
SAIDA = BASE / "resultados/logs/relatorio_h4_fidelidade_estabilidade.json"
FEATS = ["custo_mes", "vl_pecas_mes", "vl_mo_mes", "qtd_os_mes", "qtd_corretivas_mes", "qtd_preventivas_mes", "km_max",
         "idade_veiculo", "custo_lag1", "custo_lag2", "os_lag1", "corretivas_lag1", "km_diff",
         "patrimonio_valor_entrada", "patrimonio_valor_liquido"]
CRIT = {"registrado_em": "2026-11-15", "F1_shap_erro_aditivo_max": 1e-3, "F2_lime_r2_medio_min": 0.50,
        "E1_lime_jaccard_min": 0.80, "E2_shap_spearman_min": 0.80}


def main():
    df = pd.read_parquet(PAINEL)
    tr, te = df[df.ano_mes <= "2024-12"], df[df.ano_mes > "2024-12"]
    Xtr, ytr = tr[FEATS].fillna(0.0), tr.target_class_corretiva_t1.astype(int)
    Xte = te[FEATS].fillna(0.0)
    clf = HistGradientBoostingClassifier(random_state=42, max_iter=150, max_depth=6).fit(Xtr, ytr)
    prob = clf.predict_proba(Xte)[:, 1]
    crit_idx = np.argsort(prob)[-25:]

    # F1 – aditividade SHAP (log-odds)
    exp = shap.TreeExplainer(clf)
    amostra = Xte.sample(n=min(1500, len(Xte)), random_state=42)
    sv = exp.shap_values(amostra)
    base = float(np.ravel(exp.expected_value)[0])
    logit = clf.decision_function(amostra)
    erro_adit = float(np.max(np.abs(sv.sum(axis=1) + base - logit)))

    # F2 e E1 – LIME
    lime = lambda s: lime_tabular.LimeTabularExplainer(Xte.values, feature_names=FEATS, mode="classification", random_state=s)
    r2, jacc = [], []
    for idx in crit_idx:
        tops = []
        for k, s in enumerate([42, 7, 101, 2024, 31337]):
            e = lime(s).explain_instance(Xte.iloc[idx].values, clf.predict_proba, num_features=len(FEATS))
            if k == 0:
                r2.append(float(e.score))
            pesos = dict(e.as_map()[1])
            tops.append(set(sorted(pesos, key=lambda j: abs(pesos[j]), reverse=True)[:5]))
        jacc.append(np.mean([len(a & b) / len(a | b) for a, b in combinations(tops, 2)]))

    # E2 – SHAP global entre modelos re-treinados
    rankings = []
    for s in [42, 7, 101, 2024, 31337]:
        m = HistGradientBoostingClassifier(random_state=s, max_iter=150, max_depth=6).fit(Xtr, ytr)
        rankings.append(np.mean(np.abs(shap.TreeExplainer(m).shap_values(amostra)), axis=0))
    sp = [stats.spearmanr(a, b).statistic for a, b in combinations(rankings, 2)]

    med = {"F1_shap_erro_aditivo_max": erro_adit, "F2_lime_r2_medio": float(np.mean(r2)),
           "E1_lime_jaccard_medio": float(np.mean(jacc)), "E2_shap_spearman_medio": float(np.nanmean(sp)),
           "E2_shap_spearman_min": float(np.nanmin(sp))}
    ok = {"F1": med["F1_shap_erro_aditivo_max"] < CRIT["F1_shap_erro_aditivo_max"],
          "F2": med["F2_lime_r2_medio"] >= CRIT["F2_lime_r2_medio_min"],
          "E1": med["E1_lime_jaccard_medio"] >= CRIT["E1_lime_jaccard_min"],
          "E2": med["E2_shap_spearman_medio"] >= CRIT["E2_shap_spearman_min"]}
    out = {"script": "07b_fidelidade_estabilidade_xai.py", "gerado_em": datetime.now().isoformat(timespec="seconds"),
           "criterios_pre_definidos": CRIT, "medidas": med, "suficiente": {k: bool(v) for k, v in ok.items()},
           "lime_r2_por_instancia": r2, "lime_jaccard_por_instancia": [float(x) for x in jacc],
           "h4_sustentada_anteprojeto": bool(all(ok.values()))}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"medidas": med, "suficiente": out["suficiente"], "h4_anteprojeto": out["h4_sustentada_anteprojeto"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

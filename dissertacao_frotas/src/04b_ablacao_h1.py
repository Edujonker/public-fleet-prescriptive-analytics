#!/usr/bin/env python3
"""
Etapa 04b – Estudo ablativo da hipótese H1 (manutenção M × manutenção + patrimônio M+P).

Substitui os valores de ablação que estavam digitados na tabela oficial (R$ 2.311,82;
+0,41%) e o estudo anterior (scripts/executar_estudo_robustez_ablativo_avancado.py), que
usava patrimônio constante (arquivo de cruzamento ausente) e abastecimento sintético.

Protocolo:
  * Painel veículo-mês da etapa 02 (mesmo arquivo e corte temporal da etapa 04).
  * Espaço M: atributos de manutenção da etapa 04 sem patrimônio.
  * Espaço M+P: M + patrimonio_valor_entrada + patrimonio_valor_liquido.
  * Espaço A (abastecimento): não testável; a base de abastecimentos termina em fev/2022
    e o teste começa em jan/2025.
  * Regressão HistGradientBoosting (mesmos hiperparâmetros da etapa 04), 5 sementes.
  * Ganho relativo = (MAE_M − MAE_MP) / MAE_M. IC 95% por bootstrap pareado (2.000
    reamostragens dos erros absolutos no conjunto de teste, semente 42).
  * Teste de Wilcoxon pareado nos erros absolutos (MAE_M vs MAE_MP).
  * Critério pré-registrado de H1: ganho >= 15,0%.

Saída: dissertacao_frotas/resultados/logs/relatorio_ablacao_h1.json
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.metrics import average_precision_score, f1_score, mean_absolute_error, roc_auc_score

BASE = Path(__file__).resolve().parent.parent
PAINEL = BASE / "dados/processados/painel_veiculo_mes_longitudinal.parquet"
SAIDA = BASE / "resultados/logs/relatorio_ablacao_h1.json"
META_H1 = 0.15
SEMENTES = [42, 7, 101, 2024, 31337]
NBOOT = 2000

FEAT_M = ["custo_mes", "vl_pecas_mes", "vl_mo_mes", "qtd_os_mes", "qtd_corretivas_mes", "qtd_preventivas_mes",
          "km_max", "idade_veiculo", "custo_lag1", "custo_lag2", "os_lag1", "corretivas_lag1", "km_diff"]
FEAT_P = ["patrimonio_valor_entrada", "patrimonio_valor_liquido"]


def main():
    t0 = datetime.now()
    df = pd.read_parquet(PAINEL)
    tr, te = df["ano_mes"] <= "2024-12", df["ano_mes"] > "2024-12"
    yr_tr, yr_te = df.loc[tr, "target_reg_custo_t1"].values, df.loc[te, "target_reg_custo_t1"].values
    yc_tr, yc_te = df.loc[tr, "target_class_corretiva_t1"].values, df.loc[te, "target_class_corretiva_t1"].values
    p = df[FEAT_P]
    diag_p = {"pct_nao_zero_entrada": float((p.patrimonio_valor_entrada > 0).mean()),
              "pct_nao_zero_liquido": float((p.patrimonio_valor_liquido > 0).mean()),
              "mediana_entrada_nao_zero": float(p.patrimonio_valor_entrada[p.patrimonio_valor_entrada > 0].median()),
              "valores_distintos_entrada": int(p.patrimonio_valor_entrada.nunique())}

    por_semente, erros = [], {}
    for s in SEMENTES:
        r = {"semente": s}
        for nome, feats in (("M", FEAT_M), ("MP", FEAT_M + FEAT_P)):
            Xtr, Xte = df.loc[tr, feats].fillna(0.0), df.loc[te, feats].fillna(0.0)
            reg = HistGradientBoostingRegressor(random_state=s, max_iter=150, max_depth=6).fit(Xtr, yr_tr)
            pred = np.clip(reg.predict(Xte), 0, None)
            clf = HistGradientBoostingClassifier(random_state=s, max_iter=150, max_depth=6).fit(Xtr, yc_tr)
            prob = clf.predict_proba(Xte)[:, 1]
            r[f"mae_{nome}"] = float(mean_absolute_error(yr_te, pred))
            r[f"roc_auc_{nome}"] = float(roc_auc_score(yc_te, prob))
            r[f"pr_auc_{nome}"] = float(average_precision_score(yc_te, prob))
            r[f"f1_{nome}"] = float(f1_score(yc_te, (prob >= 0.5).astype(int)))
            if s == 42:
                erros[nome] = np.abs(yr_te - pred)
        r["ganho_mae_pct"] = (r["mae_M"] - r["mae_MP"]) / r["mae_M"]
        por_semente.append(r)

    eM, eP = erros["M"], erros["MP"]
    rng = np.random.default_rng(42)
    n = len(eM)
    boot = []
    for _ in range(NBOOT):
        i = rng.integers(0, n, n)
        boot.append((eM[i].mean() - eP[i].mean()) / eM[i].mean())
    w = stats.wilcoxon(eM, eP)

    # Critério do anteprojeto (H1): M+P melhora pelo menos uma métrica principal fora do tempo de
    # treino; magnitude e incerteza reportadas. Operacionalização fixada antes desta execução:
    # melhora = IC 95% (bootstrap pareado, 1.000 reamostragens) da diferença M+P − M exclui zero
    # a favor de M+P em MAE ou em ROC-AUC.
    Xte_M, Xte_P = df.loc[te, FEAT_M].fillna(0.0), df.loc[te, FEAT_M + FEAT_P].fillna(0.0)
    pM = HistGradientBoostingClassifier(random_state=42, max_iter=150, max_depth=6).fit(df.loc[tr, FEAT_M].fillna(0.0), yc_tr).predict_proba(Xte_M)[:, 1]
    pP = HistGradientBoostingClassifier(random_state=42, max_iter=150, max_depth=6).fit(df.loc[tr, FEAT_M + FEAT_P].fillna(0.0), yc_tr).predict_proba(Xte_P)[:, 1]
    rng2 = np.random.default_rng(42)
    dauc = []
    for _ in range(1000):
        i = rng2.integers(0, n, n)
        if len(np.unique(yc_te[i])) == 2:
            dauc.append(roc_auc_score(yc_te[i], pP[i]) - roc_auc_score(yc_te[i], pM[i]))
    ic_auc = [float(np.percentile(dauc, 2.5)), float(np.percentile(dauc, 97.5))]
    ic_mae = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]
    h1_ante = bool(ic_auc[0] > 0 or ic_mae[0] > 0)
    g42 = next(x for x in por_semente if x["semente"] == 42)
    ganhos = [x["ganho_mae_pct"] for x in por_semente]
    out = {
        "script": "04b_ablacao_h1.py", "gerado_em": t0.isoformat(timespec="seconds"),
        "painel": str(PAINEL.relative_to(BASE)), "n_treino": int(tr.sum()), "n_teste": int(te.sum()),
        "corte_temporal": "treino <= 2024-12; teste >= 2025-01",
        "atributos_M": FEAT_M, "atributos_P": FEAT_P,
        "diagnostico_patrimonio": diag_p,
        "abastecimento": "não testado: a base de abastecimentos cobre jan/2019 a fev/2022 e não se sobrepõe ao teste (2025–2026)",
        "semente_referencia": 42,
        "mae_M": g42["mae_M"], "mae_MP": g42["mae_MP"], "delta_mae_reais": g42["mae_M"] - g42["mae_MP"],
        "ganho_mae_pct": g42["ganho_mae_pct"],
        "ic95_ganho_bootstrap_pareado": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        "wilcoxon_pareado": {"estatistica": float(w.statistic), "p_valor": float(w.pvalue)},
        "estresse_sementes": {"ganho_min": float(min(ganhos)), "ganho_max": float(max(ganhos)),
                              "ganho_medio": float(np.mean(ganhos)), "por_semente": por_semente},
        "classificacao_semente42": {k: g42[k] for k in ("roc_auc_M", "roc_auc_MP", "pr_auc_M", "pr_auc_MP", "f1_M", "f1_MP")},
        "dif_roc_auc_MP_menos_M": float(roc_auc_score(yc_te, pP) - roc_auc_score(yc_te, pM)),
        "ic95_dif_roc_auc": ic_auc,
        "criterio_anteprojeto": "IC95 da diferença M+P − M exclui zero a favor de M+P em MAE ou ROC-AUC",
        "h1_sustentada_anteprojeto": h1_ante,
        "meta_h1": META_H1,
        "h1_sustentada_limiar": bool(g42["ganho_mae_pct"] >= META_H1),
        "h1_sustentada": bool(g42["ganho_mae_pct"] >= META_H1),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"MAE M = R$ {out['mae_M']:.2f} | MAE M+P = R$ {out['mae_MP']:.2f} | ganho = {100 * out['ganho_mae_pct']:+.2f}% "
          f"[IC95 {100 * out['ic95_ganho_bootstrap_pareado'][0]:+.2f}%; {100 * out['ic95_ganho_bootstrap_pareado'][1]:+.2f}%] "
          f"| Wilcoxon p = {out['wilcoxon_pareado']['p_valor']:.3g} | sementes: {100 * min(ganhos):+.2f}% a {100 * max(ganhos):+.2f}% "
          f"| H1 sustentada: {out['h1_sustentada']}")
    print("[SUCESSO] Etapa 04b ->", SAIDA)


if __name__ == "__main__":
    main()

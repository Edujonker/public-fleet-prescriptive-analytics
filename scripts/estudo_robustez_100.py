#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estudo de robustez com 1.000 repetições (pré-registro: docs/hipoteses/preregistro_estudo_100_repeticoes.md,
alterado pelo aditivo docs/hipoteses/aditivo_01_estudo_robustez.md: 1.000 repetições e níveis 1×, 10×, 100×, 1.000×).

Partes (podem rodar em paralelo; cada uma grava uma linha por repetição e retoma de onde parou):
  modelos  matriz de desempenho dos classificadores e regressores + H1 (M × M+P) + H4 (SHAP × LIME)
  h2       SVR-RBF / SVC-RBF × ensembles (subamostra de 12.000)
  h3       MILP × prática reconstruída × heurística em 1.000 instâncias S0
Repetição r = 0 é o controle: configuração oficial (sem bootstrap, semente 42). Ela precisa reproduzir os
números das etapas 04, 04b, 04c, 07b e 08; senão o estudo para.

Uso:
  .venv/bin/python scripts/estudo_robustez_100.py modelos --reps 0-50
  .venv/bin/python scripts/estudo_robustez_100.py h2
  .venv/bin/python scripts/estudo_robustez_100.py h3
  .venv/bin/python scripts/estudo_robustez_100.py consolidar
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import warnings
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "dissertacao_frotas/dados/processados"
LOGS = ROOT / "dissertacao_frotas/resultados/logs"
OUT = ROOT / "resultados_robustez_100"
PREREG = ROOT / "docs/hipoteses/preregistro_estudo_100_repeticoes.md"
HASH = ROOT / "docs/hipoteses/preregistro_estudo_100_repeticoes.sha256"
ADITIVO = ROOT / "docs/hipoteses/aditivo_01_estudo_robustez.md"
HASH_ADITIVO = ROOT / "docs/hipoteses/aditivo_01_estudo_robustez.sha256"
N_REP = 1000
NIVEIS = (1, 10, 100, 1000)      # 1 = só r = 0 (configuração oficial); demais = r 1..n
CORTE = "2024-12"
# Critérios do pré-registro + Aditivo 01 (único lugar com estes números; vão também para resultado_robustez.json,
# de onde os gráficos em R os leem).
CRITERIOS = {
    "robustez_fracao_minima": 0.95,          # decisão robusta: coincide com a oficial em >= 95% das repetições
    "H1_ganho_mae_limiar": 0.15,             # limiar: mediana do ganho relativo no MAE >= 15%
    "H2_dif_mae_rel_max": 0.05,              # não inferioridade: MAE do ensemble até 5% acima do SVR...
    "H2_dif_auc_min": -0.02,                 # ...e AUC no máximo 0,02 abaixo
    "H3_economia_limiar": 0.10,              # limiar: P2,5 da economia sobre a BL0 > 10%
    "H4_lime_r2_min": 0.50,                  # anteprojeto: P2,5 do R² local do LIME >= 0,50...
    "H4_erro_aditivo_max": 1e-3,             # ...e erro de aditividade do SHAP <= 1e-3
    "H4_spearman_limiar": 0.85,              # limiar: P2,5 de Spearman e de Jaccard > 0,85
    "H4_jaccard_limiar": 0.85,
}
FEATS = ["custo_mes", "vl_pecas_mes", "vl_mo_mes", "qtd_os_mes", "qtd_corretivas_mes", "qtd_preventivas_mes", "km_max",
         "idade_veiculo", "custo_lag1", "custo_lag2", "os_lag1", "corretivas_lag1", "km_diff", "patrimonio_valor_entrada",
         "patrimonio_valor_liquido"]
FEATS_M = FEATS[:13]


def semente(r: int) -> int:
    return 42 if r == 0 else 1000 + r


def conferir_preregistro():
    for doc, h in ((PREREG, HASH), (ADITIVO, HASH_ADITIVO)):
        if hashlib.sha256(doc.read_bytes()).hexdigest() != h.read_text().split()[0]:
            sys.exit(f"[ERRO] {doc.name} foi alterado depois do hash; registre um novo aditivo antes de rodar.")


def faixa(txt):
    a, b = txt.split("-") if "-" in txt else (txt, txt)
    return list(range(int(a), int(b) + 1))


# Cada processo grava no próprio arquivo (<parte>__<pid>.csv); a leitura junta todos.
def _arquivos(base: str):
    return sorted(OUT.glob(f"{base}__*.csv"))


def ler_parte(base: str):
    fs = _arquivos(base)
    if not fs:
        return pd.DataFrame(columns=["rep"])
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)


def ja_feitas(base: str):
    d = ler_parte(base)
    return set(d.rep.astype(int)) if len(d) else set()


def gravar(base: str, linha: dict):
    import os
    arq = OUT / f"{base}__{os.getpid()}.csv"
    pd.DataFrame([linha]).to_csv(arq, mode="a", header=not arq.exists(), index=False)


def painel():
    df = pd.read_parquet(PROC / "painel_veiculo_mes_longitudinal.parquet")
    tr, te = df[df.ano_mes <= CORTE].reset_index(drop=True), df[df.ano_mes > CORTE].reset_index(drop=True)
    return tr, te


def ece(y, p, n_bins=10):
    """Mesma função da etapa 04 (compute_ece), sem arredondamento."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.digitize(p, bins) - 1
    e = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.sum():
            e += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(e)


# ------------------------------------------------------------------ parte: modelos + H1 + H4
def parte_modelos(reps):
    import shap
    from lime import lime_tabular
    from scipy import stats
    from sklearn.ensemble import (ExtraTreesClassifier, ExtraTreesRegressor, HistGradientBoostingClassifier,
                                  HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor)
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (accuracy_score, auc, balanced_accuracy_score, brier_score_loss, f1_score,
                                 mean_absolute_error, mean_squared_error, precision_recall_curve, precision_score,
                                 r2_score, recall_score, roc_auc_score)
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

    tr, te = painel()
    Xte = te[FEATS].fillna(0.0)
    yte_c, yte_r = te.target_class_corretiva_t1.values, te.target_reg_custo_t1.values
    arq, arq_conf = "modelos", "confusao"
    feitas = ja_feitas(arq)
    for r in reps:
        if r in feitas:
            continue
        t0, s = time.time(), semente(r)
        b = tr if r == 0 else tr.sample(n=len(tr), replace=True, random_state=s).reset_index(drop=True)
        Xtr, ytr_c, ytr_r = b[FEATS].fillna(0.0), b.target_class_corretiva_t1.values, b.target_reg_custo_t1.values
        L = {"rep": r, "semente": s, "n_treino": len(b), "n_teste": len(te)}
        clfs = {"HistGradientBoosting": HistGradientBoostingClassifier(random_state=s, max_iter=150, max_depth=6),
                "RandomForest": RandomForestClassifier(random_state=s, n_estimators=100, max_depth=8, n_jobs=2),
                "ExtraTrees": ExtraTreesClassifier(random_state=s, n_estimators=100, max_depth=8, n_jobs=2),
                "DecisionTree": DecisionTreeClassifier(random_state=s, max_depth=5),
                "LogisticRegression": LogisticRegression(random_state=s, max_iter=500)}
        hgb_c = None
        for nome, m in clfs.items():
            m.fit(Xtr, ytr_c)
            p = m.predict_proba(Xte)[:, 1]
            q = (p >= 0.5).astype(int)
            pr, rc, _ = precision_recall_curve(yte_c, p)
            L |= {f"cls|{nome}|roc_auc": roc_auc_score(yte_c, p), f"cls|{nome}|pr_auc": auc(rc, pr),
                  f"cls|{nome}|f1": f1_score(yte_c, q), f"cls|{nome}|acuracia": accuracy_score(yte_c, q),
                  f"cls|{nome}|acuracia_balanceada": balanced_accuracy_score(yte_c, q),
                  f"cls|{nome}|precisao": precision_score(yte_c, q, zero_division=0), f"cls|{nome}|sensibilidade": recall_score(yte_c, q),
                  f"cls|{nome}|brier": brier_score_loss(yte_c, p), f"cls|{nome}|ece": ece(yte_c, p)}
            vp, fp = int(((q == 1) & (yte_c == 1)).sum()), int(((q == 1) & (yte_c == 0)).sum())
            fn, vn = int(((q == 0) & (yte_c == 1)).sum()), int(((q == 0) & (yte_c == 0)).sum())
            gravar(arq_conf, {"rep": r, "modelo": nome, "VP": vp, "FP": fp, "FN": fn, "VN": vn})
            if nome == "HistGradientBoosting":
                hgb_c, p_hgb = m, p
        regs = {"HistGradientBoosting": HistGradientBoostingRegressor(random_state=s, max_iter=150, max_depth=6),
                "RandomForest": RandomForestRegressor(random_state=s, n_estimators=100, max_depth=8, n_jobs=2),
                "ExtraTrees": ExtraTreesRegressor(random_state=s, n_estimators=100, max_depth=8, n_jobs=2),
                "DecisionTree": DecisionTreeRegressor(random_state=s, max_depth=5)}
        pred_r = {}
        for nome, m in regs.items():
            m.fit(Xtr, ytr_r)
            pred_r[nome] = m.predict(Xte)
        pred_r["Mediana"] = np.full(len(te), float(np.median(ytr_r)))
        for nome, pr_ in pred_r.items():
            L |= {f"reg|{nome}|mae": mean_absolute_error(yte_r, pr_), f"reg|{nome}|rmse": float(np.sqrt(mean_squared_error(yte_r, pr_))),
                  f"reg|{nome}|r2": r2_score(yte_r, pr_)}
        # H1: M × M+P (HistGB), mesma amostra
        cm = HistGradientBoostingClassifier(random_state=s, max_iter=150, max_depth=6).fit(b[FEATS_M].fillna(0.0), ytr_c)
        rm = HistGradientBoostingRegressor(random_state=s, max_iter=150, max_depth=6).fit(b[FEATS_M].fillna(0.0), ytr_r)
        auc_m = roc_auc_score(yte_c, cm.predict_proba(te[FEATS_M].fillna(0.0))[:, 1])
        mae_m = mean_absolute_error(yte_r, rm.predict(te[FEATS_M].fillna(0.0)))
        L |= {"h1|roc_auc_M": auc_m, "h1|roc_auc_MP": L["cls|HistGradientBoosting|roc_auc"], "h1|mae_M": mae_m,
              "h1|mae_MP": L["reg|HistGradientBoosting|mae"]}
        L["h1|dif_roc_auc"] = L["h1|roc_auc_MP"] - auc_m
        L["h1|ganho_mae"] = (mae_m - L["h1|mae_MP"]) / mae_m
        # H4: SHAP × LIME nas 25 instâncias de maior risco
        crit = np.argsort(p_hgb)[-25:]
        exp = shap.TreeExplainer(hgb_c)
        sv = exp.shap_values(Xte.iloc[crit])
        base = float(np.ravel(exp.expected_value)[0])
        logit = hgb_c.decision_function(Xte.iloc[crit])
        L["h4|shap_erro_aditivo_max"] = float(np.max(np.abs(sv.sum(axis=1) + base - logit)))
        lime = lime_tabular.LimeTabularExplainer(Xte.values, feature_names=FEATS, mode="classification", random_state=s)
        rhos, jacs, r2s = [], [], []
        for k, idx in enumerate(crit):
            e = lime.explain_instance(Xte.iloc[idx].values, hgb_c.predict_proba, num_features=len(FEATS))
            w = np.zeros(len(FEATS))
            for j, v in e.as_map()[1]:
                w[j] = v
            rho = stats.spearmanr(sv[k], w).statistic
            if not np.isnan(rho):
                rhos.append(rho)
            ts, tl = set(np.argsort(np.abs(sv[k]))[-5:]), set(np.argsort(np.abs(w))[-5:])
            jacs.append(len(ts & tl) / len(ts | tl))
            r2s.append(float(e.score))
        L |= {"h4|spearman": float(np.mean(rhos)), "h4|jaccard": float(np.mean(jacs)), "h4|lime_r2": float(np.mean(r2s))}
        L["duracao_s"] = round(time.time() - t0, 1)
        gravar(arq, L)
        print(f"modelos r={r:3d} ok em {L['duracao_s']}s | AUC HGB {L['cls|HistGradientBoosting|roc_auc']:.4f} | "
              f"H1 ΔAUC {L['h1|dif_roc_auc']:+.4f} ganho MAE {100 * L['h1|ganho_mae']:+.2f}% | H4 ρ {L['h4|spearman']:.3f}", flush=True)


# ------------------------------------------------------------------ parte: H2
def parte_h2(reps):
    from sklearn.compose import TransformedTargetRegressor
    from sklearn.ensemble import (ExtraTreesClassifier, ExtraTreesRegressor, HistGradientBoostingClassifier,
                                  HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor)
    from sklearn.metrics import mean_absolute_error, roc_auc_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC, SVR

    # mesma construção dos modelos da etapa 04c
    sys.path.insert(0, str(ROOT / "dissertacao_frotas/src"))
    import importlib
    m04c = importlib.import_module("04c_comparacao_svr_h2")
    tr, te = painel()
    Xte = te[FEATS].fillna(0.0)
    yte_c, yte_r = te.target_class_corretiva_t1.values, te.target_reg_custo_t1.values
    arq = "h2"
    feitas = ja_feitas(arq)
    for r in reps:
        if r in feitas:
            continue
        t0, s = time.time(), semente(r)
        sub = tr.sample(n=min(m04c.N_SUB, len(tr)), random_state=s)
        X, yc, yr = sub[FEATS].fillna(0.0), sub.target_class_corretiva_t1.values, sub.target_reg_custo_t1.values
        L = {"rep": r, "semente": s}
        for nome, m in m04c.regs(s).items():
            m.fit(X, yr)
            L[f"mae|{nome}"] = mean_absolute_error(yte_r, m.predict(Xte))
        for nome, m in m04c.clfs(s).items():
            m.fit(X, yc)
            L[f"auc|{nome}"] = roc_auc_score(yte_c, m04c.score_cls(m, Xte))
        for e in ("HistGradientBoosting", "RandomForest", "ExtraTrees"):
            L[f"dif_mae_rel|{e}"] = (L[f"mae|{e}"] - L["mae|SVR-RBF"]) / L["mae|SVR-RBF"]
            L[f"dif_auc|{e}"] = L[f"auc|{e}"] - L["auc|SVC-RBF"]
        L["duracao_s"] = round(time.time() - t0, 1)
        gravar(arq, L)
        print(f"h2 r={r:3d} ok em {L['duracao_s']}s | MAE SVR {L['mae|SVR-RBF']:.2f} HGB {L['mae|HistGradientBoosting']:.2f} | "
              f"AUC SVC {L['auc|SVC-RBF']:.4f} HGB {L['auc|HistGradientBoosting']:.4f}", flush=True)


# ------------------------------------------------------------------ parte: H3
def instancia_s0(df_os, s):
    """Reproduz a construção da instância da etapa 08, com a semente s no lugar de 42."""
    veiculos_unicos = df_os["veiculo_id"].dropna().unique()
    n = min(2000, len(veiculos_unicos))
    np.random.seed(s)
    sel = np.random.choice(veiculos_unicos, size=n, replace=False)
    df_sub = df_os[df_os["veiculo_id"].isin(sel)]
    T = 36
    km_base = df_sub.groupby("veiculo_id")["nr_quilometragem"].max().to_dict()
    custo_base = df_sub.groupby("veiculo_id")["vl_aprovado_total"].mean().to_dict()
    custo_medio = float(np.median([v for v in custo_base.values() if v > 0])) if custo_base else 850.0
    c, rr, h, m = np.zeros((n, T)), np.zeros((n, T)), np.zeros((n, T)), np.zeros((n, T), dtype=int)
    for i in range(n):
        v_km = km_base.get(sel[i], 80000.0)
        v_c = min(1100.0, max(280.0, float(custo_base.get(sel[i], custo_medio) * 0.288)))
        for t in range(T):
            c[i, t] = max(180.0, float(v_c * (1.0 + (t / 36.0) * 0.15) * (1.0 + (v_km / 150000.0) * 0.20) * np.random.uniform(0.94, 1.06)))
            pf = min(0.60, 0.05 + (t % 12) * 0.035 + (v_km / 200000.0) * 0.15)
            rr[i, t] = float(pf * (c[i, t] * 2.1 + 520.0))
            h[i, t] = max(1.5, float(c[i, t] / 180.0))
            if (t + (i % 6)) % 12 == 0:
                m[i, t] = 1
    B = float(np.mean(np.sum(c, axis=0)) * 0.45)
    H = float(np.mean(np.sum(h, axis=0)) * 0.50)
    return c, rr, h, m, B, H


def parte_h3(reps):
    from scipy.optimize import Bounds, LinearConstraint, milp
    df_os = pd.read_parquet(PROC / "os_consolidadas_processadas.parquet")
    arq = "h3"
    feitas = ja_feitas(arq)
    for r in reps:
        if r in feitas:
            continue
        t0, s = time.time(), semente(r)
        c, rr, h, m, B, H = instancia_s0(df_os, s)
        n, T = c.shape
        x = np.zeros((n, T), dtype=int)
        for t in range(T):
            res = milp(c=c[:, t] - rr[:, t], integrality=np.ones(n), bounds=Bounds(m[:, t].astype(float), np.ones(n)),
                       constraints=LinearConstraint(np.vstack([c[:, t], h[:, t]]), [-np.inf, -np.inf], [B, H]),
                       options={"mip_rel_gap": 0.0001})
            x[:, t] = np.round(res.x).astype(int) if res.x is not None else m[:, t]
        custo = lambda z: float(np.sum(z * c) + np.sum((1 - z) * rr))
        xh = m.copy()
        for t in range(T):
            g, hh = float(np.sum(xh[:, t] * c[:, t])), float(np.sum(xh[:, t] * h[:, t]))
            for i in sorted([i for i in range(n) if xh[i, t] == 0 and rr[i, t] > c[i, t]], key=lambda i: rr[i, t] / c[i, t], reverse=True):
                if g + c[i, t] <= B and hh + h[i, t] <= H:
                    xh[i, t] = 1; g += c[i, t]; hh += h[i, t]
        L = {"rep": r, "semente": s, "custo_milp": custo(x), "custo_bl0": custo(m), "custo_heur": custo(xh),
             "obrigatorias_pct": float(np.sum(x * m) / max(1, m.sum()) * 100)}
        L["economia_pct"] = (L["custo_bl0"] - L["custo_milp"]) / L["custo_bl0"]
        L["milp_menos_heur"] = L["custo_milp"] - L["custo_heur"]
        L["duracao_s"] = round(time.time() - t0, 1)
        gravar(arq, L)
        print(f"h3 r={r:3d} ok em {L['duracao_s']}s | economia {100 * L['economia_pct']:.2f}% | MILP−heur R$ {L['milp_menos_heur']:,.2f}", flush=True)


# ------------------------------------------------------------------ controle r = 0
def conferir_controle():
    """A repetição 0 (configuração oficial) precisa reproduzir os JSON das etapas."""
    J = lambda n: json.loads((LOGS / n).read_text(encoding="utf-8"))
    pred, abl, svr, h4o, milp = (J("relatorio_modelagem_preditiva.json"), J("relatorio_ablacao_h1.json"), J("relatorio_h2_svr.json"),
                                 J("relatorio_h4_fidelidade_estabilidade.json"), J("relatorio_otimizacao_milp.json"))
    md = ler_parte("modelos").drop_duplicates("rep", keep="last").set_index("rep").loc[0]
    h2 = ler_parte("h2").drop_duplicates("rep", keep="last").set_index("rep").loc[0]
    h3 = ler_parte("h3").drop_duplicates("rep", keep="last").set_index("rep").loc[0]
    chk = []
    def c(nome, obtido, esperado, tol):
        chk.append({"verificacao": nome, "obtido": float(obtido), "esperado": float(esperado), "tolerancia": tol,
                    "ok": bool(abs(float(obtido) - float(esperado)) <= tol)})
    for m_ in pred["metricas_classificacao"]:
        c(f"ROC-AUC {m_['modelo']} (etapa 04)", md[f"cls|{m_['modelo']}|roc_auc"], m_["roc_auc"], 6e-5)
        c(f"F1 {m_['modelo']} (etapa 04)", md[f"cls|{m_['modelo']}|f1"], m_["f1_score"], 6e-5)
        c(f"ECE {m_['modelo']} (etapa 04)", md[f"cls|{m_['modelo']}|ece"], m_["ece"], 6e-5)
    for m_ in pred["metricas_regressao"]:
        nome = "Mediana" if m_["modelo"] == "Baseline Mediana" else m_["modelo"]
        c(f"MAE {m_['modelo']} (etapa 04)", md[f"reg|{nome}|mae"], m_["mae_reais"], 0.006)
    c("MAE M (etapa 04b)", md["h1|mae_M"], abl["mae_M"], 0.01)
    c("ROC-AUC M (etapa 04b)", md["h1|roc_auc_M"], abl["classificacao_semente42"]["roc_auc_M"], 1e-6)
    for tarefa, chave, pref, tol in (("regressao", "mae", "mae|", 0.01), ("classificacao", None, "auc|", 1e-4)):
        for nome, lst in svr["por_semente"][tarefa].items():
            if nome == "SVR-RBF":
                tol = 0.50   # aditivo 01, item 6: diferença de ponto flutuante DataFrame × array
            v = next(x for x in lst if x["semente"] == 42)
            val = v["mae"] if chave else next(v[k] for k in v if k not in ("semente", "tempo_s"))
            c(f"{tarefa} {nome} semente 42 (etapa 04c)", h2[pref + nome], val, tol)
    c("R² LIME (etapa 07b)", md["h4|lime_r2"], h4o["medidas"]["F2_lime_r2_medio"], 0.01)
    c("Custo MILP (etapa 08)", h3["custo_milp"], milp["solucao_inteira_mip_brl"], 1.0)
    c("Custo BL0 (etapa 08)", h3["custo_bl0"], milp["confronto_inercial"]["custo_inercial_as_is_brl"], 1.0)
    c("Custo heurística (etapa 08)", h3["custo_heur"], milp["confronto_inercial"]["custo_heuristica_gulosa_brl"], 1.0)
    return chk


# ------------------------------------------------------------------ consolidação
P = lambda s_, q: float(np.percentile(s_, q))


def resumo(s_):
    s_ = pd.Series(s_, dtype=float)
    return {"n": int(len(s_)), "media": float(s_.mean()), "dp": float(s_.std(ddof=1)) if len(s_) > 1 else 0.0,
            "p2_5": P(s_, 2.5), "mediana": float(s_.median()), "p97_5": P(s_, 97.5), "min": float(s_.min()), "max": float(s_.max())}


def status(a, b):
    cs = [x for x in (a, b) if x is not None]
    if len(cs) == 1:
        return "SUSTENTADA" if cs[0] else "NÃO SUSTENTADA"
    return "SUSTENTADA" if all(cs) else ("PARCIALMENTE SUSTENTADA" if any(cs) else "NÃO SUSTENTADA")


def avaliar_nivel(md, h2, h3, conf, ofi):
    """Aplica as medidas e os critérios do pré-registro (com o aditivo) a um conjunto de repetições."""
    n = len(md)
    K = CRITERIOS
    lim_rob = K["robustez_fracao_minima"] * n
    matriz = {}
    for col in [c for c in md.columns if c.startswith(("cls|", "reg|"))]:
        tarefa, modelo, metrica = col.split("|")
        matriz.setdefault(tarefa, {}).setdefault(modelo, {})[metrica] = resumo(md[col])
    vit = {}
    for metrica, maior in (("roc_auc", True), ("pr_auc", True), ("f1", True), ("acuracia", True), ("acuracia_balanceada", True),
                           ("brier", False), ("ece", False)):
        cols = [c for c in md.columns if c.startswith("cls|") and c.endswith("|" + metrica)]
        v = md[cols].idxmax(axis=1) if maior else md[cols].idxmin(axis=1)
        vit[f"cls|{metrica}"] = {k.split("|")[1]: int(x) for k, x in v.value_counts().items()}
    for metrica, maior in (("mae", False), ("rmse", False), ("r2", True)):
        cols = [c for c in md.columns if c.startswith("reg|") and c.endswith("|" + metrica)]
        v = md[cols].idxmax(axis=1) if maior else md[cols].idxmin(axis=1)
        vit[f"reg|{metrica}"] = {k.split("|")[1]: int(x) for k, x in v.value_counts().items()}
    cm = conf.groupby("modelo")[["VP", "FP", "FN", "VN"]]
    conf_media = {m: {k: {"media": float(cm.mean().loc[m, k]), "dp": float(cm.std(ddof=1).fillna(0).loc[m, k])}
                      for k in ("VP", "FP", "FN", "VN")} for m in cm.mean().index}
    H = {}
    d_roc, g_mae = md["h1|dif_roc_auc"], md["h1|ganho_mae"]
    H["H1"] = {"dif_roc_auc": resumo(d_roc), "ganho_mae": resumo(g_mae),
               "ante_reamostragem": bool(P(d_roc, 2.5) > 0 or P(g_mae, 2.5) > 0), "lim_reamostragem": bool(g_mae.median() >= K["H1_ganho_mae_limiar"]),
               "reps_atende_ante": int(((d_roc > 0) | (g_mae > 0)).sum()), "reps_atende_lim": int((g_mae >= K["H1_ganho_mae_limiar"]).sum()),
               "reps_auc_MP_melhor": int((d_roc > 0).sum()), "reps_mae_MP_melhor": int((g_mae > 0).sum())}
    ens = {}
    for e in ("HistGradientBoosting", "RandomForest", "ExtraTrees"):
        dm, da = h2[f"dif_mae_rel|{e}"], h2[f"dif_auc|{e}"]
        ens[e] = {"dif_mae_rel": resumo(dm), "dif_auc": resumo(da),
                  "nao_inferior_reamostragem": bool(P(dm, 97.5) <= K["H2_dif_mae_rel_max"] and P(da, 2.5) >= K["H2_dif_auc_min"]),
                  "reps_nao_inferior": int(((dm <= K["H2_dif_mae_rel_max"]) & (da >= K["H2_dif_auc_min"])).sum()),
                  "reps_svr_melhor_mae": int((dm > 0).sum()), "reps_ensemble_melhor_auc": int((da > 0).sum())}
    rep_h2 = pd.concat([(h2[f"dif_mae_rel|{e}"] <= K["H2_dif_mae_rel_max"]) & (h2[f"dif_auc|{e}"] >= K["H2_dif_auc_min"]) for e in ens],
                       axis=1).any(axis=1)
    H["H2"] = {"ensembles": ens, "ante_reamostragem": any(v["nao_inferior_reamostragem"] for v in ens.values()), "lim_reamostragem": None,
               "reps_atende_ante": int(rep_h2.sum()), "mae_svr": resumo(h2["mae|SVR-RBF"]), "mae_hgb": resumo(h2["mae|HistGradientBoosting"]),
               "auc_svc": resumo(h2["auc|SVC-RBF"]), "auc_hgb": resumo(h2["auc|HistGradientBoosting"])}
    ante3 = (h3.custo_milp < h3.custo_bl0) & (h3.custo_milp < h3.custo_heur)
    H["H3"] = {"economia_pct": resumo(h3.economia_pct), "milp_menos_heur": resumo(h3.milp_menos_heur),
               "obrigatorias_pct_min": float(h3.obrigatorias_pct.min()),
               "ante_reamostragem": bool(ante3.sum() >= lim_rob), "lim_reamostragem": bool(P(h3.economia_pct, 2.5) > K["H3_economia_limiar"]),
               "reps_atende_ante": int(ante3.sum()), "reps_atende_lim": int((h3.economia_pct > K["H3_economia_limiar"]).sum()),
               "reps_milp_igual_heur": int((h3.milp_menos_heur.abs() < 0.01).sum())}
    sp, ja, r2, ead = md["h4|spearman"], md["h4|jaccard"], md["h4|lime_r2"], md["h4|shap_erro_aditivo_max"]
    H["H4"] = {"spearman": resumo(sp), "jaccard": resumo(ja), "lime_r2": resumo(r2), "shap_erro_aditivo_max": float(ead.max()),
               "ante_reamostragem": bool(P(r2, 2.5) >= K["H4_lime_r2_min"] and ead.max() <= K["H4_erro_aditivo_max"]),
               "lim_reamostragem": bool(P(sp, 2.5) > K["H4_spearman_limiar"] and P(ja, 2.5) > K["H4_jaccard_limiar"]),
               "reps_atende_ante": int(((r2 >= K["H4_lime_r2_min"]) & (ead <= K["H4_erro_aditivo_max"])).sum()),
               "reps_atende_lim": int(((sp > K["H4_spearman_limiar"]) & (ja > K["H4_jaccard_limiar"])).sum())}
    sn = {"sim": True, "não": False, "—": None}
    for k, v in H.items():
        o = ofi[k]
        oa, ol = sn[o["atende_anteprojeto"]], sn[o["atende_limiar"]]
        v["decisao_oficial"] = o["decisao"]
        v["decisao_sob_reamostragem"] = status(v["ante_reamostragem"], v["lim_reamostragem"])
        rob = {}
        for nome_c, oficial, chave in (("anteprojeto", oa, "reps_atende_ante"), ("limiar", ol, "reps_atende_lim")):
            if oficial is None or v.get(chave) is None:
                continue
            coincidem = v[chave] if oficial else n - v[chave]
            rob[nome_c] = {"oficial": oficial, "reps_coincidem": int(coincidem), "de": n, "robusta": bool(coincidem >= lim_rob)}
        v["robustez"] = rob
        v["decisao_oficial_robusta"] = all(x["robusta"] for x in rob.values())
        v["coincide_com_oficial"] = v["decisao_sob_reamostragem"] == o["decisao"]
    return {"repeticoes": n, "matriz_desempenho": matriz, "vitorias_por_metrica": vit, "matriz_confusao_media": conf_media, "hipoteses": H}


def consolidar():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    OFI = json.loads((LOGS / "certificado_reprodutibilidade_cientifica.json").read_text(encoding="utf-8"))
    ofi = {h["id"]: h for h in OFI["matriz_hipoteses"]}
    md = ler_parte("modelos").drop_duplicates("rep", keep="last").set_index("rep").sort_index()
    h2 = ler_parte("h2").drop_duplicates("rep", keep="last").set_index("rep").sort_index()
    h3 = ler_parte("h3").drop_duplicates("rep", keep="last").set_index("rep").sort_index()
    conf = ler_parte("confusao").drop_duplicates(["rep", "modelo"], keep="last")
    disp = min(int(d.index.max()) for d in (md, h2, h3))
    for nome, d in (("modelos", md), ("h2", h2), ("h3", h3)):
        faltam = sorted(set(range(0, disp + 1)) - set(d.index))
        if faltam:
            sys.exit(f"[ERRO] parte {nome}: faltam repetições {faltam[:10]}{'…' if len(faltam) > 10 else ''}")
    controle = conferir_controle()
    falhas = [x for x in controle if not x["ok"]]
    niveis = {}
    for nv in NIVEIS:
        reps = [0] if nv == 1 else list(range(1, nv + 1))
        if max(reps) > disp:
            continue
        niveis[str(nv)] = avaliar_nivel(md.loc[reps], h2.loc[reps], h3.loc[reps], conf[conf.rep.isin(reps)], ofi)
    if not niveis:
        sys.exit("[ERRO] nenhum nível completo")
    R = {"gerado_em": datetime.now().isoformat(timespec="seconds"), "preregistro": str(PREREG.relative_to(ROOT)),
         "preregistro_sha256": HASH.read_text().split()[0], "aditivo": str(ADITIVO.relative_to(ROOT)),
         "aditivo_sha256": HASH_ADITIVO.read_text().split()[0], "repeticoes_disponiveis": disp, "nivel_principal": "1000", "criterios": CRITERIOS,
         "controle_r0": {"verificacoes": len(controle), "aprovadas": len(controle) - len(falhas), "falhas": falhas, "detalhe": controle},
         "niveis": niveis}
    (OUT / "resultado_robustez.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
    maior = max(niveis, key=int)
    reps = [0] if maior == "1" else list(range(1, int(maior) + 1))
    figuras(niveis[maior], md.loc[reps], h2.loc[reps], h3.loc[reps], plt)
    figura_niveis(niveis, plt)
    print(f"Controle r=0: {len(controle) - len(falhas)}/{len(controle)} verificações aprovadas")
    for f in falhas:
        print("   FALHA:", f)
    for nv, N in niveis.items():
        print(f"== nível {nv}× ({N['repeticoes']} repetições)")
        for k, v in N["hipoteses"].items():
            print(f"   {k}: oficial {v['decisao_oficial']} | sob reamostragem {v['decisao_sob_reamostragem']} | "
                  f"robusta {v['decisao_oficial_robusta']} | " + "; ".join(f"{c} {x['reps_coincidem']}/{x['de']}" for c, x in v["robustez"].items()))


def figura_niveis(niveis, plt):
    """Média e P2,5–P97,5 por nível (1×, 10×, 100×, 1.000×) das métricas centrais."""
    met = [("cls", "HistGradientBoosting", "roc_auc", "ROC-AUC HistGB"), ("reg", "HistGradientBoosting", "mae", "MAE HistGB (R$)"),
           ("H1", "ganho_mae", None, "H1: ganho no MAE"), ("H2", "HistGradientBoosting", "dif_mae_rel", "H2: MAE HistGB vs SVR"),
           ("H3", "economia_pct", None, "H3: economia sobre BL0"), ("H4", "spearman", None, "H4: Spearman SHAP × LIME")]
    fig, axs = plt.subplots(1, len(met), figsize=(18, 3.6))
    xs = list(niveis)
    for ax, (a, b, c, tit) in zip(axs, met):
        vals = []
        for nv in xs:
            N = niveis[nv]
            if a in ("cls", "reg"):
                r = N["matriz_desempenho"][a][b][c]
            elif a == "H2":
                r = N["hipoteses"]["H2"]["ensembles"][b][c]
            else:
                r = N["hipoteses"][a][b]
            vals.append(r)
        m = [v["media"] for v in vals]
        lo = [v["media"] - v["p2_5"] for v in vals]
        hi = [v["p97_5"] - v["media"] for v in vals]
        ax.errorbar(range(len(xs)), m, yerr=[lo, hi], fmt="o-", color="#00693e", capsize=4)
        ax.set_xticks(range(len(xs)), [f"{x}×" for x in xs])
        ax.set_title(tit, fontsize=9)
        ax.grid(alpha=.3)
    fig.suptitle("Média e intervalo P2,5–P97,5 por número de repetições", fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "fig_convergencia_niveis.png", dpi=200); plt.close(fig)


def figuras(R, md, h2, h3, plt):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    br = lambda x, n=4: f"{x:.{n}f}".replace(".", ",")
    # 1. matriz de desempenho (heatmap da média e DP)
    M = R["matriz_desempenho"]
    mets_c = ["roc_auc", "pr_auc", "f1", "acuracia", "acuracia_balanceada", "precisao", "sensibilidade", "brier", "ece"]
    mods_c = list(M["cls"])
    fig, axs = plt.subplots(1, 2, figsize=(15, 4.6), gridspec_kw={"width_ratios": [3, 1.4]})
    A = np.array([[M["cls"][m][k]["media"] for k in mets_c] for m in mods_c])
    axs[0].imshow(A, cmap="Greens", aspect="auto")
    for i, m in enumerate(mods_c):
        for j, k in enumerate(mets_c):
            v = M["cls"][m][k]
            axs[0].text(j, i, f"{br(v['media'])}\n±{br(v['dp'])}", ha="center", va="center", fontsize=8)
    axs[0].set_xticks(range(len(mets_c)), [k.replace("_", " ") for k in mets_c], rotation=20)
    axs[0].set_yticks(range(len(mods_c)), mods_c)
    axs[0].set_title(f"Classificação: média ± DP em {R['repeticoes']} repetições (limiar 0,5)")
    mets_r, mods_r = ["mae", "rmse", "r2"], list(M["reg"])
    B = np.array([[M["reg"][m][k]["media"] for k in mets_r] for m in mods_r])
    axs[1].imshow(-B[:, :1], cmap="Blues", aspect="auto")
    for i, m in enumerate(mods_r):
        for j, k in enumerate(mets_r):
            v = M["reg"][m][k]
            axs[1].text(j / 1.0 * 0 + 0, i, "", fontsize=1)
    axs[1].clear()
    axs[1].axis("off")
    tab = axs[1].table(cellText=[[f"{M['reg'][m]['mae']['media']:,.0f} ± {M['reg'][m]['mae']['dp']:,.0f}".replace(",", "."),
                                  f"{M['reg'][m]['rmse']['media']:,.0f}".replace(",", "."), br(M["reg"][m]["r2"]["media"], 3)] for m in mods_r],
                       rowLabels=mods_r, colLabels=["MAE (R$)", "RMSE (R$)", "R²"], loc="center", cellLoc="center")
    tab.scale(1, 1.6)
    axs[1].set_title(f"Regressão: média em {R['repeticoes']} repetições")
    fig.tight_layout(); fig.savefig(OUT / "fig_matriz_desempenho_100.png", dpi=200); plt.close(fig)
    # 2. distribuições das métricas de H1–H4
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    def hist(ax, s_, ref, titulo, fmt=lambda x: br(x)):
        ax.hist(s_, bins=20, color="#00693e", alpha=.8)
        if ref is not None:
            ax.axvline(ref, color="#c8102e", ls="--", lw=1.6, label=f"critério {fmt(ref)}")
            ax.legend(fontsize=8)
        ax.axvline(np.percentile(s_, 2.5), color="#555", ls=":", lw=1)
        ax.axvline(np.percentile(s_, 97.5), color="#555", ls=":", lw=1)
        ax.set_title(titulo, fontsize=10)
    pc = lambda x: f"{100 * x:.1f}%".replace(".", ",")
    hist(axs[0, 0], md["h1|dif_roc_auc"], 0.0, "H1: Δ ROC-AUC (M+P − M)")
    hist(axs[0, 1], md["h1|ganho_mae"], 0.15, "H1: ganho no MAE (M → M+P)", pc)
    hist(axs[0, 2], h2["dif_mae_rel|HistGradientBoosting"], 0.05, "H2: MAE HistGB vs SVR (relativo)", pc)
    hist(axs[1, 0], h3["economia_pct"], 0.10, "H3: economia do MILP sobre BL0", pc)
    hist(axs[1, 1], md["h4|spearman"], 0.85, "H4: Spearman SHAP × LIME")
    hist(axs[1, 2], md["h4|lime_r2"], 0.50, "H4: R² local do LIME")
    for ax in axs.flat:
        ax.set_ylabel("repetições")
    fig.suptitle(f"Distribuição das {R['repeticoes']} repetições (linhas pontilhadas: P2,5 e P97,5)", fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "fig_distribuicoes_hipoteses_100.png", dpi=200); plt.close(fig)
    # 3. boxplot ROC-AUC e MAE por modelo
    fig, axs = plt.subplots(1, 2, figsize=(14, 4.6))
    mods = list(M["cls"])
    axs[0].boxplot([md[f"cls|{m}|roc_auc"] for m in mods], tick_labels=mods)
    axs[0].set_title(f"ROC-AUC no teste temporal ({R['repeticoes']} repetições)"); axs[0].tick_params(axis="x", rotation=15)
    mods = list(M["reg"])
    axs[1].boxplot([md[f"reg|{m}|mae"] for m in mods], tick_labels=mods)
    axs[1].set_title(f"MAE (R$) no teste temporal ({R['repeticoes']} repetições)"); axs[1].tick_params(axis="x", rotation=15)
    fig.tight_layout(); fig.savefig(OUT / "fig_boxplot_modelos_100.png", dpi=200); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parte", choices=["modelos", "h2", "h3", "consolidar"])
    ap.add_argument("--reps", default=f"0-{N_REP}")
    a = ap.parse_args()
    conferir_preregistro()
    OUT.mkdir(exist_ok=True)
    if a.parte == "consolidar":
        consolidar()
        return
    {"modelos": parte_modelos, "h2": parte_h2, "h3": parte_h3}[a.parte](faixa(a.reps))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Regenera, a partir dos resultados calculados, as figuras 12, 13, 14 e 64 usadas na
qualificação, no mapeamento e na dissertação (antes desenhadas com números digitados em
scripts/regerar_todos_graficos_formatados.py, que agora as ignora).

  fig12_ablativo_fontes_m_vs_mp.png        etapa 04b (relatorio_ablacao_h1.json)
  fig13_importancia_atributos_xai.png      etapa 07  (top_features_shap)
  fig14_otimizacao_sensibilidade_orcamento.png  etapa 08 (custo por política; mantém o nome do arquivo)
  fig64_pipeline_arquitetura_integrada.png  textos com os números oficiais

Grava em overleaf_dissertacao_udesc/figuras, graficos, charts e projeto_dissertacao/graficos.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import hipoteses_oficiais as h  # noqa: E402

LOGS = ROOT / "dissertacao_frotas/resultados/logs"
DESTINOS = [ROOT / "overleaf_dissertacao_udesc/figuras", ROOT / "graficos", ROOT / "charts", ROOT / "projeto_dissertacao/graficos"]
FONTE = "Fonte: elaborado pelo autor (2026) a partir dos dados da SEA/SC."
br = h.br


def salvar(fig, nome):
    fig.text(0.01, 0.01, FONTE, fontsize=7.5, color="#555")
    fig.tight_layout(rect=[0, 0.04, 1, 0.97])
    for d in DESTINOS:
        if d.exists():
            fig.savefig(d / nome, dpi=250)
    plt.close(fig)
    print("Salvo:", nome)


def fig12():
    a = h.ABL
    fig, (x1, x2) = plt.subplots(1, 2, figsize=(10, 4.4))
    lab = ["Manutenção (M)", "Manutenção + Patrimônio (M+P)"]
    roc = [a["classificacao_semente42"]["roc_auc_M"], a["classificacao_semente42"]["roc_auc_MP"]]
    x1.bar(lab, roc, color=["#94a3b8", "#059669"], width=.45)
    for i, v in enumerate(roc):
        x1.text(i, v + .002, br(v, 4), ha="center", fontweight="bold", fontsize=9)
    x1.set_ylim(min(roc) - .03, max(roc) + .02); x1.set_ylabel("ROC-AUC (teste 2025–2026)")
    x1.set_title(f"Classificação: {h.V['h1_dif_roc']} (IC 95% {h.V['h1_ic_roc']})", fontsize=9.5, fontweight="bold")
    mae = [a["mae_M"], a["mae_MP"]]
    x2.bar(lab, mae, color=["#94a3b8", "#2563eb"], width=.45)
    for i, v in enumerate(mae):
        x2.text(i, v + 10, "R$ " + br(v), ha="center", fontweight="bold", fontsize=9)
    x2.set_ylim(min(mae) * .95, max(mae) * 1.03); x2.set_ylabel("MAE da regressão de custos (R$)")
    x2.set_title(f"Regressão: ganho {h.V['h1_ganho_mae']} (IC 95% {h.V['h1_ic_mae']})", fontsize=9.5, fontweight="bold")
    fig.suptitle(f"Figura 12 – Estudo ablativo M × M+P: H1 {h.H['H1']['decisao'].lower()} (meta de 15% no MAE)", fontweight="bold")
    salvar(fig, "fig12_ablativo_fontes_m_vs_mp.png")


def fig13():
    x = h.XAI["top_features_shap"]
    df = pd.DataFrame(x).sort_values("importancia_relativa_pct")
    fig, ax = plt.subplots(figsize=(8.5, 5))
    cores = ["#059669" if "patrimonio" in f or "idade" in f else "#2563eb" for f in df.feature]
    ax.barh(df.feature_label, df.importancia_relativa_pct, color=cores)
    for i, v in enumerate(df.importancia_relativa_pct):
        ax.text(v + .3, i, br(v, 1) + "%", va="center", fontsize=8)
    ax.set_xlabel("Participação na importância global (média de |SHAP|, %)")
    ax.set_title("Figura 13 – Importância global dos atributos pelo SHAP (classificador HistGB)", fontweight="bold")
    fig.text(0.55, 0.06, "Verde: patrimônio e idade · Azul: histórico de manutenção", fontsize=7.5, color="#333")
    salvar(fig, "fig13_importancia_atributos_xai.png")


def fig14():
    m, ci = h.MILP, h.CI
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    pol = ["Prática reconstruída\n(só obrigatórias)", "Heurística gulosa\n(benefício/custo)", "MILP (HiGHS)"]
    val = [ci["custo_inercial_as_is_brl"], ci["custo_heuristica_gulosa_brl"], m["solucao_inteira_mip_brl"]]
    b = ax.bar(pol, [v / 1e6 for v in val], color=["#dc2626", "#d99a00", "#0284c7"], width=.5)
    for r, v in zip(b, val):
        ax.text(r.get_x() + r.get_width() / 2, v / 1e6 + .4, "R$ " + br(v / 1e6) + " mi", ha="center", fontweight="bold", fontsize=9)
    ax.set_ylim(0, max(val) / 1e6 * 1.15); ax.set_ylabel("Custo esperado em 36 meses (R$ milhões)")
    ax.set_title(f"Figura 14 – Custo esperado por política no cenário S0: MILP {h.V['h3_economia_pct']} abaixo da prática reconstruída",
                 fontweight="bold", fontsize=9.5)
    fig.text(0.40, 0.012, "Instância semissintética: 2.000 veículos reais, custos e falhas gerados por fórmula.", fontsize=7.5, color="#333")
    salvar(fig, "fig14_otimizacao_sensibilidade_orcamento.png")


def fig64():
    c = json.loads((LOGS / "tabela_unica_resultados_oficiais.json").read_text(encoding="utf-8"))
    rows = c if isinstance(c, list) else next(v for v in c.values() if isinstance(v, list))
    val = {r["id"]: r["valor_oficial"] for r in rows}
    fig, ax = plt.subplots(figsize=(10.5, 5.2)); ax.axis("off")
    caixas = [
        (0.08, "Camada 1: Ingestão e auditoria\n• 77.867 OS (350.737 itens)\n• 34.280 bens patrimoniais\n• hash SHA-256 das fontes\n• saneamento rastreável", "#dbeafe", "#1e40af"),
        (0.32, "Camada 2: Anomalias\n• Isolation Forest ν = 0,85%\n• estabilidade entre sementes\n• triagem para auditoria\n• não substitui a fiscalização", "#fef3c7", "#b45309"),
        (0.56, "Camada 3: Modelos preditivos\n• classificação de risco (HistGB)\n• regressão de custos\n• validação temporal\n• SHAP para explicação", "#dcfce7", "#15803d"),
        (0.80, "Camada 4: Prescrição\n• MILP (HiGHS) com orçamento\n  e capacidade\n• comparação com prática\n  reconstruída e heurística", "#ede9fe", "#6b21a8"),
    ]
    for x, t, bg, bd in caixas:
        ax.add_patch(FancyBboxPatch((x, .55), .18, .32, boxstyle="round,pad=0.02", facecolor=bg, edgecolor=bd, lw=2, transform=ax.transAxes))
        ax.text(x + .09, .71, t, transform=ax.transAxes, ha="center", va="center", fontsize=7.8, fontweight="bold", color=bd)
    for x1, x2 in ((.26, .32), (.50, .56), (.74, .80)):
        ax.annotate("", xy=(x2, .71), xytext=(x1, .71), xycoords="axes fraction", arrowprops=dict(arrowstyle="->", color="#334155", lw=2.5))
    ax.add_patch(FancyBboxPatch((0.08, 0.10), 0.90, 0.30, boxstyle="round,pad=0.02", facecolor="#f8fafc", edgecolor="#64748b", lw=1.5, ls="--", transform=ax.transAxes))
    txt = ("SÍNTESE DOS RESULTADOS (PPGCAP / UDESC)\n"
           f"• Base: {val.get('M02', '77.867 OSs')} entre 2020 e 2026; R$ 198,81 mi orçados e R$ 138,76 mi aprovados\n"
           f"• H1 {h.H['H1']['decisao'].lower()}: ROC-AUC {h.V['h1_dif_roc']} e MAE {h.V['h1_ganho_mae']} com patrimônio · "
           f"H2 {h.H['H2']['decisao'].lower()}: SVR-RBF erra menos na regressão\n"
           f"• H3 {h.H['H3']['decisao'].lower()}: MILP {h.V['h3_economia_pct']} ({h.V['h3_economia_mi']}) abaixo da prática reconstruída (instância semissintética)\n"
           f"• H4 {h.H['H4']['decisao'].lower()}: LIME pouco fiel (R² {h.V['h4_lime_r2']}); concordância SHAP×LIME Jaccard {h.V['h4_jaccard']}")
    txt = txt.replace("$", r"\$")
    ax.text(0.53, 0.25, txt, transform=ax.transAxes, ha="center", va="center", fontsize=8.2, color="#0f172a", fontweight="bold")
    ax.set_title("Figura 64 – Arquitetura do pipeline: auditoria, previsão, explicação e prescrição", fontweight="bold", pad=15)
    salvar(fig, "fig64_pipeline_arquitetura_integrada.png")


def fig10():
    md = json.loads((LOGS / "relatorio_modelagem_preditiva.json").read_text(encoding="utf-8"))
    reg = md["metricas_regressao"]
    rs = h.SVR["resumo_media_dp"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
    nomes = [r["modelo"].replace("HistGradientBoosting", "HistGB").replace("Baseline Mediana", "Mediana") for r in reg]
    x = range(len(reg)); w = .38
    b1 = a1.bar([i - w / 2 for i in x], [r["mae_reais"] for r in reg], w, color="#1e3a8a", label="MAE")
    b2 = a1.bar([i + w / 2 for i in x], [r["rmse_reais"] for r in reg], w, color="#93c5fd", label="RMSE")
    for b in list(b1) + list(b2):
        a1.text(b.get_x() + b.get_width() / 2, b.get_height() + 40, br(b.get_height(), 0), ha="center", fontsize=7)
    a1.set_xticks(list(x)); a1.set_xticklabels(nomes, fontsize=8); a1.set_ylabel("Erro (R$ por veículo-mês)"); a1.legend(fontsize=8)
    a1.set_title("Treino completo (etapa 04)", fontsize=9.5, fontweight="bold")
    ms = ["SVR-RBF", "HistGradientBoosting", "RandomForest", "ExtraTrees"]
    vals = [rs[f"regressao|{m}"]["media"] for m in ms]; dps = [rs[f"regressao|{m}"]["dp"] for m in ms]
    a2.bar([m.replace("HistGradientBoosting", "HistGB") for m in ms], vals, yerr=dps, capsize=4, color=["#059669", "#1e3a8a", "#475569", "#64748b"])
    for i, v in enumerate(vals):
        a2.text(i, v + 25, br(v, 0), ha="center", fontsize=8, fontweight="bold")
    a2.set_ylim(min(vals) * .9, max(vals) * 1.06); a2.set_ylabel("MAE (R$), média de 5 sementes")
    a2.set_title("Mesma subamostra de 12.000 linhas (etapa 04c)", fontsize=9.5, fontweight="bold")
    fig.suptitle(f"Figura 10 – Erro dos regressores de custo: H2 {h.H['H2']['decisao'].lower()} (SVR-RBF erra menos na regressão)", fontweight="bold")
    salvar(fig, "fig10_comparativo_mae_rmse_modelos.png")


if __name__ == "__main__":
    for d in DESTINOS[1:]:
        d.mkdir(parents=True, exist_ok=True)
    fig10(); fig12(); fig13(); fig14(); fig64()

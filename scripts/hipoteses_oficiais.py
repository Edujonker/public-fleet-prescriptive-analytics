#!/usr/bin/env python3
"""
Fonte única dos resultados das hipóteses para todos os documentos do projeto.

Lê o certificado da etapa 09 e os JSONs das etapas 04b, 04c, 07, 07b e 08 e oferece:
  V        dicionário de valores formatados (pt-BR) usados nos textos
  H        decisões por hipótese (P1, H1–H4) com critério, evidência e ressalva
  bloco_html(), bloco_latex(), bloco_md()   tabela-resumo pronta para inserir
  frase(k) frase curta com decisão e evidência de uma hipótese
  SUBSTITUICOES  pares (antigo, novo) de números que identificam de forma única os resultados antigos

Uso nos geradores:  from hipoteses_oficiais import V, H, bloco_html
Uso na linha de comando (resumo):  .venv/bin/python scripts/hipoteses_oficiais.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "dissertacao_frotas/resultados/logs"


def _j(n):
    return json.loads((LOGS / n).read_text(encoding="utf-8"))


def br(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


CERT = _j("certificado_reprodutibilidade_cientifica.json")
ABL = _j("relatorio_ablacao_h1.json")
SVR = _j("relatorio_h2_svr.json")
XAI = _j("relatorio_explicabilidade_xai.json")
FID = _j("relatorio_h4_fidelidade_estabilidade.json")
MILP = _j("relatorio_otimizacao_milp.json")
CI = MILP["confronto_inercial"]
CMP = SVR["comparacao_pareada_semente42"]["HistGradientBoosting"]

V = {
    "h1_ganho_mae": br(100 * ABL["ganho_mae_pct"]) + "%",
    "h1_ic_mae": f"{br(100 * ABL['ic95_ganho_bootstrap_pareado'][0])}% a {br(100 * ABL['ic95_ganho_bootstrap_pareado'][1])}%",
    "h1_delta_mae": "R$ " + br(ABL["delta_mae_reais"]),
    "h1_mae_m": "R$ " + br(ABL["mae_M"]), "h1_mae_mp": "R$ " + br(ABL["mae_MP"]),
    "h1_dif_roc": "+" + br(ABL["dif_roc_auc_MP_menos_M"], 4),
    "h1_ic_roc": f"{br(ABL['ic95_dif_roc_auc'][0], 4)} a {br(ABL['ic95_dif_roc_auc'][1], 4)}",
    "h2_dif_mae_svr": "+" + br(100 * CMP["dif_mae_rel_vs_svr"]) + "%",
    "h2_ic_mae_svr": f"{br(100 * CMP['ic95_dif_mae_rel'][0])}% a {br(100 * CMP['ic95_dif_mae_rel'][1])}%",
    "h2_dif_auc_svc": "+" + br(CMP["dif_auc_vs_svc"], 4),
    "h2_ic_auc_svc": f"{br(CMP['ic95_dif_auc'][0], 4)} a {br(CMP['ic95_dif_auc'][1], 4)}",
    "roc_histgb": br(CERT["comparacao_logistica_descritiva"]["roc_histgb"], 4),
    "roc_logistica": br(CERT["comparacao_logistica_descritiva"]["roc_logistica"], 4),
    "mae_histgb": "R$ " + br(CERT["comparacao_logistica_descritiva"]["mae_histgb"]),
    "h3_economia_pct": br(CI["economia_pct"]) + "%",
    "h3_economia_brl": "R$ " + br(CI["economia_prescritiva_brl"]),
    "h3_economia_mi": "R$ " + br(CI["economia_prescritiva_brl"] / 1e6) + " mi",
    "h3_bl0": "R$ " + br(CI["custo_inercial_as_is_brl"]),
    "h3_heur": "R$ " + br(CI["custo_heuristica_gulosa_brl"]),
    "h3_milp": "R$ " + br(MILP["solucao_inteira_mip_brl"]),
    "h3_lp": "R$ " + br(MILP["relaxacao_linear_lp_brl"]),
    "h3_gap_abs": "R$ " + br(MILP["integrality_gap_absoluto_brl"]),
    "h3_gap_rel": br(100 * MILP["integrality_gap_relativo"], 5) + "%",
    "h3_vs_heur_brl": "R$ " + br(CI["economia_vs_heuristica_brl"]),
    "h4_spearman": br(XAI["spearman_rho_medio"], 4),
    "h4_jaccard": br(100 * XAI["jaccard_top5_medio"]) + "%",
    "h4_lime_r2": br(FID["medidas"]["F2_lime_r2_medio"], 3),
    "h4_lime_estab": br(FID["medidas"]["E1_lime_jaccard_medio"], 3),
    "h4_shap_estab": br(FID["medidas"]["E2_shap_spearman_medio"], 3),
}

H = {}
for k, v in CERT["hipoteses"].items():
    m = next(x for x in CERT["matriz_hipoteses"] if x["id"] == k)
    H[k] = {"nome": m["hipotese"], "decisao": v["decisao"], "evidencia": v["evidencia"], "ressalva": v["ressalva"],
            "crit_ante": m["criterio_anteprojeto"], "ok_ante": m["atende_anteprojeto"],
            "crit_lim": m["criterio_limiar"], "ok_lim": m["atende_limiar"]}

# Ordem de apresentação: da hipótese menos sustentada para a mais sustentada, calculada a partir das decisões
# do certificado (os rótulos P1 e H1–H4 são os pré-registrados e não mudam). Critérios, em sequência:
#   1. decisão (NÃO SUSTENTADA < PARCIALMENTE SUSTENTADA < SUSTENTADA);
#   2. fração dos critérios atendidos;
#   3. mais critérios não atendidos vem antes;
#   4. com ressalva vem antes de sem ressalva.
_RANK = {"NÃO SUSTENTADA": 0, "PARCIALMENTE SUSTENTADA": 1, "SUSTENTADA": 2}


def _chave_ordem(k):
    h = H[k]
    oks = [x for x in (h["ok_ante"], h["ok_lim"]) if x in ("sim", "não")]
    atend = sum(x == "sim" for x in oks)
    return (_RANK[h["decisao"]], atend / len(oks) if oks else 0.0, -(len(oks) - atend), 0 if h["ressalva"] else 1)


ORDEM = sorted(H, key=_chave_ordem)
REGRA_ORDEM = ("Hipóteses apresentadas da menos para a mais sustentada; os rótulos P1 e H1–H4 são os do pré-registro.")
FRASES = {
    "P1": f"P1 (não normalidade dos custos) foi sustentada: {H['P1']['evidencia']}.",
    "H1": (f"H1 foi parcialmente sustentada: incluir o patrimônio melhora a ROC-AUC em {V['h1_dif_roc']} (IC 95% {V['h1_ic_roc']}), "
           f"mas reduz o MAE em apenas {V['h1_ganho_mae']} (IC 95% {V['h1_ic_mae']}), abaixo da meta de 15%."),
    "H2": (f"H2 não foi sustentada: os ensembles superam o SVC-RBF na classificação (AUC {V['h2_dif_auc_svc']}), "
           f"mas erram {V['h2_dif_mae_svr'].lstrip('+')} a mais que o SVR-RBF na regressão de custos (IC 95% {V['h2_ic_mae_svr']})."),
    "H3": (f"H3 foi sustentada no cenário S0: a política MILP custa {V['h3_milp']}, {V['h3_economia_pct']} ({V['h3_economia_mi']}) "
           f"menos que a prática reconstruída ({V['h3_bl0']}); a heurística gulosa chega praticamente ao mesmo custo "
           f"(diferença de {V['h3_vs_heur_brl']}), e a instância é semissintética."),
    "H4": (f"H4 não foi sustentada: o SHAP é exato e estável (estabilidade {V['h4_shap_estab']}), mas o LIME é pouco fiel ao modelo "
           f"(R² local {V['h4_lime_r2']}) e a concordância SHAP × LIME fica em Spearman {V['h4_spearman']} e Jaccard {V['h4_jaccard']}, "
           f"abaixo de 0,85."),
}


def frase(k):
    return FRASES[k]


def _linhas():
    sn = {"sim": "sim", "não": "não", "—": "—"}
    return [(k, H[k]["nome"].split(":", 1)[-1].strip(), H[k]["crit_ante"], sn.get(H[k]["ok_ante"], H[k]["ok_ante"]),
             H[k]["crit_lim"], sn.get(H[k]["ok_lim"], H[k]["ok_lim"]), H[k]["decisao"]) for k in ORDEM]


CAB = ["", "Hipótese", "Critério do anteprojeto", "Atende", "Limiar pré-registrado", "Atende", "Decisão"]


def bloco_html(estilo_th="background:#1b3a6e;color:#fff;text-align:left;padding:3pt 5pt",
               estilo_td="border-bottom:.5pt solid #c5cfdf;padding:2.5pt 5pt;vertical-align:top") -> str:
    e = html.escape
    t = ["<table style='width:100%;border-collapse:collapse;font-size:8.6pt;margin:4pt 0 8pt'><tr>"
         + "".join(f"<th style='{estilo_th}'>{e(c)}</th>" for c in CAB) + "</tr>"]
    for l in _linhas():
        t.append("<tr>" + "".join(f"<td style='{estilo_td}'>{'<b>' + e(c) + '</b>' if i == 6 else e(c)}</td>" for i, c in enumerate(l)) + "</tr>")
    t.append("</table><ul style='font-size:9pt'>" + "".join(f"<li>{e(FRASES[k])}</li>" for k in ORDEM) + "</ul>")
    return "".join(t)


def _tex(s):
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("≥", r"$\geq$"), ("≤", r"$\leq$"), ("×", r"$\times$"), ("−", "-"), ("²", r"$^2$"), ("ρ", r"$\rho$")):
        s = s.replace(a, b)
    return s


def bloco_latex(rotulo="tab:hipoteses") -> str:
    L = [r"\begin{table}[H]", r"\centering\scriptsize",
         r"\caption{Avaliação das hipóteses pelo critério do anteprojeto e pelo limiar pré-registrado}", f"\\label{{{rotulo}}}",
         r"\begin{tabular}{p{0.04\textwidth}p{0.17\textwidth}p{0.22\textwidth}p{0.05\textwidth}p{0.17\textwidth}p{0.05\textwidth}p{0.14\textwidth}}",
         r"\hline", " & ".join(f"\\textbf{{{_tex(c)}}}" for c in CAB) + r" \\ \hline"]
    L += [" & ".join(_tex(str(c)) for c in l) + r" \\" for l in _linhas()]
    L += [r"\hline", r"\end{tabular}", r"\fonte{Elaborado pelo autor (2026), a partir de \texttt{certificado\_reprodutibilidade\_cientifica.json}.}", r"\end{table}", ""]
    L += [r"\begin{itemize}"] + [f"  \\item {_tex(FRASES[k])}" for k in ORDEM] + [r"\end{itemize}"]
    return "\n".join(L)


def bloco_md() -> str:
    L = ["| " + " | ".join(CAB) + " |", "|" + "---|" * len(CAB)]
    L += ["| " + " | ".join(str(c) for c in l) + " |" for l in _linhas()]
    return "\n".join(L) + "\n\n" + "\n".join(f"- {FRASES[k]}" for k in ORDEM) + "\n"


# Números antigos que identificam de forma única os resultados substituídos.
# Usado por scripts/propagar_hipoteses.py. Ordem importa (do mais longo ao mais curto).
SUBSTITUICOES = [
    ("R$ 9.302.147,26", V["h3_economia_brl"]), ("R$ 9,302,147.26", V["h3_economia_brl"]),
    ("9.302.147,26", V["h3_economia_brl"].replace("R$ ", "")), ("9302147.26", f"{CI['economia_prescritiva_brl']:.2f}"),
    ("R$ 53.139.780,57", V["h3_bl0"]), ("R$ 43.837.633,31", V["h3_milp"]), ("R$ 43.837.384,79", V["h3_lp"]),
    ("R$ 248,52", V["h3_gap_abs"]), ("0,000567%", V["h3_gap_rel"]), ("0,00057%", V["h3_gap_rel"]),
    ("R$ 9,30 milhões", V["h3_economia_mi"].replace(" mi", " milhões")), ("R$ 9,30 mi", V["h3_economia_mi"]),
    ("R$ 9,30M", V["h3_economia_mi"]), ("R$ 9,3 mi", V["h3_economia_mi"]),
    ("17,51%", V["h3_economia_pct"]), ("17.51%", f"{CI['economia_pct']:.2f}%"),
    ("+0,41%", "+" + V["h1_ganho_mae"]), ("0,41%", V["h1_ganho_mae"]),
    ("R$ 9,47", V["h1_delta_mae"]), ("[0,28%; 0,54%]", f"[{V['h1_ic_mae'].replace(' a ', '; ')}]"),
    ("R$ 2.311,82", V["h1_mae_mp"]), ("R$ 2.321,28", V["h1_mae_m"]),
    ("0,3680", V["h4_spearman"]), ("ρ = 0,368", "ρ = " + br(XAI["spearman_rho_medio"], 3)),
    ("39,29%", V["h4_jaccard"]), ("39,3%", br(100 * XAI["jaccard_top5_medio"], 1) + "%"),
    ("0,7366", V["roc_logistica"]), ("0,8268", V["roc_logistica"]), ("0,8743", V["roc_histgb"]),
    ("0,28%; 0,54%", V["h1_ic_mae"].replace(" a ", "; ")), ("0,28\\%; 0,54\\%", V["h1_ic_mae"].replace(" a ", "; ").replace("%", "\\%")),
    ("313 veículos", "242 veículos"), ("313 viaturas", "242 viaturas"), ("313 uneconomical", "242 uneconomical"), ("313 vehicles", "242 vehicles"),
]


if __name__ == "__main__":
    for k in ORDEM:
        print(f"{k}: {H[k]['decisao']}\n   {FRASES[k]}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figura didática da Hipótese H4 (SHAP x LIME) para o slide 8 da apresentação.

Usa SOMENTE valores presentes nos arquivos do projeto:
  - Observado: dissertacao_frotas/resultados/logs/relatorio_explicabilidade_xai.json
      jaccard_top5_medio = 0.3929 ; spearman_rho_medio = 0.368
  - Metas (Jaccard > 0,85 e Spearman > 0,85): critério de decisão em
      dissertacao_frotas/src/09_validacao_estatistica.py (h4_sustentada)
O diagrama é conceitual: não mostra um caso específico nem nomes de variáveis.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
XAI_JSON = ROOT / "dissertacao_frotas" / "resultados" / "logs" / "relatorio_explicabilidade_xai.json"
OUT = ROOT / "SIC" / "img" / "h4_shap_lime_concordancia.png"

dados = json.loads(XAI_JSON.read_text(encoding="utf-8"))
jaccard = float(dados["jaccard_top5_medio"])      # 0.3929
spearman = float(dados["spearman_rho_medio"])     # 0.368
META_JACCARD = 0.85
META_SPEARMAN = 0.85

VERDE = "#005B2E"
VERDE_CLR = "#2EA84B"
AZUL = "#1B3A6E"
VERM = "#A00000"
CINZA = "#8A94A6"
FUNDO = "#F4F6FB"


def pct(v):
    return f"{v*100:.1f}".replace(".", ",") + "%"


def dec(v):
    return f"{v:.2f}".replace(".", ",")


fig = plt.figure(figsize=(8.2, 5.0), dpi=220)

# ── Painel superior: fluxo conceitual ────────────────────────────────────────
ax1 = fig.add_axes([0.02, 0.58, 0.96, 0.40])
ax1.set_xlim(0, 100)
ax1.set_ylim(0, 40)
ax1.axis("off")


def caixa(ax, x, y, w, h, texto, fc, tc="white", fs=12, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=2",
                                fc=fc, ec="none"))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center",
            color=tc, fontsize=fs, fontweight="bold" if bold else "normal",
            linespacing=1.25)


def seta(ax, p0, p1):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=16,
                                 lw=2, color=CINZA))


caixa(ax1, 1, 12, 22, 16, "Mesma previsão\ndo modelo", AZUL)
caixa(ax1, 35, 24, 26, 14, "SHAP\nteoria dos jogos", VERDE)
caixa(ax1, 35, 2, 26, 14, "LIME\nmodelo linear local", VERDE_CLR)
caixa(ax1, 73, 11, 26, 18, "Comparam os 5\nfatores que mais\npesaram", VERM, fs=11.5)

seta(ax1, (24, 22), (34.2, 30))
seta(ax1, (24, 18), (34.2, 10))
seta(ax1, (62, 30), (72.2, 24))
seta(ax1, (62, 10), (72.2, 16))

# ── Painel inferior: meta x observado ────────────────────────────────────────
ax2 = fig.add_axes([0.285, 0.17, 0.69, 0.31])
ax2.set_facecolor(FUNDO)
for s in ("top", "right"):
    ax2.spines[s].set_visible(False)

rotulos = ["Coincidência no Top-5\n(índice de Jaccard)",
           "Concordância na ordem\n(correlação de Spearman)"]
metas = [META_JACCARD, META_SPEARMAN]
obs = [jaccard, spearman]
txt_meta = [">" + f"{META_JACCARD*100:.0f}%", ">" + dec(META_SPEARMAN)]
txt_obs = [pct(jaccard), dec(spearman)]

ypos = [1.0, 0.0]
h = 0.30
for y, m, o, tm, to in zip(ypos, metas, obs, txt_meta, txt_obs):
    ax2.barh(y + h / 2 + 0.02, m, height=h, color="white", edgecolor=CINZA,
             hatch="///", lw=1.2)
    ax2.barh(y - h / 2 - 0.02, o, height=h, color=VERM)
    ax2.text(m + 0.015, y + h / 2 + 0.02, "meta " + tm, va="center", fontsize=12,
             color="#444444")
    ax2.text(o + 0.015, y - h / 2 - 0.02, "obtido " + to, va="center", fontsize=12.5,
             color=VERM, fontweight="bold")

ax2.set_yticks(ypos)
ax2.set_yticklabels(rotulos, fontsize=11.5, color="#222222")
ax2.set_xlim(0, 1.13)
ax2.set_ylim(-0.55, 1.55)
ax2.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax2.set_xticklabels(["0", "0,25", "0,5", "0,75", "1 (total)"], fontsize=10.5)
ax2.set_xlabel("Escala de concordância (1 = as duas explicações coincidem por completo)",
               fontsize=10.5, color="#333333")
fig.text(0.02, 0.535, "Meta da hipótese × resultado observado", fontsize=13,
         fontweight="bold", color=AZUL, ha="left", va="center")

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, facecolor="white")
print(f"Figura salva em: {OUT}")
print(f"  jaccard={jaccard}  spearman={spearman}")

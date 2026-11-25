#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera gráficos comparativos claros e objetivos:
1. PCA 2025 Oficial vs Modelo Prescritivo (treinado até dez/2024)
2. Evolução Bienal Comparativa (2025 e 2026): PCA Oficial (Locação) vs Modelo Prescritivo (Manutenção)

Salva em:
  - resultados_loa_pca_2026/fig_comparativo_pca_2025_real_vs_estimado.png
  - resultados_loa_pca_2026/fig_comparativo_pca_bienal_2025_2026.png
  - overleaf_dissertacao_udesc/figuras/
  - charts/
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RES_DIR = ROOT / "resultados_loa_pca_2026"
FIG_OVERLEAF = ROOT / "overleaf_dissertacao_udesc" / "figuras"
CHARTS_DIR = ROOT / "charts"

for d in [RES_DIR, FIG_OVERLEAF, CHARTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# DADOS 2025: TREINAMENTO ATÉ DEZ/2024 -> COMPARAÇÃO COM PCA 2025
# -------------------------------------------------------------------------
pca_2025_oficial = 43.67                 # R$ 43,67 mi (PE 593/2025 - docs/PCA 2025.pdf)
mod_2025_empenho = 37.56                 # R$ 37,56 mi (Projeção anual na escala de empenhos)
mod_2025_os = 32.28                      # R$ 32,28 mi (Projeção anual no censo de OS SEA/SC)
empenho_real_2025 = 41.78                # R$ 41,78 mi (Execução real no balanço SEF/SC)

dif_2025_empenho = pca_2025_oficial - mod_2025_empenho # R$ 6,11 mi (-14,0%)
dif_2025_os = pca_2025_oficial - mod_2025_os           # R$ 11,39 mi (-26,1%)

# -------------------------------------------------------------------------
# DADOS 2026: PROJEÇÃO 2026 -> COMPARAÇÃO COM PCA 2026
# -------------------------------------------------------------------------
pca_2026_oficial = 90.68                 # R$ 90,68 mi (docs/PCA-E 2026.pdf)
mod_2026_empenho = 47.10                 # R$ 47,10 mi (Projeção anual na escala de empenhos)
mod_2026_os = 33.59                      # R$ 33,59 mi (Projeção anual no censo de OS SEA/SC)

# -------------------------------------------------------------------------
# FIGURA 1: COMPARATIVO DIRETO 2025 (TREINO ATÉ DEZ/2024)
# -------------------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig1, ax1 = plt.subplots(figsize=(10.5, 6.4))
fig1.patch.set_facecolor('#ffffff')

colunas_2025 = [
    "PCA 2025 Oficial\n(Locação de Frotas\nSEA/SC)",
    "Modelo Prescritivo\n(Treino até dez/2024\nEscala Empenho)",
    "Modelo Prescritivo\n(Treino até dez/2024\nCenso OS SEA)",
    "Execução Real\nEmpenho 2025\n(SEF/SC)"
]

valores_2025 = [pca_2025_oficial, mod_2025_empenho, mod_2025_os, empenho_real_2025]
cores_2025 = ['#b91c1c', '#1d4ed8', '#0284c7', '#475569']

barras1 = ax1.bar(colunas_2025, valores_2025, color=cores_2025, width=0.48, edgecolor='#0f172a', linewidth=1.2, zorder=3)

for bar, val in zip(barras1, valores_2025):
    y = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, y + 0.8, f"R$ {val:.2f} mi",
             ha='center', va='bottom', fontsize=11.5, fontweight='bold', color='#0f172a')

# Seta e indicação de diferença
ax1.annotate('', xy=(1, mod_2025_empenho), xytext=(0, pca_2025_oficial),
             arrowprops=dict(arrowstyle='<->', color='#dc2626', lw=2, shrinkA=8, shrinkB=8))

ax1.text(0.5, 41.5, f"DIFERENÇA = -R$ {dif_2025_empenho:.2f} mi (-{dif_2025_empenho/pca_2025_oficial*100:.1f}%)",
         ha='center', va='center', fontsize=10.5, fontweight='bold', color='#991b1b',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#fee2e2', edgecolor='#f87171', lw=1.2), zorder=5)

ax1.set_title("EXERCÍCIO 2025: MODELO TREINADO ATÉ DEZ/2024 vs. PCA 2025 OFICIAL",
              fontsize=13, fontweight='bold', color='#0f172a', pad=18)
ax1.set_ylabel("Valor Anual (R$ Milhões)", fontsize=11, fontweight='bold', color='#1e293b')
ax1.set_ylim(0, 52)
ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax1.tick_params(axis='x', labelsize=10)

texto_porques_2025 = (
    "ENTENDIMENTO DOS PORQUÊS DA DIFERENÇA EM 2025:\n"
    "• Objeto do PCA 2025: Planejou R$ 43,67 mi no PE 593/2025 exclusivamente para LOCAÇÃO CORPORATIVA de veículos terceirizados.\n"
    "• Objeto do Modelo: Estimou a MANUTENÇÃO MECÂNICA da frota própria com treino até dez/2024 (R$ 37,56 mi empenho / R$ 32,28 mi OS).\n"
    "• Validação Retrospectiva Sólida: Na avaliação retrospectiva BT2, o modelo errou apenas +9,81% frente aos dados observados da SEA/SC.\n"
    "• Comparativo Institucional: O custo de manter a frota própria estadual em 2025 foi 14% a 26% menor que o valor alocado em locação."
)

fig1.text(0.08, 0.02, texto_porques_2025, fontsize=8.8, color='#334155',
          bbox=dict(boxstyle='square,pad=0.6', facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1))

plt.subplots_adjust(bottom=0.22)

fig1.savefig(RES_DIR / "fig_comparativo_pca_2025_real_vs_estimado.png", dpi=300, bbox_inches='tight')
fig1.savefig(FIG_OVERLEAF / "fig_comparativo_pca_2025_real_vs_estimado.png", dpi=300, bbox_inches='tight')
fig1.savefig(CHARTS_DIR / "fig_comparativo_pca_2025_real_vs_estimado.png", dpi=300, bbox_inches='tight')
plt.close(fig1)

# -------------------------------------------------------------------------
# FIGURA 2: COMPARATIVO BIENAL 2025 vs 2026 (EVOLUÇÃO HISTÓRICA DO PCA vs MODELO)
# -------------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(11, 6.2))
fig2.patch.set_facecolor('#ffffff')

import numpy as np
x = np.arange(2)
larg = 0.35

bar_pca = ax2.bar(x - larg/2, [pca_2025_oficial, pca_2026_oficial], width=larg, label="PCA Oficial SEA/SC (Locação de Frotas)", color='#b91c1c', edgecolor='#0f172a', zorder=3)
bar_mod = ax2.bar(x + larg/2, [mod_2025_empenho, mod_2026_empenho], width=larg, label="Modelo Prescritivo (Manutenção Frota Própria)", color='#1d4ed8', edgecolor='#0f172a', zorder=3)

# Valores sobre as barras
for bar in bar_pca:
    y = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, y + 1.5, f"R$ {y:.2f} mi", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#991b1b')

for bar in bar_mod:
    y = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, y + 1.5, f"R$ {y:.2f} mi", ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1e3a8a')

ax2.set_xticks(x)
ax2.set_xticklabels(["Exercício 2025\n(Treino até dez/2024)", "Exercício 2026\n(Treino até set/2025)"], fontsize=11, fontweight='bold')
ax2.set_ylabel("Valor Total Orçado / Estimado (R$ Milhões)", fontsize=11, fontweight='bold', color='#1e293b')
ax2.set_title("EVOLUÇÃO BIENAL: PCA OFICIAL (LOCAÇÃO) vs. MODELO PRESCRITIVO (MANUTENÇÃO)", fontsize=13, fontweight='bold', color='#0f172a', pad=18)
ax2.set_ylim(0, 108)
ax2.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax2.legend(loc='upper left', fontsize=10.5, framealpha=0.95)

# Anotações dos porquês
ax2.annotate('Alta de +107,6% no PCA\n(Entrada da Nova Contratação\nSEA 22719 de R$ 47,01 mi)',
             xy=(1 - larg/2, pca_2026_oficial), xytext=(0.45, 85),
             arrowprops=dict(facecolor='#b91c1c', shrink=0.08, width=1.2, headwidth=6),
             fontsize=9, fontweight='bold', color='#991b1b',
             bbox=dict(boxstyle="round,pad=0.4", fc="#fff5f5", ec="#feb2b2", lw=1))

ax2.annotate('Crescimento Orgânico da Manutenção\n(+25,4% entre 2025 e 2026)\nassociado ao envelhecimento da frota',
             xy=(1 + larg/2, mod_2026_empenho), xytext=(1.05, 62),
             arrowprops=dict(facecolor='#1d4ed8', shrink=0.08, width=1.2, headwidth=6),
             fontsize=9, fontweight='bold', color='#1e3a8a',
             bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#bfdbfe", lw=1))

plt.tight_layout()

fig2.savefig(RES_DIR / "fig_comparativo_pca_bienal_2025_2026.png", dpi=300, bbox_inches='tight')
fig2.savefig(FIG_OVERLEAF / "fig_comparativo_pca_bienal_2025_2026.png", dpi=300, bbox_inches='tight')
fig2.savefig(CHARTS_DIR / "fig_comparativo_pca_bienal_2025_2026.png", dpi=300, bbox_inches='tight')
plt.close(fig2)

print("✓ Figuras do PCA 2025 e Bienal geradas com sucesso!")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera gráfico técnico de projeção de gastos de frotas (2022 a 2029) e análise de viabilidade econômica:
Manutenção da Frota Própria (Inercial vs Prescritiva MILP) vs Locação de Veículos (PCA 2025/2026 e Projeção).

Salva em:
  - resultados_loa_pca_2026/fig_projecao_gastos_2028_2029_locacao_vs_propria.png
  - overleaf_dissertacao_udesc/figuras/
  - charts/
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RES_DIR = ROOT / "resultados_loa_pca_2026"
FIG_OVERLEAF = ROOT / "overleaf_dissertacao_udesc" / "figuras"
CHARTS_DIR = ROOT / "charts"

for d in [RES_DIR, FIG_OVERLEAF, CHARTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# SÉRIES TEMPORAIS HISTÓRICAS E PROJETADAS (2022 a 2029)
# -------------------------------------------------------------------------
anos = np.array([2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029])

# 1. Manutenção da Frota Própria (Escala de Empenhos SEF/SC):
# 2022-2023: estimado proporcional; 2024-2025: realizado real; 2026: experimento; 2027-2029: projetado
manut_inercial = np.array([31.96, 33.87, 37.65, 41.78, 47.10, 51.63, 56.35, 61.08])
# Com otimização prescritiva MILP (redução média certificada de 13,66% em H3):
manut_milp = manut_inercial * (1 - 0.1366)

# 2. Locação Corporativa de Frotas (Valores Oficiais do PCA e Tendência):
# 2024: histórico PE anterior ~ R$ 40 mi; 2025: PCA R$ 43,67 mi; 2026: PCA R$ 90,68 mi
# A partir de 2026, com contratos plurianuais licitados (SEA 22719 + PE 593):
locacao_oficial = np.array([38.50, 40.20, 41.50, 43.67, 90.68, 93.40, 96.20, 99.08])

# -------------------------------------------------------------------------
# FIGURA DE ALTA RESOLUÇÃO: 2 PAINÉIS ANALÍTICOS
# -------------------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5), gridspec_kw={'width_ratios': [1.35, 1]})
fig.patch.set_facecolor('#ffffff')

# Painel 1: Séries Temporais Longitudinais e Projeção até 2029
ax1.plot(anos[:5], locacao_oficial[:5], 'o-', color='#b91c1c', lw=2.4, ms=7, label="Locação de Frota (PCA Oficial SEA/SC)", zorder=4)
ax1.plot(anos[4:], locacao_oficial[4:], 'o--', color='#b91c1c', lw=2, ms=6, alpha=0.7, zorder=3)

ax1.plot(anos[:5], manut_inercial[:5], 's-', color='#2563eb', lw=2.2, ms=6.5, label="Manutenção Frota Própria (Inercial / Empenhos)", zorder=4)
ax1.plot(anos[4:], manut_inercial[4:], 's--', color='#2563eb', lw=1.8, ms=5.5, alpha=0.7, zorder=3)

ax1.plot(anos[4:], manut_milp[4:], '^-', color='#059669', lw=2.2, ms=6.5, label="Manutenção Prescritiva MILP (-13,66% em H3)", zorder=4)

# Linha divisória histórica vs projetada
ax1.axvline(x=2026, color='#64748b', linestyle=':', lw=1.5, alpha=0.8)
ax1.text(2025.85, 103, "Histórico / Experimento | Projeção Futura (2028-2029)", ha='right', va='top', fontsize=8.5, fontweight='bold', color='#475569')

# Rótulos dos pontos 2028 e 2029
ax1.text(2028, locacao_oficial[6] + 2.5, f"R$ {locacao_oficial[6]:.1f} mi", ha='center', fontsize=9, fontweight='bold', color='#991b1b')
ax1.text(2029, locacao_oficial[7] + 2.5, f"R$ {locacao_oficial[7]:.1f} mi", ha='center', fontsize=9, fontweight='bold', color='#991b1b')

ax1.text(2028, manut_inercial[6] - 4.5, f"R$ {manut_inercial[6]:.1f} mi\n(MILP: R$ {manut_milp[6]:.1f} mi)", ha='center', fontsize=8.5, fontweight='bold', color='#1e40af')
ax1.text(2029, manut_inercial[7] - 4.5, f"R$ {manut_inercial[7]:.1f} mi\n(MILP: R$ {manut_milp[7]:.1f} mi)", ha='center', fontsize=8.5, fontweight='bold', color='#1e40af')

ax1.set_title("A. Evolução Longitudinal e Projeção Orçamentária de Gastos (2022–2029)", fontsize=11.5, fontweight='bold', pad=14, color='#0f172a')
ax1.set_ylabel("Valor Anual (R$ Milhões)", fontsize=10.5, fontweight='bold', color='#1e293b')
ax1.set_xlabel("Exercício Orçamentário", fontsize=10.5, fontweight='bold', color='#1e293b')
ax1.set_ylim(20, 115)
ax1.set_xticks(anos)
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend(loc='upper left', fontsize=8.8, framealpha=0.95)

# Painel 2: Análise de Vantajosidade Econômica e TCO Unitário (2026–2029)
categorias_tco = [
    "Locação de Veículo\n(Custo Médio Anual\npor Carro Alugado)",
    "Frota Própria\n(Manutenção Inercial\npor Carro Próprio)",
    "Frota Própria\n(Manutenção MILP\npor Carro Próprio)"
]
# Valores médios anuais por veículo (R$ / veículo-ano)
# Carro locado: R$ 90,68 mi / ~2.000 carros ≈ R$ 45.340 / ano (R$ 3.778/mês)
# Carro próprio: R$ 47,10 mi / 5.000 carros ativos ≈ R$ 9.420 / ano (R$ 785/mês)
# Carro próprio MILP: R$ 40,67 mi / 5.000 carros ≈ R$ 8.134 / ano (R$ 678/mês)
valores_tco = [45.34, 9.42, 8.13]
cores_tco = ['#b91c1c', '#2563eb', '#059669']

barras2 = ax2.bar(categorias_tco, valores_tco, color=cores_tco, width=0.48, edgecolor='#0f172a', lw=1.2, zorder=3)

for bar, val in zip(barras2, valores_tco):
    y = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, y + 1.2, f"R$ {val:.2f} mil/ano\n(~R$ {val/12*1000:.0f}/mês)",
             ha='center', va='bottom', fontsize=9.2, fontweight='bold', color='#0f172a')

# Seta de Razão de Vantajosidade
ax2.annotate(f"Locação é 4,8x a 5,6x mais cara\npor veículo/ano do que manter\na frota própria em atividade!",
             xy=(0, 45.34), xytext=(0.4, 32),
             arrowprops=dict(facecolor='#b91c1c', shrink=0.08, width=1.4, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#991b1b',
             bbox=dict(boxstyle="round,pad=0.4", fc="#fff5f5", ec="#feb2b2", lw=1))

ax2.set_title("B. Análise de Vantajosidade: Custo Unitário por Veículo-Ano", fontsize=11.5, fontweight='bold', pad=14, color='#0f172a')
ax2.set_ylabel("Custo Anual por Veículo (R$ Milhares)", fontsize=10.5, fontweight='bold', color='#1e293b')
ax2.set_ylim(0, 56)
ax2.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax2.tick_params(axis='x', labelsize=8.8)

# Caixa inferior explicativa
texto_rodape = (
    "DIAGNÓSTICO TÉCNICO-CIENTÍFICO DE VANTAJOSIDADE:\n"
    "1. Volume de Frota Locada: O salto do PCA (R$ 43,67 mi -> R$ 90,68 mi) financia aproximadamente 2.000 a 2.150 veículos alugados.\n"
    "2. Projeção de Manutenção 2028-2029: Inercial de R$ 56,35 mi (2028) e R$ 61,08 mi (2029); com MILP: R$ 48,65 mi (2028) e R$ 52,73 mi (2029).\n"
    "3. Conclusão de Eficiência: Locar a frota inteira seria inviável ao erário (exigiria ~R$ 340 milhões anuais para substituir os 7.580 veículos). "
    "A locação é vantajosa apenas como complemento tático em áreas policiais severas; para o restante, a manutenção própria é até 5,6x mais econômica."
)

fig.text(0.06, 0.01, texto_rodape, fontsize=8.2, color='#334155',
         bbox=dict(boxstyle='square,pad=0.5', facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1))

plt.subplots_adjust(bottom=0.20)

fig.savefig(RES_DIR / "fig_projecao_gastos_2028_2029_locacao_vs_propria.png", dpi=300, bbox_inches='tight')
fig.savefig(FIG_OVERLEAF / "fig_projecao_gastos_2028_2029_locacao_vs_propria.png", dpi=300, bbox_inches='tight')
fig.savefig(CHARTS_DIR / "fig_projecao_gastos_2028_2029_locacao_vs_propria.png", dpi=300, bbox_inches='tight')
plt.close(fig)

print("✓ Gráfico de projeção e vantajosidade gerado com sucesso!")

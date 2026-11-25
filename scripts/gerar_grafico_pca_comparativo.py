#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera gráfico direto, limpo e descomplicado:
Previsão Prescritiva para o PCA vs PCA Oficial (Frotas 2026 SEA/SC) e a Diferença Explicada.
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
# DADOS OFICIAIS E EXATOS
# -------------------------------------------------------------------------
# 1. PCA Oficial 2026 (SEA/SC - docs/PCA-E 2026.pdf, p. 121-122):
#    Contratações compartilhadas planejadas para frotas (Locação de veículos):
#    - Nova Licitação (SEA 22719/2025): R$ 47,01 mi
#    - Prorrogação PE 593 (SEA 4749/2025): R$ 43,67 mi
#    TOTAL PCA OFICIAL = R$ 90,68 mi
val_pca_oficial = 90.68

# 2. Previsão Prescritiva / Preditiva para o PCA da Frota 2026:
#    (Demanda anual necessária de manutenção da frota própria planejada):
#    - Na escala de empenhos orçamentários oficiais (SEF/SC): R$ 47,10 mi
#    - Na base censitária líquida de ordens de serviço (SEA/SC): R$ 33,59 mi
val_prev_prescritiva_empenho = 47.10
val_prev_prescritiva_os = 33.59

# Diferença direta em relação ao valor orçamentário
dif_empenho = val_pca_oficial - val_prev_prescritiva_empenho # R$ 43,58 mi
dif_os = val_pca_oficial - val_prev_prescritiva_os           # R$ 57,09 mi

# -------------------------------------------------------------------------
# GERAÇÃO DA FIGURA: DIRETA, LIMPA E SEM CONFUSÃO
# -------------------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, ax = plt.subplots(figsize=(10, 6.2))
fig.patch.set_facecolor('#ffffff')

colunas = [
    "PCA 2026 Oficial\n(Frotas SEA/SC)",
    "Previsão Prescritiva\n(Escala Orçamentária)",
    "Previsão Prescritiva\n(Censo Líquido OS)"
]

valores = [val_pca_oficial, val_prev_prescritiva_empenho, val_prev_prescritiva_os]
cores = ['#b91c1c', '#1d4ed8', '#0284c7']

barras = ax.bar(colunas, valores, color=cores, width=0.48, edgecolor='#0f172a', linewidth=1.2, zorder=3)

# Adiciona valores monetários em destaque no topo
for bar, val in zip(barras, valores):
    y = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, y + 1.8, f"R$ {val:.2f} mi",
            ha='center', va='bottom', fontsize=12, fontweight='bold', color='#0f172a')

# Linha conectando o PCA Oficial à Previsão Prescritiva
ax.annotate('', xy=(1, val_prev_prescritiva_empenho), xytext=(0, val_pca_oficial),
            arrowprops=dict(arrowstyle='<->', color='#dc2626', lw=2, shrinkA=8, shrinkB=8))

# Caixa da Diferença
ax.text(0.5, 71, f"DIFERENÇA = R$ {dif_empenho:.2f} mi (-{dif_empenho/val_pca_oficial*100:.1f}%)",
        ha='center', va='center', fontsize=11, fontweight='bold', color='#991b1b',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#fee2e2', edgecolor='#f87171', lw=1.5), zorder=5)

# Linha de base da diferença censitária
ax.text(1.5, 42, f"Dif. Censo OS:\n-R$ {dif_os:.2f} mi",
        ha='center', va='center', fontsize=9, fontweight='bold', color='#0369a1',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#e0f2fe', edgecolor='#7dd3fc', lw=1), zorder=5)

# Formatação dos eixos
ax.set_title("COMPARATIVO DIRETO: PREVISÃO PRESCRITIVA vs. PCA 2026 OFICIAL (FROTAS)",
             fontsize=13, fontweight='bold', color='#0f172a', pad=18)
ax.set_ylabel("Valor Anual (R$ Milhões)", fontsize=11, fontweight='bold', color='#1e293b')
ax.set_ylim(0, 108)
ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax.tick_params(axis='x', labelsize=10.5)

# Caixa inferior explicativa dos porquês
texto_porques = (
    "ENTENDIMENTO DOS PORQUÊS DA DIFERENÇA:\n"
    "• Objeto Distinto: O PCA Oficial (R$ 90,68 mi) destina-se à LOCAÇÃO corporativa de veículos (frota alugada).\n"
    "• Frota Própria: A Previsão Prescritiva (R$ 47,10 mi / R$ 33,59 mi) modela a MANUTENÇÃO MECÂNICA da frota própria.\n"
    "• Causa Institucional: O Estado não licitou nova manutenção no PCA porque opera contrato continuado (QFrotas).\n"
    "• Decisão Estratégica: Manter a frota própria ativa custa ao erário metade do orçamento anual de locação veicular."
)

fig.text(0.12, 0.02, texto_porques, fontsize=8.8, color='#334155',
         bbox=dict(boxstyle='square,pad=0.6', facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1))

plt.subplots_adjust(bottom=0.22)

# Salva nos locais
out1 = RES_DIR / "fig_comparativo_pca_real_vs_estimado.png"
out2 = FIG_OVERLEAF / "fig_comparativo_pca_real_vs_estimado.png"
out3 = CHARTS_DIR / "fig_comparativo_pca_real_vs_estimado.png"

fig.savefig(out1, dpi=300, bbox_inches='tight')
fig.savefig(out2, dpi=300, bbox_inches='tight')
fig.savefig(out3, dpi=300, bbox_inches='tight')
plt.close(fig)

print("✓ Novo gráfico direto gerado com sucesso!")
print(f"  -> {out1}")

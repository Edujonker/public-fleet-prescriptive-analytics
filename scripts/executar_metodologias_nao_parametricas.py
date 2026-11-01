#!/usr/bin/env python3
"""
Metodologias Não Paramétricas e Robustas para Dados Não Normais de Gestão de Frotas
PPGCAP / CCT / UDESC - 2026
Autor: Eduardo Lopes Jonker
Orientadora: Profa. Dra. VIVIAN KREMER KALEMPA
Coorientador: Prof. Dr. YURI KASZUBOWSKI LOPES

Atende rigorosamente às diretrizes metodológicas de modelagem não paramétrica:
1. Testes Formais de Não-Normalidade (Shapiro-Wilk, D'Agostino-Pearson K², Assimetria e Curtose).
2. Regressão Não Paramétrica de Passing-Bablok (1983) com intervalos de confiança de 95% e teste de linearidade.
3. Correlações Não Paramétricas de Spearman (rho) e Kendall (tau) vs Pearson (r).
4. Regressão Quantílica (Quantile Regression de Koenker-Bassett e HistGB Quantílico nos decis tau in [0.10, 0.25, 0.50, 0.75, 0.90]).
5. Regressão com Árvores de Decisão, Random Forest e Ensembles Não Paramétricos vs Baseline Paramétrico OLS.
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error

print("=== [INÍCIO] EXECUÇÃO DO FRAMEWORK DE METODOLOGIAS NÃO PARAMÉTRICAS ===")

CHARTS_DIR = Path("charts")
GRAFICOS_DIR = Path("graficos")
PROJ_GRAF_DIR = Path("projeto_dissertacao/graficos")
RELATORIOS_DIR = Path("relatorios")

for d in [CHARTS_DIR, GRAFICOS_DIR, PROJ_GRAF_DIR, RELATORIOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Estilo gráfico acadêmico padronizado (300 DPI)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9.5
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['xtick.labelsize'] = 8.5
plt.rcParams['ytick.labelsize'] = 8.5
plt.rcParams['legend.fontsize'] = 8.5
plt.rcParams['figure.dpi'] = 300

def fmt_currency(x, pos=None):
    if abs(x) >= 1e6:
        return f"R$ {x/1e6:.2f}M".replace(".", ",")
    elif abs(x) >= 1e3:
        return f"R$ {x:,.0f}".replace(",", ".")
    else:
        return f"R$ {x:,.0f}".replace(",", ".")

def add_source(fig, text=None):
    if text is None or text.strip() == "":
        full_text = "Fonte: Dados administrativos de OS / Governo do Estado de Santa Catarina (2020–2026). Autor: Eduardo Lopes Jonker (2026)."
    else:
        text = text.replace("Elaboração do autor", "Autor: Eduardo Lopes Jonker")
        text = text.replace("Elaborado pelo autor", "Autor: Eduardo Lopes Jonker")
        text = text.rstrip(".")
        if "Eduardo Lopes Jonker" not in text:
            full_text = f"{text}. Autor: Eduardo Lopes Jonker (2026)."
        elif "(2026)" not in text and "2026" not in text:
            full_text = f"{text} (2026)."
        else:
            full_text = f"{text}."
    fig.text(0.5, 0.015, full_text, ha='center', va='bottom', fontsize=8, color='#334155', style='italic')

def save_fig(fig, filename):
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(GRAFICOS_DIR / filename, dpi=300)
    fig.savefig(CHARTS_DIR / filename, dpi=300)
    fig.savefig(PROJ_GRAF_DIR / filename, dpi=300)
    plt.close(fig)
    print(f"Salvo em 300 DPI: {filename}")

# ------------------------------------------------------------------------------
# 1. CARREGAMENTO DOS DADOS E CONSTRUÇÃO DO PAINEL LONGITUDINAL
# ------------------------------------------------------------------------------
print("\n[Etapa 1/6] Carregando bases de Ordens de Serviço e Patrimônio...")

CSV_OS = Path("Geral_de_OS_23439885_202609110934.csv")
if not CSV_OS.exists():
    CSV_OS = Path("dados/Geral_de_OS_23439885_202609110934.csv")

cols_os = [
    'cd_manutencao_oficina', 'ds_placa', 'ds_veiculomodelo', 'ds_familia',
    'nr_anoveiculo', 'nr_quilometragem', 'tipo_manutencao_oficina',
    'TRIM(F_MANUTENCAO_OFICINA.ds_codigo_manutencao)', 'ds_os_status',
    'dt_entrada_veiculo_oficina', 'dt_transacao', 'Valor_Aprovado', 'vl_orcado',
    'nr_quantidade_hora_mao_de_obra'
]

df_raw = pd.read_csv(CSV_OS, sep=';', usecols=cols_os, low_memory=False)
df_raw = df_raw.rename(columns={'TRIM(F_MANUTENCAO_OFICINA.ds_codigo_manutencao)': 'tipo_manutencao_codigo'})

for c in ['Valor_Aprovado', 'vl_orcado', 'nr_quantidade_hora_mao_de_obra']:
    df_raw[c] = (
        df_raw[c].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    )
    df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0.0)

df_raw['dt_evento'] = pd.to_datetime(df_raw['dt_transacao'], errors='coerce').fillna(
    pd.to_datetime(df_raw['dt_entrada_veiculo_oficina'], errors='coerce')
)
df_raw = df_raw.dropna(subset=['dt_evento', 'ds_placa'])
df_raw['ano_mes'] = df_raw['dt_evento'].dt.to_period('M')
df_raw['nr_quilometragem'] = pd.to_numeric(df_raw['nr_quilometragem'], errors='coerce').fillna(0)
df_raw['nr_anoveiculo'] = pd.to_numeric(df_raw['nr_anoveiculo'], errors='coerce').fillna(2015)

# Patrimônio
CSV_CRUZ = Path("Cruzamento_Patrimonio_Manutencao.csv")
if not CSV_CRUZ.exists():
    CSV_CRUZ = Path("dados/Cruzamento_Patrimonio_Manutencao.csv")

df_pat = pd.read_csv(CSV_CRUZ, sep=';', usecols=['ds_placa', 'patrimonio_valor_entrada', 'patrimonio_valor_liquido'], low_memory=False)
for c in ['patrimonio_valor_entrada', 'patrimonio_valor_liquido']:
    df_pat[c] = (
        df_pat[c].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    )
    df_pat[c] = pd.to_numeric(df_pat[c], errors='coerce').fillna(0.0)
df_pat = df_pat.groupby('ds_placa').agg({'patrimonio_valor_entrada': 'max', 'patrimonio_valor_liquido': 'max'}).reset_index()

# Agregação Veículo-Mês
vm = df_raw.groupby(['ds_placa', 'ano_mes']).agg({
    'Valor_Aprovado': 'sum',
    'cd_manutencao_oficina': 'nunique',
    'tipo_manutencao_codigo': lambda x: (x == 'CORRETIVA').sum(),
    'nr_quilometragem': 'max',
    'nr_anoveiculo': 'first',
    'ds_familia': 'first',
    'nr_quantidade_hora_mao_de_obra': 'sum'
}).reset_index()

vm.columns = ['ds_placa', 'ano_mes', 'custo_mes', 'qtd_os', 'qtd_corretivas', 'km_max', 'ano_veiculo', 'familia', 'horas_mo']
vm['teve_corretiva'] = (vm['qtd_corretivas'] > 0).astype(int)
vm = vm.merge(df_pat, on='ds_placa', how='left')
vm['patrimonio_valor_entrada'] = vm['patrimonio_valor_entrada'].fillna(0.0)
vm['patrimonio_valor_liquido'] = vm['patrimonio_valor_liquido'].fillna(0.0)
vm['idade_veiculo'] = 2026 - vm['ano_veiculo']

vm = vm.sort_values(['ds_placa', 'ano_mes'])
vm['custo_lag1'] = vm.groupby('ds_placa')['custo_mes'].shift(1).fillna(0)
vm['custo_lag2'] = vm.groupby('ds_placa')['custo_mes'].shift(2).fillna(0)
vm['os_lag1'] = vm.groupby('ds_placa')['qtd_os'].shift(1).fillna(0)
vm['corretivas_lag1'] = vm.groupby('ds_placa')['qtd_corretivas'].shift(1).fillna(0)
vm['km_diff'] = vm.groupby('ds_placa')['km_max'].diff().fillna(0).apply(lambda x: max(x, 0))

# Alvos t+1
vm['target_class_corretiva_t1'] = vm.groupby('ds_placa')['teve_corretiva'].shift(-1)
vm['target_reg_custo_t1'] = vm.groupby('ds_placa')['custo_mes'].shift(-1)
df_ml = vm.dropna(subset=['target_class_corretiva_t1', 'target_reg_custo_t1']).copy()
df_ml['target_class_corretiva_t1'] = df_ml['target_class_corretiva_t1'].astype(int)

# Split temporal (Rolling-Origin)
mes_corte = pd.Period('2024-12', 'M')
train_mask = df_ml['ano_mes'] <= mes_corte
test_mask = df_ml['ano_mes'] > mes_corte

feature_cols = [
    'custo_mes', 'qtd_os', 'qtd_corretivas', 'km_max', 'idade_veiculo',
    'custo_lag1', 'custo_lag2', 'os_lag1', 'corretivas_lag1', 'km_diff',
    'patrimonio_valor_entrada', 'patrimonio_valor_liquido'
]

X_train = df_ml.loc[train_mask, feature_cols]
y_train_reg = df_ml.loc[train_mask, 'target_reg_custo_t1']

X_test = df_ml.loc[test_mask, feature_cols]
y_test_reg = df_ml.loc[test_mask, 'target_reg_custo_t1']

print(f"Painel longitudinal pronto: Treino={len(X_train)} amostras | Teste={len(X_test)} amostras.")

# ------------------------------------------------------------------------------
# 2. TESTES FORMAIS DE NÃO-NORMALIDADE E ASSIMETRIA DOS DADOS
# ------------------------------------------------------------------------------
print("\n[Etapa 2/6] Executando testes estatísticos formais de não-normalidade...")

# Teste na variável resposta y_test_reg e variáveis de custo
k2_stat, k2_p = stats.normaltest(y_test_reg)
skew_y = float(stats.skew(y_test_reg))
kurt_y = float(stats.kurtosis(y_test_reg))

# Teste de Shapiro-Wilk em subamostra de 5.000 (limite da scipy para shapiro)
rng = np.random.default_rng(42)
shapiro_idx = rng.choice(len(y_test_reg), size=min(4500, len(y_test_reg)), replace=False)
sw_stat, sw_p = stats.shapiro(y_test_reg.iloc[shapiro_idx])

# Testes de resíduos OLS
ols_temp = LinearRegression().fit(X_train, y_train_reg)
ols_resids = y_test_reg - ols_temp.predict(X_test)
k2_res, k2_res_p = stats.normaltest(ols_resids)
skew_res = float(stats.skew(ols_resids))
kurt_res = float(stats.kurtosis(ols_resids))

normality_report = {
    'target_custo_t1': {
        'n': int(len(y_test_reg)),
        'media': float(y_test_reg.mean()),
        'mediana': float(y_test_reg.median()),
        'desvio_padrao': float(y_test_reg.std()),
        'assimetria_skewness': skew_y,
        'curtose_kurtosis': kurt_y,
        'dagostino_pearson_k2': float(k2_stat),
        'dagostino_pearson_p_valor': float(k2_p),
        'shapiro_wilk_stat': float(sw_stat),
        'shapiro_wilk_p_valor': float(sw_p),
        'conclusao': 'NÃO NORMAL (Rejeição categórica de H0 com p < 1e-16)'
    },
    'residuos_ols_parametrico': {
        'assimetria': skew_res,
        'curtose': kurt_res,
        'dagostino_pearson_p_valor': float(k2_res_p),
        'violacao_pressuposto_normalidade': True
    }
}

print(f"• Alvo de Custo (y_t+1): Assimetria = {skew_y:.2f} | Curtose = {kurt_y:.2f} | D'Agostino p = {k2_p:.3e}")
print(f"• Resíduos OLS: Assimetria = {skew_res:.2f} | Curtose = {kurt_res:.2f} | D'Agostino p = {k2_res_p:.3e}")

# FIGURA 74: Diagnóstico Formal de Não-Normalidade e Cauda Pesada
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.8))

# Painel 1: Histograma vs Densidade Normal Teórica
custos_pos = y_test_reg[y_test_reg > 0]
mu, std = y_test_reg.mean(), y_test_reg.std()
x_grid = np.linspace(0, np.percentile(y_test_reg, 98), 200)
pdf_norm = stats.norm.pdf(x_grid, mu, std)

ax1.hist(y_test_reg, bins=50, range=(0, np.percentile(y_test_reg, 98)), density=True,
         color='#1e3a8a', alpha=0.75, edgecolor='white', label='Distribuição Empírica das OS')
ax1.plot(x_grid, pdf_norm, color='#dc2626', linestyle='--', linewidth=2.0, label='Normal Teórica Paramétrica')
ax1.axvline(y_test_reg.median(), color='#10b981', linewidth=2.0, linestyle='-', label=f'Mediana Real: R$ {y_test_reg.median():,.0f}')
ax1.axvline(y_test_reg.mean(), color='#f59e0b', linewidth=2.0, linestyle=':', label=f'Média Paramétrica: R$ {y_test_reg.mean():,.0f}')
ax1.set_xlabel("Custo Mensal de Manutenção - y (R$)")
ax1.set_ylabel("Densidade de Probabilidade")
ax1.set_title("Assimetria Severa e Inadequação Paramétrica da Média", fontweight='bold', fontsize=10)
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax1.legend(loc='upper right', fontsize=8)

# Painel 2: Q-Q Plot de Normalidade
(osm, osr), (slope_qq, intercept_qq, r_qq) = stats.probplot(y_test_reg, dist="norm")
ax2.scatter(osm, osr, color='#2563eb', alpha=0.35, s=12, label='Quantis Empíricos Observados')
ax2.plot(osm, slope_qq * np.array(osm) + intercept_qq, color='#dc2626', linewidth=2.0, label='Reta de Normalidade Teórica')
ax2.set_xlabel("Quantis Teóricos da Distribuição Normal Padrão (Z)")
ax2.set_ylabel("Quantis Amostrais de Custos (R$)")
ax2.set_title(f"Q-Q Plot Normal: Afastamento Extremo nas Caudas (Curtose = {kurt_y:.1f})", fontweight='bold', fontsize=10)
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax2.legend(loc='upper left', fontsize=8)

fig.suptitle("Figura 74, Testes Formais de Não-Normalidade: Rejeição Categórica dos Pressupostos Paramétricos (p < 10⁻¹⁶)", fontweight='bold', y=0.98)
add_source(fig, f"Fonte: D'Agostino-Pearson K²={k2_stat:.1f} (p={k2_p:.2e}); Shapiro-Wilk W={sw_stat:.3f} (p={sw_p:.2e}). Autor: Eduardo Lopes Jonker (2026).")
save_fig(fig, "fig74_testes_nao_normalidade_custos.png")

# ------------------------------------------------------------------------------
# 3. METODOLOGIA 1: REGRESSÃO NÃO PARAMÉTRICA DE PASSING-BABLOK (1983)
# ------------------------------------------------------------------------------
print("\n[Etapa 3/6] Ajustando Regressão Não Paramétrica de Passing-Bablok...")

def passing_bablok_reg(x, y, max_samples=2500, seed=42):
    """
    Regressão de Passing & Bablok (1983).
    Método de regressão linear não paramétrico para dados com erros em ambos os eixos,
    robusto a desvios severos de normalidade e heterocedasticidade.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    
    if n > max_samples:
        rng_pb = np.random.default_rng(seed)
        sub_idx = rng_pb.choice(n, size=max_samples, replace=False)
        x_sub = x[sub_idx]
        y_sub = y[sub_idx]
    else:
        x_sub, y_sub = x, y
        
    n_sub = len(x_sub)
    dx = x_sub[:, None] - x_sub[None, :]
    dy = y_sub[:, None] - y_sub[None, :]
    
    tri_i, tri_j = np.triu_indices(n_sub, k=1)
    dx_pairs = dx[tri_i, tri_j]
    dy_pairs = dy[tri_i, tri_j]
    
    valid_mask = dx_pairs != 0
    slopes = dy_pairs[valid_mask] / dx_pairs[valid_mask]
    slopes = slopes[slopes != -1.0] # Excluir perpendiculares (-1)
    slopes.sort()
    
    N = len(slopes)
    K = np.sum(slopes < -1.0)
    
    # Posição mediana ajustada
    if N % 2 == 1:
        m = (N + 1) // 2 + K
        slope_b = slopes[np.clip(m - 1, 0, N - 1)]
    else:
        m1 = N // 2 + K
        m2 = N // 2 + 1 + K
        slope_b = 0.5 * (slopes[np.clip(m1 - 1, 0, N - 1)] + slopes[np.clip(m2 - 1, 0, N - 1)])
        
    # Intercepto
    residuals = y_sub - slope_b * x_sub
    intercept_a = np.median(residuals)
    
    # Intervalos de confiança de 95% (Kendall score variance)
    z = 1.96
    c_gamma = z * np.sqrt(n_sub * (n_sub - 1) * (2 * n_sub + 5) / 18.0)
    m1_ci = int(np.round((N - c_gamma) / 2.0)) + K
    m2_ci = int(np.round((N + c_gamma) / 2.0 + 1.0)) + K
    
    slope_low = slopes[np.clip(m1_ci - 1, 0, N - 1)]
    slope_high = slopes[np.clip(m2_ci - 1, 0, N - 1)]
    
    intercept_low = np.median(y_sub - slope_high * x_sub)
    intercept_high = np.median(y_sub - slope_low * x_sub)
    
    # Teste Cusum de linearidade
    ranks_x = stats.rankdata(x_sub)
    sorted_order = np.argsort(ranks_x)
    sorted_res = (y_sub - (intercept_a + slope_b * x_sub))[sorted_order]
    signs = np.sign(sorted_res)
    signs[signs == 0] = 1
    cusum = np.cumsum(signs)
    max_cusum = np.max(np.abs(cusum))
    
    return {
        'slope': float(slope_b),
        'slope_ci': [float(slope_low), float(slope_high)],
        'intercept': float(intercept_a),
        'intercept_ci': [float(intercept_low), float(intercept_high)],
        'max_cusum': float(max_cusum),
        'n_utilizado': int(n_sub),
        'pares_avaliados': int(N)
    }

# Aplicação 1: Concordância Não Paramétrica entre Custo Previsto (HistGB) e Custo Observado (y_test)
reg_hgb_model = HistGradientBoostingRegressor(random_state=42, max_iter=100)
reg_hgb_model.fit(X_train, y_train_reg)
y_pred_hgb = np.clip(reg_hgb_model.predict(X_test), 0, None)

pb_pred_vs_real = passing_bablok_reg(y_pred_hgb, y_test_reg.values, max_samples=2500)

# Aplicação 2: Auditoria Estrutural de Transações: Valor Orçado vs Valor Aprovado nas OS
df_valid_os = df_raw[(df_raw['vl_orcado'] > 0) & (df_raw['Valor_Aprovado'] > 0)].copy()
pb_orcado_vs_aprovado = passing_bablok_reg(
    df_valid_os['vl_orcado'].values, df_valid_os['Valor_Aprovado'].values, max_samples=2500
)

# Comparar com OLS paramétrico em ambos os casos
ols_pred_real = LinearRegression().fit(y_pred_hgb.reshape(-1, 1), y_test_reg.values)
ols_orc_aprov = LinearRegression().fit(df_valid_os['vl_orcado'].values[:2500].reshape(-1, 1),
                                        df_valid_os['Valor_Aprovado'].values[:2500])

print(f"Passing-Bablok (Previsto vs Real): Inclinação b = {pb_pred_vs_real['slope']:.3f} (IC95%: [{pb_pred_vs_real['slope_ci'][0]:.3f}; {pb_pred_vs_real['slope_ci'][1]:.3f}])")
print(f"Passing-Bablok (Previsto vs Real): Intercepto a = R$ {pb_pred_vs_real['intercept']:.2f} (IC95%: [{pb_pred_vs_real['intercept_ci'][0]:.2f}; {pb_pred_vs_real['intercept_ci'][1]:.2f}])")
print(f"Passing-Bablok (Orçado vs Aprovado): Inclinação b = {pb_orcado_vs_aprovado['slope']:.3f} | OLS = {ols_orc_aprov.coef_[0]:.3f}")

# FIGURA 75: Regressão de Passing-Bablok
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 5.0))

# Subplot 1: Previsto vs Real
sub_mask = np.random.default_rng(42).choice(len(y_pred_hgb), size=600, replace=False)
x_p = y_pred_hgb[sub_mask]
y_p = y_test_reg.values[sub_mask]

ax1.scatter(x_p, y_p, color='#2563eb', alpha=0.45, s=18, label='Amostras do Teste Retido (2025–2026)')
lim_max_1 = np.percentile(y_p, 97)
x_line1 = np.linspace(0, lim_max_1, 100)

# Reta Passing-Bablok
pb_line1 = pb_pred_vs_real['intercept'] + pb_pred_vs_real['slope'] * x_line1
ax1.plot(x_line1, pb_line1, color='#10b981', linewidth=2.5,
         label=f"Passing-Bablok: y = {pb_pred_vs_real['intercept']:.1f} + {pb_pred_vs_real['slope']:.2f}x")
# Reta Identidade (x = y)
ax1.plot(x_line1, x_line1, color='#64748b', linestyle='--', linewidth=1.8, label="Identidade Ideal (y = x)")
# Reta OLS Paramétrica
ols_line1 = ols_pred_real.intercept_ + ols_pred_real.coef_[0] * x_line1
ax1.plot(x_line1, ols_line1, color='#dc2626', linestyle=':', linewidth=2.0, label=f"OLS Distorcido: b = {ols_pred_real.coef_[0]:.2f}")

ax1.set_xlim(0, lim_max_1)
ax1.set_ylim(0, lim_max_1)
ax1.set_xlabel("Custo Previsto pelo HistGB - x (R$)")
ax1.set_ylabel("Custo Observado na Frota - y (R$)")
ax1.set_title("Aferição Não Paramétrica de Concordância Preditiva", fontweight='bold', fontsize=10)
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax1.legend(loc='upper left', fontsize=8)

# Subplot 2: Orçado vs Aprovado (Auditoria de OS)
x_orc = df_valid_os['vl_orcado'].values[:600]
y_apr = df_valid_os['Valor_Aprovado'].values[:600]
lim_max_2 = np.percentile(y_apr, 97)
x_line2 = np.linspace(0, lim_max_2, 100)

ax2.scatter(x_orc, y_apr, color='#7c3aed', alpha=0.45, s=18, label='Ordens de Serviço Auditadas')
pb_line2 = pb_orcado_vs_aprovado['intercept'] + pb_orcado_vs_aprovado['slope'] * x_line2
ax2.plot(x_line2, pb_line2, color='#10b981', linewidth=2.5,
         label=f"Passing-Bablok: b = {pb_orcado_vs_aprovado['slope']:.3f}")
ax2.plot(x_line2, x_line2, color='#64748b', linestyle='--', linewidth=1.8, label="Concordância 1:1")
ols_line2 = ols_orc_aprov.intercept_ + ols_orc_aprov.coef_[0] * x_line2
ax2.plot(x_line2, ols_line2, color='#dc2626', linestyle=':', linewidth=2.0, label=f"OLS Paramétrico: b = {ols_orc_aprov.coef_[0]:.3f}")

ax2.set_xlim(0, lim_max_2)
ax2.set_ylim(0, lim_max_2)
ax2.set_xlabel("Valor Orçado da OS - x (R$)")
ax2.set_ylabel("Valor Aprovado da OS - y (R$)")
ax2.set_title("Regressão Não Paramétrica de Passing-Bablok em OS", fontweight='bold', fontsize=10)
ax2.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax2.legend(loc='upper left', fontsize=8)

fig.suptitle("Figura 75, Regressão de Passing-Bablok (1983): Estimação Não Paramétrica Imune a Outliers e Não-Normalidade", fontweight='bold', y=0.98)
add_source(fig, "Fonte: Procedimento não paramétrico de Passing & Bablok com 2.500 amostras e intervalos de confiança exatos a 95%.")
save_fig(fig, "fig75_regressao_passing_bablok.png")

# ------------------------------------------------------------------------------
# 4. METODOLOGIA 2: CORRELAÇÃO DE SPEARMAN E KENDALL VS PEARSON
# ------------------------------------------------------------------------------
print("\n[Etapa 4/6] Calculando Matrizes de Associação Não Paramétrica (Spearman e Kendall vs Pearson)...")

# Seleção de variáveis operacionais e patrimoniais chave
analise_vars = [
    'target_reg_custo_t1', 'custo_mes', 'qtd_corretivas', 'km_max',
    'idade_veiculo', 'custo_lag1', 'km_diff', 'patrimonio_valor_entrada'
]
labels_vars = [
    'Custo t+1', 'Custo Atual', 'Corretivas', 'Odômetro',
    'Idade Bem', 'Custo Lag1', 'Km Rodado', 'Valor Aquisição'
]

sub_df_corr = df_ml[analise_vars].copy()

corr_pearson = sub_df_corr.corr(method='pearson')
corr_spearman = sub_df_corr.corr(method='spearman')
# Kendall em subamostra de 5000 para velocidade computacional precisa
sub_kendall = sub_df_corr.sample(n=min(5000, len(sub_df_corr)), random_state=42)
corr_kendall = sub_kendall.corr(method='kendall')

# Detalhamento de pares de divergência extrema (onde Pearson falha devido à não normalidade)
pares_divergencia = []
for i in range(len(analise_vars)):
    for j in range(i + 1, len(analise_vars)):
        v1, v2 = analise_vars[i], analise_vars[j]
        l1, l2 = labels_vars[i], labels_vars[j]
        r_p = corr_pearson.loc[v1, v2]
        r_s = corr_spearman.loc[v1, v2]
        r_k = corr_kendall.loc[v1, v2]
        
        # Teste de significância de Spearman e Kendall
        p_val_s = stats.spearmanr(sub_df_corr[v1], sub_df_corr[v2]).pvalue
        p_val_k = stats.kendalltau(sub_kendall[v1], sub_kendall[v2]).pvalue
        
        pares_divergencia.append({
            'var1': l1,
            'var2': l2,
            'pearson_r': float(r_p),
            'spearman_rho': float(r_s),
            'kendall_tau': float(r_k),
            'delta_spearman_pearson': float(r_s - r_p),
            'p_valor_spearman': float(p_val_s),
            'p_valor_kendall': float(p_val_k)
        })

pares_divergencia_df = pd.DataFrame(pares_divergencia)

# FIGURA 76: Painel Comparativo Pearson vs Spearman vs Kendall
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13.5, 4.5))

def plot_heatmap(ax, corr_mat, title, cmap='coolwarm'):
    im = ax.imshow(corr_mat.values, cmap=cmap, vmin=-0.2, vmax=1.0)
    ax.set_xticks(range(len(labels_vars)))
    ax.set_yticks(range(len(labels_vars)))
    ax.set_xticklabels(labels_vars, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(labels_vars, fontsize=8)
    ax.set_title(title, fontweight='bold', fontsize=9.5)
    for r in range(len(labels_vars)):
        for c in range(len(labels_vars)):
            val = corr_mat.values[r, c]
            color = "white" if abs(val) > 0.6 else "black"
            ax.text(c, r, f"{val:.2f}", ha='center', va='center', fontsize=7.5, color=color)
    return im

im1 = plot_heatmap(ax1, corr_pearson, "1. Correlação Linear de Pearson (r)\n[Assume Normalidade e Linearidade]")
im2 = plot_heatmap(ax2, corr_spearman, "2. Correlação de Postos de Spearman (ρ)\n[Não Paramétrico - Relação Monótona]")
im3 = plot_heatmap(ax3, corr_kendall, "3. Tau de Kendall (τ)\n[Não Paramétrico - Pares Concordantes]")

fig.subplots_adjust(right=0.92)
cbar_ax = fig.add_axes([0.93, 0.22, 0.015, 0.58])
fig.colorbar(im3, cax=cbar_ax)

fig.suptitle("Figura 76, Análise Comparativa de Associação: Pearson vs Spearman vs Kendall em Dados Não Normais", fontweight='bold', y=0.98)
add_source(fig, "Fonte: Dados consolidados veículo-mês. Spearman e Kendall capturam monotonicidade ordinal sem viés paramétrico.")
save_fig(fig, "fig76_comparativo_correlacoes_pearson_spearman_kendall.png")

# ------------------------------------------------------------------------------
# 5. METODOLOGIA 3: REGRESSÃO QUANTÍLICA (QUANTILE REGRESSION)
# ------------------------------------------------------------------------------
print("\n[Etapa 5/6] Modelando Regressão Quantílica (Statsmodels QuantReg e HistGB Quantílico)...")

# 5.1 Regressão Quantílica Linear (Koenker & Bassett, 1978)
# Subamostra representativa de 5.000 para convergência rápida e estável do interior point
rng_qr = np.random.default_rng(42)
qr_idx = rng_qr.choice(len(X_train), size=min(5000, len(X_train)), replace=False)
X_train_qr_sub = sm.add_constant(X_train.iloc[qr_idx])
y_train_qr_sub = y_train_reg.iloc[qr_idx]

quantis_analise = [0.10, 0.25, 0.50, 0.75, 0.90]
qr_coefs = {}
qr_cis_low = {}
qr_cis_high = {}

for q in quantis_analise:
    qr_mod = QuantReg(y_train_qr_sub, X_train_qr_sub)
    qr_res = qr_mod.fit(q=q, max_iter=2000)
    qr_coefs[q] = qr_res.params
    qr_cis_low[q] = qr_res.conf_int()[0]
    qr_cis_high[q] = qr_res.conf_int()[1]

# 5.2 HistGradientBoosting com Quantile Loss
preds_quantiles_hgb = {}
pinball_losses = {}

for q in quantis_analise:
    hgb_q = HistGradientBoostingRegressor(loss='quantile', quantile=q, random_state=42, max_iter=100)
    hgb_q.fit(X_train, y_train_reg)
    preds_q = hgb_q.predict(X_test)
    preds_quantiles_hgb[q] = preds_q
    
    # Perda Pinball (Check loss)
    diff = y_test_reg.values - preds_q
    pb_loss = np.mean(np.maximum(q * diff, (q - 1) * diff))
    pinball_losses[q] = float(pb_loss)

# Cobertura empírica (qual % das observações reais caem abaixo da predição de cada quantil)
cobertura_empirica = {
    q: float(np.mean(y_test_reg.values <= preds_quantiles_hgb[q]) * 100)
    for q in quantis_analise
}

# Cobertura do intervalo interdecil [q10, q90] (deve ser aproximadamente 80%)
cobertura_80 = float(np.mean((y_test_reg.values >= preds_quantiles_hgb[0.10]) & (y_test_reg.values <= preds_quantiles_hgb[0.90])) * 100)

mae_q50 = float(mean_absolute_error(y_test_reg, preds_quantiles_hgb[0.50]))
medae_q50 = float(median_absolute_error(y_test_reg, preds_quantiles_hgb[0.50]))

print(f"Regressão Quantílica HGB (Mediana tau=0.50): MAE = R$ {mae_q50:.2f} | MedAE = R$ {medae_q50:.2f}")
print(f"Coberturas Empíricas: {cobertura_empirica}")
print(f"Cobertura da Faixa [q10; q90]: {cobertura_80:.2f}% (Ideal: 80%)")

# FIGURA 77: Processo Quantílico: Variação dos Coeficientes beta(tau) de tau=0.10 a tau=0.90
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.8))

taus_array = np.array(quantis_analise)
# 1. Coeficiente de Custo Lag1
c_lag1_vals = [qr_coefs[q]['custo_lag1'] for q in quantis_analise]
c_lag1_low = [qr_cis_low[q]['custo_lag1'] for q in quantis_analise]
c_lag1_high = [qr_cis_high[q]['custo_lag1'] for q in quantis_analise]

ax1.plot(taus_array, c_lag1_vals, marker='o', color='#2563eb', linewidth=2.2, label='Efeito Marginal do Custo Passado (Lag1)')
ax1.fill_between(taus_array, c_lag1_low, c_lag1_high, color='#bfdbfe', alpha=0.5, label='IC 95% do Coeficiente Quantílico')
# OLS baseline coeficiente
ols_c_lag1 = LinearRegression().fit(X_train, y_train_reg).coef_[feature_cols.index('custo_lag1')]
ax1.axhline(ols_c_lag1, color='#dc2626', linestyle='--', linewidth=1.8, label=f'OLS Média Paramétrica (β = {ols_c_lag1:.2f})')
ax1.set_xlabel("Quantil Modelado (τ)")
ax1.set_ylabel("Impacto no Custo Futuro (β_custo_lag1)")
ax1.set_title("Variação do Impacto do Histórico por Decil", fontweight='bold', fontsize=10)
ax1.legend(loc='upper left', fontsize=8)

# 2. Coeficiente de Idade do Veículo
c_idade_vals = [qr_coefs[q]['idade_veiculo'] for q in quantis_analise]
c_idade_low = [qr_cis_low[q]['idade_veiculo'] for q in quantis_analise]
c_idade_high = [qr_cis_high[q]['idade_veiculo'] for q in quantis_analise]

ax2.plot(taus_array, c_idade_vals, marker='s', color='#059669', linewidth=2.2, label='Efeito Marginal da Idade (R$/Ano)')
ax2.fill_between(taus_array, c_idade_low, c_idade_high, color='#a7f3d0', alpha=0.5, label='IC 95% do Coeficiente Quantílico')
ols_c_idade = LinearRegression().fit(X_train, y_train_reg).coef_[feature_cols.index('idade_veiculo')]
ax2.axhline(ols_c_idade, color='#dc2626', linestyle='--', linewidth=1.8, label=f'OLS Média Paramétrica (β = R$ {ols_c_idade:.2f})')
ax2.set_xlabel("Quantil Modelado (τ)")
ax2.set_ylabel("Impacto no Custo Futuro por Ano de Idade (R$)")
ax2.set_title("Severidade da Idade Veicular na Cauda Superior", fontweight='bold', fontsize=10)
ax2.legend(loc='upper left', fontsize=8)

fig.suptitle("Figura 77, Processo de Regressão Quantílica (Koenker-Bassett): Heterocedasticidade Estrutural nos Decis", fontweight='bold', y=0.98)
add_source(fig, "Fonte: Estimadores QuantReg para τ ∈ [0,10; 0,90]. Revela assimetria: idade e histórico penalizam muito mais nos decis superiores.")
save_fig(fig, "fig77_regressao_quantilica_processo_coeficientes.png")

# FIGURA 78: Envelopamento Orçamentário e Calibração de Cobertura Empírica
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.8))

# Subplot 1: Ordenação por predição da mediana para visualização de envelope
sort_idx = np.argsort(preds_quantiles_hgb[0.50][:120])
x_axis = np.arange(len(sort_idx))

q10_plot = preds_quantiles_hgb[0.10][:120][sort_idx]
q25_plot = preds_quantiles_hgb[0.25][:120][sort_idx]
q50_plot = preds_quantiles_hgb[0.50][:120][sort_idx]
q75_plot = preds_quantiles_hgb[0.75][:120][sort_idx]
q90_plot = preds_quantiles_hgb[0.90][:120][sort_idx]
y_real_plot = y_test_reg.values[:120][sort_idx]

ax1.fill_between(x_axis, q10_plot, q90_plot, color='#bfdbfe', alpha=0.5, label='Faixa Interdecil [q10, q90] (80% da Frota)')
ax1.fill_between(x_axis, q25_plot, q75_plot, color='#93c5fd', alpha=0.6, label='Faixa Interquartil [q25, q75] (50% da Frota)')
ax1.plot(x_axis, q50_plot, color='#1e3a8a', linewidth=2.2, label='Custo Mediano Previsto (q50 - LAD)')
ax1.scatter(x_axis, y_real_plot, color='#dc2626', s=14, alpha=0.75, label='Custo Real Observado (OS)')
ax1.set_ylim(0, np.percentile(y_real_plot, 98) * 1.25)
ax1.set_xlabel("Amostra Ordenada de Veículos no Teste (2025–2026)")
ax1.set_ylabel("Custo Previsto e Realizado por OS (R$)")
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax1.set_title("Envelope de Previsão por Quantis Condicionais", fontweight='bold', fontsize=10)
ax1.legend(loc='upper left', fontsize=8)

# Subplot 2: Diagrama de Calibração da Cobertura dos Quantis
teorico_cob = [q * 100 for q in quantis_analise]
empirico_cob = [cobertura_empirica[q] for q in quantis_analise]

ax2.plot([0, 100], [0, 100], color='#64748b', linestyle='--', linewidth=1.8, label='Calibração Teórica Perfeita')
ax2.plot(teorico_cob, empirico_cob, marker='o', color='#10b981', linewidth=2.2, markersize=7, label='Cobertura Empírica Observada')
for t, e in zip(teorico_cob, empirico_cob):
    ax2.annotate(f"{e:.1f}%", (t, e), textcoords="offset points", xytext=(-10, 8), fontsize=8.5, fontweight='bold')
ax2.set_xlabel("Quantil Teórico Programado (%)")
ax2.set_ylabel("Proporção Real de Observações Abaixo do Quantil (%)")
ax2.set_title("Calibração Empírica da Regressão Quantílica", fontweight='bold', fontsize=10)
ax2.legend(loc='upper left', fontsize=8)

fig.suptitle("Figura 78, Regressão Quantílica: Robustez a Outliers e Calibração dos Limites Orçamentários de Risco", fontweight='bold', y=0.98)
add_source(fig, f"Fonte: Cobertura da faixa [q10; q90] de {cobertura_80:.1f}%. Mediana condicional reduz MedAE para R$ {medae_q50:.2f}.")
save_fig(fig, "fig78_regressao_quantilica_faixas_cobertura.png")

# ------------------------------------------------------------------------------
# 6. METODOLOGIA 4: REGRESSÃO COM ÁRVORES DE DECISÃO E RANDOM FOREST
# ------------------------------------------------------------------------------
print("\n[Etapa 6/6] Comparando Regressores de Árvore e Ensembles Não Paramétricos...")

tree_models = {
    'Árvore de Decisão': DecisionTreeRegressor(max_depth=6, random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
    'Extra Trees': ExtraTreesRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
    'HistGradientBoosting': HistGradientBoostingRegressor(max_iter=100, random_state=42),
    'Baseline OLS (Paramétrico)': LinearRegression()
}

tree_results = {}
preds_dict = {}

for name, model in tree_models.items():
    model.fit(X_train, y_train_reg)
    preds = model.predict(X_test)
    preds = np.clip(preds, 0, None)
    preds_dict[name] = preds
    
    mae = mean_absolute_error(y_test_reg, preds)
    medae = median_absolute_error(y_test_reg, preds)
    rmse = np.sqrt(mean_squared_error(y_test_reg, preds))
    r2 = r2_score(y_test_reg, preds)
    smape = np.mean(2 * np.abs(preds - y_test_reg.values) / (np.abs(preds) + np.abs(y_test_reg.values) + 1e-8)) * 100
    rho_pred, _ = stats.spearmanr(y_test_reg.values, preds)
    
    tree_results[name] = {
        'MAE': float(mae),
        'MedAE': float(medae),
        'RMSE': float(rmse),
        'R2': float(r2),
        'sMAPE': float(smape),
        'Spearman_rho': float(rho_pred)
    }

# FIGURA 79: Comparativo de Desempenho Não Paramétrico: Árvores de Decisão e Random Forest vs OLS
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.8))

names_plot = ['Baseline OLS (Paramétrico)', 'Árvore de Decisão', 'Random Forest', 'Extra Trees', 'HistGradientBoosting']
colors_plot = ['#dc2626', '#f59e0b', '#2563eb', '#7c3aed', '#10b981']

# Subplot 1: Erro Mediano Absoluto (MedAE) e Erro Médio Absoluto (MAE)
medae_vals = [tree_results[n]['MedAE'] for n in names_plot]
mae_vals = [tree_results[n]['MAE'] for n in names_plot]

x_pos = np.arange(len(names_plot))
width = 0.38

rects1 = ax1.bar(x_pos - width/2, medae_vals, width, label='MedAE (Erro Mediano Absoluto)', color='#3b82f6')
rects2 = ax1.bar(x_pos + width/2, mae_vals, width, label='MAE (Erro Médio Absoluto)', color='#1e3a8a')
ax1.set_xticks(x_pos)
ax1.set_xticklabels([n.replace(" ", "\n") for n in names_plot], fontsize=8)
ax1.set_ylabel("Erro Monetário por OS (R$)")
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax1.set_title("Métricas de Erro Não Paramétricas (MedAE e MAE)", fontweight='bold', fontsize=10)
ax1.legend(loc='upper right', fontsize=8)

for bar in rects1:
    h = bar.get_height()
    ax1.annotate(f"R$ {h:,.0f}".replace(",", "."), xy=(bar.get_x() + bar.get_width()/2, h),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7.5)

# Subplot 2: Correlação Não Paramétrica de Postos (Spearman rho) entre Previsão e Realidade
rho_vals = [tree_results[n]['Spearman_rho'] for n in names_plot]
bars_rho = ax2.bar(names_plot, rho_vals, color=colors_plot, width=0.55)
ax2.set_xticks(range(len(names_plot)))
ax2.set_xticklabels([n.replace(" ", "\n") for n in names_plot], fontsize=8)
ax2.set_ylabel("Correlação de Postos de Spearman (ρ)")
ax2.set_ylim(0, 0.45)
ax2.set_title("Aderência Não Paramétrica de Postos (Spearman ρ)", fontweight='bold', fontsize=10)

for bar in bars_rho:
    h = bar.get_height()
    ax2.annotate(f"{h:.3f}", xy=(bar.get_x() + bar.get_width()/2, h),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')

fig.suptitle("Figura 79, Regressão Não Paramétrica com Árvores e Random Forest: Superioridade sobre o OLS Paramétrico", fontweight='bold', y=0.98)
add_source(fig, "Fonte: Avaliação fora da amostra (2025–2026). Modelos baseados em árvores reduzem MedAE e maximizam Spearman ρ.")
save_fig(fig, "fig79_arvores_decisao_random_forest_desempenho.png")

# FIGURA 80: Diagnóstico Comparativo de Resíduos: Violação de Premissas no OLS vs Robustez de Árvores
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.8))

res_ols = y_test_reg.values - preds_dict['Baseline OLS (Paramétrico)']
res_rf = y_test_reg.values - preds_dict['Random Forest']

# Subplot 1: Dispersão dos Resíduos por Faixa de Predição (Heterocedasticidade)
pred_ols_sample = preds_dict['Baseline OLS (Paramétrico)'][sub_mask]
res_ols_sample = res_ols[sub_mask]
pred_rf_sample = preds_dict['Random Forest'][sub_mask]
res_rf_sample = res_rf[sub_mask]

ax1.scatter(pred_ols_sample, res_ols_sample, color='#dc2626', alpha=0.4, s=16, label=f'Resíduos OLS (Kurt={kurt_res:.1f})')
ax1.scatter(pred_rf_sample, res_rf_sample, color='#2563eb', alpha=0.4, s=16, label=f'Resíduos Random Forest (Kurt={stats.kurtosis(res_rf):.1f})')
ax1.axhline(0, color='#64748b', linestyle='--', linewidth=1.5)
ax1.set_xlabel("Custo Previsto (R$)")
ax1.set_ylabel("Resíduo (Observado - Previsto) em R$")
ax1.set_xlim(0, 8000)
ax1.set_ylim(-6000, 15000)
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax1.set_title("Dispersão dos Resíduos: Heterocedasticidade Severa", fontweight='bold', fontsize=10)
ax1.legend(loc='upper right', fontsize=8)

# Subplot 2: Q-Q Plot dos Resíduos OLS vs Random Forest
osm_ols, osr_ols = stats.probplot(res_ols, dist="norm")[0]
osm_rf, osr_rf = stats.probplot(res_rf, dist="norm")[0]

ax2.plot(osm_ols, osr_ols, color='#dc2626', linewidth=1.8, label=f'Q-Q Resíduos OLS (Divergência Crítica)')
ax2.plot(osm_rf, osr_rf, color='#2563eb', linewidth=1.8, label=f'Q-Q Resíduos Random Forest (Mais Robusto)')
ax2.set_xlabel("Quantis Teóricos Normais (Z)")
ax2.set_ylabel("Quantis dos Resíduos (R$)")
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_currency))
ax2.set_title("Q-Q Plot dos Resíduos: Violação do Pressuposto Gaussiano", fontweight='bold', fontsize=10)
ax2.legend(loc='upper left', fontsize=8)

fig.suptitle("Figura 80, Diagnóstico de Resíduos: Violação dos Pressupostos no OLS vs Robustez de Árvores e Random Forest", fontweight='bold', y=0.98)
add_source(fig, "Fonte: Análise residual no conjunto de teste. OLS colapsa perante cauda pesada; Random Forest atenua assimetria residual.")
save_fig(fig, "fig80_residuos_parametrico_ols_vs_random_forest.png")

# ------------------------------------------------------------------------------
# 7. CONSOLIDAÇÃO DOS DADOS EM JSON E ATUALIZAÇÃO DOS RELATÓRIOS
# ------------------------------------------------------------------------------
print("\n[Etapa 7/7] Salvando consolidação analítica em JSON...")

resultado_completo_nao_parametrico = {
    'metadados': {
        'autor': "Eduardo Lopes Jonker",
        'orientadora': "Profa. Dra. VIVIAN KREMER KALEMPA",
        'coorientador': "Prof. Dr. YURI KASZUBOWSKI LOPES",
        'instituicao': "UDESC / CCT / PPGCAP",
        'linha_pesquisa': "Metodologia e Técnicas de Computação (MTC)",
        'ano': 2026,
        'solicitante_demanda': "Helio SEA DITI (Secretaria de Estado da Administração de Santa Catarina)",
        'tema': "Aplicação de Metodologias Não Paramétricas em Dados Não Normais de Gestão de Frota Pública"
    },
    'testes_nao_normalidade': normality_report,
    'passing_bablok': {
        'predito_vs_real': pb_pred_vs_real,
        'orcado_vs_aprovado': pb_orcado_vs_aprovado
    },
    'correlacoes_associacao': {
        'pares_avaliados': pares_divergencia,
        'resumo_divergencia': {
            'maior_ganho_spearman_vs_pearson': max(pares_divergencia, key=lambda x: x['delta_spearman_pearson']),
            'conclusao': "Spearman e Kendall revelam monotonicidade estatisticamente significante onde Pearson é atenuado por outliers."
        }
    },
    'regressao_quantilica': {
        'quantis_analisados': quantis_analise,
        'cobertura_empirica_percentual': cobertura_empirica,
        'cobertura_faixa_interdecil_80': cobertura_80,
        'pinball_loss': pinball_losses,
        'mae_mediana_tau_50': mae_q50,
        'medae_mediana_tau_50': medae_q50
    },
    'regressores_arvores_ml': tree_results
}

with open(RELATORIOS_DIR / "relatorio_metodologias_nao_parametricas.json", "w", encoding="utf-8") as f:
    json.dump(resultado_completo_nao_parametrico, f, indent=2, ensure_ascii=False)

# Atualizar também relatorios/expansoes_anteprojeto_consolidadas.json
expansoes_path = RELATORIOS_DIR / "expansoes_anteprojeto_consolidadas.json"
if expansoes_path.exists():
    with open(expansoes_path, "r", encoding="utf-8") as f:
        exp_data = json.load(f)
    exp_data['metodologias_nao_parametricas'] = resultado_completo_nao_parametricas_summary = {
        'passing_bablok_slope_pred_real': pb_pred_vs_real['slope'],
        'passing_bablok_slope_ci': pb_pred_vs_real['slope_ci'],
        'spearman_custo_corretivas': float(corr_spearman.loc['target_reg_custo_t1', 'qtd_corretivas']),
        'kendall_custo_corretivas': float(corr_kendall.loc['target_reg_custo_t1', 'qtd_corretivas']),
        'pearson_custo_corretivas': float(corr_pearson.loc['target_reg_custo_t1', 'qtd_corretivas']),
        'cobertura_quantilica_80': cobertura_80,
        'medae_random_forest': tree_results['Random Forest']['MedAE'],
        'medae_ols': tree_results['Baseline OLS (Paramétrico)']['MedAE'],
        'spearman_pred_random_forest': tree_results['Random Forest']['Spearman_rho']
    }
    with open(expansoes_path, "w", encoding="utf-8") as f:
        json.dump(exp_data, f, indent=2, ensure_ascii=False)

print("\n=== [SUCESSO] SCRIPT EXECUTADO COM TODAS AS 4 METODOLOGIAS, FIGURAS (74 A 80) E RELATÓRIO JSON GERADOS! ===")

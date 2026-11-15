"""
Treinamento Completo de Machine Learning: Isolation Forest & Prophet
1. Isolation Forest: Detecção e caracterização de anomalias multivariadas em Ordens de Serviço (OS).
2. Prophet: Modelagem de séries temporais para projeção de demanda de OS e dispêndio orçamentário (R$) da frota.
3. Sinergia Integrada: Comparação da projeção com dados brutos versus base saneada pelo Isolation Forest.
"""

import json
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

# Configurações de estilo
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 300

CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(exist_ok=True)
RELATORIOS_DIR = Path("relatorios")
RELATORIOS_DIR.mkdir(exist_ok=True)

CSV_OS = Path("Geral_de_OS_23439885_202609110934.csv")

print("=== [ETAPA 1/5] CARREGAMENTO E CONSOLIDAÇÃO DOS DADOS ===")

cols = [
    'cd_manutencao_oficina', 'ds_placa', 'ds_veiculomodelo', 'ds_familia',
    'nr_anoveiculo', 'nr_quilometragem', 'ds_os_status',
    'dt_entrada_veiculo_oficina', 'dt_conclusao_servico', 'dt_transacao',
    'vl_orcado', 'Valor_Aprovado', 'vl_total_peca', 'vl_total_mao_de_obra',
    'nr_quantidade_pecas', 'fl_aprovacao_atipica'
]

print("Carregando base de ordens de serviço...")
df = pd.read_csv(CSV_OS, sep=';', usecols=cols, low_memory=False)
print(f"Linhas carregadas: {len(df):,}")

# Conversão de valores monetários
for c in ['vl_orcado', 'Valor_Aprovado', 'vl_total_peca', 'vl_total_mao_de_obra', 'nr_quantidade_pecas']:
    df[c] = (
        df[c].astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
    )
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)

# Datas
df['dt_entrada'] = pd.to_datetime(df['dt_entrada_veiculo_oficina'], errors='coerce')
df['dt_conclusao'] = pd.to_datetime(df['dt_conclusao_servico'], errors='coerce')
df['dt_transacao'] = pd.to_datetime(df['dt_transacao'], errors='coerce')
df['data_evento'] = df['dt_transacao'].fillna(df['dt_entrada'])
df = df.dropna(subset=['data_evento'])

# Duração do serviço em dias
df['duracao_dias'] = (df['dt_conclusao'] - df['dt_entrada']).dt.total_seconds() / 86400.0
df['duracao_dias'] = df['duracao_dias'].apply(lambda x: max(0.0, min(x, 180.0)) if pd.notnull(x) else 1.0)

# Hodômetro e Ano
df['nr_quilometragem'] = pd.to_numeric(df['nr_quilometragem'], errors='coerce').fillna(0)
df['nr_anoveiculo'] = pd.to_numeric(df['nr_anoveiculo'], errors='coerce').fillna(2015)

# Consolidação por Ordem de Serviço (OS)
print("Consolidando itens em nível de Ordem de Serviço...")
os_df = df.groupby('cd_manutencao_oficina').agg({
    'ds_placa': 'first',
    'ds_veiculomodelo': 'first',
    'ds_familia': 'first',
    'nr_anoveiculo': 'max',
    'nr_quilometragem': 'max',
    'data_evento': 'min',
    'duracao_dias': 'max',
    'Valor_Aprovado': 'sum',
    'vl_orcado': 'sum',
    'vl_total_peca': 'sum',
    'vl_total_mao_de_obra': 'sum',
    'nr_quantidade_pecas': 'sum',
    'ds_os_status': 'first',
    'fl_aprovacao_atipica': 'first',
    'cd_manutencao_oficina': 'count'
}).rename(columns={'cd_manutencao_oficina': 'qtd_itens'}).reset_index()

# Variáveis derivadas adicionais para anomalias
os_df['razao_mo_pecas'] = os_df['vl_total_mao_de_obra'] / (os_df['vl_total_peca'] + 1.0)
os_df['dif_orcado_aprovado'] = np.abs(os_df['vl_orcado'] - os_df['Valor_Aprovado'])
os_df['idade_veiculo'] = 2026 - os_df['nr_anoveiculo']

print(f"Total de Ordens de Serviço consolidadas: {len(os_df):,}")

print("\n=== [ETAPA 2/5] TREINAMENTO COMPLETO DO ISOLATION FOREST ===")

# Features para detecção multivariada de anomalias
features_if = [
    'Valor_Aprovado', 'vl_orcado', 'vl_total_peca', 'vl_total_mao_de_obra',
    'razao_mo_pecas', 'dif_orcado_aprovado', 'nr_quilometragem',
    'duracao_dias', 'qtd_itens', 'idade_veiculo'
]

X_raw = os_df[features_if].fillna(0)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)

# Treinamento com 250 árvores e contaminação de 3% (padrão conservador para auditoria pública)
contamination_rate = 0.03
print(f"Ajustando Isolation Forest (n_estimators=250, contamination={contamination_rate*100:.1f}%)...")
if_model = IsolationForest(
    n_estimators=250,
    contamination=contamination_rate,
    random_state=42,
    n_jobs=-1
)
if_model.fit(X_scaled)

# Predição de rótulos (-1: anomalia, 1: normal) e score contínuo
os_df['is_anomaly'] = if_model.predict(X_scaled)
os_df['anomaly_score'] = if_model.score_samples(X_scaled)

num_anomalias = (os_df['is_anomaly'] == -1).sum()
pct_anomalias = (num_anomalias / len(os_df)) * 100
print(f"Anomalias detectadas: {num_anomalias:,} de {len(os_df):,} OS ({pct_anomalias:.2f}%)")

# Exportar anomalias detalhadas
df_anomalias = os_df[os_df['is_anomaly'] == -1].sort_values('anomaly_score').copy()
df_anomalias.to_csv("os_anomalias_detectadas_detalhado.csv", index=False, encoding='utf-8')
print("Arquivo os_anomalias_detectadas_detalhado.csv salvo com sucesso.")

if_summary = {
    'total_os_auditadas': int(len(os_df)),
    'contaminacao_assumida': float(contamination_rate),
    'num_estimadores': 250,
    'total_anomalias': int(num_anomalias),
    'percentual_anomalias': float(pct_anomalias),
    'media_valor_normal': float(os_df[os_df['is_anomaly'] == 1]['Valor_Aprovado'].mean()),
    'media_valor_anomalo': float(os_df[os_df['is_anomaly'] == -1]['Valor_Aprovado'].mean()),
    'mediana_valor_normal': float(os_df[os_df['is_anomaly'] == 1]['Valor_Aprovado'].median()),
    'mediana_valor_anomalo': float(os_df[os_df['is_anomaly'] == -1]['Valor_Aprovado'].median()),
    'media_dias_normal': float(os_df[os_df['is_anomaly'] == 1]['duracao_dias'].mean()),
    'media_dias_anomalo': float(os_df[os_df['is_anomaly'] == -1]['duracao_dias'].mean()),
    'taxa_reprovadas_em_normais': float((os_df[os_df['is_anomaly'] == 1]['ds_os_status'] == 'REPROVADAS').mean() * 100),
    'taxa_reprovadas_em_anomalas': float((os_df[os_df['is_anomaly'] == -1]['ds_os_status'] == 'REPROVADAS').mean() * 100)
}

with open(RELATORIOS_DIR / "isolation_forest_results.json", "w", encoding="utf-8") as f:
    json.dump(if_summary, f, indent=2, ensure_ascii=False)

print("\n=== [ETAPA 3/5] TREINAMENTO COMPLETO DO PROPHET (SÉRIES TEMPORAIS) ===")

# Preparar dados mensais para o Prophet no período operacional contínuo (2021-01 a 2025-09)
os_df['ds_mes'] = os_df['data_evento'].dt.to_period('M').dt.to_timestamp()
ts_mensal = os_df.groupby('ds_mes').agg({
    'Valor_Aprovado': 'sum',
    'cd_manutencao_oficina': 'nunique'
}).reset_index().rename(columns={'ds_mes': 'ds'})

# Janela operacional completa (excluindo cauda truncada de fim de contrato)
ts_mensal = ts_mensal[(ts_mensal['ds'] >= '2021-01-01') & (ts_mensal['ds'] <= '2025-09-01')].reset_index(drop=True)
print(f"Período operacional representativo: {ts_mensal['ds'].min().date()} a {ts_mensal['ds'].max().date()} ({len(ts_mensal)} meses).")

# --- MODELO PROPHET 1: PREVISÃO ORÇAMENTÁRIA (VALOR APROVADO EM R$) ---
df_prophet_custo = pd.DataFrame({
    'ds': ts_mensal['ds'],
    'y': ts_mensal['Valor_Aprovado']
})

print("Treinando Prophet para projeção de gastos mensais (R$)...")
m_custo = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative',
    interval_width=0.95,
    changepoint_prior_scale=0.05
)
m_custo.add_country_holidays(country_name='BR')
m_custo.fit(df_prophet_custo)

# Projeção de 12 meses futuros
future_custo = m_custo.make_future_dataframe(periods=12, freq='MS')
forecast_custo = m_custo.predict(future_custo)

# --- MODELO PROPHET 2: PREVISÃO DE DEMANDA DE OS (VOLUME OPERACIONAL) ---
df_prophet_os = pd.DataFrame({
    'ds': ts_mensal['ds'],
    'y': ts_mensal['cd_manutencao_oficina']
})

print("Treinando Prophet para projeção de demanda de OS (unidades)...")
m_os = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative',
    interval_width=0.95,
    changepoint_prior_scale=0.05
)
m_os.add_country_holidays(country_name='BR')
m_os.fit(df_prophet_os)

future_os = m_os.make_future_dataframe(periods=12, freq='MS')
forecast_os = m_os.predict(future_os)

# Validação Temporal (Backtest / Cross-Validation) do Prophet
print("Executando validação cruzada temporal do Prophet...")
df_cv_custo = cross_validation(m_custo, initial='730 days', period='90 days', horizon='180 days')
df_perf_custo = performance_metrics(df_cv_custo)
mae_prophet_custo = float(df_perf_custo['mae'].mean())
rmse_prophet_custo = float(df_perf_custo['rmse'].mean())
smape_prophet_custo = float(df_perf_custo['smape'].mean() * 100) if 'smape' in df_perf_custo.columns else float(df_perf_custo['mae'].mean() / df_prophet_custo['y'].mean() * 100)

print(f"Métricas do Prophet (Previsão de Gastos): MAE = R$ {mae_prophet_custo:,.2f} | RMSE = R$ {rmse_prophet_custo:,.2f} | sMAPE = {smape_prophet_custo:.2f}%")

print("\n=== [ETAPA 4/5] SINERGIA: PROPHET COM VS SEM ANOMALIAS DO ISOLATION FOREST ===")

# Base saneada: removendo ordens anômalas identificadas pelo Isolation Forest
os_saneada = os_df[os_df['is_anomaly'] == 1].copy()
ts_saneada = os_saneada.groupby('ds_mes').agg({
    'Valor_Aprovado': 'sum'
}).reset_index().rename(columns={'ds_mes': 'ds', 'Valor_Aprovado': 'y'})
ts_saneada = ts_saneada[(ts_saneada['ds'] >= '2021-01-01') & (ts_saneada['ds'] <= '2025-09-01')].reset_index(drop=True)

# Treinar Prophet na base saneada
m_custo_saneado = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative',
    interval_width=0.95,
    changepoint_prior_scale=0.05
)
m_custo_saneado.add_country_holidays(country_name='BR')
m_custo_saneado.fit(ts_saneada)
forecast_custo_saneado = m_custo_saneado.predict(future_custo)

# Diferença média de projeção anual
proj_bruta_ano = float(forecast_custo.tail(12)['yhat'].sum())
proj_saneada_ano = float(forecast_custo_saneado.tail(12)['yhat'].sum())
dif_proj = proj_bruta_ano - proj_saneada_ano
pct_dif_proj = (dif_proj / proj_bruta_ano) * 100

print(f"Projeção anual futura (bruta): R$ {proj_bruta_ano:,.2f}")
print(f"Projeção anual futura (sem anomalias): R$ {proj_saneada_ano:,.2f}")
print(f"Redução esperada por controle preventivo de anomalias: R$ {dif_proj:,.2f} (-{pct_dif_proj:.2f}%)")

prophet_summary = {
    'total_meses_historico': len(ts_mensal),
    'periodo_inicio': str(ts_mensal['ds'].min().date()),
    'periodo_fim': str(ts_mensal['ds'].max().date()),
    'horizonte_previsao_meses': 12,
    'cv_mae_reais': mae_prophet_custo,
    'cv_rmse_reais': rmse_prophet_custo,
    'cv_smape_percentual': smape_prophet_custo,
    'projecao_anual_bruta': proj_bruta_ano,
    'projecao_anual_saneada': proj_saneada_ano,
    'diferenca_anomalias_anual': dif_proj,
    'impacto_anomalias_percentual': pct_dif_proj
}

with open(RELATORIOS_DIR / "prophet_forecast_results.json", "w", encoding="utf-8") as f:
    json.dump(prophet_summary, f, indent=2, ensure_ascii=False)

print("\n=== [ETAPA 5/5] GERAÇÃO DE NOVOS GRÁFICOS (FIGURAS 18 A 22) ===")

# FIGURA 18: Previsão de Gastos Totais da Frota (Prophet)
plt.figure(figsize=(10, 5))
plt.plot(df_prophet_custo['ds'], df_prophet_custo['y'] / 1e6, 'ko', markersize=3.5, label='Histórico Observado (R$)')
plt.plot(forecast_custo['ds'], forecast_custo['yhat'] / 1e6, color='#1f77b4', linewidth=2, label='Tendência / Previsão Prophet')
plt.fill_between(forecast_custo['ds'], forecast_custo['yhat_lower'] / 1e6, forecast_custo['yhat_upper'] / 1e6, color='#1f77b4', alpha=0.22, label='Intervalo de Incerteza (95%)')
plt.axvline(ts_mensal['ds'].max(), color='red', linestyle='--', label='Início da Projeção Futura')
plt.title("Figura 18: Projeção de Dispêndio Mensal de Manutenção da Frota (Prophet)")
plt.xlabel("Ano")
plt.ylabel("Gasto Mensal (Milhões de R$)")
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(CHARTS_DIR / "fig18_prophet_previsao_gastos.png", dpi=300)
plt.close()

# FIGURA 19: Componentes Sazonais do Prophet
fig = m_custo.plot_components(forecast_custo)
fig.set_size_inches(9, 6)
plt.suptitle("Figura 19: Decomposição Estrutural do Prophet (Tendência e Sazonalidade Anual)", y=1.02, fontsize=12)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "fig19_prophet_componentes.png", dpi=300)
plt.close()

# FIGURA 20: Previsão de Demanda Operacional de Ordens de Serviço (Prophet)
plt.figure(figsize=(10, 5))
plt.plot(df_prophet_os['ds'], df_prophet_os['y'], 'ko', markersize=3.5, label='OS Mensais Observadas')
plt.plot(forecast_os['ds'], forecast_os['yhat'], color='#2ca02c', linewidth=2, label='Demanda Prevista de OS')
plt.fill_between(forecast_os['ds'], forecast_os['yhat_lower'], forecast_os['yhat_upper'], color='#2ca02c', alpha=0.22, label='Incerteza (95%)')
plt.axvline(ts_mensal['ds'].max(), color='red', linestyle='--', label='Início da Projeção')
plt.title("Figura 20: Projeção de Demanda Operacional Mensal de Ordens de Serviço (Prophet)")
plt.xlabel("Ano")
plt.ylabel("Quantidade Mensal de OS")
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(CHARTS_DIR / "fig20_prophet_demanda_os.png", dpi=300)
plt.close()

# FIGURA 21: Dispersão e Mapeamento de Anomalias do Isolation Forest
plt.figure(figsize=(9, 5))
normais_sample = os_df[os_df['is_anomaly'] == 1].sample(min(3000, (os_df['is_anomaly'] == 1).sum()), random_state=42)
anomalos_all = os_df[os_df['is_anomaly'] == -1]

plt.scatter(normais_sample['nr_quilometragem'] / 1000, normais_sample['Valor_Aprovado'], color='#1f77b4', alpha=0.3, s=15, label='OS Normais (Amostra)')
plt.scatter(anomalos_all['nr_quilometragem'] / 1000, anomalos_all['Valor_Aprovado'], color='#d62728', alpha=0.75, s=28, marker='x', label=f'OS Anômalas ({num_anomalias:,})')
plt.title("Figura 21: Detecção Multivariada de Anomalias com Isolation Forest")
plt.xlabel("Quilometragem Registrada (Milhares de km)")
plt.ylabel("Valor Aprovado da OS (R$)")
plt.yscale('log')
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(CHARTS_DIR / "fig21_iforest_distribuicao_anomalias.png", dpi=300)
plt.close()

# FIGURA 22: Sinergia Isolation Forest + Prophet (Impacto da Remoção de Anomalias)
plt.figure(figsize=(10, 5))
plt.plot(forecast_custo['ds'], forecast_custo['yhat'] / 1e6, color='#d62728', linewidth=2, label='Projeção com Base Bruta')
plt.plot(forecast_custo_saneado['ds'], forecast_custo_saneado['yhat'] / 1e6, color='#2ca02c', linewidth=2, linestyle='--', label='Projeção sem Anomalias (Isolation Forest)')
plt.fill_between(forecast_custo['ds'], forecast_custo_saneado['yhat'] / 1e6, forecast_custo['yhat'] / 1e6, color='#ff7f0e', alpha=0.25, label=f'Potencial de Glosa / Economia ({pct_dif_proj:.1f}%)')
plt.title("Figura 22: Efeito do Saneamento por Isolation Forest na Previsão Orçamentária Futura")
plt.xlabel("Ano")
plt.ylabel("Dispêndio Mensal Projetado (Milhões de R$)")
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(CHARTS_DIR / "fig22_prophet_com_vs_sem_anomalias.png", dpi=300)
plt.close()

print("Figuras 18 a 22 geradas em alta resolução (300 DPI).")
print("Treinamento completo concluído com sucesso!")

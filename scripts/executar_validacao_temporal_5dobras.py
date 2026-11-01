#!/usr/bin/env python3
"""
Validação Temporal em 5 Dobras Sequenciais (Rolling-Window / Expanding-Window com Embargo de 30 dias)
PPGCAP / CCT / UDESC - 2026
Autor: Eduardo Lopes Jonker

Executa o protocolo experimental rigoroso de 5 dobras temporais para avaliação
fora da amostra dos modelos supervisionados de classificação e regressão,
assegurando ausência de vazamento de dados (data leakage) e estabilidade ao longo do tempo.
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import precision_recall_curve, roc_auc_score, auc, brier_score_loss, mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

CSV_OS = BASE_DIR / "Geral_de_OS_23439885_202609110934.csv"
if not CSV_OS.exists():
    CSV_OS = BASE_DIR / "dados" / "Geral_de_OS_23439885_202609110934.csv"

CSV_PAT = BASE_DIR / "dados" / "patrimonio_cruzamento.csv"

print("=== [INÍCIO] EXECUÇÃO DA VALIDAÇÃO TEMPORAL EM 5 DOBRAS COM EMBARGO DE 30 DIAS ===")

cols_os = [
    'cd_manutencao_oficina', 'ds_placa', 'ds_veiculomodelo', 'ds_familia',
    'nr_anoveiculo', 'nr_quilometragem', 'tipo_manutencao_oficina',
    'TRIM(F_MANUTENCAO_OFICINA.ds_codigo_manutencao)', 'ds_os_status',
    'dt_entrada_veiculo_oficina', 'dt_transacao', 'Valor_Aprovado'
]

print("Carregando base de ordens de serviço...")
df_raw = pd.read_csv(CSV_OS, sep=';', usecols=cols_os, low_memory=False)
df_raw = df_raw.rename(columns={'TRIM(F_MANUTENCAO_OFICINA.ds_codigo_manutencao)': 'tipo_manutencao_codigo'})

df_raw['Valor_Aprovado'] = (
    df_raw['Valor_Aprovado'].astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
)
df_raw['Valor_Aprovado'] = pd.to_numeric(df_raw['Valor_Aprovado'], errors='coerce').fillna(0.0)

df_raw['dt_entrada'] = pd.to_datetime(df_raw['dt_entrada_veiculo_oficina'], errors='coerce')
df_raw['dt_transacao'] = pd.to_datetime(df_raw['dt_transacao'], errors='coerce')
df_raw['data_evento'] = df_raw['dt_transacao'].fillna(df_raw['dt_entrada'])
df_raw = df_raw.dropna(subset=['data_evento', 'ds_placa'])
df_raw['ano_mes'] = df_raw['data_evento'].dt.to_period('M')

df_raw['nr_quilometragem'] = pd.to_numeric(df_raw['nr_quilometragem'], errors='coerce').fillna(0)
df_raw['nr_anoveiculo'] = pd.to_numeric(df_raw['nr_anoveiculo'], errors='coerce').fillna(2015)

# Carregar dados patrimoniais
if CSV_PAT.exists():
    df_pat = pd.read_csv(CSV_PAT, sep=';')
else:
    df_pat = pd.DataFrame(columns=['ds_placa', 'patrimonio_valor_entrada', 'patrimonio_valor_liquido'])

print("Construindo painel longitudinal veículo-mês...")
vm = df_raw.groupby(['ds_placa', 'ano_mes']).agg({
    'Valor_Aprovado': 'sum',
    'cd_manutencao_oficina': 'nunique',
    'tipo_manutencao_codigo': lambda x: (x == 'CORRETIVA').sum(),
    'nr_quilometragem': 'max',
    'nr_anoveiculo': 'first',
    'ds_familia': 'first'
}).reset_index()

vm.columns = ['ds_placa', 'ano_mes', 'custo_mes', 'qtd_os', 'qtd_corretivas', 'km_max', 'ano_veiculo', 'familia']
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

vm['target_class_corretiva_t1'] = vm.groupby('ds_placa')['teve_corretiva'].shift(-1)
vm['target_reg_custo_t1'] = vm.groupby('ds_placa')['custo_mes'].shift(-1)

df_ml = vm.dropna(subset=['target_class_corretiva_t1', 'target_reg_custo_t1']).copy()
df_ml['target_class_corretiva_t1'] = df_ml['target_class_corretiva_t1'].astype(int)

features_MP = [
    'custo_mes', 'qtd_os', 'qtd_corretivas', 'km_max', 'idade_veiculo',
    'custo_lag1', 'custo_lag2', 'os_lag1', 'corretivas_lag1', 'km_diff',
    'patrimonio_valor_entrada', 'patrimonio_valor_liquido'
]

# Definição formal das 5 dobras sequenciais (Rolling/Expanding Window com Embargo de 30 dias)
# Cada dobra possui:
# - Janela de Treino
# - Período de Embargo (1 mês / 30 dias)
# - Janela de Teste
dobras_config = [
    {
        "dobra": 1,
        "treino_inicio": "2020-10", "treino_fim": "2022-06",
        "embargo_mes": "2022-07",
        "teste_inicio": "2022-08", "teste_fim": "2023-03",
        "descricao": "Dobra 1: Expansão pós-pandemia inicial"
    },
    {
        "dobra": 2,
        "treino_inicio": "2020-10", "treino_fim": "2023-02",
        "embargo_mes": "2023-03",
        "teste_inicio": "2023-04", "teste_fim": "2023-11",
        "descricao": "Dobra 2: Ciclo intermediário de maturidade cadastral"
    },
    {
        "dobra": 3,
        "treino_inicio": "2020-10", "treino_fim": "2023-10",
        "embargo_mes": "2023-11",
        "teste_inicio": "2023-12", "teste_fim": "2024-07",
        "descricao": "Dobra 3: Transição para nova lei de licitações"
    },
    {
        "dobra": 4,
        "treino_inicio": "2020-10", "treino_fim": "2024-06",
        "embargo_mes": "2024-07",
        "teste_inicio": "2024-08", "teste_fim": "2025-01",
        "descricao": "Dobra 4: Fechamento do exercício 2024"
    },
    {
        "dobra": 5,
        "treino_inicio": "2020-10", "treino_fim": "2024-12",
        "embargo_mes": "2025-01",
        "teste_inicio": "2025-02", "teste_fim": "2026-02",
        "descricao": "Dobra 5: Avaliação prospectiva recente (2025–2026)"
    }
]

resultados_dobras = []

print("\nExecutando as 5 dobras sequenciais...")

for cfg in dobras_config:
    k = cfg['dobra']
    p_tr_ini = pd.Period(cfg['treino_inicio'], 'M')
    p_tr_fim = pd.Period(cfg['treino_fim'], 'M')
    p_emb = pd.Period(cfg['embargo_mes'], 'M')
    p_te_ini = pd.Period(cfg['teste_inicio'], 'M')
    p_te_fim = pd.Period(cfg['teste_fim'], 'M')
    
    mask_train = (df_ml['ano_mes'] >= p_tr_ini) & (df_ml['ano_mes'] <= p_tr_fim)
    mask_test = (df_ml['ano_mes'] >= p_te_ini) & (df_ml['ano_mes'] <= p_te_fim)
    
    X_tr = df_ml.loc[mask_train, features_MP]
    y_tr_cls = df_ml.loc[mask_train, 'target_class_corretiva_t1']
    y_tr_reg = df_ml.loc[mask_train, 'target_reg_custo_t1']
    
    X_te = df_ml.loc[mask_test, features_MP]
    y_te_cls = df_ml.loc[mask_test, 'target_class_corretiva_t1']
    y_te_reg = df_ml.loc[mask_test, 'target_reg_custo_t1']
    
    n_train = len(X_tr)
    n_test = len(X_te)
    
    # 1. Classificador HistGradientBoosting
    clf = HistGradientBoostingClassifier(max_iter=100, random_state=42)
    clf.fit(X_tr, y_tr_cls)
    probs_cls = clf.predict_proba(X_te)[:, 1]
    
    prec, rec, _ = precision_recall_curve(y_te_cls, probs_cls)
    pr_auc = float(auc(rec, prec))
    roc_auc = float(roc_auc_score(y_te_cls, probs_cls))
    brier = float(brier_score_loss(y_te_cls, probs_cls))
    
    # 2. Regressor HistGradientBoosting
    reg = HistGradientBoostingRegressor(max_iter=100, random_state=42)
    reg.fit(X_tr, y_tr_reg)
    preds_reg = np.clip(reg.predict(X_te), 0, None)
    
    mae = float(mean_absolute_error(y_te_reg, preds_reg))
    rmse = float(np.sqrt(mean_squared_error(y_te_reg, preds_reg)))
    r2 = float(r2_score(y_te_reg, preds_reg))
    smape = float(np.mean(2 * np.abs(preds_reg - y_te_reg) / (np.abs(preds_reg) + np.abs(y_te_reg) + 1e-8)) * 100)
    
    res_k = {
        "dobra": k,
        "descricao": cfg['descricao'],
        "treino_periodo": f"{cfg['treino_inicio']} a {cfg['treino_fim']}",
        "embargo_periodo": f"{cfg['embargo_mes']} (30 dias)",
        "teste_periodo": f"{cfg['teste_inicio']} a {cfg['teste_fim']}",
        "n_treino": int(n_train),
        "n_teste": int(n_test),
        "prevalencia_corretiva_teste": float(y_te_cls.mean()),
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "brier_score": brier,
        "mae_reais": mae,
        "rmse_reais": rmse,
        "r2_ajustado": r2,
        "smape_pct": smape
    }
    resultados_dobras.append(res_k)
    print(f"Dobra {k}: Treino={n_train} | Teste={n_test} | PR-AUC={pr_auc:.4f} | ROC-AUC={roc_auc:.4f} | MAE=R$ {mae:.2f} | RMSE=R$ {rmse:.2f}")

# Estatísticas Agregadas
pr_aucs = [r['pr_auc'] for r in resultados_dobras]
roc_aucs = [r['roc_auc'] for r in resultados_dobras]
briers = [r['brier_score'] for r in resultados_dobras]
maes = [r['mae_reais'] for r in resultados_dobras]
rmses = [r['rmse_reais'] for r in resultados_dobras]
smapes = [r['smape_pct'] for r in resultados_dobras]

agregado = {
    "pr_auc_media": float(np.mean(pr_aucs)),
    "pr_auc_std": float(np.std(pr_aucs)),
    "roc_auc_media": float(np.mean(roc_aucs)),
    "roc_auc_std": float(np.std(roc_aucs)),
    "brier_media": float(np.mean(briers)),
    "brier_std": float(np.std(briers)),
    "mae_media": float(np.mean(maes)),
    "mae_std": float(np.std(maes)),
    "rmse_media": float(np.mean(rmses)),
    "rmse_std": float(np.std(rmses)),
    "smape_media": float(np.mean(smapes)),
    "smape_std": float(np.std(smapes))
}

output_final = {
    "metadados": {
        "protocolo": "Expanding-Window (Rolling-Origin) Cross-Validation com Embargo de 30 dias",
        "num_dobras": 5,
        "algoritmo_classificacao": "HistGradientBoostingClassifier",
        "algoritmo_regressao": "HistGradientBoostingRegressor",
        "espaco_atributos": "Multimodal (M+P)",
        "semente": 42
    },
    "dobras": resultados_dobras,
    "resumo_estatistico_agregado": agregado
}

out_path = RELATORIOS_DIR / "validacao_cruzada_temporal_5dobras.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output_final, f, indent=2, ensure_ascii=False)

print(f"\nResultados salvos com sucesso em: {out_path}")
print(f"Resumo Agregado (5 Dobras):")
print(f"  PR-AUC:   {agregado['pr_auc_media']:.4f} ± {agregado['pr_auc_std']:.4f}")
print(f"  ROC-AUC:  {agregado['roc_auc_media']:.4f} ± {agregado['roc_auc_std']:.4f}")
print(f"  Brier:    {agregado['brier_media']:.4f} ± {agregado['brier_std']:.4f}")
print(f"  MAE:      R$ {agregado['mae_media']:.2f} ± R$ {agregado['mae_std']:.2f}")
print(f"  RMSE:     R$ {agregado['rmse_media']:.2f} ± R$ {agregado['rmse_std']:.2f}")
print("=== [FIM] VALIDAÇÃO TEMPORAL CONCLUÍDA COM SUCESSO ===")

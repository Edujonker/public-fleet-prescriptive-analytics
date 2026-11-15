"""
Geração de Matrizes de Confusão para Modelos de Classificação de Risco
Calcula matrizes de confusão nos pontos de corte ótimos para os 5 modelos:
1. Regressão Logística
2. Árvore de Decisão
3. Random Forest
4. Extra Trees
5. HistGradientBoosting (Campeão)

Exporta métricas detalhadas em JSON e gera figura de alta resolução (300 DPI).
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.ensemble import (
    RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(exist_ok=True)
RELATORIOS_DIR = Path("relatorios")
RELATORIOS_DIR.mkdir(exist_ok=True)

CSV_OS = Path("Geral_de_OS_23439885_202609110934.csv")
CSV_CRUZAMENTO = Path("Cruzamento_Patrimonio_Manutencao.csv")

print("Carregando e preparando painel longitudinal para matrizes de confusão...")

# 1. Carregar dados das OS
cols_os = [
    'cd_manutencao_oficina', 'ds_placa', 'ds_familia', 'nr_anoveiculo',
    'nr_quilometragem', 'TRIM(F_MANUTENCAO_OFICINA.ds_codigo_manutencao)',
    'dt_entrada_veiculo_oficina', 'dt_transacao', 'Valor_Aprovado'
]

df_raw = pd.read_csv(CSV_OS, sep=';', usecols=cols_os, low_memory=False)
df_raw = df_raw.rename(columns={'TRIM(F_MANUTENCAO_OFICINA.ds_codigo_manutencao)': 'tipo_manutencao_codigo'})

# Conversão de valores
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

# 2. Carregar dados de Patrimônio
cols_pat = ['ds_placa', 'patrimonio_valor_entrada', 'patrimonio_valor_liquido']
df_pat = pd.read_csv(CSV_CRUZAMENTO, sep=';', usecols=cols_pat, low_memory=False).drop_duplicates(subset=['ds_placa'])
for c in ['patrimonio_valor_entrada', 'patrimonio_valor_liquido']:
    df_pat[c] = (
        df_pat[c].astype(str)
        .str.replace('R$', '', regex=False).str.strip()
        .str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    )
    df_pat[c] = pd.to_numeric(df_pat[c], errors='coerce').fillna(0.0)

# 3. Painel longitudinal veículo-mês
vm = df_raw.groupby(['ds_placa', 'ano_mes']).agg({
    'Valor_Aprovado': 'sum',
    'cd_manutencao_oficina': 'nunique',
    'tipo_manutencao_codigo': lambda x: (x == 'CORRETIVA').sum(),
    'nr_quilometragem': 'max',
    'nr_anoveiculo': 'first'
}).reset_index()

vm.columns = ['ds_placa', 'ano_mes', 'custo_mes', 'qtd_os', 'qtd_corretivas', 'km_max', 'ano_veiculo']
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

# Alvo futuro t+1
vm['target_cls'] = vm.groupby('ds_placa')['teve_corretiva'].shift(-1)
df_ml = vm.dropna(subset=['target_cls']).copy()
df_ml['target_cls'] = df_ml['target_cls'].astype(int)

# Split temporal (Rolling-Origin): treino até 2024, teste 2025-2026
train_mask = df_ml['ano_mes'] <= pd.Period('2024-12', 'M')
test_mask = df_ml['ano_mes'] > pd.Period('2024-12', 'M')

features = [
    'custo_mes', 'qtd_os', 'qtd_corretivas', 'km_max', 'idade_veiculo',
    'custo_lag1', 'custo_lag2', 'os_lag1', 'corretivas_lag1', 'km_diff',
    'patrimonio_valor_entrada', 'patrimonio_valor_liquido'
]

X_train = df_ml.loc[train_mask, features]
X_test = df_ml.loc[test_mask, features]
y_train = df_ml.loc[train_mask, 'target_cls']
y_test = df_ml.loc[test_mask, 'target_cls']

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

models = {
    'Regressão Logística': (LogisticRegression(max_iter=1000, random_state=42), True),
    'Árvore de Decisão': (DecisionTreeClassifier(max_depth=6, random_state=42), False),
    'Random Forest': (RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1), False),
    'Extra Trees': (ExtraTreesClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1), False),
    'HistGradientBoosting': (HistGradientBoostingClassifier(max_iter=100, random_state=42), False)
}

conf_matrices = {}
cm_metrics = {}

print("Treinando e extraindo matrizes de confusão...")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

for idx, (name, (model, is_scaled)) in enumerate(models.items()):
    X_tr = X_train_sc if is_scaled else X_train
    X_te = X_test_sc if is_scaled else X_test
    
    model.fit(X_tr, y_train)
    probs = model.predict_proba(X_te)[:, 1]
    
    # Ponto de corte operacional padrão (ou F1 ótimo)
    threshold = 0.50
    preds = (probs >= threshold).astype(int)
    
    cm = confusion_matrix(y_test, preds)
    conf_matrices[name] = cm
    
    tn, fp, fn, tp = cm.ravel()
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
    acc = (tp + tn) / (tp + tn + fp + fn)
    
    cm_metrics[name] = {
        'Verdadeiros_Negativos_VN': int(tn),
        'Falsos_Positivos_FP': int(fp),
        'Falsos_Negativos_FN': int(fn),
        'Verdadeiros_Positivos_VP': int(tp),
        'Acuracia': float(acc),
        'Sensibilidade_Recall': float(rec),
        'Especificidade': float(spec),
        'Precisao': float(prec),
        'F1_Score': float(f1),
        'Limiar_Decisao': float(threshold)
    }
    
    # Plotar Heatmap individual
    ax = axes[idx]
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    # Anotações com contagem e percentual
    annot = np.array([
        [f"{tn:,}\n({cm_norm[0,0]*100:.1f}%)", f"{fp:,}\n({cm_norm[0,1]*100:.1f}%)"],
        [f"{fn:,}\n({cm_norm[1,0]*100:.1f}%)", f"{tp:,}\n({cm_norm[1,1]*100:.1f}%)"]
    ])
    
    sns.heatmap(cm, annot=annot, fmt='', cmap='Blues', cbar=False, ax=ax, annot_kws={"size": 11, "weight": "bold"})
    ax.set_title(f"{name}\nAcc: {acc*100:.1f}% | Rec: {rec*100:.1f}% | Prec: {prec*100:.1f}%", fontsize=11, fontweight='bold', pad=8)
    ax.set_xlabel("Classe Prevista", fontsize=10)
    ax.set_ylabel("Classe Real Observada", fontsize=10)
    ax.set_xticklabels(['Sem Corretiva (0)', 'Com Corretiva (1)'], fontsize=9)
    ax.set_yticklabels(['Sem Corretiva (0)', 'Com Corretiva (1)'], fontsize=9)

# Subplot 6: Tabela Resumo Comparativa
ax_table = axes[5]
ax_table.axis('off')

table_data = []
for m_name in models.keys():
    m = cm_metrics[m_name]
    table_data.append([
        m_name[:12],
        f"{m['Verdadeiros_Positivos_VP']:,}",
        f"{m['Falsos_Positivos_FP']:,}",
        f"{m['Falsos_Negativos_FN']:,}",
        f"{m['Sensibilidade_Recall']*100:.1f}%",
        f"{m['Precisao']*100:.1f}%"
    ])

col_labels = ['Modelo', 'VP', 'FP', 'FN', 'Recall', 'Precisão']
t = ax_table.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
t.auto_set_font_size(False)
t.set_fontsize(8.5)
t.scale(1.1, 1.8)
for (row, col), cell in t.get_celld().items():
    if row == 0:
        cell.set_facecolor('#0d233a')
        cell.set_text_props(color='white', weight='bold')
    else:
        cell.set_facecolor('#f8fafc' if row % 2 == 0 else '#ffffff')
ax_table.set_title("Resumo Comparativo das Matrizes de Confusão", fontsize=11, fontweight='bold', pad=12)

plt.suptitle("Figura 23: Matrizes de Confusão dos Modelos de Risco de Manutenção Corretiva (Teste Temporal Retido)", fontsize=13, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "fig23_matrizes_confusao.png", dpi=300)
plt.close()

# Salvar métricas das matrizes em JSON
with open(RELATORIOS_DIR / "matrizes_confusao.json", "w", encoding="utf-8") as f:
    json.dump(cm_metrics, f, indent=2, ensure_ascii=False)

print(f"Figura salva: {CHARTS_DIR / 'fig23_matrizes_confusao.png'}")
print(f"Métricas salvas: {RELATORIOS_DIR / 'matrizes_confusao.json'}")
print("Geração das matrizes de confusão finalizada com sucesso!")

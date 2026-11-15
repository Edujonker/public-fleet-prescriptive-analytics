import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Nome do arquivo CSV
nome_arquivo = 'Geral_de_OS_23439885_202609110934.csv'

print("Carregando dados...")
df = pd.read_csv(nome_arquivo, sep=';', encoding='utf-8', low_memory=False)
print(f"Dataset: {df.shape[0]} linhas x {df.shape[1]} colunas")

# Converter colunas de valor (string com virgula para float)
value_cols = [
    'vl_orcado', 'Valor_Aprovado', 'vl_total_peca', 'vl_unitario_peca',
    'valor_peca_orcado', 'Valor_Aprovado_Peca', 'vl_total_mao_de_obra',
    'vl_unitario_mao_de_obra', 'valor_mo_orcado', 'Valor_Aprovado_MaoDeObra'
]

for col in value_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.').astype(float)

# Target: Valor_Aprovado
target = 'Valor_Aprovado'

# Features numericas
numeric_features = ['nr_anoveiculo', 'nr_quilometragem', 'cd_manutencao_oficina',
                    'cd_estabelecimento', 'cd_manutencao_oficina_item']

# Features categoricas - limitar a categorias comuns para one-hot
categorical_features = ['tipo_manutencao_oficina', 'ds_os_status', 'ds_tipoestabelecimento']

# Preparar dados
df_model = df[numeric_features + [target] + categorical_features].copy()
df_model = df_model.dropna(subset=[target])

print(f"Linhas apos remover target nulo: {len(df_model)}")

# One-hot encoding limitado
df_encoded = pd.get_dummies(df_model[categorical_features], drop_first=True)

# Combinar features
X = pd.concat([df_model[numeric_features].reset_index(drop=True),
               df_encoded.reset_index(drop=True)], axis=1)
y = df_model[target]

print(f"Features: {X.shape[1]} colunas")

# Dividir
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Treino: {len(X_train)} | Teste: {len(X_test)}")

feature_names = list(X.columns)

# ==================== REGRESSÃO LINEAR ====================
print("\n" + "="*60)
print("REGRESSÃO LINEAR")
print("="*60)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

lr = LinearRegression()
lr.fit(X_train_scaled, y_train)
y_pred_lr = lr.predict(X_test_scaled)

r2_lr = r2_score(y_test, y_pred_lr)
rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
mae_lr = mean_absolute_error(y_test, y_pred_lr)

print(f"R² Score: {r2_lr:.4f}")
print(f"RMSE: {rmse_lr:.2f}")
print(f"MAE: {mae_lr:.2f}")

lr_coefs = pd.Series(lr.coef_, index=feature_names).abs().sort_values(ascending=False)
print("\nTop 10 features (|coeficiente|):")
print(lr_coefs.head(10))

# ==================== ÁRVORE DE DECISÃO ====================
print("\n" + "="*60)
print("ÁRVORE DE DECISÃO")
print("="*60)

dt = DecisionTreeRegressor(max_depth=10, min_samples_leaf=50, random_state=42)
dt.fit(X_train, y_train)
y_pred_dt = dt.predict(X_test)

r2_dt = r2_score(y_test, y_pred_dt)
rmse_dt = np.sqrt(mean_squared_error(y_test, y_pred_dt))
mae_dt = mean_absolute_error(y_test, y_pred_dt)

print(f"R² Score: {r2_dt:.4f}")
print(f"RMSE: {rmse_dt:.2f}")
print(f"MAE: {mae_dt:.2f}")

dt_importances = pd.Series(dt.feature_importances_, index=feature_names).sort_values(ascending=False)
print("\nTop 10 features mais importantes:")
print(dt_importances.head(10))

# Comparacao
print("\n" + "="*60)
print("COMPARACAO")
print("="*60)
print(f"{'Modelo':<25} {'R²':<10} {'RMSE':<12} {'MAE':<10}")
print("-"*57)
print(f"{'Regressao Linear':<25} {r2_lr:.4f}     {rmse_lr:.2f}      {mae_lr:.2f}")
print(f"{'Arvore de Decisao':<25} {r2_dt:.4f}     {rmse_dt:.2f}      {mae_dt:.2f}")
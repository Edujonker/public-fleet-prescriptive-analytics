#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark Científico de Modelos de Regressão Linear Aplicados a Frotas Públicas
Autores: Eduardo Lopes Jonker, Profa. Dra. Vivian Kremer Kalempa, Prof. Dr. Yuri Kaszubowski Lopes
PPGCAP / CCT / UDESC
"""

import os
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import (
    LinearRegression, RidgeCV, LassoCV, ElasticNetCV,
    HuberRegressor, RANSACRegressor, TheilSenRegressor,
    BayesianRidge, QuantileRegressor, TweedieRegressor
)
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, median_absolute_error

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "os_dataset_limpo.csv"
OUT_JSON = BASE_DIR / "resultados_modelagem" / "benchmark_regressoes_lineares.json"
OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

def load_and_preprocess(sample_size=100000, random_state=42):
    print(f"Carregando dados de {DATA_PATH}...")
    use_cols = [
        'nr_anoveiculo', 'nr_quilometragem', 'nr_quantidade_pecas',
        'nr_quantidade_hora_mao_de_obra', 'tipo_manutencao_oficina',
        'ds_familia', 'Valor_Aprovado'
    ]
    
    chunks = []
    total_loaded = 0
    for chunk in pd.read_csv(DATA_PATH, usecols=use_cols, chunksize=50000, low_memory=False):
        # Filtros de consistencia
        chunk = chunk.dropna(subset=['Valor_Aprovado'])
        chunk = chunk[chunk['Valor_Aprovado'] > 0]
        chunk = chunk[chunk['nr_quilometragem'] >= 0]
        chunk = chunk[chunk['nr_anoveiculo'] >= 1990]
        chunks.append(chunk)
        total_loaded += len(chunk)
        if total_loaded >= sample_size * 2:
            break
            
    df = pd.concat(chunks, ignore_index=True)
    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=random_state)
        
    print(f"Amostra consolidada: {len(df):,} registros.")
    
    # Feature engineering
    current_year = 2026
    df['idade_veiculo'] = current_year - df['nr_anoveiculo']
    df['idade_veiculo'] = df['idade_veiculo'].clip(lower=0, upper=35)
    df['km_por_ano'] = df['nr_quilometragem'] / (df['idade_veiculo'] + 1)
    df['is_corretiva'] = (df['tipo_manutencao_oficina'].astype(str).str.upper().str.contains('CORRETIVA')).astype(int)
    
    # Segmentos de frota dummificados
    familias_top = df['ds_familia'].value_counts().nlargest(5).index
    for fam in familias_top:
        col_name = f'fam_{fam}'.replace(' ', '_').lower()
        df[col_name] = (df['ds_familia'] == fam).astype(int)
        
    feature_cols = [
        'idade_veiculo', 'nr_quilometragem', 'km_por_ano',
        'nr_quantidade_pecas', 'nr_quantidade_hora_mao_de_obra',
        'is_corretiva'
    ] + [f'fam_{fam}'.replace(' ', '_').lower() for fam in familias_top]
    
    X = df[feature_cols].copy()
    y = pd.to_numeric(df['Valor_Aprovado'], errors='coerce').fillna(0).values
    
    # Garantir conversão estrita de cada coluna para float
    for c in feature_cols:
        X[c] = pd.to_numeric(X[c], errors='coerce').fillna(0.0)
    
    # Preenchimento de eventuais nulos
    X = X.fillna(0.0)
    
    return X, y, feature_cols

def run_benchmark():
    X, y, feature_names = load_and_preprocess(sample_size=60000)
    
    # Split Treino / Teste (80% / 20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalizacao para modelos regularizados
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Amostra reduzida para modelos computacionalmente caros (Quantile, TheilSen)
    X_train_sub = X_train_scaled[:15000]
    y_train_sub = y_train[:15000]
    
    models = {
        "1. OLS (Mínimos Quadrados Ordinários)": LinearRegression(),
        "2. Ridge Regression (L2 Tikhonov)": RidgeCV(alphas=np.logspace(-2, 3, 20)),
        "3. Lasso Regression (L1 Esparsa)": LassoCV(alphas=np.logspace(-2, 2, 20), max_iter=3000, random_state=42),
        "4. ElasticNet (L1 + L2 Balanceada)": ElasticNetCV(l1_ratio=[.1, .5, .7, .9], max_iter=3000, random_state=42),
        "5. Huber Regressor (M-Estimador Robusto)": HuberRegressor(epsilon=1.35, max_iter=1000),
        "6. RANSAC Regressor (Consenso Aleatório)": RANSACRegressor(random_state=42, min_samples=0.6),
        "7. Theil-Sen (Estimador Não-Paramétrico)": TheilSenRegressor(random_state=42, max_subpopulation=2000, n_subsamples=50),
        "8. Bayesian Ridge (Inferência Probabilística)": BayesianRidge(max_iter=500),
        "9. Quantile Regression (Mediana tau=0.50)": QuantileRegressor(quantile=0.5, alpha=0.0, solver='highs'),
        "10. GLM Gamma (Ligação Logarítmica)": TweedieRegressor(power=2.0, link='log', max_iter=1000)
    }
    
    results = {}
    
    print("\nExecutando treinamento e avaliação comparativa...")
    for name, model in models.items():
        t0 = time.time()
        is_sub = "Theil-Sen" in name or "Quantile" in name
        
        X_tr = X_train_sub if is_sub else X_train_scaled
        y_tr = y_train_sub if is_sub else y_train
        
        try:
            model.fit(X_tr, y_tr)
            train_time = time.time() - t0
            
            t1 = time.time()
            y_pred = model.predict(X_test_scaled)
            pred_time = time.time() - t1
            
            # Métricas
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            medae = median_absolute_error(y_test, y_pred)
            
            # MAPE evitando divisão por zero
            non_zero = y_test > 10.0
            mape = np.mean(np.abs((y_test[non_zero] - y_pred[non_zero]) / y_test[non_zero])) * 100.0
            
            # Coeficientes
            coefs = getattr(model, 'coef_', None)
            if coefs is not None and isinstance(coefs, np.ndarray):
                n_nonzero = int(np.sum(np.abs(coefs) > 1e-5))
                top_coefs = dict(zip(feature_names, [round(float(c), 4) for c in coefs.flatten()]))
            else:
                n_nonzero = len(feature_names)
                top_coefs = {}
                
            results[name] = {
                "R2": round(float(r2), 4),
                "MAE": round(float(mae), 2),
                "RMSE": round(float(rmse), 2),
                "MedAE": round(float(medae), 2),
                "MAPE_pct": round(float(mape), 2),
                "NonZero_Coefs": n_nonzero,
                "TrainTime_s": round(float(train_time), 3),
                "PredTime_s": round(float(pred_time), 3),
                "Top_Coeficients": top_coefs
            }
            print(f"  [OK] {name:45s} | R² = {r2:6.4f} | MAE = R$ {mae:8.2f} | MedAE = R$ {medae:8.2f} | {train_time:5.2f}s")
        except Exception as e:
            print(f"  [ERRO] {name}: {e}")
            results[name] = {"error": str(e)}

    # Salva json
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\nResultados salvos em {OUT_JSON}")
    return results

if __name__ == "__main__":
    run_benchmark()

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import json

def main():
    csv_path = Path("os_dataset_limpo.csv")
    if not csv_path.exists():
        csv_path = Path("Geral_de_OS_23439885_202609110934.csv")

    print(f"Carregando: {csv_path}")
    if csv_path.name == "os_dataset_limpo.csv":
        df = pd.read_csv(csv_path, encoding="utf-8", low_memory=False)
    else:
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)
    print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")

    # Converter colunas de valor
    value_cols = ["vl_orcado", "Valor_Aprovado", "vl_total_peca", "vl_total_mao_de_obra",
                  "vl_unitario_peca", "vl_unitario_mao_de_obra", "valor_peca_orcado",
                  "valor_mo_orcado", "Valor_Aprovado_Peca", "Valor_Aprovado_MaoDeObra",
                  "nr_quantidade_pecas"]
    for col in value_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)

    # Garantir que nr_quilometragem e nr_anoveiculo sao numericos
    for col in ["nr_quilometragem", "nr_anoveiculo"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Converter datas
    date_cols = ["dt_transacao", "dt_aprovacao_item", "dt_entrada_veiculo_oficina"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Agregar por OS: calcular atributos por OS
    print("\nAgregando por OS...")
    os_group = df.groupby("cd_manutencao_oficina").agg({
        "nr_quantidade_pecas": "sum",
        "vl_orcado": "sum",
        "vl_total_peca": "sum",
        "vl_total_mao_de_obra": "sum",
        "nr_quilometragem": "max",
        "nr_anoveiculo": "max",
    }).reset_index()

    os_group.columns = ["os_id", "total_pecas", "total_orcado", "total_peca", "total_mao_obra", "quilometragem_max", "ano_veiculo"]

    # Adicionar tipo de manutencao mais comum
    tipo_os = df.groupby("cd_manutencao_oficina")["tipo_manutencao_oficina"].agg(lambda x: x.mode()[0] if not x.mode().empty else "OUTRO").reset_index()
    tipo_os.columns = ["os_id", "tipo_manutencao"]
    os_group = os_group.merge(tipo_os, on="os_id")

    print(f"OS consolidadas: {len(os_group)}")

    # Features para modelo
    model_features = ["total_pecas", "total_orcado", "total_peca", "total_mao_obra", "quilometragem_max", "ano_veiculo"]
    X = os_group[model_features].fillna(0)

    # Normalizar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Testar diferentes contaminacao
    print("\nTestando diferentes niveis de contaminacao...")
    for contamination in [0.01, 0.02, 0.05, 0.10]:
        model = IsolationForest(contamination=contamination, n_estimators=200, random_state=42)
        preds = model.fit_predict(X_scaled)
        n_anom = (preds == -1).sum()
        pct = (n_anom / len(preds)) * 100
        print(f"  contamination={contamination}: {n_anom} anomalias ({pct:.2f}%)")

    # Usar contamination=0.05 como padrao
    model = IsolationForest(contamination=0.05, n_estimators=200, random_state=42)
    preds = model.fit_predict(X_scaled)
    scores = model.score_samples(X_scaled)

    os_group["is_anomaly"] = preds
    os_group["anomaly_score"] = scores

    n_anom = (preds == -1).sum()
    pct = (n_anom / len(preds)) * 100
    print(f"\nResultado final (contamination=0.05): {n_anom} anomalias de {len(os_group)} OS ({pct:.2f}%)")

    # Salvar
    anomalies = os_group[os_group["is_anomaly"] == -1].copy()
    anomalies.to_csv("os_anomalias_consolidadas.csv", index=False)
    print(f"Anomalias salvas em: os_anomalias_consolidadas.csv")

    # Metricas
    metrics = {
        "total_os": int(len(os_group)),
        "total_anomalias": int(n_anom),
        "percentual_anomalias": float(pct),
        "contaminacao": 0.05,
        "features_usadas": model_features,
    }
    with open("metricas_anomalias.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("Metricas salvas em: metricas_anomalias.json")

if __name__ == "__main__":
    main()
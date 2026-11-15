import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def detect_separator(path: Path):
    for sep in [";", ",", "\t", "|"]:
        try:
            pd.read_csv(path, sep=sep, encoding="latin1", engine="python", nrows=5)
            return sep
        except Exception:
            pass
    raise ValueError(f"Não foi possível detectar o separador do CSV: {path}")


def normalize_col_name(col_name):
    return re.sub(r"[^a-z0-9]+", "", str(col_name).lower())


def clean_numeric_column(series):
    s = series.astype(str).str.strip()
    s = s.str.replace(".", "", regex=False)
    s = s.str.replace(",", ".", regex=False)
    s = s.str.replace("R$", "", regex=False)
    s = s.str.replace(" ", "", regex=False)
    s = s.replace("", "NaN")
    s = s.replace("nan", "NaN")
    s = s.replace("None", "NaN")
    s = s.replace("N/A", "NaN")
    return pd.to_numeric(s, errors="coerce")


def find_date_column(df):
    date_candidates = [
        "data_os",
        "dataabertura",
        "datadeabertura",
        "data",
        "datacadastro",
        "datacriacao",
        "dataemissao",
        "dtabertura",
        "datahora",
        "datainicio",
        "dt_aprovacao_item",
    ]
    normalized = {normalize_col_name(c): c for c in df.columns}
    for candidate in date_candidates:
        if candidate in normalized:
            return normalized[candidate]
    for col in df.columns:
        if "data" in normalize_col_name(col) or "dt" in normalize_col_name(col):
            return col
    return None


def ensure_numeric_value(series):
    if pd.api.types.is_numeric_dtype(series):
        return series
    return clean_numeric_column(series)


def save_chart(fig, filename, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close(fig)


def create_charts(df, anomalies, output_dir):
    chart_dir = output_dir
    chart_dir.mkdir(parents=True, exist_ok=True)

    if "Valor_Aprovado" in df.columns:
        value_series = ensure_numeric_value(df["Valor_Aprovado"])
        anomaly_value_series = ensure_numeric_value(anomalies["Valor_Aprovado"]) if not anomalies.empty else pd.Series(dtype=float)
    else:
        numeric_candidates = [col for col in df.columns if col not in ["is_anomaly", "anomaly_score"]]
        value_series = pd.to_numeric(df[numeric_candidates[0]], errors="coerce") if numeric_candidates else pd.Series(dtype=float)
        anomaly_value_series = pd.to_numeric(anomalies[numeric_candidates[0]], errors="coerce") if not anomalies.empty and numeric_candidates else pd.Series(dtype=float)

    fig, ax = plt.subplots(figsize=(8, 5))
    counts = pd.Series({"Normais": len(df) - len(anomalies), "Anômalos": len(anomalies)})
    counts.plot(kind="bar", ax=ax, color=["#2E86DE", "#D95F02"])
    ax.set_title("Distribuição de registros normais e anômalos")
    ax.set_ylabel("Quantidade")
    ax.set_xlabel("Classe")
    save_chart(fig, "grafico_1.png", chart_dir)

    fig, ax = plt.subplots(figsize=(8, 5))
    if len(anomalies) > 0:
        ax.hist(anomalies["anomaly_score"].astype(float), bins=40, color="#D95F02", alpha=0.8, edgecolor="black")
    ax.set_title("Distribuição do score de anomalia")
    ax.set_xlabel("Score de anomalia")
    ax.set_ylabel("Frequência")
    save_chart(fig, "grafico_2.png", chart_dir)

    if "dt_aprovacao_item" in df.columns:
        dt_series = pd.to_datetime(df["dt_aprovacao_item"], errors="coerce").dropna()
        if not dt_series.empty:
            monthly = dt_series.dt.to_period("M").value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(10, 5))
            monthly.plot(kind="line", ax=ax, color="#2E86DE", marker="o")
            ax.set_title("Evolução temporal das ocorrências")
            ax.set_xlabel("Período")
            ax.set_ylabel("Quantidade de registros")
            save_chart(fig, "grafico_3.png", chart_dir)

    fig, ax = plt.subplots(figsize=(7, 5))
    if not value_series.empty:
        normal_values = value_series[df["is_anomaly"].ne(-1)] if "is_anomaly" in df.columns else value_series
        anomaly_values = anomaly_value_series if not anomaly_value_series.empty else pd.Series([], dtype=float)
        if not anomaly_values.empty and not normal_values.empty:
            data_to_plot = [normal_values.dropna().astype(float), anomaly_values.dropna().astype(float)]
            ax.boxplot(data_to_plot, labels=["Normais", "Anômalos"], patch_artist=True, boxprops={"facecolor": "#B3D9FF"}, medianprops={"color": "#1F3A5F"})
            ax.set_title("Comparação de valores em registros normais e anômalos")
            ax.set_ylabel("Valor de referência")
            save_chart(fig, "grafico_4.png", chart_dir)
        else:
            values = value_series.dropna().astype(float)
            ax.hist(values, bins=30, color="#2E86DE", alpha=0.75)
            ax.set_title("Distribuição geral de valores")
            ax.set_ylabel("Frequência")
            save_chart(fig, "grafico_4.png", chart_dir)

    metrics = {
        "total_linhas": int(len(df)),
        "total_colunas": int(len(df.columns)),
        "anomalias": int(len(anomalies)),
        "percentual_anomalias": float((len(anomalies) / len(df)) * 100 if len(df) else 0.0),
        "data_inicial": str(df["dt_aprovacao_item"].min()) if "dt_aprovacao_item" in df.columns else None,
        "data_final": str(df["dt_aprovacao_item"].max()) if "dt_aprovacao_item" in df.columns else None,
    }
    summary_path = chart_dir / "resumo_metricas.json"
    summary_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    csv_path = Path("Geral_de_OS_23439885_202609110934.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    sep = detect_separator(csv_path)
    df = pd.read_csv(csv_path, sep=sep, encoding="latin1", engine="python")
    print("=== Análise de outliers em manutenção de frota ===")
    print(f"Arquivo carregado: {csv_path}")
    print(f"Linhas: {len(df)}")
    print(f"Colunas: {len(df.columns)}")

    date_col = find_date_column(df)
    if date_col:
        print(f"Coluna de data encontrada: {date_col}")
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        print(f"Intervalo de data: {df[date_col].min()} até {df[date_col].max()}")
    else:
        print("Nenhuma coluna de data identificada.")

    numeric_cols = []
    for col in df.columns:
        if col == date_col:
            continue
        try:
            pd.to_numeric(df[col], errors="raise")
            numeric_cols.append(col)
        except Exception:
            pass

    if not numeric_cols:
        raise ValueError("Nenhuma coluna numérica útil foi encontrada.")

    cleaned = df[numeric_cols].copy()
    for col in cleaned.columns:
        cleaned[col] = clean_numeric_column(cleaned[col])

    cleaned = cleaned.dropna(axis=1, how="all")
    cleaned = cleaned.fillna(0)
    cleaned = cleaned.loc[:, cleaned.nunique() > 1]

    if cleaned.empty:
        raise ValueError("Não há variabilidade suficiente para aplicar o modelo.")

    scaler = StandardScaler()
    X = scaler.fit_transform(cleaned)

    model = IsolationForest(contamination=0.01, n_estimators=200, random_state=42)
    predictions = model.fit_predict(X)
    scores = model.score_samples(X)

    df["is_anomaly"] = predictions
    df["anomaly_score"] = scores

    anomalies = df[df["is_anomaly"] == -1].copy()
    anomaly_rate = (len(anomalies) / len(df)) * 100 if len(df) else 0.0
    print(f"Total de anomalias detectadas: {len(anomalies)}")
    print(f"Percentual: {anomaly_rate:.2f}%")

    print("\nTop 10 registros anômalos:")
    top_anomalies = anomalies.sort_values("anomaly_score").head(10)
    print(top_anomalies.to_string(index=False, max_colwidth=20))

    output_path = Path("os_anomalias.csv")
    anomalies.to_csv(output_path, index=False, encoding="latin1")
    print(f"\nArquivo salvo em: {output_path}")

    chart_dir = Path("charts")
    create_charts(df, anomalies, chart_dir)
    print(f"Gráficos salvos em: {chart_dir}")

if __name__ == "__main__":
    main()
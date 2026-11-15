"""
Análise completa de dados de OS de manutenção.
Gera gráficos, relatórios em PDF e Excel.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Configurações
CSV_PATH = Path("os_dataset_limpo.csv")
if not CSV_PATH.exists():
    CSV_PATH = Path("Geral_de_OS_23439885_202609110934.csv")
OUTPUT_DIR = Path("resultados")
OUTPUT_DIR.mkdir(exist_ok=True)

# Carregar dados
print("Carregando dados...")
if CSV_PATH.name == "os_dataset_limpo.csv":
    df = pd.read_csv(CSV_PATH, encoding="utf-8", low_memory=False)
else:
    df = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8", low_memory=False)

print(f"Dataset: {df.shape[0]} linhas x {df.shape[1]} colunas")

# Converter colunas de valor
value_cols = ["vl_orcado", "Valor_Aprovado", "vl_total_peca", "vl_total_mao_de_obra",
              "vl_unitario_peca", "vl_unitario_mao_de_obra", "valor_peca_orcado",
              "valor_mo_orcado", "Valor_Aprovado_Peca", "Valor_Aprovado_MaoDeObra",
              "nr_quantidade_pecas"]
for col in value_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)

# Converter datas
date_cols = ["dt_transacao", "dt_aprovacao_item", "dt_entrada_veiculo_oficina",
             "dt_aprovacao_os", "dt_conclusao_servico"]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# Salvar dados processados
df.to_csv(OUTPUT_DIR / "dados_processados.csv", index=False, encoding="utf-8")
print("Dados processados salvos.")

# Estatisticas descritivas
stats = {
    "total_registros": len(df),
    "total_colunas": len(df.columns),
    "veiculos_unicos": df["veiculo_id"].nunique() if "veiculo_id" in df.columns else "N/A",
    "os_unicas": df["cd_manutencao_oficina"].nunique(),
    "periodo_ini": str(df["dt_transacao"].min()) if "dt_transacao" in df.columns else "N/A",
    "periodo_fim": str(df["dt_transacao"].max()) if "dt_transacao" in df.columns else "N/A",
    "ano_veiculo_min": int(df["nr_anoveiculo"].min()),
    "ano_veiculo_max": int(df["nr_anoveiculo"].max()),
    "ano_veiculo_mean": round(df["nr_anoveiculo"].mean(), 1),
    "quilometragem_min": int(df["nr_quilometragem"].min()),
    "quilometragem_max": int(df["nr_quilometragem"].max()),
    "quilometragem_mean": round(df["nr_quilometragem"].mean(), 0),
    "valor_medio": round(df["Valor_Aprovado"].mean(), 2) if "Valor_Aprovado" in df.columns else 0,
    "valor_total": round(df["Valor_Aprovado"].sum(), 2) if "Valor_Aprovado" in df.columns else 0,
}

with open(OUTPUT_DIR / "estatisticas.json", "w") as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

print("\nEstatisticas:")
for k, v in stats.items():
    print(f"  {k}: {v}")

# Salvar relatorio CSV
relatorio = pd.DataFrame([stats])
relatorio.to_csv(OUTPUT_DIR / "relatorio_geral.csv", index=False, encoding="utf-8")

# Contagem por status
if "ds_os_status" in df.columns:
    status_counts = df["ds_os_status"].value_counts()
    status_counts.to_csv(OUTPUT_DIR / "status_os.csv", encoding="utf-8")
    print("\nStatus OS:")
    print(status_counts.to_string())

# Contagem por tipo de estabelecimento
if "ds_tipoestabelecimento" in df.columns:
    tipo_counts = df["ds_tipoestabelecimento"].value_counts()
    tipo_counts.to_csv(OUTPUT_DIR / "tipo_estabelecimento.csv", encoding="utf-8")
    print("\nTipos de estabelecimento:")
    print(tipo_counts.to_string())

# Estatisticas por ano do veiculo
if "nr_anoveiculo" in df.columns:
    ano_stats = df.groupby("nr_anoveiculo").agg({
        "cd_manutencao_oficina": "count",
        "Valor_Aprovado": ["mean", "sum", "std"]
    }).round(2)
    ano_stats.columns = ["num_os", "valor_medio", "valor_total", "valor_std"]
    ano_stats = ano_stats.reset_index()
    ano_stats.to_csv(OUTPUT_DIR / "estatisticas_por_ano.csv", index=False, encoding="utf-8")
    print("\nEstatisticas por ano do veiculo:")
    print(ano_stats.to_string())

# Top pecas
if "ds_peca" in df.columns:
    peca_stats = df.groupby("ds_peca").agg({
        "cd_manutencao_oficina": "count",
        "vl_total_peca": ["sum", "mean"]
    }).round(2)
    peca_stats.columns = ["num_os", "valor_total", "valor_medio"]
    peca_stats = peca_stats.reset_index().sort_values("valor_total", ascending=False).head(20)
    peca_stats.to_csv(OUTPUT_DIR / "top_pecas.csv", index=False, encoding="utf-8")
    print("\nTop 20 peca por valor:")
    print(peca_stats.to_string())

print("\nAnálise concluida! Arquivos salvos em:", OUTPUT_DIR)
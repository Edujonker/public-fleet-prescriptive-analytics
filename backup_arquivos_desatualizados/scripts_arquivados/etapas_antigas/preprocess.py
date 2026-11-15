"""
Preprocessamento de dados: pseudonimização e limpeza para análise.
Gera um dataset sem dados sensíveis mantendo identificador por veículo.
"""
import hashlib
import pandas as pd
from pathlib import Path


def anonymize_plate(plate):
    """Converte placa em hash SHA256 mantendo unicidade."""
    if pd.isna(plate):
        return "UNKNOWN"
    return hashlib.sha256(str(plate).upper().encode()).hexdigest()[:12]


def main():
    csv_path = Path("Geral_de_OS_23439885_202609110934.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    print("Carregando dados brutos...")
    df = pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)
    print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")

    # --- Pseudonimização ---
    print("\nPseudonimizando dados sensíveis...")

    # Placa -> hash consistente por veículo
    df["veiculo_id"] = df["ds_placa"].apply(anonymize_plate)

    # Remover colunas identificadores diretos
    sensitive_cols = [
        "ds_placa",           # placa do veículo
        "nome_completo",      # nome do cliente
        "ds_motorista",       # nome do motorista
        "ds_cidade",          # cidade (identificável)
        "ds_nomereduzido",    # nome reduzido do cliente
        "ds_nomereduzido.1",  # nome reduzido duplicado
        "cd_cgc",             # CNPJ
        "CD_TITULO",          # título
        "ds_fabricante",      # pode ser sensível
    ]

    for col in sensitive_cols:
        if col in df.columns:
            df = df.drop(columns=[col])
            print(f"  Removida: {col}")

    # Manter apenas colunas relevantes para análise
    keep_cols = [
        "veiculo_id",
        "cdCliente",
        "ds_veiculomodelo",
        "ds_familia",
        "nr_anoveiculo",
        "nr_quilometragem",
        "cd_manutencao_oficina",
        "tipo_manutencao_oficina",
        "cd_estabelecimento",
        "ds_tipoestabelecimento",
        "ds_os_status",
        "ds_peca",
        "dsgrupo_peca",
        "ds_fabricante_peca",
        "ds_complemento_peca",
        "ds_mao_de_obra",
        "nr_quantidade_pecas",
        "valor_peca_orcado",
        "Valor_Aprovado_Peca",
        "vl_total_mao_de_obra",
        "valor_mo_orcado",
        "Valor_Aprovado_MaoDeObra",
        "vl_orcado",
        "Valor_Aprovado",
        "vl_total_peca",
        "vl_unitario_peca",
        "vl_unitario_mao_de_obra",
        "nr_quantidade_hora_mao_de_obra",
        "dt_aprovacao_item",
        "dt_reprovacao_item",
        "dt_cancelamento_item",
        "dt_transacao",
        "dt_envio_orcamento",
        "dt_entrada_veiculo_oficina",
        "dt_aprovacao_os",
        "dt_conclusao_servico",
        "dt_retirada_veiculo",
        "dt_reprovacao_os",
        "relato_gestor_auto",
        "fl_aprovacao_atipica",
        "ds_uf",
        "ds_tipofrota",
        "ds_complemento",
        "ds_informacao_adicional1",
        "ds_informacao_adicional2",
        "ds_informacao_adicional3",
        "ds_informacao_adicional4",
        "ds_informacao_adicional5",
    ]

    existing_cols = [c for c in keep_cols if c in df.columns]
    df_clean = df[existing_cols].copy()

    # Converter colunas de valor para float
    value_cols = [
        "valor_peca_orcado", "Valor_Aprovado_Peca",
        "vl_total_mao_de_obra", "valor_mo_orcado",
        "Valor_Aprovado_MaoDeObra", "vl_orcado",
        "Valor_Aprovado", "vl_total_peca",
        "vl_unitario_peca", "vl_unitario_mao_de_obra",
        "nr_quantidade_hora_mao_de_obra",
    ]

    for col in value_cols:
        if col in df_clean.columns:
            df_clean[col] = (
                df_clean[col].astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
                .astype(float)
            )

    # Converter colunas de data
    date_cols = [
        "dt_aprovacao_item", "dt_reprovacao_item", "dt_cancelamento_item",
        "dt_transacao", "dt_envio_orcamento", "dt_entrada_veiculo_oficina",
        "dt_aprovacao_os", "dt_conclusao_servico", "dt_retirada_veiculo",
        "dt_reprovacao_os",
    ]
    for col in date_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")

    # Salvar dataset limpo
    output_path = Path("os_dataset_limpo.csv")
    df_clean.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nDataset limpo salvo em: {output_path}")
    print(f"Linhas: {len(df_clean)} | Colunas: {len(df_clean.columns)}")

    # Estatisticas
    print("\n=== ESTATÍSTICAS DO DATASET LIMPO ===")
    print(f"Veículos únicos: {df_clean['veiculo_id'].nunique()}")
    print(f"Veículos com mais de 1 OS: {(df_clean['veiculo_id'].value_counts() > 1).sum()}")
    print(f"Veículos com apenas 1 OS: {(df_clean['veiculo_id'].value_counts() == 1).sum()}")
    print(f"Média de OS por veículo: {df_clean['veiculo_id'].value_counts().mean():.2f}")
    print(f"Mediana de OS por veículo: {df_clean['veiculo_id'].value_counts().median():.0f}")

    if "dt_transacao" in df_clean.columns:
        print(f"\nPeríodo: {df_clean['dt_transacao'].min()} até {df_clean['dt_transacao'].max()}")

    print(f"\nColunas restantes: {list(df_clean.columns)}")


if __name__ == "__main__":
    main()
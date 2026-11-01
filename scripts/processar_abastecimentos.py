#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador e Ingestor da Base de Abastecimentos de Combustível
Dissertação de Mestrado, PPGCAP/UDESC
Autor: Eduardo Lopes Jonker

Lê a base bruta de 1.000.000 de abastecimentos (dados/2161_abastecimentos_pg0001.xlsb),
higieniza os campos, anonimiza dados pessoais (LGPD), calcula indicadores
de consumo (km/l, custo/km), converte para formato Parquet e alimenta
o banco SQLite analítico e o dashboard interativo.
"""

import sys
import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import pyxlsb
import pandas as pd
import numpy as np

def excel_date_to_str(serial):
    if serial is None or serial == "":
        return None
    try:
        dt = datetime(1899, 12, 30) + timedelta(days=float(serial))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(serial)

def hash_condutor(nome):
    if not nome or pd.isna(nome) or str(nome).strip() == "" or str(nome).lower() == "none":
        return "NÃO INFORMADO"
    return "COND_" + hashlib.sha256(str(nome).strip().encode("utf-8")).hexdigest()[:12].upper()

def processar_abastecimentos():
    start_time = datetime.now()
    base_dir = Path(__file__).resolve().parent.parent
    xlsb_path = base_dir / "dados" / "2161_abastecimentos_pg0001.xlsb"
    parquet_path = base_dir / "dados" / "abastecimentos_processados.parquet"
    db_path = base_dir / "dados" / "resultados_dissertacao.db"
    json_path = base_dir / "dashboard" / "data" / "abastecimentos_stats.json"

    print("=" * 80)
    print(" INGESTÃO E PROCESSAMENTO DA BASE DE ABASTECIMENTOS (PPGCAP/UDESC)")
    print(f" Arquivo de Origem: {xlsb_path}")
    print(f" Início: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    if not xlsb_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {xlsb_path}")
        sys.exit(1)

    print("\n[1/5] Lendo registros do arquivo binário .xlsb...")
    
    rows_data = []
    header_map = {
        0: "cod_venda",
        1: "data_excel",
        2: "horario",
        3: "prefixo",
        4: "placa",
        5: "unidade",
        6: "subunidade",
        7: "combustivel",
        8: "condutor",
        11: "posto",
        12: "uf_posto",
        14: "cidade_posto",
        15: "tipo_frota",
        16: "marca",
        17: "modelo",
        18: "tipo_veiculo",
        19: "ano_veiculo",
        20: "cnpj_posto",
        22: "odometro",
        23: "litros",
        24: "preco_unitario",
        26: "valor_total",
        28: "km_l_sistema",
        29: "km_rodados_sistema",
        31: "tipo_venda",
    }

    total_lidos = 0
    with pyxlsb.open_workbook(str(xlsb_path)) as wb:
        with wb.get_sheet('Plan1') as sheet:
            for i, row in enumerate(sheet.rows()):
                if i < 7:
                    continue  # Pula cabeçalhos institucionais e nomes de colunas
                
                # Extrai apenas as colunas relevantes para economizar memória e acelerar
                r_dict = {}
                for idx, col_name in header_map.items():
                    if idx < len(row):
                        r_dict[col_name] = row[idx].v
                    else:
                        r_dict[col_name] = None
                        
                rows_data.append(r_dict)
                total_lidos += 1
                if total_lidos % 200000 == 0:
                    print(f"  -> {total_lidos:,} registros lidos...")

    print(f"  -> Total de registros brutos extraídos: {len(rows_data):,}")

    print("\n[2/5] Convertendo para DataFrame e saneando atributos...")
    df = pd.DataFrame(rows_data)
    del rows_data  # Libera memória

    # Tratamento de Data
    print("  -> Convertendo datas e períodos...")
    df["data"] = pd.to_datetime(
        df["data_excel"].apply(excel_date_to_str),
        format="%Y-%m-%d",
        errors="coerce"
    )
    df.drop(columns=["data_excel"], inplace=True)
    df["ano"] = df["data"].dt.year
    df["mes_ano"] = df["data"].dt.to_period("M").astype(str)

    # Tratamento de Strings e Padronização
    print("  -> Padronizando placas, veículos e unidades...")
    df["placa"] = df["placa"].astype(str).str.strip().str.upper().str.replace("-", "", regex=False)
    df["prefixo"] = df["prefixo"].astype(str).str.strip().str.upper()
    df["combustivel"] = df["combustivel"].astype(str).str.strip().str.upper()
    df["marca"] = df["marca"].astype(str).str.strip().str.upper()
    df["modelo"] = df["modelo"].astype(str).str.strip().str.upper()
    df["unidade"] = df["unidade"].astype(str).str.strip()
    df["subunidade"] = df["subunidade"].astype(str).str.strip()
    df["cidade_posto"] = df["cidade_posto"].astype(str).str.strip().str.upper()
    df["posto"] = df["posto"].astype(str).str.strip().str.upper()

    # Anonimização de condutor (LGPD)
    print("  -> Aplicando anonimização criptográfica LGPD nos condutores...")
    df["condutor_anon"] = df["condutor"].apply(hash_condutor)
    df.drop(columns=["condutor"], inplace=True)

    # Tratamento de Numéricos
    print("  -> Convertendo variáveis contínuas monetárias e volumétricas...")
    numeric_cols = ["odometro", "litros", "preco_unitario", "valor_total", "km_l_sistema", "km_rodados_sistema"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Cálculo auditado de preço total quando zerado
    mask_calc = (df["valor_total"] <= 0) & (df["litros"] > 0) & (df["preco_unitario"] > 0)
    df.loc[mask_calc, "valor_total"] = df.loc[mask_calc, "litros"] * df.loc[mask_calc, "preco_unitario"]

    # Identificação de anomalias de abastecimento
    print("  -> Identificando anomalias de abastecimento...")
    df["flag_anomalia_volume"] = (df["litros"] > 120.0) & (~df["tipo_veiculo"].str.contains("CAMINH|ONIBUS|TRAT", case=False, na=False))
    df["flag_anomalia_kml"] = (df["km_l_sistema"] > 40.0) | ((df["km_l_sistema"] < 1.5) & (df["km_l_sistema"] > 0))
    df["flag_preco_discrepante"] = (df["preco_unitario"] > 9.0) | ((df["preco_unitario"] < 2.0) & (df["preco_unitario"] > 0))

    print("\n[3/5] Salvando base estruturada em formato Parquet de alta performance...")
    df.to_parquet(parquet_path, index=False, compression="snappy")
    tamanho_mb = parquet_path.stat().st_size / (1024 * 1024)
    print(f"  ✔ Arquivo salvo: {parquet_path} ({tamanho_mb:.2f} MB)")

    print("\n[4/5] Gravando no banco relacional analítico SQLite...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Cria tabela de abastecimentos com schema e tipos explícitos
    cur.execute("DROP TABLE IF EXISTS abastecimentos;")
    df.to_sql("abastecimentos", conn, if_exists="replace", index=False)
    
    print("  -> Criando índices analíticos...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_abast_placa ON abastecimentos(placa);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_abast_data ON abastecimentos(data);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_abast_ano ON abastecimentos(ano);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_abast_combustivel ON abastecimentos(combustivel);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_abast_cidade ON abastecimentos(cidade_posto);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_abast_unidade ON abastecimentos(unidade);")
    conn.commit()
    conn.close()
    print("  ✔ Tabela 'abastecimentos' e índices criados no banco SQLite com sucesso!")

    print("\n[5/5] Calculando KPIs agregados e gerando JSON para o Dashboard Interativo...")
    
    total_registros = len(df)
    total_gasto = float(df["valor_total"].sum())
    total_litros = float(df["litros"].sum())
    veiculos_unicos = int(df["placa"].replace("", np.nan).dropna().nunique())
    postos_unicos = int(df["posto"].nunique())
    cidades_unicas = int(df["cidade_posto"].nunique())
    preco_medio_geral = round(total_gasto / total_litros, 2) if total_litros > 0 else 0.0

    # Evolução Anual
    anual = df.groupby("ano").agg(
        total_gasto=("valor_total", "sum"),
        total_litros=("litros", "sum"),
        abastecimentos=("cod_venda", "count"),
        preco_medio=("preco_unitario", "mean")
    ).reset_index()
    anual["total_gasto"] = anual["total_gasto"].round(2)
    anual["total_litros"] = anual["total_litros"].round(2)
    anual["preco_medio"] = anual["preco_medio"].round(2)

    # Evolução Mensal (Top 36 meses)
    mensal = df.groupby("mes_ano").agg(
        total_gasto=("valor_total", "sum"),
        total_litros=("litros", "sum"),
        abastecimentos=("cod_venda", "count")
    ).reset_index().sort_values("mes_ano")
    mensal["total_gasto"] = mensal["total_gasto"].round(2)
    mensal["total_litros"] = mensal["total_litros"].round(2)

    # Distribuição por Tipo de Combustível
    combustiveis = df.groupby("combustivel").agg(
        total_gasto=("valor_total", "sum"),
        total_litros=("litros", "sum"),
        abastecimentos=("cod_venda", "count"),
        preco_medio=("preco_unitario", "mean")
    ).reset_index().sort_values("total_gasto", ascending=False)
    combustiveis["total_gasto"] = combustiveis["total_gasto"].round(2)
    combustiveis["total_litros"] = combustiveis["total_litros"].round(2)
    combustiveis["preco_medio"] = combustiveis["preco_medio"].round(2)

    # Top 15 Municípios
    municipios = df.groupby("cidade_posto").agg(
        total_gasto=("valor_total", "sum"),
        total_litros=("litros", "sum"),
        abastecimentos=("cod_venda", "count")
    ).reset_index().sort_values("total_gasto", ascending=False).head(15)
    municipios["total_gasto"] = municipios["total_gasto"].round(2)
    municipios["total_litros"] = municipios["total_litros"].round(2)

    # Top 15 Unidades / Batalhões
    unidades = df.groupby("unidade").agg(
        total_gasto=("valor_total", "sum"),
        total_litros=("litros", "sum"),
        abastecimentos=("cod_venda", "count"),
        veiculos_distintos=("placa", "nunique")
    ).reset_index().sort_values("total_gasto", ascending=False).head(15)
    unidades["total_gasto"] = unidades["total_gasto"].round(2)
    unidades["total_litros"] = unidades["total_litros"].round(2)

    # Top 15 Postos
    postos = df.groupby(["posto", "cidade_posto"]).agg(
        total_gasto=("valor_total", "sum"),
        total_litros=("litros", "sum"),
        abastecimentos=("cod_venda", "count"),
        preco_medio=("preco_unitario", "mean")
    ).reset_index().sort_values("total_gasto", ascending=False).head(15)
    postos["total_gasto"] = postos["total_gasto"].round(2)
    postos["total_litros"] = postos["total_litros"].round(2)
    postos["preco_medio"] = postos["preco_medio"].round(2)

    # Top 15 Veículos com maior consumo
    veiculos_top = df[df["placa"].str.len() >= 6].groupby(["placa", "modelo", "marca", "unidade"]).agg(
        total_gasto=("valor_total", "sum"),
        total_litros=("litros", "sum"),
        abastecimentos=("cod_venda", "count")
    ).reset_index().sort_values("total_gasto", ascending=False).head(20)
    veiculos_top["total_gasto"] = veiculos_top["total_gasto"].round(2)
    veiculos_top["total_litros"] = veiculos_top["total_litros"].round(2)

    # Contagem de Anomalias
    anomalias_resumo = {
        "volume_suspeito": int(df["flag_anomalia_volume"].sum()),
        "kml_discrepante": int(df["flag_anomalia_kml"].sum()),
        "preco_discrepante": int(df["flag_preco_discrepante"].sum()),
        "total_anomalias_detectadas": int((df["flag_anomalia_volume"] | df["flag_anomalia_kml"] | df["flag_preco_discrepante"]).sum())
    }

    stats_payload = {
        "metadata": {
            "gerado_em": datetime.now().isoformat(),
            "total_registros": total_registros,
            "periodo_inicio": str(df["data"].min().date()),
            "periodo_fim": str(df["data"].max().date()),
            "versao": "PPGCAP-2026-Abastecimentos"
        },
        "kpis": {
            "total_gasto_reais": total_gasto,
            "total_litros": total_litros,
            "veiculos_unicos": veiculos_unicos,
            "postos_unicos": postos_unicos,
            "cidades_unicas": cidades_unicas,
            "preco_medio_geral": preco_medio_geral,
            "anomalias": anomalias_resumo
        },
        "anual": anual.to_dict(orient="records"),
        "mensal": mensal.to_dict(orient="records"),
        "combustiveis": combustiveis.head(10).to_dict(orient="records"),
        "municipios": municipios.to_dict(orient="records"),
        "unidades": unidades.to_dict(orient="records"),
        "postos": postos.to_dict(orient="records"),
        "veiculos_top": veiculos_top.to_dict(orient="records")
    }

    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2, ensure_ascii=False)
    print(f"  ✔ JSON para o Dashboard gravado: {json_path}")

    # Também salva uma cópia consolidada em dados
    with open(base_dir / "dados" / "abastecimentos_kpis.json", "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2, ensure_ascii=False)

    tempo_total = (datetime.now() - start_time).total_seconds()
    print("=" * 80)
    print(" PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print(f" Registros Processados: {total_registros:,}")
    print(f" Gasto Total em Combustível: R$ {total_gasto:,.2f}")
    print(f" Volume Total: {total_litros:,.2f} Litros")
    print(f" Veículos Atendidos: {veiculos_unicos:,}")
    print(f" Tempo de Execução: {tempo_total:.2f}s ({tempo_total/60:.2f} min)")
    print("=" * 80)

if __name__ == "__main__":
    processar_abastecimentos()

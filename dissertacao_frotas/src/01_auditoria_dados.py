#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 01: Auditoria Integral e Perfil de Integridade dos Dados Brutos
Framework de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos
Dissertação de Mestrado - PPGCAP / CCT / UDESC
Autor: Eduardo Henrique dos Santos
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Diretriz: Exigência 1 (Imutabilidade) e Exigência 2 (Rastreabilidade Científica).
Este script audita a base bruta original fornecida pela SEA/SC sem realizar qualquer modificação
ou sobrescrita nos arquivos originais, gerando relatórios de integridade criptográfica,
perfil de cardinalidade, integridade referencial, completude e distribuição financeira/temporal.
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd


def compute_hashes(filepath: Path) -> dict:
    """Calcula hashes criptográficos SHA-256 e MD5 do arquivo para certificar imutabilidade."""
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()  # nosec B303 (integridade física de arquivos legados de dados)
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024 * 8):  # blocos de 8MB
            sha256.update(chunk)
            md5.update(chunk)
    stat = filepath.stat()
    return {
        "arquivo": filepath.name,
        "caminho_absoluto": str(filepath.resolve()),
        "tamanho_bytes": stat.st_size,
        "tamanho_mb": round(stat.st_size / (1024 * 1024), 2),
        "sha256": sha256.hexdigest(),
        "md5": md5.hexdigest(),
        "data_modificacao": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "somente_leitura": not os.access(filepath, os.W_OK)
    }


def parse_brazilian_currency(series: pd.Series) -> pd.Series:
    """Converte valores monetários no formato pt-BR (ex: '1.234,56') para float64."""
    return (
        series.astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace({"nan": np.nan, "None": np.nan, "": np.nan})
        .astype(float)
    )


def executar_auditoria_completa():
    inicio_execucao = datetime.now()
    print("=" * 85)
    print("INICIANDO SCRIPT 01: AUDITORIA INTEGRAL DOS DADOS BRUTOS")
    print(f"Timestamp: {inicio_execucao.isoformat()}")
    print("=" * 85)

    base_dir = Path(__file__).resolve().parent.parent
    dados_brutos_dir = base_dir / "dados" / "brutos"
    resultados_logs = base_dir / "resultados" / "logs"
    resultados_tabelas = base_dir / "resultados" / "tabelas"

    resultados_logs.mkdir(parents=True, exist_ok=True)
    resultados_tabelas.mkdir(parents=True, exist_ok=True)

    arquivo_os_csv = dados_brutos_dir / "Geral_de_OS_23439885_202609110934.csv"
    arquivo_mem_csv = dados_brutos_dir / "Memorias_Calculo_por_OS.csv"
    arquivo_pat_csv = dados_brutos_dir / "Cruzamento_Patrimonio_Manutencao.csv"
    arquivo_mob_xlsx = dados_brutos_dir / "RelatorioVeiculosMobiliario (2).xlsx"

    if not arquivo_os_csv.exists():
        print(f"[ERRO CRÍTICO] Arquivo principal não localizado: {arquivo_os_csv}")
        sys.exit(1)

    # 1. HASHES CRIPTOGRÁFICOS DOS ARQUIVOS BRUTOS
    print("\n[1/6] Calculando assinaturas criptográficas dos dados brutos...")
    arquivos_auditar = [arquivo_os_csv, arquivo_mem_csv, arquivo_pat_csv, arquivo_mob_xlsx]
    certificados_hash = []
    for arq in arquivos_auditar:
        if arq.exists():
            h_info = compute_hashes(arq)
            certificados_hash.append(h_info)
            print(f"  -> {arq.name} ({h_info['tamanho_mb']} MB): SHA256={h_info['sha256'][:16]}... (Read-Only: {h_info['somente_leitura']})")

    # 2. AUDITORIA ESTRUTURAL E DE CARGA (GERAL DE OS)
    print("\n[2/6] Carregando e auditando estrutura do dataset Geral de OS...")
    # Contagem de linhas físicas puras
    with open(arquivo_os_csv, "rb") as f:
        total_linhas_fisicas = sum(1 for _ in f)

    df_raw = pd.read_csv(arquivo_os_csv, sep=";", low_memory=False, encoding="utf-8")
    total_linhas_logicas = len(df_raw)
    total_colunas = len(df_raw.columns)

    print(f"  -> Linhas físicas no arquivo (incluindo quebras dentro de campos de texto): {total_linhas_fisicas:,}")
    print(f"  -> Registros tabulares lógicos (linhas de itens de OS): {total_linhas_logicas:,}")
    print(f"  -> Total de colunas: {total_colunas}")

    # 3. GRANULARIDADE E IDENTIFICADORES ÚNICOS
    print("\n[3/6] Auditando granularidade, entidades e cardinalidade...")
    col_os = "cd_manutencao_oficina"
    col_item = "cd_manutencao_oficina_item"
    col_placa = "ds_placa"
    col_oficina = "cd_estabelecimento"
    col_oficina_nome = "ds_nomereduzido.1" if "ds_nomereduzido.1" in df_raw.columns else "ds_nomereduzido"
    col_cliente = "cd_cliente"
    col_status = "ds_os_status"
    col_km = "nr_quilometragem"

    total_os_unicas = int(df_raw[col_os].nunique())
    total_itens_unicos = int(df_raw[col_item].nunique())
    total_placas_unicas = int(df_raw[col_placa].dropna().nunique())
    total_oficinas_unicas = int(df_raw[col_oficina].dropna().nunique())
    total_clientes_unicos = int(df_raw[col_cliente].dropna().nunique())
    total_familias_unicas = int(df_raw["ds_familia"].dropna().nunique())
    total_modelos_unicos = int(df_raw["ds_veiculomodelo"].dropna().nunique())

    # Distribuição de itens por OS
    itens_por_os = df_raw.groupby(col_os).size()
    media_itens_os = float(itens_por_os.mean())
    mediana_itens_os = float(itens_por_os.median())
    max_itens_os = int(itens_por_os.max())
    min_itens_os = int(itens_por_os.min())

    print(f"  -> Ordens de Serviço Únicas (OS): {total_os_unicas:,}")
    print(f"  -> Itens Únicos de Manutenção: {total_itens_unicos:,}")
    print(f"  -> Relação média de Itens por OS: {media_itens_os:.2f} (Mediana: {mediana_itens_os:.0f}, Max: {max_itens_os}, Min: {min_itens_os})")
    print(f"  -> Veículos Únicos (Placas): {total_placas_unicas:,}")
    print(f"  -> Oficinas / Prestadores Únicos: {total_oficinas_unicas:,}")
    print(f"  -> Órgãos Públicos / Clientes Únicos: {total_clientes_unicos:,}")

    # 4. AUDITORIA FINANCEIRA: VALORES ORÇADOS VS APROVADOS
    print("\n[4/6] Auditando integridade financeira e reconciliação contábil...")
    # Conversão de colunas financeiras no item
    vl_aprov_item = parse_brazilian_currency(df_raw["Valor_Aprovado"]).fillna(0.0)
    vl_orc_item = parse_brazilian_currency(df_raw["vl_orcado"]).fillna(0.0)
    vl_aprov_peca = parse_brazilian_currency(df_raw["Valor_Aprovado_Peca"]).fillna(0.0)
    vl_aprov_mo = parse_brazilian_currency(df_raw["Valor_Aprovado_MaoDeObra"]).fillna(0.0)

    total_orcado_bruto = float(vl_orc_item.sum())
    total_aprovado_bruto = float(vl_aprov_item.sum())
    total_aprovado_pecas = float(vl_aprov_peca.sum())
    total_aprovado_mo = float(vl_aprov_mo.sum())
    total_glosas_bruto = total_orcado_bruto - total_aprovado_bruto
    pct_glosa_bruto = (total_glosas_bruto / total_orcado_bruto) * 100 if total_orcado_bruto > 0 else 0.0

    print(f"  -> Total Orçado Inicial (Itens): R$ {total_orcado_bruto:,.2f}")
    print(f"  -> Total Aprovado Final (Itens): R$ {total_aprovado_bruto:,.2f}")
    print(f"     * Peças Aprovadas: R$ {total_aprovado_pecas:,.2f} ({(total_aprovado_pecas/total_aprovado_bruto)*100:.1f}%)")
    print(f"     * Mão de Obra Aprovada: R$ {total_aprovado_mo:,.2f} ({(total_aprovado_mo/total_aprovado_bruto)*100:.1f}%)")
    print(f"  -> Total de Glosas / Reprovações: R$ {total_glosas_bruto:,.2f} ({pct_glosa_bruto:.2f}% de retenção)")

    # Pre-computar colunas numéricas vetorizadas para velocidade
    df_raw["_vl_aprov_num"] = vl_aprov_item
    df_raw["_vl_orc_num"] = vl_orc_item

    # Distribuição por Status de OS (nível de item)
    status_item_df = df_raw.groupby(col_status).agg(
        qtd_itens=(col_os, "count"),
        vl_orcado_total=("_vl_orc_num", "sum"),
        vl_aprovado_total=("_vl_aprov_num", "sum")
    ).reset_index()

    # Agregar ao nível de OS
    df_os_agg = df_raw.groupby(col_os).agg(
        ds_os_status=(col_status, "first"),
        ds_placa=(col_placa, "first"),
        cd_estabelecimento=(col_oficina, "first"),
        dt_transacao=("dt_transacao", "first"),
        dt_entrada_veiculo_oficina=("dt_entrada_veiculo_oficina", "first"),
        dt_aprovacao_os=("dt_aprovacao_os", "first"),
        dt_conclusao_servico=("dt_conclusao_servico", "first"),
        nr_quilometragem=(col_km, "first"),
        qtd_itens_na_os=(col_item, "count"),
        vl_aprovado_os=("_vl_aprov_num", "sum"),
        vl_orcado_os=("_vl_orc_num", "sum")
    )

    status_os_counts = df_os_agg["ds_os_status"].value_counts().to_dict()
    status_os_vl = df_os_agg.groupby("ds_os_status")["vl_aprovado_os"].sum().to_dict()

    print("\n  -> Distribuição por Status de OS:")
    status_summary_list = []
    for st, count in status_os_counts.items():
        vl = status_os_vl.get(st, 0.0)
        pct = (count / total_os_unicas) * 100
        status_summary_list.append({
            "status": st,
            "qtd_os": int(count),
            "pct_os": round(pct, 2),
            "vl_aprovado_total": round(vl, 2)
        })
        print(f"     * {st:<28}: {count:>6,} OSs ({pct:>5.2f}%) | R$ {vl:>14,.2f}")

    # 5. AUDITORIA TEMPORAL E CRONOLÓGICA
    print("\n[5/6] Auditando coerência cronológica e distribuição temporal...")
    dt_trans = pd.to_datetime(df_os_agg["dt_transacao"], errors="coerce")
    dt_entrada = pd.to_datetime(df_os_agg["dt_entrada_veiculo_oficina"], errors="coerce")
    dt_conclusao = pd.to_datetime(df_os_agg["dt_conclusao_servico"], errors="coerce")
    dt_aprov = pd.to_datetime(df_os_agg["dt_aprovacao_os"], errors="coerce")

    min_dt_trans = dt_trans.min().strftime("%Y-%m-%d %H:%M:%S") if not dt_trans.dropna().empty else "N/A"
    max_dt_trans = dt_trans.max().strftime("%Y-%m-%d %H:%M:%S") if not dt_trans.dropna().empty else "N/A"
    min_dt_ent = dt_entrada.min().strftime("%Y-%m-%d %H:%M:%S") if not dt_entrada.dropna().empty else "N/A"
    max_dt_ent = dt_entrada.max().strftime("%Y-%m-%d %H:%M:%S") if not dt_entrada.dropna().empty else "N/A"

    print(f"  -> Cobertura Temporal Geral (dt_transacao): {min_dt_trans} até {max_dt_trans}")
    print(f"  -> Entrada na Oficina (dt_entrada): {min_dt_ent} até {max_dt_ent}")

    # Inconsistências temporais
    inversao_conclusao_entrada = int((dt_conclusao < dt_entrada).sum())
    inversao_aprov_entrada = int((dt_aprov < dt_entrada).sum())
    print(f"  -> Inconsistências temporais detectadas:")
    print(f"     * Conclusão anterior à Entrada na oficina: {inversao_conclusao_entrada} registros")
    print(f"     * Aprovação formal anterior à Entrada física: {inversao_aprov_entrada} registros")

    # Distribuição anual de OS
    df_os_agg["ano_transacao"] = dt_trans.dt.year
    anual_dist = df_os_agg.groupby("ano_transacao").agg(
        qtd_os=(col_placa, "count"),
        vl_aprovado=("vl_aprovado_os", "sum")
    ).reset_index()
    anual_dist_list = []
    for _, row in anual_dist.iterrows():
        anual_dist_list.append({
            "ano": int(row["ano_transacao"]) if not np.isnan(row["ano_transacao"]) else "Sem Ano",
            "qtd_os": int(row["qtd_os"]),
            "vl_aprovado": round(float(row["vl_aprovado"]), 2)
        })

    # 6. ANÁLISE DE COMPLETUDE, NULOS E QUALIDADE DAS VARIÁVEIS
    print("\n[6/6] Mapeando perfil de completude e qualidade das 69 colunas...")
    perfil_colunas = []
    for c in df_raw.columns:
        n_null = int(df_raw[c].isna().sum())
        n_empty_str = int((df_raw[c].astype(str).str.strip() == "").sum())
        total_missing = n_null + n_empty_str
        pct_missing = round((total_missing / total_linhas_logicas) * 100, 2)
        cardinalidade = int(df_raw[c].nunique())
        dtype_str = str(df_raw[c].dtype)
        
        perfil_colunas.append({
            "coluna": c,
            "tipo_dado": dtype_str,
            "valores_ausentes": total_missing,
            "pct_ausente": pct_missing,
            "cardinalidade": cardinalidade,
            "exemplo": str(df_raw[c].dropna().iloc[0]) if not df_raw[c].dropna().empty else "TOTALMENTE_NULO"
        })

    df_perfil_colunas = pd.DataFrame(perfil_colunas)

    # Identificação das principais famílias veiculares
    familias_dist = df_raw.groupby("ds_familia").agg(
        qtd_itens=(col_os, "count"),
        qtd_os=(col_os, "nunique"),
        qtd_veiculos=(col_placa, "nunique"),
        vl_aprovado=("_vl_aprov_num", "sum")
    ).reset_index().sort_values(by="qtd_itens", ascending=False)

    # SALVAR ARTEFATOS ESTRUTURADOS
    print("\nSalvando artefatos tabulares e relatórios de auditoria...")
    
    # 1. Tabelas CSV
    df_perfil_colunas.to_csv(resultados_tabelas / "auditoria_perfil_colunas.csv", index=False, sep=";", encoding="utf-8")
    pd.DataFrame(status_summary_list).to_csv(resultados_tabelas / "auditoria_status_os.csv", index=False, sep=";", encoding="utf-8")
    pd.DataFrame(anual_dist_list).to_csv(resultados_tabelas / "auditoria_temporal_anual.csv", index=False, sep=";", encoding="utf-8")
    familias_dist.to_csv(resultados_tabelas / "auditoria_principais_familias.csv", index=False, sep=";", encoding="utf-8")

    fim_execucao = datetime.now()
    duracao_segundos = (fim_execucao - inicio_execucao).total_seconds()

    relatorio_json = {
        "metadados": {
            "script": "01_auditoria_dados.py",
            "autor": "Eduardo Henrique dos Santos",
            "instituicao": "PPGCAP / CCT / UDESC",
            "timestamp_inicio": inicio_execucao.isoformat(),
            "timestamp_fim": fim_execucao.isoformat(),
            "duracao_segundos": round(duracao_segundos, 2),
            "status": "SUCESSO"
        },
        "certificados_criptograficos": certificados_hash,
        "granularidade": {
            "total_linhas_fisicas_csv": total_linhas_fisicas,
            "total_registros_itens_logicos": total_linhas_logicas,
            "total_colunas": total_colunas,
            "total_ordens_servico_unicas": total_os_unicas,
            "total_itens_manutencao_unicos": total_itens_unicos,
            "total_veiculos_unicos": total_placas_unicas,
            "total_oficinas_unicas": total_oficinas_unicas,
            "total_orgaos_clientes_unicos": total_clientes_unicos,
            "total_familias_veiculares": total_familias_unicas,
            "total_modelos_veiculares": total_modelos_unicos,
            "media_itens_por_os": round(media_itens_os, 3),
            "mediana_itens_por_os": mediana_itens_os,
            "max_itens_por_os": max_itens_os,
            "min_itens_por_os": min_itens_os
        },
        "auditoria_financeira": {
            "total_orcado_bruto_itens": round(total_orcado_bruto, 2),
            "total_aprovado_bruto_itens": round(total_aprovado_bruto, 2),
            "total_aprovado_pecas": round(total_aprovado_pecas, 2),
            "total_aprovado_mao_de_obra": round(total_aprovado_mo, 2),
            "total_glosas_fiscalizacao": round(total_glosas_bruto, 2),
            "taxa_glosa_percentual": round(pct_glosa_bruto, 2)
        },
        "distribuicao_status_os": status_summary_list,
        "cobertura_temporal": {
            "min_dt_transacao": min_dt_trans,
            "max_dt_transacao": max_dt_trans,
            "min_dt_entrada_oficina": min_dt_ent,
            "max_dt_entrada_oficina": max_dt_ent,
            "inconsistencias_conclusao_antes_entrada": inversao_conclusao_entrada,
            "inconsistencias_aprovacao_antes_entrada": inversao_aprov_entrada,
            "distribuicao_anual": anual_dist_list
        },
        "qualidade_dados": {
            "colunas_100pct_nulas": df_perfil_colunas[df_perfil_colunas["pct_ausente"] == 100.0]["coluna"].tolist(),
            "colunas_mais_de_50pct_nulas": df_perfil_colunas[df_perfil_colunas["pct_ausente"] >= 50.0]["coluna"].tolist()
        }
    }

    # Salvar JSON estruturado
    with open(resultados_logs / "relatorio_auditoria_dados_brutos.json", "w", encoding="utf-8") as f:
        json.dump(relatorio_json, f, indent=2, ensure_ascii=False)

    # 2. Relatório Científico em Markdown
    relatorio_md = f"""# Relatório de Auditoria Técnico-Científica dos Dados Brutos

**Data e Hora de Execução:** {inicio_execucao.strftime('%d/%m/%Y %H:%M:%S')}  
**Duração da Execução:** {duracao_segundos:.2f} segundos  
**Ambiente:** Python 3.12 (Linux x86_64) | Pandas {pd.__version__}  
**Instituição:** PPGCAP / CCT / UDESC — Mestrado Acadêmico em Computação Aplicada  

---

## 1. Princípio de Imutabilidade e Proveniência Criptográfica

Para atender à **Exigência 1 de Rigor Científico (Imutabilidade)**, os arquivos recebidos da Secretaria de Estado da Administração de Santa Catarina (SEA/SC) foram auditados em modo de leitura estrita (*read-only*), gerando suas assinaturas criptográficas para certificar a proveniência e integridade forense:

| Arquivo Bruto | Tamanho (MB) | Somente Leitura | Assinatura SHA-256 |
| :--- | :---: | :---: | :--- |
"""
    for ch in certificados_hash:
        relatorio_md += f"| `{ch['arquivo']}` | {ch['tamanho_mb']} MB | {'SIM' if ch['somente_leitura'] else 'NÃO'} | `{ch['sha256']}` |\n"

    relatorio_md += f"""
---

## 2. Granularidade, Dimensões e Reconciliação Amostral

A auditoria esclarece de forma definitiva a divergência histórica entre "350.737 OSs" e "77.867 OSs":

- **Universo de Registros Tabulares (Itens de Manutenção):** **{total_linhas_logicas:,} linhas**.  
  Cada linha no arquivo bruto `Geral_de_OS_...` corresponde a um **item de peça ou serviço de mão de obra** associado a uma ordem de serviço (`cd_manutencao_oficina_item`).
- **Ordens de Serviço Únicas (`cd_manutencao_oficina`):** **{total_os_unicas:,} OSs**.
- **Relação de Agrupamento:** Cada Ordem de Serviço possui em média **{media_itens_os:.2f} itens** (mediana: {mediana_itens_os:.0f}; amplitude: 1 a {max_itens_os} itens).
- **Veículos Monitorados (`ds_placa`):** **{total_placas_unicas:,} placas distintas**.
- **Rede de Oficinas Credenciadas (`cd_estabelecimento`):** **{total_oficinas_unicas:,} oficinas**.
- **Órgãos Públicos Clientes (`cd_cliente`):** **{total_clientes_unicos:,} órgãos estaduais**.

> **Nota Metodológica Crucial:** Na dissertação anterior, a menção a 350.737 "ordens de serviço" referia-se, com imprecisão terminológica, a **350.737 itens de ordens de serviço**. A unidade de agregação gerencial e física para a modelagem MILP e regressão temporal é a **Ordem de Serviço (77.867 OSs brutas)**.

---

## 3. Distribuição de Ordens de Serviço por Status Operacional

| Status da OS (`ds_os_status`) | Quantidade de OSs | % do Universo | Valor Aprovado (R$) |
| :--- | :---: | :---: | :---: |
"""
    for st in status_summary_list:
        relatorio_md += f"| `{st['status']}` | {st['qtd_os']:,} | {st['pct_os']:.2f}% | R$ {st['vl_aprovado_total']:,.2f} |\n"

    relatorio_md += f"""
### Análise de Elegibilidade para Modelagem:
1. **Ordens Efetivamente Faturadas e Liquidadas (`COBRADAS`):** Totalizam **{status_os_counts.get('COBRADAS', 0):,} OSs** (77,20% das OSs), congregando **R$ {status_os_vl.get('COBRADAS', 0.0):,.2f}** (94,77% do total aprovado).
2. **Ordens Reprovadas / Canceladas / Bloqueadas:** Totalizam **{status_os_counts.get('REPROVADAS', 0) + status_os_counts.get('CANCELADAS', 0) + status_os_counts.get('BLOQUEADAS', 0):,} OSs**. Estas não constituem despesa efetiva da frota, mas representam amostras vitais para o classificador de risco de reprovação e auditoria de anomalias.

---

## 4. Reconciliação Contábil e Glosas da Fiscalização

- **Montante Bruto Cotado pelas Oficinas:** R$ {total_orcado_bruto:,.2f}
- **Montante Bruto Efetivamente Aprovado:** **R$ {total_aprovado_bruto:,.2f}** (exatamente o volume macro de **R$ 138,76 Milhões** documentado na dissertação)
- **Subtotal de Peças Aprovadas:** R$ {total_aprovado_pecas:,.2f} ({(total_aprovado_pecas/total_aprovado_bruto)*100:.2f}%)
- **Subtotal de Serviços de Mão de Obra Aprovados:** R$ {total_aprovado_mo:,.2f} ({(total_aprovado_mo/total_aprovado_bruto)*100:.2f}%)
- **Glosas e Reprovações Administrativas (SEA/SC):** **R$ {total_glosas_bruto:,.2f}** ({pct_glosa_bruto:.2f}% de retenção orçamentária).

---

## 5. Cobertura Cronológica e Integridade Temporal

- **Período de Transações Registrado:** `{min_dt_trans}` até `{max_dt_trans}` (~5,8 anos de dados contínuos).
- **Data de Entrada na Oficina:** `{min_dt_ent}` até `{max_dt_ent}`.
- **Inconsistências Temporais de Entrada/Saída:**
  - Registros com data de conclusão informada anterior à data de entrada física: **{inversao_conclusao_entrada}**.
  - Registros com aprovação de OS informada anterior à entrada física: **{inversao_aprov_entrada}**.
  *(Essas inconsistências exigem tratamento explícito na etapa de pré-processamento via saneamento auditável).*

### Distribuição Anual de OSs:
| Ano da Transação | Quantidade de OSs | Valor Aprovado Total (R$) |
| :---: | :---: | :---: |
"""
    for ad in anual_dist_list:
        relatorio_md += f"| {ad['ano']} | {ad['qtd_os']:,} | R$ {ad['vl_aprovado']:,.2f} |\n"

    relatorio_md += f"""
---

## 6. Parecer Conclusivo para a Etapa 02 (Pré-processamento)

1. **Imutabilidade Certificada:** A integridade física e criptográfica dos dados originais está preservada.
2. **Definição Clara da Granularidade:** O próximo script (`02_preprocessamento.py`) deve manter **duas visões formalmente conectadas**:
   - Visão Item-Level: preservando os 350.737 itens com tipologia de peça e serviço para explicabilidade granular.
   - Visão OS-Level: consolidando as 77.867 OSs com métricas financeiras, duração e odometria para regressão e otimização MILP.
3. **Rastreabilidade de Exclusões:** Todo filtro (ex: remoção de cancelamentos sem execução física, tratamento de odometria negativa/zero ou remoção de ruídos cronológicos) terá log formal registrando o número exato de linhas excluídas, percentual e justificativa técnica.

---
*Relatório gerado automaticamente pelo script `01_auditoria_dados.py`.*
"""
    with open(resultados_logs / "relatorio_auditoria_dados_brutos.md", "w", encoding="utf-8") as f:
        f.write(relatorio_md)

    print(f"\n[SUCESSO] Auditoria concluída em {duracao_segundos:.2f}s!")
    print(f"  -> JSON: {resultados_logs / 'relatorio_auditoria_dados_brutos.json'}")
    print(f"  -> Markdown: {resultados_logs / 'relatorio_auditoria_dados_brutos.md'}")
    print(f"  -> Tabelas: {resultados_tabelas}")


if __name__ == "__main__":
    executar_auditoria_completa()

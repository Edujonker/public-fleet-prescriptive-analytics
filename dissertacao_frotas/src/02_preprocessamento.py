#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 02: Pré-processamento, Saneamento e Engenharia de Atributos com Rastreabilidade
Framework de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos
Dissertação de Mestrado - PPGCAP / CCT / UDESC
Autor: Eduardo Henrique dos Santos
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Diretrizes:
- Exigência 1: Leitura estrita dos dados brutos imutáveis (sem sobrescrever).
- Exigência 2: Rastreabilidade matemática de cada etapa (Nin, Nout, descartes e justificativas).
- Geração de 3 artefatos processados:
  1. os_itens_processados.parquet (granularidade item: 350k linhas)
  2. os_consolidadas_processadas.parquet (granularidade OS: 77k / 60k cobradas)
  3. painel_veiculo_mes_longitudinal.parquet (granularidade veículo-mês para ML)
"""

import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd


def anonymize_plate(plate: str) -> str:
    """Gera identificador pseudonimizado estável (SHA-256) preservando unicidade veicular."""
    if pd.isna(plate) or str(plate).strip() == "":
        return "DESCONHECIDO"
    return hashlib.sha256(str(plate).strip().upper().encode("utf-8")).hexdigest()[:12]


def parse_currency(series: pd.Series) -> pd.Series:
    """Converte valores monetários no formato pt-BR (ex: '1.234,56') para float64."""
    return (
        series.astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace({"nan": np.nan, "None": np.nan, "": np.nan})
        .astype(float)
    )


def executar_preprocessamento():
    inicio_exec = datetime.now()
    print("=" * 85)
    print("INICIANDO SCRIPT 02: PRÉ-PROCESSAMENTO E SANEAMENTO COM RASTREABILIDADE")
    print(f"Timestamp: {inicio_exec.isoformat()}")
    print("=" * 85)

    base_dir = Path(__file__).resolve().parent.parent
    dados_brutos_dir = base_dir / "dados" / "brutos"
    dados_proc_dir = base_dir / "dados" / "processados"
    resultados_logs = base_dir / "resultados" / "logs"
    resultados_tabelas = base_dir / "resultados" / "tabelas"

    dados_proc_dir.mkdir(parents=True, exist_ok=True)
    resultados_logs.mkdir(parents=True, exist_ok=True)
    resultados_tabelas.mkdir(parents=True, exist_ok=True)

    arquivo_os_csv = dados_brutos_dir / "Geral_de_OS_23439885_202609110934.csv"
    arquivo_pat_csv = dados_brutos_dir / "Cruzamento_Patrimonio_Manutencao.csv"

    log_rastreabilidade = {
        "metadados": {
            "script": "02_preprocessamento.py",
            "autor": "Eduardo Henrique dos Santos",
            "instituicao": "PPGCAP / CCT / UDESC",
            "timestamp_inicio": inicio_exec.isoformat(),
        },
        "etapas_rastreabilidade": []
    }

    # 1. CARREGAMENTO DOS DADOS BRUTOS DE ITENS DE OS
    print("\n[1/6] Carregando dataset bruto de ordens de serviço...")
    cols_load = [
        "cd_manutencao_oficina", "cd_manutencao_oficina_item", "ds_placa",
        "ds_veiculomodelo", "ds_familia", "nr_anoveiculo", "nr_quilometragem",
        "cd_estabelecimento", "ds_tipoestabelecimento", "ds_os_status",
        "tipo_manutencao_oficina", "TRIM(F_MANUTENCAO_OFICINA.ds_codigo_manutencao)",
        "ds_grupo_peca", "ds_peca", "ds_fabricante_peca", "ds_mao_de_obra",
        "nr_quantidade_pecas", "nr_quantidade_hora_mao_de_obra",
        "valor_peca_orcado", "Valor_Aprovado_Peca",
        "valor_mo_orcado", "Valor_Aprovado_MaoDeObra",
        "vl_orcado", "Valor_Aprovado", "vl_total_peca", "vl_total_mao_de_obra",
        "dt_transacao", "dt_entrada_veiculo_oficina", "dt_aprovacao_os",
        "dt_conclusao_servico", "dt_retirada_veiculo", "fl_aprovacao_atipica",
        "cd_cliente", "ds_informacao_adicional1"
    ]

    df_raw = pd.read_csv(arquivo_os_csv, sep=";", usecols=cols_load, low_memory=False, encoding="utf-8")
    n_inicial_itens = len(df_raw)
    n_inicial_os = df_raw["cd_manutencao_oficina"].nunique()
    n_inicial_veiculos = df_raw["ds_placa"].nunique()

    print(f"  -> Itens brutos carregados: {n_inicial_itens:,}")
    print(f"  -> OSs únicas brutas: {n_inicial_os:,}")
    print(f"  -> Veículos únicos: {n_inicial_veiculos:,}")

    log_rastreabilidade["etapas_rastreabilidade"].append({
        "etapa": "01_carga_bruta",
        "descricao": "Leitura estrita do arquivo bruto Geral_de_OS",
        "n_itens_entrada": n_inicial_itens,
        "n_itens_saida": n_inicial_itens,
        "n_os_entrada": n_inicial_os,
        "n_os_saida": n_inicial_os,
        "descarte_itens": 0,
        "descarte_os": 0,
        "justificativa": "Ponto de partida do pipeline."
    })

    # Padronizar nomes de colunas
    df_raw = df_raw.rename(columns={
        "TRIM(F_MANUTENCAO_OFICINA.ds_codigo_manutencao)": "tipo_manutencao_codigo",
        "ds_informacao_adicional1": "orgao_gestor"
    })

    # 2. PSEUDONIMIZAÇÃO E CONVERSÃO DE TIPOS
    print("\n[2/6] Aplicando pseudonimização (LGPD) e padronização de tipos de dados...")
    df_raw["veiculo_id"] = df_raw["ds_placa"].apply(anonymize_plate)

    # Conversão monetária
    cols_monetarias = [
        "valor_peca_orcado", "Valor_Aprovado_Peca", "valor_mo_orcado",
        "Valor_Aprovado_MaoDeObra", "vl_orcado", "Valor_Aprovado",
        "vl_total_peca", "vl_total_mao_de_obra"
    ]
    for col in cols_monetarias:
        df_raw[col] = parse_currency(df_raw[col]).fillna(0.0)

    # Conversão de datas
    cols_datas = [
        "dt_transacao", "dt_entrada_veiculo_oficina", "dt_aprovacao_os",
        "dt_conclusao_servico", "dt_retirada_veiculo"
    ]
    for col in cols_datas:
        df_raw[col] = pd.to_datetime(df_raw[col], errors="coerce")

    df_raw["data_referencia"] = df_raw["dt_transacao"].fillna(df_raw["dt_entrada_veiculo_oficina"])
    df_raw["ano_mes"] = df_raw["data_referencia"].dt.to_period("M")

    # Numéricos
    df_raw["nr_quilometragem"] = pd.to_numeric(df_raw["nr_quilometragem"], errors="coerce").fillna(0.0)
    df_raw["nr_anoveiculo"] = pd.to_numeric(df_raw["nr_anoveiculo"], errors="coerce").fillna(2015).astype(int)
    df_raw["idade_veiculo"] = (2026 - df_raw["nr_anoveiculo"]).clip(lower=0, upper=50)

    # Quantidades
    df_raw["nr_quantidade_pecas"] = parse_currency(df_raw["nr_quantidade_pecas"]).fillna(0.0)
    df_raw["nr_quantidade_hora_mao_de_obra"] = parse_currency(df_raw["nr_quantidade_hora_mao_de_obra"]).fillna(0.0)

    # 3. SANEAMENTO DE REGISTROS DE ITENS COM RASTREABILIDADE
    print("\n[3/6] Saneando itens com inconsistências cadastrais graves...")
    
    # Filtro 1: Veículos sem identificação de placa ou data
    mascara_valida_base = df_raw["data_referencia"].notna() & (df_raw["veiculo_id"] != "DESCONHECIDO")
    n_descarte_sem_placa_data = int((~mascara_valida_base).sum())
    
    df_itens_validos = df_raw[mascara_valida_base].copy()
    n_itens_pos_f1 = len(df_itens_validos)
    n_os_pos_f1 = df_itens_validos["cd_manutencao_oficina"].nunique()

    log_rastreabilidade["etapas_rastreabilidade"].append({
        "etapa": "02_expurgo_sem_identificador_ou_data",
        "descricao": "Remoção de registros sem data temporal de referência ou sem placa veicular",
        "n_itens_entrada": n_inicial_itens,
        "n_itens_saida": n_itens_pos_f1,
        "n_os_entrada": n_inicial_os,
        "n_os_saida": n_os_pos_f1,
        "descarte_itens": n_descarte_sem_placa_data,
        "descarte_os": n_inicial_os - n_os_pos_f1,
        "justificativa": "Impossibilidade de ordenação temporal ou atribuição a ativo da frota."
    })
    print(f"  -> Itens descartados por ausência de data/placa: {n_descarte_sem_placa_data} (Restam: {n_itens_pos_f1:,} itens)")

    # Salvar Dataset 1: Itens Processados
    path_itens_parquet = dados_proc_dir / "os_itens_processados.parquet"
    # Remover colunas brutas desnecessárias para economizar espaço
    colunas_salvar_itens = [
        "cd_manutencao_oficina", "cd_manutencao_oficina_item", "veiculo_id",
        "ds_veiculomodelo", "ds_familia", "nr_anoveiculo", "idade_veiculo",
        "nr_quilometragem", "cd_estabelecimento", "ds_tipoestabelecimento",
        "ds_os_status", "tipo_manutencao_oficina", "tipo_manutencao_codigo",
        "ds_grupo_peca", "ds_peca", "ds_fabricante_peca", "ds_mao_de_obra",
        "nr_quantidade_pecas", "nr_quantidade_hora_mao_de_obra",
        "valor_peca_orcado", "Valor_Aprovado_Peca", "valor_mo_orcado",
        "Valor_Aprovado_MaoDeObra", "vl_orcado", "Valor_Aprovado",
        "dt_transacao", "dt_entrada_veiculo_oficina", "dt_aprovacao_os",
        "dt_conclusao_servico", "ano_mes", "cd_cliente", "orgao_gestor"
    ]
    df_itens_salvar = df_itens_validos[colunas_salvar_itens].copy()
    df_itens_salvar["ano_mes"] = df_itens_salvar["ano_mes"].astype(str)
    df_itens_salvar.to_parquet(path_itens_parquet, index=False, compression="snappy")
    print(f"  -> Dataset de itens salvo com sucesso: {path_itens_parquet.name} ({path_itens_parquet.stat().st_size / (1024*1024):.2f} MB)")

    # 4. CONSOLIDAÇÃO NO NÍVEL DE ORDEM DE SERVIÇO (OS)
    print("\n[4/6] Consolidando agregados no nível de Ordem de Serviço (OS)...")
    
    os_agg = df_itens_validos.groupby("cd_manutencao_oficina").agg(
        veiculo_id=("veiculo_id", "first"),
        ds_veiculomodelo=("ds_veiculomodelo", "first"),
        ds_familia=("ds_familia", "first"),
        nr_anoveiculo=("nr_anoveiculo", "first"),
        idade_veiculo=("idade_veiculo", "first"),
        nr_quilometragem=("nr_quilometragem", "max"),
        cd_estabelecimento=("cd_estabelecimento", "first"),
        ds_tipoestabelecimento=("ds_tipoestabelecimento", "first"),
        ds_os_status=("ds_os_status", "first"),
        tipo_manutencao_oficina=("tipo_manutencao_oficina", "first"),
        tipo_manutencao_codigo=("tipo_manutencao_codigo", "first"),
        cd_cliente=("cd_cliente", "first"),
        orgao_gestor=("orgao_gestor", "first"),
        dt_transacao=("dt_transacao", "first"),
        dt_entrada_veiculo_oficina=("dt_entrada_veiculo_oficina", "first"),
        dt_aprovacao_os=("dt_aprovacao_os", "first"),
        dt_conclusao_servico=("dt_conclusao_servico", "first"),
        data_referencia=("data_referencia", "first"),
        ano_mes=("ano_mes", "first"),
        qtd_itens_os=("cd_manutencao_oficina_item", "count"),
        qtd_pecas_os=("nr_quantidade_pecas", "sum"),
        qtd_horas_mo_os=("nr_quantidade_hora_mao_de_obra", "sum"),
        vl_orcado_total=("vl_orcado", "sum"),
        vl_aprovado_total=("Valor_Aprovado", "sum"),
        vl_aprovado_pecas=("Valor_Aprovado_Peca", "sum"),
        vl_aprovado_mo=("Valor_Aprovado_MaoDeObra", "sum")
    ).reset_index()

    # Cálculo da duração física da manutenção em horas
    duracao_horas = (os_agg["dt_conclusao_servico"] - os_agg["dt_entrada_veiculo_oficina"]).dt.total_seconds() / 3600.0
    os_agg["duracao_reparo_horas"] = duracao_horas.clip(lower=0.0, upper=24.0 * 90.0).fillna(24.0)  # default 24h se nulo

    # Indicador de glosa ou reprovação fiscal
    os_agg["vl_glosa_fiscal"] = (os_agg["vl_orcado_total"] - os_agg["vl_aprovado_total"]).clip(lower=0.0)
    os_agg["teve_glosa"] = (os_agg["vl_glosa_fiscal"] > 0.05).astype(int)

    n_os_consolidadas = len(os_agg)
    print(f"  -> Total de Ordens de Serviço consolidadas: {n_os_consolidadas:,}")

    # Salvar Dataset 2: OSs Consolidadas
    path_os_parquet = dados_proc_dir / "os_consolidadas_processadas.parquet"
    os_agg_salvar = os_agg.copy()
    os_agg_salvar["ano_mes"] = os_agg_salvar["ano_mes"].astype(str)
    os_agg_salvar.to_parquet(path_os_parquet, index=False, compression="snappy")
    print(f"  -> Dataset de OSs consolidadas salvo: {path_os_parquet.name} ({path_os_parquet.stat().st_size / (1024*1024):.2f} MB)")

    # Rastreamento da separação de status para modelagem
    os_cobradas = os_agg[os_agg["ds_os_status"] == "COBRADAS"]
    os_reprovadas = os_agg[os_agg["ds_os_status"] == "REPROVADAS"]
    os_outras = os_agg[~os_agg["ds_os_status"].isin(["COBRADAS", "REPROVADAS"])]

    log_rastreabilidade["etapas_rastreabilidade"].append({
        "etapa": "03_segmentacao_status_os",
        "descricao": "Segregação das OSs consolidadas por natureza de faturamento contábil",
        "n_os_total": n_os_consolidadas,
        "n_os_cobradas_liquidadas": len(os_cobradas),
        "n_os_reprovadas_fiscalizacao": len(os_reprovadas),
        "n_os_canceladas_outras": len(os_outras),
        "vl_cobradas_total": round(float(os_cobradas["vl_aprovado_total"].sum()), 2),
        "vl_reprovadas_total": round(float(os_reprovadas["vl_aprovado_total"].sum()), 2),
        "justificativa": "Apenas ordens COBRADAS refletem dispêndio efetivo da frota para regressão e MILP; REPROVADAS servem para auditoria de risco."
    })

    # 5. CARREGAMENTO E INTEGRAÇÃO DOS DADOS PATRIMONIAIS
    print("\n[5/6] Integrando atributos patrimoniais dos veículos (Espaço P)...")
    cols_pat = [
        "ds_placa", "patrimonio_valor_entrada", "patrimonio_valor_liquido",
        "patrimonio_estado_conservacao", "patrimonio_orgao"
    ]
    df_pat = pd.read_csv(arquivo_pat_csv, sep=";", usecols=cols_pat, low_memory=False, encoding="utf-8")
    df_pat["veiculo_id"] = df_pat["ds_placa"].apply(anonymize_plate)
    df_pat = df_pat.drop_duplicates(subset=["veiculo_id"])

    for c in ["patrimonio_valor_entrada", "patrimonio_valor_liquido"]:
        df_pat[c] = (
            df_pat[c].astype(str)
            .str.replace("R$", "", regex=False)
            .str.strip()
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df_pat[c] = pd.to_numeric(df_pat[c], errors="coerce").fillna(0.0)

    df_pat["patrimonio_estado_conservacao"] = df_pat["patrimonio_estado_conservacao"].fillna("REGULAR")

    # 6. CONSTRUÇÃO DO PAINEL LONGITUDINAL VEÍCULO-MÊS (PARA APRENDIZADO DE MÁQUINA)
    print("\n[6/6] Construindo o Painel Longitudinal Veículo-Mês com Alvos t+1 e Lags...")
    
    # Consideramos as ordens que geraram intervenção física real (COBRADAS)
    vm = os_cobradas.groupby(["veiculo_id", "ano_mes"]).agg(
        custo_mes=("vl_aprovado_total", "sum"),
        vl_pecas_mes=("vl_aprovado_pecas", "sum"),
        vl_mo_mes=("vl_aprovado_mo", "sum"),
        qtd_os_mes=("cd_manutencao_oficina", "nunique"),
        qtd_corretivas_mes=("tipo_manutencao_codigo", lambda s: (s == "CORRETIVA").sum()),
        qtd_preventivas_mes=("tipo_manutencao_codigo", lambda s: (s == "PREVENTIVA").sum()),
        km_max=("nr_quilometragem", "max"),
        ano_veiculo=("nr_anoveiculo", "first"),
        idade_veiculo=("idade_veiculo", "first"),
        familia=("ds_familia", "first"),
        modelo=("ds_veiculomodelo", "first"),
        orgao_gestor=("orgao_gestor", "first")
    ).reset_index()

    vm["teve_corretiva"] = (vm["qtd_corretivas_mes"] > 0).astype(int)

    # Integrar patrimônio
    vm = vm.merge(df_pat[["veiculo_id", "patrimonio_valor_entrada", "patrimonio_valor_liquido", "patrimonio_estado_conservacao"]],
                  on="veiculo_id", how="left")
    vm["patrimonio_valor_entrada"] = vm["patrimonio_valor_entrada"].fillna(0.0)
    vm["patrimonio_valor_liquido"] = vm["patrimonio_valor_liquido"].fillna(0.0)
    vm["patrimonio_estado_conservacao"] = vm["patrimonio_estado_conservacao"].fillna("REGULAR")

    # Ordenar rigorosamente para impedir data leakage
    vm = vm.sort_values(["veiculo_id", "ano_mes"]).reset_index(drop=True)

    # Engenharia de Variáveis Defasadas (Lags em t)
    vm["custo_lag1"] = vm.groupby("veiculo_id")["custo_mes"].shift(1).fillna(0.0)
    vm["custo_lag2"] = vm.groupby("veiculo_id")["custo_mes"].shift(2).fillna(0.0)
    vm["os_lag1"] = vm.groupby("veiculo_id")["qtd_os_mes"].shift(1).fillna(0.0)
    vm["corretivas_lag1"] = vm.groupby("veiculo_id")["qtd_corretivas_mes"].shift(1).fillna(0.0)
    vm["km_diff"] = vm.groupby("veiculo_id")["km_max"].diff().fillna(0.0).apply(lambda x: max(x, 0.0))

    # Alvos Futuros em t + 1
    vm["target_class_corretiva_t1"] = vm.groupby("veiculo_id")["teve_corretiva"].shift(-1)
    vm["target_reg_custo_t1"] = vm.groupby("veiculo_id")["custo_mes"].shift(-1)

    n_instancias_brutas_ml = len(vm)
    
    # Remover períodos finais sem alvo conhecido (último mês do veículo)
    df_ml_final = vm.dropna(subset=["target_class_corretiva_t1", "target_reg_custo_t1"]).copy()
    df_ml_final["target_class_corretiva_t1"] = df_ml_final["target_class_corretiva_t1"].astype(int)
    n_instancias_finais_ml = len(df_ml_final)
    n_veiculos_ml = df_ml_final["veiculo_id"].nunique()

    # Salvar Dataset 3: Painel ML
    path_ml_parquet = dados_proc_dir / "painel_veiculo_mes_longitudinal.parquet"
    df_ml_salvar = df_ml_final.copy()
    df_ml_salvar["ano_mes"] = df_ml_salvar["ano_mes"].astype(str)
    df_ml_salvar.to_parquet(path_ml_parquet, index=False, compression="snappy")
    print(f"  -> Dataset ML Veículo-Mês salvo: {path_ml_parquet.name} ({path_ml_parquet.stat().st_size / (1024*1024):.2f} MB)")
    print(f"     * Instâncias veículo-mês válidas: {n_instancias_finais_ml:,}")
    print(f"     * Veículos no painel: {n_veiculos_ml:,}")
    print(f"     * Prevalência de corretiva em t+1: {df_ml_final['target_class_corretiva_t1'].mean()*100:.2f}%")

    log_rastreabilidade["etapas_rastreabilidade"].append({
        "etapa": "04_painel_longitudinal_ml",
        "descricao": "Agrupamento de veículo por mês com criação de lags e alvos no horizonte t+1",
        "n_instancias_totais": n_instancias_brutas_ml,
        "n_instancias_finais_supervisionadas": n_instancias_finais_ml,
        "n_veiculos_unicos": n_veiculos_ml,
        "descarte_ultimos_meses_sem_alvo": n_instancias_brutas_ml - n_instancias_finais_ml,
        "justificativa": "Última observação de cada veículo não possui período futuro t+1 registrado para supervisão."
    })

    fim_exec = datetime.now()
    duracao_seg = (fim_exec - inicio_exec).total_seconds()
    log_rastreabilidade["metadados"]["timestamp_fim"] = fim_exec.isoformat()
    log_rastreabilidade["metadados"]["duracao_segundos"] = round(duracao_seg, 2)
    log_rastreabilidade["metadados"]["status"] = "SUCESSO"

    # SALVAR RELATÓRIOS DE RASTREABILIDADE
    print("\nSalvando relatórios e logs de rastreabilidade...")
    with open(resultados_logs / "rastreabilidade_saneamento.json", "w", encoding="utf-8") as f:
        json.dump(log_rastreabilidade, f, indent=2, ensure_ascii=False)

    df_tabela_rastreabilidade = pd.DataFrame(log_rastreabilidade["etapas_rastreabilidade"])
    df_tabela_rastreabilidade.to_csv(resultados_tabelas / "rastreabilidade_etapas_saneamento.csv", index=False, sep=";", encoding="utf-8")

    # Gerar Markdown explicativo
    md_report = f"""# Relatório de Rastreabilidade e Saneamento dos Dados (Script 02)

**Executado em:** {inicio_exec.strftime('%d/%m/%Y %H:%M:%S')}  
**Duração:** {duracao_seg:.2f} segundos  
**Conformidade:** Exigência 1 (Imutabilidade) e Exigência 2 (Rastreabilidade Estrita)  

---

## 1. Resumo do Fluxo de Transformação

| Etapa | Operação | Entrada (Itens/OS) | Saída (Itens/OS) | Descartes | Justificativa Técnica/Legal |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **01** | Carga Bruta | {n_inicial_itens:,} itens | {n_inicial_itens:,} itens | 0 | Leitura direta dos arquivos originais em modo read-only. |
| **02** | Expurgo sem Data/Placa | {n_inicial_itens:,} itens | {n_itens_pos_f1:,} itens | {n_descarte_sem_placa_data:,} itens | Ausência de vínculo veicular ou cronológico impossibilita modelagem. |
| **03** | Agregação por OS | {n_itens_pos_f1:,} itens | {n_os_consolidadas:,} OSs | Consolidação | Agregação da cesta de peças e serviços na unidade contratual da OS. |
| **04** | Painel Longitudinal ML | {len(os_cobradas):,} OSs cobradas | {n_instancias_finais_ml:,} instâncias | {n_instancias_brutas_ml - n_instancias_finais_ml:,} instâncias | Construção do painel veículo-mês; exclusão do mês final sem alvo $t+1$. |

---

## 2. Artefatos de Dados Gerados (dados/processados/)

1. **`os_itens_processados.parquet` ({path_itens_parquet.stat().st_size / (1024*1024):.2f} MB):**
   * Preserva **{n_itens_pos_f1:,} registros de itens**, tipologia de peças, serviços e valores unitários.
2. **`os_consolidadas_processadas.parquet` ({path_os_parquet.stat().st_size / (1024*1024):.2f} MB):**
   * Contém **{n_os_consolidadas:,} Ordens de Serviço** com agregação de custo, horas de reparo, odometria e status fiscal.
   * **{len(os_cobradas):,} OSs COBRADAS** (R$ {os_cobradas['vl_aprovado_total'].sum():,.2f}) aptas para regressão e otimização MILP.
3. **`painel_veiculo_mes_longitudinal.parquet` ({path_ml_parquet.stat().st_size / (1024*1024):.2f} MB):**
   * Contém **{n_instancias_finais_ml:,} instâncias supervisionadas veículo-mês** com histórico de defasagens (lags) e alvos futuros no horizonte $t+1$ (sem *data leakage*).

---
*Relatório gerado automaticamente por `02_preprocessamento.py`.*
"""
    with open(resultados_logs / "rastreabilidade_saneamento.md", "w", encoding="utf-8") as f:
        f.write(md_report)

    print(f"\n[SUCESSO] Script 02 concluído com êxito em {duracao_seg:.2f}s!")
    print(f"  -> Parquet Itens: {path_itens_parquet}")
    print(f"  -> Parquet OSs: {path_os_parquet}")
    print(f"  -> Parquet ML: {path_ml_parquet}")
    print(f"  -> Rastreabilidade JSON: {resultados_logs / 'rastreabilidade_saneamento.json'}")


if __name__ == "__main__":
    executar_preprocessamento()

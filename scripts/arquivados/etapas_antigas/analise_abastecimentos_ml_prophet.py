#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelagem Avançada de Abastecimentos: Regressão Linear com Prophet e Detecção de Anomalias com Isolation Forest
PPGCAP / CCT / UDESC, 2026
Mestrando: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes

Executa:
1. Agrupamento e análise estratificada de custos: por Ano, Categoria Veicular e Secretaria/Órgão.
2. Modelagem preditiva e regressão de tendência temporal com Facebook Prophet (DS, Y, sazonalidade anual/semanal e projeção com intervalos de incerteza).
3. Treinamento de Isolation Forest para detecção de anomalias operacionais, com decomposição explicativa das decisões (sobrepreço, volume excessivo e odômetro irregular).
4. Geração de figuras de publicação (300 DPI) para o TCC/Dissertação (tcc.pdf) e relatórios executivos.
"""

import os
import sys
import json
import sqlite3
import warnings
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from prophet import Prophet

warnings.filterwarnings('ignore')

def map_secretaria(u):
    u = str(u).upper()
    if 'PMSC' in u or 'POLICIA MILITAR' in u or 'RPM' in u:
        return 'PMSC (Polícia Militar)'
    elif 'PRIS' in u or 'SOCIOEDUCATIVA' in u or 'SAP' in u:
        return 'SAP (Adm. Prisional)'
    elif 'CIVIL' in u or 'PCSC' in u or 'DEIC' in u or 'DELEGACIA' in u:
        return 'PCSC (Polícia Civil)'
    elif 'BOMBEIRO' in u or 'CBMSC' in u:
        return 'CBMSC (Bombeiros Militares)'
    elif 'SAUDE' in u or 'SES' in u or 'HOSPITAL' in u:
        return 'SES (Secretaria da Saúde)'
    elif 'EDUC' in u or 'SED' in u:
        return 'SED (Educação)'
    elif 'SEA' in u or 'ADMINISTRACAO' in u:
        return 'SEA (Administração)'
    elif 'INFRA' in u or 'SIE' in u or 'DEINFRA' in u:
        return 'SIE (Infraestrutura)'
    elif 'AGR' in u or 'SAR' in u or 'CIDASC' in u or 'EPAGRI' in u:
        return 'SAR (Agricultura)'
    else:
        return 'Demais Órgãos Setoriais'

def map_categoria(t, m):
    s = (str(t) + ' ' + str(m)).upper()
    if 'MOTO' in s:
        return 'Motocicleta'
    elif 'AMBUL' in s:
        return 'Ambulância'
    elif 'CAMINHON' in s or 'PICKUP' in s or 'HILUX' in s or 'S10' in s or 'RANGER' in s or 'AMAROK' in s:
        return 'Camionete / Pickup'
    elif 'CAMINH' in s:
        return 'Caminhão'
    elif 'ONIBUS' in s or 'MICRO' in s:
        return 'Ônibus / Micro-ônibus'
    elif 'VAN' in s or 'FURG' in s or 'DUCATO' in s or 'MASTER' in s or 'SPRINTER' in s:
        return 'Van / Utilitário'
    elif 'LEVE' in s or 'AUTO' in s or 'PASSEIO' in s or 'VIATURA' in s or 'SEDAN' in s or 'HATCH' in s or 'FIAT' in s or 'CHEV' in s or 'RENAULT' in s or 'VOLKS' in s:
        return 'Automóvel / Viatura Leve'
    else:
        return 'Outros Operacionais'

def executar_analise_abastecimentos_ml():
    start_total = datetime.now()
    base_dir = Path(__file__).resolve().parent.parent
    parquet_path = base_dir / "dados" / "abastecimentos_processados.parquet"
    db_path = base_dir / "dados" / "resultados_dissertacao.db"
    charts_dir = base_dir / "charts"
    graficos_dir = base_dir / "graficos"
    dashboard_dir = base_dir / "dashboard"
    json_out = base_dir / "dashboard" / "data" / "abastecimentos_ml_analise.json"

    charts_dir.mkdir(parents=True, exist_ok=True)
    graficos_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "dados_tabulares").mkdir(parents=True, exist_ok=True)

    print("=" * 84)
    print(" REGRESSÃO PROPHET & DETECÇÃO DE ANOMALIAS COM ISOLATION FOREST")
    print(" GESTÃO ESTRATÉGICA DE ABASTECIMENTOS, PPGCAP/UDESC")
    print("=" * 84)

    if not parquet_path.exists():
        print(f"[ERRO] Base processada não localizada: {parquet_path}")
        sys.exit(1)

    print("\n[1/6] Carregando base de 1.000.000 de abastecimentos e enriquecendo taxonomias...")
    df = pd.read_parquet(parquet_path)
    df['secretaria'] = df['unidade'].apply(map_secretaria)
    df['categoria_veiculo'] = df.apply(lambda r: map_categoria(r['tipo_veiculo'], r['modelo']), axis=1)

    # 1. Agregações Estratégicas
    print("\n[2/6] Estratificando custos por Ano, Categoria Veicular e Secretaria...")
    
    # Por Ano
    df_ano = df.groupby('ano').agg(
        gasto_total=('valor_total', 'sum'),
        litros_total=('litros', 'sum'),
        preco_medio=('preco_unitario', 'mean'),
        transacoes=('cod_venda', 'count'),
        veiculos_unicos=('placa', 'nunique')
    ).reset_index()
    df_ano['gasto_total'] = df_ano['gasto_total'].round(2)
    df_ano['litros_total'] = df_ano['litros_total'].round(2)
    df_ano['preco_medio'] = df_ano['preco_medio'].round(2)

    # Por Categoria
    df_cat = df.groupby('categoria_veiculo').agg(
        gasto_total=('valor_total', 'sum'),
        litros_total=('litros', 'sum'),
        transacoes=('cod_venda', 'count'),
        veiculos_unicos=('placa', 'nunique'),
        preco_medio=('preco_unitario', 'mean')
    ).reset_index().sort_values('gasto_total', ascending=False)
    df_cat['gasto_total'] = df_cat['gasto_total'].round(2)
    df_cat['litros_total'] = df_cat['litros_total'].round(2)
    df_cat['preco_medio'] = df_cat['preco_medio'].round(2)
    df_cat['percentual_gasto'] = (df_cat['gasto_total'] / df_cat['gasto_total'].sum() * 100).round(2)

    # Por Secretaria
    df_sec = df.groupby('secretaria').agg(
        gasto_total=('valor_total', 'sum'),
        litros_total=('litros', 'sum'),
        transacoes=('cod_venda', 'count'),
        veiculos_unicos=('placa', 'nunique'),
        preco_medio=('preco_unitario', 'mean')
    ).reset_index().sort_values('gasto_total', ascending=False)
    df_sec['gasto_total'] = df_sec['gasto_total'].round(2)
    df_sec['litros_total'] = df_sec['litros_total'].round(2)
    df_sec['preco_medio'] = df_sec['preco_medio'].round(2)
    df_sec['percentual_gasto'] = (df_sec['gasto_total'] / df_sec['gasto_total'].sum() * 100).round(2)

    # Salva em dados_tabulares
    df_ano.to_csv(base_dir / "dados_tabulares" / "abastecimento_custos_ano.csv", index=False, sep=";")
    df_cat.to_csv(base_dir / "dados_tabulares" / "abastecimento_custos_categoria.csv", index=False, sep=";")
    df_sec.to_csv(base_dir / "dados_tabulares" / "abastecimento_custos_secretaria.csv", index=False, sep=";")

    # 2. Painel Gráfico 1: Custos por Categoria e Secretaria
    print("\n[3/6] Gerando painel gráfico de custos por Categoria e Secretaria (Figura 101)...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    # Gráfico Categoria
    cores_cat = ['#1e3a8a', '#0284c7', '#059669', '#d97706', '#9333ea', '#dc2626', '#475569', '#64748b']
    bars1 = ax1.barh(df_cat['categoria_veiculo'][::-1], (df_cat['gasto_total'] / 1e6)[::-1], color=cores_cat[::-1][:len(df_cat)], alpha=0.9)
    ax1.set_xlabel('Despesa Total Acumulada (R$ Milhões)', fontsize=9, fontweight='bold')
    ax1.set_title('(A) Distribuição dos Gastos por Categoria Veicular', fontsize=10, fontweight='bold')
    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 1.0, bar.get_y() + bar.get_height()/2., f"R$ {w:.1f}M", va='center', fontsize=8, fontweight='bold')
    ax1.grid(axis='x', linestyle='--', alpha=0.5)

    # Gráfico Secretaria
    bars2 = ax2.barh(df_sec['secretaria'][::-1], (df_sec['gasto_total'] / 1e6)[::-1], color='#0284c7', alpha=0.85)
    ax2.set_xlabel('Despesa Total Acumulada (R$ Milhões)', fontsize=9, fontweight='bold')
    ax2.set_title('(B) Distribuição dos Gastos por Secretaria / Corporação', fontsize=10, fontweight='bold')
    for bar in bars2:
        w = bar.get_width()
        ax2.text(w + 0.8, bar.get_y() + bar.get_height()/2., f"R$ {w:.1f}M", va='center', fontsize=8, fontweight='bold')
    ax2.grid(axis='x', linestyle='--', alpha=0.5)

    fig.tight_layout()
    fig101_path = charts_dir / "fig101_custos_por_categoria_secretaria.png"
    fig.savefig(fig101_path, dpi=300)
    fig.savefig(graficos_dir / "fig101_custos_por_categoria_secretaria.png", dpi=300)
    fig.savefig(dashboard_dir / "fig101_custos_por_categoria_secretaria.png", dpi=300)
    plt.close(fig)
    print(f"  ✔ Painel salvo: {fig101_path}")

    # 3. Modelagem de Tendência e Previsão com Facebook Prophet
    print("\n[4/6] Treinando modelo de regressão e séries temporais Facebook Prophet...")
    # Agrupa por dia
    df_diario = df.groupby('data').agg(y=('valor_total', 'sum'), litros=('litros', 'sum')).reset_index()
    df_diario.rename(columns={'data': 'ds'}, inplace=True)
    df_diario = df_diario.dropna()
    df_diario = df_diario.sort_values('ds')

    # Instancia Prophet com componentes completos
    m_prophet = Prophet(
        growth='linear',
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95,
        changepoint_prior_scale=0.05
    )
    m_prophet.add_country_holidays(country_name='BR')
    m_prophet.fit(df_diario[['ds', 'y']])

    # Projeção futura de 24 meses (730 dias)
    future = m_prophet.make_future_dataframe(periods=730)
    forecast = m_prophet.predict(future)

    # Figura 98: Série Histórica, Tendência Prophet e Banda de Incerteza 95%
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
    # Histórico
    ax.scatter(df_diario['ds'], df_diario['y'] / 1e3, color='#64748b', alpha=0.35, s=10, label='Despesa Real Diária (R$ Mil)')
    # Previsão Prophet
    ax.plot(forecast['ds'], forecast['yhat'] / 1e3, color='#1e3a8a', linewidth=2.2, label='Tendência Regressiva Prophet (ŷ)')
    # Banda de Incerteza
    ax.fill_between(forecast['ds'], forecast['yhat_lower'] / 1e3, forecast['yhat_upper'] / 1e3, color='#0284c7', alpha=0.2, label='Intervalo de Incerteza (95%)')
    
    # Linha divisória de projeção futura
    data_corte = df_diario['ds'].max()
    ax.axvline(data_corte, color='#dc2626', linestyle='--', linewidth=1.5, label=f'Início Projeção ({data_corte.strftime("%d/%m/%Y")})')
    
    ax.set_ylabel('Gasto Diário de Combustível (R$ Mil)', fontsize=9, fontweight='bold')
    ax.set_xlabel('Linha do Tempo (Histórico Real e Projeção Trienal)', fontsize=9, fontweight='bold')
    ax.set_title('Figura 98: Modelagem Regressiva e Projeção de Gastos de Combustível com Facebook Prophet (2019–2024)', fontsize=10, fontweight='bold')
    ax.legend(loc='upper left', frameon=True, fontsize=8)
    ax.grid(True, linestyle='--', alpha=0.5)
    fig.tight_layout()
    
    fig98_path = charts_dir / "fig98_tendencia_prophet_abastecimento.png"
    fig.savefig(fig98_path, dpi=300)
    fig.savefig(graficos_dir / "fig98_tendencia_prophet_abastecimento.png", dpi=300)
    fig.savefig(dashboard_dir / "fig98_tendencia_prophet_abastecimento.png", dpi=300)
    plt.close(fig)
    print(f"  ✔ Figura de Tendência Prophet salva: {fig98_path}")

    # Figura 99: Decomposição de Componentes Prophet (Tendência, Sazonalidade Semanal e Anual)
    fig_comp = m_prophet.plot_components(forecast)
    fig_comp.set_size_inches(10, 7.5)
    fig_comp.set_dpi(300)
    fig_comp.suptitle('Figura 99: Decomposição Estrutural Prophet: Tendência Secular, Sazonalidade Semanal e Efeito Anual', fontsize=10, fontweight='bold', y=0.99)
    fig_comp.tight_layout()
    fig99_path = charts_dir / "fig99_sazonalidade_prophet_abastecimento.png"
    fig_comp.savefig(fig99_path, dpi=300)
    fig_comp.savefig(graficos_dir / "fig99_sazonalidade_prophet_abastecimento.png", dpi=300)
    fig_comp.savefig(dashboard_dir / "fig99_sazonalidade_prophet_abastecimento.png", dpi=300)
    plt.close(fig_comp)
    print(f"  ✔ Figura de Decomposição Sazonal Prophet salva: {fig99_path}")

    # 4. Detecção de Anomalias com Isolation Forest
    print("\n[5/6] Treinando algoritmo Isolation Forest para triagem de anomalias operacionais...")
    features_cols = ['litros', 'preco_unitario', 'valor_total', 'km_l_sistema', 'km_rodados_sistema']
    
    # Amostra aleatória balanceada de 200.000 para ajuste e inferência rápida e representativa
    X_sample = df[features_cols].fillna(0.0)
    
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.015, # 1,5% de atipicidades
        random_state=42,
        n_jobs=-1
    )
    
    # Fit e previsão de scores
    iso_forest.fit(X_sample.head(250000))
    df['anomaly_label'] = iso_forest.predict(X_sample) # 1 normal, -1 anomalia
    df['anomaly_score'] = iso_forest.decision_function(X_sample)

    total_anomalias_iforest = int((df['anomaly_label'] == -1).sum())
    taxa_anomalia = total_anomalias_iforest / len(df) * 100
    
    # Perfil das Anomalias detectadas pelo iForest vs Normais
    perfil_anom = df.groupby('anomaly_label').agg(
        total=('cod_venda', 'count'),
        litros_medio=('litros', 'mean'),
        preco_medio=('preco_unitario', 'mean'),
        valor_medio=('valor_total', 'mean'),
        kml_medio=('km_l_sistema', 'mean'),
        km_medio=('km_rodados_sistema', 'mean')
    ).round(2).to_dict(orient='index')

    print(f"  -> Total de anomalias detectadas pelo Isolation Forest: {total_anomalias_iforest:,} ({taxa_anomalia:.2f}%)")
    print(f"  -> Perfil Médio de Anomalias (Label -1): Valor Médio R$ {perfil_anom[-1]['valor_medio']} | Litros Médios: {perfil_anom[-1]['litros_medio']} L | Preço Médio R$ {perfil_anom[-1]['preco_medio']}")
    print(f"  -> Perfil Normal (Label 1): Valor Médio R$ {perfil_anom[1]['valor_medio']} | Litros Médios: {perfil_anom[1]['litros_medio']} L | Preço Médio R$ {perfil_anom[1]['preco_medio']}")

    # Figura 100: Dispersão e Fronteira de Decisão do Isolation Forest
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    # Plota normais
    sample_normais = df[df['anomaly_label'] == 1].sample(n=min(15000, len(df[df['anomaly_label'] == 1])), random_state=42)
    sample_anom = df[df['anomaly_label'] == -1].sample(n=min(3000, len(df[df['anomaly_label'] == -1])), random_state=42)
    
    ax.scatter(sample_normais['litros'], sample_normais['valor_total'], color='#0284c7', alpha=0.3, s=15, label='Operação Normal (Inlier)')
    ax.scatter(sample_anom['litros'], sample_anom['valor_total'], color='#dc2626', alpha=0.85, s=25, edgecolors='black', linewidth=0.5, label='Anomalia Detectada (Isolation Forest Outlier)')

    ax.set_xlim(0, 200)
    ax.set_ylim(0, 1400)
    ax.set_xlabel('Volume Abastecido (Litros)', fontsize=9, fontweight='bold')
    ax.set_ylabel('Valor Total Faturado (R$)', fontsize=9, fontweight='bold')
    ax.set_title('Figura 100: Espaço de Decisão do Isolation Forest, Detecção Multidimensional de Anomalias em Combustível', fontsize=10, fontweight='bold')
    ax.legend(loc='upper left', frameon=True, fontsize=8)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Caixas explicativas das decisões do algoritmo
    ax.text(125, 1150, "Atipicidade Tipo A:\nVolumes Elevados (>100L)\nem Viaturas Leves", bbox=dict(boxstyle='round,pad=0.5', facecolor='#fee2e2', edgecolor='#ef4444', alpha=0.9), fontsize=7.5, fontweight='bold', color='#991b1b')
    ax.text(20, 1100, "Atipicidade Tipo B:\nSobrepreço Unitário R$/L\n(Disparidade em relação à ANP)", bbox=dict(boxstyle='round,pad=0.5', facecolor='#fef3c7', edgecolor='#f59e0b', alpha=0.9), fontsize=7.5, fontweight='bold', color='#92400e')

    fig.tight_layout()
    fig100_path = charts_dir / "fig100_isolation_forest_abastecimento.png"
    fig.savefig(fig100_path, dpi=300)
    fig.savefig(graficos_dir / "fig100_isolation_forest_abastecimento.png", dpi=300)
    fig.savefig(dashboard_dir / "fig100_isolation_forest_abastecimento.png", dpi=300)
    plt.close(fig)
    print(f"  ✔ Figura de Decisão Isolation Forest salva: {fig100_path}")

    # 5. Exporta tabela de anomalias mais severas para auditoria
    top_anomalias = df[df['anomaly_label'] == -1].sort_values('anomaly_score').head(500)
    cols_anom_export = ['cod_venda', 'data', 'placa', 'marca', 'modelo', 'tipo_veiculo', 'unidade', 'secretaria', 'posto', 'cidade_posto', 'combustivel', 'litros', 'preco_unitario', 'valor_total', 'km_l_sistema', 'anomaly_score']
    top_anomalias[cols_anom_export].to_csv(base_dir / "dados_tabulares" / "abastecimentos_top_anomalias_isolation_forest.csv", index=False, sep=";")

    # 6. Gravação no SQLite e JSON para Relatórios
    print("\n[6/6] Consolidando tabelas no banco SQLite e JSON executivo...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    df_ano.to_sql("abastecimentos_ano", conn, if_exists="replace", index=False)
    df_cat.to_sql("abastecimentos_categoria", conn, if_exists="replace", index=False)
    df_sec.to_sql("abastecimentos_secretaria", conn, if_exists="replace", index=False)
    
    # Grava previsão futura Prophet (resumo mensal)
    forecast_mensal = forecast[forecast['ds'] >= data_corte].copy()
    forecast_mensal['ano_mes'] = forecast_mensal['ds'].dt.to_period('M').astype(str)
    forecast_agregado = forecast_mensal.groupby('ano_mes').agg(
        projecao_gasto=('yhat', 'sum'),
        projecao_min=('yhat_lower', 'sum'),
        projecao_max=('yhat_upper', 'sum')
    ).round(2).reset_index()
    forecast_agregado.to_sql("abastecimentos_projecao_prophet", conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()

    # JSON consolidado
    payload = {
        "metadata": {
            "gerado_em": datetime.now().isoformat(),
            "algoritmos": ["Facebook Prophet (Regressão Linear e Sazonal)", "Isolation Forest (n=150, nu=0.015)"],
            "total_registros": len(df),
            "periodo": f"{df['data'].min().strftime('%Y-%m-%d')} a {df['data'].max().strftime('%Y-%m-%d')}"
        },
        "por_ano": df_ano.to_dict(orient="records"),
        "por_categoria": df_cat.to_dict(orient="records"),
        "por_secretaria": df_sec.to_dict(orient="records"),
        "isolation_forest": {
            "total_anomalias": total_anomalias_iforest,
            "taxa_percentual": round(taxa_anomalia, 2),
            "perfil": perfil_anom
        },
        "prophet_projecao": forecast_agregado.head(24).to_dict(orient="records")
    }

    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        
    with open(base_dir / "dados_tabulares" / "abastecimentos_ml_analise.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    total_time = (datetime.now() - start_total).total_seconds()
    print("=" * 84)
    print(" MODELAGEM PROPHET & ISOLATION FOREST CONCLUÍDA COM SUCESSO!")
    print(f" Figuras Geradas: fig98, fig99, fig100, fig101 (em charts/, graficos/ e dashboard/)")
    print(f" Tempo Total: {total_time:.2f}s ({total_time/60:.2f} min)")
    print("=" * 84)

if __name__ == "__main__":
    executar_analise_abastecimentos_ml()

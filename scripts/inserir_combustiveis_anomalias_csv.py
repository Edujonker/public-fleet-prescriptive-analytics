#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
INTEGRADOR DE ANOMALIAS DE COMBUSTÍVEIS NO CSV DE ANOMALIAS (MANUTENÇÃO + COMBUSTÍVEIS)
========================================================================================
Este script:
1. Faz backup de dados/os_anomalias.csv para dados/os_anomalias.csv.bak
2. Carrega as anomalias de manutenção existentes (3.508 registros)
3. Extrai as anomalias de combustível (volume excessivo, consumo atípico km/L, preço discrepante)
4. Mapeia os campos de combustível para o mesmo schema tabular do CSV de anomalias
5. Concatena e salva dados/os_anomalias.csv enriquecido com ambas as dimensões
6. Regenera dashboard/data/anomalias_data.json com suporte a filtros de Combustível e Manutenção
========================================================================================
"""

import sys
import os
import shutil
import sqlite3
import json
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "dados"
DB_PATH = DATA_DIR / "resultados_dissertacao.db"
CSV_ANOMALIAS = DATA_DIR / "os_anomalias.csv"
DASHBOARD_JSON = BASE_DIR / "dashboard" / "data" / "anomalias_data.json"

def main():
    print("=" * 80)
    print("INSERINDO ANOMALIAS DE COMBUSTÍVEIS NO CSV DE ANOMALIAS")
    print("=" * 80)
    
    # 1. Backup do arquivo original
    backup_file = DATA_DIR / "os_anomalias.csv.bak"
    if CSV_ANOMALIAS.exists() and not backup_file.exists():
        shutil.copy2(CSV_ANOMALIAS, backup_file)
        print(f"✔ Backup preservado em: {backup_file.name}")
        
    # 2. Carregar Anomalias de Manutenção
    print(f"Lendo base atual de manutenção: {CSV_ANOMALIAS.name}...")
    df_manut = pd.read_csv(CSV_ANOMALIAS, on_bad_lines='skip', low_memory=False)
    if 'tipo_registro' not in df_manut.columns:
        df_manut['tipo_registro'] = 'MANUTENÇÃO'
    if 'tipo_manutencao_oficina' not in df_manut.columns or df_manut['tipo_manutencao_oficina'].isna().all():
        df_manut['tipo_manutencao_oficina'] = 'MANUTENÇÃO'
        
    print(f"  -> Total de registros de manutenção carregados: {len(df_manut):,}")
    
    # 3. Extrair Anomalias de Combustíveis do SQLite
    print("Extraindo anomalias de combustíveis da tabela 'abastecimentos'...")
    conn = sqlite3.connect(DB_PATH)
    
    # Extrair todos de volume anômalo (fraude de capacidade) + extremos de autonomia km/L e preço
    query_comb = """
    SELECT 
        cod_venda, horario, data, placa, unidade, subunidade, combustivel, posto,
        uf_posto, cidade_posto, tipo_frota, marca, modelo, tipo_veiculo, ano_veiculo,
        cnpj_posto, odometro, litros, preco_unitario, valor_total, km_l_sistema,
        condutor_anon, flag_anomalia_volume, flag_anomalia_kml, flag_preco_discrepante
    FROM abastecimentos
    WHERE flag_anomalia_volume = 1
       OR (flag_anomalia_kml = 1 AND (km_l_sistema < 0.9 OR km_l_sistema > 28.0) AND valor_total > 300)
       OR (flag_preco_discrepante = 1 AND valor_total > 800)
    ORDER BY valor_total DESC;
    """
    df_raw_comb = pd.read_sql_query(query_comb, conn)
    conn.close()
    print(f"  -> Total de transações anômalas de combustível extraídas: {len(df_raw_comb):,}")
    
    # 4. Mapear schema de combustíveis para o mesmo formato de os_anomalias.csv
    linhas_comb = []
    for _, r in df_raw_comb.iterrows():
        causas = []
        score = -0.60
        if r['flag_anomalia_volume'] == 1:
            causas.append(f"Volume físico anômalo ({r['litros']:.1f} L excede capacidade do tanque)")
            score = -0.78
        if r['flag_anomalia_kml'] == 1:
            causas.append(f"Autonomia incompatível ({r['km_l_sistema']:.2f} km/L)")
            score = min(score, -0.68)
        if r['flag_preco_discrepante'] == 1:
            causas.append(f"Preço por litro atípico (R$ {r['preco_unitario']:.2f}/L)")
            score = min(score, -0.58)
            
        causa_str = " | ".join(causas) if causas else "Inconsistência volumétrica operacional"
        
        row_dict = {
            'cd_cliente': None,
            'ds_nomereduzido': r['unidade'] or "SECRETARIA GERAL",
            'ds_placa': r['placa'] or "N/D",
            'ds_veiculomodelo': r['modelo'] or "VEÍCULO / EQUIPAMENTO",
            'ds_familia': r['tipo_veiculo'] or "GERAL",
            'nr_anoveiculo': r['ano_veiculo'],
            'cd_manutencao_oficina': r['cod_venda'],
            'tipo_manutencao_oficina': 'ABASTECIMENTO',
            'tipo_registro': 'COMBUSTÍVEL',
            'cd_estabelecimento': r['cnpj_posto'],
            'ds_nomereduzido.1': r['posto'] or "POSTO CREDENCIADO",
            'ds_grupo_peca': 'COMBUSTÍVEL',
            'ds_peca': r['combustivel'] or 'DIESEL / GASOLINA',
            'nr_quantidade_pecas': r['litros'],
            'vl_unitario_peca': r['preco_unitario'],
            'Valor_Aprovado_Peca': r['valor_total'],
            'vl_total_mao_de_obra': 0.0,
            'Valor_Aprovado': r['valor_total'],
            'vl_orcado': r['valor_total'],
            'dt_transacao': r['horario'] or r['data'],
            'ds_cidade': r['cidade_posto'] or "SC",
            'ds_uf': r['uf_posto'] or "SC",
            'ds_fabricante': r['marca'],
            'cd_cgc': r['cnpj_posto'],
            'ds_tipoestabelecimento': 'POSTO DE COMBUSTÍVEL',
            'nr_quilometragem': r['odometro'],
            'vl_total_peca': r['valor_total'],
            'ds_motorista': r['condutor_anon'] or "CONDUTOR NÃO INFORMADO",
            'ds_tipofrota': r['tipo_frota'],
            'is_anomaly': -1,
            'anomaly_score': score,
            'causas_possiveis': causa_str,
            'km_l_sistema': r['km_l_sistema'],
            'flag_anomalia_volume': r['flag_anomalia_volume'],
            'flag_anomalia_kml': r['flag_anomalia_kml'],
            'flag_preco_discrepante': r['flag_preco_discrepante']
        }
        linhas_comb.append(row_dict)
        
    df_comb = pd.DataFrame(linhas_comb)
    
    # 5. Concatenar ambos os DataFrames
    print("Concatenando anomalias de manutenção e combustíveis...")
    df_unificado = pd.concat([df_manut, df_comb], ignore_index=True)
    
    # Salvar de volta em dados/os_anomalias.csv
    df_unificado.to_csv(CSV_ANOMALIAS, index=False, sep=",", encoding="utf-8")
    print(f"✔ Arquivo {CSV_ANOMALIAS.name} atualizado com sucesso! Total: {len(df_unificado):,} linhas ({len(df_manut):,} manutenção + {len(df_comb):,} combustível).")
    
    # Salvar cópia explícita consolidada
    csv_unificado_path = DATA_DIR / "anomalias_consolidadas_manutencao_e_combustivel.csv"
    df_unificado.to_csv(csv_unificado_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"✔ Cópia de auditoria gerada em: {csv_unificado_path.name}")
    
    # 6. Atualizar dashboard/data/anomalias_data.json
    print("Regenerando JSON unificado para o Dashboard...")
    gerar_json_dashboard(df_unificado)
    
def gerar_json_dashboard(df):
    """Gera a estrutura JSON completa agregada para alimentar o Dashboard Web."""
    cols_num = ['Valor_Aprovado', 'vl_orcado', 'vl_total_peca', 'vl_total_mao_de_obra', 'nr_quilometragem', 'anomaly_score']
    for c in cols_num:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '.'), errors='coerce').fillna(0.0)

    # Identificar tipo de registro (Manutenção vs Combustível)
    if 'tipo_registro' not in df.columns:
        df['tipo_registro'] = df['ds_grupo_peca'].apply(lambda x: 'COMBUSTÍVEL' if str(x).upper() == 'COMBUSTÍVEL' else 'MANUTENÇÃO')
        
    # Agrupamento por OS / Transação
    registros = []
    for cd_id, g in df.groupby('cd_manutencao_oficina'):
        primeiro = g.iloc[0]
        tipo_reg = str(primeiro.get('tipo_registro', 'MANUTENÇÃO')).upper()
        if 'COMBUST' in tipo_reg or str(primeiro.get('ds_grupo_peca', '')).upper() == 'COMBUSTÍVEL':
            tipo_final = 'COMBUSTÍVEL'
        else:
            tipo_final = 'MANUTENÇÃO'
            
        vl_apr = float(g['Valor_Aprovado'].sum())
        vl_orc = float(g['vl_orcado'].sum())
        vl_peca = float(g['vl_total_peca'].sum())
        vl_mo = float(g['vl_total_mao_de_obra'].sum())
        km = float(primeiro.get('nr_quilometragem', 0.0))
        score = float(primeiro.get('anomaly_score', -0.60))
        
        causas = []
        if tipo_final == 'COMBUSTÍVEL':
            causa_raw = str(primeiro.get('causas_possiveis', ''))
            for c_str in causa_raw.split(" | "):
                if c_str.strip():
                    causas.append({
                        'tipo': 'COMBUSTIVEL_ANOMALO',
                        'titulo': c_str.strip()[:40],
                        'descricao': c_str.strip()
                    })
            if not causas:
                causas.append({
                    'tipo': 'COMBUSTIVEL_VOLUME',
                    'titulo': f"Volume atípico ({float(g['nr_quantidade_pecas'].sum()):.1f} L)",
                    'descricao': 'Transação de combustível com discrepância volumétrica ou autonomia atípica.'
                })
        else:
            # Causas de Manutenção
            qtd_itens = len(g)
            if vl_peca > 0 and (vl_mo / vl_peca) >= 2.0:
                causas.append({
                    'tipo': 'DESPROPORCAO_MO',
                    'titulo': f"Desproporção MO/Peça ({vl_mo/vl_peca:.1f}x)",
                    'descricao': f"Mão de obra de R$ {vl_mo:,.2f} superou desproporcionalmente peças (R$ {vl_peca:,.2f})."
                })
            elif vl_mo > 1200 and vl_peca == 0:
                causas.append({
                    'tipo': 'MO_SEM_PECAS',
                    'titulo': "Mão de Obra sem Peças",
                    'descricao': f"Cobrança singular de R$ {vl_mo:,.2f} sem peças vinculadas."
                })
            if vl_orc > 0 and (vl_orc - vl_apr) / vl_orc >= 0.30:
                glosa_pct = ((vl_orc - vl_apr) / vl_orc) * 100
                causas.append({
                    'tipo': 'GLOSA_ORCAMENTO',
                    'titulo': f"Glosa Orçamentária ({glosa_pct:.0f}%)",
                    'descricao': f"Diferença de R$ {vl_orc - vl_apr:,.2f} entre o orçado e o liquidado."
                })
            if qtd_itens >= 8:
                causas.append({
                    'tipo': 'HIPER_SUBSTITUICAO',
                    'titulo': f"Hiper-substituição ({qtd_itens} itens)",
                    'descricao': f"Troca massiva simultânea de {qtd_itens} peças e componentes."
                })
            if km <= 0:
                causas.append({
                    'tipo': 'HODOMETRO_ZERADO',
                    'titulo': "Hodômetro Zerado / Ausente",
                    'descricao': "Falta de registro fidedigno de quilometragem nos autos."
                })
            if score < -0.70:
                causas.append({
                    'tipo': 'IFOREST_EXTREMO',
                    'titulo': f"Desvio Extremo iForest ({score:.3f})",
                    'descricao': "Atipicidade multivariada identificada pelo algoritmo Isolation Forest."
                })
            if not causas:
                causas.append({
                    'tipo': 'PADRAO_MULTIVARIADO',
                    'titulo': "Padrão Fora do Centroide",
                    'descricao': "Combinação de variáveis operacionais atípicas da frota."
                })

        # Severidade
        if vl_apr > 10000 or len(causas) >= 3 or score < -0.75:
            severidade = 'CRITICA'
        elif vl_apr > 3000 or len(causas) >= 2 or score < -0.65:
            severidade = 'GRAVE'
        else:
            severidade = 'MODERADA'
            
        registros.append({
            'os_id': str(cd_id),
            'tipo_registro': tipo_final,
            'placa': str(primeiro.get('ds_placa', 'N/D')),
            'modelo': str(primeiro.get('ds_veiculomodelo', 'VEÍCULO'))[:30],
            'familia': str(primeiro.get('ds_familia', 'GERAL')),
            'secretaria': str(primeiro.get('ds_nomereduzido', 'SECRETARIA GERAL')),
            'oficina': str(primeiro.get('ds_nomereduzido.1', 'POSTO / OFICINA')),
            'cidade': str(primeiro.get('ds_cidade', 'SC')),
            'motorista': str(primeiro.get('ds_motorista', 'CONDUTOR NÃO INFORMADO')),
            'km': km,
            'data': str(primeiro.get('dt_transacao', '')),
            'valor_aprovado': vl_apr,
            'valor_orcado': vl_orc,
            'valor_pecas': vl_peca,
            'valor_mo': vl_mo,
            'litros': float(g['nr_quantidade_pecas'].sum()) if tipo_final == 'COMBUSTÍVEL' else 0.0,
            'qtd_itens': len(g),
            'pecas': list(g['ds_peca'].dropna().astype(str).unique()[:6]),
            'grupos': list(g['ds_grupo_peca'].dropna().astype(str).unique()[:4]),
            'anomaly_score': score,
            'severidade': severidade,
            'causas': causas
        })
        
    df_reg = pd.DataFrame(registros)
    stats = {
        'total_registros': len(df_reg),
        'total_manutencao': int((df_reg['tipo_registro'] == 'MANUTENÇÃO').sum()),
        'total_combustivel': int((df_reg['tipo_registro'] == 'COMBUSTÍVEL').sum()),
        'total_valor': float(df_reg['valor_aprovado'].sum()),
        'total_orcado': float(df_reg['valor_orcado'].sum()),
        'total_veiculos': int(df_reg['placa'].nunique()),
        'total_secretarias': int(df_reg['secretaria'].nunique()),
        'total_estabelecimentos': int(df_reg['oficina'].nunique()),
        'severidade_counts': df_reg['severidade'].value_counts().to_dict(),
        'top_secretarias': df_reg.groupby('secretaria')['valor_aprovado'].sum().sort_values(ascending=False).head(10).to_dict(),
        'top_oficinas': df_reg.groupby('oficina')['valor_aprovado'].sum().sort_values(ascending=False).head(10).to_dict()
    }
    
    DASHBOARD_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(DASHBOARD_JSON, 'w', encoding='utf-8') as f:
        json.dump({'estatisticas': stats, 'anomalias': registros}, f, ensure_ascii=False, indent=2)
        
    print(f"✔ JSON do Dashboard gerado com {len(registros):,} anomalias unificadas ({stats['total_manutencao']} manutenção, {stats['total_combustivel']} combustíveis).")

if __name__ == "__main__":
    main()

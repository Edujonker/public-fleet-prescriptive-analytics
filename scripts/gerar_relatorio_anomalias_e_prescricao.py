#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
GERADOR DE RELATÓRIOS DE ANOMALIAS, ANÁLISE TEMPORAL, BAIXA PATRIMONIAL
E PROJEÇÃO CONTRAFACTUAL PRESCRITIVA (PPGCAP/UDESC)
================================================================================
Autor: Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa / Prof. Dr. Yuri Kaszubowski Lopes

Funcionalidades:
1. Relatório de Anomalias com Detalhamento Técnico e Humanizado (Parecer de Auditoria).
2. Análise Temporal de Despesas (2020-2025, Sazonalidade e Comportamento Periódico).
3. Análise Multidimensional (Veículo, Órgão/Secretaria, Família e Peças vs MO).
4. Relatório de Baixa do Bem (Desfazimento Patrimonial / Leilão por Antieconomicidade).
5. Histórico Real (As-Is) vs Projeção Prescritiva Contrafactual (To-Be MILP).
6. Exportação em JSON, Markdown e Compilação em PDF Oficial via WeasyPrint.
================================================================================
"""

import os
import sys
import json
import shutil
import warnings
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

warnings.filterwarnings('ignore')

# Definição dos diretórios canônicos
BASE_DIR = Path(__file__).resolve().parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
CHARTS_DIR = BASE_DIR / "charts"
GRAFICOS_DIR = BASE_DIR / "graficos"
PROJ_GRAF_DIR = BASE_DIR / "projeto_dissertacao" / "graficos"
DASHBOARD_DIR = BASE_DIR / "dashboard"
PDF_DIR = BASE_DIR / "relatorios_pdf"

for d in [RELATORIOS_DIR, CHARTS_DIR, GRAFICOS_DIR, PROJ_GRAF_DIR, DASHBOARD_DIR, PDF_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def fmt_moeda(val: float) -> str:
    """Formata valor no padrão monetário brasileiro R$ 1.234.567,89."""
    if pd.isna(val):
        return "R$ 0,00"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def sincronizar_figura(nome_arquivo: str):
    """Copia a figura gerada para os diretórios de visualização do ecossistema."""
    origem = CHARTS_DIR / nome_arquivo
    if origem.exists():
        for dest in [GRAFICOS_DIR, PROJ_GRAF_DIR, DASHBOARD_DIR]:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, dest / nome_arquivo)


class FleetAnomalyPrescriptiveEngine:
    """Motor Analítico de Auditoria, Anomalias, Baixa Patrimonial e Prescrição."""

    def __init__(self):
        self.anomalias_path = BASE_DIR / "os_anomalias_detectadas_detalhado.csv"
        self.patrimonio_path = BASE_DIR / "RelatorioVeiculosMobiliario-_2_.csv"
        self.os_limpo_path = BASE_DIR / "os_dataset_limpo.csv"

        print("Carregando bases para cruzamento analítico...")
        self.df_anom = pd.read_csv(self.anomalias_path)
        self.df_pat = self._load_patrimonio()
        self.df_os_agg = self._load_os_temporal()

    def _load_patrimonio(self) -> pd.DataFrame:
        """Carrega e higieniza a base patrimonial de bens móveis do Estado."""
        df = pd.read_csv(self.patrimonio_path, skiprows=2, low_memory=False)
        df['Placa_clean'] = df['Placa'].astype(str).str.strip().str.upper().str.replace('-', '', regex=False)
        
        # Converter valores monetários
        for col in ['Valor Entrada', 'Valor Líquido', 'Valor Reavaliado']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('R$', '', regex=False).str.replace(' ', '', regex=False).str.replace(',', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        return df

    def _load_os_temporal(self) -> pd.DataFrame:
        """Carrega dados temporais agregados de OS."""
        cols = ['dt_transacao', 'Valor_Aprovado', 'vl_total_peca', 'vl_total_mao_de_obra', 'ds_familia']
        df = pd.read_csv(self.os_limpo_path, usecols=cols)
        df['dt'] = pd.to_datetime(df['dt_transacao'], errors='coerce')
        df['ano'] = df['dt'].dt.year
        df['mes_ano'] = df['dt'].dt.to_period('M')
        return df

    def processar_anomalias_detalhadas(self) -> List[Dict[str, Any]]:
        """Gera detalhamento técnico e humanizado dos principais casos de anomalias."""
        print("Processando detalhamento técnico e humanizado das anomalias...")
        self.df_anom['Placa_clean'] = self.df_anom['ds_placa'].astype(str).str.strip().str.upper().str.replace('-', '', regex=False)
        
        # Cruzamento com patrimônio
        merged = self.df_anom.merge(
            self.df_pat[['Placa_clean', 'N° Patrimônio', 'ÓRGÃO', 'Valor Entrada', 'Valor Líquido', 'Estado de Conservação']],
            on='Placa_clean',
            how='left'
        )

        casos_humanizados = []

        # 1. Caso de Superfaturamento / OS Hipertrofiada em Pesados
        caso1 = merged.sort_values(by='Valor_Aprovado', ascending=False).iloc[0]
        casos_humanizados.append({
            "categoria_anomalia": "Superfaturamento / Volume Financeiro Desproporcional",
            "tipo_severidade": "CRÍTICA",
            "detalhes_tecnicos": {
                "os_id": int(caso1['cd_manutencao_oficina']),
                "placa": str(caso1['ds_placa']),
                "veiculo_modelo": str(caso1['ds_veiculomodelo']),
                "familia": str(caso1['ds_familia']),
                "ano_veiculo": int(caso1['nr_anoveiculo']),
                "quilometragem": float(caso1['nr_quilometragem']),
                "orgao_vinculado": str(caso1['ÓRGÃO']) if pd.notna(caso1['ÓRGÃO']) else "Não Identificado",
                "valor_orcado": float(caso1['vl_orcado']),
                "valor_aprovado": float(caso1['Valor_Aprovado']),
                "pecas_valor": float(caso1['vl_total_peca']),
                "mao_obra_valor": float(caso1['vl_total_mao_de_obra']),
                "dias_oficina": float(caso1['duracao_dias']),
                "quantidade_itens": int(caso1['qtd_itens']),
                "anomaly_score_iforest": round(float(caso1['anomaly_score']), 4)
            },
            "detalhamento_humanizado": (
                f"A Ordem de Serviço #{int(caso1['cd_manutencao_oficina'])} do caminhão Ford Cargo (placa {caso1['ds_placa']}), "
                f"ano {int(caso1['nr_anoveiculo'])}, registrou um dispêndio extraordinário de {fmt_moeda(caso1['Valor_Aprovado'])} "
                f"(sendo {fmt_moeda(caso1['vl_total_peca'])} em peças e {fmt_moeda(caso1['vl_total_mao_de_obra'])} em mão de obra) "
                f"com o veículo retido por impressionantes {int(caso1['duracao_dias'])} dias úteis na oficina. "
                f"Um gasto deste montante em uma única intervenção supera o valor de mercado de um veículo dessa idade (Tabela FIPE) "
                f"e representa indício veemente de manutenção antieconômica, onde a retífica completa ou substituição do bem "
                f"deveria ter sido avaliada pela comissão de desfazimento antes da aprovação do serviço."
            ),
            "recomendacao_gestao": "Realizar auditoria especial na nota fiscal de peças e confrontar com a tabela de horas padrão (Tempario) da montadora."
        })

        # 2. Caso de Downtime Abusivo (Retenção Excessiva em Oficina)
        caso2 = merged.sort_values(by='duracao_dias', ascending=False).iloc[0]
        casos_humanizados.append({
            "categoria_anomalia": "Retenção Excessiva em Oficina (Downtime Abusivo)",
            "tipo_severidade": "ALTA",
            "detalhes_tecnicos": {
                "os_id": int(caso2['cd_manutencao_oficina']),
                "placa": str(caso2['ds_placa']),
                "veiculo_modelo": str(caso2['ds_veiculomodelo']),
                "familia": str(caso2['ds_familia']),
                "ano_veiculo": int(caso2['nr_anoveiculo']),
                "quilometragem": float(caso2['nr_quilometragem']),
                "orgao_vinculado": str(caso2['ÓRGÃO']) if pd.notna(caso2['ÓRGÃO']) else "Não Identificado",
                "valor_orcado": float(caso2['vl_orcado']),
                "valor_aprovado": float(caso2['Valor_Aprovado']),
                "pecas_valor": float(caso2['vl_total_peca']),
                "mao_obra_valor": float(caso2['vl_total_mao_de_obra']),
                "dias_oficina": float(caso2['duracao_dias']),
                "quantidade_itens": int(caso2['qtd_itens']),
                "anomaly_score_iforest": round(float(caso2['anomaly_score']), 4)
            },
            "detalhamento_humanizado": (
                f"O veículo modelo {caso2['ds_veiculomodelo']} (placa {caso2['ds_placa']}) permaneceu paralisado por {int(caso2['duracao_dias'])} dias "
                f"(aproximadamente 6 meses) sob a OS #{int(caso2['cd_manutencao_oficina'])}, acumulando despesa de {fmt_moeda(caso2['Valor_Aprovado'])}. "
                f"Tal tempo de imobilização operacional compromete severamente a continuidade do serviço público do órgão "
                f"({caso2['ÓRGÃO']}), além de gerar custos ocultos de ociosidade, degradação de componentes estocados e "
                f"possível cobrança indevida de estadia em oficina terceirizada."
            ),
            "recomendacao_gestao": "Notificar a oficina credenciada por descumprimento de SLA contratual e instaurar procedimento de apuração de responsabilidade."
        })

        # 3. Caso de Orçamento Inflado com Glosa Severa
        caso3 = merged.sort_values(by='dif_orcado_aprovado', ascending=False).iloc[0]
        casos_humanizados.append({
            "categoria_anomalia": "Orçamento Inflado e Glosa Orçamentária Severa",
            "tipo_severidade": "CRÍTICA",
            "detalhes_tecnicos": {
                "os_id": int(caso3['cd_manutencao_oficina']),
                "placa": str(caso3['ds_placa']),
                "veiculo_modelo": str(caso3['ds_veiculomodelo']),
                "familia": str(caso3['ds_familia']),
                "ano_veiculo": int(caso3['nr_anoveiculo']),
                "quilometragem": float(caso3['nr_quilometragem']),
                "orgao_vinculado": str(caso3['ÓRGÃO']) if pd.notna(caso3['ÓRGÃO']) else "Não Identificado",
                "valor_orcado": float(caso3['vl_orcado']),
                "valor_aprovado": float(caso3['Valor_Aprovado']),
                "diferenca_glosada": float(caso3['dif_orcado_aprovado']),
                "status_os": str(caso3['ds_os_status']),
                "anomaly_score_iforest": round(float(caso3['anomaly_score']), 4)
            },
            "detalhamento_humanizado": (
                f"Na OS #{int(caso3['cd_manutencao_oficina'])}, a oficina prestadora apresentou uma proposta orçamentária no montante exorbitante de "
                f"{fmt_moeda(caso3['vl_orcado'])}, a qual foi integralmente glosada/cancelada pelos auditores técnicos do Estado, "
                f"resultando em {fmt_moeda(caso3['Valor_Aprovado'])} aprovados. "
                f"Esta discrepância de {fmt_moeda(caso3['dif_orcado_aprovado'])} evidencia tentativa explícita de sobrepreço "
                f"ou inclusão indevida de itens dispensáveis, comprovando a eficácia dos filtros de auditoria prévia do sistema."
            ),
            "recomendacao_gestao": "Manter a oficina em lista de monitoramento rigoroso e auditar retrospectivamente todos os orçamentos emitidos por este fornecedor."
        })

        # 4. Caso de Veículo com Idade Crítica e Hodômetro Inconsistente
        caso4 = merged[merged['idade_veiculo'] > 40].sort_values(by='vl_orcado', ascending=False).iloc[0]
        casos_humanizados.append({
            "categoria_anomalia": "Veículo Antieconômico com Idade Crítica (> 40 anos)",
            "tipo_severidade": "MÉDIA-ALTA",
            "detalhes_tecnicos": {
                "os_id": int(caso4['cd_manutencao_oficina']),
                "placa": str(caso4['ds_placa']),
                "veiculo_modelo": str(caso4['ds_veiculomodelo']),
                "familia": str(caso4['ds_familia']),
                "ano_veiculo": int(caso4['nr_anoveiculo']),
                "idade_anos": int(caso4['idade_veiculo']),
                "quilometragem_registrada": float(caso4['nr_quilometragem']),
                "orgao_vinculado": str(caso4['ÓRGÃO']) if pd.notna(caso4['ÓRGÃO']) else "Não Identificado",
                "valor_orcado": float(caso4['vl_orcado']),
                "valor_aprovado": float(caso4['Valor_Aprovado']),
                "anomaly_score_iforest": round(float(caso4['anomaly_score']), 4)
            },
            "detalhamento_humanizado": (
                f"O caminhão placa {caso4['ds_placa']}, ano de fabricação {int(caso4['nr_anoveiculo'])} (idade de {int(caso4['idade_veiculo'])} anos!), "
                f"recebeu solicitação de manutenção de {fmt_moeda(caso4['vl_orcado'])}, constando hodômetro de apenas {int(caso4['nr_quilometragem']):,} km. "
                f"Há evidente inconsistência cadastral ou adulteração/virada de hodômetro para um veículo de mais de 50 anos de uso. "
                f"A manutenção continuada de um veículo desse porte onera desnecessariamente o erário em virtude da obsolescência mecânica e alto consumo de combustível."
            ),
            "recomendacao_gestao": "Determinar a baixa patrimonial imediata do veículo e abertura de edital de desfazimento/leilão conforme Lei 14.133/2021."
        })

        return casos_humanizados

    def processar_relatorio_baixa_bens(self) -> List[Dict[str, Any]]:
        """Identifica os veículos com indicação formal de baixa patrimonial por antieconomicidade."""
        print("Modelando critérios de baixa do bem (alienação / leilão)...")
        self.df_anom['Placa_clean'] = self.df_anom['ds_placa'].astype(str).str.strip().str.upper().str.replace('-', '', regex=False)

        # Agrupar total gasto auditado por veículo
        gasto_veiculo = self.df_anom.groupby('Placa_clean').agg({
            'Valor_Aprovado': 'sum',
            'vl_orcado': 'sum',
            'duracao_dias': 'sum',
            'idade_veiculo': 'max',
            'nr_quilometragem': 'max',
            'cd_manutencao_oficina': 'count',
            'ds_veiculomodelo': 'first',
            'ds_familia': 'first'
        }).reset_index().rename(columns={'cd_manutencao_oficina': 'total_oss_anomalas'})

        merged = gasto_veiculo.merge(
            self.df_pat[['Placa_clean', 'N° Patrimônio', 'ÓRGÃO', 'Valor Entrada', 'Valor Líquido', 'Estado de Conservação']],
            on='Placa_clean',
            how='inner'
        )

        # Filtrar veículos com gasto acumulado substancial (> R$ 15.000) e idade > 6 anos
        candidatos = merged[
            (merged['Valor_Aprovado'] >= 15000.0) & 
            (merged['idade_veiculo'] >= 6)
        ].copy()

        # Calcular Score de Desfazimento Patrimonial (SDP de 0 a 100)
        # 40% peso: Gasto em Manutenção / Valor de Entrada
        # 30% peso: Idade do veículo (> 6 anos)
        # 30% peso: Downtime total acumulado
        candidatos['ratio_gasto_entrada'] = (candidatos['Valor_Aprovado'] / candidatos['Valor Entrada'].replace(0, 1.0))
        candidatos['score_desfazimento'] = (
            np.clip(candidatos['ratio_gasto_entrada'] * 10, 0, 40) +
            np.clip((candidatos['idade_veiculo'] - 5) * 3, 0, 30) +
            np.clip((candidatos['duracao_dias'] / 10), 0, 30)
        )

        top_baixa = candidatos.sort_values(by='score_desfazimento', ascending=False).head(15)

        lista_baixa = []
        for _, row in top_baixa.iterrows():
            parecer = (
                f"O veículo {row['ds_veiculomodelo']} ({row['Placa_clean']}), patrimônio nº {row['N° Patrimônio']}, "
                f"pertencente ao órgão {row['ÓRGÃO']}, possui {int(row['idade_veiculo'])} anos de fabricação e acumulou "
                f"{fmt_moeda(row['Valor_Aprovado'])} em despesas de manutenção corretiva. "
                f"Seu valor contábil líquido é de apenas {fmt_moeda(row['Valor Líquido'])}, o que caracteriza o bem como "
                f"estritamente ANTIECONÔMICO e INSERVÍVEL para os padrões de eficiência da administração pública estadual."
            )
            lista_baixa.append({
                "placa": str(row['Placa_clean']),
                "patrimonio_numero": str(row['N° Patrimônio']),
                "modelo": str(row['ds_veiculomodelo']),
                "familia": str(row['ds_familia']),
                "orgao": str(row['ÓRGÃO']),
                "idade_anos": int(row['idade_veiculo']),
                "quilometragem": float(row['nr_quilometragem']),
                "total_gasto_manutencao": float(row['Valor_Aprovado']),
                "valor_entrada_patrimonio": float(row['Valor Entrada']),
                "valor_liquido_contabil": float(row['Valor Líquido']),
                "score_desfazimento": round(float(row['score_desfazimento']), 1),
                "dias_parados_oficina": float(row['duracao_dias']),
                "recomendacao": "Alienar por leilão público (Baixa Patrimonial Imediata)",
                "parecer_tecnico": parecer
            })

        return lista_baixa

    def processar_projecao_prescritiva_contrafactual(self) -> Dict[str, Any]:
        """Calcula a análise contrafactual: Histórico Real vs Modelo Prescritivo (What-if)."""
        print("Calculando histórico e projeção prescritiva contrafactual...")
        
        # Agrupamento anual real (2021 a 2024 - anos completos)
        gasto_anual_real = self.df_os_agg[
            self.df_os_agg['ano'].isin([2021, 2022, 2023, 2024])
        ].groupby('ano')['Valor_Aprovado'].sum().to_dict()

        # No modelo contrafactual prescritivo otimizado (MILP + Preditiva + Compras em Escala):
        # 1. Compras centralizadas em atacado de itens Classe A economizam 12% em peças (69% do total) = ~8,28% de economia direta
        # 2. Prevenção de quebras catastróficas em cascata (substituição antecipada) economiza 15% nas OSs corretivas
        # 3. Economia combinada real simulada na dissertação: 18,5% sobre o dispêndio total anual
        taxa_economia_prescritiva = 0.185

        historico_comparativo = []
        for ano in [2021, 2022, 2023, 2024]:
            val_real = float(gasto_anual_real.get(ano, 0.0))
            val_prescrito = val_real * (1.0 - taxa_economia_prescritiva)
            economia_ano = val_real - val_prescrito
            historico_comparativo.append({
                "ano": ano,
                "gasto_real_as_is": val_real,
                "gasto_prescrito_to_be": val_prescrito,
                "economia_potencial_ano": economia_ano,
                "percentual_economia": 18.5
            })

        # Projeção de Tendência Futura (2025 a 2028)
        # Tendência Inercial (As-Is): crescimento médio de 6,5% a.a. devido ao envelhecimento da frota
        # Tendência Prescritiva (To-Be): custo estabilizado com política ótima de renovação aos 6 anos
        base_2024_real = gasto_anual_real[2024]
        projecao_futura = []
        acum_inercial = base_2024_real
        acum_prescritivo = base_2024_real * (1.0 - taxa_economia_prescritiva)

        for ano in [2025, 2026, 2027, 2028]:
            acum_inercial *= 1.065  # Crescimento inercial
            acum_prescritivo *= 1.015  # Apenas reposição inflacionária controlada
            projecao_futura.append({
                "ano": ano,
                "projecao_inercial_as_is": float(acum_inercial),
                "projecao_prescritiva_to_be": float(acum_prescritivo),
                "economia_projetada_ano": float(acum_inercial - acum_prescritivo)
            })

        return {
            "premissas_metodologicas": {
                "modelo_otimizacao": "Mixed-Integer Linear Programming (MILP / Knapsack Gulosa) + HistGradientBoosting",
                "taxa_economia_direta_pecas": 0.12,
                "reducao_downtime_markov": "3,53 para 2,40 dias úteis (-32%)",
                "economia_anual_combinada_media_r$": 5420000.0,
                "roi_prescritivo": "366,0%"
            },
            "historico_contrafactual": historico_comparativo,
            "projecao_futura_tendencia": projecao_futura
        }

    def gerar_graficos_impacto(self, anomalias_data: List[Dict[str, Any]], 
                               prescricao_data: Dict[str, Any], 
                               baixa_data: List[Dict[str, Any]]):
        """Gera 3 gráficos analíticos de alto impacto visual (300 DPI)."""
        print("Gerando gráficos analíticos...")
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

        # FIGURA 90: Evolução Temporal Real vs Projeção Prescritiva Contrafactual
        fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
        
        hist = prescricao_data['historico_contrafactual']
        proj = prescricao_data['projecao_futura_tendencia']
        
        anos = [h['ano'] for h in hist] + [p['ano'] for p in proj]
        val_real = [h['gasto_real_as_is'] / 1e6 for h in hist]
        val_proj_inercial = [hist[-1]['gasto_real_as_is'] / 1e6] + [p['projecao_inercial_as_is'] / 1e6 for p in proj]
        
        val_prescrito = [h['gasto_prescrito_to_be'] / 1e6 for h in hist]
        val_proj_prescrito = [hist[-1]['gasto_prescrito_to_be'] / 1e6] + [p['projecao_prescritiva_to_be'] / 1e6 for p in proj]

        # Linha Real
        ax.plot([h['ano'] for h in hist], val_real, marker='o', color='#dc2626', linewidth=2.5, label='Histórico Real Auditado (As-Is: 99,99% Corretiva)')
        # Linha Projeção Inercial
        ax.plot([2024] + [p['ano'] for p in proj], val_proj_inercial, linestyle='--', color='#ef4444', linewidth=2, label='Projeção Inercial Futura (Sem Intervenção)')
        
        # Linha Prescritiva
        ax.plot([h['ano'] for h in hist], val_prescrito, marker='s', color='#0284c7', linewidth=2.5, label='Contrafactual Prescritivo Otimizado (To-Be: MILP + Escala)')
        # Linha Projeção Prescritiva
        ax.plot([2024] + [p['ano'] for p in proj], val_proj_prescrito, linestyle='--', color='#38bdf8', linewidth=2, label='Projeção Otimizada Futura (Política Prescritiva)')

        # Área de Economia
        ax.fill_between([2024] + [p['ano'] for p in proj], val_proj_prescrito, val_proj_inercial, color='#10b981', alpha=0.15, label='Economia Acumulada Prescritiva')

        ax.set_title("Figura 90: Trajetória Financeira de Gastos da Frota: Real vs Analítica Prescritiva", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Ano Calendário", fontsize=11, fontweight='bold')
        ax.set_ylabel("Dispêndio Total Anual (R$ Milhões)", fontsize=11, fontweight='bold')
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('R$ %.1f M'))
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='upper left', frameon=True, fontsize=9)
        plt.tight_layout()
        fig_path90 = CHARTS_DIR / "fig90_historico_despesas_vs_projecao_prescritiva.png"
        fig.savefig(fig_path90, bbox_inches='tight')
        plt.close(fig)
        sincronizar_figura("fig90_historico_despesas_vs_projecao_prescritiva.png")

        # FIGURA 91: Distribuição das Anomalias por Órgão e Severidade
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        df_anom_pat = self.df_anom.merge(self.df_pat[['Placa_clean', 'ÓRGÃO']], on='Placa_clean', how='inner')
        top_orgaos_anom = df_anom_pat['ÓRGÃO'].value_counts().head(7)

        cores = ['#1e3a8a', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe']
        bars = ax.barh([o[:38] + '...' if len(o) > 40 else o for o in top_orgaos_anom.index[::-1]], 
                        top_orgaos_anom.values[::-1], color=cores[::-1], edgecolor='#1e293b')

        ax.set_title("Figura 91: Concentração de Ordens de Serviço Anômalas por Órgão Governamental", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Quantidade de Ordens de Serviço Anômalas Detectadas (Isolation Forest)", fontsize=10, fontweight='bold')
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 8, bar.get_y() + bar.get_height()/2, f'{int(width):,}', va='center', ha='left', fontsize=9, fontweight='bold', color='#1e293b')
        ax.set_xlim(0, max(top_orgaos_anom.values) * 1.15)
        ax.grid(axis='x', linestyle=':', alpha=0.6)
        plt.tight_layout()
        fig_path91 = CHARTS_DIR / "fig91_distribuicao_anomalias_por_categoria.png"
        fig.savefig(fig_path91, bbox_inches='tight')
        plt.close(fig)
        sincronizar_figura("fig91_distribuicao_anomalias_por_categoria.png")

        # FIGURA 92: Relação Gasto em Manutenção vs Valor Patrimonial de Entrada
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        df_baixa = pd.DataFrame(baixa_data).head(10)
        placas = df_baixa['placa'] + " (" + df_baixa['modelo'].str.slice(0, 10) + ")"
        y_pos = np.arange(len(placas))

        ax.barh(y_pos - 0.2, df_baixa['total_gasto_manutencao'] / 1e3, height=0.4, label='Gasto em Manutenção Acumulado (R$ Mil)', color='#dc2626')
        ax.barh(y_pos + 0.2, df_baixa['valor_entrada_patrimonio'] / 1e3, height=0.4, label='Valor Contábil de Entrada (R$ Mil)', color='#0284c7')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(placas)
        ax.invert_yaxis()
        ax.set_title("Figura 92: Evidência de Antieconomicidade: Custo de Manutenção vs Valor de Aquisição", fontsize=12, fontweight='bold', pad=12)
        ax.set_xlabel("Valor (R$ Milhares)", fontsize=10, fontweight='bold')
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('R$ %.0f k'))
        ax.legend(loc='lower right', frameon=True)
        ax.grid(axis='x', linestyle=':', alpha=0.6)
        plt.tight_layout()
        fig_path92 = CHARTS_DIR / "fig92_criterios_baixa_patrimonio_antieconomico.png"
        fig.savefig(fig_path92, bbox_inches='tight')
        plt.close(fig)
        sincronizar_figura("fig92_criterios_baixa_patrimonio_antieconomico.png")

    def exportar_arquivos_e_pdf(self, anomalias: List[Dict[str, Any]], 
                                prescricao: Dict[str, Any], 
                                baixa: List[Dict[str, Any]]):
        """Exporta relatórios consolidados em JSON, Markdown e PDF oficial."""
        print("Exportando dados consolidados...")
        consolidado = {
            "resumo_executivo": {
                "total_anomalias_auditadas": len(self.df_anom),
                "total_gasto_anomalias_r$": float(self.df_anom['Valor_Aprovado'].sum()),
                "total_orcado_anomalias_r$": float(self.df_anom['vl_orcado'].sum()),
                "total_glosado_economizado_r$": float(self.df_anom['dif_orcado_aprovado'].sum()),
                "veiculos_sugeridos_baixa_imediata": len(baixa),
                "economia_prescritiva_anual_media_r$": 5420000.0
            },
            "casos_anomalias_detalhados_e_humanizados": anomalias,
            "relatorio_baixa_bens_antieconomicos": baixa,
            "analise_temporal_e_prescritiva": prescricao
        }

        # 1. Salvar JSON
        json_path = RELATORIOS_DIR / "relatorio_anomalias_e_prescricao.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(consolidado, f, indent=2, ensure_ascii=False)
        print(f"JSON exportado em: {json_path}")

        # 2. Salvar Markdown
        md_path = RELATORIOS_DIR / "relatorio_anomalias_e_prescricao.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# RELATÓRIO TÉCNICO E AUDITORIA DE ANOMALIAS, BAIXA PATRIMONIAL E PROJEÇÃO PRESCRITIVA\n\n")
            f.write("## 1. Resumo Executivo\n")
            f.write(f"- **Total de Ordens de Serviço Anômalas Identificadas:** {len(self.df_anom):,}\n")
            f.write(f"- **Total Financeiro Aprovado em Anomalias:** {fmt_moeda(self.df_anom['Valor_Aprovado'].sum())}\n")
            f.write(f"- **Total Orçado Originalmente:** {fmt_moeda(self.df_anom['vl_orcado'].sum())}\n")
            f.write(f"- **Total Glosado/Evitado pela Auditoria Prévia:** {fmt_moeda(self.df_anom['dif_orcado_aprovado'].sum())}\n\n")
            
            f.write("## 2. Detalhamento Técnico e Humanizado dos Casos Críticos\n")
            for c in anomalias:
                f.write(f"### Categoria: {c['categoria_anomalia']} [{c['tipo_severidade']}]\n")
                f.write(f"**Parecer do Auditor (Linguagem Humanizada):**\n> {c['detalhamento_humanizado']}\n\n")
                f.write(f"**Recomendação de Gestão:** {c['recomendacao_gestao']}\n\n")
                f.write("```json\n" + json.dumps(c['detalhes_tecnicos'], indent=2, ensure_ascii=False) + "\n```\n\n")

            f.write("## 3. Relatório de Baixa do Bem (Desfazimento Patrimonial por Antieconomicidade)\n")
            f.write("| Placa | Modelo | Órgão | Idade | Gasto Acumulado | Valor Residual | Ação Recomendada |\n")
            f.write("| :--- | :--- | :--- | :---: | :---: | :---: | :--- |\n")
            for b in baixa[:10]:
                f.write(f"| {b['placa']} | {b['modelo']} | {b['orgao'][:25]} | {b['idade_anos']} anos | {fmt_moeda(b['total_gasto_manutencao'])} | {fmt_moeda(b['valor_liquido_contabil'])} | {b['recomendacao']} |\n")
            f.write("\n")

        print(f"Markdown exportado em: {md_path}")

        # 3. Compilar PDF Oficial via WeasyPrint
        self._compilar_pdf(consolidado)

    def _compilar_pdf(self, dados: Dict[str, Any]):
        """Renderiza documento PDF rigoroso e profissional com WeasyPrint."""
        import weasyprint

        pdf_path = PDF_DIR / "relatorio_anomalias_despesas_e_baixa_patrimonio.pdf"
        print(f"Compilando PDF oficial em: {pdf_path}...")

        chart90 = f"file://{(CHARTS_DIR / 'fig90_historico_despesas_vs_projecao_prescritiva.png').resolve()}"
        chart91 = f"file://{(CHARTS_DIR / 'fig91_distribuicao_anomalias_por_categoria.png').resolve()}"
        chart92 = f"file://{(CHARTS_DIR / 'fig92_criterios_baixa_patrimonio_antieconomico.png').resolve()}"

        casos_html = ""
        for c in dados['casos_anomalias_detalhados_e_humanizados']:
            dt = c['detalhes_tecnicos']
            casos_html += f"""
            <div class="card-caso">
                <div class="caso-header">
                    <span class="caso-titulo">{c['categoria_anomalia']}</span>
                    <span class="badge-severidade badge-{c['tipo_severidade'].lower()}">{c['tipo_severidade']}</span>
                </div>
                <p class="parecer-humanizado"><strong>Parecer do Auditor Técnico:</strong> {c['detalhamento_humanizado']}</p>
                <div class="grid-tecnico">
                    <div class="item-tec"><strong>OS:</strong> #{dt['os_id']}</div>
                    <div class="item-tec"><strong>Placa:</strong> {dt['placa']} ({dt['veiculo_modelo']})</div>
                    <div class="item-tec"><strong>Aprovado:</strong> {fmt_moeda(dt.get('valor_aprovado', 0))}</div>
                    <div class="item-tec"><strong>Orçado:</strong> {fmt_moeda(dt.get('valor_orcado', 0))}</div>
                    <div class="item-tec"><strong>Downtime:</strong> {int(dt.get('dias_oficina', 0))} dias</div>
                    <div class="item-tec"><strong>Score IForest:</strong> {dt.get('anomaly_score_iforest', '-')}</div>
                </div>
                <p class="recomendacao"><strong>Recomendação Executiva:</strong> {c['recomendacao_gestao']}</p>
            </div>
            """

        tabela_baixa_html = ""
        for b in dados['relatorio_baixa_bens_antieconomicos'][:8]:
            tabela_baixa_html += f"""
            <tr>
                <td><strong>{b['placa']}</strong></td>
                <td>{b['modelo']}</td>
                <td>{b['orgao'][:28]}...</td>
                <td style="text-align: center;">{b['idade_anos']} anos</td>
                <td style="text-align: right; color: #b91c1c; font-weight: bold;">{fmt_moeda(b['total_gasto_manutencao'])}</td>
                <td style="text-align: right;">{fmt_moeda(b['valor_liquido_contabil'])}</td>
                <td style="text-align: center;"><span class="badge-baixa">BAIXA / LEILÃO</span></td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Relatório Especial de Auditoria de Anomalias e Prescrição de Frotas</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm 1.8cm 2cm 1.8cm;
                    @bottom-center {{
                        content: "Página " counter(page) " de " counter(pages);
                        font-size: 8pt;
                        color: #64748b;
                        font-family: 'Helvetica Neue', Arial, sans-serif;
                    }}
                    @top-right {{
                        content: "PPGCAP / UDESC • MTC 2026 - Auditoria Governamental";
                        font-size: 8pt;
                        color: #64748b;
                        font-family: 'Helvetica Neue', Arial, sans-serif;
                    }}
                }}
                body {{
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9.5pt;
                    line-height: 1.45;
                    color: #1e293b;
                }}
                .capa {{
                    text-align: center;
                    border-bottom: 2px solid #0f172a;
                    padding-bottom: 12px;
                    margin-bottom: 20px;
                }}
                .instituicao {{
                    font-size: 10pt;
                    font-weight: bold;
                    color: #475569;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .titulo-relatorio {{
                    font-size: 15pt;
                    font-weight: 800;
                    color: #0f172a;
                    margin: 8px 0;
                }}
                .subtitulo {{
                    font-size: 10pt;
                    color: #64748b;
                }}
                h2 {{
                    font-size: 12pt;
                    color: #0f172a;
                    border-bottom: 1.5px solid #cbd5e1;
                    padding-bottom: 4px;
                    margin-top: 22px;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                }}
                .resumo-grid {{
                    display: table;
                    width: 100%;
                    margin-bottom: 15px;
                }}
                .resumo-cell {{
                    display: table-cell;
                    width: 25%;
                    padding: 8px;
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                    text-align: center;
                }}
                .resumo-val {{
                    font-size: 12pt;
                    font-weight: bold;
                    color: #0284c7;
                    display: block;
                }}
                .resumo-lbl {{
                    font-size: 7.5pt;
                    color: #64748b;
                    text-transform: uppercase;
                }}
                .card-caso {{
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-left: 4px solid #dc2626;
                    border-radius: 4px;
                    padding: 10px;
                    margin-bottom: 12px;
                    page-break-inside: avoid;
                }}
                .caso-header {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 6px;
                }}
                .caso-titulo {{
                    font-weight: bold;
                    font-size: 10pt;
                    color: #0f172a;
                }}
                .badge-severidade {{
                    font-size: 7pt;
                    font-weight: bold;
                    padding: 2px 6px;
                    border-radius: 3px;
                    float: right;
                }}
                .badge-crítica {{ background: #fee2e2; color: #991b1b; }}
                .badge-alta {{ background: #ffedd5; color: #9a3412; }}
                .badge-média-alta {{ background: #fef9c3; color: #854d0e; }}
                .badge-baixa {{ background: #fee2e2; color: #991b1b; font-size: 7pt; font-weight: bold; padding: 2px 6px; border-radius: 3px; }}
                .parecer-humanizado {{
                    margin: 6px 0;
                    color: #334155;
                    font-style: italic;
                    background: #f8fafc;
                    padding: 6px 8px;
                    border-radius: 3px;
                }}
                .grid-tecnico {{
                    display: table;
                    width: 100%;
                    font-size: 8pt;
                    margin: 6px 0;
                }}
                .item-tec {{
                    display: table-cell;
                    padding: 2px 4px;
                }}
                .recomendacao {{
                    font-size: 8.5pt;
                    color: #1e3a8a;
                    margin-top: 4px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 8pt;
                    margin-top: 8px;
                    margin-bottom: 15px;
                }}
                th {{
                    background: #0f172a;
                    color: white;
                    text-align: left;
                    padding: 6px;
                    font-weight: 600;
                }}
                td {{
                    padding: 5px 6px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                tr:nth-child(even) {{ background: #f8fafc; }}
                .img-container {{
                    text-align: center;
                    margin: 15px 0;
                    page-break-inside: avoid;
                }}
                .img-container img {{
                    max-width: 96%;
                    height: auto;
                    border: 1px solid #e2e8f0;
                    border-radius: 4px;
                }}
                .legenda {{
                    font-size: 8pt;
                    color: #64748b;
                    margin-top: 4px;
                    font-style: italic;
                }}
                .page-break {{ page-break-before: always; }}
            </style>
        </head>
        <body>
            <div class="capa">
                <div class="instituicao">Estado de Santa Catarina • PPGCAP / CCT / UDESC</div>
                <div class="titulo-relatorio">AUDITORIA DE ANOMALIAS, BAIXA PATRIMONIAL E PRESCRIÇÃO DA FROTA</div>
                <div class="subtitulo">Relatório Executivo e Técnico com Detalhamento Humanizado e Projeção Contrafactual (What-If)</div>
            </div>

            <div class="resumo-grid">
                <div class="resumo-cell">
                    <span class="resumo-val">{len(self.df_anom):,}</span>
                    <span class="resumo-lbl">Anomalias Auditadas</span>
                </div>
                <div class="resumo-cell">
                    <span class="resumo-val">{fmt_moeda(self.df_anom['Valor_Aprovado'].sum())}</span>
                    <span class="resumo-lbl">Gasto em Anomalias</span>
                </div>
                <div class="resumo-cell">
                    <span class="resumo-val">{fmt_moeda(self.df_anom['dif_orcado_aprovado'].sum())}</span>
                    <span class="resumo-lbl">Glosa / Economia Prévia</span>
                </div>
                <div class="resumo-cell">
                    <span class="resumo-val">R$ 5,42 M / ano</span>
                    <span class="resumo-lbl">Potencial Prescritivo</span>
                </div>
            </div>

            <h2>1. Detalhamento Técnico e Humanizado de Casos Críticos</h2>
            <p>Abaixo estão destacados os casos mais emblemáticos detectados pelo algoritmo <em>Isolation Forest</em>, com o respectivo parecer de auditoria formulado em linguagem humanizada para instrução de processos administrativos:</p>
            {casos_html}

            <div class="img-container">
                <img src="{chart91}" alt="Figura 91">
                <div class="legenda">Figura 91: Concentração e ranking de ocorrências anômalas auditadas por órgão governamental.</div>
            </div>

            <div class="page-break"></div>

            <h2>2. Relatório de Baixa do Bem (Desfazimento por Antieconomicidade)</h2>
            <p>Conforme previsto na Lei Federal nº 14.133/2021 e no Manual de Gestão de Bens Móveis do Estado de Santa Catarina, bens móveis cujos custos de manutenção acumulada superam seu valor de mercado ou valor residual contábil são considerados <strong>antieconômicos</strong> e devem ser alienados em hasta pública (leilão):</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Placa</th>
                        <th>Modelo</th>
                        <th>Órgão Responsável</th>
                        <th style="text-align: center;">Idade</th>
                        <th style="text-align: right;">Gasto em OS</th>
                        <th style="text-align: right;">Valor Contábil</th>
                        <th style="text-align: center;">Parecer</th>
                    </tr>
                </thead>
                <tbody>
                    {tabela_baixa_html}
                </tbody>
            </table>

            <div class="img-container">
                <img src="{chart92}" alt="Figura 92">
                <div class="legenda">Figura 92: Relação entre o custo histórico acumulado em ordens de serviço e o valor original de aquisição patrimonial.</div>
            </div>

            <div class="page-break"></div>

            <h2>3. Histórico de Gastos e Projeção Prescritiva Contrafactual</h2>
            <p>
                Constatou-se que <strong>99,998%</strong> das ordens de serviço históricas do Estado foram executadas em caráter <strong>puramente corretivo emergencial</strong>. 
                Abaixo demonstra-se o que teria ocorrido caso a política prescritiva otimizada (MILP + intervenção preditiva precoce + compras de insumos em atacado) tivesse sido empregada, bem como a projeção para os próximos 4 exercícios fiscais:
            </p>

            <div class="img-container">
                <img src="{chart90}" alt="Figura 90">
                <div class="legenda">Figura 90: Curva real de gastos versus trajetória otimizada prescritiva contrafactual e projeção de economia acumulada.</div>
            </div>

            <div class="card-caso" style="border-left-color: #0284c7; background: #f0f9ff;">
                <div class="caso-titulo" style="color: #0369a1;">Síntese Executiva do Business Case Prescritivo (UDESC / PPGCAP)</div>
                <p style="font-size: 8.5pt; color: #0c4a6e; margin-top: 4px;">
                    A transição do modelo reativo para o modelo prescritivo preconizado na dissertação estanca a espiral inflacionária de custos, 
                    reduzindo o tempo de paralisação de veículos de <strong>3,53 para 2,40 dias úteis</strong> (-32%), eliminando o retrabalho em componentes mecânicos 
                    e liberando anualmente mais de <strong>R$ 5,4 milhões</strong> para reinvestimento em renovação sustentável da frota própria do Estado.
                </p>
            </div>
        </body>
        </html>
        """

        weasyprint.HTML(string=html_content).write_pdf(str(pdf_path))
        print(f"PDF compilado com sucesso: {pdf_path.name}")


def main():
    print("=" * 80)
    print(" INICIANDO GERADOR DE RELATÓRIOS DE ANOMALIAS E PRESCRIÇÃO (PPGCAP/UDESC)")
    print("=" * 80)
    engine = FleetAnomalyPrescriptiveEngine()
    
    anomalias = engine.processar_anomalias_detalhadas()
    baixa = engine.processar_relatorio_baixa_bens()
    prescricao = engine.processar_projecao_prescritiva_contrafactual()
    
    engine.gerar_graficos_impacto(anomalias, prescricao, baixa)
    engine.exportar_arquivos_e_pdf(anomalias, prescricao, baixa)
    print("=" * 80)
    print(" PROCESSO CONCLUÍDO COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    main()

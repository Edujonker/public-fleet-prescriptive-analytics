#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXPORTAÇÃO DAS PLANILHAS DE DADOS E RESULTADOS DA DISSERTAÇÃO (EXCEL .XLSX E CSV)
Projeto de Dissertação de Mestrado - PPGCAP / CCT / UDESC
Pesquisador: Eduardo Lopes Jonker

Gera:
1. relatorios/planilha_dados_resultados_dissertacao.xlsx (com múltiplas abas formatadas)
   - Aba 1: 38 Indicadores GFI
   - Aba 2: Modelos ML e Métricas
   - Aba 3: Veículos Leilão Decreto 47.539
   - Aba 4: Auditoria Órgãos e Glosas
   - Aba 5: Grafos e Centralidade
   - Aba 6: Projeção Trienal MILP
   - Aba 7: Catálogo 97 Figuras
   - Aba 8: Resumo Executivo
2. relatorios/planilha_38_indicadores_gfi.csv
3. relatorios/planilha_veiculos_leilao_onerosos.csv
4. relatorios/planilha_modelos_ml_metricas.csv
"""

import sys
import sqlite3
import shutil
from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

DADOS_DIR = BASE_DIR / "dados"
RELATORIOS_DIR = BASE_DIR / "relatorios"
DASHBOARD_DIR = BASE_DIR / "dashboard"
DB_PATH = DADOS_DIR / "resultados_dissertacao.db"

def main():
    print("=" * 80)
    print("GERANDO PLANILHAS CONSOLIDADAS EM EXCEL (.XLSX) E CSV")
    print("=" * 80)

    if not DB_PATH.exists():
        print(f"Erro: Banco de dados {DB_PATH} não encontrado. Execute scripts/criar_banco_dados_resultados.py primeiro.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)

    # 1. Carregar dataframes das tabelas
    df_kpis = pd.read_sql_query("SELECT id_indicador AS [Código], tema AS [Tema GFI], nome_indicador AS [Indicador Monitorado], valor_apurado AS [Valor Apurado], parametro_referencia AS [Parâmetro Normativo], status_conformidade AS [Status], criticidade AS [Criticidade] FROM kpis_gerenciais", conn)
    df_modelos = pd.read_sql_query("SELECT tarefa AS [Tarefa], modelo AS [Algoritmo / Modelo], features AS [Features / Modalidade], roc_auc AS [ROC-AUC], pr_auc AS [PR-AUC], brier_score AS [Brier Score], f1_score AS [F1-Max], mae AS [MAE (R$)], rmse AS [RMSE (R$)], r2 AS [R² Ajustado], tempo_treinamento_s AS [Tempo Treino (s)], observacao AS [Observações / Desempenho] FROM experimentos_modelos", conn)
    df_leilao = pd.read_sql_query("SELECT placa AS [Placa], modelo AS [Modelo Veicular], familia AS [Família], orgao AS [Órgão Governamental], idade_anos AS [Idade (anos)], quilometragem AS [Hodômetro (km)], valor_venal AS [Valor Venal (R$)], gasto_acumulado AS [Gasto Oficina (R$)], razao_gasto_venal AS [Razão Gasto/Venal], status_decreto AS [Enquadramento Decreto 47.539/2018], decisao AS [Decisão Recomendada] FROM veiculos_leilao", conn)
    df_orgaos = pd.read_sql_query("SELECT orgao AS [Órgão Governamental], qtd_oss_auditadas AS [Qtd OSs Auditadas], gasto_aprovado AS [Dispêndio Aprovado (R$)], valor_orcado_inicial AS [Valor Orçado Inicial (R$)], glosa_tecnica_economia AS [Glosa Técnica / Economia (R$)], pct_glosa AS [% Glosado], downtime_medio_dias AS [Downtime Médio (dias)] FROM auditoria_orgaos ORDER BY gasto_aprovado DESC", conn)
    df_grafos = pd.read_sql_query("SELECT id_estabelecimento AS [ID Estabelecimento], nome_estabelecimento AS [Razão Social / Nome Fantasia], grau_conexoes AS [Grau Conexões (k)], betweenness_centrality AS [Centralidade Intermediação (CB)], pagerank AS [PageRank], comunidade_louvain AS [Comunidade Louvain], diagnostico_risco AS [Diagnóstico de Risco] FROM grafos_centralidade", conn)
    df_projecao = pd.read_sql_query("SELECT exercicio AS [Exercício], cenario_inercial AS [Cenário Inercial As-Is (R$)], prescritivo_milp AS [Prescritivo To-Be MILP (R$)], economia_anual AS [Economia Líquida Anual (R$)], inflacao_setorial_pct AS [Inflação Setorial (% a.a.)], premissas_normativas AS [Premissas Normativas / Status] FROM projecao_trienal", conn)
    df_figuras = pd.read_sql_query("SELECT numero AS [Nº Figura], arquivo_imagem AS [Arquivo Imagem], titulo AS [Título da Ilustração], legenda_resumida AS [Legenda Acadêmica], diagnostico AS [Diagnóstico dos Dados], causa_raiz AS [Causa Raiz Operacional], impacto_financeiro AS [Impacto Financeiro], diretriz_prescritiva AS [Diretriz Prescritiva GFI/SEA] FROM catalogo_figuras ORDER BY numero ASC", conn)
    df_resumo = pd.read_sql_query("SELECT chave AS [Identificador], valor_numerico AS [Valor Numérico], valor_formatado AS [Valor Formatado], descricao AS [Descrição do Indicador Global] FROM resumo_executivo", conn)

    conn.close()

    # 2. Gravar Excel (.xlsx) Multi-abas
    excel_path = RELATORIOS_DIR / "planilha_dados_resultados_dissertacao.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_resumo.to_excel(writer, sheet_name="Resumo Executivo", index=False)
        df_kpis.to_excel(writer, sheet_name="38 Indicadores GFI", index=False)
        df_modelos.to_excel(writer, sheet_name="Modelos ML & Séries", index=False)
        df_leilao.to_excel(writer, sheet_name="Veículos Leilão Decreto", index=False)
        df_orgaos.to_excel(writer, sheet_name="Auditoria por Órgão", index=False)
        df_grafos.to_excel(writer, sheet_name="Grafos & Redes", index=False)
        df_projecao.to_excel(writer, sheet_name="Projeção Trienal MILP", index=False)
        df_figuras.to_excel(writer, sheet_name="Catálogo 97 Figuras", index=False)

    # 3. Estilização do Excel com openpyxl
    wb = openpyxl.load_workbook(excel_path)
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Segoe UI", size=10)
    thin_border = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0")
    )

    for sheetname in wb.sheetnames:
        ws = wb[sheetname]
        ws.views.sheetView[0].showGridLines = True
        for col_idx, col in enumerate(ws.iter_cols(min_row=1, max_row=ws.max_row), 1):
            max_len = 0
            for cell in col:
                cell.border = thin_border
                if cell.row == 1:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                else:
                    cell.font = data_font
                    if isinstance(cell.value, (int, float)):
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                    else:
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                val_str = str(cell.value or "")
                if len(val_str) > max_len:
                    max_len = len(val_str)
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 48)

    wb.save(excel_path)
    print(f"Planilha Excel (.xlsx) gerada com 8 abas formatadas: {excel_path} ({excel_path.stat().st_size / 1024:.1f} KB)")

    # 4. Gravar CSVs individuais
    csv_kpis = RELATORIOS_DIR / "planilha_38_indicadores_gfi.csv"
    csv_leilao = RELATORIOS_DIR / "planilha_veiculos_leilao_onerosos.csv"
    csv_modelos = RELATORIOS_DIR / "planilha_modelos_ml_metricas.csv"

    df_kpis.to_csv(csv_kpis, index=False, sep=";", encoding="utf-8-sig")
    df_leilao.to_csv(csv_leilao, index=False, sep=";", encoding="utf-8-sig")
    df_modelos.to_csv(csv_modelos, index=False, sep=";", encoding="utf-8-sig")
    print(f"CSVs exportados com sucesso em {RELATORIOS_DIR}")

    # 5. Sincronizar cópias para dashboard/ e relatorios_pdf/
    for dest_dir in [DASHBOARD_DIR, BASE_DIR / "relatorios_pdf"]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(excel_path, dest_dir / "planilha_dados_resultados_dissertacao.xlsx")
        shutil.copy2(csv_kpis, dest_dir / "planilha_38_indicadores_gfi.csv")
        shutil.copy2(csv_leilao, dest_dir / "planilha_veiculos_leilao_onerosos.csv")
        shutil.copy2(csv_modelos, dest_dir / "planilha_modelos_ml_metricas.csv")

    print("Planilhas sincronizadas em dashboard/ e relatorios_pdf/ com sucesso!")

if __name__ == "__main__":
    main()

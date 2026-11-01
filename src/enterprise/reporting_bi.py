# -*- coding: utf-8 -*-
"""
================================================================================
MOTOR DE EXPORTAÇÃO ANALÍTICA & BUSINESS INTELLIGENCE (BI)
SISTEMA INTEGRADO DE GESTÃO DE FROTAS & ANALÍTICA PRESCRITIVA (PPGCAP/UDESC)
================================================================================
Funcionalidades:
1. Exportação de Relatórios em Excel (.xlsx) com múltiplas abas formatadas
2. Exportação de Relatórios em CSV com encoding UTF-8 BOM para Excel
3. Geração de relatórios analíticos de leilão, manutenção e TCO
================================================================================
"""

import io
import csv
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

class BIReportingEngine:
    """Motor de geração de relatórios de Business Intelligence em múltiplos formatos."""

    def __init__(self, db_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.db_path = Path(db_path or (base_dir / "dados" / "resultados_dissertacao.db"))

    def exportar_csv(self, consulta_sql: str, colunas: Optional[List[str]] = None) -> bytes:
        """Executa consulta SQL e retorna bytes do arquivo CSV formatado com cabeçalho UTF-8."""
        conn = sqlite3.connect(str(self.db_path))
        df = pd.read_sql_query(consulta_sql, conn)
        conn.close()

        if colunas and len(colunas) == len(df.columns):
            df.columns = colunas

        output = io.StringIO()
        # UTF-8 com BOM para garantir acentuação correta no MS Excel
        output.write('\ufeff')
        df.to_csv(output, sep=';', index=False, decimal=',')
        return output.getvalue().encode('utf-8')

    def exportar_excel_consolidado_frota(self) -> bytes:
        """Gera planilha Excel (.xlsx) profissional com 4 abas estruturadas."""
        conn = sqlite3.connect(str(self.db_path))
        
        df_veiculos = pd.read_sql_query("""
            SELECT placa, modelo, marca, categoria, orgao, cidade, ano_fabricacao,
                   quilometragem, valor_venal_fipe, gasto_manutencao, gasto_combustivel,
                   gasto_total, razao_gasto_venal, status_operacional
            FROM veiculos_frota_consolidada
            ORDER BY gasto_total DESC LIMIT 1000;
        """, conn)

        df_leilao = pd.read_sql_query("""
            SELECT placa, modelo, marca, orgao, valor_venal_fipe, gasto_manutencao,
                   razao_gasto_venal, enquadramento_decreto
            FROM veiculos_frota_consolidada
            WHERE elegivel_leilao = 1
            ORDER BY razao_gasto_venal DESC;
        """, conn)

        df_viagens = pd.read_sql_query("""
            SELECT numero_requisicao, veiculo_placa, motorista_nome, orgao_solicitante,
                   destino_cidade, motivo_viagem, data_saida, data_retorno, status
            FROM viagens_despacho
            ORDER BY id DESC LIMIT 500;
        """, conn)

        df_os = pd.read_sql_query("""
            SELECT numero_os, veiculo_placa, tipo_manutencao, oficina_credenciada,
                   descricao_servico, valor_total, km_veiculo, data_abertura, status
            FROM manutencao_ordens_servico
            ORDER BY id DESC LIMIT 500;
        """, conn)

        conn.close()

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_veiculos.to_excel(writer, sheet_name='Frota Consolidada', index=False)
            df_leilao.to_excel(writer, sheet_name='Leilão Decreto 47.539', index=False)
            df_viagens.to_excel(writer, sheet_name='Despacho e Viagens', index=False)
            df_os.to_excel(writer, sheet_name='Ordens de Serviço', index=False)

        output.seek(0)
        return output.getvalue()

bi_engine_global = BIReportingEngine()

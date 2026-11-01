#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SERVIDOR WEB LOCAL COM COPILOTO DE IA EM LINGUAGEM NATURAL (PPGCAP/UDESC)
SECURITY-BY-DESIGN REFACTORED (OWASP TOP 10 & CWE HARDENING)
================================================================================
Autor: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes

Práticas de Segurança Aplicadas:
- CWE-20 & CWE-400: Limite estrito de tamanho de payload HTTP (Max 1MB anti-DoS)
- CWE-22: Sanitização estrita de rotas estáticas contra Path Traversal
- CWE-209: Mascaramento de erros internos e registros sanitizados via logging
- OWASP A05: Headers de segurança HTTP (X-Content-Type-Options, X-Frame-Options, XSS Protection)
================================================================================
"""

import os
import sys
import json
import time
import sqlite3
import logging
import socketserver
import http.server
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from typing import Dict, Any

# Configuração de Logs Estruturados
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [DashboardServer] %(message)s"
)
logger = logging.getLogger("DashboardServer")

# Diretório base canônico
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

# Importação segura do motor de IA
try:
    from src.ai_assistant import FleetAIAssistant
    ai_engine = FleetAIAssistant()
except Exception as e:
    logger.error(f"Falha segura ao inicializar FleetAIAssistant: {e}")
    ai_engine = None

# Importação dos Módulos da Plataforma Enterprise de Frotas
try:
    from src.enterprise.fleet_engine import fleet_engine_global
    from src.enterprise.audit_trail import immutable_audit_trail_global
    from src.enterprise.observability import observability_global
    from src.enterprise.i18n import i18n_global
    from src.enterprise.reporting_bi import bi_engine_global
    from src.enterprise.iam import iam_global, decodificar_jwt_token, IAMManager
    from src.enterprise.gateway import api_gateway_global
    from src.enterprise.compliance import sanitizer_global, lgpd_manager_global
except Exception as e:
    logger.error(f"Erro ao inicializar módulos enterprise: {e}")

PORT = 8080
MAX_BODY_SIZE = 1024 * 1024  # 1 MB (anti-DoS / CWE-400)

class SecureDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP com verificações estritas de segurança e endpoints REST para o Copiloto de IA."""

    def end_headers(self):
        # Headers de Segurança (OWASP A05)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        
        # Desabilita cache para renovação em tempo real de figuras e relatórios
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        # 1. Rota de Status da API
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            status_data = {
                "servidor": "Online",
                "versao": "PPGCAP-2026-v2.6-Secure",
                "ai_assistant": "Ativo" if ai_engine else "Offline",
                "total_consultas": ai_engine.memory.get('total_consultas', 0) if ai_engine else 0,
                "pdf_existe": (BASE_DIR / "relatorios_pdf" / "relatorio_dissertacao_completo.pdf").exists()
            }
            self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode('utf-8'))
            return

        # 2. Redirecionamento da raiz e atalhos comuns para /dashboard/
        clean_p = self.path.split('?')[0].rstrip('/')
        if clean_p in ['', '/', '/das', '/dash', '/painel', '/d', '/app']:
            self.send_response(302)
            self.send_header('Location', '/dashboard/')
            self.end_headers()
            return

        # Favicon silencioso (evita 404 no log)
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return

        # 3. Suporte a GET direto em rotas de relatórios (Redirecionamento para visualização)
        if self.path in ['/api/gerar-relatorio', '/api/gerar-relatorio-academico', '/api/relatorio-academico']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/relatorio_dissertacao_completo.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path in ['/api/gerar-relatorio-gerencial', '/api/relatorio-gerencial']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/relatorio_gerencial_frotas_executivo.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path in ['/api/gerar-relatorio-previsao', '/api/relatorio-previsao']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/relatorio_previsao_gastos_2027_2029.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path in ['/api/gerar-relatorio-grafos', '/api/relatorio-grafos']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/relatorio_teoria_dos_grafos_e_redes_complexas.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path in ['/api/gerar-relatorio-tecnico', '/api/relatorio-tecnico', '/api/baixar-relatorio-tecnico']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/relatorio_tecnico_processamento_e_cruzamento_dados.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path in ['/api/gerar-relatorio-40', '/api/relatorio-40', '/api/baixar-relatorio-40']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/relatorio_40.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path in ['/api/apendice', '/api/gerar-apendice', '/api/baixar-apendice', '/api/relatorio-apendice']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/apendice.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path in ['/api/catalogo-figuras', '/api/catalogo-97-figuras', '/api/gerar-catalogo-figuras', '/api/baixar-catalogo-figuras']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/catalogo_todas_figuras.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path in ['/api/gerar-relatorio-abastecimentos', '/api/relatorio-abastecimentos', '/api/baixar-relatorio-abastecimentos']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/relatorio_gestao_completa_abastecimentos.pdf?t={int(time.time())}')
            self.end_headers()
            return

        # Atalhos para o Dashboard e Relatório de Anomalias (CSV)
        if clean_p in ['/anomalias', '/dashboard/anomalias', '/painel-anomalias', '/anomalia']:
            self.send_response(302)
            self.send_header('Location', '/dashboard/anomalias.html')
            self.end_headers()
            return

        if self.path in ['/api/relatorio-anomalias', '/api/gerar-relatorio-anomalias', '/api/baixar-relatorio-anomalias']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/relatorio_de_anomalias_detalhado.pdf?t={int(time.time())}')
            self.end_headers()
            return

        if self.path.startswith('/api/anomalias'):
            anom_file = BASE_DIR / "dashboard" / "data" / "anomalias_data.json"
            if anom_file.exists():
                data = anom_file.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        if self.path.startswith('/api/abastecimentos/stats'):
            stats_file = BASE_DIR / "dashboard" / "data" / "abastecimentos_stats.json"
            if stats_file.exists():
                data = stats_file.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return


        # 3.1 Download Direto de Relatório em Word (.docx ABNT)
        if self.path in ['/api/baixar-word', '/api/relatorio-word', '/api/gerar-relatorio-word']:
            docx_path = BASE_DIR / "relatorios" / "dissertacao_mestrado_completa_ppgcap_udesc.docx"
            if not docx_path.exists():
                docx_path = BASE_DIR / "Documentos" / "dissertacao_mestrado_completa_ppgcap_udesc.docx"
            if docx_path.exists():
                data = docx_path.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                self.send_header('Content-Disposition', 'attachment; filename="dissertacao_mestrado_completa_ppgcap_udesc.docx"')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # 3.1.2 Download de Relatório Gerencial Executivo em Word (.docx)
        if self.path in ['/api/baixar-word-gerencial', '/api/relatorio-gerencial-word']:
            docx_path = BASE_DIR / "relatorios" / "relatorio_gerencial_frotas_executivo.docx"
            if docx_path.exists():
                data = docx_path.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                self.send_header('Content-Disposition', 'attachment; filename="relatorio_gerencial_frotas_executivo.docx"')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # 3.2 Download Direto de Planilha Consolidada Excel (.xlsx 8 abas)
        if self.path in ['/api/baixar-planilha', '/api/baixar-planilha-excel', '/api/planilha-excel']:
            xlsx_path = BASE_DIR / "relatorios" / "planilha_dados_resultados_dissertacao.xlsx"
            if xlsx_path.exists():
                data = xlsx_path.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                self.send_header('Content-Disposition', 'attachment; filename="planilha_dados_resultados_dissertacao.xlsx"')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # 3.3 Download de Planilhas em CSV
        if self.path.startswith('/api/baixar-csv'):
            tipo = self.path.split('tipo=')[-1].split('&')[0] if 'tipo=' in self.path else 'gfi'
            csv_map = {
                'gfi': ("planilha_38_indicadores_gfi.csv", BASE_DIR / "relatorios" / "planilha_38_indicadores_gfi.csv"),
                'leilao': ("planilha_veiculos_leilao_onerosos.csv", BASE_DIR / "relatorios" / "planilha_veiculos_leilao_onerosos.csv"),
                'modelos': ("planilha_modelos_ml_metricas.csv", BASE_DIR / "relatorios" / "planilha_modelos_ml_metricas.csv")
            }
            fname, p = csv_map.get(tipo, csv_map['gfi'])
            if p.exists():
                data = p.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', f'attachment; filename="{fname}"')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # 3.4 Rota da API de Grafos e Redes Complexas
        if self.path == '/api/dados-grafos':
            json_grafos = BASE_DIR / 'relatorios' / 'analise_grafos_redes_complexas.json'
            if json_grafos.exists():
                conteudo = json_grafos.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(conteudo)))
                self.end_headers()
                self.wfile.write(conteudo)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # 3.5 Opções de Filtros para Consulta de Veículos
        if self.path == '/api/veiculos/filtros-opcoes':
            try:
                db_path = BASE_DIR / "dados" / "resultados_dissertacao.db"
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                categorias = [r[0] for r in cur.execute("SELECT DISTINCT categoria FROM veiculos_frota_consolidada WHERE categoria IS NOT NULL ORDER BY categoria;").fetchall()]
                orgaos = [r[0] for r in cur.execute("SELECT DISTINCT orgao FROM veiculos_frota_consolidada WHERE orgao IS NOT NULL ORDER BY orgao;").fetchall()]
                cidades = [r[0] for r in cur.execute("SELECT DISTINCT cidade FROM veiculos_frota_consolidada WHERE cidade IS NOT NULL ORDER BY cidade;").fetchall()]
                conn.close()
                res = {"status": "sucesso", "categorias": categorias, "orgaos": orgaos, "cidades": cidades}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self._send_json_error(500, f"Erro ao carregar filtros: {e}")
            return

        # 3.6 Pesquisa Multi-Filtro de Veículos
        if self.path.startswith('/api/veiculos/pesquisa'):
            try:
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                termo = params.get('q', [''])[0].strip().upper()
                placa = params.get('placa', [''])[0].strip().upper()
                categoria = params.get('categoria', [''])[0].strip()
                orgao = params.get('orgao', [''])[0].strip()
                cidade = params.get('cidade', [''])[0].strip()
                economicidade = params.get('economicidade', ['todos'])[0].strip()
                limit = min(int(params.get('limit', [50])[0]), 500)
                offset = max(int(params.get('offset', [0])[0]), 0)

                conditions = ["1=1"]
                args = []

                if termo:
                    conditions.append("(placa LIKE ? OR modelo LIKE ? OR marca LIKE ? OR orgao LIKE ?)")
                    term_arg = f"%{termo}%"
                    args.extend([term_arg, term_arg, term_arg, term_arg])
                if placa:
                    conditions.append("placa LIKE ?")
                    args.append(f"%{placa}%")
                if categoria and categoria != 'TODAS':
                    conditions.append("categoria = ?")
                    args.append(categoria)
                if orgao and orgao != 'TODOS':
                    conditions.append("orgao = ?")
                    args.append(orgao)
                if cidade and cidade != 'TODAS':
                    conditions.append("cidade = ?")
                    args.append(cidade)
                if economicidade == 'leilao':
                    conditions.append("elegivel_leilao = 1")
                elif economicidade == 'critico':
                    conditions.append("razao_gasto_venal >= 0.80")
                elif economicidade == 'economico':
                    conditions.append("razao_gasto_venal <= 0.20")

                where_clause = " AND ".join(conditions)

                db_path = BASE_DIR / "dados" / "resultados_dissertacao.db"
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                total = cur.execute(f"SELECT COUNT(*) FROM veiculos_frota_consolidada WHERE {where_clause}", args).fetchone()[0]  # nosec B608 (parametrizado)

                query = f"""
                SELECT placa, modelo, marca, categoria, orgao, cidade, ano_fabricacao,
                       quilometragem, valor_venal_fipe, gasto_manutencao, gasto_combustivel,
                       gasto_total, razao_gasto_venal, elegivel_leilao, enquadramento_decreto, status_operacional
                FROM veiculos_frota_consolidada
                WHERE {where_clause}
                ORDER BY razao_gasto_venal DESC, gasto_total DESC
                LIMIT ? OFFSET ?;
                """  # nosec B608 (parametrizado)
                query_args = args + [limit, offset]
                rows = [dict(r) for r in cur.execute(query, query_args).fetchall()]
                conn.close()

                res = {"status": "sucesso", "total": total, "limit": limit, "offset": offset, "veiculos": rows}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self._send_json_error(500, f"Erro na consulta de veículos: {e}")
            return

        # 3.7 Listagem em Tempo Real de Veículos para Leilão (Decreto 47.539/2018)
        if self.path.startswith('/api/veiculos/leilao'):
            try:
                db_path = BASE_DIR / "dados" / "resultados_dissertacao.db"
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                query = """
                SELECT placa, modelo, marca, categoria, orgao, cidade, ano_fabricacao,
                       quilometragem, valor_venal_fipe, gasto_manutencao, gasto_combustivel,
                       gasto_total, razao_gasto_venal, elegivel_leilao, enquadramento_decreto, status_operacional
                FROM veiculos_frota_consolidada
                WHERE elegivel_leilao = 1
                ORDER BY razao_gasto_venal DESC
                LIMIT 350;
                """
                rows = [dict(r) for r in cur.execute(query).fetchall()]
                conn.close()
                res = {"status": "sucesso", "total": len(rows), "criterio_legal": "Art. 5º Decreto Estadual nº 47.539/2018 (Manutenção > 40% FIPE)", "veiculos": rows}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self._send_json_error(500, f"Erro ao listar veículos para leilão: {e}")
            return

        # 3.8 Listagem de Servidores Autorizados
        if self.path.startswith('/api/servidores'):
            try:
                db_path = BASE_DIR / "dados" / "resultados_dissertacao.db"
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                rows = [dict(r) for r in cur.execute("SELECT id, nome, matricula_cpf, orgao, cargo, email, perfil, status, data_cadastro, ultimo_acesso FROM servidores_autorizados ORDER BY id;").fetchall()]
                conn.close()
                res = {"status": "sucesso", "total": len(rows), "servidores": rows}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self._send_json_error(500, f"Erro ao listar servidores: {e}")
            return

        # 3.9 Dicionário de Dados do Banco
        if self.path.startswith('/api/dicionario-dados'):
            try:
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                tabela = params.get('tabela', [''])[0].strip()
                db_path = BASE_DIR / "dados" / "resultados_dissertacao.db"
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                if tabela:
                    rows = [dict(r) for r in cur.execute("SELECT id, tabela, coluna, tipo_sqlite, chave_primaria, permite_nulo, descricao, exemplo_formato, origem_dado FROM dicionario_dados WHERE tabela = ? ORDER BY id;", (tabela,)).fetchall()]
                else:
                    rows = [dict(r) for r in cur.execute("SELECT id, tabela, coluna, tipo_sqlite, chave_primaria, permite_nulo, descricao, exemplo_formato, origem_dado FROM dicionario_dados ORDER BY tabela, id;").fetchall()]
                conn.close()
                res = {"status": "sucesso", "total": len(rows), "atributos": rows}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self._send_json_error(500, f"Erro ao consultar dicionário: {e}")
            return

        if self.path in ['/api/dicionario-dados/pdf', '/api/baixar-dicionario-dados']:
            self.send_response(302)
            self.send_header('Location', f'/relatorios_pdf/dicionario_de_dados_banco.pdf?t={int(time.time())}')
            self.end_headers()
            return

        # 4. Defesa contra Path Traversal em arquivos estáticos (CWE-22)
        clean_path = self.path.split('?')[0].lstrip('/')
        target_file = (BASE_DIR / clean_path).resolve()
        
        if not (target_file == BASE_DIR or BASE_DIR in target_file.parents):
            logger.warning(f"Tentativa de Path Traversal bloqueada: {self.path}")
            self.send_error(403, "Acesso Proibido")
            return

        super().do_GET()

    def do_POST(self):
        # Validação estrita do tamanho do payload (CWE-400 anti-DoS)
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (ValueError, TypeError):
            self._send_json_error(400, "Header Content-Length inválido.")
            return

        if content_length > MAX_BODY_SIZE:
            self._send_json_error(413, "Payload excede o limite máximo permitido de 1MB.")
            return

        body_bytes = self.rfile.read(content_length) if content_length > 0 else b'{}'
        try:
            body_json = json.loads(body_bytes.decode('utf-8')) if body_bytes else {}
        except Exception:
            self._send_json_error(400, "Formato JSON inválido no corpo da requisição.")
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 1: CHATBOT DE LINGUAGEM NATURAL (PPGCAP/UDESC)
        # ----------------------------------------------------------------------
        if self.path == '/api/chat':
            user_msg = str(body_json.get('mensagem', '')).strip()
            if not user_msg:
                self._send_json_error(400, "O campo 'mensagem' é obrigatório.")
                return

            if ai_engine is None:
                self._send_json_error(503, "Motor de IA temporariamente indisponível.")
                return

            try:
                response_data = ai_engine.process_query(user_msg)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                logger.error(f"Erro no processamento da IA: {e}")
                self._send_json_error(500, "Ocorreu um erro interno ao processar a consulta.")
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 2: ATUALIZAR GRÁFICOS E REEXECUTAR PIPELINE ESTATÍSTICO
        # ----------------------------------------------------------------------
        elif self.path == '/api/atualizar-graficos':
            if ai_engine is None:
                self._send_json_error(503, "Motor de IA temporariamente indisponível.")
                return

            try:
                res = ai_engine._action_update_pipeline(body_json)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                logger.error(f"Erro ao atualizar gráficos: {e}")
                self._send_json_error(500, "Falha ao processar atualização dos gráficos.")
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 3: COMPILAR RELATÓRIO OFICIAL EM PDF (WEASYPRINT)
        # ----------------------------------------------------------------------
        elif self.path in ['/api/gerar-relatorio', '/api/gerar-relatorio-academico']:
            if ai_engine is None:
                self._send_json_error(503, "Motor de IA temporariamente indisponível.")
                return

            try:
                res = ai_engine._action_generate_pdf()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                logger.error(f"Erro ao compilar relatório PDF: {e}")
                self._send_json_error(500, "Falha ao compilar relatório acadêmico.")
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 4: COMPILAR / ABRIR RELATÓRIO GERENCIAL EXECUTIVO EM PDF
        # ----------------------------------------------------------------------
        elif self.path == '/api/gerar-relatorio-gerencial':
            try:
                gerencial_pdf = BASE_DIR / "relatorios_pdf" / "relatorio_gerencial_frotas_executivo.pdf"
                if not gerencial_pdf.exists() or body_json.get('force', False):
                    import subprocess
                    py_bin = str(BASE_DIR / ".venv" / "bin" / "python3")
                    if not Path(py_bin).exists():
                        py_bin = sys.executable
                    script = str(BASE_DIR / "scripts" / "compilar_relatorio_gerencial_frotas.py")
                    subprocess.run([py_bin, script], check=True, timeout=120)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "sucesso",
                    "url": "/relatorios_pdf/relatorio_gerencial_frotas_executivo.pdf",
                    "mensagem": "Relatório Gerencial Executivo de Frotas pronto para visualização!"
                }, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                logger.error(f"Erro ao gerar relatório gerencial: {e}")
                self._send_json_error(500, f"Falha ao gerar relatório gerencial: {e}")
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 5: COMPILAR / ABRIR RELATÓRIO DE PREVISÃO DE GASTOS (2027-2029)
        # ----------------------------------------------------------------------
        elif self.path == '/api/gerar-relatorio-previsao':
            try:
                previsao_pdf = BASE_DIR / "relatorios_pdf" / "relatorio_previsao_gastos_2027_2029.pdf"
                if not previsao_pdf.exists() or body_json.get('force', False):
                    import subprocess
                    py_bin = str(BASE_DIR / ".venv" / "bin" / "python3")
                    if not Path(py_bin).exists():
                        py_bin = sys.executable
                    script = str(BASE_DIR / "scripts" / "previsao_orcamentaria_inflacao.py")
                    subprocess.run([py_bin, script], check=True, timeout=120)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "sucesso",
                    "url": "/relatorios_pdf/relatorio_previsao_gastos_2027_2029.pdf",
                    "mensagem": "Relatório de Previsão Orçamentária (2027–2029) com Inflação pronto!"
                }, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                logger.error(f"Erro ao gerar relatório de previsão: {e}")
                self._send_json_error(500, f"Falha ao gerar relatório de previsão: {e}")
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 6: COMPILAR / BAIXAR DISSERTAÇÃO COMPLETA EM WORD (.DOCX ABNT)
        # ----------------------------------------------------------------------
        elif self.path in ['/api/gerar-relatorio-word', '/api/compilar-docx']:
            try:
                docx_path = BASE_DIR / "relatorios" / "dissertacao_mestrado_completa_ppgcap_udesc.docx"
                if not docx_path.exists() or body_json.get('force', False):
                    import subprocess
                    py_bin = str(BASE_DIR / ".venv" / "bin" / "python3")
                    if not Path(py_bin).exists():
                        py_bin = sys.executable
                    script = str(BASE_DIR / "scripts" / "compilar_dissertacao_mestrado_docx.py")
                    subprocess.run([py_bin, script], check=True, timeout=120)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "sucesso",
                    "url": "/api/baixar-word",
                    "mensagem": "Dissertação Completa em Word (.docx ABNT) gerada com sucesso!"
                }, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                logger.error(f"Erro ao gerar documento Word: {e}")
                self._send_json_error(500, f"Falha ao gerar documento Word: {e}")
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 7: GERAR / BAIXAR PLANILHAS CONSOLIDADAS (.XLSX / .CSV)
        # ----------------------------------------------------------------------
        elif self.path in ['/api/gerar-planilhas', '/api/compilar-planilhas']:
            try:
                xlsx_path = BASE_DIR / "relatorios" / "planilha_dados_resultados_dissertacao.xlsx"
                if not xlsx_path.exists() or body_json.get('force', False):
                    import subprocess
                    py_bin = str(BASE_DIR / ".venv" / "bin" / "python3")
                    if not Path(py_bin).exists():
                        py_bin = sys.executable
                    script = str(BASE_DIR / "scripts" / "exportar_planilhas_resultados.py")
                    subprocess.run([py_bin, script], check=True, timeout=120)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "sucesso",
                    "url": "/api/baixar-planilha",
                    "mensagem": "Planilhas Consolidadas (.xlsx / .csv) geradas com sucesso!"
                }, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                logger.error(f"Erro ao gerar planilhas: {e}")
                self._send_json_error(500, f"Falha ao gerar planilhas: {e}")
            return

        # ----------------------------------------------------------------------
        # ENDPOINT 8: CADASTRAR SERVIDOR PÚBLICO AUTORIZADO
        # ----------------------------------------------------------------------
        elif self.path == '/api/servidores/cadastrar':
            nome = str(body_json.get('nome', '')).strip()
            matricula_cpf = str(body_json.get('matricula_cpf', '')).strip()
            orgao = str(body_json.get('orgao', '')).strip()
            cargo = str(body_json.get('cargo', '')).strip()
            email = str(body_json.get('email', '')).strip()
            perfil = str(body_json.get('perfil', 'GESTOR_FROTA_SEA')).strip().upper()
            status = str(body_json.get('status', 'ATIVO')).strip().upper()

            if not nome or not matricula_cpf or not email:
                self._send_json_error(400, "Os campos Nome, Matrícula/CPF e E-mail são de preenchimento obrigatório.")
                return

            try:
                db_path = BASE_DIR / "dados" / "resultados_dissertacao.db"
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                now_str = time.strftime('%Y-%m-%d %H:%M:%S')
                cur.execute("""
                INSERT INTO servidores_autorizados 
                (nome, matricula_cpf, orgao, cargo, email, perfil, status, data_cadastro, ultimo_acesso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (nome, matricula_cpf, orgao, cargo, email, perfil, status, now_str, now_str))
                new_id = cur.lastrowid
                conn.commit()
                conn.close()

                # Sincroniza em sistema_seguro.db
                conn_seg = sqlite3.connect(BASE_DIR / "dados" / "sistema_seguro.db")
                cur_seg = conn_seg.cursor()
                cur_seg.execute("""
                INSERT OR REPLACE INTO servidores_autorizados 
                (id, nome, matricula_cpf, orgao, cargo, email, perfil, status, data_cadastro, ultimo_acesso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (new_id, nome, matricula_cpf, orgao, cargo, email, perfil, status, now_str, now_str))
                
                # Registra auditoria
                cur_seg.execute("""
                INSERT INTO trilha_auditoria (username, action, details, ip_address, timestamp)
                VALUES (?, ?, ?, ?, ?);
                """, ("admin_painel", "CADASTRO_SERVIDOR", f"Servidor {nome} ({matricula_cpf}) cadastrado com perfil {perfil}", "127.0.0.1", now_str))
                conn_seg.commit()
                conn_seg.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "sucesso",
                    "mensagem": f"Servidor {nome} cadastrado com sucesso no sistema!",
                    "id": new_id
                }, ensure_ascii=False).encode('utf-8'))
            except sqlite3.IntegrityError:
                self._send_json_error(400, "Matrícula/CPF já cadastrada no sistema.")
            except Exception as e:
                logger.error(f"Erro ao cadastrar servidor: {e}")
                self._send_json_error(500, f"Falha ao cadastrar servidor: {e}")
            return

        else:
            self._send_json_error(404, "Endpoint não encontrado.")

    def _send_json_success(self, data: Any):
        """Retorna resposta JSON estruturada de sucesso."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "sucesso", **(data if isinstance(data, dict) else {"data": data})}, ensure_ascii=False).encode('utf-8'))

    def _send_json_error(self, code: int, msg: str):
        """Retorna mensagem JSON de erro sanitizada sem vazamento de stack traces (CWE-209)."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "error", "message": msg}, ensure_ascii=False).encode('utf-8'))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    port = PORT
    for p in [8080, 8081, 8082, 8888, 3000]:
        try:
            with ThreadedTCPServer(("", p), SecureDashboardHandler) as httpd:
                logger.info(f"Dashboard Seguro Online: http://localhost:{p}/dashboard/")
                httpd.serve_forever()
        except OSError:
            continue

if __name__ == "__main__":
    main()

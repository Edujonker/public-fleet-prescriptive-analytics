# -*- coding: utf-8 -*-
"""
================================================================================
MOTOR DE GESTÃO DE FROTAS PÚBLICAS (FLEET MANAGEMENT CORE ENGINE)
SISTEMA INTEGRADO DE GESTÃO DE FROTAS & ANALÍTICA PRESCRITIVA (PPGCAP/UDESC)
================================================================================
Módulos:
1. Gestão de Veículos (CRUD, Ficha Cadastral, Ciclo de Vida e Status Operacional)
2. Gestão de Motoristas & Condutores Autorizados (CNH, Pontuação, Vencimentos)
3. Despacho de Viagens & Diário de Bordo (Requisições, Checklist Pré/Pós, Hodômetro)
4. Ordens de Serviço & Manutenção (Preventiva, Corretiva, Preditiva, Peças e Oficinas)
5. Auditoria de Abastecimentos & Detecção de Fraudes (Cartão combustível, tanque e km/L)
6. Analítica Prescritiva & Enquadramento Legal (Decreto Estadual nº 47.539/2018)
================================================================================
"""

import os
import json
import time
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("FleetEngine")

class FleetManagementEngine:
    """Motor central de regras de negócio para a gestão operacional de frotas públicas."""

    def __init__(self, db_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.db_path = Path(db_path or (base_dir / "dados" / "resultados_dissertacao.db"))
        self._inicializar_tabelas_operacionais()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _inicializar_tabelas_operacionais(self):
        """Cria e garante os esquemas relacionais necessários para o sistema operacional de frotas."""
        conn = self._get_connection()
        cur = conn.cursor()

        # 1. Tabela de Motoristas / Condutores Autorizados
        cur.execute("""
        CREATE TABLE IF NOT EXISTS motoristas_autorizados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            cnh_numero TEXT UNIQUE NOT NULL,
            cnh_categoria TEXT NOT NULL,
            cnh_validade TEXT NOT NULL,
            orgao TEXT NOT NULL,
            cargo TEXT,
            telefone TEXT,
            email TEXT,
            pontos_cnh INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ATIVO',
            data_cadastro TEXT NOT NULL
        );
        """)

        # 2. Tabela de Despacho de Viagens / Diário de Bordo
        cur.execute("""
        CREATE TABLE IF NOT EXISTS viagens_despacho (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_requisicao TEXT UNIQUE NOT NULL,
            veiculo_placa TEXT NOT NULL,
            motorista_id INTEGER,
            motorista_nome TEXT NOT NULL,
            orgao_solicitante TEXT NOT NULL,
            destino_cidade TEXT NOT NULL,
            motivo_viagem TEXT NOT NULL,
            data_saida TEXT NOT NULL,
            km_saida REAL NOT NULL,
            data_retorno TEXT,
            km_retorno REAL,
            checklist_saida_ok INTEGER DEFAULT 1,
            checklist_retorno_ok INTEGER DEFAULT 1,
            status TEXT DEFAULT 'EM_CURSO',
            observacoes TEXT,
            criado_em TEXT NOT NULL,
            FOREIGN KEY (veiculo_placa) REFERENCES veiculos_frota_consolidada(placa),
            FOREIGN KEY (motorista_id) REFERENCES motoristas_autorizados(id)
        );
        """)

        # 3. Tabela de Ordens de Serviço (OS) de Manutenção
        cur.execute("""
        CREATE TABLE IF NOT EXISTS manutencao_ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_os TEXT UNIQUE NOT NULL,
            veiculo_placa TEXT NOT NULL,
            tipo_manutencao TEXT NOT NULL,
            oficina_credenciada TEXT NOT NULL,
            cnpj_oficina TEXT,
            descricao_servico TEXT NOT NULL,
            pecas_aplicadas TEXT,
            valor_pecas REAL DEFAULT 0.0,
            valor_mao_obra REAL DEFAULT 0.0,
            valor_total REAL NOT NULL,
            km_veiculo REAL NOT NULL,
            data_abertura TEXT NOT NULL,
            data_conclusao TEXT,
            status TEXT DEFAULT 'EM_EXECUCAO',
            aprovado_por TEXT,
            FOREIGN KEY (veiculo_placa) REFERENCES veiculos_frota_consolidada(placa)
        );
        """)

        # 4. Tabela de Postos de Combustível Credenciados
        cur.execute("""
        CREATE TABLE IF NOT EXISTS postos_credenciados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_fantasia TEXT NOT NULL,
            razao_social TEXT,
            cnpj TEXT UNIQUE NOT NULL,
            cidade TEXT NOT NULL,
            bandeira TEXT,
            status TEXT DEFAULT 'ATIVO',
            total_transacoes INTEGER DEFAULT 0,
            total_faturado REAL DEFAULT 0.0
        );
        """)

        # Índices para otimização de consultas em tempo real
        cur.execute("CREATE INDEX IF NOT EXISTS idx_viagens_placa ON viagens_despacho(veiculo_placa);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_viagens_status ON viagens_despacho(status);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_os_placa ON manutencao_ordens_servico(veiculo_placa);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_os_status ON manutencao_ordens_servico(status);")

        conn.commit()

        # Seed inicial de motoristas e postos se estiverem vazios
        cur.execute("SELECT COUNT(*) FROM motoristas_autorizados;")
        if cur.fetchone()[0] == 0:
            now_str = time.strftime('%Y-%m-%d %H:%M:%S')
            motoristas_iniciais = [
                ("Carlos Eduardo Silveira", "042.881.992-10", "04992182711", "D", "2028-11-20", "PMSC", "Subtenente Motorista", "(48) 99123-4567", "carlos.silveira@pm.sc.gov.br", 0, "ATIVO", now_str),
                ("Marcos Vinicius Ribeiro", "033.441.772-88", "03881927310", "B", "2027-05-15", "SEA", "Agente Administrativo", "(48) 98877-2233", "marcos.ribeiro@sea.sc.gov.br", 3, "ATIVO", now_str),
                ("Juliana Mendes Castro", "065.112.339-44", "05112938402", "AB", "2029-01-10", "SES", "Condutora de Ambulância", "(48) 99654-1122", "juliana.castro@saude.sc.gov.br", 0, "ATIVO", now_str),
                ("Rodrigo Fagundes Alencar", "078.223.445-66", "06223491823", "E", "2027-09-30", "CBMSC", "Sargento Socorrista", "(48) 99182-3344", "rodrigo.alencar@cbm.sc.gov.br", 0, "ATIVO", now_str),
                ("Renata Cristina Boaventura", "012.998.441-23", "02998124719", "B", "2026-12-18", "SED", "Motorista de Apoio Pedagógico", "(48) 98412-8877", "renata.boaventura@sed.sc.gov.br", 4, "ATIVO", now_str)
            ]
            cur.executemany("""
            INSERT INTO motoristas_autorizados 
            (nome, cpf, cnh_numero, cnh_categoria, cnh_validade, orgao, cargo, telefone, email, pontos_cnh, status, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, motoristas_iniciais)

            postos_iniciais = [
                ("Auto Posto Ilha Bela", "Auto Posto Ilha Bela Ltda", "01.234.567/0001-89", "Florianópolis", "Ipiranga", "ATIVO", 12540, 689400.50),
                ("Posto Beira-Mar Central", "Combustíveis Beira Mar S/A", "02.345.678/0001-90", "Florianópolis", "Petrobras", "ATIVO", 18450, 1024500.00),
                ("Posto Catarinense Vale", "Posto Catarinense do Vale Ltda", "03.456.789/0001-01", "Blumenau", "Shell", "ATIVO", 8940, 485120.00),
                ("Posto Rota Norte Joinville", "Rota Norte Comércio de Derivados", "04.567.890/0001-12", "Joinville", "Ipiranga", "ATIVO", 14200, 810300.20),
                ("Posto Planalto Serrano", "Planalto Serrano Abastecedora Ltda", "05.678.901/0001-23", "Lages", "Petrobras", "ATIVO", 7350, 395400.00)
            ]
            cur.executemany("""
            INSERT INTO postos_credenciados
            (nome_fantasia, razao_social, cnpj, cidade, bandeira, status, total_transacoes, total_faturado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, postos_iniciais)

            # Algumas viagens de exemplo
            viagens_iniciais = [
                ("REQ-2026-00891", "MLH1204", 1, "Carlos Eduardo Silveira", "PMSC", "Lages", "Apoio a Operação Policial Regional", "2026-10-28 07:30:00", 142100.0, "2026-10-29 18:45:00", 142560.0, 1, 1, "CONCLUIDA", "Viagem sem intercorrências", now_str),
                ("REQ-2026-00912", "ABC1D23", 2, "Marcos Vinicius Ribeiro", "SEA", "Joinville", "Vistoria Técnica de Unidade Descentralizada", "2026-10-30 06:00:00", 87400.0, None, None, 1, 1, "EM_CURSO", "Em trânsito para a Regional Joinville", now_str),
                ("REQ-2026-00915", "MDF9942", 3, "Juliana Mendes Castro", "SES", "Criciúma", "Transporte de Insumos Médicos Prioritários", "2026-10-29 14:00:00", 215400.0, "2026-10-30 08:30:00", 215880.0, 1, 1, "CONCLUIDA", "Entrega efetuada com sucesso", now_str),
                ("REQ-2026-00920", "MKZ3321", 4, "Rodrigo Fagundes Alencar", "CBMSC", "Blumenau", "Treinamento Integrado de Salvamento", "2026-10-30 08:00:00", 112000.0, None, None, 1, 1, "EM_CURSO", "Equipe a caminho", now_str)
            ]
            cur.executemany("""
            INSERT INTO viagens_despacho
            (numero_requisicao, veiculo_placa, motorista_id, motorista_nome, orgao_solicitante, destino_cidade, motivo_viagem, data_saida, km_saida, data_retorno, km_retorno, checklist_saida_ok, checklist_retorno_ok, status, observacoes, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, viagens_iniciais)

            # Algumas ordens de serviço de exemplo
            os_iniciais = [
                ("OS-2026-0412", "MLH1204", "PREVENTIVA", "Mecânica Catarinense Ltda", "11.222.333/0001-44", "Troca de óleo sintético, filtro de óleo e filtro de ar", "Óleo 5W30 Sintético, Filtros", 350.0, 180.0, 530.0, 140000.0, "2026-10-15 09:00:00", "2026-10-15 16:30:00", "CONCLUIDA", "gestor_sea"),
                ("OS-2026-0455", "QHX8891", "CORRETIVA", "Auto Elétrica Central", "22.333.444/0001-55", "Substituição do alternador e correia de acessórios", "Alternador 120A Bosch, Correia Poly-V", 1450.0, 420.0, 1870.0, 198500.0, "2026-10-25 11:20:00", "2026-10-27 15:00:00", "CONCLUIDA", "gestor_sea"),
                ("OS-2026-0498", "MDF9942", "PREDITIVA", "Centro Automotivo Ilha", "33.444.555/0001-66", "Inspeção de pastilhas de freio e disco por sensor preditivo", "Discos de freio dianteiros, Pastilhas cerâmica", 680.0, 250.0, 930.0, 214800.0, "2026-10-28 14:00:00", None, "EM_EXECUCAO", "gestor_sea")
            ]
            cur.executemany("""
            INSERT INTO manutencao_ordens_servico
            (numero_os, veiculo_placa, tipo_manutencao, oficina_credenciada, cnpj_oficina, descricao_servico, pecas_aplicadas, valor_pecas, valor_mao_obra, valor_total, km_veiculo, data_abertura, data_conclusao, status, aprovado_por)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, os_iniciais)

            conn.commit()

        conn.close()

    # --------------------------------------------------------------------------
    # 1. GESTÃO DE VEÍCULOS & FROTA
    # --------------------------------------------------------------------------

    def listar_veiculos(self, termo: str = "", categoria: str = "", orgao: str = "",
                        cidade: str = "", economicidade: str = "", limite: int = 50,
                        offset: int = 0) -> Dict[str, Any]:
        """Consulta multi-critério de veículos com paginação e ordenação por criticidade."""
        conn = self._get_connection()
        cur = conn.cursor()

        conditions = ["1=1"]
        args = []

        if termo:
            conditions.append("(placa LIKE ? OR modelo LIKE ? OR marca LIKE ? OR orgao LIKE ?)")
            term_arg = f"%{termo.upper()}%"
            args.extend([term_arg, term_arg, term_arg, term_arg])

        if categoria and categoria.upper() != 'TODAS':
            conditions.append("categoria = ?")
            args.append(categoria)

        if orgao and orgao.upper() != 'TODOS':
            conditions.append("orgao = ?")
            args.append(orgao)

        if cidade and cidade.upper() != 'TODAS':
            conditions.append("cidade = ?")
            args.append(cidade)

        if economicidade == 'leilao':
            conditions.append("elegivel_leilao = 1")
        elif economicidade == 'critico':
            conditions.append("razao_gasto_venal >= 0.80")
        elif economicidade == 'economico':
            conditions.append("razao_gasto_venal <= 0.20")

        where_clause = " AND ".join(conditions)

        total = cur.execute(f"SELECT COUNT(*) FROM veiculos_frota_consolidada WHERE {where_clause}", args).fetchone()[0]  # nosec B608 (cláusulas estáticas parametrizadas com args)

        query = f"""
        SELECT placa, modelo, marca, categoria, orgao, cidade, ano_fabricacao,
               quilometragem, valor_venal_fipe, gasto_manutencao, gasto_combustivel,
               gasto_total, razao_gasto_venal, elegivel_leilao, enquadramento_decreto, status_operacional
        FROM veiculos_frota_consolidada
        WHERE {where_clause}
        ORDER BY razao_gasto_venal DESC, gasto_total DESC
        LIMIT ? OFFSET ?;
        """  # nosec B608 (cláusulas estáticas parametrizadas com args)
        rows = [dict(r) for r in cur.execute(query, args + [limite, offset]).fetchall()]
        conn.close()

        return {
            "total": total,
            "limite": limite,
            "offset": offset,
            "veiculos": rows
        }

    def obter_ficha_veiculo(self, placa: str) -> Optional[Dict[str, Any]]:
        """Retorna dossiê completo de um veículo, incluindo histórico de OS, viagens e abastecimentos."""
        placa = placa.strip().upper()
        conn = self._get_connection()
        cur = conn.cursor()

        veiculo_row = cur.execute("SELECT * FROM veiculos_frota_consolidada WHERE placa = ?;", (placa,)).fetchone()
        if not veiculo_row:
            conn.close()
            return None

        veiculo = dict(veiculo_row)

        # Histórico de Ordens de Serviço
        os_rows = [dict(r) for r in cur.execute("""
            SELECT numero_os, tipo_manutencao, oficina_credenciada, descricao_servico, valor_total, km_veiculo, data_abertura, status
            FROM manutencao_ordens_servico
            WHERE veiculo_placa = ?
            ORDER BY data_abertura DESC
            LIMIT 15;
        """, (placa,)).fetchall()]

        # Histórico de Viagens
        viagens_rows = [dict(r) for r in cur.execute("""
            SELECT numero_requisicao, motorista_nome, destino_cidade, motivo_viagem, data_saida, data_retorno, km_saida, km_retorno, status
            FROM viagens_despacho
            WHERE veiculo_placa = ?
            ORDER BY data_saida DESC
            LIMIT 15;
        """, (placa,)).fetchall()]

        # Amostra recente de abastecimentos
        abast_rows = [dict(r) for r in cur.execute("""
            SELECT id_abastecimento, data_abastecimento, tipo_combustivel, quantidade_litros, valor_total, quilometragem, media_consumo_kml
            FROM abastecimentos
            WHERE placa = ?
            ORDER BY data_abastecimento DESC
            LIMIT 10;
        """, (placa,)).fetchall()]

        conn.close()

        veiculo["historico_ordens_servico"] = os_rows
        veiculo["historico_viagens"] = viagens_rows
        veiculo["recentes_abastecimentos"] = abast_rows
        return veiculo

    def cadastrar_veiculo(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Cadastra um novo veículo na frota pública com validações técnicas e FIPE."""
        placa = str(dados.get("placa", "")).strip().upper()
        modelo = str(dados.get("modelo", "")).strip()
        marca = str(dados.get("marca", "")).strip()
        categoria = str(dados.get("categoria", "PASSEIO")).strip().upper()
        orgao = str(dados.get("orgao", "SEA")).strip().upper()
        cidade = str(dados.get("cidade", "Florianópolis")).strip()
        ano = int(dados.get("ano_fabricacao", 2022))
        km = float(dados.get("quilometragem", 0.0))
        valor_fipe = float(dados.get("valor_venal_fipe", 50000.0))

        if not placa or not modelo or not marca:
            raise ValueError("Placa, modelo e marca são campos obrigatórios.")

        conn = self._get_connection()
        cur = conn.cursor()

        # Verifica duplicidade
        existe = cur.execute("SELECT 1 FROM veiculos_frota_consolidada WHERE placa = ?;", (placa,)).fetchone()
        if existe:
            conn.close()
            raise ValueError(f"Veículo com placa {placa} já existe no cadastro da frota.")

        cur.execute("""
        INSERT INTO veiculos_frota_consolidada 
        (placa, modelo, marca, categoria, orgao, cidade, ano_fabricacao, quilometragem,
         valor_venal_fipe, gasto_manutencao, gasto_combustivel, gasto_total,
         razao_gasto_venal, elegivel_leilao, enquadramento_decreto, status_operacional)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0.0, 0.0, 0.0, 0, 'OPERACIONAL', 'ATIVO');
        """, (placa, modelo, marca, categoria, orgao, cidade, ano, km, valor_fipe))

        conn.commit()
        conn.close()

        return {
            "status": "sucesso",
            "mensagem": f"Veículo {placa} ({marca} {modelo}) cadastrado com sucesso!",
            "placa": placa
        }

    # --------------------------------------------------------------------------
    # 2. GESTÃO DE MOTORISTAS
    # --------------------------------------------------------------------------

    def listar_motoristas(self, status: str = "TODOS") -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        if status.upper() == "TODOS":
            rows = cur.execute("SELECT * FROM motoristas_autorizados ORDER BY nome;").fetchall()
        else:
            rows = cur.execute("SELECT * FROM motoristas_autorizados WHERE status = ? ORDER BY nome;", (status.upper(),)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def cadastrar_motorista(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        nome = str(dados.get("nome", "")).strip()
        cpf = str(dados.get("cpf", "")).strip()
        cnh = str(dados.get("cnh_numero", "")).strip()
        cat = str(dados.get("cnh_categoria", "B")).strip().upper()
        val = str(dados.get("cnh_validade", "")).strip()
        orgao = str(dados.get("orgao", "SEA")).strip().upper()
        cargo = str(dados.get("cargo", "Condutor Autorizado")).strip()
        tel = str(dados.get("telefone", "")).strip()
        email = str(dados.get("email", "")).strip()

        if not nome or not cpf or not cnh or not val:
            raise ValueError("Nome, CPF, CNH e Validade são campos obrigatórios.")

        conn = self._get_connection()
        cur = conn.cursor()
        now_str = time.strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("""
        INSERT INTO motoristas_autorizados
        (nome, cpf, cnh_numero, cnh_categoria, cnh_validade, orgao, cargo, telefone, email, pontos_cnh, status, data_cadastro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'ATIVO', ?);
        """, (nome, cpf, cnh, cat, val, orgao, cargo, tel, email, now_str))

        new_id = cur.lastrowid
        conn.commit()
        conn.close()

        return {
            "status": "sucesso",
            "mensagem": f"Motorista {nome} cadastrado com sucesso!",
            "id": new_id
        }

    # --------------------------------------------------------------------------
    # 3. DESPACHO DE VIAGENS & DIÁRIO DE BORDO
    # --------------------------------------------------------------------------

    def listar_viagens(self, status: str = "TODOS", limite: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        if status.upper() == "TODOS":
            rows = cur.execute("SELECT * FROM viagens_despacho ORDER BY id DESC LIMIT ?;", (limite,)).fetchall()
        else:
            rows = cur.execute("SELECT * FROM viagens_despacho WHERE status = ? ORDER BY id DESC LIMIT ?;", (status.upper(), limite)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def agendar_viagem(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        placa = str(dados.get("veiculo_placa", "")).strip().upper()
        mot_id = dados.get("motorista_id")
        mot_nome = str(dados.get("motorista_nome", "")).strip()
        orgao = str(dados.get("orgao_solicitante", "SEA")).strip().upper()
        destino = str(dados.get("destino_cidade", "")).strip()
        motivo = str(dados.get("motivo_viagem", "")).strip()
        km_saida = float(dados.get("km_saida", 0.0))

        if not placa or not destino or not motivo:
            raise ValueError("Placa, destino e motivo da viagem são obrigatórios.")

        conn = self._get_connection()
        cur = conn.cursor()

        # Gera número sequencial de requisição
        req_num = f"REQ-{time.strftime('%Y')}-{int(time.time()) % 100000:05d}"
        now_str = time.strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("""
        INSERT INTO viagens_despacho
        (numero_requisicao, veiculo_placa, motorista_id, motorista_nome, orgao_solicitante, destino_cidade, motivo_viagem, data_saida, km_saida, checklist_saida_ok, status, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'EM_CURSO', ?);
        """, (req_num, placa, mot_id, mot_nome, orgao, destino, motivo, now_str, km_saida, now_str))

        # Atualiza status operacional do veículo
        cur.execute("UPDATE veiculos_frota_consolidada SET status_operacional = 'EM_VIAGEM' WHERE placa = ?;", (placa,))

        conn.commit()
        conn.close()

        return {
            "status": "sucesso",
            "mensagem": f"Viagem {req_num} para {destino} despachada com sucesso!",
            "numero_requisicao": req_num
        }

    def finalizar_viagem(self, requisicao: str, km_retorno: float, observacoes: str = "") -> Dict[str, Any]:
        conn = self._get_connection()
        cur = conn.cursor()
        now_str = time.strftime('%Y-%m-%d %H:%M:%S')

        v_row = cur.execute("SELECT * FROM viagens_despacho WHERE numero_requisicao = ?;", (requisicao,)).fetchone()
        if not v_row:
            conn.close()
            raise ValueError(f"Requisição de viagem {requisicao} não encontrada.")

        placa = v_row["veiculo_placa"]
        km_saida = v_row["km_saida"]

        if km_retorno < km_saida:
            conn.close()
            raise ValueError(f"Km de retorno ({km_retorno}) não pode ser inferior ao Km de saída ({km_saida}).")

        cur.execute("""
        UPDATE viagens_despacho
        SET data_retorno = ?, km_retorno = ?, status = 'CONCLUIDA', observacoes = ?
        WHERE numero_requisicao = ?;
        """, (now_str, km_retorno, observacoes, requisicao))

        # Atualiza quilometragem do veículo e status para ATIVO
        cur.execute("""
        UPDATE veiculos_frota_consolidada 
        SET quilometragem = ?, status_operacional = 'ATIVO' 
        WHERE placa = ?;
        """, (km_retorno, placa))

        conn.commit()
        conn.close()

        km_rodados = km_retorno - km_saida
        return {
            "status": "sucesso",
            "mensagem": f"Viagem {requisicao} concluída com sucesso! Quilometragem percorrida: {km_rodados:.1f} km.",
            "km_percorridos": km_rodados
        }

    # --------------------------------------------------------------------------
    # 4. GESTÃO DE ORDENS DE SERVIÇO & MANUTENÇÃO
    # --------------------------------------------------------------------------

    def listar_ordens_servico(self, status: str = "TODOS", limite: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        if status.upper() == "TODOS":
            rows = cur.execute("SELECT * FROM manutencao_ordens_servico ORDER BY id DESC LIMIT ?;", (limite,)).fetchall()
        else:
            rows = cur.execute("SELECT * FROM manutencao_ordens_servico WHERE status = ? ORDER BY id DESC LIMIT ?;", (status.upper(), limite)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def abrir_ordem_servico(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        placa = str(dados.get("veiculo_placa", "")).strip().upper()
        tipo = str(dados.get("tipo_manutencao", "CORRETIVA")).strip().upper()
        oficina = str(dados.get("oficina_credenciada", "")).strip()
        descricao = str(dados.get("descricao_servico", "")).strip()
        pecas = str(dados.get("pecas_aplicadas", "")).strip()
        val_pecas = float(dados.get("valor_pecas", 0.0))
        val_mo = float(dados.get("valor_mao_obra", 0.0))
        val_total = val_pecas + val_mo
        km = float(dados.get("km_veiculo", 0.0))
        aprovador = str(dados.get("aprovado_por", "gestor_sea")).strip()

        if not placa or not oficina or not descricao:
            raise ValueError("Placa, oficina credenciada e descrição do serviço são obrigatórios.")

        conn = self._get_connection()
        cur = conn.cursor()

        os_num = f"OS-{time.strftime('%Y')}-{int(time.time()) % 100000:05d}"
        now_str = time.strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("""
        INSERT INTO manutencao_ordens_servico
        (numero_os, veiculo_placa, tipo_manutencao, oficina_credenciada, descricao_servico, pecas_aplicadas, valor_pecas, valor_mao_obra, valor_total, km_veiculo, data_abertura, status, aprovado_por)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'EM_EXECUCAO', ?);
        """, (os_num, placa, tipo, oficina, descricao, pecas, val_pecas, val_mo, val_total, km, now_str, aprovador))

        # Atualiza gasto acumulado de manutenção e status do veículo
        cur.execute("""
        UPDATE veiculos_frota_consolidada
        SET gasto_manutencao = gasto_manutencao + ?,
            gasto_total = gasto_total + ?,
            razao_gasto_venal = (gasto_manutencao + ?) / CASE WHEN valor_venal_fipe > 0 THEN valor_venal_fipe ELSE 1 END,
            elegivel_leilao = CASE WHEN ((gasto_manutencao + ?) / CASE WHEN valor_venal_fipe > 0 THEN valor_venal_fipe ELSE 1 END) >= 0.40 THEN 1 ELSE 0 END,
            status_operacional = 'EM_MANUTENCAO'
        WHERE placa = ?;
        """, (val_total, val_total, val_total, val_total, placa))

        conn.commit()
        conn.close()

        return {
            "status": "sucesso",
            "mensagem": f"Ordem de Serviço {os_num} aberta com sucesso para o veículo {placa}!",
            "numero_os": os_num,
            "valor_total": val_total
        }

    # --------------------------------------------------------------------------
    # 5. AUDITORIA DE ABASTECIMENTOS & DETECÇÃO DE FRAUDES
    # --------------------------------------------------------------------------

    def registrar_abastecimento(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Registra transação de combustível com auditoria em tempo real de capacidade de tanque."""
        placa = str(dados.get("placa", "")).strip().upper()
        combustivel = str(dados.get("tipo_combustivel", "GASOLINA COMUM")).strip().upper()
        litros = float(dados.get("quantidade_litros", 0.0))
        preco_litro = float(dados.get("preco_unitario", 5.89))
        valor_total = float(dados.get("valor_total", litros * preco_litro))
        km_atual = float(dados.get("quilometragem", 0.0))
        posto = str(dados.get("posto_combustivel", "Posto Credenciado")).strip()

        if not placa or litros <= 0:
            raise ValueError("Placa e quantidade de litros válida são obrigatórios.")

        # Detecção de anomalia de capacidade de tanque (ex: veículo de passeio com mais de 75 litros)
        anomalia_detectada = False
        motivo_alerta = ""
        capacidade_padrao = 65.0  # Tanque padrão de veículos de frota
        if litros > 75.0:
            anomalia_detectada = True
            motivo_alerta = f"Volume abastecido ({litros:.1f} L) excede capacidade nominal do tanque ({capacidade_padrao} L)!"

        conn = self._get_connection()
        cur = conn.cursor()
        now_str = time.strftime('%Y-%m-%d %H:%M:%S')

        # Busca último abastecimento do veículo para calcular consumo km/L
        ultimo = cur.execute("""
            SELECT quilometragem FROM abastecimentos 
            WHERE placa = ? 
            ORDER BY data_abastecimento DESC, id_abastecimento DESC 
            LIMIT 1;
        """, (placa,)).fetchone()

        km_litro = None
        if ultimo and ultimo[0] and km_atual > ultimo[0]:
            distancia = km_atual - ultimo[0]
            km_litro = round(distancia / litros, 2)
            if km_litro < 3.0 or km_litro > 25.0:
                anomalia_detectada = True
                motivo_alerta += f" Consumo atípico detectado: {km_litro} km/L."

        cur.execute("""
        INSERT INTO abastecimentos 
        (placa, data_abastecimento, tipo_combustivel, quantidade_litros, valor_total, quilometragem, media_consumo_kml)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (placa, now_str, combustivel, litros, valor_total, km_atual, km_litro))

        # Atualiza gasto de combustível acumulado no veículo
        cur.execute("""
        UPDATE veiculos_frota_consolidada
        SET gasto_combustivel = gasto_combustivel + ?,
            gasto_total = gasto_total + ?,
            quilometragem = MAX(quilometragem, ?)
        WHERE placa = ?;
        """, (valor_total, valor_total, km_atual, placa))

        conn.commit()
        conn.close()

        return {
            "status": "sucesso",
            "mensagem": f"Abastecimento de {litros:.1f} L registrado com sucesso!",
            "anomalia_detectada": anomalia_detectada,
            "motivo_alerta": motivo_alerta if anomalia_detectada else "Transação em conformidade.",
            "km_litro_calculado": km_litro
        }

    # --------------------------------------------------------------------------
    # 6. LEILÃO & DESCARTE INTELIGENTE (ART. 5º DECRETO ESTADUAL 47.539/2018)
    # --------------------------------------------------------------------------

    def listar_veiculos_leilao(self, limite: int = 100) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT placa, modelo, marca, categoria, orgao, cidade, ano_fabricacao,
                   quilometragem, valor_venal_fipe, gasto_manutencao, gasto_combustivel,
                   gasto_total, razao_gasto_venal, enquadramento_decreto, status_operacional
            FROM veiculos_frota_consolidada
            WHERE elegivel_leilao = 1
            ORDER BY razao_gasto_venal DESC
            LIMIT ?;
        """, (limite,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def obter_estatisticas_painel_frota(self) -> Dict[str, Any]:
        """Calcula KPIs consolidados para os cards superiores do dashboard da frota."""
        conn = self._get_connection()
        cur = conn.cursor()

        total_veiculos = cur.execute("SELECT COUNT(*) FROM veiculos_frota_consolidada;").fetchone()[0]
        total_leilao = cur.execute("SELECT COUNT(*) FROM veiculos_frota_consolidada WHERE elegivel_leilao = 1;").fetchone()[0]
        total_viagens_ativas = cur.execute("SELECT COUNT(*) FROM viagens_despacho WHERE status = 'EM_CURSO';").fetchone()[0]
        total_os_abertas = cur.execute("SELECT COUNT(*) FROM manutencao_ordens_servico WHERE status = 'EM_EXECUCAO';").fetchone()[0]
        total_motoristas = cur.execute("SELECT COUNT(*) FROM motoristas_autorizados WHERE status = 'ATIVO';").fetchone()[0]
        soma_gastos = cur.execute("SELECT SUM(gasto_total) FROM veiculos_frota_consolidada;").fetchone()[0] or 0.0

        conn.close()

        return {
            "total_veiculos_cadastrados": total_veiculos,
            "veiculos_elegiveis_leilao": total_leilao,
            "viagens_em_curso": total_viagens_ativas,
            "ordens_servico_abertas": total_os_abertas,
            "motoristas_ativos": total_motoristas,
            "despesa_global_frota_reais": round(soma_gastos, 2)
        }


# Instância Singleton do Motor de Frotas
fleet_engine_global = FleetManagementEngine()

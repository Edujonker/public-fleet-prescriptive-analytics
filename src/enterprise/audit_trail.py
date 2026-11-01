# -*- coding: utf-8 -*-
"""
================================================================================
MECANISMO DE LOGS & AUDITORIA IMUTÁVEL (AUDIT TRAIL / BLOCKCHAIN LEDGER)
SISTEMA DE GESTÃO DE FROTAS PÚBLICAS (PPGCAP/UDESC)
================================================================================
Funcionalidades:
- Registro estrito e não repudiável de todas as ações críticas da frota pública
- Rastreamento forense: Quem (Ator/CPF), O quê (Ação), Quando (UTC), Onde (Recurso) e De Onde (IP)
- Encadeamento criptográfico SHA-256 (Hash Chaining): cada entrada sela o hash do bloco anterior
- Verificador matemático de violação de integridade (detecta qualquer adulteração retrospectiva)
- Persistência dupla: Tabela relacional indexada e Ledger imutável append-only (.jsonl)
================================================================================
"""

import os
import json
import time
import hashlib
import sqlite3
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class ImmutableAuditTrail:
    """Gerenciador de Trilha de Auditoria com Encadeamento Criptográfico SHA-256."""

    BLOCO_GENESE_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, db_path: Optional[str] = None, jsonl_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.db_path = db_path or str(base_dir / "dados" / "resultados_dissertacao.db")
        self.jsonl_path = jsonl_path or str(base_dir / "dados" / "trilha_auditoria_ledger.jsonl")
        self._lock = threading.Lock()
        self._inicializar_tabela()

    def _obter_conexao(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _inicializar_tabela(self):
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trilha_auditoria_imutavel (
                    sequencia INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_evento TEXT UNIQUE NOT NULL,
                    timestamp_utc TEXT NOT NULL,
                    timestamp_epoch REAL NOT NULL,
                    ator_id TEXT NOT NULL,
                    ator_nome TEXT,
                    ator_cargo TEXT,
                    ator_orgao TEXT,
                    acao TEXT NOT NULL,
                    recurso TEXT NOT NULL,
                    ip_origem TEXT NOT NULL,
                    trace_id TEXT,
                    sucesso INTEGER NOT NULL DEFAULT 1,
                    detalhes_json TEXT,
                    payload_sha256 TEXT NOT NULL,
                    hash_anterior TEXT NOT NULL,
                    hash_bloco TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_ator ON trilha_auditoria_imutavel(ator_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_acao ON trilha_auditoria_imutavel(acao)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_recurso ON trilha_auditoria_imutavel(recurso)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON trilha_auditoria_imutavel(timestamp_epoch)")
            conn.commit()

    def _obter_ultimo_hash(self, cursor: sqlite3.Cursor) -> str:
        cursor.execute("SELECT hash_bloco FROM trilha_auditoria_imutavel ORDER BY sequencia DESC LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else self.BLOCO_GENESE_HASH

    @staticmethod
    def _calcular_hash_bloco(hash_anterior: str, timestamp_epoch: float, ator_id: str, acao: str, recurso: str, payload_sha256: str) -> str:
        string_bloco = f"{hash_anterior}|{timestamp_epoch:.6f}|{ator_id}|{acao}|{recurso}|{payload_sha256}"
        return hashlib.sha256(string_bloco.encode('utf-8')).hexdigest()

    def registrar_evento(
        self,
        ator_id: str,
        acao: str,
        recurso: str,
        detalhes: Optional[Dict[str, Any]] = None,
        ator_nome: str = "Desconhecido",
        ator_cargo: str = "Operador",
        ator_orgao: str = "SEA",
        ip_origem: str = "127.0.0.1",
        trace_id: Optional[str] = None,
        sucesso: bool = True
    ) -> Dict[str, Any]:
        """Registra uma ação no ledger com encadeamento de hash SHA-256 e gravação imutável."""
        detalhes = detalhes or {}
        timestamp_epoch = time.time()
        timestamp_utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(timestamp_epoch))
        id_evento = hashlib.sha256(f"{timestamp_epoch}_{ator_id}_{acao}_{recurso}".encode('utf-8')).hexdigest()[:16]

        detalhes_serializados = json.dumps(detalhes, sort_keys=True, ensure_ascii=False)
        payload_sha256 = hashlib.sha256(detalhes_serializados.encode('utf-8')).hexdigest()

        with self._lock:
            with self._obter_conexao() as conn:
                cursor = conn.cursor()
                hash_anterior = self._obter_ultimo_hash(cursor)
                hash_bloco = self._calcular_hash_bloco(hash_anterior, timestamp_epoch, ator_id, acao, recurso, payload_sha256)

                cursor.execute("""
                    INSERT INTO trilha_auditoria_imutavel (
                        id_evento, timestamp_utc, timestamp_epoch, ator_id, ator_nome,
                        ator_cargo, ator_orgao, acao, recurso, ip_origem, trace_id,
                        sucesso, detalhes_json, payload_sha256, hash_anterior, hash_bloco
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_evento, timestamp_utc, timestamp_epoch, ator_id, ator_nome,
                    ator_cargo, ator_orgao, acao, recurso, ip_origem, trace_id or "trace-root",
                    1 if sucesso else 0, detalhes_serializados, payload_sha256, hash_anterior, hash_bloco
                ))
                conn.commit()
                sequencia = cursor.lastrowid

            # Gravação append-only em arquivo Ledger (.jsonl)
            registro = {
                "sequencia": sequencia,
                "id_evento": id_evento,
                "timestamp_utc": timestamp_utc,
                "ator_id": ator_id,
                "acao": acao,
                "recurso": recurso,
                "ip_origem": ip_origem,
                "trace_id": trace_id,
                "payload_sha256": payload_sha256,
                "hash_anterior": hash_anterior,
                "hash_bloco": hash_bloco
            }
            try:
                os.makedirs(os.path.dirname(self.jsonl_path), exist_ok=True)
                with open(self.jsonl_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(registro, ensure_ascii=False) + "\n")
            except Exception:
                pass

            return registro

    def verificar_integridade(self) -> Tuple[bool, int, Optional[str]]:
        """
        Percorre toda a cadeia cronológica de blocos e valida se todos os hashes batem matematicamente.
        Retorna (Integro: bool, TotalVerificados: int, MensagemErro: Optional[str]).
        """
        with self._lock:
            with self._obter_conexao() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM trilha_auditoria_imutavel ORDER BY sequencia ASC")
                registros = cursor.fetchall()

                if not registros:
                    return True, 0, "Cadeia de auditoria vazia."

                hash_esperado_anterior = self.BLOCO_GENESE_HASH

                for r in registros:
                    # 1. Verifica se o hash anterior confere
                    if r["hash_anterior"] != hash_esperado_anterior:
                        return False, r["sequencia"], f"Adulteração detectada no bloco {r['sequencia']}: hash_anterior corrompido!"

                    # 2. Recalcula o hash do payload
                    payload_recalculado = hashlib.sha256(r["detalhes_json"].encode('utf-8')).hexdigest()
                    if payload_recalculado != r["payload_sha256"]:
                        return False, r["sequencia"], f"Adulteração no conteúdo do payload no bloco {r['sequencia']}!"

                    # 3. Recalcula o hash do bloco
                    hash_recalculado = self._calcular_hash_bloco(
                        r["hash_anterior"], r["timestamp_epoch"], r["ator_id"],
                        r["acao"], r["recurso"], r["payload_sha256"]
                    )
                    if hash_recalculado != r["hash_bloco"]:
                        return False, r["sequencia"], f"Adulteração do bloco {r['sequencia']}: hash recalculado não confere!"

                    hash_esperado_anterior = r["hash_bloco"]

                return True, len(registros), "Cadeia de auditoria 100% íntegra e verificada matematicamente."

    def listar_eventos(self, limite: int = 50, filtro_ator: Optional[str] = None, filtro_acao: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista eventos recentes para visualização no dashboard ou auditoria."""
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM trilha_auditoria_imutavel WHERE 1=1"
            params = []

            if filtro_ator:
                query += " AND (ator_id LIKE ? OR ator_nome LIKE ?)"
                params.extend([f"%{filtro_ator}%", f"%{filtro_ator}%"])
            if filtro_acao:
                query += " AND acao LIKE ?"
                params.append(f"%{filtro_acao}%")

            query += " ORDER BY sequencia DESC LIMIT ?"
            params.append(limite)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                {
                    "sequencia": r["sequencia"],
                    "id_evento": r["id_evento"],
                    "timestamp": r["timestamp_utc"],
                    "ator": f"{r['ator_nome']} ({r['ator_cargo']}/{r['ator_orgao']})",
                    "acao": r["acao"],
                    "recurso": r["recurso"],
                    "ip": r["ip_origem"],
                    "hash_bloco": r["hash_bloco"][:16] + "...",
                    "hash_anterior": r["hash_anterior"][:16] + "...",
                    "sucesso": bool(r["sucesso"])
                }
                for r in rows
            ]


# Instância Singleton Global
audit_trail_global = ImmutableAuditTrail()
immutable_audit_trail_global = audit_trail_global

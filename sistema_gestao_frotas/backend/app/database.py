# -*- coding: utf-8 -*-
"""
================================================================================
CAMADA DE DADOS MONGODB / PERSISTÊNCIA DOCUMENTAL (PPGCAP/UDESC)
Suporta conexão com MongoDB Server (local/Atlas) ou Mongita embutido em disco.
Compatibilidade garantida para Linux e Windows com zero setup manual obrigatório.
================================================================================
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from bson import ObjectId

try:
    from app.config import get_settings
except ImportError:
    from sistema_gestao_frotas.backend.app.config import get_settings

logger = logging.getLogger("FleetDatabase")
settings = get_settings()

def init_db():
    """Inicializa conexão com MongoDB / Mongita e garante índices."""
    return get_database()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DISK_DATA_DIR = BASE_DIR / "dados" / "mongodb_data"
DISK_DATA_DIR.mkdir(parents=True, exist_ok=True)

_mongo_client = None
_database = None
_is_standalone_mongita = False


def get_database():
    """
    Retorna a instância conectada do banco de dados MongoDB ou Mongita embutido.
    Inicialização resiliente e com failover automático.
    """
    global _mongo_client, _database, _is_standalone_mongita

    if _database is not None:
        return _database

    uri = (settings.MONGODB_URI or "").strip()

    # 1. Tentativa de conexão com MongoDB Server (se URI configurada)
    if uri:
        try:
            from pymongo import MongoClient
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            _mongo_client = client
            _database = client[settings.MONGODB_DB_NAME]
            _is_standalone_mongita = False
            logger.info(f"Conectado com sucesso ao MongoDB Server: {uri.split('@')[-1]}")
            _create_indexes(_database)
            return _database
        except Exception as e:
            logger.warning(f"MongoDB Server indisponível em '{uri}' ({e}). Ativando motor embutido Mongita...")

    # 2. Inicialização do motor embutido Mongita (100% autônomo em disco)
    try:
        import mongita
        _mongo_client = mongita.MongitaClientDisk(path=str(DISK_DATA_DIR))
        _database = _mongo_client[settings.MONGODB_DB_NAME]
        _is_standalone_mongita = True
        logger.info(f"Motor MongoDB embutido (Mongita) inicializado em: {DISK_DATA_DIR}")
        _create_indexes(_database)
        return _database
    except Exception as e:
        logger.error(f"Falha crítica ao inicializar Mongita: {e}")
        raise RuntimeError("Não foi possível inicializar nenhuma instância de MongoDB ou Mongita.")


def is_using_standalone_engine() -> bool:
    """Informa se está utilizando o motor embutido Mongita ou servidor MongoDB externo."""
    return _is_standalone_mongita


def _create_indexes(db):
    """Cria índices para otimização de consultas e unicidade."""
    try:
        db['usuarios'].create_index("username", unique=True)
        db['usuarios'].create_index("cpf", unique=True)
        db['usuarios'].create_index("email", unique=True)
        db['users'].create_index("username", unique=True)
        db['users'].create_index("cpf", unique=True)
        db['users'].create_index("email", unique=True)
        db['veiculos'].create_index("placa", unique=True)
        db['veiculos'].create_index("chassi", unique=True)
        db['motoristas'].create_index("cpf", unique=True)
        db['motoristas'].create_index("cnh_numero", unique=True)
        db['api_keys'].create_index("hashed_key", unique=True)
        db['telemetria_eventos'].create_index([("veiculo_id", 1), ("timestamp", -1)])
        db['ordens_servico'].create_index("numero_os", unique=True)
        db['cercas_eletronicas'].create_index("nome", unique=True)

    except Exception as e:
        # Mongita suporta índices básicos, ignoramos avisos de duplicidade de índice
        logger.debug(f"Nota na criação de índices: {e}")


def format_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Converte ObjectId para string 'id' em documentos serializados."""
    if not doc:
        return None
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


def format_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converte lista de documentos normalizando '_id' para 'id'."""
    return [format_doc(d) for d in docs if d]

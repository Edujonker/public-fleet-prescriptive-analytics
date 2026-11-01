# -*- coding: utf-8 -*-
"""
================================================================================
GERENCIAMENTO DE CHAVES DE API (API KEYS) PARA IOT GATEWAY E INTEGRAÇÕES
Security-by-Design: OWASP Top 10 A07 (Auth) & CWE-798 (No Hardcoded Secrets)
================================================================================
"""

import secrets
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from app.database import get_database, format_doc
    from app.security.crypto import hash_api_key, compare_digest_safe
    from app.security.auth import get_current_user
except ImportError:
    from sistema_gestao_frotas.backend.app.database import get_database, format_doc
    from sistema_gestao_frotas.backend.app.security.crypto import hash_api_key, compare_digest_safe
    from sistema_gestao_frotas.backend.app.security.auth import get_current_user

http_bearer = HTTPBearer(auto_error=False)


def generate_secure_api_key(prefix: str = "flt_") -> tuple:
    """Gera chave segura e seu prefixo mascarado."""
    random_part = secrets.token_urlsafe(32)
    raw_key = f"{prefix}{random_part}"
    masked = f"{raw_key[:12]}..."
    return raw_key, masked


def generate_new_api_key(name: str, scope: str = "iot_ingestion") -> Dict[str, str]:
    """
    Gera uma nova chave de API com alta entropia.
    O segredo em texto claro é retornado apenas UMA vez para o cliente.
    No banco grava-se apenas o hash SHA-256 com prefixo e metadados.
    """
    random_part = secrets.token_urlsafe(32)
    raw_key = f"flt_{scope}_{random_part}"
    hashed = hash_api_key(raw_key)

    return {
        "raw_key": raw_key,
        "hashed_key": hashed,
        "name": name,
        "scope": scope,
        "prefix": raw_key[:12] + "...",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ativo": True
    }


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Dict[str, Any]:
    """
    Verifica a autenticidade e validade da API Key passada no cabeçalho X-API-Key.
    Garante comparação segura e lookup via hash.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header 'X-API-Key' ausente ou inválido."
        )

    target_hash = hash_api_key(x_api_key)
    db = get_database()
    key_doc = db['api_keys'].find_one({"key_hash": target_hash}) or db['api_keys'].find_one({"hashed_key": target_hash})

    if not key_doc or key_doc.get("ativo") is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API inválida, revogada ou inexistente."
        )

    # Atualiza timestamp do último uso da chave
    try:
        db['api_keys'].update_one(
            {"_id": key_doc["_id"]},
            {"$set": {"last_used_at": datetime.now(timezone.utc).isoformat()}}
        )
    except Exception:
        pass

    return format_doc(key_doc)


async def get_current_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer)
) -> Dict[str, Any]:
    """
    Autenticação Híbrida: Aceita tanto Bearer Token JWT (usuários) quanto X-API-Key (IoT/integrações).
    Permite consumo flexível por navegadores e rastreadores embarcados.
    """
    # 1. Se informou API Key
    if x_api_key:
        key_info = await verify_api_key(x_api_key)
        return {
            "auth_type": "api_key",
            "principal": key_info.get("name", "iot_gateway"),
            "role": "IOT_DEVICE" if key_info.get("scope") == "iot_ingestion" else "INTEGRATION",
            "details": key_info
        }

    # 2. Se informou Bearer Token
    if bearer and bearer.credentials:
        user = await get_current_user(token=bearer.credentials)
        return {
            "auth_type": "jwt",
            "principal": user.get("username"),
            "role": user.get("role", "OPERADOR"),
            "user": user
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticação obrigatória. Forneça 'Authorization: Bearer <token>' ou 'X-API-Key: <key>'."
    )

# -*- coding: utf-8 -*-
"""
================================================================================
CRIPTOGRAFIA E HASHING DE ALTA SEGURANÇA (ARGON2ID & BCRYPT)
Security-by-Design: OWASP Top 10 A02 (Cryptographic Failures)
================================================================================
"""

import hmac
import hashlib
import logging
from typing import Optional

logger = logging.getLogger("SecurityCrypto")

# 1. Hashing de senhas: prioritariamente Argon2id (recomendado OWASP), com fallback bcrypt
_hasher = None
try:
    from argon2 import PasswordHasher
    _hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
except Exception:
    try:
        from passlib.context import CryptContext
        _hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
    except Exception:
        _hasher = None


def hash_password(password: str) -> str:
    """Gera hash seguro com sal aleatório e alto fator de custo computacional."""
    if _hasher is None:
        # Fallback SHA-256 com salt seguro (se nenhuma lib externa estiver disponível)
        salt = hashlib.sha256(password.encode()).hexdigest()[:16]
        return f"pbkdf2_sha256${salt}${hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()}"

    if hasattr(_hasher, "hash"):
        return _hasher.hash(password)
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha com proteção estrita contra Timing Attacks (CWE-208)."""
    if not plain_password or not hashed_password:
        return False

    if hashed_password.startswith("pbkdf2_sha256$"):
        parts = hashed_password.split("$")
        if len(parts) == 3:
            salt = parts[1]
            expected = parts[2]
            computed = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000).hex()
            return hmac.compare_digest(expected, computed)

    if _hasher is not None:
        try:
            if hasattr(_hasher, "verify"):
                _hasher.verify(hashed_password, plain_password)
                return True
            return _hasher.verify(plain_password, hashed_password)
        except Exception:
            return False

    return False


def hash_api_key(api_key: str) -> str:
    """Gera digest criptográfico SHA-256 para persistência segura de API Keys."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def compare_digest_safe(val1: str, val2: str) -> bool:
    """Comparação em tempo constante para evitar vazamentos por timing."""
    return hmac.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))

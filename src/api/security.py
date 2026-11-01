# -*- coding: utf-8 -*-
"""
================================================================================
AUTENTICAÇÃO, CRIPTOGRAFIA E CONTROLE DE ACESSO RBAC (PPGCAP/UDESC)
SECURITY-BY-DESIGN: OAUTH2, JWT (HS256) E BCRYPT (OWASP A01 & A07)
================================================================================
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.config import Settings, get_settings
from src.api.models import User

logger = logging.getLogger("SecurityModule")

# Algoritmo seguro para senhas: Argon2id (OWASP Top 10 recomendado via argon2-cffi)
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, InvalidHashError
    _ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
except ImportError:
    _ph = None

# Esquema OAuth2 Password Bearer para injeção via Depends
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
    description="Insira o Bearer token obtido no endpoint de autenticação."
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha utilizando Argon2id com proteção contra timing attacks."""
    if _ph is not None:
        try:
            return _ph.verify(hashed_password, plain_password)
        except Exception:
            return False
    # Fallback seguro
    return False


def get_password_hash(password: str) -> str:
    """Gera hash seguro Argon2id com sal aleatório e alto custo de memória."""
    if _ph is not None:
        return _ph.hash(password)
    raise RuntimeError("argon2-cffi não está disponível para hash de senhas.")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, settings: Optional[Settings] = None) -> str:
    """
    Emite token JWT com algoritmo HMAC-SHA256 (HS256), tempo de expiração curto
    e assinatura criptográfica verificável.
    """
    if settings is None:
        settings = get_settings()

    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now_utc,
        "nbf": now_utc
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str, settings: Settings) -> dict:
    """
    Decodifica e valida assinatura e expiração do JWT.
    Lança HTTPException padronizada sem expor detalhes internos.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token de autenticação expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload
    except JWTError as e:
        logger.warning(f"Falha de validação do token JWT: {e}")
        raise credentials_exception


async def get_current_user_dependency(
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
    # db é injetado dinamicamente para evitar import circular
) -> dict:
    """Valida o token JWT e retorna o payload do usuário autenticado."""
    payload = decode_access_token(token, settings)
    return payload


class RequireRole:
    """
    Dependência reutilizável para Role-Based Access Control (RBAC).
    Garante o princípio do menor privilégio (PoLP).
    """

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_payload: dict = Depends(get_current_user_dependency)) -> dict:
        user_role = current_payload.get("role", "pesquisador")
        if user_role not in self.allowed_roles:
            logger.warning(
                f"Acesso negado para usuário '{current_payload.get('sub')}': "
                f"papel '{user_role}' não autorizado para recursos restritos a {self.allowed_roles}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para executar esta operação."
            )
        return current_payload

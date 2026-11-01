# -*- coding: utf-8 -*-
"""
================================================================================
AUTENTICAÇÃO JWT E CONTROLE DE ACESSO RBAC (PPGCAP/UDESC)
Security-by-Design: OWASP Top 10 A01 (Broken Access Control) & A07 (Auth)
Perfis: ADMIN, GESTOR_FROTA, OPERADOR, MOTORISTA, AUDITOR
================================================================================
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

try:
    from app.config import get_settings
    from app.database import get_database, format_doc
except ImportError:
    from sistema_gestao_frotas.backend.app.config import get_settings
    from sistema_gestao_frotas.backend.app.database import get_database, format_doc

logger = logging.getLogger("SecurityAuth")
settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    description="Insira o Bearer token JWT obtido no login."
)

# Perfis válidos do sistema (RBAC)
ROLES_ALLOWED = [
    "ADMIN",           # Acesso total, configurações, gestão de usuários e API keys
    "GESTOR_FROTA",    # Aprovação de viagens, orçamentos, manutenções e cadastros
    "OPERADOR",        # Despacho diário, registro de abastecimento e OS
    "MOTORISTA",       # Execução de checklists e visualização de viagens atribuídas
    "AUDITOR"          # Leitura exclusiva, conformidade e relatórios analíticos
]


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Emite token JWT com algoritmo HMAC-SHA256, tempo de vida curto e claims completas."""
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    expire = now_utc + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({
        "exp": expire,
        "iat": now_utc,
        "nbf": now_utc,
        "iss": "sistema_gestao_frotas"
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Valida assinatura e expiração do JWT. Erros genéricos sem vazamento de stack."""
    cred_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou sessão expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise cred_exception
        return payload
    except JWTError:
        raise cred_exception


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Injeta o usuário logado com validação ativa na base de dados MongoDB."""
    payload = decode_access_token(token)
    username = payload.get("sub")

    db = get_database()
    user = db['users'].find_one({"username": username, "ativo": True})
    if not user:
        user = db['usuarios'].find_one({"username": username, "ativo": True})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inexistente ou inativado pelo administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return format_doc(user)


class RequireRole:
    """Dependência para controle de permissões por perfil (RBAC)."""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [r.upper() for r in allowed_roles]

    def __call__(self, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = (current_user.get("role") or "").upper()
        if user_role not in self.allowed_roles:
            logger.warning(
                f"Acesso negado: Usuário '{current_user.get('username')}' com papel '{user_role}' "
                f"tentou acessar recurso exclusivo para {self.allowed_roles}."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito. Esta operação requer perfil: {', '.join(self.allowed_roles)}."
            )
        return current_user

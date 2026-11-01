"""
Rotas de Autenticação, Usuários (RBAC) e Gerenciamento de Chaves de API IoT.
"""

from typing import List, Dict, Any
import re
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.database import get_database
from app.config import get_settings
from app.security.crypto import hash_password, verify_password, hash_api_key
from app.security.auth import create_access_token, get_current_user, RequireRole
from app.security.api_keys import generate_secure_api_key
from app.models.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserRole,
    APIKeyCreate,
    APIKeyResponse
)

router = APIRouter(prefix="/api/auth", tags=["Autenticação & Segurança"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """
    Autentica usuário utilizando CPF ou Nome de Usuário (username).
    Validação estrita com senha criptografada Argon2id e geração de JWT.
    """
    db = get_database()
    settings = get_settings()

    identificador = request.username.strip()
    cpf_limpo = re.sub(r'\D', '', identificador)
    cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}" if len(cpf_limpo) == 11 else None

    # Busca sequencial resiliente (compatível 100% com Mongita Disk e MongoDB Server)
    user = db.users.find_one({"username": identificador})
    if not user:
        user = db.users.find_one({"cpf": identificador})
    if not user and cpf_limpo:
        user = db.users.find_one({"cpf": cpf_limpo})
    if not user and cpf_formatado:
        user = db.users.find_one({"cpf": cpf_formatado})
    if not user:
        user = db.users.find_one({"username": identificador.lower()})

    if not user and hasattr(db, "usuarios"):
        user = db.usuarios.find_one({"username": identificador})
        if not user:
            user = db.usuarios.find_one({"cpf": identificador})
        if not user and cpf_limpo:
            user = db.usuarios.find_one({"cpf": cpf_limpo})
        if not user and cpf_formatado:
            user = db.usuarios.find_one({"cpf": cpf_formatado})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas: CPF/usuário não cadastrado ou senha incorreta."
        )


    if not user.get("ativo", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o administrador do FROTAGOV."
        )

    # Validar senha criptografada via Argon2id (ou fallback seguro)
    if not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas: CPF/usuário não cadastrado ou senha incorreta."
        )

    # Atualizar last_login
    agora_iso = datetime.now(timezone.utc).isoformat()
    db.users.update_one({"id": user["id"]}, {"$set": {"last_login": agora_iso}})
    if hasattr(db, "usuarios"):
        db.usuarios.update_one({"id": user["id"]}, {"$set": {"last_login": agora_iso}})

    # Gerar token JWT
    token = create_access_token(

        data={"sub": user["username"], "role": user.get("role", UserRole.OPERADOR.value)}
    )

    user_info = {
        "id": user["id"],
        "username": user["username"],
        "nome_completo": user.get("nome_completo", user["username"]),
        "email": user.get("email"),
        "role": user.get("role"),
        "cargo": user.get("cargo"),
        "departamento": user.get("departamento")
    }

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=user_info
    )


@router.get("/me")
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retorna dados do perfil do usuário autenticado."""
    u = dict(current_user)
    u.pop("password_hash", None)
    u.pop("_id", None)
    return u


@router.post("/api-keys", response_model=APIKeyResponse, dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_api_key(dados: APIKeyCreate):
    """
    Gera uma chave de API criptografada para integração de hardware/rastreadores IoT.
    A chave completa é retornada apenas uma única vez na resposta.
    """
    db = get_database()
    chave_completa, prefix = generate_secure_api_key("flt_")
    key_hash = hash_api_key(chave_completa)
    agora_iso = datetime.now(timezone.utc).isoformat()
    key_id = str(uuid.uuid4())

    doc = {
        "id": key_id,
        "prefix": prefix,
        "nome_dispositivo": dados.nome_dispositivo,
        "descricao": dados.descricao,
        "key_hash": key_hash,
        "role": dados.role.value,
        "created_at": agora_iso
    }
    db.api_keys.insert_one(doc)

    return APIKeyResponse(
        id=key_id,
        prefix=prefix,
        nome_dispositivo=dados.nome_dispositivo,
        descricao=dados.descricao,
        created_at=agora_iso,
        api_key_completa=chave_completa
    )


@router.get("/api-keys", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def list_api_keys():
    """Lista chaves de API cadastradas com hashes ocultos."""
    db = get_database()
    cursor = db.api_keys.find({})
    keys = []
    for doc in cursor:
        doc.pop("_id", None)
        doc.pop("key_hash", None)
        keys.append(doc)
    return keys


@router.get("/users", dependencies=[Depends(RequireRole([UserRole.ADMIN]))])
def list_users():
    """Lista todos os usuários cadastrados no sistema (Acesso restrito ADMIN)."""
    db = get_database()
    cursor = db.users.find({})
    users = []
    for doc in cursor:
        doc.pop("_id", None)
        doc.pop("password_hash", None)
        users.append(doc)
    return users


@router.post("/users", dependencies=[Depends(RequireRole([UserRole.ADMIN]))])
def create_user(dados: UserCreate):
    """Cadastra novo usuário no sistema com role RBAC (Acesso restrito ADMIN)."""
    db = get_database()
    if db.users.find_one({"username": dados.username}):
        raise HTTPException(status_code=400, detail="Nome de usuário já existe.")
    if db.users.find_one({"email": dados.email}):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    
    cpf_limpo = re.sub(r'\D', '', dados.cpf)
    if db.users.find_one({"$or": [{"cpf": dados.cpf}, {"cpf": cpf_limpo}]}):
        raise HTTPException(status_code=400, detail="CPF já cadastrado no sistema.")


    agora_iso = datetime.now(timezone.utc).isoformat()
    user_id = str(uuid.uuid4())

    doc = dados.model_dump()
    doc["id"] = user_id
    doc["password_hash"] = hash_password(dados.password)
    doc.pop("password")
    doc["ativo"] = True
    doc["created_at"] = agora_iso
    doc["last_login"] = None

    db.users.insert_one(doc)
    doc.pop("_id", None)
    doc.pop("password_hash", None)
    return doc

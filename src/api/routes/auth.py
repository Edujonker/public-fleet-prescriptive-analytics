# -*- coding: utf-8 -*-
"""
================================================================================
ROTAS DE AUTENTICAÇÃO E GESTÃO DE USUÁRIOS (PPGCAP/UDESC)
SECURITY-BY-DESIGN: OAUTH2, JWT, HASHING BCRYPT & RBAC (OWASP A01 & A07)
================================================================================
"""

import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.config import Settings, get_settings
from src.api.database import get_db
from src.api.models import User, AuditLog
from src.api.schemas import (
    UserLoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse
)
from src.api.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user_dependency,
    RequireRole
)

logger = logging.getLogger("AuthRouter")
router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/token", response_model=TokenResponse, summary="Obter token JWT via OAuth2 Password Flow")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """
    Endpoint OAuth2 compatível com documentação OpenAPI Swagger UI.
    Utiliza consultas parametrizadas com bind seguro via SQLAlchemy 2.0 (CWE-89).
    """
    # Consulta segura e parametrizada via SQLAlchemy 2.0
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Falha de autenticação para o usuário: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário inativa."
        )

    # Registro na trilha de auditoria
    audit_entry = AuditLog(
        username=user.username,
        action="LOGIN_SUCCESS",
        details="Login autenticado via OAuth2 Password Flow"
    )
    db.add(audit_entry)
    await db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "email": user.email},
        expires_delta=access_token_expires,
        settings=settings
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        role=user.role
    )


@router.post("/login", response_model=TokenResponse, summary="Login seguro via payload JSON estrito")
async def login_json(
    credentials: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Endpoint de login autenticado via Pydantic schema estrito (Anti-Injection)."""
    query = select(User).where(User.username == credentials.username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Tentativa de login inválida: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário inativa."
        )

    client_ip = request.client.host if request.client else "unknown"
    db.add(AuditLog(
        username=user.username,
        action="LOGIN_JSON",
        details="Login autenticado via JSON",
        ip_address=client_ip
    ))
    await db.commit()

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        settings=settings
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        role=user.role
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar novo usuário (Apenas Admin)")
async def register_user(
    new_user_data: UserCreateRequest,
    current_payload: dict = Depends(RequireRole(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Criação de novos usuários restrita a administradores (RBAC estrito).
    Evita vazamento de senha retornando estritamente UserResponse.
    """
    # Verifica unicidade de username e email
    check_query = select(User).where(
        (User.username == new_user_data.username) | (User.email == new_user_data.email)
    )
    existing = (await db.execute(check_query)).scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de usuário ou e-mail já registrado."
        )

    user = User(
        username=new_user_data.username,
        email=new_user_data.email,
        hashed_password=get_password_hash(new_user_data.password),
        role=new_user_data.role,
        is_active=True
    )
    db.add(user)
    db.add(AuditLog(
        username=current_payload.get("sub", "admin"),
        action="USER_CREATED",
        details=f"Novo usuário criado: {new_user_data.username} (role: {new_user_data.role})"
    ))
    await db.commit()
    await db.refresh(user)

    return user


@router.get("/me", response_model=UserResponse, summary="Dados do usuário logado (Anti-Data Leakage)")
async def get_me(
    current_payload: dict = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Retorna os dados cadastrais do usuário autenticado sem expor campos sensíveis."""
    username = current_payload.get("sub")
    query = select(User).where(User.username == username)
    user = (await db.execute(query)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não localizado.")
    return user

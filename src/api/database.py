# -*- coding: utf-8 -*-
"""
================================================================================
GERENCIADOR DE PERSISTÊNCIA ASSÍNCRONA ORM (PPGCAP/UDESC)
SECURITY-BY-DESIGN: SQLALCHEMY 2.0 ASYNC SESSION & PARAMETER BINDING (CWE-89)
================================================================================
"""

import logging
from typing import AsyncGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.api.config import get_settings
from src.api.models import Base, User
from src.api.security import get_password_hash

logger = logging.getLogger("DatabaseManager")
settings = get_settings()

# Engine assíncrona do SQLAlchemy 2.0 com pool seguro
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Fabrica de sessões assíncronas isoladas por requisição
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provedor de sessão de banco de dados assíncrona injetável via Depends().
    Garante rollback automático em exceções e fechamento de conexões.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Rollback disparado por erro na transação de banco: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Inicializa esquemas de tabelas e insere usuário administrativo inicial se inexistente."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Inicialização segura de usuário administrador
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == settings.ADMIN_DEFAULT_USERNAME)
        )
        existing_admin = result.scalars().first()

        if not existing_admin:
            logger.info("Criando usuário administrativo padrão via hashing bcrypt...")
            admin_user = User(
                username=settings.ADMIN_DEFAULT_USERNAME,
                email=settings.ADMIN_DEFAULT_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_DEFAULT_PASSWORD),
                role="admin",
                is_active=True
            )
            session.add(admin_user)

            # Cria também um pesquisador padrão para testes de acesso auditado
            pesquisador_user = User(
                username="pesquisador_ppgcap",
                email="pesquisador@udesc.br",
                hashed_password=get_password_hash("Pesquisador@PPGCAP2026!"),
                role="pesquisador",
                is_active=True
            )
            session.add(pesquisador_user)
            await session.commit()
            logger.info("Usuários seguros criados com sucesso.")

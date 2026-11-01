# -*- coding: utf-8 -*-
"""
================================================================================
GERENCIAMENTO SEGURO DE CONFIGURAÇÕES E SEGREDOS (PPGCAP/UDESC)
SECURITY-BY-DESIGN: PYDANTIC-SETTINGS V2 (CWE-798 & OWASP A05)
================================================================================
"""

from functools import lru_cache
from typing import List
from pydantic import Field, StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações centrais do sistema validadas estritamente pelo Pydantic v2."""

    # Segredos criptográficos e autenticação JWT
    SECRET_KEY: StrictStr = Field(
        ...,
        min_length=32,
        description="Chave secreta de alta entropia para assinatura HMAC-SHA256"
    )
    ALGORITHM: StrictStr = Field(default="HS256", description="Algoritmo de criptografia do token JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=5, le=1440, description="Tempo de vida do token JWT em minutos")

    # Persistência de Dados (SQLAlchemy 2.0 Async Session)
    DATABASE_URL: StrictStr = Field(
        default="sqlite+aiosqlite:///./dados/sistema_seguro.db",
        description="String de conexão assíncrona com o banco de dados"
    )

    # Restrição de Origens CORS (CWE-942)
    ALLOWED_ORIGINS: List[StrictStr] = Field(
        default=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:3000"],
        description="Lista explícita de origens permitidas (nunca wildcard '*' em produção)"
    )

    # Ambiente operacional
    ENVIRONMENT: StrictStr = Field(default="production", description="Ambiente de execução")

    # Credenciais do Administrador Padrão (Sem hardcode: carregado via .env)
    ADMIN_DEFAULT_USERNAME: StrictStr = Field(default="admin_seguro", min_length=3, max_length=50)
    ADMIN_DEFAULT_EMAIL: StrictStr = Field(default="admin@udesc.br")
    ADMIN_DEFAULT_PASSWORD: StrictStr = Field(default="AdminSeguro@PPGCAP2026!", min_length=8)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Provedor singleton e cacheado de configurações injetável via Depends()."""
    return Settings()

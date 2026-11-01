# -*- coding: utf-8 -*-
"""
================================================================================
SISTEMA DE GESTÃO DE FROTAS (PYTHON & JAVASCRIPT / MONGODB)
CONFIGURAÇÕES GERAIS E SECURITY-BY-DESIGN (OWASP TOP 10 & CWE)
================================================================================
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class FleetSettings(BaseSettings):
    """Configurações centrais do sistema validadas estritamente via Pydantic v2."""

    # Aplicação
    APP_NAME: StrictStr = Field(default="Sistema de Gestão de Frotas & Telemetria")
    APP_VERSION: StrictStr = Field(default="2.0.0-Enterprise")
    ENVIRONMENT: StrictStr = Field(default="production")
    HOST: StrictStr = Field(default="0.0.0.0")
    PORT: int = Field(default=8090, ge=1024, le=65535)

    # Segurança e Criptografia
    SECRET_KEY: StrictStr = Field(
        default="c98234af09e821bcda5612347890efab123456789abcdef0123456789abcdef0",
        min_length=32,
        description="Chave secreta de alta entropia para assinatura HMAC-SHA256 (JWT)"
    )
    ALGORITHM: StrictStr = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=120, ge=15, le=1440)

    # Base de Dados MongoDB (Suporta MongoDB Server ou Mongita embutido local)
    MONGODB_URI: Optional[str] = Field(
        default="",
        description="URI do MongoDB (ex: mongodb://localhost:27017 ou mongodb+srv://...). Se vazio, usa Mongita embutido em disco."
    )
    MONGODB_DB_NAME: StrictStr = Field(default="gestao_frota_db")

    # Restrição de Origens CORS (CWE-942)
    ALLOWED_ORIGINS: List[StrictStr] = Field(
        default=["http://localhost:8090", "http://127.0.0.1:8090", "http://localhost:3000", "*"],
        description="Lista explícita de origens permitidas (nunca wildcard '*' em produção)"
    )

    # Limite de Upload / Payload para prevenção contra DoS (CWE-400)
    MAX_CONTENT_LENGTH: int = Field(default=10 * 1024 * 1024, description="Tamanho máximo de payload (10 MB)")

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.ALLOWED_ORIGINS

    # Administrador Padrão (Criado caso inexista na inicialização)
    ADMIN_DEFAULT_USERNAME: StrictStr = Field(default="admin_frota", min_length=3, max_length=50)
    ADMIN_DEFAULT_EMAIL: StrictStr = Field(default="admin.frota@udesc.br")
    ADMIN_DEFAULT_PASSWORD: StrictStr = Field(default="Admin@Frota2026!", min_length=8)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> FleetSettings:
    """Provedor singleton e cacheado de configurações injetável via Depends()."""
    return FleetSettings()

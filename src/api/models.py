# -*- coding: utf-8 -*-
"""
================================================================================
MODELOS DE DADOS ORM (PPGCAP/UDESC)
SECURITY-BY-DESIGN: SQLALCHEMY 2.0 DECLARATIVE MAPPING (CWE-89)
================================================================================
"""

from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Classe base declarativa do SQLAlchemy 2.0."""
    pass


class User(Base):
    """Modelo de usuário com suporte a RBAC (Role-Based Access Control)."""
    __tablename__ = "usuarios_seguros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="pesquisador", nullable=False)  # admin, auditor, pesquisador
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    """Registro de trilha de auditoria para ações sensíveis (OWASP A09)."""
    __tablename__ = "trilha_auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class QueryRecord(Base):
    """Histórico estruturado de consultas submetidas ao Copiloto de IA."""
    __tablename__ = "historico_consultas_ia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    pergunta: Mapped[str] = mapped_column(String(1000), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)
    sucesso: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

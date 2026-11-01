# -*- coding: utf-8 -*-
"""
================================================================================
ESQUEMAS DE VALIDAÇÃO E MODELAGEM DE DADOS (PPGCAP/UDESC)
SECURITY-BY-DESIGN: PYDANTIC V2 STRICT VALIDATION & ANTI-DATA LEAKAGE (CWE-200)
================================================================================
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, StrictStr, EmailStr, ConfigDict


# ------------------------------------------------------------------------------
# 1. ESQUEMAS DE AUTENTICAÇÃO E USUÁRIOS
# ------------------------------------------------------------------------------

class UserLoginRequest(BaseModel):
    """Schema estrito para login com credenciais de acesso."""
    model_config = ConfigDict(strict=True, extra="forbid")

    username: StrictStr = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_\-\.]+$",
        description="Identificador alfanumérico seguro do usuário"
    )
    password: StrictStr = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Senha com comprimento mínimo obrigatório de 8 caracteres"
    )


class TokenResponse(BaseModel):
    """Schema de resposta com o JWT emitido e tempo de expiração."""
    model_config = ConfigDict(strict=True)

    access_token: StrictStr
    token_type: StrictStr = "bearer"
    expires_in_minutes: int
    role: StrictStr


class UserCreateRequest(BaseModel):
    """Schema para cadastro de novos usuários com tipagem estrita."""
    model_config = ConfigDict(strict=True, extra="forbid")

    username: StrictStr = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_\-\.]+$"
    )
    email: EmailStr
    password: StrictStr = Field(
        ...,
        min_length=8,
        max_length=128
    )
    role: StrictStr = Field(
        default="pesquisador",
        pattern=r"^(admin|auditor|pesquisador)$"
    )


class UserResponse(BaseModel):
    """
    Schema de saída para usuários (Anti-Data Leakage).
    NUNCA inclui 'hashed_password' nem segredos internos.
    """
    model_config = ConfigDict(from_attributes=True, strict=True)

    id: int
    username: StrictStr
    email: EmailStr
    role: StrictStr
    is_active: bool
    created_at: datetime


# ------------------------------------------------------------------------------
# 2. ESQUEMAS DO COPILOTO DE IA E CONSULTAS
# ------------------------------------------------------------------------------

class ChatQueryRequest(BaseModel):
    """Schema estrito de requisição para o motor de PLN e Assistente de IA."""
    model_config = ConfigDict(strict=True, extra="forbid")

    mensagem: StrictStr = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Pergunta ou comando em linguagem natural limitado a 1000 caracteres (anti-ReDoS)"
    )


class ChatQueryResponse(BaseModel):
    """Schema estrito de resposta das análises do Copiloto de IA."""
    model_config = ConfigDict(strict=True)

    resposta: StrictStr
    categoria: StrictStr
    sucesso: bool
    figura_relacionada: Optional[StrictStr] = None
    topico: Optional[StrictStr] = None


# ------------------------------------------------------------------------------
# 3. ESQUEMAS OPERACIONAIS: PIPELINE E RELATÓRIO
# ------------------------------------------------------------------------------

class PipelineUpdateRequest(BaseModel):
    """Schema parametrizado para recalcular o pipeline metodológico e gráficos."""
    model_config = ConfigDict(strict=True, extra="forbid")

    alpha: float = Field(
        default=0.05,
        ge=0.001,
        le=0.20,
        description="Nível de significância estatística (ex: 0.05 para 95% de confiança)"
    )
    frequencia: StrictStr = Field(
        default="ME",
        pattern=r"^(D|W|ME|MS|Q|Y)$",
        description="Frequência temporal de amostragem (D=diário, W=semanal, ME=mensal)"
    )
    horizonte: int = Field(
        default=6,
        ge=1,
        le=36,
        description="Horizonte de previsão temporal em períodos"
    )
    modo_hipotese: StrictStr = Field(
        default="auto",
        pattern=r"^(auto|parametrico|nao_parametrico)$",
        description="Estratégia de seleção de testes de hipóteses"
    )


class PipelineUpdateResponse(BaseModel):
    """Schema de confirmação da atualização do pipeline."""
    model_config = ConfigDict(strict=True)

    status: StrictStr
    mensagem: StrictStr
    parametros: Dict[str, Any]


class ReportGenerateResponse(BaseModel):
    """Schema de retorno da compilação do relatório oficial em PDF."""
    model_config = ConfigDict(strict=True)

    status: StrictStr
    mensagem: StrictStr
    caminho_relatorio: Optional[StrictStr] = None
    tamanho_mb: Optional[float] = None


class StatusResponse(BaseModel):
    """Schema de auditoria e status de integridade do sistema."""
    model_config = ConfigDict(strict=True)

    servidor: StrictStr
    versao: StrictStr
    ai_assistant: StrictStr
    total_consultas: int
    pdf_existe: bool
    ambiente: StrictStr


class CommercialSummaryResponse(BaseModel):
    """Schema estrito para indicadores comerciais e de gestão de frotas (Anti-Data Leakage)."""
    model_config = ConfigDict(strict=True)

    total_gasto_auditado: float
    total_ordens_servico: int
    total_veiculos_unicos: int
    percentual_corretivas: float
    percentual_pecas_custo: float
    economia_potencial_procurement_anual: float
    ponto_otimo_renovacao_anos: int
    quilometragem_troca_km: int
    top_item_pareto: StrictStr
    economia_prescritiva_milp: float


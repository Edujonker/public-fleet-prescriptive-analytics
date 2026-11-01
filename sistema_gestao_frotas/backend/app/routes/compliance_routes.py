"""
Rotas para Compliance, Gestão de Multas, Workflow de Indicação de Condutor e Vencimentos Legais.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.security.auth import RequireRole
from app.models.schemas import (
    UserRole,
    MultaCreate,
    IndicarCondutorRequest,
    SinistroCreate,
    DocumentoVencimentoCreate
)
from app.services.compliance_service import compliance_service

router = APIRouter(prefix="/api/compliance", tags=["Compliance, Multas & Sinistros"])


@router.get("/fines")
def list_multas(placa: Optional[str] = None, pendente_indicacao: bool = False):
    """Lista autuações de trânsito e status da indicação do condutor."""
    return compliance_service.listar_multas(placa=placa, pendente_indicacao=pendente_indicacao)


@router.post("/fines", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_multa(dados: MultaCreate):
    """Registra uma nova notificação de infração de trânsito."""
    return compliance_service.registrar_multa(dados)


@router.post("/fines/{multa_id}/indicar", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def indicar_condutor_multa(multa_id: str, request: IndicarCondutorRequest):
    """
    Executa workflow de indicação do condutor infrator antes do prazo legal do CTB.
    Atualiza pontuação na CNH e emite protocolo DETRAN.
    """
    try:
        res = compliance_service.indicar_condutor(multa_id, request)
        if not res:
            raise HTTPException(status_code=404, detail="Multa não encontrada.")
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/claims")
def list_sinistros(placa: Optional[str] = None):
    """Lista histórico de sinistros e acionamentos de seguradora."""
    return compliance_service.listar_sinistros(placa=placa)


@router.post("/claims", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_sinistro(dados: SinistroCreate):
    """Abre ocorrência de sinistro com dados de apólice e estimativa de danos."""
    return compliance_service.registrar_sinistro(dados)


@router.get("/expirations")
def get_expirations_alert():
    """Retorna alertas de documentos de veículos (IPVA, licenciamento) e habilitações/toxicológicos a vencer."""
    return compliance_service.relatorio_vencimentos_alerta()


@router.post("/documents", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_document(dados: DocumentoVencimentoCreate):
    """Cadastra vencimento de imposto ou seguro obrigatório/facultativo de veículo."""
    return compliance_service.cadastrar_documento(dados)

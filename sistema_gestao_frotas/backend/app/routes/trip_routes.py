"""
Rotas para Gestão de Viagens, Despacho, Rotas e Checklist Digital Pré/Pós-Viagem.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.security.auth import RequireRole
from app.models.schemas import (
    UserRole,
    SolicitacaoViagemCreate,
    ChecklistDigitalCreate
)
from app.services.trip_service import trip_service

router = APIRouter(prefix="/api/trips", tags=["Viagens, Despacho & Checklist"])


@router.get("")
def list_viagens(status_viagem: Optional[str] = Query(None, alias="status")):
    """Lista solicitações e viagens da frota com status operacional e rotas."""
    return trip_service.listar_viagens(status=status_viagem)


@router.post("", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA, UserRole.OPERADOR]))])
def create_viagem(dados: SolicitacaoViagemCreate):
    """Cria uma requisição de viagem vinculada a um centro de custo."""
    return trip_service.criar_solicitacao(dados)


@router.post("/{viagem_id}/dispatch", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA, UserRole.OPERADOR]))])
def dispatch_viagem(viagem_id: str):
    """
    Despacha a viagem autorizada.
    Valida obrigatoriamente a existência de checklist pré-viagem aprovado sem reprovações críticas.
    """
    try:
        viagem = trip_service.despachar_viagem(viagem_id)
        if not viagem:
            raise HTTPException(status_code=404, detail="Viagem não encontrada.")
        return viagem
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{viagem_id}/finish", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA, UserRole.OPERADOR, UserRole.MOTORISTA]))])
def finish_viagem(viagem_id: str):
    """Finaliza a viagem e libera o veículo para o pátio."""
    viagem = trip_service.concluir_viagem(viagem_id)
    if not viagem:
        raise HTTPException(status_code=404, detail="Viagem não encontrada.")
    return viagem


@router.get("/checklists")
def list_checklists(placa: Optional[str] = None):
    """Lista vistorias digitais de pré e pós-viagem com fotos e itens inspecionados."""
    return trip_service.listar_checklists(placa=placa)


@router.post("/checklists", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA, UserRole.OPERADOR, UserRole.MOTORISTA]))])
def create_checklist(dados: ChecklistDigitalCreate):
    """
    Registra vistoria digital de pré ou pós-viagem.
    Bloqueia automaticamente o veículo caso itens de segurança (pneus, faróis, freios) estejam reprovados.
    """
    return trip_service.registrar_checklist(dados)

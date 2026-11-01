"""
Rotas para Gestão de Abastecimento, Auditoria Antifraude e Pedágios com Tags Eletrônicas.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status

from app.security.auth import RequireRole
from app.models.schemas import (
    UserRole,
    AbastecimentoCreate,
    PedagioCreate
)
from app.services.fuel_service import fuel_service

router = APIRouter(prefix="/api/fuel", tags=["Abastecimento & Pedágios"])


@router.get("/transactions")
def list_abastecimentos(
    placa: Optional[str] = None,
    apenas_anomalias: bool = Query(False, description="Filtrar apenas suspeitas de fraude ou anomalias")
):
    """Lista transações de abastecimento com detecção de anomalias e cálculo de km/L."""
    return fuel_service.listar_abastecimentos(placa=placa, apenas_anomalias=apenas_anomalias)


@router.post("/transactions", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA, UserRole.OPERADOR, UserRole.MOTORISTA]))])
def create_abastecimento(dados: AbastecimentoCreate):
    """
    Registra abastecimento com auditoria antifraude imediata:
    Verifica capacidade física do tanque vs volume abastecido e calcula consumo médio km/L.
    """
    return fuel_service.registrar_abastecimento(dados)


@router.get("/tolls")
def list_pedagios(placa: Optional[str] = None):
    """Lista débitos automáticos de praças de pedágio via tag eletrônica (Sem Parar, Veloe, etc.)."""
    return fuel_service.listar_pedagios(placa=placa)


@router.post("/tolls", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA, UserRole.OPERADOR]))])
def create_pedagio(dados: PedagioCreate):
    """Registra passagem de pedágio conciliada via tag eletrônica."""
    return fuel_service.registrar_pedagio(dados)


# -------------------------------------------------------------
# POSTOS CREDENCIADOS
# -------------------------------------------------------------

@router.get("/stations")
def list_postos_credenciados():
    """Lista rede de postos de combustível credenciados com geolocalização GPS."""
    return fuel_service.listar_postos()


@router.post("/stations", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_posto_credenciado(dados: Any = Body(...)):
    """Credencia novo posto de combustível para fornecimento da frota."""
    from app.models.schemas import PostoCredenciadoCreate
    posto_validado = PostoCredenciadoCreate(**dados)
    return fuel_service.cadastrar_posto(posto_validado)

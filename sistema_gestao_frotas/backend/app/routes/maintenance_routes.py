"""
Rotas para Manutenção Preventiva e Corretiva, Ordens de Serviço (OS) e Gestão de Pneus.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone

from app.database import get_database
from app.security.auth import RequireRole
from app.models.schemas import (
    UserRole,
    OrdemServicoCreate,
    StatusOS,
    PlanoRevisaoCreate,
    PneuCreate,
    PneuUpdate
)
from app.services.maintenance_service import maintenance_service

router = APIRouter(prefix="/api/maintenance", tags=["Manutenção & Gestão de Pneus"])


class StatusOSUpdate(BaseModel):
    novo_status: StatusOS
    conclusao_data: Optional[str] = None


@router.get("/os")
def list_ordens_servico(placa: Optional[str] = None, status_os: Optional[str] = Query(None, alias="status")):
    """Lista Ordens de Serviço (OS) com detalhes de peças, mão de obra e oficinas."""
    return maintenance_service.listar_os(placa=placa, status=status_os)


@router.post("/os", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA, UserRole.OPERADOR]))])
def create_ordem_servico(dados: OrdemServicoCreate):
    """Abre uma nova Ordem de Serviço e vincula peças e serviços."""
    return maintenance_service.criar_os(dados)


@router.patch("/os/{os_id}/status", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA, UserRole.OPERADOR]))])
def update_os_status(os_id: str, body: StatusOSUpdate):
    """Atualiza o status da OS (ex: CONCLUIDA) e libera automaticamente o veículo."""
    res = maintenance_service.atualizar_status_os(os_id, body.novo_status, body.conclusao_data)
    if not res:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")
    return res


@router.get("/plans")
def list_planos_revisao():
    """Lista planos de revisão preventiva por quilometragem e intervalo de tempo."""
    db = get_database()
    cursor = db.planos_revisao.find({})
    planos = []
    for doc in cursor:
        doc.pop("_id", None)
        planos.append(doc)
    return planos


@router.post("/plans", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_plano_revisao(dados: PlanoRevisaoCreate):
    """Cadastra novo plano de revisão preventiva."""
    db = get_database()
    agora_iso = datetime.now(timezone.utc).isoformat()
    doc = dados.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = agora_iso
    db.planos_revisao.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/alerts")
def get_preventive_alerts():
    """Retorna diagnósticos preventivos e veículos que atingiram o limite de km para revisão."""
    return maintenance_service.verificar_alertas_revisao()


# -------------------------------------------------------------
# GESTÃO DE PNEUS
# -------------------------------------------------------------

@router.get("/tires")
def list_tires(placa: Optional[str] = None):
    """Lista inventário de pneus, controle de sulco CONTRAN, pressão e rodízios."""
    return maintenance_service.listar_pneus(placa=placa)


@router.post("/tires", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_tire(dados: PneuCreate):
    """Cadastra pneu e valida limites de sulco legal CONTRAN."""
    return maintenance_service.cadastrar_pneu(dados)


@router.put("/tires/{tire_id}", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def update_tire(tire_id: str, dados: PneuUpdate):
    """Atualiza sulco medido em milímetros, pressão PSI e histórico de recapagem."""
    res = maintenance_service.atualizar_pneu(tire_id, dados)
    if not res:
        raise HTTPException(status_code=404, detail="Pneu não encontrado.")
    return res


# -------------------------------------------------------------
# OFICINAS E FORNECEDORES CREDENCIADOS
# -------------------------------------------------------------

@router.get("/workshops")
def list_oficinas_credenciadas():
    """Lista oficinas mecânicas e fornecedores credenciados."""
    return maintenance_service.listar_oficinas()


@router.post("/workshops", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_oficina_credenciada(dados: Dict[str, Any]):
    """Credencia nova oficina mecânica ou fornecedor de autopeças."""
    from app.models.schemas import OficinaCredenciadaCreate
    oficina_validada = OficinaCredenciadaCreate(**dados)
    return maintenance_service.cadastrar_oficina(oficina_validada)


@router.get("/history/{placa}")
def get_historico_veiculo(placa: str):
    """Retorna o histórico completo de manutenções preventivas e corretivas de um veículo."""
    return maintenance_service.obter_historico_veiculo(placa)

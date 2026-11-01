"""
Rotas de Telemetria IoT, Rastreamento GPS em Tempo Real, Eventos e Geofencing.
Suporta autenticação dupla: Chave de API (X-API-Key) para rastreadores IoT e Bearer Token para usuários web.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
import uuid
import random
from datetime import datetime, timezone

from app.database import get_database
from app.security.api_keys import get_current_auth
from app.security.auth import RequireRole
from app.models.schemas import (
    UserRole,
    TelemetriaPingInput,
    TelemetriaPingResponse,
    CercaEletronicaCreate,
    CercaEletronicaResponse
)
from app.services.telemetry_service import telemetry_service

router = APIRouter(prefix="/api/telemetry", tags=["Telemetria & Rastreamento Realtime"])


@router.post("/ping", response_model=TelemetriaPingResponse)
def ingest_telemetry_ping(
    ping: TelemetriaPingInput,
    auth: Dict[str, Any] = Depends(get_current_auth)
):
    """
    Endpoint de Alta Performance para Ingestão de Dados IoT (OBD2/CANbus/GPS).
    Autenticado de forma segura via cabeçalho 'X-API-Key: flt_...' ou Bearer Token.
    """
    res = telemetry_service.processar_ping(ping)
    return res


@router.get("/live")
def get_live_positions():
    """Retorna as posições mais recentes de todos os veículos da frota para o mapa."""
    return telemetry_service.obter_posicoes_tempo_real()


@router.get("/history/{placa}")
def get_route_history(placa: str, limit: int = Query(150, ge=10, le=1000)):
    """Retorna histórico de pontos geográficos para traçado da rota percorrida no mapa."""
    return telemetry_service.obter_historico_rota(placa, limit=limit)


@router.get("/events")
def list_driving_events(placa: Optional[str] = None, limit: int = Query(50, ge=5, le=500)):
    """Lista eventos de condução agressiva (frenagem brusca, aceleração, excesso de velocidade/RPM)."""
    return telemetry_service.obter_eventos_conducao(placa=placa, limit=limit)


@router.get("/geofences")
def list_geofences():
    """Lista todas as cercas eletrônicas cadastradas."""
    db = get_database()
    cursor = db.cercas_eletronicas.find({})
    cercas = []
    for doc in cursor:
        doc.pop("_id", None)
        cercas.append(doc)
    return cercas


@router.post("/geofences", response_model=CercaEletronicaResponse, dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_geofence(dados: CercaEletronicaCreate):
    """Cria uma nova cerca eletrônica (Geofence) com regras de zona autorizada ou proibida."""
    db = get_database()
    agora_iso = datetime.now(timezone.utc).isoformat()
    cerca_id = str(uuid.uuid4())

    doc = dados.model_dump()
    doc["id"] = cerca_id
    doc["created_at"] = agora_iso

    db.cercas_eletronicas.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.post("/simulate-step")
def simulate_fleet_step():
    """
    Simulador de Ingestão de Telemetria:
    Move suavemente veículos em trânsito ao longo de rotas rodoviárias para demonstração em tempo real.
    """
    posicoes = telemetry_service.obter_posicoes_tempo_real()
    atualizados = []

    for pos in posicoes:
        if pos.get("ignicao"):
            # Variação suave de coordenadas (-0.003 a +0.003 graus)
            dlat = random.uniform(-0.0025, 0.0025)
            dlng = random.uniform(-0.0025, 0.0025)
            nova_lat = pos["latitude"] + dlat
            nova_lng = pos["longitude"] + dlng
            vel = max(40.0, min(105.0, pos.get("velocidade_kmh", 70.0) + random.uniform(-8, 8)))
            rpm = int(1400 + (vel / 110.0) * 1200 + random.randint(-80, 80))
            novo_odo = float(pos.get("odometro_km", 10000.0)) + round(vel / 3600.0 * 15, 2)

            ping = TelemetriaPingInput(
                veiculo_placa=pos["veiculo_placa"],
                latitude=round(nova_lat, 6),
                longitude=round(nova_lng, 6),
                velocidade_kmh=round(vel, 1),
                ignicao=True,
                rpm=rpm,
                odometro_km=round(novo_odo, 1),
                motorista_identificador=pos.get("motorista_identificador")
            )
            res = telemetry_service.processar_ping(ping)
            atualizados.append({"placa": pos["veiculo_placa"], "status": "simulado", "alertas": res.alertas_gerados})

    return {"status": "ok", "veiculos_movimentados": len(atualizados), "detalhes": atualizados}

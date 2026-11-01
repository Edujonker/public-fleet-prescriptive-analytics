"""
Serviço de Telemetria e Ingestão IoT em Tempo Real.
Responsável por ingestão de pings GPS, verificação de cercas eletrônicas (Geofencing),
detecção de eventos de condução agressiva e manutenção da última posição conhecida.
"""

import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid

from app.database import get_database
from app.models.schemas import (
    TelemetriaPingInput,
    TelemetriaPingResponse,
    TipoEventoConducao,
    GravidadeEvento,
    RegraCerca
)


def calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância em metros entre duas coordenadas geográficas via fórmula Haversine."""
    R = 6371000.0  # Raio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class TelemetryService:
    def __init__(self):
        self.db = get_database()

    def processar_ping(self, ping: TelemetriaPingInput) -> TelemetriaPingResponse:
        """
        Processa ping IoT de rastreador embarcado:
        1. Atualiza última posição instantânea do veículo
        2. Detecta violações de velocidade e RPM excessivo
        3. Avalia regras de cercas eletrônicas (geofences)
        4. Registra histórico na coleção de telemetria
        """
        agora_iso = datetime.now(timezone.utc).isoformat()
        timestamp_ping = ping.timestamp or agora_iso
        alertas: List[str] = []

        # 1. Recuperar dados do veículo para limites e metadados
        veiculo = self.db.veiculos.find_one({"placa": ping.veiculo_placa.upper()})
        nome_modelo = veiculo.get("modelo", "Veículo Não Identificado") if veiculo else "Veículo Não Identificado"

        # 2. Verificar eventos de condução agressiva (Excesso de velocidade, RPM)
        limite_vel = 110.0  # Limite padrão rodovia (km/h)
        if ping.velocidade_kmh > limite_vel:
            gravidade = GravidadeEvento.GRAVE if ping.velocidade_kmh > (limite_vel + 20) else GravidadeEvento.MEDIA
            evento_id = str(uuid.uuid4())
            self.db.eventos_conducao.insert_one({
                "id": evento_id,
                "veiculo_placa": ping.veiculo_placa.upper(),
                "motorista_identificador": ping.motorista_identificador,
                "timestamp": timestamp_ping,
                "tipo_evento": TipoEventoConducao.EXCESSO_VELOCIDADE.value,
                "gravidade": gravidade.value,
                "valor_registrado": ping.velocidade_kmh,
                "limite_tolerancia": limite_vel,
                "latitude": ping.latitude,
                "longitude": ping.longitude,
                "detalhes": f"Velocidade de {ping.velocidade_kmh:.1f} km/h superior ao limite de {limite_vel} km/h.",
                "created_at": agora_iso
            })
            alertas.append(f"Excesso de velocidade: {ping.velocidade_kmh:.0f} km/h (limite: {limite_vel:.0f} km/h)")

        limite_rpm = 3800
        if ping.rpm and ping.rpm > limite_rpm:
            evento_id = str(uuid.uuid4())
            self.db.eventos_conducao.insert_one({
                "id": evento_id,
                "veiculo_placa": ping.veiculo_placa.upper(),
                "motorista_identificador": ping.motorista_identificador,
                "timestamp": timestamp_ping,
                "tipo_evento": TipoEventoConducao.EXCESSO_RPM.value,
                "gravidade": GravidadeEvento.MEDIA.value,
                "valor_registrado": float(ping.rpm),
                "limite_tolerancia": float(limite_rpm),
                "latitude": ping.latitude,
                "longitude": ping.longitude,
                "detalhes": f"Rotação do motor em {ping.rpm} RPM ultrapassou limite de {limite_rpm} RPM.",
                "created_at": agora_iso
            })
            alertas.append(f"Excesso de rotação: {ping.rpm} RPM (limite: {limite_rpm} RPM)")

        # 3. Avaliar cercas eletrônicas ativas
        cercas = list(self.db.cercas_eletronicas.find({"ativo": True}))
        for cerca in cercas:
            dist = calcular_distancia_haversine(
                ping.latitude, ping.longitude,
                cerca.get("centro_lat", 0.0), cerca.get("centro_lng", 0.0)
            )
            raio = cerca.get("raio_metros", 500.0)
            esta_dentro = dist <= raio

            if cerca.get("regras") == RegraCerca.PROIBIDA.value and esta_dentro:
                alerta_msg = f"Violação de Cerca: Veículo entrou em Zona Proibida '{cerca.get('nome')}'."
                alertas.append(alerta_msg)
                self.db.eventos_conducao.insert_one({
                    "id": str(uuid.uuid4()),
                    "veiculo_placa": ping.veiculo_placa.upper(),
                    "motorista_identificador": ping.motorista_identificador,
                    "timestamp": timestamp_ping,
                    "tipo_evento": "VIOLACAO_CERCA_PROIBIDA",
                    "gravidade": GravidadeEvento.CRITICA.value,
                    "valor_registrado": dist,
                    "limite_tolerancia": raio,
                    "latitude": ping.latitude,
                    "longitude": ping.longitude,
                    "detalhes": alerta_msg,
                    "created_at": agora_iso
                })
            elif cerca.get("regras") == RegraCerca.PERMITIDA.value and not esta_dentro:
                veiculos_autorizados = cerca.get("veiculos_autorizados", [])
                if ping.veiculo_placa.upper() in veiculos_autorizados:
                    alerta_msg = f"Alerta de Rota: Veículo saiu do perímetro autorizado '{cerca.get('nome')}' ({dist:.0f}m do centro)."
                    alertas.append(alerta_msg)

        # 4. Atualizar última posição instantânea (para rápida renderização no mapa)
        doc_posicao = {
            "veiculo_placa": ping.veiculo_placa.upper(),
            "modelo": nome_modelo,
            "motorista_identificador": ping.motorista_identificador,
            "latitude": ping.latitude,
            "longitude": ping.longitude,
            "velocidade_kmh": ping.velocidade_kmh,
            "ignicao": ping.ignicao,
            "rpm": ping.rpm or 0,
            "odometro_km": ping.odometro_km or (veiculo.get("odometro_atual_km", 0.0) if veiculo else 0.0),
            "temperatura_motor_c": ping.temperatura_motor_c,
            "nivel_combustivel_percent": ping.nivel_combustivel_percent,
            "tensao_bateria_v": ping.tensao_bateria_v,
            "status_operacional": "EM_VIAGEM" if (ping.ignicao and ping.velocidade_kmh > 5) else ("LIGADO_PARADO" if ping.ignicao else "ESTACIONADO"),
            "ultima_atualizacao": agora_iso
        }
        pos_existente = self.db.posicoes_instantaneas.find_one({"veiculo_placa": ping.veiculo_placa.upper()})
        if pos_existente:
            self.db.posicoes_instantaneas.update_one(
                {"veiculo_placa": ping.veiculo_placa.upper()},
                {"$set": doc_posicao}
            )
        else:
            self.db.posicoes_instantaneas.insert_one(doc_posicao)

        # Atualizar odômetro do veículo se informado e maior
        if ping.odometro_km and veiculo and ping.odometro_km > veiculo.get("odometro_atual_km", 0.0):
            self.db.veiculos.update_one(
                {"placa": ping.veiculo_placa.upper()},
                {"$set": {"odometro_atual_km": ping.odometro_km, "updated_at": agora_iso}}
            )

        # 5. Salvar registro na série histórica de telemetria
        ping_id = str(uuid.uuid4())
        doc_historico = ping.model_dump()
        doc_historico["id"] = ping_id
        doc_historico["recebido_em"] = agora_iso
        doc_historico["alertas_gerados"] = alertas
        self.db.telemetria_pings.insert_one(doc_historico)

        return TelemetriaPingResponse(
            id=ping_id,
            veiculo_placa=ping.veiculo_placa.upper(),
            timestamp=timestamp_ping,
            latitude=ping.latitude,
            longitude=ping.longitude,
            velocidade_kmh=ping.velocidade_kmh,
            ignicao=ping.ignicao,
            rpm=ping.rpm,
            odometro_km=ping.odometro_km,
            motorista_identificador=ping.motorista_identificador,
            temperatura_motor_c=ping.temperatura_motor_c,
            nivel_combustivel_percent=ping.nivel_combustivel_percent,
            tensao_bateria_v=ping.tensao_bateria_v,
            recebido_em=agora_iso,
            alertas_gerados=alertas
        )

    def obter_posicoes_tempo_real(self) -> List[Dict[str, Any]]:
        """Retorna as posições mais recentes de todos os veículos ativos."""
        cursor = self.db.posicoes_instantaneas.find({})
        posicoes = []
        for doc in cursor:
            doc.pop("_id", None)
            posicoes.append(doc)
        return posicoes

    def obter_historico_rota(self, placa: str, limit: int = 200) -> List[Dict[str, Any]]:
        """Retorna histórico de pontos GPS para traçado de rotas percorridas."""
        cursor = self.db.telemetria_pings.find(
            {"veiculo_placa": placa.upper()}
        ).sort("timestamp", -1).limit(limit)
        
        pontos = []
        for doc in cursor:
            doc.pop("_id", None)
            pontos.append(doc)
        # Ordenar cronologicamente para exibição contínua da rota
        pontos.reverse()
        return pontos

    def obter_eventos_conducao(self, placa: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna eventos de condução agressiva e violações de cerca."""
        filtro = {}
        if placa:
            filtro["veiculo_placa"] = placa.upper()
        cursor = self.db.eventos_conducao.find(filtro).sort("timestamp", -1).limit(limit)
        eventos = []
        for doc in cursor:
            doc.pop("_id", None)
            eventos.append(doc)
        return eventos


telemetry_service = TelemetryService()

"""
Serviço de Gestão de Abastecimento, Detecção de Anomalias/Fraudes e Controle de Pedágios.
Suporte a integração com cartões de frota (Ticket Log, Alelo, VR Auto, etc.) e tags eletrônicas.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid

from app.database import get_database
from app.models.schemas import (
    AbastecimentoCreate,
    AbastecimentoResponse,
    PedagioCreate,
    PedagioResponse
)


class FuelService:
    def __init__(self):
        self.db = get_database()

    def registrar_abastecimento(self, dados: AbastecimentoCreate) -> Dict[str, Any]:
        """
        Registra abastecimento e executa algoritmos de auditoria contra fraudes:
        1. Anomalia de capacidade: litros > capacidade física do tanque do veículo.
        2. Cálculo de consumo médio km/L baseado no odômetro do abastecimento anterior.
        3. Detecção de odômetro retrocedido ou inconsistente.
        """
        agora_iso = datetime.now(timezone.utc).isoformat()
        abast_id = str(uuid.uuid4())
        data_hora = dados.data_hora or agora_iso

        veiculo = self.db.veiculos.find_one({"placa": dados.veiculo_placa.upper()})
        tanque_capacidade = float(veiculo.get("capacidade_tanque_litros", 60.0)) if veiculo else 100.0

        anomalia = False
        motivos_anomalia = []

        # 1. Regra Antifraude: Volume > Capacidade do Tanque (+5% margem bocal)
        if dados.litros > (tanque_capacidade * 1.05):
            anomalia = True
            motivo = f"VOLUME ANÔMALO: Abastecido {dados.litros:.1f} L em tanque com capacidade máxima de {tanque_capacidade:.1f} L (Excedente de {(dados.litros - tanque_capacidade):.1f} L)."
            motivos_anomalia.append(motivo)

        # 2. Buscar último abastecimento deste veículo para cálculo de autonomia
        ultimo_abast = self.db.abastecimentos.find_one(
            {"veiculo_placa": dados.veiculo_placa.upper()},
            sort=[("odometro_km", -1)]
        )

        consumo_kml = None
        consumo_l_km = None
        if ultimo_abast and ultimo_abast.get("odometro_km"):
            km_anterior = float(ultimo_abast["odometro_km"])
            km_rodado = dados.odometro_km - km_anterior

            if km_rodado <= 0:
                anomalia = True
                motivos_anomalia.append(f"ODÔMETRO INCONSISTENTE: Km atual ({dados.odometro_km:.0f}) <= Km anterior ({km_anterior:.0f}).")
            elif dados.litros > 0:
                consumo_kml = round(km_rodado / dados.litros, 2)
                consumo_l_km = round(dados.litros / km_rodado, 4)
                # Faixa plausível para frotas comerciais: 1.5 km/L (carreta pesada) a 26 km/L (híbrido/leve)
                if consumo_kml < 1.4 or consumo_kml > 28.0:
                    anomalia = True
                    motivos_anomalia.append(f"AUTONOMIA ATÍPICA: {consumo_kml} km/L ({consumo_l_km} L/km) destoa da média padrão operacional.")

        valor_total = dados.valor_total if dados.valor_total and dados.valor_total > 0 else round(dados.litros * dados.valor_litro, 2)

        doc = dados.model_dump()
        doc["id"] = abast_id
        doc["veiculo_placa"] = dados.veiculo_placa.upper()
        doc["data_hora"] = data_hora
        doc["valor_total"] = valor_total
        doc["consumo_calculado_kml"] = consumo_kml
        doc["consumo_l_km"] = consumo_l_km
        doc["anomalia_detectada"] = anomalia
        doc["motivo_anomalia"] = " | ".join(motivos_anomalia) if anomalia else None
        doc["created_at"] = agora_iso

        self.db.abastecimentos.insert_one(doc)

        # Atualizar odômetro do veículo se válido e maior
        if veiculo and dados.odometro_km > float(veiculo.get("odometro_atual_km", 0.0)):
            self.db.veiculos.update_one(
                {"placa": dados.veiculo_placa.upper()},
                {"$set": {"odometro_atual_km": dados.odometro_km, "updated_at": agora_iso}}
            )

        doc.pop("_id", None)
        return doc

    def cadastrar_posto(self, dados: Any) -> Dict[str, Any]:
        """Cadastra posto de abastecimento fornecedor credenciado."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        posto_id = str(uuid.uuid4())
        doc = dados.model_dump()
        doc["id"] = posto_id
        doc["created_at"] = agora_iso
        self.db.postos_credenciados.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def listar_postos(self) -> List[Dict[str, Any]]:
        """Lista postos credenciados com endereço e coordenadas geográficas."""
        cursor = self.db.postos_credenciados.find({})
        postos = []
        for doc in cursor:
            doc.pop("_id", None)
            postos.append(doc)
        return postos

    def listar_abastecimentos(self, placa: Optional[str] = None, apenas_anomalias: bool = False) -> List[Dict[str, Any]]:
        """Lista registros de abastecimento com opção de filtro por anomalias/fraudes."""
        filtro: Dict[str, Any] = {}
        if placa:
            filtro["veiculo_placa"] = placa.upper()
        if apenas_anomalias:
            filtro["anomalia_detectada"] = True

        cursor = self.db.abastecimentos.find(filtro).sort("data_hora", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res

    # -------------------------------------------------------------
    # CONTROLE DE PEDÁGIOS
    # -------------------------------------------------------------
    def registrar_pedagio(self, dados: PedagioCreate) -> Dict[str, Any]:
        """Registra passagem e débito de pedágio via tag automática."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        pedagio_id = str(uuid.uuid4())

        doc = dados.model_dump()
        doc["id"] = pedagio_id
        doc["veiculo_placa"] = dados.veiculo_placa.upper()
        doc["data_hora"] = dados.data_hora or agora_iso
        doc["created_at"] = agora_iso

        self.db.pedagios.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def listar_pedagios(self, placa: Optional[str] = None) -> List[Dict[str, Any]]:
        filtro: Dict[str, Any] = {}
        if placa:
            filtro["veiculo_placa"] = placa.upper()
        cursor = self.db.pedagios.find(filtro).sort("data_hora", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res


fuel_service = FuelService()

"""
Rotas para Gestão de Ativos: Veículos, Motoristas e Equipamentos Embarcados.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
import uuid
from datetime import datetime, timezone

from app.database import get_database
from app.security.auth import get_current_user, RequireRole
from app.models.schemas import (
    UserRole,
    VeiculoCreate,
    VeiculoUpdate,
    VeiculoResponse,
    MotoristaCreate,
    MotoristaUpdate,
    MotoristaResponse,
    EquipamentoEmbarcadoCreate,
    EquipamentoEmbarcadoResponse
)

router = APIRouter(prefix="/api/assets", tags=["Cadastro e Ativos"])


# -------------------------------------------------------------
# VEÍCULOS
# -------------------------------------------------------------

@router.get("/veiculos")
def list_veiculos(
    categoria: Optional[str] = None,
    status_veiculo: Optional[str] = Query(None, alias="status"),
    busca: Optional[str] = None
):
    """Lista todos os veículos com filtros opcionais por categoria, status ou busca textual."""
    db = get_database()
    filtro: Dict[str, Any] = {}
    if categoria:
        filtro["categoria"] = categoria
    if status_veiculo:
        filtro["status"] = status_veiculo
    cursor = db.veiculos.find(filtro).sort("placa", 1)
    veiculos = []
    for doc in cursor:
        doc.pop("_id", None)
        veiculos.append(doc)

    if busca:
        busca_lower = busca.lower()
        veiculos = [
            v for v in veiculos
            if busca_lower in v.get("placa", "").lower()
            or busca_lower in v.get("marca", "").lower()
            or busca_lower in v.get("modelo", "").lower()
        ]

    return veiculos


@router.post("/veiculos", response_model=VeiculoResponse, dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_veiculo(dados: VeiculoCreate):
    """Cadastra um novo veículo na frota corporativa."""
    db = get_database()
    placa_upper = dados.placa.upper()
    if db.veiculos.find_one({"placa": placa_upper}):
        raise HTTPException(status_code=400, detail=f"Veículo com placa {placa_upper} já cadastrado.")

    agora_iso = datetime.now(timezone.utc).isoformat()
    veiculo_id = str(uuid.uuid4())

    doc = dados.model_dump()
    doc["id"] = veiculo_id
    doc["placa"] = placa_upper
    doc["created_at"] = agora_iso
    doc["updated_at"] = agora_iso

    db.veiculos.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/veiculos/{placa}")
def get_veiculo(placa: str):
    """Retorna a ficha cadastral completa do veículo pela placa."""
    db = get_database()
    v = db.veiculos.find_one({"placa": placa.upper()})
    if not v:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    v.pop("_id", None)
    return v


@router.put("/veiculos/{placa}", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def update_veiculo(placa: str, dados: VeiculoUpdate):
    """Atualiza dados cadastrais ou status operacional do veículo."""
    db = get_database()
    placa_upper = placa.upper()
    v = db.veiculos.find_one({"placa": placa_upper})
    if not v:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")

    agora_iso = datetime.now(timezone.utc).isoformat()
    update_data = {k: v for k, v in dados.model_dump().items() if v is not None}
    update_data["updated_at"] = agora_iso

    db.veiculos.update_one({"placa": placa_upper}, {"$set": update_data})
    v_atualizado = db.veiculos.find_one({"placa": placa_upper})
    v_atualizado.pop("_id", None)
    return v_atualizado


# -------------------------------------------------------------
# MOTORISTAS
# -------------------------------------------------------------

@router.get("/motoristas")
def list_motoristas(busca: Optional[str] = None):
    """Lista condutores cadastrados, categorias de CNH e validade toxicológica."""
    db = get_database()
    filtro: Dict[str, Any] = {}
    cursor = db.motoristas.find(filtro).sort("nome", 1)
    motoristas = []
    for doc in cursor:
        doc.pop("_id", None)
        motoristas.append(doc)

    if busca:
        busca_lower = busca.lower()
        motoristas = [
            m for m in motoristas
            if busca_lower in m.get("nome", "").lower()
            or busca_lower in m.get("cpf", "").lower()
            or busca_lower in m.get("cnh_numero", "").lower()
        ]

    return motoristas


@router.post("/motoristas", response_model=MotoristaResponse, dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_motorista(dados: MotoristaCreate):
    """Cadastra um novo motorista com validações de CNH e exame toxicológico."""
    db = get_database()
    if db.motoristas.find_one({"cpf": dados.cpf}):
        raise HTTPException(status_code=400, detail="CPF já cadastrado para outro motorista.")
    if db.motoristas.find_one({"cnh_numero": dados.cnh_numero}):
        raise HTTPException(status_code=400, detail="Número de CNH já cadastrado.")

    agora_iso = datetime.now(timezone.utc).isoformat()
    m_id = str(uuid.uuid4())

    doc = dados.model_dump()
    doc["id"] = m_id
    doc["score_conducao"] = 100.0
    doc["created_at"] = agora_iso
    doc["updated_at"] = agora_iso

    db.motoristas.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/motoristas/{motorista_id}")
def get_motorista(motorista_id: str):
    db = get_database()
    m = db.motoristas.find_one({"id": motorista_id})
    if not m:
        raise HTTPException(status_code=404, detail="Motorista não encontrado.")
    m.pop("_id", None)
    return m


@router.put("/motoristas/{motorista_id}", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def update_motorista(motorista_id: str, dados: MotoristaUpdate):
    db = get_database()
    m = db.motoristas.find_one({"id": motorista_id})
    if not m:
        raise HTTPException(status_code=404, detail="Motorista não encontrado.")

    agora_iso = datetime.now(timezone.utc).isoformat()
    update_data = {k: v for k, v in dados.model_dump().items() if v is not None}
    update_data["updated_at"] = agora_iso

    db.motoristas.update_one({"id": motorista_id}, {"$set": update_data})
    m_atualizado = db.motoristas.find_one({"id": motorista_id})
    m_atualizado.pop("_id", None)
    return m_atualizado


# -------------------------------------------------------------
# EQUIPAMENTOS EMBARCADOS
# -------------------------------------------------------------

@router.get("/equipamentos")
def list_equipamentos():
    """Lista rastreadores, sensores de telemetria e câmeras de fadiga."""
    db = get_database()
    cursor = db.equipamentos.find({}).sort("identificador_serial", 1)
    eqs = []
    for doc in cursor:
        doc.pop("_id", None)
        eqs.append(doc)
    return eqs


@router.post("/equipamentos", response_model=EquipamentoEmbarcadoResponse, dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_equipamento(dados: EquipamentoEmbarcadoCreate):
    """Cadastra equipamento de telemetria/rastreador veicular."""
    db = get_database()
    if db.equipamentos.find_one({"identificador_serial": dados.identificador_serial}):
        raise HTTPException(status_code=400, detail="Equipamento com este serial já cadastrado.")

    agora_iso = datetime.now(timezone.utc).isoformat()
    eq_id = str(uuid.uuid4())

    doc = dados.model_dump()
    doc["id"] = eq_id
    doc["created_at"] = agora_iso

    db.equipamentos.insert_one(doc)
    doc.pop("_id", None)
    return doc


# -------------------------------------------------------------
# AUTO-CADASTRO E AUTO-DESCOBERTA IOT / CANBUS
# -------------------------------------------------------------

@router.get("/iot/dispositivos-descobertos")
def list_dispositivos_descobertos():
    """
    Retorna lista de rastreadores e módulos CANbus detectados na rede
    aguardando vinculação e autocadastro veicular plug-and-play.
    """
    db = get_database()
    dispositivos_mock = [
        {
            "serial": "TELT-FMB920-842199",
            "modelo": "Teltonika FMB920 (4G/LTE + BLE)",
            "protocolo": "CANBUS_OBD2_HEX",
            "ip_origem": "192.168.1.105",
            "vin_detectado": "9BFZZZ24ZPB084219",
            "hodometro_detectado": 185420.5,
            "combustivel_detectado": 74.0,
            "rpm_atual": 850,
            "velocidade_kmh": 0,
            "sinal_gsm_dbm": -68,
            "satelites_fix": 14,
            "status_pareamento": "PENDENTE_VINCULACAO",
            "ultimo_ping": datetime.now(timezone.utc).isoformat()
        },
        {
            "serial": "QUEC-GV300-992144",
            "modelo": "Queclink GV300 (CAN/J1939)",
            "protocolo": "QUECLINK_ASCII_PROT",
            "ip_origem": "192.168.1.112",
            "vin_detectado": "8AFZZZ37ZNB099214",
            "hodometro_detectado": 92140.0,
            "combustivel_detectado": 88.5,
            "rpm_atual": 0,
            "velocidade_kmh": 0,
            "sinal_gsm_dbm": -72,
            "satelites_fix": 12,
            "status_pareamento": "PENDENTE_VINCULACAO",
            "ultimo_ping": datetime.now(timezone.utc).isoformat()
        },
        {
            "serial": "COBAN-TK303-551022",
            "modelo": "Coban TK303G GPS/GPRS",
            "protocolo": "COBAN_GPRS_V2",
            "ip_origem": "192.168.1.120",
            "vin_detectado": "9BDZZZ14ZKB055102",
            "hodometro_detectado": 45310.2,
            "combustivel_detectado": 62.0,
            "rpm_atual": 0,
            "velocidade_kmh": 0,
            "sinal_gsm_dbm": -80,
            "satelites_fix": 10,
            "status_pareamento": "PENDENTE_VINCULACAO",
            "ultimo_ping": datetime.now(timezone.utc).isoformat()
        }
    ]

    # Verificar quais já estão pareados no banco
    veiculos = list(db.veiculos.find({}))
    veiculos_chassis = {v.get("chassi") for v in veiculos if v.get("chassi")}
    for d in dispositivos_mock:
        if d["vin_detectado"] in veiculos_chassis:
            d["status_pareamento"] = "PAREADO_ATIVO"

    return dispositivos_mock


from pydantic import BaseModel, Field

class AutoCadastroIoTRequest(BaseModel):
    serial_rastreador: str = Field(..., min_length=3)
    protocolo: str = Field("CANBUS_OBD2")
    chassi_lido_ecu: str = Field(..., min_length=17, max_length=17)
    placa: str = Field(..., min_length=7, max_length=8)
    marca: str
    modelo: str
    ano_fabricacao: int = 2022
    ano_modelo: int = 2023
    categoria: str = "UTILITARIO"
    tipo_combustivel: str = "DIESEL_S10"
    capacidade_tanque_litros: float = 80.0
    capacidade_carga_kg: float = 1400.0
    odometro_ecu: float = 0.0
    secretaria: str = "SECRETARIA_OBRAS"


@router.post("/veiculos/autocadastro-iot")
def autocadastro_veiculo_iot(dados: AutoCadastroIoTRequest):
    """
    Cadastra automaticamente um novo veículo a partir da leitura direta da ECU/CANbus
    e do pareamento com o rastreador IoT.
    """
    db = get_database()
    placa_upper = dados.placa.upper()
    chassi_upper = dados.chassi_lido_ecu.upper()
    agora_iso = datetime.now(timezone.utc).isoformat()

    # Checar se veículo já existe (compatível com Mongita)
    v1 = db.veiculos.find_one({"placa": placa_upper})
    v2 = db.veiculos.find_one({"chassi": chassi_upper}) if not v1 else None
    veiculo_existente = v1 or v2
    if veiculo_existente:
        # Atualizar odômetro e status IoT
        db.veiculos.update_one(
            {"_id": veiculo_existente["_id"]},
            {"$set": {
                "odometro_atual_km": dados.odometro_ecu,
                "rastreador_serial": dados.serial_rastreador,
                "metodo_cadastro": "IOT_CANBUS_SYNC",
                "updated_at": agora_iso
            }}
        )
        return {
            "sucesso": True,
            "mensagem": f"Veículo {placa_upper} já existente foi sincronizado e pareado com o rastreador {dados.serial_rastreador}.",
            "veiculo_id": veiculo_existente.get("id"),
            "placa": placa_upper,
            "metodo": "SINCRONIZADO_IOT"
        }

    # Criar novo veículo
    veiculo_id = str(uuid.uuid4())
    novo_veiculo = {
        "id": veiculo_id,
        "placa": placa_upper,
        "chassi": chassi_upper,
        "renavam": f"{abs(hash(chassi_upper)) % 10000000000:011d}",
        "marca": dados.marca,
        "modelo": dados.modelo,
        "ano_fabricacao": dados.ano_fabricacao,
        "ano_modelo": dados.ano_modelo,
        "categoria": dados.categoria,
        "capacidade_carga_kg": dados.capacidade_carga_kg,
        "capacidade_tanque_litros": dados.capacidade_tanque_litros,
        "tipo_combustivel": dados.tipo_combustivel,
        "odometro_atual_km": dados.odometro_ecu,
        "horimetro_atual_h": 120.0,
        "status": "DISPONIVEL",
        "centro_custo": f"CC_{dados.secretaria}",
        "secretaria": dados.secretaria,
        "rastreador_serial": dados.serial_rastreador,
        "protocolo_iot": dados.protocolo,
        "metodo_cadastro": "AUTOCADASTRO_IOT_PLUG_PLAY",
        "created_at": agora_iso,
        "updated_at": agora_iso
    }
    db.veiculos.insert_one(novo_veiculo)
    novo_veiculo.pop("_id", None)

    # Registrar / Atualizar Equipamento Embarcado (compatível com Mongita)
    eq_exist = db.equipamentos.find_one({"identificador_serial": dados.serial_rastreador})
    if eq_exist:
        db.equipamentos.update_one(
            {"_id": eq_exist["_id"]},
            {"$set": {
                "veiculo_placa": placa_upper,
                "status": "ATIVO",
                "updated_at": agora_iso
            }}
        )
    else:
        db.equipamentos.insert_one({
            "id": str(uuid.uuid4()),
            "identificador_serial": dados.serial_rastreador,
            "tipo": "RASTREADOR_GPS",
            "modelo": f"IoT Gateway {dados.protocolo}",
            "veiculo_placa": placa_upper,
            "status": "ATIVO",
            "created_at": agora_iso,
            "updated_at": agora_iso
        })

    # Registrar ping de telemetria inicial
    ping_inicial = {
        "id": str(uuid.uuid4()),
        "veiculo_id": veiculo_id,
        "placa": placa_upper,
        "timestamp": agora_iso,
        "latitude": -27.5954,
        "longitude": -48.5480,
        "velocidade": 0.0,
        "rpm": 820.0,
        "odometro": dados.odometro_ecu,
        "nivel_combustivel": 85.0,
        "ignicao": True,
        "origem": "AUTOCADASTRO_IOT_PING_ZERO"
    }
    db.telemetria_pings.insert_one(ping_inicial)

    return {
        "sucesso": True,
        "mensagem": f"Veículo {placa_upper} cadastrado e integrado com sucesso via telemetria IoT ({dados.protocolo})!",
        "veiculo": novo_veiculo,
        "dispositivo_serial": dados.serial_rastreador,
        "metodo": "AUTOCADASTRO_IOT_PLUG_PLAY"
    }

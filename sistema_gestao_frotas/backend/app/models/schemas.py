"""
Modelos e Schemas Pydantic v2 para o Sistema de Gestão de Frotas.
Segue estritamente Security-by-Design, validação de tipos e separação de input/output.
"""

from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, EmailStr


# ==========================================
# ENUMS
# ==========================================

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    GESTOR_FROTA = "GESTOR_FROTA"
    OPERADOR = "OPERADOR"
    MOTORISTA = "MOTORISTA"
    AUDITOR = "AUDITOR"


class VeiculoCategoria(str, Enum):
    LEVE = "LEVE"
    UTILITARIO = "UTILITARIO"
    PESADO = "PESADO"
    ONIBUS = "ONIBUS"
    MOTO = "MOTO"
    # Escopo Contratual Governo do Estado de Santa Catarina (SEA/SC)
    EMBARCACAO = "EMBARCACAO"
    GERADOR = "GERADOR"
    MAQUINA_EQUIPAMENTO = "MAQUINA_EQUIPAMENTO"


class VeiculoStatus(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    EM_VIAGEM = "EM_VIAGEM"
    MANUTENCAO = "MANUTENCAO"
    INATIVO = "INATIVO"


class TipoCombustivel(str, Enum):
    DIESEL = "DIESEL"
    GASOLINA = "GASOLINA"
    ETANOL = "ETANOL"
    FLEX = "FLEX"
    ELETRICO = "ELETRICO"
    GNV = "GNV"
    # Insumos, Derivados e Lubrificantes do Contrato de Santa Catarina:
    DIESEL_S10 = "DIESEL_S10"
    DIESEL_S500 = "DIESEL_S500"
    DIESEL_MARITIMO = "DIESEL_MARITIMO"
    GASOLINA_COMUM = "GASOLINA_COMUM"
    GASOLINA_ADITIVADA = "GASOLINA_ADITIVADA"
    AVGAS = "AVGAS"
    LUBRIFICANTE = "LUBRIFICANTE"
    ADITIVO_ARLA32 = "ADITIVO_ARLA32"
    ADITIVO = "ADITIVO"
    OLEO_2T_4T = "OLEO_2T_4T"
    FLUIDO_HIDRAULICO = "FLUIDO_HIDRAULICO"


class CNHCategoria(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    AB = "AB"
    AC = "AC"
    AD = "AD"
    AE = "AE"


class StatusToxicologico(str, Enum):
    VALIDO = "VALIDO"
    VENCIDO = "VENCIDO"
    AGENDADO = "AGENDADO"


class VinculoContratual(str, Enum):
    CLT = "CLT"
    TERCEIRIZADO = "TERCEIRIZADO"
    AGREGADO = "AGREGADO"


class MotoristaStatus(str, Enum):
    ATIVO = "ATIVO"
    FERIAS = "FERIAS"
    AFASTADO = "AFASTADO"
    INATIVO = "INATIVO"


class TipoEquipamento(str, Enum):
    RASTREADOR_GPS = "RASTREADOR_GPS"
    TELEMETRIA_CANBUS = "TELEMETRIA_CANBUS"
    CAMERA_FADIGA = "CAMERA_FADIGA"
    SENSOR_TEMPERATURA = "SENSOR_TEMPERATURA"


class TipoEventoConducao(str, Enum):
    FRENAGEM_BRUSCA = "FRENAGEM_BRUSCA"
    ACELERACAO_RAPIDA = "ACELERACAO_RAPIDA"
    CURVA_BRUSCA = "CURVA_BRUSCA"
    EXCESSO_VELOCIDADE = "EXCESSO_VELOCIDADE"
    EXCESSO_RPM = "EXCESSO_RPM"
    FADIGA_DETECTADA = "FADIGA_DETECTADA"
    USO_CELULAR = "USO_CELULAR"


class GravidadeEvento(str, Enum):
    LEVE = "LEVE"
    MEDIA = "MEDIA"
    GRAVE = "GRAVE"
    CRITICA = "CRITICA"


class TipoCerca(str, Enum):
    CIRCULO = "CIRCULO"
    POLIGONO = "POLIGONO"


class RegraCerca(str, Enum):
    PERMITIDA = "PERMITIDA"
    PROIBIDA = "PROIBIDA"


class TipoOS(str, Enum):
    PREVENTIVA = "PREVENTIVA"
    CORRETIVA = "CORRETIVA"
    PREDITIVA = "PREDITIVA"


class StatusOS(str, Enum):
    ABERTA = "ABERTA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    AGUARDANDO_PECA = "AGUARDANDO_PECA"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class PosicaoPneu(str, Enum):
    DIANTEIRO_ESQ = "DIANTEIRO_ESQ"
    DIANTEIRO_DIR = "DIANTEIRO_DIR"
    TRASEIRO_ESQ_EXT = "TRASEIRO_ESQ_EXT"
    TRASEIRO_ESQ_INT = "TRASEIRO_ESQ_INT"
    TRASEIRO_DIR_EXT = "TRASEIRO_DIR_EXT"
    TRASEIRO_DIR_INT = "TRASEIRO_DIR_INT"
    ESTEPE = "ESTEPE"
    ESTOQUE = "ESTOQUE"


class StatusPneu(str, Enum):
    NOVO = "NOVO"
    BOM = "BOM"
    ATENCAO = "ATENCAO"
    CRITICO = "CRITICO"
    RECAPAR = "RECAPAR"
    DESCARTADO = "DESCARTADO"


class CartaoCombustivel(str, Enum):
    TICKET_LOG = "TICKET_LOG"
    ALELO = "ALELO"
    VR_AUTO = "VR_AUTO"
    SODEXO_WEX = "SODEXO_WEX"
    OUTRO = "OUTRO"


class OperadoraTag(str, Enum):
    SEM_PARAR = "SEM_PARAR"
    VELOE = "VELOE"
    CONECTCAR = "CONECTCAR"
    MOVE_MAIS = "MOVE_MAIS"


class StatusViagem(str, Enum):
    SOLICITADA = "SOLICITADA"
    APROVADA = "APROVADA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"


class TipoChecklist(str, Enum):
    PRE_VIAGEM = "PRE_VIAGEM"
    POS_VIAGEM = "POS_VIAGEM"


class StatusChecklist(str, Enum):
    APROVADO = "APROVADO"
    REPROVADO_IMPEDIDO = "REPROVADO_IMPEDIDO"
    APROVADO_COM_RESTRICAO = "APROVADO_COM_RESTRICAO"


class StatusIndicacaoMulta(str, Enum):
    PENDENTE = "PENDENTE"
    INDICADO_AGUARDANDO_DETRAN = "INDICADO_AGUARDANDO_DETRAN"
    HOMOLOGADO = "HOMOLOGADO"
    NAO_SE_APLICA = "NAO_SE_APLICA"


class StatusPagamento(str, Enum):
    A_VENCER = "A_VENCER"
    PAGO = "PAGO"
    VENCIDO = "VENCIDO"
    RECURSO = "RECURSO"


# ==========================================
# AUTH & USUÁRIOS
# ==========================================

import re
from pydantic import field_validator

def validar_complexidade_senha(v: Optional[str]) -> Optional[str]:
    """
    Política de Senha Forte - FROTAGOV:
    1. Mínimo de 8 caracteres.
    2. Não aceita senhas exclusivamente numéricas.
    3. Exige letra maiúscula (A-Z), minúscula (a-z), número (0-9) e caractere especial.
    """
    if v is None:
        return v
    if len(v) < 8:
        raise ValueError("A senha deve possuir no mínimo 8 caracteres.")
    if v.isdigit():
        raise ValueError("A senha não pode ser exclusivamente numérica.")
    if not re.search(r'[A-Z]', v):
        raise ValueError("A senha deve conter ao menos uma letra maiúscula.")
    if not re.search(r'[a-z]', v):
        raise ValueError("A senha deve conter ao menos uma letra minúscula.")
    if not re.search(r'[0-9]', v):
        raise ValueError("A senha deve conter ao menos um dígito numérico.")
    if not re.search(r'[^A-Za-z0-9]', v):
        raise ValueError("A senha deve conter ao menos um caractere especial (!, @, #, $, %, etc.).")
    return v


class LoginRequest(BaseModel):
    # Aceita CPF (com ou sem pontuação) ou nome de usuário 'admin'
    username: str = Field(..., min_length=3, max_length=100, description="CPF do usuário ou username")
    password: str = Field(..., min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: Dict[str, Any]


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nome de login único")
    cpf: str = Field(..., min_length=11, max_length=14, description="CPF do usuário (usado no login)")
    nome_completo: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.OPERADOR
    cargo: Optional[str] = "Analista de Frota"
    departamento: Optional[str] = "Logística"
    secretaria: Optional[str] = "SECRETARIA_ADMINISTRACAO"

    @field_validator('password')
    @classmethod
    def validar_senha(cls, v: str) -> str:
        return validar_complexidade_senha(v)


class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    secretaria: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator('password')
    @classmethod
    def validar_senha_opcional(cls, v: Optional[str]) -> Optional[str]:
        return validar_complexidade_senha(v)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    cpf: Optional[str] = None
    nome_completo: str
    email: EmailStr
    role: UserRole
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    secretaria: Optional[str] = "SECRETARIA_ADMINISTRACAO"
    ativo: bool
    created_at: str
    last_login: Optional[str] = None



class APIKeyCreate(BaseModel):
    nome_dispositivo: str = Field(..., min_length=3, max_length=100)
    descricao: Optional[str] = None
    role: UserRole = UserRole.OPERADOR


class APIKeyResponse(BaseModel):
    id: str
    prefix: str
    nome_dispositivo: str
    descricao: Optional[str]
    created_at: str
    api_key_completa: Optional[str] = None  # Mostrada apenas na criação


# ==========================================
# CADASTRO E ATIVOS
# ==========================================

class VeiculoCreate(BaseModel):
    placa: str = Field(..., min_length=7, max_length=8, pattern=r"^[A-Za-z0-9]{7,8}$")
    chassi: str = Field(..., min_length=17, max_length=17)
    renavam: str = Field(..., min_length=9, max_length=11)
    marca: str = Field(..., min_length=2, max_length=50)
    modelo: str = Field(..., min_length=2, max_length=60)
    ano_fabricacao: int = Field(..., ge=1990, le=2030)
    ano_modelo: int = Field(..., ge=1990, le=2030)
    categoria: VeiculoCategoria
    capacidade_carga_kg: float = Field(..., ge=0)
    capacidade_tanque_litros: float = Field(..., gt=0)
    tipo_combustivel: TipoCombustivel
    odometro_atual_km: float = Field(0.0, ge=0)
    horimetro_atual_h: float = Field(0.0, ge=0)
    status: VeiculoStatus = VeiculoStatus.DISPONIVEL
    centro_custo: str = Field("LOGISTICA_GERAL", max_length=50)
    secretaria: str = Field("SECRETARIA_ADMINISTRACAO", max_length=60)


class VeiculoUpdate(BaseModel):
    chassi: Optional[str] = None
    renavam: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano_fabricacao: Optional[int] = None
    ano_modelo: Optional[int] = None
    categoria: Optional[VeiculoCategoria] = None
    capacidade_carga_kg: Optional[float] = None
    capacidade_tanque_litros: Optional[float] = None
    tipo_combustivel: Optional[TipoCombustivel] = None
    odometro_atual_km: Optional[float] = None
    horimetro_atual_h: Optional[float] = None
    status: Optional[VeiculoStatus] = None
    centro_custo: Optional[str] = None
    secretaria: Optional[str] = None


class VeiculoResponse(VeiculoCreate):
    id: str
    created_at: str
    updated_at: str


class MotoristaCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=120)
    cpf: str = Field(..., min_length=11, max_length=14)
    cnh_numero: str = Field(..., min_length=9, max_length=12)
    cnh_categoria: CNHCategoria
    cnh_validade: str  # YYYY-MM-DD
    pontuacao_cnh: int = Field(0, ge=0, le=100)
    status_toxicologico: StatusToxicologico = StatusToxicologico.VALIDO
    data_vencimento_toxicologico: str  # YYYY-MM-DD
    vinculo_contratual: VinculoContratual = VinculoContratual.CLT
    status: MotoristaStatus = MotoristaStatus.ATIVO
    rfid_tag: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None


class MotoristaUpdate(BaseModel):
    nome: Optional[str] = None
    cnh_categoria: Optional[CNHCategoria] = None
    cnh_validade: Optional[str] = None
    pontuacao_cnh: Optional[int] = None
    status_toxicologico: Optional[StatusToxicologico] = None
    data_vencimento_toxicologico: Optional[str] = None
    vinculo_contratual: Optional[VinculoContratual] = None
    status: Optional[MotoristaStatus] = None
    rfid_tag: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None


class MotoristaResponse(MotoristaCreate):
    id: str
    score_conducao: float = 100.0
    created_at: str
    updated_at: str


class EquipamentoEmbarcadoCreate(BaseModel):
    identificador_serial: str = Field(..., min_length=3, max_length=64)
    tipo: TipoEquipamento
    marca_modelo: str = Field(..., min_length=2, max_length=80)
    veiculo_placa: Optional[str] = None
    numero_chip_sim: Optional[str] = None
    status: str = "ATIVO"
    data_instalacao: Optional[str] = None


class EquipamentoEmbarcadoResponse(EquipamentoEmbarcadoCreate):
    id: str
    created_at: str


# ==========================================
# TELEMETRIA E RASTREAMENTO
# ==========================================

class TelemetriaPingInput(BaseModel):
    veiculo_placa: str
    timestamp: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    velocidade_kmh: float = Field(0.0, ge=0.0, le=250.0)
    ignicao: bool
    rpm: Optional[int] = Field(0, ge=0, le=10000)
    odometro_km: Optional[float] = Field(None, ge=0.0)
    motorista_identificador: Optional[str] = None  # CPF, RFID ou Nome
    temperatura_motor_c: Optional[float] = 90.0
    nivel_combustivel_percent: Optional[float] = 80.0
    tensao_bateria_v: Optional[float] = 12.6


class TelemetriaPingResponse(TelemetriaPingInput):
    id: str
    recebido_em: str
    alertas_gerados: List[str] = []


class PosicaoInstantaneaVeiculo(BaseModel):
    veiculo_placa: str
    modelo: str
    motorista_nome: Optional[str] = None
    latitude: float
    longitude: float
    velocidade_kmh: float
    ignicao: bool
    rpm: int
    odometro_km: float
    status_operacional: str
    ultima_atualizacao: str


class EventoConducaoCreate(BaseModel):
    veiculo_placa: str
    motorista_identificador: Optional[str] = None
    timestamp: Optional[str] = None
    tipo_evento: TipoEventoConducao
    gravidade: GravidadeEvento
    valor_registrado: float
    limite_tolerancia: float
    latitude: float
    longitude: float
    detalhes: Optional[str] = None


class EventoConducaoResponse(EventoConducaoCreate):
    id: str
    created_at: str


class CercaEletronicaCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    tipo: TipoCerca = TipoCerca.CIRCULO
    centro_lat: float
    centro_lng: float
    raio_metros: float = Field(500.0, ge=50.0)
    coordenadas_poligono: Optional[List[List[float]]] = None
    regras: RegraCerca = RegraCerca.PERMITIDA
    veiculos_autorizados: List[str] = []
    ativo: bool = True


class CercaEletronicaResponse(CercaEletronicaCreate):
    id: str
    created_at: str


# ==========================================
# MANUTENÇÃO PREVENTIVA E CORRETIVA
# ==========================================

class ItemPecaOS(BaseModel):
    codigo: Optional[str] = None
    descricao: str
    quantidade: float = 1.0
    valor_unitario: float = 0.0
    subtotal: float = 0.0


class ItemServicoOS(BaseModel):
    descricao: str
    horas: float = 1.0
    valor_hora: float = 0.0
    subtotal: float = 0.0


class OrdemServicoCreate(BaseModel):
    numero_os: Optional[str] = None
    veiculo_placa: str
    tipo: TipoOS
    data_abertura: Optional[str] = None
    data_previsao: str
    oficina_credenciada: str
    itens_pecas: List[ItemPecaOS] = []
    servicos: List[ItemServicoOS] = []
    valor_total: float = Field(0.0, ge=0.0)
    odometro_momento_km: float = Field(0.0, ge=0.0)
    observacoes: Optional[str] = None
    status: StatusOS = StatusOS.ABERTA


class OrdemServicoResponse(OrdemServicoCreate):
    id: str
    data_conclusao: Optional[str] = None
    created_at: str
    updated_at: str


class PlanoRevisaoCreate(BaseModel):
    nome_plano: str
    categoria_veiculo: VeiculoCategoria
    intervalo_km: int = Field(10000, ge=1000)
    intervalo_dias: int = Field(180, ge=30)
    descricao_itens: str
    ativo: bool = True


class PlanoRevisaoResponse(PlanoRevisaoCreate):
    id: str
    created_at: str


class PneuCreate(BaseModel):
    numero_fogo: str = Field(..., min_length=3, max_length=30)
    marca_modelo: str
    dimensao: str
    posicao_atual: PosicaoPneu
    veiculo_placa: Optional[str] = None
    pressao_psi: float = Field(110.0, ge=20.0, le=150.0)
    sulco_atual_mm: float = Field(8.0, ge=0.0, le=25.0)
    sulco_original_mm: float = Field(15.0, ge=5.0, le=25.0)
    status: StatusPneu = StatusPneu.BOM
    km_rodado_total: float = 0.0


class PneuUpdate(BaseModel):
    posicao_atual: Optional[PosicaoPneu] = None
    veiculo_placa: Optional[str] = None
    pressao_psi: Optional[float] = None
    sulco_atual_mm: Optional[float] = None
    status: Optional[StatusPneu] = None
    km_rodado_total: Optional[float] = None
    historico_recapagem: Optional[str] = None


class PneuResponse(PneuCreate):
    id: str
    historico_recapagens: List[Dict[str, Any]] = []
    created_at: str
    updated_at: str


# ==========================================
# POSTOS E OFICINAS CREDENCIADAS
# ==========================================

class PostoCredenciadoCreate(BaseModel):
    cnpj: str = Field(..., min_length=14, max_length=18)
    nome_fantasia: str = Field(..., min_length=3, max_length=120)
    razao_social: str = Field(..., min_length=3, max_length=150)
    bandeira: str = Field("BR", max_length=50)
    cidade: str
    uf: str = Field("PR", min_length=2, max_length=2)
    endereco: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "CREDENCIADO"
    contato: Optional[str] = None


class PostoCredenciadoResponse(PostoCredenciadoCreate):
    id: str
    created_at: str


class OficinaCredenciadaCreate(BaseModel):
    cnpj: str = Field(..., min_length=14, max_length=18)
    nome_fantasia: str = Field(..., min_length=3, max_length=120)
    razao_social: str = Field(..., min_length=3, max_length=150)
    especialidade: str = Field("MECANICA_GERAL_PESADOS", max_length=100)
    cidade: str
    uf: str = Field("PR", min_length=2, max_length=2)
    endereco: str
    telefone: Optional[str] = None
    responsavel_tecnico: Optional[str] = None
    status: str = "CREDENCIADA"


class OficinaCredenciadaResponse(OficinaCredenciadaCreate):
    id: str
    created_at: str


# ==========================================
# ABASTECIMENTO E CUSTOS
# ==========================================

class AbastecimentoCreate(BaseModel):
    veiculo_placa: str
    motorista_identificador: Optional[str] = None
    data_hora: Optional[str] = None
    posto_combustivel: str
    posto_credenciado_id: Optional[str] = None
    tipo_combustivel: TipoCombustivel
    litros: float = Field(..., gt=0.0)
    valor_litro: float = Field(..., gt=0.0)
    valor_total: Optional[float] = None
    odometro_km: float = Field(..., ge=0.0)
    cartao_combustivel: CartaoCombustivel = CartaoCombustivel.TICKET_LOG
    numero_comprovante: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AbastecimentoResponse(AbastecimentoCreate):
    id: str
    consumo_calculado_kml: Optional[float] = None
    consumo_l_km: Optional[float] = None
    anomalia_detectada: bool = False
    motivo_anomalia: Optional[str] = None
    created_at: str


class PedagioCreate(BaseModel):
    veiculo_placa: str
    data_hora: Optional[str] = None
    concessionaria_praca: str
    valor: float = Field(..., gt=0.0)
    operadora_tag: OperadoraTag = OperadoraTag.SEM_PARAR
    status_cobranca: str = "DEBITADO"


class PedagioResponse(PedagioCreate):
    id: str
    created_at: str


# ==========================================
# VIAGENS, DESPACHO E ROTAS
# ==========================================

class SolicitacaoViagemCreate(BaseModel):
    veiculo_placa: str
    motorista_identificador: str
    centro_custo: str
    origem: str
    destino: str
    data_partida_prevista: str
    data_retorno_prevista: str
    distancia_estimada_km: float = Field(..., ge=1.0)
    eta_estimado_minutos: int = Field(..., ge=1)
    observacoes: Optional[str] = None


class SolicitacaoViagemResponse(SolicitacaoViagemCreate):
    id: str
    codigo_viagem: str
    status: StatusViagem = StatusViagem.SOLICITADA
    created_at: str


class ItemChecklist(BaseModel):
    item: str
    conforme: bool
    observacao: Optional[str] = None


class ChecklistDigitalCreate(BaseModel):
    viagem_id: Optional[str] = None
    veiculo_placa: str
    motorista_identificador: str
    tipo: TipoChecklist
    data_hora: Optional[str] = None
    itens: List[ItemChecklist]
    fotos_urls: List[str] = []
    assinatura_digital_hash: Optional[str] = None


class ChecklistDigitalResponse(ChecklistDigitalCreate):
    id: str
    status_aprovacao: StatusChecklist
    motivo_reprovacao: Optional[str] = None
    created_at: str


# ==========================================
# COMPLIANCE E MULTAS
# ==========================================

class MultaCreate(BaseModel):
    auto_infracao: str = Field(..., min_length=3, max_length=50)
    veiculo_placa: str
    motorista_identificador: Optional[str] = None
    data_hora_infracao: str
    local: str
    codigo_infracao: str
    descricao_infracao: str
    pontos: int = Field(0, ge=0, le=20)
    valor_multa: float = Field(..., gt=0.0)
    vencimento_pagamento: str
    limite_indicacao_condutor: str
    status_indicacao: StatusIndicacaoMulta = StatusIndicacaoMulta.PENDENTE
    status_pagamento: StatusPagamento = StatusPagamento.A_VENCER


class IndicarCondutorRequest(BaseModel):
    motorista_identificador: str
    documento_cnh: str
    data_indicacao: Optional[str] = None
    protocolo_detran: Optional[str] = None


class MultaResponse(MultaCreate):
    id: str
    protocolo_detran: Optional[str] = None
    created_at: str
    updated_at: str


class SinistroCreate(BaseModel):
    numero_sinistro: Optional[str] = None
    veiculo_placa: str
    motorista_identificador: Optional[str] = None
    data_hora: str
    descricao: str
    seguradora: str
    apolice_numero: str
    valor_estimado_dano: float = Field(0.0, ge=0.0)
    status: str = "ABERTO"


class SinistroResponse(SinistroCreate):
    id: str
    created_at: str


class DocumentoVencimentoCreate(BaseModel):
    veiculo_placa: str
    tipo_documento: str  # IPVA, LICENCIAMENTO, SPVAT, SEGURO_CASCO
    ano_exercicio: int
    data_vencimento: str
    valor: float = Field(..., ge=0.0)
    status_pagamento: StatusPagamento = StatusPagamento.A_VENCER


class DocumentoVencimentoResponse(DocumentoVencimentoCreate):
    id: str
    created_at: str


# ==========================================
# RELATÓRIOS E KPI
# ==========================================

class DashboardKPIs(BaseModel):
    total_veiculos: int
    veiculos_em_viagem: int
    veiculos_disponiveis: int
    veiculos_manutencao: int
    total_motoristas: int
    motoristas_ativos: int
    alertas_hoje: int
    os_abertas: int
    custo_total_mes: float
    consumo_medio_frota_kml: float
    score_medio_conducao: float


class RelatorioTCOResponse(BaseModel):
    veiculo_placa: str
    modelo: str
    categoria: str
    custo_aquisicao: float
    custo_manutencao_total: float
    custo_combustivel_total: float
    custo_pneus_total: float
    custo_pedagios_total: float
    custo_multas_total: float
    custo_seguros_taxas: float
    custo_total_operacional: float
    km_total_rodado: float
    cpk_reais_por_km: float


class RankingMotoristaResponse(BaseModel):
    motorista_id: str
    nome: str
    cnh_numero: str
    cnh_categoria: str
    score_geral: float
    total_km_conduzido: float
    eventos_agressivos_count: int
    consumo_medio_kml: float
    multas_vinculadas_count: int
    classificacao: str  # "EXCELENTE", "BOM", "REGULAR", "CRITICO"


class RelatorioSecretariaItem(BaseModel):
    secretaria: str
    total_veiculos: int
    km_total_rodado: float
    gasto_combustivel: float
    gasto_manutencao: float
    gasto_pedagios: float
    gasto_total: float
    custo_por_km: float
    consumo_medio_kml: float


# ==========================================
# RELATÓRIOS E INTELIGÊNCIA PRESCRITIVA AVANÇADA
# ==========================================

class ManutencaoPreventivaDinamicaItem(BaseModel):
    veiculo_placa: str
    modelo: str
    secretaria: str
    data_hora_recomendada: str
    tempo_ocioso_estimado_horas: float
    score_desgaste_pecas: float
    estilo_conducao_fator: float
    justificativa: str
    oficina_credenciada_sugerida: str


class AlertaPrevencaoFalhaCritica(BaseModel):
    veiculo_placa: str
    modelo: str
    componente: str
    prazo_limite_horas: int
    probabilidade_pane: float
    custo_pane_estrada_estimado: float
    custo_troca_preventiva: float
    economia_prescritiva_evitada: float
    mensagem_prescritiva: str


class GestaoPneusOtimizadaItem(BaseModel):
    veiculo_placa: str
    numero_fogo: str
    posicao_atual: str
    sulco_atual_mm: float
    acao_recomendada: str  # ROTACAO, RECAUCHUTAGEM, DESCARTE_IMEDIATO, REPOSICAO
    km_estimado_proxima_acao: float
    marca_modelo_reposicao_sugerida: str
    custo_estimado: float
    justificativa_tecnica: str


class AcaoReducaoCombustivelItem(BaseModel):
    veiculo_placa: str
    motorista_identificador: str
    secretaria: str
    desvio_consumo_percentual: float
    causa_principal: str
    acao_prescritiva: str
    economia_mensal_estimada_reais: float


class EstrategiaAbastecimentoRotaItem(BaseModel):
    veiculo_placa: str
    autonomia_atual_km: float
    rota_ativa: str
    posto_parceiro_recomendado: str
    cidade_km_rota: str
    preco_litro: float
    litros_prescritos: float
    custo_estimado: float
    economia_vs_media_rota: float
    justificativa_estrategica: str


class RedirecionamentoTempoRealItem(BaseModel):
    viagem_id: str
    veiculo_placa: str
    origem: str
    destino: str
    motivo_alerta: str
    rota_original_eta: str
    rota_prescrita_alternativa: str
    tempo_economizado_minutos: int
    impacto_prazo: str


class DimensionamentoFrotaItem(BaseModel):
    secretaria_ou_filial: str
    veiculos_alocados: int
    taxa_ocupacao_atual: float
    taxa_ociosidade_percentual: float
    prescricao_dimensionamento: str
    qtd_veiculos_ajuste: int
    impacto_financeiro_anual: float


class PlanoTreinamentoMotoristaItem(BaseModel):
    motorista_id: str
    nome: str
    score_seguranca: float
    principais_desvios: List[str]
    modulos_treinamento_prescritos: List[str]
    prioridade: str
    potencial_reducao_acidentes_percentual: float


class EscalaTrabalhoInteligenteItem(BaseModel):
    motorista_id: str
    nome: str
    horas_descanso_ultimas_24h: float
    score_fadiga_estimado: float
    viagem_prescrita_id: Optional[str] = None
    tipo_rota_afinidade: str
    status_escala: str
    recomendacao_seguranca: str


class DesinvestimentoRenovacaoTCOItem(BaseModel):
    veiculo_placa: str
    modelo: str
    ano_fabricacao: int
    valor_venal_fipe: float
    custo_manutencao_acumulado: float
    razao_gasto_venal: float
    mes_ideal_venda_leilao: str
    retorno_financeiro_maximo_estimado: float
    economia_perda_evitada: float
    prescricao_decisoria: str


class RelatorioPrescritivoConsolidadoResponse(BaseModel):
    timestamp: str
    total_prescricoes_ativas: int
    economia_potencial_total_reais: float
    manutencao_preventiva_dinamica: List[ManutencaoPreventivaDinamicaItem]
    prevencao_falhas_criticas: List[AlertaPrevencaoFalhaCritica]
    gestao_pneus_otimizada: List[GestaoPneusOtimizadaItem]
    acoes_reducao_combustivel: List[AcaoReducaoCombustivelItem]
    estrategia_abastecimento: List[EstrategiaAbastecimentoRotaItem]
    redirecionamento_logistica: List[RedirecionamentoTempoRealItem]
    dimensionamento_frota: List[DimensionamentoFrotaItem]
    treinamento_motoristas: List[PlanoTreinamentoMotoristaItem]
    escala_trabalho_inteligente: List[EscalaTrabalhoInteligenteItem]
    desinvestimento_renovacao_tco: List[DesinvestimentoRenovacaoTCOItem]


# =====================================================================
# GESTÃO DE CARTÕES MAGNÉTICOS / MICROPROCESSADOS & CONTRATO SEA/SC
# =====================================================================

class TecnologiaCartao(str, Enum):
    CHIP_MICROPROCESSADO = "CHIP_MICROPROCESSADO"
    TARJA_MAGNETICA = "TARJA_MAGNETICA"
    NFC_CONTACTLESS = "NFC_CONTACTLESS"
    VIRTUAL_TOKEN = "VIRTUAL_TOKEN"


class TipoCartaoFrota(str, Enum):
    CARTAO_VEICULO = "CARTAO_VEICULO"
    CARTAO_EMBARCACAO = "CARTAO_EMBARCACAO"
    CARTAO_GERADOR = "CARTAO_GERADOR"
    CARTAO_MAQUINA = "CARTAO_MAQUINA"
    CARTAO_CONDUTOR = "CARTAO_CONDUTOR"
    CARTAO_COTA_SECRETARIA = "CARTAO_COTA_SECRETARIA"


class StatusCartao(str, Enum):
    ATIVO = "ATIVO"
    BLOQUEADO_SALDO = "BLOQUEADO_SALDO"
    BLOQUEADO_FRAUDE = "BLOQUEADO_FRAUDE"
    CANCELADO = "CANCELADO"
    EXPIRADO = "EXPIRADO"


class CartaoFrotaCreate(BaseModel):
    numero_mascarado: str = Field(..., min_length=12, max_length=24)
    tecnologia: TecnologiaCartao = TecnologiaCartao.CHIP_MICROPROCESSADO
    tipo_cartao: TipoCartaoFrota = TipoCartaoFrota.CARTAO_VEICULO
    identificador_ativo: str  # Placa do veículo, prefixo embarcação, patrimônio do gerador ou máquina
    secretaria: str = "SECRETARIA_ADMINISTRACAO"
    orgao_vinculado: str = "Governo do Estado de Santa Catarina"
    limite_mensal_reais: float = Field(..., gt=0.0)
    saldo_disponivel_reais: float = Field(..., ge=0.0)
    combustiveis_autorizados: List[str] = ["DIESEL_S10", "GASOLINA_COMUM", "LUBRIFICANTE", "ADITIVO_ARLA32"]
    exige_odometro_horimetro: bool = True
    permite_final_de_semana: bool = False
    validade: str  # YYYY-MM
    status: StatusCartao = StatusCartao.ATIVO


class CartaoFrotaResponse(CartaoFrotaCreate):
    id: str
    total_gasto_mes_atual: float = 0.0
    ultima_transacao_em: Optional[str] = None
    created_at: str
    updated_at: str


class TransacaoCartaoCreate(BaseModel):
    cartao_id: str
    posto_credenciado_id: str
    posto_nome: str
    cidade: str
    uf: str = "SC"
    tipo_ativo: VeiculoCategoria
    identificador_ativo: str  # Placa ou Prefixo
    motorista_ou_operador: str
    tipo_insumo: TipoCombustivel  # Combustível, Lubrificante, Aditivo ou Óleo
    quantidade_litros_ou_unidades: float = Field(..., gt=0.0)
    valor_unitario: float = Field(..., gt=0.0)
    valor_total: float = Field(..., gt=0.0)
    odometro_ou_horimetro: float = Field(..., ge=0.0)
    comprovante_fiscal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TransacaoCartaoResponse(TransacaoCartaoCreate):
    id: str
    autorizado: bool
    codigo_autorizacao: str
    mensagem_status: str
    anomalia_detectada: bool = False
    motivo_anomalia: Optional[str] = None
    timestamp: str


# =====================================================================
# MATRIZ DE QUALIDADE DE SOFTWARE ISO/IEC 25010 & NORMAS CORRELATAS
# =====================================================================

class ISO25010Subcaracteristica(BaseModel):
    nome: str
    descricao: str
    status: str = "CONFORME"
    score_aderencia: float = Field(100.0, ge=0.0, le=100.0)
    evidencia_tecnica: str


class ISO25010Caracteristica(BaseModel):
    codigo: str
    nome: str
    nome_ingles: str
    descricao: str
    score_geral: float = Field(..., ge=0.0, le=100.0)
    status_conformidade: str = "TOTALMENTE_CONFORME"
    subcaracteristicas: List[ISO25010Subcaracteristica]
    controles_implementados: List[str]


class NormaCorrelataItem(BaseModel):
    norma: str
    titulo: str
    escopo_aplicado: str
    status: str
    evidencias: List[str]


class ISO25010RelatorioCompleto(BaseModel):
    timestamp_auditoria: str
    sistema_avaliado: str
    versao: str
    orgao_demandante: str
    objeto_contratual: str
    score_global_qualidade: float
    status_certificacao: str
    caracteristicas_iso25010: List[ISO25010Caracteristica]
    normas_correlatas: List[NormaCorrelataItem]
    resumo_executivo: str



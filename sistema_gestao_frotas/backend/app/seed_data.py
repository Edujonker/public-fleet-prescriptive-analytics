"""
Módulo de Inicialização e População de Dados (Seed Data).
Garante base rica e realista para demonstração completa e testes imediatos em Linux e Windows.
"""

from datetime import datetime, timezone, timedelta
import uuid

from app.database import get_database
from app.security.crypto import hash_password, hash_api_key
from app.models.schemas import UserRole, VeiculoCategoria, VeiculoStatus, TipoCombustivel, CNHCategoria


def seed_database_if_empty():
    """Popula a base MongoDB/Mongita se estiver vazia."""
    db = get_database()
    agora_iso = datetime.now(timezone.utc).isoformat()
    hoje = datetime.now()

    # 1. Usuários Padrão (FROTAGOV)
    usuarios_padrao = [
        {
            "id": "usr-admin-frotagov-01",
            "username": "admin",
            "cpf": "000.000.000-00",
            "nome_completo": "Administrador Geral FROTAGOV",
            "email": "admin@frotagov.sc.gov.br",
            "password_hash": hash_password("Iprev@2021"),
            "role": UserRole.ADMIN.value,
            "cargo": "Administrador Geral do Sistema",
            "departamento": "Diretoria de Tecnologia e Governança",
            "secretaria": "SECRETARIA_ADMINISTRACAO",
            "ativo": True,
            "created_at": agora_iso
        },
        {
            "id": "usr-gestor-frotagov-02",
            "username": "gestor",
            "cpf": "111.222.333-44",
            "nome_completo": "Carlos Eduardo Siqueira",
            "email": "gestor@frotagov.sc.gov.br",
            "password_hash": hash_password("Gestor@Fleet2026!"),
            "role": UserRole.GESTOR_FROTA.value,
            "cargo": "Gestor de Frotas e Contratos",
            "departamento": "Gerência de Transporte Oficial",
            "secretaria": "SECRETARIA_ADMINISTRACAO",
            "ativo": True,
            "created_at": agora_iso
        },
        {
            "id": "usr-operador-frotagov-03",
            "username": "operador",
            "cpf": "222.333.444-55",
            "nome_completo": "Mariana Oliveira",
            "email": "operador@frotagov.sc.gov.br",
            "password_hash": hash_password("Operador@Fleet2026!"),
            "role": UserRole.OPERADOR.value,
            "cargo": "Controladora de Tráfego e Despacho",
            "departamento": "CCO - Centro de Controle Operacional",
            "secretaria": "POLICIA_MILITAR_SC",
            "ativo": True,
            "created_at": agora_iso
        },
        {
            "id": "usr-motorista-frotagov-04",
            "username": "motorista",
            "cpf": "333.444.555-66",
            "nome_completo": "Sebastião da Silva",
            "email": "sebastiao@frotagov.sc.gov.br",
            "password_hash": hash_password("Motorista@Fleet2026!"),
            "role": UserRole.MOTORISTA.value,
            "cargo": "Motorista Operacional",
            "departamento": "Transporte e Logística",
            "secretaria": "SAMU_SAUDE_SC",
            "ativo": True,
            "created_at": agora_iso
        }
    ]

    if db.users.count_documents({}) == 0:
        db.users.insert_many(usuarios_padrao)
    else:
        # Garantir atualização do admin com a senha Iprev@2021 e CPF
        admin_hash = hash_password("Iprev@2021")
        db.users.update_one(
            {"username": "admin"},
            {"$set": {
                "password_hash": admin_hash,
                "cpf": "000.000.000-00",
                "nome_completo": "Administrador Geral FROTAGOV",
                "ativo": True
            }}
        )
        if hasattr(db, "usuarios"):
            db.usuarios.update_one(
                {"username": "admin"},
                {"$set": {
                    "password_hash": admin_hash,
                    "cpf": "000.000.000-00",
                    "nome_completo": "Administrador Geral FROTAGOV",
                    "ativo": True
                }}
            )


    # 2. Chave de API IoT Gateway
    if db.api_keys.count_documents({}) == 0:
        key_iot = "flt_gateway_iot_live_sim_2026_seckey"
        db.api_keys.insert_one({
            "id": str(uuid.uuid4()),
            "prefix": "flt_gate...",
            "nome_dispositivo": "Gateway IoT Teltonika / Coban Principal",
            "descricao": "Chave de ingestão de telemetria OBD2/CANbus em tempo real",
            "key_hash": hash_api_key(key_iot),
            "role": UserRole.OPERADOR.value,
            "created_at": agora_iso
        })

    # 3. Veículos (10 veículos de várias categorias)
    if db.veiculos.count_documents({}) == 0:
        veiculos_data = [
            {
                "id": str(uuid.uuid4()),
                "placa": "BRA2E19",
                "chassi": "9BWZZZ377VT004182",
                "renavam": "01234567891",
                "marca": "Scania",
                "modelo": "R 450 Highline 6x2",
                "ano_fabricacao": 2023,
                "ano_modelo": 2024,
                "categoria": VeiculoCategoria.PESADO.value,
                "capacidade_carga_kg": 45000.0,
                "capacidade_tanque_litros": 600.0,
                "tipo_combustivel": TipoCombustivel.DIESEL.value,
                "odometro_atual_km": 142580.0,
                "horimetro_atual_h": 3840.0,
                "status": VeiculoStatus.EM_VIAGEM.value,
                "centro_custo": "TRANSPORTE_PESADO_SUL",
                "secretaria": "SECRETARIA_OBRAS",
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "placa": "RHO4A21",
                "chassi": "9BFZZZ244VP009134",
                "renavam": "01234567892",
                "marca": "Volvo",
                "modelo": "FH 540 Globetrotter 6x4",
                "ano_fabricacao": 2024,
                "ano_modelo": 2024,
                "categoria": VeiculoCategoria.PESADO.value,
                "capacidade_carga_kg": 57000.0,
                "capacidade_tanque_litros": 890.0,
                "tipo_combustivel": TipoCombustivel.DIESEL.value,
                "odometro_atual_km": 87320.0,
                "horimetro_atual_h": 2110.0,
                "status": VeiculoStatus.EM_VIAGEM.value,
                "centro_custo": "TRANSPORTE_PESADO_SUL",
                "secretaria": "SECRETARIA_OBRAS",
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "placa": "BCX9D45",
                "chassi": "8A1ZZZ511VP112948",
                "renavam": "01234567893",
                "marca": "Mercedes-Benz",
                "modelo": "Sprinter 416 Furgão Extra Longo",
                "ano_fabricacao": 2023,
                "ano_modelo": 2023,
                "categoria": VeiculoCategoria.UTILITARIO.value,
                "capacidade_carga_kg": 2100.0,
                "capacidade_tanque_litros": 75.0,
                "tipo_combustivel": TipoCombustivel.DIESEL.value,
                "odometro_atual_km": 49200.0,
                "horimetro_atual_h": 1420.0,
                "status": VeiculoStatus.DISPONIVEL.value,
                "centro_custo": "DISTRIBUICAO_URBANA",
                "secretaria": "SECRETARIA_SAUDE",
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "placa": "QNY7J12",
                "chassi": "9BDZZZ178VT334812",
                "renavam": "01234567894",
                "marca": "Iveco",
                "modelo": "Daily 30-130 Chassi Cabine",
                "ano_fabricacao": 2022,
                "ano_modelo": 2023,
                "categoria": VeiculoCategoria.UTILITARIO.value,
                "capacidade_carga_kg": 1800.0,
                "capacidade_tanque_litros": 80.0,
                "tipo_combustivel": TipoCombustivel.DIESEL.value,
                "odometro_atual_km": 68900.0,
                "horimetro_atual_h": 1980.0,
                "status": VeiculoStatus.MANUTENCAO.value,
                "centro_custo": "DISTRIBUICAO_URBANA",
                "secretaria": "SECRETARIA_EDUCACAO",
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "placa": "RLF5C88",
                "chassi": "8AJZZZ331WP901824",
                "renavam": "01234567895",
                "marca": "Toyota",
                "modelo": "Hilux Cabine Dupla 4x4 PowerPack",
                "ano_fabricacao": 2023,
                "ano_modelo": 2024,
                "categoria": VeiculoCategoria.UTILITARIO.value,
                "capacidade_carga_kg": 1000.0,
                "capacidade_tanque_litros": 80.0,
                "tipo_combustivel": TipoCombustivel.DIESEL.value,
                "odometro_atual_km": 38400.0,
                "horimetro_atual_h": 920.0,
                "status": VeiculoStatus.DISPONIVEL.value,
                "centro_custo": "SUPERVISAO_CAMPO",
                "secretaria": "SECRETARIA_SEGURANCA",
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "placa": "FGH3B10",
                "chassi": "9BGZZZ144VR771239",
                "renavam": "01234567896",
                "marca": "Chevrolet",
                "modelo": "Onix Plus 1.0 Turbo Premier",
                "ano_fabricacao": 2024,
                "ano_modelo": 2024,
                "categoria": VeiculoCategoria.LEVE.value,
                "capacidade_carga_kg": 450.0,
                "capacidade_tanque_litros": 44.0,
                "tipo_combustivel": TipoCombustivel.FLEX.value,
                "odometro_atual_km": 19850.0,
                "horimetro_atual_h": 410.0,
                "status": VeiculoStatus.DISPONIVEL.value,
                "centro_custo": "ADMINISTRATIVO_VENDAS",
                "secretaria": "SECRETARIA_ADMINISTRACAO",
                "created_at": agora_iso,
                "updated_at": agora_iso
            }
        ]
        db.veiculos.insert_many(veiculos_data)

    # 3.1 Postos Credenciados
    if db.postos_credenciados.count_documents({}) == 0:
        postos_demo = [
            {
                "id": str(uuid.uuid4()),
                "cnpj": "12.345.678/0001-90",
                "nome_fantasia": "Posto Ipiranga RodoSul BR-101",
                "razao_social": "Auto Posto RodoSul Combustíveis Ltda",
                "bandeira": "Ipiranga",
                "cidade": "São José dos Pinhais",
                "uf": "PR",
                "endereco": "BR-101 Km 140 - Trevo Afonso Pena",
                "latitude": -25.5312,
                "longitude": -49.2010,
                "status": "CREDENCIADO",
                "contato": "(41) 3382-9011 / comercial@rodosul.com.br",
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "cnpj": "98.765.432/0001-10",
                "nome_fantasia": "Auto Posto Shell Curitiba Centro",
                "razao_social": "PetroCentro Distribuidora de Derivados S/A",
                "bandeira": "Shell",
                "cidade": "Curitiba",
                "uf": "PR",
                "endereco": "Av. Sete de Setembro, 2800 - Batel",
                "latitude": -25.4389,
                "longitude": -49.2785,
                "status": "CREDENCIADO",
                "contato": "(41) 3224-5500",
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "cnpj": "45.123.890/0001-55",
                "nome_fantasia": "Posto Petrobras Marumby Porto",
                "razao_social": "Comércio Varejista Marumby Ltda",
                "bandeira": "Petrobras",
                "cidade": "Paranaguá",
                "uf": "PR",
                "endereco": "Av. Bento Rocha, 1500 - Porto",
                "latitude": -25.5160,
                "longitude": -48.5110,
                "status": "CREDENCIADO",
                "contato": "(41) 3422-7788",
                "created_at": agora_iso
            }
        ]
        db.postos_credenciados.insert_many(postos_demo)

    # 3.2 Oficinas e Fornecedores Credenciados
    if db.oficinas_credenciadas.count_documents({}) == 0:
        oficinas_demo = [
            {
                "id": str(uuid.uuid4()),
                "cnpj": "23.456.789/0001-22",
                "nome_fantasia": "Diesel Tech Serviços Especializados",
                "razao_social": "Mecânica Pesada Diesel Tech Ltda",
                "especialidade": "MECANICA_DIESEL_ELETRONICA",
                "cidade": "São José dos Pinhais",
                "uf": "PR",
                "endereco": "Rua Rui Barbosa, 4100",
                "telefone": "(41) 3383-7722",
                "responsavel_tecnico": "Eng. Paulo Roberto Antunes",
                "status": "CREDENCIADA",
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "cnpj": "34.567.890/0001-33",
                "nome_fantasia": "Centro Automotivo RodoBrasil",
                "razao_social": "RodoBrasil Manutenção e Pneus EIRELI",
                "especialidade": "SUSPENSAO_FREIOS_PNEUS",
                "cidade": "Curitiba",
                "uf": "PR",
                "endereco": "Linha Verde, 12890 - Pinheirinho",
                "telefone": "(41) 3012-9988",
                "responsavel_tecnico": "Claudio Mendonça",
                "status": "CREDENCIADA",
                "created_at": agora_iso
            }
        ]
        db.oficinas_credenciadas.insert_many(oficinas_demo)

    # 4. Motoristas
    if db.motoristas.count_documents({}) == 0:
        motoristas_data = [
            {
                "id": str(uuid.uuid4()),
                "nome": "Sebastião da Silva",
                "cpf": "123.456.789-01",
                "cnh_numero": "04981274610",
                "cnh_categoria": CNHCategoria.AE.value,
                "cnh_validade": (hoje + timedelta(days=420)).strftime("%Y-%m-%d"),
                "pontuacao_cnh": 4,
                "status_toxicologico": "VALIDO",
                "data_vencimento_toxicologico": (hoje + timedelta(days=180)).strftime("%Y-%m-%d"),
                "vinculo_contratual": "CLT",
                "status": "ATIVO",
                "rfid_tag": "TAG-RFID-9901",
                "email": "sebastiao@frotas.corp.br",
                "telefone": "(41) 99123-4567",
                "score_conducao": 94.0,
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "nome": "Roberto Carlos Mendes",
                "cpf": "234.567.890-12",
                "cnh_numero": "05192837401",
                "cnh_categoria": CNHCategoria.E.value,
                "cnh_validade": (hoje + timedelta(days=210)).strftime("%Y-%m-%d"),
                "pontuacao_cnh": 7,
                "status_toxicologico": "VALIDO",
                "data_vencimento_toxicologico": (hoje + timedelta(days=75)).strftime("%Y-%m-%d"),
                "vinculo_contratual": "CLT",
                "status": "ATIVO",
                "rfid_tag": "TAG-RFID-9902",
                "email": "roberto.mendes@frotas.corp.br",
                "telefone": "(41) 98877-6655",
                "score_conducao": 88.5,
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "nome": "Luciana Barbosa",
                "cpf": "345.678.901-23",
                "cnh_numero": "03819204918",
                "cnh_categoria": CNHCategoria.D.value,
                "cnh_validade": (hoje + timedelta(days=340)).strftime("%Y-%m-%d"),
                "pontuacao_cnh": 0,
                "status_toxicologico": "VALIDO",
                "data_vencimento_toxicologico": (hoje + timedelta(days=260)).strftime("%Y-%m-%d"),
                "vinculo_contratual": "CLT",
                "status": "ATIVO",
                "rfid_tag": "TAG-RFID-9903",
                "email": "luciana.barbosa@frotas.corp.br",
                "telefone": "(47) 99234-1122",
                "score_conducao": 98.0,
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "nome": "Fernando Henrique Ramos",
                "cpf": "456.789.012-34",
                "cnh_numero": "06718294012",
                "cnh_categoria": CNHCategoria.B.value,
                "cnh_validade": (hoje + timedelta(days=15)).strftime("%Y-%m-%d"),  # Alerta a vencer!
                "pontuacao_cnh": 12,
                "status_toxicologico": "VALIDO",
                "data_vencimento_toxicologico": (hoje + timedelta(days=300)).strftime("%Y-%m-%d"),
                "vinculo_contratual": "TERCEIRIZADO",
                "status": "ATIVO",
                "rfid_tag": "TAG-RFID-9904",
                "email": "fernando.ramos@frotas.corp.br",
                "telefone": "(11) 98112-9988",
                "score_conducao": 76.0,
                "created_at": agora_iso,
                "updated_at": agora_iso
            }
        ]
        db.motoristas.insert_many(motoristas_data)

    # 5. Cercas Eletrônicas (Geofences)
    if db.cercas_eletronicas.count_documents({}) == 0:
        cercas = [
            {
                "id": str(uuid.uuid4()),
                "nome": "CD Logístico Central - São José dos Pinhais (PR)",
                "tipo": "CIRCULO",
                "centro_lat": -25.5342,
                "centro_lng": -49.2064,
                "raio_metros": 1200.0,
                "regras": "PERMITIDA",
                "veiculos_autorizados": ["BRA2E19", "RHO4A21", "BCX9D45", "QNY7J12", "RLF5C88"],
                "ativo": True,
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "nome": "Terminal Portuário de Paranaguá (PR)",
                "tipo": "CIRCULO",
                "centro_lat": -25.5186,
                "centro_lng": -48.5098,
                "raio_metros": 2500.0,
                "regras": "PERMITIDA",
                "veiculos_autorizados": ["BRA2E19", "RHO4A21"],
                "ativo": True,
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "nome": "Zona de Restrição Central - São Paulo (SP)",
                "tipo": "CIRCULO",
                "centro_lat": -23.5505,
                "centro_lng": -46.6333,
                "raio_metros": 4500.0,
                "regras": "PROIBIDA",  # Restrição para caminhões pesados
                "veiculos_autorizados": [],
                "ativo": True,
                "created_at": agora_iso
            }
        ]
        db.cercas_eletronicas.insert_many(cercas)

    # 6. Planos de Revisão Preventiva
    if db.planos_revisao.count_documents({}) == 0:
        planos = [
            {
                "id": str(uuid.uuid4()),
                "nome_plano": "Revisão Preventiva Básica Linha Leve (10.000 km)",
                "categoria_veiculo": VeiculoCategoria.LEVE.value,
                "intervalo_km": 10000,
                "intervalo_dias": 180,
                "descricao_itens": "Troca de óleo sintético, filtro de óleo, filtro de ar, filtro de combustível, alinhamento e balanceamento.",
                "ativo": True,
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "nome_plano": "Revisão Intermediária Utilitários (15.000 km)",
                "categoria_veiculo": VeiculoCategoria.UTILITARIO.value,
                "intervalo_km": 15000,
                "intervalo_dias": 180,
                "descricao_itens": "Troca de óleo diesel 5W30, filtros, verificação de pastilhas de freio, suspensão e estepe.",
                "ativo": True,
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "nome_plano": "Plano Mestre Linha Pesada / Carretas (20.000 km)",
                "categoria_veiculo": VeiculoCategoria.PESADO.value,
                "intervalo_km": 20000,
                "intervalo_dias": 90,
                "descricao_itens": "Troca lubrificante de motor 15W40, lubrificação do chassi e 5ª roda, regulagem de freios cuícas, drenagem filtro racor, conferência de sulco dos pneus.",
                "ativo": True,
                "created_at": agora_iso
            }
        ]
        db.planos_revisao.insert_many(planos)

    # 7. Posições Instantâneas Iniciais (para o mapa Leaflet exibir de imediato)
    if db.posicoes_instantaneas.count_documents({}) == 0:
        posicoes_demo = [
            {
                "veiculo_placa": "BRA2E19",
                "modelo": "Scania R 450",
                "motorista_identificador": "Sebastião da Silva",
                "latitude": -25.4800,
                "longitude": -49.1200,
                "velocidade_kmh": 82.0,
                "ignicao": True,
                "rpm": 1450,
                "odometro_km": 142580.0,
                "temperatura_motor_c": 88.0,
                "nivel_combustivel_percent": 74.0,
                "tensao_bateria_v": 27.8,
                "status_operacional": "EM_VIAGEM",
                "ultima_atualizacao": agora_iso
            },
            {
                "veiculo_placa": "RHO4A21",
                "modelo": "Volvo FH 540",
                "motorista_identificador": "Roberto Carlos Mendes",
                "latitude": -25.5200,
                "longitude": -48.6500,
                "velocidade_kmh": 78.0,
                "ignicao": True,
                "rpm": 1380,
                "odometro_km": 87320.0,
                "temperatura_motor_c": 91.0,
                "nivel_combustivel_percent": 62.0,
                "tensao_bateria_v": 28.1,
                "status_operacional": "EM_VIAGEM",
                "ultima_atualizacao": agora_iso
            },
            {
                "veiculo_placa": "BCX9D45",
                "modelo": "Mercedes-Benz Sprinter",
                "motorista_identificador": "Luciana Barbosa",
                "latitude": -25.4300,
                "longitude": -49.2700,
                "velocidade_kmh": 0.0,
                "ignicao": False,
                "rpm": 0,
                "odometro_km": 49200.0,
                "temperatura_motor_c": 45.0,
                "nivel_combustivel_percent": 88.0,
                "tensao_bateria_v": 12.6,
                "status_operacional": "ESTACIONADO",
                "ultima_atualizacao": agora_iso
            },
            {
                "veiculo_placa": "RLF5C88",
                "modelo": "Toyota Hilux",
                "motorista_identificador": "Fernando Henrique Ramos",
                "latitude": -25.3900,
                "longitude": -49.2300,
                "velocidade_kmh": 45.0,
                "ignicao": True,
                "rpm": 1800,
                "odometro_km": 38400.0,
                "temperatura_motor_c": 86.0,
                "nivel_combustivel_percent": 55.0,
                "tensao_bateria_v": 13.9,
                "status_operacional": "EM_VIAGEM",
                "ultima_atualizacao": agora_iso
            }
        ]
        db.posicoes_instantaneas.insert_many(posicoes_demo)

    # 8. Pneus cadastrados com alerta de sulco CONTRAN
    if db.pneus.count_documents({}) == 0:
        pneus_demo = [
            {
                "id": str(uuid.uuid4()),
                "numero_fogo": "FOG-10492",
                "marca_modelo": "Michelin X Multiway 3D XZE",
                "dimensao": "295/80 R22.5",
                "posicao_atual": "DIANTEIRO_ESQ",
                "veiculo_placa": "BRA2E19",
                "pressao_psi": 120.0,
                "sulco_atual_mm": 9.2,
                "sulco_original_mm": 16.0,
                "status": "BOM",
                "km_rodado_total": 45000.0,
                "historico_recapagens": [],
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "numero_fogo": "FOG-10493",
                "marca_modelo": "Michelin X Multiway 3D XZE",
                "dimensao": "295/80 R22.5",
                "posicao_atual": "DIANTEIRO_DIR",
                "veiculo_placa": "BRA2E19",
                "pressao_psi": 118.0,
                "sulco_atual_mm": 1.4,  # ALERTA CRÍTICO CONTRAN (< 1.6mm)
                "sulco_original_mm": 16.0,
                "status": "CRITICO",
                "km_rodado_total": 82000.0,
                "historico_recapagens": [{"data": (hoje - timedelta(days=120)).strftime("%Y-%m-%d"), "descricao": "1ª Recapagem Bandag BDR-HT", "km_momento": 51000.0}],
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "numero_fogo": "FOG-20811",
                "marca_modelo": "Bridgestone R268 Ecopia",
                "dimensao": "295/80 R22.5",
                "posicao_atual": "TRASEIRO_ESQ_EXT",
                "veiculo_placa": "RHO4A21",
                "pressao_psi": 125.0,
                "sulco_atual_mm": 2.8,  # Próximo de recapagem (<= 3.0mm)
                "sulco_original_mm": 16.5,
                "status": "RECAPAR",
                "km_rodado_total": 67000.0,
                "historico_recapagens": [],
                "created_at": agora_iso,
                "updated_at": agora_iso
            }
        ]
        db.pneus.insert_many(pneus_demo)

    # 9. Abastecimentos com caso real de detecção de anomalia antifraude
    if db.abastecimentos.count_documents({}) == 0:
        abast_demo = [
            {
                "id": str(uuid.uuid4()),
                "veiculo_placa": "BRA2E19",
                "motorista_identificador": "Sebastião da Silva",
                "data_hora": (hoje - timedelta(days=3)).strftime("%Y-%m-%dT10:30:00Z"),
                "posto_combustivel": "Posto Ipiranga RodoSul - BR-101 Km 140",
                "tipo_combustivel": "DIESEL",
                "litros": 480.0,
                "valor_litro": 6.19,
                "valor_total": 2971.20,
                "odometro_km": 141200.0,
                "cartao_combustivel": "TICKET_LOG",
                "numero_comprovante": "TKT-884192",
                "consumo_calculado_kml": 2.85,
                "anomalia_detectada": False,
                "motivo_anomalia": None,
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "veiculo_placa": "BCX9D45",
                "motorista_identificador": "Luciana Barbosa",
                "data_hora": (hoje - timedelta(days=2)).strftime("%Y-%m-%dT14:15:00Z"),
                "posto_combustivel": "Auto Posto Shell Curitiba Centro",
                "tipo_combustivel": "DIESEL",
                "litros": 65.0,
                "valor_litro": 6.25,
                "valor_total": 406.25,
                "odometro_km": 49200.0,
                "cartao_combustivel": "ALELO",
                "numero_comprovante": "ALE-331049",
                "consumo_calculado_kml": 9.8,
                "anomalia_detectada": False,
                "motivo_anomalia": None,
                "created_at": agora_iso
            },
            {
                # Caso de ANOMALIA / FRAUDE DETECTADA: Tanque de Hilux é 80L, faturado 115L!
                "id": str(uuid.uuid4()),
                "veiculo_placa": "RLF5C88",
                "motorista_identificador": "Fernando Henrique Ramos",
                "data_hora": (hoje - timedelta(days=1)).strftime("%Y-%m-%dT19:40:00Z"),
                "posto_combustivel": "Posto Trevo Conveniências",
                "tipo_combustivel": "DIESEL",
                "litros": 115.0,
                "valor_litro": 6.30,
                "valor_total": 724.50,
                "odometro_km": 38400.0,
                "cartao_combustivel": "VR_AUTO",
                "numero_comprovante": "VRA-901412",
                "consumo_calculado_kml": 4.1,
                "anomalia_detectada": True,
                "motivo_anomalia": "VOLUME ANÔMALO: Abastecido 115.0 L em tanque com capacidade máxima de 80.0 L (Excedente de 35.0 L). Suspeita de abastecimento em galão ou veículo terceiro.",
                "created_at": agora_iso
            }
        ]
        db.abastecimentos.insert_many(abast_demo)

    # 10. Ordens de Serviço (OS)
    if db.ordens_servico.count_documents({}) == 0:
        os_demo = [
            {
                "id": str(uuid.uuid4()),
                "numero_os": "OS-202610-00129",
                "veiculo_placa": "QNY7J12",
                "tipo": "CORRETIVA",
                "data_abertura": (hoje - timedelta(days=2)).strftime("%Y-%m-%d"),
                "data_previsao": (hoje + timedelta(days=2)).strftime("%Y-%m-%d"),
                "data_conclusao": None,
                "oficina_credenciada": "Diesel Tech Serviços Especializados",
                "itens_pecas": [
                    {"codigo": "EMB-902", "descricao": "Kit Embreagem Luk Iveco Daily", "quantidade": 1.0, "valor_unitario": 1450.0, "subtotal": 1450.0},
                    {"codigo": "LUB-75W", "descricao": "Óleo de Câmbio Sintético 75W80", "quantidade": 3.0, "valor_unitario": 75.0, "subtotal": 225.0}
                ],
                "servicos": [
                    {"descricao": "Substituição kit embreagem e regulagem de atuador", "horas": 5.0, "valor_hora": 120.0, "subtotal": 600.0}
                ],
                "valor_total": 2275.0,
                "odometro_momento_km": 68900.0,
                "observacoes": "Veículo com patinação excessiva em subidas íngremes.",
                "status": "EM_ANDAMENTO",
                "created_at": agora_iso,
                "updated_at": agora_iso
            }
        ]
        db.ordens_servico.insert_many(os_demo)

    # 11. Multas com indicação de condutor
    if db.multas.count_documents({}) == 0:
        multas_demo = [
            {
                "id": str(uuid.uuid4()),
                "auto_infracao": "AIT-PR-2026-90412",
                "veiculo_placa": "BRA2E19",
                "motorista_identificador": "Sebastião da Silva",
                "data_hora_infracao": (hoje - timedelta(days=12)).strftime("%Y-%m-%d 14:22:00"),
                "local": "BR-277 Km 68 - Sentido Litoral (PR)",
                "codigo_infracao": "745-50",
                "descricao_infracao": "Transitar em velocidade superior à máxima permitida em até 20%",
                "pontos": 4,
                "valor_multa": 130.16,
                "vencimento_pagamento": (hoje + timedelta(days=25)).strftime("%Y-%m-%d"),
                "limite_indicacao_condutor": (hoje + timedelta(days=8)).strftime("%Y-%m-%d"),
                "status_indicacao": "PENDENTE",
                "status_pagamento": "A_VENCER",
                "protocolo_detran": None,
                "created_at": agora_iso,
                "updated_at": agora_iso
            }
        ]
        db.multas.insert_many(multas_demo)

    # 12. Documentos a vencer
    if db.documentos_vencimento.count_documents({}) == 0:
        docs_demo = [
            {
                "id": str(uuid.uuid4()),
                "veiculo_placa": "BRA2E19",
                "tipo_documento": "IPVA",
                "ano_exercicio": 2026,
                "data_vencimento": (hoje + timedelta(days=18)).strftime("%Y-%m-%d"),
                "valor": 3450.00,
                "status_pagamento": "A_VENCER",
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "veiculo_placa": "RHO4A21",
                "tipo_documento": "LICENCIAMENTO",
                "ano_exercicio": 2026,
                "data_vencimento": (hoje + timedelta(days=24)).strftime("%Y-%m-%d"),
                "valor": 192.40,
                "status_pagamento": "A_VENCER",
                "created_at": agora_iso
            }
        ]
        db.documentos_vencimento.insert_many(docs_demo)

    # 13. Pedágios
    if db.pedagios.count_documents({}) == 0:
        pedagios_demo = [
            {
                "id": str(uuid.uuid4()),
                "veiculo_placa": "BRA2E19",
                "data_hora": (hoje - timedelta(days=1)).strftime("%Y-%m-%dT11:45:00Z"),
                "concessionaria_praca": "EPR Litoral Pioneiro - Praça São José dos Pinhais",
                "valor": 44.80,
                "operadora_tag": "SEM_PARAR",
                "status_cobranca": "DEBITADO",
                "created_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "veiculo_placa": "RHO4A21",
                "data_hora": (hoje - timedelta(days=1)).strftime("%Y-%m-%dT15:20:00Z"),
                "concessionaria_praca": "Via Araucária - Praça Araucária BR-476",
                "valor": 52.40,
                "operadora_tag": "VELOE",
                "status_cobranca": "DEBITADO",
                "created_at": agora_iso
            }
        ]
        db.pedagios.insert_many(pedagios_demo)

    # 14. SEED CONTRATO DO GOVERNO DO ESTADO DE SANTA CATARINA (SEA/SC)
    # Veículos, Embarcações, Geradores, Máquinas, Cartões Magnéticos/Chip e Postos SC
    seed_contract_sc_data(db, agora_iso, hoje)

    return True


def seed_contract_sc_data(db, agora_iso: str, hoje: datetime):
    """Semeia ativos de Santa Catarina, rede de postos em SC e cartões com chip/tarja."""
    # A. Ativos específicos de Santa Catarina (se ainda não existirem)
    sc_ativos = [
        {
            "id": "sc-ativo-pmsc-9021",
            "placa": "RLS4D90",
            "chassi": "8AJZZZ331WP909021",
            "renavam": "01234567897",
            "marca": "Ford",
            "modelo": "Ranger XLS 4x4 Viatura Polícia Militar SC",
            "ano_fabricacao": 2024,
            "ano_modelo": 2024,
            "categoria": VeiculoCategoria.UTILITARIO.value,
            "capacidade_carga_kg": 1050.0,
            "capacidade_tanque_litros": 80.0,
            "tipo_combustivel": TipoCombustivel.DIESEL_S10.value,
            "odometro_atual_km": 14200.0,
            "horimetro_atual_h": 480.0,
            "status": VeiculoStatus.DISPONIVEL.value,
            "centro_custo": "PMSC_BATALHAO_FLORIANOPOLIS",
            "secretaria": "SECRETARIA_SEGURANCA",
            "created_at": agora_iso,
            "updated_at": agora_iso
        },
        {
            "id": "sc-ativo-samu-192",
            "placa": "RDU8C19",
            "chassi": "8A1ZZZ511VP119219",
            "renavam": "01234567898",
            "marca": "Mercedes-Benz",
            "modelo": "Sprinter 416 CDI Ambulância UTI Móvel SAMU/SC",
            "ano_fabricacao": 2023,
            "ano_modelo": 2024,
            "categoria": VeiculoCategoria.UTILITARIO.value,
            "capacidade_carga_kg": 1800.0,
            "capacidade_tanque_litros": 75.0,
            "tipo_combustivel": TipoCombustivel.DIESEL_S10.value,
            "odometro_atual_km": 42100.0,
            "horimetro_atual_h": 1210.0,
            "status": VeiculoStatus.DISPONIVEL.value,
            "centro_custo": "SES_SAMU_ESTADUAL",
            "secretaria": "SECRETARIA_SAUDE",
            "created_at": agora_iso,
            "updated_at": agora_iso
        },
        {
            "id": "sc-ativo-emb-marlim",
            "placa": "EMB-SC-MARLIM",
            "chassi": "BR-MARLIM-280-PMSC01",
            "renavam": "00000000001",
            "marca": "Marlim Marine",
            "modelo": "Lancha de Fiscalização Ambiental Marlim 280 (PMSC Ambiental/IMA)",
            "ano_fabricacao": 2023,
            "ano_modelo": 2023,
            "categoria": VeiculoCategoria.EMBARCACAO.value,
            "capacidade_carga_kg": 2500.0,
            "capacidade_tanque_litros": 280.0,
            "tipo_combustivel": TipoCombustivel.DIESEL_MARITIMO.value,
            "odometro_atual_km": 0.0,
            "horimetro_atual_h": 420.5,
            "status": VeiculoStatus.DISPONIVEL.value,
            "centro_custo": "POLICIA_AMBIENTAL_FLORIANOPOLIS",
            "secretaria": "SECRETARIA_SEGURANCA",
            "created_at": agora_iso,
            "updated_at": agora_iso
        },
        {
            "id": "sc-ativo-ger-hospital",
            "placa": "GER-SC-HOSP-01",
            "chassi": "CUMMINS-QSB7-250KVA-SES",
            "renavam": "00000000002",
            "marca": "Cummins Power",
            "modelo": "Gerador Estacionário Diesel 250 kVA - Hospital Regional de São José",
            "ano_fabricacao": 2022,
            "ano_modelo": 2022,
            "categoria": VeiculoCategoria.GERADOR.value,
            "capacidade_carga_kg": 3200.0,
            "capacidade_tanque_litros": 350.0,
            "tipo_combustivel": TipoCombustivel.DIESEL_S10.value,
            "odometro_atual_km": 0.0,
            "horimetro_atual_h": 310.0,
            "status": VeiculoStatus.DISPONIVEL.value,
            "centro_custo": "HOSPITAL_REGIONAL_SAO_JOSE",
            "secretaria": "SECRETARIA_SAUDE",
            "created_at": agora_iso,
            "updated_at": agora_iso
        },
        {
            "id": "sc-ativo-maq-sie-140k",
            "placa": "MAQ-SC-CAT-140K",
            "chassi": "CAT140K-SIE-SC-00441",
            "renavam": "00000000003",
            "marca": "Caterpillar",
            "modelo": "Motoniveladora 140K Obras Rodoviárias (SIE/SC)",
            "ano_fabricacao": 2023,
            "ano_modelo": 2023,
            "categoria": VeiculoCategoria.MAQUINA_EQUIPAMENTO.value,
            "capacidade_carga_kg": 17500.0,
            "capacidade_tanque_litros": 390.0,
            "tipo_combustivel": TipoCombustivel.DIESEL_S10.value,
            "odometro_atual_km": 0.0,
            "horimetro_atual_h": 1840.0,
            "status": VeiculoStatus.DISPONIVEL.value,
            "centro_custo": "SIE_INFRAESTRUTURA_RODOVIAS",
            "secretaria": "SECRETARIA_OBRAS",
            "created_at": agora_iso,
            "updated_at": agora_iso
        }
    ]

    for at in sc_ativos:
        if db.veiculos.count_documents({"placa": at["placa"]}) == 0:
            db.veiculos.insert_one(at)

    # B. Postos Credenciados em Santa Catarina
    postos_sc = [
        {
            "id": "posto-sc-floripa-ilha-sul",
            "cnpj": "83.123.456/0001-12",
            "nome_fantasia": "Posto Petrobras Ilha Sul - Florianópolis",
            "razao_social": "Auto Posto Beira Mar Sul Ltda",
            "bandeira": "Petrobras",
            "cidade": "Florianópolis",
            "uf": "SC",
            "endereco": "Rod. Gov. Aderbal Ramos da Silva, 2400 - Costeira do Pirajubaé",
            "latitude": -27.6189,
            "longitude": -48.5321,
            "status": "CREDENCIADO",
            "contato": "(48) 3226-9000 / sc.ilhasul@petrobras.com.br",
            "created_at": agora_iso
        },
        {
            "id": "posto-sc-floripa-continental",
            "cnpj": "83.987.654/0001-34",
            "nome_fantasia": "Posto Shell Estreito Continental",
            "razao_social": "Posto Continental de Combustíveis S/A",
            "bandeira": "Shell",
            "cidade": "Florianópolis",
            "uf": "SC",
            "endereco": "Av. Marinheiro Max Schramm, 3100 - Estreito",
            "latitude": -27.5850,
            "longitude": -48.5872,
            "status": "CREDENCIADO",
            "contato": "(48) 3244-1100",
            "created_at": agora_iso
        },
        {
            "id": "posto-sc-joinville-rodonorte",
            "cnpj": "84.555.666/0001-88",
            "nome_fantasia": "Auto Posto Ipiranga RodoNorte Joinville",
            "razao_social": "Comércio RodoNorte Derivados Ltda",
            "bandeira": "Ipiranga",
            "cidade": "Joinville",
            "uf": "SC",
            "endereco": "BR-101 Km 42 - Zona Industrial Norte",
            "latitude": -26.2415,
            "longitude": -48.8710,
            "status": "CREDENCIADO",
            "contato": "(47) 3433-8080",
            "created_at": agora_iso
        },
        {
            "id": "posto-sc-blumenau-vale",
            "cnpj": "85.222.333/0001-44",
            "nome_fantasia": "Posto Vale do Itajaí Petrobras",
            "razao_social": "PetroVale Abastecimento de Frotas Ltda",
            "bandeira": "Petrobras",
            "cidade": "Blumenau",
            "uf": "SC",
            "endereco": "Via Expressa Paul Fritz Kuehnrich, 1400 - Fortaleza",
            "latitude": -26.8920,
            "longitude": -49.0712,
            "status": "CREDENCIADO",
            "contato": "(47) 3323-5000",
            "created_at": agora_iso
        },
        {
            "id": "posto-sc-chapeco-oeste",
            "cnpj": "86.777.888/0001-99",
            "nome_fantasia": "Posto RodoRede Oeste Chapecó",
            "razao_social": "RodoRede Sul de Combustíveis Ltda",
            "bandeira": "Ipiranga",
            "cidade": "Chapecó",
            "uf": "SC",
            "endereco": "Acesso Plínio Arlindo de Nês, 2100 - Trevo BR-282",
            "latitude": -27.0980,
            "longitude": -52.6310,
            "status": "CREDENCIADO",
            "contato": "(49) 3328-7070",
            "created_at": agora_iso
        },
        {
            "id": "posto-sc-itajai-porto",
            "cnpj": "87.333.444/0001-55",
            "nome_fantasia": "Posto Marítimo e Rodoviário Porto de Itajaí",
            "razao_social": "Abastecimento Portuário e Fluvial Itajaí Ltda",
            "bandeira": "Petrobras",
            "cidade": "Itajaí",
            "uf": "SC",
            "endereco": "Av. Cel. Eugênio Müller, 800 - Bairro Centro / Porto",
            "latitude": -26.9080,
            "longitude": -48.6590,
            "status": "CREDENCIADO",
            "contato": "(47) 3348-1234",
            "created_at": agora_iso
        }
    ]

    for p in postos_sc:
        if db.postos_credenciados.count_documents({"cnpj": p["cnpj"]}) == 0:
            db.postos_credenciados.insert_one(p)

    # C. Cartões Magnéticos e Microprocessados com Chip
    if not hasattr(db, "cartoes_frota") or db.cartoes_frota.count_documents({}) == 0:
        cartoes_demo = [
            {
                "id": str(uuid.uuid4()),
                "numero_mascarado": "6035.7701.8824.9021",
                "tecnologia": "CHIP_MICROPROCESSADO",
                "tipo_cartao": "CARTAO_VEICULO",
                "identificador_ativo": "RLS4D90",
                "secretaria": "SECRETARIA_SEGURANCA",
                "orgao_vinculado": "Governo do Estado de Santa Catarina - PMSC",
                "limite_mensal_reais": 5000.0,
                "saldo_disponivel_reais": 3850.0,
                "total_gasto_mes_atual": 1150.0,
                "combustiveis_autorizados": ["DIESEL_S10", "LUBRIFICANTE", "ADITIVO_ARLA32"],
                "exige_odometro_horimetro": True,
                "permite_final_de_semana": True,
                "validade": "2028-12",
                "status": "ATIVO",
                "ultima_transacao_em": agora_iso,
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "numero_mascarado": "6035.7701.8824.0192",
                "tecnologia": "CHIP_MICROPROCESSADO",
                "tipo_cartao": "CARTAO_VEICULO",
                "identificador_ativo": "RDU8C19",
                "secretaria": "SECRETARIA_SAUDE",
                "orgao_vinculado": "Governo do Estado de Santa Catarina - SAMU/SES",
                "limite_mensal_reais": 7000.0,
                "saldo_disponivel_reais": 5200.0,
                "total_gasto_mes_atual": 1800.0,
                "combustiveis_autorizados": ["DIESEL_S10", "LUBRIFICANTE", "ADITIVO_ARLA32"],
                "exige_odometro_horimetro": True,
                "permite_final_de_semana": True,
                "validade": "2028-12",
                "status": "ATIVO",
                "ultima_transacao_em": agora_iso,
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "numero_mascarado": "6035.7701.8824.0088",
                "tecnologia": "CHIP_MICROPROCESSADO",
                "tipo_cartao": "CARTAO_EMBARCACAO",
                "identificador_ativo": "EMB-SC-MARLIM",
                "secretaria": "SECRETARIA_SEGURANCA",
                "orgao_vinculado": "Governo do Estado de Santa Catarina - PMSC Ambiental",
                "limite_mensal_reais": 12000.0,
                "saldo_disponivel_reais": 9400.0,
                "total_gasto_mes_atual": 2600.0,
                "combustiveis_autorizados": ["DIESEL_MARITIMO", "LUBRIFICANTE", "OLEO_2T_4T"],
                "exige_odometro_horimetro": True,
                "permite_final_de_semana": True,
                "validade": "2028-12",
                "status": "ATIVO",
                "ultima_transacao_em": agora_iso,
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "numero_mascarado": "6035.7701.8824.0350",
                "tecnologia": "TARJA_MAGNETICA",
                "tipo_cartao": "CARTAO_GERADOR",
                "identificador_ativo": "GER-SC-HOSP-01",
                "secretaria": "SECRETARIA_SAUDE",
                "orgao_vinculado": "Governo do Estado de Santa Catarina - Hospital Regional São José",
                "limite_mensal_reais": 8000.0,
                "saldo_disponivel_reais": 6800.0,
                "total_gasto_mes_atual": 1200.0,
                "combustiveis_autorizados": ["DIESEL_S10", "LUBRIFICANTE"],
                "exige_odometro_horimetro": True,
                "permite_final_de_semana": True,
                "validade": "2028-12",
                "status": "ATIVO",
                "ultima_transacao_em": agora_iso,
                "created_at": agora_iso,
                "updated_at": agora_iso
            },
            {
                "id": str(uuid.uuid4()),
                "numero_mascarado": "6035.7701.8824.0140",
                "tecnologia": "CHIP_MICROPROCESSADO",
                "tipo_cartao": "CARTAO_MAQUINA",
                "identificador_ativo": "MAQ-SC-CAT-140K",
                "secretaria": "SECRETARIA_OBRAS",
                "orgao_vinculado": "Governo do Estado de Santa Catarina - SIE Rodovias",
                "limite_mensal_reais": 15000.0,
                "saldo_disponivel_reais": 11200.0,
                "total_gasto_mes_atual": 3800.0,
                "combustiveis_autorizados": ["DIESEL_S10", "ADITIVO_ARLA32", "LUBRIFICANTE", "FLUIDO_HIDRAULICO"],
                "exige_odometro_horimetro": True,
                "permite_final_de_semana": False,
                "validade": "2028-12",
                "status": "ATIVO",
                "ultima_transacao_em": agora_iso,
                "created_at": agora_iso,
                "updated_at": agora_iso
            }
        ]
        db.cartoes_frota.insert_many(cartoes_demo)

    # D. Transações realizadas em SC com cartões
    if not hasattr(db, "transacoes_cartao_sc") or db.transacoes_cartao_sc.count_documents({}) == 0:
        transacoes_demo = [
            {
                "id": str(uuid.uuid4()),
                "cartao_id": "sc-card-pmsc",
                "posto_credenciado_id": "posto-sc-floripa-ilha-sul",
                "posto_nome": "Posto Petrobras Ilha Sul - Florianópolis",
                "cidade": "Florianópolis",
                "uf": "SC",
                "tipo_ativo": "UTILITARIO",
                "identificador_ativo": "RLS4D90",
                "motorista_ou_operador": "Sgt. Marcos Vinícius (PMSC)",
                "tipo_insumo": "DIESEL_S10",
                "quantidade_litros_ou_unidades": 68.0,
                "valor_unitario": 5.89,
                "valor_total": 400.52,
                "odometro_ou_horimetro": 14200.0,
                "comprovante_fiscal": "NFC-e SC 42261183123456000112650010000451231",
                "autorizado": True,
                "codigo_autorizacao": f"AUT-SEA-SC-{datetime.now().strftime('%Y%m%d')}-A9812B",
                "mensagem_status": "Transação Autorizada com Sucesso via Cartão Integrado Governo de SC.",
                "anomalia_detectada": False,
                "motivo_anomalia": None,
                "timestamp": (hoje - timedelta(hours=3)).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "cartao_id": "sc-card-marlim",
                "posto_credenciado_id": "posto-sc-itajai-porto",
                "posto_nome": "Posto Marítimo e Rodoviário Porto de Itajaí",
                "cidade": "Itajaí",
                "uf": "SC",
                "tipo_ativo": "EMBARCACAO",
                "identificador_ativo": "EMB-SC-MARLIM",
                "motorista_ou_operador": "Capitão Marcelo Santos (PMSC Ambiental)",
                "tipo_insumo": "DIESEL_MARITIMO",
                "quantidade_litros_ou_unidades": 220.0,
                "valor_unitario": 5.45,
                "valor_total": 1199.00,
                "odometro_ou_horimetro": 420.5,
                "comprovante_fiscal": "NFC-e SC 42261187333444000155650010000889123",
                "autorizado": True,
                "codigo_autorizacao": f"AUT-SEA-SC-{datetime.now().strftime('%Y%m%d')}-C3411E",
                "mensagem_status": "Transação Autorizada com Sucesso via Cartão Integrado Governo de SC.",
                "anomalia_detectada": False,
                "motivo_anomalia": None,
                "timestamp": (hoje - timedelta(hours=6)).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "cartao_id": "sc-card-cat140k",
                "posto_credenciado_id": "posto-sc-joinville-rodonorte",
                "posto_nome": "Auto Posto Ipiranga RodoNorte Joinville",
                "cidade": "Joinville",
                "uf": "SC",
                "tipo_ativo": "MAQUINA_EQUIPAMENTO",
                "identificador_ativo": "MAQ-SC-CAT-140K",
                "motorista_ou_operador": "Valdir Fagundes (Operador SIE/SC)",
                "tipo_insumo": "ADITIVO_ARLA32",
                "quantidade_litros_ou_unidades": 40.0,
                "valor_unitario": 4.20,
                "valor_total": 168.00,
                "odometro_ou_horimetro": 1840.0,
                "comprovante_fiscal": "NFC-e SC 42261184555666000188650010000331902",
                "autorizado": True,
                "codigo_autorizacao": f"AUT-SEA-SC-{datetime.now().strftime('%Y%m%d')}-F7123A",
                "mensagem_status": "Transação Autorizada com Sucesso via Cartão Integrado Governo de SC.",
                "anomalia_detectada": False,
                "motivo_anomalia": None,
                "timestamp": (hoje - timedelta(days=1)).isoformat()
            }
        ]
        db.transacoes_cartao_sc.insert_many(transacoes_demo)


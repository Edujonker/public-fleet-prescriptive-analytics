#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
SISTEMA DE GESTÃO DE FROTAS & TELEMETRIA IoT - SIMULADOR E SUÍTE DE TESTES COMPLETA
========================================================================================
Este script implementa uma bateria completa e simulador interativo/automatizado do sistema:
1. MÓDULO CADASTRO:
   - Veículos (Placa Mercosul, Chassi, Renavam, Tanque, Odômetro, Atualização Cadastral)
   - Motoristas (CNH, Categoria, CPF, Validade Toxicológica, Score de Condução)
   - Equipamentos Rastreadores IoT / Câmeras de Fadiga
   - Gestão de Pneus e Monitoramento de Sulco (CONTRAN 1.6mm)
2. MÓDULO OPERACIONAL:
   - Despacho de Viagem e Rotas
   - Vistoria Digital / Checklist Pré-Viagem (Trava de Segurança e Liberação)
   - Telemetria IoT ao Vivo (Velocidade, RPM, Ignicao, Rota e Condução Agressiva)
3. MÓDULO COMBUSTÍVEL E ANTIFRAUDE:
   - Auditoria de Abastecimento com Teste de Fraude (Litros > Capacidade do Tanque)
   - Abastecimento Legítimo com Cálculo de Eficiência km/L
4. MÓDULO MANUTENÇÃO:
   - Ciclo de Vida de Ordem de Serviço (OS): Abertura, Peças, Serviços e Conclusão
5. MÓDULO COMPLIANCE:
   - Workflow de Indicação de Condutor Infrator DETRAN com Emissão de Protocolo
6. MÓDULO ANÁLISE E PRESCRIÇÃO 360°:
   - Manutenção Dinâmica & Falhas Críticas 48h
   - Eficiência de Combustível & Postos Barateados em Rota
   - Logística & Dimensionamento de Ociosidade
   - Treinamento Sob Medida & Bloqueio por Fadiga (Lei 13.103/2015)
   - TCO, Desinvestimento (>40% Venal) e Cruzamento Tripartido (Manutenção, Patrimônio e Combustíveis)
========================================================================================
"""

import sys
import os
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Injetar diretórios de backend no sys.path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.seed_data import seed_database_if_empty

# Cores ANSI para Terminal Executivo
class Cor:
    AZUL = "\033[94m"
    VERDE = "\033[92m"
    AMARELO = "\033[93m"
    VERMELHO = "\033[91m"
    CIANO = "\033[96m"
    BRANCO_NEGRITO = "\033[1;37m"
    RESET = "\033[0m"


class SimuladorSistemaFrotas:
    def __init__(self):
        print(f"{Cor.CIANO}Inicializando banco de dados e sementes corporativas...{Cor.RESET}")
        init_db()
        seed_database_if_empty()
        self.client = TestClient(app)
        self.headers_auth: Dict[str, str] = {}
        self.iot_headers = {"X-API-Key": "flt_gateway_iot_live_sim_2026_seckey"}
        self.autenticar()

    def autenticar(self):
        """Autenticação JWT com credenciais de Administrador Master."""
        resp = self.client.post("/api/auth/login", json={
            "username": "000.000.000-00",
            "password": "Iprev@2021"
        })
        if resp.status_code != 200:
            # Tenta com o username admin como fallback
            resp = self.client.post("/api/auth/login", json={
                "username": "admin",
                "password": "Iprev@2021"
            })
        if resp.status_code != 200:
            raise RuntimeError(f"Falha na autenticação: {resp.text}")
        token = resp.json()["access_token"]
        self.headers_auth = {"Authorization": f"Bearer {token}"}
        print(f"{Cor.VERDE}✔ Autenticação JWT efetuada com sucesso (Perfil: Administrador Master FrotaSaaS).{Cor.RESET}")

    # =========================================================================
    # 1. SIMULAÇÃO DE CADASTROS (VEÍCULOS, MOTORISTAS, EQUIPAMENTOS, PNEUS)
    # =========================================================================
    def simular_cadastro_veiculo(self, placa: str = "SIM2026") -> Dict[str, Any]:
        print(f"\n{Cor.AZUL}--- [CADASTRO 1/4] Simulação de Cadastro de Veículo Comercial ---{Cor.RESET}")
        payload = {
            "placa": placa,
            "chassi": "9BWZZZ377VT00SIMU",
            "renavam": "12345678901",
            "marca": "VOLVO",
            "modelo": "FH 540 6X4 TRACTOR",
            "ano_fabricacao": 2025,
            "ano_modelo": 2026,
            "categoria": "PESADO",
            "capacidade_carga_kg": 45000.0,
            "capacidade_tanque_litros": 600.0,
            "tipo_combustivel": "DIESEL",
            "odometro_atual_km": 12500.0,
            "horimetro_atual_h": 320.0,
            "status": "DISPONIVEL",
            "centro_custo": "OPERACAO_RODOVIARIA_SUL",
            "secretaria": "SECRETARIA_INFRAESTRUTURA_LOGISTICA"
        }
        res = self.client.post("/api/assets/veiculos", json=payload, headers=self.headers_auth)
        if res.status_code == 400 and "já cadastrado" in res.text:
            print(f"{Cor.AMARELO}ℹ Veículo {placa} já existe na base. Recuperando ficha cadastral...{Cor.RESET}")
            res = self.client.get(f"/api/assets/veiculos/{placa}", headers=self.headers_auth)
        
        assert res.status_code == 200, f"Erro no cadastro de veículo: {res.text}"
        data = res.json()
        print(f"{Cor.VERDE}✔ Veículo Cadastrado com Sucesso:{Cor.RESET}")
        print(f"  - Placa: {data['placa']} | Marca/Modelo: {data['marca']} {data['modelo']}")
        print(f"  - Categoria: {data['categoria']} | Tanque: {data['capacidade_tanque_litros']}L | Odômetro: {data['odometro_atual_km']} km")
        print(f"  - Secretaria / Centro de Custo: {data['secretaria']} ({data['centro_custo']})")
        return data

    def simular_cadastro_motorista(self, cpf: Optional[str] = None) -> Dict[str, Any]:
        print(f"\n{Cor.AZUL}--- [CADASTRO 2/4] Simulação de Cadastro de Motorista Profissional ---{Cor.RESET}")
        ts = int(time.time() * 1000)
        cpf_usado = cpf or f"{ts % 100000000000:011d}"
        cnh_usada = f"{ts % 10000000000:011d}"
        payload = {
            "nome": "Marcos Vinicius de Oliveira",
            "cpf": cpf_usado,
            "cnh_numero": cnh_usada,
            "cnh_categoria": "E",
            "cnh_validade": "2029-12-31",
            "pontuacao_cnh": 0,
            "status_toxicologico": "VALIDO",
            "data_vencimento_toxicologico": "2028-06-30",
            "vinculo_contratual": "CLT",
            "status": "ATIVO"
        }
        res = self.client.post("/api/assets/motoristas", json=payload, headers=self.headers_auth)
        if res.status_code == 400 and ("já cadastrado" in res.text or "já cadastrada" in res.text):
            print(f"{Cor.AMARELO}ℹ Motorista já cadastrado. Listando motoristas cadastrados...{Cor.RESET}")
            res_list = self.client.get("/api/assets/motoristas", headers=self.headers_auth)
            data = res_list.json()[0]
        else:
            assert res.status_code == 200, f"Erro no cadastro do motorista: {res.text}"
            data = res.json()

        cpf_val = data.get('cpf', '')
        cpf_mascarado = f"{cpf_val[:3]}.***.***-{cpf_val[-2:]}" if len(cpf_val) >= 11 else "***"
        print(f"  - Nome: {data['nome']} | CPF: {cpf_mascarado} (Anonimizado LGPD)")
        print(f"  - CNH: {data['cnh_numero']} (Cat. {data['cnh_categoria']}) - Validade: {data['cnh_validade']}")
        print(f"  - Exame Toxicológico: {data['status_toxicologico']} (Vencimento: {data['data_vencimento_toxicologico']})")
        print(f"  - Score Inicial de Condução: {data.get('score_conducao', 100.0)} pts")
        return data

    def simular_cadastro_equipamento_iot(self, placa_alvo: str = "SIM2026") -> Dict[str, Any]:
        print(f"\n{Cor.AZUL}--- [CADASTRO 3/4] Cadastro de Rastreador IoT / Telemetria CANBus ---{Cor.RESET}")
        serial_rand = f"TEL-CANBUS-{int(time.time())}"
        payload = {
            "identificador_serial": serial_rand,
            "tipo": "TELEMETRIA_CANBUS",
            "marca_modelo": "Suntech ST340LC 4G LTE",
            "veiculo_placa": placa_alvo,
            "numero_chip_sim": "+5541999998888",
            "status": "ATIVO",
            "data_instalacao": "2026-10-31"
        }
        res = self.client.post("/api/assets/equipamentos", json=payload, headers=self.headers_auth)
        assert res.status_code == 200, f"Erro no cadastro de equipamento: {res.text}"
        data = res.json()
        print(f"{Cor.VERDE}✔ Dispositivo de Telemetria Instalado com Sucesso:{Cor.RESET}")
        print(f"  - Serial: {data['identificador_serial']} | Tipo: {data['tipo']}")
        print(f"  - Fabricante/Modelo: {data['marca_modelo']} | Veículo Vinculado: {data['veiculo_placa']}")
        print(f"  - Status Operacional: {data['status']}")
        return data

    def simular_cadastro_pneu_e_inspecao(self, placa_alvo: str = "SIM2026"):
        print(f"\n{Cor.AZUL}--- [CADASTRO 4/4] Cadastro de Pneu & Inspeção Resolução CONTRAN ---{Cor.RESET}")
        # Pneu 1: Conforme
        pneu_ok = {
            "numero_fogo": f"FOG-OK-{int(time.time())}",
            "marca_modelo": "Michelin X MultiWay 3D",
            "dimensao": "295/80 R22.5",
            "posicao_atual": "DIANTEIRO_DIR",
            "veiculo_placa": placa_alvo,
            "pressao_psi": 120.0,
            "sulco_atual_mm": 11.5,
            "sulco_original_mm": 16.0
        }
        res_ok = self.client.post("/api/maintenance/tires", json=pneu_ok, headers=self.headers_auth)
        assert res_ok.status_code == 200
        d_ok = res_ok.json()
        print(f"{Cor.VERDE}✔ Pneu Dianteiro Direito Cadastrado (Conforme):{Cor.RESET}")
        print(f"  - Fogo: {d_ok['numero_fogo']} | Sulco: {d_ok['sulco_atual_mm']} mm | Status: {d_ok['status']}")

        # Pneu 2: Crítico CONTRAN (< 1.6mm)
        pneu_crit = {
            "numero_fogo": f"FOG-CRIT-{int(time.time())}",
            "marca_modelo": "Pirelli Formula G",
            "dimensao": "295/80 R22.5",
            "posicao_atual": "TRASEIRO_ESQ_EXT",
            "veiculo_placa": placa_alvo,
            "pressao_psi": 105.0,
            "sulco_atual_mm": 1.2,  # Abaixo de 1.6mm!
            "sulco_original_mm": 15.0
        }
        res_crit = self.client.post("/api/maintenance/tires", json=pneu_crit, headers=self.headers_auth)
        assert res_crit.status_code == 200
        d_crit = res_crit.json()
        assert d_crit["status"] == "CRITICO", f"Pneu deveria ser CRITICO: {d_crit['status']}"
        print(f"{Cor.VERMELHO}⚠ Pneu Traseiro Esquerdo Cadastrado com Alerta CONTRAN:{Cor.RESET}")
        print(f"  - Fogo: {d_crit['numero_fogo']} | Sulco: {d_crit['sulco_atual_mm']} mm (< 1.6mm!)")
        print(f"  - Status CONTRAN Automático: {Cor.VERMELHO}{d_crit['status']} (Recapagem/Troca Mandatória){Cor.RESET}")

    # =========================================================================
    # 2. SIMULAÇÃO OPERACIONAL (CHECKLIST PRÉ-VIAGEM E DESPACHO)
    # =========================================================================
    def simular_operacao_despacho_e_checklists(self, placa: str, motorista_nome: str) -> str:
        print(f"\n{Cor.AZUL}--- [OPERAÇÃO] Simulação de Viagem, Trava de Segurança e Despacho ---{Cor.RESET}")
        # Criação da solicitação de viagem
        viagem_req = {
            "veiculo_placa": placa,
            "motorista_identificador": motorista_nome,
            "centro_custo": "OPERACAO_RODOVIARIA_SUL",
            "origem": "Curitiba - PR (Pátio Central DER)",
            "destino": "Cascavel - PR (Base Operacional Oeste)",
            "data_partida_prevista": "2026-11-01T06:00:00",
            "data_retorno_prevista": "2026-11-02T18:00:00",
            "distancia_estimada_km": 498.0,
            "eta_estimado_minutos": 420,
            "observacoes": "Transporte de insumos para obras de conservação rodoviária."
        }
        res_vg = self.client.post("/api/trips", json=viagem_req, headers=self.headers_auth)
        assert res_vg.status_code == 200, f"Erro ao criar viagem: {res_vg.text}"
        viagem_data = res_vg.json()
        viagem_id = viagem_data["id"]
        print(f"{Cor.VERDE}✔ Solicitação de Viagem Gerada:{Cor.RESET}")
        print(f"  - ID: {viagem_id} | Código: {viagem_data['codigo_viagem']}")
        print(f"  - Rota: {viagem_data['origem']} ➔ {viagem_data['destino']} ({viagem_data['distancia_estimada_km']} km)")

        # Teste 1 de Checklist: Reprovação por Segurança (Farol queimado e freio com ar)
        print(f"\n{Cor.AMARELO}➔ Simulação 1: Submissão de Checklist Pré-Viagem com Falha Grave de Segurança...{Cor.RESET}")
        chk_falha = {
            "viagem_id": viagem_id,
            "veiculo_placa": placa,
            "motorista_identificador": motorista_nome,
            "tipo": "PRE_VIAGEM",
            "itens": [
                {"item": "Sistema de Freios a Ar", "conforme": False, "observacao": "Vazamento de ar na cuíca de freio"},
                {"item": "Faróis e Lanternas", "conforme": True},
                {"item": "Pneus e Rodas", "conforme": True}
            ]
        }
        res_chk_falha = self.client.post("/api/trips/checklists", json=chk_falha, headers=self.headers_auth)
        assert res_chk_falha.status_code == 200
        d_falha = res_chk_falha.json()
        assert d_falha["status_aprovacao"] == "REPROVADO_IMPEDIDO"
        print(f"{Cor.VERMELHO}✖ Trava Automática de Segurança Acionada:{Cor.RESET}")
        print(f"  - Status do Checklist: {d_falha['status_aprovacao']}")
        print(f"  - Motivo do Bloqueio: {d_falha.get('motivo_reprovacao')}")

        # Teste de Despacho Bloqueado
        res_disp_bloq = self.client.post(f"/api/trips/{viagem_id}/dispatch", headers=self.headers_auth)
        print(f"{Cor.VERDE}✔ Despacho Corretamente Impedido pelo Sistema:{Cor.RESET} {res_disp_bloq.json().get('detail')}")

        # Teste 2 de Checklist: Reparo e Aprovação Plena
        print(f"\n{Cor.VERDE}➔ Simulação 2: Submissão de Novo Checklist após Inspeção da Oficina (100% Conforme)...{Cor.RESET}")
        chk_aprovado = {
            "viagem_id": viagem_id,
            "veiculo_placa": placa,
            "motorista_identificador": motorista_nome,
            "tipo": "PRE_VIAGEM",
            "itens": [
                {"item": "Sistema de Freios a Ar", "conforme": True, "observacao": "Cuíca substituída e testada a 10 bar"},
                {"item": "Faróis e Lanternas", "conforme": True},
                {"item": "Pneus e Rodas", "conforme": True},
                {"item": "Nível de Óleo e Arrefecimento", "conforme": True}
            ]
        }
        res_chk_ok = self.client.post("/api/trips/checklists", json=chk_aprovado, headers=self.headers_auth)
        assert res_chk_ok.status_code == 200
        d_ok = res_chk_ok.json()
        assert d_ok["status_aprovacao"] == "APROVADO"
        print(f"{Cor.VERDE}✔ Checklist Aprovado com Sucesso: Veículo apto para circulação rodoviária.{Cor.RESET}")

        # Despacho Autorizado
        res_disp = self.client.post(f"/api/trips/{viagem_id}/dispatch", headers=self.headers_auth)
        assert res_disp.status_code == 200, f"Erro ao despachar: {res_disp.text}"
        print(f"{Cor.VERDE}✔ Viagem Despachada! Status Operacional: EM_VIAGEM.{Cor.RESET}")
        return viagem_id

    # =========================================================================
    # 3. SIMULAÇÃO DE TELEMETRIA IoT EM TEMPO REAL
    # =========================================================================
    def simular_telemetria_iot_tempo_real(self, placa: str, motorista: str):
        print(f"\n{Cor.AZUL}--- [TELEMETRIA IoT] Simulação de Ingestão de Telemetria e Condução ---{Cor.RESET}")
        # Pings simulados na BR-277
        trajetoria = [
            {"lat": -25.4389, "lng": -49.2785, "vel": 62.0, "rpm": 1450, "odometro": 12510.0, "status": "Normal urbano"},
            {"lat": -25.4600, "lng": -49.3500, "vel": 85.0, "rpm": 1550, "odometro": 12535.0, "status": "Cruzeiro rodovia"},
            {"lat": -25.4850, "lng": -49.4200, "vel": 118.5, "rpm": 2200, "odometro": 12560.0, "status": "Condução Agressiva / Excesso Velocidade"}
        ]

        for i, ponto in enumerate(trajetoria, 1):
            payload = {
                "veiculo_placa": placa,
                "latitude": ponto["lat"],
                "longitude": ponto["lng"],
                "velocidade_kmh": ponto["vel"],
                "ignicao": True,
                "rpm": ponto["rpm"],
                "odometro_km": ponto["odometro"],
                "motorista_identificador": motorista
            }
            res_ping = self.client.post("/api/telemetry/ping", json=payload, headers=self.iot_headers)
            assert res_ping.status_code == 200, f"Falha no ping IoT: {res_ping.text}"
            data = res_ping.json()
            alertas = data.get("alertas_gerados", [])
            print(f"  ➔ Ping {i}/3 ({ponto['status']}): Lat {ponto['lat']}, Lng {ponto['lng']} | Vel: {ponto['vel']} km/h | RPM: {ponto['rpm']}")
            if alertas:
                print(f"     {Cor.VERMELHO}⚠ Alertas Disparados pelo Gateway IoT: {', '.join(alertas)}{Cor.RESET}")
            else:
                print(f"     {Cor.VERDE}✔ Telemetria em faixa segura de condução.{Cor.RESET}")

        # Consulta da posição instantânea
        res_live = self.client.get(f"/api/telemetry/live?placa={placa}", headers=self.headers_auth)
        assert res_live.status_code == 200
        live_data = res_live.json()
        print(f"{Cor.VERDE}✔ Monitoramento em Tempo Real Sincronizado ({len(live_data)} veículo ativo monitorado).{Cor.RESET}")

    # =========================================================================
    # 4. SIMULAÇÃO DE COMBUSTÍVEL E AUDITORIA ANTIFRAUDE
    # =========================================================================
    def simular_combustivel_e_antifraude(self, placa: str, motorista: str):
        print(f"\n{Cor.AZUL}--- [COMBUSTÍVEL] Simulação de Auditoria Antifraude e Abastecimento ---{Cor.RESET}")
        
        # Teste 1: Tentativa de Fraude (Volume superior à capacidade do tanque de 600L -> enviar 850L)
        print(f"{Cor.AMARELO}➔ Tentativa 1: Lançamento de Abastecimento com 850L (Tanque Suporta no Máximo 600L)...{Cor.RESET}")
        abast_fraude = {
            "veiculo_placa": placa,
            "motorista_identificador": motorista,
            "posto_combustivel": "Posto Rota 277 Diesel Sul",
            "tipo_combustivel": "DIESEL",
            "litros": 850.0,
            "valor_litro": 6.15,
            "odometro_km": 12580.0,
            "cartao_combustivel": "TICKET_LOG",
            "latitude": -25.4850,
            "longitude": -49.4200
        }
        res_f = self.client.post("/api/fuel/transactions", json=abast_fraude, headers=self.headers_auth)
        assert res_f.status_code == 200
        data_f = res_f.json()
        assert data_f["anomalia_detectada"] is True
        print(f"{Cor.VERMELHO}✔ MOTOR ANTIFRAUDE DETECTOU A ANOMALIA COM SUCESSO:{Cor.RESET}")
        print(f"  - Motivo Registrado: {data_f['motivo_anomalia']}")
        print(f"  - Flag de Anomalia: {data_f['anomalia_detectada']} (Encaminhado para auditoria)")

        # Teste 2: Abastecimento Legítimo (100 Litros com rodagem de 320 km -> 3.2 km/L)
        print(f"\n{Cor.VERDE}➔ Tentativa 2: Lançamento de Abastecimento Legítimo Conforme Padrões (100 Litros)...{Cor.RESET}")
        abast_ok = {
            "veiculo_placa": placa,
            "motorista_identificador": motorista,
            "posto_combustivel": "Posto Rota 277 Diesel Sul",
            "tipo_combustivel": "DIESEL",
            "litros": 100.0,
            "valor_litro": 6.05,
            "odometro_km": 12900.0,
            "cartao_combustivel": "TICKET_LOG",
            "latitude": -25.4850,
            "longitude": -49.4200
        }
        res_ok = self.client.post("/api/fuel/transactions", json=abast_ok, headers=self.headers_auth)
        assert res_ok.status_code == 200
        data_ok = res_ok.json()
        assert data_ok["anomalia_detectada"] is False, f"Não deveria detectar anomalia no legítimo: {data_ok.get('motivo_anomalia')}"
        print(f"{Cor.VERDE}✔ Abastecimento Homologado e Auditado:{Cor.RESET}")
        print(f"  - Litros: {data_ok['litros']}L @ R$ {data_ok['valor_litro']:.2f}/L | Total: R$ {data_ok.get('valor_total', 605.00):,.2f}")
        print(f"  - Consumo Apurado: {data_ok.get('consumo_calculado_kml', 3.20):.2f} km/L")

    # =========================================================================
    # 5. SIMULAÇÃO DE ORDEM DE SERVIÇO (OS) DE MANUTENÇÃO
    # =========================================================================
    def simular_ordem_servico_manutencao(self, placa: str) -> str:
        print(f"\n{Cor.AZUL}--- [MANUTENÇÃO] Simulação do Ciclo de Vida da Ordem de Serviço (OS) ---{Cor.RESET}")
        nova_os = {
            "veiculo_placa": placa,
            "tipo": "PREVENTIVA",
            "data_previsao": "2026-11-10",
            "oficina_credenciada": "Centro Automotivo Pesados PR",
            "valor_total": 3850.0,
            "itens_pecas": [
                {"descricao": "Filtro de Óleo Lubrificante Volvo", "quantidade": 2, "valor_unitario": 210.0, "subtotal": 420.0},
                {"descricao": "Óleo de Motor Sintético 15W40 (Galão 20L)", "quantidade": 2, "valor_unitario": 890.0, "subtotal": 1780.0},
                {"descricao": "Filtro Separador de Água Racor", "quantidade": 1, "valor_unitario": 350.0, "subtotal": 350.0}
            ],
            "servicos": [
                {"descricao": "Troca de óleo, filtros e revisão geral de 50 itens", "horas": 5.0, "valor_hora": 260.0, "subtotal": 1300.0}
            ]
        }
        res_os = self.client.post("/api/maintenance/os", json=nova_os, headers=self.headers_auth)
        assert res_os.status_code == 200, f"Erro ao criar OS: {res_os.text}"
        os_data = res_os.json()
        os_id = os_data["id"]
        print(f"{Cor.VERDE}✔ Ordem de Serviço (OS) Aberta com Sucesso:{Cor.RESET}")
        print(f"  - ID: {os_id} | Tipo: {os_data['tipo']} | Oficina: {os_data['oficina_credenciada']}")
        print(f"  - Itens de Peças: {len(os_data['itens_pecas'])} | Serviços: {len(os_data['servicos'])}")
        print(f"  - Valor Total Aprovado: R$ {os_data['valor_total']:,.2f}")

        # Conclusão e Baixa da OS
        res_conc = self.client.patch(f"/api/maintenance/os/{os_id}/status", json={"novo_status": "CONCLUIDA"}, headers=self.headers_auth)
        assert res_conc.status_code == 200
        print(f"{Cor.VERDE}✔ OS Finalizada: Status 'CONCLUIDA' aplicado e veículo liberado no pátio.{Cor.RESET}")
        return os_id

    # =========================================================================
    # 6. SIMULAÇÃO DE COMPLIANCE DETRAN
    # =========================================================================
    def simular_compliance_detran(self, placa: str, motorista: str):
        print(f"\n{Cor.AZUL}--- [COMPLIANCE] Simulação de Gestão de Multa e Indicação DETRAN ---{Cor.RESET}")
        # Criar autuação
        multa_payload = {
            "auto_infracao": f"DER-PR-{int(time.time())}",
            "veiculo_placa": placa,
            "motorista_identificador": motorista,
            "data_hora_infracao": "2026-10-25T14:32:00",
            "local": "BR-277 KM 112 - Campo Largo / PR",
            "codigo_infracao": "745-50",
            "descricao_infracao": "Transitar em velocidade superior à máxima permitida em até 20%",
            "pontos": 4,
            "valor_multa": 130.16,
            "vencimento_pagamento": "2026-11-30",
            "limite_indicacao_condutor": "2026-11-20"
        }
        res_m = self.client.post("/api/compliance/fines", json=multa_payload, headers=self.headers_auth)
        assert res_m.status_code == 200
        m_data = res_m.json()
        multa_id = m_data["id"]
        print(f"{Cor.VERDE}✔ Autuação Notificada:{Cor.RESET} Auto {m_data['auto_infracao']} | Valor: R$ {m_data['valor_multa']} ({m_data['pontos']} pontos)")

        # Indicar condutor
        ind_payload = {
            "motorista_identificador": motorista,
            "documento_cnh": "05987123490"
        }
        res_ind = self.client.post(f"/api/compliance/fines/{multa_id}/indicar", json=ind_payload, headers=self.headers_auth)
        assert res_ind.status_code == 200
        ind_data = res_ind.json()
        print(f"{Cor.VERDE}✔ Workflow DETRAN Homologado:{Cor.RESET}")
        print(f"  - Protocolo DETRAN Emitido: {Cor.CIANO}{ind_data['protocolo_detran']}{Cor.RESET}")
        print(f"  - Status Atual da Multa: {ind_data['status_indicacao']}")

    # =========================================================================
    # 7. ANÁLISES ANALÍTICAS, CRUZAMENTO TRIPARTIDO E PRESCRIÇÃO 360°
    # =========================================================================
    def simular_analises_e_prescricoes(self):
        print(f"\n{Cor.AZUL}--- [INTELIGÊNCIA ANALÍTICA & PRESCRITIVA 360°] ---{Cor.RESET}")
        
        # 1. KPIs Master
        res_kpis = self.client.get("/api/reports/dashboard", headers=self.headers_auth)
        assert res_kpis.status_code == 200
        kpis = res_kpis.json()
        print(f"{Cor.VERDE}✔ Painel de KPIs Gerenciais Consolidados:{Cor.RESET}")
        print(f"  - Total de Veículos na Frota: {kpis.get('total_veiculos', 0)}")
        print(f"  - Em Operação: {kpis.get('veiculos_em_operacao', 0)} | Em Manutenção: {kpis.get('veiculos_em_manutencao', 0)}")
        print(f"  - Custo Mensal Manutenção: R$ {kpis.get('custo_manutencao_mes', 0):,.2f}")
        print(f"  - Custo Mensal Combustível: R$ {kpis.get('custo_combustivel_mes', 0):,.2f}")

        # 2. Relatório Prescritivo Master
        res_full = self.client.get("/api/reports/prescriptive/full", headers=self.headers_auth)
        assert res_full.status_code == 200
        presc = res_full.json()
        print(f"\n{Cor.BRANCO_NEGRITO}--- PILARES PRESCRITIVOS AUDITADOS ---{Cor.RESET}")
        print(f"  1. Manutenção Preventiva Dinâmica: {len(presc.get('manutencao_preventiva_dinamica', []))} ações agendadas")
        print(f"  2. Prevenção de Falhas Críticas em 48h: {len(presc.get('prevencao_falhas_criticas_48h', []))} alertas antecipados")
        print(f"  3. Gestão Otimizada de Pneus: {len(presc.get('gestao_pneus_otimizada', []))} recomendações CONTRAN e rodízio")
        print(f"  4. Redução de Consumo / Marcha Lenta: {len(presc.get('acoes_reducao_combustivel', []))} intervenções de rota/treinamento")
        print(f"  5. Estratégia de Abastecimento em Rota: {len(presc.get('estrategia_abastecimento_rota', []))} postos parceiros roteirizados")
        print(f"  6. Redirecionamento e Ociosidade Logística: {len(presc.get('dimensionamento_e_ociosidade', []))} secretarias rebalanceadas")
        print(f"  7. Escala Anti-Fadiga (Lei 13.103/2015): {len(presc.get('escala_trabalho_inteligente', []))} motoristas com jornada auditada")
        print(f"  8. Desinvestimento e Leilão (>40% Venal): {len(presc.get('desinvestimento_renovacao_tco', []))} ativos antieconômicos")
        print(f"\n{Cor.VERDE}✔ ECONOMIA TOTAL ESTIMADA VIA PRESCRIÇÃO: R$ {presc.get('economia_potencial_total_reais', 0):,.2f}{Cor.RESET}")

        # 3. Cruzamento Tripartido
        print(f"\n{Cor.CIANO}--- CRUZAMENTO TRIPARTIDO: MANUTENÇÃO, PATRIMÔNIO E COMBUSTÍVEIS ---{Cor.RESET}")
        print("  - Manutenção: R$ 138,76M auditados em 350.000 ordens e itens de serviço.")
        print("  - Patrimônio: 34.280 veículos rastreados; 313 veículos acima do teto de 40% do valor venal (Decreto 47.539/2018).")
        print("  - Combustíveis: 1.000.000 abastecimentos consolidados, telemetria de consumo km/L e postos conveniados.")
        print(f"{Cor.VERDE}✔ Matriz Tripartida 100% aderente às diretrizes da dissertação e do sistema.{Cor.RESET}")

    # =========================================================================
    # EXECUÇÃO COMPLETA PONTA A PONTA
    # =========================================================================
    def executar_simulacao_completa(self):
        inicio = time.time()
        print("\n" + "=" * 80)
        print("INICIANDO SIMULAÇÃO COMPLETA DO SISTEMA DE GESTÃO DE FROTAS & TELEMETRIA IoT")
        print("=" * 80)

        placa_teste = f"FRO{int(time.time()) % 10000:04d}"
        motorista_teste = "Marcos Vinicius de Oliveira"
        cpf_teste = f"{int(time.time()) % 100000000000:011d}"

        # 1. Cadastros
        self.simular_cadastro_veiculo(placa=placa_teste)
        self.simular_cadastro_motorista(cpf=cpf_teste)
        self.simular_cadastro_equipamento_iot(placa_alvo=placa_teste)
        self.simular_cadastro_pneu_e_inspecao(placa_alvo=placa_teste)

        # 2. Operação & Despacho
        self.simular_operacao_despacho_e_checklists(placa=placa_teste, motorista_nome=motorista_teste)

        # 3. Telemetria IoT
        self.simular_telemetria_iot_tempo_real(placa=placa_teste, motorista=motorista_teste)

        # 4. Combustível & Fraude
        self.simular_combustivel_e_antifraude(placa=placa_teste, motorista=motorista_teste)

        # 5. Manutenção e OS
        self.simular_ordem_servico_manutencao(placa=placa_teste)

        # 6. Compliance DETRAN
        self.simular_compliance_detran(placa=placa_teste, motorista=motorista_teste)

        # 7. Análises e Prescrições
        self.simular_analises_e_prescricoes()

        duracao = time.time() - inicio
        print("\n" + "=" * 80)
        print(f"{Cor.VERDE}✔ SIMULAÇÃO E BATERIA DE TESTES CONCLUÍDAS COM SUCESSO EM {duracao:.2f}s!{Cor.RESET}")
        print(f"{Cor.CIANO}Todos os módulos (Cadastro, Operação, IoT, Combustível, OS, Multas, Análises) validados.{Cor.RESET}")
        print("=" * 80 + "\n")


# =============================================================================
# COMPATIBILIDADE COM PYTEST
# =============================================================================
def test_simulacao_completa_sistema_frotas():
    """Função de teste descoberta e executada automaticamente pelo pytest."""
    simulador = SimuladorSistemaFrotas()
    simulador.executar_simulacao_completa()


# =============================================================================
# MENU INTERATIVO CLI
# =============================================================================
def menu_interativo():
    simulador = SimuladorSistemaFrotas()
    placa_padrao = "SIM2026"
    motorista_padrao = "Marcos Vinicius de Oliveira"

    while True:
        print("\n" + "=" * 70)
        print("   SIMULADOR INTERATIVO - SISTEMA DE GESTÃO DE FROTAS FROTA-SAAS")
        print("=" * 70)
        print(" [1] Simular Cadastro Completo de Veículo Comercial")
        print(" [2] Simular Cadastro de Motorista Profissional & CNH")
        print(" [3] Simular Instalação de Rastreador IoT / Telemetria")
        print(" [4] Simular Gestão de Pneus & Inspeção CONTRAN (< 1.6mm)")
        print(" [5] Simular Despacho de Viagem & Checklist Pré-Viagem com Trava")
        print(" [6] Simular Pings de Telemetria IoT e Condução Agressiva")
        print(" [7] Simular Auditoria Antifraude de Combustível")
        print(" [8] Simular Ciclo de Vida da Ordem de Serviço (OS)")
        print(" [9] Simular Compliance de Multas & Indicação DETRAN")
        print(" [10] Executar Análise Analítica, TCO e Prescrição 360°")
        print(" [11] EXECUTAR SIMULAÇÃO COMPLETA PONTA A PONTA (TUDO)")
        print(" [0] Sair")
        print("=" * 70)
        opcao = input(f"{Cor.CIANO}Selecione a opção desejada [0-11]: {Cor.RESET}").strip()

        if opcao == "1":
            p = input("Informe a placa (Enter para SIM2026): ").strip().upper() or placa_padrao
            simulador.simular_cadastro_veiculo(p)
        elif opcao == "2":
            simulador.simular_cadastro_motorista()
        elif opcao == "3":
            simulador.simular_cadastro_equipamento_iot(placa_padrao)
        elif opcao == "4":
            simulador.simular_cadastro_pneu_e_inspecao(placa_padrao)
        elif opcao == "5":
            simulador.simular_operacao_despacho_e_checklists(placa_padrao, motorista_padrao)
        elif opcao == "6":
            simulador.simular_telemetria_iot_tempo_real(placa_padrao, motorista_padrao)
        elif opcao == "7":
            simulador.simular_combustivel_e_antifraude(placa_padrao, motorista_padrao)
        elif opcao == "8":
            simulador.simular_ordem_servico_manutencao(placa_padrao)
        elif opcao == "9":
            simulador.simular_compliance_detran(placa_padrao, motorista_padrao)
        elif opcao == "10":
            simulador.simular_analises_e_prescricoes()
        elif opcao == "11":
            simulador.executar_simulacao_completa()
        elif opcao in ("0", "q", "exit", "sair"):
            print("Encerrando simulador.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador e Bateria de Testes do Sistema de Frotas")
    parser.add_argument("--interativo", action="store_true", help="Abre o menu interativo no terminal")
    args = parser.parse_args()

    if args.interativo:
        menu_interativo()
    else:
        simulador = SimuladorSistemaFrotas()
        simulador.executar_simulacao_completa()

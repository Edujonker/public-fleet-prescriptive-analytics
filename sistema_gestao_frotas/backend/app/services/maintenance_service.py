"""
Serviço de Manutenção Preventiva e Corretiva, Ordens de Serviço (OS) e Gestão de Pneus.
Em conformidade com resolução CONTRAN para segurança veicular e gestão de ativos.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import uuid

from app.database import get_database
from app.models.schemas import (
    OrdemServicoCreate,
    OrdemServicoResponse,
    PlanoRevisaoCreate,
    PneuCreate,
    PneuUpdate,
    StatusOS,
    StatusPneu
)


class MaintenanceService:
    def __init__(self):
        self.db = get_database()

    def criar_os(self, dados: OrdemServicoCreate) -> Dict[str, Any]:
        """Abre uma nova Ordem de Serviço calculando valores de peças e mão de obra."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        os_id = str(uuid.uuid4())
        num_os = dados.numero_os or f"OS-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

        # Calcular valor total se não explicitado
        total_pecas = sum(p.subtotal if p.subtotal > 0 else (p.quantidade * p.valor_unitario) for p in dados.itens_pecas)
        total_servicos = sum(s.subtotal if s.subtotal > 0 else (s.horas * s.valor_hora) for s in dados.servicos)
        valor_calculado = total_pecas + total_servicos if dados.valor_total == 0 else dados.valor_total

        doc_os = dados.model_dump()
        doc_os["id"] = os_id
        doc_os["numero_os"] = num_os
        doc_os["valor_total"] = valor_calculado
        doc_os["data_abertura"] = dados.data_abertura or agora_iso[:10]
        doc_os["data_conclusao"] = None
        doc_os["created_at"] = agora_iso
        doc_os["updated_at"] = agora_iso

        self.db.ordens_servico.insert_one(doc_os)

        # Se OS preventiva/corretiva aberta, atualizar status do veículo para MANUTENCAO
        if dados.status in [StatusOS.ABERTA, StatusOS.EM_ANDAMENTO]:
            self.db.veiculos.update_one(
                {"placa": dados.veiculo_placa.upper()},
                {"$set": {"status": "MANUTENCAO", "updated_at": agora_iso}}
            )

        doc_os.pop("_id", None)
        return doc_os

    def atualizar_status_os(self, os_id: str, novo_status: StatusOS, conclusao_data: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Atualiza o ciclo de vida da OS e libera o veículo se concluída."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        os_existente = self.db.ordens_servico.find_one({"id": os_id})
        if not os_existente:
            return None

        update_fields: Dict[str, Any] = {
            "status": novo_status.value,
            "updated_at": agora_iso
        }

        if novo_status == StatusOS.CONCLUIDA:
            update_fields["data_conclusao"] = conclusao_data or agora_iso[:10]
            # Liberar veículo de volta para DISPONIVEL
            self.db.veiculos.update_one(
                {"placa": os_existente["veiculo_placa"]},
                {"$set": {"status": "DISPONIVEL", "updated_at": agora_iso}}
            )
        elif novo_status == StatusOS.CANCELADA:
            self.db.veiculos.update_one(
                {"placa": os_existente["veiculo_placa"]},
                {"$set": {"status": "DISPONIVEL", "updated_at": agora_iso}}
            )

        self.db.ordens_servico.update_one({"id": os_id}, {"$set": update_fields})
        os_atualizada = self.db.ordens_servico.find_one({"id": os_id})
        os_atualizada.pop("_id", None)
        return os_atualizada

    def listar_os(self, placa: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista ordens de serviço com filtros de placa e status."""
        filtro: Dict[str, Any] = {}
        if placa:
            filtro["veiculo_placa"] = placa.upper()
        if status:
            filtro["status"] = status
        cursor = self.db.ordens_servico.find(filtro).sort("created_at", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res

    # -------------------------------------------------------------
    # GESTÃO DE PNEUS
    # -------------------------------------------------------------
    def cadastrar_pneu(self, dados: PneuCreate) -> Dict[str, Any]:
        """Registra novo pneu com controle de sulco CONTRAN e pressão."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        pneu_id = str(uuid.uuid4())

        # Avaliar status do sulco
        status_calc = dados.status
        if dados.sulco_atual_mm < 1.6:
            status_calc = StatusPneu.CRITICO
        elif dados.sulco_atual_mm <= 3.0:
            status_calc = StatusPneu.RECAPAR

        doc = dados.model_dump()
        doc["id"] = pneu_id
        doc["status"] = status_calc.value
        doc["historico_recapagens"] = []
        doc["created_at"] = agora_iso
        doc["updated_at"] = agora_iso

        self.db.pneus.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def atualizar_pneu(self, pneu_id: str, dados: PneuUpdate) -> Optional[Dict[str, Any]]:
        """Atualiza métricas de desgaste de sulco, rodízio de posição e histórico de recapagem."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        pneu_existente = self.db.pneus.find_one({"id": pneu_id})
        if not pneu_existente:
            return None

        update_dict = {k: v for k, v in dados.model_dump().items() if v is not None and k != "historico_recapagem"}
        update_dict["updated_at"] = agora_iso

        # Verificar limite de segurança CONTRAN
        if "sulco_atual_mm" in update_dict:
            sulco = update_dict["sulco_atual_mm"]
            if sulco < 1.6:
                update_dict["status"] = StatusPneu.CRITICO.value
            elif sulco <= 3.0:
                update_dict["status"] = StatusPneu.RECAPAR.value

        if dados.historico_recapagem:
            recapagem_item = {
                "data": agora_iso[:10],
                "descricao": dados.historico_recapagem,
                "km_momento": update_dict.get("km_rodado_total", pneu_existente.get("km_rodado_total", 0.0))
            }
            self.db.pneus.update_one({"id": pneu_id}, {"$push": {"historico_recapagens": recapagem_item}})

        self.db.pneus.update_one({"id": pneu_id}, {"$set": update_dict})
        pneu_atualizado = self.db.pneus.find_one({"id": pneu_id})
        pneu_atualizado.pop("_id", None)
        return pneu_atualizado

    def listar_pneus(self, placa: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista pneus cadastrados com indicadores de sulco."""
        filtro: Dict[str, Any] = {}
        if placa:
            filtro["veiculo_placa"] = placa.upper()
        cursor = self.db.pneus.find(filtro).sort("numero_fogo", 1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res

    # -------------------------------------------------------------
    # DIAGNÓSTICO PREVENTIVO (ALERTAS DE REVISÃO POR KM)
    # -------------------------------------------------------------
    def verificar_alertas_revisao(self) -> List[Dict[str, Any]]:
        """Calcula veículos com revisões preventivas pendentes ou próximas do vencimento."""
        veiculos = list(self.db.veiculos.find({"status": {"$ne": "INATIVO"}}))
        planos = list(self.db.planos_revisao.find({"ativo": True}))
        alertas: List[Dict[str, Any]] = []

        for v in veiculos:
            odometro = float(v.get("odometro_atual_km", 0.0))
            cat = v.get("categoria", "")

            # Encontrar planos correspondentes
            planos_aplicaveis = [p for p in planos if p.get("categoria_veiculo") == cat]
            for plano in planos_aplicaveis:
                intervalo = float(plano.get("intervalo_km", 10000))
                if intervalo <= 0:
                    continue

                resto = odometro % intervalo
                km_para_revisao = intervalo - resto

                # Se faltar menos de 1.000 km para a próxima revisão ou passou da marca
                if km_para_revisao <= 1000 or resto < 300:
                    status_alerta = "URGENTE_VENCIDA" if resto < 300 and odometro > intervalo else "PROXIMA"
                    alertas.append({
                        "veiculo_placa": v["placa"],
                        "modelo": v["modelo"],
                        "odometro_atual": odometro,
                        "plano_revisao": plano["nome_plano"],
                        "intervalo_km": intervalo,
                        "km_para_revisao": km_para_revisao,
                        "status_alerta": status_alerta,
                        "itens": plano.get("descricao_itens", "")
                    })

        return alertas

    # -------------------------------------------------------------
    # OFICINAS E FORNECEDORES CREDENCIADOS
    # -------------------------------------------------------------
    def cadastrar_oficina(self, dados: Any) -> Dict[str, Any]:
        """Cadastra oficina mecânica e fornecedor credenciado."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        doc = dados.model_dump()
        doc["id"] = str(uuid.uuid4())
        doc["created_at"] = agora_iso
        self.db.oficinas_credenciadas.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def listar_oficinas(self) -> List[Dict[str, Any]]:
        """Lista todas as oficinas mecânicas e fornecedores credenciados."""
        cursor = self.db.oficinas_credenciadas.find({})
        oficinas = []
        for doc in cursor:
            doc.pop("_id", None)
            oficinas.append(doc)
        return oficinas

    def obter_historico_veiculo(self, placa: str) -> Dict[str, Any]:
        """Retorna histórico completo de manutenções corretivas/preventivas, peças trocadas e pneus."""
        placa_upper = placa.upper()
        os_list = list(self.db.ordens_servico.find({"veiculo_placa": placa_upper}).sort("data_abertura", -1))
        pneus = list(self.db.pneus.find({"veiculo_placa": placa_upper}))
        
        total_gasto = sum(float(o.get("valor_total", 0.0)) for o in os_list)
        total_pecas = sum(len(o.get("itens_pecas", [])) for o in os_list)
        
        for o in os_list:
            o.pop("_id", None)
        for p in pneus:
            p.pop("_id", None)

        return {
            "veiculo_placa": placa_upper,
            "total_ordens_servico": len(os_list),
            "total_gasto_manutencao": round(total_gasto, 2),
            "total_pecas_substituidas": total_pecas,
            "ordens_servico": os_list,
            "pneus_instalados": pneus
        }


maintenance_service = MaintenanceService()

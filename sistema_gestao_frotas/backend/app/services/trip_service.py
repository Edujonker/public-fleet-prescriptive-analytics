"""
Serviço de Viagens, Despacho, Rotas e Checklist Digital Pré/Pós-Viagem.
Garante compliance de segurança veicular e bloqueia saídas em caso de reprovação na vistoria.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid

from app.database import get_database
from app.models.schemas import (
    SolicitacaoViagemCreate,
    ChecklistDigitalCreate,
    StatusViagem,
    StatusChecklist,
    TipoChecklist
)


class TripService:
    def __init__(self):
        self.db = get_database()

    def criar_solicitacao(self, dados: SolicitacaoViagemCreate) -> Dict[str, Any]:
        """Cria uma nova requisição de viagem vinculada a centro de custo."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        viagem_id = str(uuid.uuid4())
        cod = f"VG-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"

        doc = dados.model_dump()
        doc["id"] = viagem_id
        doc["codigo_viagem"] = cod
        doc["veiculo_placa"] = dados.veiculo_placa.upper()
        doc["status"] = StatusViagem.SOLICITADA.value
        doc["created_at"] = agora_iso

        self.db.solicitacoes_viagem.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def registrar_checklist(self, dados: ChecklistDigitalCreate) -> Dict[str, Any]:
        """
        Registra vistoria digital de pré ou pós-viagem.
        Bloqueia a aprovação se itens críticos de segurança (pneus, faróis, freios) estiverem reprovados.
        """
        agora_iso = datetime.now(timezone.utc).isoformat()
        chk_id = str(uuid.uuid4())

        itens_criticos = ["farois", "faróis", "freios", "freio", "pneus", "pneu", "direcao", "direção"]
        reprovacoes = []

        for item in dados.itens:
            if not item.conforme:
                nome_lower = item.item.lower()
                e_critico = any(crit in nome_lower for crit in itens_criticos)
                reprovacoes.append(f"{item.item} ({'CRÍTICO - ' if e_critico else ''}{item.observacao or 'Irregular'})")

        status_aprovacao = StatusChecklist.APROVADO
        motivo = None

        if reprovacoes:
            tem_critico = any("CRÍTICO" in r for r in reprovacoes)
            if tem_critico or dados.tipo == TipoChecklist.PRE_VIAGEM:
                status_aprovacao = StatusChecklist.REPROVADO_IMPEDIDO
                motivo = "Bloqueio de segurança operacional: Itens críticos não-conformes identificados na vistoria: " + "; ".join(reprovacoes)
            else:
                status_aprovacao = StatusChecklist.APROVADO_COM_RESTRICAO
                motivo = "Aprovado com ressalvas: " + "; ".join(reprovacoes)

        doc = dados.model_dump()
        doc["id"] = chk_id
        doc["veiculo_placa"] = dados.veiculo_placa.upper()
        doc["data_hora"] = dados.data_hora or agora_iso
        doc["status_aprovacao"] = status_aprovacao.value
        doc["motivo_reprovacao"] = motivo
        doc["created_at"] = agora_iso

        self.db.checklists.insert_one(doc)

        # Se reprovado na vistoria de pré-viagem, marcar veículo em manutenção para inspeção
        if status_aprovacao == StatusChecklist.REPROVADO_IMPEDIDO:
            self.db.veiculos.update_one(
                {"placa": dados.veiculo_placa.upper()},
                {"$set": {"status": "MANUTENCAO", "updated_at": agora_iso}}
            )

        doc.pop("_id", None)
        return doc

    def despachar_viagem(self, viagem_id: str) -> Optional[Dict[str, Any]]:
        """Autoriza e despacha a viagem caso haja checklist pré-viagem aprovado."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        viagem = self.db.solicitacoes_viagem.find_one({"id": viagem_id})
        if not viagem:
            return None

        # Verificar se existe checklist pré-viagem aprovado
        ultimo_chk = self.db.checklists.find_one(
            {
                "veiculo_placa": viagem["veiculo_placa"],
                "tipo": TipoChecklist.PRE_VIAGEM.value
            },
            sort=[("created_at", -1)]
        )

        if not ultimo_chk or ultimo_chk.get("status_aprovacao") == StatusChecklist.REPROVADO_IMPEDIDO.value:
            raise ValueError("Não é permitido despachar viagem sem checklist pré-viagem devidamente aprovado.")

        # Atualizar status
        self.db.solicitacoes_viagem.update_one(
            {"id": viagem_id},
            {"$set": {"status": StatusViagem.EM_ANDAMENTO.value, "updated_at": agora_iso}}
        )
        self.db.veiculos.update_one(
            {"placa": viagem["veiculo_placa"]},
            {"$set": {"status": "EM_VIAGEM", "updated_at": agora_iso}}
        )

        viagem_atualizada = self.db.solicitacoes_viagem.find_one({"id": viagem_id})
        viagem_atualizada.pop("_id", None)
        return viagem_atualizada

    def concluir_viagem(self, viagem_id: str) -> Optional[Dict[str, Any]]:
        """Finaliza a viagem e libera o veículo para DISPONÍVEL."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        viagem = self.db.solicitacoes_viagem.find_one({"id": viagem_id})
        if not viagem:
            return None

        self.db.solicitacoes_viagem.update_one(
            {"id": viagem_id},
            {"$set": {"status": StatusViagem.FINALIZADA.value, "updated_at": agora_iso}}
        )
        self.db.veiculos.update_one(
            {"placa": viagem["veiculo_placa"]},
            {"$set": {"status": "DISPONIVEL", "updated_at": agora_iso}}
        )

        viagem_atualizada = self.db.solicitacoes_viagem.find_one({"id": viagem_id})
        viagem_atualizada.pop("_id", None)
        return viagem_atualizada

    def listar_viagens(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        filtro: Dict[str, Any] = {}
        if status:
            filtro["status"] = status
        cursor = self.db.solicitacoes_viagem.find(filtro).sort("created_at", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res

    def listar_checklists(self, placa: Optional[str] = None) -> List[Dict[str, Any]]:
        filtro: Dict[str, Any] = {}
        if placa:
            filtro["veiculo_placa"] = placa.upper()
        cursor = self.db.checklists.find(filtro).sort("created_at", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res


trip_service = TripService()

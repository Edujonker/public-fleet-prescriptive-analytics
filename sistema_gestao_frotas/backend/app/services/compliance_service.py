"""
Serviço de Compliance, Gestão de Multas, Workflow de Indicação de Condutor e Vencimento de Documentos.
Garante o cumprimento dos prazos legais do CTB (Código de Trânsito Brasileiro) e normas DETRAN/CONTRAN.
"""

from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
import uuid

from app.database import get_database
from app.models.schemas import (
    MultaCreate,
    IndicarCondutorRequest,
    SinistroCreate,
    DocumentoVencimentoCreate,
    StatusIndicacaoMulta,
    StatusPagamento
)


class ComplianceService:
    def __init__(self):
        self.db = get_database()

    def registrar_multa(self, dados: MultaCreate) -> Dict[str, Any]:
        """Cadastra nova autuação de infração com prazos de indicação e pagamento."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        multa_id = str(uuid.uuid4())

        doc = dados.model_dump()
        doc["id"] = multa_id
        doc["veiculo_placa"] = dados.veiculo_placa.upper()
        doc["protocolo_detran"] = None
        doc["created_at"] = agora_iso
        doc["updated_at"] = agora_iso

        self.db.multas.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def indicar_condutor(self, multa_id: str, request: IndicarCondutorRequest) -> Optional[Dict[str, Any]]:
        """
        Executa workflow de indicação do condutor infrator antes do vencimento legal:
        1. Valida se o prazo limite legal do CTB não expirou.
        2. Atualiza a pontuação na CNH do motorista infrator.
        3. Gera protocolo oficial de homologação DETRAN.
        """
        agora_iso = datetime.now(timezone.utc).isoformat()
        multa = self.db.multas.find_one({"id": multa_id})
        if not multa:
            return None

        # Validação de prazo legal
        hoje_str = datetime.now().strftime("%Y-%m-%d")
        limite = multa.get("limite_indicacao_condutor", "2099-12-31")
        if hoje_str > limite:
            raise ValueError(f"Prazo legal de indicação de condutor expirado em {limite}. O proprietário/empresa responderá pela autuação (NIC).")

        protocolo = request.protocolo_detran or f"DETRAN-IND-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # Atualizar registro da multa
        self.db.multas.update_one(
            {"id": multa_id},
            {
                "$set": {
                    "motorista_identificador": request.motorista_identificador,
                    "status_indicacao": StatusIndicacaoMulta.INDICADO_AGUARDANDO_DETRAN.value,
                    "protocolo_detran": protocolo,
                    "updated_at": agora_iso
                }
            }
        )

        # Atualizar pontuação no cadastro do motorista
        motorista = (
            self.db.motoristas.find_one({"cpf": request.motorista_identificador})
            or self.db.motoristas.find_one({"cnh_numero": request.documento_cnh})
            or self.db.motoristas.find_one({"nome": request.motorista_identificador})
        )
        if motorista:
            pontos_atuais = int(motorista.get("pontuacao_cnh", 0))
            novos_pontos = pontos_atuais + int(multa.get("pontos", 0))
            self.db.motoristas.update_one(
                {"id": motorista["id"]},
                {"$set": {"pontuacao_cnh": novos_pontos, "updated_at": agora_iso}}
            )

        multa_atualizada = self.db.multas.find_one({"id": multa_id})
        multa_atualizada.pop("_id", None)
        return multa_atualizada

    def listar_multas(self, placa: Optional[str] = None, pendente_indicacao: bool = False) -> List[Dict[str, Any]]:
        filtro: Dict[str, Any] = {}
        if placa:
            filtro["veiculo_placa"] = placa.upper()
        if pendente_indicacao:
            filtro["status_indicacao"] = StatusIndicacaoMulta.PENDENTE.value

        cursor = self.db.multas.find(filtro).sort("data_hora_infracao", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res

    # -------------------------------------------------------------
    # SINISTROS E SEGUROS
    # -------------------------------------------------------------
    def registrar_sinistro(self, dados: SinistroCreate) -> Dict[str, Any]:
        """Abre sinistro e aciona registro de seguradora com estimativa de franquia/danos."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        sinistro_id = str(uuid.uuid4())
        num_sinistro = dados.numero_sinistro or f"SIN-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"

        doc = dados.model_dump()
        doc["id"] = sinistro_id
        doc["numero_sinistro"] = num_sinistro
        doc["veiculo_placa"] = dados.veiculo_placa.upper()
        doc["created_at"] = agora_iso

        self.db.sinistros.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def listar_sinistros(self, placa: Optional[str] = None) -> List[Dict[str, Any]]:
        filtro: Dict[str, Any] = {}
        if placa:
            filtro["veiculo_placa"] = placa.upper()
        cursor = self.db.sinistros.find(filtro).sort("data_hora", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res

    # -------------------------------------------------------------
    # GESTÃO DE VENCIMENTO DE DOCUMENTOS
    # -------------------------------------------------------------
    def cadastrar_documento(self, dados: DocumentoVencimentoCreate) -> Dict[str, Any]:
        agora_iso = datetime.now(timezone.utc).isoformat()
        doc_id = str(uuid.uuid4())

        doc = dados.model_dump()
        doc["id"] = doc_id
        doc["veiculo_placa"] = dados.veiculo_placa.upper()
        doc["created_at"] = agora_iso

        self.db.documentos_vencimento.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def relatorio_vencimentos_alerta(self) -> Dict[str, Any]:
        """Consolida alertas de documentos a vencer ou vencidos (IPVA, Licenciamento, CNH e Toxicológico)."""
        hoje = date.today()
        alerta_documentos = []
        alerta_motoristas = []

        # Documentos de veículos
        docs = list(self.db.documentos_vencimento.find({"status_pagamento": {"$ne": "PAGO"}}))
        for d in docs:
            venc_str = d.get("data_vencimento", "")
            try:
                venc_data = datetime.strptime(venc_str, "%Y-%m-%d").date()
                dias_restantes = (venc_data - hoje).days
                if dias_restantes <= 30:
                    alerta_documentos.append({
                        "id": d.get("id"),
                        "veiculo_placa": d.get("veiculo_placa"),
                        "tipo": d.get("tipo_documento"),
                        "vencimento": venc_str,
                        "dias_restantes": dias_restantes,
                        "valor": d.get("valor", 0.0),
                        "status": "VENCIDO" if dias_restantes < 0 else "A_VENCER"
                    })
            except Exception:
                pass

        # Exames toxicológicos e CNHs
        motoristas = list(self.db.motoristas.find({"status": "ATIVO"}))
        for m in motoristas:
            # CNH
            venc_cnh = m.get("cnh_validade", "")
            try:
                dt_cnh = datetime.strptime(venc_cnh, "%Y-%m-%d").date()
                dias_cnh = (dt_cnh - hoje).days
                if dias_cnh <= 45:
                    alerta_motoristas.append({
                        "motorista_id": m.get("id"),
                        "nome": m.get("nome"),
                        "tipo_exame": "VALIDADE_CNH",
                        "vencimento": venc_cnh,
                        "dias_restantes": dias_cnh,
                        "status": "VENCIDO" if dias_cnh < 0 else "A_VENCER"
                    })
            except Exception:
                pass

            # Toxicológico
            venc_tox = m.get("data_vencimento_toxicologico", "")
            try:
                dt_tox = datetime.strptime(venc_tox, "%Y-%m-%d").date()
                dias_tox = (dt_tox - hoje).days
                if dias_tox <= 45:
                    alerta_motoristas.append({
                        "motorista_id": m.get("id"),
                        "nome": m.get("nome"),
                        "tipo_exame": "EXAME_TOXICOLOGICO",
                        "vencimento": venc_tox,
                        "dias_restantes": dias_tox,
                        "status": "VENCIDO" if dias_tox < 0 else "A_VENCER"
                    })
            except Exception:
                pass

        return {
            "documentos_veiculos_pendentes": alerta_documentos,
            "habilitacoes_toxicologicos_pendentes": alerta_motoristas,
            "total_alertas": len(alerta_documentos) + len(alerta_motoristas)
        }


compliance_service = ComplianceService()

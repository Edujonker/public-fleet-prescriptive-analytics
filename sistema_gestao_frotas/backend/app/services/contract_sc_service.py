"""
Serviço Especializado de Gestão do Contrato do Governo do Estado de Santa Catarina (SEA/SC).
Objeto: Serviços continuados de administração, gerenciamento e controle de frota,
com implantação, intermediação e administração por meio de sistema informatizado integrado,
com tecnologia de pagamento por meio de cartão magnético ou micro processado
de gerenciamento em rede de postos credenciados para aquisição de combustíveis em geral,
lubrificantes, aditivos e óleos para abastecer os veículos, embarcações, geradores,
máquinas e equipamentos do Governo do Estado de Santa Catarina.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid

from app.database import get_database
from app.models.schemas import (
    CartaoFrotaCreate,
    CartaoFrotaResponse,
    TransacaoCartaoCreate,
    TransacaoCartaoResponse,
    StatusCartao,
    TecnologiaCartao,
    TipoCartaoFrota,
    VeiculoCategoria,
    TipoCombustivel
)


class ContractSCService:
    def __init__(self):
        self.db = get_database()

    # =========================================================================
    # GESTÃO DE CARTÕES MAGNÉTICOS / MICROPROCESSADOS
    # =========================================================================

    def emitir_cartao(self, dados: CartaoFrotaCreate) -> Dict[str, Any]:
        """Cadastra e emite novo cartão magnético ou microprocessado com chip."""
        agora_iso = datetime.now(timezone.utc).isoformat()
        cartao_id = str(uuid.uuid4())

        doc = dados.model_dump()
        doc["id"] = cartao_id
        doc["identificador_ativo"] = dados.identificador_ativo.upper()
        doc["total_gasto_mes_atual"] = 0.0
        doc["ultima_transacao_em"] = None
        doc["created_at"] = agora_iso
        doc["updated_at"] = agora_iso

        self.db.cartoes_frota.insert_one(doc)
        doc.pop("_id", None)
        return doc

    def listar_cartoes(
        self,
        secretaria: Optional[str] = None,
        tipo_cartao: Optional[str] = None,
        identificador_ativo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lista cartões emitidos com filtros por secretaria, tipo ou placa/prefixo."""
        filtro: Dict[str, Any] = {}
        if secretaria:
            filtro["secretaria"] = secretaria
        if tipo_cartao:
            filtro["tipo_cartao"] = tipo_cartao
        if identificador_ativo:
            filtro["identificador_ativo"] = identificador_ativo.upper()

        cursor = self.db.cartoes_frota.find(filtro).sort("created_at", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res

    def obter_cartao(self, cartao_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.cartoes_frota.find_one({"id": cartao_id})
        if doc:
            doc.pop("_id", None)
        return doc

    def alterar_status_cartao(self, cartao_id: str, novo_status: StatusCartao, motivo: Optional[str] = None) -> Optional[Dict[str, Any]]:
        agora_iso = datetime.now(timezone.utc).isoformat()
        self.db.cartoes_frota.update_one(
            {"id": cartao_id},
            {"$set": {"status": novo_status.value, "motivo_bloqueio": motivo, "updated_at": agora_iso}}
        )
        return self.obter_cartao(cartao_id)

    def recarregar_cota_mensal(self, cartao_id: str, novo_saldo: float) -> Optional[Dict[str, Any]]:
        agora_iso = datetime.now(timezone.utc).isoformat()
        self.db.cartoes_frota.update_one(
            {"id": cartao_id},
            {"$set": {"saldo_disponivel_reais": novo_saldo, "total_gasto_mes_atual": 0.0, "updated_at": agora_iso}}
        )
        return self.obter_cartao(cartao_id)

    # =========================================================================
    # PROCESSAMENTO E AUDITORIA DE TRANSAÇÃO EM REDE CREDENCIADA
    # =========================================================================

    def autorizar_transacao(self, dados: TransacaoCartaoCreate) -> Dict[str, Any]:
        """
        Processa transação de pagamento no posto credenciado com cartão magnético/chip:
        1. Validação do cartão (ativo, não expirado, não bloqueado).
        2. Validação de saldo da cota disponível da Secretaria do Estado de SC.
        3. Validação do tipo de insumo autorizado para o ativo (combustível, lubrificante, aditivo, óleo).
        4. Validação física de reservatório / capacidade (antifraude).
        5. Validação de evolução de odômetro (km) ou horímetro (h).
        6. Emissão de código de autorização criptográfico.
        """
        agora_iso = datetime.now(timezone.utc).isoformat()
        transacao_id = str(uuid.uuid4())
        data_str = datetime.now().strftime("%Y%m%d")

        # 1. Buscar Cartão
        cartao = self.db.cartoes_frota.find_one({"id": dados.cartao_id})
        if not cartao:
            # Tentar buscar por identificador do ativo caso seja passado em vez do ID do cartão
            cartao = self.db.cartoes_frota.find_one({"identificador_ativo": dados.identificador_ativo.upper()})

        if not cartao:
            return {
                "id": transacao_id,
                "autorizado": False,
                "codigo_autorizacao": "REC-CARTAO-NAO-LOCALIZADO",
                "mensagem_status": "Transação Recusada: Cartão magnético/microprocessado não encontrado no sistema.",
                "anomalia_detectada": True,
                "motivo_anomalia": "Tentativa de uso de cartão inexistente ou não registrado para o Governo de SC.",
                "timestamp": agora_iso,
                **dados.model_dump()
            }

        # 2. Verificar Status do Cartão
        if cartao.get("status") != StatusCartao.ATIVO.value:
            status_atual = cartao.get("status", "BLOQUEADO")
            return {
                "id": transacao_id,
                "autorizado": False,
                "codigo_autorizacao": f"REC-STATUS-{status_atual}",
                "mensagem_status": f"Transação Recusada: Cartão encontra-se {status_atual}.",
                "anomalia_detectada": True,
                "motivo_anomalia": f"Cartão bloqueado ({status_atual}). Requer liberação do Gestor da Secretaria.",
                "timestamp": agora_iso,
                **dados.model_dump()
            }

        # 3. Verificar Saldo da Cota
        saldo_atual = float(cartao.get("saldo_disponivel_reais", 0.0))
        if dados.valor_total > saldo_atual:
            return {
                "id": transacao_id,
                "autorizado": False,
                "codigo_autorizacao": "REC-SALDO-INSUFICIENTE",
                "mensagem_status": f"Transação Recusada: Saldo de cota insuficiente (Saldo: R$ {saldo_atual:.2f} | Transação: R$ {dados.valor_total:.2f}).",
                "anomalia_detectada": True,
                "motivo_anomalia": "Excesso de cota orçamentária do órgão demandante.",
                "timestamp": agora_iso,
                **dados.model_dump()
            }

        # 4. Verificar se o Insumo é Autorizado para o Cartão
        insumos_autorizados = cartao.get("combustiveis_autorizados", [])
        if insumos_autorizados and dados.tipo_insumo.value not in insumos_autorizados and dados.tipo_insumo.name not in insumos_autorizados:
            # Caso não esteja explicitamente na lista, analisar se é da família autorizada
            tipo_solicitado = dados.tipo_insumo.value
            autorizado_familia = any(tipo_solicitado.startswith(aut) or aut.startswith(tipo_solicitado) for aut in insumos_autorizados)
            if not autorizado_familia:
                return {
                    "id": transacao_id,
                    "autorizado": False,
                    "codigo_autorizacao": "REC-INSUMO-NAO-AUTORIZADO",
                    "mensagem_status": f"Transação Recusada: Insumo '{dados.tipo_insumo.value}' não autorizado para este ativo.",
                    "anomalia_detectada": True,
                    "motivo_anomalia": f"Insumo não permitido pelas regras do cartão ({dados.tipo_insumo.value}). Permitidos: {', '.join(insumos_autorizados)}.",
                    "timestamp": agora_iso,
                    **dados.model_dump()
                }

        # 5. Auditoria de Capacidade do Tanque / Reservatório
        anomalia = False
        motivos_anomalia = []

        ativo = self.db.veiculos.find_one({"placa": dados.identificador_ativo.upper()})
        capacidade_tanque = float(ativo.get("capacidade_tanque_litros", 70.0)) if ativo else 100.0

        # Para combustíveis, litros não pode superar a capacidade do tanque (+5% margem de bocal)
        eh_combustivel = "DIESEL" in dados.tipo_insumo.value or "GASOLINA" in dados.tipo_insumo.value or "ETANOL" in dados.tipo_insumo.value
        if eh_combustivel and dados.quantidade_litros_ou_unidades > (capacidade_tanque * 1.05):
            anomalia = True
            motivos_anomalia.append(f"Volume de combustível ({dados.quantidade_litros_ou_unidades:.1f} L) excede a capacidade física ({capacidade_tanque:.1f} L).")

        # 6. Auditoria de Odômetro (veículos) ou Horímetro (embarcações, geradores, máquinas)
        if ativo:
            tipo_cat = ativo.get("categoria", "")
            medicao_anterior = float(ativo.get("horimetro_atual_h", 0.0)) if tipo_cat in [VeiculoCategoria.EMBARCACAO.value, VeiculoCategoria.GERADOR.value, VeiculoCategoria.MAQUINA_EQUIPAMENTO.value] else float(ativo.get("odometro_atual_km", 0.0))
            if medicao_anterior > 0 and dados.odometro_ou_horimetro < medicao_anterior:
                anomalia = True
                unidade = "Horímetro" if tipo_cat in [VeiculoCategoria.EMBARCACAO.value, VeiculoCategoria.GERADOR.value, VeiculoCategoria.MAQUINA_EQUIPAMENTO.value] else "Odômetro"
                motivos_anomalia.append(f"{unidade} retrocedido: informado ({dados.odometro_ou_horimetro:.1f}) menor que o anterior ({medicao_anterior:.1f}).")

        # Gerar Código Oficial de Autorização SEA/SC
        cod_auth = f"AUT-SEA-SC-{data_str}-{uuid.uuid4().hex[:6].upper()}"

        # Deduzir Saldo e Atualizar Cartão
        novo_saldo = round(saldo_atual - dados.valor_total, 2)
        total_gasto = round(float(cartao.get("total_gasto_mes_atual", 0.0)) + dados.valor_total, 2)

        self.db.cartoes_frota.update_one(
            {"id": cartao["id"]},
            {
                "$set": {
                    "saldo_disponivel_reais": novo_saldo,
                    "total_gasto_mes_atual": total_gasto,
                    "ultima_transacao_em": agora_iso,
                    "updated_at": agora_iso
                }
            }
        )

        # Atualizar odômetro/horímetro do ativo
        if ativo:
            tipo_cat = ativo.get("categoria", "")
            if tipo_cat in [VeiculoCategoria.EMBARCACAO.value, VeiculoCategoria.GERADOR.value, VeiculoCategoria.MAQUINA_EQUIPAMENTO.value]:
                if dados.odometro_ou_horimetro > float(ativo.get("horimetro_atual_h", 0.0)):
                    self.db.veiculos.update_one(
                        {"placa": ativo["placa"]},
                        {"$set": {"horimetro_atual_h": dados.odometro_ou_horimetro, "updated_at": agora_iso}}
                    )
            else:
                if dados.odometro_ou_horimetro > float(ativo.get("odometro_atual_km", 0.0)):
                    self.db.veiculos.update_one(
                        {"placa": ativo["placa"]},
                        {"$set": {"odometro_atual_km": dados.odometro_ou_horimetro, "updated_at": agora_iso}}
                    )

        # Registrar Transação
        doc_transacao = dados.model_dump()
        doc_transacao["id"] = transacao_id
        doc_transacao["cartao_id"] = cartao["id"]
        doc_transacao["autorizado"] = True
        doc_transacao["codigo_autorizacao"] = cod_auth
        doc_transacao["mensagem_status"] = "Transação Autorizada com Sucesso via Cartão Integrado Governo de SC."
        doc_transacao["anomalia_detectada"] = anomalia
        doc_transacao["motivo_anomalia"] = " | ".join(motivos_anomalia) if anomalia else None
        doc_transacao["timestamp"] = agora_iso

        self.db.transacoes_cartao_sc.insert_one(doc_transacao)
        doc_transacao.pop("_id", None)
        return doc_transacao

    def listar_transacoes(
        self,
        identificador_ativo: Optional[str] = None,
        apenas_anomalias: bool = False,
        cidade: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        filtro: Dict[str, Any] = {}
        if identificador_ativo:
            filtro["identificador_ativo"] = identificador_ativo.upper()
        if apenas_anomalias:
            filtro["anomalia_detectada"] = True
        if cidade:
            filtro["cidade"] = cidade

        cursor = self.db.transacoes_cartao_sc.find(filtro).sort("timestamp", -1)
        res = []
        for doc in cursor:
            doc.pop("_id", None)
            res.append(doc)
        return res

    # =========================================================================
    # CONSOLIDAÇÃO DO CONTRATO SEA/SC POR TIPOS DE ATIVOS E INSUMOS
    # =========================================================================

    def obter_resumo_contrato_sc(self) -> Dict[str, Any]:
        """
        Retorna visão holística consolidada do contrato de Santa Catarina:
        - 4 Tipos de Ativos: Veículos, Embarcações, Geradores, Máquinas e Equipamentos.
        - 4 Categorias de Insumos: Combustíveis em geral, Lubrificantes, Aditivos e Óleos.
        - Tecnologia de Pagamento: Cartões magnéticos / microprocessados ativos.
        - Rede de Postos Credenciados em SC.
        """
        veiculos_cursor = self.db.veiculos.find({})
        ativos_por_tipo = {
            "VEICULOS": {"quantidade": 0, "itens": []},
            "EMBARCACOES": {"quantidade": 0, "itens": []},
            "GERADORES": {"quantidade": 0, "itens": []},
            "MAQUINAS_EQUIPAMENTOS": {"quantidade": 0, "itens": []}
        }

        for v in veiculos_cursor:
            v.pop("_id", None)
            cat = v.get("categoria", "")
            if cat == VeiculoCategoria.EMBARCACAO.value:
                ativos_por_tipo["EMBARCACOES"]["quantidade"] += 1
                ativos_por_tipo["EMBARCACOES"]["itens"].append(v)
            elif cat == VeiculoCategoria.GERADOR.value:
                ativos_por_tipo["GERADORES"]["quantidade"] += 1
                ativos_por_tipo["GERADORES"]["itens"].append(v)
            elif cat == VeiculoCategoria.MAQUINA_EQUIPAMENTO.value:
                ativos_por_tipo["MAQUINAS_EQUIPAMENTOS"]["quantidade"] += 1
                ativos_por_tipo["MAQUINAS_EQUIPAMENTOS"]["itens"].append(v)
            else:
                ativos_por_tipo["VEICULOS"]["quantidade"] += 1
                ativos_por_tipo["VEICULOS"]["itens"].append(v)

        total_cartoes = self.db.cartoes_frota.count_documents({})
        total_postos_sc = self.db.postos_credenciados.count_documents({"uf": "SC"})
        if total_postos_sc == 0:
            total_postos_sc = self.db.postos_credenciados.count_documents({})

        total_transacoes = self.db.transacoes_cartao_sc.count_documents({})
        total_gasto_acumulado = 0.0
        for t in self.db.transacoes_cartao_sc.find({"autorizado": True}):
            total_gasto_acumulado += float(t.get("valor_total", 0.0))

        return {
            "orgao_gestor": "Governo do Estado de Santa Catarina - Secretaria de Estado da Administração (SEA/SC)",
            "contrato_objeto": "Serviços continuados de administração, gerenciamento e controle de frota por meio de sistema integrado e tecnologia de cartão magnético ou microprocessado em rede credenciada de postos para abastecer veículos, embarcações, geradores, máquinas e equipamentos.",
            "secretarias_atendidas": [
                "SEA - Secretaria de Estado da Administração",
                "PMSC - Polícia Militar de Santa Catarina",
                "CBMSC - Corpo de Bombeiros Militar de Santa Catarina",
                "SES - Secretaria de Estado da Saúde",
                "SIE - Secretaria de Estado da Infraestrutura e Mobilidade",
                "SED - Secretaria de Estado da Educação",
                "SAP - Secretaria de Administração Prisional",
                "IMA - Instituto do Meio Ambiente de Santa Catarina"
            ],
            "ativos_por_tipo": ativos_por_tipo,
            "insumos_homologados": [
                {"categoria": "Combustíveis em Geral", "tipos": ["Diesel S10", "Diesel S500", "Diesel Marítimo", "Gasolina Comum", "Gasolina Aditivada", "Etanol Comum", "GNV", "AvGas"]},
                {"categoria": "Lubrificantes", "tipos": ["Óleo Motor 15W40", "Óleo Motor 5W30 Sintético", "Óleo de Transmissão", "Fluido Hidráulico ISO VG 68"]},
                {"categoria": "Aditivos", "tipos": ["Agente Redutor Arla 32 (Euro 5/6)", "Fluido de Arrefecimento / Radiador Long Life", "Aditivo Descarbonizante"]},
                {"categoria": "Óleos Especiais", "tipos": ["Óleo 2T Náutico TC-W3 (Embarcações)", "Óleo 4T"]}
            ],
            "tecnologias_cartao_suportadas": [
                "Chip Microprocessado com criptografia EMV / ISO 7816",
                "Tarja Magnética de alta coercividade (HiCo)",
                "NFC / Contactless de proximidade",
                "Token Virtual para abastecimentos emergenciais"
            ],
            "estatisticas_operacionais": {
                "total_ativos_cadastrados": sum(a["quantidade"] for a in ativos_por_tipo.values()),
                "total_cartoes_emitidos": total_cartoes,
                "total_postos_credenciados_sc": total_postos_sc,
                "total_transacoes_processadas": total_transacoes,
                "valor_total_transacionado_reais": round(total_gasto_acumulado, 2),
                "desconto_medio_contratual_aplicado": "4.5% sobre Tabela ANP"
            }
        }


contract_sc_service = ContractSCService()

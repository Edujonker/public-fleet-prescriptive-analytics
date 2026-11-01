"""
Rotas para Gestão do Contrato do Governo do Estado de Santa Catarina (SEA/SC)
e Auditoria de Qualidade de Software ISO/IEC 25010.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.security.auth import RequireRole
from app.models.schemas import (
    UserRole,
    CartaoFrotaCreate,
    CartaoFrotaResponse,
    TransacaoCartaoCreate,
    TransacaoCartaoResponse,
    StatusCartao,
    ISO25010RelatorioCompleto
)
from app.services.contract_sc_service import contract_sc_service
from app.services.iso25010_service import iso25010_service

router = APIRouter(tags=["Governo SC & Qualidade ISO 25010"])


# =====================================================================
# ROTAS DO CONTRATO DE SANTA CATARINA (SEA/SC)
# =====================================================================

@router.get("/api/contract-sc/summary")
def get_contract_sc_summary():
    """
    Retorna o resumo consolidado do contrato do Governo do Estado de Santa Catarina:
    - 4 Tipos de Ativos: Veículos, Embarcações, Geradores, Máquinas e Equipamentos.
    - 4 Categorias de Insumos: Combustíveis em geral, Lubrificantes, Aditivos e Óleos.
    - Cartões Magnéticos / Microprocessados (chip).
    - Rede de postos credenciados e estatísticas de consumo.
    """
    return contract_sc_service.obter_resumo_contrato_sc()


@router.get("/api/contract-sc/cards", response_model=List[CartaoFrotaResponse])
def list_cards(
    secretaria: Optional[str] = None,
    tipo_cartao: Optional[str] = None,
    identificador_ativo: Optional[str] = None
):
    """Lista cartões magnéticos e microprocessados (chip) emitidos para a frota do Estado de SC."""
    return contract_sc_service.listar_cartoes(
        secretaria=secretaria,
        tipo_cartao=tipo_cartao,
        identificador_ativo=identificador_ativo
    )


@router.post("/api/contract-sc/cards", response_model=CartaoFrotaResponse, dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def create_card(dados: CartaoFrotaCreate):
    """Emite novo cartão magnético ou microprocessado para veículo, embarcação, gerador ou máquina."""
    return contract_sc_service.emitir_cartao(dados)


@router.patch("/api/contract-sc/cards/{cartao_id}/status", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def update_card_status(cartao_id: str, novo_status: StatusCartao, motivo: Optional[str] = None):
    """Bloqueia, desbloqueia ou cancela cartão de pagamento da frota."""
    res = contract_sc_service.alterar_status_cartao(cartao_id, novo_status, motivo=motivo)
    if not res:
        raise HTTPException(status_code=404, detail="Cartão não encontrado.")
    return res


@router.post("/api/contract-sc/cards/{cartao_id}/recharge", dependencies=[Depends(RequireRole([UserRole.ADMIN, UserRole.GESTOR_FROTA]))])
def recharge_card_quota(cartao_id: str, novo_saldo: float = Query(..., gt=0.0)):
    """Recarrega ou atualiza a cota orçamentária mensal do cartão da secretaria."""
    res = contract_sc_service.recarregar_cota_mensal(cartao_id, novo_saldo)
    if not res:
        raise HTTPException(status_code=404, detail="Cartão não encontrado.")
    return res


@router.post("/api/contract-sc/transactions", response_model=TransacaoCartaoResponse)
def authorize_transaction(dados: TransacaoCartaoCreate):
    """
    Processa e autoriza transação em rede de postos credenciados com cartão magnético/chip:
    - Validação de saldo da cota mensal da Secretaria
    - Validação do tipo de insumo (combustíveis, lubrificantes, aditivos Arla 32, óleos)
    - Validação física de reservatório / capacidade (antifraude)
    - Validação de odômetro (km) ou horímetro (h)
    """
    return contract_sc_service.autorizar_transacao(dados)


@router.get("/api/contract-sc/transactions")
def list_transactions(
    identificador_ativo: Optional[str] = None,
    apenas_anomalias: bool = False,
    cidade: Optional[str] = None
):
    """Lista transações em rede credenciada de postos do Estado de SC com auditoria antifraude."""
    return contract_sc_service.listar_transacoes(
        identificador_ativo=identificador_ativo,
        apenas_anomalias=apenas_anomalias,
        cidade=cidade
    )


# =====================================================================
# ROTAS DE CONFORMIDADE ISO/IEC 25010 & NORMAS CORRELATAS
# =====================================================================

@router.get("/api/compliance/iso-25010", response_model=ISO25010RelatorioCompleto)
def get_iso25010_compliance_report():
    """
    Auditoria e Matriz de Qualidade de Software ISO/IEC 25010:
    Avaliação técnica em tempo real com notas e métricas de cada uma das 8 características:
    1. Adequação Funcional
    2. Eficiência de Performance
    3. Compatibilidade
    4. Usabilidade
    5. Confiabilidade
    6. Segurança (ISO 27001)
    7. Manutenibilidade
    8. Portabilidade
    E conformidade com ISO/IEC 12207, ISO/IEC 15504 (SPICE), ISO/IEC 29110 e ISO 9001 (8.3).
    """
    return iso25010_service.gerar_relatorio_qualidade_iso25010()


@router.get("/api/compliance/iso-9241-11")
def get_iso9241_ergonomics_report():
    """
    Auditoria Ergonômica e Usabilidade NBR ISO 9241-11:
    Avaliação da Tríade de Usabilidade (Eficácia, Eficiência e Satisfação)
    e Contexto de Uso no gerenciamento de frotas do Governo de Santa Catarina.
    """
    return iso25010_service.obter_metricas_ergonomia_iso9241()


@router.get("/api/compliance/security-practices")
def get_security_devsecops_practices():
    """
    Avaliação das 5 Principais Práticas de Segurança no Desenvolvimento (DevSecOps):
    1. Prevenção contra Injeção de Código (SQL/NoSQL)
    2. Princípio do Menor Privilégio (Least Privilege & RBAC)
    3. Proteção e Criptografia de Dados (At Rest / In Transit / LGPD)
    4. Isolamento de Infraestrutura e Rede (VPCs, Frontend Desacoplado, .env)
    5. Conformidade e Normas (LGPD Lei 13.709/2018, ISO/IEC 27001, OWASP Top 10)
    """
    return iso25010_service.obter_praticas_seguranca_devsecops()


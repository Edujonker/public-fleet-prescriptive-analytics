# -*- coding: utf-8 -*-
"""
================================================================================
ROTAS DO COPILOTO DE IA E PIPELINE METODOLÓGICO (PPGCAP/UDESC)
SECURITY-BY-DESIGN: FASTAPI PYDANTIC V2, INPUT BOUNDS E RBAC
================================================================================
"""

import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_db
from src.api.models import QueryRecord, AuditLog
from src.api.schemas import (
    ChatQueryRequest,
    ChatQueryResponse,
    PipelineUpdateRequest,
    PipelineUpdateResponse,
    ReportGenerateResponse,
    StatusResponse,
    CommercialSummaryResponse
)
from src.api.security import (
    get_current_user_dependency,
    RequireRole
)

logger = logging.getLogger("AssistantRouter")
router = APIRouter(prefix="/api", tags=["Copiloto de IA e Análises"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
PDF_PATH = BASE_DIR / "relatorios_pdf" / "relatorio_dissertacao_completo.pdf"

# Import seguro do motor de IA
try:
    from src.ai_assistant import FleetAIAssistant
    ai_engine = FleetAIAssistant()
except Exception as e:
    logger.error(f"Falha ao instanciar FleetAIAssistant no router: {e}")
    ai_engine = None


def _is_safe_path(target: Path, base: Path = BASE_DIR) -> bool:
    """Valida se o caminho canônico reside estritamente sob o diretório base autorizado (CWE-22)."""
    try:
        resolved = target.resolve()
        return resolved == base or base in resolved.parents
    except Exception:
        return False


@router.get("/status", response_model=StatusResponse, summary="Verificar integridade e status da API")
async def get_system_status():
    """Retorna o status operacional do servidor, motor de IA e relatórios."""
    return StatusResponse(
        servidor="Online (FastAPI Hardened)",
        versao="PPGCAP-2026-v3.0-Enterprise",
        ai_assistant="Ativo" if ai_engine else "Offline",
        total_consultas=ai_engine.memory.get("total_consultas", 0) if ai_engine else 0,
        pdf_existe=PDF_PATH.exists(),
        ambiente="Produção Acadêmica Segura"
    )


@router.post("/chat", response_model=ChatQueryResponse, summary="Processar consulta em linguagem natural")
async def chat_interaction(
    payload: ChatQueryRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Submete uma pergunta ao Copiloto de IA em linguagem natural.
    Recebe schema Pydantic v2 estrito e grava auditoria na base ORM.
    """
    if ai_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O motor de IA está temporariamente indisponível."
        )

    try:
        result = ai_engine.process_query(payload.mensagem)
        
        # Persiste histórico de auditoria via SQLAlchemy 2.0
        client_user = "anonimo_web"
        # Se houver cabeçalho de autorização, tenta extrair com segurança
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from src.api.config import get_settings
                from src.api.security import decode_access_token
                token_val = auth_header.split(" ")[1]
                dec = decode_access_token(token_val, get_settings())
                client_user = dec.get("sub", client_user)
            except Exception:
                pass

        record = QueryRecord(
            username=client_user,
            pergunta=payload.mensagem[:1000],
            categoria=result.get("categoria", "geral"),
            sucesso=result.get("sucesso", True)
        )
        db.add(record)
        await db.commit()

        return ChatQueryResponse(
            resposta=result.get("resposta", ""),
            categoria=result.get("categoria", "geral"),
            sucesso=result.get("sucesso", True),
            figura_relacionada=result.get("figura_relacionada"),
            topico=result.get("topico")
        )
    except Exception as e:
        logger.error(f"Erro ao processar consulta de chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu uma inconsistência interna ao analisar a sua consulta."
        )


@router.post("/atualizar-graficos", response_model=PipelineUpdateResponse, summary="Recalcular pipeline analítico com parâmetros estritos")
async def update_pipeline(
    params: PipelineUpdateRequest,
    current_user: dict = Depends(RequireRole(["admin", "auditor", "pesquisador"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Executa atualização segura do pipeline estatístico e regenera figuras.
    Operação protegida por RBAC (Requer autenticação com perfil de pesquisador ou superior).
    """
    if ai_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O motor de IA e pipeline está indisponível."
        )

    try:
        # Passa parâmetros validados e tipados pelo Pydantic v2
        dict_params = {
            "alpha": params.alpha,
            "frequencia": params.frequencia,
            "horizonte": params.horizonte,
            "modo_hipotese": params.modo_hipotese
        }
        res = ai_engine._action_update_pipeline(dict_params)

        db.add(AuditLog(
            username=current_user.get("sub", "desconhecido"),
            action="PIPELINE_EXECUTION",
            details=f"Pipeline atualizado com parâmetros: {dict_params}"
        ))
        await db.commit()

        return PipelineUpdateResponse(
            status=res.get("status", "concluido"),
            mensagem=res.get("resposta", "Pipeline estatístico recalculado com sucesso!"),
            parametros=dict_params
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha controlada ao executar o pipeline analítico."
        )


@router.post("/gerar-relatorio", response_model=ReportGenerateResponse, summary="Compilar relatório oficial de dissertação (WeasyPrint)")
async def generate_official_report(
    current_user: dict = Depends(RequireRole(["admin", "auditor"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Gera o relatório acadêmico oficial completo de 19MB com WeasyPrint.
    Operação crítica restrita a administradores e auditores.
    """
    if ai_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O motor de compilação está offline."
        )

    try:
        res = ai_engine._action_generate_pdf()
        size_mb = round(PDF_PATH.stat().st_size / (1024 * 1024), 2) if PDF_PATH.exists() else 0.0

        db.add(AuditLog(
            username=current_user.get("sub", "desconhecido"),
            action="PDF_GENERATION",
            details=f"Relatório gerado com sucesso ({size_mb} MB)"
        ))
        await db.commit()

        return ReportGenerateResponse(
            status=res.get("status", "concluido"),
            mensagem=res.get("resposta", "Relatório PDF acadêmico gerado com sucesso!"),
            caminho_relatorio="/api/relatorio/download",
            tamanho_mb=size_mb
        )
    except Exception as e:
        logger.error(f"Erro ao compilar relatório PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha controlada durante a compilação do documento PDF."
        )


@router.get("/relatorio/download", summary="Download seguro do PDF da dissertação")
async def download_report_pdf():
    """Download do PDF da dissertação com validação de caminho contra Path Traversal (CWE-22)."""
    if not _is_safe_path(PDF_PATH) or not PDF_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O arquivo do relatório oficial ainda não foi compilado."
        )

    return FileResponse(
        path=PDF_PATH,
        filename="relatorio_dissertacao_completo.pdf",
        media_type="application/pdf"
    )


@router.get("/comercial/resumo", response_model=CommercialSummaryResponse, summary="Indicadores Comerciais e TCO de Gestão de Frotas")
async def get_commercial_summary():
    """Retorna os KPIs comerciais consolidados para tomada de decisão no setor de transporte."""
    json_path = BASE_DIR / "relatorios" / "analises_comerciais_frota.json"
    if not json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="As análises comerciais ainda não foram processadas."
        )

    import json
    with open(json_path, "r", encoding="utf-8") as f:
        com_data = json.load(f)

    res = com_data.get("resumo_executivo", {})
    ren = com_data.get("renovacao_frota", {})
    top_item = com_data.get("curva_abc", {}).get("top_15_itens", [{}])[0].get("item", "PNEU")

    return CommercialSummaryResponse(
        total_gasto_auditado=res.get("total_gasto_auditado", 0.0),
        total_ordens_servico=res.get("total_ordens_servico", 0),
        total_veiculos_unicos=res.get("total_veiculos_unicos", 0),
        percentual_corretivas=res.get("percentual_corretivas", 99.998),
        percentual_pecas_custo=res.get("percentual_pecas_custo", 69.18),
        economia_potencial_procurement_anual=res.get("economia_potencial_procurement_anual", 0.0),
        ponto_otimo_renovacao_anos=ren.get("ponto_otimo_renovacao_anos", 6),
        quilometragem_troca_km=ren.get("quilometragem_equivalente_km", 130000),
        top_item_pareto=top_item,
        economia_prescritiva_milp=res.get("economia_potencial_preditiva_milp", 380000.0)
    )


@router.get("/comercial/detalhes", summary="Dados completos das análises comerciais e de transporte")
async def get_commercial_details():
    """Retorna o payload completo da auditoria comercial (Pareto ABC, TCO, CPK, Ciclo de Vida e ROI)."""
    json_path = BASE_DIR / "relatorios" / "analises_comerciais_frota.json"
    if not json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="As análises comerciais ainda não foram processadas."
        )

    import json
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


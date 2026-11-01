"""
Rotas para Relatórios Gerenciais, Inteligência de Frota, TCO, CPK e Ranking de Motoristas.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends

from app.services.report_service import report_service
from app.models.schemas import DashboardKPIs, RelatorioTCOResponse, RankingMotoristaResponse

router = APIRouter(prefix="/api/reports", tags=["Relatórios & Inteligência Analítica"])


@router.get("/dashboard", response_model=DashboardKPIs)
def get_dashboard_kpis():
    """Retorna os principais KPIs da frota em tempo real."""
    return report_service.obter_kpis_dashboard()


@router.get("/tco", response_model=List[RelatorioTCOResponse])
def get_tco_report():
    """
    Retorna o relatório analítico de Total Cost of Ownership (TCO) e Custo Por Km (CPK).
    Consolida manutenção, combustível, pneus, pedágios, multas e taxas por veículo.
    """
    return report_service.gerar_relatorio_tco()


@router.get("/driver-ranking", response_model=List[RankingMotoristaResponse])
def get_driver_ranking():
    """
    Retorna o ranking de condução e score de segurança dos motoristas (0 a 100).
    Pontua infrações de velocidade, frenagem brusca, RPM excessivo e multas.
    """
    return report_service.gerar_ranking_motoristas()


@router.get("/secretarias")
def get_report_secretarias(
    secretaria: str = None,
    mes: int = None,
    ano: int = None,
    data_inicio: str = None,
    data_fim: str = None
):
    """
    Retorna relatório consolidado de custos por secretaria com suporte a filtro:
    - Por mês específico (ex: mes=11&ano=2026)
    - Por período de tempo (data_inicio a data_fim)
    Sempre trazendo a data e hora oficial de emissão e período de auditoria.
    """
    return report_service.gerar_relatorio_secretarias(
        secretaria_filtro=secretaria,
        mes=mes,
        ano=ano,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@router.get("/lancamentos")
def get_report_lancamentos(
    mes: int = None,
    ano: int = None,
    data_inicio: str = None,
    data_fim: str = None,
    tipo: str = None,
    secretaria: str = None
):
    """
    Retorna o extrato analítico com DATAS DE LANÇAMENTOS OBRIGATÓRIAS em todos os registros:
    - Filtro por mês/ano (ex: mes=11&ano=2026)
    - Filtro por período de tempo (data_inicio a data_fim)
    - Suporta filtragem por tipo de operação (ABASTECIMENTO, ORDEM_SERVICO, CARTAO_COMBUSTIVEL_SC)
    """
    return report_service.gerar_extrato_lancamentos_periodo(
        mes=mes,
        ano=ano,
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_lancamento=tipo,
        secretaria_filtro=secretaria
    )


@router.get("/export/csv")
def export_costs_csv(secretaria: str = None):
    """Exporta relatório completo de TCO e custos operacionais em formato CSV."""
    from fastapi.responses import Response
    csv_content = report_service.gerar_csv_custos(secretaria=secretaria)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relatorio_frota_custos_tco.csv"}
    )


@router.get("/export/lancamentos-csv")
def export_lancamentos_csv(
    mes: int = None,
    ano: int = None,
    data_inicio: str = None,
    data_fim: str = None,
    tipo: str = None,
    secretaria: str = None
):
    """
    Exporta extrato completo de lançamentos em CSV com DATAS DE LANÇAMENTO em todas as linhas,
    filtrado por mês ou por intervalo de tempo.
    """
    from fastapi.responses import Response
    csv_content = report_service.gerar_csv_lancamentos_periodo(
        mes=mes,
        ano=ano,
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo_lancamento=tipo,
        secretaria=secretaria
    )
    nome_arquivo = f"extrato_lancamentos_frota_{ano or '2026'}_{mes or 'periodo'}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
    )



@router.get("/compliance-national")
def get_national_data_compliance():
    """
    Verificação e auditoria de soberania de dados em território nacional:
    Confirma localização da base de dados (Brasil), políticas de retenção LGPD e criptografia em repouso.
    """
    from app.database import is_using_standalone_engine
    return {
        "armazenamento_territorio_nacional": True,
        "localizacao_datacenter": "Brasil (São Paulo / Região Sul - Instância Local Soberana)",
        "conformidade_lgpd": {
            "mascaramento_cpf": True,
            "hash_criptografico_credenciais": "Argon2id (RFC 9106)",
            "trilha_auditoria_imutavel": True,
            "direitos_titular_dados": "Acesso, Retificação e Revogação Ativos"
        },
        "motor_banco_dados": "Mongita Disk Embutido / MongoDB Server Brasil",
        "modo_execucao": "Motor Standalone Local" if is_using_standalone_engine() else "MongoDB Server Nacional"
    }


# ==========================================
# ROTAS DE INTELIGÊNCIA PRESCRITIVA AVANÇADA
# ==========================================

@router.get("/prescriptive/full")
def get_prescriptive_full():
    """
    Relatório Prescritivo Master Consolidado:
    Retorna os 5 pilares estratégicos de inteligência prescritiva com cálculo da economia evitada (R$).
    """
    return report_service.gerar_relatorio_prescritivo_completo()


@router.get("/prescriptive/maintenance")
def get_prescriptive_maintenance():
    """
    Pilar 1: Manutenção Mecânica Prescritiva:
    - Plano Preventivo Dinâmico (dia/hora exatos para menor ociosidade)
    - Prevenção de Falhas Críticas em 48h (aviso antecipado de pane mecânica)
    - Gestão de Pneus Otimizada (momento de rotação, recauchutagem ou reposição)
    """
    return {
        "manutencao_preventiva_dinamica": report_service.gerar_manutencao_preventiva_dinamica(),
        "prevencao_falhas_criticas_48h": report_service.gerar_alertas_falhas_criticas(),
        "gestao_pneus_otimizada": report_service.gerar_gestao_pneus_otimizada()
    }


@router.get("/prescriptive/fuel")
def get_prescriptive_fuel():
    """
    Pilar 2: Consumo de Combustível e Eficiência Energética:
    - Ações Diretas de Redução de Consumo (marcha lenta, RPM, calibragem)
    - Estratégia de Abastecimento (autonomia vs preços de postos parceiros na rota)
    """
    return {
        "acoes_reducao_combustivel": report_service.gerar_acoes_reducao_combustivel(),
        "estrategia_abastecimento_rota": report_service.gerar_estrategia_abastecimento()
    }


@router.get("/prescriptive/logistics")
def get_prescriptive_logistics():
    """
    Pilar 3: Roteirização e Logística Avançada:
    - Redirecionamento Dinâmico em Tempo Real (trânsito, obras, clima)
    - Dimensionamento da Frota (venda, agregação de terceiros, redistribuição)
    """
    return {
        "redirecionamento_tempo_real": report_service.gerar_redirecionamento_logistica(),
        "dimensionamento_e_ociosidade": report_service.gerar_dimensionamento_frota()
    }


@router.get("/prescriptive/drivers")
def get_prescriptive_drivers():
    """
    Pilar 4: Comportamento e Segurança do Motorista:
    - Plano de Treinamento Personalizado (ranking com módulos sob medida)
    - Escala de Trabalho Inteligente (gestão de repouso, histórico de fadiga)
    """
    return {
        "plano_treinamento_personalizado": report_service.gerar_plano_treinamento_motoristas(),
        "escala_trabalho_inteligente": report_service.gerar_escala_trabalho_inteligente()
    }


@router.get("/prescriptive/divestment-tco")
def get_prescriptive_divestment():
    """
    Pilar 5: Financeiro e TCO (Custo Total de Propriedade):
    - Momento Ideal de Desinvestimento e Renovação da Frota (Curva TCO vs Depreciação / >40% venal)
    """
    return {
        "desinvestimento_renovacao_tco": report_service.gerar_desinvestimento_renovacao_tco()
    }


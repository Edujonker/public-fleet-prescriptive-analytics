"""
Ponto de Entrada Principal da Aplicação FastAPI - Sistema de Gestão de Frotas.
Segue estritamente Security-by-Design (OWASP Top 10 e CWE), middlewares de proteção e cabeçalhos HTTP rigorosos.
"""

from contextlib import asynccontextmanager
from pathlib import Path
import logging
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.database import init_db
from app.seed_data import seed_database_if_empty
from app.routes import (
    auth_router,
    assets_router,
    telemetry_router,
    maintenance_router,
    fuel_router,
    trip_router,
    compliance_router,
    report_router,
    ai_router,
    contract_sc_router
)

# Configuração de Log Seguro
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("FleetManagementApp")


# =====================================================================
# MIDDLEWARES DE SEGURANÇA (SECURITY-BY-DESIGN)
# =====================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Aplica cabeçalhos HTTP de segurança recomendados pela OWASP."""
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: blob: https://*.tile.openstreetmap.org https://unpkg.com; "
            "connect-src 'self' ws:;"
        )
        return response


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    """Protege contra ataques de negação de serviço (DoS) por payloads excessivos."""
    def __init__(self, app, max_upload_size: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next: Callable):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_upload_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": "Payload da requisição excede o limite máximo permitido de 10MB."}
                    )
            except ValueError:
                pass
        return await call_next(request)


# =====================================================================
# LIFESPAN (INICIALIZAÇÃO E ENCERRAMENTO)
# =====================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização segura do banco de dados e seed data."""
    logger.info("Iniciando Sistema de Gestão de Frotas...")
    init_db()
    seed_database_if_empty()
    logger.info("Banco de dados pronto e dados de demonstração validados.")
    yield
    logger.info("Encerrando Sistema de Gestão de Frotas.")


# =====================================================================
# INSTÂNCIA FASTAPI
# =====================================================================

settings = get_settings()

app = FastAPI(
    title="Sistema Integrado de Gestão de Frotas & Telemetria IoT",
    description="Plataforma corporativa de controle de ativos, rastreamento em tempo real, manutenção preventiva, telemetria e compliance legal.",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Adicionar Middlewares de Segurança
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=settings.MAX_CONTENT_LENGTH)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# =====================================================================
# HANDLERS GLOBAIS DE ERRO (PREVENÇÃO DE VAZAMENTO DE INFORMAÇÕES)
# =====================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc not in ["body", "query"])
        errors.append({"campo": field, "mensagem": err["msg"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Falha de validação dos campos da requisição.", "erros": errors}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro interno não tratado na rota {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocorreu um erro interno no servidor. A equipe de segurança foi notificada."}
    )


# =====================================================================
# ROTAS DA API REST
# =====================================================================

app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(telemetry_router)
app.include_router(maintenance_router)
app.include_router(fuel_router)
app.include_router(trip_router)
app.include_router(compliance_router)
app.include_router(report_router)
app.include_router(ai_router)
app.include_router(contract_sc_router)


@app.get("/api/health", tags=["Monitoramento"])
def health_check():
    """Endpoint de liveness/readiness para balanceadores e orquestradores."""
    return {
        "status": "healthy",
        "service": "sistema-gestao-frotas",
        "version": "2.0.0",
        "database": "mongodb_mongita_resilient",
        "port": settings.PORT
    }


# =====================================================================
# ROTAS DE DASHBOARDS, RELATÓRIOS E INTEGRAÇÃO ANALÍTICA
# =====================================================================

from fastapi.responses import FileResponse

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
DASHBOARD_DIR = ROOT_DIR / "dashboard"
PDF_DIR = ROOT_DIR / "relatorios_pdf"
REL_DIR = ROOT_DIR / "relatorios"
SIC_DIR = ROOT_DIR / "SIC"

@app.get("/anomalias", tags=["Dashboards"])
@app.get("/anomalias.html", tags=["Dashboards"])
def serve_anomalias():
    """Painel Executivo de Triagem de Anomalias de Manutenção e Combustíveis."""
    anom_file = FRONTEND_DIR / "anomalias.html"
    if not anom_file.exists():
        anom_file = DASHBOARD_DIR / "anomalias.html"
    return FileResponse(str(anom_file))

@app.get("/dashboard", tags=["Dashboards"])
@app.get("/dashboard/", tags=["Dashboards"])
def serve_dashboard_root():
    """Painel Analítico de Frotas."""
    dash_index = DASHBOARD_DIR / "index.html"
    if dash_index.exists():
        return FileResponse(str(dash_index))
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/dashboard/anomalias", tags=["Dashboards"])
def serve_dashboard_anomalias():
    return FileResponse(str(DASHBOARD_DIR / "anomalias.html"))

@app.get("/dashboard/abastecimentos", tags=["Dashboards"])
def serve_dashboard_abastecimentos():
    return FileResponse(str(DASHBOARD_DIR / "relatorio_interativo_abastecimentos.html"))

@app.get("/slides", tags=["Dashboards"])
def serve_slides_sic():
    return FileResponse(str(SIC_DIR / "apresentacao_slides_sic.html"))

@app.get("/teste", tags=["Dashboards"])
@app.get("/teste-sistema", tags=["Dashboards"])
@app.get("/simulador", tags=["Dashboards"])
@app.get("/teste_frota.html", tags=["Dashboards"])
def serve_teste_frota():
    """Ambiente Gráfico Interativo de Testes e Simulação da Frota no Navegador."""
    test_file = FRONTEND_DIR / "teste_frota.html"
    if not test_file.exists():
        test_file = DASHBOARD_DIR / "teste_frota.html"
    return FileResponse(str(test_file))

@app.get("/api/anomalias", tags=["Relatórios"])
def get_anomalias_data():
    """Retorna a base analítica consolidada de anomalias (JSON)."""
    json_path = DASHBOARD_DIR / "data" / "anomalias_data.json"
    if json_path.exists():
        return FileResponse(str(json_path), media_type="application/json")
    json_sec = REL_DIR / "relatorio_anomalias_por_secretaria.json"
    if json_sec.exists():
        return FileResponse(str(json_sec), media_type="application/json")
    return {"detail": "Base de anomalias ainda não gerada"}

@app.get("/api/relatorio-anomalias", tags=["Relatórios"])
def get_relatorio_anomalias_sec():
    """Retorna o resumo gerencial de anomalias agrupado por secretaria."""
    json_path = REL_DIR / "relatorio_anomalias_por_secretaria.json"
    if json_path.exists():
        return FileResponse(str(json_path), media_type="application/json")
    return {"detail": "Relatório de secretarias não encontrado"}

CHARTS_DIR = ROOT_DIR / "charts"

if PDF_DIR.exists():
    app.mount("/relatorios_pdf", StaticFiles(directory=str(PDF_DIR)), name="relatorios_pdf")

if REL_DIR.exists():
    app.mount("/relatorios", StaticFiles(directory=str(REL_DIR)), name="relatorios")

if CHARTS_DIR.exists():
    app.mount("/charts", StaticFiles(directory=str(CHARTS_DIR)), name="charts")

if (DASHBOARD_DIR / "data").exists():
    app.mount("/data", StaticFiles(directory=str(DASHBOARD_DIR / "data")), name="data_root")
    app.mount("/dashboard/data", StaticFiles(directory=str(DASHBOARD_DIR / "data")), name="dashboard_data")

if (DASHBOARD_DIR / "css").exists():
    app.mount("/dashboard/css", StaticFiles(directory=str(DASHBOARD_DIR / "css")), name="dashboard_css")

if (DASHBOARD_DIR / "js").exists():
    app.mount("/dashboard/js", StaticFiles(directory=str(DASHBOARD_DIR / "js")), name="dashboard_js")

@app.get("/dashboard/style.css", tags=["Dashboards"])
def get_dashboard_css():
    css_file = DASHBOARD_DIR / "style.css"
    if css_file.exists():
        return FileResponse(str(css_file), media_type="text/css")
    return JSONResponse(status_code=404, content={"detail": "style.css not found"})

@app.get("/dashboard/app.js", tags=["Dashboards"])
def get_dashboard_js():
    js_file = DASHBOARD_DIR / "app.js"
    if js_file.exists():
        return FileResponse(str(js_file), media_type="application/javascript")
    return JSONResponse(status_code=404, content={"detail": "app.js not found"})

if DASHBOARD_DIR.exists():
    app.mount("/dashboard_files", StaticFiles(directory=str(DASHBOARD_DIR)), name="dashboard_files")

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")



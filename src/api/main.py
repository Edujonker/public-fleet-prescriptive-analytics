# -*- coding: utf-8 -*-
"""
================================================================================
APLICAÇÃO FASTAPI PRINCIPAL - ENTERPRISE SECURITY (PPGCAP/UDESC)
SECURITY-BY-DESIGN: FASTAPI, PYDANTIC V2, MIDDLEWARES & ERROR HANDLING
================================================================================
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.config import get_settings
from src.api.database import init_db
from src.api.middlewares import SecurityHeadersMiddleware, LimitUploadSizeMiddleware
from src.api.routes import auth, assistant

# Configuração de Logs Estruturados Sanitizados (CWE-117)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [FastAPISecure] %(message)s"
)
logger = logging.getLogger("FastAPISecure")

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida assíncrono: inicializa banco de dados e sementes seguras."""
    logger.info("Inicializando infraestrutura segura da API...")
    await init_db()
    logger.info("Banco de dados ORM e usuários administrativos prontos.")
    yield
    logger.info("Encerrando serviços de forma graciosa...")


# Instância Principal do FastAPI com Metadados Acadêmicos
app = FastAPI(
    title="Plataforma de Analítica e Copiloto de IA - Gestão de Frotas",
    description=(
        "API RESTful de Alta Segurança (Security-by-Design) desenvolvida para o PPGCAP/UDESC. "
        "Em conformidade estrita com OWASP Top 10, CWE e premissas de modelagem preditiva/prescritiva."
    ),
    version="3.0.0-SecurityHardened",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ------------------------------------------------------------------------------
# 1. MIDDLEWARES DE SEGURANÇA (OWASP A05 & CWE-400)
# ------------------------------------------------------------------------------

# Headers de Proteção HTTP (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)
app.add_middleware(SecurityHeadersMiddleware)

# Limite anti-DoS de Payload HTTP (Max 1MB)
app.add_middleware(LimitUploadSizeMiddleware)

# Configuração Restrita de CORS (CWE-942: NUNCA usar ['*'] em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
    max_age=600
)

# ------------------------------------------------------------------------------
# 2. TRATAMENTO SEGURO DE ERROS E EXCEÇÕES (CWE-209: DATA LEAKAGE PREVENTION)
# ------------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Tratador uniforme para exceções HTTP controladas."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
        headers=getattr(exc, "headers", None)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Sanitiza erros de validação do Pydantic v2.
    Informa os campos incorretos sem expor detalhes internos ou caminhos de arquivos.
    """
    errors = []
    for err in exc.errors():
        field_loc = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "campo": field_loc,
            "motivo": err.get("msg", "Valor inválido")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "validation_error",
            "message": "Falha na validação estrita dos dados fornecidos.",
            "erros": errors
        }
    )


@app.exception_handler(Exception)
async def global_uncaught_exception_handler(request: Request, exc: Exception):
    """
    Captura global de exceções não tratadas (CWE-209).
    NUNCA expõe stack traces, queries SQL ou variáveis internas ao cliente.
    """
    logger.critical(f"Exceção não tratada capturada: {type(exc).__name__}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Ocorreu um erro interno no servidor. O incidente foi registrado para auditoria."
        }
    )

# ------------------------------------------------------------------------------
# 3. REGISTRO DE ROTAS E ENDPOINTS
# ------------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(assistant.router)

# Redirecionamento da raiz para o Dashboard
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/dashboard/")

# ------------------------------------------------------------------------------
# 4. ARQUIVOS ESTÁTICOS PROTEGIDOS CONTRA PATH TRAVERSAL (CWE-22)
# ------------------------------------------------------------------------------

def _mount_if_exists(url_path: str, local_dir: Path, name: str):
    if local_dir.exists() and local_dir.is_dir():
        app.mount(url_path, StaticFiles(directory=str(local_dir), html=True), name=name)

_mount_if_exists("/dashboard", BASE_DIR / "dashboard", "dashboard")
_mount_if_exists("/charts", BASE_DIR / "charts", "charts")
_mount_if_exists("/graficos", BASE_DIR / "graficos", "graficos")
_mount_if_exists("/relatorios_pdf", BASE_DIR / "relatorios_pdf", "relatorios_pdf")

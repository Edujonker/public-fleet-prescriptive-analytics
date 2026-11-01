"""
Módulo de rotas da API do Sistema de Gestão de Frotas.
"""

from .auth_routes import router as auth_router
from .assets_routes import router as assets_router
from .telemetry_routes import router as telemetry_router
from .maintenance_routes import router as maintenance_router
from .fuel_routes import router as fuel_router
from .trip_routes import router as trip_router
from .compliance_routes import router as compliance_router
from .report_routes import router as report_router
from .ai_routes import router as ai_router
from .contract_sc_routes import router as contract_sc_router

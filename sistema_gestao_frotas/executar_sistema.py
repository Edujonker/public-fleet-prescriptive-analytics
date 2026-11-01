#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT INICIALIZADOR - SISTEMA INTEGRADO DE GESTÃO DE FROTAS & TELEMETRIA IOT
Execução Standalone compatível com Linux e Windows (Porta 8090).
================================================================================
"""

import sys
import os
from pathlib import Path

# Adiciona o backend ao PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import uvicorn
from app.config import get_settings
from app.database import init_db, is_using_standalone_engine
from app.seed_data import seed_database_if_empty

BANNER = """
==============================================================================
   🚛 FROTASAAS ENTERPRISE 2.0 - SISTEMA DE GESTÃO DE FROTAS & TELEMETRIA IOT
   Compatível com Linux & Windows | Persistência MongoDB Resiliente
==============================================================================
   🌐 Acesso Web:        http://localhost:{port}
   📚 API Docs (Swagger): http://localhost:{port}/api/docs
   📄 OpenAPI JSON:       http://localhost:{port}/api/openapi.json
   
   👤 Usuários de Acesso Padrão:
      • Admin:    admin    / Admin@Fleet2026!   (Acesso Total & Segurança)
      • Gestor:   gestor   / Gestor@Fleet2026!  (Aprovações & Relatórios)
      • Operador: operador / Operador@Fleet2026! (Despacho & Abastecimento)
      • Motorista: motorista / Motorista@Fleet2026! (Checklist Digital)
      
   🔑 Chave de API IoT Gateway:
      • Header:   X-API-Key: flt_gateway_iot_live_sim_2026_seckey
      
   💾 Base de Dados: {engine_status}
==============================================================================
"""

def main():
    settings = get_settings()
    
    # Inicialização do banco e dados
    print("Inicializando banco de dados...")
    init_db()
    seed_database_if_empty()
    
    engine_desc = "Mongita Embutido Standalone em Disco (dados/mongodb_data)" if is_using_standalone_engine() else "MongoDB Server Ativo"
    print(BANNER.format(port=settings.PORT, engine_status=engine_desc))
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()

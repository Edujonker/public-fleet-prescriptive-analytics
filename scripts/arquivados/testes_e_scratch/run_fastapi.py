#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
INICIALIZADOR DO SERVIDOR FASTAPI ENTERPRISE SECURITY (PPGCAP/UDESC)
================================================================================
"""

import sys
import os
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)

if __name__ == "__main__":
    print("=" * 80)
    print(" INICIANDO FASTAPI SECURITY-BY-DESIGN SERVER (PPGCAP/UDESC)")
    print(" Documentação Swagger OpenAPI: http://localhost:8080/docs")
    print(" Dashboard Analítico:         http://localhost:8080/dashboard/")
    print(" Status da API:               http://localhost:8080/api/status")
    print("=" * 80)

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        server_header=False,
        date_header=False,
        access_log=True
    )

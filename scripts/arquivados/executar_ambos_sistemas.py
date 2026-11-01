#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
INICIALIZADOR UNIFICADO - AMBOS OS SISTEMAS EM PARALELO (PORTAS 8080 E 8090)
PPGCAP / UDESC - DISSERTAÇÃO & SISTEMA CORPORATIVO DE GESTÃO DE FROTAS
================================================================================
Sistema 1: FrotaSaaS Enterprise 2.0 (Gestão de Frotas & Telemetria IoT) -> Porta 8090
Sistema 2: Dashboard de IA & Análise Preditiva/Prescritiva da Dissertação -> Porta 8080
================================================================================
"""

import sys
import os
import time
import signal
import subprocess
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Caminho para o Python do ambiente virtual se existir, senão o interpretador atual
VENV_PYTHON = BASE_DIR / ".venv" / "bin" / "python3"
if not VENV_PYTHON.exists():
    VENV_PYTHON = BASE_DIR / ".venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    PYTHON_CMD = sys.executable
else:
    PYTHON_CMD = str(VENV_PYTHON)

BANNER = r"""
================================================================================
   🚀 PPGCAP/UDESC - INICIALIZADOR UNIFICADO DE ECOSSISTEMAS DE FROTAS
================================================================================
   Sistema 1: FrotaSaaS Enterprise (Gestão de Frotas & IoT)  -> http://localhost:8090/
   Sistema 2: Dashboard de IA Preditiva da Dissertação       -> http://localhost:8080/dashboard/
================================================================================
"""

proc_fleet = None
proc_dissertation = None


def encerrar_processos(sig=None, frame=None):
    """Encerra os subprocessos de forma graciosa ao receber SIGINT/SIGTERM."""
    print("\n🛑 Encerrando ambos os sistemas de forma segura...")
    for proc, nome in [(proc_fleet, "FrotaSaaS 8090"), (proc_dissertation, "Dashboard 8080")]:
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
    print("✅ Ambos os sistemas foram finalizados. Até logo!")
    sys.exit(0)


def testar_url(url: str, max_tentativas: int = 15) -> bool:
    """Verifica se a URL HTTP está respondendo com código 200."""
    for _ in range(max_tentativas):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'FleetHealthChecker/1.0'})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status in (200, 301, 302):
                    return True
        except Exception:
            time.sleep(0.8)
    return False


def main():
    global proc_fleet, proc_dissertation
    print(BANNER)
    signal.signal(signal.SIGINT, encerrar_processos)
    signal.signal(signal.SIGTERM, encerrar_processos)

    # 1. Iniciar Sistema 1: FrotaSaaS Enterprise (Porta 8090)
    print("▶️ [1/2] Iniciando FrotaSaaS Enterprise 2.0 (FastAPI / IoT) na porta 8090...")
    cmd_fleet = [PYTHON_CMD, str(BASE_DIR / "sistema_gestao_frotas" / "executar_sistema.py")]
    proc_fleet = subprocess.Popen(cmd_fleet, cwd=str(BASE_DIR))

    # 2. Iniciar Sistema 2: Dashboard da Dissertação (Porta 8080)
    print("▶️ [2/2] Iniciando Dashboard Preditivo da Dissertação na porta 8080...")
    cmd_dissertation = [PYTHON_CMD, str(BASE_DIR / "run_dashboard.py")]
    proc_dissertation = subprocess.Popen(cmd_dissertation, cwd=str(BASE_DIR))

    print("\n⏳ Aguardando subida dos serviços e validação de saúde de rede...")
    
    fleet_ok = testar_url("http://localhost:8090/health")
    dissertation_ok = testar_url("http://localhost:8080/dashboard/")

    print("\n" + "=" * 80)
    if fleet_ok:
        print("  ✅ [PORTA 8090] FrotaSaaS Enterprise ATIVO:")
        print("     • Interface Web SPA : http://localhost:8090")
        print("     • Swagger Docs API  : http://localhost:8090/docs")
        print("     • Usuário Admin     : 000.000.000-00 (ou admin)  |  Senha: [DEFINIDA NO .ENV / SEED]")  # nosec
    else:
        print("  ⚠️ [PORTA 8090] FrotaSaaS Enterprise em inicialização...")

    if dissertation_ok:
        print("  ✅ [PORTA 8080] Dashboard de IA da Dissertação ATIVO:")
        print("     • URL Dashboard     : http://localhost:8080/dashboard/")
        print("     • Copiloto de IA    : Ativo e integrado via linguagem natural")
    else:
        print("  ⚠️ [PORTA 8080] Dashboard da Dissertação em inicialização...")
    print("=" * 80)
    print("\n💡 Ambos os sistemas estão em execução concorrente. Pressione [Ctrl + C] para sair.\n")

    # Manter o processo vivo e monitorando
    try:
        while True:
            time.sleep(1)
            if proc_fleet.poll() is not None:
                print("⚠️ O processo FrotaSaaS (8090) encerrou inesperadamente.")
                break
            if proc_dissertation.poll() is not None:
                print("⚠️ O processo Dashboard da Dissertação (8080) encerrou inesperadamente.")
                break
    except KeyboardInterrupt:
        encerrar_processos()


if __name__ == "__main__":
    main()

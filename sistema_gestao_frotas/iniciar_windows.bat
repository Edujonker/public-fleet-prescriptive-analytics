@echo off
REM ==============================================================================
REM Script de Inicializacao para Windows - FrotaSaaS Enterprise
REM ==============================================================================

cd /d "%~dp0"
title FrotaSaaS Enterprise 2.0 - Servidor de Gestao de Frotas e Telemetria

echo ----------------------------------------------------------------------
echo Iniciando Sistema de Gestao de Frotas ^& Telemetria IoT (Windows)...
echo ----------------------------------------------------------------------

if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" executar_sistema.py
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" executar_sistema.py
) else (
    python executar_sistema.py
)

pause

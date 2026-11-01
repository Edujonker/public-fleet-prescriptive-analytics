@echo off
REM ==============================================================================
REM PPGCAP / UDESC - EXECUÇÃO PARALELA DE AMBOS OS SISTEMAS (PORTAS 8080 E 8090)
REM ==============================================================================
cd /d "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    SET "PYTHON_BIN=.venv\Scripts\python.exe"
) ELSE (
    SET "PYTHON_BIN=python"
)

%PYTHON_BIN% executar_ambos_sistemas.py
pause

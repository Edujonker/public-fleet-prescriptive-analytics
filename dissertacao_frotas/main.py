#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador Principal do Framework de Pesquisa - Dissertação de Mestrado
Execução sequencial auditada das etapas de pesquisa.
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 80)
    print("ORQUESTRADOR GERAL - DISSERTAÇÃO DE MESTRADO PPGCAP/UDESC")
    print("Framework de Analítica Prescritiva, ML Multimodal e Teoria dos Grafos")
    print("=" * 80)
    
    etapas = [
        ("01_auditoria_dados.py", "Auditoria e Verificação de Integridade dos Dados Brutos"),
        ("02_preprocessamento.py", "Saneamento e Engenharia de Atributos com Rastreabilidade"),
        ("03_analise_descritiva.py", "Análise Exploratória e Estatística Descritiva"),
        ("04_modelos_preditivos.py", "Treinamento e Avaliação Preditiva Temporal"),
        ("05_deteccao_anomalias.py", "Detecção Multimodal de Fraudes e Sobrepreço"),
        ("06_teoria_grafos.py", "Modelagem Complexa e Análise de Redes"),
        ("07_explicabilidade_xai.py", "Auditoria de Explicabilidade Algorítmica (SHAP/LIME)"),
        ("08_otimizacao_milp.py", "Otimização Prescritiva MILP e Análise de Sensibilidade"),
        ("09_validacao_estatistica.py", "Testes Hipotéticos e Certificação de Robustez"),
    ]
    
    src_dir = Path(__file__).resolve().parent / "src"
    
    for script, desc in etapas:
        script_path = src_dir / script
        if not script_path.exists():
            print(f"[PENDENTE] Script {script} ({desc}) ainda não implementado.")
            continue
            
        print(f"\n>>> Executando: {script} ({desc})...")
        cmd = [sys.executable, str(script_path)]
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"[ERRO CRÍTICO] Falha na execução de {script}. Abortando pipeline.")
            sys.exit(res.returncode)
        print(f">>> Concluído com sucesso: {script}")

    print("\n" + "=" * 80)
    print("EXECUÇÃO DO PIPELINE FINALIZADA COM SUCESSO.")
    print("=" * 80)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador Geral de Execução Integrada — Dissertação de Mestrado PPGCAP/UDESC
Autor: Eduardo Lopes Jonker (2026)

Executa de ponta a ponta:
  Etapa 1: Pipeline Modular de Ciência de Dados (dissertacao_frotas/src/)
    01. Auditoria e Imutabilidade dos Dados Brutos (SHA-256)
    02. Pré-processamento e Saneamento com Rastreabilidade
    03. Análise Exploratória e Estatística Não Paramétrica
    04. Modelagem Preditiva Supervisionada e Validação Temporal
    05. Detecção Multimodal de Anomalias e Sobrepreço
    06. Teoria dos Grafos e Redes Complexas Bipartidas
    07. Explicabilidade Algorítmica Auditável (SHAP / LIME)
    08. Otimização Prescritiva MILP (PuLP / HiGHS / Dual Simplex)
    09. Validação Estatística Avançada e Certificação de Robustez
  Etapa 2: Compilação Completa da Dissertação em PDF ABNT com Figuras Integradas
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def main():
    start_total = time.time()
    root_dir = Path(__file__).resolve().parent
    python_bin = root_dir / ".venv" / "bin" / "python3"
    if not python_bin.exists():
        python_bin = Path(sys.executable)
        
    print("=" * 84)
    print(" DISSERTAÇÃO DE MESTRADO PPGCAP/UDESC — SISTEMA UNIFICADO DE EXECUÇÃO")
    print(f" Interpretador Python: {python_bin}")
    print(f" Diretório Raiz: {root_dir}")
    print("=" * 84)

    pipeline_scripts = [
        ("dissertacao_frotas/src/01_auditoria_dados.py", "01. Auditoria Forense dos Dados Brutos (SHA-256)"),
        ("dissertacao_frotas/src/02_preprocessamento.py", "02. Saneamento e Rastreabilidade Formal de Exclusões"),
        ("dissertacao_frotas/src/03_analise_descritiva.py", "03. Estatística Descritiva e Testes Não Paramétricos"),
        ("dissertacao_frotas/src/04_modelos_preditivos.py", "04. Modelagem Preditiva com Validação Temporal"),
        ("dissertacao_frotas/src/05_deteccao_anomalias.py", "05. Detecção de Anomalias Calibrada com Estabilidade"),
        ("dissertacao_frotas/src/06_teoria_grafos.py", "06. Modelagem de Grafos e Comunidades de Oficinas"),
        ("dissertacao_frotas/src/07_explicabilidade_xai.py", "07. Explicabilidade Algorítmica (SHAP TreeExplainer / LIME)"),
        ("dissertacao_frotas/src/08_otimizacao_milp.py", "08. Otimização Prescritiva MILP e Preços-Sombra"),
        ("dissertacao_frotas/src/09_validacao_estatistica.py", "09. Validação Estatística de Hipóteses (Wilcoxon/DeLong)"),
        ("scripts/compilar_dissertacao_mestrado_completa.py", "10. Compilação da Dissertação em PDF com Figuras Inline"),
        ("scripts/gerar_relatorio_auditoria_pdf.py", "11. Emissão do Laudo de Auditoria Científica (auditoria.pdf)"),
        ("scripts/processar_abastecimentos.py", "12. Ingestão e Processamento da Base de Abastecimentos (Parquet/SQLite)"),
        ("scripts/gerar_relatorio_abastecimentos_pdf.py", "13. Emissão do Relatório Executivo de Abastecimentos (PDF)"),
        ("scripts/criar_tabela_veiculos_consolidada.py", "14. Consolidação da Frota Veicular, Gastos e Leilão (Art. 5º Decreto 47.539)"),
        ("scripts/gerar_dicionario_dados.py", "15. Geração do Dicionário de Dados do Banco e Relatório em PDF"),
        ("scripts/compilar_artigos_internacionais_pdf.py", "16. Compilação dos 4 Artigos Científicos Qualis A1 (PT e EN) em PDF"),
        ("scripts/compilar_relatorio_anomalias_detalhado.py", "17. Relatório de Anomalias Detalhado (PDF, CSV e JSON por Secretaria)"),
        ("sistema_gestao_frotas/testar_sistema.py", "19. Testes Unitários e de Integração do Sistema de Frotas (15 testes)"),
        ("sistema_gestao_frotas/simulador_e_teste_completo_frota.py", "20. Simulador End-to-End e Teste Completo da Frota (Cadastro, Análise e Despacho)"),
        ("scripts/auditoria_seguranca_devsecops.py", "21. Auditoria DevSecOps e Conformidade de Segurança (OWASP Top 10 / ISO 27001)"),
        ("scripts/compilar_relatorio_seguranca_normas_pdf.py", "22. Compilação do Relatório de Segurança, Normas, Patches e Criptografia em PDF"),
    ]

    sucessos = 0
    falhas = 0
    tempos = {}

    for rel_path, descricao in pipeline_scripts:
        script_path = root_dir / rel_path
        if not script_path.exists():
            print(f"\n[AVISO] Script não encontrado: {rel_path} ({descricao}), Pulando...")
            continue

        print(f"\n" + "-" * 84)
        print(f"▶ EXECUTANDO: {descricao}")
        print(f"  Caminho: {script_path}")
        print("-" * 84)
        
        t0 = time.time()
        try:
            res = subprocess.run([str(python_bin), str(script_path)], cwd=str(root_dir), check=False)
            dt = time.time() - t0
            tempos[descricao] = dt
            if res.returncode == 0:
                print(f"✔ CONCLUÍDO COM SUCESSO em {dt:.2f}s: {descricao}")
                sucessos += 1
            else:
                print(f"✘ ERRO NA EXECUÇÃO (Código {res.returncode}): {descricao}")
                falhas += 1
                if sys.stdin.isatty():
                    resp = input("\nDeseja continuar a execução dos próximos scripts? (s/n): ").strip().lower()
                    if resp not in ('s', 'sim', 'y', 'yes', ''):
                        print("[ABORTADO] Execução interrompida pelo usuário.")
                        break
                else:
                    print("[CONTINUANDO] Modo não interativo detectado, prosseguindo com os próximos scripts...")
        except KeyboardInterrupt:
            print("\n[INTERROMPIDO] Operação cancelada pelo usuário.")
            break
        except Exception as e:
            print(f"✘ EXCEÇÃO: {e}")
            falhas += 1

    total_time = time.time() - start_total
    print("\n" + "=" * 84)
    print(" RESUMO DA EXECUÇÃO INTEGRADA")
    print(f" Total de Etapas Concluídas: {sucessos}")
    print(f" Falhas / Pendências: {falhas}")
    print(f" Tempo Total Decorrido: {total_time:.2f} segundos ({total_time/60:.2f} minutos)")
    print("=" * 84)
    for desc, t_sec in tempos.items():
        print(f"  • {desc:<60} : {t_sec:>7.2f}s")
    print(f"Documento Final Atualizado: {root_dir / 'dissertacao_versao_revisada.pdf'}")
    print(f"Documentação do Sistema:    {root_dir / 'documentacao_gestao_de_frotas.pdf'}")
    print(f"Auditoria de Segurança:     {root_dir / 'relatorios' / 'relatorio_auditoria_seguranca_devsecops.md'}")
    print("=" * 84)

if __name__ == "__main__":
    main()

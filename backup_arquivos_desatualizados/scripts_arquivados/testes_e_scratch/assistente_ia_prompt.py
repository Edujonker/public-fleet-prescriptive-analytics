#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ASSISTENTE DE IA VIA PROMPT INTERATIVO E CLI (PPGCAP/UDESC)
================================================================================
Dissertação: Analítica Preditiva e Prescritiva para Gestão de Frota Veicular Pública
Autor: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes

REGRAS OBRIGATÓRIAS IMPLEMENTADAS:
1. Responde apenas perguntas relacionadas aos dados e métricas do sistema fornecidos no contexto.
2. Se o usuário perguntar algo fora do contexto (ex: receitas de cozinha, futebol, piadas, opiniões gerais),
   responde exatamente: "Desculpe, só posso responder dúvidas sobre os dados do seu sistema."
3. Não inventa informações. Se os dados fornecidos não forem suficientes para responder,
   diz que a informação não está disponível.
================================================================================
"""

import sys
import os
import argparse
from pathlib import Path

# Ajustar caminho do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.ai_assistant import FleetAIAssistant

def print_banner():
    banner = """
╔════════════════════════════════════════════════════════════════════════════════════════╗
║             ASSISTENTE DE IA, DADOS E MÉTRICAS DO SISTEMA (PPGCAP/UDESC)             ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ REGRAS OBRIGATÓRIAS DO ASSISTENTE:                                                     ║
║ 1. Responde apenas perguntas sobre dados e métricas do sistema.                        ║
║ 2. Perguntas fora de contexto recebem estritamente:                                    ║
║    "Desculpe, só posso responder dúvidas sobre os dados do seu sistema."               ║
║ 3. Não inventa dados. Se a informação não constar na base, informa indisponibilidade.   ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Comandos Especiais:                                                                    ║
║   'sair', 'exit', 'q'      -> Encerra o assistente via prompt                          ║
║   'ajuda'                  -> Exibe exemplos de perguntas sobre o sistema               ║
║   'atualizar graficos'     -> Recalcula testes estatísticos e regenera figuras 76 a 79  ║
║   'gerar relatorio'        -> Compila o relatório formal em PDF (18 MB) via WeasyPrint ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_ajuda():
    ajuda = """
📌 EXEMPLOS DE PERGUNTAS VÁLIDAS SOBRE OS DADOS DO SISTEMA:
  • Quantas ordens de serviço existem na base e qual o valor total aprovado?
  • Os custos de manutenção seguem distribuição normal pelo teste de Lilliefors?
  • Qual foi o resultado do teste de hipóteses entre veículos leves e comerciais?
  • Qual é a taxa diária de falhas corretivas por Poisson e há sobredispersão?
  • Quais são as probabilidades estacionárias e tempos de permanência pela Cadeia de Markov?
  • Qual modelo de séries temporais teve melhor desempenho, ETS ou ARIMA?
  • Como foi avaliada a estabilidade do Isolation Forest e sua relação com glosas?
  • Qual a economia obtida pelo modelo prescritivo MILP e qual é o gargalo?
  • Quantas inconsistências de hodômetro foram detectadas pela auditoria?
"""
    print(ajuda)

def main():
    parser = argparse.ArgumentParser(
        description="Assistente de IA que responde dúvidas sobre dados e métricas do sistema via prompt."
    )
    parser.add_argument("pergunta_posicional", nargs="*", help="Pergunta direta passada via argumentos de linha de comando.")
    parser.add_argument("-p", "--pergunta", type=str, help="Pergunta em linguagem natural para responder via prompt.")
    parser.add_argument("--json", action="store_true", help="Retorna a resposta estruturada em JSON.")
    args = parser.parse_args()

    # Inicializar motor de IA
    assistant = FleetAIAssistant()

    # 1. Pergunta fornecida via argumento posicional ou flag --pergunta
    if args.pergunta:
        query = args.pergunta.strip()
    elif args.pergunta_posicional:
        query = " ".join(args.pergunta_posicional).strip()
    elif not sys.stdin.isatty():
        # Entrada via pipe / stdin (ex: echo "..." | python3 assistente_ia_prompt.py)
        query = sys.stdin.read().strip()
    else:
        query = None

    # Modo Não Interativo (Uma única resposta direta)
    if query:
        result = assistant.process_query(query)
        if args.json:
            import json
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result.get("resposta", ""))
        return

    # Modo Interativo via Prompt Contínuo
    print_banner()
    while True:
        try:
            prompt_input = input("\n[Usuário] > ").strip()
            if not prompt_input:
                continue

            if prompt_input.lower() in ["sair", "exit", "quit", "q"]:
                print("\nEncerrando o Assistente de IA. Sessão finalizada com sucesso.\n")
                break

            if prompt_input.lower() in ["ajuda", "help", "?"]:
                print_ajuda()
                continue

            # Processar pergunta com as regras estritas
            res = assistant.process_query(prompt_input)
            resposta = res.get("resposta", "")

            print("\n" + "─" * 80)
            print(f"[Assistente de IA]:\n{resposta}")
            print("─" * 80)

        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando o Assistente de IA. Sessão finalizada com sucesso.\n")
            break
        except Exception as e:
            print(f"\n[Erro ao processar]: {e}")

if __name__ == "__main__":
    main()

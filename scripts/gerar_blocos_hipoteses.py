#!/usr/bin/env python3
"""
Gera os blocos de texto das hipóteses a partir de scripts/hipoteses_oficiais.py:

  overleaf_dissertacao_udesc/Textuais/Bloco_Hipoteses.tex      tabela + frases (Cap. 13)
  overleaf_dissertacao_udesc/PosTextuais/ApendiceD.tex          desvios do protocolo e E1–E3
  docs/hipoteses/resumo_hipoteses.md                            versão Markdown (README, SIC)

Rodar depois da etapa 09. Não editar os arquivos gerados à mão.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hipoteses_oficiais as h  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OV = ROOT / "overleaf_dissertacao_udesc"
CAB = "% Gerado por scripts/gerar_blocos_hipoteses.py a partir do certificado da etapa 09. Não editar à mão.\n"
t = h._tex
V = h.V


def apendice_d() -> str:
    L = [CAB, r"\chapter{DESVIOS DO PROTOCOLO, CORREÇÕES E HIPÓTESES EXPLORATÓRIAS}", r"\label{ap:desvios}", "",
         r"\section{Regra de decisão}",
         t("Cada hipótese foi avaliada por dois critérios definidos antes dos resultados: o texto do anteprojeto, transformado em teste "
           "nos scripts 04b, 04c, 07b e 08 antes da primeira execução de cada um, e o limiar numérico da qualificação (H1: ganho de pelo "
           "menos 15% no MAE; H3: economia acima de 10%; H4: concordância SHAP × LIME acima de 0,85). Uma hipótese é SUSTENTADA quando "
           "atende os dois, PARCIALMENTE SUSTENTADA quando atende um e NÃO SUSTENTADA quando não atende nenhum."), "",
         r"\section{Testes acrescentados para cumprir o anteprojeto}", r"\begin{itemize}",
         r"\item " + t(f"H1: estudo ablativo M × M+P com IC 95% por bootstrap pareado em MAE e ROC-AUC. O abastecimento não pôde entrar: a base cobre jan/2019 a fev/2022 e não se sobrepõe ao período de teste (2025–2026)."),
         r"\item " + t("H2: comparação dos ensembles com SVR-RBF e SVC-RBF, como prevê o anteprojeto, por não inferioridade (margem de 5% no MAE e de −0,02 na AUC), com todos os modelos treinados na mesma subamostra de 12.000 linhas."),
         r"\item " + t(f"H3: custos calculados pelo solver HiGHS, comparados à prática reconstruída (apenas manutenções obrigatórias, {V['h3_bl0']}) e a uma heurística gulosa benefício/custo ({V['h3_heur']})."),
         r"\item " + t(f"H4: fidelidade (aditividade do SHAP; R² local do LIME = {V['h4_lime_r2']}) e estabilidade (LIME entre sementes = {V['h4_lime_estab']}; SHAP entre modelos re-treinados = {V['h4_shap_estab']})."),
         r"\end{itemize}", "",
         r"\section{Erros corrigidos que alteraram resultados}", r"\begin{enumerate}",
         r"\item " + t("Valores patrimoniais: o pré-processamento interpretava “R$ 48,010.00” como R$ 48,01, deixando o patrimônio do painel cerca de mil vezes menor."),
         r"\item " + t("Ablação de H1: o ganho de +0,"+"41% estava digitado na tabela de resultados, sem código que o produzisse."),
         r"\item " + t("Explicabilidade: a figura local SHAP × LIME exibia valores SHAP multiplicados por um fator aleatório no lugar do LIME."),
         r"\item " + t("Otimização: o script do MILP descartava o resultado do solver e usava custos fixos (economia de 17,"+"51%, R$ 9,"+"30 milhões)."),
         r"\item " + t("Validação: a etapa 09 lia uma chave inexistente e usava a ROC-AUC 0,"+"7366 para a regressão logística (valor real: 0,8292)."),
         r"\item " + t("Indicador de antieconomicidade: o número de veículos era limitado entre 313 e 427 no código; o valor calculado é 242."),
         r"\end{enumerate}", "",
         r"\section{Hipóteses exploratórias com teste confirmatório pré-registrado}",
         t("As hipóteses abaixo surgiram da análise da base atual e são exploratórias nela. Elas foram registradas em 15/11/2026 "
           "(docs/hipoteses/preregistro_hipoteses_exploratorias_2026.md, com hash SHA-256) para teste na extração de 2026 da SEA/SC, "
           "ainda não recebida."), r"\begin{itemize}",
         r"\item " + t("E1: a rede de oficinas de 2026 tem modularidade acima de 30 redes nulas e os 10% maiores concentram mais de 50% do gasto."),
         r"\item " + t("E2: o escore do Isolation Forest não separa OS glosadas (IC 95% da AUC entre 0,40 e 0,60)."),
         r"\item " + t("E3: o total realizado em 2026 fica a menos de 10% da proposta de LOA calculada (R$ 33.594.176,58)."),
         r"\end{itemize}", ""]
    return "\n".join(L)


def main():
    (OV / "Textuais/Bloco_Hipoteses.tex").write_text(CAB + h.bloco_latex(), encoding="utf-8")
    (OV / "PosTextuais/ApendiceD.tex").write_text(apendice_d(), encoding="utf-8")
    (ROOT / "docs/hipoteses/resumo_hipoteses.md").write_text(
        "# Resultado das hipóteses\n\n_Gerado por `scripts/gerar_blocos_hipoteses.py`; regra de decisão e desvios em "
        "`docs/hipoteses/desvios_do_protocolo.md`._\n\n" + h.bloco_md(), encoding="utf-8")
    print("OK: Bloco_Hipoteses.tex, ApendiceD.tex, resumo_hipoteses.md")


if __name__ == "__main__":
    main()

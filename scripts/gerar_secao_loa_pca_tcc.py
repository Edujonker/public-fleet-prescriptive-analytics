#!/usr/bin/env python3
"""Gera a seção da dissertação sobre o experimento LOA/PCA 2026 e o confronto com LOA, PCA e execução.

Saída: overleaf_dissertacao_udesc/Textuais/Secao07_PlanejamentoLOA_PCA.tex (incluída no Capítulo 7)
e cópia das figuras para overleaf_dissertacao_udesc/figuras/. Todos os números vêm dos JSON/CSV
gerados por planejamento_loa_pca_2026.py e execucao_orcamentaria_frota.py. Não editar o .tex à mão.
"""
import csv
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comparacao_loa_execucao as cmp  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "resultados_loa_pca_2026"
TEX = ROOT / "overleaf_dissertacao_udesc/Textuais/Secao07_PlanejamentoLOA_PCA.tex"
FIGDIR = ROOT / "overleaf_dissertacao_udesc/figuras"
FIGS = {"fig_avaliacao_retrospectiva.png": "loa2026_avaliacao_retrospectiva.png",
        "fig_serie_previsao.png": "loa2026_serie_previsao.png",
        "fig_execucao_loa_2026.png": "loa2026_execucao_empenhos.png"}
mi, pct = cmp.mi, cmp.pct


def t(x):
    """Escapa para LaTeX e converte @rotulo@ em \\ref{rotulo}."""
    import re
    return re.sub(r"@([A-Za-z0-9:\-]+)@", r"\\ref{\1}", cmp._tex(x))


def figura(arq, legenda, rotulo, fonte="Dados da SEA/SC e da SEF/SC processados pelo autor (2026)."):
    return "\n".join(["\\begin{figure}[H]", "\\centering", f"\\caption{{{t(legenda)}}}",
                      f"\\includegraphics[width=0.95\\textwidth]{{figuras/{FIGS[arq]}}}", f"\\fonte{{{t(fonte)}}}",
                      f"\\label{{{rotulo}}}", "\\end{figure}"])


def tabela(legenda, rotulo, cab, linhas, larg):
    col = "".join(f"p{{{w}\\textwidth}}" for w in larg)
    return "\n".join(["\\begin{table}[H]", "\\centering\\small", f"\\caption{{{t(legenda)}}}", f"\\label{{{rotulo}}}",
                      f"\\begin{{tabular}}{{{col}}}", "\\hline", " & ".join(f"\\textbf{{{t(c)}}}" for c in cab) + " \\\\ \\hline"]
                     + [" & ".join(t(c) for c in l) + " \\\\" for l in linhas]
                     + ["\\hline", "\\end{tabular}", "\\fonte{Elaborado pelo autor (2026).}", "\\end{table}"])


def main():
    E = json.loads((RES / "resultado_experimento.json").read_text(encoding="utf-8"))
    c = cmp.conteudo()
    if c is None:
        sys.exit("faltam resultado_experimento.json ou execucao_orcamentaria_frota.json")
    FIGDIR.mkdir(parents=True, exist_ok=True)
    for a, b in FIGS.items():
        shutil.copy2(RES / a, FIGDIR / b)
    esc = E["modelo_escolhido"]
    inc = E["incerteza_2026"][esc]
    corte = cmp._mes(E["corte"])
    bt = [[b.split(" (")[0], k, mi(v["previsto"]), mi(v["realizado"]), pct(v["erro_total_pct"])]
          for b, d in E["avaliacao_retrospectiva"].items() for k, v in d.items()]
    org = []
    with open(RES / "proposta_loa_2026_por_orgao.csv", encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f, delimiter=";")):
            if i >= 6:
                break
            org.append([r["orgao"], pct(float(r["participacao"].replace(",", "."))), mi(float(r["proposta_2026"].replace(",", "."))),
                        mi(float(r["realizado_2024"].replace(",", ".")))])
    a25 = E["ano_2025_observado_mais_presumido"]
    h24 = E["realizado_anual"]["2024"]
    T = ["% Gerado por scripts/gerar_secao_loa_pca_tcc.py a partir de resultados_loa_pca_2026/*.json. Não editar à mão.",
         "\\section{Aplicação ao planejamento orçamentário: LOA e PCA de 2026}", "\\label{sec:loa-pca-2026}",
         t(f"Esta seção aplica a previsão de demanda ao ciclo orçamentário. A pergunta é quanto o Estado deveria reservar na Lei Orçamentária "
           f"Anual (LOA) de 2026 para a manutenção da frota, distribuído por órgão e por natureza de despesa, e que itens o Plano de Contratações "
           f"Anual (PCA) de 2026 deveria prever, usando só dados observados até {corte}. O experimento está em scripts/planejamento_loa_pca_2026.py; "
           "o confronto com a LOA e a execução, em scripts/execucao_orcamentaria_frota.py."),
         "\\subsection{Desenho e escolha do modelo}",
         t(f"A base de OS da SEA/SC tem cobertura completa até {corte}; depois disso restam poucas OS por mês, e esses meses foram tratados como "
           "ausentes. Os meses de out--dez/2025 foram presumidos pelo modelo. Três previsores (sazonal ingênuo com crescimento, ETS amortecido e "
           "SARIMA, os dois últimos em logaritmo) e a média deles foram avaliados em dois testes retrospectivos: treino até dez/2023 para prever 2024 "
           f"e treino até dez/2024 para prever jan--{cmp.MESES[int(E['corte'][5:]) - 1]}/2025. O critério foi o menor erro absoluto médio no total do "
           f"período, e o escolhido foi o {esc}, com {pct(E['erro_medio_abs_total'][esc])} (Tabela~@tab:loa-backtest@)."),
         tabela("Testes retrospectivos dos modelos de previsão do gasto anual de manutenção", "tab:loa-backtest",
                ["Teste", "Modelo", "Previsto", "Realizado", "Erro no total"], bt, [0.08, 0.36, 0.15, 0.15, 0.13]),
         figura("fig_avaliacao_retrospectiva.png", "Previsões mensais dos testes retrospectivos contra o realizado", "fig:loa-backtest"),
         "\\subsection{Proposta de LOA e de PCA}",
         t(f"A proposta para 2026 é de {mi(E['total_2026'])}, com intervalo de 80% de {mi(inc['10'])} a {mi(inc['90'])} em 2.000 trajetórias "
           f"simuladas do modelo. O valor fica {pct(E['total_2026'] / a25 - 1)} acima de 2025 (observado e presumido, {mi(a25)}) e "
           f"{pct(E['total_2026'] / h24 - 1)} acima de 2024 ({mi(h24)}) (Figura~@fig:loa-serie@). A distribuição por órgão usa a participação dos "
           f"12 meses até o corte; aplicadas ao total real de 2024, as participações de 2023 erraram {pct(E['teste_distribuicao_orgaos_2024'])} do valor. "
           f"Peças respondem por {pct(E['participacao_pecas']['ultimos_12_meses'])} do gasto. O PCA proposto lista as 40 descrições de peça de maior "
           f"gasto, que cobrem {pct(E['pca_cobertura_top40'])} do valor de peças; {E['teste_pca_itens_2024']['itens_top40_2024_ja_no_top40_2023']} dos 40 "
           "maiores itens de 2024 já estavam entre os 40 maiores de 2023."),
         figura("fig_serie_previsao.png", "Gasto mensal de manutenção: observado, meses presumidos e previsão de 2026", "fig:loa-serie"),
         tabela("Proposta de LOA 2026 para manutenção da frota: seis maiores órgãos", "tab:loa-orgaos",
                ["Órgão", "Participação", "Proposta 2026", "OS 2024"], org, [0.40, 0.14, 0.17, 0.17]),
         "\\subsection{Confronto com a LOA, o PCA e a execução de 2026}",
         t("A LOA 2026 (Lei nº 19.683/2026) foi lida por OCR. Ela identifica a frota em 2 subações de manutenção, 1 de combustível e 8 de "
           "aquisição; nos demais órgãos, inclusive a PM, a manutenção fica dentro de ações administrativas genéricas e não pode ser isolada."),
         ]
    T.append(cmp.latex_bloco().replace("\\paragraph{", "\\paragraph{", 1))
    T.append(figura("fig_execucao_loa_2026.png",
                    "Empenho acumulado de manutenção (2024–2026) contra a proposta do experimento, e subações da LOA 2026 que isolam a frota",
                    "fig:loa-execucao", "Empenhos SEF/SC (dados.sc.gov.br), LOA 2026 e experimento; elaborado pelo autor (2026)."))
    T += ["\\subsection{Síntese}", "\\begin{itemize}"] + [f"\\item {t(x)}" for x in c["conclusoes"]] + ["\\end{itemize}",
          t("Para a gestão, o resultado tem duas leituras. O método reproduz bem um ano estável (erro médio de "
            f"{pct(E['erro_medio_abs_total'][esc])} nos testes), mas não antecipa mudanças de contrato, que precisam entrar no planejamento como "
            "informação externa. E a LOA, no nível de subação, não serve para medir o custo da frota: o acompanhamento precisa usar a natureza da "
            "despesa nos empenhos, por subelemento, cruzada com as OS.")]
    TEX.write_text("\n".join(T) + "\n", encoding="utf-8")
    cap = ROOT / "overleaf_dissertacao_udesc/Textuais/Capitulo07_ModelagemTemporal.tex"
    s = cap.read_text(encoding="utf-8")
    linha = "\\input{Textuais/Secao07_PlanejamentoLOA_PCA}"
    if linha not in s:
        cap.write_text(s.rstrip("\n") + "\n" + linha + "\n", encoding="utf-8")
    print("OK", TEX)


if __name__ == "__main__":
    main()

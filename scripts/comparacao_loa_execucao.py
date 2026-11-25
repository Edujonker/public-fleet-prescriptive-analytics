"""Texto único da comparação experimento × LOA 2026 × PCA × execução (empenhos).

Lido por planejamento_loa_pca_2026.py (relatório LOA), gerar_relatorio_qualificacao_pdf.py
e gerar_secao_loa_pca_tcc.py (dissertação). Todos os números vêm de
resultados_loa_pca_2026/resultado_experimento.json e execucao_orcamentaria_frota.json.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "resultados_loa_pca_2026/resultado_experimento.json"
EXE = ROOT / "resultados_loa_pca_2026/execucao_orcamentaria_frota.json"
LOA = ROOT / "leis_e_normativas/estaduais_SC/loa_2026_frota_extraido.json"
PCA = ROOT / "leis_e_normativas/estaduais_SC/pca_2026_pncp.json"
FIG = ROOT / "resultados_loa_pca_2026/fig_execucao_loa_2026.png"
FIG_PCA = ROOT / "resultados_loa_pca_2026/fig_comparativo_pca_real_vs_estimado.png"
FIG_PCA_2025 = ROOT / "resultados_loa_pca_2026/fig_comparativo_pca_2025_real_vs_estimado.png"
FIG_PCA_BIENAL = ROOT / "resultados_loa_pca_2026/fig_comparativo_pca_bienal_2025_2026.png"
FIG_PROJECAO = ROOT / "resultados_loa_pca_2026/fig_projecao_gastos_2028_2029_locacao_vs_propria.png"
PCA_2025_JSON = ROOT / "leis_e_normativas/estaduais_SC/pca_2025_analise.json"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _br(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mi(x):
    return "R$ " + _br(x / 1e6, 2) + " mi"


def pct(x, nd=1):
    return _br(100 * x, nd) + "%"


def _mes(ym):
    a, m = ym.split("-")
    return f"{MESES[int(m) - 1]}/{a}"


def dados():
    if not (EXP.exists() and EXE.exists()):
        return None
    return (json.loads(EXP.read_text(encoding="utf-8")), json.loads(EXE.read_text(encoding="utf-8")),
            json.loads(LOA.read_text(encoding="utf-8")) if LOA.exists() else None,
            json.loads(PCA.read_text(encoding="utf-8")) if PCA.exists() else None)


def conteudo():
    """Devolve dict com 'paragrafos' (lista de (titulo, texto)), 'tabela' (cab, linhas) e 'conclusoes'."""
    d = dados()
    if not d:
        return None
    E, X, L, P = d
    C = X["comparacao_experimento"]
    mf = X["mes_fim_2026"]
    ate = f"jan–{MESES[mf - 1]}"
    cr = X["credores_manutencao_top5"]
    ini = X["primeiro_mes_com_empenho_por_credor"]
    novo_raw = max(ini, key=ini.get)
    antigo_raw = cr["2024"][0]["credor"]
    NOMES = {"TICKET GESTAO EM MANUTENCAO EZC S A": "Ticket Gestão em Manutenção EZC S.A.", "QFROTAS SISTEMAS LTDA": "QFrotas Sistemas Ltda."}
    novo, antigo = novo_raw, antigo_raw
    sh_antigo_24 = cr["2024"][0]["participacao"]
    sh_novo_26 = next(c["participacao"] for c in cr["2026"] if c["credor"] == novo)
    ac = X["acumulado_jan_ate_mes_fim"]
    m26 = X["manutencao_mensal"]["2026"]
    tri1 = sum(m26[:3])
    ind = C["indicacao_ano_2026_pela_fracao"]
    fr = X["fracao_ate_mes_fim"]
    pc = next((p for p in C["subacoes_mesma_natureza"] if p["orgao_experimento"] == "PC SC"), None)
    sub = {s["subacao"]: s for s in X["subacoes_loa_empenho"]}
    fuel = next((s for s in X["subacoes_loa_empenho"] if s["tipo"] == "combustível"), None)
    sejuri = sub.get("750.0261.011045")
    fes = sub.get("400.0261.014016")
    sem_base = [s for s in X["subacoes_loa_empenho"] if all(s[f"empenhado_{k}"] == 0 for k in ("2024", "2025", "2026_ate_mes_fim"))]

    P_ = []
    P_.append(("Fonte da execução",
               f"A execução foi medida nos empenhos da SEF/SC publicados em dados.sc.gov.br (conjunto “empenhos”, 2024 a {MESES[mf - 1]}/2026), "
               "somando emissões e reforços e descontando anulações e estornos. Manutenção da frota corresponde aos subelementos 3.3.90.30.39 "
               "(material para manutenção de veículos) e 3.3.90.39.19 (manutenção e conservação de veículos), de todos os órgãos. "
               "Empenho é a reserva da despesa; ele não equivale ao valor liquidado nem ao aprovado nas OS."))
    P_.append(("Troca do contrato de manutenção",
               f"Em 2024, {NOMES.get(antigo, antigo)} recebeu {pct(sh_antigo_24)} do empenho de manutenção. O primeiro empenho de "
               f"{NOMES.get(novo, novo)} é de "
               f"{_mes(ini[novo])}, e em 2026 essa empresa concentra {pct(sh_novo_26)}. A base de OS da SEA/SC tem cobertura completa até "
               f"{_mes(E['corte'])}, o mesmo mês da troca. A queda de OS depois do corte, tratada no experimento como fim da extração, coincide portanto "
               "com a mudança de contrato, o que indica que a base vem do sistema da contratada anterior. A projeção de 2026 estima um gasto que passou "
               "a correr em outro contrato, com outros preços e regras."))
    P_.append(("Escala das duas medidas",
               f"Em 2024, único ano completo nas duas bases, o empenho de manutenção somou {mi(C['empenho_manutencao_2024'])} e o valor aprovado nas OS "
               f"da SEA/SC, {mi(C['os_sea_2024'])}: o empenho foi {_br(C['razao_empenho_sobre_os_2024'], 2)} vez o valor das OS. Em 2025 o empenho "
               f"foi {mi(C['empenho_manutencao_2025'])}, contra {mi(C['os_sea_2025_obs_mais_presumido'])} de OS observadas e presumidas."))
    P_.append(("Proposta do experimento contra o empenho de 2026",
               f"De {ate}/2026 foram empenhados {mi(C['empenho_manutencao_2026_ate_mes_fim'])} em manutenção, contra {mi(ac['2024']['manutencao'])} "
               f"e {mi(ac['2025']['manutencao'])} no mesmo período de 2024 e 2025 (alta de {pct(ac['2026']['manutencao'] / ac['2025']['manutencao'] - 1)} "
               f"sobre 2025). Esse valor já é {pct(C['empenho_2026_sobre_proposta'], 0)} da proposta anual do experimento ({mi(C['proposta_2026'])}) "
               f"e {pct(C['empenho_2026_sobre_proposta_base_empenho'], 0)} da proposta convertida para a escala do empenho pela razão de 2024 "
               f"({mi(C['proposta_2026_base_empenho'])}). Parte da alta vem dos empenhos globais do novo contrato no início do ano: jan–mar/2026 "
               f"concentram {mi(tri1)}. Se 2026 repetisse a fração empenhada até {MESES[mf - 1]} em 2024 ({pct(fr['2024'], 0)}) ou em 2025 "
               f"({pct(fr['2025'], 0)}), o ano fecharia entre {mi(min(ind.values()))} e {mi(max(ind.values()))}. Isso é uma indicação, não uma "
               "previsão, porque o novo contrato muda o calendário dos empenhos."))
    if pc:
        P_.append(("LOA: a subação da Polícia Civil",
                   f"A subação {pc['subacao']} (“{pc['descricao']}”) tem {mi(pc['loa_2026'])} na LOA 2026, {_br(pc['loa_2026'] / pc['proposta_experimento_2026'], 1)} "
                   f"vezes a proposta do experimento para a PC SC ({mi(pc['proposta_experimento_2026'])}). Os empenhos explicam a diferença: em 2025 a "
                   f"subação empenhou {mi(pc['empenho_total']['2025'])}, dos quais {mi(pc['empenho_combustivel']['2025'])} em combustível e só "
                   f"{mi(pc['empenho_manutencao']['2025'])} em manutenção. Na mesma natureza de despesa, o empenho de manutenção de 2024 "
                   f"({mi(pc['empenho_manutencao']['2024'])}) fica perto das OS da SEA/SC ({mi(pc['os_sea_2024'])}) e da proposta. A distância "
                   "vem do escopo da subação, que inclui combustível e locação, e não de erro da projeção."))
    linhas_extra = []
    if fuel:
        linhas_extra.append(f"a subação de combustível da SIE e da PMRv tem {mi(fuel['loa_2026'])} na LOA e já empenhou "
                            f"{mi(fuel['empenhado_2026_ate_mes_fim'])} ({pct(fuel['execucao_2026_sobre_loa'], 0)} da dotação inicial)")
    if sejuri:
        linhas_extra.append(f"a renovação da frota da SEJURI ({mi(sejuri['loa_2026'])}) não tinha empenho até {MESES[mf - 1]}/2026, depois de "
                            f"{mi(sejuri['empenhado_2025'])} em 2025")
    if fes:
        linhas_extra.append(f"a aquisição de veículos do FES tem {mi(fes['loa_2026'])} na LOA, contra {mi(fes['empenhado_2025'])} empenhados em 2025")
    estatais = sorted({s["unidade"] for s in sem_base if "S.A" in s["unidade"]})
    outras = [s for s in sem_base if "S.A" not in s["unidade"]]
    if estatais:
        linhas_extra.append("as subações de " + ", ".join(estatais) + " não têm empenho na base em nenhum dos três anos, "
                            "o que é esperado para empresas estatais, cuja execução não passa pelo SIGEF")
    for s in outras:
        desc = s["descricao"] + (" […]" if s["descricao"].split()[-1] in ("e", "de", "da", "do", "a", "para") else "")
        linhas_extra.append(f"a subação {s['subacao']} (“{desc}”, {mi(s['loa_2026'])}) não teve empenho em 2024, 2025 nem até "
                            f"{MESES[mf - 1]}/2026")
    P_.append(("LOA: demais subações da frota",
               "Fora da manutenção, a dotação inicial da LOA é um mau guia da execução: " + "; ".join(linhas_extra) + ". "
               "Na maior parte dos órgãos, inclusive a PM, a LOA não separa a frota, e a comparação só é possível pela natureza da despesa no empenho."))
    P_.append(("PCA 2025 oficial e teste retrospectivo (treino até dez/2024)",
               "O PCA oficial de 2025 da SEA/SC foi igualmente resgatado e analisado (docs/PCA 2025.pdf, 373 páginas). "
               "Em 2025, o Estado planejou R$ 43,67 mi no Processo SEA 4749/2025 (PE 593/2025) para locação corporativa de veículos terceirizados. "
               "Treinando os modelos temporais estritamente com dados até dezembro de 2024 (janela retrospectiva BT2), a previsão anual da manutenção mecânica "
               f"da frota própria atingiu R$ 37,56 mi na escala de empenhos e R$ 32,28 mi no censo de ordens de serviço. Na janela observada de jan–set/2025, "
               f"o modelo SARIMA (log) previu R$ 24,10 mi frente a R$ 21,94 mi observados (erro de apenas +9,81%, confirmando a sustentabilidade dentro da margem de 10%). "
               "Comparando com o PCA 2025, a manutenção da frota própria foi de 14% a 26% menor que o dispêndio em locação corporativa."))
    P_.append(("PCA 2026 oficial (PCA-E SEA/SC)",
               "O PCA oficial de 2026 foi obtido e analisado diretamente a partir do documento publicado pela Diretoria de Gestão de Licitações e Contratos da SEA/SC "
               f"(docs/PCA-E 2026.pdf, 335 páginas). No planejamento compartilhado de frotas, o Estado programou {mi(90677641.68)} em locação veicular "
               f"(R$ 47,01 mi no Processo SEA 22719/2025 para nova contratação compartilhada e R$ 43,67 mi no Processo SEA 4749/2025 para prorrogação do PE 593/2025). "
               "A manutenção mecânica da frota própria não consta como nova aquisição porque é gerida sob o contrato corporativo continuado de gerenciamento (QFrotas), "
               f"cujas ordens de serviço correm diretamente nos subelementos 3.3.90.30/39. Comparativamente, a proposta anual de manutenção do experimento ({mi(C['proposta_2026'])}) "
               f"equivale a cerca de {pct(C['proposta_2026'] / 90677641.68, 0)} do orçamento estadual planejado para locação de veículos."))
    P_.append(("Projeção de gastos para 2028 e 2029 e análise de vantajosidade da locação",
               "A projeção longitudinal a partir da série histórica e dos modelos de aprendizado calibrados estima que o dispêndio inercial de manutenção "
               "da frota própria atingirá R$ 56,35 mi em 2028 e R$ 61,08 mi em 2029 (ou R$ 48,65 mi e R$ 52,73 mi caso implementada a política prescritiva MILP com -13,66% de redução). "
               "Em contrapartida, a locação corporativa de veículos saltou de R$ 43,67 mi (2025) para R$ 90,68 mi (2026), projetando-se em R$ 96,20 mi (2028) e R$ 99,08 mi (2029). "
               "Quanto ao quantitativo de veículos: o orçamento de R$ 90,68 mi do PCA 2026 financia aproximadamente 2.000 a 2.150 veículos locados (a um custo médio unitário de mercado de ~R$ 3.780/mês ou R$ 45,34 mil/ano). "
               "Já a frota própria estadual (7.580 veículos no censo, com ~5.000 veículos ativos) demanda apenas R$ 9,42 mil/ano por veículo (R$ 785/mês) em manutenção inercial, caindo para R$ 8,13 mil/ano (R$ 678/mês) sob a política MILP. "
               "Conclusão de vantajosidade: Não é vantajoso substituir a totalidade da frota própria por locação (o que exigiria mais de R$ 340 milhões anuais). "
               "A locação de veículos é economicamente viável apenas como complemento tático em setores de uso severo (viaturas operacionais da Polícia Civil e Militar); para o restante da administração, manter a frota própria com manutenção prescritiva é de 4,8 a 5,6 vezes mais econômico por veículo."))
    P_.append(("Efeito sobre a hipótese exploratória E3",
               "A E3 (proposta com erro abaixo de 10% no total) foi pré-registrada contra o valor aprovado nas OS de 2026 da SEA/SC, que ainda não foi "
               "extraído; o empenho é outra medida e não decide a hipótese. O sinal é desfavorável: mesmo na escala do empenho, o valor de "
               f"{ate}/2026 já supera a proposta anual em {pct(C['empenho_2026_sobre_proposta_base_empenho'] - 1, 0)} (a proposta para os mesmos "
               f"meses é {mi(C['proposta_2026_ate_mes_fim'])}), e a troca de contrato quebra a premissa de continuidade da série usada na projeção. "
               "Há também um risco para o próprio teste: se a extração de 2026 vier do sistema da contratada anterior, ela não terá as OS do novo "
               "contrato. Nesse caso a E3 não poderá ser testada como registrada, e qualquer troca de medida terá de ser registrada como desvio "
               "antes de ver os dados."))

    cab = ["Medida", "2024", "2025", f"2026 ({ate})", "Proposta 2026"]
    linhas = [["Manutenção – empenho (todos os órgãos)", mi(C["empenho_manutencao_2024"]), mi(C["empenho_manutencao_2025"]),
               mi(C["empenho_manutencao_2026_ate_mes_fim"]), mi(C["proposta_2026_base_empenho"]) + " (esc. empenho)"],
              ["Manutenção – OS aprovadas SEA/SC", mi(C["os_sea_2024"]), mi(C["os_sea_2025_obs_mais_presumido"]) + " (c/ presumido)",
               "não extraído", mi(C["proposta_2026"])]]
    if pc:
        linhas += [["PC SC subação 013148 – total empenhado", mi(pc["empenho_total"]["2024"]), mi(pc["empenho_total"]["2025"]),
                    mi(pc["empenho_total"]["2026"]), "LOA: " + mi(pc["loa_2026"])],
                   ["PC SC subação 013148 – só manutenção", mi(pc["empenho_manutencao"]["2024"]), mi(pc["empenho_manutencao"]["2025"]),
                    mi(pc["empenho_manutencao"]["2026"]), mi(pc["proposta_experimento_2026"])],
                   ["PC SC – OS aprovadas SEA/SC", mi(pc["os_sea_2024"]), "—", "—", "—"]]
    conc = [f"A proposta do experimento ({mi(C['proposta_2026'])}) subestima a execução de 2026: o empenho de {ate} já a supera, também na escala do empenho.",
            f"Uma causa provável é a troca do contrato de manutenção em {_mes(ini[novo])}, que encerra a série da SEA/SC e muda preços e calendário.",
            "As diferenças com a LOA vêm do escopo: a subação da PC SC inclui combustível e locação; na mesma natureza, empenho, OS e proposta ficam próximos.",
            "A LOA só isola a frota em poucas subações; para os demais órgãos, a comparação precisa do empenho por subelemento.",
            f"O PCA oficial de 2026 da SEA/SC (PCA-E 2026.pdf) planeja {mi(90677641.68)} em locação veicular; a manutenção mecânica da frota própria corre no contrato continuado (QFrotas), e a validação estrita da hipótese E3 depende da extração censitária de 2026."]
    return {"paragrafos": P_, "tabela": (cab, linhas), "conclusoes": conc, "figura": FIG, "mes_fim": mf}


def html_bloco(nivel="h3", fig_caption="Execução da manutenção da frota em 2024–2026 e subações da LOA 2026."):
    c = conteudo()
    if not c:
        return ""
    e = html.escape
    H = []
    for t, p in c["paragrafos"]:
        H.append(f"<p><b>{e(t)}.</b> {e(p)}</p>")
    cab, linhas = c["tabela"]
    td = "style='text-align:left;hyphens:none;font-size:8.5pt'"
    H.append("<table style='width:100%;border-collapse:collapse'><tr>" + "".join(f"<th {td}>{e(x)}</th>" for x in cab) + "</tr>" +
             "".join("<tr>" + "".join(f"<td {td}>{e(x).replace('R$ ', 'R$&nbsp;')}</td>" for x in l) + "</tr>"
                     for l in linhas) + "</table>")
    H.append(f"<div style='page-break-inside:avoid'><img style='width:100%' src='{c['figura'].as_uri()}'>"
             f"<p style='font-size:8.5pt;text-align:center'>{e(fig_caption)} Fonte: empenhos SEF/SC; LOA 2026; experimento.</p></div>")
    if FIG_PCA.exists():
        H.append(f"<div style='page-break-inside:avoid;margin-top:12pt'><img style='width:100%' src='{FIG_PCA.as_uri()}'>"
                 f"<p style='font-size:8.5pt;text-align:center'><b>Figura 6A.4 – Comparativo entre PCA Real 2026 (Locação SEA/SC) e Estimado pelo Experimento (Manutenção Própria).</b> Fonte: PCA-E 2026 (SEA/SC); dados censitários e SEF/SC.</p></div>")
    if FIG_PCA_2025.exists():
        H.append(f"<div style='page-break-inside:avoid;margin-top:12pt'><img style='width:100%' src='{FIG_PCA_2025.as_uri()}'>"
                 f"<p style='font-size:8.5pt;text-align:center'><b>Figura 6A.5 – Exercício 2025: Modelo Treinado até Dez/2024 vs. PCA 2025 Oficial (SEA/SC).</b> Fonte: PCA 2025 (SEA/SC); experimento e balanço SEF/SC.</p></div>")
    if FIG_PCA_BIENAL.exists():
        H.append(f"<div style='page-break-inside:avoid;margin-top:12pt'><img style='width:100%' src='{FIG_PCA_BIENAL.as_uri()}'>"
                 f"<p style='font-size:8.5pt;text-align:center'><b>Figura 6A.6 – Evolução Bienal: PCA Oficial (Locação) vs. Modelo Prescritivo (Manutenção da Frota Própria).</b> Fonte: PCA 2025, PCA-E 2026 (SEA/SC) e modelos do experimento.</p></div>")
    if FIG_PROJECAO.exists():
        H.append(f"<div style='page-break-inside:avoid;margin-top:12pt'><img style='width:100%' src='{FIG_PROJECAO.as_uri()}'>"
                 f"<p style='font-size:8.5pt;text-align:center'><b>Figura 6A.7 – Projeção de Gastos de Frotas (2022–2029) e Análise de Vantajosidade Econômica (Frota Própria vs. Locação).</b> Fonte: Séries históricas SEF/SC, PCA-E SEA/SC e modelos preditivos/prescritivos.</p></div>")
    return "\n".join(H)


def _tex(s):
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("–", "--"), ("“", "``"), ("”", "''"), ("…", r"\ldots{}"), ("≥", r"$\geq$"), ("×", r"$\times$")):
        s = s.replace(a, b)
    return s


def latex_bloco():
    c = conteudo()
    if not c:
        return ""
    T = []
    for t, p in c["paragrafos"]:
        T.append(f"\\paragraph{{{_tex(t)}.}} {_tex(p)}\n")
    cab, linhas = c["tabela"]
    T += ["\\begin{table}[H]", "\\centering\\scriptsize",
          "\\caption{Manutenção da frota: empenho, OS da SEA/SC e proposta do experimento}", "\\label{tab:loa-execucao}",
          "\\begin{tabular}{p{0.30\\textwidth}p{0.13\\textwidth}p{0.15\\textwidth}p{0.13\\textwidth}p{0.17\\textwidth}}", "\\hline",
          " & ".join(f"\\textbf{{{_tex(x)}}}" for x in cab) + " \\\\ \\hline"]
    T += [" & ".join(_tex(x) for x in l) + " \\\\" for l in linhas]
    T += ["\\hline", "\\end{tabular}", "\\fonte{Empenhos SEF/SC (dados.sc.gov.br); OS da SEA/SC; elaborado pelo autor (2026).}", "\\end{table}"]
    return "\n".join(T)

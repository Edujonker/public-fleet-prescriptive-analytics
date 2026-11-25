#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador do Relatório de Qualificação de Pesquisa em PDF
Lê o documento estruturado HTML e renderiza o PDF com o motor WeasyPrint.
Gera o arquivo 'qualificacao_de_pesquisa.pdf' e cópias em relatorios_pdf/ e Documentos/.
"""

import os
import sys
import shutil
from pathlib import Path
import weasyprint

import sys as _sys_ia; from pathlib import Path as _P_ia; _sys_ia.path.insert(0, str(_P_ia(__file__).resolve().parent))
import uso_etico_ia; uso_etico_ia.ativar()  # seção "Uso ético de inteligência artificial" em todo PDF
BASE_DIR = Path(__file__).resolve().parent.parent
HTML_FILE = BASE_DIR / "relatorios" / "qualificacao_pesquisa.html"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_DIR = BASE_DIR / "Documentos"

for d in [PDF_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Seções acrescentadas na compilação, com números lidos dos resultados.
# Se um arquivo de resultado não existir, a subseção correspondente é omitida.
# ---------------------------------------------------------------------------
import json
import csv
import html as _html
from datetime import date


def _json(rel):
    p = BASE_DIR / rel
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    except Exception:
        return None


def _br(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _mi(x):
    return "R$ " + _br(x / 1e6, 2) + " mi"


def _pct(x, nd=1):
    return _br(100 * x, nd) + "%"


def _tab(cab, linhas):
    e = _html.escape
    return ("<table style='width:100%;border-collapse:collapse;font-size:9pt;margin:4pt 0 10pt'><tr>"
            + "".join(f"<th style='background:#1b3a6e;color:#fff;text-align:left;padding:3pt 5pt'>{e(c)}</th>" for c in cab) + "</tr>"
            + "".join("<tr>" + "".join(f"<td style='border-bottom:.5pt solid #c5cfdf;padding:2.5pt 5pt'>{c}</td>" for c in l) + "</tr>" for l in linhas)
            + "</table>")


def _img(rel, leg):
    p = BASE_DIR / rel
    if not p.exists():
        return ""
    return (f"<div style='text-align:center;margin:6pt 0 10pt;page-break-inside:avoid'><img src='{p.as_uri()}' style='width:92%'>"
            f"<p style='font-size:8.5pt;margin:2pt 0'><b>{_html.escape(leg)}</b> Fonte: elaborado pelo autor (2026).</p></div>")


def secao_desenvolvimentos() -> str:
    e = _html.escape
    H = ["<h1>6A. EXPERIMENTAÇÕES E ANÁLISES EM ANDAMENTO</h1>",
         f"<p>Esta seção consolida as experimentações metodológicas em andamento no percurso de pesquisa, detalhando o comportamento "
         f"dos algoritmos e os porquês das decisões experimentais. Os números são apurados diretamente a partir dos registros experimentais "
         f"na data da compilação ({date.today().strftime('%d/%m/%Y')}); cada subseção explicita o pipeline analítico e as fontes de dados de origem.</p>"]

    # ---- quadro oficial das hipóteses (fonte única: scripts/hipoteses_oficiais.py)
    try:
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        import hipoteses_oficiais as _h
        H += ["<h2>6A.0 Avaliação preliminar das hipóteses de pesquisa</h2>",
              "<p>Cada hipótese de pesquisa foi avaliada à luz dos critérios formais pré-estabelecidos no delineamento metodológico: "
              "o critério conceitual do anteprojeto e o limiar quantitativo pré-registrado para a qualificação. "
              "A classificação como SUSTENTADA, PARCIALMENTE SUSTENTADA ou NÃO SUSTENTADA reflete o comportamento empírico observado nas "
              "fases iniciais de teste, permitindo investigar as razões subjacentes aos dados antes da modelagem final da dissertação. "
              "Os testes comparativos e os ajustes de validação temporal constam em <code>docs/hipoteses/desvios_do_protocolo.md</code>.</p>",
              _h.bloco_html(),
              "<p><b>Hipóteses exploratórias.</b> Três hipóteses surgiram da análise e foram pré-registradas em 15/11/2026 para teste "
              "confirmatório na extração de 2026 da SEA/SC, ainda não recebida: E1 (estrutura de comunidades e concentração do mercado de "
              "oficinas), E2 (o detector de anomalias não captura as glosas) e E3 (a proposta de LOA 2026 erra menos de 10% no total). "
              "Documento: <code>docs/hipoteses/preregistro_hipoteses_exploratorias_2026.md</code>.</p>"]
    except Exception as ex:  # o restante da seção continua sem o quadro
        print("Aviso: quadro de hipóteses não incluído:", ex)

    # ---- revisão sistemática
    P = _json("revisao_sistematica/resultados_prisma.json")
    if P:
        val = BASE_DIR / "revisao_sistematica/dados/09_validacao_avaliador.csv"
        nval = 0
        if val.exists():
            with open(val, encoding="utf-8-sig") as f:
                nval = sum(1 for r in csv.DictReader(f, delimiter=";") if (r.get("decisao_avaliador") or "").strip())
        inc = P["incluidos"]
        H += ["<h2>6A.1 Revisão sistemática da literatura (PRISMA 2020)</h2>",
              f"<p>O protocolo da Pesquisa Bibliográfica Sistemática foi executado por <code>scripts/rsl_prisma.py</code>, com data-limite de "
              f"{e(P['data_limite_protocolo'])}. Foram identificados {_br(sum(P['identificados'].values()))} registros (bases: Scopus e IEEE Xplore; "
              f"outros métodos: bibliotecas de referências, Periódicos CAPES e busca OpenAlex + Semantic Scholar), buscados "
              f"{_br(P['textos_buscados'])} textos completos e incluídos <b>{_br(P['n_incluidos'])} estudos</b> "
              f"({inc.get('bases', 0)} de bases, {inc.get('outros', 0)} de outros métodos e {inc.get('snowballing', 0)} por snowballing). "
              f"Para esta qualificação, a base bibliográfica é a revisão estruturada de 40 obras da seção 3.4. A triagem automatizada do protocolo PRISMA está concluída; "
              f"a validação humana dos estudos incluídos e a síntese qualitativa são etapas entre a qualificação e a defesa.</p>",
              f"<p>A triagem foi feita por regras derivadas dos critérios do protocolo, e as decisões são provisórias até a validação do avaliador "
              f"único: {nval} de {_br(P['n_incluidos'])} inclusões conferidas até esta compilação. Desvios registrados: a ACM Digital Library não foi "
              f"exportada, e as consultas exatas submetidas à Scopus e ao IEEE Xplore ainda precisam ser arquivadas. O protocolo, os desvios e o registro "
              f"de cada documento incorporado estão em <code>revisao_sistematica/protocolo_sigma.pdf</code>; o fluxo e o mapeamento, em "
              f"<code>revisao_sistematica/relatorio_revisao_sistematica.pdf</code>.</p>"]

    # ---- grafo
    G = _json("dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json")
    C = _json("dissertacao_frotas/resultados/logs/relatorio_neo4j_grafo.json")
    if G and C:
        T, A = G["testes"], G["analises"]
        a1, a2, a3 = A["A1_estabilidade_louvain"], A["A2_modelo_nulo"], A["A3_concentracao"]
        sp = A["A4_centralidade_vs_auditoria"]["spearman"]
        kw = A["A4_centralidade_vs_auditoria"]["kruskal_glosa_entre_comunidades"]
        vc = C["verified_neo4j_counts"]
        ok = lambda t: "aprovado" if t["aprovado"] else "<b>reprovado</b>"
        H += ["<h2>6A.2 Grafo veículo–oficina em Neo4j: testes e validação das comunidades</h2>",
              f"<p>A rede de {_br(vc['vehicle_count'])} veículos e {_br(vc['workshop_count'])} oficinas foi persistida em Neo4j local, com identificadores "
              f"pseudonimizados por HMAC-SHA-256 (<code>graphdb/load_graph.py</code>). O script <code>scripts/analise_grafos_frotas.py</code> lê o grafo do banco e "
              f"testa a carga e as comunidades. O resultado de Louvain da seção 6.5 foi reproduzido e passou a ter um teste de significância que antes não existia.</p>",
              _tab(["Teste / análise", "Resultado"], [
                  ["T1 – contagens do Neo4j iguais às da carga", ok(T["T1_integridade"])],
                  ["T2 – projeção oficina–oficina recalculada", f"{ok(T['T2_projecao'])} ({_br(T['T2_projecao']['arestas_gravadas'])} arestas, {T['T2_projecao']['pesos_divergentes']} pesos divergentes)"],
                  ["T3 – Louvain reproduz o pipeline", f"{ok(T['T3_reproducao_etapa06'])} (Q = {_br(T['T3_reproducao_etapa06']['neo4j']['modularidade_louvain_q'], 4)})"],
                  ["Q observado × 30 redes nulas com os mesmos graus", f"{_br(a2['Q_observado'], 3)} × {_br(a2['Q_nulo_media'], 3)} ± {_br(a2['Q_nulo_dp'], 3)} (z = {_br(a2['z'], 1)})"],
                  ["Estabilidade em 30 sementes", f"{a1['comunidades_min']}–{a1['comunidades_max']} comunidades; ARI médio {_br(a1['ARI_vs_seed42_media'], 3)}"],
                  ["Concentração do gasto", f"10% das oficinas recebem {_pct(a3['participacao_top10pct_oficinas'])}; Gini {_br(a3['gini_gasto'], 2)}"],
                  ["Centralidade × taxa de anomalia (Spearman)", _br(sp["intermediacao~taxa_anomalia"]["rho"], 3)],
                  ["Centralidade × frequência de glosa (Spearman)", f"{_br(sp['intermediacao~taxa_glosa']['rho'], 3)} (p = {_br(sp['intermediacao~taxa_glosa']['p'], 2)})"],
                  ["Glosa entre comunidades (Kruskal–Wallis)", f"p = {_br(kw['p'], 2)}"],
              ]),
              _img("dissertacao_frotas/resultados/figuras/grafos_modelo_nulo_e_concentracao.png",
                   "Figura 6A.1 – Modularidade observada contra redes nulas e concentração do gasto por oficina."),
              "<p>Conclusão: a estrutura de comunidades é real e estável, e o gasto se concentra em poucas oficinas. A posição na rede, porém, não se associa "
              "à frequência de glosas, de modo que o grafo serve para descrever o mercado e montar amostras de auditoria, não para apontar irregularidades. "
              "Esses resultados deram origem ao artigo <code>SBC/artigo5_grafos_gestao_frotas_sbc.tex</code> e à seção 10.x da dissertação.</p>"]

    # ---- LOA e PCA
    L = _json("resultados_loa_pca_2026/resultado_experimento.json")
    if L:
        esc = L["modelo_escolhido"]
        inc = L["incerteza_2026"].get(esc) or next(iter(L["incerteza_2026"].values()))
        bt = L["avaliacao_retrospectiva"]
        linhas_bt = [[e(b), e(k), _mi(v["previsto"]), _mi(v["realizado"]), _br(100 * v["erro_total_pct"], 1) + "%"]
                     for b, d in bt.items() for k, v in d.items() if k == esc]
        loa_csv = BASE_DIR / "resultados_loa_pca_2026/proposta_loa_2026_por_orgao.csv"
        top_org = []
        if loa_csv.exists():
            with open(loa_csv, encoding="utf-8") as f:
                for i, r in enumerate(csv.DictReader(f, delimiter=";")):
                    if i >= 6:
                        break
                    top_org.append([e(r["orgao"]), _pct(float(r["participacao"].replace(",", ".")), 1), _mi(float(r["proposta_2026"].replace(",", ".")))])
        a25 = L["ano_2025_observado_mais_presumido"]
        H += ["<h2>6A.3 Experimento de planejamento: LOA e PCA 2026 da manutenção da frota</h2>",
              f"<p>O experimento (<code>scripts/planejamento_loa_pca_2026.py</code>) usa só dados observados até {e(L['corte'])} para propor a dotação de 2026. "
              f"A extração da SEA/SC tem cobertura completa até esse mês; depois dele há poucas OS por mês, e os empenhos (6A.3.1) mostram que esse mês coincide com a troca do contrato de manutenção. Os meses de out–dez/2025 "
              f"foram presumidos pelo modelo e aparecem destacados. Para medir a qualidade do método, os mesmos modelos foram treinados até dez/2023 (previsão de 2024) "
              f"e até dez/2024 (previsão de jan–set/2025), e o escolhido foi o de menor erro no total: <b>{e(esc)}</b>, com erro médio de "
              f"{_pct(L['erro_medio_abs_total'][esc])}.</p>",
              _tab(["Teste retrospectivo", "Modelo", "Previsto", "Realizado", "Erro no total"], linhas_bt),
              _tab(["Período", "Valor"], [["2022 realizado", _mi(L["realizado_anual"]["2022"])], ["2023 realizado", _mi(L["realizado_anual"]["2023"])],
                                          ["2024 realizado", _mi(L["realizado_anual"]["2024"])], ["2025 observado + presumido", _mi(a25)],
                                          [f"<b>2026 proposta ({e(esc)})</b>", f"<b>{_mi(L['total_2026'])}</b> (intervalo de 80%: {_mi(inc['10'])} a {_mi(inc['90'])})"]]),
              _img("resultados_loa_pca_2026/fig_serie_previsao.png", "Figura 6A.2 – Série mensal observada, meses presumidos e previsão de 2026."),
              f"<p>A proposta foi distribuída por órgão pela participação dos 12 meses mais recentes (teste em 2024: erro de {_pct(L['teste_distribuicao_orgaos_2024'])}) "
              f"e dividida em peças ({_pct(L['participacao_pecas']['ultimos_12_meses'])}) e mão de obra. O PCA proposto lista as 40 descrições de peça de maior gasto, que "
              f"cobrem {_pct(L['pca_cobertura_top40'])} das peças; {L['teste_pca_itens_2024']['itens_top40_2024_ja_no_top40_2023']} dos 40 maiores itens de 2024 já estavam "
              f"entre os 40 maiores de 2023.</p>",
              _tab(["Órgão", "Participação", "Proposta 2026"], top_org) if top_org else "",
              "<h3>6A.3.1 Confronto com a LOA, o PCA e a execução de 2026</h3>"]
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        import comparacao_loa_execucao as _cmp
        _bl = _cmp.html_bloco(fig_caption="Figura 6A.3 – Empenho acumulado de manutenção (2024–2026) contra a proposta do experimento, e subações da LOA 2026 que isolam a frota.")
        H += [_bl or "<p>A comparação com a execução depende de <code>scripts/execucao_orcamentaria_frota.py</code>.</p>",
              "<p>O relatório completo está em <code>relatorio_loa_pca_2026.pdf</code> e o texto correspondente da dissertação, na seção 7.1 "
              "(<code>Textuais/Secao07_PlanejamentoLOA_PCA.tex</code>).</p>"]

    # ---- BPM
    bpm = sorted((BASE_DIR / "docs/bpm").glob("*.bpmn")) if (BASE_DIR / "docs/bpm").exists() else []
    if bpm:
        H += ["<h2>6A.4 Mapeamento de processos (BPMN 2.0)</h2>",
              f"<p>Os processos do projeto foram mapeados em BPMN 2.0 por <code>scripts/gerar_mapeamento_bpm.py</code>: {len(bpm)} processos, da cadeia de valor "
              "ao pipeline científico, à busca diária de literatura, à revisão PRISMA, ao grafo, à atualização dos relatórios, ao atendimento de requisições "
              "na API e à publicação. Cada tarefa aponta para o script que a executa, e o gerador confere esses arquivos no disco. Os modelos ficam em "
              "<code>docs/bpm/*.bpmn</code> e a documentação em <code>mapeamento_bpm_projeto.pdf</code>.</p>"]
        svg = BASE_DIR / "docs/bpm/P00_cadeia_valor.svg"
        if svg.exists():
            H.append(f"<div style='margin:6pt 0 10pt'><img src='{svg.as_uri()}' style='width:100%'><p style='font-size:8.5pt;text-align:center'>"
                     "<b>Figura 6A.4 – Cadeia de valor do projeto (BPMN).</b> Fonte: elaborado pelo autor (2026).</p></div>")

    # ---- correções e infraestrutura
    H += ["<h2>6A.5 Correções e infraestrutura de reprodutibilidade</h2><ul>",
          "<li>O script do MILP descartava o resultado do solver e usava custos fixos. Agora a economia da seção 6.4 é calculada pelo HiGHS e comparada "
          "com a prática reconstruída e com uma heurística gulosa.</li>",
          "<li>O pré-processamento lia os valores patrimoniais cerca de mil vezes menores; a ablação de H1 estava digitada; a figura local SHAP × LIME "
          "usava LIME simulado; a etapa 09 lia uma chave errada; o número de veículos antieconômicos era limitado entre 313 e 427 (o valor real é 242). "
          "Todos foram corrigidos, e os resultados acima já refletem as correções.</li>",
          "<li>O critério de 40% foi conferido no Decreto MG nº 47.539, de 23/11/2018: está no art. 44 e considera as manutenções dos últimos doze meses e o valor de "
          "mercado usado no IPVA. O cálculo do projeto usa todo o período e valor contábil ou estimado; essa diferença precisa ser tratada antes da defesa.</li>",
          "<li>Busca diária de literatura com agendamento automático, atualização dos relatórios sem supervisão com comparação de métricas contra backup, e o "
          "relatório <code>PBS.pdf</code>, que inventaria scripts, bases, APIs e pendências a partir dos arquivos.</li></ul>"]
    return "\n".join(H)


def injetar_desenvolvimentos(html_content: str) -> str:
    marca = "<h1>7. CRONOGRAMA DE ATIVIDADES ATÉ A DEFESA FINAL</h1>"
    if marca not in html_content:
        print("Aviso: marcador da seção 7 não encontrado; desenvolvimentos não inseridos.")
        return html_content
    nota_34 = ("<p style='background:#f4f6fb;border-left:3pt solid #1b3a6e;padding:5pt 8pt;font-size:9.5pt'>Atualização: além desta matriz, "
               "foi executada a revisão sistemática completa descrita na seção 6A.1.</p>")
    h34 = "<h2>3.4 Matriz Crítica da Revisão Bibliográfica (40 Obras Mapeadas)</h2>"
    html_content = html_content.replace(h34, h34 + nota_34, 1)
    return html_content.replace(marca, secao_desenvolvimentos() + "\n" + marca, 1)


def compilar_pdf():
    print("=" * 75)
    print("COMPILAÇÃO DO RELATÓRIO DE QUALIFICAÇÃO DE PESQUISA EM PDF")
    print("Programa de Pós-Graduação em Computação Aplicada (PPGCAP / UDESC)")
    print("Autor: Eduardo Lopes Jonker")
    print("=" * 75)

    if not HTML_FILE.exists():
        print(f"Erro: Arquivo HTML não encontrado em: {HTML_FILE}")
        sys.exit(1)

    print(f"1. Lendo arquivo HTML estruturado: {HTML_FILE.name}...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Nomes e caminhos de saída
    pdf_solicitado = BASE_DIR / "qualificacao_de_pesquisa.pdf"
    pdf_relatorios = PDF_DIR / "qualificacao_de_pesquisa.pdf"
    pdf_documentos = DOCS_DIR / "qualificacao_de_pesquisa.pdf"

    html_content = injetar_desenvolvimentos(html_content)

    print("2. Renderizando PDF com WeasyPrint Engine...")
    weasyprint.HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(str(pdf_solicitado))
    
    tamanho_mb = pdf_solicitado.stat().st_size / (1024 * 1024)
    print(f"✓ PDF gerado com sucesso com nome exato solicitado: {pdf_solicitado.name}")
    print(f"  Tamanho: {tamanho_mb:.2f} MB")

    print("3. Criando cópias espelhadas de segurança e padronização...")
    shutil.copy2(pdf_solicitado, pdf_relatorios)
    shutil.copy2(pdf_solicitado, pdf_documentos)
    print(f"✓ Cópia espelhada em: {pdf_relatorios}")
    print(f"✓ Cópia espelhada em: {pdf_documentos}")

    print("=" * 75)
    print("COMPILAÇÃO DO RELATÓRIO DE QUALIFICAÇÃO CONCLUÍDA COM 100% DE SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    compilar_pdf()

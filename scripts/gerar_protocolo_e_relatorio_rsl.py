#!/usr/bin/env python3
"""
Mantém o protocolo da Pesquisa Bibliográfica Sistemática (PBS) e o relatório da revisão.

1. Atualiza revisao_sistematica/registro_incorporacoes.csv (só acrescenta linhas):
   cada arquivo-fonte, texto completo recuperado, estudo incluído, PDF manual (CAFe)
   e artigo novo da busca diária entra uma única vez, com data, MD5 e situação no
   fluxo PRISMA. Itens obtidos depois da data-limite do protocolo são registrados
   como "fora do fluxo" (candidatos a uma atualização da revisão), sem alterar o fluxo.
2. Gera revisao_sistematica/protocolo_sigma.pdf: protocolo, desvios e registro de incorporações.
3. Gera revisao_sistematica/relatorio_revisao_sistematica.pdf: fluxo PRISMA 2020,
   mapeamento por pergunta, qualidade e lista dos estudos incluídos.

Lê: revisao_sistematica/resultados_prisma.json e revisao_sistematica/dados/*.csv
(produzidos por scripts/rsl_prisma.py). Rodar depois dele.
Uso: .venv/bin/python scripts/gerar_protocolo_e_relatorio_rsl.py
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import weasyprint

ROOT = Path(__file__).resolve().parent.parent
RS = ROOT / "revisao_sistematica"
DADOS = RS / "dados"
REG = RS / "registro_incorporacoes.csv"
PROTOCOLO_ORIG = ROOT / "Metodologia de Pesquisa" / "protocolo_pesquisa_bibliografica_sistematica.pdf"
CAMPOS = ["n", "data_registro", "tipo", "chave", "descricao", "origem", "arquivo", "md5", "registros", "situacao_fluxo"]
e = html.escape


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:12]


def ler(p: Path, sep=";"):
    if not p.exists():
        return []
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=sep))


def br(n) -> str:
    return f"{int(n):,}".replace(",", ".")


# ------------------------------------------------------------ registro
def atualizar_registro(P: dict) -> tuple[list[dict], int]:
    linhas = ler(REG)
    vistos = {(l["tipo"], l["chave"]) for l in linhas}
    limite = P.get("data_limite_protocolo", "2026-11-14")
    hoje = date.today().isoformat()
    novos = []

    def add(tipo, chave, descricao, origem="", arquivo="", md="", registros="", situacao=""):
        if (tipo, chave) in vistos:
            return
        vistos.add((tipo, chave))
        novos.append({"data_registro": hoje, "tipo": tipo, "chave": chave, "descricao": descricao[:200],
                      "origem": origem, "arquivo": arquivo, "md5": md, "registros": registros, "situacao_fluxo": situacao})

    for i in P.get("inventario", []):
        arq = i.get("arquivo", "")
        dt = (i.get("data_arquivo") or "")[:10]
        sit = "no fluxo PRISMA (identificação)" if not dt or dt <= limite else "após a data-limite: fora do fluxo"
        add("fonte de busca", f"{i['fonte']}|{arq}|{i.get('md5', '')}", i.get("observacao") or i["fonte"],
            "base de dados" if i["grupo"] == "bases" else "outros métodos", arq, i.get("md5", ""), str(i.get("registros", "")), sit)

    for r in ler(DADOS / "06_07_texto_completo_elegibilidade.csv"):
        if r.get("recuperacao") == "recuperado" and r.get("pdf"):
            add("texto completo recuperado", r["id"], r["titulo"], r.get("fontes", ""), r["pdf"], "", "", f"elegibilidade: {r.get('elegibilidade', '')}")
    for r in ler(DADOS / "08_snowballing.csv"):
        if r.get("recuperacao") == "recuperado":
            add("texto completo recuperado", r["id"], r["titulo"], r.get("fonte", ""), "", "", "", f"snowballing; elegibilidade: {r.get('elegibilidade', '')}")

    for r in ler(DADOS / "09_extracao_qualidade.csv"):
        add("estudo incluído", r["id"], r["titulo"], r.get("grupo", ""), "", "", "", f"incluído (Q = {r.get('Q_total', '')}); validação do avaliador pendente")

    manual = RS / "textos_completos" / "PDF_manual_CAFe"
    for p in sorted(manual.glob("*.pdf")) if manual.exists() else []:
        add("PDF manual (CAFe)", p.name, p.stem, "acesso institucional", str(p.relative_to(ROOT)), md5(p), "", "aguarda casamento com registro do fluxo")

    exp = ROOT / "Metodologia de Pesquisa" / "exportacoes_capes"
    for p in sorted(exp.iterdir()) if exp.exists() else []:
        if p.suffix.lower() in (".ris", ".csv", ".bib", ".txt", ".enw") and p.name != "registro_buscas.csv":
            dt = datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()
            add("exportação manual", f"{p.name}|{md5(p)}", p.name, "exportacoes_capes", str(p.relative_to(ROOT)), md5(p), "",
                "no fluxo PRISMA" if dt <= limite else "após a data-limite: fora do fluxo")

    atual = ROOT / "artigos" / "atualizacoes"
    for d in sorted(atual.iterdir()) if atual.exists() else []:
        for r in ler(d / "novos.csv"):
            chave = (r.get("doi") or r.get("titulo", "")).strip().lower()
            if chave:
                add("artigo da busca diária", chave, r.get("titulo", ""), f"OpenAlex/S2, {d.name}", r.get("arquivo_pdf", ""), "", "",
                    "após a data-limite: fora do fluxo (candidato à atualização)" if d.name > limite else "no período da busca, fora do fluxo PRISMA")

    base = len(linhas)
    for k, l in enumerate(novos, start=base + 1):
        l["n"] = str(k)
    linhas += novos
    with open(REG, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
        w.writeheader()
        w.writerows(linhas)
    return linhas, len(novos)


# ------------------------------------------------------------ HTML comum
CSS = """
@page { size: A4; margin: 2cm 1.8cm; @bottom-right { content: counter(page) " / " counter(pages); font: 8.5pt Arial; color:#555; }
        @bottom-left { content: string(doc); font: 8.5pt Arial; color:#555; } }
body { font-family: Arial, sans-serif; font-size: 10pt; line-height: 1.42; color:#1d1d1d; }
.doc { string-set: doc content(); display:none; }
h1 { color:#00693e; font-size: 18pt; margin: 0 0 4pt; } .sub { color:#444; margin: 0 0 14pt; }
h2 { color:#00693e; font-size: 13pt; border-bottom: 1.5pt solid #00693e; padding-bottom: 2pt; margin: 16pt 0 6pt; }
h3 { font-size: 10.5pt; margin: 10pt 0 3pt; }
table { width:100%; border-collapse: collapse; margin: 4pt 0 10pt; font-size: 8.4pt; }
th { background:#00693e; color:#fff; text-align:left; padding: 3pt 4pt; }
td { border-bottom: .5pt solid #c9d6cf; padding: 2.4pt 4pt; vertical-align: top; }
tr:nth-child(even) td { background:#f3f8f5; }
code, .mono { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.3pt; }
.q { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.4pt; background:#f3f8f5; padding: 6pt 8pt; white-space: pre-wrap; border-left: 3pt solid #00693e; }
.nota { background:#fff7e0; border-left: 3pt solid #d99a00; padding: 5pt 8pt; margin: 6pt 0; font-size: 9pt; }
.kpi { display:flex; flex-wrap:wrap; gap:6pt; margin: 6pt 0 10pt; } .kpi div { flex:1 1 22%; border:1pt solid #00693e; border-radius:3pt; padding:5pt 7pt; }
.kpi b { display:block; font-size: 15pt; color:#00693e; }
.flow { width:100%; border-collapse: separate; border-spacing: 6pt; font-size: 8.6pt; }
.flow td { border: 1pt solid #00693e; border-radius: 3pt; background:#fff; padding: 5pt; vertical-align: middle; }
.flow td.lab { border:none; background:#00693e; color:#fff; font-weight:bold; text-align:center; width: 9%; }
.flow td.x { border-color:#b04a3a; background:#fbf1ef; }
.flow td.vazio { border:none; background:none; }
ul { margin: 3pt 0 8pt 14pt; padding: 0; } li { margin: 2pt 0; }
.small td { font-size: 7.6pt; }
"""


def tab(cab, linhas, cls=""):
    return (f"<table class='{cls}'><tr>" + "".join(f"<th>{e(c)}</th>" for c in cab) + "</tr>"
            + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas) + "</table>")


def contar_rotulos(linhas, campo):
    c = Counter()
    for r in linhas:
        for v in (r.get(campo) or "").split(";"):
            v = v.strip()
            if v and v.lower() not in ("nan", "não identificado", ""):
                c[v] += 1
    return c


# ------------------------------------------------------------ protocolo
def html_protocolo(P, reg, n_novos):
    hoje = date.today().strftime("%d/%m/%Y")
    por_tipo = Counter(l["tipo"] for l in reg)
    por_sit = Counter((l["tipo"], l["situacao_fluxo"].split(":")[0].split(";")[0].split("(")[0].strip()) for l in reg)
    datas = Counter(l["data_registro"] for l in reg)
    h = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><span class='doc'>Protocolo da PBS · registro de incorporações</span>",
         "<h1>Protocolo da Pesquisa Bibliográfica Sistemática (PBS)</h1>",
         f"<p class='sub'>Protocolo, desvios registrados e registro de incorporações · atualizado em {hoje} · "
         f"gerado por <code>scripts/gerar_protocolo_e_relatorio_rsl.py</code></p>",
         "<h2>1. Identificação</h2>",
         tab(["Item", "Valor"], [
             ["Autor e avaliador único", "Eduardo Lopes Jonker (PPGCAP/UDESC)"],
             ["Orientação", "Profa. Dra. Vivian Kremer Kalempa; Prof. Dr. Yuri Kaszubowski Lopes (coorientador)"],
             ["Protocolo original", f"<code>{e(str(PROTOCOLO_ORIG.relative_to(ROOT)))}</code> (MD5 {md5(PROTOCOLO_ORIG) if PROTOCOLO_ORIG.exists() else '—'})"],
             ["Período coberto", "01/01/2020 a 14/11/2026"],
             ["Data-limite da busca", e(P.get("data_limite_protocolo", "—"))],
             ["Última execução do fluxo", e(P.get("data_execucao", "—"))],
             ["Diretrizes", "Kitchenham (2004); Petersen et al. (2008); Wohlin (2014); relato PRISMA 2020"],
         ]),
         "<h2>2. Protocolo (resumo fiel ao documento original)</h2>",
         "<h3>Pergunta primária</h3><p>Que abordagens, técnicas ou arquiteturas de suporte à decisão integram analítica preditiva ou prescritiva "
         "e/ou Mineração de Processos com XAI, e como tratam governança de dados, privacidade e transparência em contextos do setor público?</p>",
         "<h3>Perguntas secundárias</h3><ul>"
         "<li><b>SQ1</b> – problemas decisórios, processos, domínios e técnicas de analítica, otimização ou Mineração de Processos;</li>"
         "<li><b>SQ2</b> – combinação da Mineração de Processos com previsão, prescrição, otimização ou suporte à decisão;</li>"
         "<li><b>SQ3</b> – técnicas de XAI, públicos e formas de validação;</li>"
         "<li><b>SQ4</b> – governança de dados, privacidade, responsabilização, auditabilidade e conformidade;</li>"
         "<li><b>SQ5</b> – evidências, limitações e requisitos de transferência para órgãos públicos.</li></ul>",
         "<h3>Estratégia de busca (título, resumo e palavras-chave)</h3>",
         "<div class='q'>(\"prescriptive analytics\" OR \"predictive analytics\" OR \"decision support\" OR \"decision support system*\" OR "
         "\"process mining\" OR \"process optimization\" OR \"business process*\")\nAND\n(\"explainable artificial intelligence\" OR "
         "\"explainable AI\" OR XAI OR \"interpretable machine learning\" OR \"algorithmic transparency\")\nAND\n(\"data governance\" OR "
         "\"privacy by design\" OR \"data protection\" OR privacy OR accountability OR auditability OR \"public sector\" OR government OR "
         "\"public administration\")</div>",
         "<h3>Fontes, critérios e qualidade</h3>",
         tab(["Elemento", "Definição"], [
             ["Bases", "Scopus, IEEE Xplore e ACM Digital Library; estudos secundários e referências como fontes auxiliares e snowballing"],
             ["CO1–CO5", "duplicatas; inglês ou português; 2020 a 14/11/2026; estudos primários completos com avaliação por pares; "
                         "texto não recuperado registrado à parte, não como exclusão"],
             ["Regra de inclusão", "CI1 (analítica para decisão) E CI2 (explicabilidade) E (CI3 governança/privacidade/auditabilidade OU CI4 contexto público)"],
             ["Seleção", "deduplicação → títulos e resumos → texto completo → decisão final; avaliador único (limitação declarada)"],
             ["Snowballing", "regressivo e progressivo a partir dos incluídos, com origem e estudo-semente registrados"],
             ["Qualidade", "Q1 contexto e dados; Q2 procedimento; Q3 evidência e validação; Q4 XAI e governança; 0–2 cada, sem limiar eliminatório"],
             ["Síntese", "mapeamento descritivo e síntese temática; sem metanálise"],
         ]),
         "<h2>3. Desvios e decisões de execução registrados</h2><ul>",
         "<li><b>ACM Digital Library sem exportação.</b> Uma das três bases previstas não foi consultada até a data-limite.</li>",
         "<li><b>Consultas exatas não arquivadas.</b> As exportações de Scopus e IEEE Xplore estão guardadas (com MD5), mas a consulta efetivamente "
         "submetida, os campos e os filtros ainda precisam ser preenchidos em <code>Metodologia de Pesquisa/exportacoes_capes/registro_buscas.csv</code>.</li>",
         "<li><b>Outros métodos além do previsto.</b> Biblioteca Paperpile, export.ris, Periódicos CAPES (RIS/BibTeX), referências da dissertação e "
         "busca OpenAlex + Semantic Scholar entram como “outros métodos” no PRISMA 2020, separados das bases.</li>",
         "<li><b>Triagem assistida por regras.</b> Critérios aplicados por dicionários de termos e contagem de menções no texto completo "
         "(CI2 ≥ 5; CI1 ≥ 3; CI3/CI4 ≥ 3). As decisões são provisórias até a validação do avaliador "
         "(<code>revisao_sistematica/dados/09_validacao_avaliador.csv</code>).</li>",
         "<li><b>Registros em chinês.</b> Excluídos por CO2; a literatura chinesa é tratada como limitação.</li>",
         "<li><b>Busca diária.</b> Artigos encontrados depois da data-limite são registrados abaixo como fora do fluxo; entram somente se "
         "houver uma atualização formal da revisão, com nova data-limite.</li></ul>",
         "<h2>4. Registro de incorporações</h2>",
         f"<p>Arquivo <code>revisao_sistematica/registro_incorporacoes.csv</code>, só com acréscimos: {br(len(reg))} entradas, "
         f"{br(n_novos)} adicionadas nesta atualização. Cada item entra uma vez, identificado pelo tipo e por uma chave "
         f"(arquivo + MD5, identificador do registro ou DOI).</p>",
         tab(["Tipo", "Situação no fluxo", "Itens"],
             [[e(t), e(s), br(n)] for (t, s), n in sorted(por_sit.items())]),
         "<h3>Fontes de busca e exportações incorporadas</h3>",
         tab(["Nº", "Data", "Fonte / arquivo", "Grupo", "Registros", "MD5", "Situação"],
             [[l["n"], l["data_registro"], e(l["descricao"]) + "<br><span class='mono'>" + e(l["arquivo"]) + "</span>", e(l["origem"]),
               e(l["registros"]), f"<span class='mono'>{e(l['md5'])}</span>", e(l["situacao_fluxo"])]
              for l in reg if l["tipo"] in ("fonte de busca", "exportação manual", "PDF manual (CAFe)")], "small"),
         "<h3>Últimas 40 incorporações</h3>",
         tab(["Nº", "Data", "Tipo", "Título / descrição", "Situação"],
             [[l["n"], l["data_registro"], e(l["tipo"]), e(l["descricao"][:120]), e(l["situacao_fluxo"][:70])] for l in reg[-40:]], "small"),
         "<h3>Histórico de atualizações</h3>",
         tab(["Data do registro", "Itens incorporados"], [[d, br(n)] for d, n in sorted(datas.items())]),
         "</body></html>"]
    return "\n".join(h)


# ------------------------------------------------------------ relatório
def caixa(t, n, x=False):
    return f"<td class='{'x' if x else ''}'><b>{e(t)}</b><br>{n}</td>"


def html_relatorio(P):
    hoje = date.today().strftime("%d/%m/%Y")
    ex = ler(DADOS / "09_extracao_qualidade.csv")
    val = ler(DADOS / "09_validacao_avaliador.csv")
    n_val = sum(1 for v in val if (v.get("decisao_avaliador") or "").strip())
    ident = P["identificados"]
    id_b = sum(v for k, v in ident.items() if k.startswith("bases|"))
    id_o = sum(v for k, v in ident.items() if k.startswith("outros|"))
    dup, uni = P["duplicatas"], P["unicos"]
    co, tri, rec, ele = P["co"], P["triagem"], P["recuperacao"], P["elegibilidade"]
    sb_id, sb_co, sb_tr, sb_rec, sb_el = (P["snowball_identificados"], P["snowball_co"], P["snowball_triagem"],
                                          P["snowball_recuperacao"], P["snowball_elegibilidade"])
    inc = P["incluidos"]

    def excl(d, chave_ok):
        return sum(v for k, v in d.items() if not k.startswith(chave_ok))

    def lista(d, pref="excluído"):
        return "<br>".join(f"{e(k.replace('excluído: ', ''))}: {br(v)}" for k, v in sorted(d.items(), key=lambda x: -x[1]) if k.startswith(pref) or k.startswith("CO"))

    def coluna(g):
        return {
            "id": id_b if g == "bases" else id_o,
            "dup": dup.get(g, 0), "uni": uni.get(g, 0),
            "co_ex": excl(co.get(g, {}), "aprovado"), "co_l": lista(co.get(g, {}), "CO"),
            "tri": co.get(g, {}).get("aprovado", 0), "tri_ex": excl(tri.get(g, {}), "segue"), "tri_l": lista(tri.get(g, {})),
            "busc": sum(v for k, v in tri.get(g, {}).items() if k.startswith("segue")), "nrec": rec.get(g, {}).get("nao_recuperado", 0),
            "aval": rec.get(g, {}).get("recuperado", 0),
            "el_ex": sum(v for k, v in ele.get(g, {}).items() if k.startswith("excluído")), "el_l": lista(ele.get(g, {})),
            "inc": inc.get(g, 0)}
    b, o = coluna("bases"), coluna("outros")
    sb_busc = sum(v for k, v in sb_tr.items() if k.startswith("segue"))
    fluxo = f"""<table class='flow'>
<tr><td class='lab'>Identificação</td>{caixa('Bases de dados (Scopus, IEEE Xplore)', f'n = {br(b["id"])}')}
{caixa('Duplicatas removidas', f'n = {br(b["dup"])}', True)}{caixa('Outros métodos (bibliotecas, CAPES, OpenAlex/S2)', f'n = {br(o["id"])}')}
{caixa('Duplicatas removidas (inclui ' + br(P.get('duplicatas_entre_grupos', 0)) + ' entre grupos)', f'n = {br(o["dup"])}', True)}</tr>
<tr><td class='lab'>Triagem</td>{caixa('Registros únicos', f'n = {br(b["uni"])}')}{caixa('Excluídos por critérios objetivos', f'n = {br(b["co_ex"])}<br><small>{b["co_l"]}</small>', True)}
{caixa('Registros únicos', f'n = {br(o["uni"])}')}{caixa('Excluídos por critérios objetivos', f'n = {br(o["co_ex"])}<br><small>{o["co_l"]}</small>', True)}</tr>
<tr><td class='lab'></td>{caixa('Títulos e resumos triados', f'n = {br(b["tri"])}')}{caixa('Excluídos na triagem', f'n = {br(b["tri_ex"])}<br><small>{b["tri_l"]}</small>', True)}
{caixa('Títulos e resumos triados', f'n = {br(o["tri"])}')}{caixa('Excluídos na triagem', f'n = {br(o["tri_ex"])}<br><small>{o["tri_l"]}</small>', True)}</tr>
<tr><td class='lab'></td>{caixa('Textos completos buscados', f'n = {br(b["busc"])}')}{caixa('Não recuperados', f'n = {br(b["nrec"])}', True)}
{caixa('Textos completos buscados', f'n = {br(o["busc"])}')}{caixa('Não recuperados', f'n = {br(o["nrec"])}', True)}</tr>
<tr><td class='lab'></td>{caixa('Avaliados para elegibilidade', f'n = {br(b["aval"])}')}{caixa('Excluídos após leitura', f'n = {br(b["el_ex"])}<br><small>{b["el_l"]}</small>', True)}
{caixa('Avaliados para elegibilidade', f'n = {br(o["aval"])}')}{caixa('Excluídos após leitura', f'n = {br(o["el_ex"])}<br><small>{o["el_l"]}</small>', True)}</tr>
<tr><td class='lab'>Snowballing</td>{caixa('Identificados', f'regressivo {br(sb_id.get("Snowballing regressivo", 0))}; progressivo {br(sb_id.get("Snowballing progressivo", 0))}')}
{caixa('Aprovados em CO / triados → buscados', f'{br(sb_co.get("aprovado", 0))} → {br(sb_busc)}')}{caixa('Recuperados / não recuperados', f'{br(sb_rec.get("recuperado", 0))} / {br(sb_rec.get("nao_recuperado", 0))}')}
{caixa('Incluídos por snowballing', f'n = {br(inc.get("snowballing", 0))}')}</tr>
<tr><td class='lab'>Incluídos</td><td colspan='4' style='text-align:center;font-size:10pt'><b>Estudos incluídos na revisão: {br(P["n_incluidos"])}</b>
 (bases {br(inc.get("bases", 0))}; outros métodos {br(inc.get("outros", 0))}; snowballing {br(inc.get("snowballing", 0))})</td></tr></table>"""

    anos = Counter(r["ano"] for r in ex)
    q = {k: Counter(r[k] for r in ex) for k in ("Q1", "Q2", "Q3", "Q4")}
    qt = Counter(int(float(r["Q_total"])) for r in ex if r.get("Q_total"))
    def top(campo, n=10):
        c = contar_rotulos(ex, campo)
        return tab([campo.replace("_", " ").capitalize(), "Estudos", "%"], [[e(k), br(v), f"{100 * v / len(ex):.1f}".replace(".", ",")] for k, v in c.most_common(n)])
    publico = sum(1 for r in ex if r.get("contexto_publico_CI4") == "sim")
    pm = sum(1 for r in ex if r.get("pm_integrada_decisao") == "sim")

    h = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><span class='doc'>Relatório da revisão sistemática</span>",
         "<h1>Relatório da Revisão Sistemática de Literatura</h1>",
         f"<p class='sub'>Pesquisa Bibliográfica Sistemática (PBS) · PRISMA 2020 · dados de {e(P.get('data_execucao', ''))} · "
         f"atualizado em {hoje}</p>",
         f"<div class='kpi'><div><b>{br(sum(ident.values()))}</b>registros identificados</div><div><b>{br(P['textos_buscados'])}</b>textos completos buscados</div>"
         f"<div><b>{br(P['n_incluidos'])}</b>estudos incluídos</div><div><b>{n_val}/{len(val)}</b>decisões validadas pelo avaliador</div></div>",
         "<div class='nota'>As decisões de triagem e elegibilidade foram tomadas por regras e são provisórias. O protocolo prevê um avaliador "
         f"único; {n_val} das {len(val)} inclusões foram conferidas até agora. Os números abaixo mudam conforme essa validação avança.</div>",
         "<h2>1. Fluxo PRISMA 2020</h2><p>Coluna da esquerda: bases de dados; coluna da direita: outros métodos.</p>", fluxo,
         "<h2>2. Fontes</h2>",
         tab(["Fonte", "Grupo", "Registros"], [[e(k.split("|", 1)[1]), "base de dados" if k.startswith("bases") else "outros métodos", br(v)] for k, v in ident.items()]),
         "<h2>3. Mapeamento descritivo</h2>",
         "<h3>Ano de publicação</h3>", tab(["Ano"] + sorted(anos), [["Estudos"] + [br(anos[a]) for a in sorted(anos)]]),
         f"<p>Estudos com contexto governamental ou público (CI4): {br(publico)} de {br(len(ex))}. Estudos que integram Mineração de Processos "
         f"a um modelo decisório (SQ2): {br(pm)}.</p>",
         "<h3>SQ1 – domínios</h3>", top("dominio"),
         "<h3>SQ1 – técnicas de aprendizado de máquina</h3>", top("tecnica_ml"),
         "<h3>SQ3 – técnicas de XAI</h3>", top("tecnica_xai"),
         "<h3>SQ3 – público da explicação</h3>", top("publico_explicacao"),
         "<h3>SQ3 – validação da explicação</h3>", top("validacao_xai"),
         "<h3>SQ4 – governança, privacidade e responsabilização</h3>", top("governanca"),
         "<h3>SQ5 – tipo de evidência</h3>", top("evidencia"),
         "<h2>4. Avaliação de qualidade</h2>",
         tab(["Dimensão", "0", "1", "2"], [[d, br(q[d].get("0", 0)), br(q[d].get("1", 0)), br(q[d].get("2", 0))] for d in q]),
         tab(["Pontuação total"] + [str(k) for k in sorted(qt)], [["Estudos"] + [br(qt[k]) for k in sorted(qt)]]),
         "<p>Conforme o protocolo, a pontuação caracteriza a força da evidência e não exclui estudos.</p>",
         "<h2>5. Limitações</h2><ul>"
         "<li>Triagem por regras, com validação do avaliador pendente.</li>"
         "<li>ACM Digital Library não consultada; consultas exatas de Scopus e IEEE ainda não arquivadas.</li>"
         f"<li>{br(rec.get('bases', {}).get('nao_recuperado', 0) + rec.get('outros', {}).get('nao_recuperado', 0) + sb_rec.get('nao_recuperado', 0))} textos completos "
         "não recuperados (sem versão aberta ou falha de download); a lista para acesso institucional está em "
         "<code>revisao_sistematica/textos_para_baixar_CAFe.html</code>.</li>"
         "<li>Restrição a inglês e português (CO2); viés de publicação e de cobertura das bases.</li></ul>",
         "<h2>Apêndice – estudos incluídos</h2>",
         tab(["ID", "Ano", "Título", "Veículo", "Grupo", "Q"],
             [[e(r["id"]), e(r["ano"]), e(r["titulo"][:150]), e((r.get("veiculo") or "")[:60]), e(r["grupo"]), e(r["Q_total"])]
              for r in sorted(ex, key=lambda r: (r["ano"], r["titulo"]))], "small"),
         "</body></html>"]
    return "\n".join(h)


def main():
    P = json.loads((RS / "resultados_prisma.json").read_text(encoding="utf-8"))
    reg, n_novos = atualizar_registro(P)
    weasyprint.HTML(string=html_protocolo(P, reg, n_novos), base_url=str(ROOT)).write_pdf(RS / "protocolo_sigma.pdf")
    weasyprint.HTML(string=html_relatorio(P), base_url=str(ROOT)).write_pdf(RS / "relatorio_revisao_sistematica.pdf")
    print(f"Registro: {len(reg)} entradas ({n_novos} novas) -> {REG.relative_to(ROOT)}")
    print("OK: revisao_sistematica/protocolo_sigma.pdf | revisao_sistematica/relatorio_revisao_sistematica.pdf")


if __name__ == "__main__":
    main()

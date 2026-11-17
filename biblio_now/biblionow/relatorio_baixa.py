# -*- coding: utf-8 -*-
"""
Biblio-now · relatório da baixa e matriz estatística. Autor: Eduardo Lopes Jonker.

Para cada busca:
  referencias.bib   – cada referência traz de qual base veio, se a base a marca como acesso aberto,
                      a situação do PDF (baixado, já no acervo, sem PDF aberto, falhou, não tentado) e o motivo;
                      no início, um @comment com os parâmetros; no fim, um @comment com a matriz da baixa.
  matriz_baixa.csv  – matriz base × situação do PDF (contagens e % na linha) e acesso aberto × situação.
  matriz_baixa.json – os mesmos números, lidos pelo Protocolo Sigma.

Todos os números são contados nos registros da própria busca; nada é estimado, exceto o intervalo de
confiança de 95% (Wilson) da taxa de sucesso do download, que só descreve a incerteza dessa proporção.
"""
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from . import base

SITUACOES = ["baixado", "já no acervo", "sem PDF aberto", "falhou", "não tentado"]
NOMES_BASE = {"OpenAlex": "OpenAlex", "SemanticScholar": "Semantic Scholar"}
ORDEM_BASES = ["Só OpenAlex", "Só Semantic Scholar", "OpenAlex + Semantic Scholar"]


# ---------------------------------------------------------------- classificação de cada registro
def situacao(status: str) -> tuple[str, str]:
    """('baixado'|'já no acervo'|'sem PDF aberto'|'falhou'|'não tentado', motivo)."""
    s = (status or "").strip()
    cod, _, resto = s.partition(" (")
    motivo = resto.rstrip(")") if resto else ""
    return {"baixado": "baixado", "ja_existia": "já no acervo", "sem_pdf_aberto": "sem PDF aberto",
            "falhou": "falhou"}.get(cod, "não tentado"), motivo or ("" if cod != "" else "busca interrompida")


def bases_de(fonte: str) -> list[str]:
    return [NOMES_BASE.get(f, f) for f in (fonte or "").split("+") if f]


def grupo_base(fonte: str) -> str:
    b = bases_de(fonte)
    if len(b) > 1:
        return "OpenAlex + Semantic Scholar"
    return f"Só {b[0]}" if b else "Base não informada"


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float] | None:
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(100 * max(0.0, c - m), 1), round(100 * min(1.0, c + m), 1)


# ---------------------------------------------------------------- matriz
def _linha(nome: str, cont: Counter) -> dict:
    tot = sum(cont[s] for s in SITUACOES)
    tentados = cont["baixado"] + cont["falhou"]
    com_pdf = cont["baixado"] + cont["já no acervo"]
    return {"linha": nome, **{s: cont[s] for s in SITUACOES}, "total": tot,
            "pct": {s: (round(100 * cont[s] / tot, 1) if tot else None) for s in SITUACOES},
            "cobertura_pct": round(100 * com_pdf / tot, 1) if tot else None,
            "sucesso_download_pct": round(100 * cont["baixado"] / tentados, 1) if tentados else None,
            "sucesso_ic95": wilson(cont["baixado"], tentados), "tentados": tentados}


def matriz(registros: list[dict]) -> dict:
    """registros: dicionários com 'fonte', 'acesso_aberto' (bool ou 'sim'/'não') e 'status_pdf'."""
    por_grupo, por_base, por_aa, motivos = {}, {}, {}, Counter()
    total = Counter()
    for r in registros:
        sit, mot = situacao(r.get("status_pdf", ""))
        total[sit] += 1
        por_grupo.setdefault(grupo_base(r.get("fonte", "")), Counter())[sit] += 1
        for b in bases_de(r.get("fonte", "")) or ["Base não informada"]:
            por_base.setdefault(b, Counter())[sit] += 1
        aa = r.get("acesso_aberto")
        aa = "sim" if aa in (True, "sim", "True", "true", 1) else "não"
        por_aa.setdefault(f"Acesso aberto segundo a base: {aa}", Counter())[sit] += 1
        if sit in ("falhou", "não tentado") and mot:
            motivos[(sit, re.sub(r"\s+", " ", mot)[:90])] += 1
    grupos = [g for g in ORDEM_BASES if g in por_grupo] + sorted(g for g in por_grupo if g not in ORDEM_BASES)
    return {
        "gerada_em": datetime.now().isoformat(timespec="seconds"),
        "situacoes": SITUACOES,
        "por_origem": [_linha(g, por_grupo[g]) for g in grupos] + [_linha("Total", total)],
        "por_base": [_linha(f"{b} (todos os registros da base)", por_base[b]) for b in sorted(por_base)],
        "por_acesso_aberto": [_linha(k, por_aa[k]) for k in sorted(por_aa)],
        "motivos": [{"situacao": s, "motivo": m, "n": n} for (s, m), n in motivos.most_common(15)],
        "notas": ["Uma linha 'Só OpenAlex' ou 'Só Semantic Scholar' conta registros encontrados em uma única base; "
                  "registros achados nas duas ficam em 'OpenAlex + Semantic Scholar'. Na tabela por base, o mesmo registro "
                  "conta para cada base em que apareceu, por isso a soma passa do total.",
                  "Cobertura = (baixados + já no acervo) ÷ total da linha. Sucesso do download = baixados ÷ (baixados + falhas), "
                  "com intervalo de confiança de 95% de Wilson.",
                  "'Não tentado' inclui registros que não atingem o mínimo de blocos, o limite de PDFs, falhas recentes "
                  "em espera e buscas canceladas (veja os motivos)."],
    }


def somar(matrizes: list[dict]) -> dict | None:
    """Soma as contagens de várias buscas (o mesmo artigo pode contar em mais de uma busca)."""
    if not matrizes:
        return None
    blocos = {}
    for chave in ("por_origem", "por_base", "por_acesso_aberto"):
        acum = {}
        for m in matrizes:
            for l in m.get(chave, []):
                acum.setdefault(l["linha"], Counter()).update({s: l.get(s, 0) for s in SITUACOES})
        ordem = list(acum)
        if chave == "por_origem":
            ordem = [g for g in ORDEM_BASES if g in acum] + sorted(g for g in acum if g not in ORDEM_BASES and g != "Total")
            ordem += ["Total"] if "Total" in acum else []
        blocos[chave] = [_linha(k, acum[k]) for k in ordem]
    mot = Counter()
    for m in matrizes:
        for x in m.get("motivos", []):
            mot[(x["situacao"], x["motivo"])] += x["n"]
    return {"gerada_em": datetime.now().isoformat(timespec="seconds"), "situacoes": SITUACOES, **blocos,
            "motivos": [{"situacao": s, "motivo": mm, "n": n} for (s, mm), n in mot.most_common(15)],
            "buscas": len(matrizes), "notas": matrizes[-1].get("notas", [])}


# ---------------------------------------------------------------- saídas da busca
def _n(v) -> str:
    return f"{int(v):,}".replace(",", ".")


def _fmt_pct(v):
    return "—" if v is None else f"{v:.1f}%".replace(".", ",")


def texto_matriz(m: dict) -> list[str]:
    """Matriz em texto de largura fixa (para o @comment do .bib e o consulta.txt)."""
    cab = ["Origem do registro"] + m["situacoes"] + ["Total", "Cobertura", "Sucesso (IC 95%)"]
    linhas = []
    for l in m["por_origem"] + m["por_acesso_aberto"]:
        ic = l["sucesso_ic95"]
        suc = "—" if l["sucesso_download_pct"] is None else f"{_fmt_pct(l['sucesso_download_pct'])} ({_fmt_pct(ic[0])}–{_fmt_pct(ic[1])})"
        linhas.append([l["linha"]] + [f"{l[s]} ({_fmt_pct(l['pct'][s])})" for s in m["situacoes"]] +
                      [str(l["total"]), _fmt_pct(l["cobertura_pct"]), suc])
    larg = [max(len(str(x[i])) for x in [cab] + linhas) for i in range(len(cab))]
    fmt = lambda x: "  ".join(str(c).ljust(larg[i]) for i, c in enumerate(x))
    out = [fmt(cab), "  ".join("-" * w for w in larg)] + [fmt(x) for x in linhas]
    if m.get("motivos"):
        out += ["", "Principais motivos de falha / não tentativa:"] + [f"  {x['n']:>5}  {x['situacao']}: {x['motivo']}" for x in m["motivos"]]
    return out


def gravar_matriz(m: dict, pasta: Path):
    (pasta / "matriz_baixa.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(pasta / "matriz_baixa.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        for titulo, chave in (("Base de origem × situação do PDF", "por_origem"), ("Por base (registro conta em cada base onde apareceu)", "por_base"),
                              ("Acesso aberto × situação do PDF", "por_acesso_aberto")):
            w.writerow([titulo])
            w.writerow(["linha"] + [f"{s} (n)" for s in SITUACOES] + [f"{s} (%)" for s in SITUACOES] +
                       ["total", "cobertura_%", "tentados", "sucesso_download_%", "ic95_inferior_%", "ic95_superior_%"])
            for l in m[chave]:
                ic = l["sucesso_ic95"] or (None, None)
                w.writerow([l["linha"]] + [l[s] for s in SITUACOES] + [l["pct"][s] for s in SITUACOES] +
                           [l["total"], l["cobertura_pct"], l["tentados"], l["sucesso_download_pct"], ic[0], ic[1]])
            w.writerow([])
        w.writerow(["Motivos de falha / não tentativa"])
        w.writerow(["situacao", "motivo", "n"])
        for x in m["motivos"]:
            w.writerow([x["situacao"], x["motivo"], x["n"]])
        w.writerow([])
        for n in m["notas"]:
            w.writerow([n])


def _comentario(linhas: list[str]) -> str:
    corpo = "\n".join(l.replace("{", "(").replace("}", ")") for l in linhas)
    return "@comment{\n" + corpo + "\n}\n"


def gravar_bib(registros: list[dict], caminho: Path, cabecalho: list[str], m: dict):
    """BibTeX da busca com o relatório da baixa em cada referência (campos ignorados pelos estilos ABNT/APA)."""
    usadas, entradas = set(), []
    for r in registros:
        palavra = next((p for p in re.findall(r"[A-Za-z]{4,}", base.ascii_slug(r["titulo"], 200).replace("_", " "))), "art")
        raiz = f"{base.sobrenome(r)}{r['ano'] or 'sd'}{palavra.lower()}"
        chave, n = raiz, 1
        while chave in usadas:
            n += 1
            chave = f"{raiz}{chr(96 + n)}"
        usadas.add(chave)
        tipo = "inproceedings" if any(x in (r.get("tipo") or "").lower() for x in ("proceed", "conference")) else "article"
        sit, mot = situacao(r.get("status_pdf", ""))
        bases = " e ".join(bases_de(r.get("fonte", ""))) or "não informada"
        aa = "sim" if r.get("acesso_aberto") else "não"
        nota = f"Biblio-now: base {bases}; acesso aberto segundo a base: {aa}; PDF: {sit}" + (f" ({mot})" if mot else "")
        campos = [("title", r["titulo"]), ("author", " and ".join(r["autores"])), ("year", r["ano"]),
                  ("journal" if tipo == "article" else "booktitle", r["veiculo"]), ("doi", r["doi"]), ("url", r["url"]),
                  ("biblionow_base", bases), ("biblionow_acesso_aberto", aa), ("biblionow_pdf", sit),
                  ("biblionow_motivo", mot), ("biblionow_arquivo", r.get("arquivo_pdf") and f"pdf/{r['arquivo_pdf']}"),
                  ("biblionow_url_pdf", r.get("url_pdf")), ("biblionow_verificacao", r.get("verificacao")), ("note", nota)]
        corpo = ",\n".join(f"  {k} = {{{base.bib_escape(v)}}}" for k, v in campos if v)
        entradas.append(f"@{tipo}{{{chave},\n{corpo}\n}}\n")
    rodape = ["MATRIZ ESTATÍSTICA DA BAIXA (contagens e % na linha)", ""] + texto_matriz(m) + [""] + m["notas"]
    caminho.write_text(_comentario(cabecalho) + "\n" + "\n".join(entradas) + "\n" + _comentario(rodape), encoding="utf-8")


# ---------------------------------------------------------------- HTML para o Protocolo Sigma
def html_matriz(m: dict, titulo: str) -> str:
    import html as h
    e = h.escape

    def tab(linhas, primeira):
        cab = "".join(f"<th>{e(s)}</th>" for s in m["situacoes"])
        corpo = []
        for l in linhas:
            ic = l["sucesso_ic95"]
            suc = "—" if l["sucesso_download_pct"] is None else f"{_fmt_pct(l['sucesso_download_pct'])}<br><small>{_fmt_pct(ic[0])}–{_fmt_pct(ic[1])}</small>"
            forte = " style='font-weight:bold'" if l["linha"] == "Total" else ""
            corpo.append(f"<tr{forte}><td>{e(l['linha'])}</td>" +
                         "".join(f"<td>{_n(l[s])}<br><small>{_fmt_pct(l['pct'][s])}</small></td>" for s in m["situacoes"]) +
                         f"<td>{_n(l['total'])}</td><td>{_fmt_pct(l['cobertura_pct'])}</td><td>{suc}</td></tr>")
        return (f"<table><tr><th>{e(primeira)}</th>{cab}<th>Total</th><th>Cobertura</th><th>Sucesso do download (IC 95%)</th></tr>"
                + "".join(corpo) + "</table>")

    p = [f"<h3>{e(titulo)}</h3>", tab(m["por_origem"], "Base de origem"), tab(m["por_base"], "Por base"),
         tab(m["por_acesso_aberto"], "Acesso aberto")]
    if m.get("motivos"):
        p.append("<table><tr><th>Situação</th><th>Motivo</th><th>Registros</th></tr>" +
                 "".join(f"<tr><td>{e(x['situacao'])}</td><td>{e(x['motivo'])}</td><td>{x['n']}</td></tr>" for x in m["motivos"]) + "</table>")
    return "\n".join(p)


# ---------------------------------------------------------------- pasta relatorios/
LEIA_ME = """Biblio-now · pasta de relatórios

Atualizada automaticamente ao fim de cada busca. Nada aqui é editado à mão.

<id_da_busca>/                      um subdiretório por busca (o id começa com data e hora: AAAAMMDD_HHMMSS_nome)
    relatorio_baixa.bib             referências da busca; em cada uma: base de origem, acesso aberto, situação do PDF e motivo;
                                    no fim, a matriz estatística da baixa (@comment)
    matriz_baixa.csv / .json        base × situação do PDF, acesso aberto × situação, motivos de falha
    consulta.txt                    parâmetros, consultas enviadas às bases e resumo numérico
    resultados.csv                  todos os registros avaliados
matriz_baixa_consolidada.csv/.json  soma de todas as buscas (um artigo achado em duas buscas conta nas duas)
protocolo_sigma.html / .pdf         cópia do Protocolo Sigma com a matriz consolidada e a da última busca
"""


def copiar_para_relatorios(pasta_busca: Path, relatorios: Path, id_busca: str):
    import shutil
    destino = relatorios / id_busca
    destino.mkdir(parents=True, exist_ok=True)
    for orig, nome in (("referencias.bib", "relatorio_baixa.bib"), ("matriz_baixa.csv", None), ("matriz_baixa.json", None),
                       ("consulta.txt", None), ("resultados.csv", None)):
        f = pasta_busca / orig
        if f.exists():
            shutil.copy2(f, destino / (nome or orig))
    (relatorios / "LEIA-ME.txt").write_text(LEIA_ME, encoding="utf-8")


def consolidar(repo_raiz: Path) -> tuple[dict | None, dict | None, dict | None]:
    """(consolidada, última, resumo da última) a partir de buscas/*/matriz_baixa.json; grava a consolidada em relatorios/."""
    ms, ultima, res_ultima = [], None, None
    for d in sorted((repo_raiz / "buscas").glob("*/matriz_baixa.json")):
        try:
            m = json.loads(d.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ms.append(m)
        ultima = m
        r = d.parent / "resumo.json"
        res_ultima = json.loads(r.read_text(encoding="utf-8")) if r.exists() else {"id": d.parent.name}
    total = somar(ms)
    if total:
        rel = repo_raiz / "relatorios"
        rel.mkdir(exist_ok=True)
        tmp = rel / "_consolidada"
        tmp.mkdir(exist_ok=True)
        gravar_matriz(total, tmp)
        for ext in ("csv", "json"):
            (tmp / f"matriz_baixa.{ext}").replace(rel / f"matriz_baixa_consolidada.{ext}")
        tmp.rmdir()
    return total, ultima, res_ultima

# -*- coding: utf-8 -*-
"""
Verificação das referências da dissertação contra o registro oficial dos DOIs (Crossref) e o OpenAlex.

  python scripts/verificar_referencias.py [arquivo.bib ...]   (padrão: overleaf_dissertacao_udesc/referencias.bib)

Para cada referência confere:
  1. DOI que abre, mas leva a outra obra   → título registrado no DOI × título do .bib (similaridade de palavras)
  2. Obra atribuída ao autor errado         → sobrenomes registrados no DOI × autores do .bib (primeiro autor e conjunto)
  3. Ano e periódico                        → ano e nome do periódico registrados no DOI × .bib
  4. Revista que pode não existir           → periódico encontrado no OpenAlex (fontes) e no Crossref (ISSN); presença no DOAJ
  5. Obra retratada                         → marca de retratação no OpenAlex e avisos de atualização no Crossref
  6. Referência sem DOI                     → busca bibliográfica no Crossref para achar o DOI e conferir os dados
  7. Citações no texto sem entrada no .bib  e entradas do .bib que o texto não cita

Os resultados mostram o que foi encontrado; um alerta pede conferência humana, não prova erro.
Leis, decretos, normas e manuais (tipos @manual, @misc, @techreport sem DOI) não são buscados no Crossref.
Saída: docs/verificacao_referencias/<nome do bib>_<data>.csv e .md (e um resumo no terminal).
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote

import requests

RAIZ = Path(__file__).resolve().parent.parent
PADRAO = RAIZ / "overleaf_dissertacao_udesc" / "referencias.bib"
SAIDA = RAIZ / "docs" / "verificacao_referencias"
CROSSREF = "https://api.crossref.org/works"
OPENALEX = "https://api.openalex.org"


def _env(nome):
    f = RAIZ / ".env"
    if f.exists():
        for l in f.read_text(encoding="utf-8").splitlines():
            k, _, v = l.partition("=")
            if k.strip() == nome:
                return v.strip().strip('"').strip("'")
    return ""


EMAIL = _env("OPENALEX_EMAIL") or _env("UNPAYWALL_EMAIL")
CHAVE_OA = _env("OPENALEX_API_KEY")
S = requests.Session()
S.headers["User-Agent"] = f"verificar_referencias/1.0 (dissertacao PPGCAP/UDESC; mailto:{EMAIL})" if EMAIL else "verificar_referencias/1.0"


# ---------------------------------------------------------------- leitura do .bib
LATEX = {r"\'a": "á", r"\'e": "é", r"\'i": "í", r"\'o": "ó", r"\'u": "ú", r"\~a": "ã", r"\~o": "õ", r"\^a": "â", r"\^e": "ê",
         r"\^o": "ô", r"\c{c}": "ç", r"\c c": "ç", r'\"u': "ü", r'\"o': "ö", r'\"a': "ä", r"\`a": "à", r"\&": "&", "--": "–"}


def delatex(t: str) -> str:
    t = t or ""
    t = re.sub(r"\\([`'^\"~=.])\{(\w)\}", r"\\\1\2", t)          # \'{e} -> \'e
    for a, b in LATEX.items():
        t = t.replace(a, b)
    t = re.sub(r"\\[a-zA-Z]+\s*", "", t)
    return re.sub(r"\s+", " ", t.replace("{", "").replace("}", "")).strip()


def ler_bib(f: Path) -> list[dict]:
    txt = f.read_text(encoding="utf-8", errors="replace")
    out, i = [], 0
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", txt):
        tipo, chave = m.group(1).lower(), m.group(2)
        if tipo in ("comment", "string", "preamble"):
            continue
        j, prof = m.end(), 1
        while j < len(txt) and prof:
            prof += {"{": 1, "}": -1}.get(txt[j], 0)
            j += 1
        corpo, campos, k = txt[m.end(): j - 1], {}, 0
        while True:
            mm = re.compile(r"\s*,?\s*([A-Za-z_\-]+)\s*=\s*").match(corpo, k)
            if not mm:
                break
            k = mm.end()
            if k < len(corpo) and corpo[k] == "{":
                p, a = 1, k + 1
                while a < len(corpo) and p:
                    p += {"{": 1, "}": -1}.get(corpo[a], 0)
                    a += 1
                val, k = corpo[k + 1: a - 1], a
            elif k < len(corpo) and corpo[k] == '"':
                a = corpo.index('"', k + 1)
                val, k = corpo[k + 1: a], a + 1
            else:
                a = re.compile(r"[,}\n]").search(corpo, k)
                a = a.start() if a else len(corpo)
                val, k = corpo[k:a].strip(), a
            campos[mm.group(1).lower()] = val
        out.append({"tipo": tipo, "chave": chave, **campos})
        i = j
    return out


# ---------------------------------------------------------------- comparação
def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", delatex(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", t).strip()


def sim_titulo(a: str, b: str) -> float:
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    ta, tb = set(a.split()), set(b.split())
    jac = len(ta & tb) / len(ta | tb)
    # título do .bib pode ter só o título principal (sem subtítulo): compara também o começo
    curto, longo = sorted((a, b), key=len)
    inicio = SequenceMatcher(None, curto, longo[: len(curto)]).ratio()
    return round(max(jac, inicio), 3)


def sobrenomes_bib(autor: str) -> list[str]:
    nomes = [x.strip() for x in re.split(r"\s+and\s+", delatex(autor or "")) if x.strip()]
    out = []
    for n in nomes:
        if n.lower() in ("others", "et al"):
            continue
        s = n.split(",")[0] if "," in n else n.split()[-1]
        out.append(norm(s).split()[-1] if norm(s) else "")
    return [x for x in out if x]


def _get(url, params=None, tentativas=4):
    for k in range(tentativas):
        try:
            r = S.get(url, params=params, timeout=(10, 40))
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                return {"_404": True}
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 * (k + 1))
                continue
            return {"_erro": f"HTTP {r.status_code}"}
        except (requests.RequestException, ValueError) as e:
            time.sleep(2 * (k + 1))
            erro = type(e).__name__
    return {"_erro": locals().get("erro", "sem resposta")}


def crossref_doi(doi):
    d = _get(f"{CROSSREF}/{quote(doi, safe='/')}", {"mailto": EMAIL} if EMAIL else None)
    return d.get("message") if "message" in d else d


def crossref_busca(e):
    q = " ".join(x for x in (delatex(e.get("title", "")), " ".join(sobrenomes_bib(e.get("author", ""))[:2]), e.get("year", "")) if x)
    d = _get(CROSSREF, {"query.bibliographic": q, "rows": 3, **({"mailto": EMAIL} if EMAIL else {})})
    return (d.get("message") or {}).get("items") or []


def openalex_doi(doi):
    p = {"select": "id,display_name,is_retracted,primary_location,publication_year,type"}
    if EMAIL:
        p["mailto"] = EMAIL
    if CHAVE_OA:
        p["api_key"] = CHAVE_OA
    return _get(f"{OPENALEX}/works/https://doi.org/{quote(doi, safe='/')}", p)


def openalex_fonte(nome="", issn=""):
    p = {"per_page": 3, "select": "id,display_name,issn_l,issn,is_in_doaj,works_count,host_organization_name,type"}
    if EMAIL:
        p["mailto"] = EMAIL
    if CHAVE_OA:
        p["api_key"] = CHAVE_OA
    if issn:
        d = _get(f"{OPENALEX}/sources/issn:{issn}", {k: v for k, v in p.items() if k != "per_page"})
        if d.get("id"):
            return d
    if nome:
        d = _get(f"{OPENALEX}/sources", {**p, "search": delatex(nome)[:150]})
        res = d.get("results") or []
        alvo = norm(nome)
        for s in res:
            if sim_titulo(s.get("display_name", ""), nome) >= 0.75 or norm(s.get("display_name", "")) == alvo:
                return s
    return None


# ---------------------------------------------------------------- verificação de uma entrada
SEM_BUSCA = ("manual", "misc", "techreport", "online", "electronic", "www", "standard", "legislation", "jurisdiction")


def verificar(e: dict) -> dict:
    r = {"chave": e["chave"], "tipo": e["tipo"], "titulo_bib": delatex(e.get("title", ""))[:200], "autores_bib": "; ".join(sobrenomes_bib(e.get("author", ""))),
         "ano_bib": e.get("year", ""), "periodico_bib": delatex(e.get("journal") or e.get("booktitle") or "")[:120],
         "doi": (e.get("doi") or "").strip().replace("https://doi.org/", "").replace("http://dx.doi.org/", ""),
         "situacao": "ok", "alertas": [], "titulo_registrado": "", "autores_registrados": "", "ano_registrado": "",
         "periodico_registrado": "", "sim_titulo": "", "doi_sugerido": "", "fonte_openalex": "", "doaj": "", "retratado": ""}
    reg = None
    if r["doi"]:
        reg = crossref_doi(r["doi"])
        if not reg or reg.get("_404"):
            oa = openalex_doi(r["doi"])
            if oa.get("id"):
                r["alertas"].append("DOI não está no Crossref (registrado em outra agência, ex.: DataCite); dados conferidos no OpenAlex")
                reg = {"title": [oa.get("display_name", "")], "author": [], "issued": {"date-parts": [[oa.get("publication_year")]]},
                       "container-title": [((oa.get("primary_location") or {}).get("source") or {}).get("display_name", "")]}
            else:
                r["alertas"].append("DOI NÃO EXISTE (não resolve no Crossref nem no OpenAlex)")
                r["situacao"] = "erro"
                reg = None
        elif reg.get("_erro"):
            r["alertas"].append(f"não foi possível consultar o DOI ({reg['_erro']})")
            r["situacao"] = "não verificado"
            reg = None
    elif e["tipo"] in ("article", "inproceedings", "incollection", "conference") and e.get("title"):
        itens = crossref_busca(e)
        melhor = max(itens, key=lambda it: sim_titulo((it.get("title") or [""])[0], e.get("title", "")), default=None)
        if melhor and sim_titulo((melhor.get("title") or [""])[0], e.get("title", "")) >= 0.85:
            reg = melhor
            r["doi_sugerido"] = melhor.get("DOI", "")
            r["alertas"].append(f"sem DOI no .bib; o Crossref tem a obra com DOI {r['doi_sugerido']}")
        else:
            r["alertas"].append("sem DOI e não encontrada no Crossref: confira se a obra existe e os dados estão corretos")
            r["situacao"] = "conferir"
    else:
        r["situacao"] = "não aplicável" if e["tipo"] in SEM_BUSCA or e["tipo"] == "book" else "não verificado"
        if e["tipo"] == "book":
            r["alertas"].append("livro sem DOI: confira ISBN, editora e edição no catálogo (Biblioteca/ISBN), não no Crossref")

    if reg:
        t_reg = delatex((reg.get("title") or [""])[0])
        r["titulo_registrado"] = t_reg[:200]
        s = sim_titulo(t_reg, e.get("title", "")) if e.get("title") else 0
        r["sim_titulo"] = s
        if e.get("title") and s < 0.5:
            r["alertas"].append(f"DOI LEVA A OUTRA OBRA: o título registrado é “{t_reg[:110]}”")
            r["situacao"] = "erro"
        elif e.get("title") and s < 0.8:
            r["alertas"].append("título diferente do registrado no DOI (pode ser só tradução ou subtítulo): confira")
            r["situacao"] = "conferir" if r["situacao"] == "ok" else r["situacao"]
        aut = [norm(a.get("family") or a.get("name") or "").split()[-1] for a in reg.get("author") or [] if norm(a.get("family") or a.get("name") or "")]
        r["autores_registrados"] = "; ".join(aut[:8])
        meus = sobrenomes_bib(e.get("author", ""))
        if aut and meus:
            comuns = set(meus) & set(aut)
            if not comuns:
                r["alertas"].append(f"AUTOR ERRADO: nenhum sobrenome do .bib aparece no registro ({', '.join(aut[:4])})")
                r["situacao"] = "erro"
            elif meus[0] != aut[0] and meus[0] in aut:
                r["alertas"].append(f"ordem dos autores diferente: o primeiro autor registrado é {aut[0]}")
                r["situacao"] = "conferir" if r["situacao"] == "ok" else r["situacao"]
            elif meus[0] not in aut:
                r["alertas"].append(f"primeiro autor do .bib ({meus[0]}) não está no registro; primeiro registrado: {aut[0]}")
                r["situacao"] = "erro"
            faltam = [m for m in meus if m not in aut]
            if faltam and r["situacao"] == "ok":
                r["alertas"].append(f"sobrenome(s) do .bib ausente(s) no registro: {', '.join(faltam)}")
                r["situacao"] = "conferir"
        partes = ((reg.get("issued") or reg.get("published-print") or reg.get("published-online") or {}).get("date-parts") or [[None]])[0]
        ano = str(partes[0] or "")
        r["ano_registrado"] = ano
        if ano and e.get("year") and str(e["year"])[:4] != ano:
            dif = abs(int(ano) - int(re.sub(r"\D", "", str(e["year"]))[:4] or ano))
            r["alertas"].append(f"ano diferente: .bib {e['year']}, registro {ano}" + (" (diferença de 1 ano: publicação online × impressa)" if dif == 1 else ""))
            if dif > 1:
                r["situacao"] = "conferir" if r["situacao"] == "ok" else r["situacao"]
        cont = delatex((reg.get("container-title") or [""])[0])
        r["periodico_registrado"] = cont[:120]
        if cont and r["periodico_bib"] and sim_titulo(cont, r["periodico_bib"]) < 0.5 and norm(r["periodico_bib"]) not in norm(cont):
            r["alertas"].append(f"periódico diferente: registro diz “{cont[:80]}”")
            r["situacao"] = "conferir" if r["situacao"] == "ok" else r["situacao"]
        for u in reg.get("update-to") or []:
            if (u.get("type") or "").lower() in ("retraction", "withdrawal", "removal", "expression_of_concern"):
                r["alertas"].append(f"Crossref registra {u['type']} para esta obra")
                r["situacao"] = "erro"
        issn = (reg.get("ISSN") or [""])[0]
    else:
        issn = ""

    doi_oa = r["doi"] or r["doi_sugerido"]
    if doi_oa:
        oa = openalex_doi(doi_oa)
        if oa.get("is_retracted"):
            r["retratado"] = "sim"
            r["alertas"].append("OBRA RETRATADA segundo o OpenAlex (Retraction Watch): não cite como evidência válida")
            r["situacao"] = "erro"
        else:
            r["retratado"] = "não" if oa.get("id") else ""
    if e["tipo"] in ("article",) and (r["periodico_bib"] or r["periodico_registrado"]):
        f = openalex_fonte(r["periodico_registrado"] or r["periodico_bib"], issn)
        if f:
            r["fonte_openalex"] = f"{f.get('display_name')} ({f.get('works_count', 0)} trabalhos; {f.get('host_organization_name') or 'editora não informada'})"
            r["doaj"] = "sim" if f.get("is_in_doaj") else "não"
            if (f.get("works_count") or 0) < 50:
                r["alertas"].append("periódico com menos de 50 trabalhos indexados: confira se é legítimo (ISSN, editora, corpo editorial)")
                r["situacao"] = "conferir" if r["situacao"] == "ok" else r["situacao"]
        else:
            r["alertas"].append("PERIÓDICO NÃO ENCONTRADO no OpenAlex: confira ISSN no portal ISSN e se o nome está correto")
            r["situacao"] = "conferir" if r["situacao"] == "ok" else r["situacao"]
    time.sleep(0.15)
    return r


# ---------------------------------------------------------------- citações no texto
def chaves_citadas(pasta_tex: Path) -> set[str]:
    cit = set()
    for f in pasta_tex.rglob("*.tex"):
        for m in re.finditer(r"\\(?:cite|citeonline|citeauthor|citeyear|apud|textcite|parencite|nocite)[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}",
                             f.read_text(encoding="utf-8", errors="ignore")):
            cit |= {c.strip() for c in m.group(1).split(",") if c.strip()}
    return cit


def main():
    arquivos = [Path(a) for a in sys.argv[1:]] or [PADRAO]
    SAIDA.mkdir(parents=True, exist_ok=True)
    for bib in arquivos:
        entradas = ler_bib(bib)
        print(f"\n{bib.name}: {len(entradas)} entradas")
        res = []
        for i, e in enumerate(entradas, 1):
            r = verificar(e)
            res.append(r)
            if r["situacao"] in ("erro", "conferir"):
                print(f"  [{i:3d}] {r['situacao'].upper():9s} {r['chave']}: {' | '.join(r['alertas'])[:220]}")
        citadas = chaves_citadas(bib.parent) if (bib.parent / "main.tex").exists() else set()
        chaves = {e["chave"] for e in entradas}
        sem_entrada = sorted(citadas - chaves)
        nao_citadas = sorted(chaves - citadas) if citadas else []
        cont = {s: sum(r["situacao"] == s for r in res) for s in ("ok", "conferir", "erro", "não aplicável", "não verificado")}
        data = datetime.now().strftime("%Y%m%d_%H%M")
        base = SAIDA / f"{bib.stem}_{data}"
        cols = list(res[0].keys()) if res else []
        with open(base.with_suffix(".csv"), "w", newline="", encoding="utf-8-sig") as h:
            w = csv.DictWriter(h, fieldnames=cols, delimiter=";")
            w.writeheader()
            for r in res:
                w.writerow({**r, "alertas": " | ".join(r["alertas"])})
        L = [f"# Verificação das referências: `{bib.relative_to(RAIZ) if bib.is_relative_to(RAIZ) else bib}`", "",
             f"Gerado em {datetime.now():%d/%m/%Y %H:%M} por `scripts/verificar_referencias.py`. Fontes: registro do DOI no Crossref "
             "(título, autores, ano, periódico, avisos de retratação) e OpenAlex (retratações via Retraction Watch, periódicos e DOAJ).", "",
             "| Situação | Referências |", "|---|---|"] + [f"| {k} | {v} |" for k, v in cont.items()] + [
             "", "Um alerta pede conferência humana; não é prova de erro. Erro = DOI inexistente, DOI de outra obra, autor ausente do registro ou obra retratada.", ""]
        for s in ("erro", "conferir"):
            sel = [r for r in res if r["situacao"] == s]
            if sel:
                L += [f"## {s.capitalize()} ({len(sel)})", "", "| Chave | Problema | No .bib | No registro |", "|---|---|---|---|"]
                for r in sel:
                    L.append(f"| `{r['chave']}` | {' · '.join(r['alertas'])} | {r['titulo_bib'][:70]} ({r['autores_bib'][:40]}, {r['ano_bib']}) "
                             f"| {r['titulo_registrado'][:70]} ({r['autores_registrados'][:40]}, {r['ano_registrado']}) |".replace("\n", " "))
                L.append("")
        if sem_entrada:
            L += [f"## Citadas no texto sem entrada no .bib ({len(sem_entrada)})", "", ", ".join(f"`{c}`" for c in sem_entrada), ""]
        if nao_citadas:
            L += [f"## No .bib e não citadas com \\cite no texto ({len(nao_citadas)})", "",
                  "Não aparecem na lista de referências do PDF (o abnTeX2 só lista o que é citado), salvo uso de \\nocite.", "",
                  ", ".join(f"`{c}`" for c in nao_citadas), ""]
        oks = [r for r in res if r["situacao"] == "ok"]
        if oks:
            L += [f"## Conferidas sem problema ({len(oks)})", "", ", ".join(f"`{r['chave']}`" for r in oks), ""]
        base.with_suffix(".md").write_text("\n".join(L), encoding="utf-8")
        print(f"  resumo: {json.dumps(cont, ensure_ascii=False)}")
        print(f"  citadas sem entrada: {len(sem_entrada)} · no .bib e não citadas: {len(nao_citadas)}")
        print(f"  relatório: {base.with_suffix('.md').relative_to(RAIZ)}")


if __name__ == "__main__":
    main()

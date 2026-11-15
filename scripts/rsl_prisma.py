#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revisão sistemática da literatura — pipeline PRISMA 2020
Executa o "Protocolo de Pesquisa Bibliográfica Sistemática" (Metodologia de
Pesquisa/protocolo_pesquisa_bibliografica_sistematica.pdf, versão 14/11/2026).

Etapas (cada uma grava um CSV em revisao_sistematica/dados/):
  01 identificação      lê todas as exportações do projeto (RIS, CSV, BibTeX)
  02 enriquecimento     completa resumo, idioma, tipo e links abertos via OpenAlex (por DOI)
  03 deduplicação       CO1: DOI normalizado, depois título normalizado
  04 critérios objetivos CO2 idioma, CO3 período, CO4 tipo de publicação
  05 triagem            CI1 ∧ CI2 ∧ (CI3 ∨ CI4) em título, resumo e palavras-chave
  06 texto completo     recuperação de PDFs de acesso aberto (CO5: não recuperado ≠ excluído)
  07 elegibilidade      reaplicação dos critérios no texto completo (XAI não incidental)
  08 snowballing        uma iteração regressiva e progressiva (OpenAlex) a partir dos incluídos
  09 qualidade/extração Q1–Q4 (0/1/2) e codificação por SQ1–SQ5

Natureza da triagem
  O protocolo prevê um avaliador humano único. Aqui os critérios são aplicados
  por regras explícitas (dicionários abaixo), de forma reprodutível. O resultado
  é uma triagem ASSISTIDA POR COMPUTADOR e deve ser validada pelo autor na
  planilha dados/09_validacao_avaliador.csv antes de ser tratada como final.

Uso
  python3 scripts/rsl_prisma.py               # executa tudo (usa cache)
  python3 scripts/rsl_prisma.py --sem-rede    # só cache local, sem API/downloads
  OPENALEX_API_KEY=...                         # opcional (cota 10x maior)
"""

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from buscar_artigos import baixar_pdf, resumo_de_indice  # noqa: E402

BASE = ROOT / "revisao_sistematica"
DADOS = BASE / "dados"
CACHE = BASE / "cache"
TEXTOS = BASE / "textos_completos"
TEXTOS_PDF = TEXTOS / "PDF"   # arquivos baixados
TEXTOS_TXT = TEXTOS / "TXT"   # texto extraído com pdftotext
DATA_LIMITE = date(2026, 11, 14)
ANO_MIN, ANO_MAX_VOLUME = 2020, 2027   # 2027 = volumes futuros já publicados online (ver CO3)
OPENALEX = "https://api.openalex.org/works"
UA = "rsl_prisma/1.0 (revisao sistematica PPGCAP/UDESC; python-requests)"

# ── Fontes (todas as exportações do projeto) ─────────────────────────────────
MP = ROOT / "Metodologia de Pesquisa"
FONTES = [
    # (nome, grupo PRISMA, caminho, formato, descrição)
    ("Scopus", "bases", MP / "scobus.ris", "ris",
     "Exportação Scopus, 14/11/2026, estratégia do protocolo (seção 5.1)"),
    ("IEEE Xplore", "bases", MP / "export2026.11.14-13.11.41.csv", "ieee",
     "Exportação IEEE Xplore, 14/11/2026 13:11"),
    ("Biblioteca Paperpile", "outros", MP / "Paperpile - Library - 14 de nov..ris", "ris",
     "Biblioteca de referências do autor, exportada em 14/11/2026"),
    ("Biblioteca exportada (export.ris)", "outros", MP / "export.ris", "ris",
     "Biblioteca de referências exportada em 17/10/2026"),
    ("Periódicos CAPES (RIS)", "outros", MP / "Periodicos-CAPES-RIS.ris", "ris", "Buscas exploratórias no Portal CAPES"),
    ("Periódicos CAPES (RIS)", "outros", MP / "Periodicos-CAPES-RIS (1).ris", "ris", ""),
    ("Periódicos CAPES (RIS)", "outros", ROOT / "documentos_academicos" / "Periodicos-CAPES-RIS.ris", "ris", ""),
    ("Periódicos CAPES (RIS)", "outros", ROOT / "documentos_academicos" / "Periodicos-CAPES-RIS (1).ris", "ris", ""),
    ("Base de Dados Mestrado (BibTeX)", "outros", ROOT / "documentos_academicos" / "Base de Dados Mestrado.bib", "bib",
     "Base BibTeX do mestrado"),
    ("Base de Dados Mestrado (BibTeX)", "outros", ROOT / "documentos_academicos" / "Base.mestrado.bib", "bib", ""),
    ("Referências da dissertação (Overleaf)", "outros", ROOT / "overleaf_dissertacao_udesc" / "referencias.bib", "bib",
     "Referências do texto da dissertação"),
    ("Busca OpenAlex + Semantic Scholar", "outros", ROOT / "artigos" / "resultados.csv", "artigos",
     "Busca complementar por API, 14/11/2026 (consulta diferente da do protocolo)"),
]
for p in sorted((ROOT / "documentos_academicos").glob("Periodicos-CAPES-BibTex*.bib")):
    FONTES.append(("Periódicos CAPES (BibTeX)", "outros", p, "bib", "Buscas exploratórias no Portal CAPES"))
# Exportações feitas pelo autor via Portal CAPES / CAFe (ver LEIA-ME_roteiro_de_busca.md).
# Nome: <base>_<AAAA-MM-DD>[_parteN].<ext>; base em scopus, wos, ieee, acm.
EXPORT_CAPES = MP / "exportacoes_capes"
REGISTRO_BUSCAS = EXPORT_CAPES / "registro_buscas.csv"
BASES_PREFIXO = {"scopus": "Scopus", "wos": "Web of Science", "webofscience": "Web of Science",
                 "ieee": "IEEE Xplore", "acm": "ACM Digital Library",
                 # bases chinesas (emenda ao protocolo; ver seção 6 do roteiro)
                 "cscd": "CSCD (Web of Science)", "cnki": "CNKI", "wanfang": "Wanfang"}
FORMATO_EXT = {".ris": "ris", ".bib": "bib", ".csv": "csv", ".txt": "txt"}
for p in sorted(EXPORT_CAPES.glob("*")):
    if p.suffix.lower() not in FORMATO_EXT or p.name == REGISTRO_BUSCAS.name:
        continue
    prefixo = p.stem.split("_")[0].lower()
    base = BASES_PREFIXO.get(prefixo)
    if base:
        FONTES.insert(2, (base, "bases", p, FORMATO_EXT[p.suffix.lower()], f"Exportação via Portal CAPES ({p.name})"))
    else:
        FONTES.append((f"Exportação não identificada ({p.name})", "outros", p, FORMATO_EXT[p.suffix.lower()],
                       "nome fora do padrão <base>_<data>; tratado como outro método"))
BASES_PROTOCOLO = ("Scopus", "IEEE Xplore", "ACM Digital Library")

# ── Dicionários dos critérios do protocolo (seção 6.2) ───────────────────────
def rx(*termos):
    return [re.compile(t, re.I) for t in termos]

CI = {
    "CI1": rx(r"\bdecision[- ]support", r"\bdecision[- ]making\b", r"\bprescriptive\b", r"\bpredictive\b",
              r"\bpredict(?:ion|ions|ing|s|ed)?\b", r"\bforecast", r"\boptimi[sz]", r"\bprocess mining\b",
              r"\bbusiness process", r"\brisk (?:assessment|prediction|scor)", r"\banomaly detection\b",
              r"\bfraud detection\b", r"\bprioriti[sz]"),
    "CI2": rx(r"\bexplainab", r"\binterpretab", r"\bxai\b", r"\bshap\b", r"\blime\b(?! ?stone)",
              r"\bcounterfactual explanation", r"\balgorithmic transparency\b", r"\bmodel transparency\b",
              r"\btransparent (?:model|ai|machine)"),
    # CI3 e CI4 seguem a definição do protocolo (6.2) e o bloco 3 da estratégia (5.1).
    "CI3": rx(r"\bdata governance\b", r"\b(?:ai|algorithmic|model) governance\b", r"\bprivacy\b",
              r"\bdata protection\b", r"\bgdpr\b", r"\blgpd\b", r"\baccountab", r"\bauditab"),
    "CI4": rx(r"\bpublic sector\b", r"\bgovernment", r"\bpublic administration\b", r"\bpublic services?\b",
              r"\be-government\b", r"\bmunicipal", r"\bpublic procurement\b", r"\bpublic polic",
              r"\btax(?:ation|payers?| authorit| administration| fraud| evasion)\b", r"\bpublic agenc"),
}
SECUNDARIO_TITULO = re.compile(r"\b(systematic (?:literature )?review|literature review|scoping review|survey|"
                               r"systematic mapping|mapping study|bibliometric|meta-analysis|state[- ]of[- ]the[- ]art review|"
                               r"a review|review of|overview of)\b", re.I)
SECUNDARIO_RESUMO = re.compile(r"\b(this (?:systematic )?review|we review|systematic (?:literature )?review|scoping review|"
                               r"bibliometric analysis|meta-analysis|systematic mapping|prisma guidelines|this survey)\b", re.I)

# ── Utilidades ───────────────────────────────────────────────────────────────
def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", d)
    return d.strip().rstrip(".")


def norm_tit(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", t)[:150]


def limpar_latex(s):
    s = s or ""
    s = re.sub(r"\\['`^\"~c]\{?([A-Za-z])\}?", r"\1", s)
    s = s.replace("{", "").replace("}", "").replace("\\&", "&").replace("&amp;", "&")
    return re.sub(r"\s+", " ", s).strip()


def ano_int(v):
    m = re.search(r"(19|20)\d{2}", str(v or ""))
    return int(m.group(0)) if m else None


def gravar(nome, linhas, colunas):
    DADOS.mkdir(parents=True, exist_ok=True)
    with open(DADOS / nome, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for l in linhas:
            w.writerow({k: ("; ".join(v) if isinstance(v, list) else v) for k, v in l.items()})


# ── 01 Leitores ──────────────────────────────────────────────────────────────
def ler_ris(path):
    recs, cur = [], {}
    for line in open(path, encoding="utf-8-sig", errors="replace"):
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)", line.rstrip("\n"))
        if not m:
            continue
        t, v = m.groups()
        if t == "ER":
            recs.append(cur)
            cur = {}
            continue
        cur.setdefault(t, []).append(v.strip())
    out = []
    for x in recs:
        g = lambda *ts: next((x[t][0] for t in ts if x.get(t)), "")
        ty = g("TY")
        m3 = g("M3")
        out.append({
            "titulo": limpar_latex(g("TI", "T1", "CT")),
            "resumo": limpar_latex(" ".join(x.get("AB", []) or x.get("N2", []))),
            "palavras_chave": "; ".join(x.get("KW", [])),
            "ano": ano_int(g("PY", "Y1", "DA")),
            "doi": norm_doi(g("DO")),
            "autores": "; ".join(x.get("AU", []) or x.get("A1", [])),
            "veiculo": limpar_latex(g("T2", "JO", "JF", "J2", "BT")),
            "tipo_bruto": m3 or ty,
            "idioma": g("LA"),
            "url": g("UR"),
        })
    return out


def ler_ieee(path):
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        out.append({
            "titulo": r.get("Document Title", ""),
            "resumo": r.get("Abstract", ""),
            "palavras_chave": "; ".join(filter(None, [r.get("Author Keywords", ""), r.get("IEEE Terms", "")])),
            "ano": ano_int(r.get("Publication Year")),
            "doi": norm_doi(r.get("DOI")),
            "autores": r.get("Authors", ""),
            "veiculo": r.get("Publication Title", ""),
            "tipo_bruto": r.get("Document Identifier", ""),
            "idioma": "English",
            "url": r.get("PDF Link", ""),
        })
    return out


def ler_bib(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for m in re.finditer(r"@(\w[\w\u00C0-\u017F]*)\s*\{\s*[^,]*,", txt):
        tipo = m.group(1).lower()
        if tipo in ("comment", "string", "preamble"):
            continue
        i, prof = m.end(), 1
        j = i
        while j < len(txt) and prof > 0:
            prof += {"{": 1, "}": -1}.get(txt[j], 0)
            j += 1
        corpo = txt[i:j - 1]
        campos = {}
        for f in re.finditer(r"(\w+)\s*=\s*", corpo):
            k = f.group(1).lower()
            k0 = f.end()
            if k0 >= len(corpo):
                continue
            if corpo[k0] == "{":
                d, p = 1, k0 + 1
                while p < len(corpo) and d > 0:
                    d += {"{": 1, "}": -1}.get(corpo[p], 0)
                    p += 1
                v = corpo[k0 + 1:p - 1]
            elif corpo[k0] == '"':
                p = corpo.find('"', k0 + 1)
                v = corpo[k0 + 1:p]
            else:
                v = re.match(r"[^,\n]*", corpo[k0:]).group(0)
            campos.setdefault(k, v)
        out.append({
            "titulo": limpar_latex(campos.get("title", "")),
            "resumo": limpar_latex(campos.get("abstract", "")),
            "palavras_chave": limpar_latex(campos.get("keywords", "")),
            "ano": ano_int(campos.get("year")),
            "doi": norm_doi(campos.get("doi")),
            "autores": limpar_latex(campos.get("author", "")),
            "veiculo": limpar_latex(campos.get("journal") or campos.get("booktitle") or campos.get("publisher", "")),
            "tipo_bruto": tipo,
            "idioma": campos.get("language", ""),
            "url": campos.get("url", ""),
        })
    return out


def ler_artigos(path):
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8-sig"), delimiter=";"):
        out.append({
            "titulo": r["titulo"], "resumo": "", "palavras_chave": "", "ano": ano_int(r["ano"]),
            "doi": norm_doi(r["doi"]), "autores": r["autores"], "veiculo": r["veiculo"],
            "tipo_bruto": "", "idioma": "", "url": r["url"],
            "_pdf_local": r.get("arquivo_pdf", ""),
        })
    return out


def ler_scopus_csv(path):
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        out.append({
            "titulo": r.get("Title", ""), "resumo": r.get("Abstract", ""),
            "palavras_chave": "; ".join(filter(None, [r.get("Author Keywords", ""), r.get("Index Keywords", "")])),
            "ano": ano_int(r.get("Year")), "doi": norm_doi(r.get("DOI")), "autores": r.get("Authors", ""),
            "veiculo": r.get("Source title", ""), "tipo_bruto": r.get("Document Type", ""),
            "idioma": r.get("Language of Original Document", ""), "url": r.get("Link", ""),
        })
    return out


def ler_csv(path):
    """Detecta pelo cabeçalho se o CSV é da IEEE Xplore ou da Scopus."""
    cab = open(path, encoding="utf-8-sig", errors="replace").readline()
    if "Document Title" in cab:
        return ler_ieee(path)
    if "Source title" in cab or "EID" in cab:
        return ler_scopus_csv(path)
    raise ValueError(f"CSV de formato desconhecido: {path.name}")


def ler_refer(path):
    """Formato EndNote/Refer (linhas %T, %A, %D...), usado pelas exportações da CNKI e da Wanfang."""
    recs, cur = [], {}
    for line in open(path, encoding="utf-8-sig", errors="replace"):
        line = line.rstrip("\n")
        m = re.match(r"^%(\S)\s?(.*)", line)
        if m:
            cur.setdefault(m.group(1), []).append(m.group(2).strip())
        elif not line.strip() and cur:
            recs.append(cur)
            cur = {}
    if cur:
        recs.append(cur)
    out = []
    for x in recs:
        g = lambda t: (x.get(t) or [""])[0]
        out.append({
            "titulo": g("T"), "resumo": " ".join(x.get("X", [])),
            "palavras_chave": "; ".join(k for v in x.get("K", []) for k in re.split(r"[;；,，]", v) if k.strip()),
            "ano": ano_int(g("D")), "doi": norm_doi(g("R")), "autores": "; ".join(x.get("A", [])),
            "veiculo": g("J") or g("B"), "tipo_bruto": g("0"), "idioma": g("G"), "url": g("U"),
        })
    return out


def ler_txt(path):
    """.txt pode ser EndNote/Refer (CNKI, Wanfang) ou RIS."""
    for linha in open(path, encoding="utf-8-sig", errors="replace"):
        if linha.strip():
            return ler_refer(path) if linha.lstrip().startswith("%") else ler_ris(path)
    return []


LEITORES = {"ris": ler_ris, "ieee": ler_ieee, "bib": ler_bib, "artigos": ler_artigos, "csv": ler_csv,
            "txt": ler_txt}


def ler_registro_buscas():
    """Linhas de registro_buscas.csv indexadas pelo nome do arquivo exportado."""
    if not REGISTRO_BUSCAS.exists():
        return {}
    reg = {}
    for r in csv.DictReader(open(REGISTRO_BUSCAS, encoding="utf-8-sig"), delimiter=";"):
        if r.get("arquivo"):
            reg[Path(r["arquivo"]).name] = r
    return reg


def etapa_identificacao():
    registros, vistos_md5, inventario = [], {}, []
    for nome, grupo, path, fmt, desc in FONTES:
        if not path.exists():
            inventario.append({"fonte": nome, "grupo": grupo, "arquivo": str(path.relative_to(ROOT)),
                               "registros": 0, "observacao": "arquivo não encontrado"})
            continue
        md5 = hashlib.md5(path.read_bytes()).hexdigest()
        if md5 in vistos_md5:
            inventario.append({"fonte": nome, "grupo": grupo, "arquivo": str(path.relative_to(ROOT)),
                               "registros": 0, "observacao": f"cópia idêntica de {vistos_md5[md5]} (não contada)"})
            continue
        vistos_md5[md5] = str(path.relative_to(ROOT))
        recs = LEITORES[fmt](path)
        for k, r in enumerate(recs):
            r.update({"id": f"{md5[:6]}-{k:05d}", "fonte": nome, "grupo": grupo})
        registros += recs
        inventario.append({"fonte": nome, "grupo": grupo, "arquivo": str(path.relative_to(ROOT)),
                           "registros": len(recs), "observacao": desc,
                           "data_arquivo": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                           "md5": md5[:12]})
    presentes = {f[0] for f in FONTES if f[2].exists()}
    for base in BASES_PROTOCOLO:
        if base not in presentes:
            inventario.append({"fonte": base, "grupo": "bases", "arquivo": "-", "registros": 0,
                               "observacao": "base prevista no protocolo sem exportação no projeto (desvio do protocolo)"})
    # junta o registro preenchido pelo autor (consulta, data, filtros, total informado)
    reg = ler_registro_buscas()
    for item in inventario:
        r = reg.get(Path(item["arquivo"]).name) if item["arquivo"] != "-" else None
        for campo in ("data_hora_busca", "consulta_submetida", "campos", "filtros",
                      "resultados_informados_pela_base", "formato_exportacao", "observacoes"):
            item[campo] = (r or {}).get(campo, "")
    gravar("01_inventario_fontes.csv", inventario,
           ["fonte", "grupo", "arquivo", "registros", "observacao", "data_arquivo", "md5",
            "data_hora_busca", "consulta_submetida", "campos", "filtros",
            "resultados_informados_pela_base", "formato_exportacao", "observacoes"])
    return registros, inventario


# ── 02 Enriquecimento via OpenAlex (por DOI) ─────────────────────────────────
def sessao():
    s = requests.Session()
    s.headers["User-Agent"] = UA
    k = os.environ.get("OPENALEX_API_KEY", "").strip()
    if k:
        s.headers["Authorization"] = f"Bearer {k}"
    return s


SELECT = ("id,doi,display_name,publication_year,publication_date,language,type,primary_location,"
          "best_oa_location,locations,open_access,abstract_inverted_index,referenced_works,"
          "cited_by_count,authorships,keywords")


def openalex_lote(s, filtro_campo, valores, cache_nome, sem_rede):
    """Busca obras por lote (até 50 valores por chamada), com cache em disco."""
    cache_f = CACHE / f"{cache_nome}.json"
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    faltam = [v for v in dict.fromkeys(valores) if v and v not in cache]
    if faltam and not sem_rede:
        print(f"   OpenAlex: consultando {len(faltam)} {filtro_campo}(s) em lotes de 50")
        for i in range(0, len(faltam), 50):
            lote = faltam[i:i + 50]
            vals = "|".join(("https://doi.org/" + v) if filtro_campo == "doi" else v for v in lote)
            params = {"filter": f"{filtro_campo}:{vals}", "per_page": 100, "select": SELECT}
            for tent in range(6):
                try:
                    r = s.get(OPENALEX, params=params, timeout=(15, 90))
                except requests.RequestException:
                    time.sleep(3 * (tent + 1))
                    continue
                if r.status_code == 200:
                    break
                if r.status_code == 429 or r.status_code >= 500:
                    time.sleep(min(60, 3 * 2 ** tent))
                    continue
                print("   OpenAlex erro", r.status_code, r.text[:200])
                r = None
                break
            else:
                r = None
            achados = {}
            if r is not None and r.status_code == 200:
                for w in r.json().get("results", []):
                    chave = norm_doi(w.get("doi")) if filtro_campo == "doi" else w["id"].split("/")[-1]
                    achados[chave] = w
            for v in lote:
                cache[v] = achados.get(v)   # None = consultado e não encontrado
            CACHE.mkdir(parents=True, exist_ok=True)
            cache_f.write_text(json.dumps(cache))
            time.sleep(0.25)
    return cache


def tipo_categoria(r, w=None):
    t = (r.get("tipo_bruto") or "").lower()
    if w:
        wt = (w.get("type") or "").lower()
        st = (((w.get("primary_location") or {}).get("source") or {}).get("type") or "").lower()
        if not t or t in ("misc", "jour", "gen", "elec", "unknown"):
            t = {"article": "conference" if st == "conference" else ("preprint" if st == "repository" else "journal")}.get(wt, wt)
    mapa = [
        (r"conference review|label\.ris\.referencetype\.conference_review", "nao_pesquisa"),
        (r"review|short_survey|short survey", "secundario"),
        (r"editorial|note|letter|erratum|paratext|retraction", "nao_pesquisa"),
        (r"book chapter|book_chapter|chap|incollection|inbook|ebook chapter|book-chapter", "capitulo"),
        (r"^book$|label\.ris\.referencetype\.book$|^book\b", "livro"),
        (r"conference|conf|cpaper|inproceedings|proceedings", "conferencia"),
        (r"article|jour|journal|^article$", "periodico"),
        (r"preprint|posted-content|repository", "preprint"),
        (r"thesis|dissertation|phdthesis|mastersthesis|report|techreport|standard|dataset|webpage|misc", "outro"),
    ]
    for pad, cat in mapa:
        if re.search(pad, t):
            return cat
    return "desconhecido"


def etapa_enriquecimento(registros, s, sem_rede):
    dois = [r["doi"] for r in registros if r["doi"]]
    cache = openalex_lote(s, "doi", dois, "openalex_doi", sem_rede)
    n_res = 0
    for r in registros:
        w = cache.get(r["doi"]) if r["doi"] else None
        r["_oa"] = w
        if w:
            if not r["resumo"]:
                ab = resumo_de_indice(w.get("abstract_inverted_index"))
                if ab:
                    r["resumo"], n_res = ab, n_res + 1
            if not r["ano"]:
                r["ano"] = w.get("publication_year")
            if not r["idioma"]:
                r["idioma"] = w.get("language") or ""
            # Palavras-chave do OpenAlex são atribuídas por máquina: não entram na triagem.
        r["tipo"] = tipo_categoria(r, w)
    print(f"   resumos completados pelo OpenAlex: {n_res}")
    return cache


# ── 03 Deduplicação (CO1) ────────────────────────────────────────────────────
def etapa_deduplicacao(registros):
    unicos, chave_para, dup_log = [], {}, []
    # bases primeiro, para que duplicatas de outros métodos apontem para elas
    for r in sorted(registros, key=lambda r: 0 if r["grupo"] == "bases" else 1):
        if not r["titulo"]:
            dup_log.append({**r, "decisao": "sem título (descartado)"})
            continue
        ks = [("doi:" + r["doi"]) if r["doi"] else None, "tit:" + norm_tit(r["titulo"])]
        alvo = next((chave_para[k] for k in ks if k and k in chave_para), None)
        if alvo is not None:
            u = unicos[alvo]
            u["fontes"].append(r["fonte"])
            for campo in ("resumo", "palavras_chave", "doi", "idioma", "veiculo", "autores"):
                if not u[campo] and r[campo]:
                    u[campo] = r[campo]
            if r.get("_pdf_local") and not u.get("_pdf_local"):
                u["_pdf_local"] = r["_pdf_local"]
            if u["tipo"] in ("desconhecido", "outro") and r["tipo"] not in ("desconhecido", "outro"):
                u["tipo"] = r["tipo"]
            dup_log.append({**r, "decisao": f"duplicata de {u['id']}"
                            + (" (entre grupos)" if u["grupo"] != r["grupo"] else "")})
            r["_duplicata_grupo"] = u["grupo"]
        else:
            r["fontes"] = [r["fonte"]]
            unicos.append(r)
            idx = len(unicos) - 1
            for k in ks:
                if k:
                    chave_para[k] = idx
        for k in ks:
            if k and alvo is not None:
                chave_para.setdefault(k, alvo)
    gravar("03_duplicatas.csv", dup_log, ["id", "fonte", "grupo", "titulo", "ano", "doi", "decisao"])
    return unicos, dup_log


# ── 04 Critérios objetivos (CO2–CO4) ─────────────────────────────────────────
IDIOMAS_OK = {"english", "en", "eng", "portuguese", "pt", "por", "português", "portugues"}


def etapa_objetivos(unicos, arquivo="04_criterios_objetivos.csv"):
    aprovados, log = [], []
    for r in unicos:
        motivo = ""
        if not (r["idioma"] or "").strip():
            # sem idioma informado: identifica pela escrita do título (ex.: exportações da CNKI)
            t = r["titulo"]
            if re.search(r"[\u3040-\u30ff]", t):
                r["idioma"] = "ja"
            elif re.search(r"[\u4e00-\u9fff]", t):
                r["idioma"] = "zh"
            elif re.search(r"[\uac00-\ud7af]", t):
                r["idioma"] = "ko"
            elif re.search(r"[\u0400-\u04ff]", t):
                r["idioma"] = "ru"
            elif re.search(r"[\u0600-\u06ff]", t):
                r["idioma"] = "ar"
        lang = (r["idioma"] or "").strip().lower()
        if lang and lang not in IDIOMAS_OK and lang != "undefined":
            motivo = f"CO2 idioma ({r['idioma']})"
        elif r["ano"] is None:
            motivo = "CO3 ano não informado"
        elif not (ANO_MIN <= r["ano"] <= ANO_MAX_VOLUME):
            motivo = f"CO3 fora do período ({r['ano']})"
        elif r["tipo"] == "secundario":
            motivo = "CO4 estudo secundário (tipo do registro)"
        elif r["tipo"] in ("nao_pesquisa",):
            motivo = "CO4 editorial, nota, carta ou anais"
        elif r["tipo"] in ("capitulo", "livro"):
            motivo = "CO4 capítulo ou livro"
        elif r["tipo"] in ("preprint", "outro"):
            motivo = "CO4 sem avaliação por pares (preprint, tese, relatório ou outro)"
        r["co_decisao"] = motivo or "aprovado"
        log.append(r)
        if not motivo:
            aprovados.append(r)
    if arquivo:
        gravar(arquivo, log, ["id", "fontes", "grupo", "titulo", "ano", "doi", "tipo", "idioma", "co_decisao"])
    return aprovados


# ── 05 Triagem por título, resumo e palavras-chave ───────────────────────────
def atende(texto):
    return {c: any(p.search(texto) for p in pads) for c, pads in CI.items()}


def regra(a):
    return a["CI1"] and a["CI2"] and (a["CI3"] or a["CI4"])


def etapa_triagem(aprovados, arquivo="05_triagem_titulo_resumo.csv"):
    seguem, log = [], []
    for r in aprovados:
        texto = " ".join([r["titulo"], r["resumo"], r["palavras_chave"]])
        a = atende(texto)
        tem_resumo = len(r["resumo"]) > 150
        if SECUNDARIO_TITULO.search(r["titulo"]) or (tem_resumo and SECUNDARIO_RESUMO.search(r["resumo"])):
            dec = "excluído: estudo secundário (contexto/snowballing)"
        elif regra(a):
            dec = "segue para texto completo"
        elif not tem_resumo and a["CI2"]:
            dec = "segue para texto completo (sem resumo; XAI no título)"
        elif not a["CI2"]:
            dec = "excluído: CI2 (sem explicabilidade)"
        elif not a["CI1"]:
            dec = "excluído: CI1 (sem analítica para decisão)"
        else:
            dec = "excluído: CI3/CI4 (sem governança nem contexto público)"
        r.update({f"t_{k}": int(v) for k, v in a.items()})
        r["triagem"] = dec
        log.append(r)
        if dec.startswith("segue"):
            seguem.append(r)
    if arquivo:
        gravar(arquivo, log, ["id", "fontes", "grupo", "titulo", "ano", "doi", "t_CI1", "t_CI2", "t_CI3", "t_CI4", "triagem"])
    return seguem


# ── 06 Recuperação do texto completo (CO5) ───────────────────────────────────
def slug(t, n=60):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")[:n]


def links_pdf(r):
    urls = []
    w = r.get("_oa") or {}
    for loc in [w.get("best_oa_location") or {}] + list(w.get("locations") or []):
        u = (loc or {}).get("pdf_url")
        if u and u not in urls:
            urls.append(u)
    return urls


def extrair_texto(pdf):
    txt = TEXTOS_TXT / (pdf.stem + ".txt")
    TEXTOS_TXT.mkdir(parents=True, exist_ok=True)
    if not txt.exists():
        try:
            subprocess.run(["pdftotext", "-q", "-enc", "UTF-8", str(pdf), str(txt)], timeout=120, check=False)
        except subprocess.TimeoutExpired:
            return ""
    return txt.read_text(encoding="utf-8", errors="ignore") if txt.exists() else ""


MAX_TEXTOS = 10_000          # teto de textos completos (busca principal + snowballing)
_textos_usados = 0

# PDFs salvos à mão pelo autor (acesso CAFe). Qualquer nome de arquivo serve:
# o vínculo é feito pelo nome sugerido (DOI com "/" trocado por "_"), pelo DOI
# impresso nas duas primeiras páginas ou pelo título.
TEXTOS_MANUAL = TEXTOS / "PDF_manual_CAFe"
_indice_manual = None


def doi_para_arquivo(doi):
    return re.sub(r"[^A-Za-z0-9._-]", "_", doi.replace("/", "_")) + ".pdf"


def indice_manual():
    global _indice_manual
    if _indice_manual is not None:
        return _indice_manual
    _indice_manual = {"nome": {}, "doi": {}, "texto": []}
    TEXTOS_MANUAL.mkdir(parents=True, exist_ok=True)
    for pdf in sorted(TEXTOS_MANUAL.glob("*.pdf")):
        _indice_manual["nome"][pdf.name.lower()] = pdf
        try:
            ini = subprocess.run(["pdftotext", "-q", "-l", "2", "-enc", "UTF-8", str(pdf), "-"],
                                 capture_output=True, text=True, timeout=60).stdout
        except subprocess.TimeoutExpired:
            ini = ""
        for d in re.findall(r"10\.\d{4,9}/[^\s\"<>]+", ini):
            _indice_manual["doi"].setdefault(norm_doi(d.rstrip(".,;)]")), pdf)
        texto_norm = unicodedata.normalize("NFKD", ini).encode("ascii", "ignore").decode().lower()
        _indice_manual["texto"].append((re.sub(r"[^a-z0-9]", "", texto_norm), pdf))
    return _indice_manual


def achar_pdf_manual(r):
    idx = indice_manual()
    if not (idx["nome"] or idx["doi"]):
        return None
    if r["doi"]:
        p = idx["nome"].get(doi_para_arquivo(r["doi"]).lower()) or idx["doi"].get(r["doi"])
        if p:
            return p
    t = norm_tit(r["titulo"])
    if len(t) >= 30:
        for texto, pdf in idx["texto"]:
            if t[:120] in texto:
                return pdf
    return None


def etapa_texto_completo(seguem, s, sem_rede, rotulo="principal"):
    global _textos_usados
    TEXTOS_PDF.mkdir(parents=True, exist_ok=True)
    for r in seguem:
        destino = TEXTOS_PDF / f"{r['id']}_{slug(r['titulo'])}.pdf"
        r["pdf"], r["recuperacao"] = "", ""
        local = r.get("_pdf_local")
        if _textos_usados >= MAX_TEXTOS:
            r["recuperacao"] = f"não buscado (limite de {MAX_TEXTOS} textos atingido)"
            continue
        _textos_usados += 1
        manual = achar_pdf_manual(r)
        urls = links_pdf(r)
        if destino.exists():
            r["pdf"], r["recuperacao"] = destino.name, "recuperado"
        elif manual:
            destino.write_bytes(manual.read_bytes())
            r["pdf"], r["recuperacao"] = destino.name, f"recuperado (manual via CAFe: {manual.name})"
        elif local and (ROOT / "artigos" / local).exists():
            destino.write_bytes((ROOT / "artigos" / local).read_bytes())
            r["pdf"], r["recuperacao"] = destino.name, "recuperado (pasta artigos)"
        elif not urls:
            r["recuperacao"] = "não recuperado (sem versão de acesso aberto)"
        elif sem_rede:
            r["recuperacao"] = "não recuperado (há versão aberta; execução sem rede)"
        else:
            ok, info = baixar_pdf(s, urls, destino)
            r["pdf"], r["recuperacao"] = (destino.name, "recuperado") if ok else ("", f"não recuperado ({info})")
    return seguem


# ── 07 Elegibilidade no texto completo ───────────────────────────────────────
def corpo_sem_referencias(texto):
    m = list(re.finditer(r"\n\s*(references|bibliography|referências)\s*\n", texto, re.I))
    return texto[:m[-1].start()] if m and m[-1].start() > len(texto) * 0.5 else texto


# Menções mínimas no corpo do texto (sem a lista de referências) para o critério
# não ser considerado incidental (protocolo 6.2: "XAI apenas de forma incidental").
LIM_TC = {"CI1": 3, "CI2": 5, "CI3_CI4": 3}


def contagens(texto):
    return {c: sum(len(p.findall(texto)) for p in pads) for c, pads in CI.items()}


def etapa_elegibilidade(seguem):
    incluidos, log = [], []
    for r in seguem:
        if not r["pdf"]:
            r["elegibilidade"] = "texto completo não recuperado"
            log.append(r)
            continue
        texto = corpo_sem_referencias(extrair_texto(TEXTOS_PDF / r["pdf"]))
        palavras = len(texto.split())
        c = contagens(texto)
        r.update({f"n_{k}": v for k, v in c.items()})
        r["palavras"] = palavras
        r["_texto"] = texto
        inicio = texto[:4000]
        if palavras < 1500:
            dec = "excluído: texto curto (resumo estendido ou extração falhou)"
        elif SECUNDARIO_RESUMO.search(inicio) or SECUNDARIO_TITULO.search(r["titulo"]):
            dec = "excluído: estudo secundário"
        elif c["CI2"] < LIM_TC["CI2"]:
            dec = f"excluído: XAI incidental (menos de {LIM_TC['CI2']} menções)"
        elif c["CI1"] < LIM_TC["CI1"]:
            dec = "excluído: sem analítica para decisão"
        elif c["CI3"] < LIM_TC["CI3_CI4"] and c["CI4"] < LIM_TC["CI3_CI4"]:
            dec = "excluído: sem governança nem contexto público"
        else:
            dec = "incluído"
        r["elegibilidade"] = dec
        log.append(r)
        if dec == "incluído":
            incluidos.append(r)
    return incluidos, log


# ── 08 Snowballing (uma iteração, OpenAlex) ──────────────────────────────────
def etapa_snowballing(incluidos, todos_unicos, s, sem_rede):
    chaves = {("doi:" + r["doi"]) if r["doi"] else "tit:" + norm_tit(r["titulo"]) for r in todos_unicos}
    chaves |= {"tit:" + norm_tit(r["titulo"]) for r in todos_unicos}
    sementes = [r for r in incluidos if r.get("_oa")]
    reg_ids = []
    for r in sementes:
        reg_ids += [u.split("/")[-1] for u in (r["_oa"].get("referenced_works") or [])]
    print(f"   regressivo: {len(set(reg_ids))} referências de {len(sementes)} sementes")
    cache_reg = openalex_lote(s, "openalex_id", reg_ids, "openalex_ids", sem_rede)

    cache_prog_f = CACHE / "openalex_cites.json"
    cache_prog = json.loads(cache_prog_f.read_text()) if cache_prog_f.exists() else {}
    for r in sementes:
        wid = r["_oa"]["id"].split("/")[-1]
        if wid in cache_prog or sem_rede:
            continue
        try:
            resp = s.get(OPENALEX, params={"filter": f"cites:{wid}", "per_page": 100, "select": SELECT}, timeout=(15, 90))
            cache_prog[wid] = resp.json().get("results", []) if resp.status_code == 200 else []
        except requests.RequestException:
            cache_prog[wid] = []
        CACHE.mkdir(parents=True, exist_ok=True)
        cache_prog_f.write_text(json.dumps(cache_prog))
        time.sleep(0.25)
    prog = [(w, wid) for wid, lst in cache_prog.items() for w in lst]
    print(f"   progressivo: {len(prog)} citações recebidas")

    candidatos, vistos = [], set()
    for origem, pares in (("regressivo", [(w, None) for w in cache_reg.values() if w]), ("progressivo", prog)):
        for w, semente in pares:
            doi = norm_doi(w.get("doi"))
            k = ("doi:" + doi) if doi else "tit:" + norm_tit(w.get("display_name"))
            if k in chaves or k in vistos or "tit:" + norm_tit(w.get("display_name")) in chaves:
                continue
            vistos.add(k)
            autores = "; ".join(a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or []))
            r = {
                "id": "sb-" + w["id"].split("/")[-1], "fonte": f"Snowballing {origem}", "grupo": "snowballing",
                "titulo": w.get("display_name") or "", "resumo": resumo_de_indice(w.get("abstract_inverted_index")),
                "palavras_chave": "; ".join(k.get("display_name", "") for k in (w.get("keywords") or [])),
                "ano": w.get("publication_year"), "doi": doi, "autores": autores,
                "veiculo": (((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""),
                "tipo_bruto": "", "idioma": w.get("language") or "", "url": w.get("id"), "_oa": w,
            }
            r["tipo"] = tipo_categoria(r, w)
            r["fontes"] = [r["fonte"]]
            candidatos.append(r)
    return candidatos


# ── 09 Qualidade e extração ──────────────────────────────────────────────────
def conta(texto, *pads):
    return sum(len(re.findall(p, texto, re.I)) for p in pads)


CATEGORIAS = {
    "dominio": {
        "Saúde": [r"\bhealth", r"\bclinic", r"\bpatient", r"\bhospital", r"\bmedical"],
        "Finanças e bancos": [r"\bbank", r"\bcredit\b", r"\bloan", r"\bfinancial"],
        "Tributação": [r"\btax(?:es|ation|payer)?\b"],
        "Compras públicas": [r"\bprocurement", r"\btender"],
        "Governo e serviços públicos": [r"\bgovernment", r"\bpublic sector", r"\bpublic administration", r"\bmunicipal", r"\bpublic service"],
        "Justiça e segurança": [r"\bcourt\b", r"\bjudicial", r"\bpolic(?:e|ing)\b", r"\bcriminal", r"\blaw enforcement"],
        "Energia": [r"\benergy\b", r"\bpower grid", r"\bsmart grid", r"\belectricity"],
        "Transporte e frotas": [r"\bvehicle", r"\bfleet", r"\btransport", r"\btraffic"],
        "RH e folha de pagamento": [r"\bpayroll", r"\bhuman resource", r"\bsalar(?:y|ies)\b", r"\bemployee"],
        "Educação": [r"\beducation", r"\bstudent"],
        "Indústria e manutenção": [r"\bmanufactur", r"\bpredictive maintenance", r"\bindustrial"],
        "Cibersegurança": [r"\bcyber", r"\bintrusion", r"\bmalware"],
        "Seguros": [r"\binsurance"],
    },
    "problema": {
        "Detecção de anomalias e fraude": [r"\banomal", r"\bfraud"],
        "Avaliação de risco": [r"\brisk assessment", r"\brisk prediction", r"\brisk scor"],
        "Previsão": [r"\bforecast", r"\bpredictive model", r"\bprediction"],
        "Otimização e prescrição": [r"\bprescriptive", r"\boptimi[sz]ation model", r"\blinear programming", r"\bmilp\b", r"\bmathematical programming"],
        "Mineração de processos": [r"\bprocess mining", r"\bevent log", r"\bpredictive process monitoring", r"\bprescriptive process monitoring"],
        "Suporte à decisão e recomendação": [r"\bdecision support", r"\brecommend"],
    },
    "tecnica_ml": {
        "Ensembles de árvores": [r"\brandom forest", r"\bxgboost", r"\bgradient boost", r"\blightgbm", r"\bcatboost"],
        "Redes neurais / deep learning": [r"\bneural network", r"\bdeep learning", r"\blstm\b", r"\bconvolutional", r"\btransformer"],
        "Modelos lineares": [r"\blogistic regression", r"\blinear regression"],
        "SVM": [r"\bsupport vector"],
        "Árvore de decisão": [r"\bdecision tree"],
        "Isolation Forest / autoencoder": [r"\bisolation forest", r"\bautoencoder"],
        "Grafos / GNN": [r"\bgraph neural", r"\bknowledge graph"],
        "LLM / IA generativa": [r"\blarge language model", r"\bllms?\b", r"\bgpt\b"],
        "Otimização matemática": [r"\blinear programming", r"\bmilp\b", r"\binteger programming", r"\bgenetic algorithm"],
        "Clustering": [r"\bclustering", r"\bk-means"],
    },
    "tecnica_xai": {
        "SHAP": [r"\bshap\b", r"\bshapley"],
        "LIME": [r"\blime\b"],
        "Contrafactuais": [r"\bcounterfactual"],
        "Importância de atributos / permutação": [r"\bfeature importance", r"\bpermutation importance"],
        "Atenção / saliência / gradientes": [r"\battention (?:weight|mechanism|map)", r"\bgrad-cam", r"\bsaliency", r"\bintegrated gradients"],
        "Regras / árvores substitutas": [r"\brule extraction", r"\bdecision rules?\b", r"\bsurrogate model", r"\banchors?\b"],
        "PDP / ICE": [r"\bpartial dependence", r"\bindividual conditional expectation"],
        "Modelos interpretáveis por construção": [r"\binherently interpretable", r"\bglass[- ]box", r"\bexplainable boosting", r"\bgeneralized additive"],
    },
    "publico_explicacao": {
        "Auditores e órgãos de controle": [r"\bauditors?\b", r"\boversight bod"],
        "Reguladores": [r"\bregulators?\b"],
        "Gestores e tomadores de decisão": [r"\bdecision[- ]makers?\b", r"\bmanagers?\b", r"\bpolicy[- ]?makers?\b"],
        "Cidadãos e usuários finais": [r"\bcitizens?\b", r"\bend[- ]users?\b", r"\blay users?\b"],
        "Especialistas do domínio": [r"\bdomain experts?\b", r"\bclinicians?\b", r"\banalysts?\b"],
        "Desenvolvedores e cientistas de dados": [r"\bdevelopers?\b", r"\bdata scientists?\b"],
    },
    "validacao_xai": {
        "Estudo com usuários": [r"\buser stud", r"\bparticipants\b", r"\bhuman evaluation", r"\bquestionnaire"],
        "Métricas de fidelidade/estabilidade": [r"\bfidelity\b", r"\bfaithfulness", r"\bstability of (?:the )?explanation", r"\bconsistency of (?:the )?explanation"],
        "Avaliação por especialistas": [r"\bexpert (?:evaluation|assessment|validation|feedback)", r"\bvalidated by (?:domain )?experts"],
    },
    "governanca": {
        "GDPR / LGPD / AI Act": [r"\bgdpr\b", r"\blgpd\b", r"\bai act\b", r"\bgeneral data protection"],
        "Técnicas de preservação de privacidade": [r"\bdifferential privacy", r"\bfederated learning", r"\bhomomorphic", r"\banonymi[sz]", r"\bpseudonymi[sz]"],
        "Trilha de auditoria e registro": [r"\baudit trail", r"\baudit log", r"\blogging\b", r"\btraceability"],
        "Blockchain": [r"\bblockchain"],
        "Supervisão humana": [r"\bhuman[- ]in[- ]the[- ]loop", r"\bhuman oversight"],
        "Equidade e viés": [r"\bfairness\b", r"\bbias mitigation", r"\balgorithmic bias"],
        "Documentação de modelos": [r"\bmodel cards?\b", r"\bdatasheets\b", r"\bdocumentation of (?:the )?model"],
        "Responsabilização (accountability)": [r"\baccountab"],
    },
    "evidencia": {
        "Estudo de caso com dados reais": [r"\bcase study", r"\breal[- ]world data", r"\breal data"],
        "Experimento com conjunto de dados": [r"\bexperiment", r"\bbenchmark", r"\bdataset"],
        "Simulação": [r"\bsimulat"],
        "Protótipo / sistema implantado": [r"\bprototype", r"\bdeployed\b", r"\bimplementation in production"],
    },
}
LIMIAR = 3   # menções mínimas para marcar uma categoria no texto completo


def etapa_qualidade_extracao(incluidos):
    linhas = []
    for r in incluidos:
        t = r["_texto"]
        cod = {}
        for grupo, cats in CATEGORIAS.items():
            marcadas = [c for c, pads in cats.items() if conta(t, *pads) >= (2 if grupo in ("validacao_xai", "publico_explicacao", "governanca") else LIMIAR)]
            cod[grupo] = marcadas
        if not cod["evidencia"]:
            cod["evidencia"] = ["Proposta conceitual (sem avaliação identificada)"]
        q1 = conta(t, r"\bdataset", r"\bdata set", r"\brecords\b", r"\bcollected", r"\bsample of", r"\bobservations\b")
        q2 = conta(t, r"\bmethodology", r"\bframework", r"\barchitecture", r"\balgorithm", r"\bpipeline", r"\bprocedure")
        q3 = conta(t, r"\baccuracy", r"\bprecision\b", r"\brecall\b", r"\bf1\b", r"\bauc\b", r"\brmse\b", r"\bmae\b", r"\bevaluat", r"\bvalidat")
        q4 = len(cod["tecnica_xai"]) + len(cod["governanca"])
        nota = lambda v, a, b: 2 if v >= b else (1 if v >= a else 0)
        q = {"Q1": nota(q1, 3, 10), "Q2": nota(q2, 3, 10), "Q3": nota(q3, 5, 20), "Q4": nota(q4, 1, 3)}
        sq2 = "sim" if "Mineração de processos" in cod["problema"] and any(
            p in cod["problema"] for p in ("Previsão", "Otimização e prescrição", "Suporte à decisão e recomendação")) else "não"
        linhas.append({
            "id": r["id"], "titulo": r["titulo"], "ano": r["ano"], "autores": r["autores"], "veiculo": r["veiculo"],
            "doi": r["doi"], "fontes": r["fontes"], "grupo": r["grupo"], "tipo": r["tipo"],
            **{g: v for g, v in cod.items()}, "pm_integrada_decisao": sq2,
            **q, "Q_total": sum(q.values()), "palavras": r["palavras"],
            "contexto_publico_CI4": "sim" if r.get("n_CI4", 0) >= 2 else "não",
        })
    return linhas


# ── Registro de todas as fontes consultadas (PRISMA 2020, itens 6 e 7) ───────
def gerar_registro_fontes(inventario, R):
    def md(v):
        return str(v or "—").replace("|", "\\|").replace("\n", " ")
    linhas = [
        "# Registro das fontes consultadas", "",
        f"Gerado por `scripts/rsl_prisma.py` em {date.today():%d/%m/%Y}. "
        f"Data-limite do protocolo: {DATA_LIMITE:%d/%m/%Y}. Período coberto: {ANO_MIN}–{DATA_LIMITE.year}.", "",
        "## 1. Bases de dados (PRISMA: *databases*)", "",
        "| Base | Arquivo | Data | Registros lidos | Consulta submetida | Campos | Filtros | Total informado pela base | Observação |",
        "|---|---|---|---:|---|---|---|---:|---|",
    ]
    for i in inventario:
        if i["grupo"] != "bases":
            continue
        linhas.append("| " + " | ".join(md(x) for x in (
            i["fonte"], i["arquivo"], i.get("data_hora_busca") or i.get("data_arquivo"), i["registros"],
            i.get("consulta_submetida"), i.get("campos"), i.get("filtros"),
            i.get("resultados_informados_pela_base"), i["observacao"])) + " |")
    linhas += ["", "## 2. Outros métodos (PRISMA: *other methods*)", "",
               "| Fonte | Arquivo | Data do arquivo | Registros lidos | Observação |", "|---|---|---|---:|---|"]
    for i in inventario:
        if i["grupo"] == "outros":
            linhas.append("| " + " | ".join(md(x) for x in (
                i["fonte"], i["arquivo"], i.get("data_arquivo"), i["registros"], i["observacao"])) + " |")
    sb = R.get("snowball_identificados", {})
    linhas += [
        "", "## 3. Serviços consultados por API", "",
        "| Serviço | Uso | Volume |", "|---|---|---|",
        f"| OpenAlex (api.openalex.org) | Enriquecimento por DOI: resumo, idioma, tipo, links de acesso aberto | "
        f"{sum(1 for i in inventario if i['registros'])} arquivos; cache em `cache/openalex_doi.json` |",
        f"| OpenAlex | Snowballing regressivo (referências dos incluídos) | {sb.get('Snowballing regressivo', 0)} registros novos |",
        f"| OpenAlex | Snowballing progressivo (trabalhos que citam os incluídos) | {sb.get('Snowballing progressivo', 0)} registros novos |",
        "| OpenAlex + Semantic Scholar | Busca complementar `scripts/buscar_artigos.py` (consulta própria, ver `artigos/consulta.txt`) | ver seção 2 |",
        "| Repositórios das editoras e de acesso aberto | Download dos textos completos (CO5) | "
        f"{R.get('textos_buscados', 0)} relatos buscados |",
        "", "## 4. Busca diária automática", "",
        "A busca agendada (`scripts/atualizacao_diaria_artigos.sh`, timer `busca-artigos`) grava em "
        "`artigos/atualizacoes/` e **não entra** nesta revisão, cuja busca tem data fixa. "
        "Novos estudos só entram numa atualização formal da revisão, com nova data registrada.", "",
        "## 5. Desvios em relação ao protocolo", "",
    ]
    faltam = [i["fonte"] for i in inventario if i["grupo"] == "bases" and i["arquivo"] == "-"]
    sem_consulta = [i["fonte"] for i in inventario if i["grupo"] == "bases" and i["arquivo"] != "-"
                    and (not i.get("consulta_submetida") or i["consulta_submetida"].startswith("NÃO ARQUIVADA"))]
    if faltam:
        linhas.append(f"- Bases previstas sem exportação: {', '.join(faltam)}.")
    if sem_consulta:
        linhas.append(f"- Consulta exata não arquivada: {', '.join(sem_consulta)} "
                      "(preencher em `Metodologia de Pesquisa/exportacoes_capes/registro_buscas.csv`).")
    linhas.append("- Triagem e elegibilidade aplicadas por regras explícitas (assistidas por computador), "
                  "pendentes de validação do avaliador em `dados/09_validacao_avaliador.csv`.")
    (BASE / "registro_fontes_consultadas.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


# ── Principal ────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sem-rede", action="store_true")
    ap.add_argument("--max-textos", type=int, default=10_000,
                    help="máximo de textos completos buscados (padrão 10.000)")
    args = ap.parse_args()
    global MAX_TEXTOS
    MAX_TEXTOS = args.max_textos
    for d in (DADOS, CACHE, TEXTOS_PDF, TEXTOS_TXT):
        d.mkdir(parents=True, exist_ok=True)
    s = sessao()
    R = {"data_execucao": date.today().isoformat(), "data_limite_protocolo": DATA_LIMITE.isoformat(),
         "max_textos": MAX_TEXTOS}

    print("▶ 01 identificação")
    registros, inventario = etapa_identificacao()
    R["inventario"] = inventario
    ident = Counter((r["grupo"], r["fonte"]) for r in registros)
    R["identificados"] = {f"{g}|{f}": n for (g, f), n in ident.items()}
    print("   ", dict(Counter(r["grupo"] for r in registros)))

    print("▶ 02 enriquecimento (OpenAlex por DOI)")
    etapa_enriquecimento(registros, s, args.sem_rede)
    gravar("01_registros_identificados.csv", registros,
           ["id", "fonte", "grupo", "titulo", "ano", "doi", "autores", "veiculo", "tipo_bruto", "tipo", "idioma"])

    print("▶ 03 deduplicação")
    unicos, dup = etapa_deduplicacao(registros)
    R["duplicatas"] = dict(Counter(r["grupo"] for r in dup if r["decisao"].startswith("duplicata")))
    R["duplicatas_entre_grupos"] = sum(1 for r in dup if "entre grupos" in r["decisao"])
    R["sem_titulo"] = sum(1 for r in dup if r["decisao"].startswith("sem título"))
    R["unicos"] = dict(Counter(r["grupo"] for r in unicos))

    print("▶ 04 critérios objetivos")
    aprovados = etapa_objetivos(unicos)
    R["co"] = {g: dict(Counter(r["co_decisao"].split(" (")[0] for r in unicos if r["grupo"] == g)) for g in ("bases", "outros")}

    print("▶ 05 triagem")
    seguem = etapa_triagem(aprovados)
    R["triagem"] = {g: dict(Counter(r["triagem"] for r in aprovados if r["grupo"] == g)) for g in ("bases", "outros")}

    print(f"▶ 06 texto completo ({len(seguem)} relatos)")
    etapa_texto_completo(seguem, s, args.sem_rede)
    incluidos, eleg = etapa_elegibilidade(seguem)
    R["recuperacao"] = {g: dict(Counter(("recuperado" if r["pdf"] else "nao_recuperado") for r in seguem if r["grupo"] == g)) for g in ("bases", "outros")}
    R["elegibilidade"] = {g: dict(Counter(r["elegibilidade"] for r in eleg if r["grupo"] == g)) for g in ("bases", "outros")}

    print("▶ 08 snowballing")
    cand = etapa_snowballing(incluidos, unicos, s, args.sem_rede)
    R["snowball_identificados"] = dict(Counter(r["fonte"] for r in cand))
    cand_ok = etapa_objetivos(cand, arquivo=None)
    R["snowball_co"] = dict(Counter(r["co_decisao"].split(" (")[0] for r in cand))
    cand_seg = etapa_triagem(cand_ok, arquivo=None)
    R["snowball_triagem"] = dict(Counter(r["triagem"] for r in cand_ok))
    etapa_texto_completo(cand_seg, s, args.sem_rede)
    inc_sb, eleg_sb = etapa_elegibilidade(cand_seg)
    R["snowball_recuperacao"] = dict(Counter(("recuperado" if r["pdf"] else "nao_recuperado") for r in cand_seg))
    R["snowball_elegibilidade"] = dict(Counter(r["elegibilidade"] for r in eleg_sb))
    gravar("08_snowballing.csv", cand, ["id", "fonte", "titulo", "ano", "doi", "tipo", "co_decisao", "triagem",
                                         "recuperacao", "elegibilidade"])

    # grava triagem/elegibilidade consolidadas (inclui snowballing)
    todos_eleg = eleg + eleg_sb
    gravar("06_07_texto_completo_elegibilidade.csv", todos_eleg,
           ["id", "fontes", "grupo", "titulo", "ano", "doi", "veiculo", "recuperacao", "pdf", "palavras",
            "n_CI1", "n_CI2", "n_CI3", "n_CI4", "elegibilidade"])

    print("▶ 09 qualidade e extração")
    finais = incluidos + inc_sb
    ext = etapa_qualidade_extracao(finais)
    cols = ["id", "titulo", "ano", "autores", "veiculo", "doi", "fontes", "grupo", "tipo"] + list(CATEGORIAS) + \
           ["pm_integrada_decisao", "Q1", "Q2", "Q3", "Q4", "Q_total", "palavras", "contexto_publico_CI4"]
    gravar("09_extracao_qualidade.csv", ext, cols)
    val = [{"id": e["id"], "titulo": e["titulo"], "ano": e["ano"], "doi": e["doi"],
            "decisao_automatica": "incluído", "decisao_avaliador": "", "motivo_se_excluir": "",
            "Q1_avaliador": "", "Q2_avaliador": "", "Q3_avaliador": "", "Q4_avaliador": "", "observacoes": ""} for e in ext]
    gravar("09_validacao_avaliador.csv", val, list(val[0].keys()) if val else ["id"])
    R["incluidos"] = {"bases": sum(r["grupo"] == "bases" for r in incluidos),
                      "outros": sum(r["grupo"] == "outros" for r in incluidos), "snowballing": len(inc_sb)}
    R["n_incluidos"] = len(finais)
    R["textos_buscados"] = _textos_usados
    gerar_registro_fontes(inventario, R)
    (BASE / "resultados_prisma.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(R["incluidos"], ensure_ascii=False), "→ total", len(finais))
    return 0


if __name__ == "__main__":
    sys.exit(main())

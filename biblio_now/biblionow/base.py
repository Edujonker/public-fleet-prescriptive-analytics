#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca bibliográfica para embasar o projeto e download dos PDFs de acesso aberto.

Consulta (a mesma em todas as fontes):
  (método: prescritiva, preditiva, apoio à decisão, anomalias, fraude, risco)
  AND (XAI / interpretabilidade / transparência algorítmica)
  AND (setor público, governo, compras públicas, tributos, auditabilidade, accountability)

Por que não o Google Scholar
  O Google Scholar não tem API e os termos de uso do Google proíbem consultas
  automatizadas; scripts recebem CAPTCHA e bloqueio de IP. Este script usa
  duas bases com API oficial e gratuita, que indexam os mesmos periódicos:
    - OpenAlex          (principal; busca booleana em título e resumo)
    - Semantic Scholar  (complementar; sem chave costuma responder 429)
  O link equivalente do Google Scholar é gravado em artigos/consulta.txt
  para conferência manual no navegador.

O que é baixado
  Somente PDFs de acesso aberto (licença do autor ou da editora). O script
  não contorna paywall. Para os demais, o CSV traz o DOI e o link da página.

Saídas em  artigos/
  *.pdf              artigos baixados (ano_autor_titulo.pdf)
  resultados.csv     todos os resultados, com status do PDF (separador ;)
  referencias.bib    BibTeX de todos os resultados
  consulta.txt       consulta usada, data, contagens e link do Google Scholar

Uso
  python3 scripts/buscar_artigos.py                       # 500 resultados, até 100 PDFs
  python3 scripts/buscar_artigos.py --max-resultados 2000 --max-pdfs 300
  python3 scripts/buscar_artigos.py --ano-min 2018 --ordem citacoes
  python3 scripts/buscar_artigos.py --sem-pdf             # só metadados
  python3 scripts/buscar_artigos.py --fontes openalex     # sem Semantic Scholar
  python3 scripts/buscar_artigos.py --ampla               # OpenAlex com radicalização

Fidelidade aos termos
  Por padrão o OpenAlex busca os termos literais (search...exact). Com
  radicalização, "accountability" casaria "accounting" e "government" casaria
  "governance". O Semantic Scholar sempre radicaliza; por isso cada registro é
  conferido no título e no resumo e só os que contêm os 3 grupos têm o PDF
  baixado (--incluir-parciais baixa os demais).

Chaves opcionais (gratuitas), por variável de ambiente
  OPENALEX_API_KEY   cota diária 10x maior  (https://openalex.org/settings/api-key)
  S2_API_KEY         evita o erro 429       (https://www.semanticscholar.org/product/api)

Pode ser executado de novo: PDFs já baixados são mantidos e não são baixados outra vez.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import requests

ROOT = Path(__file__).resolve().parent.parent
SAIDA_PADRAO = ROOT / "artigos"

# ── Semântica da busca ───────────────────────────────────────────────────────
GRUPOS = {
    "metodo": [
        "prescriptive analytics", "predictive analytics", "decision support",
        "anomaly detection", "fraud detection", "risk assessment",
    ],
    "xai": [
        "explainable artificial intelligence", "explainable AI", "XAI",
        "interpretable machine learning", "algorithmic transparency",
    ],
    "setor_publico": [
        "public sector", "government", "public administration",
        "public procurement", "tax", "auditability", "accountability",
    ],
}

OPENALEX_URL = "https://api.openalex.org/works"
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
USER_AGENT = "buscar_artigos/1.0 (pesquisa academica PPGCAP/UDESC; python-requests)"
PDF_MAX_BYTES = 60 * 1024 * 1024  # 60 MB


# ── Montagem das consultas ───────────────────────────────────────────────────
def consulta_booleana(op_e: str, op_ou: str) -> str:
    blocos = []
    for termos in GRUPOS.values():
        blocos.append("(" + f" {op_ou} ".join(f'"{t}"' for t in termos) + ")")
    return f" {op_e} ".join(blocos)


CONSULTA_OPENALEX = consulta_booleana("AND", "OR")   # sintaxe OpenAlex / Google Scholar
CONSULTA_S2 = consulta_booleana("+", "|")            # sintaxe Semantic Scholar (bulk)


# ── HTTP com nova tentativa ──────────────────────────────────────────────────
def get_json(sessao, url, params, headers=None, tentativas=6, rotulo=""):
    espera = 2.0
    for i in range(1, tentativas + 1):
        try:
            r = sessao.get(url, params=params, headers=headers, timeout=(15, 90))
        except requests.RequestException as e:
            print(f"   [{rotulo}] erro de rede ({e.__class__.__name__}); nova tentativa em {espera:.0f}s")
            time.sleep(espera)
            espera = min(espera * 2, 60)
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            ra = r.headers.get("Retry-After")
            pausa = float(ra) if ra and ra.replace(".", "", 1).isdigit() else espera
            pausa = min(pausa, 300)
            print(f"   [{rotulo}] HTTP {r.status_code}; tentativa {i}/{tentativas}, aguardando {pausa:.0f}s")
            time.sleep(pausa)
            espera = min(espera * 2, 180)
            continue
        # erro definitivo (400, 401, 403...)
        try:
            msg = r.json()
        except ValueError:
            msg = r.text[:300]
        raise RuntimeError(f"[{rotulo}] HTTP {r.status_code}: {msg}")
    raise RuntimeError(f"[{rotulo}] sem resposta válida após {tentativas} tentativas")


# ── OpenAlex ─────────────────────────────────────────────────────────────────
def resumo_de_indice(indice):
    """OpenAlex entrega o resumo como índice invertido {palavra: [posições]}."""
    if not indice:
        return ""
    pos = {}
    for palavra, lista in indice.items():
        for p in lista:
            pos[p] = palavra
    return " ".join(pos[k] for k in sorted(pos))


def buscar_openalex(sessao, max_resultados, ano_min, ordem, ampla=False):
    chave = os.environ.get("OPENALEX_API_KEY", "").strip()
    headers = {"Authorization": f"Bearer {chave}"} if chave else None
    # Sem chave, buscas com muitos operadores booleanos: 1 requisição/s.
    pausa = 0.3 if chave else 1.2
    # Exata (padrão): termos literais. Ampla: com radicalização, que também casa
    # "accounting" para "accountability" e "governance" para "government".
    campo = "search.title_and_abstract" if ampla else "search.title_and_abstract.exact"
    params = {
        campo: CONSULTA_OPENALEX,
        "per_page": 100,
        "select": ("id,doi,display_name,publication_year,authorships,primary_location,"
                   "best_oa_location,locations,open_access,cited_by_count,"
                   "abstract_inverted_index,type"),
    }
    # Pareceres de revisores e paratextos (capas, sumários) não são artigos.
    filtros = ["type:!peer-review", "type:!paratext"]
    if ano_min:
        filtros.append(f"publication_year:>{ano_min - 1}")
    params["filter"] = ",".join(filtros)
    if ordem == "citacoes":
        params["sort"] = "cited_by_count:desc"
    elif ordem == "recentes":
        params["sort"] = "publication_date:desc"

    email = os.environ.get("OPENALEX_EMAIL", "").strip()
    if email:
        params["mailto"] = email          # "polite pool": menos erros 429
    # Com chave de API, paginação por cursor (sem limite). Sem chave, o OpenAlex só aceita
    # paginação por página, que vai até 10.000 resultados (100 páginas de 100).
    registros, total, pagina = [], None, 1
    if chave:
        params["cursor"] = "*"
    while len(registros) < max_resultados:
        if not chave:
            if pagina > 100:
                print("   OpenAlex: limite de 10.000 resultados sem chave de API (OPENALEX_API_KEY)")
                break
            params["page"] = pagina
        try:
            dados = get_json(sessao, OPENALEX_URL, params, headers, tentativas=10, rotulo="OpenAlex")
        except RuntimeError as e:
            if chave and ("key_not_activated" in str(e) or "HTTP 401" in str(e)):
                # Chave ainda não ativada (link do e-mail não clicado) ou inválida: segue sem chave,
                # com o limite de 10.000 resultados e a cota menor do acesso sem chave.
                print("   OpenAlex: chave não aceita (", "não ativada" if "key_not_activated" in str(e) else "inválida",
                      "); seguindo sem chave", sep="")
                chave, headers, pausa = "", None, 1.2
                params.pop("cursor", None)
                continue
            raise
        if total is None:
            total = dados.get("meta", {}).get("count", 0)
            print(f"   OpenAlex: {total} trabalhos correspondem à consulta")
        lote = dados.get("results", [])
        if not lote:
            break
        for w in lote:
            registros.append(normalizar_openalex(w))
            if len(registros) >= max_resultados:
                break
        if chave:
            params["cursor"] = (dados.get("meta") or {}).get("next_cursor")
            if not params["cursor"]:
                break
        elif pagina * 100 >= (total or 0):
            break
        pagina += 1
        time.sleep(pausa)
    return registros, total or 0


def normalizar_openalex(w):
    autores = [a.get("author", {}).get("display_name") or "" for a in (w.get("authorships") or [])]
    prim = w.get("primary_location") or {}
    fonte = prim.get("source") or {}
    pdfs = []
    best = w.get("best_oa_location") or {}
    for loc in [best] + list(w.get("locations") or []):
        u = (loc or {}).get("pdf_url")
        if u and u not in pdfs:
            pdfs.append(u)
    doi = (w.get("doi") or "").replace("https://doi.org/", "").strip()
    return {
        "titulo": (w.get("display_name") or "").strip(),
        "ano": w.get("publication_year") or "",
        "autores": [a for a in autores if a],
        "veiculo": fonte.get("display_name") or "",
        "tipo": w.get("type") or "",
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else (prim.get("landing_page_url") or w.get("id") or ""),
        "citacoes": w.get("cited_by_count") or 0,
        "resumo": resumo_de_indice(w.get("abstract_inverted_index")),
        "acesso_aberto": bool((w.get("open_access") or {}).get("is_oa")),
        "pdf_urls": pdfs,
        "fonte": "OpenAlex",
        "id_openalex": w.get("id") or "",
        "licenca": best.get("license") or "",
        "versao_oa": best.get("version") or "",
        "status_oa": (w.get("open_access") or {}).get("oa_status") or "",
        "pagina_oa": best.get("landing_page_url") or "",
    }


# ── Semantic Scholar ─────────────────────────────────────────────────────────
def buscar_s2(sessao, max_resultados, ano_min, ordem):
    chave = os.environ.get("S2_API_KEY", "").strip()
    headers = {"x-api-key": chave} if chave else None
    params = {
        "query": CONSULTA_S2,
        "fields": "title,year,authors,venue,externalIds,openAccessPdf,citationCount,abstract,url,publicationTypes",
    }
    if ano_min:
        params["year"] = f"{ano_min}-"
    if ordem == "citacoes":
        params["sort"] = "citationCount:desc"
    elif ordem == "recentes":
        params["sort"] = "publicationDate:desc"

    registros, total = [], None
    while len(registros) < max_resultados:
        # Sem chave, o acesso é compartilhado e responde 429 com frequência: mais tentativas (esperas de 2 s a 3 min).
        dados = get_json(sessao, S2_URL, params, headers, tentativas=5 if chave else 9, rotulo="SemanticScholar")
        if total is None:
            total = dados.get("total", 0)
            print(f"   Semantic Scholar: {total} trabalhos correspondem à consulta")
        for p in dados.get("data") or []:
            registros.append(normalizar_s2(p))
            if len(registros) >= max_resultados:
                break
        token = dados.get("token")
        if not token:
            break
        params["token"] = token
        time.sleep(1.1)
    return registros, total or 0


def normalizar_s2(p):
    ext = p.get("externalIds") or {}
    doi = (ext.get("DOI") or "").strip()
    oa = p.get("openAccessPdf") or {}
    pdf = (oa.get("url") or "").strip()
    return {
        "titulo": (p.get("title") or "").strip(),
        "ano": p.get("year") or "",
        "autores": [a.get("name") for a in (p.get("authors") or []) if a.get("name")],
        "veiculo": p.get("venue") or "",
        "tipo": ",".join(p.get("publicationTypes") or []),
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else (p.get("url") or ""),
        "citacoes": p.get("citationCount") or 0,
        "resumo": p.get("abstract") or "",
        "acesso_aberto": bool(pdf),
        "pdf_urls": [pdf] if pdf else [],
        "fonte": "SemanticScholar",
        "id_s2": p.get("paperId") or "",
        "licenca": oa.get("license") or "",
        "status_oa": (oa.get("status") or "").lower(),
    }


# ── União, conferência da semântica e nomes de arquivo ───────────────────────
def chave_registro(r):
    if r["doi"]:
        return "doi:" + r["doi"].lower()
    return "tit:" + re.sub(r"[^a-z0-9]", "", r["titulo"].lower())[:120]


def unir(listas):
    unidos, indice = [], {}
    for lista in listas:
        for r in lista:
            k = chave_registro(r)
            if not r["titulo"]:
                continue
            if k in indice:
                base = indice[k]
                for u in r["pdf_urls"]:
                    if u not in base["pdf_urls"]:
                        base["pdf_urls"].append(u)
                base["acesso_aberto"] = base["acesso_aberto"] or r["acesso_aberto"]
                if not base["resumo"] and r["resumo"]:
                    base["resumo"] = r["resumo"]
                if r["fonte"] not in base["fonte"]:
                    base["fonte"] += "+" + r["fonte"]
                for campo in ("id_openalex", "id_s2", "licenca", "versao_oa", "status_oa", "pagina_oa"):
                    if not base.get(campo) and r.get(campo):
                        base[campo] = r[campo]
            else:
                indice[k] = r
                unidos.append(r)
    return unidos


def padrao_termo(termo):
    palavras = termo.lower().split()
    corpo = r"[\s\-]+".join(re.escape(p) for p in palavras)
    # Termos curtos (tax, XAI) só aceitam plural, para não casar "taxonomy".
    sufixo = r"(?:es|s)?\b" if len(termo) <= 3 else r"\w*"
    return re.compile(r"\b" + corpo + sufixo)


PADROES = {g: [padrao_termo(t) for t in termos] for g, termos in GRUPOS.items()}


def conferir_semantica(r):
    """As bases já filtram no servidor; aqui se confere no texto que veio de volta."""
    texto = (r["titulo"] + " " + r["resumo"]).lower()
    atende = {g: any(p.search(texto) for p in pads) for g, pads in PADROES.items()}
    if all(atende.values()):
        return "ok"
    if not r["resumo"]:
        return "sem_resumo"
    faltam = [g for g, v in atende.items() if not v]
    return "parcial (falta: " + ", ".join(faltam) + ")"


def ascii_slug(texto, limite):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")
    return t[:limite].rstrip("_") or "sem_titulo"


def sobrenome(r):
    if not r["autores"]:
        return "anon"
    return ascii_slug(r["autores"][0].split()[-1], 25).lower()


def nome_arquivo(r):
    slug = ascii_slug(r["titulo"], 70)
    if slug == "sem_titulo":   # título só com caracteres não latinos: diferencia pelo DOI ou pelo título
        import hashlib
        slug += "_" + hashlib.sha1((r["doi"] or r["titulo"]).encode("utf-8")).hexdigest()[:10]
    return f"{r['ano'] or 'sd'}_{sobrenome(r)}_{slug}.pdf"


# ── Download ─────────────────────────────────────────────────────────────────
# Muitos portais de revistas (OJS, Cloudflare) recusam a conexão quando o
# User-Agent não é de navegador. Teste de 16/11/2026 com 15 links que falharam:
# 0 PDFs com o User-Agent do script, 6 com o de navegador. O download usa,
# por isso, cabeçalhos de navegador; as consultas às APIs continuam com
# USER_AGENT, que identifica o projeto. Só são gravados arquivos que começam
# com %PDF, e a verificação de certificado TLS nunca é desligada.
HEADERS_PDF = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/pdf,application/octet-stream;q=0.9,text/html;q=0.8,*/*;q=0.5",
    "Accept-Language": "en,pt-BR;q=0.8",
}
ERROS_TRANSITORIOS = (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError)
_META_PDF = re.compile(r"""<meta[^>]+name=["'](?:citation_pdf_url|eprints\.document_url)["'][^>]+content=["']([^"']+)["']""", re.I)
_META_PDF2 = re.compile(r"""<meta[^>]+content=["']([^"']+)["'][^>]+name=["']citation_pdf_url["']""", re.I)


def _pdf_na_pagina(html_txt, base):
    """Link do PDF declarado na própria página do artigo (meta citation_pdf_url, padrão Highwire/Google Scholar)."""
    from urllib.parse import urljoin
    m = _META_PDF.search(html_txt) or _META_PDF2.search(html_txt)
    return urljoin(base, m.group(1).replace("&amp;", "&")) if m else None


def _baixar_um(sessao, url, destino, meta=None):
    """Uma tentativa num link. Retorna (ok, motivo, link_pdf_encontrado_na_pagina).
    Se `meta` for um dicionário, recebe os dados de rastreabilidade da resposta que gerou o arquivo."""
    inicio = datetime.now().astimezone()
    with sessao.get(url, stream=True, timeout=(15, 90), allow_redirects=True, headers=HEADERS_PDF) as r:
        if r.status_code == 202 and any(k.lower() == "x-amzn-waf-action" for k in r.headers):
            # Desafio anti-robô (AWS WAF, ex.: IEEE Xplore): exige navegador com JavaScript e, em geral, assinatura.
            # Não é erro passageiro; não tentamos contornar. Nova tentativa só após o prazo de falha definitiva.
            return False, f"bloqueado por proteção anti-robô do site ({urlparse(r.url).hostname})", None
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}", None
        it = r.iter_content(chunk_size=65536)
        primeiro = next(it, b"")
        if not primeiro.lstrip().startswith(b"%PDF"):
            tipo = r.headers.get("Content-Type", "")
            pagina = None
            if "html" in tipo.lower():
                corpo = primeiro + b"".join(b for _, b in zip(range(30), it))  # até ~2 MB
                pagina = _pdf_na_pagina(corpo.decode("utf-8", "ignore"), r.url)
            return False, "o link devolveu uma página, não um PDF", pagina
        tmp = destino.with_suffix(".parcial")
        tamanho = 0
        with open(tmp, "wb") as f:
            f.write(primeiro)
            tamanho += len(primeiro)
            for bloco in it:
                tamanho += len(bloco)
                if tamanho > PDF_MAX_BYTES:
                    break
                f.write(bloco)
        if tamanho > PDF_MAX_BYTES:
            tmp.unlink(missing_ok=True)
            return False, "arquivo maior que 60 MB", None
        tmp.rename(destino)
        if meta is not None:
            fim = datetime.now().astimezone()
            h = r.headers
            meta.update({
                "url_solicitada": url, "url_final": r.url,
                "redirecionamentos": [x.url for x in r.history] + ([r.url] if r.history else []),
                "status_http": r.status_code, "content_type": h.get("Content-Type", ""),
                "content_length": h.get("Content-Length", ""), "last_modified": h.get("Last-Modified", ""),
                "etag": h.get("ETag", ""), "servidor_http": h.get("Server", ""),
                "host": urlparse(r.url).hostname or "", "user_agent": HEADERS_PDF.get("User-Agent", ""),
                "inicio_download": inicio.isoformat(timespec="seconds"), "fim_download": fim.isoformat(timespec="seconds"),
                "duracao_s": round((fim - inicio).total_seconds(), 2), "bytes": tamanho,
            })
        return True, url, None


def baixar_pdf(sessao, urls, destino, tentativas=2, meta=None):
    """Tenta cada URL; se a resposta for a página do artigo, segue o link de PDF declarado nela.
    Erros de rede passageiros têm nova tentativa. Só grava se o conteúdo começar com %PDF.
    Retorna (True, url_do_pdf) ou (False, motivo)."""
    motivo = "sem link de PDF aberto"
    fila, vistos = [u for u in urls if u], set()
    while fila:
        url = fila.pop(0)
        if url in vistos:
            continue
        vistos.add(url)
        for k in range(1, tentativas + 1):
            try:
                ok, info, pagina = _baixar_um(sessao, url, destino, meta)
                if meta is not None:
                    meta.setdefault("tentativas", []).append({"url": url, "tentativa": k, "resultado": "ok" if ok else info,
                                                              "quando": datetime.now().astimezone().isoformat(timespec="seconds")})
                if ok:
                    return True, info
                motivo = info
                if pagina and pagina not in vistos:
                    fila.insert(0, pagina)
                break
            except requests.exceptions.SSLError:
                motivo = "erro de certificado TLS do site"
                if meta is not None:
                    meta.setdefault("tentativas", []).append({"url": url, "tentativa": k, "resultado": motivo,
                                                              "quando": datetime.now().astimezone().isoformat(timespec="seconds")})
                break
            except ERROS_TRANSITORIOS as e:
                motivo = f"erro de rede ({e.__class__.__name__})"
                if meta is not None:
                    meta.setdefault("tentativas", []).append({"url": url, "tentativa": k, "resultado": motivo,
                                                              "quando": datetime.now().astimezone().isoformat(timespec="seconds")})
                if k < tentativas:
                    time.sleep(5 * k)
            except requests.RequestException as e:
                motivo = f"erro de rede ({e.__class__.__name__})"
                if meta is not None:
                    meta.setdefault("tentativas", []).append({"url": url, "tentativa": k, "resultado": f"{motivo}: {str(e)[:120]}",
                                                              "quando": datetime.now().astimezone().isoformat(timespec="seconds")})
                break
            finally:
                destino.with_suffix(".parcial").unlink(missing_ok=True)  # resto de download interrompido
        time.sleep(1.0)
    return False, motivo


def links_unpaywall(sessao, doi, email):
    """Links de PDF de acesso aberto registrados no Unpaywall para o DOI (exige e-mail de contato)."""
    if not (doi and email):
        return []
    try:
        r = sessao.get(f"https://api.unpaywall.org/v2/{quote_plus(doi, safe='/')}", params={"email": email}, timeout=(10, 30))
        if r.status_code != 200:
            return []
        locs = r.json().get("oa_locations") or []
    except (requests.RequestException, ValueError):
        return []
    return [l.get("url_for_pdf") for l in locs if l.get("url_for_pdf")] + [l.get("url") for l in locs if l.get("url")]


# ── Saídas ───────────────────────────────────────────────────────────────────
def bib_escape(s):
    return str(s).replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def gravar_bib(registros, caminho):
    usadas = set()
    linhas = []
    for r in registros:
        palavra = next((p for p in re.findall(r"[A-Za-z]{4,}", ascii_slug(r["titulo"], 200).replace("_", " "))), "art")
        base = f"{sobrenome(r)}{r['ano'] or 'sd'}{palavra.lower()}"
        chave, n = base, 1
        while chave in usadas:
            n += 1
            chave = f"{base}{chr(96 + n)}"
        usadas.add(chave)
        tipo = "inproceedings" if "proceed" in (r["tipo"] or "").lower() or "conference" in (r["tipo"] or "").lower() else "article"
        campos = [
            ("title", r["titulo"]),
            ("author", " and ".join(r["autores"])),
            ("year", r["ano"]),
            ("journal" if tipo == "article" else "booktitle", r["veiculo"]),
            ("doi", r["doi"]),
            ("url", r["url"]),
        ]
        corpo = ",\n".join(f"  {k} = {{{bib_escape(v)}}}" for k, v in campos if v)
        linhas.append(f"@{tipo}{{{chave},\n{corpo}\n}}\n")
    caminho.write_text("\n".join(linhas), encoding="utf-8")


def gravar_csv(registros, caminho):
    colunas = ["n", "titulo", "ano", "autores", "veiculo", "doi", "citacoes", "fonte",
               "verificacao_semantica", "acesso_aberto", "status_pdf", "arquivo_pdf", "url", "visto_em", "url_pdf"]
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(colunas)
        for i, r in enumerate(registros, 1):
            w.writerow([i, r["titulo"], r["ano"], "; ".join(r["autores"][:6]) + (" et al." if len(r["autores"]) > 6 else ""),
                        r["veiculo"], r["doi"], r["citacoes"], r["fonte"], r["verificacao"],
                        "sim" if r["acesso_aberto"] else "não", r["status_pdf"], r["arquivo_pdf"], r["url"],
                        r.get("visto_em", ""), r.get("url_pdf", "")])


def gravar_consulta(caminho, args, totais, registros):
    scholar = "https://scholar.google.com/scholar?q=" + quote_plus(CONSULTA_OPENALEX)
    contagem = {}
    for r in registros:
        chave = r["status_pdf"].split(" (")[0]
        contagem[chave] = contagem.get(chave, 0) + 1
    verif = {}
    for r in registros:
        chave = r["verificacao"].split(" (")[0]
        verif[chave] = verif.get(chave, 0) + 1
    texto = f"""Busca bibliográfica — {datetime.now():%d/%m/%Y %H:%M}

Consulta (OpenAlex, campo título + resumo):
{CONSULTA_OPENALEX}

Consulta (Semantic Scholar, sintaxe bulk):
{CONSULTA_S2}

Parâmetros: max_resultados={args.max_resultados}, max_pdfs={args.max_pdfs}, ano_min={args.ano_min or '-'}, ordem={args.ordem}, fontes={args.fontes}
Correspondência no OpenAlex: {'ampla (com radicalização)' if args.ampla else 'exata (termos literais)'}; Semantic Scholar sempre radicaliza.
Só são baixados PDFs com os 3 grupos confirmados no título/resumo{' (exceto com --incluir-parciais)' if not args.incluir_parciais else ' — desativado por --incluir-parciais'}.

Correspondências informadas pelas bases: {json.dumps(totais, ensure_ascii=False)}
Registros únicos gravados: {len(registros)}
Conferência da semântica no título/resumo: {json.dumps(verif, ensure_ascii=False)}
Status dos PDFs: {json.dumps(contagem, ensure_ascii=False)}

Mesma consulta no Google Scholar (para conferência manual no navegador):
{scholar}
Observação: consultas longas podem ser encurtadas pelo Google Scholar; o número
de resultados lá não é comparável ao das APIs.
"""
    caminho.write_text(texto, encoding="utf-8")


def carregar_vistos(vistos_f, resultados_anteriores):
    """Registro {chave: data em que o artigo apareceu pela primeira vez}.
    Na primeira vez, os resultados de buscas anteriores entram como 'anterior',
    para não serem contados como inéditos."""
    if vistos_f.exists():
        return json.loads(vistos_f.read_text(encoding="utf-8"))
    vistos = {}
    if resultados_anteriores.exists():
        for r in csv.DictReader(open(resultados_anteriores, encoding="utf-8-sig"), delimiter=";"):
            vistos[chave_registro({"doi": r.get("doi", ""), "titulo": r.get("titulo", "")})] = "anterior"
    return vistos


def _host(url):
    from urllib.parse import urlparse
    return urlparse(url).netloc.lower()


def baixar_em_paralelo(fila, n_threads, email_upw="", passadas=2):
    """Baixa os PDFs da fila [(registro, destino)] com n_threads simultâneos, no máximo um por site
    de cada vez. Itens com erro de rede passageiro voltam numa segunda passada, no fim."""
    import threading
    from concurrent.futures import ThreadPoolExecutor
    local = threading.local()
    travas, trava_g = {}, threading.Lock()
    cont = {"n": 0}

    def sessao():
        if not hasattr(local, "s"):
            local.s = requests.Session()
            local.s.headers["User-Agent"] = USER_AGENT
        return local.s

    def tarefa(item):
        r, destino = item
        urls = list(r["pdf_urls"])
        if email_upw and r["doi"]:
            urls += [u for u in links_unpaywall(sessao(), r["doi"], email_upw) if u not in urls]
        if not urls:
            r["status_pdf"] = "sem_pdf_aberto"
            return
        with trava_g:
            tv = travas.setdefault(_host(urls[0]), threading.Lock())
        with tv:
            ok, info = baixar_pdf(sessao(), urls, destino)
        if ok:
            r["status_pdf"], r["arquivo_pdf"], r["url_pdf"] = "baixado", destino.name, info
            with trava_g:
                cont["n"] += 1
                print(f"   [{cont['n']:>4}] {destino.name}", flush=True)
        else:
            r["status_pdf"] = f"falhou ({info})"

    pendentes = list(fila)
    for passada in range(1, passadas + 1):
        if not pendentes:
            break
        if passada > 1:
            print(f"   Nova tentativa para {len(pendentes)} PDFs com erro de rede passageiro...", flush=True)
            time.sleep(30)
        with ThreadPoolExecutor(max_workers=max(1, n_threads)) as ex:
            list(ex.map(tarefa, pendentes))
        pendentes = [(r, d) for r, d in pendentes if r["status_pdf"].startswith("falhou (erro de rede")]
    return cont["n"]


# ── Controle de downloads (evita baixar de novo e repetir falhas definitivas) ─
DIAS_NOVA_TENTATIVA_FALHA_DEFINITIVA = 30
TRANSITORIAS = ("HTTP 429", "HTTP 202", "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504", "HTTP 520", "erro de rede")


def carregar_controle(pasta_pdf: Path):
    """{chave_registro: {"arquivo", "status", "tentado_em", "tentativas"}}. Na primeira vez, monta a partir dos
    resultados.csv já gravados (pasta principal e execuções diárias), para reconhecer os PDFs que já existem."""
    f = pasta_pdf / "controle_downloads.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    ctl = {}
    fontes = [pasta_pdf / "resultados.csv"] + sorted((pasta_pdf / "atualizacoes").glob("*/resultados.csv"))
    for csvf in fontes:
        if not csvf.exists():
            continue
        dia = csvf.parent.name if csvf.parent.name[:2] == "20" else ""
        for r in csv.DictReader(open(csvf, encoding="utf-8-sig"), delimiter=";"):
            k = chave_registro({"doi": norm_doi_simples(r.get("doi", "")), "titulo": r.get("titulo", "")})
            arq = r.get("arquivo_pdf") or ""
            if arq and (pasta_pdf / arq).exists():
                ctl[k] = {"arquivo": arq, "status": "baixado", "tentado_em": dia, "tentativas": 1}
            elif r.get("status_pdf", "").startswith("falhou") and k not in ctl:
                ctl[k] = {"arquivo": "", "status": r["status_pdf"], "tentado_em": dia, "tentativas": 1}
    return ctl


def norm_doi_simples(d):
    d = (d or "").strip().lower()
    for pre in ("https://doi.org/", "http://doi.org/", "doi:"):
        if d.startswith(pre):
            d = d[len(pre):]
    return d


def pular_por_controle(ent, hoje):
    """Motivo para não tentar de novo hoje, ou None."""
    if not ent or ent.get("status") == "baixado":
        return None
    st, quando = ent.get("status", ""), ent.get("tentado_em", "")
    if not quando:
        return None
    if any(t in st for t in TRANSITORIAS):
        return None if quando < hoje else "tentado hoje"
    try:
        dias = (datetime.strptime(hoje, "%Y-%m-%d") - datetime.strptime(quando, "%Y-%m-%d")).days
    except ValueError:
        return None
    return None if dias >= DIAS_NOVA_TENTATIVA_FALHA_DEFINITIVA else f"falha definitiva em {quando}; nova tentativa após {DIAS_NOVA_TENTATIVA_FALHA_DEFINITIVA} dias"


# ── Principal ────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Busca artigos (OpenAlex + Semantic Scholar) e baixa PDFs de acesso aberto.")
    ap.add_argument("--max-resultados", type=int, default=500, help="máximo de registros por fonte (padrão 500)")
    ap.add_argument("--max-pdfs", type=int, default=100, help="máximo de PDFs a baixar nesta execução (padrão 100)")
    ap.add_argument("--ano-min", type=int, default=None, help="ano mínimo de publicação")
    ap.add_argument("--ordem", choices=["relevancia", "citacoes", "recentes"], default="relevancia")
    ap.add_argument("--fontes", default="openalex,s2", help="openalex, s2 ou openalex,s2 (padrão)")
    ap.add_argument("--sem-pdf", action="store_true", help="só metadados, sem baixar PDFs")
    ap.add_argument("--ampla", action="store_true",
                    help="OpenAlex com radicalização (mais resultados, menos fiéis aos termos)")
    ap.add_argument("--incluir-parciais", action="store_true",
                    help="baixar também PDFs cujo título/resumo não confirma os 3 grupos")
    ap.add_argument("--saida", default=str(SAIDA_PADRAO), help="pasta dos relatórios (padrão: artigos/)")
    ap.add_argument("--paralelo", type=int, default=6, help="downloads simultâneos (padrão 6; um por site de cada vez)")
    ap.add_argument("--pasta-pdf", default=None,
                    help="pasta dos PDFs e do registro vistos.json (padrão: a mesma de --saida)")
    args = ap.parse_args()

    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    pasta_pdf = Path(args.pasta_pdf) if args.pasta_pdf else saida
    pasta_pdf.mkdir(parents=True, exist_ok=True)
    fontes = {f.strip().lower() for f in args.fontes.split(",")}
    vistos_f = pasta_pdf / "vistos.json"
    vistos = carregar_vistos(vistos_f, pasta_pdf / "resultados.csv")

    sessao = requests.Session()
    sessao.headers["User-Agent"] = USER_AGENT

    print("Consulta:", CONSULTA_OPENALEX, "\n")
    listas, totais = [], {}
    if "openalex" in fontes:
        print("▶ OpenAlex")
        try:
            regs, tot = buscar_openalex(sessao, args.max_resultados, args.ano_min, args.ordem, args.ampla)
            listas.append(regs)
            totais["OpenAlex"] = tot
            print(f"   {len(regs)} registros recebidos")
        except RuntimeError as e:
            print("   OpenAlex indisponível:", e)
    if "s2" in fontes:
        print("▶ Semantic Scholar")
        try:
            regs, tot = buscar_s2(sessao, args.max_resultados, args.ano_min, args.ordem)
            listas.append(regs)
            totais["SemanticScholar"] = tot
            print(f"   {len(regs)} registros recebidos")
        except RuntimeError as e:
            print("   Semantic Scholar indisponível (sem chave é comum o erro 429). Seguindo sem ele.")
            print("  ", e)
            totais["SemanticScholar"] = "indisponível"

    registros = unir(listas)
    if not registros:
        print("Nenhum resultado. Verifique a conexão ou tente mais tarde.")
        return 1
    for r in registros:
        r["verificacao"] = conferir_semantica(r)
        r["status_pdf"] = ""
        r["arquivo_pdf"] = ""
    # Confirmados primeiro (mantendo a ordem das fontes), depois sem resumo, depois parciais.
    prioridade = {"ok": 0, "sem_resumo": 1}
    registros.sort(key=lambda r: prioridade.get(r["verificacao"], 2))
    n_ok = sum(r["verificacao"] == "ok" for r in registros)
    print(f"\n{len(registros)} registros únicos após unir as fontes "
          f"({n_ok} com os 3 grupos confirmados no título/resumo)")

    hoje = datetime.now().strftime("%Y-%m-%d")
    ja_vistos = set(vistos)          # registro antes desta execução
    novos = []
    for r in registros:
        k = chave_registro(r)
        r["visto_em"] = vistos.setdefault(k, hoje)
        if k not in ja_vistos:
            novos.append(r)
    print(f"Inéditos nesta execução (nunca vistos antes): {len(novos)}")

    baixados = 0
    email_upw = os.environ.get("UNPAYWALL_EMAIL", os.environ.get("OPENALEX_EMAIL", "")).strip()
    controle = carregar_controle(pasta_pdf)
    try:
        fila = []
        for r in registros:
            k = chave_registro(r)
            ent = controle.get(k)
            destino = pasta_pdf / nome_arquivo(r)
            if ent and ent.get("arquivo") and (pasta_pdf / ent["arquivo"]).exists():
                # já baixado antes, talvez com outro nome (o 1º autor muda entre as bases)
                r["status_pdf"], r["arquivo_pdf"] = "ja_existia", ent["arquivo"]
            elif destino.exists():
                r["status_pdf"], r["arquivo_pdf"] = "ja_existia", destino.name
                controle[k] = {"arquivo": destino.name, "status": "baixado", "tentado_em": hoje, "tentativas": 1}
            elif (motivo := pular_por_controle(ent, hoje)) and not args.sem_pdf:
                r["status_pdf"] = f"nao_tentado ({motivo})"
            elif args.sem_pdf:
                r["status_pdf"] = "nao_tentado (--sem-pdf)"
            elif r["verificacao"] != "ok" and not args.incluir_parciais:
                r["status_pdf"] = "nao_tentado (semântica não confirmada)"
            elif not r["pdf_urls"] and not (email_upw and r["doi"]):
                r["status_pdf"] = "sem_pdf_aberto"
            elif len(fila) >= args.max_pdfs:
                r["status_pdf"] = "nao_tentado (limite --max-pdfs)"
            else:
                fila.append((r, destino))
        print(f"PDFs a tentar: {len(fila)} ({args.paralelo} downloads simultâneos)")
        import hashlib
        md5 = lambda f: hashlib.md5(f.read_bytes()).hexdigest()
        novos_destinos = {d.name for _, d in fila}
        por_conteudo = {md5(f): f.name for f in pasta_pdf.glob("*.pdf") if f.name not in novos_destinos}
        baixados = baixar_em_paralelo(fila, args.paralelo, email_upw)
        # Mesmo PDF com outro DOI ou título (por exemplo, preprint e versão publicada): mantém o arquivo antigo.
        for r, destino in fila:
            if r["status_pdf"] != "baixado" or not destino.exists():
                continue
            h = md5(destino)
            if h in por_conteudo and por_conteudo[h] != destino.name:
                destino.unlink()
                r["status_pdf"], r["arquivo_pdf"] = "ja_existia", por_conteudo[h]
                baixados -= 1
                print(f"   (repetido: {destino.name} tem o mesmo conteúdo de {por_conteudo[h]}; mantido o anterior)")
            else:
                por_conteudo[h] = destino.name
        for r, destino in fila:
            k = chave_registro(r)
            ant = controle.get(k, {})
            if r["status_pdf"] in ("baixado", "ja_existia") and r["arquivo_pdf"]:
                controle[k] = {"arquivo": r["arquivo_pdf"], "status": "baixado", "tentado_em": hoje,
                               "tentativas": ant.get("tentativas", 0) + 1}
            elif r["status_pdf"].startswith("falhou"):
                controle[k] = {"arquivo": "", "status": r["status_pdf"], "tentado_em": hoje,
                               "tentativas": ant.get("tentativas", 0) + 1}
    except KeyboardInterrupt:
        print("\nInterrompido. Gravando o que já foi obtido...")
        for r in registros:
            if not r["status_pdf"]:
                r["status_pdf"] = "nao_tentado (interrompido)"
    finally:
        gravar_csv(registros, saida / "resultados.csv")
        gravar_csv(novos, saida / "novos.csv")
        gravar_bib(registros, saida / "referencias.bib")
        gravar_consulta(saida / "consulta.txt", args, totais, registros)
        vistos_f.write_text(json.dumps(vistos, ensure_ascii=False, indent=0), encoding="utf-8")
        (pasta_pdf / "controle_downloads.json").write_text(json.dumps(controle, ensure_ascii=False, indent=0), encoding="utf-8")

    print(f"\nPDFs baixados nesta execução: {baixados}")
    print(f"Inéditos: {len(novos)} (lista em novos.csv)")
    print(f"Relatórios: {saida}")
    print(f"PDFs:       {pasta_pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

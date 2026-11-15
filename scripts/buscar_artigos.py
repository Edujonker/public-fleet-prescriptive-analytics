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
from urllib.parse import quote_plus

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
            pausa = min(pausa, 120)
            print(f"   [{rotulo}] HTTP {r.status_code}; tentativa {i}/{tentativas}, aguardando {pausa:.0f}s")
            time.sleep(pausa)
            espera = min(espera * 2, 60)
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

    registros, total, pagina = [], None, 1
    while len(registros) < max_resultados:
        params["page"] = pagina
        dados = get_json(sessao, OPENALEX_URL, params, headers, rotulo="OpenAlex")
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
        if pagina * 100 >= (total or 0):
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
        dados = get_json(sessao, S2_URL, params, headers, tentativas=5, rotulo="SemanticScholar")
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
    return f"{r['ano'] or 'sd'}_{sobrenome(r)}_{ascii_slug(r['titulo'], 70)}.pdf"


# ── Download ─────────────────────────────────────────────────────────────────
def baixar_pdf(sessao, urls, destino):
    """Tenta cada URL; só grava se o conteúdo começar com %PDF."""
    motivo = "sem link de PDF aberto"
    for url in urls:
        try:
            with sessao.get(url, stream=True, timeout=(15, 90), allow_redirects=True) as r:
                if r.status_code != 200:
                    motivo = f"HTTP {r.status_code}"
                    continue
                it = r.iter_content(chunk_size=65536)
                primeiro = next(it, b"")
                if not primeiro.startswith(b"%PDF"):
                    motivo = "o link devolveu uma página, não um PDF"
                    continue
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
                    motivo = "arquivo maior que 60 MB"
                    continue
                tmp.rename(destino)
                return True, url
        except requests.RequestException as e:
            motivo = f"erro de rede ({e.__class__.__name__})"
        finally:
            destino.with_suffix(".parcial").unlink(missing_ok=True)  # resto de download interrompido
            time.sleep(1.0)
    return False, motivo


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
               "verificacao_semantica", "acesso_aberto", "status_pdf", "arquivo_pdf", "url", "visto_em"]
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(colunas)
        for i, r in enumerate(registros, 1):
            w.writerow([i, r["titulo"], r["ano"], "; ".join(r["autores"][:6]) + (" et al." if len(r["autores"]) > 6 else ""),
                        r["veiculo"], r["doi"], r["citacoes"], r["fonte"], r["verificacao"],
                        "sim" if r["acesso_aberto"] else "não", r["status_pdf"], r["arquivo_pdf"], r["url"],
                        r.get("visto_em", "")])


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
    try:
        for i, r in enumerate(registros, 1):
            destino = pasta_pdf / nome_arquivo(r)
            if destino.exists():
                r["status_pdf"], r["arquivo_pdf"] = "ja_existia", destino.name
                continue
            if args.sem_pdf:
                r["status_pdf"] = "nao_tentado (--sem-pdf)"
                continue
            if r["verificacao"] != "ok" and not args.incluir_parciais:
                r["status_pdf"] = "nao_tentado (semântica não confirmada)"
                continue
            if not r["pdf_urls"]:
                r["status_pdf"] = "sem_pdf_aberto"
                continue
            if baixados >= args.max_pdfs:
                r["status_pdf"] = "nao_tentado (limite --max-pdfs)"
                continue
            ok, info = baixar_pdf(sessao, r["pdf_urls"], destino)
            if ok:
                baixados += 1
                r["status_pdf"], r["arquivo_pdf"] = "baixado", destino.name
                print(f"   [{baixados:>3}] {destino.name}")
            else:
                r["status_pdf"] = f"falhou ({info})"
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

    print(f"\nPDFs baixados nesta execução: {baixados}")
    print(f"Inéditos: {len(novos)} (lista em novos.csv)")
    print(f"Relatórios: {saida}")
    print(f"PDFs:       {pasta_pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

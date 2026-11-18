# -*- coding: utf-8 -*-
"""
Biblio-now · validação e análise da ferramenta. Autor: Eduardo Lopes Jonker.

1. testes()      – autotestes de segurança e de integridade do repositório (cada teste devolve o que conferiu);
2. metricas()    – números de uma busca, calculados a partir do resultados.csv gravado por ela;
3. referencia()  – revocação de uma busca frente a uma lista de DOIs/títulos que ela deveria encontrar.

Nada aqui altera o repositório: só lê e confere.
"""
from __future__ import annotations

import csv
import hashlib
import re
import secrets
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

from . import fichamento
from . import seguranca as seg


def _t(grupo, nome, ok, detalhe, alerta=False):
    return {"grupo": grupo, "nome": nome, "ok": bool(ok), "alerta": bool(alerta) and bool(ok), "detalhe": detalhe}


# ---------------------------------------------------------------- 1. autotestes
def testes(repo_raiz: Path, obras: dict, cofre: seg.Cofre, chaves: dict, env: Path, sessao: seg.Sessao) -> dict:
    r = []

    # --- segurança
    v = secrets.token_hex(16)
    try:
        ok = cofre._f.decrypt(cofre._f.encrypt(v.encode())).decode() == v
        r.append(_t("Segurança", "Cofre: cifrar e decifrar", ok, f"Fernet (AES-128-CBC + HMAC-SHA256); chave mestra em {cofre.origem_chave}"))
    except Exception as e:  # noqa: BLE001
        r.append(_t("Segurança", "Cofre: cifrar e decifrar", False, f"{type(e).__name__}: {e}"))

    segredos = [chaves.get(k) for k in seg.SEGREDOS if chaves.get(k)]
    if cofre.arquivo.exists():
        bruto = cofre.arquivo.read_bytes()
        vaz = [k for k in seg.SEGREDOS if chaves.get(k) and chaves[k].encode() in bruto]
        r.append(_t("Segurança", "Cofre: chaves não aparecem em texto", not vaz,
                    "nenhuma chave legível em cofre.bin" if not vaz else f"em texto: {', '.join(vaz)}"))
    else:
        r.append(_t("Segurança", "Cofre: chaves não aparecem em texto", True, "cofre.bin ainda não criado (nenhuma chave cadastrada)", alerta=True))

    if env.exists():
        txt = env.read_text(encoding="utf-8", errors="ignore")
        vaz = [k for k in seg.SEGREDOS if re.search(rf"^\s*{k}\s*=\s*\S", txt, re.M)]
        r.append(_t("Segurança", ".env sem chaves de API", not vaz, "as chaves estão só no cofre" if not vaz else f"ainda no .env: {', '.join(vaz)}"))

    if sys.platform != "win32":
        ruins = []
        for f in (cofre.arquivo, cofre.arquivo_chave, env):
            if f.exists() and f.stat().st_mode & 0o077:
                ruins.append(f"{f.name} ({oct(f.stat().st_mode & 0o777)})")
        r.append(_t("Segurança", "Permissões dos arquivos sensíveis", not ruins,
                    "cofre.bin, .chave_mestra e .env só com acesso do dono (600)" if not ruins else "acesso aberto: " + ", ".join(ruins)))

    casos = ["http://127.0.0.1/", "http://localhost:8765/", "http://10.0.0.1/", "http://192.168.0.1/", "http://169.254.169.254/latest/",
             "http://[::1]/", "file:///etc/passwd", "ftp://exemplo.org/a.pdf"]
    passaram = []
    for u in casos:
        try:
            seg.conferir_url(u)
            passaram.append(u)
        except seg.EnderecoBloqueado:
            pass
    r.append(_t("Segurança", "Bloqueio de endereços internos (SSRF)", not passaram,
                f"{len(casos) - len(passaram)} de {len(casos)} endereços internos ou esquemas proibidos recusados"
                + (f"; aceitos indevidamente: {', '.join(passaram)}" if passaram else "")))

    csp = seg.CABECALHOS.get("Content-Security-Policy", "")
    exig = ["default-src 'self'", "script-src 'self'", "frame-ancestors 'none'", "object-src 'none'"]
    falta = [x for x in exig if x not in csp] + [k for k in ("X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy")
                                                  if k not in seg.CABECALHOS]
    r.append(_t("Segurança", "Cabeçalhos de proteção (CSP e outros)", not falta,
                "CSP sem scripts externos nem inline; página não pode ser embutida em outra" if not falta else "faltam: " + ", ".join(falta)))

    r.append(_t("Segurança", "Código de sessão", len(sessao.token) >= 43,
                f"{len(sessao.token)} caracteres (32 bytes aleatórios = 256 bits, secrets.token_urlsafe); servidor só em 127.0.0.1; "
                "pedidos de alteração exigem o cabeçalho X-BiblioNow"))

    amostra = "erro com api_key=abcdefghijklmnop e s2k-ABCDEFGH12345678 " + " ".join(segredos)
    limpo = seg.limpar(amostra, segredos)
    sobrou = [s for s in ["abcdefghijklmnop", "s2k-ABCDEFGH12345678", *segredos] if s in limpo]
    r.append(_t("Segurança", "Chaves apagadas dos registros (log)", not sobrou,
                "chaves e padrões de token substituídos por [chave removida]" if not sobrou else f"{len(sobrou)} valor(es) não removidos"))

    # --- protocolo
    prot = repo_raiz / "protocolo"
    for nome in ("registro_buscas.csv", "registro_incorporacoes.csv", "registro_downloads.csv"):
        c = fichamento.verificar_cadeia(prot / nome)
        det = (f"{c['linhas']} linha(s); cadeia SHA-256 íntegra" if c["integro"]
               else f"cadeia quebrada na linha {c['primeira_falha']} (registro alterado ou apagado)")
        r.append(_t("Protocolo Sigma", f"Cadeia de hashes: {nome}", c["integro"], det if c["linhas"] else "ainda sem registros",
                    alerta=not c["linhas"]))

    # --- repositório
    pasta_pdf, pasta_txt, pasta_bib = repo_raiz / "pdf", repo_raiz / "txt", repo_raiz / "bib"
    n = len(obras)
    sem_pdf, nao_pdf, sha_dif, sem_txt, txt_vazio, sem_bib = [], [], [], [], [], []
    for oid, ob in obras.items():
        f = repo_raiz / (ob.get("pdf") or f"pdf/{oid}.pdf")
        if not f.exists():
            sem_pdf.append(oid)
            continue
        with open(f, "rb") as h:
            if not h.read(1024).lstrip().startswith(b"%PDF"):
                nao_pdf.append(oid)
        if ob.get("sha256_pdf") and seg.sha256_arquivo(f) != ob["sha256_pdf"]:
            sha_dif.append(oid)
        t = repo_raiz / (ob.get("txt") or f"txt/{oid}.txt")
        if not t.exists():
            sem_txt.append(oid)
        elif not ob.get("txt_extraido"):
            txt_vazio.append(oid)
        b = repo_raiz / (ob.get("bib") or f"bib/{oid}.bib")
        if not b.exists() or not b.read_text(encoding="utf-8", errors="ignore").lstrip().startswith("@"):
            sem_bib.append(oid)

    def lista(x):
        return ", ".join(x[:5]) + (f" e mais {len(x) - 5}" if len(x) > 5 else "")

    r.append(_t("Repositório", "Toda obra tem o PDF", not sem_pdf, f"{n - len(sem_pdf)} de {n} obras" + (f"; faltam: {lista(sem_pdf)}" if sem_pdf else ""),
                alerta=not n))
    r.append(_t("Repositório", "Arquivos começam com %PDF", not nao_pdf, "nenhum HTML ou página de erro salvo como PDF" if not nao_pdf else f"inválidos: {lista(nao_pdf)}"))
    r.append(_t("Repositório", "SHA-256 igual ao do registro", not sha_dif,
                "nenhum PDF alterado desde a incorporação" if not sha_dif else f"alterados: {lista(sha_dif)}"))
    r.append(_t("Repositório", "Toda obra tem o TXT", not sem_txt,
                f"{n - len(sem_txt)} de {n}" + (f"; {len(txt_vazio)} sem texto extraível (PDF só com imagem ou protegido)" if txt_vazio else ""),
                alerta=bool(txt_vazio)))
    sem_rast, reconst = [], 0
    for oid, ob in obras.items():
        fr = repo_raiz / (ob.get("rastreabilidade") or f"rastreabilidade/{oid}.json")
        if not fr.exists():
            sem_rast.append(oid)
        elif '"reconstruida": true' in fr.read_text(encoding="utf-8", errors="ignore")[:4000]:
            reconst += 1
    r.append(_t("Repositório", "Toda obra tem ficha de rastreabilidade", not sem_rast,
                f"{n - len(sem_rast)} de {n} fichas (data e hora, endereço do download, cabeçalhos HTTP, tentativas e hashes)"
                + (f"; {reconst} reconstruída(s) a partir dos registros da época, sem cabeçalhos HTTP" if reconst else "")
                + (f"; sem ficha: {lista(sem_rast)}" if sem_rast else ""), alerta=bool(reconst)))
    r.append(_t("Repositório", "Toda obra tem o BibTeX", not sem_bib, f"{n - len(sem_bib)} de {n}" + (f"; faltam: {lista(sem_bib)}" if sem_bib else "")))

    md5 = {}
    for f in pasta_pdf.glob("*.pdf"):
        md5.setdefault(hashlib.md5(f.read_bytes()).hexdigest(), []).append(f.name)
    dup = [v for v in md5.values() if len(v) > 1]
    r.append(_t("Repositório", "Sem PDFs duplicados (conteúdo idêntico)", not dup,
                f"{len(md5)} conteúdos distintos" if not dup else f"{len(dup)} grupo(s): " + "; ".join(" = ".join(g) for g in dup[:3])))
    ids = {Path(o.get("pdf") or "").name for o in obras.values()}
    orfaos = [f.name for f in pasta_pdf.glob("*.pdf") if f.name not in ids]
    r.append(_t("Repositório", "PDFs sem registro de obra", True,
                "nenhum" if not orfaos else f"{len(orfaos)} PDF(s) copiados à mão ou de buscas antigas: {lista(orfaos)}", alerta=bool(orfaos)))

    # --- planilha
    x = repo_raiz / "fichamento.xlsx"
    if x.exists():
        try:
            from openpyxl import load_workbook
            ws = load_workbook(x, read_only=True)["Fichamento"]
            linhas = sum(1 for row in ws.iter_rows(min_row=2, max_col=1, values_only=True) if row[0])
            r.append(_t("Fichamento", "Uma linha por obra", linhas == n, f"{linhas} linha(s) na planilha; {n} obra(s) no acervo"))
        except Exception as e:  # noqa: BLE001
            r.append(_t("Fichamento", "Uma linha por obra", False, f"não foi possível ler a planilha: {type(e).__name__}"))
    else:
        r.append(_t("Fichamento", "Uma linha por obra", True, "planilha ainda não gerada (é criada ao fim da primeira busca)", alerta=True))

    return {"quando": datetime.now().isoformat(timespec="seconds"), "total": len(r), "aprovados": sum(t["ok"] for t in r),
            "alertas": sum(t["alerta"] for t in r), "testes": r}


# ---------------------------------------------------------------- 2. métricas de uma busca
def _ler(f: Path):
    if not f.exists():
        return []
    with open(f, encoding="utf-8-sig") as h:
        return list(csv.DictReader(h, delimiter=";"))


def _pct(a, b):
    return round(100 * a / b, 1) if b else None


def metricas(resumo: dict, pasta: Path) -> dict:
    regs = _ler(pasta / "resultados.csv")
    n = len(regs)
    est = Counter((r.get("status_pdf") or "").split(" (")[0] or "—" for r in regs)
    fontes = Counter()
    for r in regs:
        for f in (r.get("fonte") or "?").split("+"):
            fontes[f] += 1
    ambas = sum("+" in (r.get("fonte") or "") for r in regs)
    atendem = sum((r.get("verificacao_semantica") or "").startswith("ok") for r in regs)
    com_doi = sum(bool(r.get("doi")) for r in regs)
    aberto = sum(r.get("acesso_aberto") == "sim" for r in regs)
    anos = Counter(r["ano"] for r in regs if str(r.get("ano", "")).isdigit())
    no_acervo = est.get("baixado", 0) + est.get("ja_existia", 0)
    tentados = est.get("baixado", 0) + sum(v for k, v in est.items() if k == "falhou")
    return {
        "id": resumo["id"], "rotulo": resumo.get("rotulo"), "estado": resumo.get("estado"), "registros": n,
        "correspondencias_bases": resumo.get("totais_bases", {}),
        "indicadores": [
            {"nome": "Registros únicos", "valor": n, "nota": "após unir as bases e remover duplicatas por DOI e título"},
            {"nome": "Encontrados nas duas bases", "valor": ambas, "pct": _pct(ambas, n), "nota": "sobreposição OpenAlex × Semantic Scholar"},
            {"nome": "Atendem ao mínimo de blocos", "valor": atendem, "pct": _pct(atendem, n),
             "nota": "termos conferidos no título e no resumo (precisão estimada da consulta)"},
            {"nome": "Com DOI", "valor": com_doi, "pct": _pct(com_doi, n)},
            {"nome": "Marcados como acesso aberto", "valor": aberto, "pct": _pct(aberto, n)},
            {"nome": "No acervo (baixados + já existiam)", "valor": no_acervo, "pct": _pct(no_acervo, atendem),
             "nota": "% sobre os que atendem ao mínimo de blocos"},
            {"nome": "Sucesso do download", "valor": est.get("baixado", 0), "pct": _pct(est.get("baixado", 0), tentados),
             "nota": "baixados ÷ (baixados + falhas)"},
        ],
        "situacao_pdf": [{"situacao": k, "n": v} for k, v in est.most_common()],
        "fontes": dict(fontes),
        "anos": [{"ano": int(a), "n": v} for a, v in sorted(anos.items())],
    }


# ---------------------------------------------------------------- 3. revocação frente a uma lista de referência
def _doi(t: str) -> str:
    t = t.strip().lower()
    t = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", t)
    return t.rstrip(".;, ")


def _titulo(t: str) -> str:
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def referencia(resumo: dict, pasta: Path, texto: str) -> dict:
    itens = [l.strip() for l in (texto or "").splitlines() if l.strip()][:2000]
    if not itens:
        raise ValueError("cole ao menos um DOI ou título")
    regs = _ler(pasta / "resultados.csv")
    por_doi = {_doi(r["doi"]): r for r in regs if r.get("doi")}
    por_tit = {_titulo(r["titulo"]): r for r in regs if r.get("titulo")}
    linhas, achados, baixados = [], 0, 0
    for it in itens:
        eh_doi = bool(re.search(r"10\.\d{4,9}/\S+", it))
        r = por_doi.get(_doi(it)) if eh_doi else por_tit.get(_titulo(it))
        st = (r or {}).get("status_pdf", "").split(" (")[0]
        no_acervo = st in ("baixado", "ja_existia")
        achados += bool(r)
        baixados += no_acervo
        linhas.append({"referencia": it, "tipo": "DOI" if eh_doi else "título", "encontrado": bool(r),
                       "no_acervo": no_acervo, "situacao_pdf": (r or {}).get("status_pdf", ""), "titulo": (r or {}).get("titulo", "")})
    return {"id": resumo["id"], "referencias": len(itens), "encontrados": achados, "no_acervo": baixados,
            "revocacao_busca": _pct(achados, len(itens)), "revocacao_acervo": _pct(baixados, len(itens)),
            "faltantes": [l["referencia"] for l in linhas if not l["encontrado"]], "itens": linhas,
            "nota": "Títulos são comparados após retirar acentos, maiúsculas e pontuação; DOIs sem o prefixo https://doi.org/."}

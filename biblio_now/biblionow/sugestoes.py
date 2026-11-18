# -*- coding: utf-8 -*-
"""
Biblio-now · sugestão de palavras-chave a partir do tema da pesquisa. Autor: Eduardo Lopes Jonker.

1. O tema é dividido em conceitos nas palavras de ligação ("tutoria socrática com IA explicável" →
   "tutoria socrática" | "IA explicável"). Cada conceito vira um bloco.
2. Para cada conceito, o OpenAlex devolve os trabalhos mais relevantes; as palavras-chave e os tópicos indexados
   nesses trabalhos (em inglês no OpenAlex) são contados. Assim um tema em português também recebe termos em inglês.
3. O autocompletar de palavras-chave do OpenAlex acrescenta variações do próprio conceito.
4. Cada sugestão é contada no OpenAlex (título e resumo), para o pesquisador ver quanto cada termo amplia a busca.

As sugestões vêm só dos dados das bases (nada é gerado por modelo de linguagem) e o pesquisador escolhe o que usar.
"""
from __future__ import annotations

import re
import time
from collections import Counter
from datetime import datetime

import requests

from . import base
from . import seguranca as seg

LIGACOES = (r"\b(e|ou|com|sem|em|no|na|nos|nas|para|pelo|pela|sobre|entre|por|ao|aos|à|às|"
            r"and|or|with|without|in|on|for|by|about|between|to|using|via|uso|aplicado|aplicada|aplicação)\b")
FRACAS = r"\b(de|do|da|dos|das|of)\b"       # ligam substantivos ("teoria dos grafos"): só divide se a frase inteira for rara
VAZIAS = {"o", "a", "os", "as", "um", "uma", "estudo", "análise", "analise", "revisão", "revisao", "pesquisa", "study", "analysis", "review"}


def _sem_acento(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c)).lower()


def conceitos(tema: str, maximo: int = 4) -> list[str]:
    """Divide o tema nos conceitos principais (no máximo `maximo`)."""
    t = re.sub(r"[\"“”'‘’()\[\]{}:;!?]", " ", tema or "")
    partes = re.split(r"\s*[,/|+]\s*|\s+" + LIGACOES + r"\s+", t, flags=re.I)
    vistos, out = set(), []
    for p in partes:
        if not p:
            continue
        p = re.sub(r"\s+", " ", p).strip(" .-")
        palavras = [w for w in p.split() if w.lower() not in VAZIAS]
        p = " ".join(palavras)
        p = re.sub(r"^(the|a|an)\s+", "", p, flags=re.I)
        if len(p) < 2 or re.fullmatch(LIGACOES, p, flags=re.I) or _sem_acento(p) in vistos:
            continue
        vistos.add(_sem_acento(p))
        out.append(p[:80])
    return out[:maximo] or ([tema.strip()[:80]] if tema.strip() else [])


def _get(sessao, url, params, chave):
    try:
        r = sessao.get(url, params=params, headers={"Authorization": f"Bearer {chave}"} if chave else None, timeout=(10, 30))
        return r.json() if r.ok else {}
    except (requests.RequestException, ValueError):
        return {}


def _contar(sessao, termo, chave, email):
    d = _get(sessao, base.OPENALEX_URL, {"search.title_and_abstract": f'"{termo}"', "per_page": 1, "select": "id",
                                          "filter": "type:!peer-review,type:!paratext", **({"mailto": email} if email else {})}, chave)
    return (d.get("meta") or {}).get("count")


def sugerir(tema: str, chaves: dict, amostra: int = 40, por_bloco: int = 10) -> dict:
    tema = (tema or "").strip()
    if len(tema) < 3:
        raise ValueError("descreva o tema com pelo menos 3 caracteres")
    if len(tema) > 300:
        raise ValueError("tema muito longo (até 300 caracteres)")
    chave, email = chaves.get("OPENALEX_API_KEY", ""), chaves.get("OPENALEX_EMAIL", "")
    sessao = seg.proteger_sessao(requests.Session())
    sessao.headers["User-Agent"] = "Biblio-now/1.0 (sugestao de palavras-chave)"
    extra = {"mailto": email} if email else {}
    blocos, topicos_gerais = [], Counter()
    lista = []
    for c in conceitos(tema):
        partes = [x.strip() for x in re.split(r"\s+" + FRACAS + r"\s+", c, flags=re.I) if x and not re.fullmatch(FRACAS, x.strip(), flags=re.I)]
        if len(partes) > 1 and (_contar(sessao, c, chave, email) or 0) < 30:
            lista += [x for x in partes if len(x) > 1]   # "aves do planalto catarinense" é raro: vira "aves" | "planalto catarinense"
        else:
            lista.append(c)                             # "teoria dos grafos" é comum: fica inteiro
    for c in list(dict.fromkeys(lista))[:4]:
        d = _get(sessao, base.OPENALEX_URL, {"search.title_and_abstract": c, "per_page": amostra, "select": "display_name,keywords,topics",
                                             "filter": "type:!peer-review,type:!paratext", **extra}, chave)
        trabalhos = d.get("results") or []
        # tópico dominante: as palavras-chave só são contadas nos trabalhos desse tema (evita homônimos e ruído)
        prim = [((w.get("topics") or [{}])[0].get("display_name") or "") for w in trabalhos]
        cont_top = Counter(t for t in prim if t)
        for t, n in cont_top.items():
            topicos_gerais[t] += n
        dominantes = {t for t, n in cont_top.most_common(2) if n >= max(2, len(trabalhos) // 10)}
        no_tema = [w for w, t in zip(trabalhos, prim) if not dominantes or t in dominantes]
        kw, origem = Counter(), {}
        for w in no_tema:
            for k in w.get("keywords") or []:
                nome = (k.get("display_name") or "").strip()
                if 2 < len(nome) <= 60:
                    kw[nome.lower()] += 1
                    origem.setdefault(nome.lower(), nome)
        auto = _get(sessao, "https://api.openalex.org/autocomplete/keywords", {"q": c, **extra}, chave).get("results") or []
        time.sleep(0.1)
        cand = [(c, "seu termo", None)]
        cbase = _sem_acento(c)
        for a in auto[:8]:
            n = (a.get("display_name") or "").strip()
            if n and re.match(re.escape(cbase) + r"(\b|$)", _sem_acento(n)):       # só palavra inteira: "aves" não vira "Avesta"
                cand.append((n, "variação do termo (autocompletar OpenAlex)", None))
        confiavel = len(no_tema) >= 5
        minimo = 2 if len(no_tema) >= 10 else 1
        tema_txt = f" do tema “{' / '.join(sorted(dominantes))}”" if dominantes else ""
        for k, f in kw.most_common(30):
            if f >= minimo:
                cand.append((origem[k], f"palavra-chave em {f} de {len(no_tema)} trabalhos{tema_txt}", f))
        termos, vistos = [], set()
        for termo, motivo, freq in cand:
            chave_t = _sem_acento(termo)
            if chave_t in vistos or not re.search(r"\w", termo) or re.search(r'["\\<>]', termo):
                continue
            vistos.add(chave_t)
            termos.append({"termo": termo, "motivo": motivo, "frequencia": freq})
            if len(termos) >= por_bloco:
                break
        for t in termos:
            t["trabalhos"] = _contar(sessao, t["termo"], chave, email)
            time.sleep(0.1)
        GERAL = 300_000                                   # acima disso o termo é amplo demais para entrar sozinho
        for t in termos:
            t["geral"] = bool(t["trabalhos"] and t["trabalhos"] > GERAL and t["motivo"] != "seu termo")
            if t["geral"]:
                t["motivo"] += " · termo muito geral"
            if not confiavel and t["frequencia"] is not None:
                t["motivo"] += " · baixa confiança (poucos trabalhos sobre o conceito)"
        for t in termos:                                  # sinônimo central (metade dos trabalhos do tema): entra mesmo se geral
            if t["geral"] and confiavel and t["frequencia"] and t["frequencia"] >= 0.5 * len(no_tema):
                t["geral"] = False
                t["motivo"] = t["motivo"].replace(" · termo muito geral", " · termo amplo, mas central no tema")
        selecionar = [t for t in termos if t["trabalhos"] and not t["geral"]
                      and (t["frequencia"] is None or (confiavel and t["frequencia"] >= max(2, len(no_tema) * 0.1)))][:5]
        for t in termos:
            t["sugerido"] = t in selecionar
        blocos.append({"conceito": c, "amostra": len(trabalhos), "no_tema": len(no_tema), "topicos": sorted(dominantes), "confiavel": confiavel,
                       "aviso": "" if confiavel else "Poucos trabalhos sobre este conceito no OpenAlex: as sugestões podem estar fora do tema. "
                                                     "Acrescente você mesmo o termo em inglês (ex.: frota → fleet).",
                       "termos": termos})
    return {"tema": tema, "conceitos": [b["conceito"] for b in blocos], "blocos": blocos,
            "topicos": [{"topico": t, "trabalhos_na_amostra": n} for t, n in topicos_gerais.most_common(8)],
            "base": "OpenAlex (palavras-chave e tópicos indexados nos trabalhos mais relevantes de cada conceito)",
            "quando": datetime.now().isoformat(timespec="seconds"),
            "nota": "Sugestões tiradas dos dados indexados no OpenAlex, sem modelo de linguagem. Confira cada termo: "
                    "palavras-chave muito gerais ampliam muito a busca e trazem trabalhos fora do tema."}

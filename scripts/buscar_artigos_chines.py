#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca de artigos em chinês (mesma semântica de scripts/buscar_artigos.py).

Bases chinesas e o que este script faz com cada uma
  - CNKI (中国知网), Wanfang (万方) e CQVIP (维普): não têm API pública; o acesso é
    por assinatura e os termos de uso não permitem coleta automatizada. NÃO são
    consultadas por script. Busca manual: ver
    "Metodologia de Pesquisa/exportacoes_capes/LEIA-ME_roteiro_de_busca.md" (seção 6).
  - CSCD (Chinese Science Citation Database): fica dentro da Web of Science;
    busca manual pelo Portal CAPES, se a assinatura da UDESC incluir a coleção.
  - OpenAlex, filtro language:zh (automático, este script): indexa periódicos
    chineses com DOI, incluindo resumos em chinês quando a editora os deposita.
    A cobertura é parcial em relação à CNKI.

Duas consultas, unidas e sem duplicatas:
  1. termos em chinês simplificado (abaixo), em título e resumo
  2. a frase em inglês de buscar_artigos.py, filtrada por idioma chinês

Modos
  padrão      os 3 blocos (método AND XAI AND setor público), como nos demais scripts
  --relaxada  pelo menos 2 dos 3 blocos; cada registro diz quais blocos atendeu

Saída (tudo em artigos/idiomas/zh/):
  *.pdf  resultados.csv  novos.csv  referencias.bib  consulta.txt  vistos.json

Uso
  python3 scripts/buscar_artigos_chines.py
  python3 scripts/buscar_artigos_chines.py --relaxada --max-pdfs 50
"""

import argparse
import json
import signal
import sys
import time
from datetime import datetime
from itertools import combinations
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import buscar_artigos as ba  # noqa: E402

SAIDA = ROOT / "artigos" / "idiomas" / "zh"

# Equivalentes em chinês simplificado dos três grupos de buscar_artigos.GRUPOS.
# "审计" (auditoria) é mais amplo que "可审计性" (auditabilidade); entra porque a
# literatura chinesa raramente usa o termo restrito. Isso fica registrado em consulta.txt.
GRUPOS_ZH = {
    "metodo": ["规范性分析", "处方性分析", "预测分析", "预测性分析", "决策支持",
               "异常检测", "欺诈检测", "舞弊识别", "风险评估"],
    "xai": ["可解释人工智能", "可解释性人工智能", "可解释的人工智能", "可解释机器学习",
            "可解释性机器学习", "算法透明", "XAI"],
    "setor_publico": ["公共部门", "政府", "公共管理", "政府采购", "公共采购", "税收", "税务",
                      "可审计性", "审计", "问责"],
}
EQUIVALENCIA = {
    "metodo": "prescriptive/predictive analytics, decision support, anomaly/fraud detection, risk assessment",
    "xai": "explainable AI, interpretable machine learning, algorithmic transparency, XAI",
    "setor_publico": "public sector, government, public administration, public procurement, tax, auditability/audit, accountability",
}
FILTRO = "language:zh,type:!peer-review,type:!paratext"


def bloco(termos):
    return "(" + " OR ".join(f'"{t}"' for t in termos) + ")"


def consultas(relaxada):
    """Lista de (rótulo, campo de busca, expressão)."""
    grupos = list(GRUPOS_ZH)
    combos = [tuple(grupos)] if not relaxada else list(combinations(grupos, 2))
    out = []
    for c in combos:
        rot = "+".join(c)
        out.append((f"zh[{rot}]", "search.title_and_abstract", " AND ".join(bloco(GRUPOS_ZH[g]) for g in c)))
    # frase em inglês de buscar_artigos (literal), só para os 3 blocos
    out.append(("en[metodo+xai+setor_publico]", "search.title_and_abstract.exact", ba.CONSULTA_OPENALEX))
    return out


def buscar(sessao, rotulo, campo, expressao, ano_min, max_res):
    params = {campo: expressao, "per_page": 100, "filter": f"{FILTRO},publication_year:>{ano_min - 1}",
              "select": ("id,doi,display_name,publication_year,authorships,primary_location,best_oa_location,"
                         "locations,open_access,cited_by_count,abstract_inverted_index,type,language")}
    regs, pagina, total = [], 1, None
    while len(regs) < max_res:
        params["page"] = pagina
        d = ba.get_json(sessao, ba.OPENALEX_URL, params, rotulo=f"OpenAlex {rotulo}")
        if total is None:
            total = d.get("meta", {}).get("count", 0)
            print(f"   {rotulo}: {total}")
        lote = d.get("results", [])
        if not lote:
            break
        for w in lote:
            r = ba.normalizar_openalex(w)
            r["fonte"] = f"OpenAlex {rotulo}"
            r["_oa_id"] = w["id"].split("/")[-1]
            regs.append(r)
        if pagina * 100 >= total:
            break
        pagina += 1
        time.sleep(1.2)
    return regs, total or 0


def blocos_atendidos(r):
    texto = r["titulo"] + " " + r["resumo"]
    baixo = texto.lower()
    atende = []
    for g, termos in GRUPOS_ZH.items():
        zh = any(t.lower() in baixo for t in termos)
        en = any(p.search(baixo) for p in ba.PADROES[g])
        if zh or en:
            atende.append(g)
    return atende


def nome_pdf(r):
    ident = ba.ascii_slug(r["doi"], 60) if r["doi"] else r.get("_oa_id", "sem_id")
    return f"{r['ano'] or 'sd'}_{ident}.pdf"


def main():
    ap = argparse.ArgumentParser(description="Busca artigos em chinês (OpenAlex, idioma zh).")
    ap.add_argument("--relaxada", action="store_true", help="aceita 2 dos 3 blocos")
    ap.add_argument("--max-resultados", type=int, default=500, help="máximo por consulta")
    ap.add_argument("--max-pdfs", type=int, default=100)
    ap.add_argument("--ano-min", type=int, default=2020)
    ap.add_argument("--sem-pdf", action="store_true")
    args = ap.parse_args()

    SAIDA.mkdir(parents=True, exist_ok=True)
    # encerramento por timeout/kill também grava os relatórios (bloco finally)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    s = requests.Session()
    s.headers["User-Agent"] = ba.USER_AGENT
    chave = __import__("os").environ.get("OPENALEX_API_KEY", "").strip()
    if chave:
        s.headers["Authorization"] = f"Bearer {chave}"

    minimo = 2 if args.relaxada else 3
    print(f"Busca em chinês — modo {'relaxado (2 de 3 blocos)' if args.relaxada else 'estrito (3 blocos)'}")
    listas, totais = [], {}
    for rot, campo, expr in consultas(args.relaxada):
        try:
            regs, tot = buscar(s, rot, campo, expr, args.ano_min, args.max_resultados)
        except RuntimeError as e:
            print("  ", e)
            regs, tot = [], "erro"
        listas.append(regs)
        totais[rot] = tot
        time.sleep(1.2)

    registros = ba.unir(listas)
    for r in registros:
        b = blocos_atendidos(r)
        r["blocos"] = b
        if len(b) == 3:
            r["verificacao"] = "ok"
        elif not r["resumo"]:
            r["verificacao"] = "sem_resumo"
        else:
            faltam = [g for g in GRUPOS_ZH if g not in b]
            r["verificacao"] = f"{len(b)} blocos (falta: {', '.join(faltam)})"
        r["status_pdf"], r["arquivo_pdf"] = "", ""
    registros.sort(key=lambda r: -len(r["blocos"]))

    vistos_f = SAIDA / "vistos.json"
    vistos = json.loads(vistos_f.read_text(encoding="utf-8")) if vistos_f.exists() else {}
    hoje = datetime.now().strftime("%Y-%m-%d")
    ja = set(vistos)
    novos = []
    for r in registros:
        k = ba.chave_registro(r)
        r["visto_em"] = vistos.setdefault(k, hoje)
        if k not in ja:
            novos.append(r)

    baixados = 0
    try:
        for r in registros:
            destino = SAIDA / nome_pdf(r)
            if destino.exists():
                r["status_pdf"], r["arquivo_pdf"] = "ja_existia", destino.name
            elif args.sem_pdf:
                r["status_pdf"] = "nao_tentado (--sem-pdf)"
            elif len(r["blocos"]) < minimo:
                r["status_pdf"] = "nao_tentado (blocos insuficientes)"
            elif not r["pdf_urls"]:
                r["status_pdf"] = "sem_pdf_aberto"
            elif baixados >= args.max_pdfs:
                r["status_pdf"] = "nao_tentado (limite --max-pdfs)"
            else:
                ok, info = ba.baixar_pdf(s, r["pdf_urls"], destino)
                if ok:
                    baixados += 1
                    r["status_pdf"], r["arquivo_pdf"] = "baixado", destino.name
                    print(f"   [{baixados:>3}] {destino.name}", flush=True)
                else:
                    r["status_pdf"] = f"falhou ({info})"
    except KeyboardInterrupt:
        print("\nInterrompido; gravando o que já foi obtido.")
    finally:
        for r in registros:
            r["status_pdf"] = r["status_pdf"] or "nao_tentado (interrompido)"
        gravar_saidas(args, registros, novos, vistos, vistos_f, totais, baixados)

    print(f"\n{len(registros)} registros únicos")
    print(f"PDFs baixados: {baixados} | inéditos: {len(novos)}")
    print(f"Saída: {SAIDA}")
    return 0


def gravar_saidas(args, registros, novos, vistos, vistos_f, totais, baixados):
    ba.gravar_csv(registros, SAIDA / "resultados.csv")
    ba.gravar_csv(novos, SAIDA / "novos.csv")
    ba.gravar_bib(registros, SAIDA / "referencias.bib")
    vistos_f.write_text(json.dumps(vistos, ensure_ascii=False, indent=0), encoding="utf-8")
    contagem = {}
    for r in registros:
        contagem[r["verificacao"].split(" (")[0]] = contagem.get(r["verificacao"].split(" (")[0], 0) + 1
    linhas = [f"Busca em chinês — {datetime.now():%d/%m/%Y %H:%M}",
              f"Fonte: OpenAlex, filtro {FILTRO}, publicação a partir de {args.ano_min}",
              f"Modo: {'relaxado, mínimo 2 de 3 blocos' if args.relaxada else 'estrito, 3 blocos'}", "",
              "Termos em chinês (equivalência em inglês):"]
    for g, termos in GRUPOS_ZH.items():
        linhas.append(f"  {g}: {' | '.join(termos)}")
        linhas.append(f"      ≈ {EQUIVALENCIA[g]}")
    linhas += ["", "Observação: 审计 (auditoria) é mais amplo que 可审计性 (auditabilidade).", "",
               "Consultas submetidas e total informado pelo OpenAlex:"]
    for rot, campo, expr in consultas(args.relaxada):
        linhas.append(f"  [{rot}] {campo} = {expr}")
        linhas.append(f"      total: {totais.get(rot)}")
    linhas += ["", f"Registros únicos: {len(registros)}  |  conferência local: {json.dumps(contagem, ensure_ascii=False)}",
               f"PDFs baixados nesta execução: {baixados}  |  inéditos: {len(novos)}", "",
               "Bases chinesas sem API (busca manual, não automatizada): CNKI, Wanfang, CQVIP; CSCD via Web of Science."]
    (SAIDA / "consulta.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"conferência local: {contagem}")


if __name__ == "__main__":
    sys.exit(main())

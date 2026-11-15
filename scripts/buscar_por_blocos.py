#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca de artigos por blocos de termos definidos em um arquivo JSON.

Cada bloco é uma lista de termos unidos por OR. O artigo entra se atender pelo
menos N blocos (padrão do arquivo, ou --minimo). Com N igual ao número de blocos,
é o AND de todos; com N menor, o script consulta cada combinação de N blocos e
une os resultados, sem duplicatas.

Fonte: OpenAlex, termos literais (sem radicalização) em título e resumo.
Cada registro é conferido no texto recebido e informa quais blocos atendeu.
Só são baixados PDFs de acesso aberto de registros que atendem ao mínimo.

Arquivo de configuração (exemplo em Metodologia de Pesquisa/buscas/):
  {"nome": "...", "saida": "artigos/minha_busca", "minimo_blocos": 3, "ano_min": 2020,
   "grupos": {"bloco1": ["termo a", "termo b"], "bloco2": [...], ...}}

Saída na pasta "saida":
  *.pdf  resultados.csv  novos.csv  referencias.bib  consulta.txt  vistos.json

Uso
  python3 scripts/buscar_por_blocos.py --config "Metodologia de Pesquisa/buscas/grafos_xai_prescritivo_regressao.json"
  python3 scripts/buscar_por_blocos.py --config ... --minimo 4        # AND de todos
  python3 scripts/buscar_por_blocos.py --config ... --sem-pdf
"""

import argparse
import json
import os
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

FILTRO_BASE = "type:!peer-review,type:!paratext"
SELECT = ("id,doi,display_name,publication_year,authorships,primary_location,best_oa_location,"
          "locations,open_access,cited_by_count,abstract_inverted_index,type,language")


def bloco(termos):
    return "(" + " OR ".join(f'"{t}"' for t in termos) + ")"


def buscar(sessao, rotulo, expressao, ano_min, max_res):
    params = {"search.title_and_abstract.exact": expressao, "per_page": 100,
              "filter": f"{FILTRO_BASE},publication_year:>{ano_min - 1}", "select": SELECT}
    regs, pagina, total = [], 1, None
    while len(regs) < max_res:
        params["page"] = pagina
        d = ba.get_json(sessao, ba.OPENALEX_URL, params, rotulo=f"OpenAlex {rotulo}")
        if total is None:
            total = d.get("meta", {}).get("count", 0)
            print(f"   {rotulo}: {total}", flush=True)
        lote = d.get("results", [])
        if not lote:
            break
        for w in lote:
            r = ba.normalizar_openalex(w)
            r["fonte"] = f"OpenAlex [{rotulo}]"
            r["_oa_id"] = w["id"].split("/")[-1]
            regs.append(r)
            if len(regs) >= max_res:
                break
        if pagina * 100 >= total:
            break
        pagina += 1
        time.sleep(1.2)
    return regs, total or 0


def main():
    ap = argparse.ArgumentParser(description="Busca por blocos de termos (OpenAlex).")
    ap.add_argument("--config", required=True, help="arquivo JSON com os blocos")
    ap.add_argument("--minimo", type=int, default=None, help="mínimo de blocos atendidos (padrão: do arquivo)")
    ap.add_argument("--max-resultados", type=int, default=1000, help="máximo por combinação de blocos")
    ap.add_argument("--max-pdfs", type=int, default=100)
    ap.add_argument("--sem-pdf", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    grupos = cfg["grupos"]
    minimo = args.minimo or cfg.get("minimo_blocos", len(grupos))
    if not 1 <= minimo <= len(grupos):
        ap.error(f"--minimo deve estar entre 1 e {len(grupos)}")
    ano_min = cfg.get("ano_min", 2020)
    saida = ROOT / cfg["saida"]
    saida.mkdir(parents=True, exist_ok=True)
    padroes = {g: [ba.padrao_termo(t) for t in termos] for g, termos in grupos.items()}

    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    s = requests.Session()
    s.headers["User-Agent"] = ba.USER_AGENT
    chave = os.environ.get("OPENALEX_API_KEY", "").strip()
    if chave:
        s.headers["Authorization"] = f"Bearer {chave}"

    print(f"{cfg.get('nome', 'Busca por blocos')} — mínimo {minimo} de {len(grupos)} blocos")
    consultas = []
    for combo in combinations(grupos, minimo):
        consultas.append(("+".join(combo), " AND ".join(bloco(grupos[g]) for g in combo)))
    listas, totais = [], {}
    for rot, expr in consultas:
        try:
            regs, tot = buscar(s, rot, expr, ano_min, args.max_resultados)
        except RuntimeError as e:
            print("  ", e)
            regs, tot = [], "erro"
        listas.append(regs)
        totais[rot] = tot
        time.sleep(1.2)

    registros = ba.unir(listas)
    for r in registros:
        texto = (r["titulo"] + " " + r["resumo"]).lower()
        r["blocos"] = [g for g, pads in padroes.items() if any(p.search(texto) for p in pads)]
        n = len(r["blocos"])
        if n >= minimo:
            r["verificacao"] = f"ok ({n} blocos: {', '.join(r['blocos'])})"
        elif not r["resumo"]:
            r["verificacao"] = "sem_resumo"
        else:
            r["verificacao"] = f"parcial ({n} blocos: {', '.join(r['blocos'])})"
        r["status_pdf"], r["arquivo_pdf"] = "", ""
    registros.sort(key=lambda r: (-len(r["blocos"]), -int(r["ano"] or 0)))

    vistos_f = saida / "vistos.json"
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
            destino = saida / ba.nome_arquivo(r)
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
        ba.gravar_csv(registros, saida / "resultados.csv")
        ba.gravar_csv(novos, saida / "novos.csv")
        ba.gravar_bib(registros, saida / "referencias.bib")
        vistos_f.write_text(json.dumps(vistos, ensure_ascii=False, indent=0), encoding="utf-8")
        por_n = {}
        for r in registros:
            por_n[len(r["blocos"])] = por_n.get(len(r["blocos"]), 0) + 1
        linhas = [f"{cfg.get('nome', 'Busca por blocos')} — {datetime.now():%d/%m/%Y %H:%M}",
                  f"Fonte: OpenAlex, termos literais em título e resumo; filtro {FILTRO_BASE}; ano >= {ano_min}",
                  f"Critério: pelo menos {minimo} de {len(grupos)} blocos", ""]
        if cfg.get("observacao"):
            linhas += [f"Observação: {cfg['observacao']}", ""]
        linhas.append("Blocos:")
        for g, termos in grupos.items():
            linhas.append(f"  {g}: {bloco(termos)}")
        linhas += ["", "Consultas submetidas (uma por combinação de blocos) e total informado:"]
        for rot, expr in consultas:
            linhas.append(f"  [{rot}] total {totais.get(rot)}")
            linhas.append(f"      {expr}")
        linhas += ["", f"Registros únicos: {len(registros)}",
                   "Blocos atendidos no título/resumo recebido: "
                   + ", ".join(f"{n} blocos = {c}" for n, c in sorted(por_n.items(), reverse=True)),
                   f"PDFs baixados nesta execução: {baixados} | inéditos: {len(novos)}"]
        (saida / "consulta.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"\n{len(registros)} registros únicos | PDFs baixados: {baixados} | inéditos: {len(novos)}")
    print(f"Saída: {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

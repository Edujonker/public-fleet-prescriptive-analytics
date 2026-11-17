#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca de livros sobre os temas da dissertação e download dos que são de acesso aberto.

O que é baixado
  Somente livros de acesso aberto: licença aberta (ex.: Creative Commons) ou
  disponibilizados pela própria editora/repositório (OAPEN, DOAB, repositórios
  institucionais), com link público para o PDF informado pelo OpenAlex.
  Não usa LibGen, Z-Library, Anna's Archive nem fontes semelhantes.
  Livros fechados ficam no CSV com DOI/link, para acesso via CAFe ou biblioteca.

Fonte
  OpenAlex, tipo "book" (com --capitulos, também "book-chapter"), termos literais
  em título e resumo. As APIs do DOAB e do OAPEN só aceitam IPs autorizados;
  os livros delas aparecem no OpenAlex com o link do repositório OAPEN.

Temas
  Arquivo JSON (padrão: Metodologia de Pesquisa/buscas/livros_temas_tcc.json),
  um bloco OR de termos por tema; uma consulta por tema.

Saída em artigos/livros/:
  <tema>/*.pdf                    livros abertos baixados, separados por tema
  <tema>/resultados.csv           todos os livros do tema (abertos e fechados)
  resultados_todos.csv            consolidado, sem duplicatas (o livro fica no 1º tema)
  referencias.bib  consulta.txt  vistos.json

Uso
  python3 scripts/buscar_livros.py
  python3 scripts/buscar_livros.py --por-tema 200 --max-pdfs 300
  python3 scripts/buscar_livros.py --capitulos           # inclui capítulos de livro
  python3 scripts/buscar_livros.py --temas 03_xai 04_grafos_e_redes
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import buscar_artigos as ba  # noqa: E402

CONFIG_PADRAO = ROOT / "Metodologia de Pesquisa" / "buscas" / "livros_temas_tcc.json"
SELECT = ("id,doi,display_name,publication_year,authorships,primary_location,best_oa_location,"
          "locations,open_access,cited_by_count,abstract_inverted_index,type,language")
ba.PDF_MAX_BYTES = 200 * 1024 * 1024   # livros são maiores que artigos


def licenca(w):
    for loc in [w.get("best_oa_location") or {}] + list(w.get("locations") or []):
        if (loc or {}).get("license"):
            return loc["license"]
    return ""


def buscar_tema(s, tema, termos, tipos, ano_min, max_res):
    expr = "(" + " OR ".join(f'"{t}"' for t in termos) + ")"
    params = {"search.title_and_abstract.exact": expr, "per_page": 100, "select": SELECT,
              "filter": f"type:{tipos},publication_year:>{ano_min - 1}"}
    regs, pagina, total = [], 1, None
    while len(regs) < max_res:
        params["page"] = pagina
        d = ba.get_json(s, ba.OPENALEX_URL, params, rotulo=f"OpenAlex {tema}")
        if total is None:
            total = d.get("meta", {}).get("count", 0)
            print(f"   {tema}: {total} livros", flush=True)
        lote = d.get("results", [])
        if not lote:
            break
        for w in lote:
            r = ba.normalizar_openalex(w)
            r["fonte"] = "OpenAlex"
            r["tema"] = tema
            r["licenca"] = licenca(w)
            r["oa_status"] = (w.get("open_access") or {}).get("oa_status", "")
            regs.append(r)
            if len(regs) >= max_res:
                break
        if pagina * 100 >= total:
            break
        pagina += 1
        time.sleep(1.2)
    return regs, total or 0, expr


def main():
    ap = argparse.ArgumentParser(description="Busca livros dos temas da dissertação (acesso aberto).")
    ap.add_argument("--config", default=str(CONFIG_PADRAO))
    ap.add_argument("--por-tema", type=int, default=100, help="máximo de livros por tema (padrão 100)")
    ap.add_argument("--max-pdfs", type=int, default=200, help="máximo de PDFs nesta execução (padrão 200)")
    ap.add_argument("--capitulos", action="store_true", help="incluir capítulos de livro")
    ap.add_argument("--temas", nargs="*", help="rodar só estes temas")
    ap.add_argument("--sem-pdf", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    temas = {k: v for k, v in cfg["temas"].items() if not args.temas or k in args.temas}
    saida = ROOT / cfg["saida"]
    saida.mkdir(parents=True, exist_ok=True)
    tipos = "book|book-chapter" if args.capitulos else "book"

    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    s = requests.Session()
    s.headers["User-Agent"] = ba.USER_AGENT
    chave = os.environ.get("OPENALEX_API_KEY", "").strip()
    if chave:
        s.headers["Authorization"] = f"Bearer {chave}"

    print(f"{cfg['nome']} — tipos: {tipos}")
    por_tema, totais, expressoes = {}, {}, {}
    for tema, termos in temas.items():
        try:
            regs, tot, expr = buscar_tema(s, tema, termos, tipos, cfg.get("ano_min", 2000), args.por_tema)
        except RuntimeError as e:
            print("  ", e)
            regs, tot, expr = [], "erro", ""
        por_tema[tema], totais[tema], expressoes[tema] = regs, tot, expr
        time.sleep(1.2)

    # consolidação: cada livro fica no primeiro tema em que aparece
    vistos_tema, unicos = {}, []
    for tema, regs in por_tema.items():
        for r in regs:
            k = ba.chave_registro(r)
            if k in vistos_tema:
                outro = vistos_tema[k]
                outro["temas"] = outro.get("temas", outro["tema"]) + f"; {tema}"
                continue
            r["temas"] = tema
            vistos_tema[k] = r
            unicos.append(r)
    for r in unicos:
        r["verificacao"] = "acesso aberto" if r["pdf_urls"] else ("aberto sem PDF direto" if r["acesso_aberto"] else "fechado")
        r["status_pdf"], r["arquivo_pdf"] = "", ""

    vistos_f = saida / "vistos.json"
    vistos = json.loads(vistos_f.read_text(encoding="utf-8")) if vistos_f.exists() else {}
    hoje, ja, novos = datetime.now().strftime("%Y-%m-%d"), None, []
    ja = set(vistos)
    for r in unicos:
        k = ba.chave_registro(r)
        r["visto_em"] = vistos.setdefault(k, hoje)
        if k not in ja:
            novos.append(r)

    baixados = 0
    try:
        # mais citados primeiro, para o limite de PDFs priorizar livros de referência
        for r in sorted(unicos, key=lambda r: -(r["citacoes"] or 0)):
            pasta = saida / r["tema"]
            pasta.mkdir(parents=True, exist_ok=True)
            destino = pasta / ba.nome_arquivo(r)
            if destino.exists():
                r["status_pdf"], r["arquivo_pdf"] = "ja_existia", f"{r['tema']}/{destino.name}"
            elif args.sem_pdf:
                r["status_pdf"] = "nao_tentado (--sem-pdf)"
            elif not r["pdf_urls"]:
                r["status_pdf"] = "fechado (acessar via CAFe/biblioteca)" if not r["acesso_aberto"] else "aberto sem PDF direto (ver link)"
            elif baixados >= args.max_pdfs:
                r["status_pdf"] = "nao_tentado (limite --max-pdfs)"
            else:
                ok, info = ba.baixar_pdf(s, r["pdf_urls"], destino)
                if ok:
                    baixados += 1
                    r["status_pdf"], r["arquivo_pdf"] = "baixado", f"{r['tema']}/{destino.name}"
                    print(f"   [{baixados:>3}] {r['tema']}/{destino.name}", flush=True)
                else:
                    r["status_pdf"] = f"falhou ({info})"
    except KeyboardInterrupt:
        print("\nInterrompido; gravando o que já foi obtido.")
    finally:
        for r in unicos:
            r["status_pdf"] = r["status_pdf"] or "nao_tentado (interrompido)"
            # coluna "veiculo" do CSV passa a mostrar editora/série e licença
            if r.get("licenca") and r["licenca"] not in r["veiculo"]:
                r["veiculo"] = f"{r['veiculo']} [licença: {r['licenca']}]".strip()
        for tema in temas:
            regs = [r for r in unicos if r["tema"] == tema]
            if regs:
                (saida / tema).mkdir(parents=True, exist_ok=True)
                ba.gravar_csv(regs, saida / tema / "resultados.csv")
        ba.gravar_csv(unicos, saida / "resultados_todos.csv")
        ba.gravar_csv(novos, saida / "novos.csv")
        ba.gravar_bib(unicos, saida / "referencias.bib")
        vistos_f.write_text(json.dumps(vistos, ensure_ascii=False, indent=0), encoding="utf-8")
        cont = {}
        for r in unicos:
            k = r["status_pdf"].split(" (")[0]
            cont[k] = cont.get(k, 0) + 1
        linhas = [f"{cfg['nome']} — {datetime.now():%d/%m/%Y %H:%M}",
                  f"Origem dos temas: {cfg.get('origem_dos_temas', '-')}",
                  f"Fonte: OpenAlex, tipos {tipos}, termos literais em título e resumo, ano >= {cfg.get('ano_min', 2000)}",
                  "Download: somente PDFs de acesso aberto com link público (sem bibliotecas-sombra).", "",
                  "Consultas e total informado pelo OpenAlex:"]
        for tema in temas:
            linhas.append(f"  [{tema}] total {totais.get(tema)} — {expressoes.get(tema)}")
        linhas += ["", f"Livros únicos: {len(unicos)} | baixados nesta execução: {baixados} | inéditos: {len(novos)}",
                   f"Situação: {json.dumps(cont, ensure_ascii=False)}"]
        (saida / "consulta.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"\n{len(unicos)} livros únicos | PDFs baixados: {baixados} | inéditos: {len(novos)}")
    print(f"Saída: {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

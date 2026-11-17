#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualização 01 da revisão sistemática (PRISMA 2020, revisão atualizada).

O que faz
- Identificação: todos os registros das buscas diárias por API (artigos/atualizacoes/AAAA-MM-DD/resultados.csv),
  isto é, OpenAlex + Semantic Scholar com a consulta de scripts/buscar_artigos.py. Grupo PRISMA: "outros métodos".
- Registros já avaliados na revisão original (identificação ou snowballing) são retirados e contados à parte:
  os 274 incluídos da revisão original e as decisões já tomadas não mudam.
- Os registros novos passam pelas MESMAS etapas e critérios de scripts/rsl_prisma.py: enriquecimento por DOI,
  deduplicação (CO1), critérios objetivos (CO2–CO4), triagem de título/resumo (CI1–CI4), texto completo (CO5),
  elegibilidade, snowballing regressivo e progressivo e qualidade/extração.
- Saídas em revisao_sistematica/atualizacao_01/ (dados/*.csv, resultados_atualizacao.json, validacao_avaliador.csv).

Limites declarados
- As bases do protocolo (Scopus, IEEE Xplore) não foram consultadas de novo: essa parte da atualização
  depende de nova exportação feita pelo autor.
- A decisão é automática; os estudos incluídos precisam da validação do avaliador, como na revisão original.

Uso: .venv/bin/python scripts/rsl_atualizacao.py [--sem-rede] [--sem-snowballing]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import rsl_prisma as rp  # noqa: E402

ID_ATUALIZACAO = "atualizacao_01"
OUT = rp.BASE / ID_ATUALIZACAO
DIAS = ROOT / "artigos" / "atualizacoes"


def chave_doi(d):
    return rp.norm_doi(d or "")


def chave_tit(t):
    return rp.norm_tit(t or "")


def ja_avaliados_na_original():
    """DOIs e títulos normalizados de tudo que a revisão original avaliou (identificação e snowballing)."""
    dois, tits = set(), set()
    for nome in ("01_registros_identificados.csv", "08_snowballing.csv"):
        p = rp.DADOS / nome
        if not p.exists():
            sys.exit(f"[ERRO] arquivo da revisão original ausente: {p.relative_to(ROOT)}")
        for r in csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"):
            if r.get("doi"):
                dois.add(chave_doi(r["doi"]))
            if r.get("titulo"):
                tits.add(chave_tit(r["titulo"]))
    dois.discard("")
    tits.discard("")
    return dois, tits


def identificacao():
    registros, inventario = [], []
    for d in sorted(p for p in DIAS.iterdir() if p.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}$", p.name)):
        arq = d / "resultados.csv"
        if not arq.exists():
            continue
        recs = rp.ler_artigos(arq)
        for k, r in enumerate(recs):
            r.update({"id": f"a01-{d.name.replace('-', '')}-{k:05d}", "fonte": f"Busca diária OpenAlex + Semantic Scholar ({d.name})",
                      "grupo": "outros", "data_busca": d.name})
        cons = (d / "consulta.txt").read_text(encoding="utf-8") if (d / "consulta.txt").exists() else ""
        m = re.search(r"Correspondências informadas pelas bases: (\{.*\})", cons)
        inventario.append({"fonte": "Busca diária OpenAlex + Semantic Scholar", "grupo": "outros", "arquivo": str(arq.relative_to(ROOT)),
                           "registros": len(recs), "data_hora_busca": d.name, "correspondencias_nas_bases": m.group(1) if m else "",
                           "md5": __import__("hashlib").md5(arq.read_bytes()).hexdigest()[:12]})
        registros += recs
    return registros, inventario


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sem-rede", action="store_true")
    ap.add_argument("--sem-snowballing", action="store_true")
    args = ap.parse_args()
    dados = OUT / "dados"
    dados.mkdir(parents=True, exist_ok=True)
    orig_dados = rp.DADOS
    rp.DADOS = dados                      # todas as gravações das etapas vão para a pasta da atualização
    rp._textos_usados = 0
    s = rp.sessao()
    chave = os.environ.get("OPENALEX_API_KEY", "").strip()
    if chave:
        s.headers["Authorization"] = f"Bearer {chave}"

    R = {"atualizacao": ID_ATUALIZACAO, "data_execucao": date.today().isoformat(),
         "data_limite_revisao_original": rp.DATA_LIMITE.isoformat(),
         "metodo": "mesmas etapas e critérios de scripts/rsl_prisma.py; grupo PRISMA 'outros métodos'",
         "bases_do_protocolo_reconsultadas": False}

    print("▶ 01 identificação (buscas diárias)")
    registros, inventario = identificacao()
    R["inventario"] = inventario
    R["identificados"] = len(registros)
    R["identificados_por_busca"] = dict(Counter(r["data_busca"] for r in registros))
    rp.gravar("01_inventario_fontes.csv", inventario, ["fonte", "grupo", "arquivo", "registros", "data_hora_busca",
                                                      "correspondencias_nas_bases", "md5"])

    print("▶ 02 enriquecimento (OpenAlex por DOI)")
    rp.etapa_enriquecimento(registros, s, args.sem_rede)
    rp.gravar("01_registros_identificados.csv", registros,
              ["id", "fonte", "grupo", "data_busca", "titulo", "ano", "doi", "autores", "veiculo", "tipo_bruto", "tipo", "idioma"])

    print("▶ 03 deduplicação entre as buscas diárias")
    unicos, dup = rp.etapa_deduplicacao(registros)
    R["duplicatas_entre_buscas"] = sum(1 for r in dup if r["decisao"].startswith("duplicata"))
    R["sem_titulo"] = sum(1 for r in dup if r["decisao"].startswith("sem título"))

    print("▶ 03b retirada dos registros já avaliados na revisão original")
    dois, tits = ja_avaliados_na_original()
    novos, ja = [], []
    for r in unicos:
        (ja if (chave_doi(r["doi"]) in dois or chave_tit(r["titulo"]) in tits) else novos).append(r)
    R["ja_avaliados_na_revisao_original"] = len(ja)
    R["novos_para_avaliar"] = len(novos)
    rp.gravar("03b_ja_avaliados_na_original.csv", ja, ["id", "titulo", "ano", "doi"])
    print(f"    {len(ja)} já avaliados na revisão original; {len(novos)} novos")

    print("▶ 04 critérios objetivos")
    aprovados = rp.etapa_objetivos(novos)
    R["co"] = dict(Counter(r["co_decisao"].split(" (")[0] for r in novos))

    print("▶ 05 triagem de título e resumo")
    seguem = rp.etapa_triagem(aprovados)
    R["triagem"] = dict(Counter(r["triagem"] for r in aprovados))

    print(f"▶ 06 texto completo ({len(seguem)} relatos)")
    rp.etapa_texto_completo(seguem, s, args.sem_rede, rotulo=ID_ATUALIZACAO)
    incluidos, eleg = rp.etapa_elegibilidade(seguem)
    R["recuperacao"] = dict(Counter(("recuperado" if r["pdf"] else "nao_recuperado") for r in seguem))
    R["elegibilidade"] = dict(Counter(r["elegibilidade"] for r in eleg))

    inc_sb, eleg_sb, cand = [], [], []
    if not args.sem_snowballing and incluidos:
        print("▶ 08 snowballing dos novos incluídos")
        # exclui o que já foi avaliado na original e nesta atualização
        conhecidos = list(unicos)
        for nome in ("01_registros_identificados.csv", "08_snowballing.csv"):
            for r in csv.DictReader(open(orig_dados / nome, encoding="utf-8-sig"), delimiter=";"):
                conhecidos.append({"doi": rp.norm_doi(r.get("doi", "")), "titulo": r.get("titulo", "")})
        cand = rp.etapa_snowballing(incluidos, conhecidos, s, args.sem_rede)
        R["snowball_identificados"] = dict(Counter(r["fonte"] for r in cand))
        cand_ok = rp.etapa_objetivos(cand, arquivo=None)
        R["snowball_co"] = dict(Counter(r["co_decisao"].split(" (")[0] for r in cand))
        cand_seg = rp.etapa_triagem(cand_ok, arquivo=None)
        R["snowball_triagem"] = dict(Counter(r["triagem"] for r in cand_ok))
        rp.etapa_texto_completo(cand_seg, s, args.sem_rede, rotulo=ID_ATUALIZACAO + "_snowballing")
        inc_sb, eleg_sb = rp.etapa_elegibilidade(cand_seg)
        R["snowball_recuperacao"] = dict(Counter(("recuperado" if r["pdf"] else "nao_recuperado") for r in cand_seg))
        R["snowball_elegibilidade"] = dict(Counter(r["elegibilidade"] for r in eleg_sb))
        rp.gravar("08_snowballing.csv", cand, ["id", "fonte", "titulo", "ano", "doi", "tipo", "co_decisao", "triagem",
                                               "recuperacao", "elegibilidade"])
    rp.gravar("06_07_texto_completo_elegibilidade.csv", eleg + eleg_sb,
              ["id", "fontes", "grupo", "titulo", "ano", "doi", "veiculo", "recuperacao", "pdf", "palavras",
               "n_CI1", "n_CI2", "n_CI3", "n_CI4", "elegibilidade"])

    print("▶ 09 qualidade e extração")
    finais = incluidos + inc_sb
    ext = rp.etapa_qualidade_extracao(finais) if finais else []
    cols = ["id", "titulo", "ano", "autores", "veiculo", "doi", "fontes", "grupo", "tipo"] + list(rp.CATEGORIAS) + \
           ["pm_integrada_decisao", "Q1", "Q2", "Q3", "Q4", "Q_total", "palavras", "contexto_publico_CI4"]
    rp.gravar("09_extracao_qualidade.csv", ext, cols)
    val = [{"id": e["id"], "titulo": e["titulo"], "ano": e["ano"], "doi": e["doi"], "decisao_automatica": "incluído",
            "decisao_avaliador": "", "motivo_se_excluir": "", "Q1_avaliador": "", "Q2_avaliador": "", "Q3_avaliador": "",
            "Q4_avaliador": "", "observacoes": ""} for e in ext]
    rp.gravar("09_validacao_avaliador.csv", val, list(val[0].keys()) if val else ["id"])
    R["incluidos"] = {"busca_diaria": len(incluidos), "snowballing": len(inc_sb)}
    R["n_incluidos_atualizacao"] = len(finais)
    orig = json.loads((rp.BASE / "resultados_prisma.json").read_text(encoding="utf-8"))
    R["n_incluidos_revisao_original"] = orig["n_incluidos"]
    R["n_incluidos_total"] = orig["n_incluidos"] + len(finais)
    R["textos_buscados"] = rp._textos_usados
    (OUT / "resultados_atualizacao.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
    rp.DADOS = orig_dados
    print(json.dumps({k: R[k] for k in ("identificados", "ja_avaliados_na_revisao_original", "novos_para_avaliar",
                                       "incluidos", "n_incluidos_total")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

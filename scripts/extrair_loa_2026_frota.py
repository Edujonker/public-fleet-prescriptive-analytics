#!/usr/bin/env python3
"""
Extrai da LOA 2026 de SC (Lei nº 19.683/2026, texto obtido por OCR em
leis_e_normativas/estaduais_SC/ocr_loa_2026/) as subações ligadas à frota e compara com
a proposta do experimento (resultados_loa_pca_2026/proposta_loa_2026_por_orgao.csv).

Regras (literais, sem estimativa):
  * Subação = linha "AAA.BBBB.CCCCCC Descrição [F] valor" no detalhamento do crédito.
  * Entra se a ação ou a descrição contém "frota", "manutenção de veículos" ou "aquisição de veículos".
  * Classificação: "manutenção" (ação 0262 ou descrição com manutenção/combustível/gestão da frota)
    ou "aquisição" (ação 0261 ou descrição com aquisição/renovação/modernização).
  * Valor por grupo de despesa (3 = outras despesas correntes; 4 = investimentos) somado das linhas seguintes
    até a próxima subação. Meta física ("Veículo mantido unidade N") lida da página de metas.
  * Comparação só onde há correspondência inequívoca de órgão com o cliente da SEA/SC no experimento.

Saída: leis_e_normativas/estaduais_SC/loa_2026_frota_extraido.json (lido por planejamento_loa_pca_2026.py)
"""
from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OCR = ROOT / "leis_e_normativas/estaduais_SC/ocr_loa_2026"
PROP = ROOT / "resultados_loa_pca_2026/proposta_loa_2026_por_orgao.csv"
SAIDA = ROOT / "leis_e_normativas/estaduais_SC/loa_2026_frota_extraido.json"
PDF_PAG0 = 0  # páginas do OCR = páginas do PDF

RX_SUB = re.compile(r"^(\d{3})\.(\d{4})\.(\d{6})\s+(.+?)\s+(?:F\s+)?([\d.]{3,})\s*$")
RX_GRP = re.compile(r"^([34])\s+(Outras Despesas|Investimentos)\s+\d{2}\s+(?:[\d.]{11}\s+)?([\d.]+)\s*$")
RX_UO = re.compile(r"UNIDADE ORÇAMENT[ÁA]RIA\s*\|?:\s*(\d{5})\s+(.+?)\s+Em R\$")
RX_META = re.compile(r"Ve[ií]culo (mantido|adquirido)\s+unidade\s+([\d.]+)\s+([\d.]+)")
CHAVE = re.compile(r"frota|viatura|combust[ií]ve|manuten[cç][aã]o de ve[ií]culo|aquisi[cç][aã]o de ve[ií]culo", re.I)
# Correspondência inequívoca UO da LOA -> cliente SEA/SC no experimento
MAPA = {"16084": "PC SC", "16091": "SSP SC", "53001": "SIE", "54096": "SAP"}
num = lambda s: int(s.replace(".", ""))


def extrair():
    itens = {}
    for f in sorted(OCR.glob("pagina_*.txt")):
        pag = int(f.stem.split("_")[1])
        linhas = [re.sub(r"\s+", " ", l).strip() for l in f.read_text(encoding="utf-8", errors="ignore").splitlines()]
        uo = next((RX_UO.search(l) for l in linhas if RX_UO.search(l)), None)
        acao_atual = ""
        atual = None
        for i, l in enumerate(linhas):
            m_acao = re.match(r"^(\d{3}\.\d{4})\s+(.+)$", l)
            if m_acao and not RX_SUB.match(l):
                acao_atual = m_acao.group(2)
            m = RX_SUB.match(l)
            if m:
                cod = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
                desc = re.sub(r"[\s\]\[|I]+$", "", m.group(4)).strip()
                atual = None
                if CHAVE.search(desc) or CHAVE.search(acao_atual):
                    tipo = ("combustível" if re.search(r"combust", desc, re.I) and not re.search(r"frota|manuten", desc, re.I) else
                            "aquisição" if m.group(2) == "0261" or re.search(r"aquisi|renova|moderniza", desc, re.I) else "manutenção")
                    atual = itens.setdefault(cod, {"codigo": cod, "acao": acao_atual, "descricao": desc, "tipo": tipo,
                                                   "uo": uo.group(1) if uo else "", "unidade": uo.group(2) if uo else "",
                                                   "total": num(m.group(5)), "grupos": {}, "meta_fisica": None, "paginas": []})
                    if pag not in atual["paginas"]:
                        atual["paginas"].append(pag)
                continue
            g = RX_GRP.match(l)
            if g and atual is not None:
                k = "3 – outras despesas correntes" if g.group(1) == "3" else "4 – investimentos"
                atual["grupos"][k] = atual["grupos"].get(k, 0) + num(g.group(3))
            mm = RX_META.search(l)
            if mm:
                # metas: a linha de meta vem logo após a repetição da subação na página de metas
                cod_ant = next((RX_SUB.match(linhas[j]) or re.match(r"^(\d{3})\.(\d{4})\.(\d{6})", linhas[j]))
                               for j in range(i - 1, max(-1, i - 4), -1) if re.match(r"^\d{3}\.\d{4}\.\d{6}", linhas[j])) if i else None
                if cod_ant:
                    c = ".".join(cod_ant.groups()[:3])
                    if c in itens:
                        itens[c]["meta_fisica"] = {"tipo": mm.group(1), "quantidade": num(mm.group(2)), "valor": num(mm.group(3))}
                        if pag not in itens[c]["paginas"]:
                            itens[c]["paginas"].append(pag)
    return list(itens.values())


def proposta():
    if not PROP.exists():
        return {}
    with open(PROP, encoding="utf-8") as f:
        return {r["orgao"]: r for r in csv.DictReader(f, delimiter=";")}


def br(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mi(x):
    return "R$ " + br(x / 1e6) + " mi"


def main():
    itens = extrair()
    prop = proposta()
    comp = []
    for it in itens:
        org = MAPA.get(it["uo"])
        if it["tipo"] == "manutenção" and org and org in prop:
            p = prop[org]
            v = lambda k: float(p[k].replace(",", "."))
            comp.append({"subacao": it["codigo"], "descricao": it["descricao"], "orgao_experimento": org,
                         "loa_2026": it["total"], "proposta_experimento_2026": v("proposta_2026"),
                         "realizado_2024_os_sea": v("realizado_2024"), "razao_loa_sobre_proposta": it["total"] / v("proposta_2026")})
    man = [i for i in itens if i["tipo"] == "manutenção"]; aq = [i for i in itens if i["tipo"] == "aquisição"]; cb = [i for i in itens if i["tipo"] == "combustível"]
    e = html.escape
    linhas_c = "".join(f"<tr><td>{e(c['descricao'])} ({e(c['subacao'])})</td><td>{mi(c['loa_2026'])}</td><td>{mi(c['proposta_experimento_2026'])}</td>"
                       f"<td>{mi(c['realizado_2024_os_sea'])}</td><td>{br(c['razao_loa_sobre_proposta'], 1)}×</td></tr>" for c in comp)
    linhas_i = "".join(f"<tr><td>{e(i['unidade'])}</td><td>{e(i['descricao'])}<br><small>{e(i['codigo'])} · {e(i['acao'])}</small></td><td>{e(i['tipo'])}</td>"
                       f"<td>{mi(i['total'])}</td><td>{'; '.join(f'{e(k)}: {mi(v)}' for k, v in i['grupos'].items()) or '—'}</td>"
                       f"<td>{(str(i['meta_fisica']['quantidade']) + ' veículos ' + i['meta_fisica']['tipo'] + 's') if i['meta_fisica'] else '—'}</td>"
                       f"<td>{', '.join(str(p) for p in i['paginas'])}</td></tr>" for i in sorted(itens, key=lambda x: -x["total"]))
    resumo = (
        "<p><b>LOA 2026 (Lei nº 19.683/2026).</b> O detalhamento do crédito foi lido por OCR (629 páginas). A LOA identifica a frota "
        f"em apenas {len(man)} subações de manutenção, {len(cb)} de combustível e {len(aq)} de aquisição. Nos demais órgãos, inclusive a PM, que responde por metade do gasto "
        "da base da SEA/SC, a manutenção de veículos fica dentro de ações genéricas (por exemplo, 900.0002 “Administração e manutenção de unidades gestoras”) "
        "e o detalhamento chega só ao grupo de despesa. Por isso a LOA não permite isolar a dotação de manutenção da frota da maioria dos órgãos.</p>"
        "<table><tr><th>Unidade orçamentária</th><th>Subação</th><th>Tipo</th><th>Valor LOA</th><th>Por grupo de despesa</th><th>Meta física</th><th>Pág. PDF</th></tr>"
        + linhas_i + "</table>"
        "<p><b>Comparação onde há correspondência de órgão.</b></p>"
        "<table><tr><th>Subação da LOA</th><th>LOA 2026</th><th>Proposta do experimento</th><th>Realizado 2024 (OS da SEA/SC)</th><th>LOA ÷ proposta</th></tr>"
        + linhas_c + "</table>"
        "<p>A diferença vem do escopo: as subações da LOA tratam da gestão da frota (manutenção, combustível e outros custos), e o experimento prevê "
        "apenas as OS do contrato de manutenção da SEA/SC. A proposta ficou próxima do realizado de 2024 nesses órgãos, o que é coerente, mas não "
        "confirma a previsão de 2026. Para comparar orçamento e execução, a fonte adequada é a execução da despesa por elemento e subelemento "
        "(3.3.90.30 e 3.3.90.39) filtrada pelo contrato de manutenção.</p>")
    out = {"fonte": "LOA 2026 SC, Lei nº 19.683/2026; OCR por scripts/ocr_loa_2026.sh", "subacoes_frota": itens,
           "comparacao": comp, "n_manutencao": len(man), "n_aquisicao": len(aq), "n_combustivel": len(cb), "html_resumo": resumo}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(itens)} subações ({len(man)} manutenção, {len(aq)} aquisição); {len(comp)} comparações -> {SAIDA.relative_to(ROOT)}")
    for c in comp:
        print(f"   {c['orgao_experimento']}: LOA {mi(c['loa_2026'])} × proposta {mi(c['proposta_experimento_2026'])} × realizado 2024 {mi(c['realizado_2024_os_sea'])}")
    for i in itens:
        print(f"   {i['codigo']} {i['tipo']:10s} {mi(i['total'])} {i['unidade'][:40]} | {i['descricao'][:50]} | meta {i['meta_fisica']}")


if __name__ == "__main__":
    main()

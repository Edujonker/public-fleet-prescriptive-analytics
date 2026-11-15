#!/usr/bin/env python3
"""Execução orçamentária da frota (empenhos SEF/SC, dados.sc.gov.br) 2024–2026.

Lê os JSON de empenhos (CSV desalinhado: o histórico tem quebras de linha e ';'),
soma o valor com sinal (tipos 3 e 4 já vêm negativos) e agrega:
  - por ano, mês e subelemento de despesa da frota;
  - por subação da LOA 2026 que isola a frota (códigos do loa_2026_frota_extraido.json);
  - participação dos credores no subelemento de manutenção.
Saída: resultados_loa_pca_2026/execucao_orcamentaria_frota.json e figura.
Empenho não é liquidação: empenhos globais/estimativos concentram valor no início do ano.
"""
import gc
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DADOS = ROOT / "dados/execucao_orcamentaria_sc"
OUT = ROOT / "resultados_loa_pca_2026"
LOA = ROOT / "leis_e_normativas/estaduais_SC/loa_2026_frota_extraido.json"
EXP = OUT / "resultado_experimento.json"

SUBEL = {
    "33903039": "Material para manutenção de veículos",
    "33903919": "Manutenção e conservação de veículos",
    "33903001": "Combustíveis e lubrificantes automotivos",
    "33903927": "Locação de veículos",
    "44905252": "Aquisição de veículos",
}
MANUT = ("33903039", "33903919")
GRUPOS = ("manutencao", "combustivel", "locacao", "aquisicao", "outros")


def num(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def main():
    loa = json.loads(LOA.read_text(encoding="utf-8"))
    sub_loa = {s["codigo"].split(".")[-1].lstrip("0"): s for s in loa["subacoes_frota"]}
    anual = defaultdict(float)            # (ano, subel)
    mensal = defaultdict(float)           # (ano, mes, grupo)
    por_sub = defaultdict(float)          # (ano, subacao) só subações da LOA
    por_sub_grupo = defaultdict(float)    # (ano, subacao, grupo de subelemento)
    credor = defaultdict(float)           # (ano, nome) manutenção
    credor_mes = defaultdict(float)       # (ano, mes, nome) manutenção
    orgao = defaultdict(float)            # (ano, orgao) manutenção
    ultima = {}
    for ano in (2024, 2025, 2026):
        arq = DADOS / f"empenhos-{ano}.json"
        if not arq.exists():
            sys.exit(f"falta {arq}")
        dados = json.loads(arq.read_text(encoding="utf-8"))
        for r in dados:
            dt = (r.get("DTLANCAMENTO") or "")[:10]
            if dt[:4] != str(ano):
                continue
            ultima[ano] = max(ultima.get(ano, ""), dt)
            sa = str(r.get("CDSUBACAO") or "").lstrip("0")
            v = num(r.get("VLEMPENHO"))
            se = str(r.get("CDSUBELEMENTO") or "")
            if sa in sub_loa:
                por_sub[(ano, sa)] += v
                gs = ("manutencao" if se in MANUT else "combustivel" if se == "33903001" else
                      "locacao" if se == "33903927" else "aquisicao" if se.startswith("449052") else "outros")
                por_sub_grupo[(ano, sa, gs)] += v
            if se not in SUBEL:
                continue
            anual[(ano, se)] += v
            g = "manutencao" if se in MANUT else se
            mensal[(ano, int(dt[5:7]), g)] += v
            if se in MANUT:
                credor[(ano, (r.get("NMCREDOR") or "").strip())] += v
                credor_mes[(ano, int(dt[5:7]), (r.get("NMCREDOR") or "").strip())] += v
                orgao[(ano, (r.get("NMORGAO") or "").split(": ")[-1].strip())] += v
        del dados
        gc.collect()
        print("lido", ano, "último lançamento", ultima.get(ano))

    mes_fim = int(ultima[2026][5:7])
    R = {"fonte": "dados.sc.gov.br, conjunto 'empenhos' (SEF/SC); valor com sinal (emissão + reforço − anulação − estorno)",
         "ultimo_lancamento": ultima, "mes_fim_2026": mes_fim,
         "subelementos": SUBEL,
         "anual": {str(a): {se: anual[(a, se)] for se in SUBEL} for a in (2024, 2025, 2026)}}
    acum = {}
    for a in (2024, 2025, 2026):
        acum[str(a)] = {g: sum(mensal[(a, m, g)] for m in range(1, mes_fim + 1))
                        for g in ["manutencao", "33903001", "33903927", "44905252"]}
    R["acumulado_jan_ate_mes_fim"] = acum
    R["manutencao_anual"] = {str(a): sum(anual[(a, s)] for s in MANUT) for a in (2024, 2025, 2026)}
    R["manutencao_mensal"] = {str(a): [mensal[(a, m, "manutencao")] for m in range(1, 13)] for a in (2024, 2025, 2026)}
    for a in (2024, 2025):
        tot = R["manutencao_anual"][str(a)]
        R.setdefault("fracao_ate_mes_fim", {})[str(a)] = acum[str(a)]["manutencao"] / tot if tot else None
    cr = {}
    for a in (2024, 2025, 2026):
        itens = sorted(((n, v) for (aa, n), v in credor.items() if aa == a), key=lambda x: -x[1])
        tot = sum(v for _, v in itens)
        cr[str(a)] = [{"credor": n, "valor": v, "participacao": v / tot if tot else 0} for n, v in itens[:5]]
    R["credores_manutencao_top5"] = cr
    # transição de contrato: valor mensal dos dois maiores credores de manutenção
    principais = {c["credor"] for a in cr for c in cr[a][:2]}
    trans = {}
    for (a, m, n), v in credor_mes.items():
        if n in principais:
            trans.setdefault(n, {})[f"{a}-{m:02d}"] = trans.get(n, {}).get(f"{a}-{m:02d}", 0) + v
    R["manutencao_mensal_por_credor_principal"] = {n: dict(sorted(d.items())) for n, d in trans.items()}
    R["primeiro_mes_com_empenho_por_credor"] = {n: min(k for k, v in d.items() if v > 0) for n, d in trans.items()}
    R["orgaos_manutencao_2025_top8"] = [{"orgao": n, "valor": v} for (a, n), v in
                                        sorted(orgao.items(), key=lambda x: -x[1]) if a == 2025][:8]
    comp = []
    for sa, s in sub_loa.items():
        comp.append({"subacao": s["codigo"], "descricao": s["descricao"], "tipo": s["tipo"], "unidade": s["unidade"],
                     "loa_2026": s["total"], "empenhado_2024": por_sub[(2024, sa)], "empenhado_2025": por_sub[(2025, sa)],
                     "empenhado_2026_ate_mes_fim": por_sub[(2026, sa)],
                     "execucao_2026_sobre_loa": por_sub[(2026, sa)] / s["total"] if s["total"] else None,
                     "por_grupo": {str(a): {g: por_sub_grupo[(a, sa, g)] for g in GRUPOS if por_sub_grupo[(a, sa, g)]}
                                   for a in (2024, 2025, 2026)}})
    R["subacoes_loa_empenho"] = sorted(comp, key=lambda x: -x["loa_2026"])

    E = json.loads(EXP.read_text(encoding="utf-8")) if EXP.exists() else {}
    if E:
        R["comparacao_experimento"] = {
            "proposta_2026": E["total_2026"],
            "proposta_2026_ate_mes_fim": sum(v for k, v in E["previsao_mensal_2026"].items() if int(k[5:7]) <= mes_fim),
            "os_sea_2024": E["realizado_anual"]["2024"],
            "os_sea_2025_obs_mais_presumido": E["ano_2025_observado_mais_presumido"],
            "empenho_manutencao_2024": R["manutencao_anual"]["2024"],
            "empenho_manutencao_2025": R["manutencao_anual"]["2025"],
            "empenho_manutencao_2026_ate_mes_fim": acum["2026"]["manutencao"],
            "razao_empenho_sobre_os_2024": R["manutencao_anual"]["2024"] / E["realizado_anual"]["2024"],
        }
        C = R["comparacao_experimento"]
        # proposta convertida para a base de empenho pela razão observada em 2024 (único ano completo nas duas bases)
        C["proposta_2026_base_empenho"] = C["proposta_2026"] * C["razao_empenho_sobre_os_2024"]
        C["empenho_2026_sobre_proposta"] = C["empenho_manutencao_2026_ate_mes_fim"] / C["proposta_2026"]
        C["empenho_2026_sobre_proposta_base_empenho"] = C["empenho_manutencao_2026_ate_mes_fim"] / C["proposta_2026_base_empenho"]
        # indicação (não previsão): ano completo se 2026 repetir a fração jan–mes_fim de 2024 ou de 2025
        # comparação de mesma natureza nas subações que a LOA isola e que o experimento também cobre
        comp_loa = {c["subacao"]: c for c in loa.get("comparacao", [])}
        pares = []
        for x in R["subacoes_loa_empenho"]:
            if x["subacao"] in comp_loa:
                cl = comp_loa[x["subacao"]]
                pares.append({"subacao": x["subacao"], "descricao": x["descricao"], "orgao_experimento": cl["orgao_experimento"],
                              "loa_2026": x["loa_2026"], "proposta_experimento_2026": cl["proposta_experimento_2026"],
                              "os_sea_2024": cl["realizado_2024_os_sea"],
                              "empenho_total": {a: x["empenhado_" + ("2026_ate_mes_fim" if a == "2026" else a)] for a in ("2024", "2025", "2026")},
                              "empenho_manutencao": {a: x["por_grupo"][a].get("manutencao", 0.0) for a in ("2024", "2025", "2026")},
                              "empenho_combustivel": {a: x["por_grupo"][a].get("combustivel", 0.0) for a in ("2024", "2025", "2026")}})
        C["subacoes_mesma_natureza"] = pares
        fr = R["fracao_ate_mes_fim"]
        C["indicacao_ano_2026_pela_fracao"] = {a: C["empenho_manutencao_2026_ate_mes_fim"] / f for a, f in fr.items() if f}
    OUT.mkdir(exist_ok=True)
    (OUT / "execucao_orcamentaria_frota.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")

    # figura: manutenção mensal acumulada 2024/2025/2026 vs proposta acumulada
    meses = list(range(1, 13))
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    cores = {"2024": "#999999", "2025": "#d99a00", "2026": "#00693e"}
    for a in ("2024", "2025", "2026"):
        m = R["manutencao_mensal"][a]
        lim = mes_fim if a == "2026" else 12
        ac, s = [], 0
        for v in m[:lim]:
            s += v
            ac.append(s / 1e6)
        axs[0].plot(meses[:lim], ac, "o-", ms=3, color=cores[a], label=f"empenho {a}")
    if E:
        s, ac = 0, []
        for k in sorted(E["previsao_mensal_2026"]):
            s += E["previsao_mensal_2026"][k]
            ac.append(s / 1e6)
        axs[0].plot(meses, ac, "s--", ms=3, color="#1b3a6e", label="proposta do experimento 2026")
    axs[0].set_title("Manutenção da frota (3.3.90.30.39 + 3.3.90.39.19): acumulado no ano", fontsize=9)
    axs[0].set_xlabel("mês"); axs[0].set_ylabel("R$ milhões"); axs[0].grid(alpha=.3); axs[0].legend(fontsize=7)
    c = [x for x in R["subacoes_loa_empenho"] if x["loa_2026"] >= 1e6]
    def rotulo(x):
        u = x["unidade"]
        sig = u[u.rfind("(") + 1:u.rfind(")")] if "(" in u else u.replace(" S.A.", "")[:22]
        return f"{x['tipo'].capitalize()} – {sig}"
    nomes = [rotulo(x) for x in c]
    y = range(len(c))
    axs[1].barh([i + .2 for i in y], [x["loa_2026"] / 1e6 for x in c], .4, color="#1b3a6e", label="LOA 2026 (dotação inicial)")
    axs[1].barh([i - .2 for i in y], [x["empenhado_2026_ate_mes_fim"] / 1e6 for x in c], .4, color="#00693e",
                label=f"empenhado 2026 até {mes_fim:02d}/2026")
    axs[1].set_yticks(list(y)); axs[1].set_yticklabels(nomes, fontsize=7); axs[1].invert_yaxis()
    axs[1].set_xlabel("R$ milhões"); axs[1].legend(fontsize=7); axs[1].grid(axis="x", alpha=.3)
    axs[1].set_title("Subações da LOA 2026 que isolam a frota (≥ R$ 1 mi)", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "fig_execucao_loa_2026.png", dpi=180); plt.close(fig)
    print(json.dumps(R.get("comparacao_experimento"), indent=1))
    print("OK", OUT / "execucao_orcamentaria_frota.json")


if __name__ == "__main__":
    main()

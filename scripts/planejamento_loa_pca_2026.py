#!/usr/bin/env python3
"""
Experimento: proposta de LOA e PCA 2026 para a manutenção da frota a partir dos
dados da SEA/SC observados até o último mês completo, com avaliação retrospectiva.

Regras do experimento (nada é digitado à mão):
  * Série: valor aprovado das OS COBRADAS por mês da transação (dt_transacao).
  * Início do treino: jan/2022, primeiro ano civil completo depois da implantação
    do contrato (2020-10 a 2021 têm rampa de adesão dos órgãos).
  * Corte: último mês com pelo menos 50% das OS do mesmo mês do ano anterior.
    Os meses seguintes até dez/2025 são PRESUMIDOS pelo modelo e marcados como tal.
  * Modelos candidatos: sazonal ingênuo com crescimento anual (SNg), ETS amortecido
    em log, SARIMA(1,0,0)(0,1,1)12 em log e a média dos três.
  * Avaliação retrospectiva (o "comparativo" do experimento):
      BT1  treino até dez/2023 -> previsão de 2024 (12 meses realizados)
      BT2  treino até dez/2024 -> previsão de jan/2025 até o corte (realizado)
    O modelo da proposta é o de menor erro absoluto médio no total do período.
  * Incerteza: 2.000 trajetórias simuladas do ETS e do SARIMA (anos 2026).
  * Distribuição por órgão (cd_cliente), peças/mão de obra e itens do PCA:
    participação nos 12 últimos meses observados, com o mesmo teste retrospectivo
    (participações de 2023 aplicadas ao total real de 2024).
  * Preços do PCA: mediana do preço unitário nos 12 últimos meses, sem correção.

Saídas:
  resultados_loa_pca_2026/  (CSV, JSON, figuras)
  relatorio_loa_pca_2026.pdf  e  relatorios_pdf/relatorio_loa_pca_2026.pdf
Uso: .venv/bin/python scripts/planejamento_loa_pca_2026.py
"""
from __future__ import annotations

import html
import json
import shutil
import warnings
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import weasyprint
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
import comparacao_loa_execucao
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "dissertacao_frotas/dados/processados"
RAW = ROOT / "dados/Geral_de_OS_23439885_202609110934.csv"
OUT = ROOT / "resultados_loa_pca_2026"
LOA_OFICIAL = ROOT / "leis_e_normativas/estaduais_SC/loa_2026_frota_extraido.json"
PCA_OFICIAL = ROOT / "leis_e_normativas/estaduais_SC/pca_2026_pncp.json"
INICIO = pd.Period("2022-01", "M")
ANO = 2026
NSIM = 2000
RNG = 42


# ------------------------------------------------------------------ dados
def carregar():
    o = pd.read_parquet(PROC / "os_consolidadas_processadas.parquet",
                        columns=["ds_os_status", "dt_transacao", "vl_aprovado_total", "vl_aprovado_pecas", "vl_aprovado_mo", "cd_cliente"])
    o = o[o.ds_os_status == "COBRADAS"].copy()
    o["m"] = pd.to_datetime(o.dt_transacao, errors="coerce").dt.to_period("M")
    o["cd_cliente"] = o.cd_cliente.astype(str).str.replace(r"\.0$", "", regex=True)
    it = pd.read_parquet(PROC / "os_itens_processados.parquet",
                         columns=["ds_os_status", "dt_transacao", "ds_peca", "nr_quantidade_pecas", "Valor_Aprovado_Peca"])
    it = it[(it.ds_os_status == "COBRADAS") & (it.Valor_Aprovado_Peca > 0) & (it.nr_quantidade_pecas > 0)].copy()
    it["m"] = pd.to_datetime(it.dt_transacao, errors="coerce").dt.to_period("M")
    nomes = pd.read_csv(RAW, sep=";", usecols=[0, 1], dtype=str, encoding="latin-1", on_bad_lines="skip")
    nomes.columns = ["cd_cliente", "nome"]
    nomes = nomes.groupby("cd_cliente").nome.agg(lambda s: s.value_counts().index[0]).str.replace("MANUTENCAO ", "", regex=False).str.strip(" -")
    return o, it, nomes.to_dict()


def definir_corte(cont: pd.Series, inicio: pd.Period) -> pd.Period:
    """Último mês, a partir do início, com pelo menos 50% das OS do mesmo mês do ano anterior."""
    corte = None
    for m in cont.index[cont.index >= inicio]:
        ref = cont.get(m - 12)
        if ref is None or cont[m] < 0.5 * ref:
            break
        corte = m
    return corte


# ------------------------------------------------------------------ modelos
def f_sng(y: pd.Series, h: int) -> np.ndarray:
    g = y.iloc[-12:].sum() / y.iloc[-24:-12].sum()
    base = y.iloc[-12:].values
    return np.array([base[i % 12] * g ** (1 + i // 12) for i in range(h)])


def ajustar_ets(y):
    return ETSModel(np.log(y), error="add", trend="add", damped_trend=True, seasonal="add",
                    seasonal_periods=12).fit(disp=False, maxiter=2000)


def ajustar_sarima(y):
    return SARIMAX(np.log(y.values), order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="c").fit(disp=False)


def f_ets(y, h):
    return np.exp(np.asarray(ajustar_ets(y).forecast(h), float))


def f_sarima(y, h):
    return np.exp(ajustar_sarima(y).forecast(h))


MODELOS = {"SNg (sazonal ingênuo com crescimento)": f_sng, "ETS amortecido (log)": f_ets, "SARIMA (log)": f_sarima}


def prever(y, h):
    p = {k: np.asarray(f(y, h), float) for k, f in MODELOS.items()}
    p["Média dos três"] = np.mean(list(p.values()), axis=0)
    return p


def simular(y, h, idx_ano):
    """Totais do ano simulados (soma das trajetórias nos meses de idx_ano)."""
    out = {}
    e = ajustar_ets(y)
    s = np.asarray(e.simulate(h, anchor="end", repetitions=NSIM, random_errors="bootstrap", rng=np.random.default_rng(RNG)))
    out["ETS amortecido (log)"] = np.exp(s[idx_ano]).sum(axis=0)
    sa = ajustar_sarima(y)
    ss = np.asarray(sa.simulate(h, anchor="end", repetitions=NSIM, rng=np.random.default_rng(RNG))).reshape(h, -1)
    out["SARIMA (log)"] = np.exp(ss[idx_ano]).sum(axis=0)
    return out


# ------------------------------------------------------------------ util
def br(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mi(x):
    return "R$ " + br(x / 1e6, 2) + " mi"


def pct(x, nd=1):
    return br(100 * x, nd) + "%"


def erro_ponderado(prev: pd.Series, real: pd.Series) -> float:
    a = pd.concat([prev, real], axis=1).fillna(0)
    return float((a.iloc[:, 0] - a.iloc[:, 1]).abs().sum() / a.iloc[:, 1].sum())


# ------------------------------------------------------------------ principal
def main():
    OUT.mkdir(exist_ok=True)
    o, it, nomes = carregar()
    serie_full = o.groupby("m").vl_aprovado_total.sum()
    cont = o.groupby("m").size()
    corte = definir_corte(cont, INICIO)
    meses = pd.period_range(INICIO, corte, freq="M")
    y = serie_full.reindex(meses).astype(float)
    y.index = y.index.to_timestamp()
    R = {"gerado_em": datetime.now().isoformat(timespec="seconds"), "inicio_treino": str(INICIO), "corte": str(corte),
         "regra_corte": "último mês com >= 50% das OS do mesmo mês do ano anterior",
         "meses_apos_corte_na_base": {str(k): int(v) for k, v in cont[cont.index > corte].items()}}

    # -------- avaliação retrospectiva
    bts = {"BT1 (treino até dez/2023 → 2024)": (pd.Timestamp("2023-12-01"), pd.Timestamp("2024-12-01")),
           "BT2 (treino até dez/2024 → jan–" + corte.strftime("%b/%Y").lower() + ")": (pd.Timestamp("2024-12-01"), corte.to_timestamp())}
    bt_res, bt_mensal = {}, []
    for nome, (fim_tr, fim_te) in bts.items():
        tr, te = y[:fim_tr], y[(y.index > fim_tr) & (y.index <= fim_te)]
        p = prever(tr, len(te))
        bt_res[nome] = {}
        for k, v in p.items():
            bt_res[nome][k] = {"previsto": float(v.sum()), "realizado": float(te.sum()),
                               "erro_total_pct": float(v.sum() / te.sum() - 1),
                               "mape_mensal": float(np.mean(np.abs(v / te.values - 1)))}
            for d, pv, rv in zip(te.index, v, te.values):
                bt_mensal.append({"teste": nome, "modelo": k, "mes": d.strftime("%Y-%m"), "previsto": pv, "realizado": rv})
    pd.DataFrame(bt_mensal).to_csv(OUT / "avaliacao_retrospectiva_mensal.csv", sep=";", index=False, decimal=",")
    media_erro = {k: float(np.mean([abs(bt_res[b][k]["erro_total_pct"]) for b in bt_res])) for k in bt_res[next(iter(bt_res))]}
    escolhido = min(media_erro, key=media_erro.get)
    R["avaliacao_retrospectiva"] = bt_res
    R["erro_medio_abs_total"] = media_erro
    R["modelo_escolhido"] = escolhido

    # -------- previsão final
    futuro = pd.date_range(corte.to_timestamp() + pd.offsets.MonthBegin(1), f"{ANO}-12-01", freq="MS")
    p = prever(y, len(futuro))
    prev = pd.Series(p[escolhido], index=futuro)
    idx_ano = np.where(futuro.year == ANO)[0]
    sims = simular(y, len(futuro), idx_ano)
    presumidos = prev[prev.index.year < ANO]
    total_ano = float(prev[prev.index.year == ANO].sum())
    obs_2025 = float(y[y.index.year == 2025].sum())
    R["presumidos_2025"] = {d.strftime("%Y-%m"): float(v) for d, v in presumidos.items()}
    R["ano_2025_observado_mais_presumido"] = obs_2025 + float(presumidos.sum())
    R["previsao_mensal_2026"] = {d.strftime("%Y-%m"): float(v) for d, v in prev[prev.index.year == ANO].items()}
    R["total_2026"] = total_ano
    R["todos_modelos_total_2026"] = {k: float(np.asarray(v)[idx_ano].sum()) for k, v in p.items()}
    R["incerteza_2026"] = {k: {q: float(np.percentile(v, q)) for q in (5, 10, 50, 90, 95)} for k, v in sims.items()}
    hist = {int(a): float(serie_full[[m for m in serie_full.index if m.year == a]].sum()) for a in (2022, 2023, 2024)}
    R["realizado_anual"] = hist

    # -------- distribuição: órgãos, peças/MO
    ult12 = pd.period_range(corte - 11, corte, freq="M")
    base12 = o[o.m.isin(ult12)]
    sh_org = base12.groupby("cd_cliente").vl_aprovado_total.sum() / base12.vl_aprovado_total.sum()
    sh_pecas = base12.vl_aprovado_pecas.sum() / base12.vl_aprovado_total.sum()
    o23, o24 = o[o.m.dt.year == 2023], o[o.m.dt.year == 2024]
    sh23 = o23.groupby("cd_cliente").vl_aprovado_total.sum() / o23.vl_aprovado_total.sum()
    real24 = o24.groupby("cd_cliente").vl_aprovado_total.sum()
    R["teste_distribuicao_orgaos_2024"] = erro_ponderado(sh23 * real24.sum(), real24)
    sp23 = o23.vl_aprovado_pecas.sum() / o23.vl_aprovado_total.sum()
    sp24 = o24.vl_aprovado_pecas.sum() / o24.vl_aprovado_total.sum()
    R["participacao_pecas"] = {"ultimos_12_meses": float(sh_pecas), "2023": float(sp23), "2024": float(sp24)}

    loa = pd.DataFrame({"cd_cliente": sh_org.index, "orgao": [nomes.get(c, c) for c in sh_org.index], "participacao": sh_org.values})
    loa["proposta_2026"] = loa.participacao * total_ano
    loa["pecas_339030"] = loa.proposta_2026 * sh_pecas
    loa["mao_de_obra_339039"] = loa.proposta_2026 * (1 - sh_pecas)
    loa["realizado_2024"] = loa.cd_cliente.map(real24).fillna(0)
    loa = loa.sort_values("proposta_2026", ascending=False)
    loa.to_csv(OUT / "proposta_loa_2026_por_orgao.csv", sep=";", index=False, decimal=",")

    # -------- PCA (itens)
    it12 = it[it.m.isin(ult12)]
    gi = it12.groupby("ds_peca").agg(valor=("Valor_Aprovado_Peca", "sum"), qtd=("nr_quantidade_pecas", "sum"))
    gi["preco_mediano"] = it12.assign(u=it12.Valor_Aprovado_Peca / it12.nr_quantidade_pecas).groupby("ds_peca").u.median()
    gi["participacao"] = gi.valor / gi.valor.sum()
    gi = gi.sort_values("valor", ascending=False)
    pecas_2026 = total_ano * sh_pecas
    N = 40
    top = gi.head(N).copy()
    top["valor_2026"] = top.participacao * pecas_2026
    top["qtd_2026"] = (top.valor_2026 / top.preco_mediano).round(0)
    pca = top.reset_index()[["ds_peca", "participacao", "preco_mediano", "qtd_2026", "valor_2026"]]
    pca.loc[len(pca)] = ["DEMAIS PEÇAS (" + br(len(gi) - N) + " descrições)", gi.participacao.iloc[N:].sum(), np.nan, np.nan, gi.participacao.iloc[N:].sum() * pecas_2026]
    pca.loc[len(pca)] = ["SERVIÇOS DE MÃO DE OBRA (contrato de manutenção)", np.nan, np.nan, np.nan, total_ano * (1 - sh_pecas)]
    pca.to_csv(OUT / "proposta_pca_2026_itens.csv", sep=";", index=False, decimal=",")
    i23, i24 = it[it.m.dt.year == 2023], it[it.m.dt.year == 2024]
    s23 = i23.groupby("ds_peca").Valor_Aprovado_Peca.sum() / i23.Valor_Aprovado_Peca.sum()
    r24 = i24.groupby("ds_peca").Valor_Aprovado_Peca.sum()
    top24 = r24.sort_values(ascending=False).head(N).index
    R["teste_pca_itens_2024"] = {"erro_ponderado_top40": erro_ponderado((s23 * r24.sum()).reindex(top24).fillna(0), r24.reindex(top24)),
                                 "itens_top40_2024_ja_no_top40_2023": int(len(set(top24) & set(s23.sort_values(ascending=False).head(N).index)))}
    R["pca_cobertura_top40"] = float(gi.participacao.head(N).sum())

    # -------- comparação com documentos oficiais (se já extraídos)
    R["loa_oficial"] = json.loads(LOA_OFICIAL.read_text(encoding="utf-8")) if LOA_OFICIAL.exists() else None
    R["pca_oficial"] = json.loads(PCA_OFICIAL.read_text(encoding="utf-8")) if PCA_OFICIAL.exists() else None

    (OUT / "resultado_experimento.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")

    # -------- figuras
    fig, ax = plt.subplots(figsize=(10, 4.2))
    yo = serie_full[(serie_full.index >= INICIO)]
    ax.plot(yo.index.to_timestamp(), yo.values / 1e6, color="#999", lw=1, label="base (inclui meses incompletos)")
    ax.plot(y.index, y.values / 1e6, color="#00693e", lw=2, label="observado (até o corte)")
    ax.plot(presumidos.index, presumidos.values / 1e6, "o--", color="#d99a00", label="presumido (out–dez/2025)")
    p26 = prev[prev.index.year == ANO]
    ax.plot(p26.index, p26.values / 1e6, "s-", color="#1b3a6e", label=f"previsão {ANO} ({escolhido})")
    ax.axvline(corte.to_timestamp(), color="#b04a3a", ls=":", lw=1)
    ax.set_ylabel("R$ milhões / mês"); ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=.3)
    ax.set_title("Valor aprovado mensal em manutenção da frota – SEA/SC")
    fig.tight_layout(); fig.savefig(OUT / "fig_serie_previsao.png", dpi=180); plt.close(fig)

    bm = pd.DataFrame(bt_mensal)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, (nome, _) in zip(axs, bts.items()):
        d = bm[(bm.teste == nome)]
        r = d[d.modelo == escolhido]
        ax.plot(pd.to_datetime(r.mes), r.realizado / 1e6, "k-o", ms=3, label="realizado")
        for k, c in zip(list(MODELOS) + ["Média dos três"], ["#00693e", "#1b3a6e", "#d99a00", "#b04a3a"]):
            dd = d[d.modelo == k]
            ax.plot(pd.to_datetime(dd.mes), dd.previsto / 1e6, "--", color=c, lw=1.4 if k == escolhido else .9, label=k)
        ax.set_title(nome, fontsize=9); ax.tick_params(axis="x", labelsize=7, rotation=45); ax.grid(alpha=.3)
    axs[0].set_ylabel("R$ milhões / mês"); axs[1].legend(fontsize=6.5)
    fig.tight_layout(); fig.savefig(OUT / "fig_avaliacao_retrospectiva.png", dpi=180); plt.close(fig)

    # -------- PDF
    gerar_pdf(R, loa, pca, bt_res, escolhido, corte)


def gerar_pdf(R, loa, pca, bt_res, escolhido, corte):
    e = html.escape
    def tab(cab, linhas, cls=""):
        return (f"<table class='{cls}'><tr>" + "".join(f"<th>{e(c)}</th>" for c in cab) + "</tr>"
                + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas) + "</table>")
    total = R["total_2026"]
    inc = R["incerteza_2026"]
    a25 = R["ano_2025_observado_mais_presumido"]
    h24 = R["realizado_anual"][2024]
    bt_linhas = []
    for b, d in bt_res.items():
        for k, v in d.items():
            bt_linhas.append([e(b), ("<b>" + e(k) + "</b>") if k == escolhido else e(k), mi(v["previsto"]), mi(v["realizado"]),
                              br(100 * v["erro_total_pct"], 1) + "%", br(100 * v["mape_mensal"], 1) + "%"])
    css = """@page { size: A4; margin: 2cm 1.8cm; @bottom-right { content: counter(page) " / " counter(pages); font: 8.5pt Arial; color:#555; } }
body { font-family: Arial, sans-serif; font-size: 10pt; line-height: 1.42; } h1 { color:#00693e; font-size: 18pt; margin:0 0 4pt; }
.sub { color:#444; margin-bottom: 12pt; } h2 { color:#00693e; font-size: 13pt; border-bottom: 1.5pt solid #00693e; margin: 16pt 0 6pt; }
table { width:100%; border-collapse: collapse; margin: 4pt 0 10pt; font-size: 8.6pt; } th { background:#00693e; color:#fff; text-align:left; padding:3pt 4pt; }
td { border-bottom: .5pt solid #c9d6cf; padding: 2.4pt 4pt; } tr:nth-child(even) td { background:#f3f8f5; }
.nota { background:#fff7e0; border-left: 3pt solid #d99a00; padding: 5pt 8pt; margin: 6pt 0; font-size: 9pt; }
.kpi { display:flex; gap:6pt; margin: 6pt 0 10pt; } .kpi div { flex:1; border:1pt solid #00693e; border-radius:3pt; padding:5pt 7pt; } .kpi b { display:block; font-size: 14pt; color:#00693e; }
img { width:100%; } ul { margin: 3pt 0 8pt 14pt; padding:0; } li { margin: 2pt 0; } .small td { font-size: 7.8pt; }"""
    m_ap = {k: int(v) for k, v in R["meses_apos_corte_na_base"].items()}
    H = [f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>",
         "<h1>Planejamento da LOA e do PCA 2026 – manutenção da frota</h1>",
         f"<p class='sub'>Experimento com dados da SEA/SC observados até {e(corte.strftime('%m/%Y'))} · gerado em {e(R['gerado_em'][:16].replace('T', ' '))} por "
         "<code>scripts/planejamento_loa_pca_2026.py</code></p>",
         f"<div class='kpi'><div><b>{mi(total)}</b>proposta 2026 ({e(escolhido)})</div>"
         f"<div><b>{mi(inc[escolhido if escolhido in inc else 'SARIMA (log)'][10])} – {mi(inc[escolhido if escolhido in inc else 'SARIMA (log)'][90])}</b>intervalo de 80% ({e(escolhido if escolhido in inc else 'SARIMA (log)')})</div>"
         f"<div><b>{br(100 * R['erro_medio_abs_total'][escolhido], 1)}%</b>erro médio no total anual (testes retrospectivos)</div></div>",
         "<h2>1. Pergunta e desenho</h2>",
         "<p>Com os dados disponíveis até o fim de 2025, quanto o Estado deveria reservar na LOA de 2026 para manutenção da frota, distribuído "
         "por órgão e por natureza de despesa, e que itens o PCA de 2026 deveria prever? Como o realizado de 2026 ainda não está na base, a "
         "qualidade do método é medida em anos já conhecidos: os mesmos modelos foram treinados até dez/2023 para prever 2024 e até dez/2024 para "
         f"prever jan–{e(corte.strftime('%m/%Y'))}.</p>",
         "<div class='nota'><b>Dados disponíveis.</b> A extração da SEA/SC tem cobertura completa até "
         f"{e(corte.strftime('%m/%Y'))}. Depois disso a base tem apenas " + ", ".join(f"{k}: {v}" for k, v in m_ap.items()) +
         " OS cobradas por mês. Esses meses foram tratados como ausentes; out–dez/2025 foram presumidos pelo modelo e aparecem destacados. "
         "Os empenhos da SEF/SC (seção 6) mostram que o corte coincide com a troca do contrato de manutenção, e não com queda do gasto.</div>",
         "<h2>2. Teste retrospectivo dos modelos</h2>",
         tab(["Teste", "Modelo", "Previsto", "Realizado", "Erro no total", "Erro mensal médio"], bt_linhas, "small"),
         f"<p>Escolhido: <b>{e(escolhido)}</b>, o de menor erro absoluto médio no total do período "
         f"({br(100 * R['erro_medio_abs_total'][escolhido], 1)}%). Erros médios dos demais: "
         + "; ".join(f"{e(k)} {br(100 * v, 1)}%" for k, v in R["erro_medio_abs_total"].items() if k != escolhido) + ".</p>",
         f"<img src='{(OUT / 'fig_avaliacao_retrospectiva.png').as_uri()}'>",
         "<h2>3. Projeção</h2>", f"<img src='{(OUT / 'fig_serie_previsao.png').as_uri()}'>",
         tab(["Período", "Valor", "Base"], [
             ["2022 (realizado)", mi(R["realizado_anual"][2022]), "observado"],
             ["2023 (realizado)", mi(R["realizado_anual"][2023]), "observado"],
             ["2024 (realizado)", mi(h24), "observado"],
             ["2025", mi(a25), f"observado até {corte.strftime('%m/%Y')} + presumido " + ", ".join(f"{k}: {mi(v)}" for k, v in R["presumidos_2025"].items())],
             [f"<b>2026 (proposta)</b>", f"<b>{mi(total)}</b>", f"{e(escolhido)}; variação de {br(100 * (total / a25 - 1), 1)}% sobre 2025"],
         ]),
         tab(["Modelo", "Total 2026 (ponto)", "P10", "P50", "P90"],
             [[e(k), mi(R["todos_modelos_total_2026"][k]),
               mi(inc[k][10]) if k in inc else "—", mi(inc[k][50]) if k in inc else "—", mi(inc[k][90]) if k in inc else "—"]
              for k in R["todos_modelos_total_2026"]]),
         "<p>Os percentis vêm de 2.000 trajetórias simuladas de cada modelo estatístico. O SNg e a média não têm modelo de erro próprio.</p>",
         "<h2>4. Proposta de LOA 2026 por órgão</h2>",
         f"<p>Distribuição pela participação de cada órgão nos 12 meses até {e(corte.strftime('%m/%Y'))}. Peças: {pct(R['participacao_pecas']['ultimos_12_meses'])} do valor "
         f"(2023: {pct(R['participacao_pecas']['2023'])}; 2024: {pct(R['participacao_pecas']['2024'])}). Teste do critério: as participações de 2023 aplicadas ao total "
         f"real de 2024 erram {pct(R['teste_distribuicao_orgaos_2024'])} do valor (soma dos erros absolutos por órgão).</p>",
         "<div class='nota'>As colunas 3.3.90.30 (material de consumo) e 3.3.90.39 (serviços de terceiros – PJ) seguem a classificação usual de peças e "
         "de mão de obra. Em contratos de gerenciamento de frota, peças podem ser empenhadas como serviço; a natureza deve ser confirmada no contrato vigente.</div>",
         tab(["Órgão", "Participação", "Proposta 2026", "Peças (3.3.90.30)", "Mão de obra (3.3.90.39)", "Realizado 2024"],
             [[e(r.orgao), pct(r.participacao, 2), mi(r.proposta_2026), mi(r.pecas_339030), mi(r.mao_de_obra_339039), mi(r.realizado_2024)]
              for r in loa.itertuples()], "small"),
         "<h2>5. Proposta de PCA 2026</h2>",
         f"<p>As 40 descrições de peça de maior gasto cobrem {pct(R['pca_cobertura_top40'])} do valor de peças. Valor por item = participação × peças previstas para 2026; "
         "quantidade = valor ÷ preço unitário mediano dos últimos 12 meses (sem correção de preço). Teste: as participações de 2023 aplicadas a 2024 erram "
         f"{pct(R['teste_pca_itens_2024']['erro_ponderado_top40'])} do valor dos 40 maiores itens de 2024; "
         f"{R['teste_pca_itens_2024']['itens_top40_2024_ja_no_top40_2023']} desses 40 já estavam entre os 40 maiores de 2023.</p>",
         tab(["Item", "Participação", "Preço mediano", "Quantidade 2026", "Valor 2026"],
             [[e(r.ds_peca), pct(r.participacao, 2) if pd.notna(r.participacao) else "—", ("R$ " + br(r.preco_mediano, 2)) if pd.notna(r.preco_mediano) else "—",
               br(r.qtd_2026) if pd.notna(r.qtd_2026) else "—", mi(r.valor_2026)] for r in pca.itertuples()], "small"),
         "<h2>6. Comparação com a LOA e o PCA oficiais de 2026</h2>"]
    lo, pc = R.get("loa_oficial"), R.get("pca_oficial")
    if lo:
        H.append(lo.get("html_resumo", ""))
    else:
        H.append("<p><b>LOA 2026:</b> o documento oficial (Lei nº 19.683/2026, SEF/SC) ainda não foi extraído para comparação.</p>")
    bloco_exec = comparacao_loa_execucao.html_bloco(fig_caption="Empenho acumulado de manutenção da frota (2024–2026) contra a proposta do experimento, e subações da LOA 2026.")
    if bloco_exec:
        H.append("<h3>Execução orçamentária de 2026 (empenhos SEF/SC)</h3>" + bloco_exec)
    if pc:
        H.append(pc.get("html_resumo", ""))
    else:
        H.append("<p><b>PCA 2026:</b> a consulta ao PNCP não retornou dados nas tentativas feitas (serviço indisponível ou sem plano publicado).</p>")
    H += ["<h2>7. Conclusões</h2><ul>",
          f"<li>A proposta para 2026 é de {mi(total)}, com intervalo de 80% de {mi(inc[escolhido if escolhido in inc else 'SARIMA (log)'][10])} a {mi(inc[escolhido if escolhido in inc else 'SARIMA (log)'][90])} pelo modelo escolhido. "
          f"O valor fica {br(100 * (total / a25 - 1), 1)}% acima de 2025 (observado + presumido) e {br(100 * (total / h24 - 1), 1)}% acima de 2024.</li>",
          f"<li>Nos testes retrospectivos, o modelo escolhido errou o total do período em média {br(100 * R['erro_medio_abs_total'][escolhido], 1)}%. "
          "Esse é o erro a esperar na dotação, antes de mudanças de frota, preços ou contrato.</li>",
          f"<li>A distribuição entre órgãos é estável (erro de {pct(R['teste_distribuicao_orgaos_2024'])} no teste), o que permite planejar por unidade com a participação recente.</li>",
          f"<li>O PCA concentra-se em poucos itens: 40 descrições respondem por {pct(R['pca_cobertura_top40'])} das peças, e a lista dos maiores itens muda pouco entre anos.</li>",
          ] + ["<li>" + e(x) + "</li>" for x in ((comparacao_loa_execucao.conteudo() or {}).get("conclusoes") or
               ["A avaliação do 2026 realizado depende de nova extração da SEA/SC ou dos dados de execução orçamentária."])] + ["</ul>",
          "<h2>8. Limitações</h2><ul><li>A série cobre o contrato de manutenção; abastecimento não entra (a base de abastecimentos termina em fev/2022).</li>"
          "<li>O valor é o aprovado nas OS cobradas, que se aproxima da despesa liquidada, mas não é o empenho.</li>"
          "<li>Não há correção de preços nem variáveis externas (tamanho da frota, IPCA); a projeção estende o padrão de 2022–2025.</li>"
          "<li>Dois testes retrospectivos são poucos para estimar o erro com precisão.</li></ul></body></html>"]
    pdf = ROOT / "relatorio_loa_pca_2026.pdf"
    weasyprint.HTML(string="\n".join(H), base_url=str(ROOT)).write_pdf(pdf)
    (ROOT / "relatorios_pdf").mkdir(exist_ok=True)
    shutil.copy2(pdf, ROOT / "relatorios_pdf" / pdf.name)
    print("OK:", pdf, "| corte:", corte, "| escolhido:", escolhido, "| total 2026:", mi(total))


if __name__ == "__main__":
    main()

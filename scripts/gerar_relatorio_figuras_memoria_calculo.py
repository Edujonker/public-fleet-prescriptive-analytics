#!/usr/bin/env python3
"""
Relatório de figuras dos testes com explicação detalhada e memória de cálculo.

Para cada figura gerada pelos testes (pipeline 03–09, ablação H1, grafo Neo4j, XAI e
experimento LOA/PCA) o relatório mostra: o que a figura mostra, dados e filtros,
memória de cálculo com os números reais (lidos dos JSONs de resultado), como ler,
valores fixos no código e ressalvas. Ao final, executa verificações que recalculam
números a partir dos dados processados e comparam com os JSONs.

Saída: relatorio_figuras_memoria_calculo.pdf (raiz) e cópia em relatorios_pdf/
Uso:   .venv/bin/python scripts/gerar_relatorio_figuras_memoria_calculo.py
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import weasyprint

import sys as _sys_ia; from pathlib import Path as _P_ia; _sys_ia.path.insert(0, str(_P_ia(__file__).resolve().parent))
import uso_etico_ia; uso_etico_ia.ativar()  # seção "Uso ético de inteligência artificial" em todo PDF
ROOT = Path(__file__).resolve().parent.parent
DF = ROOT / "dissertacao_frotas"
LOGS = DF / "resultados/logs"
FIGS = DF / "resultados/figuras"
PROC = DF / "dados/processados"
LOA = ROOT / "resultados_loa_pca_2026"
SAIDA = ROOT / "relatorio_figuras_memoria_calculo.pdf"
e = html.escape


def J(nome):
    p = LOGS / nome
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def br(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def rs(x, nd=2):
    return "R$ " + br(x, nd)


def pct(x, nd=2):
    return br(100 * x, nd) + "%"


# ------------------------------------------------------------------ dados
D = J("relatorio_analise_descritiva.json")
M = J("relatorio_modelagem_preditiva.json")
AB = J("relatorio_ablacao_h1.json")
AN = J("relatorio_deteccao_anomalias.json")
GR = J("relatorio_teoria_grafos.json")
X = J("relatorio_explicabilidade_xai.json")
MI = J("relatorio_otimizacao_milp.json")
CE = J("certificado_reprodutibilidade_cientifica.json")
GN = J("relatorio_analise_grafos_neo4j.json")
NC = J("relatorio_neo4j_grafo.json")
LP = json.loads((LOA / "resultado_experimento.json").read_text(encoding="utf-8")) if (LOA / "resultado_experimento.json").exists() else {}


def figura_ablacao():
    """Figura nova: MAE M × M+P com IC do ganho e estresse de sementes (dados da etapa 04b)."""
    if not AB:
        return None
    ps = AB["estresse_sementes"]["por_semente"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    a1.bar(["M (manutenção)", "M+P (manutenção + patrimônio)"], [AB["mae_M"], AB["mae_MP"]], color=["#94a3b8", "#00693e"], width=.5)
    for i, v in enumerate([AB["mae_M"], AB["mae_MP"]]):
        a1.text(i, v + 15, rs(v), ha="center", fontsize=9, fontweight="bold")
    a1.set_ylim(min(AB["mae_M"], AB["mae_MP"]) * 0.9, max(AB["mae_M"], AB["mae_MP"]) * 1.05)
    a1.set_ylabel("MAE no teste (R$ por veículo-mês)")
    a1.set_title(f"Ganho {pct(AB['ganho_mae_pct'])} (semente 42)", fontsize=10)
    g = [100 * x["ganho_mae_pct"] for x in ps]
    a2.scatter([str(x["semente"]) for x in ps], g, color="#1b3a6e", s=40, zorder=3)
    lo, hi = [100 * x for x in AB["ic95_ganho_bootstrap_pareado"]]
    a2.axhspan(lo, hi, color="#9bb7a8", alpha=.4, label=f"IC 95% bootstrap ({br(lo)}% a {br(hi)}%)")
    a2.axhline(100 * AB["meta_h1"], color="#b04a3a", ls="--", label=f"meta H1 ({br(100 * AB['meta_h1'], 0)}%)")
    a2.axhline(0, color="#555", lw=.8)
    a2.set_ylabel("Ganho no MAE (%)"); a2.set_xlabel("Semente")
    a2.set_title("Estresse: 5 sementes e intervalo de confiança", fontsize=10); a2.legend(fontsize=7.5)
    fig.tight_layout()
    out = FIGS / "ablacao_h1_m_vs_mp.png"
    fig.savefig(out, dpi=200); plt.close(fig)
    return out


# ------------------------------------------------------------------ verificações
def verificacoes():
    V = []

    def add(n, desc, esperado, obtido, ok, fonte):
        V.append((n, desc, esperado, obtido, ok, fonte))

    os_ = pd.read_parquet(PROC / "os_consolidadas_processadas.parquet")
    cob = os_[os_.ds_os_status == "COBRADAS"]
    eg = {r["variavel"]: r for r in D.get("estatisticas_gerais", [])}
    va = eg.get("Valor Aprovado por OS (R$)", {})
    add(1, "Nº de OS cobradas (recontagem no parquet × etapa 03)", br(va.get("n_observacoes", 0), 0), br(len(cob), 0),
        len(cob) == va.get("n_observacoes"), "os_consolidadas_processadas.parquet")
    add(2, "Mediana do valor aprovado por OS cobrada", rs(va.get("mediana", 0)), rs(float(cob.vl_aprovado_total.median())),
        abs(cob.vl_aprovado_total.median() - va.get("mediana", -1)) < 0.01, "idem")
    tot = float(cob.vl_aprovado_total.sum())
    add(3, "Soma do valor aprovado das OS cobradas × carga do Neo4j", rs(NC.get("source_counts", {}).get("approved_value_total_reais", 0)), rs(tot),
        abs(tot - NC.get("source_counts", {}).get("approved_value_total_reais", -1)) < 1, "relatorio_neo4j_grafo.json")
    try:
        import joblib
        from sklearn.metrics import roc_auc_score
        pm = pd.read_parquet(PROC / "painel_veiculo_mes_longitudinal.parquet")
        feats = ["custo_mes", "vl_pecas_mes", "vl_mo_mes", "qtd_os_mes", "qtd_corretivas_mes", "qtd_preventivas_mes", "km_max",
                 "idade_veiculo", "custo_lag1", "custo_lag2", "os_lag1", "corretivas_lag1", "km_diff", "patrimonio_valor_entrada", "patrimonio_valor_liquido"]
        te = pm[pm.ano_mes > "2024-12"]
        clf = joblib.load(DF / "resultados/modelos/classificador_histgradientboosting.joblib")
        roc = roc_auc_score(te.target_class_corretiva_t1, clf.predict_proba(te[feats].fillna(0.0))[:, 1])
        rj = next(r["roc_auc"] for r in M["metricas_classificacao"] if r["modelo"] == "HistGradientBoosting")
        add(4, "ROC-AUC do HistGB recalculado com o modelo salvo (teste 2025–2026)", br(rj, 4), br(roc, 4), abs(roc - rj) < 1e-3, "classificador_histgradientboosting.joblib")
    except Exception as ex:
        add(4, "ROC-AUC do HistGB recalculado com o modelo salvo", "—", f"erro: {ex}", False, "—")
    g = (AB["mae_M"] - AB["mae_MP"]) / AB["mae_M"]
    add(5, "Ganho da ablação = (MAE_M − MAE_MP) / MAE_M", pct(AB["ganho_mae_pct"], 4), pct(g, 4), abs(g - AB["ganho_mae_pct"]) < 1e-12, "relatorio_ablacao_h1.json")
    h1c = next(h for h in CE["matriz_hipoteses"] if h["hipotese"].startswith("Hipótese H1"))
    add(6, "H1 no certificado (etapa 09) igual à ablação (etapa 04b)", "NÃO SUSTENTADA" if not AB["h1_sustentada"] else "SUSTENTADA",
        h1c["decisao"], (h1c["decisao"] == "NÃO SUSTENTADA") == (not AB["h1_sustentada"]), "certificado_reprodutibilidade_cientifica.json")
    mr = AN["modelo_referencia"]
    add(7, "Isolation Forest: anomalias ÷ OS = contaminação 0,85%", "0,85%", pct(mr["total_anomalias_detectadas"] / len(os_), 3),
        abs(mr["total_anomalias_detectadas"] / len(os_) - mr["contaminacao_nu"]) < 0.0005, "relatorio_deteccao_anomalias.json")
    add(8, "Glosa nas anomalias = orçado − aprovado", rs(mr["vl_total_glosas_concentradas"]), rs(mr["vl_total_orcado"] - mr["vl_total_aprovado"]),
        abs(mr["vl_total_orcado"] - mr["vl_total_aprovado"] - mr["vl_total_glosas_concentradas"]) < 0.02, "idem")
    t3 = GN["testes"]["T3_reproducao_etapa06"]
    add(9, "Grafo: rede da etapa 06 = rede lida do Neo4j (nós, arestas, Q)",
        f"{t3['etapa06']['nos_oficinas']} / {t3['etapa06']['arestas']} / {br(t3['etapa06']['modularidade_louvain_q'], 4)}",
        f"{t3['neo4j']['nos_oficinas']} / {t3['neo4j']['arestas']} / {br(t3['neo4j']['modularidade_louvain_q'], 4)}", t3["aprovado"], "relatorio_analise_grafos_neo4j.json")
    a2 = GN["analises"]["A2_modelo_nulo"]
    add(10, "Modularidade observada acima de todas as 30 redes nulas", f"> {br(a2['Q_nulo_max'], 4)}", br(a2["Q_observado"], 4),
        a2["Q_observado"] > a2["Q_nulo_max"], "idem")
    h4c = next(h for h in CE["matriz_hipoteses"] if h["hipotese"].startswith("Hipótese H4"))
    okh4 = f"{X['spearman_rho_medio']:.4f}" in h4c["estatistica_teste"]
    add(11, "H4 no certificado usa o Spearman da etapa 07", br(X["spearman_rho_medio"], 4), h4c["estatistica_teste"], okh4, "relatorio_explicabilidade_xai.json")
    add(12, "XAI: decisão da etapa 07 igual à da etapa 09 (limiar 0,85)", str(X["hipotese_h4_sustentada"]),
        str(h4c["decisao"] == "SUSTENTADA"), X["hipotese_h4_sustentada"] == (h4c["decisao"] == "SUSTENTADA"), "07 × 09")
    ci = MI["confronto_inercial"]
    add(13, "MILP: economia = linha de base BL0 − custo MILP", rs(ci["economia_prescritiva_brl"]), rs(ci["custo_inercial_as_is_brl"] - MI["solucao_inteira_mip_brl"]),
        abs(ci["custo_inercial_as_is_brl"] - MI["solucao_inteira_mip_brl"] - ci["economia_prescritiva_brl"]) < 0.02, "relatorio_otimizacao_milp.json")
    src08 = (DF / "src/08_otimizacao_milp.py").read_text(encoding="utf-8")
    fixo = "custo_total_mip = 43837633.31" in src08 and "custo_bl0 = 53139780.57" in src08
    add(14, "MILP: custos vêm do solver (e não de constantes no script 08)", "calculados", "fixos no código" if fixo else "calculados", not fixo, "08_otimizacao_milp.py")
    src07 = (DF / "src/07_explicabilidade_xai.py").read_text(encoding="utf-8")
    add(15, "Figura local SHAP × LIME usa pesos LIME reais", "LIME real", "LIME real" if "lime_mock" not in src07 else "simulado", "lime_mock" not in src07, "07_explicabilidade_xai.py")
    if LP:
        s26 = sum(LP["previsao_mensal_2026"].values())
        add(16, "LOA 2026: total = soma das 12 previsões mensais", rs(LP["total_2026"]), rs(s26), abs(s26 - LP["total_2026"]) < 0.01, "resultado_experimento.json")
    pm2 = pd.read_parquet(PROC / "painel_veiculo_mes_longitudinal.parquet", columns=["patrimonio_valor_entrada"])
    med = float(pm2[pm2.patrimonio_valor_entrada > 0].patrimonio_valor_entrada.median())
    add(17, "Patrimônio no painel em reais (mediana > R$ 1.000; antes da correção era R$ 89)", "> R$ 1.000", rs(med), med > 1000, "painel_veiculo_mes_longitudinal.parquet")
    return V


# ------------------------------------------------------------------ fichas
def fichas():
    F = []
    eg = {r["variavel"]: r for r in D.get("estatisticas_gerais", [])}
    va = eg.get("Valor Aprovado por OS (R$)", {})
    mw = (D.get("comparacoes_mann_whitney") or [{}])[0]
    F.append(dict(sec="Etapa 03 – Estatística descritiva", arq=FIGS / "distribuicao_custos_log_boxplot.png",
        tit="Distribuição do valor aprovado por OS (escala logarítmica) e comparação corretiva × preventiva",
        mostra="À esquerda, o histograma do valor aprovado de cada OS cobrada, em escala logarítmica, com a curva de densidade. À direita, caixas (boxplot) do valor aprovado para OS corretivas e preventivas.",
        dados=f"<code>os_consolidadas_processadas.parquet</code>, só OS com situação COBRADAS ({br(va.get('n_observacoes', 0), 0)} OS). O histograma usa apenas valores maiores que zero.",
        calc=[f"Mediana do valor aprovado: {rs(va.get('mediana', 0))}; média: {rs(va.get('media', 0))}. A média é {br(va.get('media', 0) / max(va.get('mediana', 1), 1), 1)} vezes a mediana, sinal de cauda longa à direita.",
              f"Quartis: Q1 = {rs(va.get('q25', 0))}, Q3 = {rs(va.get('q75', 0))}; IQR = Q3 − Q1 = {rs(va.get('iqr', 0))}. Máximo: {rs(va.get('maximo', 0))}.",
              f"Assimetria = {br(va.get('assimetria_skewness', 0), 3)} e curtose = {br(va.get('curtose', 0), 3)} (uma distribuição normal tem 0 e 0).",
              f"Mann-Whitney corretiva × preventiva: medianas {rs(mw.get('mediana_1', 0))} (n = {br(mw.get('n1', 0), 0)}) e {rs(mw.get('mediana_2', 0))} (n = {br(mw.get('n2', 0), 0)}); U = {br(mw.get('u_statistic', 0), 1)}; p = {br(mw.get('p_value', 1), 4)}."],
        ler="Cada barra do histograma conta quantas OS caem numa faixa de valor; como o eixo é logarítmico, cada passo à direita multiplica o valor. A linha vermelha marca a mediana dos valores positivos. Nas caixas, a linha central é a mediana, a caixa vai de Q1 a Q3 e os pontos isolados são valores extremos.",
        fixos="Nenhum número exibido é digitado. Constantes de desenho: 40 classes no histograma.",
        ress="A mediana da legenda usa só valores positivos; a da tabela (JSON) inclui zeros, por isso podem diferir. Zeros não aparecem no eixo logarítmico. A diferença corretiva × preventiva é estatisticamente detectável, mas pequena em reais."))
    F.append(dict(sec="Etapa 03 – Estatística descritiva", arq=FIGS / "serie_temporal_mensal_despesas.png",
        tit="Série mensal do valor aprovado em manutenção",
        mostra="A soma mensal do valor aprovado das OS cobradas, em milhões de reais.",
        dados="Mesmas OS cobradas; agrupamento pelo mês da transação (<code>ano_mes</code>).",
        calc=["Para cada mês m: S(m) = Σ valor aprovado das OS cobradas com transação em m; o gráfico mostra S(m) ÷ 1.000.000.",
              f"A soma de todos os meses é igual ao total das OS cobradas, {rs(NC.get('source_counts', {}).get('approved_value_total_reais', 0))} (verificação 3)."],
        ler="Cada ponto é um mês. Quedas em janeiro e picos em dezembro seguem o calendário orçamentário. A queda depois de set/2025 não é real: a extração da SEA/SC termina nesse período.",
        fixos="O intervalo de anos no título é texto digitado, não calculado.",
        ress="Meses sem OS não são preenchidos com zero; a linha liga os meses vizinhos. Os últimos meses são incompletos (ver experimento LOA/PCA)."))
    cls = {r["modelo"]: r for r in M.get("metricas_classificacao", [])}
    reg = {r["modelo"]: r for r in M.get("metricas_regressao", [])}
    h = cls.get("HistGradientBoosting", {}); lg = cls.get("LogisticRegression", {})
    F.append(dict(sec="Etapa 04 – Modelos preditivos", arq=FIGS / "curvas_roc_pr_classificacao.png",
        tit="Curvas ROC e precisão–revocação dos classificadores de risco de manutenção corretiva",
        mostra="Para cinco classificadores, a curva ROC (taxa de verdadeiros positivos × falsos positivos) e a curva precisão–revocação, ao prever se um veículo terá manutenção corretiva no mês seguinte.",
        dados="Painel veículo-mês (<code>painel_veiculo_mes_longitudinal.parquet</code>). Treino até dez/2024, teste de jan/2025 em diante (sem embaralhar o tempo). 15 atributos de manutenção e patrimônio.",
        calc=[f"ROC-AUC = área sob a curva ROC = probabilidade de o modelo dar nota maior a um caso positivo do que a um negativo. HistGB: {br(h.get('roc_auc', 0), 4)} (IC95 {e(h.get('ci_95_roc_auc', ''))}); Regressão Logística: {br(lg.get('roc_auc', 0), 4)}.",
              f"Diferença: {br(h.get('roc_auc', 0), 4)} − {br(lg.get('roc_auc', 0), 4)} = {br(h.get('roc_auc', 0) - lg.get('roc_auc', 0), 4)}.",
              f"PR-AUC (área sob precisão–revocação) do HistGB: {br(h.get('pr_auc', 0), 4)}; F1 com limiar 0,5: {br(h.get('f1_score', 0), 4)}; Brier: {br(h.get('brier_score', 0), 4)}; erro de calibração (ECE): {br(h.get('ece', 0), 4)}.",
              "Linha de referência: uma curva sobre a diagonal (AUC = 0,5) equivale a sorteio."],
        ler="Quanto mais a curva ROC se aproxima do canto superior esquerdo, melhor. Na curva precisão–revocação, mais alto e mais à direita é melhor. Como cerca de 78% dos meses de teste têm corretiva, a precisão de base já é alta.",
        fixos="Nenhum número exibido é digitado; as AUC da legenda são calculadas.",
        ress="A classe positiva é majoritária (≈ 78%), o que favorece PR-AUC alta. A comparação de AUC na etapa 09 usa erro-padrão constante (0,0084), não o teste de DeLong exato."))
    pb = M.get("passing_bablok", {})
    F.append(dict(sec="Etapa 04 – Modelos preditivos", arq=FIGS / "dispersao_regressao_passing_bablok.png",
        tit="Custo real × custo previsto no mês seguinte, com reta de Passing-Bablok",
        mostra="Cada ponto é um veículo-mês do teste: no eixo x o custo real no mês seguinte, no eixo y o previsto pelo HistGB. A reta tracejada é a identidade (previsão perfeita) e a vermelha é a de Passing-Bablok.",
        dados="Conjunto de teste do painel (2025–2026); 1.500 pontos sorteados para o gráfico (semente 42).",
        calc=[f"MAE (erro absoluto médio) do HistGB: {rs(reg.get('HistGradientBoosting', {}).get('mae_reais', 0))}; da previsão ingênua pela mediana do treino: {rs(reg.get('Baseline Mediana', {}).get('mae_reais', 0))}.",
              f"Comparação: ({rs(reg.get('Baseline Mediana', {}).get('mae_reais', 0))} − {rs(reg.get('HistGradientBoosting', {}).get('mae_reais', 0))}) ÷ {rs(reg.get('Baseline Mediana', {}).get('mae_reais', 0))} = {br((reg.get('Baseline Mediana', {}).get('mae_reais', 1) - reg.get('HistGradientBoosting', {}).get('mae_reais', 0)) / reg.get('Baseline Mediana', {}).get('mae_reais', 1) * 100)}%. Negativo significa que o modelo erra mais que a mediana.",
              f"RMSE: HistGB {rs(reg.get('HistGradientBoosting', {}).get('rmse_reais', 0))} × mediana {rs(reg.get('Baseline Mediana', {}).get('rmse_reais', 0))}; R² do HistGB = {br(reg.get('HistGradientBoosting', {}).get('r2_score', 0), 4)}.",
              f"Passing-Bablok: inclinação β = mediana das inclinações entre pares de pontos (2.000 pontos sorteados, semente 42) = {br(pb.get('inclinacao_beta', 0), 4)}; intercepto α = mediana(y − βx) = {rs(pb.get('intercepto_alpha', 0))}."],
        ler="Se o modelo fosse perfeito, os pontos ficariam sobre a diagonal. Uma reta de Passing-Bablok mais deitada que a diagonal (β < 1) indica que o modelo subestima custos altos e superestima custos baixos.",
        fixos="Nenhum número exibido é digitado.",
        ress="O HistGB erra mais que a mediana em MAE, mas menos em RMSE: acerta melhor os casos extremos e pior os típicos. Corrigido nesta versão: as subamostras não tinham semente fixa e mudavam a cada execução."))
    ps = AB.get("estresse_sementes", {}).get("por_semente", [])
    F.append(dict(sec="Etapa 04b – Ablação da hipótese H1", arq=FIGS / "ablacao_h1_m_vs_mp.png",
        tit="Ablação: manutenção (M) × manutenção + patrimônio (M+P)",
        mostra="À esquerda, o MAE do mesmo modelo treinado sem e com os dois atributos de patrimônio. À direita, o ganho em cinco sementes, o intervalo de confiança e a meta de 15%.",
        dados=f"Painel veículo-mês; {br(AB.get('n_treino', 0), 0)} linhas de treino (até dez/2024) e {br(AB.get('n_teste', 0), 0)} de teste. Patrimônio: valor de entrada (presente em {pct(AB.get('diagnostico_patrimonio', {}).get('pct_nao_zero_entrada', 0), 1)} das linhas; mediana {rs(AB.get('diagnostico_patrimonio', {}).get('mediana_entrada_nao_zero', 0))}) e valor líquido.",
        calc=[f"Ganho = (MAE_M − MAE_MP) ÷ MAE_M = ({rs(AB['mae_M'])} − {rs(AB['mae_MP'])}) ÷ {rs(AB['mae_M'])} = {rs(AB['delta_mae_reais'])} ÷ {rs(AB['mae_M'])} = {pct(AB['ganho_mae_pct'])}.",
              f"IC 95%: 2.000 reamostragens pareadas dos erros absolutos do teste; percentis 2,5 e 97,5 do ganho = {pct(AB['ic95_ganho_bootstrap_pareado'][0])} a {pct(AB['ic95_ganho_bootstrap_pareado'][1])}. O intervalo inclui zero.",
              f"Wilcoxon pareado nos erros absolutos: p = {AB['wilcoxon_pareado']['p_valor']:.2e}. Com {br(AB.get('n_teste', 0), 0)} pares, diferenças pequenas já dão p baixo; o tamanho do efeito é o que importa.",
              "Estresse por semente: " + "; ".join(f"{x['semente']}: {pct(x['ganho_mae_pct'])}" for x in ps) + ".",
              f"Classificação (semente 42): ROC-AUC M = {br(AB['classificacao_semente42']['roc_auc_M'], 4)}; M+P = {br(AB['classificacao_semente42']['roc_auc_MP'], 4)}.",
              f"Decisão pelo critério do código (ganho ≥ {pct(AB['meta_h1'], 0)}): {'sustentada' if AB['h1_sustentada'] else 'não sustentada'}."],
        ler="As duas barras quase iguais mostram que o patrimônio muda pouco o erro. No painel da direita, todos os pontos ficam muito abaixo da linha vermelha da meta.",
        fixos="Nenhum; figura nova gerada por este relatório a partir de <code>relatorio_ablacao_h1.json</code>.",
        ress="Abastecimento não foi testado: a base de abastecimentos cobre jan/2019 a fev/2022 e não se sobrepõe ao período de teste. Atenção à definição de H1 (ver seção 2): no anteprojeto, H1 pede melhora em pelo menos uma métrica principal, sem limiar de 15%; a ROC-AUC sobe com M+P."))
    est = AN.get("estabilidade_sementes", [])
    F.append(dict(sec="Etapa 05 – Detecção de anomalias", arq=FIGS / "estabilidade_jaccard_contaminacao.png",
        tit="Estabilidade do Isolation Forest entre sementes, por taxa de contaminação",
        mostra="Para cada taxa de contaminação (fração de OS que o algoritmo marca como anômalas), a semelhança média entre os conjuntos de anomalias obtidos com três sementes diferentes.",
        dados="Todas as OS (todas as situações); 8 atributos numéricos padronizados; Isolation Forest com 100 árvores; sementes 42, 123 e 999.",
        calc=["Jaccard entre dois conjuntos A e B = |A ∩ B| ÷ |A ∪ B| (1 = idênticos, 0 = sem nada em comum). Para cada contaminação, média dos três pares de sementes."]
             + [f"ν = {br(r['contaminacao_pct'], 2)}%: {br(r['anomalias_detectadas'], 0)} anomalias, Jaccard médio {br(r['jaccard_medio_sementes'], 4)} ({'≥' if r['jaccard_medio_sementes'] >= .8 else '<'} 0,80)." for r in est],
        ler="Quanto mais alto o ponto, mais o resultado se repete quando se troca a semente. A linha cinza em 0,80 é o limiar de estabilidade adotado.",
        fixos="O limiar 0,80, a grade de contaminações e as sementes são constantes do código.",
        ress="Só três sementes e os mesmos dados: mede a aleatoriedade do algoritmo, não a robustez a dados novos. O limiar 0,80 é uma convenção."))
    cf = AN.get("concordancia_fiscal", {})
    F.append(dict(sec="Etapa 05 – Detecção de anomalias", arq=FIGS / "distribuicao_scores_anomalia_glosas.png",
        tit="Distribuição dos escores de anomalia: OS com e sem glosa",
        mostra="A densidade dos escores do Isolation Forest para OS sem glosa (verde) e com glosa (vermelho). Escore menor = mais atípico. A linha tracejada é o corte do modelo de referência (ν = 0,85%).",
        dados="Todas as OS; modelo de referência com ν = 0,0085 e semente 42. Glosa = orçado − aprovado > R$ 0,05.",
        calc=[f"Anomalias: {br(mr['total_anomalias_detectadas'], 0)} OS = {br(mr['pct_universo_os'], 2)}% do total." if (mr := AN.get('modelo_referencia')) else "",
              f"Nessas OS: orçado {rs(mr['vl_total_orcado'])}, aprovado {rs(mr['vl_total_aprovado'])}, glosa = orçado − aprovado = {rs(mr['vl_total_glosas_concentradas'])} ({br(mr['taxa_retencao_glosas_pct'], 2)}% do orçado).",
              f"Teste t de Welch (escores com glosa × sem glosa): t = {br(cf.get('t_statistic', 0), 3)}, p = {cf.get('t_p_value', 1):.2e}. O t positivo indica escores <b>maiores</b> (menos atípicos) nas OS com glosa.",
              f"Mann-Whitney unilateral (glosadas com escores menores?): p = {br(cf.get('mann_whitney_p', 1), 3)}. Não há evidência de que OS glosadas sejam mais atípicas."],
        ler="Se o detector capturasse o que a fiscalização glosa, a curva vermelha estaria deslocada para a esquerda. Ela não está.",
        fixos="O rótulo “0,85%” e ν = 0,0085 são constantes do código.",
        ress="Este resultado contradiz leituras de que as anomalias “concordam” com as glosas: os dados mostram o contrário. O modelo é ajustado em todos os dados (não há conjunto de teste)."))
    tr = GR.get("topologia_rede", {})
    F.append(dict(sec="Etapa 06 – Grafos", arq=FIGS / "distribuicao_graus_lei_potencia.png",
        tit="Distribuição dos graus das oficinas na rede de compartilhamento de veículos",
        mostra="Quantas oficinas têm cada número de ligações (grau) na rede em que duas oficinas se ligam quando atendem pelo menos dois veículos em comum.",
        dados="OS cobradas; rede bipartida veículo–oficina projetada em oficina–oficina; arestas com peso ≥ 2.",
        calc=[f"Nós: {br(tr.get('nos_oficinas', 0), 0)}; arestas: {br(tr.get('arestas', 0), 0)}.",
              f"Grau médio = 2 × arestas ÷ nós = 2 × {br(tr.get('arestas', 0), 0)} ÷ {br(tr.get('nos_oficinas', 0), 0)} = {br(2 * tr.get('arestas', 0) / max(tr.get('nos_oficinas', 1), 1), 1)}.",
              f"Densidade = arestas ÷ [n(n−1)/2] = {br(tr.get('densidade', 0), 5)}; agrupamento médio ponderado = {br(tr.get('coeficiente_clustering', 0), 4)}."],
        ler="A maioria das oficinas tem poucas ligações e poucas têm muitas (cauda longa).",
        fixos="Filtro de peso ≥ 2 e 30 classes.",
        ress="O nome do arquivo cita “lei de potência”, mas nenhum ajuste de lei de potência é feito; a figura não sustenta afirmação de rede livre de escala."))
    a1 = GN.get("analises", {}).get("A1_estabilidade_louvain", {}); a2 = GN.get("analises", {}).get("A2_modelo_nulo", {})
    F.append(dict(sec="Etapa 06 – Grafos", arq=FIGS / "rede_oficinas_comunidades_louvain.png",
        tit="Rede de oficinas colorida pelas comunidades de Louvain",
        mostra="O maior componente conectado da rede de oficinas, com cores por comunidade detectada pelo algoritmo de Louvain e tamanho proporcional ao grau.",
        dados="Mesma rede oficina–oficina; Louvain com pesos, semente 42.",
        calc=["Modularidade Q = (1/2m) Σ_ij [A_ij − k_i k_j / 2m] δ(c_i, c_j): fração de arestas dentro das comunidades menos a esperada ao acaso.",
              f"Q = {br(tr.get('modularidade_louvain_q', 0), 4)}; {tr.get('total_comunidades', '—')} comunidades; maiores com {', '.join(str(x) for x in tr.get('maiores_comunidades_tamanho', []))} oficinas.",
              f"Validação (análise do grafo no Neo4j): em 30 redes nulas com os mesmos graus, Q = {br(a2.get('Q_nulo_media', 0), 4)} ± {br(a2.get('Q_nulo_dp', 0), 4)}; z = ({br(a2.get('Q_observado', 0), 4)} − {br(a2.get('Q_nulo_media', 0), 4)}) ÷ {br(a2.get('Q_nulo_dp', 0), 4)} = {br(a2.get('z', 0), 1)}.",
              f"Estabilidade em 30 sementes: {a1.get('comunidades_min', '—')}–{a1.get('comunidades_max', '—')} comunidades; ARI médio {br(a1.get('ARI_vs_seed42_media', 0), 3)}."],
        ler="Grupos de mesma cor ligados entre si são oficinas que tendem a atender os mesmos veículos.",
        fixos="Semente 42 e parâmetros de desenho; Q no título é calculado.",
        ress="Com 18 comunidades e 10 cores, cores se repetem. O desenho mostra só o maior componente, mas Q é da rede inteira. Comunidade densa não é indício de conluio."))
    for nome, leg, ex in (("grafos_modelo_nulo_e_concentracao.png", "Modularidade observada × redes nulas e concentração do gasto", "A2_A3"),
                          ("grafos_centralidade_vs_glosa.png", "Centralidade da oficina × percentual de OS com glosa", "A4")):
        an = GN.get("analises", {})
        if ex == "A2_A3":
            a3 = an.get("A3_concentracao", {})
            calc = [f"Histograma de Q em 30 redes nulas (troca dupla de arestas, 5 trocas por aresta, pesos permutados); linha verde = Q observado {br(a2.get('Q_observado', 0), 4)}.",
                    f"Curva de concentração: oficinas ordenadas por gasto aprovado; os 10% maiores somam {pct(a3.get('participacao_top10pct_oficinas', 0), 1)} do gasto; Gini = {br(a3.get('gini_gasto', 0), 3)}; HHI = Σ (participação × 100)² = {br(a3.get('hhi', 0), 1)}."]
            ler = "À esquerda, quanto mais longe a linha verde do histograma, menos provável que a estrutura seja acaso. À direita, quanto mais a curva se afasta da diagonal, mais concentrado o gasto."
        else:
            sp = an.get("A4_centralidade_vs_auditoria", {}).get("spearman", {})
            calc = [f"Spearman entre grau ponderado e taxa de glosa: ρ = {br(sp.get('grau_ponderado~taxa_glosa', {}).get('rho', 0), 3)} (p = {br(sp.get('grau_ponderado~taxa_glosa', {}).get('p', 1), 3)}; n = {sp.get('grau_ponderado~taxa_glosa', {}).get('n', '—')} oficinas com ≥ 30 OS).",
                    f"Mesmo grau × taxa de anomalia: ρ = {br(sp.get('grau_ponderado~taxa_anomalia', {}).get('rho', 0), 3)} (p = {sp.get('grau_ponderado~taxa_anomalia', {}).get('p', 1):.2g})."]
            ler = "Uma nuvem sem inclinação indica que oficinas centrais não têm mais glosas que as periféricas."
        F.append(dict(sec="Grafo persistido no Neo4j", arq=FIGS / nome, tit=leg,
            mostra="Figura da análise do grafo lido do Neo4j (<code>scripts/analise_grafos_frotas.py</code>).",
            dados=f"{br(NC.get('verified_neo4j_counts', {}).get('vehicle_count', 0), 0)} veículos, {br(NC.get('verified_neo4j_counts', {}).get('workshop_count', 0), 0)} oficinas, identificadores pseudonimizados (HMAC-SHA-256).",
            calc=calc, ler=ler, fixos="Nenhum número exibido é digitado.", ress="Associação não implica causalidade; oficinas maiores recebem mais OS e mais fiscalização."))
    F.append(dict(sec="Etapa 07 – Explicabilidade (XAI)", arq=FIGS / "figura_xai_shap_beeswarm.png",
        tit="Importância global dos atributos pelo SHAP (gráfico de enxame)",
        mostra="Para cada atributo, um ponto por instância: a posição horizontal é a contribuição SHAP para o risco previsto (em log-odds) e a cor é o valor do atributo (azul = baixo, vermelho = alto).",
        dados=f"Classificador HistGB salvo na etapa 04; 1.500 instâncias de teste sorteadas (semente 42) — gravado {X.get('amostra_avaliada_shap', '—')}.",
        calc=["Valor SHAP do atributo j na instância x: φ_j = média, sobre todas as ordens de entrada dos atributos, do quanto j altera a previsão (valor de Shapley). Para árvores, o TreeExplainer calcula exatamente."]
             + [f"{r['feature_label']}: média |φ| = {br(r['mean_abs_shap'], 4)} ({br(r['importancia_relativa_pct'], 1)}% do total)" for r in X.get("top_features_shap", [])[:5]],
        ler="Atributos no topo influenciam mais. Pontos vermelhos à direita indicam que valores altos aumentam o risco.",
        fixos="Nenhum número exibido é digitado.",
        ress="Importância preditiva não é efeito causal. A ordem depende do modelo e dos dados de teste."))
    ic = X.get("instancia_critica_comparativo", {})
    F.append(dict(sec="Etapa 07 – Explicabilidade (XAI)", arq=FIGS / "figura_xai_comparativo_local_shap_lime.png",
        tit="Explicação local de uma instância crítica: SHAP × LIME",
        mostra="Para o veículo-mês de maior risco previsto, as seis maiores contribuições SHAP (esquerda) e os pesos LIME dos mesmos atributos (direita).",
        dados=f"Instância de teste com P(falha) = {pct(ic.get('probabilidade_falha', 0), 1)}.",
        calc=["LIME: gera vizinhos perturbados da instância, obtém as previsões do modelo e ajusta uma regressão linear local ponderada pela proximidade; os coeficientes são os pesos."]
             + [f"{a}: SHAP {br(s, 4)} | LIME {br(l, 4)}" for a, s, l in zip(ic.get("atributos", []), ic.get("shap", []), ic.get("lime", []))]
             + [f"Concordância média nas 25 instâncias de maior risco: Spearman {br(X.get('spearman_rho_medio', 0), 4)}; Jaccard das 5 maiores {pct(X.get('jaccard_top5_medio', 0), 1)}. Critério de H4 no código: ambos > 0,85 → {'sustentada' if X.get('hipotese_h4_sustentada') else 'não sustentada'}."],
        ler="Se os métodos concordassem, as barras dos dois lados teriam tamanhos e sinais parecidos. Aqui divergem em ordem e magnitude.",
        fixos="Nenhum após a correção.",
        ress="Corrigido nesta versão: o painel LIME usava os valores SHAP multiplicados por um fator aleatório (<code>lime_mock</code>), o que fazia os dois lados parecerem concordar. Agora mostra o LIME real."))
    h4img = ROOT / "SIC/img/h4_shap_lime_concordancia.png"
    if h4img.exists():
        F.append(dict(sec="Etapa 07 – Explicabilidade (XAI)", arq=h4img, tit="Concordância SHAP × LIME frente à meta de H4 (figura da apresentação)",
            mostra="Jaccard e Spearman médios comparados com a meta de 0,85.", dados="<code>relatorio_explicabilidade_xai.json</code>; gerada por <code>scripts/gerar_figura_h4_xai.py</code>.",
            calc=[f"Jaccard = {br(X.get('jaccard_top5_medio', 0), 4)}; Spearman = {br(X.get('spearman_rho_medio', 0), 4)}; meta 0,85."],
            ler="Barras abaixo da linha da meta indicam H4 não sustentada.", fixos="Meta de 0,85.", ress="Regenerada com os números desta versão."))
    ci = MI.get("confronto_inercial", {})
    F.append(dict(sec="Etapa 08 – Otimização prescritiva (MILP)", arq=FIGS / "figura_milp_trajetoria_financeira.png",
        tit="Custo esperado por mês das três políticas no cenário S0",
        mostra="Custo mensal esperado (manutenções feitas mais risco das não feitas) da linha de base BL0, da heurística gulosa e do MILP, nos 36 meses.",
        dados="Todos os pontos são calculados pelo script 08 a partir da instância S0 e das soluções do solver.",
        calc=["Instância do MILP: 2.000 veículos sorteados (semente 42) × 36 meses. Os custos por veículo e mês são gerados por fórmulas com fatores aleatórios uniformes (0,94 a 1,06) a partir do custo médio real de cada veículo; as manutenções obrigatórias seguem um ciclo de 12 meses.",
              "Custo do mês = Σ (decisão × custo de executar) + Σ ((1 − decisão) × custo de risco), para cada política.",
              f"Totais: MILP {rs(MI.get('solucao_inteira_mip_brl', 0))}; relaxação LP {rs(MI.get('relaxacao_linear_lp_brl', 0))}; BL0 (só obrigatórias) {rs(ci.get('custo_inercial_as_is_brl', 0))}; heurística gulosa {rs(ci.get('custo_heuristica_gulosa_brl', 0))}.",
              f"Economia = BL0 − MILP = {rs(ci.get('custo_inercial_as_is_brl', 0))} − {rs(MI.get('solucao_inteira_mip_brl', 0))} = {rs(ci.get('economia_prescritiva_brl', 0))} ({br(ci.get('economia_pct', 0))}%); MILP contra a heurística: {rs(ci.get('economia_vs_heuristica_brl', 0))}."],
        ler="A linha do MILP abaixo das outras indica menor custo; a heurística quase coincide com o MILP.",
        fixos="Parâmetros da instância semissintética (fatores 0,94–1,06, ciclo de 12 meses, semente 42).",
        ress="A instância é semissintética: a economia de H3 vale para esse cenário e não para a frota real. Quase toda a economia é obtida também pela heurística gulosa."))
    F.append(dict(sec="Etapa 09 – Validação das hipóteses", arq=FIGS / "figura_validacao_hipoteses_consolidada.png",
        tit="Quadro-resumo das hipóteses",
        mostra="Uma barra por premissa/hipótese, colorida pela decisão (verde = sustentada, âmbar = parcial, vermelho = não sustentada), com o número decisivo ao lado.",
        dados="JSONs das etapas 04, 04b, 07 e 08 (lidos pela etapa 09 após a correção).",
        calc=[f"{e(h['hipotese'])}: {e(h['estatistica_teste'])} → <b>{e(h['decisao'].split('.')[0])}</b>" for h in CE.get("matriz_hipoteses", [])],
        ler="A cor resume a decisão; o texto mostra o número que a determina.",
        fixos="Os limiares de decisão do código: P1 (p < 0,05 e |assimetria| > 1), H1 (ganho ≥ 15%), H2 (ΔROC > 0,05), H3 (economia > 10% e gap < 1%), H4 (Spearman e Jaccard > 0,85).",
        ress="Corrigido nesta versão: a etapa 09 procurava a chave errada no JSON da etapa 04 e usava ROC digitado para a regressão logística (0,7366, contra 0,8292 real); os textos de H1 e H2 eram digitados. Com os valores reais, H2 passou de “parcialmente sustentada” para “não sustentada” pelo critério do código."))
    if LP:
        esc = LP["modelo_escolhido"]; inc = LP["incerteza_2026"].get(esc, {})
        bt = LP["avaliacao_retrospectiva"]
        F.append(dict(sec="Experimento LOA/PCA 2026", arq=LOA / "fig_avaliacao_retrospectiva.png",
            tit="Teste retrospectivo dos modelos de previsão",
            mostra="Previsão mensal de cada modelo contra o realizado em dois testes: treino até dez/2023 prevendo 2024, e treino até dez/2024 prevendo jan–set/2025.",
            dados="Valor aprovado mensal das OS cobradas, jan/2022 a set/2025.",
            calc=["Erro no total = (Σ previsto − Σ realizado) ÷ Σ realizado."]
                 + [f"{e(b)} – {e(k)}: previsto {rs(v['previsto'])}, realizado {rs(v['realizado'])}, erro {pct(v['erro_total_pct'], 1)}" for b, d in bt.items() for k, v in d.items()]
                 + [f"Escolhido: {e(esc)} (menor erro absoluto médio: {pct(LP['erro_medio_abs_total'][esc], 1)})."],
            ler="A linha preta é o realizado; quanto mais próxima a linha do modelo, melhor.", fixos="Nenhum número exibido é digitado.",
            ress="Dois testes são poucos para estimar o erro com precisão."))
        F.append(dict(sec="Experimento LOA/PCA 2026", arq=LOA / "fig_serie_previsao.png",
            tit="Série observada, meses presumidos e previsão para 2026",
            mostra="Valor mensal observado até o corte, meses presumidos (out–dez/2025) e a previsão de 2026 pelo modelo escolhido.",
            dados=f"Corte da série: {e(LP['corte'])} (último mês com pelo menos 50% das OS do mesmo mês do ano anterior).",
            calc=[f"2025 = observado até {e(LP['corte'])} + presumido = {rs(LP['ano_2025_observado_mais_presumido'])}.",
                  f"2026 = Σ das 12 previsões mensais = {rs(LP['total_2026'])}; intervalo de 80% por 2.000 trajetórias simuladas: {rs(inc.get('10', 0))} a {rs(inc.get('90', 0))}."],
            ler="Pontos laranja são estimativas, não dados.", fixos="Nenhum número exibido é digitado.",
            ress="A projeção não inclui correção de preços nem mudanças de frota ou contrato."))
    return F


CSS = """
@page { size: A4; margin: 1.8cm 1.7cm; @bottom-right { content: counter(page) " / " counter(pages); font: 8.5pt Arial; color:#555; }
        @bottom-left { content: "Figuras e memória de cálculo · PPGCAP/UDESC"; font: 8.5pt Arial; color:#555; } }
body { font-family: Arial, sans-serif; font-size: 9.8pt; line-height: 1.42; color:#1d1d1d; }
h1 { color:#00693e; font-size: 19pt; margin: 0 0 4pt; } .sub { color:#444; margin-bottom: 10pt; }
h2 { color:#00693e; font-size: 13.5pt; border-bottom: 1.5pt solid #00693e; padding-bottom: 2pt; margin: 16pt 0 6pt; }
h3 { font-size: 11pt; margin: 0 0 4pt; color:#1b3a6e; }
.fig { page-break-before: always; } .fig img { width: 100%; max-height: 10.5cm; object-fit: contain; border:.5pt solid #ddd; margin: 4pt 0; }
.sec { font-size: 8.5pt; color:#00693e; text-transform: uppercase; letter-spacing: .5pt; }
.bl { margin: 5pt 0; } .bl b.t { display:block; color:#00693e; font-size: 9.5pt; }
.calc { background:#f3f8f5; border-left: 3pt solid #00693e; padding: 5pt 8pt; } .calc li { margin: 2pt 0; }
.fixo { background:#f4f6fb; border-left: 3pt solid #1b3a6e; padding: 4pt 8pt; }
.ress { background:#fff7e0; border-left: 3pt solid #d99a00; padding: 4pt 8pt; }
table { width:100%; border-collapse: collapse; margin: 4pt 0 10pt; font-size: 8.3pt; } th { background:#00693e; color:#fff; text-align:left; padding: 3pt 4pt; }
td { border-bottom: .5pt solid #c9d6cf; padding: 2.4pt 4pt; vertical-align: top; } tr:nth-child(even) td { background:#f3f8f5; }
.ok { color:#00693e; font-weight:bold; } .nok { color:#b04a3a; font-weight:bold; }
.ver td:nth-child(2) { width: 34%; } .ver td:nth-child(3), .ver td:nth-child(4) { width: 15%; } .ver td:nth-child(6) { width: 18%; word-break: break-all; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.2pt; } ul { margin: 2pt 0 2pt 14pt; padding: 0; }
"""


def main():
    figura_ablacao()
    V = verificacoes()
    F = fichas()
    nok = [v for v in V if not v[4]]
    H = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>",
         "<h1>Figuras dos testes e memória de cálculo</h1>",
         f"<p class='sub'>Analítica prescritiva para a frota pública de Santa Catarina · Eduardo Lopes Jonker · PPGCAP/UDESC · "
         f"gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} por <code>scripts/gerar_relatorio_figuras_memoria_calculo.py</code></p>",
         "<h2>1. Como usar este relatório</h2>",
         f"<p>Para cada uma das {len(F)} figuras: o que mostra, dados e filtros, memória de cálculo com os números desta execução "
         "(lidos dos arquivos de resultado, sem digitação), como ler, valores fixos no código e ressalvas. Na seção 4, "
         f"{len(V)} verificações recalculam números a partir dos dados e comparam com os resultados gravados: "
         f"{len(V) - len(nok)} confirmadas e {len(nok)} com divergência.</p>",
         "<h2>2. Correções feitas nesta versão e efeito nos resultados</h2><ul>",
         "<li><b>Patrimônio lido errado.</b> A etapa 02 interpretava “R$ 48,010.00” como R$ 48,01: todos os valores patrimoniais do painel estavam cerca de mil vezes menores. "
         f"Corrigido; a mediana do valor de entrada passou a {rs(AB.get('diagnostico_patrimonio', {}).get('mediana_entrada_nao_zero', 0))}.</li>",
         f"<li><b>Ablação H1 sem código.</b> O “+0,41%” estava digitado. A nova etapa 04b mede o ganho com patrimônio real: {pct(AB.get('ganho_mae_pct', 0))} "
         f"(IC 95% {pct(AB.get('ic95_ganho_bootstrap_pareado', [0, 0])[0])} a {pct(AB.get('ic95_ganho_bootstrap_pareado', [0, 0])[1])}). A conclusão não muda.</li>",
         "<li><b>Painel LIME simulado.</b> A figura local SHAP × LIME desenhava SHAP vezes um fator aleatório. Agora usa o LIME real. O JSON da etapa 07 passou a usar o mesmo limiar de 0,85 da etapa 09.</li>",
         "<li><b>Etapa 09 lendo chave errada.</b> O ROC da regressão logística vinha de um valor digitado (0,7366). Com o real (0,8292), H2 deixou de ser “parcialmente sustentada” pelo critério do código.</li>",
         "<li><b>Subamostras sem semente</b> no Passing-Bablok e no gráfico de dispersão: agora usam semente 42.</li></ul>",
         "<h3>Critérios do anteprojeto × critérios do código</h3>",
         "<table><tr><th>Hipótese</th><th>Anteprojeto</th><th>Código (etapa 09)</th><th>Decisão pelo código</th></tr>"]
    dec = {h["hipotese"].split(":")[0].replace("Hipótese ", ""): h["decisao"].split(".")[0] for h in CE.get("matriz_hipoteses", [])}
    for hip, ante, cod in (("H1", "M+P melhora pelo menos uma métrica principal fora do tempo de treino; reportar magnitude e incerteza", "ganho no MAE ≥ 15%"),
                           ("H2", "ensembles competitivos frente a SVR-RBF; nenhum vencedor pressuposto", "ΔROC > 0,05 sobre regressão logística e MAE menor que a mediana"),
                           ("H3", "política reduz o custo esperado frente à prática reconstruída e a heurísticas (contrafactual simulado)", "economia > 10% e gap < 1%"),
                           ("H4", "explicações com fidelidade e estabilidade suficientes para revisão por especialistas", "Spearman e Jaccard > 0,85")):
        H.append(f"<tr><td>{hip}</td><td>{e(ante)}</td><td>{e(cod)}</td><td>{e(dec.get(hip, '—'))}</td></tr>")
    H.append("</table><p class='ress'>Os limiares numéricos do código não estão no anteprojeto. Pelo texto do anteprojeto, H1 poderia ser considerada sustentada "
             f"na classificação (ROC-AUC {br(AB.get('classificacao_semente42', {}).get('roc_auc_M', 0), 4)} → {br(AB.get('classificacao_semente42', {}).get('roc_auc_MP', 0), 4)}), "
             "e H2 não foi testada contra SVR-RBF. A escolha do critério deve ser decidida com os orientadores e registrada antes da defesa.</p>")
    H.append("<h2>3. Sumário das figuras</h2><table><tr><th>#</th><th>Seção</th><th>Figura</th><th>Arquivo</th></tr>")
    for i, f in enumerate(F, 1):
        H.append(f"<tr><td>{i}</td><td>{e(f['sec'])}</td><td>{e(f['tit'])}</td><td><code>{e(f['arq'].name)}</code></td></tr>")
    H.append("</table>")
    for i, f in enumerate(F, 1):
        img = f"<img src='{f['arq'].as_uri()}'>" if f["arq"].exists() else "<p class='nok'>Arquivo da figura não encontrado.</p>"
        H.append(f"<div class='fig'><div class='sec'>{e(f['sec'])}</div><h3>Figura {i}. {e(f['tit'])}</h3>{img}"
                 f"<div class='bl'><b class='t'>O que mostra</b>{f['mostra']}</div>"
                 f"<div class='bl'><b class='t'>Dados e filtros</b>{f['dados']}</div>"
                 f"<div class='bl calc'><b class='t'>Memória de cálculo</b><ul>" + "".join(f"<li>{c}</li>" for c in f["calc"] if c) + "</ul></div>"
                 f"<div class='bl'><b class='t'>Como ler</b>{f['ler']}</div>"
                 f"<div class='bl fixo'><b class='t'>Valores fixos no código</b>{f['fixos']}</div>"
                 f"<div class='bl ress'><b class='t'>Ressalvas</b>{f['ress']}</div></div>")
    H.append("<h2 style='page-break-before:always'>4. Verificações de confirmação</h2>"
             "<p>Cada linha recalcula um número a partir dos dados ou confere a coerência entre etapas. “Divergente” indica um problema a resolver, não um erro do relatório.</p>"
             "<table class='ver'><tr><th>#</th><th>Verificação</th><th>Esperado</th><th>Obtido</th><th>Resultado</th><th>Fonte</th></tr>")
    for n, d, esp, obt, ok, fonte in V:
        H.append(f"<tr><td>{n}</td><td>{e(d)}</td><td>{e(str(esp))}</td><td>{e(str(obt))[:160]}</td>"
                 f"<td class='{'ok' if ok else 'nok'}'>{'confirmada' if ok else 'divergente'}</td><td><code>{e(fonte)}</code></td></tr>")
    H.append("</table></body></html>")
    weasyprint.HTML(string="\n".join(H), base_url=str(ROOT)).write_pdf(SAIDA)
    (ROOT / "relatorios_pdf").mkdir(exist_ok=True)
    shutil.copy2(SAIDA, ROOT / "relatorios_pdf" / SAIDA.name)
    print(f"OK: {SAIDA.name} | figuras: {len(F)} | verificações: {len(V) - len(nok)}/{len(V)} confirmadas")
    for v in nok:
        print("   divergente:", v[0], v[1], "| esperado", v[2], "| obtido", str(v[3])[:80])


if __name__ == "__main__":
    main()

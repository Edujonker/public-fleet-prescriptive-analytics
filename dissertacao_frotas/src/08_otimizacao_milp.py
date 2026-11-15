#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 08: Otimização Prescritiva Estocástica MILP e Relaxação Linear Contínua
Repositório: Public Fleet Prescriptive Analytics (GitHub: https://github.com/Edujonker/public-fleet-prescriptive-analytics)
Dissertação de Mestrado - PPGCAP / CCT / UDESC
Autor: Eduardo Lopes Jonker (Eduardo Henrique dos Santos)
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Diretriz: MILP Verificável (Função objetivo, restrições, parâmetros,
solucionador HiGHS, status, gap de otimalidade e comparação com políticas viáveis).
Formula e resolve o modelo de Programação Linear Inteira Mista (MILP) com 2.000 veículos
ao longo de 36 períodos mensais (Triênio 2027-2029), confrontando a solução inteira exata com
a Relaxação Linear (LP Relaxation) para auditoria poliedral e cálculo de preços-sombra.
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import milp, linprog, LinearConstraint, Bounds
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def executar_otimizacao_milp():
    inicio_exec = datetime.now()
    print("=" * 85)
    print("INICIANDO SCRIPT 08: OTIMIZAÇÃO PRESCRITIVA MILP E ANÁLISE POLIEDRAL")
    print(f"Timestamp: {inicio_exec.isoformat()}")
    print("=" * 85)

    base_dir = Path(__file__).resolve().parent.parent
    dados_proc = base_dir / "data" / "processed"
    if not dados_proc.exists():
        dados_proc = base_dir.parent / "dissertacao_frotas" / "dados" / "processados"
    res_metricas = base_dir / "results" / "metrics"
    res_figuras = base_dir / "results" / "figures"
    res_logs = base_dir / "results" / "solver_logs"

    res_metricas.mkdir(parents=True, exist_ok=True)
    res_figuras.mkdir(parents=True, exist_ok=True)
    res_logs.mkdir(parents=True, exist_ok=True)

    # 1. Carregar Dados de Frota e Instância Canônica do Cenário S0
    print("\n[1/5] Carregando painel de veículos e instanciando parâmetros do MILP Cenário S0...")
    caminho_os = dados_proc / "os_consolidadas_processadas.parquet"
    if not caminho_os.exists():
        print(f"[ERRO] Arquivo não encontrado: {caminho_os}.")
        sys.exit(1)

    df_os = pd.read_parquet(caminho_os)
    veiculos_unicos = df_os["veiculo_id"].dropna().unique()
    n_veiculos = min(2000, len(veiculos_unicos))
    np.random.seed(42)
    veiculos_selecionados = np.random.choice(veiculos_unicos, size=n_veiculos, replace=False)
    df_sub = df_os[df_os["veiculo_id"].isin(veiculos_selecionados)].copy()

    # Parâmetros calibrados para a instância canônica S0 (Nominal, 36 meses)
    T = 36  # Horizonte trienal 2027-2029 (36 meses)
    km_base = df_sub.groupby("veiculo_id")["nr_quilometragem"].max().to_dict()
    custo_base = df_sub.groupby("veiculo_id")["vl_aprovado_total"].mean().to_dict()
    custo_medio_geral = float(np.median([v for v in custo_base.values() if v > 0])) if custo_base else 850.0

    c_it = np.zeros((n_veiculos, T))  # Custo direto de manutenção preventiva
    r_it = np.zeros((n_veiculos, T))  # Redução estocástica esperada no custo de falha corretiva
    h_it = np.zeros((n_veiculos, T))  # Consumo de capacidade operacional de oficina (horas)
    m_it = np.zeros((n_veiculos, T), dtype=int)  # Intervenções mandatórias regulatórias

    for i in range(n_veiculos):
        v_placa = veiculos_selecionados[i]
        v_km = km_base.get(v_placa, 80000.0)
        v_c = min(1100.0, max(280.0, float(custo_base.get(v_placa, custo_medio_geral) * 0.288)))

        for t in range(T):
            fator_idade = 1.0 + (t / 36.0) * 0.15
            fator_km = 1.0 + (v_km / 150000.0) * 0.20
            c_it[i, t] = max(180.0, float(v_c * fator_idade * fator_km * np.random.uniform(0.94, 1.06)))

            prob_falha = min(0.60, 0.05 + (t % 12) * 0.035 + (v_km / 200000.0) * 0.15)
            custo_emergencial = c_it[i, t] * 2.1 + 520.0
            r_it[i, t] = float(prob_falha * custo_emergencial)
            h_it[i, t] = max(1.5, float(c_it[i, t] / 180.0))

            if (t + (i % 6)) % 12 == 0:
                m_it[i, t] = 1

    # Limites orçamentários nominais B_t e de oficina H_t do Cenário S0
    custo_potencial_mensal = np.sum(c_it, axis=0)
    horas_potencial_mensal = np.sum(h_it, axis=0)

    B_t = {t: float(np.mean(custo_potencial_mensal) * 0.45) for t in range(T)}
    H_t = {t: float(np.mean(horas_potencial_mensal) * 0.50) for t in range(T)}

    # 2. Resolução do Modelo Inteiro Exato (MIP via HiGHS)
    print("\n[2/5] Resolvendo MILP Inteiro Exato (Solucionador HiGHS)...")
    t0_mip = time.time()
    x_mip = np.zeros((n_veiculos, T), dtype=int)
    custo_direto_mip = 0.0
    risco_residual_mip = 0.0

    for t in range(T):
        c_obj = c_it[:, t] - r_it[:, t]
        A_mat = np.vstack([c_it[:, t], h_it[:, t]])
        b_u = np.array([B_t[t], H_t[t]])
        b_l = np.array([-np.inf, -np.inf])
        constraints = LinearConstraint(A_mat, b_l, b_u)

        lb = m_it[:, t].astype(float)
        ub = np.ones(n_veiculos)
        bounds = Bounds(lb, ub)
        integrality = np.ones(n_veiculos)

        res = milp(c=c_obj, integrality=integrality, bounds=bounds, constraints=constraints, options={'time_limit': 2.0, 'mip_rel_gap': 0.0001})
        x_t = np.round(res.x).astype(int) if (res.x is not None) else m_it[:, t]
        x_mip[:, t] = x_t

        custo_direto_mip += float(np.sum(x_t * c_it[:, t]))
        risco_residual_mip += float(np.sum((1 - x_t) * r_it[:, t]))

    tempo_mip = time.time() - t0_mip
    custo_total_mip = custo_direto_mip + risco_residual_mip

    # ------------------------------------------------------------------
    # Correção (15/11/2026): os custos passam a ser os calculados pelo solver.
    # A versão anterior descartava o resultado do HiGHS e usava constantes
    # (MIP R$ 43.837.633,31; BL0 R$ 53.139.780,57; MILP-0 R$ 48.719.011,68).
    #
    # Critério de H3 (anteprojeto), fixado antes desta execução:
    #   "Sob o mesmo orçamento, capacidade e nível de risco admissível, a política de
    #    otimização reduz o custo total esperado ... em relação à prática reconstruída
    #    e a regras heurísticas." -> H3 sustentada se custo MILP < custo BL0 (prática
    #   reconstruída = só manutenções obrigatórias) E custo MILP < custo da heurística
    #   gulosa, ambas sob as mesmas restrições de orçamento e capacidade.
    #   Limiar numérico pré-registrado (qualificação): economia > 10% sobre BL0.
    # ------------------------------------------------------------------
    def custo_politica(x):
        return float(np.sum(x * c_it) + np.sum((1 - x) * r_it))

    # Relaxação linear (limite inferior do MIP), mês a mês
    t0_lp = time.time()
    custo_total_lp, status_lp = 0.0, []
    for t in range(T):
        res_lp = milp(c=c_it[:, t] - r_it[:, t], integrality=np.zeros(n_veiculos),
                      bounds=Bounds(m_it[:, t].astype(float), np.ones(n_veiculos)),
                      constraints=LinearConstraint(np.vstack([c_it[:, t], h_it[:, t]]), [-np.inf, -np.inf], [B_t[t], H_t[t]]))
        status_lp.append(int(res_lp.status))
        xl = res_lp.x if res_lp.x is not None else m_it[:, t].astype(float)
        custo_total_lp += float(np.sum(xl * c_it[:, t]) + np.sum((1 - xl) * r_it[:, t]))
    tempo_lp = time.time() - t0_lp

    # BL0: prática reconstruída (apenas manutenções obrigatórias)
    x_bl0 = m_it.astype(int)
    custo_bl0 = custo_politica(x_bl0)

    # BL1: heurística gulosa por razão benefício/custo dentro do orçamento e da capacidade
    x_heur = m_it.astype(int).copy()
    for t in range(T):
        gasto = float(np.sum(x_heur[:, t] * c_it[:, t])); horas = float(np.sum(x_heur[:, t] * h_it[:, t]))
        cand = [i for i in range(n_veiculos) if x_heur[i, t] == 0 and r_it[i, t] > c_it[i, t]]
        for i in sorted(cand, key=lambda i: r_it[i, t] / c_it[i, t], reverse=True):
            if gasto + c_it[i, t] <= B_t[t] and horas + h_it[i, t] <= H_t[t]:
                x_heur[i, t] = 1; gasto += c_it[i, t]; horas += h_it[i, t]
    custo_heur = custo_politica(x_heur)

    viavel_bl0 = all(float(np.sum(m_it[:, t] * c_it[:, t])) <= B_t[t] + 1e-6 and float(np.sum(m_it[:, t] * h_it[:, t])) <= H_t[t] + 1e-6 for t in range(T))
    integrality_gap_abs = custo_total_mip - custo_total_lp
    integrality_gap_rel = integrality_gap_abs / custo_total_lp if custo_total_lp else float("nan")
    economia_gerada = custo_bl0 - custo_total_mip
    pct_economia = economia_gerada / custo_bl0 * 100.0
    economia_vs_heur = custo_heur - custo_total_mip
    pct_economia_heur = economia_vs_heur / custo_heur * 100.0
    gasto_mes = np.sum(x_mip * c_it, axis=0)
    pct_orc_ativo = float(np.mean([gasto_mes[t] >= 0.99 * B_t[t] for t in range(T)]) * 100)
    pct_ofi_ativo = float(np.mean([np.sum(x_mip[:, t] * h_it[:, t]) >= 0.99 * H_t[t] for t in range(T)]) * 100)
    cumprimento_mandatorio = float(np.sum(x_mip * m_it) / max(1, np.sum(m_it)) * 100)
    h3_anteprojeto = bool(custo_total_mip < custo_bl0 and custo_total_mip < custo_heur)
    h3_limiar = bool(pct_economia > 10.0)

    print(f"  -> MILP (HiGHS): R$ {custo_total_mip:,.2f} | LP: R$ {custo_total_lp:,.2f} | gap {integrality_gap_rel * 100:.5f}%")
    print(f"  -> BL0 (só obrigatórias): R$ {custo_bl0:,.2f} | Heurística gulosa: R$ {custo_heur:,.2f}")
    print(f"  -> Economia vs BL0: R$ {economia_gerada:,.2f} ({pct_economia:.2f}%) | vs heurística: R$ {economia_vs_heur:,.2f} ({pct_economia_heur:.2f}%)")
    print(f"  -> Orçamento ativo em {pct_orc_ativo:.1f}% dos meses | oficina ativa em {pct_ofi_ativo:.1f}% | obrigatórias cumpridas {cumprimento_mandatorio:.1f}%")
    print(f"  -> H3 (anteprojeto): {h3_anteprojeto} | H3 (limiar > 10%): {h3_limiar}")

    # 3. Figura: custo mensal das três políticas (todos os valores calculados)
    print("\n[3/5] Gerando figura com os custos calculados...")
    meses = np.arange(1, T + 1)
    cm = lambda x: (np.sum(x * c_it, axis=0) + np.sum((1 - x) * r_it, axis=0)) / 1e6
    fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=300)
    ax.plot(meses, cm(x_bl0), "o-", color="#dc2626", ms=3, lw=1.8, label=f"BL0 – só obrigatórias (R$ {custo_bl0 / 1e6:,.2f} mi)")
    ax.plot(meses, cm(x_heur), "^-", color="#d99a00", ms=3, lw=1.5, label=f"Heurística gulosa (R$ {custo_heur / 1e6:,.2f} mi)")
    ax.plot(meses, cm(x_mip), "s-", color="#0284c7", ms=3, lw=2.0, label=f"MILP HiGHS (R$ {custo_total_mip / 1e6:,.2f} mi)")
    ax.set_xlabel("Mês do horizonte simulado (1 a 36)"); ax.set_ylabel("Custo esperado no mês (R$ milhões)")
    ax.set_title(f"Custo esperado por política – cenário S0 ({n_veiculos} veículos, {T} meses)", fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.45); ax.legend(fontsize=8.5)
    plt.tight_layout(); plt.savefig(res_figuras / "figura_milp_trajetoria_financeira.png", dpi=300); plt.close()

    df_auditoria_milp = pd.DataFrame([
        {"metrica": "Custo total MILP (HiGHS)", "valor_brl": round(custo_total_mip, 2)},
        {"metrica": "Relaxação linear (LP)", "valor_brl": round(custo_total_lp, 2)},
        {"metrica": "BL0 – só manutenções obrigatórias", "valor_brl": round(custo_bl0, 2)},
        {"metrica": "Heurística gulosa benefício/custo", "valor_brl": round(custo_heur, 2)},
    ])
    df_auditoria_milp.to_csv(res_metricas / "auditoria_poliedral_milp.csv", index=False)

    duracao = (datetime.now() - inicio_exec).total_seconds()
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "duracao_segundos": round(duracao, 2),
        "cenario": "Cenário de Referência S0 (Nominal, 36 meses)",
        "natureza_da_instancia": ("Semissintética: 2.000 veículos reais sorteados (semente 42); custos, probabilidades de falha "
                                  "e calendário de obrigatórias gerados por fórmulas com fatores aleatórios (seed 42). "
                                  "Resultado é contrafactual simulado, não economia observada."),
        "solver": "HiGHS via scipy.optimize.milp (36 problemas mensais independentes)",
        "dimensoes": {"veiculos": n_veiculos, "periodos_meses": T, "total_variaveis_decisao": int(n_veiculos * T)},
        "solucao_inteira_mip_brl": round(custo_total_mip, 2),
        "relaxacao_linear_lp_brl": round(custo_total_lp, 2),
        "integrality_gap_relativo": round(integrality_gap_rel, 9),
        "integrality_gap_absoluto_brl": round(integrality_gap_abs, 2),
        "tolerancia_mip_rel_gap": 0.0001,
        "tempo_mip_s": round(tempo_mip, 2), "tempo_lp_s": round(tempo_lp, 2),
        "status_lp_por_mes": status_lp,
        "cumprimento_mandatorio_pct": round(cumprimento_mandatorio, 2),
        "bl0_viavel": viavel_bl0,
        "gargalos_ativos": {"restricao_orcamentaria_pct_periodos": round(pct_orc_ativo, 2),
                            "restricao_oficina_pct_periodos": round(pct_ofi_ativo, 2)},
        "confronto_inercial": {
            "definicao_bl0": "prática reconstruída: executar apenas as manutenções obrigatórias",
            "custo_inercial_as_is_brl": round(custo_bl0, 2),
            "custo_heuristica_gulosa_brl": round(custo_heur, 2),
            "economia_prescritiva_brl": round(economia_gerada, 2),
            "economia_pct": round(pct_economia, 2),
            "economia_vs_heuristica_brl": round(economia_vs_heur, 2),
            "economia_vs_heuristica_pct": round(pct_economia_heur, 2),
        },
        "criterio_h3": {"anteprojeto": "custo MILP < BL0 e < heurística, sob as mesmas restrições",
                        "limiar_pre_registrado": "economia > 10% sobre BL0"},
        "hipotese_h3_sustentada_anteprojeto": h3_anteprojeto,
        "hipotese_h3_sustentada_limiar": h3_limiar,
        "hipotese_h3_sustentada": bool(h3_anteprojeto and h3_limiar),
        "conclusao_auditoria": (
            f"MILP (HiGHS) R$ {custo_total_mip:,.2f}; BL0 R$ {custo_bl0:,.2f}; heurística R$ {custo_heur:,.2f}. "
            f"Economia de {pct_economia:.2f}% sobre BL0 e {pct_economia_heur:.2f}% sobre a heurística, em instância semissintética."
        )
    }

    with open(res_logs / "relatorio_otimizacao_milp.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    # Cópia no diretório lido pela etapa 09 e pelos relatórios (resultados/logs).
    # Sem ela, a etapa 09 certificava H3 com um arquivo antigo de 22/10/2026.
    res_logs_oficial = base_dir / "resultados" / "logs"
    res_logs_oficial.mkdir(parents=True, exist_ok=True)
    with open(res_logs_oficial / "relatorio_otimizacao_milp.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    with open(res_metricas / "experimento_milp_cenario_s0.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCESSO] Script 08 concluído com êxito em {duracao:.2f}s!")
    print(f"  -> JSON: {res_logs / 'relatorio_otimizacao_milp.json'}")


if __name__ == "__main__":
    executar_otimizacao_milp()

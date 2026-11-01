#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria Matemática Avançada do Modelo MILP:
Relaxação Linear Contínua (LP), Gap de Integralidade, Preços-Sombra e Sensibilidade
PPGCAP / CCT / UDESC - 2026
Autor: Eduardo Lopes Jonker

Executa a análise matemática formal exigida na Etapa 3:
1. Solução Linear Contínua (LP Relaxation) vs Solução Inteira (MIP).
2. Cálculo exato do Integrality Gap (MIP Gap).
3. Identificação de Restrições Ativas (Gargalos: Orçamento B_t vs Capacidade H_t).
4. Análise de Sensibilidade Orçamentária e Fronteira de Eficiência.
"""

import sys
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import milp, linprog, LinearConstraint, Bounds

BASE_DIR = Path(__file__).resolve().parent.parent
DADOS_DIR = BASE_DIR / "dados"
RELATORIOS_DIR = BASE_DIR / "relatorios"
RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

print("=== [INÍCIO] AUDITORIA MATEMÁTICA AVANÇADA DO SOLVER MILP (HiGHS) ===")

# Carregar os mesmos dados canônicos do protocolo S0
csv_path = DADOS_DIR / "os_dataset_limpo.csv"
df = pd.read_csv(csv_path, usecols=['veiculo_id', 'nr_anoveiculo', 'nr_quilometragem', 'Valor_Aprovado'], low_memory=False)

veiculos_unicos = df['veiculo_id'].dropna().unique()
N_veiculos = min(2000, len(veiculos_unicos))
np.random.seed(42)
veiculos_selecionados = np.random.choice(veiculos_unicos, size=N_veiculos, replace=False)
df_sub = df[df['veiculo_id'].isin(veiculos_selecionados)].copy()

custo_medio_historico = df_sub['Valor_Aprovado'].median()
if np.isnan(custo_medio_historico) or custo_medio_historico <= 0:
    custo_medio_historico = 850.0

T = 36
km_base = df_sub.groupby('veiculo_id')['nr_quilometragem'].max().to_dict()
custo_base = df_sub.groupby('veiculo_id')['Valor_Aprovado'].mean().to_dict()

c_it = np.zeros((N_veiculos, T))
r_it = np.zeros((N_veiculos, T))
h_it = np.zeros((N_veiculos, T))
m_it = np.zeros((N_veiculos, T), dtype=int)

for i in range(N_veiculos):
    v_id = veiculos_selecionados[i]
    v_km = km_base.get(v_id, 80000)
    v_c = custo_base.get(v_id, custo_medio_historico)
    
    for t in range(T):
        fator_idade = 1.0 + (t / 36.0) * 0.15
        fator_km = 1.0 + (v_km / 150000.0) * 0.20
        c_it[i, t] = max(250.0, float(v_c * fator_idade * fator_km * np.random.uniform(0.92, 1.08)))
        
        prob_falha = min(0.65, 0.05 + (t % 12) * 0.035 + (v_km / 200000.0) * 0.15)
        custo_falha_emergencial = c_it[i, t] * 2.1 + 850.0
        r_it[i, t] = float(prob_falha * custo_falha_emergencial)
        h_it[i, t] = max(1.5, float(c_it[i, t] / 180.0))
        
        if (t + (i % 6)) % 12 == 0:
            m_it[i, t] = 1

custo_total_mensal_potencial = np.sum(c_it, axis=0)
horas_total_mensal_potencial = np.sum(h_it, axis=0)

B_t = {t: float(np.mean(custo_total_mensal_potencial) * 0.45) for t in range(T)}
H_t = {t: float(np.mean(horas_total_mensal_potencial) * 0.50) for t in range(T)}

# 1. RESOLVER MIP INTEIRO (HiGHS)
print("\n[1/3] Resolvendo MIP Inteiro (HiGHS)...")
t0 = time.time()
x_mip = np.zeros((N_veiculos, T), dtype=int)
custo_direto_mip = 0.0
risco_residual_mip = 0.0

for t in range(T):
    c_obj = c_it[:, t] - r_it[:, t]
    A_mat = np.vstack([c_it[:, t], h_it[:, t]])
    b_u = np.array([B_t[t], H_t[t]])
    b_l = np.array([-np.inf, -np.inf])
    constraints = LinearConstraint(A_mat, b_l, b_u)
    
    lb = m_it[:, t].astype(float)
    ub = np.ones(N_veiculos)
    bounds = Bounds(lb, ub)
    integrality = np.ones(N_veiculos) # 1 = binário/inteiro
    
    res = milp(c=c_obj, integrality=integrality, bounds=bounds, constraints=constraints)
    x_t = np.round(res.x).astype(int)
    x_mip[:, t] = x_t

tempo_mip = time.time() - t0
custo_direto_mip = np.sum(c_it * x_mip)
risco_residual_mip = np.sum(r_it * (1 - x_mip))
custo_total_mip = custo_direto_mip + risco_residual_mip

# 2. RESOLVER RELAXAÇÃO LINEAR CONTÍNUA (LP Relaxation)
print("[2/3] Resolvendo Relaxação Linear Contínua (LP Relaxation via HiGHS Dual Simplex)...")
t0 = time.time()
x_lp = np.zeros((N_veiculos, T), dtype=float)
custo_direto_lp = 0.0
risco_residual_lp = 0.0
dual_orcamento = []
dual_horas = []

for t in range(T):
    c_obj = c_it[:, t] - r_it[:, t]
    A_ub = np.vstack([c_it[:, t], h_it[:, t]])
    b_ub = np.array([B_t[t], H_t[t]])
    
    bounds_lp = [(m_it[i, t], 1.0) for i in range(N_veiculos)]
    
    res_lp = linprog(c=c_obj, A_ub=A_ub, b_ub=b_ub, bounds=bounds_lp, method='highs-ds')
    x_lp[:, t] = res_lp.x
    
    # Preços-sombra (shadow prices / dual variables)
    # No scipy highs-ds, res_lp.ineqlin.marginals contém os multiplicadores de Lagrange
    marginais = res_lp.ineqlin.marginals if hasattr(res_lp, 'ineqlin') and res_lp.ineqlin is not None else [0.0, 0.0]
    dual_orcamento.append(float(marginais[0]))
    dual_horas.append(float(marginais[1]))

tempo_lp = time.time() - t0
custo_direto_lp = np.sum(c_it * x_lp)
risco_residual_lp = np.sum(r_it * (1 - x_lp))
custo_total_lp = custo_direto_lp + risco_residual_lp

integrality_gap = ((custo_total_mip - custo_total_lp) / custo_total_mip) * 100.0

print(f"Custo Total MIP (Inteiro): R$ {custo_total_mip:,.2f}")
print(f"Custo Total LP  (Relaxado): R$ {custo_total_lp:,.2f}")
print(f"Integrality Gap: {integrality_gap:.4f}% ({abs(custo_total_mip - custo_total_lp):,.2f} reais)")

# 3. ANÁLISE DE RESTRIÇÕES ATIVAS E PREÇOS-SOMBRA MÉDIOS
prop_orc_ativo = float(np.mean([abs(d) > 1e-5 for d in dual_orcamento])) * 100.0
prop_hrs_ativo = float(np.mean([abs(d) > 1e-5 for d in dual_horas])) * 100.0

print(f"Meses com Orçamento Restritivo Ativo (B_t): {prop_orc_ativo:.1f}%")
print(f"Meses com Capacidade de Horas Ativa (H_t): {prop_hrs_ativo:.1f}%")

# 4. ANÁLISE DE SENSIBILIDADE ORÇAMENTÁRIA (0.75x, 1.00x, 1.25x, 1.50x)
print("\n[3/3] Executando Análise de Sensibilidade Paramétrica Orçamentária...")
fatores_orcamento = [0.70, 0.85, 1.00, 1.15, 1.30]
sensibilidade_res = []

for fator in fatores_orcamento:
    x_sens = np.zeros((N_veiculos, T), dtype=int)
    for t in range(T):
        c_obj = c_it[:, t] - r_it[:, t]
        A_mat = np.vstack([c_it[:, t], h_it[:, t]])
        b_u = np.array([B_t[t] * fator, H_t[t]])
        b_l = np.array([-np.inf, -np.inf])
        constraints = LinearConstraint(A_mat, b_l, b_u)
        
        lb = m_it[:, t].astype(float)
        ub = np.ones(N_veiculos)
        bounds = Bounds(lb, ub)
        integrality = np.ones(N_veiculos)
        
        res = milp(c=c_obj, integrality=integrality, bounds=bounds, constraints=constraints)
        if res.success or res.status in [0, 1]:
            x_sens[:, t] = np.round(res.x).astype(int)
        else:
            x_sens[:, t] = m_it[:, t]
            
    c_dir = np.sum(c_it * x_sens)
    r_res = np.sum(r_it * (1 - x_sens))
    c_tot = c_dir + r_res
    h_imob = np.sum(h_it * x_sens)
    h_quebra = np.sum((r_it / 450.0) * (1 - x_sens))
    disp = max(0.0, min(100.0, ((N_veiculos * T * 160) - h_imob - (h_quebra * 8)) / (N_veiculos * T * 160) * 100.0))
    interv_total = int(np.sum(x_sens))
    
    sensibilidade_res.append({
        "fator_orcamento": float(fator),
        "fator_descricao": f"{int(fator*100)}% do Orçamento Nominal",
        "orcamento_total_trienal": float(sum(B_t.values()) * fator),
        "custo_intervencoes": float(c_dir),
        "risco_residual": float(r_res),
        "custo_total": float(c_tot),
        "disponibilidade_pct": float(disp),
        "intervencoes_realizadas": interv_total
    })
    print(f"Fator {fator:.2f} | Custo Total: R$ {c_tot:,.2f} | Disp: {disp:.2f}% | Intervenções: {interv_total}")

relatorio_milp_avancado = {
    "metadados": {
        "solver": "HiGHS (Simplex Dual / Branch-and-Cut)",
        "versao_scipy": "1.16+",
        "tolerancia_otimalidade": 1e-7,
        "n_veiculos": N_veiculos,
        "horizonte_meses": T,
        "variaveis_decisao": N_veiculos * T,
        "restricoes_totais": T * 2 + int(np.sum(m_it))
    },
    "auditoria_relaxacao_linear": {
        "custo_total_mip_inteiro": float(custo_total_mip),
        "custo_total_lp_relaxado": float(custo_total_lp),
        "integrality_gap_absoluto": float(abs(custo_total_mip - custo_total_lp)),
        "integrality_gap_relativo_pct": float(integrality_gap),
        "tempo_mip_segundos": float(tempo_mip),
        "tempo_lp_segundos": float(tempo_lp)
    },
    "restricoes_ativas": {
        "propensao_orcamento_ativo_pct": prop_orc_ativo,
        "propensao_horas_ativas_pct": prop_hrs_ativo,
        "gargalo_dominante": "Orçamento Financeiro Mensal (B_t)" if prop_orc_ativo >= prop_hrs_ativo else "Capacidade Operacional de Oficinas (H_t)"
    },
    "sensibilidade_orcamentaria": sensibilidade_res
}

out_json = RELATORIOS_DIR / "auditoria_matematica_milp_avancada.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(relatorio_milp_avancado, f, indent=2, ensure_ascii=False)

print(f"\n[SUCESSO] Relatório de Auditoria Matemática MILP salvo em: {out_json}")
print("=== [FIM] AUDITORIA MATEMÁTICA CONCLUÍDA ===")

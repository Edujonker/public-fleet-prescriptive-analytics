#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Removedor de Marcações LaTeX dos Artigos Científicos
Dissertação de Mestrado, PPGCAP/UDESC
Substitui notações LaTeX brutas ($...$ e $$...$$) por tipografia limpa Unicode
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIGOS_DIR = BASE_DIR / "artigos_internacionais"

def limpar_artigo1_pt():
    p = ARTIGOS_DIR / "artigo1_analitica_prescritiva_milp_gestao_frotas_pt.md"
    t = p.read_text(encoding="utf-8")

    # Afiliações
    t = t.replace("Eduardo Lopes Jonker$^1$", "Eduardo Lopes Jonker¹")
    t = t.replace("Vivian Kremer Kalempa$^1$", "Vivian Kremer Kalempa¹")
    t = t.replace("Yuri Kaszubowski Lopes$^1$", "Yuri Kaszubowski Lopes¹")
    t = t.replace("$^1$ Programa", "¹ Programa")

    # Bloco Função Objetivo
    eq_obj_old = """$$\\min \\mathcal{Z} = \\sum_{t=1}^T \\sum_{i \\in \\mathcal{V}} \\frac{1}{(1 + \\delta)^t} \\left[ c_{it}^{prev} x_{it} + \\hat{c}_{it}^{comb} y_{it} + \\hat{p}_{it}^{falha} c_{it}^{corr} (1 - x_{it}) y_{it} - v_i^{leilao} z_{it} \\right]$$"""
    eq_obj_new = """```text
Minimizar Z = Σ_{t=1..T} Σ_{i∈V} [ 1 / (1 + δ)^t ] * [ c_it(prev) * x_it + ĉ_it(comb) * y_it + p̂_it(falha) * c_it(corr) * (1 - x_it) * y_it - v_i(leilao) * z_it ]
```"""
    t = t.replace(eq_obj_old, eq_obj_new)

    # Restrições
    t = t.replace("$$y_{it} + z_{it} = y_{i, t-1}, \\quad \\forall i \\in \\mathcal{V}, \\forall t \\in \\mathcal{T}$$",
                  "`y_it + z_it = y_i(t-1),  ∀ i ∈ V, ∀ t ∈ T`")
    t = t.replace("$$z_{it} \\ge z_{i, t-1}, \\quad \\forall i \\in \\mathcal{V}, \\forall t \\in \\mathcal{T} \\quad \\text{(A desincorporação é um estado absorvente)}$$",
                  "`z_it ≥ z_i(t-1),  ∀ i ∈ V, ∀ t ∈ T (Desincorporação é estado absorvente)`")
    t = t.replace("$$x_{it} \\le y_{it}, \\quad \\forall i \\in \\mathcal{V}, \\forall t \\in \\mathcal{T}$$",
                  "`x_it ≤ y_it,  ∀ i ∈ V, ∀ t ∈ T`")
    t = t.replace("$$x_{it} \\ge m_{it} y_{it}, \\quad \\forall i \\in \\mathcal{V}, \\forall t \\in \\mathcal{T}$$",
                  "`x_it ≥ m_it * y_it,  ∀ i ∈ V, ∀ t ∈ T`")
    t = t.replace("$$\\sum_{i \\in \\mathcal{B}_k} y_{it} \\ge \\alpha_k |\\mathcal{B}_k|, \\quad \\forall k, \\forall t \\in \\mathcal{T}$$",
                  "`Σ_{i ∈ B_k} y_it ≥ α_k * |B_k|,  ∀ k, ∀ t ∈ T`")
    t = t.replace("$$\\sum_{i \\in \\mathcal{V}} \\left( c_{it}^{prev} x_{it} + \\hat{p}_{it}^{falha} c_{it}^{corr} (1 - x_{it}) y_{it} \\right) \\le B_t, \\quad \\forall t \\in \\mathcal{T} \\quad [\\text{Multiplicador Dual: } \\lambda_t \\ge 0]$$",
                  "`Σ_{i ∈ V} [ c_it(prev) * x_it + p̂_it(falha) * c_it(corr) * (1 - x_it) * y_it ] ≤ B_t,  ∀ t ∈ T  [Preço-Sombra Dual: λ_t ≥ 0]`")
    t = t.replace("$$\\text{Se } \\sum_{\\tau=1}^t c_{i\\tau}^{real} \\ge 0,40 \\cdot \\text{Valor}_{i}^{FIPE} \\implies z_{it} = 1$$",
                  "`Se Σ_{τ=1..t} c_iτ(real) ≥ 0,40 * Valor_FIPE(i)  ⟹  z_it = 1 (Alienação Obrigatória)`")

    # Inlines
    repl_inlines = [
        ("$R^2 = 0,748$", "R² = 0,748"),
        ("$R^2 = 0.748$", "R² = 0,748"),
        ("$\\ge 95,26\\%$", "≥ 95,26%"),
        ("$\\ge 95.26\\%$", "≥ 95,26%"),
        ("$N = 1.000$", "N = 1.000"),
        ("$\\hat{p}_{it}$", "p̂_it"),
        ("$B_t$", "B_t"),
        ("$\\mathcal{V} = \\{1, 2, \\dots, N\\}$", "V = {1, 2, ..., N}"),
        ("$N = 5.914$", "N = 5.914"),
        ("$\\mathcal{T} = \\{1, 2, \\dots, T\\}$", "T = {1, 2, ..., T}"),
        ("$T = 36$", "T = 36"),
        ("$\\mathcal{B}_k \\subset \\mathcal{V}$", "B_k ⊂ V"),
        ("$\\bigcup_k \\mathcal{B}_k = \\mathcal{V}$", "∪ B_k = V"),
        ("$\\mathcal{B}_j \\cap \\mathcal{B}_k = \\emptyset$", "B_j ∩ B_k = ∅"),
        ("$j \\neq k$", "j ≠ k"),
        ("$i \\in \\mathcal{V}$", "i ∈ V"),
        ("$t \\in \\mathcal{T}$", "t ∈ T"),
        ("$x_{it} \\in \\{0, 1\\}$", "x_it ∈ {0, 1}"),
        ("$y_{it} \\in \\{0, 1\\}$", "y_it ∈ {0, 1}"),
        ("$z_{it} \\in \\{0, 1\\}$", "z_it ∈ {0, 1}"),
        ("$\\delta$", "δ"),
        ("$\\mathcal{Z}$", "Z"),
        ("$c_{it}^{prev}$", "c_it(prev)"),
        ("$\\hat{c}_{it}^{comb}$", "ĉ_it(comb)"),
        ("$\\hat{p}_{it}^{falha} \\in [0, 1]$", "p̂_it(falha) ∈ [0, 1]"),
        ("$\\hat{p}_{it}^{falha}$", "p̂_it(falha)"),
        ("$c_{it}^{corr}$", "c_it(corr)"),
        ("$c_{it}^{reparo\\_corr}$", "c_it(reparo_corr)"),
        ("$c_{it}^{downtime}$", "c_it(downtime)"),
        ("$v_i^{leilao}$", "v_i(leilao)"),
        ("$\\mathcal{Q}_{50}$", "Q_50"),
        ("$m_{it} = 1$", "m_it = 1"),
        ("$\\alpha_k \\in [0,90; 0,95]$", "α_k ∈ [0,90; 0,95]"),
        ("$\\lambda_t \\ge 0$", "λ_t ≥ 0"),
        ("$\\lambda_t > 0$", "λ_t > 0"),
        ("$\\lambda_t = 0$", "λ_t = 0"),
        ("$\\lambda_t$", "λ_t"),
        ("$Z = 16,39; \\mathbf{p < 10^{-50}}$", "Z = 16,39; p < 10⁻⁵⁰"),
        ("$R^2$", "R²"),
        ("$W = 1.482.910; \\mathbf{p < 10^{-15}}$", "W = 1.482.910; p < 10⁻¹⁵"),
        ("$\\beta = 3,318$", "β = 3,318"),
        ("$\\alpha = -\\text{R\\$ } 5.855,12$", "α = -R$ 5.855,12"),
        ("$\\Delta = \\text{R\\$ } 9,47$", "Δ = R$ 9,47"),
        ("$t+1$", "t+1"),
        ("$\\delta = 0,005$", "δ = 0,005"),
        ("$R^2 Out-of-Sample$", "R² Out-of-Sample")
    ]
    for old, new in repl_inlines:
        t = t.replace(old, new)

    p.write_text(t, encoding="utf-8")
    print(f"✔ {p.name} limpo!")

def limpar_artigo2_pt():
    p = ARTIGOS_DIR / "artigo2_auditoria_ia_xai_shap_lime_redes_complexas_pt.md"
    t = p.read_text(encoding="utf-8")

    # Afiliações
    t = t.replace("Eduardo Lopes Jonker$^1$", "Eduardo Lopes Jonker¹")
    t = t.replace("Vivian Kremer Kalempa$^1$", "Vivian Kremer Kalempa¹")
    t = t.replace("Yuri Kaszubowski Lopes$^1$", "Yuri Kaszubowski Lopes¹")
    t = t.replace("$^1$ Programa", "¹ Programa")

    # Display blocks
    eq_shap_old = """$$\\phi_i(x) = \\sum_{S \\subseteq F \\setminus \\{i\\}} \\frac{|S|! (|F| - |S| - 1)!}{|F|!} \\left[ f_x(S \\cup \\{i\\}) - f_x(S) \\right]$$"""
    eq_shap_new = """```text
φ_i(x) = Σ_{S ⊆ F \\ {i}} [ |S|! * (|F| - |S| - 1)! / |F|! ] * [ f_x(S ∪ {i}) - f_x(S) ]
```"""
    t = t.replace(eq_shap_old, eq_shap_new)

    eq_lime1_old = """$$\\xi(x) = \\arg\\min_{g \\in G} \\mathcal{L}(f, g, \\pi_x) + \\Omega(g)$$"""
    eq_lime1_new = """```text
ξ(x) = argmin_{g ∈ G} L(f, g, π_x) + Ω(g)
```"""
    t = t.replace(eq_lime1_old, eq_lime1_new)

    eq_lime2_old = """$$\\pi_x(z) = \\exp\\left( - \\frac{D(x, z)^2}{\\sigma^2} \\right)$$"""
    eq_lime2_new = """```text
π_x(z) = exp( - D(x, z)² / σ² )
```"""
    t = t.replace(eq_lime2_old, eq_lime2_new)

    eq_jaccard_old = """$$J_k = \\frac{|\\mathcal{S}_k^{SHAP} \\cap \\mathcal{S}_k^{LIME}|}{|\\mathcal{S}_k^{SHAP} \\cup \\mathcal{S}_k^{LIME}|}$$"""
    eq_jaccard_new = """```text
J_k = | S_k(SHAP) ∩ S_k(LIME) | / | S_k(SHAP) ∪ S_k(LIME) |
```"""
    t = t.replace(eq_jaccard_old, eq_jaccard_new)

    eq_louvain_old = """$$Q = \\frac{1}{2m} \\sum_{i, j} \\left[ A_{ij} - \\frac{k_i k_j}{2m} \\right] \\delta(c_i, c_j) = 0,5646$$"""
    eq_louvain_new = """```text
Q = (1 / 2m) * Σ_{i,j} [ A_ij - (k_i * k_j) / (2m) ] * δ(c_i, c_j) = 0,5646
```"""
    t = t.replace(eq_louvain_old, eq_louvain_new)

    eq_metp_old = """$$\\text{Escore de Elegibilidade Decisória } (\\Omega_i) = w_1 \\cdot \\text{Rank}_{SHAP}(i) + w_2 \\cdot \\text{Rank}_{LIME}(i) + w_3 \\cdot \\text{Centralidade}_{Grafo}(i) + w_4 \\cdot \\text{Regra}_{Normativa}(i)$$"""
    eq_metp_new = """```text
Escore de Elegibilidade Decisória Ω(i) = w_1 * Rank_SHAP(i) + w_2 * Rank_LIME(i) + w_3 * Centralidade_Grafo(i) + w_4 * Regra_Normativa(i)
```"""
    t = t.replace(eq_metp_old, eq_metp_new)

    # Inlines
    repl_inlines = [
        ("$\\rho = 0,3680$", "ρ = 0,3680"),
        ("$\\rho = 0.3680$", "ρ = 0,3680"),
        ("$\\tau_b = 0,2915$", "τ_b = 0,2915"),
        ("$\\tau_b = 0.2915$", "τ_b = 0,2915"),
        ("$\\nu = 0,0085$", "ν = 0,0085"),
        ("$\\nu = 0.0085$", "ν = 0,0085"),
        ("$J = 0,8055$", "J = 0,8055"),
        ("$J = 0.8055$", "J = 0,8055"),
        ("$Q = 0,5646$", "Q = 0,5646"),
        ("$Q = 0.5646$", "Q = 0,5646"),
        ("$Q = 0,384$", "Q = 0,384"),
        ("$Q = 0.384$", "Q = 0,384"),
        ("$\\sum_{i \\in F} \\phi_i(x) = f(x) - \\mathbb{E}[f(x)]$", "Σ_{i ∈ F} φ_i(x) = f(x) - E[f(x)]"),
        ("$f(S \\cup \\{i\\}) = f(S \\cup \\{j\\})$", "f(S ∪ {i}) = f(S ∪ {j})"),
        ("$\\phi_i = \\phi_j$", "φ_i = φ_j"),
        ("$f(S \\cup \\{i\\}) = f(S)$", "f(S ∪ {i}) = f(S)"),
        ("$\\phi_i = 0$", "φ_i = 0"),
        ("$f + g$", "f + g"),
        ("$\\phi_i(f + g) = \\phi_i(f) + \\phi_i(g)$", "φ_i(f + g) = φ_i(f) + φ_i(g)"),
        ("$g(z') = w^T z'$", "g(z') = wᵀ z'"),
        ("$\\Omega(g)$", "Ω(g)"),
        ("$\\pi_x(z)$", "π_x(z)"),
        ("$\\sigma$", "σ"),
        ("$n = 2.500$", "n = 2.500"),
        ("$N = 77.867$", "N = 77.867"),
        ("$\\mathcal{S}_k^{SHAP}$", "S_k(SHAP)"),
        ("$\\mathcal{S}_k^{LIME}$", "S_k(LIME)"),
        ("($J$)", "(J)"),
        ("($\\rho$)", "(ρ)"),
        ("($\\tau_b$)", "(τ_b)"),
        ("($p < 10^{-50}$)", "(p < 10⁻⁵⁰)"),
        ("($> 0,40$", "(> 0,40"),
        ("($> 0.40$", "(> 0,40"),
        ("$\\mathcal{G} = (\\mathcal{V}_{veic}, \\mathcal{V}_{ofic}, \\mathcal{E}, \\mathcal{W})$", "G = (V_veic, V_ofic, E, W)"),
        ("$\\mathcal{V}_{veic}$", "V_veic"),
        ("$\\mathcal{V}_{ofic}$", "V_ofic"),
        ("$\\mathcal{E}$", "E"),
        ("$\\mathcal{W}$", "W"),
        ("$u$", "u"),
        ("$v$", "v"),
        ("$n_{arvores} = 150$", "n_arvores = 150"),
        ("($t = 3,524; p = 0,000426$)", "(t = 3,524; p = 0,000426)"),
        ("($J = 39,29\\%$)", "(J = 39,29%)"),
        ("$\\phi_i^{SHAP}$", "φ_i(SHAP)"),
        ("$\\phi_i^{LIME}$", "φ_i(LIME)"),
        ("$\\text{Sinal}(\\phi_i) \\neq \\text{Sinal}(w_i)$", "Sinal(φ_i) ≠ Sinal(w_i)"),
        ("$> 85,0\\%$", "> 85,0%"),
        ("$> 85.0\\%$", "> 85,0%"),
        ("$> 0,800$", "> 0,800"),
        ("$> 0.800$", "> 0,800"),
        ("$> 0,750$", "> 0,750"),
        ("$> 0.750$", "> 0,750"),
        ("$> 95,0\\%$", "> 95,0%"),
        ("$> 95.0\\%$", "> 95,0%")
    ]
    for old, new in repl_inlines:
        t = t.replace(old, new)

    p.write_text(t, encoding="utf-8")
    print(f"✔ {p.name} limpo!")

def limpar_paper1_en():
    p = ARTIGOS_DIR / "paper1_prescriptive_analytics_milp_fleet_management.md"
    t = p.read_text(encoding="utf-8")

    # Affiliations
    t = t.replace("Eduardo Lopes Jonker$^1$", "Eduardo Lopes Jonker¹")
    t = t.replace("Vivian Kremer Kalempa$^1$", "Vivian Kremer Kalempa¹")
    t = t.replace("Yuri Kaszubowski Lopes$^1$", "Yuri Kaszubowski Lopes¹")
    t = t.replace("$^1$ Graduate", "¹ Graduate")

    # Display blocks
    eq_obj_old = """$$\\min \\mathcal{Z} = \\sum_{t=1}^T \\sum_{i \\in \\mathcal{V}} \\frac{1}{(1 + \\delta)^t} \\left[ c_{it}^{prev} x_{it} + \\hat{c}_{it}^{comb} y_{it} + \\hat{p}_{it}^{fail} c_{it}^{corr} (1 - x_{it}) y_{it} - v_i^{salvage} z_{it} \\right]$$"""
    eq_obj_new = """```text
Minimize Z = Σ_{t=1..T} Σ_{i∈V} [ 1 / (1 + δ)^t ] * [ c_it(prev) * x_it + ĉ_it(fuel) * y_it + p̂_it(fail) * c_it(corr) * (1 - x_it) * y_it - v_i(salvage) * z_it ]
```"""
    t = t.replace(eq_obj_old, eq_obj_new)

    # Constraints
    t = t.replace("$$y_{it} + z_{it} = y_{i, t-1}, \\quad \\forall i \\in \\mathcal{V}, \\forall t \\in \\mathcal{T}$$",
                  "`y_it + z_it = y_i(t-1),  ∀ i ∈ V, ∀ t ∈ T`")
    t = t.replace("$$z_{it} \\ge z_{i, t-1}, \\quad \\forall i \\in \\mathcal{V}, \\forall t \\in \\mathcal{T} \\quad \\text{(Disposal is an absorbing state)}$$",
                  "`z_it ≥ z_i(t-1),  ∀ i ∈ V, ∀ t ∈ T (Disposal is an absorbing state)`")
    t = t.replace("$$x_{it} \\le y_{it}, \\quad \\forall i \\in \\mathcal{V}, \\forall t \\in \\mathcal{T}$$",
                  "`x_it ≤ y_it,  ∀ i ∈ V, ∀ t ∈ T`")
    t = t.replace("$$x_{it} \\ge m_{it} y_{it}, \\quad \\forall i \\in \\mathcal{V}, \\forall t \\in \\mathcal{T}$$",
                  "`x_it ≥ m_it * y_it,  ∀ i ∈ V, ∀ t ∈ T`")
    t = t.replace("$$\\sum_{i \\in \\mathcal{B}_k} y_{it} \\ge \\alpha_k |\\mathcal{B}_k|, \\quad \\forall k, \\forall t \\in \\mathcal{T}$$",
                  "`Σ_{i ∈ B_k} y_it ≥ α_k * |B_k|,  ∀ k, ∀ t ∈ T`")
    t = t.replace("$$\\sum_{i \\in \\mathcal{V}} \\left( c_{it}^{prev} x_{it} + \\hat{p}_{it}^{fail} c_{it}^{corr} (1 - x_{it}) y_{it} \\right) \\le B_t, \\quad \\forall t \\in \\mathcal{T} \\quad [\\text{Dual Shadow Price: } \\lambda_t \\ge 0]$$",
                  "`Σ_{i ∈ V} [ c_it(prev) * x_it + p̂_it(fail) * c_it(corr) * (1 - x_it) * y_it ] ≤ B_t,  ∀ t ∈ T  [Dual Shadow Price: λ_t ≥ 0]`")
    t = t.replace("$$\\text{If } \\sum_{\\tau=1}^t c_{i\\tau}^{actual} \\ge 0.40 \\cdot \\text{Value}_{i}^{FIPE} \\implies z_{it} = 1$$",
                  "`If Σ_{τ=1..t} c_iτ(actual) ≥ 0.40 * Value_FIPE(i)  ⟹  z_it = 1 (Mandatory Auction Disposal)`")

    # Inlines
    repl_inlines = [
        ("$R^2 = 0.748$", "R² = 0.748"),
        ("$\\ge 95.26\\%$", "≥ 95.26%"),
        ("$\\ge 15.0\\%$", "≥ 15.0%"),
        ("$N = 1,000$", "N = 1,000"),
        ("$\\hat{p}_{it}$", "p̂_it"),
        ("$B_t$", "B_t"),
        ("$\\mathcal{V} = \\{1, 2, \\dots, N\\}$", "V = {1, 2, ..., N}"),
        ("$N = 5,914$", "N = 5,914"),
        ("$\\mathcal{T} = \\{1, 2, \\dots, T\\}$", "T = {1, 2, ..., T}"),
        ("$T = 36$", "T = 36"),
        ("$\\mathcal{B}_k \\subset \\mathcal{V}$", "B_k ⊂ V"),
        ("$\\bigcup_k \\mathcal{B}_k = \\mathcal{V}$", "∪ B_k = V"),
        ("$\\mathcal{B}_j \\cap \\mathcal{B}_k = \\emptyset$", "B_j ∩ B_k = ∅"),
        ("$j \\neq k$", "j ≠ k"),
        ("$i \\in \\mathcal{V}$", "i ∈ V"),
        ("$t \\in \\mathcal{T}$", "t ∈ T"),
        ("$x_{it} \\in \\{0, 1\\}$", "x_it ∈ {0, 1}"),
        ("$y_{it} \\in \\{0, 1\\}$", "y_it ∈ {0, 1}"),
        ("$z_{it} \\in \\{0, 1\\}$", "z_it ∈ {0, 1}"),
        ("$\\delta$", "δ"),
        ("$\\mathcal{Z}$", "Z"),
        ("$c_{it}^{prev}$", "c_it(prev)"),
        ("$\\hat{c}_{it}^{comb}$", "ĉ_it(fuel)"),
        ("$\\hat{p}_{it}^{fail} \\in [0, 1]$", "p̂_it(fail) ∈ [0, 1]"),
        ("$\\hat{p}_{it}^{fail}$", "p̂_it(fail)"),
        ("$c_{it}^{corr}$", "c_it(corr)"),
        ("$c_{it}^{corr} = c_{it}^{repair\\_corr} + c_{it}^{downtime}$", "c_it(corr) = c_it(repair_corr) + c_it(downtime)"),
        ("$v_i^{salvage}$", "v_i(salvage)"),
        ("$\\mathcal{Q}_{50}$", "Q_50"),
        ("$m_{it} = 1$", "m_it = 1"),
        ("$\\alpha_k \\in [0.90, 0.95]$", "α_k ∈ [0.90, 0.95]"),
        ("$\\lambda_t \\ge 0$", "λ_t ≥ 0"),
        ("$\\lambda_t > 0$", "λ_t > 0"),
        ("$\\lambda_t = 0$", "λ_t = 0"),
        ("$\\lambda_t$", "λ_t"),
        ("$Z = 16.39, p < 10^{-50}$", "Z = 16.39, p < 10⁻⁵⁰"),
        ("$R^2$", "R²"),
        ("$W = 1,482,910, p < 10^{-15}$", "W = 1,482,910, p < 10⁻¹⁵"),
        ("$\\beta = 3.318$", "β = 3.318"),
        ("$\\alpha = -\\text{R\\$ } 5,855.12$", "α = -R$ 5,855.12"),
        ("$\\Delta = \\text{R\\$ } 9.47$", "Δ = R$ 9.47"),
        ("$t+1$", "t+1"),
        ("$\\delta = 0.005$", "δ = 0.005"),
        ("$R^2 Out-of-Sample$", "R² Out-of-Sample")
    ]
    for old, new in repl_inlines:
        t = t.replace(old, new)

    p.write_text(t, encoding="utf-8")
    print(f"✔ {p.name} limpo!")

def limpar_paper2_en():
    p = ARTIGOS_DIR / "paper2_xai_audit_shap_lime_network_graphs.md"
    t = p.read_text(encoding="utf-8")

    # Affiliations
    t = t.replace("Eduardo Lopes Jonker$^1$", "Eduardo Lopes Jonker¹")
    t = t.replace("Vivian Kremer Kalempa$^1$", "Vivian Kremer Kalempa¹")
    t = t.replace("Yuri Kaszubowski Lopes$^1$", "Yuri Kaszubowski Lopes¹")
    t = t.replace("$^1$ Graduate", "¹ Graduate")

    # Display blocks
    eq_shap_old = """$$\\phi_i(x) = \\sum_{S \\subseteq F \\setminus \\{i\\}} \\frac{|S|! (|F| - |S| - 1)!}{|F|!} \\left[ f_x(S \\cup \\{i\\}) - f_x(S) \\right]$$"""
    eq_shap_new = """```text
φ_i(x) = Σ_{S ⊆ F \\ {i}} [ |S|! * (|F| - |S| - 1)! / |F|! ] * [ f_x(S ∪ {i}) - f_x(S) ]
```"""
    t = t.replace(eq_shap_old, eq_shap_new)

    eq_lime1_old = """$$\\xi(x) = \\arg\\min_{g \\in G} \\mathcal{L}(f, g, \\pi_x) + \\Omega(g)$$"""
    eq_lime1_new = """```text
ξ(x) = argmin_{g ∈ G} L(f, g, π_x) + Ω(g)
```"""
    t = t.replace(eq_lime1_old, eq_lime1_new)

    eq_lime2_old = """$$\\pi_x(z) = \\exp\\left( - \\frac{D(x, z)^2}{\\sigma^2} \\right)$$"""
    eq_lime2_new = """```text
π_x(z) = exp( - D(x, z)² / σ² )
```"""
    t = t.replace(eq_lime2_old, eq_lime2_new)

    eq_jaccard_old = """$$J_k = \\frac{|\\mathcal{S}_k^{SHAP} \\cap \\mathcal{S}_k^{LIME}|}{|\\mathcal{S}_k^{SHAP} \\cup \\mathcal{S}_k^{LIME}|}$$"""
    eq_jaccard_new = """```text
J_k = | S_k(SHAP) ∩ S_k(LIME) | / | S_k(SHAP) ∪ S_k(LIME) |
```"""
    t = t.replace(eq_jaccard_old, eq_jaccard_new)

    eq_louvain_old = """$$Q = \\frac{1}{2m} \\sum_{i, j} \\left[ A_{ij} - \\frac{k_i k_j}{2m} \\right] \\delta(c_i, c_j) = 0.5646$$"""
    eq_louvain_new = """```text
Q = (1 / 2m) * Σ_{i,j} [ A_ij - (k_i * k_j) / (2m) ] * δ(c_i, c_j) = 0.5646
```"""
    t = t.replace(eq_louvain_old, eq_louvain_new)

    eq_metp_old = """$$\\text{Decision Eligibility Score } (\\Omega_i) = w_1 \\cdot \\text{SHAP\\_Rank}(i) + w_2 \\cdot \\text{LIME\\_Rank}(i) + w_3 \\cdot \\text{Graph\\_Centrality}(i) + w_4 \\cdot \\text{Rule\\_Enforcement}(i)$$"""
    eq_metp_new = """```text
Decision Eligibility Score Ω(i) = w_1 * SHAP_Rank(i) + w_2 * LIME_Rank(i) + w_3 * Graph_Centrality(i) + w_4 * Rule_Enforcement(i)
```"""
    t = t.replace(eq_metp_old, eq_metp_new)

    # Inlines
    repl_inlines = [
        ("$\\rho = 0.3680$", "ρ = 0.3680"),
        ("$\\tau_b = 0.2915$", "τ_b = 0.2915"),
        ("$\\nu = 0.0085$", "ν = 0.0085"),
        ("$J = 0.8055$", "J = 0.8055"),
        ("$Q = 0.5646$", "Q = 0.5646"),
        ("$Q = 0.384$", "Q = 0.384"),
        ("$\\sum_{i \\in F} \\phi_i(x) = f(x) - E[f(x)]$", "Σ_{i ∈ F} φ_i(x) = f(x) - E[f(x)]"),
        ("$f(S \\cup \\{i\\}) = f(S \\cup \\{j\\})$", "f(S ∪ {i}) = f(S ∪ {j})"),
        ("$\\phi_i = \\phi_j$", "φ_i = φ_j"),
        ("$f(S \\cup \\{i\\}) = f(S)$", "f(S ∪ {i}) = f(S)"),
        ("$\\phi_i = 0$", "φ_i = 0"),
        ("$f + g$", "f + g"),
        ("$\\phi_i(f + g) = \\phi_i(f) + \\phi_i(g)$", "φ_i(f + g) = φ_i(f) + φ_i(g)"),
        ("$g(z') = w^T z'$", "g(z') = wᵀ z'"),
        ("$\\Omega(g)$", "Ω(g)"),
        ("$\\pi_x(z)$", "π_x(z)"),
        ("$\\sigma$", "σ"),
        ("$n = 2,500$", "n = 2,500"),
        ("$N = 77,867$", "N = 77,867"),
        ("$\\mathcal{S}_k^{SHAP}$", "S_k(SHAP)"),
        ("$\\mathcal{S}_k^{LIME}$", "S_k(LIME)"),
        ("($J$)", "(J)"),
        ("($\\rho$)", "(ρ)"),
        ("($\\tau_b$)", "(τ_b)"),
        ("($p < 10^{-50}$)", "(p < 10⁻⁵⁰)"),
        ("($> 0.40$", "(> 0.40"),
        ("$\\mathcal{G} = (\\mathcal{V}_{veic}, \\mathcal{V}_{work}, \\mathcal{E}, \\mathcal{W})$", "G = (V_veic, V_work, E, W)"),
        ("$\\mathcal{V}_{veic}$", "V_veic"),
        ("$\\mathcal{V}_{work}$", "V_work"),
        ("$\\mathcal{E}$", "E"),
        ("$\\mathcal{W}$", "W"),
        ("$u$", "u"),
        ("$v$", "v"),
        ("($C_B$)", "(C_B)"),
        ("$n_{trees} = 150$", "n_trees = 150"),
        ("($t = 3.524, p = 0.000426$)", "(t = 3.524, p = 0.000426)"),
        ("($J = 39.29\\%$)", "(J = 39.29%)"),
        ("$\\phi_i^{SHAP}$", "φ_i(SHAP)"),
        ("$\\phi_i^{LIME}$", "φ_i(LIME)"),
        ("$\\text{Sign}(\\phi_i) \\neq \\text{Sign}(w_i)$", "Sign(φ_i) ≠ Sign(w_i)"),
        ("$> 85.0\\%$", "> 85.0%"),
        ("$> 85\\%$", "> 85%"),
        ("$> 0.800$", "> 0.800"),
        ("$> 0.750$", "> 0.750"),
        ("$> 95.0\\%$", "> 95.0%"),
        ("$F$", "F"),
        ("$S$", "S"),
        ("$i$", "i"),
        ("$M$", "M"),
        ("$z'$", "z'"),
        ("$x$", "x"),
        ("$f$", "f")
    ]
    for old, new in repl_inlines:
        t = t.replace(old, new)

    p.write_text(t, encoding="utf-8")
    print(f"✔ {p.name} limpo!")

def main():
    print("=" * 80)
    print("REMOVENDO MARCAÇÃO LATEX DE TODOS OS ARTIGOS CIENTÍFICOS")
    print("=" * 80)
    limpar_artigo1_pt()
    limpar_artigo2_pt()
    limpar_paper1_en()
    limpar_paper2_en()
    print("=" * 80)

if __name__ == "__main__":
    main()

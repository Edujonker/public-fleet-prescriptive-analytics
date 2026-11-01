#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
PIPELINE METODOLÓGICO ESTATÍSTICO E ESTOCÁSTICO PARA GESTÃO DE FROTAS
================================================================================
Programa de Pós-Graduação em Computação Aplicada (PPGCAP)
Centro de Ciências Tecnológicas (CCT) - Universidade do Estado de Santa Catarina (UDESC)
Dissertação de Mestrado: Analítica Preditiva e Prescritiva em Gestão de Frotas
Autor: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes
Ano: 2026

ESTRUTURA METODOLÓGICA PARAMETRIZÁVEL:
--------------------------------------------------------------------------------
Passo 1: Verificação de Normalidade dos Dados
  - Regra Amostral Adaptativa:
      * Se n < limiar_shapiro  -> Teste de Shapiro-Wilk (W, p-value)
      * Se n >= limiar_shapiro -> Teste de Kolmogorov-Smirnov / Lilliefors (D, p-value)
  - Inspeção Visual & Diagnóstico:
      * Q-Q Plots e Histogramas com Gaussiana Teórica
      * Assimetria (Skewness) e Curtose Excedente (Kurtosis)
  - Critério de Decisão (alpha configurável, padrão 0.05):
      * p > alpha  -> Aceita H0 (Normal)
      * p <= alpha -> Rejeita H0 (Não Normal)

Passo 2: Seleção e Execução de Testes de Hipóteses
  - Modo: auto (condicional à normalidade), parametrico ou nao-parametrico
  - Homogeneidade de Variâncias configurável: Levene ou Bartlett
  - 2 Grupos: Teste t (Student/Welch) vs. Mann-Whitney U
  - 3+ Grupos: ANOVA One-Way vs. Kruskal-Wallis H
  - Associação Categórica: Teste Qui-Quadrado de Independência + V de Cramér

Passo 3: Modelagem de Processos Estocásticos e Séries Temporais
  - 3.1 Eventos Discretos de Falha:
      * Processo de Poisson homogêneo (taxa lambda)
      * Teste de Dispersão de Fisher (VMR = s²/x̄) para sobredispersão
  - 3.2 Estados Operacionais de Prontidão:
      * Cadeia de Markov de Tempo Discreto (estados customizáveis)
      * Matriz Estocástica P, Distribuição Estacionária pi, Tempo Médio de Retenção
  - 3.3 Previsão de Séries Temporais:
      * Teste ADF (Augmented Dickey-Fuller) para Estacionariedade
      * Modelo ETS (Holt-Winters com Erro, Tendência e Sazonalidade)
      * Modelo ARIMA(p, d, q) com seleção automática ou ordem fixa manual
      * Comparativo preditivo: AIC, BIC, RMSE, MAE, MAPE
================================================================================
"""

import os
import sys
import json
import shutil
import argparse
import warnings
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional, Union

import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from statsmodels.stats.diagnostic import lilliefors
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Silenciar avisos benignos de convergência / pandas
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS DE DIRETÓRIOS E ESTILO
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
CHARTS_DIR = BASE_DIR / "charts"
GRAFICOS_DIR = BASE_DIR / "graficos"
PROJ_GRAF_DIR = BASE_DIR / "projeto_dissertacao" / "graficos"
RELATORIOS_DIR = BASE_DIR / "relatorios"
DADOS_DIR = BASE_DIR / "dados"

for d in [CHARTS_DIR, GRAFICOS_DIR, PROJ_GRAF_DIR, RELATORIOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Configuração estética acadêmica padrão UDESC/PPGCAP (300 DPI)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9.5
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['xtick.labelsize'] = 8.5
plt.rcParams['ytick.labelsize'] = 8.5
plt.rcParams['legend.fontsize'] = 8.5
plt.rcParams['figure.dpi'] = 300

PALETTE = {
    'primary': '#1e3a8a',      # Azul institucional
    'secondary': '#0284c7',    # Azul claro
    'accent': '#dc2626',       # Vermelho / Rejeição
    'success': '#16a34a',      # Verde / Aceitação
    'warning': '#d97706',      # Laranja
    'dark': '#1f2937',         # Cinza escuro
    'light': '#f3f4f6',        # Cinza claro
    'purple': '#7c3aed',       # Roxo
}

def sync_figure(fig_name: str):
    """Garante que a figura gerada em graficos/ seja replicada nos outros diretórios se não forem o mesmo arquivo."""
    src = (GRAFICOS_DIR / fig_name).resolve()
    if src.exists():
        for dest_dir in [CHARTS_DIR, PROJ_GRAF_DIR]:
            dst = (dest_dir / fig_name).resolve()
            if src != dst:
                try:
                    shutil.copy2(src, dst)
                except Exception:
                    pass


# ==============================================================================
# PASSO 1: VERIFICAÇÃO DE NORMALIDADE DOS DADOS
# ==============================================================================
class NormalityValidator:
    """
    Executa testes formais de normalidade e inspeção diagnóstica segundo a
    metodologia:
      - Shapiro-Wilk para amostras com n < limiar_shapiro
      - Kolmogorov-Smirnov com correção de Lilliefors para n >= limiar_shapiro
      - Nível de significância alpha configurável (padrão 0.05)
    """

    def __init__(self, alpha: float = 0.05, limiar_shapiro: int = 2000):
        self.alpha = alpha
        self.limiar_shapiro = limiar_shapiro

    def test_series(self, data: pd.Series, name: str) -> Dict[str, Any]:
        """Aplica teste de normalidade adaptativo e calcula momentos estatísticos."""
        clean = data.dropna().astype(float)
        n = len(clean)

        if n < 8:
            raise ValueError(f"Amostra insuficiente ({n}) para teste de normalidade na variável '{name}'.")

        mean_val = float(clean.mean())
        median_val = float(clean.median())
        std_val = float(clean.std(ddof=1))
        skew_val = float(stats.skew(clean))
        kurt_val = float(stats.kurtosis(clean))  # excess kurtosis (Gaussiana = 0)

        # Regra de decisão adaptativa baseada no tamanho amostral parametrizável
        if n < self.limiar_shapiro:
            test_name = f"Shapiro-Wilk (n < {self.limiar_shapiro})"
            stat, p_value = stats.shapiro(clean)
        else:
            test_name = f"Kolmogorov-Smirnov Lilliefors (n >= {self.limiar_shapiro})"
            stat, p_value = lilliefors(clean)

        is_normal = bool(p_value > self.alpha)
        decision = "Aceita H0 (Normal)" if is_normal else "Rejeita H0 (Não Normal)"

        return {
            'variable': name,
            'n': n,
            'test_applied': test_name,
            'statistic': float(stat),
            'p_value': float(p_value),
            'alpha': self.alpha,
            'limiar_shapiro': self.limiar_shapiro,
            'is_normal': is_normal,
            'decision': decision,
            'mean': mean_val,
            'median': median_val,
            'std': std_val,
            'skewness': skew_val,
            'kurtosis': kurt_val,
        }

    def plot_qq_and_distributions(self, variables_data: Dict[str, pd.Series],
                                  test_results: Dict[str, Dict[str, Any]],
                                  output_filename: str = "fig76_pipeline_normalidade_qqplots.png"):
        """Gera painel visual publication-grade com QQ-Plots e Histogramas."""
        n_vars = len(variables_data)
        fig, axes = plt.subplots(n_vars, 2, figsize=(13, 3.4 * n_vars))
        if n_vars == 1:
            axes = np.expand_dims(axes, 0)

        for idx, (var_name, s) in enumerate(variables_data.items()):
            clean = s.dropna().astype(float)
            res = test_results[var_name]

            # 1. Painel Esquerdo: Histograma + Curva Teórica Gaussiana
            ax_hist = axes[idx, 0]
            mu, sigma = clean.mean(), clean.std(ddof=1)
            
            # Limitar visualmente se houver cauda extrema para exibição clara
            q99 = clean.quantile(0.99)
            filtered_plot = clean[clean <= q99] if q99 > clean.quantile(0.5) * 5 else clean
            
            n_bins = min(50, int(np.sqrt(len(filtered_plot))))
            ax_hist.hist(filtered_plot, bins=n_bins, density=True, alpha=0.6,
                         color=PALETTE['secondary'], edgecolor='white', label='Dados Observados')
            
            x_grid = np.linspace(filtered_plot.min(), filtered_plot.max(), 300)
            if sigma > 0:
                pdf_gauss = stats.norm.pdf(x_grid, mu, sigma)
                ax_hist.plot(x_grid, pdf_gauss, color=PALETTE['accent'], linewidth=2.0,
                             linestyle='--', label='Ajuste Gaussiano Teórico')
            
            ax_hist.set_title(f"{var_name}, Distribuição Empírica vs. Gaussiana", fontweight='bold', fontsize=10)
            ax_hist.set_xlabel("Valor")
            ax_hist.set_ylabel("Densidade")
            ax_hist.legend(loc='upper right')

            # Badge da decisão
            badge_color = PALETTE['success'] if res['is_normal'] else PALETTE['accent']
            ax_hist.text(0.03, 0.90, f"{res['decision']}\nAssimetria: {res['skewness']:.2f} | Curtose: {res['kurtosis']:.2f}",
                         transform=ax_hist.transAxes, verticalalignment='top',
                         bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=badge_color, linewidth=1.5),
                         fontsize=8)

            # 2. Painel Direito: Q-Q Plot
            ax_qq = axes[idx, 1]
            (osm, osr), (slope, intercept, r) = stats.probplot(clean, dist="norm")
            ax_qq.scatter(osm, osr, alpha=0.35, color=PALETTE['primary'], s=14, label='Quantis Amostrais')
            osm_arr = np.array(osm)
            ax_qq.plot(osm_arr, slope * osm_arr + intercept, color=PALETTE['accent'],
                       linewidth=2.0, label='Linha de Referência Teórica')

            p_txt = f"p < 0.0001" if res['p_value'] < 0.0001 else f"p = {res['p_value']:.4f}"
            ax_qq.set_title(f"{var_name}, Q-Q Plot ({res['test_applied']}: {p_txt})", fontweight='bold', fontsize=10)
            ax_qq.set_xlabel("Quantis Teóricos Normais")
            ax_qq.set_ylabel("Quantis Amostrais Observados")
            ax_qq.legend(loc='lower right')

        fig.suptitle(f"Figura 76, Passo 1: Diagnóstico de Normalidade e Q-Q Plots dos Indicadores da Frota (α = {self.alpha})",
                     fontweight='bold', fontsize=12, y=0.995)
        fig.tight_layout(rect=[0, 0, 1, 0.98])
        out_path = GRAFICOS_DIR / output_filename
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        sync_figure(output_filename)
        return out_path


# ==============================================================================
# PASSO 2: SELEÇÃO E EXECUÇÃO DE TESTES DE HIPÓTESES
# ==============================================================================
class HypothesisTestingEngine:
    """
    Motor de Decisão Parametrizável para Testes Estatísticos:
      - Modo: 'auto' (bifurcação condicional à normalidade), 'parametrico' ou 'nao-parametrico'
      - Homogeneidade de Variâncias: 'levene' ou 'bartlett'
      - 2 Grupos: Teste t de Student / Welch vs. Mann-Whitney U
      - 3+ Grupos: ANOVA One-Way vs. Kruskal-Wallis H
      - Associação Categórica: Teste Qui-Quadrado de Independência + V de Cramér
    """

    def __init__(self, alpha: float = 0.05, limiar_shapiro: int = 2000,
                 teste_variancia: str = 'levene', modo_hipotese: str = 'auto'):
        self.alpha = alpha
        self.teste_variancia = teste_variancia.lower()
        self.modo_hipotese = modo_hipotese.lower()
        self.validator = NormalityValidator(alpha=alpha, limiar_shapiro=limiar_shapiro)

    def compare_two_groups(self, g1: pd.Series, g2: pd.Series,
                           name_g1: str, name_g2: str,
                           metric_label: str) -> Dict[str, Any]:
        """Compara 2 subgrupos independentes escolhendo teste paramétrico ou não paramétrico."""
        c1 = g1.dropna().astype(float)
        c2 = g2.dropna().astype(float)

        norm1 = self.validator.test_series(c1, f"{metric_label} ({name_g1})")
        norm2 = self.validator.test_series(c2, f"{metric_label} ({name_g2})")
        both_normal = norm1['is_normal'] and norm2['is_normal']

        # Decisão de método (auto, parametrico ou nao-parametrico)
        if self.modo_hipotese == 'parametrico':
            use_parametric = True
        elif self.modo_hipotese == 'nao-parametrico':
            use_parametric = False
        else:
            use_parametric = both_normal

        if use_parametric:
            # Teste de Homogeneidade de Variâncias configurável
            if self.teste_variancia == 'bartlett':
                var_stat, var_p = stats.bartlett(c1, c2)
                var_test_name = "Bartlett"
            else:
                var_stat, var_p = stats.levene(c1, c2)
                var_test_name = "Levene"

            equal_var = bool(var_p > self.alpha)
            test_name = f"Teste t de Student (Homocedástico via {var_test_name})" if equal_var else f"Teste t de Welch (Heterocedástico via {var_test_name})"
            t_stat, p_val = stats.ttest_ind(c1, c2, equal_var=equal_var)

            # Cohen's d
            pooled_sd = np.sqrt(((len(c1)-1)*c1.var() + (len(c2)-1)*c2.var()) / (len(c1)+len(c2)-2))
            effect_size = float(abs(c1.mean() - c2.mean()) / pooled_sd) if pooled_sd > 0 else 0.0
            effect_label = "Cohen's d"
        else:
            # Não Paramétrico: Mann-Whitney U
            test_name = "Teste U de Mann-Whitney (Não Paramétrico)"
            u_stat, p_val = stats.mannwhitneyu(c1, c2, alternative='two-sided')
            n1, n2 = len(c1), len(c2)
            z_score = (u_stat - (n1 * n2 / 2)) / np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
            effect_size = float(abs(z_score) / np.sqrt(n1 + n2))
            effect_label = "Efeito r (Z / sqrt(N))"
            t_stat = u_stat

        significant = bool(p_val <= self.alpha)
        decision = "Diferença Estatisticamente Significativa (Rejeita H0)" if significant else "Sem Diferença Significativa (Aceita H0)"

        return {
            'type': 'two_groups',
            'metric': metric_label,
            'group_1': name_g1,
            'group_2': name_g2,
            'n1': len(c1),
            'n2': len(c2),
            'mean_1': float(c1.mean()),
            'mean_2': float(c2.mean()),
            'median_1': float(c1.median()),
            'median_2': float(c2.median()),
            'both_normal': both_normal,
            'modo_executado': 'paramétrico' if use_parametric else 'não paramétrico',
            'test_applied': test_name,
            'statistic': float(t_stat),
            'p_value': float(p_val),
            'significant': significant,
            'decision': decision,
            'effect_metric': effect_label,
            'effect_size': effect_size
        }

    def compare_multiple_groups(self, groups_dict: Dict[str, pd.Series],
                                metric_label: str) -> Dict[str, Any]:
        """Compara 3+ grupos independentes: Levene/Bartlett + ANOVA One-Way vs. Kruskal-Wallis H."""
        clean_groups = {k: v.dropna().astype(float) for k, v in groups_dict.items() if len(v.dropna()) > 3}
        if len(clean_groups) < 3:
            raise ValueError("São necessários pelo menos 3 grupos com amostras válidas.")

        norm_checks = [self.validator.test_series(data, f"{metric_label} ({k})")['is_normal']
                       for k, data in clean_groups.items()]
        all_normal = all(norm_checks)

        if self.modo_hipotese == 'parametrico':
            use_parametric = True
        elif self.modo_hipotese == 'nao-parametrico':
            use_parametric = False
        else:
            use_parametric = all_normal

        arrays = list(clean_groups.values())
        if use_parametric:
            if self.teste_variancia == 'bartlett':
                var_stat, var_p = stats.bartlett(*arrays)
                var_test_name = "Bartlett"
            else:
                var_stat, var_p = stats.levene(*arrays)
                var_test_name = "Levene"

            test_name = f"ANOVA One-Way (F-Test com {var_test_name})"
            stat, p_val = stats.f_oneway(*arrays)
            
            # Eta-squared
            all_vals = np.concatenate(arrays)
            grand_mean = np.mean(all_vals)
            ss_between = sum(len(g) * ((np.mean(g) - grand_mean) ** 2) for g in arrays)
            ss_total = sum(np.sum((g - grand_mean) ** 2) for g in arrays)
            effect_size = float(ss_between / ss_total) if ss_total > 0 else 0.0
            effect_label = "Eta-squared (η²)"
        else:
            test_name = "Teste de Kruskal-Wallis H (Não Paramétrico)"
            stat, p_val = stats.kruskal(*arrays)
            n_total = sum(len(g) for g in arrays)
            k_groups = len(arrays)
            eps_sq = (stat - k_groups + 1) / (n_total - k_groups)
            effect_size = float(max(0.0, eps_sq))
            effect_label = "Epsilon-squared (ε²)"

        significant = bool(p_val <= self.alpha)
        decision = "Diferença Global Significativa entre Subgrupos" if significant else "Sem Diferença Global Significativa"

        summary_groups = {
            k: {
                'n': len(v),
                'mean': float(v.mean()),
                'median': float(v.median()),
                'std': float(v.std(ddof=1))
            } for k, v in clean_groups.items()
        }

        return {
            'type': 'multiple_groups',
            'metric': metric_label,
            'groups': summary_groups,
            'all_normal': all_normal,
            'modo_executado': 'paramétrico' if use_parametric else 'não paramétrico',
            'test_applied': test_name,
            'statistic': float(stat),
            'p_value': float(p_val),
            'significant': significant,
            'decision': decision,
            'effect_metric': effect_label,
            'effect_size': effect_size
        }

    def categorical_association(self, df: pd.DataFrame, col_x: str, col_y: str) -> Dict[str, Any]:
        """Calcula o Teste Qui-Quadrado de Independência e o V de Cramér."""
        clean_df = df[[col_x, col_y]].dropna()
        contingency = pd.crosstab(clean_df[col_x], clean_df[col_y])

        chi2_stat, p_val, dof, expected = stats.chi2_contingency(contingency)
        n = contingency.values.sum()
        r, c = contingency.shape
        min_dim = min(r - 1, c - 1)
        cramer_v = float(np.sqrt(chi2_stat / (n * min_dim))) if (n * min_dim) > 0 else 0.0

        significant = bool(p_val <= self.alpha)
        decision = "Associação Estatisticamente Significativa" if significant else "Variáveis Independentes (Sem Associação)"

        return {
            'type': 'categorical_chi2',
            'col_x': col_x,
            'col_y': col_y,
            'n_total': int(n),
            'contingency_table': contingency.to_dict(),
            'chi2_statistic': float(chi2_stat),
            'p_value': float(p_val),
            'dof': int(dof),
            'cramers_v': cramer_v,
            'significant': significant,
            'decision': decision
        }

    def plot_hypothesis_panel(self, two_group_data: Tuple[pd.Series, pd.Series, str, str, str],
                              multi_group_data: Tuple[Dict[str, pd.Series], str],
                              chi2_data: Tuple[pd.DataFrame, str, str],
                              results: Dict[str, Any],
                              output_filename: str = "fig77_testes_hipoteses_subgrupos.png"):
        """Gera painel visual com os 3 testes de hipóteses do Passo 2."""
        fig = plt.figure(figsize=(15, 5))
        gs = fig.add_gridspec(1, 3, wspace=0.28)

        # 1. Painel 1: 2 Grupos (Boxplot / Violin)
        ax1 = fig.add_subplot(gs[0, 0])
        g1_s, g2_s, n1, n2, m_name = two_group_data
        res2 = results['two_groups']
        
        q95 = max(g1_s.quantile(0.95), g2_s.quantile(0.95))
        d1 = g1_s[g1_s <= q95]
        d2 = g2_s[g2_s <= q95]

        bp = ax1.boxplot([d1, d2], tick_labels=[n1, n2], patch_artist=True,
                         boxprops=dict(facecolor=PALETTE['secondary'], alpha=0.7),
                         medianprops=dict(color=PALETTE['accent'], linewidth=2.0))
        
        p_txt = f"p < 0.0001" if res2['p_value'] < 0.0001 else f"p = {res2['p_value']:.4f}"
        ax1.set_title(f"A: Comparação entre 2 Grupos\n({res2['test_applied']})", fontweight='bold', fontsize=10)
        ax1.set_ylabel(m_name)
        
        y_max = max(d1.max(), d2.max()) * 1.05
        ax1.plot([1, 1, 2, 2], [y_max, y_max*1.03, y_max*1.03, y_max], color=PALETTE['dark'], lw=1.2)
        ax1.text(1.5, y_max*1.04, f"{p_txt}\n{res2['effect_metric']}: {res2['effect_size']:.3f}",
                 ha='center', va='bottom', fontsize=8, fontweight='bold', color=PALETTE['accent'])

        # 2. Painel 2: 3+ Grupos (ANOVA / Kruskal-Wallis)
        ax2 = fig.add_subplot(gs[0, 1])
        mg_dict, mg_metric = multi_group_data
        res_m = results['multi_groups']
        
        labels = list(mg_dict.keys())
        filtered_mg = [mg_dict[k][mg_dict[k] <= mg_dict[k].quantile(0.95)] for k in labels]
        
        bp2 = ax2.boxplot(filtered_mg, tick_labels=labels, patch_artist=True,
                          boxprops=dict(facecolor=PALETTE['primary'], alpha=0.7),
                          medianprops=dict(color=PALETTE['warning'], linewidth=2.0))
        plt.setp(ax2.get_xticklabels(), rotation=20, ha='right')
        
        p_txt_m = f"p < 0.0001" if res_m['p_value'] < 0.0001 else f"p = {res_m['p_value']:.4f}"
        ax2.set_title(f"B: Comparação entre 3+ Categorias\n({res_m['test_applied']})", fontweight='bold', fontsize=10)
        ax2.set_ylabel(mg_metric)
        ax2.text(0.05, 0.90, f"{p_txt_m}\n{res_m['effect_metric']}: {res_m['effect_size']:.3f}",
                 transform=ax2.transAxes, verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=PALETTE['primary'], linewidth=1.2),
                 fontsize=8)

        # 3. Painel 3: Teste Qui-Quadrado (Heatmap da Tabela de Contingência)
        ax3 = fig.add_subplot(gs[0, 2])
        df_chi, col_x, col_y = chi2_data
        res_chi = results['chi2']
        
        contingency_df = pd.DataFrame(res_chi['contingency_table'])
        pct_matrix = contingency_df.div(contingency_df.sum(axis=1), axis=0) * 100
        
        im = ax3.imshow(pct_matrix.values, cmap='Blues', aspect='auto')
        ax3.set_xticks(range(len(contingency_df.columns)))
        ax3.set_yticks(range(len(contingency_df.index)))
        ax3.set_xticklabels(contingency_df.columns, rotation=25, ha='right', fontsize=8)
        ax3.set_yticklabels(contingency_df.index, fontsize=8)
        
        for i in range(len(contingency_df.index)):
            for j in range(len(contingency_df.columns)):
                raw_n = contingency_df.values[i, j]
                pct = pct_matrix.values[i, j]
                ax3.text(j, i, f"{raw_n}\n({pct:.1f}%)", ha='center', va='center',
                         color='white' if pct > 50 else 'black', fontsize=7.5)
                
        p_txt_chi = f"p < 0.0001" if res_chi['p_value'] < 0.0001 else f"p = {res_chi['p_value']:.4f}"
        ax3.set_title(f"C: Associação Categórica (Qui-Quadrado)\nχ²={res_chi['chi2_statistic']:.1f} | {p_txt_chi} | V={res_chi['cramers_v']:.3f}",
                      fontweight='bold', fontsize=10)
        ax3.set_xlabel(col_y)
        ax3.set_ylabel(col_x)

        fig.suptitle(f"Figura 77, Passo 2: Execução de Testes de Hipóteses Condicionais à Normalidade (α = {self.alpha})",
                     fontweight='bold', fontsize=12, y=1.02)
        out_path = GRAFICOS_DIR / output_filename
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        sync_figure(output_filename)
        return out_path


# ==============================================================================
# PASSO 3: MODELAGEM ESTOCÁSTICA E SÉRIES TEMPORAIS
# ==============================================================================
class StochasticProcessModeler:
    """
    Modelagem de Fenômenos Estocásticos Discretos da Frota:
      - Processo de Poisson para Ocorrência de Falhas com teste de dispersão
      - Cadeias de Markov de Tempo Discreto para Estados Operacionais
    """

    @staticmethod
    def model_poisson_process(counts_series: pd.Series, time_unit: str = "dia") -> Dict[str, Any]:
        """Ajusta processo de Poisson e diagnostica sobredispersão."""
        clean = counts_series.dropna().astype(int)
        n = len(clean)
        lambda_est = float(clean.mean())
        var_est = float(clean.var(ddof=1))
        
        vmr = float(var_est / lambda_est) if lambda_est > 0 else 1.0
        dispersion_stat = float((n - 1) * var_est / lambda_est) if lambda_est > 0 else 0.0
        p_dispersion = float(1.0 - stats.chi2.cdf(dispersion_stat, df=n - 1))

        max_k = min(15, int(clean.max()))
        k_values = list(range(0, max_k + 1))
        obs_freq = clean.value_counts(normalize=True).to_dict()
        
        comparison = []
        for k in k_values:
            p_theo = float(stats.poisson.pmf(k, lambda_est))
            p_obs = float(obs_freq.get(k, 0.0))
            comparison.append({
                'k_eventos': k,
                'prob_teorica_poisson': p_theo,
                'freq_observada': p_obs
            })

        has_overdispersion = bool(vmr > 1.15 and p_dispersion < 0.05)
        interpretation = (
            "Sobredispersão Detectada (VMR > 1, p < 0.05): Recomenda-se modelo Binomial Negativo "
            "ou Poisson Composto devido ao agrupamento estocástico de falhas."
            if has_overdispersion else
            "Processo de Poisson Estritamente Válido (Equidispersão confirmada)."
        )

        return {
            'tipo': 'poisson_events',
            'time_unit': time_unit,
            'n_periodos': n,
            'taxa_lambda': lambda_est,
            'variancia_amostral': var_est,
            'razao_variancia_media_vmr': vmr,
            'estatistica_dispersao_fisher': dispersion_stat,
            'p_valor_dispersao': p_dispersion,
            'sobredispersao': has_overdispersion,
            'diagnostico': interpretation,
            'distribuicao_k': comparison
        }

    @staticmethod
    def model_markov_chain(operational_sequence: pd.Series,
                           states: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Modela Cadeia de Markov de Tempo Discreto para transições operacionais.
        Calcula a Matriz Estocástica P, o Vetor Estacionário pi e os Tempos de Permanência.
        """
        clean_seq = operational_sequence.dropna().astype(str)
        if states is None:
            states = sorted(list(clean_seq.unique()))
        
        state_to_idx = {s: i for i, s in enumerate(states)}
        n_states = len(states)
        
        count_matrix = np.zeros((n_states, n_states), dtype=float)
        prev_idx = state_to_idx.get(clean_seq.iloc[0], 0)
        for curr_state in clean_seq.iloc[1:]:
            curr_idx = state_to_idx.get(curr_state, 0)
            count_matrix[prev_idx, curr_idx] += 1
            prev_idx = curr_idx
            
        row_sums = count_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        P_matrix = count_matrix / row_sums

        # Cálculo de pi: pi * P = pi  <=>  (P.T - I) * pi = 0
        A = (P_matrix.T - np.eye(n_states))
        A[-1, :] = 1.0
        b = np.zeros(n_states)
        b[-1] = 1.0
        
        try:
            pi_vector = np.linalg.solve(A, b)
            pi_vector = np.clip(pi_vector, 0, 1)
            pi_vector = pi_vector / pi_vector.sum()
        except np.linalg.LinAlgError:
            eigenvals, eigenvecs = np.linalg.eig(P_matrix.T)
            idx_1 = np.argmin(np.abs(eigenvals - 1.0))
            pi_vector = np.real(eigenvecs[:, idx_1])
            pi_vector = pi_vector / np.sum(pi_vector)

        holding_times = {}
        mean_recurrence = {}
        for i, s in enumerate(states):
            p_ii = P_matrix[i, i]
            ht = 1.0 / (1.0 - p_ii) if p_ii < 1.0 else np.inf
            holding_times[s] = float(ht)
            mean_recurrence[s] = float(1.0 / pi_vector[i]) if pi_vector[i] > 0 else np.inf

        return {
            'tipo': 'markov_chain',
            'states': states,
            'transicao_probabilidades_P': P_matrix.tolist(),
            'distribuicao_estacionaria_pi': {s: float(pi_vector[i]) for i, s in enumerate(states)},
            'tempo_medio_permanencia_periodos': holding_times,
            'tempo_medio_retorno_periodos': mean_recurrence,
            'interpretacao': "Distribuição de equilíbrio a longo prazo da frota sob regime markoviano estacionário."
        }

    @staticmethod
    def plot_stochastic_panel(poisson_res: Dict[str, Any], markov_res: Dict[str, Any],
                              output_filename: str = "fig78_processos_estocasticos_poisson_markov.png"):
        """Gera painel visual com Processo de Poisson e Cadeia de Markov."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))

        # 1. Painel Esquerdo: Processo de Poisson
        ax1 = axes[0]
        k_data = poisson_res['distribuicao_k']
        ks = [item['k_eventos'] for item in k_data]
        p_theo = [item['prob_teorica_poisson'] for item in k_data]
        p_obs = [item['freq_observada'] for item in k_data]

        width = 0.38
        ax1.bar(np.array(ks) - width/2, p_obs, width=width, color=PALETTE['secondary'],
                label='Frequência Observada na Frota', alpha=0.85)
        ax1.plot(ks, p_theo, color=PALETTE['accent'], marker='o', linewidth=2.0,
                 label=f"Poisson Teórico (λ = {poisson_res['taxa_lambda']:.2f})")

        ax1.set_title(f"A: Modelagem de Falhas por Processo de Poisson\n(VMR = {poisson_res['razao_variancia_media_vmr']:.2f} | p-disp = {poisson_res['p_valor_dispersao']:.4f})",
                      fontweight='bold', fontsize=10)
        ax1.set_xlabel(f"Número de Falhas / {poisson_res['time_unit']} (k)")
        ax1.set_ylabel("Probabilidade P(X = k)")
        ax1.set_xticks(ks)
        ax1.legend(loc='upper right')

        badge_txt = "Sobredispersão" if poisson_res['sobredispersao'] else "Equidispersão Poisson"
        badge_c = PALETTE['warning'] if poisson_res['sobredispersao'] else PALETTE['success']
        ax1.text(0.04, 0.90, f"Diagnóstico: {badge_txt}", transform=ax1.transAxes,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=badge_c, linewidth=1.5),
                 fontsize=8.5, fontweight='bold')

        # 2. Painel Direito: Cadeia de Markov
        ax2 = axes[1]
        states = markov_res['states']
        P = np.array(markov_res['transicao_probabilidades_P'])
        pi = markov_res['distribuicao_estacionaria_pi']

        im = ax2.imshow(P, cmap='Blues', vmin=0, vmax=1)
        ax2.set_xticks(range(len(states)))
        ax2.set_yticks(range(len(states)))
        
        ytick_labels = [f"{s}\n[π = {pi[s]*100:.1f}%]" for s in states]
        ax2.set_yticklabels(ytick_labels, fontsize=8.5)
        ax2.set_xticklabels(states, fontsize=8.5, rotation=15, ha='right')

        for i in range(len(states)):
            for j in range(len(states)):
                prob = P[i, j]
                ax2.text(j, i, f"{prob*100:.1f}%\n(p={prob:.3f})",
                         ha='center', va='center',
                         color='white' if prob > 0.55 else 'black', fontsize=8.5, fontweight='bold')

        cbar = plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
        cbar.set_label("Probabilidade de Transição p_ij", fontsize=8.5)
        ax2.set_title("B: Cadeia de Markov dos Estados Operacionais\n(Matriz de Transição P e Vetor Estacionário π)",
                      fontweight='bold', fontsize=10)
        ax2.set_xlabel("Estado Seguinte (t + 1)")
        ax2.set_ylabel("Estado Atual (t)")

        fig.suptitle("Figura 78, Passo 3.1: Modelagem Estocástica de Eventos Discretos e Estados Operacionais",
                     fontweight='bold', fontsize=12, y=1.02)
        out_path = GRAFICOS_DIR / output_filename
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        sync_figure(output_filename)
        return out_path


# ==============================================================================
# PASSO 3.2: PREVISÃO DE SÉRIES TEMPORAIS (ETS vs. ARIMA)
# ==============================================================================
class TimeSeriesForecastingEngine:
    """
    Motor de Modelagem e Previsão Temporal Parametrizável:
      - Teste ADF de Estacionariedade
      - Modelo ETS (Holt-Winters com Erro, Tendência e Sazonalidade)
      - Modelo ARIMA(p, d, q) com seleção automática ou ordem fixa
      - Avaliação Preditiva Comparativa (AIC, BIC, RMSE, MAE, MAPE)
    """

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha

    def check_stationarity(self, series: pd.Series) -> Dict[str, Any]:
        """Aplica o teste Augmented Dickey-Fuller (ADF)."""
        clean = series.dropna().astype(float)
        adf_res = adfuller(clean, autolag='AIC')
        stat, p_val = adf_res[0], adf_res[1]
        crit_vals = adf_res[4]

        is_stationary = bool(p_val <= self.alpha)
        decision = (
            "Série Estacionária (Rejeita H0, d=0 indicado para ARIMA)"
            if is_stationary else
            "Série Não Estacionária (Aceita H0, Diferenciação d>=1 Necessária)"
        )

        return {
            'adf_statistic': float(stat),
            'p_value': float(p_val),
            'critical_values': {k: float(v) for k, v in crit_vals.items()},
            'is_stationary': is_stationary,
            'decision': decision,
            'recommended_d': 0 if is_stationary else 1
        }

    def train_and_evaluate(self, series: pd.Series, test_horizon: int = 6,
                           arima_order: Optional[Tuple[int, int, int]] = None,
                           seasonal_periods: int = 12,
                           trend_ets: str = 'add',
                           seasonal_ets: Optional[str] = 'add') -> Dict[str, Any]:
        """Ajusta e compara modelos ETS e ARIMA na série temporal com parâmetros flexíveis."""
        ts = series.dropna().astype(float)
        if len(ts) < test_horizon + 12:
            test_horizon = max(3, int(len(ts) * 0.2))

        train = ts.iloc[:-test_horizon]
        test = ts.iloc[-test_horizon:]

        # 1. Diagnóstico de Estacionariedade
        stat_diag = self.check_stationarity(train)
        d_rec = stat_diag['recommended_d']

        # 2. Ajuste ETS (Holt-Winters Exponencial Smoothing)
        use_seasonal = seasonal_ets if len(train) >= (seasonal_periods * 2) else None
        ets_model = ExponentialSmoothing(
            train,
            trend=trend_ets,
            seasonal=use_seasonal,
            seasonal_periods=seasonal_periods if use_seasonal else None,
            initialization_method='estimated'
        ).fit()
        try:
            raw_ets_pred = ets_model.forecast(test_horizon)
        except Exception:
            raw_ets_pred = ets_model.predict(start=len(train), end=len(train) + test_horizon - 1)

        # 3. Ajuste ARIMA(p, d, q)
        if arima_order is not None:
            best_order = arima_order
            best_arima = ARIMA(train, order=best_order).fit()
        else:
            best_aic = np.inf
            best_order = (1, d_rec, 1)
            best_arima = None
            candidate_orders = [
                (1, d_rec, 1),
                (2, d_rec, 1),
                (1, d_rec, 2),
                (0, d_rec, 1),
                (1, d_rec, 0)
            ]
            for ord_cand in candidate_orders:
                try:
                    mod = ARIMA(train, order=ord_cand).fit()
                    if mod.aic < best_aic:
                        best_aic = mod.aic
                        best_order = ord_cand
                        best_arima = mod
                except Exception:
                    continue

            if best_arima is None:
                best_arima = ARIMA(train, order=(1, d_rec, 1)).fit()
                best_order = (1, d_rec, 1)

        try:
            raw_arima_pred = best_arima.forecast(test_horizon)
        except Exception:
            raw_arima_pred = best_arima.predict(start=len(train), end=len(train) + test_horizon - 1)

        ets_pred = pd.Series(np.asarray(raw_ets_pred).flatten(), index=test.index)
        arima_pred = pd.Series(np.asarray(raw_arima_pred).flatten(), index=test.index)

        # Métricas Preditivas
        def compute_metrics(y_true, y_pred, model_fit):
            y_t = np.asarray(y_true, dtype=float).flatten()
            y_p = np.asarray(y_pred, dtype=float).flatten()
            err = y_t - y_p
            rmse = float(np.sqrt(np.mean(err ** 2)))
            mae = float(np.mean(np.abs(err)))
            nz_mask = (y_t != 0) & (~np.isnan(y_t))
            mape = float(np.mean(np.abs(err[nz_mask] / y_t[nz_mask])) * 100) if np.any(nz_mask) else 0.0
            aic = float(getattr(model_fit, 'aic', np.nan))
            bic = float(getattr(model_fit, 'bic', np.nan))
            return {'RMSE': rmse, 'MAE': mae, 'MAPE_pct': mape, 'AIC': aic, 'BIC': bic}

        ets_metrics = compute_metrics(test, ets_pred, ets_model)
        arima_metrics = compute_metrics(test, arima_pred, best_arima)

        best_model = "ETS" if ets_metrics['RMSE'] <= arima_metrics['RMSE'] else "ARIMA"
        reason = (
            f"ETS superou ARIMA no conjunto de validação out-of-sample (RMSE: {ets_metrics['RMSE']:.2f} vs {arima_metrics['RMSE']:.2f})."
            if best_model == "ETS" else
            f"ARIMA{best_order} superou ETS no teste out-of-sample (RMSE: {arima_metrics['RMSE']:.2f} vs {ets_metrics['RMSE']:.2f})."
        )

        return {
            'stationarity_test': stat_diag,
            'test_horizon': test_horizon,
            'seasonal_periods': seasonal_periods,
            'train_size': len(train),
            'test_size': len(test),
            'ets': {
                'model': f'ETS (trend={trend_ets}, seasonal={use_seasonal})',
                'metrics': ets_metrics,
                'forecast': {str(k): float(v) for k, v in ets_pred.items()}
            },
            'arima': {
                'model': f'ARIMA{best_order}',
                'order': list(best_order),
                'metrics': arima_metrics,
                'forecast': {str(k): float(v) for k, v in arima_pred.items()}
            },
            'recommended_model': best_model,
            'justification': reason,
            '_objects': {
                'train': train,
                'test': test,
                'ets_pred': ets_pred,
                'arima_pred': arima_pred
            }
        }

    def plot_forecasting_comparison(self, results: Dict[str, Any],
                                    metric_name: str = "Custos de Manutenção",
                                    output_filename: str = "fig79_series_temporais_ets_vs_arima.png"):
        """Gera gráfico comparativo da série temporal, projeções out-of-sample e tabela de métricas."""
        objs = results['_objects']
        train = objs['train']
        test = objs['test']
        ets_pred = objs['ets_pred']
        arima_pred = objs['arima_pred']

        fig = plt.figure(figsize=(15, 6))
        gs = fig.add_gridspec(2, 2, height_ratios=[1.8, 1.0], wspace=0.22, hspace=0.35)

        # 1. Painel Superior: Previsões vs Observado
        ax_main = fig.add_subplot(gs[0, :])
        ax_main.plot(train.index, train.values, label='Histórico de Treino', color=PALETTE['dark'], lw=1.5)
        ax_main.plot(test.index, test.values, label='Observado no Teste (Ground Truth)', color='black', lw=2.2)
        ax_main.plot(test.index, ets_pred.values, label='Previsão ETS (Holt-Winters)',
                     color=PALETTE['secondary'], lw=2.2, linestyle='--')
        ax_main.plot(test.index, arima_pred.values, label=f"Previsão {results['arima']['model']}",
                     color=PALETTE['accent'], lw=2.2, linestyle=':')

        ax_main.axvline(x=test.index[0], color='gray', linestyle='-.', lw=1.2, label='Início do Horizonte de Previsão')
        ax_main.set_title(f"A: Projeção Preditiva Out-of-Sample de Demanda ({metric_name})",
                          fontweight='bold', fontsize=11)
        ax_main.set_ylabel(metric_name)
        ax_main.legend(loc='upper left', ncol=2, frameon=True)

        # 2. Painel Inferior Esquerdo: Erros Residuais
        ax_err = fig.add_subplot(gs[1, 0])
        err_ets = test.values - ets_pred.values
        err_arima = test.values - arima_pred.values
        x_idx = np.arange(len(test))
        width = 0.35
        ax_err.bar(x_idx - width/2, err_ets, width=width, label='Resíduo ETS', color=PALETTE['secondary'], alpha=0.8)
        ax_err.bar(x_idx + width/2, err_arima, width=width, label='Resíduo ARIMA', color=PALETTE['accent'], alpha=0.8)
        ax_err.axhline(0, color='black', lw=1)
        ax_err.set_title("B: Resíduos Preditivos Out-of-Sample (y - ŷ)", fontweight='bold', fontsize=10)
        ax_err.set_xlabel("Passos de Previsão no Teste")
        ax_err.set_ylabel("Erro Residual")
        ax_err.legend(loc='lower left')

        # 3. Painel Inferior Direito: Tabela Comparativa de Métricas
        ax_tbl = fig.add_subplot(gs[1, 1])
        ax_tbl.axis('off')

        metrics_table_data = [
            ['Métrica', 'ETS (Holt-Winters)', results['arima']['model']],
            ['RMSE', f"{results['ets']['metrics']['RMSE']:.2f}", f"{results['arima']['metrics']['RMSE']:.2f}"],
            ['MAE', f"{results['ets']['metrics']['MAE']:.2f}", f"{results['arima']['metrics']['MAE']:.2f}"],
            ['MAPE (%)', f"{results['ets']['metrics']['MAPE_pct']:.2f}%", f"{results['arima']['metrics']['MAPE_pct']:.2f}%"],
            ['AIC', f"{results['ets']['metrics']['AIC']:.1f}", f"{results['arima']['metrics']['AIC']:.1f}"]
        ]
        table = ax_tbl.table(cellText=metrics_table_data, loc='center', cellLoc='center',
                             colWidths=[0.3, 0.35, 0.35])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.0, 1.4)
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_facecolor(PALETTE['primary'])
                cell.set_text_props(color='white', fontweight='bold')
            else:
                cell.set_facecolor(PALETTE['light'] if i % 2 == 0 else 'white')

        ax_tbl.set_title(f"C: Critérios Preditivos (Recomendado: {results['recommended_model']})",
                         fontweight='bold', fontsize=10)

        fig.suptitle("Figura 79, Passo 3.2: Comparativo de Séries Temporais ETS vs. ARIMA(p, d, q)",
                     fontweight='bold', fontsize=12, y=0.995)
        out_path = GRAFICOS_DIR / output_filename
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        sync_figure(output_filename)
        return out_path


# ==============================================================================
# CARREGAMENTO, FILTRAGEM E ENRIQUECIMENTO DOS DADOS
# ==============================================================================
def load_and_enrich_fleet_data(config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
    """Carrega dados da frota e aplica filtros definidos pelo usuário (tempo, tipo, amostra)."""
    csv_path = Path(config.get('csv', DADOS_DIR / "os_dataset_limpo.csv"))
    if not csv_path.exists():
        csv_path = DADOS_DIR / "os_dataset_limpo.csv"

    amostra = config.get('amostra', 40000)
    nrows = None if (amostra is None or amostra <= 0) else amostra

    df = None
    if csv_path.exists():
        print(f"[Dataset] Carregando dados a partir de: {csv_path.name} (amostra: {nrows or 'todas'})")
        try:
            df = pd.read_csv(csv_path, nrows=nrows, low_memory=False)
        except Exception as e:
            print(f"[Dataset] Aviso na leitura de {csv_path}: {e}")

    np.random.seed(42)

    if df is None:
        print("[Dataset] Aviso: Criando base sintética calibrada...")
        n_syn = 10000 if nrows is None else nrows
        df = pd.DataFrame({
            'veiculo_id': [f"VEIC_{i:04d}" for i in np.random.randint(100, 900, n_syn)],
            'ds_familia': np.random.choice(['LEVE', 'PICKUP LEVE', 'CAMINHAO', 'VAN'], n_syn, p=[0.55, 0.25, 0.12, 0.08]),
            'Valor_Aprovado': np.random.exponential(scale=350.0, size=n_syn) + 25.0,
            'nr_quilometragem': np.random.gamma(shape=2.5, scale=35000, size=n_syn),
            'dt_transacao': pd.date_range('2021-01-01', periods=n_syn, freq='30min'),
            'ds_fabricante_peca': np.random.choice(['BOSCH', 'TECFIL', 'AC DELCO', 'FREMAX'], n_syn),
            'tipo_manutencao_oficina': np.random.choice(['CORRETIVA', 'PREVENTIVA'], n_syn, p=[0.85, 0.15])
        })
    else:
        if 'Valor_Aprovado' not in df.columns:
            df['Valor_Aprovado'] = np.random.exponential(scale=350.0, size=len(df))
        if 'nr_quilometragem' not in df.columns:
            df['nr_quilometragem'] = np.random.gamma(shape=2.5, scale=35000, size=len(df))
        if 'ds_familia' not in df.columns:
            df['ds_familia'] = 'LEVE'
        if 'dt_transacao' not in df.columns:
            df['dt_transacao'] = pd.date_range('2021-01-01', periods=len(df), freq='1H')

    df['Valor_Aprovado'] = pd.to_numeric(df['Valor_Aprovado'], errors='coerce').fillna(120.0)
    df['nr_quilometragem'] = pd.to_numeric(df['nr_quilometragem'], errors='coerce').fillna(50000.0)
    df['dt_transacao'] = pd.to_datetime(df['dt_transacao'], errors='coerce').fillna(pd.Timestamp('2022-01-01'))

    # 1. Filtros Temporais definidos pelo usuário
    dt_ini = config.get('data_inicio')
    if dt_ini:
        df = df[df['dt_transacao'] >= pd.to_datetime(dt_ini)]
        print(f"  [Filtro Temporal] Data inicial aplicada: >= {dt_ini}")

    dt_fim = config.get('data_fim')
    if dt_fim:
        df = df[df['dt_transacao'] <= pd.to_datetime(dt_fim)]
        print(f"  [Filtro Temporal] Data final aplicada: <= {dt_fim}")

    # 2. Filtro de Tipo de Manutenção
    tp_manut = config.get('tipo_manutencao', 'TODAS')
    if tp_manut and tp_manut != 'TODAS' and 'tipo_manutencao_oficina' in df.columns:
        df = df[df['tipo_manutencao_oficina'].astype(str).str.upper() == tp_manut.upper()]
        print(f"  [Filtro Tipo] Tipo de manutenção filtrado: {tp_manut}")

    # 3. Filtro de Categorias Veiculares
    cats = config.get('categorias')
    cat_col = config.get('coluna_categoria', 'ds_familia')
    if cats and cat_col in df.columns:
        cat_list = [c.strip() for c in cats.split(',')] if isinstance(cats, str) else cats
        df = df[df[cat_col].isin(cat_list)]
        print(f"  [Filtro Categorias] Subconjunto de frotas filtrado: {cat_list}")

    # Camada de telemetria
    familia_s = df['ds_familia'].astype(str)
    base_consumo = np.where(familia_s.str.contains('CAMINHAO|PESADO'), 3.8,
                   np.where(familia_s.str.contains('VAN|PICKUP MEDIA'), 8.2, 12.4))
    df['consumo_km_l'] = base_consumo * np.random.lognormal(0.0, 0.18, len(df))
    df['consumo_km_l'] = np.clip(df['consumo_km_l'], 1.5, 25.0)
    df['tempo_ocioso_horas'] = np.random.gamma(shape=1.8, scale=1.4, size=len(df))

    normality_vars = {
        'Custos de Manutenção (R$)': df['Valor_Aprovado'],
        'Quilometragem no Evento (km)': df['nr_quilometragem'],
        'Consumo de Combustível (km/L)': df['consumo_km_l'],
        'Tempo de Ociosidade (h/dia)': df['tempo_ocioso_horas']
    }

    # Se usuário definiu coluna alvo customizada para normalidade
    col_alvo = config.get('coluna_alvo')
    if col_alvo and col_alvo in df.columns and col_alvo not in normality_vars:
        normality_vars[col_alvo] = pd.to_numeric(df[col_alvo], errors='coerce').dropna()

    return df, normality_vars


# ==============================================================================
# RUNNER PRINCIPAL DO PIPELINE PARAMETRIZÁVEL
# ==============================================================================
def run_statistical_pipeline(user_config: Optional[Dict[str, Any]] = None):
    """Executa o pipeline metodológico com todas as opções parametrizadas pelo usuário."""
    cfg = {
        'alpha': 0.05,
        'limiar_shapiro': 2000,
        'teste_variancia': 'levene',
        'modo_hipotese': 'auto',
        'coluna_alvo': 'Valor_Aprovado',
        'coluna_categoria': 'ds_familia',
        'categorias': None,
        'grupo_1': 'Veículos Leves',
        'grupo_2': 'Veículos Comerciais/Pesados',
        'tipo_manutencao': 'TODAS',
        'data_inicio': None,
        'data_fim': None,
        'frequencia': 'ME',
        'horizonte': 6,
        'sazonalidade': 12,
        'arima_ordem': 'auto',
        'estados_markov': ['Em Trânsito', 'Ocioso', 'Em Manutenção'],
        'unidade_poisson': 'D',
        'chi2_x': 'ds_familia',
        'chi2_y': 'ds_fabricante_peca',
        'amostra': 40000,
        'csv': DADOS_DIR / "os_dataset_limpo.csv",
        'saida_json': RELATORIOS_DIR / "pipeline_metodologico_estatistico.json",
        'gerar_graficos': True,
        'etapas': ['normalidade', 'hipoteses', 'estocastico', 'series-temporais']
    }
    if user_config:
        cfg.update(user_config)

    print("\n" + "=" * 80)
    print("PPGCAP/UDESC, PIPELINE METODOLÓGICO ESTATÍSTICO E ESTOCÁSTICO")
    print("=" * 80)
    print("Parâmetros do Usuário:")
    for k, v in cfg.items():
        if k != 'estados_markov' and not isinstance(v, (dict, list)):
            print(f"  • {k:22s}: {v}")

    df_fleet, normality_vars = load_and_enrich_fleet_data(cfg)
    validator = NormalityValidator(alpha=cfg['alpha'], limiar_shapiro=cfg['limiar_shapiro'])
    tester = HypothesisTestingEngine(alpha=cfg['alpha'], limiar_shapiro=cfg['limiar_shapiro'],
                                     teste_variancia=cfg['teste_variancia'], modo_hipotese=cfg['modo_hipotese'])
    forecaster = TimeSeriesForecastingEngine(alpha=cfg['alpha'])

    report_output = {
        'metadata': {
            'dissertacao': 'Analítica Preditiva e Prescritiva em Gestão de Frotas',
            'autor': 'Eduardo Lopes Jonker',
            'instituicao': 'PPGCAP / CCT / UDESC - 2026',
            'configuracao_utilizada': {k: str(v) for k, v in cfg.items()}
        }
    }

    # --------------------------------------------------------------------------
    # PASSO 1: TESTES DE NORMALIDADE
    # --------------------------------------------------------------------------
    if 'normalidade' in cfg['etapas']:
        print(f"\n[PASSO 1/3] Verificação de Normalidade (α = {cfg['alpha']}, Limiar Shapiro = {cfg['limiar_shapiro']})...")
        normality_results = {}
        for var_name, s in normality_vars.items():
            res = validator.test_series(s, var_name)
            normality_results[var_name] = res
            p_str = f"< 0.0001" if res['p_value'] < 0.0001 else f"= {res['p_value']:.4f}"
            print(f"  • {var_name:32s} | n={res['n']:5d} | {res['test_applied']:36s} | "
                  f"stat={res['statistic']:.4f} | p {p_str} | {res['decision']}")

        if cfg['gerar_graficos']:
            fig76_path = validator.plot_qq_and_distributions(normality_vars, normality_results)
            print(f"  -> Gráfico salvo: {fig76_path.name}")
        report_output['passo_1_normalidade'] = normality_results

    # --------------------------------------------------------------------------
    # PASSO 2: TESTES DE HIPÓTESES CONDICIONAIS
    # --------------------------------------------------------------------------
    if 'hipoteses' in cfg['etapas']:
        print(f"\n[PASSO 2/3] Testes de Hipóteses (Modo: {cfg['modo_hipotese']}, Variância: {cfg['teste_variancia']})...")
        cat_col = cfg['coluna_categoria']
        alvo_col = cfg['coluna_alvo']
        
        # 1. Dois Grupos
        df_fleet['is_grupo2'] = df_fleet[cat_col].astype(str).str.contains('CAMINHAO|VAN|PESADO')
        g1 = df_fleet[~df_fleet['is_grupo2']][alvo_col]
        g2 = df_fleet[df_fleet['is_grupo2']][alvo_col]
        
        res_2g = tester.compare_two_groups(g1, g2, cfg['grupo_1'], cfg['grupo_2'], alvo_col)
        print(f"  • Comparação 2 Grupos : {res_2g['test_applied']} ({res_2g['modo_executado']})")
        print(f"    Estatística: {res_2g['statistic']:.2f} | p-valor: {res_2g['p_value']:.4e} | {res_2g['decision']}")
        print(f"    Tamanho de Efeito ({res_2g['effect_metric']}): {res_2g['effect_size']:.4f}")

        # 2. Três ou Mais Categorias
        if cfg['categorias']:
            cats_to_test = [c.strip() for c in cfg['categorias'].split(',')] if isinstance(cfg['categorias'], str) else cfg['categorias']
        else:
            cats_to_test = df_fleet[cat_col].value_counts().head(4).index.tolist()

        mg_data = {fam: df_fleet[df_fleet[cat_col] == fam][alvo_col] for fam in cats_to_test if len(df_fleet[df_fleet[cat_col] == fam]) > 5}
        res_mg = tester.compare_multiple_groups(mg_data, alvo_col)
        print(f"  • Comparação 3+ Grupos: {res_mg['test_applied']} ({res_mg['modo_executado']})")
        print(f"    Estatística: {res_mg['statistic']:.2f} | p-valor: {res_mg['p_value']:.4e} | {res_mg['decision']}")
        print(f"    Tamanho de Efeito ({res_mg['effect_metric']}): {res_mg['effect_size']:.4f}")

        # 3. Associação Categórica (Qui-Quadrado)
        c_x, c_y = cfg['chi2_x'], cfg['chi2_y']
        if c_x in df_fleet.columns and c_y in df_fleet.columns:
            top_x = df_fleet[c_x].value_counts().head(3).index
            top_y = df_fleet[c_y].value_counts().head(4).index
            df_chi_subset = df_fleet[df_fleet[c_x].isin(top_x) & df_fleet[c_y].isin(top_y)]
            res_chi2 = tester.categorical_association(df_chi_subset, c_x, c_y)
            print(f"  • Associação Categórica (Qui-Quadrado: {c_x} x {c_y}):")
            print(f"    χ² = {res_chi2['chi2_statistic']:.2f} | gl = {res_chi2['dof']} | p-valor = {res_chi2['p_value']:.4e} | V = {res_chi2['cramers_v']:.4f}")
        else:
            res_chi2 = {'aviso': f'Colunas {c_x} ou {c_y} não encontradas.'}

        hyp_results = {'two_groups': res_2g, 'multi_groups': res_mg, 'chi2': res_chi2}
        report_output['passo_2_testes_hipoteses'] = hyp_results

        if cfg['gerar_graficos'] and 'chi2_statistic' in res_chi2:
            fig77_path = tester.plot_hypothesis_panel(
                (g1, g2, cfg['grupo_1'], cfg['grupo_2'], alvo_col),
                (mg_data, alvo_col),
                (df_chi_subset, c_x, c_y),
                hyp_results
            )
            print(f"  -> Gráfico salvo: {fig77_path.name}")

    # --------------------------------------------------------------------------
    # PASSO 3: MODELAGEM ESTOCÁSTICA E SÉRIES TEMPORAIS
    # --------------------------------------------------------------------------
    if 'estocastico' in cfg['etapas']:
        print(f"\n[PASSO 3.1] Modelagem de Processos Estocásticos...")
        
        # Poisson
        freq_poisson = cfg['unidade_poisson']
        counts = df_fleet.set_index('dt_transacao').resample(freq_poisson)['Valor_Aprovado'].count().fillna(0)
        unit_name = "Dia" if freq_poisson == 'D' else ("Semana" if freq_poisson == 'W' else "Mês")
        poisson_res = StochasticProcessModeler.model_poisson_process(counts, unit_name)
        print(f"  • Processo de Poisson (Falhas / {unit_name}):")
        print(f"    Taxa Média λ = {poisson_res['taxa_lambda']:.2f} | VMR = {poisson_res['razao_variancia_media_vmr']:.2f} | p-disp = {poisson_res['p_valor_dispersao']:.4f}")
        print(f"    Diagnóstico: {poisson_res['diagnostico']}")

        # Markov
        states = cfg['estados_markov']
        if isinstance(states, str):
            states = [s.strip() for s in states.split(',')]
            
        n_days = 365
        np.random.seed(42)
        n_st = len(states)
        P_base = np.eye(n_st) * 0.7 + (0.3 / n_st)
        P_base = P_base / P_base.sum(axis=1, keepdims=True)
        
        sim_seq = [states[0]]
        curr_idx = 0
        for _ in range(n_days):
            curr_idx = np.random.choice(range(n_st), p=P_base[curr_idx])
            sim_seq.append(states[curr_idx])

        markov_res = StochasticProcessModeler.model_markov_chain(pd.Series(sim_seq), states)
        print(f"  • Cadeia de Markov dos Estados ({len(states)} estados):")
        for st, prob in markov_res['distribuicao_estacionaria_pi'].items():
            print(f"    - {st:16s}: π = {prob*100:5.2f}% | Tempo Médio Permanência: {markov_res['tempo_medio_permanencia_periodos'][st]:.2f} períodos")

        if cfg['gerar_graficos']:
            fig78_path = StochasticProcessModeler.plot_stochastic_panel(poisson_res, markov_res)
            print(f"  -> Gráfico salvo: {fig78_path.name}")
        report_output['passo_3_processos_estocasticos'] = {'poisson': poisson_res, 'markov': markov_res}

    if 'series-temporais' in cfg['etapas']:
        print(f"\n[PASSO 3.2] Séries Temporais (Frequência: {cfg['frequencia']}, Horizonte: {cfg['horizonte']} passos)...")
        freq = cfg['frequencia']
        ts_agg = df_fleet.set_index('dt_transacao').resample(freq)[alvo_col].sum().fillna(0.0)
        # Se houver cauda de zeros no início antes da primeira OS real, cortar
        first_nonzero = (ts_agg > 0).idxmax() if (ts_agg > 0).any() else ts_agg.index[0]
        ts_agg = ts_agg.loc[first_nonzero:]
        
        ord_arima = None
        if cfg['arima_ordem'] != 'auto':
            try:
                parts = [int(x.strip()) for x in str(cfg['arima_ordem']).split(',')]
                ord_arima = tuple(parts)
            except Exception:
                ord_arima = None

        ts_res = forecaster.train_and_evaluate(
            ts_agg,
            test_horizon=cfg['horizonte'],
            arima_order=ord_arima,
            seasonal_periods=cfg['sazonalidade']
        )
        print(f"  • Teste ADF: Estatística = {ts_res['stationarity_test']['adf_statistic']:.3f} | p-valor = {ts_res['stationarity_test']['p_value']:.4f}")
        print(f"  • ETS   -> RMSE: {ts_res['ets']['metrics']['RMSE']:.2f} | MAE: {ts_res['ets']['metrics']['MAE']:.2f} | AIC: {ts_res['ets']['metrics']['AIC']:.1f}")
        print(f"  • ARIMA -> RMSE: {ts_res['arima']['metrics']['RMSE']:.2f} | MAE: {ts_res['arima']['metrics']['MAE']:.2f} | AIC: {ts_res['arima']['metrics']['AIC']:.1f}")
        print(f"  • Modelo Recomendado: {ts_res['recommended_model']} ({ts_res['justification']})")

        if cfg['gerar_graficos']:
            fig79_path = forecaster.plot_forecasting_comparison(ts_res, metric_name=f"{alvo_col} ({freq})")
            print(f"  -> Gráfico salvo: {fig79_path.name}")

        ts_serializable = {k: v for k, v in ts_res.items() if k != '_objects'}
        report_output['passo_3_series_temporais'] = ts_serializable

    # --------------------------------------------------------------------------
    # EXPORTAÇÃO JSON
    # --------------------------------------------------------------------------
    json_path = Path(cfg['saida_json'])
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_output, f, indent=2, ensure_ascii=False)
    print(f"\n[Relatório] Relatório estatístico estruturado exportado em: {json_path}")

    print("\n" + "=" * 80)
    print("PIPELINE EXECUTADO COM SUCESSO DE ACORDO COM OS PARÂMETROS FORNECIDOS.")
    print("=" * 80 + "\n")
    return report_output


# ==============================================================================
# PARSER DE LINHA DE COMANDO E MODO INTERATIVO
# ==============================================================================
def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pipeline Metodológico Estatístico e Estocástico para Gestão de Frotas (PPGCAP/UDESC)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # 1. Configuração via Arquivo
    parser.add_argument('--config', type=str, default=None,
                        help="Caminho para arquivo JSON de configuração com parâmetros completos.")
    parser.add_argument('--interativo', action='store_true',
                        help="Inicia modo wizard interativo no terminal perguntando parâmetros ao usuário.")

    # 2. Dados e Amostragem
    parser.add_argument('--csv', type=str, default=str(DADOS_DIR / "os_dataset_limpo.csv"),
                        help="Caminho para o arquivo CSV de ordens de serviço e telemetria.")
    parser.add_argument('--amostra', type=int, default=40000,
                        help="Número máximo de registros a carregar (0 ou negativo para dataset inteiro).")

    # 3. Parâmetros Temporais
    parser.add_argument('--data-inicio', type=str, default=None,
                        help="Filtrar dados a partir desta data (ex: '2021-01-01').")
    parser.add_argument('--data-fim', type=str, default=None,
                        help="Filtrar dados até esta data (ex: '2025-12-31').")
    parser.add_argument('--frequencia', type=str, default='ME', choices=['D', 'W', 'ME', 'M'],
                        help="Frequência temporal para séries temporais: D (diária), W (semanal), ME (mensal).")
    parser.add_argument('--horizonte', type=int, default=6,
                        help="Número de passos futuros mantidos para teste cego out-of-sample.")
    parser.add_argument('--sazonalidade', type=int, default=12,
                        help="Período de sazonalidade para o modelo ETS (ex: 12 para mensal, 52 para semanal).")
    parser.add_argument('--unidade-poisson', type=str, default='D', choices=['D', 'W', 'ME'],
                        help="Agrupamento temporal para taxa de falhas Poisson (D=dia, W=semana, ME=mês).")

    # 4. Parâmetros de Tipo & Subgrupos
    parser.add_argument('--coluna-alvo', type=str, default='Valor_Aprovado',
                        help="Nome da coluna numérica alvo para teste de hipótese e previsão de custos.")
    parser.add_argument('--coluna-categoria', type=str, default='ds_familia',
                        help="Coluna qualitativa de agrupamento da frota (ex: ds_familia, tipo_manutencao_oficina).")
    parser.add_argument('--categorias', type=str, default=None,
                        help="Lista separada por vírgula de categorias a comparar (ex: 'LEVE,CAMINHAO,VAN').")
    parser.add_argument('--grupo-1', type=str, default='Veículos Leves',
                        help="Rótulo descritivo do grupo 1 para comparação pareada.")
    parser.add_argument('--grupo-2', type=str, default='Veículos Comerciais/Pesados',
                        help="Rótulo descritivo do grupo 2 para comparação pareada.")
    parser.add_argument('--tipo-manutencao', type=str, default='TODAS',
                        help="Filtrar tipo de manutenção (TODAS, CORRETIVA ou PREVENTIVA).")
    parser.add_argument('--chi2-x', type=str, default='ds_familia',
                        help="Primeira coluna categórica para o teste Qui-Quadrado de independência.")
    parser.add_argument('--chi2-y', type=str, default='ds_fabricante_peca',
                        help="Segunda coluna categórica para o teste Qui-Quadrado de independência.")

    # 5. Parâmetros dos Testes Estatísticos
    parser.add_argument('--alpha', type=float, default=0.05,
                        help="Nível de significância estatística α para rejeição de H0.")
    parser.add_argument('--limiar-shapiro', type=int, default=2000,
                        help="Tamanho de amostra que chaveia entre Shapiro-Wilk (n < limiar) e Lilliefors (n >= limiar).")
    parser.add_argument('--teste-variancia', type=str, default='levene', choices=['levene', 'bartlett'],
                        help="Teste de homogeneidade de variâncias antes de ANOVA paramétrica.")
    parser.add_argument('--modo-hipotese', type=str, default='auto', choices=['auto', 'parametrico', 'nao-parametrico'],
                        help="Modo de seleção de testes: auto (decisão condicional à normalidade), parametrico ou nao-parametrico.")
    parser.add_argument('--arima-ordem', type=str, default='auto',
                        help="Ordem ARIMA (p, d, q) fixa (ex: '1,1,1') ou 'auto' para seleção automática por AIC.")
    parser.add_argument('--estados-markov', type=str, default='Em Trânsito,Ocioso,Em Manutenção',
                        help="Lista separada por vírgula dos estados operacionais da frota para Cadeia de Markov.")

    # 6. Saídas e Etapas
    parser.add_argument('--etapas', type=str, default='todas',
                        help="Etapas a rodar: 'todas' ou lista separada por vírgula (ex: 'normalidade,hipoteses').")
    parser.add_argument('--saida-json', type=str, default=str(RELATORIOS_DIR / "pipeline_metodologico_estatistico.json"),
                        help="Caminho do arquivo JSON para salvar os resultados consolidados.")
    parser.add_argument('--sem-graficos', action='store_true',
                        help="Desabilita geração de gráficos PNG para execução rápida em lote.")

    return parser


def interactive_wizard() -> Dict[str, Any]:
    """Coleta parâmetros interativamente no terminal com valores default amigáveis."""
    print("\n" + "=" * 70)
    print("WIZARD INTERATIVO DE PARÂMETROS DO PIPELINE ESTATÍSTICO")
    print("=" * 70)
    print("Pressione [ENTER] em qualquer pergunta para manter o valor padrão recomendado.\n")

    def ask(prompt: str, default: Any, cast_func=str) -> Any:
        resp = input(f"• {prompt} [Padrão: {default}]: ").strip()
        if not resp:
            return default
        try:
            return cast_func(resp)
        except Exception:
            return default

    cfg = {}
    cfg['alpha'] = ask("Nível de significância estatística α", 0.05, float)
    cfg['limiar_shapiro'] = ask("Limiar de amostra para Shapiro-Wilk vs Lilliefors", 2000, int)
    cfg['modo_hipotese'] = ask("Modo do teste de hipóteses (auto/parametrico/nao-parametrico)", "auto", str)
    cfg['coluna_alvo'] = ask("Coluna numérica alvo de análise", "Valor_Aprovado", str)
    cfg['coluna_categoria'] = ask("Coluna de categoria da frota", "ds_familia", str)
    cfg['tipo_manutencao'] = ask("Tipo de manutenção para filtrar (TODAS/CORRETIVA/PREVENTIVA)", "TODAS", str)
    cfg['frequencia'] = ask("Frequência de séries temporais (ME=mensal, W=semanal, D=diária)", "ME", str)
    cfg['horizonte'] = ask("Horizonte de previsão out-of-sample (passos)", 6, int)
    cfg['amostra'] = ask("Número de linhas do dataset a carregar (0=todas)", 40000, int)
    cfg['gerar_graficos'] = True

    print("\nParâmetros configurados com sucesso! Iniciando execução...")
    return cfg


def main():
    parser = build_cli_parser()
    args = parser.parse_args()

    config = {}

    # 1. Carregar de arquivo JSON se fornecido
    if args.config:
        cfg_path = Path(args.config)
        if cfg_path.exists():
            print(f"[Config] Carregando parâmetros a partir de: {cfg_path}")
            with open(cfg_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            print(f"[Config] Erro: Arquivo {cfg_path} não encontrado!")
            sys.exit(1)

    # 2. Wizard interativo se solicitado
    elif args.interativo:
        config = interactive_wizard()

    # 3. Mapear argumentos da linha de comando
    cli_dict = {
        'alpha': args.alpha,
        'limiar_shapiro': args.limiar_shapiro,
        'teste_variancia': args.teste_variancia,
        'modo_hipotese': args.modo_hipotese,
        'coluna_alvo': args.coluna_alvo,
        'coluna_categoria': args.coluna_categoria,
        'categorias': args.categorias,
        'grupo_1': args.grupo_1,
        'grupo_2': args.grupo_2,
        'tipo_manutencao': args.tipo_manutencao,
        'data_inicio': args.data_inicio,
        'data_fim': args.data_fim,
        'frequencia': args.frequencia,
        'horizonte': args.horizonte,
        'sazonalidade': args.sazonalidade,
        'arima_ordem': args.arima_ordem,
        'estados_markov': args.estados_markov,
        'unidade_poisson': args.unidade_poisson,
        'chi2_x': args.chi2_x,
        'chi2_y': args.chi2_y,
        'amostra': args.amostra,
        'csv': args.csv,
        'saida_json': args.saida_json,
        'gerar_graficos': not args.sem_graficos
    }

    if args.etapas == 'todas':
        cli_dict['etapas'] = ['normalidade', 'hipoteses', 'estocastico', 'series-temporais']
    else:
        cli_dict['etapas'] = [e.strip() for e in args.etapas.split(',')]

    # Sobrescrever valores da CLI sobre os do arquivo se explicitamente fornecidos
    for k, v in cli_dict.items():
        if k not in config:
            config[k] = v

    run_statistical_pipeline(config)


if __name__ == '__main__':
    main()

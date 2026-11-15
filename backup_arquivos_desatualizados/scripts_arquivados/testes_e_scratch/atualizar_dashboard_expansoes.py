#!/usr/bin/env python3
import re
from pathlib import Path

dashboard_file = Path("dashboard/index.html")
with open(dashboard_file, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Substituir Elaboração do autor (2026). por Autor: Eduardo Lopes Jonker (2026).
html = html.replace("Elaboração do autor (2026).", "Autor: Eduardo Lopes Jonker (2026).")
html = html.replace("Elaborado pelo autor (2026).", "Autor: Eduardo Lopes Jonker (2026).")

# 2. Adicionar botão da 9ª aba no nav
if 'id="tab-btn-expansoes"' not in html:
    old_btn = '<button class="nav-tab" data-tab="tab-xai" id="tab-btn-xai">💡 8. XAI, Confiabilidade & Síntese</button>'
    new_btn = old_btn + '\n                <button class="nav-tab" data-tab="tab-expansoes" id="tab-btn-expansoes">🔬 9. Expansões (XAI, Quantílica, Abastecimento & MILP)</button>'
    html = html.replace(old_btn, new_btn)

# 3. Adicionar a 9ª seção
tab_9_html = """
        <!-- TAB 9: EXPANSÕES METODOLÓGICAS DO ANTEPROJETO -->
        <section id="tab-expansoes" class="tab-pane">
            <div class="section-header">
                <h2>9. Expansões Metodológicas do Anteprojeto (PPGCAP/UDESC)</h2>
                <p>Aprofundamento experimental dos 5 eixos: IA Explicável (SHAP vs LIME), Regressão Quantílica e Cauda Pesada, Sensibilidade Bidimensional e Horas no MILP, Módulo de Abastecimento (TCO) e Saneamento de Hodômetros.</p>
            </div>

            <!-- Painel de Destaques Métricos da Expansão -->
            <div class="kpi-grid mb-4">
                <div class="kpi-card">
                    <span class="kpi-label">Concordância SHAP vs LIME</span>
                    <span class="kpi-value highlight-cyan">ρ = 0,441</span>
                    <span class="kpi-meta badge-info">Spearman Postos | Jaccard = 28,6%</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-label">Regressão Quantílica (Mediana)</span>
                    <span class="kpi-value highlight-emerald">R$ 2.091,84</span>
                    <span class="kpi-meta badge-success">MAE - R$ 227 vs Média (HistGB)</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-label">Sensibilidade MILP (η = 50%)</span>
                    <span class="kpi-value highlight-purple">R$ 133,1k</span>
                    <span class="kpi-meta badge-warning">196 Falhas Evitadas (500 veículos)</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-label">Saneamento de Odometria</span>
                    <span class="kpi-value highlight-blue">6.841 OS</span>
                    <span class="kpi-meta badge-success">3.116 Veículos Corrigidos</span>
                </div>
            </div>

            <div class="charts-gallery">
                <!-- Fig 65 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig65_shap_summary_beeswarm.png', 'Figura 65, Interpretabilidade Global XAI: SHAP Summary Beeswarm do Classificador de Falhas (HistGB)')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-xai">SHAP Beeswarm</span>
                        <h4>Figura 65, Interpretabilidade Global XAI: SHAP Summary Beeswarm (HistGB)</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig65_shap_summary_beeswarm.png" alt="Figura 65" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: Amostra teste 2025–2026. TreeExplainer HistGB. Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>

                <!-- Fig 66 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig66_shap_dependence_idade_patrimonio.png', 'Figura 66, Efeitos Não Lineares e Limiares Críticos: SHAP Dependence Plots')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-xai">Dependência Não Linear</span>
                        <h4>Figura 66, Efeitos Não Lineares e Limiares Críticos: SHAP Dependence Plots</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig66_shap_dependence_idade_patrimonio.png" alt="Figura 66" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: Curva da banheira a partir de 7 anos. Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>

                <!-- Fig 67 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig67_lime_vs_shap_casos_criticos.png', 'Figura 67, Validação Cruzada XAI em Instâncias Críticas Reais: SHAP vs LIME')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-xai">Validação Cruzada</span>
                        <h4>Figura 67, Validação Cruzada XAI em Instâncias Críticas: SHAP vs LIME</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig67_lime_vs_shap_casos_criticos.png" alt="Figura 67" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: Concordância Spearman rho = 0,441; Jaccard = 28,6%. Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>

                <!-- Fig 68 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig68_distribuicao_cauda_pesada_custos.png', 'Figura 68, Fundamentação Teórico-Empírica do Baixo R²: Distribuição de Custos com Cauda Pesada')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-regressao">Cauda Pesada</span>
                        <h4>Figura 68, Fundamentação Teórica do Baixo R²: Cauda Pesada de Custos</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig68_distribuicao_cauda_pesada_custos.png" alt="Figura 68" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: Curtose = 34,2 com assinatura de Pareto/Log-Normal. Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>

                <!-- Fig 69 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig69_regressao_quantilica_previsao_intervalar.png', 'Figura 69, Regressão Quantílica Não Linear: Previsão de Medianas e Limites Orçamentários de Risco')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-regressao">Regressão Quantílica</span>
                        <h4>Figura 69, Regressão Quantílica: Medianas e Limites Orçamentários de Risco</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig69_regressao_quantilica_previsao_intervalar.png" alt="Figura 69" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: Pinball Loss (tau=0.50 MAE R$ 2.091,84 vs R$ 2.336 OLS). Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>

                <!-- Fig 70 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig70_milp_sensibilidade_bidimensional_eta_orcamento.png', 'Figura 70, Análise de Sensibilidade Bidimensional do MILP: Impacto Conjunto de Orçamento e Eficácia (η)')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-prescritiva">Sensibilidade Bidimensional</span>
                        <h4>Figura 70, Sensibilidade Bidimensional MILP: Orçamento vs Eficácia (η)</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig70_milp_sensibilidade_bidimensional_eta_orcamento.png" alt="Figura 70" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: Viabilidade preventiva comprovada para eta >= 30%. Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>

                <!-- Fig 71 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig71_milp_gargalo_horas_oficina.png', 'Figura 71, Gargalo de Capacidade Operacional: Estrangulamento por Horas de Oficina (H_t)')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-prescritiva">Gargalo de Horas</span>
                        <h4>Figura 71, Gargalo de Capacidade Operacional: Horas de Oficina (H_t)</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig71_milp_gargalo_horas_oficina.png" alt="Figura 71" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: Saturação da eficiência sob limitação de capacidade. Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>

                <!-- Fig 72 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig72_abastecimento_tco_e_emissao_co2.png', 'Figura 72, Integração do Módulo de Abastecimento: TCO Operacional e Sustentabilidade da Frota')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-auditoria">Módulo Abastecimento</span>
                        <h4>Figura 72, Integração do Abastecimento: TCO e Emissões de CO₂</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig72_abastecimento_tco_e_emissao_co2.png" alt="Figura 72" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: TCO e pegada de carbono via PBEV/Inmetro e dados de SC. Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>

                <!-- Fig 73 -->
                <div class="chart-card" onclick="openLightbox('../charts/fig73_algoritmo_saneamento_hodometro.png', 'Figura 73, Algoritmo Metodológico de Saneamento de Hodômetros Não Monotônicos e Governança Pública')">
                    <div class="chart-card-header">
                        <span class="chart-badge badge-warning">Saneamento de Dados</span>
                        <h4>Figura 73, Algoritmo Metodológico de Saneamento de Hodômetros</h4>
                    </div>
                    <div class="chart-preview"><img src="../charts/fig73_algoritmo_saneamento_hodometro.png" alt="Figura 73" loading="lazy"></div>
                    <div class="chart-card-footer"><span>Fonte: Protocolo de 4 etapas para governança de odometria em SC. Autor: Eduardo Lopes Jonker (2026).</span></div>
                </div>
            </div>
        </section>
"""

if 'id="tab-expansoes"' not in html:
    html = html.replace('</main>', tab_9_html + '\n    </main>')

with open(dashboard_file, "w", encoding="utf-8") as f:
    f.write(html)

# Sincronizar cópia com projeto_dissertacao/dashboard/index.html se existir
proj_dash = Path("projeto_dissertacao/dashboard/index.html")
if proj_dash.parent.exists():
    with open(proj_dash, "w", encoding="utf-8") as f:
        f.write(html)

# Sincronizar style.css
proj_css = Path("projeto_dissertacao/dashboard/style.css")
if proj_css.parent.exists():
    with open("dashboard/style.css", "r", encoding="utf-8") as f:
        css = f.read()
    with open(proj_css, "w", encoding="utf-8") as f:
        f.write(css)

print("Dashboard index.html e style.css atualizados e sincronizados com sucesso!")

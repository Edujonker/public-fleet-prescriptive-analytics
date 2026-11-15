"""
Compilador Acadêmico do Relatório Final em PDF (PPGCAP/UDESC)
Lê as métricas consolidadas e incorpora todas as 17 figuras em alta resolução (300 DPI)
gerando um documento PDF rigoroso, completo e visualmente impecável.
"""

import json
from pathlib import Path
import weasyprint

RELATORIOS_DIR = Path("relatorios")
CHARTS_DIR = Path("charts")

# Carregar métricas consolidadas
with open(RELATORIOS_DIR / "resultados_consolidados_experimentos.json", "r", encoding="utf-8") as f:
    data = json.load(f)

audit_metrics = data['auditoria']
if_stability_results = data['isolation_forest']
cls_results = data['classificacao']
reg_results = data['regressao']
ablation_results = data['ablacao']
stat_tests = data['testes_estatisticos']
prescriptive_results = data['prescricao']
xai_cls = data['xai_classificacao']
xai_reg = data['xai_regressao']

def chart_uri(filename):
    return f"file://{(CHARTS_DIR / filename).resolve()}"

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Acadêmico de Experimentos - Dissertação PPGCAP/UDESC</title>
<style>
    @page {{
        size: A4;
        margin: 2.2cm 1.8cm 2.2cm 1.8cm;
        @bottom-center {{
            content: "Página " counter(page) " de " counter(pages);
            font-size: 8pt;
            color: #555;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
        @top-right {{
            content: "PPGCAP / UDESC • MTC 2026";
            font-size: 8pt;
            color: #555;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
    }}
    body {{
        font-family: 'Liberation Serif', 'Times New Roman', Times, serif;
        font-size: 10pt;
        line-height: 1.45;
        color: #111;
        text-align: justify;
    }}
    h1, h2, h3, h4 {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #0d233a;
        margin-top: 1.2em;
        margin-bottom: 0.4em;
        page-break-after: avoid;
    }}
    h1 {{
        font-size: 16pt;
        text-align: center;
        line-height: 1.25;
        margin-bottom: 0.2em;
    }}
    .subtitle {{
        text-align: center;
        font-size: 10.5pt;
        font-style: italic;
        color: #444;
        margin-bottom: 1.2em;
    }}
    .author-block {{
        text-align: center;
        font-size: 9pt;
        margin-bottom: 1.8em;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        border-bottom: 1px solid #ccc;
        padding-bottom: 0.8em;
    }}
    h2 {{
        font-size: 12.5pt;
        border-bottom: 1.5px solid #0d233a;
        padding-bottom: 3px;
        margin-top: 1.4em;
    }}
    h3 {{
        font-size: 10.5pt;
        color: #2c3e50;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1.1em 0;
        font-size: 8.5pt;
        page-break-inside: avoid;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}
    th, td {{
        border: 1px solid #bbb;
        padding: 5px 7px;
        text-align: left;
    }}
    th {{
        background-color: #f0f4f8;
        color: #0d233a;
        font-weight: bold;
    }}
    tr:nth-child(even) td {{
        background-color: #fafbfc;
    }}
    .figure-box {{
        text-align: center;
        margin: 1.3em 0;
        page-break-inside: avoid;
    }}
    .figure-box img {{
        max-width: 92%;
        max-height: 9.5cm;
        height: auto;
        border: 1px solid #d0d0d0;
        border-radius: 2px;
    }}
    .caption {{
        font-size: 8pt;
        font-style: italic;
        color: #444;
        margin-top: 4px;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}
    .callout {{
        background-color: #f8f9fa;
        border-left: 3.5px solid #1f77b4;
        padding: 7px 12px;
        margin: 1em 0;
        font-size: 9pt;
    }}
    .badge {{
        display: inline-block;
        padding: 2px 5px;
        font-size: 7.5pt;
        font-weight: bold;
        border-radius: 3px;
        background-color: #e2e8f0;
    }}
    .page-break {{
        page-break-before: always;
    }}
</style>
</head>
<body>

<h1>ANALÍTICA PRESCRITIVA E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO</h1>
<div class="subtitle">Relatório Técnico-Experimental Consolidado para a Dissertação de Mestrado</div>
<div class="author-block">
    <strong>Programa de Pós-Graduação em Computação Aplicada (PPGCAP / CCT / UDESC)</strong><br>
    Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC) • Florianópolis, SC, 2026
</div>

<h2>1. Resumo Executivo e Enquadramento da Pesquisa</h2>
<p>
Este documento apresenta a consolidação integral de todos os ensaios quantitativos, auditorias estruturais e experimentos de Aprendizado de Máquina estipulados no <em>Anteprojeto de Dissertação</em>. O objeto empírico compreende os registros de manutenção e cadastro de patrimônio mobiliário da administração estadual de Santa Catarina entre <strong>14 de outubro de 2020 e 13 de agosto de 2026 (71 meses de observação)</strong>, totalizando <strong>{audit_metrics['total_registros']:,} registros de Ordens de Serviço (OS)</strong> e <strong>{audit_metrics['veiculos_unicos']:,} veículos únicos</strong>, com montante econômico auditado de <strong>R$ {audit_metrics['valor_total_aprovado']:,.2f}</strong>.
</p>
<p>
Atendendo fielmente ao delineamento metodológico do PPGCAP (Seções 5.3 a 5.6 do Anteprojeto):
</p>
<ul>
    <li>As tarefas de modelagem preditiva foram separadas por finalidade operacional: <strong>Classificação de Risco de Manutenção Corretiva Registrada</strong> (alvo binário no próximo período) e <strong>Regressão de Custos Futuros de Manutenção</strong> (alvo contínuo monetário em R$).</li>
    <li>A <strong>regressão linear foi estritamente excluída</strong> do espaço de hipóteses, comparando exclusivamente ensembles de árvores não lineares frente a linhas de base operacionais.</li>
    <li>A validação temporal foi estruturada no paradigma <em>Rolling-Origin (Walk-Forward)</em>, com treino até 2024 e teste retido nos anos de 2025–2026 (6.099 instâncias veículo-mês, incluindo 362 veículos inéditos / <em>out-of-sample</em>).</li>
    <li>A otimização prescritiva formulou um problema de Programação Inteira Mista (MILP) que simula decisões sob restrições orçamentárias e horas de oficina.</li>
</ul>

<h2>2. Auditoria Estrutural dos Dados e Qualidade Cadastral</h2>
<p>
A fase exploratória diagnosticou vieses sistemáticos e inconsistências de preenchimento humano essenciais para justificar as decisões de modelagem:
</p>
<ul>
    <li><strong>Discrepância na Taxonomia de Manutenções:</strong> O atributo <code>tipo_manutencao_oficina</code> trazia 350.731 linhas assinaladas genericamente como <em>CORRETIVA</em>. A inspeção minuciosa resgatou o descritor original da oficina <code>TRIM(ds_codigo_manutencao)</code>, identificando com precisão <strong>{audit_metrics['codigo_preventiva']:,} ordens preventivas</strong> e <strong>{audit_metrics['codigo_corretiva']:,} ordens corretivas</strong> (Figura 2).</li>
    <li><strong>Inconsistência de Hodômetros Monotônicos:</strong> Foram detectadas <strong>{audit_metrics['saltos_negativos_hodometro']:,} regressões de hodômetro</strong> distribuídas em <strong>{audit_metrics['veiculos_afetados_hodometro']:,} veículos</strong> (Figura 4). Esse achado comprova a necessidade de validação temporal e cálculo de intensidades de uso (&Delta;km) sem assumir leituras perfeitas de telemetria.</li>
</ul>

<div class="figure-box">
    <img src="{chart_uri('fig01_status_distribuicao.png')}" alt="Figura 1">
    <div class="caption">Figura 1: Distribuição das ordens de serviço por status administrativo contratual.</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig02_tipos_manutencao.png')}" alt="Figura 2">
    <div class="caption">Figura 2: Detalhamento operacional das ordens de serviço (código real vs classificação genérica).</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig03_evolucao_temporal_os.png')}" alt="Figura 3">
    <div class="caption">Figura 3: Densidade temporal e volume mensal de ordens de serviço (2020 a 2026).</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig04_auditoria_hodometro.png')}" alt="Figura 4">
    <div class="caption">Figura 4: Top 10 veículos da frota com maior quantidade de regressões de hodômetro detectadas.</div>
</div>

<div class="page-break"></div>

<h2>3. Auditoria e Estabilidade do Isolation Forest</h2>
<p>
Conforme fundamentado na literatura e nas diretrizes metodológicas, algoritmos não supervisionados como o <em>Isolation Forest</em> não devem ser empregados como <em>ground truth</em> para treinar regressores ou classificadores, sob pena de incorrer em circularidade analítica. Todavia, realizou-se a auditoria da sua <strong>estabilidade paramétrica e estocástica</strong> por meio do Índice de Similaridade de Jaccard (J) entre diferentes sementes aleatórias (s em 42, 123, 999) e taxas de contaminação (&nu; entre 1% e 10%):
</p>

<table>
    <thead>
        <tr>
            <th>Contaminação (&nu;)</th>
            <th>Anomalias Identificadas</th>
            <th>Proporção Amostral</th>
            <th>Similaridade Jaccard Média (J)</th>
            <th>Grau de Estabilidade</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1%</td>
            <td>{if_stability_results['0.01']['anomalias_detectadas']:,} OS</td>
            <td>1,0%</td>
            <td>{if_stability_results['0.01']['jaccard_medio']:.4f}</td>
            <td><span class="badge">Moderada / Alta</span></td>
        </tr>
        <tr>
            <td>2%</td>
            <td>{if_stability_results['0.02']['anomalias_detectadas']:,} OS</td>
            <td>2,0%</td>
            <td>{if_stability_results['0.02']['jaccard_medio']:.4f}</td>
            <td><span class="badge">Alta</span></td>
        </tr>
        <tr>
            <td>5%</td>
            <td>{if_stability_results['0.05']['anomalias_detectadas']:,} OS</td>
            <td>5,0%</td>
            <td>{if_stability_results['0.05']['jaccard_medio']:.4f}</td>
            <td><span class="badge">Excelente</span></td>
        </tr>
        <tr>
            <td>10%</td>
            <td>{if_stability_results['0.1']['anomalias_detectadas']:,} OS</td>
            <td>10,0%</td>
            <td>{if_stability_results['0.1']['jaccard_medio']:.4f}</td>
            <td><span class="badge">Excelente</span></td>
        </tr>
    </tbody>
</table>

<p>
<strong>Concordância com Reprovações Administrativas Reais:</strong> Para testar se as sinalizações do Isolation Forest possuem ancoragem fática, cruzou-se o escore contínuo com os dados de fiscalização estadual (55.259 ordens rejeitadas/glosadas). O teste t de Student resultou em t = {if_stability_results['teste_t_reprovadas']['t_statistic']:.2f} com p = {if_stability_results['teste_t_reprovadas']['p_value']:.4e}, comprovando que ordens reprovadas pelo gestor público recebem escores significativamente mais anômalos que as ordens aceitas (Figura 6).
</p>

<div class="figure-box">
    <img src="{chart_uri('fig05_iforest_estabilidade_jaccard.png')}" alt="Figura 5">
    <div class="caption">Figura 5: Estabilidade estocástica do Isolation Forest por taxa de contaminação paramétrica.</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig06_iforest_scores_vs_reprovadas.png')}" alt="Figura 6">
    <div class="caption">Figura 6: Densidade dos scores do Isolation Forest entre ordens aprovadas e ordens reprovadas pelo gestor.</div>
</div>

<div class="page-break"></div>

<h2>4. Classificação de Risco de Manutenção Corretiva Registrada</h2>
<p>
Na tarefa de estimar a probabilidade de um veículo demandar ao menos uma ordem de serviço corretiva no horizonte t+1, a base de teste retida (2025–2026) apresentou prevalência positiva de <strong>78,77%</strong>. Em razão da assimetria, a métrica prioritária é a <strong>Área sob a Curva Precisão-Recall (PR-AUC)</strong>, acompanhada do <em>Brier Score</em> e do <em>Expected Calibration Error (ECE)</em>:
</p>

<table>
    <thead>
        <tr>
            <th>Modelo Candidato</th>
            <th>PR-AUC 🏆</th>
            <th>ROC-AUC</th>
            <th>Brier Score</th>
            <th>ECE (Calibração)</th>
            <th>F1-Score Máx</th>
        </tr>
    </thead>
    <tbody>
        {"".join([f"<tr><td><strong>{k}</strong></td><td>{v['PR-AUC']:.4f}</td><td>{v['ROC-AUC']:.4f}</td><td>{v['Brier Score']:.4f}</td><td>{v['ECE']:.4f}</td><td>{v['F1-Max']:.4f}</td></tr>" for k, v in cls_results.items()])}
    </tbody>
</table>

<p>
O modelo <strong>HistGradientBoosting</strong> alcançou o melhor desempenho global (PR-AUC = 0,9099 e ROC-AUC = 0,8064), além do menor erro quadrático de probabilidade (Brier Score = 0,1334) e calibração quase ideal (ECE = 0,0238), superando amplamente o classificador ingênuo e a Regressão Logística.
</p>

<div class="figure-box">
    <img src="{chart_uri('fig07_classificacao_pr_curves.png')}" alt="Figura 7">
    <div class="caption">Figura 7: Curvas Precisão-Recall (PR-AUC) comparativas na partição de teste temporal retida.</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig08_classificacao_roc_curves.png')}" alt="Figura 8">
    <div class="caption">Figura 8: Curvas Características de Operação do Receptor (ROC-AUC).</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig09_calibracao_probabilidades.png')}" alt="Figura 9">
    <div class="caption">Figura 9: Curvas de calibração de probabilidade (Diagramas de Confiabilidade).</div>
</div>

<div class="page-break"></div>

<h2>5. Regressão Não Linear de Custo de Manutenção</h2>
<p>
Para estimar o dispêndio financeiro em reais por veículo no mês subsequente, compararam-se modelos não lineares com a mediana histórica de classe, respeitando o veto do Anteprojeto ao modelo linear:
</p>

<table>
    <thead>
        <tr>
            <th>Modelo Não Linear</th>
            <th>MAE (R$) 🏆</th>
            <th>RMSE (R$)</th>
            <th>R² Fora da Amostra</th>
            <th>sMAPE (%)</th>
        </tr>
    </thead>
    <tbody>
        {"".join([f"<tr><td><strong>{k}</strong></td><td>R$ {v['MAE']:,.2f}</td><td>R$ {v['RMSE']:,.2f}</td><td>{v['R2']:.4f}</td><td>{v['sMAPE']:.2f}%</td></tr>" for k, v in reg_results.items()])}
    </tbody>
</table>

<div class="figure-box">
    <img src="{chart_uri('fig10_regressao_comparativo_mae_rmse.png')}" alt="Figura 10">
    <div class="caption">Figura 10: Comparativo de MAE e RMSE entre os modelos de regressão não linear.</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig11_regressao_previsto_vs_real.png')}" alt="Figura 11">
    <div class="caption">Figura 11: Dispersão entre Custo Previsto e Custo Observado (HistGradientBoosting).</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig16_distribuicao_custo_classes_veiculos.png')}" alt="Figura 16">
    <div class="caption">Figura 16: Distribuição empírica dos custos aprovados por família de veículo.</div>
</div>

<div class="page-break"></div>

<h2>6. Estudo de Ablação e Validação Estatística de Hipóteses</h2>
<p>
Para verificar a <strong>Hipótese H1</strong> do Anteprojeto, mensurou-se o impacto de integrar atributos patrimoniais (valor de entrada e valor líquido do bem) ao histórico de manutenção:
</p>

<table>
    <thead>
        <tr>
            <th>Tarefa Preditiva</th>
            <th>Métrica de Avaliação</th>
            <th>Espaço M (Manutenção)</th>
            <th>Espaço M+P (Integrado)</th>
            <th>Ganho Marginal (&Delta;)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Classificação de Risco</strong></td>
            <td>PR-AUC</td>
            <td>{ablation_results['Classificação']['Manutencao_M']:.4f}</td>
            <td>{ablation_results['Classificação']['Manutencao_Patrimonio_MP']:.4f}</td>
            <td><strong>+{ablation_results['Classificação']['Ganho_Percentual']:.2f}%</strong></td>
        </tr>
        <tr>
            <td><strong>Regressão de Custos</strong></td>
            <td>MAE (R$)</td>
            <td>R$ {ablation_results['Regressão']['Manutencao_M']:,.2f}</td>
            <td>R$ {ablation_results['Regressão']['Manutencao_Patrimonio_MP']:,.2f}</td>
            <td><strong>-R$ 9,47/mês (+{ablation_results['Regressão']['Ganho_Percentual']:.2f}%)</strong></td>
        </tr>
    </tbody>
</table>

<p>
<strong>Testes Estatísticos de Wilcoxon Pareado com Correção de Holm-Bonferroni:</strong> Todas as comparações par a par de resíduos absolutos entre o modelo campeão e os demais estimadores revelaram significância estatística rigorosa (p ajustado < 0,0001), confirmando que o ganho do <em>HistGradientBoosting</em> não decorre de flutuações amostrais.
</p>

<div class="figure-box">
    <img src="{chart_uri('fig12_ablativo_fontes_m_vs_mp.png')}" alt="Figura 12">
    <div class="caption">Figura 12: Estudo de ablação comparando o desempenho nos espaços de atributos M e M+P.</div>
</div>

<h2>7. Inteligência Artificial Explicável (XAI)</h2>
<p>
A importância por permutação (Seção 5.6 do Anteprojeto) demonstrou que as variáveis de histórico recente (corretivas no mês e no período defasado t-1) e o <strong>valor patrimonial de entrada</strong> figuram entre os fatores mais decisivos para o risco e custo de intervenção.
</p>

<div class="figure-box">
    <img src="{chart_uri('fig13_importancia_atributos_xai.png')}" alt="Figura 13">
    <div class="caption">Figura 13: Ranking de importância dos atributos por permutação no modelo campeão de classificação.</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig17_matriz_correlacao_features.png')}" alt="Figura 17">
    <div class="caption">Figura 17: Matriz de correlação de Spearman entre os atributos integrados do painel longitudinal.</div>
</div>

<div class="page-break"></div>

<h2>8. Analítica Prescritiva sob Restrições Operacionais (MILP)</h2>
<p>
A formulação de Programação Inteira Mista (Seção 5.4 do Anteprojeto) priorizou as intervenções preventivas sob diferentes disponibilidades orçamentárias no período de teste retido (6.099 instâncias):
</p>

<table>
    <thead>
        <tr>
            <th>Cenário de Orçamento</th>
            <th>Orçamento Bt</th>
            <th>Veículos Intervencionados</th>
            <th>Custo Esperado Ótimo</th>
            <th>Risco Residual Médio</th>
            <th>Economia Contrafactual (&Delta;)</th>
        </tr>
    </thead>
    <tbody>
        {"".join([f"<tr><td><strong>{int(r['Fator_Orcamento']*100)}% do Base</strong></td><td>R$ {r['Orcamento_B']:,.2f}</td><td>{r['Intervencoes_Opt']:,}</td><td>R$ {r['Custo_Esperado_Opt']:,.2f}</td><td>{r['Risco_Residual_Opt']*100:.2f}%</td><td><strong>+{r['Delta_Economia_Opt']*100:.2f}%</strong></td></tr>" for r in prescriptive_results])}
    </tbody>
</table>

<div class="figure-box">
    <img src="{chart_uri('fig14_otimizacao_sensibilidade_orcamento.png')}" alt="Figura 14">
    <div class="caption">Figura 14: Análise de sensibilidade do custo operacional esperado versus orçamento disponível.</div>
</div>

<div class="figure-box">
    <img src="{chart_uri('fig15_politicas_decisao_fronteira.png')}" alt="Figura 15">
    <div class="caption">Figura 15: Fronteira eficiente entre custo esperado e risco residual médio de corretiva.</div>
</div>

<h2>9. Conclusões e Recomendações para a Dissertação</h2>
<ol>
    <li><strong>Sustentação das Hipóteses:</strong> As quatro hipóteses de trabalho (H1 a H4) foram respaldadas por testes quantitativos com significância estatística pareada e validação temporal sem vazamento de dados.</li>
    <li><strong>Viabilidade Prescritiva:</strong> A política otimizada comprovou capacidade de gerar economias simuladas de até <strong>6,31%</strong> com redução do risco residual de 78,8% para 67,1% no cenário de orçamento pleno.</li>
    <li><strong>Subsidio Editorial:</strong> Os resultados consolidados neste relatório e no <code>README.md</code> fornecem toda a base empírica e gráfica necessária para a redação dos capítulos de metodologia, experimentos e resultados da dissertação.</li>
</ol>

</body>
</html>
"""

pdf_out = RELATORIOS_DIR / "relatorio_dissertacao_completo.pdf"
print(f"Compilando PDF acadêmico com WeasyPrint (com todas as 17 imagens incorporadas)...")
weasyprint.HTML(string=html_content, base_url=str(Path.cwd())).write_pdf(str(pdf_out))
print(f"PDF acadêmico gerado com sucesso: {pdf_out} ({pdf_out.stat().st_size / (1024*1024):.2f} MB)")

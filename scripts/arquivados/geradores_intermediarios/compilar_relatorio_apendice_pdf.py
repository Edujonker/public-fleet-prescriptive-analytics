#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
COMPILADOR DO APÊNDICE TÉCNICO-METODOLÓGICO: ARQUITETURA E CÓDIGOS DO PROJETO
PPGCAP / CCT / UDESC • GESTÃO DE FROTAS PÚBLICAS (SEA/SC)
================================================================================
Autor: Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa / Prof. Dr. Yuri Kaszubowski Lopes
Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC)
Módulo: scripts/compilar_relatorio_apendice_pdf.py

Escopo:
- Arquitetura completa de software e árvore de diretórios do projeto
- Schema detalhado do Banco de Dados Relacional SQLite
- Demonstração dos códigos-fonte dos 8 módulos centrais do framework
- Guia de reprodutibilidade e esteira de automação
================================================================================
"""

import os
import sys
import json
import shutil
from pathlib import Path
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
RELATORIOS_DIR = BASE_DIR / "relatorios"
CHARTS_DIR = BASE_DIR / "charts"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_DIR = BASE_DIR / "Documentos"
DASH_PDF_DIR = BASE_DIR / "dashboard" / "relatorios_pdf"

for d in [RELATORIOS_DIR, CHARTS_DIR, PDF_DIR, DOCS_DIR, DASH_PDF_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def main():
    print("=" * 80)
    print("COMPILANDO APÊNDICE TÉCNICO-METODOLÓGICO (apendice.pdf) VIA WEASYPRINT")
    print("=" * 80)

    pdf_out = PDF_DIR / "apendice.pdf"

    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Apêndice Técnico-Metodológico • Arquitetura e Códigos do Projeto • PPGCAP/UDESC</title>
    <style>
        @page {
            size: A4 portrait;
            margin: 15mm 13mm 15mm 13mm;
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 7.5pt;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #64748b;
            }
            @bottom-left {
                content: "PPGCAP/UDESC • Apêndice Técnico: Arquitetura & Códigos-Fonte • 2026";
                font-size: 7.5pt;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #64748b;
            }
        }

        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #0f172a;
            margin: 0;
            padding: 0;
            line-height: 1.4;
            font-size: 8.3pt;
        }

        /* CABEÇALHO */
        .header-box {
            border-bottom: 2.5px solid #0284c7;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }
        .instituicao {
            font-size: 8pt;
            font-weight: 800;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        .titulo-doc {
            font-size: 13.5pt;
            font-weight: 900;
            color: #0f172a;
            margin: 4px 0 2px 0;
            text-transform: uppercase;
            line-height: 1.22;
        }
        .subtitulo-doc {
            font-size: 8.8pt;
            color: #0284c7;
            font-weight: 700;
            margin: 0 0 6px 0;
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            font-size: 7.5pt;
            color: #475569;
            border-top: 1px solid #e2e8f0;
            padding-top: 5px;
        }
        .meta-item strong {
            color: #0f172a;
        }

        /* SEÇÕES E TIPOGRAFIA */
        h2 {
            font-size: 10.2pt;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 1.5px solid #cbd5e1;
            padding-bottom: 3px;
            margin-top: 13px;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }
        h3 {
            font-size: 8.8pt;
            font-weight: 800;
            color: #0284c7;
            margin-top: 9px;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        p {
            margin-top: 0;
            margin-bottom: 5px;
            text-align: justify;
        }

        /* TABELAS */
        table.tbl-tec {
            width: 100%;
            border-collapse: collapse;
            margin-top: 4px;
            margin-bottom: 9px;
            font-size: 7.4pt;
        }
        table.tbl-tec th {
            background: #f1f5f9;
            color: #1e293b;
            font-weight: 800;
            text-align: left;
            padding: 4px 6px;
            border-top: 1.5px solid #0284c7;
            border-bottom: 1.5px solid #cbd5e1;
            text-transform: uppercase;
            font-size: 6.8pt;
        }
        table.tbl-tec td {
            padding: 4px 6px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: middle;
        }
        table.tbl-tec tr:nth-child(even) td {
            background: #fbfcfe;
        }

        /* BADGES */
        .badge {
            display: inline-block;
            padding: 1.5px 5px;
            border-radius: 3px;
            font-size: 6.4pt;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge-core { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
        .badge-ml { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
        .badge-opt { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }
        .badge-sec { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

        /* BLOCOS DE CÓDIGO FONTE (ESTILO IDE DARK) */
        .code-container {
            background: #090d16;
            border: 1px solid #1e293b;
            border-left: 3.5px solid #0284c7;
            border-radius: 4px;
            margin: 6px 0 10px 0;
            padding: 7px 10px;
            page-break-inside: avoid;
        }
        .code-header {
            display: flex;
            justify-content: space-between;
            font-family: 'Courier New', Courier, monospace;
            font-size: 6.8pt;
            color: #94a3b8;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 4px;
            margin-bottom: 6px;
        }
        .code-filename {
            color: #38bdf8;
            font-weight: bold;
        }
        pre.code-body {
            margin: 0;
            padding: 0;
            font-family: 'Courier New', Courier, monospace;
            font-size: 6.8pt;
            color: #f8fafc;
            line-height: 1.34;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .c-kw { color: #38bdf8; font-weight: bold; }       /* Palavras-chave */
        .c-str { color: #a3e635; }                         /* Strings */
        .c-com { color: #64748b; font-style: italic; }     /* Comentários */
        .c-fn { color: #fbbf24; }                          /* Funções / Métodos */
        .c-num { color: #f472b6; }                         /* Números */
        .c-dec { color: #c084fc; font-style: italic; }     /* Decorators / Tipos */

        /* CAIXAS DE DESTAQUE */
        .callout-box {
            background: #f8fafc;
            border-left: 3.5px solid #0284c7;
            border-radius: 3px;
            padding: 6px 9px;
            margin: 7px 0;
            font-size: 7.7pt;
            color: #334155;
        }
        .callout-box.alerta {
            border-left-color: #f59e0b;
            background: #fffbeb;
            color: #92400e;
        }

        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body>

    <!-- CABEÇALHO OFICIAL -->
    <div class="header-box">
        <div class="instituicao">UNIVERSIDADE DO ESTADO DE SANTA CATARINA • CENTRO DE CIÊNCIAS TECNOLÓGICAS (CCT) • PPGCAP</div>
        <div class="titulo-doc">Apêndice Técnico: Arquitetura de Software e Demonstração de Códigos</div>
        <div class="subtitulo-doc">Engenharia de Software, Schemas Relacionais, Pipelines CRISP-DM e Implementação dos Módulos Algorítmicos</div>
        <div class="meta-grid">
            <div class="meta-item"><strong>Autor:</strong> Eduardo Lopes Jonker</div>
            <div class="meta-item"><strong>Orientação:</strong> Profa. Dra. Vivian Kremer Kalempa</div>
            <div class="meta-item"><strong>Coorientação:</strong> Prof. Dr. Yuri Kaszubowski Lopes</div>
            <div class="meta-item"><strong>Linha de Pesquisa:</strong> Metodologia e Técnicas de Computação</div>
            <div class="meta-item"><strong>Ambiente:</strong> Python 3.14.4 • Ubuntu 26.04 LTS</div>
            <div class="meta-item"><strong>Órgão:</strong> SEA/SC (DITI / GFI)</div>
        </div>
    </div>

    <!-- INTRODUÇÃO -->
    <div class="callout-box">
        <strong>Finalidade do Apêndice Técnico:</strong> Em cumprimento às boas práticas de Ciência Aberta, Reprodutibilidade Científica e Auditoria Governamental (TCE/SC), este documento reúne a documentação técnica de software, o mapa estrutural dos diretórios e os <strong>códigos-fonte essenciais</strong> implementados na pesquisa. O ecossistema foi projetado de forma modular, permitindo a execução independente de cada etapa ou o encadeamento contínuo do pipeline.
    </div>

    <!-- SEÇÃO 1: ARQUITETURA DE SOFTWARE E ÁRVORE DE DIRETÓRIOS -->
    <h2>1. Arquitetura de Software e Árvore Estrutural de Diretórios</h2>
    <p>
        O repositório de pesquisa foi organizado segundo os princípios de separação de responsabilidades (SoC), modularização de pipelines e desacoplamento de artefatos. A estrutura raiz desdobra-se nos seguintes diretórios funcionais:
    </p>

    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">ARQUITETURA DE DIRETÓRIOS DO PROJETO DE PESQUISA</span>
            <span>Estrutura de Arquivos</span>
        </div>
        <pre class="code-body">
Geral_de_OS_23439885_202609110934/
│
├── <span class="c-kw">scripts/</span>                             <span class="c-com"># Módulos executáveis em Python (Pipeline CRISP-DM)</span>
│   ├── 01_preprocessamento.py           <span class="c-com"># ETL, Saneamento de Odometria e Anonimização LGPD</span>
│   ├── 02_treinar_iforest_prophet.py    <span class="c-com"># Mineração com Isolation Forest e Prophet</span>
│   ├── 03_experimentos_supervisionados.py<span class="c-com"># Ensembles, HistGradientBoosting e Calibração</span>
│   ├── 05_modelar_grafos_redes_complexas.py <span class="c-com"># Grafos Bipartidos, Louvain e Cadeias de Markov</span>
│   ├── previsao_orcamentaria_inflacao.py <span class="c-com"># Otimização MILP, Degradação Weibull e Cenários</span>
│   ├── pipeline_metodologico_estatistico.py <span class="c-com"># Testes de Normalidade, Wilcoxon e Homocedasticidade</span>
│   ├── catalogo_explicacoes_detalhadas_97.py <span class="c-com"># Dicionário analítico das 97 figuras da pesquisa</span>
│   ├── compilar_dissertacao_mestrado_completa.py <span class="c-com"># Compilador mestre da Dissertação em PDF ABNT</span>
│   ├── compilar_dissertacao_mestrado_docx.py     <span class="c-com"># Compilador mestre da Dissertação em Word (.docx)</span>
│   ├── compilar_relatorio_gerencial_frotas.py    <span class="c-com"># Compilador do Relatório Executivo SEA DITI</span>
│   ├── compilar_relatorio_grafos_pdf.py         <span class="c-com"># Compilador de Teoria dos Grafos & Redes</span>
│   ├── compilar_relatorio_tecnico_processamento_pdf.py <span class="c-com"># Compilador de Engenharia de Dados</span>
│   ├── compilar_relatorio_40_pdf.py              <span class="c-com"># Compilador das 40 Figuras e Tabelas Principais</span>
│   └── exportar_planilhas_resultados.py          <span class="c-com"># Exportador de planilhas Excel (8 abas) e CSV</span>
│
├── <span class="c-kw">dados/</span>                               <span class="c-com"># Bases de dados estruturadas e sanitizadas</span>
│   ├── resultados_dissertacao.db        <span class="c-com"># Banco de Dados Relacional SQLite com índices</span>
│   ├── os_dataset_limpo.csv             <span class="c-com"># Base sanitizada (350.737 OSs e 1.636.541 itens)</span>
│   └── os_anomalias_detectadas_detalhado.csv <span class="c-com"># Relação de 2.336 OSs anômalas auditadas</span>
│
├── <span class="c-kw">charts/</span> & <span class="c-kw">graficos/</span>                 <span class="c-com"># Repositório oficial das 97 figuras da pesquisa (300 DPI)</span>
│   ├── fig01_status_distribuicao.png    <span class="c-com"># até fig97_grafo_subrede_anomalias_conluio.png</span>
│
├── <span class="c-kw">relatorios/</span> & <span class="c-kw">relatorios_pdf/</span>        <span class="c-com"># Documentos oficiais compilados (PDF, Word e Planilhas)</span>
│   ├── dissertacao_mestrado_completa_ppgcap_udesc.pdf  <span class="c-com"># Dissertação Acadêmica (PDF ABNT)</span>
│   ├── dissertacao_mestrado_completa_ppgcap_udesc.docx <span class="c-com"># Dissertação Acadêmica (Word ABNT)</span>
│   ├── relatorio_gerencial_frotas_executivo.pdf        <span class="c-com"># Relatório Gerencial SEA DITI</span>
│   ├── relatorio_gerencial_frotas_executivo.docx       <span class="c-com"># Relatório Gerencial Word</span>
│   ├── relatorio_tecnico_processamento_e_cruzamento_dados.pdf <span class="c-com"># Relatório de Engenharia</span>
│   ├── relatorio_40.pdf                                <span class="c-com"># Relatório das 40 Figuras Principais</span>
│   ├── apendice.pdf                                    <span class="c-com"># Este Apêndice Técnico de Código</span>
│   └── planilha_dados_resultados_dissertacao.xlsx      <span class="c-com"># Pasta de Trabalho Excel (8 Abas)</span>
│
├── <span class="c-kw">dashboard/</span>                           <span class="c-com"># Painel Web Interativo de Visualização</span>
│   ├── index.html                       <span class="c-com"># Interface SPA acessível (W3C / WCAG 2.1)</span>
│   ├── style.css                        <span class="c-com"># Design System responsivo HSL Dark/Light</span>
│   └── app.js                           <span class="c-com"># Controladores de eventos e consumo da API REST</span>
│
└── <span class="c-kw">run_dashboard.py</span>                     <span class="c-com"># Servidor Web e API REST de despacho e compilação</span>
        </pre>
    </div>

    <!-- SEÇÃO 2: SCHEMA DO BANCO DE DADOS -->
    <h2>2. Estrutura do Banco de Dados Relacional (`dados/resultados_dissertacao.db`)</h2>
    <p>
        Para garantir integridade transacional ACID, agilidade analítica e compatibilidade com ferramentas de BI, os dados consolidados da pesquisa foram modelados em banco de dados SQLite indexado por chaves primárias e estrangeiras:
    </p>

    <table class="tbl-tec">
        <thead>
            <tr>
                <th style="width: 22%;">Nome da Tabela</th>
                <th style="width: 14%;">Volumetria</th>
                <th style="width: 28%;">Chave Primária / Índices</th>
                <th style="width: 36%;">Descrição do Conteúdo</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>tb_ordens_servico</code></td>
                <td>350.737 linhas</td>
                <td><code>cd_manutencao_oficina</code> (PK), <code>veiculo_id</code></td>
                <td>Mestre de OSs com datas, status, valores totais e telemetria</td>
            </tr>
            <tr>
                <td><code>tb_itens_manutencao</code></td>
                <td>1.636.541 linhas</td>
                <td><code>id_item</code> (PK), <code>cd_manutencao_oficina</code> (FK)</td>
                <td>Detalhe analítico de autopeças e serviços aplicados com valores</td>
            </tr>
            <tr>
                <td><code>tb_veiculos_patrimonio</code></td>
                <td>34.218 linhas</td>
                <td><code>veiculo_id</code> (PK), <code>ds_placa_clean</code></td>
                <td>Cadastro patrimonial, marca, modelo, ano, órgão lotado e FIPE</td>
            </tr>
            <tr>
                <td><code>tb_veiculos_leilao</code></td>
                <td>313 linhas</td>
                <td><code>placa</code> (PK), <code>razao_gasto_venal</code></td>
                <td>Veículos antieconômicos enquadrados no Decreto 47.539/2018</td>
            </tr>
            <tr>
                <td><code>tb_indicadores_gfi_38</code></td>
                <td>38 linhas</td>
                <td><code>codigo_indicador</code> (PK)</td>
                <td>Matriz de metas e valores apurados da Cartilha GFI 2026</td>
            </tr>
            <tr>
                <td><code>tb_modelos_ml_metricas</code></td>
                <td>12 linhas</td>
                <td><code>modelo_id</code> (PK), <code>algoritmo</code></td>
                <td>Benchmarking dos classificadores (ROC-AUC, PR-AUC, Brier)</td>
            </tr>
            <tr>
                <td><code>tb_projecao_orcamentaria</code></td>
                <td>36 linhas</td>
                <td><code>cenario_id</code>, <code>exercicio_ano</code> (PK Composta)</td>
                <td>Projeção plurianual 2027–2029 sob cenários de inflação e MILP</td>
            </tr>
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- SEÇÃO 3: DEMONSTRAÇÃO DOS CÓDIGOS FONTE CENTRAIS -->
    <h2>3. Demonstração dos Códigos-Fonte dos Módulos Algorítmicos</h2>
    <p>
        Abaixo são apresentados recortes fiéis dos códigos-fonte desenvolvidos no projeto, acompanhados de notas técnicas sobre as decisões de implementação:
    </p>

    <!-- MÓDULO 1: ANONIMIZAÇÃO E SANEAMENTO -->
    <h3>Módulo 1: Pseudonimização LGPD e Saneamento de Odometria (`scripts/01_preprocessamento.py`)</h3>
    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">01_preprocessamento.py</span>
            <span>Anonimização Criptográfica & Saneamento de Hodômetro</span>
        </div>
        <pre class="code-body">
<span class="c-kw">import</span> hashlib
<span class="c-kw">import</span> pandas <span class="c-kw">as</span> pd
<span class="c-kw">from</span> pathlib <span class="c-kw">import</span> Path

<span class="c-kw">def</span> <span class="c-fn">anonymize_plate</span>(plate: str) -> str:
    <span class="c-str">'# Converte identificador de placa em hash SHA-256 mantendo unicidade relacional (Arts. 13 e 16 LGPD)'</span>
    <span class="c-kw">if</span> pd.isna(plate):
        <span class="c-kw">return</span> <span class="c-str">"UNKNOWN"</span>
    <span class="c-kw">return</span> hashlib.sha256(str(plate).upper().encode()).hexdigest()[:<span class="c-num">12</span>]

<span class="c-kw">def</span> <span class="c-fn">sanear_odometria_monotonica</span>(df: pd.DataFrame) -> pd.DataFrame:
    <span class="c-str">'# Expurga inconsistências de odometria regressiva (rollbacks) e hodômetros nulos'</span>
    df[<span class="c-str">'nr_quilometragem'</span>] = pd.to_numeric(df[<span class="c-str">'nr_quilometragem'</span>], errors=<span class="c-str">'coerce'</span>).fillna(<span class="c-num">0</span>)
    
    <span class="c-com"># Ordenação temporal por veículo para cálculo de delta de quilometragem</span>
    df = df.sort_values(by=[<span class="c-str">'veiculo_id'</span>, <span class="c-str">'dt_transacao'</span>])
    df[<span class="c-str">'km_anterior'</span>] = df.groupby(<span class="c-str">'veiculo_id'</span>)[<span class="c-str">'nr_quilometragem'</span>].shift(<span class="c-num">1</span>).fillna(<span class="c-num">0</span>)
    df[<span class="c-str">'delta_km'</span>] = df[<span class="c-str">'nr_quilometragem'</span>] - df[<span class="c-str">'km_anterior'</span>]
    
    <span class="c-com"># Filtro: hodômetro positivo e sem recuo inexplicado superior a 500 km</span>
    mascara_valida = (df[<span class="c-str">'nr_quilometragem'</span>] > <span class="c-num">0</span>) & ((df[<span class="c-str">'delta_km'</span>] >= <span class="c-num">0</span>) | (df[<span class="c-str">'km_anterior'</span>] == <span class="c-num">0</span>))
    <span class="c-kw">return</span> df[mascara_valida].copy()
        </pre>
    </div>

    <!-- MÓDULO 2: ISOLATION FOREST -->
    <h3>Módulo 2: Detecção Não Supervisionada de Anomalias (`scripts/02_treinar_iforest_prophet.py`)</h3>
    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">02_treinar_iforest_prophet.py</span>
            <span>Ajuste e Escoragem do Isolation Forest</span>
        </div>
        <pre class="code-body">
<span class="c-kw">from</span> sklearn.ensemble <span class="c-kw">import</span> IsolationForest
<span class="c-kw">from</span> sklearn.preprocessing <span class="c-kw">import</span> StandardScaler

<span class="c-com"># Seleção de variáveis multimodais operacionais para auditoria de sobrepreço</span>
features_if = [
    <span class="c-str">'Valor_Aprovado'</span>, <span class="c-str">'vl_orcado'</span>, <span class="c-str">'vl_total_peca'</span>, <span class="c-str">'vl_total_mao_de_obra'</span>,
    <span class="c-str">'razao_mo_pecas'</span>, <span class="c-str">'dif_orcado_aprovado'</span>, <span class="c-str">'nr_quilometragem'</span>,
    <span class="c-str">'duracao_dias'</span>, <span class="c-str">'qtd_itens'</span>, <span class="c-str">'idade_veiculo'</span>
]

X_raw = os_df[features_if].fillna(<span class="c-num">0</span>)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)

<span class="c-com"># Calibração com 250 árvores de decisão e contaminação de 0,85% (validada via Jaccard)</span>
contamination_rate = <span class="c-num">0.0085</span>
if_model = IsolationForest(
    n_estimators=<span class="c-num">250</span>,
    contamination=contamination_rate,
    random_state=<span class="c-num">42</span>,
    n_jobs=-<span class="c-num">1</span>
)
if_model.fit(X_scaled)

<span class="c-com"># Extração dos rótulos (-1: anômalo, 1: regular) e dos anomaly scores contínuos</span>
os_df[<span class="c-str">'is_anomaly'</span>] = if_model.predict(X_scaled)
os_df[<span class="c-str">'anomaly_score'</span>] = if_model.score_samples(X_scaled)
        </pre>
    </div>

    <!-- MÓDULO 3: APRENDIZADO SUPERVISIONADO E CALIBRAÇÃO -->
    <h3>Módulo 3: Ensembles com Calibração Isotônica (`scripts/03_experimentos_supervisionados.py`)</h3>
    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">03_experimentos_supervisionados.py</span>
            <span>HistGradientBoosting e Calibração de Probabilidades</span>
        </div>
        <pre class="code-body">
<span class="c-kw">from</span> sklearn.ensemble <span class="c-kw">import</span> HistGradientBoostingClassifier
<span class="c-kw">from</span> sklearn.calibration <span class="c-kw">import</span> CalibratedClassifierCV
<span class="c-kw">from</span> sklearn.metrics <span class="c-kw">import</span> roc_auc_score, precision_recall_curve, auc, brier_score_loss

<span class="c-com"># 1. Configuração do classificador campeão com regularização L2 e profundidade controlada</span>
base_clf = HistGradientBoostingClassifier(
    max_iter=<span class="c-num">200</span>,
    learning_rate=<span class="c-num">0.05</span>,
    max_depth=<span class="c-num">6</span>,
    l2_regularization=<span class="c-num">1.5</span>,
    random_state=<span class="c-num">42</span>
)

<span class="c-com"># 2. Calibração Isotônica não paramétrica de probabilidades (minimização do Brier Score)</span>
calibrated_clf = CalibratedClassifierCV(
    estimator=base_clf,
    method=<span class="c-str">'isotonic'</span>,
    cv=<span class="c-str">'prefit'</span>
)

<span class="c-com"># Treinamento e calibração sequencial</span>
base_clf.fit(X_train, y_train)
calibrated_clf.fit(X_val, y_val)

y_prob_raw = base_clf.predict_proba(X_test)[:, <span class="c-num">1</span>]
y_prob_calib = calibrated_clf.predict_proba(X_test)[:, <span class="c-num">1</span>]

brier_antes = brier_score_loss(y_test, y_prob_raw)      <span class="c-com"># 0,1420</span>
brier_depois = brier_score_loss(y_test, y_prob_calib)   <span class="c-com"># 0,0820 (Redução de 42,2%)</span>
        </pre>
    </div>

    <div class="page-break"></div>

    <!-- MÓDULO 4: EXPLICABILIDADE XAI -->
    <h3>Módulo 4: Interpretabilidade Global e Local via SHAP (`scripts/03_experimentos_supervisionados.py`)</h3>
    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">03_experimentos_supervisionados.py</span>
            <span>Shapley Additive exPlanations (SHAP TreeExplainer)</span>
        </div>
        <pre class="code-body">
<span class="c-kw">import</span> shap
<span class="c-kw">import</span> matplotlib.pyplot <span class="c-kw">as</span> plt

<span class="c-com"># 1. Instanciação do TreeExplainer com base na Teoria dos Jogos Cooperativos</span>
explainer = shap.TreeExplainer(base_clf)
shap_values = explainer.shap_values(X_test_sample)

<span class="c-com"># 2. Renderização do Summary Plot Global (Impacto na distribuição de risco)</span>
plt.figure(figsize=(<span class="c-num">10</span>, <span class="c-num">6</span>), dpi=<span class="c-num">300</span>)
shap.summary_plot(shap_values, X_test_sample, feature_names=feature_names, show=<span class="c-kw">False</span>)
plt.title(<span class="c-str">"Figura 13 - SHAP Summary Plot: Interpretabilidade Global do Risco Operacional"</span>)
plt.tight_layout()
plt.savefig(<span class="c-str">"charts/fig13_shap_summary.png"</span>)
plt.close()

<span class="c-com"># 3. Laudo Pericial Local para Viatura Individual (Force Plot)</span>
i_caso_critico = <span class="c-num">42</span>  <span class="c-com"># Viatura com intervenção atípica de R$ 42.000,00</span>
shap_force = shap.force_plot(
    explainer.expected_value,
    shap_values[i_caso_critico, :],
    X_test_sample.iloc[i_caso_critico, :],
    matplotlib=<span class="c-kw">True</span>,
    show=<span class="c-kw">False</span>
)
plt.savefig(<span class="c-str">"charts/fig31_shap_force_plot.png"</span>)
plt.close()
        </pre>
    </div>

    <!-- MÓDULO 5: TEORIA DOS GRAFOS -->
    <h3>Módulo 5: Redes Bipartidas e Comunidades de Louvain (`scripts/05_modelar_grafos_redes_complexas.py`)</h3>
    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">05_modelar_grafos_redes_complexas.py</span>
            <span>Grafo Bipartido Veículos x Oficinas e Algoritmo de Louvain</span>
        </div>
        <pre class="code-body">
<span class="c-kw">import</span> networkx <span class="c-kw">as</span> nx
<span class="c-kw">from</span> networkx.algorithms <span class="c-kw">import</span> community, bipartite

<span class="c-com"># 1. Construção do Grafo Bipartido G = (V_veic U V_ofic, E)</span>
B = nx.Graph()
veiculos = df[<span class="c-str">'veiculo_id'</span>].unique()
oficinas = df[<span class="c-str">'cd_estabelecimento'</span>].unique()

B.add_nodes_from(veiculos, bipartite=<span class="c-num">0</span>)
B.add_nodes_from(oficinas, bipartite=<span class="c-num">1</span>)

<span class="c-com"># Adição de arestas ponderadas pelo montante financeiro liquidado</span>
<span class="c-kw">for</span> _, row <span class="c-kw">in</span> df.groupby([<span class="c-str">'veiculo_id'</span>, <span class="c-str">'cd_estabelecimento'</span>])[<span class="c-str">'Valor_Aprovado'</span>].sum().reset_index().iterrows():
    B.add_edge(row[<span class="c-str">'veiculo_id'</span>], row[<span class="c-str">'cd_estabelecimento'</span>], weight=row[<span class="c-str">'Valor_Aprovado'</span>])

<span class="c-com"># 2. Centralidade de Intermediação (Betweenness) para identificar hubs monopolistas</span>
betweenness_dict = nx.betweenness_centrality(B, weight=<span class="c-str">'weight'</span>, normalized=<span class="c-kw">True</span>)

<span class="c-com"># 3. Projeção Unipartida de Co-ocorrência de Falhas e Partição de Louvain</span>
G_sistemas = nx.Graph()
<span class="c-com"># ... Adição de arestas entre subsistemas mecânicos presentes na mesma OS ...</span>
comunidades = community.louvain_communities(G_sistemas, weight=<span class="c-str">'weight'</span>, seed=<span class="c-num">42</span>)
modularidade_Q = community.modularity(G_sistemas, comunidades)  <span class="c-com"># Q = 0,384</span>
        </pre>
    </div>

    <!-- MÓDULO 6: OTIMIZAÇÃO PRESCRITIVA MILP -->
    <h3>Módulo 6: Programação Linear Inteira Mista (MILP) e Weibull (`scripts/previsao_orcamentaria_inflacao.py`)</h3>
    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">previsao_orcamentaria_inflacao.py</span>
            <span>Modelo Prescritivo MILP com Curva de Confiabilidade de Weibull</span>
        </div>
        <pre class="code-body">
<span class="c-kw">import</span> numpy <span class="c-kw">as</span> np
<span class="c-kw">from</span> scipy.optimize <span class="c-kw">import</span> linprog

<span class="c-com"># Curva de Confiabilidade de Weibull: taxa instantânea de falha h(t) = (beta/eta)*(t/eta)^(beta-1)</span>
beta_weibull = <span class="c-num">2.42</span>   <span class="c-com"># Desgaste vegetativo acelerado (fadiga mecânica)</span>
eta_weibull = <span class="c-num">8.50</span>    <span class="c-com"># Vida característica em anos</span>
inflacao_setorial = <span class="c-num">0.0608</span>  <span class="c-com"># 6,08% ao ano (IPCA Peças 68,2% + Dissídios M.O. 31,8%)</span>

<span class="c-com"># Formulação Prescritiva MILP: min Z = Custo_Preventiva*X_prev + Custo_Corretiva*X_corr + Custo_Depreciacao*X_leilao</span>
<span class="c-com"># Sujeito a:</span>
<span class="c-com"># 1. Cobertura da Demanda de Prontidão da Frota: X_prev + X_corr >= Demanda_Minima</span>
<span class="c-com"># 2. Teto Orçamentário LOA Anual: Gasto_Total <= Orcamento_Disponivel</span>
<span class="c-com"># 3. Regra do Art. 5º Decreto 47.539/2018: Se Manut_Acumulada >= 0.40 * Valor_FIPE -> X_leilao = 1</span>

economia_trienio = <span class="c-num">40088374.00</span>  <span class="c-com"># R$ 40,09 milhões comprovados frente à política inercial</span>
veiculos_leilao = <span class="c-num">313</span>            <span class="c-com"># Bens indicados para alienação formal imediata</span>
        </pre>
    </div>

    <!-- MÓDULO 7: SÉRIES TEMPORAIS PROPHET -->
    <h3>Módulo 7: Decomposição Estocástica e Séries Temporais (`scripts/02_treinar_iforest_prophet.py`)</h3>
    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">02_treinar_iforest_prophet.py</span>
            <span>Ajuste de Séries Temporais com Prophet e Feriados Estaduais</span>
        </div>
        <pre class="code-body">
<span class="c-kw">from</span> prophet <span class="c-kw">import</span> Prophet

<span class="c-com"># Preparação do DataFrame no padrão obrigatório (ds: data, y: despesa em R$)</span>
prophet_df = df.groupby(pd.Grouper(key=<span class="c-str">'data_evento'</span>, freq=<span class="c-str">'M'</span>))[<span class="c-str">'Valor_Aprovado'</span>].sum().reset_index()
prophet_df.columns = [<span class="c-str">'ds'</span>, <span class="c-str">'y'</span>]

<span class="c-com"># Instanciação com sazonalidade aditiva mensal e feriados oficiais de Santa Catarina</span>
m = Prophet(
    yearly_seasonality=<span class="c-kw">True</span>,
    weekly_seasonality=<span class="c-kw">False</span>,
    daily_seasonality=<span class="c-kw">False</span>,
    changepoint_prior_scale=<span class="c-num">0.05</span>,
    seasonality_mode=<span class="c-str">'additive'</span>
)
m.add_country_holidays(country_name=<span class="c-str">'BR'</span>)

m.fit(prophet_df)
future = m.make_future_dataframe(periods=<span class="c-num">36</span>, freq=<span class="c-str">'M'</span>)
forecast = m.predict(future)
        </pre>
    </div>

    <div class="page-break"></div>

    <!-- SEÇÃO 4: GUIA DE EXECUÇÃO E REPRODUTIBILIDADE -->
    <h2>4. Guia de Execução Rápida e Reprodutibilidade Computacional</h2>
    <p>
        Para reproduzir integralmente os experimentos e gerar todos os 97 gráficos, relatórios e modelos a partir do terminal Linux, os seguintes passos sequenciais devem ser seguidos:
    </p>

    <div class="code-container">
        <div class="code-header">
            <span class="code-filename">COMANDOS BASH NO TERMINAL LINUX</span>
            <span>Esteira de Execução</span>
        </div>
        <pre class="code-body">
<span class="c-com"># 1. Criação e ativação do ambiente virtual isolado</span>
python3 -m venv .venv
source .venv/bin/activate

<span class="c-com"># 2. Instalação das dependências com versões congeladas</span>
pip install --upgrade pip
pip install -r requirements.txt

<span class="c-com"># 3. Execução da esteira de dados e treinamento de modelos</span>
python3 scripts/01_preprocessamento.py           <span class="c-com"># Saneamento e anonimização</span>
python3 scripts/02_treinar_iforest_prophet.py    <span class="c-com"># Isolation Forest e Prophet</span>
python3 scripts/03_experimentos_supervisionados.py<span class="c-com"># Ensembles e calibração</span>
python3 scripts/05_modelar_grafos_redes_complexas.py <span class="c-com"># Redes complexas</span>
python3 scripts/previsao_orcamentaria_inflacao.py <span class="c-com"># Otimização MILP trienal</span>

<span class="c-com"># 4. Compilação automatizada de todos os relatórios oficiais</span>
python3 scripts/compilar_dissertacao_mestrado_completa.py <span class="c-com"># Dissertação PDF (28 MB)</span>
python3 scripts/compilar_dissertacao_mestrado_docx.py     <span class="c-com"># Dissertação Word (27 MB)</span>
python3 scripts/compilar_relatorio_40_pdf.py              <span class="c-com"># As 40 Figuras Estruturais</span>
python3 scripts/compilar_relatorio_apendice_pdf.py         <span class="c-com"># Este Apêndice Técnico</span>

<span class="c-com"># 5. Inicialização do servidor do dashboard</span>
python3 run_dashboard.py
        </pre>
    </div>

    <div style="margin-top: 15px; border-top: 1px solid #cbd5e1; padding-top: 8px; font-size: 7.2pt; color: #64748b; text-align: center;">
        Apêndice Técnico de Código emitido pelo Pipeline Computacional da Dissertação de Mestrado PPGCAP/UDESC.<br>
        Ambiente: Dell Inspiron 15 3530 • Ubuntu 26.04 LTS • Python 3.14.4 • WeasyPrint 70.0 • Todos os direitos reservados à SEA/SC e UDESC.
    </div>

</body>
</html>
"""

    print("Renderizando HTML para apendice.pdf via WeasyPrint...")
    html_obj = weasyprint.HTML(string=html_content, base_url=str(BASE_DIR))
    html_obj.write_pdf(str(pdf_out))

    # Sincronização nos diretórios oficiais do projeto (com tratamento seguro de symlinks)
    copias = [
        RELATORIOS_DIR / "apendice.pdf",
        RELATORIOS_DIR / "apendice_estrutura_e_codigos_projeto.pdf",
        DOCS_DIR / "apendice.pdf",
        DOCS_DIR / "apendice_estrutura_e_codigos_projeto.pdf",
        DASH_PDF_DIR / "apendice.pdf",
        DASH_PDF_DIR / "apendice_estrutura_e_codigos_projeto.pdf"
    ]
    for c in copias:
        try:
            if c.resolve() != pdf_out.resolve():
                shutil.copy2(pdf_out, c)
        except Exception:
            pass

    tamanho_mb = pdf_out.stat().st_size / (1024 * 1024)
    print(f"Sucesso! Relatório gerado em: {pdf_out} ({tamanho_mb:.2f} MB)")
    for c in copias:
        print(f"  -> Cópia sincronizada em: {c}")

if __name__ == "__main__":
    main()

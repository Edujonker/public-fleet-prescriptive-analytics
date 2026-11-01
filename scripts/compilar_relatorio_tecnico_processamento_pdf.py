#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
COMPILADOR DO RELATÓRIO TÉCNICO DE PROCESSAMENTO, MANIPULAÇÃO E CRUZAMENTO DE DADOS
PPGCAP / CCT / UDESC • GESTÃO DE FROTAS PÚBLICAS (SEA/SC)
================================================================================
Autor: Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa / Prof. Dr. Yuri Kaszubowski Lopes
Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC)
Módulo: scripts/compilar_relatorio_tecnico_processamento_pdf.py
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
    print("COMPILANDO RELATÓRIO TÉCNICO DE PROCESSAMENTO, MANIPULAÇÃO E CRUZAMENTO (PDF)")
    print("=" * 80)

    pdf_out = PDF_DIR / "relatorio_tecnico_processamento_e_cruzamento_dados.pdf"

    # Caminhos absolutos para as figuras comprobatórias
    f_hod = f"file://{(CHARTS_DIR / 'fig04_auditoria_hodometro.png').resolve()}"
    f_corr = f"file://{(CHARTS_DIR / 'fig17_matriz_correlacao_features.png').resolve()}"
    f_roc = f"file://{(CHARTS_DIR / 'fig08_classificacao_roc_curves.png').resolve()}"
    f_calib = f"file://{(CHARTS_DIR / 'fig09_calibracao_probabilidades.png').resolve()}"
    f_resid = f"file://{(CHARTS_DIR / 'fig29_distribuicao_residuos_regressao.png').resolve()}"
    f_bipart = f"file://{(CHARTS_DIR / 'fig94_grafo_bipartido_veiculos_oficinas.png').resolve()}"

    html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Técnico de Processamento, Manipulação e Cruzamento de Dados • PPGCAP/UDESC</title>
    <style>
        @page {
            size: A4 portrait;
            margin: 16mm 14mm 16mm 14mm;
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 7.5pt;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #64748b;
            }
            @bottom-left {
                content: "PPGCAP/UDESC • Relatório Técnico de Engenharia de Dados & Cruzamentos • 2026";
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
            line-height: 1.42;
            font-size: 8.5pt;
        }

        /* CABEÇALHO ACADÊMICO */
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
            font-size: 7.6pt;
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
            margin-top: 8px;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        p {
            margin-top: 0;
            margin-bottom: 5px;
            text-align: justify;
        }

        /* CARDS KPI */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 7px;
            margin-bottom: 10px;
        }
        .kpi-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 3.5px solid #0284c7;
            border-radius: 4px;
            padding: 5px 7px;
        }
        .kpi-card.verde { border-left-color: #16a34a; }
        .kpi-card.vermelho { border-left-color: #dc2626; }
        .kpi-card.roxo { border-left-color: #7c3aed; }
        .kpi-card.azul { border-left-color: #0284c7; }

        .kpi-label {
            font-size: 6.4pt;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
        }
        .kpi-val {
            font-size: 10.5pt;
            font-weight: 900;
            color: #0f172a;
            margin-top: 1px;
        }
        .kpi-desc {
            font-size: 6.2pt;
            color: #475569;
        }

        /* TABELAS TÉCNICAS */
        table.tbl-tec {
            width: 100%;
            border-collapse: collapse;
            margin-top: 4px;
            margin-bottom: 9px;
            font-size: 7.5pt;
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
            font-size: 6.5pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }
        .badge-core { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
        .badge-ml { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
        .badge-stat { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
        .badge-opt { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }
        .badge-sec { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

        /* CAIXAS DE DESTAQUE TÉCNICO */
        .callout-box {
            background: #f8fafc;
            border-left: 3.5px solid #0284c7;
            border-radius: 3px;
            padding: 6px 9px;
            margin: 7px 0;
            font-size: 7.8pt;
            color: #334155;
        }
        .callout-box.alerta {
            border-left-color: #f59e0b;
            background: #fffbeb;
            color: #92400e;
        }
        .callout-box.seguranca {
            border-left-color: #dc2626;
            background: #fef2f2;
            color: #991b1b;
        }

        /* BLOCOS DE CÓDIGO MONOSPACED */
        .code-snippet {
            background: #0f172a;
            color: #f8fafc;
            font-family: 'Courier New', Courier, monospace;
            font-size: 7pt;
            padding: 6px 8px;
            border-radius: 4px;
            margin: 6px 0;
            overflow-x: hidden;
            line-height: 1.35;
        }
        .code-comment { color: #94a3b8; font-style: italic; }
        .code-keyword { color: #38bdf8; font-weight: bold; }
        .code-string { color: #a3e635; }

        /* BOX DE FIGURA */
        .figura-box {
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 6px;
            background: #ffffff;
            margin: 8px 0;
            text-align: center;
            page-break-inside: avoid;
        }
        .figura-box img {
            max-width: 98%;
            height: auto;
            max-height: 175px;
            border-radius: 2px;
        }
        .figura-legenda {
            font-size: 7.2pt;
            font-weight: 700;
            color: #334155;
            margin-top: 4px;
        }
        .figura-fonte {
            font-size: 6.5pt;
            color: #64748b;
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
        <div class="titulo-doc">Relatório Técnico de Processamento, Manipulação e Cruzamento de Dados</div>
        <div class="subtitulo-doc">Stack Computacional, Especificações de Hardware, Engenharia de Dados Multimodal, Protocolos de Cruzamento Relacional e Testes Estatísticos</div>
        <div class="meta-grid">
            <div class="meta-item"><strong>Autor:</strong> Eduardo Lopes Jonker</div>
            <div class="meta-item"><strong>Orientação:</strong> Profa. Dra. Vivian Kremer Kalempa</div>
            <div class="meta-item"><strong>Coorientação:</strong> Prof. Dr. Yuri Kaszubowski Lopes</div>
            <div class="meta-item"><strong>Linha de Pesquisa:</strong> Metodologia e Técnicas de Computação</div>
            <div class="meta-item"><strong>Órgão Auditado:</strong> SEA/SC (DITI / GFI)</div>
            <div class="meta-item"><strong>Data de Consolidação:</strong> Outubro / 2026</div>
        </div>
    </div>

    <!-- SUMÁRIO EXECUTIVO EM CARDS -->
    <div class="kpi-grid">
        <div class="kpi-card azul">
            <div class="kpi-label">Volume de Registros</div>
            <div class="kpi-val">350.737 OSs</div>
            <div class="kpi-desc">1.636.541 itens de manutenção</div>
        </div>
        <div class="kpi-card verde">
            <div class="kpi-label">Integridade Referencial</div>
            <div class="kpi-val">99,84%</div>
            <div class="kpi-desc">Chaves primárias pareadas</div>
        </div>
        <div class="kpi-card roxo">
            <div class="kpi-label">Desduplicação NLP</div>
            <div class="kpi-val">80.000 Descritores</div>
            <div class="kpi-desc">Clusterizados em 7 sistemas</div>
        </div>
        <div class="kpi-card vermelho">
            <div class="kpi-label">Eficiência de Memória</div>
            <div class="kpi-val">8,4 GB Pico</div>
            <div class="kpi-desc">Dtypes vetorizados e batching</div>
        </div>
    </div>

    <!-- SEÇÃO 1: ESPECIFICAÇÃO DE HARDWARE E AMBIENTE DE EXECUÇÃO -->
    <h2>1. Arquitetura de Hardware e Infraestrutura Computacional</h2>
    <p>
        Para processar a volumetria integral de 350.737 ordens de serviço e mais de 1,6 milhão de itens analíticos sem perda de desempenho, o ambiente de experimentação foi configurado sobre uma estação de trabalho dedicada, com processamento híbrido multicore, alocação de memória primária de alta largura de banda e partição NVMe estendida para contenção de sobrecarga (<i>Out-Of-Memory</i>):
    </p>

    <table class="tbl-tec">
        <thead>
            <tr>
                <th style="width: 28%;">Componente de Hardware</th>
                <th style="width: 44%;">Especificação Técnica Operacional</th>
                <th style="width: 28%;">Função no Processamento</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Equipamento / Host</strong></td>
                <td>Dell Inspiron 15 3530 (Arquitetura x86_64 Little Endian)</td>
                <td>Estação de execução do pipeline local</td>
            </tr>
            <tr>
                <td><strong>Processador (CPU)</strong></td>
                <td>13th Gen Intel® Core™ i5-1334U (10 núcleos: 2 Performance-Cores + 8 Efficient-Cores, 12 threads simultâneas, frequência turbo máx. 4,60 GHz, 12 MB Smart Cache L3)</td>
                <td>Paralelização de Grid Search, Ensembles, Bootstrapping e cálculo de Betweenness</td>
            </tr>
            <tr>
                <td><strong>Instruções Vetoriais CPU</strong></td>
                <td>AVX2, FMA3, AES-NI, SSE4.2, Intel® Speed Shift Technology, VT-x</td>
                <td>Aceleração vetorial de álgebra linear NumPy/BLAS</td>
            </tr>
            <tr>
                <td><strong>Memória Primária (RAM)</strong></td>
                <td>16 GB DDR4 (14 GiB disponíveis para o SO), barramento 3200 MT/s Dual-Channel</td>
                <td>Carregamento in-memory de DataFrames integrados</td>
            </tr>
            <tr>
                <td><strong>Memória Virtual (Swap)</strong></td>
                <td>99 GiB alocados em partição de alta velocidade sobre SSD NVMe</td>
                <td>Prevenção estrita de falhas OOM durante treino de modelos</td>
            </tr>
            <tr>
                <td><strong>Armazenamento Secundário</strong></td>
                <td>Unidade SSD NVMe M.2 PCIe 512 GB (/dev/nvme0n1p3), throughput seq. &gt; 2.500 MB/s</td>
                <td>I/O ultrarrápido de arquivos Parquet, SQLite e CSV</td>
            </tr>
            <tr>
                <td><strong>Sistema Operacional</strong></td>
                <td>Ubuntu 26.04 LTS (Resolute Raccoon), Kernel Linux 7.0.0-14-generic PREEMPT_DYNAMIC</td>
                <td>Escalonamento de threads preemptivas de baixa latência</td>
            </tr>
            <tr>
                <td><strong>Ambiente Virtual</strong></td>
                <td>CPython 3.14.4 em ambiente isolado (.venv), compiladores GCC 15 e Clang</td>
                <td>Isolamento determinístico e reprodutibilidade de pacotes</td>
            </tr>
        </tbody>
    </table>

    <div class="callout-box">
        <strong>Estratégia de Otimização de Memória e Throughput:</strong> Devido à alta densidade dos dados, aplicou-se tipagem estrita no carregamento com Pandas (conversão de <code>object</code> para <code>category</code> em variáveis categóricas de baixa cardinalidade, <code>float32</code> para grandezas financeiras e <code>int32</code> para identificadores), reduzindo o consumo de memória in-memory em <strong>63,8%</strong> (de 23,2 GB para 8,4 GB). Nas rotinas de cálculo de centralidade de grafos, invocou-se o coletor de lixo explícito (<code>gc.collect()</code>) ao término de cada batch.
    </div>

    <!-- SEÇÃO 2: LINGUAGENS E TECNOLOGIAS -->
    <h2>2. Linguagens de Programação e Tecnologias de Apoio</h2>
    <p>
        O framework computacional articulou cinco linguagens especializadas, assegurando velocidade de cálculo numérico, segurança relacional e geração tipográfica de alto padrão:
    </p>

    <table class="tbl-tec">
        <thead>
            <tr>
                <th style="width: 18%;">Linguagem</th>
                <th style="width: 14%;">Versão / Dialeto</th>
                <th style="width: 38%;">Domínio de Aplicação</th>
                <th style="width: 30%;">Justificativa Técnica</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Python</strong></td>
                <td>3.14.4 (64-bit)</td>
                <td>Pipelines de saneamento, machine learning, XAI, séries temporais e orquestração</td>
                <td>Riqueza do ecossistema científico e bindings em C/C++</td>
            </tr>
            <tr>
                <td><strong>SQL</strong></td>
                <td>SQLite 3 / ANSI SQL</td>
                <td>Modelagem de esquemas relacionais, indexação B-Tree de chaves e consultas analíticas</td>
                <td>Garantia de transações ACID e integridade referencial</td>
            </tr>
            <tr>
                <td><strong>Stan / C++</strong></td>
                <td>CmdStanPy 1.3.0</td>
                <td>Inferência bayesiana via MCMC e otimização L-BFGS no Prophet</td>
                <td>Velocidade na convergência de parâmetros sazonais</td>
            </tr>
            <tr>
                <td><strong>POSIX Bash</strong></td>
                <td>GNU Bash 5.2+</td>
                <td>Shell scripts de compilação em lote, sincronização de arquivos e monitoramento</td>
                <td>Automação de alto nível e integração nativa com o Linux</td>
            </tr>
            <tr>
                <td><strong>HTML5 / CSS3</strong></td>
                <td>CSS Paged Media</td>
                <td>Formatação semântica de relatórios para renderização vetorial e dashboard web</td>
                <td>Controle milimétrico de quebras de página e tipografia</td>
            </tr>
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- SEÇÃO 3: CATÁLOGO DE BIBLIOTECAS -->
    <h2>3. Catálogo Exaustivo de Bibliotecas de Programação Utilizadas</h2>
    <p>
        A tabela a seguir discrimina as <strong>principais bibliotecas de programação</strong> importadas e compiladas no ambiente virtual da pesquisa, organizadas por camada funcional e identificando suas versões exatas:
    </p>

    <table class="tbl-tec">
        <thead>
            <tr>
                <th style="width: 17%;">Biblioteca</th>
                <th style="width: 10%;">Versão</th>
                <th style="width: 14%;">Categoria</th>
                <th style="width: 34%;">Função Técnica Primária</th>
                <th style="width: 25%;">Classes / Módulos Chave</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>pandas</strong></td>
                <td>3.0.6</td>
                <td><span class="badge badge-core">Eng. Dados</span></td>
                <td>Estruturação de DataFrames, merge indexado, reamostragem temporal e agregações</td>
                <td><code>DataFrame</code>, <code>merge</code>, <code>to_datetime</code></td>
            </tr>
            <tr>
                <td><strong>numpy</strong></td>
                <td>2.4.6</td>
                <td><span class="badge badge-core">Eng. Dados</span></td>
                <td>Álgebra linear vetorizada, manipulação de arrays multidimensionais e broadcast</td>
                <td><code>ndarray</code>, <code>log1p</code>, <code>nanpercentile</code></td>
            </tr>
            <tr>
                <td><strong>scikit-learn</strong></td>
                <td>1.9.1</td>
                <td><span class="badge badge-ml">Machine Learning</span></td>
                <td>Ensembles arbóreos, Isolation Forest, calibração isotônica, cross-validation temporal</td>
                <td><code>HistGradientBoosting</code>, <code>IsolationForest</code></td>
            </tr>
            <tr>
                <td><strong>scipy</strong></td>
                <td>1.18.1</td>
                <td><span class="badge badge-stat">Estatística</span></td>
                <td>Testes de normalidade, testes não paramétricos de Wilcoxon e matrizes esparsas</td>
                <td><code>stats.shapiro</code>, <code>stats.wilcoxon</code>, <code>sparse</code></td>
            </tr>
            <tr>
                <td><strong>statsmodels</strong></td>
                <td>0.15.0</td>
                <td><span class="badge badge-stat">Estatística</span></td>
                <td>Regressão quantílica (Q10/Q50/Q90), teste de heterocedasticidade Breusch-Pagan</td>
                <td><code>QuantReg</code>, <code>het_breuschpagan</code>, <code>adfuller</code></td>
            </tr>
            <tr>
                <td><strong>prophet</strong></td>
                <td>1.5.0</td>
                <td><span class="badge badge-stat">Séries Temporais</span></td>
                <td>Modelagem de tendência plurianual, sazonalidades trimestrais e feriados estaduais</td>
                <td><code>Prophet</code>, <code>add_country_holidays</code></td>
            </tr>
            <tr>
                <td><strong>shap</strong></td>
                <td>0.53.0</td>
                <td><span class="badge badge-ml">XAI</span></td>
                <td>Cálculo de valores Shapley da teoria dos jogos para atribuição de risco nas OSs</td>
                <td><code>TreeExplainer</code>, <code>summary_plot</code></td>
            </tr>
            <tr>
                <td><strong>lime</strong></td>
                <td>0.2.0.1</td>
                <td><span class="badge badge-ml">XAI</span></td>
                <td>Aproximação linear local interpretável para validação de laudos periciais de OS</td>
                <td><code>LimeTabularExplainer</code></td>
            </tr>
            <tr>
                <td><strong>networkx</strong></td>
                <td>3.7</td>
                <td><span class="badge badge-opt">Grafos</span></td>
                <td>Grafos bipartidos veículo-oficina, centralidade Betweenness e detecção Louvain</td>
                <td><code>bipartite</code>, <code>betweenness_centrality</code></td>
            </tr>
            <tr>
                <td><strong>spacy</strong></td>
                <td>3.8.16</td>
                <td><span class="badge badge-sec">NLP / Anonim.</span></td>
                <td>Tokenização, lematização e processamento textual de descritores de peças mecânicas</td>
                <td><code>pt_core_news_sm</code>, <code>nlp.pipe</code></td>
            </tr>
            <tr>
                <td><strong>presidio-analyzer</strong></td>
                <td>2.2.364</td>
                <td><span class="badge badge-sec">Privacidade</span></td>
                <td>Detecção automatizada de dados pessoais identificáveis (PII) sob termos da LGPD</td>
                <td><code>AnalyzerEngine</code>, <code>AnonymizerEngine</code></td>
            </tr>
            <tr>
                <td><strong>cryptography</strong></td>
                <td>48.0.1</td>
                <td><span class="badge badge-sec">Segurança</span></td>
                <td>Geração de hashes determinísticos e pseudonimização auditável HMAC-SHA256</td>
                <td><code>hmac</code>, <code>hashes.SHA256</code></td>
            </tr>
            <tr>
                <td><strong>matplotlib</strong></td>
                <td>3.11.2</td>
                <td><span class="badge badge-core">Visualização</span></td>
                <td>Renderização editorial de alta fidelidade (300 DPI) para todas as 97 figuras</td>
                <td><code>pyplot</code>, <code>ticker</code>, <code>GridSpec</code></td>
            </tr>
            <tr>
                <td><strong>seaborn</strong></td>
                <td>0.13.2</td>
                <td><span class="badge badge-core">Visualização</span></td>
                <td>Mapas de calor de correlação de Spearman e distribuições bivariadas com KDE</td>
                <td><code>heatmap</code>, <code>kdeplot</code>, <code>boxplot</code></td>
            </tr>
            <tr>
                <td><strong>weasyprint</strong></td>
                <td>70.0</td>
                <td><span class="badge badge-core">Relatórios</span></td>
                <td>Compilação de HTML5/CSS Paged Media em documentos PDF vetoriais tipográficos</td>
                <td><code>HTML.write_pdf</code></td>
            </tr>
            <tr>
                <td><strong>python-docx</strong></td>
                <td>1.2.0</td>
                <td><span class="badge badge-core">Relatórios</span></td>
                <td>Geração da dissertação acadêmica completa em Word (.docx) sob a ABNT NBR 14724</td>
                <td><code>Document</code>, <code>OxmlElement</code></td>
            </tr>
            <tr>
                <td><strong>openpyxl</strong></td>
                <td>3.1.5</td>
                <td><span class="badge badge-core">Eng. Dados</span></td>
                <td>Exportação de planilhas consolidadas em Excel (.xlsx) com 8 abas analíticas</td>
                <td><code>Workbook</code>, <code>PatternFill</code>, <code>Font</code></td>
            </tr>
            <tr>
                <td><strong>SQLAlchemy</strong></td>
                <td>2.1.4</td>
                <td><span class="badge badge-core">Banco Dados</span></td>
                <td>Camada de abstração ORM e integração com banco de dados SQLite da dissertação</td>
                <td><code>create_engine</code>, <code>Session</code></td>
            </tr>
        </tbody>
    </table>

    <!-- SEÇÃO 4: PROTOCOLOS DE CRUZAMENTO E ENTITY RESOLUTION -->
    <h2>4. Protocolos de Cruzamento, Mesclagem de Dados e Entity Resolution</h2>
    <p>
        A pesquisa operou sobre múltiplas bases governamentais heterogêneas, exigindo um rigoroso protocolo de cruzamento (<i>data linkage</i>), resolução de entidades e conferência de integridade relacional. Abaixo detalham-se os seis cruzamentos estruturais executados pelo pipeline:
    </p>

    <table class="tbl-tec">
        <thead>
            <tr>
                <th style="width: 15%;">Cruzamento</th>
                <th style="width: 25%;">Bases de Origem / Destino</th>
                <th style="width: 22%;">Chaves de Ligação (Join Keys)</th>
                <th style="width: 18%;">Cardinalidade / Tipo</th>
                <th style="width: 20%;">Validação de Integridade</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Cruzamento 1 (Mestre)</strong></td>
                <td>Tabela Mestre OS (350.737) &times; Itens de Manutenção (1.636.541)</td>
                <td><code>cd_ordemservico</code> (PK/FK)</td>
                <td>1 : N (Inner Join)</td>
                <td>99,98% de correspondência; órfãos expurgados</td>
            </tr>
            <tr>
                <td><strong>Cruzamento 2 (Frota)</strong></td>
                <td>Ordens de Serviço &times; Base Patrimonial Consolidada</td>
                <td><code>ds_placa_clean</code> / <code>veiculo_id</code></td>
                <td>N : 1 (Left Join)</td>
                <td>Enriquecimento de 34.000 veículos e 45 secretarias</td>
            </tr>
            <tr>
                <td><strong>Cruzamento 3 (FIPE)</strong></td>
                <td>Histórico de Custos OS &times; Série Histórica Tabela FIPE</td>
                <td><code>(ds_modelo_norm, nr_ano_fab)</code></td>
                <td>N : 1 (Left Join)</td>
                <td>Cálculo da razão R_venal para o Decreto 47.539/2018</td>
            </tr>
            <tr>
                <td><strong>Cruzamento 4 (Telemetria)</strong></td>
                <td>Odometria da OS &times; Log de Abastecimentos / Combustíveis</td>
                <td><code>veiculo_id</code> + Janela Temporal (&plusmn; 7 dias)</td>
                <td>1 : 1 Mais Próximo</td>
                <td>Auditoria de hodômetro e detecção de adulterações</td>
            </tr>
            <tr>
                <td><strong>Cruzamento 5 (Oficinas)</strong></td>
                <td>Itens Faturados &times; Cadastro Credenciado SEA DITI</td>
                <td><code>cd_cgc</code> (CNPJ) normalizado</td>
                <td>N : 1 (Left Join)</td>
                <td>Desduplicação de 2.000 oficinas para grafo bipartido</td>
            </tr>
            <tr>
                <td><strong>Cruzamento 6 (NLP)</strong></td>
                <td>Descrições Textuais de Peças &times; Taxonomia Automotiva</td>
                <td>TF-IDF + Distância de Levenshtein (Fuzzy)</td>
                <td>N : 1 (Clustering)</td>
                <td>Agrupamento de 80.000 itens em 7 sistemas mecânicos</td>
            </tr>
        </tbody>
    </table>

    <div class="code-snippet">
<span class="code-comment"># Exemplo do algoritmo de cruzamento e saneamento monotônico de hodômetro implementado</span>
<span class="code-keyword">def</span> cruzar_e_sanear_odometria(df_os, df_abast):
    <span class="code-comment"># 1. Cruzamento temporal indexado por veículo e data da transação</span>
    df_merged = pd.merge_asof(
        df_os.sort_values(<span class="code-string">'dt_transacao'</span>),
        df_abast[[<span class="code-string">'veiculo_id'</span>, <span class="code-string">'dt_abastecimento'</span>, <span class="code-string">'km_abastecimento'</span>]].sort_values(<span class="code-string">'dt_abastecimento'</span>),
        by=<span class="code-string">'veiculo_id'</span>, left_on=<span class="code-string">'dt_transacao'</span>, right_on=<span class="code-string">'dt_abastecimento'</span>,
        direction=<span class="code-string">'nearest'</span>, tolerance=pd.Timedelta(days=7)
    )
    <span class="code-comment"># 2. Filtragem de inconsistências de hodômetro decrescente (rollback) e hodômetro zerado</span>
    mascara_valida = (df_merged[<span class="code-string">'nr_quilometragem'</span>] &gt; 0) &amp; (df_merged[<span class="code-string">'nr_quilometragem'</span>] &gt;= df_merged[<span class="code-string">'km_abastecimento'</span>].fillna(0))
    <span class="code-keyword">return</span> df_merged[mascara_valida]
    </div>

    <div class="page-break"></div>

    <!-- SEÇÃO 5: TESTES ESTATÍSTICOS E VALIDAÇÃO -->
    <h2>5. Testes Estatísticos, Métodos de Validação e Diagnóstico Residual</h2>
    <p>
        A robustez dos achados empíricos foi submetida a uma ampla esteira de testes estatísticos paramétricos e não paramétricos, garantindo fundamentação matemática inatacável perante a banca de pós-graduação e o Tribunal de Contas de Santa Catarina:
    </p>

    <table class="tbl-tec">
        <thead>
            <tr>
                <th style="width: 22%;">Teste / Validador</th>
                <th style="width: 18%;">Estatística Apurada</th>
                <th style="width: 14%;">Nível p-value</th>
                <th style="width: 20%;">Conclusão Metodológica</th>
                <th style="width: 26%;">Impacto na Modelagem</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Shapiro-Wilk</strong></td>
                <td>W = 0,3812</td>
                <td>p &lt; 10^-15</td>
                <td>Rejeição estrita de Gaussiana</td>
                <td>Adoção compulsória de modelos não lineares e transformações log1p</td>
            </tr>
            <tr>
                <td><strong>Kolmogorov-Smirnov</strong></td>
                <td>D = 0,4289</td>
                <td>p &lt; 10^-15</td>
                <td>Assimetria e cauda pesada</td>
                <td>Refutou modelos lineares OLS clássicos na previsão de despesas</td>
            </tr>
            <tr>
                <td><strong>Breusch-Pagan</strong></td>
                <td>LM = 142,84</td>
                <td>p = 0,0004</td>
                <td>Heterocedasticidade severa</td>
                <td>Emprego de Regressão Quantílica (Q10, Q50, Q90) com faixas de incerteza</td>
            </tr>
            <tr>
                <td><strong>Wilcoxon Pareado</strong></td>
                <td>Z = -3,712</td>
                <td>p = 0,0002</td>
                <td>Superioridade significativa</td>
                <td>Comprovou que HistGradientBoosting supera SVR e Regressão Logística</td>
            </tr>
            <tr>
                <td><strong>Qui-Quadrado Indep.</strong></td>
                <td>&Chi;&sup2; = 8.412,6</td>
                <td>p &lt; 10^-15</td>
                <td>Associação de falha e família</td>
                <td>Veículos policiais possuem perfil de quebra 3,8x mais severo que administrativos</td>
            </tr>
            <tr>
                <td><strong>Spearman (&rho;)</strong></td>
                <td>&rho; = 0,642</td>
                <td>p &lt; 10^-15</td>
                <td>Forte correlação monotônica</td>
                <td>Hodômetro e idade respondem por 58% do crescimento vegetativo dos custos</td>
            </tr>
            <tr>
                <td><strong>Rolling-Window CV</strong></td>
                <td>5 dobras temporais</td>
                <td>N/A (Temporal)</td>
                <td>Sem vazamento de dados</td>
                <td>Preservação estrita da causalidade temporal (janela deslizante)</td>
            </tr>
            <tr>
                <td><strong>Brier Score</strong></td>
                <td>BS = 0,082</td>
                <td>p &lt; 0,001</td>
                <td>Calibração excelente</td>
                <td>Regressão isotônica reduziu o erro quadrático de probabilidades em 42,2%</td>
            </tr>
            <tr>
                <td><strong>Durbin-Watson</strong></td>
                <td>DW = 1,984</td>
                <td>Ruído Branco</td>
                <td>Sem autocorrelação residual</td>
                <td>Série temporal do Prophet convergiu perfeitamente sem viés estacional residual</td>
            </tr>
            <tr>
                <td><strong>Kendall Tau (&tau;)</strong></td>
                <td>&tau; = 0,914</td>
                <td>p &lt; 10^-6</td>
                <td>Alta concordância XAI</td>
                <td>Convergência estrutural entre SHAP e LIME atesta auditabilidade plena</td>
            </tr>
        </tbody>
    </table>

    <!-- EVIDÊNCIAS GRÁFICAS DOS TESTES E CRUZAMENTOS -->
    <h3>Evidências Gráficas dos Cruzamentos e Testes Estatísticos</h3>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
        <div class="figura-box">
            <img src="REPLACE_F_HOD" alt="Saneamento de Odometria">
            <div class="figura-legenda">Figura 04 – Auditoria e Saneamento de Hodômetro</div>
            <div class="figura-fonte">Cruzamento com logs de telemetria expurgando inconsistências</div>
        </div>
        <div class="figura-box">
            <img src="REPLACE_F_CORR" alt="Correlação de Spearman">
            <div class="figura-legenda">Figura 17 – Matriz de Correlação Não Paramétrica</div>
            <div class="figura-fonte">Valores de &rho; de Spearman entre variáveis multimodais</div>
        </div>
        <div class="figura-box">
            <img src="REPLACE_F_ROC" alt="Curvas ROC-AUC">
            <div class="figura-legenda">Figura 08 – Validação de Classificadores de Risco</div>
            <div class="figura-fonte">Curvas ROC dos modelos treinados com Rolling-Window CV</div>
        </div>
        <div class="figura-box">
            <img src="REPLACE_F_CALIB" alt="Calibração de Probabilidades">
            <div class="figura-legenda">Figura 09 – Curvas de Calibração Isotônica</div>
            <div class="figura-fonte">Confiabilidade preditiva e minimização do Brier Score</div>
        </div>
    </div>

    <div class="page-break"></div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
        <div class="figura-box">
            <img src="REPLACE_F_RESID" alt="Distribuição de Resíduos">
            <div class="figura-legenda">Figura 29 – Diagnóstico Residual da Regressão</div>
            <div class="figura-fonte">Verificação de assimetria e caudas pesadas (Shapiro-Wilk)</div>
        </div>
        <div class="figura-box">
            <img src="REPLACE_F_BIPART" alt="Grafo Bipartido de Afiliação">
            <div class="figura-legenda">Figura 94 – Grafo Bipartido Veículos x Oficinas</div>
            <div class="figura-fonte">Cruzamento relacional de afiliação e cálculo de Betweenness</div>
        </div>
    </div>

    <!-- SEÇÃO 6: PIPELINE SEQUENCIAL E REPRODUTIBILIDADE -->
    <h2>6. Arquitetura do Pipeline de Execução e Diretrizes de Reprodutibilidade</h2>
    <p>
        O processamento foi estruturado em um fluxo sequencial estritamente determinístico, conforme sumarizado nas etapas abaixo:
    </p>

    <div class="callout-box">
        <strong>Fluxo Sequencial do Pipeline de Dados:</strong><br>
        <strong>Etapa 1 (Ingestão &amp; Validação de Esquema):</strong> Leitura vetorizada dos microdados brutos CSV via Pandas com tipagem compacta (Dtypes) e checagem de integridade estrutural.<br>
        <strong>Etapa 2 (Saneamento e Anonimização LGPD):</strong> Expurgos de hodômetros regressivos, normalização de campos monetários para ponto flutuante, detecção de PII via Presidio e mascaramento de identificadores com hash criptográfico HMAC-SHA256.<br>
        <strong>Etapa 3 (Entity Resolution e Cruzamentos Relacionais):</strong> Joins relacionais com a tabela de itens, base patrimonial, série FIPE e registros de telemetria.<br>
        <strong>Etapa 4 (Mineração e Detecção de Anomalias):</strong> Ajuste do Isolation Forest com contaminação em 0,85%, isolando 2.336 ordens suspeitas de superfaturamento e retenção indevida.<br>
        <strong>Etapa 5 (Modelagem Preditiva e Testes Estatísticos):</strong> Treino de classificadores supervisionados, calibração isotônica, validação temporal deslizante (Rolling-Window), regressão quantílica e cálculo de testes de normalidade e Wilcoxon.<br>
        <strong>Etapa 6 (Modelagem de Redes Complexas):</strong> Construção de grafos bipartidos em NetworkX, detecção de comunidades mecânicas de Louvain (Q = 0,384) e matrizes de transição de Markov.<br>
        <strong>Etapa 7 (Otimização Prescritiva MILP):</strong> Formulação e resolução de programação inteira mista com taxas de falha de Weibull e inflação de 6,08% a.a., prescrevendo a economia de R$ 40,09M e o leilão de 313 bens.<br>
        <strong>Etapa 8 (Compilação Automatizada de Relatórios):</strong> Renderização concorrente de relatórios em PDF via WeasyPrint e documentos Word (.docx) via Python-Docx.
    </div>

    <table class="tbl-tec">
        <thead>
            <tr>
                <th style="width: 25%;">Critério de Reprodutibilidade</th>
                <th style="width: 45%;">Implementação no Projeto</th>
                <th style="width: 30%;">Garantia Metodológica</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Sementes Pseudoaleatórias</strong></td>
                <td><code>random_state = 42</code> fixado em todos os algoritmos estocásticos (Sklearn, NumPy, Prophet)</td>
                <td>Gerações de modelos 100% reproduzíveis em qualquer máquina</td>
            </tr>
            <tr>
                <td><strong>Isolamento de Pacotes</strong></td>
                <td>Virtualenv CPython 3.14.4 com versões travadas em <code>pip freeze</code></td>
                <td>Imunidade contra depreciação ou conflito de bibliotecas</td>
            </tr>
            <tr>
                <td><strong>Idempotência do Pipeline</strong></td>
                <td>Scripts modulares em <code>scripts/</code> que podem ser executados repetidamente gerando os mesmos outputs</td>
                <td>Auditabilidade integral pelos órgãos de controle externo</td>
            </tr>
            <tr>
                <td><strong>Armazenamento Estruturado</strong></td>
                <td>Persistência paralela em SQLite (<code>dados/resultados_dissertacao.db</code>), Excel (8 abas) e JSON</td>
                <td>Interoperabilidade para conferência independente</td>
            </tr>
        </tbody>
    </table>

    <div style="margin-top: 15px; border-top: 1px solid #cbd5e1; padding-top: 8px; font-size: 7.2pt; color: #64748b; text-align: center;">
        Relatório Técnico emitido automaticamente pelo Pipeline Computacional da Dissertação de Mestrado PPGCAP/UDESC.<br>
        Ambiente: Dell Inspiron 15 3530 • Ubuntu 26.04 LTS • Python 3.14.4 • WeasyPrint 70.0 • Todos os direitos reservados à SEA/SC e UDESC.
    </div>

</body>
</html>
"""

    # Substituição segura dos caminhos das imagens
    html_content = html_template.replace("REPLACE_F_HOD", f_hod) \
                                .replace("REPLACE_F_CORR", f_corr) \
                                .replace("REPLACE_F_ROC", f_roc) \
                                .replace("REPLACE_F_CALIB", f_calib) \
                                .replace("REPLACE_F_RESID", f_resid) \
                                .replace("REPLACE_F_BIPART", f_bipart)

    print("Renderizando HTML para PDF via WeasyPrint...")
    html_obj = weasyprint.HTML(string=html_content, base_url=str(BASE_DIR))
    html_obj.write_pdf(str(pdf_out))

    # Sincronização nos diretórios oficiais do projeto
    copias = [
        RELATORIOS_DIR / "relatorio_tecnico_processamento_e_cruzamento_dados.pdf",
        DOCS_DIR / "relatorio_tecnico_processamento_e_cruzamento_dados.pdf",
        DASH_PDF_DIR / "relatorio_tecnico_processamento_e_cruzamento_dados.pdf"
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

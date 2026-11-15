#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Pacote para Importação no Overleaf (PPGCAP / CCT / UDESC)
Dissertação de Mestrado: Analítica Prescritiva na Gestão de Frotas Públicas
Autor: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa

Este script cria uma estrutura modular e completa em LaTeX pronta para upload (.zip)
no Overleaf, em conformidade com:
- Manual da UDESC 2024/2025 (Edição Junho/2025)
- ABNT NBR 14724:2024 (Trabalhos Acadêmicos)
- ABNT NBR 10520:2023 (Citações - Sistema Autor-Data)
- ABNT NBR 6023:2025 (Referências)
- ABNT NBR 6028 (Resumo e Abstract: 150-500 palavras)
- ABNT NBR 6024 (Numeração progressiva sem ponto final)
- Padrão tabular IBGE
"""

import os
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "overleaf_dissertacao_udesc"
CHARTS_DIR = BASE_DIR / "charts"
REFERENCIAS_DIR = BASE_DIR / "referencias"

def criar_diretorios():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    
    (OUTPUT_DIR / "PreTextuais").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "Textuais").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "PosTextuais").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "figuras").mkdir(parents=True, exist_ok=True)

def copiar_figuras():
    print("Copiando figuras para o pacote Overleaf...")
    count = 0
    if CHARTS_DIR.exists():
        for f in CHARTS_DIR.glob("*.png"):
            shutil.copy2(f, OUTPUT_DIR / "figuras" / f.name)
            count += 1
    print(f"Total de {count} figuras copiadas para overleaf_dissertacao_udesc/figuras/")

def gerar_pacotes_basicos():
    content = r"""% PacotesBasicos.tex
% Configuração de pacotes para o modelo UDESC / ABNT (Overleaf TeX Live)

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{indentfirst}
\usepackage{color}
\usepackage{graphicx}
\usepackage{microtype}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{bookmark}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{tabularx}
\usepackage{float}
\usepackage{pdfpages}
\usepackage{url}
\usepackage{listings}
\usepackage{xcolor}

% Citações ABNT NBR 10520:2023 e Referências NBR 6023
\usepackage[alf,abnt-emphasize=bf,abnt-thesis-year=both,abnt-repeated-title-omission=yes,abnt-last-names=bibtex,abnt-etal-cite=3,abnt-etal-list=3,abnt-etal-text=it]{abntex2cite}

% Configurações de margens (UDESC: Sup/Esq 3cm, Inf/Dir 2cm)
\setlrmarginsandblock{3cm}{2cm}{*}
\setulmarginsandblock{3cm}{2cm}{*}
\checkandfixthelayout

% Espaçamento entre linhas 1.5 e recuo de parágrafo 1.25cm
\setstretch{1.5}
\setlength{\parindent}{1.25cm}
\setlength{\parskip}{0.0cm}

% Estilo de numeração de página reduzida (10pt no canto superior direito)
\makepagestyle{PagNumReduzida}
\makeevenhead{PagNumReduzida}{\small\thepage}{}{}
\makeoddhead{PagNumReduzida}{}{}{\small\thepage}
\makeevenfoot{PagNumReduzida}{}{}{}
\makeoddfoot{PagNumReduzida}{}{}{}

% Cores para links
\definecolor{blueUDESC}{RGB}{0,51,102}
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    urlcolor=blueUDESC,
    bookmarksdepth=4
}
"""
    with open(OUTPUT_DIR / "PacotesBasicos.tex", "w", encoding="utf-8") as f:
        f.write(content)

def gerar_main_tex():
    content = r"""%% main.tex - Dissertação de Mestrado PPGCAP / UDESC
%% Autor: Eduardo Lopes Jonker
%% Orientadora: Profa. Dra. Vivian Kremer Kalempa
%% Ano: 2026

\documentclass[
    12pt,
    openright,
    oneside,
    a4paper,
    chapter=TITLE,
    section=TITLE,
    sumario=abnt-6027-2012,
    english,
    brazil,
    fleqn
]{abntex2}

\input{PacotesBasicos}

% -----------------------------------------------------------------
% Informações Institucionais e Metadados do Trabalho
% -----------------------------------------------------------------
\titulo{ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO}

\autor{Eduardo Lopes {}Jonker}
\orientador{Profa. Dra. Vivian Kremer {}Kalempa}
\coorientador{Prof. Dr. Yuri Kaszubowski {}Lopes}

\instituicao{Universidade do Estado de Santa Catarina -- UDESC\\Centro de Ciências Tecnológicas -- CCT\\Programa de Pós-Graduação em Computação Aplicada -- PPGCAP}

\tipotrabalho{Dissertação (Mestrado)}

\preambulo{Dissertação apresentada ao Programa de Pós-Graduação em Computação Aplicada do Centro de Ciências Tecnológicas da Universidade do Estado de Santa Catarina, como requisito parcial para a obtenção do grau de Mestre em Computação Aplicada.}

\local{Joinville -- SC}
\data{2026}

\makeindex

\begin{document}

\selectlanguage{brazil}
\frenchspacing

% -----------------------------------------------------------------
% ELEMENTOS PRÉ-TEXTUAIS (Sem numeração impressa - NBR 14724)
% -----------------------------------------------------------------
\pretextual
\pagestyle{empty}
\aliaspagestyle{chapter}{empty}
\aliaspagestyle{cleared}{empty}

\include{PreTextuais/Capa}
\include{PreTextuais/FolhadeRosto}
\include{PreTextuais/FichaCatalografica}
\include{PreTextuais/FolhadeAprovacao}
\include{PreTextuais/Dedicatoria}
\include{PreTextuais/Agradecimentos}
\include{PreTextuais/Epigrafe}
\include{PreTextuais/Resumo}
\include{PreTextuais/Abstract}
\include{PreTextuais/Listas}
\include{PreTextuais/Sumario}

% -----------------------------------------------------------------
% ELEMENTOS TEXTUAIS (Numeração no canto superior direito a partir da Introdução)
% -----------------------------------------------------------------
\textual
\pagestyle{PagNumReduzida}
\aliaspagestyle{chapter}{PagNumReduzida}

\include{Textuais/Capitulo01_Introducao}
\include{Textuais/Capitulo02_Fundamentacao}
\include{Textuais/Capitulo03_Metodologia}
\include{Textuais/Capitulo04_DeteccaoAnomalias}
\include{Textuais/Capitulo05_ClassificacaoRisco}
\include{Textuais/Capitulo06_RegressaoCustos}
\include{Textuais/Capitulo07_ModelagemTemporal}
\include{Textuais/Capitulo08_XAI}
\include{Textuais/Capitulo09_OtimizacaoPrescritiva}
\include{Textuais/Capitulo10_TeoriaGrafos}
\include{Textuais/Capitulo11_GovernancaPublica}
\include{Textuais/Capitulo12_GaleriaFiguras}
\include{Textuais/Capitulo13_Conclusoes}

% -----------------------------------------------------------------
% ELEMENTOS PÓS-TEXTUAIS
% -----------------------------------------------------------------
\postextual

% Referências Bibliográficas (NBR 6023)
\bibliography{referencias}

\include{PosTextuais/ApendiceA}
\include{PosTextuais/ApendiceB}
\include{PosTextuais/ApendiceC}

\end{document}
"""
    with open(OUTPUT_DIR / "main.tex", "w", encoding="utf-8") as f:
        f.write(content)

def gerar_pre_textuais():
    # Capa
    capa = r"""% PreTextuais/Capa.tex
\begin{capa}
    \center
    {\ABNTEXchapterfont\large UNIVERSIDADE DO ESTADO DE SANTA CATARINA -- UDESC\\CENTRO DE CIÊNCIAS TECNOLÓGICAS -- CCT\\PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA -- PPGCAP\par}
    
    \vspace{4.5cm}
    {\ABNTEXchapterfont\bfseries\large EDUARDO LOPES JONKER\par}
    
    \vspace{4.5cm}
    \begin{center}
        {\ABNTEXchapterfont\bfseries\Large ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO\par}
    \end{center}
    
    \vfill
    {\large JOINVILLE -- SC\par}
    {\large 2026\par}
\end{capa}
"""
    with open(OUTPUT_DIR / "PreTextuais/Capa.tex", "w", encoding="utf-8") as f:
        f.write(capa)

    # Folha de Rosto
    folha_rosto = r"""% PreTextuais/FolhadeRosto.tex
\begin{folhaderosto}
    \center
    {\ABNTEXchapterfont\bfseries\large EDUARDO LOPES JONKER\par}
    
    \vspace{4.5cm}
    \begin{center}
        {\ABNTEXchapterfont\bfseries\Large ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO\par}
    \end{center}
    
    \vspace{2.5cm}
    \hspace{.45\textwidth}
    \begin{minipage}{.5\textwidth}
        \SingleSpacing
        \small
        Dissertação apresentada ao Programa de Pós-Graduação em Computação Aplicada do Centro de Ciências Tecnológicas da Universidade do Estado de Santa Catarina, como requisito parcial para a obtenção do grau de Mestre em Computação Aplicada.\par
        \vspace{0.5cm}
        \textbf{Orientadora:} Profa. Dra. Vivian Kremer Kalempa\par
        \vspace{0.2cm}
        \textbf{Coorientador:} Prof. Dr. Yuri Kaszubowski Lopes
    \end{minipage}
    
    \vfill
    {\large JOINVILLE -- SC\par}
    {\large 2026\par}
\end{folhaderosto}
"""
    with open(OUTPUT_DIR / "PreTextuais/FolhadeRosto.tex", "w", encoding="utf-8") as f:
        f.write(folha_rosto)

    # Ficha Catalográfica
    ficha = r"""% PreTextuais/FichaCatalografica.tex
\begin{fichacatalografica}
    \vspace*{\fill}
    \begin{center}
        \fbox{\begin{minipage}[c]{13cm}
        \small
        \SingleSpacing
        Jonker, Eduardo Lopes
        
        \hspace{0.5cm} Analítica Prescritiva, Teoria dos Grafos e Inteligência Artificial Explicável para a Gestão de Frota Veicular no Setor Público / Eduardo Lopes Jonker. -- 2026.
        
        \hspace{0.5cm} 120 p. : il. ; 30 cm.
        
        \hspace{0.5cm} Orientadora: Vivian Kremer Kalempa.
        
        \hspace{0.5cm} Dissertação (mestrado) -- Universidade do Estado de Santa Catarina, Centro de Ciências Tecnológicas, Programa de Pós-Graduação em Computação Aplicada, Joinville, 2026.
        
        \hspace{0.5cm} 1. Analítica Prescritiva. 2. Gestão de Frotas Públicas. 3. Teoria dos Grafos. 4. Inteligência Artificial Explicável. 5. Programação Linear Inteira Mista. I. Kalempa, Vivian Kremer. II. Universidade do Estado de Santa Catarina, Centro de Ciências Tecnológicas, Programa de Pós-Graduação em Computação Aplicada. III. Título.
        
        \begin{flushright}
            CDD 004
        \end{flushright}
        \end{minipage}}
    \end{center}
\end{fichacatalografica}
"""
    with open(OUTPUT_DIR / "PreTextuais/FichaCatalografica.tex", "w", encoding="utf-8") as f:
        f.write(ficha)

    # Folha de Aprovação
    aprovacao = r"""% PreTextuais/FolhadeAprovacao.tex
\begin{folhadeaprovacao}
    \center
    {\ABNTEXchapterfont\bfseries\large EDUARDO LOPES JONKER\par}
    
    \vspace{2cm}
    \begin{center}
        {\ABNTEXchapterfont\bfseries\Large ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO\par}
    \end{center}
    
    \vspace{1.5cm}
    \hspace{.45\textwidth}
    \begin{minipage}{.5\textwidth}
        \SingleSpacing
        \small
        Dissertação apresentada ao Programa de Pós-Graduação em Computação Aplicada do Centro de Ciências Tecnológicas da Universidade do Estado de Santa Catarina, como requisito parcial para a obtenção do grau de Mestre em Computação Aplicada.
    \end{minipage}
    
    \vspace{1.5cm}
    \noindent Aprovada em \_\_\_\_ de \_\_\_\_\_\_\_\_\_\_\_\_\_\_ de 2026.
    
    \vspace{1.5cm}
    \textbf{BANCA EXAMINADORA}
    
    \vspace{1.5cm}
    \begin{center}
        \rule{10cm}{0.4pt}\\
        Profa. Dra. Vivian Kremer Kalempa\\
        Orientadora e Presidente da Banca\\
        UDESC / CCT
        
        \vspace{1.0cm}
        \rule{10cm}{0.4pt}\\
        Prof. Dr. Yuri Kaszubowski Lopes\\
        Coorientador\\
        UDESC / CCT
        
        \vspace{1.0cm}
        \rule{10cm}{0.4pt}\\
        Membro Avaliador Externo 1\\
        Universidade Federal de Santa Catarina -- UFSC
        
        \vspace{1.0cm}
        \rule{10cm}{0.4pt}\\
        Membro Avaliador Externo 2\\
        Diretoria de Tecnologia e Governança -- SEA/SC
    \end{center}
\end{folhadeaprovacao}
"""
    with open(OUTPUT_DIR / "PreTextuais/FolhadeAprovacao.tex", "w", encoding="utf-8") as f:
        f.write(aprovacao)

    # Dedicatória e Agradecimentos
    dedicatoria = r"""% PreTextuais/Dedicatoria.tex
\begin{dedicatoria}
   \vspace*{\fill}
   \centering
   \noindent
   \textit{Dedicado a todos os servidores públicos estaduais que, com diligência e dedicação diária,\\zelam pelo patrimônio público e pela segurança da sociedade catarinense.} \vspace*{\fill}
\end{dedicatoria}
"""
    with open(OUTPUT_DIR / "PreTextuais/Dedicatoria.tex", "w", encoding="utf-8") as f:
        f.write(dedicatoria)

    agradecimentos = r"""% PreTextuais/Agradecimentos.tex
\begin{agradecimentos}
À \textbf{Universidade do Estado de Santa Catarina (UDESC)} e aos professores e coordenadores do \textbf{PPGCAP} pelo suporte acadêmico de excelência.

À minha orientadora, \textbf{Profa. Dra. Vivian Kremer Kalempa}, e ao meu coorientador, \textbf{Prof. Dr. Yuri Kaszubowski Lopes}, pela orientação precisa, rigor metodológico, paciência e estímulo intelectual ao longo de toda a pesquisa.

Ao \textbf{Dr. Helio Aisenberg Ferenhof}, pelas orientações e dicas, apontando caminhos que economizaram semanas de pesquisas.

À \textbf{Secretaria de Estado da Administração de Santa Catarina (SEA/SC)}, em especial à Diretoria de Gestão Patrimonial e Gerência de Frotas, pela cooperação institucional e disponibilização dos dados administrativos necessários para a validação empírica.

À \textbf{Diretoria de Apoio Operacional da Secretaria de Administração} pelo apoio e incentivo.

À minha \textbf{família} pela compreensão das horas a fio em frente ao computador, o apoio quando algo dava errado.
\end{agradecimentos}
"""
    with open(OUTPUT_DIR / "PreTextuais/Agradecimentos.tex", "w", encoding="utf-8") as f:
        f.write(agradecimentos)

    epigrafe = r"""% PreTextuais/Epigrafe.tex
\begin{epigrafe}
    \vspace*{\fill}
	\begin{flushright}
		\textit{``A otimização na administração pública não é apenas uma busca por eficiência econômica,\\mas um compromisso ético e republicano de zelo pelo bem comum.''\\(Autor Desconhecido)}
	\end{flushright}
\end{epigrafe}
"""
    with open(OUTPUT_DIR / "PreTextuais/Epigrafe.tex", "w", encoding="utf-8") as f:
        f.write(epigrafe)

    # Resumo (NBR 6028 - 247 palavras, 5 palavras-chave)
    resumo = r"""% PreTextuais/Resumo.tex
\begin{resumo}
A gestão de frotas no setor público historicamente opera sob rotinas reativas emergenciais devido à fragmentação de dados entre cadastros patrimoniais, ordens de serviço (OSs) e abastecimentos. Esta dissertação propõe e avalia uma arquitetura computacional de analítica prescritiva orientada por Inteligência Artificial Explicável (XAI), Teoria dos Grafos e Otimização Inteira Mista (MILP). A base empírica abrange 77.867 ordens de serviço transacionadas entre 2020 e 2026 no Poder Executivo de Santa Catarina, totalizando R\$ 138,76 milhões em dispêndio financeiro aprovado e liquidado (após a retenção de R\$ 60,05 milhões em glosas técnicas preventivas pela fiscalização contratual), vinculadas a 34.280 veículos e 32,84 milhões de litros de combustível. Avaliaram-se regressores e classificadores não lineares sob validação cruzada temporal. No Cenário Canônico S0 (2.000 veículos monitorados por 36 períodos mensais), o modelo MILP resolvido pelo solver HiGHS com gap de otimalidade de 0,0000\% alcançou uma economia simulada de R\$ 9.302.147,26 (17,51\% frente à política inercial), com 100\% de conformidade com manutenções obrigatórias. A fusão multimodal (H1) apresentou significância estatística, mas ganho marginal de 0,41\% no erro médio absoluto, sendo classificada como não sustentada frente ao patamar de relevância prática pré-fixado de 15,0\%. A avaliação de explicabilidade (H4) revelou concordância Top-5 de Jaccard de 39,29\% entre SHAP e LIME, não sustentando a intercambialidade direta dos métodos e fundamentando a necessidade de protocolos de triangulação analítica para auditoria governamental. Por fim, identificaram-se 313 veículos em condição antieconômica para subsidiar decisões de alienação e leilão. Conclui-se que a analítica prescritiva sob restrições contrafactuais auditadas viabiliza ganhos fiscais mensuráveis e transparência decisória para a governança pública.

\vspace{\onelineskip}
\noindent
\textbf{Palavras-chave:} analítica prescritiva; gestão de frotas públicas; teoria dos grafos; inteligência artificial explicável; programação linear inteira mista.
\end{resumo}
"""
    with open(OUTPUT_DIR / "PreTextuais/Resumo.tex", "w", encoding="utf-8") as f:
        f.write(resumo)

    # Abstract (226 words, 5 keywords)
    abstract = r"""% PreTextuais/Abstract.tex
\begin{resumo}[ABSTRACT]
\begin{otherlanguage*}{english}
Public fleet management has historically operated under reactive emergency routines due to fragmented administrative records across asset inventories, maintenance work orders (WOs), and fuel logs. This master's thesis formulates and benchmarks a prescriptive analytics architecture driven by Explainable Artificial Intelligence (XAI), Graph Theory, and Mixed-Integer Linear Programming (MILP). The empirical foundation comprises 77,867 work orders executed between 2020 and 2026 within the State Government of Santa Catarina, totaling BRL 138.76 million in approved and settled expenditures (following BRL 60.05 million retained through technical audit deductions), cross-referenced with 34,280 vehicles and 32.84 million liters of fuel. Nonlinear ensemble learners were evaluated under rolling-window temporal validation. In Canonical Scenario S0 (2,000 vehicles monitored over 36 monthly periods), the MILP model solved by HiGHS with a 0.0000\% optimality gap achieved estimated simulated savings of BRL 9,302,147.26 (17.51\% over the inertial baseline), with 100\% mandatory maintenance compliance. Multimodal data fusion (H1) achieved statistical significance but yielded a marginal error reduction of 0.41\%, failing to reach the pre-registered 15.0\% practical relevance threshold. Explainability benchmarking (H4) revealed a Top-5 Jaccard agreement of 39.29\% between SHAP and LIME, refuting direct method interchangeability and establishing the need for multi-method explanation triangulation in public auditing. Finally, 313 uneconomical vehicles were identified to support statutory disposal procedures. The prescriptive architecture demonstrates measurable efficiency gains and transparent decision-making for public sector governance.

\vspace{\onelineskip}
\noindent
\textbf{Keywords:} prescriptive analytics; public fleet management; graph theory; explainable artificial intelligence; mixed-integer linear programming.
\end{otherlanguage*}
\end{resumo}
"""
    with open(OUTPUT_DIR / "PreTextuais/Abstract.tex", "w", encoding="utf-8") as f:
        f.write(abstract)

    # Listas
    listas = r"""% PreTextuais/Listas.tex
% Lista de Ilustrações
\pdfbookmark[0]{\listfigurename}{lof}
\listoffigures*
\cleardoublepage

% Lista de Tabelas
\pdfbookmark[0]{\listtablename}{lot}
\listoftables*
\cleardoublepage

% Lista de Abreviaturas e Siglas
\begin{siglas}
    \item[ABNT] Associação Brasileira de Normas Técnicas
    \item[ANP] Agência Nacional do Petróleo, Gás Natural e Biocombustíveis
    \item[CPK] Custo por Quilômetro Rodado (Cost per Kilometer)
    \item[CRISP-DM] Cross-Industry Standard Process for Data Mining
    \item[DTMC] Cadeia de Markov de Tempo Discreto (Discrete-Time Markov Chain)
    \item[GFI] Gestão de Frota por Indicadores (Metodologia Oficial SEA/Seplag SC)
    \item[HistGB] HistGradientBoosting Classifier / Regressor (Scikit-Learn)
    \item[LDO / LOA] Lei de Diretrizes Orçamentárias / Lei Orçamentária Anual
    \item[LIME] Local Interpretable Model-agnostic Explanations
    \item[LRF] Lei de Responsabilidade Fiscal (Lei Complementar Federal nº 101/2000)
    \item[MILP] Programação Linear Inteira Mista (Mixed-Integer Linear Programming)
    \item[PCSC] Polícia Civil do Estado de Santa Catarina
    \item[PMSC] Polícia Militar do Estado de Santa Catarina
    \item[PPGCAP] Programa de Pós-Graduação em Computação Aplicada (UDESC)
    \item[PR-AUC] Área sob a Curva de Precisão-Recall (Precision-Recall Area Under Curve)
    \item[ROC-AUC] Área sob a Curva Característica de Operação do Receptor
    \item[SEA / DITI] Secretaria de Estado da Administração / Diretoria de Tecnologia e Informação
    \item[SHAP] Shapley Additive exPlanations (Teoria dos Jogos Cooperativos)
    \item[TCE-SC] Tribunal de Contas do Estado de Santa Catarina
    \item[TCO] Custo Total de Propriedade (Total Cost of Ownership)
    \item[UDESC] Universidade do Estado de Santa Catarina
    \item[XAI] Inteligência Artificial Explicável (Explainable Artificial Intelligence)
\end{siglas}
\cleardoublepage
"""
    with open(OUTPUT_DIR / "PreTextuais/Listas.tex", "w", encoding="utf-8") as f:
        f.write(listas)

    # Sumário
    sumario = r"""% PreTextuais/Sumario.tex
\pdfbookmark[0]{\contentsname}{toc}
\tableofcontents*
\cleardoublepage
"""
    with open(OUTPUT_DIR / "PreTextuais/Sumario.tex", "w", encoding="utf-8") as f:
        f.write(sumario)

def gerar_capitulos():
    # Capítulo 1
    c1 = r"""% Textuais/Capitulo01_Introducao.tex
\chapter{INTRODUÇÃO, CONTEXTUALIZAÇÃO E ANTEPROJETO DE PESQUISA}
\label{cap:introducao}

A gestão de uma frota institucional no setor público exige conciliar disponibilidade física dos veículos, segurança dos servidores e cidadãos, manutenção mecânica, consumo de combustíveis e rigorosos limites orçamentários fixados pela Lei de Responsabilidade Fiscal (LRF) e pela Nova Lei de Licitações (Lei Federal nº 14.133/2021). Essas dimensões deixam vestígios em sistemas administrativos distintos: o cadastro patrimonial identifica características do bem; as ordens de serviço registram peças, mão de obra e falhas; e o módulo de abastecimento informa volume, preço e odômetro.

Historicamente, a fragmentação cadastral e a ausência de modelos analíticos integrados limitaram a gestão a rotinas reativas emergenciais. A literatura aponta que a manutenção preditiva e a analítica prescritiva oferecem meios para antecipar falhas e otimizar recursos, mas enfrentam desafios de qualidade de dados, explicabilidade perante órgãos de controle e formulação sob restrições reais de governo \cite{mahale2025}.

A estrutura lógica e a condução metodológica desta investigação são fundamentadas nos princípios do método lógico para redação e investigação científica preconizado por Volpato \cite{volpato2015}. Sob essa perspectiva epistemológica, a pesquisa é estruturada como um sistema dedutivo fechado e rigoroso: o problema científico decorre de assimetrias reais na gestão pública de frotas; os objetivos estabelecem as metas de falseamento; as hipóteses constituem proposições teóricas verificáveis sob critérios \textit{a priori}; e as conclusões derivam estritamente das evidências quantitativas observadas, respeitando-se os limites de inferência empírica e distinguindo-se categoricamente significância estatística de relevância prática operacional.

\section{As Quatro Hipóteses Centrais de Pesquisa e Critérios Formais}

\begin{itemize}
    \item \textbf{Hipótese H1 (Integração Multimodal):} Conforme formulada originalmente no anteprojeto de pesquisa, a modelagem preditiva multimodal (integrando manutenção, cadastro patrimonial e abastecimento) propõe que a fusão de bases heterogêneas reduz o erro de predição de custo e eleva o PR-AUC frente a modelos restritos exclusivamente a ordens de serviço. Na avaliação experimental, separa-se a comprovação de significância estatística do teste pareado da sua relevância prática operacional (adotando-se na discussão o patamar referencial de 15,0\% de ganho como critério analítico de corte para justificar os custos operacionais de integração contínua de dados legados no setor público).
    
    \item \textbf{Hipótese H2 (Superioridade dos Modelos Não Lineares):} Modelos ensemble baseados em árvores (\textit{HistGradientBoosting} e \textit{Extra Trees}) superam o regressor vetorial de suporte com núcleo radial (\textit{Support Vector Regression -- SVR-RBF}) e baselines lineares paramétricos em tempo de treinamento computacional e métricas preditivas de erro sob distribuição empírica assimétrica não Gaussiana.
    
    \item \textbf{Hipótese H3 (Eficácia Prescritiva do MILP):} A programação linear inteira mista (MILP) orientada por previsões probabilísticas calibradas gera um plano ótimo de intervenções preventivas com custo total esperado estimado como inferior à política inercial em cenário simulado sob os mesmos limites orçamentários, garantindo disponibilidade operacional e cumprimento das revisões obrigatórias.
    
    \item \textbf{Hipótese H4 (Concordância e Auditabilidade da XAI):} As atribuições de importância local e global produzidas pelos métodos de inteligência artificial explicável SHAP (valores de Shapley) e LIME (aproximação linear local) exibem convergência estrutural estrita ($>$85\% de similaridade de Jaccard Top-5), viabilizando sua intercambialidade direta e auditabilidade perante órgãos de controle público (TCE-SC).
\end{itemize}
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo01_Introducao.tex", "w", encoding="utf-8") as f:
        f.write(c1)

    # Capítulo 2
    c2 = r"""% Textuais/Capitulo02_Fundamentacao.tex
\chapter{FUNDAMENTAÇÃO TEÓRICA, MARCO REGULATÓRIO E REVISÃO DA LITERATURA}
\label{cap:fundamentacao}

\section{Marco Regulatório e Governança da Gestão de Frotas Públicas em Santa Catarina}

A transição paradigmática da engenharia de manutenção veicular desdobra-se em quatro estágios evolutivos fundamentais:
(1) \textbf{Reativa/Corretiva} (intervenção emergencial pós-falha, caracterizada por indisponibilidade prolongada do veículo e custos elevados de guincho e reparo);
(2) \textbf{Preventiva Periódica} (intervenções baseadas em cronogramas rígidos de tempo transcorrido ou quilometragem acumulada, incorrendo frequentemente em intervenções desnecessárias ou substituição prematura de componentes íntegros);
(3) \textbf{Preditiva} (monitoramento contínuo de sinais e diagnóstico precoce para estimar a probabilidade condicional de falha em horizontes futuros); e
(4) \textbf{Prescritiva} (integração entre modelos preditivos probabilísticos e programação matemática para determinar não apenas \textit{quando} uma falha poderá ocorrer, mas \textit{qual ação ótima} deve ser executada sob restrições orçamentárias rígidas, capacidade instalada de oficinas e prioridades operacionais de interesse público).

No contexto da administração pública do Estado de Santa Catarina, a governança patrimonial e logística é balizada por normativas específicas:
\begin{itemize}
    \item \textbf{Marco Regulatório Catarinense e Parâmetro Comparativo de Antieconomicidade:} No âmbito do Estado de Santa Catarina, a governança patrimonial, o uso e a gestão de veículos oficiais são estritamente regidos pelos Decretos Estaduais nº 1.488/2008 e nº 2.056/2009. O critério quantitativo de \textbf{40\% do valor venal contábil} -- originário do Artigo 5º do Decreto Estadual nº 47.539/2018 do Estado de Minas Gerais -- é adotado nesta pesquisa estritamente como parâmetro comparativo de simulação analítica e benchmarking interfederativo (conforme referenciado na Cartilha GFI da SEA/SC), e \textbf{não como determinação automática ou obrigação legal impositiva de baixa e leilão para os órgãos do Estado de Santa Catarina}. O limiar de 40\% opera como um indicador preditivo de antieconomicidade para triagem de portfólio, cabendo a decisão administrativa às comissões da SEA/SC.
    \item \textbf{Cartilha de Gestão de Frota por Indicadores (GFI -- SEA, 2026):} Formaliza a matriz oficial de 38 indicadores de desempenho para auditoria de consumo volumétrico de combustível, validação cruzada de hodômetros e regularidade de manutenções.
    \item \textbf{Normas Fiscais (LRF e Lei nº 14.133/2021):} A Lei de Responsabilidade Fiscal e a Nova Lei de Licitações exigem planejamento prévio e comprovação de vantajosidade econômica.
\end{itemize}

\section{Revisão Estruturada da Literatura e Análise Crítica de 40 Trabalhos}

Para delimitar o estado da arte e situar a originalidade desta dissertação, procedeu-se a uma revisão estruturada da literatura contemplando \textbf{40 obras científicas de referência}, cobrindo o período de 1998 a 2026. A taxonomia adotada na matriz bibliográfica classificou os estudos em três extratos de aderência:
(a) \textbf{Classe A (Fundamentais -- 13 obras, 32,5\%):} Trabalhos que fornecem formulações teóricas diretas, modelagens matemáticas ou trade-offs de confiabilidade essenciais à arquitetura proposta;
(b) \textbf{Classe B (Complementares Relevantes -- 17 obras, 42,5\%):} Estudos que abordam modelagens correlatas, técnicas heurísticas pontuais ou taxonomias de roteamento e despacho; e
(c) \textbf{Classe C (Contextuais -- 10 obras, 25,0\%):} Pesquisas em domínios adjacentes que provêm subsídios conceituais.

Dentre os estudos que conectam a previsão à decisão operacional, \citeonline{chien2012} e \citeonline{cao2023} modelam políticas sob deterioração e choques aleatórios; \citeonline{zheng2022} analisam políticas híbridas de reparo sob modelo de riscos proporcionais; e \citeonline{hu2012} consideram manutenção oportunística em sistemas complexos com dependências entre componentes.

\section{Fundamentos Teóricos Estruturantes Complementares}

Além dos 40 estudos aplicados mapeados na matriz, a presente pesquisa ancora-se em referenciais teóricos seminais da literatura científica:
\begin{enumerate}
    \item \textbf{Transição da Predição à Prescrição Ótima \cite{bertsimas2020}:} Estabelece a teoria matemática da analítica prescritiva orientada por dados com garantia de otimalidade assintótica.
    \item \textbf{Prevenção de Vazamento de Dados e Reprodutibilidade \cite{kapoor2023}:} Mapeia as causas de falha de generalização por \textit{data leakage} temporal.
    \item \textbf{Interpretabilidade no Setor Público \cite{rudin2019}:} Fundamenta a necessidade de escrutínio rigoroso sobre modelos black-box em decisões públicas.
    \item \textbf{Valores de Shapley \cite{lundberg2017}:} Propriedades axiomáticas de aditividade e simetria do SHAP.
    \item \textbf{Aproximações Locais Interpretáveis \cite{ribeiro2016}:} Formulação agnóstica do algoritmo LIME.
    \item \textbf{Detecção de Comunidades em Redes Complexas \cite{blondel2008}:} Otimização de modularidade via algoritmo de Louvain.
    \item \textbf{Validação Sequencial Temporal \cite{bergmeir2012}:} Protocolo \textit{walk-forward} sem antecipação cronológica (\textit{lookahead bias}).
\end{enumerate}
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo02_Fundamentacao.tex", "w", encoding="utf-8") as f:
        f.write(c2)

    # Capítulo 3
    c3 = r"""% Textuais/Capitulo03_Metodologia.tex
\chapter{METODOLOGIA CRISP-DM, BASE EMPÍRICA MULTIMODAL E SANEAMENTO}
\label{cap:metodologia}

\section{Delineamento Experimental e Enquadramento Lógico-Metodológico}

O delineamento experimental da pesquisa estrutura-se segundo o ciclo de mineração de dados CRISP-DM (\textit{Cross-Industry Standard Process for Data Mining}), operacionalizado em estrita consonância com os postulados do método lógico de investigação e redação científica preconizados por Volpato \cite{volpato2015}. Esse enquadramento garante a vinculação indissolúvel entre a questão norteadora (otimização prescritiva sob restrições reais de governo), o controle rígido de variáveis preditoras (prevenção de viés de antecipação com embargo temporal de 30 dias), a suficiência da base censitária (350.737 registros de itens de manutenção) e o falseamento empírico das hipóteses H1 a H4, impedindo inferências extrapolativas que ultrapassem a validade interna dos dados.

\section{Estrutura Contábil do Dispêndio Auditado}

Para assegurar total transparência e afastar quaisquer ambiguidades contábeis, esclarece-se a relação entre os montantes financeiros analisados na base empírica de 77.867 ordens de serviço (350.737 itens):
\begin{itemize}
    \item \textbf{Valor Orçado Bruto Inicial: R\$ 198.806.964,49 (100,0\%).} Representa o montante original orçado e demandado pelas oficinas mecânicas credenciadas antes de qualquer intervenção fiscalizadora do Estado.
    \item \textbf{Glosas Técnicas e Retenções Fiscais: R\$ 60.047.310,67 (30,2\%).} Corresponde ao montante histórico de despesas orçadas que foram formalmente bloqueadas, glosadas ou retidas pelos fiscais de contrato da SEA/SC em decorrência de sobrepreço, desconformidade com tabelas de tempo-padrão de montadoras ou orçamentação indevida de peças. Esse indicador quantifica a atuação preventiva do controle administrativo contratual (despesas que deixaram de ser liquidadas), sem configurar automaticamente economia de caixa livre realizada, a qual depende de comprovação de impacto orçamentário líquido final.
    \item \textbf{Dispêndio Financeiro Efetivamente Aprovado e Liquidado: R\$ 138.759.653,82 (69,8\%).} Montante que permaneceu após as glosas, sendo devidamente atestado, faturado e pago pelo erário público estadual.
\end{itemize}

\noindent\textbf{Fechamento Contábil:} \textbf{Valor Orçado Bruto (R\$ 198,81M) = Glosas Retidas (R\$ 60,05M) + Dispêndio Aprovado (R\$ 138,76M)}. Os valores não são independentes nem concorrentes, mas etapas sucessivas e complementares do fluxo de auditoria e liquidação da despesa pública.

\begin{figure}[H]
    \centering
    \caption{Série Temporal Histórica Mensal de Gastos de Manutenção (2020--2026)}
    \includegraphics[width=0.9\textwidth]{figuras/fig01_serie_gastos_manutencao.png}
    \vspace{0.2cm}
    \fonte{Dados empíricos da frota pública de Santa Catarina processados pelo autor (2026).}
    \label{fig:serie_gastos}
\end{figure}

\section{Protocolo de Validação Temporal em 5 Dobras Sequenciais}

A dissertação adota dois protocolos complementares e independentes, devidamente segregados para finalidades metodológicas distintas:
\begin{itemize}
    \item \textbf{Protocolo A (Validação Temporal em Janela Expansiva -- Walk-Forward 5 Dobras):} Executado sobre o histórico cronológico de Ordens de Serviço (base de 60.114 OSs faturadas, 2020--2026), expandindo de 15.587 OSs (Dobra 1) até 45.145 OSs de treino na Dobra 5 (com 5.681 OSs no conjunto de teste out-of-time), sob embargo estrito de 30 dias entre treino e teste. Avalia a estabilidade de generalização out-of-time frente à degradação cronológica, reportando a média temporal agregada de \textbf{PR-AUC = 0,8941 $\pm$ 0,0089}, \textbf{ROC-AUC = 0,7544 $\pm$ 0,0281}, \textbf{Brier Score = 0,1378 $\pm$ 0,0025} e MAE = R\$ 2.273,16 $\pm$ R\$ 35,15.
    
    \item \textbf{Protocolo B (Particionamento Holdout Out-of-Time Canônico com Calibração Isotônica):} Executado para seleção agnóstica de hiperparâmetros, ranking de explicabilidade XAI e homologação de calibragem probabilística, reportando no conjunto de teste independente do ciclo final (2025--2026, 4.754 amostras) \textbf{PR-AUC = 0,9510}, \textbf{ROC-AUC = 0,8743 [IC 95\%: 0,8617; 0,8878]}, F1-Score = 0,9113, Brier Score = 0,1043, ECE = 0,0174 e MAE = R\$ 2.236,06 [IC 95\%: 2.146,76; 2.321,17]. A métrica pontual de 0,9510 e a média multianual de 0,8941 coexistem de forma plenamente coerente por derivarem de agregações amostrais e horizontes temporais distintos.
\end{itemize}

\noindent\textbf{Regras de Disponibilidade Temporal das Variáveis e Embargo de 30 Dias:} Toda variável preditora é calculada estritamente a partir de eventos consumados até a data de corte $T_{\text{corte}}$. O embargo de 30 dias entre treino e teste expurga ordens de serviço abertas ou em trânsito de oficina, prevenindo viés de antecipação cronológica (\textit{lookahead bias}).

\section{Protocolo de Anonimização e Conformidade com a LGPD (Lei nº 13.709/2018)}

Para assegurar total conformidade jurídica e ética com a Lei Geral de Proteção de Dados Pessoais (LGPD), todas as placas veiculares reais foram convertidas em identificadores criptográficos irreversíveis (\texttt{VEIC\_HASH}), fornecedores mecânicos foram mascarados (\texttt{FORNECEDOR\_XXX}) e servidores públicos foram desvinculados dos registros.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo03_Metodologia.tex", "w", encoding="utf-8") as f:
        f.write(c3)

    # Capítulo 4 a 11 (resumos metodológicos completos)
    c4 = r"""% Textuais/Capitulo04_DeteccaoAnomalias.tex
\chapter{DETECÇÃO NÃO SUPERVISIONADA DE ANOMALIAS E AUDITORIA FISCAL}
\label{cap:anomalias}

O algoritmo \textit{Isolation Forest} isolou atipicidades multidimensionais no espaço contínuo composto por custo aprovado, valor orçado, duração de reparo, quilometragem, idade veicular e quantidade de itens. Com parâmetro de contaminação calibrado em $\nu = 0,0085$ (0,85\%) sobre o universo de \textbf{77.867 Ordens de Serviço consolidadas}, foram isoladas \textbf{662 ordens de serviço anômalas} (com índice de similaridade de Jaccard multissemente certificado em 0,8055), que concentraram R\$ 17,10 milhões em orçamentos cotados pelas oficinas e R\$ 16,58 milhões em dispêndio aprovado.

\begin{figure}[H]
    \centering
    \caption{Distribuição dos Escores de Anomalia do Isolation Forest}
    \includegraphics[width=0.85\textwidth]{figuras/fig05_distribuicao_escores_anomalia.png}
    \vspace{0.2cm}
    \fonte{Dados empíricos da frota pública de Santa Catarina processados pelo autor (2026).}
    \label{fig:iforest}
\end{figure}

Ressalta-se que o algoritmo atua como instrumento de triagem prioritária para fiscalização técnica, e não como comprovação jurídica autônoma de ilicitude.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo04_DeteccaoAnomalias.tex", "w", encoding="utf-8") as f:
        f.write(c4)

    c5 = r"""% Textuais/Capitulo05_ClassificacaoRisco.tex
\chapter{CLASSIFICAÇÃO NÃO LINEAR DE RISCO OPERACIONAL, ACURÁCIA E CALIBRAÇÃO (HIPÓTESE H2)}
\label{cap:classificacao}

O modelo \textit{HistGradientBoosting} sagrou-se campeão absoluto na classificação de risco com PR-AUC de \textbf{0,9510}, ROC-AUC de \textbf{0,8743} [IC 95\%: 0,8617; 0,8878], F1-Score de \textbf{0,9113} e ECE de \textbf{0,0174}. A calibração de probabilidades reduziu o Brier Score de 0,1695 para 0,1043.

\begin{figure}[H]
    \centering
    \caption{Curvas ROC e Precision-Recall dos Classificadores de Risco}
    \includegraphics[width=0.85\textwidth]{figuras/fig07_curvas_roc_modelos.png}
    \vspace{0.2cm}
    \fonte{Dados empíricos da frota pública de Santa Catarina processados pelo autor (2026).}
    \label{fig:roc}
\end{figure}

O teste não paramétrico de DeLong et al. (1988) confirmou a superioridade estatística frente à Regressão Logística ($Z = 16,39; p < 10^{-50}$).
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo05_ClassificacaoRisco.tex", "w", encoding="utf-8") as f:
        f.write(c5)

    c6 = r"""% Textuais/Capitulo06_RegressaoCustos.tex
\chapter{REGRESSÃO NÃO LINEAR DE CUSTOS, CONFRONTO COM SVR-RBF E HIPÓTESE H2}
\label{cap:regressao}

Avaliaram-se múltiplos regressores ensemble frente ao \textit{SVR-RBF} e à mediana histórica de custos. O modelo \textbf{HistGradientBoosting} obteve o menor RMSE (R\$ 3.780,20, redução de 9,97\% frente ao baseline), menor MAE entre os ensembles (R\$ 2.236,06) e tempo de treinamento de 1,8 segundos frente à inviabilidade computacional assintótica do SVR.

O teste pareado de Wilcoxon com correção de Holm confirmou $p < 10^{-4}$, sustentando a Hipótese H2.

\section{Estudo Ablativo Multimodal e Avaliação da Hipótese H1}

O estudo ablativo confrontou modelos baseados exclusivamente em ordens de serviço (M) contra modelos integrados (M+P+A). A inclusão de dados multimodais reduziu o MAE em R\$ 9,47 por ordem de serviço (ganho de \textbf{+0,41\% [IC 95\%: 0,28\%; 0,54\%]}). Embora estatisticamente significante ($p < 10^{-15}$), o ganho não atingiu o patamar de relevância prática pré-registrado de 15,0\%. Portanto, \textbf{a Hipótese H1 é formalmente classificada como NÃO SUSTENTADA} sob a régua operacional pré-estabelecida.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo06_RegressaoCustos.tex", "w", encoding="utf-8") as f:
        f.write(c6)

    c7 = r"""% Textuais/Capitulo07_ModelagemTemporal.tex
\chapter{MODELAGEM TEMPORAL, DECOMPOSIÇÃO E PREVISÃO DE DEMANDA}
\label{cap:temporal}

A modelagem de séries temporais via \textit{Prophet} isolou componentes de tendência e sazonalidade anual, com picos de despesa em novembro e dezembro decorrentes do encerramento do exercício financeiro estadual.

\begin{figure}[H]
    \centering
    \caption{Decomposição da Série Temporal de Gastos via Prophet}
    \includegraphics[width=0.85\textwidth]{figuras/fig19_decomposicao_prophet.png}
    \vspace{0.2cm}
    \fonte{Dados empíricos da frota pública de Santa Catarina processados pelo autor (2026).}
    \label{fig:prophet}
\end{figure}
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo07_ModelagemTemporal.tex", "w", encoding="utf-8") as f:
        f.write(c7)

    c8 = r"""% Textuais/Capitulo08_XAI.tex
\chapter{INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL (XAI), TRIANGULAÇÃO E CONFIABILIDADE (HIPÓTESE H4)}
\label{cap:xai}

A explicabilidade dos modelos preditivos foi avaliada via valores de Shapley (SHAP) e aproximações locais lineares (LIME). Ao confrontar os rankings de relevância de atributos sobre as instâncias auditadas, obteve-se \textbf{similaridade de Jaccard Top-5 de 39,29\% (39,3\%)} e \textbf{correlação de postos de Spearman de $\rho = 0,3680$}.

\begin{figure}[H]
    \centering
    \caption{Comparativo de Importância de Features entre SHAP e LIME}
    \includegraphics[width=0.85\textwidth]{figuras/fig13_concordancia_shap_lime.png}
    \vspace{0.2cm}
    \fonte{Dados empíricos da frota pública de Santa Catarina processados pelo autor (2026).}
    \label{fig:xai}
\end{figure}

Em decorrência dessa divergência geométrica intrínseca, a \textbf{Hipótese H4 NÃO FOI SUSTENTADA} sob o limiar a priori de alta concordância ($>$85\%), fundamentando a necessidade de protocolos de triangulação explicativa multimetodológica na administração pública.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo08_XAI.tex", "w", encoding="utf-8") as f:
        f.write(c8)

    c9 = r"""% Textuais/Capitulo09_OtimizacaoPrescritiva.tex
\chapter{OTIMIZAÇÃO PRESCRITIVA (MILP), PROTOCOLO S0 E DECISÃO SOB RESTRIÇÕES (HIPÓTESE H3)}
\label{cap:milp}

A formulação canônica de Programação Linear Inteira Mista (\textit{Mixed-Integer Linear Programming} -- MILP) modela a alocação ótima e o escalonamento de manutenções preventivas veiculares sob restrições orçamentárias e de capacidade instalada da rede credenciada de oficinas. A função objetivo bi-critério visa minimizar conjuntamente o dispêndio orçamentário direto com intervenções programadas e o risco operacional residual decorrente de potenciais quebras corretivas:

\begin{equation}
    \min_{x} \quad Z = \sum_{t=1}^{T} \sum_{i=1}^{N} \left[ \alpha \cdot c_{it} x_{it} + \beta \cdot r_{it} (1 - x_{it}) \right]
    \label{eq:milp_objetivo}
\end{equation}

\noindent sujeita ao conjunto de restrições operacionais, orçamentárias e físicas:
\begin{align}
    \sum_{i=1}^{N} c_{it} x_{it} &\le B_t, \quad \forall t \in \{1, \dots, T\} \label{eq:milp_orcamento} \\
    \sum_{i=1}^{N} h_{it} x_{it} &\le H_t, \quad \forall t \in \{1, \dots, T\} \label{eq:milp_capacidade} \\
    x_{it} &\ge m_{it}, \quad \forall (i, t) \mid m_{it} = 1 \label{eq:milp_obrigatoria} \\
    x_{it} &\in \{0, 1\}, \quad \forall i \in \{1, \dots, N\}, \, \forall t \in \{1, \dots, T\} \label{eq:milp_dominio}
\end{align}

\noindent na qual os índices, variáveis de decisão e parâmetros do modelo linearizado são formalmente definidos por:
\begin{itemize}
    \item $i \in \{1, \dots, N\}$: índice correspondente a cada veículo oficial monitorado na frota pública ($N = 2.000$ na instância canônica S0);
    \item $t \in \{1, \dots, T\}$: índice do período de planejamento temporal discreto em meses ($T = 36$ períodos mensais, cobrindo o triênio de governança);
    \item $x_{it} \in \{0, 1\}$: variável de decisão binária que assume o valor $1$ caso o veículo $i$ seja escalonado para manutenção preventiva no período $t$, e $0$ caso contrário, conforme fixado na Equação~(\ref{eq:milp_dominio});
    \item $c_{it}$: custo unitário financeiro estimado para a execução da manutenção preventiva do veículo $i$ no mês $t$ (em Reais);
    \item $r_{it}$: custo de risco operacional associado à falha corretiva do veículo $i$ no mês $t$ caso a intervenção preventiva não seja executada ($x_{it} = 0$), calculado a partir da probabilidade condicional de falha calibrada multiplicada pelo custo severo de reparo emergencial;
    \item $\alpha, \beta \in [0, 1]$: fatores exógenos de ponderação no \textit{trade-off} bi-objetivo entre dispêndio orçamentário direto ($\alpha$) e mitigação do risco de indisponibilidade ($\beta$), satisfazendo $\alpha + \beta = 1$ (adotando-se $\alpha = 0,5$ e $\beta = 0,5$ no cenário de referência equilibrado);
    \item $B_t$: teto orçamentário financeiro máximo disponível para o custeio de manutenções preventivas no período mensal $t$ (em Reais), formalizado na Equação~(\ref{eq:milp_orcamento}), vinculado aos limites de empenho fixados na Lei Orçamentária Anual (LOA);
    \item $h_{it}$: demanda estimada de mão de obra para a execução da manutenção preventiva do veículo $i$ no mês $t$ (em horas-homem de serviço de oficina);
    \item $H_t$: capacidade máxima física disponível de mão de obra na rede credenciada de oficinas mecânicas no período $t$ (em horas-homem mensais), delimitada na Equação~(\ref{eq:milp_capacidade});
    \item $m_{it} \in \{0, 1\}$: parâmetro binário de obrigatoriedade legal ou técnica que impõe preventivas compulsórias ($x_{it} = 1$) para o veículo $i$ no período $t$, conforme a Equação~(\ref{eq:milp_obrigatoria}), garantindo o cumprimento compulsório de revisões de segurança, garantias contratuais de montadora ou itens de risco viário crítico.
\end{itemize}

No Cenário de Referência S0 (2.000 veículos monitorados por 36 períodos mensais, totalizando 72.000 variáveis binárias e 6.072 restrições lineares), o solver \textit{HiGHS} convergiu em 8,92 segundos com \textbf{MIP Gap certificado de 0,0000\%}, obtendo um custo To-Be otimizado de \textbf{R\$ 43.837.633,31} frente à linha de base inercial de R\$ 53.139.780,57. Esse resultado demonstra uma \textbf{economia líquida potencial simulada de R\$ 9.302.147,26 (redução de 17,51\%)} com 95,26\% de disponibilidade média da frota e 100\% de cumprimento compulsório das manutenções mandatórias de segurança.

\section{Análise de Preços-Sombra (Shadow Prices) e Capacidade de Oficinas}

Os multiplicadores duais ($\lambda_t$) associados à restrição orçamentária da Equação~(\ref{eq:milp_orcamento}) governada por $B_t$ foram extraídos da \textbf{relaxação linear contínua (LP)} da instância S0. Ressalva-se que, em problemas inteiros com variáveis binárias ($x_{it} \in \{0, 1\}$), \textbf{não há teoria de dualidade forte equivalente à programação linear clássica}: os preços-sombra derivados da relaxação contínua constituem indicadores aproximados de sensibilidade marginal local e \textit{não devem ser interpretados como derivadas estritas no problema MILP}, cuja resposta a variações orçamentárias de $B_t$ é discreta e deve ser aferida por reotimização paramétrica global.

Por sua vez, a restrição de capacidade física das oficinas credenciadas ($H_t$), expressa na Equação~(\ref{eq:milp_capacidade}), não se mostrou vinculante em nenhum dos 36 períodos da simulação (\textbf{0,0\% dos meses com multiplicador dual nulo}). Esse comportamento evidencia que, \textit{sob os parâmetros agregados de capacidade de horas adotados no cenário S0}, a dotação financeira $B_t$ constitui o gargalo ativo primário na governança de frotas públicas. Todavia, esse resultado numérico \textbf{não autoriza a inferência de que haja ociosidade física generalizada em todas as mecânicas conveniadas de Santa Catarina}, visto que a parametrização agregada de $H_t$ não captura atritos logísticos locais, picos sazonais de fim de exercício, especialidades mecânicas raras ou barreiras de distância geográfica entre unidades operacionais e estabelecimentos credenciados.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo09_OtimizacaoPrescritiva.tex", "w", encoding="utf-8") as f:
        f.write(c9)

    c10 = r"""% Textuais/Capitulo10_TeoriaGrafos.tex
\chapter{TEORIA DOS GRAFOS \& REDES COMPLEXAS NA GESTÃO DE FROTAS PÚBLICAS}
\label{cap:grafos}

A modelagem de redes articulou a rede bipartida entre 7.291 veículos e 1.039 oficinas credenciadas, detectando \textbf{18 comunidades regionais com modularidade Louvain $Q = 0,5646$}, além do grafo de co-ocorrência de falhas com $Q = 0,384$.

\begin{figure}[H]
    \centering
    \caption{Rede Bipartida de Estabelecimentos Credenciados e Comunidades de Louvain}
    \includegraphics[width=0.85\textwidth]{figuras/fig94_rede_fornecedores_louvain.png}
    \vspace{0.2cm}
    \fonte{Dados empíricos da frota pública de Santa Catarina processados pelo autor (2026).}
    \label{fig:grafos}
\end{figure}

Ressalva-se que a identificação de agrupamentos densos opera estritamente como ferramenta de priorização amostral para auditoria, e não como comprovação de conluio.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo10_TeoriaGrafos.tex", "w", encoding="utf-8") as f:
        f.write(c10)

    c11 = r"""% Textuais/Capitulo11_GovernancaPublica.tex
\chapter{GOVERNANÇA PÚBLICA, MATRIZ DOS 38 INDICADORES GFI E CARTILHA SEA 2026}
\label{cap:governanca}

Apresenta-se a matriz dos 38 indicadores oficiais da Cartilha GFI da SEA/SC e a identificação de 313 veículos em estado antieconômico (gasto acumulado de oficina superior a 40\% do valor venal contábil), fornecendo subsídios técnicos objetivos para processos administrativos de desfazimento e leilão.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo11_GovernancaPublica.tex", "w", encoding="utf-8") as f:
        f.write(c11)

    c12 = r"""% Textuais/Capitulo12_GaleriaFiguras.tex
\chapter{GALERIA EXAUSTIVA E ANÁLISE EXPLICATIVA DAS FIGURAS DA PESQUISA}
\label{cap:galeria}

Em atendimento estrito aos princípios de transparência analítica e reprodutibilidade, este capítulo cataloga as principais evidências visuais e experimentais geradas no pipeline de pesquisa, cobrindo séries históricas, diagnósticos de anomalias, curvas ROC, explicabilidade via SHAP/LIME e otimização prescritiva MILP.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo12_GaleriaFiguras.tex", "w", encoding="utf-8") as f:
        f.write(c12)

    # Capítulo 13 com as correções científicas exatas
    c13 = r"""% Textuais/Capitulo13_Conclusoes.tex
\chapter{CONCLUSÕES, SUSTENTAÇÃO DAS HIPÓTESES E RECOMENDAÇÕES ACADÊMICAS}
\label{cap:conclusoes}

A presente dissertação investigou a aplicação integrada de técnicas de aprendizado de máquina, inteligência artificial explicável, teoria dos grafos e programação matemática à gestão de frotas públicas. Os experimentos permitiram avaliar as quatro hipóteses formuladas, identificando resultados favoráveis à otimização prescritiva no cenário simulado, ganhos preditivos modestos decorrentes da integração de bases administrativas e limitações na concordância entre métodos de explicabilidade. Os resultados devem ser interpretados à luz das condições experimentais, das características dos dados utilizados e da ausência de validação prospectiva da economia projetada.

\section{Síntese da Sustentação das Hipóteses}

\begin{enumerate}
    \item \textbf{Hipótese H1 -- NÃO SUSTENTADA SEGUNDO O CRITÉRIO DE RELEVÂNCIA PRÁTICA (apesar de ganho estatístico significante com $p < 10^{-6}$):}
    \textit{Classificação epistemológica:} Sob a ótica puramente inferencial/estatística, a hipótese de ganho preditivo foi formalmente confirmada (Wilcoxon pareado $p < 10^{-6}$). Contudo, sob o critério de relevância prática e operacional previamente estabelecido (limiar mínimo de 15,0\% de redução do erro para justificar a sobrecarga de governança e engenharia de dados de integração contínua de bases heterogêneas), a hipótese H1 classifica-se formal e conclusivamente como \textbf{NÃO SUSTENTADA} (ganho observado de apenas 1,13\% no teste out-of-time e 0,41\% no estudo ablativo).
    
    \item \textbf{Hipótese H2 -- PARCIALMENTE SUSTENTADA:}
    Os modelos ensemble baseados em árvores superaram categoricamente o regressor vetorial de suporte (SVR-RBF) em precisão preditiva (MAE de R\$ 2.236,06 vs R\$ 2.569,20; $p < 10^{-4}$) e em tempo computacional (1,8s vs inviabilidade $O(N^2)$). Na classificação de risco, o HistGB superou amplamente a Regressão Logística (ROC-AUC de 0,8743 vs 0,8268; $p < 10^{-50}$). Na regressão direta em MAE, a mediana teórica apresentou menor erro devido à forte assimetria ($L_1$), mas o HistGB reduziu o RMSE em 9,97\%.
    
    \item \textbf{Hipótese H3 -- SUSTENTADA NO CENÁRIO S0 E SIMULAÇÃO TRIENAL:}
    O modelo prescritivo MILP convergiu para o ótimo global com Gap de Otimalidade certificado pelo solver HiGHS de 0,0000\% e diferença para a relaxação linear de 0,00057\% (R\$ 248,52), propiciando economia simulada de R\$ 9.302.147,26 (17,51\% sobre a linha de base inercial) no Cenário S0 com 100\% de cumprimento compulsório das manutenções de segurança.
    
    \item \textbf{Hipótese H4 -- NÃO SUSTENTADA NO LIMIAR A PRIORI ($>$85\%):}
    A similaridade de Jaccard Top-5 entre SHAP e LIME foi de 39,29\% e correlação de Spearman de $\rho = 0,3680$, demonstrando a necessidade imperativa de protocolos de triangulação analítica multimetodológica na governança pública.
\end{enumerate}

\section{Validade Externa, Condições de Contorno e Generalização}

A arquitetura apresenta potencial de adaptação a outros entes federativos, condicionado à compatibilidade estrutural e semântica das bases administrativas, à disponibilidade dos atributos requeridos e à parametrização das restrições normativas e operacionais locais. Conforme as características dos sistemas institucionais, poderão ser necessárias adaptações nas rotinas de ingestão, integração, processamento e validação dos dados.

O arcabouço metodológico ancora-se em quatro dimensões:
\begin{itemize}
    \item \textbf{Diversidade Amostral Interna:} Cobertura de 34.280 veículos e 77.867 ordens de serviço (regimes severos, saúde, fiscalização e administrativos leves).
    \item \textbf{Parametrização Exógena:} Desacoplamento entre formulação matemática e parâmetros normativos locais (teto de 40\% de antieconomicidade, orçamentos e prazos de desincorporação).
    \item \textbf{Compatibilidade Contratual:} O arcabouço analítico ancora-se no modelo de contratação de manutenção terceirizada mediante catálogos de tempo-padrão de montadora e tabelas referenciais de peças (como Sintec e Audatex), \textbf{modelo de contratação utilizado em diferentes administrações públicas} sob a Lei Federal nº 14.133/2021.
    \item \textbf{Resiliência sob Estresse Macroeconômico:} Estabilidade de 96,4\% da base de variáveis ativas de decisão em 1.000 iterações de Monte Carlo com inflação setorial de 6,08\% a.a.
\end{itemize}

No benchmark computacional sintético calibrado (Base B), \textbf{27 veículos (5,4\% da frota sintética) foram sinalizados pelo critério simulado de antieconomicidade}. Ressalva-se que esse teste em benchmark sintético demonstra a execução do pipeline no cenário sintético avaliado e a estabilidade numérica das formulações, mas não substitui validações empíricas prospectivas em bases administrativas de outros entes federativos.
"""
    with open(OUTPUT_DIR / "Textuais/Capitulo13_Conclusoes.tex", "w", encoding="utf-8") as f:
        f.write(c13)

def gerar_pos_textuais():
    # Apêndice A (Formulação Matemática e 6.072 restrições)
    ap_a = r"""% PosTextuais/ApendiceA.tex
\begin{apendicesenv}
\partapendices

\chapter{FORMULAÇÃO MATEMÁTICA COMPLETA E LINEARIZADA DO SOLVER MILP}
\label{apendice:a}

O problema de alocação ótima e escalonamento de manutenções com restrição de capacidade física e teto orçamentário para a frota do Estado de Santa Catarina é formulado canonicamente como um modelo de Programação Linear Inteira Mista (\textit{Mixed-Integer Linear Programming} -- MILP), estruturado pela função objetivo multiobjetivo linearizada:

\begin{equation}
    \min_{x} \quad Z = \sum_{t=1}^T \sum_{i=1}^N \left[ \alpha \cdot c_{it} x_{it} + \beta \cdot r_{it} (1 - x_{it}) \right]
    \label{eq:apendice_milp_obj}
\end{equation}

\noindent sujeita às restrições estruturais de governança e viabilidade física:
\begin{align}
    \sum_{i=1}^N c_{it} x_{it} &\le B_t, \quad \forall t \in \{1, \dots, T\} \label{eq:apendice_milp_bt} \\
    \sum_{i=1}^N h_{it} x_{it} &\le H_t, \quad \forall t \in \{1, \dots, T\} \label{eq:apendice_milp_ht} \\
    x_{it} &\ge m_{it}, \quad \forall (i, t) \mid m_{it} = 1 \label{eq:apendice_milp_mit} \\
    x_{it} &\in \{0, 1\}, \quad \forall i \in \{1, \dots, N\}, \, \forall t \in \{1, \dots, T\} \label{eq:apendice_milp_dom}
\end{align}

\noindent nas quais:
\begin{itemize}
    \item A Equação~(\ref{eq:apendice_milp_bt}) estabelece a restrição de teto orçamentário financeiro mensal, impondo que o somatório dos custos de intervenção preventiva $c_{it}$ de todos os veículos $i \in \{1, \dots, N\}$ escalonados no período $t$ ($x_{it} = 1$) não exceda a dotação financeira disponível $B_t$;
    \item A Equação~(\ref{eq:apendice_milp_ht}) formaliza o limite de capacidade instalada da rede credenciada de mecânicas, garantindo que a demanda agregada em horas de mão de obra $h_{it}$ não ultrapasse o teto mensal $H_t$;
    \item A Equação~(\ref{eq:apendice_milp_mit}) impõe o cumprimento compulsório das manutenções mandatórias de segurança e revisões contratuais obrigatórias de garantia ($m_{it} = 1$), vedando a postergação de serviços críticos pelo solver;
    \item A Equação~(\ref{eq:apendice_milp_dom}) define o domínio binário de decisão integral das variáveis $x_{it}$.
\end{itemize}

\noindent\textbf{Métricas Poliedrais e Complexidade Computacional da Instância S0:}

A instância canônica S0 contempla 72.000 variáveis binárias de decisão, correspondentes a 2.000 veículos avaliados ao longo de 36 períodos mensais. O modelo apresenta 6.072 restrições lineares reportadas, compreendendo limites orçamentários ($B_t$), capacidades operacionais ($H_t$) e exigências de manutenção mandatória ($m_{it}$). A quantidade de restrições efetivamente ativas na solução ótima foi determinada a partir dos resultados do solver \textit{HiGHS}, demonstrando que o teto orçamentário $B_t$ é vinculante nos meses de maior demanda de revisão preventiva, enquanto a capacidade agregada $H_t$ operou com folga sob os parâmetros vigentes da rede credenciada catarinense.
"""
    with open(OUTPUT_DIR / "PosTextuais/ApendiceA.tex", "w", encoding="utf-8") as f:
        f.write(ap_a)

    # Apêndice B
    ap_b = r"""% PosTextuais/ApendiceB.tex
\chapter{PROTOCOLO DE AUDITORIA E INTEGRIDADE PÚBLICA DA SEA DITI}
\label{apendice:b}

Em estrita conformidade com a Lei Federal nº 14.133/2021 e a Instrução Normativa nº 05/2024 da SEA/SC, o protocolo de auditoria preventiva sobre fornecedores mecânicos compreende:
\begin{itemize}
    \item Triagem técnica preventiva para itens orçados com divergência superior a 2 desvios-padrão da mediana histórica regional, assegurando o contraditório e ampla defesa;
    \item Direcionamento de fiscalização presencial para estabelecimentos credenciados agrupados em comunidades de alta densidade financeira e suspeição estrutural (Louvain $Q > 0,35$);
    \item Comunicação formal ao Tribunal de Contas de Santa Catarina (TCE-SC) das ordens atípicas isoladas pelo \textit{Isolation Forest}.
\end{itemize}
"""
    with open(OUTPUT_DIR / "PosTextuais/ApendiceB.tex", "w", encoding="utf-8") as f:
        f.write(ap_b)

    # Apêndice C
    ap_c = r"""% PosTextuais/ApendiceC.tex
\chapter{CADERNO METODOLÓGICO DE REPRODUTIBILIDADE (DIRETRIZES ACM E INFORMS)}
\label{apendice:c}

Em alinhamento com as diretrizes da ACM e da INFORMS, o framework disponibiliza semente determinística global (seed 42), dicionário de variáveis, linhagem completa de dados, código aberto dos modelos e suíte automatizada de testes com Pytest (10/10 testes aprovados).

\section{Delimitação entre Protocolo A e Protocolo B na Portabilidade}

\begin{itemize}
    \item \textbf{Protocolo A (Base Processada em Parquet com Hashes SHA-256 e Anonimização LGPD):} Apresenta portabilidade plenamente verificada e congruência matemática absoluta entre os ambientes Linux e Windows 11 (zero drift e diferença de R\$ 0,00 no fechamento aritmético do solver HiGHS, com 20 de 20 checkpoints aprovados).
    \item \textbf{Protocolo B (Ingestão Primária a partir do CSV Bruto de 1,2 GB):} O código de saída 1 observado no script preliminar no ambiente Windows decorreu exclusivamente da supressão deliberada do arquivo CSV desanonimizado, retido por imperativo de proteção de dados pessoais (LGPD). Portanto, o Protocolo B permanece condicionado à disponibilização institucional dos dados brutos.
\end{itemize}

\section{Comprovação de Reprodutibilidade via Trilha de Logs e Artefatos Originais (Protocolo A)}

A reprodutibilidade experimental é rigorosamente bem delimitada no \textbf{Protocolo A}, assegurando portabilidade multiplataforma autônoma e congruência matemática absoluta (20 de 20 checkpoints aprovados, zero \textit{drift} e fechamento financeiro exato ao centavo de R\$ 9.302.147,26 no Cenário S0 do solver HiGHS). Contudo, em estrito rigor metodológico e pericial, a confirmação independente por pesquisadores externos e órgãos de controle público (TCE-SC) não se apoia em alegações abstratas: ela \textbf{depende diretamente da verificação e conferência cruzada dos logs de execução e da integridade criptográfica dos artefatos originais preservados no repositório}.

Para viabilizar a auditoria forense integral sem necessidade de requisição à custódia restrita dos dados brutos (preservados sob sigilo da LGPD), disponibilizam-se as assinaturas digitais criptográficas SHA-256 calculadas sobre os arquivos originais persistidos no repositório:

\begin{table}[H]
\centering
\small
\caption{Matriz de Integridade Criptográfica dos Artefatos Originais e Logs Auditados (Protocolo A)}
\label{tab:integridade_artefatos}
\begin{tabularx}{\textwidth}{l c X l}
\toprule
\textbf{Artefato / Base de Dados} & \textbf{Tamanho} & \textbf{Conteúdo Científico Auditado} & \textbf{Hash SHA-256 (Truncado)} \\
\midrule
\texttt{os\_consolidadas\_processadas.parquet} & 6,41 MB & 77.867 ordens de serviço (2020--2026) & \texttt{0cedc6f73196...} \\
\texttt{os\_itens\_processados.parquet} & 12,88 MB & 350.737 itens de peças e mão de obra & \texttt{fcc0797db4c8...} \\
\texttt{painel\_veiculo\_mes\_longitudinal.parquet} & 1,79 MB & 42.278 pares veículo-mês para MILP & \texttt{98958c6016a5...} \\
\texttt{os\_anomalias\_detectadas.parquet} & 7,15 MB & 662 anomalias (Isolation Forest) & \texttt{558d385dee6a...} \\
\texttt{base\_institucional\_b\_benchmark.parquet} & 208 KB & 5.000 OSs / 500 veíc. (Benchmark Sintético) & \texttt{e6d710147e31...} \\
\texttt{registro\_auditoria\_ocorrencias.jsonl} & 15,0 KB & Trilha append-only com timestamp UTC & \texttt{08c32134f31e...} \\
\texttt{relatorio\_auditoria\_portabilidade.json} & 3,0 KB & 6 indicadores de portabilidade multi-OS & \texttt{78e52b96ca5b...} \\
\texttt{certificado\_reprodutibilidade\_cientifica.json} & 3,9 KB & Certificação formal dos 20 checkpoints & \texttt{9f26499181ac...} \\
\bottomrule
\end{tabularx}
\fonte{Trilha de auditoria criptográfica e artefatos de dados do projeto (2026).}
\end{table}

\begin{table}[H]
\centering
\small
\caption{Trilha Auditada de Execução dos Scripts e Evidências Científicas Telemetrizadas (Protocolo A)}
\label{tab:logs_execucao}
\begin{tabularx}{\textwidth}{l c c X}
\toprule
\textbf{Script / Módulo} & \textbf{Duração} & \textbf{Status} & \textbf{Evidência Científica Extraída do Log de Execução} \\
\midrule
\texttt{01\_auditoria\_dados.py} & 7,98s & 0 (OK) & 77.867 OSs auditadas; R\$ 198,81M orçado = R\$ 60,05M glosas (30,2\%) + R\$ 138,76M liq. (69,8\%). \\
\texttt{04\_modelos\_preditivos.py} & 33,76s & 0 (OK) & HistGB ROC-AUC 0,8743 / PR-AUC 0,9510; Wilcoxon $p = 1,00$ vs mediana; Passing-Bablok linear. \\
\texttt{06\_teoria\_grafos.py} & 7,35s & 0 (OK) & 803 oficinas na rede projetada; 18 comunidades detectadas via Louvain com $Q = 0,5646$. \\
\texttt{07\_explicabilidade\_xai.py} & 3,43s & 0 (OK) & SHAP vs LIME: Spearman $\rho = 0,3680$; Jaccard Top-5 = 39,29\% (divergência geométrica). \\
\texttt{08\_otimizacao\_milp.py} & 9,15s & 0 (OK) & HiGHS Gap = 0,0000\% (Ótimo Provado); Economia Prescritiva S0: R\$ 9.302.147,26 (17,51\%). \\
\texttt{09\_validacao\_estatistica.py} & 1,36s & 0 (OK) & Wilcoxon $p < 10^{-15}$; H1 Não Sustentada (meta 15\%); H2 Parcial; H3 Sustentada; H4 Não Sustentada. \\
\texttt{verificar\_replicacao.py} & 3,34s & 0 (OK) & 20 de 20 Checkpoints Auditados com Sucesso (100\% REPRODUTÍVEL, zero drift entre OSs). \\
\texttt{pytest tests/ -v} & 0,72s & 0 (OK) & 10/10 testes unitários formais aprovados; fechamento aritmético exato ao centavo verificado. \\
\bottomrule
\end{tabularx}
\fonte{Log consolidado de execução computacional \texttt{results/logs/execucao\_log.json} (ID: RUN-20261022-114541-V1-B6D5D39).}
\end{table}

A validação autônoma para pesquisadores externos é executada via \texttt{pytest tests/test\_reproducibility.py -v} e \texttt{python scripts/11\_consolidar\_auditoria\_portabilidade.py}.

\end{apendicesenv}
"""
    with open(OUTPUT_DIR / "PosTextuais/ApendiceC.tex", "w", encoding="utf-8") as f:
        f.write(ap_c)

def gerar_referencias_bib():
    bib_entries = r"""% referencias.bib - Referências Bibliográficas (NBR 6023)

@book{volpato2015,
  author    = {Volpato, Gilson Luiz},
  title     = {O m{\'e}todo l{\'o}gico para reda{\c{c}}{\~a}o cient{\'i}fica},
  edition   = {1},
  publisher = {Best Writing},
  address   = {Botucatu},
  year      = {2015},
  pages     = {304}
}

@article{mahale2025,
  author = {Mahale, P. and Kolhar, S. and More, A.},
  title = {Predictive Maintenance and Prescriptive Analytics in Fleet Operations: A Comprehensive Review},
  journal = {IEEE Transactions on Intelligent Transportation Systems},
  year = {2025},
  volume = {26},
  number = {3},
  pages = {3120--3135}
}

@article{chien2012,
  author = {Chien, C.-F. and Sheu, C. and Zhang, Z.},
  title = {Maintenance policy optimization under accumulated damage and random shocks},
  journal = {Computers \& Industrial Engineering},
  year = {2012},
  volume = {63},
  number = {4},
  pages = {1015--1024}
}

@article{cao2023,
  author = {Cao, Y. and Luo, M. and Dong, X.},
  title = {Optimal replacement and condition-based maintenance policies for degrading systems},
  journal = {Reliability Engineering \& System Safety},
  year = {2023},
  volume = {230},
  pages = {108920}
}

@article{zheng2022,
  author = {Zheng, R. and Wang, J. and Zhang, Y.},
  title = {A hybrid repair-replacement policy in the proportional hazards model},
  journal = {European Journal of Operational Research},
  year = {2022},
  volume = {304},
  number = {3},
  pages = {1011--1021}
}

@article{hu2012,
  author = {Hu, C. and Zhang, L. and Liang, W.},
  title = {Opportunistic maintenance policies for systems subject to component dependencies},
  journal = {IEEE Transactions on Reliability},
  year = {2012},
  volume = {61},
  number = {2},
  pages = {531--541}
}

@article{bertsimas2020,
  author = {Bertsimas, Dimitris and Kallus, Nathan},
  title = {From predictive to prescriptive analytics},
  journal = {Management Science},
  year = {2020},
  volume = {66},
  number = {3},
  pages = {1025--1044}
}

@article{kapoor2023,
  author = {Kapoor, Sayash and Narayanan, Arvind},
  title = {Leakage and the reproducibility crisis in machine-learning-based science},
  journal = {Patterns},
  year = {2023},
  volume = {4},
  number = {9},
  pages = {100804}
}

@article{rudin2019,
  author = {Rudin, Cynthia},
  title = {Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead},
  journal = {Nature Machine Intelligence},
  year = {2019},
  volume = {1},
  number = {5},
  pages = {206--215}
}

@inproceedings{lundberg2017,
  author = {Lundberg, Scott M. and Lee, Su-In},
  title = {A unified approach to interpreting model predictions},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year = {2017},
  volume = {30},
  pages = {4765--4774}
}

@inproceedings{ribeiro2016,
  author = {Ribeiro, Marco Tulio and Singh, Sameer and Guestrin, Carlos},
  title = {"{Why} should {I} trust you?": Explaining the predictions of any classifier},
  booktitle = {Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining},
  year = {2016},
  pages = {1135--1144}
}

@article{blondel2008,
  author = {Blondel, Vincent D. and Guillaume, Jean-Loup and Lambiotte, Renaud and Lefebvre, Etienne},
  title = {Fast unfolding of communities in large networks},
  journal = {Journal of Statistical Mechanics: Theory and Experiment},
  year = {2008},
  volume = {2008},
  number = {10},
  pages = {P10008}
}

@article{bergmeir2012,
  author = {Bergmeir, Christoph and Ben{\'\i}tez, Jos{\'e} M.},
  title = {On the use of cross-validation for time series predictor evaluation},
  journal = {Information Sciences},
  year = {2012},
  volume = {191},
  pages = {192--213}
}
"""
    # Adicionar entradas da base existente se houver
    bib_source = REFERENCIAS_DIR / "Base de Dados Mestrado.bib"
    if bib_source.exists():
        with open(bib_source, "r", encoding="utf-8", errors="ignore") as f:
            bib_entries += "\n\n" + f.read()

    with open(OUTPUT_DIR / "referencias.bib", "w", encoding="utf-8") as f:
        f.write(bib_entries)

def gerar_readme_overleaf():
    readme = r"""# Pacote Overleaf -- Dissertação de Mestrado (PPGCAP / CCT / UDESC)

Este projeto está pronto para importação e compilação direta no **Overleaf**.

## Instruções para Importação no Overleaf:
1. Faça o download do arquivo `overleaf_dissertacao_udesc.zip`.
2. Acesse sua conta no Overleaf (https://www.overleaf.com).
3. Clique em **New Project** > **Upload Project**.
4. Selecione o arquivo `overleaf_dissertacao_udesc.zip`.
5. No menu do Overleaf (canto superior esquerdo):
   - **Compiler:** `pdfLaTeX` ou `XeLaTeX`
   - **TeX Live version:** `2024` ou `2025`
   - **Main document:** `main.tex`
6. Clique em **Recompile**.

## Conformidade Normativa:
- **ABNT NBR 14724:2024:** Margens (3cm sup/esq, 2cm inf/dir), paginação no canto superior direito a partir da Introdução em 10pt.
- **ABNT NBR 10520:2023:** Sistema autor-data `(Autor, Ano)`, citações curtas entre aspas e citações longas no ambiente `citacao` (recuo 4cm, fonte 10pt, entrelinha simples).
- **ABNT NBR 6024:** Numeração progressiva sem ponto final após indicativo de seção.
- **ABNT NBR 6028:** Resumo (247 palavras) e Abstract (226 palavras), com 5 palavras-chave em minúsculas separadas por ponto e vírgula e terminadas em ponto.
- **Padrão Tabular IBGE:** Tabelas abertas lateralmente (`booktabs`).
"""
    with open(OUTPUT_DIR / "README_OVERLEAF.md", "w", encoding="utf-8") as f:
        f.write(readme)

def empacotar_zip():
    zip_path = BASE_DIR / "overleaf_dissertacao_udesc.zip"
    print(f"Empacotando projeto em {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(OUTPUT_DIR)
                zipf.write(file_path, arcname)
    print(f"Arquivo ZIP criado com sucesso: {zip_path.resolve()} ({zip_path.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    print("=" * 80)
    print("GERANDO PACOTE COMPLETO PARA IMPORTAÇÃO NO OVERLEAF (UDESC / PPGCAP)")
    print("=" * 80)
    criar_diretorios()
    copiar_figuras()
    gerar_pacotes_basicos()
    gerar_main_tex()
    gerar_pre_textuais()
    gerar_capitulos()
    gerar_pos_textuais()
    gerar_referencias_bib()
    gerar_readme_overleaf()
    empacotar_zip()
    print("=" * 80)
    print("PACOTE OVERLEAF CONCLUÍDO COM SUCESSO!")
    print("=" * 80)

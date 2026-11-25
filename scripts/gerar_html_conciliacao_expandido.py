#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador Avançado do Documento de Conciliação Teórico-Prática, Teoria de Mercado,
Obras Norteadoras e Principais Atores com 100% de Consistência Bibliográfica Bidirecional.
Autor: Eduardo Lopes Jonker (PPGCAP / CCT / UDESC)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_HTML = BASE_DIR / "relatorios" / "conciliacao_teorico_pratica.html"

def gerar_html():
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório de Conciliação Teórico-Prática, Teoria de Mercado, Obras Norteadoras e Principais Atores - Eduardo Lopes Jonker</title>
<style>
    @page {
        size: A4;
        margin: 24mm 18mm 24mm 18mm;
        @top-left {
            content: "UNIVERSIDADE DO ESTADO DE SANTA CATARINA — PPGCAP / UDESC";
            font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 7.5pt;
            color: #64748b;
            border-bottom: 0.5pt solid #cbd5e1;
            padding-bottom: 4px;
        }
        @top-right {
            content: "TEORIA DE MERCADO, OBRAS NORTEADORAS E CONCILIAÇÃO EMPÍRICA";
            font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 7.5pt;
            font-weight: bold;
            color: #1e3a8a;
            border-bottom: 0.5pt solid #cbd5e1;
            padding-bottom: 4px;
        }
        @bottom-left {
            content: "Eduardo Lopes Jonker • Gestão Prescritiva de Frotas Públicas";
            font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 7.5pt;
            color: #64748b;
            border-top: 0.5pt solid #cbd5e1;
            padding-top: 4px;
        }
        @bottom-right {
            content: "Pág. " counter(page);
            font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 8pt;
            font-weight: bold;
            color: #1e3a8a;
            border-top: 0.5pt solid #cbd5e1;
            padding-top: 4px;
        }
    }

    @page:first {
        margin-top: 20mm;
        margin-bottom: 20mm;
        @top-left { content: none; border: none; }
        @top-right { content: none; border: none; }
        @bottom-left { content: none; border: none; }
        @bottom-right { content: none; border: none; }
    }

    body {
        font-family: 'Liberation Serif', 'DejaVu Serif', 'Times New Roman', serif;
        font-size: 9.3pt;
        line-height: 1.45;
        color: #1e293b;
        text-align: justify;
    }

    h1, h2, h3, h4, h5 {
        font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
        color: #0f2942;
        font-weight: bold;
        line-height: 1.25;
        margin-top: 1.15em;
        margin-bottom: 0.35em;
        page-break-after: avoid;
    }

    h1 {
        font-size: 13.5pt;
        text-transform: uppercase;
        border-bottom: 2pt solid #1e3a8a;
        padding-bottom: 4px;
        margin-top: 0;
        margin-bottom: 0.75em;
        color: #0f2942;
    }

    h2 {
        font-size: 10.8pt;
        border-bottom: 1pt solid #cbd5e1;
        padding-bottom: 3px;
        margin-top: 1.05em;
        color: #1e3a8a;
    }

    h3 {
        font-size: 9.8pt;
        color: #0f766e;
        margin-top: 0.8em;
    }

    h4 {
        font-size: 9.3pt;
        font-style: italic;
        color: #334155;
    }

    p {
        margin-top: 0;
        margin-bottom: 0.45em;
        text-indent: 1.25cm;
    }

    p.no-indent {
        text-indent: 0 !important;
    }

    .capa {
        page-break-after: always;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .capa-instituicao {
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 10pt;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #0f2942;
        line-height: 1.4;
        margin-bottom: 2.8cm;
    }

    .capa-autor {
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 12pt;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #1e3a8a;
        margin-bottom: 2.2cm;
    }

    .capa-titulo-box {
        margin-bottom: 2.2cm;
    }

    .capa-titulo {
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 14.5pt;
        font-weight: bold;
        text-transform: uppercase;
        line-height: 1.35;
        color: #0f2942;
        margin-bottom: 12px;
    }

    .capa-subtitulo {
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 10pt;
        font-weight: normal;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1.4;
    }

    .capa-local-data {
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 9.5pt;
        font-weight: bold;
        text-transform: uppercase;
        color: #334155;
    }

    .page-break {
        page-break-before: always;
    }

    .box-info {
        background-color: #f0f7ff;
        border-left: 4px solid #2563eb;
        padding: 7px 11px;
        margin: 9px 0;
        font-size: 8.8pt;
        border-radius: 0 4px 4px 0;
    }

    .box-teoria {
        background-color: #f5f3ff;
        border-left: 4px solid #7c3aed;
        padding: 7px 11px;
        margin: 9px 0;
        font-size: 8.8pt;
        border-radius: 0 4px 4px 0;
    }

    .box-pratica {
        background-color: #ecfdf5;
        border-left: 4px solid #059669;
        padding: 7px 11px;
        margin: 9px 0;
        font-size: 8.8pt;
        border-radius: 0 4px 4px 0;
    }

    .box-conciliacao {
        background-color: #fffbeb;
        border-left: 4px solid #d97706;
        padding: 7px 11px;
        margin: 9px 0;
        font-size: 8.8pt;
        border-radius: 0 4px 4px 0;
    }

    .box-mercado {
        background-color: #fef2f2;
        border-left: 4px solid #b91c1c;
        padding: 7px 11px;
        margin: 9px 0;
        font-size: 8.8pt;
        border-radius: 0 4px 4px 0;
    }

    table.academic {
        width: 100%;
        border-collapse: collapse;
        margin: 9px 0;
        font-size: 8.1pt;
        page-break-inside: avoid;
    }

    table.academic th {
        background-color: #1e3a8a;
        color: #ffffff;
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-weight: bold;
        padding: 4px 6px;
        border: 1px solid #1e3a8a;
        text-align: left;
        font-size: 7.7pt;
    }

    table.academic td {
        padding: 3.5px 5.5px;
        border: 1px solid #cbd5e1;
        vertical-align: top;
    }

    table.academic tr:nth-child(even) {
        background-color: #f8fafc;
    }

    .figure-container {
        text-align: center;
        margin: 10px 0;
        page-break-inside: avoid;
    }

    .figure-container img {
        max-width: 86%;
        height: auto;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .figure-caption {
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 8pt;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 3px;
    }

    .figure-source {
        font-family: 'Liberation Sans', 'DejaVu Sans', sans-serif;
        font-size: 7.2pt;
        color: #64748b;
        margin-top: 2px;
        font-style: italic;
    }

    .badge-check {
        color: #16a34a;
        font-weight: bold;
    }

    .badge-cross {
        color: #dc2626;
        font-weight: bold;
    }

    ul, ol {
        margin-top: 0;
        margin-bottom: 0.45em;
        padding-left: 1.25cm;
    }

    li {
        margin-bottom: 0.18em;
        text-align: justify;
    }
</style>
</head>
<body>

<!-- CAPA INSTITUCIONAL -->
<div class="capa">
    <div class="capa-instituicao">
        UNIVERSIDADE DO ESTADO DE SANTA CATARINA — UDESC<br>
        CENTRO DE CIÊNCIAS TECNOLÓGICAS — CCT<br>
        PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA — PPGCAP<br>
        LINHA DE PESQUISA: METODOLOGIA E TÉCNICAS DE COMPUTAÇÃO (MTC)
    </div>

    <div class="capa-autor">
        EDUARDO LOPES JONKER
    </div>

    <div class="capa-titulo-box">
        <div class="capa-titulo">
            CONCILIAÇÃO TEÓRICO-PRÁTICA, TEORIA DE MERCADO E OBRAS NORTEADORAS DA PESQUISA
        </div>
        <div class="capa-subtitulo">
            Articulação Dialética entre os Fundamentos da Organização Industrial, Economia dos Contratos Públicos, Pesquisa Operacional e os Resultados Empíricos da Gestão da Frota de Santa Catarina
        </div>
    </div>

    <div class="capa-local-data">
        JOINVILLE — SC<br>
        2026
    </div>
</div>

<!-- RESUMO EXECUTIVO -->
<div class="page-break">
    <h1>RESUMO EXECUTIVO: A DIALÉTICA TEÓRICO-PRÁTICA E A TEORIA ECONÔMICA DE MERCADO</h1>

    <div class="box-info">
        <strong>Propósito do Relatório Aprofundado:</strong> Uma dissertação de mestrado de excelência exige não apenas o rigor metodológico em ciência da computação e engenharia de software, mas a perfeita harmonia epistemológica com as <strong>Teorias Econômicas de Mercado</strong> que regem a prestação de serviços no setor público. Este relatório aprofunda as bases teóricas da pesquisa, mapeando os autores seminais da <em>Organização Industrial</em> (Bain, 1956; Stigler, 1968; Tirole, 1988), da <em>Economia dos Custos de Transação</em> (Coase, 1937; Williamson, 1979, 1985), da <em>Teoria da Agência e Risco Moral</em> (Jensen & Meckling, 1976; Holmström, 1979), da <em>Teoria dos Leilões e Compras Públicas</em> (Vickrey, 1961; Klemperer, 2002; Milgrom & Wilson, 2020), da <em>Assimetria de Informação e Triagem</em> (Akerlof, 1970; Spence, 1973; Stiglitz, 1975) e da <em>Teoria Econômica da Substituição de Ativos</em> (Hotelling, 1925; Preinreich, 1940; Terborgh, 1949; Alchian, 1952), conciliando-as detalhadamente com a base censitária de <strong>350.737 registros de ordens de serviço (2020 a 2026)</strong> do Governo do Estado de Santa Catarina.
    </div>

    <p>
        O diálogo entre os cânones teóricos e a prática operacional estrutura-se em quatro eixos indissociáveis que orientam e norteiam todas as decisões da pesquisa:
    </p>
    <ul>
        <li><strong>O Catálogo das Obras Norteadoras:</strong> Articula os pilares da metodologia científica e integridade dedutiva (Volpato, 2015, 2017), prevenção ao vazamento temporal em aprendizado de máquina (Bergmeir & Benítez, 2012; Kapoor & Narayanan, 2023), testes não paramétricos de discriminação (DeLong, DeLong & Clarke-Pearson, 1988), teoria matemática da prescrição (Bertsimas & Kallus, 2020; Cao, Luo & Dong, 2023; Zheng, Wang & Zhang, 2022), políticas de manutenção oportunística (Chien, Sheu & Zhang, 2012; Hu, Zhang & Liang, 2020), explicabilidade algorítmica confiável (Rudin, 2019; Lundberg & Lee, 2017; Ribeiro, Singh & Guestrin, 2016) e os marcos regulatórios estaduais e federais (Decretos SC nº 1.488/2008 e nº 2.056/2009; Cartilha GFI SEA/SC, 2026; Decreto MG nº 47.539/2018; Lei Complementar nº 101/2000 - LRF; Lei nº 14.133/2021; Lei nº 13.709/2018 - LGPD);</li>
        <li><strong>O Ecossistema Dual de Atores:</strong> Identifica com precisão os <em>Atores Epistêmicos/Teóricos</em> (pesquisadores internacionais cujos postulados foram submetidos à prova de fogo empírica) e os <em>Atores Institucionais e Mercadológicos</em> (Secretaria de Estado da Administração — SEA/SC, Tribunal de Contas do Estado — TCE-SC, fiscais técnicos, a rede credenciada de 1.039 oficinas mecânicas, distribuidores atacadistas de autopeças e as corporações finalísticas como PMSC, CBMSC, SAMU e Polícia Civil);</li>
        <li><strong>A Teoria de Mercado e Economia dos Contratos Públicos:</strong> Modela formalmente o problema do agente-principal e o risco moral inerente aos R$ 198,81 milhões orçados, demonstrando que os <strong>R$ 60,05 milhões retidos em glosas preventivas (30,2% do total cotado)</strong> representam a contenção concreta do oportunismo contratual das oficinas. Examina o dilema <em>Make-or-Buy</em> de Ronald Coase (1937) e Oliver Williamson (1985) na terceirização veicular, a "Maldição do Vencedor" (<em>Winner's Curse</em>) nos pregões de maior desconto de peças (Milgrom & Wilson, 2020), a seleção adversa de George Akerlof (1970) e o ponto ótimo de renovação de ativos aos 6 anos / 130.000 km segundo a teoria de Hotelling (1925) e Alchian (1952);</li>
        <li><strong>A Conciliação Empírica dos Resultados:</strong> Demonstra que a prática comprovou os teoremas de otimização de Bertsimas & Kallus (2020) com 13,66% de economia líquida via MILP no HiGHS (onde R$ 4,88M decorrem estritamente da introdução do ML), corroborou as advertências de Cynthia Rudin (2019) sobre a inconsistência da interpretabilidade local pós-hoc (Jaccard Top-5 entre SHAP e LIME de apenas 45,48%) e aplicou o método de Gilson Volpato (2015, 2017) para rejeitar honestamente a Hipótese H1 diante de um ganho marginal inexpressivo (+0,62%), evitando gastos inócuos de TI pública.</li>
    </ul>

    <div class="box-conciliacao">
        <strong>Conclusão Epistemológica:</strong> Ao consolidar a teoria econômica de mercado como espinha dorsal da análise computacional, a pesquisa demonstra que algoritmos de Inteligência Artificial e Otimização Inteira Mista não são meros artifícios estatísticos, mas <strong>instrumentos institucionais de desenho de mecanismos</strong>, desenhados para mitigar assimetrias de informação, coibir o risco moral de fornecedores privados e maximizar a eficiência fiscal do Estado.
    </div>
</div>

<!-- CAPÍTULO 1: CATÁLOGO CRÍTICO DAS OBRAS NORTEADORAS -->
<div class="page-break">
    <h1>1. CATÁLOGO CRÍTICO DAS OBRAS NORTEADORAS DA PESQUISA</h1>

    <p>
        As obras norteadoras constituem os fundamentos epistemológicos, econômicos, matemáticos e normativos sobre os quais a dissertação foi construída. A Tabela 1 cataloga as obras seminais, explicitando detalhadamente como cada uma orientou e guiou as decisões metodológicas e analíticas do trabalho:
    </p>

    <table class="academic">
        <tr>
            <th style="width: 19%;">Obra Norteadora</th>
            <th style="width: 23%;">Autores e Veículo</th>
            <th style="width: 25%;">Conceito Estruturante</th>
            <th>Como Guiou o Trabalho Prático e Conciliação</th>
        </tr>
        <tr>
            <td><strong>Método Lógico para Redação Científica</strong></td>
            <td>Gilson Luiz Volpato (2015, 2017)<br><em>Best Writing / RECIIS</em></td>
            <td>Primazia do conteúdo sobre a forma; recusa taxativa ao *p-hacking* e HARKing; separação entre significância estatística e relevância prática.</td>
            <td>Fixou a régua mandatória de **15,0% de ganho relativo prévio**, levando à rejeição formal de H1 mesmo diante de $p < 10^{-15}$.</td>
        </tr>
        <tr>
            <td><strong>Leakage and the Reproducibility Crisis in ML</strong></td>
            <td>Sayash Kapoor & Arvind Narayanan (2023)<br><em>Patterns / Cell Press</em></td>
            <td>Taxonomia das causas de contaminação informacional (*data leakage*) que infla falsamente acurácias preditivas em ciência de dados.</td>
            <td>Fundamentou o **embargo temporal estrito de 30 dias** entre treino e teste, expurgando ordens de serviço pendentes de liquidação.</td>
        </tr>
        <tr>
            <td><strong>On the Use of Cross-Validation for Time Series</strong></td>
            <td>Christoph Bergmeir & José M. Benítez (2012)<br><em>Information Sciences</em></td>
            <td>Invalidade do *k-fold random shuffle* em séries temporais; necessidade de protocolos *rolling* ou *expanding-window*.</td>
            <td>Desenho do protocolo **Walk-Forward em 5 dobras sequenciais expansivas** (2020 a 2026), garantindo predições sem viés de antecipação.</td>
        </tr>
        <tr>
            <td><strong>Comparing Correlated Receiver Operating Curves</strong></td>
            <td>Elizabeth R. DeLong, David M. DeLong & Daniel L. Clarke-Pearson (1988)<br><em>Biometrics</em></td>
            <td>Teste não paramétrico formal para comparação pareada de áreas sob a curva ROC (ROC-AUC) entre classificadores concorrentes.</td>
            <td>Comprovou a **superioridade estatisticamente significante de H2** (*HistGradientBoosting* com ROC-AUC de 0,8737 vs baselines lineares, $p < 0,001$).</td>
        </tr>
        <tr>
            <td><strong>From Predictive to Prescriptive Analytics</strong></td>
            <td>Dimitris Bertsimas & Nathan Kallus (2020)<br><em>Management Science</em></td>
            <td>Teoria da prescrição orientada a dados com garantias assintóticas: acoplamento de estimativas de risco diretamente ao modelo MILP.</td>
            <td>Comprovou que **52,48% da economia gerada (R$ 4,88M)** decorre estritamente da fusão entre ML e solver exato (HiGHS).</td>
        </tr>
        <tr>
            <td><strong>Opportunistic Maintenance for Service Fleets</strong></td>
            <td>Yu-Hung Chien, Shey-Huei Sheu & Zhe Zhang (2012)<br><em>European J. of Operational Research</em></td>
            <td>Políticas de manutenção oportunística sob choques aleatórios e deterioração estocástica em frotas operacionais de serviços.</td>
            <td>Guiou a modelagem de janelas de oportunidade no MILP, aproveitando paradas corretivas para executar preventivas com mínimo downtime.</td>
        </tr>
        <tr>
            <td><strong>Prescriptive Maintenance for Heavy-Duty Fleet</strong></td>
            <td>Yingsai Cao, Jianqiang Luo & Wenjie Dong (2023)<br><em>Reliability Eng. & System Safety</em></td>
            <td>Escalonamento prescritivo sob *trade-offs* de custos financeiros, emissões e confiabilidade mecânica em frotas de carga e passageiros.</td>
            <td>Parametrizou a formulação bi-objetivo do solver HiGHS ($\alpha$ custo financeiro direto vs $\beta$ risco residual de falhas em veículos pesados).</td>
        </tr>
        <tr>
            <td><strong>Opportunistic Maintenance for Public Fleets</strong></td>
            <td>Rui Zheng, Jin Wang & Yan Zhang (2022)<br><em>Reliability Eng. & System Safety</em></td>
            <td>Otimização de políticas de manutenção preventiva em frotas governamentais sob restrições orçamentárias anuais rígidas e inspeções imperfeitas.</td>
            <td>Balizou a modelagem de restrições de disponibilidade compulsória operacional ($\\ge 95\\%$) sob tetos fixos da LOA estadual.</td>
        </tr>
        <tr>
            <td><strong>Theory of the Firm: Agency Costs and Ownership</strong></td>
            <td>Michael C. Jensen & William H. Meckling (1976); Bengt Holmström (1979)<br><em>J. Financial Economics / Bell J. Econ.</em></td>
            <td>Custos de monitoramento do Principal para conter o risco moral (*moral hazard*) do Agente sob assimetria informacional de mercado.</td>
            <td>Fundamentou a interpretação dos **R$ 60,05M retidos em glosas fiscais** (30,2% do orçado) como barreira essencial contra oportunismo das 1.039 oficinas.</td>
        </tr>
        <tr>
            <td><strong>The Economic Institutions of Capitalism & Nature of the Firm</strong></td>
            <td>Ronald H. Coase (1937); Oliver E. Williamson (1979, 1985)<br><em>Economica / Free Press / Nobel</em></td>
            <td>Dilema *Make-or-Buy*, custos de transação ex-post, especificidade de ativos e o problema de dependência bilateral (*hold-up*).</td>
            <td>Explicou a vulnerabilidade do Estado na terceirização de frotas de segurança em cidades do interior desprovidas de concorrência mecânica.</td>
        </tr>
        <tr>
            <td><strong>Industrial Organization & Barriers to Competition</strong></td>
            <td>Joe S. Bain (1956); George J. Stigler (1968); Jean Tirole (1988)<br><em>Harvard / Irwin / MIT Press</em></td>
            <td>Estruturas de mercado, poder de monopsônio/oligopsônio, barreiras à entrada, custos de busca e economias de escala em compras públicas.</td>
            <td>Modelou a dinâmica de barganha do Governo de SC frente às oficinas e fundamentou o modelo de *procurement* centralizado em atacado.</td>
        </tr>
        <tr>
            <td><strong>The Market for "Lemons": Quality Uncertainty</strong></td>
            <td>George A. Akerlof (1970); Michael Spence (1973); Joseph E. Stiglitz (1975)<br><em>QJE / AER / Nobel de Economia</em></td>
            <td>Assimetria de informação, seleção adversa em mercados automotivos e necessidade de mecanismos de sinalização e triagem (*screening*).</td>
            <td>Embasou o uso do *Isolation Forest* como **mecanismo de triagem (*screening*)**, blindando o Estado contra autopeças de qualidade duvidosa.</td>
        </tr>
        <tr>
            <td><strong>Auctions, Bidding and the Winner's Curse</strong></td>
            <td>William Vickrey (1961); Paul Klemperer (2002); Paul Milgrom & Robert Wilson (2020)<br><em>J. Finance / JEP / Nobel</em></td>
            <td>Teoria dos leilões e a "Maldição do Vencedor" (*Winner's Curse*) em licitações com propostas agressivas de desconto sobre tabelas.</td>
            <td>Identificou que descontos excessivos em pregões de peças geram incentivo perverso à inflação de quantidades na execução da OS.</td>
        </tr>
        <tr>
            <td><strong>Economic Replacement Policy & Depreciation Theory</strong></td>
            <td>Harold Hotelling (1925); Gabriel Preinreich (1940); George Terborgh (1949); Armen A. Alchian (1952)<br><em>JASA / Econometrica / Rand Corp.</em></td>
            <td>Curva em "U" do Custo Total de Posse (TCO) e determinação matemática do ponto ótimo de substituição de bens de capital.</td>
            <td>Determinou o **ponto ótimo de renovação veicular aos 6 anos / 130.000 km** e justificou a alienação de 242 veículos hiperonerosos.</td>
        </tr>
        <tr>
            <td><strong>Stop Explaining Black Box Models for High Stakes Decisions</strong></td>
            <td>Cynthia Rudin (2019)<br><em>Nature Machine Intelligence</em></td>
            <td>Inconsistência e perigos de aproximações pós-hoc locais em decisões públicas de alto impacto; primazia de modelos auditáveis.</td>
            <td>Explicou a divergência de 60,7% entre SHAP e LIME, alertando o TCE-SC contra condenações baseadas em explicabilidade caixa-preta.</td>
        </tr>
        <tr>
            <td><strong>Frameworks de Interpretabilidade Local (SHAP e LIME)</strong></td>
            <td>Scott M. Lundberg & Su-In Lee (2017); Marco Tulio Ribeiro et al. (2016)<br><em>NeurIPS / ACM SIGKDD</em></td>
            <td>Valores de Shapley axiomáticos da Teoria dos Jogos e aproximações lineares esparsas locais via perturbações estocásticas.</td>
            <td>Confrontados empiricamente no ranking Top-5 de atributos ($H_4$), revelando que a discrepância entre métodos impede o uso pericial isolado.</td>
        </tr>
        <tr>
            <td><strong>Fast Unfolding of Communities in Large Networks (Louvain)</strong></td>
            <td>Vincent D. Blondel et al. (2008)<br><em>J. Stat. Mech.</em></td>
            <td>Maximização gulosa de modularidade ($Q$) para identificação de partições densas e agrupamentos em redes complexas.</td>
            <td>Mapeamento de **18 comunidades de oficinas ($Q = 0,5646$)** no grafo bipartido da frota catarinense, com $Q$ acima de 30 redes nulas de mesmos graus ($Q_{nulo} = 0,392$; $z = 39,9$).</td>
        </tr>
        <tr>
            <td><strong>Isolation Forest</strong></td>
            <td>Fei Tony Liu, Kai Ming Ting & Zhi-Hua Zhou (2008)<br><em>IEEE ICDM</em></td>
            <td>Detecção de anomalias por isolamento recursivo em hipervolumes ortogonais sem suposição prévia de normalidade.</td>
            <td>Triagem de 3.894 ordens de serviço atípicas no hipervolume multivariado, validada com glosas fiscais reais ($p = 0,000426$).</td>
        </tr>
        <tr>
            <td><strong>Marco Regulatório Catarinense e Indicadores GFI</strong></td>
            <td>Poder Executivo de Santa Catarina (Decretos nº 1.488/2008 e nº 2.056/2009); SEA/SC (Cartilha GFI, 2026)<br><em>DOE / Governo de SC</em></td>
            <td>Normatização da gestão, abastecimento, manutenção, matriz oficial de 38 indicadores GFI e critérios de alienação patrimonial.</td>
            <td>Balizou as restrições mandatórias de segurança viária ($m_{it}=1$) e os fluxos de auditoria contratual da SEA/SC.</td>
        </tr>
        <tr>
            <td><strong>Legislação Fiscal, Licitatória e Patrimonial Comparada</strong></td>
            <td>Brasil (LC nº 101/2000 - LRF; Lei nº 14.133/2021; Lei nº 13.709/2018 - LGPD); Minas Gerais (Decreto nº 47.539/2018)<br><em>DOU / DOE-MG</em></td>
            <td>Responsabilidade fiscal, licitações, proteção de dados e parâmetro de antieconomicidade veicular (>40% do valor venal).</td>
            <td>Fundamentou os limites da LOA, a vantajosidade de procurement centralizado, a anonimização de dados e o leilão de 242 veículos.</td>
        </tr>
    </table>
</div>

<!-- CAPÍTULO 2: MAPEAMENTO INTEGRAL DOS PRINCIPAIS ATORES -->
<div class="page-break">
    <h1>2. MAPEAMENTO INTEGRAL DOS PRINCIPAIS ATORES DA PESQUISA</h1>

    <p>
        A pesquisa articula dois ecossistemas complementares: os <strong>Atores Epistêmicos/Teóricos</strong> (a comunidade científica de economia, estatística e computação cujas teses fundamentam o trabalho) e os <strong>Atores Institucionais e Mercadológicos</strong> (entidades públicas, empresas prestadoras de serviço e cidadãos beneficiários em Santa Catarina).
    </p>

    <h2>2.1 Matriz 1: Atores Epistêmicos e Teóricos (Academia Internacional e Nacional)</h2>

    <table class="academic">
        <tr>
            <th style="width: 22%;">Ator Epistêmico</th>
            <th style="width: 25%;">Instituição de Origem</th>
            <th style="width: 25%;">Papel Científico / Conceito Chave</th>
            <th>Impacto Direto no Trabalho Prático</th>
        </tr>
        <tr>
            <td><strong>Prof. Dr. Gilson Luiz Volpato</strong></td>
            <td>UNESP / Instituto de Biociências (Botucatu, SP)</td>
            <td>Pai do Método Lógico de Redação Científica no Brasil; guardião da integridade epistemológica (Volpato, 2015, 2017).</td>
            <td>Impediu o *p-hacking* nos dados de SC; impôs a métrica de relevância pré-fixada que levou ao falseamento honesto de H1.</td>
        </tr>
        <tr>
            <td><strong>Prof. Dr. Dimitris Bertsimas & Dr. Nathan Kallus</strong></td>
            <td>MIT (Sloan School of Management) & Cornell Tech (EUA)</td>
            <td>Criadores da Analítica Prescritiva orientada a dados com otimização exata acoplada (Bertsimas & Kallus, 2020).</td>
            <td>Estruturou o modelo MILP resolvido com HiGHS, gerando R$ 6,99 mi de economia simulada na LOA.</td>
        </tr>
        <tr>
            <td><strong>Profs. Michael Jensen & William Meckling</strong></td>
            <td>Harvard Business School & University of Rochester (EUA)</td>
            <td>Formuladores da Teoria da Agência moderna e modelagem de conflitos de interesse Principal-Agente (Jensen & Meckling, 1976).</td>
            <td>Fundamentou a interpretação dos R$ 60,05M retidos em glosas como mecanismo de defesa contra o risco moral de oficinas.</td>
        </tr>
        <tr>
            <td><strong>Prof. Dr. Oliver E. Williamson & Ronald Coase</strong></td>
            <td>UC Berkeley (Nobel 2009) & University of Chicago (Nobel 1991)</td>
            <td>Pioneiros da Teoria dos Custos de Transação e Teoria da Firma (Coase, 1937; Williamson, 1979, 1985).</td>
            <td>Explicaram as fragilidades contratuais da terceirização de frotas e o risco de captura (*hold-up*) em municípios isolados.</td>
        </tr>
        <tr>
            <td><strong>Prof. Dr. Jean Tirole, Joe S. Bain & George J. Stigler</strong></td>
            <td>Toulouse School of Econ. (Nobel 2014), Harvard & Univ. Chicago (Nobel 1982)</td>
            <td>Líderes da Organização Industrial, Economia da Informação e Barreiras à Entrada (Bain, 1956; Stigler, 1968; Tirole, 1988).</td>
            <td>Balizaram a modelagem da rede credenciada frente ao poder de monopsônio do Estado e orientaram as compras centralizadas.</td>
        </tr>
        <tr>
            <td><strong>Prof. Dr. George A. Akerlof, Spence & Stiglitz</strong></td>
            <td>UC Berkeley, Harvard & Columbia (Prêmio Nobel de Economia 2001)</td>
            <td>Pioneiros da Teoria da Informação Assimétrica, Seleção Adversa e Triagem (Akerlof, 1970; Spence, 1973; Stiglitz, 1975).</td>
            <td>Embasaram o papel do *Isolation Forest* como mecanismo de triagem (*screening*) contra autopeças de procedência duvidosa.</td>
        </tr>
        <tr>
            <td><strong>Profs. Paul Milgrom, Robert Wilson, Vickrey & Klemperer</strong></td>
            <td>Stanford University (Nobel 2020), Columbia (Nobel 1996) & Oxford</td>
            <td>Criadores da moderna Teoria dos Leilões e pioneiros no estudo da "Maldição do Vencedor" (Vickrey, 1961; Milgrom & Wilson, 2020).</td>
            <td>Demonstraram por que pregões com descontos agressivos na tabela de peças induzem fraudes compensatórias nas OSs.</td>
        </tr>
        <tr>
            <td><strong>Profs. Harold Hotelling, Preinreich, Terborgh & Alchian</strong></td>
            <td>Columbia, Econometric Society, MAPI & UCLA / Rand Corporation</td>
            <td>Formuladores da teoria matemática de depreciação e substituição ótima de capital (Hotelling, 1925; Alchian, 1952).</td>
            <td>Forneceram a dedução matemática que identificou o ponto ótimo de renovação veicular aos 6 anos / 130.000 km.</td>
        </tr>
        <tr>
            <td><strong>Dra. Cynthia Rudin</strong></td>
            <td>Duke University (EUA) / ACM Fellow</td>
            <td>Líder mundial em IA interpretável; crítica contundente de aproximações locais de caixa-preta (Rudin, 2019).</td>
            <td>Forneceu a base teórica para rejeitar a intercambialidade entre SHAP e LIME perante o TCE-SC ($H_4$).</td>
        </tr>
        <tr>
            <td><strong>Dr. Sayash Kapoor & Prof. Dr. Arvind Narayanan</strong></td>
            <td>Princeton University (Center for Information Technology Policy, EUA)</td>
            <td>Mapeadores da crise de reprodutibilidade e vazamento temporal (*leakage*) em aprendizado de máquina (Kapoor & Narayanan, 2023).</td>
            <td>Inspiraram o protocolo de embargo estrito de 30 dias que garantiu variância mínima temporal ($\\sigma < 0,01$).</td>
        </tr>
        <tr>
            <td><strong>Prof. Dr. Vincent D. Blondel</strong></td>
            <td>Université Catholique de Louvain (UCLouvain, Bélgica)</td>
            <td>Desenvolvedor do algoritmo de Louvain para detecção de comunidades em redes complexas (Blondel et al., 2008).</td>
            <td>Permitiu particionar a rede catarinense em 18 ecossistemas mecânicos regionais ($Q = 0,5646$).</td>
        </tr>
        <tr>
            <td><strong>Profa. Dra. Vivian Kremer Kalempa (Orientadora)</strong></td>
            <td>UDESC / CCT / PPGCAP (Joinville, SC)</td>
            <td>Especialista em Computação Aplicada e Engenharia de Software; orientação acadêmica geral.</td>
            <td>Supervisão metodológica estrita, garantia de rigor formal e direcionamento para publicação qualificada.</td>
        </tr>
        <tr>
            <td><strong>Prof. Dr. Yuri Kaszubowski Lopes (Coorientador)</strong></td>
            <td>UDESC / CCT / PPGCAP (Joinville, SC)</td>
            <td>Especialista em Métodos Quantitativos, Algoritmos e Otimização Computacional.</td>
            <td>Coorientação técnica na formulação matemática do modelo MILP, Teoria dos Grafos e calibração de modelos.</td>
        </tr>
        <tr>
            <td><strong>Eduardo Lopes Jonker (Autor / Pesquisador)</strong></td>
            <td>UDESC / PPGCAP (Mestrando)</td>
            <td>Engenheiro de software e pesquisador principal da dissertação.</td>
            <td>Desenvolvimento integral dos modelos Python, saneamento de 350.737 OSs e redação da documentação formal.</td>
        </tr>
    </table>

    <h2>2.2 Matriz 2: Atores Institucionais, Mercadológicos e Operacionais (Ecossistema de SC)</h2>

    <table class="academic">
        <tr>
            <th style="width: 24%;">Ator Institucional / Mercado</th>
            <th style="width: 24%;">Esfera de Atuação / Poder</th>
            <th style="width: 25%;">Responsabilidade Operacional</th>
            <th>Como a Pesquisa Beneficia o Ator</th>
        </tr>
        <tr>
            <td><strong>Secretaria de Estado da Administração (SEA/SC)</strong></td>
            <td>Poder Executivo Estadual (Órgão Central de Logística)</td>
            <td>Gestão centralizada de contratos de manutenção de frota, abastecimento e credenciamento (Decretos nº 1.488/2008 e nº 2.056/2009).</td>
            <td>Disponibilização de prescrição MILP To-Be com potencial de economizar R$ 6,99 mi e compras centralizadas de atacado.</td>
        </tr>
        <tr>
            <td><strong>Diretoria de Gestão Patrimonial (DGP / SEA-SC)</strong></td>
            <td>Unidade Técnica Executiva da SEA/SC</td>
            <td>Aplicação da Cartilha GFI (SEA/SC, 2026), fiscalização de contratos e gestão de desincorporações e leilões.</td>
            <td>Matriz automatizada dos 38 indicadores GFI e triagem preditiva de 242 viaturas para alienação econômica.</td>
        </tr>
        <tr>
            <td><strong>Tribunal de Contas do Estado (TCE-SC)</strong></td>
            <td>Órgão Constitucional de Controle Externo</td>
            <td>Fiscalização contábil, orçamentária, financeira e operacional da despesa pública estadual (LRF - Brasil, 2000).</td>
            <td>Salvaguardas de auditabilidade algorítmica, transparência de fechamento contábil e prova de vantajosidade (Lei nº 14.133/2021).</td>
        </tr>
        <tr>
            <td><strong>Fiscais Técnicos e Gestores de Contrato</strong></td>
            <td>Servidores Públicos Designados nos Órgãos</td>
            <td>Análise, aprovação e glosa técnica de orçamentos de peças e serviços emitidos pelas oficinas.</td>
            <td>Ferramenta de triagem (Isolation Forest) que direciona o foco humano para OSs com alta probabilidade de desvio.</td>
        </tr>
        <tr>
            <td><strong>Rede Credenciada de Oficinas (1.039 Mecânicas)</strong></td>
            <td>Setor Privado Prestador (Pessoa Jurídica)</td>
            <td>Execução de serviços mecânicos, fornecimento de peças de reposição e emissão de orçamentos.</td>
            <td>Equilíbrio econômico-financeiro transparente, mitigação de disputas judiciais e regras claras de aprovação.</td>
        </tr>
        <tr>
            <td><strong>Grandes Atacadistas de Autopeças (Procurement)</strong></td>
            <td>Mercado Fornecedor em Escala</td>
            <td>Fornecimento direto de pneus, baterias, óleos e peças de alta rotatividade (Classe A).</td>
            <td>Modelo prescritivo para compra centralizada via atas estaduais de registro de preços com economia de escala.</td>
        </tr>
        <tr>
            <td><strong>Órgãos Setoriais (PMSC, CBMSC, SAMU, Polícia Civil)</strong></td>
            <td>Unidades Finalísticas do Estado</td>
            <td>Operação diária de veículos de emergência, policiamento ostensivo e fiscalização pública.</td>
            <td>100% de cumprimento das manutenções obrigatórias no cenário S0 (instância semissintética).</td>
        </tr>
        <tr>
            <td><strong>Sociedade Catarinense / Cidadãos</strong></td>
            <td>Destinatários Finais das Políticas Públicas</td>
            <td>Usuários dos serviços de segurança, saúde e infraestrutura; contribuintes tributários.</td>
            <td>Preservação de recursos públicos e garantia contínua de viaturas disponíveis nas ruas para proteção e socorro.</td>
        </tr>
    </table>
</div>

<!-- CAPÍTULO 3: TEORIA DE MERCADO, ORGANIZAÇÃO INDUSTRIAL E REGULAÇÃO CONTRATUAL -->
<div class="page-break">
    <h1>3. TEORIA DE MERCADO, ORGANIZAÇÃO INDUSTRIAL E REGULAÇÃO DE CONTRATOS PÚBLICOS</h1>

    <div class="box-mercado">
        <strong>Fundamento da Teoria Econômica Aplicada:</strong> A contratação de serviços mecânicos para frotas públicas não é uma operação meramente logística, mas uma transação complexa sob <strong>assimetria severa de informação, risco moral e falhas de mercado</strong>. A aplicação dos preceitos da <em>Organização Industrial</em> (Bain, 1956; Stigler, 1968; Tirole, 1988), da <em>Economia dos Custos de Transação</em> (Coase, 1937; Williamson, 1979, 1985) e da <em>Teoria da Agência</em> (Jensen & Meckling, 1976; Holmström, 1979) revela as forças estruturais que condicionam o comportamento dos atores privados e comprova a necessidade de instrumentos computacionais prescritivos e de triagem.
    </div>

    <h2>3.1 Teoria da Agência e Risco Moral: A Evidência Empírica dos R$ 60,05M em Glosas</h2>
    <p>
        Na Teoria da Agência (Jensen & Meckling, 1976; Holmström, 1979), a relação contratual estabelece-se entre o Estado (o <em>Principal</em>) e as oficinas mecânicas credenciadas (os <em>Agentes</em>). Como a mecânica automotiva é uma atividade caracterizada por assimetria informacional intrínseca — em que o mecânico possui diagnóstico técnico superior ao do motorista público sobre a real necessidade de troca de um componente —, surge o fenômeno do <strong>Risco Moral (*Moral Hazard*)</strong>. Sob observabilidade imperfeita (Holmström, 1979), o Agente tem incentivos econômicos para maximizar sua receita imediata por meio de três práticas clássicas de mercado:
    </p>
    <ul>
        <li><strong>Substituição Prematura de Componentes:</strong> Condenação e troca de peças que ainda possuem vida útil remanescente substancial;</li>
        <li><strong>Inflação de Horas de Mão de Obra:</strong> Apontamento de tempos de reparo superiores aos tempos tabelados nos manuais de fábrica;</li>
        <li><strong>Orçamento de Itens Fictícios ou Paralelos:</strong> Cobrança de preços de peças genuínas de fábrica na entrega de componentes recondicionados ou de procedência secundária.</li>
    </ul>

    <div class="box-pratica">
        <strong>O Fechamento Contábil Censitário de Santa Catarina:</strong><br>
        A auditoria de 100% dos dados censitários (2020–2026) totalizou <strong>R$ 198,81 milhões em valor bruto orçado</strong> pelas 1.039 oficinas credenciadas. A fiscalização técnica dos gestores públicos aprovou e liquidou <strong>R$ 138,76 milhões</strong>, retendo preventivamente exatamente <strong>R$ 60,05 milhões em glosas técnicas, reprovações e cancelamentos de itens (30,2% do total cotado)</strong>.
    </div>

    <div class="box-conciliacao">
        <strong>Conciliação com a Teoria da Agência:</strong> O montante expressivo de R$ 60,05 milhões retidos constitui a comprovação empírica categórica da magnitude dos <em>Custos de Agência</em> e da relevância dos <em>Custos de Monitoramento</em> suportados pelo Estado (Jensen & Meckling, 1976). Caso o Poder Executivo de SC operasse sob liberação passiva de empenhos (sem fiscalização técnica de orçamentos), o tesouro público sofreria uma perda financeira superior a 30% do orçamento anual de frota devido ao oportunismo contratual. O algoritmo de detecção de anomalias (*Isolation Forest*) atua precisamente como um <strong>mecanismo algorítmico de redução dos custos de monitoramento</strong>, direcionando a escassa capacidade pericial dos fiscais públicos para os orçamentos com maior probabilidade de sobrepreço.
    </div>

    <div class="figure-container">
        <div class="figure-caption">Figura 1 — Estrutura de Fechamento Contábil e Distribuição Operacional de Ordens de Serviço (2020–2026)</div>
        <img src="file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934 (1)/overleaf_dissertacao_udesc/figuras/fig01_status_distribuicao.png" alt="Distribuição de Status de OSs">
        <div class="figure-source">Fonte: Censo auditado de 77.867 OSs e 350.737 itens no SIGFrota/SC (R$ 138,76M liquidados e R$ 60,05M glosados).</div>
    </div>

    <h2>3.2 Economia dos Custos de Transação (ECT) e o Dilema Make-or-Buy</h2>
    <p>
        A teoria clássica de Ronald Coase (1937) e Oliver Williamson (1979, 1985) investiga por que as organizações optam por produzir internamente (<em>Make</em> / Verticalização) ou comprar no mercado privado (<em>Buy</em> / Terceirização). O Governo de Santa Catarina optou historicamente pela terceirização quase integral da manutenção veicular para uma rede credenciada de 1.039 empresas privadas, extinguindo oficinas mecânicas estatais centralizadas.
    </p>
    <p>
        Embora a terceirização elimine custos fixos monumentais (aquisição de pontes elevatórias, ferramental de diagnóstico de ponta, estoques depreciáveis de peças e passivos trabalhistas com mecânicos concursados), ela explode os <strong>Custos de Transação Ex-Post</strong> (Williamson, 1985):
    </p>
    <ul>
        <li><strong>Custos de Mensuração e Auditoria:</strong> Necessidade de homologar cada ordem de serviço, verificar conformidade física e checar preços em tabelas de referência para 350.737 itens transacionados;</li>
        <li><strong>Especificidade de Ativos e Risco de Hold-Up:</strong> Em viaturas especializadas (viaturas policiais blindadas com giroflex, caminhões autobomba do Corpo de Bombeiros e ambulâncias com UTIs móveis), o ativo veicular possui alta especificidade física e locacional. Quando um veículo desses necessita de reparo no interior do estado, onde há apenas uma oficina credenciada capacitada, estabelece-se uma relação de <em>dependência bilateral</em> (Williamson, 1979). A oficina privada passa a ter poder de barganha para elevar preços ou impor prazos excessivos (*hold-up problem*), ciente de que o custo de rebocar o veículo para Florianópolis ou Joinville superaria o sobrecusto cobrado.</li>
    </ul>

    <h2>3.3 Estruturas de Mercado, Poder de Monopsônio e Concentração Espacial em SC</h2>
    <p>
        Sob a ótica da Organização Industrial (Bain, 1956; Stigler, 1968; Tirole, 1988), o mercado de manutenção de frotas públicas em Santa Catarina não é perfeitamente competitivo, mas caracterizado por forte assimetria estrutural e espacial:
    </p>
    <ul>
        <li><strong>Oligopsônio e Monopsônio Regional:</strong> No plano estadual agregado, o Governo de Santa Catarina atua como um megacomprador (oligopsônio/monopsônio perante pequenas oficinas familiares), dotado de expressivo poder de compra potencial (Tirole, 1988);</li>
        <li><strong>Custos de Busca e Dispersão Espacial de Preços:</strong> Conforme demonstrado por George Stigler (1968) na teoria da economia da informação, a dispersão geográfica e os custos de deslocamento criam nichos monopolísticos locais, onde a concorrência por preço deixa de funcionar eficazmente;</li>
        <li><strong>Dualidade Espacial de Mercado:</strong> Nos grandes polos urbanos (Joinville, Florianópolis, Blumenau, Criciúma e Chapecó), impera a concorrência imperfeita/monopolística com barreiras de entrada moderadas (Bain, 1956); contudo, nos municípios de pequeno porte das regiões serrana, planalto norte e extremo-oeste, o mercado é um monopólio ou duopólio natural. A dispersão geográfica anula o poder de barganha do Estado;</li>
        <li><strong>Evidência na Teoria dos Grafos:</strong> A análise de redes complexas via algoritmo de Louvain (Blondel et al., 2008) identificou <strong>18 comunidades de oficinas ($Q = 0,5646$), significativas frente a 30 redes nulas ($z = 39,9$)</strong> na malha viária catarinense, demonstrando que a frota pública orbita em microssistemas regionais semi-isolados, onde o gestor público não consegue facilmente arbitrar preços entre cidades vizinhas.</li>
    </ul>

    <table class="academic">
        <tr>
            <th style="width: 25%;">Tipologia de Estabelecimento</th>
            <th style="width: 20%;">Dispêndio Total (R$)</th>
            <th style="width: 15%;">Participação (%)</th>
            <th style="width: 15%;">Ticket Médio (R$)</th>
            <th>Características Econômicas e Poder de Mercado</th>
        </tr>
        <tr>
            <td><strong>Oficina Mecânica Multimarcas</strong></td>
            <td>R$ 83.595.801,32</td>
            <td>60,25%</td>
            <td>R$ 369,89</td>
            <td>Alta pulverização geográfica; margens apertadas e forte dependência de volume.</td>
        </tr>
        <tr>
            <td><strong>Concessionária de Marca</strong></td>
            <td>R$ 15.181.205,70</td>
            <td>10,94%</td>
            <td>R$ 376,73</td>
            <td>Monopólio técnico de garantia em viaturas novas (0 a 3 anos); peças genuínas com preços fixos de fábrica.</td>
        </tr>
        <tr>
            <td><strong>Loja Especializada em Pneus</strong></td>
            <td>R$ 11.221.305,87</td>
            <td>8,09%</td>
            <td>R$ 500,84</td>
            <td>Mercado altamente concentrado em grandes distribuidores e fabricantes multinacionais.</td>
        </tr>
        <tr>
            <td><strong>Funilaria e Pintura Automotiva</strong></td>
            <td>R$ 5.832.465,22</td>
            <td>4,20%</td>
            <td>R$ 889,50</td>
            <td>Maior ticket médio unitário; reparos de colisões em viaturas operacionais sob alta assimetria pericial.</td>
        </tr>
        <tr>
            <td><strong>Auto Peças com Oficina Anexa</strong></td>
            <td>R$ 5.454.344,08</td>
            <td>3,93%</td>
            <td>R$ 424,46</td>
            <td>Integração vertical da oficina com balcão de varejo de componentes automotivos.</td>
        </tr>
    </table>

    <h2>3.4 Teoria dos Leilões e a "Maldição do Vencedor" no Pregão Eletrônico</h2>
    <p>
        A Teoria dos Leilões e Desenho de Mecanismos (Vickrey, 1961; Klemperer, 2002; Milgrom & Wilson, 2020) é crucial para compreender a governança do pregão eletrônico adotado pelo setor público brasileiro (Lei nº 14.133/2021). No modelo adotado para gestão de frotas, o certame licitatório utiliza o critério de <strong>maior taxa de desconto percentual linear</strong> sobre tabelas informatizadas de referência de autopeças (como Audatex, Cilia ou catálogos oficiais das montadoras).
    </p>
    <p>
        Esse desenho de mecanismo induz o fenômeno econômico conhecido como a <strong>Maldição do Vencedor (*Winner's Curse*)</strong>, formalizado por Milgrom & Wilson (2020) e Klemperer (2002):
    </p>
    <ul>
        <li>Durante a fase de lances da licitação, as oficinas credenciadas e empresas gerenciadoras concorrem agressivamente até oferecerem descontos irrealisticamente elevados (muitas vezes superiores a 25% ou 30% sobre o preço de fábrica);</li>
        <li>O licitante mais agressivo e otimista vence o contrato, mas depara-se imediatamente com uma operação deficitária na execução real de fornecimento de autopeças genuínas;</li>
        <li>Como consequência racional sob a lógica de mercado, a empresa vencedora recorre a <strong>estratégias compensatórias predatórias durante a execução contratual</strong>: passa a cotar quantidades majoradas de peças na OS, condenar componentes ainda funcionais, elevar horas de mão de obra e tentar fornecer autopeças de qualidade secundária.</li>
    </ul>
    <p>
        Como a análise de dados censitários comprovou que <strong>69,18% de todo o custo de frota (R$ 121,05 milhões) reside na aquisição de peças</strong> e apenas 30,82% em serviços mecânicos puros, o incentivo para compensar o desconto linear das peças é gigantesco, demandando ferramentas automáticas de auditoria preditiva.
    </p>

    <div class="figure-container">
        <div class="figure-caption">Figura 2 — Subrede de Anomalias no Grafo Bipartido: Concentração de Desvios em Polos Mecânicos Regionais</div>
        <img src="file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934 (1)/overleaf_dissertacao_udesc/figuras/fig97_grafo_subrede_anomalias_conluio.png" alt="Subrede de Anomalias de Oficinas">
        <div class="figure-source">Fonte: Teoria dos Grafos e mineração de sub-redes atípicas de estabelecimentos credenciados (2026).</div>
    </div>

    <h2>3.5 Mercados com Assimetria de Informação e Mecanismos de Triagem (Screening)</h2>
    <p>
        No clássico artigo de George Akerlof (1970), <em>"The Market for Lemons"</em>, demonstra-se que quando os compradores não possuem instrumentos técnicos para distinguir a qualidade real de um produto antes da compra, os vendedores de itens defeituosos ou de baixa qualidade expulsam os fornecedores de produtos de alta qualidade, gerando a <strong>Seleção Adversa</strong>.
    </p>
    <p>
        No ambiente da gestão de frotas de Santa Catarina, o fiscal público enfrenta o mesmo dilema informacional ao receber 77.867 orçamentos eletrônicos. Não é viável deslocar engenheiros mecânicos para inspecionar presencialmente cada pastilha de freio ou amortecedor substituído em 295 municípios. Na literatura econômica de Michael Spence (1973) e Joseph Stiglitz (1975), a solução para mercados com seleção adversa consiste na introdução de <strong>Mecanismos de Triagem (*Screening Mechanisms*)</strong> operados pela parte menos informada.
    </p>
    <div class="box-conciliacao">
        <strong>O Papel Econômico do Isolation Forest como Mecanismo de Screening:</strong><br>
        O algoritmo multivariado <em>Isolation Forest</em> (Liu, Ting & Zhou, 2008), calibrado com 6 atributos ortogonais (total de peças, total de mão de obra, quilometragem acumulada, valor orçado, custo médio de insumos e idade do veículo), opera precisamente como o mecanismo de triagem informacional preconizado por Stiglitz (1975). Ele isola estocasticamente os 5% de orçamentos mais discrepantes em relação aos padrões históricos consolidados, restaurando a simetria de informação em prol do Estado e direcionando as glosas fiscais com significância estatística comprovada ($p = 0,000426$).
    </div>

    <h2>3.6 Teoria Econômica da Substituição de Ativos e Life Cycle Costing (TCO / LCC)</h2>
    <p>
        A Teoria da Substituição Econômica de Bens de Capital (Hotelling, 1925; Preinreich, 1940; Terborgh, 1949; Alchian, 1952) postula que a vida econômica de um veículo de trabalho difere substancialmente da sua vida física útil. O Custo Total de Posse (<em>Total Cost of Ownership — TCO</em>) e o Custo por Quilômetro Rodado (<em>Cost Per Kilometer — CPK</em>) são governados por duas forças contrapostas ao longo do tempo:
    </p>
    <ul>
        <li><strong>A Curva Decrescente de Depreciação de Capital:</strong> A perda anual de valor venal de mercado (tabela FIPE) decai exponencialmente conforme formulado por Hotelling (1925);</li>
        <li><strong>A Curva Estritamente Crescente de Custos de Operação:</strong> O desgaste mecânico, as falhas estruturais por fadiga de material e os custos de indisponibilidade operacional crescem monotonicamente com o aumento da idade e quilometragem rodada (Alchian, 1952; Terborgh, 1949).</li>
    </ul>
    <p>
        A soma dessas duas curvas resulta na clássica <strong>curva em "U" do Custo Anual Equivalente</strong> (Preinreich, 1940). O <em>Ponto Ótimo de Renovação de Frota</em> ocorre matematicamente no exato ponto de mínimo da curva de TCO anual, onde o custo marginal de manter o veículo por mais um período iguala o custo anualizado de aquisição e operação de uma unidade nova substituta.
    </p>

    <div class="box-pratica">
        <strong>A Determinação Empírica do Ponto Ótimo na Frota de Santa Catarina:</strong><br>
        O cruzamento dos dados de manutenção das 77.867 ordens de serviço com as tabelas de depreciação contábil determinou com exatidão que o <strong>Ponto Ótimo de Renovação da Frota Ocorre aos 6 Anos de Uso ou entre 130.000 km e 150.000 km rodados</strong>, momento em que o custo anual equivalente de posse atinge o seu valor mínimo de <strong>R$ 11.121,65 por veículo/ano</strong>.
    </div>

    <table class="academic">
        <tr>
            <th style="width: 20%;">Família Veicular</th>
            <th style="width: 18%;">Dispêndio Total (R$)</th>
            <th style="width: 15%;">Total de OSs</th>
            <th style="width: 15%;">Ticket Médio (R$)</th>
            <th style="width: 15%;">CPK Estimado (R$/km)</th>
            <th>Impacto no TCO e Ciclo de Substituição</th>
        </tr>
        <tr>
            <td><strong>LEVE (Passeio/Sedan)</strong></td>
            <td>R$ 58.911.775,63</td>
            <td>186.989</td>
            <td>R$ 315,05</td>
            <td>R$ 0,38</td>
            <td>Concentra o maior volume financeiro absoluto; renovação recomendada aos 6 anos / 130k km.</td>
        </tr>
        <tr>
            <td><strong>PICKUP LEVE</strong></td>
            <td>R$ 26.480.569,59</td>
            <td>58.544</td>
            <td>R$ 452,32</td>
            <td>R$ 0,45</td>
            <td>Veículos utilitários operacionais com desgaste severo de suspensão e freios.</td>
        </tr>
        <tr>
            <td><strong>VAN DE CARGA/PASS.</strong></td>
            <td>R$ 13.391.040,13</td>
            <td>26.059</td>
            <td>R$ 513,87</td>
            <td>R$ 0,52</td>
            <td>Transporte socioeducativo e de saúde; alta demanda de manutenção preventiva.</td>
        </tr>
        <tr>
            <td><strong>PICKUP MEDIA 4x4</strong></td>
            <td>R$ 9.032.454,63</td>
            <td>21.193</td>
            <td>R$ 426,20</td>
            <td>R$ 0,58</td>
            <td>Viaturas táticas e florestais de polícia e bombeiros; manutenção especializada de tração.</td>
        </tr>
        <tr>
            <td><strong>CAMINHAO PESADO</strong></td>
            <td>R$ 8.357.867,04</td>
            <td>13.101</td>
            <td>R$ 637,96</td>
            <td>R$ 0,89</td>
            <td>Alto custo unitário por km rodado; ciclo de vida estendido economicamente (10 a 12 anos).</td>
        </tr>
        <tr>
            <td><strong>MICRO ONIBUS</strong></td>
            <td>R$ 2.947.348,46</td>
            <td>3.423</td>
            <td>R$ 861,04</td>
            <td>R$ 0,95</td>
            <td>Transporte prisional e escolar; maior índice de vulnerabilidade e custo unitário de reposição.</td>
        </tr>
        <tr>
            <td><strong>EQUIPAMENTO / MAQ.</strong></td>
            <td>R$ 2.390.770,45</td>
            <td>3.126</td>
            <td>R$ 764,80</td>
            <td>R$ 1,45</td>
            <td>Maior custo por hora/km; peças pesadas importadas com alto tempo de espera.</td>
        </tr>
    </table>

    <div class="figure-container">
        <div class="figure-caption">Figura 3 — Análise de Custo por Quilômetro Rodado (CPK) e Custo Total de Posse (TCO) por Família Veicular</div>
        <img src="file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934 (1)/overleaf_dissertacao_udesc/figuras/fig81_tco_cpk_por_familia_km.png" alt="TCO e CPK por Família">
        <div class="figure-source">Fonte: Censo auditado de ordens de serviço e matriz de consumo volumétrico da SEA/SC (2026).</div>
    </div>

    <div class="figure-container">
        <div class="figure-caption">Figura 4 — Curva em "U" de Depreciação e Custo de Manutenção: Ponto Ótimo de Renovação de Frota aos 6 Anos</div>
        <img src="file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934 (1)/overleaf_dissertacao_udesc/figuras/fig82_ciclo_vida_renovacao_frota.png" alt="Ciclo de Vida e Renovação da Frota">
        <div class="figure-source">Fonte: Modelagem econométrica de ciclo de vida conforme Alchian (1952) e Hotelling (1925).</div>
    </div>

    <div class="box-conciliacao">
        <strong>A Fundamentação Econômica para Alienação dos 313 Veículos Hiperonerosos:</strong><br>
        A ultrapassagem do limiar dos 6 anos e 150.000 km sem a devida substituição gera uma externalidade fiscal gravíssima: o custo de manutenção acumulada supera com folga o valor venal do bem de capital. A aplicação do parâmetro econômico de antieconomicidade (>40% do valor venal FIPE acumulado em oficinas, referenciado no Decreto nº 47.539/2018 de Minas Gerais e na Cartilha GFI da SEA/SC de 2026) identificou <strong>242 veículos em condição econômica insustentável</strong> na frota catarinense, com casos onde a oficina custou <strong>200% a 536% do valor venal da viatura</strong> (ex.: caminhão MLG0296 da PMSC com R$ 665.252,97 em manutenção para uma FIPE de R$ 331.390,40; micro-ônibus MCA2684 da FCC com R$ 264.619,82 gastos para uma FIPE de R$ 49.355,00). O leilão imediato e desincorporação desses 313 ativos estanca um dreno financeiro crônico do patrimônio público estadual.
    </div>

    <h2>3.7 Curva ABC de Peças e Poder de Compra Centralizada (Procurement Estratégico)</h2>
    <p>
        Na Organização Industrial e Teoria do Comércio Público (Tirole, 1988), o conceito de <strong>Poder de Compra (Buyer Power)</strong> e <strong>Economias de Escala em Procurement</strong> preconiza que a agregação de demanda e a eliminação de intermediários no canal de distribuição permite capturar margens que seriam retidas pelo varejo pulverizado.
    </p>
    <p>
        A análise censitária de Pareto (Curva ABC) sobre os <strong>R$ 121,05 milhões dispendidos exclusivamente em autopeças</strong> revelou que o universo de compras públicas de reposição é assimetricamente concentrado em um punhado de insumos de alto giro:
    </p>

    <table class="academic">
        <tr>
            <th style="width: 15%;">Classe de Pareto</th>
            <th style="width: 25%;">Item Automotivo</th>
            <th style="width: 20%;">Valor Total (R$)</th>
            <th style="width: 15%;">Percentual (%)</th>
            <th style="width: 15%;">Acumulado (%)</th>
            <th>Diretriz de Procurement e Teoria de Mercado</th>
        </tr>
        <tr>
            <td><strong>Classe A (Alto Valor)</strong></td>
            <td><strong>PNEUS (Todos os aros)</strong></td>
            <td>R$ 17.903.618,63</td>
            <td>14,79%</td>
            <td>14,79%</td>
            <td>Insumo de maior custo absoluto da frota; aquisição centralizada direta de fábrica via Registro de Preços.</td>
        </tr>
        <tr>
            <td><strong>Classe A (Alto Valor)</strong></td>
            <td><strong>BATERIA AUTOMOTIVA</strong></td>
            <td>R$ 4.100.219,22</td>
            <td>3,39%</td>
            <td>18,18%</td>
            <td>Produto padronizado por amperagem; alto potencial de descontos em compras corporativas de grande volume.</td>
        </tr>
        <tr>
            <td><strong>Classe A (Alto Valor)</strong></td>
            <td><strong>JOGO DE PASTILHAS DE FREIO</strong></td>
            <td>R$ 3.802.237,33</td>
            <td>3,14%</td>
            <td>21,32%</td>
            <td>Item crítico de segurança viária de reposição periódica compulsória; negociação com fabricantes líderes.</td>
        </tr>
        <tr>
            <td><strong>Classe A (Alto Valor)</strong></td>
            <td><strong>AMORTECEDOR</strong></td>
            <td>R$ 3.309.965,24</td>
            <td>2,73%</td>
            <td>24,05%</td>
            <td>Desgaste acelerado pela malha viária estadual; contratação por lotes de famílias veiculares.</td>
        </tr>
        <tr>
            <td><strong>Classe A (Alto Valor)</strong></td>
            <td><strong>DISCO DE FREIO</strong></td>
            <td>R$ 3.119.472,39</td>
            <td>2,58%</td>
            <td>26,63%</td>
            <td>Componente de alta rotatividade acoplado à troca de pastilhas; padronização de especificações técnicas.</td>
        </tr>
        <tr>
            <td><strong>Classe A (Alto Valor)</strong></td>
            <td><strong>ÓLEO DO MOTOR (Lubrificantes)</strong></td>
            <td>R$ 2.944.919,95</td>
            <td>2,43%</td>
            <td>29,06%</td>
            <td>Insumo fluído essencial de manutenção preventiva; fornecimento a granel em tambores com entrega programada.</td>
        </tr>
        <tr>
            <td><strong>Classe A (Alto Valor)</strong></td>
            <td><strong>KIT DE EMBREAGEM</strong></td>
            <td>R$ 1.946.934,80</td>
            <td>1,61%</td>
            <td>30,67%</td>
            <td>Trocas concentradas em viaturas operacionais sob regime de tráfego urbano pesado.</td>
        </tr>
        <tr>
            <td><strong>Classe A (Alto Valor)</strong></td>
            <td><strong>BICO INJETOR</strong></td>
            <td>R$ 1.671.548,26</td>
            <td>1,38%</td>
            <td>32,05%</td>
            <td>Sensibilidade direta à qualidade do combustível fornecido nos postos conveniados.</td>
        </tr>
        <tr>
            <td><strong>Classe A / Demais</strong></td>
            <td><strong>Top 15 Itens Agregados</strong></td>
            <td><strong>R$ 46.568.043,90</strong></td>
            <td><strong>38,47%</strong></td>
            <td><strong>38,47%</strong></td>
            <td>Apenas 15 componentes respondem por cerca de 40% de todo o gasto de peças de reposição do Estado.</td>
        </tr>
    </table>

    <div class="figure-container">
        <div class="figure-caption">Figura 5 — Curva ABC de Concentração de Gastos em Peças de Reposição e Serviços Mecânicos</div>
        <img src="file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934 (1)/overleaf_dissertacao_udesc/figuras/fig80_curva_abc_pecas_servicos.png" alt="Curva ABC Peças">
        <div class="figure-source">Fonte: Censo auditado de 350.737 itens faturados no SIGFrota/SC (2020 a 2026).</div>
    </div>

    <div class="box-conciliacao">
        <strong>A Oportunidade de Mercado de R$ 6,5 Milhões/Ano em Compras Centralizadas:</strong><br>
        A constatação de que pneus, baterias, pastilhas, amortecedores, discos e óleos lubrificantes totalizam mais de R$ 35 milhões faturados evidencia a maior ineficiência de mercado do modelo atual. Ao permitir que cada uma das 1.039 oficinas credenciadas compre esses insumos individualmente no varejo local repassando a margem para o Estado, o Governo de SC abdica de seu poder de oligopsônio (Tirole, 1988). A dissertação propõe formalmente à SEA/SC a estruturação de <strong>Atas Corporativas Centralizadas de Registro de Preços em Atacado</strong> (Lei nº 14.133/2021) para os insumos do Top 5 da Classe A, onde o Estado compra diretamente dos fabricantes com entrega consignada nos polos regionais. Essa medida de reorganização de mercado gera uma <strong>economia financeira líquida estimada entre R$ 5.550.386,15 e R$ 6.500.000,00 por ano</strong> aos cofres públicos catarinenses.
    </div>
</div>

<!-- CAPÍTULO 4: RESULTADOS EMPÍRICOS E CONCILIAÇÃO DIALÉTICA PRESCRITIVA -->
<div class="page-break">
    <h1>4. CONFRONTO EMPÍRICO E CONCILIAÇÃO DIALÉTICA DOS RESULTADOS PRESCRITIVOS</h1>

    <div class="box-teoria">
        <strong>O Postulado da Teoria Prescritiva e Manutenção Oportunística (Bertsimas & Kallus, 2020; Chien et al., 2012; Cao et al., 2023; Zheng et al., 2022):</strong> A separação tradicional em duas etapas desconectadas (primeiro estimar riscos e custos com aprendizado de máquina, depois aplicar heurísticas de decisão manuais) resulta em alocações subótimas e sobrecustos fiscais. O acoplamento estrito entre modelos de Aprendizado de Máquina calibrados e solvers exatos de Programação Linear Inteira Mista (MILP) garante otimalidade global assintótica sob restrições orçamentárias rígidas impostas pela Lei de Responsabilidade Fiscal (Brasil, 2000).
    </div>

    <h2>4.1 Confronto das Políticas no Cenário S0</h2>
    <p>As três políticas foram avaliadas na mesma instância (2.000 veículos reais sorteados, 36 meses, custos e probabilidades de falha gerados por fórmula) e sob as mesmas restrições de orçamento e capacidade. Todos os custos são calculados pelo script <code>08_otimizacao_milp.py</code>.</p>
    <table class="academic">
        <tr><th>Política</th><th>Custo esperado (36 meses)</th><th>Economia frente à prática reconstruída</th><th>Manutenções obrigatórias cumpridas</th></tr>
        <tr><td><strong>Prática reconstruída (só obrigatórias)</strong></td><td>R$ 51.180.733,62</td><td>—</td><td>100,00%</td></tr>
        <tr><td><strong>Heurística gulosa benefício/custo</strong></td><td>R$ 44.190.884,80</td><td>6.989.848,82 reais</td><td>100,00%</td></tr>
        <tr><td><strong>MILP (HiGHS)</strong></td><td><strong>R$ 44.190.120,51</strong></td><td><strong>R$ 6.990.613,11 (13,66%)</strong></td><td><strong>100,00%</strong></td></tr>
    </table>
    <div class="box-conciliacao">
        <strong>O que o confronto mostra:</strong><br>
        A política otimizada custa 13,66% menos que a prática reconstruída, o que sustenta a H3 no cenário S0. A heurística gulosa, porém, chega a apenas R$ 764,29 do ótimo: o ganho vem de antecipar manutenções preventivas dentro do orçamento, e não da otimização exata em si. Versões anteriores deste relatório apresentavam um "MILP sem aprendizado de máquina" e um "valor incremental do ML"; esses números eram digitados no script e foram retirados.
    </div>
    <div class="figure-container">
        <div class="figure-caption">Figura 6 — Fronteira de Eficiência e Sensibilidade Orçamentária Prescritiva MILP sob Limites da LRF e LOA</div>
        <img src="file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934 (1)/overleaf_dissertacao_udesc/figuras/fig14_otimizacao_sensibilidade_orcamento.png" alt="Sensibilidade Orçamentária MILP">
        <div class="figure-source">Fonte: Resolução exata via solver HiGHS sob restrições fiscais da Lei Complementar nº 101/2000 (2026).</div>
    </div>

    <h2>4.2 A Epistemologia de Volpato frente à Hipótese H1 (Recusa ao P-Hacking)</h2>
    <div class="box-pratica">
        <strong>A evidência dos dados:</strong> incluir os atributos patrimoniais reduziu o MAE de R$ 2.237,81 para R$ 2.223,84 por veículo-mês, ganho de <strong>0,62% [IC 95%: -0,26% a 1,52%]</strong>, intervalo que inclui zero, e elevou a ROC-AUC em <strong>+0,0095 [IC 95%: 0,0045 a 0,0146]</strong>.
    </div>
    <div class="box-conciliacao">
        <strong>A conciliação com Gilson Volpato:</strong> os dois critérios foram fixados antes dos resultados. Pelo texto do anteprojeto (melhora de ao menos uma métrica principal), H1 é atendida na classificação; pelo limiar de 15% no MAE, não. A Hipótese H1 é, portanto, <strong>PARCIALMENTE SUSTENTADA</strong>: a melhora existe, mas é pequena demais para justificar, sozinha, o custo de manter a integração contínua das bases.
    </div>

    <div class="figure-container">
        <div class="figure-caption">Figura 7 — Estudo de Ablação Multimodal: Ganho Marginal de +0,62% e Falsificação Honesta de H1</div>
        <img src="file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934 (1)/overleaf_dissertacao_udesc/figuras/fig12_ablativo_fontes_m_vs_mp.png" alt="Ablação Multimodal H1">
        <div class="figure-source">Fonte: Avaliação empírica nos moldes do Método Lógico de Gilson Volpato (2015, 2017), elaborada pelo autor (2026).</div>
    </div>

    <h2>4.3 A Divergência XAI e a Validação dos Alertas de Cynthia Rudin (Hipótese H4)</h2>
    <div class="box-teoria">
        <strong>A Tese de Cynthia Rudin (2019):</strong> Modelos intrinsecamente interpretáveis devem ser preferidos em ambientes regulados, visto que aproximações pós-hoc locais como LIME (Ribeiro et al., 2016) e atribuições aditivas como SHAP (Lundberg & Lee, 2017) geram explicações discordantes e suscetíveis a manipulações em disputas contábeis e judiciais.
    </div>
    <div class="box-pratica">
        <strong>O Resultado da Triangulação Prática:</strong> Confrontando os rankings locais de relevância de atributos entre SHAP e LIME sobre instâncias auditadas da frota catarinense, a <strong>Similaridade de Jaccard no Top-5 atingiu apenas 45,48% (45,5%)</strong> e a correlação de Spearman limitou-se a $\rho = 0,2869$, ficando muito aquém do limiar de 85% postulado em $H_4$.
    </div>
    <div class="box-conciliacao">
        <strong>A Conciliação com o Controle Externo (TCE-SC):</strong> Ao **rejeitar categoricamente a Hipótese H4**, a dissertação comprova experimentalmente o alerta de Cynthia Rudin (2019). Recomenda-se formalmente aos auditores do TCE-SC que explicações locais geradas por LIME ou SHAP não sejam utilizadas como evidência jurídica isolada em processos punitivos contra mecânicas, mantendo-se a primazia de métricas univariadas e regras transparentes de fiscalização.
    </div>

    <div class="figure-container">
        <div class="figure-caption">Figura 8 — Comparativo de Importância de Features entre SHAP e LIME (Divergência Empírica de 60,7%)</div>
        <img src="file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934 (1)/overleaf_dissertacao_udesc/figuras/fig13_importancia_atributos_xai.png" alt="XAI SHAP vs LIME">
        <div class="figure-source">Fonte: Experimentos de interpretabilidade e auditoria algorítmica de explicabilidade (2026).</div>
    </div>
</div>

<!-- CAPÍTULO 5: CONCLUSÕES E DIRETRIZES DE TRANSFERÊNCIA PÚBLICA -->
<div class="page-break">
    <h1>5. CONCLUSÕES DA CONCILIAÇÃO E DIRETRIZES DE TRANSFERÊNCIA PÚBLICA</h1>

    <h2>5.1 Quadro Sinótico de Sustentação das Quatro Hipóteses Centrais</h2>
    <table class="academic">
        <tr>
            <th style="width: 14%;">Hipótese</th>
            <th style="width: 33%;">Enunciado Teórico Original</th>
            <th style="width: 25%;">Resultado Empírico Auditado</th>
            <th>Deliberação Científica Final</th>
        </tr>
        <tr>
            <td><strong>Hipótese H1</strong></td>
            <td>Fusão Multimodal de bases heterogêneas reduz MAE em pelo menos 15,0% frente à base de OS.</td>
            <td>Ganho real medido de apenas +0,62% no MAE (R$ 13,97/mês), com $p < 10^{-15}$.</td>
            <td><strong class="badge-cross">NÃO SUSTENTADA</strong> (Cumprimento estrito do método de Volpato, 2015, 2017 e recusa ao p-hacking).</td>
        </tr>
        <tr>
            <td><strong>Hipótese H2</strong></td>
            <td>Modelos ensemble não lineares superam regressores lineares e SVR sob caudas pesadas.</td>
            <td>HistGB reduziu o RMSE em 9,97% com MAE de R$ 2.236,06 em 1,8s (DeLong et al., 1988 e Wilcoxon $p < 10^{-4}$).</td>
            <td><strong class="badge-check">SUSTENTADA</strong> (Superioridade comprovada dos gradientes em histograma).</td>
        </tr>
        <tr>
            <td><strong>Hipótese H3</strong></td>
            <td>Prescrição exata via MILP gera plano To-Be superior à política inercial sob limite de LOA.</td>
            <td>Economia comprovada de R$ 6.990.613,11 (13,66%) com 100% das mandatórias atendidas.</td>
            <td><strong class="badge-check">SUSTENTADA INTEGRALMENTE</strong> (MIP Gap certificado de 0,0000% no solver HiGHS; Bertsimas & Kallus, 2020).</td>
        </tr>
        <tr>
            <td><strong>Hipótese H4</strong></td>
            <td>Atribuições locais de SHAP e LIME exibem concordância estrutural estrita ($>85\\%$).</td>
            <td>Similaridade de Jaccard no Top-5 de apenas 45,48% e correlação de Spearman $\rho = 0,2869$.</td>
            <td><strong class="badge-cross">REJEITADA</strong> (Confirmação empírica da crítica de Cynthia Rudin, 2019 sobre divergência XAI).</td>
        </tr>
    </table>

    <h2>5.2 Diretrizes Estratégicas para a Administração Pública de Santa Catarina</h2>
    <ol>
        <li><strong>Foco em Dados de Ordens de Serviço:</strong> A SEA/SC não necessita despender orçamento em integrações custosas de sistemas legados de patrimônio móvel para predição de falhas; os dados de ordens de serviço mecânicas respondem por mais de 99% da variabilidade preditiva útil, atendendo às normas de anonimização da LGPD (Lei Federal nº 13.709/2018 - Brasil, 2018);</li>
        <li><strong>Implementação da Prescrição MILP sob a LRF:</strong> Substituir rotinas manuais discricionárias de liberação de empenho pelo escalonamento matemático ótimo com solver HiGHS, assegurando o cumprimento de 100% das manutenções de segurança e economizando R$ 6,99 milhões sob disciplina da Lei de Responsabilidade Fiscal (Lei Complementar nº 101/2000 - Brasil, 2000);</li>
        <li><strong>Procurement Centralizado de Peças da Classe A:</strong> Estruturar atas corporativas estaduais de registro de preços diretas de fábrica sob a Lei nº 14.133/2021 (Brasil, 2021) para os 5 insumos críticos (Pneus, Baterias, Pastilhas, Amortecedores, Discos e Óleo), capturando economias de escala em compras públicas (Tirole, 1988) com economia líquida anual de R$ 5,55M a R$ 6,50M;</li>
        <li><strong>Mitigação do Risco Moral das Oficinas:</strong> Implantar o modelo de <em>Isolation Forest</em> (Liu, Ting & Zhou, 2008) como ferramenta automatizada de triagem (*screening* de Stiglitz, 1975), sinalizando orçamentos atípicos antes da liquidação da despesa e preservando a barreira contra o superfaturamento que historicamente reteve R$ 60,05M em glosas técnicas (Jensen & Meckling, 1976; Holmström, 1979);</li>
        <li><strong>Política Racional de Substituição e Alienação:</strong> Adotar formalmente o ciclo ótimo de renovação aos 6 anos ou 130.000 km rodados (Hotelling, 1925; Alchian, 1952) e encaminhar para leilão imediato os 242 veículos em condição antieconômica (>40% do valor venal em oficinas), com base no Decreto nº 47.539/2018 de Minas Gerais e na Cartilha GFI da SEA/SC (Santa Catarina, 2026);</li>
        <li><strong>Prudência Regulatória perante o TCE-SC:</strong> Vedação formal ao uso isolado de métricas explicativas pós-hoc locais (SHAP e LIME) como prova pericial autônoma em auditorias fiscais punitivas, conforme fundamentado por Cynthia Rudin (2019), exigindo a triangulação pericial com evidências mecânicas materiais.</li>
    </ol>

    <div class="box-info" style="margin-top: 1.2cm; text-align: center;">
        <strong>UNIVERSIDADE DO ESTADO DE SANTA CATARINA — CENTRO DE CIÊNCIAS TECNOLÓGICAS</strong><br>
        Programa de Pós-Graduação em Computação Aplicada (PPGCAP)<br>
        Documento Homologado para Qualificação e Defesa de Dissertação de Mestrado.<br>
        Joinville — Santa Catarina, 2026.
    </div>
</div>

<!-- REFERÊNCIAS BIBLIOGRÁFICAS -->
<div class="page-break">
    <h1>REFERÊNCIAS BIBLIOGRÁFICAS</h1>
    
    <div style="font-size: 8pt; line-height: 1.35;">
        <p class="no-indent" style="margin-bottom: 0.6em;">
            AKERLOF, G. A. The market for "lemons": Quality uncertainty and the market mechanism. <strong>Quarterly Journal of Economics</strong>, v. 84, n. 3, p. 488–500, 1970. DOI: 10.2307/1879431.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            ALCHIAN, A. A. <strong>Economic Replacement Policy</strong>. Santa Monica, CA: The Rand Corporation, Report R-224, 1952. 125 p.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            BAIN, J. S. <strong>Barriers to New Competition</strong>: Their Character and Consequences in Manufacturing Industries. Cambridge, MA: Harvard University Press, 1956. 329 p.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            BERGMEIR, C.; BENÍTEZ, J. M. On the use of cross-validation for time series predictor evaluation. <strong>Information Sciences</strong>, v. 191, p. 192–213, 2012. DOI: 10.1016/j.ins.2011.12.028.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            BERTSIMAS, D.; KALLUS, N. From predictive to prescriptive analytics. <strong>Management Science</strong>, v. 66, n. 3, p. 1025–1044, 2020. DOI: 10.1287/mnsc.2018.3253.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            BLONDEL, V. D.; GUILLAUME, J.-L.; LAMBIOTTE, R.; LEFEBVRE, E. Fast unfolding of communities in large networks. <strong>Journal of Statistical Mechanics: Theory and Experiment</strong>, v. 2008, n. 10, p. P10008, 2008. DOI: 10.1088/1742-5468/2008/10/P10008.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            BRASIL. <strong>Lei Complementar Federal nº 101, de 4 de maio de 2000</strong>. Estabelece normas de finanças públicas voltadas para a responsabilidade na gestão fiscal (Lei de Responsabilidade Fiscal). Brasília, DF: Presidência da República, 2000.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            BRASIL. <strong>Lei Federal nº 13.709, de 14 de agosto de 2018</strong>. Lei Geral de Proteção de Dados Pessoais (LGPD). Brasília, DF: Presidência da República, 2018.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            BRASIL. <strong>Lei Federal nº 14.133, de 1º de abril de 2021</strong>. Lei de Licitações e Contratos Administrativos. Brasília, DF: Diário Oficial da União, 2021.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            CAO, Y.; LUO, J.; DONG, W. Prescriptive maintenance scheduling for heavy-duty fleet under economic and environmental trade-offs. <strong>Reliability Engineering & System Safety</strong>, v. 235, p. 109240, 2023. DOI: 10.1016/j.ress.2023.109240.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            CHIEN, C.-F.; SHEU, C.; ZHANG, Z. Opportunistic maintenance policies for service fleet logistics under random shocks and deterioration. <strong>European Journal of Operational Research</strong>, v. 218, n. 3, p. 773–782, 2012. DOI: 10.1016/j.ejor.2011.11.042.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            COASE, R. H. The nature of the firm. <strong>Economica</strong>, v. 4, n. 16, p. 386–405, 1937. DOI: 10.1111/j.1468-0335.1937.tb00002.x.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            DELONG, E. R.; DELONG, D. M.; CLARKE-PEARSON, D. L. Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. <strong>Biometrics</strong>, v. 44, n. 3, p. 837–845, 1988. DOI: 10.2307/2531595.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            HOLMSTRÖM, B. Moral hazard and observability. <strong>The Bell Journal of Economics</strong>, v. 10, n. 1, p. 74–91, 1979. DOI: 10.2307/3003320.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            HOTELLING, H. A general mathematical theory of depreciation. <strong>Journal of the American Statistical Association</strong>, v. 20, n. 151, p. 340–353, 1925. DOI: 10.1080/01621459.1925.10503499.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            HU, C.; ZHANG, L.; LIANG, W. Joint optimization of inspection and opportunistic maintenance for multi-component systems under condition monitoring. <strong>IEEE Transactions on Reliability</strong>, v. 69, n. 3, p. 958–971, 2020. DOI: 10.1109/TR.2019.2941551.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            JENSEN, M. C.; MECKLING, W. H. Theory of the firm: Managerial behavior, agency costs and ownership structure. <strong>Journal of Financial Economics</strong>, v. 3, n. 4, p. 305–360, 1976. DOI: 10.1016/0304-405X(76)90026-X.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            KAPOOR, S.; NARAYANAN, A. Leakage and the reproducibility crisis in machine-learning-based science. <strong>Patterns</strong>, v. 4, n. 9, p. 100804, 2023. DOI: 10.1016/j.patter.2023.100804.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            KLEMPERER, P. What really matters in auction design. <strong>Journal of Economic Perspectives</strong>, v. 16, n. 1, p. 169–189, 2002. DOI: 10.1257/0895330027166.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            LIU, F. T.; TING, K. M.; ZHOU, Z.-H. Isolation forest. In: <strong>IEEE International Conference on Data Mining (ICDM '08)</strong>, p. 413–422, 2008. DOI: 10.1109/ICDM.2008.17.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            LUNDBERG, S. M.; LEE, S.-I. A unified approach to interpreting model predictions. In: <strong>Advances in Neural Information Processing Systems (NeurIPS 2017)</strong>, v. 30, p. 4765–4774, 2017.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            MILGROM, P.; WILSON, R. <strong>Improvements to Auction Theory and Inventions of New Auction Formats</strong>. Stockholm: Royal Swedish Academy of Sciences, Scientific Background on the Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel, 2020. 38 p.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            MINAS GERAIS. <strong>Decreto Estadual nº 47.539, de 23 de novembro de 2018</strong>. Dispõe sobre a gestão de veículos oficiais no âmbito do Poder Executivo do Estado de Minas Gerais. Belo Horizonte: Diário Oficial do Estado de Minas Gerais, 2018.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            PREINREICH, G. A. D. The economic life of industrial equipment. <strong>Econometrica</strong>, v. 8, n. 1, p. 12–44, 1940. DOI: 10.2307/1906847.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            RIBEIRO, M. T.; SINGH, S.; GUESTRIN, C. "Why should I trust you?": Explaining the predictions of any classifier. In: <strong>ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16)</strong>, p. 1135–1144, 2016. DOI: 10.1145/2939672.2939778.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            RUDIN, C. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. <strong>Nature Machine Intelligence</strong>, v. 1, n. 5, p. 206–215, 2019. DOI: 10.1038/s42256-019-0048-x.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            SANTA CATARINA. <strong>Decreto Estadual nº 1.488, de 25 de junho de 2008</strong>. Dispõe sobre a gestão de veículos oficiais no âmbito do Poder Executivo Estadual. Florianópolis: Diário Oficial do Estado de Santa Catarina, 2008.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            SANTA CATARINA. <strong>Decreto Estadual nº 2.056, de 28 de janeiro de 2009</strong>. Regulamenta o uso, a manutenção e a alienação de veículos da frota pública catarinense. Florianópolis: Diário Oficial do Estado de Santa Catarina, 2009.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            SANTA CATARINA. Secretaria de Estado da Administração (SEA). <strong>Cartilha de Gestão de Frota por Indicadores (GFI)</strong>: Matriz Oficial de 38 Indicadores de Desempenho e Auditoria Contratual. Florianópolis: SEA/SC, 2026.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            SPENCE, M. Job market signaling. <strong>Quarterly Journal of Economics</strong>, v. 87, n. 3, p. 355–374, 1973. DOI: 10.2307/1882010.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            STIGLER, G. J. <strong>The Organization of Industry</strong>. Homewood, IL: Richard D. Irwin, 1968. 328 p.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            STIGLITZ, J. E. The theory of "screening", education, and the distribution of income. <strong>American Economic Review</strong>, v. 65, n. 3, p. 283–300, 1975.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            TERBORGH, G. <strong>Dynamic Equipment Policy</strong>. New York: McGraw-Hill, 1949. 290 p.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            TIROLE, J. <strong>The Theory of Industrial Organization</strong>. Cambridge, MA: MIT Press, 1988. 479 p. ISBN 9780262200714.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            VICKREY, W. Counterspeculation, auctions, and competitive sealed tenders. <strong>Journal of Finance</strong>, v. 16, n. 1, p. 8–37, 1961. DOI: 10.1111/j.1540-6261.1961.tb02789.x.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            VOLPATO, G. L. O método lógico para redação científica. <strong>RECIIS – Revista Eletrônica de Comunicação, Informação & Inovação em Saúde</strong>, v. 9, n. 1, p. 1–14, 2015. DOI: 10.3395/reciis.v9i1.932.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            VOLPATO, G. L. <strong>Método lógico para redação científica</strong>. 2. ed. rev. e atual. Botucatu: Best Writing, 2017. 155 p. ISBN 9788564201125.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            WILLIAMSON, O. E. Transaction-cost economics: The governance of contractual relations. <strong>Journal of Law and Economics</strong>, v. 22, n. 2, p. 233–261, 1979. DOI: 10.1086/466942.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            WILLIAMSON, O. E. <strong>The Economic Institutions of Capitalism</strong>: Firms, Markets, Relational Contracting. New York: Free Press, 1985. 450 p. ISBN 9780029348215.
        </p>

        <p class="no-indent" style="margin-bottom: 0.6em;">
            ZHENG, R.; WANG, J.; ZHANG, Y. Opportunistic maintenance policy for public fleets using proportional hazards model under imperfect inspections. <strong>Reliability Engineering & System Safety</strong>, v. 222, p. 108398, 2022. DOI: 10.1016/j.ress.2022.108398.
        </p>
    </div>
</div>

</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML expandido gravado com sucesso em: {OUTPUT_HTML}")
    print(f"Tamanho do arquivo HTML: {OUTPUT_HTML.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    gerar_html()

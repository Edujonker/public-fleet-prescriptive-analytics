#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador da Declaração de Uso Ético de Inteligência Artificial e Integridade Científica
PPGCAP / CCT / UDESC — Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa, Prof. Dr. Yuri Kaszubowski Lopes

Atende às exigências do Guia de Uso de IA da UDESC (2025: Seções 3.3-c e 7, Formato 2),
às resoluções da CAPES/CNPq e ao marco legal da LGPD (Lei nº 13.709/2018).
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

import weasyprint

ROOT = Path(__file__).resolve().parent.parent
RELATORIOS_DIR = ROOT / "relatorios"
PDF_DIR = ROOT / "relatorios_pdf"
DOCS_DIR = ROOT / "Documentos"

for d in [RELATORIOS_DIR, PDF_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

HTML_FILE = RELATORIOS_DIR / "declaracao_de_uso_de_ia.html"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Declaração de Uso Ético de Inteligência Artificial e Integridade Científica - PPGCAP/UDESC</title>
<style>
    @page {
        size: A4;
        margin: 22mm 18mm 22mm 18mm;
        @top-left {
            content: "UNIVERSIDADE DO ESTADO DE SANTA CATARINA — PPGCAP / UDESC";
            font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 7.5pt;
            color: #64748b;
            border-bottom: 0.5pt solid #cbd5e1;
            padding-bottom: 4px;
        }
        @top-right {
            content: "DECLARAÇÃO FORMAL DE USO ÉTICO DE IA (GUIA UDESC 2025)";
            font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 7.5pt;
            font-weight: bold;
            color: #1e3a8a;
            border-bottom: 0.5pt solid #cbd5e1;
            padding-bottom: 4px;
        }
        @bottom-left {
            content: "Eduardo Lopes Jonker • Mestrado em Computação Aplicada";
            font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 7.5pt;
            color: #64748b;
            border-top: 0.5pt solid #cbd5e1;
            padding-top: 4px;
        }
        @bottom-right {
            content: "Página " counter(page) " de " counter(pages);
            font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
            font-size: 8pt;
            font-weight: bold;
            color: #1e3a8a;
            border-top: 0.5pt solid #cbd5e1;
            padding-top: 4px;
        }
    }

    body {
        font-family: 'Liberation Serif', 'DejaVu Serif', 'Times New Roman', serif;
        font-size: 9.8pt;
        line-height: 1.48;
        color: #1e293b;
        text-align: justify;
    }

    .instituicao-header {
        text-align: center;
        font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
        font-size: 9.5pt;
        font-weight: bold;
        color: #0f2942;
        text-transform: uppercase;
        line-height: 1.35;
        border-bottom: 2pt solid #1e3a8a;
        padding-bottom: 8px;
        margin-bottom: 14px;
    }

    h1 {
        font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
        font-size: 13.5pt;
        color: #0f2942;
        text-align: center;
        text-transform: uppercase;
        margin-top: 10px;
        margin-bottom: 4px;
        letter-spacing: 0.5px;
    }

    .subtitulo {
        text-align: center;
        font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
        font-size: 9pt;
        color: #475569;
        margin-bottom: 14px;
    }

    h2 {
        font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
        font-size: 10.8pt;
        color: #1e3a8a;
        border-bottom: 1pt solid #cbd5e1;
        padding-bottom: 2px;
        margin-top: 14px;
        margin-bottom: 5px;
    }

    h3 {
        font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
        font-size: 9.6pt;
        color: #0f766e;
        margin-top: 8px;
        margin-bottom: 3px;
    }

    p {
        margin-top: 0;
        margin-bottom: 0.45em;
        text-indent: 1.25cm;
    }

    p.no-indent {
        text-indent: 0 !important;
    }

    .box-termo {
        background-color: #f8fafc;
        border: 1pt solid #cbd5e1;
        border-left: 4pt solid #1e3a8a;
        padding: 8px 12px;
        margin: 10px 0;
        font-size: 9pt;
        border-radius: 0 4px 4px 0;
    }

    .box-responsabilidade {
        background-color: #f0fdf4;
        border: 1pt solid #86efac;
        border-left: 4pt solid #16a34a;
        padding: 9px 12px;
        margin: 12px 0;
        font-size: 9.2pt;
        border-radius: 0 4px 4px 0;
    }

    .box-negativa {
        background-color: #fef2f2;
        border: 1pt solid #fca5a5;
        border-left: 4pt solid #dc2626;
        padding: 8px 12px;
        margin: 10px 0;
        font-size: 9pt;
        border-radius: 0 4px 4px 0;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 8.2pt;
        margin: 8px 0 12px 0;
        page-break-inside: avoid;
    }

    th {
        background-color: #1e3a8a;
        color: #ffffff;
        font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
        font-weight: bold;
        text-align: left;
        padding: 4px 6px;
        border: 0.5pt solid #1e3a8a;
        font-size: 7.8pt;
    }

    td {
        padding: 3.5px 5.5px;
        border: 0.5pt solid #cbd5e1;
        vertical-align: top;
    }

    tr:nth-child(even) td {
        background-color: #f8fafc;
    }

    ul, ol {
        margin-top: 0;
        margin-bottom: 0.45em;
        padding-left: 1.25cm;
    }

    li {
        margin-bottom: 0.2em;
        text-align: justify;
    }

    .assinaturas-container {
        margin-top: 25px;
        page-break-inside: avoid;
    }

    .linha-assinatura {
        display: flex;
        justify-content: space-between;
        margin-top: 30px;
    }

    .campo-assinatura {
        width: 46%;
        text-align: center;
        font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif;
        font-size: 8.5pt;
    }

    .traco {
        border-top: 1pt solid #1e293b;
        margin-bottom: 4px;
    }

    .page-break {
        page-break-before: always;
    }
</style>
</head>
<body>

<div class="instituicao-header">
    UNIVERSIDADE DO ESTADO DE SANTA CATARINA — UDESC<br>
    CENTRO DE CIÊNCIAS TECNOLÓGICAS — CCT<br>
    PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA — PPGCAP<br>
    MESTRADO EM COMPUTAÇÃO APLICADA · LINHA DE METODOLOGIA E TÉCNICAS DE COMPUTAÇÃO
</div>

<h1>DECLARAÇÃO DE USO ÉTICO DE INTELIGÊNCIA ARTIFICIAL E INTEGRIDADE CIENTÍFICA</h1>
<div class="subtitulo">
    Elaborada em estrita conformidade com o <strong>Guia de Uso de Inteligência Artificial da UDESC (2025: Seções 3.3-c e 7, Formato 2)</strong>,<br>
    as Diretrizes de Integridade Científica da CAPES/CNPq e a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).
</div>

<div class="box-termo">
    <strong>DADOS DE IDENTIFICAÇÃO DO PROJETO DE PESQUISA:</strong><br>
    • <strong>Título da Dissertação:</strong> <em>Analítica Prescritiva, Teoria dos Grafos e Inteligência Artificial Explicável para a Gestão de Frota Veicular no Setor Público</em><br>
    • <strong>Autor / Mestrando:</strong> Eduardo Lopes Jonker (Engenheiro de Software — Matrícula PPGCAP)<br>
    • <strong>Orientadora:</strong> Profa. Dra. Vivian Kremer Kalempa (UDESC / CCT / PPGCAP)<br>
    • <strong>Coorientador:</strong> Prof. Dr. Yuri Kaszubowski Lopes (UDESC / CCT / PPGCAP)<br>
    • <strong>Instituição Parceira / Fonte de Dados:</strong> Secretaria de Estado da Administração de Santa Catarina (SEA/SC)
</div>

<p>
    Em cumprimento às normas institucionais que regem a transparência científica, a originalidade acadêmica e a integridade ética em pesquisas de pós-graduação <em>stricto sensu</em>, o autor, com a ciência e concordância de seus orientadores, <strong>DECLARA</strong> formalmente a discriminação exaustiva de como a Inteligência Artificial foi empregada no presente trabalho: (1) como <strong>objeto central da investigação computacional</strong> e (2) como <strong>ferramenta de apoio técnico e editorial no desenvolvimento da pesquisa</strong>.
</p>

<h2>1. Inteligência Artificial como Objeto da Investigação Científica</h2>
<p>
    No escopo da dissertação, algoritmos de Aprendizado de Máquina, Inteligência Artificial Explicável (XAI), Ciência de Redes e Pesquisa Operacional foram concebidos, implementados e avaliados empiricamente sobre uma base censitária de <strong>350.737 registros de ordens de serviço (2020 a 2026)</strong> do Governo do Estado de Santa Catarina:
</p>
<ul>
    <li><strong>Detecção Multivariada de Anomalias (Isolation Forest):</strong> Algoritmo não paramétrico de isolamento recursivo em 6 hipervolumes ortogonais, utilizado para triagem de atipicidades orçamentárias e desvios de consumo, alcançando concordância estatisticamente significante com glosas fiscais reais ($p = 0,000426$);</li>
    <li><strong>Modelagem Supervisionada de Risco e Custo (HistGradientBoosting, Random Forest, SVR, etc.):</strong> Treinamento de regressores e classificadores sob protocolo estrito de validação temporal <em>Walk-Forward</em> expansivo (2020–2024 treino; 2025–2026 teste) com embargo temporal de 30 dias para mitigação integral de vazamento informacional (*data leakage*);</li>
    <li><strong>Explicabilidade Algorítmica e Auditoria Pericial (XAI — SHAP e LIME):</strong> Avaliação empírica da interpretabilidade local. Demonstrou-se que SHAP e LIME exibem similaridade de Jaccard no Top-5 de apenas 39,29% (divergência de 60,7%), comprovando os alertas de Cynthia Rudin (2019) e fundamentando que aproximações locais de caixa-preta não devem ser usadas isoladamente como prova jurídica punitiva;</li>
    <li><strong>Teoria dos Grafos e Redes Complexas (Algoritmo de Louvain):</strong> Particionamento da malha estadual em 18 ecossistemas mecânicos regionais ($Q = 0,5646$), identificando estruturas espaciais de dependência e fornecimento;</li>
    <li><strong>Otimização Matemática Prescritiva (MILP via Solver HiGHS):</strong> Acoplamento entre previsões de risco e Programação Linear Inteira Mista (Bertsimas & Kallus, 2020). Esclarece-se que o MILP constitui <em>pesquisa operacional exata determinística</em> e não aprendizado de máquina, alcançando 17,51% de economia orçamentária certificada (MIP Gap 0,0000%).</li>
</ul>

<h3>Salvaguardas de Privacidade e Governança de Dados (LGPD)</h3>
<p>
    Os dados operacionais governamentais foram manuseados sob autorização formal da SEA/SC e rigoroso sigilo institucional:
</p>
<ul>
    <li><strong>Pseudonimização Criptográfica:</strong> Todas as placas de viaturas operacionais e identificadores de oficinas credenciadas foram submetidos a hash com chave secreta HMAC-SHA-256;</li>
    <li><strong>Anonimização de Dados Pessoais:</strong> Remoção e ofuscação sistemática de nomes de condutores, matrículas funcionais e dados sensíveis através da biblioteca de conformidade <em>Microsoft Presidio</em>, em estrito atendimento à Lei Federal nº 13.709/2018 (LGPD);</li>
    <li><strong>Ambiente Local Seguro:</strong> Nenhum dado individualizado ou sensível de servidores do Estado foi transmitido a servidores externos ou nuvens comerciais de terceiros.</li>
</ul>

<h3>Princípio da Não-Substituição da Decisão Humana</h3>
<p>
    Os modelos de inteligência artificial desenvolvidos operam exclusivamente como <strong>sistemas de suporte e triagem analítica</strong>. O score de anomalia sinaliza ordens de serviço prioritárias para inspeção humana, jamais aplicando sanções ou glosas automáticas. A decisão administrativa final é sempre privativa e motivada por fiscais e gestores públicos legalmente investidos, em respeito ao Art. 37 da Constituição Federal e à Lei nº 14.133/2021.
</p>

<div class="page-break"></div>

<h2>2. Ferramentas de IA Generativa no Apoio ao Desenvolvimento (Guia UDESC 2025, Formato 2)</h2>
<p>
    Em estrito cumprimento ao <strong>Formato 2 (Tabela de Rastreabilidade e Registro de Prompts)</strong> estabelecido nas Seções 3.3-c e 7 do Guia de IA da UDESC (2025), apresenta-se a discriminação completa de todas as ferramentas de assistência computacional utilizadas durante o desenvolvimento do projeto:
</p>

<table>
    <tr>
        <th style="width: 17%;">Ferramenta</th>
        <th style="width: 15%;">Desenvolvedor</th>
        <th style="width: 12%;">Versão / Modelo</th>
        <th style="width: 16%;">Período de Uso</th>
        <th style="width: 10%;">Pedidos</th>
        <th>Finalidade Técnica Declarada</th>
    </tr>
    <tr>
        <td><strong>Kiro IDE</strong></td>
        <td>Amazon Web Services</td>
        <td>1.4.121<br><small>qdev::auto</small></td>
        <td>08/11/2026 a 17/11/2026</td>
        <td>141</td>
        <td>Análise e correção de erros de sintaxe; escrita e refatoração de scripts de análise de dados, busca bibliográfica automatizada e compilação de relatórios e slides.</td>
    </tr>
    <tr>
        <td><strong>Google Antigravity IDE</strong></td>
        <td>Google DeepMind</td>
        <td>2.1.4<br><small>Gemini Pro/Flash</small></td>
        <td>09/10/2026 a 20/11/2026</td>
        <td>18</td>
        <td>Análise de integridade de código, auditoria de repositório, geração de relatórios formais e compilação de PDFs via WeasyPrint Engine.</td>
    </tr>
    <tr>
        <td><strong>Kilo Code</strong><br><small>(Extensão VS Code)</small></td>
        <td>Kilo Code Inc.</td>
        <td>7.8.27<br><small>kilo-auto/free</small></td>
        <td>28/07/2026 a 11/10/2026</td>
        <td>24</td>
        <td>Correção de scripts de suporte, análise exploratória preliminar e suporte na parametrização da anonimização de dados via Microsoft Presidio.</td>
    </tr>
    <tr>
        <td><strong>GitHub Copilot Chat</strong><br><small>(VS Code)</small></td>
        <td>GitHub / Microsoft</td>
        <td>Copilot Chat<br><small>0.66.0 / 0.69.0</small></td>
        <td>09/10/2026 a 10/10/2026</td>
        <td>24</td>
        <td>Consultas de sintaxe de bibliotecas Python (`scipy`, `pandas`, `weasyprint`) e depuração pontual de exceções de código.</td>
    </tr>
    <tr>
        <td><strong>Gemini Code Assist</strong><br><small>(VS Code)</small></td>
        <td>Google Cloud</td>
        <td>2.107.0<br><small>Autocompletion</small></td>
        <td>Outubro / Novembro de 2026</td>
        <td>—<br><small>(Inline)</small></td>
        <td>Sugestões de autocompletar de código em tempo real diretamente no editor Visual Studio Code (sem histórico local de chat).</td>
    </tr>
    <tr>
        <td><strong>Recursos de IA do Overleaf</strong></td>
        <td>Digital Science</td>
        <td>Serviço Web<br><small>Overleaf Cloud</small></td>
        <td>Novembro de 2026</td>
        <td>—<br><small>(Editorial)</small></td>
        <td>Revisão ortográfica e adequação da estrutura de citações bibliográficas às normas da ABNT no ambiente LaTeX online.</td>
    </tr>
</table>

<p class="no-indent" style="font-size: 8.5pt; color: #64748b; font-style: italic;">
    Nota de Rastreabilidade: Os registros integrais dos prompts submetidos pelo autor, com data, hora e conteúdo devidamente expurgado de dados confidenciais e credenciais, encontram-se arquivados em <code>docs/registro_uso_ia/prompts/</code>, auditáveis por script de verificação automática.
</p>

<h2>3. Declaração Negativa de Integridade Científica (O que as Ferramentas NÃO Fizeram)</h2>
<div class="box-negativa">
    <strong>GARANTIAS DE AUTENTICIDADE E ORIGINALIDADE DOS DADOS E RESULTADOS:</strong><br>
    Para resguardar de maneira inequívoca a idoneidade acadêmica da dissertação perante a banca examinadora do PPGCAP/UDESC, a CAPES e a comunidade científica, o autor e seus orientadores atestam taxativamente que:
    <ol style="margin-top: 4px; margin-bottom: 0;">
        <li><strong>NÃO houve geração sintética ou artificial de dados:</strong> Todos os 350.737 registros de ordens de serviço, R$ 138,76 milhões em dispêndios liquidados e R$ 60,05 milhões em glosas decorrem estritamente da base oficial do Poder Executivo de Santa Catarina;</li>
        <li><strong>NÃO houve fabricação de resultados analíticos:</strong> Todas as tabelas, métricas estatísticas (MAE, RMSE, ROC-AUC, p-valores, intervalos de confiança) e matrizes de sensibilidade do MILP foram calculadas de forma determinística por código Python sobre dados brutos;</li>
        <li><strong>NÃO houve geração de figuras ou gráficos por modelos generativos de difusão/imagem:</strong> Todas as 97 figuras da dissertação foram renderizadas programaticamente via bibliotecas científicas (`matplotlib`, `seaborn`, `networkx`);</li>
        <li><strong>NÃO houve formulação ou ajuste a posteriori de hipóteses (*HARKing* ou *p-hacking*):</strong> As quatro hipóteses centrais (H1 a H4) e o critério de corte de 15,0% de relevância prática foram pré-estabelecidos sob o Método Lógico de Gilson Volpato, resultando no falseamento transparente e na rejeição honesta de H1 e H4;</li>
        <li><strong>NÃO houve substituição da leitura e conferência crítica da literatura:</strong> As 40 obras do referencial teórico e os 546 textos completos da base de artigos foram conferidos contra os metadados oficiais registrados no Crossref e OpenAlex.</li>
    </ol>
</div>

<h2>4. Termo de Compromisso e Responsabilidade Integral do Autor</h2>
<div class="box-responsabilidade">
    <strong>DECLARAÇÃO FORMAL DE AUTORIA E RESPONSABILIDADE:</strong><br>
    Declaro, sob as penas da lei e das normas acadêmicas da Universidade do Estado de Santa Catarina, que revisei integralmente todo o código-fonte, dados, tabelas, figuras, interpretações e textos produzidos ou auxiliados por ferramentas computacionais e assistentes de inteligência artificial. Assumo responsabilidade integral e irrestrita pelo conteúdo, pela originalidade intelectual, pelas conclusões e pela integridade de todo o material que compõe a presente Dissertação de Mestrado.
</div>

<p class="no-indent" style="text-align: right; margin-top: 15px; font-weight: bold; color: #334155;">
    Florianópolis / Joinville (SC), 20 de novembro de 2026.
</p>

<div class="assinaturas-container">
    <div class="linha-assinatura">
        <div class="campo-assinatura">
            <div class="traco"></div>
            <strong>EDUARDO LOPES JONKER</strong><br>
            Autor / Mestrando PPGCAP<br>
            <small style="color:#64748b">Engenheiro de Software — SEA/SC</small>
        </div>
        <div class="campo-assinatura">
            <div class="traco"></div>
            <strong>PROFA. DRA. VIVIAN KREMER KALEMPA</strong><br>
            Orientadora de Mestrado<br>
            <small style="color:#64748b">CCT / PPGCAP / UDESC</small>
        </div>
    </div>
    <div class="linha-assinatura" style="justify-content: center; margin-top: 25px;">
        <div class="campo-assinatura" style="width: 55%;">
            <div class="traco"></div>
            <strong>PROF. DR. YURI KASZUBOWSKI LOPES</strong><br>
            Coorientador de Mestrado<br>
            <small style="color:#64748b">CCT / PPGCAP / UDESC</small>
        </div>
    </div>
</div>

</body>
</html>
"""

def compilar_declaracao_pdf():
    print("=" * 75)
    print("COMPILAÇÃO DA DECLARAÇÃO DE USO ÉTICO DE IA EM PDF (PPGCAP/UDESC)")
    print("Autor: Eduardo Lopes Jonker")
    print("=" * 75)

    print("1. Gravando arquivo HTML estruturado...")
    HTML_FILE.write_text(HTML_CONTENT, encoding="utf-8")
    print(f"✓ HTML salvo em: {HTML_FILE}")

    # Nomes dos arquivos PDF de saída
    pdf_solicitado = ROOT / "declaraçãode uso de ia.pdf"
    pdf_com_espaco = ROOT / "declaração de uso de ia.pdf"
    pdf_normalizado = ROOT / "declaracao_de_uso_de_ia.pdf"
    pdf_relatorios = PDF_DIR / "declaracao_de_uso_de_ia.pdf"
    pdf_documentos = DOCS_DIR / "declaracao_de_uso_de_ia.pdf"

    print("2. Renderizando PDF oficial com motor WeasyPrint...")
    weasyprint.HTML(string=HTML_CONTENT, base_url=str(ROOT)).write_pdf(pdf_solicitado)
    tamanho_kb = pdf_solicitado.stat().st_size / 1024
    print(f"✓ PDF gerado com sucesso: {pdf_solicitado.name} ({tamanho_kb:.1f} KB)")

    print("3. Criando cópias espelhadas de padronização...")
    shutil.copy2(pdf_solicitado, pdf_com_espaco)
    shutil.copy2(pdf_solicitado, pdf_normalizado)
    shutil.copy2(pdf_solicitado, pdf_relatorios)
    shutil.copy2(pdf_solicitado, pdf_documentos)

    print(f"✓ Cópia espelhada em: {pdf_com_espaco.name}")
    print(f"✓ Cópia espelhada em: {pdf_normalizado.name}")
    print(f"✓ Cópia espelhada em: {pdf_relatorios.relative_to(ROOT)}")
    print(f"✓ Cópia espelhada em: {pdf_documentos.relative_to(ROOT)}")

    print("=" * 75)
    print("DECLARAÇÃO DE USO ÉTICO DE IA CONCLUÍDA COM 100% DE SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    compilar_declaracao_pdf()

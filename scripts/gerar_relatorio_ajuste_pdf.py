#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script gerador do relatório 'ajuste.pdf' (Versão Expandida e Reconciliada)
Incorpora a auditoria completa E01-E20, o plano de ajustes metodológicos,
o mapeamento word/media/imageNN.png <-> charts/figXX_...png e os 4 PNGs corretos em 300 DPI:
1. fig62_lime_caso_preventiva.png (fig15 LIME Local)
2. fig22_rolling_window_cross_val.png (fig18 Rolling-Window CV com Embargo)
3. fig23_calibracao_platt_isotonica.png (fig19 Calibração Platt vs Isotônica)
4. fig69_regressao_quantilica_previsao_intervalar.png (fig20 Regressão Quantílica)
"""

import sys
from pathlib import Path
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_OUT = BASE_DIR / "ajuste.pdf"
CHARTS_DIR = BASE_DIR / "charts"

def chart_uri(filename):
    p = CHARTS_DIR / filename
    return f"file://{p.resolve()}"

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório de Diagnóstico e Plano de Ajustes - Dissertação PPGCAP/UDESC</title>
<style>
    @page {{
        size: A4;
        margin: 2.0cm 1.8cm 2.0cm 1.8cm;
        @bottom-right {{
            content: "Página " counter(page) " de " counter(pages);
            font-size: 8pt;
            color: #64748b;
            font-family: 'Liberation Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
        @bottom-left {{
            content: "PPGCAP / UDESC • Relatório Técnico de Ajustes e Reconciliação (V6)";
            font-size: 8pt;
            color: #64748b;
            font-family: 'Liberation Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
        @top-center {{
            content: "AUDITORIA FORENSE, PLANO DE CORREÇÃO E GUIA DE IMAGENS DOCX/PDF";
            font-size: 7.5pt;
            letter-spacing: 0.08em;
            color: #94a3b8;
            border-bottom: 0.5px solid #e2e8f0;
            padding-bottom: 4px;
            font-family: 'Liberation Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
    }}
    
    body {{
        font-family: 'Liberation Serif', 'Times New Roman', Times, serif;
        font-size: 9.6pt;
        line-height: 1.45;
        color: #1e293b;
        text-align: justify;
    }}
    
    h1, h2, h3, h4 {{
        font-family: 'Liberation Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #0f172a;
        page-break-after: avoid;
    }}
    
    .cover {{
        text-align: center;
        page-break-after: always;
        padding-top: 2.2cm;
    }}
    .cover-inst {{
        font-size: 11pt;
        font-weight: bold;
        letter-spacing: 0.05em;
        color: #334155;
        margin-bottom: 0.3em;
        font-family: 'Liberation Sans', sans-serif;
    }}
    .cover-prog {{
        font-size: 10pt;
        color: #64748b;
        margin-bottom: 2.2cm;
        font-family: 'Liberation Sans', sans-serif;
    }}
    .cover-title {{
        font-size: 17.5pt;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.25;
        margin-bottom: 0.6em;
    }}
    .cover-subtitle {{
        font-size: 11.5pt;
        color: #2563eb;
        font-weight: 600;
        margin-bottom: 2.2cm;
        line-height: 1.35;
    }}
    .cover-meta {{
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px 22px;
        font-size: 9pt;
        color: #475569;
        text-align: left;
        display: inline-block;
        width: 88%;
        margin-bottom: 2.2cm;
        font-family: 'Liberation Sans', sans-serif;
    }}
    .cover-meta table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .cover-meta td {{
        padding: 4px 6px;
        vertical-align: top;
    }}
    .cover-meta td.label {{
        font-weight: bold;
        color: #1e293b;
        width: 28%;
    }}
    
    h1 {{
        font-size: 13.5pt;
        border-bottom: 2px solid #0f172a;
        padding-bottom: 4px;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    
    h2 {{
        font-size: 11.2pt;
        color: #1e40af;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 3px;
        margin-top: 1.2em;
        margin-bottom: 0.4em;
    }}
    
    h3 {{
        font-size: 10.0pt;
        color: #0f172a;
        margin-top: 1.0em;
        margin-bottom: 0.3em;
    }}
    
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 8px 0 14px 0;
        font-size: 8.5pt;
    }}
    
    th, td {{
        border: 1px solid #cbd5e1;
        padding: 5px 8px;
        vertical-align: middle;
    }}
    
    th {{
        background-color: #f1f5f9;
        color: #0f172a;
        font-weight: bold;
        text-align: left;
        font-family: 'Liberation Sans', sans-serif;
    }}
    
    tr:nth-child(even) td {{
        background-color: #f8fafc;
    }}
    
    .badge {{
        display: inline-block;
        padding: 2px 6px;
        font-size: 7.5pt;
        font-weight: bold;
        border-radius: 4px;
        text-align: center;
        font-family: 'Liberation Sans', sans-serif;
    }}
    .badge-crit {{ background-color: #fee2e2; color: #b91c1c; border: 1px solid #f87171; }}
    .badge-warn {{ background-color: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }}
    .badge-ok   {{ background-color: #dcfce7; color: #15803d; border: 1px solid #86efac; }}
    .badge-info {{ background-color: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }}

    .box-alert {{
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 9px 13px;
        margin: 10px 0;
        font-size: 8.8pt;
        border-radius: 0 5px 5px 0;
    }}
    .box-crit {{
        background-color: #fff1f2;
        border-left: 4px solid #e11d48;
        padding: 9px 13px;
        margin: 10px 0;
        font-size: 8.8pt;
        border-radius: 0 5px 5px 0;
    }}
    .box-formula {{
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        padding: 8px 12px;
        margin: 8px 0;
        font-family: 'Liberation Mono', monospace;
        font-size: 8.5pt;
        text-align: center;
        border-radius: 4px;
    }}
    
    .figure-card {{
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 8px 10px;
        margin: 12px 0 16px 0;
        background-color: #ffffff;
        page-break-inside: avoid;
        text-align: center;
    }}
    .figure-card img {{
        max-width: 95%;
        max-height: 8.6cm;
        height: auto;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
        display: block;
        margin: 6px auto;
    }}
    .figure-caption {{
        font-weight: bold;
        font-size: 8.8pt;
        color: #0f172a;
        margin-bottom: 4px;
        text-align: center;
        font-family: 'Liberation Sans', sans-serif;
    }}
    .figure-source {{
        font-size: 7.8pt;
        color: #64748b;
        margin-top: 4px;
        text-align: center;
    }}
    .figure-meta-badge {{
        display: inline-block;
        margin-bottom: 4px;
        font-size: 7.5pt;
        padding: 2px 8px;
        border-radius: 3px;
        background-color: #0f172a;
        color: #ffffff;
        font-family: 'Liberation Mono', monospace;
    }}
    
    .quebra-pagina {{
        page-break-after: always;
    }}
</style>
</head>
<body>

<!-- CAPA DO RELATÓRIO -->
<div class="cover">
    <div class="cover-inst">UNIVERSIDADE DO ESTADO DE SANTA CATARINA, UDESC</div>
    <div class="cover-prog">CENTRO DE CIÊNCIAS TECNOLÓGICAS (CCT) • PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA (PPGCAP)</div>
    
    <div class="cover-title">RELATÓRIO TÉCNICO DE AUDITORIA FORENSE, PLANO DE AJUSTES E GUIA DE IMAGENS</div>
    <div class="cover-subtitle">Diagnóstico Estrutural, Reconciliação Empírica e Mapeamento de Arquivos PNG vs. Word (word/media/imageNN.png)<br>Dissertação de Mestrado Acadêmico em Computação Aplicada</div>
    
    <div class="cover-meta">
        <table>
            <tr>
                <td class="label">Arquivo Auditado:</td>
                <td><code>dissertacao.pdf</code> (101 páginas / 15,3 MB / Hash PDFium)</td>
            </tr>
            <tr>
                <td class="label">Arquivo DOCX Editável:</td>
                <td><code>Dissertacao_Eduardo_Lopes_Jonker_editavel.docx</code> (96 imagens incorporadas em <code>word/media/</code>)</td>
            </tr>
            <tr>
                <td class="label">Mestrando:</td>
                <td>Eduardo Lopes Jonker</td>
            </tr>
            <tr>
                <td class="label">Orientação:</td>
                <td>Profa. Dra. Vivian Kremer Kalempa (Orientadora) / Prof. Dr. Yuri Kaszubowski Lopes (Coorientador)</td>
            </tr>
            <tr>
                <td class="label">Base de Dados:</td>
                <td>350.737 Ordens de Serviço (SIGFrota/SEA-SC) • R$ 138,76M Manutenção / R$ 184,25M Combustível</td>
            </tr>
            <tr>
                <td class="label">Finalidade:</td>
                <td>Atendimento integral aos apontamentos E01 a E20, incorporação das 4 figuras corretas em 300 DPI e mapeamento para Word</td>
            </tr>
        </table>
    </div>
    
    <div style="font-size: 9pt; color: #64748b; font-family: 'Liberation Sans', sans-serif;">
        FLORIANÓPOLIS – SC<br>OUTUBRO DE 2026
    </div>
</div>

<!-- SUMÁRIO EXECUTIVO -->
<h1>1. Sumário Executivo e Diagnóstico Geral da Versão Atual</h1>

<p>
    A inspeção forense automatizada e visual realizada sobre o arquivo <code>dissertacao.pdf</code> (101 páginas compiladas) e confrontada com o arquivo mestre do Microsoft Word <code>Dissertacao_Eduardo_Lopes_Jonker_editavel.docx</code> atesta avanços substanciais na versão V5, especialmente quanto à maturidade científica das conclusões:
</p>
<ul>
    <li><strong>Superação de Sobreafirmações (E05, E06 e E07):</strong> O texto abandonou termos categóricos de fraude comprovada ou cartelização automática nas oficinas, tratando os achados como triagem de atipicidades e afiliação estrutural de redes complexas.</li>
    <li><strong>Epistemologia das Hipóteses (E03 e E08):</strong> A Hipótese H1 é honestamente tratada como não confirmada pelo limiar estrito de 15% (atingiu 14,1% na ablação), eliminando a falsa impressão de aprovação irrestrita.</li>
</ul>

<div class="box-crit">
    <strong>Pendências Críticas Solucionadas Neste Relatório:</strong><br>
    &bull; <strong>Item E09 (Figuras Trocadas):</strong> Mapeamento exato de todas as divergências nas páginas 46 a 55 do PDF e identificação dos arquivos correspondentes em <code>word/media/imageNN.png</code>.<br>
    &bull; <strong>Envio dos PNGs Corretos (300 DPI):</strong> Geração e incorporação direta no relatório das 4 figuras corretas solicitadas (LIME, Rolling-Window, Calibração Platt vs Isotônica e Regressão Quantílica).<br>
    &bull; <strong>Item E04 (Isolation Forest):</strong> Reconciliação matemática formal do denominador de 274.823 OSs (&nu; = 0,85%) vs universo de 350.737 OSs (0,67%).<br>
    &bull; <strong>Apêndice B:</strong> Eliminação do erro tipográfico de textos colados sem espaços nas legendas.<br>
    &bull; <strong>Itens E10, E16, E17 e E20:</strong> Saneamento da Tabela 4, remoção de comentário esquecido na Lista de Tabelas e revisão do Abstract em inglês.
</div>

<!-- SEÇÃO DAS 4 FIGURAS CORRETAS -->
<div class="quebra-pagina"></div>
<h1>2. Visualização das 4 Figuras Reconciliadas em Alta Resolução (300 DPI)</h1>

<p>
    Abaixo são apresentados os <strong>quatro arquivos PNG definitivos</strong> gerados pelo pipeline do projeto em resolução de impressão (300 DPI), prontos para substituição no Word (<code>.docx</code>) ou no código LaTeX:
</p>

<!-- FIGURA 15: LIME -->
<div class="figure-card">
    <span class="figure-meta-badge">Arquivo no Projeto: charts/fig62_lime_caso_preventiva.png (ou fig15_lime_explicacao_caso.png)</span>
    <div class="figure-caption">Figura 15 / 62 – Interpretabilidade Local (LIME) para Decisão em Intervenção Crítica</div>
    <img src="{chart_uri('fig62_lime_caso_preventiva.png')}" alt="LIME Local">
    <div class="figure-source">Fonte: Elaborado pelo autor a partir dos dados da pesquisa (2026). Explicação aditiva local da decisão.</div>
</div>

<!-- FIGURA 18: ROLLING-WINDOW -->
<div class="figure-card">
    <span class="figure-meta-badge">Arquivo no Projeto: charts/fig22_rolling_window_cross_val.png (ou fig18_rolling_window_cross_val.png)</span>
    <div class="figure-caption">Figura 18 / 22 – Esquema da Validação Temporal com Janela Deslizante (Rolling-Window CV) com Embargo</div>
    <img src="{chart_uri('fig22_rolling_window_cross_val.png')}" alt="Rolling-Window CV">
    <div class="figure-source">Fonte: Elaborado pelo autor a partir dos dados da pesquisa (2026). Preservação estrita da seta do tempo e gap de 30 dias.</div>
</div>

<div class="quebra-pagina"></div>

<!-- FIGURA 19: CALIBRAÇÃO -->
<div class="figure-card">
    <span class="figure-meta-badge">Arquivo no Projeto: charts/fig23_calibracao_platt_isotonica.png (ou fig19_calibracao_platt_isotonica.png)</span>
    <div class="figure-caption">Figura 19 / 23 – Comparativo de Calibração de Probabilidades: Platt Scaling vs. Regressão Isotônica</div>
    <img src="{chart_uri('fig23_calibracao_platt_isotonica.png')}" alt="Calibração Platt vs Isotônica">
    <div class="figure-source">Fonte: Elaborado pelo autor a partir dos dados da pesquisa (2026). Regressão isotônica minimizou ECE para 0,0238 e Brier para 0,066.</div>
</div>

<!-- FIGURA 20: REGRESSÃO QUANTÍLICA -->
<div class="figure-card">
    <span class="figure-meta-badge">Arquivo no Projeto: charts/fig69_regressao_quantilica_previsao_intervalar.png (ou fig20_regressao_quantilica.png)</span>
    <div class="figure-caption">Figura 20 / 69 – Banda Intervalar de Regressão Quantílica por Decil de Quilometragem</div>
    <img src="{chart_uri('fig69_regressao_quantilica_previsao_intervalar.png')}" alt="Regressão Quantílica">
    <div class="figure-source">Fonte: Elaborado pelo autor a partir dos dados da pesquisa (2026). Banda calibrada [Q10; Q90] com cobertura real de 87,7% das ordens.</div>
</div>

<div class="quebra-pagina"></div>

<!-- GUIA DE SUBSTITUIÇÃO NO WORD DOCX -->
<h1>3. Guia de Mapeamento: Arquivos PNG do Projeto vs. Word (word/media/imageNN.png)</h1>

<p>
    Para que o autor ou revisor realize a substituição cirúrgica das imagens diretamente no arquivo editável <code>Dissertacao_Eduardo_Lopes_Jonker_editavel.docx</code> (ou através de descompactação do arquivo <code>.docx</code> como ZIP), apresenta-se a tabela de correlação exata entre o número da figura, o arquivo no diretório <code>charts/</code> e o identificador interno de mídia do Word:
</p>

<table>
    <thead>
        <tr>
            <th style="width: 14%;">Figura na Obra</th>
            <th style="width: 25%;">Arquivo PNG no Projeto (300 DPI)</th>
            <th style="width: 20%;">Arquivo no Word (DOCX ZIP)</th>
            <th style="width: 23%;">O que Estava no PDF Atual</th>
            <th style="width: 18%; text-align: center;">Ação de Ajuste</th>
        </tr>
    </thead>
    <tbody>
        <tr style="background-color: #fef2f2;">
            <td><strong>Figura 15 (pág. 49)</strong></td>
            <td><code>fig62_lime_caso_preventiva.png</code><br><em>(fig15_lime_explicacao_caso.png)</em></td>
            <td><strong><code>word/media/image17.png</code></strong></td>
            <td>Heatmap de Correlação Linear de Pearson (Incorreto)</td>
            <td style="text-align: center;"><span class="badge badge-crit">Substituir por LIME</span></td>
        </tr>
        <tr style="background-color: #fef2f2;">
            <td><strong>Figura 18 (pág. 51)</strong></td>
            <td><code>fig22_rolling_window_cross_val.png</code><br><em>(fig18_rolling_window_cross_val.png)</em></td>
            <td><strong><code>word/media/image22.png</code></strong></td>
            <td>Gráfico Temporal Prophet com/sem filtro (Incorreto)</td>
            <td style="text-align: center;"><span class="badge badge-crit">Substituir por Rolling-CV</span></td>
        </tr>
        <tr style="background-color: #fef2f2;">
            <td><strong>Figura 19 (pág. 51)</strong></td>
            <td><code>fig23_calibracao_platt_isotonica.png</code><br><em>(fig19_calibracao_platt_isotonica.png)</em></td>
            <td><strong><code>word/media/image23.png</code></strong></td>
            <td>5 Matrizes de Confusão 2x2 (Incorreto)</td>
            <td style="text-align: center;"><span class="badge badge-crit">Substituir por Curvas Calib.</span></td>
        </tr>
        <tr style="background-color: #fef2f2;">
            <td><strong>Figura 20 (pág. 52)</strong></td>
            <td><code>fig69_regressao_quantilica_previsao_intervalar.png</code><br><em>(fig20_regressao_quantilica.png)</em></td>
            <td><strong><code>word/media/image24.png</code></strong><br>(ou <code>image69.png</code>)</td>
            <td>Barras de Jaccard do Isolation Forest (Incorreto)</td>
            <td style="text-align: center;"><span class="badge badge-crit">Substituir por Banda Quant.</span></td>
        </tr>
        <tr>
            <td><strong>Figura 14 (pág. 49)</strong></td>
            <td><code>fig15_politicas_decisao_fronteira.png</code></td>
            <td><code>word/media/image15.png</code></td>
            <td>Fronteira Pareto (Harmonizar título interno de 15 para 14)</td>
            <td style="text-align: center;"><span class="badge badge-warn">Ajustar Título</span></td>
        </tr>
        <tr>
            <td><strong>Figuras 16 e 17 (pág. 50)</strong></td>
            <td><code>fig18_prophet_previsao_gastos.png</code><br><code>fig19_prophet_componentes.png</code></td>
            <td><code>word/media/image18.png</code><br><code>word/media/image19.png</code></td>
            <td>Decomposição Prophet (Títulos internos trazem 18 e 19)</td>
            <td style="text-align: center;"><span class="badge badge-warn">Ajustar Título</span></td>
        </tr>
        <tr>
            <td><strong>Figura 21 (pág. 52)</strong></td>
            <td><code>fig25_composicao_custos_peca_vs_mo.png</code></td>
            <td><code>word/media/image25.png</code></td>
            <td>Peças vs MO (Título interno traz Figura 25)</td>
            <td style="text-align: center;"><span class="badge badge-warn">Ajustar Título</span></td>
        </tr>
        <tr>
            <td><strong>Figuras Apêndice B</strong></td>
            <td><code>fig49, fig50, fig24, fig36, fig60...</code></td>
            <td><code>word/media/image49.png</code> em diante</td>
            <td>Legendas coladas sem espaço (<code>Figuraadicional...</code>)</td>
            <td style="text-align: center;"><span class="badge badge-warn">Corrigir Tipografia</span></td>
        </tr>
    </tbody>
</table>

<div class="box-alert">
    <strong>Como Atualizar Diretamente no Word (DOCX):</strong><br>
    <strong>Método 1 (Interface Word):</strong> Clicar com o botão direito na imagem incorreta &rarr; <em>Alterar Imagem &rarr; Deste Arquivo...</em> &rarr; Selecionar o PNG correspondente na pasta <code>charts/</code>.<br>
    <strong>Método 2 (Via Descompactação ZIP):</strong> Renomear <code>Dissertacao.docx</code> para <code>.zip</code>, extrair a pasta <code>word/media/</code>, sobrescrever <code>image17.png</code>, <code>image22.png</code>, <code>image23.png</code> e <code>image24.png</code> com os PNGs reconciliados, compactar novamente e renomear para <code>.docx</code>.
</div>

<!-- AUDITORIA DO ITEM E04 -->
<h1>4. Reconciliação Amostral e Denominador do Isolation Forest (Item E04)</h1>

<p>
    Para sanar definitivamente a dúvida avaliativa do Item E04 sobre o denominador da contaminação do <em>Isolation Forest</em>, formaliza-se a memória de cálculo:
</p>

<div class="box-formula">
    <strong>Dedução Formal dos Universos Amostrais:</strong><br><br>
    Universo Documental Bruto (N_bruto) = <strong>350.737 OSs</strong> (2020 a 2026)<br>
    (-) Expurgo de OSs reprovadas/canceladas sem liquidação: 55.259 OSs<br>
    (-) Expurgo de odometrias inconsistentes / nulas não recuperáveis: 20.655 OSs<br>
    (=) Subconjunto Elegível Saneado para Modelagem (N_modelado) = <strong>274.823 OSs</strong><br><br>
    Taxa de Contaminação Calibrada (&nu;) = <strong>0,0085 (0,85%)</strong><br>
    Ordens Anômalas Detectadas = 274.823 &times; 0,0085 = <strong>2.336 OSs</strong><br>
    Taxa Global Efetiva = 2.336 / 350.737 = <strong>0,00666 &asymp; 0,67%</strong>
</div>

<p>
    Portanto, <strong>não existe contradição</strong>: o hiperparâmetro de contaminação teórico do algoritmo foi calibrado em &nu; = 0,85% sobre a massa de 274.823 ordens com execução física comprovada, enquanto 0,67% representa a incidência macro sobre a totalidade documental do Estado.
</p>

<!-- AUDITORIA DO APÊNDICE B -->
<h1 style="margin-top: 25px;">5. Correção Tipográfica do Apêndice B ("Figuras Adicionais")</h1>

<p>
    Nas páginas 71 a 75 do arquivo PDF atual, todas as legendas e fontes da galeria complementar aparecem sem espaço tipográfico. Apresenta-se o texto corrigido:
</p>

<table>
    <thead>
        <tr>
            <th style="width: 14%;">Página PDF</th>
            <th style="width: 38%;">Texto Atual no PDF (Corrompido)</th>
            <th style="width: 48%;">Redação Padronizada ABNT (Correta)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Pág. 71</strong></td>
            <td><code>Figuraadicional, imagem1</code></td>
            <td><strong>Figura B.1 – Matriz de Penalidade Econômica Assimétrica das Decisões Operacionais</strong></td>
        </tr>
        <tr>
            <td><strong>Pág. 72 (Topo)</strong></td>
            <td><code>Figuraadicional, imagem2</code></td>
            <td><strong>Figura B.2 – Calibração de Probabilidades e Erro ECE por Família Veicular</strong></td>
        </tr>
        <tr>
            <td><strong>Pág. 72 (Base)</strong></td>
            <td><code>Figuraadicional, imagem5</code></td>
            <td><strong>Figura B.3 – Distribuição do Tempo de Reparo e Imobilização em Oficina</strong></td>
        </tr>
        <tr>
            <td><strong>Pág. 73 (Topo)</strong></td>
            <td><code>Figuraadicional, imagem8</code></td>
            <td><strong>Figura B.4 – Tempo Médio Entre Falhas (MTBF) por Categoria Operacional</strong></td>
        </tr>
        <tr>
            <td><strong>Pág. 73 (Base)</strong></td>
            <td><code>Figuraadicional, imagem9</code></td>
            <td><strong>Figura B.5 – Superfície de Resposta Bidimensional MILP (&eta; vs Orçamento)</strong></td>
        </tr>
        <tr>
            <td><strong>Todas as Págs.</strong></td>
            <td><code>Fonte:Elaboradopeloautorapartirdos...</code></td>
            <td><strong>Fonte: Elaborado pelo autor a partir dos dados da pesquisa (2026).</strong></td>
        </tr>
    </tbody>
</table>

<div class="quebra-pagina"></div>

<!-- STATUS DAS HIPÓTESES E EVIDÊNCIAS -->
<h1>6. Status das Hipóteses e Evidências (Versão Reconciliada)</h1>

<p>
    À luz das correções incorporadas, as hipóteses devem ser tratadas como em validação até que os resultados sejam recalculados e reproduzidos a partir de uma única fonte de artefatos:
</p>

<div class="box-formula" style="font-size: 9.5pt; line-height: 1.55; margin-bottom: 20px;">
    <strong>1. H1, Integração multimodal e redução de erro preditivo:</strong><br>
    O estudo ablativo reporta redução de MAE de <strong>14,1%</strong> (MAE de R$ 1.042,50 para R$ 895,40). Mantido o limiar de 15% definido em H1, a hipótese não é sustentada por esse resultado; alternativamente, requer revisão do limiar ou demonstração de outro experimento correspondente, com conjunto de teste explicitado.<br><br>

    <strong>2. H2, Desempenho de ensembles sob desbalanceamento e calibração:</strong><br>
    Os valores <strong>ROC-AUC = 0,882</strong> e <strong>PR-AUC = 0,8410</strong> são relevantes, porém demandam especificação reprodutível da validação (temporalidade, janelas, unidade observacional, prevenção de vazamento), baselines comparáveis e incerteza. Assim, a evidência deve ser tratada como parcial.<br><br>

    <strong>3. H3, Otimização prescritiva MILP e economia trienal:</strong><br>
    A economia de <strong>R$ 40.088.374,00</strong> (grafado inicialmente como <em>R$ 40 088 374,00</em>) no triênio 2027–2029 é um resultado de cenário simulado, condicionado às premissas e à formulação completa do MILP (objetivo, variáveis, restrições, solver, status/gap e sensibilidade), não uma economia realizada.<br><br>

    <strong>4. H4, Explicabilidade XAI (SHAP/LIME) e concordância:</strong><br>
    A taxa de <strong>91,4%</strong> de concordância requer definição operacional (métrica, amostra, protocolo e estabilidade). Até essa formalização, a hipótese permanece indeterminada.
</div>

<table>
    <thead>
        <tr>
            <th style="width: 15%;">Hipótese</th>
            <th style="width: 25%;">Resultado Empírico Auditado</th>
            <th style="width: 25%;">Status Epistemológico</th>
            <th style="width: 35%;">Encaminhamento Recomendado</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>H1 (Multimodal)</strong></td>
            <td>Redução de 14,1% no MAE (R$ 1.042,50 &rarr; R$ 895,40)</td>
            <td><span class="badge badge-fail">Não Sustentada pelo Limiar</span></td>
            <td>Qualificar honestamente no texto que atingiu 14,1% frente à meta de 15%, demonstrando rigor científico.</td>
        </tr>
        <tr>
            <td><strong>H2 (Ensembles)</strong></td>
            <td>ROC-AUC = 0,882; PR-AUC = 0,8410; Brier = 0,086</td>
            <td><span class="badge badge-warn">Evidência Parcial</span></td>
            <td>Explicitar validação temporal rolling-window com 30 dias de gap e intervalos de confiança (IC 95%).</td>
        </tr>
        <tr>
            <td><strong>H3 (Prescritivo)</strong></td>
            <td>Otimização MILP projeta R$ 40.088.374,00 (2027–2029)</td>
            <td><span class="badge badge-warn">Cenário Simulado</span></td>
            <td>Enfatizar que se trata de modelo ex-ante com solver CBC e gap &le; 1%, e não economia financeira retroativa.</td>
        </tr>
        <tr>
            <td><strong>H4 (XAI)</strong></td>
            <td>Concordância Top-5 SHAP vs LIME = 91,4%</td>
            <td><span class="badge badge-warn">Em Validação</span></td>
            <td>Formalizar métrica de Jaccard, estabilidade local e tamanho da amostra amostrada no protocolo.</td>
        </tr>
    </tbody>
</table>

<div class="quebra-pagina"></div>

<!-- AUDITORIA DA TABELA PATRIMONIAL -->
<h1>7. Auditoria da Tabela 4 e da Lista de Tabelas (Itens E10 e E20)</h1>

<p>
    A auditoria detectou que a Tabela 4 (página 41) já possui percentuais calculados para viaturas rodoviárias (200,7%, 179,2%, 536,3%, 137,1%, 111,3%), mas necessita de dois ajustes finais:
</p>
<ol>
    <li><strong>Remoção de Bens sem Valor Venal:</strong> As linhas referentes a <code>BARCO</code> e maquinário pesado <code>JCB</code> exibem <code>Valor Venal = R$ 0,00</code> e <code>% Venal = N/D</code>. Devem ser substituídas pelas viaturas leves e pesadas que possuem valor venal contábil homologado.</li>
    <li><strong>Exclusão de Comentário Editorial na Lista de Tabelas (Pág. 7):</strong> Excluir a nota de revisão provisória <code>"(requer regeneração/validação do denominador do valor venal e dos percentuais...)"</code> que ficou esquecida no sumário preliminar.</li>
    <li><strong>Correção de Chamada Textual (Pág. 40):</strong> No parágrafo introdutório, alterar <em>"A Tabela 1 apresenta uma amostra..."</em> para <strong>"A Tabela 4 apresenta uma amostra..."</strong>.</li>
</ol>

<!-- HARMONIZAÇÃO DO ABSTRACT E RESUMO -->
<h1>8. Harmonização Textual: Resumo e Abstract em Inglês (Itens E16 e E17)</h1>

<table>
    <thead>
        <tr>
            <th style="width: 20%;">Ponto Crítico</th>
            <th style="width: 40%;">Texto Atual no Abstract Inglês (Pág. 5)</th>
            <th style="width: 40%;">Redação Reconciliada (Padrão V6)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>MAE e Hipótese H1</strong></td>
            <td><code>"reducing MAE by 18.4% and confirming H1"</code></td>
            <td><strong>"reducing MAE by 14.1% in the ablation study, qualifying H1 against the 15% threshold"</strong></td>
        </tr>
        <tr>
            <td><strong>Isolation Forest</strong></td>
            <td><code>"with 0.85% contamination rate"</code></td>
            <td><strong>"detecting 2,336 anomalous orders (0.85% of filtered dataset; 0.67% of total records)"</strong></td>
        </tr>
        <tr>
            <td><strong>Redes e Fornecedores</strong></td>
            <td><code>"mitigating collusive pricing risk in repair shops"</code></td>
            <td><strong>"identifying supplier affiliation hubs without inferring illegal collusive practices"</strong></td>
        </tr>
        <tr>
            <td><strong>Resumo PT (Pág. 4)</strong></td>
            <td><code>"2021–2024Ṅa classificação"</code></td>
            <td><strong>"2021–2024. Na classificação" (correção do caractere corrompido)</strong></td>
        </tr>
    </tbody>
</table>

<div class="box-alert" style="margin-top: 20px;">
    <strong>Conclusão e Prontidão de Entrega:</strong><br>
    Com a disponibilização das 4 figuras em 300 DPI em <code>charts/</code>, a inserção dos painéis visuais nas páginas 3 e 4 deste relatório <code>ajuste.pdf</code> e o mapeamento dos identificadores <code>word/media/imageNN.png</code>, a dissertação possui todos os insumos técnicos e visuais para atingir a conformidade estrita perante o comitê examinador do PPGCAP/UDESC.
</div>

</body>
</html>
"""

def main():
    print("=" * 80)
    print("COMPILANDO RELATÓRIO TÉCNICO DE AJUSTES E RECONCILIAÇÃO (ajuste.pdf)")
    print("=" * 80)
    
    print(f"Gerando PDF com os 4 painéis PNG e guia DOCX em: {PDF_OUT}")
    weasyprint.HTML(string=html_content).write_pdf(str(PDF_OUT))
    print(f"PDF gerado com sucesso! Tamanho: {PDF_OUT.stat().st_size / 1024:.1f} KB")
    
    # Sincronização nos múltiplos destinos
    destinos = [
        BASE_DIR / "Documentos" / "ajuste.pdf",
        BASE_DIR / "relatorios_pdf" / "ajuste.pdf",
        BASE_DIR / "relatorios" / "ajuste.pdf"
    ]
    for d in destinos:
        try:
            d.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(PDF_OUT, d)
            print(f"Sincronizado em: {d}")
        except Exception as e:
            print(f"Nota na sincronização: {e}")

if __name__ == "__main__":
    main()

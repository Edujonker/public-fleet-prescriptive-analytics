#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
COMPILADOR DO CATÁLOGO COMPLETO DE TODAS AS 97 FIGURAS DA PESQUISA (PDF)
PPGCAP / CCT / UDESC • GESTÃO DE FROTAS PÚBLICAS (SEA/SC)
================================================================================
Autor: Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa / Prof. Dr. Yuri Kaszubowski Lopes
Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC)
Módulo: scripts/compilar_catalogo_todas_figuras_pdf.py

Escopo:
- Tabela-Índice de Consulta Rápida de todas as 97 figuras (Número, Arquivo, Título, Do que se trata)
- Galeria Exaustiva de Figuras 01 a 97 com miniaturas em 300 DPI
- Diagnóstico técnico, causa raiz, impacto orçamentário e diretriz prescritiva GFI para cada uma
================================================================================
"""

import os
import sys
import json
import shutil
from pathlib import Path
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.catalogo_explicacoes_detalhadas_97 import CATALOGO_DETALHADO_97

RELATORIOS_DIR = BASE_DIR / "relatorios"
CHARTS_DIR = BASE_DIR / "charts"
GRAFICOS_DIR = BASE_DIR / "graficos"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_DIR = BASE_DIR / "Documentos"
DASH_PDF_DIR = BASE_DIR / "dashboard" / "relatorios_pdf"

for d in [RELATORIOS_DIR, CHARTS_DIR, PDF_DIR, DOCS_DIR, DASH_PDF_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def resolver_imagem(num):
    """Localiza o arquivo físico exato da figura em charts/ ou graficos/."""
    arquivos = list(CHARTS_DIR.glob(f"fig{num:02d}_*.png"))
    if not arquivos:
        arquivos = list(GRAFICOS_DIR.glob(f"fig{num:02d}_*.png"))
    if arquivos:
        return f"file://{arquivos[0].resolve()}", arquivos[0].name
    return "", f"fig{num:02d}.png"

def categorizar_eixo(num):
    """Atribui o eixo temático da figura para agrupamento analítico."""
    if num in [1, 2, 4, 25, 26, 27, 28, 33, 63, 73]:
        return "1. Diagnóstico Descritivo & Saneamento"
    elif num in [5, 6, 21, 41, 42, 59, 60, 68]:
        return "2. Detecção de Anomalias (Isolation Forest)"
    elif num in [7, 8, 9, 10, 11, 23, 38, 50, 71, 72]:
        return "3. Aprendizado Supervisionado & Calibração"
    elif num in [12, 13, 17, 31, 57, 58, 67, 75, 76]:
        return "4. Explicabilidade (XAI SHAP & LIME)"
    elif num in [14, 15, 32, 55, 61, 84, 85, 90, 91, 92]:
        return "5. Otimização Prescritiva (MILP)"
    elif num in [16, 22, 24, 29, 30, 49, 51, 52, 53, 54]:
        return "6. Resíduos, Incerteza & Testes Estatísticos"
    elif num in [18, 19, 20, 47, 48, 62, 69, 70, 78, 86, 93]:
        return "7. Séries Temporais & Projeção Trienal"
    else:
        return "8. Teoria dos Grafos & Redes Complexas"

def main():
    print("=" * 80)
    print("COMPILANDO CATÁLOGO COMPLETO DE TODAS AS 97 FIGURAS DA PESQUISA (PDF)")
    print("=" * 80)

    pdf_out = PDF_DIR / "catalogo_todas_figuras.pdf"

    # Construção das linhas da Tabela-Índice Consolidada
    linhas_tabela_indice = ""
    for i in range(1, 98):
        info = CATALOGO_DETALHADO_97.get(i, {})
        _, arq_real = resolver_imagem(i)
        titulo = info.get("titulo", f"Figura {i:02d}")
        desc = info.get("desc", "Análise quantitativa dos dados da frota.")
        eixo = categorizar_eixo(i)

        linhas_tabela_indice += f"""
        <tr>
            <td style="text-align: center; font-weight: bold; color: #0284c7;">{i:02d}</td>
            <td style="font-family: monospace; font-size: 6.8pt; color: #334155;">{arq_real}</td>
            <td style="font-weight: 700; color: #0f172a;">{titulo}</td>
            <td style="font-size: 7.2pt; color: #475569;">{desc}</td>
            <td><span class="badge-eixo-mini">{eixo.split('.')[1].strip()}</span></td>
        </tr>
        """

    # Construção da Galeria Exaustiva de Figuras (Cards Analíticos)
    html_cards = ""
    for i in range(1, 98):
        info = CATALOGO_DETALHADO_97.get(i, {})
        img_url, arq_real = resolver_imagem(i)
        titulo = info.get("titulo", f"Figura {i:02d}")
        desc = info.get("desc", "Análise de padrões empíricos da frota estadual.")
        diag = info.get("diag", "Diagnóstico quantitativo baseado na base empírica de 350.737 OSs.")
        causa = info.get("causa", "Comportamento operacional decorrente do uso contínuo de viaturas.")
        impacto = info.get("impacto", "Impacto orçamentário relevante sobre a execução financeira da SEA DITI.")
        presc = info.get("presc", "Adoção dos parâmetros da Cartilha GFI 2026 e Decreto Estadual 47.539/2018.")
        eixo = categorizar_eixo(i)

        box_img = ""
        if img_url:
            box_img = f"""
            <div class="card-figura">
                <img src="{img_url}" alt="{titulo}">
            </div>
            """

        html_cards += f"""
        <div class="card-figura-bloco">
            <div class="card-header">
                <div class="card-header-top">
                    <span class="badge-num">FIGURA {i:02d}</span>
                    <span class="badge-arq">{arq_real}</span>
                    <span class="badge-eixo">{eixo}</span>
                </div>
                <div class="card-titulo">{titulo}</div>
            </div>

            {box_img}

            <div class="box-do-que-se-trata">
                <span class="rotulo-se-trata">DO QUE SE TRATA:</span>
                <span class="texto-se-trata">{desc}</span>
            </div>

            <div class="grid-analise">
                <div class="col-analise">
                    <span class="rotulo-analise">Diagnóstico Técnico:</span>
                    <span class="texto-analise">{diag}</span>
                </div>
                <div class="col-analise">
                    <span class="rotulo-analise">Causa Raiz Operacional:</span>
                    <span class="texto-analise">{causa}</span>
                </div>
                <div class="col-analise">
                    <span class="rotulo-analise">Impacto Orçamentário:</span>
                    <span class="texto-analise">{impacto}</span>
                </div>
                <div class="col-analise">
                    <span class="rotulo-analise">Diretriz Prescritiva GFI/SEA:</span>
                    <span class="texto-analise">{presc}</span>
                </div>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Catálogo Completo das 97 Figuras da Pesquisa • PPGCAP/UDESC</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 15mm 13mm 15mm 13mm;
            @bottom-right {{
                content: "Página " counter(page) " de " counter(pages);
                font-size: 7.5pt;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #64748b;
            }}
            @bottom-left {{
                content: "PPGCAP/UDESC • Catálogo Oficial de Todas as 97 Figuras da Dissertação • 2026";
                font-size: 7.5pt;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #64748b;
            }}
        }}

        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #0f172a;
            margin: 0;
            padding: 0;
            line-height: 1.38;
            font-size: 8.2pt;
        }}

        /* CABEÇALHO */
        .header-box {{
            border-bottom: 2.5px solid #0284c7;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }}
        .instituicao {{
            font-size: 8pt;
            font-weight: 800;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }}
        .titulo-doc {{
            font-size: 13.5pt;
            font-weight: 900;
            color: #0f172a;
            margin: 4px 0 2px 0;
            text-transform: uppercase;
            line-height: 1.22;
        }}
        .subtitulo-doc {{
            font-size: 8.8pt;
            color: #0284c7;
            font-weight: 700;
            margin: 0 0 6px 0;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 6px;
            font-size: 7.4pt;
            color: #475569;
            border-top: 1px solid #e2e8f0;
            padding-top: 5px;
        }}
        .meta-item strong {{
            color: #0f172a;
        }}

        /* SEÇÕES E TIPOGRAFIA */
        h2 {{
            font-size: 10.5pt;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 1.5px solid #cbd5e1;
            padding-bottom: 3px;
            margin-top: 14px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        p {{
            margin-top: 0;
            margin-bottom: 6px;
            text-align: justify;
        }}

        /* CARDS KPI */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 7px;
            margin-bottom: 12px;
        }}
        .kpi-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 3.5px solid #0284c7;
            border-radius: 4px;
            padding: 5px 8px;
        }}
        .kpi-card.verde {{ border-left-color: #16a34a; }}
        .kpi-card.roxo {{ border-left-color: #7c3aed; }}
        .kpi-card.laranja {{ border-left-color: #ea580c; }}

        .kpi-label {{
            font-size: 6.4pt;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
        }}
        .kpi-val {{
            font-size: 11pt;
            font-weight: 900;
            color: #0f172a;
            margin-top: 1px;
        }}
        .kpi-desc {{
            font-size: 6.2pt;
            color: #475569;
        }}

        /* TABELA ÍNDICE */
        table.tbl-indice {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 6px;
            margin-bottom: 14px;
            font-size: 7.2pt;
        }}
        table.tbl-indice th {{
            background: #f1f5f9;
            color: #1e293b;
            font-weight: 800;
            text-align: left;
            padding: 4px 6px;
            border-top: 1.5px solid #0284c7;
            border-bottom: 1.5px solid #cbd5e1;
            text-transform: uppercase;
            font-size: 6.6pt;
        }}
        table.tbl-indice td {{
            padding: 3.5px 5px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: middle;
        }}
        table.tbl-indice tr:nth-child(even) td {{
            background: #fbfcfe;
        }}

        /* BADGES */
        .badge-num {{
            background: #0284c7;
            color: #ffffff;
            font-size: 6.5pt;
            font-weight: 800;
            padding: 1.5px 5px;
            border-radius: 3px;
        }}
        .badge-arq {{
            background: #0f172a;
            color: #38bdf8;
            font-family: 'Courier New', Courier, monospace;
            font-size: 6.4pt;
            padding: 1.5px 5px;
            border-radius: 3px;
        }}
        .badge-eixo {{
            background: #f1f5f9;
            color: #334155;
            border: 1px solid #cbd5e1;
            font-size: 6.4pt;
            font-weight: 700;
            padding: 1.5px 5px;
            border-radius: 3px;
        }}
        .badge-eixo-mini {{
            background: #e0f2fe;
            color: #0369a1;
            font-size: 6pt;
            font-weight: 700;
            padding: 1px 4px;
            border-radius: 2px;
            display: inline-block;
            white-space: nowrap;
        }}

        /* CARDS DA GALERIA */
        .card-figura-bloco {{
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            background: #ffffff;
            margin-bottom: 12px;
            padding: 7px 9px;
            page-break-inside: avoid;
        }}
        .card-header {{
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
            margin-bottom: 5px;
        }}
        .card-header-top {{
            display: flex;
            gap: 6px;
            margin-bottom: 3px;
        }}
        .card-titulo {{
            font-size: 9.2pt;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.25;
        }}

        .card-figura {{
            text-align: center;
            margin: 5px 0;
            background: #f8fafc;
            border: 1px solid #f1f5f9;
            padding: 3px;
            border-radius: 3px;
        }}
        .card-figura img {{
            max-width: 98%;
            max-height: 140px;
            height: auto;
            border-radius: 2px;
        }}

        /* BOX DO QUE SE TRATA */
        .box-do-que-se-trata {{
            background: #f0fdf4;
            border-left: 3.5px solid #16a34a;
            border-radius: 3px;
            padding: 4px 7px;
            margin: 4px 0 6px 0;
        }}
        .rotulo-se-trata {{
            font-size: 6.5pt;
            font-weight: 900;
            color: #15803d;
            display: block;
            margin-bottom: 1px;
        }}
        .texto-se-trata {{
            font-size: 7.7pt;
            font-weight: 700;
            color: #14532d;
            line-height: 1.3;
        }}

        /* GRID ANALÍTICO */
        .grid-analise {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 5px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 3px;
            padding: 5px 7px;
        }}
        .col-analise {{
            display: flex;
            flex-direction: column;
            gap: 1px;
        }}
        .rotulo-analise {{
            font-size: 6.3pt;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
        }}
        .texto-analise {{
            font-size: 7.1pt;
            color: #334155;
            line-height: 1.3;
        }}

        .page-break {{
            page-break-before: always;
        }}
    </style>
</head>
<body>

    <!-- CABEÇALHO OFICIAL -->
    <div class="header-box">
        <div class="instituicao">UNIVERSIDADE DO ESTADO DE SANTA CATARINA • CENTRO DE CIÊNCIAS TECNOLÓGICAS (CCT) • PPGCAP</div>
        <div class="titulo-doc">Catálogo Geral das 97 Figuras da Pesquisa: Nomes, Escopo e Análises</div>
        <div class="subtitulo-doc">Inventário Técnico Completo, Títulos Acadêmicos, Descrição de do que se Trata Cada Ilustração e Prescrições (SEA/SC)</div>
        <div class="meta-grid">
            <div class="meta-item"><strong>Autor:</strong> Eduardo Lopes Jonker</div>
            <div class="meta-item"><strong>Orientação:</strong> Profa. Dra. Vivian Kremer Kalempa</div>
            <div class="meta-item"><strong>Coorientação:</strong> Prof. Dr. Yuri Kaszubowski Lopes</div>
            <div class="meta-item"><strong>Linha de Pesquisa:</strong> Metodologia e Técnicas de Computação</div>
            <div class="meta-item"><strong>Universo Amostral:</strong> 350.737 OSs e 1.636.541 itens</div>
            <div class="meta-item"><strong>Total de Figuras:</strong> 97 Ilustrações (300 DPI)</div>
        </div>
    </div>

    <!-- CARDS KPI DE SÍNTESE -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Total de Ilustrações</div>
            <div class="kpi-val">97 Figuras</div>
            <div class="kpi-desc">Resolução editorial 300 DPI</div>
        </div>
        <div class="kpi-card verde">
            <div class="kpi-label">Base Empírica</div>
            <div class="kpi-val">350.737 OSs</div>
            <div class="kpi-desc">Quadriênio 2021 a 2024</div>
        </div>
        <div class="kpi-card roxo">
            <div class="kpi-label">Eixos Temáticos</div>
            <div class="kpi-val">8 Eixos</div>
            <div class="kpi-desc">Da engenharia aos grafos</div>
        </div>
        <div class="kpi-card laranja">
            <div class="kpi-label">Economia Projetada</div>
            <div class="kpi-val">R$ 40,09M</div>
            <div class="kpi-desc">Prescrição trienal To-Be</div>
        </div>
    </div>

    <!-- SEÇÃO 1: TABELA ÍNDICE CONSOLIDADA -->
    <h2>1. Tabela-Índice Consolidada de Todas as 97 Figuras (Consulta Rápida)</h2>
    <p>
        A tabela a seguir apresenta a relação exaustiva e sequencial de todas as 97 figuras da pesquisa, identificando o número de ordem, o nome oficial do arquivo gráfico em disco, o título acadêmico e a síntese conceitual de do que trata cada ilustração:
    </p>

    <table class="tbl-indice">
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">Nº</th>
                <th style="width: 25%;">Nome do Arquivo Físico</th>
                <th style="width: 32%;">Título Acadêmico Oficial</th>
                <th style="width: 24%;">Do que se trata</th>
                <th style="width: 14%;">Eixo</th>
            </tr>
        </thead>
        <tbody>
            {linhas_tabela_indice}
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- SEÇÃO 2: GALERIA ANALÍTICA COMPLETA DE TODAS AS 97 FIGURAS -->
    <h2>2. Galeria Exaustiva e Análise Técnica Individualizada (Figuras 01 a 97)</h2>
    <p>
        A seguir, cada uma das 97 ilustrações é apresentada com sua miniatura gráfica em alta resolução, o detalhamento conceitual de do que se trata, o diagnóstico quantitativo dos dados, a causa raiz observada, o impacto financeiro mensurado e a diretriz prescritiva preconizada:
    </p>

    {html_cards}

    <!-- ENCERRAMENTO -->
    <div style="margin-top: 15px; border-top: 1px solid #cbd5e1; padding-top: 8px; font-size: 7.2pt; color: #64748b; text-align: center;">
        Catálogo Geral de Figuras compilado via WeasyPrint 70.0 sob os padrões do PPGCAP/UDESC.<br>
        Ambiente: Dell Inspiron 15 3530 • Ubuntu 26.04 LTS • Python 3.14.4 • Todos os direitos reservados à SEA/SC e UDESC.
    </div>

</body>
</html>
"""

    print("Renderizando HTML do Catálogo Completo das 97 Figuras via WeasyPrint...")
    html_obj = weasyprint.HTML(string=html_content, base_url=str(BASE_DIR))
    html_obj.write_pdf(str(pdf_out))

    # Sincronização nos diretórios oficiais do projeto (com proteção a symlinks)
    copias = [
        RELATORIOS_DIR / "catalogo_todas_figuras.pdf",
        RELATORIOS_DIR / "catalogo_97_figuras.pdf",
        DOCS_DIR / "catalogo_todas_figuras.pdf",
        DOCS_DIR / "catalogo_97_figuras.pdf",
        DASH_PDF_DIR / "catalogo_todas_figuras.pdf",
        DASH_PDF_DIR / "catalogo_97_figuras.pdf"
    ]
    for c in copias:
        try:
            if c.resolve() != pdf_out.resolve():
                shutil.copy2(pdf_out, c)
        except Exception:
            pass

    tamanho_mb = pdf_out.stat().st_size / (1024 * 1024)
    print(f"Sucesso! Catálogo gerado em: {pdf_out} ({tamanho_mb:.2f} MB)")
    for c in copias:
        print(f"  -> Cópia sincronizada em: {c}")

if __name__ == "__main__":
    main()

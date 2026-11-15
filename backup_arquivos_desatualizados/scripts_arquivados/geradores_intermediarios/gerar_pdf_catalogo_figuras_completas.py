#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
COMPILADOR DO CATÁLOGO DE TODAS AS 97 FIGURAS COM PARÁGRAFOS EXPLICATIVOS FLUIDOS
PPGCAP / CCT / UDESC • GESTÃO DE FROTAS PÚBLICAS (SEA/SC)
================================================================================
Autor: Eduardo Lopes Jonker
Orientadores: Profa. Dra. Vivian Kremer Kalempa / Prof. Dr. Yuri Kaszubowski Lopes
Linha de Pesquisa: Metodologia e Técnicas de Computação (MTC)
================================================================================
"""

import os
import sys
import re
import json
import shutil
from pathlib import Path
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.catalogo_explicacoes_detalhadas_97 import CATALOGO_DETALHADO_97

CHARTS_DIR = BASE_DIR / "charts"
GRAFICOS_DIR = BASE_DIR / "graficos"
PDF_DIR = BASE_DIR / "relatorios_pdf"
RELATORIOS_DIR = BASE_DIR / "relatorios"

for d in [PDF_DIR, RELATORIOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def categorizar_eixo(num):
    """Categorização temática das 97 figuras."""
    if num in [1, 2, 4, 25, 26, 27, 28, 33, 34, 35, 36, 37, 63, 73]:
        return "1. Diagnóstico Descritivo, Perfil Operacional & Saneamento"
    elif num in [5, 6, 21, 41, 42, 43, 44, 45, 46, 91]:
        return "2. Detecção Não Supervisionada de Anomalias & Auditoria (Isolation Forest)"
    elif num in [7, 8, 9, 10, 11, 23, 30, 38, 39, 40, 50, 77]:
        return "3. Aprendizado Supervisionado, Classificação de Risco & Calibração"
    elif num in [12, 13, 17, 31, 55, 56, 57, 62, 63, 65, 66, 67]:
        return "4. Inteligência Explicável (XAI - SHAP Global/Local & LIME)"
    elif num in [14, 15, 32, 60, 61, 70, 71, 84, 85, 90, 92]:
        return "5. Otimização Prescritiva Estocástica & Fronteiras de Decisão (MILP)"
    elif num in [16, 24, 29, 49, 51, 52, 53, 54, 58, 59, 68, 69, 74, 75, 76]:
        return "6. Modelagem Não Paramétrica, Incerteza & Resíduos Estatísticos"
    elif num in [3, 18, 19, 20, 22, 47, 48, 72, 78, 79, 81, 82, 83, 86, 87, 88, 89, 93]:
        return "7. Séries Temporais, Custos de Ciclo de Vida (TCO) & Projeções Plurianuais"
    else:
        return "8. Teoria dos Grafos & Redes Complexas da Rede de Serviços"

def resolver_imagem(num):
    info = CATALOGO_DETALHADO_97.get(num, {})
    cadastrado = info.get("arquivo", "")
    p = CHARTS_DIR / cadastrado
    if p.exists():
        return f"file://{p.resolve()}", cadastrado
    
    # Busca por padrão
    matches = list(CHARTS_DIR.glob(f"fig{num:02d}_*.png"))
    if matches:
        return f"file://{matches[0].resolve()}", matches[0].name
    
    matches_graf = list(GRAFICOS_DIR.glob(f"fig{num:02d}_*.png"))
    if matches_graf:
        return f"file://{matches_graf[0].resolve()}", matches_graf[0].name
        
    return "", cadastrado or f"fig{num:02d}.png"

def sintetizar_paragrafo_fluido(num, item):
    """
    Constrói um parágrafo fluido, articulado e analítico para a figura,
    evitando a mera leitura mecânica dos eixos e fechando a interpretação técnica.
    """
    diag = item.get("diag", "").strip().rstrip(".")
    causa = item.get("causa", "").strip().rstrip(".")
    impacto = item.get("impacto", "").strip().rstrip(".")
    presc = item.get("presc", "").strip().rstrip(".")
    
    # Tratamento de causas
    c_lower = causa[0].lower() + causa[1:] if len(causa) > 1 else causa
    if c_lower.startswith("a ") or c_lower.startswith("o ") or c_lower.startswith("os ") or c_lower.startswith("as "):
        frase_causa = f"Este comportamento tem como vetor determinante {c_lower}"
    elif any(c_lower.startswith(w) for w in ["fragilidade", "cultura", "pressão", "erros", "padrões", "sobrepreço", "degradação", "desgaste", "falta", "ausência"]):
        frase_causa = f"Tal manifestação reflete, estruturalmente, {c_lower}"
    else:
        frase_causa = f"Essa dinâmica empírica decorre de {c_lower}"
        
    # Tratamento de impacto
    i_lower = impacto[0].lower() + impacto[1:] if len(impacto) > 1 else impacto
    if any(w in i_lower for w in ["evitaram", "evitou", "economizou", "gerou"]):
        frase_impacto = f"No âmbito orçamentário e de controle patrimonial, constata-se que {i_lower}"
    elif any(i_lower.startswith(w) for w in ["glosas", "intervenções", "sobrecarga", "inconsistências", "foco", "permite", "redução", "o montante", "economia", "subsidia", "minimiza", "assegura"]):
        frase_impacto = f"Em relação aos desdobramentos financeiros e operacionais, {i_lower}"
    else:
        frase_impacto = f"Sob a perspectiva de impacto na gestão, {i_lower}"
        
    # Tratamento de prescrição
    p_lower = presc[0].lower() + presc[1:] if len(presc) > 1 else presc
    if any(p_lower.startswith(w) for w in ["exigir", "migrar", "instituir", "implementar", "priorizar", "bloquear", "adotar", "licitar", "utilizar", "apresentar", "dimensionar", "configurar", "formalizar", "recomendar", "estabelecer"]):
        frase_presc = f"Diante desse panorama analítico, define-se como determinação prescritiva {p_lower}."
    else:
        frase_presc = f"Por conseguinte, a diretriz prescritiva imperativa estabelece {p_lower}."
        
    paragrafo = f"{diag}. {frase_causa}. {frase_impacto}. {frase_presc}"
    paragrafo = re.sub(r"\s+", " ", paragrafo)
    return paragrafo

def main():
    print("=" * 80)
    print("GERANDO CATÁLOGO INTEGRAL DE TODAS AS 97 FIGURAS COM PARÁGRAFOS FLUIDOS")
    print("=" * 80)

    # Construção da Tabela Sumária do Índice
    linhas_tabela = ""
    for i in range(1, 98):
        info = CATALOGO_DETALHADO_97.get(i, {})
        _, arq_real = resolver_imagem(i)
        titulo = info.get("titulo", f"Figura {i:02d}")
        eixo = categorizar_eixo(i)
        
        linhas_tabela += f"""
        <tr>
            <td class="col-num">{i:02d}</td>
            <td class="col-arq">{arq_real}</td>
            <td class="col-tit">{titulo}</td>
            <td class="col-eixo"><span class="badge-eixo-tbl">{eixo.split('.')[1].strip()[:35]}</span></td>
        </tr>
        """

    # Construção das páginas individuais das 97 figuras
    paginas_figuras = ""
    for i in range(1, 98):
        info = CATALOGO_DETALHADO_97.get(i, {})
        img_url, arq_real = resolver_imagem(i)
        titulo = info.get("titulo", f"Figura {i:02d}")
        eixo = categorizar_eixo(i)
        paragrafo = sintetizar_paragrafo_fluido(i, info)
        
        paginas_figuras += f"""
        <div class="pagina-figura">
            <div class="topo-figura">
                <div class="meta-faixa">
                    <span class="badge-numero">FIGURA {i:02d}</span>
                    <span class="badge-arquivo">{arq_real}</span>
                    <span class="badge-eixo">{eixo}</span>
                </div>
                <h2 class="titulo-figura">{titulo}</h2>
            </div>
            
            <div class="conteiner-imagem">
                <img src="{img_url}" alt="{titulo}" class="img-preview">
            </div>
            
            <div class="bloco-interpretacao">
                <div class="cabecalho-interpretacao">
                    <span class="icone-interpretacao">✦</span>
                    <span class="rotulo-interpretacao">ANÁLISE ANALÍTICA INTEGRADA E DIRETRIZ PRESCRITIVA</span>
                </div>
                <p class="texto-paragrafo-fluido">
                    {paragrafo}
                </p>
            </div>
        </div>
        """

    html_completo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Catálogo Completo das 97 Figuras da Pesquisa • PPGCAP/UDESC</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 14mm 14mm 14mm 14mm;
            @bottom-right {{
                content: "Página " counter(page) " de " counter(pages);
                font-size: 7.2pt;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #64748b;
                font-weight: bold;
            }}
            @bottom-left {{
                content: "PPGCAP / UDESC • Pesquisa de Governança e Analítica Prescritiva em Frotas Públicas • 2026";
                font-size: 7pt;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #64748b;
            }}
        }}

        @page:first {{
            margin: 0;
            @bottom-right {{ content: normal; }}
            @bottom-left {{ content: normal; }}
        }}

        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #0f172a;
            margin: 0;
            padding: 0;
            line-height: 1.42;
            font-size: 8.5pt;
        }}

        /* CAPA EXECUTIVA */
        .capa {{
            height: 100vh;
            padding: 60px 45px 45px 45px;
            box-sizing: border-box;
            background: linear-gradient(135deg, #091e3a 0%, #0f172a 100%);
            color: #ffffff;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            page-break-after: always;
        }}
        .capa-topo {{
            border-bottom: 2px solid #0284c7;
            padding-bottom: 18px;
        }}
        .capa-inst {{
            font-size: 9.5pt;
            font-weight: 800;
            letter-spacing: 1.5px;
            color: #38bdf8;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .capa-centro {{
            margin: 40px 0;
        }}
        .capa-tag {{
            display: inline-block;
            background: #0284c7;
            color: #ffffff;
            padding: 4px 10px;
            font-size: 8pt;
            font-weight: 800;
            border-radius: 3px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }}
        .capa-titulo {{
            font-size: 23pt;
            font-weight: 900;
            line-height: 1.18;
            color: #ffffff;
            margin: 0 0 15px 0;
            text-transform: uppercase;
        }}
        .capa-subtitulo {{
            font-size: 11pt;
            font-weight: 400;
            color: #94a3b8;
            line-height: 1.4;
            max-width: 90%;
        }}
        .capa-meta {{
            border-top: 1px solid #1e293b;
            padding-top: 18px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            font-size: 8.5pt;
            color: #cbd5e1;
        }}
        .capa-meta strong {{
            color: #ffffff;
            display: block;
            margin-bottom: 2px;
        }}

        /* INTRODUÇÃO E ÍNDICE */
        .secao-textual {{
            page-break-after: always;
            padding-top: 5px;
        }}
        h1.titulo-secao {{
            font-size: 13pt;
            font-weight: 900;
            color: #0f172a;
            border-bottom: 2.5px solid #0284c7;
            padding-bottom: 4px;
            margin-top: 0;
            margin-bottom: 12px;
            text-transform: uppercase;
        }}
        p.intro-p {{
            text-align: justify;
            font-size: 8.4pt;
            color: #334155;
            margin-bottom: 8px;
            line-height: 1.45;
        }}
        
        .grid-kpis-intro {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin: 14px 0;
        }}
        .kpi-intro-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 3.5px solid #0284c7;
            padding: 6px 9px;
            border-radius: 4px;
        }}
        .kpi-intro-card.verde {{ border-left-color: #16a34a; }}
        .kpi-intro-card.roxo {{ border-left-color: #7c3aed; }}
        .kpi-intro-card.laranja {{ border-left-color: #ea580c; }}
        
        .kpi-label {{
            font-size: 6.5pt;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
        }}
        .kpi-val {{
            font-size: 12pt;
            font-weight: 900;
            color: #0f172a;
            margin: 1px 0;
        }}
        .kpi-sub {{
            font-size: 6.2pt;
            color: #475569;
        }}

        /* TABELA SUMÁRIA */
        table.tbl-indice-geral {{
            width: 100%;
            border-collapse: collapse;
            font-size: 7.2pt;
            margin-top: 8px;
        }}
        table.tbl-indice-geral th {{
            background: #f1f5f9;
            color: #0f172a;
            font-weight: 800;
            text-align: left;
            padding: 4.5px 6px;
            border-top: 2px solid #0284c7;
            border-bottom: 1px solid #cbd5e1;
            text-transform: uppercase;
            font-size: 6.8pt;
        }}
        table.tbl-indice-geral td {{
            padding: 3.5px 5px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: middle;
        }}
        table.tbl-indice-geral tr:nth-child(even) td {{
            background: #fbfcfe;
        }}
        .col-num {{
            font-weight: 800;
            color: #0284c7;
            text-align: center;
            width: 30px;
        }}
        .col-arq {{
            font-family: monospace;
            font-size: 6.6pt;
            color: #475569;
            width: 180px;
        }}
        .col-tit {{
            font-weight: 700;
            color: #1e293b;
        }}
        .col-eixo {{
            width: 140px;
            text-align: right;
        }}
        .badge-eixo-tbl {{
            background: #e0f2fe;
            color: #0369a1;
            padding: 1.5px 4px;
            border-radius: 2px;
            font-size: 6pt;
            font-weight: 700;
            display: inline-block;
            white-space: nowrap;
        }}

        /* PÁGINA INDIVIDUAL DA FIGURA (1 FIGURA POR PÁGINA) */
        .pagina-figura {{
            page-break-after: always;
            padding: 0;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
        }}
        .topo-figura {{
            border-bottom: 1.5px solid #e2e8f0;
            padding-bottom: 5px;
            margin-bottom: 7px;
        }}
        .meta-faixa {{
            display: flex;
            gap: 6px;
            margin-bottom: 4px;
            align-items: center;
        }}
        .badge-numero {{
            background: #0284c7;
            color: #ffffff;
            font-size: 7.2pt;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 3px;
            letter-spacing: 0.5px;
        }}
        .badge-arquivo {{
            background: #0f172a;
            color: #38bdf8;
            font-family: monospace;
            font-size: 6.8pt;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .badge-eixo {{
            background: #f8fafc;
            color: #334155;
            border: 1px solid #cbd5e1;
            font-size: 6.8pt;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .titulo-figura {{
            font-size: 10.2pt;
            font-weight: 800;
            color: #0f172a;
            margin: 2px 0 0 0;
            line-height: 1.25;
        }}

        /* CONTEINER DA IMAGEM */
        .conteiner-imagem {{
            text-align: center;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 6px;
            margin: 6px 0 10px 0;
        }}
        .img-preview {{
            max-width: 98%;
            max-height: 125mm;
            height: auto;
            border-radius: 2px;
            display: inline-block;
        }}

        /* BLOCO ANALÍTICO INTEGRADO COM O PARÁGRAFO FLUIDO */
        .bloco-interpretacao {{
            background: #f8fafc;
            border: 1.2px solid #cbd5e1;
            border-left: 4px solid #0284c7;
            border-radius: 4px;
            padding: 10px 14px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        .cabecalho-interpretacao {{
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 5px;
        }}
        .icone-interpretacao {{
            color: #0284c7;
            font-size: 9pt;
            font-weight: 900;
        }}
        .rotulo-interpretacao {{
            font-size: 7.2pt;
            font-weight: 900;
            color: #0369a1;
            letter-spacing: 0.6px;
            text-transform: uppercase;
        }}
        .texto-paragrafo-fluido {{
            font-size: 8.6pt;
            color: #1e293b;
            line-height: 1.5;
            text-align: justify;
            margin: 0;
            text-indent: 1.5em;
        }}
    </style>
</head>
<body>

    <!-- CAPA -->
    <div class="capa">
        <div class="capa-topo">
            <div class="capa-inst">Universidade do Estado de Santa Catarina (UDESC)</div>
            <div style="font-size: 8.5pt; color: #94a3b8;">Centro de Ciências Tecnológicas (CCT) • Programa de Pós-Graduação em Computação Aplicada (PPGCAP)</div>
        </div>
        
        <div class="capa-centro">
            <span class="capa-tag">Documento Suplementar Oficial</span>
            <h1 class="capa-titulo">Catálogo Analítico Ilustrado das 97 Figuras da Pesquisa</h1>
            <div class="capa-subtitulo">
                Coletânea Integral de Evidências Experimentais, Diagnósticos Descritivos, Detecção de Anomalias, Curvas ROC/PR, Explicabilidade XAI (SHAP & LIME), Otimização Prescritiva MILP e Modelagem em Grafos da Frota Pública de Santa Catarina.
            </div>
        </div>
        
        <div class="capa-meta">
            <div>
                <strong>Mestrando / Autor:</strong>
                Eduardo Lopes Jonker (Engenheiro SEA/SC)
            </div>
            <div>
                <strong>Orientadores:</strong>
                Profa. Dra. Vivian Kremer Kalempa<br>
                Prof. Dr. Yuri Kaszubowski Lopes
            </div>
            <div>
                <strong>Base Empírica Subjacente:</strong>
                350.737 Itens de OS • 77.867 Ordens de Serviço • 5.914 Veículos
            </div>
            <div>
                <strong>Local e Ano de Defesa:</strong>
                Joinville / Florianópolis – Santa Catarina • 2026
            </div>
        </div>
    </div>

    <!-- INTRODUÇÃO METODOLÓGICA -->
    <div class="secao-textual">
        <h1 class="titulo-secao">Estrutura Metodológica e Rastreabilidade Analítica</h1>
        <p class="intro-p">
            O presente documento reúne, de forma exaustiva e integral, as <strong>97 figuras científicas</strong> geradas ao longo do pipeline experimental da dissertação de mestrado <em>"Analítica Prescritiva e Governança de Frotas Públicas Estaduais: Um Modelo Baseado em Aprendizado de Máquina, Inteligência Explicável e Otimização Inteira Mista"</em>. A pesquisa fundamenta-se nos dados reais da frota pertencente ao Governo do Estado de Santa Catarina, gerida pela Secretaria de Estado da Administração (SEA/SC) e auditada pela Diretoria de Gestão Patrimonial (DGP) e Gerência de Frotas e Transporte Oficial (GFI).
        </p>
        
        <div class="grid-kpis-intro">
            <div class="kpi-intro-card">
                <div class="kpi-label">Base Longitudinal</div>
                <div class="kpi-val">350.737</div>
                <div class="kpi-sub">Registros de itens de manutenção</div>
            </div>
            <div class="kpi-intro-card verde">
                <div class="kpi-label">Ordens de Serviço</div>
                <div class="kpi-val">77.867</div>
                <div class="kpi-sub">Eventos transacionados na rede</div>
            </div>
            <div class="kpi-intro-card roxo">
                <div class="kpi-label">População de Veículos</div>
                <div class="kpi-val">5.914</div>
                <div class="kpi-sub">Veículos oficiais ativos monitorados</div>
            </div>
            <div class="kpi-intro-card laranja">
                <div class="kpi-label">Economia Otimizada</div>
                <div class="kpi-val">R$ 40,09M</div>
                <div class="kpi-sub">Potencial no triênio 2027–2029</div>
            </div>
        </div>

        <p class="intro-p">
            Para garantir a plena apreensão técnica e evitar ambiguidades interpretativas, cada figura é acompanhada por um <strong>parágrafo analítico fluido e autônomo</strong>. Essa formulação sintetiza: (i) as métricas quantitativas e percentuais observados empiricamente; (ii) os mecanismos operacionais, mecânicos ou normativos que constituem a causa raiz do padrão; (iii) a mensuração do impacto financeiro, orçamentário ou de disponibilidade operacional da frota; e (iv) a decisão prescritiva mandatória lastreada na <em>Cartilha de Gestão de Frotas Integrada (GFI 2026)</em> e no <em>Decreto Estadual nº 47.539/2018</em>. Dessa forma, a interpretação não é delegada ao leitor, mas explicitada com rigor científico e aplicabilidade direta na administração pública.
        </p>
    </div>

    <!-- SUMÁRIO EXECUTIVO DAS FIGURAS -->
    <div class="secao-textual">
        <h1 class="titulo-secao">Índice Sistemático das 97 Figuras da Pesquisa</h1>
        <table class="tbl-indice-geral">
            <thead>
                <tr>
                    <th style="text-align: center; width: 28px;">Nº</th>
                    <th style="width: 175px;">Arquivo Físico</th>
                    <th>Título da Ilustração Científica</th>
                    <th style="text-align: right; width: 140px;">Eixo Metodológico</th>
                </tr>
            </thead>
            <tbody>
                {linhas_tabela}
            </tbody>
        </table>
    </div>

    <!-- PÁGINAS INDIVIDUAIS DAS 97 FIGURAS -->
    {paginas_figuras}

</body>
</html>
"""

    html_file = BASE_DIR / "relatorios" / "catalogo_figuras_gerado.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_completo)
    print(f"HTML intermediário salvo em: {html_file}")

    pdf_out = PDF_DIR / "catalogo_todas_figuras_explicadas.pdf"
    print(f"Renderizando PDF com WeasyPrint em: {pdf_out}...")
    
    # Renderização WeasyPrint
    doc = weasyprint.HTML(filename=str(html_file))
    doc.write_pdf(str(pdf_out))
    print(f"✓ PDF gerado com sucesso! Tamanho: {pdf_out.stat().st_size / (1024*1024):.2f} MB")

    # Copiar para os caminhos padronizados do repositório
    destinos = [
        RELATORIOS_DIR / "catalogo_todas_figuras.pdf",
        RELATORIOS_DIR / "catalogo_97_figuras.pdf",
        RELATORIOS_DIR / "catalogo_figuras_explicadas.pdf",
        PDF_DIR / "catalogo_todas_figuras.pdf",
        PDF_DIR / "catalogo_97_figuras.pdf"
    ]
    for dest in destinos:
        shutil.copy2(pdf_out, dest)
        print(f"✓ Cópia sincronizada em: {dest}")

    print("=" * 80)
    print("PROCESSO CONCLUÍDO COM SUCESSO!")
    print("=" * 80)

if __name__ == "__main__":
    main()

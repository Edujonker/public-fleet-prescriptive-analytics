#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera Apresentacao_36_SIC_UDESC_nova.pptx
Conteúdo: 16+2 slides consolidados aproveitando:
  - estrutura narrativa do Apresentacao_36_SIC_UDESC_com_bibliografia.pptx (16 slides)
  - conteúdo técnico do apresentaçao_SIC.pdf (32 páginas de relatório de apoio)

Paleta e tipografia:
  Azul escuro  #1B3A6E  — títulos, blocos de header
  Azul médio   #2D6BB5  — subtítulos, ênfase
  Azul claro   #EAF1FB  — fundos de slide de conteúdo
  Branco       #FFFFFF  — fundo geral
  Cinza escuro #2B2B2B  — corpo de texto
  Verde        #1A7A3A  — resultados confirmados / hipóteses
  Vermelho     #A00000  — hipótese refutada / alertas
  Laranja      #C47800  — avisos / contrafactuais
  Cinza claro  #F4F6FB  — box de nota

Tipografia:
  Títulos principais  : Calibri 32-28pt Bold
  Subtítulos de slide : Calibri 18pt Bold
  Corpo               : Calibri Light 15pt
  Nota / rodapé       : Calibri 10pt Italic
  Número do slide     : Calibri 20pt Bold (canto superior esquerdo)
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ── Cores ────────────────────────────────────────────────────────────────────
AZUL_ESC  = RGBColor(0x1B, 0x3A, 0x6E)
AZUL_MED  = RGBColor(0x2D, 0x6B, 0xB5)
AZUL_CLR  = RGBColor(0xEA, 0xF1, 0xFB)
BRANCO    = RGBColor(0xFF, 0xFF, 0xFF)
CINZA_ESC = RGBColor(0x2B, 0x2B, 0x2B)
VERDE     = RGBColor(0x1A, 0x7A, 0x3A)
VERMELHO  = RGBColor(0xA0, 0x00, 0x00)
LARANJA   = RGBColor(0xC4, 0x78, 0x00)
CINZA_CLR = RGBColor(0xF4, 0xF6, 0xFB)
CINZA_BOX = RGBColor(0xDD, 0xE3, 0xEF)

ROOT     = Path(__file__).resolve().parent.parent
OUT      = ROOT / "SIC" / "SIC_final.pptx"
TOTAL_SLIDES = 20
IMG_H4   = str(ROOT / "SIC" / "img" / "h4_shap_lime_concordancia.png")
LOGO_DIR = Path("/tmp/udesc_logos")
LOGO_HORIZ  = str(LOGO_DIR / "Imagem 20.png")   # logo UDESC horizontal 302×103
LOGO_SYMBOL = str(LOGO_DIR / "Imagem 1.png")    # símbolo UDESC verde 1071×2111
LOGO_BARRA  = str(LOGO_DIR / "Imagem 13.png")   # barra verde fina 51×723

# Cores UDESC oficiais
VERDE_UDESC_ESC = RGBColor(0x00, 0x5B, 0x2E)   # verde escuro #005B2E
VERDE_UDESC_CLR = RGBColor(0x2E, 0xA8, 0x4B)   # verde claro  #2EA84B
VERDE_FUNDO     = RGBColor(0xE8, 0xF5, 0xEC)   # verde muito claro para fundo

# ── Dimensões 16:9 ────────────────────────────────────────────────────────────
W = Inches(13.33)
H = Inches(7.50)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

# ── Helpers ───────────────────────────────────────────────────────────────────

def blank(prs):
    """Slide completamente em branco."""
    return prs.slides.add_slide(prs.slide_layouts[6])

def bg(slide, color: RGBColor):
    """Define cor de fundo sólido do slide."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, l, t, w, h, fill_color=None, border_color=None, border_pt=0):
    """Retângulo de fundo (shape sem texto)."""
    shp = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.line.width = Pt(border_pt)
    if border_color:
        shp.line.color.rgb = border_color
    else:
        shp.line.fill.background()
    if fill_color:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill_color
    else:
        shp.fill.background()
    return shp

def txt(slide, text, l, t, w, h,
        size=15, bold=False, italic=False,
        color=CINZA_ESC, align=PP_ALIGN.LEFT,
        wrap=True, font="Calibri Light"):
    """Caixa de texto simples."""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name  = font
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb

def txt_multi(slide, lines, l, t, w, h,
              size=14, bold=False, color=CINZA_ESC,
              spacing_pt=4, font="Calibri Light"):
    """Caixa com múltiplas linhas (lista de strings)."""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(spacing_pt)
        run = p.add_run()
        run.text = line
        run.font.name  = font
        run.font.size  = Pt(size)
        run.font.bold  = bold
        run.font.color.rgb = color
    return tb

def header_bar(slide, numero: str, titulo: str, subtitulo: str = ""):
    """Barra de cabeçalho padrão — número visível no rodapé à direita."""
    box(slide, 0, 0, 13.33, 1.35, fill_color=AZUL_ESC)
    # título
    txt(slide, titulo, 0.35, 0.08, 11.50, 0.68,
        size=30, bold=True, color=BRANCO, font="Calibri")
    # subtítulo
    if subtitulo:
        txt(slide, subtitulo, 0.35, 0.82, 11.50, 0.45,
            size=15, bold=False, italic=True, color=AZUL_CLR, font="Calibri Light")
    # rodapé
    box(slide, 0, 7.15, 13.33, 0.35, fill_color=AZUL_MED)
    # texto do rodapé à esquerda
    txt(slide, "36º SIC  •  PPGCAP/CCT/UDESC  •  Eduardo Lopes Jonker",
        0.20, 7.17, 11.20, 0.28,
        size=10, bold=False, italic=True, color=BRANCO, font="Calibri Light")
    # número do slide à direita — automático (posição real no deck)
    num_str = f"{len(prs.slides)} / {TOTAL_SLIDES}"
    txt(slide, num_str, 11.45, 7.17, 1.65, 0.28,
        size=11, bold=True, color=BRANCO,
        align=PP_ALIGN.RIGHT, font="Calibri")

def nota(slide, texto: str, icone: str = "⚠", cor=None):
    """Nota de rodapé de conteúdo (acima da barra)."""
    box(slide, 0.35, 6.74, 12.63, 0.38, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.5)
    txt(slide, f"{icone}  {texto}", 0.42, 6.76, 12.50, 0.35,
        size=10, italic=True, color=cor or LARANJA, font="Calibri Light")

def kpi_box(slide, valor, label, l, t, w=2.80, h=1.20, val_color=AZUL_ESC):
    """Caixa KPI: valor grande + label menor."""
    box(slide, l, t, w, h, fill_color=AZUL_CLR,
        border_color=AZUL_MED, border_pt=1)
    txt(slide, valor, l+0.08, t+0.05, w-0.16, 0.68,
        size=24, bold=True, color=val_color, align=PP_ALIGN.CENTER, font="Calibri")
    txt(slide, label, l+0.08, t+0.74, w-0.16, 0.40,
        size=11, bold=False, color=CINZA_ESC, align=PP_ALIGN.CENTER, font="Calibri Light")

def bullet_col(slide, titulo: str, bullets, l, t, w=5.80, h=4.40,
               titulo_size=15, bullet_size=13):
    """Coluna com título e lista de bullets."""
    box(slide, l, t, w, 0.44, fill_color=AZUL_MED)
    txt(slide, titulo, l+0.10, t+0.05, w-0.20, 0.36,
        size=titulo_size, bold=True, color=BRANCO, font="Calibri")
    buls = ["▸  " + b for b in bullets]
    txt_multi(slide, buls, l+0.12, t+0.50, w-0.24, h-0.54,
              size=bullet_size, font="Calibri Light", spacing_pt=6)

def hipotese_row(slide, hid, enunciado, resultado, evidencia, top):
    """Linha da tabela de hipóteses."""
    # ✓ sustentada (verde) · ◐ parcialmente sustentada (laranja) · ✗ não sustentada (vermelho)
    cor_res = VERDE if "✓" in resultado else (LARANJA if "◐" in resultado else VERMELHO)
    box(slide, 0.35, top, 0.80, 0.56, fill_color=AZUL_ESC)
    txt(slide, hid, 0.35, top+0.06, 0.80, 0.44,
        size=18, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")
    box(slide, 1.17, top, 4.50, 0.56, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.5)
    txt(slide, enunciado, 1.22, top+0.07, 4.40, 0.44,
        size=13, font="Calibri Light", color=CINZA_ESC)
    box(slide, 5.69, top, 1.85, 0.56, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.5)
    txt(slide, resultado, 5.72, top+0.07, 1.80, 0.44,
        size=13, bold=True, color=cor_res, align=PP_ALIGN.CENTER, font="Calibri")
    box(slide, 7.56, top, 5.42, 0.56, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.5)
    txt(slide, evidencia, 7.60, top+0.07, 5.35, 0.44,
        size=12, font="Calibri Light", color=CINZA_ESC)

def num_slide(slide, n: int, total: int = 20):
    """Número do slide no canto inferior direito — usado na capa e encerramento."""
    txt(slide, f"{n} / {total}", 12.60, 7.18, 0.60, 0.26,
        size=10, bold=True, color=BRANCO,
        align=PP_ALIGN.RIGHT, font="Calibri")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 01 — CAPA  (identidade visual UDESC: verde + símbolo oficial)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)

# ── Coluna esquerda verde (1/4 da largura) ───────────────────────────────────
box(s, 0, 0, 3.33, 7.50, fill_color=VERDE_UDESC_ESC)

# Símbolo UDESC na coluna verde — centralizado verticalmente
# Proporção original: 1071×2111 → altura 2.80" → largura = 2.80 * (1071/2111) ≈ 1.42"
SYM_H = 2.60
SYM_W = SYM_H * (1071 / 2111)       # ≈ 1.32"
SYM_L = (3.33 - SYM_W) / 2          # centrado na coluna
SYM_T = (7.50 - SYM_H) / 2          # centrado verticalmente
s.shapes.add_picture(LOGO_SYMBOL, Inches(SYM_L), Inches(SYM_T),
                     Inches(SYM_W), Inches(SYM_H))

# Texto "UDESC" sob o símbolo
txt(s, "UDESC", SYM_L - 0.10, SYM_T + SYM_H + 0.10, SYM_W + 0.20, 0.38,
    size=14, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")

# 36º SIC na base da coluna
txt(s, "36º SIC", 0.10, 7.00, 3.10, 0.38,
    size=11, bold=False, color=BRANCO,
    align=PP_ALIGN.CENTER, font="Calibri Light")

# ── Faixa superior direita (nome da instituição) ─────────────────────────────
box(s, 3.33, 0, 10.00, 0.90, fill_color=VERDE_UDESC_ESC)
txt(s, "Universidade do Estado de Santa Catarina — UDESC",
    3.55, 0.05, 9.60, 0.40,
    size=12, bold=True, color=BRANCO, font="Calibri")
txt(s, "Centro de Ciências Tecnológicas — CCT  |  Programa de Pós-Graduação em Computação Aplicada — PPGCAP",
    3.55, 0.48, 9.60, 0.36,
    size=10, bold=False, color=BRANCO, font="Calibri Light")

# Logo horizontal UDESC (302×103) — canto superior direito
# Proporção: largura 2.0" → altura = 2.0 * (103/302) ≈ 0.68"
LOG_W = 2.00
LOG_H = LOG_W * (103 / 302)
s.shapes.add_picture(LOGO_HORIZ,
                     Inches(13.33 - LOG_W - 0.20), Inches(0.11),
                     Inches(LOG_W), Inches(LOG_H))

# ── Bloco de título (fundo verde escuro — texto branco) ──────────────────────
box(s, 3.33, 0.90, 10.00, 0.06, fill_color=VERDE_UDESC_CLR)   # linha divisória
box(s, 3.33, 0.96, 10.00, 3.38, fill_color=VERDE_UDESC_ESC)

txt(s, "ANALÍTICA PRESCRITIVA E IA EXPLICÁVEL",
    3.60, 1.08, 9.60, 0.82,
    size=28, bold=True, color=BRANCO,
    align=PP_ALIGN.LEFT, font="Calibri")
txt(s, "PARA A GESTÃO DE FROTAS PÚBLICAS",
    3.60, 1.88, 9.60, 0.72,
    size=25, bold=True, color=VERDE_UDESC_CLR,
    align=PP_ALIGN.LEFT, font="Calibri")
# linha clara sob título
box(s, 3.60, 2.62, 9.40, 0.04, fill_color=VERDE_UDESC_CLR)

txt(s, "Apoio à decisão em manutenção veicular com dados reais do Estado de Santa Catarina",
    3.60, 2.72, 9.60, 0.44,
    size=12.5, bold=False, italic=True, color=BRANCO,
    align=PP_ALIGN.LEFT, font="Calibri Light")
txt(s, "Métodos: analítica prescritiva  ·  grafos  ·  IA explicável  ·  MILP",
    3.60, 3.20, 9.60, 0.36,
    size=12, bold=False, color=BRANCO,
    align=PP_ALIGN.LEFT, font="Calibri Light")

# ── Bloco de identificação (fundo verde escuro — texto branco) ───────────────
box(s, 3.33, 4.34, 10.00, 0.04, fill_color=VERDE_UDESC_CLR)   # separador
box(s, 3.33, 4.38, 10.00, 2.08, fill_color=VERDE_UDESC_ESC)

dados = [
    ("Mestrando:",    "Eduardo Lopes Jonker"),
    ("Orientadora:",  "Profa. Dra. Vivian Kremer Kalempa"),
    ("Coorientador:", "Prof. Dr. Yuri Kaszubowski Lopes"),
]
for i, (label, valor) in enumerate(dados):
    t = 4.48 + i * 0.58
    txt(s, label, 3.52, t, 2.10, 0.42,
        size=13, bold=True, color=BRANCO, font="Calibri")
    txt(s, valor, 5.65, t, 7.55, 0.42,
        size=13, color=BRANCO, font="Calibri Light")

# ── Rodapé verde escuro ───────────────────────────────────────────────────────
box(s, 3.33, 6.50, 10.00, 1.00, fill_color=VERDE_UDESC_ESC)
txt(s, "Florianópolis — SC  ·  2026  ·  PPGCAP / CCT / UDESC",
    3.55, 6.65, 8.80, 0.40,
    size=12, bold=False, color=BRANCO,
    align=PP_ALIGN.CENTER, font="Calibri Light")
# número do slide — canto inferior direito
txt(s, f"{len(prs.slides)} / {TOTAL_SLIDES}", 12.30, 6.68, 0.90, 0.30,
    size=11, bold=True, color=VERDE_UDESC_CLR,
    align=PP_ALIGN.RIGHT, font="Calibri")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 02 — SUMÁRIO / ROTEIRO DA APRESENTAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "02", "Roteiro da Apresentação", "7 capítulos · 20 minutos")

box(s, 0.35, 1.52, 12.63, 5.18, fill_color=AZUL_CLR,
    border_color=CINZA_BOX, border_pt=0.5)

caps = [
    ("01", "Introdução",             "Contexto, problema, hipóteses e o que cada uma mostrou",          "≈ 3 min"),
    ("02", "Conceitos Fundamentais", "Literatura de base: ML, prescritiva, XAI, MILP",                  "≈ 2 min"),
    ("03", "Revisão da Literatura",  "Manutenção preditiva, decisão, explicabilidade e redes",          "≈ 2 min"),
    ("04", "Proposta",               "Arquitetura metodológica, pipeline de 9 etapas e formulação MILP", "≈ 4 min"),
    ("05", "Validação",              "Resultados empíricos: ML, anomalias, grafos, MILP, XAI",           "≈ 5 min"),
    ("06", "Discussões",             "Análise das hipóteses H1–H4, limitações e literatura",             "≈ 2 min"),
    ("07", "Conclusão",              "Contribuições, trabalhos futuros e considerações finais",           "≈ 2 min"),
]
top0 = 1.65
for i, (num, cap, desc, tempo) in enumerate(caps):
    t = top0 + i * 0.70
    box(s, 0.45, t, 0.72, 0.52, fill_color=AZUL_ESC)
    txt(s, num, 0.45, t+0.08, 0.72, 0.36,
        size=16, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")
    txt(s, cap, 1.22, t+0.07, 2.80, 0.38,
        size=14, bold=True, color=AZUL_ESC, font="Calibri")
    txt(s, desc, 4.08, t+0.09, 7.70, 0.35,
        size=12, font="Calibri Light", color=CINZA_ESC)
    txt(s, tempo, 11.85, t+0.09, 1.00, 0.35,
        size=11, bold=True, color=AZUL_MED, align=PP_ALIGN.RIGHT, font="Calibri")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 03 — VISÃO GERAL DA PESQUISA (slide novo — aproveitado do PDF de apoio)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "03", "Visão Geral da Pesquisa", "Problema, proposta, objeto e abordagem em uma página")

# 4 blocos 2×2
blocos = [
    (AZUL_ESC, BRANCO,    "🎯  PROBLEMA",
     ["Dados de patrimônio, manutenção e abastecimento",
      "estão dispersos em sistemas distintos.",
      "Sem integração é difícil estimar risco de falha,",
      "custo operacional e prioridade de intervenção.",
      "Resultado: orçamento alocado sem critério quantitativo."]),
    (AZUL_MED, BRANCO,    "💡  PROPOSTA",
     ["Arquitetura de analítica prescritiva + XAI que:",
      "▸  integra as 3 fontes administrativas (M + P + A)",
      "▸  compara modelos preditivos não lineares",
      "▸  explica previsões via SHAP e LIME",
      "▸  otimiza intervenções com MILP (solver HiGHS)"]),
    (VERDE,    BRANCO,    "📊  OBJETO EMPÍRICO",
     ["350.737 itens em 77.867 ordens de serviço (out/2020–ago/2026)",
      "7.580 veículos únicos  ·  71 meses de cobertura",
      "R$ 138,76 mi aprovados  ·  R$ 60,05 mi em glosas",
      "34.280 bens cadastrados  ·  ~1 milhão abastecimentos",
      "Painel veículo-mês: 51.244 instâncias para ML"]),
    (LARANJA,  BRANCO,    "🔬  ABORDAGEM",
     ["Pipeline de 9 etapas sequenciais e idempotentes",
      "Validação temporal Rolling-Origin (sem embaralhamento)",
      "Teste retido: período 2025–2026",
      "Comparações estatísticas pareadas (Wilcoxon + Holm)",
      "Resultado contrafactual — não é economia realizada"]),
]
coords = [(0.35, 1.55), (6.90, 1.55), (0.35, 4.10), (6.90, 4.10)]
for (l, t), (fc, tc, titulo, buls) in zip(coords, blocos):
    box(s, l, t, 6.30, 0.42, fill_color=fc)
    txt(s, titulo, l+0.12, t+0.06, 6.08, 0.32,
        size=13, bold=True, color=tc, font="Calibri")
    box(s, l, t+0.42, 6.30, 2.10, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.5)
    txt_multi(s, buls, l+0.15, t+0.50, 6.00, 1.95,
              size=12, font="Calibri Light", spacing_pt=4)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 04 — LACUNAS IDENTIFICADAS (slide novo — do PDF seção 3 + relatório)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "04", "Lacunas Identificadas na Literatura",
           "O que a pesquisa aborda que trabalhos anteriores não cobrem de forma integrada")

box(s, 0.35, 1.52, 12.63, 0.42, fill_color=AZUL_MED)
for col, label in [(0.37, "Lacuna"), (4.70, "Trabalhos anteriores"), (8.90, "O que esta pesquisa faz")]:
    txt(s, label, col+0.08, 1.56, 4.00, 0.34,
        size=12, bold=True, color=BRANCO, font="Calibri")

# Redação baseada no anteprojeto (Justificativa e seções 4.4/5.5) e em
# Mahale, Kolhar e More (2025); evita generalizações sem fonte.
lacunas = [
    ("Integração das 3 fontes\nde dados da frota",
     "Integração, previsão e decisão\ncostumam ser estudadas em separado",
     "Une manutenção + patrimônio +\nabastecimento por veículo"),
    ("Validação que respeita\no tempo",
     "Embaralhar os dados pode inflar\no desempenho em séries temporais",
     "Treino no passado, teste no futuro;\nteste retido 2025–2026"),
    ("Explicações avaliadas,\nnão só desenhadas",
     "Adoção de XAI ainda é desafio\nem manutenção veicular (Mahale, 2025)",
     "Mede a concordância entre\nSHAP e LIME (Jaccard e Spearman)"),
    ("Da previsão à decisão\nsob restrições",
     "Prever risco não diz qual\nintervenção fazer primeiro",
     "MILP com orçamento, capacidade\ne manutenção obrigatória"),
    ("Limites declarados\ncom clareza",
     "Economia simulada pode ser lida\ncomo economia realizada",
     "Resultados declarados como\nsimulação, com premissas visíveis"),
]
for i, (lac, ant, faz) in enumerate(lacunas):
    t = 2.00 + i * 0.90
    cor = AZUL_CLR if i % 2 == 0 else BRANCO
    box(s, 0.35, t, 12.63, 0.86, fill_color=cor,
        border_color=CINZA_BOX, border_pt=0.3)
    txt(s, lac, 0.45, t+0.08, 4.18, 0.70,
        size=12, bold=True, color=AZUL_ESC, font="Calibri")
    txt(s, ant, 4.68, t+0.08, 4.14, 0.70,
        size=11, font="Calibri Light", color=CINZA_ESC)
    txt(s, faz, 8.88, t+0.08, 4.02, 0.70,
        size=11, bold=False, color=VERDE, font="Calibri Light")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 05 — CONTRIBUIÇÕES E INOVAÇÃO (slide novo — do PDF seções 17-18 + caps 6-7 do PPTX)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "05", "Contribuições e Inovação",
           "O que este trabalho entrega ao meio científico e à gestão pública")

# 2 colunas
# col esq: contribuições científicas
box(s, 0.35, 1.55, 6.10, 0.40, fill_color=AZUL_ESC)
txt(s, "CONTRIBUIÇÕES CIENTÍFICAS", 0.45, 1.58, 5.90, 0.32,
    size=12, bold=True, color=BRANCO, font="Calibri")

contrib = [
    ("Empírica", "Base longitudinal com 350.737 itens em 77.867 OS;\nauditoria de 6.841 regressões de hodômetro;\ncorreção do campo de tipo de manutenção."),
    ("Metodológica", "Arquitetura completa auditoria → ML → XAI → MILP\ncom validação Rolling-Origin e testes estatísticos\npareados (Wilcoxon + Holm-Bonferroni)."),
    ("Compu-\ntacional", "Artefato reprodutível (repositório público);\nhomologado Linux × Windows 11 — resultados\nexatos ao centavo em 3 baterias independentes."),
    ("XAI", "Mede quanto SHAP e LIME concordam\nem dados reais de frota pública:\nJaccard Top-5 = 45,48%; Spearman ρ = 0,2869."),
]
for i, (tipo, desc) in enumerate(contrib):
    t = 2.02 + i * 1.12
    box(s, 0.35, t, 1.35, 0.95, fill_color=AZUL_MED)
    txt(s, tipo, 0.38, t+0.22, 1.28, 0.52,
        size=11, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")
    box(s, 1.72, t, 4.68, 0.95, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.4)
    txt(s, desc, 1.80, t+0.07, 4.52, 0.82,
        size=11, font="Calibri Light", color=CINZA_ESC)

# col dir: inovação e contribuição para gestão pública
box(s, 6.88, 1.55, 6.10, 0.40, fill_color=VERDE)
txt(s, "INOVAÇÃO E IMPACTO POTENCIAL", 6.98, 1.58, 5.90, 0.32,
    size=12, bold=True, color=BRANCO, font="Calibri")

inovacoes = [
    ("🔗 Integração aplicada",
     "Conecta 3 fontes administrativas heterogêneas\n(manutenção + patrimônio + abastecimento)\nem uma base única por veículo e mês."),
    ("💰 Prescritiva orçamentária",
     "Economia contrafactual no cenário S0:\nR$ 6.990.613,11 (13,66%) vs. linha de base.\nProjeção trienal 2027–29: R$ 40,09 mi.\n⚠ Resultado simulado — não é economia realizada."),
    ("🏛 Gestão pública",
     "242 veículos sinalizados para avaliação patrimonial.\n662 OS e 13.936 abastecimentos atípicos triados.\nFluxo: dados → análise → opções viáveis → gestor."),
    ("🔁 Reprodutibilidade",
     "Pipeline com 20 checkpoints validados.\n100% PASS em Linux e Windows 11.\nSub-repositório público para replicação."),
]
for i, (tipo, desc) in enumerate(inovacoes):
    t = 2.02 + i * 1.12
    box(s, 6.88, t, 1.52, 0.95, fill_color=VERDE)
    txt(s, tipo, 6.91, t+0.14, 1.46, 0.68,
        size=10, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")
    box(s, 8.42, t, 4.52, 0.95, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.4)
    txt(s, desc, 8.50, t+0.07, 4.36, 0.82,
        size=11, font="Calibri Light", color=CINZA_ESC)

nota(s, "Resultados condicionais às premissas do cenário S0 (2.000 veículos · 36 meses). "
        "Validação prospectiva necessária para confirmar impacto real.")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 06 — PROBLEMA E OBJETIVO (Cap. 1 do PPTX)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "06", "Cap. 1 | Problema e Objetivo",
           "Pergunta central: como priorizar manutenções com recursos limitados?")

# Pergunta de pesquisa em destaque
box(s, 0.35, 1.55, 12.63, 1.05, fill_color=AZUL_ESC)
txt(s, "Como integrar dados de patrimônio, manutenção e abastecimento para comparar modelos não lineares\n"
       "de previsão e, a partir deles, gerar recomendações de manutenção para uma frota pública\n"
       "sob restrições de custo, capacidade de oficina e segurança?",
    0.48, 1.60, 12.38, 0.95,
    size=13, bold=False, italic=True, color=BRANCO, font="Calibri Light")

# 3 colunas
bullet_col(s, "O PROBLEMA NOS DADOS",
           ["Ordens de serviço, custos, patrimônio e abastecimentos em sistemas distintos",
            "6.841 regressões de hodômetro em 3.116 veículos",
            "O campo de tipo de manutenção do sistema não reflete o serviço real",
            "R$ 198,81 mi orçados: R$ 138,76 mi aprovados e R$ 60,05 mi glosados"],
           0.35, 2.68, 4.00, 3.50, titulo_size=13, bullet_size=12)

bullet_col(s, "POR QUE ISSO IMPORTA",
           ["Veículos indisponíveis afetam serviços públicos essenciais",
            "Orçamento e capacidade das oficinas são limitados e disputados",
            "Decisões sem critério quantitativo aumentam custo total de propriedade",
            "Dados existem mas não estão integrados nem utilizados preditivamente"],
           4.47, 2.68, 4.10, 3.50, titulo_size=13, bullet_size=12)

bullet_col(s, "OBJETIVO CENTRAL",
           ["Desenvolver e avaliar arquitetura de analítica prescritiva + XAI",
            "Integrar patrimônio + manutenção + abastecimento",
            "Comparar múltiplos algoritmos não lineares (classificação e regressão)",
            "Gerar e avaliar recomendações com MILP sob restrições explícitas"],
           8.59, 2.68, 4.39, 3.50, titulo_size=13, bullet_size=12)

nota(s, "Resultados históricos descrevem o que aconteceu — não explicam sozinhos o que fazer a seguir.")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 07 — HIPÓTESES DE TRABALHO
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "07", "Cap. 1 | Hipóteses de Trabalho",
           "Quatro hipóteses com metas definidas: o que cada resultado mostrou")

# Enunciados curtos; decisão e evidência vêm de scripts/hipoteses_oficiais.py; ordem: da menos para a mais sustentada
import sys as _sys_h; _sys_h.path.insert(0, str(ROOT / "scripts")); import hipoteses_oficiais as HO  # noqa: E402
_V = HO.V
_SIMB = {"SUSTENTADA": "✓ Sustentada", "PARCIALMENTE SUSTENTADA": "◐ Parcial", "NÃO SUSTENTADA": "✗ Não sustentada"}
_ENUN = {
    "H1": ("Integrar o patrimônio melhora a previsão (anteprojeto) e reduz o MAE em ≥ 15% (limiar)",
           f"ROC-AUC {_V['h1_dif_roc']} (IC exclui zero); MAE {_V['h1_ganho_mae']} (meta 15%). Melhora real, mas pequena"),
    "H2": ("Ensembles de árvores são competitivos frente ao SVR-RBF (anteprojeto)",
           f"Superam o SVC-RBF na classificação (AUC {_V['h2_dif_auc_svc']}); erram {_V['h2_dif_mae_svr'].lstrip('+')} a mais que o SVR na regressão"),
    "H3": ("Política MILP reduz o custo frente à prática reconstruída e a heurísticas",
           f"S0: {_V['h3_economia_mi']} a menos ({_V['h3_economia_pct']}); heurística gulosa chega ao mesmo custo"),
    "H4": ("SHAP e LIME fiéis e estáveis (anteprojeto); concordância > 0,85 (limiar)",
           f"LIME pouco fiel (R² {_V['h4_lime_r2']}); Jaccard {_V['h4_jaccard']}; Spearman {_V['h4_spearman']}"),
}
for i, (hid, en, r, ev) in enumerate([(k, _ENUN[k][0], _SIMB[HO.H[k]["decisao"]], _ENUN[k][1]) for k in HO.ORDEM if k in _ENUN]):
    hipotese_row(s, hid, en, r, ev, 1.52 + i * 0.78)

# ── Adendo: por que a H4 foi refutada (linguagem simples) ────────────────────
box(s, 0.35, 4.58, 12.63, 0.42, fill_color=VERMELHO)
txt(s, "ADENDO  |  POR QUE A H4 NÃO FOI SUSTENTADA? (EM LINGUAGEM SIMPLES)",
    0.48, 4.62, 12.40, 0.34,
    size=14, bold=True, color=BRANCO, font="Calibri")

adendo = [
    ("O QUE COMPARAMOS",
     "SHAP e LIME são como duas lupas que mostram quais informações mais "
     "pesaram em cada previsão do modelo. Esperávamos que as duas apontassem "
     "os mesmos fatores."),
    ("O QUE ENCONTRAMOS",
     "Nos 5 fatores mais importantes, a coincidência foi de apenas 45,48% "
     "(índice de Jaccard). A concordância na ordem também foi fraca: 0,37, numa "
     "escala em que 1 seria concordância total."),
    ("POR QUE ISSO IMPORTA",
     "As duas tentam explicar a mesma coisa, mas chegaram a respostas "
     "diferentes. Por isso, uma não confirma a outra, e a explicação não "
     "prova causa. Não confirmar também é resultado científico."),
]
for i, (tit, corpo) in enumerate(adendo):
    l = 0.35 + i * 4.28
    box(s, l, 5.04, 4.07, 1.62, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.5)
    txt(s, tit, l + 0.12, 5.08, 3.83, 0.32,
        size=12, bold=True, color=VERMELHO, font="Calibri")
    txt(s, corpo, l + 0.12, 5.38, 3.83, 1.25,
        size=13, color=CINZA_ESC, font="Calibri Light")

nota(s, "Resultado refere-se aos dados e ao protocolo deste estudo; não prova que um método seja melhor que o outro.")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 08 — ENTENDENDO A HIPÓTESE H4 (explicação para leigos, com figura)
# Fontes: relatorio_explicabilidade_xai.json (observado) e
#         matriz_validacao_hipoteses.csv (meta > 85%)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "08", "Cap. 1 | Entendendo a Hipótese H4",
           "Por que SHAP e LIME não concordaram e o que isso significa")

# Figura (esquerda): proporção original 1804 x 1100
IMG_W = 8.10
IMG_HH = IMG_W * 1100 / 1804
s.shapes.add_picture(IMG_H4, Inches(0.35), Inches(1.52), Inches(IMG_W), Inches(IMG_HH))

# Texto (direita): 3 blocos curtos
blocos_h4 = [
    ("MESMA PREVISÃO, DUAS EXPLICAÇÕES", AZUL_ESC,
     "SHAP e LIME recebem a mesma previsão e apontam os 5 fatores que mais "
     "pesaram nela. Cada um usa um método diferente."),
    ("A META NÃO FOI ATINGIDA", VERMELHO,
     "A meta da hipótese era concordância acima de 85%. Resultado: 45,5% de "
     "coincidência e correlação de 0,37 (meta: 0,85)."),
    ("O QUE MUDA NA PRÁTICA", VERDE,
     "Um método não confirma o outro. Por isso, recomenda-se usar os dois em "
     "conjunto (triangulação) e tratar a explicação como pista, não como causa."),
]
for i, (tit, cor, corpo) in enumerate(blocos_h4):
    t = 1.52 + i * 1.66
    box(s, 8.62, t, 4.36, 0.40, fill_color=cor)
    txt(s, tit, 8.72, t + 0.04, 4.16, 0.32,
        size=12, bold=True, color=BRANCO, font="Calibri")
    box(s, 8.62, t + 0.40, 4.36, 1.14, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.5)
    txt(s, corpo, 8.72, t + 0.44, 4.16, 1.08,
        size=13, color=CINZA_ESC, font="Calibri Light")

nota(s, "Ilustração do processo, sem caso específico. Valores: relatório de explicabilidade XAI "
        "(HistGradientBoosting) e matriz de validação de hipóteses do projeto.")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 09 — QUANDO A HIPÓTESE NÃO SE CONFIRMA
# Fontes: README do repositório público (avaliação "sem HARKing") e anteprojeto
#         (seção 6: "todos são resultados cientificamente válidos").
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "09", "Cap. 1 | Quando a hipótese não se confirma",
           "Um resultado negativo também é resultado científico: o que cada um ensinou")

# Tabela (esquerda): H1, H2 e H4
cols_x = [0.35, 1.15, 3.25, 5.35]
cols_w = [0.78, 2.08, 2.08, 2.80]
box(s, 0.35, 1.52, 7.80, 0.42, fill_color=AZUL_ESC)
for x, w, h in zip(cols_x, cols_w, ["", "Meta", "Obtido", "O que aprendemos"]):
    txt(s, h, x + 0.06, 1.56, w - 0.12, 0.34,
        size=13, bold=True, color=BRANCO, font="Calibri")

_NC = {
    "H1": ("Melhorar a previsão; reduzir o MAE em ≥ 15%", f"ROC-AUC {_V['h1_dif_roc']}; MAE {_V['h1_ganho_mae']}",
           "Integrar patrimônio ajuda pouco. A melhora existe, mas não chega à meta."),
    "H2": ("Ser competitivo frente ao SVR-RBF", f"Melhor na classificação; {_V['h2_dif_mae_svr'].lstrip('+')} pior na regressão",
           "Não há modelo campeão único: a escolha depende da tarefa."),
    "H4": ("Explicações fiéis e estáveis; concordância > 0,85", f"LIME R² {_V['h4_lime_r2']}; Jaccard {_V['h4_jaccard']}",
           "O LIME é estável, mas não reproduz o modelo. Usar o SHAP na auditoria."),
}
_COR = {"NÃO SUSTENTADA": VERMELHO, "PARCIALMENTE SUSTENTADA": LARANJA}
linhas_nc = [(k, _COR[HO.H[k]["decisao"]], *_NC[k]) for k in HO.ORDEM if k in _NC and HO.H[k]["decisao"] in _COR]
for i, (hid, cor, meta, obt, apr) in enumerate(linhas_nc):
    t = 1.98 + i * 1.20
    box(s, cols_x[0], t, cols_w[0], 1.14, fill_color=cor)
    txt(s, hid, cols_x[0], t + 0.34, cols_w[0], 0.46,
        size=20, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")
    for x, w, conteudo, negrito in [(cols_x[1], cols_w[1], meta, False),
                                    (cols_x[2], cols_w[2], obt, True),
                                    (cols_x[3], cols_w[3], apr, False)]:
        box(s, x, t, w, 1.14, fill_color=CINZA_CLR if i % 2 == 0 else BRANCO,
            border_color=CINZA_BOX, border_pt=0.5)
        txt(s, conteudo, x + 0.08, t + 0.06, w - 0.16, 1.02,
            size=12, bold=negrito, color=cor if negrito else CINZA_ESC,
            font="Calibri" if negrito else "Calibri Light")

# Glossário (abaixo da tabela)
box(s, 0.35, 5.62, 7.80, 0.98, fill_color=AZUL_CLR,
    border_color=AZUL_MED, border_pt=0.8)
txt(s, "HARKing", 0.48, 5.66, 2.0, 0.32,
    size=13, bold=True, color=AZUL_ESC, font="Calibri")
txt(s, "Ajustar a hipótese ou a meta depois de ver o resultado, para parecer que deu "
       "certo. Aqui, as metas foram mantidas e o resultado foi reportado como saiu.",
    0.48, 5.96, 7.55, 0.62,
    size=12.5, color=CINZA_ESC, font="Calibri Light")

# Coluna da direita: como o resultado é tratado
blocos_nc = [
    ("AS METAS NÃO FORAM MOVIDAS", AZUL_ESC,
     "Os limiares de 15% (H1) e 85% (H4), fixados na dissertação antes da avaliação, "
     "foram mantidos. Ajustá-los para caber nos dados seria HARKing."),
    ("ISSO TAMBÉM É RESULTADO", AZUL_MED,
     "O anteprojeto já previa: nenhum ganho era antecipado e todo resultado é "
     "cientificamente válido. Não confirmar mostra até onde os dados sustentam a hipótese."),
    ("EFEITO NAS CONCLUSÕES", VERDE,
     "Ficam proporcionais à evidência: ganho de integração pequeno, XAI com os dois "
     "métodos em conjunto e economia do MILP tratada como simulação."),
]
for i, (tit, cor, corpo) in enumerate(blocos_nc):
    t = 1.52 + i * 1.72
    box(s, 8.45, t, 4.53, 0.40, fill_color=cor)
    txt(s, tit, 8.55, t + 0.04, 4.33, 0.32,
        size=12, bold=True, color=BRANCO, font="Calibri")
    box(s, 8.45, t + 0.40, 4.53, 1.22, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.5)
    txt(s, corpo, 8.55, t + 0.44, 4.33, 1.16,
        size=13, color=CINZA_ESC, font="Calibri Light")

nota(s, "Critérios fixados antes dos resultados: texto do anteprojeto e limiar da qualificação. "
        "Sustentada = atende os dois; parcial = atende um. H3: sustentada no S0 (simulação).")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — CONCEITOS FUNDAMENTAIS (Cap. 2)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "08", "Cap. 2 | Conceitos Fundamentais",
           "Literatura consolidada que sustenta as escolhas metodológicas")

cols = [
    ("APRENDIZADO DE MÁQUINA", AZUL_ESC,
     ["Random Forest — Breiman (2001): agrega árvores com amostras aleatórias",
      "Extra Trees — Geurts et al. (2006): aleatoriza também os cortes",
      "HistGradientBoosting: boosting com binning de histogramas (eficiente)",
      "SVR-RBF — Cortes & Vapnik (1995): margem com kernel não linear",
      "⚠  Nenhum método é garantido — comparação empírica é central"]),
    ("ANALÍTICA PRESCRITIVA", AZUL_MED,
     ["Bertsimas & Kallus (2020): otimização estocástica condicional a previsões",
      "MILP: variáveis 0/1 por veículo × período",
      "Minimizar custo preventivo + risco residual esperado",
      "Sujeito a: orçamento Bₜ, capacidade Hₜ, elegibilidade eᵢₜ",
      "Solver HiGHS: Dual Simplex + Branch-and-Bound"]),
    ("XAI E VALIDAÇÃO", VERDE,
     ["SHAP — Lundberg & Lee (2017): decomposição aditiva de Shapley",
      "LIME — Ribeiro et al. (2016): surrogate local por perturbação",
      "Importância por permutação: referência model-agnostic global",
      "Rolling-Origin: treino no passado → teste no futuro (causalidade)",
      "Wilcoxon pareado: comparação estatística nos mesmos blocos"]),
]
for i, (tit, cor, buls) in enumerate(cols):
    l = 0.35 + i * 4.30
    box(s, l, 1.55, 4.10, 0.40, fill_color=cor)
    txt(s, tit, l+0.10, 1.58, 3.90, 0.32,
        size=11, bold=True, color=BRANCO, font="Calibri")
    box(s, l, 1.97, 4.10, 4.60, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.4)
    txt_multi(s, ["▸  " + b for b in buls],
              l+0.12, 2.04, 3.88, 4.46,
              size=12, font="Calibri Light", spacing_pt=5)

nota(s, "Formulação MILP (anteprojeto, 5.4):  min Σᵢₜ [ cᴹᵢₜ xᵢₜ + ((1−xᵢₜ)p⁰ᵢₜ + xᵢₜp¹ᵢₜ)(cᶠᵢₜ + cᴰᵢₜ) ]   sujeito a xᵢₜ ∈ {0,1}",
     icone="Σ", cor=AZUL_ESC)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 09 — REVISÃO DA LITERATURA (Cap. 3)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "09", "Cap. 3 | O que esta pesquisa acrescenta",
           "Contribuição está na integração aplicada e na avaliação — não na invenção dos algoritmos")

# Tabela de posicionamento
headers = ["Eixo", "Referências anteriores", "Aplicação neste estudo", "Contribuição e limite"]
widths  = [2.20, 3.80, 3.60, 3.03]
lefts   = [0.35, 2.57, 6.39, 10.01]

box(s, 0.35, 1.55, 12.63, 0.44, fill_color=AZUL_ESC)
for lft, wid, hdr in zip(lefts, widths, headers):
    txt(s, hdr, lft+0.08, 1.58, wid-0.16, 0.36,
        size=12, bold=True, color=BRANCO, font="Calibri")

rows = [
    ("Manutenção\ne decisão",
     "De Castro & Cavalca (2006);\nBertsimas & Kallus (2020)",
     "Risco+custo estimados com escolhas\nsob orçamento e capacidade reais",
     "Dados de SC; S0 é simulação,\nnão piloto operacional"),
    ("Explicabilidade",
     "Lundberg & Lee (2017): SHAP;\nRibeiro et al. (2016): LIME;\nRudin (2019): cautela em decisões",
     "Compara SHAP e LIME com\nconcordância Jaccard: 45,48%",
     "Comparação não prova causalidade\nnem superioridade universal"),
    ("Validação e redes",
     "Bergmeir & Benítez (2012): validação\ntemporal; Blondel et al. (2008): Louvain;\nGarcia (2019): TCU",
     "Avaliação temporal + protótipo\nNeo4j local para relações de frota",
     "Louvain reproduzido no grafo\nNeo4j e testado contra nulo"),
    ("Manutenção preditiva\nveicular",
     "Mahale et al. (2025): revisão de\n94 estudos; Katreddi et al. (2023):\ncaminhões XGBoost vs RF",
     "Dados tabulares reais de frota\npública com validação OOT estrita",
     "Resultado condicionado ao\nperíodo e à frota de SC"),
]
for i, row in enumerate(rows):
    t = 2.05 + i * 1.12
    cor = CINZA_CLR if i % 2 == 0 else BRANCO
    for j, (lft, wid, cell) in enumerate(zip(lefts, widths, row)):
        box(s, lft, t, wid, 1.08, fill_color=cor,
            border_color=CINZA_BOX, border_pt=0.3)
        txt(s, cell, lft+0.08, t+0.08, wid-0.16, 0.92,
            size=11, bold=(j == 0), color=AZUL_ESC if j == 0 else CINZA_ESC,
            font="Calibri" if j == 0 else "Calibri Light")

nota(s, "Síntese: integração aplicada + validação temporal + restrições explícitas + análise dos limites")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — BASE EMPÍRICA (Cap. 4)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "10", "Cap. 4 | Base Empírica — Santa Catarina",
           "Ordens, itens e veículos são unidades diferentes; cada fonte tem cobertura própria")

# KPIs
kpi_box(s, "350.737",    "itens de manutenção\n(em 77.867 OS)",       0.35, 1.58)
kpi_box(s, "7.580",      "veículos únicos\n(placas identificadas)",   3.27, 1.58)
kpi_box(s, "R$ 138,76 mi", "gastos aprovados\nno período auditado",   6.19, 1.58, val_color=VERDE)
kpi_box(s, "R$ 60,05 mi",  "glosados pela fiscalização\n(orçado − aprovado)", 9.11, 1.58, val_color=VERMELHO)

# Auditoria
bullet_col(s, "AUDITORIA DOS DADOS",
           ["6.841 regressões de hodômetro em 3.116 veículos",
            "Pelo código real: 270.510 corretivas e 37.897 preventivas",
            "Campo TRIM(ds_codigo_manutencao) recupera o sinal real",
            "SHA-256 verificado na entrada do pipeline"],
           0.35, 3.10, 5.90, 3.00, titulo_size=13, bullet_size=12)

bullet_col(s, "FONTES INTEGRADAS",
           ["Manutenção (M): 77.867 OS únicas · 69 colunas brutas",
            "Patrimônio (P): 34.280 bens · valor venal e depreciação SEA/SC",
            "Abastecimento (A): ~1 milhão de transações processadas",
            "Painel veículo-mês: 51.244 instâncias para modelagem ML"],
           6.43, 3.10, 6.55, 3.00, titulo_size=13, bullet_size=12)

nota(s, "Resultados do Poder Executivo de SC não se transferem automaticamente para outros estados/órgãos.")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — PIPELINE METODOLÓGICO (Cap. 4)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "11", "Cap. 4 | Pipeline de 9 Etapas",
           "Cada script é autossuficiente, idempotente e rastreável")

etapas = [
    ("01", "Auditoria Forense",   "SHA-256 · hodômetro · completude"),
    ("02", "Pré-processamento",   "Saneamento · feature engineering"),
    ("03", "Análise Descritiva",  "Lilliefors · não gaussiano → não linear"),
    ("04", "Modelos Preditivos",  "HistGB · RF · ET · DT · LR · Rolling-Origin"),
    ("05", "Anomalias",           "Isolation Forest · estabilidade Jaccard 0,86–0,88"),
    ("06", "Teoria dos Grafos",   "Bipartido · Louvain Q=0,5646 · 18 comunidades"),
    ("07", "Explicabilidade XAI", "SHAP TreeExplainer · LIME · Permutação"),
    ("08", "Otimização MILP",     "PuLP + HiGHS · 5 cenários (50%–150%)"),
    ("09", "Validação Estatística","Wilcoxon · DeLong · Holm-Bonferroni"),
]
# 2 linhas: 5 + 4
for i, (num, nome, desc) in enumerate(etapas):
    col = i if i < 5 else i - 5
    row = 0 if i < 5 else 1
    l = 0.30 + col * 2.55
    t = 1.60 + row * 2.60
    w = 2.42
    box(s, l, t, w, 0.46, fill_color=AZUL_ESC)
    tb_num = txt(s, num, l+0.04, t+0.07, 0.50, 0.32,
                 size=14, bold=True, color=AZUL_CLR, font="Calibri")
    tb_num.text_frame.word_wrap = False
    txt(s, nome, l+0.52, t+0.08, w-0.60, 0.30,
        size=11, bold=True, color=BRANCO, font="Calibri")
    box(s, l, t+0.46, w, 1.65, fill_color=CINZA_CLR,
        border_color=CINZA_BOX, border_pt=0.4)
    txt(s, desc, l+0.10, t+0.54, w-0.20, 1.50,
        size=11, font="Calibri Light", color=CINZA_ESC)

nota(s, "Ordem no tempo: treino com o histórico, depois validação e, por fim, teste no período retido 2025–2026 (sem embaralhar).")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — RESULTADOS: MODELOS PREDITIVOS (Cap. 5)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "12", "Cap. 5 | Modelos Preditivos — Resultados",
           "Classificação de risco e regressão de custo — teste retido 2025–2026")

# Tabela classificação
box(s, 0.35, 1.55, 6.10, 0.40, fill_color=AZUL_ESC)
txt(s, "CLASSIFICAÇÃO DE RISCO  (prevalência 78,77%)", 0.45, 1.58, 6.00, 0.32,
    size=12, bold=True, color=BRANCO, font="Calibri")

headers_cl = ["Modelo", "PR-AUC", "ROC-AUC", "Brier", "ECE"]
widths_cl  = [2.20, 0.90, 0.90, 0.80, 0.80]
lefts_cl   = [0.35, 2.57, 3.49, 4.41, 5.23]
box(s, 0.35, 1.97, 6.08, 0.36, fill_color=AZUL_MED)
for lft, wid, h in zip(lefts_cl, widths_cl, headers_cl):
    txt(s, h, lft+0.04, 2.00, wid-0.08, 0.28,
        size=10, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")

rows_cl = [
    ("HistGB ★", "0,9099", "0,8064", "0,1334", "0,0238", VERDE),
    ("Random Forest", "0,9081", "0,8016", "0,1362", "0,0660", CINZA_ESC),
    ("Árvore Decisão", "0,9041", "0,7905", "0,1378", "0,1303", CINZA_ESC),
    ("Extra Trees",    "0,8796", "0,7631", "0,1710", "0,2381", CINZA_ESC),
    ("Reg. Logística", "0,8660", "0,8292", "0,1673", "0,2258", CINZA_ESC),
    ("Baseline",       "0,7924", "0,5000", "0,1873", "0,0390", LARANJA),
]
for i, (m, pr, roc, br, ece, cor) in enumerate(rows_cl):
    t = 2.35 + i * 0.47
    bg_c = CINZA_CLR if i % 2 == 0 else BRANCO
    box(s, 0.35, t, 6.08, 0.44, fill_color=bg_c,
        border_color=CINZA_BOX, border_pt=0.2)
    for lft, wid, val in zip(lefts_cl, widths_cl,
                             [m, pr, roc, br, ece]):
        bold_v = (i == 0)
        aln = PP_ALIGN.CENTER if lft > 0.50 else PP_ALIGN.LEFT
        txt(s, val, lft+0.04, t+0.08, wid-0.08, 0.28,
            size=11, bold=bold_v, color=cor if lft < 0.50 else (VERDE if i == 0 else CINZA_ESC),
            align=aln, font="Calibri" if bold_v else "Calibri Light")

# Tabela regressão
box(s, 6.78, 1.55, 6.20, 0.40, fill_color=AZUL_ESC)
txt(s, "REGRESSÃO DE CUSTO  (sem regressão linear)", 6.88, 1.58, 6.00, 0.32,
    size=12, bold=True, color=BRANCO, font="Calibri")

headers_rg = ["Modelo", "MAE (R$)", "RMSE (R$)", "R²"]
widths_rg  = [2.30, 1.40, 1.40, 0.90]
lefts_rg   = [6.78, 9.10, 10.52, 11.94]
box(s, 6.78, 1.97, 6.18, 0.36, fill_color=AZUL_MED)
for lft, wid, h in zip(lefts_rg, widths_rg, headers_rg):
    txt(s, h, lft+0.04, 2.00, wid-0.08, 0.28,
        size=10, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")

rows_rg = [
    ("HistGB ★", "2.311,82", "4.363,75", "0,099", VERDE),
    ("Rand. Forest","2.353,31","4.426,50", "0,073", CINZA_ESC),
    ("Extra Trees", "2.354,89","4.441,20", "0,067", CINZA_ESC),
    ("Árvore Reg.", "2.407,47","4.566,07", "0,014", CINZA_ESC),
    ("Mediana hist.","2.209,02","4.811,12","−0,095",LARANJA),
]
for i, (m, mae, rmse, r2, cor) in enumerate(rows_rg):
    t = 2.35 + i * 0.47
    bg_c = CINZA_CLR if i % 2 == 0 else BRANCO
    box(s, 6.78, t, 6.18, 0.44, fill_color=bg_c,
        border_color=CINZA_BOX, border_pt=0.2)
    for lft, wid, val in zip(lefts_rg, widths_rg, [m, mae, rmse, r2]):
        bold_v = (i == 0)
        aln = PP_ALIGN.CENTER if lft > 7.00 else PP_ALIGN.LEFT
        txt(s, val, lft+0.04, t+0.08, wid-0.08, 0.28,
            size=11, bold=bold_v,
            color=cor if lft < 7.00 else (VERDE if i == 0 else CINZA_ESC),
            align=aln, font="Calibri" if bold_v else "Calibri Light")

# Ablação
box(s, 0.35, 5.22, 12.63, 0.36, fill_color=AZUL_MED)
txt(s, "ESTUDO DE ABLAÇÃO — Fontes M vs M+P", 0.45, 5.25, 7.00, 0.28,
    size=11, bold=True, color=BRANCO, font="Calibri")
txt(s, "Classificação: PR-AUC 0,9060 → 0,9099  (+0,43%)    "
       "Regressão: MAE R$ 2.237,81 → R$ 2.223,84  (−R$ 13,97/mês)",
    0.45, 5.62, 12.45, 0.35,
    size=12, bold=False, color=AZUL_ESC, font="Calibri")

txt(s, "Outro protocolo do projeto (5 dobras temporais, usado na homologação Linux × Windows) reporta "
       "ROC-AUC 0,8737 e PR-AUC 0,9510. Valores de protocolos diferentes não se comparam.",
    0.45, 6.02, 12.45, 0.62,
    size=11, italic=True, color=CINZA_ESC, font="Calibri Light")

nota(s, "Wilcoxon + Holm: HistGB difere de Árvore, Extra Trees e Random Forest (p ajustado < 10⁻⁴). "
        "Frente ao SVR-RBF, os ensembles perdem na regressão (H2 não sustentada).")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — ANOMALIAS, GRAFOS E XAI (Cap. 5)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "13", "Cap. 5 | Anomalias · Grafos · Explicabilidade",
           "Triagem não supervisionada, estrutura relacional e comparação de métodos XAI")

# 3 colunas
bullet_col(s, "ISOLATION FOREST",
           ["Estabilidade: com ν de 1% a 10% e 3 sementes, Jaccard de 0,86 a 0,88",
            "Modelo final (ν = 0,85%): 662 OS e 13.936 abastecimentos sinalizados",
            "OS reprovadas × aprovadas: escores quase iguais (−0,412 × −0,415)",
            "Teste t significativo (p = 0,0004), mas a diferença é mínima",
            "⚠ Sinaliza casos para revisão — não prova fraude"],
           0.35, 1.55, 4.10, 5.17, titulo_size=13, bullet_size=12)

bullet_col(s, "TEORIA DOS GRAFOS",
           ["Rede bipartida: veículos ↔ oficinas (NetworkX)",
            "Protótipo Neo4j: 7.291 veículos com serviço · 1.039 oficinas",
            "25.122 ligações veículo–oficina observadas",
            "Louvain: Q = 0,5646 · 18 comunidades",
            "Validado: Q nulo 0,392 (z = 39,9), estável",
            "⚠ Descreve a rede — não prova conluio"],
           4.50, 1.55, 4.15, 5.17, titulo_size=13, bullet_size=12)

bullet_col(s, "EXPLICABILIDADE XAI",
           ["SHAP TreeExplainer: valores de Shapley globais e locais",
            "LIME: surrogate local por perturbação sintética",
            "Concordância Jaccard Top-5: 45,48%",
            "Spearman ρ = 0,2869",
            "→ H4 NÃO SUSTENTADA: os dois métodos divergem",
            "⚠ Importância preditiva ≠ efeito causal"],
           8.68, 1.55, 4.30, 5.17, titulo_size=13, bullet_size=12)

nota(s, "Resultados da rede Neo4j (protótipo local): IDs pseudonimizados com HMAC-SHA-256.")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — MILP E CENÁRIOS (Cap. 5)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "14", "Cap. 5 | Otimização Prescritiva — MILP",
           "Custo esperado por política no cenário S0 (solver HiGHS)")

# Tabela de cenários — Experimento A (sensibilidade ao orçamento)
txt(s, "A · Políticas comparadas sob o mesmo orçamento e capacidade",
    0.35, 1.48, 10.33, 0.36,
    size=13, bold=True, color=AZUL_ESC, font="Calibri")

hds = ["Política", "Custo (36 meses)", "Obrig.", "Dif. p/ MILP", "Economia"]
ws  = [2.60, 2.30, 1.30, 2.10, 1.95]
ls  = [0.35, 2.97, 5.29, 6.61, 8.73]
TAB_T = 1.88

box(s, 0.35, TAB_T, 10.33, 0.40, fill_color=AZUL_ESC)
for lft, wid, h in zip(ls, ws, hds):
    txt(s, h, lft+0.06, TAB_T+0.03, wid-0.12, 0.32,
        size=11, bold=True, color=BRANCO, align=PP_ALIGN.CENTER, font="Calibri")

cen_rows = [
    ("Prática reconstruída", "R$ 51.180.733,62", "100%", "R$ 6.990.613,11", "—", LARANJA),
    ("Heurística gulosa", "R$ 44.190.884,80", "100%", "R$ 764,29", "6,99 mi", CINZA_ESC),
    ("MILP (HiGHS) ★", "R$ 44.190.120,51", "100%", "—", "13,66%", VERDE),
]
for i, row_data in enumerate(cen_rows):
    vals = row_data[:-1]; cor = row_data[-1]
    t = TAB_T + 0.42 + i * 0.60
    bg_c = CINZA_CLR if i % 2 == 0 else BRANCO
    box(s, 0.35, t, 10.33, 0.56, fill_color=bg_c,
        border_color=CINZA_BOX, border_pt=0.2)
    for lft, wid, val in zip(ls, ws, vals):
        bold_v = (i == len(cen_rows) - 1)
        txt(s, val, lft+0.06, t+0.12, wid-0.12, 0.34,
            size=12, bold=bold_v, color=cor, align=PP_ALIGN.CENTER,
            font="Calibri" if bold_v else "Calibri Light")

# Experimento B — cenário S0 (quadro à direita)
txt(s, "B · Cenário S0", 10.80, 1.48, 2.20, 0.36,
    size=13, bold=True, color=AZUL_ESC, font="Calibri")
box(s, 10.80, 1.88, 2.18, 4.60, fill_color=AZUL_ESC)
txt_multi(s,
    ["2.000 veículos", "36 meses", "",
     "Prática reconstruída", "R$ " + "51,18 mi", "MILP", "R$ 44,19 mi", "",
     "Redução", "R$ 6,99 mi (13,66%)", "",
     "Instância", "semissintética", "(custos por fórmula)"],
    10.88, 1.96, 2.04, 4.46,
    size=12, color=BRANCO, font="Calibri", spacing_pt=2)

nota(s, "Simulação com 2.000 veículos reais e custos gerados por fórmula. Não é economia realizada.")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — DISCUSSÃO (Cap. 6)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "15", "Cap. 6 | Discussões",
           "O que os resultados permitem e o que não permitem afirmar")

bullet_col(s, "LIMITAÇÕES RECONHECIDAS",
           ["Economia do MILP é simulada (cenário S0); não é economia realizada",
            "Eficácia da manutenção preventiva não foi medida com dados reais; usaram-se cenários",
            "H1 e H2 não atingiram as metas: integrar patrimônio ajuda pouco e a mediana vence no MAE",
            "Resultados valem para a frota de SC no período auditado",
            "242 veículos são candidatos à avaliação, não decisão de leilão"],
           0.35, 1.55, 6.10, 4.60, titulo_size=13, bullet_size=12)

bullet_col(s, "LEITURA À LUZ DA LITERATURA",
           ["Mahale et al. (2025): dados e XAI seguem como desafios; aqui ambos foram testados com dados reais",
            "Bertsimas & Kallus (2020): avaliar pela decisão; por isso o MILP é comparado à linha de base",
            "Explicações podem divergir com atributos correlacionados: coerente com a H4 não sustentada",
            "Rudin (2019): cautela com explicações pós-hoc; aqui a explicação é pista, não prova",
            "Embaralhar dados temporais infla o desempenho; por isso o teste é no período mais recente"],
           6.58, 1.55, 6.40, 4.60, titulo_size=13, bullet_size=12)

box(s, 0.35, 6.25, 12.63, 0.44, fill_color=LARANJA)
txt(s, "Fluxo proposto:  dados  →  análise  →  alternativas viáveis  →  revisão humana  →  decisão do gestor. "
       "O sistema apoia — não substitui — critérios de segurança e julgamento técnico.",
    0.48, 6.28, 12.42, 0.36,
    size=11, bold=False, italic=True, color=BRANCO, font="Calibri Light")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — CONCLUSÃO (Cap. 7)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "16", "Cap. 7 | Conclusão",
           "Contribuições integradas, trabalhos futuros e considerações finais")

bullet_col(s, "PRINCIPAIS CONTRIBUIÇÕES",
           ["Empírica: base de 350.737 itens em 77.867 OS, com correção do tipo de manutenção",
            "Metodológica: auditoria → ML → XAI → MILP com validação temporal e Wilcoxon",
            "Computacional: artefato reprodutível, homologado Linux × Windows, exato ao centavo",
            "XAI: SHAP e LIME concordaram só 45,48% no Top-5; usar os dois em conjunto",
            "Gestão pública: política prescritiva R$ 6,99 mi (13,66%) no cenário S0, como simulação"],
           0.35, 1.55, 6.10, 4.70, titulo_size=13, bullet_size=12)

bullet_col(s, "TRABALHOS FUTUROS",
           ["Validação prospectiva em período real de operação da frota",
            "Extensão do modelo de Markov para tipos de falha com granularidade maior",
            "Telemetria IoT em tempo real para atualização dinâmica dos parâmetros de risco",
            "Avaliação com especialistas em manutenção sobre SHAP e LIME",
            "Generalização para outras frotas estaduais com estrutura de dados similar"],
           6.58, 1.55, 6.40, 4.70, titulo_size=13, bullet_size=12)

box(s, 0.35, 6.28, 12.63, 0.44, fill_color=VERDE)
txt(s, "\"É possível conectar dados administrativos heterogêneos, modelos preditivos não lineares e otimização "
       "prescritiva em um artefato auditável e reprodutível que apoia — sem substituir — a decisão do gestor.\"",
    0.48, 6.31, 12.42, 0.36,
    size=11, bold=False, italic=True, color=BRANCO, font="Calibri Light")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — REFERÊNCIAS
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)
header_bar(s, "17", "Referências Principais",
           "Seleção resumida; referências completas estão na dissertação")

refs_esq = [
    "BERTSIMAS, D.; KALLUS, N. From predictive to prescriptive analytics. Management Science, 66(3), 2020.",
    "DE CASTRO, H. F.; CAVALCA, K. L. Maintenance resources optimization applied to a manufacturing system. Reliab. Eng. Syst. Saf., 91(4), 2006.",
    "MAHALE, Y.; KOLHAR, S.; MORE, A. S. AI driven predictive maintenance in vehicles: a review. Discover Applied Sciences, 7, 2025.",
    "RUDIN, C. Stop explaining black box machine learning models for high stakes decisions. Nature Machine Intelligence, 1, 2019.",
    "LUNDBERG, S. M.; LEE, S.-I. A unified approach to interpreting model predictions. NeurIPS, 2017.",
    "RIBEIRO, M. T.; SINGH, S.; GUESTRIN, C. \"Why should I trust you?\" KDD, 2016.",
]
refs_dir = [
    "BERGMEIR, C.; BENÍTEZ, J. M. On the use of cross-validation for time series. Information Sciences, 2012.",
    "BLONDEL, V. D. et al. Fast unfolding of communities in large networks. J. Stat. Mech., 2008.",
    "FRIEDMAN, J. H. Greedy function approximation: a gradient boosting machine. Ann. Statistics, 2001.",
    "GARCIA, L. M. O uso de ferramentas de Data Analytics pelo Auditor Governamental. ISC/TCU, 2019.",
    "HUANGFU, Q.; HALL, J. A. J. Parallelizing the dual revised simplex method. Math. Prog. Comp., 2018.",
    "LIU, F. T.; TING, K. M.; ZHOU, Z.-H. Isolation forest. IEEE ICDM, 2008.",
]
box(s, 0.35, 1.55, 12.63, 0.36, fill_color=AZUL_MED)
txt(s, "DECISÃO E MANUTENÇÃO  ·  EXPLICABILIDADE  ·  VALIDAÇÃO  ·  REDES  ·  ANOMALIAS",
    0.45, 1.58, 12.45, 0.28,
    size=10, bold=True, color=BRANCO, font="Calibri")

for i, ref in enumerate(refs_esq):
    t = 1.98 + i * 0.73
    box(s, 0.35, t, 6.10, 0.68, fill_color=CINZA_CLR if i%2==0 else BRANCO,
        border_color=CINZA_BOX, border_pt=0.2)
    txt(s, ref, 0.44, t+0.06, 5.92, 0.58,
        size=10, font="Calibri Light", color=CINZA_ESC)

for i, ref in enumerate(refs_dir):
    t = 1.98 + i * 0.73
    box(s, 6.58, t, 6.40, 0.68, fill_color=CINZA_CLR if i%2==0 else BRANCO,
        border_color=CINZA_BOX, border_pt=0.2)
    txt(s, ref, 6.67, t+0.06, 6.22, 0.58,
        size=10, font="Calibri Light", color=CINZA_ESC)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — AGRADECIMENTOS / ENCERRAMENTO  (mesma identidade da capa)
# ═══════════════════════════════════════════════════════════════════════════════
s = blank(prs)
bg(s, BRANCO)

# Coluna esquerda verde (mesma da capa)
box(s, 0, 0, 3.33, 7.50, fill_color=VERDE_UDESC_ESC)

# Símbolo UDESC na coluna verde
SYM_H2 = 2.60
SYM_W2 = SYM_H2 * (1071 / 2111)
SYM_L2 = (3.33 - SYM_W2) / 2
SYM_T2 = (7.50 - SYM_H2) / 2
s.shapes.add_picture(LOGO_SYMBOL, Inches(SYM_L2), Inches(SYM_T2),
                     Inches(SYM_W2), Inches(SYM_H2))

# Faixa superior
box(s, 3.33, 0, 10.00, 0.90, fill_color=VERDE_UDESC_ESC)
txt(s, "Universidade do Estado de Santa Catarina — UDESC  |  PPGCAP / CCT",
    3.55, 0.08, 9.60, 0.38,
    size=11, bold=True, color=BRANCO, font="Calibri")
txt(s, "36º Seminário de Inovação em Computação  ·  2026",
    3.55, 0.50, 9.60, 0.32,
    size=10, color=BRANCO, font="Calibri Light")

# Logo horizontal
LOG_W2 = 2.00
LOG_H2 = LOG_W2 * (103 / 302)
s.shapes.add_picture(LOGO_HORIZ,
                     Inches(13.33 - LOG_W2 - 0.20), Inches(0.11),
                     Inches(LOG_W2), Inches(LOG_H2))

# "Obrigado" centralizado
box(s, 3.33, 0.90, 10.00, 0.06, fill_color=VERDE_UDESC_CLR)
txt(s, "Obrigado", 3.55, 1.20, 9.60, 1.60,
    size=62, bold=True, color=VERDE_UDESC_ESC,
    align=PP_ALIGN.CENTER, font="Calibri")

# Título da pesquisa
box(s, 3.60, 2.86, 9.40, 0.04, fill_color=VERDE_UDESC_CLR)
txt(s, "ANALÍTICA PRESCRITIVA E IA EXPLICÁVEL PARA A GESTÃO DE FROTAS PÚBLICAS",
    3.60, 2.96, 9.60, 0.56,
    size=13, bold=True, color=CINZA_ESC,
    align=PP_ALIGN.CENTER, font="Calibri")

# Bloco de identificação
box(s, 3.33, 3.70, 10.00, 0.04, fill_color=VERDE_UDESC_ESC)
box(s, 3.33, 3.74, 10.00, 2.10, fill_color=VERDE_FUNDO)
dados_enc = [
    ("Mestrando:",    "Eduardo Lopes Jonker"),
    ("Contato:",      "eduardo.jonker@edu.udesc.br"),
    ("Orientadora:",  "Profa. Dra. Vivian Kremer Kalempa"),
    ("Coorientador:", "Prof. Dr. Yuri Kaszubowski Lopes"),
    ("Programa:",     "PPGCAP / CCT / UDESC  ·  Florianópolis, SC"),
]
for i, (lbl, val) in enumerate(dados_enc):
    t = 3.82 + i * 0.37
    txt(s, lbl, 3.52, t, 2.20, 0.34,
        size=11, bold=True, color=VERDE_UDESC_ESC, font="Calibri")
    txt(s, val, 5.75, t, 7.45, 0.34,
        size=11, color=CINZA_ESC, font="Calibri Light")

# Rodapé encerramento
box(s, 3.33, 5.84, 10.00, 0.04, fill_color=VERDE_UDESC_CLR)
box(s, 3.33, 5.88, 10.00, 1.62, fill_color=VERDE_UDESC_ESC)
txt(s, "\"É possível conectar dados administrativos heterogêneos, modelos preditivos não lineares\n"
       "e otimização prescritiva em um artefato auditável que apoia — sem substituir — a decisão do gestor.\"",
    3.55, 6.05, 8.80, 1.10,
    size=13, italic=True, color=BRANCO,
    align=PP_ALIGN.CENTER, font="Calibri Light")
# número do slide — canto inferior direito
txt(s, f"{len(prs.slides)} / {TOTAL_SLIDES}", 12.20, 7.20, 0.90, 0.26,
    size=11, bold=True, color=VERDE_UDESC_CLR,
    align=PP_ALIGN.RIGHT, font="Calibri")

# ── Salvar ────────────────────────────────────────────────────────────────────
assert len(prs.slides) == TOTAL_SLIDES, (
    f"TOTAL_SLIDES={TOTAL_SLIDES}, mas o deck tem {len(prs.slides)} slides")
OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print(f"✓ Apresentação salva em: {OUT}")
print(f"  Slides: {len(prs.slides)}")
print(f"  Tamanho: {OUT.stat().st_size / 1024:.1f} KB")

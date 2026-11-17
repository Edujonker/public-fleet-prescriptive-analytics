#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apresentação do Exame de Qualificação de Mestrado (PPGCAP/UDESC) em PPTX.

Mestrando: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes

Fidelidade ao projeto:
  - Todo número vem dos resultados calculados (JSON/Parquet do pipeline, LOA/PCA,
    PRISMA) ou de scripts/hipoteses_oficiais.py. Nada é digitado no texto dos slides.
  - As figuras são as oficiais (overleaf_dissertacao_udesc/figuras e
    resultados_loa_pca_2026). Se faltar uma figura, o script para com erro.
  - Antes de salvar, verificações cruzadas conferem os números entre fontes
    (por exemplo, decisão de cada hipótese × certificado da etapa 09).
  - Cada slide leva nas notas do apresentador as fontes de seus números, e o
    arquivo fontes_apresentacao.md lista todas.

Layout baseado na proposta do autor (paleta UDESC, cartões, tabelas).
Uso: .venv/bin/python scripts/gerar_apresentacao_qualificacao.py
Saída: apresentacao_qualificacao/Qualificacao_Mestrado_UDESC_Eduardo_Jonker.pptx
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import hipoteses_oficiais as HO  # noqa: E402

LOGS = ROOT / "dissertacao_frotas/resultados/logs"
PROC = ROOT / "dissertacao_frotas/dados/processados"
FIG = ROOT / "overleaf_dissertacao_udesc/figuras"
LOA = ROOT / "resultados_loa_pca_2026"
OUT_DIR = ROOT / "apresentacao_qualificacao"
OUT = OUT_DIR / "Qualificacao_Mestrado_UDESC_Eduardo_Jonker.pptx"
FONTES_MD = OUT_DIR / "fontes_apresentacao.md"
QUALIF_HTML = ROOT / "relatorios/qualificacao_pesquisa.html"
LOGO = Path("/tmp/udesc_logos/Imagem 20.png")  # opcional; usado só se existir

# Paleta institucional UDESC
VERDE_ESCURO = RGBColor(0, 77, 46)
VERDE_MEDIO = RGBColor(0, 122, 71)
VERDE_CLARO = RGBColor(232, 245, 238)
VERMELHO_UDESC = RGBColor(200, 16, 46)
CINZA_ESCURO = RGBColor(38, 50, 56)
CINZA_TEXTO = RGBColor(55, 71, 79)
CINZA_FUNDO = RGBColor(248, 250, 252)
CINZA_LINHA = RGBColor(203, 213, 225)
CINZA_RODAPE = RGBColor(100, 116, 139)
BRANCO = RGBColor(255, 255, 255)
AMBAR = RGBColor(180, 83, 9)
AMBAR_CLARO = RGBColor(254, 243, 199)
VERMELHO_CLARO = RGBColor(254, 226, 226)
VERDE_TEXTO_CAPA = RGBColor(167, 243, 208)
VERDE_SUB = RGBColor(209, 250, 229)
COR_DECISAO = {"SUSTENTADA": VERDE_MEDIO, "PARCIALMENTE SUSTENTADA": AMBAR, "NÃO SUSTENTADA": VERMELHO_UDESC}
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


# ------------------------------------------------------------------ formatação
def br(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def inteiro(x):
    return br(x, 0)


def pct(x, nd=1):
    """x em fração (0,137 -> 13,7%)."""
    return br(100 * x, nd) + "%"


def mi(x, nd=2):
    return f"R$ {br(x / 1e6, nd)} mi"


def rs(x, nd=2):
    return f"R$ {br(x, nd)}"


def mes_ano(ym: str):
    a, m = ym[:4], int(ym[5:7])
    return f"{MESES[m - 1]}/{a}"


def _j(p: Path):
    if not p.exists():
        sys.exit(f"[ERRO] arquivo de resultados ausente: {p.relative_to(ROOT)}")
    return json.loads(p.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ dados
def carregar():
    D = {
        "aud": _j(LOGS / "relatorio_auditoria_dados_brutos.json"),
        "san": _j(LOGS / "rastreabilidade_saneamento.json"),
        "pred": _j(LOGS / "relatorio_modelagem_preditiva.json"),
        "abl": _j(LOGS / "relatorio_ablacao_h1.json"),
        "svr": _j(LOGS / "relatorio_h2_svr.json"),
        "anom": _j(LOGS / "relatorio_deteccao_anomalias.json"),
        "graf": _j(LOGS / "relatorio_teoria_grafos.json"),
        "neo": _j(LOGS / "relatorio_analise_grafos_neo4j.json"),
        "xai": _j(LOGS / "relatorio_explicabilidade_xai.json"),
        "h4": _j(LOGS / "relatorio_h4_fidelidade_estabilidade.json"),
        "milp": _j(LOGS / "relatorio_otimizacao_milp.json"),
        "cert": _j(LOGS / "certificado_reprodutibilidade_cientifica.json"),
        "loa": _j(LOA / "resultado_experimento.json"),
        "exe": _j(LOA / "execucao_orcamentaria_frota.json"),
        "prisma": _j(ROOT / "revisao_sistematica/resultados_prisma.json"),
    }
    # Tipo de manutenção dos itens (campo corrigido ds_codigo_manutencao) e período da base
    itens = pd.read_parquet(PROC / "os_itens_processados.parquet", columns=["tipo_manutencao_codigo"])
    vc = itens.tipo_manutencao_codigo.value_counts()
    D["itens_corretivos"] = int(vc.get("CORRETIVA", 0))
    D["itens_preventivos"] = int(vc.get("PREVENTIVA", 0))
    os_ = pd.read_parquet(PROC / "os_consolidadas_processadas.parquet",
                          columns=["veiculo_id", "data_referencia", "nr_quilometragem"])
    D["data_min"] = os_.data_referencia.min()
    D["data_max"] = os_.data_referencia.max()
    # Regressões de hodômetro: queda da quilometragem entre OS consecutivas do mesmo veículo
    x = os_.dropna(subset=["data_referencia"]).sort_values(["veiculo_id", "data_referencia"])
    queda = x.groupby("veiculo_id").nr_quilometragem.diff() < 0
    D["hodo_regressoes"] = int(queda.sum())
    D["hodo_veiculos"] = int(x.loc[queda, "veiculo_id"].nunique())
    D["cronograma"] = cronograma_qualificacao()
    D["referencias"] = referencias_qualificacao()
    D["agradecimentos"] = agradecimentos_dissertacao()
    return D


# Obras citadas nos slides, na ordem da lista da qualificação (prefixo da referência ABNT)
REFS_CITADAS = ["BERGMEIR, C.", "BERTSIMAS, D.", "BLONDEL, V. D.", "DELONG, E. R.", "KAPOOR, S.", "LUNDBERG, S. M.",
                "RIBEIRO, M. T.", "RUDIN, C.", "VOLPATO, G. L. O método", "VOLPATO, G. L. Método",
                "BRASIL. Lei Complementar Federal nº 101", "BRASIL. Lei Federal nº 13.709", "BRASIL. Lei Federal nº 14.133",
                "SANTA CATARINA. Decreto nº 311", "SANTA CATARINA. Decreto nº 577", "SANTA CATARINA. Secretaria de Estado da Administração"]


def referencias_qualificacao():
    s = QUALIF_HTML.read_text(encoding="utf-8")
    seg = s[s.rfind("REFERÊNCIAS"):]
    todas = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<(?:p|li)[^>]*>(.*?)</(?:p|li)>", seg, re.S)]
    todas = [re.sub(r"\s+", " ", r) for r in todas if len(r) > 40]
    sel = []
    for pre in REFS_CITADAS:
        achou = [r for r in todas if r.startswith(pre)]
        if len(achou) != 1:
            sys.exit(f"[ERRO] referência '{pre}' encontrada {len(achou)} vez(es) na qualificação")
        sel.append(achou[0])
    return sel


def agradecimentos_dissertacao():
    """Parágrafos do Agradecimentos.tex como listas de (texto, negrito)."""
    tex = (ROOT / "overleaf_dissertacao_udesc/PreTextuais/Agradecimentos.tex").read_text(encoding="utf-8")
    corpo = tex.split("\\begin{agradecimentos}", 1)[1].split("\\end{agradecimentos}", 1)[0]
    pars = []
    for linha in corpo.strip().split("\n"):
        linha = linha.strip()
        if not linha or linha.startswith("%"):
            continue
        partes, pos = [], 0
        for m in re.finditer(r"\\textbf\{([^}]*)\}", linha):
            if m.start() > pos:
                partes.append((linha[pos:m.start()], False))
            partes.append((m.group(1), True))
            pos = m.end()
        if pos < len(linha):
            partes.append((linha[pos:], False))
        pars.append(partes)
    if not pars:
        sys.exit("[ERRO] agradecimentos vazios")
    return pars


def cronograma_qualificacao():
    """Lê a Tabela 7.1 (cronograma) do relatório de qualificação, para não divergir dele."""
    s = QUALIF_HTML.read_text(encoding="utf-8")
    i = s.find("Mês 1</strong>")
    if i < 0:
        sys.exit("[ERRO] cronograma (Mês 1) não encontrado em relatorios/qualificacao_pesquisa.html")
    linhas = []
    for r in re.findall(r"<tr>(.*?)</tr>", s[i - 200:i + 8000], re.S):
        c = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(c) == 4 and c[0].startswith("Mês"):
            linhas.append(c)
    if len(linhas) != 7:
        sys.exit(f"[ERRO] cronograma da qualificação com {len(linhas)} linhas (esperado 7)")
    return linhas


# ------------------------------------------------------------------ verificações cruzadas
def verificar(D):
    erros = []
    def chk(cond, msg):
        if not cond:
            erros.append(msg)
    san = D["san"]["etapas_rastreabilidade"][3]
    chk(D["abl"]["n_treino"] + D["abl"]["n_teste"] == san["n_instancias_finais_supervisionadas"],
        "treino + teste da ablação ≠ painel supervisionado")
    cert = {h["id"]: h["decisao"] for h in D["cert"]["matriz_hipoteses"]}
    for k, h in HO.H.items():
        chk(cert.get(k) == h["decisao"], f"{k}: decisão em hipoteses_oficiais ({h['decisao']}) ≠ certificado ({cert.get(k)})")
    hgb = next(m for m in D["pred"]["metricas_classificacao"] if m["modelo"] == "HistGradientBoosting")
    chk(abs(hgb["roc_auc"] - D["abl"]["classificacao_semente42"]["roc_auc_MP"]) < 5e-4, "ROC-AUC HistGB: etapa 04 ≠ ablação M+P")
    m = D["milp"]
    chk(abs(m["confronto_inercial"]["custo_inercial_as_is_brl"] - m["solucao_inteira_mip_brl"]
            - m["confronto_inercial"]["economia_prescritiva_brl"]) < 0.02, "MILP: economia ≠ BL0 − MILP")
    chk(m["hipotese_h3_sustentada"] == (HO.H["H3"]["decisao"] == "SUSTENTADA"), "H3: JSON do MILP ≠ hipóteses oficiais")
    chk(D["xai"]["hipotese_h4_sustentada"] is False and HO.H["H4"]["decisao"] == "NÃO SUSTENTADA", "H4 inconsistente")
    chk(D["svr"]["h2_sustentada"] is False and HO.H["H2"]["decisao"] == "NÃO SUSTENTADA", "H2 inconsistente")
    chk(D["prisma"]["n_incluidos"] == sum(D["prisma"]["incluidos"].values()), "PRISMA: soma dos incluídos ≠ total")
    g = D["neo"]["testes"]
    chk(all(g[t]["aprovado"] for t in ("T1_integridade", "T2_projecao", "T3_reproducao_etapa06")), "grafo: teste T1–T3 reprovado")
    pr = D["prisma"]
    seg = sum(v for g in pr["triagem"].values() for k, v in g.items() if k.startswith("segue")) + \
        sum(v for k, v in pr["snowball_triagem"].items() if k.startswith("segue"))
    chk(seg == pr["textos_buscados"], "PRISMA: triagem 'segue' ≠ textos buscados")
    est = next(e for e in D["anom"]["estabilidade_sementes"] if abs(e["contaminacao_nominal"] - D["anom"]["modelo_referencia"]["contaminacao_nu"]) < 1e-9)
    chk(est["anomalias_detectadas"] == D["anom"]["modelo_referencia"]["total_anomalias_detectadas"], "anomalias: estabilidade ≠ modelo de referência")
    s26 = sum(D["loa"]["previsao_mensal_2026"].values())
    chk(abs(s26 - D["loa"]["total_2026"]) < 0.01, "LOA: total 2026 ≠ soma mensal")
    if erros:
        sys.exit("[ERRO] verificações cruzadas falharam:\n  - " + "\n  - ".join(erros))
    return 12


# ------------------------------------------------------------------ primitivas de layout
class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.fontes: list[tuple[str, list[str]]] = []
        self.numeros = []  # (índice do slide, caixa de texto do número)

    def base(self, titulo, subtitulo=""):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = CINZA_FUNDO
        retangulo(s, 0, 0, 13.333, 1.05, VERDE_ESCURO)
        retangulo(s, 0, 1.05, 13.333, 0.05, VERMELHO_UDESC)
        texto(s, titulo, 0.5, 0.13, 12.0, 0.5, 24, True, BRANCO)
        if subtitulo:
            texto(s, subtitulo, 0.5, 0.62, 12.0, 0.35, 13, False, VERDE_SUB)
        retangulo(s, 0.5, 7.05, 12.333, 0.015, CINZA_LINHA)
        texto(s, "PPGCAP/UDESC — Exame de Qualificação de Mestrado | Eduardo Lopes Jonker (2026)", 0.5, 7.1, 10.5, 0.3, 10, False, CINZA_RODAPE)
        self.numeros.append((len(self.prs.slides), texto(s, "", 11.5, 7.1, 1.333, 0.3, 10, True, VERDE_ESCURO, PP_ALIGN.RIGHT)))
        self.fontes.append((titulo, []))
        return s

    def fonte(self, s, *itens):
        """Registra as fontes dos números do slide (notas do apresentador + fontes_apresentacao.md)."""
        self.fontes[-1][1].extend(itens)
        tf = s.notes_slide.notes_text_frame
        tf.text = "Fontes dos números deste slide:\n" + "\n".join(f"- {i}" for i in self.fontes[-1][1])

    def numerar(self):
        n = len(self.prs.slides)
        for i, tb in self.numeros:
            p = tb.text_frame.paragraphs[0]
            r = p.runs[0] if p.runs else p.add_run()
            r.text = f"{i} / {n}"


def retangulo(s, l, t, w, h, cor, borda=None, forma=MSO_SHAPE.RECTANGLE):
    r = s.shapes.add_shape(forma, Inches(l), Inches(t), Inches(w), Inches(h))
    r.fill.solid()
    r.fill.fore_color.rgb = cor
    if borda:
        r.line.color.rgb = borda
        r.line.width = Pt(1.5)
    else:
        r.line.fill.background()
    return r


def texto(s, t, l, top, w, h, tam=14, negrito=False, cor=CINZA_TEXTO, alinh=PP_ALIGN.LEFT):
    tb = s.shapes.add_textbox(Inches(l), Inches(top), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    linhas = t.split("\n") if t else [""]
    for k, linha in enumerate(linhas):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.alignment = alinh
        r = p.add_run()
        r.text = linha
        r.font.name = "Calibri"
        r.font.size = Pt(tam)
        r.font.bold = negrito
        r.font.color.rgb = cor
    return tb


# ---- medida de texto para ajustar a fonte à caixa
# O LibreOffice deste computador substitui Calibri por Noto Sans, que é mais larga;
# um texto que cabe em Noto Sans também cabe em Calibri no PowerPoint.
_FONTES = {False: "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
           True: "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"}
_CACHE = {}


def _fonte(tam, negrito=False):
    from PIL import ImageFont
    k = (round(tam * 4), negrito)
    if k not in _CACHE:
        _CACHE[k] = ImageFont.truetype(_FONTES[negrito], int(round(tam * 4)))  # 4 px por ponto
    return _CACHE[k]


def _linhas(txt, tam, larg_pol, negrito=False):
    """Número de linhas que o texto ocupa numa largura (polegadas) com a fonte em pontos."""
    f = _fonte(tam, negrito)
    lim = larg_pol * 72 * 4
    n, atual = 0, ""
    for par in txt.split("\n"):
        n += 1
        atual = ""
        for w in par.split():
            teste = (atual + " " + w).strip()
            if f.getlength(teste) <= lim or not atual:
                atual = teste
            else:
                n += 1
                atual = w
    return n


def altura_texto(blocos, larg_pol):
    """blocos: lista de (texto, tamanho, negrito, espaço_depois_pt). Retorna altura em polegadas."""
    tot = 0.0
    for txt, tam, neg, esp in blocos:
        tot += _linhas(txt, tam, larg_pol, neg) * tam * 1.2 + esp
    return tot / 72


def maior_fonte(gerar_blocos, larg_pol, alt_pol, maximo=22, minimo=10):
    """Maior tamanho (passo de 0,5 pt) cujo texto cabe na caixa."""
    t = maximo
    while t > minimo and altura_texto(gerar_blocos(t), larg_pol) > alt_pol:
        t -= 0.5
    return t


def cartao(s, l, t, w, h, titulo, itens, borda=VERDE_MEDIO, fundo=BRANCO, cor_titulo=VERDE_ESCURO, tam=None):
    """Cartão com título e itens. A fonte dos itens é a maior que cabe na caixa (ou `tam`, se dado)."""
    marg_x, marg_y = 0.18, 0.12
    larg, alt = w - 2 * marg_x - 0.2, h - 2 * marg_y - 0.15   # folga para margens internas da caixa de texto
    itens_txt = [it if it.startswith("→") else f"• {it}" for it in itens]
    def blocos(tm):
        tt = min(tm + 3, 22)
        return [(titulo, tt, True, 6)] + [(x, tm, False, tm * 0.35) for x in itens_txt]
    if tam is None:
        tam = maior_fonte(blocos, larg, alt)
    tam_tit = min(tam + 3, 22)
    c = retangulo(s, l, t, w, h, fundo, borda, MSO_SHAPE.ROUNDED_RECTANGLE)
    c.adjustments[0] = 0.03
    tb = s.shapes.add_textbox(Inches(l + 0.18), Inches(t + 0.12), Inches(w - 0.36), Inches(h - 0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = titulo
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = "Calibri", Pt(tam_tit), True, cor_titulo
    p.space_after = Pt(6)
    for it in itens_txt:
        p = tf.add_paragraph()
        r = p.add_run()
        r.text = it
        r.font.name, r.font.size, r.font.color.rgb = "Calibri", Pt(tam), CINZA_TEXTO
        p.space_after = Pt(tam * 0.35)


def figura(s, caminho: Path, l, t, w, h, legenda=""):
    """Insere a figura inteira dentro da caixa (l, t, w, h), mantendo a proporção."""
    if not caminho.exists():
        sys.exit(f"[ERRO] figura ausente: {caminho.relative_to(ROOT)}")
    hl = 0.3 if legenda else 0
    with Image.open(caminho) as im:
        iw, ih = im.size
    esc = min(w / iw, (h - hl) / ih)
    fw, fh = iw * esc, ih * esc
    s.shapes.add_picture(str(caminho), Inches(l + (w - fw) / 2), Inches(t + (h - hl - fh) / 2), Inches(fw), Inches(fh))
    if legenda:
        texto(s, legenda, l, t + h - hl, w, hl, 10, False, CINZA_RODAPE, PP_ALIGN.CENTER)


def tabela(s, l, t, w, h, larguras, cab, linhas, tam=11.5):
    tb = s.shapes.add_table(len(linhas) + 1, len(cab), Inches(l), Inches(t), Inches(w), Inches(h)).table
    for i, lw in enumerate(larguras):
        tb.columns[i].width = Inches(lw)
    def cel(r, c, val, fundo, cor, negrito=False, tam_=tam):
        x = tb.cell(r, c)
        x.fill.solid()
        x.fill.fore_color.rgb = fundo
        x.vertical_anchor = MSO_ANCHOR.MIDDLE
        x.margin_left = x.margin_right = Inches(0.06)
        p = x.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = val
        run.font.name, run.font.size, run.font.bold, run.font.color.rgb = "Calibri", Pt(tam_), negrito, cor
    for c, v in enumerate(cab):
        cel(0, c, v, VERDE_ESCURO, BRANCO, True, tam + 0.5)
    for r, linha in enumerate(linhas, 1):
        fundo = BRANCO if r % 2 else RGBColor(241, 245, 249)
        for c, v in enumerate(linha):
            cor = COR_DECISAO.get(v, CINZA_ESCURO)
            cel(r, c, v, fundo, cor, v in COR_DECISAO)
    return tb


# ------------------------------------------------------------------ slides
def montar(D):
    d = Deck()
    aud, gr, fin = D["aud"], D["aud"]["granularidade"], D["aud"]["auditoria_financeira"]
    san = D["san"]["etapas_rastreabilidade"]
    painel = san[3]
    abl, svr, pred = D["abl"], D["svr"], D["pred"]
    hgb_cls = next(m for m in pred["metricas_classificacao"] if m["modelo"] == "HistGradientBoosting")
    reg = {m["modelo"]: m for m in pred["metricas_regressao"]}
    rs_svr = svr["resumo_media_dp"]
    cp = svr["comparacao_pareada_semente42"]["HistGradientBoosting"]
    milp, ci = D["milp"], D["milp"]["confronto_inercial"]
    xai, h4 = D["xai"], D["h4"]
    an, mr, cf = D["anom"], D["anom"]["modelo_referencia"], D["anom"]["concordancia_fiscal"]
    est = next(e for e in an["estabilidade_sementes"] if abs(e["contaminacao_nominal"] - mr["contaminacao_nu"]) < 1e-9)
    topo, neo = D["graf"]["topologia_rede"], D["neo"]
    a1, a2, a3, a4 = (neo["analises"][k] for k in ("A1_estabilidade_louvain", "A2_modelo_nulo", "A3_concentracao", "A4_centralidade_vs_auditoria"))
    t1 = neo["testes"]["T1_integridade"]["observado"]
    loa, exe = D["loa"], D["exe"]
    cx = exe["comparacao_experimento"]
    pr = D["prisma"]
    n_corr, n_prev = D["itens_corretivos"], D["itens_preventivos"]
    sh_corr = n_corr / (n_corr + n_prev)
    periodo = f"{MESES[D['data_min'].month - 1]}/{D['data_min'].year} a {MESES[D['data_max'].month - 1]}/{D['data_max'].year}"
    corte = mes_ano(loa["corte"])
    J = "dissertacao_frotas/resultados/logs/"

    # 1. Capa ------------------------------------------------------------
    s = d.prs.slides.add_slide(d.prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = VERDE_ESCURO
    retangulo(s, 0, 0, 0.35, 7.5, VERMELHO_UDESC)
    texto(s, "UNIVERSIDADE DO ESTADO DE SANTA CATARINA — UDESC\nCENTRO DE CIÊNCIAS TECNOLÓGICAS — CCT\n"
             "PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA — PPGCAP", 0.9, 0.6, 9.5, 1.1, 14, True, VERDE_TEXTO_CAPA)
    if LOGO.exists():
        with Image.open(LOGO) as im:
            r = im.size[1] / im.size[0]
        s.shapes.add_picture(str(LOGO), Inches(10.6), Inches(0.6), Inches(2.2), Inches(2.2 * r))
    texto(s, "ANALÍTICA PRESCRITIVA, TEORIA DOS GRAFOS E INTELIGÊNCIA ARTIFICIAL EXPLICÁVEL "
             "PARA A GESTÃO DE FROTA VEICULAR NO SETOR PÚBLICO", 0.9, 2.0, 11.5, 1.6, 28, True, BRANCO)
    texto(s, "Exame de Qualificação de Dissertação de Mestrado\nLinha de Pesquisa: Metodologia e Técnicas de Computação (MTC)",
          0.9, 3.75, 11.5, 0.9, 16, False, VERDE_SUB)
    texto(s, "Mestrando: Eduardo Lopes Jonker\nOrientadora: Profa. Dra. Vivian Kremer Kalempa (UDESC/PPGCAP)\n"
             "Coorientador: Prof. Dr. Yuri Kaszubowski Lopes (UDESC/PPGCAP)\nJoinville — SC | 2026", 0.9, 4.9, 11.5, 1.8, 15, False, BRANCO)
    d.fontes.append(("Capa", ["Título, banca e linha de pesquisa: relatorios/qualificacao_pesquisa.html (capa)"]))

    # 2. Contexto e problema --------------------------------------------
    s = d.base("1. Contextualização e Problema de Pesquisa", "Fragmentação informacional e gestão reativa nas frotas do setor público")
    cartao(s, 0.5, 1.35, 3.9, 2.55, "Silo 1: Cadastro Patrimonial",
           ["Atributos estáticos do bem (ano, marca, modelo, tombamento).",
            "Valor contábil desvinculado do desgaste mecânico real."])
    cartao(s, 4.7, 1.35, 3.9, 2.55, "Silo 2: Ordens de Serviço (OS)",
           [f"Peças e mão de obra em {inteiro(gr['total_oficinas_unicas'])} oficinas e {inteiro(gr['total_orgaos_clientes_unicos'])} órgãos.",
            f"{inteiro(D['hodo_regressoes'])} quedas de hodômetro entre OS consecutivas, em {inteiro(D['hodo_veiculos'])} veículos."])
    cartao(s, 8.9, 1.35, 3.9, 2.55, "Silo 3: Abastecimento",
           ["Volume, combustível e hodômetro por transação.",
            f"Base disponível: {abl['abastecimento'].split('cobre ')[1].split(' e não')[0]}; não cobre o período de teste."])
    cartao(s, 0.5, 4.2, 12.33, 2.6, "Consequências e marco legal",
           [f"Gestão reativa: {pct(sh_corr)} dos itens com tipo corretiva ou preventiva são corretivos "
            f"({inteiro(n_corr)} contra {inteiro(n_prev)} preventivos).",
            "Indisponibilidade de viaturas em serviços essenciais (segurança, saúde) e custos de guincho.",
            "Marco legal: LRF (LC nº 101/2000), Lei nº 14.133/2021, Decretos SC nº 311/2011 e nº 577/2016 (Sistema GVE) "
            "e Cartilha GFI SEA/SC (2026, 38 indicadores)."],
           borda=VERMELHO_UDESC, cor_titulo=VERMELHO_UDESC)
    d.fonte(s, f"Oficinas e órgãos: {J}relatorio_auditoria_dados_brutos.json (granularidade)",
            "Hodômetro: queda de nr_quilometragem entre OS consecutivas do veículo, ordenadas por data_referencia (os_consolidadas_processadas.parquet)",
            "Abastecimento: relatorio_ablacao_h1.json (campo abastecimento)",
            "Corretivas/preventivas: tipo_manutencao_codigo em os_itens_processados.parquet",
            "Marco legal e Cartilha GFI: relatorios/qualificacao_pesquisa.html")

    # 3. Base empírica ---------------------------------------------------
    s = d.base("2. Base Empírica Censitária e Conciliação Contábil",
               f"Poder Executivo de Santa Catarina — OS de {periodo} (cobertura completa até {corte})")
    cartao(s, 0.5, 1.35, 5.8, 5.4, "Dimensão auditada (SEA/SC)",
           [f"{inteiro(gr['total_ordens_servico_unicas'])} ordens de serviço.",
            f"{inteiro(gr['total_registros_itens_logicos'])} itens de peças e serviços.",
            f"{inteiro(gr['total_veiculos_unicos'])} veículos e {inteiro(gr['total_oficinas_unicas'])} oficinas.",
            f"Painel veículo-mês: {inteiro(painel['n_instancias_finais_supervisionadas'])} instâncias supervisionadas "
            f"({inteiro(painel['n_veiculos_unicos'])} veículos), 15 atributos preditivos.",
            f"SHA-256 dos {len(aud['certificados_criptograficos'])} arquivos brutos; anonimização (Presidio + HMAC-SHA-256)."])
    cartao(s, 6.6, 1.35, 6.2, 5.4, "Identidade contábil (ao centavo)",
           [f"Orçado bruto: {rs(fin['total_orcado_bruto_itens'])} (100%)",
            f"Glosas e retenções: {rs(fin['total_glosas_fiscalizacao'])} ({br(fin['taxa_glosa_percentual'], 2)}%)",
            f"Aprovado: {rs(fin['total_aprovado_bruto_itens'])} ({br(100 - fin['taxa_glosa_percentual'], 2)}%)",
            f"→ {mi(fin['total_orcado_bruto_itens'])} = {mi(fin['total_glosas_fiscalizacao'])} (glosas) + {mi(fin['total_aprovado_bruto_itens'])} (aprovado).",
            f"→ Peças {mi(fin['total_aprovado_pecas'])}; mão de obra {mi(fin['total_aprovado_mao_de_obra'])}."],
           fundo=VERDE_CLARO)
    d.fonte(s, f"{J}relatorio_auditoria_dados_brutos.json (granularidade, auditoria_financeira, certificados)",
            f"{J}rastreabilidade_saneamento.json (etapa 04_painel_longitudinal_ml)",
            "Período: min/max de data_referencia; corte de cobertura: resultados_loa_pca_2026/resultado_experimento.json")

    # 4. Lacunas e pergunta ----------------------------------------------
    s = d.base("3. Lacunas Científicas e Pergunta de Pesquisa",
               f"Posicionamento perante o estado da arte (revisão PRISMA 2020: {inteiro(pr['n_incluidos'])} estudos na triagem assistida)")
    p1 = HO.H["P1"]["evidencia"]
    cartao(s, 0.5, 1.35, 3.9, 3.1, "Lacuna 1: Dados reais",
           ["Literatura dominada por dados simulados ou frotas privadas homogêneas.",
            f"Custos da frota pública têm cauda pesada ({p1.split('; ', 1)[1]})."])
    cartao(s, 4.7, 1.35, 3.9, 3.1, "Lacuna 2: Auditabilidade da XAI",
           ["Poucos estudos ligam XAI a requisitos de controle externo (TCE-SC).",
            "Alerta de Rudin (2019) sobre explicações locais pós-hoc."])
    cartao(s, 8.9, 1.35, 3.9, 3.1, "Lacuna 3: Ciclo ponta a ponta",
           ["Estudos param na acurácia preditiva (ROC/PR).",
            "Falta integração com otimização MILP sob tetos orçamentários da LOA."])
    cartao(s, 0.5, 4.75, 12.33, 2.0, "Pergunta de pesquisa",
           ["Como conceber, validar e avaliar uma arquitetura analítico-prescritiva orientada por dados censitários que integre "
            "aprendizado de máquina calibrado, XAI, teoria dos grafos e otimização inteira mista (MILP), para antecipar falhas, "
            "reduzir custos sob restrições fiscais e dar suporte auditável à gestão de frotas no setor público?"],
           borda=VERDE_ESCURO, fundo=VERDE_CLARO)
    d.fonte(s, "Lacunas e pergunta: relatorios/qualificacao_pesquisa.html",
            "Assimetria e curtose: scripts/hipoteses_oficiais.py (P1, de certificado_reprodutibilidade_cientifica.json)",
            "Estudos incluídos: revisao_sistematica/resultados_prisma.json (n_incluidos)")

    # 5. Delineamento ----------------------------------------------------
    s = d.base("4. Delineamento Epistemológico (Volpato)", "Falseabilidade, prevenção de p-hacking e de vazamento temporal")
    cartao(s, 0.5, 1.4, 3.9, 5.25, "1. Conteúdo precede a forma",
           ["Argumento dedutivo fechado.",
            "Variáveis, métricas e critérios fixados antes da execução.",
            "Desvios registrados em docs/hipoteses/desvios_do_protocolo.md."])
    cartao(s, 4.7, 1.4, 3.9, 5.25, "2. Combate ao p-hacking",
           ["Sem validação cruzada aleatória (k-fold) em dados temporais.",
            f"Holdout temporal: {abl['corte_temporal']}.",
            "Validação walk-forward em 5 dobras com embargo de 30 dias (Kapoor & Narayanan, 2023)."])
    cartao(s, 8.9, 1.4, 3.9, 5.25, "3. Significância × relevância",
           [f"Com {inteiro(gr['total_registros_itens_logicos'])} itens, efeitos triviais atingem p < 0,001.",
            "Limiar de relevância fixado a priori: ganho de 15,0% no MAE para H1.",
            "Cada hipótese tem critério duplo: anteprojeto e limiar da qualificação."])
    d.fonte(s, "Delineamento: relatorios/qualificacao_pesquisa.html (seções 4 e 5)",
            f"Corte temporal: {J}relatorio_ablacao_h1.json (corte_temporal)",
            "Critérios: docs/hipoteses/ e scripts/hipoteses_oficiais.py")

    # 6. Hipóteses -------------------------------------------------------
    s = d.base("5. Hipóteses e Critérios Pré-Registrados",
               "SUSTENTADA = atende aos dois critérios; PARCIALMENTE = a um; NÃO = a nenhum; com um só critério, vale ele")
    linhas = []
    for k in ("P1", "H1", "H2", "H3", "H4"):
        h = HO.H[k]
        # "—" no certificado = critério inexistente naquele documento; vale o outro (regra_de_decisao da etapa 09)
        ca = ("não previsto no anteprojeto (premissa da qualificação)" if h["crit_ante"] == "—"
              else f"{h['crit_ante']} ({h['ok_ante']})")
        cl = ("sem limiar numérico na qualificação; vale o anteprojeto" if h["crit_lim"] == "—"
              else f"{h['crit_lim']} ({h['ok_lim']})")
        linhas.append([h["nome"].split(": ", 1)[0], h["nome"].split(": ", 1)[1], ca, cl, h["decisao"]])
    tabela(s, 0.4, 1.35, 12.53, 5.4, [1.35, 3.1, 3.55, 2.53, 2.0],
           ["Hipótese", "Enunciado", "Critério do anteprojeto (atende?)", "Limiar da qualificação (atende?)", "Decisão"], linhas, 11)
    d.fonte(s, "scripts/hipoteses_oficiais.py (H), conferido com certificado_reprodutibilidade_cientifica.json (matriz_hipoteses)",
            "Regra de decisão: certificado_reprodutibilidade_cientifica.json (regra_de_decisao)")

    # 7. Arquitetura e saneamento ----------------------------------------
    s = d.base("6. Arquitetura Ponta a Ponta e Saneamento de Dados", "Pipeline em etapas auditáveis e reprodutíveis (01–09)")
    figura(s, FIG / "fig64_pipeline_arquitetura_integrada.png", 0.5, 1.3, 7.6, 5.6, "Arquitetura integrada do pipeline (figura oficial)")
    cartao(s, 8.3, 1.35, 4.5, 5.45, "Engenharia de dados",
           [f"Hodômetro: {inteiro(D['hodo_regressoes'])} quedas em {inteiro(D['hodo_veiculos'])} veículos, tratadas por validação monotônica.",
            f"Tipo de manutenção pelo código: {pct(sh_corr)} corretivas e {pct(1 - sh_corr)} preventivas (itens).",
            f"Painel: {inteiro(painel['n_instancias_totais'])} instâncias; {inteiro(painel['descarte_ultimos_meses_sem_alvo'])} "
            f"últimos meses sem alvo t+1 descartados → {inteiro(painel['n_instancias_finais_supervisionadas'])}.",
            f"Treino {inteiro(abl['n_treino'])} (até dez/2024) e teste {inteiro(abl['n_teste'])} (a partir de jan/2025)."])
    d.fonte(s, "Figura: overleaf_dissertacao_udesc/figuras/fig64_pipeline_arquitetura_integrada.png (scripts/gerar_figuras_oficiais.py)",
            f"{J}rastreabilidade_saneamento.json; {J}relatorio_ablacao_h1.json (n_treino, n_teste)",
            "Hodômetro e tipo de manutenção: parquets processados (calculados por este script)")

    # 8. Anomalias -------------------------------------------------------
    s = d.base("7. Detecção Não Supervisionada de Anomalias (Isolation Forest)",
               "Estabilidade entre sementes e aderência às glosas da SEA/SC")
    figura(s, ROOT / "dissertacao_frotas/resultados/figuras/estabilidade_jaccard_contaminacao.png", 0.5, 1.3, 7.3, 5.6,
           "Jaccard médio entre sementes por taxa de contaminação (etapa 05)")
    cartao(s, 8.0, 1.35, 4.8, 5.45, "Resultados e validade externa",
           [f"Contaminação ν = {br(100 * mr['contaminacao_nu'], 2)}%: {inteiro(mr['total_anomalias_detectadas'])} OS atípicas "
            f"({mi(mr['vl_total_orcado'])} orçados).",
            f"Estabilidade: Jaccard médio entre sementes de {br(est['jaccard_medio_sementes'], 4)}.",
            f"As OS com glosa têm escores menos atípicos (Welch t = {br(cf['t_statistic'], 2)}; Mann-Whitney unilateral p = {br(cf['mann_whitney_p'], 2)}).",
            f"As anomalias concentram só {br(mr['taxa_retencao_glosas_pct'], 1)}% de glosa sobre o orçado.",
            "→ Serve para triagem de casos incomuns, não para substituir a auditoria (hipótese exploratória E2)."],
           borda=AMBAR, cor_titulo=AMBAR)
    d.fonte(s, f"{J}relatorio_deteccao_anomalias.json (modelo_referencia, estabilidade_sementes, concordancia_fiscal)",
            "Figura: dissertacao_frotas/resultados/figuras/estabilidade_jaccard_contaminacao.png (gerada pela etapa 05)")

    # 9. H2 --------------------------------------------------------------
    s = d.base("8. Modelagem Preditiva de Risco e Custo (Hipótese H2)",
               f"HistGradientBoosting lidera na classificação; SVR-RBF erra menos na regressão — H2 {HO.H['H2']['decisao']}")
    figura(s, FIG / "fig10_comparativo_mae_rmse_modelos.png", 0.5, 1.3, 7.3, 5.6, "Erro dos regressores de custo (figura oficial)")
    mae_svr, mae_hgb = rs_svr["regressao|SVR-RBF"]["media"], rs_svr["regressao|HistGradientBoosting"]["media"]
    cartao(s, 8.0, 1.35, 4.8, 5.45, f"H2: {HO.H['H2']['decisao']}",
           [f"Classificação (falha corretiva em t+1): HistGB ROC-AUC {br(hgb_cls['roc_auc'], 4)}, PR-AUC {br(hgb_cls['pr_auc'], 4)}, "
            f"ECE {br(hgb_cls['ece'], 4)}; supera o SVC-RBF ({HO.V['h2_dif_auc_svc']} de AUC).",
            f"Regressão (etapa 04c, {len(svr['sementes'])} sementes): SVR-RBF MAE {rs(mae_svr)} × HistGB {rs(mae_hgb)} "
            f"({HO.V['h2_dif_mae_svr']}; IC 95% {HO.V['h2_ic_mae_svr']}), acima da margem de 5%.",
            f"Nenhum regressor bate a mediana histórica: MAE {rs(reg['Baseline Mediana']['mae_reais'])} × HistGB "
            f"{rs(reg['HistGradientBoosting']['mae_reais'])} (R² {br(reg['HistGradientBoosting']['r2_score'], 3)}).",
            "→ Custo mensal por veículo tem pouco sinal preditivo; o risco de falha, sim."],
           borda=VERMELHO_UDESC, cor_titulo=VERMELHO_UDESC)
    d.fonte(s, f"{J}relatorio_modelagem_preditiva.json (metricas_classificacao, metricas_regressao)",
            f"{J}relatorio_h2_svr.json (resumo_media_dp, comparacao_pareada_semente42)",
            "Figura: overleaf_dissertacao_udesc/figuras/fig10_comparativo_mae_rmse_modelos.png")

    # 10. H1 -------------------------------------------------------------
    s = d.base("9. Estudo de Ablação Multimodal (Hipótese H1)",
               "Somente manutenção (M) contra manutenção integrada ao patrimônio (M+P)")
    c42 = abl["classificacao_semente42"]
    figura(s, FIG / "fig12_ablativo_fontes_m_vs_mp.png", 0.5, 1.3, 7.3, 5.6, "Ablação M × M+P (figura oficial)")
    eg = abl["estresse_sementes"]
    cartao(s, 8.0, 1.35, 4.8, 5.45, f"H1: {HO.H['H1']['decisao']}",
           [f"Classificação: ROC-AUC {br(c42['roc_auc_M'], 4)} → {br(c42['roc_auc_MP'], 4)} ({HO.V['h1_dif_roc']}; IC 95% {HO.V['h1_ic_roc']}).",
            f"Regressão: MAE {HO.V['h1_mae_m']} → {HO.V['h1_mae_mp']} ({HO.V['h1_delta_mae']}/mês; {HO.V['h1_ganho_mae']}; "
            f"IC 95% {HO.V['h1_ic_mae']}, inclui zero).",
            f"Em {len(eg['por_semente'])} sementes o ganho no MAE variou de {pct(eg['ganho_min'], 2)} a {pct(eg['ganho_max'], 2)}, "
            "longe da régua de 15%.",
            "→ A integração com o patrimônio não se justifica para estimar custo."],
           borda=AMBAR, cor_titulo=AMBAR)
    d.fonte(s, f"{J}relatorio_ablacao_h1.json; scripts/hipoteses_oficiais.py (V h1_*)",
            "Figura: overleaf_dissertacao_udesc/figuras/fig12_ablativo_fontes_m_vs_mp.png")

    # 11. H3 -------------------------------------------------------------
    s = d.base("10. Otimização Prescritiva via MILP (Hipótese H3)",
               "Alocação de manutenções preventivas sob restrições de orçamento e de oficina — cenário S0")
    dm = milp["dimensoes"]
    figura(s, FIG / "fig14_otimizacao_sensibilidade_orcamento.png", 0.5, 1.3, 7.3, 5.6, "Custo esperado por política no cenário S0 (figura oficial)")
    cartao(s, 8.0, 1.35, 4.8, 5.45, f"H3: {HO.H['H3']['decisao']}",
           [f"Instância semissintética: {inteiro(dm['veiculos'])} veículos reais sorteados × {dm['periodos_meses']} meses "
            f"({inteiro(dm['total_variaveis_decisao'])} variáveis binárias); custos gerados por fórmula.",
            f"HiGHS: {br(milp['tempo_mip_s'], 2)} s; distância à relaxação LP de {HO.V['h3_gap_rel']} ({HO.V['h3_gap_abs']}).",
            f"Custo: prática reconstruída {mi(ci['custo_inercial_as_is_brl'])} → MILP {mi(milp['solucao_inteira_mip_brl'])} "
            f"({HO.V['h3_economia_pct']}; {HO.V['h3_economia_mi']}); {br(milp['cumprimento_mandatorio_pct'], 0)}% das obrigatórias.",
            f"Heurística gulosa: {mi(ci['custo_heuristica_gulosa_brl'])}, só {HO.V['h3_vs_heur_brl']} acima do MILP.",
            f"Orçamento ativo em {br(milp['gargalos_ativos']['restricao_orcamentaria_pct_periodos'], 1)}% dos meses."])
    d.fonte(s, f"{J}relatorio_otimizacao_milp.json; scripts/hipoteses_oficiais.py (V h3_*)",
            "Figura: overleaf_dissertacao_udesc/figuras/fig14_otimizacao_sensibilidade_orcamento.png")

    # 12. H4 -------------------------------------------------------------
    s = d.base("11. Auditoria de Explicabilidade (Hipótese H4)",
               "SHAP (TreeExplainer) e LIME nas 25 instâncias de maior risco")
    top = xai["top_features_shap"][:4]
    figura(s, FIG / "fig13_importancia_atributos_xai.png", 0.5, 1.3, 7.3, 5.6,
           "Importância global SHAP: " + "; ".join(f"{t['feature_label']} {br(t['importancia_relativa_pct'], 1)}%" for t in top[:2]))
    med, cr = h4["medidas"], h4["criterios_pre_definidos"]
    cartao(s, 8.0, 1.35, 4.8, 5.45, f"H4: {HO.H['H4']['decisao']}",
           [f"Concordância SHAP × LIME: Jaccard Top-5 {HO.V['h4_jaccard']} e Spearman {HO.V['h4_spearman']} (meta > 0,85).",
            f"SHAP: erro aditivo máximo {med['F1_shap_erro_aditivo_max']:.1e}; estabilidade {HO.V['h4_shap_estab']} entre re-treinos.",
            f"LIME: estável ({HO.V['h4_lime_estab']}), mas pouco fiel ao modelo (R² local {HO.V['h4_lime_r2']}; mínimo {br(cr['F2_lime_r2_medio_min'], 2)}).",
            "→ Para decisões auditáveis, usar SHAP; o LIME não deve fundamentar a decisão."],
           borda=VERMELHO_UDESC, cor_titulo=VERMELHO_UDESC)
    d.fonte(s, f"{J}relatorio_explicabilidade_xai.json; {J}relatorio_h4_fidelidade_estabilidade.json; scripts/hipoteses_oficiais.py (V h4_*)",
            "Figura: overleaf_dissertacao_udesc/figuras/fig13_importancia_atributos_xai.png")

    # 13. Grafos ---------------------------------------------------------
    s = d.base("12. Modelagem Estrutural via Teoria dos Grafos",
               "Rede bipartida veículo–oficina persistida em Neo4j e comparada com redes nulas")
    figura(s, FIG / "grafos_modelo_nulo_e_concentracao.png", 0.5, 1.3, 7.3, 5.6, "Modularidade contra redes nulas e concentração do gasto")
    sp = a4["spearman"]["grau_ponderado~taxa_glosa"]
    cartao(s, 8.0, 1.35, 4.8, 5.45, "Testes T1–T3 aprovados",
           [f"Rede: {inteiro(t1['vehicle_count'])} veículos, {inteiro(t1['workshop_count'])} oficinas, {inteiro(t1['service_edge_count'])} relações; "
            f"projeção com {inteiro(topo['nos_oficinas'])} oficinas e {inteiro(topo['arestas'])} arestas.",
            f"Louvain: Q = {br(topo['modularidade_louvain_q'], 4)} ({topo['total_comunidades']} comunidades); redes nulas "
            f"{br(a2['Q_nulo_media'], 4)} ± {br(a2['Q_nulo_dp'], 4)} (z = {br(a2['z'], 1)}); ARI entre sementes {br(a1['ARI_vs_seed42_media'], 3)}.",
            f"10% das oficinas recebem {pct(a3['participacao_top10pct_oficinas'])} do gasto (Gini {br(a3['gini_gasto'], 2)}).",
            f"Centralidade não se associa à glosa (Spearman {br(sp['rho'], 3)}; p {br(sp['p'], 2)}).",
            "→ Uso: descrever o mercado e estratificar amostras de auditoria."])
    d.fonte(s, f"{J}relatorio_teoria_grafos.json (topologia_rede); {J}relatorio_analise_grafos_neo4j.json (testes, A1–A4)",
            "Figura: overleaf_dissertacao_udesc/figuras/grafos_modelo_nulo_e_concentracao.png")

    # 14. LOA/PCA 2026 ---------------------------------------------------
    s = d.base("13. Aplicação: LOA e PCA 2026 da Manutenção da Frota",
               f"Previsão com dados até {corte} confrontada com a LOA e os empenhos da SEF/SC")
    figura(s, LOA / "fig_execucao_loa_2026.png", 0.4, 1.3, 7.6, 5.6, "Empenho acumulado × proposta; subações da LOA 2026")
    esc = loa["modelo_escolhido"]
    inc = loa["incerteza_2026"][esc]
    mf = exe["mes_fim_2026"]
    pc = next(p for p in cx["subacoes_mesma_natureza"] if p["orgao_experimento"] == "PC SC")
    ini = exe["primeiro_mes_com_empenho_por_credor"]
    novo = max(ini, key=ini.get)
    cartao(s, 8.15, 1.35, 4.65, 5.45, "Proposta × execução",
           [f"Proposta 2026 ({esc}): {mi(loa['total_2026'])} (80%: {mi(inc['10'])} a {mi(inc['90'])}); erro retrospectivo médio "
            f"{pct(loa['erro_medio_abs_total'][esc])}.",
            f"Empenho de manutenção jan–{MESES[mf - 1]}/2026: {mi(cx['empenho_manutencao_2026_ate_mes_fim'])}, "
            f"{pct(cx['empenho_2026_sobre_proposta'], 0)} da proposta anual.",
            f"O contrato de manutenção mudou em {mes_ano(ini[novo])}, o mês do corte da base de OS: a série projetada deixou de existir.",
            f"LOA PC SC: {mi(pc['loa_2026'])} na subação da frota, mas só {mi(pc['empenho_manutencao']['2025'])} de manutenção em 2025 "
            "(o resto é combustível e locação).",
            "→ E3 continua pré-registrada para a extração de 2026 da SEA/SC."])
    d.fonte(s, "resultados_loa_pca_2026/resultado_experimento.json; resultados_loa_pca_2026/execucao_orcamentaria_frota.json",
            "Figura: resultados_loa_pca_2026/fig_execucao_loa_2026.png (scripts/execucao_orcamentaria_frota.py)")

    # 15. Revisão sistemática e reprodutibilidade -----------------------
    s = d.base("14. Revisão Sistemática e Reprodutibilidade", "PRISMA 2020 e trilha de auditoria do pipeline")
    ident = sum(pr["identificados"].values())
    unic = sum(pr["unicos"].values())
    snow = sum(pr["snowball_identificados"].values())
    tabela(s, 0.5, 1.4, 6.1, 4.0, [3.9, 2.2], ["Etapa PRISMA", "Registros"], [
        ["Identificados nas bases e coleções", inteiro(ident)],
        ["Únicos após deduplicação", inteiro(unic)],
        ["Identificados por snowballing", inteiro(snow)],
        ["Seguem para texto completo", inteiro(pr["textos_buscados"])],
        ["Incluídos (triagem assistida)", inteiro(pr["n_incluidos"])],
    ], 12)
    texto(s, f"Incluídos por origem: bases {pr['incluidos']['bases']}, outras coleções {pr['incluidos']['outros']}, "
             f"snowballing {pr['incluidos']['snowballing']}. A validação humana das inclusões está pendente.",
          0.5, 5.55, 6.1, 1.2, 12, False, CINZA_TEXTO)
    cartao(s, 6.9, 1.35, 5.9, 5.45, "Reprodutibilidade e pendências",
           [f"Certificado da etapa 09 com as {len(D['cert']['matriz_hipoteses'])} decisões; tabela oficial e figuras geradas dos JSON.",
            "Pré-registro de E1–E3 com hash SHA-256, antes da extração de 2026 da SEA/SC.",
            "Desvios do protocolo documentados (docs/hipoteses/desvios_do_protocolo.md).",
            "Processos mapeados em BPMN 2.0 (docs/bpm/).",
            "Pendente: refazer a homologação Linux × Windows depois das correções de integridade.",
            "Pendente: validação humana dos estudos incluídos na revisão."],
           borda=AMBAR, cor_titulo=AMBAR)
    d.fonte(s, "revisao_sistematica/resultados_prisma.json", f"{J}certificado_reprodutibilidade_cientifica.json",
            "docs/hipoteses/preregistro_hipoteses_exploratorias_2026.md(.sha256)")

    # 16. Cronograma -----------------------------------------------------
    s = d.base("15. Cronograma até a Defesa", "Tabela 7.1 do relatório de qualificação")
    tabela(s, 0.5, 1.35, 12.33, 5.5, [1.0, 2.9, 5.43, 3.0], ["Período", "Atividade", "Descrição", "Entrega"],
           D["cronograma"], 10)
    d.fonte(s, "relatorios/qualificacao_pesquisa.html (Tabela 7.1, lida por este script)")

    # 17. Síntese --------------------------------------------------------
    s = d.base("16. Síntese e Próximos Passos", "O que os resultados sustentam e o que falta")
    dec = {k: HO.H[k]["decisao"] for k in HO.H}
    sust = [k for k, v in dec.items() if v == "SUSTENTADA"]
    parc = [k for k, v in dec.items() if v == "PARCIALMENTE SUSTENTADA"]
    nao = [k for k, v in dec.items() if v == "NÃO SUSTENTADA"]
    cartao(s, 0.5, 1.35, 6.0, 5.45, "Resultados",
           [f"Sustentadas: {', '.join(sust)}. Parcialmente: {', '.join(parc)}. Não sustentadas: {', '.join(nao)}.",
            f"Risco de falha previsível (ROC-AUC {br(hgb_cls['roc_auc'], 4)}); custo mensal, pouco previsível.",
            f"MILP reduz {HO.V['h3_economia_pct']} do custo esperado na instância S0, mas a heurística gulosa chega quase lá.",
            "SHAP é adequado para auditoria; LIME, não.",
            "A LOA não isola a frota na maioria dos órgãos; o acompanhamento precisa do empenho por subelemento."])
    cartao(s, 6.8, 1.35, 6.0, 5.45, "Limitações e próximos passos",
           ["MILP em instância semissintética: validar com custos e calendário reais.",
            "Testar E1–E3 na extração de 2026 da SEA/SC, conforme o pré-registro.",
            "Refazer a homologação Linux × Windows.",
            "Validar as inclusões da revisão sistemática.",
            "Incorporar as recomendações da banca (Mês 2 do cronograma)."],
           borda=AMBAR, cor_titulo=AMBAR)
    d.fonte(s, "scripts/hipoteses_oficiais.py; relatórios citados nos slides anteriores")

    # 18. Referências principais ----------------------------------------
    s = d.base("17. Referências Principais", "Seleção da lista de referências do relatório de qualificação (ABNT)")
    refs = D["referencias"]
    meio = (len(refs) + 1) // 2
    for col, grupo in enumerate((refs[:meio], refs[meio:])):
        l = 0.5 + col * 6.25
        tm = maior_fonte(lambda t, g=grupo: [(r, t, False, t * 0.45) for r in g], 5.75, 5.55, 16, 9)
        tb = s.shapes.add_textbox(Inches(l), Inches(1.35), Inches(6.0), Inches(5.6))
        tf = tb.text_frame
        tf.word_wrap = True
        for k, r_ in enumerate(grupo):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.space_after = Pt(tm * 0.45)
            autor, resto = r_.split(". ", 1) if ". " in r_ else (r_, "")
            for txt, neg in ((autor + ". ", True), (resto, False)):
                run = p.add_run()
                run.text = txt
                run.font.name, run.font.size, run.font.bold, run.font.color.rgb = "Calibri", Pt(tm), neg, CINZA_TEXTO
    d.fonte(s, "relatorios/qualificacao_pesquisa.html (seção REFERÊNCIAS), filtrada pelas obras citadas nos slides")

    # 19. Agradecimentos -------------------------------------------------
    s = d.base("Agradecimentos", "Texto dos agradecimentos da dissertação")
    blocos_ag = D["agradecimentos"]
    tm = maior_fonte(lambda t: [("".join(x for x, _ in b), t, False, t * 0.6) for b in blocos_ag], 11.8, 5.4, 24, 12)
    tb = s.shapes.add_textbox(Inches(0.75), Inches(1.45), Inches(12.0), Inches(5.5))
    tf = tb.text_frame
    tf.word_wrap = True
    for k, b in enumerate(blocos_ag):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.space_after = Pt(tm * 0.6)
        for txt, neg in b:
            run = p.add_run()
            run.text = txt
            run.font.name, run.font.size, run.font.bold = "Calibri", Pt(tm), neg
            run.font.color.rgb = VERDE_ESCURO if neg else CINZA_TEXTO
    d.fonte(s, "overleaf_dissertacao_udesc/PreTextuais/Agradecimentos.tex")

    # 20. Encerramento ---------------------------------------------------
    s = d.prs.slides.add_slide(d.prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = VERDE_ESCURO
    retangulo(s, 0, 0, 0.35, 7.5, VERMELHO_UDESC)
    texto(s, "Obrigado!", 0.9, 2.4, 11.5, 1.2, 44, True, BRANCO)
    texto(s, "Eduardo Lopes Jonker — PPGCAP/UDESC\nDúvidas e contribuições da banca", 0.9, 3.7, 11.5, 1.0, 18, False, VERDE_SUB)
    d.fontes.append(("Encerramento", ["—"]))

    d.numerar()
    return d


def main():
    D = carregar()
    n_chk = verificar(D)
    d = montar(D)
    OUT_DIR.mkdir(exist_ok=True)
    d.prs.save(OUT)
    md = [f"# Fontes da apresentação de qualificação\n",
          f"Gerado em {datetime.now():%d/%m/%Y %H:%M} por `scripts/gerar_apresentacao_qualificacao.py`. "
          f"{n_chk} verificações cruzadas aprovadas antes de salvar.\n"]
    for i, (tit, fs) in enumerate(d.fontes, 1):
        md.append(f"\n## Slide {i} — {tit}\n")
        md += [f"- {f}" for f in fs]
    FONTES_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"OK: {OUT.relative_to(ROOT)} ({len(d.prs.slides)} slides); fontes em {FONTES_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

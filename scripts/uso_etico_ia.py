#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonte única da seção "Uso ético de inteligência artificial" de todos os documentos do projeto.

O texto declara (1) a IA que é objeto da pesquisa e (2) as ferramentas de IA generativa usadas no
desenvolvimento, dizendo o que foi usado, como e por quê. As ferramentas e tarefas foram informadas
pelo autor em 16/11/2026; as tarefas feitas no Kiro IDE também constam do histórico das sessões.

Uso nos geradores
    import uso_etico_ia; uso_etico_ia.ativar()
        Insere a seção em todo PDF gerado com weasyprint.HTML(string=...) ou HTML(filename=*.html):
        antes das referências, se houver, ou no fim do documento. Não duplica.
    uso_etico_ia.html() / latex() / markdown() / slide()
        Versões para inserção direta.
"""
from __future__ import annotations

import html as _html
import re

TITULO = "Uso ético de inteligência artificial"
MARCA = "<!-- secao-uso-etico-ia -->"
DATA_DECLARACAO = "16/11/2026"

# ---------------------------------------------------------------- conteúdo
OBJETO = {
    "titulo": "IA como objeto da pesquisa",
    "o_que": [
        "Detecção de anomalias com Isolation Forest.",
        "Classificação do risco de manutenção corretiva e regressão do custo mensal (HistGradientBoosting, Random Forest, "
        "Extra Trees, árvore de decisão, regressão logística, SVR e SVC).",
        "Explicação das previsões com SHAP e LIME.",
        "Comunidades de oficinas em grafos (Louvain) e previsão de séries temporais (SARIMA, ETS) para o planejamento orçamentário.",
        "Otimização da manutenção preventiva com programação linear inteira mista (MILP), que é otimização matemática e não aprendizado de máquina.",
    ],
    "como": [
        "Dados administrativos da SEA/SC usados com autorização institucional, mantidos no computador do autor e fora do repositório público.",
        "Identificadores de veículos e oficinas pseudonimizados com HMAC-SHA-256 e campos pessoais anonimizados (Microsoft Presidio), "
        "conforme a LGPD (Lei nº 13.709/2018).",
        "Validação temporal (treino até dez/2024, teste a partir de jan/2025), intervalos de confiança e hipóteses com critérios "
        "registrados antes da execução.",
        "Resultados negativos são publicados: H2 e H4 não foram sustentadas, e o LIME se mostrou pouco fiel ao modelo.",
        "Os modelos apoiam a decisão e não a substituem. Uma anomalia indica um caso para conferência, não uma irregularidade; "
        "a decisão é sempre de um servidor responsável.",
    ],
    "por_que": [
        "Apoiar a gestão pública da frota com informação verificável, em linha com a transparência e a motivação dos atos "
        "exigidas pela Lei nº 14.133/2021.",
        "Explicações auditáveis permitem que gestores e órgãos de controle contestem cada recomendação.",
    ],
}

GENERATIVA = {
    "titulo": "Ferramentas de IA generativa no desenvolvimento do trabalho",
    "o_que": [
        "Gemini Code Assist e GitHub Copilot, como assistentes de código.",
        "Kiro IDE e Google Antigravity IDE, ambientes de desenvolvimento com agentes de IA.",
        "Overleaf e Visual Studio Code, editores em que essas ferramentas foram usadas na redação em LaTeX e no código.",
    ],
    "como": [
        "Análise e correção de erros de código.",
        "Escrita e alteração de scripts de análise, de busca de literatura e de geração de relatórios e slides "
        "(principalmente no Kiro IDE).",
        "Revisão da redação e adequação às normas da ABNT.",
        "Montagem de slides e de relatórios a partir dos resultados calculados.",
        "Todas as sugestões foram revisadas pelo autor. O código foi validado por execução e por verificações automáticas "
        "que comparam os números entre as etapas.",
    ],
    "nao": [
        "Não gerou dados nem resultados: todo número vem da execução dos scripts sobre os dados.",
        "Não gerou figuras: os gráficos são produzidos pelos scripts a partir dos resultados.",
        "Não definiu nem ajustou hipóteses ou critérios, que foram registrados antes da execução.",
        "Não substituiu a leitura das fontes: as referências são conferidas pelo DOI.",
    ],
    "por_que": [
        "Ganhar tempo em tarefas repetitivas, achar erros de código mais cedo e padronizar o texto e a formatação.",
    ],
    "dados": "As bases administrativas ficaram no computador do autor. As ferramentas operaram sobre o código, os registros "
             "de execução e resultados agregados; também se aplicam as políticas de privacidade de cada fornecedor.",
}

RESPONSABILIDADE = ("O autor revisou todo o conteúdo gerado ou sugerido por essas ferramentas e assume integral responsabilidade "
                    f"pelo texto, pelo código, pelos dados e pelas conclusões deste trabalho. Declaração feita em {DATA_DECLARACAO}.")

INTRO = ("Esta seção informa onde a inteligência artificial aparece neste trabalho: como objeto da pesquisa e como ferramenta "
         "de apoio ao desenvolvimento. Para cada caso, diz o que foi usado, como e por quê.")


# ---------------------------------------------------------------- saídas
def _ul(itens):
    return "<ul>" + "".join(f"<li>{_html.escape(i)}</li>" for i in itens) + "</ul>"


def html(nivel: str = "h2") -> str:
    e = _html.escape
    sub = {"h1": "h2", "h2": "h3"}.get(nivel, "h4")
    return (f"{MARCA}<section class='uso-etico-ia'>"
            f"<{nivel}>{e(TITULO)}</{nivel}><p>{e(INTRO)}</p>"
            f"<{sub}>1. {e(OBJETO['titulo'])}</{sub}>"
            f"<p><b>O que:</b></p>{_ul(OBJETO['o_que'])}<p><b>Como:</b></p>{_ul(OBJETO['como'])}"
            f"<p><b>Por quê:</b></p>{_ul(OBJETO['por_que'])}"
            f"<{sub}>2. {e(GENERATIVA['titulo'])}</{sub}>"
            f"<p><b>O que:</b></p>{_ul(GENERATIVA['o_que'])}<p><b>Como (tarefas):</b></p>{_ul(GENERATIVA['como'])}"
            f"<p><b>O que as ferramentas não fizeram:</b></p>{_ul(GENERATIVA['nao'])}"
            f"<p><b>Por quê:</b></p>{_ul(GENERATIVA['por_que'])}"
            f"<p><b>Dados:</b> {e(GENERATIVA['dados'])}</p>"
            f"<p style='border-left:3pt solid #00693e;padding-left:6pt'><b>Responsabilidade.</b> {e(RESPONSABILIDADE)}</p>"
            f"</section>")


def _tex(s: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("–", "--"), ("“", "``"), ("”", "''")):
        s = s.replace(a, b)
    return s


def latex(comando: str = "section") -> str:
    """Seção LaTeX. comando='chapter' para apêndice/capítulo, 'section' para seção."""
    sub = {"chapter": "section", "section": "subsection", "subsection": "subsubsection"}[comando]
    it = lambda xs: "\\begin{itemize}\n" + "\n".join(f"  \\item {_tex(x)}" for x in xs) + "\n\\end{itemize}"
    tit = _tex(TITULO).upper() if comando == "chapter" else _tex(TITULO)
    return "\n".join([
        "% Gerado por scripts/uso_etico_ia.py. Não editar à mão.",
        f"\\{comando}{{{tit}}}", "\\label{sec:uso-etico-ia}", _tex(INTRO), "",
        f"\\{sub}{{{_tex(OBJETO['titulo'])}}}",
        "\\textbf{O que.}", it(OBJETO["o_que"]), "\\textbf{Como.}", it(OBJETO["como"]), "\\textbf{Por quê.}", it(OBJETO["por_que"]),
        f"\\{sub}{{{_tex(GENERATIVA['titulo'])}}}",
        "\\textbf{O que.}", it(GENERATIVA["o_que"]), "\\textbf{Como (tarefas).}", it(GENERATIVA["como"]),
        "\\textbf{O que as ferramentas não fizeram.}", it(GENERATIVA["nao"]), "\\textbf{Por quê.}", it(GENERATIVA["por_que"]),
        "", f"\\textbf{{Dados.}} {_tex(GENERATIVA['dados'])}", "",
        f"\\textbf{{Responsabilidade.}} {_tex(RESPONSABILIDADE)}", ""])


def markdown(nivel: int = 2) -> str:
    h = "#" * nivel
    l = lambda xs: "\n".join(f"- {x}" for x in xs)
    return "\n".join([
        f"{h} {TITULO}", "", INTRO, "",
        f"{h}# 1. {OBJETO['titulo']}", "", "**O que:**", "", l(OBJETO["o_que"]), "", "**Como:**", "", l(OBJETO["como"]), "",
        "**Por quê:**", "", l(OBJETO["por_que"]), "",
        f"{h}# 2. {GENERATIVA['titulo']}", "", "**O que:**", "", l(GENERATIVA["o_que"]), "", "**Como (tarefas):**", "",
        l(GENERATIVA["como"]), "", "**O que as ferramentas não fizeram:**", "", l(GENERATIVA["nao"]), "", "**Por quê:**", "",
        l(GENERATIVA["por_que"]), "", f"**Dados:** {GENERATIVA['dados']}", "", f"**Responsabilidade.** {RESPONSABILIDADE}", ""])


def slide() -> dict:
    """Conteúdo resumido para um slide de três colunas."""
    return {
        "titulo": TITULO,
        "subtitulo": "O que foi usado, como e por quê",
        "colunas": [
            ("IA como objeto da pesquisa",
             ["Isolation Forest, ensembles, SVR/SVC, SHAP, LIME, Louvain e SARIMA.",
              "Dados da SEA/SC pseudonimizados (HMAC) e anonimizados (LGPD), fora do repositório público.",
              "Hipóteses pré-registradas; resultados negativos publicados (H2, H4).",
              "Os modelos apoiam; a decisão é de um servidor responsável."]),
            ("IA generativa no desenvolvimento",
             ["Gemini Code Assist, GitHub Copilot, Kiro IDE e Antigravity IDE, no Overleaf e no VS Code.",
              "Tarefas: correção e escrita de código, revisão de redação e ABNT, slides e relatórios.",
              "Não gerou dados, resultados, figuras nem hipóteses.",
              "Código validado por execução e verificações automáticas."]),
            ("Por quê e responsabilidade",
             ["Transparência e auditabilidade na gestão pública (Lei nº 14.133/2021).",
              "Ganho de tempo e detecção precoce de erros.",
              "O autor revisou todo o conteúdo e assume integral responsabilidade."]),
        ],
    }


# ---------------------------------------------------------------- inserção automática nos PDFs
_REF = re.compile(r"<h[1-3][^>]*>\s*(?:<[^>]+>\s*)*(?:\d+[\.\s]*)?(?:REFER[ÊE]NCIAS|Refer[êe]ncias|BIBLIOGRAFIA|Bibliografia|"
                  r"References|REFERENCES)", re.I)


def inserir_html(doc: str) -> str:
    if MARCA in doc or "class='uso-etico-ia'" in doc:
        return doc
    bloco = html()
    ms = list(_REF.finditer(doc))
    if ms:                                   # a última ocorrência é a seção de referências (as anteriores podem ser do sumário)
        m = ms[-1]
        return doc[:m.start()] + bloco + doc[m.start():]
    i = doc.lower().rfind("</body>")
    return (doc[:i] + bloco + doc[i:]) if i >= 0 else doc + bloco


def ativar():
    """Faz weasyprint.HTML(...) inserir a seção em todo PDF gerado pelo processo."""
    import weasyprint
    if getattr(weasyprint.HTML, "_uso_etico_ia", False):
        return
    original = weasyprint.HTML

    class HTML(original):  # type: ignore[misc, valid-type]
        _uso_etico_ia = True

        def __init__(self, *a, **kw):
            if isinstance(kw.get("string"), str):
                kw["string"] = inserir_html(kw["string"])
            elif kw.get("filename") and str(kw["filename"]).lower().endswith((".html", ".htm")):
                from pathlib import Path
                p = Path(kw.pop("filename"))
                kw["string"] = inserir_html(p.read_text(encoding="utf-8"))
                kw.setdefault("base_url", str(p.parent))
            super().__init__(*a, **kw)

    weasyprint.HTML = HTML


def texto_curto() -> str:
    """Parágrafo único para artigos curtos (limite de páginas)."""
    return ("Os modelos de IA estudados (Isolation Forest, ensembles, SVR/SVC, SHAP, LIME, Louvain, SARIMA) usaram dados "
            "administrativos da SEA/SC com identificadores pseudonimizados (HMAC-SHA-256) e campos pessoais anonimizados, conforme "
            "a LGPD; os modelos apoiam a decisão, que cabe a um servidor responsável. No desenvolvimento, o autor usou ferramentas de "
            "IA generativa (Gemini Code Assist, GitHub Copilot, Kiro IDE e Google Antigravity IDE, no Overleaf e no Visual Studio Code) "
            "para analisar e corrigir erros de código, escrever e alterar scripts, revisar a redação e a formatação ABNT e montar "
            "slides e relatórios. Essas ferramentas não geraram dados, resultados, figuras nem hipóteses. " + RESPONSABILIDADE)


# ---------------------------------------------------------------- gravação nos documentos-fonte
INI, FIM = "<!-- inicio-uso-etico-ia -->", "<!-- fim-uso-etico-ia -->"
INI_TEX, FIM_TEX = "% inicio-uso-etico-ia", "% fim-uso-etico-ia"


def _substituir_ou_inserir(txt: str, ini: str, fim: str, bloco: str, antes_de: re.Pattern | None) -> str:
    novo = f"{ini}\n{bloco}\n{fim}\n"
    if ini in txt and fim in txt:
        a, b = txt.index(ini), txt.index(fim) + len(fim)
        return txt[:a] + novo.rstrip("\n") + txt[b:]
    ms = list(antes_de.finditer(txt)) if antes_de else []
    if ms:
        m = ms[-1]
        return txt[:m.start()] + novo + "\n" + txt[m.start():]
    return txt.rstrip("\n") + "\n\n" + novo


def gravar_arquivos(raiz=None) -> list[str]:
    """Grava/atualiza a seção nos documentos-fonte: dissertação LaTeX (apêndice E), artigos SBC (.tex e .md),
    README.md e docs/uso_etico_ia.md. Retorna a lista de arquivos alterados."""
    from pathlib import Path
    R = Path(raiz) if raiz else Path(__file__).resolve().parent.parent
    alterados = []
    def escrever(p: Path, txt: str):
        if not p.exists() or p.read_text(encoding="utf-8") != txt:
            p.write_text(txt, encoding="utf-8")
            alterados.append(str(p.relative_to(R)))
    # 1. Dissertação: apêndice E incluído no main.tex
    ov = R / "overleaf_dissertacao_udesc"
    escrever(ov / "PosTextuais/ApendiceE.tex", latex("chapter"))
    main = ov / "main.tex"
    m = main.read_text(encoding="utf-8")
    if "\\include{PosTextuais/ApendiceE}" not in m:
        m = m.replace("\\include{PosTextuais/ApendiceD}", "\\include{PosTextuais/ApendiceD}\n\\include{PosTextuais/ApendiceE}", 1)
        escrever(main, m)
    # 2. Artigos SBC: completos recebem a seção; curtos, o parágrafo
    ref_tex = re.compile(r"^\\begin\{thebibliography\}|^\\section\*\{Refer|^\\bibliography\{", re.M)
    ref_md = re.compile(r"^#+\s*\**\s*Refer[êe]ncias", re.M | re.I)
    for p in sorted((R / "SBC").glob("*.tex")):
        completo = "completo" in p.name
        bloco = latex("section").replace("\\label{sec:uso-etico-ia}\n", "\\label{sec:uso-etico-ia}\n") if completo else \
            f"\\section*{{{_tex(TITULO)}}}\n{_tex(texto_curto())}"
        escrever(p, _substituir_ou_inserir(p.read_text(encoding="utf-8"), INI_TEX, FIM_TEX, bloco, ref_tex))
    for p in sorted((R / "SBC").glob("*.md")):
        bloco = markdown(2) if "completo" in p.name else f"## {TITULO}\n\n{texto_curto()}\n"
        escrever(p, _substituir_ou_inserir(p.read_text(encoding="utf-8"), INI, FIM, bloco, ref_md))
    # 3. README e documento próprio
    readme = R / "README.md"
    escrever(readme, _substituir_ou_inserir(readme.read_text(encoding="utf-8"), INI, FIM, markdown(2), None))
    (R / "docs").mkdir(exist_ok=True)
    escrever(R / "docs/uso_etico_ia.md", "# Declaração de uso ético de inteligência artificial\n\n"
             "Gerado por `scripts/uso_etico_ia.py`, fonte única do texto em todos os documentos.\n\n" + markdown(2))
    return alterados


if __name__ == "__main__":
    for a in gravar_arquivos():
        print("atualizado:", a)

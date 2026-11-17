# -*- coding: utf-8 -*-
"""
Biblio-now · planilha de fichamento e relatório de protocolo. Autor: Eduardo Lopes Jonker.

Depois de cada execução:
  repositorio/fichamento.xlsx
      Aba "Fichamento": uma linha por obra do repositório. As colunas de identificação vêm dos metadados;
      as colunas de fichamento (objetivo, método, resultados...) são preenchidas pelo pesquisador e
      PRESERVADAS quando a planilha é regenerada (casamento pelo ID da obra).
      Aba "Buscas": uma linha por execução.  Aba "Leia-me": como usar.
  repositorio/protocolo/registro_incorporacoes.csv   só acrescenta linhas (obra, busca, data)
  repositorio/protocolo/registro_buscas.csv          só acrescenta linhas (uma por execução)
  repositorio/protocolo/protocolo_sigma.html         relatório do protocolo, regenerado a cada execução
  repositorio/protocolo/protocolo_sigma.pdf          o mesmo em PDF, se o WeasyPrint estiver instalado
"""
from __future__ import annotations

import csv
import html
import json
from datetime import datetime
from pathlib import Path

VERSAO = "1.0.0"
AUTOR = "Eduardo Lopes Jonker"

COLS_ID = [("id", "ID da obra", 34), ("titulo", "Título", 60), ("autores", "Autores", 36), ("ano", "Ano", 7),
           ("veiculo", "Veículo", 30), ("doi", "DOI", 26), ("url", "Link", 26), ("citacoes", "Citações", 9),
           ("fonte", "Base de origem", 16), ("verificacao", "Blocos atendidos", 18), ("resumo", "Resumo", 70),
           ("pdf", "Arquivo PDF", 30), ("txt", "Arquivo TXT", 30), ("bib", "Arquivo BibTeX", 30), ("sha256_pdf", "SHA-256 do PDF", 20),
           ("palavras_txt", "Palavras no TXT", 10), ("incorporada_em", "Incorporada em", 18),
           ("busca_origem_nome", "Busca de origem", 24), ("buscas_n", "Nº de buscas que a encontraram", 12)]
COLS_FICHA = [("leitura", "Situação da leitura", 16), ("relevancia", "Relevância (1–5)", 10),
              ("objetivo", "Objetivo / pergunta", 40), ("metodo", "Método", 40), ("dados", "Dados / amostra", 30),
              ("resultados", "Principais resultados", 45), ("contribuicao", "Contribuição para a pesquisa", 40),
              ("limitacoes", "Limitações", 35), ("citacoes_diretas", "Citações diretas (com página)", 45),
              ("palavras_chave", "Palavras-chave", 25), ("notas", "Notas", 40)]


def _txt_celula(v):
    if isinstance(v, list):
        v = "; ".join(str(x) for x in v)
    s = "" if v is None else str(v)
    return s[:32000]                                   # limite de caracteres por célula do Excel


def _ler_manuais(xlsx: Path) -> dict:
    """Valores digitados pelo pesquisador nas colunas de fichamento, por ID da obra."""
    if not xlsx.exists():
        return {}
    from openpyxl import load_workbook
    try:
        wb = load_workbook(xlsx, read_only=True, data_only=True)
    except Exception:  # noqa: BLE001 - planilha aberta em outro programa ou corrompida
        return {}
    if "Fichamento" not in wb.sheetnames:
        return {}
    ws = wb["Fichamento"]
    linhas = ws.iter_rows(values_only=True)
    cab = next(linhas, None) or ()
    rot2chave = {rot: k for k, rot, _ in COLS_FICHA}
    idx_id = list(cab).index("ID da obra") if "ID da obra" in cab else None
    if idx_id is None:
        return {}
    out = {}
    for row in linhas:
        if not row or not row[idx_id]:
            continue
        vals = {rot2chave[c]: row[i] for i, c in enumerate(cab) if c in rot2chave and i < len(row) and row[i] not in (None, "")}
        if vals:
            out[str(row[idx_id])] = vals
    wb.close()
    return out


def gerar_planilha(repo_raiz: Path, obras: dict, buscas: list[dict]) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    xlsx = repo_raiz / "fichamento.xlsx"
    manuais = _ler_manuais(xlsx)
    wb = Workbook()
    ws = wb.active
    ws.title = "Fichamento"
    cab = [rot for _, rot, _ in COLS_ID] + [rot for _, rot, _ in COLS_FICHA]
    ws.append(cab)
    azul, verde = PatternFill("solid", fgColor="1F3A5F"), PatternFill("solid", fgColor="2E7D5B")
    for i, c in enumerate(ws[1], 1):
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = azul if i <= len(COLS_ID) else verde
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for ob in sorted(obras.values(), key=lambda o: (o.get("incorporada_em", ""), o.get("id", ""))):
        ob = dict(ob, buscas_n=len(ob.get("buscas") or []))
        man = manuais.get(ob["id"], {})
        ws.append([_txt_celula(ob.get(k)) for k, _, _ in COLS_ID] + [man.get(k, "") for k, _, _ in COLS_FICHA])
    for i, (_, _, w) in enumerate(COLS_ID + COLS_FICHA, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=False, vertical="top")
    n = ws.max_row
    if n >= 2:
        col = lambda chave: get_column_letter(len(COLS_ID) + [k for k, _, _ in COLS_FICHA].index(chave) + 1)
        dv1 = DataValidation(type="list", formula1='"não lida,em leitura,lida,descartada"', allow_blank=True)
        dv2 = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
        ws.add_data_validation(dv1); ws.add_data_validation(dv2)
        dv1.add(f"{col('leitura')}2:{col('leitura')}{n + 500}")
        dv2.add(f"{col('relevancia')}2:{col('relevancia')}{n + 500}")
    wb2 = wb.create_sheet("Buscas")
    cb = ["ID da busca", "Nome", "Origem", "Início", "Fim", "Estado", "Blocos", "Mínimo de blocos", "Registros únicos",
          "Atendem", "PDFs baixados", "Já existiam", "Sem PDF aberto", "Falharam"]
    wb2.append(cb)
    for c in wb2[1]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), azul
    for b in buscas:
        wb2.append([b.get("id"), b.get("rotulo"), b.get("origem"), b.get("inicio"), b.get("fim"), b.get("estado"),
                    " AND ".join("(" + " OR ".join(x) + ")" for x in b.get("blocos") or []), b.get("minimo_blocos"),
                    b.get("registros"), b.get("atendem"), b.get("baixados"), b.get("ja_existiam"), b.get("sem_pdf", 0), b.get("falharam")])
    for i, w in enumerate([30, 28, 20, 20, 20, 12, 60, 10, 10, 10, 10, 10, 10, 10], 1):
        wb2.column_dimensions[get_column_letter(i)].width = w
    lm = wb.create_sheet("Leia-me")
    for linha in [f"Biblio-now {VERSAO} · {AUTOR}", "",
                  "Aba Fichamento: uma linha por obra. As colunas em azul são preenchidas pelo Biblio-now; as verdes são suas.",
                  "Pode preencher as colunas verdes à vontade: elas são mantidas quando a planilha é atualizada após uma nova busca.",
                  "Não mude o texto da coluna 'ID da obra' nem os títulos das colunas verdes: é por eles que o fichamento é recuperado.",
                  "Feche a planilha antes de rodar uma busca; com ela aberta, o Windows impede a gravação e a atualização é adiada.",
                  "Os arquivos citados nas colunas PDF, TXT e BibTeX estão nas pastas pdf/, txt/ e bib/ do repositório.",
                  f"Atualizada em {datetime.now():%d/%m/%Y %H:%M}."]:
        lm.append([linha])
    lm.column_dimensions["A"].width = 120
    tmp = xlsx.with_suffix(".tmp.xlsx")
    wb.save(tmp)
    try:
        tmp.replace(xlsx)
    except PermissionError:                             # planilha aberta no Excel (Windows)
        alt = repo_raiz / f"fichamento_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        tmp.replace(alt)
        return alt
    return xlsx


# ---------------------------------------------------------------- protocolo
def _ultimo_hash(f: Path) -> str:
    if not f.exists():
        return "0" * 64
    with open(f, encoding="utf-8-sig") as h:
        linhas = list(csv.reader(h, delimiter=";"))
    return linhas[-1][-1] if len(linhas) > 1 and linhas[-1] else "0" * 64


def _anexar_csv(f: Path, cab: list[str], linhas: list[list]):
    """Só acrescenta. Cada linha leva o hash da anterior e o próprio (SHA-256): alterar ou apagar
    uma linha antiga quebra a cadeia, e a verificação aponta onde."""
    from .seguranca import hash_linha
    novo = not f.exists()
    ant = _ultimo_hash(f)
    with open(f, "a", newline="", encoding="utf-8-sig") as h:
        w = csv.writer(h, delimiter=";")
        if novo:
            w.writerow(cab + ["hash_anterior", "hash_linha"])
        for l in linhas:
            hl = hash_linha(ant, l)
            w.writerow(list(l) + [ant, hl])
            ant = hl


def verificar_cadeia(f: Path) -> dict:
    """Recalcula a cadeia de hashes de um registro do protocolo."""
    from .seguranca import hash_linha
    if not f.exists():
        return {"arquivo": f.name, "linhas": 0, "integro": True, "primeira_falha": None}
    with open(f, encoding="utf-8-sig") as h:
        linhas = list(csv.reader(h, delimiter=";"))
    ant = "0" * 64
    for i, l in enumerate(linhas[1:], 2):
        if len(l) < 2 or l[-2] != ant or hash_linha(ant, l[:-2]) != l[-1]:
            return {"arquivo": f.name, "linhas": len(linhas) - 1, "integro": False, "primeira_falha": i}
        ant = l[-1]
    return {"arquivo": f.name, "linhas": len(linhas) - 1, "integro": True, "primeira_falha": None}


def registrar(repo_raiz: Path, ex_resumo: dict, obras: dict):
    """Acrescenta a execução e as obras incorporadas por ela aos registros do protocolo (só acréscimos)."""
    prot = repo_raiz / "protocolo"
    prot.mkdir(exist_ok=True)
    b = ex_resumo
    _anexar_csv(prot / "registro_buscas.csv",
                ["data_registro", "id_busca", "nome", "origem", "inicio", "fim", "estado", "consulta_openalex", "minimo_blocos",
                 "correspondencias_bases", "registros_unicos", "atendem", "pdfs_baixados", "ja_existiam", "sem_pdf_aberto", "falharam"],
                [[datetime.now().isoformat(timespec="seconds"), b["id"], b.get("rotulo", ""), b.get("origem", ""), b.get("inicio"), b.get("fim"),
                  b.get("estado"), " AND ".join("(" + " OR ".join(x) + ")" for x in b.get("blocos") or []), b.get("minimo_blocos"),
                  json.dumps(b.get("totais_bases", {}), ensure_ascii=False), b.get("registros"), b.get("atendem"), b.get("baixados"),
                  b.get("ja_existiam"), b.get("sem_pdf", 0), b.get("falharam")]])
    novas = [o for o in obras.values() if o.get("busca_origem") == b["id"]]
    if novas:
        _anexar_csv(prot / "registro_incorporacoes.csv",
                    ["data_incorporacao", "id_busca", "nome_busca", "id_obra", "titulo", "autores", "ano", "doi", "pdf", "txt", "bib"],
                    [[o.get("incorporada_em"), b["id"], b.get("rotulo", ""), o["id"], o.get("titulo"), "; ".join(o.get("autores") or [])[:300],
                      o.get("ano"), o.get("doi"), o.get("pdf"), o.get("txt"), o.get("bib")] for o in novas])


def _ler_csv(f: Path):
    if not f.exists():
        return []
    with open(f, encoding="utf-8-sig") as h:
        return list(csv.DictReader(h, delimiter=";"))


def gerar_protocolo(repo_raiz: Path, obras: dict, ultima: dict | None = None) -> Path:
    e = html.escape
    prot = repo_raiz / "protocolo"
    buscas = _ler_csv(prot / "registro_buscas.csv")
    incorp = _ler_csv(prot / "registro_incorporacoes.csv")
    num = lambda x: f"{int(x):,}".replace(",", ".") if str(x).strip().lstrip("-").isdigit() else e(str(x or "—"))
    tot = lambda campo: sum(int(b.get(campo) or 0) for b in buscas if str(b.get(campo) or "").isdigit())
    agora = datetime.now()
    txt_ok = sum(1 for o in obras.values() if o.get("txt_extraido"))
    cadeias = [verificar_cadeia(prot / n) for n in ("registro_buscas.csv", "registro_incorporacoes.csv")]
    css = """@page{size:A4;margin:1.8cm 1.6cm;@bottom-right{content:counter(page) " / " counter(pages);font:8pt Arial;color:#667}}
body{font-family:Arial,Helvetica,sans-serif;font-size:10pt;color:#1d2433;line-height:1.4;max-width:1100px;margin:auto;padding:16px}
h1{color:#1f3a5f;font-size:20pt;margin:0}.marca{color:#2e7d5b;font-weight:bold;letter-spacing:.5px}
h2{color:#1f3a5f;border-bottom:2px solid #2e7d5b;padding-bottom:2px;margin-top:20px;font-size:13pt}
table{width:100%;border-collapse:collapse;font-size:8.6pt;margin:6px 0 12px}th{background:#1f3a5f;color:#fff;text-align:left;padding:4px}
td{border-bottom:1px solid #d7dde8;padding:3px 4px;vertical-align:top}tr:nth-child(even) td{background:#f4f7fb}
.kpi{display:flex;gap:8px;flex-wrap:wrap}.kpi div{flex:1 1 150px;border:1px solid #2e7d5b;border-radius:6px;padding:6px 10px}
.kpi b{display:block;font-size:16pt;color:#2e7d5b}.nota{background:#fff8e6;border-left:4px solid #d99a00;padding:6px 10px;font-size:9pt}
.atual{background:#e8f4ee;border-left:4px solid #2e7d5b;padding:6px 10px}"""
    H = [f"<html><head><meta charset='utf-8'><title>Protocolo Sigma · Biblio-now</title><style>{css}</style></head><body>",
         f"<p class='marca'>BIBLIO-NOW</p><h1>Protocolo Sigma do repositório</h1>",
         f"<p>Registro auditável das buscas e das obras incorporadas. Gerado automaticamente pelo Biblio-now {VERSAO} "
         f"({e(AUTOR)}). <b>Última atualização: {agora:%d/%m/%Y às %H:%M}</b>.</p>"]
    if ultima:
        H.append(f"<p class='atual'>Atualizado após a busca <b>{e(ultima.get('rotulo') or ultima['id'])}</b> "
                 f"({e(ultima.get('origem', ''))}), executada de {e((ultima.get('inicio') or '').replace('T', ' '))} a "
                 f"{e((ultima.get('fim') or '').replace('T', ' '))}: {num(ultima.get('baixados', 0))} obra(s) nova(s), "
                 f"{num(ultima.get('ja_existiam', 0))} já existente(s), {num(ultima.get('falharam', 0))} falha(s) de download.</p>")
    H.append(f"""<div class='kpi'><div><b>{num(len(buscas))}</b>execuções registradas</div><div><b>{num(len(obras))}</b>obras no repositório</div>
<div><b>{num(txt_ok)}</b>com texto extraído (TXT)</div><div><b>{num(tot('registros_unicos'))}</b>registros avaliados (soma das execuções)</div></div>""")
    H.append("<h2>Integridade dos registros</h2><table><tr><th>Registro</th><th>Linhas</th><th>Cadeia de hashes (SHA-256)</th></tr>" +
             "".join(f"<tr><td>{e(c['arquivo'])}</td><td>{num(c['linhas'])}</td><td>" +
                     ("íntegra" if c["integro"] else f"<b style='color:#b42318'>QUEBRADA na linha {c['primeira_falha']}</b>") + "</td></tr>"
                     for c in cadeias) + "</table>")
    H.append("<h2>1. Método</h2><ul>"
             "<li><b>Fontes:</b> OpenAlex e Semantic Scholar, por API pública; PDFs só de versões de acesso aberto (links das bases, página do artigo e Unpaywall).</li>"
             "<li><b>Consulta:</b> blocos de termos; OR dentro do bloco e AND entre blocos. O registro só é baixado se tiver o mínimo de blocos definido na busca no título ou no resumo.</li>"
             "<li><b>Deduplicação:</b> por DOI ou título normalizado e pelo conteúdo do PDF (MD5). Uma obra encontrada de novo não é baixada outra vez; a nova busca é associada a ela.</li>"
             "<li><b>Arquivos de cada obra:</b> <code>pdf/</code> (texto completo), <code>txt/</code> (texto extraído) e <code>bib/</code> (referência BibTeX).</li>"
             "<li><b>Registros:</b> <code>registro_buscas.csv</code> e <code>registro_incorporacoes.csv</code> só recebem acréscimos, com data e hora.</li></ul>")
    H.append("<h2>2. Fluxo acumulado</h2><table><tr><th>Etapa</th><th>Quantidade</th></tr>" +
             "".join(f"<tr><td>{a}</td><td>{num(b)}</td></tr>" for a, b in [
                 ("Registros únicos avaliados (soma das execuções)", tot("registros_unicos")),
                 ("Atendem ao mínimo de blocos", tot("atendem")),
                 ("PDFs baixados (obras novas)", tot("pdfs_baixados")),
                 ("Encontrados de novo (já no repositório)", tot("ja_existiam")),
                 ("Sem versão de acesso aberto", tot("sem_pdf_aberto")),
                 ("Falhas de download", tot("falharam")),
                 ("Obras no repositório hoje", len(obras))]) + "</table>")
    H.append("<h2>3. Registro das execuções</h2><table><tr><th>Data</th><th>Nome</th><th>Origem</th><th>Consulta</th><th>Mín.</th>"
             "<th>Registros</th><th>Atendem</th><th>Novas</th><th>Já existiam</th><th>Falhas</th><th>Estado</th></tr>" +
             "".join(f"<tr><td>{e((b.get('inicio') or '').replace('T', ' '))}</td><td>{e(b.get('nome') or b.get('id_busca'))}</td>"
                     f"<td>{e(b.get('origem', ''))}</td><td>{e(b.get('consulta_openalex', ''))}</td><td>{e(str(b.get('minimo_blocos', '')))}</td>"
                     f"<td>{num(b.get('registros_unicos'))}</td><td>{num(b.get('atendem'))}</td><td>{num(b.get('pdfs_baixados'))}</td>"
                     f"<td>{num(b.get('ja_existiam'))}</td><td>{num(b.get('falharam'))}</td><td>{e(b.get('estado', ''))}</td></tr>"
                     for b in reversed(buscas)) + "</table>")
    H.append(f"<h2>4. Obras incorporadas ({num(len(incorp))})</h2><table><tr><th>#</th><th>Incorporada em</th><th>Busca</th>"
             "<th>Título</th><th>Autores</th><th>Ano</th><th>DOI</th></tr>" +
             "".join(f"<tr><td>{i}</td><td>{e((o.get('data_incorporacao') or '').replace('T', ' '))}</td><td>{e(o.get('nome_busca') or o.get('id_busca'))}</td>"
                     f"<td>{e(o.get('titulo', ''))}</td><td>{e((o.get('autores') or '')[:120])}</td><td>{e(str(o.get('ano', '')))}</td>"
                     f"<td>{e(o.get('doi', ''))}</td></tr>" for i, o in enumerate(incorp, 1)) + "</table>")
    from . import relatorio_baixa as rb
    total, m_ult, r_ult = rb.consolidar(repo_raiz)
    if total:
        H.append(f"<h2>5. Matriz estatística da baixa</h2><p>Contagens e percentuais na linha, calculados nos registros de cada busca. "
                 f"Consolidada: soma das {num(total['buscas'])} busca(s) com relatório (um artigo encontrado em duas buscas conta nas duas). "
                 f"Arquivos: <code>relatorios/matriz_baixa_consolidada.csv</code> e <code>relatorios/&lt;busca&gt;/matriz_baixa.csv</code>.</p>")
        H.append(rb.html_matriz(total, "5.1 Consolidada (todas as buscas)"))
        if m_ult:
            H.append(rb.html_matriz(m_ult, f"5.2 Última busca: {(r_ult or {}).get('rotulo') or (r_ult or {}).get('id', '')}"))
        H.append("<ul>" + "".join(f"<li>{e(n)}</li>" for n in total["notas"]) + "</ul>")
    H.append("<p class='nota'>A busca confere termos, não a qualidade do veículo: preprints e revistas sem revisão por pares podem aparecer. "
             "Antes de citar, confira a obra e registre a avaliação na planilha de fichamento.</p>")
    H.append(f"<p style='color:#667;font-size:8.5pt'>Biblio-now {VERSAO} · © {agora:%Y} {e(AUTOR)}</p></body></html>")
    f = prot / "protocolo_sigma.html"
    f.write_text("\n".join(H), encoding="utf-8")
    try:                                               # PDF opcional (WeasyPrint precisa de bibliotecas do sistema)
        import weasyprint
        weasyprint.HTML(string="\n".join(H), base_url=str(prot)).write_pdf(prot / "protocolo_sigma.pdf")
    except Exception:  # noqa: BLE001
        pass
    import shutil
    rel = repo_raiz / "relatorios"
    rel.mkdir(exist_ok=True)
    for nome in ("protocolo_sigma.html", "protocolo_sigma.pdf"):
        if (prot / nome).exists():
            shutil.copy2(prot / nome, rel / nome)
    return f


def atualizar_tudo(repo_raiz: Path, obras: dict, buscas: list[dict], ultima: dict | None):
    if ultima:
        registrar(repo_raiz, ultima, obras)
    planilha = gerar_planilha(repo_raiz, obras, buscas)
    protocolo = gerar_protocolo(repo_raiz, obras, ultima)
    return planilha, protocolo

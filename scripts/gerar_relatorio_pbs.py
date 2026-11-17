#!/usr/bin/env python3
"""
Gera PBS.pdf: relatório de scripts, bases de dados, bases externas baixadas
e sistemas próprios de API do projeto.

Todos os números são lidos do disco no momento da execução (docstrings,
rotas FastAPI, tamanhos e contagens de arquivos, JSONs de resultados).
Nada é digitado à mão, exceto as descrições curtas das bases operacionais
e o texto interpretativo das seções de diferenciais e limitações, que citam
o arquivo e a linha de onde cada afirmação foi verificada.

Uso:
  .venv/bin/python scripts/gerar_relatorio_pbs.py           # -> PBS.pdf
"""
from __future__ import annotations

import ast
import csv
import html
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import weasyprint

import sys as _sys_ia; from pathlib import Path as _P_ia; _sys_ia.path.insert(0, str(_P_ia(__file__).resolve().parent))
import uso_etico_ia; uso_etico_ia.ativar()  # seção "Uso ético de inteligência artificial" em todo PDF
ROOT = Path(__file__).resolve().parent.parent
SAIDA = ROOT / "PBS.pdf"
LOGO = Path("/tmp/udesc_logos/Imagem 20.png")

GRUPOS_SCRIPTS = [
    ("Pipeline científico (dissertacao_frotas/src)", "dissertacao_frotas/src"),
    ("Módulos analíticos (src)", "src"),
    ("API acadêmica (src/api)", "src/api"),
    ("Plataforma enterprise (src/enterprise)", "src/enterprise"),
    ("Sistema de gestão de frotas (sistema_gestao_frotas)", "sistema_gestao_frotas"),
    ("Grafo Neo4j (graphdb)", "graphdb"),
    ("Scripts de apoio, relatórios e literatura (scripts)", "scripts"),
    ("Testes automatizados (tests)", "tests"),
]
IGNORAR = ("__pycache__", "/arquivados/", "/.venv/", "/node_modules/")

DESC_BASES = {
    "Geral_de_OS_23439885_202609110934.csv": "Extração geral de ordens de serviço de manutenção (SEA/SC), base original",
    "Cruzamento_Patrimonio_Manutencao.csv": "Itens de OS cruzados com o cadastro patrimonial pela placa",
    "RelatorioVeiculosMobiliario-_2_.csv": "Relatório patrimonial de veículos (situação, valores, conservação)",
    "RelatorioVeiculosMobiliario (2).xlsx": "Mesmo relatório patrimonial, formato original Excel",
    "2161_abastecimentos_pg0001.xlsb": "Transações de abastecimento (formato original Excel binário)",
    "abastecimentos_processados.parquet": "Abastecimentos tratados",
    "os_dataset_limpo.csv": "OS após limpeza",
    "os_anomalias_detectadas_detalhado.csv": "OS com escores de anomalia",
    "Memorias_Calculo_por_OS.csv": "Memórias de cálculo por OS",
    "resultados_dissertacao.db": "Banco SQLite de resultados consolidados",
    "sistema_seguro.db": "Banco SQLite do sistema de gestão",
    "trilha_auditoria_ledger.jsonl": "Trilha de auditoria encadeada (ledger)",
}

MECANISMOS = {
    "JWT": r"\bjwt\b",
    "Argon2": r"argon2",
    "bcrypt": r"bcrypt",
    "HMAC": r"\bhmac\b",
    "SHA-256": r"sha-?256",
    "RBAC (papéis)": r"\brbac\b",
    "Limite de requisições": r"rate.?limit",
    "CORS": r"\bcors\b",
    "Chaves de API": r"api[_ ]?key",
    "Ledger / trilha de auditoria": r"ledger|audit_trail|trilha",
}


# ---------------------------------------------------------------- utilidades
def esc(x) -> str:
    return html.escape(str(x))


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def tam(n: int) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{n:,.0f} {u}".replace(",", ".") if u == "B" else f"{n:,.1f} {u}".replace(",", "X").replace(".", ",").replace("X", ".")
        n /= 1024
    return str(n)


def num(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def contar_linhas(p: Path) -> int:
    with open(p, "rb") as f:
        return sum(buf.count(b"\n") for buf in iter(lambda: f.read(1 << 20), b""))


def ler_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def ler_csv(p: Path, sep=";"):
    try:
        with open(p, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f, delimiter=sep))
    except Exception:
        return []


def tabela(cab, linhas, classe="") -> str:
    th = "".join(f"<th>{esc(c)}</th>" for c in cab)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas)
    return f'<table class="{classe}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


# ---------------------------------------------------------------- scripts
def descricao_py(p: Path) -> str:
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
        doc = ast.get_docstring(ast.parse(src))
    except Exception:
        doc, src = None, p.read_text(encoding="utf-8", errors="replace")
    if doc:
        for l in doc.strip().splitlines():
            l = l.strip(" =-#")
            if len(l) > 3:
                return l[:170]
    for l in src.splitlines()[:15]:
        if l.startswith("#") and not l.startswith("#!") and "coding" not in l and len(l) > 4:
            return l.strip("# ")[:170]
    return "—"


def inventariar_scripts():
    vistos, grupos = set(), []
    for titulo, pasta in GRUPOS_SCRIPTS:
        base = ROOT / pasta
        itens = []
        for p in sorted(base.rglob("*.py")) + sorted(base.rglob("*.sh")):
            r = rel(p)
            if any(x in "/" + r for x in IGNORAR) or r in vistos:
                continue
            # subpastas com grupo próprio ficam no grupo próprio
            if pasta == "src" and (r.startswith("src/api/") or r.startswith("src/enterprise/")):
                continue
            vistos.add(r)
            txt = p.read_text(encoding="utf-8", errors="replace")
            desc = descricao_py(p) if p.suffix == ".py" else next(
                (l.strip("# ")[:170] for l in txt.splitlines()[1:12] if l.startswith("#") and len(l) > 4), "—")
            itens.append((r, txt.count("\n") + 1, desc))
        grupos.append((titulo, pasta, itens))
    for extra in ("executar_todos_os_scripts.py", "executar_tudo.sh"):
        p = ROOT / extra
        if p.exists():
            txt = p.read_text(encoding="utf-8", errors="replace")
            d = descricao_py(p) if p.suffix == ".py" else next(
                (l.strip("# ") for l in txt.splitlines()[1:6] if l.startswith("#")), "—")
            grupos[-2][2].append((extra, txt.count("\n") + 1, d))
    return grupos


# ---------------------------------------------------------------- APIs
def inventariar_rotas():
    rotas = []
    pastas = [ROOT / "sistema_gestao_frotas/backend/app", ROOT / "src/api"]
    for pasta in pastas:
        for p in sorted(pasta.rglob("*.py")):
            if "__pycache__" in str(p):
                continue
            s = p.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"APIRouter\([^)]*prefix\s*=\s*[\"']([^\"']+)", s)
            prefixo = m.group(1) if m else ""
            for met, cam in re.findall(r"@(?:router|app)\.(get|post|put|delete|patch)\(\s*[\"']([^\"']*)", s):
                rotas.append((rel(pasta), rel(p), met.upper(), prefixo + cam))
    return rotas


def inventariar_mecanismos():
    achados = defaultdict(set)
    for pasta in ("sistema_gestao_frotas/backend", "src/api", "src/enterprise", "graphdb"):
        for p in (ROOT / pasta).rglob("*.py"):
            if any(x in "/" + rel(p) for x in IGNORAR):
                continue
            s = p.read_text(encoding="utf-8", errors="replace").lower()
            for nome, rx in MECANISMOS.items():
                if re.search(rx, s):
                    achados[nome].add(rel(p))
    return achados


def hosts_externos():
    c = Counter()
    for p in list((ROOT / "scripts").glob("*.py")) + list((ROOT / "scripts").glob("*.sh")):
        for h in re.findall(r"https?://([a-z0-9.-]+\.[a-z]{2,})", p.read_text(encoding="utf-8", errors="replace")):
            c[h] += 1
    return c


# ---------------------------------------------------------------- bases
def inventariar_bases_operacionais():
    linhas = []
    for p in sorted((ROOT / "dados").iterdir()):
        if not p.is_file() or p.name.endswith((".bak",)):
            continue
        n = "—"
        if p.suffix == ".csv":
            n = num(max(contar_linhas(p) - 1, 0))
        elif p.suffix == ".jsonl":
            n = num(contar_linhas(p))
        elif p.suffix == ".parquet":
            try:
                import pyarrow.parquet as pq
                n = num(pq.ParquetFile(p).metadata.num_rows)
            except Exception:
                pass
        linhas.append((esc(p.name), tam(p.stat().st_size), n, esc(DESC_BASES.get(p.name, "Derivada / auxiliar"))))
    proc = []
    try:
        import pyarrow.parquet as pq
        for p in sorted((ROOT / "dissertacao_frotas/dados/processados").glob("*.parquet")):
            md = pq.ParquetFile(p).metadata
            proc.append((esc(p.name), tam(p.stat().st_size), num(md.num_rows), str(md.num_columns)))
    except Exception:
        pass
    backups = list((ROOT / "dados/backups_dr").glob("*.db")) if (ROOT / "dados/backups_dr").exists() else []
    return linhas, proc, backups


def resumo_busca(pasta: Path):
    linhas = ler_csv(pasta / "resultados.csv")
    pdfs = len(list(pasta.glob("*.pdf")))
    abertos = sum(1 for r in linhas if (r.get("acesso_aberto") or "").lower() in ("sim", "true", "1", "yes"))
    return len(linhas), pdfs, abertos


def inventariar_literatura():
    a = ROOT / "artigos"
    buscas = []
    rotulos = [
        ("Busca principal XAI × setor público (OpenAlex + Semantic Scholar)", a),
        ("Busca chinesa (OpenAlex language:zh)", a / "idiomas/zh"),
        ("Busca grafos × XAI × prescritivo × regressão (≥3 de 4 blocos)", a / "busca_grafos_xai_regressao"),
        ("Livros de acesso aberto por tema", a / "livros"),
    ]
    for rot, p in rotulos:
        if (p / "resultados.csv").exists():
            n, pdfs, ab = resumo_busca(p)
            buscas.append((esc(rot), esc(rel(p)), num(n), num(ab), num(pdfs)))
        elif p.exists():
            sub = [d for d in p.iterdir() if d.is_dir()]
            n = sum(resumo_busca(d)[0] for d in sub)
            pdfs = sum(len(list(d.glob("*.pdf"))) for d in sub)
            buscas.append((esc(rot), esc(rel(p)), num(n), "—", num(pdfs)))
        else:
            buscas.append((esc(rot), esc(rel(p)), "não executada", "—", "—"))
    diarias = sorted(d.name for d in (a / "atualizacoes").iterdir() if re.match(r"\d{4}-\d{2}-\d{2}", d.name)) if (a / "atualizacoes").exists() else []
    novos_diarios = sum(len(ler_csv(a / "atualizacoes" / d / "novos.csv")) for d in diarias)
    tc = ROOT / "revisao_sistematica/textos_completos"
    n_pdf = len(list((tc / "PDF").glob("*.pdf"))) if (tc / "PDF").exists() else 0
    n_txt = len(list((tc / "TXT").glob("*.txt"))) if (tc / "TXT").exists() else 0
    tam_tc = sum(f.stat().st_size for f in tc.rglob("*") if f.is_file()) if tc.exists() else 0
    tam_art = sum(f.stat().st_size for f in a.rglob("*.pdf")) if a.exists() else 0
    return buscas, diarias, novos_diarios, n_pdf, n_txt, tam_tc, tam_art


def inventariar_acervo(data_limite_protocolo: str):
    """Acervo da busca contínua (artigos/*.pdf) ligado aos metadados das execuções diárias.
    Grava artigos/acervo_pdfs.csv (um PDF por linha) e devolve os números para o relatório."""
    import csv as _csv
    a = ROOT / "artigos"
    pdfs = sorted(p.name for p in a.glob("*.pdf"))
    dias = sorted(d for d in (a / "atualizacoes").iterdir() if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}$", d.name)) if (a / "atualizacoes").exists() else []
    fontes_csv = [d / "resultados.csv" for d in reversed(dias)] + [a / "resultados.csv"]   # mais recente primeiro
    meta, execucoes = {}, []
    for f in fontes_csv:
        linhas = ler_csv(f)
        for r in linhas:
            if r.get("arquivo_pdf"):
                meta.setdefault(r["arquivo_pdf"], r)
    for d in dias:
        linhas = ler_csv(d / "resultados.csv")
        st = Counter((r.get("status_pdf") or "").split(" (")[0] for r in linhas)
        cons = (d / "consulta.txt").read_text(encoding="utf-8") if (d / "consulta.txt").exists() else ""
        m = re.search(r"Correspondências informadas pelas bases: (\{.*\})", cons)
        execucoes.append((d.name, len(linhas), len(ler_csv(d / "novos.csv")), st.get("baixado", 0), st.get("ja_existia", 0),
                          st.get("falhou", 0), m.group(1) if m else "—"))
    com_meta = [meta[x] for x in pdfs if x in meta]
    ano = Counter(r.get("ano") or "s.d." for r in com_meta)
    veic = Counter((r.get("veiculo") or "").strip() for r in com_meta if (r.get("veiculo") or "").strip())
    fonte = Counter(r.get("fonte") or "—" for r in com_meta)
    sem_ok = sum(1 for r in com_meta if (r.get("verificacao_semantica") or "").startswith("ok"))
    PREPRINT = ("research square", "arxiv", "ssrn", "preprints", "techrxiv", "medrxiv", "biorxiv", "authorea", "osf preprints")
    preprints = sum(1 for r in com_meta if any(k in (r.get("veiculo") or "").lower() for k in PREPRINT)
                    or (r.get("doi") or "").lower().startswith(("10.21203/rs.", "10.48550/arxiv", "10.2139/ssrn", "10.20944/preprints")))
    pos = [r for r in com_meta if (r.get("visto_em") or "") > data_limite_protocolo and r.get("visto_em") != "anterior"]
    ult = ler_csv(dias[-1] / "resultados.csv") if dias else []
    falhas = Counter((r.get("status_pdf") or "")[8:-1] for r in ult if (r.get("status_pdf") or "").startswith("falhou"))
    cat = a / "acervo_pdfs.csv"
    with open(cat, "w", newline="", encoding="utf-8-sig") as f:
        w = _csv.writer(f, delimiter=";")
        w.writerow(["arquivo_pdf", "titulo", "ano", "autores", "veiculo", "doi", "fonte", "verificacao_semantica", "visto_em",
                    "apos_data_limite_prisma", "url_pdf"])
        for x in pdfs:
            r = meta.get(x, {})
            w.writerow([x, r.get("titulo", ""), r.get("ano", ""), r.get("autores", ""), r.get("veiculo", ""), r.get("doi", ""),
                        r.get("fonte", ""), r.get("verificacao_semantica", ""), r.get("visto_em", ""),
                        "sim" if r in pos else ("não" if r else "sem metadados"), r.get("url_pdf", "")])
    return {"n_pdfs": len(pdfs), "n_meta": len(com_meta), "sem_meta": len(pdfs) - len(com_meta), "semantica_ok": sem_ok,
            "anos": sorted(ano.items(), key=lambda kv: kv[0], reverse=True), "veiculos": veic.most_common(10),
            "fontes": fonte.most_common(), "pos_limite": len(pos), "execucoes": execucoes,
            "falhas_ultima": falhas.most_common(6), "n_ultima": len(ult), "catalogo": rel(cat),
            "preprints": preprints, "vistos": len(json.loads((a / "vistos.json").read_text(encoding="utf-8"))) if (a / "vistos.json").exists() else 0}


def inventariar_fipe():
    pasta = ROOT / "FIPE"
    if not pasta.exists():
        return None
    import hashlib
    arquivos = sorted(pasta.glob("*.csv"))
    hashes = {hashlib.md5(p.read_bytes()).hexdigest() for p in arquivos}
    idx = pasta / "fipemaster-indice-historico.csv"
    meses = (contar_linhas(idx) - 2) if idx.exists() else 0
    anos = sorted(re.search(r"(\d{4})", p.name).group(1) for p in arquivos if "segmentos" in p.name and "(" not in p.name)
    return len(arquivos), len(hashes), meses, anos


def estado_timer() -> str:
    try:
        out = subprocess.run(["systemctl", "--user", "is-active", "busca-artigos.timer"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out or "desconhecido"
    except Exception:
        return "não verificado"


def contar_testes():
    total, arquivos = 0, []
    for p in sorted((ROOT / "tests").glob("test_*.py")):
        n = len(re.findall(r"^\s*def test_", p.read_text(encoding="utf-8"), re.M))
        total += n
        arquivos.append((rel(p), n))
    return total, arquivos


# ---------------------------------------------------------------- HTML
CSS = """
@page { size: A4; margin: 2cm 1.8cm 2cm 1.8cm;
  @bottom-right { content: "PBS · " counter(page) " / " counter(pages); font: 8.5pt Arial; color:#555; } }
@page capa { margin: 0; @bottom-right { content: none; } }
body { font-family: Arial, sans-serif; font-size: 10pt; color:#1d1d1d; line-height:1.42; }
.capa { page: capa; height: 297mm; background:#00693e; color:#fff; padding: 30mm 22mm; box-sizing:border-box; }
.capa img { height: 22mm; background:#fff; padding:3mm; border-radius:2mm; }
.capa h1 { font-size: 34pt; margin: 38mm 0 4mm; color:#fff; border:none; page-break-before:auto; }
.capa h2 { color:#fff; }
.capa h2 { font-size: 15pt; font-weight: normal; margin:0 0 30mm; }
.capa p { font-size: 11.5pt; margin: 1.5mm 0; }
h1 { color:#00693e; font-size: 17pt; border-bottom: 2px solid #00693e; padding-bottom:2pt; margin-top: 0; page-break-before: always; }
h1.nb { page-break-before: auto; }
h2 { color:#00693e; font-size: 12.5pt; margin: 14pt 0 5pt; }
h3 { font-size: 10.5pt; margin: 10pt 0 3pt; }
table { width:100%; border-collapse: collapse; margin: 4pt 0 10pt; font-size: 8.3pt; }
th { background:#00693e; color:#fff; text-align:left; padding:3pt 4pt; }
td { border-bottom: 0.5pt solid #c9d6cf; padding: 2.4pt 4pt; vertical-align: top; }
tr:nth-child(even) td { background:#f3f8f5; }
table.scr td:first-child { font-family: 'DejaVu Sans Mono', monospace; font-size: 7.4pt; width: 33%; word-break: break-all; }
table.scr td:nth-child(2) { width: 6%; text-align:right; }
table.rot td:nth-child(3), table.rot td:nth-child(4) { font-family: 'DejaVu Sans Mono', monospace; font-size: 7.4pt; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.4pt; background:#eef3f0; padding:0 2pt; }
.kpi { display:flex; flex-wrap:wrap; gap:6pt; margin: 6pt 0 10pt; }
.kpi div { flex: 1 1 28%; border:1pt solid #00693e; border-radius:3pt; padding:5pt 7pt; }
.kpi b { display:block; font-size:15pt; color:#00693e; }
.nota { background:#fff7e0; border-left: 3pt solid #d99a00; padding: 5pt 8pt; margin: 6pt 0; font-size: 9pt; }
.fluxo { font-family: 'DejaVu Sans Mono', monospace; font-size: 8pt; background:#f3f8f5; padding:8pt; white-space: pre; border-radius:3pt; }
ul { margin: 3pt 0 8pt 14pt; padding:0; } li { margin: 2pt 0; }
"""


def montar_html() -> str:
    grupos = inventariar_scripts()
    rotas = inventariar_rotas()
    mecs = inventariar_mecanismos()
    hosts = hosts_externos()
    bases, proc, backups = inventariar_bases_operacionais()
    buscas, diarias, novos_diarios, n_pdf, n_txt, tam_tc, tam_art = inventariar_literatura()
    fipe = inventariar_fipe()
    prisma = ler_json(ROOT / "revisao_sistematica/resultados_prisma.json") or {}
    acervo = inventariar_acervo(prisma.get("data_limite_protocolo", "9999-12-31"))
    neo = ler_json(ROOT / "dissertacao_frotas/resultados/logs/relatorio_neo4j_grafo.json") or {}
    grafo = ler_json(ROOT / "dissertacao_frotas/resultados/logs/relatorio_teoria_grafos.json") or {}
    n_testes, testes = contar_testes()
    timer = estado_timer()

    n_scripts = sum(len(g[2]) for g in grupos)
    n_linhas = sum(l for g in grupos for _, l, _ in g[2])
    rotas_sis = [r for r in rotas if r[0].startswith("sistema_gestao_frotas")]
    rotas_api = [r for r in rotas if r[0].startswith("src/api")]
    hoje = date.today().strftime("%d/%m/%Y")

    h = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"]

    # capa
    logo = f"<img src='{LOGO.as_uri()}'>" if LOGO.exists() else ""
    h.append(f"""<section class="capa">{logo}
<h1>Relatório PBS</h1>
<h2>Scripts, bases de dados, bases externas baixadas e sistemas próprios de API do projeto de analítica prescritiva para a frota pública de Santa Catarina</h2>
<p><b>Universidade do Estado de Santa Catarina (UDESC)</b></p>
<p>Programa de Pós-Graduação em Computação Aplicada (PPGCAP)</p>
<p>Mestrando: Eduardo Lopes Jonker</p>
<p>Orientadora: Profa. Dra. Vivian Kremer Kalempa</p>
<p>Coorientador: Prof. Dr. Yuri Kaszubowski Lopes</p>
<p style="margin-top:14mm">Gerado automaticamente por <code style="background:none;color:#fff">scripts/gerar_relatorio_pbs.py</code> em {hoje}</p>
</section>""")

    # 1 visão geral
    inc = prisma.get("n_incluidos", "—")
    h.append(f"""<h1>1. Visão geral</h1>
<p>Este relatório documenta o que existe no repositório: os scripts e o que cada um faz, as bases de dados operacionais da SEA/SC, as bases externas consultadas e baixadas (literatura científica, revisão sistemática, índices FIPE) e os sistemas próprios com API. Os números são lidos dos arquivos no momento da geração; as descrições dos scripts vêm das suas próprias docstrings ou do primeiro comentário.</p>
<div class="kpi">
<div><b>{num(n_scripts)}</b>scripts Python/Shell ativos ({num(n_linhas)} linhas)</div>
<div><b>{num(len(rotas))}</b>rotas HTTP em 2 APIs FastAPI</div>
<div><b>{num(n_testes)}</b>testes automatizados</div>
<div><b>{inc}</b>estudos incluídos na revisão PRISMA 2020</div>
<div><b>{num(acervo['n_pdfs'])}</b>PDFs de acesso aberto no acervo da busca contínua ({num(acervo['vistos'])} registros já vistos)</div>
<div><b>{num(n_pdf)}</b>textos completos (PDF) com {num(n_txt)} TXT extraídos</div>
<div><b>{num(neo.get('verified_neo4j_counts', {}).get('vehicle_count', 0))}</b>veículos no grafo Neo4j verificado</div>
</div>
<h2>Fluxo do projeto</h2>
<div class="fluxo">Bases SEA/SC (OS, itens, patrimônio, abastecimento)
   │  dissertacao_frotas/src/01..09  (auditoria → pré-processamento → descritiva → modelos
   │                                  → anomalias → grafos → XAI → MILP → validação)
   ▼
Resultados (logs JSON, tabelas, figuras) ──► Banco SQLite de resultados
   │                                         │
   ├──► Relatórios PDF/HTML, dissertação LaTeX, SIC, MEP
   ├──► Sistema de gestão de frotas (FastAPI, {len(rotas_sis)} rotas)  +  API acadêmica ({len(rotas_api)} rotas)
   └──► Grafo Neo4j local (graphdb/, identificadores pseudonimizados por HMAC)

Literatura: OpenAlex + Semantic Scholar + exportações Scopus/IEEE/CAPES/Paperpile
   └──► scripts/rsl_prisma.py (PRISMA 2020, etapas 01–09)  +  busca diária (systemd)</div>""")

    # 2 bases operacionais
    h.append("<h1>2. Bases de dados operacionais (SEA/SC)</h1>")
    h.append("<p>Arquivos em <code>dados/</code>. Registros: em CSV, linhas físicas menos o cabeçalho (valor aproximado se houver quebras de linha dentro de campos ou linhas de título, como no relatório patrimonial); em Parquet, contagem exata pelos metadados. Formatos Excel não foram abertos para contagem.</p>")
    h.append(tabela(["Arquivo", "Tamanho", "Registros", "Conteúdo"], bases))
    if proc:
        h.append("<h2>Bases processadas do pipeline científico</h2>")
        h.append("<p>Pasta <code>dissertacao_frotas/dados/processados/</code>, gerada pelas etapas 01–02.</p>")
        h.append(tabela(["Arquivo", "Tamanho", "Linhas", "Colunas"], proc))
    if backups:
        tb = sum(b.stat().st_size for b in backups)
        h.append(f"<p>Cópias de segurança (recuperação de desastre) em <code>dados/backups_dr/</code>: {len(backups)} arquivos, {tam(tb)}.</p>")
    h.append('<p class="nota">As bases operacionais contêm dados administrativos do Estado e ficam fora do repositório público (<code>.gitignore</code>: <code>dados/</code>, <code>*.db</code>, <code>*.parquet</code>).</p>')

    # 3 bases externas
    h.append("<h1>3. Bases externas consultadas e baixadas</h1>")
    h.append("<h2>3.1 Buscas de literatura por API</h2>")
    h.append("<p>Todas as buscas usam APIs públicas e baixam somente versões de acesso aberto. Cada pasta guarda <code>resultados.csv</code>, <code>referencias.bib</code>, <code>consulta.txt</code> (a consulta exata) e <code>vistos.json</code> (controle do que já foi visto).</p>")
    h.append(tabela(["Busca", "Pasta", "Registros", "Acesso aberto", "PDFs baixados"], buscas))
    h.append(f"<p>Atualização diária automática: timer <code>busca-artigos.timer</code> (systemd do usuário, 08:00, <code>Persistent=true</code>), estado atual <b>{esc(timer)}</b>. Execuções registradas: {len(diarias)} ({', '.join(diarias) or '—'}), com {num(novos_diarios)} registros inéditos no total. A linha “Busca principal” da tabela acima é a busca inicial; o acervo atualizado está em 3.1.1.</p>")
    A = acervo
    h.append("<h2>3.1.1 Acervo da busca contínua</h2>")
    h.append(f"""<p>A busca principal roda todos os dias às 08:00 com a consulta de três grupos (método analítico × XAI × setor público), limite de 10.000 registros por base e chave de API do OpenAlex. Os PDFs ficam em <code>artigos/</code>; o catálogo <code>{esc(A['catalogo'])}</code> liga cada arquivo ao seu registro (título, ano, DOI, veículo, link de onde foi baixado).</p>
<div class="kpi"><div><b>{num(A['n_pdfs'])}</b>PDFs no acervo</div><div><b>{num(A['semantica_ok'])}</b>com os 3 grupos confirmados no título ou resumo</div>
<div><b>{num(A['pos_limite'])}</b>vistos depois da data-limite do protocolo PRISMA</div></div>
<p class="nota"><b>Qualidade das fontes.</b> A busca confere os termos, não a qualidade do veículo. {num(A['preprints'])} PDFs vêm de servidores de preprint (Research Square, arXiv, SSRN, Preprints.org e similares), sem revisão por pares, e vários veículos da lista abaixo são revistas multidisciplinares cuja revisão por pares e indexação não foram verificadas. Antes de citar um texto do acervo, confira o veículo; na revisão sistemática, esse filtro é o critério CO4.</p>""")
    h.append(tabela(["Execução", "Registros", "Inéditos", "PDFs baixados", "Já existiam", "Falharam", "Correspondências nas bases"],
                    [(esc(d), num(n), num(nv), num(b), num(j), num(fl), esc(c)) for d, n, nv, b, j, fl, c in A["execucoes"]]))
    h.append("<h3>PDFs por ano de publicação</h3>")
    h.append(tabela(["Ano", "PDFs"], [(esc(k), num(v)) for k, v in A["anos"]]))
    h.append("<h3>Veículos com mais PDFs no acervo</h3>")
    h.append(tabela(["Veículo", "PDFs"], [(esc(k), num(v)) for k, v in A["veiculos"]]))
    if A["falhas_ultima"]:
        h.append(f"<p>Na última execução ({num(A['n_ultima'])} registros), os downloads que falharam tiveram estes motivos: "
                 + "; ".join(f"{esc(k)} ({v})" for k, v in A["falhas_ultima"])
                 + ". Sites que exigem login ou bloqueiam download automático (HTTP 403) não são contornados.</p>")
    h.append(f"""<p class="nota"><b>Relação com a revisão sistemática.</b> O acervo da busca contínua não entra automaticamente na revisão PRISMA, cuja data-limite é {esc(prisma.get('data_limite_protocolo', '—'))}. Os {num(A['pos_limite'])} PDFs vistos depois dessa data são candidatos a uma atualização da revisão: para entrarem, precisam passar pelas mesmas etapas (critérios objetivos, triagem, elegibilidade e qualidade) e ser registrados em <code>revisao_sistematica/registro_incorporacoes.csv</code>, com a nova data de busca declarada no fluxograma.{f" {A['sem_meta']} PDF(s) não casam com os metadados das execuções guardadas e aparecem como “sem metadados” no catálogo." if A['sem_meta'] else ""}</p>""")
    h.append(f"<p>Volume em disco: {tam(tam_art)} de PDFs em <code>artigos/</code> e {tam(tam_tc)} em <code>revisao_sistematica/textos_completos/</code>. Esses textos são de terceiros e ficam fora do repositório público.</p>")

    if prisma:
        h.append("<h2>3.2 Revisão sistemática PRISMA 2020</h2>")
        agg = defaultdict(lambda: [0, ""])
        for i in prisma.get("inventario", []):
            k = (i["fonte"], i["grupo"])
            agg[k][0] += int(i.get("registros") or 0)
            agg[k][1] = i.get("formato_exportacao") or Path(i.get("arquivo", "")).suffix.lstrip(".").upper()
        h.append(tabela(["Fonte", "Grupo PRISMA", "Registros", "Formato"],
                        [(esc(f), "base de dados" if g == "bases" else "outros métodos", num(n), esc(fm or "—")) for (f, g), (n, fm) in agg.items()]))
        u = prisma.get("unicos", {}); inc_d = prisma.get("incluidos", {})
        sb = prisma.get("snowball_identificados", {})
        h.append(f"""<p>Fluxo: {num(sum(prisma.get('identificados', {}).values()))} registros identificados;
{num(u.get('bases', 0))} únicos em bases e {num(u.get('outros', 0))} em outros métodos;
{num(prisma.get('textos_buscados', 0))} textos completos buscados;
snowballing com {num(sum(sb.values()))} referências ({num(sb.get('Snowballing regressivo', 0))} regressivas, {num(sb.get('Snowballing progressivo', 0))} progressivas);
<b>{inc} estudos incluídos</b> ({inc_d.get('bases', 0)} de bases, {inc_d.get('outros', 0)} de outros métodos, {inc_d.get('snowballing', 0)} por snowballing).
Data-limite do protocolo: {esc(prisma.get('data_limite_protocolo', '—'))}. Limite configurado: {num(prisma.get('max_textos', 0))} textos.</p>""")

    if fipe:
        n_arq, n_uni, meses, anos = fipe
        h.append("<h2>3.3 Índices FIPE (FipeMaster Open Data, CC-BY 4.0)</h2>")
        h.append(f"<p>Pasta <code>FIPE/</code>: {n_arq} arquivos, dos quais {n_uni} têm conteúdo distinto (os demais são cópias). Índice histórico mensal com {meses} meses (preço médio, mediana e número de versões) e variação anual por combustível para {', '.join(anos)}. Os arquivos não têm marca, modelo nem código FIPE, então servem para correção agregada de valores, não para o valor de mercado de cada veículo.</p>")

    h.append("<h2>3.4 Serviços externos usados pelos scripts</h2>")
    h.append(tabela(["Domínio", "Ocorrências no código (scripts/)"],
                    [(esc(k), str(v)) for k, v in hosts.most_common() if not k.endswith(("w3.org", "github.com"))]))
    h.append("""<ul>
<li><b>Usados:</b> OpenAlex (busca, metadados, citações para snowballing, filtro de livros) e Semantic Scholar (busca complementar).</li>
<li><b>Consultados e documentados, sem automação:</b> Google Scholar, CAPES/CAFe, CNKI, Wanfang e CQVIP, por falta de API pública ou por termos de uso; o roteiro manual está em <code>Metodologia de Pesquisa/exportacoes_capes/LEIA-ME_roteiro_de_busca.md</code>.</li>
<li><b>Testados e indisponíveis:</b> as APIs do DOAB e do OAPEN recusam o endereço IP (lista de permissão); a API de busca do Mercado Livre respondeu 403.</li>
<li><b>Em avaliação:</b> a API de dados abertos de compras públicas (<code>dadosabertos.compras.gov.br</code>, módulos de catálogo CATMAT e de pesquisa de preços), para comparar preços de peças com os custos da SEA/SC. O catálogo responde; a consulta de preços ainda não retornou registros nos testes.</li>
</ul>""")

    # 4 scripts
    h.append("<h1>4. Scripts</h1>")
    h.append("<p>Pastas <code>arquivados/</code>, ambientes virtuais e caches foram excluídos. A coluna “Linhas” conta linhas de código-fonte.</p>")
    for i, (titulo, pasta, itens) in enumerate(grupos):
        if not itens:
            continue
        h.append(f"<h2>4.{i + 1} {esc(titulo)} — {len(itens)} arquivos</h2>")
        h.append(tabela(["Arquivo", "Linhas", "Função (docstring)"],
                        [(esc(r), num(l), esc(d)) for r, l, d in itens], "scr"))

    # 5 sistemas próprios
    h.append("<h1>5. Sistemas próprios com API</h1>")
    por_arq = Counter(r[1] for r in rotas_sis)
    h.append(f"""<h2>5.1 Sistema de gestão de frotas</h2>
<p><code>sistema_gestao_frotas/</code>: backend FastAPI com {len(rotas_sis)} rotas distribuídas em {len(por_arq)} módulos (autenticação, ativos, telemetria, manutenção, combustível, viagens, conformidade, relatórios, IA e contratos SC), serviços em <code>backend/app/services/</code>, camada de segurança em <code>backend/app/security/</code>, frontend próprio e scripts de execução para Linux e Windows.</p>""")
    h.append(tabela(["Módulo de rotas", "Rotas"], [(esc(Path(k).name), str(v)) for k, v in sorted(por_arq.items())]))
    h.append(f"<h2>5.2 API acadêmica</h2><p><code>src/api/</code>: FastAPI com {len(rotas_api)} rotas (autenticação e assistente), configuração, middlewares, modelos e esquemas próprios.</p>")
    ent = sorted(p.stem for p in (ROOT / "src/enterprise").glob("*.py") if p.stem != "__init__")
    h.append(f"<h2>5.3 Plataforma enterprise</h2><p><code>src/enterprise/</code>: {len(ent)} módulos — {', '.join(f'<code>{e}</code>' for e in ent)}.</p>")
    h.append("<h2>5.4 Mecanismos de segurança presentes no código</h2>")
    h.append("<p>Busca textual nos módulos dos sistemas. Indica que o mecanismo aparece no código; não substitui uma auditoria de segurança.</p>")
    h.append(tabela(["Mecanismo", "Arquivos", "Onde"],
                    [(esc(k), str(len(v)), esc(", ".join(sorted("/".join(Path(x).parts[-2:]) for x in v))[:220])) for k, v in mecs.items()]))
    vc = neo.get("verified_neo4j_counts", {})
    if vc:
        tr = grafo.get("topologia_rede", {})
        h.append(f"""<h2>5.5 Grafo Neo4j local</h2>
<p><code>graphdb/</code>: Neo4j 5.26 em Docker, ligado somente a 127.0.0.1. Carga verificada em {esc(neo.get('generated_at_utc', '')[:10])}: {num(vc.get('vehicle_count', 0))} veículos, {num(vc.get('workshop_count', 0))} oficinas, {num(vc.get('service_edge_count', 0))} relações veículo–oficina e {num(vc.get('shared_workshop_edge_count', 0))} relações entre {num(vc.get('projected_workshop_count', 0))} oficinas que atendem pelo menos dois veículos em comum. Identificadores são pseudonimizados com HMAC-SHA-256 e segredo local; placas, nomes, CPF/CNPJ e textos livres não são gravados. A impressão digital SHA-256 da fonte fica no relatório de carga.</p>
<p>A projeção oficina–oficina tem o mesmo tamanho da rede analisada na etapa 06 do pipeline ({num(tr.get('nos_oficinas', 0))} nós, {num(tr.get('arestas', 0))} arestas, modularidade de Louvain Q = {tr.get('modularidade_louvain_q', '—')}, {tr.get('total_comunidades', '—')} comunidades). O protótipo Neo4j persiste o grafo; ele não reexecutou o algoritmo de Louvain.</p>""")
        h.append(tabela(["Teste", "Funções de teste"], [(esc(a), str(n)) for a, n in testes]))

    # 5.6 análise do grafo
    ag = ler_json(ROOT / "dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json")
    if ag:
        T, A = ag["testes"], ag["analises"]
        a1, a2, a3 = A["A1_estabilidade_louvain"], A["A2_modelo_nulo"], A["A3_concentracao"]
        sp = A["A4_centralidade_vs_auditoria"]["spearman"]
        kw = A["A4_centralidade_vs_auditoria"]["kruskal_glosa_entre_comunidades"]
        def br(x, nd=3):
            return f"{x:.{nd}f}".replace(".", ",")
        h.append(f"""<h2>5.6 Teste e análise do grafo</h2>
<p><code>scripts/analise_grafos_frotas.py</code> lê o grafo do Neo4j e executa três testes e cinco análises (execução de {esc(ag['gerado_em_utc'][:10])}, {ag['duracao_s']} s).</p>""")
        h.append(tabela(["Teste", "Resultado"], [
            ["T1 – contagens do Neo4j iguais às do relatório de carga", "aprovado" if T["T1_integridade"]["aprovado"] else "<b>reprovado</b>"],
            [f"T2 – projeção recalculada igual à gravada ({num(T['T2_projecao']['arestas_gravadas'])} arestas, {T['T2_projecao']['pesos_divergentes']} pesos divergentes)", "aprovado" if T["T2_projecao"]["aprovado"] else "<b>reprovado</b>"],
            [f"T3 – Louvain reproduz a etapa 06 (Q {br(T['T3_reproducao_etapa06']['neo4j']['modularidade_louvain_q'], 4)} × {br(T['T3_reproducao_etapa06']['etapa06']['modularidade_louvain_q'], 4)})", "aprovado" if T["T3_reproducao_etapa06"]["aprovado"] else "<b>reprovado</b>"],
        ]))
        h.append(tabela(["Análise", "Resultado"], [
            ["A1 – estabilidade (30 sementes)", f"Q = {br(a1['Q_media'], 4)} ± {br(a1['Q_dp'], 4)}; {a1['comunidades_min']}–{a1['comunidades_max']} comunidades; ARI médio {br(a1['ARI_vs_seed42_media'])}"],
            ["A2 – modelo nulo (30 redes, graus preservados)", f"Q nulo = {br(a2['Q_nulo_media'])} ± {br(a2['Q_nulo_dp'])}; z = {br(a2['z'], 1)}; p {esc(a2['p_empirico'].replace('.', ','))}"],
            ["A3 – concentração do gasto", f"10% das oficinas = {br(100 * a3['participacao_top10pct_oficinas'], 1)}% do gasto; Gini {br(a3['gini_gasto'], 2)}; HHI {br(a3['hhi'], 0)}"],
            ["A4 – centralidade × fiscalização", f"anomalia ρ = {br(sp['intermediacao~taxa_anomalia']['rho'])}; proporção glosada ρ = {br(sp['intermediacao~glosa_sobre_orcado']['rho'])}; frequência de glosa ρ = {br(sp['intermediacao~taxa_glosa']['rho'])} (p = {br(sp['intermediacao~taxa_glosa']['p'], 2)}); Kruskal–Wallis entre comunidades p = {br(kw['p'], 2)}"],
            ["A5 – oficinas por veículo × custo por registro", f"ρ = {br(A['A5_dispersao_veiculo']['spearman_oficinas_custo_por_registro']['rho'])}"],
        ]))

    # 5.7 artefatos novos
    ARTEFATOS = [
        ("Artigo SBC – grafos na gestão de frotas", "SBC/artigo5_grafos_gestao_frotas_sbc.pdf", "scripts/gerar_artigo_grafos.py"),
        ("Artigo SBC – fonte LaTeX (Overleaf)", "SBC/artigo5_grafos_gestao_frotas_sbc.tex", "scripts/gerar_artigo_grafos.py"),
        ("Seção 10.x da dissertação (teste do grafo)", "overleaf_dissertacao_udesc/Textuais/Secao10_TesteGrafos.tex", "scripts/gerar_artigo_grafos.py"),
        ("Relatório JSON da análise do grafo", "dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json", "scripts/analise_grafos_frotas.py"),
        ("Figura: modelo nulo e concentração", "dissertacao_frotas/resultados/figuras/grafos_modelo_nulo_e_concentracao.png", "scripts/analise_grafos_frotas.py"),
        ("Figura: centralidade × glosa", "dissertacao_frotas/resultados/figuras/grafos_centralidade_vs_glosa.png", "scripts/analise_grafos_frotas.py"),
        ("Protocolo da PBS e registro de incorporações", "revisao_sistematica/protocolo_sigma.pdf", "scripts/gerar_protocolo_e_relatorio_rsl.py"),
        ("Relatório da revisão sistemática (PRISMA 2020)", "revisao_sistematica/relatorio_revisao_sistematica.pdf", "scripts/gerar_protocolo_e_relatorio_rsl.py"),
        ("Registro de incorporações (somente acréscimos)", "revisao_sistematica/registro_incorporacoes.csv", "scripts/gerar_protocolo_e_relatorio_rsl.py"),
        ("Apresentação SIC", "SIC/SIC_final.pptx", "scripts/gerar_apresentacao_sic.py"),
        ("MEP", "mep.pdf", "scripts/gerar_mep_pdf.py"),
        ("Certificado de reprodutibilidade (H1–H4)", "dissertacao_frotas/resultados/logs/certificado_reprodutibilidade_cientifica.json", "dissertacao_frotas/src/09_validacao_estatistica.py"),
        ("Executor de atualização sem supervisão", "scripts/atualizacao_noturna.sh", "—"),
    ]
    linhas_art = []
    for nome, caminho, gerador in ARTEFATOS:
        p = ROOT / caminho
        if p.exists():
            from datetime import datetime as _dt
            linhas_art.append((esc(nome), f"<code>{esc(caminho)}</code>", tam(p.stat().st_size),
                               _dt.fromtimestamp(p.stat().st_mtime).strftime("%d/%m/%Y %H:%M"), f"<code>{esc(gerador)}</code>"))
        else:
            linhas_art.append((esc(nome), f"<code>{esc(caminho)}</code>", "—", "<b>não encontrado</b>", f"<code>{esc(gerador)}</code>"))
    h.append("<h2>5.7 Artefatos gerados nesta etapa</h2>")
    h.append(tabela(["Artefato", "Arquivo", "Tamanho", "Atualizado em", "Gerador"], linhas_art, "scr"))
    reg = ler_csv(ROOT / "revisao_sistematica/registro_incorporacoes.csv")
    if reg:
        c = Counter(r["tipo"] for r in reg)
        h.append(f"<p>Registro de incorporações da revisão: {num(len(reg))} entradas — "
                 + "; ".join(f"{esc(k)}: {num(v)}" for k, v in c.most_common()) + ".</p>")
    noite = sorted((ROOT / "logs_atualizacao_noturna").glob("2*/RESUMO.md")) if (ROOT / "logs_atualizacao_noturna").exists() else []
    if noite:
        txt = noite[-1].read_text(encoding="utf-8")
        ok = txt.count("| ok |"); falhas = len(re.findall(r"\| \*\*(falhou|tempo esgotado)", txt))
        tot = re.search(r"Total de campos alterados: (\d+)", txt)
        h.append(f"<p>Última atualização sem supervisão (<code>{esc(str(noite[-1].relative_to(ROOT)))}</code>): {ok} etapas concluídas, "
                 f"{falhas} com falha; {tot.group(1) if tot else '—'} campos de métricas diferentes do backup anterior.</p>")

    # 6 diferenciais
    h.append(f"""<h1>6. Diferenciais da execução</h1>
<ul>
<li><b>Sistema próprio, não apenas modelos.</b> Os resultados do pipeline alimentam {len(rotas)} rotas HTTP em dois backends FastAPI, com frontend, trilha de auditoria e módulos de conformidade e contratos de SC. A pesquisa entrega um sistema que pode ser executado, além dos relatórios.</li>
<li><b>Coleta de literatura reprodutível e versionada.</b> Cada busca grava a consulta exata, a data, o resultado bruto e o BibTeX. O controle por <code>vistos.json</code> separa o que é novo a cada execução, e a busca diária roda sozinha pelo systemd com trava de concorrência (<code>flock</code>).</li>
<li><b>Revisão PRISMA executável.</b> <code>scripts/rsl_prisma.py</code> lê exportações em RIS, CSV, BibTeX e EndNote, remove duplicatas por DOI e título, aplica os critérios do protocolo, faz o snowballing pela API do OpenAlex e produz o diagrama e as tabelas de cada etapa. O inventário registra o MD5 de cada arquivo de entrada.</li>
<li><b>Controle semântico das buscas.</b> A busca literal é o padrão porque a radicalização trocava <i>accountability</i> por <i>accounting</i> e <i>government</i> por <i>governance</i>. Antes de baixar um PDF, uma verificação local confirma que os três blocos da consulta aparecem no registro.</li>
<li><b>Privacidade por construção no grafo.</b> O Neo4j recebe apenas identificadores HMAC, roda em endereço local e confere as contagens após a carga.</li>
<li><b>Limites legais respeitados.</b> Somente acesso aberto; sem raspagem de Google Scholar, CAPES/CAFe ou CNKI, e sem bibliotecas-sombra. Onde não há API, o projeto documenta um roteiro manual em vez de automatizar.</li>
<li><b>Relatórios gerados por código.</b> MEP, apresentação do SIC, figuras e este relatório saem de scripts, então podem ser regenerados quando os dados mudam.</li>
</ul>""")

    # 7 limitações
    h.append("""<h1>7. Limitações e pendências verificadas</h1>
<p>Pontos encontrados durante a preparação deste relatório. Eles precisam ser resolvidos ou declarados antes da defesa.</p>
<ul>
<li><b>Corrigido – contagem de veículos antieconômicos.</b> <code>src/indicadores_gfi.py</code> fixava o resultado entre 313 e 427 (<code>min(427, max(qtd, 313))</code>). A trava foi removida; a contagem calculada é de 242 veículos.</li>
<li><b>Valor venal estimado por categoria.</b> <code>scripts/criar_tabela_veiculos_consolidada.py</code>, linhas 166–172: a coluna <code>valor_venal_fipe</code> recebe R$ 55 mil, 280 mil, 95 mil ou 28 mil conforme a categoria. Esses valores não vêm da Tabela FIPE.</li>
<li><b>Critério de 40% diferente do decreto.</b> O Decreto MG nº 47.539, de 23/11/2018 (art. 44), considera as manutenções dos últimos 12 meses e o valor de mercado usado no IPVA. O cálculo do projeto soma todo o período e usa valor contábil ou estimado. A data (23/11/2018) e o artigo foram conferidos no site da ALMG. O <code>referencias.bib</code> já foi corrigido (data e ementa); o texto e os geradores ainda citam o art. 5º.</li>
<li><b>Senha de teste no repositório público.</b> A senha usada pelos dados de exemplo e pelos testes do sistema de gestão aparece em texto claro em 8 arquivos (por exemplo <code>sistema_gestao_frotas/backend/app/seed_data.py</code> e <code>frontend/js/api.js</code>) e no histórico do GitHub. Se ela for ou já tiver sido usada em algum sistema real, precisa ser trocada; no código, deve vir de variável de ambiente.</li>
<li><b>Métricas digitadas no banco de resultados.</b> <code>scripts/criar_banco_dados_resultados.py</code>, linhas 199 e 216: as métricas de regressão e de séries temporais são inseridas como constantes (por exemplo, MAE de R$ 895,40), enquanto a tabela oficial registra MAE de R$ 2.223,84 para o modelo multimodal.</li>
<li><b>Outros indicadores constantes.</b> <code>src/indicadores_gfi.py</code>: confiabilidade de quilometragem de 84,6% (linha 152) e indicadores IND-05 e IND-06 (linhas 166–167) estão fixos no código.</li>
<li><b>Revisão sistemática.</b> A triagem é assistida por regras e precisa da validação do autor (<code>revisao_sistematica/dados/09_validacao_avaliador.csv</code>); as consultas exatas de Scopus e IEEE não foram arquivadas; a ACM Digital Library não foi exportada.</li>
<li><b>Legislação de SC não localizada em fonte oficial.</b> Decretos estaduais nº 1.488/2008 e nº 2.056/2009 e a IN SEA nº 05/2024. Os textos da qualificação passaram a citar o Decreto SC nº 311/2011 (Sistema GVE), alterado pelo Decreto nº 577/2016.</li>
<li><b>Corrigido – MILP lido de arquivo antigo.</b> A etapa 08 gravava o resultado em <code>results/solver_logs/</code>, e a etapa 09 lia <code>resultados/logs/</code>, onde havia uma versão de 22/10/2026 (R$ 10,75 mi; 12,82%). A etapa 08 passou a gravar nos dois locais, e o certificado voltou a registrar R$ 6,99 mi (13,66%), coerente com os textos.</li>
<li><b>Corrigido – gerador do SIC.</b> <code>scripts/gerar_apresentacao_sic.py</code> tinha um comando <code>pip install</code> colado na primeira linha, inclusive na versão publicada no GitHub, e não executava.</li>
<li><b>Corrigido – relatório de XAI.</b> O campo <code>conclusao_auditoria</code> dizia que H4 foi sustentada enquanto <code>hipotese_h4_sustentada</code> era falso. Com LIME real e limiar de 0,85, os dois campos indicam H4 não sustentada.</li>
<li><b>Corrigido – custos do MILP.</b> A etapa 08 substituía o resultado do solver por constantes. Agora os custos do MILP, da relaxação LP, da linha de base BL0 e da heurística gulosa vêm do solver (economia de 13,66% sobre BL0; R$ 764,29 sobre a heurística).</li>
<li><b>Etapas 04b, 04c e 07b fora do orquestrador.</b> A etapa 09 lê os JSON dessas três etapas, mas <code>executar_todos_os_scripts.py</code> não as executava. Foram incluídas antes da etapa 09.</li>
<li><b>Homologação Linux × Windows.</b> Os números mudaram depois das correções; a homologação precisa ser refeita.</li>
</ul>""")
    h.append("</body></html>")
    return "\n".join(h)


def main():
    html_txt = montar_html()
    weasyprint.HTML(string=html_txt, base_url=str(ROOT)).write_pdf(SAIDA)
    print(f"OK: {SAIDA} ({SAIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

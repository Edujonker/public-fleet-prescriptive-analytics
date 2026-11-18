# -*- coding: utf-8 -*-
"""
Biblio-now · servidor web local (FastAPI). Autor: Eduardo Lopes Jonker.

  python -m biblionow.app [--porta 8765] [--sem-navegador]

Só aceita conexões do próprio computador (127.0.0.1) e abre a interface por um link com token de sessão.
Cada PESQUISA tem o próprio repositório em repositorio/pesquisas/<nome>/ (pdf, txt, bib, buscas, protocolo,
relatorios, rastreabilidade, fichamento.xlsx), para que temas diferentes nunca se misturem.
Uma busca roda por vez, em segundo plano no servidor: trocar de aba ou fechar o navegador não interrompe o download.
Chaves de API ficam no cofre criptografado (seguranca.py).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import queue
import re
import shutil
import sys
import threading
import unicodedata
import webbrowser
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import fichamento
from . import seguranca as seg
from . import validacao
from .agendador import DIAS_SEMANA, Agendador
from .nucleo import Execucao, Parametros, Repositorio, executar, nome_pesquisa

VERSAO = fichamento.VERSAO
AUTOR = fichamento.AUTOR
RAIZ = Path(__file__).resolve().parent.parent
REPO = Path(os.environ.get("BIBLIONOW_REPOSITORIO") or (RAIZ / "repositorio")).resolve()
PESQUISAS = REPO / "pesquisas"
ESTATICO = Path(__file__).resolve().parent / "static"
ENV = RAIZ / ".env"
VARS = ("OPENALEX_API_KEY", "OPENALEX_EMAIL", "UNPAYWALL_EMAIL", "S2_API_KEY")


# ---------------------------------------------------------------- configuração
cofre = seg.Cofre(RAIZ)
CHAVES_IMPORTADAS = cofre.importar_env(ENV)          # chaves em texto no .env vão para o cofre


def ler_chaves() -> dict:
    d = cofre.ler()
    return {k: os.environ.get(k) or d.get(k, "") for k in VARS}


CHAVES = ler_chaves()
sessao = seg.Sessao()
PORTA = 8765


# ---------------------------------------------------------------- pesquisas (um repositório cada)
repositorios: dict[str, Repositorio] = {}
trava_pesq = threading.RLock()


def _info_pesquisa(pasta: Path) -> dict:
    f = pasta / "pesquisa.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"nome": pasta.name}


def abrir_pesquisa(nome: str, criar=False, descricao="") -> Repositorio:
    n = nome_pesquisa(nome)
    with trava_pesq:
        if n in repositorios:
            return repositorios[n]
        pasta = PESQUISAS / n
        if not pasta.exists() and not criar:
            raise HTTPException(404, f"pesquisa não encontrada: {n}")
        pasta.mkdir(parents=True, exist_ok=True)
        if not (pasta / "pesquisa.json").exists():
            (pasta / "pesquisa.json").write_text(json.dumps(
                {"nome": n, "descricao": descricao[:500], "criada_em": datetime.now().astimezone().isoformat(timespec="seconds"),
                 "criada_por": f"Biblio-now {VERSAO}"}, ensure_ascii=False, indent=2), encoding="utf-8")
        repositorios[n] = Repositorio(pasta)
        return repositorios[n]


def _rastreio_reconstruido(repo: Repositorio):
    """Obras baixadas antes da versão com rastreabilidade: ficha montada com o que foi registrado na época,
    marcada como reconstruída. Os campos que não foram registrados ficam vazios (nada é inventado)."""
    for oid, ob in repo.obras.items():
        f = repo.rastreio / f"{oid}.json"
        if f.exists():
            continue
        pdf = repo.raiz / (ob.get("pdf") or f"pdf/{oid}.pdf")
        ficha = {"arquivo": ob.get("pdf"), "pesquisa": repo.nome, "reconstruida": True,
                 "nota": ("Obra baixada antes da versão do Biblio-now que registra a rastreabilidade completa. "
                          "Data e hora de incorporação, busca e URL do PDF vêm de obras.json; cabeçalhos HTTP, redirecionamentos "
                          "e tentativas não foram registrados na época e ficam vazios."),
                 "busca": {"id": ob.get("busca_origem"), "nome": ob.get("busca_origem_nome")},
                 "registro_bibliografico": {k: ob.get(k) for k in ("titulo", "autores", "ano", "veiculo", "doi", "url", "fonte")},
                 "download": {"url_final": ob.get("url_pdf", ""), "fim_download": "", "incorporada_em": ob.get("incorporada_em")},
                 "integridade": {"sha256": seg.sha256_arquivo(pdf) if pdf.exists() else "", "md5": repo._md5(pdf) if pdf.exists() else "",
                                 "bytes_em_disco": pdf.stat().st_size if pdf.exists() else 0},
                 "reconstruida_em": datetime.now().astimezone().isoformat(timespec="seconds")}
        f.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
        ob.setdefault("rastreabilidade", f"rastreabilidade/{oid}.json")
        ob.setdefault("pesquisa", repo.nome)
        ob.setdefault("md5_pdf", ficha["integridade"]["md5"])
        ob.setdefault("url_pdf_final", ob.get("url_pdf", ""))
    repo.gravar()


def migrar_repositorio_antigo():
    """Versões anteriores guardavam tudo em repositorio/ (uma pasta só). Move para pesquisas/<nome>/,
    com o nome tirado da primeira busca. Só move (não apaga) e registra a migração."""
    itens = ["pdf", "txt", "bib", "buscas", "protocolo", "relatorios", "obras.json", "controle_downloads.json",
             "indice_conteudo.json", "fichamento.xlsx", "agendamentos_antigos.json"]
    if not any((REPO / i).exists() for i in ("obras.json", "pdf", "buscas")) or PESQUISAS.exists() and any(PESQUISAS.iterdir()):
        return None
    nome = "Geral"
    buscas = sorted((REPO / "buscas").glob("*/parametros.json")) if (REPO / "buscas").exists() else []
    if buscas:
        pr = json.loads(buscas[0].read_text(encoding="utf-8"))
        nome = pr.get("rotulo") or " ".join(pr.get("blocos", [["Geral"]])[0]) or "Geral"
    destino = PESQUISAS / nome_pesquisa(nome.capitalize() if nome.islower() else nome)
    destino.mkdir(parents=True, exist_ok=True)
    movidos = []
    for i in itens:
        if (REPO / i).exists() and not (destino / i).exists():
            shutil.move(str(REPO / i), str(destino / i))
            movidos.append(i)
    for b in (destino / "buscas").glob("*/parametros.json"):
        pr = json.loads(b.read_text(encoding="utf-8"))
        if not pr.get("pesquisa"):
            pr["pesquisa"] = destino.name
            b.write_text(json.dumps(pr, ensure_ascii=False, indent=2), encoding="utf-8")
    (destino / "MIGRACAO.txt").write_text(
        f"Em {datetime.now():%d/%m/%Y %H:%M} o Biblio-now {VERSAO} moveu o repositório único para esta pasta de pesquisa.\n"
        f"Itens movidos (sem alteração de conteúdo): {', '.join(movidos)}\n", encoding="utf-8")
    return destino.name


def carregar_pesquisas():
    PESQUISAS.mkdir(parents=True, exist_ok=True)
    for d in sorted(PESQUISAS.iterdir()):
        if d.is_dir():
            repo = abrir_pesquisa(d.name, criar=True)
            _rastreio_reconstruido(repo)


# ---------------------------------------------------------------- buscas
execucoes: dict[str, Execucao] = {}
fila: "queue.Queue[str]" = queue.Queue()
trava_fich = threading.Lock()


def slug(t: str, n=40) -> str:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")[:n].lower() or "busca"


def repo_de(ex: Execucao) -> Repositorio:
    return abrir_pesquisa(ex.params.pesquisa, criar=True)


def resumo(ex: Execucao) -> dict:
    return ex.resumo() | {"pesquisa": ex.params.pesquisa}


def resumos_buscas(pesquisa: str | None = None):
    return sorted((resumo(e) for e in execucoes.values() if pesquisa is None or e.params.pesquisa == pesquisa), key=lambda r: r["id"])


def apos_execucao(ex: Execucao):
    repo = repo_de(ex)
    with trava_fich:
        fichamento.atualizar_tudo(repo.raiz, repo.obras, resumos_buscas(repo.nome), ex.resumo())
    ex.escrever("Planilha de fichamento e Protocolo Sigma atualizados.")


def trabalhador():
    while True:
        id_ = fila.get()
        ex = execucoes.get(id_)
        if ex and not ex.cancelar.is_set():
            executar(ex, repo_de(ex), CHAVES, apos_execucao)
        elif ex:
            ex.estado = "cancelada"
        fila.task_done()


def nova_execucao(params: Parametros, origem="manual") -> Execucao:
    params.validar()
    repo = abrir_pesquisa(params.pesquisa, criar=True)
    id_ = f"{datetime.now():%Y%m%d_%H%M%S}_{slug(params.rotulo or ' '.join(params.blocos[0]))}"
    while id_ in execucoes:
        id_ += "_"
    pasta = repo.raiz / "buscas" / id_
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "parametros.json").write_text(json.dumps(params.como_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    ex = Execucao(id=id_, params=params, pasta=pasta, origem=origem)
    execucoes[id_] = ex
    fila.put(id_)
    return ex


def disparar_agendamento(ag: dict) -> str:
    p = Parametros(**{k: v for k, v in ag["busca"].items() if k in Parametros.__dataclass_fields__})
    p.rotulo = p.rotulo or ag["nome"]
    return nova_execucao(p, origem=f"agendamento: {ag['nome']}").id


agendador = Agendador(REPO / "agendamentos.json", disparar_agendamento)


def carregar_anteriores():
    for repo in list(repositorios.values()):
        for d in sorted((repo.raiz / "buscas").iterdir()):
            f = d / "resumo.json"
            if not d.is_dir() or d.name in execucoes or not (f.exists() or (d / "parametros.json").exists()):
                continue
            if f.exists():
                r = json.loads(f.read_text(encoding="utf-8"))
            else:                                       # servidor encerrado no meio da busca: reconstrói pelo acervo
                r = {"parametros": json.loads((d / "parametros.json").read_text(encoding="utf-8")), "estado": "interrompida",
                     "baixados": sum(o.get("busca_origem") == d.name for o in repo.obras.values()),
                     "ja_existiam": sum(d.name in (o.get("buscas") or []) and o.get("busca_origem") != d.name for o in repo.obras.values()),
                     "erro": "o Biblio-now foi encerrado durante a busca; use Retomar para continuar"}
            pr = r.get("parametros") or {"blocos": r.get("blocos") or [["?"]], "minimo_blocos": r.get("minimo_blocos"), "rotulo": r.get("rotulo", "")}
            pr["pesquisa"] = repo.nome                  # a pasta manda: a busca pertence à pesquisa onde está guardada
            p = Parametros(**{k: v for k, v in pr.items() if k in Parametros.__dataclass_fields__})
            ex = Execucao(id=d.name, params=p, pasta=d, origem=r.get("origem", "manual"))
            for k in ("estado", "inicio", "fim", "totais_bases", "registros", "atendem", "a_tentar", "baixados", "ja_existiam",
                      "falharam", "sem_pdf", "erro", "diagnostico"):
                setattr(ex, k, r.get(k, getattr(ex, k)))
            if ex.estado in ("na fila", "buscando", "baixando"):
                ex.estado = "interrompida"
                ex.erro = ex.erro or "o Biblio-now foi encerrado durante a busca; use Retomar para continuar"
            execucoes[d.name] = ex


# ---------------------------------------------------------------- API
app = FastAPI(title="Biblio-now", version=VERSAO, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=ESTATICO), name="static")

PAGINA_SEM_SESSAO = """<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Biblio-now</title>
<body style="font-family:system-ui;max-width:620px;margin:80px auto;color:#1d2433"><h1 style="color:#1f3a5f">Biblio-now</h1>
<p>Abra o Biblio-now pelo link exibido na janela em que ele foi iniciado, ou pelo arquivo <b>ABRIR_BIBLIO_NOW.html</b>
na pasta do programa (contém um código de acesso desta sessão).</p>
<p>O código protege a interface contra acessos de outros programas e páginas.</p></body></html>"""
CSP_RELATORIO = "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'"


def _cabecalhos(resp, caminho: str):
    for k, v in seg.CABECALHOS.items():
        resp.headers.setdefault(k, v)                   # setdefault: rotas de relatório definem a própria CSP
    if caminho.startswith("/api/") or caminho == "/":
        resp.headers["Cache-Control"] = "no-store"
    return resp


@app.middleware("http")
async def protecao(request: Request, call_next):
    caminho = request.url.path
    if request.headers.get("host", "") not in seg.hosts_permitidos(PORTA):
        return _cabecalhos(PlainTextResponse("Host não permitido", status_code=421), caminho)
    if caminho == "/" and request.query_params.get("t"):
        if not sessao.valido(request.query_params["t"]):
            return _cabecalhos(HTMLResponse(PAGINA_SEM_SESSAO, status_code=401), caminho)
        r = RedirectResponse("/", status_code=303)       # tira o token da barra de endereço
        r.set_cookie(seg.Sessao.COOKIE, sessao.token, httponly=True, samesite="strict", path="/")
        return _cabecalhos(r, caminho)
    if not caminho.startswith("/static/"):
        if not sessao.valido(request.cookies.get(seg.Sessao.COOKIE)):
            if caminho == "/":
                return _cabecalhos(HTMLResponse(PAGINA_SEM_SESSAO, status_code=401), caminho)
            return _cabecalhos(JSONResponse({"detail": "sessão inválida"}, status_code=401), caminho)
        if request.method not in ("GET", "HEAD", "OPTIONS") and request.headers.get(seg.Sessao.CABECALHO_CSRF) != "1":
            return _cabecalhos(JSONResponse({"detail": "pedido sem o cabeçalho de proteção"}, status_code=403), caminho)
    return _cabecalhos(await call_next(request), caminho)


class PedidoBusca(BaseModel):
    pesquisa: str = Field("Geral", min_length=1, max_length=80)
    rotulo: str = Field("", max_length=80)
    blocos: list[list[str]] = Field(..., min_length=1, max_length=8)
    minimo_blocos: int | None = Field(None, ge=1, le=8)
    fontes: list[str] = ["openalex", "s2"]
    periodo: str = Field("todos", pattern="^(todos|1|5|10|personalizado)$")
    ano_min: int | None = Field(None, ge=1900, le=2100)
    ano_max: int | None = Field(None, ge=1900, le=2100)
    ordem: str = "relevancia"
    max_resultados: int = Field(1000, ge=1, le=10_000)
    max_pdfs: int = Field(1000, ge=0, le=10_000)
    paralelo: int = Field(6, ge=1, le=12)
    baixar_parciais: bool = False
    exata: bool = True


class PedidoAgendamento(BaseModel):
    nome: str = Field("", max_length=80)
    periodicidade: str
    hora: str = "08:00"
    dia_semana: int = Field(0, ge=0, le=6)
    dia_mes: int = Field(1, ge=1, le=31)
    ativo: bool = True
    busca: PedidoBusca


class PedidoChaves(BaseModel):
    OPENALEX_API_KEY: str = Field("", max_length=200)
    OPENALEX_EMAIL: str = Field("", max_length=200)
    UNPAYWALL_EMAIL: str = Field("", max_length=200)
    S2_API_KEY: str = Field("", max_length=200)


class PedidoPesquisa(BaseModel):
    nome: str = Field(..., min_length=1, max_length=80)
    descricao: str = Field("", max_length=500)


class PedidoTema(BaseModel):
    tema: str = Field(..., min_length=3, max_length=300)


class PedidoReferencia(BaseModel):
    texto: str = Field(..., min_length=1, max_length=400_000)


def _ex(id_: str) -> Execucao:
    ex = execucoes.get(id_)
    if not ex:
        raise HTTPException(404, "busca não encontrada")
    return ex


def _repo(pesquisa: str) -> Repositorio:
    n = nome_pesquisa(pesquisa)
    if n not in repositorios:
        raise HTTPException(404, f"pesquisa não encontrada: {n}")
    return repositorios[n]


@app.get("/", response_class=HTMLResponse)
def inicio():
    return (ESTATICO / "index.html").read_text(encoding="utf-8")


@app.get("/api/estado")
def estado():
    ativa = next((resumo(e) for e in execucoes.values() if e.estado in ("buscando", "baixando")), None)
    pesq = []
    for n, r in sorted(repositorios.items()):
        info = _info_pesquisa(r.raiz)
        pesq.append({"nome": n, "descricao": info.get("descricao", ""), "criada_em": info.get("criada_em", ""),
                     "obras": len(r.obras), "pdfs": len(list(r.pdf.glob("*.pdf"))), "pasta": str(r.raiz),
                     "buscas": sum(1 for e in execucoes.values() if e.params.pesquisa == n)})
    return {"versao": VERSAO, "autor": AUTOR, "chaves": {k: bool(v) for k, v in CHAVES.items()},
            "seguranca": {"cofre": cofre.origem_chave, "plataforma": seg.plataforma()},
            "pesquisas": pesq, "obras": sum(p["obras"] for p in pesq), "pdfs": sum(p["pdfs"] for p in pesq),
            "buscas": len(execucoes), "agendamentos": sum(1 for a in agendador.listar() if a.get("ativo")),
            "na_fila": fila.qsize(), "ativa": ativa, "repositorio": str(PESQUISAS)}


@app.post("/api/pesquisas")
def criar_pesquisa(p: PedidoPesquisa):
    n = nome_pesquisa(p.nome)
    existia = n in repositorios
    repo = abrir_pesquisa(n, criar=True, descricao=p.descricao.strip())
    return {"nome": repo.nome, "pasta": str(repo.raiz), "ja_existia": existia}


@app.post("/api/chaves")
def definir_chaves(p: PedidoChaves):
    novas = {k: v.strip() for k, v in p.model_dump().items() if v.strip()}
    for k in ("OPENALEX_EMAIL", "UNPAYWALL_EMAIL"):
        if k in novas and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", novas[k]):
            raise HTTPException(422, "e-mail inválido")
    if novas:
        cofre.atualizar(novas)
        CHAVES.update(novas)
    return {k: bool(v) for k, v in CHAVES.items()}


@app.post("/api/buscas")
def criar_busca(p: PedidoBusca):
    try:
        return resumo(nova_execucao(Parametros(**p.model_dump())))
    except (ValueError, TypeError) as e:
        raise HTTPException(422, str(e))


@app.post("/api/sugestoes")
def sugerir_palavras(p: PedidoTema):
    """Palavras-chave sugeridas a partir do tema (dados indexados no OpenAlex; nada é baixado)."""
    from . import sugestoes
    try:
        return sugestoes.sugerir(p.tema, CHAVES)
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.post("/api/consulta/testar")
def testar_consulta(p: PedidoBusca):
    """Conta os trabalhos de cada termo, de cada bloco e da combinação, sem baixar nada."""
    from .nucleo import diagnosticar
    try:
        return diagnosticar(Parametros(**p.model_dump()), CHAVES)
    except (ValueError, TypeError) as e:
        raise HTTPException(422, str(e))


@app.get("/api/buscas")
def listar_buscas(pesquisa: str | None = None):
    return list(reversed(resumos_buscas(nome_pesquisa(pesquisa) if pesquisa else None)))


@app.get("/api/buscas/{id_}")
def detalhe(id_: str):
    ex = _ex(id_)
    log = ex.log[-150:]
    if not log and (ex.pasta / "log.txt").exists():
        log = (ex.pasta / "log.txt").read_text(encoding="utf-8").splitlines()[-150:]
    return resumo(ex) | {"log": log, "pasta": str(ex.pasta)}


@app.post("/api/buscas/{id_}/cancelar")
def cancelar(id_: str):
    ex = _ex(id_)
    ex.cancelar.set()
    if ex.estado == "na fila":
        ex.estado = "cancelada"
    return resumo(ex)


@app.post("/api/buscas/{id_}/retomar")
def retomar(id_: str):
    """Nova execução com os mesmos parâmetros e na mesma pesquisa. O que já foi baixado aparece como
    'já no acervo' e não é baixado de novo."""
    ex = _ex(id_)
    if ex.estado in ("na fila", "buscando", "baixando"):
        raise HTTPException(409, "a busca ainda está em andamento")
    p = Parametros(**{k: v for k, v in ex.params.como_dict().items() if k in Parametros.__dataclass_fields__})
    base_nome = re.sub(r"\s*\(retomada\)$", "", p.rotulo or " ".join(p.blocos[0]))
    p.rotulo = base_nome[:68] + " (retomada)"
    return resumo(nova_execucao(p, origem=f"retomada de {ex.id}"))


ARQUIVOS = {"matriz_baixa.csv": "text/csv", "resultados.csv": "text/csv", "referencias.bib": "application/x-bibtex",
            "consulta.txt": "text/plain", "log.txt": "text/plain", "resumo.json": "application/json"}


@app.get("/api/buscas/{id_}/arquivos/{nome}")
def arquivo_busca(id_: str, nome: str):
    ex = _ex(id_)
    if nome not in ARQUIVOS or not (ex.pasta / nome).exists():
        raise HTTPException(404, "arquivo não disponível")
    return FileResponse(ex.pasta / nome, media_type=ARQUIVOS[nome], filename=f"{ex.id}_{nome}")


@app.get("/api/buscas/{id_}/zip")
def zip_busca(id_: str):
    """ZIP com as obras desta busca (pdf/, txt/, bib/, rastreabilidade/) e os relatórios da execução."""
    ex = _ex(id_)
    repo = repo_de(ex)
    lista = ex.pasta / "pdfs_desta_busca.txt"
    nomes = [n.strip() for n in lista.read_text(encoding="utf-8").splitlines() if n.strip()] if lista.exists() else []
    if not nomes:                                       # busca interrompida: usa as obras associadas a ela
        nomes = [Path(o["pdf"]).name for o in repo.obras.values() if ex.id in (o.get("buscas") or []) and o.get("pdf")]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in ARQUIVOS | {"matriz_baixa.json": ""}:
            if (ex.pasta / n).exists():
                z.write(ex.pasta / n, n)
        for n in dict.fromkeys(nomes):
            stem = Path(n).stem
            for pasta, ext in ((repo.pdf, ".pdf"), (repo.txt, ".txt"), (repo.bib, ".bib"), (repo.rastreio, ".json")):
                f = pasta / f"{stem}{ext}"
                if f.exists():
                    z.write(f, f"{pasta.name}/{f.name}")
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="{ex.id}.zip"'})


@app.get("/api/buscas/{id_}/registros")
def registros_busca(id_: str, limite: int = 2000):
    ex = _ex(id_)
    f = ex.pasta / "resultados.csv"
    if not f.exists():
        return []
    with open(f, encoding="utf-8-sig") as h:
        linhas = list(csv.DictReader(h, delimiter=";"))
    cols = ("titulo", "ano", "autores", "veiculo", "doi", "fonte", "verificacao_semantica", "status_pdf", "arquivo_pdf")
    return [{c: r.get(c, "") for c in cols} for r in linhas[: max(1, min(limite, 10_000))]]


@app.get("/api/obras")
def obras(pesquisa: str, q: str = "", limite: int = 300, pagina: int = 1):
    repo = _repo(pesquisa)
    q = q.strip().lower()
    itens = sorted(repo.obras.values(), key=lambda o: o.get("incorporada_em", ""), reverse=True)
    if q:
        itens = [o for o in itens if q in " ".join([o.get("titulo", ""), " ".join(o.get("autores") or []), o.get("veiculo", ""),
                                                     str(o.get("ano", "")), o.get("doi", "")]).lower()]
    limite = max(1, min(limite, 1000))
    ini = (max(1, pagina) - 1) * limite
    cols = ("id", "titulo", "autores", "ano", "veiculo", "doi", "url", "incorporada_em", "busca_origem_nome", "txt_extraido",
            "palavras_txt", "baixado_em", "host_download", "fonte")
    return {"total": len(itens), "itens": [{c: o.get(c) for c in cols} for o in itens[ini: ini + limite]]}


@app.get("/api/obras/{id_}/rastreabilidade")
def rastreabilidade(id_: str, pesquisa: str):
    repo = _repo(pesquisa)
    f = (repo.rastreio / f"{Path(id_).name}.json").resolve()
    if f.parent != repo.rastreio.resolve() or not f.exists():
        raise HTTPException(404, "ficha de rastreabilidade não encontrada")
    return json.loads(f.read_text(encoding="utf-8"))


@app.get("/api/obras/{id_}/{formato}")
def arquivo_obra(id_: str, formato: str, pesquisa: str):
    repo = _repo(pesquisa)
    pastas = {"pdf": (repo.pdf, "application/pdf"), "txt": (repo.txt, "text/plain; charset=utf-8"),
              "bib": (repo.bib, "application/x-bibtex")}
    if formato not in pastas:
        raise HTTPException(404, "formato inválido")
    pasta, mime = pastas[formato]
    f = (pasta / f"{Path(id_).name}.{formato}").resolve()
    if f.parent != pasta.resolve() or not f.exists():
        raise HTTPException(404, "arquivo não encontrado")
    return FileResponse(f, media_type=mime, filename=f.name if formato != "pdf" else None)


@app.get("/api/fichamento")
def baixar_fichamento(pesquisa: str):
    repo = _repo(pesquisa)
    f = repo.raiz / "fichamento.xlsx"
    if not f.exists():
        with trava_fich:
            fichamento.gerar_planilha(repo.raiz, repo.obras, resumos_buscas(repo.nome))
    return FileResponse(f, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=f"biblionow_fichamento_{slug(repo.nome)}_{datetime.now():%Y%m%d}.xlsx")


@app.get("/api/protocolo", response_class=HTMLResponse)
def ver_protocolo(pesquisa: str):
    repo = _repo(pesquisa)
    f = repo.protocolo / "protocolo_sigma.html"
    if not f.exists():
        with trava_fich:
            fichamento.gerar_protocolo(repo.raiz, repo.obras)
    r = HTMLResponse(f.read_text(encoding="utf-8"))
    r.headers["Content-Security-Policy"] = CSP_RELATORIO
    return r


@app.get("/api/protocolo/pdf")
def protocolo_pdf(pesquisa: str):
    repo = _repo(pesquisa)
    f = repo.protocolo / "protocolo_sigma.pdf"
    if not f.exists():
        raise HTTPException(404, "PDF do protocolo indisponível (instale o WeasyPrint) – use a versão HTML")
    return FileResponse(f, media_type="application/pdf", filename=f"protocolo_sigma_{slug(repo.nome)}_{datetime.now():%Y%m%d}.pdf")


# ---------------------------------------------------------------- pasta relatorios/ de cada pesquisa
TIPOS_REL = {".csv": "text/csv", ".json": "application/json", ".txt": "text/plain; charset=utf-8", ".bib": "application/x-bibtex",
             ".html": "text/html; charset=utf-8", ".pdf": "application/pdf"}


@app.get("/api/relatorios")
def listar_relatorios(pesquisa: str):
    repo = _repo(pesquisa)
    itens = []
    for f in sorted(repo.relatorios.rglob("*")):
        if f.is_file() and f.suffix in TIPOS_REL:
            itens.append({"caminho": f.relative_to(repo.relatorios).as_posix(), "tamanho": f.stat().st_size,
                          "alterado": datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")})
    return {"pasta": str(repo.relatorios), "itens": itens}


@app.get("/api/relatorios/{caminho:path}")
def arquivo_relatorio(caminho: str, pesquisa: str):
    rel = _repo(pesquisa).relatorios.resolve()
    f = (rel / caminho).resolve()
    if rel not in f.parents or not f.is_file() or f.suffix not in TIPOS_REL:
        raise HTTPException(404, "relatório não encontrado")
    if f.suffix == ".html":
        r = HTMLResponse(f.read_text(encoding="utf-8"))
        r.headers["Content-Security-Policy"] = CSP_RELATORIO
        return r
    return FileResponse(f, media_type=TIPOS_REL[f.suffix], filename=None if f.suffix == ".pdf" else f.name)


# ---------------------------------------------------------------- agendamentos
@app.get("/api/agendamentos")
def listar_agendamentos():
    return {"itens": agendador.listar(), "dias_semana": DIAS_SEMANA}


@app.post("/api/agendamentos")
def criar_agendamento(p: PedidoAgendamento):
    try:
        b = Parametros(**p.busca.model_dump()).validar()
        d = p.model_dump()
        d["busca"]["pesquisa"] = b.pesquisa
        abrir_pesquisa(b.pesquisa, criar=True)
        return agendador.criar(d)
    except (ValueError, TypeError) as e:
        raise HTTPException(422, str(e))


@app.patch("/api/agendamentos/{id_}")
def alterar_agendamento(id_: str, mudancas: dict):
    if id_ not in agendador.itens:
        raise HTTPException(404, "agendamento não encontrado")
    permitidos = {k: v for k, v in mudancas.items() if k in ("ativo", "periodicidade", "hora", "dia_semana", "dia_mes", "nome")}
    try:
        return agendador.alterar(id_, permitidos)
    except (ValueError, TypeError) as e:
        raise HTTPException(422, str(e))


@app.delete("/api/agendamentos/{id_}")
def remover_agendamento(id_: str):
    agendador.remover(id_)
    return {"ok": True}


@app.post("/api/agendamentos/{id_}/executar")
def executar_agendamento(id_: str):
    if id_ not in agendador.itens:
        raise HTTPException(404, "agendamento não encontrado")
    return {"busca": agendador.executar_agora(id_)}


# ---------------------------------------------------------------- validação
@app.post("/api/validacao/testes")
def validacao_testes(pesquisa: str):
    repo = _repo(pesquisa)
    with repo.trava:
        obras_ = dict(repo.obras)
    return validacao.testes(repo.raiz, obras_, cofre, CHAVES, ENV, sessao) | {"pesquisa": repo.nome}


@app.get("/api/validacao/metricas/{id_}")
def validacao_metricas(id_: str):
    ex = _ex(id_)
    return validacao.metricas(ex.resumo(), ex.pasta)


@app.post("/api/validacao/referencia/{id_}")
def validacao_referencia(id_: str, p: PedidoReferencia):
    ex = _ex(id_)
    try:
        return validacao.referencia(ex.resumo(), ex.pasta, p.texto)
    except ValueError as e:
        raise HTTPException(422, str(e))


# ---------------------------------------------------------------- execução
ENDERECO_TXT = RAIZ / "ENDERECO_BIBLIO_NOW.txt"
ENDERECO_HTML = RAIZ / "ABRIR_BIBLIO_NOW.html"


def _encerrar():
    """Ao fechar o servidor no meio de uma busca, grava o que já foi feito e marca a busca como interrompida."""
    for ex in list(execucoes.values()):
        if ex.estado in ("buscando", "baixando", "na fila"):
            ex.cancelar.set()
            ex.estado, ex.fim = "interrompida", datetime.now().isoformat(timespec="seconds")
            ex.erro = "o Biblio-now foi encerrado durante a busca; use Retomar para continuar"
            try:
                ex.escrever("Biblio-now encerrado durante a busca: progresso gravado; use Retomar para continuar.")
                (ex.pasta / "resumo.json").write_text(json.dumps(ex.resumo(), ensure_ascii=False, indent=2), encoding="utf-8")
            except OSError:
                pass
    for repo in repositorios.values():
        repo.gravar()


def _apagar_endereco():
    for f in (ENDERECO_TXT, ENDERECO_HTML):
        f.unlink(missing_ok=True)


def gravar_endereco(url: str):
    """Grava na pasta do Biblio-now o endereço desta sessão (texto e um atalho HTML que redireciona).
    O link contém o código de acesso: os arquivos ficam só com permissão do usuário e são apagados ao encerrar."""
    import atexit
    import html as _html
    agora = f"{datetime.now():%d/%m/%Y %H:%M}"
    ENDERECO_TXT.write_text(
        f"Biblio-now {VERSAO} · sessão iniciada em {agora}\n\n"
        f"Abra no navegador:\n{url}\n\n"
        "O código depois de ?t= vale só para esta sessão. Não compartilhe.\n"
        "Este arquivo é apagado quando o Biblio-now é encerrado e recriado a cada nova execução.\n",
        encoding="utf-8")
    u = _html.escape(url, quote=True)
    ENDERECO_HTML.write_text(
        f'<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={u}">'
        f'<title>Abrir Biblio-now</title><p>Abrindo o Biblio-now… Se não abrir, clique: <a href="{u}">{u}</a></p></html>\n',
        encoding="utf-8")
    for f in (ENDERECO_TXT, ENDERECO_HTML):
        try:
            os.chmod(f, 0o600)
        except OSError:
            pass                                        # Windows: a pasta do usuário já restringe o acesso
    atexit.register(_apagar_endereco)                   # saída normal do Python
    atexit.register(_encerrar)


app.router.on_shutdown.append(_encerrar)                # Ctrl+C/SIGTERM: o uvicorn reenvia o sinal e pula o atexit
app.router.on_shutdown.append(_apagar_endereco)


def main():
    import uvicorn
    ap = argparse.ArgumentParser(description="Biblio-now (servidor web local)")
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--sem-navegador", action="store_true")
    a = ap.parse_args()
    global PORTA
    PORTA = a.porta
    try:
        sys.stdout.reconfigure(line_buffering=True)     # mostra o link na hora, mesmo com a saída redirecionada
    except (AttributeError, ValueError):
        pass
    migrada = migrar_repositorio_antigo()
    carregar_pesquisas()
    carregar_anteriores()
    threading.Thread(target=trabalhador, daemon=True, name="buscas").start()
    agendador.iniciar()
    url = f"http://127.0.0.1:{a.porta}/?t={sessao.token}"
    gravar_endereco(url)
    print(f"Biblio-now {VERSAO} · {AUTOR}")
    print(f"Abra: {url}")
    print("      (link com o código de acesso desta sessão; não compartilhe. Ctrl+C para encerrar)")
    print(f"      O mesmo link está em {ENDERECO_TXT.name} e no atalho {ENDERECO_HTML.name}, na pasta {RAIZ}")
    print(f"Cofre de chaves: {cofre.origem_chave}")
    if CHAVES_IMPORTADAS:
        print(f"Chaves levadas do .env para o cofre criptografado: {', '.join(CHAVES_IMPORTADAS)}")
    if migrada:
        print(f"Repositório antigo movido para a pesquisa '{migrada}'")
    print(f"Pesquisas em {PESQUISAS}: " + (", ".join(f"{n} ({len(r.obras)} obras)" for n, r in sorted(repositorios.items())) or "nenhuma"))
    print("Chaves: " + ", ".join(f"{k} {'definida' if v else 'não definida'}" for k, v in CHAVES.items()))
    if not a.sem_navegador:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=a.porta, log_level="warning")


if __name__ == "__main__":
    main()

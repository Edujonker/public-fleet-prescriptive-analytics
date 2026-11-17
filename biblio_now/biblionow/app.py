# -*- coding: utf-8 -*-
"""
Biblio-now · servidor web local (FastAPI). Autor: Eduardo Lopes Jonker.

  python -m biblionow.app [--porta 8765] [--sem-navegador]

Só aceita conexões do próprio computador (127.0.0.1) e abre a interface por um link com token de sessão.
Uma busca roda por vez; as demais esperam na fila. Chaves de API ficam no cofre criptografado (seguranca.py);
se estiverem em texto no .env, são levadas para o cofre e apagadas do .env na primeira execução.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import queue
import re
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
from .nucleo import Execucao, Parametros, Repositorio, executar

VERSAO = fichamento.VERSAO
AUTOR = fichamento.AUTOR
RAIZ = Path(__file__).resolve().parent.parent
REPO = Path(os.environ.get("BIBLIONOW_REPOSITORIO") or (RAIZ / "repositorio")).resolve()
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


# ---------------------------------------------------------------- estado do servidor
repositorio = Repositorio(REPO)
execucoes: dict[str, Execucao] = {}
fila: "queue.Queue[str]" = queue.Queue()
trava_fich = threading.Lock()


def slug(t: str, n=40) -> str:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")[:n].lower() or "busca"


def resumos_buscas():
    return sorted((e.resumo() for e in execucoes.values()), key=lambda r: r["id"])


def apos_execucao(ex: Execucao):
    with trava_fich:
        fichamento.atualizar_tudo(REPO, repositorio.obras, resumos_buscas(), ex.resumo())
    ex.escrever("Planilha de fichamento e Protocolo Sigma atualizados.")


def trabalhador():
    while True:
        id_ = fila.get()
        ex = execucoes.get(id_)
        if ex and not ex.cancelar.is_set():
            executar(ex, repositorio, CHAVES, apos_execucao)
        elif ex:
            ex.estado = "cancelada"
        fila.task_done()


def nova_execucao(params: Parametros, origem="manual") -> Execucao:
    params.validar()
    id_ = f"{datetime.now():%Y%m%d_%H%M%S}_{slug(params.rotulo or ' '.join(params.blocos[0]))}"
    while id_ in execucoes:
        id_ += "_"
    pasta = REPO / "buscas" / id_
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
    for d in sorted((REPO / "buscas").iterdir()):
        f = d / "resumo.json"
        if not (d.is_dir() and f.exists()) or d.name in execucoes:
            continue
        r = json.loads(f.read_text(encoding="utf-8"))
        pr = r.get("parametros") or {"blocos": r.get("blocos") or [["?"]], "minimo_blocos": r.get("minimo_blocos"), "rotulo": r.get("rotulo", "")}
        p = Parametros(**{k: v for k, v in pr.items() if k in Parametros.__dataclass_fields__})
        ex = Execucao(id=d.name, params=p, pasta=d, origem=r.get("origem", "manual"))
        for k in ("estado", "inicio", "fim", "totais_bases", "registros", "atendem", "a_tentar", "baixados", "ja_existiam",
                  "falharam", "sem_pdf", "erro"):
            setattr(ex, k, r.get(k, getattr(ex, k)))
        if ex.estado in ("na fila", "buscando", "baixando"):
            ex.estado = "interrompida"
        execucoes[d.name] = ex


# ---------------------------------------------------------------- API
app = FastAPI(title="Biblio-now", version=VERSAO, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=ESTATICO), name="static")

PAGINA_SEM_SESSAO = """<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Biblio-now</title>
<body style="font-family:system-ui;max-width:620px;margin:80px auto;color:#1d2433"><h1 style="color:#1f3a5f">Biblio-now</h1>
<p>Abra o Biblio-now pelo link exibido na janela em que ele foi iniciado (contém um código de acesso desta sessão).</p>
<p>O código protege a interface contra acessos de outros programas e páginas.</p></body></html>"""


def _cabecalhos(resp, caminho: str):
    for k, v in seg.CABECALHOS.items():
        resp.headers.setdefault(k, v)
    if caminho.startswith("/api/protocolo") and "pdf" not in caminho:   # relatório estático com CSS embutido
        resp.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'"
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


def _ex(id_: str) -> Execucao:
    ex = execucoes.get(id_)
    if not ex:
        raise HTTPException(404, "busca não encontrada")
    return ex


@app.get("/", response_class=HTMLResponse)
def inicio():
    return (ESTATICO / "index.html").read_text(encoding="utf-8")


@app.get("/api/estado")
def estado():
    ativa = next((e.resumo() for e in execucoes.values() if e.estado in ("buscando", "baixando")), None)
    return {"versao": VERSAO, "autor": AUTOR, "chaves": {k: bool(v) for k, v in CHAVES.items()},
            "seguranca": {"cofre": cofre.origem_chave, "plataforma": seg.plataforma()},
            "obras": len(repositorio.obras), "pdfs": len(list(repositorio.pdf.glob("*.pdf"))),
            "buscas": len(execucoes), "agendamentos": sum(1 for a in agendador.listar() if a.get("ativo")),
            "na_fila": fila.qsize(), "ativa": ativa, "repositorio": str(REPO)}


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
        return nova_execucao(Parametros(**p.model_dump())).resumo()
    except (ValueError, TypeError) as e:
        raise HTTPException(422, str(e))


@app.get("/api/buscas")
def listar_buscas():
    return list(reversed(resumos_buscas()))


@app.get("/api/buscas/{id_}")
def detalhe(id_: str):
    ex = _ex(id_)
    log = ex.log[-150:]
    if not log and (ex.pasta / "log.txt").exists():
        log = (ex.pasta / "log.txt").read_text(encoding="utf-8").splitlines()[-150:]
    return ex.resumo() | {"log": log}


@app.post("/api/buscas/{id_}/cancelar")
def cancelar(id_: str):
    ex = _ex(id_)
    ex.cancelar.set()
    if ex.estado == "na fila":
        ex.estado = "cancelada"
    return ex.resumo()


ARQUIVOS = {"resultados.csv": "text/csv", "referencias.bib": "application/x-bibtex", "consulta.txt": "text/plain",
            "log.txt": "text/plain", "resumo.json": "application/json"}


@app.get("/api/buscas/{id_}/arquivos/{nome}")
def arquivo_busca(id_: str, nome: str):
    ex = _ex(id_)
    if nome not in ARQUIVOS or not (ex.pasta / nome).exists():
        raise HTTPException(404, "arquivo não disponível")
    return FileResponse(ex.pasta / nome, media_type=ARQUIVOS[nome], filename=f"{ex.id}_{nome}")


@app.get("/api/buscas/{id_}/zip")
def zip_busca(id_: str):
    """ZIP com as obras desta busca (pdf/, txt/, bib/) e os relatórios da execução."""
    ex = _ex(id_)
    lista = ex.pasta / "pdfs_desta_busca.txt"
    nomes = [n.strip() for n in lista.read_text(encoding="utf-8").splitlines() if n.strip()] if lista.exists() else []
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in ARQUIVOS:
            if (ex.pasta / n).exists():
                z.write(ex.pasta / n, n)
        for n in dict.fromkeys(nomes):
            stem = Path(n).stem
            for pasta, ext in ((repositorio.pdf, ".pdf"), (repositorio.txt, ".txt"), (repositorio.bib, ".bib")):
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
def obras(q: str = "", limite: int = 300, pagina: int = 1):
    q = q.strip().lower()
    itens = sorted(repositorio.obras.values(), key=lambda o: o.get("incorporada_em", ""), reverse=True)
    if q:
        itens = [o for o in itens if q in " ".join([o.get("titulo", ""), " ".join(o.get("autores") or []), o.get("veiculo", ""),
                                                     str(o.get("ano", "")), o.get("doi", "")]).lower()]
    ini = (max(1, pagina) - 1) * limite
    cols = ("id", "titulo", "autores", "ano", "veiculo", "doi", "url", "incorporada_em", "busca_origem_nome", "txt_extraido", "palavras_txt")
    return {"total": len(itens), "itens": [{c: o.get(c) for c in cols} for o in itens[ini: ini + limite]]}


@app.get("/api/obras/{id_}/{formato}")
def arquivo_obra(id_: str, formato: str):
    pastas = {"pdf": (repositorio.pdf, "application/pdf"), "txt": (repositorio.txt, "text/plain; charset=utf-8"),
              "bib": (repositorio.bib, "application/x-bibtex")}
    if formato not in pastas:
        raise HTTPException(404, "formato inválido")
    pasta, mime = pastas[formato]
    f = (pasta / f"{Path(id_).name}.{formato}").resolve()
    if f.parent != pasta.resolve() or not f.exists():
        raise HTTPException(404, "arquivo não encontrado")
    return FileResponse(f, media_type=mime, filename=f.name if formato != "pdf" else None)


@app.get("/api/fichamento")
def baixar_fichamento():
    f = REPO / "fichamento.xlsx"
    if not f.exists():
        with trava_fich:
            fichamento.gerar_planilha(REPO, repositorio.obras, resumos_buscas())
    return FileResponse(f, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename=f"biblionow_fichamento_{datetime.now():%Y%m%d}.xlsx")


@app.get("/api/protocolo", response_class=HTMLResponse)
def ver_protocolo():
    f = REPO / "protocolo" / "protocolo_sigma.html"
    if not f.exists():
        with trava_fich:
            fichamento.gerar_protocolo(REPO, repositorio.obras)
    return f.read_text(encoding="utf-8")


@app.get("/api/protocolo/pdf")
def protocolo_pdf():
    f = REPO / "protocolo" / "protocolo_sigma.pdf"
    if not f.exists():
        raise HTTPException(404, "PDF do protocolo indisponível (instale o WeasyPrint) – use a versão HTML")
    return FileResponse(f, media_type="application/pdf", filename=f"protocolo_sigma_{datetime.now():%Y%m%d}.pdf")


@app.get("/api/agendamentos")
def listar_agendamentos():
    return {"itens": agendador.listar(), "dias_semana": DIAS_SEMANA}


@app.post("/api/agendamentos")
def criar_agendamento(p: PedidoAgendamento):
    try:
        Parametros(**p.busca.model_dump()).validar()
        return agendador.criar(p.model_dump())
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
class PedidoReferencia(BaseModel):
    texto: str = Field(..., min_length=1, max_length=400_000)


@app.post("/api/validacao/testes")
def validacao_testes():
    with repositorio.trava:
        obras_ = dict(repositorio.obras)
    return validacao.testes(REPO, obras_, cofre, CHAVES, ENV, sessao)


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
    app.router.on_shutdown.append(_apagar_endereco)     # Ctrl+C/SIGTERM: o uvicorn reenvia o sinal e pula o atexit


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
    print(f"Repositório: {REPO}")
    print("Chaves: " + ", ".join(f"{k} {'definida' if v else 'não definida'}" for k, v in CHAVES.items()))
    if not a.sem_navegador:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=a.porta, log_level="warning")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Biblio-now · núcleo de busca e download de artigos científicos de acesso aberto.
Autor: Eduardo Lopes Jonker.

Reaproveita as funções testadas de base.py (cópia de scripts/buscar_artigos.py do projeto de dissertação
PPGCAP/UDESC): HTTP com novas tentativas, normalização dos registros do OpenAlex e do Semantic Scholar,
download que só grava arquivos que começam com %PDF, busca do link do PDF na página do artigo e Unpaywall.

Repositório (compartilhado por todas as buscas):
  pdf/<obra>.pdf      texto completo
  txt/<obra>.txt      texto extraído do PDF (para leitura, busca e fichamento)
  bib/<obra>.bib      referência BibTeX da obra
  obras.json          metadados de cada obra (título, autores, resumo, DOI, busca de origem, datas)
  controle_downloads.json, indice_conteudo.json   evitam baixar de novo e guardar duplicatas
  buscas/<id>/        resultados.csv, referencias.bib, consulta.txt, log.txt, resumo.json de cada execução
Depois de cada execução, fichamento.py atualiza a planilha de fichamento e o relatório de protocolo.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import requests

from . import base
from . import relatorio_baixa as rb
from . import seguranca as seg

PERIODOS = ("todos", "1", "5", "10", "personalizado")
USER_AGENT = "Biblio-now/1.0 (busca academica de acesso aberto; python-requests)"
TRANSITORIAS = ("HTTP 429", "HTTP 202", "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504", "HTTP 520", "erro de rede")
DIAS_NOVA_TENTATIVA = 30


# ---------------------------------------------------------------- parâmetros de uma busca
@dataclass
class Parametros:
    blocos: list[list[str]]                 # [["explainable AI", "XAI"], ["public sector", "government"]]
    minimo_blocos: int | None = None        # padrão: todos os blocos
    fontes: tuple[str, ...] = ("openalex", "s2")
    periodo: str = "todos"                  # todos | 1 | 5 | 10 (últimos N anos, contando o atual) | personalizado
    ano_min: int | None = None              # usados só com periodo = "personalizado"
    ano_max: int | None = None
    ordem: str = "relevancia"               # relevancia | citacoes | recentes
    max_resultados: int = 1000              # por base
    max_pdfs: int = 1000
    paralelo: int = 6
    baixar_parciais: bool = False
    exata: bool = True
    rotulo: str = ""

    def validar(self):
        self.blocos = [b for b in ([t.strip() for t in blk if t and t.strip()] for blk in self.blocos) if b]
        if not self.blocos:
            raise ValueError("informe ao menos um bloco com um termo")
        if len(self.blocos) > 8 or any(len(b) > 30 for b in self.blocos):
            raise ValueError("no máximo 8 blocos e 30 termos por bloco")
        for b in self.blocos:
            for t in b:
                if len(t) > 120 or re.search(r'["\\<>]', t):
                    raise ValueError(f"termo inválido: {t[:40]!r} (sem aspas, barras ou < >; até 120 caracteres)")
        n = len(self.blocos)
        self.minimo_blocos = n if not self.minimo_blocos else max(1, min(int(self.minimo_blocos), n))
        self.fontes = tuple(f for f in self.fontes if f in ("openalex", "s2")) or ("openalex",)
        self.ordem = self.ordem if self.ordem in ("relevancia", "citacoes", "recentes") else "relevancia"
        self.max_resultados = max(1, min(int(self.max_resultados), 10_000))
        self.max_pdfs = max(0, min(int(self.max_pdfs), 10_000))
        self.paralelo = max(1, min(int(self.paralelo), 12))
        for a in ("ano_min", "ano_max"):
            v = getattr(self, a)
            setattr(self, a, int(v) if v not in (None, "", 0) else None)
        self.periodo = str(self.periodo or "todos")
        if self.periodo not in PERIODOS:
            self.periodo = "personalizado" if (self.ano_min or self.ano_max) else "todos"
        if self.ano_min and self.ano_max and self.ano_min > self.ano_max:
            raise ValueError("o ano inicial é maior que o ano final")
        self.rotulo = (self.rotulo or "").strip()[:80]
        return self

    def intervalo_anos(self) -> tuple[int | None, int | None]:
        """Anos efetivos da busca. Períodos relativos são recalculados a cada execução (útil nos agendamentos)."""
        if self.periodo in ("1", "5", "10"):
            ano = datetime.now().year
            return ano - int(self.periodo) + 1, None       # sem ano final: inclui artigos publicados online antes do volume
        if self.periodo == "personalizado":
            return self.ano_min, self.ano_max
        return None, None

    def descrever_periodo(self) -> str:
        a, b = self.intervalo_anos()
        nomes = {"todos": "todos os anos", "1": "último ano", "5": "últimos 5 anos", "10": "últimos 10 anos"}
        if self.periodo in nomes and self.periodo != "todos":
            return f"{nomes[self.periodo]} (a partir de {a})"
        if self.periodo == "personalizado":
            return f"{a or '…'} a {b or '…'}"
        return nomes["todos"]

    def consulta(self, op_e, op_ou):
        """Com todos os blocos obrigatórios, o servidor recebe (A1 OR A2) AND (B1 OR B2)...; com mínimo menor,
        recebe OR entre todos os termos e o mínimo de blocos é conferido aqui, no título e no resumo."""
        blocos = ["(" + f" {op_ou} ".join(f'"{t}"' for t in b) + ")" for b in self.blocos]
        if self.minimo_blocos == len(self.blocos):
            return f" {op_e} ".join(blocos)
        return "(" + f" {op_ou} ".join(f'"{t}"' for b in self.blocos for t in b) + ")"

    def como_dict(self):
        return {k: (list(v) if isinstance(v, tuple) else v) for k, v in self.__dict__.items()}


# ---------------------------------------------------------------- uma execução
@dataclass
class Execucao:
    id: str
    params: Parametros
    pasta: Path
    origem: str = "manual"                  # manual | agendamento <nome>
    estado: str = "na fila"                 # na fila | buscando | baixando | concluída | cancelada | erro
    inicio: str = ""
    fim: str = ""
    totais_bases: dict = field(default_factory=dict)
    registros: int = 0
    atendem: int = 0
    a_tentar: int = 0
    baixados: int = 0
    ja_existiam: int = 0
    falharam: int = 0
    sem_pdf: int = 0
    erro: str = ""
    log: list[str] = field(default_factory=list)
    cancelar: threading.Event = field(default_factory=threading.Event)
    segredos: tuple = ()                    # valores apagados do log

    def escrever(self, msg: str):
        linha = f"{datetime.now():%H:%M:%S} {seg.limpar(msg, self.segredos)}"
        self.log.append(linha)
        del self.log[:-400]
        with open(self.pasta / "log.txt", "a", encoding="utf-8") as f:
            f.write(linha + "\n")

    def resumo(self):
        return {"id": self.id, "rotulo": self.params.rotulo, "origem": self.origem, "estado": self.estado,
                "inicio": self.inicio, "fim": self.fim, "totais_bases": self.totais_bases, "registros": self.registros,
                "atendem": self.atendem, "a_tentar": self.a_tentar, "baixados": self.baixados,
                "ja_existiam": self.ja_existiam, "falharam": self.falharam, "sem_pdf": self.sem_pdf, "erro": self.erro,
                "blocos": self.params.blocos, "minimo_blocos": self.params.minimo_blocos,
                "parametros": self.params.como_dict()}


class _Saida:
    """Leva os print() das funções de base.py para o log da execução."""
    def __init__(self, ex: Execucao):
        self.ex, self.buf = ex, ""

    def write(self, s):
        self.buf += s
        while "\n" in self.buf:
            linha, self.buf = self.buf.split("\n", 1)
            if linha.strip():
                self.ex.escrever(linha.strip())

    def flush(self):
        pass


# ---------------------------------------------------------------- repositório
def _bibtex(r: dict, chave: str) -> str:
    tipo = "inproceedings" if any(x in (r.get("tipo") or "").lower() for x in ("proceed", "conference")) else "article"
    campos = [("title", r.get("titulo")), ("author", " and ".join(r.get("autores") or [])), ("year", r.get("ano")),
              ("journal" if tipo == "article" else "booktitle", r.get("veiculo")), ("doi", r.get("doi")), ("url", r.get("url")),
              ("abstract", (r.get("resumo") or "")[:4000]),
              ("biblionow_base", " e ".join(rb.bases_de(r.get("fonte", ""))) or "não informada"),
              ("biblionow_acesso_aberto", "sim" if r.get("acesso_aberto") else "não"),
              ("biblionow_pdf", "baixado"), ("biblionow_url_pdf", r.get("url_pdf")),
              ("biblionow_data", datetime.now().strftime("%Y-%m-%d %H:%M")),
              ("note", f"Obtido por Biblio-now em {datetime.now():%d/%m/%Y}; base: "
                       f"{' e '.join(rb.bases_de(r.get('fonte', ''))) or 'não informada'}; PDF de acesso aberto baixado")]
    corpo = ",\n".join(f"  {k} = {{{base.bib_escape(v)}}}" for k, v in campos if v)
    return f"@{tipo}{{{chave},\n{corpo}\n}}\n"


def extrair_txt(pdf: Path, destino: Path) -> tuple[bool, int]:
    """Extrai o texto com pypdf (Python puro: funciona no Linux e no Windows). Retorna (ok, palavras)."""
    try:
        from pypdf import PdfReader
        leitor = PdfReader(str(pdf))
        partes = []
        for pg in leitor.pages:
            try:
                partes.append(pg.extract_text() or "")
            except Exception:  # noqa: BLE001 - página com fonte ou estrutura inválida
                partes.append("")
        texto = "\n\n".join(partes).strip()
    except Exception:  # noqa: BLE001 - PDF corrompido, protegido ou só com imagens
        texto = ""
    destino.write_text(texto, encoding="utf-8")
    return bool(texto), len(texto.split())


class Repositorio:
    def __init__(self, raiz: Path):
        self.raiz = raiz
        self.pdf, self.txt, self.bib = raiz / "pdf", raiz / "txt", raiz / "bib"
        self.relatorios = raiz / "relatorios"
        for d in (self.pdf, self.txt, self.bib, raiz / "buscas", raiz / "protocolo", self.relatorios):
            d.mkdir(parents=True, exist_ok=True)
        self._ctl_f, self._hash_f, self._obras_f = raiz / "controle_downloads.json", raiz / "indice_conteudo.json", raiz / "obras.json"
        ler = lambda f: json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        self.controle, self.hashes, self.obras = ler(self._ctl_f), ler(self._hash_f), ler(self._obras_f)
        conhecidos = set(self.hashes.values())
        for f in self.pdf.glob("*.pdf"):                 # PDFs copiados à mão também entram no índice
            if f.name not in conhecidos:
                self.hashes[self._md5(f)] = f.name
        self.trava = threading.RLock()

    @staticmethod
    def _md5(f: Path):
        return hashlib.md5(f.read_bytes()).hexdigest()

    def gravar(self):
        with self.trava:
            for f, d in ((self._ctl_f, self.controle), (self._hash_f, self.hashes), (self._obras_f, self.obras)):
                tmp = f.with_suffix(".tmp")
                tmp.write_text(json.dumps(d, ensure_ascii=False, indent=0), encoding="utf-8")
                tmp.replace(f)

    def deduplicar(self, destino: Path) -> str:
        """Nome do arquivo a usar: o recém-baixado, ou o já existente se o conteúdo for idêntico."""
        h = self._md5(destino)
        with self.trava:
            ant = self.hashes.get(h)
            if ant and ant != destino.name and (self.pdf / ant).exists():
                destino.unlink()
                return ant
            self.hashes[h] = destino.name
            return destino.name

    def incorporar(self, r: dict, nome_pdf: str, ex: Execucao) -> dict:
        """Grava txt/ e bib/ da obra e registra seus metadados. Devolve o registro da obra."""
        stem = Path(nome_pdf).stem
        ok_txt, palavras = extrair_txt(self.pdf / nome_pdf, self.txt / f"{stem}.txt")
        (self.bib / f"{stem}.bib").write_text(_bibtex(r, re.sub(r"[^A-Za-z0-9]", "", stem)[:60] or "obra"), encoding="utf-8")
        agora = datetime.now().isoformat(timespec="seconds")
        with self.trava:
            ob = self.obras.get(stem) or {"id": stem, "incorporada_em": agora, "busca_origem": ex.id,
                                          "busca_origem_nome": ex.params.rotulo or ex.id}
            ob.update({"titulo": r.get("titulo", ""), "autores": r.get("autores") or [], "ano": r.get("ano", ""),
                       "veiculo": r.get("veiculo", ""), "doi": r.get("doi", ""), "url": r.get("url", ""),
                       "url_pdf": r.get("url_pdf", ""), "resumo": r.get("resumo", ""), "fonte": r.get("fonte", ""),
                       "citacoes": r.get("citacoes", 0), "verificacao": r.get("verificacao", ""),
                       "pdf": f"pdf/{nome_pdf}", "txt": f"txt/{stem}.txt", "bib": f"bib/{stem}.bib",
                       "txt_extraido": ok_txt, "palavras_txt": palavras,
                       "sha256_pdf": seg.sha256_arquivo(self.pdf / nome_pdf)})
            ob.setdefault("buscas", [])
            if ex.id not in ob["buscas"]:
                ob["buscas"].append(ex.id)
            self.obras[stem] = ob
        return ob

    def associar(self, nome_pdf: str, ex: Execucao):
        """Obra já existente encontrada de novo: só acrescenta a busca à lista da obra."""
        stem = Path(nome_pdf).stem
        with self.trava:
            ob = self.obras.get(stem)
            if ob is not None and ex.id not in ob.setdefault("buscas", []):
                ob["buscas"].append(ex.id)


def _pular(ent, hoje):
    if not ent or ent.get("status") == "baixado" or not ent.get("tentado_em"):
        return None
    if any(t in ent.get("status", "") for t in TRANSITORIAS):
        return None if ent["tentado_em"] < hoje else "tentado hoje"
    dias = (datetime.strptime(hoje, "%Y-%m-%d") - datetime.strptime(ent["tentado_em"], "%Y-%m-%d")).days
    return None if dias >= DIAS_NOVA_TENTATIVA else f"falha definitiva em {ent['tentado_em']}"


# ---------------------------------------------------------------- consultas às bases
def _openalex(sessao, p: Parametros, chave: str, email: str, ex: Execucao):
    headers = {"Authorization": f"Bearer {chave}"} if chave else None
    campo = "search.title_and_abstract.exact" if p.exata else "search.title_and_abstract"
    params = {campo: p.consulta("AND", "OR"), "per_page": 100,
              "select": ("id,doi,display_name,publication_year,authorships,primary_location,best_oa_location,"
                         "locations,open_access,cited_by_count,abstract_inverted_index,type")}
    filtros = ["type:!peer-review", "type:!paratext"]
    ano_min, ano_max = p.intervalo_anos()
    if ano_min:
        filtros.append(f"publication_year:>{ano_min - 1}")
    if ano_max:
        filtros.append(f"publication_year:<{ano_max + 1}")
    params["filter"] = ",".join(filtros)
    if email:
        params["mailto"] = email
    if p.ordem == "citacoes":
        params["sort"] = "cited_by_count:desc"
    elif p.ordem == "recentes":
        params["sort"] = "publication_date:desc"
    regs, total, pagina = [], None, 1
    if chave:
        params["cursor"] = "*"
    while len(regs) < p.max_resultados and not ex.cancelar.is_set():
        if not chave:
            if pagina > 100:
                ex.escrever("OpenAlex: limite de 10.000 resultados sem chave de API")
                break
            params["page"] = pagina
        dados = base.get_json(sessao, base.OPENALEX_URL, params, headers, tentativas=10, rotulo="OpenAlex")
        if total is None:
            total = dados.get("meta", {}).get("count", 0)
            ex.escrever(f"OpenAlex: {total} trabalhos correspondem à consulta")
        lote = dados.get("results", [])
        if not lote:
            break
        regs += [base.normalizar_openalex(w) for w in lote][: p.max_resultados - len(regs)]
        if chave:
            params["cursor"] = (dados.get("meta") or {}).get("next_cursor")
            if not params["cursor"]:
                break
        elif pagina * 100 >= (total or 0):
            break
        pagina += 1
        time.sleep(0.3 if chave else 1.2)
    return regs, total or 0


def _s2(sessao, p: Parametros, chave: str, ex: Execucao):
    headers = {"x-api-key": chave} if chave else None
    params = {"query": p.consulta("+", "|"),
              "fields": "title,year,authors,venue,externalIds,openAccessPdf,citationCount,abstract,url,publicationTypes"}
    ano_min, ano_max = p.intervalo_anos()
    if ano_min or ano_max:
        params["year"] = f"{ano_min or ''}-{ano_max or ''}"
    if p.ordem == "citacoes":
        params["sort"] = "citationCount:desc"
    elif p.ordem == "recentes":
        params["sort"] = "publicationDate:desc"
    regs, total = [], None
    while len(regs) < p.max_resultados and not ex.cancelar.is_set():
        dados = base.get_json(sessao, base.S2_URL, params, headers, tentativas=5 if chave else 9, rotulo="SemanticScholar")
        if total is None:
            total = dados.get("total", 0)
            ex.escrever(f"Semantic Scholar: {total} trabalhos correspondem à consulta")
        regs += [base.normalizar_s2(x) for x in (dados.get("data") or [])][: p.max_resultados - len(regs)]
        if not dados.get("token"):
            break
        params["token"] = dados["token"]
        time.sleep(1.1)                      # limite de 1 pedido por segundo com chave
    return regs, total or 0


def _semantica(r, padroes, minimo):
    texto = (r["titulo"] + " " + r["resumo"]).lower()
    n = sum(any(x.search(texto) for x in b) for b in padroes)
    if n >= minimo:
        return "ok", n
    return ("sem_resumo" if not r["resumo"] else f"parcial ({n} de {len(padroes)} blocos)"), n


# ---------------------------------------------------------------- execução completa
def executar(ex: Execucao, repo: Repositorio, chaves: dict, depois: Callable[[Execucao], None] = lambda e: None):
    p = ex.params
    ex.inicio = datetime.now().isoformat(timespec="seconds")
    ex.estado = "buscando"
    ex.segredos = tuple(v for k, v in chaves.items() if k in seg.SEGREDOS and v)
    sessao = seg.proteger_sessao(requests.Session())
    sessao.headers["User-Agent"] = USER_AGENT
    registros = []
    with contextlib.redirect_stdout(_Saida(ex)):
        try:
            listas = []
            if "openalex" in p.fontes and not ex.cancelar.is_set():
                try:
                    regs, tot = _openalex(sessao, p, chaves.get("OPENALEX_API_KEY", ""), chaves.get("OPENALEX_EMAIL", ""), ex)
                except RuntimeError as e:
                    if "key_not_activated" in str(e) or "HTTP 401" in str(e):
                        ex.escrever("OpenAlex: chave não aceita; repetindo sem chave")
                        regs, tot = _openalex(sessao, p, "", chaves.get("OPENALEX_EMAIL", ""), ex)
                    else:
                        ex.escrever(f"OpenAlex indisponível: {e}")
                        regs, tot = [], "indisponível"
                listas.append(regs)
                ex.totais_bases["OpenAlex"] = tot
                ex.escrever(f"OpenAlex: {len(regs)} registros recebidos")
            if "s2" in p.fontes and not ex.cancelar.is_set():
                try:
                    regs, tot = _s2(sessao, p, chaves.get("S2_API_KEY", ""), ex)
                except RuntimeError as e:
                    ex.escrever(f"Semantic Scholar indisponível: {e}")
                    regs, tot = [], "indisponível"
                listas.append(regs)
                ex.totais_bases["SemanticScholar"] = tot
                ex.escrever(f"Semantic Scholar: {len(regs)} registros recebidos")
            registros = base.unir(listas)
            pads = [[base.padrao_termo(t) for t in b] for b in p.blocos]
            for r in registros:
                r["verificacao"], r["n_blocos"] = _semantica(r, pads, p.minimo_blocos)
                r["status_pdf"], r["arquivo_pdf"], r["url_pdf"] = "", "", ""
            registros.sort(key=lambda r: (r["verificacao"] != "ok", -r["n_blocos"]))
            ex.registros, ex.atendem = len(registros), sum(r["verificacao"] == "ok" for r in registros)
            ex.escrever(f"{ex.registros} registros únicos; {ex.atendem} com pelo menos {p.minimo_blocos} bloco(s) no título/resumo")

            hoje = datetime.now().strftime("%Y-%m-%d")
            email = chaves.get("UNPAYWALL_EMAIL") or chaves.get("OPENALEX_EMAIL") or ""
            fila = []
            for r in registros:
                ent = repo.controle.get(base.chave_registro(r))
                if ent and ent.get("arquivo") and (repo.pdf / ent["arquivo"]).exists():
                    r["status_pdf"], r["arquivo_pdf"] = "ja_existia", ent["arquivo"]
                    repo.associar(ent["arquivo"], ex)
                    ex.ja_existiam += 1
                elif r["verificacao"] != "ok" and not p.baixar_parciais:
                    r["status_pdf"] = "nao_tentado (não atende ao mínimo de blocos)"
                elif not r["pdf_urls"] and not (email and r["doi"]):
                    r["status_pdf"] = "sem_pdf_aberto"
                    ex.sem_pdf += 1
                elif motivo := _pular(ent, hoje):
                    r["status_pdf"] = f"nao_tentado ({motivo})"
                elif len(fila) >= p.max_pdfs:
                    r["status_pdf"] = "nao_tentado (limite de PDFs)"
                else:
                    fila.append(r)
            ex.a_tentar = len(fila)
            ex.estado = "baixando"
            ex.escrever(f"PDFs a tentar: {len(fila)} ({p.paralelo} downloads simultâneos)")
            _baixar(fila, ex, repo, p.paralelo, email, hoje)
            for r in registros:
                r["status_pdf"] = r["status_pdf"] or "nao_tentado (cancelado)"
            ex.estado = "cancelada" if ex.cancelar.is_set() else "concluída"
        except Exception as e:  # noqa: BLE001 - a interface precisa receber o erro
            ex.estado, ex.erro = "erro", f"{type(e).__name__}: {e}"
            ex.escrever(f"ERRO: {ex.erro}")
        finally:
            ex.fim = datetime.now().isoformat(timespec="seconds")
            try:
                _gravar_saidas(ex, registros)
            except Exception as e:  # noqa: BLE001
                ex.escrever(f"ERRO ao gravar relatórios da busca: {e}")
            repo.gravar()
            (ex.pasta / "resumo.json").write_text(json.dumps(ex.resumo(), ensure_ascii=False, indent=2), encoding="utf-8")
            ex.escrever(f"Fim: {ex.estado}. Baixados {ex.baixados}; já existiam {ex.ja_existiam}; falharam {ex.falharam}.")
    try:
        depois(ex)                               # fichamento e protocolo
    except Exception as e:  # noqa: BLE001
        ex.escrever(f"ERRO ao atualizar fichamento/protocolo: {type(e).__name__}: {e}")


def _baixar(fila, ex: Execucao, repo: Repositorio, n_threads, email, hoje):
    local = threading.local()
    travas, trava_g = {}, threading.Lock()

    def sessao():
        if not hasattr(local, "s"):
            local.s = seg.proteger_sessao(requests.Session())
            local.s.headers["User-Agent"] = USER_AGENT
        return local.s

    def tarefa(r):
        if ex.cancelar.is_set():
            return
        urls = list(r["pdf_urls"])
        if email and r["doi"]:
            urls += [u for u in base.links_unpaywall(sessao(), r["doi"], email) if u not in urls]
        if not urls:
            r["status_pdf"] = "sem_pdf_aberto"
            with trava_g:
                ex.sem_pdf += 1
            return
        k = base.chave_registro(r)
        destino = repo.pdf / base.nome_arquivo(r)
        with trava_g:
            tv = travas.setdefault(base._host(urls[0]), threading.Lock())
        with tv:                                 # um download por site de cada vez
            ok, info = base.baixar_pdf(sessao(), urls, destino)
        ant = repo.controle.get(k, {})
        if ok:
            nome = repo.deduplicar(destino)
            r["arquivo_pdf"], r["url_pdf"] = nome, info
            if nome == destino.name:
                r["status_pdf"] = "baixado"
                repo.incorporar(r, nome, ex)
            else:
                r["status_pdf"] = "ja_existia"
                repo.associar(nome, ex)
            with trava_g:
                repo.controle[k] = {"arquivo": nome, "status": "baixado", "tentado_em": hoje, "tentativas": ant.get("tentativas", 0) + 1}
                if r["status_pdf"] == "baixado":
                    ex.baixados += 1
                    ex.escrever(f"[{ex.baixados}] {nome}")
                else:
                    ex.ja_existiam += 1
        else:
            r["status_pdf"] = f"falhou ({info})"
            with trava_g:
                repo.controle[k] = {"arquivo": "", "status": r["status_pdf"], "tentado_em": hoje, "tentativas": ant.get("tentativas", 0) + 1}
                ex.falharam += 1
        if (ex.baixados + ex.falharam) % 20 == 0:
            repo.gravar()

    pendentes = list(fila)
    for passada in (1, 2):
        if not pendentes or ex.cancelar.is_set():
            break
        if passada == 2:
            ex.escrever(f"Nova tentativa para {len(pendentes)} PDFs com erro de rede passageiro")
            with trava_g:
                ex.falharam -= len(pendentes)
            time.sleep(20)
        with ThreadPoolExecutor(max_workers=n_threads) as pool:
            list(pool.map(tarefa, pendentes))
        pendentes = [r for r in pendentes if r["status_pdf"].startswith("falhou (erro de rede")]


def _gravar_saidas(ex: Execucao, registros):
    p = ex.params
    for r in registros:
        r.setdefault("visto_em", "")
        if r.get("verificacao") == "ok":
            r["verificacao"] = f"ok ({r['n_blocos']} de {len(p.blocos)} blocos)"
    base.gravar_csv(registros, ex.pasta / "resultados.csv")
    linhas = [f"Biblio-now · busca: {p.rotulo or ex.id}", f"Origem: {ex.origem}", f"Início: {ex.inicio} · fim: {ex.fim}", "",
              "Blocos (OR dentro do bloco, AND entre blocos):"] + \
             [f"  {i}. " + " OR ".join(b) for i, b in enumerate(p.blocos, 1)] + \
             ["", f"Mínimo de blocos no título/resumo: {p.minimo_blocos} de {len(p.blocos)}",
              f"Consulta enviada ao OpenAlex: {p.consulta('AND', 'OR')}",
              f"Consulta enviada ao Semantic Scholar: {p.consulta('+', '|')}",
              f"Fontes: {', '.join(p.fontes)} · período: {p.descrever_periodo()} · ordem: {p.ordem}",
              f"Máximo por base: {p.max_resultados} · máximo de PDFs: {p.max_pdfs} · baixar parciais: {p.baixar_parciais}",
              f"Correspondências informadas pelas bases: {json.dumps(ex.totais_bases, ensure_ascii=False)}",
              f"Registros únicos: {ex.registros} · atendem: {ex.atendem} · PDFs baixados: {ex.baixados} · "
              f"já existiam: {ex.ja_existiam} · sem PDF aberto: {ex.sem_pdf} · falharam: {ex.falharam}"]
    m = rb.matriz(registros)
    rb.gravar_matriz(m, ex.pasta)
    rb.gravar_bib(registros, ex.pasta / "referencias.bib", ["RELATÓRIO DA BAIXA · " + linhas[0]] + linhas[1:] +
                  ["", "Campos de cada referência: biblionow_base (base de origem), biblionow_acesso_aberto (segundo a base),",
                   "biblionow_pdf (baixado | já no acervo | sem PDF aberto | falhou | não tentado), biblionow_motivo, biblionow_arquivo."], m)
    linhas += ["", "MATRIZ ESTATÍSTICA DA BAIXA (também em matriz_baixa.csv e no Protocolo Sigma)", ""] + rb.texto_matriz(m) + [""] + m["notas"]
    (ex.pasta / "consulta.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    rb.copiar_para_relatorios(ex.pasta, ex.pasta.parent.parent / "relatorios", ex.id)
    with open(ex.pasta / "pdfs_desta_busca.txt", "w", encoding="utf-8") as f:
        for r in registros:
            if r.get("arquivo_pdf"):
                f.write(r["arquivo_pdf"] + "\n")

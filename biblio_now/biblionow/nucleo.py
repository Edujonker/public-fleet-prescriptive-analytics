# -*- coding: utf-8 -*-
"""
Biblio-now · núcleo de busca e download de artigos científicos de acesso aberto.
Autor: Eduardo Lopes Jonker.

Reaproveita as funções testadas de base.py (cópia de scripts/buscar_artigos.py do projeto de dissertação
PPGCAP/UDESC): HTTP com novas tentativas, normalização dos registros do OpenAlex e do Semantic Scholar,
download que só grava arquivos que começam com %PDF, busca do link do PDF na página do artigo e Unpaywall.

Repositório: um por PESQUISA (pesquisas/<nome da pesquisa>/), para que temas diferentes não se misturem:
  pdf/<obra>.pdf      texto completo
  txt/<obra>.txt      texto extraído do PDF (para leitura, busca e fichamento)
  bib/<obra>.bib      referência BibTeX da obra
  obras.json          metadados de cada obra (título, autores, resumo, DOI, busca de origem, datas)
  controle_downloads.json, indice_conteudo.json   evitam baixar de novo e guardar duplicatas
  buscas/<id>/        resultados.csv, referencias.bib, consulta.txt, log.txt, resumo.json de cada execução
  rastreabilidade/<obra>.json   de onde, quando e como cada arquivo foi baixado (URL pedida e final, redirecionamentos,
                      cabeçalhos HTTP, tentativas, SHA-256/MD5, base, IDs, licença, busca e consulta)
  protocolo/registro_downloads.csv   toda tentativa de download (sucesso ou falha), com cadeia de hashes
Depois de cada execução, fichamento.py atualiza a planilha de fichamento e o relatório de protocolo.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import re
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import requests

import platform
import sys

from . import base
from . import fichamento
from . import relatorio_baixa as rb
from . import seguranca as seg

PERIODOS = ("todos", "1", "5", "10", "personalizado")
USER_AGENT = "Biblio-now/1.0 (busca academica de acesso aberto; python-requests)"
TRANSITORIAS = ("HTTP 429", "HTTP 202", "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504", "HTTP 520", "erro de rede")
DIAS_NOVA_TENTATIVA = 30


# ---------------------------------------------------------------- parâmetros de uma busca
_PROIBIDOS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVADOS = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def nome_pesquisa(nome: str) -> str:
    """Nome da pesquisa usado como nome da pasta: legível e válido no Linux e no Windows."""
    n = re.sub(r"\s+", " ", _PROIBIDOS.sub(" ", str(nome or ""))).strip(" .")[:60].strip(" .")
    if not n:
        n = "Geral"
    if n.upper() in _RESERVADOS or n in (".", ".."):
        n += "_"
    return n


@dataclass
class Parametros:
    blocos: list[list[str]]                 # [["explainable AI", "XAI"], ["public sector", "government"]]
    pesquisa: str = "Geral"                 # nome da pesquisa: cada uma tem o próprio repositório
    minimo_blocos: int | None = None        # padrão: 1 (OU entre blocos, busca ampla); n = E entre todos os blocos
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
        self.blocos = [b for b in ([re.sub(r"\s+", " ", t).strip() for t in blk if t and t.strip()] for blk in self.blocos) if b]
        self.blocos = [list(dict.fromkeys(b)) for b in self.blocos]          # termos repetidos no mesmo bloco
        if not self.blocos:
            raise ValueError("informe ao menos um bloco com um termo")
        if len(self.blocos) > 8 or any(len(b) > 30 for b in self.blocos):
            raise ValueError("no máximo 8 blocos e 30 termos por bloco")
        for b in self.blocos:
            for t in b:
                if len(t) > 120 or re.search(r'["\\<>]', t):
                    raise ValueError(f"termo inválido: {t[:40]!r} (sem aspas, barras ou < >; até 120 caracteres)")
        n = len(self.blocos)
        self.minimo_blocos = 1 if not self.minimo_blocos else max(1, min(int(self.minimo_blocos), n))
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
        self.pesquisa = nome_pesquisa(self.pesquisa)
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
    diagnostico: dict = field(default_factory=dict)

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
                "blocos": self.params.blocos, "minimo_blocos": self.params.minimo_blocos, "diagnostico": self.diagnostico,
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
              ("biblionow_pesquisa", r.get("_pesquisa")), ("biblionow_busca", r.get("_busca")),
              ("biblionow_baixado_em", r.get("_baixado_em")), ("biblionow_url_final", r.get("_url_final")),
              ("biblionow_sha256", r.get("_sha256")), ("biblionow_licenca", r.get("licenca")),
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
        self.relatorios, self.rastreio, self.protocolo = raiz / "relatorios", raiz / "rastreabilidade", raiz / "protocolo"
        self.nome = raiz.name
        for d in (self.pdf, self.txt, self.bib, raiz / "buscas", self.protocolo, self.relatorios, self.rastreio):
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

    COLS_DOWNLOADS = ["data_hora", "pesquisa", "id_busca", "nome_busca", "resultado", "motivo", "arquivo", "titulo", "doi", "base",
                      "url_solicitada", "url_final", "status_http", "content_type", "bytes", "sha256", "md5",
                      "inicio_download", "fim_download", "duracao_s", "links_tentados"]

    def registrar_download(self, ex: Execucao, r: dict, resultado: str, motivo: str, nome_pdf: str, meta: dict, sha256="", md5=""):
        """Toda tentativa de download (sucesso ou falha) entra em protocolo/registro_downloads.csv, com cadeia de hashes."""
        linha = [datetime.now().astimezone().isoformat(timespec="seconds"), self.nome, ex.id, ex.params.rotulo or ex.id, resultado,
                 motivo, nome_pdf and f"pdf/{nome_pdf}", r.get("titulo", "")[:300], r.get("doi", ""), r.get("fonte", ""),
                 meta.get("url_solicitada", ""), meta.get("url_final", ""), meta.get("status_http", ""), meta.get("content_type", ""),
                 meta.get("bytes", ""), sha256, md5, meta.get("inicio_download", ""), meta.get("fim_download", ""), meta.get("duracao_s", ""),
                 " | ".join(f"{t['url']} → {t['resultado']}" for t in meta.get("tentativas", []))[:2000]]
        with self.trava:
            fichamento._anexar_csv(self.protocolo / "registro_downloads.csv", self.COLS_DOWNLOADS, [linha])

    def _rastreabilidade(self, r: dict, nome_pdf: str, ex: Execucao, meta: dict) -> dict:
        f = self.pdf / nome_pdf
        p = ex.params
        return {
            "arquivo": f"pdf/{nome_pdf}", "pesquisa": self.nome,
            "busca": {"id": ex.id, "nome": p.rotulo or ex.id, "origem": ex.origem, "inicio": ex.inicio,
                      "blocos": p.blocos, "minimo_blocos": p.minimo_blocos, "periodo": p.descrever_periodo(),
                      "consulta_openalex": p.consulta("AND", "OR"), "consulta_semantic_scholar": p.consulta("+", "|")},
            "registro_bibliografico": {"titulo": r.get("titulo", ""), "autores": r.get("autores") or [], "ano": r.get("ano", ""),
                                       "veiculo": r.get("veiculo", ""), "tipo": r.get("tipo", ""), "doi": r.get("doi", ""),
                                       "pagina_do_artigo": r.get("url", ""), "base_de_origem": rb.bases_de(r.get("fonte", "")),
                                       "id_openalex": r.get("id_openalex", ""), "id_semantic_scholar": r.get("id_s2", ""),
                                       "verificacao_blocos": r.get("verificacao", "")},
            "acesso_aberto": {"segundo_a_base": bool(r.get("acesso_aberto")), "status_oa": r.get("status_oa", ""),
                              "licenca": r.get("licenca", ""), "versao": r.get("versao_oa", ""), "pagina_oa": r.get("pagina_oa", ""),
                              "links_de_pdf_informados": list(r.get("pdf_urls") or [])},
            "download": {k: meta.get(k) for k in ("url_solicitada", "url_final", "redirecionamentos", "host", "status_http",
                                                   "content_type", "content_length", "last_modified", "etag", "servidor_http",
                                                   "inicio_download", "fim_download", "duracao_s", "bytes", "user_agent")},
            "tentativas": meta.get("tentativas", []),
            "integridade": {"sha256": seg.sha256_arquivo(f), "md5": self._md5(f), "bytes_em_disco": f.stat().st_size,
                            "comeca_com_%PDF": f.read_bytes()[:1024].lstrip().startswith(b"%PDF")},
            "ambiente": {"programa": f"Biblio-now {fichamento.VERSAO}", "autor_do_programa": fichamento.AUTOR,
                         "sistema": f"{platform.system()} {platform.release()}", "python": sys.version.split()[0]},
        }

    def incorporar(self, r: dict, nome_pdf: str, ex: Execucao, meta: dict | None = None) -> dict:
        """Grava txt/, bib/ e rastreabilidade/ da obra e registra seus metadados. Devolve o registro da obra."""
        stem = Path(nome_pdf).stem
        meta = meta or {}
        ok_txt, palavras = extrair_txt(self.pdf / nome_pdf, self.txt / f"{stem}.txt")
        rast = self._rastreabilidade(r, nome_pdf, ex, meta)
        (self.rastreio / f"{stem}.json").write_text(json.dumps(rast, ensure_ascii=False, indent=2), encoding="utf-8")
        r = dict(r, _pesquisa=self.nome, _busca=ex.id, _baixado_em=meta.get("fim_download", ""), _url_final=meta.get("url_final", ""),
                 _sha256=rast["integridade"]["sha256"])
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
                       "sha256_pdf": rast["integridade"]["sha256"], "md5_pdf": rast["integridade"]["md5"],
                       "pesquisa": self.nome, "rastreabilidade": f"rastreabilidade/{stem}.json",
                       "baixado_em": meta.get("fim_download", ""), "url_pdf_final": meta.get("url_final", ""),
                       "host_download": meta.get("host", ""), "status_http": meta.get("status_http", ""),
                       "bytes": rast["integridade"]["bytes_em_disco"], "licenca": r.get("licenca", ""),
                       "id_openalex": r.get("id_openalex", ""), "id_s2": r.get("id_s2", "")})
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


# ---------------------------------------------------------------- diagnóstico da consulta
def _contar_openalex(sessao, consulta: str, p: Parametros, chave: str, email: str) -> int | None:
    campo = "search.title_and_abstract.exact" if p.exata else "search.title_and_abstract"
    params = {campo: consulta, "per_page": 1, "select": "id"}
    filtros = ["type:!peer-review", "type:!paratext"]
    a, b = p.intervalo_anos()
    if a:
        filtros.append(f"publication_year:>{a - 1}")
    if b:
        filtros.append(f"publication_year:<{b + 1}")
    params["filter"] = ",".join(filtros)
    if email:
        params["mailto"] = email
    try:
        r = sessao.get(base.OPENALEX_URL, params=params, headers={"Authorization": f"Bearer {chave}"} if chave else None, timeout=(10, 30))
        return (r.json().get("meta") or {}).get("count") if r.ok else None
    except (requests.RequestException, ValueError):
        return None


def diagnosticar(p: Parametros, chaves: dict, sessao=None) -> dict:
    """Quantos trabalhos o OpenAlex tem para cada termo, cada bloco e a combinação, com os mesmos filtros da busca.
    Mostra qual termo ou bloco zera o resultado. Só conta (não baixa nada); no máximo 40 consultas."""
    p.validar()
    sessao = sessao or seg.proteger_sessao(requests.Session())
    sessao.headers.setdefault("User-Agent", USER_AGENT)
    chave, email = chaves.get("OPENALEX_API_KEY", ""), chaves.get("OPENALEX_EMAIL", "")
    termos, blocos, n = [], [], 0
    for i, b in enumerate(p.blocos, 1):
        tb = []
        for t in b:
            c = _contar_openalex(sessao, f'"{t}"', p, chave, email) if n < 40 else None
            n += 1
            tb.append({"termo": t, "trabalhos": c})
            time.sleep(0.12)
        cb = _contar_openalex(sessao, "(" + " OR ".join(f'"{t}"' for t in b) + ")", p, chave, email)
        blocos.append({"bloco": i, "termos": tb, "trabalhos": cb})
    blocos_e = " AND ".join("(" + " OR ".join(f'"{t}"' for t in b) + ")" for b in p.blocos)
    todos = _contar_openalex(sessao, "(" + " OR ".join(f'"{t}"' for b in p.blocos for t in b) + ")", p, chave, email)
    juntos = _contar_openalex(sessao, blocos_e, p, chave, email) if len(p.blocos) > 1 else todos
    combinacao = juntos if p.minimo_blocos == len(p.blocos) else todos     # o que a busca de fato envia
    sugestoes = []
    zerados = [t["termo"] for b in blocos for t in b["termos"] if t["trabalhos"] == 0]
    if zerados:
        sugestoes.append("Nenhum trabalho tem estes termos no título ou no resumo: " + "; ".join(f"“{z}”" for z in zerados)
                         + ". Use palavras mais curtas ou sinônimos (por exemplo, só o substantivo principal).")
    vazios = [b["bloco"] for b in blocos if b["trabalhos"] == 0]
    if vazios:
        sugestoes.append(f"O(s) bloco(s) {', '.join(map(str, vazios))} não encontram nada sozinhos"
                         + (": com E entre blocos, a busca fica vazia." if p.minimo_blocos == len(p.blocos) and len(p.blocos) > 1 else
                            "; troque os termos desse bloco por sinônimos ou retire o bloco."))
    if len(p.blocos) > 1 and p.minimo_blocos > 1 and combinacao == 0 and not vazios:
        sugestoes.append("Cada bloco tem resultados, mas nenhum trabalho tem os blocos juntos. Reduza o “mínimo de blocos” "
                         "(a busca passa a usar OU e confere o mínimo no título/resumo) ou troque um bloco por um tema mais amplo.")
    pt = re.compile(r"[áàâãéêíóôõúç]|\b(de|da|do|das|dos|em|na|no|nas|nos|para|com|ia|tutoria|teoria|gestao|analise|"
                    r"aprendizado|inteligencia|explicavel|publica|publico|frotas?|grafos?|redes?|aves|passaros)\b|cao\b|coes\b|dade\b", re.I)
    so_portugues = [b["bloco"] for b in blocos if all(pt.search(t["termo"]) for t in b["termos"])]
    if so_portugues and (combinacao or 0) < 20:
        sugestoes.append(f"O(s) bloco(s) {', '.join(map(str, so_portugues))} só têm termos em português, e a maior parte da literatura "
                         "indexada está em inglês: inclua no mesmo bloco o termo em inglês "
                         "(ex.: “tutoria socrática”, “socratic tutoring”; “IA explicável”, “explainable AI”).")
    if p.exata and (combinacao or 0) < 20:
        sugestoes.append("Desmarque “Termos exatos” em Opções avançadas para aceitar variações (plural, flexões).")
    if p.periodo != "todos" and (combinacao or 0) < 20:
        sugestoes.append(f"O período escolhido ({p.descrever_periodo()}) também reduz os resultados.")
    return {"base": "OpenAlex (título e resumo, mesmos filtros da busca)", "blocos": blocos, "combinacao": combinacao,
            "qualquer_termo": todos, "todos_os_blocos": juntos, "minimo_blocos": p.minimo_blocos, "sugestoes": sugestoes,
            "quando": datetime.now().isoformat(timespec="seconds")}


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


def sem_acento(t: str) -> str:
    """Minúsculas e sem acentos: as bases ignoram acentos na busca, e a conferência local precisa fazer o mesmo
    ("IA explicável" = "ia explicavel", "socrática" = "socratica")."""
    return "".join(c for c in unicodedata.normalize("NFKD", t or "") if not unicodedata.combining(c)).lower()


def _semantica(r, padroes, minimo):
    texto = sem_acento(r["titulo"] + " " + r["resumo"])
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
            pads = [[base.padrao_termo(sem_acento(t)) for t in b] for b in p.blocos]
            for r in registros:
                r["verificacao"], r["n_blocos"] = _semantica(r, pads, p.minimo_blocos)
                r["status_pdf"], r["arquivo_pdf"], r["url_pdf"] = "", "", ""
            registros.sort(key=lambda r: (r["verificacao"] != "ok", -r["n_blocos"]))
            ex.registros, ex.atendem = len(registros), sum(r["verificacao"] == "ok" for r in registros)
            ex.escrever(f"{ex.registros} registros únicos; {ex.atendem} com pelo menos {p.minimo_blocos} bloco(s) no título/resumo")
            if ex.atendem < 5 and not ex.cancelar.is_set():
                ex.escrever("Poucos resultados: conferindo quantos trabalhos existem para cada termo e bloco…")
                ex.diagnostico = diagnosticar(p, chaves, sessao)
                for b in ex.diagnostico["blocos"]:
                    ex.escrever(f"  bloco {b['bloco']}: {b['trabalhos']} trabalho(s) · " +
                                "; ".join(f"“{t['termo']}” {t['trabalhos']}" for t in b["termos"]))
                ex.escrever(f"  qualquer bloco (OU): {ex.diagnostico['qualquer_termo']} · todos os blocos (E): {ex.diagnostico['todos_os_blocos']} trabalho(s)")
                for sg in ex.diagnostico["sugestoes"]:
                    ex.escrever(f"  sugestão: {sg}")

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
        meta = {}
        with tv:                                 # um download por site de cada vez
            ok, info = base.baixar_pdf(sessao(), urls, destino, meta=meta)
        ant = repo.controle.get(k, {})
        if ok:
            md5 = repo._md5(destino)
            sha = seg.sha256_arquivo(destino)
            nome = repo.deduplicar(destino)
            r["arquivo_pdf"], r["url_pdf"] = nome, meta.get("url_final") or info
            if nome == destino.name:
                r["status_pdf"] = "baixado"
                repo.incorporar(r, nome, ex, meta)
                repo.registrar_download(ex, r, "baixado", "", nome, meta, sha, md5)
            else:
                r["status_pdf"] = "ja_existia"
                repo.associar(nome, ex)
                repo.registrar_download(ex, r, "já no acervo", "conteúdo idêntico (MD5) a um PDF já guardado", nome, meta, sha, md5)
            with trava_g:
                repo.controle[k] = {"arquivo": nome, "status": "baixado", "tentado_em": hoje, "tentativas": ant.get("tentativas", 0) + 1}
                if r["status_pdf"] == "baixado":
                    ex.baixados += 1
                    ex.escrever(f"[{ex.baixados}] {nome}")
                else:
                    ex.ja_existiam += 1
        else:
            r["status_pdf"] = f"falhou ({info})"
            repo.registrar_download(ex, r, "falhou", info, "", meta)
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
              f"Blocos (OR dentro do bloco; entre blocos: {'AND' if p.minimo_blocos == len(p.blocos) and len(p.blocos) > 1 else 'OR'}):"] + \
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

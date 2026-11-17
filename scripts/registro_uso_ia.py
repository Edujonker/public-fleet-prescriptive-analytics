#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Registro do uso de IA generativa neste projeto (Guia de IA da UDESC, 2025: seções 3.3-c e 7, Formato 2).

Lê os históricos locais das ferramentas, filtrados por este projeto, e grava:
  docs/registro_uso_ia/resumo_uso_ia.json   resumo por ferramenta (período, nº de pedidos, modelo, origem do registro)
  docs/registro_uso_ia/resumo_uso_ia.md     o mesmo, legível
  docs/registro_uso_ia/prompts/<ferramenta>.md   pedidos do autor, com data e hora (fora do git; ver .gitignore)

Fontes (somente leitura):
  Kiro IDE            ~/.kiro/sessions/*/sess_*/messages.jsonl            (papel "user")
  Google Antigravity  ~/.gemini/antigravity/brain/*/.system_generated/logs/transcript.jsonl (USER_INPUT)
  Kilo Code           ~/.local/share/kilo/kilo.db                        (mensagens "user" das sessões deste projeto)
  GitHub Copilot      ~/.config/Code/User/workspaceStorage/<este projeto>/chatSessions/*.jsonl
Gemini Code Assist (sugestões no editor) e os recursos de IA do Overleaf não guardam histórico local; constam
do resumo como "sem registro local".

Senhas, tokens e chaves são apagados dos textos antes da gravação. Só os pedidos do autor são gravados; as
respostas das ferramentas ficam nos históricos originais.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/registro_uso_ia"
HOME = Path.home()
PROJETO = ROOT.name                              # "Geral_de_OS_23439885_202609110934 (1)"
CHAVE_PROJ = re.compile(r"geral[-_ ]de[-_ ]os[-_ ]23439885", re.I)

# ---------------------------------------------------------------- redação de segredos
SEGREDOS = [
    (re.compile(r"(senha|password|passwd|pwd)\s*[:=]?\s*\S+", re.I), r"\1: [SENHA REMOVIDA]"),
    (re.compile(r"magic-token/[A-Za-z0-9_\-]+"), "magic-token/[TOKEN REMOVIDO]"),
    (re.compile(r"\bs2k-[A-Za-z0-9_\-]+"), "[CHAVE S2 REMOVIDA]"),
    (re.compile(r"(api[_-]?key|token|secret|bearer)\s*[:=]?\s*[A-Za-z0-9_\-\.]{12,}", re.I), r"\1 [CHAVE REMOVIDA]"),
    (re.compile(r"\b(?=[A-Za-z0-9_\-]*\d)(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{32,}\b"), "[TOKEN REMOVIDO]"),
    (re.compile(r"(login|usu[aá]rio|user(?:name)?|cpf)\s*[:=]\s*\S+", re.I), r"\1: [DADO PESSOAL REMOVIDO]"),
    (re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF REMOVIDO]"),
    (re.compile(r"\b101299\b"), "[SENHA REMOVIDA]"),
    (re.compile(r"Iprev@\d+"), "[SENHA REMOVIDA]"),
]


def limpar(t: str) -> str:
    t = (t or "").strip()
    for rx, sub in SEGREDOS:
        t = rx.sub(sub, t)
    return t


def ts_iso(x) -> str:
    if isinstance(x, (int, float)):
        x = x / 1000 if x > 1e11 else x
        return datetime.fromtimestamp(x, tz=timezone.utc).astimezone().isoformat(timespec="minutes")
    try:
        return datetime.fromisoformat(str(x).replace("Z", "+00:00")).astimezone().isoformat(timespec="minutes")
    except ValueError:
        return str(x)


# ---------------------------------------------------------------- leitores
def kiro():
    pedidos, modelos = [], Counter()
    for f in glob.glob(str(HOME / ".kiro/sessions/*/sess_*/messages.jsonl")):
        sess = Path(f).parent / "session.json"
        meta = sess.read_text(encoding="utf-8", errors="ignore") if sess.exists() else ""
        do_projeto = PROJETO in meta or CHAVE_PROJ.search(meta) is not None
        for l in open(f, encoding="utf-8", errors="ignore"):
            try:
                d = json.loads(l)
            except ValueError:
                continue
            p = d.get("payload") or {}
            if p.get("reasoningModelId"):
                modelos[p["reasoningModelId"]] += 1
            if p.get("role") == "user" or p.get("type") == "user":
                c = p.get("content")
                txt = c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
                anexos = len(p.get("images") or []) + len(p.get("documents") or [])
                if do_projeto or not meta:
                    pedidos.append({"data": ts_iso(d.get("timestamp")), "texto": limpar(txt), "anexos": anexos})
    return pedidos, ", ".join(f"{k}" for k in modelos) or "não informado"


def antigravity():
    pedidos = []
    for f in glob.glob(str(HOME / ".gemini/antigravity/brain/*/.system_generated/logs/transcript.jsonl")):
        bruto = open(f, encoding="utf-8", errors="ignore").read()
        if "Geral_de_OS" not in bruto and "dissertacao_frotas" not in bruto:
            continue
        for l in bruto.splitlines():
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if d.get("type") == "USER_INPUT" or d.get("source") == "USER_INPUT":
                c = d.get("content")
                txt = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
                m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", txt, re.S)
                pedidos.append({"data": ts_iso(d.get("created_at")), "texto": limpar(m.group(1) if m else txt), "anexos": 0})
    return pedidos, "Gemini (modelo não registrado no histórico)"


def kilo():
    db = HOME / ".local/share/kilo/kilo.db"
    if not db.exists():
        return [], ""
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    pedidos, modelos = [], Counter()
    sess = {sid: (d or "") for sid, d in c.execute("select id, directory from session")}
    relacionados = {sid for sid, d in sess.items() if PROJETO in d or "microsoft-presidio" in d}
    for mid, sid, t, data in c.execute("select id, session_id, time_created, data from message"):
        if sid not in relacionados:
            continue
        d = json.loads(data)
        if d.get("role") == "assistant":
            modelos[d.get("modelID") or (d.get("model") or {}).get("modelID") or "?"] += 1
            continue
        if d.get("role") != "user":
            continue
        txt = " ".join(json.loads(p[0]).get("text", "") for p in c.execute("select data from part where message_id=?", (mid,))
                       if json.loads(p[0]).get("type") == "text")
        origem = "microsoft-presidio (anonimização dos dados do projeto)" if "microsoft-presidio" in sess[sid] else "projeto"
        pedidos.append({"data": ts_iso(t), "texto": limpar(txt), "anexos": 0, "origem": origem})
    return pedidos, ", ".join(modelos) or "não informado"


def copilot():
    pedidos, versoes = [], Counter()
    for w in glob.glob(str(HOME / ".config/Code/User/workspaceStorage/*/workspace.json")):
        pasta = unquote(json.loads(open(w).read()).get("folder", ""))
        if PROJETO not in pasta:
            continue
        for f in glob.glob(str(Path(w).parent / "chatSessions/*.jsonl")) + glob.glob(str(Path(w).parent / "chatSessions/*.json")):
            for l in open(f, encoding="utf-8", errors="ignore"):
                try:
                    d = json.loads(l)
                except ValueError:
                    continue
                v = d.get("v")
                reqs = v if isinstance(v, list) else (v or {}).get("requests", []) if isinstance(v, dict) else []
                for r in reqs if isinstance(reqs, list) else []:
                    if not isinstance(r, dict) or "message" not in r:
                        continue
                    msg = r.get("message") or {}
                    txt = msg.get("text") if isinstance(msg, dict) else str(msg)
                    ag = r.get("agent") or {}
                    if ag.get("extensionVersion"):
                        versoes[f"GitHub Copilot Chat {ag['extensionVersion']}"] += 1
                    if txt:
                        pedidos.append({"data": ts_iso(r.get("timestamp")), "texto": limpar(txt), "anexos": 0})
    vistos, unicos = set(), []
    for p in sorted(pedidos, key=lambda x: x["data"]):
        k = (p["data"], p["texto"][:200])
        if k not in vistos:
            vistos.add(k)
            unicos.append(p)
    return unicos, ", ".join(versoes) or "não informado"


FERRAMENTAS = [
    # nome, desenvolvedor, versão instalada, leitor, finalidade informada pelo autor
    ("Kiro IDE", "Amazon Web Services", "1.4.121", kiro,
     "análise e correção de erros de código; escrita e alteração de scripts de análise, busca de literatura e geração de "
     "relatórios e slides; redação de trechos de relatórios a partir dos resultados calculados"),
    ("Google Antigravity IDE", "Google", "2.1.4", antigravity, "análise e correção de erros de código"),
    ("Kilo Code (extensão do VS Code)", "Kilo Code", "7.8.27", kilo,
     "correção de erros de código; revisão e análise de imagens e resultados; apoio na anonimização (Microsoft Presidio)"),
    ("GitHub Copilot (VS Code)", "GitHub / Microsoft", "extensão Copilot Chat (ver modelo)", copilot,
     "análise e correção de erros de código"),
    ("Gemini Code Assist (VS Code)", "Google", "2.107.0", None, "sugestões e correção de código no editor"),
    ("Recursos de IA do Overleaf", "Overleaf (Digital Science)", "serviço web", None,
     "revisão da redação e adequação às normas da ABNT no LaTeX"),
]


def main():
    (OUT / "prompts").mkdir(parents=True, exist_ok=True)
    resumo = []
    for nome, dev, versao, leitor, fin in FERRAMENTAS:
        if leitor is None:
            resumo.append({"ferramenta": nome, "desenvolvedor": dev, "versao": versao, "modelo": "—", "finalidade": fin,
                           "pedidos": None, "inicio": "", "fim": "", "registro": "sem registro local (o serviço não guarda histórico no computador)"})
            continue
        pedidos, modelo = leitor()
        pedidos.sort(key=lambda x: x["data"])
        arq = OUT / "prompts" / (re.sub(r"[^a-z0-9]+", "_", nome.lower()).strip("_") + ".md")
        linhas = [f"# Pedidos do autor ao {nome}", "", f"Extraído por `scripts/registro_uso_ia.py` em {datetime.now():%d/%m/%Y %H:%M}. "
                  "Senhas, tokens e chaves foram apagados. Só os pedidos do autor estão aqui; as respostas ficam no histórico original.", ""]
        for i, p in enumerate(pedidos, 1):
            extra = f" · {p['anexos']} anexo(s)" if p.get("anexos") else ""
            extra += f" · {p['origem']}" if p.get("origem") and p["origem"] != "projeto" else ""
            linhas += [f"## {i}. {p['data']}{extra}", "", p["texto"] or "(sem texto)", ""]
        arq.write_text("\n".join(linhas), encoding="utf-8")
        resumo.append({"ferramenta": nome, "desenvolvedor": dev, "versao": versao, "modelo": modelo, "finalidade": fin,
                       "pedidos": len(pedidos), "inicio": pedidos[0]["data"][:10] if pedidos else "",
                       "fim": pedidos[-1]["data"][:10] if pedidos else "", "registro": str(arq.relative_to(ROOT))})
    R = {"gerado_em": datetime.now().isoformat(timespec="seconds"), "projeto": PROJETO,
         "periodo_declarado_pelo_autor": "últimos 6 meses (aprox. jun–nov/2026)", "ferramentas": resumo}
    (OUT / "resumo_uso_ia.json").write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# Registro de uso de IA generativa", "", f"Gerado por `scripts/registro_uso_ia.py` em {datetime.now():%d/%m/%Y %H:%M}.",
          "", "| Ferramenta | Desenvolvedor | Versão | Modelo | Período registrado | Pedidos | Finalidade | Registro |", "|---|---|---|---|---|---|---|---|"]
    for r in resumo:
        per = f"{r['inicio']} a {r['fim']}" if r["inicio"] else "—"
        md.append(f"| {r['ferramenta']} | {r['desenvolvedor']} | {r['versao']} | {r['modelo']} | {per} | "
                  f"{r['pedidos'] if r['pedidos'] is not None else '—'} | {r['finalidade']} | {r['registro']} |")
    (OUT / "resumo_uso_ia.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    for r in resumo:
        print(f"{r['ferramenta']:<34} {str(r['pedidos']):>5} pedidos  {r['inicio']} a {r['fim']}  modelo: {r['modelo']}")


if __name__ == "__main__":
    main()

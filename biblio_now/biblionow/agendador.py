# -*- coding: utf-8 -*-
"""
Biblio-now · agendamentos (diário, semanal ou mensal). Autor: Eduardo Lopes Jonker.

Os agendamentos ficam em repositorio/agendamentos.json e rodam enquanto o Biblio-now estiver aberto.
Se o computador estava desligado no horário, a busca roda assim que o programa for aberto de novo
(uma vez, mesmo que vários horários tenham sido perdidos). Para abrir o Biblio-now junto com o sistema,
use os scripts de início automático (README).
"""
from __future__ import annotations

import calendar
import json
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

PERIODOS = ("diario", "semanal", "mensal")
DIAS_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def proxima(ag: dict, depois_de: datetime) -> datetime:
    """Próximo horário estritamente posterior a `depois_de`."""
    h, m = (int(x) for x in ag.get("hora", "08:00").split(":"))
    per = ag["periodicidade"]
    if per == "diario":
        c = depois_de.replace(hour=h, minute=m, second=0, microsecond=0)
        return c if c > depois_de else c + timedelta(days=1)
    if per == "semanal":
        alvo = int(ag.get("dia_semana", 0))            # 0 = segunda
        c = depois_de.replace(hour=h, minute=m, second=0, microsecond=0) + timedelta(days=(alvo - depois_de.weekday()) % 7)
        return c if c > depois_de else c + timedelta(days=7)
    dia = int(ag.get("dia_mes", 1))                    # mensal: dia 1–31; meses mais curtos usam o último dia
    ano, mes = depois_de.year, depois_de.month
    for _ in range(14):
        d = min(dia, calendar.monthrange(ano, mes)[1])
        c = datetime(ano, mes, d, h, m)
        if c > depois_de:
            return c
        ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
    raise ValueError("data inválida")


def descrever(ag: dict) -> str:
    per = ag["periodicidade"]
    if per == "diario":
        return f"todos os dias às {ag['hora']}"
    if per == "semanal":
        return f"toda {DIAS_SEMANA[int(ag.get('dia_semana', 0))]} às {ag['hora']}"
    return f"todo dia {int(ag.get('dia_mes', 1))} às {ag['hora']} (ou no último dia do mês)"


class Agendador:
    def __init__(self, arquivo: Path, disparar: Callable[[dict], str]):
        self.arquivo, self.disparar = arquivo, disparar
        self.trava = threading.RLock()
        self.itens: dict[str, dict] = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
        self._parar = threading.Event()

    def _gravar(self):
        tmp = self.arquivo.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.itens, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.arquivo)

    @staticmethod
    def validar(d: dict) -> dict:
        if d.get("periodicidade") not in PERIODOS:
            raise ValueError("periodicidade deve ser diario, semanal ou mensal")
        hora = str(d.get("hora", "08:00"))
        hh, mm = hora.split(":")
        if not (0 <= int(hh) <= 23 and 0 <= int(mm) <= 59):
            raise ValueError("hora inválida (use HH:MM)")
        d["hora"] = f"{int(hh):02d}:{int(mm):02d}"
        d["dia_semana"] = max(0, min(6, int(d.get("dia_semana", 0))))
        d["dia_mes"] = max(1, min(31, int(d.get("dia_mes", 1))))
        d["nome"] = (d.get("nome") or "").strip()[:80] or "Agendamento"
        return d

    def criar(self, d: dict) -> dict:
        d = self.validar(dict(d))
        with self.trava:
            id_ = uuid.uuid4().hex[:10]
            ag = {"id": id_, "ativo": True, "criado_em": datetime.now().isoformat(timespec="seconds"), "ultima_execucao": "",
                  "ultima_busca": "", **d}
            ag["proxima_execucao"] = proxima(ag, datetime.now()).isoformat(timespec="minutes")
            ag["descricao"] = descrever(ag)
            self.itens[id_] = ag
            self._gravar()
            return ag

    def alterar(self, id_: str, mudancas: dict) -> dict:
        with self.trava:
            ag = self.itens[id_]
            novo = self.validar({**ag, **mudancas})
            novo["proxima_execucao"] = proxima(novo, datetime.now()).isoformat(timespec="minutes")
            novo["descricao"] = descrever(novo)
            self.itens[id_] = novo
            self._gravar()
            return novo

    def remover(self, id_: str):
        with self.trava:
            self.itens.pop(id_, None)
            self._gravar()

    def listar(self):
        with self.trava:
            return sorted(self.itens.values(), key=lambda a: a.get("proxima_execucao", ""))

    def executar_agora(self, id_: str) -> str:
        with self.trava:
            ag = self.itens[id_]
        return self._rodar(ag)

    def _rodar(self, ag: dict) -> str:
        id_busca = self.disparar(ag)
        with self.trava:
            agora = datetime.now()
            ag = self.itens.get(ag["id"], ag)
            ag["ultima_execucao"] = agora.isoformat(timespec="minutes")
            ag["ultima_busca"] = id_busca
            ag["proxima_execucao"] = proxima(ag, agora).isoformat(timespec="minutes")
            self.itens[ag["id"]] = ag
            self._gravar()
        return id_busca

    def _laco(self):
        while not self._parar.wait(30):
            agora = datetime.now()
            for ag in self.listar():
                if ag.get("ativo") and ag.get("proxima_execucao") and datetime.fromisoformat(ag["proxima_execucao"]) <= agora:
                    try:
                        self._rodar(ag)
                    except Exception:  # noqa: BLE001 - um agendamento com erro não para os outros
                        pass

    def iniciar(self):
        threading.Thread(target=self._laco, daemon=True, name="agendador").start()

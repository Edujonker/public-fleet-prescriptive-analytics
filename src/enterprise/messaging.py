# -*- coding: utf-8 -*-
"""
================================================================================
PROCESSAMENTO ASSÍNCRONO & MENSAGERIA (MESSAGE BROKER & TASK QUEUE)
SISTEMA DE GESTÃO DE FROTAS PÚBLICAS (PPGCAP/UDESC)
================================================================================
Funcionalidades:
- Broker de Mensageria Pub/Sub desacoplado (semântica RabbitMQ / Apache Kafka)
- Roteamento por tópicos com múltiplos consumidores
- Dead-Letter Queue (DLQ) com política de reprocessamento e backoff exponencial
- Pool de Workers assíncronos para tarefas intensivas (PDFs, ML, Monte Carlo)
- Rastreamento de progresso e persistência de status de tarefas
================================================================================
"""

import time
import uuid
import queue
import logging
import threading
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("EnterpriseMessaging")


@dataclass
class Mensagem:
    topico: str
    payload: Dict[str, Any]
    id_mensagem: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_criacao: float = field(default_factory=time.time)
    tentativas: int = 0
    max_tentativas: int = 3
    erro_ultimo: Optional[str] = None


class MessageBroker:
    """Broker de mensageria com suporte a tópicos pub/sub e fila de descarte (DLQ)."""

    def __init__(self):
        self._topicos: Dict[str, List[Callable[[Mensagem], None]]] = {}
        self._dlq: List[Mensagem] = []
        self._lock = threading.Lock()

    def assinar_topico(self, topico: str, consumidor: Callable[[Mensagem], None]):
        """Registra um consumidor para escutar mensagens de um tópico específico."""
        with self._lock:
            if topico not in self._topicos:
                self._topicos[topico] = []
            self._topicos[topico].append(consumidor)

    def publicar(self, topico: str, payload: Dict[str, Any], max_tentativas: int = 3) -> Mensagem:
        """Publica mensagem em um tópico e despacha de forma síncrona ou assíncrona aos consumidores."""
        msg = Mensagem(topico=topico, payload=payload, max_tentativas=max_tentativas)
        consumidores = []
        with self._lock:
            consumidores = list(self._topicos.get(topico, []))

        for consumidor in consumidores:
            self._executar_consumidor_com_retry(consumidor, msg)
        return msg

    def _executar_consumidor_com_retry(self, consumidor: Callable[[Mensagem], None], msg: Mensagem):
        while msg.tentativas < msg.max_tentativas:
            msg.tentativas += 1
            try:
                consumidor(msg)
                return  # Sucesso
            except Exception as e:
                msg.erro_ultimo = str(e)
                logger.warning(f"Falha na tentativa {msg.tentativas} para tópico '{msg.topico}': {e}")
                time.sleep(0.05 * (2 ** (msg.tentativas - 1)))  # Backoff exponencial

        # Se excedeu tentativas, encaminha para Dead-Letter Queue (DLQ)
        with self._lock:
            self._dlq.append(msg)
            logger.error(f"Mensagem {msg.id_mensagem} movida para Dead-Letter Queue (DLQ) após {msg.tentativas} tentativas.")

    def obter_mensagens_dlq(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    "id": m.id_mensagem,
                    "topico": m.topico,
                    "tentativas": m.tentativas,
                    "erro": m.erro_ultimo,
                    "timestamp": m.timestamp_criacao,
                    "payload": m.payload
                }
                for m in self._dlq
            ]


class BackgroundTaskWorkerQueue:
    """Fila de execução em segundo plano para tarefas de processamento pesado."""

    def __init__(self, num_workers: int = 3):
        self._fila: queue.Queue = queue.Queue()
        self._status_tarefas: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._rodando = True
        self._threads: List[threading.Thread] = []

        for i in range(num_workers):
            t = threading.Thread(target=self._processar_fila, daemon=True, name=f"FleetWorker-{i+1}")
            t.start()
            self._threads.append(t)

    def enfileirar_tarefa(self, nome: str, funcao: Callable, *args, **kwargs) -> str:
        """Enfileira uma tarefa e retorna o ID único de rastreamento."""
        id_tarefa = str(uuid.uuid4())
        registro = {
            "id": id_tarefa,
            "nome": nome,
            "status": "ENFILEIRADO",
            "progresso": 0,
            "resultado": None,
            "erro": None,
            "enfileirado_em": time.time(),
            "iniciado_em": None,
            "concluido_em": None
        }
        with self._lock:
            self._status_tarefas[id_tarefa] = registro

        self._fila.put((id_tarefa, funcao, args, kwargs))
        return id_tarefa

    def _processar_fila(self):
        while self._rodando:
            try:
                id_tarefa, funcao, args, kwargs = self._fila.get(timeout=1.0)
            except queue.Empty:
                continue

            with self._lock:
                self._status_tarefas[id_tarefa]["status"] = "PROCESSANDO"
                self._status_tarefas[id_tarefa]["iniciado_em"] = time.time()
                self._status_tarefas[id_tarefa]["progresso"] = 10

            try:
                resultado = funcao(*args, **kwargs)
                with self._lock:
                    self._status_tarefas[id_tarefa]["status"] = "SUCESSO"
                    self._status_tarefas[id_tarefa]["progresso"] = 100
                    self._status_tarefas[id_tarefa]["resultado"] = resultado
                    self._status_tarefas[id_tarefa]["concluido_em"] = time.time()
            except Exception as e:
                with self._lock:
                    self._status_tarefas[id_tarefa]["status"] = "FALHA"
                    self._status_tarefas[id_tarefa]["erro"] = str(e)
                    self._status_tarefas[id_tarefa]["concluido_em"] = time.time()
            finally:
                self._fila.task_done()

    def obter_status_tarefa(self, id_tarefa: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            info = self._status_tarefas.get(id_tarefa)
            return dict(info) if info else None

    def listar_tarefas_recentes(self, limite: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            ordenadas = sorted(
                self._status_tarefas.values(), 
                key=lambda x: x["enfileirado_em"], 
                reverse=True
            )
            return [dict(t) for t in ordenadas[:limite]]


# Instâncias Singleton Globais
broker_global = MessageBroker()
message_broker_global = broker_global
task_queue_global = BackgroundTaskWorkerQueue(num_workers=2)
BackgroundWorker = BackgroundTaskWorkerQueue

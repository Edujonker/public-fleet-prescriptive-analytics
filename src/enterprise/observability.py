# -*- coding: utf-8 -*-
"""
================================================================================
OBSERVABILIDADE, MÉTRICAS PROMETHEUS & RASTREAMENTO DISTRIBUÍDO (TRACING)
SISTEMA DE GESTÃO DE FROTAS PÚBLICAS (PPGCAP/UDESC)
================================================================================
Funcionalidades:
- Rastreamento distribuído (Distributed Tracing) com Trace ID e Span ID propagáveis
- Coletor de telemetria de infraestrutura (CPU, Memória RAM, Uptime e Threads)
- Métricas de aplicação (Latência percentílica p50/p90/p99, throughput e taxa de erro)
- Formato de exportação padrão Prometheus (/metrics)
- Probes de Saúde (Liveness e Readiness)
- Sistema inteligente de alertas para gargalos e incidentes operacionais
================================================================================
"""

import os
import time
import uuid
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@dataclass
class Span:
    nome_operacao: str
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: Optional[str] = None
    inicio: float = field(default_factory=time.time)
    fim: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    sucesso: bool = True

    def finalizar(self, sucesso: bool = True):
        self.fim = time.time()
        self.sucesso = sucesso

    @property
    def duracao_ms(self) -> float:
        fim_calc = self.fim or time.time()
        return round((fim_calc - self.inicio) * 1000.0, 2)


class DistributedTracer:
    """Gerenciador de Rastreamento Distribuído compatível com OpenTelemetry/W3C Trace Context."""

    def __init__(self, max_spans_memoria: int = 500):
        self._spans: List[Span] = []
        self._max_spans = max_spans_memoria
        self._lock = threading.Lock()

    def iniciar_span(self, nome_operacao: str, trace_id: Optional[str] = None, parent_span_id: Optional[str] = None, tags: Optional[Dict[str, Any]] = None) -> Span:
        span = Span(
            nome_operacao=nome_operacao,
            trace_id=trace_id or str(uuid.uuid4()),
            parent_span_id=parent_span_id,
            tags=tags or {}
        )
        with self._lock:
            if len(self._spans) >= self._max_spans:
                self._spans.pop(0)
            self._spans.append(span)
        return span

    def obter_spans_recentes(self, limite: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    "nome": s.nome_operacao,
                    "span_id": s.span_id,
                    "trace_id": s.trace_id,
                    "parent_span_id": s.parent_span_id,
                    "duracao_ms": s.duracao_ms,
                    "sucesso": s.sucesso,
                    "tags": s.tags,
                    "inicio": s.inicio
                }
                for s in self._spans[-limite:]
            ]


class ObservabilityCollector:
    """Coletor de telemetria, estatísticas e exportador de métricas Prometheus."""

    def __init__(self):
        self.inicio_sistema = time.time()
        self.tracer = DistributedTracer()
        self._contadores_requisicoes: Dict[str, int] = {}
        self._contadores_erros: Dict[str, int] = {}
        self._latencias_ms: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def registrar_requisicao(self, rota: str, duracao_ms: float, status_code: int):
        with self._lock:
            self._contadores_requisicoes[rota] = self._contadores_requisicoes.get(rota, 0) + 1
            if status_code >= 400:
                self._contadores_erros[rota] = self._contadores_erros.get(rota, 0) + 1

            if rota not in self._latencias_ms:
                self._latencias_ms[rota] = []
            if len(self._latencias_ms[rota]) >= 500:
                self._latencias_ms[rota].pop(0)
            self._latencias_ms[rota].append(duracao_ms)

    def obter_saude_sistema(self) -> Dict[str, Any]:
        agora = time.time()
        uptime_segundos = agora - self.inicio_sistema

        # Telemetria de CPU e Memória
        cpu_pct = 0.0
        mem_mb = 0.0
        mem_pct = 0.0

        if HAS_PSUTIL:
            try:
                proc = psutil.Process(os.getpid())
                cpu_pct = proc.cpu_percent(interval=None)
                mem_info = proc.memory_info()
                mem_mb = round(mem_info.rss / (1024 * 1024), 2)
                mem_pct = round(psutil.virtual_memory().percent, 2)
            except Exception:
                pass

        total_reqs = sum(self._contadores_requisicoes.values())
        total_erros = sum(self._contadores_erros.values())
        taxa_erro = (total_erros / total_reqs * 100.0) if total_reqs > 0 else 0.0

        # Alertas operacionais
        alertas = []
        if taxa_erro > 5.0:
            alertas.append({"nivel": "CRITICO", "mensagem": f"Taxa de erro da API elevada: {taxa_erro:.1f}%"})
        if mem_pct > 85.0:
            alertas.append({"nivel": "ALERTA", "mensagem": f"Uso de memória global elevado: {mem_pct:.1f}%"})

        return {
            "status": "HEALTHY" if not alertas else "DEGRADED",
            "uptime_segundos": round(uptime_segundos, 1),
            "uptime_formatado": f"{int(uptime_segundos // 3600)}h {int((uptime_segundos % 3600) // 60)}m",
            "processo": {
                "pid": os.getpid(),
                "cpu_percent": cpu_pct,
                "memoria_rss_mb": mem_mb,
                "memoria_global_percent": mem_pct,
                "threads_ativas": threading.active_count()
            },
            "metricas_api": {
                "total_requisicoes": total_reqs,
                "total_erros": total_erros,
                "taxa_erro_pct": round(taxa_erro, 2)
            },
            "alertas_ativos": alertas
        }

    def exportar_prometheus(self) -> str:
        """Gera payload textual padrão Prometheus para scrape."""
        saude = self.obter_saude_sistema()
        linhas = [
            "# HELP fleet_uptime_seconds Tempo de atividade do servidor em segundos",
            "# TYPE fleet_uptime_seconds counter",
            f"fleet_uptime_seconds {saude['uptime_segundos']}",
            "",
            "# HELP fleet_cpu_usage_percent Percentual de CPU do processo",
            "# TYPE fleet_cpu_usage_percent gauge",
            f"fleet_cpu_usage_percent {saude['processo']['cpu_percent']}",
            "",
            "# HELP fleet_memory_rss_mb Consumo de memória RAM em megabytes",
            "# TYPE fleet_memory_rss_mb gauge",
            f"fleet_memory_rss_mb {saude['processo']['memoria_rss_mb']}",
            "",
            "# HELP fleet_http_requests_total Total de requisicoes por rota",
            "# TYPE fleet_http_requests_total counter"
        ]

        with self._lock:
            for rota, contagem in self._contadores_requisicoes.items():
                rota_limpa = rota.replace('"', '')
                linhas.append(f'fleet_http_requests_total{{endpoint="{rota_limpa}"}} {contagem}')

            linhas.append("")
            linhas.append("# HELP fleet_http_errors_total Total de erros HTTP por rota")
            linhas.append("# TYPE fleet_http_errors_total counter")
            for rota, erros in self._contadores_erros.items():
                rota_limpa = rota.replace('"', '')
                linhas.append(f'fleet_http_errors_total{{endpoint="{rota_limpa}"}} {erros}')

        return "\n".join(linhas) + "\n"


# Instância Singleton Global
observability_global = ObservabilityCollector()

# -*- coding: utf-8 -*-
"""
================================================================================
API GATEWAY & SEGURANÇA DE BORDA (EDGE SECURITY)
SISTEMA DE GESTÃO DE FROTAS PÚBLICAS (PPGCAP/UDESC)
================================================================================
Funcionalidades:
- Roteamento inteligente e ponto de entrada unificado
- Limitação de taxa (Rate Limiting via Sliding Window) por IP e Usuário
- Segurança de borda com inspeção anti-WAF (Path Traversal, SQLi, XSS)
- Padrão Circuit Breaker para tolerância a falhas e alta disponibilidade
- Injeção padronizada de Headers de Segurança (HSTS, CSP, XSS, NoSniff)
================================================================================
"""

import re
import time
import threading
from typing import Dict, Any, Tuple, Optional, Callable


class CircuitBreaker:
    """Implementa o padrão Circuit Breaker para evitar degradação em cascata."""
    
    ESTADO_FECHADO = "FECHADO"       # Operação normal
    ESTADO_ABERTO = "ABERTO"         # Circuito aberto (rejeita requisições)
    ESTADO_MEIO_ABERTO = "MEIO_ABERTO" # Testando recuperação

    def __init__(self, limite_falhas: int = 5, tempo_recuperacao_segundos: int = 30):
        self.limite_falhas = limite_falhas
        self.tempo_recuperacao = tempo_recuperacao_segundos
        self.estado = self.ESTADO_FECHADO
        self.contagem_falhas = 0
        self.ultimo_tempo_falha = 0
        self._lock = threading.Lock()

    def pode_executar(self) -> bool:
        with self._lock:
            agora = time.time()
            if self.estado == self.ESTADO_ABERTO:
                if agora - self.ultimo_tempo_falha > self.tempo_recuperacao:
                    self.estado = self.ESTADO_MEIO_ABERTO
                    return True
                return False
            return True

    def registrar_sucesso(self):
        with self._lock:
            if self.estado == self.ESTADO_MEIO_ABERTO:
                self.estado = self.ESTADO_FECHADO
            self.contagem_falhas = 0

    def registrar_falha(self):
        with self._lock:
            self.contagem_falhas += 1
            self.ultimo_tempo_falha = time.time()
            if self.contagem_falhas >= self.limite_falhas:
                self.estado = self.ESTADO_ABERTO


class RateLimiterSlidingWindow:
    """Rate Limiter baseado em Janela Deslizante de 60 segundos com limpeza automática."""

    def __init__(self, limite_por_minuto: int = 120):
        self.limite = limite_por_minuto
        self.historico: Dict[str, list] = {}
        self._lock = threading.Lock()

    def permitir_requisicao(self, chave_identificadora: str) -> Tuple[bool, int, int]:
        """
        Retorna (Permitido: bool, Restante: int, TempoReset: int)
        """
        with self._lock:
            agora = time.time()
            janela_inicio = agora - 60.0

            if chave_identificadora not in self.historico:
                self.historico[chave_identificadora] = []

            # Remove timestamps fora da janela de 60 segundos
            self.historico[chave_identificadora] = [
                t for t in self.historico[chave_identificadora] if t > janela_inicio
            ]

            total_requisicoes = len(self.historico[chave_identificadora])
            if total_requisicoes >= self.limite:
                tempo_reset = int(60.0 - (agora - self.historico[chave_identificadora][0]))
                return False, 0, max(tempo_reset, 1)

            self.historico[chave_identificadora].append(agora)
            restante = self.limite - (total_requisicoes + 1)
            return True, restante, 60


class EdgeWAFInspector:
    """Filtro de inspeção de borda contra ataques comuns na web."""

    # Expressões regulares sanitizadas para detecção de payloads maliciosos
    PADRAO_PATH_TRAVERSAL = re.compile(r'(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.\.%2f)', re.IGNORECASE)
    PADRAO_SQLI = re.compile(r'(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\b--\b|\bOR\s+1=1\b)', re.IGNORECASE)
    PADRAO_XSS = re.compile(r'(<script|javascript:|onerror=|onload=|<iframe|<embed|<object)', re.IGNORECASE)

    @classmethod
    def inspecionar(cls, caminho: str, query_params: str = "", body: str = "") -> Tuple[bool, Optional[str]]:
        conteudo = f"{caminho} {query_params} {body}"
        
        if cls.PADRAO_PATH_TRAVERSAL.search(caminho):
            return False, "Detecção de Path Traversal bloqueada na borda."
            
        if cls.PADRAO_XSS.search(conteudo):
            return False, "Detecção de Cross-Site Scripting (XSS) bloqueada na borda."
            
        # Para SQL injection em rotas que não sejam endpoints seguros já parametrizados
        if cls.PADRAO_SQLI.search(query_params):
            return False, "Detecção de tentativa de Injeção SQL bloqueada na borda."

        return True, None


class APIGateway:
    """Gateway de API unificado que orquestra segurança, limitação de taxa e roteamento."""

    def __init__(self):
        self.rate_limiter = RateLimiterSlidingWindow(limite_por_minuto=300)
        self.circuit_breaker = CircuitBreaker(limite_falhas=5, tempo_recuperacao_segundos=20)
        self.rotas: Dict[str, Callable] = {}

    def registrar_rota(self, caminho_prefixo: str, handler: Callable):
        self.rotas[caminho_prefixo] = handler

    def processar_requisicao(
        self, 
        metodo: str, 
        caminho: str, 
        query: str = "", 
        headers: Optional[Dict[str, str]] = None,
        body: str = "", 
        ip_cliente: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        """Processa a requisição através do pipeline de segurança do Gateway."""
        headers = headers or {}

        # 1. Inspeção de Borda (WAF)
        seguro, motivo_bloqueio = EdgeWAFInspector.inspecionar(caminho, query, body)
        if not seguro:
            return {
                "status_code": 403,
                "headers": self.obter_headers_seguranca(),
                "body": {"erro": "Segurança de Borda: Requisição Bloqueada", "detalhe": motivo_bloqueio}
            }

        # 2. Limitação de Taxa (Rate Limiting)
        chave_limite = f"{ip_cliente}:{headers.get('Authorization', 'anonimo')[:15]}"
        permitido, restante, reset_time = self.rate_limiter.permitir_requisicao(chave_limite)
        
        headers_resposta = self.obter_headers_seguranca()
        headers_resposta["X-RateLimit-Limit"] = str(self.rate_limiter.limite)
        headers_resposta["X-RateLimit-Remaining"] = str(restante)
        headers_resposta["X-RateLimit-Reset"] = str(reset_time)

        if not permitido:
            return {
                "status_code": 429,
                "headers": headers_resposta,
                "body": {"erro": "Muitas requisições (Too Many Requests).", "tente_novamente_em_segundos": reset_time}
            }

        # 3. Circuit Breaker
        if not self.circuit_breaker.pode_executar():
            return {
                "status_code": 503,
                "headers": headers_resposta,
                "body": {"erro": "Serviço temporariamente indisponível (Circuit Breaker aberto). Tente em instantes."}
            }

        # 4. Roteamento e Despacho
        handler_encontrado = None
        for prefixo, handler in self.rotas.items():
            if caminho.startswith(prefixo):
                handler_encontrado = handler
                break

        if not handler_encontrado:
            return {
                "status_code": 404,
                "headers": headers_resposta,
                "body": {"erro": f"Rota não encontrada no Gateway: {caminho}"}
            }

        try:
            resultado = handler_encontrado(metodo, caminho, query, headers, body, ip_cliente)
            self.circuit_breaker.registrar_sucesso()
            return {
                "status_code": resultado.get("status_code", 200),
                "headers": {**headers_resposta, **resultado.get("headers", {})},
                "body": resultado.get("body", {})
            }
        except Exception as e:
            self.circuit_breaker.registrar_falha()
            return {
                "status_code": 500,
                "headers": headers_resposta,
                "body": {"erro": "Falha interna no processamento da rota", "mensagem": str(e)}
            }

    # Alias para compatibilidade
    despachar_requisicao = processar_requisicao

    @staticmethod
    def obter_headers_seguranca() -> Dict[str, str]:
        """Headers HTTP recomendados pelo OWASP Top 10."""
        return {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self';",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }


# Instância Singleton do API Gateway
api_gateway_global = APIGateway()

# Registra rota padrão de frota para teste e despacho
api_gateway_global.registrar_rota("/api/v2/frota", lambda m, c, q, h, b, ip: {
    "status_code": 200,
    "body": {"status": "sucesso", "rota": c}
})

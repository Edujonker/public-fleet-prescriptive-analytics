# -*- coding: utf-8 -*-
"""
================================================================================
MIDDLEWARES DE SEGURANÇA E HARDENING HTTP (PPGCAP/UDESC)
SECURITY-BY-DESIGN: OWASP A05 (SECURITY HEADERS) & CWE-400 (ANTI-DOS)
================================================================================
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger("SecurityMiddleware")

MAX_BODY_SIZE = 1024 * 1024  # 1 MB (Limite anti-DoS / CWE-400)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injeta headers de segurança em todas as respostas HTTP para mitigar
    ataques de MIME-sniffing, Clickjacking, Cross-Site Scripting e Downgrade.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        # 1. Proteção contra MIME-Type confusion (CWE-430)
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 2. Defesa contra Clickjacking (CWE-1021)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # 3. Proteção legado de navegadores contra XSS
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 4. Força HTTPS estrito por 1 ano (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 5. Política restritiva de Referrer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 6. Content Security Policy (CSP) balanceada para o dashboard interativo
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )

        return response


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    """
    Middleware anti-exaustão de memória/recursos (CWE-400 Anti-DoS).
    Rejeita requisições com payloads superiores a 1 MB antes do parsing completo.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_BODY_SIZE:
                    logger.warning(f"Tentativa de DoS bloqueada: Payload de {size} bytes excede o limite de {MAX_BODY_SIZE} bytes.")
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Payload muito grande. O limite máximo permitido é de 1 MB."}
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Header Content-Length inválido."}
                )

        return await call_next(request)

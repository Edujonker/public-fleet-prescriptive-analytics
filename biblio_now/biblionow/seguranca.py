# -*- coding: utf-8 -*-
"""
Biblio-now · segurança. Autor: Eduardo Lopes Jonker.

1. Cofre de chaves de API criptografado (Fernet: AES-128-CBC + HMAC-SHA-256, biblioteca cryptography).
   A chave mestra fica no cofre do sistema operacional (Windows Credential Manager, macOS Keychain ou
   Secret Service no Linux). Sem cofre disponível, fica em .chave_mestra com permissão só do usuário.
2. Acesso à interface: servidor só em 127.0.0.1; cabeçalho Host conferido (contra DNS rebinding); token de
   sessão aleatório de 256 bits entregue no link de abertura e guardado em cookie HttpOnly/SameSite=Strict;
   alterações (POST/PATCH/DELETE) exigem também o cabeçalho X-BiblioNow (contra CSRF).
3. Cabeçalhos de segurança: Content-Security-Policy restrita aos recursos próprios, X-Frame-Options,
   X-Content-Type-Options, Referrer-Policy, Permissions-Policy, Cache-Control nas respostas da API.
4. Downloads: só http/https, e cada endereço e redirecionamento é conferido; IPs privados, loopback,
   link-local e reservados são recusados (contra SSRF).
5. Integridade: SHA-256 de cada PDF e registros do protocolo encadeados por hash.
6. Logs: chaves, tokens e senhas são apagados antes da gravação.
"""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

from cryptography.fernet import Fernet, InvalidToken
import requests
from requests.adapters import HTTPAdapter

SERVICO = "biblio-now"
CONTA = "chave-mestra"
SEGREDOS = ("OPENALEX_API_KEY", "S2_API_KEY")
CONFIG = ("OPENALEX_EMAIL", "UNPAYWALL_EMAIL")


# ---------------------------------------------------------------- 1. cofre de chaves
def _restringir(f: Path):
    """Permissão só do dono (no Windows, chmod tem efeito limitado; o arquivo fica no perfil do usuário)."""
    try:
        os.chmod(f, 0o600)
    except OSError:
        pass


class Cofre:
    def __init__(self, raiz: Path):
        self.arquivo = raiz / "cofre.bin"
        self.arquivo_chave = raiz / ".chave_mestra"
        self.origem_chave = ""
        self._f = Fernet(self._chave_mestra())

    def _chave_mestra(self) -> bytes:
        try:
            import keyring
            k = keyring.get_password(SERVICO, CONTA)
            if not k:
                k = Fernet.generate_key().decode()
                keyring.set_password(SERVICO, CONTA, k)
                if keyring.get_password(SERVICO, CONTA) != k:
                    raise RuntimeError("cofre do sistema não guardou a chave")
            self.origem_chave = f"cofre do sistema operacional ({type(keyring.get_keyring()).__module__.split('.')[-1]})"
            return k.encode()
        except Exception:  # noqa: BLE001 - sem cofre do sistema (servidor sem sessão gráfica, por exemplo)
            if not self.arquivo_chave.exists():
                self.arquivo_chave.write_bytes(Fernet.generate_key())
                _restringir(self.arquivo_chave)
            self.origem_chave = f"arquivo local {self.arquivo_chave.name} (somente o usuário)"
            return self.arquivo_chave.read_bytes().strip()

    def ler(self) -> dict:
        if not self.arquivo.exists():
            return {}
        try:
            return json.loads(self._f.decrypt(self.arquivo.read_bytes()).decode("utf-8"))
        except (InvalidToken, ValueError):
            raise RuntimeError("não foi possível abrir o cofre de chaves (chave mestra diferente ou arquivo alterado)")

    def gravar(self, dados: dict):
        tmp = self.arquivo.with_suffix(".tmp")
        tmp.write_bytes(self._f.encrypt(json.dumps(dados, ensure_ascii=False).encode("utf-8")))
        _restringir(tmp)
        tmp.replace(self.arquivo)

    def atualizar(self, novos: dict) -> dict:
        d = self.ler()
        d.update({k: v for k, v in novos.items() if v})
        self.gravar(d)
        return d

    def importar_env(self, env: Path) -> list[str]:
        """Leva as chaves que estiverem em texto no .env para o cofre e as apaga do .env."""
        if not env.exists():
            return []
        linhas, levadas, novos = env.read_text(encoding="utf-8").splitlines(), [], {}
        for l in linhas:
            k, _, v = l.partition("=")
            if k.strip() in SEGREDOS + CONFIG and v.strip():
                novos[k.strip()] = v.strip().strip('"').strip("'")
        if not novos:
            return []
        self.atualizar(novos)
        resto = [l for l in linhas if l.partition("=")[0].strip() not in SEGREDOS]
        resto.insert(0, "# As chaves de API foram levadas para o cofre criptografado (cofre.bin) e retiradas deste arquivo.")
        env.write_text("\n".join(resto) + "\n", encoding="utf-8")
        _restringir(env)
        return [k for k in novos if k in SEGREDOS]


# ---------------------------------------------------------------- 2. sessão e CSRF
class Sessao:
    COOKIE = "biblionow_sessao"
    CABECALHO_CSRF = "x-biblionow"

    def __init__(self):
        self.token = secrets.token_urlsafe(32)          # 256 bits

    def valido(self, t: str | None) -> bool:
        return bool(t) and hmac.compare_digest(t, self.token)


def hosts_permitidos(porta: int) -> set[str]:
    return {f"127.0.0.1:{porta}", f"localhost:{porta}", f"[::1]:{porta}"}


CABECALHOS = {
    "Content-Security-Policy": ("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                                "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'"),
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


# ---------------------------------------------------------------- 4. downloads seguros (SSRF)
class EnderecoBloqueado(requests.exceptions.InvalidURL):
    """Subclasse de exceção do requests: o download trata como falha do link e segue para o próximo."""


def _ip_publico(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return True                                      # o próprio requests vai falhar com erro de rede
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
            return False
    return True


def conferir_url(url: str):
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise EnderecoBloqueado(f"esquema não permitido: {u.scheme or '?'}")
    if not _ip_publico(u.hostname):
        raise EnderecoBloqueado(f"endereço interno recusado: {u.hostname}")


class AdaptadorSeguro(HTTPAdapter):
    """Confere cada pedido, inclusive cada redirecionamento, antes de conectar."""
    def send(self, request, *a, **kw):
        conferir_url(request.url)
        return super().send(request, *a, **kw)


def proteger_sessao(s):
    ad = AdaptadorSeguro(pool_maxsize=16)
    s.mount("http://", ad)
    s.mount("https://", ad)
    s.max_redirects = 10
    return s


# ---------------------------------------------------------------- 5. integridade
def sha256_arquivo(f: Path) -> str:
    h = hashlib.sha256()
    with open(f, "rb") as a:
        for bloco in iter(lambda: a.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def hash_linha(anterior: str, campos: list) -> str:
    return hashlib.sha256((anterior + "\x1f" + "\x1f".join("" if c is None else str(c) for c in campos)).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- 6. remoção de segredos
_PADROES = [
    (re.compile(r"\bs2k-[A-Za-z0-9_\-]+"), "[chave removida]"),
    (re.compile(r"(api[_-]?key|token|secret|bearer|senha|password)\s*[:=]?\s*[A-Za-z0-9_\-\.]{8,}", re.I), r"\1 [removido]"),
]


def limpar(texto: str, segredos: list[str] | tuple = ()) -> str:
    for s in segredos:
        if s and len(s) >= 8:
            texto = texto.replace(s, "[chave removida]")
    for rx, sub in _PADROES:
        texto = rx.sub(sub, texto)
    return texto


def plataforma() -> str:
    return {"win32": "Windows", "darwin": "macOS"}.get(sys.platform, "Linux")

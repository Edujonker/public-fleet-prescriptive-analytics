# -*- coding: utf-8 -*-
"""
================================================================================
CAMADA DE AUTENTICAÇÃO E AUTORIZAÇÃO (IAM - IDENTITY & ACCESS MANAGEMENT)
SISTEMA DE GESTÃO DE FROTAS PÚBLICAS (PPGCAP/UDESC)
================================================================================
Funcionalidades:
- RBAC (Role-Based Access Control) com 5 perfis hierárquicos
- ABAC (Attribute-Based Access Control) para filtros departamentais e sigilo
- Tokens padrão OAuth2 / OpenID Connect (JWT com expiração e rotação)
- MFA (Multi-Factor Authentication) baseado em RFC 6238 TOTP
- Provedor Single Sign-On (SSO Gov.br / OIDC) simulado e extensível
- Armazenamento com hash criptográfico PBKDF2-HMAC-SHA256 (100.000 iterações)
- Proteção contra força bruta com bloqueio temporário após 5 tentativas
================================================================================
"""

import os
import hmac
import hashlib
import time
import base64
import struct
import secrets
import json
import sqlite3
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Tentativa de importação do PyJWT, com fallback para codificador RFC 7519 nativo
try:
    import jwt
    HAS_PYJWT = True
except ImportError:
    HAS_PYJWT = False

# Chave secreta mestre para assinatura de tokens (em produção obtida de env/vault)
JWT_SECRET_KEY = os.environ.get("FLEET_JWT_SECRET", "super-secret-fleet-master-key-ppgcap-2026-audit-sc")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Definição de Perfis (RBAC) e Permissões Granulares
PERFIS_PERMISSOES: Dict[str, List[str]] = {
    "ADMIN": [
        "frota:ler", "frota:escrever", "frota:excluir", "frota:leilao_autorizar",
        "servidores:gerenciar", "auditoria:ler", "auditoria:verificar",
        "sistema:backup", "sistema:metricas", "compliance:lgpd", "bi:exportar"
    ],
    "AUDITOR_FISCAL": [
        "frota:ler", "frota:leilao_visualizar", "auditoria:ler", "auditoria:verificar",
        "sistema:metricas", "compliance:lgpd", "bi:exportar"
    ],
    "GESTOR_FROTA": [
        "frota:ler", "frota:escrever", "frota:leilao_solicitar", "frota:leilao_visualizar",
        "bi:exportar", "sistema:metricas"
    ],
    "OPERADOR": [
        "frota:ler", "frota:escrever", "bi:exportar"
    ],
    "LEITOR": [
        "frota:ler", "bi:exportar"
    ]
}


def hash_senha(senha: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Gera hash PBKDF2-HMAC-SHA256 com 100.000 iterações."""
    if not salt:
        salt = secrets.token_hex(16)
    chave = hashlib.pbkdf2_hmac(
        'sha256',
        senha.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return chave.hex(), salt


def verificar_senha(senha: str, hash_armazenado: str, salt: str) -> bool:
    """Verifica senha contra hash armazenado em tempo constante contra timing attacks."""
    hash_calculado, _ = hash_senha(senha, salt)
    return hmac.compare_digest(hash_calculado, hash_armazenado)


# ------------------------------------------------------------------------------
# GERADOR E VALIDADOR DE JWT (COMPATÍVEL RFC 7519)
# ------------------------------------------------------------------------------

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def _base64url_decode(s: str) -> bytes:
    padding = '=' * (4 - (len(s) % 4)) if len(s) % 4 != 0 else ''
    return base64.urlsafe_b64decode(s + padding)


def criar_jwt_token(payload: Dict[str, Any], expira_em_segundos: int = 3600) -> str:
    """Cria token JWT assinado digitalmente com HMAC-SHA256."""
    payload_completo = payload.copy()
    agora = int(time.time())
    payload_completo.setdefault("iat", agora)
    payload_completo.setdefault("exp", agora + expira_em_segundos)
    payload_completo.setdefault("iss", "fleet-prescriptive-iam-udesc")

    if HAS_PYJWT:
        return jwt.encode(payload_completo, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # Fallback RFC 7519 nativo
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _base64url_encode(json.dumps(payload_completo, separators=(',', ':')).encode('utf-8'))
    
    msg = f"{header_b64}.{payload_b64}".encode('utf-8')
    sig = hmac.new(JWT_SECRET_KEY.encode('utf-8'), msg, hashlib.sha256).digest()
    sig_b64 = _base64url_encode(sig)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decodificar_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Valida assinatura e expiração de um token JWT."""
    if not token or not isinstance(token, str):
        return None
        
    if HAS_PYJWT:
        try:
            return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except Exception:
            return None

    # Fallback RFC 7519 nativo
    partes = token.split('.')
    if len(partes) != 3:
        return None
    header_b64, payload_b64, sig_b64 = partes

    try:
        msg = f"{header_b64}.{payload_b64}".encode('utf-8')
        sig_esperada = hmac.new(JWT_SECRET_KEY.encode('utf-8'), msg, hashlib.sha256).digest()
        sig_recebida = _base64url_decode(sig_b64)
        
        if not hmac.compare_digest(sig_esperada, sig_recebida):
            return None
            
        payload = json.loads(_base64url_decode(payload_b64).decode('utf-8'))
        if payload.get("exp", 0) < int(time.time()):
            return None  # Expirado
            
        return payload
    except Exception:
        return None


# ------------------------------------------------------------------------------
# MULTI-FACTOR AUTHENTICATION (RFC 6238 TOTP)
# ------------------------------------------------------------------------------

class TOTPEngine:
    """Implementação nativa do algoritmo TOTP (Time-Based One-Time Password - RFC 6238)."""

    @staticmethod
    def gerar_segredo_base32() -> str:
        """Gera chave secreta aleatória de 160 bits codificada em Base32."""
        bytes_aleatorios = secrets.token_bytes(20)
        return base64.b32encode(bytes_aleatorios).decode('utf-8')

    @staticmethod
    def gerar_codigo_totp(segredo_base32: str, intervalo_tempo: int = 30, timestamp: Optional[int] = None) -> str:
        """Gera o código numérico de 6 dígitos para o timestamp corrente."""
        if timestamp is None:
            timestamp = int(time.time())
        passo = timestamp // intervalo_tempo
        
        try:
            chave_bytes = base64.b32decode(segredo_base32.upper())
        except Exception:
            return "000000"

        msg = struct.pack(">Q", passo)
        h = hmac.new(chave_bytes, msg, hashlib.sha1).digest()
        
        offset = h[-1] & 0x0F
        codigo_truncado = struct.unpack(">I", h[offset:offset+4])[0] & 0x7FFFFFFF
        otp = codigo_truncado % 1000000
        return f"{otp:06d}"

    @classmethod
    def validar_codigo_totp(cls, segredo_base32: str, codigo_digitado: str, janela_tolerancia: int = 1) -> bool:
        """Valida código TOTP com tolerância de drift temporal (+/- 1 intervalo)."""
        if not codigo_digitado or len(codigo_digitado.strip()) != 6:
            return False
        
        t_atual = int(time.time())
        codigo_limpo = codigo_digitado.strip()
        
        for deslocamento in range(-janela_tolerancia, janela_tolerancia + 1):
            t_teste = t_atual + (deslocamento * 30)
            if hmac.compare_digest(cls.gerar_codigo_totp(segredo_base32, timestamp=t_teste), codigo_limpo):
                return True
        return False

    @staticmethod
    def obter_uri_provisionamento(usuario: str, segredo_base32: str, emissor: str = "FrotaPublica-SC") -> str:
        """Retorna URI padrão otpauth:// para escanear em apps como Google Authenticator / Authy."""
        return f"otpauth://totp/{emissor}:{usuario}?secret={segredo_base32}&issuer={emissor}&algorithm=SHA1&digits=6&period=30"


# ------------------------------------------------------------------------------
# GERENCIADOR CENTRAL DE IDENTIDADE E ACESSO (IAM)
# ------------------------------------------------------------------------------

class IAMManager:
    """Gerenciador de Identidades, Permissões RBAC/ABAC e Autenticação Multifator."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            db_path = str(base_dir / "dados" / "resultados_dissertacao.db")
        self.db_path = db_path
        self._inicializar_tabelas()

    def _obter_conexao(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _inicializar_tabelas(self):
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios_iam (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpf TEXT UNIQUE NOT NULL,
                    matricula TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    cargo TEXT NOT NULL,
                    orgao TEXT NOT NULL,
                    lotacao TEXT,
                    perfil_rbac TEXT NOT NULL DEFAULT 'OPERADOR',
                    nivel_acesso TEXT NOT NULL DEFAULT 'OPERACIONAL',
                    hash_senha TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    mfa_habilitado INTEGER DEFAULT 0,
                    mfa_segredo TEXT,
                    tentativas_falhas INTEGER DEFAULT 0,
                    bloqueado_ate INTEGER DEFAULT 0,
                    ativo INTEGER DEFAULT 1,
                    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                    ultimo_login TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_cpf ON usuarios_iam(cpf)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios_iam(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_orgao ON usuarios_iam(orgao)")
            conn.commit()
            
            # Semente de usuário administrador inicial se tabela estiver vazia
            cursor.execute("SELECT COUNT(*) FROM usuarios_iam")
            if cursor.fetchone()[0] == 0:
                h, s = hash_senha("Admin@Udesc2026!")
                segredo_mfa = TOTPEngine.gerar_segredo_base32()
                cursor.execute("""
                    INSERT INTO usuarios_iam (
                        cpf, matricula, nome, email, cargo, orgao, lotacao,
                        perfil_rbac, nivel_acesso, hash_senha, salt, mfa_habilitado, mfa_segredo, ativo
                    ) VALUES (
                        '000.000.000-00', 'ADMIN-01', 'Administrador Geral da Frota',
                        'admin.frota@sea.sc.gov.br', 'Auditor Geral', 'SEA', 'DIRETORIA_FROTAS',
                        'ADMIN', 'ESTRATEGICO', ?, ?, 1, ?, 1
                    )
                """, (h, s, segredo_mfa))
                conn.commit()

    def cadastrar_usuario(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Cadastra novo servidor ou operador no sistema com validação de duplicidade."""
        senha = dados.get("senha", "Mudar@123")
        h, s = hash_senha(senha)
        segredo_mfa = TOTPEngine.gerar_segredo_base32() if dados.get("mfa_habilitado") else None
        
        perfil = dados.get("perfil_rbac", "OPERADOR").upper()
        if perfil not in PERFIS_PERMISSOES:
            perfil = "OPERADOR"

        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO usuarios_iam (
                        cpf, matricula, nome, email, cargo, orgao, lotacao,
                        perfil_rbac, nivel_acesso, hash_senha, salt, mfa_habilitado, mfa_segredo, ativo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    dados.get("cpf", "").strip(),
                    dados.get("matricula", "").strip(),
                    dados.get("nome", "").strip(),
                    dados.get("email", "").strip().lower(),
                    dados.get("cargo", "").strip(),
                    dados.get("orgao", "SEA").strip(),
                    dados.get("lotacao", "CENTRAL").strip(),
                    perfil,
                    dados.get("nivel_acesso", "OPERACIONAL"),
                    h, s,
                    1 if segredo_mfa else 0,
                    segredo_mfa
                ))
                conn.commit()
                novo_id = cursor.lastrowid
                return {
                    "sucesso": True,
                    "id": novo_id,
                    "mensagem": f"Usuário {dados.get('nome')} cadastrado com sucesso no perfil {perfil}.",
                    "mfa_segredo": segredo_mfa,
                    "mfa_uri": TOTPEngine.obter_uri_provisionamento(dados.get('email', ''), segredo_mfa) if segredo_mfa else None
                }
            except sqlite3.IntegrityError as e:
                return {"sucesso": False, "mensagem": f"Violação de integridade (CPF ou E-mail já cadastrado): {e}"}

    def autenticar(self, login: str, senha: str, codigo_mfa: Optional[str] = None, ip_origem: str = "127.0.0.1") -> Dict[str, Any]:
        """
        Autentica credenciais, valida bloqueio por força bruta, verifica senha e código MFA (se ativo).
        Retorna tokens JWT (Access e Refresh) e perfil RBAC/ABAC.
        """
        login_limpo = login.strip()
        agora = int(time.time())

        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM usuarios_iam 
                WHERE (email = ? OR cpf = ? OR matricula = ?) AND ativo = 1
            """, (login_limpo.lower(), login_limpo, login_limpo))
            usr = cursor.fetchone()

            if not usr:
                return {"sucesso": False, "mensagem": "Credenciais inválidas.", "codigo": 401}

            # Verificação de bloqueio por tentativas falhas
            if usr["bloqueado_ate"] and usr["bloqueado_ate"] > agora:
                minutos_restantes = (usr["bloqueado_ate"] - agora) // 60 + 1
                return {
                    "sucesso": False, 
                    "mensagem": f"Conta temporariamente bloqueada por segurança. Tente novamente em {minutos_restantes} minuto(s).",
                    "codigo": 429
                }

            # Validação de senha
            if not verificar_senha(senha, usr["hash_senha"], usr["salt"]):
                tentativas = usr["tentativas_falhas"] + 1
                bloqueio = agora + (15 * 60) if tentativas >= 5 else 0
                cursor.execute("""
                    UPDATE usuarios_iam 
                    SET tentativas_falhas = ?, bloqueado_ate = ? 
                    WHERE id = ?
                """, (tentativas, bloqueio, usr["id"]))
                conn.commit()
                return {"sucesso": False, "mensagem": "Credenciais inválidas.", "codigo": 401}

            # Verificação de MFA se habilitado
            if usr["mfa_habilitado"]:
                if not codigo_mfa:
                    return {
                        "sucesso": False, 
                        "requer_mfa": True, 
                        "mensagem": "Autenticação em duas etapas requerida. Informe o código MFA de 6 dígitos.",
                        "codigo": 403
                    }
                if not TOTPEngine.validar_codigo_totp(usr["mfa_segredo"], codigo_mfa):
                    return {"sucesso": False, "mensagem": "Código MFA inválido ou expirado.", "codigo": 401}

            # Reset de tentativas falhas e atualização de último login
            cursor.execute("""
                UPDATE usuarios_iam 
                SET tentativas_falhas = 0, bloqueado_ate = 0, ultimo_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (usr["id"],))
            conn.commit()

            # Emissão de Tokens OAuth2 / JWT
            payload_access = {
                "sub": str(usr["id"]),
                "cpf": usr["cpf"],
                "nome": usr["nome"],
                "email": usr["email"],
                "orgao": usr["orgao"],
                "lotacao": usr["lotacao"],
                "perfil_rbac": usr["perfil_rbac"],
                "nivel_acesso": usr["nivel_acesso"],
                "permissoes": PERFIS_PERMISSOES.get(usr["perfil_rbac"], []),
                "tipo": "access_token"
            }
            access_token = criar_jwt_token(payload_access, expira_em_segundos=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

            payload_refresh = {
                "sub": str(usr["id"]),
                "tipo": "refresh_token"
            }
            refresh_token = criar_jwt_token(payload_refresh, expira_em_segundos=REFRESH_TOKEN_EXPIRE_DAYS * 86400)

            return {
                "sucesso": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "usuario": {
                    "id": usr["id"],
                    "nome": usr["nome"],
                    "email": usr["email"],
                    "orgao": usr["orgao"],
                    "perfil_rbac": usr["perfil_rbac"],
                    "permissoes": PERFIS_PERMISSOES.get(usr["perfil_rbac"], [])
                }
            }

    def autenticar_sso_govbr(self, codigo_sso: str) -> Dict[str, Any]:
        """
        Simula o fluxo de Single Sign-On (SSO) com Provedor OpenID Connect Gov.br.
        Decodifica o ticket de autorização e mapeia para servidor público estadual.
        """
        if not codigo_sso or "govbr" not in codigo_sso.lower():
            return {"sucesso": False, "mensagem": "Ticket SSO Gov.br inválido ou expirado."}

        # Simulação de retorno federado com claims verificadas
        email_federado = "auditor.sso@sea.sc.gov.br"
        with self._obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_iam WHERE email = ?", (email_federado,))
            usr = cursor.fetchone()
            if not usr:
                # Provisionamento Just-in-Time (JIT) do servidor federado
                h, s = hash_senha(secrets.token_hex(20))
                cursor.execute("""
                    INSERT INTO usuarios_iam (
                        cpf, matricula, nome, email, cargo, orgao, lotacao,
                        perfil_rbac, nivel_acesso, hash_senha, salt, mfa_habilitado, ativo
                    ) VALUES (
                        '111.222.333-44', 'SSO-GOVBR-01', 'Auditor Federado Gov.br',
                        ?, 'Auditor Externo', 'TCE', 'AUDITORIA_GERAL',
                        'AUDITOR_FISCAL', 'ESTRATEGICO', ?, ?, 0, 1
                    )
                """, (email_federado, h, s))
                conn.commit()
                cursor.execute("SELECT * FROM usuarios_iam WHERE email = ?", (email_federado,))
                usr = cursor.fetchone()

        payload = {
            "sub": str(usr["id"]),
            "cpf": usr["cpf"],
            "nome": usr["nome"],
            "email": usr["email"],
            "orgao": usr["orgao"],
            "perfil_rbac": usr["perfil_rbac"],
            "permissoes": PERFIS_PERMISSOES.get(usr["perfil_rbac"], []),
            "auth_provider": "gov.br_oidc"
        }
        token = criar_jwt_token(payload, expira_em_segundos=3600)
        return {
            "sucesso": True,
            "access_token": token,
            "token_type": "Bearer",
            "provedor": "Gov.br OIDC Federado",
            "usuario": payload
        }

    @staticmethod
    def verificar_autorizacao(token: str, permissao_requerida: str, contexto_abac: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Avalia tanto RBAC (permissões de função) quanto ABAC (atributos contextuais de órgão e lotação).
        """
        payload = decodificar_jwt_token(token)
        if not payload:
            return False, "Token inválido, expirado ou não informado."

        permissoes_usuario = payload.get("permissoes", [])
        perfil = payload.get("perfil_rbac", "LEITOR")

        # Avaliação RBAC
        if permissao_requerida not in permissoes_usuario and perfil != "ADMIN":
            return False, f"Acesso negado: Perfil '{perfil}' não possui a permissão '{permissao_requerida}'."

        # Avaliação ABAC (se houver restrição de órgão no recurso requisitado)
        if contexto_abac and perfil != "ADMIN":
            orgao_recurso = contexto_abac.get("orgao_alvo")
            orgao_usuario = payload.get("orgao")
            if orgao_recurso and orgao_usuario and orgao_recurso != orgao_usuario:
                return False, f"Acesso negado (ABAC): Servidor do órgão '{orgao_usuario}' não pode gerenciar dados do órgão '{orgao_recurso}'."

        return True, "Acesso autorizado."


# Instância Singleton do IAM
iam_global = IAMManager()

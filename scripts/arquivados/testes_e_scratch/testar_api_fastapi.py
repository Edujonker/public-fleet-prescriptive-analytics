#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BATERIA DE TESTES DE SEGURANÇA E CONFORMIDADE FASTAPI (PPGCAP/UDESC)
SECURITY-BY-DESIGN: OWASP TOP 10, CWE & PYDANTIC V2 VALIDATION SUITE
================================================================================
"""

import sys
import os
import json
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)

from starlette.testclient import TestClient
from src.api.main import app
from src.api.config import get_settings
from src.api.database import init_db

settings = get_settings()

def run_fastapi_security_tests():
    print("=" * 80)
    print(" INICIANDO AUDITORIA E TESTES DE SEGURANÇA FASTAPI (PPGCAP/UDESC)")
    print("=" * 80)

    # Inicializa banco de dados e usuários sementes
    asyncio.run(init_db())

    client = TestClient(app)
    testes_executados = 0
    testes_aprovados = 0
    falhas = []

    def assert_test(nome_teste: str, condicao: bool, detalhe_erro: str = ""):
        nonlocal testes_executados, testes_aprovados
        testes_executados += 1
        if condicao:
            testes_aprovados += 1
            print(f"  [PASS] Teste #{testes_executados:02d}: {nome_teste}")
        else:
            falhas.append({"id": testes_executados, "nome": nome_teste, "erro": detalhe_erro})
            print(f"  [FAIL] Teste #{testes_executados:02d}: {nome_teste} | Erro: {detalhe_erro}")

    # --------------------------------------------------------------------------
    # 1. TESTE DE HEADERS DE SEGURANÇA (OWASP A05: SECURITY MISCONFIGURATION)
    # --------------------------------------------------------------------------
    resp = client.get("/api/status")
    assert_test(
        "Headers de Segurança: X-Content-Type-Options: nosniff",
        resp.headers.get("x-content-type-options") == "nosniff",
        f"Header incorreto: {resp.headers.get('x-content-type-options')}"
    )
    assert_test(
        "Headers de Segurança: X-Frame-Options: SAMEORIGIN",
        resp.headers.get("x-frame-options") == "SAMEORIGIN",
        f"Header incorreto: {resp.headers.get('x-frame-options')}"
    )
    assert_test(
        "Headers de Segurança: Strict-Transport-Security (HSTS)",
        "max-age=31536000" in (resp.headers.get("strict-transport-security") or ""),
        f"Header incorreto: {resp.headers.get('strict-transport-security')}"
    )
    assert_test(
        "Headers de Segurança: Content-Security-Policy (CSP)",
        "default-src 'self'" in (resp.headers.get("content-security-policy") or ""),
        f"CSP incorreta: {resp.headers.get('content-security-policy')}"
    )

    # --------------------------------------------------------------------------
    # 2. VALIDAÇÃO E MODELAGEM PYDANTIC V2 (CWE-20: IMPROPER INPUT VALIDATION)
    # --------------------------------------------------------------------------
    # Requisição com payload inválido (campo ausente)
    resp_inv = client.post("/api/chat", json={})
    assert_test(
        "Pydantic v2: Rejeição de payload sem campo obrigatório (HTTP 422)",
        resp_inv.status_code == 422 and "validation_error" in resp_inv.text,
        f"Status: {resp_inv.status_code}, Body: {resp_inv.text}"
    )

    # Requisição com payload com tipo incorreto (int em vez de str)
    resp_type = client.post("/api/chat", json={"mensagem": 12345})
    assert_test(
        "Pydantic v2: Rejeição de tipo estrito (StrictStr int->str) (HTTP 422)",
        resp_type.status_code == 422,
        f"Status: {resp_type.status_code}"
    )

    # Requisição com campos extras não permitidos (extra='forbid')
    resp_extra = client.post("/api/chat", json={"mensagem": "Quantas OS existem?", "campo_malicioso": "exploit"})
    assert_test(
        "Pydantic v2: Rejeição de campos extras proibidos extra='forbid' (HTTP 422)",
        resp_extra.status_code == 422,
        f"Status: {resp_extra.status_code}"
    )

    # --------------------------------------------------------------------------
    # 3. AUTENTICAÇÃO OAUTH2 + JWT (OWASP A07: IDENTIFICATION AND AUTHENTICATION)
    # --------------------------------------------------------------------------
    # Login com senha incorreta
    resp_bad_login = client.post("/api/auth/login", json={
        "username": settings.ADMIN_DEFAULT_USERNAME,
        "password": "SenhaCompletamenteIncorreta123!"
    })
    assert_test(
        "Autenticação: Rejeição de credenciais incorretas (HTTP 401)",
        resp_bad_login.status_code == 401,
        f"Status: {resp_bad_login.status_code}"
    )

    # Tentativa de SQL Injection no campo de username
    resp_sqli = client.post("/api/auth/login", json={
        "username": "admin' OR '1'='1",
        "password": "QualquerSenha123!"
    })
    assert_test(
        "SQL Injection: Bloqueio via regex no Pydantic e bind SQLAlchemy 2.0",
        resp_sqli.status_code in [401, 422],
        f"Status: {resp_sqli.status_code}"
    )

    # Login válido do Administrador
    resp_admin_login = client.post("/api/auth/login", json={
        "username": settings.ADMIN_DEFAULT_USERNAME,
        "password": settings.ADMIN_DEFAULT_PASSWORD
    })
    admin_token_data = resp_admin_login.json()
    admin_token = admin_token_data.get("access_token", "")
    assert_test(
        "Autenticação: Login do Administrador com emissão de JWT (HTTP 200)",
        resp_admin_login.status_code == 200 and len(admin_token) > 20,
        f"Status: {resp_admin_login.status_code}"
    )

    # Login válido do Pesquisador
    resp_pesq_login = client.post("/api/auth/login", json={
        "username": "pesquisador_ppgcap",
        "password": "Pesquisador@PPGCAP2026!"
    })
    pesq_token_data = resp_pesq_login.json()
    pesq_token = pesq_token_data.get("access_token", "")
    assert_test(
        "Autenticação: Login do Pesquisador com emissão de JWT (HTTP 200)",
        resp_pesq_login.status_code == 200 and len(pesq_token) > 20,
        f"Status: {resp_pesq_login.status_code}"
    )

    # --------------------------------------------------------------------------
    # 4. PREVENÇÃO DE VAZAMENTO DE DADOS (CWE-200: ANTI-DATA LEAKAGE)
    # --------------------------------------------------------------------------
    resp_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    user_me_data = resp_me.json()
    assert_test(
        "Anti-Data Leakage: /api/auth/me NÃO expõe campo 'hashed_password' nem 'password'",
        "password" not in user_me_data and "hashed_password" not in user_me_data and user_me_data.get("username") == settings.ADMIN_DEFAULT_USERNAME,
        f"Dados retornados: {user_me_data}"
    )

    # --------------------------------------------------------------------------
    # 5. CONTROLE DE ACESSO BASEADO EM PAPÉIS (RBAC / OWASP A01: BROKEN ACCESS CONTROL)
    # --------------------------------------------------------------------------
    # Acesso a recurso de Admin por usuário comum (Pesquisador) deve dar 403 Forbidden
    resp_forbidden = client.post(
        "/api/gerar-relatorio",
        headers={"Authorization": f"Bearer {pesq_token}"}
    )
    assert_test(
        "RBAC: Bloqueio de rota exclusiva de Admin para papel 'pesquisador' (HTTP 403)",
        resp_forbidden.status_code == 403 and "Permissão insuficiente" in resp_forbidden.text,
        f"Status: {resp_forbidden.status_code}, Body: {resp_forbidden.text}"
    )

    # Rejeição de token inválido / falsificado
    resp_bad_jwt = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer token_completamente_falso_e_invalido"}
    )
    assert_test(
        "JWT: Rejeição de token forjado/inválido (HTTP 401)",
        resp_bad_jwt.status_code == 401,
        f"Status: {resp_bad_jwt.status_code}"
    )

    # --------------------------------------------------------------------------
    # 6. COPILOTO DE IA E CONSULTAS EM LINGUAGEM NATURAL
    # --------------------------------------------------------------------------
    resp_chat = client.post("/api/chat", json={"mensagem": "Quantas ordens de serviço existem na base?"})
    chat_json = resp_chat.json()
    assert_test(
        "Copiloto de IA: Processamento com resposta estruturada via Pydantic (HTTP 200)",
        resp_chat.status_code == 200 and "350.737" in chat_json.get("resposta", ""),
        f"Status: {resp_chat.status_code}, Resposta: {chat_json.get('resposta', '')[:100]}"
    )

    # Pergunta fora de escopo (Regra 2)
    resp_chat_ood = client.post("/api/chat", json={"mensagem": "Qual a receita de bolo de fubá?"})
    assert_test(
        "Copiloto de IA: Aplicação estrita da Regra 2 para temas fora de contexto",
        resp_chat_ood.status_code == 200 and "Desculpe, só posso responder dúvidas sobre os dados do seu sistema." == resp_chat_ood.json().get("resposta"),
        f"Resposta: {resp_chat_ood.json().get('resposta')}"
    )

    # --------------------------------------------------------------------------
    # 7. PARÂMETROS ESTATÍSTICOS DO PIPELINE (PYDANTIC V2 RANGE CHECKS)
    # --------------------------------------------------------------------------
    # Alpha inválido (fora do intervalo 0.001 a 0.20)
    resp_alpha_invalido = client.post(
        "/api/atualizar-graficos",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"alpha": 0.85, "frequencia": "ME", "horizonte": 6}
    )
    assert_test(
        "Pydantic v2: Rejeição de alpha fora dos limites estatísticos (HTTP 422)",
        resp_alpha_invalido.status_code == 422,
        f"Status: {resp_alpha_invalido.status_code}"
    )

    # Frequência temporal inválida (regex)
    resp_freq_invalida = client.post(
        "/api/atualizar-graficos",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"alpha": 0.05, "frequencia": "INVALID_FREQ", "horizonte": 6}
    )
    assert_test(
        "Pydantic v2: Rejeição de frequência temporal inválida por Regex (HTTP 422)",
        resp_freq_invalida.status_code == 422,
        f"Status: {resp_freq_invalida.status_code}"
    )

    # --------------------------------------------------------------------------
    # RESUMO FINAL DOS RESULTADOS
    # --------------------------------------------------------------------------
    taxa_sucesso = (testes_aprovados / testes_executados) * 100
    print("=" * 80)
    print(f" RESULTADO FINAL: {testes_aprovados}/{testes_executados} TESTES PASSARAM ({taxa_sucesso:.1f}%)")
    print("=" * 80)

    # Salva relatório de auditoria de segurança
    report_path = BASE_DIR / "relatorios" / "auditoria_seguranca_fastapi.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_testes": testes_executados,
            "testes_aprovados": testes_aprovados,
            "taxa_sucesso": taxa_sucesso,
            "falhas": falhas,
            "conformidade_owasp": [
                "A01: Broken Access Control (RBAC)",
                "A02: Cryptographic Failures (Argon2/Bcrypt + HS256)",
                "A03: Injection (SQLAlchemy 2.0 ORM Bind + Pydantic v2)",
                "A04: Insecure Design (Strict Input/Output Schema Separation)",
                "A05: Security Misconfiguration (HSTS, CSP, X-Frame, Nosniff, CORS restrito)",
                "A07: Identification and Authentication Failures (JWT + OAuth2 Bearer)",
                "A09: Security Logging and Monitoring Failures (AuditLog Table)"
            ]
        }, f, indent=2, ensure_ascii=False)
    print(f"Relatório gravado em: {report_path}")

    return 0 if len(falhas) == 0 else 1

if __name__ == "__main__":
    exit_code = run_fastapi_security_tests()
    sys.exit(exit_code)

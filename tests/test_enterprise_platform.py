# -*- coding: utf-8 -*-
"""
================================================================================
SUÍTE DE TESTES AUTOMATIZADOS DA PLATAFORMA ENTERPRISE DE FROTAS
PPGCAP / UDESC - SEGURANÇA POR DESIGN & CONFORMIDADE
================================================================================
"""

import sys
from pathlib import Path

# Garante inclusão da raiz do repositório no sys.path para resolução de src.*
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
import time
from src.enterprise.iam import iam_global, decodificar_jwt_token, IAMManager, TOTPEngine
from src.enterprise.gateway import api_gateway_global
from src.enterprise.messaging import message_broker_global, BackgroundWorker
from src.enterprise.audit_trail import immutable_audit_trail_global
from src.enterprise.storage import cache_global, nosql_global, storage_global, dr_manager_global
from src.enterprise.compliance import compliance_global, crypto_global, lgpd_manager_global, sanitizer_global
from src.enterprise.observability import observability_global
from src.enterprise.fleet_engine import fleet_engine_global
from src.enterprise.i18n import i18n_global


def test_iam_authentication_and_rbac():
    """Testa autenticação, geração de JWT e controle de acesso RBAC/ABAC."""
    ts = int(time.time() * 1000) % 1000000
    cpf_teste = f"111.{ts % 900 + 100:03d}.{ts % 800 + 100:03d}-44"
    email_teste = f"operador.{ts}@sea.sc.gov.br"

    # Cadastra usuário de teste sem MFA
    novo = iam_global.cadastrar_usuario({
        "cpf": cpf_teste,
        "matricula": f"TEST-{ts}",
        "nome": "Operador de Testes",
        "email": email_teste,
        "cargo": "Analista de Frotas",
        "orgao": "SEA",
        "perfil_rbac": "GESTOR_FROTA",
        "senha": "SenhaForte@2026",
        "mfa_habilitado": False
    })
    assert novo["sucesso"] is True

    # Autenticação
    auth_res = iam_global.autenticar(email_teste, "SenhaForte@2026")
    assert auth_res["sucesso"] is True
    token = auth_res["access_token"]
    assert token is not None

    # Validação do token
    payload = decodificar_jwt_token(token)
    assert payload is not None
    assert payload["email"] == email_teste
    assert payload["perfil_rbac"] == "GESTOR_FROTA"

    # Autorização RBAC
    autorizado, _ = IAMManager.verificar_autorizacao(token, "frota:ler")
    assert autorizado is True


def test_api_gateway_rate_limiting_and_waf():
    """Testa roteamento do API Gateway, detecção WAF e rate limiter."""
    # Requisição legítima
    res = api_gateway_global.despachar_requisicao("GET", "/api/v2/frota/veiculos", ip_cliente="127.0.0.1")
    assert res["status_code"] == 200
    assert "X-RateLimit-Limit" in res["headers"]
    assert "X-Frame-Options" in res["headers"]

    # Tentativa de Path Traversal bloqueada pelo WAF
    res_waf_path = api_gateway_global.despachar_requisicao("GET", "/api/v2/frota/../../etc/passwd", ip_cliente="10.0.0.9")
    assert res_waf_path["status_code"] == 403
    assert "Path Traversal" in res_waf_path["body"]["detalhe"]

    # Tentativa de SQL Injection bloqueada pelo WAF
    res_waf_sqli = api_gateway_global.despachar_requisicao("GET", "/api/v2/frota", query="q=' UNION SELECT 1--", ip_cliente="10.0.0.9")
    assert res_waf_sqli["status_code"] == 403
    assert "Injeção SQL" in res_waf_sqli["body"]["detalhe"]


def test_immutable_audit_trail_hash_chain():
    """Testa registro em bloco e verificação matemática da cadeia de custódia SHA-256."""
    bloco = immutable_audit_trail_global.registrar_evento(
        ator_id=1,
        acao="CONSULTA_PRESCRIÇÃO_MILP",
        recurso="veiculos_frota/MLH1204",
        detalhes={"algoritmo": "MILP", "status": "AUDITADO"},
        ip_origem="192.168.1.100"
    )
    assert bloco["sequencia"] > 0
    assert len(bloco["hash_bloco"]) == 64

    # Verificação da integridade da cadeia
    integro, total, msg = immutable_audit_trail_global.verificar_integridade()
    assert integro is True
    assert total > 0


def test_fleet_engine_operations():
    """Testa listagem, KPIs, cadastro de motoristas e ordens de serviço."""
    stats = fleet_engine_global.obter_estatisticas_painel_frota()
    assert stats["total_veiculos_cadastrados"] > 0
    assert stats["veiculos_elegiveis_leilao"] > 0

    # Consulta multi-critério
    busca = fleet_engine_global.listar_veiculos(economicidade="leilao", limite=10)
    assert len(busca["veiculos"]) > 0
    assert busca["veiculos"][0]["elegivel_leilao"] == 1

    # Motoristas
    motoristas = fleet_engine_global.listar_motoristas()
    assert len(motoristas) >= 5


def test_storage_cache_and_disaster_recovery():
    """Testa cache em memória, NoSQL store e validação de Disaster Recovery."""
    cache_global.set("teste_chave", {"frota": 2026}, ttl_segundos=10)
    res = cache_global.get("teste_chave")
    assert res == {"frota": 2026}

    # NoSQL Document Store
    doc = nosql_global.salvar_documento("configuracoes", "alerta_combustivel", {"limite_litros": 75})
    assert doc["_id"] == "alerta_combustivel"
    recuperado = nosql_global.obter_documento("configuracoes", "alerta_combustivel")
    assert recuperado["limite_litros"] == 75

    # Snapshot Disaster Recovery
    snapshot = dr_manager_global.executar_backup_snapshot()
    assert snapshot["status"] == "VALIDADO_INTEGRO"
    assert snapshot["tamanho_mb"] > 0

    # Simulação de Restauração RTO
    restauracao = dr_manager_global.testar_restauracao_disaster_recovery(snapshot["arquivo"])
    assert restauracao["sucesso"] is True
    assert restauracao["status_integridade"] == "100% OPERACIONAL"


from src.enterprise.compliance import lgpd_manager_global, sanitizer_global, crypto_global


def test_compliance_and_lgpd():
    """Testa anonimização LGPD, criptografia e sanitização de entradas."""
    cpf_mascarado = lgpd_manager_global.mascarar_cpf("042.881.992-10")
    assert cpf_mascarado == "***.881.992-**"

    # Sanitização XSS
    sanitizado = sanitizer_global.sanitizar_texto_xss("<script>alert('xss')</script>Texto Limpo")
    assert "<script>" not in sanitizado
    assert "Texto Limpo" in sanitizado

    # Validação de CPF e Placa
    assert sanitizer_global.validar_placa("ABC1D23") is True
    assert sanitizer_global.validar_placa("INVALIDA") is False

    # Criptografia reversível AES-GCM
    cifrado = crypto_global.cifrar_texto("SegredoInstitucional2026")
    decifrado = crypto_global.decifrar_texto(cifrado)
    assert decifrado == "SegredoInstitucional2026"


def test_i18n_translations():
    """Testa dicionários de internacionalização."""
    pt = i18n_global.get_translations("pt-BR")
    en = i18n_global.get_translations("en-US")
    es = i18n_global.get_translations("es-ES")
    assert "Gestão de Veículos" in pt["tab_veiculos"]
    assert "Fleet Vehicle" in en["tab_veiculos"]
    assert "Gestión de Vehículos" in es["tab_veiculos"]


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))


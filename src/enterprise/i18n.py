# -*- coding: utf-8 -*-
"""
================================================================================
INTERNACIONALIZAÇÃO (i18n) & LOCALIZAÇÃO (l10n)
SISTEMA INTEGRADO DE GESTÃO DE FROTAS & ANALÍTICA PRESCRITIVA (PPGCAP/UDESC)
================================================================================
Idiomas Suportados:
- pt-BR: Português do Brasil (Padrão)
- en-US: Inglês (American English)
- es-ES: Espanhol (Castellano)
Formatadores de Moeda (BRL R$, USD $, EUR €), Datas e Números.
================================================================================
"""

from typing import Dict, Any, Optional

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "pt-BR": {
        "app_title": "Sistema Integrado de Gestão de Frotas Públicas e Analítica Prescritiva",
        "app_subtitle": "PPGCAP / UDESC • Segurança por Design & Evidência Pericial TCE/SC",
        "tab_dashboard": "Painel Gerencial",
        "tab_veiculos": "Gestão de Veículos",
        "tab_leilao": "Leilão & Descarte",
        "tab_abastecimentos": "Abastecimentos & Fraudes",
        "tab_manutencao": "Ordens de Serviço & Oficinas",
        "tab_viagens": "Despacho & Diário de Bordo",
        "tab_servidores": "Gestão de Acessos & IAM",
        "tab_dicionario": "Dicionário de Dados",
        "tab_auditoria": "Trilha de Auditoria Imutável",
        "tab_observabilidade": "Observabilidade & Métricas",
        "tab_artigos": "Artigos Científicos & Relatórios",
        "btn_search": "Pesquisar",
        "btn_filter": "Filtrar",
        "btn_export_excel": "Exportar Excel (.xlsx)",
        "btn_export_csv": "Exportar CSV",
        "btn_generate_pdf": "Gerar PDF Oficial",
        "btn_new_vehicle": "Novo Veículo",
        "btn_new_driver": "Novo Motorista",
        "btn_dispatch_trip": "Despachar Viagem",
        "btn_new_os": "Nova Ordem de Serviço",
        "btn_verify_ledger": "Verificar Integridade SHA-256",
        "status_operational": "Operacional",
        "status_maintenance": "Em Manutenção",
        "status_trip": "Em Viagem",
        "status_auction": "Elegível para Leilão (Decreto 47.539/2018)",
        "legal_basis": "Art. 5º Decreto Estadual nº 47.539/2018 (Manutenção acumulada ≥ 40% do valor venal FIPE)",
        "currency_symbol": "R$ ",
        "system_online": "Sistema Online",
        "security_hardened": "Hardened (OWASP / LGPD)"
    },
    "en-US": {
        "app_title": "Integrated Public Fleet Management & Prescriptive Analytics System",
        "app_subtitle": "PPGCAP / UDESC • Security-by-Design & Court of Accounts Forensic Standard",
        "tab_dashboard": "Executive Dashboard",
        "tab_veiculos": "Fleet Vehicle Inventory",
        "tab_leilao": "Auction & Decommission",
        "tab_abastecimentos": "Fuel & Fraud Detection",
        "tab_manutencao": "Service Orders & Workshops",
        "tab_viagens": "Trip Dispatch & Logbook",
        "tab_servidores": "Access Management & IAM",
        "tab_dicionario": "Data Dictionary",
        "tab_auditoria": "Immutable Audit Trail",
        "tab_observabilidade": "Observability & Metrics",
        "tab_artigos": "Research Papers & Reports",
        "btn_search": "Search",
        "btn_filter": "Filter",
        "btn_export_excel": "Export Excel (.xlsx)",
        "btn_export_csv": "Export CSV",
        "btn_generate_pdf": "Generate Official PDF",
        "btn_new_vehicle": "Register Vehicle",
        "btn_new_driver": "Register Driver",
        "btn_dispatch_trip": "Dispatch Trip",
        "btn_new_os": "Open Service Order",
        "btn_verify_ledger": "Verify SHA-256 Integrity",
        "status_operational": "Operational",
        "status_maintenance": "Under Maintenance",
        "status_trip": "On Trip",
        "status_auction": "Eligible for Auction (State Decree 47.539/2018)",
        "legal_basis": "Art. 5 State Decree No. 47.539/2018 (Accumulated maintenance ≥ 40% of FIPE market value)",
        "currency_symbol": "$ ",
        "system_online": "System Online",
        "security_hardened": "Hardened (OWASP / GDPR)"
    },
    "es-ES": {
        "app_title": "Sistema Integrado de Gestión de Flotas Públicas y Analítica Prescriptiva",
        "app_subtitle": "PPGCAP / UDESC • Seguridad por Diseño y Evidencia Pericial de Auditoría",
        "tab_dashboard": "Panel Gerencial",
        "tab_veiculos": "Gestión de Vehículos",
        "tab_leilao": "Subasta y Baja",
        "tab_abastecimentos": "Combustible y Fraudes",
        "tab_manutencao": "Órdenes de Servicio y Talleres",
        "tab_viagens": "Despacho y Libro de Ruta",
        "tab_servidores": "Gestión de Accesos e IAM",
        "tab_dicionario": "Diccionario de Datos",
        "tab_auditoria": "Pista de Auditoría Inmutable",
        "tab_observabilidade": "Observabilidad y Métricas",
        "tab_artigos": "Artículos Científicos e Informes",
        "btn_search": "Buscar",
        "btn_filter": "Filtrar",
        "btn_export_excel": "Exportar Excel (.xlsx)",
        "btn_export_csv": "Exportar CSV",
        "btn_generate_pdf": "Generar PDF Oficial",
        "btn_new_vehicle": "Nuevo Vehículo",
        "btn_new_driver": "Nuevo Conductor",
        "btn_dispatch_trip": "Despachar Viaje",
        "btn_new_os": "Nueva Orden de Servicio",
        "btn_verify_ledger": "Verificar Integridad SHA-256",
        "status_operational": "Operacional",
        "status_maintenance": "En Mantenimiento",
        "status_trip": "En Viaje",
        "status_auction": "Elegible para Subasta (Decreto 47.539/2018)",
        "legal_basis": "Art. 5º Decreto Estadual nº 47.539/2018 (Mantenimiento acumulado ≥ 40% del valor venal FIPE)",
        "currency_symbol": "€ ",
        "system_online": "Sistema En Línea",
        "security_hardened": "Protegido (OWASP / RGPD)"
    }
}

class I18nManager:
    """Gerenciador de internacionalização para a interface e APIs."""

    def __init__(self, default_lang: str = "pt-BR"):
        self.default_lang = default_lang

    def get_translations(self, lang: Optional[str] = None) -> Dict[str, str]:
        selected = lang if lang in TRANSLATIONS else self.default_lang
        return TRANSLATIONS.get(selected, TRANSLATIONS["pt-BR"])

    def translate(self, key: str, lang: Optional[str] = None, fallback: str = "") -> str:
        dict_lang = self.get_translations(lang)
        return dict_lang.get(key, fallback or key)

i18n_global = I18nManager()

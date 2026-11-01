#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador do Mapa Mental Executivo e Fluxograma de Módulos em PDF
Sistema de Gestão de Frotas & Telemetria IoT - FrotaSaaS Enterprise 2.0 (Porta 8090)
Autor: Eduardo Lopes Jonker (PPGCAP / UDESC)
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "sistema_gestao_frotas" / "docs"
PDF_DIR = BASE_DIR / "relatorios_pdf"
DOCS_GERAL_DIR = BASE_DIR / "Documentos"

for d in [DOCS_DIR, PDF_DIR, DOCS_GERAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def gerar_mapa_mental_pdf():
    pdf_out = DOCS_DIR / "MAPA_MENTAL_SISTEMA_FROTAS.pdf"
    
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Mapa Mental e Fluxograma de Módulos - FrotaSaaS Enterprise 2.0</title>
<style>
    @page {
        size: A4 portrait;
        margin: 1.6cm 1.4cm 1.8cm 1.4cm;
        @top-left {
            content: "SISTEMA DE GESTÃO DE FROTAS & TELEMETRIA IOT • FROTASAAS 2.0";
            font-size: 7pt;
            font-family: 'Liberation Sans', Helvetica, Arial, sans-serif;
            color: #64748b;
            font-weight: 700;
        }
        @top-right {
            content: "MAPA MENTAL & FLUXOGRAMA DE MÓDULOS";
            font-size: 7pt;
            font-family: 'Liberation Sans', Helvetica, Arial, sans-serif;
            color: #64748b;
            font-style: italic;
        }
        @bottom-left {
            content: "PPGCAP / CCT / UDESC • MESTRADO EM COMPUTAÇÃO APLICADA • 2026";
            font-size: 7pt;
            font-family: 'Liberation Sans', Helvetica, Arial, sans-serif;
            color: #64748b;
        }
        @bottom-right {
            content: "Página " counter(page) " de " counter(pages);
            font-size: 7pt;
            font-family: 'Liberation Sans', Helvetica, Arial, sans-serif;
            color: #64748b;
            font-weight: 700;
        }
    }

    body {
        font-family: 'Liberation Sans', Helvetica, Arial, sans-serif;
        font-size: 8.5pt;
        line-height: 1.45;
        color: #1e293b;
        margin: 0;
        padding: 0;
    }

    /* CAPA & CABEÇALHOS */
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #312e81 100%);
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 6px;
        margin-bottom: 14px;
        border-left: 6px solid #8b5cf6;
    }
    .header-title {
        font-size: 15pt;
        font-weight: 900;
        margin: 0 0 4px 0;
        letter-spacing: -0.3px;
        color: #f8fafc;
    }
    .header-subtitle {
        font-size: 9.5pt;
        color: #c4b5fd;
        margin: 0 0 8px 0;
        font-weight: 600;
    }
    .header-meta {
        font-size: 7.5pt;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
        border-top: 1px solid rgba(255,255,255,0.12);
        padding-top: 6px;
    }

    .section-title {
        font-size: 10.5pt;
        font-weight: 900;
        color: #0f172a;
        background: #f1f5f9;
        padding: 5px 8px;
        border-left: 4px solid #0284c7;
        margin: 16px 0 8px 0;
        text-transform: uppercase;
        letter-spacing: -0.2px;
    }
    .section-title.purple { border-left-color: #8b5cf6; }
    .section-title.red { border-left-color: #ef4444; }
    .section-title.emerald { border-left-color: #10b981; }

    /* CARDS & GRIDS */
    .grid-2 {
        display: table;
        width: 100%;
        table-layout: fixed;
        margin-bottom: 10px;
    }
    .grid-col {
        display: table-cell;
        vertical-align: top;
        padding: 0 6px;
    }
    .grid-col:first-child { padding-left: 0; }
    .grid-col:last-child { padding-right: 0; }

    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 5px;
        padding: 8px 10px;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .card-title {
        font-size: 8.5pt;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 4px 0;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* BADGES */
    .badge {
        display: inline-block;
        padding: 1.5px 5px;
        border-radius: 3px;
        font-size: 6.5pt;
        font-weight: 800;
        text-transform: uppercase;
    }
    .badge-blue { background: #e0f2fe; color: #0369a1; }
    .badge-purple { background: #ede9fe; color: #6d28d9; }
    .badge-red { background: #fee2e2; color: #b91c1c; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-amber { background: #fef3c7; color: #b45309; }
    .badge-dark { background: #0f172a; color: #ffffff; }

    /* TABELAS */
    table.data-table {
        width: 100%;
        border-collapse: collapse;
        margin: 6px 0 10px 0;
        font-size: 7.2pt;
        table-layout: fixed;
    }
    table.data-table th {
        background: #0f172a;
        color: #ffffff;
        font-weight: 800;
        padding: 4px 6px;
        text-align: left;
        border: 1px solid #334155;
    }
    table.data-table td {
        padding: 4px 6px;
        border: 1px solid #e2e8f0;
        vertical-align: top;
        word-wrap: break-word;
    }
    table.data-table tr:nth-child(even) {
        background: #f8fafc;
    }

    /* FLUXOGRAMA SVG EMBED */
    .svg-container {
        text-align: center;
        margin: 8px 0;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 8px 4px;
    }

    .page-break {
        page-break-before: always;
    }
</style>
</head>
<body>

    <!-- =====================================================================
         PÁGINA 1: CABEÇALHO EXECUTIVO E O MAPA MENTAL SISTÊMICO
         ===================================================================== -->
    <div class="header-box">
        <div class="header-title">MAPA MENTAL E ARQUITETURA SISTÊMICA DA FROTA</div>
        <div class="header-subtitle">Plataforma FrotaSaaS Enterprise 2.0 • Telemetria IoT & Decisão Prescritiva</div>
        <div class="header-meta">
            <span><strong>Ambiente:</strong> Produção & Homologação (Porta 8090)</span>
            <span><strong>Backend:</strong> FastAPI • Mongita / MongoDB Brasil</span>
            <span><strong>Autor:</strong> Eduardo Lopes Jonker (PPGCAP / UDESC)</span>
            <span><strong>Data:</strong> Outubro de 2026</span>
        </div>
    </div>

    <div class="section-title">1. Mapa Mental Global da Arquitetura do Sistema</div>
    <p style="font-size: 7.8pt; color: #475569; margin: 0 0 6px 0;">
        A representação vetorial abaixo consolida o ecossistema integrado em 6 dimensões operacionais, estruturando desde a coleta de telemetria M2M nos veículos até a camada de governança corporativa e otimização prescritiva MILP:
    </p>

    <!-- MAPA MENTAL VETORIAL EM SVG -->
    <div class="svg-container">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 430" width="100%" height="410">
            <defs>
                <linearGradient id="gradCenter" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#1e1b4b"/>
                    <stop offset="100%" stop-color="#4338ca"/>
                </linearGradient>
                <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
                    <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.15"/>
                </filter>
            </defs>

            <!-- NÓ CENTRAL -->
            <rect x="290" y="175" width="200" height="75" rx="10" fill="url(#gradCenter)" filter="url(#shadow)"/>
            <text x="390" y="205" fill="#ffffff" font-family="'Liberation Sans', sans-serif" font-weight="900" font-size="12" text-anchor="middle">🚛 FrotaSaaS Enterprise 2.0</text>
            <text x="390" y="222" fill="#c4b5fd" font-family="'Liberation Sans', sans-serif" font-size="8.5" text-anchor="middle">Gestão Integrada de Frotas & IoT</text>
            <text x="390" y="236" fill="#a5b4fc" font-family="'Liberation Sans', sans-serif" font-size="7" text-anchor="middle">FastAPI • Porta 8090 • Soberania LGPD</text>

            <!-- LINHAS CONECTORAS -->
            <!-- Top Left: Telemetria -->
            <path d="M 320 175 C 240 120, 180 90, 130 75" fill="none" stroke="#0284c7" stroke-width="2.5" stroke-dasharray="4,2"/>
            <!-- Top Right: Manutenção -->
            <path d="M 460 175 C 540 120, 600 90, 650 75" fill="none" stroke="#10b981" stroke-width="2.5"/>
            <!-- Mid Left: Combustível -->
            <path d="M 290 212 C 200 212, 170 215, 120 220" fill="none" stroke="#d97706" stroke-width="2.5"/>
            <!-- Mid Right: Viagens -->
            <path d="M 490 212 C 580 212, 610 215, 660 220" fill="none" stroke="#6366f1" stroke-width="2.5"/>
            <!-- Bottom Left: Compliance & RBAC -->
            <path d="M 330 250 C 250 310, 190 340, 130 360" fill="none" stroke="#ef4444" stroke-width="2.5"/>
            <!-- Bottom Right: Prescrição 360 -->
            <path d="M 450 250 C 530 310, 590 340, 650 360" fill="none" stroke="#8b5cf6" stroke-width="3"/>

            <!-- RAMO 1: TELEMETRIA IOT -->
            <g transform="translate(15, 30)">
                <rect width="215" height="80" rx="6" fill="#f0f9ff" stroke="#0284c7" stroke-width="1.5" filter="url(#shadow)"/>
                <text x="12" y="20" fill="#0369a1" font-weight="bold" font-size="10">📡 Telemetria IoT & Rastreamento</text>
                <text x="12" y="36" fill="#334155" font-size="7.5">• Pings GPS Tempo Real (Lat, Lng, Vel, RPM)</text>
                <text x="12" y="48" fill="#334155" font-size="7.5">• Cercas Eletrônicas Geofencing (In/Out)</text>
                <text x="12" y="60" fill="#334155" font-size="7.5">• Eventos Agressivos (Frenagem, Curva, Aceleração)</text>
                <text x="12" y="72" fill="#0284c7" font-size="7" font-weight="bold">Autenticação M2M via Header X-API-Key</text>
            </g>

            <!-- RAMO 2: MANUTENÇÃO & PNEUS -->
            <g transform="translate(550, 30)">
                <rect width="215" height="80" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5" filter="url(#shadow)"/>
                <text x="12" y="20" fill="#047857" font-weight="bold" font-size="10">🔧 Manutenção & Pneus CONTRAN</text>
                <text x="12" y="36" fill="#334155" font-size="7.5">• Ordens de Serviço (Peças, Mão de Obra, Status)</text>
                <text x="12" y="48" fill="#334155" font-size="7.5">• Planos Preventivos por Km e Data</text>
                <text x="12" y="60" fill="#334155" font-size="7.5">• Gestão de Pneus: Sulco mm &lt; 1,6mm Crítico</text>
                <text x="12" y="72" fill="#047857" font-size="7" font-weight="bold">Oficinas Credenciadas & SLA de Reparo</text>
            </g>

            <!-- RAMO 3: ABASTECIMENTO ANTIFRAUDE -->
            <g transform="translate(15, 175)">
                <rect width="215" height="85" rx="6" fill="#fffbeb" stroke="#d97706" stroke-width="1.5" filter="url(#shadow)"/>
                <text x="12" y="20" fill="#b45309" font-weight="bold" font-size="10">⛽ Abastecimento & Antifraude</text>
                <text x="12" y="36" fill="#334155" font-size="7.5">• Auditoria de Volume &gt; Capacidade do Tanque</text>
                <text x="12" y="48" fill="#334155" font-size="7.5">• Trava de Odômetro Decrescente / Regressivo</text>
                <text x="12" y="60" fill="#334155" font-size="7.5">• Autonomia Automática Real (km/L e L/km)</text>
                <text x="12" y="72" fill="#334155" font-size="7.5">• Gestão de Postos Credenciados e Pedágios</text>
                <text x="12" y="82" fill="#b45309" font-size="7" font-weight="bold">Cartões de Frota (Ticket Log, Alelo, VR)</text>
            </g>

            <!-- RAMO 4: VIAGENS & DESPACHO -->
            <g transform="translate(550, 175)">
                <rect width="215" height="85" rx="6" fill="#eef2ff" stroke="#6366f1" stroke-width="1.5" filter="url(#shadow)"/>
                <text x="12" y="20" fill="#4338ca" font-weight="bold" font-size="10">📋 Viagens, Despacho & Vistoria</text>
                <text x="12" y="36" fill="#334155" font-size="7.5">• Solicitação de Viagem por Centro de Custo</text>
                <text x="12" y="48" fill="#334155" font-size="7.5">• Checklist Digital Pré-Viagem Obrigatório</text>
                <text x="12" y="60" fill="#334155" font-size="7.5">• Trava Mecânica: Bloqueio em Não Conforme</text>
                <text x="12" y="72" fill="#334155" font-size="7.5">• Despacho Formal e Mudança de Status Veicular</text>
                <text x="12" y="82" fill="#4338ca" font-size="7" font-weight="bold">Responsabilidade Civil e Segurança Operacional</text>
            </g>

            <!-- RAMO 5: COMPLIANCE DETRAN & SEGURANÇA -->
            <g transform="translate(15, 315)">
                <rect width="215" height="90" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5" filter="url(#shadow)"/>
                <text x="12" y="20" fill="#b91c1c" font-weight="bold" font-size="10">⚖️ Compliance DETRAN & Segurança</text>
                <text x="12" y="36" fill="#334155" font-size="7.5">• Workflow de Indicação de Condutor Infrator</text>
                <text x="12" y="48" fill="#334155" font-size="7.5">• Emissão de Protocolo Oficial DETRAN-IND</text>
                <text x="12" y="60" fill="#334155" font-size="7.5">• Monitoramento de CNH e Toxicológico</text>
                <text x="12" y="72" fill="#334155" font-size="7.5">• Perfis RBAC: ADMIN, GESTOR, OPERADOR</text>
                <text x="12" y="84" fill="#b91c1c" font-size="7" font-weight="bold">Soberania de Dados Nacional (LGPD)</text>
            </g>

            <!-- RAMO 6: INTELIGÊNCIA PRESCRITIVA 360° -->
            <g transform="translate(550, 315)">
                <rect width="215" height="90" rx="6" fill="#f5f3ff" stroke="#8b5cf6" stroke-width="2" filter="url(#shadow)"/>
                <text x="12" y="20" fill="#6d28d9" font-weight="bold" font-size="10">🎯 Inteligência Prescritiva 360°</text>
                <text x="12" y="36" fill="#334155" font-size="7.5">• Prevenção de Falhas Críticas na Estrada (48h)</text>
                <text x="12" y="48" fill="#334155" font-size="7.5">• Manutenção Preventiva Dinâmica (Dia/Hora)</text>
                <text x="12" y="60" fill="#334155" font-size="7.5">• Eficiência Energética (Corte de Marcha Lenta)</text>
                <text x="12" y="72" fill="#334155" font-size="7.5">• Escala Anti-Fadiga & Desinvestimento TCO</text>
                <text x="12" y="84" fill="#6d28d9" font-size="7" font-weight="bold">Economia Potencial Mapeada: R$ 492.464,00</text>
            </g>
        </svg>
    </div>

    <!-- SÍNTESE DE ARQUITETURA -->
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 5px; padding: 6px 10px; font-size: 7.3pt; color: #334155;">
        <strong>Arquitetura Dual-Engine Resiliente:</strong> O sistema opera de forma nativa e sem necessidade de infraestrutura externa utilizando o banco embutido <em>Mongita Disk</em>, com chaveamento instantâneo para <em>MongoDB Server</em> corporativo via variável de ambiente <code>MONGODB_URI</code>. Toda comunicação M2M de telemetria IoT utiliza o cabeçalho seguro <code>X-API-Key</code> com validação de hash criptográfico SHA-256.
    </div>

    <!-- =====================================================================
         PÁGINA 2: FLUXOGRAMAS DOS CICLOS OPERACIONAIS
         ===================================================================== -->
    <div class="page-break"></div>

    <div class="section-title">2. Fluxogramas dos Principais Ciclos Operacionais</div>

    <!-- FLUXOGRAMA 1: DESPACHO E CHECKLIST -->
    <div class="card">
        <div class="card-title"><span class="badge badge-purple">Fluxo 1</span> Despacho Seguro com Trava Mecânica Obrigatória de Checklist</div>
        <div class="svg-container" style="background:#ffffff; margin: 4px 0;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 140" width="100%" height="130">
                <!-- Passos -->
                <!-- 1 -->
                <rect x="10" y="45" width="125" height="50" rx="5" fill="#f1f5f9" stroke="#64748b" stroke-width="1.2"/>
                <text x="72" y="66" font-size="7.5" font-weight="bold" fill="#0f172a" text-anchor="middle">1. Solicitação Viagem</text>
                <text x="72" y="80" font-size="6.5" fill="#475569" text-anchor="middle">Origem, Destino, Centro</text>

                <line x1="135" y1="70" x2="165" y2="70" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>

                <!-- 2 -->
                <rect x="165" y="45" width="135" height="50" rx="5" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.2"/>
                <text x="232" y="66" font-size="7.5" font-weight="bold" fill="#0369a1" text-anchor="middle">2. Vistoria Pré-Viagem</text>
                <text x="232" y="80" font-size="6.5" fill="#475569" text-anchor="middle">Pneus, Freios, Luzes, Óleo</text>

                <line x1="300" y1="70" x2="335" y2="70" stroke="#64748b" stroke-width="1.5"/>

                <!-- Decisão -->
                <polygon points="380,45 425,70 380,95 335,70" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>
                <text x="380" y="73" font-size="6.8" font-weight="bold" fill="#b45309" text-anchor="middle">Aprovado?</text>

                <!-- Não -> Reprovação -->
                <line x1="380" y1="45" x2="380" y2="18" stroke="#ef4444" stroke-width="1.5"/>
                <line x1="380" y1="18" x2="480" y2="18" stroke="#ef4444" stroke-width="1.5"/>
                <rect x="480" y="5" width="220" height="30" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.2"/>
                <text x="590" y="19" font-size="7" font-weight="bold" fill="#b91c1c" text-anchor="middle">TRAVA ATIVADA: REPROVADO_IMPEDIDO</text>
                <text x="590" y="29" font-size="6.2" fill="#7f1d1d" text-anchor="middle">Veículo bloqueado no pátio e OS corretiva aberta</text>

                <!-- Sim -> Despacho -->
                <line x1="425" y1="70" x2="480" y2="70" stroke="#10b981" stroke-width="1.5"/>
                <rect x="480" y="45" width="220" height="50" rx="5" fill="#dcfce7" stroke="#10b981" stroke-width="1.2"/>
                <text x="590" y="66" font-size="7.5" font-weight="bold" fill="#15803d" text-anchor="middle">3. Despacho Liberado (EM_VIAGEM)</text>
                <text x="590" y="80" font-size="6.5" fill="#166534" text-anchor="middle">Status atualizado e rastreador ativo na rota</text>
            </svg>
        </div>
    </div>

    <!-- FLUXOGRAMA 2: TELEMETRIA IOT -->
    <div class="card">
        <div class="card-title"><span class="badge badge-blue">Fluxo 2</span> Ingestão IoT com Autenticação Criptográfica e Detecção de Alertas</div>
        <div class="svg-container" style="background:#ffffff; margin: 4px 0;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 120" width="100%" height="110">
                <rect x="10" y="35" width="120" height="50" rx="5" fill="#f8fafc" stroke="#64748b" stroke-width="1.2"/>
                <text x="70" y="55" font-size="7.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Rastreador GPS 4G</text>
                <text x="70" y="68" font-size="6.5" fill="#475569" text-anchor="middle">Teltonika / Queclink</text>
                <text x="70" y="78" font-size="5.8" fill="#64748b" text-anchor="middle">Pings periódicos (5s-30s)</text>

                <line x1="130" y1="60" x2="175" y2="60" stroke="#0284c7" stroke-width="1.5"/>

                <rect x="175" y="35" width="145" height="50" rx="5" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.2"/>
                <text x="247" y="55" font-size="7.5" font-weight="bold" fill="#0369a1" text-anchor="middle">FastAPI Gateway (8090)</text>
                <text x="247" y="68" font-size="6.5" fill="#475569" text-anchor="middle">Validação Hash SHA-256</text>
                <text x="247" y="78" font-size="5.8" fill="#0284c7" text-anchor="middle">Header X-API-Key</text>

                <line x1="320" y1="60" x2="365" y2="60" stroke="#0284c7" stroke-width="1.5"/>

                <rect x="365" y="35" width="165" height="50" rx="5" fill="#f1f5f9" stroke="#334155" stroke-width="1.2"/>
                <text x="447" y="55" font-size="7.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Motor de Telemetria</text>
                <text x="447" y="68" font-size="6.5" fill="#475569" text-anchor="middle">Cálculo Haversine & Cercas</text>
                <text x="447" y="78" font-size="5.8" fill="#475569" text-anchor="middle">Score Condução (Vel/RPM/Fren)</text>

                <line x1="530" y1="60" x2="575" y2="60" stroke="#0284c7" stroke-width="1.5"/>

                <rect x="575" y="35" width="135" height="50" rx="5" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.2"/>
                <text x="642" y="55" font-size="7.5" font-weight="bold" fill="#6d28d9" text-anchor="middle">Persistência & Alertas</text>
                <text x="642" y="68" font-size="6.5" fill="#5b21b6" text-anchor="middle">MongoDB / Mongita</text>
                <text x="642" y="78" font-size="5.8" fill="#6d28d9" text-anchor="middle">Broadcast Websocket/Push</text>
            </svg>
        </div>
    </div>

    <!-- FLUXOGRAMA 3: AUDITORIA ANTIFRAUDE ABASTECIMENTO -->
    <div class="card">
        <div class="card-title"><span class="badge badge-amber">Fluxo 3</span> Motor de Auditoria Antifraude de Combustível em Tempo Real</div>
        <div class="svg-container" style="background:#ffffff; margin: 4px 0;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 120" width="100%" height="110">
                <rect x="10" y="35" width="130" height="50" rx="5" fill="#f8fafc" stroke="#64748b" stroke-width="1.2"/>
                <text x="75" y="55" font-size="7.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Registro no Posto</text>
                <text x="75" y="68" font-size="6.5" fill="#475569" text-anchor="middle">Cartão Ticket Log / App</text>
                <text x="75" y="78" font-size="5.8" fill="#64748b" text-anchor="middle">Placa, Litros, Km, GPS</text>

                <line x1="140" y1="60" x2="185" y2="60" stroke="#d97706" stroke-width="1.5"/>

                <rect x="185" y="35" width="150" height="50" rx="5" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>
                <text x="260" y="55" font-size="7.5" font-weight="bold" fill="#b45309" text-anchor="middle">Validação Cruzada</text>
                <text x="260" y="68" font-size="6.5" fill="#78350f" text-anchor="middle">Litros vs Capacidade Tanque</text>
                <text x="260" y="78" font-size="5.8" fill="#78350f" text-anchor="middle">Odômetro Atual vs Anterior</text>

                <line x1="335" y1="60" x2="380" y2="60" stroke="#d97706" stroke-width="1.5"/>

                <!-- Ramo Fraude -->
                <rect x="380" y="10" width="155" height="42" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.2"/>
                <text x="457" y="27" font-size="7" font-weight="bold" fill="#b91c1c" text-anchor="middle">ANOMALIA / FRAUDE</text>
                <text x="457" y="39" font-size="6.2" fill="#7f1d1d" text-anchor="middle">Trava Volume ou Km Inconsistente</text>

                <!-- Ramo Regular -->
                <rect x="380" y="65" width="155" height="42" rx="4" fill="#dcfce7" stroke="#10b981" stroke-width="1.2"/>
                <text x="457" y="82" font-size="7" font-weight="bold" fill="#15803d" text-anchor="middle">ABASTECIMENTO HOMOLOGADO</text>
                <text x="457" y="94" font-size="6.2" fill="#166534" text-anchor="middle">Cálculo Autonomia km/L e L/km</text>

                <line x1="535" y1="86" x2="575" y2="86" stroke="#10b981" stroke-width="1.5"/>

                <rect x="575" y="45" width="135" height="45" rx="5" fill="#f1f5f9" stroke="#64748b" stroke-width="1.2"/>
                <text x="642" y="65" font-size="7.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Atualização TCO</text>
                <text x="642" y="77" font-size="6.5" fill="#475569" text-anchor="middle">CPK recalculado na hora</text>
            </svg>
        </div>
    </div>

    <!-- =====================================================================
         PÁGINA 3: DEMONSTRAÇÃO COMPLETA DOS 5 PILARES PRESCRITIVOS
         ===================================================================== -->
    <div class="page-break"></div>

    <div class="section-title purple">3. Demonstração dos 5 Pilares de Inteligência Prescritiva 360°</div>
    <p style="font-size: 7.8pt; color: #475569; margin: 0 0 8px 0;">
        Conforme a parametrização do sistema, a inteligência prescritiva converte dados analíticos brutos em <strong>ações práticas com impacto financeiro mensurável</strong>:
    </p>

    <!-- PILAR 1: MANUTENÇÃO DINÂMICA & FALHAS CRÍTICAS 48H -->
    <div class="card" style="border-left: 4px solid #ef4444;">
        <div class="card-title">
            <span class="badge badge-red">Pilar 1</span> Prevenção de Falhas Críticas na Estrada (48h) & Manutenção Preventiva Dinâmica
        </div>
        <p style="font-size: 7.2pt; color: #475569; margin: 0 0 4px 0;">
            O modelo antecipa panes graves na estrada, calculando a economia evitada em reboques pesados e colapsos mecânicos:
        </p>
        <table class="data-table">
            <thead>
                <tr>
                    <th style="width: 14%;">Veículo / Placa</th>
                    <th style="width: 25%;">Componente em Fadiga</th>
                    <th style="width: 10%;">Janela</th>
                    <th style="width: 15%;">Custo Pane Estrada</th>
                    <th style="width: 15%;">Custo Preventivo</th>
                    <th style="width: 21%;">Economia Evitada / Ação</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>BRA2E19</strong><br/>Scania R 450 6x2</td>
                    <td>Válvula Termostática e Bomba D'água Auxiliar</td>
                    <td><span class="badge badge-red">48 Horas</span></td>
                    <td>R$ 6.800,00</td>
                    <td>R$ 950,00</td>
                    <td style="color:#15803d; font-weight:bold;">+ R$ 5.850,00 evitada<br/><span style="font-size:6pt; color:#475569;">Substituição antes de viagem BR-101</span></td>
                </tr>
                <tr>
                    <td><strong>RHO4A21</strong><br/>Volvo FH 540 6x4</td>
                    <td>Injetor Alta Pressão Common Rail Cilindro #4</td>
                    <td><span class="badge badge-red">48 Horas</span></td>
                    <td>R$ 9.400,00</td>
                    <td>R$ 1.850,00</td>
                    <td style="color:#15803d; font-weight:bold;">+ R$ 7.550,00 evitada<br/><span style="font-size:6pt; color:#475569;">Evita quebra de pistão na serra</span></td>
                </tr>
                <tr>
                    <td><strong>BCX9D45</strong><br/>Sprinter 416 Ambulância</td>
                    <td>Alternador e Tensor Poly-V Auxiliar</td>
                    <td><span class="badge badge-red">48 Horas</span></td>
                    <td>R$ 4.200,00</td>
                    <td>R$ 680,00</td>
                    <td style="color:#15803d; font-weight:bold;">+ R$ 3.520,00 evitada<br/><span style="font-size:6pt; color:#475569;">Evita interrupção em resgate médico</span></td>
                </tr>
            </tbody>
        </table>
        <div style="font-size: 7pt; color: #0369a1; background: #f0f9ff; padding: 4px 6px; border-radius: 4px;">
            <strong>Manutenção Preventiva Dinâmica:</strong> Em vez de paradas arbitrárias a cada 10.000 km, o algoritmo cruza odômetro com o estilo de condução (fator de agressividade 1.0x a 1.35x) e recomenda o dia e hora exatos no vale operacional (ex: <em>Terça-feira às 14:00</em>), reduzindo o tempo ocioso em pátio de 4,0h para 2,5h.
        </div>
    </div>

    <!-- PILAR 2 & 3: PNEUS & COMBUSTÍVEL -->
    <div class="grid-2">
        <div class="grid-col">
            <div class="card" style="border-left: 3px solid #10b981; height: 165px;">
                <div class="card-title"><span class="badge badge-green">Pilar 2</span> Gestão de Pneus CONTRAN</div>
                <table class="data-table" style="font-size: 6.8pt;">
                    <thead>
                        <tr>
                            <th>Nº Fogo</th>
                            <th>Sulco</th>
                            <th>Prescrição Operacional</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>FOG-TEST-999</strong></td>
                            <td><span class="badge badge-red">1.3 mm</span></td>
                            <td><strong>DESCARTE IMEDIATO</strong><br/>Abaixo de 1.6mm CONTRAN. Repor por Michelin X MultiWay (CPK: R$ 0,014/km).</td>
                        </tr>
                        <tr>
                            <td><strong>FOG-SUL-002</strong></td>
                            <td><span class="badge badge-amber">3.0 mm</span></td>
                            <td><strong>RECAUCHUTAGEM (2ª VIDA)</strong><br/>Vulcanizar com banda Bandag BDR-HG (65% economia vs pneu novo).</td>
                        </tr>
                        <tr>
                            <td><strong>FOG-NOR-005</strong></td>
                            <td><span class="badge badge-green">7.5 mm</span></td>
                            <td><strong>ROTAÇÃO CRUZADA</strong><br/>Rodízio aos 8.000 km para nivelar desgaste de ombros.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="grid-col">
            <div class="card" style="border-left: 3px solid #d97706; height: 165px;">
                <div class="card-title"><span class="badge badge-amber">Pilar 3</span> Eficiência de Combustível & Rota</div>
                <div style="font-size: 7.2pt; line-height: 1.35;">
                    <p style="margin: 0 0 4px 0;"><strong>Ação Direta no Veículo BRA2E19:</strong><br/>
                    Consumo 15.4% acima da média por 3h12min diárias em marcha lenta. Prescrito corte de ignição em 5 min e reciclagem do motorista Sebastião (+R$ 2.840,00/mês economizados).</p>
                    <p style="margin: 0 0 4px 0;"><strong>Estratégia de Abastecimento em Rota:</strong><br/>
                    Autonomia de 340 km permite alcançar Posto Credenciado de Itajaí na BR-101 a R$ 5,89/L (R$ 0,90 mais barato por litro que postos de serra da BR-376), gerando R$ 342,00 de economia por abastecimento.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- PILAR 4 & 5: LOGÍSTICA, MOTORISTAS E TCO -->
    <div class="grid-2">
        <div class="grid-col">
            <div class="card" style="border-left: 3px solid #6366f1; height: 160px;">
                <div class="card-title"><span class="badge badge-purple">Pilar 4</span> Logística & Escala Anti-Fadiga</div>
                <div style="font-size: 7.2pt; line-height: 1.35;">
                    <p style="margin: 0 0 4px 0;"><strong>Redirecionamento em Tempo Real:</strong><br/>
                    Acidente no Km 198 da BR-101 com fila de 1h50. Redirecionamento dinâmico via Contorno Viário SC-281 economiza 78 minutos e 34 litros.</p>
                    <p style="margin: 0 0 4px 0;"><strong>Trava de Fadiga (Lei 13.103/2015):</strong><br/>
                    Motorista Fernando Ramos apresentou apenas 6h de descanso nas últimas 24h. Sistema bloqueia escala com parada obrigatória de repouso de 5 horas adicionais.</p>
                </div>
            </div>
        </div>
        <div class="grid-col">
            <div class="card" style="border-left: 3px solid #b45309; height: 160px;">
                <div class="card-title"><span class="badge badge-dark">Pilar 5</span> Desinvestimento & Leilão TCO</div>
                <div style="font-size: 7.2pt; line-height: 1.35;">
                    <p style="margin: 0 0 4px 0;"><strong>Veículo Fiesta MHM8192 (64.8% Venal):</strong><br/>
                    Custo de manutenção superou o teto de 40% do Decreto 47.539/2018. Prescrição: Vender no lote de <em>Novembro/2026</em> para capturar retorno de R$ 16.200 antes de retífica de motor de R$ 6.200.</p>
                    <p style="margin: 0 0 4px 0;"><strong>Economia Consolidada da Frota:</strong><br/>
                    Soma de ações prescritivas estanca R$ 492.464,00 em desperdícios operacionais imediatos.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- =====================================================================
         PÁGINA 4: MATRIZ DE ATORES, ENDPOINTS E DEMONSTRAÇÃO DA REST API
         ===================================================================== -->
    <div class="page-break"></div>

    <div class="section-title emerald">4. Matriz de Perfis RBAC e Catálogo da REST API FastAPI</div>

    <!-- MATRIZ RBAC -->
    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 25%;">Módulo Operacional</th>
                <th style="width: 12%;">ADMIN</th>
                <th style="width: 15%;">GESTOR_FROTA</th>
                <th style="width: 15%;">OPERADOR</th>
                <th style="width: 15%;">MOTORISTA</th>
                <th style="width: 18%;">DISPOSITIVO_IOT</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Painel & Indicadores TCO</strong></td>
                <td><span class="badge badge-green">Total</span></td>
                <td><span class="badge badge-green">Total</span></td>
                <td><span class="badge badge-blue">Leitura Sec.</span></td>
                <td><span class="badge badge-red">Restrito</span></td>
                <td>-</td>
            </tr>
            <tr>
                <td><strong>Ingestão Telemetria / Ping</strong></td>
                <td><span class="badge badge-green">Total</span></td>
                <td><span class="badge badge-blue">Consulta</span></td>
                <td><span class="badge badge-blue">Consulta</span></td>
                <td>-</td>
                <td><span class="badge badge-purple">X-API-Key</span></td>
            </tr>
            <tr>
                <td><strong>Abastecimento Antifraude</strong></td>
                <td><span class="badge badge-green">Total</span></td>
                <td><span class="badge badge-green">Aprovação</span></td>
                <td><span class="badge badge-blue">Registro</span></td>
                <td><span class="badge badge-blue">Consulta</span></td>
                <td>-</td>
            </tr>
            <tr>
                <td><strong>Checklist & Despacho</strong></td>
                <td><span class="badge badge-green">Total</span></td>
                <td><span class="badge badge-green">Auditoria</span></td>
                <td><span class="badge badge-blue">Despacho</span></td>
                <td><span class="badge badge-amber">Preenchimento</span></td>
                <td>-</td>
            </tr>
            <tr>
                <td><strong>Multas & Indicação DETRAN</strong></td>
                <td><span class="badge badge-green">Total</span></td>
                <td><span class="badge badge-green">Protocolo</span></td>
                <td><span class="badge badge-blue">Consulta</span></td>
                <td><span class="badge badge-blue">Consulta</span></td>
                <td>-</td>
            </tr>
            <tr>
                <td><strong>Prescrição Operacional 360°</strong></td>
                <td><span class="badge badge-green">Total</span></td>
                <td><span class="badge badge-green">Total</span></td>
                <td><span class="badge badge-blue">Operação</span></td>
                <td><span class="badge badge-blue">Feedback</span></td>
                <td>-</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">5. Demonstração de Endpoints RESTful Principais (FastAPI)</div>

    <table class="data-table" style="font-size: 7pt;">
        <thead>
            <tr>
                <th style="width: 12%;">Método</th>
                <th style="width: 33%;">Endpoint da API</th>
                <th style="width: 25%;">Segurança / Header</th>
                <th style="width: 30%;">Finalidade e Resposta</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><span class="badge badge-blue">GET</span></td>
                <td><code>/api/health</code></td>
                <td>Público</td>
                <td>Health check e latência da base Mongita/MongoDB.</td>
            </tr>
            <tr>
                <td><span class="badge badge-green">POST</span></td>
                <td><code>/api/auth/login</code></td>
                <td>Argon2id Payload</td>
                <td>Emissão de JWT Bearer Token com claims RBAC.</td>
            </tr>
            <tr>
                <td><span class="badge badge-green">POST</span></td>
                <td><code>/api/telemetry/ping</code></td>
                <td><code>X-API-Key: flt_...</code></td>
                <td>Ingestão M2M, cálculo Haversine e detecção de frenagens.</td>
            </tr>
            <tr>
                <td><span class="badge badge-green">POST</span></td>
                <td><code>/api/fuel/transactions</code></td>
                <td>Bearer Token (OPERADOR)</td>
                <td>Registro com auditoria antifraude de tanque e hodômetro.</td>
            </tr>
            <tr>
                <td><span class="badge badge-green">POST</span></td>
                <td><code>/api/trips/checklists</code></td>
                <td>Bearer Token (MOTORISTA)</td>
                <td>Validação digital pré-viagem com trava impeditiva.</td>
            </tr>
            <tr>
                <td><span class="badge badge-green">POST</span></td>
                <td><code>/api/compliance/fines/{id}/indicar</code></td>
                <td>Bearer Token (GESTOR)</td>
                <td>Workflow DETRAN com emissão de protocolo oficial.</td>
            </tr>
            <tr>
                <td><span class="badge badge-purple">GET</span></td>
                <td><code>/api/reports/prescriptive/full</code></td>
                <td>Bearer Token (GESTOR/ADMIN)</td>
                <td>Relatório master com as 10 prescrições e economia R$.</td>
            </tr>
            <tr>
                <td><span class="badge badge-blue">GET</span></td>
                <td><code>/api/reports/export/csv</code></td>
                <td>Bearer Token</td>
                <td>Exportação contábil RFC 4180 de custos TCO e CPK.</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">6. Conclusões e Diretrizes para Gestores Públicos</div>
    <div style="font-size: 7.3pt; line-height: 1.4; color: #334155; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 5px; padding: 8px 12px;">
        <ol style="margin: 0; padding-left: 16px;">
            <li><strong>Governança de Dados Soberana:</strong> Todos os dados de condutores, frotas e telemetria estão em estrita conformidade com a LGPD e armazenados em infraestrutura nacional auditada.</li>
            <li><strong>Prescrição Ativa no Lugar de Diagnósticos Passivos:</strong> O gestor de frota recebe recomendações imediatas de dia e hora de parada mecânica, desvio de rotas e momentos exatos para envio de pneus à recauchutagem ou leilão de veículos deficitários.</li>
            <li><strong>Zero Setup e Alta Disponibilidade:</strong> A plataforma suporta execução local instantânea (Linux e Windows) com motor <em>Mongita</em> e escala corporativa para nuvem com <em>MongoDB</em>.</li>
        </ol>
    </div>

    <div style="margin-top: 15px; border-top: 1px solid #cbd5e1; padding-top: 5px; font-size: 6.5pt; color: #64748b; text-align: center;">
        Documento Técnico Oficial • Sistema FrotaSaaS Enterprise 2.0 • Dissertação de Mestrado PPGCAP/UDESC • Florianópolis/SC • 2026
    </div>

</body>
</html>
"""

    weasyprint.HTML(string=html_content).write_pdf(str(pdf_out))
    print(f"✔ PDF do Mapa Mental gerado com sucesso em: {pdf_out} ({pdf_out.stat().st_size / 1024:.1f} KB)")
    
    # Sincronização nos diretórios canônicos
    destinos = [
        PDF_DIR / "MAPA_MENTAL_SISTEMA_FROTAS.pdf",
        DOCS_GERAL_DIR / "MAPA_MENTAL_SISTEMA_FROTAS.pdf"
    ]
    for d in destinos:
        shutil.copy2(pdf_out, d)
        print(f"✔ Sincronizado em: {d}")

if __name__ == "__main__":
    gerar_mapa_mental_pdf()

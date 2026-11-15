#!/usr/bin/env python3
"""
Mapeamento de processos (BPM) do projeto em BPMN 2.0.

Cada processo é descrito uma vez, como dados, e gera:
  docs/bpm/<id>.bpmn   BPMN 2.0 com diagrama (abre no Camunda Modeler e no bpmn.io)
  docs/bpm/<id>.svg    diagrama renderizado
  mapeamento_bpm_projeto.pdf  documento com cadeia de valor, diagramas, fichas e
                              matriz de rastreabilidade tarefa → script/artefato

Auditoria: toda tarefa que cita um arquivo do repositório é conferida no disco;
a matriz informa "existe" ou "AUSENTE". Nenhum número de resultado é escrito
aqui; os diagramas descrevem o fluxo, e os resultados ficam nos relatórios.
Uso: .venv/bin/python scripts/gerar_mapeamento_bpm.py
"""
from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import weasyprint

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "bpm"
PDF = ROOT / "mapeamento_bpm_projeto.pdf"

# Tipos: start, timer, end, task (serviço/script), user (humana), gw (exclusivo), sub (subprocesso)
# Nó: (id, tipo, raia, coluna, rótulo, artefato)   Fluxo: (origem, destino, rótulo)
PROCESSOS = [
    {
        "id": "P00_cadeia_valor", "nome": "P00 · Cadeia de valor do projeto",
        "objetivo": "Visão de ponta a ponta: dos dados da SEA/SC e da literatura aos produtos acadêmicos e ao sistema.",
        "gatilho": "Início de um ciclo de pesquisa ou atualização dos dados", "dono": "Mestrando",
        "raias": ["Pesquisador", "Automação (scripts)", "Produtos"],
        "nos": [
            ("s", "start", 0, 0, "Novo ciclo", ""),
            ("t1", "user", 0, 1, "Obter extrações da SEA/SC", "dados/"),
            ("p1", "sub", 1, 2, "P01 Pipeline científico 01–09", "executar_todos_os_scripts.py"),
            ("p3", "sub", 1, 3, "P03 Busca diária de literatura", "scripts/atualizacao_diaria_artigos.sh"),
            ("p4", "sub", 1, 4, "P04 Revisão sistemática PRISMA", "scripts/rsl_prisma.py"),
            ("p5", "sub", 1, 5, "P05 Grafo Neo4j e análise", "scripts/analise_grafos_frotas.py"),
            ("p6", "sub", 1, 6, "P06 Atualização dos relatórios", "scripts/atualizacao_noturna.sh"),
            ("t2", "task", 2, 7, "Dissertação, artigos, SIC, MEP, PBS", "overleaf_dissertacao_udesc/main.tex"),
            ("p7", "sub", 2, 8, "P07 Sistema de gestão (API)", "sistema_gestao_frotas/backend/app/main.py"),
            ("p8", "sub", 0, 9, "P08 Publicação no GitHub", ".gitignore"),
            ("e", "end", 0, 10, "Ciclo concluído", ""),
        ],
        "fluxos": [("s", "t1"), ("t1", "p1"), ("p1", "p3"), ("p3", "p4"), ("p4", "p5"), ("p5", "p6"), ("p6", "t2"),
                   ("t2", "p7"), ("p7", "p8"), ("p8", "e")],
    },
    {
        "id": "P01_pipeline_cientifico", "nome": "P01 · Pipeline científico (etapas 01–09)",
        "objetivo": "Transformar as bases da SEA/SC em resultados auditáveis e testar as hipóteses H1–H4.",
        "gatilho": "executar_tudo.sh ou execução manual de cada etapa", "dono": "Mestrando",
        "raias": ["Bases SEA/SC", "Pipeline (dissertacao_frotas/src)", "Resultados"],
        "nos": [
            ("s", "start", 0, 0, "Bases brutas disponíveis", "dados/Geral_de_OS_23439885_202609110934.csv"),
            ("t01", "task", 1, 1, "01 Auditoria dos dados (SHA-256)", "dissertacao_frotas/src/01_auditoria_dados.py"),
            ("g1", "gw", 1, 2, "Integridade ok?", ""),
            ("x", "end", 0, 2, "Interromper e corrigir fonte", ""),
            ("t02", "task", 1, 3, "02 Pré-processamento e exclusões", "dissertacao_frotas/src/02_preprocessamento.py"),
            ("t03", "task", 1, 4, "03 Estatística descritiva", "dissertacao_frotas/src/03_analise_descritiva.py"),
            ("t04", "task", 1, 5, "04 Modelos preditivos", "dissertacao_frotas/src/04_modelos_preditivos.py"),
            ("t05", "task", 1, 6, "05 Detecção de anomalias", "dissertacao_frotas/src/05_deteccao_anomalias.py"),
            ("t06", "task", 1, 7, "06 Grafos e comunidades", "dissertacao_frotas/src/06_teoria_grafos.py"),
            ("t07", "task", 1, 8, "07 XAI (SHAP × LIME)", "dissertacao_frotas/src/07_explicabilidade_xai.py"),
            ("t08", "task", 1, 9, "08 Otimização MILP", "dissertacao_frotas/src/08_otimizacao_milp.py"),
            ("t09", "task", 1, 10, "09 Validação das hipóteses", "dissertacao_frotas/src/09_validacao_estatistica.py"),
            ("r", "task", 2, 11, "Certificado e tabela oficial", "dissertacao_frotas/resultados/logs/certificado_reprodutibilidade_cientifica.json"),
            ("e", "end", 2, 12, "Resultados publicados", ""),
        ],
        "fluxos": [("s", "t01"), ("t01", "g1"), ("g1", "x", "não"), ("g1", "t02", "sim"), ("t02", "t03"), ("t03", "t04"),
                   ("t04", "t05"), ("t05", "t06"), ("t06", "t07"), ("t07", "t08"), ("t08", "t09"), ("t09", "r"), ("r", "e")],
    },
    {
        "id": "P02_orquestracao", "nome": "P02 · Orquestração integrada (executar_tudo)",
        "objetivo": "Executar em sequência o pipeline, os relatórios, os testes do sistema e a auditoria de segurança.",
        "gatilho": "./executar_tudo.sh", "dono": "Mestrando",
        "raias": ["Orquestrador", "Etapas"],
        "nos": [
            ("s", "start", 0, 0, "executar_tudo.sh", "executar_tudo.sh"),
            ("t1", "sub", 1, 1, "Etapas 01–09 (P01)", "executar_todos_os_scripts.py"),
            ("t2", "task", 1, 2, "10 Compilar dissertação", "scripts/compilar_dissertacao_mestrado_completa.py"),
            ("t3", "task", 1, 3, "11 Laudo de auditoria", "scripts/gerar_relatorio_auditoria_pdf.py"),
            ("t4", "task", 1, 4, "12–13 Abastecimentos", "scripts/processar_abastecimentos.py"),
            ("t5", "task", 1, 5, "14 Frota consolidada e leilão", "scripts/criar_tabela_veiculos_consolidada.py"),
            ("t6", "task", 1, 6, "15–17 Dicionário, artigos, anomalias", "scripts/compilar_relatorio_anomalias_detalhado.py"),
            ("t7", "task", 1, 7, "19–20 Testes do sistema", "sistema_gestao_frotas/testar_sistema.py"),
            ("t8", "task", 1, 8, "21–22 DevSecOps e normas", "scripts/auditoria_seguranca_devsecops.py"),
            ("g", "gw", 0, 9, "Alguma etapa falhou?", ""),
            ("ef", "end", 0, 10, "Resumo com falhas", ""),
            ("e", "end", 1, 10, "Resumo: todas concluídas", ""),
        ],
        "fluxos": [("s", "t1"), ("t1", "t2"), ("t2", "t3"), ("t3", "t4"), ("t4", "t5"), ("t5", "t6"), ("t6", "t7"), ("t7", "t8"),
                   ("t8", "g"), ("g", "ef", "sim"), ("g", "e", "não")],
    },
    {
        "id": "P03_busca_diaria", "nome": "P03 · Busca diária de literatura",
        "objetivo": "Coletar todos os dias artigos novos de acesso aberto, sem raspagem e com controle semântico.",
        "gatilho": "Timer systemd busca-artigos.timer, 08:00, Persistent=true", "dono": "Automação",
        "raias": ["systemd", "Busca (scripts/buscar_artigos.py)", "APIs externas"],
        "nos": [
            ("s", "timer", 0, 0, "08:00 diário", "scripts/instalar_agendamento_diario.sh"),
            ("g0", "gw", 0, 1, "Outra busca em curso? (flock)", "scripts/atualizacao_diaria_artigos.sh"),
            ("x", "end", 0, 2, "Sair sem buscar", ""),
            ("t1", "task", 2, 2, "Consultar OpenAlex e Semantic Scholar", "scripts/buscar_artigos.py"),
            ("t2", "task", 1, 3, "Unir e deduplicar registros", "scripts/buscar_artigos.py"),
            ("g1", "gw", 1, 4, "3 blocos presentes?", ""),
            ("t3", "task", 1, 5, "Marcar como fora do escopo", ""),
            ("g2", "gw", 1, 6, "Versão aberta disponível?", ""),
            ("t4", "task", 2, 7, "Baixar PDF (verifica %PDF)", "scripts/buscar_artigos.py"),
            ("t5", "task", 1, 8, "Gravar resultados, novos e vistos", "artigos/vistos.json"),
            ("e", "end", 0, 9, "Log diário gravado", "artigos/atualizacoes/logs"),
        ],
        "fluxos": [("s", "g0"), ("g0", "x", "sim"), ("g0", "t1", "não"), ("t1", "t2"), ("t2", "g1"), ("g1", "t3", "não"),
                   ("g1", "g2", "sim"), ("t3", "t5"), ("g2", "t4", "sim"), ("g2", "t5", "não"), ("t4", "t5"), ("t5", "e")],
    },
    {
        "id": "P04_revisao_prisma", "nome": "P04 · Revisão sistemática (PRISMA 2020)",
        "objetivo": "Executar o protocolo da PBS de forma rastreável e manter o relatório atualizado a cada incorporação.",
        "gatilho": "Nova exportação de base, PDF manual (CAFe) ou nova execução do fluxo", "dono": "Mestrando (avaliador único)",
        "raias": ["Avaliador", "rsl_prisma.py", "Relatórios"],
        "nos": [
            ("s", "start", 0, 0, "Exportações das bases", "Metodologia de Pesquisa/exportacoes_capes/registro_buscas.csv"),
            ("t1", "task", 1, 1, "01 Identificação e inventário", "revisao_sistematica/dados/01_inventario_fontes.csv"),
            ("t2", "task", 1, 2, "03 Deduplicação", "revisao_sistematica/dados/03_duplicatas.csv"),
            ("t3", "task", 1, 3, "04 Critérios objetivos CO1–CO4", "revisao_sistematica/dados/04_criterios_objetivos.csv"),
            ("t4", "task", 1, 4, "05 Triagem título/resumo", "revisao_sistematica/dados/05_triagem_titulo_resumo.csv"),
            ("g1", "gw", 1, 5, "Texto completo recuperado?", ""),
            ("u0", "user", 0, 6, "Baixar via CAFe (manual)", "revisao_sistematica/textos_para_baixar_CAFe.html"),
            ("t5", "task", 1, 6, "06–07 Elegibilidade no texto", "revisao_sistematica/dados/06_07_texto_completo_elegibilidade.csv"),
            ("t6", "task", 1, 7, "08 Snowballing (OpenAlex)", "revisao_sistematica/dados/08_snowballing.csv"),
            ("t7", "task", 1, 8, "09 Qualidade e extração", "revisao_sistematica/dados/09_extracao_qualidade.csv"),
            ("u1", "user", 0, 9, "Validar inclusões e notas Q1–Q4", "revisao_sistematica/dados/09_validacao_avaliador.csv"),
            ("t8", "task", 2, 10, "Registro de incorporações e protocolo", "scripts/gerar_protocolo_e_relatorio_rsl.py"),
            ("t9", "task", 2, 11, "Relatório da revisão e PBS", "revisao_sistematica/relatorio_revisao_sistematica.pdf"),
            ("e", "end", 2, 12, "Revisão atualizada", ""),
        ],
        "fluxos": [("s", "t1"), ("t1", "t2"), ("t2", "t3"), ("t3", "t4"), ("t4", "g1"), ("g1", "u0", "não"), ("u0", "t1", "novo PDF"),
                   ("g1", "t5", "sim"), ("t5", "t6"), ("t6", "t7"), ("t7", "u1"), ("u1", "t8"), ("t8", "t9"), ("t9", "e")],
    },
    {
        "id": "P05_grafo_neo4j", "nome": "P05 · Grafo veículo–oficina (Neo4j)",
        "objetivo": "Persistir a rede com identificadores pseudonimizados, verificar a carga e testar as comunidades.",
        "gatilho": "Nova base processada de OS", "dono": "Mestrando",
        "raias": ["Operador", "graphdb/load_graph.py", "Análise"],
        "nos": [
            ("s", "start", 0, 0, "Base processada de OS", "dissertacao_frotas/dados/processados/os_consolidadas_processadas.parquet"),
            ("u1", "user", 0, 1, "Criar segredo local (--init-env)", "graphdb/.env.example"),
            ("u2", "user", 0, 2, "Subir Neo4j local (docker compose)", "graphdb/compose.yaml"),
            ("t1", "task", 1, 3, "Pseudonimizar IDs (HMAC-SHA-256)", "graphdb/load_graph.py"),
            ("t2", "task", 1, 4, "Gravar nós, SERVICED_AT e projeção", "graphdb/load_graph.py"),
            ("g1", "gw", 1, 5, "Contagens conferem?", ""),
            ("x", "end", 1, 6, "Falha de carga", ""),
            ("t3", "task", 2, 6, "Testes T1–T3 e análises A1–A5", "scripts/analise_grafos_frotas.py"),
            ("t4", "task", 2, 7, "Artigo 5 e seção 10.x", "scripts/gerar_artigo_grafos.py"),
            ("e", "end", 2, 8, "Resultados do grafo", "dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json"),
        ],
        "fluxos": [("s", "u1"), ("u1", "u2"), ("u2", "t1"), ("t1", "t2"), ("t2", "g1"), ("g1", "x", "não"), ("g1", "t3", "sim"),
                   ("t3", "t4"), ("t4", "e")],
    },
    {
        "id": "P06_atualizacao_relatorios", "nome": "P06 · Atualização dos relatórios sem supervisão",
        "objetivo": "Regenerar todos os relatórios com os dados novos, dentro de um prazo, e comparar métricas com o backup.",
        "gatilho": "systemd-run do usuário com prazo (ex.: 10:00)", "dono": "Automação",
        "raias": ["Pesquisador", "atualizacao_noturna.sh", "Saídas"],
        "nos": [
            ("s", "start", 0, 0, "Disparo com prazo e backup", "scripts/atualizacao_noturna.sh"),
            ("u1", "user", 0, 1, "Copiar resultados para archives/", "archives/"),
            ("g0", "gw", 1, 2, "Pipeline principal em execução?", ""),
            ("t0", "task", 1, 3, "Aguardar término do pipeline", ""),
            ("t1", "task", 1, 4, "Executar próximo gerador (timeout)", "scripts/atualizacao_noturna.sh"),
            ("g1", "gw", 1, 5, "Prazo atingido?", ""),
            ("g2", "gw", 1, 6, "Restam geradores?", ""),
            ("t2", "task", 2, 7, "Comparar JSONs com o backup", ""),
            ("t3", "task", 2, 8, "Gravar RESUMO.md", "logs_atualizacao_noturna"),
            ("u2", "user", 0, 9, "Revisar e publicar", ""),
            ("e", "end", 0, 10, "Fim", ""),
        ],
        "fluxos": [("s", "u1"), ("u1", "g0"), ("g0", "t0", "sim"), ("g0", "t1", "não"), ("t0", "t1"), ("t1", "g1"), ("g1", "t2", "sim"),
                   ("g1", "g2", "não"), ("g2", "t1", "sim"), ("g2", "t2", "não"), ("t2", "t3"), ("t3", "u2"), ("u2", "e")],
    },
    {
        "id": "P07_requisicao_api", "nome": "P07 · Atendimento de requisição no sistema de gestão (API)",
        "objetivo": "Atender uma operação do sistema de frotas com autenticação, controle de acesso por papel e registro.",
        "gatilho": "Requisição HTTP do frontend ou de outro cliente", "dono": "Sistema",
        "raias": ["Usuário / frontend", "Middlewares e segurança", "Rotas e serviços"],
        "nos": [
            ("s", "start", 0, 0, "Requisição HTTP", "sistema_gestao_frotas/frontend/js/api.js"),
            ("t1", "task", 1, 1, "Cabeçalhos, limite de upload, CORS", "sistema_gestao_frotas/backend/app/main.py"),
            ("t2", "task", 1, 2, "Validar token JWT", "sistema_gestao_frotas/backend/app/security/auth.py"),
            ("g1", "gw", 1, 3, "Token válido?", ""),
            ("x1", "end", 0, 4, "401 Não autenticado", ""),
            ("g2", "gw", 1, 4, "Papel permitido?", "sistema_gestao_frotas/backend/app/security/auth.py"),
            ("x2", "end", 0, 5, "403 Acesso restrito", ""),
            ("t3", "task", 2, 5, "Rota do módulo (11 routers)", "sistema_gestao_frotas/backend/app/routes"),
            ("t4", "task", 2, 6, "Serviço de negócio", "sistema_gestao_frotas/backend/app/services"),
            ("t5", "task", 2, 7, "Persistir e registrar", "sistema_gestao_frotas/backend/app/database.py"),
            ("e", "end", 0, 8, "Resposta JSON", ""),
        ],
        "fluxos": [("s", "t1"), ("t1", "t2"), ("t2", "g1"), ("g1", "x1", "não"), ("g1", "g2", "sim"), ("g2", "x2", "não"),
                   ("g2", "t3", "sim"), ("t3", "t4"), ("t4", "t5"), ("t5", "e")],
    },
    {
        "id": "P08_publicacao", "nome": "P08 · Publicação no repositório público",
        "objetivo": "Publicar código e resultados sem dados administrativos, textos de terceiros ou segredos.",
        "gatilho": "Decisão do pesquisador de publicar", "dono": "Mestrando",
        "raias": ["Pesquisador", "Verificações"],
        "nos": [
            ("s", "start", 0, 0, "Mudanças prontas", ""),
            ("t1", "task", 1, 1, "Aplicar .gitignore (dados, PDFs, caches)", ".gitignore"),
            ("t2", "task", 1, 2, "Arquivos > 50 MB?", ""),
            ("t3", "task", 1, 3, "Buscar segredos no conteúdo", ""),
            ("g1", "gw", 1, 4, "Algum problema?", ""),
            ("u1", "user", 0, 5, "Remover do índice / corrigir", ""),
            ("u2", "user", 0, 6, "Commit e push", ""),
            ("e", "end", 0, 7, "Publicado", ""),
        ],
        "fluxos": [("s", "t1"), ("t1", "t2"), ("t2", "t3"), ("t3", "g1"), ("g1", "u1", "sim"), ("u1", "t1"), ("g1", "u2", "não"), ("u2", "e")],
    },
]

BPMN_TAG = {"start": "startEvent", "timer": "startEvent", "end": "endEvent", "task": "serviceTask", "user": "userTask",
            "gw": "exclusiveGateway", "sub": "callActivity"}
TIPO_TXT = {"start": "evento inicial", "timer": "evento inicial temporizado", "end": "evento final", "task": "tarefa automática",
            "user": "tarefa humana", "gw": "decisão (exclusiva)", "sub": "subprocesso"}
COL_W, LANE_H, X0, LANE_LABEL = 150, 130, 40, 34
TW, TH, EV, GW = 118, 62, 34, 44


def tam(tipo):
    return (EV, EV) if tipo in ("start", "timer", "end") else (GW, GW) if tipo == "gw" else (TW, TH)


def geometria(p):
    pos = {}
    for nid, tipo, lane, col, rot, art in p["nos"]:
        w, h = tam(tipo)
        cx = X0 + LANE_LABEL + 20 + col * COL_W + TW / 2
        cy = lane * LANE_H + LANE_H / 2
        pos[nid] = (cx - w / 2, cy - h / 2, w, h, cx, cy)
    ncol = max(n[3] for n in p["nos"]) + 1
    largura = X0 + LANE_LABEL + 40 + ncol * COL_W
    return pos, largura, len(p["raias"]) * LANE_H


def rota(pos, a, b):
    xa, ya, wa, ha, cxa, cya = pos[a]
    xb, yb, wb, hb, cxb, cyb = pos[b]
    if abs(cya - cyb) < 1:
        if cxb > cxa:
            return [(xa + wa, cya), (xb, cyb)]
        return [(cxa, ya + ha), (cxa, ya + ha + 22), (cxb, ya + ha + 22), (cxb, yb + hb)]
    if cxb > cxa:
        sx = xa + wa if cya != cyb else xa + wa
        mx = (xa + wa + xb) / 2
        return [(xa + wa, cya), (mx, cya), (mx, cyb), (xb, cyb)]
    if abs(cxb - cxa) < 1:
        return [(cxa, ya + ha if cyb > cya else ya), (cxb, yb if cyb > cya else yb + hb)]
    return [(cxa, ya if cyb < cya else ya + ha), (cxa, cyb), (xb + wb, cyb)]


# ---------------------------------------------------------------- BPMN XML
def gerar_bpmn(p) -> str:
    NS = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL", "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
          "dc": "http://www.omg.org/spec/DD/20100524/DC", "di": "http://www.omg.org/spec/DD/20100524/DI"}
    for k, v in NS.items():
        ET.register_namespace(k, v)
    b = lambda t: f"{{{NS['bpmn']}}}{t}"
    d = lambda t: f"{{{NS['bpmndi']}}}{t}"
    defs = ET.Element(b("definitions"), {"id": f"Defs_{p['id']}", "targetNamespace": "https://udesc.br/ppgcap/frota-bpm",
                                         "exporter": "scripts/gerar_mapeamento_bpm.py", "exporterVersion": "1"})
    collab = ET.SubElement(defs, b("collaboration"), {"id": f"Col_{p['id']}"})
    pid = f"Proc_{p['id']}"
    ET.SubElement(collab, b("participant"), {"id": f"Part_{p['id']}", "name": p["nome"], "processRef": pid})
    proc = ET.SubElement(defs, b("process"), {"id": pid, "name": p["nome"], "isExecutable": "false"})
    doc = ET.SubElement(proc, b("documentation"))
    doc.text = f"Objetivo: {p['objetivo']} | Gatilho: {p['gatilho']} | Dono: {p['dono']}"
    ls = ET.SubElement(proc, b("laneSet"), {"id": f"LS_{p['id']}"})
    lanes = [ET.SubElement(ls, b("lane"), {"id": f"L{i}_{p['id']}", "name": n}) for i, n in enumerate(p["raias"])]
    entra, sai = {}, {}
    for i, f in enumerate(p["fluxos"]):
        sai.setdefault(f[0], []).append(f"F{i}"); entra.setdefault(f[1], []).append(f"F{i}")
    for nid, tipo, lane, col, rot, art in p["nos"]:
        el = ET.SubElement(proc, b(BPMN_TAG[tipo]), {"id": nid, "name": rot})
        if art:
            ET.SubElement(el, b("documentation")).text = f"Artefato: {art}"
        for fid in entra.get(nid, []):
            ET.SubElement(el, b("incoming")).text = fid
        for fid in sai.get(nid, []):
            ET.SubElement(el, b("outgoing")).text = fid
        if tipo == "timer":
            ted = ET.SubElement(el, b("timerEventDefinition"), {"id": f"TD_{nid}"})
            ET.SubElement(ted, b("timeCycle")).text = "R/PT24H"
        ET.SubElement(lanes[lane], b("flowNodeRef")).text = nid
    for i, f in enumerate(p["fluxos"]):
        at = {"id": f"F{i}", "sourceRef": f[0], "targetRef": f[1]}
        if len(f) > 2:
            at["name"] = f[2]
        ET.SubElement(proc, b("sequenceFlow"), at)
    pos, W, H = geometria(p)
    dg = ET.SubElement(defs, d("BPMNDiagram"), {"id": f"D_{p['id']}"})
    pl = ET.SubElement(dg, d("BPMNPlane"), {"id": f"PL_{p['id']}", "bpmnElement": f"Col_{p['id']}"})
    def shape(el, x, y, w, h, extra=None):
        s = ET.SubElement(pl, d("BPMNShape"), {"id": f"S_{el}", "bpmnElement": el, **(extra or {})})
        ET.SubElement(s, f"{{{NS['dc']}}}Bounds", {"x": f"{x:.0f}", "y": f"{y:.0f}", "width": f"{w:.0f}", "height": f"{h:.0f}"})
    shape(f"Part_{p['id']}", X0, 0, W - X0, H, {"isHorizontal": "true"})
    for i in range(len(p["raias"])):
        shape(f"L{i}_{p['id']}", X0 + LANE_LABEL, i * LANE_H, W - X0 - LANE_LABEL, LANE_H, {"isHorizontal": "true"})
    for nid, (x, y, w, h, *_ ) in pos.items():
        shape(nid, x, y, w, h)
    for i, f in enumerate(p["fluxos"]):
        e_ = ET.SubElement(pl, d("BPMNEdge"), {"id": f"E_F{i}", "bpmnElement": f"F{i}"})
        for x, y in rota(pos, f[0], f[1]):
            ET.SubElement(e_, f"{{{NS['di']}}}waypoint", {"x": f"{x:.0f}", "y": f"{y:.0f}"})
    ET.indent(defs)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(defs, encoding="unicode")


# ---------------------------------------------------------------- SVG
def quebrar(t, n=17):
    linhas, l = [], ""
    for w in t.split():
        if len(l) + len(w) + 1 > n and l:
            linhas.append(l); l = w
        else:
            l = (l + " " + w).strip()
    return linhas + [l]


def gerar_svg(p) -> str:
    e = html.escape
    pos, W, H = geometria(p)
    S = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W + 10:.0f} {H + 10:.0f}' font-family='Arial' font-size='10'>",
         "<defs><marker id='a' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto'>"
         "<path d='M0,0L10,5L0,10z' fill='#333'/></marker></defs>",
         f"<rect x='{X0}' y='0' width='{W - X0}' height='{H}' fill='#fff' stroke='#333'/>"]
    for i, n in enumerate(p["raias"]):
        y = i * LANE_H
        S.append(f"<rect x='{X0}' y='{y}' width='{LANE_LABEL}' height='{LANE_H}' fill='#00693e' stroke='#333'/>")
        S.append(f"<rect x='{X0 + LANE_LABEL}' y='{y}' width='{W - X0 - LANE_LABEL}' height='{LANE_H}' fill='{'#f6faf8' if i % 2 else '#fff'}' stroke='#999'/>")
        S.append(f"<text transform='translate({X0 + LANE_LABEL / 2 + 4},{y + LANE_H / 2}) rotate(-90)' text-anchor='middle' fill='#fff' font-size='9' font-weight='bold'>"
                 + "".join(f"<tspan x='0' dy='{0 if k == 0 else 10}'>{e(t)}</tspan>" for k, t in enumerate(quebrar(n, 22)[:2])) + "</text>")
    for i, f in enumerate(p["fluxos"]):
        pts = rota(pos, f[0], f[1])
        S.append("<polyline fill='none' stroke='#333' stroke-width='1.1' marker-end='url(#a)' points='"
                 + " ".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "'/>")
        if len(f) > 2:
            (x1, y1), (x2, y2) = pts[0], pts[1]
            S.append(f"<text x='{(x1 + x2) / 2 + 3:.0f}' y='{(y1 + y2) / 2 - 4:.0f}' font-size='8.5' fill='#b04a3a'>{e(f[2])}</text>")
    for nid, tipo, lane, col, rot, art in p["nos"]:
        x, y, w, h, cx, cy = pos[nid]
        if tipo in ("start", "timer", "end"):
            sw = 3 if tipo == "end" else 1.5
            S.append(f"<circle cx='{cx}' cy='{cy}' r='{w / 2}' fill='#fff' stroke='{'#b04a3a' if tipo == 'end' else '#00693e'}' stroke-width='{sw}'/>")
            if tipo == "timer":
                S.append(f"<circle cx='{cx}' cy='{cy}' r='{w / 2 - 4}' fill='none' stroke='#00693e'/><path d='M{cx},{cy - 8} L{cx},{cy} L{cx + 6},{cy}' stroke='#00693e' fill='none'/>")
            ty = cy + w / 2 + 11
            for k, t in enumerate(quebrar(rot, 20)):
                S.append(f"<text x='{cx}' y='{ty + 10 * k}' text-anchor='middle' font-size='8.5'>{e(t)}</text>")
        elif tipo == "gw":
            S.append(f"<polygon points='{cx},{y} {x + w},{cy} {cx},{y + h} {x},{cy}' fill='#fff7e0' stroke='#d99a00' stroke-width='1.5'/>"
                     f"<text x='{cx}' y='{cy + 5}' text-anchor='middle' font-size='14' fill='#d99a00'>×</text>")
            for k, t in enumerate(quebrar(rot, 20)):
                S.append(f"<text x='{cx}' y='{y - 14 + 10 * k - 10 * (len(quebrar(rot, 20)) - 1)}' text-anchor='middle' font-size='8.5'>{e(t)}</text>")
        else:
            fill = {"task": "#eef5f1", "user": "#e8eef8", "sub": "#ffffff"}[tipo]
            S.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='8' fill='{fill}' stroke='#00693e' stroke-width='{2.2 if tipo == 'sub' else 1.2}'/>")
            if tipo == "user":
                S.append(f"<circle cx='{x + 10}' cy='{y + 9}' r='3.5' fill='none' stroke='#1b3a6e'/><path d='M{x + 4},{y + 19} q6,-8 12,0' fill='none' stroke='#1b3a6e'/>")
            elif tipo == "task":
                S.append(f"<circle cx='{x + 10}' cy='{y + 10}' r='4.5' fill='none' stroke='#00693e' stroke-dasharray='2 1.5'/>")
            else:
                S.append(f"<rect x='{cx - 6}' y='{y + h - 13}' width='12' height='11' fill='none' stroke='#00693e'/><text x='{cx}' y='{y + h - 4}' text-anchor='middle' font-size='10'>+</text>")
            ls_ = quebrar(rot, 19)[:4]
            for k, t in enumerate(ls_):
                S.append(f"<text x='{cx}' y='{cy - 5 * (len(ls_) - 1) + 10 * k + 3}' text-anchor='middle' font-size='9'>{e(t)}</text>")
    S.append("</svg>")
    return "\n".join(S)


# ---------------------------------------------------------------- PDF
CSS = """
@page { size: A4 landscape; margin: 1.4cm 1.5cm; @bottom-right { content: counter(page) " / " counter(pages); font: 8pt Arial; color:#555; }
        @bottom-left { content: "Mapeamento BPM do projeto · BPMN 2.0"; font: 8pt Arial; color:#555; } }
body { font-family: Arial, sans-serif; font-size: 9.5pt; line-height: 1.38; color:#1d1d1d; }
h1 { color:#00693e; font-size: 20pt; margin: 0 0 4pt; } .sub { color:#444; margin-bottom: 10pt; }
h2 { color:#00693e; font-size: 13.5pt; border-bottom: 1.5pt solid #00693e; padding-bottom: 2pt; margin: 0 0 6pt; page-break-before: always; }
h3 { font-size: 10.5pt; margin: 8pt 0 3pt; }
table { width:100%; border-collapse: collapse; margin: 3pt 0 8pt; font-size: 8pt; }
th { background:#00693e; color:#fff; text-align:left; padding: 2.5pt 4pt; } td { border-bottom: .5pt solid #c9d6cf; padding: 2pt 4pt; vertical-align: top; }
tr:nth-child(even) td { background:#f3f8f5; } code { font-family: 'DejaVu Sans Mono', monospace; font-size: 7.6pt; }
img { width: 100%; max-height: 11.5cm; object-fit: contain; } .ficha td:first-child { width: 16%; font-weight: bold; }
.aus { color:#b04a3a; font-weight:bold; } .ok { color:#00693e; }
.leg span { display:inline-block; margin-right: 12pt; }
"""


def gerar_pdf(verif):
    e = html.escape
    hoje = date.today().strftime("%d/%m/%Y")
    total_art = sum(1 for v in verif if v[3])
    ausentes = [v for v in verif if v[3] and not v[4]]
    H = [f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>",
         "<h1>Mapeamento de processos (BPM) do projeto</h1>",
         f"<p class='sub'>Analítica prescritiva para a frota pública de Santa Catarina · PPGCAP/UDESC · Eduardo Lopes Jonker · BPMN 2.0 · "
         f"gerado em {hoje} por <code>scripts/gerar_mapeamento_bpm.py</code></p>",
         "<h3>Como ler</h3><p>Cada processo está em notação BPMN 2.0, com raias (quem executa), eventos (círculos: verde = início, vermelho = fim), "
         "tarefas (retângulos: automática ou humana), subprocessos (borda grossa e +) e decisões exclusivas (losangos). Os arquivos <code>docs/bpm/*.bpmn</code> "
         "abrem no Camunda Modeler e no bpmn.io e podem ser editados. Cada tarefa cita o script ou artefato que a executa; a matriz de rastreabilidade "
         f"no final confere esses arquivos no disco ({total_art - len(ausentes)} de {total_art} encontrados).</p>",
         "<table><tr><th>Processo</th><th>Objetivo</th><th>Gatilho</th><th>Dono</th><th>Tarefas</th><th>Decisões</th><th>Arquivo BPMN</th></tr>"]
    for p in PROCESSOS:
        nt = sum(1 for n in p["nos"] if n[1] in ("task", "user", "sub"))
        ng = sum(1 for n in p["nos"] if n[1] == "gw")
        H.append(f"<tr><td><b>{e(p['nome'])}</b></td><td>{e(p['objetivo'])}</td><td>{e(p['gatilho'])}</td><td>{e(p['dono'])}</td>"
                 f"<td>{nt}</td><td>{ng}</td><td><code>docs/bpm/{p['id']}.bpmn</code></td></tr>")
    H.append("</table>")
    for p in PROCESSOS:
        H.append(f"<h2>{e(p['nome'])}</h2>")
        H.append(f"<table class='ficha'><tr><td>Objetivo</td><td>{e(p['objetivo'])}</td></tr><tr><td>Gatilho</td><td>{e(p['gatilho'])}</td></tr>"
                 f"<tr><td>Dono</td><td>{e(p['dono'])}</td></tr><tr><td>Raias</td><td>{e(' · '.join(p['raias']))}</td></tr></table>")
        H.append(f"<img src='{(OUT / (p['id'] + '.svg')).as_uri()}'>")
        H.append("<h3>Atividades</h3><table><tr><th>Elemento</th><th>Tipo</th><th>Raia</th><th>Executado por / artefato</th><th>Situação</th></tr>")
        for nid, tipo, lane, col, rot, art in p["nos"]:
            v = next(x for x in verif if x[0] == p["id"] and x[1] == nid)
            sit = "" if not art else ("<span class='ok'>existe</span>" if v[4] else "<span class='aus'>AUSENTE</span>")
            H.append(f"<tr><td>{e(rot)}</td><td>{TIPO_TXT[tipo]}</td><td>{e(p['raias'][lane])}</td><td><code>{e(art)}</code></td><td>{sit}</td></tr>")
        H.append("</table>")
    H.append("<h2>Matriz de rastreabilidade</h2><p>Todos os artefatos citados nos processos, conferidos no disco na geração deste documento.</p>")
    H.append("<table><tr><th>Processo</th><th>Elemento</th><th>Artefato</th><th>Situação</th></tr>")
    vistos = set()
    for pid, nid, rot, art, ok in verif:
        if art and (pid, art) not in vistos:
            vistos.add((pid, art))
            H.append(f"<tr><td>{e(pid)}</td><td>{e(rot)}</td><td><code>{e(art)}</code></td><td>{'<span class=ok>existe</span>' if ok else '<span class=aus>AUSENTE</span>'}</td></tr>")
    H.append("</table></body></html>")
    weasyprint.HTML(string="\n".join(H), base_url=str(ROOT)).write_pdf(PDF)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    verif = []
    for p in PROCESSOS:
        ids = {n[0] for n in p["nos"]}
        for f in p["fluxos"]:
            assert f[0] in ids and f[1] in ids, f"{p['id']}: fluxo com nó inexistente {f}"
        xml = gerar_bpmn(p)
        ET.fromstring(xml.split("\n", 1)[1])  # valida XML bem-formado
        (OUT / f"{p['id']}.bpmn").write_text(xml, encoding="utf-8")
        (OUT / f"{p['id']}.svg").write_text(gerar_svg(p), encoding="utf-8")
        for nid, tipo, lane, col, rot, art in p["nos"]:
            verif.append((p["id"], nid, rot, art, bool(art) and (ROOT / art).exists()))
    gerar_pdf(verif)
    aus = [v for v in verif if v[3] and not v[4]]
    print(f"OK: {len(PROCESSOS)} processos -> docs/bpm/*.bpmn|svg e {PDF.name}; artefatos ausentes: {len(aus)}")
    for v in aus:
        print("   AUSENTE:", v[0], v[2], v[3])


if __name__ == "__main__":
    main()

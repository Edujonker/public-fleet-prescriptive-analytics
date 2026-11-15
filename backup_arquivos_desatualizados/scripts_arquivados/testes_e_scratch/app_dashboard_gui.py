#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
DASHBOARD DESKTOP PROFISSIONAL EM PYQT6 COM COPILOTO DE IA (PPGCAP/UDESC)
================================================================================
Dissertação: Analítica Preditiva e Prescritiva para Gestão de Frota Veicular Pública
Autor: Eduardo Lopes Jonker
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes
Ano: 2026

Recursos:
- Interface gráfica nativa profissional com tema Dark Moderno e Glassmorphism
- Copiloto de Inteligência Artificial em Linguagem Natural integrado
- Botão "Gerar Relatório (PDF)" não bloqueante via QThread
- Botão "Atualizar Gráficos & Pipeline" com recarregamento em tempo real
- Visualizador científico de figuras em 300 DPI com zoom e navegação
- Painel interativo de parametrização estatística (tempo, tipo, testes)
================================================================================
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

# Garantir diretório base
BASE_DIR = Path(__file__).resolve().parent.parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

# Importação do PyQt6
try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
    from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QLinearGradient
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
        QScrollArea, QFrame, QSplitter, QProgressBar, QComboBox,
        QDoubleSpinBox, QSpinBox, QMessageBox, QGridLayout, QSizePolicy
    )
except ImportError:
    print("Erro: PyQt6 não encontrado. Execute: pip install PyQt6")
    sys.exit(1)

# Importação do Assistente de IA
try:
    from src.ai_assistant import FleetAIAssistant
    ai_engine = FleetAIAssistant()
except Exception as e:
    print(f"Aviso ao carregar motor de IA: {e}")
    ai_engine = None

# Diretórios
RELATORIOS_DIR = BASE_DIR / "relatorios"
CHARTS_DIR = BASE_DIR / "charts"
GRAFICOS_DIR = BASE_DIR / "graficos"
PDF_FILE = BASE_DIR / "relatorios_pdf" / "relatorio_dissertacao_completo.pdf"

# ==============================================================================
# ESTILOS QSS PROFISSIONAIS (DARK THEME MODERNO)
# ==============================================================================
DARK_QSS = """
QMainWindow {
    background-color: #0b0f19;
}
QWidget {
    font-family: 'Inter', 'Segoe UI', 'DejaVu Sans', sans-serif;
    color: #e2e8f0;
    font-size: 13px;
}
QFrame.kpi-card {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #131b2e, stop:1 #0f172a);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 12px;
}
QFrame.kpi-card:hover {
    border: 1px solid #38bdf8;
    background: #172554;
}
QPushButton {
    background: #1e293b;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
    color: #f8fafc;
}
QPushButton:hover {
    background: #334155;
    border-color: #38bdf8;
}
QPushButton:pressed {
    background: #0f172a;
}
QPushButton.btn-primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #2563eb);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #ffffff;
}
QPushButton.btn-primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #1d4ed8);
    border-color: #7dd3fc;
}
QPushButton.btn-action {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
    border: 1px solid rgba(16, 185, 129, 0.4);
}
QPushButton.btn-action:hover {
    background: #047857;
}
QPushButton.chip-btn {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 14px;
    padding: 5px 12px;
    font-size: 11.5px;
    color: #93c5fd;
}
QPushButton.chip-btn:hover {
    background: #1e3a8a;
    border-color: #60a5fa;
    color: #ffffff;
}
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    background: #0f172a;
    top: -1px;
}
QTabBar::tab {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    color: #94a3b8;
}
QTabBar::tab:selected {
    background: #0f172a;
    border-color: #38bdf8;
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
}
QTabBar::tab:hover:!selected {
    background: #1e293b;
    color: #f1f5f9;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #38bdf8;
    background: #0b1329;
}
QScrollBar:vertical {
    border: none;
    background: #0f172a;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 25px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QProgressBar {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    text-align: center;
    background: #111827;
    color: #f8fafc;
    font-weight: 600;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #10b981);
    border-radius: 5px;
}
"""

# ==============================================================================
# WORKERS EM THREAD SEPARADA (NÃO TRAVAM A INTERFACE)
# ==============================================================================
class PipelineWorker(QThread):
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(str)

    def __init__(self, custom_args: Optional[list] = None):
        super().__init__()
        self.custom_args = custom_args or []

    def run(self):
        try:
            self.progress_signal.emit("Executando pipeline metodológico estatístico...")
            cmd = [sys.executable, str(BASE_DIR / "scripts" / "pipeline_metodologico_estatistico.py")] + self.custom_args
            import subprocess
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.finished_signal.emit(True, "Pipeline executado e figuras 76 a 79 atualizadas com sucesso!")
            else:
                self.finished_signal.emit(False, f"Falha na execução:\n{res.stderr[:400]}")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class ReportWorker(QThread):
    finished_signal = pyqtSignal(bool, str)

    def run(self):
        try:
            cmd = [sys.executable, str(BASE_DIR / "scripts" / "04_compilar_relatorio_pdf.py")]
            import subprocess
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.finished_signal.emit(True, "Relatório PDF acadêmico (18MB) compilado com sucesso!")
            else:
                self.finished_signal.emit(False, f"Falha na compilação:\n{res.stderr[:400]}")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


# ==============================================================================
# JANELA PRINCIPAL DO SISTEMA
# ==============================================================================
class FleetAnalyticsDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analítica Prescritiva & Gestão Inteligente de Frotas • PPGCAP/UDESC 2026")
        self.resize(1340, 880)
        self.setStyleSheet(DARK_QSS)

        # Container Principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(18, 16, 18, 16)
        self.main_layout.setSpacing(14)

        # Construção da Interface
        self._build_header()
        self._build_kpi_bar()
        self._build_tabs()
        self._build_status_bar()

    # --- 1. CABEÇALHO EXECUTIVO ---
    def _build_header(self):
        header_layout = QHBoxLayout()

        # Bloco de Título
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        badge_lbl = QLabel("UDESC • CCT • PPGCAP 2026")
        badge_lbl.setStyleSheet("color: #38bdf8; font-weight: 700; font-size: 11px; letter-spacing: 0.5px;")
        
        main_title = QLabel("Analítica Prescritiva & Gestão Inteligente da Frota Veicular Pública")
        main_title.setStyleSheet("font-size: 19px; font-weight: 800; color: #f8fafc;")

        authorship = QLabel("Autor: Eduardo Lopes Jonker • Orientadora: Profa. Dra. VIVIAN KREMER KALEMPA • Coorientador: Prof. Dr. YURI KASZUBOWSKI LOPES")
        authorship.setStyleSheet("color: #94a3b8; font-size: 11.5px;")

        title_box.addWidget(badge_lbl)
        title_box.addWidget(main_title)
        title_box.addWidget(authorship)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Botões de Ação Solicitados
        self.btn_update_charts = QPushButton("⚡ Atualizar Gráficos")
        self.btn_update_charts.setObjectName("btn_update_charts")
        self.btn_update_charts.setToolTip("Reexecuta o pipeline estatístico e recarrega todas as figuras científicas")
        self.btn_update_charts.clicked.connect(self.trigger_pipeline_update)

        self.btn_generate_pdf = QPushButton("📄 Gerar Relatório (PDF)")
        self.btn_generate_pdf.setObjectName("btn_generate_pdf")
        self.btn_generate_pdf.setProperty("class", "btn-primary")
        self.btn_generate_pdf.setToolTip("Compila o relatório acadêmico formal de 18MB via WeasyPrint")
        self.btn_generate_pdf.clicked.connect(self.trigger_report_generation)

        self.btn_open_pdf = QPushButton("📂 Abrir PDF")
        self.btn_open_pdf.setToolTip("Abre o arquivo PDF gerado no visualizador do sistema")
        self.btn_open_pdf.clicked.connect(self.open_generated_pdf)

        header_layout.addWidget(self.btn_update_charts)
        header_layout.addWidget(self.btn_generate_pdf)
        header_layout.addWidget(self.btn_open_pdf)

        self.main_layout.addLayout(header_layout)

    # --- 2. BARRA DE CARDS KPI ---
    def _build_kpi_bar(self):
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(12)

        cards = [
            ("Ordens de Serviço (OS)", "350.737", "Base 2020 a 2026", "#38bdf8"),
            ("Veículos Monitorados", "7.580 placas", "Painel Veículo-Mês", "#818cf8"),
            ("Gasto Efetivo Auditado", "R$ 138,76M", "Aprovado em Manutenção", "#34d399"),
            ("Classificador Campeão", "PR-AUC 0,9099", "HistGradientBoosting", "#10b981"),
            ("Redução Erro Custo", "MAE R$ 895", "Ganho Ablativo M+P", "#f59e0b"),
            ("Economia Prescritiva", "R$ 380 mil/ano", "Otimização MILP", "#c084fc")
        ]

        for title, val, meta, color in cards:
            frame = QFrame()
            frame.setProperty("class", "kpi-card")
            f_box = QVBoxLayout(frame)
            f_box.setContentsMargins(12, 10, 12, 10)
            f_box.setSpacing(3)

            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("font-size: 11px; color: #94a3b8; font-weight: 600;")
            lbl_v = QLabel(val)
            lbl_v.setStyleSheet(f"font-size: 16px; color: {color}; font-weight: 800;")
            lbl_m = QLabel(meta)
            lbl_m.setStyleSheet("font-size: 10px; color: #64748b;")

            f_box.addWidget(lbl_t)
            f_box.addWidget(lbl_v)
            f_box.addWidget(lbl_m)
            kpi_layout.addWidget(frame)

        self.main_layout.addLayout(kpi_layout)

    # --- 3. ABAS DO SISTEMA ---
    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Aba 1: Copiloto de IA em Linguagem Natural
        self.tab_chat = QWidget()
        self._setup_tab_chat()
        self.tabs.addTab(self.tab_chat, "🤖 Copiloto de IA da Frota")

        # Aba 2: Pipeline Metodológico & Modelagem Estocástica (Figuras 76 a 79)
        self.tab_pipeline = QWidget()
        self._setup_tab_pipeline()
        self.tabs.addTab(self.tab_pipeline, "📐 Pipeline Metodológico & Estocástico")

        # Aba 3: Configuração Parametrizada de Testes
        self.tab_config = QWidget()
        self._setup_tab_config()
        self.tabs.addTab(self.tab_config, "⚙️ Parâmetros de Teste & Execução")

        # Aba 4: Galeria Completa das Figuras Científicas
        self.tab_galeria = QWidget()
        self._setup_tab_galeria()
        self.tabs.addTab(self.tab_galeria, "📊 Auditoria, ML & Prescrição")

        self.main_layout.addWidget(self.tabs, stretch=1)

    # --- SETUP ABA 1: COPILOTO DE IA EM LINGUAGEM NATURAL ---
    def _setup_tab_chat(self):
        layout = QVBoxLayout(self.tab_chat)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Histórico da Conversa
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #0b1120;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 14px;
                font-size: 13.5px;
                line-height: 1.5;
            }
        """)
        self._append_ai_message(
            "Olá, Eduardo! Sou o **Copiloto de IA e Analítica da Frota** (PPGCAP/UDESC).\n\n"
            "Fui integrado diretamente aos dados auditados de 350 mil OS e aos modelos da sua dissertação. "
            "Respondo qualquer dúvida metodológica em linguagem natural, executo atualizações de parâmetros "
            "e **aprendo continuamente** com seus questionamentos.\n\n"
            "💡 *Você pode clicar em uma das sugestões abaixo ou digitar livremente sua dúvida ou comando.*"
        )
        layout.addWidget(self.chat_history, stretch=1)

        # Barra de Chips com Sugestões Rápidas
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(8)

        suggestions = [
            ("Custos são normais?", "Os custos de manutenção seguem distribuição normal?"),
            ("Taxa de quebra (Poisson)", "Qual é a taxa diária de falhas por Poisson e há sobredispersão?"),
            ("Tempo em manutenção (Markov)", "Quanto tempo um veículo passa em manutenção pela Cadeia de Markov?"),
            ("ETS vs ARIMA", "Qual modelo de série temporal é superior, ETS ou ARIMA?"),
            ("Atualizar com α=0.01", "Atualize os gráficos com alfa = 0.01 e frequência semanal"),
            ("Compilar PDF", "Gere o relatório em PDF agora")
        ]

        for label, full_prompt in suggestions:
            btn = QPushButton(label)
            btn.setProperty("class", "chip-btn")
            btn.clicked.connect(lambda _, p=full_prompt: self.send_chat_message(p))
            chips_layout.addWidget(btn)

        chips_layout.addStretch()
        layout.addLayout(chips_layout)

        # Barra de Entrada de Texto
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Pergunte em linguagem natural ou dê um comando (ex: 'Atualize os gráficos com alfa de 0.01')...")
        self.chat_input.returnPressed.connect(lambda: self.send_chat_message(self.chat_input.text()))

        self.btn_send_chat = QPushButton("Enviar")
        self.btn_send_chat.setProperty("class", "btn-primary")
        self.btn_send_chat.clicked.connect(lambda: self.send_chat_message(self.chat_input.text()))

        input_layout.addWidget(self.chat_input, stretch=1)
        input_layout.addWidget(self.btn_send_chat)
        layout.addLayout(input_layout)

    def _append_ai_message(self, text: str):
        formatted = text.replace("\n", "<br>").replace("**", "<b>").replace("<b>", "<strong>").replace("</b>", "</strong>")
        self.chat_history.append(f"""
            <div style="margin-bottom: 12px; padding: 10px 14px; background: rgba(30, 41, 59, 0.6); border-radius: 8px; border-left: 3px solid #38bdf8;">
                <span style="color: #38bdf8; font-weight: bold;">🤖 Copiloto da Frota:</span><br>
                <span style="color: #f1f5f9;">{formatted}</span>
            </div>
        """)

    def _append_user_message(self, text: str):
        self.chat_history.append(f"""
            <div style="margin-bottom: 12px; padding: 10px 14px; background: rgba(2, 132, 199, 0.15); border-radius: 8px; border-right: 3px solid #2563eb; text-align: right;">
                <span style="color: #60a5fa; font-weight: bold;">👤 Pesquisador:</span><br>
                <span style="color: #ffffff;">{text}</span>
            </div>
        """)

    def send_chat_message(self, text: str):
        query = text.strip()
        if not query:
            return
        self.chat_input.clear()
        self._append_user_message(query)

        if ai_engine is None:
            self._append_ai_message("Erro: O motor de IA não está inicializado.")
            return

        # Processamento inteligente
        resp_dict = ai_engine.process_query(query)
        self._append_ai_message(resp_dict.get('resposta', 'Sem resposta gerada.'))

        # Se a ação envolveu atualizar gráficos, recarrega o visualizador
        if resp_dict.get('acao_executada') == 'update_charts':
            self.reload_pipeline_view()

    # --- SETUP ABA 2: PIPELINE ESTATÍSTICO & ESTOCÁSTICO ---
    def _setup_tab_pipeline(self):
        layout = QHBoxLayout(self.tab_pipeline)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        # Painel Esquerdo: Visualizador de Imagens
        left_panel = QVBoxLayout()
        
        # Seletor de Figuras
        fig_selector_box = QHBoxLayout()
        fig_selector_box.addWidget(QLabel("Figura Científica:"))
        self.combo_fig = QComboBox()
        self.fig_map = {
            "Figura 76, Passo 1: Q-Q Plots e Normalidade (Lilliefors)": "fig76_pipeline_normalidade_qqplots.png",
            "Figura 77, Passo 2: Testes de Hipóteses Condicionais": "fig77_testes_hipoteses_subgrupos.png",
            "Figura 78, Passo 3.1: Falhas por Poisson & Markov de Prontidão": "fig78_processos_estocasticos_poisson_markov.png",
            "Figura 79, Passo 3.2: Séries Temporais ETS vs ARIMA": "fig79_series_temporais_ets_vs_arima.png"
        }
        for k in self.fig_map.keys():
            self.combo_fig.addItem(k)
        self.combo_fig.currentIndexChanged.connect(self.display_selected_figure)
        fig_selector_box.addWidget(self.combo_fig, stretch=1)
        left_panel.addLayout(fig_selector_box)

        # Scroll Area da Imagem
        self.img_scroll = QScrollArea()
        self.img_scroll.setWidgetResizable(True)
        self.img_scroll.setStyleSheet("background: #0b1120; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;")
        
        self.lbl_image = QLabel("Carregando figura científica...")
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_scroll.setWidget(self.lbl_image)
        left_panel.addWidget(self.img_scroll, stretch=1)

        layout.addLayout(left_panel, stretch=2)

        # Painel Direito: Resumo dos Indicadores e Interpretação
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)

        lbl_side_title = QLabel("Evidências Estatísticas Auditadas")
        lbl_side_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #38bdf8;")
        right_panel.addWidget(lbl_side_title)

        self.stat_summary_box = QTextEdit()
        self.stat_summary_box.setReadOnly(True)
        self.stat_summary_box.setStyleSheet("background: #0f172a; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px;")
        right_panel.addWidget(self.stat_summary_box, stretch=1)

        layout.addLayout(right_panel, stretch=1)

        # Carregar primeira figura
        self.display_selected_figure()

    def display_selected_figure(self):
        curr_text = self.combo_fig.currentText()
        filename = self.fig_map.get(curr_text, "fig76_pipeline_normalidade_qqplots.png")
        img_path = GRAFICOS_DIR / filename
        if not img_path.exists():
            img_path = CHARTS_DIR / filename

        if img_path.exists():
            pix = QPixmap(str(img_path))
            scaled_pix = pix.scaledToWidth(760, Qt.TransformationMode.SmoothTransformation)
            self.lbl_image.setPixmap(scaled_pix)
        else:
            self.lbl_image.setText(f"Figura não encontrada:\n{filename}\nClique em 'Atualizar Gráficos' para gerar.")

        # Atualizar resumo lateral conforme figura
        if "76" in filename:
            self.stat_summary_box.setHtml("""
                <h4 style="color:#38bdf8; margin:0;">Passo 1: Normalidade dos Dados</h4>
                <p><b>Teste:</b> Kolmogorov-Smirnov com correção de Lilliefors (n ≥ 2000)</p>
                <p><b>Custos de Manutenção:</b> D = 0,3329 | p = 0,0010 (p < 10⁻¹⁶)</p>
                <p><b>Assimetria:</b> +8,29 | <b>Curtose:</b> +137,67 (Leptocúrtica extrema)</p>
                <p><b>Decisão:</b> Rejeição categórica de normalidade (α = 0,05).</p>
                <hr style="border:0; border-top:1px solid #334155;">
                <p style="color:#94a3b8; font-size:11px;"><i>Fundamentação: Veta OLS e modelos lineares clássicos.</i></p>
            """)
        elif "77" in filename:
            self.stat_summary_box.setHtml("""
                <h4 style="color:#38bdf8; margin:0;">Passo 2: Testes de Hipóteses</h4>
                <p><b>2 Grupos (Leves vs Pesados):</b> Mann-Whitney U = 7,70×10⁷ (p < 10⁻¹⁵⁰), efeito r = 0,144.</p>
                <p><b>3+ Grupos (Categorias):</b> Kruskal-Wallis H = 915,32 (p < 10⁻¹⁹⁰).</p>
                <p><b>Associação Categórica:</b> Qui-Quadrado χ² = 103,83, gl = 6, p < 10⁻¹⁶, V de Cramér = 0,1183.</p>
                <hr style="border:0; border-top:1px solid #334155;">
                <p style="color:#94a3b8; font-size:11px;"><i>Diferenças estatisticamente significantes confirmadas.</i></p>
            """)
        elif "78" in filename:
            self.stat_summary_box.setHtml("""
                <h4 style="color:#38bdf8; margin:0;">Passo 3.1: Modelagem Estocástica</h4>
                <p><b>Processo de Poisson:</b> λ = 19,67 falhas/dia na frota.</p>
                <p><b>Razão Variância/Média:</b> VMR = 1.592,34 >> 1,0 (p < 10⁻¹⁶).</p>
                <p><b>Diagnóstico:</b> Sobredispersão severa (refuta Poisson puro).</p>
                <hr style="border:0; border-top:1px solid #334155;">
                <p><b>Cadeia de Markov de Prontidão (Equilíbrio π):</b></p>
                <p>• Em Trânsito: 33,4% (retenção 4,3 dias)</p>
                <p>• Ocioso: 29,0% (retenção 4,6 dias)</p>
                <p>• Em Manutenção: 37,6% (retenção 5,8 dias)</p>
            """)
        elif "79" in filename:
            self.stat_summary_box.setHtml("""
                <h4 style="color:#38bdf8; margin:0;">Passo 3.2: Séries Temporais</h4>
                <p><b>Teste ADF:</b> -5,489 (p = 0,0000 -> Estacionária em nível).</p>
                <p><b>ETS (Holt-Winters):</b> RMSE = R$ 95.926,07 | MAE = R$ 90.723,30 | AIC = 1.181,4</p>
                <p><b>ARIMA(1,0,0):</b> RMSE = R$ 89.672,96 | MAE = R$ 81.207,72 | AIC = 1.306,0</p>
                <hr style="border:0; border-top:1px solid #334155;">
                <p style="color:#10b981;"><b>Vencedor:</b> ARIMA(1,0,0) superou ETS em validação out-of-sample.</p>
            """)

    def reload_pipeline_view(self):
        self.display_selected_figure()

    # --- SETUP ABA 3: CONFIGURAÇÃO PARAMETRIZADA ---
    def _setup_tab_config(self):
        layout = QVBoxLayout(self.tab_config)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Painel de Parametrização dos Testes Estatísticos")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #38bdf8;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(14)

        # 1. Nível de Significância Alfa
        grid.addWidget(QLabel("Nível de Significância (α):"), 0, 0)
        self.spin_alpha = QDoubleSpinBox()
        self.spin_alpha.setRange(0.001, 0.20)
        self.spin_alpha.setSingleStep(0.01)
        self.spin_alpha.setValue(0.05)
        grid.addWidget(self.spin_alpha, 0, 1)

        # 2. Limiar de Shapiro-Wilk
        grid.addWidget(QLabel("Limiar Amostral Shapiro vs Lilliefors:"), 0, 2)
        self.spin_shapiro = QSpinBox()
        self.spin_shapiro.setRange(500, 10000)
        self.spin_shapiro.setSingleStep(500)
        self.spin_shapiro.setValue(2000)
        grid.addWidget(self.spin_shapiro, 0, 3)

        # 3. Teste de Homogeneidade de Variâncias
        grid.addWidget(QLabel("Teste de Variância:"), 1, 0)
        self.combo_var = QComboBox()
        self.combo_var.addItems(["Levene", "Bartlett"])
        grid.addWidget(self.combo_var, 1, 1)

        # 4. Modo de Hipóteses
        grid.addWidget(QLabel("Modo do Teste de Hipóteses:"), 1, 2)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["auto (Condicional à Normalidade)", "parametrico (Forçar t/ANOVA)", "nao-parametrico (Forçar Mann-Whitney/Kruskal)"])
        grid.addWidget(self.combo_mode, 1, 3)

        # 5. Frequência Temporal
        grid.addWidget(QLabel("Frequência de Séries Temporais:"), 2, 0)
        self.combo_freq = QComboBox()
        self.combo_freq.addItem("ME (Mensal)", "ME")
        self.combo_freq.addItem("W (Semanal)", "W")
        self.combo_freq.addItem("D (Diária)", "D")
        grid.addWidget(self.combo_freq, 2, 1)

        # 6. Horizonte de Previsão
        grid.addWidget(QLabel("Horizonte de Previsão (Passos):"), 2, 2)
        self.spin_horiz = QSpinBox()
        self.spin_horiz.setRange(2, 36)
        self.spin_horiz.setValue(6)
        grid.addWidget(self.spin_horiz, 2, 3)

        # 7. Tipo de Manutenção
        grid.addWidget(QLabel("Tipo de Manutenção:"), 3, 0)
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["TODAS", "CORRETIVA", "PREVENTIVA"])
        grid.addWidget(self.combo_tipo, 3, 1)

        # 8. Amostra
        grid.addWidget(QLabel("Amostra Máxima (0 = Todas):"), 3, 2)
        self.spin_sample = QSpinBox()
        self.spin_sample.setRange(0, 350000)
        self.spin_sample.setSingleStep(10000)
        self.spin_sample.setValue(40000)
        grid.addWidget(self.spin_sample, 3, 3)

        layout.addLayout(grid)

        # Botão de Aplicação
        self.btn_apply_params = QPushButton("💾 Salvar Parâmetros e Reexecutar Pipeline Completo")
        self.btn_apply_params.setProperty("class", "btn-action")
        self.btn_apply_params.clicked.connect(self.apply_custom_params_and_run)
        layout.addWidget(self.btn_apply_params)

        layout.addStretch()

    def apply_custom_params_and_run(self):
        freq_code = self.combo_freq.currentData() or "ME"
        mode_val = "auto"
        if "parametrico" in self.combo_mode.currentText() and "nao" not in self.combo_mode.currentText():
            mode_val = "parametrico"
        elif "nao-parametrico" in self.combo_mode.currentText():
            mode_val = "nao-parametrico"

        args = [
            "--alpha", str(self.spin_alpha.value()),
            "--limiar-shapiro", str(self.spin_shapiro.value()),
            "--teste-variancia", self.combo_var.currentText().lower(),
            "--modo-hipotese", mode_val,
            "--frequencia", freq_code,
            "--horizonte", str(self.spin_horiz.value()),
            "--tipo-manutencao", self.combo_tipo.currentText(),
            "--amostra", str(self.spin_sample.value())
        ]

        self.trigger_pipeline_update(custom_args=args)

    # --- SETUP ABA 4: GALERIA COMPLETA ---
    def _setup_tab_galeria(self):
        layout = QVBoxLayout(self.tab_galeria)
        layout.setContentsMargins(14, 14, 14, 14)

        top_sel = QHBoxLayout()
        top_sel.addWidget(QLabel("Selecione a Evidência do Anteprojeto:"))

        self.combo_galeria = QComboBox()
        galeria_items = [
            ("Figura 01, Distribuição de Status de OS", "fig01_status_distribuicao.png"),
            ("Figura 04, Auditoria de Hodômetro e Saltos Negativos", "fig04_auditoria_hodometro.png"),
            ("Figura 05, Estabilidade Jaccard do Isolation Forest", "fig05_iforest_estabilidade_jaccard.png"),
            ("Figura 07, Curvas Precision-Recall (Classificação)", "fig07_classificacao_pr_curves.png"),
            ("Figura 10, Regressão Não Linear de Custos", "fig10_regressao_comparativo_mae_rmse.png"),
            ("Figura 12, Estudo Ablativo M vs M+P", "fig12_ablativo_fontes_m_vs_mp.png"),
            ("Figura 14, Otimização MILP e Sensibilidade", "fig14_otimizacao_sensibilidade_orcamento.png"),
            ("Figura 32, Economia Contrafactual por Cenário", "fig32_comparativo_economia_politicas.png"),
            ("Figura 73, Algoritmo de Saneamento de Hodômetro", "fig73_algoritmo_saneamento_hodometro.png")
        ]
        self.galeria_files = {}
        for title, fn in galeria_items:
            self.combo_galeria.addItem(title)
            self.galeria_files[title] = fn

        self.combo_galeria.currentIndexChanged.connect(self.display_galeria_image)
        top_sel.addWidget(self.combo_galeria, stretch=1)
        layout.addLayout(top_sel)

        self.scroll_galeria = QScrollArea()
        self.scroll_galeria.setWidgetResizable(True)
        self.scroll_galeria.setStyleSheet("background: #0b1120; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;")

        self.lbl_galeria_img = QLabel("Selecione um gráfico acima...")
        self.lbl_galeria_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_galeria.setWidget(self.lbl_galeria_img)
        layout.addWidget(self.scroll_galeria, stretch=1)

        self.display_galeria_image()

    def display_galeria_image(self):
        sel = self.combo_galeria.currentText()
        fn = self.galeria_files.get(sel, "fig01_status_distribuicao.png")
        p = CHARTS_DIR / fn
        if not p.exists():
            p = GRAFICOS_DIR / fn

        if p.exists():
            pix = QPixmap(str(p))
            scaled = pix.scaledToWidth(880, Qt.TransformationMode.SmoothTransformation)
            self.lbl_galeria_img.setPixmap(scaled)
        else:
            self.lbl_galeria_img.setText(f"Arquivo não encontrado: {fn}")

    # --- 4. BARRA DE STATUS INFERIOR ---
    def _build_status_bar(self):
        status_box = QHBoxLayout()
        self.lbl_status = QLabel("Sistema Pronto • PPGCAP/UDESC • Base de Dados: 350.737 OS")
        self.lbl_status.setStyleSheet("color: #64748b; font-size: 11px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setFixedWidth(140)
        self.progress_bar.setVisible(False)

        status_box.addWidget(self.lbl_status)
        status_box.addStretch()
        status_box.addWidget(self.progress_bar)
        self.main_layout.addLayout(status_box)

    # --- CONTROLE DAS AÇÕES EM BACKGROUND ---
    def trigger_pipeline_update(self, custom_args: Optional[list] = None):
        self.btn_update_charts.setEnabled(False)
        self.btn_update_charts.setText("⏳ Atualizando...")
        self.progress_bar.setVisible(True)
        self.lbl_status.setText("Executando testes estatísticos e gerando figuras 76 a 79...")

        self.p_worker = PipelineWorker(custom_args)
        self.p_worker.finished_signal.connect(self._on_pipeline_finished)
        self.p_worker.start()

    def _on_pipeline_finished(self, success: bool, message: str):
        self.btn_update_charts.setEnabled(True)
        self.btn_update_charts.setText("⚡ Atualizar Gráficos")
        self.progress_bar.setVisible(False)

        if success:
            self.lbl_status.setText("Gráficos e testes atualizados com sucesso!")
            self.reload_pipeline_view()
            QMessageBox.information(self, "Sucesso", message)
        else:
            self.lbl_status.setText("Falha na atualização do pipeline.")
            QMessageBox.warning(self, "Inconsistência", message)

    def trigger_report_generation(self):
        self.btn_generate_pdf.setEnabled(False)
        self.btn_generate_pdf.setText("⏳ Compilando...")
        self.progress_bar.setVisible(True)
        self.lbl_status.setText("Compilando relatório formal em PDF via WeasyPrint (300 DPI)...")

        self.r_worker = ReportWorker()
        self.r_worker.finished_signal.connect(self._on_report_finished)
        self.r_worker.start()

    def _on_report_finished(self, success: bool, message: str):
        self.btn_generate_pdf.setEnabled(True)
        self.btn_generate_pdf.setText("📄 Gerar Relatório (PDF)")
        self.progress_bar.setVisible(False)

        if success:
            self.lbl_status.setText("Relatório em PDF gerado com sucesso!")
            res = QMessageBox.question(
                self, "Relatório Compilado",
                "O relatório acadêmico de 18MB foi gerado com sucesso!\nDeseja abri-lo agora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if res == QMessageBox.StandardButton.Yes:
                self.open_generated_pdf()
        else:
            self.lbl_status.setText("Falha ao compilar relatório PDF.")
            QMessageBox.warning(self, "Erro de Compilação", message)

    def open_generated_pdf(self):
        if PDF_FILE.exists():
            webbrowser.open(str(PDF_FILE))
        else:
            QMessageBox.information(self, "Aviso", "O arquivo PDF ainda não foi gerado. Clique em 'Gerar Relatório (PDF)'.")


# ==============================================================================
# PONTO DE ENTRADA DO APLICATIVO
# ==============================================================================
def main():
    app = QApplication(sys.argv)
    window = FleetAnalyticsDashboard()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

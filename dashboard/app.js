/**
 * ================================================================================
 * LÓGICA INTERATIVA E COPILOTO DE IA DO DASHBOARD (PPGCAP/UDESC 2026)
 * ================================================================================
 * Autor: Eduardo Lopes Jonker
 * Orientadora: Profa. Dra. Vivian Kremer Kalempa
 * Coorientador: Prof. Dr. Yuri Kaszubowski Lopes
 *
 * Funcionalidades:
 * - Navegação ágil por abas temáticas
 * - Simulador Prescritivo Interativo (MILP)
 * - Visualizador Lightbox em Alta Definição (300 DPI) com zoom
 * - Ações Rápidas:
 *     * Atualizar Gráficos & Pipeline Metodológico (POST /api/atualizar-graficos)
 *     * Compilar Relatório Oficial em PDF (POST /api/gerar-relatorio)
 *     * Recarregamento instantâneo de cache de imagens
 *     * Executar Pipeline Parametrizado (α, frequência, horizonte)
 * - Copiloto de IA em Linguagem Natural com Aprendizado Contínuo (POST /api/chat)
 * - Sistema de Notificações Toast Moderno
 * ================================================================================
 */

// Dados das simulações prescritivas (MILP) geradas no teste temporal
const prescriptiveData = {
    50: {
        budgetLabel: "50% (Cenário Reduzido: R$ 137.227,50)",
        intervencoes: "304 veículos",
        custo: "R$ 8.330.655,73",
        risco: "72,62%",
        economia: "+2,18% (R$ 185.494,69)"
    },
    75: {
        budgetLabel: "75% (Cenário Intermediário: R$ 205.841,25)",
        intervencoes: "457 veículos",
        custo: "R$ 8.240.844,99",
        risco: "71,21%",
        economia: "+3,23% (R$ 275.305,43)"
    },
    100: {
        budgetLabel: "100% (Cenário Base: R$ 274.455,00)",
        intervencoes: "609 veículos",
        custo: "R$ 8.152.969,01",
        risco: "69,83%",
        economia: "+4,26% (R$ 363.181,41)"
    },
    125: {
        budgetLabel: "125% (Cenário Expandido: R$ 343.068,75)",
        intervencoes: "762 veículos",
        custo: "R$ 8.065.409,17",
        risco: "68,44%",
        economia: "+5,29% (R$ 450.741,25)"
    },
    150: {
        budgetLabel: "150% (Cenário Pleno: R$ 411.682,50)",
        intervencoes: "914 veículos",
        custo: "R$ 7.979.175,35",
        risco: "67,07%",
        economia: "+6,31% (R$ 536.975,07)"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initPrescriptiveSlider();
    initKeyboardShortcuts();
    initChatWelcome();
    atualizarSimulacaoOrcamento();
});

// ==============================================================================
// 1. NAVEGAÇÃO ENTRE ABAS
// ==============================================================================
function initTabs() {
    const tabButtons = Array.from(document.querySelectorAll('.nav-tab'));
    const tabPanes = Array.from(document.querySelectorAll('.tab-pane'));

    function activateTab(btn) {
        const targetTabId = btn.getAttribute('data-tab');

        // Atualiza botões
        tabButtons.forEach(b => {
            b.classList.remove('active');
            b.setAttribute('aria-selected', 'false');
            b.setAttribute('tabindex', '-1');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        btn.setAttribute('tabindex', '0');
        btn.focus();

        // Atualiza painéis
        tabPanes.forEach(pane => {
            if (pane.id === targetTabId) {
                pane.classList.add('active');
            } else {
                pane.classList.remove('active');
            }
        });

        // Se for a aba de grafos, inicializa ou redimensiona o canvas interativo
        if (targetTabId === 'tab-grafos') {
            setTimeout(() => {
                if (typeof initGrafoCanvas === 'function') {
                    initGrafoCanvas();
                }
            }, 80);
        }

        // Rolagem suave para o início da área principal
        window.scrollTo({ top: 130, behavior: 'smooth' });
    }

    tabButtons.forEach((btn, index) => {
        btn.addEventListener('click', () => activateTab(btn));

        // Navegação acessível por teclado (WCAG 2.1 - Tabs Pattern)
        btn.addEventListener('keydown', (e) => {
            let targetIndex = null;
            if (e.key === 'ArrowRight') {
                targetIndex = (index + 1) % tabButtons.length;
            } else if (e.key === 'ArrowLeft') {
                targetIndex = (index - 1 + tabButtons.length) % tabButtons.length;
            } else if (e.key === 'Home') {
                targetIndex = 0;
            } else if (e.key === 'End') {
                targetIndex = tabButtons.length - 1;
            }

            if (targetIndex !== null) {
                e.preventDefault();
                activateTab(tabButtons[targetIndex]);
            }
        });
    });
}

// ==============================================================================
// 2. SIMULADOR PRESCRITIVO INTERATIVO (MILP)
// ==============================================================================
function initPrescriptiveSlider() {
    const slider = document.getElementById('budget-slider');
    const label = document.getElementById('slider-val-label');
    const elIntervencoes = document.getElementById('sim-intervencoes');
    const elCusto = document.getElementById('sim-custo');
    const elRisco = document.getElementById('sim-risco');
    const elEconomia = document.getElementById('sim-economia');

    if (!slider) return;

    slider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        const data = prescriptiveData[val];

        if (data) {
            label.textContent = data.budgetLabel;
            if (elIntervencoes) elIntervencoes.textContent = data.intervencoes;
            if (elCusto) elCusto.textContent = data.custo;
            if (elRisco) elRisco.textContent = data.risco;
            if (elEconomia) elEconomia.textContent = data.economia;
        }
    });
}

// ==============================================================================
// 3. VISUALIZADOR LIGHTBOX (300 DPI)
// ==============================================================================
function openLightbox(imgSrc, title) {
    const modal = document.getElementById('lightbox-modal');
    const modalImg = document.getElementById('lightbox-img');
    const modalTitle = document.getElementById('lightbox-title');

    if (!modal || !modalImg) return;

    // Preserva o cache busting se já existir
    modalImg.src = imgSrc;
    if (modalTitle) modalTitle.textContent = title || "Visualização Ampliada (300 DPI)";
    modal.style.display = 'flex';
}

function closeLightbox(event) {
    if (!event || event.target.id === 'lightbox-modal' || event.target.classList.contains('lightbox-close')) {
        const modal = document.getElementById('lightbox-modal');
        if (modal) modal.style.display = 'none';
    }
}

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('lightbox-modal');
            if (modal && modal.style.display === 'flex') {
                modal.style.display = 'none';
            }
            const drawer = document.getElementById('ai-chat-drawer');
            if (drawer && drawer.classList.contains('open')) {
                toggleAIChat();
            }
        }
    });
}

// ==============================================================================
// 4. NOTIFICAÇÕES TOAST MODERNAS
// ==============================================================================
function showToast(message, type = 'info', duration = 4500) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';
    if (type === 'loading') icon = '⏳';

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-text">${message}</span>
    `;

    container.appendChild(toast);

    // Animação de entrada
    requestAnimationFrame(() => {
        toast.classList.add('visible');
    });

    // Auto remoção
    setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 350);
    }, duration);
}

// ==============================================================================
// 5. BOTÕES PRINCIPAIS: ATUALIZAR GRÁFICOS, GERAR PDF E RECARREGAR
// ==============================================================================

/**
 * Reexecuta o pipeline metodológico estatístico e regenera as figuras 76 a 79.
 */
async function atualizarGraficosPipeline() {
    const btn = document.getElementById('btn-atualizar-graficos');
    const originalHtml = btn ? btn.innerHTML : '';

    if (btn) {
        btn.disabled = true;
        btn.classList.add('loading');
        btn.innerHTML = `
            <span class="spinner"></span>
            <span>Recalculando...</span>
        `;
    }

    showToast('⚡ Reexecutando testes de normalidade, Poisson, Markov e ARIMA...', 'loading', 6000);

    try {
        const response = await fetch('/api/atualizar-graficos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ origem: 'botao_topo' })
        });

        if (!response.ok) {
            throw new Error(`Servidor retornou status HTTP ${response.status}`);
        }

        const data = await response.json();
        recarregarTodasImagens();
        showToast('✅ Figuras 76, 77, 78 e 79 recalculadas e atualizadas com sucesso!', 'success', 5000);

        // Se o drawer do chat estiver aberto ou visível, adiciona notificação
        if (data.resposta) {
            appendChatMessage('Copiloto de IA', data.resposta, true);
        }
    } catch (err) {
        console.error('Erro ao atualizar gráficos:', err);
        showToast(`Erro ao atualizar gráficos: ${err.message}. Verifique se 'python3 run_dashboard.py' está em execução.`, 'error', 6000);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('loading');
            btn.innerHTML = originalHtml;
        }
    }
}

/**
 * Executa o pipeline com parâmetros customizados definidos na Aba 10.
 */
async function executarPipelineComParametros() {
    const alpha = document.getElementById('quick-param-alpha')?.value || '0.05';
    const freq = document.getElementById('quick-param-freq')?.value || 'ME';
    const horizon = document.getElementById('quick-param-horizon')?.value || '6';

    showToast(`⚡ Aplicando α = ${alpha}, Freq = ${freq}, Horizonte = ${horizon}...`, 'loading', 6000);

    try {
        const response = await fetch('/api/atualizar-graficos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                alpha: parseFloat(alpha),
                frequencia: freq,
                horizonte: parseInt(horizon)
            })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        recarregarTodasImagens();
        showToast(`✅ Parâmetros aplicados! Figuras atualizadas para α=${alpha} e ${freq}.`, 'success', 5000);

        if (data.resposta) {
            appendChatMessage('Copiloto de IA', data.resposta, true);
        }
    } catch (err) {
        console.error('Erro na parametrização:', err);
        showToast(`Falha ao aplicar parâmetros: ${err.message}`, 'error', 5000);
    }
}

/**
 * Resolve o caminho do PDF para funcionar tanto em servidor HTTP (localhost)
 * quanto quando aberto diretamente pelo sistema de arquivos (protocolo file://).
 */
function resolverUrlPdf(caminho) {
    const limpo = caminho.replace(/^\/+/, '');
    if (window.location.protocol === 'file:') {
        return '../' + limpo;
    }
    // Adiciona timestamp para evitar cache e garantir a versão mais recente
    return '/' + limpo + (limpo.indexOf('?') === -1 ? `?t=${Date.now()}` : `&t=${Date.now()}`);
}

/**
 * Abre o PDF de forma robusta e garantida, evitando bloqueios de pop-up do navegador
 * e fornecendo link direto no Toast caso o navegador bloqueie novas abas.
 */
function abrirPdfRobusto(url, titulo) {
    let win = null;
    try {
        win = window.open(url, '_blank');
    } catch (e) {
        console.warn('window.open interceptado:', e);
    }

    if (!win || win.closed || typeof win.closed === 'undefined') {
        try {
            const link = document.createElement('a');
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            document.body.appendChild(link);
            link.click();
            setTimeout(() => link.remove(), 400);
        } catch (err) {
            console.warn('Fallback por tag <a> falhou:', err);
        }
    }

    showToast(`📄 <strong>${titulo}</strong> pronto! <a href="${url}" target="_blank" style="color: #38bdf8; text-decoration: underline; font-weight: 700; margin-left: 6px;">[Clique aqui para abrir]</a>`, 'success', 10000);
}

/**
 * Função unificada para gerar e abrir relatórios PDF com feedback visual,
 * compilação sob demanda via backend (quando disponível) e proteção anti-bloqueio de popup.
 */
async function dispararGeracaoRelatorio(endpoint, caminhoPdf, titulo, botaoId) {
    const btn = botaoId ? document.getElementById(botaoId) : null;
    const originalHtml = btn ? btn.innerHTML : '';

    if (btn) {
        btn.disabled = true;
        btn.classList.add('loading');
        btn.innerHTML = `
            <span class="spinner" style="display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 0.8s linear infinite;"></span>
            <span>Gerando PDF...</span>
        `;
    }

    showToast(`⚙️ Gerando <strong>${titulo}</strong>... Processando dados e diagramando documento.`, 'loading', 15000);

    const urlFallback = resolverUrlPdf(caminhoPdf);

    // Se estiver em modo local HTTP (porta 8080/servidor rodando), solicita compilação ao backend
    if (window.location.protocol !== 'file:' && endpoint) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000);

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ timestamp: Date.now(), force: true }),
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (res.ok) {
                const data = await res.json();
                const urlGerada = resolverUrlPdf(data.url || caminhoPdf);
                abrirPdfRobusto(urlGerada, titulo);
                return;
            }
        } catch (err) {
            console.warn(`Compilação via backend demorou ou falhou (${err.message}). Abrindo versão compilada.`);
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.classList.remove('loading');
                btn.innerHTML = originalHtml;
            }
        }
    } else {
        if (btn) {
            setTimeout(() => {
                btn.disabled = false;
                btn.classList.remove('loading');
                btn.innerHTML = originalHtml;
            }, 600);
        }
    }

    // Abertura com fallback imediato
    abrirPdfRobusto(urlFallback, titulo);
}

/**
 * Dispara a geração e abertura oficial do Relatório Acadêmico da Dissertação em PDF (97 Gráficos).
 */
function gerarRelatorioAcademicoPDF() {
    dispararGeracaoRelatorio('/api/gerar-relatorio', 'relatorios_pdf/relatorio_dissertacao_completo.pdf', 'Relatório Acadêmico da Dissertação (97 Gráficos)', 'btn-relatorio-academico');
}

/**
 * Alias retrocompatível para Relatório Acadêmico.
 */
function gerarRelatorioPDF() {
    gerarRelatorioAcademicoPDF();
}

/**
 * Dispara a geração e abertura do Relatório Gerencial Executivo em PDF (Frotas GFI).
 */
function gerarRelatorioGerencialPDF() {
    dispararGeracaoRelatorio('/api/gerar-relatorio-gerencial', 'relatorios_pdf/relatorio_gerencial_frotas_executivo.pdf', 'Relatório Gerencial Executivo de Frotas', 'btn-relatorio-gerencial');
}

/**
 * Dispara a geração e abertura do Relatório de Previsão de Gastos (2027-2029) em PDF.
 */
function gerarRelatorioPrevisaoPDF() {
    dispararGeracaoRelatorio('/api/gerar-relatorio-previsao', 'relatorios_pdf/relatorio_previsao_gastos_2027_2029.pdf', 'Relatório de Previsão Orçamentária 2027–2029', 'btn-relatorio-previsao');
}

/**
 * Dispara a abertura do Relatório de Teoria dos Grafos e Redes Complexas em PDF.
 */
function abrirRelatorioGrafosPDF() {
    dispararGeracaoRelatorio('/api/gerar-relatorio-grafos', 'relatorios_pdf/relatorio_teoria_dos_grafos_e_redes_complexas.pdf', 'Relatório de Teoria dos Grafos & Redes Complexas', 'btn-relatorio-grafos');
}

/**
 * Dispara a abertura do Relatório Técnico de Processamento, Manipulação e Cruzamento em PDF.
 */
function abrirRelatorioTecnicoPDF() {
    dispararGeracaoRelatorio('/api/gerar-relatorio-tecnico', 'relatorios_pdf/relatorio_tecnico_processamento_e_cruzamento_dados.pdf', 'Relatório Técnico de Processamento & Cruzamentos', 'btn-relatorio-tecnico');
}

/**
 * Dispara a abertura do Relatório Oficial das 40 Figuras e Tabelas Mais Importantes em PDF.
 */
function abrirRelatorio40PDF() {
    dispararGeracaoRelatorio('/api/gerar-relatorio-40', 'relatorios_pdf/relatorio_40.pdf', 'As 40 Figuras & Tabelas Mais Importantes da Pesquisa', 'btn-relatorio-40');
}

/**
 * Dispara a abertura do Apêndice Técnico de Arquitetura e Códigos em PDF.
 */
function abrirApendicePDF() {
    dispararGeracaoRelatorio('/api/gerar-apendice', 'relatorios_pdf/apendice.pdf', 'Apêndice Técnico: Arquitetura & Códigos do Projeto', 'btn-apendice');
}

/**
 * Baixa a cópia oficial da Dissertação Completa em Word (.docx ABNT).
 */
function baixarRelatorioWord() {
    showToast('📥 Baixando Dissertação Acadêmica em formato Word (.docx ABNT)...', 'info', 5000);
    const link = document.createElement('a');
    if (window.location.protocol !== 'file:') {
        link.href = '/api/baixar-word';
    } else {
        link.href = '../relatorios/dissertacao_mestrado_completa_ppgcap_udesc.docx';
    }
    link.download = 'dissertacao_mestrado_completa_ppgcap_udesc.docx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Baixa o Relatório Gerencial Executivo de Frotas em Word (.docx).
 */
function baixarRelatorioGerencialWord() {
    showToast('📥 Baixando Relatório Gerencial Executivo em formato Word (.docx)...', 'info', 5000);
    const link = document.createElement('a');
    if (window.location.protocol !== 'file:') {
        link.href = '/api/baixar-word-gerencial';
    } else {
        link.href = '../relatorios/relatorio_gerencial_frotas_executivo.docx';
    }
    link.download = 'relatorio_gerencial_frotas_executivo.docx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Baixa a Planilha Consolidada da Pesquisa em Excel (.xlsx - 8 Abas Formatadas).
 */
function baixarPlanilhaExcel() {
    showToast('📊 Baixando Planilha Consolidada em Excel (.xlsx com 8 abas)...', 'info', 5000);
    const link = document.createElement('a');
    if (window.location.protocol !== 'file:') {
        link.href = '/api/baixar-planilha';
    } else {
        link.href = '../relatorios/planilha_dados_resultados_dissertacao.xlsx';
    }
    link.download = 'planilha_dados_resultados_dissertacao.xlsx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Baixa planilhas setoriais em formato CSV (GFI, Leilão, Modelos ML).
 */
function baixarPlanilhaCSV(tipo) {
    const nomes = {
        'gfi': 'planilha_38_indicadores_gfi.csv',
        'leilao': 'planilha_veiculos_leilao_onerosos.csv',
        'modelos': 'planilha_modelos_ml_metricas.csv'
    };
    const fname = nomes[tipo] || 'planilha_dados.csv';
    showToast(`📁 Baixando Planilha CSV: ${fname}...`, 'info', 4000);
    const link = document.createElement('a');
    if (window.location.protocol !== 'file:') {
        link.href = `/api/baixar-csv?tipo=${tipo}`;
    } else {
        link.href = `../relatorios/${fname}`;
    }
    link.download = fname;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Controla abertura e fechamento do Dropdown de Downloads de Relatórios.
 */
function toggleDropdownDownloads(event) {
    if (event) event.stopPropagation();
    const menu = document.getElementById('dropdown-downloads-menu');
    if (!menu) return;
    const isVisible = menu.classList.contains('show');
    document.querySelectorAll('.dropdown-menu.show').forEach(m => m.classList.remove('show'));
    if (!isVisible) {
        menu.classList.add('show');
    }
}

// Fechar dropdowns ao clicar fora
document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown-container')) {
        document.querySelectorAll('.dropdown-menu.show').forEach(m => m.classList.remove('show'));
    }
});

/**
 * Filtro em tempo real para a Tabela de Bens para Leilão.
 */
function filtrarTabelaLeilao() {
    const input = document.getElementById('search-leilao');
    if (!input) return;
    const filter = input.value.toUpperCase();
    const tableBody = document.getElementById('tabela-leilao-body');
    if (!tableBody) return;
    const rows = tableBody.getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const text = rows[i].textContent || rows[i].innerText;
        if (text.toUpperCase().indexOf(filter) > -1) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

/**
 * Simulador Interativo de Orçamento Trienal (2027, 2028 e 2029).
 */
function atualizarSimulacaoOrcamento() {
    const sliderPecas = document.getElementById('sim-pecas');
    const sliderMO = document.getElementById('sim-mo');
    const sliderIdade = document.getElementById('sim-idade');

    if (!sliderPecas || !sliderMO || !sliderIdade) return;

    const pecasVal = parseFloat(sliderPecas.value);
    const moVal = parseFloat(sliderMO.value);
    const idadeVal = parseFloat(sliderIdade.value);

    // Atualiza os labels dos sliders
    const lblPecas = document.getElementById('lbl-sim-pecas');
    const lblMO = document.getElementById('lbl-sim-mo');
    const lblIdade = document.getElementById('lbl-sim-idade');

    if (lblPecas) lblPecas.textContent = pecasVal.toFixed(1) + '% a.a.';
    if (lblMO) lblMO.textContent = moVal.toFixed(1) + '% a.a.';
    if (lblIdade) lblIdade.textContent = idadeVal.toFixed(1) + '% a.a.';

    // Ponderação empírica: 69,18% peças e 30,82% mão de obra
    const inflacaoPonderada = (0.6918 * (pecasVal / 100)) + (0.3082 * (moVal / 100));

    // Base histórica 2025
    const base2025 = 34464759.78;

    // Fatores de progressão por idade (desgaste acelerado Weibull)
    const taxa2026 = ((1.0 + inflacaoPonderada) * (1.0 + (idadeVal / 100))) - 1.0;
    const taxa2027 = ((1.0 + inflacaoPonderada) * (1.0 + (idadeVal / 100) * 1.08)) - 1.0;
    const taxa2028 = ((1.0 + inflacaoPonderada) * (1.0 + (idadeVal / 100) * 1.20)) - 1.0;
    const taxa2029 = ((1.0 + inflacaoPonderada) * (1.0 + (idadeVal / 100) * 1.36)) - 1.0;

    const v2026 = base2025 * (1.0 + taxa2026);
    const v2027 = v2026 * (1.0 + taxa2027);
    const v2028 = v2027 * (1.0 + taxa2028);
    const v2029 = v2028 * (1.0 + taxa2029);

    // Prescritivo otimizado
    const p2027 = 30016766.69;
    const p2028 = 31029832.57;
    const p2029 = 32077086.91;

    const saving2027 = v2027 - p2027;
    const saving2028 = v2028 - p2028;
    const saving2029 = v2029 - p2029;
    const totalSaving = saving2027 + saving2028 + saving2029;

    function fmtM(val) {
        return 'R$ ' + (val / 1e6).toFixed(2).replace('.', ',') + 'M';
    }

    const el2027 = document.getElementById('val-sim-2027');
    const el2028 = document.getElementById('val-sim-2028');
    const el2029 = document.getElementById('val-sim-2029');
    const elSaving = document.getElementById('val-sim-saving');

    if (el2027) el2027.textContent = fmtM(v2027);
    if (el2028) el2028.textContent = fmtM(v2028);
    if (el2029) el2029.textContent = fmtM(v2029);
    if (elSaving) elSaving.textContent = fmtM(totalSaving);
}

/**
 * Força a renovação do cache de todas as imagens da página instantaneamente.
 */
function recarregarTodasImagens() {
    const images = document.querySelectorAll('img');
    const timestamp = Date.now();
    let count = 0;

    images.forEach(img => {
        if (img.src) {
            const url = new URL(img.src, window.location.href);
            url.searchParams.set('t', timestamp);
            img.src = url.toString();
            count++;
        }
    });

    showToast(`🔄 Cache renovado: ${count} figuras científicas atualizadas!`, 'info', 3000);
}

// ==============================================================================
// 6. COPILOTO DE IA EM LINGUAGEM NATURAL E APRENDIZADO
// ==============================================================================

/**
 * Abre/fecha o painel lateral do chat com o Copiloto de IA.
 */
function toggleAIChat() {
    const drawer = document.getElementById('ai-chat-drawer');
    const floatingBtn = document.getElementById('floating-chat-btn');
    if (!drawer) return;

    const isOpen = drawer.classList.contains('open');

    if (isOpen) {
        drawer.classList.remove('open');
        if (floatingBtn) floatingBtn.style.display = 'flex';
    } else {
        drawer.classList.add('open');
        if (floatingBtn) floatingBtn.style.display = 'none';
        const input = document.getElementById('chat-input');
        if (input) setTimeout(() => input.focus(), 250);
    }
}

/**
 * Inicializa a mensagem de boas-vindas no chat se estiver vazio.
 */
function initChatWelcome() {
    const container = document.getElementById('chat-messages-container');
    if (!container || container.children.length > 0) return;

    const welcomeHtml = `
        <div class="chat-message chat-msg-ai">
            <div class="msg-avatar">🤖</div>
            <div class="msg-content">
                <strong>Copiloto de IA da Frota (PPGCAP/UDESC)</strong>
                <p>Olá! Sou o assistente inteligente especializado nos <strong>dados e métricas do sistema da dissertação</strong>.</p>
                <p>Estou estritamente instruído a responder com base nas evidências auditadas (350 mil OS, R$ 138M, Lilliefors, Poisson, Markov, ARIMA e MILP).</p>
                <div class="msg-prompt-hint">
                    💡 <em>Clique em uma das sugestões abaixo ou digite sua dúvida no prompt:</em>
                </div>
            </div>
        </div>
    `;
    container.innerHTML = welcomeHtml;
}

/**
 * Envia uma pergunta pré-configurada ao clicar em uma chip.
 */
function enviarPerguntaChip(perguntaTexto) {
    const input = document.getElementById('chat-input');
    if (input) {
        input.value = perguntaTexto;
    }
    const form = document.getElementById('chat-form');
    if (form) {
        form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
}

/**
 * Limpa o histórico de mensagens do chat.
 */
function limparHistoricoChat() {
    const container = document.getElementById('chat-messages-container');
    if (container) {
        container.innerHTML = '';
        initChatWelcome();
        showToast('Histórico do chat foi limpo.', 'info', 2500);
    }
}

/**
 * Processa o envio do formulário de chat em linguagem natural.
 */
async function enviarMensagemChat(e) {
    if (e && e.preventDefault) e.preventDefault();

    const input = document.getElementById('chat-input');
    if (!input) return;

    const text = input.value.trim();
    if (!text) return;

    // 1. Renderiza mensagem do usuário
    appendChatMessage('Pesquisador', text, false);
    input.value = '';

    // 2. Renderiza indicador de digitação
    const container = document.getElementById('chat-messages-container');
    const typingId = 'typing-' + Date.now();
    if (container) {
        const typingEl = document.createElement('div');
        typingEl.id = typingId;
        typingEl.className = 'chat-message chat-msg-ai typing-msg';
        typingEl.innerHTML = `
            <div class="msg-avatar">🤖</div>
            <div class="msg-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        container.appendChild(typingEl);
        container.scrollTop = container.scrollHeight;
    }

    // 3. Chamada à API REST
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensagem: text })
        });

        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const respText = data.resposta || "Sem resposta recebida.";
        appendChatMessage('Copiloto de IA', respText, true, data);

        // Se uma ação do pipeline foi disparada pela IA, recarrega figuras
        if (data.acao_executada === 'update_charts') {
            recarregarTodasImagens();
            showToast('Gráficos atualizados pelo comando da IA!', 'success', 4000);
        } else if (data.acao_executada === 'generate_pdf') {
            showToast('PDF acadêmico gerado com sucesso!', 'success', 4000);
        }

    } catch (err) {
        console.error('Erro ao enviar mensagem:', err);
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        appendChatMessage('Sistema', `⚠️ Falha ao contatar o servidor local da API (${err.message}). Certifique-se de executar 'python3 run_dashboard.py'.`, true);
    }
}

/**
 * Insere uma bolha de mensagem no contêiner do chat.
 */
function appendChatMessage(author, content, isAi, metaData = null) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${isAi ? 'chat-msg-ai' : 'chat-msg-user'}`;

    const formattedContent = formatChatMarkdown(content);

    let actionButtonHtml = '';
    if (metaData && metaData.url && metaData.acao_executada === 'generate_pdf') {
        actionButtonHtml = `
            <div style="margin-top: 10px;">
                <a href="${metaData.url}" target="_blank" class="btn btn-primary btn-sm" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; text-decoration: none;">
                    📄 Abrir PDF Oficial (UDESC)
                </a>
            </div>
        `;
    }

    msgDiv.innerHTML = `
        <div class="msg-avatar">${isAi ? '🤖' : '👤'}</div>
        <div class="msg-content">
            <strong>${author}</strong>
            <div class="msg-text">${formattedContent}</div>
            ${actionButtonHtml}
        </div>
    `;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

/**
 * Formatador leve de Markdown para exibição rica de mensagens da IA.
 */
function formatChatMarkdown(text) {
    if (!text) return '';

    let escaped = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Negrito (**texto**)
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Itálico (*texto*)
    escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Código em linha (`codigo`)
    escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Links em markdown [texto](url)
    escaped = escaped.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: #38bdf8; text-decoration: underline;">$1</a>');

    // Bullets (• item)
    escaped = escaped.replace(/•\s+(.+)/g, '<div class="bullet-item">• $1</div>');

    // Quebras de linha
    escaped = escaped.replace(/\n\n/g, '<div style="margin-top: 8px;"></div>');
    escaped = escaped.replace(/\n/g, '<br>');

    return escaped;
}

// ==============================================================================
// 14. MÓDULO INTERATIVO DE TEORIA DOS GRAFOS & REDES COMPLEXAS
// ==============================================================================
let grafoState = {
    modo: 'bipartido',
    animId: null,
    nodes: [],
    edges: [],
    hoveredNode: null,
    width: 1100,
    height: 380
};

/**
 * Inicializa ou reinicia o Canvas do Grafo Interativo.
 */
function initGrafoCanvas() {
    const canvas = document.getElementById('canvas-grafo');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const container = canvas.parentElement;
    const rect = container.getBoundingClientRect();
    
    // Configura resolução real do canvas
    canvas.width = Math.max(rect.width, 800);
    canvas.height = 380;
    grafoState.width = canvas.width;
    grafoState.height = canvas.height;

    gerarDadosGrafo(grafoState.modo);
    setupGrafoEventos(canvas);
    startGrafoLoop(canvas, ctx);
}

/**
 * Gera os dados de nós e arestas conforme o modo selecionado.
 */
function gerarDadosGrafo(modo) {
    grafoState.nodes = [];
    grafoState.edges = [];
    const w = grafoState.width;
    const h = grafoState.height;

    if (modo === 'bipartido') {
        // Modo Bipartido: Oficinas à esquerda, Veículos à direita
        const oficinas = [
            { id: 'O1024', label: 'Oficina #1024', tipo: 'oficina', val: 'R$ 3,84M', cb: '0,284', deg: 48, r: 18, x: w * 0.2, y: h * 0.25 },
            { id: 'O1088', label: 'Oficina #1088', tipo: 'oficina', val: 'R$ 2,41M', cb: '0,195', deg: 36, r: 16, x: w * 0.2, y: h * 0.45 },
            { id: 'O2015', label: 'Oficina #2015', tipo: 'oficina', val: 'R$ 1,95M', cb: '0,142', deg: 29, r: 14, x: w * 0.2, y: h * 0.65 },
            { id: 'O3142', label: 'Oficina #3142', tipo: 'oficina', val: 'R$ 1,24M', cb: '0,098', deg: 24, r: 12, x: w * 0.2, y: h * 0.82 }
        ];

        const veiculos = [];
        const placas = ['MEN7009', 'MLG0296', 'RYW5D02', 'QID5668', 'MJK2938', 'RAB9182', 'MFK3921', 'PXT8821', 'NBE4920', 'SCB1029'];
        for (let i = 0; i < placas.length; i++) {
            veiculos.push({
                id: 'V_' + placas[i],
                label: placas[i],
                tipo: 'veiculo',
                val: 'R$ ' + (15 + (i * 7)) + 'k',
                cb: (0.01 + i * 0.005).toFixed(3),
                deg: 1 + (i % 3),
                r: 9,
                x: w * 0.78,
                y: h * (0.12 + (i * 0.082))
            });
        }

        grafoState.nodes = [...oficinas, ...veiculos];

        // Arestas ponderadas
        oficinas.forEach((ofic, oIdx) => {
            veiculos.forEach((veic, vIdx) => {
                if ((oIdx + vIdx) % 2 === 0 || (vIdx < 4 && oIdx === 0)) {
                    grafoState.edges.push({
                        from: ofic,
                        to: veic,
                        weight: 1 + ((oIdx + vIdx) % 4),
                        color: oIdx === 0 ? 'rgba(56, 189, 248, 0.45)' : 'rgba(148, 163, 184, 0.25)'
                    });
                }
            });
        });

    } else if (modo === 'coocorrencia') {
        // Modo Co-ocorrência de Falhas (Clusters de Louvain)
        const sistemas = [
            { id: 'S1', label: 'Freios & Pastilhas', tipo: 'sistema', cluster: 1, r: 16, val: '2.850 OSs', deg: 7, x: w * 0.35, y: h * 0.3 },
            { id: 'S2', label: 'Suspensão & Amortecedor', tipo: 'sistema', cluster: 1, r: 17, val: '3.400 OSs', deg: 8, x: w * 0.5, y: h * 0.28 },
            { id: 'S3', label: 'Pneus & Alinhamento', tipo: 'sistema', cluster: 1, r: 18, val: '4.100 OSs', deg: 9, x: w * 0.42, y: h * 0.15 },
            { id: 'S4', label: 'Motor & Cabeçote', tipo: 'sistema', cluster: 2, r: 15, val: '1.850 OSs', deg: 6, x: w * 0.25, y: h * 0.65 },
            { id: 'S5', label: 'Arrefecimento / Radiador', tipo: 'sistema', cluster: 2, r: 13, val: '1.200 OSs', deg: 5, x: w * 0.4, y: h * 0.72 },
            { id: 'S6', label: 'Injeção Eletrônica', tipo: 'sistema', cluster: 2, r: 14, val: '1.640 OSs', deg: 6, x: w * 0.28, y: h * 0.82 },
            { id: 'S7', label: 'Câmbio & Embreagem', tipo: 'sistema', cluster: 3, r: 15, val: '2.100 OSs', deg: 5, x: w * 0.72, y: h * 0.4 },
            { id: 'S8', label: 'Sistema Elétrico & Bateria', tipo: 'sistema', cluster: 4, r: 14, val: '1.920 OSs', deg: 5, x: w * 0.75, y: h * 0.68 }
        ];

        grafoState.nodes = sistemas;

        const conexoes = [
            ['S1', 'S2', 4, '#10b981'], ['S2', 'S3', 5, '#10b981'], ['S1', 'S3', 3, '#10b981'],
            ['S4', 'S5', 4, '#0ea5e9'], ['S4', 'S6', 3.5, '#0ea5e9'], ['S5', 'S6', 2.5, '#0ea5e9'],
            ['S1', 'S4', 1.5, '#64748b'], ['S7', 'S4', 2.5, '#f59e0b'], ['S8', 'S6', 2.5, '#8b5cf6']
        ];

        conexoes.forEach(([id1, id2, peso, cor]) => {
            const n1 = sistemas.find(s => s.id === id1);
            const n2 = sistemas.find(s => s.id === id2);
            if (n1 && n2) {
                grafoState.edges.push({ from: n1, to: n2, weight: peso, color: cor + '88' });
            }
        });

    } else if (modo === 'anomalias') {
        // Modo Sub-rede de Anomalias Críticas e Conluio
        const hubsAnom = [
            { id: 'ANOM_1', label: 'Oficina Suspeita #1024', tipo: 'anomalia', val: 'R$ 840k Atípico', deg: 12, cb: '0,312', r: 19, x: w * 0.35, y: h * 0.5 },
            { id: 'ANOM_2', label: 'Oficina Suspeita #1088', tipo: 'anomalia', val: 'R$ 510k Atípico', deg: 8, cb: '0,215', r: 16, x: w * 0.65, y: h * 0.45 }
        ];

        const veicAnom = [];
        for (let i = 1; i <= 8; i++) {
            veicAnom.push({
                id: 'VA_' + i,
                label: 'Vtr Anômala #' + (7000 + i),
                tipo: 'veic_anom',
                val: 'OS Atípica (Score < -0.15)',
                deg: 2,
                r: 8,
                x: (i % 2 === 0 ? w * 0.2 + (i * 15) : w * 0.78 - (i * 12)),
                y: h * (0.15 + (i * 0.09))
            });
        }

        grafoState.nodes = [...hubsAnom, ...veicAnom];

        veicAnom.forEach((va, idx) => {
            const targetHub = idx < 5 ? hubsAnom[0] : hubsAnom[1];
            grafoState.edges.push({
                from: targetHub,
                to: va,
                weight: 3,
                color: 'rgba(239, 68, 68, 0.6)'
            });
        });
    }

    // Inicializa velocidades para micro-animação
    grafoState.nodes.forEach(n => {
        n.vx = (Math.random() - 0.5) * 0.3;
        n.vy = (Math.random() - 0.5) * 0.3;
        n.baseX = n.x;
        n.baseY = n.y;
    });
}

/**
 * Loop de renderização em 60 FPS com micro-física suave.
 */
function startGrafoLoop(canvas, ctx) {
    if (grafoState.animId) {
        cancelAnimationFrame(grafoState.animId);
    }

    function frame() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 1. Atualiza micro-física dos nós
        grafoState.nodes.forEach(n => {
            n.x += n.vx;
            n.y += n.vy;

            // Retorno elástico suave à posição base
            const dx = n.baseX - n.x;
            const dy = n.baseY - n.y;
            n.vx += dx * 0.02;
            n.vy += dy * 0.02;

            n.vx *= 0.92;
            n.vy *= 0.92;
        });

        // 2. Desenha arestas
        grafoState.edges.forEach(e => {
            ctx.beginPath();
            ctx.moveTo(e.from.x, e.from.y);
            ctx.lineTo(e.to.x, e.to.y);
            ctx.lineWidth = e.weight || 1;
            ctx.strokeStyle = e.color || 'rgba(148, 163, 184, 0.2)';
            ctx.stroke();
        });

        // 3. Desenha nós
        grafoState.nodes.forEach(n => {
            const isHover = (grafoState.hoveredNode === n);
            const radius = isHover ? n.r + 4 : n.r;

            ctx.beginPath();
            ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);

            if (n.tipo === 'oficina') {
                ctx.fillStyle = isHover ? '#38bdf8' : '#0284c7';
                ctx.strokeStyle = '#ffffff';
            } else if (n.tipo === 'anomalia') {
                ctx.fillStyle = isHover ? '#f87171' : '#dc2626';
                ctx.strokeStyle = '#fef2f2';
            } else if (n.tipo === 'veic_anom') {
                ctx.fillStyle = '#ea580c';
                ctx.strokeStyle = '#fff';
            } else if (n.tipo === 'sistema') {
                ctx.fillStyle = n.cluster === 1 ? '#10b981' : (n.cluster === 2 ? '#0284c7' : '#f59e0b');
                ctx.strokeStyle = '#fff';
            } else {
                ctx.fillStyle = isHover ? '#60a5fa' : '#3b82f6';
                ctx.strokeStyle = '#e2e8f0';
            }

            ctx.lineWidth = isHover ? 2.5 : 1.5;
            ctx.fill();
            ctx.stroke();

            // Rótulo de texto para nós maiores
            if (n.r >= 12 || isHover) {
                ctx.font = isHover ? 'bold 11px sans-serif' : '10px sans-serif';
                ctx.fillStyle = '#ffffff';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(n.label, n.x, n.y + n.r + 12);
            }
        });

        grafoState.animId = requestAnimationFrame(frame);
    }

    grafoState.animId = requestAnimationFrame(frame);
}

/**
 * Eventos de Mouse e Hover no Canvas.
 */
function setupGrafoEventos(canvas) {
    const tooltip = document.getElementById('grafo-tooltip');

    canvas.onmousemove = function(e) {
        const rect = canvas.getBoundingClientRect();
        const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
        const my = (e.clientY - rect.top) * (canvas.height / rect.height);

        let found = null;
        for (let i = grafoState.nodes.length - 1; i >= 0; i--) {
            const n = grafoState.nodes[i];
            const dist = Math.hypot(n.x - mx, n.y - my);
            if (dist <= n.r + 5) {
                found = n;
                break;
            }
        }

        grafoState.hoveredNode = found;

        if (found && tooltip) {
            tooltip.style.display = 'block';
            tooltip.style.left = (e.clientX - rect.left + 14) + 'px';
            tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
            tooltip.innerHTML = `
                <div style="font-weight: 800; color: #38bdf8; margin-bottom: 3px;">${found.label}</div>
                <div>Tipo: <strong>${found.tipo.toUpperCase()}</strong></div>
                <div>Grau (k): <strong>${found.deg} conexões</strong></div>
                ${found.cb ? `<div>Betweenness: <strong>${found.cb}</strong></div>` : ''}
                <div>Métrica / Valor: <span style="color: #4ade80; font-weight: bold;">${found.val}</span></div>
            `;
            canvas.style.cursor = 'pointer';
        } else if (tooltip) {
            tooltip.style.display = 'none';
            canvas.style.cursor = 'default';
        }
    };

    canvas.onmouseleave = function() {
        grafoState.hoveredNode = null;
        const tooltip = document.getElementById('grafo-tooltip');
        if (tooltip) tooltip.style.display = 'none';
    };
}

/**
 * Alterna entre os modos de visualização de grafos.
 */
function alternarModoGrafo(modo) {
    grafoState.modo = modo;
    ['btn-grafo-bipartido', 'btn-grafo-cooc', 'btn-grafo-anom'].forEach(id => {
        const b = document.getElementById(id);
        if (b) {
            b.classList.remove('btn-primary');
            b.classList.add('btn-secondary');
        }
    });

    const activeBtn = document.getElementById(
        modo === 'bipartido' ? 'btn-grafo-bipartido' : (modo === 'coocorrencia' ? 'btn-grafo-cooc' : 'btn-grafo-anom')
    );
    if (activeBtn) {
        activeBtn.classList.remove('btn-secondary');
        activeBtn.classList.add('btn-primary');
    }

    gerarDadosGrafo(modo);
}

/**
 * Reinicia a física do grafo espalhando os nós.
 */
function reiniciarAnimacaoGrafo() {
    grafoState.nodes.forEach(n => {
        n.vx = (Math.random() - 0.5) * 8;
        n.vy = (Math.random() - 0.5) * 8;
    });
}

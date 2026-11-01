/**
 * Controlador Principal da Aplicação SPA - FROTAGOV
 * Sistema Integrado de Gestão Pública de Frotas & Telemetria IoT (Governo de SC)
 */

document.addEventListener('DOMContentLoaded', async () => {
  console.log('Inicializando FROTAGOV Web Application...');

  setupNavigation();
  setupModals();
  setupSecretariaFilter();
  setupSimulateButton();

  // Verificar se o usuário já possui sessão autenticada
  const estaAutenticado = verificarSessaoFROTAGOV();
  if (estaAutenticado) {
    await loadDashboard();
  } else {
    // Exibir tela de login com foco e preenchimento sugerido
    const authScreen = document.getElementById('auth-screen');
    if (authScreen) authScreen.style.display = 'flex';
  }

  // Polling em background para telemetria (a cada 10s apenas se logado)
  setInterval(async () => {
    if (!api.token) return;
    const activeTab = document.querySelector('.nav-item.active')?.dataset.tab;
    if (activeTab === 'rastreamento') {
      updateVehicleMarkersOnMap();
    }
  }, 10000);
});

// =====================================================================
// AUTENTICAÇÃO E SESSÃO FROTAGOV (CPF & SENHA FORTE)
// =====================================================================

function verificarSessaoFROTAGOV() {
  const authScreen = document.getElementById('auth-screen');
  if (api.token && api.currentUser) {
    if (authScreen) authScreen.style.display = 'none';
    atualizarPerfilUsuarioLogado(api.currentUser);
    return true;
  } else {
    if (authScreen) authScreen.style.display = 'flex';
    return false;
  }
}

function atualizarPerfilUsuarioLogado(user) {
  if (!user) return;
  const nameEl = document.getElementById('sidebar-user-name');
  const cpfEl = document.getElementById('sidebar-user-cpf');
  const avatarEl = document.getElementById('sidebar-user-avatar');

  if (nameEl) nameEl.textContent = user.nome_completo || user.username;
  if (cpfEl) {
    const cpfDisplay = user.cpf || '000.000.000-00';
    const roleDisplay = user.role || 'ADMIN';
    cpfEl.textContent = `CPF: ${cpfDisplay} • ${roleDisplay}`;
  }
  if (avatarEl) {
    const iniciais = (user.nome_completo || user.username || 'AG')
      .split(' ')
      .map(p => p[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
    avatarEl.textContent = iniciais || 'SC';
  }
}

function alternarVisibilidadeSenha() {
  const input = document.getElementById('login-senha-usuario');
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
}

function preencherDemoLogin(usuario, senha) {
  const usrInput = document.getElementById('login-cpf-usuario');
  const passInput = document.getElementById('login-senha-usuario');
  if (usrInput) usrInput.value = usuario;
  if (passInput) {
    passInput.value = senha;
    verificarForcaSenhaFrontend(senha);
  }
}

function verificarForcaSenhaFrontend(senha) {
  const critLength = document.getElementById('crit-length');
  const critNotNumeric = document.getElementById('crit-not-numeric');
  const critUpperLower = document.getElementById('crit-upper-lower');
  const critNumberSpecial = document.getElementById('crit-number-special');

  const s = senha || '';

  // 1. Mínimo 8 caracteres
  const okLength = s.length >= 8;
  if (critLength) {
    critLength.className = `criteria-item ${okLength ? 'valid' : 'invalid'}`;
  }

  // 2. Não apenas numérica
  const isOnlyDigits = /^\d+$/.test(s) && s.length > 0;
  const okNotNumeric = s.length > 0 && !isOnlyDigits;
  if (critNotNumeric) {
    critNotNumeric.className = `criteria-item ${okNotNumeric ? 'valid' : 'invalid'}`;
  }

  // 3. Letras maiúscula e minúscula
  const hasUpper = /[A-Z]/.test(s);
  const hasLower = /[a-z]/.test(s);
  const okUpperLower = hasUpper && hasLower;
  if (critUpperLower) {
    critUpperLower.className = `criteria-item ${okUpperLower ? 'valid' : 'invalid'}`;
  }

  // 4. Número e caractere especial
  const hasNumber = /[0-9]/.test(s);
  const hasSpecial = /[^A-Za-z0-9]/.test(s);
  const okNumberSpecial = hasNumber && hasSpecial;
  if (critNumberSpecial) {
    critNumberSpecial.className = `criteria-item ${okNumberSpecial ? 'valid' : 'invalid'}`;
  }

  return okLength && okNotNumeric && okUpperLower && okNumberSpecial;
}

async function executarLoginFROTAGOV() {
  const usrInput = document.getElementById('login-cpf-usuario');
  const passInput = document.getElementById('login-senha-usuario');
  const btnSubmit = document.getElementById('btn-submit-login');

  const identificador = (usrInput?.value || '').trim();
  const senha = passInput?.value || '';

  if (!identificador || !senha) {
    showToast('Informe seu CPF/usuário e senha de acesso.', 'warning');
    return;
  }

  // Validação client-side das regras de complexidade da senha
  const senhaForte = verificarForcaSenhaFrontend(senha);
  if (!senhaForte) {
    showToast('A senha não cumpre os requisitos: mínimo 8 chars, maiúscula, minúscula, números e caractere especial (não pode ser puramente numérica).', 'error');
    return;
  }

  if (btnSubmit) {
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span>Autenticando...</span>';
  }

  try {
    const res = await api.login(identificador, senha);
    showToast(`Bem-vindo ao FROTAGOV, ${res.user.nome_completo || res.user.username}!`, 'success');

    const authScreen = document.getElementById('auth-screen');
    if (authScreen) {
      authScreen.style.opacity = '0';
      setTimeout(() => {
        authScreen.style.display = 'none';
        authScreen.style.opacity = '1';
      }, 300);
    }

    atualizarPerfilUsuarioLogado(res.user);
    await loadDashboard();

  } catch (err) {
    showToast(err.message || 'Falha na autenticação: credenciais incorretas.', 'error');
  } finally {
    if (btnSubmit) {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = '<span>Acessar Módulos do FROTAGOV</span> <span>➔</span>';
    }
  }
}

function executarLogoutFROTAGOV() {
  api.clearSession();
  const authScreen = document.getElementById('auth-screen');
  if (authScreen) {
    authScreen.style.display = 'flex';
    authScreen.style.opacity = '1';
  }
  const passInput = document.getElementById('login-senha-usuario');
  if (passInput) {
    passInput.value = '';
    verificarForcaSenhaFrontend('');
  }
  showToast('Sessão encerrada com sucesso no FROTAGOV.', 'info');
}


// =====================================================================
// NAVEGAÇÃO ENTRE MÓDULOS
// =====================================================================
function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item, .mobile-nav-btn');

  navItems.forEach(item => {
    item.addEventListener('click', async (e) => {
      e.preventDefault();
      const tabName = item.dataset.tab;
      if (!tabName) return;

      // Atualizar classes ativas
      document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
      document.querySelectorAll('.mobile-nav-btn').forEach(n => n.classList.remove('active'));

      const activeSidebar = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
      if (activeSidebar) activeSidebar.classList.add('active');

      const activeMobile = document.querySelector(`.mobile-nav-btn[data-tab="${tabName}"]`);
      if (activeMobile) activeMobile.classList.add('active');

      // Alternar painéis de conteúdo
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      const targetPane = document.getElementById(`pane-${tabName}`);
      if (targetPane) {
        targetPane.classList.add('active');
      }

      // Atualizar título da barra superior
      const titles = {
        'dashboard': 'Painel Executivo & Indicadores',
        'rastreamento': 'Rastreamento & Telemetria em Tempo Real',
        'abastecimento': 'Gestão de Abastecimento & Postos Credenciados',
        'manutencao': 'Manutenção Preventiva, Corretiva & Pneus',
        'viagens': 'Viagens, Despacho & Checklist Digital',
        'compliance': 'Compliance, Multas & Prazos Legais',
        'relatorios': 'Inteligência Analítica, TCO & Auditoria',
        'seguranca': 'Segurança, Perfis RBAC & Chaves de API IoT',
        'cadastro-veiculos': '📝 Central de Cadastro de Veículos & Ativos (Manual & IoT)',
        'ai-copilot': '🤖 Copilot de Inteligência Artificial & Diagnóstico Prescritivo',
        'iso25010-sc': '🏛️ Matriz de Qualidade ISO/IEC 25010 & Contrato Governo SC'
      };
      const titleElem = document.getElementById('current-page-title');
      if (titleElem && titles[tabName]) {
        titleElem.textContent = titles[tabName];
      }

      // Inicializar módulo específico
      if (tabName === 'dashboard') await loadDashboard();
      if (tabName === 'rastreamento') {
        setTimeout(() => initFleetMap(), 150);
        await loadTelemetryEvents();
      }
      if (tabName === 'cadastro-veiculos') await carregarModuloCadastro();
      if (tabName === 'abastecimento') await loadFuelModule();
      if (tabName === 'manutencao') await loadMaintenanceModule();
      if (tabName === 'viagens') await loadTripsModule();
      if (tabName === 'compliance') await loadComplianceModule();
      if (tabName === 'relatorios') await loadReportsModule();
      if (tabName === 'seguranca') await loadSecurityModule();
      if (tabName === 'ai-copilot') await loadAICopilotModule();
      if (tabName === 'iso25010-sc') await loadISO25010Module();
    });
  });
}

// =====================================================================
// FILTRO MULTI-SECRETARIA
// =====================================================================
function setupSecretariaFilter() {
  const select = document.getElementById('select-secretaria');
  if (!select) return;

  select.addEventListener('change', async () => {
    const sec = select.value;
    showToast(`Filtrando dados para: ${sec ? select.options[select.selectedIndex].text : 'Todas as Secretarias'}`);
    
    const activeTab = document.querySelector('.nav-item.active')?.dataset.tab || 'dashboard';
    if (activeTab === 'dashboard') await loadDashboard();
    if (activeTab === 'abastecimento') await loadFuelModule();
    if (activeTab === 'manutencao') await loadMaintenanceModule();
    if (activeTab === 'relatorios') await loadReportsModule();
  });
}

// =====================================================================
// DASHBOARD & KPIS
// =====================================================================
async function loadDashboard() {
  try {
    const kpis = await api.getDashboardKPIs();
    
    document.getElementById('kpi-total-veiculos').textContent = kpis.total_veiculos || '0';
    document.getElementById('kpi-em-viagem').textContent = kpis.veiculos_em_viagem || '0';
    document.getElementById('kpi-disponiveis').textContent = kpis.veiculos_disponiveis || '0';
    document.getElementById('kpi-manutencao').textContent = kpis.veiculos_manutencao || '0';
    document.getElementById('kpi-alertas-hoje').textContent = kpis.alertas_hoje || '0';
    document.getElementById('kpi-custo-mes').textContent = `R$ ${kpis.custo_total_mes.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    document.getElementById('kpi-consumo-medio').textContent = `${kpis.consumo_medio_frota_kml} km/L`;
    document.getElementById('kpi-score-medio').textContent = `${kpis.score_medio_conducao} pts`;

    // Carregar alertas críticos pendentes
    const alertasPrev = await api.getPreventiveAlerts();
    const expira = await api.getExpirations();

    const alertContainer = document.getElementById('dashboard-alerts-list');
    if (alertContainer) {
      alertContainer.innerHTML = '';

      if (alertasPrev.length === 0 && expira.total_alertas === 0) {
        alertContainer.innerHTML = '<div style="color: #64748b; font-size: 13px;">Nenhum alerta crítico pendente no momento. Frota 100% em conformidade.</div>';
      }

      alertasPrev.forEach(a => {
        alertContainer.innerHTML += `
          <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
            <div style="display:flex; justify-content:space-between;">
              <strong style="color: #fbbf24; font-size: 13px;">🔧 Revisão Preventiva por KM: ${a.veiculo_placa} (${a.modelo})</strong>
              <span class="status-pill warning">Faltam ${a.km_para_revisao.toFixed(0)} km</span>
            </div>
            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">${a.plano_revisao} - Odômetro atual: ${a.odometro_atual.toLocaleString('pt-BR')} km</div>
          </div>
        `;
      });

      expira.documentos_veiculos_pendentes?.forEach(d => {
        alertContainer.innerHTML += `
          <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
            <div style="display:flex; justify-content:space-between;">
              <strong style="color: #f87171; font-size: 13px;">⚠️ Vencimento Documento: ${d.veiculo_placa} (${d.tipo})</strong>
              <span class="status-pill danger">${d.dias_restantes < 0 ? 'VENCIDO' : `Vence em ${d.dias_restantes} dias`}</span>
            </div>
            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">Data Limite: ${d.vencimento} | Valor: R$ ${d.valor.toFixed(2)}</div>
          </div>
        `;
      });
    }

    // Carregar tabela de veículos
    await loadVehiclesTable();
  } catch (err) {
    console.error('Erro ao carregar Dashboard:', err);
  }
}

async function loadVehiclesTable() {
  const tbody = document.getElementById('vehicles-table-body');
  if (!tbody) return;

  const sec = document.getElementById('select-secretaria')?.value;
  const veiculos = await api.getVehicles();

  tbody.innerHTML = '';
  veiculos.forEach(v => {
    if (sec && (v.secretaria !== sec && v.centro_custo !== sec)) return;

    let badgeClass = 'success';
    if (v.status === 'EM_VIAGEM') badgeClass = 'info';
    if (v.status === 'MANUTENCAO') badgeClass = 'warning';
    if (v.status === 'INATIVO') badgeClass = 'danger';

    tbody.innerHTML += `
      <tr>
        <td><b>${v.placa}</b></td>
        <td>${v.marca} ${v.modelo} (${v.ano_modelo})</td>
        <td><span class="status-pill info">${v.categoria}</span></td>
        <td>${v.secretaria || v.centro_custo || 'Administração'}</td>
        <td>${v.odometro_atual_km.toLocaleString('pt-BR')} km</td>
        <td>${v.capacidade_tanque_litros} L (${v.tipo_combustivel})</td>
        <td><span class="status-pill ${badgeClass}">${v.status}</span></td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="openHistoryModal('${v.placa}')">Histórico</button>
        </td>
      </tr>
    `;
  });
}

// =====================================================================
// TELEMETRIA & EVENTOS EM TEMPO REAL
// =====================================================================
async function loadTelemetryEvents() {
  const container = document.getElementById('telemetry-events-list');
  if (!container) return;

  try {
    const eventos = await api.getTelemetryEvents();
    container.innerHTML = '';

    if (eventos.length === 0) {
      container.innerHTML = '<div style="color: #64748b; font-size: 13px;">Nenhum evento agressivo registrado recentemente.</div>';
      return;
    }

    eventos.slice(0, 15).forEach(e => {
      let icon = '⚡';
      let cor = '#f59e0b';
      if (e.tipo_evento === 'EXCESSO_VELOCIDADE') { icon = '🚨'; cor = '#ef4444'; }
      if (e.tipo_evento === 'EXCESSO_RPM') { icon = '⚙️'; cor = '#f97316'; }
      if (e.tipo_evento.includes('CERCA')) { icon = '🚧'; cor = '#ec4899'; }

      container.innerHTML += `
        <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight: 700; color: ${cor}; font-size: 12px;">${icon} ${e.tipo_evento}</span>
            <span style="font-size: 11px; color: #64748b;">${e.timestamp.substring(11, 19)}</span>
          </div>
          <div style="font-size: 12px; color: #f8fafc; margin-top: 4px;">Veículo: <b>${e.veiculo_placa}</b> | Condutor: ${e.motorista_identificador || 'N/I'}</div>
          <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">${e.detalhes || ''}</div>
        </div>
      `;
    });
  } catch (err) {
    console.error('Erro ao carregar eventos de telemetria:', err);
  }
}

// =====================================================================
// ABASTECIMENTO & POSTOS CREDENCIADOS
// =====================================================================
async function loadFuelModule() {
  const tbody = document.getElementById('fuel-table-body');
  const stationsContainer = document.getElementById('fuel-stations-list');
  if (!tbody) return;

  try {
    const transacoes = await api.getFuelTransactions();
    tbody.innerHTML = '';

    transacoes.forEach(t => {
      const isAnomalia = t.anomalia_detectada;
      const statusBadge = isAnomalia 
        ? '<span class="status-pill danger" title="' + (t.motivo_anomalia || '') + '">🚨 ANOMALIA DETECTADA</span>'
        : '<span class="status-pill success">✓ AUDITADO</span>';

      const kml = t.consumo_calculado_kml ? `${t.consumo_calculado_kml} km/L` : '-';
      const lkm = t.consumo_l_km ? `(${t.consumo_l_km} L/km)` : '';

      tbody.innerHTML += `
        <tr style="${isAnomalia ? 'background: rgba(239, 68, 68, 0.08);' : ''}">
          <td>${t.data_hora ? t.data_hora.substring(0, 16).replace('T', ' ') : '-'}</td>
          <td><b>${t.veiculo_placa}</b></td>
          <td>${t.motorista_identificador || '-'}</td>
          <td>${t.posto_combustivel}</td>
          <td>${t.litros.toFixed(1)} L (${t.tipo_combustivel})</td>
          <td>R$ ${t.valor_total.toFixed(2)}</td>
          <td>${t.odometro_km.toLocaleString('pt-BR')} km</td>
          <td><b>${kml}</b> <span style="font-size:10px; color:#94a3b8;">${lkm}</span></td>
          <td>${statusBadge}</td>
        </tr>
      `;
    });

    // Postos credenciados
    if (stationsContainer) {
      const postos = await api.getFuelStations();
      stationsContainer.innerHTML = '';
      postos.forEach(p => {
        stationsContainer.innerHTML += `
          <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong style="color: #60a5fa; font-size: 13px;">⛽ ${p.nome_fantasia}</strong>
              <span class="status-pill success">CREDENCIADO</span>
            </div>
            <div style="font-size: 11.5px; color: #94a3b8; margin-top: 4px;">CNPJ: ${p.cnpj} | Bandeira: <b>${p.bandeira}</b></div>
            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 2px;">📍 ${p.endereco} - ${p.cidade}/${p.uf}</div>
            <div style="font-size: 10.5px; color: #64748b; margin-top: 4px;">GPS: ${p.latitude || '-'}, ${p.longitude || '-'} | Contato: ${p.contato || '-'}</div>
          </div>
        `;
      });
    }
  } catch (err) {
    console.error('Erro ao carregar abastecimentos:', err);
  }
}

// =====================================================================
// MANUTENÇÃO & GESTÃO DE PNEUS
// =====================================================================
async function loadMaintenanceModule() {
  const tbodyOS = document.getElementById('os-table-body');
  const tbodyTires = document.getElementById('tires-table-body');
  const workshopsContainer = document.getElementById('workshops-list');

  try {
    // 1. Ordens de Serviço
    if (tbodyOS) {
      const ordens = await api.getMaintenanceOS();
      tbodyOS.innerHTML = '';
      ordens.forEach(os => {
        let badge = 'info';
        if (os.status === 'CONCLUIDA') badge = 'success';
        if (os.status === 'EM_ANDAMENTO') badge = 'warning';
        if (os.status === 'CANCELADA') badge = 'danger';

        const btnConcluir = os.status !== 'CONCLUIDA' 
          ? `<button class="btn btn-emerald btn-sm" onclick="concluirOS('${os.id}')">Concluir OS</button>`
          : '<span style="color:#10b981; font-weight:600; font-size:11px;">Finalizada</span>';

        tbodyOS.innerHTML += `
          <tr>
            <td><b>${os.numero_os}</b></td>
            <td><b>${os.veiculo_placa}</b></td>
            <td><span class="status-pill ${os.tipo === 'PREVENTIVA' ? 'info' : 'warning'}">${os.tipo}</span></td>
            <td>${os.oficina_credenciada}</td>
            <td>R$ ${os.valor_total.toFixed(2)}</td>
            <td>${os.data_previsao}</td>
            <td><span class="status-pill ${badge}">${os.status}</span></td>
            <td>${btnConcluir}</td>
          </tr>
        `;
      });
    }

    // 2. Inventário de Pneus (CONTRAN)
    if (tbodyTires) {
      const pneus = await api.getTires();
      tbodyTires.innerHTML = '';
      pneus.forEach(p => {
        const isCritico = p.sulco_atual_mm < 1.6;
        const isRecapar = p.sulco_atual_mm <= 3.0 && !isCritico;
        
        let statusBadge = '<span class="status-pill success">BOM</span>';
        if (isCritico) {
          statusBadge = '<span class="status-pill danger" title="Limite legal CONTRAN violado (< 1.6mm)">⚠️ CRÍTICO CONTRAN</span>';
        } else if (isRecapar) {
          statusBadge = '<span class="status-pill warning">RECAPAR (≤3mm)</span>';
        }

        tbodyTires.innerHTML += `
          <tr style="${isCritico ? 'background: rgba(239, 68, 68, 0.08);' : ''}">
            <td><b>${p.numero_fogo}</b></td>
            <td>${p.marca_modelo} (${p.dimensao})</td>
            <td><b>${p.veiculo_placa || 'ESTOQUE'}</b> - ${p.posicao_atual}</td>
            <td>${p.pressao_psi} PSI</td>
            <td><b style="${isCritico ? 'color: #ef4444; font-size: 14px;' : ''}">${p.sulco_atual_mm.toFixed(1)} mm</b> (orig. ${p.sulco_original_mm}mm)</td>
            <td>${p.km_rodado_total.toLocaleString('pt-BR')} km</td>
            <td>${statusBadge}</td>
          </tr>
        `;
      });
    }

    // 3. Oficinas Credenciadas
    if (workshopsContainer) {
      const oficinas = await api.getWorkshops();
      workshopsContainer.innerHTML = '';
      oficinas.forEach(o => {
        workshopsContainer.innerHTML += `
          <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong style="color: #60a5fa; font-size: 13px;">🛠️ ${o.nome_fantasia}</strong>
              <span class="status-pill success">CREDENCIADA</span>
            </div>
            <div style="font-size: 11.5px; color: #94a3b8; margin-top: 4px;">Especialidade: <b>${o.especialidade}</b></div>
            <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 2px;">📍 ${o.endereco} - ${o.cidade}/${o.uf} | Tel: ${o.telefone || '-'}</div>
            <div style="font-size: 10.5px; color: #64748b; margin-top: 4px;">Resp. Técnico: ${o.responsavel_tecnico || '-'} | CNPJ: ${o.cnpj}</div>
          </div>
        `;
      });
    }
  } catch (err) {
    console.error('Erro ao carregar módulo de manutenção:', err);
  }
}

async function concluirOS(osId) {
  if (!confirm('Deseja marcar esta Ordem de Serviço como CONCLUÍDA e liberar o veículo para circulação?')) return;
  try {
    await api.updateOSStatus(osId, 'CONCLUIDA');
    showToast('Ordem de Serviço concluída com sucesso! Veículo liberado para DISPONÍVEL.');
    await loadMaintenanceModule();
  } catch (err) {
    alert('Erro ao concluir OS: ' + err.message);
  }
}

// =====================================================================
// VIAGENS, DESPACHO & CHECKLIST DIGITAL
// =====================================================================
async function loadTripsModule() {
  const tbodyTrips = document.getElementById('trips-table-body');
  const tbodyCheck = document.getElementById('checklists-table-body');

  try {
    if (tbodyTrips) {
      const viagens = await api.getTrips();
      tbodyTrips.innerHTML = '';
      viagens.forEach(v => {
        let badge = 'info';
        if (v.status === 'EM_ANDAMENTO') badge = 'warning';
        if (v.status === 'FINALIZADA') badge = 'success';

        let btnAcao = '';
        if (v.status === 'SOLICITADA') {
          btnAcao = `<button class="btn btn-primary btn-sm" onclick="despacharViagem('${v.id}')">Despachar</button>`;
        } else if (v.status === 'EM_ANDAMENTO') {
          btnAcao = `<button class="btn btn-emerald btn-sm" onclick="finalizarViagem('${v.id}')">Concluir</button>`;
        }

        tbodyTrips.innerHTML += `
          <tr>
            <td><b>${v.codigo_viagem}</b></td>
            <td><b>${v.veiculo_placa}</b></td>
            <td>${v.motorista_identificador}</td>
            <td>${v.origem} ➔ ${v.destino}</td>
            <td>${v.distancia_estimada_km} km (${v.eta_estimado_minutos} min)</td>
            <td><span class="status-pill ${badge}">${v.status}</span></td>
            <td>${btnAcao}</td>
          </tr>
        `;
      });
    }

    if (tbodyCheck) {
      const checks = await api.getChecklists();
      tbodyCheck.innerHTML = '';
      checks.forEach(c => {
        const isReprovado = c.status_aprovacao === 'REPROVADO_IMPEDIDO';
        const badge = isReprovado ? 'danger' : 'success';

        tbodyCheck.innerHTML += `
          <tr style="${isReprovado ? 'background: rgba(239, 68, 68, 0.08);' : ''}">
            <td>${c.data_hora ? c.data_hora.substring(0, 16).replace('T', ' ') : '-'}</td>
            <td><b>${c.veiculo_placa}</b></td>
            <td>${c.tipo}</td>
            <td>${c.motorista_identificador}</td>
            <td><span class="status-pill ${badge}">${c.status_aprovacao}</span></td>
            <td style="font-size: 11px; color: ${isReprovado ? '#f87171' : '#94a3b8'};">${c.motivo_reprovacao || 'Todos os itens conformes'}</td>
          </tr>
        `;
      });
    }
  } catch (err) {
    console.error('Erro ao carregar viagens:', err);
  }
}

async function despacharViagem(tripId) {
  try {
    await api.dispatchTrip(tripId);
    showToast('Viagem despachada com sucesso! Veículo em trânsito.');
    await loadTripsModule();
  } catch (err) {
    alert('Bloqueio Operacional: ' + err.message + '\n\nCertifique-se de realizar e aprovar a vistoria do Checklist Pré-Viagem.');
  }
}

async function finalizarViagem(tripId) {
  try {
    await api.finishTrip(tripId);
    showToast('Viagem concluída e veículo liberado no pátio.');
    await loadTripsModule();
  } catch (err) {
    alert('Erro ao finalizar viagem: ' + err.message);
  }
}

// =====================================================================
// COMPLIANCE, MULTAS & PRAZOS LEGAIS
// =====================================================================
async function loadComplianceModule() {
  const tbodyFines = document.getElementById('fines-table-body');
  if (!tbodyFines) return;

  try {
    const multas = await api.getFines();
    tbodyFines.innerHTML = '';

    multas.forEach(m => {
      const isPendente = m.status_indicacao === 'PENDENTE';
      const btnIndicar = isPendente
        ? `<button class="btn btn-amber btn-sm" onclick="openIndicarModal('${m.id}', '${m.veiculo_placa}', '${m.limite_indicacao_condutor}')">Indicar Condutor DETRAN</button>`
        : `<span style="color:#10b981; font-weight:600; font-size:11px;">${m.protocolo_detran || 'Homologado'}</span>`;

      tbodyFines.innerHTML += `
        <tr>
          <td><b>${m.auto_infracao}</b></td>
          <td><b>${m.veiculo_placa}</b></td>
          <td>${m.descricao_infracao} (${m.pontos} pts)</td>
          <td>R$ ${m.valor_multa.toFixed(2)}</td>
          <td><b style="color: ${isPendente ? '#f59e0b' : '#94a3b8'};">${m.limite_indicacao_condutor}</b></td>
          <td><span class="status-pill ${isPendente ? 'warning' : 'success'}">${m.status_indicacao}</span></td>
          <td>${btnIndicar}</td>
        </tr>
      `;
    });
  } catch (err) {
    console.error('Erro ao carregar multas:', err);
  }
}

// =====================================================================
// RELATÓRIOS, TCO & EXPORTAÇÃO COM DATAS DE LANÇAMENTOS E FILTRO TEMPORAL
// =====================================================================
function alternarModoFiltroRelatorio(modo) {
  const boxMes = document.getElementById('box-filtro-mes');
  const boxPeriodo = document.getElementById('box-filtro-periodo');
  if (!boxMes || !boxPeriodo) return;

  if (modo === 'MES') {
    boxMes.style.display = 'flex';
    boxPeriodo.style.display = 'none';
  } else if (modo === 'PERIODO') {
    boxMes.style.display = 'none';
    boxPeriodo.style.display = 'flex';
  } else {
    // TODOS
    boxMes.style.display = 'none';
    boxPeriodo.style.display = 'none';
  }
}

function obterParametrosFiltroRelatorio() {
  const modo = document.getElementById('rel-modo-filtro')?.value || 'MES';
  const tipo = document.getElementById('rel-filtro-tipo')?.value || 'TODOS';
  const sec = document.getElementById('rel-filtro-secretaria')?.value || '';

  const params = {};
  if (tipo && tipo !== 'TODOS') params.tipo = tipo;
  if (sec) params.secretaria = sec;

  if (modo === 'MES') {
    params.mes = document.getElementById('rel-filtro-mes')?.value || '11';
    params.ano = document.getElementById('rel-filtro-ano')?.value || '2026';
  } else if (modo === 'PERIODO') {
    params.data_inicio = document.getElementById('rel-data-inicio')?.value || '';
    params.data_fim = document.getElementById('rel-data-fim')?.value || '';
  }
  return { modo, params };
}

async function filtrarRelatoriosPeriodo() {
  const tbodyLanc = document.getElementById('lancamentos-table-body');
  const bannerPeriodo = document.getElementById('rel-resumo-periodo');
  const bannerEmissao = document.getElementById('rel-resumo-data-emissao');
  const bannerTotalLanc = document.getElementById('rel-resumo-total-lanc');
  const bannerValorTotal = document.getElementById('rel-resumo-valor-total');
  const tbodySec = document.getElementById('secretarias-table-body');

  const { modo, params } = obterParametrosFiltroRelatorio();

  if (tbodyLanc) {
    tbodyLanc.innerHTML = '<tr><td colspan="10" style="text-align:center; color:#64748b;">Consultando extrato com datas de lançamento...</td></tr>';
  }

  try {
    const data = await api.getExtratoLancamentos(params);
    if (!data) return;

    if (bannerPeriodo) bannerPeriodo.innerText = data.periodo_auditado || 'Novembro/2026';
    if (bannerEmissao) bannerEmissao.innerText = data.data_hora_emissao_utc ? new Date(data.data_hora_emissao_utc).toLocaleString('pt-BR') : new Date().toLocaleString('pt-BR');
    if (bannerTotalLanc) bannerTotalLanc.innerText = data.total_registros ?? 0;
    if (bannerValorTotal) bannerValorTotal.innerText = `R$ ${(data.valor_total_consolidado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    if (tbodyLanc) {
      if (!data.lancamentos || data.lancamentos.length === 0) {
        tbodyLanc.innerHTML = '<tr><td colspan="10" style="text-align:center; color:#64748b; padding:18px;">Nenhum lançamento registrado no período selecionado.</td></tr>';
      } else {
        tbodyLanc.innerHTML = '';
        data.lancamentos.forEach(l => {
          const badgeTipo = l.tipo_operacao === 'CARTAO_COMBUSTIVEL_SC' 
            ? '<span class="badge badge-success" style="font-size:10px;">💳 Cartão SC</span>'
            : l.tipo_operacao === 'ORDEM_SERVICO'
            ? '<span class="badge badge-warning" style="font-size:10px;">🔧 OS Oficina</span>'
            : '<span class="badge badge-info" style="font-size:10px;">⛽ Abastec.</span>';

          tbodyLanc.innerHTML += `
            <tr>
              <td style="font-weight:700; color:#1e40af; background-color:#f8fafc; white-space:nowrap;">
                📅 ${l.data_lancamento_formatada || '-'}
              </td>
              <td style="white-space:nowrap; font-size:11.5px; color:#64748b;">${l.competencia_mes_ano || '-'}</td>
              <td>${badgeTipo}</td>
              <td><b>${l.placa_ativo || '-'}</b></td>
              <td style="font-size:12px;">${l.secretaria || '-'}</td>
              <td style="font-size:11px; font-family:monospace; color:#475569;">${l.documento_autorizacao || '-'}</td>
              <td style="font-size:12px; max-width:220px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${l.descricao_fornecimento || ''}">
                ${l.descricao_fornecimento || '-'}
              </td>
              <td style="text-align:right;">${(l.quantidade_litros_servicos || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
              <td style="text-align:right; font-weight:700; color:#0f172a;">R$ ${(l.valor_total || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
              <td><span class="badge badge-success" style="font-size:10px;">${l.status || 'AUTORIZADO'}</span></td>
            </tr>
          `;
        });
      }
    }

    // Atualiza também os totais por secretaria com os mesmos filtros temporais
    if (tbodySec) {
      const secData = await api.getSecretariaReport(params);
      tbodySec.innerHTML = '';
      if (!secData || secData.length === 0) {
        tbodySec.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#64748b;">Nenhum dado por secretaria no período.</td></tr>';
      } else {
        secData.forEach(s => {
          tbodySec.innerHTML += `
            <tr>
              <td><b>${s.secretaria}</b></td>
              <td>${s.total_veiculos}</td>
              <td>${(s.km_total_rodado || 0).toLocaleString('pt-BR')} km</td>
              <td>R$ ${(s.gasto_combustivel || 0).toFixed(2)}</td>
              <td>R$ ${(s.gasto_manutencao || 0).toFixed(2)}</td>
              <td>R$ ${(s.gasto_pedagios || 0).toFixed(2)}</td>
              <td><b>R$ ${(s.gasto_total || 0).toFixed(2)}</b></td>
              <td>R$ ${(s.custo_por_km || 0).toFixed(3)}/km</td>
              <td>${s.consumo_medio_kml || 0} km/L</td>
            </tr>
          `;
        });
      }
    }
  } catch (err) {
    console.error('Erro ao filtrar relatórios do período:', err);
    showToast('Falha ao consultar extrato de lançamentos.', 'error');
  }
}

function exportarLancamentosCSVPeriodo() {
  const { params } = obterParametrosFiltroRelatorio();
  const q = new URLSearchParams();
  if (params.mes) q.append('mes', params.mes);
  if (params.ano) q.append('ano', params.ano);
  if (params.data_inicio) q.append('data_inicio', params.data_inicio);
  if (params.data_fim) q.append('data_fim', params.data_fim);
  if (params.tipo) q.append('tipo', params.tipo);
  if (params.secretaria) q.append('secretaria', params.secretaria);
  
  const query = q.toString() ? `?${q.toString()}` : '';
  window.location.href = `/api/reports/export/lancamentos-csv${query}`;
  showToast('Download do extrato analítico com datas de lançamento iniciado!');
}

async function loadReportsModule() {
  const tbodyTCO = document.getElementById('tco-table-body');

  try {
    // 1. TCO por Veículo
    if (tbodyTCO) {
      const tcoList = await api.getTCOReport();
      tbodyTCO.innerHTML = '';
      tcoList.forEach(t => {
        tbodyTCO.innerHTML += `
          <tr>
            <td><b>${t.veiculo_placa}</b></td>
            <td>${t.modelo}</td>
            <td>${t.km_total_rodado.toLocaleString('pt-BR')} km</td>
            <td>R$ ${t.custo_combustivel_total.toFixed(2)}</td>
            <td>R$ ${t.custo_manutencao_total.toFixed(2)}</td>
            <td>R$ ${t.custo_pneus_total.toFixed(2)}</td>
            <td>R$ ${t.custo_pedagios_total.toFixed(2)}</td>
            <td><b style="color: #60a5fa;">R$ ${t.custo_total_operacional.toFixed(2)}</b></td>
            <td><b style="color: #34d399; font-size: 14px;">R$ ${t.cpk_reais_por_km.toFixed(3)}/km</b></td>
          </tr>
        `;
      });
    }

    // 2. Extrato Temporal com Datas de Lançamentos Obrigatórias e Totais por Secretaria
    await filtrarRelatoriosPeriodo();

    // 3. Auditoria de Soberania de Dados
    const comp = await api.getNationalCompliance();
    const compElem = document.getElementById('national-compliance-info');
    if (compElem) {
      compElem.innerHTML = `
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 14px;">
          <div style="font-weight: 700; color: #34d399; margin-bottom: 6px;">✓ Soberania de Dados e Conformidade LGPD em Território Nacional</div>
          <div style="font-size: 12px; color: #cbd5e1;">Datacenter: <b>${comp.localizacao_datacenter}</b></div>
          <div style="font-size: 12px; color: #cbd5e1;">Banco de Dados: <b>${comp.motor_banco_dados} (${comp.modo_execucao})</b></div>
          <div style="font-size: 11.5px; color: #94a3b8; margin-top: 4px;">Hash Criptográfico de Credenciais: ${comp.conformidade_lgpd.hash_criptografico_credenciais} | Trilha Imutável Ativa</div>
        </div>
      `;
    }
  } catch (err) {
    console.error('Erro ao carregar relatórios:', err);
  }
}

function exportarRelatorioCSV() {
  const sec = document.getElementById('select-secretaria')?.value || '';
  window.location.href = `/api/reports/export/csv${sec ? '?secretaria=' + sec : ''}`;
  showToast('Download do arquivo CSV de auditoria financeira iniciado!');
}

function imprimirRelatorioPDF() {
  window.print();
}

// =====================================================================
// SEGURANÇA & API KEYS IOT
// =====================================================================
async function loadSecurityModule() {
  const containerKeys = document.getElementById('api-keys-list');
  if (!containerKeys) return;

  try {
    const keys = await api.getAPIKeys();
    containerKeys.innerHTML = '';
    keys.forEach(k => {
      containerKeys.innerHTML += `
        <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px 14px; margin-bottom: 8px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color: #60a5fa; font-size: 13px;">🔑 ${k.nome_dispositivo}</strong>
            <span class="status-pill success">ATIVA</span>
          </div>
          <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Prefixo Seguro: <code>${k.prefix}</code> | Papel: <b>${k.role}</b></div>
          <div style="font-size: 11px; color: #64748b; margin-top: 2px;">${k.descricao || ''} - Criada em: ${k.created_at.substring(0, 10)}</div>
        </div>
      `;
    });
  } catch (err) {
    console.error('Erro ao carregar módulo de segurança:', err);
  }
}

// =====================================================================
// SIMULAÇÃO DE TELEMETRIA EM TRÂNSITO
// =====================================================================
function setupSimulateButton() {
  const btn = document.getElementById('btn-simulate-step');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    btn.innerHTML = '⏳ Simulando Pings...';

    try {
      const res = await api.simulateFleetStep();
      showToast(`Pings IoT Ingeridos com sucesso! ${res.veiculos_movimentados} veículos movimentados.`);
      
      const activeTab = document.querySelector('.nav-item.active')?.dataset.tab;
      if (activeTab === 'rastreamento') {
        await updateVehicleMarkersOnMap();
        await loadTelemetryEvents();
      }
      await loadDashboard();
    } catch (err) {
      alert('Erro na simulação IoT: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '🛰️ Simular Telemetria em Trânsito';
    }
  });
}

// =====================================================================
// MODAIS & CADASTROS RÁPIDOS
// =====================================================================
function setupModals() {
  // Fechar modais ao clicar no X ou backdrop
  document.querySelectorAll('.modal-close, .modal-backdrop').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target === el) {
        document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.remove('active'));
      }
    });
  });

  // Formulário Novo Abastecimento
  const formAbast = document.getElementById('form-novo-abastecimento');
  if (formAbast) {
    formAbast.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        veiculo_placa: document.getElementById('abast-placa').value.toUpperCase(),
        motorista_identificador: document.getElementById('abast-motorista').value,
        posto_combustivel: document.getElementById('abast-posto').value,
        tipo_combustivel: document.getElementById('abast-combustivel').value,
        litros: parseFloat(document.getElementById('abast-litros').value),
        valor_litro: parseFloat(document.getElementById('abast-valor-litro').value),
        odometro_km: parseFloat(document.getElementById('abast-odometro').value),
        cartao_combustivel: document.getElementById('abast-cartao').value,
        latitude: parseFloat(document.getElementById('abast-lat').value) || -25.5312,
        longitude: parseFloat(document.getElementById('abast-lng').value) || -49.2010
      };

      try {
        const res = await api.createFuelTransaction(payload);
        document.getElementById('modal-novo-abastecimento').classList.remove('active');
        formAbast.reset();
        
        if (res.anomalia_detectada) {
          alert('⚠️ ALERTA DE AUDITORIA ANTIFRAUDE:\n\n' + res.motivo_anomalia);
        } else {
          showToast('Abastecimento registrado e auditado com sucesso!');
        }
        await loadFuelModule();
        await loadDashboard();
      } catch (err) {
        alert('Erro ao registrar abastecimento: ' + err.message);
      }
    });
  }

  // Formulário Nova Ordem de Serviço
  const formOS = document.getElementById('form-nova-os');
  if (formOS) {
    formOS.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        veiculo_placa: document.getElementById('os-placa').value.toUpperCase(),
        tipo: document.getElementById('os-tipo').value,
        data_previsao: document.getElementById('os-previsao').value,
        oficina_credenciada: document.getElementById('os-oficina').value,
        valor_total: parseFloat(document.getElementById('os-valor').value) || 0.0,
        odometro_momento_km: parseFloat(document.getElementById('os-odometro').value) || 0.0,
        observacoes: document.getElementById('os-obs').value,
        itens_pecas: [],
        servicos: []
      };

      try {
        await api.createMaintenanceOS(payload);
        document.getElementById('modal-nova-os').classList.remove('active');
        formOS.reset();
        showToast('Ordem de Serviço aberta! Veículo movido para MANUTENÇÃO.');
        await loadMaintenanceModule();
        await loadDashboard();
      } catch (err) {
        alert('Erro ao abrir OS: ' + err.message);
      }
    });
  }

  // Formulário Checklist Digital
  const formCheck = document.getElementById('form-checklist-digital');
  if (formCheck) {
    formCheck.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        veiculo_placa: document.getElementById('chk-placa').value.toUpperCase(),
        motorista_identificador: document.getElementById('chk-motorista').value,
        tipo: document.getElementById('chk-tipo').value,
        itens: [
          { item: 'Faróis e Lanternas', conforme: document.getElementById('chk-farois').checked },
          { item: 'Sistema de Freios', conforme: document.getElementById('chk-freios').checked },
          { item: 'Condição dos Pneus e Estepe', conforme: document.getElementById('chk-pneus').checked },
          { item: 'Nível de Óleo e Arrefecimento', conforme: document.getElementById('chk-oleo').checked },
          { item: 'Lataria e Vidros', conforme: document.getElementById('chk-lataria').checked }
        ]
      };

      try {
        const res = await api.createChecklist(payload);
        document.getElementById('modal-checklist-digital').classList.remove('active');
        formCheck.reset();
        
        if (res.status_aprovacao === 'REPROVADO_IMPEDIDO') {
          alert('🚫 BLOQUEIO DE SEGURANÇA OPERACIONAL:\n\n' + res.motivo_reprovacao + '\n\nO veículo não poderá ser despachado até a regularização.');
        } else {
          showToast('Vistoria de Checklist registrada e aprovada!');
        }
        await loadTripsModule();
      } catch (err) {
        alert('Erro ao registrar checklist: ' + err.message);
      }
    });
  }

  // Formulário Indicar Condutor Multa
  const formIndicar = document.getElementById('form-indicar-condutor');
  if (formIndicar) {
    formIndicar.addEventListener('submit', async (e) => {
      e.preventDefault();
      const multaId = document.getElementById('indicar-multa-id').value;
      const payload = {
        motorista_identificador: document.getElementById('indicar-condutor-nome').value,
        documento_cnh: document.getElementById('indicar-condutor-cnh').value
      };

      try {
        const res = await api.indicateFineDriver(multaId, payload);
        document.getElementById('modal-indicar-condutor').classList.remove('active');
        alert(`✓ Protocolo DETRAN Emitido com Sucesso!\n\nProtocolo Oficial: ${res.protocolo_detran}\nPontos debitados no prontuário do condutor.`);
        await loadComplianceModule();
      } catch (err) {
        alert('Erro no workflow de indicação: ' + err.message);
      }
    });
  }
}

// Helpers para abrir modais
function openNovoAbastecimentoModal() {
  document.getElementById('modal-novo-abastecimento')?.classList.add('active');
}

function openNovaOSModal() {
  document.getElementById('modal-nova-os')?.classList.add('active');
}

function openChecklistModal() {
  document.getElementById('modal-checklist-digital')?.classList.add('active');
}

function openIndicarModal(multaId, placa, limite) {
  document.getElementById('indicar-multa-id').value = multaId;
  document.getElementById('indicar-info-multa').textContent = `Veículo ${placa} - Prazo Limite Legal: ${limite}`;
  document.getElementById('modal-indicar-condutor')?.classList.add('active');
}

async function openHistoryModal(placa) {
  try {
    const hist = await api.getVehicleHistory(placa);
    alert(`Dossiê de Manutenção do Veículo ${placa}:\n\n` +
          `• Total de Ordens de Serviço: ${hist.total_ordens_servico}\n` +
          `• Total Gasto em Manutenção: R$ ${hist.total_gasto_manutencao.toFixed(2)}\n` +
          `• Pneus Instalados: ${hist.pneus_instalados.length}\n` +
          `• Peças Substituídas: ${hist.total_pecas_substituidas} itens`);
  } catch (err) {
    alert('Erro ao carregar histórico: ' + err.message);
  }
}

function showToast(mensagem) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>ℹ️</span> <div>${mensagem}</div>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4000);
}

// =====================================================================
// COPILOT DE INTELIGÊNCIA ARTIFICIAL & DIAGNÓSTICO PRESCRITIVO
// =====================================================================
async function loadAICopilotModule() {
  const container = document.getElementById('ai-chat-messages');
  if (container && container.children.length === 0) {
    appendAIMessage('Olá! Sou o **Copilot de IA do FrotaSaaS Enterprise 2.0**.\n\nFui treinado com o conhecimento empírico de 9.514 Ordens de Serviço, 6.954 anomalias e R$ 4,92 milhões auditados. Posso responder sobre métricas da frota, anomalias por secretaria, auditoria antifraude de combustível e otimização prescritiva de leilão.\n\nComo posso ajudar?');
  }
}

async function sendAIChatMessage(customText = null) {
  const input = document.getElementById('ai-chat-input');
  const text = customText || input?.value.trim();
  if (!text) return;
  if (!customText && input) input.value = '';

  appendUserMessage(text);
  const loadingId = appendAILoading();

  try {
    const res = await api.chatAI(text);
    removeAILoading(loadingId);
    appendAIMessage(res.resposta);
  } catch (err) {
    removeAILoading(loadingId);
    appendAIMessage(`⚠️ Não foi possível consultar o motor de IA: ${err.message}`);
  }
}

function appendUserMessage(text) {
  const container = document.getElementById('ai-chat-messages');
  if (!container) return;
  const div = document.createElement('div');
  div.className = 'ai-msg user-msg';
  div.style.cssText = 'display:flex; flex-direction:column; align-items:flex-end; margin-bottom:12px;';
  div.innerHTML = `
    <div style="background: #2563eb; color: #fff; padding: 10px 14px; border-radius: 12px 12px 2px 12px; max-width: 80%; font-size: 13px; line-height: 1.4;">
      ${escapeHtml(text)}
    </div>
    <div style="font-size: 10px; color: #64748b; margin-top: 3px;">Você • ${new Date().toLocaleTimeString()}</div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function appendAIMessage(text) {
  const container = document.getElementById('ai-chat-messages');
  if (!container) return;
  const div = document.createElement('div');
  div.className = 'ai-msg assistant-msg';
  div.style.cssText = 'display:flex; flex-direction:column; align-items:flex-start; margin-bottom:12px;';
  
  let formatted = escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n• /g, '<br>• ');

  div.innerHTML = `
    <div style="display:flex; gap:8px; max-width:85%;">
      <div style="font-size:20px; width:32px; height:32px; border-radius:50%; background:rgba(56,189,248,0.15); display:flex; align-items:center; justify-content:center; flex-shrink:0;">🤖</div>
      <div style="background: #1e293b; color: #f1f5f9; padding: 12px 16px; border-radius: 12px 12px 12px 2px; border: 1px solid #334155; font-size: 13px; line-height: 1.5;">
        ${formatted}
      </div>
    </div>
    <div style="font-size: 10px; color: #64748b; margin-top: 3px; margin-left: 40px;">Copilot IA • ${new Date().toLocaleTimeString()}</div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function appendAILoading() {
  const container = document.getElementById('ai-chat-messages');
  if (!container) return null;
  const id = 'loading-' + Date.now();
  const div = document.createElement('div');
  div.id = id;
  div.style.cssText = 'display:flex; gap:8px; margin-bottom:12px; align-items:center;';
  div.innerHTML = `
    <div style="font-size:20px; width:32px; height:32px; border-radius:50%; background:rgba(56,189,248,0.15); display:flex; align-items:center; justify-content:center;">🤖</div>
    <div style="background: #1e293b; color: #38bdf8; padding: 8px 14px; border-radius: 12px; font-size: 12px; font-style: italic; border: 1px solid #334155;">
      Analisando base de frotas e calculando resposta...
    </div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeAILoading(id) {
  if (id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
}

function escapeHtml(str) {
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

async function runAIDiagnostic() {
  const placa = document.getElementById('diag-placa')?.value || 'QHA-8421';
  const km = parseFloat(document.getElementById('diag-km')?.value || '185000');
  const anos = parseInt(document.getElementById('diag-anos')?.value || '8');
  const custo = parseFloat(document.getElementById('diag-custo')?.value || '32000');
  const resultadoDiv = document.getElementById('diag-resultado');

  if (resultadoDiv) {
    resultadoDiv.innerHTML = '<div style="color:#38bdf8; padding:12px;">Processando diagnóstico prescritivo via IA...</div>';
  }

  try {
    const res = await api.diagnosticarVeiculoAI({
      placa,
      hodometro: km,
      idade_anos: anos,
      custo_manutencao_acumulado: custo
    });

    const corBadge = res.cor === 'vermelho' ? '#ef4444' : (res.cor === 'amarelo' ? '#f59e0b' : '#10b981');
    resultadoDiv.innerHTML = `
      <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid ${corBadge}; border-radius: 8px; padding: 16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <strong style="font-size:15px; color:#fff;">Diagnóstico: ${res.placa}</strong>
          <span style="background:${corBadge}; color:#fff; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;">${res.classificacao}</span>
        </div>
        <p style="color:#cbd5e1; font-size:13px; margin-bottom:6px;"><strong>Score de Risco Prescritivo:</strong> ${res.score_risco_percentual}% (Prioridade ${res.prioridade})</p>
        <p style="color:#e2e8f0; font-size:13px; margin-bottom:8px;"><strong>Recomendação da IA:</strong> ${res.recomendacao_prescritiva}</p>
        <div style="font-size:12px; color:#94a3b8;">
          <strong>Fatores Identificados:</strong>
          <ul style="margin:4px 0 0 16px;">
            ${res.motivos_detectados.map(m => `<li>${m}</li>`).join('')}
          </ul>
        </div>
      </div>
    `;
  } catch (err) {
    if (resultadoDiv) {
      resultadoDiv.innerHTML = `<div style="color:#ef4444; padding:12px;">Falha no diagnóstico: ${err.message}</div>`;
    }
  }
}

async function runAIAuditFuel() {
  const placa = document.getElementById('audit-placa')?.value || 'BRA-2E19';
  const litros = parseFloat(document.getElementById('audit-litros')?.value || '75');
  const capacidade = parseFloat(document.getElementById('audit-capacidade')?.value || '60');
  const kmAtual = parseFloat(document.getElementById('audit-km-atual')?.value || '105200');
  const kmAnterior = parseFloat(document.getElementById('audit-km-anterior')?.value || '105250');
  const preco = parseFloat(document.getElementById('audit-preco')?.value || '6.19');
  const resultadoDiv = document.getElementById('audit-resultado');

  if (resultadoDiv) {
    resultadoDiv.innerHTML = '<div style="color:#38bdf8; padding:12px;">Auditando transação de combustível com os 4 algoritmos antifraude...</div>';
  }

  try {
    const res = await api.auditarAbastecimentoAI({
      placa,
      litros,
      capacidade_tanque: capacidade,
      hodometro_atual: kmAtual,
      hodometro_anterior: kmAnterior,
      preco_litro: preco,
      posto_credenciado: true
    });

    const cor = res.aprovado_sem_ressalvas ? '#10b981' : '#ef4444';
    resultadoDiv.innerHTML = `
      <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid ${cor}; border-radius: 8px; padding: 16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <strong style="font-size:15px; color:#fff;">Auditoria Antifraude: ${res.placa}</strong>
          <span style="background:${cor}; color:#fff; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;">${res.status_auditoria}</span>
        </div>
        <p style="color:#cbd5e1; font-size:13px; margin-bottom:6px;"><strong>Score de Risco de Fraude:</strong> ${res.score_risco_fraude}%</p>
        <p style="color:#e2e8f0; font-size:13px; margin-bottom:8px;"><strong>Ação Prescrita:</strong> ${res.acao_recomendada}</p>
        <div style="font-size:12px; color:#94a3b8;">
          <strong>Apontamentos Antifraude:</strong>
          <ul style="margin:4px 0 0 16px;">
            ${res.anomalias_detectadas.map(a => `<li style="color:${res.aprovado_sem_ressalvas ? '#cbd5e1' : '#f87171'}">${a}</li>`).join('')}
          </ul>
        </div>
      </div>
    `;
  } catch (err) {
    if (resultadoDiv) {
      resultadoDiv.innerHTML = `<div style="color:#ef4444; padding:12px;">Falha na auditoria: ${err.message}</div>`;
    }
  }
}

function toggleFloatingAIChat() {
  const modal = document.getElementById('floating-ai-window');
  if (modal) {
    modal.style.display = (modal.style.display === 'none' || !modal.style.display) ? 'flex' : 'none';
    if (modal.style.display === 'flex') {
      loadAICopilotModule();
      document.getElementById('floating-ai-input')?.focus();
    }
  }
}

async function sendFloatingAIChat() {
  const input = document.getElementById('floating-ai-input');
  const text = input?.value.trim();
  if (!text) return;
  input.value = '';

  const messagesDiv = document.getElementById('floating-ai-messages');
  if (!messagesDiv) return;

  // Add user bubble
  const userBubble = document.createElement('div');
  userBubble.style.cssText = 'background:#2563eb; color:#fff; padding:8px 12px; border-radius:12px 12px 2px 12px; font-size:12px; margin-bottom:8px; align-self:flex-end; max-width:85%;';
  userBubble.textContent = text;
  messagesDiv.appendChild(userBubble);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  // Add loading
  const loadDiv = document.createElement('div');
  loadDiv.style.cssText = 'background:#1e293b; color:#38bdf8; padding:8px 12px; border-radius:12px 12px 12px 2px; font-size:12px; margin-bottom:8px; align-self:flex-start; font-style:italic; border:1px solid #334155;';
  loadDiv.textContent = 'Processando com IA...';
  messagesDiv.appendChild(loadDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  try {
    const res = await api.chatAI(text);
    loadDiv.remove();
    const aiBubble = document.createElement('div');
    aiBubble.style.cssText = 'background:#1e293b; color:#f1f5f9; padding:8px 12px; border-radius:12px 12px 12px 2px; font-size:12px; margin-bottom:8px; align-self:flex-start; max-width:90%; border:1px solid #334155; line-height:1.4;';
    aiBubble.innerHTML = escapeHtml(res.resposta)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n• /g, '<br>• ');
    messagesDiv.appendChild(aiBubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  } catch (err) {
    loadDiv.textContent = '⚠️ Erro ao consultar IA: ' + err.message;
  }
}

// =====================================================================
// MÓDULO DE CADASTRO DE VEÍCULOS (MANUAL & POR IOT / CANBUS)
// =====================================================================

function alternarModoCadastro(modo) {
  const containerManual = document.getElementById('container-cadastro-manual');
  const containerIoT = document.getElementById('container-cadastro-iot');
  const btnManual = document.getElementById('btn-toggle-modo-manual');
  const btnIoT = document.getElementById('btn-toggle-modo-iot');

  if (modo === 'manual') {
    if (containerManual) containerManual.style.display = 'block';
    if (containerIoT) containerIoT.style.display = 'none';
    if (btnManual) { btnManual.className = 'btn btn-emerald'; }
    if (btnIoT) { btnIoT.className = 'btn btn-outline'; }
  } else {
    if (containerManual) containerManual.style.display = 'none';
    if (containerIoT) containerIoT.style.display = 'block';
    if (btnManual) { btnManual.className = 'btn btn-outline'; }
    if (btnIoT) { btnIoT.className = 'btn btn-emerald'; }
    carregarDispositivosDescobertosIoT();
  }
}

async function carregarModuloCadastro() {
  await carregarTabelaVeiculosCadastrados();
  await carregarDispositivosDescobertosIoT();
}

async function submeterCadastroManual() {
  const placa = document.getElementById('cad-placa')?.value.trim().toUpperCase();
  const chassi = document.getElementById('cad-chassi')?.value.trim().toUpperCase();
  const renavam = document.getElementById('cad-renavam')?.value.trim();
  const marca = document.getElementById('cad-marca')?.value.trim();
  const modelo = document.getElementById('cad-modelo')?.value.trim();
  const anoFab = parseInt(document.getElementById('cad-ano-fab')?.value || '2023');
  const anoMod = parseInt(document.getElementById('cad-ano-mod')?.value || '2024');
  const categoria = document.getElementById('cad-categoria')?.value || 'UTILITARIO';
  const combustivel = document.getElementById('cad-combustivel')?.value || 'DIESEL_S10';
  const tanque = parseFloat(document.getElementById('cad-tanque')?.value || '80');
  const carga = parseFloat(document.getElementById('cad-carga')?.value || '1450');
  const odometro = parseFloat(document.getElementById('cad-odometro')?.value || '0');
  const secretaria = document.getElementById('cad-secretaria')?.value || 'SECRETARIA_ADMINISTRACAO';

  if (!placa || !chassi || !renavam || !marca || !modelo) {
    alert('Por favor, preencha todos os campos obrigatórios do veículo.');
    return;
  }

  try {
    const payload = {
      placa,
      chassi,
      renavam,
      marca,
      modelo,
      ano_fabricacao: anoFab,
      ano_modelo: anoMod,
      categoria,
      capacidade_carga_kg: carga,
      capacidade_tanque_litros: tanque,
      tipo_combustivel: combustivel,
      odometro_atual_km: odometro,
      horimetro_atual_h: 0.0,
      status: 'DISPONIVEL',
      centro_custo: `CC_${secretaria}`,
      secretaria
    };

    const res = await api.createVehicle(payload);
    showToast(`✓ Veículo ${placa} cadastrado com sucesso na frota!`);
    alert(`✓ Sucesso! Veículo ${placa} (${marca} ${modelo}) cadastrado oficialmente na base patrimonial.`);
    document.getElementById('form-cadastro-manual-veiculo')?.reset();
    await carregarTabelaVeiculosCadastrados();
  } catch (err) {
    alert('Erro no cadastro manual: ' + err.message);
  }
}

async function carregarDispositivosDescobertosIoT() {
  const tbody = document.getElementById('iot-descobertos-tbody');
  if (!tbody) return;

  try {
    const dispositivos = await api.getDispositivosDescobertosIoT();
    if (!dispositivos || dispositivos.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:#94a3b8; padding:16px;">Nenhum dispositivo novo detectado no momento.</td></tr>';
      return;
    }

    tbody.innerHTML = dispositivos.map(d => `
      <tr>
        <td><strong>${d.modelo}</strong></td>
        <td><code>${d.serial}</code></td>
        <td><span class="status-pill info">${d.protocolo}</span></td>
        <td>
          <div style="font-size:12px;">VIN: <code>${d.vin_detectado}</code></div>
          <div style="font-size:11px; color:#94a3b8;">Km: ${d.hodometro_detectado} km • Tanque: ${d.combustivel_detectado}%</div>
        </td>
        <td>
          <span style="color:#4ade80;">📶 ${d.sinal_gsm_dbm} dBm</span> • 🛰️ ${d.satelites_fix} sats
        </td>
        <td>
          ${d.status_pareamento === 'PAREADO_ATIVO' 
            ? '<span class="status-pill success">PAREADO ATIVO</span>' 
            : '<span class="status-pill warning">AGUARDANDO PAREAMENTO</span>'}
        </td>
        <td>
          <button class="btn btn-outline" style="font-size:11px; padding:4px 8px;" onclick="selecionarDispositivoIoT('${d.serial}', '${d.protocolo}', '${d.vin_detectado}', ${d.hodometro_detectado}, ${d.combustivel_detectado})">
            ⚡ Preencher & Parear
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#ef4444; padding:16px;">Erro ao carregar dispositivos IoT: ${err.message}</td></tr>`;
  }
}

function selecionarDispositivoIoT(serial, protocolo, vin, hodometro, combustivel) {
  const inputSerial = document.getElementById('iot-serial');
  const inputProto = document.getElementById('iot-protocolo');
  const inputChassi = document.getElementById('iot-chassi');
  const inputOdometro = document.getElementById('iot-odometro');
  const inputPlaca = document.getElementById('iot-placa');
  const inputMarca = document.getElementById('iot-marca');
  const inputModelo = document.getElementById('iot-modelo');

  if (inputSerial) inputSerial.value = serial;
  if (inputProto) inputProto.value = protocolo;
  if (inputChassi) inputChassi.value = vin;
  if (inputOdometro) inputOdometro.value = hodometro;
  if (inputPlaca && !inputPlaca.value) inputPlaca.value = 'SC-IOT-' + serial.slice(-4);
  if (inputMarca && !inputMarca.value) inputMarca.value = 'Toyota';
  if (inputModelo && !inputModelo.value) inputModelo.value = 'Hilux 2.8 4x4 Power';

  showToast(`Dispositivo ${serial} selecionado para pareamento veicular.`);
}

async function submeterPareamentoIoT() {
  const serial = document.getElementById('iot-serial')?.value;
  const protocolo = document.getElementById('iot-protocolo')?.value;
  const chassi = document.getElementById('iot-chassi')?.value.trim().toUpperCase();
  const placa = document.getElementById('iot-placa')?.value.trim().toUpperCase();
  const marca = document.getElementById('iot-marca')?.value.trim();
  const modelo = document.getElementById('iot-modelo')?.value.trim();
  const odometro = parseFloat(document.getElementById('iot-odometro')?.value || '0');
  const secretaria = document.getElementById('iot-secretaria')?.value;
  const tanque = parseFloat(document.getElementById('iot-tanque')?.value || '80');
  const carga = parseFloat(document.getElementById('iot-carga')?.value || '1200');

  if (!serial || !chassi || !placa || !marca || !modelo) {
    alert('Por favor, selecione um dispositivo IoT e preencha a placa e modelo.');
    return;
  }

  try {
    const payload = {
      serial_rastreador: serial,
      protocolo: protocolo || 'CANBUS_OBD2',
      chassi_lido_ecu: chassi,
      placa: placa,
      marca: marca,
      modelo: modelo,
      ano_fabricacao: 2023,
      ano_modelo: 2024,
      categoria: 'UTILITARIO',
      tipo_combustivel: 'DIESEL_S10',
      capacidade_tanque_litros: tanque,
      capacidade_carga_kg: carga,
      odometro_ecu: odometro,
      secretaria: secretaria || 'SECRETARIA_OBRAS'
    };

    const res = await api.autoCadastroIoT(payload);
    showToast(`✓ Sucesso! Veículo ${placa} pareado e ativo via IoT!`);
    alert(`✓ Pareamento IoT Concluído com Sucesso!\n\nVeículo: ${placa} (${marca} ${modelo})\nRastreador: ${serial}\nProtocolo: ${protocolo}\nStatus: Pings de Telemetria Ativos`);
    await carregarModuloCadastro();
  } catch (err) {
    alert('Erro no pareamento IoT: ' + err.message);
  }
}

async function carregarTabelaVeiculosCadastrados() {
  const tbody = document.getElementById('veiculos-cadastrados-tbody');
  if (!tbody) return;

  try {
    const veiculos = await api.getVehicles();
    if (!veiculos || veiculos.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#94a3b8; padding:16px;">Nenhum veículo cadastrado.</td></tr>';
      return;
    }

    tbody.innerHTML = veiculos.map(v => {
      const metodo = v.metodo_cadastro || (v.rastreador_serial ? 'AUTOCADASTRO_IOT' : 'MANUAL');
      const badgeMetodo = metodo.includes('IOT') 
        ? '<span class="status-pill info">🛰️ Auto IoT</span>' 
        : '<span class="status-pill violet">📋 Manual</span>';
      
      const badgeStatus = v.status === 'DISPONIVEL' ? '<span class="status-pill success">DISPONÍVEL</span>' :
                          (v.status === 'EM_VIAGEM' ? '<span class="status-pill primary">EM VIAGEM</span>' :
                          '<span class="status-pill warning">' + v.status + '</span>');

      return `
        <tr>
          <td><strong>${v.placa}</strong></td>
          <td>${v.marca} ${v.modelo}</td>
          <td><code>${v.chassi || 'N/A'}</code></td>
          <td>${v.categoria || 'UTILITARIO'}</td>
          <td>${v.tipo_combustivel || 'DIESEL'}</td>
          <td>${(v.odometro_atual_km || 0).toLocaleString('pt-BR')} km</td>
          <td>${v.secretaria ? v.secretaria.replace('SECRETARIA_', '') : 'GERAL'}</td>
          <td>${badgeMetodo}</td>
          <td>${badgeStatus}</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color:#ef4444; padding:16px;">Erro ao carregar veículos: ${err.message}</td></tr>`;
  }
}

// =====================================================================
// MÓDULO MATRIZ DE QUALIDADE ISO/IEC 25010 & CONTRATO GOVERNO SC
// =====================================================================

async function loadISO25010Module() {
  console.log('Carregando Módulo ISO/IEC 25010 e Contrato Santa Catarina...');
  showToast('Auditoria ISO/IEC 25010 em execução...');

  try {
    // 1. Carregar Resumo do Contrato SC
    const resumoSC = await api.getContractSCSummary();
    if (resumoSC && resumoSC.ativos_por_tipo) {
      const at = resumoSC.ativos_por_tipo;
      const elVeic = document.getElementById('sc-total-veiculos');
      const elEmb = document.getElementById('sc-total-embarcacoes');
      const elGer = document.getElementById('sc-total-geradores');
      const elMaq = document.getElementById('sc-total-maquinas');

      if (elVeic) elVeic.textContent = at.VEICULOS?.quantidade || 0;
      if (elEmb) elEmb.textContent = at.EMBARCACOES?.quantidade || 0;
      if (elGer) elGer.textContent = at.GERADORES?.quantidade || 0;
      if (elMaq) elMaq.textContent = at.MAQUINAS_EQUIPAMENTOS?.quantidade || 0;
    }

    // 2. Carregar Cartões e Transações
    await carregarTabelaCartoesSC();
    await carregarTabelaTransacoesSC();

    // 3. Carregar Matriz de Qualidade ISO/IEC 25010
    const dadosISO = await api.getISO25010Compliance();
    if (dadosISO) {
      renderizarMatrizISO25010(dadosISO);
    }
  } catch (err) {
    console.error('Erro ao carregar Módulo ISO 25010:', err);
    showToast('Falha ao carregar dados ISO 25010: ' + err.message, 'error');
  }
}

function renderizarMatrizISO25010(data) {
  const scoreElem = document.getElementById('iso-score-global');
  const statusElem = document.getElementById('iso-status-badge');
  if (scoreElem) scoreElem.textContent = `${data.score_global_qualidade}%`;
  if (statusElem) statusElem.textContent = `✓ ${data.status_certificacao.replace(/_/g, ' ')}`;

  // Renderizar os 8 pilares
  const pilaresGrid = document.getElementById('iso25010-pilares-grid');
  if (pilaresGrid && data.caracteristicas_iso25010) {
    const iconesPilares = {
      'CAR-01': '🎯',
      'CAR-02': '⚡',
      'CAR-03': '🔌',
      'CAR-04': '✨',
      'CAR-05': '🛡️',
      'CAR-06': '🔒',
      'CAR-07': '🔧',
      'CAR-08': '📦'
    };

    pilaresGrid.innerHTML = data.caracteristicas_iso25010.map(car => {
      const icone = iconesPilares[car.codigo] || '📊';
      const corBarra = car.score_geral >= 98 ? '#10b981' : (car.score_geral >= 95 ? '#3b82f6' : '#f59e0b');

      return `
        <div class="card" style="padding:18px; border:1px solid rgba(51,65,85,0.7); background:rgba(15,23,42,0.85); display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-size:11px; font-weight:700; color:#94a3b8; font-family:monospace;">${car.codigo}</span>
              <span style="font-size:14px; font-weight:900; color:${corBarra};">${car.score_geral}%</span>
            </div>
            
            <h4 style="font-size:15px; font-weight:700; color:#fff; margin-bottom:4px; display:flex; align-items:center; gap:8px;">
              <span>${icone}</span> ${car.nome}
            </h4>
            <div style="font-size:11px; color:#64748b; margin-bottom:8px;"><em>${car.nome_ingles}</em></div>
            
            <!-- Barra de Progresso do Pilar -->
            <div style="height:6px; background:rgba(51,65,85,0.5); border-radius:999px; overflow:hidden; margin-bottom:12px;">
              <div style="height:100%; width:${car.score_geral}%; background:${corBarra}; border-radius:999px;"></div>
            </div>

            <p style="font-size:12px; color:#cbd5e1; line-height:1.5; margin-bottom:12px;">
              ${car.descricao}
            </p>

            <!-- Subcaracterísticas -->
            <div style="border-top:1px solid rgba(51,65,85,0.5); padding-top:10px; margin-bottom:12px;">
              <div style="font-size:11px; font-weight:700; color:#94a3b8; text-transform:uppercase; margin-bottom:6px;">
                Subcaracterísticas & Evidências:
              </div>
              <ul style="list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:6px;">
                ${car.subcaracteristicas.map(sub => `
                  <li style="font-size:11px; color:#94a3b8; line-height:1.4;">
                    <strong style="color:#f8fafc;">• ${sub.nome} (${sub.score_aderencia}%):</strong> ${sub.evidencia_tecnica}
                  </li>
                `).join('')}
              </ul>
            </div>
          </div>

          <!-- Controles Implementados -->
          <div style="background:rgba(0,0,0,0.3); padding:8px 10px; border-radius:6px; border:1px solid rgba(51,65,85,0.4);">
            <div style="font-size:10px; font-weight:700; color:#38bdf8; text-transform:uppercase; margin-bottom:4px;">
              Controles Técnicos Ativos:
            </div>
            <div style="font-size:11px; color:#cbd5e1;">
              ${car.controles_implementados.map(c => `✓ ${c}`).join('<br>')}
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Renderizar Normas Correlatas
  const normasCont = document.getElementById('normas-correlatas-container');
  if (normasCont && data.normas_correlatas) {
    normasCont.innerHTML = data.normas_correlatas.map(n => `
      <div style="background:rgba(15,23,42,0.8); border:1px solid rgba(51,65,85,0.6); border-radius:10px; padding:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <strong style="color:#fbbf24; font-size:14px;">${n.norma}</strong>
          <span class="status-pill success" style="font-size:10px;">${n.status.replace(/_/g, ' ')}</span>
        </div>
        <div style="font-size:12px; font-weight:600; color:#f8fafc; margin-bottom:6px;">${n.titulo}</div>
        <p style="font-size:11.5px; color:#94a3b8; line-height:1.5; margin-bottom:10px;">${n.escopo_aplicado}</p>
        <div style="font-size:11px; color:#cbd5e1; border-left:2px solid #f59e0b; padding-left:8px;">
          ${n.evidencias.map(e => `• ${e}`).join('<br>')}
        </div>
      </div>
    `).join('');
  }
}

async function carregarTabelaCartoesSC() {
  const tbody = document.getElementById('tbody-cartoes-sc');
  if (!tbody) return;

  try {
    const cartoes = await api.getContractSCCards();
    if (!cartoes || cartoes.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#94a3b8; padding:14px;">Nenhum cartão emitido.</td></tr>';
      return;
    }

    tbody.innerHTML = cartoes.map(c => {
      const techBadge = c.tecnologia === 'CHIP_MICROPROCESSADO'
        ? '<span class="status-pill primary">💳 Chip EMV</span>'
        : '<span class="status-pill warning">📟 Tarja Mag</span>';

      const statusBadge = c.status === 'ATIVO'
        ? '<span class="status-pill success">ATIVO</span>'
        : '<span class="status-pill danger">' + c.status + '</span>';

      const insumosStr = (c.combustiveis_autorizados || []).map(i => i.replace('DIESEL_', 'D-').replace('GASOLINA_', 'G-')).join(', ');

      return `
        <tr>
          <td><strong>${c.numero_mascarado}</strong></td>
          <td>${techBadge}</td>
          <td><code>${c.identificador_ativo}</code> <span style="font-size:10px; color:#94a3b8;">(${c.tipo_cartao.replace('CARTAO_', '')})</span></td>
          <td>${c.secretaria ? c.secretaria.replace('SECRETARIA_', '') : 'GERAL'}</td>
          <td>R$ ${c.limite_mensal_reais.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
          <td style="color:#34d399; font-weight:700;">R$ ${c.saldo_disponivel_reais.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
          <td style="font-size:11px; color:#cbd5e1;">${insumosStr}</td>
          <td>${statusBadge}</td>
          <td>
            <button class="btn btn-secondary" style="padding:4px 8px; font-size:10px;" onclick="promptRecarregarCartao('${c.id}', ${c.saldo_disponivel_reais})">
              💰 Recarregar
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color:#ef4444; padding:14px;">Erro ao carregar cartões: ${err.message}</td></tr>`;
  }
}

async function carregarTabelaTransacoesSC() {
  const tbody = document.getElementById('tbody-transacoes-sc');
  if (!tbody) return;

  try {
    const transacoes = await api.getContractSCTransactions();
    if (!transacoes || transacoes.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:#94a3b8; padding:14px;">Nenhuma transação registrada.</td></tr>';
      return;
    }

    tbody.innerHTML = transacoes.map(t => {
      const dt = t.timestamp ? new Date(t.timestamp).toLocaleDateString('pt-BR') + ' ' + new Date(t.timestamp).toLocaleTimeString('pt-BR').slice(0,5) : 'N/A';
      const statusBadge = t.autorizado
        ? '<span class="status-pill success">✓ AUTORIZADA</span>'
        : '<span class="status-pill danger">✗ RECUSADA</span>';

      return `
        <tr>
          <td><code style="color:#38bdf8;">${t.codigo_autorizacao || 'AUT-SC'}</code></td>
          <td>${dt}</td>
          <td><strong>${t.identificador_ativo}</strong></td>
          <td>${t.posto_nome || 'Posto SC'} <span style="font-size:10px; color:#94a3b8;">(${t.cidade || 'SC'})</span></td>
          <td>${t.tipo_insumo}</td>
          <td>${t.quantidade_litros_ou_unidades} L/un</td>
          <td style="font-weight:700;">R$ ${(t.valor_total || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
          <td>${t.odometro_ou_horimetro}</td>
          <td>${statusBadge}</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color:#ef4444; padding:14px;">Erro ao carregar transações: ${err.message}</td></tr>`;
  }
}

async function promptRecarregarCartao(cartaoId, saldoAtual) {
  const novoSaldoStr = prompt(`Informe o novo saldo da cota orçamentária do cartão (Saldo atual: R$ ${saldoAtual.toFixed(2)}):`, (saldoAtual + 1000).toFixed(2));
  if (!novoSaldoStr) return;
  const novoSaldo = parseFloat(novoSaldoStr);
  if (isNaN(novoSaldo) || novoSaldo <= 0) {
    alert('Valor inválido!');
    return;
  }

  try {
    await api.rechargeCardQuota(cartaoId, novoSaldo);
    showToast('✓ Cota orçamentária recarregada com sucesso!');
    await carregarTabelaCartoesSC();
  } catch (err) {
    alert('Erro ao recarregar cota: ' + err.message);
  }
}

function abrirModalNovaTransacaoCartaoSC() {
  const identificador = prompt('Informe a Placa / Prefixo do Ativo para Abastecimento com Cartão:', 'EMB-SC-MARLIM');
  if (!identificador) return;

  const insumo = prompt('Informe o Insumo (DIESEL_S10, DIESEL_MARITIMO, GASOLINA_COMUM, LUBRIFICANTE, ADITIVO_ARLA32, OLEO_2T_4T):', 'DIESEL_MARITIMO');
  if (!insumo) return;

  const litrosStr = prompt('Quantidade em Litros ou Unidades:', '100');
  if (!litrosStr) return;
  const litros = parseFloat(litrosStr);

  const valorUnitStr = prompt('Valor Unitário por Litro/Unidade (R$):', '5.40');
  if (!valorUnitStr) return;
  const valorUnit = parseFloat(valorUnitStr);

  const odometroStr = prompt('Odômetro (Km) ou Horímetro (h) atual:', '440.0');
  if (!odometroStr) return;
  const odometro = parseFloat(odometroStr);

  const payload = {
    cartao_id: 'auto-select',
    posto_credenciado_id: 'posto-sc-itajai-porto',
    posto_nome: 'Posto Marítimo e Rodoviário Porto de Itajaí',
    cidade: 'Itajaí',
    uf: 'SC',
    tipo_ativo: identificador.includes('EMB') ? 'EMBARCACAO' : (identificador.includes('GER') ? 'GERADOR' : (identificador.includes('MAQ') ? 'MAQUINA_EQUIPAMENTO' : 'UTILITARIO')),
    identificador_ativo: identificador,
    motorista_ou_operador: 'Operador Credenciado Governo SC',
    tipo_insumo: insumo,
    quantidade_litros_ou_unidades: litros,
    valor_unitario: valorUnit,
    valor_total: Math.round(litros * valorUnit * 100) / 100,
    odometro_ou_horimetro: odometro
  };

  api.authorizeCardTransaction(payload).then(res => {
    if (res.autorizado) {
      alert(`✓ TRANSAÇÃO AUTORIZADA COM SUCESSO!\n\nCódigo: ${res.codigo_autorizacao}\nAtivo: ${res.identificador_ativo}\nInsumo: ${res.tipo_insumo} (${res.quantidade_litros_ou_unidades} L)\nValor Total: R$ ${res.valor_total.toFixed(2)}\n\nCartão do Governo do Estado de Santa Catarina validado.`);
    } else {
      alert(`✗ TRANSAÇÃO RECUSADA PELO MOTOR ANTIFRAUDE!\n\nCódigo: ${res.codigo_autorizacao}\nMotivo: ${res.motivo_anomalia || res.mensagem_status}\n\nOperação bloqueada preventivamente.`);
    }
    carregarTabelaCartoesSC();
    carregarTabelaTransacoesSC();
  }).catch(err => {
    alert('Erro no processamento da transação: ' + err.message);
  });
}

function exportarRelatorioTecnicoISO() {
  window.open('/api/compliance/iso-25010', '_blank');
}


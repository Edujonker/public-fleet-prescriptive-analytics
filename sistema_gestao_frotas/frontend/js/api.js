/**
 * API Client para o Sistema Integrado de Gestão de Frotas
 * Comunicação assíncrona com backend FastAPI, JWT Bearer e tratamento resiliente.
 */

const API_BASE = '/api';

class FleetAPI {
  constructor() {
    this.token = localStorage.getItem('fleet_jwt_token') || '';
    this.currentUser = JSON.parse(localStorage.getItem('fleet_user_profile') || 'null');
  }

  setSession(token, user) {
    this.token = token;
    this.currentUser = user;
    localStorage.setItem('fleet_jwt_token', token);
    localStorage.setItem('fleet_user_profile', JSON.stringify(user));
  }

  clearSession() {
    this.token = '';
    this.currentUser = null;
    localStorage.removeItem('fleet_jwt_token');
    localStorage.removeItem('fleet_user_profile');
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });

      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        // Se sessão expirou, podemos tentar relogar como demo ou redirecionar
        console.warn('Sessão expirada. Tentando autenticação automática de demonstração...');
        await this.autoLoginDemo();
        // Tentar novamente com novo token
        headers['Authorization'] = `Bearer ${this.token}`;
        const retryRes = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        if (!retryRes.ok) throw new Error(`Erro ${retryRes.status}: Falha na requisição`);
        return await retryRes.json();
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const msg = errorData.detail || `Erro HTTP ${response.status}`;
        throw new Error(msg);
      }

      // Se for download ou sem conteúdo
      if (response.status === 204) return null;
      return await response.json();
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  }

  async autoLoginDemo() {
    try {
      const data = await this.login('admin', 'Iprev@2021');
      return data;
    } catch (e) {
      console.warn('Login automático demo não executado ou aguardando ação do usuário:', e);
    }
  }


  // --- AUTENTICAÇÃO ---
  async login(username, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setSession(res.access_token, res.user);
    return res;
  }

  async getMe() {
    return await this.request('/auth/me');
  }

  async getAPIKeys() {
    return await this.request('/auth/api-keys');
  }

  async createAPIKey(payload) {
    return await this.request('/auth/api-keys', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getUsers() {
    return await this.request('/auth/users');
  }

  // --- ATIVOS (VEÍCULOS E MOTORISTAS) ---
  async getVehicles(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return await this.request(`/assets/veiculos${qs ? '?' + qs : ''}`);
  }

  async createVehicle(payload) {
    return await this.request('/assets/veiculos', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async autoCadastroIoT(payload) {
    return await this.request('/assets/veiculos/autocadastro-iot', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getDispositivosDescobertosIoT() {
    return await this.request('/assets/iot/dispositivos-descobertos');
  }

  async getDrivers() {
    return await this.request('/assets/motoristas');
  }

  async createDriver(payload) {
    return await this.request('/assets/motoristas', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- TELEMETRIA & RASTREAMENTO ---
  async getTelemetryLive() {
    return await this.request('/telemetry/live');
  }

  async getTelemetryHistory(placa) {
    return await this.request(`/telemetry/history/${placa}`);
  }

  async getTelemetryEvents(placa = '') {
    return await this.request(`/telemetry/events${placa ? '?placa=' + placa : ''}`);
  }

  async getGeofences() {
    return await this.request('/telemetry/geofences');
  }

  async simulateFleetStep() {
    return await this.request('/telemetry/simulate-step', { method: 'POST' });
  }

  // --- ABASTECIMENTO & POSTOS ---
  async getFuelTransactions(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return await this.request(`/fuel/transactions${qs ? '?' + qs : ''}`);
  }

  async createFuelTransaction(payload) {
    return await this.request('/fuel/transactions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getFuelStations() {
    return await this.request('/fuel/stations');
  }

  async createFuelStation(payload) {
    return await this.request('/fuel/stations', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getTolls() {
    return await this.request('/fuel/tolls');
  }

  // --- MANUTENÇÃO & OFICINAS ---
  async getMaintenanceOS(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return await this.request(`/maintenance/os${qs ? '?' + qs : ''}`);
  }

  async createMaintenanceOS(payload) {
    return await this.request('/maintenance/os', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateOSStatus(osId, status) {
    return await this.request(`/maintenance/os/${osId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ novo_status: status }),
    });
  }

  async getWorkshops() {
    return await this.request('/maintenance/workshops');
  }

  async createWorkshop(payload) {
    return await this.request('/maintenance/workshops', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getVehicleHistory(placa) {
    return await this.request(`/maintenance/history/${placa}`);
  }

  async getTires(placa = '') {
    return await this.request(`/maintenance/tires${placa ? '?placa=' + placa : ''}`);
  }

  async getPreventiveAlerts() {
    return await this.request('/maintenance/alerts');
  }

  // --- VIAGENS & CHECKLIST ---
  async getTrips(status = '') {
    return await this.request(`/trips${status ? '?status=' + status : ''}`);
  }

  async createTrip(payload) {
    return await this.request('/trips', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async dispatchTrip(tripId) {
    return await this.request(`/trips/${tripId}/dispatch`, { method: 'POST' });
  }

  async finishTrip(tripId) {
    return await this.request(`/trips/${tripId}/finish`, { method: 'POST' });
  }

  async getChecklists(placa = '') {
    return await this.request(`/trips/checklists${placa ? '?placa=' + placa : ''}`);
  }

  async createChecklist(payload) {
    return await this.request('/trips/checklists', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- COMPLIANCE & MULTAS ---
  async getFines(placa = '') {
    return await this.request(`/compliance/fines${placa ? '?placa=' + placa : ''}`);
  }

  async indicateFineDriver(fineId, payload) {
    return await this.request(`/compliance/fines/${fineId}/indicar`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getExpirations() {
    return await this.request('/compliance/expirations');
  }

  // --- RELATÓRIOS & INTELIGÊNCIA ---
  async getDashboardKPIs() {
    return await this.request('/reports/dashboard');
  }

  async getTCOReport() {
    return await this.request('/reports/tco');
  }

  async getDriverRanking() {
    return await this.request('/reports/driver-ranking');
  }

  async getSecretariaReport(params = {}) {
    let query = '';
    if (typeof params === 'string') {
      query = params ? `?secretaria=${params}` : '';
    } else {
      const q = new URLSearchParams();
      if (params.secretaria) q.append('secretaria', params.secretaria);
      if (params.mes) q.append('mes', params.mes);
      if (params.ano) q.append('ano', params.ano);
      if (params.data_inicio) q.append('data_inicio', params.data_inicio);
      if (params.data_fim) q.append('data_fim', params.data_fim);
      query = q.toString() ? `?${q.toString()}` : '';
    }
    return await this.request(`/reports/secretarias${query}`);
  }

  async getExtratoLancamentos(params = {}) {
    const q = new URLSearchParams();
    if (params.mes) q.append('mes', params.mes);
    if (params.ano) q.append('ano', params.ano);
    if (params.data_inicio) q.append('data_inicio', params.data_inicio);
    if (params.data_fim) q.append('data_fim', params.data_fim);
    if (params.tipo) q.append('tipo', params.tipo);
    if (params.secretaria) q.append('secretaria', params.secretaria);
    const query = q.toString() ? `?${q.toString()}` : '';
    return await this.request(`/reports/lancamentos${query}`);
  }

  async getNationalCompliance() {
    return await this.request('/reports/compliance-national');
  }


  // --- INTELIGÊNCIA PRESCRITIVA AVANÇADA 360° ---
  async getPrescriptiveFull() {
    return await this.request('/reports/prescriptive/full');
  }

  // --- INTELIGÊNCIA ARTIFICIAL & COPILOT OPERACIONAL ---
  async chatAI(pergunta) {
    return await this.request('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ pergunta }),
    });
  }

  async getAISugestoes() {
    return await this.request('/ai/sugestoes');
  }

  async diagnosticarVeiculoAI(payload) {
    return await this.request('/ai/diagnostico-veiculo', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async auditarAbastecimentoAI(payload) {
    return await this.request('/ai/auditar-abastecimento', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- GOVERNO SC & QUALIDADE ISO 25010 ---
  async getContractSCSummary() {
    return await this.request('/contract-sc/summary');
  }

  async getContractSCCards(params = '') {
    return await this.request(`/contract-sc/cards${params ? '?' + params : ''}`);
  }

  async createContractSCCard(payload) {
    return await this.request('/contract-sc/cards', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateCardStatus(cardId, status, motivo = '') {
    return await this.request(`/contract-sc/cards/${cardId}/status?novo_status=${status}${motivo ? '&motivo=' + encodeURIComponent(motivo) : ''}`, {
      method: 'PATCH',
    });
  }

  async rechargeCardQuota(cardId, novoSaldo) {
    return await this.request(`/contract-sc/cards/${cardId}/recharge?novo_saldo=${novoSaldo}`, {
      method: 'POST',
    });
  }

  async authorizeCardTransaction(payload) {
    return await this.request('/contract-sc/transactions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getContractSCTransactions(params = '') {
    return await this.request(`/contract-sc/transactions${params ? '?' + params : ''}`);
  }

  async getISO25010Compliance() {
    return await this.request('/compliance/iso-25010');
  }
}

const api = new FleetAPI();



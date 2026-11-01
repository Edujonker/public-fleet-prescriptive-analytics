# Manual do Sistema - FrotaSaaS Enterprise 2.0
## Sistema Integrado de Gestão de Frotas, Telemetria IoT e Inteligência Operacional

---

### 1. Visão Geral e Arquitetura do Sistema

O **FrotaSaaS Enterprise** é uma plataforma corporativa desenvolvida para gestão completa do ciclo de vida de frotas públicas e privadas. O sistema integra hardware embarcado (rastreadores GPS, telemetria OBD2/CANbus e câmeras de fadiga), rotinas operacionais (abastecimento, manutenção e despacho) e auditoria de compliance (prazos do CTB, DETRAN, CONTRAN e LGPD).

```
                      ARQUITETURA TÉCNICA DO SISTEMA
                      
 [Rastreadores / IoT / CANbus]               [Navegador Web / Mobile PWA]
             │                                            │
             │ (HTTP / Header X-API-Key)                  │ (HTTP / JWT Bearer)
             ▼                                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND ENGINE (Porta 8090)                  │
│                                                                        │
│ • Security Middlewares (OWASP Headers, Rate Limit, Upload Shield)      │
│ • Autenticação Híbrida: JWT (Argon2id) + Chaves de API IoT (SHA-256)   │
│ • RBAC: ADMIN, GESTOR_FROTA, OPERADOR, MOTORISTA, AUDITOR             │
│ • Módulos de Negócio: Ativos, Telemetria, Abastecimento, OS, Multas    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│              CAMADA DE DADOS MONGODB RESILIENTE (DUAL ENGINE)          │
│                                                                        │
│  [Opção 1: MongoDB Server / Atlas]   OU   [Opção 2: Mongita Disk Local] │
│  (Configurado via MONGODB_URI)            (100% autônomo, zero setup)   │
│                                                                        │
│  Armazenamento Documental com Soberania de Dados em Território Nacional │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Especificações Técnicas e Requisitos Mínimos

* **Sistemas Operacionais Suportados**: Linux (Ubuntu, Debian, Fedora, CentOS, Arch) e Windows (10, 11 e Windows Server).
* **Linguagens e Frameworks**: Python 3.10+ (FastAPI, Pydantic v2, Uvicorn, Argon2-cffi) e JavaScript Moderno (Vanilla ES6+, HTML5, CSS3, Leaflet.js).
* **Banco de Dados**: MongoDB 5.0+ ou Motor Mongita embutido em disco (`dados/mongodb_data`).
* **Portas de Rede**:
  * **Porta 8090**: Sistema de Gestão de Frotas & Telemetria IoT (`http://localhost:8090`)
  * **Porta 8080**: Dashboard de Inteligência Preditiva e Prescritiva da Dissertação (`http://localhost:8080/dashboard/`)

---

### 3. Como Executar o Sistema

O sistema foi concebido para execução imediata em qualquer ambiente sem necessidade de instalar dependências de banco de dados externas.

#### 3.1 Execução no Linux / macOS
Abra o terminal na pasta raiz e execute:
```bash
./sistema_gestao_frotas/iniciar_linux.sh
```
Ou diretamente via Python:
```bash
python3 sistema_gestao_frotas/executar_sistema.py
```

#### 3.2 Execução no Windows
Dê um duplo clique no arquivo:
```cmd
sistema_gestao_frotas\iniciar_windows.bat
```
Ou no Prompt de Comando / PowerShell:
```cmd
python sistema_gestao_frotas\executar_sistema.py
```

#### 3.3 Execução dos Dois Sistemas em Paralelo (Porta 8080 e 8090)
Para iniciar conjuntamente o **Sistema de Frotas (8090)** e o **Dashboard da Dissertação (8080)**:
```bash
python3 executar_ambos_sistemas.py
```

---

### 4. Credenciais de Acesso e Perfis de Usuário (RBAC)

O sistema possui controle de acesso rigoroso baseado em papéis (Role-Based Access Control):

| Usuário | Senha Padrão | Perfil (Role) | Permissões e Escopo |
| :--- | :--- | :--- | :--- |
| **`admin`** | `Admin@Fleet2026!` | **ADMIN** | Controle total, gestão de usuários, emissão de API Keys e auditoria. |
| **`gestor`** | `Gestor@Fleet2026!` | **GESTOR_FROTA** | Aprovação de manutenções, indicação de condutor DETRAN e relatórios. |
| **`operador`** | `Operador@Fleet2026!` | **OPERADOR** | Despacho de viagens, registro de abastecimentos e abertura de OS. |
| **`motorista`** | `Motorista@Fleet2026!` | **MOTORISTA** | Execução de checklists digitais pré/pós-viagem e consulta de viagens. |

#### Chave de API Padrão para Rastreadores IoT
* **Cabeçalho HTTP**: `X-API-Key: flt_gateway_iot_live_sim_2026_seckey`
* **Finalidade**: Ingestão de telemetria e coordenadas GPS sem necessidade de login interativo.

---

### 5. Guia Operacional dos Módulos

#### 5.1 Painel Executivo & Indicadores (Dashboard)
* **Objetivo**: Fornecer visão panorâmica em tempo real da disponibilidade, custos acumulados e alertas críticos.
* **Métricas Principais**:
  * Total de Ativos, Veículos em Trânsito, Disponíveis no Pátio e em Manutenção.
  * Custo total do mês ($R\$$) consolidando combustível, peças, mão de obra e pedágios.
  * Consumo médio geral da frota ($km/L$).
  * Score médio de segurança e condução econômica.
* **Filtro Multi-Secretaria**: Permite isolar os indicadores por órgão (Saúde, Educação, Obras, Segurança, Administração).

#### 5.2 Rastreamento & Telemetria em Tempo Real
* **Mapa Interativo (Leaflet.js)**:
  * Marcadores com atualização dinâmica: Verde (Em trânsito > 5 km/h), Amarelo (Ligado/Marcha lenta), Azul (Estacionado).
  * Traçado de Histórico de Rota: clique no veículo e selecione "Traçar Histórico de Rota" para desenhar a rota percorrida.
  * Cercas Eletrônicas (Geofencing): visualização de zonas permitidas (Centros de Distribuição e Portos) e zonas proibidas (restrição de pesados).
* **Simulador de Tráfego**: Clique no botão superior `🛰️ Simular Telemetria em Trânsito` para emitir pings GPS automáticos ao longo de rodovias.

#### 5.3 Gestão de Abastecimento & Auditoria Antifraude
* **Registro de Abastecimento**:
  * Hodômetro verificado a cada evento.
  * Identificação do condutor e cartão de frota (Ticket Log, Alelo, VR Auto, etc.).
  * Coordenadas GPS do posto no momento da transação.
  * Cálculo automático de autonomia em $km/L$ e $L/km$.
* **Detecção Automática de Fraudes**:
  * Volume abastecido maior que a capacidade física do tanque do veículo.
  * Consumo atípico (inconsistência de odômetro retrocedido ou autonomia fora do padrão).
* **Postos Fornecedores Credenciados**: Cadastro mestre com CNPJ, bandeira, cidade/UF e geolocalização.

#### 5.4 Manutenção Preventiva, Corretiva & Gestão de Pneus
* **Planos de Revisão Preventiva**: Alertas automáticos por quilometragem atingida (ex: 10.000 km, 20.000 km) ou tempo decorrido.
* **Ordens de Serviço (OS)**:
  * Abertura com vinculação de oficina credenciada.
  * Detalhamento de peças com código, quantidade e valor unitário.
  * Detalhamento de serviços com horas e taxa de mão de obra.
  * Trava de status: ao abrir uma OS, o veículo é marcado automaticamente como `MANUTENCAO`. Ao concluir, retorna a `DISPONIVEL`.
* **Gestão Técnica de Pneus (Resolução CONTRAN)**:
  * Controle individual pelo "número de fogo".
  * Medição de sulco em milímetros: alerta imediato de **`CRÍTICO CONTRAN`** caso o sulco seja inferior a **1.6 mm** (risco legal e de segurança).
  * Histórico de recapagens e controle de rodízio.

#### 5.5 Viagens, Despacho & Checklist Digital
* **Solicitação de Viagem**: Vinculação a centro de custo/secretaria, origem, destino, distância estimada e ETA.
* **Trava de Segurança Operacional**:
  * É **obrigatório** registrar a vistoria do Checklist Digital de Pré-Viagem antes do despacho.
  * Caso qualquer item crítico (freios, faróis, pneus, direção) esteja não-conforme, o sistema aplica o status **`REPROVADO_IMPEDIDO`** e **bloqueia o despacho** do veículo.

#### 5.6 Compliance, Multas & Prazos Legais (CTB / DETRAN)
* **Gestão de Autuações**: Registro de multas com auto de infração, enquadramento, pontuação e data limite legal de indicação de condutor.
* **Workflow de Indicação de Condutor Infrator**:
  * Valida se o prazo legal do CTB não expirou.
  * Vincula os pontos diretamente ao prontuário da CNH do motorista infrator.
  * Emite protocolo oficial de homologação DETRAN (ex: `DETRAN-IND-20261030-XXXX`).
* **Vencimento de Documentos**: Alertas com 30, 15 e 7 dias para IPVA, Licenciamento Anual, seguro obrigatório e exame toxicológico periódico dos motoristas (categorias C, D e E).

#### 5.7 Inteligência Analítica, Relatórios & TCO
* **Relatório Consolidado por Secretaria**: Comparativo de custos de combustível, manutenção, pedágios, custo por km ($R\$/km$) e consumo médio agrupado por órgão.
* **Total Cost of Ownership (TCO) & CPK**: Cálculo exato de custo operacional por quilômetro rodado de cada ativo da frota.
* **Ranking de Segurança dos Motoristas**: Score de 0 a 100 baseado em frenagens bruscas, acelerações, excesso de RPM, velocidade e multas.
* **Exportação**:
  * **Download CSV**: Arquivo estruturado compatível com Excel e ERPs públicos.
  * **Impressão / PDF**: Formatação limpa para emissão de relatórios oficiais.

#### 5.8 Segurança & Chaves de API IoT
* **Geração de Chaves de API (`flt_...`)**: Criação de credenciais de alta entropia para rastreadores com armazenamento estrito em hash SHA-256.
* **Compatibilidade PWA**: Layout mobile-first responsivo permitindo acesso em smartphones Android e iOS sem necessidade de instalação via app store.

---

### 6. Conformidade e Soberania de Dados (LGPD)

Em estrita conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018):
1. **Armazenamento em Território Nacional**: Os dados operacionais e de condutores residem em infraestrutura soberana no Brasil (instância local autônoma ou datacenter nacional).
2. **Criptografia de Credenciais**: Senhas armazenadas com Argon2id (RFC 9106) e chaves de API com HMAC-SHA256.
3. **Trilha de Auditoria**: Registros com data, hora UTC e autoria para qualquer alteração cadastral ou movimentação financeira.

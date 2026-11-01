# Manual Técnico de Arquitetura, Mapeamento de Processos, Banco de Dados & API
## Plataforma FrotaSaaS Enterprise 2.0 & Telemetria IoT (Porta 8090)

---

### 1. Visão Geral do Ecossistema e Mapa Mental

O ecossistema **FrotaSaaS Enterprise 2.0** foi projetado para atender aos mais rigorosos padrões de segurança, resiliência operacional e prescrição analítica em frotas públicas e corporativas. O mapa mental abaixo sintetiza as conexões estruturais entre hardware embarcado, barramento de APIs, regras de negócio e tomada de decisão:

```mermaid
mindmap
  root((🚛 FrotaSaaS Enterprise 2.0))
    Módulos Funcionais
      1. Cadastro e Gestão de Ativos
        Veículos :: Placa Mercosul, Chassi, Renavam, Tanque, Odômetro
        Motoristas :: CNH, Exame Toxicológico, RFID, Score Condução
        Equipamentos IoT :: Rastreadores 4G, CANBus, Sensores, Câmera Fadiga
        Gestão de Pneus :: Matrícula/Fogo, Sulco mm, Resolução CONTRAN 1.6mm
      2. Viagens, Despacho e Checklist
        Solicitação de Viagens :: Origem, Destino, Centro de Custo, ETA
        Checklist Digital :: Vistoria Pré/Pós Viagem Obrigatória
        Trava de Segurança :: Bloqueio Automático em REPROVADO_IMPEDIDO
        Controle de Pátio :: Transições DISPONIVEL / EM_VIAGEM / MANUTENCAO
      3. Telemetria e Monitoramento IoT
        Ingestão M2M :: Pings Contínuos (Lat, Lng, Vel, RPM, Ignição, Odômetro)
        Motor de Geofencing :: Cercas Eletrônicas Circulares e Poligonais
        Condução Agressiva :: Detecção de Frenagem, Curva e Excesso Vel/RPM
        Score do Condutor :: Algoritmo Dinâmico de 0 a 100 pontos
      4. Abastecimento e Antifraude
        Transação de Combustível :: Litros, Preço/L, Valor Total, Cartão
        Auditoria Antifraude Tridimensional :: Volume > Tanque, Odômetro, Preço ANP
        Eficiência Energética :: Cálculo Automático de km/L e L/km
        Rede Credenciada :: Postos Homologados com Geolocalização
        Gestão de Pedágios :: Concessionárias e Integração com TAGs
      5. Manutenção e Gestão de OS
        Ordens de Serviço :: Peças, Mão de Obra, Oficinas Credenciadas
        Auditoria de Orçamentos :: Razão MO/Peça e Glosas Preventivas
        Planos Preventivos :: Revisão por Intervalo de Km e Dias
        Ciclo de Vida da OS :: ABERTA / EM_ANDAMENTO / CONCLUIDA
      6. Compliance, Multas e DETRAN
        Gestão de Autuações :: Notificações, Pontos, Prazos Legais CTB
        Workflow DETRAN :: Indicação de Condutor com Emissão de Protocolo
        Sinistros e Seguradoras :: Apólices e Estimativas de Danos
        Vencimentos :: IPVA, Licenciamento e Exame Toxicológico
      7. Inteligência Analítica e Prescrição 360°
        Manutenção Dinâmica :: Agendamento Inteligente e Falhas 48h
        Eficiência de Combustível :: Intervenção em Marcha Lenta e Postos em Rota
        Reroteamento Logístico :: Desvios em Tempo Real e Redimensionamento
        Segurança e Fadiga :: Escala com Trava Legal (Lei 13.103/2015)
        TCO e Desinvestimento :: Ponto Ótimo de Alienação (>40% Valor Venal)
        Matriz Tripartida :: Manutenção + Patrimônio + Combustíveis
    Segurança e Arquitetura
      Autenticação Híbrida
        JWT Bearer Token :: Usuários Humanos via Hash Argon2id
        Chaves de API M2M :: Dispositivos IoT via Hash SHA-256 (X-API-Key)
      Controle de Acesso RBAC
        ADMIN :: Controle Irrestrito e Gestão de Chaves
        GESTOR_FROTA :: Manutenção, Aprovações, Multas e Despacho
        OPERADOR :: Lançamento de Abastecimentos, OS e Viagens
        MOTORISTA :: Vistoria de Checklist e Consultas Pessoais
        AUDITOR :: Fiscalização, Trilha Imutável e Relatórios
      Defesa em Profundidade
        Validação Pydantic v2 :: Tipos Estritos e Sanitização RFC 7807
        Proteção DoS :: Payload Shield com Limite de 10 MB
        Headers OWASP :: CSP, HSTS, X-Content-Type-Options, X-Frame-Options
        Soberania de Dados :: Armazenamento Exclusivo em Solo Nacional
    Persistência de Dados
      Dual Engine Resiliente
        MongoDB Server :: Ambientes Corporativos de Produção / Cluster Atlas
        Mongita Disk :: Motor Embutido de Alta Performance Zero-Setup
      21 Coleções NoSQL
        Ativos :: veiculos, motoristas, equipamentos
        Telemetria :: telemetria_pings, posicoes_instantaneas, cercas, eventos
        Custos :: abastecimentos, postos_credenciados, pedagios
        Oficina :: ordens_servico, planos_revisao, pneus, oficinas
        Operação :: viagens, checklists_digitais, multas, sinistros
        Segurança :: usuarios, chaves_api, documentos_vencimento
```

---

### 2. Mapeamento Aprofundado dos Processos e Fluxogramas por Módulo

Cada processo operacional do sistema foi mapeado formalmente com seus atores, validações de integridade, pontos de decisão e impactos no estado do banco de dados:

---

#### 2.1 Módulo 1: Gestão de Ativos, Cadastros e Pneus CONTRAN

##### Processo 1.1: Ciclo de Vida e Validação de Pneus (Resolução CONTRAN)
O controle de pneus monitora a espessura do sulco de borracha e determina compulsoriamente a transição de estado entre pneu novo, rodízio, recapagem e descarte:

```mermaid
flowchart TD
    Start([Início da Inspeção do Pneu]) --> Medicao[Técnico Mede Sulco com Profundímetro mm]
    Medicao --> Input[POST /api/maintenance/tires ou Atualização]
    Input --> Validar{Sulco Atual <= 1.6 mm?}
    
    Validar -- SIM --> BloqueioCONTRAN[Status: CRÍTICO<br>Alerta CONTRAN Compulsório]
    BloqueioCONTRAN --> AcaoCritica{Carcaça Suporta Recapagem?}
    AcaoCritica -- SIM --> EncaminhaRecap[Status: RECAPAR<br>Envio para Recapagem 1ª ou 2ª Vida]
    AcaoCritica -- NÃO --> Descarte[Status: DESCARTADO<br>Laudo Técnico de Inservibilidade]
    
    Validar -- NÃO --> ChecarSulco{Sulco entre 1.7 e 3.0 mm?}
    ChecarSulco -- SIM --> AlertaAtencao[Status: ATENÇÃO<br>Programar Rodízio / Pré-Recapagem]
    ChecarSulco -- NÃO --> Conforme[Status: BOM / NOVO<br>Pneu Liberado para Operação Normal]
    
    EncaminhaRecap --> Fim([Fim do Ciclo de Inspeção])
    Descarte --> Fim
    AlertaAtencao --> Fim
    Conforme --> Fim
```

---

#### 2.2 Módulo 2: Viagens, Despacho e Vistoria Digital com Trava de Segurança

##### Processo 2.1: Workflow de Despacho com Trava Preventiva
Nenhum veículo pode ser liberado no pátio sem que o checklist pré-viagem tenha sido preenchido e aprovado pelo motorista no aplicativo:

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Operador de Logística
    actor Motorista as Motorista Escalado
    participant API as FastAPI Gateway
    participant TripService as Trip Service
    participant DB as Banco de Dados
    participant Veiculo as Estado do Veículo

    Operador->>API: POST /api/trips (Origem, Destino, Centro de Custo, Placa, Motorista)
    API->>TripService: Validar Disponibilidade do Veículo e Habilitação do Motorista
    TripService->>DB: Salvar Requisição (Status: SOLICITADA)
    API-->>Operador: Viagem Criada com Sucesso (ID, Código)

    Motorista->>API: POST /api/trips/checklists (Tipo: PRE_VIAGEM, Itens Inspecionados, Fotos)
    API->>TripService: Avaliar Itens Críticos (Freios, Pneus, Faróis, Direção)
    
    alt Algum Item Crítico Reprovado
        TripService->>DB: Checklist Status: REPROVADO_IMPEDIDO
        TripService->>Veiculo: Bloquear Veículo (Status: MANUTENCAO)
        API-->>Motorista: ALERTA CRÍTICO: Veículo Impedido de Trafegar!
        Operador->>API: POST /api/trips/{id}/dispatch
        API-->>Operador: HTTP 400 Bad Request: Despacho Bloqueado por Falha de Segurança!
    else Todos os Itens Conformes
        TripService->>DB: Checklist Status: APROVADO
        API-->>Motorista: Vistoria Conforme. Veículo Liberado.
        Operador->>API: POST /api/trips/{id}/dispatch
        TripService->>DB: Viagem Status: EM_ANDAMENTO
        TripService->>Veiculo: Veículo Status: EM_VIAGEM
        API-->>Operador: HTTP 200 OK: Viagem Despachada com Sucesso!
    end

    Note over Motorista,API: Execução da Rota Rodoviária com Telemetria Ativa...
    
    Motorista->>API: POST /api/trips/checklists (Tipo: POS_VIAGEM, Odômetro Final, Avarias)
    Operador->>API: POST /api/trips/{id}/finish
    TripService->>DB: Viagem Status: FINALIZADA
    TripService->>Veiculo: Veículo Status: DISPONIVEL (Liberado no Pátio)
    API-->>Operador: Viagem Concluída e Custos Integrados.
```

---

#### 2.3 Módulo 3: Telemetria IoT em Tempo Real e Detecção de Eventos

##### Processo 3.1: Ingestão de Telemetria, Geofencing e Cálculo de Score

```mermaid
flowchart TD
    IoT[Terminal Telemático GPS/CANbus] -->|POST /api/telemetry/ping<br>Header: X-API-Key| Gateway[FastAPI IoT Gateway]
    Gateway --> Auth{Validação SHA-256<br>da Chave de API}
    
    Auth -- Inválida --> Deny[HTTP 401 Unauthorized]
    Auth -- Válida --> Processar[Parse do Payload: Lat, Lng, Vel, RPM, Ignição, Odômetro]
    
    Processar --> GeoCheck{Verificar Cercas Eletrônicas<br>Polígono / Raio Circular}
    GeoCheck -- Fora de Cerca Permitida --> AlertaCerca[Gerar Alerta: VIOLACAO_GEOFENCE]
    GeoCheck -- Dentro de Área Proibida --> AlertaProibida[Gerar Alerta: ENTRADA_AREA_RESTRITA]
    GeoCheck -- Conforme --> ConducaoCheck
    
    AlertaCerca --> ConducaoCheck{Análise Telemática de Condução}
    AlertaProibida --> ConducaoCheck
    
    ConducaoCheck --> VelCheck{Velocidade > 110 km/h?}
    VelCheck -- SIM --> AlertaVel[Alerta: EXCESSO_VELOCIDADE]
    VelCheck -- NÃO --> RPMCheck
    
    AlertaVel --> RPMCheck{RPM > Limite Faixa Verde?}
    RPMCheck -- SIM --> AlertaRPM[Alerta: EXCESSO_RPM]
    RPMCheck -- NÃO --> AcelCheck
    
    AlertaRPM --> AcelCheck{Aceleração / Frenagem Brusca?}
    AcelCheck -- SIM --> AlertaFrenagem[Alerta: FRENAGEM_OU_CURVA_BRUSCA]
    AcelCheck -- NÃO --> SalvarPosicao
    
    AlertaFrenagem --> PenalizarScore[Penalizar Score de Condução do Condutor]
    PenalizarScore --> SalvarPosicao[Atualizar Posição Instantânea na Coleção posicoes_instantaneas]
    
    SalvarPosicao --> PersistirPing[Persistir Histórico em telemetria_pings]
    PersistirPing --> Response[HTTP 200 OK: Lista de Alertas Gerados]
```

---

#### 2.4 Módulo 4: Gestão de Combustíveis e Auditoria Antifraude Tridimensional

##### Processo 4.1: Triagem Antifraude em Abastecimento
O algoritmo de auditoria cruza o volume solicitado com a capacidade física cadastral do tanque do veículo e valida o histórico do hodômetro para estancar fraudes:

```mermaid
flowchart TD
    Req[POST /api/fuel/transactions<br>Placa, Litros, Valor/L, Odômetro, Posto] --> ConsultaVeiculo[Consultar Veículo no Banco de Dados]
    ConsultaVeiculo --> ValidaTanque{Litros > Capacidade Tanque * 1.05?}
    
    ValidaTanque -- SIM --> FraudeVolume[Flag Anomalia = TRUE<br>Motivo: CAPACIDADE_TANQUE_EXCEDIDA]
    ValidaTanque -- NÃO --> ConsultaUltimoAbast[Consultar Último Abastecimento do Veículo]
    
    FraudeVolume --> ConsultaUltimoAbast
    ConsultaUltimoAbast --> ValidaKm{Odômetro Atual <= Odômetro Anterior?}
    
    ValidaKm -- SIM --> FraudeKm[Flag Anomalia = TRUE<br>Motivo: ODOMETRO_INCONSISTENTE_RETROCEDIDO]
    ValidaKm -- NÃO --> CalcConsumo[Calcular Autonomia: km_rodado / litros]
    
    FraudeKm --> CalcConsumo
    CalcConsumo --> ValidaAutonomia{Consumo < 1.4 km/L ou > 28.0 km/L?}
    
    ValidaAutonomia -- SIM --> FraudeAutonomia[Flag Anomalia = TRUE<br>Motivo: AUTONOMIA_ATIPICA_FORA_DA_FAIXA]
    ValidaAutonomia -- NÃO --> Concluir
    
    FraudeAutonomia --> Concluir[Gravar Registro na Coleção abastecimentos]
    Concluir --> AtualizarOdometro[Se Odômetro Válido: Atualizar odometro_atual_km do Veículo]
    AtualizarOdometro --> Notificar{Anomalia Detectada?}
    
    Notificar -- SIM --> EnviarAuditoria[Notificar Gestor de Frota e Encaminhar para Glosa/Auditoria]
    Notificar -- NÃO --> Aprovado[Transação Homologada com Sucesso]
```

---

#### 2.5 Módulo 5: Manutenção, Gestão de OS e Auditoria de Peças

##### Processo 5.1: Ciclo de Vida da Ordem de Serviço (OS)

```mermaid
sequenceDiagram
    autonumber
    actor Gestor as Gestor de Manutenção
    actor Oficina as Oficina Credenciada
    participant API as FrotaSaaS Maintenance API
    participant Audit as Motor de Auditoria MO/Peças
    participant DB as Coleções de Manutenção

    Gestor->>API: POST /api/maintenance/os (Placa, Tipo: PREVENTIVA, Oficina, Previsão)
    API->>DB: Criar OS (Status: ABERTA)
    API-->>Gestor: OS Criada com Sucesso

    Oficina->>API: Lança Itens de Peças e Horas de Mão de Obra
    API->>Audit: Auditar Proposta Orçada
    Audit->>Audit: Calcular Razão MO / Peças
    
    alt Razão MO/Peças > 2.0x sem Justificativa
        Audit-->>API: Alerta: Desproporção Elevada de Mão de Obra!
        API->>DB: Registrar Flag de Auditoria / Glosa Parcial
    end

    Gestor->>API: Aprova Orçamento e Inicia Serviço
    API->>DB: Atualizar OS (Status: EM_ANDAMENTO)
    
    Note over Oficina,API: Execução física dos serviços mecânicos e substituição de peças...

    Oficina->>API: Notifica Conclusão do Serviço
    Gestor->>API: PATCH /api/maintenance/os/{id}/status (novo_status: CONCLUIDA)
    API->>DB: Atualizar OS para CONCLUIDA, Gravar Data de Conclusão
    API->>DB: Liberar Veículo no Pátio (Status: DISPONIVEL)
    API-->>Gestor: OS Liquidada e Histórico do Veículo Atualizado.
```

---

#### 2.6 Módulo 6: Compliance de Trânsito, Multas e Workflow DETRAN

##### Processo 6.1: Indicação de Condutor Infrator e Emissão de Protocolo DETRAN

```mermaid
flowchart TD
    Notificacao[Recebimento de Notificação de Infração CTB] --> CadastroMulta[POST /api/compliance/fines<br>Auto, Placa, Data/Hora, Local, Pontos, Valor]
    CadastroMulta --> ConsultaTelemetria[Consultar telemetria_pings e viagens no Instante da Infração]
    ConsultaTelemetria --> IdentificaMotorista{Condutor Localizado na Escala/GPS?}
    
    IdentificaMotorista -- SIM --> MotoristaConfirmado[Identificação Inequívoca do Condutor]
    IdentificaMotorista -- NÃO --> AlertaAuditoria[Alerta ao Gestor: Veículo em Uso sem Despacho Autorizado]
    
    MotoristaConfirmado --> SubmeterIndicacao[POST /api/compliance/fines/{id}/indicar<br>Motorista Identificador, Documento CNH]
    SubmeterIndicacao --> ValidaPrazo{Data Atual <= Limite Indicação?}
    
    ValidaPrazo -- NÃO --> MultaNIC[Inadmissível CTB: Risco de Multa NIC duplicada ao Órgão]
    ValidaPrazo -- SIM --> EmiteProtocolo[Gerar Protocolo Oficial: DETRAN-IND-YYYYMMDD-XXXXXX]
    
    EmiteProtocolo --> AtualizaMulta[Atualizar Multa: Status INDICADO_AGUARDANDO_DETRAN]
    AtualizaMulta --> AtualizaMotorista[Lançar Pontuação Provisória na CNH do Motorista]
    AtualizaMotorista --> FimMulta([Workflow Homologado e Arquivado])
```

---

#### 2.7 Módulo 7: Inteligência Prescritiva 360° e Tomada de Decisão

##### Processo 7.1: Orquestração dos 5 Pilares Prescritivos

```mermaid
flowchart LR
    subgraph Ingestao [Ingestão de Dados em Tempo Real]
        D1[(Telemetria IoT)]
        D2[(Manutenção OS)]
        D3[(Abastecimento)]
        D4[(Patrimônio SEA)]
    end

    subgraph Motores [Motores Analíticos e Prescritivos]
        P1[1. Manutenção Preventiva Dinâmica & Falhas 48h]
        P2[2. Eficiência Energética & Rota de Abastecimento]
        P3[3. Reroteamento Logístico & Dimensionamento]
        P4[4. Treinamento Sob Medida & Escala Anti-Fadiga]
        P5[5. TCO & Momento Ideal de Desinvestimento Leilão]
    end

    subgraph Acoes [Ações Prescritivas Operacionais]
        A1[Recomendar Parada Terça 14h / Trocar Válvula em 48h]
        A2[Alerta Marcha Lenta > 5 min / Abastecer Posto Rota R$ 5,89]
        A3[Desvio de Tráfego / Transferir 3 Viaturas Ociosas]
        A4[Bloqueio Motorista < 11h Repouso Lei 13.103/2015]
        A5[Alienação Compulsória Leilão Decreto 47.539/2018]
    end

    Ingestao --> Motores
    Motores --> Acoes
```

---

### 3. Detalhamento Completo do Banco de Dados

O sistema opera sobre uma arquitetura NoSQL Documental estruturada no **MongoDB / Mongita**, combinada com um banco analítico relacional **SQLite** (`dados/resultados_dissertacao.db`) para suporte aos modelos econométricos e prescrittivos da dissertação.

#### 3.1 Diagrama Entidade-Relacionamento do Banco de Dados (ERD)

```mermaid
erDiagram
    usuarios ||--o{ chaves_api : emite
    veiculos ||--o{ equipamentos : equipa
    veiculos ||--o{ telemetria_pings : gera
    veiculos ||--|| posicoes_instantaneas : reflete
    veiculos ||--o{ ordens_servico : sofre
    veiculos ||--o{ pneus : calca
    veiculos ||--o{ abastecimentos : consome
    veiculos ||--o{ pedagios : tarifa
    veiculos ||--o{ viagens : transporta
    veiculos ||--o{ multas : recebe
    veiculos ||--o{ sinistros : colide
    
    motoristas ||--o{ viagens : conduz
    motoristas ||--o{ checklists_digitais : vistoria
    motoristas ||--o{ multas : pontua
    motoristas ||--o{ abastecimentos : registra
    
    viagens ||--o{ checklists_digitais : condiciona
    oficinas_credenciadas ||--o{ ordens_servico : realiza
    postos_credenciados ||--o{ abastecimentos : abastece
    planos_revisao ||--o{ ordens_servico : parametriza
```

#### 3.2 Especificação Detalhada das 21 Coleções do FrotaSaaS

| Coleção | Finalidade Principal | Chave Primária | Índices Críticos | Relacionamentos Principais |
| :--- | :--- | :--- | :--- | :--- |
| `usuarios` | Contas de acesso e RBAC | `_id` (ObjectId) | `username` (unique), `email` | `chaves_api.usuario_id` |
| `chaves_api` | Tokens M2M para IoT e ERPs | `_id` (ObjectId) | `hashed_key` (unique, SHA-256) | - |
| `veiculos` | Cadastro mestre de ativos da frota | `_id` (ObjectId) | `placa` (unique), `chassi` (unique) | `abastecimentos`, `ordens_servico`, `viagens` |
| `motoristas` | Condutores, CNH e Exame Toxicológico | `_id` (ObjectId) | `cpf` (unique), `cnh_numero` (unique) | `viagens`, `multas`, `checklists_digitais` |
| `equipamentos` | Rastreadores GPS, CANbus e câmeras | `_id` (ObjectId) | `identificador_serial` (unique) | `veiculos.placa` |
| `pneus` | Ciclo de vida e sulcagem CONTRAN 1.6mm | `_id` (ObjectId) | `numero_fogo` (unique) | `veiculos.placa` |
| `viagens` | Requisições e despacho de rotas | `_id` (ObjectId) | `codigo_viagem` (unique), `status` | `veiculos.placa`, `motoristas.id` |
| `checklists_digitais` | Vistorias pré e pós-viagem com travas | `_id` (ObjectId) | `viagem_id`, `veiculo_placa` | `viagens.id` |
| `telemetria_pings` | Histórico imutável de pacotes GPS IoT | `_id` (ObjectId) | `veiculo_placa`, `recebido_em` | `veiculos.placa` |
| `posicoes_instantaneas` | Última posição em tempo real no mapa | `_id` (ObjectId) | `veiculo_placa` (unique) | `veiculos.placa` |
| `cercas_eletronicas` | Geofencing circular e poligonal | `_id` (ObjectId) | `nome`, `ativo` | `veiculos.placa` |
| `eventos_conducao` | Frenagem, aceleração e excesso vel. | `_id` (ObjectId) | `veiculo_placa`, `timestamp` | `veiculos.placa`, `motoristas.id` |
| `abastecimentos` | Transações de combustível e antifraude | `_id` (ObjectId) | `veiculo_placa`, `odometro_km` | `veiculos.placa`, `postos_credenciados` |
| `postos_credenciados`| Postos homologados e preços ANP | `_id` (ObjectId) | `cnpj` (unique), `cidade` | `abastecimentos` |
| `pedagios` | Passagens em praças e débito de TAGs | `_id` (ObjectId) | `veiculo_placa`, `data_hora` | `veiculos.placa` |
| `ordens_servico` | Manutenção, peças e horas de MO | `_id` (ObjectId) | `id`, `veiculo_placa`, `status` | `veiculos.placa`, `oficinas_credenciadas` |
| `oficinas_credenciadas`| Oficinas mecânicas homologadas | `_id` (ObjectId) | `cnpj` (unique) | `ordens_servico` |
| `planos_revisao` | Intervalos preventivos (km/tempo) | `_id` (ObjectId) | `categoria_veiculo` | `ordens_servico` |
| `multas` | Autuações de trânsito e protocolo DETRAN | `_id` (ObjectId) | `auto_infracao` (unique) | `veiculos.placa`, `motoristas.id` |
| `sinistros` | Ocorrências, colisões e seguradoras | `_id` (ObjectId) | `numero_sinistro` | `veiculos.placa` |
| `documentos_vencimento`| Controle de IPVA, Licenciamento e Taxas| `_id` (ObjectId) | `veiculo_placa`, `tipo_documento` | `veiculos.placa` |

#### 3.3 Tabelas do Banco de Dados Analítico SQLite (`resultados_dissertacao.db`)

Para suportar o cruzamento tripartido da dissertação (**Manutenção + Patrimônio + Combustíveis**), o SQLite estrutura tabelas de alta volumetria:

* **`veiculos_frota_consolidada` (17.252 registros):** Cruza placa, marca, modelo, categoria, órgão, valor venal SEA, custo acumulado de manutenção, custo acumulado de combustível, razão gasto/venal e flag de elegibilidade para leilão (`razao_gasto_venal >= 0.40`).
* **`abastecimentos` (1.000.000 registros):** Histórico completo de 1 milhão de abastecimentos com flags auditadas (`flag_anomalia_volume`, `flag_anomalia_kml`, `flag_preco_discrepante`).
* **`manutencao_itens` (223.819 registros):** Todos os itens individuais de peças e serviços extraídos da base bruta estadual.
* **`veiculos_leilao` (30 veículos críticos):** Top veículos com manutenção estourada (>40% a 300% do valor venal) sujeitos a alienação imediata conforme Decreto 47.539/2018.

---

### 4. Especificação Completa da API RESTful

A API do **FrotaSaaS Enterprise 2.0** opera sob os padrões OpenAPI 3.0 / Swagger, oferecendo documentação interativa em `http://localhost:8090/docs` e especificação JSON em `http://localhost:8090/openapi.json`.

#### 4.1 Catálogo Exaustivo de Endpoints

| Método | Endpoint | Autenticação Requerida | Papéis Autorizados (RBAC) | Descrição e Finalidade |
| :---: | :--- | :--- | :--- | :--- |
| **GET** | `/api/health` | Pública | Todos | Verificação de status e saúde da API e banco de dados |
| **POST** | `/api/auth/login` | Pública | Todos | Login com credenciais e emissão de JWT Bearer (Argon2id) |
| **GET** | `/api/auth/me` | JWT Bearer | Todos os usuários logados | Retorna dados do perfil do usuário autenticado |
| **POST** | `/api/auth/api-keys` | JWT Bearer | `ADMIN` | Emissão de chave de API para IoT / M2M (X-API-Key) |
| **GET** | `/api/auth/api-keys` | JWT Bearer | `ADMIN` | Lista todas as chaves de API ativas e seus prefixos |
| **DELETE**| `/api/auth/api-keys/{id}` | JWT Bearer | `ADMIN` | Revogação imediata de chave de API M2M |
| **GET** | `/api/assets/veiculos` | Pública / JWT | Todos | Lista veículos com filtros por categoria, status ou busca |
| **POST** | `/api/assets/veiculos` | JWT Bearer | `ADMIN`, `GESTOR_FROTA` | Cadastro de novo veículo com validações de chassi e renavam |
| **GET** | `/api/assets/veiculos/{placa}` | Pública / JWT | Todos | Retorna ficha cadastral completa e odômetro do veículo |
| **PUT** | `/api/assets/veiculos/{placa}` | JWT Bearer | `ADMIN`, `GESTOR_FROTA` | Atualização cadastral ou de status do veículo |
| **GET** | `/api/assets/motoristas` | JWT Bearer | Todos | Lista condutores, categorias de CNH e validade toxicológica |
| **POST** | `/api/assets/motoristas` | JWT Bearer | `ADMIN`, `GESTOR_FROTA` | Cadastro de novo condutor com validações de CNH e CPF |
| **GET** | `/api/assets/motoristas/{id}` | JWT Bearer | Todos | Ficha completa do motorista e pontuação na CNH |
| **PUT** | `/api/assets/motoristas/{id}` | JWT Bearer | `ADMIN`, `GESTOR_FROTA` | Atualização de dados cadastrais ou renovação de CNH |
| **GET** | `/api/assets/equipamentos` | JWT Bearer | Todos | Lista rastreadores GPS, módulos CANBus e sensores |
| **POST** | `/api/assets/equipamentos` | JWT Bearer | `ADMIN`, `GESTOR_FROTA` | Cadastra equipamento embarcado vinculado a uma placa |
| **POST** | `/api/telemetry/ping` | `X-API-Key` ou JWT | `OPERADOR`, `ADMIN`, Dispositivos | Ingestão M2M de telemetria IoT em tempo real |
| **GET** | `/api/telemetry/live` | JWT Bearer | Todos | Retorna última posição geográfica de todos os veículos ativos |
| **GET** | `/api/telemetry/events` | JWT Bearer | Todos | Lista infrações de condução (velocidade, RPM, frenagem) |
| **GET** | `/api/telemetry/geofences` | JWT Bearer | Todos | Lista cercas eletrônicas cadastradas |
| **POST** | `/api/telemetry/geofences` | JWT Bearer | `ADMIN`, `GESTOR_FROTA` | Cria cerca eletrônica circular ou poligonal |
| **POST** | `/api/fuel/transactions` | JWT Bearer | `ADMIN`, `GESTOR_FROTA`, `OPERADOR` | Lança abastecimento com auditoria antifraude imediata |
| **GET** | `/api/fuel/transactions` | JWT Bearer | Todos | Consulta histórico de abastecimentos e flags de anomalia |
| **GET** | `/api/fuel/stations` | JWT Bearer | Todos | Lista postos credenciados conveniados e bandeiras |
| **POST** | `/api/fuel/toll` | JWT Bearer | `OPERADOR`, `GESTOR_FROTA`, `ADMIN` | Registra passagem em pedágio via tag eletrônica |
| **POST** | `/api/maintenance/tires` | JWT Bearer | `ADMIN`, `GESTOR_FROTA` | Cadastro de pneu com validação de sulco CONTRAN 1.6mm |
| **GET** | `/api/maintenance/tires` | JWT Bearer | Todos | Lista pneus da frota, quilometragem e status de desgaste |
| **GET** | `/api/maintenance/os` | JWT Bearer | Todos | Lista Ordens de Serviço com peças, serviços e oficinas |
| **POST** | `/api/maintenance/os` | JWT Bearer | `ADMIN`, `GESTOR_FROTA`, `OPERADOR` | Abre nova OS e vincula itens orçados de peças e MO |
| **PATCH**| `/api/maintenance/os/{id}/status`| JWT Bearer| `ADMIN`, `GESTOR_FROTA`, `OPERADOR` | Conclui OS e libera automaticamente o veículo no pátio |
| **GET** | `/api/trips` | JWT Bearer | Todos | Lista solicitações de viagem e rotas ativas |
| **POST** | `/api/trips` | JWT Bearer | `ADMIN`, `GESTOR_FROTA`, `OPERADOR` | Cria solicitação de viagem vinculada a um centro de custo |
| **POST** | `/api/trips/{id}/dispatch`| JWT Bearer | `ADMIN`, `GESTOR_FROTA`, `OPERADOR` | Despacha viagem (valida obrigatoriamente checklist aprovado) |
| **POST** | `/api/trips/{id}/finish` | JWT Bearer | `ADMIN`, `GESTOR_FROTA`, `OPERADOR`, `MOTORISTA` | Finaliza viagem e retorna veículo para DISPONIVEL |
| **POST** | `/api/trips/checklists` | JWT Bearer | `ADMIN`, `GESTOR_FROTA`, `OPERADOR`, `MOTORISTA` | Submete vistoria digital de pré ou pós-viagem |
| **GET** | `/api/compliance/fines` | JWT Bearer | Todos | Lista multas de trânsito e status da indicação do condutor |
| **POST** | `/api/compliance/fines` | JWT Bearer | `ADMIN`, `GESTOR_FROTA` | Registra notificação de autuação de trânsito |
| **POST** | `/api/compliance/fines/{id}/indicar`| JWT Bearer| `ADMIN`, `GESTOR_FROTA` | Executa workflow DETRAN e emite protocolo oficial |
| **GET** | `/api/reports/dashboard` | JWT Bearer | Todos | Retorna os principais KPIs da frota em tempo real |
| **GET** | `/api/reports/secretarias` | JWT Bearer | Todos | Consolidado de custos e consumos por secretaria |
| **GET** | `/api/reports/tco` | JWT Bearer | Todos | Relatório analítico de TCO e CPK (custo por km) |
| **GET** | `/api/reports/driver-ranking` | JWT Bearer | Todos | Ranking de segurança e score de motoristas (0 a 100) |
| **GET** | `/api/reports/export/csv` | JWT Bearer | Todos | Exportação RFC 4180 de custos de frota em formato CSV |
| **GET** | `/api/reports/compliance-national`| JWT Bearer| Todos | Auditoria de soberania nacional e residência de dados LGPD |
| **GET** | `/api/reports/prescriptive/full` | JWT Bearer | Todos | Relatório Prescritivo Master consolidado em 5 pilares |
| **GET** | `/api/reports/prescriptive/maintenance` | JWT Bearer | Todos | Prescrição de manutenção dinâmica e prevenção falhas 48h |
| **GET** | `/api/reports/prescriptive/fuel` | JWT Bearer | Todos | Ações de corte de marcha lenta e postos em rota de menor custo |
| **GET** | `/api/reports/prescriptive/logistics` | JWT Bearer | Todos | Redirecionamento em tempo real e taxa de ociosidade |
| **GET** | `/api/reports/prescriptive/drivers` | JWT Bearer | Todos | Treinamento sob medida e escala anti-fadiga (Lei 13.103/2015) |
| **GET** | `/api/reports/prescriptive/divestment-tco` | JWT Bearer | Todos | Análise TCO e recomendação de leilão (>40% valor venal) |

---

### 5. Documentos Complementares

* [MAPA_MENTAL_SISTEMA_FROTAS.pdf](file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934%20(1)/sistema_gestao_frotas/docs/MAPA_MENTAL_SISTEMA_FROTAS.pdf)
* [DICIONARIO_DE_DADOS.md](file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934%20(1)/sistema_gestao_frotas/docs/DICIONARIO_DE_DADOS.md)
* [GUIA_INTEGRACAO_API.md](file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934%20(1)/sistema_gestao_frotas/docs/GUIA_INTEGRACAO_API.md)
* [MANUAL_DO_SISTEMA.md](file:///home/eduardo-note/Documentos/Dissertação/Geral_de_OS_23439885_202609110934%20(1)/sistema_gestao_frotas/docs/MANUAL_DO_SISTEMA.md)

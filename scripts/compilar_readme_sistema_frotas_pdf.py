#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador do README Executivo e Técnico Completo do Sistema de Gestão de Frotas em PDF
Sistema de Gestão de Frotas & Telemetria IoT - FrotaSaaS Enterprise 2.0 (Porta 8090)
Autor: Eduardo Lopes Jonker (PPGCAP / UDESC)
Orientadora: Profa. Dra. Vivian Kremer Kalempa
Coorientador: Prof. Dr. Yuri Kaszubowski Lopes
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import weasyprint

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "sistema_gestao_frotas" / "docs"
PDF_DIR = BASE_DIR / "relatorios_pdf"
REL_ENGENHARIA_DIR = BASE_DIR / "relatorios" / "pdf" / "engenharia_e_sistema"
DOCS_GERAL_DIR = BASE_DIR / "Documentos"

for d in [DOCS_DIR, PDF_DIR, REL_ENGENHARIA_DIR, DOCS_GERAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

MD_CONTENT = """# Manual Técnico e Executivo Geral do Sistema de Gestão de Frotas & Telemetria IoT
## FrotaSaaS Enterprise 2.0 - Arquitetura, Módulos, Modelagem NoSQL e Catálogo de APIs
**Autor:** Eduardo Lopes Jonker  
**Programa:** Mestrado em Computação Aplicada (PPGCAP) - CCT / UDESC  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes  
**Data:** Outubro de 2026 | Versão 2.0-LTS  

---

## 1. Visão Geral e Proposta de Valor

O **FrotaSaaS Enterprise 2.0** é uma plataforma corporativa e governamental de alta disponibilidade desenvolvida para a gestão integral, auditoria contínua e otimização prescritiva de frotas públicas e privadas. 

Concebido no âmbito da pesquisa de mestrado do PPGCAP/UDESC, o sistema une técnicas de ponta em:
* **Engenharia de Software Resiliente**: Backend assíncrono em Python com FastAPI, dual-engine de persistência (MongoDB nativo ou Mongita embutido em disco zero-dependency), segurança baseada em princípios Zero-Trust e RBAC estrito.
* **Internet das Coisas (IoT) & Telemetria em Tempo Real**: Rastreamento satelital GPS, telemetria CANbus/OBD2, medição de velocidade, RPM, temperatura do motor, nível de combustível, hodômetro digital e cercas eletrônicas dinâmicas (geofencing).
* **Auditoria de Compliance e Segurança Veicular**: Checklist digital pré/pós-viagem com **trava eletrônica obrigatória** (bloqueio do veículo em caso de não conformidade de itens críticos de segurança CONTRAN) e validação de CNH/exame toxicológico junto a órgãos de trânsito.
* **Algoritmos Antifraude em Abastecimentos**: Detecção automatizada em tempo de execução de fraudes de combustível, incluindo hodômetro regredido, abastecimento que supera o volume nominal do tanque, discrepância excessiva de consumo ($km/L$) e abastecimentos fora de postos credenciados.
* **Ciclo de Vida de Manutenção (Work Orders)**: Controle total de Ordens de Serviço (preventivas, corretivas e preditivas), peças, mão de obra, cotações, SLA de oficinas credenciadas e apuração do Custo Total de Propriedade (TCO).
* **Analítica Prescritiva & Otimização Matemática**: Modelagem MILP (*Mixed-Integer Linear Programming*) para desativação e alienação de veículos antieconômicos, detecção de anomalias com *Isolation Forest* e projeção de despesas orçamentárias trienais com *Facebook Prophet*.

---

## 2. Arquitetura de Software e Pilha Tecnológica

### 2.1 Componentes e Camadas do Sistema

1. **Camada de Borda e IoT (Edge / Hardware)**:
   * Rastreadores GPS/GPRS, dongles OBD2/CANbus e coletores de dados móveis.
   * Comunicação via HTTP seguro com cabeçalho `X-API-Key: flt_gateway_iot_live_sim_2026_seckey`.
2. **Camada de API Backend (FastAPI Engine - Porta 8090)**:
   * Framework assíncrono moderno `FastAPI` (Python 3.10+ / 3.14).
   * Validação estrita de contratos de dados com `Pydantic v2`.
   * Criptografia de alta resistência: senhas com `Argon2id` e tokens de sessão com `JWT (JSON Web Tokens)` assinados com algoritmo HMAC-SHA256.
   * Middlewares de Proteção: Headers de segurança OWASP (Content-Security-Policy, HSTS, X-Frame-Options, X-Content-Type-Options), limitador de tamanho de upload (15MB) e proteção CORS configurável.
3. **Camada de Dados Dual-Engine (Persistência Resiliente)**:
   * **Engine 1 (Produção)**: Conexão nativa com instâncias MongoDB Server 5.0+ ou MongoDB Atlas na nuvem.
   * **Engine 2 (Autônomo Standalone)**: Motor embutido em disco `Mongita` armazenado no diretório `dados/mongodb_data`, permitindo execução 100% autônoma, sem necessidade de instalar daemons externos ou servidores adicionais.
4. **Camada de Apresentação (Frontend PWA & Dashboards)**:
   * Single-Page Application (SPA) em HTML5 semântico, Vanilla ES6+ e CSS3 customizado.
   * Renderização de mapas geoespaciais interativos com biblioteca `Leaflet.js` e camadas OpenStreetMap.
   * Painel de Triagem de Anomalias com filtros dinâmicos por secretaria, tipo de falha e severidade.
   * Ambiente Visual de Teste e Simulação no Navegador (`/teste`).

---

## 3. Os 8 Módulos Funcionais Exaustivos

### Módulo 1: Gestão de Ativos e Veículos
* **Cadastro Completo**: Placa Mercosul, Chassi, Renavam, Marca, Modelo, Ano Fabricação/Modelo, Tipo de Combustível, Capacidade do Tanque (L), Capacidade de Carga (kg), Hodômetro e Horímetro atuais.
* **Lotação e Governança**: Vinculação a secretarias (Saúde, Educação, Obras, Segurança, Administração, etc.), centros de custo e motorista titular.
* **Ciclo de Vida do Ativo**: Controle de estados operacionais (`DISPONIVEL`, `EM_VIAGEM`, `EM_MANUTENCAO`, `AGUARDANDO_INSPECAO`, `SINISTRADO`, `BAIXADO_LEILAO`).
* **Indicadores Patrimoniais**: Cálculo contínuo de depreciação, valor de tabela FIPE, custo acumulado de manutenção e indicador de viabilidade de substituição (TCO).

### Módulo 2: Checklist Digital e Inspeção Pré/Pós-Viagem
* **Inspeção de 24 Itens Regulamentares**: Pneus (profundidade de sulco TWI), freios, luzes (faróis, setas, lanternas, freio), fluídos (óleo motor, freio, arrefecimento), equipamentos obrigatórios (triângulo, macaco, chave de roda, cinto de segurança) e integridade da lataria/vidros.
* **Trava Mecânica/Eletrônica de Despacho**: Caso qualquer item de severidade crítica seja reprovado, o sistema rejeita imediatamente o checklist, altera o status do veículo para `BLOQUEADO_INSPECAO` e impede abertura de viagem ou emissão de requisição até que uma OS corretiva seja finalizada.
* **Evidências Digitais**: Registro de fotos da não conformidade com geolocalização e assinatura digital do condutor.

### Módulo 3: Telemetria IoT e Rastreamento em Tempo Real
* **Ingestão Contínua**: Endpoint dedicado `/api/gateway/telemetria` para recepção de pings GPS a cada 30 segundos.
* **Telemetria de Motor**: Leitura de RPM, velocidade real, temperatura do líquido de arrefecimento, código de falha da injeção (DTC / OBD2) e percentual do tanque.
* **Cercas Eletrônicas (Geofencing)**:
  * Zonas Permitidas: Centros operacionais, garagens, unidades de saúde e pátios municipais.
  * Zonas Proibidas / Restritas: Regiões de circulação proibida para veículos pesados ou fora da rota homologada.
* **Mecanismo de Alertas Automáticos**: Disparo de avisos imediatos por excesso de velocidade (> 80 km/h em vias urbanas), acelerações bruscas, frenagens perigosas e marcha lenta excessiva (> 15 minutos com ignição ligada sem deslocamento).

### Módulo 4: Gestão de Abastecimento & Algoritmos Antifraude
* **Registro de Transação**: Data/hora, posto de combustível, tipo de combustível (Gasolina, Etanol, Diesel S10, GNV), litragem, valor unitário, valor total, condutor e hodômetro registrado na bomba.
* **Regra Antifraude 1 (Hodômetro Inconsistente)**: O hodômetro informado não pode ser menor ou igual ao último hodômetro verificado na base de dados.
* **Regra Antifraude 2 (Volume Superior à Capacidade)**: A litragem faturada é confrontada com o volume nominal do tanque homologado no cadastro do veículo, impedindo cobranças indevidas de tanques paralelos ou recipientes avulsos.
* **Regra Antifraude 3 (Eficiência Energética Fora do Padrão)**: O cálculo de $km/L$ do intervalo é submetido a teste estatístico; se desviar mais de 3 desvios-padrão da média do modelo, é classificado como anomalia grave.
* **Regra Antifraude 4 (Geolocalização de Postos)**: Cruzamento das coordenadas do veículo no momento do faturamento com as coordenadas cadastrais do posto credenciado.

### Módulo 5: Gestão de Manutenção e Ciclo de Vida da OS
* **Fluxo de Trabalho Rigoroso**: `ABERTA` $\to$ `EM_COTACAO` $\to$ `APROVADA` $\to$ `EM_EXECUCAO` $\to$ `FINALIZADA` $\to$ `PAGA`.
* **Tipos de Manutenção**:
  * Preventiva: Por gatilho de hodômetro (a cada 10.000 km) ou tempo (a cada 6 meses).
  * Corretiva: Emergencial ou oriunda de reprovação em Checklist Digital.
  * Preditiva: Baseada em sinais de telemetria IoT (elevação gradual de temperatura ou vibração anormal).
* **Catálogo de Peças e Serviços**: Controle de preços de referência, peças aplicadas, horas de mão de obra e aplicação da Curva ABC.
* **Auditoria de Fornecedores**: Ranqueamento de oficinas credenciadas por pontualidade no SLA, índice de retrabalho e desvio de cotação.

### Módulo 6: Gestão de Condutores & Compliance DETRAN
* **Cadastro de Motoristas**: CNH, Categoria (A, B, C, D, E), Data de Validade da CNH, Data de Vencimento do Exame Toxicológico Periódico (obrigatório para C, D e E - Lei 14.071/20) e prontuário de pontos.
* **Trava de Atribuição**: O sistema impede a alocação de motoristas com CNH vencida, toxicológico pendente ou cuja categoria seja incompatível com o veículo a ser conduzido.
* **Gestão de Infrações (Multas)**: Cadastro do Auto de Infração, tipificação CTB, órgão autuador, valor com desconto, prazo de defesa prévia e indicação formal do condutor infrator no sistema estadual (DETRAN/SC).

### Módulo 7: Analítica Prescritiva, Otimização MILP & Machine Learning
* **Detecção de Anomalias Não Supervisionada**: Algoritmo *Isolation Forest* treinado sobre variáveis de custo de OS, frequência de reparos e consumo de combustível para isolar transações suspeitas de sobrepreço.
* **Projeção Orçamentária Trienal**: Modelo aditivo *Facebook Prophet* com sazonalidade anual e regressão de cenários inflacionários (IPCA / IGP-M) projetando o custeio da frota de 2027 a 2029.
* **Otimização MILP de Substituição de Frota**: Algoritmo de Programação Linear Inteira Mista que determina o momento ótimo de alienação/leilão de veículos antieconômicos e substituição por modelos eficientes, comprovando economia anual de **R$ 492.464,00**.

### Módulo 8: Segurança, RBAC & Governança de Dados
* **Matriz de Perfis (RBAC)**:
  * `ADMIN`: Acesso irrestrito a configurações de segurança, emissão de API-Keys e gestão de usuários.
  * `GESTOR_FROTA`: Aprovação de despesas, emissão de relatórios executivos e auditoria de contratos.
  * `OPERADOR`: Despacho de veículos, liberação de pátio e lançamento de notas de abastecimento.
  * `MOTORISTA`: Acesso móvel restrito à execução do Checklist Digital e consulta da própria agenda de viagens.
  * `AUDITOR`: Acesso somente-leitura aos relatórios e trilha de auditoria para órgãos de controle interno e tribunais de contas (TCE).
* **Trilha de Auditoria Imutável**: Log com data/hora UTC, IP, usuário, ação executada e snapshot do estado anterior e posterior.

---

## 4. Dicionário de Dados NoSQL (21 Coleções)

| # | Nome da Coleção | Finalidade Principal | Chave de Partição / Índices |
| :--- | :--- | :--- | :--- |
| 1 | `veiculos` | Cadastro mestre do ativo veicular e status operacional | `placa` (Unique), `secretaria_id`, `status` |
| 2 | `motoristas` | Dados funcionais e habilitação dos condutores | `cpf` (Unique), `cnh_numero`, `status` |
| 3 | `usuarios` | Contas de acesso, perfis RBAC e hashes de credenciais | `username` (Unique), `email`, `role` |
| 4 | `checklists` | Registros de inspeções pré e pós-viagem | `veiculo_id`, `motorista_id`, `data_criacao` |
| 5 | `telemetria_pings` | Série temporal de coordenadas GPS e grandezas do motor | `veiculo_id`, `timestamp`, `coordenadas` (2dsphere) |
| 6 | `abastecimentos` | Transações de combustível e validações de consumo | `veiculo_id`, `data_abastecimento`, `posto_id` |
| 7 | `ordens_servico` | Ordens de manutenção preventiva e corretiva | `numero_os` (Unique), `veiculo_id`, `status` |
| 8 | `pecas_catalogo` | Catálogo mestre de peças com preços de referência | `codigo_peca` (Unique), `categoria` |
| 9 | `oficinas_credenciadas` | Cadastro de prestadores de serviços automotivos credenciados | `cnpj` (Unique), `status_credenciamento` |
| 10 | `multas_infracoes` | Registro de autuações de trânsito e controle de prazos | `numero_auto` (Unique), `veiculo_id`, `status` |
| 11 | `cercas_eletronicas` | Polígonos de zonas permitidas e proibidas (Geofence) | `nome`, `tipo_cerca`, `geometria` |
| 12 | `alertas_sistema` | Notificações de violação operacional e telemetria | `veiculo_id`, `severidade`, `lido` |
| 13 | `viagens_despacho` | Requisições e autorizações formais de saída do pátio | `veiculo_id`, `motorista_id`, `status` |
| 14 | `postos_combustivel` | Rede credenciada de postos de abastecimento | `cnpj` (Unique), `localizacao` |
| 15 | `solicitacoes_veiculo` | Pedidos de agendamento de veículos pelas secretarias | `secretaria_id`, `data_necessidade` |
| 16 | `rotas_planejadas` | Itinerários planejados e pontos de passagem previstos | `viagem_id`, `distancia_estimada_km` |
| 17 | `diario_bordo` | Registro manual de ocorrências pelo motorista | `viagem_id`, `data_registro` |
| 18 | `contratos_locacao` | Gestão de veículos locados de terceiros | `numero_contrato` (Unique), `locadora_cnpj` |
| 19 | `seguros_apolices` | Controle de coberturas, franquias e vigência de apólices | `numero_apolice` (Unique), `veiculo_id` |
| 20 | `sinistros` | Histórico de colisões, avarias e acionamento de seguro | `veiculo_id`, `data_sinistro` |
| 21 | `logs_auditoria` | Trilha de auditoria imutável de todas as ações de usuários | `timestamp`, `usuario_id`, `recurso` |

---

## 5. Catálogo Completo da API REST (35+ Endpoints)

| Método | Endpoint | Perfil Mínimo | Descrição Funcional |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Público | Autenticação por credenciais com emissão de JWT Bearer token |
| `GET` | `/api/auth/me` | Usuário Autenticado | Retorna os dados do perfil logado e permissões ativas |
| `GET` | `/api/veiculos` | Operador | Lista os veículos com paginação e filtros multi-secretaria |
| `POST` | `/api/veiculos` | Gestor de Frota | Cadastra um novo veículo no acervo da frota |
| `GET` | `/api/veiculos/{id}` | Operador | Detalhes cadastrais e status operacional do veículo |
| `PUT` | `/api/veiculos/{id}` | Gestor de Frota | Atualiza dados cadastrais ou lotação do veículo |
| `DELETE` | `/api/veiculos/{id}` | Admin | Desativação ou baixa de veículo por alienação |
| `GET` | `/api/motoristas` | Operador | Lista de motoristas cadastrados e situação de habilitação |
| `POST` | `/api/motoristas` | Gestor de Frota | Cadastra novo condutor com dados de CNH e exame toxicológico |
| `GET` | `/api/motoristas/{id}` | Operador | Consulta de prontuário, CNH e viagens realizadas |
| `PUT` | `/api/motoristas/{id}` | Gestor de Frota | Atualiza validade de CNH ou registro de curso especializado |
| `POST` | `/api/checklists` | Motorista | Submete formulário de inspeção digital pré ou pós-viagem |
| `GET` | `/api/checklists/veiculo/{id}` | Operador | Histórico de checklists realizados com status de aprovação |
| `POST` | `/api/gateway/telemetria` | Gateway IoT (API-Key) | Ingestão em lote de coordenadas GPS e grandezas de telemetria |
| `GET` | `/api/telemetria/veiculo/{id}/ultimo` | Operador | Retorna a última posição satelital e telemetria conhecida |
| `GET` | `/api/telemetria/veiculo/{id}/historico` | Gestor de Frota | Trilha percorrida em intervalo de data com coordenadas e paradas |
| `POST` | `/api/abastecimentos` | Operador | Registra novo abastecimento disparando verificações antifraude |
| `GET` | `/api/abastecimentos/veiculo/{id}` | Operador | Histórico de abastecimentos e cálculo de média de consumo |
| `GET` | `/api/abastecimentos/anomalias` | Gestor de Frota | Lista de abastecimentos com flags de alerta antifraude ativos |
| `POST` | `/api/ordens-servico` | Operador | Abertura de Ordem de Serviço preventiva ou corretiva |
| `GET` | `/api/ordens-servico` | Operador | Relação de OS com filtros por status e oficina executora |
| `PUT` | `/api/ordens-servico/{id}/aprovar` | Gestor de Frota | Aprovação gerencial de orçamento de manutenção |
| `PUT` | `/api/ordens-servico/{id}/finalizar` | Gestor de Frota | Conclusão de OS com baixa de peças e validação de retorno ao pátio |
| `GET` | `/api/multas` | Gestor de Frota | Relação de infrações de trânsito pendentes e pagas |
| `POST` | `/api/multas` | Gestor de Frota | Cadastro de nova autuação com prazos de defesa e recursos |
| `PUT` | `/api/multas/{id}/indicar-condutor` | Gestor de Frota | Vinculação formal do motorista responsável pela infração |
| `GET` | `/api/cercas-eletronicas` | Operador | Relação de polígonos de geofencing cadastrados |
| `POST` | `/api/cercas-eletronicas` | Gestor de Frota | Criação de nova cerca virtual de restrição ou tráfego |
| `GET` | `/api/alertas` | Operador | Lista de alertas operacionais pendentes de visualização |
| `PUT` | `/api/alertas/{id}/reconhecer` | Operador | Marcação de alerta como verificado pelo operador de pátio |
| `GET` | `/api/anomalias` | Gestor de Frota | Base consolidada de anomalias de manutenção e combustíveis (JSON) |
| `GET` | `/api/relatorio-anomalias` | Gestor de Frota | Resumo gerencial agrupado por secretaria municipal/estadual |
| `GET` | `/api/prescritiva/leilao` | Gestor de Frota | Lista otimizada de veículos com recomendação de baixa/leilão |
| `GET` | `/api/prescritiva/previsao-gastos` | Gestor de Frota | Projeção trienal de gastos futuros por modelo de regressão |
| `POST` | `/api/ai/chat` | Usuário Autenticado | Motor NLP de Inteligência Artificial para consultas e auditoria |
| `GET` | `/api/ai/sugestoes` | Usuário Autenticado | Sugestões executivas dinâmicas geradas pela IA da frota |
| `POST` | `/api/ai/diagnostico-veiculo` | Gestor de Frota | Diagnóstico preditivo e análise de saúde do ativo veicular por IA |
| `POST` | `/api/ai/auditar-abastecimento` | Gestor de Frota | Auditoria antifraude de abastecimento por raciocínio analítico |
| `GET` | `/api/assets/iot/dispositivos-descobertos` | Operador | Escaneamento e auto-descoberta de telemetria IoT / CANbus na rede |
| `POST` | `/api/assets/veiculos/autocadastro-iot` | Gestor de Frota | Emparelhamento e cadastro automatizado de veículos via IoT |
| `GET` | `/api/health` | Público | Verificação de integridade do backend e conexão de banco de dados |

---

## 6. Interfaces Web, Dashboards & Suite de Testes no Navegador

### 6.1 Painel Principal da Frota (`http://localhost:8090/`)
* Visão consolidada de KPIs operacionais: total de ativos, veículos em trânsito, veículos disponíveis e em manutenção.
* Mapa interativo em tempo real via Leaflet.js com marcadores inteligentes coloridos pelo status do veículo.
* Tabela de rastreamento com atualização dinâmica de velocidade e última coordenada recebida.
* Widget flutuante de Inteligência Artificial para consultas interativas instantâneas em qualquer tela do sistema.

### 6.2 Ambiente Gráfico de Testes & Simulação (`http://localhost:8090/teste`)
* **Simulador Operacional de 7 Etapas**:
  1. *Inicialização do Sistema*: Checagem de conectividade com a API REST e carregamento do perfil de acesso.
  2. *Inventário de Veículos*: Carga dos dados cadastrais do veículo de teste (ex: Ford Transit Placa QHA-8421).
  3. *Checklist Digital Pré-Viagem*: Simulação de inspeção dos 24 itens, com demonstração visual da **Trava Mecânica**.
  4. *Rastreamento IoT em Tempo Real*: Emissão contínua de pings GPS pela rota pré-programada.
  5. *Telemetria de Condução e Motor*: Painel com mostradores circulares (gauges) dinâmicos de Velocidade, RPM e Combustível.
  6. *Auditoria Antifraude em Abastecimento*: Execução dos 4 testes de validação com verificação de hodômetro e capacidade.
  7. *Ciclo de Vida da Ordem de Serviço*: Abertura de OS preventiva e simulação de aprovação gerencial.
* **Console Cyberpunk ao Vivo**: Exibição dos pacotes JSON trafegados e respostas HTTP em tempo real.

### 6.3 Painel Executivo e Central de Rankings Forenses de Anomalias (`http://localhost:8090/anomalias`)
* Triagem das **6.954 anomalias consolidadas** na base histórica do órgão público (R$ 4.92M auditados).
* **Quíntuplo Ranking Forense de Concentração**:
  1. *Top 10 Oficinas Mecânicas*: Ranqueamento de prestadores com maior índice de inconformidades em OS (liderado por Kalila Melane, Mecânica Dalbosco, Auto Giro e Admol).
  2. *Top 10 Postos de Combustível*: Identificação de estabelecimentos com desvios volumétricos, preços atípicos e hodômetros inconsistentes (liderado por Delta Posto Delta, Posto Palmeiras SC e Agricopel).
  3. *Top 10 Veículos Reincidentes*: Ativos veiculares com maior frequência de falhas e consumo anômalo (liderado por EQU1611, EQU1610 e LXS7849).
  4. *Top 10 Motoristas com Desvios*: Condutores com reincidência em alertas de telemetria, odômetro e abastecimento (liderado por COND_77F3C7FAB075).
  5. *🎯 Tríades & Clusters (Motorista × Veículo × Estabelecimento)*: Cruzamento forense multidimensional que expõe conluios e monopólios fechados, como o motorista COND_77F3C7FAB075 conduzindo EQU1611/EQU1610 exclusivamente no Posto Palmeiras SC (R$ 576k faturados e 97,8% das anomalias do posto) ou o condutor Nuclécio C. da Fonseca respondendo por 100% das anomalias da oficina Kalila Melane.
* **Filtragem Forense Instantânea**: Botões de ação rápida `🔍 Filtrar` em cada linha do ranking que aplicam filtros automáticos na tabela de auditoria com destaque visual e rolagem suave.
* Gráficos analíticos e botão de exportação de dados em formato CSV para subsidiar tomadas de contas especiais e auditorias de Tribunais de Contas (TCE).

### 6.4 Painel Integrado de Cadastro de Veículos: Manual & IoT (`http://localhost:8090/#pane-cadastro-veiculos`)
* **Aba 1 - Cadastro Manual CONTRAN**: Formulário estruturado com validação de Placa Mercosul, Chassi de 17 caracteres, Renavam, secretaria responsável, tipo de combustível e capacidade volumétrica do tanque.
* **Aba 2 - Auto-Descoberta IoT / CANbus Plug-and-Play**: Escaneador em tempo real de dongles OBD2 e rastreadores instalados na frota, permitindo o emparelhamento e autocadastro do veículo com 1 clique a partir da telemetria ativa.

### 6.5 Copiloto Operacional & Inteligência Artificial Nativa (`http://localhost:8090/#pane-ai-copilot`)
* Assistente de IA conversacional integrado diretamente à base histórica (9.514 OS, 6.954 anomalias e R$ 492.464,00 de economia MILP).
* Raciocínio analítico para diagnóstico preditivo de saúde mecânica do veículo e auditoria de abastecimentos.
* Widget flutuante com minimização e expansão rápida disponível em todas as páginas do sistema.

### 6.6 Painel de Abastecimentos (`http://localhost:8090/dashboard/abastecimentos`)
* Rastreamento de consumo por placa, média histórica de $km/L$ e análise comparativa de preços por posto credenciado.

### 6.7 Documentação Interativa da API (`http://localhost:8090/api/docs`)
* Swagger UI interativo permitindo execução de chamadas REST diretamente pelo navegador com suporte a Bearer Token e API-Key.

---

## 7. Guia de Instalação, Configuração e Execução

### 7.1 Requisitos Mínimos
* **Sistema Operacional**: Linux (Ubuntu 20.04+, Debian 11+, Fedora 36+) ou Windows (10, 11, Server 2019+).
* **Interpretador**: Python 3.10 ou superior (testado com sucesso no Python 3.14).
* **Navegador**: Google Chrome, Mozilla Firefox, Microsoft Edge ou Safari atualizados.

### 7.2 Inicialização com Um Único Comando
O sistema possui persistência embarcada via Mongita, não necessitando de instalação prévia de MongoDB para operar.

* **No Linux / macOS**:
  ```bash
  .venv/bin/python sistema_gestao_frotas/executar_sistema.py
  ```
* **No Windows**:
  ```cmd
  python sistema_gestao_frotas\executar_sistema.py
  ```

### 7.3 Credenciais Padrão de Demonstração (RBAC)

* **Administrador**: `admin` / `Admin@Fleet2026!`
* **Gestor de Frota**: `gestor` / `Gestor@Fleet2026!`
* **Operador de Pátio**: `operador` / `Operador@Fleet2026!`
* **Motorista**: `motorista` / `Motorista@Fleet2026!`
* **Gateway IoT (Chave de API)**: `flt_gateway_iot_live_sim_2026_seckey`

---

## 8. Considerações Finais e Conformidade Regulatória

O **FrotaSaaS Enterprise 2.0** atende integralmente às exigências da **Lei Geral de Proteção de Dados (LGPD - Lei 13.709/18)** ao aplicar pseudonimização em dados sensíveis de condutores, anonimização em logs de geolocalização após encerramento do expediente oficial e consentimento expresso para telemetria de condução.

Em termos de governança pública, o sistema adere às diretrizes de frotas da **Secretaria de Estado da Administração de Santa Catarina (SEA/SC)** e às normas do **CONTRAN / DENATRAN**, constituindo uma ferramenta de alta maturidade para a gestão eficiente do erário e conservação do patrimônio público veicular.
"""

def compilar_pdf():
    # Salvar markdown
    md_file = DOCS_DIR / "README_SISTEMA_FROTAS.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(MD_CONTENT)
    print(f"✓ Markdown salvo: {md_file}")

    # Estilo HTML executivo para WeasyPrint
    html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Manual Técnico e Executivo Geral - FrotaSaaS Enterprise 2.0</title>
<style>
    @page {
        size: A4 portrait;
        margin: 1.8cm 1.5cm 2.0cm 1.5cm;
        @top-left {
            content: "SISTEMA INTEGRADO DE GESTÃO DE FROTAS & TELEMETRIA IOT • FROTASAAS 2.0";
            font-size: 7.5pt;
            font-family: 'Liberation Sans', Helvetica, Arial, sans-serif;
            color: #64748b;
            font-weight: 700;
        }
        @top-right {
            content: "MANUAL TÉCNICO & CATÁLOGO DE ENGENHARIA";
            font-size: 7.5pt;
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
            font-size: 7.5pt;
            font-family: 'Liberation Sans', Helvetica, Arial, sans-serif;
            color: #64748b;
            font-weight: 700;
        }
    }

    body {
        font-family: 'Liberation Sans', Helvetica, Arial, sans-serif;
        font-size: 8.8pt;
        line-height: 1.5;
        color: #1e293b;
        margin: 0;
        padding: 0;
    }

    .cover-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0369a1 100%);
        color: #ffffff;
        padding: 28px 24px;
        border-radius: 8px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .cover-badge {
        display: inline-block;
        background: #38bdf8;
        color: #0f172a;
        font-size: 7.5pt;
        font-weight: 800;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 4px;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }

    .cover-title {
        font-size: 20pt;
        font-weight: 900;
        line-height: 1.2;
        margin: 0 0 6px 0;
        color: #ffffff;
    }

    .cover-subtitle {
        font-size: 11pt;
        font-weight: 400;
        color: #bae6fd;
        margin: 0 0 16px 0;
    }

    .cover-meta {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 12px;
        font-size: 8pt;
        color: #e2e8f0;
    }

    .cover-meta strong {
        color: #ffffff;
    }

    h1, h2, h3, h4 {
        color: #0f172a;
        font-weight: 800;
        page-break-after: avoid;
    }

    h2 {
        font-size: 13pt;
        border-bottom: 2px solid #0284c7;
        padding-bottom: 4px;
        margin-top: 22px;
        margin-bottom: 12px;
    }

    h3 {
        font-size: 10.5pt;
        color: #0369a1;
        margin-top: 14px;
        margin-bottom: 6px;
    }

    p {
        margin: 0 0 8px 0;
        text-align: justify;
    }

    ul, ol {
        margin: 0 0 10px 0;
        padding-left: 20px;
    }

    li {
        margin-bottom: 4px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0 16px 0;
        font-size: 7.8pt;
        page-break-inside: avoid;
    }

    th {
        background: #0f172a;
        color: #ffffff;
        font-weight: 700;
        text-align: left;
        padding: 6px 8px;
        border: 1px solid #334155;
    }

    td {
        padding: 5px 8px;
        border: 1px solid #cbd5e1;
        vertical-align: top;
    }

    tr:nth-child(even) td {
        background-color: #f8fafc;
    }

    code {
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 1px 4px;
        border-radius: 3px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 8pt;
    }

    pre {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 10px 14px;
        border-radius: 6px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 7.8pt;
        line-height: 1.4;
        margin: 10px 0 14px 0;
        page-break-inside: avoid;
    }

    .alert-box {
        background-color: #f0f9ff;
        border-left: 4px solid #0284c7;
        padding: 10px 12px;
        border-radius: 0 6px 6px 0;
        margin: 12px 0;
        font-size: 8.2pt;
    }

    .alert-box strong {
        color: #0369a1;
    }

    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin: 12px 0 16px 0;
    }

    .kpi-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px 8px;
        text-align: center;
    }

    .kpi-val {
        font-size: 13pt;
        font-weight: 900;
        color: #0284c7;
    }

    .kpi-label {
        font-size: 7pt;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
    }

    .footer-sign {
        margin-top: 30px;
        border-top: 1px solid #cbd5e1;
        padding-top: 14px;
        font-size: 7.5pt;
        color: #64748b;
        display: flex;
        justify-content: space-between;
    }
</style>
</head>
<body>

<div class="cover-box">
    <div class="cover-badge">RELEASE OFICIAL v2.0-LTS • SISTEMA HOMOLOGADO</div>
    <div class="cover-title">FrotaSaaS Enterprise 2.0</div>
    <div class="cover-subtitle">Sistema Integrado de Gestão de Frotas, Telemetria IoT & Analítica Prescritiva</div>
    <div class="cover-meta">
        <div><strong>Autor:</strong> Eduardo Lopes Jonker (PPGCAP / UDESC)</div>
        <div><strong>Orientadora:</strong> Profa. Dra. Vivian Kremer Kalempa</div>
        <div><strong>Coorientador:</strong> Prof. Dr. Yuri Kaszubowski Lopes</div>
        <div><strong>Instituição:</strong> Universidade do Estado de Santa Catarina</div>
        <div><strong>Arquitetura:</strong> FastAPI, Resilient Mongita/MongoDB, Leaflet.js</div>
        <div><strong>Data de Compilação:</strong> """ + datetime.now().strftime("%d/%m/%Y às %H:%M") + """</div>
    </div>
</div>

<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-val">8</div>
        <div class="kpi-label">Módulos Operacionais</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-val">21</div>
        <div class="kpi-label">Coleções NoSQL</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-val">35+</div>
        <div class="kpi-label">Endpoints REST</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-val">100%</div>
        <div class="kpi-label">Autonomia Standalone</div>
    </div>
</div>

"""

    import markdown
    body_html = markdown.markdown(MD_CONTENT, extensions=['tables', 'fenced_code'])
    # Remove o primeiro h1 do markdown para usar o cabeçalho executivo estilizado
    if "</h1>" in body_html:
        body_html = body_html.split("</h1>", 1)[1]

    full_html = html_template + body_html + """
<div class="footer-sign">
    <div><strong>PPGCAP / UDESC</strong> - Centro de Ciências Tecnológicas (CCT)</div>
    <div>Documento Técnico Registrado para Auditoria e Implantação</div>
</div>
</body>
</html>
"""

    pdf_out = DOCS_DIR / "README_SISTEMA_FROTAS.pdf"
    print("Compilando PDF com WeasyPrint...")
    weasyprint.HTML(string=full_html).write_pdf(str(pdf_out))
    print(f"✓ PDF gerado com sucesso em: {pdf_out}")

    # Copiar para as pastas oficiais de relatórios e documentos
    destinos = [
        REL_ENGENHARIA_DIR / "README_SISTEMA_FROTAS.pdf",
        PDF_DIR / "README_SISTEMA_FROTAS.pdf",
        DOCS_GERAL_DIR / "README_SISTEMA_FROTAS.pdf"
    ]
    for dest in destinos:
        shutil.copy2(pdf_out, dest)
        print(f"✓ Cópia espelhada em: {dest}")

if __name__ == "__main__":
    compilar_pdf()

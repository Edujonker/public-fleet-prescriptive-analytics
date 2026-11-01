# Guia de Integração e Criação de APIs para Conexão Externa
## Plataforma FrotaSaaS Enterprise 2.0 (REST API / IoT Gateway)

---

### 1. Visão Geral da Integração

O **FrotaSaaS Enterprise** dispõe de uma API RESTful de alta performance projetada para interoperabilidade contínua com sistemas terceiros:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          SISTEMAS EXTERNOS                             │
│                                                                        │
│ [Rastreadores GPS 4G]   [Cartões de Frota]   [ERPs Municipais / SAP]   │
│  (Suntech, Queclink)     (Ticket Log, Alelo)  (Contabilidade/Patrimônio)│
└──────────────┬───────────────────┬───────────────────┬─────────────────┘
               │                   │                   │
               │ (Header X-API-Key)│ (Header X-API-Key)│ (JWT Bearer)
               ▼                   ▼                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   FROTASAAS REST API GATEWAY (Porta 8090)              │
│                                                                        │
│ • Roteamento e Validação Estrita (Pydantic v2 / RFC 7807)              │
│ • Autenticação Híbrida: M2M (SHA-256) ou JWT Bearer (Argon2id)         │
│ • Rate Limiting e Payload Shield (Max 10 MB)                           │
│ • Endpoints REST: Telemetria, Abastecimento, OS, TCO, Compliance       │
└────────────────────────────────────────────────────────────────────────┘
```

A API permite:
1. **Ingestão Telemática em Tempo Real**: Envio de pacotes GPS de rastreadores, sensores CANbus e câmeras de fadiga.
2. **Intercâmbio Financeiro com Cartões de Frota**: Registro automatizado de notas e cupons de abastecimento (Ticket Log, Alelo, VR Auto, Sodexo).
3. **Conexão com ERPs de Gestão Pública/Privada**: Sincronização de centros de custo, dados patrimoniais de veículos, ordens de serviço e relatórios contábeis de TCO.
4. **Integração com Órgãos de Trânsito (DETRAN)**: Homologação e indicação de condutores infratores com emissão de protocolo legal.

---

### 2. Autenticação e Gestão de Chaves de API

O sistema adota o modelo de **Autenticação Híbrida** para atender tanto usuários humanos em navegadores quanto integrações automatizadas Machine-to-Machine (M2M).

---

#### 2.1 Método 1: Chaves de API para Integrações M2M (`X-API-Key`)
Recomendado para rastreadores IoT, gateways de telemetria, webhooks e rotinas cron de ERPs que não possuem intervenção humana direta.

##### Características da Chave:
* **Formato**: String de alta entropia iniciada pelo prefixo `flt_` (ex: `flt_gateway_iot_live_sim_2026_seckey`).
* **Segurança Criptográfica**: A chave **nunca é armazenada em texto puro**. No banco de dados, guarda-se exclusivamente o hash criptográfico **SHA-256** da chave.
* **Envio**: Deve ser informada no cabeçalho HTTP:
  ```http
  X-API-Key: flt_gateway_iot_live_sim_2026_seckey
  ```

##### Como Criar uma Nova Chave de API:

###### Opção A: Pelo Painel Web (Interface Gráfica)
1. Acesse o sistema em `http://localhost:8090`.
2. No menu lateral esquerdo, clique em **🔑 Segurança & API Keys**.
3. No formulário "Emitir Nova Chave de API (IoT / M2M)", preencha:
   * **Nome do Dispositivo / Sistema**: Identificador do parceiro (ex: `Gateway Rastreadores Suntech`).
   * **Finalidade / Descrição**: Descrição do fluxo (ex: `Ingestão de pings GPS da frota de pesados`).
   * **Perfil / Permissão**: `OPERADOR`, `GESTOR_FROTA` ou `ADMIN`.
4. Clique no botão **⚡ Gerar Chave Segura**.
5. **ATENÇÃO**: O token completo será exibido na tela apenas uma vez. Copie e guarde em local seguro (cofre de senhas ou arquivo `.env` do parceiro).

###### Opção B: Via Chamada REST API
Envie uma requisição autenticada com perfil `ADMIN`:

```bash
curl -X POST http://localhost:8090/api/v1/auth/api-keys \
  -H "Authorization: Bearer <SEU_JWT_TOKEN_ADMIN>" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_dispositivo": "ERP Municipal Contabilidade",
    "descricao": "Sincronização de custos e TCO de veículos",
    "role": "GESTOR_FROTA"
  }'
```

**Resposta (HTTP 201 Created):**
```json
{
  "id": "672288e1c4a1b2c3d4e5f678",
  "prefix": "flt_4a9b",
  "nome_dispositivo": "ERP Municipal Contabilidade",
  "descricao": "Sincronização de custos e TCO de veículos",
  "created_at": "2026-10-30T16:50:00Z",
  "api_key_completa": "flt_4a9b7f12e8c456a1b2d3e4f50987654321fedcba"
}
```

---

#### 2.2 Método 2: Autenticação via JWT Bearer Token (Usuários e Sistemas Web)
Recomendado para aplicações web e integrações interativas com controle de sessão.

##### Endpoint de Login:
`POST /api/v1/auth/login`

##### Requisição:
```bash
curl -X POST http://localhost:8090/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin@Fleet2026!"
  }'
```

##### Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in_minutes": 1440,
  "user": {
    "username": "admin",
    "nome_completo": "Administrador Geral",
    "role": "ADMIN",
    "secretaria": "SECRETARIA_ADMINISTRACAO"
  }
}
```

Nas requisições subsequentes, inclua o header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3. Catálogo de Endpoints de Integração

A URL base para todas as chamadas é:
`http://localhost:8090/api/v1`

---

#### 3.1 Ingestão de Telemetria IoT e Pings GPS
Utilizado por rastreadores, gateways e dispositivos embarcados para transmitir coordenadas, velocidade e telemetria.

* **Método**: `POST`
* **Rota**: `/telemetria/ping`
* **Autenticação**: `X-API-Key` ou `Bearer <Token>`
* **Content-Type**: `application/json`

##### Payload de Requisição:
```json
{
  "veiculo_placa": "ABC1D23",
  "timestamp": "2026-10-30T16:45:00Z",
  "latitude": -25.4284,
  "longitude": -49.2733,
  "velocidade_kmh": 68.5,
  "ignicao": true,
  "rpm": 1750,
  "odometro_km": 45210.8,
  "motorista_identificador": "111.222.333-44",
  "temperatura_motor_c": 88.0,
  "nivel_combustivel_percent": 74.0,
  "tensao_bateria_v": 13.8
}
```

##### Resposta de Sucesso (HTTP 200 OK):
```json
{
  "id": "67228a42e5f1b2c3d4e5f678",
  "veiculo_placa": "ABC1D23",
  "timestamp": "2026-10-30T16:45:00Z",
  "latitude": -25.4284,
  "longitude": -49.2733,
  "velocidade_kmh": 68.5,
  "ignicao": true,
  "rpm": 1750,
  "odometro_km": 45210.8,
  "recebido_em": "2026-10-30T16:45:01Z",
  "alertas_gerados": []
}
```
*Se houver violação de velocidade, excesso de RPM ou entrada em cerca proibida, os avisos virão listados no array `alertas_gerados`.*

---

#### 3.2 Consulta de Posições Instantâneas da Frota
Utilizado por dashboards de controle e centrais de monitoramento para obter o último status conhecido de todos os veículos.

* **Método**: `GET`
* **Rota**: `/telemetria/posicoes`
* **Autenticação**: `Bearer <Token>` ou `X-API-Key`

##### Resposta de Sucesso (HTTP 200 OK):
```json
[
  {
    "veiculo_placa": "ABC1D23",
    "modelo": "Scania R450 6x2",
    "motorista_nome": "Carlos Silva",
    "latitude": -25.4284,
    "longitude": -49.2733,
    "velocidade_kmh": 68.5,
    "ignicao": true,
    "rpm": 1750,
    "odometro_km": 45210.8,
    "status_operacional": "EM_TRANSITO",
    "ultima_atualizacao": "2026-10-30T16:45:01Z"
  }
]
```

---

#### 3.3 Integração de Abastecimentos (Cartões Frota / Postos)
Utilizado para importar abastecimentos realizados em postos conveniados ou por meio de cartões de frota (Ticket Log, Alelo, VR Auto).

* **Método**: `POST`
* **Rota**: `/abastecimento/`
* **Autenticação**: `Bearer <Token>` ou `X-API-Key`

##### Payload de Requisição:
```json
{
  "veiculo_placa": "ABC1D23",
  "motorista_identificador": "111.222.333-44",
  "posto_combustivel": "Posto Ipiranga Rodo BR-277",
  "tipo_combustivel": "DIESEL",
  "litros": 280.0,
  "valor_litro": 5.89,
  "odometro_km": 45210.0,
  "cartao_combustivel": "TICKET_LOG",
  "numero_comprovante": "NF-987452"
}
```

##### Resposta de Sucesso com Validação Antifraude (HTTP 200 OK):
```json
{
  "id": "67228b8fe5f1b2c3d4e5f679",
  "veiculo_placa": "ABC1D23",
  "litros": 280.0,
  "valor_total": 1649.20,
  "consumo_calculado_kml": 3.85,
  "consumo_l_km": 0.26,
  "anomalia_detectada": false,
  "motivo_anomalia": null,
  "created_at": "2026-10-30T16:46:00Z"
}
```
*Caso o volume ultrapasse o tanque (ex: 350L para tanque de 300L), o campo `anomalia_detectada` será `true` e conterá a justificativa técnica.*

---

#### 3.4 Abertura de Ordem de Serviço (Oficinas Credenciadas / ERP Manutenção)
Utilizado por oficinas autorizadas para registrar manutenções com detalhamento de peças e serviços.

* **Método**: `POST`
* **Rota**: `/manutencao/os`
* **Autenticação**: `Bearer <Token>` ou `X-API-Key`

##### Payload de Requisição:
```json
{
  "veiculo_placa": "DEF2G45",
  "tipo": "PREVENTIVA",
  "data_previsao": "2026-11-05",
  "oficina_credenciada": "Oficina Diesel Master Curitiba",
  "odometro_momento_km": 28500.0,
  "observacoes": "Troca de filtros e óleo do motor",
  "itens_pecas": [
    {
      "codigo": "FIL-001",
      "descricao": "Filtro de Óleo Lubrificante",
      "quantidade": 1.0,
      "valor_unitario": 120.0,
      "subtotal": 120.0
    }
  ],
  "servicos": [
    {
      "descricao": "Mão de obra de troca e revisão",
      "horas": 2.5,
      "valor_hora": 90.0,
      "subtotal": 225.0
    }
  ]
}
```

---

#### 3.5 Consulta de TCO e CPK para ERP Contábil
Utilizado pela contabilidade e controladoria para extrair o custo total de posse e custo por quilômetro rodado ($R\$/km$).

* **Método**: `GET`
* **Rota**: `/relatorios/tco`
* **Autenticação**: `Bearer <Token>` ou `X-API-Key`

##### Resposta de Sucesso (HTTP 200 OK):
```json
[
  {
    "veiculo_placa": "ABC1D23",
    "modelo": "Scania R450 6x2",
    "categoria": "PESADO",
    "custo_aquisicao": 650000.0,
    "custo_manutencao_total": 4250.0,
    "custo_combustivel_total": 8920.0,
    "custo_pneus_total": 3100.0,
    "custo_pedagios_total": 650.0,
    "custo_multas_total": 0.0,
    "custo_seguros_taxas": 12000.0,
    "custo_total_operacional": 28920.0,
    "km_total_rodado": 12450.0,
    "cpk_reais_por_km": 2.32
  }
]
```

---

#### 3.6 Indicação de Condutor Infrator (Integração DETRAN)
Utilizado para cumprir o prazo legal do CTB e transferir a pontuação da multa para o prontuário do motorista responsável.

* **Método**: `POST`
* **Rota**: `/compliance/multas/{multa_id}/indicar-condutor`
* **Autenticação**: `Bearer <Token>`

##### Payload de Requisição:
```json
{
  "motorista_identificador": "111.222.333-44",
  "documento_cnh": "12345678900"
}
```

##### Resposta de Sucesso:
```json
{
  "id": "67228c11e5f1b2c3d4e5f680",
  "auto_infracao": "AIT-PR-2026-99881",
  "status_indicacao": "HOMOLOGADO",
  "protocolo_detran": "DETRAN-IND-20261030-99881",
  "updated_at": "2026-10-30T16:47:00Z"
}
```

---

### 4. Exemplos Práticos de Código para Integração

---

#### 4.1 Exemplo em Python (`requests`)
Ideal para scripts de ingestão e conexões de backend com ERP:

```python
import requests
import json

BASE_URL = "http://localhost:8090/api/v1"
API_KEY = "flt_gateway_iot_live_sim_2026_seckey"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 1. Enviar telemetria de um veículo
payload_telemetria = {
    "veiculo_placa": "ABC1D23",
    "latitude": -25.4284,
    "longitude": -49.2733,
    "velocidade_kmh": 65.0,
    "ignicao": True,
    "rpm": 1600,
    "odometro_km": 45300.0,
    "motorista_identificador": "111.222.333-44"
}

response = requests.post(f"{BASE_URL}/telemetria/ping", json=payload_telemetria, headers=headers)

if response.status_code == 200:
    print("Telemetria recebida:", response.json())
else:
    print("Erro na integração:", response.status_code, response.text)

# 2. Consultar posições de toda a frota
posicoes = requests.get(f"{BASE_URL}/telemetria/posicoes", headers=headers).json()
print(f"Total de veículos monitorados: {len(posicoes)}")
```

---

#### 4.2 Exemplo em cURL (Bash / Terminal)
Ideal para testes rápidos em linha de comando ou chamadas cron no Linux:

```bash
# Ingestão de Ping de Telemetria
curl -X POST "http://localhost:8090/api/v1/telemetria/ping" \
  -H "X-API-Key: flt_gateway_iot_live_sim_2026_seckey" \
  -H "Content-Type: application/json" \
  -d '{
    "veiculo_placa": "MNO3P45",
    "latitude": -25.4512,
    "longitude": -49.2891,
    "velocidade_kmh": 42.0,
    "ignicao": true,
    "rpm": 1400,
    "odometro_km": 15420.0
  }'

# Consulta do Relatório de TCO
curl -X GET "http://localhost:8090/api/v1/relatorios/tco" \
  -H "X-API-Key: flt_gateway_iot_live_sim_2026_seckey"
```

---

#### 4.3 Exemplo em JavaScript / Node.js (`fetch`)
Ideal para microserviços e frontends integradores:

```javascript
const API_BASE = 'http://localhost:8090/api/v1';
const API_KEY = 'flt_gateway_iot_live_sim_2026_seckey';

async function enviarAbastecimento(dados) {
  try {
    const response = await fetch(`${API_BASE}/abastecimento/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify(dados)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Falha no abastecimento: ${errorData.detail}`);
    }

    const resultado = await response.json();
    console.log('Abastecimento registrado com sucesso:', resultado);
    return resultado;
  } catch (error) {
    console.error('Erro na chamada da API:', error.message);
  }
}

// Chamada de teste
enviarAbastecimento({
  veiculo_placa: 'DEF2G45',
  posto_combustivel: 'Posto Petrobras Cidade',
  tipo_combustivel: 'GASOLINA',
  litros: 45.0,
  valor_litro: 5.99,
  odometro_km: 28650.0,
  cartao_combustivel: 'ALELO'
});
```

---

### 5. Tratamento de Erros e Códigos de Status HTTP

Todas as respostas de erro seguem o padrão padronizado com código HTTP apropriado e corpo JSON seguro:

| Código HTTP | Significado | Causa Típica |
| :--- | :--- | :--- |
| **`200 OK`** | Sucesso | Requisição processada com êxito. |
| **`201 Created`** | Criado | Recurso (veículo, OS, viagem, API key) cadastrado com sucesso. |
| **`400 Bad Request`** | Regra de Negócio Violada | Ex: Prazo do CTB expirado, checklist reprovado com trava impeditiva. |
| **`401 Unauthorized`** | Não Autenticado | Chave de API ausente, inválida ou token JWT expirado. |
| **`403 Forbidden`** | Acesso Negado | Perfil de usuário sem autorização no RBAC para a operação. |
| **`404 Not Found`** | Recurso Não Encontrado | Veículo, motorista ou OS não localizada com o identificador fornecido. |
| **`422 Unprocessable`**| Erro de Validação de Dados | Campos obrigatórios ausentes, tipos incorretos ou regex incompatível. |
| **`429 Too Many Req`**| Limite de Taxa Excedido | Número de requisições por segundo superior à política de proteção. |
| **`500 Internal Error`**| Erro do Servidor | Falha interna não tratada (resposta sanitizada sem vazamento de stack). |

#### Formato do JSON de Erro:
```json
{
  "detail": "Não foi possível despachar a viagem: checklist de segurança foi REPROVADO por não-conformidade técnica."
}
```

---

### 6. Diretrizes de Segurança para Conexão Externa

1. **Proteção do Segredo**: Nunca comite chaves `flt_...` ou tokens em repositórios de código públicos (Git). Use variáveis de ambiente (`.env`).
2. **Rotação de Chaves**: Recomenda-se rotacionar as chaves de API a cada 90 ou 180 dias. O sistema permite criar uma chave nova e revogar a antiga sem paradas operacionais.
3. **Limite de Tamanho de Payload**: O gateway rejeita qualquer pacote de requisição com tamanho superior a **10 MB**, prevenindo ataques de negação de serviço (DoS por exaustão de memória).
4. **Proteção contra Injeção**: Todas as entradas são validadas de forma estrita contra schemas Pydantic v2 com tipagem forte e expressões regulares.

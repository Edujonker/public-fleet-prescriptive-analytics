# Central de Documentação Técnica e Operacional
## FrotaSaaS Enterprise 2.0 - Gestão Integrada de Frotas, Telemetria IoT & TCO

Seja bem-vindo à central de documentação oficial do **FrotaSaaS Enterprise 2.0**. Esta pasta reúne guias completos que cobrem desde a operação diária das telas até a modelagem avançada de banco de dados e APIs de integração para sistemas externos.

---

### 📚 Índice dos Documentos Oficiais

| Documento | Descrição e Finalidade | Formato e Recursos |
| :--- | :--- | :--- |
| **[Manual do Sistema](MANUAL_DO_SISTEMA.md)** | Guia operacional completo de todos os 8 módulos da aplicação, perfis de usuários (RBAC), credenciais de acesso, instruções de inicialização (Linux e Windows) e regras de negócio. | Markdown estruturado com tabelas operacionais e passos de execução. |
| **[Dicionário de Dados](DICIONARIO_DE_DADOS.md)** | Especificação exaustiva de todas as 21 coleções do banco de dados (MongoDB/Mongita), detalhando campos, tipos de dados, validações Pydantic v2, valores padrão, restrições e diagrama ERD. | Diagrama Mermaid ERD + 21 tabelas de especificação de campos. |
| **[Guia de Integração e Criação de APIs](GUIA_INTEGRACAO_API.md)** | Manual para desenvolvedores e arquitetos de software para conexão com ERPs externos (contabilidade, folha, patrimônio), cartões frota (Ticket Log, Alelo), rastreadores GPS IoT e DETRAN. | Especificação OpenAPI, JSON schemas, cURL, Python e JavaScript. |
| **[Mapa Mental do Sistema](MAPA_MENTAL_SISTEMA_FROTAS.md)** | Visualização panorâmica de todo o ecossistema, interconexão de módulos operacionais, diagramas de sequência de despacho seguro, telemetria e matriz de atores. | Diagrama Mermaid `mindmap` + `sequenceDiagram` interativos. |
| **[Infográfico do Sistema](INFOGRAFICO_SISTEMA_FROTAS.md)** | Representação visual em alta definição dos 6 pilares de inteligência veicular, rastreamento satelital, trava mecânica de checklist, inspeção CONTRAN e cofre de segurança. | Imagem tecnológica em alta definição (`img/infografico_gestao_frotas.jpg`) + decomposição técnica. |

---

### 🚀 Inicialização Rápida dos Sistemas

#### Opção 1: Iniciar Somente o Sistema de Frotas (Porta 8090)
* **Linux**: `./sistema_gestao_frotas/iniciar_linux.sh` ou `python3 sistema_gestao_frotas/executar_sistema.py`
* **Windows**: `sistema_gestao_frotas\iniciar_windows.bat` ou `python sistema_gestao_frotas\executar_sistema.py`
* **URL de Acesso**: `http://localhost:8090`
* **Documentação Interativa Swagger**: `http://localhost:8090/docs`
* **Documentação Redoc**: `http://localhost:8090/redoc`

#### Opção 2: Iniciar Ambos os Sistemas em Paralelo (Porta 8080 e 8090)
* **Comando Universal**: `python3 executar_ambos_sistemas.py`
* **Porta 8090**: Sistema de Gestão de Frotas & Telemetria IoT (`http://localhost:8090`)
* **Porta 8080**: Dashboard de Inteligência Preditiva da Dissertação (`http://localhost:8080/dashboard/`)

---

### 🛡️ Credenciais Padrão do Sistema (RBAC)

* **Administrador Geral**: Usuário `admin` | Senha `Admin@Fleet2026!` (Acesso total)
* **Gestor de Frota**: Usuário `gestor` | Senha `Gestor@Fleet2026!` (Aprovações e relatórios)
* **Operador de Pátio**: Usuário `operador` | Senha `Operador@Fleet2026!` (Despacho e abastecimento)
* **Motorista**: Usuário `motorista` | Senha `Motorista@Fleet2026!` (Checklists)
* **Chave de API IoT Padrão**: `flt_gateway_iot_live_sim_2026_seckey`

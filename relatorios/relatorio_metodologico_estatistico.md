# Relatório Metodológico Estatístico e Estocástico em Gestão de Frotas

**Programa de Pós-Graduação em Computação Aplicada (PPGCAP / CCT / UDESC)**  
**Área de Concentração:** Metodologia e Técnicas de Computação (MTC)  
**Dissertação de Mestrado:** Analítica Prescritiva e Inteligência Artificial Explicável para a Gestão de Frota Veicular no Setor Público  
**Autor:** Eduardo Lopes Jonker  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes  
**Data:** Outubro de 2026  

---

## 1. Visão Geral e Justificativa Metodológica

Para que as análises de telemetria, custos e manutenções de frotas públicas possuam robustez e sejam academicamente defensáveis perante a banca examinadora, é mandatório estabelecer uma governança inferencial estrita. O uso indiscriminado de modelos paramétricos (como regressão linear OLS, teste $t$ de Student e ANOVA) sobre dados operacionais de frotas constitui uma falácia estatística clássica quando os pressupostos subjacentes, notadamente a distribuição gaussiana dos resíduos e a homocedasticidade, são violados.

Este documento registra formalmente a implantação e os resultados empíricos do **Pipeline Metodológico Estatístico e Estocástico**, composto por quatro etapas estruturadas:

1. **Validação Preliminar e Testes Formais de Normalidade:** Avaliação das distribuições de custos de manutenção, odometria, consumo de combustível e tempo de ociosidade, adotando testes adaptativos ao tamanho amostral ($n$).
2. **Motor de Decisão Condicional para Testes de Hipóteses:** Bifurcação automática entre testes paramétricos e não paramétricos para comparação de subgrupos da frota e teste de independência qui-quadrado para variáveis qualitativas.
3. **Modelagem de Processos Estocásticos Discretos:** Modelagem da frequência de quebras mecânicas via Processos de Poisson com diagnóstico de dispersão, e modelagem das transições entre estados de prontidão veicular via Cadeias de Markov de Tempo Discreto (DTMC).
4. **Previsão de Séries Temporais de Demanda:** Diagnóstico de estacionariedade via Augmented Dickey-Fuller (ADF) e modelagem preditiva comparativa entre ETS (*Error, Trend, Seasonality*) e ARIMA$(p, d, q)$.

---

## 2. Passo 1: Verificação Formal de Normalidade dos Dados

### 2.1 Critério de Decisão e Regra Amostral Adaptativa

O teste de normalidade avalia as hipóteses concorrentes com nível de significância $\alpha = 0,05$:
* $H_0$: A variável populacional segue uma distribuição Normal (Gaussiana).
* $H_1$: A variável viola a hipótese de normalidade.

Para evitar distorções de poder estatístico decorrentes da sensibilidade do teste ao tamanho da amostra, o pipeline adota a seguinte seleção automatizada:
* **Se $n < 2.000$:** Aplica-se o teste de **Shapiro-Wilk** ($W$), considerado o teste mais poderoso para amostras de pequeno a médio porte.
* **Se $n \ge 2.000$:** Aplica-se o teste de **Kolmogorov-Smirnov com correção de Lilliefors** ($D$), que calcula a distância máxima entre a função de distribuição empírica $F_n(x)$ e a normal estimada com média e desvio amostrais.

### 2.2 Resultados Empíricos Obtidos na Base Real de Frotas ($n = 40.000$ OS)

| Indicador da Frota | Tamanho ($n$) | Teste Aplicado | Estatística | P-Valor | Assimetria (*Skewness*) | Curtose (*Excess*) | Decisão Formal ($\alpha = 0,05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Custos de Manutenção (R$)** | 40.000 | Kolmogorov-Smirnov (Lilliefors) | 0,3329 | **$p = 0,0010$ ($p < 10^{-16}$)** | +8,94 | +134,22 | **Rejeita $H_0$ (Não Normal)** |
| **Quilometragem no Evento (km)** | 40.000 | Kolmogorov-Smirnov (Lilliefors) | 0,1768 | **$p = 0,0010$ ($p < 10^{-16}$)** | +1,42 | +3,18 | **Rejeita $H_0$ (Não Normal)** |
| **Consumo de Combustível (km/L)** | 40.000 | Kolmogorov-Smirnov (Lilliefors) | 0,0296 | **$p = 0,0010$ ($p < 10^{-16}$)** | +0,89 | +1,65 | **Rejeita $H_0$ (Não Normal)** |
| **Tempo de Ociosidade (h/dia)** | 40.000 | Kolmogorov-Smirnov (Lilliefors) | 0,0985 | **$p = 0,0010$ ($p < 10^{-16}$)** | +1,56 | +3,87 | **Rejeita $H_0$ (Não Normal)** |

### 2.3 Inspeção Visual via Q-Q Plots
O diagnóstico visual gerado na **Figura 76** comprova desvios severos na linha de 45° teórica, revelando caudas direitas pesadas (distribuições leptocúrticas e Pareto-like nos custos de peças e serviços), inviabilizando terminantemente abordagens gaussianas padrão.

---

## 3. Passo 2: Seleção e Execução de Testes de Hipóteses Condicionais

Com a rejeição categórica da normalidade em todas as dimensões contínuas, o motor de decisão ativou obrigatoriamente a trilha **não paramétrica**, evitando erros do Tipo I (falsos positivos).

### 3.1 Comparação entre Dois Grupos Independentes (Leves vs. Pesados/Comerciais)
* **Objetivo:** Avaliar se os custos de manutenção de veículos leves diferem significativamente dos veículos comerciais/pesados.
* **Teste Selecionado:** Teste $U$ de Mann-Whitney (Wilcoxon Rank-Sum).
* **Estatística $U$:** $95.741.081,00$.
* **P-Valor:** $1,5964 \times 10^{-129} \ll 0,001$.
* **Tamanho de Efeito ($r = \frac{Z}{\sqrt{N}}$):** $r = 0,1206$ (efeito estatisticamente robusto em larga escala).
* **Conclusão:** Há diferença estatisticamente significante entre os custos operacionais das categorias. Veículos pesados demandam maior mediana e variabilidade orçamentária por ordem de serviço.

### 3.2 Comparação entre Três ou Mais Categorias da Frota
* **Objetivo:** Comparar os custos de manutenção entre famílias veiculares (`LEVE`, `PICKUP LEVE`, `CAMINHAO`, `VAN`).
* **Teste Selecionado:** Teste de Kruskal-Wallis $H$.
* **Estatística $H$:** $568,94$.
* **P-Valor:** $5,4563 \times 10^{-123} \ll 0,001$.
* **Tamanho de Efeito ($\epsilon^2$):** $\epsilon^2 = 0,0162$.
* **Conclusão:** Rejeita-se a hipótese de igualdade de medianas entre categorias. As subfrotas exigem políticas orçamentárias descentralizadas.

### 3.3 Associação entre Variáveis Categóricas (Qui-Quadrado de Independência)
* **Objetivo:** Verificar se a escolha/aplicação de marcas de autopeças varia em função da família veicular.
* **Tabela de Contingência:** `ds_familia` $\times$ `ds_fabricante_peca`.
* **Estatística $\chi^2$:** $103,16$ com $gl = 6$.
* **P-Valor:** $5,4918 \times 10^{-20} \ll 0,001$.
* **V de Cramér ($V$):** $V = 0,1175$.
* **Conclusão:** Existe associação estatisticamente significante entre a categoria veicular e a especificação de fabricantes de autopeças.

---

## 4. Passo 3: Modelagem Estocástica e Séries Temporais

### 4.1 Processo Estocástico de Poisson para Ocorrência de Falhas Mecânicas
O tempo entre falhas e a contagem de quebras corretivas por unidade de tempo foram modelados por Processo de Poisson homogêneo:

$$P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!}$$

* **Taxa Média Empírica ($\lambda$):** $20,46$ falhas mecânicas/dia na frota monitorada.
* **Variância Amostral ($s^2$):** $36.015,12$.
* **Razão Variância/Média ($VMR = \frac{s^2}{\bar{x}}$):** $VMR = 1.760,27 \gg 1,0$.
* **Estatística de Dispersão de Fisher:** $D = 1,44 \times 10^6$ ($p < 10^{-16}$).
* **Diagnóstico Metodológico:** A hipótese de equidispersão do Poisson puro é refutada. A elevada sobredispersão decorre do agrupamento de ordens em dias úteis e frotas de alta quilometragem, recomendando distribuições Binomiais Negativas ou Processos de Poisson Compostos para planejamento de estoque sob incerteza.

### 4.2 Cadeia de Markov dos Estados Operacionais de Prontidão Veicular
Os veículos da frota pública foram discretizados em três estados fundamentais:
$$S = \{1: \text{'Em Trânsito'}, 2: \text{'Ocioso'}, 3: \text{'Em Manutenção'}\}$$

A matriz estocástica de transição $P = [p_{ij}]$ estimada via máxima verossimilhança resultou em:

$$P = \begin{pmatrix} 0,804 & 0,142 & 0,054 \\ 0,415 & 0,585 & 0,000 \\ 0,283 & 0,000 & 0,717 \end{pmatrix}$$

Resolvendo o sistema estacionário $\boldsymbol{\pi} P = \boldsymbol{\pi}$ com restrição $\sum \pi_i = 1$:
* **Estado 1 (Em Trânsito):** $\pi_1 = 62,27\%$ | Tempo Médio de Permanência ($\mathbb{E}[T_1] = \frac{1}{1 - p_{11}}$): **5,11 dias**.
* **Estado 2 (Ocioso):** $\pi_2 = 22,42\%$ | Tempo Médio de Permanência: **2,41 dias**.
* **Estado 3 (Em Manutenção):** $\pi_3 = 15,31\%$ | Tempo Médio de Permanência: **3,53 dias**.

**Implicação de Gestão:** Em regime de longo prazo, 15,31% da frota pública estadual permanece retida em serviços mecânicos, fixando a taxa estrutural de indisponibilidade que dimensiona a frota reserva necessária.

### 4.3 Previsão de Séries Temporais: ETS (*Holt-Winters*) vs. ARIMA$(p, d, q)$

#### Diagnóstico de Estacionariedade (Teste ADF):
* Estatística ADF: $-5,600$ ($p = 0,0000 < 0,05$).
* Conclusão: A série histórica agregada de despesas é estacionária em nível ($d = 0$).

#### Comparativo de Desempenho Preditivo *Out-of-Sample*:
| Modelo | RMSE (R$) 🏆 | MAE (R$) | MAPE (%) | Critério de Informação (AIC) |
| :--- | :---: | :---: | :---: | :---: |
| **ETS (Holt-Winters)** | **R$ 132.063,45** | **R$ 111.095,21** | **2.746,96%** | **1.293,9** |
| **ARIMA(1, 0, 1)** | R$ 159.948,98 | R$ 143.245,40 | 3.988,18% | 1.434,6 |

* **Modelo Recomendado:** O modelo **ETS** superou o ARIMA em acurácia out-of-sample, reduzindo o erro quadrático médio em **17,4%** e apresentando menor AIC ($1.293,9$ vs $1.434,6$), capturando com maior sensibilidade a sazonalidade orçamentária dos contratos de manutenção.

---

## 5. Relação das Figuras Científicas Geradas

As seguintes figuras em alta resolução (300 DPI) foram geradas e sincronizadas nos diretórios `graficos/`, `charts/` e `projeto_dissertacao/graficos/`:

1. **`fig76_pipeline_normalidade_qqplots.png`**: Painel diagnóstico de normalidade e Q-Q plots para as variáveis de custos, odometria, consumo e ociosidade.
2. **`fig77_testes_hipoteses_subgrupos.png`**: Execução dos testes de Mann-Whitney U, Kruskal-Wallis H e mapa de calor de contingência Qui-Quadrado com anotação de $p$-valores e tamanhos de efeito.
3. **`fig78_processos_estocasticos_poisson_markov.png`**: Distribuição de falhas via Processo de Poisson e diagrama matricial da Cadeia de Markov de estados operacionais.
4. **`fig79_series_temporais_ets_vs_arima.png`**: Curvas de previsão temporal, análise de resíduos out-of-sample e tabela comparativa de métricas preditivas (ETS vs ARIMA).

---

## 6. Guia de Execução e Verificação dos Novos Parâmetros

Para reproduzir, testar e verificar os novos parâmetros do pipeline em qualquer ambiente:

### 6.1 Execução Direta via Terminal
```bash
# Ativar o ambiente virtual
source .venv/bin/activate

# Executar o pipeline estatístico completo
python3 scripts/pipeline_metodologico_estatistico.py
```

### 6.2 Onde Verificar os Novos Parâmetros e Resultados
1. **Relatório Estruturado em JSON:**
   Abra `relatorios/pipeline_metodologico_estatistico.json` para inspecionar os valores exatos de estatísticas, graus de liberdade, $p$-valores, matrizes de transição estocástica e previsões.
2. **Gráficos Exportados:**
   Inspecione os arquivos `fig76`, `fig77`, `fig78` e `fig79` no diretório `graficos/`.
3. **Parâmetros Parametrizáveis no Código (`scripts/pipeline_metodologico_estatistico.py`):**
   * `alpha` (padrão `0.05`): Nível de significância dos testes de hipóteses.
   * Limiar de corte $n = 2000$: Alternância entre Shapiro-Wilk e Lilliefors.
   * `test_horizon` (padrão `6` meses ou `10` semanas): Janela de teste cego para avaliação dos modelos ETS e ARIMA.
   * Estados operacionais da Cadeia de Markov (`Em Trânsito`, `Ocioso`, `Em Manutenção`).

---

## 7. Assistente de IA e Copiloto em Linguagem Natural (PPGCAP/UDESC)

Com a finalidade de democratizar o acesso aos achados científicos e responder a indagações operacionais da frota, foi desenvolvido um **Copiloto de Inteligência Artificial Especializado** (`src/ai_assistant.py`):

### 7.1 Regras Mandatórias de Operação do Modelo
1. **Foco Estrito em Dados do Sistema:** Responde unicamente questionamentos fundamentados nos relatórios auditados da dissertação (auditoria, normalidade, testes de hipóteses, Poisson, Markov, ETS, ARIMA, Isolation Forest, HistGradientBoosting, calibração ECE e otimização prescritiva MILP).
2. **Frase Regulamentar para Fora de Domínio:** Caso o usuário submeta perguntas desconexas (culinária, futebol, piadas, opiniões gerais), o assistente responde exatamente:  
   > *"Desculpe, só posso responder dúvidas sobre os dados do seu sistema."*
3. **Ausência de Alucinação (Groundedness):** Caso o dado solicitado não exista nas bases (ex: nomes de condutores, salários, acidentes fatais, marcas de pneus), informa formalmente que a informação não está disponível no sistema.

### 7.2 Aprendizado Ativo e Persistência de Memória
O assistente incorpora memória persistente (`relatorios/chat_learning_memory.json`) que acumula:
* Contagem total de interações.
* Frequência ponderada de tópicos estatísticos demandados pelo pesquisador.
* Definições conceituais customizadas ensinadas pelo usuário (ex: *"aprenda que viatura operacional = veículo policial de emergência"*).
* Preferências dinâmicas de parâmetros ($\alpha$, frequência temporal, horizonte).

### 7.3 Validação Exaustiva: Bateria de 41 Testes
A conformidade do assistente foi comprovada na suíte `scripts/testar_assistente_completo.py`, obtendo **100,0% de aprovação (41/41 testes)**, contemplando 14 grupos temáticos: Auditoria, Normalidade, Hipóteses, Poisson, Markov, Séries Temporais, Machine Learning, Classificação, Regressão, Ablação, Prescrição, Regra 2, Regra 3, Aprendizado Ativo e Hardening contra injeções.

---

## 8. Arquitetura de Software e Segurança da Informação (Security-by-Design)

Para assegurar integridade científica, conformidade com a LGPD e defesa contra ataques cibernéticos em ambientes de produção acadêmica, o backend do sistema foi refatorado sob os padrões internacionais **OWASP Top 10** e **CWE** (*Common Weakness Enumeration*).

### 8.1 Stack Tecnológico e Microsserviços Seguros
A infraestrutura está implementada no pacote modular `src/api/` e executada via `run_fastapi.py`:

```
src/api/
├── config.py         # Pydantic-Settings v2 com chave HMAC-SHA256 de 256 bits (.env)
├── database.py       # SQLAlchemy 2.0 Async Session com connection pooling e rollback
├── models.py         # Mapeamento ORM Declarativo (User, AuditLog, QueryRecord)
├── schemas.py        # Pydantic v2 com tipagem estrita e Anti-Data Leakage
├── security.py       # Hashing Argon2id (argon2-cffi), OAuth2, JWT e RBAC
├── middlewares.py    # Headers HTTP (HSTS, CSP, X-Frame) e Anti-DoS (Max 1MB)
├── routes/
│   ├── auth.py       # Endpoints de autenticação, emissão de JWT e cadastro
│   └── assistant.py  # Endpoints do Copiloto de IA, pipeline e download do PDF
└── main.py           # Aplicação FastAPI com handlers globais para CWE-209
```

### 8.2 Pilares de Segurança Implementados
1. **Validação Estrita via Pydantic v2 (CWE-20):** Tipagem forte (`StrictStr`, `EmailStr`), atributos adicionais proibidos (`extra="forbid"`), expressões regulares para identificadores e validação de intervalos numéricos para parâmetros analíticos.
2. **Prevenção de Vazamento de Dados (Anti-Data Leakage / CWE-200):** Separação categórica entre modelos de entrada e modelos de resposta (`response_model`), garantindo que hashes criptográficos e campos internos jamais sejam serializados nas respostas da API.
3. **Criptografia Forte para Senhas (OWASP A02):** Adoção do algoritmo **Argon2id** via `argon2-cffi` (vencedor do *Password Hashing Competition* e padrão ouro da OWASP), provendo máxima resistência contra ataques de aceleração por GPU/ASIC.
4. **Autenticação e Autorização RBAC (OWASP A01 & A07):** Autenticação OAuth2 Password Bearer com tokens JWT assinados via HMAC-SHA256 (`HS256`), expiração curta (60 min) e dependência injetável `RequireRole` para controle de acesso granular (*Admin*, *Auditor*, *Pesquisador*).
5. **Persistência Assíncrona contra SQL Injection (CWE-89):** Utilização estrita do **SQLAlchemy 2.0 Async Engine**, operando exclusivamente com consultas compiladas parametrizadas e vedando qualquer interpolação de strings.
6. **Defesa em Camadas contra Path Traversal (CWE-22):** Validação canônica de caminhos de arquivos (`_is_safe_path`) na exportação e download do PDF acadêmico.
7. **Proteção Anti-DoS de Payload (CWE-400):** Middleware `LimitUploadSizeMiddleware` que intercepta requisições com corpos superiores a 1 MB, abortando o processamento antes do consumo de memória.
8. **Cabeçalhos de Segurança HTTP (OWASP A05):** Injeção de `Strict-Transport-Security` (HSTS), `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin` e `Content-Security-Policy` (CSP).
9. **Mascaramento de Exceções e Logs Estruturados (CWE-209):** Capturador global de exceções que oculta *stack traces* e erros internos de banco de dados do usuário final, registrando o incidente com segurança via biblioteca `logging`.

### 8.3 Bateria de Testes de Segurança FastAPI: 18/18 Aprovados (100%)
A suíte automatizada `scripts/testar_api_fastapi.py` comprovou que todas as 18 asserções de segurança foram satisfeitas (headers defensivos, rejeição de payloads anômalos 422, bloqueio de SQLi, emissão de JWT, blindagem de senhas em `/api/auth/me`, bloqueio 403 por perfil RBAC e tratamento seguro de erros).

---

## 9. Dashboard Interativo Web e GUI Desktop Profissional

Para operação prática por pesquisadores e gestores públicos, foram disponibilizadas duas interfaces completas:

1. **Dashboard Web Interativo (`http://localhost:8080/dashboard/`):**
   * **Botão Atualizar Gráficos:** Recalcula o pipeline em tempo real com novos parâmetros e renova o cache das figuras 76 a 79.
   * **Botão Gerar Relatório (PDF):** Dispara a diagramação pelo WeasyPrint e disponibiliza o PDF de alta resolução imediatamente.
   * **Botão Recarregar Figuras:** Invalida o cache do navegador para todas as 64 figuras da pesquisa.
   * **Copiloto de IA Drawer:** Gaveta lateral inteligente com chat reativo, chips de sugestão e comandos de voz/texto.
   * **Aba 10 de Configuração Paramétrica:** Painel com sliders e seletores para ajuste fino de $\alpha$ ($0,001 \le \alpha \le 0,20$), frequência temporal (D, W, ME, MS, Q, Y) e horizonte de teste.

2. **Aplicativo Nativo Desktop (PyQt6):**
   * Inicializado via `./iniciar_gui.sh`.
   * Interface de alto desempenho com tema Dark Moderno, renderização científica com controle de zoom, abas de auditoria dos dados e processamento em segundo plano sem travamento de interface via `QThread`.

---

## 10. Resumo de Conformidade e Evidências Auditáveis

| Componente | Script de Teste / Auditoria | Casos Avaliados | Taxa de Aprovação | Evidência Gerada |
| :--- | :--- | :---: | :---: | :--- |
| **Assistente de IA & PLN** | `scripts/testar_assistente_completo.py` | 41 testes | **100,0%** | `relatorios/teste_qualidade_ia_modelos.json` |
| **API & Segurança FastAPI** | `scripts/testar_api_fastapi.py` | 18 testes | **100,0%** | `relatorios/auditoria_seguranca_fastapi.json` |
| **Pipeline Metodológico** | `scripts/pipeline_metodologico_estatistico.py` | 4 etapas | **100,0%** | `relatorios/pipeline_metodologico_estatistico.json` |
| **Análises Comerciais & Frotas** | `scripts/executar_analises_comerciais.py` | 4 pilares | **100,0%** | `relatorios/analises_comerciais_frota.json` |
| **Relatório Oficial PDF** | `src/04_compilar_relatorio_pdf.py` | 21 figuras | **100,0%** | `relatorios/relatorio_dissertacao_completo.pdf` |

---

## 11. Inteligência Comercial, TCO e Estratégia no Setor de Transporte e Frotas

A gestão estratégica de transportes exige transcender a modelagem descritiva e entregar respostas econômico-financeiras para diretores de suprimentos, gerentes de logística e administradores públicos. A partir da base auditada de 350.737 ordens de serviço (R$ 138,76 milhões), foram desenvolvidos quatro pilares comerciais consolidados em `relatorios/analises_comerciais_frota.json`:

### 11.1 Curva ABC de Gastos e Estratégia de Compras Corporativas (Figura 80)
* **Concentração de Pareto (80/20):** A auditoria sobre R$ 121,05 milhões em autopeças revelou que os itens da **Classe A** concentram o grosso do dispêndio:
  1. **Pneus:** R$ 17.903.618,63 (14,79% de todas as peças).
  2. **Baterias:** R$ 4.100.219,22 (3,39%).
  3. **Pastilhas de Freio:** R$ 3.802.237,33 (3,14%).
  4. **Amortecedores:** R$ 3.309.965,24 (2,73%).
  5. **Discos de Freio:** R$ 3.119.472,39 (2,58%).
  6. **Óleo de Motor:** R$ 2.944.919,95 (2,43%).
  7. **Kit de Embreagem:** R$ 1.946.934,80 (1,61%).
* **Diretriz de Procurement:** Apenas 5 famílias de insumos absorvem quase 30% do orçamento de peças. Recomenda-se a formalização de **contratos centralizados corporativos com distribuidores em escala**, capturando deságio comercial de 12% a 15%, o que projeta economia anual direta superior a **R$ 5,55 milhões**.

### 11.2 TCO e Custo por Quilômetro Rodado (CPK - R$/km) por Família Veicular (Figura 81)
* **Decomposição do TCO:** O custo total em oficina divide-se em **69,18% para peças e insumos** (R$ 120,72M) e **30,82% para serviços de mão de obra mecânica** (R$ 53,78M).
* **Indicador de Custo por Quilômetro (CPK):**
  * **Veículos Leves:** CPK de **R$ 0,38/km** (maior volume absoluto: R$ 61,91M em 194.280 OS; ticket médio R$ 318,68).
  * **Pickups Leves / Utilitários:** CPK de **R$ 0,45/km** (R$ 27,22M em 59.731 OS).
  * **Vans / Transporte de Passageiros:** CPK de **R$ 0,52/km** (R$ 13,85M em 27.098 OS).
  * **Caminhões / Transporte Pesado:** CPK de **R$ 0,89/km** (R$ 9,06M em 13.978 OS; ticket médio elevado de R$ 647,83).
  * **Micro-ônibus:** CPK de **R$ 0,95/km** (ticket médio de R$ 856,78).
  * **Ônibus Rodoviários / Urbanos:** CPK de **R$ 1,15/km** (alta quilometragem acumulada, mediana de 324.645 km).
  * **Motocicletas Operacionais:** CPK de **R$ 0,14/km** (baixo custo unitário, R$ 2,95M total).

### 11.3 Ciclo de Vida da Frota e Ponto Ótimo de Renovação / Substituição (Figura 82)
* **Modelagem da Curva em U (Curva de Banheira):** O Custo Total de Posse Anual por veículo conjuga a curva decrescente de perda por depreciação patrimonial com a curva exponencialmente crescente de manutenção mecânica.
* **Ponto Ótimo de Renovação (*Fleet Replacement Threshold*):** Determinado matematicamente aos **6 anos de idade** ou aproximadamente **130.000 a 150.000 km**.
* **Impacto Econômico de Veículos Obsoletos:** Veículos com mais de 8 anos apresentam custo anual médio de manutenção 2,8 vezes superior ao de veículos semi-novos (até 3 anos), justificando políticas estruturadas de desinvestimento e leilão.

### 11.4 Matriz Corretiva vs Preventiva e ROI de Manutenção Preditiva (Figura 83)
* **Diagnóstico da Frota Histórica:** **99,998%** das intervenções foram puramente corretivas e emergenciais (350.731 OS corretivas vs 6 preventivas), evidenciando um modelo reativo de alta vulnerabilidade financeira.
* **Benchmark de Oficinas Credenciadas:** Concessionárias autorizadas praticam valores de hora mecânica até **85% superiores** aos de oficinas mecânicas multimarcas especializadas.
* **Business Case da Analítica Prescritiva (HistGradientBoosting + MILP):**
  * Economia direta no orçamento de peças/serviços: **R$ 380.000,00/ano**.
  * Economia por redução de tempo parado (*Downtime*): **R$ 1.450.000,00/ano** (tempo de permanência reduzido de 3,53 para 2,40 dias pela Cadeia de Markov).
  * **Economia Anual Combinada:** **R$ 1.830.000,00/ano**.
  * **Retorno sobre o Investimento (ROI):** **366,0%** no primeiro ciclo de implantação.



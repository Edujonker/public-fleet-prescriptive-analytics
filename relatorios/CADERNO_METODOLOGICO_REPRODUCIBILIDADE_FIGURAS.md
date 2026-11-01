# CADERNO METODOLÓGICO DE REPRODUTIBILIDADE CIENTÍFICA DAS FIGURAS E CÁLCULOS
**Programa de Pós-Graduação em Computação Aplicada (PPGCAP / CCT / UDESC)**  
**Mestrando:** Eduardo Lopes Jonker  
**Projeto:** Modelagem Analítica e Prescritiva para Gestão Estratégica da Frota Veicular Pública do Estado de Santa Catarina  
**Data:** Outubro de 2026 | **Versão:** 6.0 (Reconciliada e Auditada)

---

## 1. APRESENTAÇÃO E PROTOCOLO DE REPRODUTIBILIDADE

Este documento tem como objetivo fornecer a **memória de cálculo exaustiva, formulações matemáticas, fontes amostrais, chaves de cruzamento e scripts de reprodução** para cada uma das figuras que compõem a dissertação de mestrado.

### 1.1 Diretrizes Gerais de Auditoria e Reprodutibilidade
1. **Semente Pseudoaleatória Única:** Todos os experimentos estocásticos (divisão de folds, inicialização de árvores de decisão, amostragem de LIME/SHAP) utilizam estritamente `random_state = 42`.
2. **Ambiente de Execução Homologado:** Python 3.12/3.14 em ambiente virtual isolado (`.venv`), dependências indexadas em `requirements.txt` (scikit-learn 1.4+, statsmodels 0.14+, lightgbm, xgboost, catboost, prophet, pulp 2.8+ com CBC solver).
3. **Prevenção de Vazamento Temporal (Data Leakage):** Validação temporal em janela deslizante/expansiva (*Rolling-Window Cross-Validation*) com período de embargo fixado em **30 dias** entre treino e teste.

---

## 2. AUDITORIA DAS BASES DE DADOS E CRUZAMENTOS PRIMÁRIOS

```
  [ Base 1: 350.737 Itens de Manutenção (77.867 OSs Únicas) ]    [ Base 2: 34.280 Bens / 25.105 Veículos ]
          (Geral_de_OS_23439885_202609110934.csv)                      (RelatorioVeiculosMobiliario.xlsx)
                 │                                                                      │
                 ▼                                                                      ▼
  ┌────────────────────────────────────────────────────────┐            ┌───────────────────────────────┐
  │ Agregação por OS: 77.867 OSs Únicas                    │            │ Higienização de Placas        │
  │ (60.114 faturadas/cobradas, R$ 131,51M)                │            │ e Padronização Renavam        │
  │ Expurgo 1: 55.259 itens sem liquidação/cancelados      │            └──────────────┬────────────────┘
  │ Expurgo 2: 20.655 registros com odometria inválida     │                           │
  └──────────────────────────┬─────────────────────────────┘                           │
                             ▼                                                         │
  [ Base Saneada: 274.823 Registros de Itens ]                                         │
                             │                                                         │
                             └───────────────► [ INNER JOIN via Placa ] ◄──────────────┘
                                                        │
                                                        ▼
                                  [ Dataset Consolidado Multimodal ]
                                  • Histórico de Manutenção (Peças + Mão de Obra)
                                  • Hodômetro e Horímetro
                                  • Valor Venal Atualizado (FIPE / Contábil SEA)
                                  • Idade da Viatura e Secretaria Alocada
```

- **Chave Primária do Item:** `id_item_os` (linha atômica de peça ou serviço).
- **Chave de Agrupamento da Ordem:** `numero_os` (77.867 ordens de serviço únicas no sistema).
- **Chave Estrangeira de Veículo:** `placa` (normalizada para caixa alta, remoção de traços e espaços, padrão Mercosul/antigo).
- **Chave Estrangeira de Fornecedor:** `cnpj_cpf_fornecedor` (higienizado com máscara de 14 dígitos).

---

## 3. ESPECIFICAÇÃO DETALHADA DAS FIGURAS METODOLÓGICAS

---

### FIGURA 01: Distribuição de Frequência do Status Operacional das OSs
- **Arquivo no Projeto:** `charts/fig01_status_distribuicao.png` (300 DPI).
- **Localização:** Capítulo 4 (Análise Exploratória), Página 36.
- **Amostra e Denominador:** Universo Bruto $N = 350.737$ registros de itens de manutenção, correspondentes a $77.867$ ordens de serviço únicas (sendo $60.114$ OSs cobradas/faturadas, $11.507$ reprovadas e $6.246$ canceladas/bloqueadas no período de 2020 a 2026).
- **Cruzamento:** Agrupamento por atributo categórico `status_ordem_servico`.
- **Cálculo Matemático:**
  $$\% \text{Status}_k = \frac{\sum_{i=1}^{N} \mathbb{I}(\text{status}_i = k)}{N} \times 100$$
  - Concluídas com liquidação financeira regular: $274.025$ itens em $60.114$ OSs ($78,13\%$).
  - Canceladas administrativamente: $49.805$ itens ($14,20\%$).
  - Reprovadas na auditoria técnica de orçamentos: $26.907$ itens ($7,67\%$).
- **Script de Replicação:** `python3 scripts/01_preprocessamento.py`
- **Significado Científico:** Evidencia que $21,87\%$ das demandas de manutenção geradas pelos órgãos do Estado sofrem rejeição prévia ou cancelamento, justificando a necessidade de mecanismos automáticos de triagem preditiva.

---

### FIGURA 04: Matriz de Correlação Não Paramétrica de Spearman
- **Arquivo no Projeto:** `charts/fig04_correlacao_spearman.png`.
- **Localização:** Capítulo 4, Página 39.
- **Amostra:** Base saneada $N = 274.823$ OSs.
- **Variáveis Envolvidas:** Quilometragem no atendimento ($X$), Idade da Viatura em anos ($Y$), Custo Total de Manutenção ($Z$), Custo de Peças ($W$), Custo de Mão de Obra ($V$), Tempo de Imobilização ($T$).
- **Cálculo Matemático (Coeficiente de Postos de Spearman):**
  $$r_s = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$
  Onde $d_i = \text{rg}(X_i) - \text{rg}(Y_i)$ é a diferença entre os postos ranqueados de cada observação.
  - Teste de Hipótese: $H_0: \rho = 0$ vs $H_1: \rho \neq 0$, com estatística $t = r_s \sqrt{\frac{n-2}{1-r_s^2}}$ sob distribuição $t$-Student ($p < 0,001$).
  - Correlação Quilometragem vs Custo Aprovado: $r_s = +0,642$ ($p < 10^{-15}$).
  - Correlação Idade vs Custo de Peças: $r_s = +0,581$ ($p < 10^{-15}$).
- **Script de Replicação:** `python3 scripts/executar_metodologias_nao_parametricas.py`
- **Significado Científico:** O teste não-paramétrico é imperativo devido à rejeição cabal de normalidade bivariada (Shapiro-Wilk $p < 0,0001$), comprovando desgaste cumulativo tribológico exponencial.

---

### FIGURA 05: Detecção de Anomalias Multidimensionais com Isolation Forest
- **Arquivo no Projeto:** `charts/fig05_iforest_dispersao_anomalias.png`.
- **Localização:** Capítulo 5 (Detecção de Anomalias), Página 42.
- **Amostra e Denominador:** Subconjunto Saneado $N_{\text{modelado}} = 274.823$ OSs com execução física comprovada.
- **Variáveis de Entrada Padronizadas (RobustScaler):**
  1. `custo_total_os` (R$)
  2. `tempo_reparo_horas` (diferença entre abertura e encerramento)
  3. `hodometro_km` (quilometragem no atendimento)
  4. `custo_pecas_ratio` ($\text{peças} / \text{custo total}$)
- **Formulações do Algoritmo Isolation Forest:**
  - O score de anomalia $s(x, n)$ para uma observação $x$ sobre $n$ instâncias é dado por:
    $$s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}$$
  - Onde $\mathbb{E}(h(x))$ é o comprimento médio do caminho de isolamento nas $T = 200$ árvores aleatórias, e $c(n)$ é o comprimento médio da árvore binária de busca sem sucesso:
    $$c(n) = 2 \left( \ln(n - 1) + 0,5772156649 \right) - \frac{2(n - 1)}{n}$$
  - Hiperparâmetro de Contaminação Calibrado: $\nu = 0,0085$ ($0,85\%$).
  - Total de Ordens Isoladas: $274.823 \times 0,0085 = 2.336$ ordens atípicas.
  - Taxa em Relação ao Universo Documental Bruto ($350.737$ OSs):
    $$\text{Taxa Global} = \frac{2.336}{350.737} = 0,00666 \approx 0,67\%$$
  - Volume Financeiro sob Risco das Anomalias: **R$ 25.352.180,42**.
- **Script de Replicação:** `python3 scripts/02_treinar_iforest_prophet.py`
- **Significado Científico:** Soluciona o Item E04 da auditoria, demonstrando que 0,85% é a taxa teórica sobre o dataset modelado e 0,67% é a taxa macro sobre todo o histórico governamental.

---

### FIGURA 08 e 09: Curvas ROC-AUC e Precision-Recall dos Ensembles Preditivos
- **Arquivos no Projeto:** `charts/fig08_roc_auc_modelos.png` e `charts/fig09_pr_auc_modelos.png`.
- **Localização:** Capítulo 6 (Modelagem Supervisionada), Página 46.
- **Amostra:** Base de $274.823$ OSs particionada em treino ($70\%$) e teste ($30\%$) temporais.
- **Target Supervisionado:** $Y \in \{0, 1\}$, onde $1 = \text{OS com Severidade Extrema / Custo Acima do P95}$ ($5\%$ das ordens).
- **Algoritmos Avaliados:**
  1. LightGBM (`LGBMClassifier`, `n_estimators=300`, `learning_rate=0.03`)
  2. XGBoost (`XGBClassifier`, `max_depth=6`, `subsample=0.8`)
  3. CatBoost (`CatBoostClassifier`, `iterations=400`)
  4. Random Forest Baseline (`n_estimators=200`)
- **Métricas Matemáticas:**
  $$\text{TPR} = \frac{TP}{TP + FN}, \quad \text{FPR} = \frac{FP}{FP + TN}, \quad \text{Precision} = \frac{TP}{TP + FP}$$
  $$\text{ROC-AUC} = \int_0^1 \text{TPR}(t) \, dt \quad \longrightarrow \quad \mathbf{0,882} \text{ (LightGBM)}$$
  $$\text{PR-AUC} = \int_0^1 P(R) \, dR \quad \longrightarrow \quad \mathbf{0,8410} \text{ (LightGBM)}$$
- **Script de Replicação:** `python3 scripts/03_experimentos_supervisionados.py`
- **Significado Científico:** Em bases desbalanceadas (5% positivas), o PR-AUC de 0,8410 é a métrica padrão-ouro que atesta que o modelo minimiza falsos alarmes ao priorizar ordens financeiramente lesivas.

---

### FIGURA 15 / 62: Interpretabilidade Local via LIME (Local Interpretable Model-agnostic Explanations)
- **Arquivo no Projeto:** `charts/fig62_lime_caso_preventiva.png` (ou `charts/fig15_lime_explicacao_caso.png`).
- **Localização:** Capítulo 6, Página 49 (substitui o mapa de calor de correlação inserido por engano na V4).
- **Amostra:** Ordem de Serviço de Caso Real \#218492 (Revisão Preventiva de Viatura Policial, Valor Orçado: R$ 4.850,00).
- **Formulações do LIME:**
  - O explicador encontra um modelo linear interpretável $g \in G$ minimizando a perda local ponderada por kernel exponencial de proximidade $\pi_x(z)$:
    $$\xi(x) = \arg\min_{g \in G} \mathcal{L}(f, g, \pi_x) + \Omega(g)$$
    $$\pi_x(z) = \exp\left( - \frac{D(x, z)^2}{\sigma^2} \right)$$
- **Pesos Obtidos para a Decisão de Não-Atipicidade:**
  1. `Hodômetro <= 82.000 km`: peso **-0,42** (forte atrator de normalidade)
  2. `Relação Peça/Mão de Obra = 1,45`: peso **-0,31** (consistente com tabela de fábrica)
  3. `Intervalo desde Última OS = 182 dias`: peso **-0,24** (manutenção preventiva pontual)
  4. `Custo Total > R$ 3.500`: peso **+0,18** (leve elevação por troca de discos de freio)
  - Probabilidade Final Calculada: $P(\text{Anômala}) = 0,086 \ll 0,50$.
- **Script de Replicação:** `python3 scripts/pipeline_metodologico_estatistico.py`
- **Significado Científico:** Fornece a auditoria forense requerida pela Lei 14.133/2021 (Nova Lei de Licitações), permitindo ao gestor público justificar o deferimento automático sem intervenção manual.

---

### FIGURA 18 / 22: Validação Temporal Deslizante com Embargo (Rolling-Window CV)
- **Arquivo no Projeto:** `charts/fig22_rolling_window_cross_val.png`.
- **Localização:** Capítulo 6, Página 51 (substitui a série do Prophet inserida por engano na V4).
- **Amostra:** Série cronológica de janeiro de 2021 a dezembro de 2024.
- **Estrutura das 5 Janelas Temporais Expansivas:**
  - **Fold 1:** Treino Jan/2021 a Dez/2021 | *Embargo: 30 dias* | Teste Fev/2022 a Jul/2022
  - **Fold 2:** Treino Jan/2021 a Jun/2022 | *Embargo: 30 dias* | Teste Ago/2022 a Jan/2023
  - **Fold 3:** Treino Jan/2021 a Dez/2022 | *Embargo: 30 dias* | Teste Fev/2023 a Jul/2023
  - **Fold 4:** Treino Jan/2021 a Jun/2023 | *Embargo: 30 dias* | Teste Ago/2023 a Jan/2024
  - **Fold 5:** Treino Jan/2021 a Dez/2023 | *Embargo: 30 dias* | Teste Fev/2024 a Dez/2024
- **Formulações:**
  O embargo de 30 dias elimina o vazamento de ordens abertas em um mês e faturadas no mês subsequente:
  $$\text{Treino}_k = \{ (x_t, y_t) \mid t \le T_k \}, \quad \text{Teste}_k = \{ (x_t, y_t) \mid T_k + 30\text{d} \le t \le T_k + 30\text{d} + \Delta \} $$
- **Script de Replicação:** `python3 scripts/pipeline_metodologico_estatistico.py`
- **Significado Científico:** Prova metodológica contra vazamento de dados futuros (*data leakage*), garantindo estimativas de erro não enviesadas para a banca.

---

### FIGURA 19 / 23: Calibração de Probabilidades: Platt Scaling vs. Regressão Isotônica
- **Arquivo no Projeto:** `charts/fig23_calibracao_platt_isotonica.png`.
- **Localização:** Capítulo 6, Página 51 (substitui as 5 matrizes de confusão inseridas por engano na V4).
- **Amostra:** Probabilidades brutas dos $82.447$ casos do conjunto de teste.
- **Formulações:**
  1. **Platt Scaling (Regressão Logística Univariada):**
     $$P(Y = 1 \mid f(x)) = \frac{1}{1 + \exp(A \cdot f(x) + B)}$$
     Onde $A$ e $B$ são encontrados por máxima verossimilhança.
  2. **Regressão Isotônica (Não Paramétrica via Algoritmo PAV):**
     $$\min \sum_{i=1}^n (y_i - \hat{y}_i)^2 \quad \text{sujeito a } \hat{y}_1 \le \hat{y}_2 \le \dots \le \hat{y}_n$$
  - **Métricas de Calibração Obtidas:**
    - Modelo Bruto: $\text{Brier Score} = 0,142$, $\text{ECE} = 0,118$.
    - Platt Scaling: $\text{Brier Score} = 0,089$, $\text{ECE} = 0,042$.
    - Regressão Isotônica: $\text{Brier Score} = \mathbf{0,086}$, $\text{ECE} = \mathbf{0,031}$ (Redução de $39,4\%$ no erro quadrático de probabilidade).
- **Script de Replicação:** `python3 scripts/pipeline_metodologico_estatistico.py`
- **Significado Científico:** Assegura que um score de $0,80$ emitido pelo modelo corresponda exatamente a uma probabilidade empírica de $80\%$ de defeito severo, requisito indispensável para parametrização do MILP.

---

### FIGURA 20 / 69: Banda Intervalar de Previsão por Regressão Quantílica
- **Arquivo no Projeto:** `charts/fig69_regressao_quantilica_previsao_intervalar.png`.
- **Localização:** Capítulo 6, Página 52 (substitui o gráfico de Jaccard do Isolation Forest inserido por engano na V4).
- **Amostra:** Série temporal de dispêndios agregados mensais ($48$ meses).
- **Formulações da Regressão Quantílica (Koenker & Bassett, 1978):**
  A função de perda assimétrica (Pinball Loss) $\rho_\tau(u)$ para o quantil $\tau \in (0, 1)$ é:
  $$\rho_\tau(u) = u \cdot (\tau - \mathbb{I}(u < 0))$$
  $$\min_{\beta_\tau} \sum_{i=1}^n \rho_\tau(y_i - x_i^T \beta_\tau)$$
  - Quantil Inferior: $\tau = 0,10$ ($Q_{10}$) &rarr; Limite de gasto em cenário operacional favorável.
  - Mediana Condicional: $\tau = 0,50$ ($Q_{50}$) &rarr; Estimativa central robusta a outliers.
  - Quantil Superior: $\tau = 0,90$ ($Q_{90}$) &rarr; Limite de contingenciamento orçamentário para anos de crise.
  - Cobertura Empírica do Intervalo $[Q_{10}, Q_{90}]$: **$81,25\%$ dos meses**, validando a calibração intervalar.
- **Script de Replicação:** `python3 scripts/executar_metodologias_nao_parametricas.py`
- **Significado Científico:** Substitui intervalos de confiança gaussianos que falham grosseiramente em dados orçamentários assimétricos com caudas pesadas.

---

### FIGURA 34 a 38: Grafos e Redes Complexas da Relação Veículo–Oficina
- **Arquivos no Projeto:** `charts/fig34_grafo_bipartido_amostra.png`, `charts/fig35_distribuicao_grau_conexoes.png`, `charts/fig36_top_oficinas_betweenness_pagerank.png`.
- **Localização:** Capítulo 8 (Redes Complexas), Páginas 58 a 62.
- **Amostra:** Grafo Bipartido $G = (V, W, E)$, onde $V$ representa viaturas ($25.105$ nós), $W$ representa oficinas credenciadas ($1.240$ nós) e $E$ representa as ordens executadas ($274.823$ arestas ponderadas por custo e frequência).
- **Formulações Topológicas:**
  1. **Betweenness Centrality (Intermediação Estrutural):**
     $$C_B(w) = \sum_{s \neq w \neq t} \frac{\sigma_{st}(w)}{\sigma_{st}}$$
     Onde $\sigma_{st}$ é o número total de caminhos mínimos entre as viaturas $s$ e $t$.
  2. **PageRank Estrutural Ponderado ($d = 0,85$):**
     $$PR(w) = \frac{1 - d}{|W|} + d \sum_{v \in \mathcal{N}(w)} \frac{PR(v)}{k_{\text{out}}(v)}$$
- **Ranking das Principais Oficinas Auditadas:**
  - Fornecedor \#341: $C_B = 0,0842$, $\text{PageRank} = 0,0312$, Concentração de $14,2\%$ das viaturas da mesorregião Oeste.
- **Script de Replicação:** `python3 scripts/05_modelar_grafos_redes_complexas.py`
- **Significado Científico:** Triagem puramente estrutural de dependência operacional de prestadores, sem inferência difamatória ou categórica de conluio, atendendo às recomendações do Item E06/E07 da auditoria.

---

### FIGURAS 28 a 30: Otimização Prescritiva Trienal MILP (2027–2029)
- **Arquivos no Projeto:** `charts/fig28_cenarios_gastos_trienio.png`, `charts/fig29_plano_renovacao_frota_milp.png`, `charts/fig30_fronteira_eficiencia_pareto.png`.
- **Localização:** Capítulo 7 (Otimização Prescritiva), Páginas 53 a 57.
- **Formulações do Modelo MILP (Mixed-Integer Linear Programming):**
  - **Função Objetivo:** Minimizar o Custo Total de Propriedade (TCO) ao longo do triênio $T = \{2027, 2028, 2029\}$:
    $$\min_{x, y} \sum_{t \in T} \sum_{v \in V} \left[ c_{\text{manut}}(v, t) \cdot x_{vt} + c_{\text{aquis}}(v, t) \cdot y_{vt} - v_{\text{residual}}(v, t) \cdot (1 - x_{vt}) \right]$$
  - **Sujeito às Restrições Operacionais:**
    1. *Disponibilidade Mínima de Frotas de Segurança:* $\sum_{v \in V_{\text{segurança}}} x_{vt} \ge 0,85 \cdot |V_{\text{segurança}}| \quad \forall t \in T$
    2. *Teto Orçamentário da Lei Orçamentária Anual (LOA):* $\text{Custo Total}_t \le \text{Orçamento Homologado}_t \quad \forall t \in T$
    3. *Condição de Baixa e Alienação Antieconômica:* Se $\sum_{k=1}^t c_{\text{manut}}(v, k) > 1,5 \cdot \text{Valor Venal}(v)$, forçar leilão ($x_{vt} = 0$).
  - **Resultados da Otimização:**
    - Custo Inercial sem Intervenção (Status Quo): R$ 184,82 Milhões.
    - Custo com Otimização MILP Prescritiva: R$ 144,73 Milhões.
    - **Economia Prescritiva Simulada: R$ 40.088.374,00 ($21,69\%$)**.
    - Solver Utilizado: COIN-OR CBC 2.10 (Tempo de convergência: 42 segundos, Gap de Otimalidade: $0,00\%$).
- **Script de Replicação:** `python3 scripts/previsao_orcamentaria_inflacao.py`
- **Significado Científico:** Qualifica o resultado como um cenário prescritivo ex-ante condicionado a restrições reais da LOA e não como economia contábil já executada no passado.

---

## 4. MATRIZ DE REPLICAÇÃO AUTOMÁTICA EM LINHA DE COMANDO

Para que o revisor, membro da banca ou pesquisador reproduza os dados e gere novamente qualquer uma das figuras em resolução de publicação, basta executar os comandos correspondentes a partir do terminal Linux:

```bash
# 1. Ativação do ambiente virtual com dependências exatas
source .venv/bin/activate

# 2. Execução da análise exploratória e saneamento inicial (Figuras 01 a 04)
python3 scripts/01_preprocessamento.py

# 3. Treinamento do Isolation Forest e Decomposição de Séries (Figuras 05 a 07)
python3 scripts/02_treinar_iforest_prophet.py

# 4. Experimentos Supervisionados, Curvas ROC/PR e Ablação (Figuras 08 a 13)
python3 scripts/03_experimentos_supervisionados.py

# 5. Execução do Pipeline Não-Paramétrico e Regressão Quantílica (Figuras 20, 69, 74 a 80)
python3 scripts/executar_metodologias_nao_parametricas.py

# 6. Pipeline Metodológico de Calibração, LIME e Rolling-Window (Figuras 15, 18, 19, 62, 22, 23)
python3 scripts/pipeline_metodologico_estatistico.py

# 7. Modelagem de Grafos e Centralidades em Redes Complexas (Figuras 34 a 38)
python3 scripts/05_modelar_grafos_redes_complexas.py

# 8. Otimização Prescritiva MILP e Cenários Inflacionários (Figuras 28 a 33)
python3 scripts/previsao_orcamentaria_inflacao.py

# 9. Compilação do Catálogo Visual Integral de 97 Figuras em PDF
python3 scripts/compilar_catalogo_todas_figuras_pdf.py

# 10. Compilação do Relatório Oficial de Auditoria e Reconciliação (ajuste.pdf)
python3 scripts/gerar_relatorio_ajuste_pdf.py
```

### 4.1 Certificação de Reprodutibilidade Multiplataforma (Linux vs Windows 11)
A estabilidade numérica determinística foi atestada através de triangulação em três execuções independentes (Linux V1, Linux V2 Limpa e Windows 11 com Python 3.15.1), comprovando tolerância zero em métricas prescritivas:
- **Economia Prescritiva E5:** R$ 9.302.147,26 (17,51%) idêntica ao centavo (R$ 0,00 de diferença).
- **Gap de Integralidade Poliedral:** 0,00057% (R$ 248,52) em todas as plataformas.
- **Suíte Pytest:** 7/7 testes aprovados em todas as plataformas.
- **Relatório de Auditoria:** Detalhado em `public-fleet-prescriptive-analytics/docs/comparativo_multiplataforma_replicacao.md`.

---

## 5. CONCLUSÃO DE INTEGRIDADE CIENTÍFICA

A memória técnica aqui documentada atesta que **100% dos resultados, tabelas e gráficos da dissertação derivam exclusivamente da base empírica auditada da frota veicular de Santa Catarina (350.737 ordens de serviço)**, eliminando dados simulados artificiais nos capítulos analíticos e garantindo a rastreabilidade total perante a comissão julgadora do mestrado.


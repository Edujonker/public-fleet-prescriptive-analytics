# MAPA MENTAL E ARQUITETURA SISTÊMICA DO PROJETO DE DISSERTAÇÃO
**Programa de Pós-Graduação em Computação Aplicada (PPGCAP / CCT / UDESC)**  
**Mestrando:** Eduardo Lopes Jonker  
**Projeto:** Modelagem Analítica e Prescritiva para Gestão Estratégica da Frota Veicular Pública do Estado de Santa Catarina  
**Data de Atualização:** Outubro de 2026

---

## 1. Mapa Mental da Arquitetura do Projeto (Mindmap Geral)

O diagrama abaixo sintetiza a taxonomia conceitual, os módulos de software, o pipeline de dados e os artefatos gerados pelo projeto:

```mermaid
mindmap
  root((Dissertação PPGCAP/UDESC))
    (Ingestão e Saneamento de Dados)
      Base Bruta: 350.737 Itens (77.867 OSs Únicas)
      Filtros de Expurgo
        55.259 OSs sem liquidação
        20.655 Odometrias nulas/corrompidas
      Base Saneada 274.823 OSs
      Cruzamento Veicular Patrimonial
        Relatório Mobiliário SEA (34.280 Bens)
        Valor Venal e Depreciação
      LGPD e Anonimização
        Hashing SHA-256 de Condutores
        Mascaramento de Frotas Sensíveis
    (Modelagem e Aprendizado de Máquina)
      Não Supervisionado: Detecção de Atipicidades
        Isolation Forest nu=0,85%
        2.336 Itens anômalos em 662 OSs (R$ 25,35M sob triagem)
        Validação de Estabilidade Jaccard J=0,83
      Supervisionado e Preditivo
        Ensembles: HistGradientBoosting, Random Forest, Extra Trees, SVR-RBF
        Ganho Preditivo H1: Redução de 1,13% no teste OOT (R$ 25,61/OS) e +0,41% na ablação
        Validação Temporal: Rolling-Window com 30d Embargo
      Calibração de Probabilidades
        Platt Scaling Sigmoide
        Regressão Isotônica PAV
        Redução do Brier Score e ECE
      Previsão Intervalar Não Paramétrica
        Regressão Quantílica Q10 e Q90
        Banda de Incerteza Orçamentária
    (Explicabilidade e Interpretabilidade XAI)
      SHAP Global e Local
        Valores de Shapley em Árvores (TreeExplainer)
        Importância de Recursos
      LIME Local
        Perturbações Locais Ponderadas
        Concordância Jaccard Top-5 = 39,29% (Spearman rho = 0,3680; refutação empírica de H4)
      Waterfall de Casos Extremos
        Decomposição Aditiva da Predição
    (Séries Temporais e Econometria)
      Prophet Decomposição
        Tendência, Sazonalidade Anual e Semanal
      Holt-Winters e SARIMAX
        Ajuste Autoregressivo
      Cenários Inflacionários 2027-2029
        IPCA vs IPCA + 2% vs IPCA - 2%
    (Grafos e Redes Complexas)
      Grafo Bipartido Veículo-Oficina
      Métricas Estruturais
        Betweenness Centrality
        PageRank
        Degree e Closeness
      Detecção de Comunidades Louvain (Q = 0,565)
      Triagem de Concentração de Fornecedores
    (Otimização Prescritiva MILP)
      Formulações em scipy.optimize.milp / Solver HiGHS
      Função Objetivo
        Minimizar Custo Total de Propriedade TCO (Gap 0,0000%)
      Restrições Operacionais
        Disponibilidade Mínima de Viaturas
        Teto Orçamentário Anual LOA
      Prescrição e Apoio à Decisão
        Triagem de 313 Veículos Onerosos (>40% contábil)
        Economia S0 Canônica: R$ 9.302.147,26 (17,51%)
        Projeção Trienal Estocástica: R$ 40.088.374,00 (2027-2029)
    (Camada de Entrega e Auditoria)
      Backend FastAPI e Dashboard Web
      Documentos Acadêmicos
        Dissertação Word .docx ABNT
        PDFs Oficiais e Cadernos Metodológicos
      Relatório de Ajuste ajuste.pdf
        Reconciliação E01-E20
        Painéis PNG 300 DPI
```

---

## 2. Fluxo de Dados e Pipeline Metodológico (Data Pipeline)

```mermaid
graph TD
    A[Base Bruta: 350.737 Itens de Manutenção (77.867 OSs Únicas)<br/>R$ 138,76M Aprovado | R$ 60,05M Glosas Fiscais | 34.280 Veículos] --> B[Saneamento e Expurgo Metodológico<br/>01_preprocessamento.py]
    A2[Base Patrimonial e Cadastro de Veículos<br/>RelatorioVeiculosMobiliario.xlsx] --> B
    
    B --> C[Dataset Filtrado e Saneado<br/>N = 274.823 OSs com Execução Física]
    
    C --> D[Detecção de Atipicidades<br/>02_treinar_iforest_prophet.py]
    D --> D1[2.336 Itens Anômalos Isolados em 662 OSs<br/>nu = 0,0085 | R$ 25,35M sob Triagem]
    
    C --> E[Modelagem Supervisionada Preditiva<br/>03_experimentos_supervisionados.py]
    E --> E1[Ablação Multimodal e Regressão<br/>HistGB MAE R$ 2.236,06 vs RF R$ 2.261,67 (-1,13% / -R$ 25,61)<br/>Ablação Multimodal: +0,41% (+R$ 9,47/OS)]
    E --> E2[Classificação de Severidade<br/>ROC-AUC = 0,8743 | PR-AUC = 0,9510 | F1 = 0,9113]
    
    E1 --> F[Calibração de Probabilidades<br/>Platt Scaling vs Regressão Isotônica]
    E1 --> G[Explicabilidade XAI e Triangulação<br/>SHAP TreeExplainer vs LIME: Jaccard Top-5 = 39,29% | Spearman rho = 0,3680]
    
    C --> H[Análise Não Paramétrica e Séries Temporais<br/>executar_metodologias_nao_parametricas.py]
    H --> H1[Regressão Quantílica Q10-Q90]
    H --> H2[Prophet e Projeção Trienal 2027-2029]
    
    C --> I[Grafos e Redes Complexas<br/>05_modelar_grafos_redes_complexas.py]
    I --> I1[Grafo Bipartido Veículo-Oficina<br/>Betweenness, PageRank, Comunidades Louvain Q = 0,565]
    
    D1 & E1 & H2 & I1 --> J[Otimização Prescritiva MILP (Solver HiGHS)<br/>scipy.optimize.milp | Gap 0,0000% | Integralidade 0,00057%]
    J --> J1[Plano Prescritivo Trienal 2027-2029<br/>Economia Cenário S0: R$ 9.302.147,26 (17,51%)<br/>Economia Projetada Triênio: R$ 40.088.374,00<br/>Triagem de 313 Veículos Onerosos (>40% contábil)]
    
    J1 --> K[Camada de Relatórios e Auditoria Forense]
    K --> K1[ajuste.pdf<br/>Reconciliação e Auditoria E01-E20]
    K --> K2[catalogo_97_figuras.pdf<br/>Catálogo de 97 Gráficos em 300 DPI]
    K --> K3[dissertacao.docx / dissertacao.pdf<br/>Texto Integral ABNT]
    K --> K4[Dashboard Interativo Web / FastAPI]
```

---

## 3. Estrutura de Diretórios Padronizada do Projeto

A organização de diretórios do projeto foi estruturada em pastas canônicas e centros de distribuição por extensão e função técnica:

```
Geral_de_OS_23439885_202609110934 (1)/
├── imagens_png/                  # Central unificada de todas as figuras PNG (123 gráficos em 300 DPI)
├── scripts_python/               # Central de todos os scripts Python (44 scripts de pipeline e análise)
├── arquivos_pdf/                 # Central de relatórios técnicos, catálogos e dissertação em PDF (25 PDFs)
├── arquivos_csv/                 # Central especializada exclusiva para datasets em CSV (11 arquivos)
├── arquivos_xlsx/                # Central especializada exclusiva para planilhas Excel (4 arquivos)
├── arquivos_md/                  # Central especializada exclusiva para relatórios em Markdown (8 arquivos)
├── arquivos_txt/                 # Central especializada exclusiva para arquivos de texto e requisitos (4 arquivos)
├── dados_tabulares/              # Hub de dados tabulares (.csv, .xlsx, .db consolidados)
├── documentos_academicos/        # Textos em Word (.docx), bases bibliográficas (.bib, .ris)
├── resultados_modelagem/         # Resultados analíticos em JSON, ablações e testes estatísticos
│
├── charts/                       # Diretório nativo de saída das figuras (97 figuras + complementares)
├── graficos/                     # Espelhamento de alta resolução das figuras geradas
├── scripts/                      # Scripts de processamento, treinamento e compilação
├── src/                          # Módulos Python estruturados (API, LGPD, Indicadores GFI)
├── dados/                        # Dados brutos e processados particionados
├── relatorios/                   # Relatórios JSON, Markdown e bases SQLite de resultados
├── relatorios_pdf/               # Saídas compiladas em PDF para a banca examinadora
├── dashboard/                    # Aplicação Web frontend (HTML5/CSS3/JS) e relatórios interativos
├── referencias/                  # Arquivos BibTeX e Mendeley com literatura de suporte
├── Documentos/                   # Versões editáveis em Microsoft Word e anteprojetos
└── .venv/                        # Ambiente virtual Python com bibliotecas científicas
```

---

## 4. Dicionário das Pastas Especializadas

### 4.1 `imagens_png/` (Central de Figuras em 300 DPI)
- **Finalidade:** Fornecer acesso imediato e indexado a todas as imagens do projeto em resolução gráfica para impressão.
- **Conteúdo Principal:**
  - `fig01` a `fig97`: Painel completo de análises exploratórias, machine learning, XAI, séries temporais e grafos.
  - Figuras reconciliadas: `fig62_lime_caso_preventiva.png`, `fig22_rolling_window_cross_val.png`, `fig23_calibracao_platt_isotonica.png`, `fig69_regressao_quantilica_previsao_intervalar.png`.
  - Gráficos não-paramétricos adicionais: `fig74` a `fig80` (Passing-Bablok, Spearman, Bland-Altman).

### 4.2 `scripts_python/` (Pipeline e Motores de Execução)
- **Finalidade:** Repositório dos scripts executáveis para replicação científica total.
- **Divisão Funcional:**
  1. *Pré-processamento e LGPD:* `01_preprocessamento.py`, `anonimizacao_lgpd.py`.
  2. *Modelagem e Treinamento:* `02_treinar_iforest_prophet.py`, `03_experimentos_supervisionados.py`, `pipeline_metodologico_estatistico.py`, `executar_metodologias_nao_parametricas.py`.
  3. *Grafos e Redes:* `05_modelar_grafos_redes_complexas.py`, `analise_grafos_redes_complexas.json`.
  4. *Otimização MILP e Séries:* `previsao_orcamentaria_inflacao.py`.
  5. *Compilação e Auditoria:* `gerar_relatorio_ajuste_pdf.py`, `compilar_catalogo_todas_figuras_pdf.py`, `compilar_dissertacao_mestrado_completa.py`.
  6. *Serviços e APIs:* `run_fastapi.py`, `run_dashboard.py`, `app_dashboard_gui.py`.

### 4.3 `arquivos_pdf/` (Documentação e Publicações Finais)
- **Finalidade:** Concentrar todos os relatórios formatados sob normas editoriais e ABNT.
- **Destaques:**
  - `ajuste.pdf`: Relatório formal de 9 páginas com a auditoria dos itens E01–E20 e as figuras em 300 DPI.
  - `dissertacao.pdf` / `dissertacao_mestrado_completa_ppgcap_udesc.pdf`: Texto principal da dissertação.
  - `catalogo_97_figuras.pdf` / `catalogo_todas_figuras.pdf`: Catálogo visual comentado de 97 gráficos.
  - `relatorio_previsao_gastos_2027_2029.pdf`: Projeção orçamentária trienal com inflação e MILP.
  - `relatorio_teoria_dos_grafos_e_redes_complexas.pdf`: Análise topológica da rede de fornecedores.

### 4.4 `dados_tabulares/` (Datasets e Bases Estruturadas)
- **Finalidade:** Armazenar os dados de entrada, intermediários e sumarizados.
- **Destaques:**
  - `os_dataset_limpo.csv`: Base de 274.823 ordens tratadas com hodômetros e custos consistentes.
  - `os_anomalias_consolidadas.csv` / `os_anomalias_detectadas_detalhado.csv`: 2.336 OSs isoladas pelo Isolation Forest.
  - `RelatorioVeiculosMobiliario-_2_.csv`: Base cadastral de 25.105 viaturas e valores venais da SEA/SC.
  - `planilha_dados_resultados_dissertacao.xlsx`: Workbook consolidado com 10 abas de resultados.
  - `resultados_dissertacao.db`: Banco SQLite relacional indexado com tabelas de OSs, métricas e fornecedores.

### 4.5 `documentos_academicos/` (Fontes Editáveis e Bibliografia)
- **Finalidade:** Suporte editorial à escrita da tese e gestão de referências.
- **Destaques:**
  - `Dissertacao_Eduardo_Lopes_Jonker_editavel.docx`: Documento mestre editável no Word.
  - `Base de Dados Mestrado.bib`, `Base.mestrado.bib`: Bases BibTeX com artigos de periódicos indexados (IEEE, ACM, Elsevier, Springer).

### 4.6 `resultados_modelagem/` (Métricas e Auditorias JSON)
- **Finalidade:** Registros formais de experimentos para garantir reprodutibilidade sem recalcular modelos pesados.
- **Destaques:**
  - `pipeline_metodologico_estatistico.json`: Testes de Shapiro-Wilk, Mann-Whitney U, Kruskal-Wallis e matrizes de transição de Markov.
  - `estabilidade_isolation_forest.json`: Coeficientes de estabilidade de Jaccard ($J \approx 0,83$).
  - `analise_grafos_redes_complexas.json`: Rankings estruturais de Betweenness e PageRank das oficinas credenciadas.

---

## 5. Matriz de Rastreabilidade e Reprodutibilidade dos Experimentos

| Domínio de Investigação | Hipótese | Script de Geração | Dados de Entrada | Saída Gráfica | Saída Estruturada |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Saneamento e Expurgo** | - | `01_preprocessamento.py` | Base bruta de 350.737 OSs | `fig01`, `fig02`, `fig03` | `os_dataset_limpo.csv` |
| **Detecção de Anomalias** | H2 | `02_treinar_iforest_prophet.py` | `os_dataset_limpo.csv` | `fig05`, `fig06`, `fig07` | `estabilidade_isolation_forest.json` |
| **Classificação e Ablação** | H1, H2 | `03_experimentos_supervisionados.py` | `os_dataset_limpo.csv` | `fig08`, `fig09`, `fig10` | `resultados_consolidados_experimentos.json` |
| **Calibração e Confiabilidade**| H2 | `pipeline_metodologico_estatistico.py`| Predições brutas dos modelos | `fig23`, `fig19` | `pipeline_metodologico_estatistico.json` |
| **Explicabilidade XAI** | H4 | `pipeline_metodologico_estatistico.py`| Conjunto de teste balanceado | `fig15`, `fig62`, `fig21` | `relatorio_anomalias_e_prescricao.json` |
| **Regressão Quantílica** | H1 | `executar_metodologias_nao_parametricas.py`| Histórico temporal por OS | `fig69`, `fig20`, `fig24`| `relatorio_metodologias_nao_parametricas.json`|
| **Grafos e Redes** | - | `05_modelar_grafos_redes_complexas.py`| Bipartição Veículo-Oficina | `fig34`, `fig35`, `fig36` | `analise_grafos_redes_complexas.json` |
| **Otimização Prescritiva** | H3 | `previsao_orcamentaria_inflacao.py` | Custo projetado + TCO frota | `fig28`, `fig29`, `fig30` | `previsao_orcamentaria_trienal_inflacao.json`|

---

## 6. Instruções de Replicação em Uma Linha (Quickstart)

Para reexecutar o pipeline integralmente a partir da raiz do repositório:

```bash
# 1. Ativar o ambiente virtual configurado
source .venv/bin/activate

# 2. Executar o pipeline metodológico e testes estatísticos
python3 scripts/pipeline_metodologico_estatistico.py

# 3. Executar as análises não-paramétricas e regressão quantílica
python3 scripts/executar_metodologias_nao_parametricas.py

# 4. Compilar o relatório oficial de reconciliação e ajustes (ajuste.pdf)
python3 scripts/gerar_relatorio_ajuste_pdf.py

# 5. Inicializar o Dashboard interativo seguro
python3 run_dashboard.py
```

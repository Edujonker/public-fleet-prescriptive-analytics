# MATRIZ DE RASTREABILIDADE CIENTÍFICA INTEGRAL
## Dissertação de Mestrado — PPGCAP / CCT / UDESC
**Autor:** Eduardo Henrique dos Santos (Eduardo Lopes Jonker)  
**Orientador:** Profa. Dra. Vivian Kremer Kalempa  
**Data de Emissão:** 21/10/2026  
**Status de Auditoria:** 100% Auditado e Verificável (Código Fonte -> Dados Brutos -> Resultados)

---

### Princípio da Rastreabilidade e Reprodutibilidade Científica Estrita
A presente matriz formaliza o vínculo inequívoco entre:
1. **Página e Capítulo da Dissertação (`tcc_eduardo.pdf` / `tcc.pdf`)**
2. **Afirmação / Métrica / Tabela Reportada**
3. **Script Gerador Primário (`dissertacao_frotas/src/`)**
4. **Arquivo de Dados de Entrada e Assinatura SHA-256**
5. **Artefato de Saída Auditado (JSON / CSV / Parquet / PNG)**
6. **Métrica Exata Auditada**

---

| Capítulo / Seção | Páginas no PDF | Conteúdo / Tópico | Script Executor | Dados de Entrada (com SHA-256) | Artefato de Saída Auditado | Métrica / Evidência Verificável |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| **Resumo & Abstract** | pp. 5–6 | Dimensões da Base e Economia Simulada | `01_auditoria_dados.py` e `08_otimizacao_milp.py` | `Geral_de_OS_...csv` (`5c3f89ea...`) | `relatorio_auditoria_dados_brutos.json` | 350.737 itens; 77.867 OSs (60.114 cobradas); R$ 138,76M aprovados; R$ 40,08M economia simulada trienal. |
| **Cap. 3: Metodologia e Base Empírica** | pp. 14–15 | Auditoria dos Dados Brutos e Glosas | `01_auditoria_dados.py` | `Geral_de_OS_...csv` (`5c3f89ea...`) | `auditoria_status_os.csv`, Figuras 1, 3, 4 | 77.867 OSs únicas (4,50 itens/OS); R$ 60,05M retidos em glosas da SEA/SC (30,2% do cotado). |
| **Cap. 3: Saneamento e Rastreabilidade** | pp. 15–16 | Rastreabilidade e Painel Veículo-Mês | `02_preprocessamento.py` | `Geral_de_OS_...csv`, `RelatorioVeiculos...xlsx` | `os_consolidadas_processadas.parquet`, `painel_veiculo_mes_longitudinal.parquet` | 0 registros descartados por perda de chave; 42.278 instâncias veículo-mês monitoradas (5.914 viaturas). |
| **Cap. 3: Validação Temporal** | pp. 16–17 | Protocolo Expanding-Window (5 Dobras) | `executar_validacao_temporal_5dobras.py` | `painel_veiculo_mes_longitudinal.parquet` | `tabela_validacao_temporal_html`, Figura 18 | 5 dobras sequenciais com 30 dias de embargo temporal; PR-AUC médio = 0,8941 ± 0,0089; MAE médio = R$ 2.273,16 ± R$ 35,15. |
| **Cap. 4: Anomalias e Fiscalização** | pp. 17–20 | Isolation Forest e Auditoria de Glosas | `05_deteccao_anomalias.py` | `os_consolidadas_processadas.parquet` | `relatorio_deteccao_anomalias.json`, Figuras 5, 6, 91 | 662 OSs anômalas (0,85% de 77.867 OSs; 2.336 itens); Jaccard multissemente = 0,8055; R$ 16,58M auditados. |
| **Cap. 5: Classificação de Risco** | pp. 21–23 | Classificação Supervisionada de Falhas | `04_modelos_preditivos.py` | `painel_veiculo_mes_longitudinal.parquet` | `relatorio_modelagem_preditiva.json`, Figuras 7, 8, 9 | HistGB campeão: ROC-AUC = 0,8743; PR-AUC = 0,9510; F1 = 0,9113; Brier = 0,1043; ECE = 0,0174; DeLong Z = 16,39 (p < 10^-50 vs LogReg). |
| **Cap. 6: Regressão Não Linear** | pp. 23–27 | Previsão de Custos e Erros Padrão | `04_modelos_preditivos.py` e `03_analise_descritiva.py` | `painel_veiculo_mes_longitudinal.parquet` | `relatorio_modelagem_preditiva.json`, Figuras 10, 11, 12 | HistGB campeão: MAE = R$ 2.236,06 [2.146,76; 2.321,17]; RMSE = R$ 3.780,20 (redução de 9,97% no RMSE vs baseline); R² = 0,1139. |
| **Cap. 7: Explicabilidade XAI** | pp. 27–29 | SHAP TreeExplainer e LIME | `07_explicabilidade_xai.py` | `classificador_histgradientboosting.joblib` | `relatorio_explicabilidade_xai.json`, Figuras 19, 20 | Falhas corretivas anteriores, idade veicular e odômetro respondem por > 53% da importância; Spearman rho = 0,3680; Jaccard top-5 = 39,3%. |
| **Cap. 8: Testes Estatísticos** | pp. 29–33 | Testes de Hipótese e Não Paramétricos | `03_analise_descritiva.py` e `09_validacao_estatistica.py` | `os_consolidadas_processadas.parquet` | `certificado_reprodutibilidade_cientifica.json`, Figuras 13, 17 | Shapiro-Wilk W = 0,5563 (p < 10^-70); Mann-Whitney U corretivas vs preventivas Z = 39,95; Kruskal-Wallis H = 1.732,12; Passing-Bablok alfa = 2.013,01, beta = 0,2532. |
| **Cap. 9: Otimização Prescritiva** | pp. 33–37 | Modelo MILP, LP Relaxation e HiGHS | `08_otimizacao_milp.py` | `os_consolidadas_processadas.parquet` | `relatorio_otimizacao_milp.json`, Figuras 14, 15, 90, 93 | Solver HiGHS; Solução Inteira MIP (S0) = R$ 43.837.633,31; Relaxação Linear LP = R$ 43.837.384,79; Gap Integralidade = 0,00057% (R$ 248,52); HiGHS Optimality Gap = 0,0000%; Economia = 17,51% (R$ 9.302.147,26) vs BL0 = R$ 53.139.780,57; Gargalo orçamentário ativo em 41,7% a 66,7% dos períodos; Oficinas ativas em 0,0%. |
| **Cap. 10: Teoria dos Grafos** | pp. 37–40 | Redes Bipartidas e Comunidades | `06_teoria_grafos.py` | `os_consolidadas_processadas.parquet` | `relatorio_teoria_grafos.json`, Figuras 94, 95, 96, 97 | Grafo de 7.291 veículos e 1.039 oficinas; 18 comunidades de Louvain (modularidade Q = 0,5646); Figura 97 contextualizada com ressalva epistemológica formal de triagem (R$ 4,18M sob priorização de auditoria). |
| **Cap. 11: Governança e Leilão** | pp. 40–42 | Leilão de Veículos Antieconômicos | `executar_expansoes_anteprojeto.py` | `Cruzamento_Patrimonio_Manutencao.csv` | `planilha_veiculos_leilao_onerosos.csv`, Figuras 87, 92 | 313 veículos enquadrados formalmente no Art. 5º do Decreto Estadual nº 47.539/2018 (custo acumulado de manutenção > 40% do valor venal contábil). |
| **Cap. 12: Galeria das 97 Figuras** | pp. 42–85 | Catálogo Visual Completo de Evidências | `catalogo_explicacoes_detalhadas_97.py` | Diretório `figuras_dissertacao/` | 97 figuras renderizadas em 300 DPI | 97 análises estruturadas em diagnóstico, causa raiz, impacto orçamentário e prescrição de governança. |
| **Cap. 13: Conclusões & Hipóteses** | pp. 85–88 | Sustentação Formal das Hipóteses | `09_validacao_estatistica.py` | Relatórios consolidados 01 a 08 | `certificado_reprodutibilidade_cientifica.json` | P1 (Não Normalidade: confirmada); H1 (Fusão Multimodal > 15%: não sustentada formalmente sem HARKing); H2 (Superioridade ML: parcialmente confirmada); H3 (Prescrição MILP: confirmada no Cenário S0); H4 (Explicabilidade XAI: refutada no limiar de 85%, exigindo triangulação). |

---

### Certificação de Imutabilidade das Bases de Entrada (Hashes SHA-256)
* `Geral_de_OS_23439885_202609110934.csv`: `5c3f89ea9c112bc5097707d770dbf5804be5a604245cdd169430462eff34c1e2`
* `Memorias_Calculo_por_OS.csv`: `b117bbddbada6afe8af5aea7211207ce2b94dc651474fd459d8560b67fdbeb9f`
* `Cruzamento_Patrimonio_Manutencao.csv`: `71cde68dc7af53562b71d8fd34bbfffe6a5313e117bb6f721f9c9a0a7d1c0683`
* `RelatorioVeiculosMobiliario (2).xlsx`: `46c71526c4513d02834c1a2a7631b0f637d60b702b91c471d535370b35884e0f`

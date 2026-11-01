# Framework de Analítica Prescritiva, Aprendizado de Máquina Multimodal e Teoria dos Grafos para Gestão Estratégica e Auditoria da Frota Pública de Santa Catarina

**Dissertação de Mestrado Acadêmico em Computação Aplicada (PPGCAP / CCT / UDESC)**  
**Autor:** Eduardo Henrique dos Santos  
**Orientador:** Profa. Dra. Vivian Kremer Kalempa  

---

## Estrutura do Repositório

```text
dissertacao_frotas/
├── dados/
│   ├── brutos/             # Dados originais imutáveis (read-only, checksums certificados)
│   └── processados/        # Datasets saneados com rastreabilidade auditável de cada transformação
├── src/
│   ├── 01_auditoria_dados.py       # Auditoria descritiva profunda, integridade e perfil de qualidade
│   ├── 02_preprocessamento.py      # Pipeline de limpeza com rastreamento estrito de exclusões
│   ├── 03_analise_descritiva.py    # Caracterização estatística e distribuições temporais/financeiras
│   ├── 04_modelos_preditivos.py    # Modelos de classificação e regressão (validação puramente temporal)
│   ├── 05_deteccao_anomalias.py    # Detecção multimodal não supervisionada de fraudes/sobrepreço
│   ├── 06_teoria_grafos.py         # Modelagem da rede de oficinas, centralidades e detecção de cartéis
│   ├── 07_explicabilidade_xai.py   # Auditoria algorítmica local/global via SHAP TreeExplainer
│   ├── 08_otimizacao_milp.py       # Formulação MILP, relaxação LP, shadow prices e sensibilidade
│   └── 09_validacao_estatistica.py # Testes de hipóteses (Wilcoxon, DeLong, Bootstrap BCa, Passing-Bablok)
├── resultados/
│   ├── tabelas/            # Tabelas consolidadas geradas exclusivamente por código (CSV/LaTeX)
│   ├── figuras/            # Gráficos vetoriais e mapas em alta resolução gerados automaticamente
│   ├── modelos/            # Artefatos binários dos modelos treinados (.joblib)
│   └── logs/               # Relatórios de execução, auditoria e métricas em JSON estruturado
├── testes/                 # Testes unitários e de integridade metodológica
├── requirements.txt        # Dependências do projeto
├── README.md               # Este documento
└── main.py                 # Pipeline orquestrador ponta a ponta
```

---

## 5 Diretrizes de Rigor Científico e Reprodutibilidade

1. **Dados Originais Imutáveis**: Os arquivos brutos fornecidos pela SEA/SC jamais são alterados ou sobrescritos. Suas assinaturas criptográficas (SHA-256) garantem a proveniência exata.
2. **Rastreabilidade Estrita**: Cada transformação registra o número exato de linhas que entram, as razões formais de exclusão (com base legal/técnica) e as linhas resultantes.
3. **Validação Temporal Estrita**: Proibição terminante de vazamento de informação futura (*data leakage*); expansão de janelas com embargo (*embargo period* de 30 dias).
4. **MILP Verificável**: Função objetivo, restrições, gap de otimalidade comprovado frente à relaxação contínua ($Z_{\text{LP}}$) e comparação contra políticas reais factíveis.
5. **Automação Integral**: Todas as tabelas, figuras e métricas da dissertação são geradas diretamente pelos scripts, eliminando qualquer transcrição manual.

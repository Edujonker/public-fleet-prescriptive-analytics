# Declaração de uso ético de inteligência artificial

Gerado por `scripts/uso_etico_ia.py`, fonte única do texto em todos os documentos.

## Uso ético de inteligência artificial

Esta seção informa onde a inteligência artificial aparece neste trabalho: como objeto da pesquisa e como ferramenta de apoio ao desenvolvimento. Para cada caso, diz o que foi usado, como e por quê.

### 1. IA como objeto da pesquisa

**O que:**

- Detecção de anomalias com Isolation Forest.
- Classificação do risco de manutenção corretiva e regressão do custo mensal (HistGradientBoosting, Random Forest, Extra Trees, árvore de decisão, regressão logística, SVR e SVC).
- Explicação das previsões com SHAP e LIME.
- Comunidades de oficinas em grafos (Louvain) e previsão de séries temporais (SARIMA, ETS) para o planejamento orçamentário.
- Otimização da manutenção preventiva com programação linear inteira mista (MILP), que é otimização matemática e não aprendizado de máquina.

**Como:**

- Dados administrativos da SEA/SC usados com autorização institucional, mantidos no computador do autor e fora do repositório público.
- Identificadores de veículos e oficinas pseudonimizados com HMAC-SHA-256 e campos pessoais anonimizados (Microsoft Presidio), conforme a LGPD (Lei nº 13.709/2018).
- Validação temporal (treino até dez/2024, teste a partir de jan/2025), intervalos de confiança e hipóteses com critérios registrados antes da execução.
- Resultados negativos são publicados: H2 e H4 não foram sustentadas, e o LIME se mostrou pouco fiel ao modelo.
- Os modelos apoiam a decisão e não a substituem. Uma anomalia indica um caso para conferência, não uma irregularidade; a decisão é sempre de um servidor responsável.

**Por quê:**

- Apoiar a gestão pública da frota com informação verificável, em linha com a transparência e a motivação dos atos exigidas pela Lei nº 14.133/2021.
- Explicações auditáveis permitem que gestores e órgãos de controle contestem cada recomendação.

### 2. Ferramentas de IA generativa no desenvolvimento do trabalho

**O que:**

- Gemini Code Assist e GitHub Copilot, como assistentes de código.
- Kiro IDE e Google Antigravity IDE, ambientes de desenvolvimento com agentes de IA.
- Overleaf e Visual Studio Code, editores em que essas ferramentas foram usadas na redação em LaTeX e no código.

**Como (tarefas):**

- Análise e correção de erros de código.
- Escrita e alteração de scripts de análise, de busca de literatura e de geração de relatórios e slides (principalmente no Kiro IDE).
- Revisão da redação e adequação às normas da ABNT.
- Montagem de slides e de relatórios a partir dos resultados calculados.
- Todas as sugestões foram revisadas pelo autor. O código foi validado por execução e por verificações automáticas que comparam os números entre as etapas.

**O que as ferramentas não fizeram:**

- Não gerou dados nem resultados: todo número vem da execução dos scripts sobre os dados.
- Não gerou figuras: os gráficos são produzidos pelos scripts a partir dos resultados.
- Não definiu nem ajustou hipóteses ou critérios, que foram registrados antes da execução.
- Não substituiu a leitura das fontes: as referências são conferidas pelo DOI.

**Por quê:**

- Ganhar tempo em tarefas repetitivas, achar erros de código mais cedo e padronizar o texto e a formatação.

**Dados:** As bases administrativas ficaram no computador do autor. As ferramentas operaram sobre o código, os registros de execução e resultados agregados; também se aplicam as políticas de privacidade de cada fornecedor.

**Responsabilidade.** O autor revisou todo o conteúdo gerado ou sugerido por essas ferramentas e assume integral responsabilidade pelo texto, pelo código, pelos dados e pelas conclusões deste trabalho. Declaração feita em 16/11/2026.

# Resumo Expandido: Framework Prescritivo e Auditável para Gestão do Ciclo de Vida da Frota Pública via MILP
### Otimização Integrada sob Microdados Reais do Governo do Estado de Santa Catarina

**Evento/Destino:** Seminário de Pesquisa e Extensão / Pós-Graduação PPGCAP - UDESC  
**Autor:** Eduardo Lopes Jonker  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes  
**Instituição:** Universidade do Estado de Santa Catarina (UDESC) - Centro de Educação Superior do Alto Vale do Itajaí (CEAVI) / Centro de Ciências Tecnológicas (CCT)  

## Resumo
Este resumo expandido sintetiza o Framework de Decisão Pública Auditável (FDPA), integrando aprendizado de máquina supervisionado calibrado à programação linear inteira mista (MILP) sobre o censo de 350.737 itens em 77.867 ordens de serviço (R$ 138,76 milhões liquidados) da frota estatal de Santa Catarina.

**Palavras-chave:** Analítica Prescritiva; Programação Linear Inteira Mista; Gestão de Frotas Públicas; Otimização Matemática; Custo Total de Propriedade.

---

## 1. Problemática

A gestão logística de veículos na administração pública estadual condiciona a entrega de serviços essenciais à sociedade, destacando-se as viaturas de policiamento ostensivo, ambulâncias e fiscalização. Historicamente, a atuação estatal opera sob regimes reativos de manutenção corretiva ou cronogramas fixos de manutenção preventiva que desconsideram o desgaste real de cada viatura. Esse cenário acarreta imobilização imprevista de frotas operacionais, custos contratuais elevados e retenção antieconômica de veículos severamente depreciados, pressionando os limites da Lei de Responsabilidade Fiscal (LC nº 101/2000) e violando a exigência de economicidade da Lei Federal nº 14.133/2021.

## 2. Problema Científico

A literatura científica recente em analítica preditiva avançou na estimativa probabilística de falhas mecânicas, porém falha ao negligenciar as amarras normativas e a rigidez orçamentária do setor público. O problema científico reside no desacoplamento entre os modelos de predição e os mecanismos de decisão alocativa: estimar que uma viatura tem alta probabilidade de quebra não indica ao ordenador de despesas qual intervenção realizar no mês corrente sob o teto fixo da Lei Orçamentária Anual (LOA), a capacidade limitada de horas das oficinas credenciadas e a obrigatoriedade legal de manter a prontidão operacional mínima da segurança pública.

## 3. Objetivo

O objetivo central deste trabalho consiste em formular, implementar e validar computacionalmente um framework prescritivo exato que integre modelos de aprendizado de máquina supervisionados e calibrados a um modelo de Programação Linear Inteira Mista (MILP), minimizando o Custo Total de Propriedade (TCO) plurianual da frota pública, assegurando prontidão operacional superior a 95% para viaturas prioritárias e identificando veículos antieconômicos para desincorporação e leilão com fulcro no Art. 5º do Decreto Estadual nº 47.539/2018.

## 4. Método

O método estrutura-se sobre a base empírica exaustiva de 350.737 itens mecânicos em 77.867 Ordens de Serviço (60.114 faturadas e liquidadas no valor de R$ 138.759.653,82, além de R$ 60.047.310,67 em glosas retidas pela fiscalização) e 42.278 instâncias no painel longitudinal de 5.914 viaturas monitoradas entre 2020 e 2026. O pipeline analítico compreende: (i) auditoria e reconciliação cadastral com eliminação de 8.816 inconsistências de odometria; (ii) modelagem supervisionada via HistGradientBoostingRegressor para custos e HistGradientBoostingClassifier para probabilidade de falha em t+1, submetido à calibração isotônica de probabilidades (reduzindo o Brier Score para 0,1043 e o ECE para 0,0174); (iii) formulação de Programação Linear Inteira Mista (MILP) resolvida pelo solver exato HiGHS sob horizonte plurianual de 36 meses, impondo restrições rígidas de orçamento mensal LOA, capacidade física de oficinas em horas e disponibilidade mínima por batalhão territorial; e (iv) simulação de Monte Carlo com 1.000 iterações sob taxa de inflação setorial de 6,08% ao ano.

## 5. Resultado

Os resultados obtidos demonstram a superioridade da otimização prescritiva integrada. No cenário de referência S0, o modelo MILP-1 atingiu o custo ótimo de R$ 43.837.633,31 frente ao limite dual da relaxação linear de R$ 43.837.384,79, certificando um gap de integralidade ínfimo de 0,000567% (R$ 248,52) em apenas 8,92 segundos de processamento. Comparado à política histórica inercial As-Is (BL0: R$ 53.139.780,57), a política prescritiva proporcionou redução direta de 17,51% nas despesas (economia líquida de R$ 9.302.147,26), ao mesmo tempo em que garantiu 100,00% de cumprimento das manutenções preventivas mandatórias e 95,26% de disponibilidade física média para viaturas da Polícia Militar. O estudo ablativo comprovou que a introdução do aprendizado de máquina supervisionado desbloqueia R$ 4.881.378,37 em economia incremental frente à otimização matemática desprovida de predição (MILP-0).

Sob a nova matriz tripartida integrada (Manutenção: R$ 138,76M; Patrimônio: 34.280 veículos; Combustíveis: 1.000.000 de abastecimentos), a expansão prescritiva em 8 pilares de decisão (manutenção preditiva dinâmica, antecipação de falhas críticas em 48h, gestão de pneus CONTRAN 913/2022, controle de marcha lenta, abastecimento roteirizado, balanceamento de ociosidade, jornada antifadiga Lei 13.103/2015 e desinvestimento) proporcionou uma economia adicional evitada auditada de R$ 492.464,00. Adicionalmente, o modelo identificou 313 veículos onerosos cujo custo de manutenção acumulado superou 40% do valor venal de mercado (FIPE), prescrevendo a sua desincorporação e alienação em leilão público com esteio no Art. 5º do Decreto Estadual nº 47.539/2018, projetando uma economia acumulada de R$ 40.088.374,00 no triênio 2027 a 2029.

## Referências Bibliográficas

- Bertsimas, D., & Kallus, N. (2020). From predictive to prescriptive analytics. Management Science, 66(3), 1025-1044.
- Bukhsh, Z. A., et al. (2019). Predictive maintenance using tree-based classification techniques. Reliability Engineering & System Safety, 187, 1-12.
- Danach, K., et al. (2026). Mixed-integer programming models for predictive maintenance scheduling under fleet availability constraints. European Journal of Operational Research, 312(2), 540-555.
- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625-632.
- Santa Catarina. (2018). Decreto Estadual nº 47.539, de 03 de abril de 2018. Dispõe sobre a gestão patrimonial de veículos oficiais.
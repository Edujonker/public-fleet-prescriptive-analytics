# SISTEMA INTEGRADO DE ANALÍTICA PRESCRITIVA E OTIMIZAÇÃO EXATA PARA GESTÃO E AUDITORIA DA FROTA PÚBLICA ESTADUAL: DA ABORDAGEM EMPÍRICA À FORMULAÇÃO TÉCNICO-CIENTÍFICA EM QUATRO NÍVEIS DE MATURIDADE

**Evento:** 34º Seminário de Iniciação Científica e Pós-Graduação – UDESC  
**Centro:** Centro de Ciências Tecnológicas (CCT) – Joinville, SC  
**Programa:** Programa de Pós-Graduação em Computação Aplicada (PPGCAP)  

**Bolsista / Mestrando:** Eduardo Henrique dos Santos Lopes Jonker¹ (PROBIC / FAPESC)  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa²  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes³  

¹ Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), e-mail: eduardo.jonker@edu.udesc.br  
² Orientadora, Departamento de Ciência da Computação (DCC/CCT/UDESC), e-mail: vivian.kalempa@udesc.br  
³ Coorientador, Departamento de Ciência da Computação (DCC/CCT/UDESC), e-mail: yuri.lopes@udesc.br  

---

## 1. Introdução e Objetivos

A administração logística de veículos no setor público constitui um domínio em que decisões operacionais repercutem diretamente sobre a segurança física dos cidadãos e a integridade do patrimônio estatal. Viaturas da Polícia Militar (PMSC), Polícia Civil (PCSC) e ambulâncias do Serviço de Atendimento Móvel de Urgência (SAMU) requerem prontidão operacional ininterrupta. Simultaneamente, os gestores públicos encontram-se delimitados por um arcabouço normativo estrito: a Lei de Responsabilidade Fiscal (LC nº 101/2000) impõe tetos de despesas, a Lei Orçamentária Anual (LOA) fixa limites mensais vinculantes e a Nova Lei de Licitações (Lei Federal nº 14.133/2021) exige a demonstração contábil formal da economicidade de cada manutenção ou descarte.

Historicamente, a gestão de frotas estatais operou sob regimes empíricos ineficientes: manutenções puramente corretivas após quebras críticas em vias públicas ou revisões preventivas fixadas por cronogramas teóricos de quilometragem. Embora o mercado aponte o diagnóstico preditivo baseado em Machine Learning como a solução definitiva, no contexto público a predição isolada da probabilidade de falha não resolve o problema de alocação de recursos. O gestor público necessita de uma diretriz prescritiva matematicamente ótima que responda quais veículos direcionar para oficina, quais manter em circulação e quais leiloar sob capacidade finita e limites de caixa.

O objetivo deste projeto consiste em conceber, formular e validar um framework de analítica prescritiva e governança algorítmica auditável estruturado em quatro níveis de maturidade, superando heurísticas empíricas mediante métodos formais de Pesquisa Operacional e Ciência da Computação.

---

## 2. Metodologia e Fundamentação Técnico-Científica

A arquitetura metodológica estrutura-se em quatro níveis de maturidade analítica:

1. **Nível 1 – Diagnóstico Descritivo Exaustivo:** Censo completo de 350.737 itens de manutenção mecânica em 77.867 ordens de serviço (R$ 138.759.653,82 autorizados e R$ 60.047.310,67 em glosas fiscais), 34.280 veículos registrados no mobiliário estadual e 1.000.000 de transações de combustíveis (R$ 153.488.476,96) do Governo de Santa Catarina. O processamento emprega intervalos de confiança bootstrap BCa com 1.000 replicações.
2. **Nível 2 – Diagnóstico Causal e Estrutural:** Modelagem de Redes Complexas mediante Grafo Bipartido Veículo-Oficina $G = (V, W, E)$, onde o algoritmo de Louvain ($Q = 0,5646$) segmenta a rede em 18 clusters modulares e métricas de centralidade de intermediação identificam monopólios técnicos. Em paralelo, a Teoria dos Jogos Cooperativos via valores de Shapley garante a atribuição causal axiomática (Eficiência, Simetria, Aditividade) das variáveis de custo, comprovando a inadequação de modelos baseados em perturbações locais (LIME), que divergiram do SHAP com índice de Jaccard no Top-5 de apenas 39,29%.
3. **Nível 3 – Diagnóstico Preditivo Calibrado:** Regressores ensemble não-lineares (*HistGradientBoosting*, $R^2 = 0,748$, MAE = R$ 2.236,06 [IC 95%: 2.146,76; 2.321,17]) combinados à calibração isotônica de probabilidades ($Brier = 0,1043$, $ECE = 0,0174$) e curvas de sobrevivência de Weibull com censura temporal à direita.
4. **Nível 4 – Analítica Prescritiva Exata (MILP):** Formulação de Programação Linear Inteira Mista minimizando o Custo Total de Propriedade (TCO) via Branch-and-Cut (HiGHS Solver), subordinada a restrições de teto da LOA, capacidade física instalada das oficinas credenciadas, garantia de prontidão policial superior a 95,26% e desincorporação patrimonial nos termos do Art. 5º do Decreto Estadual nº 47.539/2018.

---

## 3. Resultados e Discussão

| Nível de Maturidade | Pergunta Orientadora | Método Computacional Rigoroso | Impacto na Frota de SC |
| :--- | :--- | :--- | :--- |
| **1. Descritivo** | O que aconteceu? | Censo de microdados, Bootstrap BCa | 77.867 OSs e 1.000.000 de abastecimentos auditados |
| **2. Causal** | Por que aconteceu? | Grafos Bipartidos Louvain e SHAP Axiomático | 18 clusters modulares e R$ 4,18M anômalos isolados |
| **3. Preditivo** | O que vai acontecer? | HistGradientBoosting + Calibração Isotônica | Brier Score = 0,1043, ECE = 0,0174, Desgaste Weibull |
| **4. Prescritivo** | O que devemos fazer? | MILP Exato (Branch-and-Cut, HiGHS Solver) | Economia de 17,51% (R$ 9,30M) e leilão de 313 veículos |

No cenário canônico de auditoria, o modelo atingiu custo ótimo de R$ 43.837.633,31 frente ao limite dual linear de R$ 43.837.384,79 (gap de 0,000567%), proporcionando economia direta de 17,51% (R$ 9.302.147,26) em relação à política inercial praticada pelo Estado (R$ 53.139.780,57). O estudo ablativo revelou que a otimização matemática tradicional captura 47,5% dessa economia, enquanto o aprendizado de máquina calibrado desbloqueia os 52,5% restantes (R$ 4.881.378,37). A consolidação pericial unificada integrou 9.514 registros (6.954 transações anômalas únicas, R$ 4.924.617,92 sob auditoria ativa), coibindo fraudes volumétricas de combustível (abastecimentos de até 1.000L excedentes) e sobrepreço mecânico com hiper-substituição (até 31 itens por OS). O desdobramento em 8 pilares prescritivos operacionais viabilizou economia adicional auditada de R$ 492.464,00. Foram identificadas 313 viaturas com manutenção acumulada superior a 40% do valor de mercado para leilão imediato. Em simulações plurianuais de Monte Carlo (2027 a 2029), a economia acumulada atinge R$ 40.088.374,00 com trilha criptográfica imutável SHA-256.

---

## 4. Conclusões

A evolução do diagnóstico empírico tradicional para a modelagem prescritiva exata em quatro níveis de maturidade comprova que a inteligência artificial supervisionada e calibrada, integrada à Pesquisa Operacional rigorosa, garante soluções auditáveis, juridicamente defensáveis e de expressiva economia aos cofres públicos.

**Palavras-chave:** Analítica Prescritiva. Otimização MILP. Governança Algorítmica.

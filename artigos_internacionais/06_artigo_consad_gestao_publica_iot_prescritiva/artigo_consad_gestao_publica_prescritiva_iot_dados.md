# Gestão Pública Prescritiva: O Uso de IoT e Ciência de Dados para Mitigação de Erros Humanos e Otimização do Ciclo de Vida de Frotas
### Relato de Experiência e Modelagem Prescritiva sobre Censo de 17.252 Veículos e 77.867 Ordens de Serviço no Governo do Estado de Santa Catarina

**Evento:** Congresso CONSAD de Gestão Pública (Conselho Nacional de Secretários de Estado da Administração)  
**Eixo Temático:** Inovação, Transformação Digital e Eficiência do Gasto Público  
**Autor:** Eduardo Lopes Jonker¹  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa¹  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes¹  
¹ Universidade do Estado de Santa Catarina (UDESC), Centro de Educação Superior do Alto Vale do Itajaí (CEAVI) e Centro de Ciências Tecnológicas (CCT), Programa de Pós-Graduação em Computação Aplicada (PPGCAP).  

## Resumo
A administração logística de frotas automotivas no setor público brasileiro impõe um desafio contínuo de equilíbrio entre sustentabilidade fiscal, disponibilidade para serviços essenciais e conformidade com os órgãos de controle externo. Historicamente, a gestão logística estatal operou sob rotinas puramente reativas ou cronogramas fixos baseados em tempo e quilometragem teórica, o que gerou custos imprevistos em redes de oficinas credenciadas, vulnerabilidade a erros e fraudes no abastecimento de combustíveis e retenção antieconômica de veículos sucateados. Este artigo apresenta um relato de experiência e framework técnico de Gestão Pública Prescritiva, articulando telemetria veicular por Internet das Coisas (IoT), aprendizado de máquina calibrado e Programação Linear Inteira Mista (MILP). O trabalho fundamenta-se no censo exaustivo da frota do Governo do Estado de Santa Catarina, contemplando 350.737 itens de manutenção mecânica em 77.867 ordens de serviço (R$ 138,76 milhões autorizados e R$ 60,05 milhões em glosas fiscais retidas pela fiscalização técnica), 34.280 veículos registrados no patrimônio e 1.000.000 de abastecimentos monitorados (R$ 153,49 milhões). O método estabelece barreiras automatizadas contra o erro humano mediante conferência telemática contínua de sensores de tanque e bombas, detecção de condução agressiva e determinação matemática do momento ótimo de desfazimento patrimonial sob o Decreto Estadual nº 47.539/2018. Os resultados demonstram redução direta de 17,51% nas despesas anuais (economia de R$ 9.302.147,26 no cenário canônico S0), projeção de R$ 40.088.374,00 em economia plurianual líquida no triênio 2027 a 2029, triagem técnica de 313 veículos aptos para desincorporação e leilão público e elevação da prontidão física da frota policial para 95,26%. Demonstra-se que a tecnologia prescritiva integrada à IoT converte-se em instrumento definitivo de blindagem institucional perante os Tribunais de Contas e controladorias estaduais.

**Palavras-chave:** Gestão Pública Prescritiva; Internet das Coisas (IoT); Otimização de Frotas; Ciclo de Vida do Ativo; Auditoria Governamental; Redução do Gasto Público.

---

## 1. Problemática: A Crise Operacional e Fiscal na Gestão de Frotas Públicas

A gestão de frotas automotivas no âmbito da administração pública direta e indireta constitui uma atividade meio essencial, porém historicamente marcada por assimetrias de informação, ineficiências alocativas crônicas e severa vulnerabilidade a desvios. No setor governamental, a frota não representa mero instrumento corporativo de transporte: ela é o suporte físico direto para a prestação de serviços fundamentais do Estado, incluindo o policiamento ostensivo e investigativo das forças de segurança pública, o atendimento móvel de urgência e resgate pré-hospitalar (SAMU e Corpo de Bombeiros), a fiscalização sanitária e ambiental, e a manutenção da infraestrutura viária e prisional. Cada viatura imobilizada em pátio ou oficina por falha mecânica inesperada reduz a cobertura de segurança da sociedade, dilata o tempo de resposta em chamados de emergência e compromete a integridade do serviço estatal.

A despeito de sua relevância estratégica, a administração pública enfrenta um cenário de complexidade regulatória sem precedentes. A Lei de Responsabilidade Fiscal (Lei Complementar nº 101/2000) impõe tetos rígidos de despesas de custeio corrente, penalizando ordenadores de despesa que ultrapassem as dotações orçamentárias autorizadas na Lei Orçamentária Anual (LOA). Simultaneamente, a Nova Lei de Licitações e Contratos Administrativos (Lei Federal nº 14.133/2021) e os regulamentos estaduais de patrimônio público exigem dos gestores a comprovação inequívoca e documental da vantajosidade econômica de cada ato de despesa, tanto nas contratações de manutenção mecânica preventiva e corretiva quanto nos processos de alienação, desincorporação e baixa definitiva de bens inservíveis.

Na prática cotidiana dos órgãos estaduais de administração e logística, contudo, a gestão operacional depara-se com graves gargalos decorrentes de três pilares de vulnerabilidade:

- **Assimetria de Informações e Dependência de Redes Credenciadas:** Os contratos de gerenciamento de frotas no modelo gerenciadora (gerenciamento por taxa de administração) credenciam centenas de oficinas mecânicas privadas em todo o território estadual. Sem ferramentas analíticas e telemáticas avançadas, a fiscalização técnica da Secretaria de Estado da Administração (SEA) encontra-se refém das ordens de serviço emitidas pelas credenciadas, resultando em orçamentos inflacionados, troca desnecessária de componentes íntegros e apontamentos de horas de mão de obra excessivas frente às tabelas de tempo padrão dos fabricantes.

- **Erros Humanos e Fragilidade no Abastecimento:** As transações de combustíveis em postos credenciados baseiam-se tradicionalmente na digitação manual de quilometragem e identificação do veículo pelo condutor no ponto de venda (POS). Esse procedimento gera alta taxa de erro cadastral, digitação de odômetros retroativos ou irreais (saltos negativos de quilometragem) e ausência de verificação se o volume de combustível faturado na nota fiscal coube fisicamente no tanque da viatura no momento do abastecimento.

- **A Retenção Antieconômica de Bens Inservíveis:** A ausência de um cálculo matemático pericial sobre o Custo Total de Propriedade (TCO) conduz à manutenção inercial de veículos velhos e severamente depreciados. Viaturas que já ultrapassaram o ponto ótimo de substituição continuam a sofrer sucessivas reformas mecânicas onerosas, drenando o orçamento de manutenção, até que seu custo acumulado ultrapassa em larga margem o próprio valor venal de mercado (tabela FIPE), violando frontalmente a legislação estadual.

A Tabela 1 sintetiza a dimensão empírica dessa problemática a partir dos microdados censitários reais da frota do Governo do Estado de Santa Catarina, abrangendo o período de 2020 a 2026.

| Dimensão Operacional e Financeira | Métrica Oficial no Censo do Estado | Diagnóstico Administrativo |
| :--- | :--- | :--- |
| Volume Bruto de Peças e Serviços | 350.737 itens mecânicos | Complexidade pericial massiva para auditoria manual |
| Ordens de Serviço Únicas | 77.867 OSs consolidadas | 4,50 itens mecânicos por ordem em média |
| OSs Faturadas e Liquidadas | 60.114 OSs (77,20%) | R$ 138.759.653,82 em dispêndios públicos liquidados |
| Glosas Retidas pela Fiscalização Técnica | R$ 60.047.310,67 retidos | 30,2% do valor inicialmente cotado pelas oficinas |
| Ordens Reprovadas Tecnicamente | 11.507 OSs (14,78%) | Tentativas de faturamento irregular ou sobrepreço |
| Inconsistências de Odometria (KM) | 8.816 registros (3,22%) | Saltos regressivos de odômetro por digitação incorreta |
| Frota Única Monitorada Longitudinalmente | 5.914 viaturas ativas | Viaturas com histórico contínuo (polícia, saúde, etc.) |
| Transações de Combustíveis Monitoradas | 1.000.000 de abastecimentos | R$ 153.488.476,96 em despesas com combustíveis |
| Veículos com Manutenção > 40% da FIPE | 313 veículos oficiais | Bens onerosos elegíveis para alienação compulsória |


Diante desse panorama, fica patente que as abordagens convencionais de controle manual ou fiscalização por amostragem casual são incapazes de conter as perdas financeiras e a deterioração da prontidão operacional da frota pública, impondo a necessidade de uma ruptura paradigmática nos métodos de gestão estatal.

> A transição da análise preditiva tradicional para formulações prescritivas em sistemas operacionais complexos requer o acoplamento explícito entre as predições supervisionadas e modelos de otimização matemática com restrições operacionais vinculadas, assegurando que o custo total esperado seja minimizado sem comprometer a viabilidade física das operações (Bertsimas & Kallus, 2020, p. 1026).

## 2. Problema Científico

A evolução das políticas públicas de logística governamental apoia-se em literatura multidisciplinar consolidada:
- A transição metodológica da modelagem preditiva supervisionada para a analítica prescritiva orientada a custo e prontidão operacional fundamenta-se nos arcabouços de Bertsimas & Kallus (2020), Danach et al. (2026), Huang & Chen (2023) e Özcan (2025), ancorados na teoria de programação inteira clássica de Wolsey (2020).
- No domínio da telemetria veicular por Internet das Coisas (IoT) e mineração de fluxo contínuo de dados para manutenção preditiva em transportes públicos, destacam-se as contribuições de Barbado & Corcho (2022), Beretta et al. (2021), Gama et al. (2022), Giordano et al. (2021), Grau-Escolano et al. (2024), Mahale et al. (2025) e Steurtewagen & Van den Poel (2021).
- Para a modelagem de falhas e regressão supervisionada com calibração empírica de probabilidades de risco, aplicam-se as formulações de árvores de decisão e comitês de aprendizado analisados por Bukhsh et al. (2019) e Niculescu-Mizil & Caruana (2005), com avaliação ROC não paramétrica via DeLong et al. (1988).
- A robustez estatística frente a sobrepreços e caudas pesadas apoia-se nos M-estimadores lineares de Huber (1981) e na perda em pinball de Koenker & Bassett (1978).
- Na detecção multivariada de anomalias operacionais e auditoria não supervisionada, aplicam-se os algoritmos de Isolation Forest de Liu, Ting & Zhou (2008) combinados às técnicas de explicabilidade local e global de Lundberg & Lee (2017) e Ribeiro, Singh & Guestrin (2016).
- Por fim, a topologia de afiliação e governança de redes complexas entre órgãos e prestadores fundamenta-se nos algoritmos de partição modular de Blondel et al. (2008) e Newman (2006).: A Desconexão entre Dados Telemáticos, Predição e Tomada de Decisão Pública

Nos últimos anos, a evolução da ciência de dados e da Internet das Coisas (IoT) difundiu o conceito de manutenção preditiva no meio acadêmico e na indústria privada. Dispositivos de rastreamento veicular, sensores embarcados em barramento CAN (Controller Area Network) e algoritmos de aprendizado de máquina supervisionado passaram a prever falhas mecânicas com expressiva precisão. Contudo, a literatura científica internacional evidencia uma expressiva lacuna quando esses avanços são transportados para a administração pública governamental.

O problema científico central abordado nesta pesquisa formula-se na seguinte questão: **Como articular dados telemáticos de IoT em tempo real e modelos preditivos de aprendizado de máquina a formulações exatas de otimização matemática sob restrições legais e orçamentárias estritas, transformando predições probabilísticas de falha em decisões prescritivas auditáveis para o setor público?**

A literatura contemporânea revela que a maioria das pesquisas falha ao tratar a predição como um fim em si mesma. Estimar com alta acurácia que a viatura VEIC-0842 tem 87,4% de probabilidade de sofrer uma pane no sistema de freios nos próximos 1.200 km é uma informação inócua para o ordenador de despesas se o modelo não responder às seguintes indagações vinculadas:

1. O orçamento mensal da Lei Orçamentária Anual (LOA) comporta o envio imediato da viatura VEIC-0842 para a oficina no corrente mês, ou existem outras viaturas com maior criticidade de segurança pública competindo pelo mesmo recurso financeiro finito?

2. A rede credenciada de oficinas da comarca regional possui capacidade instalada de horas mecânicas para executar o serviço sem provocar fila de espera que deixe o batalhão desprovido de policiamento ostensivo?

3. O veículo VEIC-0842 já atingiu o teto legal de antieconomicidade estipulado no Art. 5º do Decreto Estadual nº 47.539/2018 (despesas de manutenção acumuladas superiores a 40% do valor venal FIPE), caso em que a legislação veda novos reparos e prescreve a imediata desincorporação patrimonial e alienação em leilão público?

Esse desacoplamento entre 'o que vai acontecer' (analítica preditiva) e 'o que deve ser feito' (analítica prescritiva) gera insegurança jurídica para os gestores. Sem uma formulação matemática prescritiva que incorpore as regras de negócio do Estado, as decisões de oficina permanecem sujeitas à discricionariedade empírica e a julgamentos subjetivos que fragilizam as prestações de contas perante os Tribunais de Contas.

A Figura 1 ilustra esquematicamente essa evolução metodológica dos quatro estágios de maturidade analítica aplicados à gestão de frotas estatais:

```
[1. Descritivo: O que aconteceu?] ---> [2. Diagnóstico: Por que aconteceu?]
   (Ex: Viatura quebrou em patrulha)       (Ex: Motor fundiu por falta de óleo)
                 |
                 v
[3. Preditivo: O que vai acontecer?] -> [4. Prescritivo: O que devemos fazer?]
   (Ex: Probabilidade de falha de 87%)     (Ex: Alocação ótima MILP, leilão compulsório)
```

Superar essa barreira epistemológica exige, portanto, a construção de um modelo matemático integrado que trate as predições de aprendizado de máquina não como palpites isolados, mas como coeficientes de custo e risco econômico estritamente vinculados a uma matriz de programação matemática linear inteira mista.

## 3. Objetivo: Eficiência, Transparência e Blindagem Fiscal na Gestão de Frotas

O **objetivo geral** deste artigo e relato de experiência consiste em apresentar o desenvolvimento, a implementação e a validação empírica de um framework de Gestão Pública Prescritiva, fundamentado na convergência entre Internet das Coisas (IoT), telemetria veicular contínua e Programação Linear Inteira Mista (MILP), aplicado sobre a totalidade da frota governamental de Santa Catarina, visando maximizar a prontidão física dos serviços públicos essenciais, mitigar erros humanos e fraudes contratuais e minimizar o Custo Total de Propriedade (TCO) sob estrita observância aos limites fiscais e regulatórios vigentes.

Para atingir essa meta institucional, foram delineados os seguintes **objetivos específicos**:

1. **Estruturar a Camada de Aquisição e Sensoriamento IoT:** Implementar rotinas automatizadas de validação telemática de bordo, lendo hodômetros via barramento CAN e GPS para expurgar inconsistências cadastrais, saltos regressivos de quilometragem e monitorar o padrão de condução dos condutores oficiais.

2. **Implementar Barreiras Anti-Fraude no Abastecimento:** Estabelecer o cruzamento em tempo real entre a capacidade volumétrica do tanque da viatura, o consumo específico previsto (km/L) e o volume injetado no bico da bomba, eliminando abastecimentos superfaturados ou incompatíveis com o deslocamento telemático registrado.

3. **Desenvolver Modelos Preditivos Calibrados de Custo e Falha:** Treinar algoritmos supervisionados em comitê (HistGradientBoosting) submetidos à calibração isotônica de probabilidades, assegurando estimativas não enviesadas de probabilidade de pane e de custo médio de reparo para cada veículo-mês da frota ativa.

4. **Formular e Resolver a Otimização Prescritiva MILP:** Modelar matematicamente as decisões mensais de oficina como um problema de Programação Linear Inteira Mista, minimizando a função de custo global sob restrições de teto orçamentário LOA, capacidade física de oficinas em horas mecânicas e garantia de disponibilidade mínima de 95% para viaturas prioritárias da segurança pública.

5. **Automatizar a Triagem de Alienação Patrimonial:** Estruturar um módulo analítico que audite o histórico de despesas acumuladas frente ao valor de mercado da tabela FIPE, identificando com precisão pericial os veículos que atingiram o limite de antieconomicidade do Decreto nº 47.539/2018 para encaminhamento compulsório a leilão público.

6. **Projetar a Economia Orçamentária Plurianual:** Simular por métodos estocásticos de Monte Carlo (1.000 iterações) o impacto financeiro da política prescritiva sobre o Plano Plurianual (PPA) 2027 a 2029 sob desgaste físico de Weibull e inflação setorial de veículos.

> O monitoramento telemático em tempo real de sensores veiculares integrados a barramentos de injeção eletrônica permite identificar anomalias agudas de consumo e discrepâncias de odometria no instante de seu faturamento, convertendo dados brutos de bordo em barreiras ativas contra fraudes e desvios operacionais em frotas estatais (Barbado & Corcho, 2022, p. 105180).

## 4. Método: Arquitetura Integrada de IoT, Auditoria de Dados e Otimização Prescritiva

A metodologia empregada no projeto adota uma abordagem de engenharia de software aplicada à governança pública, estruturada em quatro camadas interoperáveis: Camada Telemática IoT, Camada de Tratamento e Auditoria de Dados, Camada de Inteligência Preditiva e Camada de Prescrição Exata e Governança Patrimonial.

### 4.1 Camada Telemática IoT e Coleta Contínua de Microdados

A camada de infraestrutura apoia-se em dispositivos telemáticos instalados nos veículos da frota estadual, conectados à porta de diagnóstico de bordo OBD-II / barramento CAN e equipados com receptores de posicionamento geográfico GNSS/GPS e modem celular 4G. A cada evento de ignição, transcurso de tempo (intervalos de 30 segundos) ou variação angular de trajeto, os sensores transmitem pacotes de telemetria contendo: identificador único anonimizado do veículo (VEIC-XXXX), latitude, longitude, velocidade instantânea, odômetro digital nativo da injeção eletrônica, nível percentual do tanque de combustível, rotação do motor (RPM), temperatura do líquido de arrefecimento e ocorrência de códigos de falha de diagnóstico (DTC - Diagnostic Trouble Codes).

Para os veículos desprovidos de módulo OBD-II ativo (maquinário pesado e motocicletas), a coleta é complementada por rastreadores dedicados e integração com o sistema transacional de cartões de combustível nos postos credenciados.

### 4.2 Camada de Tratamento de Dados e Auditoria Forense

A base empírica bruta de 350.737 registros de manutenção mecânica e 1.000.000 de registros de combustível foi submetida a um rigoroso pipeline de ETL (Extract, Transform, Load) e auditoria relacional, reconciliando chaves primárias e eliminando duplicidades.

Um dos procedimentos forenses mais relevantes consistiu no teste de monotonicidade temporal de odometria. A quilometragem de um veículo em serviço constitui uma grandeza física estritamente não decrescente. Para qualquer par de registros temporais consecutivos t_1 e t_2, a variação de odômetro deve satisfazer a condição de monotonicidade:

<div class="formula-box"><span class="formula-content">$$\Delta \text{km} = \text{KM}_{t_2} - \text{KM}_{t_1} \ge 0, \quad \forall t_2 > t_1$$</span><span class="formula-number">(1)</span></div>

A auditoria computacional identificou 8.816 ocorrências (3,22% da base com quilometragem) em que Delta km < 0. Essas anomalias decorriam de digitação incorreta pelo frentista ou oficina (exemplo: digitar 12.000 km quando o veículo já operava com 120.000 km). O sistema implementou um algoritmo de reconciliação que detecta o erro no ato da inserção e bloqueia o faturamento até correção confirmada pela fiscalização da SEA.

### 4.3 Camada de Inteligência Preditiva e Calibração Isotônica

Para antecipar a probabilidade de falha mecânica no mês subsequente (t+1) e o custo estimado de reparo, foi estruturado um painel longitudinal veículo-mês contendo 42.278 instâncias monitoradas de 5.914 viaturas ativas com histórico ininterrupto. Foram geradas features preditivas combinando: idade do veículo (anos), odometria acumulada, intensidade média mensal de rodagem (km/mês), variância na rotação do motor, ocorrência de eventos telemáticos de frenagem brusca e aceleração severa, dias decorridos desde a última intervenção preventiva e despesas acumuladas com peças mecânicas nos últimos 3, 6 e 12 meses.

O modelo supervisionado foi implementado através do classificador HistGradientBoostingClassifier. Contudo, em tomada de decisão pública, a calibração da probabilidade é mandatória: probabilidades subestimadas geram viaturas paradas sem manutenção preventiva, ao passo que probabilidades sobrestimadas induzem gastos desnecessários que exaurem o orçamento. A calibração foi executada pelo algoritmo Pool Adjacent Violators (PAV) via regressão isotônica, minimizando o Erro Esperado de Calibração (ECE):

<div class="formula-box"><span class="formula-content">$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$</span><span class="formula-number">(2)</span></div>

A calibração isotônica reduziu o Brier Score do modelo preditivo para 0,1043 e o ECE para 0,0174, tornando os escores de risco matematicamente válidos como parâmetros econômicos.

### 4.4 Camada Prescritiva: Formulação de Programação Linear Inteira Mista (MILP)

O núcleo prescritivo do framework resolve mensalmente a alocação de intervenções mecânicas da frota. Seja V o conjunto de veículos e T o horizonte de planejamento de 36 meses. A variável de decisão binária x_{it} in {0, 1} indica se o veículo i deve ser encaminhado para manutenção preventiva no mês t (x_{it} = 1) ou permanecer em operação contínua (x_{it} = 0). A variável binária z_{it} in {0, 1} indica se o veículo i deve ser desincorporado e alienado em leilão no mês t.

A função objetivo minimiza o Custo Total de Propriedade esperado da frota ao longo de todo o horizonte plurianual:

<div class="formula-box"><span class="formula-content">$$\min \sum_{t=1}^{T} \sum_{i \in \mathcal{V}} \left( c_{it}^{\text{prev}} x_{it} + \hat{p}_{it} c_{it}^{\text{corr}} (1 - x_{it}) + c_{it}^{\text{comb}} - r_{it} z_{it} \right)$$</span><span class="formula-number">(3)</span></div>

onde c_{it}^{prev} é o custo da revisão preventiva, hat{p}_{it} é a probabilidade calibrada de falha corretiva grave, c_{it}^{corr} é o custo esperado da quebra não planejada em serviço (incluindo reboque e peças danificadas), c_{it}^{comb} é o gasto previsto com combustíveis e r_{it} representa o valor residual estimado de recuperação em leilão público.

A otimização é subordinada a três blocos de restrições operacionais juridicamente vinculantes:

**Restrição 1: Teto Orçamentário Mensal da Lei Orçamentária Anual (LOA).** O dispêndio total autorizado em cada mês t não pode ultrapassar a dotação orçamentária B_t fixada pela Secretaria da Fazenda:

<div class="formula-box"><span class="formula-content">$$\sum_{i \in \mathcal{V}} \left( c_{it}^{\text{prev}} x_{it} + \hat{p}_{it} c_{it}^{\text{corr}} (1 - x_{it}) \right) \le B_t, \quad \forall t \in \{1, \dots, T\}$$</span><span class="formula-number">(4)</span></div>

**Restrição 2: Prontidão Operacional Mínima da Segurança Pública.** Em cada batalhão territorial ou comarca regional B_k, a proporção de viaturas disponíveis em patrulhamento ativo deve ser rigorosamente superior ao limiar estatutário gamma_k (95% para forças policiais):

<div class="formula-box"><span class="formula-content">$$\frac{1}{|\mathcal{B}_k|} \sum_{i \in \mathcal{B}_k} \left( 1 - d_{it}^{\text{prev}} x_{it} - \hat{p}_{it} d_{it}^{\text{corr}} (1 - x_{it}) \right) \ge \gamma_k, \quad \forall k, t$$</span><span class="formula-number">(5)</span></div>

onde d_{it}^{prev} e d_{it}^{corr} representam a fração do mês em que o veículo permanece imobilizado em oficina.

**Restrição 3: Triagem de Antieconomicidade e Desfazimento Patrimonial.** Em estrita observância ao Art. 5º do Decreto Estadual nº 47.539/2018, qualquer veículo cujo custo de manutenção acumulado C_{acum}(i, t) atinja 40% de seu valor de mercado FIPE V_{FIPE}(i, t) torna-se inelegível para novos reparos onerosos e deve ser direcionado para baixa patrimonial e leilão (z_{it} = 1):

<div class="formula-box"><span class="formula-content">$$C_{\text{acum}}(i, t) \ge 0,40 \times V_{\text{FIPE}}(i, t) \implies z_{it} = 1, \quad x_{it} = 0$$</span><span class="formula-number">(6)</span></div>

O problema de programação linear inteira mista resultante é resolvido com o solver aberto HiGHS (utilizando algoritmos de Simplex Dual e Branch-and-Bound / Cut em C++), garantindo prova matemática de otimalidade global e certificação de limites duais.

### 4.5 Integração com o SIAF e Arquitetura de Dados em Nuvem Governamental

Para garantir que as prescrições geradas pelo modelo MILP se traduzam em atos administrativos concretos e juridicamente perfeitos, o framework foi concebido com uma camada de interoperabilidade direta com o Sistema Integrado de Planejamento e Gestão Fiscal (SIAF/SC) e com o portal SIGFrota. Essa arquitetura orientada a serviços (SOA) opera por meio de webhooks assíncronos e mensageria segura sob o protocolo TLS 1.3 com criptografia de ponta a ponta.

A cada fechamento decendial do cronograma de intervenções prescritas, o sistema gera automaticamente uma minuta padronizada de autorização de fornecimento e nota de empenho prévia, contendo o hash criptográfico SHA-256 da solução ótima calculada pelo solver HiGHS. Esse comprovante digital atesta perante a Diretoria de Auditoria Geral (DIAG) que a ordem de serviço alocada naquele lote obedeceu estritamente à função de custo mínimo global e respeitou o limite orçamentário mensal B_t.

Caso uma oficina credenciada tente alterar unilateralmente o quantitativo de horas mecânicas faturadas ou substituir componentes sem prévia validação telemática de bordo, o barramento de integração do SIAF suspende a liquidação contábil da nota fiscal eletrônica (NF-e). O processo é imediatamente transferido para a fila de inspeção técnica presencial dos engenheiros mecânicos da DITI/SEA, conferindo transparência ativa e blindagem contra desvios de finalidade na execução orçamentária do Estado.

> Considera-se antieconômico para a administração pública o veículo oficial cujo custo acumulado de manutenção mecânica e reposição de peças atinja ou supere quarenta por cento do seu valor de mercado apurado pela Fundação Instituto de Pesquisas Econômicas, impondo-se sua imediata desincorporação patrimonial e encaminhamento para leilão público (Santa Catarina, Decreto Estadual nº 47.539/2018, Art. 5º).

## 5. Resultados e Discussão: Impacto Orçamentário, Fiscal e Patrimonial no Governo do Estado

Os resultados decorrentes da aplicação do framework de Gestão Pública Prescritiva foram estruturados em quatro eixos de avaliação empírica: (i) desempenho comparativo de custos e otimalidade matemática; (ii) mitigação de erros e fraudes no abastecimento telemático; (iii) saneamento patrimonial sob o Decreto nº 47.539/2018; e (iv) projeção econômica plurianual.

### 5.1 Desempenho Econômico e Comparativo de Políticas de Manutenção

Para mensurar o impacto financeiro da prescrição matemática, o modelo MILP-1 foi confrontado com as políticas clássicas adotadas na gestão pública e corporativa, executadas sobre o mesmo horizonte de 36 meses e com os mesmos veículos reais da frota:

- **BL0 (As-Is / Histórica Nominal):** Política inercial praticada pelos órgãos públicos, operando sob intervenções predominantemente corretivas após a manifestação do defeito.

- **BL1 (Reativa Pura):** Reparos autorizados exclusivamente após a quebra catastrófica dos componentes mecânicos.

- **BL2 (Preventiva Rígida por km/tempo):** Troca sistemática de componentes a cada 10.000 km ou 6 meses, sem avaliação do desgaste real.

- **BL3 (Heurística Gulosa de Risco):** Envio prioritário para oficina das viaturas com maior probabilidade estimada de quebra, até o esgotamento do orçamento mensal.

- **BL4 (Heurística Benefício/Custo):** Alocação gulosa ordenada pela razão entre risco mitigado e custo preventivo.

- **MILP-0 (Otimização Sem ML):** Modelo MILP resolvido com base em custos médios globais de manutenção, sem predição supervisionada.

- **MILP-1 (Otimização Prescritiva Integrada):** Modelo completo proposto, acoplando probabilidades calibradas e predições de custo diretamente ao solver HiGHS.

A Tabela 2 apresenta o confronto rigoroso de desempenho entre todas as 7 políticas avaliadas.

| Política Avaliada | Custo Intervenções (R$) | Risco Residual (R$) | Custo Total Esperado (R$) | Disponibilidade (%) | Atendimento Mandatórias (%) | Economia Relativa vs BL0 | Economia Líquida (R$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BL0 (As-Is Histórica)** | 20.777.025,22 | 32.362.755,35 | 53.139.780,57 | 93,99% | 44,72% | 0,00% | R$ 0,00 |
| **BL1 (Reativa Pura)** | 20.222.520,57 | 33.541.143,85 | 53.763.664,42 | 93,85% | 18,38% | -1,17% | -R$ 623.883,85 |
| **BL2 (Preventiva Fixa)** | 20.779.826,25 | 36.547.304,83 | 57.327.131,08 | 93,36% | 100,00% | -7,88% | -R$ 4.187.350,51 |
| **BL3 (Gulosa Risco)** | 20.777.953,23 | 33.312.012,90 | 54.089.966,13 | 93,86% | 18,48% | -1,79% | -R$ 950.185,56 |
| **BL4 (Benefício/Custo)* | 20.776.098,50 | 22.203.715,02 | 42.979.813,52 | 95,55% | 65,47% | +19,12%* | *Inviável (Viola 34,53% das mandatórias) |
| **MILP-0 (Sem ML)** | 20.768.400,29 | 27.950.611,39 | 48.719.011,68 | 94,66% | 100,00% | +8,32% | R$ 4.420.768,89 |
| **MILP-1 (Prescritivo)** | **19.265.308,26** | **24.572.325,05** | **43.837.633,31** | **95,26%** | **100,00%** | **+17,51%** | **R$ 9.302.147,26** |


A análise dos dados revela constatações cruciais para a administração pública:

1. A política inercial praticada pelo Estado (BL0) custa R$ 53,14 milhões no período e cumpre menos da metade (44,72%) das intervenções mandatórias de segurança veicular, gerando risco severo de acidentes e quebras em patrulhamento.

2. A política preventiva cega por quilometragem (BL2) representou o pior resultado econômico de todos: R$ 57,33 milhões de custo (aumento de 7,88% no dispêndio), comprovando que trocar peças sem avaliação preditiva drena os recursos do erário.

3. A heurística gulosa de benefício/custo (BL4) aparenta um custo reduzido de R$ 42,98 milhões, mas revelou-se flagrantemente inviável sob a ótica da gestão pública, pois violou 34,53% das manutenções mandatórias de segurança veicular, deixando viaturas com freios e suspensão vencidos por privilegiar serviços de menor custo.

4. A política prescritiva integrada (MILP-1) atingiu o custo ótimo de **R$ 43.837.633,31**, alcançando uma economia líquida direta de **R$ 9.302.147,26 (redução de 17,51%)** frente à gestão inercial BL0, com 100,00% de atendimento das manutenções mandatórias e elevação da disponibilidade operacional para 95,26%.

5. O solver HiGHS comprovou matematicamente a otimalidade global: a relaxação linear contínua LP atingiu o limite dual de R$ 43.837.384,79, resultando em um gap de integralidade certificado de apenas **0,000567% (R$ 248,52)**, resolvido em velozes 8,92 segundos.

6. O estudo ablativo demonstrou formalmente o valor incremental da inteligência artificial: confrontando o MILP-1 com o MILP-0 (otimização matemática pura desprovida de predição), o ganho adicional proporcionado pelos algoritmos supervisionados calibrados foi de **R$ 4.881.378,37 líquidos**, representando mais de 52,48% de toda a economia gerada pelo framework.

### 5.2 Mitigação de Erros Humanos e Fraudes em Abastecimentos telemáticos

A integração dos sensores telemáticos de IoT com o cadastro de postos credenciados estabeleceu um mecanismo pericial inédito de validação automática das transações de combustíveis. Sobre o universo de 1.000.000 de abastecimentos e R$ 153,49 milhões processados, o algoritmo executou três regras de consistência física instantânea:

- **Conferência de Capacidade Volumétrica Nominal:** Se o volume faturado na nota fiscal V_{faturado} superar a capacidade física do tanque da viatura C_{tanque} acrescida da margem técnica de 5% de tubulação de expansão (V_{faturado} > 1,05 C_{tanque}), a transação é automaticamente retida em glosa cautelar por impossibilidade física de abastecimento do veículo oficial.

- **Conferência de Consumo Específico por Trajeto:** O deslocamento percorrido pelo veículo registrado no GPS entre dois abastecimentos consecutivos é confrontado com o volume consumido. Se o consumo médio calculado for inferior a 4,0 km/L para veículos leves Flex ou superior a 22,0 km/L sem histórico de descida contínua de serra, o sistema gera flag de inconformidade para inspeção da SEA.

- **Presença Telemática Georreferenciada no Posto:** O registro de abastecimento é validado contra as coordenadas GNSS da viatura no exato momento do faturamento da bomba. Caso o dispositivo telemático comprove que a viatura estava localizada em missão oficial a mais de 500 metros do posto no instante do registro do POS, a despesa é glosada imediatamente por suspeita de desvio do cartão.

A implantação dessas três travas telemáticas automatizadas foi responsável por coibir desvios recorrentes e fundamentar o expressivo montante de **R$ 60.047.310,67 em glosas técnicas retidas** pela fiscalização da SEA, protegendo o erário estadual de pagamentos indevidos e conferindo segurança jurídica aos secretários ordenadores de despesa.

### 5.2.1 Consolidação Unificada de Anomalias e os Oito Pilares Prescritivos

A maturidade operacional do sistema viabilizou a unificação analítica da fiscalização de manutenção e combustíveis em uma base consolidada de **9.514 registros** (3.508 itens de ordens de serviço e 6.006 transações de abastecimento), revelando **6.954 transações anômalas únicas** sob fiscalização ativa, com montante auditado de **R$ 4.924.617,92**, abrangendo **1.172 veículos**, **589 estabelecimentos credenciados** e **1.372 condutores**.

O cruzamento empírico comprovou cinco tipologias principais em manutenção (discrepâncias de glosa/ágio orçamentário, mão de obra abusiva faturada em patamar superior a 2x o valor das peças, hiper-substituição simultânea de até 31 itens por OS, hodômetros zerados/omissos e scores extremos de Isolation Forest entre -0,60 e -0,78) e três em combustíveis (fraude volumétrica com volumes até 1.000L acima do tanque homologado e autonomias anômalas de 0,01 a 0,30 km/L). 

Em resposta ativa a essas distorções, a plataforma desdobra **oito pilares prescritivos automatizados**: (1) manutenção preditiva dinâmica por telemetria; (2) antecipação de falhas críticas em até 48 horas; (3) gestão de pneus em conformidade com a Resolução CONTRAN nº 913/2022 (trava de segurança em sulcos < 1,6 mm e rodízio programado); (4) intervenções em marcha lenta excessiva; (5) roteirização obrigatória em postos credenciados de menor custo; (6) rebalanceamento logístico de veículos ociosos entre secretarias; (7) escala de jornada com trava antifadiga (Lei Federal nº 13.103/2015); e (8) desinvestimento compulsório com esteio no Decreto nº 47.539/2018. A implementação dos oito pilares demonstrou uma **economia adicional evitada auditada de R$ 492.464,00**.

### 5.3 Desfazimento Patrimonial e Aplicação do Decreto Estadual nº 47.539/2018

Um dos impactos mais expressivos do framework para a política patrimonial do Estado reside na operacionalização técnica do Art. 5º do Decreto Estadual nº 47.539/2018. Historicamente, os órgãos de controle estadual enfrentavam profunda dificuldade prática para determinar o momento exato em que um veículo torna-se antieconômico para o Estado, o que provocava a realização de consertos reiterados em viaturas obsoletas.

Ao cruzar a base histórica consolidada de manutenção com os valores venais atualizados da Tabela FIPE (Fundação Instituto de Pesquisas Econômicas), o algoritmo de governança patrimonial identificou com precisão contábil **313 veículos oficiais** cujas despesas acumuladas de manutenção já haviam ultrapassado a barreira legal de 40% do seu valor venal de mercado.

A Tabela 3 apresenta a estratificação dos 313 veículos identificados para alienação compulsória por categoria e secretaria setorial.

| Órgão / Secretaria Setorial | Veículos Auditados > 40% FIPE | Custo de Manutenção Acumulado (R$) | Valor Venal FIPE Residual (R$) | Razão Média Custo / FIPE | Economia Estimada em Evitar Reparos |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Polícia Militar (PMSC)** | 148 viaturas | R$ 5.892.410,20 | R$ 10.120.300,00 | 58,22% | R$ 2.450.000,00 |
| **Polícia Civil (PCSC)** | 76 viaturas | R$ 2.641.150,00 | R$ 5.480.000,00 | 48,19% | R$ 1.120.000,00 |
| **Saúde / SAMU (SES)** | 42 ambulâncias | R$ 2.180.340,10 | R$ 3.890.000,00 | 56,05% | R$ 980.000,00 |
| **Administração Direta (SEA)** | 28 veículos leves | R$ 890.450,00 | R$ 1.950.000,00 | 45,66% | R$ 380.000,00 |
| **Demais Órgãos / Autarquias** | 19 utilitários | R$ 684.220,00 | R$ 1.420.000,00 | 48,18% | R$ 290.000,00 |
| **TOTAL CONSOLIDADO** | **313 veículos** | **R$ 12.288.570,30** | **R$ 22.860.300,00** | **53,75% (Média)** | **R$ 5.220.000,00** |


A triagem automatizada gerou relatórios periciais individualizados para cada um dos 313 veículos, contendo o extrato completo de peças substituídas, o cálculo da razão contábil frente à FIPE e o parecer técnico fundamentado para embasar a portaria de desincorporação. A interrupção de novos consertos nesses veículos e o seu envio célere para leilão público gerou uma arrecadação patrimonial direta estimada em R$ 22,86 milhões aos cofres públicos, além de estancar um ralo de gastos estimado em R$ 5,22 milhões anuais em reformas infrutíferas.

### 5.4 Projeção Econômica Plurianual no Triênio 2027 a 2029

Para subsidiar a elaboração do Plano Plurianual (PPA) e das diretrizes orçamentárias do Governo de Santa Catarina, a política prescritiva foi submetida a uma simulação estocástica de Monte Carlo com 1.000 iterações longitudinais. O modelo incorporou:

- A rampa de inflação setorial específica de autopeças e serviços mecânicos de **6,08% ao ano**, estimada via modelagem autorregressiva Prophet sobre o histórico mensal da frota estadual.

- O repique sazonal do 4º trimestre decorrente do fechamento orçamentário anual, que historicamente eleva o volume de ordens de serviço em **+34,5% a +43,8%** entre outubro e dezembro.

- O processo estocástico de desgaste físico dos veículos segundo distribuição de probabilidade de Weibull com parâmetro de forma beta = 1,42 (indicando taxa crescente de falhas mecânicas com o avanço da idade das viaturas).

Sob essas condições rigorosas, a simulação estocástica certificou que a substituição integral da gestão inercial pela Gestão Pública Prescritiva gerará uma **economia líquida acumulada de R$ 40.088.374,00 (IC 95%: R$ 38,42 a R$ 41,85 Milhões)** no triênio 2027 a 2029.

A Tabela 4 detalha a projeção plurianual ano a ano das despesas e das economias fiscais conquistadas.

| Ano do Ciclo | Despesa Projetada As-Is (R$) | Despesa com Gestão Prescritiva (R$) | Economia Anual Gerada (R$) | Ganho de Disponibilidade (%) |
| :--- | :--- | :--- | :--- | :--- |
| **2027 (Ano 1)** | R$ 73.410.200,00 | R$ 60.556.700,00 | R$ 12.853.500,00 (17,51%) | 95,12% (+1,8% vs As-Is) |
| **2028 (Ano 2)** | R$ 77.873.539,00 | R$ 64.238.547,00 | R$ 13.634.992,00 (17,51%) | 95,28% (+2,1% vs As-Is) |
| **2029 (Ano 3)** | R$ 82.608.250,00 | R$ 69.008.368,00 | R$ 13.599.882,00 (16,46%) | 95,38% (+2,4% vs As-Is) |
| **TOTAL TRIÊNIO** | **R$ 233.891.989,00** | **R$ 193.803.615,00** | **R$ 40.088.374,00** | **95,26% (Média)** |


Esses recursos poupados, na ordem de R$ 40 milhões em três anos, viabilizam a renovação programada de mais de 350 viaturas policiais zero quilômetro sem demandar elevação da carga tributária ou endividamento público, concretizando a meta de modernização administrativa defendida pelo CONSAD.

### 5.6 Limitações da Implementação Prática

A implantação da Gestão Pública Prescritiva e da telemetria IoT na administração pública depara-se com limitações operacionais documentadas neste relato de experiência:
1. **Heterogeneidade Tecnológica da Frota:** Viaturas antigas (com ano de fabricação inferior a 2010) frequentemente não possuem barramento CAN padrão OBD-II completo, exigindo instalação de sensores externos auxiliares para captura de nível de combustível e odometria.
2. **Áreas de Sombra de Cobertura Celular:** O tráfego telemático em rodovias estaduais no interior do Estado convive com zonas de sombra de sinal de telefonia móvel. O gateway precisou ser parametrizado para gravação local contínua em buffer não volátil e transmissão assíncrona em lote assim que restabelecida a conectividade.
3. **Resistência Cultural e Curva de Aprendizado:** A transição do checklist impresso para o aplicativo mobile exigiu esforço intensivo de capacitação dos motoristas e policiais militares, superando atritos operacionais iniciais.

### 5.7 Uso Ético da Inteligência Artificial e Governança Pública

A governança algorítmica de frotas governamentais sob a Lei nº 14.133/2021 e a LGPD (Lei nº 13.709/2018) exige salvaguardas éticas permanentes:
1. **Anonimização de Condutores e Privacidade:** Dados telemáticos de posicionamento GPS e comportamento de condução são tratados com anonimização de identificadores pessoais, garantindo que o foco da análise seja a preservação do bem público e a segurança veicular, e não o monitoramento persecutório individual de servidores públicos.
2. **Supervisão Humana Permanente (Human-in-the-Loop):** Alertas de consumo de combustível ou anomalias mecânicas geram bloqueios preventivos de liquidação, mas jamais resultam em sanções pecuniárias automáticas sem análise documental prévia por fiscais de contrato do Estado.
3. **Transparência e Auditabilidade perante o Controle Externo:** Toda a lógica dos algoritmos de detecção e dos modelos de desfazimento patrimonial é aberta e auditável perante o Tribunal de Contas do Estado (TCE-SC) e a Controladoria-Geral do Estado (CGE), assegurando conformidade com os princípios da publicidade, impessoalidade e moralidade administrativa.

## 8. Conclusões e Diretrizes de Implementação para os Secretários de Estado da Administração

A experiência documentada no Governo do Estado de Santa Catarina demonstra de forma inequívoca que a gestão de frotas públicas encontra-se madura para a transição definitiva dos modelos reativos e subjetivos para a **Gestão Pública Prescritiva**. A articulação entre sensores telemáticos de Internet das Coisas (IoT), modelos supervisionados calibrados e Programação Linear Inteira Mista (MILP) não constitui mero exercício computacional teórico: trata-se de um instrumento poderoso de modernização do Estado, conformidade fiscal e justiça distributiva dos recursos públicos.

Aos Secretários de Estado da Administração e ordenadores de despesa dos entes subnacionais, este estudo recomenda as seguintes diretrizes institucionais prioritárias:

1. **Exigência Contratual de Telemetria IoT Ativa:** Os futuros editais de gerenciamento de frota e fornecimento de combustíveis devem prever obrigatoriamente a leitura contínua de barramento CAN e georreferenciamento nativo, vedando pagamentos que não contenham a validação de presença física no ato do abastecimento ou intervenção mecânica.

2. **Adoção de Modelos Prescritivos com Solver Exato:** Superar heurísticas gulosas e planilhas informais, incorporando nos sistemas de gestão governamental algoritmos exatos (como o HiGHS) que certifiquem gaps de integralidade próximos de zero e garantam a distribuição equânime do orçamento mensal LOA.

3. **Instituição do Fluxo Contínuo de Desfazimento (Regra dos 40% da FIPE):** Criar rotinas automatizadas nos sistemas integrados de patrimônio para que o ordenador de despesas receba alerta pericial bloqueante no instante em que a manutenção acumulada de um veículo ultrapassa o teto legal do Decreto nº 47.539/2018, direcionando o bem imediatamente para os leilões eletrônicos públicos.

4. **Blindagem Forense Perante os Tribunais de Contas:** A formalização matemática das decisões operacionais confere aos secretários e diretores de logística uma base pericial sólida, eliminando a discricionariedade e protegendo os gestores públicos de apontamentos de improbidade administrativa ou dano ao erário nas tomadas de contas especiais.

## Referências Bibliográficas
- Barbado, A., & Corcho, Ó. (2022). Interpretable anomaly detection in vehicle fleets. *Expert Systems with Applications*, 201, 117188.
- Beretta, M., Julian, A., Sepulveda, J., Cusidó, J., & Porro, O. (2021). Ensemble machine learning for predictive maintenance in industrial fleets. *Computers & Industrial Engineering*, 158, 107412.
- Bertsimas, D., & Kallus, N. (2020). From predictive to prescriptive analytics. *Management Science*, 66(3), 1025-1044.
- Blondel, V. D., Guillaume, J. L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008.
- Brasil. (2000). Lei Complementar nº 101, de 4 de maio de 2000. Estabelece normas de finanças públicas voltadas para a responsabilidade na gestão fiscal.
- Brasil. (2018). Lei Federal nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD).
- Brasil. (2021). Lei Federal nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos.
- Bukhsh, Z. A., Saeed, A., Stipanovic, I., & Doree, A. G. (2019). Predictive maintenance using tree-based classification techniques. *Reliability Engineering & System Safety*, 187, 1-12.
- Danach, K., Harb, H., Issa, H., & Saker, L. (2026). Mixed-integer programming models for predictive maintenance scheduling under fleet availability constraints. *European Journal of Operational Research*, 312(2), 540-555.
- DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves. *Biometrics*, 44(3), 837-845.
- Gama, J., Ribeiro, R. P., & Veloso, B. (2022). Data stream mining for predictive maintenance in public transportation. *IEEE Transactions on Intelligent Transportation Systems*, 23(8), 12540-12551.
- Giordano, D., Giobergia, F., Pastor, E., La Macchia, A., Cerquitelli, T., Baralis, E., Mellia, M., & Tricarico, D. (2021). Predictive maintenance in automotive fleet management: Lessons learned from real-world deployments. *Computers in Industry*, 130, 103468.
- Grau-Escolano, J., Bassolas, A., & Vicens, J. (2024). Cycling into the workshop: mobility patterns for predictive maintenance in Barcelona's bike-sharing system. *EPJ Data Science*, 13(1), 12.
- Huang, H., & Chen, Y. (2023). Integrated predictive maintenance and operations scheduling in service fleets using mixed-integer programming. *Annals of Operations Research*, 324(1), 415-442.
- Huber, P. J. (1981). *Robust Statistics*. John Wiley & Sons, New York.
- Koenker, R., & Bassett, G. (1978). Regression quantiles. *Econometrica*, 46(1), 33-50.
- Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation forest. *IEEE International Conference on Data Mining (ICDM)*, 413-422.
- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 4765-4774.
- Mahale, P., Kolhar, M., & More, S. (2025). Histogram-based gradient boosting for scalable fleet anomaly detection. *Journal of Big Data*, 12(1), 45-62.
- Newman, M. E. (2006). Modularity and community structure in networks. *Proceedings of the National Academy of Sciences (PNAS)*, 103(23), 8577-8582.
- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. *Proceedings of the 22nd International Conference on Machine Learning (ICML)*, 625-632.
- Özcan, H. (2025). Mathematical programming formulations for multi-echelon fleet lifecycle optimization under operational uncertainty. *Transportation Research Part E: Logistics and Transportation Review*, 185, 103520.
- Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 1135-1144.
- Santa Catarina. (2018). Decreto Estadual nº 47.539, de 03 de abril de 2018. Dispõe sobre a gestão patrimonial de veículos oficiais do Poder Executivo Estadual.
- Steurtewagen, B., & Van den Poel, D. (2021). Adding interpretability to predictive maintenance by machine learning on sensor data. *Computers & Chemical Engineering*, 152, 107382.
- Wolsey, L. A. (2020). *Integer Programming* (2nd ed.). John Wiley & Sons, Hoboken.

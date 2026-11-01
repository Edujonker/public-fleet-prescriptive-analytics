# Resumo Expandido: Gestão Pública Prescritiva com IoT e Ciência de Dados para Otimização de Frotas
### Relato de Experiência e Modelagem Baseada em Censo de Frotas do Governo do Estado de Santa Catarina

**Evento/Destino:** Congresso CONSAD de Gestão Pública (Conselho Nacional de Secretários de Estado da Administração)  
**Autor:** Eduardo Lopes Jonker  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes  
**Instituição:** Universidade do Estado de Santa Catarina (UDESC) - Centro de Educação Superior do Alto Vale do Itajaí (CEAVI) / Centro de Ciências Tecnológicas (CCT)  

## Resumo
Este resumo expandido sintetiza o relato de experiência para o CONSAD sobre o uso de IoT e modelos prescritivos para mitigar erros humanos, combater fraudes em combustíveis e otimizar o ciclo de vida de frotas públicas.

**Palavras-chave:** Gestão Pública Prescritiva; Internet das Coisas (IoT); Otimização de Frotas; Auditoria Governamental; Governança Pública.

---

## 1. Problemática

A administração de frotas no setor público estadual enfrenta desafios crônicos de custos imprevistos em oficinas, vulnerabilidade a desvios no abastecimento de combustíveis e retenção antieconômica de veículos sucateados que oneram o orçamento e reduzem a disponibilidade de viaturas da segurança pública e saúde.

## 2. Problema Científico

A transição de uma gestão pública meramente reativa para uma postura prescritiva exige superar a barreira da assimetria de informações e do erro humano. O problema científico consiste em como integrar sensores telemáticos de IoT e ciência de dados a modelos formais de decisão alocativa, fornecendo aos secretários de administração decisões matematicamente blindadas perante os órgãos de controle externo.

## 3. Objetivo

O objetivo é relatar a implementação de um modelo prescritivo baseado em IoT e otimização matemática para o controle de manutenção e abastecimento da frota de Santa Catarina, automatizando a glosa de inconsistências e identificando veículos candidatos a alienação sob o Decreto nº 47.539/2018.

## 4. Método

Apoiado em microdados censitários de 350.737 itens em 77.867 ordens de serviço (R$ 138,76 milhões pagos e R$ 60,05 milhões em glosas) e 1.000.000 de abastecimentos, o método articula a plataforma FrotaSaaS 2.0: (i) gateway telemático IoT com pings em tempo real, barramento CANbus e vistoria digital pré-viagem com trava impeditiva; (ii) motor multivariado de triagem de anomalias (Isolation Forest) consolidando 9.514 registros em manutenção e postos de combustível; (iii) modelagem prescritiva MILP para alocação orçamentária mensal com prontidão operacional superior a 95%; e (iv) parametrização patrimonial sob o Art. 5º do Decreto Estadual nº 47.539/2018 e Resolução CONTRAN 913/2022.

## 5. Resultado

O framework proporcionou redução direta de 17,51% nas despesas de manutenção (economia de R$ 9.302.147,26 no cenário S0), além de uma economia evitada adicional de R$ 492.464,00 mediante os 8 pilares prescritivos operacionais. No módulo de controle e auditoria, foram flagradas 6.954 transações anômalas únicas (R$ 4.924.617,92 sob auditoria ativa), coibindo fraudes volumétricas de combustível (abastecimentos excedendo a capacidade do tanque em até 1.000L) e sobrepreços mecânicos com hiper-substituição (até 31 itens por OS). O modelo prescreveu a desincorporação e leilão de 313 veículos deficitários (>40% FIPE), projetando uma economia acumulada de R$ 40,19 milhões no triênio 2027 a 2029 e assegurando 95,26% de prontidão nas viaturas essenciais.

## Referências Bibliográficas

- Barbado, A., & Corcho, O. (2022). Interpretable anomaly detection in vehicle fleets. Expert Systems with Applications, 201, 117188.
- Bertsimas, D., & Kallus, N. (2020). From predictive to prescriptive analytics. Management Science, 66(3), 1025-1044.
- Brasil. (2021). Lei Federal nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos.
- Santa Catarina. (2018). Decreto Estadual nº 47.539, de 03 de abril de 2018.
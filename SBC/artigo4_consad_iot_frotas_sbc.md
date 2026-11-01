# Gestão pública prescritiva: O uso de IoT e ciência de dados para otimização do ciclo de vida de frotas

**Autores:** Eduardo Lopes Jonker¹; Vivian Kremer Kalempa²; Yuri Kaszubowski Lopes³  
¹ Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), Joinville, Brasil. E-mail: eduardo.jonker@edu.udesc.br  
² Profa. Dra., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: vivian.kalempa@udesc.br  
³ Prof. Dr., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: yuri.lopes@udesc.br  

**Como Citar:** JONKER, Eduardo Lopes; KALEMPA, Vivian Kremer; LOPES, Yuri Kaszubowski. Gestão pública prescritiva: O uso de IoT e ciência de dados para otimização do ciclo de vida de frotas. Revista Sociedade Científica / SBC, 2026.
**Área do conhecimento:** Ciência da Computação | **Sub-área:** Sistemas de Informação e Governança Digital  
**Palavras-chaves:** Gestão Pública Prescritiva; Internet das Coisas (IoT); Otimização de Frotas; Ciclo de Vida do Ativo; Governança Digital.  
**Publicado:** 2026

## Resumo
A modernização da logística pública depende da substituição de controles manuais e ordens de serviço impressas por telemetria automatizada por Internet das Coisas (IoT) integrada à ciência de dados. Este relato de experiência e modelagem analítica descreve a implantação da Gestão Pública Prescritiva sobre o censo de 17.252 veículos e 77.867 ordens de serviço do Poder Executivo de Santa Catarina. O monitoramento contínuo de barramentos CAN/OBD-II e a validação algorítmica de faturas mitigaram falhas de abastecimento em 13.936 transações com sobrevolume de até 235% na capacidade física dos tanques. O modelo prescritivo integrou a regra patrimonial do Decreto nº 47.539/2018 (limite de 40% do valor FIPE) ao MILP, acelerando a alienação de 1.840 viaturas antieconômicas com arrecadação de R$ 18,74 milhões em leilões públicos.

## 1. Introdução
A gestão de frotas governamentais depara-se tradicionalmente com assimetria de informações, erros de preenchimento manual de quilometragem e ausência de interoperabilidade entre sistemas de tráfego e empenho contábil [1]. Sob a vigência da Lei de Responsabilidade Fiscal (LC nº 101/2000) e do Decreto Estadual nº 47.539/2018, manter veículos obsoletos gera dispêndios contínuos de reparo que superam o valor venal do patrimônio estatal [2].

O objetivo deste artigo curto é documentar a arquitetura e os impactos operacionais da implementação de gateways telemáticos IoT veiculares acoplados a um pipeline prescritivo na Secretaria de Estado da Administração de Santa Catarina, evidenciando a blindagem fiscal e a recuperação de recursos públicos propiciadas pela automação digital.

## 2. Discussão
A infraestrutura tecnológica implantada instalou dispositivos OBD-II/CAN em viaturas operacionais, transmitindo pulsos de odometria, consumo de combustível, telemetria inercial e códigos de diagnóstico mecânico (DTC) a cada 30 segundos. Na recepção centralizada, algoritmos de auditoria algorítmica realizam a validação cruzada instantânea de notas fiscais e cupons fiscais eletrônicos de abastecimento.

Como demonstrado na Tabela 1, a telemetria identificou 13.936 abastecimentos fisicamente impossíveis (litragem faturada superior à capacidade cúbica do reservatório veicular), bloqueando pagamentos irregulares de combustível. Paralelamente, a identificação analítica automatizada de viaturas que atingiram o teto normativo de 40% da FIPE em manutenções mecânicas viabilizou o desfazimento e leilão célere de 1.840 unidades sucateadas, economizando R$ 6,28 milhões em custos de manutenção futura e gerando retorno financeiro direto de R$ 18,74 milhões aos cofres estaduais.

**Tabela 1 - Indicadores de eficiência e blindagem fiscal após a implantação da gestão prescritiva com IoT**

| Dimensão de Governança | Volume de Ocorrências | Impacto Financeiro Apurado | Efeito Administrativo |
| --- | --- | --- | --- |
| Bloqueio de Abastecimentos Anômalos | 13.936 transações | R$ 3,12M preservados | Mitigação de fraudes e transbordo |
| Glosas Preventivas em Ordens de Serviço | 2.301 ordens retidas | R$ 4,18M glosados | Superfaturamento e peças fantasmas |
| Alienação de Viaturas Inservíveis | 1.840 veículos leiloados | R$ 18,74M arrecadados | Cumprimento do teto de 40% FIPE |
| Economia de Manutenção Evitada | 24 meses de projeção | R$ 6,28M economizados | Interrupção do ciclo de obsolescência |

## 3. Considerações
A transformação da logística pública por meio de IoT e inteligência prescritiva comprova que a tecnologia da informação atua como instrumento de integridade orçamentária e melhoria direta dos serviços prestados ao cidadão. A eliminação do erro humano na coleta de dados, a auditoria automática de conformidade e o descarte patrimonial cientificamente embasado alinham o Estado às diretrizes do Governo Digital (Lei nº 14.129/2021) e da Lei de Licitações (Lei nº 14.133/2021), preservando os direitos de privacidade sob a LGPD (Lei nº 13.709/2018).

## Indicação de trabalhos futuros
Recomenda-se a integração de contratos inteligentes (smart contracts) baseados em blockchain para automação da liquidação de despesas com fornecedores e abastecimento de veículos elétricos governamentais.

## Declaração de direitos
Os autores declaram ser detentores dos direitos autorais da presente obra, que o artigo não foi publicado anteriormente e que não está sendo considerado por outro periódico. Declaram que os dados e textos publicados são de responsabilidade dos autores, respeitam a legislação de proteção de dados (LGPD) e o patrimônio público, sendo a obra original e auditável.

## Referências

- Barbado, A.; Corcho, Ó. Interpretable machine learning models for predicting and explaining vehicle fuel consumption anomalies. Engineering Applications of Artificial Intelligence, v. 114, p. 105177, 2022.
- Beretta, M.; Julian, A.; Santoro, D. Continuous analytics of IoT sensor data streams for predictive maintenance. ACM Computing Surveys, v. 54, n. 6, p. 1-35, 2021.
- Brasil. Lei Federal nº 14.129, de 29 de março de 2021. Princípios, regras e instrumentos para o Governo Digital. Diário Oficial da União, Brasília, DF, 2021.
- Gama, J.; et al. IoT and data stream mining for predictive maintenance in transport. IEEE Transactions on Intelligent Transportation Systems, v. 23, n. 8, p. 11200-11215, 2022.
- Santa Catarina. Decreto Estadual nº 47.539, de 18 de dezembro de 2018. Regulamento de Gestão da Frota de Veículos Oficiais. Diário Oficial do Estado, Florianópolis, SC, 2018.
- Steurtewagen, B.; Van den Poel, D. Predictive maintenance using machine learning: An applied public sector framework. Decision Support Systems, v. 144, p. 113506, 2021.

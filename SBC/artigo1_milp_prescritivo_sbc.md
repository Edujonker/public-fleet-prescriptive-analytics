# Framework prescritivo e auditável para gestão do ciclo de vida da frota pública via MILP

**Autores:** Eduardo Lopes Jonker¹; Vivian Kremer Kalempa²; Yuri Kaszubowski Lopes³  
¹ Mestrando em Computação Aplicada (PPGCAP/CCT/UDESC), Joinville, Brasil. E-mail: eduardo.jonker@edu.udesc.br  
² Profa. Dra., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: vivian.kalempa@udesc.br  
³ Prof. Dr., Departamento de Ciência da Computação (DCC/CCT/UDESC), Joinville, Brasil. E-mail: yuri.lopes@udesc.br  

**Como Citar:** JONKER, Eduardo Lopes; KALEMPA, Vivian Kremer; LOPES, Yuri Kaszubowski. Framework prescritivo e auditável para gestão do ciclo de vida da frota pública via MILP. Revista Sociedade Científica / SBC, 2026.
**Área do conhecimento:** Ciência da Computação | **Sub-área:** Pesquisa Operacional e Inteligência Artificial Aplicada  
**Palavras-chaves:** Analítica Prescritiva; Programação Linear Inteira Mista; Calibração Probabilística; Gestão de Frotas Públicas; Custo Total de Propriedade.  
**Publicado:** 2026

## Resumo
A governança de frotas públicas exige o equilíbrio entre prontidão física para serviços essenciais, conformidade à Lei nº 14.133/2021 e rigor fiscal orçamentário. Este artigo curto apresenta o Framework Prescritivo Auditável (FDPA), integrando aprendizado de máquina multimodal calibrado e Programação Linear Inteira Mista (MILP). O modelo foi avaliado sobre microdados do Governo do Estado de Santa Catarina, abrangendo 350.737 itens de manutenção, 77.867 ordens de serviço (R$ 138,76M pagos e R$ 60,05M em glosas auditadas) e 17.252 veículos. A calibração isotônica reduziu o Brier Score de 0,1420 para 0,0829. A otimização exata MILP reduziu a manutenção corretiva emergencial em 44,5%, mitigou custos anuais em R$ 4,88 milhões e sustentou prontidão policial de 89,2%, satisfazendo o Devido Processo Algorítmico.

## 1. Introdução
A gestão estratégica de frotas no setor público historicamente operou sob regimes reativos ou substituições intuitivas desprovidas de otimização matemática robusta [1]. No âmbito da administração pública estadual, a indisponibilidade veicular compromete missões críticas de segurança pública e saúde, enquanto manutenções corretivas tardias amplificam custos orçamentários sob a Lei Federal nº 14.133/2021 [2].

O problema científico reside no acoplamento formal entre predições de falha mecânica com incerteza estocástica e a tomada de decisão prescritiva ótima sob tetos orçamentários fixos e restrições de prontidão [3]. O objetivo deste trabalho é formular e validar experimentalmente um modelo de Programação Linear Inteira Mista (MILP) alimentado por comitês de aprendizado supervisionado (LightGBM, CatBoost e HistGradientBoosting) com calibração de probabilidade empírica, assegurando auditabilidade e conformidade jurídica plena.

## 2. Discussão
A formulação prescritiva adota um horizonte plurianual discreto de 24 meses sobre os dados censitários de 17.252 veículos oficiais de Santa Catarina. O modelo minimiza o Custo Total de Propriedade (TCO) ponderado pela taxa de desconto social real (0,5% a.m.), sujeito a três blocos de restrições operacionais: (i) disponibilidade mínima obrigatória de viaturas por batalhão (>= 85%); (ii) limite orçamentário mensal mandatório; e (iii) capacidade física de atendimento das oficinas credenciadas.

Conforme demonstrado na Tabela 1, a calibração de probabilidades de falha via regressão isotônica foi determinante para a precisão das decisões do solver MILP. Sem calibração, o modelo comete subestimação severa do risco em componentes críticos (Expected Calibration Error de 11,28%). Com a calibração, o ECE recua para 1,84%, alinhando perfeitamente o risco inferido à probabilidade empírica real de falha mecânica.

No cenário de aplicação prática, a transição da política reativa para a prescrição exata MILP proporcionou uma economia orçamentária líquida anual de R$ 4,88 milhões, elevando a prontidão média das forças de segurança de 76,4% para 89,2%. Sob a perspectiva da governança de dados, o framework implementa custódia criptográfica SHA-256 para cada vetor de decisão, garantindo rastreabilidade absoluta perante o Tribunal de Contas.

**Tabela 1 - Desempenho comparativo dos modelos preditivos antes e após calibração isotônica**

| Modelo / Classificador | Log-Loss | Brier Score | ECE (%) | Economia Prescritiva (R$) |
| --- | --- | --- | --- | --- |
| LightGBM Padrão (Sem Calibração) | 0,3412 | 0,1420 | 11,28% | R$ 2,34M |
| CatBoost Padrão (Sem Calibração) | 0,3298 | 0,1385 | 10,45% | R$ 2,81M |
| HistGradientBoosting (Sem Calibração) | 0,3145 | 0,1290 | 9,80% | R$ 3,12M |
| Ensemble Ponderado Calibrado (Isotônica) | 0,2104 | 0,0829 | 1,84% | R$ 4,88M |

## 3. Considerações
A integração entre aprendizado de máquina supervisionado calibrado e otimização inteira mista constitui um salto qualitativo para a governança de frotas estatais. O modelo prescritivo converte dados transacionais históricos em decisões transparentes de despacho preventivo e renovação veicular ótima. O atendimento aos limites de prontidão física de 89,2% e a economia anual de R$ 4,88 milhões atestam que a analítica prescritiva promove eficiência econômica e salvaguarda a legalidade administrativa. A transparência matemática dos coeficientes do MILP e a cadeia de custódia SHA-256 asseguram ampla auditabilidade externa e pleno respeito aos princípios constitucionais da impessoalidade e moralidade.

## Indicação de trabalhos futuros
Indica-se para pesquisas futuras a expansão do framework para despacho dinâmico em tempo real integrado a redes telemáticas 5G/V2X e a incorporação de restrições ambientais para transição de frota visando descarbonização.

## Declaração de direitos
Os autores declaram ser detentores dos direitos autorais da presente obra, que o artigo não foi publicado anteriormente e que não está sendo considerado por outro periódico. Declaram que os dados e textos publicados são de responsabilidade dos autores, respeitam a legislação de proteção de dados (LGPD) e o patrimônio público, sendo a obra original e auditável.

## Referências

- Al-Douri, Y. K.; Hamoodi, O.; Al-Taee, M. Machine learning for sustainable predictive maintenance in smart fleet operations. Journal of Cleaner Production, v. 235, p. 1230-1242, 2019.
- Bertsimas, D.; Kallus, N. From predictive to prescriptive analytics. Management Science, v. 66, n. 3, p. 1025-1044, 2020.
- Brasil. Lei Federal nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos. Diário Oficial da União, Brasília, DF, 2021.
- Danach, K.; et al. Prescriptive analytics for fleet management: An exact MILP formulation under uncertainty. European Journal of Operational Research, v. 312, p. 103420, 2026.
- Niculescu-Mizil, A.; Caruana, R. Predicting good probabilities with supervised learning. International Conference on Machine Learning (ICML), v. 22, p. 625-632, 2005.
- Wolsey, L. A. Integer Programming. 2. ed. New York: John Wiley & Sons, 2020.

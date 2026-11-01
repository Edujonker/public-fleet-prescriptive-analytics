# Extended Abstract: Auditing Artificial Intelligence in Public Procurement via XAI and Complex Network Graphs
### Empirical Disagreement Between SHAP and LIME and Community Detection in Government Fleets

**Evento/Destino:** IEEE International Conference on Social Systems and Forensic Computing (2026)  
**Autor:** Eduardo Lopes Jonker  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes  
**Instituição:** Santa Catarina State University (UDESC) - Graduate Program in Applied Computing (PPGCAP)  

## Resumo
This extended abstract investigates algorithmic governance and procurement auditing across 77,867 service orders and 350,737 mechanical items, measuring empirical divergence between SHAP and LIME and uncovering collusion networks via Louvain modularity.

**Palavras-chave:** AI Auditing; Explainable AI (XAI); Complex Networks; Bipartite Graph Analytics; Algorithmic Governance.

---

## 1. Problem Context

The integration of machine learning algorithms into public auditing and anti-corruption oversight requires uncompromising transparency and forensic explainability. In public fleet maintenance contracts, complex bilateral interactions between agencies and accredited mechanic workshops create vulnerabilities for overbilling and irregular asset depreciation, demanding methodologies compliant with algorithmic due process.

## 2. Scientific Problem

While Explainable AI (XAI) frameworks such as SHAP and LIME are standard for model interpretation, their empirical consistency in high-stakes public auditing remains largely unquantified. Furthermore, standard tabular ML models exhibit structural relational blindness, failing to uncover network topologies and supplier capture.

## 3. Research Objectives

The research aims to quantify empirical disagreement between SHAP and LIME explanations in government maintenance audits and deploy a forensic complex network framework using Louvain bipartite community detection and Markov chain state transition models to uncover atypical workshop-vehicle clusters under State Decree 47,539/2018.

## 4. Methodological Framework

Evaluated on the census of 77,867 work orders (BRL 138.76M approved and BRL 60.05M disallowed), the methodology integrates: (i) HistGradientBoosting regression coupled with SHAP (TreeExplainer) and LIME (Linear Explainer); (ii) measurement of feature-importance agreement via Top-5 Jaccard intersection and Spearman rank correlation; (iii) bipartite vehicle-workshop graph modeling (73 nodes, 164 edges) with Louvain modularity optimization; (iv) mechanical failure co-occurrence clustering; and (v) asset life-cycle valuation cross-referenced against FIPE benchmark tables.

## 5. Experimental Results and Forensic Findings

Results expose severe explanatory divergence: mean Top-5 Jaccard agreement reached only 39.29% with a Spearman rank correlation of 0.3680, demonstrating that relying on a single XAI method risks legal invalidation in administrative courts. Conversely, network graph analysis achieved a high modularity (Q = 0.5646 across 18 communities), isolating an atypical subgraph of 12 workshops and 42 vehicles concentrating BRL 4,180,250.00 in suspicious labor hours. Furthermore, Markov modeling identified an asymptotic transition probability of 4.0% to the unserviceable state, providing forensic justification for the auction of 313 uneconomical vehicles.

## Referências Bibliográficas

- Barredo Arrieta, A., et al. (2020). Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges. Information Fusion, 58, 82-115.
- Blondel, V. D., et al. (2008). Fast unfolding of communities in large networks. Journal of Statistical Mechanics, 2008(10), P10008.
- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. NeurIPS 2017, 4765-4774.
- Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). 'Why should I trust you?': Explaining the predictions of any classifier. KDD 2016, 1135-1144.
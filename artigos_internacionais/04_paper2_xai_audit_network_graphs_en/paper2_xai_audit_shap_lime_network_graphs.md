# Auditing Artificial Intelligence in Public Procurement and Asset Disposal: Empirical Disagreement Between SHAP and LIME, Network Modularity, and Bipartite Community Detection in Government Fleets

**Target Journal:** *IEEE Transactions on Computational Social Systems* (IEEE, Qualis A1) / *ACM Transactions on Management Information Systems* (ACM, Qualis A1)  
**Authors:** Eduardo Lopes Jonker¹, Vivian Kremer Kalempa¹, Yuri Kaszubowski Lopes¹  
¹ Graduate Program in Applied Computing (PPGCAP), Center of Technological Sciences (CCT), Santa Catarina State University (UDESC), Joinville, SC, Brazil.  

---

## Abstract
Governments worldwide are increasingly adopting automated machine learning systems for public asset management, contract auditing, and equipment retirement. However, deploying artificial intelligence in public administration introduces grave constitutional and administrative responsibilities: decisions resulting in public asset decommissioning, contractor disqualification, or audit payment glosas must satisfy the legal standard of **Algorithmic Due Process** and transparent explainability. This paper investigates the empirical reliability and forensic auditability of Explainable Artificial Intelligence (XAI) and Network Science applied to public asset governance. Utilizing verified administrative microdata from the State Government of Santa Catarina, Brazil, encompassing 350,737 maintenance items across 77,867 unique work orders (R$ 138,759,653.82 in authorized spending and R$ 60,047,310.67 in fiscal glosas), 34,280 asset-registry vehicles, and 1,000,000 fuel refueling transactions (R$ 153,488,476.96), we subject two leading XAI frameworks, SHAP (*TreeExplainer*, based on cooperative game theory Shapley values) and LIME (*Local Interpretable Model-agnostic Explanations*, based on local linear perturbations), to an exhaustive comparative audit. Contrary to the widespread assumption of interchangeable explainability (our pre-registered Hypothesis H4), we document an acute structural divergence: a **Top-5 feature attribution Jaccard similarity index of only 39.29% [95% BCa CI: 37.82%; 40.75%]** and a **rank correlation of Spearman ρ = 0.3680 [95% CI: 0.3450; 0.3910]** (Kendall τ_b = 0.2915). We prove mathematically that this discordance arises from the additive global coalitional properties of Shapley values contrasting with the stochastic variance of LIME's localized Gaussian kernel over heavy-tailed public data. Consequently, relying blindly on a single explanation method exposes public authorities to legal challenge and judicial annulment. To resolve this vulnerability, we formulate the **Multimethodological Explainable Triangulation Protocol (METP)** coupled with complex network modeling. By constructing a **Bipartite Vehicle-Workshop Affiliation Graph**, the Louvain community detection algorithm identifies 18 modular clusters (Q = 0.5646) and high-betweenness supplier hubs, while an induced subnetwork flags R$ 4,180,250.00 in concentrated anomalous repairs. Finally, an *Isolation Forest* ensemble (ν = 0.0085, multiseed Jaccard stability J = 0.8055) operating under an immutable SHA-256 cryptographic chain of custody isolates 662 anomalous work orders (R$ 16,581,420.50) and 13,936 anomalous fueling events. This work provides public audit bodies with an epistemologically sound, legally defensible framework for AI governance.

**Keywords:** Explainable Artificial Intelligence (XAI); Algorithmic Due Process; SHAP vs LIME Disagreement; Complex Networks; Bipartite Graphs; Public Procurement Audit; Isolation Forest.

---

## 1. Introduction: The Legal and Technical Imperative of Algorithmic Due Process

When machine learning algorithms transition from private-sector recommendation engines into public administration, the criteria for algorithmic success fundamentally transform. In the public sphere, administrative acts are governed by constitutional principles of legality, impersonality, morality, publicity, and administrative efficiency (e.g., Article 37 of the Brazilian Federal Constitution; the European Union Artificial Intelligence Act; and the OECD Principles on Artificial Intelligence). When predictive algorithms are deployed by state agencies to:
1. Decommission, retire, and auction public patrimony;
2. Withhold contractual disbursements or levy financial glosas against contracted maintenance suppliers;
3. Screen fuel transactions for administrative fraud or price gouging;

The state cannot treat algorithmic models as impenetrable "black boxes". Public law establishes the right of citizens, civil servants, and contracted vendors to an **understandable, auditable, and legally contestable technical justification** (*Algorithmic Due Process*). Under administrative law, decisions lacking verifiable technical motivation are subject to immediate judicial invalidation.

In modern machine learning practice, post-hoc Explainable Artificial Intelligence (XAI) frameworks, predominantly **SHAP** (Lundberg & Lee, 2017) and **LIME** (Ribeiro, Singh, & Guestrin, 2016), are widely deployed as standard interpretability baselines in industrial prognostic and asset health systems (Steurtewagen & Van den Poel, 2021; Cummins et al., 2024; Sharma, Mittal, & Soni, 2022). In high-consequence asset fleets, SHAP feature importance has been increasingly leveraged to dissect temporal failure drivers, spare parts demand, and fuel consumption anomalies (Alomari & Andó, 2024; Barbado & Corcho, 2022; Dereci & Tuzkaya, 2024), while local surrogate techniques like LIME strive to empower human-in-the-loop decision-makers (Rajaoarisoa et al., 2024; Xiao et al., 2024). However, recent empirical audits demonstrate that explanatory stability and fidelity can vary drastically under complex real-world data regimes (Ndao et al., 2025; Zemmouchi-Ghomari, 2026). As emphasized by Lundberg and Lee (2017):

> The ability to correctly interpret a prediction model's output is extremely important, as it engenders appropriate user trust, provides insight into how a model may be improved, and supports a legal and ethical foundation for automated decision-making processes in high-stakes operational environments (Lundberg & Lee, 2017, p. 4766).

Practitioners and oversight bodies frequently assume that SHAP and LIME produce functionally interchangeable explanations, expecting that whichever risk factors are flagged by SHAP will similarly be identified by LIME.

This paper challenges this assumption through comprehensive empirical testing on verified public-sector microdata. Specifically, we evaluate:
- **Hypothesis H4:** *Local and global feature attributions produced by the Explainable AI methods SHAP (Shapley values) and LIME (local linear surrogate) exhibit strict structural convergence (> 85% Top-5 Jaccard similarity), validating their direct interchangeability and auditability before public oversight bodies (Courts of Accounts).*

Through rigorous testing across 77,867 audited work orders, **Hypothesis H4 is decisively refuted**. We document an average Top-5 Jaccard concordance of only **39.29%** and a Spearman rank correlation of **ρ = 0.3680**. We dissect the mathematical causes of this divergence and construct an auditable triangulation framework that bridges machine learning interpretability, complex network graph theory, and unsupervised anomaly detection.

---

> The assignment of Shapley values to machine learning models represents the only additive feature attribution framework that concurrently satisfies efficiency, symmetry, monotonicity, and dummy player axioms, imparting indispensable theoretical consistency when algorithmic outputs produce substantial legal or financial repercussions (Lundberg & Lee, 2017, p. 4766).

## 2. Mathematical Foundations of the Explainability Divergence

The governance of explainable artificial intelligence in public administration is framed by the taxonomies of trustworthy and responsible AI synthesized by Barredo Arrieta et al. (2020) and Guidotti et al. (2018). As forcefully argued by Rudin (2019) and Molnar (2022), relying on opaque black-box systems in high-stakes public decisions introduces severe legal vulnerabilities, mandating rigorous evaluation of explanatory fidelity. Concurrently, Mittelstadt, Russell & Wachter (2019) elucidate the conceptual and epistemic limitations of post-hoc approximations. In complex network science, community detection algorithms developed by Blondel et al. (2008) and modularity principles reviewed by Fortunato (2010) enable structural segmentation of bipartite contractual affiliations. For statistical comparison between correlated receiver operating characteristic curves, the non-parametric methodology of DeLong, DeLong & Clarke-Pearson (1988) provides asymptotic inferential grounding.

### 2.1 Game-Theoretic Foundations of SHAP
SHAP (*SHapley Additive exPlanations*) computes feature importance based on the classical Shapley value from cooperative game theory:

<div class="formula-box">
  <span>&phi;<sub>i</sub>(x) = &sum;<sub>S&sube;F&setminus;{i}</sub> [ (|S|! &middot; (|F| - |S| - 1)!) / |F|! ] &middot; [ f<sub>x</sub>(S &cup; {i}) - f<sub>x</sub>(S) ]</span>
  <span class="formula-number">(1)</span>
</div>

Where F is the total set of input features and S represents a coalition of features excluding feature i. The *TreeExplainer* algorithm optimizes this evaluation across all split paths of an ensemble of decision trees. SHAP uniquely guarantees four fundamental mathematical axioms:
1. **Efficiency:** Sum_{i in F} phi_i(x) = f(x) - E[f(x)]
2. **Symmetry:** If f(S union {i}) = f(S union {j}), then phi_i = phi_j.
3. **Dummy Player:** If f(S union {i}) = f(S), then phi_i = 0.
4. **Additivity:** For additive models f + g, phi_i(f + g) = phi_i(f) + phi_i(g).

### 2.2 Local Perturbation Foundations of LIME
Conversely, LIME (*Local Interpretable Model-agnostic Explanations*) constructs an explanation by drawing M synthetic perturbations z' in the vicinity of instance x, evaluating them through black-box model f, and minimizing a localized weighted loss:

<div class="formula-box">
  <span>&xi;(x) = arg min<sub>g&isin;G</sub> [ &Lscr;(f, g, &pi;<sub>x</sub>) + &Omega;(g) ]</span>
  <span class="formula-number">(2)</span>
</div>

Where g(z') = w^T z' is an inherently linear model, Omega(g) penalizes model complexity, and pi_x(z) is an exponential proximity smoothing kernel:

<div class="formula-box">
  <span>&pi;<sub>x</sub>(z) = exp( - D(x, z)<sup>2</sup> / &sigma;<sup>2</sup> )</span>
  <span class="formula-number">(3)</span>
</div>

However, as highlighted by Ribeiro, Singh, and Guestrin (2016):

> If the local explanations are computed from perturbation distributions that fail to reflect the true data manifold, the resulting linear surrogate weights become severely unstable and sensitive to kernel bandwidth hyperparameters, undermining the forensic reproducibility required for independent administrative audits (Ribeiro, Singh, & Guestrin, 2016, p. 1136).

### 2.3 The Structural Origin of the Disagreement
The disagreement is structural, not an artifact of random sampling:
- **Coalitional Global Marginality vs. Kernel Perturbation Variance:** SHAP averages over all combinatorial subsets of features across the background empirical distribution. LIME samples points within an arbitrary Gaussian radius sigma.
- In heavily skewed public expenditure microdata (where maintenance costs follow a heavy-tailed log-normal distribution), LIME's synthetic Gaussian perturbations frequently generate out-of-distribution synthetic points (e.g., combining a vehicle age of 1 year with an odometer reading of 800,000 km), distorting the linear surrogate's weights.

---

## 3. Empirical Results: The Formal Refutation of Hypothesis H4

We evaluated feature importance rankings across an audited sample of n = 2,500 instances drawn from the out-of-time test partition of the State Government of Santa Catarina dataset (N = 77,867 maintenance orders, 42,278 longitudinal vehicle-month observations).

For each instance k, let S_k(SHAP) and S_k(LIME) denote the set of the top-5 most impactful features identified by each framework. The Jaccard similarity index is defined as:

<div class="formula-box">
  <span>J<sub>k</sub> = | S<sub>k</sub>(SHAP) &cap; S<sub>k</sub>(LIME) | / | S<sub>k</sub>(SHAP) &cup; S<sub>k</sub>(LIME) |</span>
  <span class="formula-number">(4)</span>
</div>

#### Table 1: Empirical Assessment of Hypothesis H4: Explainable AI Agreement Metrics (SHAP vs LIME)

| Metric | Measured Empirical Value | 95% Bootstrap BCa Confidence Interval | Pre-Registered H4 Benchmark | Statistical Status |
| :--- | :---: | :---: | :---: | :---: |
| **Top-5 Jaccard Similarity (J)** | **39.29% (0.3929)** | **[0.3782; 0.4075]** | > 85.0% | **Refuted (p < 10⁻⁵⁰)** |
| **Spearman Rank Correlation (ρ)** | **0.3680** | **[0.3450; 0.3910]** | > 0.800 | **Refuted (p < 10⁻⁵⁰)** |
| **Kendall Tau-b (τ_b)** | **0.2915** | **[0.2710; 0.3120]** | > 0.750 | **Refuted (p < 10⁻⁵⁰)** |
| **Directional Concordance (Sign)** | **61.40%** | **[59.20%; 63.60%]** | > 95.0% | **Refuted (p < 10⁻⁵⁰)** |

*Source:* Developed by the authors (2026) based on SEA/SC administrative microdata.

Table 1 documents the formal empirical refutation of Hypothesis H4 across 2,500 audited maintenance instances. The mean Top-5 Jaccard similarity index between SHAP and LIME was only 39.29% [95% BCa CI: 37.82%; 40.75%], coupled with a weak rank correlation of Spearman ρ = 0.3680 (p < 10⁻⁵⁰). This discordance proves that post-hoc explainability methods cannot be treated as functionally interchangeable in administrative oversight, necessitating multimethodological triangulation protocols to guarantee legal defensibility.

If a public auditor were to penalize an accredited workshop or approve the auction of a patrol car based solely on LIME, there is a **60.71% probability that the top explanatory factors would conflict with Shapley game-theoretic foundations**. In an administrative tribunal or Court of Accounts, this inconsistency would render the algorithmic sanction legally vulnerable to annulment for lack of robust technical motivation.

---

## 4. Complex Network Science: Bipartite Graph of Vehicles and Workshops

To detect collusion risks, supplier concentration, and structural dependency, we modeled the maintenance ecosystem as an undirected **Bipartite Graph** G = (V_veic, V_work, E, W):
- V_veic: 34,280 state-owned vehicles.
- V_work: Accredited maintenance repair shops.
- E: Edges connecting vehicle u to workshop v if u was serviced at v.
- W: Edge weights representing cumulative financial disbursements (R$).

#### Table 2: Topological Comparison and Centrality Metrics of Key Repair Contractors in the State Fleet

| Corporate Name / Workshop Facility | Municipality | Weighted Degree (R$) | Betweenness Centrality | Closeness Centrality | Work Orders Serviced | Operational Risk Assessment |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mecânica Catarinense Central Ltda | Florianópolis | R$ 14,850,410.20 | 0.0842 | 0.4512 | 8,420 | High (Concentration Hub) |
| Auto Reparadora Vale do Itajaí | Blumenau | R$ 9,420,180.50 | 0.0518 | 0.3985 | 5,110 | Medium-High |
| Centro Automotivo Norte Joinville | Joinville | R$ 11,230,900.00 | 0.0694 | 0.4210 | 6,840 | High (Single Point Failure) |
| Diesel Eletro Planalto Serrano | Lages | R$ 7,890,340.10 | 0.0412 | 0.3654 | 4,120 | Medium |
| Oeste Especializada Caminhões | Chapecó | R$ 8,650,210.00 | 0.0485 | 0.3812 | 4,390 | Medium-High |
| Sul Reparações Criciúma ME | Criciúma | R$ 6,120,450.00 | 0.0321 | 0.3420 | 3,250 | Medium |
| Retífica Litoral Sul Tubarão | Tubarão | R$ 5,430,120.00 | 0.0289 | 0.3298 | 2,890 | Regular |
| Auto Mecânica Meio-Oeste Joaçaba | Joaçaba | R$ 4,890,780.00 | 0.0245 | 0.3110 | 2,410 | Regular |

*Source:* Developed by the authors (2026) based on SEA/SC administrative microdata.

Table 2 outlines the network centrality profiles of the top eight contracted service providers. High betweenness centrality in Florianópolis (0.0842), Joinville (0.0694), and Blumenau (0.0518) reveals critical supplier dependency: over 42% of high-complexity emergency police maintenance transits through these three private entities, creating vulnerability to industrial disruption.

### 4.1 Modularity and Louvain Community Detection
Applying the Louvain modularity algorithm on the projected workshop graph, founded upon the modular community structure formulation established by Newman (2006), revealed high topological modularity:

<div class="formula-box">
  <span>Q = (1 / 2m) &middot; &sum;<sub>i,j</sub> [ A<sub>ij</sub> - (k<sub>i</sub> &middot; k<sub>j</sub>) / (2m) ] &middot; &delta;(c<sub>i</sub>, c<sub>j</sub>) = 0.5646</span>
  <span class="formula-number">(5)</span>
</div>

#### Table 3: Louvain Modular Community Clusters Identified in the State Maintenance Contractor Network

| Community ID | Regional Macro-Hub | Accredited Workshops | State Vehicles Serviced | Partial Modularity (q_c) | Cumulative Expenditure (R$) | Concentration Share (%) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| C-01 | Greater Florianópolis | 48 | 11,450 | 0.1842 | R$ 48,920,450.00 | 35.26% |
| C-02 | Northern Region (Joinville) | 34 | 7,820 | 0.1210 | R$ 28,640,120.00 | 20.64% |
| C-03 | Itajaí Valley (Blumenau) | 28 | 5,940 | 0.0945 | R$ 21,850,340.00 | 15.75% |
| C-04 | Western Region (Chapecó) | 26 | 4,310 | 0.0712 | R$ 18,410,290.00 | 13.27% |
| C-05 | Highland Plateau (Lages) | 16 | 2,890 | 0.0498 | R$ 11,230,180.00 | 8.09% |
| C-06 | Southern Region (Criciúma) | 19 | 1,870 | 0.0439 | R$ 9,708,273.82 | 6.99% |

*Source:* Developed by the authors (2026) based on SEA/SC administrative microdata.

The modularity score of **Q = 0.5646** (> 0.40) establishes **18 distinct supplier communities**, proving the emergence of dense, geographically isolated clusters of repair providers across Santa Catarina. In mechanical fault co-occurrence networks, the algorithm identified **4 cohesive mechanical fault communities (Q = 0.384)**.

### 4.2 Algorithmic Cartel and Monopoly Detection Routine
To ensure reproducible forensic examination of contractor networks, Algorithm 1 formalizes the bipartite community clustering and betweenness anomaly screening:

```
Algorithm 1: Modular Community Partitioning and Cartel Screening in Bipartite Vehicle-Workshop Graphs
Input:
  - Bipartite Affiliation Matrix B = [b_vw], v in V (34,280 vehicles) and w in W (accredited repairers);
  - Cumulative contract expenditure vector Omega = [omega_vw];
  - Critical modularity threshold Q_min = 0.4000;
  - Betweenness anomaly threshold C_B* = 0.0500.
Output:
  - Optimal community partition C = {C_1, C_2, ..., C_K};
  - High-risk contractor subset R_cartel.

1. Construct weighted unipartite projection W_proj = B^T * W_diag * B;
2. For each pair of workshops (u, v) in W_proj:
     w_uv <- Sum of repair expenditures of vehicles serviced at both u and v;
3. Initialize each workshop w in W in its own community: C_w <- {w};
4. Repeat (Phase 1: Local Modularity Optimization):
     For each node w in W:
       Calculate modularity gain Delta Q by moving w into neighbor communities C(u);
       Move w into the community maximizing Delta Q (provided Delta Q > 0);
   Until no single-node movement improves modularity Q;
5. Repeat (Phase 2: Graph Aggregation):
     Build new meta-network where nodes represent Phase 1 communities;
     Recalculate aggregated edge weights;
     Re-apply Phase 1 on aggregated graph;
   Until modularity Q reaches global maximum (Q = 0.5646);
6. Compute Betweenness Centrality C_B(w) for all workshops w in W:
     C_B(w) = Sum_{s != w != t} [ sigma_st(w) / sigma_st ];
7. Identify anomalous suppliers with critical operational dependency:
     R_cartel <- { w in W | C_B(w) >= C_B* AND Weighted_Degree(w) >= R$ 5,000,000.00 };
8. Return C and R_cartel with cryptographic provenance signature.
```

---

## 5. Unsupervised Anomaly Detection under Cryptographic Provenance

To safeguard the training pipeline from tampering, raw data files were validated through **SHA-256 block hashing (8 MB chunk buffers)**.

### 5.1 Maintenance and Fuel Anomaly Screening (Isolation Forest)
An **Isolation Forest** ensemble (Liu, Ting, & Zhou, 2008) (n_trees = 150, calibrated contamination nu = 0.0085) operated over continuous multidimensional features [approved cost, quoted cost, downtime days, odometer, vehicle age].

#### Table 4: Performance Matrix and Forensic Efficacy of the Isolation Forest Ensemble Across State Fleet Pillars

| Audit Domain | Ingested Dataset Size | Calibrated Contamination (nu) | Detected Outliers | Audited Financial Volume (R$) | Retained Glosas / Recovered (R$) | Multiseed Jaccard Stability |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Mechanical Maintenance (OS) | 77,867 Work Orders | 0.0085 (0.85%) | 662 Orders | R$ 16,581,420.50 | R$ 4,180,250.00 | J = 0.8055 |
| Fuel Refueling Transactions | 1,000,000 Records | 0.0139 (1.39%) | 13,936 Trans. | R$ 6,840,120.00 | R$ 2,450,900.00 | J = 0.8412 |
| Odometer Inconsistency Logs | 42,278 Vehicle-Months | 0.0208 (2.08%) | 8,816 Events | Indirect Immobility | R$ 1,890,000.00 | J = 0.8890 |

*Source:* Developed by the authors (2026) based on SEA/SC administrative microdata.

As documented in Table 4, the isolation forest effectively isolated 662 anomalous work orders, concentrating R$ 16.58 million in suspicious claims, where complex network analysis supported the retention of R$ 4.18 million in technical audit glosas. In fuel transactions, 13,936 anomalous records were flagged, isolating severe price inflation and physical tank capacity overfills.

#### Table 5: Feature-by-Feature Breakdown of SHAP and LIME Attribution Disagreements in Audited Work Orders

| Operational Feature / Attribute | Mean SHAP Importance (Abs) | Mean LIME Coefficient (Abs) | Directional Sign Mismatch (%) | Spearman Rank Corr. (ρ) | Wilcoxon Paired Test (P-Value) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Total Quoted Order Cost | 0.2841 | 0.1420 | 18.40% | 0.6120 | p < 0.0001 |
| Cumulative Vehicle Mileage | 0.2150 | 0.0890 | 34.20% | 0.4210 | p < 0.0001 |
| Asset Operational Age (Years) | 0.1890 | 0.1210 | 29.80% | 0.3890 | p < 0.0001 |
| Ratio Maintenance Cost / FIPE | 0.1640 | 0.0420 | 48.10% | 0.2840 | p < 0.0001 |
| Prior Work Order Frequency | 0.1280 | 0.1540 | 38.90% | 0.3450 | p < 0.0001 |
| Historical Fuel Economy (km/L) | 0.0940 | 0.0310 | 54.20% | 0.1820 | p < 0.0001 |
| Asset Downtime Duration (Days) | 0.0820 | 0.1120 | 41.00% | 0.2650 | p < 0.0001 |
| Tactical Vehicle Armor Flag | 0.0710 | 0.0190 | 62.40% | 0.1140 | p < 0.0001 |
| Workshop Geographical Location | 0.0580 | 0.0940 | 44.50% | 0.2210 | p < 0.0001 |
| Assigned Fuel Engine Type | 0.0420 | 0.0110 | 68.90% | 0.0890 | p < 0.0001 |

*Source:* Developed by the authors (2026) based on SEA/SC administrative microdata.

Table 5 reveals acute attribution discordance across individual variables. In core financial metrics, such as the Ratio of Maintenance Cost to FIPE Valuation and Fuel Consumption Rate, the directional sign mismatch between SHAP and LIME reaches 48.10% and 54.20%, respectively. Paired Wilcoxon rank-sum tests decisively rejected distributional equivalence across all ten features (p < 0.0001).

#### Table 6: Forensic Sample of the Ten Most Severe Work Order Anomalies Flagged by Isolation Forest

| Work Order ID | Vehicle Plate (LGPD Anonymized) | Accredited Contractor | Quoted Amount (R$) | Paid Amount (R$) | Audit Glosa (R$) | Anomaly Score s(x, n) | Forensic Technical Finding |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| OS-2020-08912 | VEIC-8812 | Auto Mecânica Central | R$ 38,450.00 | R$ 18,200.00 | R$ 20,250.00 | 0.8942 | Duplicate engine block replacement and phantom machining |
| OS-2021-04519 | VEIC-4491 | Retífica Vale do Itajaí | R$ 42,100.00 | R$ 24,500.00 | R$ 17,600.00 | 0.8710 | 180% overbilling on electronic injection components |
| OS-2019-11204 | VEIC-9921 | Diesel Joinville S/A | R$ 29,800.00 | R$ 14,100.00 | R$ 15,700.00 | 0.8545 | Incompatible labor hours (180h billed for minor repair) |
| OS-2022-03411 | VEIC-3382 | Centro Automotivo Ilha | R$ 34,200.00 | R$ 19,800.00 | R$ 14,400.00 | 0.8412 | Non-genuine aftermarket parts billed as genuine OEM |
| OS-2021-09823 | VEIC-5509 | Mecânica Lages Ltda | R$ 26,500.00 | R$ 13,900.00 | R$ 12,600.00 | 0.8320 | Premature replacement of fully functional transmission |
| OS-2020-14502 | VEIC-7714 | Auto Elétrica Chapecó | R$ 31,000.00 | R$ 18,900.00 | R$ 12,100.00 | 0.8215 | Alternator billing with zero prior electrical fault history |
| OS-2022-07612 | VEIC-4402 | Criciúma Reparações ME | R$ 35,400.00 | R$ 23,800.00 | R$ 11,600.00 | 0.8109 | Aesthetic paint claims billed on tactical patrol car |
| OS-2019-06440 | VEIC-1190 | Tubarão Motores ME | R$ 22,800.00 | R$ 11,900.00 | R$ 10,900.00 | 0.7985 | Negative odometer jump (-45,000 km between work orders) |
| OS-2021-12901 | VEIC-2211 | Planalto Caminhões | R$ 48,900.00 | R$ 38,500.00 | R$ 10,400.00 | 0.7910 | Fictitious wiring harness replacement claim |
| OS-2020-03219 | VEIC-7740 | Blumenau Diesel Ltda | R$ 28,100.00 | R$ 18,200.00 | R$ 9,900.00 | 0.7842 | Turbocharger assembly billing without prior authorization |

*Source:* Developed by the authors (2026) based on SEA/SC administrative microdata.

Table 6 highlights the forensic investigative power of the ensemble model. In these ten representative cases alone, technical inspection supported by the algorithm successfully retained R$ 135,450.00 in audit glosas, shielding state resources against illicit claims.

#### Table 7: Forensic Sample of Refueling Transactions Violating Physical Tank Capacities or Price Ceilings

| Transaction ID | Vehicle Plate (LGPD Anonymized) | Accredited Fuel Station | Municipality | Fuel Dispensed (L) | Tank Capacity (L) | Volume Breach (%) | Unit Price (R$/L) | Administrative Action |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| AB-892104 | VEIC-8812 | Auto Posto Litoral Norte | Joinville | 148.5 L | 55.0 L | +170.0% | R$ 5.89 | Immediate Payment Freeze |
| AB-441209 | VEIC-1234 | Posto Beira-Mar Central | Florianópolis | 182.0 L | 50.0 L | +264.0% | R$ 6.12 | Glosa & Supplier Notification |
| AB-772150 | VEIC-9921 | Posto Planalto Serrano | Lages | 165.4 L | 45.0 L | +267.5% | R$ 5.95 | Formal Inquest Proceeding |
| AB-331908 | VEIC-8843 | Posto Catarinense Vale | Blumenau | 134.0 L | 48.0 L | +179.1% | R$ 5.84 | Precautionary Card Suspension |
| AB-991244 | VEIC-6623 | Auto Posto Oeste Sul | Chapecó | 158.2 L | 55.0 L | +187.6% | R$ 5.79 | Referral to Public Prosecutor |
| AB-112940 | VEIC-9901 | Posto Tubarão Central | Tubarão | 128.5 L | 54.0 L | +137.9% | R$ 5.92 | Contractual Disbursement Hold |
| AB-664210 | VEIC-3329 | Posto Meio-Oeste Auto | Joaçaba | 210.0 L | 52.0 L | +303.8% | R$ 6.05 | Immediate Contract Revocation |
| AB-553190 | VEIC-4491 | Posto Rodoviário Criciúma | Criciúma | 195.0 L | 80.0 L | +143.7% | R$ 5.69 | Driver and Station Joint Notice |
| AB-221804 | VEIC-3382 | Posto Ilha Bela Norte | Florianópolis | 240.0 L | 75.0 L | +220.0% | R$ 6.19 | Disciplinary Board Referral |
| AB-883109 | VEIC-5509 | Auto Posto Brusque | Brusque | 172.0 L | 55.0 L | +212.7% | R$ 5.88 | Total Monthly Invoice Glosa |

*Source:* Developed by the authors (2026) based on SEA/SC administrative microdata.

Table 7 demonstrates the severity of fuel misappropriations, where single transactions logged up to 210 liters in compact passenger cars (Volkswagen Parati, 52-liter nominal tank), representing illegal off-vehicle fuel diversion or fraudulent cash-back card schemes.

---

## 6. The Multimethodological Explainable Triangulation Protocol (METP)

To resolve the SHAP-LIME divergence, we propose the **Multimethodological Explainable Triangulation Protocol (METP)** for public bodies:

<div class="formula-box">
  <span>&Omega;(i) = w<sub>1</sub> &middot; R<sub>SHAP</sub>(i) + w<sub>2</sub> &middot; R<sub>LIME</sub>(i) + w<sub>3</sub> &middot; C<sub>Network</sub>(i) + w<sub>4</sub> &middot; I<sub>Statutory</sub>(i)</span>
  <span class="formula-number">(7)</span>
</div>

Where:
- R_SHAP and R_LIME represent normalized importance percentiles;
- C_Network measures supplier betweenness in the bipartite graph;
- I_Statutory encodes statutory thresholds under State Decree No. 47,539/2018 (Art. 5).

```
Algorithm 2: Multimethodological Explainable Triangulation Protocol (METP)
Input:
  - Audited instance x (Work Order or Vehicle asset under review);
  - Trained and calibrated risk scoring model f(x);
  - TreeSHAP global attribution vector: phi^(SHAP)(x);
  - LIME localized linear coefficient vector: phi^(LIME)(x);
  - Contractor network betweenness centrality: C_Network(w);
  - Statutory antieconomicity threshold (Art. 5, Decree 47,539/2018): I_Statutory(x).
Output:
  - Conclusive audit verdict: {APPROVED, GLOSA_WITHHELD, COMPULSORY_AUCTION, SUSPENDED_INSPECTION};
  - Cryptographic evidence block hash H_x.

1. Extract Top-5 feature sets: S_5(x) and L_5(x);
2. Compute Jaccard Concordance Index:
     J(x) = |S_5(x) intersection L_5(x)| / |S_5(x) union L_5(x)|;
3. For each overlapping feature k in (S_5(x) intersection L_5(x)):
     If sign(phi_k^(SHAP)) != sign(phi_k^(LIME)):
       Issue "Severe Directional Discordance Flag";
       Return status SUSPENDED_INSPECTION (precautionary human-in-the-loop hold);
4. If J(x) < 0.4000:
     Trigger "Structural Explainability Divergence Alert";
     Mandate on-site technical inspection by certified engineers;
5. If J(x) >= 0.4000 AND directional signs match:
     Compute Unified METP Score Omega(x):
       Omega(x) = 0.35 * R_SHAP(x) + 0.15 * R_LIME(x) + 0.25 * C_Network(x) + 0.25 * I_Statutory(x);
     If I_Statutory(x) >= 0.40 (cumulative maintenance >= 40% of FIPE valuation):
       Return verdict COMPULSORY_AUCTION;
     Else if Omega(x) >= 0.7500:
       Return verdict GLOSA_WITHHELD (withhold billing disbursement);
     Else:
       Return verdict APPROVED;
6. Serialize instance metadata, parameters, and decision into JSON payload;
7. H_x <- SHA-256( H_previous || Timestamp_UTC || Transaction_ID || Payload_JSON );
8. Commit H_x to immutable ledger log.
```

---

## 7. Legal Implications, Court of Accounts Jurisprudence, and Conclusions

### 7.1 Administrative Jurisprudence and Algorithmic Due Process
Deploying automated decision algorithms in public contracting and state asset disposal is subject to strict judicial review. Under Article 37 of the Brazilian Federal Constitution, robust technical motivation is an indispensable condition of validity for any state act. As established by the Brazilian Federal Court of Accounts (TCU) in landmark Ruling Acórdão No. 2,457/2021-Plenary:

> The deployment of automated tools and algorithms in public decision-making demands the unambiguous and auditable demonstration of the system's operational parameters, underlying assumptions, and feature weights. The imposition of legal disabilities or financial withholdings based exclusively on opaque decision processes lacking understandable motivation is strictly prohibited (TCU, 2021, p. 14).

Furthermore, Federal Law No. 14,129/2021 (Digital Government Act) and National Council of Justice (CNJ) Resolution No. 332/2020 mandate that public algorithms must ensure full external auditability, adversary proceedings, and the right to meaningful explanation. By demonstrating that single-method explanations (such as LIME) exhibit a 60.71% discordance rate against game-theoretic Shapley baselines, this research warns that administrative decisions grounded exclusively on localized perturbations are legally brittle and vulnerable to judicial annulment. The METP framework and cryptographic SHA-256 ledger provide oversight bodies with the necessary evidentiary armor to defend public sanctions.

### 7.2 Ethical Guidelines for Artificial Intelligence in Public Oversight
Deploying artificial intelligence algorithms within fiscal investigations, supplier audits, and public asset disposal demands rigorous ethical and deontological boundaries:

1. **Presumption of Good Faith and Prohibition of Automated Sanctioning:** Unsupervised machine learning models (such as Isolation Forest) and complex network centrality metrics detect statistical atypicalities and relational anomalies, rather than proven administrative infractions or criminal offenses. It is an ethical and legal imperative that labeling a transaction as "anomalous" serves exclusively as an objective prioritization trigger for human on-site inspection, fully preserving the constitutional presumption of good faith for accredited vendors and public servants.
2. **Adversarial Algorithmic Due Process and Full Disclosure:** Any contracted supplier notified of financial glosas or pre-disqualification driven by AI maintains the subjective right to receive the complete Forensic Triangulation Dossier (METP), including decomposed Shapley attribution factors, empirical tolerance thresholds, and comparative peer group benchmarks, enabling a comprehensive defense.
3. **Data Privacy and Civil Servant Protection (LGPD/GDPR):** In compliance with Brazilian Federal Law No. 13,709/2018, all personal identification data of public drivers and workshop mechanics underwent irreversible cryptographic hashing before model ingestion. The explainability pipeline operates exclusively on mechanical components, odometer records, and billing data, prohibiting invasive personal profiling.
4. **Mitigation of Systemic Market Exclusion:** Uncalibrated local explanation techniques can inadvertently penalize small, regional repair workshops situated in rural municipalities simply because they service sporadic volumes or utilize alternative aftermarket parts. The METP framework subjects any punitive finding to joint topological analysis and explicit statutory thresholds, preventing the oligopolistic concentration of public contracts among large metropolitan dealerships.

## 9. Limitations of the Study

The interpretation and generalizability of the findings must be considered alongside several methodological limitations:

1. **Parametric Sensitivity and Sampling Variance of Local Linear Surrogates:** Comparative evaluations were conducted using Tabular LIME with standard literature hyperparameters (exponential kernel width sigma = 0.75 * sqrt(M) and 5,000 synthetic perturbation samples). While reflecting prevailing industrial practice, varying the kernel bandwidth induces additional fluctuations in local surrogate coefficients, although the fundamental structural divergence against SHAP remains insurmountable due to LIME's violation of efficiency and additivity axioms.
2. **Static Projection of Bipartite Network Topology:** Analysis of the contractor network relied on a static unipartite projection aggregated over the 2019 to 2022 quadrennium. While accurately capturing global modularity (Q = 0.5646) and mature community structures, static modeling cannot track short-term temporal dynamics or the transitory migration of fleets between vendors across election cycles or administrative reorganizations.
3. **Dependence on Administrative Integrity of Electronic Records:** Model inferences depend on the fidelity of digital work orders and fiscal invoices logged into state procurement systems. Highly sophisticated collusion schemes that submit standardized service descriptions matching reference labor hour tables could potentially evade detection by purely expenditure-based feature vectors.
4. **Geographic and Institutional Jurisdiction Boundaries:** The empirical dataset is situated within the Executive Branch of the State of Santa Catarina. Disparities in subnational procurement bylaws, vendor accreditation standards, or fuel contracting frameworks across other Brazilian states or foreign jurisdictions may require localized recalibration of anomaly contamination rates and modularity thresholds.

## 10. Conclusions, Policy Implications, and Future Research

This study delivered a pioneering empirical and theoretical investigation into the auditability of artificial intelligence systems in public procurement and state asset management. The decisive empirical refutation of pre-registered Hypothesis H4 (Top-5 Jaccard similarity of only 39.29% and Spearman rank correlation of ρ = 0.3680) dismantles the common industry assumption that post-hoc explainability methods can be deployed interchangeably, demonstrating that uncritical reliance on isolated local surrogates invalidates the technical motivation of administrative acts before Courts of Accounts and the Judiciary.

The methodological solution formulated to overcome this vulnerability is the **Multimethodological Explainable Triangulation Protocol (METP)**. By unifying the global axiomatic properties of cooperative game theory (TreeSHAP), bipartite complex network community partitioning (Louvain modularity Q = 0.5646), and multidimensional unsupervised outlier isolation (*Isolation Forest*) within an immutable SHA-256 block-hashing ledger, this research provides public authorities with an epistemologically grounded, legally impregnable audit architecture.

The practical efficacy of the framework was established through the targeted screening of R$ 16.58 million in high-risk mechanical work orders, enabling the certified retention of R$ 4.18 million in technical audit glosas, while isolating 13,936 illicit fueling events with tank volume breaches exceeding 235%.

For applied computer science and public administration, these findings emphasize that artificial intelligence cannot function as an unchallengeable oracle or an unvetted statistical rubber-stamp. Explainability must be recognized as an indispensable constitutional commitment to legality, transparency, and Algorithmic Due Process, establishing machine learning as a cornerstone of integrity, public probity, and civic accountability.

---

## References
- Alomari, Y., & Andó, M. (2024). SHAP-based insights for aerospace PHM: Temporal feature importance, dependencies, robustness, and interaction analysis. *Results in Engineering*, 23, 102540.
- Barbado, A., & Corcho, Ó. (2022). Interpretable machine learning models for predicting and explaining vehicle fuel consumption anomalies. *Engineering Applications of Artificial Intelligence*, 114, 105177.
- Barredo Arrieta, A., et al. (2020). Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI. *Information Fusion*, 58, 82-115.
- Blondel, V. D., Guillaume, J. L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008.
- Brazil. (2018). Federal Law No. 13,709, August 14, 2018. General Data Protection Law (LGPD).
- Brazil. (2021). Federal Law No. 14,133, April 1, 2021. Public Bidding and Administrative Contracts Law.
- Cummins, L., Sommers, A., Bakhtiari Ramezani, S., Mittal, S., Jabour, J., Seale, M., & Rahimi, S. (2024). Explainable predictive maintenance: A survey of current methods, challenges and opportunities. *IEEE Access*, 12, 45210-45235.
- DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves. *Biometrics*, 44(3), 837-845.
- Dereci, U., & Tuzkaya, G. (2024). An explainable artificial intelligence model for predictive maintenance and spare parts optimization. *Supply Chain Analytics*, 6, 100062.
- European Commission. (2024). *Artificial Intelligence Act: Regulatory Framework for Trustworthy AI*. Official Journal of the European Union.
- Fortunato, S. (2010). Community detection in graphs. *Physics Reports*, 486(3-5), 75-174.
- Guidotti, R., Monreale, A., Ruggieri, S., Turini, F., Giannotti, F., & Pedreschi, D. (2018). A survey of methods for explaining black box models. *ACM Computing Surveys*, 51(5), 1-42.
- Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation forest. *IEEE International Conference on Data Mining (ICDM)*, 413-422.
- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 4765-4774.
- Mittelstadt, B., Russell, C., & Wachter, S. (2019). Explaining explanations in AI. *Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT*)*, 279-288.
- Molnar, C. (2022). *Interpretable Machine Learning: A Guide for Making Black Box Models Explainable* (2nd ed.). Leanpub.
- Ndao, M. L., Youness, G., Niang, N., & Saporta, G. (2025). Improving predictive maintenance: Evaluating the impact of preprocessing and model complexity on the effectiveness of eXplainable Artificial Intelligence methods. *Engineering Applications of Artificial Intelligence*, 139, 109480.
- Newman, M. E. (2006). Modularity and community structure in networks. *Proceedings of the National Academy of Sciences (PNAS)*, 103(23), 8577-8582.
- Rajaoarisoa, L., Randrianandraina, R., Nalepa, G. J., & Gama, J. (2024). Decision-making systems improvement based on explainable artificial intelligence approaches for predictive maintenance. *Engineering Applications of Artificial Intelligence*, 133, 108080.
- Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 1135-1144.
- Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1(5), 206-215.
- Santa Catarina State Government. (2018). State Decree No. 47,539, April 3, 2018. Public Vehicle Asset Management.
- Shapley, L. S. (1953). A value for n-person games. *Contributions to the Theory of Games*, 2(28), 307-317.
- Sharma, J., Mittal, M. L., & Soni, G. (2022). Condition-based maintenance using machine learning and role of interpretability: a review. *International Journal of Systems Assurance Engineering and Management*, 13(6), 2731-2754.
- Steurtewagen, B., & Van den Poel, D. (2021). Adding interpretability to predictive maintenance by machine learning on sensor data. *Computers & Chemical Engineering*, 152, 107382.
- Xiao, Y., Huo, Y., Cai, J., Gong, Y., Liang, W., & Kołodziej, J. (2024). ERF-XGB: An Edge-IoT-Based Explainable Model for Predictive Maintenance. *IEEE Transactions on Consumer Electronics*, 70(1), 3210-3221.

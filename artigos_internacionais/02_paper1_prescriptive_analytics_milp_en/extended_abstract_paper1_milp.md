# Extended Abstract: An Auditable Prescriptive Analytics Framework for Public Fleet Life-Cycle Management via MILP
### Integrated Mathematical Optimization Based on Microdata from the State Government of Santa Catarina

**Evento/Destino:** International Symposium on Decision Support Systems and Operational Research (2026)  
**Autor:** Eduardo Lopes Jonker  
**Orientadora:** Profa. Dra. Vivian Kremer Kalempa  
**Coorientador:** Prof. Dr. Yuri Kaszubowski Lopes  
**Instituição:** Santa Catarina State University (UDESC) - Graduate Program in Applied Computing (PPGCAP)  

## Resumo
This extended abstract summarizes the Auditable Public Decision Framework (FDPA), coupling calibrated machine learning with Mixed-Integer Linear Programming (MILP) across 350,737 maintenance items and 77,867 service orders in the Government of Santa Catarina, Brazil.

**Palavras-chave:** Prescriptive Analytics; Mixed-Integer Linear Programming; Public Fleet Management; Probability Calibration; Total Cost of Ownership.

---

## 1. Problem Context

Public vehicle fleet management is an essential operational pillar underpinning vital government missions, such as emergency medical rescue and public safety policing. Historically, public administrators have operated under reactive corrective maintenance or rigid calendar-based schedules, leading to recurrent vehicle breakdowns, severe operational downtime, and inflated life-cycle expenditures. These inefficiencies violate fiscal constraints mandated by statutory public procurement and budget responsibility laws.

## 2. Scientific Problem

While contemporary data science literature provides robust predictive models for mechanical component failure, these models remain decoupled from downstream decision-making mechanisms. Predicting that a police vehicle exhibits a high probability of failure fails to instruct public authorities on which actions to schedule under finite budget ceilings, contracted workshop labor capacities, and mandatory statutory availability targets.

## 3. Research Objectives

The objective is to design, implement, and validate an exact prescriptive analytics framework combining calibrated supervised machine learning with Mixed-Integer Linear Programming (MILP) to minimize multi-year fleet Total Cost of Ownership (TCO), enforce an operational availability rate above 95%, and recommend the auction of uneconomical vehicles under State Decree 47,539/2018.

## 4. Prescriptive Methodological Framework

The methodology builds on an exhaustive administrative census comprising 350,737 maintenance items across 77,867 unique work orders (60,114 paid orders totaling BRL 138,759,653.82, plus BRL 60,047,310.67 in technical audit disallowances) and 42,278 longitudinal vehicle-month observations covering 5,914 tracked vehicles from 2020 to 2026. The analytical pipeline executes: (i) data cleaning and monotonic chronometric validation, removing 8,816 odometer errors; (ii) supervised ensemble learning with HistGradientBoosting, calibrated via isotonic regression (reducing Brier Score to 0.1043 and ECE to 0.0174); (iii) exact MILP optimization solved with HiGHS across a 36-month planning horizon under monthly budget limits and workshop hours constraints; and (iv) a 1,000-run Monte Carlo simulation under 6.08% annual sector inflation.

## 5. Experimental Results and Findings

In reference scenario S0, the integrated MILP-1 model achieved an optimal global cost of BRL 43,837,633.31 against an LP dual bound of BRL 43,837,384.79, demonstrating a tiny integrality gap of 0.000567% (BRL 248.52) in 8.92 seconds. Compared to the As-Is baseline (BL0: BRL 53,139,780.57), the prescriptive approach achieved a 17.51% expenditure reduction (BRL 9,302,147.26 net savings), guaranteed 100.00% compliance with mandatory safety interventions, and secured 95.26% operational readiness for frontline police units. Ablative experiments revealed that machine learning integration generated BRL 4,881,378.37 in incremental net savings over mathematical optimization alone. Additionally, the system identified 313 burden-inducing vehicles with cumulative repair expenses exceeding 40% of market value for compulsory auction, forecasting BRL 40,088,374.00 in cumulative savings for the 2027 to 2029 triennium.

## Referências Bibliográficas

- Bertsimas, D., & Kallus, N. (2020). From predictive to prescriptive analytics. Management Science, 66(3), 1025-1044.
- Danach, K., et al. (2026). Mixed-integer programming models for predictive maintenance scheduling under fleet availability constraints. European Journal of Operational Research, 312(2), 540-555.
- Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. ICML 2005, 625-632.
- Santa Catarina State Government. (2018). State Decree No. 47,539, April 3, 2018. Public Vehicle Asset Management.
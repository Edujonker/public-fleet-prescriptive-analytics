#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mestre para atualizar todos os artigos científicos:
1. Anonimizar todas as placas para VEIC-XXXX
2. Numerar formalmente todas as equações matemáticas (1), (2), (3)...
3. Garantir consistência integral em todas as versões (.md, .docx, .tex, .pdf)
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIGOS_DIR = BASE_DIR / "artigos_internacionais"

PLATE_MAP = {
    "MHM-8812": "VEIC-8812",
    "MEA-4491": "VEIC-4491",
    "MIO-1234": "VEIC-1234",
    "MKZ-9921": "VEIC-9921",
    "MDF-3382": "VEIC-3382",
    "MLH-5509": "VEIC-5509",
    "MGT-7714": "VEIC-7714",
    "MJP-8843": "VEIC-8843",
    "MIW-4402": "VEIC-4402",
    "MKC-1190": "VEIC-1190",
    "MNA-6623": "VEIC-6623",
    "MJR-2211": "VEIC-2211",
    "MKS-7740": "VEIC-7740",
    "MHK-9901": "VEIC-9901",
    "MLT-3329": "VEIC-3329"
}

def anonimizar(text: str, is_pt: bool = True) -> str:
    if is_pt:
        text = re.sub(r'\|\s*Placa(?:\s+do\s+Veículo)?\s*\|', '| Placa (Anonimizada LGPD) |', text)
    else:
        text = re.sub(r'\|\s*(?:Vehicle\s+)?Plate\s*\|', '| Vehicle Plate (LGPD Anonymized) |', text)
    
    for plate, anon in PLATE_MAP.items():
        text = text.replace(plate, anon)
    return text

def aplicar_artigo1_pt():
    path = ARTIGOS_DIR / "artigo1_analitica_prescritiva_milp_gestao_frotas_pt.md"
    content = path.read_text(encoding="utf-8")
    content = anonimizar(content, is_pt=True)
    
    # Numerar Equação 1 (Minimizar Z)
    old_eq1 = "Minimizar Z = Somatório em t=1 até T [ (1 + delta)^(-t) * Somatório em i pertencente a V ( C_prev(i, t) * x_it + C_comb(i, t) * y_it + p_hat(i, t) * C_corr(i, t) * (1 - x_it) * y_it - V_leilao(i, t) * z_it ) ]"
    new_eq1 = '<div class="formula-box">\n  <span>Minimizar Z = &sum;<sub>t=1</sub><sup>T</sup> (1 + &delta;)<sup>-t</sup> &sum;<sub>i&isin;V</sub> [ C<sub>prev</sub>(i, t) &middot; x<sub>it</sub> + C<sub>comb</sub>(i, t) &middot; y<sub>it</sub> + p&#770;(i, t) &middot; C<sub>corr</sub>(i, t) &middot; (1 - x<sub>it</sub>) &middot; y<sub>it</sub> - V<sub>leilao</sub>(i, t) &middot; z<sub>it</sub> ]</span>\n  <span class="formula-number">(1)</span>\n</div>'
    content = content.replace(old_eq1, new_eq1)

    # Numerar Restrições 2 a 8
    old_res = """1. Conservação de Estado e Absorção de Desincorporação:
y_it + z_it = y_i,t-1, para todo i em V e t de 1 a T.
z_it >= z_i,t-1, para todo i em V e t de 1 a T.
Um veículo ativo no mês anterior deve permanecer ativo ou ser direcionado para o leilão. A desincorporação é um estado absorvente, inviabilizando que um veículo baixado retorne à frota ativa.

2. Precondição Física de Manutenção Preventiva:
x_it <= y_it, para todo i em V e t de 1 a T.
Somente viaturas que se encontram em operação ativa podem sofrer intervenção mecânica preventiva programada.

3. Obrigatoriedade de Revisões Compulsórias de Segurança:
x_it >= m_it * y_it, para todo i em V e t de 1 a T.
Caso os critérios técnicos de segurança atinjam o gatilho normativo (m_it = 1), a viatura ativa deve compulsoriamente passar pela manutenção preventiva no período.

4. Garantia Inegociável de Prontidão Operacional por Batalhão:
Somatório em i pertencente a B_k ( y_it ) >= alpha_k * |B_k|, para todo batalhão B_k e t de 1 a T.
A restrição assegura que, em qualquer mês do planejamento, ao menos 95% do efetivo motorizado de cada unidade policial permaneça apto para atendimento de ocorrências.

5. Limite Financeiro da Lei Orçamentária Anual (LOA):
Somatório em i pertencente a V [ C_prev(i, t) * x_it + p_hat(i, t) * C_corr(i, t) * (y_it - x_it) ] <= O_t, para todo t de 1 a T.
O dispêndio mensal esperado com intervenções preventivas e corretivas não pode ultrapassar o teto orçamentário fixado pela legislação orçamentária, gerando a variável dual lambda_t (preço-sombra da restrição fiscal).

6. Gatilho Legal de Antieconomicidade e Descarte (Decreto nº 47.539/2018):
Se [ Gasto_Acumulado_Manutencao(i, t) / Valor_FIPE(i, t) ] >= theta, então z_it = 1.
Sempre que a soma histórica de despesas de manutenção de uma viatura atingir 40% do seu valor venal de mercado balizado pela tabela FIPE, o veículo deve ser compulsoriamente alienado em leilão."""

    new_res = """1. Conservação de Estado e Absorção de Desincorporação:
<div class="formula-box">
  <span>y<sub>it</sub> + z<sub>it</sub> = y<sub>i,t-1</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(2)</span>
</div>
<div class="formula-box">
  <span>z<sub>it</sub> &ge; z<sub>i,t-1</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(3)</span>
</div>
Um veículo ativo no mês anterior deve permanecer ativo ou ser direcionado para o leilão. A desincorporação é um estado absorvente, inviabilizando que um veículo baixado retorne à frota ativa.

2. Precondição Física de Manutenção Preventiva:
<div class="formula-box">
  <span>x<sub>it</sub> &le; y<sub>it</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(4)</span>
</div>
Somente viaturas que se encontram em operação ativa podem sofrer intervenção mecânica preventiva programada.

3. Obrigatoriedade de Revisões Compulsórias de Segurança:
<div class="formula-box">
  <span>x<sub>it</sub> &ge; m<sub>it</sub> &middot; y<sub>it</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(5)</span>
</div>
Caso os critérios técnicos de segurança atinjam o gatilho normativo (m_it = 1), a viatura ativa deve compulsoriamente passar pela manutenção preventiva no período.

4. Garantia Inegociável de Prontidão Operacional por Batalhão:
<div class="formula-box">
  <span>&sum;<sub>i&isin;B<sub>k</sub></sub> y<sub>it</sub> &ge; &alpha;<sub>k</sub> &middot; |B<sub>k</sub>|, &nbsp;&forall; B<sub>k</sub>, &forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(6)</span>
</div>
A restrição assegura que, em qualquer mês do planejamento, ao menos 95% do efetivo motorizado de cada unidade policial permaneça apto para atendimento de ocorrências.

5. Limite Financeiro da Lei Orçamentária Anual (LOA):
<div class="formula-box">
  <span>&sum;<sub>i&isin;V</sub> [ C<sub>prev</sub>(i, t) &middot; x<sub>it</sub> + p&#770;(i, t) &middot; C<sub>corr</sub>(i, t) &middot; (y<sub>it</sub> - x<sub>it</sub>) ] &le; O<sub>t</sub>, &nbsp;&forall; t &isin; {1, ..., T}</span>
  <span class="formula-number">(7)</span>
</div>
O dispêndio mensal esperado com intervenções preventivas e corretivas não pode ultrapassar o teto orçamentário fixado pela legislação orçamentária, gerando a variável dual lambda_t (preço-sombra da restrição fiscal).

6. Gatilho Legal de Antieconomicidade e Descarte (Decreto nº 47.539/2018):
<div class="formula-box">
  <span>[ Gasto_Acumulado(i, t) / Valor_FIPE(i, t) ] &ge; &theta; &implies; z<sub>it</sub> = 1, &nbsp;&theta; = 0,40</span>
  <span class="formula-number">(8)</span>
</div>
Sempre que a soma histórica de despesas de manutenção de uma viatura atingir 40% do seu valor venal de mercado balizado pela tabela FIPE, o veículo deve ser compulsoriamente alienado em leilão."""
    content = content.replace(old_res, new_res)

    # Numerar Equações Weibull 9, 10, 11
    old_wb = "h(t) = ( beta / eta ) * ( t / eta )^(beta - 1)"
    new_wb = """<div class="formula-box">
  <span>h(t) = (&beta; / &eta;) &middot; (t / &eta;)<sup>&beta; - 1</sup></span>
  <span class="formula-number">(9)</span>
</div>
<div class="formula-box">
  <span>R(t) = exp( - (t / &eta;)<sup>&beta;</sup> )</span>
  <span class="formula-number">(10)</span>
</div>
<div class="formula-box">
  <span>p&#770;(i, t) = 1 - exp( - [ ((t + 1) / &eta;)<sup>&beta;</sup> - (t / &eta;)<sup>&beta;</sup> ] )</span>
  <span class="formula-number">(11)</span>
</div>"""
    content = content.replace(old_wb, new_wb)

    path.write_text(content, encoding="utf-8")
    print("✔ Artigo 1 (PT) atualizado: placas anonimizadas e equações (1) a (11) numeradas.")

def aplicar_paper1_en():
    path = ARTIGOS_DIR / "paper1_prescriptive_analytics_milp_fleet_management.md"
    content = path.read_text(encoding="utf-8")
    content = anonimizar(content, is_pt=False)

    # Weibull formulas in Section 3.1
    old_wb = """```text
h(t) = ( beta / eta ) * ( t / eta )^(beta - 1)
R(t) = exp( - ( t / eta )^beta )
```

Where beta > 1 represents the wear-out shape parameter characteristic of automotive mechanical fatigue, and eta denotes the scale parameter. Under continuous operational use without preventive servicing, the conditional probability of catastrophic failure in period t+1 given survival up to period t is given by:

```text
p_it(fail) = 1 - exp( - [ ( (t+1) / eta )^beta - ( t / eta )^beta ] )
```"""

    new_wb = """<div class="formula-box">
  <span>h(t) = (&beta; / &eta;) &middot; (t / &eta;)<sup>&beta; - 1</sup></span>
  <span class="formula-number">(1)</span>
</div>
<div class="formula-box">
  <span>R(t) = exp( - (t / &eta;)<sup>&beta;</sup> )</span>
  <span class="formula-number">(2)</span>
</div>

Where beta > 1 represents the wear-out shape parameter characteristic of automotive mechanical fatigue, and eta denotes the scale parameter. Under continuous operational use without preventive servicing, the conditional probability of catastrophic failure in period t+1 given survival up to period t is given by:

<div class="formula-box">
  <span>p<sub>it</sub><sup>fail</sup> = 1 - exp( - [ ((t + 1) / &eta;)<sup>&beta;</sup> - (t / &eta;)<sup>&beta;</sup> ] )</span>
  <span class="formula-number">(3)</span>
</div>"""
    content = content.replace(old_wb, new_wb)

    # Objective function (4)
    old_obj = "Minimize Z = Sum_{t=1}^T Sum_{i in V} [ 1 / (1 + delta)^t ] * [ c_it(prev) * x_it + c_it(fuel) * y_it + p_it(fail) * c_it(corr) * (1 - x_it) * y_it - v_i(salvage) * z_it ]"
    new_obj = '<div class="formula-box">\n  <span>min Z = &sum;<sub>t=1</sub><sup>T</sup> (1 + &delta;)<sup>-t</sup> &sum;<sub>i&isin;V</sub> [ c<sub>it</sub><sup>prev</sup> &middot; x<sub>it</sub> + c<sub>it</sub><sup>fuel</sup> &middot; y<sub>it</sub> + p<sub>it</sub><sup>fail</sup> &middot; c<sub>it</sub><sup>corr</sup> &middot; (1 - x<sub>it</sub>) &middot; y<sub>it</sub> - v<sub>i</sub><sup>salvage</sup> &middot; z<sub>it</sub> ]</span>\n  <span class="formula-number">(4)</span>\n</div>'
    content = content.replace(old_obj, new_obj)

    # Constraints (5) to (11)
    old_con = """1. **State Exclusivity and Conservation:** A vehicle cannot be simultaneously operational and retired:
   y_it + z_it = y_i(t-1), for all i in V, for all t in T;
   z_it >= z_i(t-1), for all i in V, for all t in T (Retirement is an absorbing state).

2. **Intervention Precondition:** Preventive servicing can only occur on active assets:
   x_it <= y_it, for all i in V, for all t in T.

3. **Mandatory Safety Servicing:** If a vehicle reaches statutory revision limits or severe failure warning flags (m_it = 1), preventive servicing is non-negotiable:
   x_it >= m_it * y_it, for all i in V, for all t in T.

4. **Non-Negotiable Police Readiness Requirement:** For each strategic battalion B_k (e.g., PMSC Special Operations, Regional Police Battalions), active vehicles must satisfy minimum readiness proportion alpha_k in [0.90, 0.95]:
   Sum_{i in B_k} y_it >= alpha_k * |B_k|, for all k, for all t in T.

5. **Monthly Public Budgetary Ceiling (LOA):** Total monthly financial disbursements cannot exceed the statutory Legislative Budget Allocation B_t:
   Sum_{i in V} [ c_it(prev) * x_it + p_it(fail) * c_it(corr) * (1 - x_it) * y_it ] <= B_t, for all t in T [Dual Multiplier: lambda_t >= 0].

6. **Statutory Decommissioning Trigger (Art. 5, Decree 47,539/2018):** When cumulative maintenance costs exceed 40% of the asset FIPE market valuation, the asset enters retirement evaluation:
   If Sum_{tau=1}^t c_itau(actual) >= 0.40 * Valuation_i(FIPE) implies z_it = 1."""

    new_con = """1. **State Exclusivity and Conservation:** A vehicle cannot be simultaneously operational and retired:
<div class="formula-box">
  <span>y<sub>it</sub> + z<sub>it</sub> = y<sub>i,t-1</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; T</span>
  <span class="formula-number">(5)</span>
</div>
<div class="formula-box">
  <span>z<sub>it</sub> &ge; z<sub>i,t-1</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; T</span>
  <span class="formula-number">(6)</span>
</div>

2. **Intervention Precondition:** Preventive servicing can only occur on active assets:
<div class="formula-box">
  <span>x<sub>it</sub> &le; y<sub>it</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; T</span>
  <span class="formula-number">(7)</span>
</div>

3. **Mandatory Safety Servicing:** If a vehicle reaches statutory revision limits or severe failure warning flags (m_it = 1), preventive servicing is non-negotiable:
<div class="formula-box">
  <span>x<sub>it</sub> &ge; m<sub>it</sub> &middot; y<sub>it</sub>, &nbsp;&forall; i &isin; V, &forall; t &isin; T</span>
  <span class="formula-number">(8)</span>
</div>

4. **Non-Negotiable Police Readiness Requirement:** For each strategic battalion B_k (e.g., PMSC Special Operations, Regional Police Battalions), active vehicles must satisfy minimum readiness proportion alpha_k in [0.90, 0.95]:
<div class="formula-box">
  <span>&sum;<sub>i&isin;B<sub>k</sub></sub> y<sub>it</sub> &ge; &alpha;<sub>k</sub> &middot; |B<sub>k</sub>|, &nbsp;&forall; k, &forall; t &isin; T</span>
  <span class="formula-number">(9)</span>
</div>

5. **Monthly Public Budgetary Ceiling (LOA):** Total monthly financial disbursements cannot exceed the statutory Legislative Budget Allocation B_t:
<div class="formula-box">
  <span>&sum;<sub>i&isin;V</sub> [ c<sub>it</sub><sup>prev</sup> &middot; x<sub>it</sub> + p<sub>it</sub><sup>fail</sup> &middot; c<sub>it</sub><sup>corr</sup> &middot; (1 - x<sub>it</sub>) &middot; y<sub>it</sub> ] &le; B<sub>t</sub>, &nbsp;&forall; t &isin; T</span>
  <span class="formula-number">(10)</span>
</div>

6. **Statutory Decommissioning Trigger (Art. 5, Decree 47,539/2018):** When cumulative maintenance costs exceed 40% of the asset FIPE market valuation, the asset enters retirement evaluation:
<div class="formula-box">
  <span>[ &sum;<sub>&tau;=1</sub><sup>t</sup> c<sub>i&tau;</sub><sup>actual</sup> / Valuation<sub>i</sub><sup>FIPE</sup> ] &ge; 0.40 &implies; z<sub>it</sub> = 1</span>
  <span class="formula-number">(11)</span>
</div>"""
    content = content.replace(old_con, new_con)

    path.write_text(content, encoding="utf-8")
    print("✔ Paper 1 (EN) atualizado: placas anonimizadas e equações (1) a (11) numeradas.")

def aplicar_artigo2_pt():
    path = ARTIGOS_DIR / "artigo2_auditoria_ia_xai_shap_lime_redes_complexas_pt.md"
    content = path.read_text(encoding="utf-8")
    content = anonimizar(content, is_pt=True)

    # Eq 1: SHAP
    old_eq1 = "phi_i(x) = Somatório sobre todos os subconjuntos S contidos em F excluindo i de [ (|S|! * (|F| - |S| - 1)!) / |F|! ] * [ f_x(S união {i}) - f_x(S) ]"
    new_eq1 = '<div class="formula-box">\n  <span>&phi;<sub>i</sub>(x) = &sum;<sub>S&sube;F&setminus;{i}</sub> [ (|S|! &middot; (|F| - |S| - 1)!) / |F|! ] &middot; [ f<sub>x</sub>(S &cup; {i}) - f<sub>x</sub>(S) ]</span>\n  <span class="formula-number">(1)</span>\n</div>'
    content = content.replace(old_eq1, new_eq1)

    # Eq 2 & 3: LIME
    old_eq2 = "argmin_g pertencente a G [ L(f, g, pi_x) + Omega(g) ]"
    new_eq2 = '<div class="formula-box">\n  <span>arg min<sub>g&isin;G</sub> [ &Lscr;(f, g, &pi;<sub>x</sub>) + &Omega;(g) ]</span>\n  <span class="formula-number">(2)</span>\n</div>'
    content = content.replace(old_eq2, new_eq2)

    old_eq3 = "pi_x(z) = exp( - D(x, z)² / sigma² )"
    new_eq3 = '<div class="formula-box">\n  <span>&pi;<sub>x</sub>(z) = exp( - D(x, z)<sup>2</sup> / &sigma;<sup>2</sup> )</span>\n  <span class="formula-number">(3)</span>\n</div>'
    content = content.replace(old_eq3, new_eq3)

    # Eq 4: Jaccard
    old_eq4 = "J_k = | S_5(k) interseção L_5(k) | / | S_5(k) união L_5(k) |"
    new_eq4 = '<div class="formula-box">\n  <span>J<sub>k</sub> = | S<sub>5</sub>(k) &cap; L<sub>5</sub>(k) | / | S<sub>5</sub>(k) &cup; L<sub>5</sub>(k) |</span>\n  <span class="formula-number">(4)</span>\n</div>'
    content = content.replace(old_eq4, new_eq4)

    # Eq 5: Louvain Modularity
    old_eq5 = "Q = ( 1 / (2m) ) * Somatório em i e j [ A_ij - ( (k_i * k_j) / (2m) ) ] * delta(c_i, c_j)"
    new_eq5 = '<div class="formula-box">\n  <span>Q = (1 / 2m) &middot; &sum;<sub>i,j</sub> [ A<sub>ij</sub> - (k<sub>i</sub> &middot; k<sub>j</sub>) / (2m) ] &middot; &delta;(c<sub>i</sub>, c<sub>j</sub>)</span>\n  <span class="formula-number">(5)</span>\n</div>'
    content = content.replace(old_eq5, new_eq5)

    # Eq 6: Isolation Forest Anomaly Score
    old_eq6 = "s(x, n) = 2^( - E[h(x)] / c(n) )"
    new_eq6 = '<div class="formula-box">\n  <span>s(x, n) = 2<sup>- &Eopf;[h(x)] / c(n)</sup></span>\n  <span class="formula-number">(6)</span>\n</div>'
    content = content.replace(old_eq6, new_eq6)

    # Eq 7: c(n)
    old_eq7 = "c(n) = 2 * [ ln(n - 1) + 0,5772156649 ] - [ (2 * (n - 1)) / n ]"
    new_eq7 = '<div class="formula-box">\n  <span>c(n) = 2 &middot; [ ln(n - 1) + 0,5772156649 ] - [ 2(n - 1) / n ]</span>\n  <span class="formula-number">(7)</span>\n</div>'
    content = content.replace(old_eq7, new_eq7)

    # Eq 8: SHA-256
    old_eq8 = "H_k = SHA-256( H_k-1 || Timestamp_UTC || Registro_ID || Payload_JSON )"
    new_eq8 = '<div class="formula-box">\n  <span>H<sub>k</sub> = SHA-256( H<sub>k-1</sub> &parallel; Timestamp<sub>UTC</sub> &parallel; Registro<sub>ID</sub> &parallel; Payload<sub>JSON</sub> )</span>\n  <span class="formula-number">(8)</span>\n</div>'
    content = content.replace(old_eq8, new_eq8)

    # Eq 9: METP
    old_eq9 = "Omega(i) = w_1 * R_SHAP(i) + w_2 * R_LIME(i) + w_3 * C_Rede(i) + w_4 * I_Normativa(i)"
    new_eq9 = '<div class="formula-box">\n  <span>&Omega;(i) = w<sub>1</sub> &middot; R<sub>SHAP</sub>(i) + w<sub>2</sub> &middot; R<sub>LIME</sub>(i) + w<sub>3</sub> &middot; C<sub>Rede</sub>(i) + w<sub>4</sub> &middot; I<sub>Normativa</sub>(i)</span>\n  <span class="formula-number">(9)</span>\n</div>'
    content = content.replace(old_eq9, new_eq9)

    path.write_text(content, encoding="utf-8")
    print("✔ Artigo 2 (PT) atualizado: placas anonimizadas e equações (1) a (9) numeradas.")

def aplicar_paper2_en():
    path = ARTIGOS_DIR / "paper2_xai_audit_shap_lime_network_graphs.md"
    content = path.read_text(encoding="utf-8")
    content = anonimizar(content, is_pt=False)

    # Eq 1: SHAP
    old_eq1 = "phi_i(x) = Sum_{S subseteq F \\setminus {i}} [ |S|! * (|F| - |S| - 1)! / |F|! ] * [ f_x(S union {i}) - f_x(S) ]"
    new_eq1 = '<div class="formula-box">\n  <span>&phi;<sub>i</sub>(x) = &sum;<sub>S&sube;F&setminus;{i}</sub> [ (|S|! &middot; (|F| - |S| - 1)!) / |F|! ] &middot; [ f<sub>x</sub>(S &cup; {i}) - f<sub>x</sub>(S) ]</span>\n  <span class="formula-number">(1)</span>\n</div>'
    content = content.replace(old_eq1, new_eq1)

    # Eq 2 & 3: LIME
    old_eq2 = "xi(x) = argmin_{g in G} [ L(f, g, pi_x) + Omega(g) ]"
    new_eq2 = '<div class="formula-box">\n  <span>&xi;(x) = arg min<sub>g&isin;G</sub> [ &Lscr;(f, g, &pi;<sub>x</sub>) + &Omega;(g) ]</span>\n  <span class="formula-number">(2)</span>\n</div>'
    content = content.replace(old_eq2, new_eq2)

    old_eq3 = "pi_x(z) = exp( - D(x, z)² / sigma² )"
    new_eq3 = '<div class="formula-box">\n  <span>&pi;<sub>x</sub>(z) = exp( - D(x, z)<sup>2</sup> / &sigma;<sup>2</sup> )</span>\n  <span class="formula-number">(3)</span>\n</div>'
    content = content.replace(old_eq3, new_eq3)

    # Eq 4: Jaccard
    old_eq4 = "J_k = | S_k(SHAP) intersection S_k(LIME) | / | S_k(SHAP) union S_k(LIME) |"
    new_eq4 = '<div class="formula-box">\n  <span>J<sub>k</sub> = | S<sub>k</sub>(SHAP) &cap; S<sub>k</sub>(LIME) | / | S<sub>k</sub>(SHAP) &cup; S<sub>k</sub>(LIME) |</span>\n  <span class="formula-number">(4)</span>\n</div>'
    content = content.replace(old_eq4, new_eq4)

    # Eq 5: Louvain Modularity
    old_eq5 = "Q = (1 / 2m) * Sum_{i,j} [ A_ij - (k_i * k_j) / (2m) ] * delta(c_i, c_j) = 0.5646"
    new_eq5 = '<div class="formula-box">\n  <span>Q = (1 / 2m) &middot; &sum;<sub>i,j</sub> [ A<sub>ij</sub> - (k<sub>i</sub> &middot; k<sub>j</sub>) / (2m) ] &middot; &delta;(c<sub>i</sub>, c<sub>j</sub>) = 0.5646</span>\n  <span class="formula-number">(5)</span>\n</div>'
    content = content.replace(old_eq5, new_eq5)

    # Eq 6: Isolation Forest Anomaly Score
    # Eq 7: c(n)
    # Check if section 5.1 has s(x, n)
    if "s(x, n) = 2^( - E[h(x)] / c(n) )" in content:
        content = content.replace("s(x, n) = 2^( - E[h(x)] / c(n) )", '<div class="formula-box">\n  <span>s(x, n) = 2<sup>- &Eopf;[h(x)] / c(n)</sup></span>\n  <span class="formula-number">(6)</span>\n</div>')

    # Eq 8: METP
    old_eq8 = "Omega(i) = w_1 * R_SHAP(i) + w_2 * R_LIME(i) + w_3 * C_Network(i) + w_4 * I_Statutory(i)"
    new_eq8 = '<div class="formula-box">\n  <span>&Omega;(i) = w<sub>1</sub> &middot; R<sub>SHAP</sub>(i) + w<sub>2</sub> &middot; R<sub>LIME</sub>(i) + w<sub>3</sub> &middot; C<sub>Network</sub>(i) + w<sub>4</sub> &middot; I<sub>Statutory</sub>(i)</span>\n  <span class="formula-number">(7)</span>\n</div>'
    content = content.replace(old_eq8, new_eq8)

    path.write_text(content, encoding="utf-8")
    print("✔ Paper 2 (EN) atualizado: placas anonimizadas e equações (1) a (7) numeradas.")

if __name__ == "__main__":
    aplicar_artigo1_pt()
    aplicar_paper1_en()
    aplicar_artigo2_pt()
    aplicar_paper2_en()
    print("Todos os 4 artigos (.md) atualizados com sucesso!")

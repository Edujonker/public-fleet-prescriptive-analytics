#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import re

ARTIGOS_DIR = Path("artigos_internacionais")

def ajustar_artigo2_pt():
    p = ARTIGOS_DIR / "03_artigo2_auditoria_xai_redes_complexas_pt" / "artigo2_auditoria_ia_xai_shap_lime_redes_complexas_pt.md"
    text = p.read_text(encoding="utf-8")
    
    bloco = """
A governança de inteligência artificial explicável no setor público apoia-se nas taxonomias e princípios de IA responsável desenvolvidos por Barredo Arrieta et al. (2020) e Guidotti et al. (2018). Conforme alertam Rudin (2019) e Molnar (2022), a dependência acrítica de modelos caixa-preta em decisões de alto impacto social e jurídico impõe sérios riscos éticos, sendo imperativo compreender as premissas e limitações dos métodos explicativos pós-hoc. Paralelamente, Mittelstadt, Russell & Wachter (2019) discutem as armadilhas conceituais das explicações locais perante órgãos de fiscalização. No campo da ciência de redes, os algoritmos de detecção de comunidades de Blondel et al. (2008) e a análise topológica de modularidade revisada por Fortunato (2010) viabilizam a segregação de clusters relacionais em larga escala. Por fim, para a validação inferencial da capacidade discriminativa das curvas ROC correlacionadas, emprega-se o teste não paramétrico de DeLong, DeLong & Clarke-Pearson (1988).
"""
    if "Barredo Arrieta et al. (2020)" not in text:
        target = "## 2. Fundamentos Matemáticos e Epistemológicos da Divergência entre SHAP e LIME"
        text = text.replace(target, target + "\n" + bloco)
        p.write_text(text, encoding="utf-8")
        print("[OK] Artigo 2 PT citações integradas!")

def ajustar_paper2_en():
    p = ARTIGOS_DIR / "04_paper2_xai_audit_network_graphs_en" / "paper2_xai_audit_shap_lime_network_graphs.md"
    text = p.read_text(encoding="utf-8")
    
    bloco = """
The governance of explainable artificial intelligence in public administration is framed by the taxonomies of trustworthy and responsible AI synthesized by Barredo Arrieta et al. (2020) and Guidotti et al. (2018). As forcefully argued by Rudin (2019) and Molnar (2022), relying on opaque black-box systems in high-stakes public decisions introduces severe legal vulnerabilities, mandating rigorous evaluation of explanatory fidelity. Concurrently, Mittelstadt, Russell & Wachter (2019) elucidate the conceptual and epistemic limitations of post-hoc approximations. In complex network science, community detection algorithms developed by Blondel et al. (2008) and modularity principles reviewed by Fortunato (2010) enable structural segmentation of bipartite contractual affiliations. For statistical comparison between correlated receiver operating characteristic curves, the non-parametric methodology of DeLong, DeLong & Clarke-Pearson (1988) provides asymptotic inferential grounding.
"""
    if "Barredo Arrieta et al. (2020)" not in text:
        target = "## 2. Mathematical and Epistemic Foundations of Explanatory Divergence between SHAP and LIME"
        text = text.replace(target, target + "\n" + bloco)
        p.write_text(text, encoding="utf-8")
        print("[OK] Paper 2 EN citações integradas!")

def ajustar_artigo3_pt():
    p = ARTIGOS_DIR / "05_artigo3_regressoes_lineares_comparativo_pt" / "artigo3_regressoes_lineares_frotas_comparativo_pt.md"
    text = p.read_text(encoding="utf-8")
    
    # Adicionar MacKay na seção de Bayesian Ridge e McCullagh na de GLM Gamma
    if "MacKay (1992)" not in text:
        text = text.replace(
            "**8. Bayesian Ridge Regression (Inferência Probabilística):**",
            "**8. Bayesian Ridge Regression (Inferência Probabilística sob MacKay, 1992):**\nConforme estabelecido no arcabouço de interpolação bayesiana de MacKay (1992), o modelo assume priores gaussianas conjugadas para coeficientes e precisão do ruído:"
        )
    if "McCullagh & Nelder (1989)" not in text:
        text = text.replace(
            "**10. Modelos Lineares Generalizados (GLM Gamma com Ligação Log):**",
            "**10. Modelos Lineares Generalizados (GLM Gamma sob McCullagh & Nelder, 1989):**\nSegundo a formulação canônica de Modelos Lineares Generalizados de McCullagh & Nelder (1989), a variável de resposta obedece à distribuição Gamma com função de ligação logarítmica:"
        )
    p.write_text(text, encoding="utf-8")
    print("[OK] Artigo 3 PT MacKay e McCullagh integrados!")

def ajustar_consad():
    p = ARTIGOS_DIR / "06_artigo_consad_gestao_publica_iot_prescritiva" / "artigo_consad_gestao_publica_prescritiva_iot_dados.md"
    text = p.read_text(encoding="utf-8")
    
    if "Brasil (2000)" not in text:
        text = text.replace(
            "Lei de Responsabilidade Fiscal (LC nº 101/2000)",
            "Lei de Responsabilidade Fiscal (Brasil, 2000; LC nº 101/2000)"
        )
    if "Brasil (2018)" not in text:
        text = text.replace(
            "Lei Geral de Proteção de Dados (Lei nº 13.709/2018)",
            "Lei Geral de Proteção de Dados (Brasil, 2018; Lei nº 13.709/2018)"
        )
    if "Brasil (2021)" not in text:
        text = text.replace(
            "Nova Lei de Licitações (Lei Federal nº 14.133/2021)",
            "Nova Lei de Licitações (Brasil, 2021; Lei Federal nº 14.133/2021)"
        )
    p.write_text(text, encoding="utf-8")
    print("[OK] CONSAD citações de Brasil integradas!")

if __name__ == "__main__":
    ajustar_artigo2_pt()
    ajustar_paper2_en()
    ajustar_artigo3_pt()
    ajustar_consad()

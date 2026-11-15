#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do MEP — Mapa de Estrutura da Pesquisa
Dissertação de Mestrado PPGCAP/UDESC — Eduardo Lopes Jonker
Data: 19/10/2026
Conteúdo extraído dos documentos reais do projeto:
  - docs/anteprojeto_text.txt
  - relatorios/MAPA_MENTAL_PROJETO.md
  - relatorios/relatorio_metodologico_estatistico.md
  - README.md (resultados empíricos)
"""

from pathlib import Path
import weasyprint

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "mep.pdf"

HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<style>
@page {
  size: A4;
  margin: 18mm 18mm 20mm 20mm;
  @bottom-center {
    content: counter(page) " / " counter(pages);
    font-size: 8pt; color: #888;
    font-family: Arial, sans-serif;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 10.5pt; line-height: 1.55; color: #1a1a1a; background: #fff;
}

/* CAPA */
.cover {
  min-height: 260mm;
  display: flex; flex-direction: column;
  align-items: center; justify-content: space-between;
  text-align: center; padding: 12mm 10mm 10mm 10mm;
  page-break-after: always;
}
.cover .inst {
  font-family: Arial, sans-serif; font-size: 9pt; color: #333;
  text-transform: uppercase; letter-spacing: 0.08em;
  line-height: 1.8; border-bottom: 1px solid #c5cfdf;
  padding-bottom: 6mm; width: 100%;
}
.cover .inst strong { color: #1b3a6e; font-size: 10pt; }
.cover .label {
  font-family: Arial, sans-serif; font-size: 9pt; color: #1b3a6e;
  font-weight: bold; text-transform: uppercase; letter-spacing: 0.15em;
  border: 2px solid #1b3a6e; padding: 2mm 8mm;
  display: inline-block; margin-bottom: 6mm; margin-top: 4mm;
}
.cover .title-block {
  background: #1b3a6e; width: 100%;
  padding: 10mm 8mm; margin: 4mm 0;
}
.cover h1 {
  font-size: 18pt; font-weight: bold; color: #ffffff;
  line-height: 1.35; margin: 0;
}
.cover .subtitle {
  font-size: 10pt; color: #adc4e8; margin-top: 4mm;
  font-style: italic; letter-spacing: 0.03em;
}
.cover .ident-block {
  width: 100%; border: 1.5px solid #c5cfdf;
  padding: 5mm 8mm; text-align: left;
  font-family: Arial, sans-serif; font-size: 10pt;
  line-height: 2.1; background: #f7f8fc;
}
.cover .ident-block .row { display: flex; gap: 4mm; }
.cover .ident-block .lbl {
  color: #1b3a6e; font-weight: bold; min-width: 32mm;
}
.cover .ident-block .val { color: #1a1a1a; }
.cover .date-box {
  margin-top: 4mm; font-family: Arial, sans-serif; font-size: 9pt;
  background: #1b3a6e; color: #fff;
  display: inline-block; padding: 2mm 10mm; border-radius: 3px;
  letter-spacing: 0.05em;
}

/* HEADINGS */
h2 {
  font-family: Arial, sans-serif; font-size: 12.5pt; color: #1b3a6e;
  font-weight: bold; margin-top: 8mm; margin-bottom: 3mm;
  padding-bottom: 1.5mm; border-bottom: 2px solid #1b3a6e;
  page-break-after: avoid;
}
h3 {
  font-family: Arial, sans-serif; font-size: 10.5pt; color: #2d5086;
  font-weight: bold; margin-top: 5mm; margin-bottom: 2mm;
  page-break-after: avoid;
}

/* PARAGRAFO */
p { margin-bottom: 2.5mm; text-align: justify; text-indent: 7mm; }
p.noindent { text-indent: 0; }

/* RESUMO */
.abstract-box {
  border: 1px solid #c5cfdf; background: #f7f8fc;
  padding: 4mm 6mm; margin: 4mm 0 5mm 0; page-break-inside: avoid;
}
.abstract-box p { text-indent: 0; margin-bottom: 2mm; }
.abstract-label {
  font-family: Arial, sans-serif; font-size: 9.5pt; font-weight: bold;
  color: #1b3a6e; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2mm;
}
.keywords { font-family: Arial, sans-serif; font-size: 9pt; color: #333; margin-top: 2mm; }
.keywords strong { color: #1b3a6e; }

/* TABELAS */
table {
  width: 100%; border-collapse: collapse; font-size: 9pt;
  margin: 3mm 0 4mm 0; page-break-inside: avoid;
}
th {
  background: #1b3a6e; color: #fff; font-family: Arial, sans-serif;
  font-weight: bold; padding: 2mm 3mm; text-align: center; font-size: 8.5pt;
}
td { padding: 1.5mm 3mm; border-bottom: 1px solid #dde3ef; vertical-align: top; }
tr:nth-child(even) td { background: #f4f6fb; }
td.num { text-align: center; font-family: Arial, sans-serif; }
td.hl  { font-weight: bold; color: #1b3a6e; }

/* CAPITULOS */
.chapter { page-break-before: always; padding-top: 4mm; }
.chapter:first-of-type { page-break-before: avoid; }

/* BOXES */
.box-info {
  border-left: 4px solid #1b3a6e; background: #f4f6fb;
  padding: 3mm 5mm; margin: 3mm 0; font-size: 9.5pt; page-break-inside: avoid;
}
.box-result {
  border-left: 4px solid #2a7a3a; background: #f4fbf5;
  padding: 3mm 5mm; margin: 3mm 0; font-size: 9.5pt; page-break-inside: avoid;
}
.box-method {
  border-left: 4px solid #c47800; background: #fdf8f0;
  padding: 3mm 5mm; margin: 3mm 0; font-size: 9.5pt; page-break-inside: avoid;
}

ul, ol { margin-left: 7mm; margin-bottom: 2mm; }
li { margin-bottom: 1mm; }

.timing {
  font-family: Arial, sans-serif; font-size: 8.5pt; color: #888;
  text-align: right; font-style: italic; margin-bottom: 2mm;
}
.ref-note { font-size: 8pt; color: #666; font-style: italic; text-indent: 0; }
.section-footer {
  margin-top: 4mm; padding-top: 2mm; border-top: 1px dashed #c5cfdf;
  font-family: Arial, sans-serif; font-size: 8.5pt; color: #888;
}
</style>
</head>
<body>

<!-- CAPA -->
<div class="cover">

  <!-- Instituição -->
  <div class="inst">
    <strong>Universidade do Estado de Santa Catarina &mdash; UDESC</strong><br/>
    Centro de Ci&ecirc;ncias Tecnol&oacute;gicas &mdash; CCT<br/>
    Programa de P&oacute;s-Gradua&ccedil;&atilde;o em Computa&ccedil;&atilde;o Aplicada &mdash; PPGCAP<br/>
    Linha de Pesquisa: Metodologia e T&eacute;cnicas de Computa&ccedil;&atilde;o (MTC)
  </div>

  <!-- Rótulo MEP -->
  <div class="label">MEP &mdash; Mapa de Estrutura da Pesquisa</div>

  <!-- Título em destaque -->
  <div class="title-block">
    <h1>Anal&iacute;tica Prescritiva e Intelig&ecirc;ncia Artificial<br/>
        Explic&aacute;vel para a Gest&atilde;o de Frota Veicular<br/>
        no Setor P&uacute;blico</h1>
    <div class="subtitle">
      Estudo comparativo com dados de manuten&ccedil;&atilde;o, patrim&ocirc;nio<br/>
      e abastecimento da frota estadual de Santa Catarina
    </div>
  </div>

  <!-- Identificação -->
  <div class="ident-block">
    <div class="row"><span class="lbl">Mestrando:</span>     <span class="val">Eduardo Lopes Jonker</span></div>
    <div class="row"><span class="lbl">Orientadora:</span>   <span class="val">Profa. Dra. Vivian Kremer Kalempa</span></div>
    <div class="row"><span class="lbl">Coorientador:</span>  <span class="val">Prof. Dr. Yuri Kaszubowski Lopes</span></div>
    <div class="row"><span class="lbl">Programa:</span>      <span class="val">Mestrado Acad&ecirc;mico em Computa&ccedil;&atilde;o Aplicada &mdash; PPGCAP / CCT / UDESC</span></div>
    <div class="row"><span class="lbl">Local:</span>         <span class="val">Florian&oacute;polis &mdash; SC, Brasil</span></div>
  </div>

  <div class="date-box">19 de outubro de 2026</div>
</div>


<!-- RESUMO -->
<div class="chapter">
<h2>Resumo</h2>
<div class="abstract-box">
  <div class="abstract-label">Resumo</div>
  <p class="noindent">
    A gest&atilde;o de frotas p&uacute;blicas re&uacute;ne informa&ccedil;&otilde;es dispersas em cadastros patrimoniais,
    registros de manuten&ccedil;&atilde;o e comprovantes de abastecimento. A fragmenta&ccedil;&atilde;o dificulta
    estimar risco de falha, custo operacional e prioridade de interven&ccedil;&atilde;o, e limita a convers&atilde;o
    de previs&otilde;es em decis&otilde;es justific&aacute;veis. Este trabalho prop&otilde;e e avalia uma arquitetura de
    anal&iacute;tica prescritiva, com intelig&ecirc;ncia artificial explic&aacute;vel, para apoiar a programa&ccedil;&atilde;o
    de manuten&ccedil;&atilde;o preventiva e o planejamento de custos de uma frota institucional.
    Foram integradas extra&ccedil;&otilde;es administrativas de patrim&ocirc;nio, manuten&ccedil;&atilde;o e abastecimento
    do Estado de Santa Catarina &mdash; 350.737 registros de ordens de servi&ccedil;o (outubro/2020 a
    agosto/2026), 7.580 ve&iacute;culos &uacute;nicos e R$ 138.759.653,82 em gastos auditados.
    M&uacute;ltiplos m&eacute;todos n&atilde;o lineares foram comparados com valida&ccedil;&atilde;o temporal Rolling-Origin.
    O modelo campe&atilde;o (HistGradientBoosting) atingiu PR-AUC = 0,9099 e MAE = R$ 2.311,82.
    A pol&iacute;tica prescritiva gerou economia contrafactual de at&eacute; 6,31% no per&iacute;odo de teste e
    R$ 9.302.147,26 (17,51%) no cen&aacute;rio de or&ccedil;amento expandido.
  </p>
  <div class="keywords">
    <strong>Palavras-chave:</strong>
    anal&iacute;tica prescritiva; gest&atilde;o de frotas; manuten&ccedil;&atilde;o preditiva; intelig&ecirc;ncia artificial explic&aacute;vel; otimiza&ccedil;&atilde;o
  </div>
</div>
</div>


<!-- ESTRUTURA GERAL -->
<div class="chapter">
<h2>Estrutura da Apresenta&ccedil;&atilde;o (20 min)</h2>
<table>
  <thead>
    <tr>
      <th style="width:6%">#</th>
      <th style="width:33%">Cap&iacute;tulo</th>
      <th style="width:11%">Tempo</th>
      <th style="width:50%">Conte&uacute;do central</th>
    </tr>
  </thead>
  <tbody>
    <tr><td class="num hl">1</td><td>Introdu&ccedil;&atilde;o</td><td class="num">&asymp; 2 min</td><td>Contexto, problema de pesquisa e hip&oacute;teses de trabalho</td></tr>
    <tr><td class="num hl">2</td><td>Conceitos Fundamentais</td><td class="num">&asymp; 2 min</td><td>Literatura de base: ML, prescritiva, XAI, MILP (passado)</td></tr>
    <tr><td class="num hl">3</td><td>Revis&atilde;o da Literatura</td><td class="num">&asymp; 3 min</td><td>Estado da arte: manuten&ccedil;&atilde;o preditiva, grafos, s&eacute;ries temporais</td></tr>
    <tr><td class="num hl">4</td><td>Proposta</td><td class="num">&asymp; 4 min</td><td>Arquitetura metodol&oacute;gica, pipeline de dados e formula&ccedil;&atilde;o MILP</td></tr>
    <tr><td class="num hl">5</td><td>Valida&ccedil;&atilde;o</td><td class="num">&asymp; 5 min</td><td>Resultados emp&iacute;ricos: ML, anomalias, grafos, MILP, XAI, estat&iacute;sticas</td></tr>
    <tr><td class="num hl">6</td><td>Discuss&otilde;es</td><td class="num">&asymp; 2 min</td><td>An&aacute;lise das hip&oacute;teses, limita&ccedil;&otilde;es, compara&ccedil;&atilde;o com literatura</td></tr>
    <tr><td class="num hl">7</td><td>Conclus&atilde;o</td><td class="num">&asymp; 2 min</td><td>Contribui&ccedil;&otilde;es, trabalhos futuros e considera&ccedil;&otilde;es finais</td></tr>
  </tbody>
</table>
</div>


<!-- CAP 1 — INTRODUCAO -->
<div class="chapter">
<div class="timing">Bloco 1 &mdash; &asymp; 2 minutos</div>
<h2>Cap. 1 &mdash; Introdu&ccedil;&atilde;o</h2>

<h3>1.1 Contexto</h3>
<p>A gest&atilde;o de uma frota institucional exige conciliar disponibilidade dos ve&iacute;culos, seguran&ccedil;a,
manuten&ccedil;&atilde;o, consumo de combust&iacute;vel e limites or&ccedil;ament&aacute;rios. Essas dimens&otilde;es deixam
vest&iacute;gios em sistemas distintos: o cadastro patrimonial identifica caracter&iacute;sticas e situa&ccedil;&atilde;o
do bem; as ordens de servi&ccedil;o registram interven&ccedil;&otilde;es, falhas e custos; e os abastecimentos
informam volume, valor e hod&ocirc;metro. Sem integra&ccedil;&atilde;o temporal e sem uma chave confi&aacute;vel
de ve&iacute;culo, a administra&ccedil;&atilde;o tende a analisar os dados em relat&oacute;rios isolados, dificultando
detectar padr&otilde;es de desgaste ou comparar o custo de opera&ccedil;&atilde;o entre unidades e per&iacute;odos.
<span class="ref-note">(Anteprojeto, Se&ccedil;&atilde;o 1)</span></p>

<p>Este trabalho utiliza dados reais do Estado de Santa Catarina:
<strong>350.737 registros de ordens de servi&ccedil;o</strong> (outubro/2020 a agosto/2026),
<strong>7.580 ve&iacute;culos &uacute;nicos</strong> e <strong>R$ 138.759.653,82</strong> em gastos auditados,
cobrindo 71 meses de opera&ccedil;&atilde;o cont&iacute;nua da frota estadual.</p>

<h3>1.2 Problema de Pesquisa</h3>
<div class="box-info">
  <p class="noindent">Como integrar dados de patrim&ocirc;nio, manuten&ccedil;&atilde;o e abastecimento para comparar
  modelos n&atilde;o lineares de previs&atilde;o e m&eacute;todos de explicabilidade e, a partir deles, gerar e
  avaliar recomenda&ccedil;&otilde;es de manuten&ccedil;&atilde;o para uma frota p&uacute;blica sob restri&ccedil;&otilde;es de custo,
  capacidade de oficina e seguran&ccedil;a?
  <span class="ref-note">(Anteprojeto, Se&ccedil;&atilde;o 1.1)</span></p>
</div>

<h3>1.3 Hip&oacute;teses de Trabalho</h3>
<ul>
  <li><strong>H1 &mdash;</strong> A integra&ccedil;&atilde;o de atributos patrimoniais, hist&oacute;ricos de manuten&ccedil;&atilde;o e medidas
    de abastecimento melhora pelo menos uma m&eacute;trica principal de previs&atilde;o fora do tempo de
    treinamento em rela&ccedil;&atilde;o a modelos treinados apenas com manuten&ccedil;&atilde;o.</li>
  <li><strong>H2 &mdash;</strong> Ensembles de &aacute;rvores (Random Forest, Extra Trees, Gradient Boosting) apresentam
    desempenho competitivo frente a SVR-RBF em dados tabulares da frota.</li>
  <li><strong>H3 &mdash;</strong> Sob o mesmo or&ccedil;amento e n&iacute;vel de risco admiss&iacute;vel, a pol&iacute;tica de otimiza&ccedil;&atilde;o
    reduz o custo total esperado no experimento retrospectivo em rela&ccedil;&atilde;o &agrave; pr&aacute;tica hist&oacute;rica
    e a regras heur&iacute;sticas.</li>
  <li><strong>H4 &mdash;</strong> As explica&ccedil;&otilde;es SHAP e LIME representam fatores locais e globais com fidelidade
    e estabilidade suficientes para revis&atilde;o por especialistas.</li>
</ul>

<h3>1.4 Objetivo Geral</h3>
<p>Desenvolver e avaliar uma arquitetura computacional de anal&iacute;tica prescritiva e IA explic&aacute;vel
para apoiar a gest&atilde;o de frota veicular p&uacute;blica, integrando dados de patrim&ocirc;nio, manuten&ccedil;&atilde;o
e abastecimento e comparando m&uacute;ltiplos algoritmos n&atilde;o lineares quanto &agrave; previs&atilde;o,
explicabilidade e qualidade das decis&otilde;es recomendadas.
<span class="ref-note">(Anteprojeto, Se&ccedil;&atilde;o 3.1)</span></p>
</div>


<!-- CAP 2 — CONCEITOS FUNDAMENTAIS -->
<div class="chapter">
<div class="timing">Bloco 2 &mdash; &asymp; 2 minutos &nbsp;&middot;&nbsp; Literatura (passado)</div>
<h2>Cap. 2 &mdash; Conceitos Fundamentais</h2>

<div class="box-method">
  <p class="noindent"><em>Nota de apresenta&ccedil;&atilde;o:</em> Cap&iacute;tulo dedicado &agrave; literatura consolidada que
  sustenta as escolhas metodol&oacute;gicas. Exposi&ccedil;&atilde;o objetiva; evitar longas cita&ccedil;&otilde;es.</p>
</div>

<h3>2.1 Aprendizado de M&aacute;quina para Dados Tabulares</h3>
<p>Modelos baseados em &aacute;rvores particionam o espa&ccedil;o de atributos e capturam intera&ccedil;&otilde;es e
n&atilde;o-linearidades sem exigir forma funcional linear. <em>Random Forest</em> agrega &aacute;rvores treinadas
com amostras e subconjuntos aleat&oacute;rios de atributos (Breiman, 2001); <em>Extra Trees</em> amplia a
aleatoriza&ccedil;&atilde;o dos cortes (Geurts; Ernst; Wehenkel, 2006); <em>Gradient Boosting</em> ajusta
sequencialmente &aacute;rvores para reduzir o erro (Friedman, 2001); <em>HistGradientBoosting</em> &eacute; uma
implementa&ccedil;&atilde;o eficiente com binning de histogramas. SVM com kernel RBF oferece
compara&ccedil;&atilde;o baseada em margens e fun&ccedil;&otilde;es de similaridade n&atilde;o lineares (Cortes; Vapnik, 1995).</p>

<h3>2.2 Anal&iacute;tica Prescritiva e Otimiza&ccedil;&atilde;o</h3>
<p>Na formula&ccedil;&atilde;o prescritiva, o modelo de aprendizado fornece probabilidades e custos que
alimentam uma decis&atilde;o sujeita a recursos limitados. Bertsimas e Kallus (2020) formalizam
essa passagem como otimiza&ccedil;&atilde;o estoc&aacute;stica condicionada a informa&ccedil;&otilde;es preditivas.
<span class="ref-note">(Anteprojeto, Se&ccedil;&atilde;o 4.3)</span></p>

<h3>2.3 Intelig&ecirc;ncia Artificial Explic&aacute;vel (XAI)</h3>
<p>SHAP distribui a contribui&ccedil;&atilde;o das vari&aacute;veis para cada predi&ccedil;&atilde;o dentro de uma estrutura
aditiva: <em>f(x) = E[f(X)] + &sum;<sub>j</sub> &phi;<sub>j</sub></em>
(Lundberg; Lee, 2017). LIME aproxima localmente o comportamento do modelo por um
explicador simples (Ribeiro; Singh; Guestrin, 2016). A import&acirc;ncia por permuta&ccedil;&atilde;o oferece
uma refer&ecirc;ncia <em>model-agnostic</em> global.</p>

<h3>2.4 Formula&ccedil;&atilde;o MILP &mdash; Base Matem&aacute;tica</h3>
<div class="box-info">
  <p class="noindent"><strong>Minimizar:</strong>
  &sum;<sub>i</sub>&sum;<sub>t</sub> [ c<sup>M</sup><sub>it</sub> x<sub>it</sub> +
  ((1&minus;x<sub>it</sub>)p<sup>0</sup><sub>it</sub> + x<sub>it</sub>p<sup>1</sup><sub>it</sub>)
  (c<sup>F</sup><sub>it</sub> + c<sup>D</sup><sub>it</sub>) ]</p>
  <p class="noindent"><strong>Sujeito a:</strong>
  &sum;<sub>i</sub> c<sup>M</sup><sub>it</sub> x<sub>it</sub> &le; B<sub>t</sub> (or&ccedil;amento);
  &sum;<sub>i</sub> h<sub>it</sub> x<sub>it</sub> &le; H<sub>t</sub> (capacidade de oficina);
  x<sub>it</sub> &le; e<sub>it</sub> (elegibilidade); x<sub>it</sub> &isin; {0,1}
  <span class="ref-note">(Anteprojeto, Se&ccedil;&atilde;o 5.4)</span></p>
</div>

<h3>2.5 Valida&ccedil;&atilde;o Temporal Rolling-Origin</h3>
<p>Em dados longitudinais de frota, embaralhamento aleat&oacute;rio pode inflar o desempenho por
permitir que informa&ccedil;&atilde;o temporalmente pr&oacute;xima apare&ccedil;a nos conjuntos de treino e teste.
A valida&ccedil;&atilde;o Rolling-Origin mant&eacute;m per&iacute;odos mais antigos para treino e o bloco mais
recente retido para teste final, respeitando a causalidade temporal.
<span class="ref-note">(Anteprojeto, Se&ccedil;&atilde;o 5.5)</span></p>
</div>


<!-- CAP 3 — REVISAO DA LITERATURA -->
<div class="chapter">
<div class="timing">Bloco 3 &mdash; &asymp; 3 minutos</div>
<h2>Cap. 3 &mdash; Revis&atilde;o da Literatura</h2>

<h3>3.1 Manuten&ccedil;&atilde;o Preditiva em Ve&iacute;culos</h3>
<p>A literatura de manuten&ccedil;&atilde;o preditiva veicular re&uacute;ne m&eacute;todos de aprendizado de m&aacute;quina,
dados de sensores e hist&oacute;ricos de oficina, mas destaca desafios de qualidade, integra&ccedil;&atilde;o e
explicabilidade. Uma revis&atilde;o sistem&aacute;tica recente examina 94 estudos e aponta que a
disponibilidade de dados e a ado&ccedil;&atilde;o de XAI permanecem quest&otilde;es relevantes
(Mahale; Kolhar; More, 2025). Em estudo emp&iacute;rico com caminh&otilde;es, modelos de floresta
aleat&oacute;ria, XGBoost, redes neurais e combina&ccedil;&atilde;o de modelos foram comparados para estimar
custos por dist&acirc;ncia, ilustrando tanto a viabilidade de modelos n&atilde;o lineares quanto a
relev&acirc;ncia de dados reais e valida&ccedil;&atilde;o em ve&iacute;culos n&atilde;o vistos (Katreddi et al., 2023).
<span class="ref-note">(Anteprojeto, Se&ccedil;&atilde;o 1)</span></p>

<h3>3.2 Gest&atilde;o de Frotas P&uacute;blicas e Dados Administrativos</h3>
<p>Estudos no contexto de administra&ccedil;&atilde;o p&uacute;blica evidenciam a dispers&atilde;o dos registros em
sistemas distintos. A integra&ccedil;&atilde;o exige padroniza&ccedil;&atilde;o de identificadores, deduplicamento,
verifica&ccedil;&atilde;o de hod&ocirc;metros mon&oacute;tonos e concilia&ccedil;&atilde;o de c&oacute;digos. No caso deste estudo, a
discrepância semântica entre os campos <em>tipo_manutencao_oficina</em> (com vi&eacute;s de sistema)
e <em>TRIM(ds_codigo_manutencao)</em> (que recupera o sinal real) representa um achado
emp&iacute;rico inédito sobre a base estadual.</p>

<h3>3.3 Redes Complexas e An&aacute;lise de Fornecedores</h3>
<p>Grafos bipartidos ve&iacute;culo-oficina permitem identificar concentra&ccedil;&atilde;o de fornecedores e
vulnerabilidades estruturais. Betweenness centrality, PageRank e closeness centrality
ranqueiam fornecedores por influ&ecirc;ncia na rede. O algoritmo de Louvain detecta comunidades
de alta modularidade sem defini&ccedil;&atilde;o pr&eacute;via do n&uacute;mero de grupos.</p>

<h3>3.4 Lacunas Identificadas</h3>
<div class="box-info">
  <ul>
    <li>Poucos estudos integram simultaneamente as tr&ecirc;s fontes (patrim&ocirc;nio, manuten&ccedil;&atilde;o e
    abastecimento) com chave de ve&iacute;culo auditada e valida&ccedil;&atilde;o temporal estrita.</li>
    <li>A XAI raramente &eacute; avaliada por m&eacute;tricas de fidelidade e estabilidade em contexto de
    frota p&uacute;blica.</li>
    <li>A passagem de previs&atilde;o preditiva para prescri&ccedil;&atilde;o com restri&ccedil;&otilde;es or&ccedil;ament&aacute;rias expl&iacute;citas
    &eacute; pouco documentada no contexto de frotas institucionais brasileiras.</li>
  </ul>
</div>
</div>


<!-- CAP 4 — PROPOSTA -->
<div class="chapter">
<div class="timing">Bloco 4 &mdash; &asymp; 4 minutos</div>
<h2>Cap. 4 &mdash; Proposta</h2>

<h3>4.1 Delineamento Metodol&oacute;gico</h3>
<p>Pesquisa aplicada, quantitativa, com estudo de caso instrumental e desenvolvimento e
avalia&ccedil;&atilde;o de artefato computacional. Fluxo de trabalho compat&iacute;vel com CRISP-DM.
Unidade de an&aacute;lise: <strong>ve&iacute;culo-m&ecirc;s</strong> &mdash; <strong>51.244 inst&acirc;ncias</strong>.
Parti&ccedil;&atilde;o de teste retido: per&iacute;odo 2025&ndash;2026.
<span class="ref-note">(Anteprojeto, Se&ccedil;&atilde;o 5.1; README)</span></p>

<h3>4.2 Pipeline de Dados (9 Etapas Sequenciais)</h3>
<div class="box-method">
  <p class="noindent">Cada etapa &eacute; implementada em um script numerado, autossuficiente e idempotente,
  produzindo artefatos rastreáveis (Parquet, CSV, SQLite, figuras PNG 300 DPI).</p>
</div>
<table>
  <thead>
    <tr>
      <th style="width:8%">Script</th>
      <th style="width:35%">Etapa</th>
      <th style="width:57%">Procedimento</th>
    </tr>
  </thead>
  <tbody>
    <tr><td class="num hl">01</td><td>Auditoria Forense</td><td>Verifica&ccedil;&atilde;o SHA-256; diagn&oacute;stico de 6.841 regress&otilde;es de hod&ocirc;metro; relat&oacute;rio forense</td></tr>
    <tr><td class="num hl">02</td><td>Pr&eacute;-processamento</td><td>Saneamento de nulos e outliers; resolu&ccedil;&atilde;o da discrepância sem&acirc;ntica de tipos de OS; feature engineering</td></tr>
    <tr><td class="num hl">03</td><td>An&aacute;lise Descritiva</td><td>Estat&iacute;stica descritiva; Shapiro-Wilk / Lilliefors; fundamenta&ccedil;&atilde;o para modelos n&atilde;o lineares</td></tr>
    <tr><td class="num hl">04</td><td>Modelos Preditivos</td><td>Valida&ccedil;&atilde;o Rolling-Origin; classifica&ccedil;&atilde;o de risco e regress&atilde;o de custo; estudo de abla&ccedil;&atilde;o M vs M+P</td></tr>
    <tr><td class="num hl">05</td><td>Detec&ccedil;&atilde;o de Anomalias</td><td>Isolation Forest com 3 sementes; &Iacute;ndice de Jaccard por contamina&ccedil;&atilde;o; concord&acirc;ncia com reprova&ccedil;&otilde;es reais</td></tr>
    <tr><td class="num hl">06</td><td>Teoria dos Grafos</td><td>Rede bipartida ve&iacute;culos &harr; oficinas; Louvain; betweenness, PageRank</td></tr>
    <tr><td class="num hl">07</td><td>Explicabilidade XAI</td><td>SHAP TreeExplainer; LIME; import&acirc;ncia por permuta&ccedil;&atilde;o; fidelidade e estabilidade</td></tr>
    <tr><td class="num hl">08</td><td>Otimiza&ccedil;&atilde;o MILP</td><td>PuLP + Solver HiGHS (Dual Simplex + B&amp;B); 5 cen&aacute;rios or&ccedil;ament&aacute;rios (50%&ndash;150%); pre&ccedil;os-sombra</td></tr>
    <tr><td class="num hl">09</td><td>Valida&ccedil;&atilde;o Estat&iacute;stica</td><td>Wilcoxon pareado por pares de modelos; corre&ccedil;&atilde;o de Holm-Bonferroni; teste DeLong</td></tr>
  </tbody>
</table>

<h3>4.3 Auditoria de Dados &mdash; Achados Principais</h3>
<table>
  <thead>
    <tr><th>Dimens&atilde;o Auditada</th><th>Valor Observado</th><th>Implica&ccedil;&atilde;o Metodol&oacute;gica</th></tr>
  </thead>
  <tbody>
    <tr><td>Total de Registros de OS</td><td class="num hl">350.737</td><td>Cobertura longitudinal de 71 meses</td></tr>
    <tr><td>Ve&iacute;culos &Uacute;nicos</td><td class="num hl">7.580 placas</td><td>Painel ve&iacute;culo-m&ecirc;s: 51.244 inst&acirc;ncias</td></tr>
    <tr><td>Gasto Total Aprovado</td><td class="num hl">R$ 138.759.653,82</td><td>Base econ&ocirc;mica para calibra&ccedil;&atilde;o dos cen&aacute;rios MILP</td></tr>
    <tr><td>Regress&otilde;es de Hod&ocirc;metro</td><td class="num hl">6.841 em 3.116 ve&iacute;culos</td><td>Exige valida&ccedil;&atilde;o mon&oacute;tona antes da modelagem</td></tr>
    <tr><td>Discrepância Semântica de Tipos</td><td class="num hl">270.510 Corretivas / 37.897 Preventivas</td><td>Campo TRIM(ds_codigo_manutencao) recupera sinal real</td></tr>
    <tr><td>OS Reprovadas (Glosas)</td><td class="num hl">55.259</td><td>Valida&ccedil;&atilde;o cruzada com fiscaliza&ccedil;&atilde;o estadual</td></tr>
  </tbody>
</table>
</div>


<!-- CAP 5 — VALIDACAO -->
<div class="chapter">
<div class="timing">Bloco 5 &mdash; &asymp; 5 minutos</div>
<h2>Cap. 5 &mdash; Valida&ccedil;&atilde;o</h2>

<h3>5.1 Classifica&ccedil;&atilde;o de Risco &mdash; Teste Retido 2025&ndash;2026</h3>
<p class="noindent">Preval&ecirc;ncia da classe positiva em t+1: 78,77%.</p>
<table>
  <thead>
    <tr><th>Modelo</th><th>PR-AUC</th><th>ROC-AUC</th><th>Brier Score</th><th>ECE</th><th>F1 M&aacute;x.</th></tr>
  </thead>
  <tbody>
    <tr><td class="hl">HistGradientBoosting &#127942;</td><td class="num hl">0,9099</td><td class="num hl">0,8064</td><td class="num hl">0,1334</td><td class="num hl">0,0238</td><td class="num hl">0,8884</td></tr>
    <tr><td>Random Forest</td><td class="num">0,9081</td><td class="num">0,8016</td><td class="num">0,1362</td><td class="num">0,0660</td><td class="num">0,8873</td></tr>
    <tr><td>&Aacute;rvore de Decis&atilde;o</td><td class="num">0,9041</td><td class="num">0,7905</td><td class="num">0,1378</td><td class="num">0,1303</td><td class="num">0,8837</td></tr>
    <tr><td>Extra Trees</td><td class="num">0,8796</td><td class="num">0,7631</td><td class="num">0,1710</td><td class="num">0,2381</td><td class="num">0,8777</td></tr>
    <tr><td>Regress&atilde;o Log&iacute;stica</td><td class="num">0,8660</td><td class="num">0,7366</td><td class="num">0,1673</td><td class="num">0,2258</td><td class="num">0,8750</td></tr>
    <tr><td><em>Baseline Ing&ecirc;nuo</em></td><td class="num">0,7924</td><td class="num">0,5000</td><td class="num">0,1873</td><td class="num">0,0390</td><td class="num">&mdash;</td></tr>
  </tbody>
</table>

<h3>5.2 Regress&atilde;o N&atilde;o Linear de Custo (R$/M&ecirc;s)</h3>
<p class="noindent"><em>Regress&atilde;o linear exclu&iacute;da conforme Se&ccedil;&atilde;o 5.3 do Anteprojeto.</em></p>
<table>
  <thead>
    <tr><th>Modelo N&atilde;o Linear</th><th>MAE (R$)</th><th>RMSE (R$)</th><th>R&sup2; Fora da Amostra</th><th>sMAPE (%)</th></tr>
  </thead>
  <tbody>
    <tr><td class="hl">HistGradientBoosting &#127942;</td><td class="num hl">R$ 2.311,82</td><td class="num hl">R$ 4.363,75</td><td class="num hl">0,0994</td><td class="num hl">98,51%</td></tr>
    <tr><td>Random Forest</td><td class="num">R$ 2.353,31</td><td class="num">R$ 4.426,50</td><td class="num">0,0734</td><td class="num">99,87%</td></tr>
    <tr><td>Extra Trees</td><td class="num">R$ 2.354,89</td><td class="num">R$ 4.441,20</td><td class="num">0,0672</td><td class="num">100,96%</td></tr>
    <tr><td>&Aacute;rvore de Regress&atilde;o</td><td class="num">R$ 2.407,47</td><td class="num">R$ 4.566,07</td><td class="num">0,0140</td><td class="num">101,13%</td></tr>
    <tr><td><em>Mediana Hist&oacute;rica (Baseline)</em></td><td class="num">R$ 2.209,02</td><td class="num">R$ 4.811,12</td><td class="num">&minus;0,0947</td><td class="num">104,13%</td></tr>
  </tbody>
</table>

<h3>5.3 Estudo de Abla&ccedil;&atilde;o &mdash; Fontes M vs M+P</h3>
<table>
  <thead>
    <tr><th>Tarefa</th><th>M&eacute;trica</th><th>Espa&ccedil;o M</th><th>Espa&ccedil;o M+P</th><th>Ganho &Delta;</th></tr>
  </thead>
  <tbody>
    <tr><td>Classifica&ccedil;&atilde;o de Risco</td><td class="num">PR-AUC</td><td class="num">0,9060</td><td class="num hl">0,9099</td><td class="num hl">+0,43%</td></tr>
    <tr><td>Regress&atilde;o de Custos</td><td class="num">MAE (R$)</td><td class="num">R$ 2.321,28</td><td class="num hl">R$ 2.311,82</td><td class="num hl">&minus;R$ 9,47/m&ecirc;s</td></tr>
  </tbody>
</table>

<h3>5.4 Detec&ccedil;&atilde;o de Anomalias &mdash; Isolation Forest</h3>
<div class="box-result">
  <p class="noindent">Teste t de concord&acirc;ncia com reprova&ccedil;&otilde;es reais: <strong>t = 3,52, p = 0,000426</strong>.
  OS reprovadas apresentam escores significativamente mais an&ocirc;malos &mdash; confirma ader&ecirc;ncia operacional.</p>
</div>
<table>
  <thead>
    <tr><th>Contamina&ccedil;&atilde;o (&nu;)</th><th>Anomalias</th><th>Jaccard M&eacute;dio (J)</th><th>N&iacute;vel de Estabilidade</th></tr>
  </thead>
  <tbody>
    <tr><td class="num">1%</td><td class="num">779 OS</td><td class="num">0,8641</td><td>Moderada / Alta</td></tr>
    <tr><td class="num">2%</td><td class="num">1.557 OS</td><td class="num">0,8678</td><td>Alta</td></tr>
    <tr><td class="num">5%</td><td class="num">3.894 OS</td><td class="num">0,8725</td><td>Excelente</td></tr>
    <tr><td class="num hl">10%</td><td class="num hl">7.787 OS</td><td class="num hl">0,8811</td><td class="hl">Excelente</td></tr>
  </tbody>
</table>

<h3>5.5 Teoria dos Grafos &mdash; Rede de Oficinas</h3>
<div class="box-result">
  <p class="noindent">Grafo bipartido ve&iacute;culos &harr; oficinas (NetworkX).
  Algoritmo de Louvain: <strong>Q = 0,5646</strong> &mdash; <strong>18 comunidades</strong> detectadas.
  M&eacute;tricas: betweenness centrality, PageRank, degree e closeness.</p>
</div>

<h3>5.6 Explicabilidade XAI</h3>
<div class="box-result">
  <p class="noindent">Concord&acirc;ncia SHAP &times; LIME (Jaccard Top-5): <strong>39,29%</strong>
  (Spearman &rho; = 0,3680). Resultado mostra que a <strong>H4 n&atilde;o foi sustentada</strong>: os dois m&eacute;todos capturam aspectos distintos
  do comportamento local do modelo &mdash; n&atilde;o s&atilde;o intercambi&aacute;veis.</p>
</div>

<h3>5.7 Otimiza&ccedil;&atilde;o Prescritiva MILP &mdash; 5 Cen&aacute;rios</h3>
<table>
  <thead>
    <tr><th>Cen&aacute;rio</th><th>Or&ccedil;amento B<sub>t</sub></th><th>Ve&iacute;culos</th><th>Risco Residual</th><th>Economia &Delta;</th></tr>
  </thead>
  <tbody>
    <tr><td>50% do Base</td><td class="num">R$ 137.227,50</td><td class="num">304</td><td class="num">72,62%</td><td class="num">2,18%</td></tr>
    <tr><td>75% do Base</td><td class="num">R$ 205.841,25</td><td class="num">457</td><td class="num">71,21%</td><td class="num">3,23%</td></tr>
    <tr><td>100% &mdash; Base</td><td class="num">R$ 274.455,00</td><td class="num">609</td><td class="num">69,83%</td><td class="num">4,26%</td></tr>
    <tr><td>125% do Base</td><td class="num">R$ 343.068,75</td><td class="num">762</td><td class="num">68,44%</td><td class="num">5,29%</td></tr>
    <tr><td class="hl">150% do Base</td><td class="num hl">R$ 411.682,50</td><td class="num hl">914</td><td class="num hl">67,07%</td><td class="num hl">6,31%</td></tr>
    <tr><td><em>Status Quo</em></td><td class="num">R$ 0,00</td><td class="num">0</td><td class="num">78,77%</td><td class="num">0,00%</td></tr>
  </tbody>
</table>
<div class="box-result">
  <p class="noindent">Cen&aacute;rio S0 (2.000 ve&iacute;culos, 36 meses), simulado:
  <strong>R$ 9.302.147,26 (17,51%)</strong>. Solver HiGHS: Gap MIP = 0,0000%;
  Gap Poliedral = 0,00057% (R$ 248,52). Reprodutibilidade verificada em Linux e
  Windows 11 &mdash; exato ao centavo em 3 baterias independentes.</p>
</div>

<h3>5.8 Testes Estat&iacute;sticos Pareados (Wilcoxon + Holm-Bonferroni)</h3>
<table>
  <thead>
    <tr><th>Compara&ccedil;&atilde;o</th><th>Estat&iacute;stica W</th><th>P-valor Ajustado (Holm)</th><th>Sig. a 5%</th></tr>
  </thead>
  <tbody>
    <tr><td>HistGB vs &Aacute;rvore de Regress&atilde;o</td><td class="num">833.682,5</td><td class="num hl">3,17 &times; 10&minus;10</td><td class="num hl">&#10003; Sim</td></tr>
    <tr><td>HistGB vs Extra Trees</td><td class="num">885.268,5</td><td class="num hl">1,63 &times; 10&minus;05</td><td class="num hl">&#10003; Sim</td></tr>
    <tr><td>HistGB vs Random Forest</td><td class="num">886.668,0</td><td class="num hl">1,05 &times; 10&minus;05</td><td class="num hl">&#10003; Sim</td></tr>
  </tbody>
</table>

<h3>5.9 Pipeline Estat&iacute;stico (Normalidade, Poisson, Markov, S&eacute;ries Temporais)</h3>
<div class="box-result">
  <ul>
    <li><strong>Normalidade (Lilliefors):</strong> Todas as dimens&otilde;es rejeitam H&#8320; (p &lt; 10&minus;16) &mdash; fundamenta o uso de m&eacute;todos n&atilde;o param&eacute;tricos.</li>
    <li><strong>Mann-Whitney U (Leves vs Comerciais):</strong> U = 95.741.081, p = 1,60 &times; 10&minus;129, efeito r = 0,121.</li>
    <li><strong>Kruskal-Wallis (Categorias):</strong> H = 568,94, p = 5,46 &times; 10&minus;123.</li>
    <li><strong>Poisson:</strong> &lambda; = 20,46 falhas/dia; VMR = 1.760,27 &mdash; sobredispers&atilde;o severa.</li>
    <li><strong>Cadeia de Markov:</strong> 62,27% Em Tr&acirc;nsito &middot; 22,42% Ocioso &middot; 15,31% Em Manuten&ccedil;&atilde;o (perman&ecirc;ncia m&eacute;dia 3,53 dias).</li>
    <li><strong>S&eacute;ries Temporais:</strong> ETS supera ARIMA(1,0,1) fora da amostra (RMSE R$ 132.063 vs R$ 159.949; AIC 1.293,9 vs 1.434,6).</li>
  </ul>
</div>
</div>


<!-- CAP 6 — DISCUSSOES -->
<div class="chapter">
<div class="timing">Bloco 6 &mdash; &asymp; 2 minutos</div>
<h2>Cap. 6 &mdash; Discuss&otilde;es</h2>

<h3>6.1 An&aacute;lise das Hip&oacute;teses</h3>
<table>
  <thead>
    <tr><th style="width:8%">Hip.</th><th style="width:38%">Enunciado</th><th style="width:17%">Resultado</th><th style="width:37%">Evid&ecirc;ncia</th></tr>
  </thead>
  <tbody>
    <tr>
      <td class="num hl">H1</td>
      <td>Integrar patrim&ocirc;nio reduz o MAE em pelo menos 15%</td>
      <td style="color:#a00000;text-align:center;font-weight:bold;">&#10007; N&atilde;o sustentada</td>
      <td>MAE &minus;0,41% (&minus;R$ 9,47 por ve&iacute;culo-m&ecirc;s); PR-AUC +0,43%. Ganho real, mas pequeno</td>
    </tr>
    <tr>
      <td class="num hl">H2</td>
      <td>HistGB supera baselines lineares e ing&ecirc;nuos</td>
      <td style="color:#c47800;text-align:center;font-weight:bold;">&#9680; Parcial</td>
      <td>Supera na classifica&ccedil;&atilde;o; a mediana hist&oacute;rica tem MAE menor</td>
    </tr>
    <tr>
      <td class="num hl">H3</td>
      <td>Pol&iacute;tica MILP reduz o custo frente &agrave; linha de base</td>
      <td class="num hl">&#10003; Sustentada</td>
      <td>Cen&aacute;rio S0: R$ 9,30 mi (17,51%), simula&ccedil;&atilde;o</td>
    </tr>
    <tr>
      <td class="num hl">H4</td>
      <td>SHAP e LIME concordam em mais de 85%</td>
      <td style="color:#a00000;text-align:center;font-weight:bold;">&#10007; N&atilde;o sustentada</td>
      <td>Jaccard Top-5 = 39,29%; &rho; = 0,3680 (metas: 0,85)</td>
    </tr>
  </tbody>
</table>

<h3>6.2 Limita&ccedil;&otilde;es Reconhecidas</h3>
<ul>
  <li><strong>Resultado contrafactual:</strong> A economia MILP &eacute; simulada retrospectivamente; n&atilde;o equivale a economia causal sem valida&ccedil;&atilde;o prospectiva.</li>
  <li><strong>Efic&aacute;cia da interven&ccedil;&atilde;o (&eta;):</strong> N&atilde;o estimada com dados observacionais compar&aacute;veis; cen&aacute;rios de sensibilidade foram usados como mitiga&ccedil;&atilde;o.</li>
  <li><strong>Generaliza&ccedil;&atilde;o:</strong> Resultados referem-se &agrave; frota estadual de SC no per&iacute;odo auditado.</li>
  <li><strong>LGPD:</strong> Identificadores de condutores pseudonimizados; dados brutos n&atilde;o redistribu&iacute;veis (Lei n&ordm; 13.709/2018).</li>
</ul>

<h3>6.3 Compara&ccedil;&atilde;o com a Literatura</h3>
<p>Mahale, Kolhar e More (2025) apontam a disponibilidade de dados e a ado&ccedil;&atilde;o de XAI como
desafios da manuten&ccedil;&atilde;o preditiva veicular; este estudo trata os dois com dados reais.
A H4 n&atilde;o sustentada &eacute; coerente com a ressalva do anteprojeto (se&ccedil;&atilde;o 4.4) de que
explica&ccedil;&otilde;es podem ser inst&aacute;veis quando os atributos s&atilde;o correlacionados.</p>
</div>


<!-- CAP 7 — CONCLUSAO -->
<div class="chapter">
<div class="timing">Bloco 7 &mdash; &asymp; 2 minutos</div>
<h2>Cap. 7 &mdash; Conclus&atilde;o</h2>

<h3>7.1 Principais Contribui&ccedil;&otilde;es</h3>
<div class="box-result">
  <ul>
    <li><strong>Emp&iacute;rica:</strong> Base anal&iacute;tica longitudinal com 350.737 OS, auditoria forense de 6.841 regress&otilde;es de hod&ocirc;metro e diagn&oacute;stico inédito da discrepância sem&acirc;ntica de tipos de OS na frota estadual de SC.</li>
    <li><strong>Metodol&oacute;gica:</strong> Arquitetura completa conectando auditoria &rarr; modelos preditivos &rarr; XAI &rarr; MILP prescritiva, com valida&ccedil;&atilde;o Rolling-Origin e testes estat&iacute;sticos pareados.</li>
    <li><strong>Computacional:</strong> Artefato reprodut&iacute;vel (sub-reposit&oacute;rio p&uacute;blico), homologado cross-platform (Linux e Windows 11), exato ao centavo em 3 baterias independentes.</li>
    <li><strong>Gest&atilde;o P&uacute;blica:</strong> Pol&iacute;tica prescritiva com economia contrafactual de R$ 9.302.147,26 (17,51%) e proje&ccedil;&atilde;o trienal de R$ 40.088.374,00 (2027&ndash;2029).</li>
  </ul>
</div>

<h3>7.2 Trabalhos Futuros</h3>
<ul>
  <li>Valida&ccedil;&atilde;o prospectiva da pol&iacute;tica prescritiva em per&iacute;odo real de opera&ccedil;&atilde;o.</li>
  <li>Extens&atilde;o do modelo de Markov para estados com granularidade de tipo de falha.</li>
  <li>Incorpora&ccedil;&atilde;o de dados de telemetria IoT em tempo real para atualiza&ccedil;&atilde;o din&acirc;mica dos par&acirc;metros de risco.</li>
  <li>Avalia&ccedil;&atilde;o com especialistas em manuten&ccedil;&atilde;o sobre clareza e plausibilidade das explica&ccedil;&otilde;es SHAP e LIME.</li>
  <li>Estudo de generaliza&ccedil;&atilde;o para outras frotas estaduais com estrutura de dados similar.</li>
</ul>

<h3>7.3 Considera&ccedil;&otilde;es Finais</h3>
<p>Este trabalho demonstrou que &eacute; poss&iacute;vel conectar integra&ccedil;&atilde;o de dados administrativos
heterog&ecirc;neos, compara&ccedil;&atilde;o controlada de modelos preditivos n&atilde;o lineares e otimiza&ccedil;&atilde;o
prescritiva em um artefato computacional audit&aacute;vel e reprodut&iacute;vel. Os resultados fornecem
evid&ecirc;ncia quantitativa robusta para apoiar o planejamento de manuten&ccedil;&atilde;o e a aloca&ccedil;&atilde;o
or&ccedil;ament&aacute;ria de frotas p&uacute;blicas. As recomenda&ccedil;&otilde;es permanecem como suporte ao gestor
&mdash; n&atilde;o substituem crit&eacute;rios de seguran&ccedil;a, normas do fabricante ou julgamento t&eacute;cnico.</p>

<div class="section-footer">
  PPGCAP / CCT / UDESC &mdash; Eduardo Lopes Jonker &mdash; Outubro de 2026 &nbsp;&middot;&nbsp;
  Conte&uacute;do extra&iacute;do de: <em>Anteprojeto de Pesquisa</em>,
  <em>MAPA_MENTAL_PROJETO.md</em>, <em>relatorio_metodologico_estatistico.md</em> e
  <em>README.md</em>.
</div>
</div>


<!-- REFERENCIAS -->
<div class="chapter">
<h2>Refer&ecirc;ncias Principais</h2>
<p class="noindent" style="font-size:9pt; color:#555; margin-bottom:4mm;">
  Sele&ccedil;&atilde;o das 10 refer&ecirc;ncias mais diretamente citadas no trabalho,
  extra&iacute;das dos arquivos <em>Periodicos-CAPES-BibTex (7).bib</em>,
  <em>Periodicos-CAPES-BibTex (8).bib</em>, <em>Periodicos-CAPES-BibTex (5).bib</em>
  e <em>Periodicos-CAPES-BibTex (1).bib</em> presentes em <code>documentos_academicos/</code>.
  Formato: Sobrenome, Ano (conforme orienta&ccedil;&atilde;o do programa).
</p>

<ol style="font-size: 9.5pt; line-height: 1.65; margin-left: 5mm;">

  <li style="margin-bottom: 3mm;">
    DALZOCHIO, J.; KUNST, R.; PIGNATON, E.; BINOTTO, A.; SANYAL, S.; FAVILLA, J.;
    BARBOSA, J. <strong>Machine learning and reasoning for predictive maintenance in
    Industry 4.0: Current status and challenges.</strong>
    <em>Computers in Industry</em>, v. 123, p. 103298, 2020.
    DOI: 10.1016/j.compind.2020.103298.
  </li>

  <li style="margin-bottom: 3mm;">
    VAN DINTER, R.; TEKINERDOGAN, B.; CATAL, C. <strong>Predictive maintenance using
    digital twins: A systematic literature review.</strong>
    <em>Information and Software Technology</em>, v. 151, p. 107008, 2022.
    DOI: 10.1016/j.infsof.2022.107008.
  </li>

  <li style="margin-bottom: 3mm;">
    ESTEBAN, A.; ZAFRA, A.; VENTURA, S. <strong>Data mining in predictive maintenance
    systems: A taxonomy and systematic review.</strong>
    <em>Wiley Interdisciplinary Reviews: Data Mining and Knowledge Discovery</em>,
    v. 12, n. 5, 2022. DOI: 10.1002/widm.1471.
  </li>

  <li style="margin-bottom: 3mm;">
    MENG, H.; LIU, X.; XING, J.; ZIO, E. <strong>A method for economic evaluation of
    predictive maintenance technologies by integrating system dynamics and evolutionary
    game modelling.</strong>
    <em>Reliability Engineering &amp; System Safety</em>, v. 222, p. 108424, 2022.
    DOI: 10.1016/j.ress.2022.108424.
  </li>

  <li style="margin-bottom: 3mm;">
    LIU, Y.-Y.; CHANG, K.-H.; CHEN, Y.-Y. <strong>Simultaneous predictive maintenance
    and inventory policy in a continuously monitoring system using simulation
    optimization.</strong>
    <em>Computers &amp; Operations Research</em>, v. 153, p. 106146, 2023.
    DOI: 10.1016/j.cor.2023.106146.
  </li>

  <li style="margin-bottom: 3mm;">
    LONGO, L.; BRCIC, M.; CABITZA, F. et al. <strong>Explainable Artificial Intelligence
    (XAI) 2.0: A manifesto of open challenges and interdisciplinary research
    directions.</strong>
    <em>Information Fusion</em>, v. 106, p. 102301, 2024.
    DOI: 10.1016/j.inffus.2024.102301.
  </li>

  <li style="margin-bottom: 3mm;">
    WANG, H.; LIANG, Q.; HANCOCK, J. T.; KHOSHGOFTAAR, T. M. <strong>Feature selection
    strategies: a comparative analysis of SHAP-value and importance-based methods.</strong>
    <em>Journal of Big Data</em>, v. 11, n. 1, 2024.
    DOI: 10.1186/s40537-024-00905-w.
  </li>

  <li style="margin-bottom: 3mm;">
    REDMER, A. <strong>Strategic vehicle fleet management &ndash; a joint solution of
    make-or-buy, composition and replacement problems.</strong>
    <em>Journal of Quality in Maintenance Engineering</em>, v. 28, n. 2,
    p. 327&ndash;349, 2020. DOI: 10.1108/jqme-04-2020-0026.
  </li>

  <li style="margin-bottom: 3mm;">
    ROKHFOROZ, P.; FINK, O. <strong>Hierarchical multi-agent predictive maintenance
    scheduling for trains using price-based approach.</strong>
    <em>Computers &amp; Industrial Engineering</em>, v. 159, p. 107475, 2021.
    DOI: 10.1016/j.cie.2021.107475.
  </li>

  <li style="margin-bottom: 3mm;">
    REN, Y. <strong>Optimizing Predictive Maintenance With Machine Learning for
    Reliability Improvement.</strong>
    <em>ASCE-ASME Journal of Risk and Uncertainty in Engineering Systems,
    Part B: Mechanical Engineering</em>, v. 7, n. 3, 2021.
    DOI: 10.1115/1.4049525.
  </li>

</ol>
</div>


</body>
</html>
"""

html_tmp = ROOT / "_mep_tmp.html"
html_tmp.write_text(HTML, encoding="utf-8")

print(f"Gerando {OUT} ...")
doc = weasyprint.HTML(filename=str(html_tmp)).write_pdf()
OUT.write_bytes(doc)
html_tmp.unlink()

size_kb = OUT.stat().st_size / 1024
print(f"PDF gerado com sucesso: {OUT}")
print(f"Tamanho: {size_kb:.1f} KB")

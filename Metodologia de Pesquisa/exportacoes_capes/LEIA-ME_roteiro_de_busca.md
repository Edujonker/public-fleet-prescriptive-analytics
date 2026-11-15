# Roteiro de busca nas bases (acesso pelo Portal de Periódicos CAPES / CAFe)

Esta pasta recebe as exportações das buscas que você faz no navegador. O pipeline
`scripts/rsl_prisma.py` lê automaticamente todos os arquivos daqui na próxima execução.

## 1. Como acessar

1. Entre em <https://www.periodicos.capes.gov.br> → **Acesso CAFe** → UDESC → seu login institucional.
2. No Portal, busque o nome da base (Scopus, Web of Science, IEEE Xplore, ACM Digital Library) e abra pelo link do Portal, para a sessão ser reconhecida como UDESC.
3. Faça **uma busca por base**, exatamente como abaixo, e exporte **todos** os resultados.

## 2. Frase de busca do protocolo (seção 5.1)

```
("prescriptive analytics" OR "predictive analytics" OR "decision support" OR "decision support system*"
 OR "process mining" OR "process optimization" OR "business process*")
AND
("explainable artificial intelligence" OR "explainable AI" OR XAI OR "interpretable machine learning"
 OR "algorithmic transparency")
AND
("data governance" OR "privacy by design" OR "data protection" OR privacy OR accountability
 OR auditability OR "public sector" OR government OR "public administration")
```

**Filtro na base: só o período, 2020 a 2026.** Não filtre idioma nem tipo de documento na base:
o pipeline aplica CO2 (idioma) e CO4 (tipo) e conta essas exclusões no fluxograma PRISMA.

## 3. Sintaxe por base

### Scopus — campo título, resumo e palavras-chave
```
TITLE-ABS-KEY(("prescriptive analytics" OR "predictive analytics" OR "decision support" OR "decision support system*" OR "process mining" OR "process optimization" OR "business process*") AND ("explainable artificial intelligence" OR "explainable AI" OR XAI OR "interpretable machine learning" OR "algorithmic transparency") AND ("data governance" OR "privacy by design" OR "data protection" OR privacy OR accountability OR auditability OR "public sector" OR government OR "public administration")) AND PUBYEAR > 2019 AND PUBYEAR < 2027
```
Exportar: **Export → RIS** (ou CSV), marcando *Citation information* e *Abstract & keywords*.

### Web of Science (Core Collection) — Advanced Search, campo TS (tópico = título, resumo, palavras-chave)
```
TS=(("prescriptive analytics" OR "predictive analytics" OR "decision support" OR "decision support system*" OR "process mining" OR "process optimization" OR "business process*") AND ("explainable artificial intelligence" OR "explainable AI" OR XAI OR "interpretable machine learning" OR "algorithmic transparency") AND ("data governance" OR "privacy by design" OR "data protection" OR privacy OR accountability OR auditability OR "public sector" OR government OR "public administration")) AND PY=(2020-2026)
```
Exportar: **Export → RIS (other reference software)** ou **BibTeX**, conteúdo *Full Record*.
Se houver mais de 1.000 resultados, exporte em partes (registros 1–1000, 1001–2000…).

### IEEE Xplore — Advanced Search → Command Search
```
("All Metadata":"prescriptive analytics" OR "All Metadata":"predictive analytics" OR "All Metadata":"decision support" OR "All Metadata":"process mining" OR "All Metadata":"process optimization" OR "All Metadata":"business process*") AND ("All Metadata":"explainable artificial intelligence" OR "All Metadata":"explainable AI" OR "All Metadata":XAI OR "All Metadata":"interpretable machine learning" OR "All Metadata":"algorithmic transparency") AND ("All Metadata":"data governance" OR "All Metadata":"privacy by design" OR "All Metadata":"data protection" OR "All Metadata":privacy OR "All Metadata":accountability OR "All Metadata":auditability OR "All Metadata":"public sector" OR "All Metadata":government OR "All Metadata":"public administration")
```
Filtro: *Year 2020–2026*. Exportar: **Export → Citations → RIS**, *Citation & Abstract* (ou CSV).
**Adaptação a registrar:** o IEEE limita o número de termos e de curingas por consulta; por isso
usa-se o campo *All Metadata* em vez de título/resumo/palavras-chave separados, e
"decision support system*" fica coberto por "decision support". Se a interface recusar a consulta,
anote a mensagem e a consulta que funcionou.

### ACM Digital Library — Advanced Search, campos título, resumo e palavras-chave
Para cada um dos três blocos acima, use os campos `Title:`, `Abstract:` e `Keyword:` unidos por OR,
e una os três blocos por AND. Exemplo do bloco 2:
```
(Title:("explainable artificial intelligence" OR "explainable AI" OR XAI OR "interpretable machine learning" OR "algorithmic transparency") OR Abstract:(...) OR Keyword:(...))
```
Filtro: *Publication date 2020–2026*. Exportar: selecionar todos → **Export Citations → BibTeX**.
Se a interface não aceitar os campos, use *Search within: Anywhere* e registre a adaptação.

## 4. Nome dos arquivos

`<base>_<AAAA-MM-DD>[_parteN].<ext>`, com base em `scopus`, `wos`, `ieee` ou `acm`. Exemplos:

```
scopus_2026-11-20.ris
wos_2026-11-20_parte1.ris
wos_2026-11-20_parte2.ris
ieee_2026-11-20.csv
acm_2026-11-20.bib
```

Formatos aceitos: `.ris`, `.bib`, `.csv` (Scopus ou IEEE).

## 5. Registro obrigatório (PRISMA 2020, item 7)

Para cada arquivo, preencha uma linha em `registro_buscas.csv` (abre no Excel/LibreOffice, separador `;`):
data e hora, consulta **exatamente como submetida**, campos, filtros e número de resultados que a base
mostrou. O pipeline junta esse registro ao inventário de fontes e ao relatório do artigo.

## 6. Bases chinesas (busca manual)

CNKI (中国知网), Wanfang (万方) e CQVIP (维普) não têm API pública e os termos de uso não
permitem coleta automatizada. A parte automatizável (OpenAlex com idioma chinês) está em
`scripts/buscar_artigos_chines.py`, com saída em `artigos/idiomas/zh/`.

Acesso: a UDESC pode não assinar essas bases. Confirme com a biblioteca universitária. A CNKI
tem versão internacional (CNKI Overseas, <https://kns.cnki.net>), que exige assinatura
institucional para o texto completo. A busca e os resumos costumam ser abertos.

### CSCD — Chinese Science Citation Database (dentro da Web of Science)
No Web of Science, troque a coleção de *Web of Science Core Collection* para
**Chinese Science Citation Database**, se aparecer na lista, e use a mesma consulta `TS=(...)`
da seção 3. Exporte em RIS como `cscd_AAAA-MM-DD.ris`.

### CNKI — busca profissional (专业检索), campos SU (主题: título, resumo, palavras-chave)
```
SU=('规范性分析'+'处方性分析'+'预测分析'+'决策支持'+'异常检测'+'欺诈检测'+'舞弊识别'+'风险评估') AND SU=('可解释人工智能'+'可解释性人工智能'+'可解释机器学习'+'可解释性机器学习'+'算法透明'+'XAI') AND SU=('公共部门'+'政府'+'公共管理'+'政府采购'+'公共采购'+'税收'+'税务'+'可审计性'+'审计'+'问责')
```
Na CNKI, `+` é OU e `AND` é E. Filtro: ano 2020–2026. Se a interface recusar a expressão,
monte os três blocos na busca avançada (高级检索) com o campo 主题 e registre a adaptação.
Exportar: selecionar → 导出与分析 → **EndNote** (arquivo `.txt`), salvo como `cnki_AAAA-MM-DD.txt`.

### Wanfang — busca profissional (专业检索)
Mesma lógica de blocos, com o campo 主题 e os operadores da interface. Exportar em **EndNote**
ou **RIS** como `wanfang_AAAA-MM-DD.txt` ou `.ris`.

Os arquivos `cscd_`, `cnki_` e `wanfang_` colocados nesta pasta são lidos pelo pipeline como
bases de dados adicionais ao protocolo. Registre cada busca em `registro_buscas.csv`: a inclusão
de bases não previstas é uma emenda ao protocolo e precisa constar como tal no artigo.

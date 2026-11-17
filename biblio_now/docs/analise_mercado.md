# Biblio-now · Análise de mercado: ferramentas de busca e download de artigos científicos

Autor: Eduardo Lopes Jonker · Levantamento feito em 17/11/2026, com pesquisa na web. Os preços e os números de desempenho vêm das fontes citadas. Várias comparações publicadas são de empresas concorrentes (Paperguide, SciSpace) e servem só como indicação; o dado mais sólido é o estudo independente sobre a sensibilidade do Elicit.

## 1. Resumo

O mercado está dividido em ferramentas que fazem bem **uma** etapa do trabalho: achar artigos, ler e resumir com IA, guardar referências ou triar estudos numa revisão sistemática. Nenhuma das ferramentas analisadas faz numa só execução, de forma reprodutível e local, o ciclo completo:

**consulta booleana registrada → busca em bases abertas → download do texto completo em lote → TXT e BibTeX de cada obra → fichamento → protocolo auditável → atualização agendada.**

Esse ciclo é o núcleo do Biblio-now e o principal diferencial. Os outros diferenciais vêm das lacunas da seção 3: sensibilidade baixa das buscas por IA, falta de reprodutibilidade, custo por assinatura, dados na nuvem e pouca atenção a fontes e normas brasileiras.

## 2. Ferramentas analisadas

| Categoria | Ferramentas | O que fazem bem | Limitações para o nosso caso |
|---|---|---|---|
| Gerenciadores de referências | Zotero, Mendeley, Paperpile, EndNote | Biblioteca, citações no editor, captura pelo navegador. O Zotero é aberto e funciona offline ([Paperguide](https://paperguide.ai/blog/zotero-vs-mendeley/)) | Capturam artigo por artigo. Não fazem busca booleana em várias bases nem download em lote; não geram fichamento nem protocolo |
| Assistentes de pesquisa com IA | Elicit, Consensus, SciSpace | Perguntas em linguagem natural, resumo e extração em tabela | Sensibilidade baixa em revisões: o Elicit encontrou em média 39,5% dos estudos, contra 94,5% das buscas tradicionais ([estudo em PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12483133/)). Resultados não reprodutíveis. Assinatura: Elicit Pro US$ 39–49 por usuário/mês ([Citely](https://citely.ai/posts/elicit-alternatives-2026)); Consensus US$ 20/mês, ou US$ 12 no plano anual ([Zemith](https://www.zemith.com/en/contents/elicit-alternative)) |
| Mapas de citação | ResearchRabbit, Connected Papers, Litmaps | Acham artigos ligados por citação, mesmo com outra terminologia ([ResearchRabbit](https://www.researchrabbit.ai/articles/find-papers-with-citation-networks)). O Litmaps tem alertas de novos artigos no plano pago ([CASRAI](https://www.casrai.org/guides/litmaps)) | Partem de artigos-semente, não de uma consulta. Não baixam texto completo nem registram protocolo |
| Plataformas de revisão sistemática | Covidence, Rayyan, ASReview, DistillerSR | Triagem por dois avaliadores, resolução de conflitos e fluxograma PRISMA a partir da triagem ([CASRAI](https://casrai.org/guides/ai-tools-for-systematic-literature-review)). O ASReview é aberto e usa aprendizado ativo | Começam **depois** da busca: o usuário importa exportações das bases. Não buscam nem baixam PDFs. O Covidence é pago por instituição; o Rayyan cobra pelos recursos avançados ([CASRAI](https://casrai.org/guides/rayyan)) |
| Bases e indexadores | Google Scholar, Semantic Scholar, OpenAlex, Scopus, Web of Science | Cobertura ampla; OpenAlex e Semantic Scholar têm API aberta | O Google Scholar não tem API e limita exportação. Scopus e WoS são pagos e só mandam alertas por e-mail, sem baixar nada |
| Fluxogramas PRISMA | Pacote/app PRISMA2020 (R/Shiny) | Desenha o fluxograma a partir de números informados ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8958186/)) | Os números são digitados à mão; não há ligação com a busca real |

**Sobre confiabilidade das IA generativas:** um estudo encontrou cerca de 20% de citações inventadas no ChatGPT-4o em revisões de literatura de finanças ([Springer](https://link.springer.com/article/10.1007/s41060-025-00731-0)). As ferramentas acadêmicas (Elicit, SciSpace) erram muito menos nas referências, porque buscam antes de responder ([DergiPark](https://dergipark.org.tr/en/download/article-file/5634316)). Mesmo assim, a sensibilidade continua baixa.

## 3. Lacunas do mercado

1. **Nenhuma ferramenta junta busca, download em lote e acervo local.** Para montar um corpus hoje, o pesquisador busca numa ferramenta, exporta, importa em outra e baixa PDF por PDF.
2. **Busca por IA não substitui busca booleana reprodutível.** A sensibilidade é baixa, e a mesma pergunta dá resultados diferentes em dias diferentes. Para uma revisão sistemática, a consulta exata, a data e as bases precisam ficar registradas (PRISMA-S).
3. **Falta de rastreabilidade.** Nenhuma ferramenta gera um registro à prova de adulteração do que foi buscado, quando e com qual resultado.
4. **Revisão viva (living review) é cara e manual.** Os alertas avisam, mas não baixam, não fichan e não atualizam o fluxograma.
5. **Dados e textos ficam na nuvem do fornecedor.** Isso afeta grupos com dados sensíveis, pesquisa em órgãos públicos e LGPD.
6. **Assinaturas em dólar.** Pesam para estudantes e universidades brasileiras.
7. **Pouca atenção ao contexto brasileiro:**
   - interfaces em inglês;
   - SciELO, BDTD e Portal de Periódicos CAPES ficam de fora ou com cobertura parcial;
   - não há fichamento no formato das universidades brasileiras;
   - não há indicação de Qualis.
8. **Qualidade do veículo não é conferida.** As buscas misturam revistas indexadas, preprints e periódicos de qualidade duvidosa sem aviso.
9. **Nenhuma ferramenta mede a própria cobertura.** O usuário não sabe quantos estudos relevantes a busca deixou de encontrar, exceto no modo de simulação do ASReview, que mede outra coisa (triagem).

## 4. Diferenciais para o Biblio-now

### Já implementados

| Diferencial | Lacuna que cobre |
|---|---|
| Ciclo completo em uma execução: busca booleana por blocos, download em lote de acesso aberto, PDF + TXT + BibTeX por obra | 1 |
| Consulta, data, bases e parâmetros gravados em cada execução; Protocolo Sigma com registros encadeados por hash (SHA-256) | 2, 3 |
| Agendamento diário, semanal ou mensal, com download e protocolo atualizados a cada execução | 4 |
| Execução local, chaves de API em cofre criptografado, sem conta nem nuvem | 5 |
| Gratuito, usando OpenAlex, Semantic Scholar e Unpaywall | 6 |
| Interface em português e planilha de fichamento que preserva o que o pesquisador digita | 7 (em parte) |
| Período dos artigos (último ano, 5 anos, 10 anos, todos ou personalizado) recalculado a cada agendamento | 4 |
| Deduplicação por DOI, por título e pelo conteúdo do PDF | 1 |

### A implementar, por prioridade

| Prioridade | Diferencial | Como fazer | Lacuna |
|---|---|---|---|
| **1** | **Fluxograma PRISMA 2020 automático e relatório PRISMA-S** a partir das execuções reais, inclusive para revisão viva | Os números já estão no protocolo; falta desenhar o fluxograma (SVG/PDF) e montar o texto PRISMA-S com consultas, datas e bases | 2, 3, 4 |
| **2** | **Medida de cobertura (revocação)** contra uma lista de referência | Já previsto na aba Validação: o usuário cola os DOIs que a busca deveria achar e vê quantos foram encontrados e baixados | 9 |
| **3** | **Fontes brasileiras:** SciELO e BDTD | SciELO (ArticleMeta) e BDTD têm APIs públicas; entram como novas fontes no núcleo | 7 |
| **4** | **Selo de qualidade do veículo:** DOAJ, preprint, Qualis | DOAJ tem API aberta; a lista Qualis da CAPES é pública e pode ser importada | 8 |
| **5** | **Verificador de referências:** conferir pelo DOI (Crossref/OpenAlex) se as referências de um texto ou de um `.bib` existem | Útil contra citações inventadas por IA; consulta por lote | confiabilidade |
| **6** | **Expansão por citações** (snowballing para trás e para frente) a partir das obras baixadas | O OpenAlex já fornece referências e citações; o código de snowballing da revisão da dissertação pode ser reaproveitado | 1 |
| **7** | **Fichamento assistido opcional:** pré-preencher objetivo, método e resultados a partir do TXT, sempre marcado como sugestão | Pode usar um modelo local, para os textos não saírem do computador; deve seguir o Guia de IA da UDESC (declaração e revisão humana) | 7 |
| **8** | **Exportação para triagem:** RIS e CSV no formato do Rayyan e do ASReview | Em vez de refazer a triagem, integrar com as ferramentas que já fazem isso bem | 1 |
| **9** | **Referências em ABNT** além do BibTeX | Gerar a referência ABNT de cada obra na planilha | 7 |

### O que não fazer

- **Não usar fontes piratas** (Sci-Hub, LibGen e similares). O valor do Biblio-now está em ser legal e auditável. O download fica restrito a versões de acesso aberto.
- **Não competir com o Zotero na gestão de citações no Word.** É melhor exportar BibTeX/RIS para ele.
- **Não vender a IA como substituta da busca sistemática.** Os dados de sensibilidade mostram o risco; a IA entra só como apoio, e declarada.

## 5. Proposta de posicionamento

> **Biblio-now: o acervo da sua revisão, completo e auditável, montado e atualizado sozinho, no seu computador.**

**Público:**
- mestrandos e doutorandos, especialmente no Brasil;
- grupos de pesquisa que mantêm revisões vivas;
- bibliotecas universitárias;
- órgãos públicos que precisam de rastreabilidade.

**Mensagem central:** onde as ferramentas de IA respondem perguntas, o Biblio-now entrega o **corpus** com o **registro de como ele foi obtido**.

## 6. Próximos passos sugeridos

1. Terminar e testar a versão atual: interface, segurança e aba Validação.
2. Implementar os diferenciais 1 (PRISMA automático) e 2 (cobertura), que usam dados que o sistema já tem.
3. Acrescentar SciELO e BDTD (diferencial 3) e o selo de qualidade (diferencial 4).
4. Validar com usuários reais: refazer a busca da revisão da dissertação no Biblio-now e comparar a cobertura com a revisão PRISMA original.

---
*Conteúdo das fontes resumido e parafraseado para fins de análise.*

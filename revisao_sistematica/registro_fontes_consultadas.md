# Registro das fontes consultadas

Gerado por `scripts/rsl_prisma.py` em 14/11/2026. Data-limite do protocolo: 14/11/2026. Período coberto: 2020–2026.

## 1. Bases de dados (PRISMA: *databases*)

| Base | Arquivo | Data | Registros lidos | Consulta submetida | Campos | Filtros | Total informado pela base | Observação |
|---|---|---|---:|---|---|---|---:|---|
| Scopus | Metodologia de Pesquisa/scobus.ris | 2026-11-14 (exportado às 14:49) | 666 | NÃO ARQUIVADA - preencher com a consulta exata | título, resumo, palavras-chave (a confirmar) | a confirmar | 666 exportados | Exportação Scopus, 14/11/2026, estratégia do protocolo (seção 5.1) |
| IEEE Xplore | Metodologia de Pesquisa/export2026.11.14-13.11.41.csv | 2026-11-14 13:11 | 25 | NÃO ARQUIVADA - preencher com a consulta exata | a confirmar | a confirmar | 25 exportados | Exportação IEEE Xplore, 14/11/2026 13:11 |
| ACM Digital Library | - | — | — | — | — | — | — | base prevista no protocolo sem exportação no projeto (desvio do protocolo) |

## 2. Outros métodos (PRISMA: *other methods*)

| Fonte | Arquivo | Data do arquivo | Registros lidos | Observação |
|---|---|---|---:|---|
| Biblioteca Paperpile | Metodologia de Pesquisa/Paperpile - Library - 14 de nov..ris | 2026-11-14 15:20 | 1622 | Biblioteca de referências do autor, exportada em 14/11/2026 |
| Biblioteca exportada (export.ris) | Metodologia de Pesquisa/export.ris | 2026-10-17 15:30 | 1334 | Biblioteca de referências exportada em 17/10/2026 |
| Periódicos CAPES (RIS) | Metodologia de Pesquisa/Periodicos-CAPES-RIS.ris | 2026-11-14 15:18 | 30 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (RIS) | Metodologia de Pesquisa/Periodicos-CAPES-RIS (1).ris | 2026-11-14 15:18 | 94 | — |
| Periódicos CAPES (RIS) | documentos_academicos/Periodicos-CAPES-RIS.ris | 2026-11-01 16:44 | 66 | — |
| Periódicos CAPES (RIS) | documentos_academicos/Periodicos-CAPES-RIS (1).ris | 2026-11-01 16:44 | 30 | — |
| Base de Dados Mestrado (BibTeX) | documentos_academicos/Base de Dados Mestrado.bib | 2026-11-01 16:44 | 60 | Base BibTeX do mestrado |
| Base de Dados Mestrado (BibTeX) | documentos_academicos/Base.mestrado.bib | 2026-11-01 16:44 | — | — |
| Referências da dissertação (Overleaf) | overleaf_dissertacao_udesc/referencias.bib | 2026-11-12 10:51 | 81 | Referências do texto da dissertação |
| Busca OpenAlex + Semantic Scholar | artigos/resultados.csv | 2026-11-14 15:57 | 880 | Busca complementar por API, 14/11/2026 (consulta diferente da do protocolo) |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex (1).bib | 2026-11-01 16:44 | 30 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex (2).bib | 2026-11-01 16:44 | 30 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex (3).bib | 2026-11-01 16:44 | 29 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex (4).bib | 2026-11-01 16:44 | 99 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex (5).bib | 2026-11-01 16:44 | 30 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex (6).bib | 2026-11-01 16:44 | 30 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex (7).bib | 2026-11-01 16:44 | 30 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex (8).bib | 2026-11-01 16:44 | 30 | Buscas exploratórias no Portal CAPES |
| Periódicos CAPES (BibTeX) | documentos_academicos/Periodicos-CAPES-BibTex.bib | — | — | cópia idêntica de documentos_academicos/Periodicos-CAPES-BibTex (7).bib (não contada) |

## 3. Serviços consultados por API

| Serviço | Uso | Volume |
|---|---|---|
| OpenAlex (api.openalex.org) | Enriquecimento por DOI: resumo, idioma, tipo, links de acesso aberto | 19 arquivos; cache em `cache/openalex_doi.json` |
| OpenAlex | Snowballing regressivo (referências dos incluídos) | 3859 registros novos |
| OpenAlex | Snowballing progressivo (trabalhos que citam os incluídos) | 1593 registros novos |
| OpenAlex + Semantic Scholar | Busca complementar `scripts/buscar_artigos.py` (consulta própria, ver `artigos/consulta.txt`) | ver seção 2 |
| Repositórios das editoras e de acesso aberto | Download dos textos completos (CO5) | 1333 relatos buscados |

## 4. Busca diária automática

A busca agendada (`scripts/atualizacao_diaria_artigos.sh`, timer `busca-artigos`) grava em `artigos/atualizacoes/` e **não entra** nesta revisão, cuja busca tem data fixa. Novos estudos só entram numa atualização formal da revisão, com nova data registrada.

## 5. Desvios em relação ao protocolo

- Bases previstas sem exportação: ACM Digital Library.
- Consulta exata não arquivada: Scopus, IEEE Xplore (preencher em `Metodologia de Pesquisa/exportacoes_capes/registro_buscas.csv`).
- Triagem e elegibilidade aplicadas por regras explícitas (assistidas por computador), pendentes de validação do avaliador em `dados/09_validacao_avaliador.csv`.

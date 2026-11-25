# Fontes da apresentação de qualificação

Gerado em 24/11/2026 08:21 por `scripts/gerar_apresentacao_qualificacao.py`. 12 verificações cruzadas aprovadas antes de salvar.


## Slide 1 — Capa

- Título, banca e linha de pesquisa: relatorios/qualificacao_pesquisa.html (capa)

## Slide 2 — 1. Contextualização e Problema de Pesquisa

- Oficinas e órgãos: dissertacao_frotas/resultados/logs/relatorio_auditoria_dados_brutos.json (granularidade)
- Hodômetro: queda de nr_quilometragem entre OS consecutivas do veículo, ordenadas por data_referencia (os_consolidadas_processadas.parquet)
- Abastecimento: relatorio_ablacao_h1.json (campo abastecimento)
- Corretivas/preventivas: tipo_manutencao_codigo em os_itens_processados.parquet
- Marco legal e Cartilha GFI: relatorios/qualificacao_pesquisa.html

## Slide 3 — 2. Base Empírica Censitária e Conciliação Contábil

- dissertacao_frotas/resultados/logs/relatorio_auditoria_dados_brutos.json (granularidade, auditoria_financeira, certificados)
- dissertacao_frotas/resultados/logs/rastreabilidade_saneamento.json (etapa 04_painel_longitudinal_ml)
- Período: min/max de data_referencia; corte de cobertura: resultados_loa_pca_2026/resultado_experimento.json

## Slide 4 — 3. Lacunas Científicas e Pergunta de Pesquisa

- Lacunas e pergunta: relatorios/qualificacao_pesquisa.html
- Assimetria e curtose: scripts/hipoteses_oficiais.py (P1, de certificado_reprodutibilidade_cientifica.json)
- Estudos incluídos: revisao_sistematica/resultados_prisma.json (n_incluidos)

## Slide 5 — 4. Delineamento Epistemológico (Volpato)

- Delineamento: relatorios/qualificacao_pesquisa.html (seções 4 e 5)
- Corte temporal: dissertacao_frotas/resultados/logs/relatorio_ablacao_h1.json (corte_temporal)
- Critérios: docs/hipoteses/ e scripts/hipoteses_oficiais.py

## Slide 6 — 5. Hipóteses e Critérios Pré-Registrados

- scripts/hipoteses_oficiais.py (H), conferido com certificado_reprodutibilidade_cientifica.json (matriz_hipoteses)
- Regra de decisão: certificado_reprodutibilidade_cientifica.json (regra_de_decisao)

## Slide 7 — 6. Arquitetura Ponta a Ponta e Saneamento de Dados

- Figura: overleaf_dissertacao_udesc/figuras/fig64_pipeline_arquitetura_integrada.png (scripts/gerar_figuras_oficiais.py)
- dissertacao_frotas/resultados/logs/rastreabilidade_saneamento.json; dissertacao_frotas/resultados/logs/relatorio_ablacao_h1.json (n_treino, n_teste)
- Hodômetro e tipo de manutenção: parquets processados (calculados por este script)

## Slide 8 — 7. Detecção Não Supervisionada de Anomalias (Isolation Forest)

- dissertacao_frotas/resultados/logs/relatorio_deteccao_anomalias.json (modelo_referencia, estabilidade_sementes, concordancia_fiscal)
- Figura: dissertacao_frotas/resultados/figuras/estabilidade_jaccard_contaminacao.png (gerada pela etapa 05)

## Slide 9 — 8. Modelagem Preditiva de Risco e Custo (Hipótese H2)

- dissertacao_frotas/resultados/logs/relatorio_modelagem_preditiva.json (metricas_classificacao, metricas_regressao)
- dissertacao_frotas/resultados/logs/relatorio_h2_svr.json (resumo_media_dp, comparacao_pareada_semente42)
- Figura: overleaf_dissertacao_udesc/figuras/fig10_comparativo_mae_rmse_modelos.png

## Slide 10 — 9. Estudo de Ablação Multimodal (Hipótese H1)

- dissertacao_frotas/resultados/logs/relatorio_ablacao_h1.json; scripts/hipoteses_oficiais.py (V h1_*)
- Figura: overleaf_dissertacao_udesc/figuras/fig12_ablativo_fontes_m_vs_mp.png

## Slide 11 — 10. Otimização Prescritiva via MILP (Hipótese H3)

- dissertacao_frotas/resultados/logs/relatorio_otimizacao_milp.json; scripts/hipoteses_oficiais.py (V h3_*)
- Figura: overleaf_dissertacao_udesc/figuras/fig14_otimizacao_sensibilidade_orcamento.png

## Slide 12 — 11. Auditoria de Explicabilidade (Hipótese H4)

- dissertacao_frotas/resultados/logs/relatorio_explicabilidade_xai.json; dissertacao_frotas/resultados/logs/relatorio_h4_fidelidade_estabilidade.json; scripts/hipoteses_oficiais.py (V h4_*)
- Figura: overleaf_dissertacao_udesc/figuras/fig13_importancia_atributos_xai.png

## Slide 13 — 12. Modelagem Estrutural via Teoria dos Grafos

- dissertacao_frotas/resultados/logs/relatorio_teoria_grafos.json (topologia_rede); dissertacao_frotas/resultados/logs/relatorio_analise_grafos_neo4j.json (testes, A1–A4)
- Figura: overleaf_dissertacao_udesc/figuras/grafos_modelo_nulo_e_concentracao.png

## Slide 14 — 13. Aplicação: LOA e PCA 2026 da Manutenção da Frota

- resultados_loa_pca_2026/resultado_experimento.json; resultados_loa_pca_2026/execucao_orcamentaria_frota.json
- Figura: resultados_loa_pca_2026/fig_execucao_loa_2026.png (scripts/execucao_orcamentaria_frota.py)

## Slide 15 — 14. Revisão Sistemática e Reprodutibilidade

- revisao_sistematica/resultados_prisma.json
- dissertacao_frotas/resultados/logs/certificado_reprodutibilidade_cientifica.json
- docs/hipoteses/preregistro_hipoteses_exploratorias_2026.md(.sha256)

## Slide 16 — 15. Cronograma até a Defesa

- relatorios/qualificacao_pesquisa.html (Tabela 7.1, lida por este script)

## Slide 17 — 15b. BiblioNow: Busca e Download Automatizado de Artigos

- biblio_now/ (app.py, nucleo.py, agendador.py, seguranca.py)
- artigos/resultados.csv (2552 linhas), artigos/protocolo_sigma.pdf
- artigos/acervo_pdfs.csv (568 PDFs mapeados com hash)

## Slide 18 — 15c. APIs Abertas para Coleta Automatizada de Arquivos

- scripts/buscar_artigos.py (funções buscar_openalex, buscar_s2, buscar_scopus)
- biblio_now/biblionow/nucleo.py (ciclo de busca e download)
- credenciais_api.bin (cofre de senhas PBKDF2 + Fernet)

## Slide 19 — 15d. Protocolo Sigma: Rastreabilidade e Automatização da Base de Artigos

- scripts/gerar_protocolo_sigma_artigos.py (cadeia de hashes, HTML, PDF)
- biblio_now/biblionow/agendador.py (execução agendada)
- artigos/protocolo/ (CSV auditáveis), artigos/protocolo_sigma.pdf

## Slide 20 — 18. Síntese e Próximos Passos

- scripts/hipoteses_oficiais.py; relatórios citados nos slides anteriores

## Slide 21 — 19. Referências Principais

- relatorios/qualificacao_pesquisa.html (seção REFERÊNCIAS), filtrada pelas obras citadas nos slides

## Slide 22 — Agradecimentos

- overleaf_dissertacao_udesc/PreTextuais/Agradecimentos.tex

## Slide 23 — Encerramento

- —

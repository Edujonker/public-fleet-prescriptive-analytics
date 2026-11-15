# Scripts arquivados em 15/11/2026

Estes scripts saíram de uso. Ficam aqui para consulta e para o histórico do projeto. Não rode nenhum deles: vários gravam números antigos ou digitados por cima dos resultados calculados.

| Script | Motivo | Substituto |
|---|---|---|
| `executar_estudo_robustez_ablativo_avancado.py` | Ablação de H1 com patrimônio constante e combustível sintético. | `dissertacao_frotas/src/04b_ablacao_h1.py` |
| `executar_protocolo_milp_cenario_s0.py` | Narrativa MILP-0 com custos fixos; gravava `relatorios/experimento_milp_cenario_s0.json` com valores que o solver não produz. | `dissertacao_frotas/src/08_otimizacao_milp.py` (`relatorio_otimizacao_milp.json`) |
| `ajustar_citacoes_100pct.py` | Ajuste pontual de citações nos artigos de `artigos_internacionais/`, já aplicado. | — |
| `atualizar_artigo3_reconciliado.py` | Reescrita única do artigo 3 com números digitados no código (Huber 50,7%, quantílica 58,8% etc.). | Artigos em `SBC/` atualizados por `scripts/propagar_hipoteses.py` |
| `atualizar_todos_artigos_completos.py` | Inserção única de seções em 6 artigos, já aplicada. | — |
| `gerar_relatorio_ajuste_pdf.py` | Gerava `ajuste.pdf` (auditoria E01–E20 de 01/11/2026), superado pelas correções de integridade. | `relatorio_figuras_memoria_calculo.pdf`, `docs/hipoteses/desvios_do_protocolo.md` |

As cópias `.bak_hipoteses` criadas por `propagar_hipoteses.py --aplicar` foram movidas para `archives/bak_hipoteses_20261115/` (fora do git), com a mesma estrutura de pastas.

`relatorios/CADERNO_METODOLOGICO_REPRODUCIBILIDADE_FIGURAS.md` e `relatorios/MAPA_MENTAL_PROJETO.md` ainda citam `gerar_relatorio_ajuste_pdf.py`; são documentos de 01/11/2026.

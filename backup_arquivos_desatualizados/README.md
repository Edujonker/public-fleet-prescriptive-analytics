# Backup de arquivos desatualizados

Arquivos que saíram de uso mas foram guardados, em vez de apagados. Nenhum script lê esta pasta.

**Padrão de nome:** `nome_AAAAMMDD_HHMM.ext`, com a data e a hora da última modificação do arquivo antes de ser arquivado. Itens que já tinham data no nome (por exemplo `backup_resultados_20261114_2206`) ficaram como estavam.

## pdfs_duplicados/ (arquivados em 15/11/2026)

Cópias idênticas de PDFs que ficavam na raiz com outro nome. Os geradores passaram a gravar só o nome padrão, mais as cópias que já faziam em `relatorios_pdf/` e `Documentos/` (a documentação do sistema vai para `sistema_gestao_frotas/docs/`).

| Arquivo guardado | Nome que vale agora | Gerador |
|---|---|---|
| `qualificacao_de_pesquisa_20261115_1536.pdf` | `qualificacao_de_pesquisa.pdf` | `scripts/gerar_relatorio_qualificacao_pdf.py` |
| `mapeamento_de_pesquisa_20261115_0131.pdf` | `mapeamento_de_pesquisa.pdf` | `scripts/gerar_mapeamento_pesquisa_pdf.py` |
| `documentacao_gestao_de_fortas_20261115_0131.pdf` | `documentacao_gestao_de_frotas.pdf` | `scripts/compilar_documentacao_gestao_frotas_pdf.py` |
| `conciliacao_do_trabalho_pratico_com_o_referencial_teorico_20261115_0131.pdf` | `conciliacao_teorico_pratica.pdf` | `scripts/gerar_relatorio_conciliacao_teorico_pratica_pdf.py` |
| `relatorio_referencial_teorico_e_resultados_20261115_0131.pdf` | `conciliacao_teorico_pratica.pdf` | idem |

## apresentacoes_sic_antigas/

Versões anteriores das apresentações do SIC (34º e 36º) e do Seminário de Inovação, de 01/11 a 13/11/2026. A versão em uso é `SIC/SIC_final.pptx`, gerada por `scripts/gerar_apresentacao_sic.py`.

## scripts_arquivados/

Antiga pasta `scripts/arquivados/`: scripts fora de uso. `superados_2026-11-15/README.md` explica os seis scripts arquivados em 15/11/2026 e os substitutos. Não rode nenhum deles: vários gravam números antigos ou digitados por cima dos resultados calculados.

## backups_locais/ (fora do git)

Ignorada no `.gitignore` por conter dados e resultados antigos (cerca de 1,6 GB).

| Item | Conteúdo |
|---|---|
| `backup_resultados_20261114_2206` | Resultados de antes das correções de integridade. Única cópia dos números antigos. |
| `Teste_Windows_01_20261022` | Homologação Linux × Windows antiga (precisa ser refeita). |
| `bak_hipoteses_20261115` | Cópias `.bak_hipoteses` de antes da propagação das hipóteses. |
| `Antigravity_IDE_20261011_1918.tar.gz` | Pacote de IDE; não parece ser do projeto. |

O backup de comparação desta rodada continua em `archives/backup_resultados_20261115_1519`.

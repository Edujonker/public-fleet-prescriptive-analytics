# Gráficos estatísticos em R

Gráficos da dissertação feitos em R (ggplot2 + ggdist). Leem os números já calculados pelo pipeline em Python;
nenhuma decisão de hipótese é refeita aqui.

## Preparar o ambiente (uma vez por computador)

```bash
Rscript R/instalar_pacotes.R
```

Instala os pacotes em `R/renv/library` (fora do git) nas versões de `R/renv.lock`. No Ubuntu usa binários do
Posit Public Package Manager, sem compilar.

## Gerar os gráficos do estudo de robustez (1.000 repetições)

```bash
python scripts/estudo_robustez_100.py consolidar   # cria resultados_robustez_100/resultado_robustez.json
Rscript R/graficos_robustez.R
```

Saída em `dissertacao_frotas/resultados/figuras_r/` (PNG 300 dpi e PDF vetorial para o LaTeX):

| Arquivo | Conteúdo |
|---|---|
| `fig_r_hipoteses_1000` | Distribuição de cada medida das hipóteses H1–H4 nas 1.000 repetições, intervalo P2,5–P97,5, valor oficial (r = 0) e critério do pré-registro |
| `fig_r_desempenho_modelos_1000` | Intervalos de 50%, 80% e 95% das métricas de classificação e de regressão por modelo |
| `fig_r_convergencia_niveis` | Média e P2,5–P97,5 em 1×, 10×, 100× e 1.000× repetições |
| `fig_r_matriz_confusao_media` | Matriz de confusão média ± desvio-padrão por classificador |
| `sessao_R.txt` | Versões do R e dos pacotes usados |

Os critérios (limiares) vêm do bloco `criterios` de `resultado_robustez.json`, gravado a partir do dicionário
`CRITERIOS` em `scripts/estudo_robustez_100.py`. Nenhum número é digitado nos scripts R.

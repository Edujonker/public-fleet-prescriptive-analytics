# Gráficos estatísticos (R/ggplot2) do estudo de robustez com 1.000 repetições.
# Autor: Eduardo Lopes Jonker · Dissertação PPGCAP/UDESC
#
# Uso, na raiz do projeto (depois de "python scripts/estudo_robustez_100.py consolidar"):
#   Rscript R/graficos_robustez.R
#
# Entradas (nada é digitado à mão aqui):
#   resultados_robustez_100/<parte>__<pid>.csv   valores de cada repetição (r = 0 é a configuração oficial)
#   resultados_robustez_100/resultado_robustez.json   resumos por nível (1×, 10×, 100×, 1.000×), matriz de confusão
#                                                    média e os critérios do pré-registro (bloco "criterios")
# Saídas: dissertacao_frotas/resultados/figuras_r/*.png (300 dpi) e *.pdf (vetorial, para o LaTeX)
# Estes gráficos só mostram os números já calculados em Python; nenhuma decisão de hipótese é refeita aqui.

suppressPackageStartupMessages({
  raiz_r <- normalizePath(if (dir.exists("R")) "R" else ".", mustWork = TRUE)
  renv::load(raiz_r, quiet = TRUE)
  library(ggplot2); library(dplyr); library(tidyr); library(readr)
  library(jsonlite); library(ggdist); library(patchwork); library(scales); library(forcats)
})

raiz <- dirname(raiz_r)
dir_rob <- file.path(raiz, "resultados_robustez_100")
dir_out <- file.path(raiz, "dissertacao_frotas", "resultados", "figuras_r")
dir.create(dir_out, recursive = TRUE, showWarnings = FALSE)

R <- fromJSON(file.path(dir_rob, "resultado_robustez.json"), simplifyVector = FALSE)
if (is.null(R$criterios)) stop("resultado_robustez.json sem o bloco 'criterios': rode de novo a consolidação em Python")
K <- R$criterios
N <- R$niveis[["1000"]]
if (is.null(N)) stop("nível 1000× ausente no JSON")

# ---------------------------------------------------------------- dados por repetição (mesma regra do Python: última linha de cada rep)
ler_parte <- function(base) {
  arqs <- sort(list.files(dir_rob, pattern = paste0("^", base, "__.*\\.csv$"), full.names = TRUE))
  if (!length(arqs)) stop("sem arquivos da parte ", base)
  d <- bind_rows(lapply(arqs, function(f) read_csv(f, show_col_types = FALSE, progress = FALSE)))
  chave <- if (base == "confusao") c("rep", "modelo") else "rep"
  d |> mutate(.ordem = row_number()) |> group_by(across(all_of(chave))) |> slice_max(.ordem, n = 1) |> ungroup() |> select(-.ordem)
}
md <- ler_parte("modelos"); h2 <- ler_parte("h2"); h3 <- ler_parte("h3")
stopifnot(all(0:1000 %in% md$rep), all(0:1000 %in% h2$rep), all(0:1000 %in% h3$rep))
reps <- 1:1000

# ---------------------------------------------------------------- aparência (ABNT: título na legenda do LaTeX, não na figura)
verde <- "#00693e"; azul <- "#1f3a5f"; vermelho <- "#b42318"; cinza <- "#5b6577"
tema <- theme_minimal(base_size = 10, base_family = "sans") +
  theme(panel.grid.minor = element_blank(), strip.text = element_text(face = "bold", hjust = 0),
        plot.title = element_text(face = "bold", size = 10.5), plot.subtitle = element_text(colour = cinza, size = 8.5),
        plot.caption = element_text(colour = cinza, size = 7.5, hjust = 0), legend.position = "bottom")
theme_set(tema)
milhar <- function(x) formatC(x, format = "d", big.mark = ".", decimal.mark = ",")
fonte <- sprintf("Fonte: elaborado pelo autor (%s), %s repetições com reamostragem.", format(Sys.Date(), "%Y"), milhar(length(reps)))
fonte_ofi <- paste(fonte, "Ponto vermelho = configuração oficial (r = 0).")
# bandas de intervalo: mais escuro = 50% (centro), mais claro = 95%
cores_int <- function(escura, media, clara) scale_colour_manual("Intervalo", values = c("0.5" = escura, "0.8" = media, "0.95" = clara),
                                                                 breaks = c("0.5", "0.8", "0.95"), labels = c("50%", "80%", "95%"))
br <- function(acc = 0.01) label_number(accuracy = acc, decimal.mark = ",", big.mark = ".")
pct <- function(acc = 1) label_percent(accuracy = acc, decimal.mark = ",")

salvar <- function(g, nome, larg, alt) {
  ragg::agg_png(file.path(dir_out, paste0(nome, ".png")), width = larg, height = alt, units = "cm", res = 300)
  print(g); invisible(dev.off())
  grDevices::cairo_pdf(file.path(dir_out, paste0(nome, ".pdf")), width = larg / 2.54, height = alt / 2.54)
  print(g); invisible(dev.off())
  cat("  ", nome, "\n")
}

# distribuição (meia-violino) + intervalo P2,5–P97,5 + valor oficial + linha do critério
painel <- function(x, oficial, titulo, sub, limiar = NULL, rot_limiar = NULL, fmt = br(), lado_ok = c("acima", "abaixo")) {
  lado_ok <- match.arg(lado_ok)
  d <- tibble(x = x)
  atende <- if (is.null(limiar)) NA else if (lado_ok == "acima") mean(x > limiar) else mean(x <= limiar)
  g <- ggplot(d, aes(x = x, y = 0)) +
    stat_halfeye(fill = verde, alpha = .55, .width = .95, point_interval = "median_qi", slab_colour = NA,
                 interval_colour = azul, point_colour = azul, normalize = "panels") +
    geom_point(data = tibble(x = oficial), aes(x, -0.08), colour = vermelho, size = 2.4) +
    scale_x_continuous(labels = fmt) + scale_y_continuous(NULL, breaks = NULL) +
    labs(title = titulo, subtitle = sub, x = NULL)
  if (!is.null(limiar)) {
    dados_a_direita <- median(x) > limiar          # rótulo do lado em que há espaço (oposto aos dados)
    g <- g + geom_vline(xintercept = limiar, linetype = "dashed", colour = vermelho, linewidth = .5) +
      annotate("label", x = limiar, y = 0.95, label = sprintf("%s\n%s das repetições %s", rot_limiar,
                                                             pct(0.1)(atende), if (lado_ok == "acima") "acima" else "dentro"),
               size = 2.6, colour = vermelho, fill = "white", linewidth = 0, hjust = if (dados_a_direita) 1.05 else -0.05) +
      expand_limits(x = limiar + (limiar - median(x)) * if (dados_a_direita) 0.9 else 0.9)
  }
  g
}

ofi <- function(d, col) d[[col]][d$rep == 0]
sel <- function(d, col) d[[col]][d$rep %in% reps]

cat("Gerando em", dir_out, "\n")

# ---------------------------------------------------------------- 1. hipóteses
g1a <- painel(sel(md, "h1|ganho_mae"), ofi(md, "h1|ganho_mae"), "H1 · ganho relativo no MAE (fusão multimodal)",
              "Mediana e intervalo de 95% (P2,5–P97,5)", K$H1_ganho_mae_limiar, sprintf("limiar %s", pct()(K$H1_ganho_mae_limiar)), pct(0.1))
g1b <- painel(sel(md, "h1|dif_roc_auc"), ofi(md, "h1|dif_roc_auc"), "H1 · diferença de ROC-AUC (M+P − M)",
              "Acima de zero: a fusão melhora a classificação", 0, "zero", br(0.001))
d2 <- h2 |> filter(rep %in% reps) |> select(rep, starts_with("dif_mae_rel|")) |>
  pivot_longer(-rep, names_to = "modelo", values_to = "v") |> mutate(modelo = sub("dif_mae_rel\\|", "", modelo))
o2 <- h2 |> filter(rep == 0) |> select(starts_with("dif_mae_rel|")) |> pivot_longer(everything(), names_to = "modelo", values_to = "v") |>
  mutate(modelo = sub("dif_mae_rel\\|", "", modelo))
g2 <- ggplot(d2, aes(x = v, y = fct_rev(modelo))) +
  stat_halfeye(fill = verde, alpha = .55, .width = .95, slab_colour = NA, interval_colour = azul, point_colour = azul) +
  geom_point(data = o2, colour = vermelho, size = 2.2, position = position_nudge(y = -0.12)) +
  geom_vline(xintercept = K$H2_dif_mae_rel_max, linetype = "dashed", colour = vermelho) +
  scale_x_continuous(labels = pct()) +
  labs(title = "H2 · MAE do ensemble em relação ao SVR",
       subtitle = sprintf("Positivo: ensemble pior que o SVR-RBF.\nTracejado: não inferioridade até +%s (%s das repetições dentro)",
                          pct()(K$H2_dif_mae_rel_max), pct(0.1)(N$hipoteses$H2$reps_atende_ante / length(reps))), x = NULL, y = NULL)
g3 <- painel(sel(h3, "economia_pct"), ofi(h3, "economia_pct"), "H3 · economia do MILP sobre a linha de base BL0",
             "Cenário S0: instância refeita com a semente de cada repetição\n(até 2.000 veículos sorteados, como na etapa 08)", K$H3_economia_limiar, sprintf("limiar %s", pct()(K$H3_economia_limiar)), pct(0.1))
d4 <- md |> filter(rep %in% reps) |> transmute(rep, `Spearman (SHAP × LIME)` = `h4|spearman`, `Jaccard top-5` = `h4|jaccard`,
                                               `R² local do LIME` = `h4|lime_r2`) |> pivot_longer(-rep, names_to = "medida", values_to = "v")
o4 <- md |> filter(rep == 0) |> transmute(`Spearman (SHAP × LIME)` = `h4|spearman`, `Jaccard top-5` = `h4|jaccard`, `R² local do LIME` = `h4|lime_r2`) |>
  pivot_longer(everything(), names_to = "medida", values_to = "v")
lim4 <- tibble(medida = c("Spearman (SHAP × LIME)", "Jaccard top-5", "R² local do LIME"),
               v = c(K$H4_spearman_limiar, K$H4_jaccard_limiar, K$H4_lime_r2_min))
g4 <- ggplot(d4, aes(x = v, y = fct_rev(medida))) +
  stat_halfeye(fill = verde, alpha = .55, .width = .95, slab_colour = NA, interval_colour = azul, point_colour = azul) +
  geom_point(data = o4, colour = vermelho, size = 2.2, position = position_nudge(y = -0.12)) +
  geom_point(data = lim4, shape = "|", size = 7, colour = vermelho) +
  scale_x_continuous(labels = br(0.1), limits = c(0, 1), breaks = seq(0, 1, 0.2)) +
  labs(title = "H4 · fidelidade e estabilidade da explicação", subtitle = "Traço vermelho = critério do pré-registro", x = NULL, y = NULL)

decisoes <- vapply(c("H1", "H2", "H3", "H4"), function(h) {
  v <- N$hipoteses[[h]]
  sprintf("%s: %s (robusta: %s)", h, v$decisao_oficial, if (isTRUE(v$decisao_oficial_robusta)) "sim" else "não")
}, "")
fig1 <- (g1a | g1b) / (g2 | g3) / g4 +
  plot_annotation(caption = paste0(fonte_ofi, "\nDecisões oficiais mantidas sob reamostragem: ", paste(decisoes, collapse = " · ")))
salvar(fig1, "fig_r_hipoteses_1000", 26, 24)

# ---------------------------------------------------------------- 2. desempenho dos modelos
long_md <- md |> filter(rep %in% reps) |> select(rep, matches("^(cls|reg)\\|")) |>
  pivot_longer(-rep, names_to = "col", values_to = "v") |> separate(col, c("tarefa", "modelo", "metrica"), sep = "\\|")
rot <- c(roc_auc = "ROC-AUC", pr_auc = "PR-AUC", acuracia_balanceada = "Acurácia balanceada", brier = "Brier (menor é melhor)",
         ece = "ECE (menor é melhor)", mae = "MAE (R$; menor é melhor)", r2 = "R²")
ordem_cls <- long_md |> filter(tarefa == "cls", metrica == "roc_auc") |> group_by(modelo) |> summarise(m = median(v)) |> arrange(m) |> pull(modelo)
gcls <- long_md |> filter(tarefa == "cls", metrica %in% c("roc_auc", "pr_auc", "acuracia_balanceada", "brier", "ece")) |>
  mutate(metrica = factor(rot[metrica], rot[c("roc_auc", "pr_auc", "acuracia_balanceada", "brier", "ece")]),
         modelo = factor(modelo, ordem_cls)) |>
  ggplot(aes(v, modelo)) +
  stat_interval(aes(colour = after_stat(factor(.width))), .width = c(.5, .8, .95), linewidth = 3.2) + stat_summary(fun = median, geom = "point", size = 1.3, colour = "black") +
  cores_int(verde, "#7fbf9f", "#cfe6da") +
  facet_wrap(~metrica, scales = "free_x", nrow = 1) + scale_x_continuous(labels = br(0.01)) +
  labs(title = "Classificação de risco: distribuição das métricas nas 1.000 repetições", x = NULL, y = NULL)
ordem_reg <- long_md |> filter(tarefa == "reg", metrica == "mae") |> group_by(modelo) |> summarise(m = median(v)) |> arrange(desc(m)) |> pull(modelo)
greg <- long_md |> filter(tarefa == "reg", metrica %in% c("mae", "r2")) |>
  mutate(metrica = factor(rot[metrica], rot[c("mae", "r2")]),
         modelo = fct_recode(factor(modelo, ordem_reg), "Mediana (referência ingênua)" = "Mediana")) |>
  ggplot(aes(v, modelo)) +
  stat_interval(aes(colour = after_stat(factor(.width))), .width = c(.5, .8, .95), linewidth = 3.2) + stat_summary(fun = median, geom = "point", size = 1.3, colour = "black") +
  cores_int(azul, "#8aa6cc", "#d6e0ee") +
  facet_wrap(~metrica, scales = "free_x") +
  scale_x_continuous(labels = function(v) if (max(abs(v), na.rm = TRUE) > 10) br(1)(v) else br(0.01)(v)) +
  labs(title = "Regressão do custo mensal por veículo", x = NULL, y = NULL)
vit <- N$vitorias_por_metrica[["cls|roc_auc"]]
fig2 <- gcls / greg + plot_layout(heights = c(1.15, 1)) +
  plot_annotation(caption = paste0(fonte, "\nMelhor ROC-AUC por repetição: ",
                                   paste(sprintf("%s %s", names(vit), unlist(vit)), collapse = "; "), " (de 1.000)."))
salvar(fig2, "fig_r_desempenho_modelos_1000", 30, 18)

# ---------------------------------------------------------------- 3. convergência 1× · 10× · 100× · 1.000×
pega <- function(Nv, caminho) Reduce(function(a, k) a[[k]], caminho, Nv)
met <- list(list(c("matriz_desempenho", "cls", "HistGradientBoosting", "roc_auc"), "ROC-AUC (HistGB)", br(0.001), NULL),
            list(c("matriz_desempenho", "reg", "HistGradientBoosting", "mae"), "MAE HistGB (R$)", br(1), NULL),
            list(c("hipoteses", "H1", "ganho_mae"), "H1 · ganho no MAE", pct(0.1), K$H1_ganho_mae_limiar),
            list(c("hipoteses", "H2", "ensembles", "HistGradientBoosting", "dif_mae_rel"), "H2 · MAE HistGB vs SVR", pct(0.1), K$H2_dif_mae_rel_max),
            list(c("hipoteses", "H3", "economia_pct"), "H3 · economia sobre BL0", pct(0.1), K$H3_economia_limiar),
            list(c("hipoteses", "H4", "spearman"), "H4 · Spearman SHAP × LIME", br(0.01), K$H4_spearman_limiar))
conv <- bind_rows(lapply(met, function(m) bind_rows(lapply(names(R$niveis), function(nv) {
  s <- pega(R$niveis[[nv]], m[[1]])
  tibble(nivel = factor(paste0(milhar(as.integer(nv)), "×"), levels = c("1×", "10×", "100×", "1.000×")),
         painel = m[[2]], media = s$media, lo = s$p2_5, hi = s$p97_5)
}))))
paineis <- lapply(met, function(m) {
  d <- filter(conv, painel == m[[2]])
  g <- ggplot(d, aes(nivel, media, group = 1)) + geom_line(colour = cinza, linewidth = .4) +
    geom_pointrange(aes(ymin = lo, ymax = hi), colour = verde, size = .35) +
    scale_y_continuous(labels = m[[3]]) + labs(title = m[[2]], x = NULL, y = NULL)
  if (!is.null(m[[4]])) g <- g + geom_hline(yintercept = m[[4]], linetype = "dashed", colour = vermelho)
  g
})
fig3 <- wrap_plots(paineis, nrow = 2) +
  plot_annotation(caption = paste0("Fonte: elaborado pelo autor. Média e intervalo P2,5–P97,5 por número de repetições; ",
                                   "1× = configuração oficial; tracejado vermelho = critério do pré-registro."))
salvar(fig3, "fig_r_convergencia_niveis", 26, 14)

# ---------------------------------------------------------------- 4. matriz de confusão média
cm <- bind_rows(lapply(names(N$matriz_confusao_media), function(m) {
  x <- N$matriz_confusao_media[[m]]
  tibble(modelo = m, celula = names(x), media = vapply(x, `[[`, 0, "media"), dp = vapply(x, `[[`, 0, "dp"))
})) |>
  mutate(real = ifelse(celula %in% c("VP", "FN"), "Alto risco", "Baixo risco"),
         previsto = ifelse(celula %in% c("VP", "FP"), "Alto risco", "Baixo risco"),
         acerto = celula %in% c("VP", "VN")) |>
  group_by(modelo) |> mutate(prop = media / sum(media)) |> ungroup()
fig4 <- ggplot(cm, aes(previsto, fct_rev(real), fill = acerto, alpha = prop)) +
  geom_tile(colour = "white", linewidth = 1) +
  geom_text(aes(label = sprintf("%s\n%s ± %s\n(%s)", celula, br(0.1)(media), br(0.1)(dp), pct(0.1)(prop))), alpha = 1, size = 2.7) +
  scale_fill_manual(values = c(`TRUE` = verde, `FALSE` = vermelho), guide = "none") + scale_alpha(range = c(.25, .9), guide = "none") +
  facet_wrap(~modelo, nrow = 1) +
  labs(x = "Classe prevista", y = "Classe real", caption = paste0(fonte, "\nMédia ± desvio-padrão das contagens no conjunto de teste."))
salvar(fig4, "fig_r_matriz_confusao_media", 30, 9.5)

writeLines(capture.output(sessionInfo()), file.path(dir_out, "sessao_R.txt"))
cat("Concluído. Versões dos pacotes em", file.path(dir_out, "sessao_R.txt"), "\n")

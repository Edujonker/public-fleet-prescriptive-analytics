# Ambiente R do projeto (renv): bibliotecas próprias em R/renv/library e versões fixadas em R/renv.lock.
# Uso, na raiz do projeto:   Rscript R/instalar_pacotes.R
# Na primeira vez instala os pacotes; depois, com renv.lock presente, restaura exatamente as mesmas versões.
# Usa os binários do Posit Public Package Manager para Ubuntu (sem compilar). Em Windows/macOS usa o CRAN normal.

raiz_r <- normalizePath(if (dir.exists("R")) "R" else ".", mustWork = TRUE)
pacotes <- c("ggplot2", "dplyr", "tidyr", "readr", "jsonlite", "ggdist", "patchwork", "scales", "forcats", "ragg", "svglite")

repo <- "https://cloud.r-project.org"
if (Sys.info()[["sysname"]] == "Linux" && file.exists("/etc/os-release")) {
  os <- readLines("/etc/os-release")
  codinome <- sub("^VERSION_CODENAME=", "", grep("^VERSION_CODENAME=", os, value = TRUE))
  if (length(codinome) == 1 && nzchar(codinome)) repo <- sprintf("https://packagemanager.posit.co/cran/__linux__/%s/latest", codinome)
}
options(repos = c(CRAN = repo), renv.config.ppm.enabled = TRUE)
options(HTTPUserAgent = sprintf("R/%s R (%s)", getRversion(),
                                paste(getRversion(), R.version["platform"], R.version["arch"], R.version["os"])))

usuario <- Sys.getenv("R_LIBS_USER")
dir.create(usuario, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(usuario, .libPaths()))
if (!requireNamespace("renv", quietly = TRUE)) install.packages("renv", lib = usuario)

lock <- file.path(raiz_r, "renv.lock")
if (file.exists(lock)) {
  renv::restore(project = raiz_r, prompt = FALSE)
} else {
  renv::init(project = raiz_r, bare = TRUE, restart = FALSE, load = FALSE)
  renv::load(raiz_r, quiet = TRUE)
  renv::install(pacotes, project = raiz_r, prompt = FALSE)
  writeLines(paste0("library(", pacotes, ")"), file.path(raiz_r, "dependencias.R"))   # renv.lock lista estes pacotes
  renv::snapshot(project = raiz_r, prompt = FALSE, type = "implicit")
}
cat("Ambiente R pronto em", file.path(raiz_r, "renv"), "\n")

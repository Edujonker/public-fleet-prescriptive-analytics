#!/usr/bin/env python3
"""
Propaga os resultados oficiais das hipóteses (scripts/hipoteses_oficiais.py) para os
documentos-fonte do projeto.

1. Substitui números antigos que identificam de forma única os resultados substituídos
   (lista SUBSTITUICOES), apenas em arquivos de texto/fonte de documentos.
2. Lista as frases que ainda descrevem decisões antigas e precisam de reescrita manual
   (ex.: "H2 ... parcialmente", "MILP-0", "valor incremental do ML").

Arquivos registrados como históricos (versões já submetidas) não são alterados.
Uso:
  .venv/bin/python scripts/propagar_hipoteses.py            # simulação (não grava)
  .venv/bin/python scripts/propagar_hipoteses.py --aplicar  # grava e faz cópia .bak_hipoteses
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hipoteses_oficiais import SUBSTITUICOES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ALVOS = ["README.md", "projeto_dissertacao/README.md", "relatorios", "overleaf_dissertacao_udesc", "SBC", "SIC",
         "scripts", "src/ai_assistant.py", "docs/relatorio_geral.md"]
EXT = {".md", ".tex", ".html", ".py"}
# Versões já submetidas: preservadas como registro histórico.
HISTORICOS = {"SIC/Resumo_Expandido_36_SIC_2026_SIGAA.tex", "SIC/Resumo_Expandido_36_SIC_2026_SIGAA.md",
              "SIC/Resumo_Expandido_34_SIC_UDESC.md", "SIC/Resumo_Expandido_34_SIC_UDESC.tex",
              "SIC/Campos_Submissao_SIGAA_36_SIC_2026.json"}
NAO_TOCAR = {"scripts/hipoteses_oficiais.py", "scripts/propagar_hipoteses.py", "scripts/gerar_relatorio_figuras_memoria_calculo.py",
             "scripts/gerar_blocos_hipoteses.py", "overleaf_dissertacao_udesc/Textuais/Bloco_Hipoteses.tex",
             "overleaf_dissertacao_udesc/PosTextuais/ApendiceD.tex"}
SEMANTICOS = [
    (r"H2[^\n.]{0,120}PARCIAL", "H2 descrita como parcialmente sustentada (agora: não sustentada)"),
    (r"H1[^\n.]{0,120}N[ÃA]O SUSTENTADA|H1[^\n.]{0,80}não (foi )?sustentada|H1 (foi )?refutada", "H1 descrita como não sustentada (agora: parcialmente)"),
    (r"MILP-0|valor incremental do ML|4\.881\.378|48\.719\.011|52,48%", "MILP-0 / valor incremental do ML (não existe mais)"),
    (r"8,32%|R\$ 4,42|Monte Carlo[^\n]{0,60}40[,.]1", "números derivados do MILP antigo"),
    (r"95,26%", "disponibilidade 95,26% (era constante no script 08)"),
    (r"0,8743|0,8268", "ROC antigos da etapa 04 (atual: HistGB 0,8737; logística 0,8292)"),
]


def arquivos():
    for a in ALVOS:
        p = ROOT / a
        it = [p] if p.is_file() else (f for f in p.rglob("*") if f.is_file())
        for f in it:
            r = str(f.relative_to(ROOT))
            if f.suffix in EXT and "arquivados" not in r and ".bak" not in r and r not in HISTORICOS and r not in NAO_TOCAR:
                yield f, r


def main(aplicar: bool):
    total, mudados, pend = 0, 0, {}
    for f, r in arquivos():
        s = f.read_text(encoding="utf-8", errors="ignore")
        n_arq, novo = 0, s
        pares = list(SUBSTITUICOES)
        if f.suffix == ".tex":
            esc = lambda t: t.replace("%", "\\%").replace("R$", "R\\$")
            pares = [(esc(x), esc(y)) for x, y in SUBSTITUICOES] + pares
        for a, b in pares:
            c = novo.count(a)
            if c:
                novo = novo.replace(a, b); n_arq += c
        if n_arq:
            total += n_arq; mudados += 1
            print(f"{n_arq:4d}  {r}")
            if aplicar:
                shutil.copy2(f, f.with_name(f.name + ".bak_hipoteses"))
                f.write_text(novo, encoding="utf-8")
        for rx, desc in SEMANTICOS:
            for m in re.finditer(rx, novo, re.I):
                linha = novo.count("\n", 0, m.start()) + 1
                pend.setdefault(r, []).append((linha, desc))
    print(f"\n{'Aplicado' if aplicar else 'Simulação'}: {total} substituições em {mudados} arquivos.")
    print(f"Frases para reescrita manual: {sum(len(v) for v in pend.values())} em {len(pend)} arquivos")
    for r, l in sorted(pend.items(), key=lambda x: -len(x[1])):
        print(f"  {len(l):3d} {r}: " + "; ".join(sorted({d for _, d in l}))[:160])
    print("Preservados como históricos:", ", ".join(sorted(HISTORICOS)))


if __name__ == "__main__":
    main("--aplicar" in sys.argv)

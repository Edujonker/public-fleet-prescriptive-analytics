#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lista dos estudos que passaram na triagem mas não têm texto completo de acesso aberto.

Gera:
  revisao_sistematica/textos_para_baixar_CAFe.html   página para abrir no navegador
  revisao_sistematica/textos_para_baixar_CAFe.csv    mesma lista, para acompanhar no Excel

Uso individual, dentro dos termos do Portal CAPES: você abre cada link logado pelo
CAFe (UDESC), lê o artigo e, se for o caso, salva o PDF em
  revisao_sistematica/textos_completos/PDF_manual_CAFe/
Qualquer nome de arquivo serve; o nome sugerido evita ambiguidade. Na próxima
execução, scripts/rsl_prisma.py reconhece o arquivo (pelo nome, pelo DOI impresso
no PDF ou pelo título) e o leva para a etapa de elegibilidade.

Execute depois de scripts/rsl_prisma.py:
  python3 scripts/gerar_lista_cafe.py
"""

import csv
import html
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import rsl_prisma as rsl  # noqa: E402

ENTRADA = rsl.DADOS / "06_07_texto_completo_elegibilidade.csv"
SAIDA_HTML = rsl.BASE / "textos_para_baixar_CAFe.html"
SAIDA_CSV = rsl.BASE / "textos_para_baixar_CAFe.csv"
ORDEM_GRUPO = {"bases": 0, "outros": 1, "snowballing": 2}
NOME_GRUPO = {"bases": "Bases de dados (Scopus, IEEE Xplore…)", "outros": "Outros métodos (bibliotecas e buscas exploratórias)",
              "snowballing": "Snowballing (referências e citações dos incluídos)"}


def main():
    if not ENTRADA.exists():
        print("Rode antes: python3 scripts/rsl_prisma.py")
        return 1
    linhas = list(csv.DictReader(open(ENTRADA, encoding="utf-8-sig"), delimiter=";"))
    alvo = [l for l in linhas if l["recuperacao"].startswith("não recuperado")]
    for l in alvo:
        motivo = l["recuperacao"].split("(", 1)[-1].rstrip(")")
        if motivo.startswith("há versão aberta"):
            motivo = "há versão aberta, mas o download automático falhou"
        l["motivo"] = motivo
        l["arquivo_sugerido"] = rsl.doi_para_arquivo(l["doi"]) if l["doi"] else ""
        l["ja_salvo"] = "sim" if rsl.achar_pdf_manual({"doi": l["doi"], "titulo": l["titulo"]}) else ""
        l["link"] = f"https://doi.org/{l['doi']}" if l["doi"] else ""
    alvo.sort(key=lambda l: (ORDEM_GRUPO.get(l["grupo"], 3), -(int(l["ano"]) if l["ano"].isdigit() else 0), l["titulo"]))

    cols = ["grupo", "ano", "titulo", "veiculo", "doi", "link", "motivo", "arquivo_sugerido", "ja_salvo", "id"]
    with open(SAIDA_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(alvo)

    salvos = sum(1 for l in alvo if l["ja_salvo"])
    por_grupo = Counter(l["grupo"] for l in alvo)
    esc = html.escape
    blocos = []
    for g in sorted(por_grupo, key=lambda g: ORDEM_GRUPO.get(g, 3)):
        itens = [l for l in alvo if l["grupo"] == g]
        linhas_html = []
        for n, l in enumerate(itens, 1):
            link = (f'<a href="{esc(l["link"])}" target="_blank" rel="noopener">{esc(l["doi"])}</a>'
                    if l["link"] else "<em>sem DOI — buscar pelo título</em>")
            linhas_html.append(
                f'<tr class="{"ok" if l["ja_salvo"] else ""}"><td>{n}</td><td>{esc(l["ano"])}</td>'
                f'<td>{esc(l["titulo"])}<div class="veic">{esc(l.get("veiculo", ""))}</div></td>'
                f'<td>{link}</td><td><code>{esc(l["arquivo_sugerido"])}</code></td>'
                f'<td>{esc(l["motivo"])}</td><td>{"✓ salvo" if l["ja_salvo"] else ""}</td></tr>')
        blocos.append(
            f'<h2>{esc(NOME_GRUPO.get(g, g))} — {len(itens)}</h2>'
            '<table><thead><tr><th>#</th><th>Ano</th><th>Título / veículo</th><th>DOI</th>'
            '<th>Salvar como</th><th>Motivo</th><th>Situação</th></tr></thead><tbody>'
            + "".join(linhas_html) + "</tbody></table>")

    pasta = rsl.TEXTOS_MANUAL
    pagina = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Textos completos para baixar via CAFe</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;margin:24px;color:#222;max-width:1400px}}
h1{{color:#1b3a6e;margin-bottom:4px}} h2{{color:#005b2e;margin-top:32px}}
.box{{background:#f4f6fb;border-left:4px solid #1b3a6e;padding:10px 16px;margin:12px 0}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th{{background:#1b3a6e;color:#fff;text-align:left;padding:6px;position:sticky;top:0}}
td{{border-bottom:1px solid #dde3ef;padding:6px;vertical-align:top}}
tr.ok td{{background:#e8f5ec}} .veic{{color:#666;font-size:12px}} code{{font-size:11px}}
input{{padding:6px;width:340px;margin:8px 0}}
</style></head><body>
<h1>Textos completos para baixar via CAFe</h1>
<p>Gerado em {date.today():%d/%m/%Y}. {len(alvo)} estudos passaram na triagem e não têm texto
completo de acesso aberto ({salvos} já salvos).</p>
<div class="box">
<b>Como usar (uso individual, dentro dos termos do Portal CAPES)</b><ol>
<li>No navegador, entre no Portal de Periódicos CAPES pelo <b>Acesso CAFe → UDESC</b>.</li>
<li>Abra o link do DOI. Se a editora pedir acesso, use <i>Access through your institution</i> /
<i>Login via institution</i> e escolha CAFe/UDESC.</li>
<li>Salve o PDF em <code>{esc(str(pasta))}</code>, de preferência com o nome da coluna “Salvar como”.</li>
<li>Rode <code>python3 scripts/rsl_prisma.py</code> e depois este script de novo. Os salvos ficam verdes.</li>
</ol>Se o artigo não estiver no acervo assinado, deixe sem salvar: ele segue registrado como
“texto completo não recuperado” (protocolo, CO5), separado das exclusões por conteúdo.</div>
<input id="f" placeholder="Filtrar por título, ano ou DOI…" oninput="
for(const tr of document.querySelectorAll('tbody tr'))tr.style.display=tr.textContent.toLowerCase().includes(this.value.toLowerCase())?'':'none'">
{''.join(blocos)}
</body></html>"""
    SAIDA_HTML.write_text(pagina, encoding="utf-8")
    print(f"{len(alvo)} estudos sem texto aberto ({salvos} já salvos) — {dict(por_grupo)}")
    print(f"Página: {SAIDA_HTML}")
    print(f"CSV:    {SAIDA_CSV}")
    print(f"Salvar PDFs em: {pasta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

/* Biblio-now · interface · Eduardo Lopes Jonker
   JavaScript puro, sem bibliotecas externas. Compatível com a CSP do servidor:
   nada de scripts ou estilos inline; larguras dinâmicas são definidas via element.style. */
"use strict";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = (v) => (v === null || v === undefined || v === "" ? "—" : Number(v).toLocaleString("pt-BR"));
const dataHora = (iso) => {
  if (!iso) return "—";
  const d = new Date(iso);
  return isNaN(d) ? esc(iso) : d.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
};
const ANO = new Date().getFullYear();
const ATIVOS = ["na fila", "buscando", "baixando"];

const estadoApp = { aba: "painel", buscas: [], detalhe: null, estado: null, diasSemana: [], acervoPagina: 1, sessaoPerdida: false };

/* ------------------------------------------------------------ comunicação com o servidor */
async function api(metodo, url, corpo) {
  const op = { method: metodo, credentials: "same-origin", headers: { "X-BiblioNow": "1" } };
  if (corpo !== undefined) {
    op.headers["Content-Type"] = "application/json";
    op.body = JSON.stringify(corpo);
  }
  const r = await fetch(url, op);
  if (r.status === 401) {
    if (!estadoApp.sessaoPerdida) {
      estadoApp.sessaoPerdida = true;
      aviso("Sessão expirada: abra o Biblio-now de novo pelo arquivo ABRIR_BIBLIO_NOW.html.", true, 15000);
    }
    throw new Error("sessão inválida");
  }
  const tipo = r.headers.get("content-type") || "";
  const dados = tipo.includes("json") ? await r.json() : await r.text();
  if (!r.ok) {
    let msg = dados && dados.detail !== undefined ? dados.detail : dados;
    if (Array.isArray(msg)) msg = msg.map((e) => `${(e.loc || []).slice(1).join(".")}: ${e.msg}`).join("; ");
    throw new Error(typeof msg === "string" ? msg : `erro ${r.status}`);
  }
  return dados;
}

let tempoAviso;
function aviso(msg, erro = false, ms = 4000) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.toggle("erro", erro);
  t.classList.add("visivel");
  clearTimeout(tempoAviso);
  tempoAviso = setTimeout(() => t.classList.remove("visivel"), ms);
}

function selo(estado) {
  const cls = { "concluída": "concluida", "na fila": "fila", buscando: "buscando", baixando: "baixando", erro: "erro",
                cancelada: "cancelada", interrompida: "interrompida" }[estado] || "";
  return `<span class="selo ${cls}">${esc(estado)}</span>`;
}

function tabela(cab, linhas, classeLinha = "") {
  return `<div class="tabela-envelope"><table><thead><tr>${cab.map((c) => `<th${c.startsWith("#") ? ' class="num"' : ""}>${esc(c.replace(/^#/, ""))}</th>`).join("")}</tr></thead>
    <tbody>${linhas.map((l) => `<tr class="${classeLinha}"${l.id ? ` data-id="${esc(l.id)}"` : ""}>${l.celulas.join("")}</tr>`).join("")}</tbody></table></div>`;
}

/* ------------------------------------------------------------ abas */
function irPara(aba, empurrar = true) {
  if (!document.getElementById(aba)) aba = "painel";
  estadoApp.aba = aba;
  $$(".aba").forEach((b) => {
    const ativa = b.dataset.aba === aba;
    b.classList.toggle("ativa", ativa);
    b.setAttribute("aria-selected", ativa);
  });
  $$(".secao").forEach((s) => s.classList.toggle("ativa", s.id === aba));
  if (empurrar && location.hash !== `#${aba}`) history.replaceState(null, "", `#${aba}`);
  carregarAba(aba);
}

function carregarAba(aba) {
  const f = { painel: atualizarPainel, buscas: atualizarBuscas, acervo: () => carregarAcervo(true), agenda: carregarAgenda,
              validacao: prepararValidacao, config: carregarConfig }[aba];
  if (f) f().catch((e) => e.message !== "sessão inválida" && aviso(e.message, true));
}

document.addEventListener("click", (e) => {
  const aba = e.target.closest(".aba");
  if (aba) return irPara(aba.dataset.aba);
  const ir = e.target.closest("[data-ir]");
  if (ir) {
    e.preventDefault();
    irPara(ir.dataset.ir);
  }
});

/* ------------------------------------------------------------ painel */
async function lerEstado() {
  estadoApp.estado = await api("GET", "/api/estado");
  $("#versao").textContent = estadoApp.estado.versao;
  return estadoApp.estado;
}

function blocoAtiva(a) {
  if (!a) return '<div class="vazio">Nenhuma busca em andamento.</div>';
  return `<p><b>${esc(a.rotulo || a.id)}</b> ${selo(a.estado)}</p>${barraProgresso(a)}${numeros(a)}
    <div class="links"><button class="botao secundario mini" data-abrir="${esc(a.id)}">Ver detalhes</button></div>`;
}

function barraProgresso(b) {
  if (b.estado === "buscando" || b.estado === "na fila") return '<div class="barra indef"><div></div></div>';
  if (b.estado !== "baixando") return "";
  const feito = (b.baixados || 0) + (b.falharam || 0);
  const pct = b.a_tentar ? Math.min(100, Math.round((100 * feito) / b.a_tentar)) : 100;
  return `<div class="barra"><div data-largura="${pct}"></div></div><div class="ajuda">${num(feito)} de ${num(b.a_tentar)} PDFs tentados (${pct}%)</div>`;
}

function aplicarLarguras(raiz = document) {
  $$("[data-largura]", raiz).forEach((d) => (d.style.width = `${d.dataset.largura}%`));
}

function numeros(b) {
  return `<div class="numeros">
    <span>Registros: <b>${num(b.registros)}</b></span><span>Atendem: <b>${num(b.atendem)}</b></span>
    <span>Baixados: <b>${num(b.baixados)}</b></span><span>Já no acervo: <b>${num(b.ja_existiam)}</b></span>
    <span>Sem PDF aberto: <b>${num(b.sem_pdf)}</b></span><span>Falharam: <b>${num(b.falharam)}</b></span></div>`;
}

async function atualizarPainel() {
  const [s, buscas] = await Promise.all([lerEstado(), api("GET", "/api/buscas")]);
  estadoApp.buscas = buscas;
  const kpis = [["Obras no acervo", s.obras], ["PDFs", s.pdfs], ["Buscas realizadas", s.buscas],
                ["Agendamentos ativos", s.agendamentos], ["Na fila", s.na_fila]];
  $("#kpis").innerHTML = kpis.map(([l, v]) => `<div class="kpi"><div class="valor">${num(v)}</div><div class="legenda">${esc(l)}</div></div>`).join("");
  const ativa = $("#ativa");
  ativa.classList.toggle("vazio", !s.ativa);
  ativa.innerHTML = blocoAtiva(s.ativa);
  aplicarLarguras(ativa);
  const ult = $("#ultimas");
  ult.classList.toggle("vazio", !buscas.length);
  ult.innerHTML = buscas.length
    ? tabela(["Busca", "Início", "Estado", "#Baixados"], buscas.slice(0, 6).map((b) => ({
        id: b.id, celulas: [`<td class="titulo">${esc(b.rotulo || b.id)}</td>`, `<td>${dataHora(b.inicio)}</td>`,
                            `<td>${selo(b.estado)}</td>`, `<td class="num">${num(b.baixados)}</td>`] })), "clicavel")
    : "Nenhuma busca ainda.";
  $("#aviso-chaves").hidden = Boolean(s.chaves.OPENALEX_API_KEY && s.chaves.S2_API_KEY);
}

document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-abrir]");
  const linha = e.target.closest("#ultimas tr[data-id], #lista-buscas tr[data-id]");
  const id = b ? b.dataset.abrir : linha ? linha.dataset.id : null;
  if (id) {
    irPara("buscas");
    abrirDetalhe(id);
  }
});

/* ------------------------------------------------------------ nova busca */
function termosDe(texto) {
  return texto.split(/[\n,;]+/).map((t) => t.trim()).filter(Boolean);
}

function adicionarBloco(termos = []) {
  const n = $$("#blocos .bloco").length;
  if (n >= 8) return aviso("No máximo 8 blocos.", true);
  const d = document.createElement("div");
  d.className = "bloco";
  d.innerHTML = `<div class="bloco-topo"><b>Bloco ${n + 1}</b><button type="button" class="icone" title="Remover bloco" aria-label="Remover bloco">✕</button></div>
    <textarea rows="2" placeholder="${n === 0 ? "explainable AI, XAI, interpretable machine learning" : "public sector, government, public administration"}"></textarea>`;
  $("textarea", d).value = termos.join("\n");
  $("#blocos").appendChild(d);
  renumerarBlocos();
}

function renumerarBlocos() {
  $$("#blocos .bloco").forEach((b, i) => ($("b", b).textContent = i > 0 ? `Bloco ${i + 1} · E` : "Bloco 1"));
  const n = Math.max(1, $$("#blocos .bloco").length);
  const sel = $("#minimo");
  const atual = Number(sel.value) || n;
  sel.innerHTML = Array.from({ length: n }, (_, i) => `<option value="${i + 1}">${i + 1} de ${n}${i + 1 === n ? " (todos)" : ""}</option>`).join("");
  sel.value = String(sel.dataset.mexido ? Math.min(atual, n) : n);
  atualizarPrevia();
}

function lerBlocos() {
  return $$("#blocos textarea").map((t) => termosDe(t.value)).filter((b) => b.length);
}

function atualizarPrevia() {
  const blocos = lerBlocos();
  const min = Number($("#minimo").value) || blocos.length;
  let q = "";
  if (blocos.length) {
    const partes = blocos.map((b) => "(" + b.map((t) => `"${t}"`).join(" OR ") + ")");
    q = min >= blocos.length ? partes.join(" AND ") : "(" + blocos.flat().map((t) => `"${t}"`).join(" OR ") + ")" +
        `  → depois: ao menos ${min} de ${blocos.length} blocos no título/resumo`;
  }
  $("#previa").textContent = q || "(digite os termos)";
}

function intervaloPeriodo() {
  const p = $("#periodo").value;
  if (["1", "5", "10"].includes(p)) return [ANO - Number(p) + 1, null];
  if (p === "personalizado") return [Number($("#ano_min").value) || null, Number($("#ano_max").value) || null];
  return [null, null];
}

function atualizarPeriodo() {
  const p = $("#periodo").value;
  $$(".campo.anos").forEach((c) => (c.hidden = p !== "personalizado"));
  const [a, b] = intervaloPeriodo();
  $("#periodo-ajuda").textContent = p === "todos" ? "Sem filtro de ano."
    : p === "personalizado" ? `Artigos de ${a || "…"} a ${b || "…"}.`
    : `Artigos publicados a partir de ${a}. Nos agendamentos o período é recalculado a cada execução.`;
}

function lerFormulario() {
  const fontes = [];
  if ($("#f_openalex").checked) fontes.push("openalex");
  if ($("#f_s2").checked) fontes.push("s2");
  const p = $("#periodo").value;
  return {
    rotulo: $("#rotulo").value.trim(), blocos: lerBlocos(), minimo_blocos: Number($("#minimo").value) || null, fontes, periodo: p,
    ano_min: p === "personalizado" ? Number($("#ano_min").value) || null : null,
    ano_max: p === "personalizado" ? Number($("#ano_max").value) || null : null,
    ordem: $("#ordem").value, max_resultados: Number($("#max_resultados").value) || 1000,
    max_pdfs: Number($("#max_pdfs").value) || 0, paralelo: Number($("#paralelo").value) || 6,
    baixar_parciais: $("#parciais").checked, exata: $("#exata").checked,
  };
}

function conferirFormulario(f) {
  if (!f.blocos.length) return "Informe ao menos um termo.";
  if (!f.fontes.length) return "Escolha ao menos uma fonte.";
  const ruim = f.blocos.flat().find((t) => /["\\<>]/.test(t) || t.length > 120);
  if (ruim) return `Termo inválido: "${ruim.slice(0, 40)}" (sem aspas, barras ou < >; até 120 caracteres).`;
  if (f.blocos.some((b) => b.length > 30)) return "No máximo 30 termos por bloco.";
  if (f.periodo === "personalizado" && f.ano_min && f.ano_max && f.ano_min > f.ano_max) return "O ano inicial é maior que o final.";
  return "";
}

$("#add-bloco").addEventListener("click", () => adicionarBloco());
$("#blocos").addEventListener("input", atualizarPrevia);
$("#blocos").addEventListener("click", (e) => {
  if (!e.target.closest(".icone")) return;
  if ($$("#blocos .bloco").length === 1) return aviso("A busca precisa de ao menos um bloco.", true);
  e.target.closest(".bloco").remove();
  renumerarBlocos();
});
$("#minimo").addEventListener("change", (e) => { e.target.dataset.mexido = "1"; atualizarPrevia(); });
["#periodo", "#ano_min", "#ano_max"].forEach((s) => $(s).addEventListener("input", atualizarPeriodo));

$("#form-busca").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = lerFormulario();
  const erro = conferirFormulario(f);
  $("#erro-busca").textContent = erro;
  if (erro) return;
  const botao = $("#form-busca button[type=submit]");
  botao.disabled = true;
  try {
    const r = await api("POST", "/api/buscas", f);
    aviso(`Busca "${r.rotulo || r.id}" enviada.`);
    irPara("buscas");
    abrirDetalhe(r.id);
  } catch (err) {
    $("#erro-busca").textContent = err.message;
  } finally {
    botao.disabled = false;
  }
});

/* ------------------------------------------------------------ buscas */
async function atualizarBuscas() {
  estadoApp.buscas = await api("GET", "/api/buscas");
  const el = $("#lista-buscas");
  const b = estadoApp.buscas;
  el.classList.toggle("vazio", !b.length);
  el.innerHTML = b.length
    ? tabela(["Busca", "Origem", "Início", "Estado", "#Registros", "#Atendem", "#Baixados", "#Já no acervo"], b.map((x) => ({
        id: x.id, celulas: [`<td class="titulo">${esc(x.rotulo || x.id)}<div class="sub">${esc(x.id)}</div></td>`,
          `<td>${esc(x.origem)}</td>`, `<td>${dataHora(x.inicio)}</td>`, `<td>${selo(x.estado)}</td>`,
          `<td class="num">${num(x.registros)}</td>`, `<td class="num">${num(x.atendem)}</td>`,
          `<td class="num">${num(x.baixados)}</td>`, `<td class="num">${num(x.ja_existiam)}</td>`] })), "clicavel")
    : "Nenhuma busca ainda. Crie uma em Nova busca.";
  if (estadoApp.detalhe) await abrirDetalhe(estadoApp.detalhe, false);
}

const ARQS = [["resultados.csv", "Resultados (.csv)"], ["referencias.bib", "Referências (.bib)"], ["consulta.txt", "Consulta (.txt)"], ["log.txt", "Log"]];

async function abrirDetalhe(id, rolar = true) {
  estadoApp.detalhe = id;
  const d = await api("GET", `/api/buscas/${encodeURIComponent(id)}`);
  const el = $("#detalhe");
  const ativo = ATIVOS.includes(d.estado);
  const p = d.parametros || {};
  const bases = Object.entries(d.totais_bases || {}).map(([k, v]) => `${esc(k)}: <b>${esc(typeof v === "number" ? num(v) : v)}</b>`).join(" · ");
  const logAnterior = $(".log", el);
  const noFim = !logAnterior || logAnterior.scrollTop + logAnterior.clientHeight >= logAnterior.scrollHeight - 20;
  el.hidden = false;
  el.innerHTML = `<div class="rotulo-linha"><h2>${esc(d.rotulo || d.id)} ${selo(d.estado)}</h2>
      <div class="acoes">${ativo ? `<button class="botao perigo mini" id="cancelar-busca">Cancelar</button>` : ""}
      <button class="botao secundario mini" id="fechar-detalhe">Fechar</button></div></div>
    <p class="ajuda">${esc(d.origem)} · início ${dataHora(d.inicio)}${d.fim ? ` · fim ${dataHora(d.fim)}` : ""} ·
      período: ${esc(p.periodo === "todos" || !p.periodo ? "todos os anos" : p.periodo === "personalizado" ? `${p.ano_min || "…"}–${p.ano_max || "…"}` : `últimos ${p.periodo} ano(s)`)}
      · mínimo de blocos: ${esc(d.minimo_blocos)} de ${esc((d.blocos || []).length)}</p>
    <p class="ajuda">${(d.blocos || []).map((b) => "(" + b.map(esc).join(" OU ") + ")").join(" E ")}</p>
    ${bases ? `<p class="ajuda">Correspondências nas bases: ${bases}</p>` : ""}
    ${barraProgresso(d)}${numeros(d)}
    ${d.erro ? `<p class="erro">${esc(d.erro)}</p>` : ""}
    <div class="links">${ARQS.map(([n, r]) => `<a class="botao secundario mini" href="/api/buscas/${encodeURIComponent(d.id)}/arquivos/${n}">${r}</a>`).join("")}
      ${ativo ? "" : `<a class="botao mini" href="/api/buscas/${encodeURIComponent(d.id)}/zip">Baixar obras (.zip)</a>
      <button class="botao secundario mini" id="ver-registros">Ver registros</button>`}</div>
    <div class="log">${esc((d.log || []).join("\n")) || "(sem mensagens)"}</div>
    <div id="registros-busca"></div>`;
  aplicarLarguras(el);
  const log = $(".log", el);
  if (noFim) log.scrollTop = log.scrollHeight;
  if (rolar) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

$("#detalhe").addEventListener("click", async (e) => {
  const id = estadoApp.detalhe;
  if (e.target.id === "fechar-detalhe") {
    estadoApp.detalhe = null;
    $("#detalhe").hidden = true;
  } else if (e.target.id === "cancelar-busca") {
    if (!confirm("Cancelar esta busca? Os PDFs já baixados ficam no acervo.")) return;
    await api("POST", `/api/buscas/${encodeURIComponent(id)}/cancelar`).catch((x) => aviso(x.message, true));
    aviso("Cancelamento pedido; a busca para após os downloads em curso.");
    abrirDetalhe(id, false);
  } else if (e.target.id === "ver-registros") {
    e.target.disabled = true;
    try {
      const regs = await api("GET", `/api/buscas/${encodeURIComponent(id)}/registros?limite=2000`);
      $("#registros-busca").innerHTML = `<h2>Registros (${num(regs.length)})</h2>` + tabela(["Título", "Ano", "Fonte", "Verificação", "PDF"],
        regs.map((r) => ({ celulas: [`<td class="titulo">${r.doi ? `<a href="https://doi.org/${esc(r.doi)}" target="_blank" rel="noopener noreferrer">${esc(r.titulo)}</a>` : esc(r.titulo)}<div class="sub">${esc(r.autores)}${r.veiculo ? " · " + esc(r.veiculo) : ""}</div></td>`,
          `<td>${esc(r.ano)}</td>`, `<td>${esc(r.fonte)}</td>`, `<td>${esc(r.verificacao_semantica)}</td>`, `<td>${esc(r.status_pdf)}</td>`] })));
    } catch (x) {
      aviso(x.message, true);
      e.target.disabled = false;
    }
  }
});

/* ------------------------------------------------------------ acervo */
let tempoFiltro;
$("#filtro-acervo").addEventListener("input", () => {
  clearTimeout(tempoFiltro);
  tempoFiltro = setTimeout(() => carregarAcervo(true), 300);
});

async function carregarAcervo(reiniciar = false) {
  if (reiniciar) estadoApp.acervoPagina = 1;
  const q = encodeURIComponent($("#filtro-acervo").value.trim());
  const r = await api("GET", `/api/obras?q=${q}&limite=200&pagina=${estadoApp.acervoPagina}`);
  const el = $("#lista-acervo");
  const linhas = r.itens.map((o) => {
    const id = encodeURIComponent(o.id);
    const autores = (o.autores || []).slice(0, 4).join("; ") + ((o.autores || []).length > 4 ? " et al." : "");
    return { celulas: [
      `<td class="titulo"><b>${esc(o.titulo || o.id)}</b><div class="sub">${esc(autores)}</div></td>`,
      `<td>${esc(o.ano)}</td>`, `<td>${esc(o.veiculo)}</td>`,
      `<td>${o.doi ? `<a href="https://doi.org/${esc(o.doi)}" target="_blank" rel="noopener noreferrer">${esc(o.doi)}</a>` : "—"}</td>`,
      `<td>${dataHora(o.incorporada_em)}<div class="sub">${esc(o.busca_origem_nome)}</div></td>`,
      `<td class="links"><a class="botao mini" href="/api/obras/${id}/pdf" target="_blank" rel="noopener">PDF</a>
        <a class="botao secundario mini" href="/api/obras/${id}/txt" target="_blank" rel="noopener" title="${o.txt_extraido ? num(o.palavras_txt) + " palavras" : "PDF sem texto extraível"}">TXT</a>
        <a class="botao secundario mini" href="/api/obras/${id}/bib">BIB</a></td>`] };
  });
  const cab = `<p class="ajuda">${num(r.total)} obra(s)${$("#filtro-acervo").value.trim() ? " com o filtro" : ""}.</p>`;
  const tab = tabela(["Obra", "Ano", "Veículo", "DOI", "Incorporada em", "Arquivos"], linhas);
  if (reiniciar || !$("table", el)) {
    el.classList.toggle("vazio", !r.total);
    el.innerHTML = r.total ? cab + tab : "O acervo está vazio. As obras aparecem aqui ao fim de cada busca.";
  } else {
    $("tbody", el).insertAdjacentHTML("beforeend", $("tbody", new DOMParser().parseFromString(`<table>${tab.match(/<tbody>[\s\S]*<\/tbody>/)[0]}</table>`, "text/html")).innerHTML);
  }
  $("#mais-acervo")?.remove();
  if (estadoApp.acervoPagina * 200 < r.total) {
    el.insertAdjacentHTML("beforeend", '<div class="links"><button class="botao secundario" id="mais-acervo">Carregar mais</button></div>');
    $("#mais-acervo").addEventListener("click", () => { estadoApp.acervoPagina += 1; carregarAcervo(false); });
  }
}

/* ------------------------------------------------------------ agendamentos */
const modal = $("#modal-agenda");

function atualizarModal() {
  const per = $("#ag_per").value;
  $("#campo-dia-sem").hidden = per !== "semanal";
  $("#campo-dia-mes").hidden = per !== "mensal";
  const h = $("#ag_hora").value || "08:00";
  const dia = estadoApp.diasSemana[Number($("#ag_dsem").value)] || "segunda";
  $("#ag_resumo").textContent = per === "diario" ? `Roda todos os dias às ${h}.`
    : per === "semanal" ? `Roda toda ${dia} às ${h}.`
    : `Roda todo dia ${$("#ag_dmes").value || 1} às ${h} (em meses mais curtos, no último dia).`;
}

$("#salvar-agenda").addEventListener("click", async () => {
  const f = lerFormulario();
  const erro = conferirFormulario(f);
  $("#erro-busca").textContent = erro;
  if (erro) return;
  if (!estadoApp.diasSemana.length) {
    const r = await api("GET", "/api/agendamentos").catch(() => ({ dias_semana: [] }));
    estadoApp.diasSemana = r.dias_semana;
  }
  $("#ag_dsem").innerHTML = estadoApp.diasSemana.map((d, i) => `<option value="${i}">${esc(d)}</option>`).join("");
  $("#ag_nome").value = f.rotulo || f.blocos.map((b) => b[0]).join(" + ").slice(0, 80);
  $("#erro-agenda").textContent = "";
  atualizarModal();
  modal.showModal();
});

["#ag_per", "#ag_hora", "#ag_dsem", "#ag_dmes"].forEach((s) => $(s).addEventListener("input", atualizarModal));

$("#form-agenda").addEventListener("submit", async (e) => {
  if (e.submitter && e.submitter.value === "cancelar") return;
  e.preventDefault();
  const corpo = { nome: $("#ag_nome").value.trim(), periodicidade: $("#ag_per").value, hora: $("#ag_hora").value,
                  dia_semana: Number($("#ag_dsem").value) || 0, dia_mes: Number($("#ag_dmes").value) || 1, ativo: true, busca: lerFormulario() };
  if (!corpo.nome) return ($("#erro-agenda").textContent = "Dê um nome ao agendamento.");
  try {
    const ag = await api("POST", "/api/agendamentos", corpo);
    modal.close();
    aviso(`Agendado: ${ag.descricao}. Próxima execução em ${dataHora(ag.proxima_execucao)}.`, false, 6000);
    irPara("agenda");
  } catch (x) {
    $("#erro-agenda").textContent = x.message;
  }
});

async function carregarAgenda() {
  const r = await api("GET", "/api/agendamentos");
  estadoApp.diasSemana = r.dias_semana;
  const el = $("#lista-agenda");
  el.classList.toggle("vazio", !r.itens.length);
  el.innerHTML = r.itens.length
    ? tabela(["Nome", "Quando", "Próxima execução", "Última execução", "Ativo", ""], r.itens.map((a) => ({
        id: a.id, celulas: [
          `<td class="titulo"><b>${esc(a.nome)}</b><div class="sub">${(a.busca.blocos || []).map((b) => "(" + b.map(esc).join(" OU ") + ")").join(" E ")}</div></td>`,
          `<td>${esc(a.descricao)}</td>`, `<td>${a.ativo ? dataHora(a.proxima_execucao) : "—"}</td>`,
          `<td>${a.ultima_busca ? `<a href="#" data-abrir="${esc(a.ultima_busca)}">${dataHora(a.ultima_execucao)}</a>` : "—"}</td>`,
          `<td><label class="check"><input type="checkbox" data-ativo="${esc(a.id)}"${a.ativo ? " checked" : ""}> ${a.ativo ? "sim" : "não"}</label></td>`,
          `<td class="links"><button class="botao secundario mini" data-executar="${esc(a.id)}">Executar agora</button>
            <button class="botao perigo mini" data-remover="${esc(a.id)}">Remover</button></td>`] })))
    : "Nenhum agendamento.";
}

$("#lista-agenda").addEventListener("click", async (e) => {
  const ex = e.target.closest("[data-executar]");
  const rm = e.target.closest("[data-remover]");
  try {
    if (ex) {
      ex.disabled = true;
      const r = await api("POST", `/api/agendamentos/${ex.dataset.executar}/executar`);
      aviso("Busca enviada para a fila.");
      irPara("buscas");
      abrirDetalhe(r.busca);
    } else if (rm) {
      if (!confirm("Remover este agendamento? As buscas já feitas continuam no acervo.")) return;
      await api("DELETE", `/api/agendamentos/${rm.dataset.remover}`);
      aviso("Agendamento removido.");
      carregarAgenda();
    }
  } catch (x) {
    aviso(x.message, true);
  }
});

$("#lista-agenda").addEventListener("change", async (e) => {
  const c = e.target.closest("[data-ativo]");
  if (!c) return;
  try {
    await api("PATCH", `/api/agendamentos/${c.dataset.ativo}`, { ativo: c.checked });
    aviso(c.checked ? "Agendamento ativado." : "Agendamento pausado.");
  } catch (x) {
    aviso(x.message, true);
  }
  carregarAgenda();
});

/* ------------------------------------------------------------ validação */
async function prepararValidacao() {
  const buscas = await api("GET", "/api/buscas");
  estadoApp.buscas = buscas;
  const sel = $("#val-busca");
  const atual = sel.value;
  const ok = buscas.filter((b) => !ATIVOS.includes(b.estado));
  sel.innerHTML = ok.length ? '<option value="">Escolha uma busca…</option>' + ok.map((b) => `<option value="${esc(b.id)}">${esc(b.rotulo || b.id)} · ${dataHora(b.inicio)}</option>`).join("")
                            : '<option value="">Nenhuma busca concluída</option>';
  if (atual && ok.some((b) => b.id === atual)) sel.value = atual;
}

$("#rodar-testes").addEventListener("click", async (e) => {
  e.target.disabled = true;
  const el = $("#resultado-testes");
  el.textContent = "Rodando…";
  try {
    const r = await api("POST", "/api/validacao/testes");
    const falhas = r.total - r.aprovados;
    el.classList.remove("vazio");
    el.innerHTML = `<p><span class="selo ${falhas ? "nao" : "sim"}">${r.aprovados} de ${r.total} aprovados</span>
        ${r.alertas ? `<span class="selo interrompida">${r.alertas} alerta(s)</span>` : ""} <span class="ajuda">em ${dataHora(r.quando)}</span></p>` +
      tabela(["Grupo", "Teste", "Resultado", "O que foi conferido"], r.testes.map((t) => ({ celulas: [
        `<td>${esc(t.grupo)}</td>`, `<td>${esc(t.nome)}</td>`,
        `<td>${t.ok ? (t.alerta ? '<span class="selo interrompida">alerta</span>' : '<span class="selo sim">ok</span>') : '<span class="selo nao">falhou</span>'}</td>`,
        `<td>${esc(t.detalhe)}</td>`] })));
  } catch (x) {
    el.textContent = x.message;
  } finally {
    e.target.disabled = false;
  }
});

$("#val-busca").addEventListener("change", async (e) => {
  const id = e.target.value;
  const el = $("#metricas");
  $("#resultado-ref").innerHTML = "";
  if (!id) {
    el.className = "vazio";
    el.textContent = "Escolha uma busca.";
    return;
  }
  try {
    const m = await api("GET", `/api/validacao/metricas/${encodeURIComponent(id)}`);
    el.className = "";
    const maxAno = Math.max(1, ...m.anos.map((a) => a.n));
    el.innerHTML = `<div class="cartoes">${m.indicadores.map((i) => `<div class="kpi"><div class="valor">${num(i.valor)}${i.pct !== undefined && i.pct !== null ? `<small> ${String(i.pct).replace(".", ",")}%</small>` : ""}</div>
        <div class="legenda">${esc(i.nome)}</div>${i.nota ? `<div class="sub">${esc(i.nota)}</div>` : ""}</div>`).join("")}</div>
      <div class="grade2"><div><h2>Situação dos PDFs</h2>${tabela(["Situação", "#Registros"], m.situacao_pdf.map((s) => ({ celulas: [`<td>${esc(s.situacao)}</td>`, `<td class="num">${num(s.n)}</td>`] })))}
        <h2 class="espaco">Registros por base</h2>${tabela(["Base", "#Registros"], Object.entries(m.fontes).map(([k, v]) => ({ celulas: [`<td>${esc(k)}</td>`, `<td class="num">${num(v)}</td>`] })))}</div>
      <div><h2>Registros por ano</h2>${m.anos.length ? `<div class="grafico">${m.anos.map((a) => `<div class="g-linha"><span>${a.ano}</span><div class="g-barra"><div data-largura="${Math.round((100 * a.n) / maxAno)}"></div></div><b>${num(a.n)}</b></div>`).join("")}</div>` : '<p class="vazio">Sem anos informados.</p>'}</div></div>`;
    aplicarLarguras(el);
  } catch (x) {
    el.textContent = x.message;
  }
});

$("#comparar").addEventListener("click", async () => {
  const id = $("#val-busca").value;
  const texto = $("#val-ref").value.trim();
  $("#erro-ref").textContent = !id ? "Escolha a busca em “Métricas de uma busca”." : !texto ? "Cole ao menos um DOI ou título." : "";
  if (!id || !texto) return;
  try {
    const r = await api("POST", `/api/validacao/referencia/${encodeURIComponent(id)}`, { texto });
    const pct = (v) => (v === null ? "—" : `${String(v).replace(".", ",")}%`);
    $("#resultado-ref").innerHTML = `<div class="cartoes">
        <div class="kpi"><div class="valor">${pct(r.revocacao_busca)}</div><div class="legenda">Revocação da busca (${r.encontrados} de ${r.referencias} encontrados)</div></div>
        <div class="kpi"><div class="valor">${pct(r.revocacao_acervo)}</div><div class="legenda">No acervo (${r.no_acervo} de ${r.referencias} com PDF)</div></div>
        <div class="kpi"><div class="valor">${num(r.faltantes.length)}</div><div class="legenda">Não encontrados</div></div></div>
      <p class="ajuda">${esc(r.nota)}</p>` + tabela(["Referência", "Tipo", "Encontrado", "PDF"], r.itens.map((i) => ({ celulas: [
        `<td class="titulo">${esc(i.referencia)}${i.titulo && i.tipo === "DOI" ? `<div class="sub">${esc(i.titulo)}</div>` : ""}</td>`, `<td>${esc(i.tipo)}</td>`,
        `<td>${i.encontrado ? '<span class="selo sim">sim</span>' : '<span class="selo nao">não</span>'}</td>`, `<td>${esc(i.situacao_pdf || "—")}</td>`] })));
  } catch (x) {
    $("#erro-ref").textContent = x.message;
  }
});

/* ------------------------------------------------------------ configurações */
async function carregarConfig() {
  const s = await lerEstado();
  const st = (id, ok) => {
    const e = $(id);
    e.textContent = ok ? "definida" : "não definida";
    e.className = `selo ${ok ? "sim" : "nao"}`;
  };
  st("#st_oa", s.chaves.OPENALEX_API_KEY);
  st("#st_s2", s.chaves.S2_API_KEY);
  st("#st_mail", s.chaves.OPENALEX_EMAIL || s.chaves.UNPAYWALL_EMAIL);
  $("#info-seguranca").textContent = `Sistema: ${s.seguranca.plataforma}. Chave mestra: ${s.seguranca.cofre}. Servidor aceito só em 127.0.0.1, ` +
    "com código de sessão, cookie HttpOnly/SameSite=Strict, proteção contra pedidos de outras páginas (CSRF), CSP restritiva e bloqueio de downloads para endereços internos.";
  $("#caminho-repo").textContent = `Pasta do repositório: ${s.repositorio}`;
}

$("#form-chaves").addEventListener("submit", async (e) => {
  e.preventDefault();
  const mail = $("#k_mail").value.trim();
  const corpo = { OPENALEX_API_KEY: $("#k_oa").value.trim(), S2_API_KEY: $("#k_s2").value.trim(), OPENALEX_EMAIL: mail, UNPAYWALL_EMAIL: mail };
  const msg = $("#msg-chaves");
  if (!Object.values(corpo).some(Boolean)) {
    msg.className = "erro";
    msg.textContent = "Nada para salvar.";
    return;
  }
  try {
    await api("POST", "/api/chaves", corpo);
    ["#k_oa", "#k_s2", "#k_mail"].forEach((s) => ($(s).value = ""));
    msg.className = "ok";
    msg.textContent = "Salvo no cofre criptografado.";
    carregarConfig();
  } catch (x) {
    msg.className = "erro";
    msg.textContent = x.message;
  }
});

/* ------------------------------------------------------------ atualização periódica */
let anteriorAtiva = null;
async function ciclo() {
  if (!estadoApp.sessaoPerdida && !document.hidden) {
    try {
      const s = await lerEstado();
      const idAtiva = s.ativa ? s.ativa.id : null;
      if (anteriorAtiva && anteriorAtiva !== idAtiva) {
        aviso("Busca concluída: fichamento e Protocolo Sigma atualizados.");
        if (estadoApp.aba === "acervo") carregarAcervo(true);
        if (estadoApp.aba === "validacao") prepararValidacao();
      }
      anteriorAtiva = idAtiva;
      if (estadoApp.aba === "painel") await atualizarPainel();
      else if (estadoApp.aba === "buscas" && (idAtiva || s.na_fila || (estadoApp.detalhe && ATIVOS.includes((estadoApp.buscas.find((b) => b.id === estadoApp.detalhe) || {}).estado)))) await atualizarBuscas();
    } catch (_) { /* aviso já mostrado em api() */ }
  }
  setTimeout(ciclo, anteriorAtiva ? 2000 : 6000);
}

/* ------------------------------------------------------------ início */
$("#ano").textContent = ANO;
adicionarBloco();
adicionarBloco();
atualizarPeriodo();
irPara((location.hash || "#painel").slice(1), false);
window.addEventListener("hashchange", () => irPara(location.hash.slice(1), false));
setTimeout(ciclo, 2000);

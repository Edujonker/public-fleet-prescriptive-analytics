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

const estadoApp = { aba: "painel", buscas: [], detalhe: null, estado: null, diasSemana: [], acervoPagina: 1, sessaoPerdida: false,
                    pesquisa: localStorage.getItem("biblionow.pesquisa") || "" };
const qp = () => `pesquisa=${encodeURIComponent(estadoApp.pesquisa || "Geral")}`;

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
  const s = (estadoApp.estado = await api("GET", "/api/estado"));
  $("#versao").textContent = s.versao;
  const nomes = s.pesquisas.map((p) => p.nome);
  if (!nomes.includes(estadoApp.pesquisa)) definirPesquisa(nomes[0] || "Geral", false);
  const sel = $("#pesquisa-atual");
  const opcoes = (nomes.length ? nomes : ["Geral"]).map((n) => `<option value="${esc(n)}">${esc(n)}</option>`).join("");
  if (sel.dataset.opcoes !== opcoes) {
    sel.innerHTML = opcoes;
    sel.dataset.opcoes = opcoes;
  }
  sel.value = estadoApp.pesquisa;
  atualizarIndicador(s.ativa);
  return s;
}

function pesquisaAtual() {
  return (estadoApp.estado?.pesquisas || []).find((p) => p.nome === estadoApp.pesquisa) || { nome: estadoApp.pesquisa, obras: 0, pdfs: 0, buscas: 0 };
}

function definirPesquisa(nome, recarregar = true) {
  estadoApp.pesquisa = nome;
  localStorage.setItem("biblionow.pesquisa", nome);
  $("#nome-pesquisa-busca").textContent = nome;
  $$('[data-link="fichamento"]').forEach((a) => (a.href = `/api/fichamento?${qp()}`));
  $$('[data-link="protocolo"]').forEach((a) => (a.href = `/api/protocolo?${qp()}`));
  if (recarregar) {
    estadoApp.detalhe = null;
    $("#detalhe").hidden = true;
    carregarAba(estadoApp.aba);
  }
}

function atualizarIndicador(a) {
  const el = $("#indicador");
  el.hidden = !a;
  if (!a) return;
  const feito = (a.baixados || 0) + (a.falharam || 0);
  const pct = a.estado === "baixando" && a.a_tentar ? Math.min(100, Math.round((100 * feito) / a.a_tentar)) : 0;
  el.dataset.id = a.id;
  el.innerHTML = `<span class="pulso"></span><span>Em segundo plano: <b>${esc(a.rotulo || a.id)}</b> (${esc(a.pesquisa)}) · ${esc(a.estado)}
    ${a.estado === "baixando" ? ` · ${num(feito)} de ${num(a.a_tentar)} PDFs` : ""}</span>
    ${a.estado === "baixando" ? `<span class="mini-barra"><div data-largura="${pct}"></div></span>` : ""}
    <span class="ajuda">Pode trocar de aba ou fechar o navegador: o download continua.</span>`;
  aplicarLarguras(el);
}

$("#indicador").addEventListener("click", () => {
  const id = $("#indicador").dataset.id;
  const a = estadoApp.estado?.ativa;
  if (!id || !a) return;
  if (a.pesquisa !== estadoApp.pesquisa) definirPesquisa(a.pesquisa, false);
  irPara("buscas");
  abrirDetalhe(id);
});

$("#pesquisa-atual").addEventListener("change", (e) => definirPesquisa(e.target.value));

$("#nova-pesquisa").addEventListener("click", () => {
  $("#pq_nome").value = "";
  $("#pq_desc").value = "";
  $("#erro-pesquisa").textContent = "";
  $("#modal-pesquisa").showModal();
});

$("#form-pesquisa").addEventListener("submit", async (e) => {
  if (e.submitter && e.submitter.value === "cancelar") return;
  e.preventDefault();
  try {
    const r = await api("POST", "/api/pesquisas", { nome: $("#pq_nome").value.trim(), descricao: $("#pq_desc").value.trim() });
    $("#modal-pesquisa").close();
    aviso(r.ja_existia ? `A pesquisa "${r.nome}" já existia; selecionada.` : `Pesquisa "${r.nome}" criada em ${r.pasta}`, false, 6000);
    definirPesquisa(r.nome, false);
    await lerEstado();
    irPara("nova");
  } catch (x) {
    $("#erro-pesquisa").textContent = x.message;
  }
});

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
  const s = await lerEstado();
  const buscas = await api("GET", `/api/buscas?${qp()}`);
  estadoApp.buscas = buscas;
  const pa = pesquisaAtual();
  const kpis = [["Obras nesta pesquisa", pa.obras], ["PDFs nesta pesquisa", pa.pdfs], ["Buscas nesta pesquisa", pa.buscas],
                ["Pesquisas", s.pesquisas.length], ["Agendamentos ativos", s.agendamentos], ["Na fila", s.na_fila]];
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
  carregarRelatorios().catch(() => {});
}

async function carregarRelatorios() {
  const el = $("#lista-relatorios");
  if (!pesquisaAtual().buscas) {
    el.className = "vazio";
    el.textContent = "Os relatórios aparecem aqui ao fim de cada busca.";
    $("#pasta-relatorios").textContent = "";
    return;
  }
  const r = await api("GET", `/api/relatorios?${qp()}`);
  $("#pasta-relatorios").textContent = r.pasta;
  el.className = r.itens.length ? "" : "vazio";
  if (!r.itens.length) return (el.textContent = "Os relatórios aparecem aqui ao fim de cada busca.");
  const kb = (b) => (b < 1024 ? `${b} B` : b < 1048576 ? `${Math.round(b / 1024)} KB` : `${(b / 1048576).toFixed(1).replace(".", ",")} MB`);
  el.innerHTML = tabela(["Arquivo", "Atualizado em", "#Tamanho"], r.itens.slice(-60).reverse().map((i) => ({ celulas: [
    `<td><a href="/api/relatorios/${i.caminho.split("/").map(encodeURIComponent).join("/")}?${qp()}" target="_blank" rel="noopener">${esc(i.caminho)}</a></td>`,
    `<td>${dataHora(i.alterado)}</td>`, `<td class="num">${kb(i.tamanho)}</td>`] })));
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
  $$("#blocos .bloco").forEach((b, i) => ($("b", b).textContent = i > 0 ? `Bloco ${i + 1} · ${Number($("#minimo").value) === $$("#blocos .bloco").length ? "E" : "OU"}` : "Bloco 1"));
  const n = Math.max(1, $$("#blocos .bloco").length);
  const sel = $("#minimo");
  const atual = Number(sel.value) || n;
  sel.innerHTML = Array.from({ length: n }, (_, i) => `<option value="${i + 1}">${i === 0 ? (n > 1 ? "OU · qualquer bloco (busca ampla)" : "1 bloco") : i + 1 === n ? `E · todos os ${n} blocos (busca restrita)` : `ao menos ${i + 1} de ${n} blocos`}</option>`).join("");
  sel.value = String(sel.dataset.mexido ? Math.min(atual, n) : 1);
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
        (min > 1 ? `  → depois: ao menos ${min} de ${blocos.length} blocos no título/resumo` : "");
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
    pesquisa: estadoApp.pesquisa || "Geral", rotulo: $("#rotulo").value.trim(), blocos: lerBlocos(), minimo_blocos: Number($("#minimo").value) || null, fontes, periodo: p,
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
$("#minimo").addEventListener("change", (e) => {
  e.target.dataset.mexido = "1";
  $$("#blocos .bloco").forEach((b, i) => i > 0 && ($("b", b).textContent = `Bloco ${i + 1} · ${Number(e.target.value) === $$("#blocos .bloco").length ? "E" : "OU"}`));
  atualizarPrevia();
});
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

function htmlDiagnostico(d) {
  if (!d || !d.blocos) return "";
  const cor = (n) => (n === 0 ? "nao" : n === null || n === undefined ? "" : n < 20 ? "interrompida" : "sim");
  const sel = (n) => `<span class="selo ${cor(n)}">${n === null || n === undefined ? "?" : num(n)}</span>`;
  return `<h2>Diagnóstico da consulta</h2><p class="ajuda">${esc(d.base)}. Quantos trabalhos existem para cada termo e bloco.</p>` +
    tabela(["Bloco", "Termos (trabalhos)", "Bloco inteiro (OU)"], d.blocos.map((b) => ({ celulas: [
      `<td>${b.bloco}</td>`, `<td>${b.termos.map((t) => `${esc(t.termo)} ${sel(t.trabalhos)}`).join("<br>")}</td>`, `<td>${sel(b.trabalhos)}</td>`] }))) +
    `<p><b>Esta busca enviará:</b> ${sel(d.combinacao)}${d.blocos.length > 1 ? ` · qualquer bloco (OU): ${sel(d.qualquer_termo)} · todos os blocos (E): ${sel(d.todos_os_blocos)}` : ""}</p>` +
    (d.sugestoes && d.sugestoes.length ? `<ul class="sugestoes">${d.sugestoes.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : '<p class="ok">A consulta encontra trabalhos.</p>');
}

/* sugestão de palavras-chave a partir do tema */
let ultimaSugestao = null;
$("#sugerir").addEventListener("click", async (e) => {
  const tema = $("#tema").value.trim();
  const el = $("#sugestoes");
  if (tema.length < 3) return aviso("Escreva o tema da pesquisa (pelo menos 3 caracteres).", true);
  el.hidden = false;
  el.innerHTML = '<p class="ajuda">Procurando no OpenAlex os trabalhos mais relevantes de cada conceito e as palavras-chave indexadas neles…</p>';
  e.target.disabled = true;
  try {
    const r = (ultimaSugestao = await api("POST", "/api/sugestoes", { tema }));
    el.innerHTML = `<div class="rotulo-linha"><h2>Palavras-chave sugeridas</h2><span class="ajuda">${esc(r.base)}</span></div>
      <p class="ajuda">Cada conceito do tema vira um bloco. Marque os termos que quer usar; o número é quantos trabalhos têm o termo no título ou no resumo.</p>` +
      r.blocos.map((b, i) => `<div class="conceito"><h3>Bloco ${i + 1}: ${esc(b.conceito)} ${b.topicos.length ? `<span class="ajuda">· tema: ${esc(b.topicos.join(" / "))}</span>` : ""}</h3>
        ${b.aviso ? `<p class="ajuda erro">${esc(b.aviso)}</p>` : ""}
        <div class="fichas">${b.termos.map((t, j) => `<label class="ficha-termo${t.sugerido ? " marcada" : ""}${t.geral ? " geral" : ""}" title="${esc(t.motivo)}">
          <input type="checkbox" data-b="${i}" data-t="${j}"${t.sugerido ? " checked" : ""}> ${esc(t.termo)} <small>${t.trabalhos === null || t.trabalhos === undefined ? "?" : num(t.trabalhos)}</small></label>`).join("")}</div></div>`).join("") +
      `<p class="ajuda">${esc(r.nota)}</p>
      <div class="rodape-form"><button type="button" class="botao" id="usar-sugestoes">Usar como blocos da busca</button></div>`;
  } catch (x) {
    el.innerHTML = `<p class="erro">${esc(x.message)}</p>`;
  } finally {
    e.target.disabled = false;
  }
});
$("#tema").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); $("#sugerir").click(); } });

$("#sugestoes").addEventListener("change", (e) => {
  const c = e.target.closest("input[type=checkbox]");
  if (c) c.closest(".ficha-termo").classList.toggle("marcada", c.checked);
});

$("#sugestoes").addEventListener("click", (e) => {
  if (e.target.id !== "usar-sugestoes" || !ultimaSugestao) return;
  const escolhidos = ultimaSugestao.blocos.map((b, i) => b.termos.filter((_, j) => $(`#sugestoes input[data-b="${i}"][data-t="${j}"]`).checked).map((t) => t.termo))
    .filter((b) => b.length);
  if (!escolhidos.length) return aviso("Marque ao menos um termo.", true);
  $("#blocos").innerHTML = "";
  escolhidos.forEach((b) => adicionarBloco(b));
  delete $("#minimo").dataset.mexido;
  renumerarBlocos();
  if (!$("#rotulo").value.trim()) $("#rotulo").value = ultimaSugestao.tema.slice(0, 80);
  aviso(`${escolhidos.length} bloco(s) preenchido(s), combinados com OU. Use “Testar consulta” para ver o total.`, false, 6000);
  $("#blocos").scrollIntoView({ behavior: "smooth", block: "start" });
});

$("#testar-consulta").addEventListener("click", async (e) => {
  const f = lerFormulario();
  const erro = conferirFormulario(f);
  $("#erro-busca").textContent = erro;
  if (erro) return;
  const el = $("#resultado-teste");
  el.hidden = false;
  el.innerHTML = '<p class="ajuda">Contando os trabalhos de cada termo no OpenAlex…</p>';
  e.target.disabled = true;
  try {
    el.innerHTML = htmlDiagnostico(await api("POST", "/api/consulta/testar", f));
  } catch (x) {
    el.innerHTML = `<p class="erro">${esc(x.message)}</p>`;
  } finally {
    e.target.disabled = false;
  }
});

/* ------------------------------------------------------------ buscas */
async function atualizarBuscas() {
  estadoApp.buscas = await api("GET", `/api/buscas?${qp()}`);
  const el = $("#lista-buscas");
  const b = estadoApp.buscas;
  el.classList.toggle("vazio", !b.length);
  el.innerHTML = b.length
    ? tabela(["Busca", "Origem", "Início", "Estado", "#Registros", "#Atendem", "#Baixados", "#Já no acervo"], b.map((x) => ({
        id: x.id, celulas: [`<td class="titulo">${esc(x.rotulo || x.id)}<div class="sub">${esc(x.id)}</div></td>`,
          `<td>${esc(x.origem)}</td>`, `<td>${dataHora(x.inicio)}</td>`, `<td>${selo(x.estado)}</td>`,
          `<td class="num">${num(x.registros)}</td>`, `<td class="num">${num(x.atendem)}</td>`,
          `<td class="num">${num(x.baixados)}</td>`, `<td class="num">${num(x.ja_existiam)}</td>`] })), "clicavel")
    : `Nenhuma busca na pesquisa "${esc(estadoApp.pesquisa)}". Crie uma em Nova busca.`;
  if (estadoApp.detalhe) await abrirDetalhe(estadoApp.detalhe, false);
}

const ARQS = [["matriz_baixa.csv", "Matriz da baixa (.csv)"], ["resultados.csv", "Resultados (.csv)"], ["referencias.bib", "Referências (.bib)"], ["consulta.txt", "Consulta (.txt)"], ["log.txt", "Log"]];

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
      ${["interrompida", "cancelada", "erro"].includes(d.estado) ? `<button class="botao mini" id="retomar-busca">Retomar</button>` : ""}
      <button class="botao secundario mini" id="fechar-detalhe">Fechar</button></div></div>
    <p class="ajuda">Pesquisa <b>${esc(d.pesquisa)}</b> · pasta <code>${esc(d.pasta)}</code></p>
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
    ${d.diagnostico && d.diagnostico.blocos ? `<div class="diagnostico">${htmlDiagnostico(d.diagnostico)}</div>` : ""}
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
  } else if (e.target.id === "retomar-busca") {
    e.target.disabled = true;
    try {
      const r = await api("POST", `/api/buscas/${encodeURIComponent(id)}/retomar`);
      aviso("Busca retomada: o que já foi baixado não é baixado de novo.");
      await atualizarBuscas();
      abrirDetalhe(r.id);
    } catch (x) {
      aviso(x.message, true);
      e.target.disabled = false;
    }
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
  const r = await api("GET", `/api/obras?${qp()}&q=${q}&limite=200&pagina=${estadoApp.acervoPagina}`);
  const el = $("#lista-acervo");
  const linhas = r.itens.map((o) => {
    const id = encodeURIComponent(o.id);
    const autores = (o.autores || []).slice(0, 4).join("; ") + ((o.autores || []).length > 4 ? " et al." : "");
    return { celulas: [
      `<td class="titulo"><b>${esc(o.titulo || o.id)}</b><div class="sub">${esc(autores)}</div></td>`,
      `<td>${esc(o.ano)}</td>`, `<td>${esc(o.veiculo)}</td>`,
      `<td>${o.doi ? `<a href="https://doi.org/${esc(o.doi)}" target="_blank" rel="noopener noreferrer">${esc(o.doi)}</a>` : "—"}</td>`,
      `<td>${dataHora(o.baixado_em || o.incorporada_em)}<div class="sub">${esc(o.host_download || "")}${o.host_download ? " · " : ""}${esc(o.busca_origem_nome)}</div></td>`,
      `<td class="links"><a class="botao mini" href="/api/obras/${id}/pdf?${qp()}" target="_blank" rel="noopener">PDF</a>
        <a class="botao secundario mini" href="/api/obras/${id}/txt?${qp()}" target="_blank" rel="noopener" title="${o.txt_extraido ? num(o.palavras_txt) + " palavras" : "PDF sem texto extraível"}">TXT</a>
        <a class="botao secundario mini" href="/api/obras/${id}/bib?${qp()}">BIB</a>
        <button class="botao secundario mini" data-rastreio="${esc(o.id)}">Rastreio</button></td>`] };
  });
  const cab = `<p class="ajuda">${num(r.total)} obra(s)${$("#filtro-acervo").value.trim() ? " com o filtro" : ""}.</p>`;
  const tab = tabela(["Obra", "Ano", "Veículo", "DOI", "Baixado em", "Arquivos"], linhas);
  if (reiniciar || !$("table", el)) {
    el.classList.toggle("vazio", !r.total);
    el.innerHTML = r.total ? cab + tab : `A pesquisa "${esc(estadoApp.pesquisa)}" ainda não tem obras. Elas aparecem aqui conforme são baixadas.`;
  } else {
    $("tbody", el).insertAdjacentHTML("beforeend", $("tbody", new DOMParser().parseFromString(`<table>${tab.match(/<tbody>[\s\S]*<\/tbody>/)[0]}</table>`, "text/html")).innerHTML);
  }
  $("#mais-acervo")?.remove();
  if (estadoApp.acervoPagina * 200 < r.total) {
    el.insertAdjacentHTML("beforeend", '<div class="links"><button class="botao secundario" id="mais-acervo">Carregar mais</button></div>');
    $("#mais-acervo").addEventListener("click", () => { estadoApp.acervoPagina += 1; carregarAcervo(false); });
  }
}

$("#lista-acervo").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-rastreio]");
  if (!b) return;
  try {
    const f = await api("GET", `/api/obras/${encodeURIComponent(b.dataset.rastreio)}/rastreabilidade?${qp()}`);
    $("#conteudo-rastreio").innerHTML = fichaRastreio(f);
    $("#modal-rastreio").showModal();
  } catch (x) {
    aviso(x.message, true);
  }
});
$("#fechar-rastreio").addEventListener("click", () => $("#modal-rastreio").close());

function fichaRastreio(f) {
  const v = (x) => (x === null || x === undefined || x === "" || (Array.isArray(x) && !x.length) ? "—" : Array.isArray(x) ? x.map((i) => esc(typeof i === "object" ? JSON.stringify(i) : i)).join("<br>") : esc(typeof x === "object" ? JSON.stringify(x) : x));
  const bloco = (titulo, obj, nomes) => obj ? `<h3>${esc(titulo)}</h3><dl>${Object.entries(nomes).map(([k, n]) => `<dt>${esc(n)}</dt><dd>${v(obj[k])}</dd>`).join("")}</dl>` : "";
  const d = f.download || {};
  return `<div class="ficha">${f.reconstruida ? `<p class="cartao aviso">${esc(f.nota)}</p>` : ""}
    <dl><dt>Arquivo</dt><dd>${v(f.arquivo)}</dd><dt>Pesquisa</dt><dd>${v(f.pesquisa)}</dd></dl>
    ${bloco("Download", d, { fim_download: "Data e hora da baixa", inicio_download: "Início", duracao_s: "Duração (s)", url_solicitada: "Endereço pedido",
      url_final: "Endereço final (de onde veio o arquivo)", redirecionamentos: "Redirecionamentos", host: "Servidor", status_http: "Resposta HTTP",
      content_type: "Tipo de conteúdo", bytes: "Bytes recebidos", last_modified: "Last-Modified (servidor)", etag: "ETag", servidor_http: "Software do servidor",
      user_agent: "Identificação usada", incorporada_em: "Incorporada em" })}
    ${f.tentativas ? `<h3>Tentativas (${f.tentativas.length})</h3>${tabela(["Quando", "Endereço", "Resultado"], f.tentativas.map((t) => ({ celulas: [`<td>${esc(t.quando)}</td>`, `<td>${esc(t.url)}</td>`, `<td>${esc(t.resultado)}</td>`] })))}` : ""}
    ${bloco("Busca e consulta", f.busca, { nome: "Busca", id: "ID da busca", origem: "Origem", inicio: "Início da busca", consulta_openalex: "Consulta no OpenAlex",
      consulta_semantic_scholar: "Consulta no Semantic Scholar", periodo: "Período", minimo_blocos: "Mínimo de blocos" })}
    ${bloco("Registro bibliográfico", f.registro_bibliografico, { titulo: "Título", autores: "Autores", ano: "Ano", veiculo: "Veículo", doi: "DOI",
      pagina_do_artigo: "Página do artigo", url: "Página do artigo", base_de_origem: "Base de origem", fonte: "Base de origem", id_openalex: "ID OpenAlex",
      id_semantic_scholar: "ID Semantic Scholar", verificacao_blocos: "Blocos atendidos" })}
    ${bloco("Acesso aberto", f.acesso_aberto, { segundo_a_base: "Acesso aberto segundo a base", status_oa: "Status OA", licenca: "Licença", versao: "Versão",
      pagina_oa: "Página OA", links_de_pdf_informados: "Links de PDF informados pelas bases" })}
    ${bloco("Integridade", f.integridade, { sha256: "SHA-256", md5: "MD5", bytes_em_disco: "Bytes em disco", "comeca_com_%PDF": "Começa com %PDF" })}
    ${bloco("Ambiente", f.ambiente, { programa: "Programa", sistema: "Sistema operacional", python: "Python" })}</div>`;
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
          `<td class="titulo"><b>${esc(a.nome)}</b><div class="sub">Pesquisa: ${esc(a.busca.pesquisa || "Geral")}</div><div class="sub">${(a.busca.blocos || []).map((b) => "(" + b.map(esc).join(" OU ") + ")").join(" E ")}</div></td>`,
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
  const buscas = await api("GET", `/api/buscas?${qp()}`);
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
    const r = await api("POST", `/api/validacao/testes?${qp()}`);
    const falhas = r.total - r.aprovados;
    el.classList.remove("vazio");
    el.innerHTML = `<p><span class="selo ${falhas ? "nao" : "sim"}">${r.aprovados} de ${r.total} aprovados</span>
        ${r.alertas ? `<span class="selo interrompida">${r.alertas} alerta(s)</span>` : ""} <span class="ajuda">pesquisa ${esc(r.pesquisa)} · em ${dataHora(r.quando)}</span></p>` +
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
  $("#caminho-repo").textContent = `Pasta das pesquisas: ${s.repositorio} (uma subpasta por pesquisa: ${s.pesquisas.map((p) => p.nome).join(", ") || "nenhuma ainda"})`;
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
        if (estadoApp.aba === "painel") carregarRelatorios().catch(() => {});
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
definirPesquisa(estadoApp.pesquisa || "Geral", false);
adicionarBloco();
adicionarBloco();
atualizarPeriodo();
irPara((location.hash || "#painel").slice(1), false);
window.addEventListener("hashchange", () => irPara(location.hash.slice(1), false));
setTimeout(ciclo, 2000);

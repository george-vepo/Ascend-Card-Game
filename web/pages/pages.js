"use strict";
/* GitHub Pages: armazenamento somente neste navegador, sem backend. */
(() => {
  const key = "ascend-card-game/pages-resultado-demo-v1";
  const core = window.SRDLocalDemo;
  const el = id => document.getElementById(id);
  let state = core.initial();
  let broken = false;
  const fields = side => {
    const s = side.toLowerCase();
    return {
      nome: el("setup-name-"+s), id: el("setup-id-"+s),
      pv_max: el("setup-max-"+s), pv_atual: el("setup-hp-"+s),
      ca: el("setup-ac-"+s)
    };
  };
  function feedback(msg, error) {
    let e = el("feedback");
    if (!e) {
      e = document.createElement("p");
      e.id = "feedback"; e.className = "feedback";
      e.setAttribute("role", "status"); e.setAttribute("aria-live", "polite");
      el("setup-section").before(e);
    }
    e.classList.toggle("error", !!error);
    e.classList.toggle("success", !error);
    e.textContent = msg;
  }
  function load() {
    try {
      const raw = localStorage.getItem(key);
      state = raw ? core.validate(JSON.parse(raw)) : core.initial();
    } catch (_) { broken = true; }
  }
  function save(next) {
    core.validate(next);
    localStorage.setItem(key, JSON.stringify(next));
    state = next;
  }
  function renderBoard(side) {
    const card = state.campos[side], s = side.toLowerCase();
    el("name-"+s).textContent = card ? card.nome : "Sem criatura no campo";
    el("id-"+s).textContent = card ? card.id : "—";
    el("ac-"+s).textContent = card ? card.ca ?? "—" : "—";
    el("hp-"+s).textContent = card ? card.pv_atual+" / "+card.pv_max : "—";
    el("winner-name-"+s).textContent = card ? card.nome : "—";
  }
  function renderSetup() {
    el("setup-section").hidden = state.fase !== "CONFIGURACAO";
    if (state.fase !== "CONFIGURACAO") return;
    for (const side of ["J1", "J2"]) {
      const card = state.campos[side], inputs = fields(side);
      for (const [field, input] of Object.entries(inputs)) {
        input.value = card ? (card[field] ?? "") : "";
        input.readOnly = !!card;
        input.classList.toggle("locked", !!card);
      }
      el("survivor-"+side.toLowerCase()).hidden = !card;
    }
  }
  function updateLimit() {
    const side = document.querySelector('input[name="winner"]:checked')?.value;
    const card = side && state.campos[side], input = el("remaining-hp");
    el("max-hp").textContent = card ? "/ "+card.pv_max+" PV máx." : "/ — PV máx.";
    el("pv-rule").textContent = card ? "De 1 a "+card.pv_max+" PV." : "Selecione o vencedor.";
    if (card) {
      input.max = String(card.pv_max);
      if (Number(input.value)>card.pv_max) input.value="";
    } else { input.removeAttribute("max"); input.value=""; }
  }
  function renderHistory() {
    const root = el("history"); root.replaceChildren();
    if (!state.historico.length) {
      const p = document.createElement("p"); p.className="muted";
      p.textContent="Nenhum combate registrado neste navegador.";
      root.appendChild(p); return;
    }
    for (const e of [...state.historico].reverse()) {
      const p = document.createElement("p"); p.className="history-row";
      p.textContent="Combate "+e.combate+" · "+e.vencedor+" ("+e.nome_vencedor+
        ") venceu com "+e.pv_vencedor_final+" PV · "+e.carta_derrotada_id+" no cemitério";
      root.appendChild(p);
    }
  }
  function render() {
    el("combat-number").textContent=String(state.combate);
    const labels={
      CONFIGURACAO:"Preparação", COMBATE:"Combate",
      POS_COMBATE:"Pós-combate", ENCERRADA:"Duelo encerrado"
    };
    el("phase").textContent="Fase: "+labels[state.fase];
    el("current-version").textContent="Estado local V"+state.versao;
    for (const side of ["J1","J2"]) {
      el("score-"+side.toLowerCase()).textContent=state.placar[side];
      renderBoard(side);
    }
    const grave=side=>state.cemiterio.filter(x=>x.jogador===side).length;
    el("cemetery-summary").textContent="Cemitério: J1 "+grave("J1")+" · J2 "+grave("J2");
    renderSetup();
    el("result-section").hidden=state.fase!=="COMBATE";
    const after=["POS_COMBATE","ENCERRADA"].includes(state.fase)&&!!state.ultimo;
    el("after").hidden=!after;
    if (after) {
      const e=state.ultimo;
      el("after-title").textContent="Vitória de "+e.vencedor;
      el("after-details").textContent=e.nome_vencedor+" ("+e.carta_vencedora_id+
        ") permanece com "+e.pv_vencedor_final+" PV; "+e.carta_derrotada_id+
        " foi ao cemitério. Placar local: "+state.placar.J1+" × "+state.placar.J2+".";
      el("next").hidden=state.fase==="ENCERRADA";
    }
    if (state.fase==="COMBATE") updateLimit();
    renderHistory();
  }
  function cardFromForm(side) {
    const c=fields(side);
    return {
      nome:c.nome.value.trim(), id:c.id.value.trim(),
      pv_max:Number(c.pv_max.value), pv_atual:Number(c.pv_atual.value),
      ca:c.ca.value.trim()==="" ? null : Number(c.ca.value)
    };
  }
  el("setup-form").addEventListener("submit", event=>{
    event.preventDefault();
    try {
      save(core.preparar(state,{J1:cardFromForm("J1"),J2:cardFromForm("J2")},state.versao));
      el("result-form").reset(); render();
      feedback("Combate preparado! Simule no ChatGPT e informe o resultado.",false);
    } catch(e) { feedback(e.message,true); }
  });
  document.querySelectorAll('input[name="winner"]').forEach(input=>
    input.addEventListener("change",updateLimit));
  el("result-form").addEventListener("submit",event=>{
    event.preventDefault();
    const winner=document.querySelector('input[name="winner"]:checked')?.value;
    const hpText=el("remaining-hp").value.trim();
    if (!el("confirm").checked) { feedback("Confirme que a batalha foi simulada externamente.",true); return; }
    if (!/^\d+$/.test(hpText)) { feedback("PV restantes devem ser inteiros.",true); return; }
    try {
      save(core.resultado(state,{
        vencedor:winner,pv_restantes:Number(hpText),
        evento_id:"manual-"+crypto.randomUUID(),
        combate:state.combate,versao_base:state.versao
      }));
      render(); feedback("Resultado salvo apenas neste navegador.",false);
    } catch(e) { feedback(e.message,true); }
  });
  el("next").addEventListener("click",()=>{
    try {
      save(core.proximo(state,state.versao));render();
      feedback("Novo combate: a criatura sobrevivente preservou os PV.",false);
      el("setup-section").scrollIntoView({behavior:"smooth",block:"start"});
    } catch(e) { feedback(e.message,true); }
  });
  el("reset").addEventListener("click",()=>{
    if (!confirm("Apagar placar, histórico e cemitério desta demonstração LOCAL?")) return;
    try {
      save(core.initial());el("result-form").reset();render();
      el("setup-form").hidden=false;broken=false;
      feedback("Demonstração reiniciada.",false);
    } catch(e) {feedback(e.message,true);}
  });
  load();render();
  if (broken) {
    el("setup-form").hidden=true;el("result-form").hidden=true;
    feedback("Dados locais ilegíveis. Use Reiniciar demonstração para limpar.",true);
  }
})();

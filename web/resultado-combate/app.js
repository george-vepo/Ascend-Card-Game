"use strict";

const $ = (id) => document.getElementById(id);
let snapshot = null;
let eventId = null;

async function getJson(url, options = {}) {
  const response = await fetch(url, { cache: "no-store", ...options });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.motivo || data.erro || "Não foi possível concluir.");
  }
  return data;
}

function message(text, error = false) {
  const area = $("feedback");
  area.textContent = text;
  area.classList.toggle("error", error);
  area.classList.toggle("success", !error);
}

function fieldInfo(jogador) {
  return snapshot?.mesa?.jogadores?.[jogador]?.campo ?? null;
}

function renderFighter(player) {
  const fighter = fieldInfo(player);
  $("name-" + player.toLowerCase()).textContent = fighter?.nome ?? "Sem criatura em campo";
  $("id-" + player.toLowerCase()).textContent = fighter?.carta_id ?? "—";
  $("ac-" + player.toLowerCase()).textContent = fighter?.ca ?? "—";
  $("hp-" + player.toLowerCase()).textContent = fighter
    ? `${fighter.pv_atual} / ${fighter.pv_max}` : "—";
  $("conditions-" + player.toLowerCase()).textContent =
    fighter?.condicoes?.length ? fighter.condicoes.join(" · ") : "Sem condições";
  $("winner-name-" + player.toLowerCase()).textContent = fighter?.nome ?? "Sem criatura";
}

function updateLimit() {
  const winner = document.querySelector("input[name=winner]:checked")?.value;
  const info = winner && fieldInfo(winner);
  const input = $("remaining-hp");
  if (!info) {
    input.value = "";
    input.removeAttribute("max");
    $("max-hp").textContent = "/ — PV máx.";
    $("pv-rule").textContent = "Escolha o vencedor para ver o limite.";
    return;
  }
  input.max = String(info.pv_max);
  $("max-hp").textContent = `/ ${info.pv_max} PV máx.`;
  $("pv-rule").textContent = `Entre 1 e ${info.pv_max} PV, após a simulação externa.`;
  if (input.value && Number(input.value) > info.pv_max) {
    input.value = "";
  }
}

function render() {
  const mesa = snapshot.mesa;
  $("combat-number").textContent = String(snapshot.combate_numero);
  $("phase").textContent = `Fase: ${mesa.fase}`;
  $("score-j1").textContent = mesa.placar.J1;
  $("score-j2").textContent = mesa.placar.J2;
  $("current-version").textContent = `Estado ${snapshot.versao_base}`;
  renderFighter("J1");
  renderFighter("J2");
  const available = mesa.fase === "COMBATE"
    && fieldInfo("J1") !== null && fieldInfo("J2") !== null;
  for (const element of $("result-form").elements) {
    element.disabled = !available;
  }
  $("result-form").hidden = !available;
  const result = mesa.ultimo_resultado_externo;
  if (result) {
    $("after").hidden = false;
    $("after-title").textContent = `Vitória de ${result.vencedor}`;
    $("after-details").textContent =
      `${result.carta_vencedora_id} permanece com ${result.pv_vencedor_final} PV. ` +
      `${result.carta_derrotada_id} foi ao cemitério. Placar: ` +
      `${mesa.placar.J1} × ${mesa.placar.J2}.`;
  } else {
    $("after").hidden = true;
  }
  if (!available && !result) {
    message("O registro manual só é permitido durante um combate com duas criaturas ativas.", true);
  }
  updateLimit();
}

async function refresh() {
  try {
    const data = await getJson("/api/combate");
    if (snapshot?.versao_base !== data.versao_base) {
      eventId = null;
    }
    snapshot = data;
    render();
  } catch (error) {
    message("Não foi possível carregar a mesa: " + error.message, true);
    $("result-form").hidden = true;
  }
}

async function submit(event) {
  event.preventDefault();
  if (!snapshot || snapshot.mesa.fase !== "COMBATE") return;
  const winner = document.querySelector("input[name=winner]:checked")?.value;
  const target = winner && fieldInfo(winner);
  const hp = $("remaining-hp").value.trim();
  if (!target || !/^\d+$/.test(hp)
      || !Number.isSafeInteger(Number(hp))
      || Number(hp) < 1 || Number(hp) > target.pv_max) {
    message("Escolha o vencedor e informe PV inteiros entre 1 e o PV máximo.", true);
    return;
  }
  if (!$("confirm").checked) {
    message("Confirme que o resultado foi apurado fora do site.", true);
    return;
  }
  eventId ??= "externo-" + crypto.randomUUID();
  $("submit-result").disabled = true;
  message("Registrando resultado…");
  try {
    const payload = {
      evento_id: eventId,
      combate_numero: snapshot.combate_numero,
      vencedor: winner,
      pv_restantes_vencedor: Number(hp),
      versao_base: snapshot.versao_base,
      hash_estado_base: snapshot.hash_estado_base,
      confirmacao_usuario: true,
    };
    const result = await getJson("/api/resultado", {
      method: "POST",
      headers: { "Content-Type": "application/json",
                 "X-CSRF-Token": snapshot.token_formulario },
      body: JSON.stringify(payload),
    });
    if (result.decisao !== "ACEITA") {
      throw new Error(result.motivo || "Não autorizado.");
    }
    message("Resultado registrado! O placar e os PV foram atualizados.");
    await refresh();
  } catch (error) {
    message(error.message + " Atualize a mesa e confira antes de tentar novamente.", true);
  } finally {
    $("submit-result").disabled = false;
  }
}

$("reload").addEventListener("click", refresh);
for (const option of document.querySelectorAll("input[name=winner]")) {
  option.addEventListener("change", updateLimit);
}
$("result-form").addEventListener("submit", submit);
refresh();

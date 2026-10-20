/* SRD Card Game — demonstração local no navegador, nunca estado oficial. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.SRDLocalDemo = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";
  const SIDES = ["J1", "J2"];
  const FAIL = (message) => { throw new Error(message); };
  const copy = (item) => JSON.parse(JSON.stringify(item));
  const opposite = (p) => p === "J1" ? "J2" : "J1";
  const validSide = (p) => SIDES.includes(p);
  const isInt = (n) => Number.isSafeInteger(n);

  function initial() {
    return {
      schema: 1, ambiente: "DEMO_LOCAL_NAO_OFICIAL",
      versao: 0, fase: "CONFIGURACAO", combate: 1,
      placar: { J1: 0, J2: 0 },
      campos: { J1: null, J2: null },
      cemiterio: [], historico: [], ultimo: null,
    };
  }

  function validCard(c, side) {
    if (!c || typeof c !== "object" || Array.isArray(c)
        || Object.keys(c).sort().join("|") !== ["ca", "id", "nome", "pv_atual", "pv_max"].sort().join("|"))
      return FAIL("Preencha todos os dados públicos da criatura " + side + ".");
    if (typeof c.nome !== "string" || !c.nome.trim() || c.nome.length > 90 ||
        typeof c.id !== "string" || !/^[A-Za-z0-9_:-]{1,80}$/.test(c.id))
      FAIL("Nome ou ID inválido para " + side + ".");
    if (!isInt(c.pv_max) || c.pv_max < 1 || c.pv_max > 100000 ||
        !isInt(c.pv_atual) || c.pv_atual < 1 || c.pv_atual > c.pv_max)
      FAIL("Os PV de " + side + " precisam ser inteiros entre 1 e o máximo.");
    if (c.ca !== null && (!isInt(c.ca) || c.ca < 0 || c.ca > 100))
      FAIL("CA de " + side + " inválida.");
    return copy(c);
  }

  function validate(state) {
    if (!state || state.schema !== 1 || state.ambiente !== "DEMO_LOCAL_NAO_OFICIAL"
        || !isInt(state.versao) || state.versao < 0
        || !isInt(state.combate) || state.combate < 1
        || !["CONFIGURACAO", "COMBATE", "POS_COMBATE", "ENCERRADA"].includes(state.fase)
        || !state.placar || !state.campos ||
        !Array.isArray(state.historico) || !Array.isArray(state.cemiterio))
      FAIL("Dados locais incompatíveis. Reinicie a demonstração.");
    for (const side of SIDES) {
      if (!isInt(state.placar[side]) || state.placar[side] < 0 || state.placar[side] > 3)
        FAIL("Placar local inválido.");
      if (state.campos[side] !== null) validCard(state.campos[side], side);
    }
    if (state.campos.J1 && state.campos.J2 && state.campos.J1.id === state.campos.J2.id)
      FAIL("IDs de cópias do campo precisam ser diferentes.");
    if (state.fase === "COMBATE" && (!state.campos.J1 || !state.campos.J2))
      FAIL("Combate exige duas criaturas em campo.");
    if (state.fase === "ENCERRADA" && !SIDES.some(p => state.placar[p] === 3))
      FAIL("Vitória final precisa de três pontos.");
    if (state.fase === "POS_COMBATE" && SIDES.some(p => state.placar[p] === 3))
      FAIL("Não pode continuar depois de três pontos.");
    return state;
  }

  function preparar(state, cards, expectedVersion) {
    validate(state);
    if (state.fase !== "CONFIGURACAO") FAIL("Este combate já foi preparado.");
    if (state.versao !== expectedVersion) FAIL("Estado alterado. Atualize a página.");
    const next = copy(state);
    const data = {};
    for (const p of SIDES) {
      data[p] = validCard(cards[p], p);
      if (state.campos[p] && JSON.stringify(state.campos[p]) !== JSON.stringify(data[p]))
        FAIL("A criatura sobrevivente deve permanecer com os PV anteriores.");
    }
    if (data.J1.id === data.J2.id) FAIL("IDs de cópias precisam ser diferentes.");
    next.campos = data;
    next.fase = "COMBATE";
    next.versao++;
    return validate(next);
  }

  function resultado(state, { vencedor, pv_restantes, evento_id, combate, versao_base }) {
    validate(state);
    if (state.fase !== "COMBATE") FAIL("Não há combate aguardando resultado.");
    if (state.versao !== versao_base || state.combate !== combate)
      FAIL("Versão ou combate divergente. Atualize a tela.");
    if (!validSide(vencedor)) FAIL("Escolha J1 ou J2 como vencedor.");
    if (typeof evento_id !== "string" || !/^[A-Za-z0-9_-]{1,128}$/.test(evento_id))
      FAIL("ID do evento inválido.");
    if (state.historico.some(event => event.evento_id === evento_id))
      FAIL("Este evento já foi registrado.");
    const winner = state.campos[vencedor];
    const loserId = opposite(vencedor);
    const loser = state.campos[loserId];
    if (!winner || !loser) FAIL("É necessário haver duas criaturas no campo.");
    if (!isInt(pv_restantes) || pv_restantes < 1 || pv_restantes > winner.pv_max)
      FAIL("PV restantes devem estar entre 1 e o PV máximo do vencedor.");
    const next = copy(state);
    next.campos[vencedor].pv_atual = pv_restantes;
    next.campos[loserId] = null;
    next.cemiterio.push({
      combate: state.combate, jogador: loserId, carta_id: loser.id, nome: loser.nome, pv_final: 0,
    });
    next.placar[vencedor] += 1;
    const event = {
      evento_id, combate: state.combate,
      vencedor, nome_vencedor: winner.nome, carta_vencedora_id: winner.id,
      pv_vencedor_final: pv_restantes, perdedor: loserId,
      carta_derrotada_id: loser.id, status: "RESULTADO_MANUAL_NAO_VERIFICADO",
    };
    next.ultimo = event;
    next.historico.push(event);
    next.fase = next.placar[vencedor] === 3 ? "ENCERRADA" : "POS_COMBATE";
    next.versao++;
    return validate(next);
  }

  function proximo(state, expectedVersion) {
    validate(state);
    if (state.fase !== "POS_COMBATE") FAIL("A partida não pode iniciar outro combate.");
    if (state.versao !== expectedVersion) FAIL("Atualize antes de continuar.");
    const next = copy(state);
    next.combate++;
    next.fase = "CONFIGURACAO";
    next.ultimo = null;
    next.versao++;
    return validate(next);
  }

  return { initial, validate, preparar, resultado, proximo };
});

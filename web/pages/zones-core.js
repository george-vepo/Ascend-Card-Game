/* Etapa 1: invariantes das zonas. Rascunho local, sem iniciar uma partida. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.SRDZonesDemo = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  const SIDES = ['J1', 'J2'];
  const RARITIES = ['Comum', 'Incomum', 'Rara', 'Lendária', 'Mítica'];
  const copy = value => JSON.parse(JSON.stringify(value));
  const fail = message => { throw new Error(message); };
  const isCount = value => Number.isSafeInteger(value) && value >= 0;

  function card(value) {
    if (!value || typeof value !== 'object' ||
        typeof value.copiaId !== 'string' || !/^[A-Za-z0-9_:-]{1,80}$/.test(value.copiaId) ||
        typeof value.catalogoId !== 'string' || !/^[A-Za-z0-9_-]{1,80}$/.test(value.catalogoId) ||
        typeof value.nome !== 'string' || !value.nome.trim() ||
        typeof value.tipo !== 'string' || !value.tipo.trim() ||
        !RARITIES.includes(value.raridade) ||
        (typeof value.nd !== 'string' && typeof value.nd !== 'number') ||
        String(value.nd).trim() === '' ||
        (typeof value.nd === 'number' && !Number.isFinite(value.nd))) fail('Identidade da carta inválida.');
    const ca = value.ca ?? null;
    const pvMax = value.pvMax ?? null;
    if ((ca !== null && !isCount(ca)) ||
        (pvMax !== null && (!isCount(pvMax) || pvMax === 0)))
      fail('Ficha numérica inválida.');
    return {
      copiaId: value.copiaId, catalogoId: value.catalogoId,
      nome: value.nome, tipo: value.tipo, raridade: value.raridade, nd: value.nd,
      ca, pvMax, imagem: value.imagem ?? '', fichaUrl: value.fichaUrl ?? ''
    };
  }

  // Confere a identidade de todas as 80 cópias, não apenas a soma das zonas.
  function check(state) {
    if (!state || state.ambiente !== 'DEMO_LOCAL_NAO_OFICIAL' ||
        state.estagio !== 'RASCUNHO_ZONAS' || !isCount(state.versao) ||
        !state.jogadores || !state.inventario || !state.placar ||
        state.placar.J1 !== 0 || state.placar.J2 !== 0)
      fail('Rascunho local inválido.');

    const seen = new Set();
    const registered = new Set();
    for (const side of SIDES) {
      const player = state.jogadores[side];
      const inventory = state.inventario[side];
      if (!player || !Array.isArray(player.monte) || !Array.isArray(player.mao) ||
          !Array.isArray(player.cemiterio) || !Object.hasOwn(player, 'campo') ||
          !Array.isArray(inventory) || inventory.length !== 40)
        fail('Zonas ou inventário ausentes.');
      const canonical = new Map();
      for (const original of inventory) {
        const registeredCard = card(original);
        if (registered.has(registeredCard.copiaId)) fail('ID duplicado no inventário.');
        registered.add(registeredCard.copiaId);
        canonical.set(registeredCard.copiaId, registeredCard);
      }
      const zones = [...player.monte, ...player.mao, ...player.cemiterio,
        ...(player.campo === null ? [] : [player.campo])];
      if (zones.length !== 40) fail('A soma das zonas deve ser 40.');
      for (const current of zones) {
        const currentCard = card(current);
        if (seen.has(currentCard.copiaId)) fail('ID duplicado entre zonas.');
        seen.add(currentCard.copiaId);
        const original = canonical.get(currentCard.copiaId);
        if (!original || JSON.stringify(original) !== JSON.stringify(currentCard))
          fail('Cópia ausente, substituída ou com identidade alterada.');
      }
      if (player.campo !== null &&
          (!isCount(player.campo.pvAtual) || player.campo.pvAtual === 0 ||
           player.campo.pvMax === null || player.campo.pvAtual > player.campo.pvMax))
        fail('PV da criatura em campo inválidos.');
    }
    return state;
  }

  // Não embaralha, compra, invoca ou altera zonas. As cartas vêm do importador validado.
  function newDraft(decks) {
    const players = {}, inventory = {};
    for (const side of SIDES) {
      if (!Array.isArray(decks?.[side]) || decks[side].length !== 40)
        fail('Cada deck precisa de 40 cópias.');
      const entries = decks[side].map(card);
      inventory[side] = copy(entries);
      players[side] = { monte: copy(entries), mao: [], campo: null, cemiterio: [] };
    }
    return check({
      ambiente: 'DEMO_LOCAL_NAO_OFICIAL', estagio: 'RASCUNHO_ZONAS',
      versao: 0, jogadores: players, inventario: inventory, placar: { J1: 0, J2: 0 }
    });
  }

  function publico(state) {
    check(state);
    const players = {};
    for (const side of SIDES) {
      const player = state.jogadores[side];
      players[side] = {
        monte: player.monte.length, mao: player.mao.length,
        cemiterio: player.cemiterio.length,
        campo: player.campo === null ? null :
          { ...card(player.campo), pvAtual: player.campo.pvAtual }
      };
    }
    return { ambiente: state.ambiente, estagio: state.estagio,
      versao: state.versao, placar: copy(state.placar), jogadores: players };
  }

  function privado(state, side) {
    check(state);
    if (!SIDES.includes(side)) fail('Jogador inválido.');
    return copy(state.jogadores[side].mao);
  }

  return { newDraft, check, publico, privado };
});

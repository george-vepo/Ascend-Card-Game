/* Etapa 3: preparação de criaturas somente em testes sintéticos, sem partida oficial. */
(function (root, factory) {
  const node = typeof module === 'object' && module.exports;
  const zones = node ? require('./zones-core.js') : root && root.SRDZonesDemo;
  const exchange = node ? require('./draw-exchange-fixtures.js') : root && root.SRDDrawExchangeFixtures;
  const catalog = node ? require('./decks-core.js') : root && root.SRDDeckImport;
  const api = factory(zones, exchange, catalog);
  if (node) module.exports = api;
  if (root) root.SRDCreaturePreparationFixtures = api;
})(typeof window !== 'undefined' ? window : null, function (zones, exchange, catalog) {
  'use strict';
  const RARITIES = ['Comum', 'Incomum', 'Rara', 'Lendária', 'Mítica'];
  const SIDES = ['J1', 'J2'];
  const clone = value => JSON.parse(JSON.stringify(value));
  const fail = message => { throw new Error(message); };
  const other = side => side === 'J1' ? 'J2' : 'J1';

  function checkFixture(state, expectedVersion) {
    if (!zones || !exchange || !catalog ||
        typeof catalog.rarity !== 'function') fail('Dependências das etapas 1 e 2 indisponíveis.');
    zones.check(state);
    const sim = state.simulacao;
    if (!sim || sim.modo !== exchange.MODE ||
        !SIDES.includes(sim.primeiro) || !Array.isArray(sim.eventos))
      fail('Preparação permitida somente em fixture sintética.');
    if (!Number.isSafeInteger(expectedVersion) || expectedVersion !== state.versao)
      fail('Versão obsoleta da fixture.');
    return sim;
  }

  function beginFixture(state, expectedVersion) {
    const sim = checkFixture(state, expectedVersion);
    if (sim.etapa !== 'PREPARACAO_NAO_IMPLEMENTADA' || sim.vez !== null)
      fail('A preparação depende das duas trocas concluídas.');
    const [opening, first, second] = sim.eventos;
    if (sim.eventos.length !== 3 || opening?.acao !== 'ABERTURA_SINTETICA' ||
        first?.acao !== 'TROCA_SINTETICA' || first?.jogador !== sim.primeiro ||
        second?.acao !== 'TROCA_SINTETICA' || second?.jogador !== other(sim.primeiro))
      fail('Histórico da preparação sintética inconsistente.');
    const next = clone(state);
    next.versao++;
    next.simulacao.etapa = 'CRIATURA';
    next.simulacao.vez = sim.primeiro;
    next.simulacao.concluidos = [];
    next.simulacao.eventos.push({
      acao: 'INICIO_PREPARACAO_SINTETICA', versao: next.versao
    });
    return zones.check(next);
  }

  function requireTurn(state, side, expectedVersion) {
    const sim = checkFixture(state, expectedVersion);
    if (sim.etapa !== 'CRIATURA' || !Array.isArray(sim.concluidos) ||
        sim.concluidos.some(s => !SIDES.includes(s)))
      fail('Fora da preparação de criatura sintética.');
    if (!SIDES.includes(side) || sim.vez !== side || sim.concluidos.includes(side))
      fail('Ação fora da vez de preparação.');
    return state.jogadores[side];
  }

  function checkRarity(card) {
    if (catalog.rarity(card.nd) !== card.raridade)
      fail('Raridade da carta inconsistente com ND.');
  }

  function playFixture(state, side, copyId, expectedVersion) {
    const player = requireTurn(state, side, expectedVersion);
    if (typeof copyId !== 'string' || !copyId.trim()) fail('ID de cópia inválido.');
    const selected = player.mao.find(c => c.copiaId === copyId);
    if (!selected) fail('A carta deve estar na mão do próprio jogador.');
    checkRarity(selected);
    if (selected.ca === null || !Number.isSafeInteger(selected.ca) ||
        selected.pvMax === null || !Number.isSafeInteger(selected.pvMax) ||
        selected.pvMax <= 0)
      fail('PENDENTE: CA/PV da ficha individual indisponíveis.');
    const current = player.campo;
    if (!current) {
      if (selected.raridade !== 'Comum')
        fail('Somente Comum pode ser invocada diretamente.');
    } else {
      checkRarity(current);
      if (selected.tipo !== current.tipo)
        fail('Evolução exige o mesmo tipo de criatura.');
      if (RARITIES.indexOf(selected.raridade) !== RARITIES.indexOf(current.raridade) + 1)
        fail('Evolução exige raridade imediatamente superior.');
    }
    const next = clone(state);
    const destination = next.jogadores[side];
    destination.mao = destination.mao.filter(c => c.copiaId !== copyId);
    if (destination.campo) destination.cemiterio.push(destination.campo);
    destination.campo = { ...selected, pvAtual: selected.pvMax };
    next.versao++;
    next.simulacao.eventos.push({
      acao: current ? 'EVOLUCAO_SINTETICA' : 'INVOCACAO_SINTETICA',
      jogador: side, copiaId: copyId, substituida: current?.copiaId ?? null,
      versao: next.versao
    });
    return zones.check(next);
  }

  function finishFixture(state, side, expectedVersion) {
    const player = requireTurn(state, side, expectedVersion);
    if (!player.campo) fail('A preparação exige uma criatura ativa.');
    const next = clone(state);
    next.versao++;
    next.simulacao.concluidos.push(side);
    next.simulacao.eventos.push({
      acao: 'FIM_PREPARACAO_SINTETICA', jogador: side, versao: next.versao
    });
    if (side === next.simulacao.primeiro) {
      next.simulacao.vez = other(side);
    } else {
      next.simulacao.vez = null;
      next.simulacao.etapa = 'SUPORTE_NAO_IMPLEMENTADO';
    }
    return zones.check(next);
  }

  function publico(state) {
    const sim = checkFixture(state, state?.versao);
    if (!['CRIATURA', 'SUPORTE_NAO_IMPLEMENTADO'].includes(sim.etapa))
      fail('Nenhuma preparação sintética para exibir.');
    return exchange.publico(state);
  }

  return { beginFixture, playFixture, finishFixture, publico };
});

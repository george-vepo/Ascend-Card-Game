/* Etapa 2: PREVISÃO sintética de saques e trocas, nunca uma partida real. */
(function (root, factory) {
  const zones = typeof module === 'object' && module.exports
    ? require('./zones-core.js') : root && root.SRDZonesDemo;
  const api = factory(zones);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.SRDDrawExchangeFixtures = api;
})(typeof window !== 'undefined' ? window : null, function (zones) {
  'use strict';

  const SIDES = ['J1', 'J2'];
  const MODE = 'TESTES_SINTETICOS';
  const fail = message => { throw new Error(message); };
  const clone = value => JSON.parse(JSON.stringify(value));
  const opposite = side => side === 'J1' ? 'J2' : 'J1';

  function core() {
    if (!zones || typeof zones.check !== 'function')
      fail('Motor de zonas da Etapa 1 indisponível.');
    return zones;
  }

  // Representação exclusivamente convencional para fixtures: o topo é o último índice.
  // Nenhum embaralhamento é executado ou autorizado aqui.
  function drawFromOrderedTop(player, count) {
    for (let i = 0; i < count; i++) player.mao.push(player.monte.pop());
  }

  function startFixture(draft, primeiro, mode) {
    core().check(draft);
    if (mode !== MODE) fail('Somente testes sintéticos autorizados.');
    if (!SIDES.includes(primeiro)) fail('Ordem sintética precisa ser J1 ou J2.');
    if (draft.versao !== 0 || Object.hasOwn(draft, 'simulacao'))
      fail('Rascunho já inicializado para teste.');
    for (const side of SIDES) {
      const p = draft.jogadores[side];
      if (p.monte.length !== 40 || p.mao.length !== 0 ||
          p.cemiterio.length !== 0 || p.campo !== null)
        fail('Fixture de abertura exige zonas iniciais intocadas.');
    }

    const state = clone(draft);
    for (const side of SIDES) drawFromOrderedTop(state.jogadores[side], 5);
    state.versao += 1;
    state.simulacao = {
      modo: MODE, etapa: 'TROCA', primeiro, vez: primeiro,
      eventos: [{ acao: 'ABERTURA_SINTETICA', quantidadePorJogador: 5, versao: state.versao }]
    };
    return core().check(state);
  }

  function requireExchange(state, side, ids, expectedVersion) {
    core().check(state);
    const sim = state.simulacao;
    if (!sim || sim.modo !== MODE || sim.etapa !== 'TROCA' ||
        !SIDES.includes(sim.primeiro) || !SIDES.includes(sim.vez) ||
        !Array.isArray(sim.eventos)) fail('Não existe troca sintética ativa.');
    if (!SIDES.includes(side) || sim.vez !== side)
      fail('Troca fora da ordem sintética.');
    if (!Number.isSafeInteger(expectedVersion) || expectedVersion !== state.versao)
      fail('Versão obsoleta da previsão.');
    if (!Array.isArray(ids) || ids.length > 5 ||
        ids.some(id => typeof id !== 'string') || new Set(ids).size !== ids.length)
      fail('Selecione de 0 a 5 IDs de cópia distintos.');
    const player = state.jogadores[side];
    if (player.mao.length !== 5) fail('Mão inicial da fixture foi alterada.');
    const handIds = new Set(player.mao.map(c => c.copiaId));
    if (ids.some(id => !handIds.has(id)))
      fail('Troca exige cópia presente na própria mão.');
    // Q-06 não homologada: não inventar como resolver troca com monte insuficiente.
    if (player.monte.length < ids.length)
      fail('PENDENTE: monte insuficiente para a troca; Q-06 não aprovada.');
  }

  function exchangeFixture(state, side, ids, expectedVersion) {
    requireExchange(state, side, ids, expectedVersion);
    const next = clone(state);
    const player = next.jogadores[side];
    const selected = new Set(ids);
    const discarded = player.mao.filter(c => selected.has(c.copiaId));
    player.mao = player.mao.filter(c => !selected.has(c.copiaId));
    player.cemiterio.push(...discarded);
    drawFromOrderedTop(player, ids.length);
    next.versao += 1;
    next.simulacao.eventos.push({
      acao: 'TROCA_SINTETICA', jogador: side,
      descartadas: discarded.length, compradas: ids.length,
      versao: next.versao
    });
    if (side === next.simulacao.primeiro) {
      next.simulacao.vez = opposite(side);
    } else {
      next.simulacao.vez = null;
      next.simulacao.etapa = 'PREPARACAO_NAO_IMPLEMENTADA';
    }
    return core().check(next);
  }

  function publico(state) {
    core().check(state);
    if (!state.simulacao || state.simulacao.modo !== MODE)
      fail('Não é uma fixture de compra ou troca.');
    return {
      ...core().publico(state),
      simulacao: { modo: MODE, etapa: state.simulacao.etapa, vez: state.simulacao.vez }
    };
  }

  return { MODE, startFixture, exchangeFixture, publico };
});

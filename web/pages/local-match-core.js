/* V1 local: partida Humano x IA. Nunca usar fixtures como criaturas oficiais. */
(function (root, factory) {
  const node = typeof module === 'object' && module.exports;
  const zones = node ? require('./zones-core.js') : root && root.SRDZonesDemo;
  const decks = node ? require('./decks-core.js') : root && root.SRDDeckImport;
  const combat = node ? require('./combat-srd-subset.js') : root && root.SRDCombatSubset;
  const api = factory(zones, decks, combat);
  if (node) module.exports = api;
  if (root) root.SRDLocalMatch = api;
})(typeof window !== 'undefined' ? window : null, function (zones, decks, combat) {
  'use strict';
  const SIDES = ['J1', 'J2'];
  const RARITIES = ['Comum', 'Incomum', 'Rara', 'Lendária', 'Mítica'];
  const MODE = 'PARTIDA_LOCAL_HUMANO_IA_V1';
  const PHASES = ['TROCA', 'CRIATURA', 'SUPORTE', 'COMBATE_PENDENTE',
    'INICIATIVA_EMPATE_PENDENTE', 'COMBATE', 'INICIO_CICLO_PENDENTE', 'ENCERRADA'];
  const clone = data => JSON.parse(JSON.stringify(data));
  const fail = message => { throw new Error(message); };
  const other = side => side === 'J1' ? 'J2' : 'J1';
  const validId = value => typeof value === 'string' && /^[A-Za-z0-9_:-]{1,100}$/.test(value);

  /* Reutiliza invariantes de 40 cópias sem alterar o contrato do laboratório. */
  function check(state) {
    if (!state || state.schema !== 1 || state.modo !== MODE ||
        state.ambiente !== 'LOCAL_BROWSER_NAO_COMPETITIVO' ||
        !PHASES.includes(state.fase) || !SIDES.includes(state.primeiro) ||
        (state.vez !== null && !SIDES.includes(state.vez)) ||
        !Number.isSafeInteger(state.versao) || state.versao < 1 ||
        !Array.isArray(state.historico) || state.historico.length !== state.versao ||
        new Set(state.historico.map(e => e.id)).size !== state.historico.length ||
        state.historico.some((e, i) => !validId(e.id) || e.versao !== i + 1 ||
          typeof e.acao !== 'string') ||
        !state.placar || SIDES.some(s => !Number.isSafeInteger(state.placar[s]) ||
          state.placar[s] < 0 || state.placar[s] > 3) ||
        (state.placar.J1 === 3 && state.placar.J2 === 3))
      fail('Checkpoint local incompatível ou corrompido.');
    const pending = ['COMBATE_PENDENTE', 'INICIATIVA_EMPATE_PENDENTE',
      'INICIO_CICLO_PENDENTE', 'ENCERRADA'];
    if (pending.includes(state.fase) && state.vez !== null)
      fail('Fase sem turno jogável não deve possuir ator.');
    if (!pending.includes(state.fase) && !SIDES.includes(state.vez))
      fail('Turno de preparação ou combate inválido.');
    if (state.fase === 'ENCERRADA' && !SIDES.some(s => state.placar[s] === 3))
      fail('Vitória final exige três pontos.');
    if (state.fase !== 'ENCERRADA' && SIDES.some(s => state.placar[s] === 3))
      fail('Não é permitido prosseguir depois do terceiro ponto.');
    if (state.fase === 'COMBATE') {
      const c = state.combate;
      if (!c || !Number.isSafeInteger(c.numero) || c.numero !== state.ciclo ||
          !Number.isSafeInteger(c.rodada) || c.rodada < 1 ||
          ![0, 1].includes(c.indice) || !Array.isArray(c.ordem) ||
          c.ordem.length !== 2 || new Set(c.ordem).size !== 2 ||
          c.ordem.some(s => !SIDES.includes(s)) || state.vez !== c.ordem[c.indice] ||
          !state.jogadores.J1.campo || !state.jogadores.J2.campo ||
          !c.iniciativas || !c.iniciativas.J1 || !c.iniciativas.J2)
        fail('Turno ou iniciativa de combate inválidos.');
      combat.profile(state.jogadores.J1.campo);
      combat.profile(state.jogadores.J2.campo);
    }
    if (['COMBATE_PENDENTE', 'INICIATIVA_EMPATE_PENDENTE'].includes(state.fase) &&
        (!state.jogadores.J1.campo || !state.jogadores.J2.campo))
      fail('Combate pendente exige duas criaturas ativas.');
    if (state.fase === 'INICIATIVA_EMPATE_PENDENTE' &&
        (!state.combate || state.combate.ordem !== null ||
         state.combate.indice !== null || state.combate.iniciativas?.J1?.total !==
         state.combate.iniciativas?.J2?.total))
      fail('Empate pendente exige rolagens de iniciativa iguais e registradas.');
    if (['INICIO_CICLO_PENDENTE', 'ENCERRADA'].includes(state.fase) &&
        Number(Boolean(state.jogadores.J1.campo)) +
        Number(Boolean(state.jogadores.J2.campo)) !== 1)
      fail('Após KO deve existir exatamente uma criatura sobrevivente.');
    if (!zones || typeof zones.check !== 'function') fail('Motor de zonas indisponível.');
    // O estado real tem marcador independente; apenas uma projeção transitória,
    // nunca persistida, é enviada ao validador de integridade das zonas.
    zones.check({
      ambiente: 'DEMO_LOCAL_NAO_OFICIAL', estagio: 'RASCUNHO_ZONAS',
      versao: state.versao, jogadores: state.jogadores,
      inventario: state.inventario, placar: { J1: 0, J2: 0 }
    });
    for (const side of SIDES) {
      const p = state.jogadores[side];
      if (p.mao.length > 5) fail('Mão excede cinco cartas.');
      if (state.fase === 'SUPORTE' && !state.jogadores[side].campo)
        fail('Suporte exige ambas as criaturas preparadas.');
    }
    return state;
  }

  function randomIndex(upper) {
    if (!Number.isSafeInteger(upper) || upper < 1 || upper > 40)
      fail('Intervalo de sorteio inválido.');
    if (typeof crypto === 'undefined' || !crypto.getRandomValues)
      fail('Sorteio seguro do navegador indisponível.');
    const range = 0x100000000, limit = range - range % upper;
    const numbers = new Uint32Array(1);
    let value;
    do { crypto.getRandomValues(numbers); value = numbers[0]; } while (value >= limit);
    return value % upper;
  }

  function pick(upper, random) {
    const index = random(upper);
    if (!Number.isSafeInteger(index) || index < 0 || index >= upper)
      fail('Sorteador produziu índice inválido.');
    return index;
  }
  function shuffle(stack, random) {
    for (let i = stack.length - 1; i > 0; i--) {
      const j = pick(i + 1, random);
      [stack[i], stack[j]] = [stack[j], stack[i]];
    }
  }
  function draw(player, quantity) {
    for (let i = 0; i < quantity; i++) player.mao.push(player.monte.pop());
  }
  function start(catalog, csvHuman, csvIA, random = randomIndex) {
    if (!decks || !(catalog instanceof Map) || !catalog.size)
      fail('Catálogo SRD precisa estar carregado.');
    if (typeof random !== 'function') fail('Sorteador inválido.');
    const human = decks.importDeck(csvHuman, catalog, 'J1');
    const ai = decks.importDeck(csvIA, catalog, 'J2', human);
    const draft = zones.newDraft({ J1: human, J2: ai });
    const first = pick(2, random) === 0 ? 'J1' : 'J2';
    const next = {
      schema: 1, modo: MODE, ambiente: 'LOCAL_BROWSER_NAO_COMPETITIVO',
      versao: 1, fase: 'TROCA', vez: first, primeiro: first,
      ciclo: 1, placar: { J1: 0, J2: 0 }, combate: null,
      inventario: draft.inventario, jogadores: draft.jogadores,
      historico: [{
        id: 'INICIO_LOCAL', versao: 1, acao: 'ABERTURA',
        detalhe: 'Dois montes embaralhados no dispositivo; 5 cartas por lado. Sorteio local não auditável externamente.'
      }]
    };
    for (const side of SIDES) {
      shuffle(next.jogadores[side].monte, random);
      draw(next.jogadores[side], 5);
    }
    return check(next);
  }
  function requireTurn(state, side, expectedVersion, id, phase) {
    check(state);
    if (state.fase !== phase || state.vez !== side)
      fail('Ação fora da fase ou da vez.');
    if (state.versao !== expectedVersion)
      fail('Versão obsoleta: atualize a partida local.');
    if (!validId(id) || state.historico.some(e => e.id === id))
      fail('Evento inválido ou já executado.');
  }
  function commit(state, id, acao, side, detail, mutate) {
    const next = clone(state);
    mutate(next);
    next.versao++;
    next.historico.push({
      id, versao: next.versao, acao, jogador: side, detalhe: detail
    });
    return check(next);
  }
  function exchange(state, side, ids, expectedVersion, id) {
    requireTurn(state, side, expectedVersion, id, 'TROCA');
    if (!Array.isArray(ids) || ids.length > 5 ||
        ids.some(x => typeof x !== 'string') || new Set(ids).size !== ids.length)
      fail('Troca exige de 0 a 5 IDs distintos.');
    const p = state.jogadores[side];
    if (ids.some(x => !p.mao.some(c => c.copiaId === x)))
      fail('Só é possível descartar cartas da própria mão.');
    if (p.monte.length < ids.length)
      fail('PENDENTE Q-06: monte insuficiente para comprar na troca.');
    return commit(state, id, 'TROCA', side, ids.length + ' carta(s) trocada(s)', next => {
      const player = next.jogadores[side];
      const selected = new Set(ids);
      player.cemiterio.push(...player.mao.filter(c => selected.has(c.copiaId)));
      player.mao = player.mao.filter(c => !selected.has(c.copiaId));
      draw(player, ids.length);
      next.vez = side === next.primeiro ? other(side) : next.primeiro;
      if (side !== next.primeiro) next.fase = 'CRIATURA';
    });
  }
  function legalCreature(player, candidate) {
    if (decks.rarity(candidate.nd) !== candidate.raridade)
      fail('Raridade divergente do ND no catálogo.');
    if (candidate.ca === null || candidate.pvMax === null)
      fail('PENDENTE: CA e PV completos não disponíveis na ficha.');
    if (!player.campo) {
      if (candidate.raridade !== 'Comum') fail('Invocação direta exige Comum.');
    } else if (candidate.tipo !== player.campo.tipo ||
        RARITIES.indexOf(candidate.raridade) !== RARITIES.indexOf(player.campo.raridade) + 1) {
      fail('Evolução exige mesmo tipo e raridade imediatamente superior.');
    }
  }
  function play(state, side, copyId, expectedVersion, id) {
    requireTurn(state, side, expectedVersion, id, 'CRIATURA');
    const player = state.jogadores[side];
    const candidate = player.mao.find(c => c.copiaId === copyId);
    if (!candidate) fail('Cópia ausente da própria mão.');
    legalCreature(player, candidate);
    return commit(state, id, player.campo ? 'EVOLUCAO' : 'INVOCACAO',
      side, candidate.nome + ' (' + candidate.copiaId + ')', next => {
        const p = next.jogadores[side];
        p.mao = p.mao.filter(c => c.copiaId !== copyId);
        if (p.campo) p.cemiterio.push(p.campo);
        p.campo = { ...candidate, pvAtual: candidate.pvMax };
      });
  }
  function finishCreature(state, side, expectedVersion, id) {
    requireTurn(state, side, expectedVersion, id, 'CRIATURA');
    if (!state.jogadores[side].campo) fail('PENDENTE: nenhuma criatura ativa para prosseguir.');
    return commit(state, id, 'FIM_CRIATURA', side, 'Preparação concluída', next => {
      next.vez = side === next.primeiro ? other(side) : next.primeiro;
      if (side !== next.primeiro) next.fase = 'SUPORTE';
    });
  }
  function noSupport(state, side, expectedVersion, id) {
    requireTurn(state, side, expectedVersion, id, 'SUPORTE');
    return commit(state, id, 'SEM_SUPORTE', side, 'Nenhuma carta reservada ou consumida', next => {
      next.vez = side === next.primeiro ? other(side) : null;
      if (side !== next.primeiro) next.fase = 'COMBATE_PENDENTE';
    });
  }

  // Somente Cat/Owl/Giant Owl (fichas SRD 5.2.1 verificadas) podem avançar
  // do estado de preparação para o combate; demais perfis ficam pendentes.
  function beginCombat(state, expectedVersion, id, rng = randomIndex) {
    check(state);
    if (state.fase !== 'COMBATE_PENDENTE')
      fail('A iniciativa só ocorre após ambos escolherem suporte.');
    if (state.versao !== expectedVersion)
      fail('Versão obsoleta: atualize a partida local.');
    if (!validId(id) || state.historico.some(e => e.id === id))
      fail('Evento inválido ou já executado.');
    if (!combat) fail('Motor SRD parcial indisponível.');
    const order = combat.initiative(
      state.jogadores.J1.campo, state.jogadores.J2.campo, rng);
    return commit(state, id,
      order.empate ? 'INICIATIVA_EMPATE_PENDENTE' : 'INICIATIVA_SRD_PARCIAL',
      null,
      'Perfis SRD parciais · J1 d20 ' + order.valores.J1.d20 + ' + ' +
      order.valores.J1.modificador + ' = ' + order.valores.J1.total +
      '; J2 d20 ' + order.valores.J2.d20 + ' + ' +
      order.valores.J2.modificador + ' = ' + order.valores.J2.total +
      (order.empate ? ' · EMPATE: pendente de regra, sem rerrolagem' : '') +
      ' · sorteio local não auditável externamente', next => {
        next.combate = {
          numero: next.ciclo, rodada: order.empate ? 0 : 1,
          indice: order.empate ? null : 0,
          ordem: order.ordem, iniciativas: order.valores,
          cobertura: 'SRD521_CAT_OWL_GIANT_OWL_ATAQUES_PARCIAIS'
        };
        next.fase = order.empate ? 'INICIATIVA_EMPATE_PENDENTE' : 'COMBATE';
        next.vez = order.empate ? null : order.ordem[0];
      });
  }

  function attack(state, side, expectedVersion, id, rng = randomIndex) {
    requireTurn(state, side, expectedVersion, id, 'COMBATE');
    if (!combat) fail('Motor SRD parcial indisponível.');
    const enemy = other(side);
    const result = combat.attack(
      state.jogadores[side].campo, state.jogadores[enemy].campo, rng);
    const victim = state.jogadores[enemy].campo;
    const lethal = result.acerto && victim.pvAtual <= result.dano;
    const detail = result.ataque + ': d20 ' + result.d20 + ' + ' +
      result.bonus + ' = ' + result.total + ' vs CA ' + result.caAlvo +
      '; ' + (result.acerto ? 'acertou' : 'errou') +
      (result.critico ? ' (crítico; dano fixo)' : '') +
      '; dano ' + (result.danoComDados ?
        result.dadosDano.join(' + ') + ' + ' + result.modificadorDano +
        ' = ' + result.danoBruto : String(result.danoBruto) + ' fixo') +
      ' ' + result.tipoDano + (result.resistenciaAplicada ?
        '; resistência: ' + result.dano + ' efetivo' : '') +
      (lethal ? '; KO de ' + victim.nome + '; +1 ponto ' + side : '') +
      '; sorteio local não auditável externamente';
    return commit(state, id, 'ATAQUE_SRD_PARCIAL', side, detail, next => {
      const defender = next.jogadores[enemy];
      defender.campo.pvAtual = Math.max(0, defender.campo.pvAtual - result.dano);
      if (defender.campo.pvAtual === 0) {
        defender.cemiterio.push(defender.campo);
        defender.campo = null;
        next.placar[side]++;
        next.fase = next.placar[side] === 3 ? 'ENCERRADA' : 'INICIO_CICLO_PENDENTE';
        next.vez = null;
      } else {
        next.combate.indice = 1 - next.combate.indice;
        if (next.combate.indice === 0) next.combate.rodada++;
        next.vez = next.combate.ordem[next.combate.indice];
      }
    });
  }

  function beginCycle(state, expectedVersion, id) {
    check(state);
    if (state.fase !== 'INICIO_CICLO_PENDENTE')
      fail('Não há novo ciclo liberado após o combate.');
    if (state.versao !== expectedVersion)
      fail('Versão obsoleta: atualize a partida local.');
    if (!validId(id) || state.historico.some(e => e.id === id))
      fail('Evento inválido ou já executado.');
    return commit(state, id, 'INICIO_CICLO', null,
      'Reposição até cinco para ambos (sem sexta carta, sem curar sobrevivente)', next => {
        for (const side of SIDES) {
          const p = next.jogadores[side];
          draw(p, Math.min(5 - p.mao.length, p.monte.length));
        }
        next.ciclo++;
        next.combate = null;
        next.fase = 'TROCA';
        next.vez = next.primeiro;
      });
  }

  function aiStep(state) {
    check(state);
    if (state.vez !== 'J2') fail('IA não pode agir fora da própria vez.');
    const id = 'IA_V' + (state.versao + 1);
    if (state.fase === 'TROCA') return exchange(state, 'J2', [], state.versao, id);
    if (state.fase === 'SUPORTE') return noSupport(state, 'J2', state.versao, id);
    if (state.fase === 'COMBATE') return attack(state, 'J2', state.versao, id);
    if (state.fase !== 'CRIATURA') fail('IA sem ação disponível.');
    const p = state.jogadores.J2;
    const choice = p.mao.find(c => c.ca !== null && c.pvMax !== null &&
      decks.rarity(c.nd) === c.raridade &&
      (!p.campo ? c.raridade === 'Comum' :
        c.tipo === p.campo.tipo &&
        RARITIES.indexOf(c.raridade) === RARITIES.indexOf(p.campo.raridade) + 1));
    if (choice) return play(state, 'J2', choice.copiaId, state.versao, id);
    if (!p.campo) fail('PENDENTE: IA sem Comum invocável com ficha válida; não existe regra de derrota automática.');
    return finishCreature(state, 'J2', state.versao, id);
  }
  function publico(state) {
    check(state);
    const players = {};
    for (const side of SIDES) {
      const p = state.jogadores[side];
      players[side] = {
        monte: p.monte.length, mao: p.mao.length,
        cemiterio: p.cemiterio.length,
        campo: p.campo && {
          copiaId: p.campo.copiaId, nome: p.campo.nome, tipo: p.campo.tipo,
          nd: p.campo.nd, raridade: p.campo.raridade, ca: p.campo.ca,
          pvAtual: p.campo.pvAtual, pvMax: p.campo.pvMax,
          imagem: p.campo.imagem
        }
      };
    }
    return {
      modo: MODE, versao: state.versao, ciclo: state.ciclo, fase: state.fase,
      vez: state.vez, primeiro: state.primeiro, placar: clone(state.placar),
      combate: state.combate ? clone(state.combate) : null,
      jogadores: players, maoHumano: clone(state.jogadores.J1.mao),
      historico: clone(state.historico)
    };
  }
  return {
    MODE, check, start, exchange, play, finishCreature, noSupport,
    aiStep, beginCombat, attack, beginCycle, publico
  };
});

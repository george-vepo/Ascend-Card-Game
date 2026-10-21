/* Etapa 4 — interface de teste sintético, sem catálogo, deck ou mãos reais. */
(function (root, factory) {
  const node = typeof module === 'object' && module.exports;
  const zones = node ? require('./zones-core.js') : root && root.SRDZonesDemo;
  const exchange = node ? require('./draw-exchange-fixtures.js') : root && root.SRDDrawExchangeFixtures;
  const prepare = node ? require('./creature-preparation-fixtures.js') : root && root.SRDCreaturePreparationFixtures;
  const api = factory(zones, exchange, prepare);
  if (node) module.exports = api;
  if (root) {
    root.SRDFixtureLab = api;
    if (root.document) {
      const boot = () => api.mount(root.document);
      if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', boot);
      else boot();
    }
  }
})(typeof window !== 'undefined' ? window : null, function (zones, exchange, prepare) {
  'use strict';

  const fail = text => { throw new Error(text); };
  const COPY_PREFIX = 'SINTETICO';
  const sideId = (side, index) => side + '-' + COPY_PREFIX + '-' + String(index).padStart(2, '0');

  // Estes marcadores não pertencem ao Catálogo SRD e jamais devem ser usados numa partida.
  function syntheticDeck(side) {
    if (!['J1', 'J2'].includes(side)) fail('Jogador sintético inválido.');
    return Array.from({ length: 40 }, (_, index) => {
      const rarity = index === 38 ? ['Incomum', '6', 30] :
        index === 37 ? ['Rara', '11', 40] : ['Comum', '5', 20];
      return {
        copiaId: sideId(side, index), catalogoId: 'FICTICIO-' + index,
        nome: 'Marcador fictício de teste', tipo: 'Aberração',
        raridade: rarity[0], nd: rarity[1],
        ca: 10, pvMax: rarity[2], imagem: '', fichaUrl: ''
      };
    });
  }

  function start() {
    if (!zones || !exchange || !prepare) fail('Módulos de teste ausentes.');
    const draft = zones.newDraft({ J1: syntheticDeck('J1'), J2: syntheticDeck('J2') });
    return exchange.startFixture(draft, 'J1', exchange.MODE);
  }

  function ensure(state, expectedVersion) {
    zones.check(state);
    if (state.simulacao?.modo !== exchange.MODE || state.simulacao.primeiro !== 'J1')
      fail('Somente dados sintéticos locais são permitidos.');
    if (!Number.isSafeInteger(expectedVersion) || expectedVersion !== state.versao)
      fail('Versão obsoleta da demonstração.');
  }

  function nextAction(state) {
    ensure(state, state?.versao);
    const sim = state.simulacao;
    if (sim.etapa === 'TROCA') return sim.vez === 'J1' ?
      'J1: trocar 1 marcador sintético' : 'J2: confirmar troca de 0 marcadores';
    if (sim.etapa === 'PREPARACAO_NAO_IMPLEMENTADA') return 'Iniciar preparação sintética';
    if (sim.etapa === 'CRIATURA') {
      const side = sim.vez;
      if (!['J1', 'J2'].includes(side)) fail('Turno sintético inválido.');
      const active = state.jogadores[side].campo;
      if (!active) return side + ': invocar marcador Comum';
      if (active.raridade === 'Comum') return side + ': evoluir para Incomum';
      if (side === 'J1' && active.raridade === 'Incomum')
        return side + ': evoluir para Rara';
      return side + ': encerrar preparação';
    }
    if (sim.etapa === 'SUPORTE_NAO_IMPLEMENTADO')
      return null;
    fail('Fase não suportada pelo laboratório.');
  }

  function step(state, expectedVersion) {
    ensure(state, expectedVersion);
    const action = nextAction(state);
    if (action === null) fail('O laboratório termina antes dos suportes e do combate.');
    const sim = state.simulacao;
    if (sim.etapa === 'TROCA') {
      // Um marcador descartado apenas para mostrar a operação; nenhum ID oculto é exibido.
      const ids = sim.vez === 'J1' ? [sideId('J1', 35)] : [];
      return exchange.exchangeFixture(state, sim.vez, ids, state.versao);
    }
    if (sim.etapa === 'PREPARACAO_NAO_IMPLEMENTADA')
      return prepare.beginFixture(state, state.versao);
    const side = sim.vez;
    const field = state.jogadores[side].campo;
    if (!field) return prepare.playFixture(state, side, sideId(side, 39), state.versao);
    if (field.raridade === 'Comum')
      return prepare.playFixture(state, side, sideId(side, 38), state.versao);
    if (side === 'J1' && field.raridade === 'Incomum')
      return prepare.playFixture(state, side, sideId(side, 37), state.versao);
    return prepare.finishFixture(state, side, state.versao);
  }

  // Lista explícita de campos públicos: nunca devolver mão, inventário nem ordem do monte.
  function publicView(state) {
    ensure(state, state?.versao);
    const source = zones.publico(state);
    const result = {};
    for (const side of ['J1', 'J2']) {
      const p = source.jogadores[side];
      const c = p.campo;
      result[side] = {
        monte: p.monte, mao: p.mao, cemiterio: p.cemiterio,
        campo: c === null ? null : {
          nome: c.nome, copiaId: c.copiaId, tipo: c.tipo, nd: c.nd,
          raridade: c.raridade, ca: c.ca, pvAtual: c.pvAtual, pvMax: c.pvMax
        }
      };
    }
    return {
      ambiente: 'LABORATORIO_FICTICIO_SEM_PARTIDA',
      versao: source.versao,
      placar: { J1: source.placar.J1, J2: source.placar.J2 },
      fase: state.simulacao.etapa, vez: state.simulacao.vez,
      jogadores: result, proximaAcao: nextAction(state)
    };
  }

  function mount(document) {
    const $ = id => document.getElementById(id);
    if (!$('lab-next') || !$('lab-reset')) return;
    let state = null;
    const feedback = $('lab-feedback');

    function render() {
      const view = state === null ? null : publicView(state);
      $('lab-phase').textContent = view ? view.fase : 'NÃO INICIADO';
      $('lab-turn').textContent = view ? (view.vez || '—') : '—';
      $('lab-version').textContent = view ? 'V' + view.versao : '—';
      for (const side of ['J1', 'J2']) {
        const s = side.toLowerCase(), data = view?.jogadores[side];
        const c = data?.campo;
        $('lab-name-' + s).textContent = c ? c.nome : 'Campo vazio';
        $('lab-id-' + s).textContent = c ? c.copiaId : '—';
        $('lab-info-' + s).textContent = c ?
          c.tipo + ' · ND ' + c.nd + ' · ' + c.raridade : 'Sem criatura invocada';
        $('lab-stats-' + s).textContent = c ?
          'CA ' + c.ca + ' · PV ' + c.pvAtual + '/' + c.pvMax : 'CA — · PV —';
        $('lab-count-' + s).textContent = data ?
          'Monte ' + data.monte + ' · Mão ' + data.mao + ' · Cemitério ' + data.cemiterio :
          'Monte — · Mão — · Cemitério —';
        $('lab-score-' + s).textContent = view ? String(view.placar[side]) : '0';
      }
      const action = view?.proximaAcao;
      $('lab-next').disabled = view !== null && action === null;
      $('lab-next').textContent = view === null ? 'Iniciar laboratório sintético' :
        action === null ? 'Fim da demonstração (suportes não implementados)' :
        'Próximo passo: ' + action;
      $('lab-summary').textContent = view === null ?
        'Nenhuma fixture iniciada. A execução ocorre somente nesta página.' :
        'Fixture pública V' + view.versao + '. Cartas do teste: 40 por lado, placar 0 × 0.';
    }

    $('lab-next').addEventListener('click', () => {
      try {
        state = state === null ? start() : step(state, state.versao);
        feedback.textContent = 'Transição sintética validada; não é jogada oficial.';
        render();
      } catch (error) {
        feedback.textContent = 'Operação bloqueada: ' + error.message;
      }
    });
    $('lab-reset').addEventListener('click', () => {
      state = null;
      feedback.textContent = 'Laboratório reiniciado. Nenhum dado oficial foi afetado.';
      render();
    });
    render();
  }

  return { start, step, nextAction, publicView, mount };
});

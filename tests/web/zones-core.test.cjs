'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const zones = require('../../web/pages/zones-core.js');
const creature = (side, index) => ({
  copiaId: side + '-' + String(index).padStart(2, '0'),
  catalogoId: 'AT-002', nome: 'Roper', tipo: 'Aberração', nd: '5',
  raridade: 'Comum', ca: 20, pvMax: 93, imagem: '', fichaUrl: ''
});
const deck = side => Array.from({ length: 40 }, (_, i) => creature(side, i));
const decks = () => ({ J1: deck('J1'), J2: deck('J2') });
const draft = () => zones.newDraft(decks());
const moveToHand = (state, side) => {
  state.jogadores[side].mao.push(state.jogadores[side].monte.pop());
};

test('cria rascunho sem embaralhar, comprar ou iniciar combate', () => {
  const state = draft();
  assert.equal(state.estagio, 'RASCUNHO_ZONAS');
  assert.equal(state.ambiente, 'DEMO_LOCAL_NAO_OFICIAL');
  for (const side of ['J1', 'J2']) {
    assert.equal(state.jogadores[side].monte.length, 40);
    assert.equal(state.jogadores[side].mao.length, 0);
    assert.equal(state.jogadores[side].cemiterio.length, 0);
    assert.equal(state.jogadores[side].campo, null);
  }
  assert.equal(state.jogadores.J1.monte[0].copiaId, 'J1-00');
  assert.deepEqual(state.placar, { J1: 0, J2: 0 });
});

test('permite 40 cópias de um mesmo catálogo com identidades distintas', () => {
  const state = draft();
  assert.equal(new Set(state.jogadores.J1.monte.map(c => c.catalogoId)).size, 1);
  assert.equal(new Set(state.jogadores.J1.monte.map(c => c.copiaId)).size, 40);
  assert.equal(zones.check(state), state);
});

test('não modifica os decks de entrada', () => {
  const source = decks(), snapshot = JSON.stringify(source);
  const state = zones.newDraft(source);
  state.jogadores.J1.monte[0].nome = 'alterado';
  assert.equal(JSON.stringify(source), snapshot);
});

test('recusa decks com 39 ou 41 cartas', () => {
  for (const count of [39, 41]) {
    const input = decks(); input.J2.length = count;
    assert.throws(() => zones.newDraft(input), /40 cópias/);
  }
});

test('recusa identidade duplicada no mesmo jogador e entre jogadores', () => {
  const local = decks(); local.J1[1].copiaId = local.J1[0].copiaId;
  assert.throws(() => zones.newDraft(local), /duplicado/);
  const across = decks(); across.J2[0].copiaId = across.J1[0].copiaId;
  assert.throws(() => zones.newDraft(across), /duplicado/);
});

test('conserva exatamente 40 cartas após movimentação legítima entre zonas', () => {
  const state = draft();
  moveToHand(state, 'J1');
  const c = state.jogadores.J1.mao.pop();
  state.jogadores.J1.campo = { ...c, pvAtual: 93 };
  assert.equal(zones.check(state), state);
  state.jogadores.J1.cemiterio.push({ ...state.jogadores.J1.campo, pvAtual: 0 });
  state.jogadores.J1.campo = null;
  assert.equal(zones.check(state), state);
});

test('recusa perda e duplicidade de carta entre mão, monte e cemitério', () => {
  const missing = draft(); missing.jogadores.J1.monte.pop();
  assert.throws(() => zones.check(missing), /soma das zonas/);
  const doubled = draft();
  moveToHand(doubled, 'J1');
  doubled.jogadores.J1.monte[0] = { ...doubled.jogadores.J1.mao[0] };
  assert.throws(() => zones.check(doubled), /duplicado/);
});

test('não aceita substituição por outra cópia mantendo a contagem de 40', () => {
  const state = draft();
  state.jogadores.J1.monte[0].copiaId = 'J1-FAKE';
  assert.throws(() => zones.check(state), /substituída/);
});

test('não aceita alteração de catálogo ou atributos da identidade', () => {
  const state = draft();
  state.jogadores.J1.monte[0].catalogoId = 'AT-999';
  assert.throws(() => zones.check(state), /identidade alterada/);
  const changed = draft();
  changed.jogadores.J2.monte[0].pvMax = 500;
  assert.throws(() => zones.check(changed), /identidade alterada/);
});

test('só aceita criatura em campo com PV atuais válidos e ficha conhecida', () => {
  for (const pvAtual of [0, 94, -1, null]) {
    const state = draft();
    const card = state.jogadores.J1.monte.pop();
    state.jogadores.J1.campo = { ...card, pvAtual };
    assert.throws(() => zones.check(state), /PV da criatura/);
  }
});

test('resumo público protege as mãos e os inventários completos', () => {
  const state = draft(); moveToHand(state, 'J1'); moveToHand(state, 'J2');
  const publicView = zones.publico(state);
  assert.equal(publicView.jogadores.J1.mao, 1);
  assert.equal(publicView.jogadores.J2.mao, 1);
  assert.equal(JSON.stringify(publicView).includes('J1-39'), false);
  assert.equal(JSON.stringify(publicView).includes('J2-39'), false);
  assert.equal('inventario' in publicView, false);
  assert.equal(Array.isArray(publicView.jogadores.J1.mao), false);
});

test('resumo público mostra só atributos conhecidos da criatura ativa', () => {
  const state = draft();
  const c = state.jogadores.J1.monte.pop();
  state.jogadores.J1.campo = { ...c, pvAtual: 13, segredoInterno: 'não divulgar' };
  const publicView = zones.publico(state);
  assert.equal(publicView.jogadores.J1.campo.pvAtual, 13);
  assert.equal(JSON.stringify(publicView).includes('segredoInterno'), false);
  assert.equal(JSON.stringify(publicView).includes('não divulgar'), false);
});

test('mão privada é exclusiva do jogador e é cópia independente', () => {
  const state = draft(); moveToHand(state, 'J1'); moveToHand(state, 'J2');
  const hand = zones.privado(state, 'J1');
  assert.equal(hand.length, 1);
  assert.equal(hand[0].copiaId, 'J1-39');
  assert.equal(JSON.stringify(hand).includes('J2-39'), false);
  hand[0].nome = 'não altera estado';
  assert.equal(state.jogadores.J1.mao[0].nome, 'Roper');
  assert.throws(() => zones.privado(state, 'J3'), /Jogador inválido/);
});

test('não permite apresentar o rascunho como partida já pontuada', () => {
  const state = draft(); state.placar.J1 = 1;
  assert.throws(() => zones.check(state), /Rascunho local inválido/);
});

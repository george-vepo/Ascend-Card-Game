'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const zones = require('../../web/pages/zones-core.js');
const fixtures = require('../../web/pages/draw-exchange-fixtures.js');

const makeDeck = side => Array.from({ length: 40 }, (_, i) => ({
  copiaId: side + '-' + String(i).padStart(2, '0'),
  catalogoId: 'AT-002', nome: 'Roper', tipo: 'Aberração',
  nd: '5', raridade: 'Comum', ca: 20, pvMax: 93
}));
const draft = () => zones.newDraft({ J1: makeDeck('J1'), J2: makeDeck('J2') });
const start = (side = 'J1') => fixtures.startFixture(draft(), side, fixtures.MODE);
const ids = (state, side, n) => state.jogadores[side].mao.slice(0, n).map(c => c.copiaId);

test('somente marcador explícito de fixture libera abertura sintética', () => {
  assert.throws(() => fixtures.startFixture(draft(), 'J1'), /Somente testes sintéticos/);
  assert.throws(() => fixtures.startFixture(draft(), 'J3', fixtures.MODE), /Ordem sintética/);
});

test('abertura sintética retira cinco cartas de cada topo, sem embaralhar', () => {
  const state = start();
  assert.deepEqual(state.jogadores.J1.mao.map(c => c.copiaId),
    ['J1-39','J1-38','J1-37','J1-36','J1-35']);
  assert.deepEqual(state.jogadores.J2.mao.map(c => c.copiaId),
    ['J2-39','J2-38','J2-37','J2-36','J2-35']);
  assert.equal(state.jogadores.J1.monte.length, 35);
  assert.equal(state.jogadores.J2.monte.length, 35);
  assert.equal(state.simulacao.primeiro, 'J1');
  assert.equal(state.simulacao.vez, 'J1');
  zones.check(state);
});

test('abertura não modifica rascunho, sorteia ou pontua', () => {
  const source = draft();
  const before = JSON.stringify(source);
  const state = fixtures.startFixture(source, 'J2', fixtures.MODE);
  assert.equal(JSON.stringify(source), before);
  assert.equal(source.versao, 0);
  assert.equal(state.simulacao.vez, 'J2');
  assert.deepEqual(state.placar, {J1:0,J2:0});
  assert.equal('combate' in state, false);
});

test('abertura duplicada no mesmo estado é rejeitada sem alterações', () => {
  const state = start();
  const before = JSON.stringify(state);
  assert.throws(() => fixtures.startFixture(state, 'J1', fixtures.MODE), /já inicializado/);
  assert.equal(JSON.stringify(state), before);
});

test('troca zero passa a vez sem consumir ou comprar carta', () => {
  const s = start(), next = fixtures.exchangeFixture(s, 'J1', [], s.versao);
  assert.equal(s.simulacao.vez, 'J1');
  assert.equal(next.simulacao.vez, 'J2');
  assert.equal(next.jogadores.J1.mao.length, 5);
  assert.equal(next.jogadores.J1.monte.length, 35);
  assert.equal(next.jogadores.J1.cemiterio.length, 0);
  assert.equal(next.versao, s.versao + 1);
  assert.equal(next.simulacao.eventos.at(-1).compradas, 0);
});

test('troca de cinco movimenta as cópias para cemitério e compra cinco do topo', () => {
  const s = start();
  const selected = ids(s,'J1',5);
  const next = fixtures.exchangeFixture(s,'J1',selected,s.versao);
  assert.deepEqual(next.jogadores.J1.cemiterio.map(c => c.copiaId), selected);
  assert.deepEqual(next.jogadores.J1.mao.map(c => c.copiaId),
    ['J1-34','J1-33','J1-32','J1-31','J1-30']);
  assert.equal(next.jogadores.J1.monte.length,30);
  assert.equal(next.jogadores.J1.mao.length,5);
  assert.equal(s.jogadores.J1.cemiterio.length,0);
  zones.check(next);
});

test('troca parcial preserva cartas não escolhidas na mão', () => {
  const s = start();
  const next = fixtures.exchangeFixture(s,'J1',ids(s,'J1',2),s.versao);
  assert.deepEqual(next.jogadores.J1.mao.map(c => c.copiaId),
    ['J1-37','J1-36','J1-35','J1-34','J1-33']);
  assert.equal(next.jogadores.J1.cemiterio.length,2);
  zones.check(next);
});

test('ordem fixa PRIMEIRO depois SEGUNDO finaliza apenas a troca', () => {
  const s = start('J2');
  assert.throws(() => fixtures.exchangeFixture(s,'J1',[],s.versao), /fora da ordem/);
  const first = fixtures.exchangeFixture(s,'J2',[],s.versao);
  const second = fixtures.exchangeFixture(first,'J1',[],first.versao);
  assert.equal(second.simulacao.etapa,'PREPARACAO_NAO_IMPLEMENTADA');
  assert.equal(second.simulacao.vez,null);
  assert.throws(() => fixtures.exchangeFixture(second,'J2',[],second.versao), /Não existe troca/);
});

test('versão obsoleta e repetição de ação após avanço são rejeitadas', () => {
  const s = start();
  const next = fixtures.exchangeFixture(s,'J1',[],s.versao);
  const snapshot = JSON.stringify(next);
  assert.throws(() => fixtures.exchangeFixture(next,'J2',[],s.versao), /Versão obsoleta/);
  assert.throws(() => fixtures.exchangeFixture(next,'J1',[],next.versao), /fora da ordem/);
  assert.equal(JSON.stringify(next),snapshot);
});

test('troca bloqueia ID ausente, repetido ou de outro jogador', () => {
  const s = start(), original = JSON.stringify(s);
  assert.throws(() => fixtures.exchangeFixture(s,'J1',['J1-X'],s.versao), /própria mão/);
  assert.throws(() => fixtures.exchangeFixture(s,'J1',['J2-39'],s.versao), /própria mão/);
  assert.throws(() => fixtures.exchangeFixture(s,'J1',['J1-39','J1-39'],s.versao), /distintos/);
  assert.equal(JSON.stringify(s), original);
});

test('troca bloqueia mais de cinco ou parâmetros malformados', () => {
  const s = start();
  assert.throws(() => fixtures.exchangeFixture(s,'J1',['a','b','c','d','e','f'],s.versao), /0 a 5/);
  assert.throws(() => fixtures.exchangeFixture(s,'J1',null,s.versao), /0 a 5/);
  assert.throws(() => fixtures.exchangeFixture(s,'J1',[undefined],s.versao), /0 a 5/);
});

test('monte insuficiente para trocar permanece PENDENTE sem descartar', () => {
  const s = start();
  const p = s.jogadores.J1;
  p.cemiterio.push(...p.monte.splice(0, 32));
  zones.check(s);
  const snapshot = JSON.stringify(s);
  assert.throws(() => fixtures.exchangeFixture(s,'J1',ids(s,'J1',5),s.versao),
    /PENDENTE.*Q-06/);
  assert.equal(JSON.stringify(s),snapshot);
});

test('sem sexta carta: mão permanece em cinco mesmo ao trocar cinco', () => {
  const s = start();
  const next = fixtures.exchangeFixture(s,'J1',ids(s,'J1',5),s.versao);
  assert.equal(next.jogadores.J1.mao.length,5);
  assert.equal(next.jogadores.J2.mao.length,5);
});

test('projeção pública não expõe IDs de mãos, montes e eventos', () => {
  const s = start();
  const n = fixtures.exchangeFixture(s,'J1',ids(s,'J1',1),s.versao);
  const preview = fixtures.publico(n);
  assert.equal(preview.jogadores.J1.mao,5);
  assert.equal(preview.jogadores.J2.mao,5);
  assert.equal(preview.simulacao.vez,'J2');
  assert.equal('eventos' in preview.simulacao, false);
  assert.equal(JSON.stringify(preview).includes('J1-39'), false);
  assert.equal(JSON.stringify(preview).includes('J2-39'), false);
});

test('o módulo não exporta mutações de partida oficial', () => {
  assert.deepEqual(Object.keys(fixtures).sort(),
    ['MODE','exchangeFixture','publico','startFixture'].sort());
});

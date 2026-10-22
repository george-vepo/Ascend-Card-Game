'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const engine = require('../../web/pages/local-match-core.js');
const zones = require('../../web/pages/zones-core.js');
const importer = require('../../web/pages/decks-core.js');

// Catálogo isolado SOMENTE para testes. Não cria cartas canônicas de produção.
const catalog = new Map([
  ['TEST-C', { id: 'TEST-C', nome: 'Marcador comum de teste',
    tipo: 'Aberração', nd: '5', raridade: 'Comum', ca: 12, pvMax: 21 }],
  ['TEST-I', { id: 'TEST-I', nome: 'Marcador incomum de teste',
    tipo: 'Aberração', nd: '6', raridade: 'Incomum', ca: 14, pvMax: 29 }],
  ['TEST-W', { id: 'TEST-W', nome: 'Marcador tipo diferente',
    tipo: 'Celestial', nd: '6', raridade: 'Incomum', ca: 15, pvMax: 32 }]
]);
const csv = side => 'copia_id;catalogo_id\n' +
  Array.from({ length: 40 }, (_, i) =>
    side + '-C' + String(i + 1).padStart(2, '0') + ';' +
    (i === 3 ? 'TEST-I' : i === 6 ? 'TEST-W' : 'TEST-C')).join('\n');
const first = () => engine.start(catalog, csv('J1'), csv('J2'), () => 0);
const action = (s, side, kind, arg) => {
  const id = 'E' + (s.versao + 1);
  return kind === 'troca' ? engine.exchange(s, side, arg || [], s.versao, id) :
    kind === 'jogar' ? engine.play(s, side, arg, s.versao, id) :
    kind === 'fim' ? engine.finishCreature(s, side, s.versao, id) :
    engine.noSupport(s, side, s.versao, id);
};
const takeTurn = s => s.vez === 'J2' ? engine.aiStep(s) : action(s, 'J1', 'troca');
const preparedExchange = () => {
  let s = first();
  s = takeTurn(s);
  s = takeTurn(s);
  return s;
};
test('início local valida CSV, sorteia uma vez, embaralha e compra exatamente cinco', () => {
  const s = first();
  assert.equal(s.modo, engine.MODE);
  assert.equal(s.fase, 'TROCA');
  assert.equal(s.primeiro, 'J1');
  assert.equal(s.versao, 1);
  for (const side of ['J1','J2']) {
    assert.equal(s.jogadores[side].monte.length, 35);
    assert.equal(s.jogadores[side].mao.length, 5);
    assert.equal(s.jogadores[side].cemiterio.length, 0);
    assert.equal(new Set(s.inventario[side].map(c => c.copiaId)).size, 40);
  }
  assert.equal(s.placar.J1 + s.placar.J2, 0);
  assert.equal(engine.check(s), s);
});
test('não aceita CSV sem catálogo, cópia duplicada ou RNG inválido', () => {
  assert.throws(() => engine.start(null, csv('J1'), csv('J2'), () => 0), /Catálogo/);
  assert.throws(() => engine.start(catalog, csv('J1'), csv('J1'), () => 0), /duplicado/);
  assert.throws(() => engine.start(catalog, csv('J1'), csv('J2'), () => 40), /Sorteador/);
});
test('não admite importação da fixture como sessão ou estado falso', () => {
  const s = zones.newDraft({
    J1: Array.from({ length: 40 }, (_, i) => ({
      copiaId:'J1-'+i,catalogoId:'FAKE',nome:'Fixture',tipo:'Aberração',
      nd:'5',raridade:'Comum',ca:12,pvMax:21
    })),
    J2: Array.from({ length: 40 }, (_, i) => ({
      copiaId:'J2-'+i,catalogoId:'FAKE',nome:'Fixture',tipo:'Aberração',
      nd:'5',raridade:'Comum',ca:12,pvMax:21
    }))
  });
  assert.throws(() => engine.check(s), /Checkpoint local/);
});
test('troca zero e IA automática sem revelar mão adversária', () => {
  let s = first();
  s = action(s,'J1','troca');
  const next = engine.aiStep(s);
  assert.equal(next.fase, 'CRIATURA');
  assert.equal(next.vez, 'J1');
  assert.equal(next.jogadores.J2.mao.length, 5);
  const view = engine.publico(next);
  assert.equal(view.jogadores.J2.mao, 5);
  assert.equal('mao' in view.jogadores.J2 && Array.isArray(view.jogadores.J2.mao), false);
  assert.equal('monte' in next.jogadores.J2, true);
  assert.equal('inventario' in view, false);
  assert.equal(JSON.stringify(view).includes('J2-C40'), false);
});
test('troca cinco conserva 40 cópias e não cria a sexta carta', () => {
  const s = first(), ids = s.jogadores.J1.mao.map(c=>c.copiaId);
  const next = action(s, 'J1','troca',ids);
  assert.equal(next.jogadores.J1.mao.length, 5);
  assert.equal(next.jogadores.J1.monte.length, 30);
  assert.equal(next.jogadores.J1.cemiterio.length, 5);
  assert.equal(s.jogadores.J1.cemiterio.length, 0);
  engine.check(next);
});
test('ids inválidos, estado velho e execução repetida rejeitados sem mutação', () => {
  const s = first(), snapshot=JSON.stringify(s);
  assert.throws(()=>action(s,'J1','troca',['J2-C12']),/própria mão/);
  assert.throws(()=>engine.exchange(s,'J1',[],0,'ERR'),/Versão obsoleta/);
  const once=action(s,'J1','troca');
  assert.throws(()=>engine.exchange(once,'J1',[],once.versao,'E2'),/Evento inválido|fora da fase/);
  assert.equal(JSON.stringify(s),snapshot);
});
test('invocação Comum e evolução imediata usam a mão e preservam identidades', () => {
  let s = preparedExchange();
  const common=s.jogadores.J1.mao.find(c=>c.raridade==='Comum');
  s=action(s,'J1','jogar',common.copiaId);
  assert.equal(s.jogadores.J1.campo.pvAtual,21);
  const next=s.jogadores.J1.mao.find(c=>c.raridade==='Incomum' && c.tipo==='Aberração');
  if (next) {
    s=action(s,'J1','jogar',next.copiaId);
    assert.equal(s.jogadores.J1.campo.pvAtual,29);
    assert.equal(s.jogadores.J1.cemiterio.at(-1).copiaId,common.copiaId);
  }
  engine.check(s);
});
test('raridade indevida e cópia fora da mão são rejeitadas', () => {
  let s=preparedExchange();
  assert.throws(()=>action(s,'J1','jogar','J1-C999'),/ausente/);
  const rare=s.jogadores.J1.mao.find(c=>c.raridade==='Incomum');
  if (rare) assert.throws(()=>action(s,'J1','jogar',rare.copiaId),/Comum/);
});
test('IA age somente na própria vez, e avança de forma determinística', () => {
  let s=preparedExchange();
  assert.throws(()=>engine.aiStep(s),/fora da própria vez/);
  const common=s.jogadores.J1.mao.find(c=>c.raridade==='Comum');
  s=action(s,'J1','jogar',common.copiaId);
  s=action(s,'J1','fim');
  assert.equal(s.vez,'J2');
  for(let i=0;i<5 && s.vez==='J2';i++) s=engine.aiStep(s);
  assert.equal(s.fase,'SUPORTE');
  assert.equal(s.vez,'J1');
  assert.ok(s.jogadores.J2.campo);
});
test('Sem suporte não descarta e combate permanece bloqueado até motor SRD', () => {
  let s=preparedExchange();
  s=action(s,'J1','jogar',s.jogadores.J1.mao.find(c=>c.raridade==='Comum').copiaId);
  s=action(s,'J1','fim');
  while(s.vez==='J2') s=engine.aiStep(s);
  const j1=s.jogadores.J1.mao.length;
  s=action(s,'J1','suporte');
  s=engine.aiStep(s);
  assert.equal(s.fase,'COMBATE_PENDENTE');
  assert.equal(s.vez,null);
  assert.equal(s.jogadores.J1.mao.length,j1);
  assert.deepEqual(s.placar,{J1:0,J2:0});
  assert.throws(()=>engine.aiStep(s),/fora da própria vez/);
  assert.equal(engine.check(JSON.parse(JSON.stringify(s))).versao,s.versao);
});
test('checkpoint adulterado com duplicação de carta é rejeitado', () => {
  const s=first();s.jogadores.J1.monte[0]=s.jogadores.J1.mao[0];
  assert.throws(()=>engine.check(s),/duplicado/);
});

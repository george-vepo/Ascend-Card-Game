'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const zones = require('../../web/pages/zones-core.js');
const draws = require('../../web/pages/draw-exchange-fixtures.js');
const prep = require('../../web/pages/creature-preparation-fixtures.js');

// Dados marcados como fixtures: não são cartas do catálogo, nem atributos oficiais.
const card = (side, i) => ({
  copiaId: side + '-TEST-' + String(i).padStart(2,'0'),
  catalogoId: 'FIXTURE-' + i, nome: 'TESTE SINTETICO ' + i,
  tipo: 'Aberração', raridade: 'Comum', nd: '5', ca: 10, pvMax: 20
});
function decks() {
  const make = side => Array.from({length:40},(_,i)=>card(side,i));
  const d = {J1:make('J1'),J2:make('J2')};
  for(const side of ['J1','J2']){
    Object.assign(d[side][38],{raridade:'Incomum',nd:'6',pvMax:30});
    Object.assign(d[side][37],{raridade:'Rara',nd:'11',pvMax:40});
    Object.assign(d[side][36],{tipo:'Besta',raridade:'Incomum',nd:'6'});
    Object.assign(d[side][35],{raridade:'Lendária',nd:'16',pvMax:50});
  }
  return d;
}
const open = (decksInput=decks(), first='J1') => draws.startFixture(zones.newDraft(decksInput),first,draws.MODE);
function ready(decksInput=decks(), first='J1'){
  let s=open(decksInput,first);
  s=draws.exchangeFixture(s,first,[],s.versao);
  const second=first==='J1'?'J2':'J1';
  s=draws.exchangeFixture(s,second,[],s.versao);
  return prep.beginFixture(s,s.versao);
}
const id=(side,i)=>side+'-TEST-'+String(i).padStart(2,'0');
const play=(s,side,i)=>prep.playFixture(s,side,id(side,i),s.versao);
const finish=(s,side)=>prep.finishFixture(s,side,s.versao);

test('somente após as duas trocas e sem iniciar uma partida',()=>{
  const s=open();
  assert.throws(()=>prep.beginFixture(s,s.versao),/duas trocas/);
  const afterFirst=draws.exchangeFixture(s,'J1',[],s.versao);
  assert.throws(()=>prep.beginFixture(afterFirst,afterFirst.versao),/duas trocas/);
  const prepared=ready();
  assert.equal(prepared.simulacao.etapa,'CRIATURA');
  assert.equal(prepared.ambiente,'DEMO_LOCAL_NAO_OFICIAL');
  assert.deepEqual(prepared.placar,{J1:0,J2:0});
  assert.equal('combate' in prepared,false);
});

test('preparação segue PRIMEIRO sintético sem novo sorteio',()=>{
  const s=ready(decks(),'J2');
  assert.equal(s.simulacao.primeiro,'J2');
  assert.equal(s.simulacao.vez,'J2');
  assert.equal(s.simulacao.eventos.at(-1).acao,'INICIO_PREPARACAO_SINTETICA');
});

test('invocação inicial exige Comum e move uma única cópia mão->campo',()=>{
  const s=ready();
  const next=play(s,'J1',39);
  assert.equal(next.jogadores.J1.campo.copiaId,id('J1',39));
  assert.equal(next.jogadores.J1.campo.pvAtual,20);
  assert.equal(next.jogadores.J1.mao.length,4);
  assert.equal(next.jogadores.J1.monte.length,35);
  assert.equal(next.jogadores.J1.cemiterio.length,0);
  assert.equal(s.jogadores.J1.campo,null);
  assert.equal(next.versao,s.versao+1);
  assert.equal(next.simulacao.eventos.at(-1).acao,'INVOCACAO_SINTETICA');
  zones.check(next);
});

test('rejeita invocar Incomum, Rara, Lendária ou do jogador adversário',()=>{
  const s=ready(), snapshot=JSON.stringify(s);
  for(const i of [38,37,35])
    assert.throws(()=>play(s,'J1',i),/Somente Comum/);
  assert.throws(()=>prep.playFixture(s,'J1',id('J2',39),s.versao),/próprio jogador/);
  assert.throws(()=>play(s,'J2',39),/fora da vez/);
  assert.equal(JSON.stringify(s),snapshot);
});

test('evolução válida exige mesmo tipo e raridade adjacente',()=>{
  const s=play(ready(),'J1',39);
  const evolved=play(s,'J1',38);
  assert.equal(evolved.jogadores.J1.campo.copiaId,id('J1',38));
  assert.equal(evolved.jogadores.J1.campo.pvAtual,30);
  assert.deepEqual(evolved.jogadores.J1.cemiterio.map(c=>c.copiaId),[id('J1',39)]);
  assert.equal(evolved.jogadores.J1.mao.length,3);
  assert.equal(evolved.jogadores.J1.monte.length,35);
  assert.equal(evolved.simulacao.eventos.at(-1).acao,'EVOLUCAO_SINTETICA');
  zones.check(evolved);
});

test('permite múltiplas evoluções legais na mesma preparação, sem teto fictício',()=>{
  let s=play(ready(),'J1',39);
  s=play(s,'J1',38);
  s=play(s,'J1',37);
  // O tipo da carta de teste de posição 35 é o mesmo; a posição 36 não pode ser usada.
  s=play(s,'J1',35);
  assert.equal(s.jogadores.J1.campo.raridade,'Lendária');
  assert.equal(s.jogadores.J1.campo.pvAtual,50);
  assert.equal(s.jogadores.J1.cemiterio.length,3);
  assert.equal(s.jogadores.J1.mao.length,1);
  assert.equal(s.jogadores.J1.monte.length,35);
  zones.check(s);
});

test('bloqueia salto de raridade e diferença de tipo',()=>{
  const base=play(ready(),'J1',39);
  const snapshot=JSON.stringify(base);
  assert.throws(()=>play(base,'J1',37),/imediatamente superior/);
  assert.throws(()=>play(base,'J1',36),/mesmo tipo/);
  assert.equal(JSON.stringify(base),snapshot);
});

test('não permite evoluir para mesma raridade nem invocar outra Comum no campo',()=>{
  const d=decks();Object.assign(d.J1[35],{raridade:'Comum',nd:'5'});
  const s=play(ready(d),'J1',39);
  assert.throws(()=>play(s,'J1',35),/imediatamente superior/);
});

test('rejeita raridade declarada divergente do ND, sem inventar ficha',()=>{
  const d=decks();d.J1[39].raridade='Mítica';
  const s=ready(d);
  assert.throws(()=>play(s,'J1',39),/inconsistente com ND/);
  const other=decks();other.J1[38].nd='21';
  const q=play(ready(other),'J1',39);
  assert.throws(()=>play(q,'J1',38),/inconsistente com ND/);
});

test('CA ou PV faltante devolvem PENDENTE, preservando todas as zonas',()=>{
  for(const field of ['ca','pvMax']){
    const d=decks();d.J1[39][field]=null;
    const s=ready(d), snapshot=JSON.stringify(s);
    assert.throws(()=>play(s,'J1',39),/PENDENTE/);
    assert.equal(JSON.stringify(s),snapshot);
  }
});

test('a evolução restaura PV máximos da evoluída, sem curar a substituída',()=>{
  const s=play(ready(),'J1',39);
  s.jogadores.J1.campo.pvAtual=3;
  zones.check(s);
  const evolved=play(s,'J1',38);
  assert.equal(evolved.jogadores.J1.cemiterio[0].pvAtual,3);
  assert.equal(evolved.jogadores.J1.campo.pvAtual,30);
});

test('terminar exige criatura ativa, e primeiro passa ao segundo',()=>{
  const s=ready();
  assert.throws(()=>finish(s,'J1'),/criatura ativa/);
  assert.throws(()=>finish(s,'J2'),/fora da vez/);
  const played=play(s,'J1',39);
  const next=finish(played,'J1');
  assert.equal(next.simulacao.vez,'J2');
  assert.equal(next.simulacao.etapa,'CRIATURA');
  assert.deepEqual(next.simulacao.concluidos,['J1']);
  assert.throws(()=>play(next,'J1',38),/fora da vez/);
});

test('segundo prepara e encerra na fronteira: suporte ainda não implementado',()=>{
  let s=play(ready(),'J1',39);
  s=finish(s,'J1');
  s=play(s,'J2',39);
  s=finish(s,'J2');
  assert.equal(s.simulacao.etapa,'SUPORTE_NAO_IMPLEMENTADO');
  assert.equal(s.simulacao.vez,null);
  assert.deepEqual(s.simulacao.concluidos,['J1','J2']);
  assert.throws(()=>play(s,'J2',38),/Fora da preparação/);
  assert.throws(()=>finish(s,'J1'),/Fora da preparação/);
  assert.deepEqual(s.placar,{J1:0,J2:0});
  zones.check(s);
});

test('versões obsoletas são rejeitadas sem operações duplicadas',()=>{
  const s=play(ready(),'J1',39), before=JSON.stringify(s);
  assert.throws(()=>prep.playFixture(s,'J1',id('J1',38),s.versao-1),/Versão obsoleta/);
  const n=play(s,'J1',38);
  assert.throws(()=>prep.playFixture(n,'J1',id('J1',38),n.versao),/próprio jogador/);
  assert.equal(JSON.stringify(s),before);
});

test('não permite começar preparação duas vezes',()=>{
  const s=ready(), before=JSON.stringify(s);
  assert.throws(()=>prep.beginFixture(s,s.versao),/duas trocas/);
  assert.equal(JSON.stringify(s),before);
});

test('previsão pública revela apenas campo e contagens, não a mão adversária',()=>{
  let s=play(ready(),'J1',39);
  const view=prep.publico(s);
  assert.equal(view.jogadores.J1.campo.copiaId,id('J1',39));
  assert.equal(view.jogadores.J1.mao,4);
  assert.equal(view.jogadores.J2.mao,5);
  assert.equal(JSON.stringify(view).includes(id('J2',39)),false);
  assert.equal(JSON.stringify(view).includes(id('J1',38)),false);
  assert.equal(JSON.stringify(view).includes('FIXTURE-38'),false);
  assert.equal('eventos' in view.simulacao,false);
});

test('todas as transições conservam 40 IDs de cada jogador e nenhum saque extra',()=>{
  let s=ready();
  const before={J1:s.jogadores.J1.monte.map(c=>c.copiaId),
                J2:s.jogadores.J2.monte.map(c=>c.copiaId)};
  s=play(s,'J1',39);
  s=play(s,'J1',38);
  s=finish(s,'J1');
  s=play(s,'J2',39);
  s=finish(s,'J2');
  for(const side of ['J1','J2']){
    assert.deepEqual(s.jogadores[side].monte.map(c=>c.copiaId),before[side]);
    assert.equal(s.jogadores[side].monte.length,35);
  }
  zones.check(s);
});

test('não expõe métodos de suporte, combate ou alteração oficial',()=>{
  assert.deepEqual(Object.keys(prep).sort(),
    ['beginFixture','playFixture','finishFixture','publico'].sort());
});

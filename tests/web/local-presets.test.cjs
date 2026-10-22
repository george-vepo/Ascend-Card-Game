'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const presets=require('../../web/pages/local-presets.js');
const decks=require('../../web/pages/decks-core.js');
const match=require('../../web/pages/local-match-core.js');
function catalog() {
  return new Map([
    ['AT-009',{id:'AT-009',nome:'Cat',tipo:'Besta',nd:'0',raridade:'Comum',ca:12,pvMax:2}],
    ['AT-010',{id:'AT-010',nome:'Owl',tipo:'Besta',nd:'0',raridade:'Comum',ca:11,pvMax:1}]
  ]);
}
test('cria CSVs UTF-8 ponto-e-vírgula de 40 cópias canônicas distintas por lado',()=>{
  const source=catalog(), before=JSON.stringify([...source]);
  const result=presets.create(source);
  assert.equal(result.modo,'DECKS_VIRTUAIS_LOCAL_SEM_POSSE');
  assert.match(result.J1,/^\uFEFFcopia_id;catalogo_id\r\n/);
  assert.equal(decks.parseCSV(result.J1).length,40);
  assert.equal(decks.parseCSV(result.J2).length,40);
  const j1=decks.importDeck(result.J1,source,'J1');
  const j2=decks.importDeck(result.J2,source,'J2',j1);
  assert.equal(new Set([...j1,...j2].map(c=>c.copiaId)).size,80);
  assert.equal(j1.every(c=>c.catalogoId==='AT-009'),true);
  assert.equal(j2.every(c=>c.catalogoId==='AT-010'),true);
  assert.equal(JSON.stringify([...source]),before);
});
test('gerar preset não inicia partida, sorteio nem compra',()=>{
  const result=presets.create(catalog());
  assert.equal('versao' in result,false);
  assert.equal('jogadores' in result,false);
  assert.equal('fase' in result,false);
});
test('bloqueia preset se criatura faltante ou atributos divergentes',()=>{
  const incomplete=catalog();incomplete.delete('AT-010');
  assert.throws(()=>presets.create(incomplete),/ausente/);
  const tampered=catalog();tampered.get('AT-009').pvMax=200;
  assert.throws(()=>presets.create(tampered),/PENDENTE/);
});
test('usuário pode iniciar sessão somente após gerar CSVs, sem fixture sintética',()=>{
  const result=presets.create(catalog());
  const s=match.start(catalog(),result.J1,result.J2,()=>0);
  assert.equal(s.jogadores.J1.mao.length,5);
  assert.equal(s.jogadores.J2.mao.length,5);
  assert.equal(s.modo,match.MODE);
});

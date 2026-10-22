'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const presets=require('../../web/pages/local-presets.js');
const importer=require('../../web/pages/decks-core.js');
const zones=require('../../web/pages/zones-core.js');
const match=require('../../web/pages/local-match-core.js');
function catalog(){
  return new Map([
    ['AT-009',{id:'AT-009',nome:'Cat',tipo:'Besta',nd:'0',raridade:'Comum',ca:12,pvMax:2}],
    ['AT-010',{id:'AT-010',nome:'Owl',tipo:'Besta',nd:'0',raridade:'Comum',ca:11,pvMax:1}],
    ['AT-023',{id:'AT-023',nome:'Giant Owl',tipo:'Celestial',nd:'1/4',raridade:'Comum',ca:12,pvMax:19}]
  ]);
}
const selection=()=>({
  J1:{'AT-009':10,'AT-010':10,'AT-023':20},
  J2:{'AT-009':12,'AT-010':14,'AT-023':14}
});
const getIds=csv=>importer.parseCSV(csv).map(x=>x.catalogo_id);
test('monta dois decks virtuais mistos 40+40 em UTF-8 e ponto-e-vírgula',()=>{
  const source=catalog(), snapshot=JSON.stringify([...source]);
  const plan=presets.compose(source,selection());
  assert.equal(plan.preset,'PERSONALIZADO');
  assert.equal(plan.modo,'DECKS_VIRTUAIS_LOCAL_SEM_POSSE');
  assert.match(plan.J1,/^\uFEFFcopia_id;catalogo_id\r\n/);
  assert.equal(importer.parseCSV(plan.J1).length,40);
  assert.equal(importer.parseCSV(plan.J2).length,40);
  assert.deepEqual(getIds(plan.J1).filter(id=>id==='AT-009').length,10);
  assert.deepEqual(getIds(plan.J1).filter(id=>id==='AT-010').length,10);
  assert.deepEqual(getIds(plan.J1).filter(id=>id==='AT-023').length,20);
  const a=importer.importDeck(plan.J1,source,'J1');
  const b=importer.importDeck(plan.J2,source,'J2',a);
  assert.equal(new Set([...a,...b].map(c=>c.copiaId)).size,80);
  assert.equal(JSON.stringify([...source]),snapshot);
});
test('permite 40 cópias de uma espécie já existente sem identidade duplicada',()=>{
  const plan=presets.compose(catalog(),{J1:{'AT-023':40},J2:{'AT-009':40}});
  assert.equal(new Set(importer.parseCSV(plan.J1).map(c=>c.copia_id)).size,40);
  assert.equal(new Set(importer.parseCSV(plan.J2).map(c=>c.copia_id)).size,40);
  assert.equal(getIds(plan.J1).every(id=>id==='AT-023'),true);
});
test('rejeita 39, 41, números fracionários e negativos, sem gerar CSV parcial',()=>{
  const invalid=[
    {J1:{'AT-009':39},J2:{'AT-010':40}},
    {J1:{'AT-009':41},J2:{'AT-010':40}},
    {J1:{'AT-009':39.5,'AT-010':0.5},J2:{'AT-010':40}},
    {J1:{'AT-009':-1,'AT-010':41},J2:{'AT-010':40}},
    {J1:{'AT-009':'40'},J2:{'AT-010':40}}
  ];
  for(const s of invalid) assert.throws(()=>presets.compose(catalog(),s),/40 cópias|Quantidade inválida/);
});
test('bloqueia criatura de fora do subconjunto, mesmo com CA/PV plausíveis',()=>{
  const source=catalog();
  source.set('AT-999',{id:'AT-999',nome:'Inventada',tipo:'Besta',nd:'0',raridade:'Comum',ca:12,pvMax:2});
  assert.throws(()=>presets.compose(source,{
    J1:{'AT-999':40},J2:{'AT-010':40}
  }),/PENDENTE/);
});
test('bloqueia ficha divergente, inexistente e entradas inesperadas de estrutura',()=>{
  const bad=catalog();
  bad.get('AT-023').pvMax=200;
  assert.throws(()=>presets.compose(bad,selection()),/PENDENTE/);
  assert.throws(()=>presets.compose(catalog(),{J1:{'AT-009':40}}),/distribuição J1\/J2/);
  assert.throws(()=>presets.compose(catalog(),{J1:{'AT-009':40},J2:[],J3:{}}),/distribuição J1\/J2/);
  assert.throws(()=>presets.compose(catalog(),{J1:{'AT-009':40},J2:[]}),/Distribuição inválida/);
});
test('compor deck não embaralha, não cria partida nem altera zonas',()=>{
  const plan=presets.compose(catalog(),selection());
  assert.equal('fase' in plan,false);
  assert.equal('jogadores' in plan,false);
  assert.equal('versao' in plan,false);
  assert.equal('histórico' in plan,false);
});
test('partida só começa após chamar o motor V1 com CSVs do editor',()=>{
  const plan=presets.compose(catalog(),selection());
  const s=match.start(catalog(),plan.J1,plan.J2,()=>0);
  assert.equal(s.fase,'TROCA');
  assert.equal(s.versao,1);
  assert.equal(s.jogadores.J1.mao.length,5);
  assert.equal(s.jogadores.J2.mao.length,5);
  assert.equal(s.jogadores.J1.monte.length,35);
  const draft={
    ambiente:'DEMO_LOCAL_NAO_OFICIAL',estagio:'RASCUNHO_ZONAS',
    versao:s.versao,jogadores:s.jogadores,inventario:s.inventario,
    placar:{J1:0,J2:0}
  };
  zones.check(draft);
});

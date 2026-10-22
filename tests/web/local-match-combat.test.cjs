'use strict';
const test = require('node:test'), assert=require('node:assert/strict');
const game=require('../../web/pages/local-match-core.js');
const catalog=new Map([
  ['AT-009',{id:'AT-009',nome:'Cat',tipo:'Besta',nd:'0',raridade:'Comum',ca:12,pvMax:2}],
  ['AT-010',{id:'AT-010',nome:'Owl',tipo:'Besta',nd:'0',raridade:'Comum',ca:11,pvMax:1}]
]);
function csv(side,id) {
  return 'copia_id;catalogo_id\n'+Array.from({length:40},(_,i)=>
    side+'-C'+String(i+1).padStart(2,'0')+';'+id).join('\n');
}
const start=()=>game.start(catalog,csv('J1','AT-009'),csv('J2','AT-010'),()=>0);
const id=s=>'T_'+(s.versao+1);
function prepare(state) {
  let s=state;
  const order=s.primeiro;
  // Primeira fase: sem descartar.
  while(s.fase==='TROCA') {
    s=s.vez==='J2' ? game.aiStep(s) : game.exchange(s,'J1',[],s.versao,id(s));
  }
  while(s.fase==='CRIATURA') {
    if(s.vez==='J2') s=game.aiStep(s);
    else if(!s.jogadores.J1.campo)
      s=game.play(s,'J1',s.jogadores.J1.mao[0].copiaId,s.versao,id(s));
    else s=game.finishCreature(s,'J1',s.versao,id(s));
  }
  while(s.fase==='SUPORTE') {
    s=s.vez==='J2' ? game.aiStep(s) : game.noSupport(s,'J1',s.versao,id(s));
  }
  assert.equal(s.fase,'COMBATE_PENDENTE');
  assert.equal(s.primeiro,order);
  return s;
}
test('Cat/Owl permite iniciativa, turno SRD, dano fixo, KO e score em recorte',()=>{
  let s=prepare(start());
  s=game.beginCombat(s,s.versao,id(s),()=>0);
  assert.equal(s.fase,'COMBATE');
  assert.equal(s.vez,'J1');
  assert.equal(s.combate.iniciativas.J1.total,3);
  const prev=s.versao;
  s=game.attack(s,'J1',s.versao,id(s),()=>19);
  assert.equal(s.versao,prev+1);
  assert.equal(s.placar.J1,1);
  assert.equal(s.jogadores.J2.cemiterio.length,1);
  assert.equal(s.jogadores.J1.campo.pvAtual,2);
  assert.equal(s.fase,'INICIO_CICLO_PENDENTE');
  assert.equal(s.historico.at(-1).acao,'ATAQUE_SRD_PARCIAL');
  assert.match(s.historico.at(-1).detalhe,/20 .+crítico.+KO/);
  assert.equal(game.check(s),s);
});
test('miss usa turno, próxima ação do outro e rodada preservada',()=>{
  let s=prepare(start());
  s=game.beginCombat(s,s.versao,id(s),()=>0);
  s=game.attack(s,'J1',s.versao,id(s),()=>0);
  assert.equal(s.placar.J1,0);
  assert.equal(s.vez,'J2');
  assert.equal(s.combate.rodada,1);
  s=game.aiStep(s); // d20 real do navegador (não forçar resultado)
  assert.equal(s.combate?.rodada===2 || s.fase==='INICIO_CICLO_PENDENTE',true);
});
test('após KO um novo ciclo repõe ambos até 5, sem curar sobrevivente e sem sorteio PRIMEIRO',()=>{
  let s=prepare(start()), first=s.primeiro;
  s=game.beginCombat(s,s.versao,id(s),()=>0);
  s=game.attack(s,'J1',s.versao,id(s),()=>19);
  const survivor=s.jogadores.J1.campo.copiaId;
  const hp=s.jogadores.J1.campo.pvAtual;
  const after=game.beginCycle(s,s.versao,id(s));
  assert.equal(after.ciclo,2);
  assert.equal(after.primeiro,first);
  assert.equal(after.vez,first);
  assert.equal(after.fase,'TROCA');
  assert.equal(after.jogadores.J1.mao.length,5);
  assert.equal(after.jogadores.J2.mao.length,5);
  assert.equal(after.jogadores.J1.campo.copiaId,survivor);
  assert.equal(after.jogadores.J1.campo.pvAtual,hp);
  assert.equal(after.jogadores.J2.cemiterio.length,1);
  assert.equal(after.jogadores.J1.monte.length,34);
  assert.equal(after.jogadores.J2.monte.length,34);
});
test('três KOs encerram imediatamente sem quarto ciclo, perdedor conserva 40 cartas',()=>{
  let s=start();
  for(let cycle=1;cycle<=3;cycle++) {
    s=prepare(s);
    s=game.beginCombat(s,s.versao,id(s),()=>0);
    s=game.attack(s,'J1',s.versao,id(s),()=>19);
    assert.equal(s.placar.J1,cycle);
    if(cycle<3) s=game.beginCycle(s,s.versao,id(s));
  }
  assert.equal(s.fase,'ENCERRADA');
  assert.equal(s.vez,null);
  assert.deepEqual(s.placar,{J1:3,J2:0});
  assert.equal(s.jogadores.J2.cemiterio.length,3);
  assert.equal(s.jogadores.J1.campo.pvAtual,2);
  assert.throws(()=>game.beginCycle(s,s.versao,'AFTER'),/Não há novo ciclo/);
  assert.throws(()=>game.attack(s,'J1',s.versao,'AFTER',()=>19),/fora da fase/);
  game.check(JSON.parse(JSON.stringify(s)));
});
test('duplicação e versão antiga não rolam de novo nem mudam PV/placar',()=>{
  const s=prepare(start()), snapshot=JSON.stringify(s);
  assert.throws(()=>game.beginCombat(s,s.versao-1,'OLD',()=>0),/Versão obsoleta/);
  assert.throws(()=>game.beginCombat(s,s.versao,id(s),()=>99),/Sorteador d20/);
  assert.equal(JSON.stringify(s),snapshot);
  const ready=game.beginCombat(s,s.versao,id(s),()=>0);
  assert.throws(()=>game.attack(ready,'J1',ready.versao-1,'OLD',()=>19),/Versão obsoleta/);
  assert.throws(()=>game.attack(ready,'J2',ready.versao,'WRONG',()=>19),/fora da fase/);
  assert.equal(game.check(ready),ready);
});
test('dados de criatura sem homologação exata não iniciam iniciativa',()=>{
  const fake=new Map([['OTHER',{id:'OTHER',nome:'Outro',tipo:'Besta',nd:'0',raridade:'Comum',ca:12,pvMax:2}]]);
  const valid=game.start(fake,csv('J1','OTHER'),csv('J2','OTHER'),()=>0);
  const staged=prepare(valid);
  assert.throws(()=>game.beginCombat(staged,staged.versao,id(staged),()=>0),/PENDENTE/);
  assert.equal(staged.fase,'COMBATE_PENDENTE');
});
test('projeção pública do combate não vaza mão/ordem J2',()=>{
  let s=prepare(start());s=game.beginCombat(s,s.versao,id(s),()=>0);
  const pub=game.publico(s);
  assert.equal(pub.jogadores.J2.mao,4);
  assert.equal('inventario' in pub,false);
  assert.equal('mao' in pub.jogadores.J2 && Array.isArray(pub.jogadores.J2.mao),false);
  assert.equal(JSON.stringify(pub).includes('J2-C40'),false);
  assert.equal(pub.combate.cobertura,'SRD521_CAT_OWL_GIANT_OWL_ATAQUES_PARCIAIS');
});

test('empate é evento auditado e não permite rerrolagem automática',()=>{
  const s=prepare(start());
  const rolls=[0,1], next=game.beginCombat(s,s.versao,id(s),()=>rolls.shift());
  assert.equal(next.fase,'INICIATIVA_EMPATE_PENDENTE');
  assert.equal(next.vez,null);
  assert.equal(next.combate.iniciativas.J1.total,3);
  assert.equal(next.combate.iniciativas.J2.total,3);
  assert.match(next.historico.at(-1).detalhe,/EMPATE: pendente/);
  assert.throws(()=>game.beginCombat(next,next.versao,'RETRY',()=>19),/iniciativa só ocorre/);
  assert.throws(()=>game.aiStep(next),/fora da própria vez/);
  assert.throws(()=>game.attack(next,'J1',next.versao,'HIT',()=>19),/fora da fase/);
  assert.equal(game.check(next),next);
});

'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
const sr=require('../../web/pages/combat-srd-subset.js');
const match=require('../../web/pages/local-match-core.js');
const presets=require('../../web/pages/local-presets.js');
const giant={catalogoId:'AT-023',nome:'Giant Owl',tipo:'Celestial',nd:'1/4',
  raridade:'Comum',ca:12,pvMax:19};
const cat={catalogoId:'AT-009',nome:'Cat',tipo:'Besta',nd:'0',
  raridade:'Comum',ca:12,pvMax:2};
const owl={catalogoId:'AT-010',nome:'Owl',tipo:'Besta',nd:'0',
  raridade:'Comum',ca:11,pvMax:1};
const catalog=()=>new Map([
  ['AT-023',{...giant,id:'AT-023'}],
  ['AT-009',{...cat,id:'AT-009'}],
  ['AT-010',{...owl,id:'AT-010'}]
]);
const event=s=>'G_'+(s.versao+1);
function prepare(state) {
  let s=state, iterations=0;
  while(s.fase!=='COMBATE_PENDENTE') {
    if(++iterations>20) throw Error('Preparação sem progresso');
    if(s.vez==='J2'){s=match.aiStep(s);continue;}
    if(s.fase==='TROCA') s=match.exchange(s,'J1',[],s.versao,event(s));
    else if(s.fase==='CRIATURA') {
      if(s.jogadores.J1.campo)
        s=match.finishCreature(s,'J1',s.versao,event(s));
      else s=match.play(s,'J1',s.jogadores.J1.mao[0].copiaId,s.versao,event(s));
    } else if(s.fase==='SUPORTE')
      s=match.noSupport(s,'J1',s.versao,event(s));
    else throw Error('Fase desconhecida');
  }
  return s;
}
test('Giant Owl possui ND 1/4, CA 12, PV19, iniciativa +2 e Talons +4 no perfil SRD',()=>{
  const p=sr.profile(giant);
  assert.equal(p.ataque,'Talons');
  assert.deepEqual(p.dadosDano,[1,10]);
  assert.equal(p.danoModificador,2);
  assert.equal(p.iniciativa,2);
  assert.deepEqual(p.resistencias,['necrotic','radiant']);
});
test('rejeita ficha Gigante de edição incorreta, ID homônimo e dados adulterados',()=>{
  assert.throws(()=>sr.profile({...giant,catalogoId:'AT-010'}),/PENDENTE/);
  assert.throws(()=>sr.profile({...giant,tipo:'Besta'}),/PENDENTE/);
  assert.throws(()=>sr.profile({...giant,bonus:6,ca:13}),/PENDENTE/);
  assert.throws(()=>sr.profile({...giant,pvMax:20}),/PENDENTE/);
  assert.equal(sr.profile({...giant,nd:'0.25'}).id,'AT-023');
});
test('Talons SRD normal: d20+4, dano 1d10+2, apenas um dado',()=>{
  const rolls=[14,3], faces=[];
  const result=sr.attack(giant,cat,upper=>{faces.push(upper);return rolls.shift();});
  assert.equal(result.d20,15);
  assert.equal(result.total,19);
  assert.equal(result.acerto,true);
  assert.deepEqual(result.dadosDano,[4]);
  assert.equal(result.modificadorDano,2);
  assert.equal(result.danoBruto,6);
  assert.equal(result.dano,6);
  assert.equal(result.resistenciaAplicada,false);
  assert.deepEqual(faces,[20,10]);
});
test('crítico dobra d10 sem duplicar +2; 1 natural erra e não rola dano',()=>{
  const d20crit=[19,4,5], calls=[];
  const critical=sr.attack(giant,owl,upper=>{calls.push(upper);return d20crit.shift();});
  assert.equal(critical.critico,true);
  assert.deepEqual(critical.dadosDano,[5,6]);
  assert.equal(critical.dano,13);
  assert.deepEqual(calls,[20,10,10]);
  const f=[];
  const miss=sr.attack(giant,cat,upper=>{f.push(upper);return 0;});
  assert.equal(miss.dano,0);
  assert.deepEqual(miss.dadosDano,[]);
  assert.deepEqual(f,[20]);
});
test('erros de d10 e dados incompletos rejeitam o ataque sem resultado fictício',()=>{
  assert.throws(()=>sr.attack(giant,cat,upper=>upper===20?19:10),/Sorteador d10/);
  const rng=[19,5,undefined];
  assert.throws(()=>sr.attack(giant,cat,()=>rng.shift()),/Sorteador d10/);
});
test('preset Giant Owl x Cat gera apenas CSVs; não gera rolagens, zonas ou partida',()=>{
  const plan=presets.create(catalog(),'GIANT_OWL_CAT');
  assert.equal(plan.preset,'GIANT_OWL_CAT');
  assert.equal(plan.modo,'DECKS_VIRTUAIS_LOCAL_SEM_POSSE');
  assert.equal('fase' in plan,false);
  assert.match(plan.J1,/AT-023/);
  assert.match(plan.J2,/AT-009/);
  assert.equal((plan.J1.match(/AT-023/g)||[]).length,40);
  assert.equal((plan.J2.match(/AT-009/g)||[]).length,40);
  assert.throws(()=>presets.create(catalog(),'ANY_OTHER'),/Preset desconhecido/);
});
test('Giant Owl x Cat completa combate SRD parcial com dados e log auditável',()=>{
  const plan=presets.create(catalog(),'GIANT_OWL_CAT');
  let s=prepare(match.start(catalog(),plan.J1,plan.J2,()=>0));
  const init=[1,0]; // d20 2+2 =4 para Owl; d20 1+2=3 para Cat
  s=match.beginCombat(s,s.versao,event(s),()=>init.shift());
  assert.equal(s.vez,'J1');
  const before=s;
  const dices=[14,3]; // hit d20=15+4 e d10=4 -> 6
  s=match.attack(s,'J1',s.versao,event(s),()=>dices.shift());
  assert.equal(before.jogadores.J2.campo.pvAtual,2);
  assert.equal(s.placar.J1,1);
  assert.equal(s.fase,'INICIO_CICLO_PENDENTE');
  assert.equal(s.jogadores.J1.campo.pvAtual,19);
  assert.equal(s.jogadores.J2.cemiterio.length,1);
  assert.match(s.historico.at(-1).detalhe,/4 \+ 2 = 6/);
  assert.match(s.historico.at(-1).detalhe,/KO de Cat/);
  assert.equal(match.check(s),s);
});
test('dano d10 malformado não altera estado, turno, PV nem consome evento',()=>{
  const plan=presets.create(catalog(),'GIANT_OWL_CAT');
  let s=prepare(match.start(catalog(),plan.J1,plan.J2,()=>0));
  const init=[1,0]; s=match.beginCombat(s,s.versao,event(s),()=>init.shift());
  const before=JSON.stringify(s);
  assert.throws(()=>match.attack(s,'J1',s.versao,event(s),upper=>upper===20?18:10),
    /Sorteador d10/);
  assert.equal(JSON.stringify(s),before);
});

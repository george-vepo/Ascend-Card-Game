'use strict';
const test = require('node:test'), assert = require('node:assert/strict');
const sr = require('../../web/pages/combat-srd-subset.js');
const cat = { catalogoId:'AT-009', nome:'Cat', tipo:'Besta', nd:'0',
  raridade:'Comum', ca:12, pvMax:2 };
const owl = { catalogoId:'AT-010', nome:'Owl', tipo:'Besta', nd:'0',
  raridade:'Comum', ca:11, pvMax:1 };
test('perfis oficiais de Cat e Owl são exatos, não autohomologam novas fichas', ()=>{
  assert.equal(sr.profile(cat).ataque,'Scratch');
  assert.equal(sr.profile(owl).bonus,3);
  assert.throws(()=>sr.profile({...cat,ca:10}),/PENDENTE/);
  assert.throws(()=>sr.profile({...owl,pvMax:99}),/PENDENTE/);
  assert.throws(()=>sr.profile({...cat,catalogoId:'TF-999'}),/PENDENTE/);
});
test('iniciativa depende do d20 e atributo de cada ficha, independente da ordem inicial', ()=>{
  const r=sr.initiative(cat,owl,()=>0);
  assert.equal(r.valores.J1.total,3);
  assert.equal(r.valores.J2.total,2);
  assert.deepEqual(r.ordem,['J1','J2']);
  const opposite=sr.initiative(cat,owl,upper => upper === 20 ? 0 : -1);
  assert.deepEqual(opposite.ordem,['J1','J2']);
});
test('empate de iniciativa fica pendente; não aplica prioridade da preparação',()=>{
  const seq=[0,1];
  const tie=sr.initiative(cat,owl,()=>seq.shift());
  assert.equal(tie.empate,true);
  assert.equal(tie.ordem,null);
  assert.equal(tie.valores.J1.total,3);
  assert.equal(tie.valores.J2.total,3);
});
test('20 natural é crítico mas Scratch fixo não dobra; 1 natural erra',()=>{
  const crit=sr.attack(cat,owl,()=>19);
  assert.equal(crit.critico,true);
  assert.equal(crit.dano,1);
  assert.equal(crit.danoComDados,false);
  const miss=sr.attack(cat,owl,()=>0);
  assert.equal(miss.acerto,false);
  assert.equal(miss.dano,0);
});
test('Owl Talons e CA: hit com soma igual, miss abaixo',()=>{
  assert.equal(sr.attack(owl,cat,()=>8).acerto,true); // 9+3=12
  assert.equal(sr.attack(owl,cat,()=>7).acerto,false); // 8+3=11
  assert.equal(sr.attack(owl,cat,()=>8).tipoDano,'slashing');
});
test('sorteador inválido não produz efeito ou dano fictício',()=>{
  assert.throws(()=>sr.attack(cat,owl,()=>20),/Sorteador d20/);
  assert.throws(()=>sr.initiative(cat,owl,()=>-1),/Sorteador d20/);
});

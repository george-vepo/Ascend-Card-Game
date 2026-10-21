'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const zones = require('../../web/pages/zones-core.js');
const lab = require('../../web/pages/fixture-lab.js');

function advance(state, n) {
  let current = state;
  for (let i = 0; i < n; i++) current = lab.step(current, current.versao);
  return current;
}

test('laboratório cria somente um rascunho sintético de 40 cópias por lado', () => {
  const s = lab.start(), view = lab.publicView(s);
  assert.equal(s.ambiente, 'DEMO_LOCAL_NAO_OFICIAL');
  assert.equal(view.ambiente, 'LABORATORIO_FICTICIO_SEM_PARTIDA');
  assert.equal(view.fase, 'TROCA');
  assert.equal(view.vez, 'J1');
  assert.equal(view.versao, 1);
  assert.deepEqual(view.placar, {J1:0,J2:0});
  for (const side of ['J1','J2']) {
    assert.equal(s.inventario[side].length,40);
    assert.equal(view.jogadores[side].monte,35);
    assert.equal(view.jogadores[side].mao,5);
    assert.equal(view.jogadores[side].cemiterio,0);
    assert.equal(view.jogadores[side].campo,null);
  }
  assert.equal(s.jogadores.J1.mao[0].catalogoId.startsWith('FICTICIO-'),true);
  zones.check(s);
});

test('não expõe identidades de mãos ou ordem dos montes na projeção pública', () => {
  const s=lab.start();
  const view=lab.publicView(s), text=JSON.stringify(view);
  assert.equal('inventario' in view,false);
  assert.equal('eventos' in view,false);
  assert.equal(Array.isArray(view.jogadores.J1.mao),false);
  assert.equal(text.includes('J1-SINTETICO-39'),false);
  assert.equal(text.includes('J2-SINTETICO-39'),false);
  assert.equal(text.includes('FICTICIO-'),false);
});

test('o primeiro passo troca um marcador de J1 sem revelar a mão', () => {
  const s=lab.start(), snapshot=JSON.stringify(s);
  const next=lab.step(s,s.versao), view=lab.publicView(next);
  assert.equal(JSON.stringify(s),snapshot);
  assert.equal(view.fase,'TROCA');assert.equal(view.vez,'J2');
  assert.equal(view.jogadores.J1.cemiterio,1);
  assert.equal(view.jogadores.J1.monte,34);
  assert.equal(view.jogadores.J1.mao,5);
  assert.equal(JSON.stringify(view).includes('J1-SINTETICO-35'),false);
  zones.check(next);
});

test('a troca de zero de J2 não altera mão ou monte', () => {
  const s=advance(lab.start(),2), view=lab.publicView(s);
  assert.equal(view.fase,'PREPARACAO_NAO_IMPLEMENTADA');
  assert.equal(view.jogadores.J2.monte,35);
  assert.equal(view.jogadores.J2.mao,5);
  assert.equal(view.jogadores.J2.cemiterio,0);
  assert.equal(view.proximaAcao,'Iniciar preparação sintética');
});

test('invocação Comum aparece no campo público com PV máximos', () => {
  const s=advance(lab.start(),4), view=lab.publicView(s);
  assert.equal(view.fase,'CRIATURA');
  assert.equal(view.vez,'J1');
  assert.equal(view.jogadores.J1.campo.copiaId,'J1-SINTETICO-39');
  assert.equal(view.jogadores.J1.campo.raridade,'Comum');
  assert.equal(view.jogadores.J1.campo.pvAtual,20);
  assert.equal(view.jogadores.J1.mao,4);
  assert.equal(view.jogadores.J1.cemiterio,1);
  assert.equal(JSON.stringify(view).includes('J2-SINTETICO-39'),false);
});

test('evoluções consecutivas substituem a ativa e não compram cartas', () => {
  const s=advance(lab.start(),6), view=lab.publicView(s);
  assert.equal(view.jogadores.J1.campo.raridade,'Rara');
  assert.equal(view.jogadores.J1.campo.copiaId,'J1-SINTETICO-37');
  assert.equal(view.jogadores.J1.campo.pvAtual,40);
  assert.equal(view.jogadores.J1.cemiterio,3);
  assert.equal(view.jogadores.J1.mao,2);
  assert.equal(view.jogadores.J1.monte,34);
  zones.check(s);
});

test('encerrar primeiro transfere a preparação para o segundo', () => {
  const s=advance(lab.start(),7), view=lab.publicView(s);
  assert.equal(view.fase,'CRIATURA');
  assert.equal(view.vez,'J2');
  assert.equal(view.jogadores.J1.campo.raridade,'Rara');
  assert.equal(view.jogadores.J2.campo,null);
});

test('o roteiro para antes de suporte, batalha e pontuação', () => {
  const s=advance(lab.start(),10), view=lab.publicView(s);
  assert.equal(view.fase,'SUPORTE_NAO_IMPLEMENTADO');
  assert.equal(view.vez,null);
  assert.equal(view.proximaAcao,null);
  assert.equal(view.jogadores.J2.campo.raridade,'Incomum');
  assert.deepEqual(view.placar,{J1:0,J2:0});
  assert.throws(()=>lab.step(s,s.versao),/termina antes dos suportes/);
  zones.check(s);
});

test('rejeita carta externa mesmo com inventário e zonas coerentes', () => {
  const s = lab.start();
  const modified = JSON.parse(JSON.stringify(s));
  modified.inventario.J1[0].catalogoId = 'AT-002';
  modified.jogadores.J1.monte[0].catalogoId = 'AT-002';
  zones.check(modified);
  assert.throws(() => lab.publicView(modified), /marcadores fictícios fixos/);
  assert.throws(() => lab.step(modified,modified.versao), /marcadores fictícios fixos/);
  assert.equal(s.inventario.J1[0].catalogoId, 'FICTICIO-0');
});

test('versão antiga não modifica estado sintético', () => {
  const s=lab.start(), old=JSON.stringify(s);
  assert.throws(()=>lab.step(s,s.versao-1),/Versão obsoleta/);
  assert.equal(JSON.stringify(s),old);
});

test('todos os passos preservam inventário de 40 cópias por jogador', () => {
  let s=lab.start();
  for(let i=0;i<=10;i++){
    zones.check(s);
    for(const side of ['J1','J2']){
      const p=s.jogadores[side];
      assert.equal(p.monte.length+p.mao.length+p.cemiterio.length+(p.campo?1:0),40);
    }
    if(i<10)s=lab.step(s,s.versao);
  }
});

test('página usa apenas fontes locais e mostra avisos contra dados reais', () => {
  const base=path.join(__dirname,'../../web/pages');
  const html=fs.readFileSync(path.join(base,'fixture-lab.html'),'utf8');
  for(const file of ['decks-core.js','zones-core.js','draw-exchange-fixtures.js',
      'creature-preparation-fixtures.js','fixture-lab.js'])
    assert.ok(html.includes('src="./'+file+'"'),file);
  assert.ok(html.includes('inteiramente fictícios'));
  assert.ok(html.includes('Não envie mãos ou decks privados'));
  assert.equal(html.includes('type="file"'),false);
  assert.equal(html.includes('localStorage'),false);
  const script=fs.readFileSync(path.join(base,'fixture-lab.js'),'utf8');
  for(const banned of ['localStorage','sessionStorage','fetch(','XMLHttpRequest','innerHTML'])
    assert.equal(script.includes(banned),false,banned);
});

test('motor público não exporta funções de acesso às mãos ou de combate',()=>{
  assert.deepEqual(Object.keys(lab).sort(),
    ['start','step','nextAction','publicView','mount'].sort());
});

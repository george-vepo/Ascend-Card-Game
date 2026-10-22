'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const adapter=require('../../web/pages/decks-core.js');
test('smoke: catálogo publicado contém Roper canônico com ficha',
 {skip:process.env.ASCEND_CATALOG_NETWORK_TEST!=='1'}, async()=>{
  const catalog=await adapter.loadCatalog();
  assert.ok(catalog.size>=500);
  const roper=catalog.get('AT-002');
  assert.equal(roper?.nome,'Roper');
  assert.equal(roper?.ca,20);
  assert.equal(roper?.pvMax,93);
  assert.equal(roper?.raridade,'Comum');
});
test('smoke real: Cat, Owl e Giant Owl publicados permitem os presets locais',
 {skip:process.env.ASCEND_CATALOG_NETWORK_TEST!=='1'}, async()=>{
  const combat=require('../../web/pages/combat-srd-subset.js');
  const presets=require('../../web/pages/local-presets.js');
  const catalog=await adapter.loadCatalog();
  for(const id of ['AT-009','AT-010','AT-023']) {
    const source=catalog.get(id);
    assert.ok(source,'Identidade '+id+' ausente do catálogo publicado');
    assert.equal(combat.profile({
      catalogoId:source.id,nome:source.nome,tipo:source.tipo,
      nd:source.nd,raridade:source.raridade,ca:source.ca,pvMax:source.pvMax
    }).id,id);
  }
  for(const kind of ['CAT_OWL','GIANT_OWL_CAT']) {
    const plan=presets.create(catalog,kind);
    assert.equal(adapter.parseCSV(plan.J1).length,40);
    assert.equal(adapter.parseCSV(plan.J2).length,40);
  }
});

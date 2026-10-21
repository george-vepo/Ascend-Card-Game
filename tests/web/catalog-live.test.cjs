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
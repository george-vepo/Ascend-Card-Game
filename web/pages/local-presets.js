/* Decks virtuais locais Cat/Owl para teste controlado — nunca posse oficial. */
(function (root, factory) {
  const node = typeof module === 'object' && module.exports;
  const importer = node ? require('./decks-core.js') : root && root.SRDDeckImport;
  const combat = node ? require('./combat-srd-subset.js') : root && root.SRDCombatSubset;
  const api = factory(importer, combat);
  if (node) module.exports = api;
  if (root) root.SRDLocalPresets = api;
})(typeof window !== 'undefined' ? window : null, function (importer, combat) {
  'use strict';
  const fail = m => { throw new Error(m); };
  const SPECIES = Object.freeze({J1:'AT-009',J2:'AT-010'});
  function csv(side, catalogId) {
    return '\uFEFFcopia_id;catalogo_id\r\n' +
      Array.from({length:40}, (_,i)=>
        side+'-C'+String(i+1).padStart(2,'0')+';'+catalogId).join('\r\n')+'\r\n';
  }
  function create(catalog) {
    if (!importer || !combat || !(catalog instanceof Map))
      fail('Carregue o catálogo verificado antes de criar decks virtuais.');
    for (const side of ['J1','J2']) {
      const entry = catalog.get(SPECIES[side]);
      if (!entry) fail('Criatura canônica do preset ausente do Catálogo SRD: '+SPECIES[side]);
      combat.profile({
        catalogoId: entry.id, nome: entry.nome, tipo: entry.tipo,
        nd: entry.nd, raridade: entry.raridade, ca: entry.ca, pvMax: entry.pvMax
      });
    }
    const J1=csv('J1',SPECIES.J1), J2=csv('J2',SPECIES.J2);
    const human=importer.importDeck(J1,catalog,'J1');
    const ai=importer.importDeck(J2,catalog,'J2',human);
    if (human.length!==40 || ai.length!==40)
      fail('Falha de integridade do preset Cat/Owl.');
    return Object.freeze({J1,J2,modo:'DECKS_VIRTUAIS_LOCAL_SEM_POSSE'});
  }
  return { create };
});

/* Decks virtuais locais verificáveis para testes — nunca posse oficial. */
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
  const PRESETS = Object.freeze({
    CAT_OWL: Object.freeze({J1:'AT-009',J2:'AT-010'}),
    GIANT_OWL_CAT: Object.freeze({J1:'AT-023',J2:'AT-009'})
  });
  function csv(side, catalogId) {
    return '\uFEFFcopia_id;catalogo_id\r\n' +
      Array.from({length:40}, (_,i)=>
        side+'-C'+String(i+1).padStart(2,'0')+';'+catalogId).join('\r\n')+'\r\n';
  }
  function create(catalog, preset = 'CAT_OWL') {
    if (!importer || !combat || !(catalog instanceof Map))
      fail('Carregue o catálogo verificado antes de criar decks virtuais.');
    const species = PRESETS[preset];
    if (!Object.hasOwn(PRESETS, preset) || !species)
      fail('Preset desconhecido: não criar criaturas artificiais.');
    for (const side of ['J1','J2']) {
      const entry = catalog.get(species[side]);
      if (!entry) fail('Criatura canônica do preset ausente do Catálogo SRD: '+species[side]);
      combat.profile({
        catalogoId: entry.id, nome: entry.nome, tipo: entry.tipo,
        nd: entry.nd, raridade: entry.raridade, ca: entry.ca, pvMax: entry.pvMax
      });
    }
    const J1=csv('J1',species.J1), J2=csv('J2',species.J2);
    const human=importer.importDeck(J1,catalog,'J1');
    const ai=importer.importDeck(J2,catalog,'J2',human);
    if (human.length!==40 || ai.length!==40)
      fail('Falha de integridade do preset Cat/Owl.');
    return Object.freeze({J1,J2,preset,modo:'DECKS_VIRTUAIS_LOCAL_SEM_POSSE'});
  }
  return { create };
});

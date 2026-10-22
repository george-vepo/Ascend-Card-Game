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
  function csv(side, ids) {
    return '\uFEFFcopia_id;catalogo_id\r\n' +
      ids.map((catalogId, i) =>
        side + '-C' + String(i + 1).padStart(2, '0') + ';' + catalogId)
        .join('\r\n') + '\r\n';
  }
  // Composição de DECKS VIRTUAIS (não coleção). O Catálogo SRD é a fonte
  // única: somente as fichas que o combate incremental suporta podem entrar.
  function compose(catalog, distribution) {
    if (!importer || !combat || !(catalog instanceof Map))
      fail('Carregue o catálogo verificado antes de criar decks virtuais.');
    if (!distribution || typeof distribution !== 'object' ||
        Array.isArray(distribution) ||
        Object.keys(distribution).sort().join(',') !== 'J1,J2')
      fail('Informe a distribuição J1/J2 de ambos os decks.');
    const prepared = {};
    for (const side of ['J1','J2']) {
      const selected = distribution[side];
      if (!selected || typeof selected !== 'object' || Array.isArray(selected))
        fail('Distribuição inválida do jogador ' + side + '.');
      const ids = [];
      for (const [id, count] of Object.entries(selected)) {
        if (!Object.hasOwn(combat.PROFILES, id))
          fail('PENDENTE: criatura fora do subconjunto de combate SRD: ' + id);
        if (!Number.isSafeInteger(count) || count < 0 || count > 40)
          fail('Quantidade inválida de cópias de ' + id + '.');
        if (count === 0) continue;
        const entry = catalog.get(id);
        if (!entry) fail('Criatura canônica ausente do Catálogo SRD: ' + id);
        combat.profile({
          catalogoId: entry.id, nome: entry.nome, tipo: entry.tipo,
          nd: entry.nd, raridade: entry.raridade, ca: entry.ca, pvMax: entry.pvMax
        });
        for (let i=0; i<count; i++) ids.push(id);
      }
      if (ids.length !== 40)
        fail(side + ': deck virtual exige exatamente 40 cópias; recebeu ' + ids.length + '.');
      prepared[side] = csv(side, ids);
    }
    const human = importer.importDeck(prepared.J1, catalog, 'J1');
    const ai = importer.importDeck(prepared.J2, catalog, 'J2', human);
    if (human.length !== 40 || ai.length !== 40)
      fail('Integridade dos 80 IDs de cópia não confirmada.');
    return Object.freeze({
      J1: prepared.J1, J2: prepared.J2,
      preset: 'PERSONALIZADO', modo: 'DECKS_VIRTUAIS_LOCAL_SEM_POSSE'
    });
  }
  function create(catalog, preset = 'CAT_OWL') {
    const species = PRESETS[preset];
    if (!Object.hasOwn(PRESETS, preset) || !species)
      fail('Preset desconhecido: não criar criaturas artificiais.');
    const generated = compose(catalog, {
      J1: {[species.J1]: 40}, J2: {[species.J2]: 40}
    });
    return Object.freeze({...generated, preset});
  }
  return { create, compose };
});

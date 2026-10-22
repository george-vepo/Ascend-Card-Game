/* Subconjunto SRD 5.2.1: Cat e Owl. Nenhuma mecânica de outros monstros. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.SRDCombatSubset = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';
  // Fichas: SRD_CC_v5.2.1.pdf pp. 346 (Cat) e 358 (Owl).
  // Controle editorial: Catalogo-SRD/docs/catalogo/data/drive-fichas-srd-20261021/
  // AT-009-cat.json e AT-010-owl.json; não existe homologação de outras ações.
  const PROFILES = Object.freeze({
    'AT-009': Object.freeze({
      id: 'AT-009', nome: 'Cat', tipo: 'Besta', nd: 0,
      ca: 12, pvMax: 2, iniciativa: 2, ataque: 'Scratch',
      bonus: 4, danoFixo: 1, tipoDano: 'slashing'
    }),
    'AT-010': Object.freeze({
      id: 'AT-010', nome: 'Owl', tipo: 'Besta', nd: 0,
      ca: 11, pvMax: 1, iniciativa: 1, ataque: 'Talons',
      bonus: 3, danoFixo: 1, tipoDano: 'slashing'
    })
  });
  const fail = msg => { throw new Error(msg); };
  function profile(card) {
    const expected = card && PROFILES[card.catalogoId];
    if (!expected ||
        card.nome !== expected.nome || card.tipo !== expected.tipo ||
        String(card.nd) !== '0' || card.raridade !== 'Comum' ||
        card.ca !== expected.ca || card.pvMax !== expected.pvMax)
      fail('PENDENTE: combate SRD só admite Cat (AT-009) e Owl (AT-010) com fichas exatas.');
    return expected;
  }
  function d20(rng) {
    if (typeof rng !== 'function') fail('Sorteador inválido.');
    const n = rng(20);
    if (!Number.isSafeInteger(n) || n < 0 || n >= 20)
      fail('Sorteador d20 produziu valor inválido.');
    return n + 1;
  }
  function initiative(cardJ1, cardJ2, rng) {
    const a = profile(cardJ1), b = profile(cardJ2);
    const d1 = d20(rng), d2 = d20(rng);
    const values = {
      J1: { d20: d1, modificador: a.iniciativa, total: d1 + a.iniciativa },
      J2: { d20: d2, modificador: b.iniciativa, total: d2 + b.iniciativa }
    };
    // O contrato ainda não define arbitragem automática do empate de iniciativa
    // humano x IA. Não introduzir "prioridade fixa" como desempate por palpite.
    if (values.J1.total === values.J2.total)
      return { valores: values, empate: true, ordem: null };
    const first = values.J1.total > values.J2.total ? 'J1' : 'J2';
    return { valores: values, empate: false,
      ordem: [first, first === 'J1' ? 'J2' : 'J1'] };
  }
  function attack(attacker, defender, rng) {
    const a = profile(attacker), target = profile(defender);
    const die = d20(rng);
    const critical = die === 20, hit = critical ||
      (die !== 1 && die + a.bonus >= target.ca);
    return {
      ataque: a.ataque, origem: a.id, alvo: target.id,
      d20: die, bonus: a.bonus, total: die + a.bonus, caAlvo: target.ca,
      acerto: hit, critico: critical, dano: hit ? a.danoFixo : 0,
      tipoDano: a.tipoDano, danoComDados: false,
      // Critical Hits rolam dados de dano duas vezes; dano fixo NÃO tem dados.
      observacao: 'Dano fixo SRD, sem dados para duplicar em crítico.'
    };
  }
  return { PROFILES, profile, initiative, attack };
});

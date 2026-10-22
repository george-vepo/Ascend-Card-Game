/* Subconjunto SRD 5.2.1: Cat, Owl, Giant Owl — ataques pontuais verificados. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.SRDCombatSubset = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';
  // SRD_CC_v5.2.1.pdf: Cat p.346; Giant Owl p.352; Owl p.358.
  // Catalogo-SRD/docs/catalogo/data/drive-fichas-srd-20261021/
  // AT-009-cat.json, AT-010-owl.json, AT-023-giant-owl.json.
  // Giant Owl: SOMENTE Talons; Spellcasting não implementada nem homologada.
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
    }),
    'AT-023': Object.freeze({
      id: 'AT-023', nome: 'Giant Owl', tipo: 'Celestial', nd: '1/4',
      ca: 12, pvMax: 19, iniciativa: 2, ataque: 'Talons',
      bonus: 4, dadosDano: Object.freeze([1, 10]), danoModificador: 2,
      tipoDano: 'slashing',
      // Resistências da ficha confirmadas; estas três criaturas só causam
      // dano cortante, portanto não há aplicação neste recorte.
      resistencias: Object.freeze(['necrotic', 'radiant'])
    })
  });
  const fail = msg => { throw new Error(msg); };
  function profile(card) {
    const expected = card && PROFILES[card.catalogoId];
    if (!expected ||
        card.nome !== expected.nome || card.tipo !== expected.tipo ||
        !([String(expected.nd)].concat(expected.id === 'AT-023' ? ['0.25'] : [])
          .includes(String(card.nd))) || card.raridade !== 'Comum' ||
        card.ca !== expected.ca || card.pvMax !== expected.pvMax)
      fail('PENDENTE: combate SRD só admite Cat (AT-009), Owl (AT-010) ' +
        'e Giant Owl (AT-023) com fichas exatas.');
    return expected;
  }
  function rollDie(faces, rng) {
    if (typeof rng !== 'function') fail('Sorteador inválido.');
    const n = rng(faces);
    if (!Number.isSafeInteger(n) || n < 0 || n >= faces)
      fail('Sorteador d' + faces + ' produziu valor inválido.');
    return n + 1;
  }
  const d20 = rng => rollDie(20, rng);
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
    const damageDice = [];
    if (hit && a.dadosDano) {
      const [count, faces] = a.dadosDano;
      for (let i = 0; i < count * (critical ? 2 : 1); i++)
        damageDice.push(rollDie(faces, rng));
    }
    // Critical Hits: duplicar apenas o número de dados, não o modificador.
    // Cat/Owl usam dano fixo 1 e NÃO têm dados a duplicar.
    const damage = hit ? (a.dadosDano ?
      damageDice.reduce((sum, n) => sum + n, a.danoModificador) : a.danoFixo) : 0;
    const resisted = Boolean(target.resistencias?.includes(a.tipoDano));
    const finalDamage = resisted ? Math.floor(damage / 2) : damage;
    return {
      ataque: a.ataque, origem: a.id, alvo: target.id,
      d20: die, bonus: a.bonus, total: die + a.bonus, caAlvo: target.ca,
      acerto: hit, critico: critical, dano: finalDamage,
      danoBruto: damage, dadosDano: damageDice,
      modificadorDano: hit && a.dadosDano ? a.danoModificador : 0,
      resistenciaAplicada: resisted && hit,
      tipoDano: a.tipoDano, danoComDados: Boolean(a.dadosDano),
      observacao: a.dadosDano ?
        'Talons: dados SRD 1d10+2; crítico duplica apenas o d10.' :
        'Dano fixo SRD, sem dados para duplicar em crítico.'
    };
  }
  return { PROFILES, profile, initiative, attack };
});

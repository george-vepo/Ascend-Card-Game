# Roper: fuga do agarrão, dano e destruição do tentáculo (fixture SRD)

**Fonte mecânica:** Catálogo SRD, ficha integral SRD 5.2.1 do Roper e da Giant Owl, no commit fixado no contrato. A regra geral **Grappling — Ending a Grapple** do SRD permite usar a Action para tentar escapar com Strength (Athletics) ou Dexterity (Acrobatics) contra a CD de fuga. A ficha do Roper estabelece CD **14**.

## Fuga (Giant Owl)

No comando experimental \`ESCAPAR_GRAPPLE_ROPER_TESTE\`, o controlador da Giant Owl escolhe **Athletics ou Acrobatics**, fornece um d20 **simulado** e consome o turno para fazer o teste. Os bônus da coruja são extraídos da ficha SRD: Athletics +1 e Acrobatics +2 (a lista de perícias não inclui proficiência nessas duas).

- Resultado ≥ CD 14: encerra **Grappled** e, pela ficha Tentacle, **Poisoned**; o slot do tentáculo fica disponível novamente, mas não é destruído.
- Resultado abaixo da CD: as condições continuam, mas a Action é consumida.
- Declaração sem turno correto, sem fonte ou sem dado: rejeitada/pendente conforme a causa, sem mutação.

## Dano no tentáculo

O SRD do Roper permite atacar/danificar tentáculos agarrando alvos: **CA 20, PV 10, imunidades Poison e Psychic**. O comando \`ATACAR_TENTACULO_ROPER_TESTE\` usa somente Talons da Giant Owl, com alcance até o tentáculo confirmado por dado externo de cenário. Sob Poisoned, a coruja tem desvantagem e deve fornecer dois d20 simulados. O dano vai **exclusivamente ao tentáculo**, nunca ao Roper.

- Dano parcial fica associado ao slot, no checkpoint e na visão pública.
- Quando o tentáculo chega a 0 PV, libera Grappled/Poisoned e o vínculo.
- O SRD determina que o tentáculo destruído **regenera no começo do próximo turno do Roper**. Nesta fixture de um ataque por turno, a troca de iniciativa que inicia o turno do Roper já registra a regeneração; não ocorre no instante de causar dano.
- Os dados não são sorteados internamente. A integração permanece apenas para o confronto Giant Owl × Roper.

## Pendências

\`Reel\` depende de geometria e continua **PENDENTE** sem alterar o estado. \`Multiattack\`, terreno, Flyby, magias, múltiplos tentáculos e modificadores situacionais não foram implementados. Isto **não é um combate SRD completo** nem uma partida oficial.

Estados privados nunca devem ser publicados; relatórios públicos mostram apenas dados de campo e recursos públicos. As 40 cópias de cada deck permanecem preservadas.

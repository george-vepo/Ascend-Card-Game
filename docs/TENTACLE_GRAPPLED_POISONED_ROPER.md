# Tentacle, Grappled e Poisoned do Roper — recorte experimental

**Fonte:** ficha integral do Roper (AT-002, cópia AB-POC-017) no Catálogo SRD, SRD 5.2.1, p.320. O Ascend lê a versão e o hash do documento remoto pinado. Não copia ficha, carta ou arte.

## Implementado e testado

Tentacle é um ataque corpo a corpo independente documentado nas Actions do Roper. Na fixture com Giant Owl, a jogada exige:
- Controle do Roper, turno válido, escopo limitado aceito
- Confirmação de que a Giant Owl está ao alcance de 60 pés; sem arena, a geometria não é inferida
- Tentáculo numerado explicitamente de 1 a 6, não ocupado, e d20 **simulado** fornecido
- Acerto usa +7 contra CA 12; em acerto aplica *Grappled* e *Poisoned*, registrando fonte, tentáculo e CD 14; não aplica dano, pois Tentacle não declara dados de dano
- Tentacle consome o turno na fixture; não é a ação completa Multiattack

A Giant Owl ainda pode tentar Talons se o alcance corpo a corpo estiver explicitamente confirmado, mas *Poisoned* exige dois d20 simulados por desvantagem, usando o menor. *Grappled* representa a condição e suas limitações de deslocamento; a POC continua sem execução real de movimento.

O vínculo entre a condição e o tentáculo é guardado no evento e no estado, e verificado com o hash da ficha antes de resolver novos ataques e ao restaurar checkpoint. A mesa pública exibe condições e tentáculos ocupados sem divulgar mão ou ordem de monte.

## Lacunas sem aprovação

O SRD estabelece seis tentáculos, com **CA 20/PV 10**, imunidades a dano Poison/Psychic, destruição que liberta a vítima e regeneração no começo do próximo turno do Roper. Esses parâmetros são extraídos da ficha, mas **dano direcionado ao tentáculo, destruição, regeneração e fuga com CD 14 ainda não são executados**.

**Reel** puxa criaturas agarradas até 30 pés, mas a POC não regulamenta posições/arena. A declaração permanece **PENDENTE** sem mudar estado, mesmo havendo vítima agarrada. Tentativas de múltiplos tentáculos no mesmo alvo também ficam pendentes. *Multiattack* (2 Tentacle + Reel + 2 Bite) e *Spider Climb* continuam não homologados.

Toda rolagem usada é um parâmetro explicitamente simulado, nunca RNG oculto. Partida oficial não iniciada; placar 0 × 0.

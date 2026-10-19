# Ratificação de regra vigente — combate sem posicionamento

**Data de ratificação:** 19/10/2026. **Regra original aprovada:** 15/10/2026.

## Fonte e precedência

O administrador reiterou: **"não temos posição, toda a ação não deve levar em consideração a posição da criatura para resolver"**. A diretriz já constava de `docs/poc/01_Regras/CONTRATO_DE_REGRAS.md`, em **Formato de combate e restrições**, desde 15/10: a POC elimina movimentação, posicionamento e alcance espacial. Esta ratificação **não cria um novo modelo de arena**.

## Contrato de implementação

- Não armazenar nem solicitar coordenadas, direção, linha de visão geográfica, vizinhança ou distância para validar ataques e habilidades.
- Ignorar campos legados de fixtures como `alvo_no_alcance_fixture`: ausência, `true` e `false` não afetam a legalidade de uma ação.
- Números espaciais da ficha (alcance em pés, deslocamento) podem ser exibidos como **dados de origem SRD**, jamais como condição operacional no Card Game.
- Roper **Tentacle** mantém teste de ataque, Grappled, Poisoned, DC de fuga, slots e regeneração. Nenhum alcance de 60 ft precisa ser comprovado.
- Roper **Reel** mantém sua identificação e a exigência de alvos Grappled da ficha. O puxão espacial de até 30 ft **não altera o estado da partida**, pois não há posição nem deslocamento a representar. A Action individual pode ser registrada e avançar o turno, sem causar dano/condição por conta própria.
- Roper **Bite** mantém rolagem, bônus, dano, crítico e consequências, dispensada a checagem de 5 ft.
- Roper **Multiattack** continua compondo **duas Tentacle, Reel e duas Bite na mesma Action**. Não executar essas etapas como turnos independentes; preservar bloqueio técnico até suportar alvos/condições e economia de uma Action.
- Permanecem obrigatórias verificações de vez/fase, alvo não espacialmente válido, condições, CA/PV, CDs, dados, recursos, reações, concentração e integridade das 40 cópias. Não inferir efeitos de movimento sobre outras regras.

## Controle

[Issue #19](https://github.com/george-vepo/Ascend-Card-Game/issues/19) foi encerrada por regra previamente aprovada, sem alterar a ficha no `Catalogo-SRD`. Esta decisão não modifica nenhuma partida oficial; partida não iniciada, placar 0 × 0.

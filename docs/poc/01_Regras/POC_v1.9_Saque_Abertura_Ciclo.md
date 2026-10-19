# SRD Card Game — POC v1.9 | Compra na abertura de cada novo ciclo

**Status:** aprovada pelo administrador em 17/10/2026. **Escopo:** duelo humano J1 (Celestial) versus IA J2 (Aberração), decks experimentais de 40 IDs cada; partida ainda não iniciada.

## Vocabulário

- **Rodada interna de combate:** sequência de turnos sob a iniciativa daquele combate, podendo ocorrer várias até o KO. **Não gera saque.**
- **Combate:** confronto das duas criaturas ativas que termina quando uma chega a 0 PV; pontuação +1 ao vencedor. Nenhuma reposição ocorre ao registrar o KO.
- **Ciclo de preparação:** etapa seguinte entre confrontos, iniciada somente após combate terminado e se nenhum lado alcançou três pontos. **Único gatilho de reposição.**

## Sequência obrigatória

**Primeiro ciclo:** após validação e autorização expressa de iniciar partida, embaralhar cada monte e comprar 5 iniciais (setup). Esses saques **substituem**, e não se somam, à reposição de abertura do primeiro ciclo. Sorteio único de PRIMEIRO/SEGUNDO; sem novo sorteio nos demais ciclos.

**Fim de um combate:** validar KO, pontuar e preservar PV da sobrevivente, campos, mãos, montes, cemitérios e recursos. Não comprar. Se 3 pontos, encerrar a partida imediatamente.

**Abertura de novo ciclo (se o duelo continua):** registrar `INICIO_CICLO` com identificador de ciclo único; para **cada jogador** (J1 e J2) comprar do topo do respectivo monte `max(0, 5 - tamanho_da_mão)` cartas, limitado ao número de cartas disponíveis. Nunca comprar sexta carta e não inventar cartas. Registrar a janela de saque para ambos com idempotência, sem expor a mão do adversário.

**Depois do saque de ambos:** abrir troca de 0 a 5 por jogador com descarte e compra equivalente, desde que haja monte; selecionar/evoluir criatura (quantas evoluções legais as cartas já presentes na mão permitirem); PRIMEIRO e SEGUNDO escolhem 0/1 suporte da mão; resolver suporte do PRIMEIRO e do SEGUNDO, sem compra imediata; lançar iniciativa SRD e continuar combate por quantas rodadas internas forem necessárias até outro KO.

## Proibições

- Nada de compra por passagem de turno, início de rodada interna, invocação, evolução, suporte, fim imediato do KO ou benefício exclusivo do sobrevivente.
- Não realizar novo saque após o combate que entregar a terceira vitória.
- Não duplicar evento de abertura: `saque_ciclo` contém no máximo um processamento por `ciclo_id` e por jogador.
- Se o monte não comportar a reposição plena, completar somente o possível; resultado competitivo de esgotamento do monte continua sujeito à decisão própria.
- Não antecipar embaralhamento, compra, sorteio ou qualquer execução antes das validações mecânicas e autorização.

## Registro de alterações

Esta v1.9 **substitui as interpretações conflitantes** da reposição imediata pós-combate da v1.7 e da dúvida sobre significado de “rodada” da v1.8. Fecha **Q-17**. Mantém decisões sobre suportes pré-iniciativa (v1.3), luta até KO (v1.4), ordem fixa (v1.5) e evolução sem teto numérico (v1.6).
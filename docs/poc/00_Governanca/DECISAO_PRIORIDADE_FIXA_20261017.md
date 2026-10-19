# POC — Decisão aprovada: sorteio único de prioridade de preparação

**Data do registro:** 17/10/2026. **Status:** APROVADA para POC SRD Card Game humano vs IA.

## Declaração do administrador

> Aprovo manter PRIMEIRO e SEGUNDO definidos pelo sorteio inicial durante todos os ciclos do duelo. A iniciativa SRD continua independente a cada novo combate. Registre na POC, sem embaralhar ainda.

## Aplicação vinculante

- Realizar exatamente **um sorteio inicial** para designar PRIMEIRO e SEGUNDO no **duelo inteiro**, somente quando a partida for autorizada a começar e os bloqueios resolvidos.
- A ordem PRIMEIRO -> SEGUNDO fica **fixa em todos os ciclos seguintes**, incluindo troca de cartas, preparação da criatura, seleção do suporte e resolução sequencial de suportes, respeitadas outras regras aprovadas.
- **Proibido refazer o sorteio** quando uma criatura chegar a 0 PV e começar outro ciclo. A terceira vitória encerra imediatamente a partida.
- A **iniciativa SRD é independente**: cada novo combate realiza sua própria rolagem de iniciativa, que pode dar o primeiro turno a quem foi SEGUNDO na preparação. Turnos/rodadas dentro do mesmo combate mantêm a mesma iniciativa, salvo alguma alteração expressamente prevista na ficha/SRD.
- Registrar no estado da partida os IDs PRIMEIRO e SEGUNDO, identificador/evento do sorteio e a garantia `ordem_fixa_ate_fim_do_duelo = true`. No momento presente esses IDs são **nulos** porque o sorteio inicial **não ocorreu**.
- Esta decisão **não autoriza embaralhamento, compra de cartas, início de duelo ou execução de combate**.

## Relação com versões anteriores

Esta decisão resolve Q-01 quanto à frequência do sorteio e a parte remanescente de Q-14, sem substituir as regras aprovadas de suporte pré-batalha v1.3 nem a regra de combate até 0 PV v1.4. Não resolve a ordem fina da fase extra de saque/troca da criatura sobrevivente, limite de evoluções ou homologação de fichas e suportes.
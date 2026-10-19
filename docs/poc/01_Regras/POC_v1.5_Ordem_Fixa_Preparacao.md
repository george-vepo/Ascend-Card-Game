# SRD Card Game — POC v1.5 | Ordem fixa durante todo o duelo

**Registrado:** 17/10/2026. **Status:** decisão do administrador aprovada para a POC; partida ainda não iniciada.

## Regra aprovada — uma vez por duelo

Antes do primeiro ciclo de preparação, quando os decks e as regras indispensáveis estiverem aprovados, o árbitro realiza **um único sorteio** para estabelecer:

- `PRIMEIRO`: J1 ou J2 (resultado do sorteio único).
- `SEGUNDO`: o outro jogador.

A designação se mantém **imutável durante todos os ciclos daquele duelo**. Cada novo ciclo começa diretamente com a troca de cartas na mesma ordem. **Não há novo sorteio de PRIMEIRO/SEGUNDO após derrota.**

O sorteio inicial **ainda não foi realizado**. Não antecipar nem presumir qual jogador será PRIMEIRO.

## Sequência de ciclo (com ordem fixa)

1. PRIMEIRO faz a troca de cartas; SEGUNDO faz a troca legal.
2. PRIMEIRO seleciona/prepara sua criatura; SEGUNDO seleciona/prepara sua criatura.
3. PRIMEIRO escolhe **zero ou um** suporte da própria mão; SEGUNDO escolhe zero ou um suporte.
4. Suporte de PRIMEIRO é resolvido antes do de SEGUNDO, quando válido; se não houver suporte, pula a etapa. Descarte e reposição obedecem à POC v1.3.
5. **Cada combate** faz **nova rolagem de iniciativa SRD**, independentemente da prioridade de preparação. O resultado determina a ordem dos turnos naquele combate e permanece válido pelas rodadas desse combate, conforme SRD.
6. Combate continua por rodadas até uma criatura chegar a 0 PV. Perdedor vai ao cemitério, vencedor +1 ponto, criatura sobrevivente continua no campo com PV restantes.
7. Se alguém atingir 3 pontos, fim imediato do duelo. Senão, concluir fase extra pertinente da sobrevivente segundo o manual e **abrir outro ciclo com os mesmos PRIMEIRO/SEGUNDO**.

**Invariantes:** sem reiniciar mãos/montes/cemitérios; sem reembaralhar automaticamente; sem mudar PRIMEIRO/SEGUNDO no meio do duelo; sem reexecutar suporte na rodada seguinte. Caso de empate simultâneo/sem resultado continua sem regra aprovada.

## Estado de dados

O objeto `prioridade_preparacao` registra `primeiro`, `segundo`, `sorteio_evento_id`, `sorteio_realizado` e `ordem_fixa_ate_fim_do_duelo`. Antes da autorização de início: `primeiro=null`, `segundo=null`, `sorteio_evento_id=null`, `sorteio_realizado=false` e `ordem_fixa_ate_fim_do_duelo=true`.

## Fonte e precedência

Decisão expressa do administrador desta conversa, em complemento à POC v1.4 (combate até 0 PV), v1.3 (suportes antes da batalha) e manual v0.9. Nesta matéria de periodicidade da prioridade, **v1.5 prevalece** sobre qualquer indicação anterior de pendência ou novo sorteio. Não substitui SRD 5.2.1 para iniciativa/combate.

## Não aprovado por esta decisão

Limite de evoluções, mudanças de suporte confirmado, micro-ordem do saque/troca extra da sobrevivente, casos de morte simultânea, monte vazio, controles de habilidades passivas e fichas/suportes sem homologação. Continuam bloqueantes conforme sua ocorrência.

**Bloqueios mantidos:** nenhuma partida, nenhum sorteio, nenhum embaralhamento, nenhuma compra, nenhuma ação de combate executada.
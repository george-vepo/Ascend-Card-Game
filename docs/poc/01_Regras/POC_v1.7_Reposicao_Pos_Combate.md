# SRD Card Game — POC v1.7 | Reposição somente após o combate

**Aprovado pelo administrador em 17/10/2026.** Decisão específica da POC; substitui a regra de reposição automática imediata descrita no manual v0.9 e em documentos históricos da POC v1.1–v1.6 **somente quanto ao momento da reposição**. Não altera fichas, não homologa suportes e não inicia partida.

## Regra POC-17 — janela única da reposição automática

1. **Não repor automaticamente** a mão após invocação, qualquer evolução, encerramento de cadeia evolutiva ou resolução e descarte de suporte. Durante a preparação, o jogador usa exclusivamente as cópias que já tem na mão.
2. A **reposição automática até cinco cartas** de cada jogador só é permitida **após o término de um combate** (quando uma criatura é reduzida a 0 PV e o resultado é validado), na transição pós-combate. Não repor entre rodadas internas enquanto ambas as criaturas estão vivas.
3. No pós-combate: primeiro resolver o resultado (derrotada → cemitério; +1 ponto; sobrevivente mantém PV, condições e recursos pertinentes), depois verificar a mão de cada lado e comprar **somente a quantidade necessária para atingir cinco**, limitada às cópias efetivamente restantes no monte. Preservar ordem do monte, IDs e demais zonas; nenhum reembaralhamento ou cura automática.
4. **Exceções que não são reposição automática:** as cinco compras iniciais na abertura do duelo e a compra de igual quantidade de cartas descartadas voluntariamente na **fase de troca** continuam conforme regras aprovadas. A fase extra de saque/descarte/troca da criatura sobrevivente ocorre somente pós-combate, conforme o manual, mas sua micro-ordem com a reposição automática ainda exige homologação/decisão específica para evitar duplicar compras.
5. **Limite numérico de evoluções permanece ilimitado**, mas a cadeia usa apenas cópias da mão já disponíveis — nenhuma compra intermediária amplia a cadeia naquele ciclo. Idêntico para humano e IA.
6. **Suporte pré-batalha:** no máximo uma carta escolhida da mão (ou Sem suporte); resolver na ordem PRIMEIRO → SEGUNDO antes da iniciativa; carta efetivamente utilizada vai ao cemitério e **não gera reposição naquele momento**. O efeito já validado persiste por sua duração legal.
7. **Duelo a três pontos:** vitória final termina imediatamente, sem abrir novo ciclo. O destino operacional de eventuais compras puramente cosméticas após a vitória final não foi definido; não realizar transição de reposição para novo ciclo após a terceira vitória por suposição.

## Precedência e pendências

Esta decisão **encerra Q-15** (momento da reposição da mão na cadeia) e substitui a regra de compra imediata pós-suporte. Não resolve a micro-ordem **pós-combate** entre reposição automática dos dois jogadores e a fase extra do sobrevivente; registrar esta última como **Q-16 — ordem de reposição e troca extra do sobrevivente** antes de executá-la.

A escolha de suporte confirmada, mas com execução impedida, continua sem solução automática (Q-04/Q-13); morte simultânea, esgotamento do monte e fichas/habilidades incompletas continuam pendentes. Não inventar regras para situações não homologadas.

## Ciclo vigente em síntese

Sorteio **único** de PRIMEIRO/SEGUNDO na abertura do duelo → mão inicial de cinco por lado → troca conforme fase → primeiro prepara criatura e evolui usando **somente cartas da mão** → segundo faz o mesmo → escolha opcional de até um suporte de cada lado → resolução dos suportes na mesma ordem, sem reposição → iniciativa SRD independente → turnos até 0 PV → resultado, pontuação e reposição pós-combate (ordem da fase extra do sobrevivente pendente) → novo ciclo se não houver terceiro ponto.

## Critérios de aceite

- Invocar / evoluir / resolver suporte não aumenta a mão nem diminui o monte por reposição automática.
- Se o jogador ficar sem cartas na mão antes da iniciativa, não inventar novas cópias.
- Rodadas seguintes do **mesmo** combate não liberam reposição.
- Após combate validamente encerrado, a reposição automática do pós-combate respeita `max(0, 5 - quantidade_mao)` e `min(necessarias, quantidade_monte)` para ambos; compra nunca gera sexta carta.
- Compras da troca (descarte por compra igual) e distribuição inicial não são bloqueadas por POC-17.
- Cada operação conserva quarenta IDs únicos por lado, sem duplicação de cópias.
- A partida permanece **NÃO INICIADA**: nenhum sorteio, embaralhamento, compra, invocação ou combate realizado.
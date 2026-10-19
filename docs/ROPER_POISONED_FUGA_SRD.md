# Correção SRD 5.2.1 — Poisoned e fuga do Tentacle do Roper

## Contexto e regra

A Giant Owl (CE-001) pode receber as condições **Grappled** e **Poisoned** pela ação Tentacle do Roper (AB-POC-017). No SRD 5.2.1, *Ending a Grapple* permite usar uma **Action** para testar Strength (Athletics) ou Dexterity (Acrobatics) contra a CD de fuga (14, extraída da ficha do Roper). A condição **Poisoned** impõe **desvantagem nos testes de atributo e ataques**.

Portanto, o pedido de fuga deve conter a perícia escolhida pelo jogador e **dois d20 explícitos** quando Poisoned estiver ativa. O motor aplica o **menor**, soma o modificador da perícia, compara com a CD e registra ambos os dados e a fonte da desvantagem. Não faz sorteios internos. Um d20 único fica PENDENTE; dados impossíveis são REJEITADOS. Nenhuma declaração inválida ou pendente altera estados ou eventos aceitos.

Na fuga bem-sucedida, Grappled e Poisoned são retiradas junto ao vínculo com o tentáculo; na fuga fracassada, ambas permanecem. A ação consome o turno da fixture, independentemente do resultado. A habilidade continua limitada ao confronto Giant Owl × Roper, sem movimento ou arena.

Os bônus da Giant Owl vêm da ficha consultada no Catálogo SRD; a CD e o vínculo do tentáculo também. O arquivo genérico `src/ascend/testes_d20_srd.py` apenas resolve valores explicitamente informados e não fornece atributos da criatura. **Poisoned não impõe desvantagem em testes de resistência**, apenas em testes de atributo e ataques.

*Reel* continua PENDENTE enquanto a POC não tiver posicionamento aprovado. Nenhuma partida oficial foi iniciada; os testes usam dados simulados.

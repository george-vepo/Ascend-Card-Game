# Roper — Multiattack atômico nos casos já verificáveis

**Fonte de regras:** SRD 5.2.1 p. 320, ficha Roper AT-002 no Catálogo SRD externo pinado em `03f84e8426f469ef6a0e471faea2093b7c0b69c9`. **Regra de jogo:** contrato de 15/10/2026 confirmado em 19/10/2026, combate sem posição, arena, movimento ou alcance espacial.

## Incremento

`MULTIATTACK_ROPER_TESTE` recebe `aceite_escopo = "MULTIATTACK_ATOMICO_CASOS_SEM_GRAPPLE_DUPLO"`, **dois** lançamentos Tentacle associados a slots diferentes e **dois** Bite com seus d20 e dados de dano quando pertinentes. Os dados são todos simulados, explícitos, sem rolagem oculta do motor. Sem confirmação do escopo, a ação continua `PENDENTE`.

A execução usa **uma única Action**, com componentes na ordem exata da fonte: 2 Tentacle (CA, crítico sem dano e vínculo condicional) → Reel (sem deslocamento, porque não há posicionamento) → 2 Bite (CA, críticos 6d8, dano, resistências/imunidades). A próxima vez só muda ao final da Action. Ao causar KO no primeiro Bite, interrompe antes do segundo, limpa Grappled, move o derrotado para cemitério e soma **um** ponto, sem rodada ou evento extra.

## Limite de escopo — não inventar regras

- **No máximo um tentáculo pode ter vínculo Grappled com o mesmo alvo** neste recorte experimental. Se outro Tentacle acertar enquanto houver vínculo ativo — inclusive a segunda tentativa da mesma Action — a resolução retorna **PENDENTE**, sem qualquer alteração de estado, eventos, recursos, PV, zonas ou placar.
- O motivo não é arena: a ficha do Roper e a regra geral de uma parte corporal por grapple são verificáveis, mas ainda não há implementação validada para encerrar e controlar vínculos simultâneos no mesmo alvo. Não escolher arbitrariamente qual grapple termina em uma fuga.
- `prevalidar_multiattack()` permanece consulta pura, `executavel=false` para o conjunto **integral** de situações da ficha; acrescenta `executavel_parcial=true` e o escopo limitado acima.
- Multiattack não é cinco turnos; nem uma ação de suporte. Reel fora do Multiattack continua sua Action individual.
- Em fixture, um Multiattack sem alvo Grappled executa Reel como componente **sem efeito** entre os ataques; nenhuma aproximação ou consequência espacial é inferida.
- Não implementar Spider Climb, voo, deslocamento ou demais passivos por analogia.
- O catálogo não sofre alterações, e as identidades das 40 cartas por jogador permanecem preservadas.

## Integridade e testes

`tests/integration/test_roper_multiattack_atomic_safe_real.py` tem 16 cenários: ordem dos componentes, primeiro/segundo Tentacle, ausência de alvo em Reel, rollback quando dois Tentacle acertam, dois Bite com dano, crítico, KO no primeiro/segundo, parâmetros inválidos, escopo ausente, validação de vez, posição ignorada, idempotência, checkpoint e privacidade. Workflows devem aprovar os testes antes de merge.

## Próximo passo

Implementar estrutura de **múltiplos grapples por partes corporais** somente após conferir interpretação completa da ficha e definir/liberar por testes a semântica de fuga, dano/destruição de cada tentáculo e persistência das condições. Depois retirar o bloqueio de caso parcial para Multiattack integral; **não inventar posicionamento**.

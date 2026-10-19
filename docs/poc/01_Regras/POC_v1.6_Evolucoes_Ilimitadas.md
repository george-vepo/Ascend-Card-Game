# SRD Card Game — POC v1.6 | Evoluções sem limite numérico por ciclo

**Aprovado pelo administrador em 17/10/2026.** Aplicável apenas à POC humano Celestial vs IA Aberração. **Não inicia partida e não autoriza embaralhamento.**

## Regra POC-16 — Quantas evoluções forem legalmente possíveis

Durante a sua etapa de preparação da criatura de combate, cada jogador pode realizar **quantas evoluções consecutivas conseguir efetuar legalmente**, sem teto numérico arbitrário de 1, 2 ou 3 evoluções por ciclo.

Cada evolução individual exige:

1. Uma criatura própria atualmente ativa no campo; se a fase começar sem ativa, a invocação direta inicial exige carta **Comum** na mão.
2. **Uma carta real e disponível na mão** com a **mesma espécie de tipo** da ativa (mesmo **tipo do catálogo**, não espécie/nome necessariamente igual) e **classe imediatamente superior**: Comum → Incomum → Rara → Lendária → Mítica. Não saltar classe.
3. A antiga cópia sai do campo e vai ao cemitério, a nova cópia entra como única ativa e com **PV máximos da sua ficha integral**. O processo registra um evento próprio e verifica a partição das 40 cópias.
4. Só permitir o próximo passo se o novo estado e a próxima carta satisfizerem novamente todos os requisitos. A sequência termina quando o jogador decide parar ou não é possível prosseguir legalmente; a Mítica não tem classe superior homologada.
5. Regras idênticas a J1 e J2. A IA não pode inventar cartas da mão e não usa informações ocultas de J1 para decidir suas evoluções.

**Exemplo ilustrativo (não constitui compra nem jogada):** uma Comum do tipo Celestial poderia evoluir, em sequência, para uma Incomum, depois uma Rara e depois uma Lendária, **somente se todas essas cópias estiverem disponíveis e cada passo for validado**. Se faltar uma classe intermediária, a cadeia interrompe; uma Mítica não pode ser colocada diretamente no lugar da Comum.

## Limite implícito de recursos

'Quantas puder' não autoriza evolução gratuita, geração de carta, pulo de classe, invocação direta de classe alta ou superação dos limites de zona. Cada evolução consome uma cópia da mão, transfere a anterior ao cemitério e respeita a única criatura ativa.

## Questão operacional que permanece aberta

O manual v0.9 prevê reposição da mão até cinco após invocação/evolução, mas lista como lacuna o **momento exato da compra numa cadeia de evoluções**. Esta aprovação de quantidade **não escolhe** entre:

- **A. Reposição imediatamente após cada evolução validada**, podendo oferecer cartas adicionais para a próxima evolução da mesma preparação; ou
- **B. Reposição somente depois que o jogador encerrar sua sequência de evoluções**, restringindo a cadeia às cartas já presentes na mão durante a sequência.

**Ambas são propostas pendentes.** Até decisão explícita, não executar uma cadeia que dependa de compras intermediárias; não antecipar a compra por suposição. Mesmo após aprovação, nunca comprar sexta carta por reposição ou ultrapassar o monte existente.

## Ordem e interação com suporte

A criatura é preparada, com todas as evoluções legais daquele jogador, na ordem fixa PRIMEIRO → SEGUNDO (POC v1.5); somente **depois de ambas as preparações** cada lado escolhe 0 ou 1 suporte de sua própria mão. Suportes selecionados são resolvidos, na ordem PRIMEIRO → SEGUNDO, **antes da iniciativa** (POC v1.3). Combate até uma criatura chegar a 0 PV, com novo ciclo preservando recursos (POC v1.4).

## Auditoria

Registrar cada evolução como evento único com `copia_anterior_id`, `copia_nova_id`, `tipo_comprovado`, `classe_origem`, `classe_destino`, `PV_max_destino`, eventual compra legal de reposição, e estado-base E###. Falta de ficha integral, passo inválido e esgotamento de cartas bloqueiam o passo afetado, sem inventar atributos ou cartas.

**Ainda bloqueante para iniciar a partida:** homologação de fichas e habilidades, decisão sobre o tempo de reposição na sequência, demais exceções explicitadas em `00_Governanca/DECISOES_E_PENDENCIAS.md`. Zero sorteios, embaralhamentos e compras realizados.
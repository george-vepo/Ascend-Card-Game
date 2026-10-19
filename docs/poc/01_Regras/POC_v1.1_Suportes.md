# SRD Card Game — POC dentro do ChatGPT
## Especificação funcional v1.1 — seleção, reserva e ativação de suporte

**Data:** 16/10/2026  
**Situação:** decisões de suporte aprovadas para a POC; implementação não iniciada.  
**Escopo:** um jogador humano contra um oponente controlado pela IA, com arbitragem e combate conduzidos pelo ChatGPT. Não altera automaticamente o catálogo, a coleção, o site ou o manual principal.

### 1. Referências e precedência

- **Manual do Duelo de Criaturas SRD v0.9:** regras-base de deck, zonas, mão, invocação, evolução e combate.
- **Manual Operacional dos Chats v1.3:** separação das informações, histórico versionado e validação pelo árbitro.
- **SRD 5.2.1:** mecânicas de combate e fichas correspondentes.
- **Decisões de combate e suportes (15/10/2026):** regras gerais aprovadas para habilidade de suporte e seus limites; as habilidades individuais candidatas não são automaticamente homologadas.
- **Decisões desta conversa (16/10/2026):** seleção, reserva e janela de ativação do suporte na POC.

Em caso de divergência, respeitar a regra específica aprovada mais recente e sinalizar conflitos não resolvidos, sem criar regras novas silenciosamente.

### 2. Decisões aprovadas para a POC

**SUP-01 — Momento da seleção.** Cada jogador pode selecionar **no máximo uma carta de suporte da própria mão**, depois de concluída a preparação da criatura de combate (invocação/evolução) e **antes do início do combate**. Uma segunda carta não pode ser escolhida como suporte para o mesmo combate.

**SUP-02 — Reserva na mão.** A cópia selecionada continua na zona **MÃO**. Recebe a marca lógica `suporte_reservado = true` e fica indisponível para invocação, evolução, troca ou outro uso enquanto estiver reservada. A seleção **não** a envia ao campo nem ao cemitério, **não** cria uma nova zona e **não** gera compra de reposição: continua contando na quantidade de cartas da mão.

**SUP-03 — Momento da ativação.** A carta reservada pode ser ativada **durante o próprio turno**, **antes ou depois da ação principal**, desde que as condições da habilidade sejam satisfeitas. **Não** é permitida interrupção livre no turno adversário. A ativação do suporte não consome ação, ação bônus ou reação, conforme decisão anterior aprovada.

**SUP-04 — Resolução.** O árbitro valida o estado-base, o proprietário, a carta, a habilidade de suporte individualmente homologada, o alvo, os gatilhos e os recursos aplicáveis. Uma carta de suporte **aplica o efeito uma única vez por combate**. O efeito é resolvido com os números, CDs, testes, condições e durações da ficha correta; não se inventam habilidades. A regra geral dá prioridade de escolha **Cura → Buff → Debuff → Dano (último recurso)** na determinação da habilidade de suporte.

**SUP-05 — Descarte e reposição.** Após a ativação e a resolução, a cópia sai da mão e vai ao **CEMITÉRIO/DESCARTE**. O árbitro repõe a mão até **cinco cartas**, comprando do topo do monte, se houver cartas disponíveis. Não compra uma sexta carta por reposição e não cria cartas. Um efeito já aplicado pode persistir pelo prazo legal da habilidade, mesmo após o descarte.

**SUP-06 — Suporte não utilizado.** Se o combate terminar sem ativação, a marca de reserva é retirada e a **mesma cópia permanece na mão**, sem descarte e sem compra decorrente da liberação. A carta poderá voltar a ser considerada segundo as regras do combate seguinte.

**SUP-07 — Mesmo tratamento para a IA.** O oponente IA obedece às mesmas regras de escolha, reserva, janela de ativação, descarte e reposição. A identidade do suporte da IA permanece oculta para o jogador até a revelação exigida pela sua utilização.

**SUP-08 — Integridade e auditoria.** Cada cópia de carta tem ID próprio. Uma cópia reservada conta **uma única vez**, na mão do proprietário. O árbitro registra ação, validação, uso do suporte, efeito, descarte, compra e versão do estado (`E###`), e confere que cada deck continua com exatamente 40 cópias distribuídas pelas zonas válidas.

### 3. Fluxo da POC até o combate

1. **Novo duelo:** criar ID da sessão e identificar humano (J1) e IA (J2).
2. **Decks:** conferir 40 cópias válidas de cada jogador, sem duplicar IDs; distinguir decks de teste das coleções oficiais.
3. **Embaralhamento e mão inicial:** registrar a ordem gerada e comprar cinco cartas por lado; não revelar mão nem ordem do monte adversário.
4. **Troca:** aplicar a troca de 0–5 cartas segundo o manual.
5. **Preparação da criatura:** invocar Comum e, quando permitido, evoluir pelo mesmo tipo e classe imediatamente superior; repor mão conforme o manual.
6. **Seleção de suporte:** cada jogador escolhe a sua carta da mão e confirma a reserva, antes da iniciativa. O painel exibe o suporte reservado ao próprio dono, mas não revela a carta rival.
7. **Iniciativa:** estabelecer a ordem de turnos conforme as regras e as decisões vigentes.
8. **Combate:** o controlador decide suas ações. Em seu turno, poderá ativar o suporte reservado antes ou depois da ação principal, quando a habilidade for válida. A IA arbitra, lança ou identifica dados simulados e registra resultados.
9. **Fim do combate:** criatura a zero PV é movida ao cemitério, a sobrevivente mantém os PV restantes, o vencedor ganha um ponto, e reservas não utilizadas são liberadas. A partida termina quando um lado chega a três vitórias.

**Nota:** esta sequência representa o fluxo proposto para a POC, com as decisões de suporte aprovadas. Outras lacunas de fases e arena permanecem sujeitas às aprovações vigentes; não devem ser supridas por analogia.

### 4. Interface na mesa

**Durante a preparação:** mostrar a criatura ativa, a mão numerada (até cinco cartas após as operações), um indicador de seleção e um painel com a habilidade candidata, sua origem e seus pré-requisitos. A ação **Confirmar suporte** bloqueia a cópia escolhida. Não haverá uma quinta zona física de cartas: o espaço visual “Suporte reservado” é apenas uma representação da marca na mão.

**Durante o combate:** mostrar placar, fase, ator da vez, duas criaturas ativas, CA/PV/condições, quantidades das zonas e histórico recente. Na mão do jogador, destacar a carta reservada e oferecer **Ativar suporte** somente em turno e momento permitidos; mostrar a IA adversária com a mão oculta. Ao ativar, exibir o efeito, o envio ao cemitério e a compra de reposição. Uma carta sem habilidade homologada não deve oferecer ativação efetiva.

**Ao final do combate:** remover a marca `suporte_reservado` de toda carta não utilizada, mantendo-a na mão. Não zerar mãos, montes, cemitérios ou PV da criatura sobrevivente.

### 5. Estados e eventos mínimos

```text
Carta: { id_copia, id_criatura, zona: MAO|MONTE|CAMPO|CEMITERIO,
         suporte_reservado: boolean }
Combate: { id_partida, estado_E, indice_combate, rodada, turno,
           jogador_da_vez, placar, criatura_ativa_J1, criatura_ativa_J2,
           suporte_reservado_J1?, suporte_reservado_J2? }
Eventos: SELECAO_SUPORTE, ATIVACAO_SUPORTE, EFEITO_APLICADO,
         DESCARTE_SUPORTE, COMPRA_REPOSICAO, LIBERACAO_RESERVA
```

O campo `suporte_reservado_J1/J2` **referencia** um ID que continua na zona MÃO, não corresponde a uma cópia adicional. Eventos devem ter identificadores únicos para evitar execução duplicada. A IA adversária e o árbitro são papéis lógicos no mesmo ChatGPT, **sem isolamento técnico verificável** de informações privadas.

### 6. Critérios de aceite da POC

- **CT-01:** selecionar suporte válido marca uma carta da mão, sem removê-la nem comprar reposição.
- **CT-02:** carta reservada não pode ser invocada, evoluída, trocada nem reservada novamente.
- **CT-03:** ativação antes ou depois da ação principal, no próprio turno, é admitida se a habilidade for válida.
- **CT-04:** ativação durante o turno adversário é recusada e não modifica o estado.
- **CT-05:** ativação válida aplica **uma vez**, registra efeitos, descarta a cópia e repõe a mão até cinco quando houver monte.
- **CT-06:** suporte não ativado retorna ao estado normal da mão no fim do combate, sem compra ou descarte.
- **CT-07:** os mesmos procedimentos são exigidos do oponente IA, sem revelar antecipadamente sua carta reservada.
- **CT-08:** nenhuma operação duplica cartas ou altera o total de 40 cópias por deck; eventos são registrados em sequência auditável.
- **CT-09:** habilidade candidata não homologada permanece indisponível para resolução oficial.
- **CT-10:** a IA não afirma ter executado rolagem verificável sem mecanismo de sorteio verificável.

### 7. Pendências explícitas (não aprovadas por esta revisão)

1. **Seleção obrigatória ou opcional:** a regra aprovada limita a seleção a uma carta por combate, mas ainda não estabelece expressamente o procedimento para quem não puder ou não quiser selecionar uma.
2. **Alteração da escolha antes de começar o combate:** definir se a reserva confirmada pode ser substituída ainda na preparação.
3. **Efeitos passivos, contínuos e baseados em gatilhos:** homologar individualmente sua conciliação com a regra de uma aplicação por combate, sobretudo regeneração e concentração.
4. **Demais lacunas do manual v0.9:** ordem detalhada entre jogadores, limites de evolução, empate, esgotamento do monte e reinícios; aplicar somente decisões já aprovadas e pedir deliberação para o restante.
5. **Segurança competitiva:** esta POC usa isolamento apenas lógico entre árbitro e adversário IA; não comprova sigilo técnico ou imparcialidade reproduzível entre agentes distintos.

### 8. Registro de mudança v1.0 → v1.1

**Adicionado:** limite de uma cópia de suporte selecionada da mão após a criatura de combate e antes do início da batalha; reserva lógica na mão; bloqueio de outros usos; ativação no próprio turno antes/depois da ação principal; proibição de interrupção livre de turno adversário; descarte e reposição após ativação; liberação da reserva ao fim do combate quando não utilizada; telas, estados e critérios de teste correspondentes.

**Não alterado:** manual base, catálogo, fichas e estado de partidas existentes. **Nenhuma partida foi iniciada por este documento.**
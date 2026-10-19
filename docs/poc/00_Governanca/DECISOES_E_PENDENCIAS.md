> **POC-21 — DIRETRIZ VIGENTE (17/10/2026): fichas sob demanda.** Confirmada a existência de **80/80 arquivos individuais** de ficha nos decks Celestial/Aberração (40/40 cada, posições 01–40). Não usar ausência de *homologação integral* como bloqueio global da POC; prosseguir com interface, fluxo, estados e testes não mecânicos. Consultar fichas existentes apenas quando necessário. Se faltar realmente ficha ou dado essencial para resolver uma jogada, suspender **somente essa operação**, sem inventar valores. A seleção **Sem suporte** permanece válida. Nenhum embaralhamento foi autorizado. Veja `01_Regras/POC_v2.1_Fichas_Sob_Demanda.md`.

---

> **REGRA VIGENTE POC-20 (17/10/2026): KO por suporte pré-iniciativa encerra imediatamente o combate e dá 1 ponto ao controlador do suporte; o segundo suporte reservado permanece na mão sem consumo (reserva liberada), não há iniciativa e o próximo saque de ambos só ocorre na abertura do próximo ciclo, se não houve o terceiro ponto.** Consulte `01_Regras/POC_v2.0_KO_Pre_Iniciativa.md`. Esta decisão fecha o item de **KO** de Q-13, mas NÃO homologa poderes nem resolve morte simultânea; quaisquer anotações históricas de “KO pré-batalha pendente” estão superadas.


---

# Registro de decisões e pendências — POC 1.6

> **REGRA VIGENTE — POC v1.9 (17/10/2026), decisão do administrador.** **Rodada de saque** significa somente a **abertura de um novo ciclo de preparação após o combate anterior acabar com uma criatura a 0 PV**, desde que ninguém tenha alcançado 3 pontos. Nesse instante, **AMBOS os jogadores repõem suas mãos até 5 cartas** a partir do topo de seus montes, conforme disponibilidade. Não há saque no encerramento do KO, ao passar rodadas/turnos do mesmo combate, após invocação, evolução ou suporte, nem saque extra da criatura sobrevivente. Compras iniciais e compras equivalentes aos descartes na fase de troca continuam distintas. **Q-17 resolvida.** Esta regra posterior prevalece sobre as versões v1.7 e v1.8 nos pontos conflitantes.


## Aprovado (aplicável exclusivamente à POC)

- **POC-01:** J1 humano x J2 IA, com arbitragem pelo ChatGPT; um único estado de partida registrado.
- **POC-02:** suporte é selecionado **da mão**, depois da preparação da criatura de combate (invocação/evolução) e antes de iniciar o combate.
- **POC-03:** **no máximo uma** cópia selecionada como suporte por jogador e por combate.
- **POC-04:** suporte confirmado **permanece na mão**, marcado `suporte_reservado`, indisponível para qualquer outro uso; reserva não compra carta nem cria outra zona.
- **POC-05 (SUPERADA em v1.3):** a antiga ativação no próprio turno foi substituída pela resolução pré-batalha. Não aplicar em paralelo.
- **POC-06:** ativar não consome ação/ação bônus/reação; cada cópia de suporte aplica um efeito por combate; após resolver, é descartada **sem reposição imediata**; a mão será reposta apenas no pós-combate (POC-17).
- **POC-07 (casos sem aplicação):** suporte não resolvido por ausência de seleção continua na mão; situações de reserva já confirmada mas com resolução inviável não são decididas por analogia.
- **POC-08:** mesmo tratamento para J1 e J2; mão, suporte reservado e ordem do monte de J2 não são exibidos ao humano.
- **POC-09 (aprovada nesta conversa):** a seleção de suporte é **OPCIONAL**. Cada jogador pode confirmar **zero ou uma** carta da própria mão depois de preparar sua criatura e antes do início do combate. **Sem suporte** é uma escolha válida inclusive quando não há habilidade homologada disponível. Ao confirmar zero, `suporte_reservado_id = null`, nenhuma carta é bloqueada, descartada ou comprada pela escolha, e não há ativação de suporte naquele combate. J1 e J2 obedecem igualmente. Esta aprovação não homologa habilidades candidatas. A janela de ativação foi alterada posteriormente por POC-12.

- **POC-10 — PRIORIDADE (complementada por POC-15):** um sorteio **único por duelo** define PRIMEIRO/SEGUNDO e fixa essa ordem para todos os ciclos. Sorteio **independente** da iniciativa SRD; nenhum sorteio foi realizado.
- **POC-11 — ORDEM:** troca de ambos os lados, criatura do primeiro, criatura do segundo, suporte do primeiro, suporte do segundo, resolução do suporte do primeiro, resolução do suporte do segundo, início do combate com iniciativa SRD e continuidade após rodada/combate.
- **POC-12 — SUPORTES PRÉ-BATALHA:** ativação/resolução das cartas selecionadas ocorre **antes da iniciativa**, não no próprio turno de combate. Conservar 0–1 suporte da mão, reserva lógica, aplicação única por combate, descarte sem reposição imediata; repor só após o combate (POC-17), sem gasto da economia de ações.
- **POC-13 — LIMITES (parcialmente resolvido por POC-16):** interações de suporte pré-iniciativa e revisão de fichas permanecem pendentes; limite numérico de evoluções aprovado em POC-16; o significado da nova rodada/ciclo foi resolvido por POC-14.
- **POC-14 — CICLO E COMBATE ATÉ 0 PV:** um combate continua por múltiplas rodadas até uma das criaturas chegar a 0 PV. Somente então +1 ponto ao vencedor, perdedora ao cemitério, sobrevivente com PV remanescentes, demais zonas e recursos preservados; se ninguém atingiu 3 pontos, **começa outro ciclo de preparação**. Não repetir suportes nem preparação a cada rodada interna. Primeiro a 3 pontos encerra imediatamente.

- **POC-15 — PRIORIDADE FIXA NO DUELO:** PRIMEIRO/SEGUNDO são definidos exclusivamente pelo sorteio inicial e permanecem os mesmos durante TODOS os ciclos do duelo; não refazer sorteio após cada combate. A iniciativa SRD é rolada novamente **em cada novo combate**, independentemente da ordem fixa de preparação. Nenhum sorteio executado ou início autorizado.

**POC-16 — EVOLUÇÕES SEM LIMITE NUMÉRICO:** durante a preparação da sua criatura, o jogador pode fazer quantas evoluções consecutivas conseguir cumprir, sempre com carta da mão, mesmo tipo, classe imediatamente superior, antiga carta ao cemitério e nova carta com PV máximos. Sem saltos ou cartas criadas. **Q-02 resolvida.** **POC-17 definiu a reposição exclusivamente no pós-combate**, sem compras na cadeia; **Q-15 resolvida**. Fonte: `01_Regras/POC_v1.6_Evolucoes_Ilimitadas.md`.

## Regras documentadas anteriores preservadas

- Dois decks virtuais independentes, autorizados exclusivamente para a POC, de 40 cópias identificadas; 5 cartas iniciais para cada lado; uma criatura ativa por lado.
- Invocação direta só de Comum; evolução mesmo tipo e raridade imediatamente superior, sem pular; substituída ao cemitério; evoluída entra com PV máximos.
- Troca 0 a 5 cartas da mão, descartando e comprando igual quantidade, sem reembaralhar.
- Combate por SRD 5.2.1 e ficha correta (com decisões posteriores aplicáveis); primeiro a três vitórias vence; sobrevivente mantém PV.
- Suporte extraído de habilidade que realmente consta na ficha da edição correta, com prioridade de escolha de habilidade Cura > Buff > Debuff > Dano; candidatos não homologados não são ativáveis oficialmente.
- Regra posterior aprovada para este formato: sem movimentação, posicionamento e cálculos de alcance; demais requisitos/efeitos continuam válidos. **Sinalizar divergências com fontes mais antigas.**

## Propostas / questões ainda bloqueantes

| ID | Tema | Situação | Ação necessária |
|---|---|---|---|
| Q-01 | Prioridade e sequência de preparação | **RESOLVIDO (POC-15):** único sorteio inicial fixa PRIMEIRO/SEGUNDO por TODO o duelo; sem re-sorteio nos novos ciclos | Aplicar sequência POC-11 e registrar prioridade no estado |
| Q-02 | Limite de evoluções antes do combate | **RESOLVIDO (POC-16): quantas consecutivas forem legalmente possíveis, sem limite numérico** | Conferir requisitos e registrar cada evolução |
| Q-03 | Seleção opcional vs obrigatória de suporte, ou ausência de elegível | **RESOLVIDO — seleção 0–1; Sem suporte permitido** | POC-09 |
| Q-04 | Alterar suporte já confirmado antes da sua resolução | Aberto | Decisão do administrador |
| Q-05 | Habilidades passivas e com gatilhos/duração, incluindo regeneração | Homologação individual faltante | Não ativar sem validação |
| Q-06 | Monte vazio: resultado competitivo e continuação | Aberto | Decisão quando relevante |
| Q-07 | Mortes simultâneas, combate travado / sem dano | Aberto | Decisão antes de adjudicar |
| Q-08 | Destino/resultado da criatura ativa fora de combate em substituição voluntária | Aberto | Não permitir por analogia |
| Q-09 | Aprovação das fichas completas de ambos os decks escolhidos | Parcial | Ver `03_Dados/AUDITORIA_INICIAL_DECKS.md` |
| Q-10 | Homologação individual dos suportes selecionáveis | **Pendente** | Validar uma ou mais habilidades em ficha integral, sem inventar efeitos |
| Q-11 | IDs `AB-REF-001...040` e cópias para o duelo | **RESOLVIDO apenas na POC**: AB-POC-001..040, sem atribuir propriedade às coleções | Ver `DECISAO_DECKS_VIRTUAIS_POC.md` |
| Q-12 | Persistência verificável entre sessões do ChatGPT | Não implementada | Checkpoints explícitos; não prometer banco de dados |
| Q-13 | Suportes antes da iniciativa: efeitos por turno, concentração, cura/dano e KO pré-batalha | Aberto | Homologação individual e decisão se ocorrer |
| Q-14 | Sentido de “outra rodada” e novo ciclo | **RESOLVIDO (POC-14):** combate até 0 PV; próximo ciclo só após derrota e se ninguém atingiu 3 pontos | **POC-15 resolveu a frequência do sorteio (uma única vez no duelo)**; micro-ordem pós-combate continua pendente |

| Q-15 | Momento da reposição até 5 numa cadeia de evoluções | **RESOLVIDO (POC-17): somente após o fim do combate** | Não comprar entre evoluções ou ao encerrá-las |
| Q-16 | Micro-ordem pós-combate da reposição e do saque/troca extra da sobrevivente | **ABERTO** | Aprovar ordem operacional para não duplicar compras |

## Itens que não são regras novas

A tela ilustrativa, o schema JSON e o plano de teste são **contratos de implementação**. Não definem poderes, bônus ou exceções de combate. A POC não dá, por si, propriedade de cartas experimentais ao usuário.

**Precedência v1.6:** `01_Regras/POC_v1.6_Evolucoes_Ilimitadas.md` e `00_Governanca/DECISAO_EVOLUCOES_SEM_LIMITE_20261017.md` prevalecem para o limite numérico de evoluções. **Precedência v1.5:** `01_Regras/POC_v1.5_Ordem_Fixa_Preparacao.md` e `00_Governanca/DECISAO_PRIORIDADE_FIXA_20261017.md` sobre frequência de sorteio, em complemento às regras anteriores. **Precedência v1.4:** `01_Regras/POC_v1.4_Ciclos_e_Combate.md` e `00_Governanca/DECISAO_CICLO_COMBATES_20261016.md` para término de combate/novo ciclo; `01_Regras/POC_v1.3_Fases_e_Suportes.md` e `00_Governanca/DECISAO_FLUXO_SORTEIO_SUPORTES_20261016.md` para ordem das fases e ativação de suporte.


**POC-17 — REPOSIÇÃO AUTOMÁTICA SOMENTE NO PÓS-COMBATE (17/10/2026):** não há compra para repor até cinco após invocar, evoluir, terminar evolução nem usar suporte; reposição automática para os dois jogadores só após o combate efetivamente terminar com derrota a 0 PV, antes de preparar o próximo confronto (a micro-ordem com a fase extra da sobrevivente é Q-16, pendente). As compras iniciais de cinco e as compras por troca com descarte igual continuam permitidas. Q-15 encerrada. **Precedência:** `01_Regras/POC_v1.7_Reposicao_Pos_Combate.md` prevalece sobre qualquer instrução antiga de reposição imediata.

## POC-18 — correção aprovada: saque simétrico no início da rodada

- **Aprovado:** saque dos **DOIS** jogadores no início da **rodada**; nada de saque/descarte/troca especial só para a criatura sobrevivente. A regra anterior de saque imediatamente pós-combate (POC-17/v1.7) está **superada quanto ao gatilho**.
- **Não aprovado nem inferido:** um saque adicional pós-KO, compra após suporte/invocação/evolução, ou saque duplicado no encerramento/início.
- **Q-16 (substituída por Q-17):** a pergunta da ordem da fase extra da sobrevivente é encerrada por INAPLICABILIDADE: essa fase não existe na POC vigente.
- **Q-17 (RESOLVIDA por POC-19):** `rodada` de saque é a abertura do novo ciclo após KO, exceto fim de partida a 3 pontos. Ambos repõem até cinco antes da troca; nunca a cada rodada do mesmo combate.
- **Fichas e habilidades de suporte:** continuam pendentes de homologação. A partida não foi iniciada e não houve sorteio.

## POC-19 — decisão posterior e prevalente (17/10/2026)

- O saque de **ambos** acontece **somente na abertura de cada novo ciclo de preparação**, depois de encerrado o combate anterior e se o duelo ainda não atingiu 3 pontos. Comprar do topo **até completar 5**; se o monte terminar, comprar apenas o que existir.
- **Não** comprar ao resolver KO; **não** comprar em cada rodada interna do combate; **não** comprar após invocação/evolução/suporte. Primeira distribuição de cinco e compras substitutivas da troca são exceções distintas.
- Eliminar a fase extra de saque/troca exclusiva da sobrevivente. Manter PV restantes no campo e demais zonas persistentes.
- **Q-17 RESOLVIDA.** A parte da POC-17 que fixava a compra no pós-combate imediato e as frases de v1.8 com ambiguidade da rodada são **históricas, não vigentes**.
- A ordem de saque no novo ciclo é após a abertura `INICIO_CICLO` e **antes da troca**, sem re-sortear a prioridade fixa.
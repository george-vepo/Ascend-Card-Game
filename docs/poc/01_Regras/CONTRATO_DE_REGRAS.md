> **POC-21 — DIRETRIZ VIGENTE (17/10/2026): fichas sob demanda.** Confirmada a existência de **80/80 arquivos individuais** de ficha nos decks Celestial/Aberração (40/40 cada, posições 01–40). Não usar ausência de *homologação integral* como bloqueio global da POC; prosseguir com interface, fluxo, estados e testes não mecânicos. Consultar fichas existentes apenas quando necessário. Se faltar realmente ficha ou dado essencial para resolver uma jogada, suspender **somente essa operação**, sem inventar valores. A seleção **Sem suporte** permanece válida. Nenhum embaralhamento foi autorizado. Veja `01_Regras/POC_v2.1_Fichas_Sob_Demanda.md`.

---

> **REGRA VIGENTE POC-20 (17/10/2026): KO por suporte pré-iniciativa encerra imediatamente o combate e dá 1 ponto ao controlador do suporte; o segundo suporte reservado permanece na mão sem consumo (reserva liberada), não há iniciativa e o próximo saque de ambos só ocorre na abertura do próximo ciclo, se não houve o terceiro ponto.** Consulte `01_Regras/POC_v2.0_KO_Pre_Iniciativa.md`. Esta decisão fecha o item de **KO** de Q-13, mas NÃO homologa poderes nem resolve morte simultânea; quaisquer anotações históricas de “KO pré-batalha pendente” estão superadas.


---

# Contrato de execução do árbitro — POC humano vs IA

> **REGRA VIGENTE — POC v1.9 (17/10/2026), decisão do administrador.** **Rodada de saque** significa somente a **abertura de um novo ciclo de preparação após o combate anterior acabar com uma criatura a 0 PV**, desde que ninguém tenha alcançado 3 pontos. Nesse instante, **AMBOS os jogadores repõem suas mãos até 5 cartas** a partir do topo de seus montes, conforme disponibilidade. Não há saque no encerramento do KO, ao passar rodadas/turnos do mesmo combate, após invocação, evolução ou suporte, nem saque extra da criatura sobrevivente. Compras iniciais e compras equivalentes aos descartes na fase de troca continuam distintas. **Q-17 resolvida.** Esta regra posterior prevalece sobre as versões v1.7 e v1.8 nos pontos conflitantes.


## Precedência

1. Manual do Duelo de Criaturas SRD v0.9, para regras específicas de cartas, fases e zonas.
2. Decisões posteriores **explicitamente aprovadas** pelo administrador: suporte 15/10, POC 16/10 (registro 00), sem converter hipóteses em lei.
3. Ficha integral da criatura correta e SRD 5.2.1 para combate, limites e efeitos. Distinguir SRD e material externo/homebrew.
4. Manual de chats v1.3 para exibição, histórico e proteção de informações; adaptar os três papéis para árbitro + adversário IA dentro da mesma sessão, sem afirmar isolamento técnico real.

Em caso de conflito: identificar o documento, a data e a decisão posterior aplicável. Se não houver precedência inequívoca, a ação fica PENDENTE.

## Evolução de criaturas — POC v1.6

- **Não existe teto numérico por ciclo:** na etapa do controlador, permitir quantas evoluções sucessivas forem válidas, cada uma exigindo carta da mão, tipo idêntico e **classe imediatamente superior**. Antes da primeira evolução de um campo vazio, a invocação direta exige uma carta Comum.
- Por evolução, mover a ativa ao cemitério, colocar a carta selecionada no campo com PV máximos, registrar evento independente e validar as 40 cópias; não inventar carta/ficha e não saltar etapas. O jogador pode parar.
- **POC-19 (prevalece sobre POC-17):** nenhuma reposição durante a invocação/evolução/cadeia; reposição apenas na abertura do próximo ciclo elegível. Q-15 resolvida. A cadeia usa apenas cartas já disponíveis na mão.

## Mecânica de suporte consolidada

- Categoria visual do suporte: Cura, Buff, Debuff ou Dano, conforme habilidade **individualmente homologada**.
- Cada jogador escolhe **zero ou uma** carta da própria mão por combate. Escolher **Sem suporte** confirma a etapa sem reserva (`null`), descarte, reposição ou ativação; uma carta pode ser reservada e continuará na mão, indisponível para outras operações.
- **Janela v1.3:** resolver suportes do PRIMEIRO e SEGUNDO, nessa ordem, antes de rolar iniciativa e antes da batalha; não ativar suportes durante turnos de combate. A norma pré-batalha substitui a antiga janela no próprio turno.
- Após ativação: resolver efeito uma vez; mover carta da mão ao cemitério; **não repor a mão nesse momento**. Reposição somente na abertura do próximo ciclo elegível conforme POC-19.
- Habilidades passivas, gatilhos e duração precisam de tratamento individual, não criar reaplicações por recarga.
- **Sem suporte** na fase de seleção: não reservar, ativar, descartar ou comprar. Se houver carta reservada e ocorrer impedimento na resolução, marcar PENDENTE sem alterar zona/carta por suposição.

## Formato de combate e restrições

A decisão de 15/10 para o Card Game elimina mecânicas de movimentação, posicionamento e alcance espacial. Isso **não** elimina validação de alvo, requisitos não espaciais, condições, CDs, dano, concentração, economia de ações, reações e recursos. Se uma habilidade não puder ser traduzida sem criar regra, impedir o uso e pedir deliberação.

As habilidades das criaturas em campo seguem sua própria ficha e economia de ações, não o limite de 1 aplicação de suporte por combate.

## Ordem da POC v1.5 (v1.3 + v1.4 + prioridade fixa)

1. Após validações e autorização, sorteio **único para todo o duelo** de PRIMEIRO/SEGUNDO **para preparação**, separado da iniciativa SRD. A ordem não muda nos ciclos seguintes.
2. Troca de 0–5, para ambos em ordem de preparação, sem revelar a mão adversária.
3. PRIMEIRO prepara criatura e pode evoluir tantas vezes quanto legalmente conseguir; SEGUNDO faz o mesmo. Não realizar reposição após nenhuma evolução; a POC-19 permite repor somente na abertura do próximo ciclo.
4. Primeiro escolhe zero ou um suporte de sua mão; segundo faz o mesmo.
5. Primeiro resolve suporte, se válido; segundo resolve suporte, se válido; descarte sem reposição imediata; a reposição só ocorre no começo do próximo ciclo elegível (POC-19).
6. **Somente então** rolar **nova iniciativa SRD para cada novo combate** e iniciar combate; novos turnos dentro desse mesmo combate não repetem seleção de suporte.
7. **Dentro do mesmo combate:** continuar turnos e rodadas na iniciativa vigente **até uma criatura chegar a 0 PV**; não repetir suporte por rodada.
8. **Fim do combate:** criatura derrotada ao cemitério, +1 ponto ao vencedor, sobrevivente fica no campo com PV atuais; preservar mãos, ordem dos montes, cemitérios, recursos e histórico. Se um lado alcançar **3 pontos**, encerrar imediatamente, sem preparação adicional.
9. Se ninguém alcançou 3 pontos, **abrir novo ciclo de preparação**, repor a mão **de ambos** até 5 (se houver cartas no monte), uma vez no início desse ciclo, e então conduzir a fase de troca e a preparação na ordem fixa de PRIMEIRO/SEGUNDO. **Não** conceder saque/troca extra à sobrevivente; **não** refazer o sorteio PRIMEIRO/SEGUNDO.

Se a primeira resolução de suporte inviabilizar o segundo suporte, ou uma criatura cair a zero antes da iniciativa, **suspender a transição** e solicitar regra aprovada. Não declarar vitória automática por inferência.

## Protocolo por ação

1. Verificar ID de duelo, estado-base `E###`, jogador da vez, fase, cópia e zona.
2. Verificar que o jogador humano declarou explicitamente a escolha; J2 IA pode decidir apenas suas próprias ações, usando apenas informação acessível a J2.
3. Se a ação for inválida: REJEITADA, **sem qualquer alteração**.
4. Se faltar ficha, decisão ou recurso: PENDENTE, **sem qualquer alteração**.
5. Se válida: resolver por ordem da ficha/SRD, identificar dados como verificáveis ou simulados, calcular PV/condições/recursos, registrar evento idempotente.
6. Validar a partição de **40 IDs únicos para cada deck** nas quatro zonas oficiais e inexistência de carta em duas zonas.
7. Publicar resultado público e a próxima ação; nunca publicar carta oculta de J2 antecipadamente.

## Segurança do protótipo

Não confiar exclusivamente no histórico em linguagem natural para persistência. O modelo em `04_Estado/` é um template, não uma partida em andamento. Uma partida real necessita checkpoint explícito após alterações relevantes. Não afirmar que tela dinâmica isolada compartilha estado com arquivos da Biblioteca automaticamente.

**Referência vigente de prioridade:** `01_Regras/POC_v1.5_Ordem_Fixa_Preparacao.md`; fases: `01_Regras/POC_v1.3_Fases_e_Suportes.md`; combate/ciclos: `01_Regras/POC_v1.4_Ciclos_e_Combate.md`. As versões 1.1/1.2 ficam como histórico, não como instruções de ativação concomitantes.

**Referências vigentes:** evolução sem teto na v1.6; reposição somente pós-combate em `01_Regras/POC_v1.7_Reposicao_Pos_Combate.md`. Q-02 e Q-15 resolvidas; Q-16 (micro-ordem pós-combate) pendente.


## Precedência mais recente — POC-17

Nenhuma reposição automática depois de invocação, evolução (mesmo no fim da cadeia) ou descarte de suporte. Após a conclusão do combate por KO validado, proceder à reposição até cinco do topo do monte de cada jogador, sem gerar sexta carta, respeitando a ordem de compra ainda pendente com a fase extra do sobrevivente (Q-16). **Exceções distintas da reposição:** mão inicial de cinco e compra de quantidade igual à descartada na fase de troca. Não repor nas rodadas internas do mesmo combate. Não iniciar próximo ciclo após terceiro ponto.

## Precedência operacional v1.9 — saque dos dois apenas na abertura do ciclo

1. Ao registrar o KO, apenas resolver derrota, pontuação, recursos e zonas; **não comprar no mesmo evento**.
2. Se alguém alcançou três pontos, encerrar a partida sem novas compras ou preparação.
3. Caso contrário, abrir **um único** novo ciclo, registrar `INICIO_CICLO` e **repor simultaneamente como direito**, em execuções auditadas por jogador, a mão de J1 e J2 **até cinco**, comprando do topo quando possível. Garantir idempotência para não comprar duas vezes no mesmo ciclo.
4. Só depois dessa reposição conduzir a troca de cartas e as demais fases já aprovadas. Não existe saque especial do sobrevivente; não há saque no começo de rodadas internas do mesmo combate.
5. A v1.7 e partes das seções históricas acima que determinavam reposição ao KO estão superadas. Q-16 e Q-17 estão resolvidas.

## POC-20 — validação de KO pré-iniciativa (vigente)

Se a primeira resolução de suporte homologado causar KO, descartar apenas o primeiro suporte utilizado, liberar a reserva não usada do segundo suporte, registrar 1 ponto e encerrar sem rolar iniciativa. Sem saque no momento do KO. Se 3 pontos, encerrar a partida; senão, iniciar o próximo ciclo e repor até 5 para ambos no INÍCIO desse ciclo. Rejeitar resoluções duplicadas do mesmo evento. Empate/morte simultânea: pendente.
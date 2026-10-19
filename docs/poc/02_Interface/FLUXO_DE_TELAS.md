> **POC-21 — DIRETRIZ VIGENTE (17/10/2026): fichas sob demanda.** Confirmada a existência de **80/80 arquivos individuais** de ficha nos decks Celestial/Aberração (40/40 cada, posições 01–40). Não usar ausência de *homologação integral* como bloqueio global da POC; prosseguir com interface, fluxo, estados e testes não mecânicos. Consultar fichas existentes apenas quando necessário. Se faltar realmente ficha ou dado essencial para resolver uma jogada, suspender **somente essa operação**, sem inventar valores. A seleção **Sem suporte** permanece válida. Nenhum embaralhamento foi autorizado. Veja `01_Regras/POC_v2.1_Fichas_Sob_Demanda.md`.

---

> **REGRA VIGENTE POC-20 (17/10/2026): KO por suporte pré-iniciativa encerra imediatamente o combate e dá 1 ponto ao controlador do suporte; o segundo suporte reservado permanece na mão sem consumo (reserva liberada), não há iniciativa e o próximo saque de ambos só ocorre na abertura do próximo ciclo, se não houve o terceiro ponto.** Consulte `01_Regras/POC_v2.0_KO_Pre_Iniciativa.md`. Esta decisão fecha o item de **KO** de Q-13, mas NÃO homologa poderes nem resolve morte simultânea; quaisquer anotações históricas de “KO pré-batalha pendente” estão superadas.


---

# Design das telas e navegação — POC ChatGPT v1.7

> **REGRA VIGENTE — POC v1.9 (17/10/2026), decisão do administrador.** **Rodada de saque** significa somente a **abertura de um novo ciclo de preparação após o combate anterior acabar com uma criatura a 0 PV**, desde que ninguém tenha alcançado 3 pontos. Nesse instante, **AMBOS os jogadores repõem suas mãos até 5 cartas** a partir do topo de seus montes, conforme disponibilidade. Não há saque no encerramento do KO, ao passar rodadas/turnos do mesmo combate, após invocação, evolução ou suporte, nem saque extra da criatura sobrevivente. Compras iniciais e compras equivalentes aos descartes na fase de troca continuam distintas. **Q-17 resolvida.** Esta regra posterior prevalece sobre as versões v1.7 e v1.8 nos pontos conflitantes.


**Identidade visual:** fantasia sombria, fundo `#0B1219`, painéis `#172732`, dourado discreto `#D6B47A`, controles legíveis. Imagem é ilustração de referência, não fonte mecânica.

## Tela 01 — Abertura

**Novo duelo contra IA**; **Continuar partida** somente após checkpoint oficial válido; **Regras** e **Catálogo** são consultas. Sem backend web obrigatório: interface dentro do ChatGPT.

## Tela 02 — Seleção de decks e validações

J1 humano / deck Celestial (CE-001..CE-040); J2 IA / deck Aberração (AB-POC-001..040, referência AB-REF). Informar claramente: decks virtuais autorizados **apenas para POC**, 40 IDs por lado, fichas e suportes ainda não homologados individualmente. A tela não oferece embaralhamento até a aprovação dos bloqueios.

## Tela 03 — Prioridade e troca

- Após autorização futura da partida, realizar **um único sorteio rastreável/simulado identificado POR DUELO** para determinar quem começa a preparação: PRIMEIRO e SEGUNDO. **Manter mesma ordem nos ciclos seguintes.**
- Ambos trocam de 0 a 5 cartas da própria mão, na ordem PRIMEIRO → SEGUNDO. Não revelar a mão nem a ordem do monte de J2.
- Não confundir esta prioridade com **iniciativa**; iniciativa será sorteada na tela de batalha.

## Tela 04 — Seleção das criaturas (primeiro e segundo)

- PRIMEIRO prepara criatura ativa; SEGUNDO realiza procedimento equivalente.
- Invocação direta: somente Comum; evolução com carta na mão, mesmo tipo e classe imediatamente superior, nova criatura com PV máximos, anterior no cemitério.
- **POC-16 aprovada:** evoluções consecutivas sem limite numérico; validar **cada passo**, sempre mesmo tipo e classe imediatamente superior, consumindo carta da mão; a criatura substituída vai ao cemitério e a nova entra com PV máximos. Campo: zero ou uma criatura ativa por jogador.
- Exibir botão **Evoluir novamente** somente para próxima carta legal disponível; opção **Encerrar evolução**. Somente ausência real de dado mecânico indispensável bloqueia a operação concreta; não bloquear toda a etapa pela homologação geral ainda em andamento. **POC-17/Q-15 resolvida:** não exibir compra de reposição após invocação, entre evoluções nem quando o jogador encerra a sequência; reposição somente após o combate.
- Mostrar nomes/CA/PV das criaturas ativas como informação pública, mas não expor a mão de J2.

## Tela 05 — Seleção de suporte (primeiro e segundo)

- PRIMEIRO escolhe 0 ou 1 suporte de sua própria mão; SEGUNDO faz o mesmo.
- **Sem suporte** é permitido para ambos; sem compra, reserva ou descarte.
- Selecionado: marca `suporte_reservado` na MÃO, indisponível para outros usos até a resolução; não cria zona nem repõe mão.
- Mostrar habilidade candidata, origem e status de homologação; bloquear confirmação de efeito não homologado.
- Identidade da seleção da IA permanece oculta enquanto for privada.

## Tela 06 — Resolução pré-batalha dos suportes

- Painel sequencial: **Suporte do PRIMEIRO → Suporte do SEGUNDO**; se escolha foi zero, pular a etapa correspondente.
- Resolver apenas habilidade individualmente homologada, aplicável antes da batalha; registrar modificadores, dados/CD, PV/condições/duração e recursos. Descartar cópia efetivamente usada, **sem compra de reposição nesta tela**. Apenas pós-combate ocorre a reposição automática (POC-17).
- Revelar à mesa a carta/efeito quando ativada; nunca revelar outras cartas da mão adversária.
- Se um efeito requer turno/iniciativa ou provoca KO antes do combate, bloquear e solicitar decisão, sem inventar adaptação.
- Proibir ativação de suporte durante o combate nesta versão.

## Tela 07 — Mesa de batalha SRD

- Primeiro rolar iniciativa após os suportes; somente este resultado estabelece a ordem de turnos.
- Exibir ID, E###, combate, rodada, turno, placar, campos (nome/tipo/ND/classe/ID, CA, PV, condições, recursos), mãos/monte/cemitério por quantidade, log auditável.
- Ações: Atacar, Habilidade, Magia, Ficha, Histórico, Encerrar turno; sem botão **Ativar suporte**.
- Usar combate SRD 5.2.1 conforme decisões posteriores: **sem movimentação, posicionamento e alcance espacial**. Não remover requisitos não espaciais.
- Rolagens verificáveis se houver ferramenta verificável; caso contrário, identificar como simuladas.

## Tela 08 — Rodadas, fim do combate e novo ciclo

- **Ambas as criaturas acima de 0 PV:** mostrar **Próxima rodada** do mesmo combate, conservar iniciativa, campo e efeitos em curso; não exibir novo menu de troca/invocação/suporte.
- **Uma criatura chega a 0 PV:** apresentar resultado, mover derrota ao cemitério, acrescentar 1 ponto, manter sobrevivente com PV atuais, preservar mãos, ordem dos montes, cemitérios e recursos.
- **Primeiro a 3 pontos:** tela **Vitória final**, sem novo ciclo.
- **Nenhum lado chegou a 3 pontos:** apresentar **pós-combate**, incluindo reposição até cinco de ambos os jogadores (limitada pelo monte) e fase extra de saque/descarte/troca da sobrevivente conforme manual. **Q-16:** a ordem relativa desses dois procedimentos está pendente de aprovação; somente após sua execução abrir **Novo ciclo**. A criatura sobrevivente permanece no campo, sem cura automática.
- **Atenção:** PRIMEIRO/SEGUNDO são fixos por todo o duelo; não apresentar novo sorteio ao abrir o ciclo seguinte. A iniciativa de **cada novo combate** é própria e independente. Fase extra da sobrevivente continua exigindo ordem operacional aprovada.

## Responsividade

Desktop: campo humano/IA lado a lado. Mobile: painéis empilhados. Cartas reais apenas após identidade e arte verificadas; falta de imagem não bloqueia ficha textual. Componentes visuais e estados não substituem homologação mecânica.

**Status:** design documentado, não jogo iniciado.


**Atualização v1.7:** compras iniciais e por troca continuam; reposições automáticas ocorrem SOMENTE após combate encerrado por 0 PV; nenhuma após invocar/evoluir/suporte ou por passagem de rodada. Registrar pendência Q-16 antes da fase extra do sobrevivente.

## Tela e fluxo vigentes — POC v1.9

- Em `NOVO_DUELO`, após validação e autorização, compra inicial de cinco para ambos (sem compra de abertura duplicada do ciclo 1).
- **Ao KO:** mostrar resultado/placar e estado da sobrevivente sem comprar carta.
- **Ao clicar `Iniciar próximo ciclo`** (somente se ninguém atingiu 3): primeiro registrar `INICIO_CICLO`; comprar do topo para J1 e J2 somente o necessário para **até cinco cartas**; mostrar quantidades, sem revelar mão da IA.
- Depois dessa compra, oferecer a fase de **Troca** e, em seguida, preparação das criaturas e suportes, na ordem fixa.
- Em `COMBATE`, botão/controle de compra permanece indisponível mesmo em novas rodadas de turnos. Não existe fase extra exclusiva de saque da sobrevivente.

## Ramo pré-batalha POC-20

Ao resolver suporte 1, avaliar `PV_inimigo == 0`: se sim, exibir resultado do combate/placar, mover derrotado ao cemitério, liberar reserva de suporte 2 **sem revelá-lo/consumi-lo**, pular iniciativa e ir ao próximo ciclo ou tela final. Se não houver KO, resolver suporte 2; se este causar KO, o mesmo encerramento imediato se aplica. Só rolar iniciativa se ambos os combatentes ainda tiverem PV positivos.
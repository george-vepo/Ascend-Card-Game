> **POC-21 — DIRETRIZ VIGENTE (17/10/2026): fichas sob demanda.** Confirmada a existência de **80/80 arquivos individuais** de ficha nos decks Celestial/Aberração (40/40 cada, posições 01–40). Não usar ausência de *homologação integral* como bloqueio global da POC; prosseguir com interface, fluxo, estados e testes não mecânicos. Consultar fichas existentes apenas quando necessário. Se faltar realmente ficha ou dado essencial para resolver uma jogada, suspender **somente essa operação**, sem inventar valores. A seleção **Sem suporte** permanece válida. Nenhum embaralhamento foi autorizado. Veja `01_Regras/POC_v2.1_Fichas_Sob_Demanda.md`.

---

> **REGRA VIGENTE POC-20 (17/10/2026): KO por suporte pré-iniciativa encerra imediatamente o combate e dá 1 ponto ao controlador do suporte; o segundo suporte reservado permanece na mão sem consumo (reserva liberada), não há iniciativa e o próximo saque de ambos só ocorre na abertura do próximo ciclo, se não houve o terceiro ponto.** Consulte `01_Regras/POC_v2.0_KO_Pre_Iniciativa.md`. Esta decisão fecha o item de **KO** de Q-13, mas NÃO homologa poderes nem resolve morte simultânea; quaisquer anotações históricas de “KO pré-batalha pendente” estão superadas.


---

# Plano de testes — SRD Card Game POC no ChatGPT

> **REGRA VIGENTE — POC v1.9 (17/10/2026), decisão do administrador.** **Rodada de saque** significa somente a **abertura de um novo ciclo de preparação após o combate anterior acabar com uma criatura a 0 PV**, desde que ninguém tenha alcançado 3 pontos. Nesse instante, **AMBOS os jogadores repõem suas mãos até 5 cartas** a partir do topo de seus montes, conforme disponibilidade. Não há saque no encerramento do KO, ao passar rodadas/turnos do mesmo combate, após invocação, evolução ou suporte, nem saque extra da criatura sobrevivente. Compras iniciais e compras equivalentes aos descartes na fase de troca continuam distintas. **Q-17 resolvida.** Esta regra posterior prevalece sobre as versões v1.7 e v1.8 nos pontos conflitantes.


## Objetivo

Comprovar fluxo de abertura -> decks -> mão -> invocação/evolução -> suporte -> primeiro turno e resolução de combate, com histórico auditável. Nada aqui afirma testes concluídos.

## Estratégia

- **T0 Estrutura:** verificar pastas, modelos de estados, nomes e referências dos decks.
- **T1 Integridade:** dois decks de 40 IDs efetivos, independentes, sem duplicidades; todo ID aparece exatamente em uma zona oficial.
- **T2 Fases:** opção legal/ilegal de troca, invocação/evolução, momento da reserva e iniciativa.
- **T3 Suporte:** selecionar 0 ou 1 na mão, aceitar **Sem suporte** para humano/IA (inclusive sem carta elegível), impedir segundo suporte, impedir uso da carta reservada, exigir habilidade homologada e efeito único, resolução sequencial pré-batalha antes da iniciativa, descarte **sem reposição imediata**; validar reposição somente pós-combate, rejeitar ativação no turno de combate.
- **T4 IA adversária:** agir apenas no próprio turno, não explorar mão do jogador em decisões táticas, ocultar escolhas J2 na saída pública. Limitação: isolamento apenas por instrução, não tecnicamente demonstrável.
- **T5 Combate:** d20 e modificadores, crítico, multiataque quando houver, resistências, magias, efeitos e recursos, PV remanescente, primeira terceira vitória.
- **T6 Persistência:** eventos idempotentes; ação repetida não aplica dano de novo; checkpoint E### recuperável sem resetar zonas.

## Critérios globais

1. Nenhuma ação sem ficha verificada ou regra necessária aprovada.
2. Nenhuma rolagem descrita como verificável quando for simulada.
3. Nenhuma carta duplicada ou comprada além do monte.
4. Nenhuma mão/topo do monte da IA revelada; a IA árbitra pode internamente acessar ambos os lados, mas a interface não mostra.
5. Não há sucesso de POC se o efeito de suporte vier exclusivamente de candidato não homologado.

## Bloqueios atuais

- Homologar sob demanda apenas efeitos realmente resolvidos em ações concretas; não bloquear os testes estruturais por homologação em massa.
- IDs virtuais `AB-POC` já atribuídos para a POC; falta homologação de efeitos/fichas.
- Sequência de preparação v1.3, combate até 0 PV v1.4 e prioridade fixa para todos os ciclos v1.5 aprovados. Limite numérico de evolução **resolvido em v1.6**; **Q-15 resolvida em v1.7:** nenhuma reposição automática até o pós-combate; permanecem a micro-ordem dessa reposição com a fase extra da sobrevivente (Q-16) e efeitos pré-batalha complexos.

Os casos atômicos estão em `CASOS_TESTE.json`; `resultado` inicia sempre como `NAO_EXECUTADO`.

## Acréscimo de testes v1.3

- Prioridade sorteada da preparação **não** substitui a iniciativa do combate.
- Troca de ambos, seleção de criatura, seleção de suporte, resolução de suporte e iniciativa seguem ordem expressa.
- A antiga ativação no turno do combate é rejeitada, sem mutação do estado.
- Se suporte causa KO antes da iniciativa ou depende de turno, solicitar regra; não improvisar.
- Se o mesmo combate segue a outra rodada, não reabrir suportes.

Todos os cenários seguem `NAO_EXECUTADO`; nenhum sorteio/embaralhamento ocorreu.

## T7 — Combate até 0 PV / próximo ciclo (decisão POC-14)

- Se ambos ainda têm PV acima de zero após uma rodada, manter mesmo combate, iniciativa, turnos, efeitos e recursos; não repetir seleção/resolução de suportes.
- No KO validado, terminar **aquele** combate, enviar derrotada ao cemitério, pontuar exatamente 1, preservar a criatura sobrevivente com PV restantes e estado persistente.
- Se a pontuação alcançar 3, encerrar o duelo imediatamente; caso contrário, iniciar outro ciclo de preparação, preservando zonas e recursos e respeitando a fase extra da sobrevivente.
- Nunca sortear prioridade PRIMEIRO/SEGUNDO no novo ciclo: reutilizar exatamente a ordem do sorteio único inicial (POC-15).
- Simultaneous KO e situações sem resultado permanecem pendentes (não criar empate por analogia).

## T8 — Prioridade única do duelo (decisão POC-15 / v1.5)

- Antes do início autorizado: `primeiro=null`, `segundo=null`, `sorteio_realizado=false`; nenhuma rolagem é inventada.
- Uma única ocorrência de sorteio de prioridade determina ambos os papéis, com IDs diferentes e evento auditável; não confundir com iniciativa.
- Ao abrir o segundo ou qualquer outro ciclo: manter PRIMEIRO/SEGUNDO e proibir um novo sorteio de preparação.
- A cada novo combate: nova iniciativa SRD, mesmo quando o primeiro a atuar em combate não é PRIMEIRO na preparação.
- Durante as rodadas do mesmo combate: conservar iniciativa salvo efeito da ficha que legalmente a altere.
- Uma tentativa de alterar PRIMEIRO/SEGUNDO no meio do duelo deve ser REJEITADA sem alterar o estado.

Esses cenários são especificados e não executados. Embaralhamento e compra continuam bloqueados.

## T9 — Evoluções sem limite numérico (POC-16)

- Aceitar cada evolução legal em sequência (Comum → Incomum → Rara → Lendária → Mítica), com cartas existentes, classe adjacente e tipo idêntico.
- Permitir ao jogador encerrar a sequência voluntariamente; não forçar evolução.
- Rejeitar tentativa de salto de classe, mudança de tipo, evolução sem cópia válida, acima de Mítica ou com duas ativas.
- Registrar antigo campo → cemitério, novo campo com PV máximos e eventos únicos, sem duplicidade entre as 40 cópias.
- Testar cadeia que exigiria nova carta comprada: **REJEITAR compras intermediárias** conforme POC-17. Só cartas já disponíveis na mão podem ampliar a cadeia.

Testes apenas definidos; **0 executados**.


## T10 — Reposição somente pós-combate (POC-17)

- Confirmar que invocação, evolução individual, fim da cadeia e descarte de suporte **não** repõem a mão; monte inalterado por essas ações.
- Em rodadas seguintes do mesmo combate, não liberar reposição.
- Após KO e placar atualizados, testar reposição até cinco para ambos, limitada à disponibilidade do monte, e sem sexta carta.
- Verificar exceções: mão inicial de cinco e compra igual ao descarte na fase de troca.
- Quando a fase extra do sobrevivente coexistir com reposição pós-combate, **Q-16 impede presumir a micro-ordem**; não duplicar saques.
- Todos os cenários adicionados continuam `NAO_EXECUTADO`; partida ainda não autorizada.

## T11 — Correção do saque POC-18 (ainda não executado)

- Ao final do combate (KO), testar que **não há compra automática no próprio evento**.
- Não conceder qualquer fase de compra/troca extra ao sobrevivente; os dois jogadores têm o mesmo gatilho de saque.
- Na abertura da rodada, após a decisão Q-17, permitir saque para ambos no momento aprovado, sem exceder o limite aplicável, sem carta além do monte e sem compras duplicadas.
- Antes de Q-17, tentativa de saque de rodada fica **PENDENTE sem mudança de estado**, inclusive sem sorteio/embaralhamento.
- Revisar os testes históricos de T10 e CT anteriores: afirmações de pós-combate e fase extra sobrevivente são SUPERADAS.

## T12 — POC-19, saque no início do novo ciclo (substitui T10/T11 no conflito)

- Dado um combate com 2 criaturas sobrevivendo após uma rodada: **nenhuma compra**.
- Dado KO com placar ainda inferior a três: **nenhuma compra no evento de KO**; abrir o ciclo seguinte e completar **J1 e J2 até 5** uma só vez cada antes da troca.
- Dada mão com quatro cartas, comprar uma; mão com cinco, comprar zero; monte insuficiente, comprar somente o disponível; não criar sexta carta.
- Dado terceiro ponto: encerrar sem abrir novo ciclo e sem compras.
- No primeiro ciclo: cinco cartas iniciais no setup, mas nenhum segundo gatilho de reposição de abertura.
- Preservar `PRIMEIRO/SEGUNDO` sem novo sorteio, PV do sobrevivente, descarte, recursos e IDs únicos.
- Os testes antigos que exigiam compra imediata pós-KO, bloqueio por Q-17, ou fase extra do sobrevivente são históricos e **não aplicáveis**.

## Casos POC-20 e lote02 (17/10/2026)

Total **77** cenários de teste registrados, TODOS `NAO_EXECUTADO` (CT-67 a CT-77 são novos). KO por suporte antes da iniciativa, preservação do segundo suporte, idempotência, vitória por terceiro ponto e ficha/fonte separada de homologação. Ver `03_Dados/HOMOLOGACAO_SUPORTES_LOTE02_20261017.md`.

## Pesquisa externa lote 03

CT-78 a CT-80 documentam fontes externas de Ahu-Nixta Drudge, Light Eater e Maw Swarm e a ausência de homologação automática entre sistemas. **80 testes, todos não executados.** Ver `03_Dados/VALIDACAO_FONTES_EXTERNAS_LOTE03_20261017.md`.

## Execução experimental do motor de comandos v2.2 (17/10/2026)

Testes separados dos 84 casos históricos: 55 testes automatizados contra a implementação `07_Motor_Experimental/v22/motor_poc.py`; **55 passaram, zero falhas**. A regressão com o simulador de referência anterior (84 cenários) foi repetida separadamente: 80 passaram (43 estruturais, 37 com resultados artificialmente injetados); CT-11, CT-20, CT-75, CT-83 não executados. Uma demonstração do motor novo consumiu 24 eventos artificiais, 2 combates, 3 ciclos; preservou 40 cartas de cada lado, registrou ações com hashes, validou exportação JSON contra schema histórico a cada evento. Nenhum teste se aplica à partida oficial, nem homologa habilidade/atributo de ficha. Artefatos individuais em `07_Motor_Experimental/`.


## Execução de integração SRD parcial — v2.3 (17/10/2026)

- Testes mecanicamente delimitados `07_Motor_Experimental/v23/test_combate_srd.py`: **30 executados e aprovados**. Incluem iniciativa por dados simulados, modificadores oficiais de dois monstros, ordem por iniciativa, ataques documentados, d20 1/20, crítico (dobrar dados), validação estrita de dados, bloqueio de habilidades não integradas, rodada seguinte, KO, conservação de zonas, idempotência, privacidade, checkpoint restaurável e dados inválidos.
- Reexecutado motor v2.2: **55/55 aprovados**; regressão estrutural anterior: **80/84**, com CT-11, CT-20, CT-75, CT-83 não executados. **Não são 169 testes independentes de combate completo**: os 84 são cenários isolados de fluxo e parte deles usa resultados injetados.
- Demo determinística `demo_combate_srd.py`: 19 eventos aceitos, sete ataques, KO, PV remanescentes persistidos e saque somente na abertura do próximo ciclo; schema JSON validado a cada evento. Não contabilizar isso como partida oficial.
- Pendências: passivos e habilidades especiais, magia, ações bônus, reações, recursos, concentração, defesa/salvaguardas, implementações restantes das fichas; prioridade aleatória e rolagem verificável não foram introduzidas.


## Bateria isolada da implementação v2.4 (17/10/2026)

**48 testes adicionais executados e aprovados** para efeitos SRD parciais: salvaguarda SAB de Gibbering, d8 1–6, d8 7–8 pendente, Blinding Spittle DES CD 10, resistência radiante, duração de Blinded, vantagem/desvantagem, recarga 5–6, pré-condições de ação, dados simulados, idempotência, controle das 40 cópias, checkpoint e projeção JSON. Essas verificações são da implementação específica, separadas dos 84 cenários gerais anteriores. Evidência: `07_Motor_Experimental/v24/RESULTADOS_TESTES_V2_4.json`; demonstração pública em `07_Motor_Experimental/Execucoes_Isoladas/20261017/v24/`. **Não** marcar os casos CT-11/20/75/83 como executados, nem afirmar homologação de combate SRD completo.

## Regressão adicional v2.5 — executada isoladamente

A suíte modular de combate experimental foi executada em quatro módulos: **55 testes v2.2**, **30 v2.3**, **48 v2.4** e **55 v2.5**, somando **188/188 aprovados**. A suíte independente antiga manteve 43 testes estruturais aprovados, 37 *stubs* aprovados e quatro não executados (CT-11, CT-20, CT-75, CT-83), sem falhas. O caso de uso v2.5 verifica ação bônus *Divine Aid* (2/dia, Cure Wounds 2d8+5) e ação Multiattack do Deva no mesmo turno, consumo de recursos, limites de PV, idempotência, checkpoints, iniciativa simulada e integralidade das 40 cópias por jogador. Documentos: `07_Motor_Experimental/v25/RELATORIO_IMPLEMENTACAO_V2_5.md` e `RESULTADOS_TESTES_V2_5.json`. Nenhuma partida oficial foi iniciada.

## Integração de compatibilidade — registro paralelo (18/10/2026)

O experimento de orquestração de **quatro perfis legados (v2.2–v2.6)** foi arquivado em `07_Motor_Experimental/Compatibilidade_Motores_Legados_20261018/`. Possui **304 testes locais aprovados** (270 testes históricos desses módulos + 34 testes da API de compatibilidade), quatro demonstrações de dados simulados, checkpoints de fixture verificados e nenhuma publicação de dados privados. **Não** substitui a versão canônica `v27/`, que trata de concentração SRD, nem as versões técnicas posteriores `v28+` e `v6.x` já existentes na Biblioteca. O arquivo do orquestrador conserva o nome histórico `orquestrador_srd_v27.py` apenas dentro desse ramo de compatibilidade.

A variante v2.6 de ações lendárias que estava pendente de gravação foi recuperada em `07_Motor_Experimental/v26/Lendarias_Separadas/`. A v2.6 de reações permanece no seu local original. Os testes de movimentação são um **estudo SRD que não constitui regra da POC sem posicionamento**. Nenhuma nova regra competitiva, carta ou efeito de suporte foi homologado. Nenhuma partida oficial iniciada, sem embaralhamento, compras, rolagens ou mudança do placar 0 × 0.
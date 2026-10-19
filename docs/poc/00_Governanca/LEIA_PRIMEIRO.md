> **POC-21 — DIRETRIZ VIGENTE (17/10/2026): fichas sob demanda.** Confirmada a existência de **80/80 arquivos individuais** de ficha nos decks Celestial/Aberração (40/40 cada, posições 01–40). Não usar ausência de *homologação integral* como bloqueio global da POC; prosseguir com interface, fluxo, estados e testes não mecânicos. Consultar fichas existentes apenas quando necessário. Se faltar realmente ficha ou dado essencial para resolver uma jogada, suspender **somente essa operação**, sem inventar valores. A seleção **Sem suporte** permanece válida. Nenhum embaralhamento foi autorizado. Veja `01_Regras/POC_v2.1_Fichas_Sob_Demanda.md`.

---

> **REGRA VIGENTE POC-20 (17/10/2026): KO por suporte pré-iniciativa encerra imediatamente o combate e dá 1 ponto ao controlador do suporte; o segundo suporte reservado permanece na mão sem consumo (reserva liberada), não há iniciativa e o próximo saque de ambos só ocorre na abertura do próximo ciclo, se não houve o terceiro ponto.** Consulte `01_Regras/POC_v2.0_KO_Pre_Iniciativa.md`. Esta decisão fecha o item de **KO** de Q-13, mas NÃO homologa poderes nem resolve morte simultânea; quaisquer anotações históricas de “KO pré-batalha pendente” estão superadas.


---

# SRD Card Game — POC ChatGPT | Índice operacional

> **REGRA VIGENTE — POC v1.9 (17/10/2026), decisão do administrador.** **Rodada de saque** significa somente a **abertura de um novo ciclo de preparação após o combate anterior acabar com uma criatura a 0 PV**, desde que ninguém tenha alcançado 3 pontos. Nesse instante, **AMBOS os jogadores repõem suas mãos até 5 cartas** a partir do topo de seus montes, conforme disponibilidade. Não há saque no encerramento do KO, ao passar rodadas/turnos do mesmo combate, após invocação, evolução ou suporte, nem saque extra da criatura sobrevivente. Compras iniciais e compras equivalentes aos descartes na fase de troca continuam distintas. **Q-17 resolvida.** Esta regra posterior prevalece sobre as versões v1.7 e v1.8 nos pontos conflitantes.


**Versão do conjunto:** 1.5, atualizado em 17/10/2026 (prioridade de preparação fixa por todo o duelo).  
**Objetivo:** prova de conceito de jogo conduzido dentro do ChatGPT, um humano (J1) contra um oponente IA (J2); ChatGPT também é árbitro. **Este diretório é documentação/artefatos da POC; nenhuma partida foi iniciada.**

**Regras vigentes POC-09 a POC-14:** suporte opcional de zero ou uma carta da mão; sorteio para prioridade de preparação e resolução de suporte antes da iniciativa. Consultar **`01_Regras/POC_v1.3_Fases_e_Suportes.md`**; v1.1/v1.2 permanecem apenas como histórico das decisões anteriores.

## Pastas

- `00_Governanca/`: índice, escopo, decisões e pendências; distingue aprovado de proposto.
- `01_Regras/`: v1.3 com fluxo sorteado e suportes resolvidos antes da iniciativa; v1.1/v1.2 são versões históricas.
- `02_Interface/`: tela inicial, preparação, seleção de suporte, mesa e resultado; contrato de interação.
- `03_Dados/`: **referências** dos decks reais existentes na Biblioteca e auditoria inicial; não copia nem altera os decks.
- `04_Estado/`: modelo de estado de partida, zonas, cópias, reserva e eventos. **Modelos vazios não são estados oficiais.**
- `05_Testes/`: critérios e cenários de teste sem execução simulada apresentada como real.
- `06_Prompts/`: prompt de início da POC e separação lógica de árbitro/IA adversária.

## Fontes de verdade já existentes (não duplicar)

- `/SRD Card Game/Decks/Celestial/` — manifesto e registros das 40 cartas CE-001..CE-040, fichas e suportes candidatos.
- `/SRD Card Game/Decks/Aberração/` — manifesto, registros de 40 entradas e suportes experimentais.
- `/SRD Card Game/Fichas/` e `/SRD Card Game/Imagens/` — fontes de fichas e artes; conferir origem/estado.
- `/SRD Card Game/Controle/` — filas e controle de conteúdos; não usar como estado de duelo.
- `manual_completo_duelo_criaturas_SRD_v0_9.pdf` (Biblioteca) — regras específicas do card game.
- `SRD_Card_Game_Manual_Completo_dos_Chats_v1.3_Imagens_Web-1.docx` — operação de chats, como referência; o modo humano vs IA é adaptação da POC.
- `SRD_CC_v5.2.1.pdf` — combate SRD.
- Decisões aprovadas de combate/suporte em `operational/research/decks/aberracao-40-20261014/DECISOES_COMBATE_E_SUPORTES_40_20261015.md` (repositório do projeto).

**Versão operacional vigente:** ler `01_Regras/POC_v1.6_Evolucoes_Ilimitadas.md` e `00_Governanca/DECISAO_EVOLUCOES_SEM_LIMITE_20261017.md` para evolução sem teto numérico (Q-02 resolvida, Q-15 em aberto). Também ler primeiro `01_Regras/POC_v1.5_Ordem_Fixa_Preparacao.md` e `00_Governanca/DECISAO_PRIORIDADE_FIXA_20261017.md` para prioridade de preparação, e ler também `01_Regras/POC_v1.4_Ciclos_e_Combate.md` e `00_Governanca/DECISAO_CICLO_COMBATES_20261016.md`, com prevalência sobre qualquer indefinição anterior quanto à rodada e ao próximo ciclo.

## Rotina de uma execução de teste

1. Ler `01_Regras/POC_v1.3_Fases_e_Suportes.md`, `01_Regras/CONTRATO_DE_REGRAS.md`, `00_Governanca/DECISOES_E_PENDENCIAS.md` e `00_Governanca/DECISAO_FLUXO_SORTEIO_SUPORTES_20261016.md`.
2. Ler os **manifests originais** e validar exatamente 40 IDs por jogador e a existência dos 40 arquivos de ficha de cada deck; consultar a mecânica integral da carta ou suporte somente quando a jogada concreta a exigir.
3. Não sortear, comprar nem atualizar placar antes das decisões bloqueantes e dos decks válidos.
4. Abrir as telas conforme `02_Interface/FLUXO_DE_TELAS.md`.
5. Validar declaração -> resolver ação -> conferir invariantes -> emitir evento único `E###` e resumo público.
6. Em caso de erro ou lacuna: suspender somente a ação afetada; **não** improvisar regras.

## Limitações transparentes

Uma tela interativa no ChatGPT não significa backend permanente ou isolamento técnico da mão entre agentes. O árbitro e o adversário são papéis lógicos no mesmo modelo. Dados do acervo e competências dos agentes podem estar incompletos. Nunca apresentar resultados de cartas candidatas como homologados.

**Não mexer no GitHub, não gerar ZIP, não criar cópias de baralhos e não disparar jobs.**

**Atualização v1.3:** o início da preparação é determinado por sorteio (não é iniciativa); a ordem é troca, criaturas, seleção de suportes, resolução do suporte do primeiro e segundo, então iniciativa/combate. **Não ativar suporte durante turnos**, regra anterior substituída. Passo “outra rodada” foi esclarecido em v1.4: lutar até 0 PV, depois outro ciclo se ninguém tiver 3 pontos. **POC v1.5 aprovada: sorteio PRIMEIRO/SEGUNDO uma única vez por duelo; ordem fixa em todos os ciclos, iniciativa SRD independente para cada combate.** Nenhuma partida/sorteio foi iniciado.

**Regra v1.5:** a frequência do sorteio está fechada. Não mudar PRIMEIRO/SEGUNDO ao iniciar novo ciclo. Nenhum sorteio realizado, embaralhamento, compra ou partida iniciada.

**Atualização v1.6 (17/10/2026):** durante a preparação, permitir quantas evoluções individuais forem legais, nunca pulando classe nem criando cartas. A reposição da mão após cada passo ou no fim da sequência está pendente (Q-15). Nenhum sorteio, compra, embaralhamento ou início do duelo realizado.


**Atualização v1.7:** ler prioritariamente `01_Regras/POC_v1.7_Reposicao_Pos_Combate.md` e `00_Governanca/DECISAO_REPOSICAO_POS_COMBATE_20261017.md`. Decisão mais recente: reposição automática da mão só após o combate encerrar com derrota por 0 PV; nenhuma reposição pós-invocação/evolução/suporte. **Q-15 resolvida**; Q-16 (micro-ordem com fase extra do sobrevivente) aberta. Preservar mão inicial e compras da fase de troca. Versões anteriores são históricas quanto à reposição.

## Regra principal vigente v1.9

A referência mais recente para saques é `01_Regras/POC_v1.9_Saque_Abertura_Ciclo.md`, com decisão em `00_Governanca/DECISAO_SAQUE_ABERTURA_CICLO_20261017.md`. **Q-17 fechada**. Saque simétrico até 5 na abertura de novo ciclo após combate terminado por KO; não no KO, nem na rodada interna, nem após terceiro ponto. v1.7 e v1.8 são históricas quanto ao gatilho; não existe fase extra para sobrevivente. Partida permanece não iniciada.

## Auditoria SRD — lote 01 (17/10/2026)

- `03_Dados/AUDITORIA_MECANICA_SRD_LOTE01_20261017.md`: auditoria de 12 espécies/13 cópias com ficha SRD integral, sem homologação automática de suporte.
- `03_Dados/MATRIZ_VALIDACAO_SRD_13_COPIAS.json`: matriz de habilidades verificadas, fórmulas e bloqueios individualizados.
- `05_Testes/TESTES_MECANICOS_SUPORTES_LOTE01.json`: 10 cenários novos, todos `NAO_EXECUTADO`, complementares ao plano geral.
- **Bloqueio prioritário:** como resolver KO por suporte pré-iniciativa (especialmente quando o primeiro suporte mata antes de o segundo ser aplicado).
- **Sem executar sorteios, embaralhamento, compras ou combate.**

## Continuação da homologação — lote 03 (17/10/2026)

Três cartas Aberração adicionais tiveram fontes externas confrontadas: `AB-POC-001` (Ahu-Nixta Drudge, Tome of Beasts 2/5E), `AB-POC-004` (Light Eater, Tome of Beasts 3/5E) e `AB-POC-013` (Maw Swarm, Dungeon Delver’s Guide/A5E). `03_Dados/VALIDACAO_FONTES_EXTERNAS_LOTE03_20261017.md`. **Não** somar essas criaturas às 3 fichas integrais SRD 5.2.1 da Aberração. Contagem de suportes homologados continua 0, partidas/sorteios/compras continuam 0.

## Módulo de testes de comandos (motor experimental v2.2)

Existe `07_Motor_Experimental/` com `v22/motor_poc.py`, `test_motor_poc.py`, README e resultados, além de `source/` com entradas congeladas. Demonstrou 55 testes do novo motor aprovados e a regressão antiga repetida (80/84, 4 não executados). **Nunca confundir snapshots e resultados injetados de fixture com a partida oficial.** O estado oficial permanece não iniciado, sem embaralhamento. Consulte `07_Motor_Experimental/v22/RELATORIO_IMPLEMENTACAO_V2_2.md`.


## Atualização técnica: motor experimental v2.3

Consultar `07_Motor_Experimental/v23/README_V2_3.md` e `RELATORIO_COMBATE_V2_3.md`. O novo módulo exerce d20, iniciativa, acertos/críticos, dano, PV, KO e turnos com Talons (Giant Owl) e Bite (Gibbering Mouther), em **escopo de ataque isolado**; habilidades passivas e alternativas continuam pendentes. **30 novos testes aprovados**, além de 55 do motor v2.2 e da mesma regressão estrutural 80/84. A demonstração é inteiramente simulada; não houve embaralhamento, dados reais ou mutação do estado oficial.


## Motor experimental v2.4 — condições e gatilhos (17/10/2026)

Criada a pasta `07_Motor_Experimental/v24/` com módulo parcial `motor_condicoes_srd.py`, 48 testes específicos, documentação, resultados e demonstração pública em `Execucoes_Isoladas/20261017/v24/`. Entra em jogo somente a dupla de referência Giant Owl × Gibbering Mouther, exclusivamente em fixtures. Não iniciar a partida oficial nem tratar o módulo como SRD completo. A implementação v2.4 controla início de turno, salvaguardas para Gibbering/Blinding Spittle, resistência radiante, Blinded, duração, recarga e vantagem/desvantagem; demais mecânicas continuam pendentes. D8 7–8 do Gibbering gera PENDENTE sem alterar estado. Para predicados espaciais de efeitos, exige confirmação sintética explícita, não inferência de alcance.

## Motor experimental v2.5 — ações bônus e magias (17/10/2026)

**Código:** `07_Motor_Experimental/v25/motor_magias_srd.py`. **Testes:** `07_Motor_Experimental/v25/test_magias_srd.py`. **Relatório:** `07_Motor_Experimental/v25/RELATORIO_IMPLEMENTACAO_V2_5.md`. Fixture Deva (CE-026) com Divine Aid/Cure Wounds e Multiattack, com 55 testes novos passando; 188 testes de regressão dos módulos v2.2–v2.5 passaram. Reações não são simuladas sem habilidade na ficha, nem se libera suporte. Trilha e mesa públicas em `07_Motor_Experimental/Execucoes_Isoladas/20261017/v25/`. A partida oficial segue NÃO INICIADA.

## Integração de compatibilidade — registro paralelo (18/10/2026)

O experimento de orquestração de **quatro perfis legados (v2.2–v2.6)** foi arquivado em `07_Motor_Experimental/Compatibilidade_Motores_Legados_20261018/`. Possui **304 testes locais aprovados** (270 testes históricos desses módulos + 34 testes da API de compatibilidade), quatro demonstrações de dados simulados, checkpoints de fixture verificados e nenhuma publicação de dados privados. **Não** substitui a versão canônica `v27/`, que trata de concentração SRD, nem as versões técnicas posteriores `v28+` e `v6.x` já existentes na Biblioteca. O arquivo do orquestrador conserva o nome histórico `orquestrador_srd_v27.py` apenas dentro desse ramo de compatibilidade.

A variante v2.6 de ações lendárias que estava pendente de gravação foi recuperada em `07_Motor_Experimental/v26/Lendarias_Separadas/`. A v2.6 de reações permanece no seu local original. Os testes de movimentação são um **estudo SRD que não constitui regra da POC sem posicionamento**. Nenhuma nova regra competitiva, carta ou efeito de suporte foi homologado. Nenhuma partida oficial iniciada, sem embaralhamento, compras, rolagens ou mudança do placar 0 × 0.
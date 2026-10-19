> **POC-21 — DIRETRIZ VIGENTE (17/10/2026): fichas sob demanda.** Confirmada a existência de **80/80 arquivos individuais** de ficha nos decks Celestial/Aberração (40/40 cada, posições 01–40). Não usar ausência de *homologação integral* como bloqueio global da POC; prosseguir com interface, fluxo, estados e testes não mecânicos. Consultar fichas existentes apenas quando necessário. Se faltar realmente ficha ou dado essencial para resolver uma jogada, suspender **somente essa operação**, sem inventar valores. A seleção **Sem suporte** permanece válida. Nenhum embaralhamento foi autorizado. Veja `01_Regras/POC_v2.1_Fichas_Sob_Demanda.md`.

---

> **REGRA VIGENTE POC-20 (17/10/2026): KO por suporte pré-iniciativa encerra imediatamente o combate e dá 1 ponto ao controlador do suporte; o segundo suporte reservado permanece na mão sem consumo (reserva liberada), não há iniciativa e o próximo saque de ambos só ocorre na abertura do próximo ciclo, se não houve o terceiro ponto.** Consulte `01_Regras/POC_v2.0_KO_Pre_Iniciativa.md`. Esta decisão fecha o item de **KO** de Q-13, mas NÃO homologa poderes nem resolve morte simultânea; quaisquer anotações históricas de “KO pré-batalha pendente” estão superadas.


---

# POC SRD Card Game — Status atual antes do embaralhamento

> **REGRA VIGENTE — POC v1.9 (17/10/2026), decisão do administrador.** **Rodada de saque** significa somente a **abertura de um novo ciclo de preparação após o combate anterior acabar com uma criatura a 0 PV**, desde que ninguém tenha alcançado 3 pontos. Nesse instante, **AMBOS os jogadores repõem suas mãos até 5 cartas** a partir do topo de seus montes, conforme disponibilidade. Não há saque no encerramento do KO, ao passar rodadas/turnos do mesmo combate, após invocação, evolução ou suporte, nem saque extra da criatura sobrevivente. Compras iniciais e compras equivalentes aos descartes na fase de troca continuam distintas. **Q-17 resolvida.** Esta regra posterior prevalece sobre as versões v1.7 e v1.8 nos pontos conflitantes.


**Consolidação após autorização do administrador:** decks virtuais de teste aprovados, sem atribuir posse na coleção oficial. Esta atualização complementa, e quando necessário prevalece operacionalmente sobre, a lista de pendências inicial em `00_Governanca/DECISOES_E_PENDENCIAS.md`.

## Resolvido

- **Q-01 — ordem fixa de preparação:** APROVADA na POC v1.5: único sorteio inicial define PRIMEIRO/SEGUNDO por TODO o duelo, inclusive ciclos após derrota; iniciativa SRD separada em CADA novo combate. **Nenhum sorteio realizado.**
- **Q-03 — suporte opcional:** resolvido por aprovação expressa do administrador: **zero ou uma** carta; `Sem suporte` permitido para J1 e J2, sem movimentação/compra/reserva.
- **Q-11 — identidade de cópias da IA para esta POC:** resolvido pela aprovação expressa de decks **virtuais** e pelos novos IDs `AB-POC-001` a `AB-POC-040`, com vínculo 1:1 a `AB-REF-001` a `AB-REF-040`.
- Atribuídos apenas IDs documentais, sem cartas possuídas ou coleções oficiais criadas; `CE-001` a `CE-040` permanecem como identificadores do deck humano de teste.
- Em 80 entradas, conferidos unicidade de ID, nome, ND, raridade e posição nos controles originais. Os índices não são ordem de monte.

## Revisão de fichas

- J1 Celestial: 40 cópias; 10 possuem fichas SRD integrais nas fontes disponíveis, correspondentes a 9 espécies; 30 ainda precisam de comprovação de ficha integral da edição adequada.
- J2 Aberração: 40 cópias; 3 possuem fichas SRD integrais; 37 ainda precisam de comprovação. Os cinco registros sem CA/PV no controle original são `AB-POC-002` (Cranium Rat), `AB-POC-003` (Gazer), `AB-POC-020` (Mindwitness), `AB-POC-039` (Kalaraq Quori) e `AB-POC-040` (Greater Star Spawn Emissary).
- **Suportes homologados individualmente para ativação:** 0 de 80. A presença da habilidade na ficha oficial é etapa de conferência, não aprovação.
- Duas revisões prioritárias de escolha de habilidade por categoria: Unicorn (`Shimmering Shield` vs `Unicorn’s Blessing/Cure Wounds`) e Planetar (`Invisibility` vs `Cure Wounds`). Não substituir candidato sem homologação.

## Ainda bloqueante

- **Q-02 RESOLVIDA — POC-16:** quantas evoluções legais forem possíveis, sem limite numérico. **Q-15 RESOLVIDA — POC-17:** reposição da mão SOMENTE depois do combate terminar, sem compras entre evoluções nem após suporte. **Q-01 foi resolvida integralmente quanto à ordem PRIMEIRO/SEGUNDO por todos os ciclos**; a ordem operacional da fase extra da sobrevivente continua pendente.
- **Q-04:** possibilidade de alterar reserva confirmada antes da resolução pré-batalha ainda não definida. **Q-03 foi resolvida** com seleção opcional.
- **Q-05/Q-10:** homologação das habilidades candidatas; foco especial em passivos, agarrões, controle, concentração e duração após descarte.
- **Q-09:** fichas integrais do conjunto completo ainda não disponíveis/validadas para 80 cartas.
- **Q-06/Q-07/Q-08:** exceções de monte vazio, morte simultânea/combate travado, substituição voluntária.
- **Q-12:** persistência da partida entre sessões ainda não demonstrada; checkpoints necessários.
- **Q-13:** suporte pré-batalha que exige turno/iniciativa ou causa KO antes do combate não tem tratamento homologado.
- **Q-14 parcialmente resolvida:** administrador confirmou combate até 0 PV, novo ciclo somente após derrota, placar +1 e preservação do estado. **Frequência de sorteio resolvida (POC-15): apenas uma vez por duelo**; permanece pendente a ordem operacional da fase extra de saque/troca da sobrevivente.

## Arquivos desta etapa

- `00_Governanca/DECISAO_DECKS_VIRTUAIS_POC.md`
- `03_Dados/MAPEAMENTO_COPIAS_AB_POC.json` e `MAPEAMENTO_COPIAS_AB_POC.csv` (UTF-8, `;`)
- `03_Dados/STATUS_FICHAS_SUPORTES_80.json`
- `03_Dados/AUDITORIA_FICHAS_SUPORTES_POC_20261016.md`
- `05_Testes/CHECKLIST_ANTES_EMBARALHAR.json`

**Sem execução de jogo:** nenhuma partida oficial criada; 0 embaralhamentos, 0 compras, 0 invocações, 0 rolagens, 0 ações executadas. A POC continua em preparação.

**Fluxo vigente:** `01_Regras/POC_v1.4_Ciclos_e_Combate.md` junto com `01_Regras/POC_v1.3_Fases_e_Suportes.md`. A janela de ativação em turno própria da v1.2 foi substituída. A etapa de combate segue bloqueada.

## Atualização POC v1.5 — prioridade fixa

PRIMEIRO/SEGUNDO permanecerão os mesmos de acordo com um único sorteio no início do duelo, mesmo após derrotas. Cada novo combate rolará iniciativa SRD própria; as rodadas do mesmo combate continuam com aquela iniciativa. A ordem sorteada NÃO foi gerada; J1 e J2 não têm ainda posição PRIMEIRO/SEGUNDO atribuída. Ver `01_Regras/POC_v1.5_Ordem_Fixa_Preparacao.md`.

## Atualização POC v1.6 — evoluções sem teto

O administrador aprovou “quantas puder” evoluções na etapa de criatura. Cada passo requer carta na mão, mesmo tipo e classe imediatamente superior, com carta anterior ao cemitério e nova com PV máximos. **Q-02 e Q-15 encerradas:** evoluções ilimitadas apenas com cartas da mão; repor até cinco somente após o combate terminar (POC-17). Não iniciar qualquer partida nem embaralhamento; homologação de fichas e suportes continua parcial. Ver `01_Regras/POC_v1.6_Evolucoes_Ilimitadas.md`.


## Atualização POC v1.7 — reposição somente após o combate

Não há reposição automática após invocação, cada evolução, fim da sequência ou resolução do suporte; tampouco em rodadas internas do mesmo combate. Somente após KO validado e fim do combate pode ocorrer reposição até cinco do monte de cada lado, sem sexta carta; mãos iniciais e trocas com descarte equivalente continuam válidas. **Q-15 fechada; Q-16 em aberto** (micro-ordem com a fase extra de saque/descarte/troca do sobrevivente). Nenhuma partida, embaralhamento ou compra executados.

## Situação vigente v1.9

**Q-17 RESOLVIDA:** saque até 5 para os dois **somente no início do novo ciclo**, após um combate com KO e antes da troca; nenhuma compra no evento KO ou nas rodadas de turno. Nenhum saque adicional para a sobrevivente. O primeiro ciclo usa o saque inicial de cinco do setup, sem duplicação. Se terceiro ponto encerrar o duelo, não haverá outro saque. As anotações históricas v1.7 acima são superadas neste ponto. Persistem homologações mecânicas e exceções restantes; partida ainda não iniciada.

## Auditoria mecânica SRD — lote 01 (17/10/2026)

Revisadas 12 espécies/13 cópias com texto completo do `SRD_CC_v5.2.1.pdf`: 10 Celestial (nove espécies) e 3 Aberração (três espécies). Todas as habilidades descritas na matriz foram cotejadas com o SRD, mas **0 suportes homologados** para a resolução pré-batalha. Adicionados 10 testes separados, `NAO_EXECUTADO`. Arquivos: `03_Dados/AUDITORIA_MECANICA_SRD_LOTE01_20261017.md`, `03_Dados/MATRIZ_VALIDACAO_SRD_13_COPIAS.json` e `05_Testes/TESTES_MECANICOS_SUPORTES_LOTE01.json`.

Próximo bloqueio prioritário: definição de KO ocorrido durante suporte 1/2 antes da iniciativa. A regra de v1.9 sobre saque no início de novo ciclo e a proibição de reembaralhar continuam vigentes. Não alterar o estado da partida antes das homologações.

## Continuação da homologação — lote 03 (17/10/2026)

Três cartas Aberração adicionais tiveram fontes externas confrontadas: `AB-POC-001` (Ahu-Nixta Drudge, Tome of Beasts 2/5E), `AB-POC-004` (Light Eater, Tome of Beasts 3/5E) e `AB-POC-013` (Maw Swarm, Dungeon Delver’s Guide/A5E). `03_Dados/VALIDACAO_FONTES_EXTERNAS_LOTE03_20261017.md`. **Não** somar essas criaturas às 3 fichas integrais SRD 5.2.1 da Aberração. Contagem de suportes homologados continua 0, partidas/sorteios/compras continuam 0.

## Incremento técnico v2.2 — motor experimental isolado (17/10/2026)

- **Sem alterar a partida oficial:** ainda não iniciada; nenhum embaralhamento, sorteio, compra ou combate oficial.
- Motor de comandos experimental em `07_Motor_Experimental/v22/motor_poc.py`, com validação de fases, 40 cartas por lado, reservas, evoluções, KO, pontuação, saque por abertura de ciclo, rejeição sem mutação, idempotência, trilha de eventos encadeada por hash e checkpoint restaurável.
- **55 testes automatizados do motor novo passaram**, 0 falhas. **Regressão histórica separada**: 80/84 passaram no simulador anterior; CT-11, CT-20, CT-75 e CT-83 não executados.
- Trilha isolada do motor novo: 24 eventos aceitos; 2 combates de resultado **injetado como fixture**; 3 ciclos abertos; placar fictício 1 × 1; cada projeção passou na validação estrutural do schema; estado de teste arquivado separadamente.
- Resultados, código e entradas congeladas em `07_Motor_Experimental/`, sem ZIP. Checkpoint integral/ordem dos montes e eventos administrativos não são visão pública; estão em `Execucoes_Isoladas/20261017/Interno_Arbitro/` para uso de arbitragem/teste e não devem ser exibidos ao adversário.
- **Ainda não há motor SRD de combate COMPLETO nem escolha estratégica IA plenamente integrada.** A iniciativa e os resultados de KO da demonstração foram fornecidos como fixtures expressos, sem ficha mecânica executada. A POC permanece v2.1 quanto às regras vigentes; v2.2 nomeia somente o protótipo técnico.


## Incremento técnico v2.3 — ataque SRD parcial, isolado (17/10/2026)

- Código: `07_Motor_Experimental/v23/motor_combate_srd.py`, com base congelada do v2.2. Implementa dois comandos de **fixture**: iniciativa por d20 simulado e ataque isolado (Talons da Giant Owl/CE-001 e Bite do Gibbering Mouther/AB-POC-008). Consultou SRD 5.2.1 pp. 7, 13, 16, 288 e 352.
- Os efeitos contínuos/passivos e ações alternativas **NÃO** estão calculados (notadamente Gibbering, Aberrant Ground, Flyby, Spellcasting); é obrigatório confirmar o escopo limitado em cada ataque.
- Resultado: **30/30 testes novos** e **55/55 do v2.2** passaram. Regressão estrutural separada: **80/84** (4 não executados). A demonstração com 19 eventos/7 ataques, resultado fictício J1 1×0 e PV 4 da sobrevivente, **não** é combate SRD integral e não modifica o placar oficial.
- Arquivos públicos de demonstração não incluem as mãos nem a ordem dos montes; não foram publicados checkpoints privados integrais da v2.3.
- **Regras oficiais da POC continuam v2.1; motor técnico experimental v2.3.** Partida não iniciada, nenhum sorteio/embaralhamento oficial.


## Execução isolada do motor v2.4 — 17/10/2026

O motor experimental v2.4 foi salvo em `07_Motor_Experimental/v24` e os resultados públicos em `07_Motor_Experimental/Execucoes_Isoladas/20261017/v24`. **48/48** novos testes passaram; **30/30** testes v2.3 e **55/55** testes v2.2 passaram nas implementações respectivas. Regressão histórica: **80/84** passaram, quatro **não executados** (CT-11, CT-20, CT-75, CT-83). A demonstração produziu **23 eventos aceitos** com dados simulados e área/alcance declarados como fatos de teste; J1 **0 × 0** J2, Giant Owl **10/19 PV**, Gibbering Mouther **44/52 PV**, combate fictício ainda na rodada 4. **SRD integral não certificado; nenhuma partida oficial iniciada, nenhum sorteio/embaralhamento oficial.** Regra de fichas sob demanda permanece; habilidades fora do escopo, especialmente Gibbering d8 7–8, não são automaticamente homologadas.

## Atualização motor experimental v2.5 (17/10/2026)

A versão de desenvolvimento `07_Motor_Experimental/v25/` integra, **apenas em cenário isolado Deva × Gibbering Mouther**, Multiattack do Deva, a magia *Cure Wounds* via **Divine Aid** como ação bônus (2 usos/dia), recursos persistentes e economia independente de ação/ação bônus. Utilizou fichas existentes SRD 5.2.1 (pp. 121, 279, 288) sob demanda. **55 testes novos aprovados**; regressão de 188 testes de módulos do motor sem falhas; suíte estrutural 80/84, quatro não executados. Trilha pública isolada: 22 eventos, placar fictício 0 × 0, Deva 227/229 PV e Gibbering Mouther 39/52 PV na rodada 2. Reações e outras habilidades permanecem pendentes; isto **não homologa suporte algum**. Arquivos públicos em `07_Motor_Experimental/Execucoes_Isoladas/20261017/v25/`. Estado oficial não iniciado, zero compras, embaralhamentos e rolagens oficiais.

## Integração de compatibilidade — registro paralelo (18/10/2026)

O experimento de orquestração de **quatro perfis legados (v2.2–v2.6)** foi arquivado em `07_Motor_Experimental/Compatibilidade_Motores_Legados_20261018/`. Possui **304 testes locais aprovados** (270 testes históricos desses módulos + 34 testes da API de compatibilidade), quatro demonstrações de dados simulados, checkpoints de fixture verificados e nenhuma publicação de dados privados. **Não** substitui a versão canônica `v27/`, que trata de concentração SRD, nem as versões técnicas posteriores `v28+` e `v6.x` já existentes na Biblioteca. O arquivo do orquestrador conserva o nome histórico `orquestrador_srd_v27.py` apenas dentro desse ramo de compatibilidade.

A variante v2.6 de ações lendárias que estava pendente de gravação foi recuperada em `07_Motor_Experimental/v26/Lendarias_Separadas/`. A v2.6 de reações permanece no seu local original. Os testes de movimentação são um **estudo SRD que não constitui regra da POC sem posicionamento**. Nenhuma nova regra competitiva, carta ou efeito de suporte foi homologado. Nenhuma partida oficial iniciada, sem embaralhamento, compras, rolagens ou mudança do placar 0 × 0.
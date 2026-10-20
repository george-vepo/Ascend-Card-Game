# Ascend Card Game — checkpoint verificável de desenvolvimento

**Atualizado:** 2026-10-19. **Base de código:** `main` após o PR #38; commit `e2e1c5e12bf573e181cc2f903ce10c54d7f11301`.

## Fonte da verdade e arquitetura

- Código do jogo, motor experimental, regras, testes e estado: **george-vepo/Ascend-Card-Game**.
- Cartas, fichas completas, identidades e imagens: **george-vepo/Catalogo-SRD**. Nenhuma ficha, dataset, carta ou imagem deve ser replicada neste repositório.
- Manifesto de leitura externa em `config/catalogo_srd.json`, fixando a revisão do catálogo `03f84e8426f469ef6a0e471faea2093b7c0b69c9`. Identidade, revisão e hash do documento devem ser verificados.
- Fonte mecânica: SRD 5.2.1; ficha Roper p. 320, Roper `AT-002` / cópia de teste `AB-POC-017`, Giant Owl `CE-001`.
- Regras do card game: `docs/poc/01_Regras/CONTRATO_DE_REGRAS.md` e decisões administrativas vigentes em `docs/poc/00_Governanca/`. **Não converter propostas em regras.**

## Commits e evidências confirmados

| Entrega | Resultado | Commit integrado na main | Evidência CI |
| --- | --- | --- | --- |
| [PR #12](https://github.com/george-vepo/Ascend-Card-Game/pull/12) | Bite do Roper isolado | `62b4f3d7862d092060905df748cf3a1d661799b6` | Histórico do PR |
| [PR #13](https://github.com/george-vepo/Ascend-Card-Game/pull/13) | Tentacle, Grappled, Poisoned | `02ccb983734ceb9efe8c2ed5c3b81272e3080b84` | Histórico do PR |
| [PR #14](https://github.com/george-vepo/Ascend-Card-Game/pull/14) | Fuga, dano/destruição de tentáculos | `d0824a692292d41072206c46e7150a5efd953fa0` | Histórico do PR |
| [PR #15](https://github.com/george-vepo/Ascend-Card-Game/pull/15) | Desvantagem Poisoned na fuga | `9f8d2de819581ef61002f4e88ceeb5d4ada87df0` | Histórico do PR |
| [PR #16](https://github.com/george-vepo/Ascend-Card-Game/pull/16) | Reel: pré-validação pura; movimento bloqueado | `186c5d0da6af04d4e893f5b811e9ba803063ca78` | Histórico do PR |
| [PR #17](https://github.com/george-vepo/Ascend-Card-Game/pull/17) | KO libera Grappled/Poisoned/tentáculos e valida checkpoints | `a1c8cad2ff77fa7038e3ffc7a5d6a8e8c07b646c` | [126 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39324566200) e [81 testes de regressão](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39324566217) |
| [PR #18](https://github.com/george-vepo/Ascend-Card-Game/pull/18) | Multiattack: sequência verificada, execução bloqueada | `71971a0873523374f4c0a52e6652f017789bcdc0` | [138 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39325453504) e [81 testes de regressão](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39325453465) |
| [PR #21](https://github.com/george-vepo/Ascend-Card-Game/pull/21) | Sem arena nem alcance; Reel individual sem deslocamento; Multiattack ainda bloqueado por composição | `7b0cda4950abdbdc1fd202d0f129345d2566e989` | [138 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39327919830) e [81 testes de regressão](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39327919896); cinco workflows verdes |
| [PR #23](https://github.com/george-vepo/Ascend-Card-Game/pull/23) | Multiattack atômico do Roper (2 Tentacle, Reel, 2 Bite) em casos com até um vínculo Grappled; duplo vínculo retorna PENDENTE sem mutação | `92cefa9357d3f48a8fb652bb2b1e1239842f248c` | [154 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39352157314) na suíte Roper e [81 testes de regressão](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39352157313); cinco workflows verdes |
| [PR #26](https://github.com/george-vepo/Ascend-Card-Game/pull/26) | **Homebrew aprovado:** múltiplos tentáculos por alvo, fuga única libera todos, destruição isolada conserva demais, Reel alvo único, KO limpa tudo e Multiattack completo na Action | `74422eb458457380477deb1e3036598b06934e26` | [170 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39353711185) e [81 de regressão](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39353711192), cinco workflows verdes |
| [PR #28](https://github.com/george-vepo/Ascend-Card-Game/pull/28) | Inventário SRD de Spider Climb/Flyby como traits exclusivamente espaciais (sem efeito na POC); Spellcasting da Owl (At Will Detect Evil and Good / Detect Magic; Clairvoyance 1/Day) auditada sem conjuração; limitações obsoletas do perfil corrigidas | `213684db8a9faaa5c9514f2b8837aae377804693` | [186 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39354689642) e [81 regressões](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39354689537), cinco workflows verdes |
| [PR #31](https://github.com/george-vepo/Ascend-Card-Game/pull/31) | **Decisão delegada #30:** Detect Evil and Good e Detect Magic como Actions de detecção só do campo público, concentração 100 rodadas e salvaguarda Constituição sob dano; Clairvoyance sem locais/10 minutos é inaplicável e não consome 1/Day | `2a547c07ce5045831a5cb2ec9bdfed73f64ecb2c` | [210 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39356307864) e [81 regressões](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39356307710), cinco workflows verdes |
| [PR #33](https://github.com/george-vepo/Ascend-Card-Game/pull/33) | Próxima criatura: **Gibbering Mouther** com ficha SRD p. 288 estritamente verificada, inventário de Gibbering/Wis DC10+d8, Blinding Spittle Dex DC10/Recharge 5–6/Blinded, Bite e Aberrant Ground; preflight público puro sem executar efeitos não regulamentados | `885b1aa1029dacdca2ba06f9fc895d7cdbdb4b0f` | [16 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39357381590) no workflow Mouther; estrutura, ponte e referências do Catálogo SRD também aprovadas |
| [PR #36](https://github.com/george-vepo/Ascend-Card-Game/pull/36) | **Mudança arquitetural aprovada, issue #35:** ponte de propostas da IA com declaração autenticada, ficha/versão/hash conferidos, pacote de rolagens da fixture e execução limitada em passos/lotes com status público e replay idempotente de KO. Não há modelo real conectado nem worker independente ativo. | `6aad0de3a244cb1ed8a10d6482932205e45fc452` | [235 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39367692596), quatro workflows verdes (inclui 25 testes novos de bridge) |
| [PR #38](https://github.com/george-vepo/Ascend-Card-Game/pull/38) | Fila SQLite **durável** para jobs de simulação em background: lease, fencing, heartbeat, cancelamento, retomada sob entrada externa validada, tick de worker injetado, somente metadados públicos, nenhuma ficha/deck/checkpoint privado persistido na fila. Modelo e daemon não conectados. | `e2e1c5e12bf573e181cc2f903ce10c54d7f11301` | [24 testes aprovados](https://github.com/george-vepo/Ascend-Card-Game/actions/runs/39368323012), três workflows verdes: fila background, estrutura, referências externas. |

**Contagens dos workflows:** os 81 testes da suíte de fuga/destruição são repetidos parcialmente no workflow principal. Não somar esses totais como testes independentes. Três workflows do PR #38 foram aprovados (fila background, estrutura, referências do catálogo). Quatro workflows do PR #36 também foram aprovados (Roper/árbitro IA, estrutura, ponte de identidades e referências do Catálogo). Também constam neste histórico quatro workflows do PR #33. Os cinco workflows do PR #31 também estão documentados no histórico: Roper, fuga/destruição, estrutura, ponte e referências do Catálogo SRD.

## Arquivos e módulos atuais relevantes

- `experimental/integration/motor_roper_basico.py`: ações isoladas da fixture e pré-validações; contém `prevalidar_reel`, `prevalidar_multiattack`, liberação de Grappled em KO e validação pós-combate.
- `src/ascend/tentaculo_roper_srd.py`: extrai apenas mecânicas de Tentacle, Reel e composição de Multiattack diretamente do texto da ficha pinada.
- `src/ascend/perfil_combate_srd.py`, `src/ascend/fuga_roper_srd.py`, `src/ascend/testes_d20_srd.py`: perfis, fuga, dados explícitos/desvantagem.
- `tests/integration/test_roper_ko_grapple_cleanup_real.py`: nove casos novos do PR #17.
- `tests/integration/test_roper_multiattack_preflight_real.py`: doze casos do PR #18, ajustados para indicar execução parcial.
- `tests/integration/test_roper_multiattack_atomic_safe_real.py`: dezesseis cenários do PR #23, atualizados para Grappled múltiplo.
- `tests/integration/test_roper_grapple_multiplo_real.py`: dezesseis cenários novos do PR #26.
- `src/ascend/habilidades_poc_srd.py`: extrator estrito de Traits espaciais e lista de magias da Owl, apenas consulta.
- `tests/integration/test_habilidades_poc_srd_real.py`: dezesseis cenários de auditoria pura e sem efeitos, adicionados no PR #28.
- `docs/POC_AUDITORIA_TRAITS_MAGIAS_ROPER_OWL.md`: histórico da pré-auditoria do PR #28, **superado em parte** pelo PR #31.
- `src/ascend/magias_owl_poc.py`: classificação de tipos públicos, efeitos mágicos públicos e salvaguarda de Constituição extraída da ficha SRD.
- `tests/integration/test_owl_spellcasting_publico_real.py`: 24 testes novos de detecção, concentração, rollback, privacidade e checkpoint.
- `docs/poc/00_Governanca/DECISAO_20261019_MAGIAS_GIANT_OWL_SEM_POSICAO.md`: decisão **homebrew** delegada #30 e regras da POC de detecção.
- `src/ascend/gibbering_mouther_srd.py`: extrator estrito dos efeitos e recursos SRD da ficha Gibbering Mouther `AT-001 / AB-POC-008`.
- `experimental/integration/preflight_gibbering_mouther.py`: verifica identidade, hash, CA/PV de criatura já em campo sem alterar zona/turno/eventos.
- `tests/integration/test_gibbering_mouther_preflight_real.py`: 16 testes novos de fonte, privacidade e checkpoint, integrados pelo PR #33.
- `docs/POC_GIBBERING_MOUTHER_PREVALIDACAO.md`: lacunas e estado consultivo da próxima criatura.
- `experimental/integration/arbitro_ia_background.py`: MVP de protocolo seguro de proposta IA e simulação por passos, sem modelo ou scheduler durável.
- `tests/integration/test_arbitro_ia_background_real.py`: 25 cenários de autoria, fonte, sorteio simulado externo, rejeição de mutações, KO e replay.
- `docs/POC_ARBITRO_IA_SIMULACAO_BACKGROUND.md`: contrato, fila e limitações do worker de background; [issue #35](https://github.com/george-vepo/Ascend-Card-Game/issues/35) continua aberta para implementação integral.
- `src/ascend/fila_simulacao_background.py`: fila SQLite de jobs, reserva de lease com fencing, heartbeat, cancelamento, status público e tick externo de worker.
- `tests/integration/test_fila_simulacao_background.py`: 24 testes de lease, concorrência, segurança de resumo, durabilidade de status e execução por tick.
- `.github/workflows/validate-fila-simulacao-background.yml`: CI da fila SQLite.
- `docs/poc/00_Governanca/DECISAO_20261019_GRAPPLE_MULTIPLO_ROPER.md`: homebrew aprovado, distinto do SRD.
- `docs/ROPER_MULTIATTACK_ATOMICO_PARCIAL.md`: limite de escopo, dados simulados, Action única e rollback.
- `.github/workflows/validate-roper-basico.yml`: regressão de todos os componentes do Roper.
- `docs/ROPER_KO_GRAPPLE_CLEANUP.md` e `docs/ROPER_MULTIATTACK_PREVALIDACAO.md`: escopo e limites por incremento.

## Estado mecânico e bloqueios

**No recorte experimental:** Bite e Tentacle individuais (sem exigência de alcance), Grappled/Poisoned, fuga com desvantagem Poisoned, ataque e destruição/regeneração de tentáculos, limpeza de vínculos em KO, preflight puro de Reel/Multiattack, Action Reel individual executável **sem deslocamento** quando há Grappled válido e Multiattack do Roper (2 Tentacle → Reel → 2 Bite) executável **em uma Action**, agora incluindo vários vínculos Grappled independentes por alvo. Condições não acumulam; fuga bem-sucedida (uma Action com desvantagem Poisoned) libera todos; destruição de apenas um tentáculo preserva os demais; KO encerra todos. Os testes exercitam rollback, idempotência, checkpoint e privacidade. Todos exigem fontes verificadas e não são combate SRD integral.

**DECISÃO JÁ VIGENTE DESDE 15/10/2026, RATIFICADA EM 19/10/2026:** nenhum combate usa posição, arena, distância ou checagem de alcance espacial. Ver contrato `docs/poc/01_Regras/CONTRATO_DE_REGRAS.md` e [Issue #19 encerrada](https://github.com/george-vepo/Ascend-Card-Game/issues/19). A ausência de arena jamais bloqueia uma ação. O [PR #21](https://github.com/george-vepo/Ascend-Card-Game/pull/21) removeu as verificações espaciais e habilitou Reel individual como Action sem deslocamento, com cinco workflows verdes e merge confirmado na `main`.

**RESOLVIDO:** [Issue #24](https://github.com/george-vepo/Ascend-Card-Game/issues/24) encerrada após aprovação expressa, testes e merge do PR #26. A regra de uma única fuga liberando todos os tentáculos do Roper é **homebrew do Card Game**, não texto literal do SRD. **CLASSIFICADOS SEM EFEITO ESPACIAL:** Spider Climb do Roper e Flyby da Owl são Traits auditadas, mas movimento e alcance não existem no Card Game. **ISSUE #30 RESOLVIDA:** [decision](https://github.com/george-vepo/Ascend-Card-Game/issues/30) e PR #31 integrados. Detect Evil and Good/Detect Magic executáveis como **Actions** da Owl, com leitura estrita de informações públicas do campo, concentração de no máximo 100 rodadas, salvaguarda de Constituição verificada, substituição/encerramento e rollback transacional no dano; **Clairvoyance inaplicável** com 1/Day preservado (não consumido). A substituição do domínio físico pelo campo público é **homebrew aprovada**, não texto do SRD. **AINDA FORA DO RECORTE:** inspeção de escola/aura com segunda Magic Action em efeitos concretos, magias de outras criaturas e demais componentes SRD. Deslocamento posicional/vôo/arena **não será implementado**; verificar separadamente se uma habilidade tem efeitos não espaciais traduzíveis sem inventar regras.

**NOVA DIRETRIZ DA ARQUITETURA (20/10/2026):** a IA deve **simular os combates em segundo plano**, interpretando fichas e ações, não apenas validando golpes isolados. Foi aprovada a separação IA planejadora/árbitra → rolagens externas → motor de estado determinístico, sem perder privacidade nem a prioridade das regras; [issue #35](https://github.com/george-vepo/Ascend-Card-Game/issues/35) está **aberta**. Não retomar implementação manual criatura a criatura como estratégia principal. A infraestrutura de PR #36 cobre **somente um contrato seguro e execução por passos** de fixture com propostas externas; não há IA real/worker persistente executando fora da sessão neste estágio.

**Próximo incremento seguro:** a fila SQLite/lease/fencing de **metadados públicos já existe** (PR #38). Agora implementar **armazenamento privado confiável dos checkpoints**, retomada consistente após reinício, processo independente de worker que execute `JobSimulacao` a partir dessa referência, gateway de modelo de IA conectado e serviço externo de rolagens verificáveis. Somente então o modo background estará realmente operacional. O motor continua experimental, **não equivale a combate SRD integral**.

**Partida oficial:** não iniciada. **Placar oficial:** J1 0 × 0 J2. **Rolagens em CI:** simuladas, externas e explícitas. Não publicar mãos, decks privados, ordem de montes nem snapshots de estado competitivo real.

## Procedimento de retomada

1. Confirmar o commit **real e atual** da `main`, PRs e branches antes de qualquer alteração (este arquivo é um checkpoint histórico, não substitui consulta ao GitHub).
2. Comparar com os PRs e issues posteriores a #18/#19; aproveitar branches válidas ainda não integradas.
3. Verificar novamente `config/catalogo_srd.json`, a ficha integral externa e o manual SRD 5.2.1 antes de alterar combate.
4. Criar branch a partir da `main` mais recente, implementar apenas incremento seguro com testes unitários/de integração, aguardar GitHub Actions e integrar somente após aprovação.
5. Atualizar este checkpoint com links, SHA efetivamente integrado, resultados, bloqueios e próximo passo. Nunca atualizar dados de jogo oficial por testes.

# Ascend Card Game — checkpoint verificável de desenvolvimento

**Atualizado:** 2026-10-19. **Base de código:** `main` após o PR #23; commit `92cefa9357d3f48a8fb652bb2b1e1239842f248c`.

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

**Contagens dos workflows:** os 81 testes da suíte de fuga/destruição são repetidos parcialmente no workflow principal. Não somar esses totais como testes independentes. Cinco workflows do PR #23 foram aprovados: Roper, fuga/destruição, estrutura, ponte e referências do Catálogo SRD.

## Arquivos e módulos atuais relevantes

- `experimental/integration/motor_roper_basico.py`: ações isoladas da fixture e pré-validações; contém `prevalidar_reel`, `prevalidar_multiattack`, liberação de Grappled em KO e validação pós-combate.
- `src/ascend/tentaculo_roper_srd.py`: extrai apenas mecânicas de Tentacle, Reel e composição de Multiattack diretamente do texto da ficha pinada.
- `src/ascend/perfil_combate_srd.py`, `src/ascend/fuga_roper_srd.py`, `src/ascend/testes_d20_srd.py`: perfis, fuga, dados explícitos/desvantagem.
- `tests/integration/test_roper_ko_grapple_cleanup_real.py`: nove casos novos do PR #17.
- `tests/integration/test_roper_multiattack_preflight_real.py`: doze casos do PR #18, ajustados para indicar execução parcial.
- `tests/integration/test_roper_multiattack_atomic_safe_real.py`: dezesseis cenários do PR #23.
- `docs/ROPER_MULTIATTACK_ATOMICO_PARCIAL.md`: limite de escopo, dados simulados, Action única e rollback.
- `.github/workflows/validate-roper-basico.yml`: regressão de todos os componentes do Roper.
- `docs/ROPER_KO_GRAPPLE_CLEANUP.md` e `docs/ROPER_MULTIATTACK_PREVALIDACAO.md`: escopo e limites por incremento.

## Estado mecânico e bloqueios

**No recorte experimental:** Bite e Tentacle individuais (sem exigência de alcance), Grappled/Poisoned, fuga com desvantagem Poisoned, ataque e destruição/regeneração de tentáculos, limpeza de vínculos em KO, preflight puro de Reel/Multiattack, Action Reel individual executável **sem deslocamento** quando há Grappled válido e Multiattack executável **em uma Action** no subconjunto sem dois Grappled simultâneos, com 16 novos testes e rollback transacional em cenários não integrados. Todos exigem fontes verificadas e não são combate SRD integral.

**DECISÃO JÁ VIGENTE DESDE 15/10/2026, RATIFICADA EM 19/10/2026:** nenhum combate usa posição, arena, distância ou checagem de alcance espacial. Ver contrato `docs/poc/01_Regras/CONTRATO_DE_REGRAS.md` e [Issue #19 encerrada](https://github.com/george-vepo/Ascend-Card-Game/issues/19). A ausência de arena jamais bloqueia uma ação. O [PR #21](https://github.com/george-vepo/Ascend-Card-Game/pull/21) removeu as verificações espaciais e habilitou Reel individual como Action sem deslocamento, com cinco workflows verdes e merge confirmado na `main`.

**PENDENTE:** Multiattack integral quando dois tentáculos agarram simultaneamente o mesmo alvo; a semântica da fuga/encerramento de vínculos depende da [issue #24](https://github.com/george-vepo/Ascend-Card-Game/issues/24). Spider Climb e demais componentes SRD ainda não suportados. O deslocamento posicional/vôo/arena **não será implementado**; efeitos não espaciais dessas habilidades exigem ficha e contrato verificáveis.

**Próximo incremento seguro:** aguardar decisão expressa da issue #24 antes de homologar **dois Grappled simultâneos**; em paralelo, fortalecer os cenários independentes (crítico, KO, resistências, idempotência, integridade/checkpoint) sem inventar semântica de fuga nem geometria. O Multiattack atômico **parcial** já foi integrado pelo PR #23, e a checagem espacial foi removida no PR #21; não recriar.

**Partida oficial:** não iniciada. **Placar oficial:** J1 0 × 0 J2. **Rolagens em CI:** simuladas, externas e explícitas. Não publicar mãos, decks privados, ordem de montes nem snapshots de estado competitivo real.

## Procedimento de retomada

1. Confirmar o commit **real e atual** da `main`, PRs e branches antes de qualquer alteração (este arquivo é um checkpoint histórico, não substitui consulta ao GitHub).
2. Comparar com os PRs e issues posteriores a #18/#19; aproveitar branches válidas ainda não integradas.
3. Verificar novamente `config/catalogo_srd.json`, a ficha integral externa e o manual SRD 5.2.1 antes de alterar combate.
4. Criar branch a partir da `main` mais recente, implementar apenas incremento seguro com testes unitários/de integração, aguardar GitHub Actions e integrar somente após aprovação.
5. Atualizar este checkpoint com links, SHA efetivamente integrado, resultados, bloqueios e próximo passo. Nunca atualizar dados de jogo oficial por testes.

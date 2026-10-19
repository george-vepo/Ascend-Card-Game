# Ascend Card Game — checkpoint verificável de desenvolvimento

**Atualizado:** 2026-10-19. **Base de código:** `main` após o PR #18; commit `71971a0873523374f4c0a52e6652f017789bcdc0`.

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

**Contagens dos workflows:** os 81 testes da suíte de fuga/destruição são repetidos parcialmente no workflow principal. Não somar esses totais como testes independentes. Cinco workflows do PR #18 foram aprovados: Roper, fuga/destruição, estrutura, ponte e referências do Catálogo SRD.

## Arquivos e módulos atuais relevantes

- `experimental/integration/motor_roper_basico.py`: ações isoladas da fixture e pré-validações; contém `prevalidar_reel`, `prevalidar_multiattack`, liberação de Grappled em KO e validação pós-combate.
- `src/ascend/tentaculo_roper_srd.py`: extrai apenas mecânicas de Tentacle, Reel e composição de Multiattack diretamente do texto da ficha pinada.
- `src/ascend/perfil_combate_srd.py`, `src/ascend/fuga_roper_srd.py`, `src/ascend/testes_d20_srd.py`: perfis, fuga, dados explícitos/desvantagem.
- `tests/integration/test_roper_ko_grapple_cleanup_real.py`: nove casos novos do PR #17.
- `tests/integration/test_roper_multiattack_preflight_real.py`: doze casos novos do PR #18.
- `.github/workflows/validate-roper-basico.yml`: regressão de todos os componentes do Roper.
- `docs/ROPER_KO_GRAPPLE_CLEANUP.md` e `docs/ROPER_MULTIATTACK_PREVALIDACAO.md`: escopo e limites por incremento.

## Estado mecânico e bloqueios

**No recorte experimental:** Bite e Tentacle individuais, Grappled/Poisoned, fuga com desvantagem Poisoned, ataque e destruição/regeneração de tentáculos, limpeza de vínculos em KO e preflight puro de Reel e Multiattack. Todos exigem fontes verificadas e não são combate SRD integral.

**DECISÃO JÁ VIGENTE DESDE 15/10/2026, RATIFICADA EM 19/10/2026:** nenhum combate usa posição, arena, distância ou checagem de alcance espacial. Ver contrato `docs/poc/01_Regras/CONTRATO_DE_REGRAS.md` e [Issue #19 encerrada](https://github.com/george-vepo/Ascend-Card-Game/issues/19). A ausência de arena jamais bloqueia uma ação. A branch `fix/roper-sem-posicionamento-poc` corrige verificações espaciais no motor experimental, habilitando Reel individual como Action sem deslocamento; confirmar CI e merge antes de tratar como integrado.

**PENDENTE:** Multiattack executável (segunda Tentacle no mesmo alvo, sequência completa como uma Action), Spider Climb e demais componentes SRD ainda não suportados. O deslocamento posicional/vôo/arena **não será implementado**; efeitos não espaciais dessas habilidades exigem ficha e contrato verificáveis.

**Próximo incremento seguro:** corrigir e integrar com CI as chamadas que exigiam `alvo_no_alcance_fixture` ou arena indevidamente. Em seguida, implementar Multiattack por etapas verificadas com testes e economia de uma Action, sem arena e sem criar mecânicas de movimento. Não recriar o que já está integrado.

**Partida oficial:** não iniciada. **Placar oficial:** J1 0 × 0 J2. **Rolagens em CI:** simuladas, externas e explícitas. Não publicar mãos, decks privados, ordem de montes nem snapshots de estado competitivo real.

## Procedimento de retomada

1. Confirmar o commit **real e atual** da `main`, PRs e branches antes de qualquer alteração (este arquivo é um checkpoint histórico, não substitui consulta ao GitHub).
2. Comparar com os PRs e issues posteriores a #18/#19; aproveitar branches válidas ainda não integradas.
3. Verificar novamente `config/catalogo_srd.json`, a ficha integral externa e o manual SRD 5.2.1 antes de alterar combate.
4. Criar branch a partir da `main` mais recente, implementar apenas incremento seguro com testes unitários/de integração, aguardar GitHub Actions e integrar somente após aprovação.
5. Atualizar este checkpoint com links, SHA efetivamente integrado, resultados, bloqueios e próximo passo. Nunca atualizar dados de jogo oficial por testes.

# Continuidade SRD — limpeza do Grappled no KO do Roper

## Contexto e origem
- Base: `main` após PR #16 (`186c5d0da6af04d4e893f5b811e9ba803063ca78`).
- Trabalho preservado da branch anterior `feat/roper-ko-grapple-cleanup` (commit `fdd1230da4324869232fb2e1042ac3d7d6a138c3`), transposto para a base atual **sem reverter a pré-validação de Reel**.
- Fonte de fichas: `george-vepo/Catalogo-SRD`, revisão `03f84e8426f469ef6a0e471faea2093b7c0b69c9`, Roper `AT-002` / cópia `AB-POC-017` e Giant Owl `CE-001`.
- SRD 5.2.1: Roper p. 320 (Tentacle aplica Grappled e Poisoned até o fim do grapple; tentáculos independentes, sem dano aplicado ao Roper); regra geral de término do Grappled. Nenhum valor de ficha foi copiado para o motor.

## Correção
A fixture `MotorRoperBasico` encerrava o combate e movia a criatura derrotada para o cemitério, mas não liberava o vínculo do Tentacle. A nova sobreposição de `_ko` confere o vínculo com a ficha externa, desfaz Grappled e Poisoned e os registros dos tentáculos ativos, remove registros temporários de destruição, **depois** delega o placar e as zonas a `MotorFichasPOC._ko`. O resultado experimental expõe apenas os números de tentáculos liberados/destruídos e os nomes das condições removidas.

`validate` agora rejeita vínculos de grapple e registros de tentáculos persistentes em `POS_COMBATE` / `ENCERRADA`. Um ataque sem KO **não** limpa condições. A restauração de checkpoint limpo é testada. O comando existente continua idempotente.

## Testes e CI
- Novos casos em `tests/integration/test_roper_ko_grapple_cleanup_real.py`: 9 cenários, com dados explicitamente **simulados** e checkout pinado real do catálogo.
- CI: `.github/workflows/validate-roper-basico.yml` executa os novos testes **e** as regressões de Bite, Tentacle, fuga/destruição, rolagens, Poisoned e Reel.
- Status de CI/merge: **a registrar após os workflows**. Não declarar testes concluídos antes de confirmação.

## Ainda não implementado
- Reel com deslocamento: depende de arena/posições e decisão administrativa.
- Multiattack (2 Tentacle, Reel e 2 Bite): não executar antes de homologar cada componente e a economia de ações composta.
- Spider Climb, combate SRD integral, múltiplos tentáculos no mesmo alvo e movimento.
- Nenhuma partida oficial iniciada; placar oficial permanece 0 × 0; apenas fixtures experimentais.

## Próximo incremento sugerido
Extrair/validar a composição do Multiattack diretamente da ficha externa e oferecer pré-validação **pura e não executável** até que Reel/arena estejam normatizados; alternativamente, depois da decisão administrativa, executar Reel com posicionamento verificado. 

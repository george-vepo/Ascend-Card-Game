# Roper — Multiattack: contrato de fonte e pré-validação sem execução

## Revisão e fonte
Base de desenvolvimento: `main` após PR #17, merge commit `a1c8cad2ff77fa7038e3ffc7a5d6a8e8c07b646c`. O jogo consulta o **Catálogo SRD externo** em `george-vepo/Catalogo-SRD@03f84e8426f469ef6a0e471faea2093b7c0b69c9`, Roper `AT-002`, cópia `AB-POC-017`; material mecânico: SRD 5.2.1, p.320. Nenhuma ficha, imagem ou dataset foi copiado para Ascend.

## Incremento verificável
- O extrator `extrair_multiattack_roper` confere, com correspondência estrita e única, a sequência da seção **Actions** da ficha: duas ações **Tentacle**, uma **Reel**, duas **Bite**, nessa ordem. Se o texto estiver ausente, duplicado ou divergir nas quantidades, retorna `FichaConflitante`.
- `MotorRoperBasico.prevalidar_multiattack()` é uma **consulta pura** e inexecutável: entrega a composição e hash da fonte, identifica bloqueios e não consome Action, dados, eventos, recursos, zonas, PV ou placar.
- `MULTIATTACK_ROPER_TESTE` é validado somente para o Roper no turno correto, mas retorna **PENDENTE**; argumentos declarando arena, distâncias ou rolagens como aprovados não removem o bloqueio. Spider Climb continua inalterado.
- Os ataques individuais já implementados permanecem isolados, sem falsa equivalência com Multiattack. O contrato de Multiattack está documentado e **não habilitado**.

## Bloqueios conhecidos
- O recorte atual não resolve dois tentáculos no mesmo alvo, incluindo o efeito da primeira aplicação de Grappled.
- Reel exige geometria e movimentação homologadas pelo administrador; a pré-validação do PR #16 não autoriza sua execução.
- Bite após Reel exige distância real e regra aprovada de arena.
- Execução de vários ataques e uso de Reel dentro de uma **única Action** ainda não existe; jamais tratá-los como cinco turnos independentes.

## Testes e checkpoint
- `tests/integration/test_roper_multiattack_preflight_real.py`: 12 casos usando checkout real pinado, incluindo integridade da fonte, divergências do texto, ausência de mutação, fase/vez, spoofing de parâmetros, checkpoint e privacidade.
- Workflow `validate-roper-basico.yml`: roda os 12 testes e todas as suítes regressivas anteriores (Bite/Tentacle/fuga/rolagens/Poisoned/Reel/KO).
- Evidência de CI: conferir PR #18. A aprovação e o merge dependem dos workflows.
- Partida oficial **não iniciada**; placar oficial **0 × 0**. Rolagens de testes permanecem rotuladas como simuladas.

## Próximo passo
Sem decisão administrativa de arena, continuar apenas componentes independentes, como reforçar testes de integridade ou contratos de ações. Antes de autorizar Multiattack, regulamentar arena/posições e implementar Reel e múltiplos ataques na economia de uma Action com testes de integração.

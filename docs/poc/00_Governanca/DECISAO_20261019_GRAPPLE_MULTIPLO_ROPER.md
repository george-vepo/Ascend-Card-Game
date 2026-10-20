# Decisão aprovada — múltiplos Tentacle agarrando o mesmo alvo (Roper)

**Aprovação expressa do administrador:** 19/10/2026, em resposta afirmativa à proposta de simplificação do Card Game. **Issue de origem:** [#24](https://github.com/george-vepo/Ascend-Card-Game/issues/24). Esta regra é **homebrew do jogo**, não um novo texto oficial do SRD.

## Precedência

- SRD 5.2.1, ficha Roper, p. 320: Tentacle, Grappled, Poisoned, escape DC 14, seis tentáculos, CA/PV de cada tentáculo, regeneração, Reel e Multiattack.
- Contrato [15/10/2026](../01_Regras/CONTRATO_DE_REGRAS.md): elimina todas as posições, medidas de distância e alcance espacial em combate.
- Esta aprovação resolve exclusivamente a sobreposição de **múltiplos Grappled do mesmo Roper sobre a mesma criatura** (não regula efeitos de criaturas diferentes nem condições arbitrárias).

## Contrato mecânico aprovado

1. Tentáculos diferentes do mesmo Roper **podem acertar e agarrar o mesmo alvo**. Cada slot de 1 a 6 mantém vínculo individual, PV atuais e máximos, origem e identificação próprios. Slot destruído não pode atacar antes da regeneração prevista pela ficha. Um mesmo slot não pode estar ocupado duas vezes.
2. Os vínculos múltiplos geram **uma ocorrência visual** das condições `Grappled` e `Poisoned` no alvo. Não multiplicar penalidades, CD, dano ou outras consequências dessas condições por número de tentáculos.
3. O alvo escolhe **Athletics** ou **Acrobatics** e gasta **uma Action** para escapar. Faz **um teste** contra a **CD 14** extraída da ficha. `Poisoned` impõe desvantagem (dois d20, usa o menor). **Um sucesso libera todos os vínculos desse Roper com o alvo**; uma falha conserva todos. Não rolar uma fuga por tentáculo. A liberação conjunta em um teste é a simplificação **homebrew** expressamente aprovada.
4. Destruição ou liberação **individual** de tentáculo termina apenas aquele vínculo. Enquanto ao menos um vínculo permanecer, `Grappled` e `Poisoned` permanecem. Ao terminar o último, ambas desaparecem.
5. `Reel` é usado **uma vez** dentro de `Multiattack` (2 Tentacle, Reel, 2 Bite, numa única Action) e considera cada criatura alvo apenas **uma vez** independentemente da quantidade de tentáculos agarrando. Não há deslocamento, arena, posições ou checagem de alcance.
6. Em **KO**, liberar todos os tentáculos/grapples ativos e remover as condições relacionadas antes de concluir o combate, mover a carta derrotada ao cemitério e pontuar **uma vez**. Preservar 40 cópias em zonas, identificadores únicos, privacidade, ordem do monte e histórico idempotente.

## Limites e implementação

- O jogo continua sem arena ou métricas espaciais; valores de alcance no SRD podem ser exibidos apenas como metadados de origem.
- A regra só fica **implementada no motor** depois de testes e merge. Não inferir sua execução a partir da existência deste documento.
- O motor experimental `MotorRoperBasico` continua recorte de fixture, com dados/rolagens simulados e explícitos; não constitui combate SRD integral nem inicia partida oficial.
- A origem das fichas permanece o Catálogo SRD externo fixado pelo manifesto. Não duplicar fichas ou artes neste repositório.

**Partida oficial:** não iniciada. **Placar:** J1 0 × 0 J2.

# SRD Card Game — POC ChatGPT v1.3
## Ordem de preparação, prioridade aleatória e resolução pré-batalha dos suportes

**Decisão do administrador:** 16/10/2026 — sequência expressa na conversa.  
**Aplicação:** somente POC humano (J1, deck Celestial) contra IA (J2, deck Aberração).  
**Natureza:** especificação de execução; **não é partida iniciada**.  
**Precedência:** esta v1.3 substitui somente as janelas de ativação de suporte e a sequência de fases conflitantes de v1.1/v1.2. Demais disposições aprovadas seguem válidas.

## 1. Nova sequência definida pelo administrador

0. **Sorteio da prioridade:** antes da preparação, determinar aleatoriamente quem começa a executar as etapas. Chamar os lados `PRIMEIRO` e `SEGUNDO` exclusivamente para a preparação. Não confundir esse resultado com iniciativa do combate. Ainda não foi sorteado nada.
1. **Troca de cartas:** fase de troca (0 a 5 cartas da mão, descartar e comprar a mesma quantidade do topo). A ordem de execução entre J1/J2 segue a prioridade sorteada. A duração/frequência da troca para confrontos futuros depende das regras aplicáveis e pendências.
2. **Escolha da criatura pelo PRIMEIRO:** invocar uma Comum válida, ou preparar a criatura já ativa segundo as regras cabíveis. Evoluções dependem do limite ainda a aprovar e dos requisitos de mesmo tipo + classe adjacente.
3. **Escolha da criatura pelo SEGUNDO:** ação equivalente; mão adversária permanece oculta, criatura no campo é pública.
4. **Escolha do suporte pelo PRIMEIRO:** selecionar **zero ou uma carta de sua mão**, ou **Sem suporte**. Se selecionar, marcar `suporte_reservado = true` na própria mão; nada comprar nesta etapa.
5. **Escolha do suporte pelo SEGUNDO:** ação equivalente, mantendo carta do oponente oculta até ser usada.
6. **Resolução do suporte do PRIMEIRO:** se escolheu Sem suporte, pular. Se houver carta válida/homologada, verificar habilidade e elegibilidade, resolver **uma aplicação** antes da iniciativa, registrar efeitos, enviar cópia da mão ao cemitério, repor mão até 5 quando houver monte. Não consumir ação, ação bônus ou reação.
7. **Resolução do suporte do SEGUNDO:** mesmo procedimento. Se o efeito anterior inviabilizar a segunda resolução ou a própria batalha, não improvisar solução: marcar PENDENTE e solicitar decisão.
8. **Batalha:** apenas após 6–7, aplicar os efeitos ainda vigentes e rolar iniciativa segundo SRD 5.2.1. A **iniciativa**, não o sorteio de preparação, determina quem age primeiro e a ordem dos turnos. Respeitar ficha de origem e a adaptação de combate aprovada para o Card Game (sem movimentação/posicionamento/alcance espacial). **Não há botão de ativação de suporte durante o combate** nesta versão.
9. **Rodada seguinte:** a expressão do administrador ainda exige distinção. Se o combate continua, seguir novas rodadas/turnos com a iniciativa vigente, **sem repetir escolhas e suportes**. Se uma criatura caiu a 0 PV, aplicar vitória/placar/zonas e a preparação do **próximo combate**, preservando PV da sobrevivente, mãos, montes, cemitérios e recursos. Frequência do novo sorteio e início de fases no confronto seguinte são PENDENTES.

## 2. Diferença decisiva em relação à v1.2

A regra anterior `ativar o suporte durante o próprio turno, antes ou depois da ação principal` foi **substituída pela nova ordem declarada**: as etapas 6 e 7 ocorrem **antes de começar a batalha e antes da iniciativa**. Não executar ambas as modalidades. O bloqueio de usos concorrentes enquanto reservado, o limite de uma carta, a escolha opcional e a única aplicação por combate permanecem.

## 3. Integridade e privacidade

- A reserva permanece na **MÃO**; nunca é quinta zona e não provoca compra.
- Até a resolução do suporte, não é permitido usar essa mesma cópia para qualquer outra finalidade.
- Quando a habilidade é válida e aplicada, revelá-la como fato de jogo, descartar e recompletar a mão até 5 conforme o manual. A informação de J2 não revelada continua oculta.
- **Sem suporte:** não reservar, não descartar, não comprar; pular somente a etapa de suporte do respectivo lado.
- Suporte candidato não homologado **não** se torna legal pela mudança de fase; não resolver nem descartar em caso de PENDENTE.
- A resolução exige ficha integral da versão correta e validação de requisitos, alvos, CDs, dano, testes, duração, concentração, recargas e efeitos. Passivos e habilidades condicionais exigem aprovação específica; não inventar conversão para uso pré-batalha.
- Registre cada rolagem com sua origem; se não houver ferramenta de sorteio verificável, identificar como `SIMULADA`. Não antecipar sorteio agora.
- Conservar 40 IDs únicos por deck em quatro zonas oficiais; J1 `CE-001..040`, J2 `AB-POC-001..040`, preservando referências `AB-REF` originais.
- A IA controla suas próprias estratégias sem usar informações privadas da mão do humano, embora a separação dentro de um único ChatGPT seja apenas lógica.

## 4. Pendências que não foram aprovadas pela sequência

1. **Q-02 — Quantidade de evoluções** na preparação (nenhum número foi aprovado).
2. **Q-04 — Alterar suporte já confirmado** antes de sua resolução.
3. **Q-05/Q-10 — Homologar individualmente os efeitos** para aplicação pré-batalha; atualmente 0 de 80 homologados.
4. **Q-09 — Fichas completas** dos decks experimentais; a maioria ainda sem validação integral.
5. **Q-13 — Interações pré-batalha:** habilidade que pressupõe turno/reação/iniciativa; efeitos que incapacitem ou reduzam a criatura a zero PV antes da batalha; prazos de condições e concentração iniciados na preparação.
6. **Q-14 — Significado de “outra rodada”**: rodada de combate ou próximo confronto depois do resultado; início das fases e eventual novo sorteio no próximo confronto.
7. **Q-06/Q-07/Q-08:** monte vazio, resultado simultâneo/combate sem progresso e substituição voluntária permanecem sem regra geral aprovada.

**Regra de arbitragem:** na dúvida, a ação depende de deliberação do administrador; não aplicar dano, descartes ou vitória por analogia.

## 5. Checklist antes de iniciar

- [x] Modo humano vs IA e decks virtuais de 40 IDs para a POC autorizados.
- [x] Suporte opcional 0–1, da mão, após escolher criatura.
- [x] Sorteio para prioridade de preparação, efeitos de suportes antes da batalha e iniciativa separada definidos.
- [ ] Homologação de fichas e dos suportes necessários.
- [ ] Limite de evoluções e situações pré-batalha críticas decididos.
- [ ] Procedimento de rodadas/confrontos seguintes esclarecido.
- [ ] Autorização explícita para embaralhar e distribuir.

**Estado atual:** PRÉ-PARTIDA / BLOQUEADO. **Zero sorteios, zero embaralhamentos, zero compras, zero efeitos executados.**
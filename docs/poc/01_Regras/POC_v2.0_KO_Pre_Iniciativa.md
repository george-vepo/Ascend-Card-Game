# POC 2.0 — KO por suporte antes da iniciativa

**Decisão aprovada pelo administrador em 17/10/2026.** Escopo exclusivo da POC ChatGPT (Celestial humano x Aberração IA). **Nenhum combate nem sorteio ocorreu.** Esta decisão resolve a parte de Q-13 referente ao KO pré-iniciativa; NÃO homologa automaticamente as habilidades dos decks.

## Regra executável POC-20

1. Durante a preparação, PRIMEIRO e SEGUNDO escolhem individualmente 0 ou 1 suporte da mão. Seleção confirmada fica reservada na própria mão (`suporte_reservado = true`). A prioridade PRIMEIRO/SEGUNDO foi definida por um único sorteio de duelo (ainda NÃO realizado) e permanece a mesma nos ciclos seguintes.
2. Resolver a habilidade individualmente homologada do PRIMEIRO, **antes da iniciativa**, considerando alvo válido, CA/CD, rolagens, tipos de dano, resistências, imunidades, condições, durações e demais requisitos do SRD/ficha da criatura. O suporte aplicado sai da mão para o cemitério, sem saque imediato.
3. **Se essa resolução deixar a criatura adversária a 0 PV, encerrar imediatamente o combate**. A criatura derrotada vai ao cemitério, o controlador do suporte que causou o KO recebe **1 ponto** (e não pontos extras pelo mesmo efeito). Registrar `KO_PRE_INICIATIVA`, `VITORIA_COMBATE` e alterações de zona de maneira idempotente. **Não rolar iniciativa.**
4. O SEGUNDO não resolve nem ativa seu suporte. Se havia uma carta reservada, retirar somente `suporte_reservado`; **a mesma cópia permanece na mão** e não é descartada nem comprada outra para substituí-la. Nada é revelado além do permitido pelo efeito e das informações públicas da batalha.
5. Caso não haja KO pelo PRIMEIRO, resolver o suporte homologado do SEGUNDO, quando selecionado e legal. **Se o SEGUNDO causar KO**, finalizar imediatamente, atribuir-lhe 1 ponto e não rolar iniciativa. Os suportes efetivamente usados anteriormente já permanecem consumidos/descartados.
6. Se, após as resoluções de suporte, ambas criaturas estiverem acima de 0 PV, rolar a iniciativa SRD desse combate e seguir turnos até uma criatura atingir 0 PV.
7. Com 3 pontos, a partida encerra imediatamente. Sem vencedor final, começa um novo ciclo na **ordem fixa de preparação**; J1 e J2 compram do topo **até completar 5** só **na abertura do novo ciclo**, antes da troca. Não há compra no próprio evento KO nem saque especial do sobrevivente. PV da sobrevivente, mãos, montes, cemitérios e recursos remanescentes persistem.

## Exceções NÃO resolvidas

- Se um efeito provocar **mortes simultâneas** ou KO no próprio controlador do suporte, a regra atual não especifica vencedor do combate; parar antes de conceder ponto e solicitar decisão administrativa (Q-07).
- Suporte inválido ou sem homologação não causa efeito, consumo nem KO; não tratar simples declaração como execução.
- Duração ancorada no próximo turno da criatura de suporte descartada, efeitos passivos, controle, agarrão e concentração exigem homologação específica. POC-20 não as torna válidas.
- Alterar uma reserva já confirmada antes da resolução continua sem regra aprovada (Q-04).
- Monte vazio e compra insuficiente só consomem cartas realmente existentes; resultado competitivo por esgotamento segue pendente (Q-06).

## Invariantes do árbitro

- Uma única cópia em cada zona, 40 cópias por jogador, toda marca de suporte associada à cópia na mão; liberação da reserva antes de concluir o evento de vitória.
- Histórico público com evento e versão E###, PV antes/depois, dano e resistências, cartas publicamente reveladas, placar e próxima fase.
- Rolagens não verificáveis são identificadas como **SIMULADAS**.
- O estado oficial segue não iniciado; esta decisão não executa sorteio de PRIMEIRO, iniciativa, compra, dano ou partida.
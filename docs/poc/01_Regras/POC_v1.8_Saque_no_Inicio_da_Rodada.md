# SRD Card Game — POC v1.8 | Saque simétrico no início da rodada

**Data:** 17/10/2026. **Status:** decisão do administrador registrada; um detalhe operacional aberto. **Não foi iniciada partida.**

## Regra POC-18 — Decisão expressa

O administrador corrigiu a suposição de compra extra para a sobrevivente e declarou: **“não tem isso não, o saque acontece para ambos jogadores no inicio da rodada”.**

1. **Não existe fase de saque/troca especial da criatura sobrevivente** na POC. Não aplicar a previsão antiga do manual v0.9 ou os trechos históricos das versões 1.1–1.7 nesse ponto.
2. **O saque deve ser concedido aos dois jogadores no início da rodada**, simultaneamente como direito de ambos e sem benefício de sobrevivência. Registrar como evento de compra validado e auditável quando a janela for operacionalmente definida.
3. **Não executar compra automática no instante do KO/fim do combate.** As compras não ocorrem após invocar, evoluir ou usar suporte. A distribuição inicial de cinco cartas e as compras de substituição durante a fase de troca continuam distintas.
4. Repor mão até cinco continua a referência da mecânica anterior, mas a expressão **“rodada” precisa ser desambiguada** antes de definir o disparo do saque: (A) rodada interna de turnos do mesmo combate, ou (B) novo ciclo de preparação depois do KO. Não adotar A nem B automaticamente. Se necessário, confirmar se a quantidade é exatamente até cinco nessa janela.
5. Não duplicar saque no fim de um combate e no início do seguinte. Respeitar a ordem do monte, disponibilidade de cartas, IDs únicos e proteção das informações ocultas.
6. O combate continua até uma criatura atingir 0 PV; vencedor +1 ponto; sobrevivente permanece com PV restantes; primeiro a 3 pontos encerra imediatamente. A ordem PRIMEIRO/SEGUNDO permanece fixa por sorteio único antes de toda a partida; iniciativa é própria de cada combate.

## Conflitos documentais e precedência

- O manual v0.9 e a POC v1.7 mencionavam fase adicional exclusiva da sobrevivente e/ou reposição imediatamente após KO. **POC-18 supera essas disposições na POC**, por instrução posterior e explícita do administrador.
- **Q-16 encerrada como não aplicável. Q-17 aberta:** definição operacional de `rodada`. Até Q-17, não realizar compra automática cujo gatilho dependa da palavra rodada.
- Os suportes continuam selecionados 0–1 da mão, resolvidos PRIMEIRO → SEGUNDO antes da iniciativa, com descarte e sem compra instantânea. Suportes e fichas candidatos ainda não são homologados automaticamente.

## Testes de aceitação (não executados)

- Nenhuma compra extra para a sobrevivente.
- Nenhuma compra imediata na resolução do KO.
- Após Q-17, ambos compram na mesma janela aprovada, sem ultrapassar mão máxima ou monte restante.
- Não há saque duplicado entre fim e início de ciclos.
- Compras iniciais e troca com reposição equivalente são preservadas.
- Contagem de exatamente 40 cópias por jogador em zonas válidas.

**Estado da POC:** pré-partida, sem sorteio inicial, sem embaralhar, sem compra ou combate.
# SRD Card Game — POC ChatGPT v1.4 | Ciclos e combate até a morte

**Data:** 16/10/2026 | **Status:** complemento aprovado para POC; nenhuma partida iniciada.

## Precedência

Complementa a POC v1.3, o manual do duelo v0.9 e a decisão expressa do administrador desta conversa sobre a expressão **“outro ciclo”**. Em divergência com rascunhos anteriores que apresentem o passo 9 como ambíguo, prevalece esta definição de ciclo. A aprovação não completa regras pendentes.

## Preparação (cada novo ciclo, quando legalmente aplicável)

0. Prioridade PRIMEIRO/SEGUNDO decidida por sorteio para a **primeira preparação**. **PENDENTE** se repete o sorteio nos ciclos seguintes.
1. **Troca de cartas** segundo o manual, respeitando a ordem legal de preparação a definir para ciclos subsequentes.
2. PRIMEIRO prepara criatura de combate: invocação Comum, ou evolução legal de criatura ativa do mesmo tipo e classe consecutiva; não remover a criatura sobrevivente sem regra aprovada.
3. SEGUNDO prepara criatura sob as mesmas regras.
4. PRIMEIRO seleciona **zero ou uma carta de suporte da mão**.
5. SEGUNDO seleciona zero ou uma carta de suporte da mão.
6. Suporte do PRIMEIRO: aplicar **uma única vez** a habilidade homologada, antes da iniciativa, depois descartar e repor mão até cinco quando possível; se Sem suporte, pular.
7. Suporte do SEGUNDO: idem, na ordem; avaliar efeitos anteriores e requisitos.
8. **Novo combate:** rolar iniciativa SRD, aplicando todas as regras de combate aprovadas ao Card Game; sem movimento, posicionamento ou alcance espacial conforme decisão posterior.

## Enquanto nenhuma criatura chegou a 0 PV

- Prosseguir a ordem dos turnos e rodadas **na mesma batalha e mesma iniciativa**.
- Preservar PV, condições, concentrações, recargas, limitações e recursos, com aplicação de duração conforme ficha oficial.
- Não trocar baralhos, não reiniciar mão/cemitério, não reiniciar sorteios, não escolher/ativar novamente suportes por simples início de rodada.
- Confronto não termina por fim de rodada ou por ND; somente por derrota conforme regra aprovada, ressalvados casos excepcionais ainda sem solução.

## Quando uma criatura chega a 0 PV

1. Validar a derrota, os danos e os efeitos, registrar evento e PV/condições.
2. Colocar a cópia derrotada no CEMITÉRIO e retirar sua posição de CAMPO.
3. Creditar **um ponto** à sobrevivente.
4. Manter a sobrevivente em CAMPO com **PV remanescentes**, sem cura automática, e preservar zonas, ordem dos montes e histórico.
5. Concluir descarte/liberação de eventuais reservas não usadas segundo a regra aplicável; como os suportes são pré-batalha, não gerar reativação no fim.
6. Se a pontuação chegar a 3: **fim imediato do duelo**, sem fase preparatória ou saque pós-combate por encerramento.
7. Se não chegou a 3: aplicar a **fase extra de saque e descarte/troca da sobrevivente** prevista no manual, respeitando decisão de ordenação operacional e disponibilidade de cartas; abrir **outro ciclo** com preparação apropriada para o combate seguinte; o derrotado deverá voltar a ter criatura legal em campo e a sobrevivente mantém seu estado até eventual evolução legal.

## Separações indispensáveis

- **Rodada:** turnos dentro do mesmo combate — sem repetição de seleção de suportes.
- **Combate:** dura até 0 PV de uma criatura; vale um ponto à sobrevivente.
- **Ciclo:** preparação + combate, repetido após uma derrota enquanto ninguém tiver 3 pontos.
- **Partida/duelo:** conjunto persistente de ciclos até 3 pontos.

## Questões NÃO resolvidas por esta decisão

- Frequência do sorteio de PRIMEIRO/SEGUNDO no **novo ciclo**.
- Limite de evoluções e ordem detalhada de fases pós-combate, incluindo fase extra da sobrevivente.
- Troca voluntária de criatura sobrevivente, alteração de suporte já confirmado, empate/morte simultânea, monte vazio e habilidades que exigem início de turno antes da iniciativa.
- Homologação individual das fichas/80 habilidades candidatas; apenas cartas e suportes validados podem ser resolvidos.

## Verificações obrigatórias

- Nunca executar dois combates como se fossem a mesma rodada; não zerar o estado ao abrir novo ciclo.
- Ao terminar uma rodada sem derrota, próximo turno/rodada preserva a iniciativa do combate corrente.
- Ao terminar combate, somar somente 1 ponto, não mais de 1 por criatura derrotada.
- Ao alcançar a terceira vitória, interromper antes da próxima preparação.
- Registrar todo evento em estado versionado e auditar 40 IDs únicos por lado.

**Estado atual:** PREPARAÇÃO, sem sorteios, embaralhamentos, mãos compradas ou combate iniciado.
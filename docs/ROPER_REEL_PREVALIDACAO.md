# Reel — pré-validação sem arena

A ficha SRD 5.2.1 do Roper estabelece que **Reel** puxa cada criatura agarrada por ele até **30 pés em linha reta na direção do Roper**. O Ascend já controla um tentáculo ativo, sua cópia de origem e a condição Grappled/Poisoned. Entretanto, o posicionamento e a movimentação da arena continuam sem regra aprovada.

`prevalidar_reel()` consulta o turno, a ficha externa e o vínculo do tentáculo com a criatura agarrada. Retorna o limite de 30 pés da fonte, os alvos identificados e a lista de dados de posicionamento que dependeriam de decisão do administrador. A consulta é pura e **não consome ação, não move criaturas, não altera zonas, PV, eventos ou placar**.

`REEL_ROPER_TESTE` permanece **PENDENTE** quando há alvo válido, explicitando a ausência de regra de arena. Sem alvo agarrado, o diagnóstico é `SEM_ALVO_AGARRADO`. Não é autorização para executar Reel, nem define arena ou distância por conta própria. A execução dependerá de regra aprovada e testes adicionais.

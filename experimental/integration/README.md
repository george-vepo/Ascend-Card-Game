# Integração de identidades de cópias com o motor legado

Este recorte liga `src/ascend/catalogo_poc.py` ao `experimental/legacy/src/motor_poc.py`, **sem importar datasets para o repositório do Ascend**.

## O que está implementado

- Converte 40 IDs `CE-001...` e 40 IDs virtuais `AB-POC-001...` em registros mínimos para a máquina de estados experimental.
- Conserva identidade, tipo, ND, raridade e chave do Catálogo SRD; não converte texto livre de habilidades em poderes.
- **PV, CA, ataques e outros atributos não são presumidos.** O campo `pv_fonte` fica ausente (`None`) até uma fonte mecânica específica ser verificada. Invocar sem PV é **PENDENTE** e não altera o estado.
- Em testes, `pv_simulados` permite injetar PV explícitos, jamais publicados como ficha ou usados para partida real.
- Verifica 40 cópias de cada lado, posse por ID, separação de mãos, event sourcing, idempotência e checkpoints do motor legado.
- Acrescenta à fixture um vínculo à revisão/hash dos JSONs consultados no catálogo. Restauração com outra origem/identidade não é aceita.

## O que ainda NÃO está implementado

- Embaralhamento, saques e prioridade iniciais oficiais; a fixture recebe uma **ordem determinística de teste**, não aleatória.
- Consulta mecanicamente homologada de PV/CA/ações por criatura ou combate geral SRD 5.2.1.
- Habilidades de suporte homologadas, IA estratégica, interface pública definitiva.
- Persistência real segura de estado entre sessões e isolamento de dados de jogadores.
- Execução de partidas oficiais, decisões para lacunas Q-04, Q-06, Q-07, Q-08 e Q-12.

## Testes

`tests/bridge/` contém fixtures sintéticas: **não copia cartas reais**. `tests/integration/test_motor_catalogo_real.py` utiliza checkout externo do Catálogo SRD no commit configurado e testa apenas as identidades/estado de referência sem PV. Todos os testes são isolados.

Importação do módulo legado exige `PYTHONPATH=src:experimental/legacy/src:experimental/integration`. O projeto não deve tratar o pacote `experimental/` como motor pronto para produção.

**Privacidade:** os checkpoints completos contêm informações ocultas. Nunca publicar artefatos `checkpoint()` em GitHub público, logs compartilhados ou relatórios de mesa. Para UI, usar `mesa_publica()` ou `visao_privada(jogador)`, com controle de autorização em camada futura.

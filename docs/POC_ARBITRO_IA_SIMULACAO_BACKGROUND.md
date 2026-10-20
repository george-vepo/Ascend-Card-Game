# POC — IA simula batalha em segundo plano (issue #35)

**Diretriz administrativa aprovada em 20/10/2026:** interromper a implementação manual de habilidades individualmente como requisito para cobrir o acervo geral. Adotar **árbitro IA híbrido com simulação de batalha em background**.

## Fluxo alvo

1. Jogadores registram suas escolhas no chat/cliente. A IA pode fazer escolhas **só pelo lado que controla**; testes totalmente autônomos podem designar bots aos dois lados, identificados como fixtures.
2. O servidor abre um **job de simulação** desacoplado da interface: `NA_FILA` → `EXECUTANDO` → `AGUARDANDO_JOGADOR` / `AGUARDANDO_DADOS` / `PENDENTE_REGRA` → `CONCLUIDO` ou `FALHOU`. A tela consulta apenas progresso e histórico público, sem precisar permanecer aberta.
3. Modelo consulta **ficha integral da criatura ativa**, SRD 5.2.1 e normas Card Game; recebe somente estado permitido ao controlador. Gera interpretação da jogada e **proposta estruturada**, não um patch arbitrário no estado.
4. Sorteador externo fornece d20 e demais dados verificáveis, nunca arbitrados pela IA; em CI os dados são **explicitamente simulados**, não sorteios oficiais.
5. Motor valida intenção autenticada, ator, fase/vez, revisão/versão/hash de estado, ficha e texto de regras, parâmetros, rolagens e zonas. Só este motor muta PV, condições, recursos, turnos, KO e placar.
6. Histórico auditável registra apenas eventos aceitos e saldos públicos. Histórico privado de entrada, mãos, ordem de montes e checkpoints não são compartilhados com oponentes ou observadores.
7. Em ausência de declaração humana, dado, ficha ou regra suficiente, o job fica **suspenso sem concluir o lance**. Retomada futura não duplica o evento graças à idempotência e hash do estado.
8. Não há espaço, arena, movimentação, distância ou alcance físico em nenhuma ação. Regras homebrew aprovadas têm prioridade sobre tradução genérica.

## MVP implementado neste PR (ponte verificável, sem modelo real)

`experimental/integration/arbitro_ia_background.py` expõe:

- `contexto_publico(sessao)`: projeção de campo e metadados de ficha do ator, sem mão ou ordem de monte; `hash_estado` é apenas um compromisso de integridade.
- `JobSimulacao(job_id, sessao, max_passos)`: estado de execução em memória com `status_publico()`; `processar_passo(declaracao, proposta, rolagens)` decide no máximo **uma Action**; `processar_lote(passos, limite_por_lote)` limita execuções sequenciais para evitar loops.
- Contrato `ARBITRO_IA_BACKGROUND_V1`: declarações externas autenticadas pelo serviço que invoca a ponte (J1 humano, J2 controlado pela IA na fixture), proposta literal com hash e proveniência imutáveis, e pacote de dados **SIMULADO_EXTERNO_TESTE**. Proposta adulterada, versão obsoleta, campos extras, comando desconhecido, dados vindos do modelo ou escolha do controlador alterada são rejeitados antes do motor.
- Lista fechada de ações já executáveis na fixture Roper × Giant Owl; nenhuma API deixa a IA escolher arbitrariamente o vencedor, aplicar dano ou revelar a mão adversária.
- Decisões do motor são **ACEITA**, **REJEITADA** ou **PENDENTE**; a ponte preserva os efeitos transacionais de `MotorPOC.apply` e a rastreabilidade de cada evento; o histórico público da fila omite a justificativa livre do modelo.

`tests/integration/test_arbitro_ia_background_real.py` exerce uma sequência **IA Roper → jogador Owl → IA Roper / KO**, privacidade, integridade de 40 cópias, versões, fontes, origem dos dados, tentativas de alterar comando ou payload, replay, pendência de concentração e checkpoint; CI com fichas externas pinadas.

**Limitações explícitas desta primeira entrega:**

- **Ainda NÃO existe um modelo de IA real conectado nem inferência automática**: a proposta é fornecida por um stub externo nos testes.
- **Ainda NÃO existe daemon/worker persistente rodando fora do chat**, banco durável de jobs, lease, scheduler, notificação e tela de progresso. As funções são pontos de integração de um executor assíncrono futuro; não prometer que a simulação continua após encerrar o chat nesta versão.
- O mecanismo ainda está limitado a comandos já presentes na fixture Roper × Giant Owl, não arbitra automaticamente o catálogo com mais de 1.000 fichas.
- A proteção da autenticação da declaração e a prova criptográfica de origem das rolagens devem ser produzidas pelo backend, antes de chamar a ponte. A etiqueta `SIMULADO_EXTERNO_TESTE` em CI não é um sorteador oficial.

## Incremento 2 — fila SQLite durável com lease e fencing (PR posterior ao #36)

A fila persiste **somente metadados públicos e referência opaca** ao checkpoint privado (não guarda cartas, mão, ordem de montes ou estado de combate). `src/ascend/fila_simulacao_background.py` implementa:

- `FilaBackground(path).enfileirar(job_id, referencia_opaca)`: cria job `NA_FILA`, bloqueia IDs duplicados e não recebe dados privados.
- `reivindicar(worker_id)`: reserva job por lease com `token` secreto e número de fencing monotônico, usando transação SQLite `BEGIN IMMEDIATE`; bloqueia execução concorrente dupla.
- `renovar(claim)`: renova lease válido sem perdê-lo; claims antigos não conseguem confirmar depois de expirados/substituídos.
- `confirmar(claim, status, resumo_publico)`: grava somente campos sanitizados `passos_aceitos`, `fase`, `ator_da_vez`, `versao_estado`, `placar_fixture`; rejeita quaisquer campos de mãos/decks/histórico.
- `retomar(job_id, entrada_externa_validada=True)`: apenas quando serviço de autenticação/rolagens indicar nova entrada válida; não presume entradas.
- `cancelar(job_id)`: invalida lease de worker ativo sem alterar por conta própria o estado do motor.
- `executar_tick_worker(fila, worker_id, executor)`: retira **um job** e invoca callback de execução injetado, que carrega a fixture a partir do armazenamento privado e resolve passos sob o contrato anterior; devolve `NA_FILA`, `AGUARDANDO_JOGADOR`, `AGUARDANDO_DADOS`, `PENDENTE_REGRA`, `CONCLUIDO` ou `FALHOU`. Exceções não vazam mensagem nem criam placar falso.
- `status_publico(job_id)`: somente progresso e resumo sem token, IDs privados ou snapshot de cartas.

**Caveat essencial:** o banco de metadados e o tick são duráveis e podem ser utilizados por **um processo separado**, mas ainda não existe adaptador do modelo/sorteador, armazenamento cifrado/restrito dos checkpoints e **serviço daemon efetivamente iniciado**. O sistema não está simulando continuamente uma batalha real enquanto o chat está fechado. A fila isolada não consegue reconstruir o combate do nada; dependerá do backend de execução.

**Validação:** `tests/integration/test_fila_simulacao_background.py`, incluindo reclamação única concorrente, invalidação de worker antigo, heartbeat, retomada apenas após confirmação confiável, cancelamento, privacidade e persistência após reabrir SQLite.

## Próximas entregas para atender o modo background integral

1. Criar **fila durável de jobs**, storage privado de checkpoint com identidade da partida, **worker independente da sessão/UI**, retomada após reinício e API de polling/streaming público; abortar/cancelar com segurança e limites de custo/tempo.
2. Conectar modelo de IA real, com saídas estruturadas e ferramentas de acesso restrito ao Catálogo SRD; manter autenticação dos comandos fora da IA.
3. Integrar serviço de rolagens verificáveis e tradutor de efeitos SRD suficientemente genérico para o acervo, sempre com validação determinística de estado/recursos e tratamento `PENDENTE_REGRA`.
4. Medir cobertura e divergências em fixtures de dezenas/centenas/milhares de fichas, sem confundir passagem no benchmark com homologação completa do SRD.

**Partida oficial:** não iniciada. Placar oficial J1 0 × 0 J2. Nenhuma ficha copiada ou alterada no Catálogo SRD.

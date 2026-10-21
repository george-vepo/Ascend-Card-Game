# Checkpoint privado cifrado — etapa experimental (sem partida oficial)

Este componente armazena snapshots **exclusivamente em um SQLite privado fora do Git**, para possibilitar retomadas com versionamento verificável. É um adaptador de storage **isolado**, que ainda não está conectado ao `JobSimulacao`, à fila ou a um daemon. Não inicia partidas, não simula decisões, não consulta IA e não valida resultados de combate.

## Contrato de acesso

- `CheckpointPrivado(caminho_absoluto_db, chave_aes_256_em_bytes)` exige uma chave externa de 32 bytes; **não a gera, não a grava nem a publica**. O backend deve obter e administrar a chave por um gestor de segredos seguro, configurando backup e rotação antes de produção.
- `salvar(referencia_opaca, estado_privado, versao_esperada=0)` cria um snapshot e retorna versão `1`; depois toda alteração exige `versao_esperada` igual à versão atual. Escritores antigos são rejeitados com `VersaoDesatualizada` por uma transação SQLite.
- `carregar(referencia_opaca)` devolve `{versao, estado}` para o backend autenticado com a chave, ou `None` se não existe. A referência é um identificador opaco sem dados privados, compatível com a fila existente.
- AES-256-GCM com nonce novo por gravação e dados autenticados (`referencia` + `versao`) protege confidencialidade e integridade. Alterar o ciphertext, misturar referências ou usar outra chave provoca erro, sem expor mãos, montes, cópias ou stacktrace no retorno do módulo.
- Limite de 2 MB por snapshot JSON; validação de IDs e revisões impede caminhos e replays.

## Segurança operacional

- O arquivo SQLite e eventuais arquivos de journal devem ficar num diretório **fora do clone Git**, com controle de acesso somente ao processo autorizado. Em POSIX, o código exige pasta `0700` e arquivo `0600`; em Windows, o operador precisa configurar ACLs NTFS adequadas, pois as permissões Unix não são equivalentes.
- **Nunca adicionar banco, chave, token ou snapshot à árvore Git, ao Pages, a logs de CI, a relatórios de jogo ou ao Drive.** Apenas os testes com cartas fictícias fazem parte do repositório.
- A chave não deve ser perdida: sem ela os estados cifrados não poderão ser recuperados. Ainda não há rotação, recuperação de backup, alta disponibilidade ou gestor de chaves integrado.
- A fila SQLite pública continua armazenando somente metadados e a referência opaca. O jogo deverá verificar o fencing da fila também antes da persistência final do snapshot; este módulo **não** concede permissão de escrita a workers por si só.

## Testes

`python -m pip install "cryptography>=42,<48"`

`PYTHONPATH=src python -m unittest discover -s tests/integration -p test_checkpoint_privado.py -v`

Os testes exercitam 10 cenários: persistência após reabrir, ciphertext sem cartas em texto plano, comparação de versão, proteção contra chave errada, corrupção, troca de referências, identificadores inseguros, tipos inválidos, permissões POSIX e concorrência de escritores. **Todas as mãos e montes são fixtures fictícias; nenhuma partida oficial foi criada.**

## Próximo passo

Implementar adaptador autenticado que associe a `referencia_opaca` da fila a este storage e imponha `fencing`/lease no momento de gravar, seguidos de testes de interrupção do processo e recuperação antes de ligar uma IA real. Somente depois adicionar executor daemon, serviço de dados e sorteador verificável.

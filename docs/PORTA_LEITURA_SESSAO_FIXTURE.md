# Etapa 5 — Porta de leitura privada de fixtures (backend isolado)

Esta entrega adiciona `src/ascend/porta_leitura_fixture.py`, um **adaptador de leitura** para snapshots de teste armazenados por `CheckpointPrivado` (SQLite cifrado, da etapa #48).

## Limites e finalidade

- **Não é login de produção, servidor HTTP, autenticação de navegador ou jogo oficial.**
- O laboratório publicado em GitHub Pages **não** acessa este backend. Nenhum arquivo de checkpoint, credencial ou estado privado foi adicionado ao Pages.
- Apenas snapshots com `ambiente = "FIXTURE_NAO_OFICIAL"` e estrutura estrita de duas zonas de 40 cópias são processados.
- Os tokens são configurados por **backend confiável**, associados a uma referência opaca e ao papel `PUBLICO`, `J1` ou `J2`. É obrigatório fornecer os três, distintos, codificados com pelo menos 32 caracteres URL-safe. **A biblioteca não gera, entrega, persiste ou revoga credenciais**; isso exige serviço de identidade futuro.
- Há uma referência de checkpoint por sessão. Tokens de outra sessão são rejeitados **antes da leitura do banco**. A ausência de referência e a credencial inválida usam o mesmo erro genérico.
- `PUBLICO` recebe só fase, vez, placar, versão, contagens e criatura em campo com CA/PV públicos. Nenhum ID de mão, ordem de monte, inventário ou histórico privado.
- `J1` e `J2` recebem **além do público somente sua própria mão**; a mão oposta continua resumida por quantidade. Nenhum extra desconhecido do snapshot atravessa as whitelists.
- As visões são objetos novos e não atualizam o checkpoint. A API exposta não possui métodos de escrita.
- Valida soma de 40 cópias por jogador, IDs distintos globalmente, PV válidos da criatura em campo e marcador de fixture antes de devolver dados.

## Segurança: o que NÃO está resolvido

O isolamento é válido **somente se o backend controlar a referência, o token e a instância**, sem permitir a execução de código arbitrário no mesmo processo. Python não transforma os atributos internos do objeto em barreiras contra código malicioso que já roda com privilégios de servidor. Não expor `_checkpoint`, `_chaves`, snapshots ou tokens a usuários.

Antes de conectar o site: implantar HTTPS, autenticação de jogador, emissão/rotação/revogação e entrega segura de credenciais, autorização ligada à identidade e ao duelo, proteção contra CSRF e vazamentos de URL/log, rate limit, gestão de segredos e checkpoints, trilha de auditoria, controle transacional de escrita (lease/fencing/CAS), recuperação após reinício e homologação mecânica. Uma implementação de leitura de fixtures não substitui esses componentes.

## Testes

`python -m pip install 'cryptography>=42,<48'`

`PYTHONPATH=src python -m unittest discover -s tests/integration -p test_porta_leitura_fixture.py -v`

Cobertura: público só com contagens, privacidade J1/J2, credenciais desconhecidas e cruzadas, proibição de escalonamento por parâmetro, configuração de tokens, snapshots inválidos, conservação de IDs, PV da criatura ativa e ausência de mutações. Todos os IDs/nomes nos testes são fictícios, sem dados de partidas.

**Próximo incremento:** contrato de serviço autenticado de leitura que delegue a este adaptador e rejeite origens não autorizadas, ainda com fixtures. Somente depois da camada HTTP endurecida conectar a interface e estudar fluxo de partida não sintética.

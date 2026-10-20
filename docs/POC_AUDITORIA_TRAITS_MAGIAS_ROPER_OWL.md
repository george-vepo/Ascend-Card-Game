# Auditoria de Traits espaciais e Spellcasting — Roper × Giant Owl

## Fontes e escopo

Consulta individual das fichas **SRD 5.2.1** do Catálogo SRD externo fixado em `config/catalogo_srd.json`, revisão `03f84e8426f469ef6a0e471faea2093b7c0b69c9`. Fontes originais: Roper, p. 320; Giant Owl, p. 352. Regras do Card Game de 15/10/2026 ratificadas em 19/10/2026: **nenhuma ação depende de posição, movimentação ou alcance espacial**. Sem transmutar comportamentos da ficha em novas regras por suposição.

## Resultado verificável

- **Roper — Spider Climb:** é **Trait**, não Action; permite andar por superfícies e tetos sem teste, efeito exclusivamente espacial. Não existe movimento/escalada para executar nesta POC. Inventário a marca como `SEM_EFEITO_ESPACIAL`, `executavel_como_action=false`, `consome_acao=false`. Não converter em bônus de ataque/CA.
- **Giant Owl — Flyby:** é **Trait**, não Action; evita Opportunity Attack quando a coruja voa para fora do alcance. O jogo não calcula alcance/saída/movimento, portanto esse gatilho não ocorre. Inventário também marca `SEM_EFEITO_ESPACIAL`, sem alterar recursos, condições ou iniciativa.
- **Giant Owl — Spellcasting:** a ficha especifica **Wisdom**, **sem componentes**, `At Will: Detect Evil and Good, Detect Magic`, `1/Day: Clairvoyance`. A auditoria registra os três nomes e as frequências *da fonte*. **Não declara essas magias executáveis**, nem gera detecção, informações ocultas, eventos, gastos, efeitos ou conjuração automática.

## Garantias técnicas

O extrator `src/ascend/habilidades_poc_srd.py` verifica nome, ID/cópia, versão SRD, seção `Traits`, texto exato e ocorrência única do passivo; exige lista e limite da Owl idênticos à fonte. Fichas adulteradas ou novas habilidades falham com `FichaConflitante`.

O motor `prevalidar_habilidades_poc()` é **consulta pura**: exige ambas criaturas ativas, retorna exclusivamente dados públicos das fichas, não consome Action, não modifica estado, recurso, histórico, rolagem, inventário, zona, placar ou hash de evento. O comando legado de `SPIDER_CLIMB_ROPER_TESTE` continua sem resolução mecânica, porque Spider Climb não é uma Action e movimento não existe no Card Game; não cria turno fictício nem concede habilidades novas.

`src/ascend/perfil_combate_srd.py` deixa de afirmar falsamente que Tentacle/Reel/Multiattack não foram integrados na fixture. **Não declara o combate SRD completo.**

## Próximas pendências

A magia `Clairvoyance` envolve um limite de uma utilização por dia; `Detect Magic` e `Detect Evil and Good` exigem análise de seus efeitos, alvos e informação revelada, preservando privacidade. A auditoria de nomes **não autoriza** conjuração, consumo do uso diário nem inferência de raios. A próxima implementação deve consultar o texto **integral** de cada magia e separar efeitos não espaciais daqueles que não são aplicáveis sem posicionamento; se existir lacuna, pedir deliberação ao administrador.

Nenhuma partida oficial foi iniciada; placar 0 × 0. Catálogo externo e sua revisão permanecem inalterados.

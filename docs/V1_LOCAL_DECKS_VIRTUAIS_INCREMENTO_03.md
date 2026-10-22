# V1 Humano × IA — incremento 03: acesso rápido com decks virtuais reais

Dependência: PR #52 → PR #51. Não modificar PR #50; não fazer merges automáticos.

A página de partida local oferece um botão opcional para **preparar**, sem iniciar, dois CSVs: J1 40 cópias de Cat (AT-009) e J2 40 cópias de Owl (AT-010). Cada cópia possui ID único por lado. As criaturas são as entradas canônicas do **Catálogo SRD carregado em tempo real**, não fixtures fictícias nem novos registros de catálogo. Os atributos são confrontados com o subconjunto de combate SRD já validado. Se a origem não coincidir, bloquear.

O botão não sorteia ordem, não embaralha, não compra, não inicia partida, não atribui posse. Apenas preenche a configuração local, exigindo ação posterior explícita em **Iniciar sessão humano × IA**. A interface informa que **cópias virtuais não demonstram posse na coleção**.

Testes verificam CSV UTF-8 com ponto-e-vírgula, 40 cópias únicas, ausência de efeitos colaterais, bloqueio de ficha divergente e início separado somente sob comando. Os dois CSVs também podem continuar sendo importados manualmente.

Limitações: não adiciona deck builder visual, coleção, IA avançada, ataque de outras espécies ou suporte de magias. O sucesso dos testes não substitui o teste real desktop/mobile do fluxo de seleção e início.

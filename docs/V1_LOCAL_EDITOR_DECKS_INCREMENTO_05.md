# Ascend V1-05 — Editor visual de decks (três criaturas com combate suportado)

**Dependência:** PR #54 → #53 → #52 → #51. Não há merge automático e o PR #50 permanece independente.

## O que acrescenta

A página \`local-match.html\` inclui **montagem visual**, separada da importação CSV e dos presets. Cada lado escolhe quantidades inteiras entre 0 e 40 de Cat (AT-009), Owl (AT-010) e Giant Owl (AT-023), até **exatamente 40 cópias por lado**. As três opções vêm do Catálogo SRD publicado e passam pelo mesmo pré-check do módulo de combate parcial.

O compositor \`local-presets.compose(catalog, distribution)\` produz dois CSVs UTF-8 com \`;\` e 80 IDs únicos (prefixos J1-/J2-). Reusa \`decks-core.importDeck\` para validar identidade e duplicação entre decks. Se uma criatura, atributo ou raridade divergir, ou se a quantidade for incorreta, **não gera** arquivos. Os presets anteriores agora reutilizam o mesmo compositor, evitando duas lógicas paralelas.

O botão **Preparar decks escolhidos (sem iniciar)** apenas atribui os CSVs validados aos controles da página; **Iniciar sessão humano × IA** permanece ação distinta e explícita, responsável pela única abertura/embaralhamento. A seleção não altera coleção, zonas, mãos, histórico nem placar.

## Controles visuais

A tela mostra duas colunas, uma para o humano e outra para a IA, três cartões canônicos com nome, tipo, ND, raridade, CA, PV e ilustração verificada quando disponível, além de campo de quantidade e contador \`0/40\` por deck. Desktop usa duas colunas; celular empilha os lados. Erros são exibidos sem importar deck parcial.

## Limitações transparentes

- Só três criaturas já suportadas pelo **subconjunto** SRD. Outros monstros podem ser importados por CSV, mas o combate fica PENDENTE até validação.
- Decks virtuais não comprovam posse de coleção e não simulam boosters.
- A seleção de quantidades não é persistida enquanto é rascunho (a **partida iniciada** utiliza checkpoint local), e a mão do oponente segue oculta apenas na interface.
- A disponibilidade de ilustrações não altera mecânicas.
- Falta validação E2E com navegador visual real e testes em celular.

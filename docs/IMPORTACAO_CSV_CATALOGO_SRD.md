# Importação CSV e Catálogo SRD — incremento web consultivo

A interface estática em \`web/pages/decks.html\` é acessada pela página principal do GitHub Pages. Ela carrega, **somente para leitura**, estes arquivos publicados no projeto independente \`george-vepo/Catalogo-SRD\`:

- \`data/megalista-1320.json\`: identidade, ID canônico, tipo, ND e raridade declarada.
- \`data/fichas-607.json\`: dados mecânicos quando disponíveis, especialmente CA e PV.
- \`data/imagens-607.json\`: URLs de referência já verificadas; imagens ausentes não são substituídas.

**Importante:** 1.320 registros na megalista não são 1.320 criaturas homologadas; importam-se somente entradas com ID canônico. As 607 fichas e as URLs visuais têm coberturas distintas. Uma ficha existente não significa aprovação de todos os seus efeitos.

## Modelo de CSV

Codificação UTF-8, com ou sem BOM; separador recomendado \`;\` (também são aceitos vírgula e tabulação). Cabeçalho:

\`\`\`csv
copia_id;catalogo_id;nome
J1-C01;AT-002;Roper
J1-C02;AT-023;Giant Owl
\`\`\`

O exemplo acima é **ilustrativo e incompleto**: cada arquivo de importação precisa ter exatamente 40 linhas de cópias. O botão de modelo gera 40 posições com \`catalogo_id\` e \`nome\` em branco, para o usuário preencher com cartas reais, sem criar criaturas fictícias.

- \`copia_id\`: identificação da **cópia do jogador**, única dentro de ambos os decks.
- \`catalogo_id\`: ID canônico da **espécie/ficha**, que pode repetir se há múltiplas cópias.
- \`nome\`: opcional, mas, se presente, deve corresponder exatamente (ignorando caixa e acentos) ao ID informado.
- Não aceitar coluna de atributos como fonte de CA, PV, habilidade ou ND.

## Sem promessa de partida oficial

A importação confere sintaxe, quantidade, unicidade e identidade; não comprova que um jogador possui cartas repetidas em sua coleção. O navegador não armazena os CSVs nem cria estado oficial. Ambos os decks podem ser vistos pelo operador desta tela; não abrir ou compartilhar essa visão com um adversário durante partidas privadas. O resultado não alimenta automaticamente o motor de preparação, a mão ou o formulário de combate da demonstração.

A próxima etapa é integrar o adaptador a um motor de zonas e aos contratos de preparação já aprovados, com verificação de coleção e segregação segura de informações antes de habilitar partidas compartilhadas.

## Verificações

- \`node --test tests/web/*.test.cjs\`: parser/identidade, regressão da demonstração e importação.
- CI de Pages: smoke do catálogo publicado com \`ASCEND_CATALOG_NETWORK_TEST=1\`; falha de rede/esquema deve bloquear a integração, em vez de criar fichas fictícias.
- O deploy copia \`decks.html\`, \`decks-core.js\`, \`decks.js\` e \`decks.css\` para o artefato estático.

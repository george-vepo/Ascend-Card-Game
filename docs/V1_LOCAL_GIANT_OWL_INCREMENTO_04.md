# Incremento V1-04 — Giant Owl (AT-023): Talons e dano com dados

**Dependência:** PR #53, que depende de #52 → #51. Sem merge automático.

## Fonte mecânica confirmada

- \`SRD_CC_v5.2.1.pdf\`, **página impressa 352**, bloco *Giant Owl*: Large Celestial, CR 1/4; AC 12, HP 19, iniciativa +2; ataque **Talons +4**, \`1d10 + 2\` Slashing, 7 de dano médio.
- \`Catalogo-SRD/docs/catalogo/data/drive-fichas-srd-20261021/AT-023-giant-owl.json\`: nome, tipo Celestial, ND 1/4, CA/PV, ataque Talons e atributos conferidos no catálogo. Este arquivo contém \`homologacao_administrativa: false\` e pendências sobre magias e suportes; não interpretamos a ficha como homologação geral para o Card Game.
- Cat e Owl seguem com dano fixo 1 conforme SRD, pp. 346 e 358.

## Funcionalidade

- Ampliação **do mesmo motor de combate** \`combat-srd-subset.js\`, sem recriar o motor Python. Autoriza apenas três IDs canônicos \`AT-009\`, \`AT-010\`, \`AT-023\` e campos conferidos com fichas. \`Giant Owl\` aceita ND \`1/4\` ou \`0.25\` como representação numérica equivalente, com classe Comum.
- Novo dano real de **um d10 + 2** quando o ataque Talons acerta. Em 20 natural rola **dois d10 + 2**, nunca duplica o modificador; em erro não rola dados de dano. Registra valores individuais dos dados no evento, modificador, dano bruto, efetivo e KO.
- RNG através do mesmo \`crypto.getRandomValues\` utilizado na V1; injeção de rolagens **simuladas/determinísticas nos testes**, e sorteios locais não auditáveis externamente em operação.
- Nuevo preset **Giant Owl × Cat**, 40 cópias virtuais com IDs distintos por lado; botão somente prepara CSVs, não inicia partida, nem comprova posse. Preset Cat × Owl continua inalterado.
- Persistência local, histórico, zonas, IA, ordem fixa de preparação, KO, PV sobrevivente, reposição de ciclo e vitória aos três pontos continuam os mesmos. Testes específicos de dano com dados e regressão.

## Limitações mecânicas assumidas

- **A única ação disponível da Giant Owl neste recorte é Talons**. Spellcasting (Detect Evil and Good, Detect Magic, Clairvoyance), Flyby e posicionamento não são disponibilizados. O recorte não implica homologação de suporte, reações, magias ou das demais 632+ criaturas.
- As resistências Necrotic/Radiant são registradas a partir da ficha, mas nenhuma das três criaturas habilitadas causa esses tipos; não significa que o motor tenha tratamento completo de dano misto ou efeito mágico.
- **Iniciativa empatada** continua registrada como pendência sem rerrolagem, por falta de decisão específica na POC.
- Não testado no navegador real nem com dados remotos de produção; CI automatizada é gate, não equivalência a homologação de partida real.

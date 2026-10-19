# Divisão entre os repositórios

## Ascend Card Game (este repositório)
- Regras específicas, decisões aprovadas e histórico de propostas com precedência explícita.
- Motor, estado de partida, fluxo de jogadores e interface.
- Testes estruturais, testes de mecânicas isoladas e registro de limitações.
- Sem dados secretos de sessões reais.

## Catálogo SRD (repositório externo)
- Identificadores canônicos, tipos, ND, raridades, fichas e imagens das criaturas.
- Decks Celestial/Aberração como fontes de referência, não como partidas em andamento.
- Pesquisas de fontes, rastreabilidade e site do bestiário.

Repositório externo: https://github.com/george-vepo/Catalogo-SRD

### Contrato de integração proposto (a implementar)
1. Registrar a revisão exata (commit SHA) do catálogo usada na importação.
2. Ler os JSON/CSV publicados pelo catálogo, sem alterá-los.
3. Validar ID canônico/tipo/ND e distinguir ficha homologada de informação em pesquisa.
4. Gerar instâncias de cópias do jogo separadamente; cada cópia tem ID e estado próprio.
5. Nunca gerar atributos, magias, dados, habilidades ou arte por suposição.

### Precedência
O manual específico do duelo e as decisões administrativas posteriores prevalecem onde houver regra própria; SRD 5.2.1 vale para as mecânicas de combate, sem converter propostas em regras. Leia `docs/poc/01_Regras/CONTRATO_DE_REGRAS.md`.

### Limitações da migração
Os arquivos originais do manual PDF e do manual de chats DOCX permanecem na Biblioteca para auditoria; ainda não foram copiados como binários para o GitHub. O código legado é recorte experimental e não resolve todas as fichas.

# Migração inicial — Ascend Card Game × Catálogo SRD

**Origem:** Biblioteca ChatGPT, pasta `/SRD Card Game/POC/`. Os arquivos de regras foram preservados sem reescrever mecânicas.

- Regras e decisões administrativas: `docs/poc/00_Governanca/` e `docs/poc/01_Regras/`.
- Mesa/privacidade: `docs/poc/02_Interface/`.
- Esquema e modelo de partida não iniciada: `docs/poc/04_Estado/`.
- Testes e casos estruturais: `docs/poc/05_Testes/`.
- Código do motor legado: `experimental/legacy/` (não homologado; migrado em etapa separada).
- **Não migrar:** Catálogo ativo Excel, fichas individuais, decks e inventários por criatura, artes, histórico de pesquisas e dados ocultos de partidas.

## Dependências e pendências
- O [Catálogo SRD](https://github.com/george-vepo/Catalogo-SRD) é a fonte de cartas e criaturas, não este repositório.
- O manual de jogo PDF original e o manual de chats DOCX ainda precisam de uma estratégia de cópia fiel como binários; nada foi reconstruído de memória.
- Há regras históricas conflitantes na documentação; a precedência é a do contrato vigente e das decisões mais recentes expressamente aprovadas.
- A integração de dados por adaptador e os testes funcionais completos precisam ser validados antes de uma partida oficial.
- Esta migração é proposta em branch/PR, sem merge automático na main.

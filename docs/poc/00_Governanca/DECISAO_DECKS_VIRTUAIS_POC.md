# Decisão aprovada — cópias virtuais para o piloto

**Status:** APROVADA apenas para a POC humano (J1) vs IA (J2). Nenhuma partida iniciada.

1. Os 40 registros de `/SRD Card Game/Decks/Celestial/` são utilizados como baralho experimental do humano, mantendo exatamente `CE-001` a `CE-040`.
2. Os 40 registros de `/SRD Card Game/Decks/Aberração/` são autorizados como baralho experimental da IA, com novos IDs exclusivos `AB-POC-001` a `AB-POC-040`.
3. A ligação `AB-POC-NNN` → `AB-REF-NNN` é **um para um** e preserva a chave da espécie, nome, ND e classe. A numeração `NNN` conserva apenas a **ordem da lista de referência**; não é ordem de compra/monte.
4. As coleções reais não foram auditadas nem modificadas; o uso da carta aqui não comprova posse fora da POC.
5. Os artefatos de mapeamento são `03_Dados/MAPEAMENTO_COPIAS_AB_POC.json` e `.csv` (UTF-8; separador `;`).
6. Nenhum embaralhamento, distribuição de mão, sorteio, seleção de suporte, invocação ou combate foi realizado. `04_Estado/TEMPLATE_PARTIDA_NAO_INICIADA.json` segue intocado e não é um estado oficial iniciado.
7. Esta autorização **não homologa** fichas incompletas, habilidades candidatas, regras de fase pendentes nem cartas fora dos decks de teste.

**Evento administrativo:** autorização de decks de teste e atribuição de IDs exclusivamente documentais (não consome ação do jogo nem cria evento `E###` de partida).
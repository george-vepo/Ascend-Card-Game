# Gibbering d8 7–8 — ataque corpo a corpo forçado (recorte)

**Fonte:** ficha do Gibbering Mouther no Catálogo SRD, SRD 5.2.1, página 288. Em falha na resistência de SAB CD 10, o resultado **7–8 no d8** obriga a criatura afetada a atacar corpo a corpo uma criatura determinada aleatoriamente dentre as que estão ao seu alcance; se não puder atacar, não age.

## Regras implementadas

A POC possui uma criatura ativa por lado. No confronto restrito `CE-001` (Giant Owl) × `AB-POC-008` (Gibbering Mouther), existe **um único alvo externo** possível: o Mouther. O motor **não deduz posicionamento**: exige o booleano explícito `mouther_ao_alcance_fixture` no evento de início de turno. Sem essa confirmação a jogada fica **PENDENTE** e não altera o estado.

- **Alvo alcançável:** a coruja fica obrigada a resolver `RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE` com o ataque Talons documentado, fornecendo d20 e dados de dano simulados. Não pode atacar voluntariamente ou passar a vez sem resolver o efeito.
- **Sem alvo alcançável:** a coruja não realiza ataque; o comando de passar turno avança a iniciativa, sem dados de ataque.
- **Ação forçada:** rolagem +4 contra CA 9, natural 1 erra, natural 20 é crítico e duplica apenas o dado 1d10, mantendo +2 fixo. Cegueira impõe desvantagem; o efeito é resolvido antes de encerrar o turno do recorte.
- **Integridade:** IDs e CA/PV estão vinculados a hashes das duas fichas SRD externas. O efeito pendente está no checkpoint privado e a exigência de ação fica visível na mesa pública, sem expor mãos.

## Limitações explícitas

A lógica do *alvo único* é aplicável exclusivamente ao confronto isolado de dois combatentes. Não é sorteador de alvos genérico, não cria criatura adicional, não inventa distâncias. A economia completa de ações e ações bônus, movimentos, magias, Flyby, Aberrant Ground e outros elementos SRD continuam parciais.

**Não converter esse resultado em regra nova sobre ataques forçados em outros confrontos.** Os testes são fixtures com dados predeterminados; a partida oficial segue não iniciada, 0 × 0.

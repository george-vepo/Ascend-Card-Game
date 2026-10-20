# Gibbering Mouther — extração SRD e pré-validação de ações

**Estado:** consulta de ficha SRD 5.2.1 real, sem execução de novas habilidades nem alterações na partida. **Fonte:** ficha de `AT-001 / AB-POC-008`, SRD 5.2.1 p. 288, diretamente do **Catálogo SRD externo pinado** pelo manifesto `config/catalogo_srd.json`.

O contrato de 15/10/2026, ratificado em 19/10/2026, elimina qualquer posicionamento, alcance ou movimentação. Números de área/alcance constam como metadados da fonte, **nunca como requisito de geometria**. Ausência de posição não autoriza deduzir automaticamente quais cartas entrariam numa esfera ou como executar movimento aleatório.

## Mecânicas documentadas, sem ação criada

- **Aberrant Ground (Trait):** terreno difícil numa emanação de 10 ft, exclusivamente espacial; `SEM_EFEITO_ESPACIAL`.
- **Gibbering (Trait):** mouther balbucia enquanto não está Incapacitated; salvaguarda **Wisdom CD 10**, disparada no início do turno de criatura sujeita ao efeito; em falha, **1d8** com resultados SRD **1–4** (não faz nada), **5–6** (sem Action/Bonus Action e movimento aleatório), **7–8** (ataque corpo a corpo contra criatura aleatória ou nada). Sem arena, falta a semântica aprovada para o resultado 5–6 e a seleção de alvo em 7–8. **Não executar parcialmente a tabela sem aprovação.**
- **Bite (Action):** `+2` ataque, `2d6` Piercing, alvo Medium ou menor sofre Prone; em KO causado por Bite, ficha descreve absorção do corpo. A zona **cemitério** do Card Game é regra vigente; absorção não pode destruir ID de carta. Pré-validação não integra esses efeitos adicionais; o extrator genérico de Bite é independente desta implementação.
- **Blinding Spittle (Action; Recharge 5–6):** salvaguarda **Dexterity CD 10**, dano **2d6 Radiant**, Blinded até o final do próximo turno do mouther para quem falhar. A ficha especifica esfera de raio 10 ft centrada em ponto até 30 ft. **Não escolher quais criaturas estão na esfera sem regra aprovada para áreas não espaciais.** A recarga também requer recurso e rolagem documentados, nenhum deles consumido por consulta.
- **Imunidade:** condição Prone, verificada literalmente na ficha.

## Artefatos deste incremento

- `src/ascend/gibbering_mouther_srd.py`: extrai cada número e trecho **da ficha real**, exige identidade canônica e texto completo dos efeitos, recusa divergências. Em nenhum momento converte dados em efeitos executáveis.
- `experimental/integration/preflight_gibbering_mouther.py`: consulta **pura** somente quando a cópia correta já ocupa o campo do J2 e sua ficha externa confere com o hash e PV/CA da carta. Resposta pública tem bloqueios explícitos, sem revelar mãos ou monte.
- `tests/integration/test_gibbering_mouther_preflight_real.py`: 16 cenários com fonte externa pinada, integridade e checkpoint.
- `.github/workflows/validate-gibbering-mouther.yml`: executa os cenários contra checkout externo da revisão exata.

## Próxima etapa segura

Avançar pela parte comprovadamente não espacial da ficha (**Bite** contra alvo cujo tamanho já esteja verificado, por exemplo Giant Owl Large, sem Prone adicional) ou propor decisão explícita para os gatilhos `Gibbering` e `Blinding Spittle`. Fugas, ações, iniciativas, d20 e efeitos que não possuem tradução inequívoca permanecem bloqueados. Não converter este registro de pendência em regra aprovada.

**Partida oficial:** não iniciada; placar J1 0 × 0 J2. Nenhuma cópia foi criada, removida ou reproduzida.

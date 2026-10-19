# Extração SRD de testes de resistência e efeitos — recorte v2.4

O motor experimental do Ascend continua limitado a **Giant Owl (CE-001)** e **Gibbering Mouther (AB-POC-008)**. Este incremento remove da rota integrada os bônus e CDs que estavam fixados no código de condições.

A extração de `src/ascend/efeitos_srd.py` depende do texto integral do Catálogo SRD no commit configurado e checa trechos não ambíguos:

- Giant Owl: bônus de salvaguardas **Sabedoria** e **Destreza**.
- Gibbering: CD de Sabedoria, gatilho dentro de 20 pés e dado 1d8 com seus resultados.
- Blinding Spittle: CD de Destreza, esfera de 10 pés de raio, alcance de 30 pés, dano 2d6 Radiante, recarga 5–6 e expiração de Blinded no fim do próximo turno da fonte.

A validação de `perfil_combate_srd.py` e de `fichas_srd.py` continua anterior à resolução: identidade, revisão e hashes verificados. O motor legado `motor_condicoes_srd.py` passa a aceitar um *hook* `_regras_efeitos`; sua implementação padrão mantém os cenários antigos, enquanto **o motor integrado sobrescreve o hook exclusivamente com valores extraídos da fonte**. Textos faltantes, duplicados, tipos de dano não implementados ou expressões malformadas suspendem o evento antes da alteração do estado.

A área ou alcance efetivo da criatura **não é inferido**. O árbitro do teste fornece booleanos de contexto; não há arena/movimento operacional. Dados são explicitamente simulados. Não habilita Flyby, magias, terreno difícil, outros monstros nem combate SRD completo.

As fichas e cartas permanecem somente no Catálogo SRD; o Ascend versiona código e testes sintéticos. **Nenhuma partida oficial foi iniciada, 0 × 0.**

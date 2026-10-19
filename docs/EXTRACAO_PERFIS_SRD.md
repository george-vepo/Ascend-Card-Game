# Extrator de perfis SRD (duelo experimental)

**Motivação:** o motor legado `motor_combate_v23.py` tem `VERIFIED_SRD`, uma tabela fixa dos dois monstros. A integração do Ascend deixa de consultá-la para iniciativa, CA, PV, ataque e resistência do confronto Giant Owl × Gibbering Mouther.

`src/ascend/perfil_combate_srd.py` extrai essas grandezas **exclusivamente do texto integral da ficha obtida no Catálogo SRD**, depois de verificar revisão, identidade e hashes com `consultar_ficha`. O extrator valida uma ocorrência exata de `Initiative`, `AC`, `HP`, `Actions` e a ação corpo a corpo explicitamente reconhecida `Talons` ou `Bite`. Captura bônus, alcance, expressão de dados, modificador e tipo de dano. Confronta o dano médio publicado com a expressão de dados.

Não há valores padrão de atributos mecânicos. Uma divergência, campo ambíguo ou expressão desconhecida produz **PENDENTE** antes da transação ser aceita. A execução do combate não infere novo tipo de dano, alcance, habilidade, rolagem ou posição. O confronto continua exigindo dados simulados externos.

**Limite:** reconhecer dois nomes de ataques não constitui um motor de fichas geral. Flyby, Spellcasting, Aberrant Ground e outros efeitos ainda não são resolvidos por esse extrator. `Immunities Prone` é imunidade de condição, não imunidade de dano.

**Testes:** fixtures sintéticas de parser e regressão com as duas fichas reais através do checkout pinado do Catálogo SRD; nenhum dado real duplicado no repositório Ascend. Partida oficial não iniciada.

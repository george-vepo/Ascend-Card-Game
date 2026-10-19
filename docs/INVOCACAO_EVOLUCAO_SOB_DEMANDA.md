# Motor experimental — invocação e evolução com fichas sob demanda

A camada `experimental/integration/motor_fichas_poc.py` incorpora **consulta estrita de CA/PV à transação de INVOCAR/EVOLUIR** do motor v2.2, sem alterar o motor legado.

- **Fonte exclusiva:** checkout externo pinado do [Catálogo SRD](https://github.com/george-vepo/Catalogo-SRD). Os dois decks fornecem identidades; a ficha integral consultada fornece CA, PV e texto mecânico.
- **Ao entrar em campo:** apenas uma carta Comum na mão pode ser invocada. Após validar a vez/fase/zona, o motor consulta a ficha; se ela passar, registra PV máximos, CA, hash da fonte e status editorial **dentro do evento aceito**. O texto de habilidade não é convertido em execução.
- **Ao evoluir:** somente carta da mão, mesmo tipo e raridade imediatamente superior. A antiga vai ao cemitério, a nova entra com PV máximos da própria ficha verificada. Sem reabastecer a mão.
- **Bloqueios:** ausência de ficha, edição/identidade/CA/PV conflitante ou revisão diferente coloca a ação como PENDENTE; estado e zonas não mudam.
- **Integridade:** 40 cópias por lado e eventos encadeados, com checkpoints privados validados contra os hashes da origem e das fichas individualmente consultadas.
- **Checkout limpo:** não aceita alterações de dados locais mascaradas pelo mesmo SHA de HEAD.
- **Disponibilidade inicial:** `AB-POC-008` Gibbering Mouther, `AB-POC-017` Roper, `AB-POC-031` Aboleth. As demais exigem ficha individual sob demanda. Nenhum suporte é homologado automaticamente.

**Escopo:** fixtures isoladas, com mão e ordem determinísticas para teste, sem sorteio real, sem compra inicial oficial, sem resultados de combate, sem planejamento de IA e sem início de partida oficial. Toda ação cuja ficha esteja pendente não altera o estado da partida.

**Confidencialidade:** checkpoint integral armazena mãos e ordem de monte. NÃO compartilhar checkpoint, trilha com dados privados ou artefatos de execução em repositório público. Use a visão pública e privada com controles de permissão.

Os testes sintéticos criam monstros artificiais claramente identificados apenas em memória temporária; a integração real consulta Roper → Aboleth no Catálogo SRD sem trazer seus JSONs para o Ascend.

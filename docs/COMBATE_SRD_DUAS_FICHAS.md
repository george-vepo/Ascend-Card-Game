# Combate parcial com fichas reais — Giant Owl × Gibbering Mouther

Este módulo integra o **preparo da POC** com os estados e efeitos de combate de um **recorte experimental anterior**, mas agora valida **ambas as fichas diretamente** no Catálogo SRD, no commit fixado.

- J1 **CE-001**, Giant Owl: AC 12, HP 19, Talons +4, 1d10+2 Slashing, resistência Radiante/Necrotic, iniciativa +2.
- J2 **AB-POC-008**, Gibbering Mouther: AC 9, HP 52, Bite +2, 2d6 Piercing; Gibbering CD10, Blinding Spittle recarga 5–6 CD10 2d6 radiante.
- Fontes do mesmo catálogo: `fichas_srd521_giant_owl_1.json` e `fichas_srd521_integral_3.json`, SRD 5.2.1, páginas 352 e 288.

O motor aceita apenas ações explicitamente simuladas, com **alcance/alvo contextual informado separadamente pela fixture**, iniciativa e economia de ações do recorte antigo. Gatilhos de Gibbering e área de Spittle exigem fatos de teste explícitos, sem inventar arena. Dano, defesa, cegueira, vantagem/desvantagem, recarga e duração são auditáveis.

**Limitações relevantes:** o recorte não resolve todos os resultados do Gibbering (d8 7–8), Flyby, magias, terreno difícil, movimento ou outras ações não integradas. Ele **não resolve integralmente um duelo SRD**, nem substitui a validação das 80 criaturas; seu código ainda está em `experimental/`.

A implementação mantém estados e checkpoints privados, evento aceito com dados fornecidos e verificação de hash da ficha. A visão pública não inclui mão ou ordem de montes.

Os testes isolados não alteram o placar oficial, não sorteiam dados, não criam cartas ou imagens e não modificam o Catálogo SRD.

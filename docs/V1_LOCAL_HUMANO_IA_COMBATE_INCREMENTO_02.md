# V1 Humano × IA — incremento 02: combate SRD incremental Cat/Owl

**Escopo de implementação, não aprovação geral de combate.** Este PR depende do incremento 01 (PR #51). Não altera o catálogo de referência nem o PR #50, não inicia partida real, não integra backend.

## Fontes verificadas

- \`SRD_CC_v5.2.1.pdf\`, p. 346: **Cat** (AT-009), CA 12, PV 2, iniciativa +2, Scratch +4, dano fixo 1 cortante; Jumper não tem implicações no duelo sem posicionamento.
- \`SRD_CC_v5.2.1.pdf\`, p. 358: **Owl** (AT-010), CA 11, PV 1, iniciativa +1, Talons +3, dano fixo 1 cortante; Flyby não se aplica sem posicionamento.
- Catálogo: \`Catalogo-SRD/docs/catalogo/data/drive-fichas-srd-20261021/AT-009-cat.json\` e \`AT-010-owl.json\`. Ambos indicam pendências editoriais/administrativas; este recorte usa apenas as ações acima, não libera habilidades adicionais.

## Comportamento implementado

O módulo \`combat-srd-subset.js\` compara ID canônico, nome, tipo, ND, CA, PV e raridade com as duas fichas verificadas antes de processar rolagens. Não é suficiente um campo de CA/PV preenchido manualmente ou o ND da criatura. Ações desconhecidas são **PENDENTE**.

Após concluir \`Sem suporte\` de ambos, o usuário pode rolar iniciativa d20 + modificador. Em caso de empate a operação fica PENDENTE (não foi aprovado um desempate automático para humano × IA); o estado não muda. Em combate disponível há um único ataque identificado por turno; a IA usa exatamente o mesmo validador de rolagens, CA e dano, sem decidir resultados. Críticos 20 acertam, mas **não duplicam dano fixo**, pois não existem dados de dano para rolar duas vezes. 1 natural erra. O RNG local usa \`crypto.getRandomValues\`; sorteios **não auditáveis externamente**, RNG injetado em testes é **determinístico/simulado**.

KO leva somente a carta derrotada para o cemitério, dá exatamente +1 ponto e preserva PV da sobrevivente. Abertura de um novo ciclo (exceto após o terceiro ponto) repõe até cinco para ambos, sem sexto card, não refaz embaralhamento nem a prioridade inicial e mantém a criatura sobrevivente. Terceiro ponto fecha a sessão sem saque seguinte.

## Limitações abertas

- Apenas Cat/Owl. Outras criaturas com Multiattack, magias, condições, reações, resistências, vulnerabilidades, recursos, ações bônus ou efeitos complexos **não são automaticamente liberadas**.
- Não há posicionamento conforme decisão específica da POC; efeitos espaciais bloqueados.
- Empate na iniciativa e exceções competitivas de monte vazio seguem pendentes de política; não inventar desempate ou punições.
- Fichas administrativas ainda sem homologação geral; não interpretar o subconjunto como aprovação de seus suportes.
- Estado local é tecnicamente inspecionável. UI não revela mão da IA, mas não oferece segurança competitiva.
- Testes automatizados não substituem QA visual desktop/mobile e verificações com dados reais do catálogo.

## Próximo incremento

Expandir **somente** a partir de fichas completas e particularidades SRD conferidas, começando pelos casos de Multiattack, condições e resistências disponíveis no motor Python experimental, com testes de ação atômica e efeitos. Rever as pendências de desempate e casos sem Comum antes de ampliar suporte.

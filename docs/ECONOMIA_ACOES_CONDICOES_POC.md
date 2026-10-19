# Economia de ações e duração dos efeitos — SRD parcial

**Escopo:** POC isolada Giant Owl (CE-001) × Gibbering Mouther (AB-POC-008), com fichas lidas no Catálogo SRD, revisão fixada, dados de teste fornecidos externamente. Não é uma partida oficial.

## Resultados 1–4, 5–6 e 7–8 de Gibbering

- **1–4:** a criatura afetada não faz nada no turno. O motor do recorte bloqueia a ação voluntária e oferece somente o comando de encerramento do turno.
- **5–6:** a criatura não pode usar Action nem Bonus Action **e deve gastar todo o movimento em direção aleatória**, conforme a ficha SRD 5.2.1. A POC ainda não tem regra aprovada de movimento/posicionamento, direção aleatória ou arena. **Logo a declaração fica PENDENTE, sem modificar o estado, a vez, os eventos aceitos ou o placar.** Não podemos tratá-la como 1–4 nem passar o turno automaticamente. Exige decisão do administrador antes de implementar a resolução.
- **7–8:** mantém a implementação anterior: ataque corpo a corpo forçado, somente contra adversário confirmado ao alcance, com dados simulados, ou nenhuma ação se não houver alvo elegível.

O bônus de Sabedoria e a CD são consultados das fichas. Um sucesso em Sabedoria não admite um dado d8 de Gibbering excedente: a declaração é rejeitada.

## Consulta pública de opções no turno

\`acoes_disponiveis_teste()\` fornece uma visão **sem efeitos colaterais**, restrita aos comandos aceitos *em princípio* pela economia de ações do recorte. Ela não é uma declaração, não escolhe estratégia, não homologa dados de ataque e não faz rolagens. A mesa pública inclui \`proximas_acoes_fixture\` sem expor mão ou ordem do monte.

- Início de turno pendente → \`INICIO_TURNO_V24_TESTE\`.
- Ataque obrigatório pendente → somente \`RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE\`.
- Incapacidade de agir ou 7–8 sem alvo → somente \`PASSAR_TURNO_V24_TESTE\`.
- Turno normal da Giant Owl → \`ATAQUE_V24_TESTE\`.
- Turno normal do Mouther → \`ATAQUE_V24_TESTE\`, mais \`BLINDING_SPITTLE_V24_TESTE\` apenas quando o recurso está disponível.

Cada comando continua validado individualmente em sua transação; a lista **não** atesta alcance, terreno, recursos de fichas ainda não tratados nem a legalidade final do movimento.

## Recurso e duração

\`Blinding Spittle\` consome sua disponibilidade no uso, inclusive quando o alvo está fora da área. Depois, a recarga (5–6 no d6 simulado) é checada no início do turno do Mouther; se falhar, a ação não reaparece entre as opções. \`Blinded\` fica ativa até o **fim do turno seguinte do Mouther** (fonte da condição) e é removida nesse encerramento; a condição afeta vantagem/desvantagem enquanto vigente. Duração e CD saem das fichas externas consultadas.

## Testes e limites

Adicionados testes de resultados 5–6, de declarações com dados extras, opções de ação, bloqueios, recarga, duração, visibilidade pública e invariantes de 40 cópias. Não há gerador de RNG, IA estratégica, movimentação, arena ou resultado oficial. Tudo roda em CI como **fixture explicitamente simulado**.

Outras criaturas, habilidades e economia completa de ações SRD ainda não estão homologadas. A pista de evolução está em \`experimental/\` e **não deve iniciar partidas reais**.

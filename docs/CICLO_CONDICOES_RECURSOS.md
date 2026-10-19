# Ciclo reutilizável de condições e recursos (POC)

Implementação em \`src/ascend/ciclo_efeitos.py\`, **sem fichas, cartas, IA ou dados de criatura**.

## Regras cobertas no recorte

O código recebe parâmetros explicitamente validados das fichas do Catálogo SRD:

- **Recurso recarregável:** disponível → consumir → indisponível; só rolar recarga se indisponível. A checagem usa as faces do dado e limites fornecidos pela ficha, sem RNG. Dado ausente bloqueia como PENDENTE; valores inválidos ou lançamento indevido são REJEITADOS.
- **Condição temporária:** registra marcador, condição, **ID da cópia fonte** e o turno de fonte no qual expira. Renovar o mesmo marcador da mesma fonte substitui o prazo anterior, sem duplicar a condição.
- **Múltiplas fontes:** ao fim do turno da fonte, somente efeitos vencidos dessa fonte são retirados. Uma condição não desaparece enquanto outro efeito registrado ainda a sustentar.
- **Segurança:** parâmetros inválidos, efeitos desconhecidos ou mapeamentos contraditórios não alteram o estado. Todas as funções retornam estruturas novas, que o motor só instala no estado proposto de sua transação.

A integração inicial cobre **Blinding Spittle → Blinded** da cópia \`AB-POC-008\`: recarga 5–6, origem do efeito, duração até o fim do próximo turno do Mouther e resistência radiante já validadas. Os números e CDs continuam vindo de \`efeitos_srd.py\` após consulta do Catálogo SRD pinado; o mecanismo genérico não os inventa.

O motor legado v2.4 recebeu pontos de extensão para manter seus testes históricos funcionando. O motor integrado do Ascend sobrescreve esses pontos com o ciclo genérico e registra o ID fonte.

**Atenção:** a infraestrutura é reutilizável, mas só um efeito do confronto está habilitado. Não cria nem homologa habilidades, não modela arena ou movimento e não cobre concentração ou economia completa de ações do SRD. Checkpoints contêm informações privadas e não devem ser publicados.

Testes unitários sintéticos e regressão com fichas reais externas; nenhuma partida oficial iniciada.

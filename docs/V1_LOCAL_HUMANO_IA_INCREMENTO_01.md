# Ascend Card Game — V1 humano × IA: incremento 01

## Entregue
- Rota experimental independente \`web/pages/local-match.html\`. Não substitui a demonstração nem o laboratório sintético.
- Importação de dois CSVs de 40 cópias pelo importador existente e Catálogo SRD remoto, sem criar fichas.
- Sessão local com marcador próprio, ordem PRIMEIRO/SEGUNDO sorteada uma única vez e dois montes embaralhados com CSPRNG do navegador; cinco cartas iniciais por lado. Sorteio local **não auditável por terceiros**.
- Integridade das 40 cópias revalidada pelo motor existente de zonas. Fases de troca, invocação, evolução e escolha "Sem suporte" com versão/evento por transição, sem saque posterior imediato.
- IA determinística usa **somente sua própria mão/campo**: troca 0, invoca Comum com CA/PV disponíveis, evolui legalmente se possível, passa preparação e dispensa suporte. Sem Comum válida, informa pendência em vez de inventar derrota.
- Interface responsiva com mão humana, campo das duas criaturas, contagens dos montes/mãos/cemitérios, histórico e retomada via localStorage (schema 1). A mão/ordem do monte da IA não são renderizadas.
- Nenhum fixture é utilizado como carta de produção; testes utilizam marcadores locais isolados.

## Proibido afirmar
Este incremento **não é ainda jogo completo**. A fase COMBATE_PENDENTE para obrigatoriamente antes de iniciativa/ataques. Não resolve poderes de suporte, combate SRD, PV/KO, ciclos seguintes ou vitória a três pontos. Também não verifica posse da coleção, não autentica usuários nem torna inacessível o estado da IA a inspeção técnica local.

## Decisões aplicadas
Contrato \`docs/poc/01_Regras/CONTRATO_DE_REGRAS.md\`, POC v1.5 (ordem de preparação), v1.6 (evoluções sem teto numérico), v1.9 (somente repor na abertura de ciclo posterior) e POC-21 (fichas sob demanda). Sem suporte é escolha válida; nenhuma habilidade não homologada é executada. O início exige ação expressa do usuário no navegador; testes não iniciam uma partida real.

## Próximo incremento
Adaptador para fichas SRD reais e sequência de turnos de combate, com seleção limitada a ataques e ações comprovadamente suportados pelo motor existente. Validar fichas antes da jogada; adicionar iniciativa, rolagem registrada, efeitos, KO, placar e abertura idempotente de novos ciclos por pequenos PRs. Não permitir que a IA atribua vitória.

## Riscos revisados
- Estado local pode ser adulterado pelo dono do dispositivo: não é backend competitivo.
- Checkpoint local conserva cartas ocultas tecnicamente; nunca enviá-las à telemetria ou artefatos públicos.
- Falha do catálogo impede nova partida, mas não deve destruir checkpoint existente.
- A ausência de Comum invocável, CA/PV ou decisão de esgotamento requer tratamento normativo, não derrota presumida.

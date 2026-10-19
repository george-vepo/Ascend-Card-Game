> **POC-21 — DIRETRIZ VIGENTE (17/10/2026): fichas sob demanda.** Confirmada a existência de **80/80 arquivos individuais** de ficha nos decks Celestial/Aberração (40/40 cada, posições 01–40). Não usar ausência de *homologação integral* como bloqueio global da POC; prosseguir com interface, fluxo, estados e testes não mecânicos. Consultar fichas existentes apenas quando necessário. Se faltar realmente ficha ou dado essencial para resolver uma jogada, suspender **somente essa operação**, sem inventar valores. A seleção **Sem suporte** permanece válida. Nenhum embaralhamento foi autorizado. Veja `01_Regras/POC_v2.1_Fichas_Sob_Demanda.md`.

---

> **REGRA VIGENTE POC-20 (17/10/2026): KO por suporte pré-iniciativa encerra imediatamente o combate e dá 1 ponto ao controlador do suporte; o segundo suporte reservado permanece na mão sem consumo (reserva liberada), não há iniciativa e o próximo saque de ambos só ocorre na abertura do próximo ciclo, se não houve o terceiro ponto.** Consulte `01_Regras/POC_v2.0_KO_Pre_Iniciativa.md`. Esta decisão fecha o item de **KO** de Q-13, mas NÃO homologa poderes nem resolve morte simultânea; quaisquer anotações históricas de “KO pré-batalha pendente” estão superadas.


---

# Contrato de componentes de interface da POC

> **REGRA VIGENTE — POC v1.9 (17/10/2026), decisão do administrador.** **Rodada de saque** significa somente a **abertura de um novo ciclo de preparação após o combate anterior acabar com uma criatura a 0 PV**, desde que ninguém tenha alcançado 3 pontos. Nesse instante, **AMBOS os jogadores repõem suas mãos até 5 cartas** a partir do topo de seus montes, conforme disponibilidade. Não há saque no encerramento do KO, ao passar rodadas/turnos do mesmo combate, após invocação, evolução ou suporte, nem saque extra da criatura sobrevivente. Compras iniciais e compras equivalentes aos descartes na fase de troca continuam distintas. **Q-17 resolvida.** Esta regra posterior prevalece sobre as versões v1.7 e v1.8 nos pontos conflitantes.


## CardCriatura

Dados mínimos públicos: `copia_id`, `nome`, `tipo`, `nd`, `classe`, `ca`, `pv_atual`, `pv_max`, `iniciativa`, `condicoes`, `recursos_relevantes`, `arte_ref` (opcional), `fonte_ficha`, `status_ficha`. A arte não define nenhum atributo. Em ausência de ficha validada, impedir uso oficial e exibir justificativa.

## CardMao

Mostrar ao J1 somente `id_copia`, `nome`, `tipo`, `classe`, `nd`, arte quando disponível e selo de `suporte_reservado`. IDs de J2 ocultos; exibir apenas contagem. Não gerar mão por sorteio visual sem registrar o monte oficial.

## SuporteReservado

Estados: `NAO_SELECIONADO`, `SEM_SUPORTE`, `RESERVADO`, `ATIVADO`, `LIBERADO`. `SEM_SUPORTE` é confirmado pelo jogador e referencia `null`, sem bloquear ou movimentar cartas. A reserva é propriedade de **cópia na MÃO**, não uma zona de cartas. Ao reservar, campo `suporteReservadoId` referencia a cópia real. `Ativar suporte` só aparece se proprietário em seu próprio turno e a habilidade está homologada e utilizável.

## BarraDeAcoes

`Trocar`, `Invocar`, `Evoluir`, `Confirmar suporte`, **`Sem suporte`**, `Ativar suporte`, `Atacar`, `Usar habilidade`, `Conjurar magia`, `Encerrar turno`, `Consultar regras`. Botões indisponíveis têm motivo legível; não disparar resolução local desvinculada do árbitro.

## RegistroEvento

Mostrar `evento_id`, `estado_base`, `estado_novo`, `autor`, `acao`, `decisao`, `rolagens` com proveniência, `efeitos`, `movimentacoes_zonas` e `proximo_ator`. Para ação PENDENTE/REJEITADA, `estado_novo` = `estado_base`.

## Interação ChatGPT

Duas responsabilidades: interface envia **declaração estruturada** ao árbitro; árbitro valida e devolve **estado oficial**. Estado visual deve derivar do último snapshot oficial, jamais do clique sozinho. No escopo ChatGPT POC, os controles são protótipos de UI e a validação continua na conversa. A sessão não oferece isolamento técnico real entre árbitro e agente adversário.

## Atualização v1.9

Exibir `Saques do ciclo — J1 / J2` apenas na abertura de **novo ciclo de preparação** pós-KO, quando a partida continua. O comando nunca deve reaparecer em rodadas internas do combate nem no resultado que fechou o terceiro ponto. Não incluir saque extra para a criatura sobrevivente. Os dados privados do deck da IA não devem ser exibidos.

## Exibição POC-20

Painel de histórico: evento `KO_PRE_INICIATIVA`, PV antes/depois, tipo de dano, ponto concedido, `SEGUNDO_SUPORTE_NAO_CONSUMIDO` e próxima fase. **Não renderizar a identidade da carta de suporte IA que não foi ativada**. A cópia continua em `MAO` sem `suporte_reservado`; a contagem não muda.
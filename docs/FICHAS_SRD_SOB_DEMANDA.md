# Fichas SRD sob demanda — etapa 1

A consulta mecânica do Ascend foi ligada ao checkout **externo** do [Catálogo SRD](https://github.com/george-vepo/Catalogo-SRD), na revisão fixada por `config/catalogo_srd.json`. Nenhuma ficha ou arte é versionada no Ascend.

## Recorte implementado

O arquivo fonte de três fichas integrais em `operational/research/decks/aberracao-40-20261014/fichas_srd521_integral_3.json` disponibiliza:

- `AB-POC-008` — Gibbering Mouther: CA 9; PV 52; ficha SRD 5.2.1 de referência
- `AB-POC-017` — Roper: CA 20; PV 93; ficha SRD 5.2.1 de referência
- `AB-POC-031` — Aboleth: CA 17; PV 150; ficha SRD 5.2.1 de referência

O leitor confirma **ID do catálogo, nome, tipo, ND, raridade, edição, CA, PV, atribuição, texto da ficha e revisão da fonte**; mantém o texto de ações e habilidades sem interpretá-lo como comandos de jogo.

**Importante:** a coluna `editorial_review` dessas fichas é `FONTE_INTEGRAL_IDENTIFICADA; AINDA_NAO_TESTADA_EM_ENGINE`. Logo, a consulta de CA/PV e do texto de ações **não equivale à homologação dos efeitos de combate**. `mecanicas_automaticamente_homologadas=False` é constante.

## Demais criaturas

Se uma cópia não constar dessas três, a consulta é `FichaPendente`: não inferir ficha a partir de ND ou de uma criatura homônima, nem consumir suporte, invocar, atribuir dano ou alterar estado em decorrência da consulta. Uma divergência comprovada é `FichaConflitante` e exige revisão.

Conforme a POC v2.1 aprovada, esse estado **bloqueia apenas a operação mecânica dependente da ficha**, não o progresso do restante da implementação e das consultas.

## Próxima etapa

Integrar esse leitor ao comando específico do motor experimental com transação de validação de ficha, sem ativar autoexecução de ataques ou habilidades. Para Celestiais, localizar fonte integral com a mesma rastreabilidade. O manual PDF e outras fichas continuam como fontes na Biblioteca, não reconstruídas no código.

Nenhuma partida oficial, shuffle, compra, sorteio ou alteração de placar nesta entrega.

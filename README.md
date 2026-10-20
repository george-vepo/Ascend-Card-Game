# Ascend Card Game

**Repositório do jogo**, separado do [Catálogo SRD](https://github.com/george-vepo/Catalogo-SRD).

Este projeto mantém as regras aprovadas do duelo, o estado/fluxo de partida, o motor, os testes e a futura interface. **Criaturas, cartas, fichas, atributos e imagens continuam exclusivamente no Catálogo SRD.**

## Documentação

- [Contrato de regras vigente](docs/poc/01_Regras/CONTRATO_DE_REGRAS.md).
- [Regras posteriores — fichas sob demanda](docs/poc/01_Regras/POC_v2.1_Fichas_Sob_Demanda.md), [KO pré-iniciativa](docs/poc/01_Regras/POC_v2.0_KO_Pre_Iniciativa.md), [compras por ciclo](docs/poc/01_Regras/POC_v1.9_Saque_Abertura_Ciclo.md).
- [Decisões aprovadas e pendências](docs/poc/00_Governanca/DECISOES_E_PENDENCIAS.md).
- [Fluxo de telas](docs/poc/02_Interface/FLUXO_DE_TELAS.md) e [estado de jogo](docs/poc/04_Estado/SCHEMA_ESTADO_POC.json).
- [Plano de testes](docs/poc/05_Testes/PLANO_TESTES.md) e [84 cenários estruturais](docs/poc/05_Testes/CASOS_TESTE.json).
- [Política de separação](docs/MIGRACAO.md).
- [Formulário web experimental — resultado de combate externo e PV](docs/INTERFACE_RESULTADO_COMBATE_EXTERNO.md) (servidor local, somente fixture não oficial).
- [GitHub Pages — interface estática com registro local de vencedor e PV](docs/GITHUB_PAGES_RESULTADO_COMBATE.md) (sem backend nem partida oficial).

## Estado

**POC ainda não iniciada:** nenhum embaralhamento, saque, rolagem nem placar de teste representa uma partida oficial. Código experimental transferido posteriormente para `experimental/legacy/` **não constitui motor SRD completo**.

## Catálogo externo

Os dados versionados continuam no repositório [Catálogo SRD](https://github.com/george-vepo/Catalogo-SRD), principalmente em `docs/catalogo/data/` e `operational/research/decks/`. O Ascend deve usá-los via adaptadores, sem copiar os datasets inteiros. Nunca versionar mãos ocultas, ordem de monte ou checkpoints reais.

> As fontes PDF/DOCX originais continuam preservadas na Biblioteca ChatGPT. Esta migração incorpora os documentos de regras em texto disponíveis na POC, sem inventar nem homologar novas regras.

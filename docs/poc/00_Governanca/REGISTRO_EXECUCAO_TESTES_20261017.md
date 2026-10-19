# SRD Card Game POC — Registro de testes estruturais isolados (17/10/2026)

**Escopo:** testes estruturais de regras aprovadas até a POC v2.1. **Isto não é partida oficial nem avaliação de um motor de jogo já implementado.** O conjunto oficial de 84 cenários em `/POC/05_Testes/CASOS_TESTE.json` foi preservado sem alterações dos resultados originais.

## Resultado confirmado

- 84 cenários cadastrados.
- 43 PASSOU_ESTRUTURAL no simulador independente.
- 37 PASSOU_STUB no simulador independente, com resultados de combate/suporte artificialmente injetados, sem dado real ou simulado de combate.
- 0 falhas após correção de um erro interno do próprio script de testes, não das regras.
- 4 NÃO EXECUTADOS:
  - CT-11: sorteio/embaralhamento e saque inicial reais proibidos neste estágio.
  - CT-20: interação espacial concreta exige ação/regra específica.
  - CT-75: resultado de morte simultânea sem regra aprovada.
  - CT-83: a ausência efetiva de ficha não se verifica neste conjunto de 80 arquivos presentes.

## Teste de continuidade

Trilha sintética: 2 resultados de combate por KO injetados, 3 ciclos de preparação, preservação de PV/zonas/placar, compra de ambos somente na abertura do ciclo, prioridade de preparação fixa como dado de teste e iniciativa de combate injetada separadamente. Placar sintético final 1 x 1, sem partida oficial criada. Um snapshot sintético com 80 cópias foi estruturalmente validado pelo schema `04_Estado/SCHEMA_ESTADO_POC.json`.

## Arquivos e reprodução

Todos os arquivos estão salvos em `/SRD Card Game/POC/05_Testes/Execucoes_Isoladas/20261017/`:

- `RELATORIO_TESTES_POC_SIMULADOS.md`
- `RESULTADOS_TESTES_POC_SIMULADOS.json`
- `TRILHA_SIMULADA_2_COMBATES_3_CICLOS.md`
- `TRILHA_SIMULADA_2_COMBATES_3_CICLOS.json`
- `executar_testes_isolados.py`
- `gerar_trace_isolado.py`

Scripts dependem dos dados referenciados em `03_Dados/STATUS_FICHAS_SUPORTES_80.json`, `05_Testes/CASOS_TESTE.json` e `04_Estado/SCHEMA_ESTADO_POC.json`. Requerem adaptações de caminho para outra máquina. Não constituem engine de produção.

**Invariantes mantidas:** nenhuma carta oficial movida; 40 IDs exclusivos por jogador nos cenários, zero rolagens, zero sorteios reais, zero embaralhamentos oficiais, zero compras oficiais e nenhum estado de partida oficial criado.
# Motor experimental migrado — não homologado

Esta pasta contém **arquivos Python originalmente produzidos na POC do ChatGPT**, preservados como material de referência e testes de recorte, não como motor oficial do Ascend.

- `motor_poc.py` / `motor_base_v22.py`: estado de fixture, zonas, comandos e trilhas auditáveis.
- `motor_combate_srd.py` / `motor_combate_v23.py`: ataques simples no cenário Giant Owl × Gibbering Mouther.
- `motor_condicoes_srd.py`: condições e habilidades limitadas.
- `motor_magias_srd.py`: Deva, ações bônus, cura e Multiataque.
- `motor_reacoes_srd.py`: reação de oportunidade em ambiente **espacial experimental**, **não válida** na adaptação atual da POC, que ignora movimentação/posição.
- `motor_concentracao_srd.py`: concentração em uma magia específica.
- `motor_lendarias_srd.py`: Solar × Aboleth e ações lendárias limitadas.
- `orquestrador_srd_v27.py`: despacha perfis isolados, não unifica todas as habilidades em um combate completo.

### Dependências
Os testes históricos podem depender dos JSON de status das 80 cartas da Biblioteca ChatGPT (`STATUS_FICHAS_SUPORTES_80.json`), **não copiados para o Ascend** por pertencerem ao domínio do Catálogo SRD. Até adaptar o carregamento a partir do repositório externo, **não executar nem anunciar como suíte do Ascend** esses testes legados.

**Nunca executar esses recortes para partidas oficiais.** Eles usam rolagens/ações simuladas, podem manter habilidades em código e não implementam todas as regras. Futuras integrações precisam validar mecanicamente cada habilidade contra a ficha completa e o SRD 5.2.1.

Fonte de cartas: https://github.com/george-vepo/Catalogo-SRD

A biblioteca preserva trabalhos posteriores (até v6.3, inclusive supervisão de processos e isolamento operacional), os quais **não foram migrados automaticamente**, por não constituírem o motor de jogo canônico nem uma linha de versões linear.

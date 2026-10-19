# Testes do Ascend

`tests/quality` verifica os limites entre os repositórios, os documentos e o adaptador externo. Não acessa rede nem criaturas reais.

`experimental/legacy/tests` preserva testes da POC antiga. Eles não são executados por este workflow porque dependem de fixtures e dados específicos que pertencem ao **Catálogo SRD**, não migrados ao Ascend. Não interpretar a aprovação dos testes de qualidade como homologação do combate.

Os 84 cenários estruturais originais estão em `docs/poc/05_Testes/CASOS_TESTE.json`, preservados como especificação; seu campo histórico de resultado não é alterado automaticamente.

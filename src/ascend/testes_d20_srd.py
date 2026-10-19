"""Resolução determinística de d20 para testes de atributo SRD 5.2.1.

Somente rolagens fornecidas pelo árbitro (simuladas em fixtures). Sem RNG,
sem seleção de perícia e sem inferência sobre arena ou deslocamento.
"""
from __future__ import annotations
from typing import Any

class TesteD20Invalido(ValueError):
    """Dados explícitos inválidos ou incompatíveis com condições."""


class TesteD20Pendente(ValueError):
    """Aguardando dados adicionais; não realizar a ação."""


def resolver_teste_atributo(
    *,
    condicoes: list[str],
    dados: Any,
    modificador: int,
    cd: int,
) -> dict:
    """Poisoned: desvantagem em ataques e testes de atributo.

    Este componente cobre testes de atributo (fuga via Athletics/Acrobatics).
    Não implementa testes de resistência, que não são afetados por Poisoned.
    """
    if (not isinstance(condicoes, list) or
            not all(isinstance(x, str) and x for x in condicoes) or
            len(condicoes) != len(set(condicoes))):
        raise TesteD20Invalido("lista de condições inválida")
    if (type(modificador) is not int or type(cd) is not int or
            not -30 <= modificador <= 30 or not 1 <= cd <= 35):
        raise TesteD20Invalido("modificador ou CD inválidos")
    if not isinstance(dados, list):
        raise TesteD20Pendente(
            "rolagens d20 externas são obrigatórias para teste de atributo"
        )
    desvantagem = "Poisoned" in condicoes
    quantidade = 2 if desvantagem else 1
    if len(dados) != quantidade:
        raise TesteD20Pendente(
            f"{'Poisoned' if desvantagem else 'Teste normal'} exige "
            f"{quantidade} d20 externo(s)"
        )
    if not all(type(x) is int and 1 <= x <= 20 for x in dados):
        raise TesteD20Invalido("valor d20 inválido (1–20, sem booleanos)")
    aplicado = min(dados) if desvantagem else dados[0]
    total = aplicado + modificador
    return {
        "tipo": "TESTE_ATRIBUTO",
        "modo_rolagem": "DESVANTAGEM" if desvantagem else "NORMAL",
        "d20_simulados": list(dados),
        "d20_aplicado": aplicado,
        "modificador": modificador,
        "total": total,
        "cd": cd,
        "sucesso": total >= cd,
        "dados_simulados": True,
        "fonte_desvantagem": "Poisoned" if desvantagem else None,
    }

"""Ciclo genérico e determinístico de recursos e condições para fixtures SRD.

Não escolhe ações, não rola dados, não pressupõe distâncias. Nenhum dado de
criatura vive aqui: CDs, recargas, fontes e turnos são argumentos explícitos.
As funções são puras e devem ser usadas dentro da transação do motor.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


class CicloInvalido(ValueError):
    """Parâmetros/estado mecânico incompatíveis com o contrato."""


class CicloPendente(CicloInvalido):
    """É necessário um dado ou uma decisão antes de executar a transação."""


def _inteiro_positivo(valor: Any, campo: str, *, zero: bool = False) -> int:
    if type(valor) is not int or (valor < 0 if zero else valor < 1):
        raise CicloInvalido(f"{campo}: inteiro válido obrigatório")
    return valor


def _nome(valor: Any, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise CicloInvalido(f"{campo}: identificação obrigatória")
    return valor.strip()


def consumir_recurso(disponivel: bool) -> bool:
    """Retorna indisponível; nunca consume duas vezes o mesmo recurso."""
    if type(disponivel) is not bool or not disponivel:
        raise CicloInvalido("recurso não está disponível para consumo")
    return False


def verificar_recarga(
    disponivel: bool, dado: int | None, *,
    faces: int, minimo: int, maximo: int,
) -> tuple[bool, dict | None]:
    """Verifica valor EXTERNO de dado; recurso disponível dispensa rolagem."""
    if type(disponivel) is not bool:
        raise CicloInvalido("disponibilidade de recurso inválida")
    _inteiro_positivo(faces, "faces do dado")
    _inteiro_positivo(minimo, "limite mínimo")
    _inteiro_positivo(maximo, "limite máximo")
    if minimo > maximo or maximo > faces:
        raise CicloInvalido("intervalo de recarga inconsistente")
    if disponivel:
        if dado is not None:
            raise CicloInvalido("não rolar recarga com o recurso disponível")
        return True, None
    if dado is None:
        raise CicloPendente("rolagem externa de recarga necessária")
    if type(dado) is not int or not 1 <= dado <= faces:
        raise CicloInvalido("valor do dado de recarga inválido")
    sucesso = minimo <= dado <= maximo
    return sucesso, {
        "dado": dado, "faces": faces, "minimo": minimo,
        "maximo": maximo, "recarregou": sucesso,
        "dados_simulados": True,
    }


def _listas(condicoes: Any, efeitos: Any) -> tuple[list[str], list[dict]]:
    if not isinstance(condicoes, list) or not all(
        isinstance(c, str) and c.strip() for c in condicoes
    ) or len(condicoes) != len(set(condicoes)):
        raise CicloInvalido("lista de condições inconsistente")
    if not isinstance(efeitos, list) or not all(isinstance(e, dict) for e in efeitos):
        raise CicloInvalido("lista de efeitos inconsistente")
    return list(condicoes), deepcopy(efeitos)


def _condicao_de_efeito(efeito: dict, mapeamento: Mapping[str, str]) -> str:
    marcador = _nome(efeito.get("tipo"), "marcador de efeito")
    explicita = efeito.get("condicao")
    if explicita is not None:
        condicao = _nome(explicita, "condição do efeito")
        if marcador in mapeamento and mapeamento[marcador] != condicao:
            raise CicloInvalido("mapeamento de condição contradiz o efeito")
        return condicao
    if marcador not in mapeamento:
        raise CicloPendente("tipo de efeito sem condição mapeada")
    return _nome(mapeamento[marcador], "condição mapeada")


def registrar_condicao(
    condicoes: list[str],
    efeitos: list[dict],
    *,
    marcador: str,
    condicao: str,
    fonte: str,
    expira_no_turno_fonte: int,
    mapeamento: Mapping[str, str],
) -> tuple[list[str], list[dict]]:
    """Ativa ou renova um marcador da mesma fonte sem apagar outros efeitos."""
    marcador = _nome(marcador, "marcador")
    condicao = _nome(condicao, "condição")
    fonte = _nome(fonte, "fonte")
    _inteiro_positivo(expira_no_turno_fonte, "turno de expiração")
    if mapeamento.get(marcador) != condicao:
        raise CicloInvalido("tipo de efeito não autorizado para esta condição")
    conds, ef = _listas(condicoes, efeitos)
    atual = []
    marcadores_iguais = 0
    for e in ef:
        _condicao_de_efeito(e, mapeamento)
        if e.get("tipo") == marcador and e.get("fonte") == fonte:
            marcadores_iguais += 1
        else:
            atual.append(e)
    if marcadores_iguais > 1:
        raise CicloInvalido("mesmo efeito e fonte já estão duplicados")
    atual.append({
        "tipo": marcador,
        "condicao": condicao,
        "fonte": fonte,
        "expira_ao_fim_turno_fonte": expira_no_turno_fonte,
    })
    if condicao not in conds:
        conds.append(condicao)
    return conds, atual


def expirar_efeitos(
    condicoes: list[str],
    efeitos: list[dict],
    *,
    fonte: str,
    turno_fonte: int,
    mapeamento: Mapping[str, str],
) -> tuple[list[str], list[dict], list[str]]:
    """Expira SOMENTE efeitos dessa fonte vencidos ao fim do turno indicado.

    Remove uma condição apenas se nenhuma outra fonte/efeito a sustenta.
    Entrega cópias novas, não altera os objetos recebidos.
    """
    fonte = _nome(fonte, "fonte")
    _inteiro_positivo(turno_fonte, "turno da fonte", zero=True)
    conds, ef = _listas(condicoes, efeitos)
    restantes, removidos = [], []
    for efeito in ef:
        condicao = _condicao_de_efeito(efeito, mapeamento)
        origem = _nome(efeito.get("fonte"), "fonte do efeito")
        expira = _inteiro_positivo(
            efeito.get("expira_ao_fim_turno_fonte"), "turno de expiração"
        )
        if origem == fonte and expira <= turno_fonte:
            removidos.append(condicao)
        else:
            restantes.append(efeito)
    mantidas = {
        _condicao_de_efeito(e, mapeamento) for e in restantes
    }
    expiradas = []
    for nome in dict.fromkeys(removidos):
        if nome not in mantidas:
            if nome not in conds:
                raise CicloInvalido("efeito declara condição não ativa")
            conds.remove(nome)
            expiradas.append(nome)
    return conds, restantes, expiradas

"""Pré-validação exclusivamente consultiva do Gibbering Mouther na fixture.

Nada é resolvido nem modifica estados, mãos, turnos, recursos ou pontuação.
Não converte esfera/alcance do SRD em conjunto de alvos por suposição.
"""
from __future__ import annotations

from ascend.fichas_srd import consultar_ficha, FichaPendente, FichaConflitante
from ascend.gibbering_mouther_srd import extrair_habilidades_gibbering_mouther
from motor_poc import UnresolvedRule


def prevalidar_gibbering_mouther(sessao) -> dict:
    """Consulta pública somente quando a criatura já foi invocada em CAMPO."""
    motor = sessao.motor
    state = motor.state
    result = {
        "estado": "INAPLICAVEL",
        "executavel": False,
        "consome_acao": False,
        "altera_estado": False,
        "carta_id": None,
        "habilidades": None,
        "bloqueios": [],
    }
    if state["jogadores"]["J2"].get("criatura_ativa_id") != "AB-POC-008":
        return result
    card = state["jogadores"]["J2"]["cartas"]["AB-POC-008"]
    if card["zona"] != "CAMPO":
        return result
    try:
        ficha = consultar_ficha(
            motor.checkout_catalogo, motor.contrato, motor.referencias,
            "AB-POC-008", exigir_revisao=motor.exigir_revisao,
        )
        origem = card.get("origem_ficha")
        if (not isinstance(origem, dict)
                or origem.get("sha256_documento") != ficha.sha256_documento
                or origem.get("revisao_git") != ficha.revisao_git
                or card.get("ca_fonte") != ficha.ca
                or card.get("pv_max") != ficha.pv_maximos):
            raise UnresolvedRule("carta de campo divergiu de sua ficha SRD externa")
        inventory = extrair_habilidades_gibbering_mouther(ficha)
    except (FichaPendente, FichaConflitante) as exc:
        raise UnresolvedRule("ficha Gibbering Mouther pendente: " + str(exc)) from exc

    result.update({
        "estado": "FICHA_VERIFICADA_EXECUCAO_PENDENTE",
        "carta_id": "AB-POC-008",
        "habilidades": inventory,
        "bloqueios": [
            "GIBBERING_TABELA_D8_REQUER_SEMANTICA_DE_TURNO_SEM_MOVIMENTO",
            "BLINDING_SPITTLE_REQUER_ALVOS_DE_ESFERA_SEM_ARENA",
            "BITE_REQUER_TRATAR_PRONE_E_KO_ABSORVIDO_NA_ZONA_CEMITERIO",
        ],
    })
    return result

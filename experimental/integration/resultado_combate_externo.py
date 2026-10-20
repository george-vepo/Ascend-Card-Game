"""Registro manual de resultado de combate externo — somente fixture de teste.

O chat/IA conduz a batalha fora do motor; o usuário atesta o vencedor e
PV finais. Este adapter não finge verificar o transcript ou sorteios SRD.
Mantém atomicidade, idempotência, 40 cópias e a regra de KO do motor.
"""
from __future__ import annotations

from motor_poc import InvalidAction, UnresolvedRule, SIDES, other, digest

COMANDO_RESULTADO_EXTERNO = "REGISTRAR_RESULTADO_EXTERNO_TESTE"
ORIGEM_EXTERNA = "CHATGPT_IA_EXTERNA_RESULTADO_MANUAL_NAO_VERIFICADO"
PARAMETROS_PERMITIDOS = frozenset({
    "combate_numero", "vencedor", "pv_restantes_vencedor",
    "versao_base", "hash_estado_base", "origem",
    "confirmacao_usuario",
})


def aplicar_resultado_externo(motor, estado: dict, ator: str,
                             parametros: dict) -> dict:
    """Ação do árbitro por submissão autenticada fora do modelo.
    
    Chamar EXCLUSIVAMENTE de dentro de _transition do motor: apply()
    já duplica o estado antes, valida após e registra a transação.
    """
    if ator != "ARBITRO":
        raise InvalidAction("registro manual requer mediador do backend")
    if estado["situacao"] != "EM_ANDAMENTO" or estado["fase"] != "COMBATE":
        raise InvalidAction("resultado só pode ser registrado em combate ativo")
    if not isinstance(parametros, dict) or set(parametros) != PARAMETROS_PERMITIDOS:
        raise InvalidAction("campos do resultado externo inválidos")
    if parametros["origem"] != ORIGEM_EXTERNA:
        raise InvalidAction("origem não corresponde a resultado declarado")
    if parametros["confirmacao_usuario"] is not True:
        raise InvalidAction("exige confirmação explícita de quem registrou")
    if (type(parametros["combate_numero"]) is not int
            or parametros["combate_numero"] != estado["combate"]["numero"]):
        raise InvalidAction("resultado se refere a outro combate")
    if parametros["versao_base"] != estado["versao"]:
        raise InvalidAction("estado mudou desde a visualização do formulário")
    if parametros["hash_estado_base"] != digest(estado):
        raise InvalidAction("hash do estado foi alterado desde a visualização")
    vencedor = parametros["vencedor"]
    if vencedor not in SIDES:
        raise InvalidAction("vencedor precisa ser J1 ou J2")
    perdedor = other(vencedor)
    campo_vencedor = estado["jogadores"][vencedor]["criatura_ativa_id"]
    campo_perdedor = estado["jogadores"][perdedor]["criatura_ativa_id"]
    if not campo_vencedor or not campo_perdedor:
        raise InvalidAction("ambos os campos devem ter criatura ativa")
    carta_vencedora = motor.get_card(estado, vencedor, campo_vencedor)
    carta_perdedora = motor.get_card(estado, perdedor, campo_perdedor)
    if (carta_vencedora["zona"] != "CAMPO"
            or carta_perdedora["zona"] != "CAMPO"
            or not isinstance(carta_vencedora["pv_max"], int)
            or type(carta_vencedora["pv_atual"]) is not int
            or carta_vencedora["pv_atual"] <= 0
            or type(carta_perdedora["pv_atual"]) is not int
            or carta_perdedora["pv_atual"] <= 0):
        raise UnresolvedRule("campos ou PV de origem não conferem com a ficha")
    pv = parametros["pv_restantes_vencedor"]
    if type(pv) is not int or not 1 <= pv <= carta_vencedora["pv_max"]:
        raise InvalidAction("PV do vencedor devem ser de 1 até o PV máximo da ficha")
    # O combate externo pode ter cura. Não deduzir ou autorizar uma
    # habilidade de cura: o dado é declaração humana, NÃO resolução SRD.
    previa = carta_vencedora["pv_atual"]
    carta_vencedora["pv_atual"] = pv
    limpeza = motor._ko(estado, vencedor, ORIGEM_EXTERNA)
    resultado = {
        "registro": "RESULTADO_EXTERNO_MANUAL_NAO_VERIFICADO",
        "combate_numero": parametros["combate_numero"],
        "vencedor": vencedor,
        "derrotado": perdedor,
        "carta_vencedora_id": campo_vencedor,
        "carta_derrotada_id": campo_perdedor,
        "pv_vencedor_anterior": previa,
        "pv_vencedor_final": pv,
        "pv_derrotado_final": 0,
        "pv_max_vencedor": carta_vencedora["pv_max"],
        "aviso": ("resultado informado pelo usuário; golpes, dados e cura "
                  "não foram verificados pelo motor"),
        "placar": estado["placar"].copy(),
        "fase_seguinte": estado["fase"],
        "partida_encerrada": estado["situacao"] == "ENCERRADA",
    }
    if isinstance(limpeza, dict):
        resultado["limpeza_de_efeitos"] = limpeza
    # Dados de exibição públicos; não inclui cartas em mão, monte nem RNG.
    estado["combate"]["ultimo_resultado_manual_publico"] = resultado.copy()
    return resultado

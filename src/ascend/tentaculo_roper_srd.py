"""Parâmetros do Tentacle/Roper extraídos da ficha SRD 5.2.1 verificada.

Não transforma Multiattack, Reel, fuga do agarrão nem dano em tentáculos
em ações executáveis. Nenhum valor de combate é deduzido de ND.
"""
from __future__ import annotations
import re
from ascend.fichas_srd import FichaConsultada, FichaConflitante


def extrair_tentaculo_roper(ficha: FichaConsultada) -> dict:
    if ficha.id_copia != "AB-POC-017" or ficha.nome != "Roper":
        raise FichaConflitante("extrator exclusivo da ficha verificada do Roper")
    if ficha.versao != "SRD 5.2.1":
        raise FichaConflitante("versão SRD não aceita")
    if ficha.ficha_integral.count("\nActions\n") != 1:
        raise FichaConflitante("Actions da ficha Roper ausente ou duplicada")
    actions = " ".join(ficha.ficha_integral.split("\nActions\n", 1)[1].split())
    pattern = (
        r"\bTentacle\.\s+Melee Attack Roll:\s*([+−-]?\d+),\s*"
        r"reach\s+(\d+)\s+ft\.\s+Hit:\s+The target has the Grappled "
        r"condition\s+\(escape DC\s+(\d+)\)\s+from one of\s+(\w+)\s+tentacles,"
        r"\s+and the target has the Poisoned condition until the grapple ends\."
        r"\s+The tentacle can be damaged, freeing a creature it has "
        r"Grappled when destroyed\s+\(AC\s+(\d+),\s+HP\s+(\d+),"
        r"\s+Immunity to Poison and Psychic damage\)\."
        r"\s+Damaging the tentacle deals no damage to the roper,"
        r"\s+and a destroyed tentacle regrows at the start of the roper’s next turn\."
    )
    found = list(re.finditer(pattern, actions))
    if len(found) != 1:
        raise FichaConflitante(
            "Tentacle: trecho mecânico ausente, ambíguo ou divergente"
        )
    m=found[0]
    if m.group(4) != "six":
        raise FichaConflitante("quantidade de tentáculos não reconhecida")
    reel = list(re.finditer(
        r"\bReel\.\s+The roper pulls each creature Grappled by it "
        r"up to\s+(\d+)\s+feet straight toward it\.", actions
    ))
    if len(reel) != 1:
        raise FichaConflitante("Reel: texto e deslocamento não verificáveis")
    number = lambda txt: int(txt.replace("−", "-"))
    bonus, reach, escape_dc, slots, ac, hp, pull = (
        number(m.group(1)), int(m.group(2)), int(m.group(3)),
        6, int(m.group(5)), int(m.group(6)), int(reel[0].group(1)),
    )
    if not (-30<=bonus<=30 and 1<=reach<=1000 and
            1<=escape_dc<=35 and ac>0 and hp>0 and 1<=pull<=1000):
        raise FichaConflitante("parâmetro Tentacle/Reel fora dos limites")
    return {
        "nome":"Tentacle","bonus_ataque":bonus,"alcance_ft":reach,
        "escape_dc":escape_dc,"quantidade_tentaculos":slots,
        "condicoes_no_acerto":["Grappled","Poisoned"],
        "tentaculo":{"ca":ac,"pv":hp,"imunidades_dano":["Poison","Psychic"]},
        "reel":{"distancia_maxima_ft":pull,"movimento_homologado":False},
        "sha256_documento":ficha.sha256_documento,
        "origem_ficha":ficha.id_catalogo,
    }

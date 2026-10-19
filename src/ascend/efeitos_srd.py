"""Extrai CDs, salvaguardas e parâmetros de efeitos das duas fichas SRD.

Escopo propositalmente pequeno (Giant Owl e Gibbering Mouther).
Cada campo deve ter exatamente uma origem textual verificável; na falta
de fonte ou diante de formatação ambígua, suspende a ação mecânica.
Não interpreta efeitos para outras criaturas nem homologa fichas inteiras.
"""
from __future__ import annotations

import re
from ascend.fichas_srd import FichaConsultada, FichaConflitante


def _unico(padrao: str, texto: str, campo: str):
    achados = list(re.finditer(padrao, texto, re.DOTALL))
    if len(achados) != 1:
        raise FichaConflitante(f"{campo}: esperado trecho SRD único; encontrados {len(achados)}")
    return achados[0]


def _bonus(valor: str) -> int:
    return int(valor.replace("−", "-"))


def _limite(valor: int, label: str, minimo: int = 1, maximo: int = 100) -> int:
    if not minimo <= valor <= maximo:
        raise FichaConflitante(f"{label} fora do intervalo suportado")
    return valor


def extrair_salvaguardas_celestial(ficha: FichaConsultada) -> dict:
    if ficha.id_copia != "CE-001" or ficha.nome != "Giant Owl":
        raise FichaConflitante("salvaguardas não suportadas para esta criatura")
    # Texto SRD 5.2.1: "Dex 15 +2 +2; ... Wis 14 +2 +4"
    body = ficha.ficha_integral
    result = {}
    for name, key in (("Dex", "dex_bonus"), ("Wis", "wis_bonus")):
        found = _unico(
            rf"\b{name}\s+\d+\s+[+−-]?\d+\s+([+−-]?\d+)\b",
            body, f"salvaguarda {name}",
        )
        result[key] = _bonus(found.group(1))
        _limite(abs(result[key]), f"salvaguarda {name}", 0, 30)
    return result


def extrair_efeitos_gibbering(ficha: FichaConsultada) -> dict:
    if ficha.id_copia != "AB-POC-008" or ficha.nome != "Gibbering Mouther":
        raise FichaConflitante("efeitos não suportados para esta criatura")
    text = ficha.ficha_integral
    if text.count("\nActions\n") != 1:
        raise FichaConflitante("separação de Actions não verificável")
    traits, actions = text.split("\nActions\n", 1)
    if traits.count("Gibbering.") != 1 or actions.count("Blinding Spittle (Recharge") != 1:
        raise FichaConflitante("nomes dos efeitos ausentes ou duplicados")

    area_gibbering = " ".join(traits.split("Gibbering.", 1)[1].split())
    gib = _unico(
        r"^.*?Wisdom Saving Throw:\s*DC\s+(\d+),\s*any creature that starts its turn "
        r"within\s+(\d+)\s+feet\s+of the mouther.*?"
        r"Failure:\s*The target rolls\s+1d(\d+)\s+to determine what it does",
        area_gibbering, "Gibbering",
    )
    # Não confundir 1–4/5–6/7–8 com a recarga do outro efeito.
    if not all(x in area_gibbering for x in (
        "1–4.", "5–6.", "7–8.", "randomly determined creature within",
    )):
        raise FichaConflitante("faixas d8 do Gibbering incompletas")
    cd_gib = _limite(int(gib.group(1)), "CD Gibbering", 1, 35)
    range_gib = _limite(int(gib.group(2)), "alcance Gibbering", 1, 500)
    faces_gib = _limite(int(gib.group(3)), "dado Gibbering", 2, 100)
    if faces_gib != 8:
        raise FichaConflitante("faixas 1–4/5–6/7–8 incompatíveis com dado")

    text_actions = " ".join(actions.split())
    spit = _unico(
        r"Blinding Spittle\s+\(Recharge\s+(\d+)[–-](\d+)\)\.\s+"
        r"Dexterity Saving Throw:\s*DC\s+(\d+),\s+each creature in a "
        r"(\d+)-foot-radius Sphere centered on a point within\s+(\d+)\s+feet\.\s+"
        r"Failure:\s*(\d+)\s+\((\d+)d(\d+)\)\s+([A-Za-z]+)\s+damage,\s+"
        r"and the target has the Blinded condition until the end of the mouther’s next turn\.",
        text_actions, "Blinding Spittle",
    )
    recharge_min, recharge_max, dc, radius, reach, average, n, faces = (
        int(spit.group(i)) for i in range(1, 9)
    )
    dtype = spit.group(9)
    for val, label, mx in (
        (recharge_min, "recarga min", 6), (recharge_max, "recarga max", 6),
        (dc, "CD Blinding Spittle", 35), (radius, "raio Spittle", 200),
        (reach, "alcance Spittle", 1000), (average, "média Spittle", 500),
        (n, "quantidade dados Spittle", 20), (faces, "faces dado Spittle", 100),
    ):
        _limite(val, label, 1, mx)
    if (recharge_max < recharge_min or
            (n * (faces + 1) // 2) != average):
        raise FichaConflitante("recarga ou expressão/média de dano inconsistente")
    # Somente a habilidade Radiante já parcialmente implementada é admitida.
    if dtype != "Radiant":
        raise FichaConflitante("tipo de dano especial não implementado")
    return {
        "gibbering": {
            "dc": cd_gib, "range_ft": range_gib,
            "d8_faces": faces_gib,
        },
        "spittle": {
            "dc": dc, "radius_ft": radius, "range_ft": reach,
            "damage_dice": (n, faces), "damage_type": dtype,
            "recharge_min": recharge_min, "recharge_max": recharge_max,
            "blinded_termina_no_proximo_turno_fonte": True,
        },
    }

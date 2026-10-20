"""Inventário mecânico estrito do Gibbering Mouther a partir da ficha SRD 5.2.1.

Este módulo NÃO executa combate, sorteia dados, escolhe alvos ou modifica o
estado oficial. O contrato do Card Game não prevê arena/posição/distâncias.
"""
from __future__ import annotations

import re
from ascend.fichas_srd import FichaConsultada, FichaConflitante


def _unico(texto: str, padrao: str, nome: str, flags: int = 0):
    matches = list(re.finditer(padrao, texto, flags))
    if len(matches) != 1:
        raise FichaConflitante(
            f"{nome}: esperado um único trecho SRD íntegro, encontrados {len(matches)}"
        )
    return matches[0]


def extrair_habilidades_gibbering_mouther(ficha: FichaConsultada) -> dict:
    """Extrai sem homologar efeitos incompatíveis com a ausência de posição."""
    if (ficha.id_copia != "AB-POC-008"
            or ficha.id_catalogo != "AT-001"
            or ficha.nome != "Gibbering Mouther"
            or ficha.versao != "SRD 5.2.1"):
        raise FichaConflitante("extrator reservado ao Gibbering Mouther verificado")
    corpo = ficha.ficha_integral
    if corpo.count("\nTraits\n") != 1 or corpo.count("\nActions\n") != 1:
        raise FichaConflitante("seções Traits e Actions ausentes ou duplicadas")
    traits = " ".join(corpo.split("\nTraits\n", 1)[1].split("\nActions\n", 1)[0].split())
    actions = " ".join(corpo.split("\nActions\n", 1)[1].split())
    _unico(corpo, r"^Immunities\s+Prone\s*$",
           "imunidade à condição Prone", re.MULTILINE)

    aberrant = _unico(
        traits,
        r"\bAberrant Ground\. The ground in a (\d+)-foot Emanation "
        r"originating from the mouther is Difficult Terrain\.",
        "Aberrant Ground",
    )
    gibber = _unico(
        traits,
        r"\bGibbering\. The mouther babbles incoherently while it doesn’t "
        r"have the Incapacitated condition\. Wisdom Saving Throw: DC (\d+), "
        r"any creature that starts its turn within (\d+) feet of the mouther "
        r"while it is babbling\. Failure: The target rolls (\d+)d(\d+) "
        r"to determine what it does during the current turn: "
        r"1–4\. The target does nothing\. "
        r"5–6\. The target takes no action or Bonus Action and uses all its "
        r"movement to move in a random direction\. "
        r"7–8\. The target makes a melee attack against a randomly "
        r"determined creature within its reach or does nothing if it can’t "
        r"make such an attack\.",
        "Gibbering",
    )
    if traits != (aberrant.group(0) + " " + gibber.group(0)):
        raise FichaConflitante("Traits extras ou ordem divergente da ficha fonte")

    bite = _unico(
        actions,
        r"\bBite\. Melee Attack Roll: ([+−-]?\d+), reach (\d+) ft\. "
        r"Hit: (\d+) \((\d+)d(\d+)\) Piercing damage\. "
        r"If the target is a Medium or smaller creature, it has the Prone "
        r"condition\. The target dies if it is reduced to 0 Hit Points by "
        r"this attack\. Its body is then absorbed into the mouther, "
        r"leaving only equipment behind\.",
        "Bite",
    )
    spittle = _unico(
        actions,
        r"\bBlinding Spittle \(Recharge (\d+)–(\d+)\)\. "
        r"Dexterity Saving Throw: DC (\d+), each creature in a "
        r"(\d+)-foot-radius Sphere centered on a point within (\d+) feet\. "
        r"Failure: (\d+) \((\d+)d(\d+)\) Radiant damage, and the target "
        r"has the Blinded condition until the end of the mouther’s next turn\.",
        "Blinding Spittle",
    )
    gib_dc, gib_reach, n_dice, faces = map(int, gibber.groups())
    b_bonus = int(bite.group(1).replace("−", "-"))
    b_reach, b_mean, b_n, b_faces = map(int, bite.groups()[1:])
    recharge_lo, recharge_hi, spell_dc, radius, range_ft, damage_avg, dmg_n, dmg_faces = (
        map(int, spittle.groups())
    )
    # Os valores são lidos acima do texto SRD, mas sua identidade canônica
    # é fixada nesta integração: mudanças exigem revisão, nunca fallback.
    if not ((gib_dc, gib_reach, n_dice, faces) == (10, 20, 1, 8)
            and (b_bonus, b_reach, b_mean, b_n, b_faces) == (2, 5, 7, 2, 6)
            and (recharge_lo, recharge_hi, spell_dc, radius, range_ft,
                 damage_avg, dmg_n, dmg_faces) == (5, 6, 10, 10, 30, 7, 2, 6)):
        raise FichaConflitante("números incompatíveis com o texto SRD verificado")
    return {
        "carta_id": ficha.id_copia,
        "id_catalogo": ficha.id_catalogo,
        "origem_ficha_sha256": ficha.sha256_documento,
        "versao": ficha.versao,
        "imunidade_condicao": ["Prone"],
        "passivas": [
            {
                "nome": "Aberrant Ground", "emanacao_ft_fonte": int(aberrant.group(1)),
                "estado_poc": "SEM_EFEITO_ESPACIAL",
                "motivo": "NAO_HA_TERRENO_OU_DESLOCAMENTO",
                "executavel": False,
            },
            {
                "nome": "Gibbering", "salvaguarda": "Wisdom",
                "cd": gib_dc, "gatilho_turno_inicial": True,
                "alcance_ft_metadado": gib_reach,
                "dado_efeito": [n_dice, faces],
                "tabela_fonte": [
                    {"faces": [1, 2, 3, 4], "resultado": "NAO_FAZ_NADA"},
                    {"faces": [5, 6], "resultado": "SEM_ACTION_BONUS_E_MOVIMENTO_ALEATORIO"},
                    {"faces": [7, 8], "resultado": "ATAQUE_CORPO_A_CORPO_ALEATORIO_OU_NADA"},
                ],
                "estado_poc": "PENDENTE_SEMANTICA_DE_TURNO",
                "executavel": False,
            },
        ],
        "acoes": [
            {
                "nome": "Bite", "bonus_ataque": b_bonus,
                "alcance_ft_metadado": b_reach,
                "dano": {"dados": [b_n, b_faces], "media_fonte": b_mean,
                         "tipo": "Piercing"},
                "prone_se_alvo_medium_ou_menor": True,
                "absorve_corpo_em_ko": True,
                "estado_poc": "PENDENTE_EFEITOS_CONDICIONAIS",
                "executavel": False,
            },
            {
                "nome": "Blinding Spittle",
                "recarga_d6": [recharge_lo, recharge_hi],
                "salvaguarda": "Dexterity", "cd": spell_dc,
                "area_raio_ft_metadado": radius,
                "alcance_ft_metadado": range_ft,
                "dano_falha": {"dados": [dmg_n, dmg_faces],
                               "media_fonte": damage_avg,
                               "tipo": "Radiant"},
                "condicao_falha": "Blinded",
                "duracao": "ATE_FIM_PROXIMO_TURNO_MOUTHER",
                "estado_poc": "PENDENTE_ALVOS_DA_AREA_SEM_POSICIONAMENTO",
                "executavel": False,
            },
        ],
        "mecanicas_integralmente_executaveis": False,
        "consultavel_sem_mutacao": True,
        "regra_poc": "SEM_POSICIONAMENTO_15_10_2026",
    }

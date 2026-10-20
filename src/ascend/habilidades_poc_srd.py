"""Auditoria estrita de Traits espaciais e Spellcasting de fichas SRD pinadas.

Somente interpreta o que está escrito nas fichas verificadas.
O Card Game (regra de 15/10/2026) não executa movimento, alcance ou posição.
Esta consulta NÃO conjura magias, consome Action, aplica condição ou usa recursos.
"""
from __future__ import annotations

import re
from ascend.fichas_srd import FichaConsultada, FichaConflitante


_TRAITS_FONTE = {
    "AB-POC-017": (
        "Roper",
        "Spider Climb",
        "The roper can climb difficult surfaces, including along ceilings, "
        "without needing to make an ability check.",
    ),
    "CE-001": (
        "Giant Owl",
        "Flyby",
        "The owl doesn't provoke an Opportunity Attack when it flies out "
        "of an enemy's reach.",
    ),
}

_MAGIAS_OWL = {
    "At Will": ["Detect Evil and Good", "Detect Magic"],
    "1/Day": ["Clairvoyance"],
}


def _trecho_unico(texto: str, padrao: str, etiqueta: str, flags: int = 0):
    hits = list(re.finditer(padrao, texto, flags))
    if len(hits) != 1:
        raise FichaConflitante(
            f"{etiqueta}: esperado um único trecho exato na ficha, obtidos {len(hits)}"
        )
    return hits[0]


def extrair_habilidades_poc_srd(ficha: FichaConsultada) -> dict:
    """Faz apenas inventário auditável, sem liberar jogada ou efeito mecânico.

    O resultado não substitui a ficha integral, nem declara habilidades
    homologadas para execução. Recusa versões e conteúdo divergente.
    """
    expected = _TRAITS_FONTE.get(ficha.id_copia)
    if (expected is None or ficha.nome != expected[0]
            or ficha.versao != "SRD 5.2.1"
            or ficha.id_catalogo != (
                "AT-002" if ficha.id_copia == "AB-POC-017" else "AT-023"
            )):
        raise FichaConflitante("inventário restrito a Roper e Giant Owl verificados")
    corpo = ficha.ficha_integral
    _trecho_unico(corpo, r"^Traits\s*$", "seção Traits", re.MULTILINE)
    _trecho_unico(corpo, r"^Actions\s*$", "seção Actions", re.MULTILINE)
    traits = corpo.split("\nTraits\n", 1)[1].split("\nActions\n", 1)[0]
    actions = corpo.split("\nActions\n", 1)[1]

    nome, habilidade = expected[1], expected[2]
    frase = nome + ". " + habilidade
    _trecho_unico(traits, re.escape(frase), nome)
    # Não aceitar duplicação da habilidade fora da seção Traits.
    _trecho_unico(corpo, re.escape(frase), "identidade " + nome)
    if nome == "Spider Climb" and "Flyby." in traits:
        raise FichaConflitante("Trait da criatura incorreta na ficha Roper")
    if nome == "Flyby" and "Spider Climb." in traits:
        raise FichaConflitante("Trait da criatura incorreta na ficha Giant Owl")

    result = {
        "carta_id": ficha.id_copia,
        "nome": ficha.nome,
        "origem_ficha_sha256": ficha.sha256_documento,
        "versao": ficha.versao,
        "passiva": {
            "nome": nome,
            "categoria_srd": "Trait",
            "aplicabilidade_card_game": "SEM_EFEITO_ESPACIAL",
            "motivo": "MOVIMENTO_OU_ALCANCE_ESPACIAL_NAO_EXISTEM_NA_POC",
            "executavel_como_action": False,
            "consome_acao": False,
            "altera_estado": False,
        },
        "conjuracao": None,
    }

    if ficha.id_copia == "AB-POC-017":
        if re.search(r"^Spellcasting\.", actions, re.MULTILINE):
            raise FichaConflitante("Spellcasting inesperada na ficha Roper")
        return result

    # Fonte Giant Owl: feitiços somente identificados; efeitos não homologados.
    header = (
        "Spellcasting. The owl casts one of the following spells, requiring "
        "no spell components and using Wisdom as the spellcasting ability:"
    )
    _trecho_unico(actions, re.escape(header), "Spellcasting Giant Owl")
    _trecho_unico(actions, r"^Spellcasting\.", "Spellcasting única", re.MULTILINE)
    l1 = _trecho_unico(actions, r"^At Will:\s*([^\r\n]+)$",
                       "magias At Will", re.MULTILINE)
    l2 = _trecho_unico(actions, r"^1/Day:\s*([^\r\n]+)$",
                       "magia 1/Day", re.MULTILINE)
    list_at_will = [x.strip() for x in l1.group(1).split(",")]
    list_daily = [x.strip() for x in l2.group(1).split(",")]
    if (list_at_will != _MAGIAS_OWL["At Will"]
            or list_daily != _MAGIAS_OWL["1/Day"]):
        raise FichaConflitante("lista ou limite de magias da Owl divergente")
    result["conjuracao"] = {
        "categoria_srd": "Action/Spellcasting",
        "atributo": "Wisdom",
        "componentes": "nenhum",
        "magias": [
            {"nome": nome, "frequencia_srd": frequencia,
             "limite_fonte_por_dia": None if frequencia == "At Will" else 1,
             "efeito_integrado": False}
            for frequencia, nomes in (
                ("At Will", list_at_will), ("1/Day", list_daily)
            )
            for nome in nomes
        ],
        "executavel_na_poc": False,
        "consome_acao": False,
        "usa_recurso": False,
        "motivo": "EFEITOS_E_ALVOS_DAS_MAGIAS_AINDA_NAO_INTEGRADOS",
    }
    return result

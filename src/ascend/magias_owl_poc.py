"""Magias de detecção da Giant Owl: projeções exclusivamente do campo público.

Base mecânica: SRD 5.2.1, pp. 115, 123 e 179. Tradução de alcance
para campo público sem coordenadas é HOMEbrew administrativo (issue #30).
Não pesquisa, itera ou projeta mão, monte ou informações privadas.
"""
from __future__ import annotations

import re
from ascend.fichas_srd import FichaConsultada, FichaConflitante

DETECCOES_OWL = ("Detect Evil and Good", "Detect Magic")
CATEGORIAS_DETECT_EVIL_GOOD = (
    "Aberration", "Celestial", "Elemental", "Fey", "Fiend", "Undead"
)
# Somente as identidades SRD explicitamente verificadas nesta fixture.
TIPO_POR_ID = {"CE-001": "Celestial", "AB-POC-017": "Aberration"}
REGRA_APROVADA = "OWL_DETECCAO_CAMPO_PUBLICO_SEM_POSICAO_20261019"
DURACAO_CONCENTRACAO_RODADAS = 100  # 10 min / 6 s por rodada.


def bonus_salvaguarda_constituicao_owl(ficha: FichaConsultada) -> int:
    """Extrai a salvaguarda de Constituição da ficha pinada, nunca estima por ND."""
    if (ficha.id_copia != "CE-001" or ficha.id_catalogo != "AT-023"
            or ficha.nome != "Giant Owl" or ficha.versao != "SRD 5.2.1"):
        raise FichaConflitante("salvaguarda somente para Giant Owl SRD 5.2.1")
    achados = list(re.finditer(
        r"\bCon\s+(\d+)\s+([+−-]?\d+)\s+([+−-]?\d+)\b",
        ficha.ficha_integral,
    ))
    if len(achados) != 1:
        raise FichaConflitante("Constitution save ambígua ou ausente")
    escore, mod, save = achados[0].groups()
    mod, save = int(mod.replace("−", "-")), int(save.replace("−", "-"))
    if int(escore) != 12 or mod != 1 or save != 1:
        raise FichaConflitante("atributos de Constituição divergiram da ficha")
    return save


def detectar_publico(estado: dict, magia: str) -> dict:
    """Leitura estrita de criatura(s) CAMPO e concentração explicitamente pública."""
    if magia not in DETECCOES_OWL:
        raise ValueError("magia não suportada nesta projeção")
    jogadores = estado["jogadores"]
    alvos = []
    for jogador, id_ficha in (("J1", "CE-001"), ("J2", "AB-POC-017")):
        reg = jogadores[jogador]
        if reg.get("criatura_ativa_id") != id_ficha:
            raise ValueError("fixture de campo divergente da fonte")
        carta = reg["cartas"][id_ficha]
        if carta.get("zona") != "CAMPO":
            raise ValueError("somente criaturas ativas no campo são consultáveis")
        alvos.append((jogador, id_ficha, carta))
    base = {
        "magia": magia,
        "regra_homebrew": REGRA_APROVADA,
        "escopo": "SOMENTE_CAMPOS_PUBLICOS",
        "sem_posicionamento": True,
    }
    if magia == "Detect Evil and Good":
        base["criaturas_identificadas"] = [
            {"jogador": jogador, "carta_id": card_id,
             "tipo_srd": TIPO_POR_ID[card_id]}
            for jogador, card_id, _ in alvos
            if TIPO_POR_ID[card_id] in CATEGORIAS_DETECT_EVIL_GOOD
        ]
        base["hallow_detectado"] = False
        base["hallow_fonte"] = "SEM_EFEITO_HALLOW_PUBLICO_HOMOLOGADO"
    else:
        # Fonte de magia concreta nesta fixture: Concentração com SRD
        # identificado, nunca inferir magia do Grappled/Poisoned do Roper.
        conc = estado["combate"].get("concentracao_owl")
        comprovados = []
        if conc is not None:
            if (conc.get("caster_id") != "CE-001"
                    or conc.get("magia") not in DETECCOES_OWL):
                raise ValueError("concentração pública não comprovada")
            comprovados.append({
                "jogador": "J1", "carta_id": "CE-001",
                "origem": "CONCENTRACAO_OWL_PUBLICA",
            })
        base["efeitos_magicos_publicos"] = comprovados
        base["cobertura"] = "SOMENTE_EFEITOS_HOMOLOGADOS_NO_CAMPO"
        base["aura_escola_revelada"] = False
    return base

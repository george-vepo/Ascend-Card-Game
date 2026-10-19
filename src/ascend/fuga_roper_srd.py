"""Parâmetros para escapar do Tentacle do Roper no recorte SRD 5.2.1.

A regra de Grappling do SRD permite Action para teste de
Strength (Athletics) OU Dexterity (Acrobatics) contra escape DC.
Não escolhe pelo jogador e não gera rolagens. Só Giant Owl nesta POC.
"""
from __future__ import annotations
import re
from ascend.fichas_srd import FichaConsultada, FichaConflitante


def _um(pattern: str, text: str, label: str) -> re.Match:
    hits=list(re.finditer(pattern,text,re.MULTILINE))
    if len(hits)!=1:
        raise FichaConflitante(f"{label}: campo ausente/ambíguo")
    return hits[0]


def _numero(text: str) -> int:
    return int(text.replace("−","-"))


def extrair_testes_fuga_owl(ficha: FichaConsultada) -> dict[str,int]:
    """Só modificadores de Athletics/Acrobatics verificados na ficha CE-001."""
    if (ficha.id_copia!="CE-001" or ficha.nome!="Giant Owl"
            or ficha.tipo!="Celestial" or ficha.versao!="SRD 5.2.1"):
        raise FichaConflitante("ficha de fuga não é Giant Owl SRD 5.2.1")
    text=ficha.ficha_integral
    # Na tabela de atributos: score, modificador e salvaguarda, nessa ordem.
    mods={}
    for ability, skill in (("Str","Athletics"),("Dex","Acrobatics")):
        m=_um(rf"\b{ability}\s+\d+\s+([+−-]?\d+)\s+[+−-]?\d+\b",
              text,ability)
        mod=_numero(m.group(1))
        if not -10 <= mod <= 30:
            raise FichaConflitante("modificador fora do intervalo admitido")
        mods[skill]=mod
    skills=_um(r"^Skills\s+([^\r\n]+)$",text,"Skills").group(1)
    # Se tiver proficiência em Athletics/Acrobatics, o cálculo requer
    # interpretar o respectivo valor explícito: este extrator ainda não faz isso.
    if re.search(r"\b(?:Athletics|Acrobatics)\b",skills):
        raise FichaConflitante(
            "proficiência de fuga exige extrator de perícia específico"
        )
    return mods

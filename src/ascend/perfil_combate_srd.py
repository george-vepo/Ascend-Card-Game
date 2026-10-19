"""Perfis de ataque do recorte Giant Owl × Gibbering Mouther (SRD 5.2.1).

Extrai dados DA FICHA CONSULTADA em vez de um dicionário fixo de
atributos. Só reconhece a ação corpo a corpo já implementada pelo motor.
Qualquer campo ausente ou inesperado permanece pendente; não há fallback.
"""
from __future__ import annotations
import re

from ascend.fichas_srd import FichaConsultada, FichaConflitante

ATAQUES_HOMOLOGADOS_PARA_TESTE = {
    "CE-001": "Talons",
    "AB-POC-008": "Bite",
}
LIMITACOES_POC = {
    "CE-001": ["Flyby, movimento e magias não integrados"],
    "AB-POC-008": ["Aberrant Ground, movimento e alvos múltiplos não integrados"],
}
_NUM = r"([+−-]?\d+)"


def _inteiro_assinado(valor: str) -> int:
    return int(valor.replace("−", "-"))


def _unico(padrao: str, texto: str, etiqueta: str, flags: int = 0):
    achados = list(re.finditer(padrao, texto, flags))
    if len(achados) != 1:
        raise FichaConflitante(
            f"{etiqueta}: esperado um único trecho completo na ficha; encontrados {len(achados)}"
        )
    return achados[0]


def extrair_perfil_de_combate(ficha: FichaConsultada) -> dict:
    """Somente perfil dos dois ataques do recorte; não reconhece magia ou suporte.

    A consulta de ficha anterior já checou versão, ID, ND, CA, PV e hash.
    """
    nome_ataque = ATAQUES_HOMOLOGADOS_PARA_TESTE.get(ficha.id_copia)
    if nome_ataque is None:
        raise FichaConflitante(
            "Esta criatura não possui extrator de ataque autorizado neste recorte"
        )
    corpo = ficha.ficha_integral
    iniciativa = _unico(
        rf"^Initiative\s+{_NUM}\s+\(\d+\)\s*$",
        corpo, "iniciativa", re.MULTILINE
    )
    tipo_fonte = "Celestial" if ficha.id_copia == "CE-001" else "Aberration"
    porte = _unico(
        rf"^(Tiny|Small|Medium|Large|Huge|Gargantuan)\s+{tipo_fonte}\b",
        corpo, "tamanho", re.MULTILINE
    )
    # Somente linhas numéricas explícitas do texto integral são consideradas.
    ca = _unico(r"^AC\s+(\d+)\s*$", corpo, "CA", re.MULTILINE)
    pv = _unico(r"^HP\s+(\d+)\s+\(", corpo, "PV", re.MULTILINE)
    if int(ca.group(1)) != ficha.ca or int(pv.group(1)) != ficha.pv_maximos:
        raise FichaConflitante("CA/PV no texto integral não conferem com ficha")

    if "\nActions\n" not in corpo:
        raise FichaConflitante("Seção Actions ausente")
    # Linhas da ação podem ser quebradas entre expressão de dano e tipo.
    actions = " ".join(corpo.split("\nActions\n", 1)[1].split())
    padrao = (
        rf"\b{re.escape(nome_ataque)}\.\s+Melee Attack Roll:\s*{_NUM},"
        r"\s*reach\s+(\d+)\s*ft\.\s*Hit:\s*(\d+)\s*"
        r"\((\d+)d(\d+)(?:\s*([+−-])\s*(\d+))?\)"
        r"\s+(Slashing|Piercing)\s+damage\."
    )
    atk = _unico(padrao, actions, "ação "+nome_ataque)
    bonus = _inteiro_assinado(atk.group(1))
    alcance = int(atk.group(2))
    media_ficha = int(atk.group(3))
    num_dados = int(atk.group(4))
    faces = int(atk.group(5))
    sinal = atk.group(6)
    magnitude = int(atk.group(7)) if atk.group(7) else 0
    fixo = -magnitude if sinal in ("−", "-") else magnitude
    tipo_dano = atk.group(8)
    if not (1 <= num_dados <= 20 and 2 <= faces <= 100
            and 1 <= alcance <= 1000 and -30 <= bonus <= 30
            and -30 <= fixo <= 30 and 0 < media_ficha <= 200):
        raise FichaConflitante("Parâmetros do ataque fora dos limites aceitos")
    # A média publicada é um dado textual de auditoria, não um dado a rolar.
    # O valor na fonte deve concordar com a expressão de dano (arredondamento SRD).
    media_calculada = (num_dados * (faces + 1) // 2) + fixo
    if media_calculada != media_ficha:
        raise FichaConflitante("Dano médio publicado diverge dos dados e modificador")

    resistencias = _unico(
        r"^Resistances\s+([^\r\n]+)\s*$",
        corpo, "resistências Celestial", re.MULTILINE
    ).group(1).strip() if ficha.id_copia == "CE-001" else ""
    resistencias_list = [x.strip() for x in resistencias.split(",") if x.strip()]
    if ficha.id_copia == "AB-POC-008":
        _unico(r"^Immunities\s+Prone\s*$", corpo, "imunidade à condição Prone",
               re.MULTILINE)
        condicoes_imunes = ["Prone"]
    else:
        condicoes_imunes = []
    # Não interpretar "Immunities Prone" como imunidade a dano.
    return {
        "name": ficha.nome,
        "source": f"{ficha.versao} / {ficha.id_catalogo}",
        "ac": ficha.ca, "hp": ficha.pv_maximos,
        "initiative": _inteiro_assinado(iniciativa.group(1)),
        "size": porte.group(1),
        "resistances": resistencias_list,
        "immunities": [],
        "condition_immunities": condicoes_imunes,
        "attack": {
            "name": nome_ataque, "bonus": bonus, "reach_ft": alcance,
            "dice": (num_dados, faces), "flat": fixo,
            "type": tipo_dano, "average_in_source": media_ficha,
        },
        "limitations": list(LIMITACOES_POC[ficha.id_copia]),
        "source_sha256": ficha.sha256_documento,
        "source_git_commit": ficha.revisao_git,
        "mechanics_fully_supported": False,
    }

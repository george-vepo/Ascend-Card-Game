"""Consultas MECÂNICAS sob demanda do Catálogo SRD, somente leitura.

Não inventa atributos, não homologa ações e não altera o estado de jogo.
São fontes identificadas três fichas de Aberração e uma Celestial no catálogo pinado.
O campo editorial_review das três ainda informa "AINDA_NAO_TESTADA_EM_ENGINE".
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence
import hashlib
import json

from ascend.catalogo_poc import (
    CopiaReferencia, RevisaoCatalogoDivergente, nd_decimal, raridade_pelo_nd,
    _commit_checkout,
)

CAMINHO_FICHAS = (
    "operational/research/decks/aberracao-40-20261014/"
    "fichas_srd521_integral_3.json"
)
SCHEMA_ESPERADO = "SRD_3_ABERRACOES_SR521_CC_BY_2026-10-14"
CAMINHO_FICHA_CELESTIAL = (
    "operational/research/decks/celestial-40-20261015/"
    "fichas_srd521_giant_owl_1.json"
)
SCHEMA_CELESTIAL = "SRD_1_CELESTIAL_SRD521_CC_BY_2026-10-19"
REVISAO_EDITORIAL = "FONTE_INTEGRAL_IDENTIFICADA; AINDA_NAO_TESTADA_EM_ENGINE"
ORIGEM_SRD = "https://www.dndbeyond.com/srd"


class FichaPendente(LookupError):
    """Não há uma ficha mecânica suficiente para a cópia solicitada."""


class FichaConflitante(ValueError):
    """Documento apresenta divergências que impedem usar seus dados."""


@dataclass(frozen=True)
class FichaConsultada:
    id_copia: str
    id_catalogo: str
    nome: str
    tipo: str
    nd: str
    ca: int
    pv_maximos: int
    ficha_integral: str
    fonte: str
    versao: str
    atribuicao: str
    editorial_review: str
    sha256_documento: str
    revisao_git: str | None
    mecanicas_automaticamente_homologadas: bool = False

    def referencia_sem_texto(self) -> dict:
        """Metadados estritos — não executar ataques/magias por este retorno."""
        return {
            "id_copia": self.id_copia, "id_catalogo": self.id_catalogo,
            "nome": self.nome, "tipo": self.tipo, "nd": self.nd,
            "ca": self.ca, "pv_maximos": self.pv_maximos,
            "fonte": self.fonte, "versao": self.versao,
            "editorial_review": self.editorial_review,
            "sha256_documento": self.sha256_documento,
            "revisao_git": self.revisao_git,
            "mecanicas_automaticamente_homologadas": False,
        }


def _campo_string(item: dict, name: str) -> str:
    val = item.get(name)
    if not isinstance(val, str) or not val.strip():
        raise FichaConflitante(f"Campo essencial ausente: {name}")
    return val.strip()


def _ca_pv(item: dict, name: str) -> int:
    value = item.get(name)
    if type(value) is not int or value <= 0:
        raise FichaConflitante(f"{name} precisa ser inteiro positivo")
    return value


def consultar_ficha(
    raiz_catalogo: str | Path,
    contrato_catalogo: Mapping,
    referencias: Sequence[CopiaReferencia],
    id_copia: str,
    *,
    exigir_revisao: bool = True,
) -> FichaConsultada:
    """Consulta individual após a identidade da carta já ter sido validada.

    exigir_revisao=False só é aceito em testes sintéticos. Não usar para
    partidas oficiais. Esta função NUNCA muda o motor.
    """
    if not isinstance(id_copia, str) or not id_copia.strip():
        raise FichaPendente("ID de cópia obrigatório")
    refs = [x for x in referencias if x.id_copia == id_copia]
    if len(refs) != 1:
        raise FichaPendente("ID ausente ou ambíguo nas referências")
    ref = refs[0]
    if not ref.id_catalogo:
        raise FichaPendente("Cópia não tem ficha canônica vinculada")

    raiz = Path(raiz_catalogo).expanduser().resolve()
    esperado = contrato_catalogo.get("revisao_commit")
    atual = _commit_checkout(raiz) if exigir_revisao else None
    if exigir_revisao and (
        not isinstance(esperado, str) or atual != esperado
    ):
        raise RevisaoCatalogoDivergente("Commit do catálogo diverge do manifesto")

    caminho_relativo, schema = (
        (CAMINHO_FICHA_CELESTIAL, SCHEMA_CELESTIAL)
        if ref.id_catalogo == "AT-023" and ref.id_copia == "CE-001"
        else (CAMINHO_FICHAS, SCHEMA_ESPERADO)
    )
    path = (raiz / caminho_relativo).resolve()
    if not path.is_relative_to(raiz):
        raise FichaConflitante("Fonte fora do catálogo")
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise FichaPendente("Acervo integral SRD ainda não disponível") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise FichaConflitante("Documento de fichas inválido") from exc
    if not isinstance(payload, dict) or payload.get("schema") != schema:
        raise FichaConflitante("Schema da fonte de fichas não reconhecido")
    if payload.get("source") != ORIGEM_SRD:
        raise FichaConflitante("Fonte do documento não corresponde ao SRD")
    registros = payload.get("records")
    if not isinstance(registros, list):
        raise FichaConflitante("Registros de ficha ausentes")
    candidatos = [
        r for r in registros
        if isinstance(r, dict) and r.get("id") == ref.id_catalogo
    ]
    if not candidatos:
        raise FichaPendente("Ficha individual ainda não consta neste acervo")
    if len(candidatos) != 1:
        raise FichaConflitante("ID de ficha duplicado no acervo")
    item = candidatos[0]
    nome = _campo_string(item, "nome")
    tipo = _campo_string(item, "tipo")
    nd = nd_decimal(_campo_string(item, "nd"))
    raridade = _campo_string(item, "raridade")
    versao = _campo_string(item, "versao")
    revisao_editorial = _campo_string(item, "editorial_review")
    atribuicao = _campo_string(item, "attribution")
    conteudo = _campo_string(item, "ficha_integral_texto_local")
    ca, pv = _ca_pv(item, "ca"), _ca_pv(item, "pv")
    if nome != ref.nome or tipo != ref.tipo or nd != ref.nd:
        raise FichaConflitante("Nome, tipo ou ND difere do catálogo de cartas")
    if raridade != ref.raridade or raridade != raridade_pelo_nd(nd):
        raise FichaConflitante("Raridade incompatível com ND da carta")
    if versao != "SRD 5.2.1" or revisao_editorial != REVISAO_EDITORIAL:
        raise FichaConflitante("Versão ou situação editorial não reconhecida")
    if _campo_string(item, "licenca") not in {
        "CC-BY-4.0",
        "Creative Commons Attribution 4.0",
        "Creative Commons Attribution 4.0 International",
    }:
        raise FichaConflitante("Atribuição/licença SRD ausente")
    # Não basta uma cifra solta: o próprio corpo precisa confirmar AC/HP.
    if (
        not conteudo.startswith(nome + " |")
        or f"AC {ca}\n" not in conteudo
        or f"HP {pv} " not in conteudo
        or "\nActions\n" not in conteudo
    ):
        raise FichaConflitante("Cabeçalho, CA, PV ou ações divergem do texto")
    return FichaConsultada(
        id_copia=ref.id_copia, id_catalogo=ref.id_catalogo,
        nome=nome, tipo=tipo, nd=str(nd),
        ca=ca, pv_maximos=pv, ficha_integral=conteudo,
        fonte=ORIGEM_SRD, versao=versao, atribuicao=atribuicao,
        editorial_review=revisao_editorial,
        sha256_documento=hashlib.sha256(raw).hexdigest(),
        revisao_git=atual,
    )

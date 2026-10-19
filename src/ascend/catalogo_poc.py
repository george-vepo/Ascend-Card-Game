"""Leitura estrita dos 2 decks de REFERÊNCIA do Catálogo SRD.

O Catálogo SRD é a fonte de fichas, cartas, imagens e dados mecânicos.
Aqui ficam SOMENTE identidades de cópias geradas em memória e seus metadados
de referência. Nada neste arquivo homologa fichas, habilidades ou suportes.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import json
import subprocess
from typing import Any


class CatalogoInvalido(ValueError):
    """Formato ou informações de referência incompatíveis com o contrato POC."""


class RevisaoCatalogoDivergente(CatalogoInvalido):
    """O checkout externo não é o commit aprovado para esta integração."""


@dataclass(frozen=True)
class CopiaReferencia:
    jogador: str
    id_copia: str
    posicao_referencia: int
    nome: str
    tipo: str
    nd: Decimal
    raridade: str
    id_catalogo: str | None
    fonte_classificacao_ficha: str
    status_suporte: str
    homologacao_declarada_catalogo: str

    # Esta classe NÃO contém CA, PV, ataques, arte, recursos, magias ou
    # conteúdo de ficha. Esses dados devem ser consultados sob demanda.


def nd_decimal(texto: Any) -> Decimal:
    if not isinstance(texto, str) or not texto.strip():
        raise CatalogoInvalido("ND deve ser texto explícito")
    valor = texto.strip()
    try:
        if "/" in valor:
            partes = valor.split("/")
            if len(partes) != 2:
                raise CatalogoInvalido("Fração de ND inválida")
            a, b = Decimal(partes[0]), Decimal(partes[1])
            if b == 0:
                raise CatalogoInvalido("ND com denominador zero")
            nd = a / b
        else:
            nd = Decimal(valor)
    except (InvalidOperation, ZeroDivisionError) as exc:
        raise CatalogoInvalido("ND não numérico") from exc
    if not nd.is_finite() or nd < 0:
        raise CatalogoInvalido("ND não finito ou negativo")
    return nd


def raridade_pelo_nd(nd: Decimal) -> str:
    if 0 <= nd <= 5:
        return "Comum"
    if 6 <= nd <= 10:
        return "Incomum"
    if 11 <= nd <= 15:
        return "Rara"
    if 16 <= nd <= 20:
        return "Lendária"
    if nd >= 21:
        return "Mítica"
    raise CatalogoInvalido(f"ND {nd} não classificado nas faixas aprovadas")


def _texto(registro: dict, campo: str, deck: str, indice: int) -> str:
    valor = registro.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise CatalogoInvalido(f"{deck} #{indice}: campo obrigatório {campo}")
    return valor.strip()


def _json_raiz(raiz: Path, relativo: str) -> tuple[list[dict], str]:
    caminho = (raiz / relativo).resolve()
    if not caminho.is_relative_to(raiz):
        raise CatalogoInvalido("Caminho fora do checkout externo")
    try:
        raw = caminho.read_bytes()
    except FileNotFoundError as exc:
        raise CatalogoInvalido(f"Arquivo de catálogo ausente: {relativo}") from exc
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise CatalogoInvalido(f"JSON inválido: {relativo}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise CatalogoInvalido(f"Esperado objeto com lista records: {relativo}")
    return data["records"], hashlib.sha256(raw).hexdigest()


def _commit_checkout(raiz: Path) -> str:
    try:
        p = subprocess.run(
            ["git", "-C", str(raiz), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=8, check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RevisaoCatalogoDivergente(
            "Checkout do Catálogo SRD precisa ser um repositório Git legível"
        ) from exc
    return p.stdout.strip()


def carregar_referencias(
    checkout_catalogo: str | Path,
    contrato: dict[str, Any],
    *,
    exigir_revisao: bool = True,
) -> tuple[tuple[CopiaReferencia, ...], dict[str, Any]]:
    """Lê os dados SOMENTE do checkout externo e devolve cópias POC em memória.

    exigir_revisao=False serve unicamente para fixtures sintéticas/testes,
    nunca autoriza partidas oficiais. Não há embaralhamento ou compra.
    """
    raiz = Path(checkout_catalogo).expanduser().resolve()
    rev = _commit_checkout(raiz) if exigir_revisao else None
    esperado = contrato.get("revisao_commit")
    if exigir_revisao and (not isinstance(esperado, str) or rev != esperado):
        raise RevisaoCatalogoDivergente(
            f"Revisão divergente: atual={rev}; esperada={esperado}"
        )
    if contrato.get("quantidade_por_deck") != 40:
        raise CatalogoInvalido("POC exige 40 cópias em cada deck")
    arquivos = contrato.get("arquivos")
    if not isinstance(arquivos, dict) or set(arquivos) != {"celestial", "aberracao"}:
        raise CatalogoInvalido("Manifesto dos dois decks é obrigatório")
    cel, hash_cel = _json_raiz(raiz, arquivos["celestial"])
    abe, hash_abe = _json_raiz(raiz, arquivos["aberracao"])
    if len(cel) != 40 or len(abe) != 40:
        raise CatalogoInvalido("Cada deck deve ter exatamente 40 registros")

    saida: list[CopiaReferencia] = []
    for indice, registro in enumerate(cel, 1):
        if not isinstance(registro, dict):
            raise CatalogoInvalido("Registro Celestial inválido")
        cid = _texto(registro, "id", "Celestial", indice)
        if cid != f"CE-{indice:03d}":
            raise CatalogoInvalido("ID de cópia Celestial ausente ou fora de ordem")
        nome = _texto(registro, "name", "Celestial", indice)
        tipo = _texto(registro, "type", "Celestial", indice)
        if tipo != "Celestial":
            raise CatalogoInvalido("Tipo inesperado no deck Celestial")
        nd = nd_decimal(_texto(registro, "nd", "Celestial", indice))
        rare = _texto(registro, "rarity", "Celestial", indice)
        if rare != raridade_pelo_nd(nd):
            raise CatalogoInvalido(f"Raridade Celestial difere do ND: {cid}")
        saida.append(CopiaReferencia(
            jogador="J1", id_copia=cid, posicao_referencia=indice,
            nome=nome, tipo=tipo, nd=nd, raridade=rare,
            id_catalogo=(str(registro.get("catalogId") or "").strip() or None),
            fonte_classificacao_ficha="CONSULTAR_FICHA_SOB_DEMANDA",
            status_suporte=str(registro.get("status") or "NAO_HOMOLOGADO"),
            homologacao_declarada_catalogo="NAO_VERIFICADA_NESTE_ADAPTADOR",
        ))

    for indice, registro in enumerate(abe, 1):
        if not isinstance(registro, dict):
            raise CatalogoInvalido("Registro Aberração inválido")
        ordem = _texto(registro, "ORDEM", "Aberração", indice)
        if ordem != str(indice):
            raise CatalogoInvalido("Ordem de Aberração inválida")
        nome = _texto(registro, "NOME", "Aberração", indice)
        tipo = _texto(registro, "TIPO", "Aberração", indice)
        if tipo != "Aberração":
            raise CatalogoInvalido("Tipo inesperado no deck Aberração")
        nd = nd_decimal(_texto(registro, "ND", "Aberração", indice))
        rare = _texto(registro, "RARIDADE", "Aberração", indice)
        if rare != raridade_pelo_nd(nd):
            raise CatalogoInvalido(f"Raridade Aberração difere do ND: {indice}")
        saida.append(CopiaReferencia(
            jogador="J2", id_copia=f"AB-POC-{indice:03d}",
            posicao_referencia=indice, nome=nome, tipo=tipo, nd=nd,
            raridade=rare,
            id_catalogo=(str(registro.get("ID_CATALOGO") or "").strip() or None),
            fonte_classificacao_ficha=str(registro.get("CLASSIFICACAO_FICHA") or
                                           "NAO_VERIFICADA"),
            status_suporte="NAO_HOMOLOGADO",
            homologacao_declarada_catalogo=str(registro.get("HOMOLOGACAO_JOGO") or
                                               "NAO_VERIFICADA"),
        ))

    ids = [c.id_copia for c in saida]
    if len(set(ids)) != 80:
        raise CatalogoInvalido("IDs de cópia duplicados")
    proveniencia = {
        "repositor_io": contrato.get("repositor_io"),
        "revisao_git": rev,
        "revisao_verificada": exigir_revisao,
        "sha256_conteudos": {"celestial": hash_cel, "aberracao": hash_abe},
        "copias": {"J1": 40, "J2": 40},
        "aviso": "Identidades de referência; não é estado oficial, embaralhamento, "
                 "ficha homologada nem autorização de uso de suporte",
    }
    return tuple(saida), proveniencia


def ler_contrato(pasta_ascend: str | Path) -> dict[str, Any]:
    p = Path(pasta_ascend) / "config/catalogo_srd.json"
    return json.loads(p.read_text(encoding="utf-8"))

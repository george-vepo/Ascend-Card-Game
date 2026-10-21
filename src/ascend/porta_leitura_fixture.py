"""Leitura de checkpoints fictícios cifrados com credenciais por sessão.

Somente biblioteca de backend. NÃO é endpoint HTTP nem autenticação de produção.
Não distribuir credenciais, snapshots ou esta instância ao navegador.
"""
from __future__ import annotations

import hashlib
import hmac
import math
import re
from collections.abc import Mapping
from typing import Any

from ascend.checkpoint_privado import CheckpointPrivado

_PAPEIS = ("PUBLICO", "J1", "J2")
_REF = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")
_TOKEN = re.compile(r"[A-Za-z0-9_-]{32,128}\Z")
_COPIA = re.compile(r"[A-Za-z0-9_:-]{1,80}\Z")
_PUBLICOS = ("copiaId", "nome", "tipo", "nd", "raridade", "ca", "pvMax")
_PRIVADOS = ("copiaId", "catalogoId", "nome", "tipo", "nd", "raridade", "ca", "pvMax")
_FASES = frozenset(("TROCA", "CRIATURA", "PREPARACAO_NAO_IMPLEMENTADA",
                    "SUPORTE_NAO_IMPLEMENTADO"))


class AcessoNegado(Exception):
    """Não revela se a sessão existe ou qual credencial falhou."""


class EstadoIndisponivel(Exception):
    """Checkpoint não é uma fixture legível, sem divulgar dados privados."""


def _falhar_estado() -> None:
    raise EstadoIndisponivel("checkpoint sintético indisponível")


def _cartao(carta: dict[str, Any], campos: tuple[str, ...]) -> dict[str, Any]:
    # Whitelist: campos extras no snapshot não atravessam a fronteira de leitura.
    resultado = {campo: carta.get(campo) for campo in campos}
    if not isinstance(resultado["copiaId"], str) or not _COPIA.fullmatch(resultado["copiaId"]):
        _falhar_estado()
    if not isinstance(resultado["nome"], str) or not resultado["nome"].strip():
        _falhar_estado()
    if not isinstance(resultado["tipo"], str) or not resultado["tipo"].strip():
        _falhar_estado()
    if not isinstance(resultado["raridade"], str) or not resultado["raridade"].strip():
        _falhar_estado()
    nd = resultado["nd"]
    if type(nd) not in (str, int, float) or (isinstance(nd, str) and not nd.strip()) or (
        type(nd) is float and not math.isfinite(nd)
    ):
        _falhar_estado()
    ca, pv = resultado["ca"], resultado["pvMax"]
    if ca is not None and (type(ca) is not int or ca < 0):
        _falhar_estado()
    if pv is not None and (type(pv) is not int or pv < 1):
        _falhar_estado()
    return resultado


def _projecoes(estado: dict[str, Any], versao: int, papel: str) -> dict[str, Any]:
    if not isinstance(estado, dict) or estado.get("ambiente") != "FIXTURE_NAO_OFICIAL":
        _falhar_estado()
    fase, vez, placar = estado.get("fase"), estado.get("vez"), estado.get("placar")
    jogadores = estado.get("jogadores")
    if not isinstance(fase, str) or fase not in _FASES or vez not in ("J1", "J2", None):
        _falhar_estado()
    if not isinstance(placar, dict) or set(placar) != {"J1", "J2"}:
        _falhar_estado()
    if any(type(placar[s]) is not int or placar[s] != 0 for s in ("J1", "J2")):
        _falhar_estado()
    if not isinstance(jogadores, dict) or set(jogadores) != {"J1", "J2"}:
        _falhar_estado()

    publico = {}
    maos_privadas = {}
    identificadores = set()
    for lado in ("J1", "J2"):
        jogador = jogadores[lado]
        if not isinstance(jogador, dict):
            _falhar_estado()
        monte, mao, cemiterio, campo = (
            jogador.get("monte"), jogador.get("mao"),
            jogador.get("cemiterio"), jogador.get("campo")
        )
        if any(not isinstance(x, list) for x in (monte, mao, cemiterio)):
            _falhar_estado()
        copias = monte + mao + cemiterio + ([] if campo is None else [campo])
        if len(copias) != 40:
            _falhar_estado()
        for carta in copias:
            if not isinstance(carta, dict):
                _falhar_estado()
            identidade = _cartao(carta, _PUBLICOS)["copiaId"]
            if identidade in identificadores:
                _falhar_estado()
            identificadores.add(identidade)
        if campo is not None:
            ativa = _cartao(campo, _PUBLICOS)
            atual = campo.get("pvAtual")
            if type(atual) is not int or atual < 1 or (
                ativa["pvMax"] is None or atual > ativa["pvMax"]
            ):
                _falhar_estado()
            ativa["pvAtual"] = atual
        else:
            ativa = None
        publico[lado] = {
            "monte": len(monte), "mao": len(mao),
            "cemiterio": len(cemiterio), "campo": ativa,
        }
        if lado == papel:
            maos_privadas[lado] = [_cartao(c, _PRIVADOS) for c in mao]

    visao = {
        "modo": "FIXTURE_NAO_OFICIAL",
        "versao_checkpoint": versao,
        "fase": fase, "vez": vez,
        "placar": {"J1": placar["J1"], "J2": placar["J2"]},
        "jogadores": publico,
    }
    if papel in ("J1", "J2"):
        visao["mao_privada"] = {"jogador": papel, "cartas": maos_privadas[papel]}
    return visao


class PortaLeituraFixture:
    """Leitura somente: exige credenciais distintas por referência e jogador.

    O backend confiável configura {ref: {"PUBLICO": token, "J1": token, "J2": token}}.
    Tokens são por sessão e nunca entram no resultado ou no SQLite.
    A geração e distribuição segura desses tokens são responsabilidades futuras.
    """

    def __init__(self, checkpoint: CheckpointPrivado,
                 credenciais: Mapping[str, Mapping[str, str]]):
        if not isinstance(checkpoint, CheckpointPrivado) or not isinstance(credenciais, Mapping):
            raise ValueError("configuração de leitura inválida")
        chaves = {}
        for ref, papeis in credenciais.items():
            if not isinstance(ref, str) or not _REF.fullmatch(ref):
                raise ValueError("referência de sessão inválida")
            if not isinstance(papeis, Mapping) or set(papeis) != set(_PAPEIS):
                raise ValueError("credenciais devem definir PUBLICO, J1 e J2")
            tokens = list(papeis.values())
            if any(not isinstance(t, str) or not _TOKEN.fullmatch(t) for t in tokens) or (
                len(set(tokens)) != len(_PAPEIS)
            ):
                raise ValueError("credenciais de sessão inválidas ou duplicadas")
            # Mantém somente digests, nunca tokens plaintext dentro do gate.
            chaves[ref] = {
                papel: hashlib.sha256((ref + ":" + papeis[papel]).encode("ascii")).digest()
                for papel in _PAPEIS
            }
        self._checkpoint = checkpoint
        self._chaves = chaves

    def consultar(self, referencia: str, token: str) -> dict[str, Any]:
        # Autorização ANTES do SQLite: referência inexistente não é distinguível.
        if (not isinstance(referencia, str) or not _REF.fullmatch(referencia)
                or not isinstance(token, str) or not _TOKEN.fullmatch(token)):
            raise AcessoNegado("acesso não autorizado")
        esperadas = self._chaves.get(referencia)
        if esperadas is None:
            raise AcessoNegado("acesso não autorizado")
        digest = hashlib.sha256((referencia + ":" + token).encode("ascii")).digest()
        papel = None
        for candidato in _PAPEIS:
            if hmac.compare_digest(digest, esperadas[candidato]):
                papel = candidato
        if papel is None:
            raise AcessoNegado("acesso não autorizado")
        loaded = self._checkpoint.carregar(referencia)
        if loaded is None:
            _falhar_estado()
        return _projecoes(loaded["estado"], loaded["versao"], papel)

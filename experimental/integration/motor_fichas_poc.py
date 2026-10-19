"""Invocação/evolução de fixture com ficha SRD obtida SOB DEMANDA.

Somente motor experimental. Nenhum dado de CA/PV é presumido, nenhum
ataque/suporte é homologado e nenhuma partida oficial é criada.
Cada ficha aceita é consultada NA TRANSAÇÃO do evento, nunca mutada antes.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from ascend.catalogo_poc import (
    CopiaReferencia, carregar_referencias, RevisaoCatalogoDivergente,
)
from ascend.fichas_srd import consultar_ficha, FichaPendente, FichaConflitante
from bridge_catalogo_motor import _registros, FonteDivergente
from motor_poc import MotorPOC, InvalidAction, UnresolvedRule, CorruptedCheckpoint
from motor_poc import RANKS, digest


DECK_ARQUIVOS = (
    "docs/catalogo/data/deck-celestial-40.json",
    "docs/catalogo/data/deck-aberracao-40.json",
)
FICHAS_ARQUIVOS = (
    "operational/research/decks/aberracao-40-20261014/"
    "fichas_srd521_integral_3.json",
    "operational/research/decks/celestial-40-20261015/"
    "fichas_srd521_giant_owl_1.json",
)


def conferir_checkout_sem_modificacoes(raiz: str | Path) -> None:
    """Evita tomar arquivo local modificado como se fosse o commit pinado.

    Nunca altera o checkout. O git status inclui caminhos alterados/novos.
    """
    try:
        p = subprocess.run(
            ["git", "-C", str(raiz), "status", "--porcelain", "--",
             *DECK_ARQUIVOS, *FICHAS_ARQUIVOS],
            text=True, capture_output=True, check=True, timeout=8,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RevisaoCatalogoDivergente(
            "Não foi possível inspecionar o checkout externo"
        ) from exc
    if p.stdout.strip():
        raise RevisaoCatalogoDivergente(
            "Checkout do Catálogo SRD contém modificações não versionadas "
            "nos arquivos de referência"
        )


class MotorFichasPOC(MotorPOC):
    """Mesmas fases do motor v2.2, com fonte validada para CA/PV de cartas alvo."""

    def __init__(
        self,
        registros: list[dict],
        *,
        referencias: Sequence[CopiaReferencia],
        contrato: Mapping[str, Any],
        checkout_catalogo: str | Path,
        primeiro: str = "J1",
        maos_fixadas: dict[str, list[str]] | None = None,
        exigir_revisao: bool = True,
    ):
        self.referencias = tuple(referencias)
        self.contrato = copy.deepcopy(dict(contrato))
        self.checkout_catalogo = Path(checkout_catalogo).expanduser().resolve()
        self.exigir_revisao = exigir_revisao
        super().__init__(
            registros, first=primeiro, hands=maos_fixadas,
            match_id="ASCEND-FICHAS-FIXTURE-NAO-OFICIAL", test_fixture=True,
        )

    def _transition(self, state, actor, command, params):
        if command not in {"INVOCAR", "EVOLUIR"}:
            return super()._transition(state, actor, command, params)

        # Apenas ações já legais na fase solicitada chegam à consulta externa.
        if actor not in ("J1", "J2"):
            raise InvalidAction("ação de criatura exige jogador")
        self._gate(state, "INVOCACAO_EVOLUCAO", actor)
        j = state["jogadores"][actor]
        cid = params.get("carta_id")
        alvo = self.get_card(state, actor, cid)
        if command == "INVOCAR":
            if (j["criatura_ativa_id"] is not None or
                    alvo["zona"] != "MAO" or alvo["raridade"] != "Comum"):
                raise InvalidAction("invocação exige Comum na mão e campo vazio")
        else:
            old_id = j["criatura_ativa_id"]
            if not old_id:
                raise InvalidAction("sem criatura ativa para evoluir")
            anterior = self.get_card(state, actor, old_id)
            if (alvo["zona"] != "MAO" or anterior["tipo"] != alvo["tipo"] or
                    RANKS.index(alvo["raridade"]) !=
                    RANKS.index(anterior["raridade"]) + 1):
                raise InvalidAction("evolução exige mesma categoria e raridade adjacente")

        if self.exigir_revisao:
            conferir_checkout_sem_modificacoes(self.checkout_catalogo)
        try:
            ficha = consultar_ficha(
                self.checkout_catalogo, self.contrato, self.referencias,
                cid, exigir_revisao=self.exigir_revisao,
            )
        except (FichaPendente, FichaConflitante) as exc:
            raise UnresolvedRule("ficha individual pendente/divergente: " + str(exc)) from exc

        # Modifica SOMENTE o estado PROPOSTO da transação; apply() só registra
        # após a transição e a validação completa do motor.
        if alvo["pv_max"] is not None and alvo["pv_max"] != ficha.pv_maximos:
            raise UnresolvedRule("PV da ficha não conferem com o registro existente")
        anterior_ficha = alvo.get("origem_ficha")
        fonte = {
            "id_catalogo": ficha.id_catalogo,
            "versao": ficha.versao,
            "revisao_git": ficha.revisao_git,
            "sha256_documento": ficha.sha256_documento,
            "editorial_review": ficha.editorial_review,
            "habilidades_homologadas": False,
        }
        if anterior_ficha is not None and anterior_ficha != fonte:
            raise UnresolvedRule("ficha da carta mudou durante a fixture")
        alvo["pv_max"] = ficha.pv_maximos
        alvo["ca_fonte"] = ficha.ca
        alvo["origem_ficha"] = fonte
        resultado = super()._transition(state, actor, command, params)
        resultado["ficha_consultada"] = {
            "id_catalogo": ficha.id_catalogo,
            "ca": ficha.ca,
            "pv_maximos": ficha.pv_maximos,
            "revisao_git": ficha.revisao_git,
            "sha256_documento": ficha.sha256_documento,
            "habilidades_homologadas": False,
        }
        return resultado


@dataclass
class SessaoFichasFixture:
    """Fixture isolada vinculada à origem das 80 cópias, sem side effects."""

    motor: MotorFichasPOC
    registros: list[dict]
    referencias: tuple[CopiaReferencia, ...]
    proveniencia: dict[str, Any]
    contrato: dict[str, Any]
    hash_identidades: str

    @classmethod
    def criar_de_referencias(
        cls, referencias: Sequence[CopiaReferencia],
        proveniencia: Mapping[str, Any], contrato: Mapping[str, Any],
        checkout_catalogo: str | Path, *,
        primeiro: str = "J1",
        maos_fixadas: dict[str, list[str]] | None = None,
    ) -> "SessaoFichasFixture":
        """Somente para testes sintéticos: NÃO verifica um checkout Git real."""
        if not isinstance(proveniencia, Mapping) or not isinstance(
            proveniencia.get("sha256_conteudos"), dict
        ) or set(proveniencia["sha256_conteudos"]) != {"celestial", "aberracao"}:
            raise InvalidAction("proveniência dos dois decks obrigatória")
        registros = _registros(referencias)
        motor = MotorFichasPOC(
            registros, referencias=referencias, contrato=contrato,
            checkout_catalogo=checkout_catalogo, primeiro=primeiro,
            maos_fixadas=maos_fixadas, exigir_revisao=False,
        )
        return cls(
            motor, registros, tuple(referencias),
            copy.deepcopy(dict(proveniencia)), copy.deepcopy(dict(contrato)),
            digest(registros),
        )

    @classmethod
    def criar_de_checkout(
        cls, checkout_catalogo: str | Path,
        contrato: Mapping[str, Any], *,
        primeiro: str = "J1",
        maos_fixadas: dict[str, list[str]] | None = None,
    ) -> "SessaoFichasFixture":
        conferir_checkout_sem_modificacoes(checkout_catalogo)
        refs, origem = carregar_referencias(
            checkout_catalogo, dict(contrato), exigir_revisao=True,
        )
        registros = _registros(refs)
        motor = MotorFichasPOC(
            registros, referencias=refs, contrato=contrato,
            checkout_catalogo=checkout_catalogo, primeiro=primeiro,
            maos_fixadas=maos_fixadas, exigir_revisao=True,
        )
        return cls(
            motor, registros, tuple(refs), copy.deepcopy(origem),
            copy.deepcopy(dict(contrato)), digest(registros),
        )

    def comando(self, evento_id: str, ator: str, acao: str, params=None) -> dict:
        return self.motor.apply(evento_id, ator, acao, params)

    def mesa_publica(self) -> dict:
        return self.motor.public()

    def visao_privada(self, jogador: str) -> dict:
        return self.motor.private(jogador)

    def checkpoint(self) -> dict:
        """PRIVADO: contém mãos e ordem de montes, não publicar no Git."""
        return {
            "schema": "ASCEND_FICHAS_FIXTURE_V1",
            "unicamente_teste": True,
            "proveniencia": copy.deepcopy(self.proveniencia),
            "hash_identidades": self.hash_identidades,
            "contrato": copy.deepcopy(self.contrato),
            "motor": self.motor.checkpoint(),
        }

    @classmethod
    def restaurar(
        cls, checkpoint: dict,
        checkout_catalogo: str | Path,
        contrato: Mapping[str, Any], *,
        exigir_revisao: bool = True,
        referencias_fixture: Sequence[CopiaReferencia] | None = None,
        proveniencia_fixture: Mapping[str, Any] | None = None,
    ) -> "SessaoFichasFixture":
        if (checkpoint.get("schema") != "ASCEND_FICHAS_FIXTURE_V1"
                or checkpoint.get("unicamente_teste") is not True):
            raise FonteDivergente("checkpoint não pertence a esta fixture")
        if exigir_revisao:
            conferir_checkout_sem_modificacoes(checkout_catalogo)
            refs, prov = carregar_referencias(
                checkout_catalogo, dict(contrato), exigir_revisao=True,
            )
        else:
            if referencias_fixture is None or proveniencia_fixture is None:
                raise FonteDivergente("restauração sintética exige referências explícitas")
            refs, prov = tuple(referencias_fixture), dict(proveniencia_fixture)
        registros = _registros(refs)
        if (checkpoint.get("hash_identidades") != digest(registros)
                or checkpoint.get("proveniencia") != prov
                or checkpoint.get("contrato") != dict(contrato)):
            raise FonteDivergente("identidades, contrato ou fonte divergentes")
        # Valida a cadeia de eventos e os hashes ANTES de reconstruir a camada.
        antigo = MotorPOC.restore(checkpoint["motor"], registros)

        # Todas as fichas carregadas precisam continuar idênticas no checkout.
        for p in ("J1", "J2"):
            for cid, card in antigo.state["jogadores"][p]["cartas"].items():
                origem = card.get("origem_ficha")
                if origem is None:
                    continue
                try:
                    ficha = consultar_ficha(
                        checkout_catalogo, dict(contrato), refs, cid,
                        exigir_revisao=exigir_revisao,
                    )
                except (FichaPendente, FichaConflitante) as exc:
                    raise FonteDivergente("ficha restaurada indisponível") from exc
                if (
                    card["pv_max"] != ficha.pv_maximos
                    or card.get("ca_fonte") != ficha.ca
                    or origem != {
                        "id_catalogo": ficha.id_catalogo,
                        "versao": ficha.versao,
                        "revisao_git": ficha.revisao_git,
                        "sha256_documento": ficha.sha256_documento,
                        "editorial_review": ficha.editorial_review,
                        "habilidades_homologadas": False,
                    }
                ):
                    raise FonteDivergente("CA/PV/proveniência da ficha restaurada divergem")

        fresh = MotorFichasPOC(
            registros, referencias=refs, contrato=contrato,
            checkout_catalogo=checkout_catalogo,
            primeiro=antigo.state["prioridade_preparacao"]["primeiro"],
            exigir_revisao=exigir_revisao,
        )
        fresh.state = antigo.state
        fresh.events = antigo.events
        fresh.rejections = antigo.rejections
        fresh.responses = antigo.responses
        fresh.head_hash = antigo.head_hash
        fresh.validate()
        return cls(fresh, registros, tuple(refs), copy.deepcopy(dict(prov)),
                   copy.deepcopy(dict(contrato)), digest(registros))

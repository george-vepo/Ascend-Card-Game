"""Duelo Giant Owl × Gibbering Mouther com fichas externas confirmadas.

Integra, em fixtures isoladas, o leitor do Catálogo SRD ao módulo v2.4
de condições e ataques limitados. NÃO é combate SRD completo nem partida oficial.
Nunca cria sorteio, usa dados não fornecidos ou faz ações pelo jogador.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Mapping, Sequence, Any

from ascend.catalogo_poc import CopiaReferencia
from ascend.fichas_srd import consultar_ficha, FichaPendente, FichaConflitante
from motor_fichas_poc import MotorFichasPOC, SessaoFichasFixture
from motor_condicoes_srd import MotorCondicoesSRD
from motor_poc import (
    MotorPOC, InvalidAction, UnresolvedRule, SIDES,
)

PARES = {"J1": "CE-001", "J2": "AB-POC-008"}
ESCOPO = "EFEITOS_SRD_PARCIAIS_TESTE"

# Reconhecimentos mínimos vindos dos textos integrais, não são ficha
# alternativa; divergência do Catálogo suspende somente este combate.
FRASES_OBRIGATORIAS = {
    "CE-001": (
        "Large Celestial",
        "Talons. Melee Attack Roll: +4, reach 5 ft.",
        "Hit: 7 (1d10 + 2) Slashing damage.",
        "Resistances Necrotic, Radiant",
        "Flyby.",
        "Spellcasting.",
    ),
    "AB-POC-008": (
        "Medium Aberration",
        "Gibbering.",
        "Wisdom Saving Throw: DC 10",
        "Bite. Melee Attack Roll: +2, reach 5 ft.",
        "Hit: 7 (2d6) Piercing damage.",
        "Blinding Spittle (Recharge 5–6).",
        "Dexterity Saving Throw: DC 10",
    ),
}


class MotorCombateFichasSRD(MotorFichasPOC, MotorCondicoesSRD):
    """Mesmo estado event-sourced do motor de preparo; combate parcial v2.4."""

    def _get_combat_pair(self, s):
        for jogador, cid in PARES.items():
            if s["jogadores"][jogador]["criatura_ativa_id"] != cid:
                raise UnresolvedRule(
                    "combate integrado só cobre Giant Owl × Gibbering Mouther"
                )
            card = self.get_card(s, jogador, cid)
            origem = card.get("origem_ficha")
            if not origem:
                raise UnresolvedRule("criatura ativa sem ficha consultada")
            try:
                ficha = consultar_ficha(
                    self.checkout_catalogo, self.contrato,
                    self.referencias, cid,
                    exigir_revisao=self.exigir_revisao,
                )
            except (FichaPendente, FichaConflitante) as exc:
                raise UnresolvedRule("ficha de combate pendente: "+str(exc)) from exc
            esperado = {
                "id_catalogo": ficha.id_catalogo,
                "versao": ficha.versao,
                "revisao_git": ficha.revisao_git,
                "sha256_documento": ficha.sha256_documento,
                "editorial_review": ficha.editorial_review,
                "habilidades_homologadas": False,
            }
            if (origem != esperado
                or card.get("ca_fonte") != ficha.ca
                or card.get("pv_max") != ficha.pv_maximos):
                raise UnresolvedRule("CA/PV/identidade ou hash da ficha divergiu")
            texto = " ".join(ficha.ficha_integral.split())
            if any(frase not in texto for frase in FRASES_OBRIGATORIAS[cid]):
                raise UnresolvedRule(
                    "ação, resistência ou traço ausente na ficha consultada"
                )
        return super()._get_combat_pair(s)

    def _transition(self, s, actor, command, params):
        if command == "ATAQUE_V24_TESTE":
            reach = params.get("alvo_no_alcance_fixture")
            if type(reach) is not bool:
                raise UnresolvedRule(
                    "alcance do ataque não estabelecido: confirmar fixture"
                )
            if not reach:
                raise InvalidAction("alvo fora do alcance confirmado em fixture")
        return super()._transition(s, actor, command, params)

    def checkpoint(self):
        """Formato v2.2 base para restauração verificável da camada integrada.

        A origem/estado de cada ficha é adicionalmente conferida na sessão.
        Contém dados ocultos: não exportar para locais públicos.
        """
        return MotorPOC.checkpoint(self)


class SessaoCombateFichasFixture(SessaoFichasFixture):
    """Fábrica de combate parcial, explicitamente isolada de partida oficial."""

    @classmethod
    def _promover(cls, original: SessaoFichasFixture) -> "SessaoCombateFichasFixture":
        m = original.motor
        motor = MotorCombateFichasSRD(
            original.registros,
            referencias=original.referencias,
            contrato=original.contrato,
            checkout_catalogo=m.checkout_catalogo,
            primeiro=m.state["prioridade_preparacao"]["primeiro"],
            exigir_revisao=m.exigir_revisao,
        )
        # Construímos de novo com as mesmas 80 identidades, e só então
        # transferimos estado/eventos previamente validados.
        motor.state = copy.deepcopy(m.state)
        motor.events = copy.deepcopy(m.events)
        motor.rejections = copy.deepcopy(m.rejections)
        motor.responses = copy.deepcopy(m.responses)
        motor.head_hash = m.head_hash
        motor.validate()
        return cls(
            motor=motor,
            registros=copy.deepcopy(original.registros),
            referencias=tuple(original.referencias),
            proveniencia=copy.deepcopy(original.proveniencia),
            contrato=copy.deepcopy(original.contrato),
            hash_identidades=original.hash_identidades,
        )

    @classmethod
    def criar_de_checkout(
        cls,
        checkout_catalogo: str | Path,
        contrato: Mapping[str, Any],
        *,
        primeiro: str = "J1",
        maos_fixadas: dict[str, list[str]] | None = None,
    ) -> "SessaoCombateFichasFixture":
        s = SessaoFichasFixture.criar_de_checkout(
            checkout_catalogo, contrato,
            primeiro=primeiro, maos_fixadas=maos_fixadas,
        )
        return cls._promover(s)

    @classmethod
    def restaurar(
        cls, checkpoint: dict,
        checkout_catalogo: str | Path,
        contrato: Mapping[str, Any],
        *,
        exigir_revisao: bool = True,
        referencias_fixture: Sequence[CopiaReferencia] | None = None,
        proveniencia_fixture: Mapping[str, Any] | None = None,
    ) -> "SessaoCombateFichasFixture":
        s = SessaoFichasFixture.restaurar(
            checkpoint, checkout_catalogo, contrato,
            exigir_revisao=exigir_revisao,
            referencias_fixture=referencias_fixture,
            proveniencia_fixture=proveniencia_fixture,
        )
        result = cls._promover(s)
        if (result.motor.state["fase"] == "COMBATE"
            and result.motor.state["combate"].get("v24") is not None):
            result.motor._get_combat_pair(result.motor.state)
        return result

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
from motor_base_v22 import (
    InvalidAction as InvalidActionV22,
    UnresolvedRule as UnresolvedRuleV22,
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
        "7–8. The target makes a melee attack against a randomly determined creature within its reach",
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

    def _iniciar_gibbering_78(self, s, actor, params):
        """SRD 5.2.1, p.288: 7-8 força ataque em criatura no alcance.

        Na POC existem dois combatentes; havendo apenas o Mouther elegível,
        ele é o único alvo possível. A geometria NÃO é inferida: o árbitro
        precisa informar explicitamente a elegibilidade do alvo.
        """
        v = MotorCondicoesSRD._ready(self, s, actor)
        self._get_combat_pair(s)
        if actor != "J1" or not v["pendente_inicio"]:
            raise InvalidAction("Gibbering 7–8 só no início do turno da Giant Owl")
        if params.get("aceite_escopo") != ESCOPO:
            raise UnresolvedRule("escopo parcial de combate deve ser aceito")
        if params.get("gibbering_aplicavel_fixture") is not True:
            raise InvalidAction("rolagem 7–8 exige gatilho Gibbering confirmado")
        wis = params.get("wis_d20_simulado")
        d8 = params.get("gibbering_d8_simulado")
        if not self._die(wis, 20) or wis + 4 >= 10:
            raise InvalidAction("resultado 7–8 requer falha real em SAB CD 10")
        if type(d8) is not int or d8 not in (7, 8):
            raise InvalidAction("somente resultados 7 e 8 deste evento")
        ao_alcance = params.get("mouther_ao_alcance_fixture")
        if type(ao_alcance) is not bool:
            raise UnresolvedRule("confirmar se o único alvo externo está a até 5 pés")

        # Aplicamos ao estado PROPOSTO pelo motor: nada é gravado se uma
        # pré-condição, fonte ou dado simulado falhar.
        v["turnos_iniciados"]["J1"] += 1
        v["pendente_inicio"] = False
        v["inicio_resolvido"] = True
        v["bloqueado"] = True  # impede ataque voluntário no mesmo turno
        v["ataque_forcado"] = (
            {"ator": "J1", "alvo": "AB-POC-008", "ataque": "Talons",
             "d8": d8} if ao_alcance else None
        )
        v["gibbering_sem_alvo"] = not ao_alcance
        return {
            "ator": "J1", "dados_simulados": True,
            "numero_turno_proprio": v["turnos_iniciados"]["J1"],
            "gibbering_sab": {"d20": wis, "bonus": 4, "total": wis + 4,
                              "cd": 10, "sucesso": False},
            "gibbering_resultado_d8": d8,
            "mouther_ao_alcance_fixture": ao_alcance,
            "acao_exigida": ("RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE"
                             if ao_alcance else "PASSAR_TURNO_V24_TESTE"),
            "alvo_unico_elegivel": "AB-POC-008" if ao_alcance else None,
            "alvo_sorteado": False,  # um único elegível dispensa sorteio
            "turno_com_acao_livre": False,
        }

    def _resolver_gibbering_78(self, s, actor, params):
        v = MotorCondicoesSRD._ready(self, s, actor)
        members = self._get_combat_pair(s)
        forcado = v.get("ataque_forcado")
        if (actor != "J1" or not v["inicio_resolvido"]
                or not isinstance(forcado, dict)
                or forcado.get("alvo") != "AB-POC-008"):
            raise InvalidAction("não há ataque forçado pendente para este turno")
        if params.get("aceite_escopo") != ESCOPO:
            raise UnresolvedRule("confirmar escopo mecânico parcial")
        if params.get("alvo_id") != "AB-POC-008":
            raise InvalidAction("o alvo é o único inimigo elegível, AB-POC-008")
        if params.get("ataque") != "Talons":
            raise InvalidAction("a única ação corpo a corpo da coruja é Talons")

        src = members["J1"][1]
        target = members["J2"][1]
        atk = src["attack"]
        owl_card = self.get_card(s, "J1", "CE-001")
        mouther_card = self.get_card(s, "J2", "AB-POC-008")
        # Reutiliza a regra SRD de Blinded; vantagem/desvantagem se cancelam.
        own_blind = "Blinded" in owl_card["condicoes"]
        target_blind = "Blinded" in mouther_card["condicoes"]
        modo = ("NORMAL" if own_blind == target_blind else
                "DESVANTAGEM" if own_blind else "VANTAGEM")
        rolls = params.get("d20_simulados")
        quantidade = 1 if modo == "NORMAL" else 2
        if (not isinstance(rolls, list) or len(rolls) != quantidade or
                not all(self._die(x, 20) for x in rolls)):
            raise InvalidAction(f"{modo}: exige {quantidade} d20 simulado(s)")
        d20 = (min(rolls) if modo == "DESVANTAGEM" else
               max(rolls) if modo == "VANTAGEM" else rolls[0])
        total = d20 + atk["bonus"]
        critico = d20 == 20
        acertou = critico or (d20 != 1 and total >= target["ac"])
        quantidade_dano = atk["dice"][0] * (2 if critico else 1) if acertou else 0
        dice = params.get("dano_dados", [])
        if (not isinstance(dice, list) or len(dice) != quantidade_dano
                or not all(self._die(x, atk["dice"][1]) for x in dice)):
            raise InvalidAction(
                f"Talons: exige {quantidade_dano} d10 simulados para este resultado"
            )
        bruto = sum(dice) + atk["flat"] if acertou else 0
        if atk["type"] in target["immunities"]:
            aplicado = 0
        elif atk["type"] in target["resistances"]:
            aplicado = bruto // 2
        else:
            aplicado = bruto
        antes = mouther_card["pv_atual"]
        mouther_card["pv_atual"] = max(0, antes - aplicado)
        # Ataque forçado consome a resolução do turno neste recorte.
        v["ataque_forcado"] = None
        v["gibbering_sem_alvo"] = False
        result = {
            "gatilho": "Gibbering d8 7–8",
            "ator": "J1", "alvo": "J2", "carta_alvo": "AB-POC-008",
            "ataque": "Talons", "seleção_alvo": "UNICO_ELEGIVEL",
            "origem_dados": "DADOS_SIMULADOS_TESTE",
            "gibbering_d8": forcado["d8"],
            "modo_rolagem": modo, "d20_simulados": list(rolls),
            "d20_aplicado": d20, "bonus_ataque": atk["bonus"],
            "total_ataque": total, "ca_alvo": target["ac"],
            "acertou": acertou, "critico": critico, "dados_dano": list(dice),
            "dano_bruto": bruto, "dano_aplicado": aplicado,
            "pv_antes": antes, "pv_depois": mouther_card["pv_atual"],
            "turno_com_acao_livre": False,
        }
        if mouther_card["pv_atual"] == 0:
            self._ko(s, "J1", "FIXTURE_SRD_GIBBERING_78_ALVO_UNICO")
            result["ko"] = True
        else:
            result.update(MotorCondicoesSRD._finish_turn(self, s, actor))
            result["ko"] = False
        return result

    def _transition(self, s, actor, command, params):
        if (command == "INICIO_TURNO_V24_TESTE" and actor == "J1"
                and params.get("gibbering_d8_simulado") in (7, 8)):
            return self._iniciar_gibbering_78(s, actor, params)
        if command == "RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE":
            return self._resolver_gibbering_78(s, actor, params)
        v = s.get("combate", {}).get("v24")
        if v and v.get("ataque_forcado"):
            if command in {
                "ATAQUE_V24_TESTE", "PASSAR_TURNO_V24_TESTE",
                "INICIO_TURNO_V24_TESTE",
            }:
                raise InvalidAction(
                    "resolver primeiro o ataque forçado de Gibbering"
                )
        if (v and v.get("gibbering_sem_alvo")
                and command == "PASSAR_TURNO_V24_TESTE"):
            result = MotorCondicoesSRD._transition(
                self, s, actor, command, params
            )
            v["gibbering_sem_alvo"] = False
            result["passou_por"] = "Gibbering 7–8 sem alvo ao alcance"
            return result
        # As versões v2.2/v2.3 carregam MotorPOC de módulos Python distintos
        # (motor_poc versus motor_base_v22). Um super() linear aqui desviaria
        # iniciativa/ataque para a implementação base, "comando desconhecido".
        # Roteamos explicitamente SOMENTE as ações do recorte já testado.
        combate = {
            "INICIATIVA_SRD_TESTE",
            "INICIO_TURNO_V24_TESTE",
            "ATAQUE_V24_TESTE",
            "BLINDING_SPITTLE_V24_TESTE",
            "PASSAR_TURNO_V24_TESTE",
            # atalhos legados permanecem proibidos pelo módulo v2.4
            "ATAQUE_SRD_TESTE", "INICIATIVA_FIXTURE",
            "RODADA_SEGUINTE_FIXTURE", "KO_COMBATE_FIXTURE",
        }
        if command in combate:
            if command == "ATAQUE_V24_TESTE":
                reach = params.get("alvo_no_alcance_fixture")
                if type(reach) is not bool:
                    raise UnresolvedRule(
                        "alcance do ataque não estabelecido: confirmar fixture"
                    )
                if not reach:
                    raise InvalidAction(
                        "alvo fora do alcance confirmado em fixture"
                    )
            try:
                return MotorCondicoesSRD._transition(self, s, actor, command, params)
            except UnresolvedRuleV22 as exc:
                # Compatibilidade: a v2.4 usa outro objeto de classe-base.
                # A API nova preserva PENDENTE sem mutar o estado.
                raise UnresolvedRule(str(exc)) from exc
            except InvalidActionV22 as exc:
                raise InvalidAction(str(exc)) from exc
        return MotorFichasPOC._transition(self, s, actor, command, params)

    def public(self):
        data = MotorCondicoesSRD.public(self)
        v = self.state.get("combate", {}).get("v24")
        if v is not None and self.state.get("fase") == "COMBATE":
            data.setdefault("efeitos_combate", {})["gibbering_forcado"] = (
                "ATAQUE_TALONS_PENDENTE"
                if v.get("ataque_forcado") else
                "SEM_ALVO_PASSAR_TURNO"
                if v.get("gibbering_sem_alvo") else None
            )
        return data

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

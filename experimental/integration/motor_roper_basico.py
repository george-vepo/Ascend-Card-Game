"""Terceira criatura SRD: duelo de Bite isolado Roper × Giant Owl.

NÃO é combate SRD completo: Tentacle, Reel, Multiattack, Spider Climb, Flyby,
movimento, recursos e magias continuam sem resolução neste recorte.
Somente cópias com ficha verificada no Catálogo SRD pinado.
Dados e alcance são informados externamente em fixtures, sem RNG.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

from ascend.catalogo_poc import CopiaReferencia
from ascend.fichas_srd import consultar_ficha, FichaPendente, FichaConflitante
from ascend.perfil_combate_srd import extrair_perfil_de_combate
from motor_poc import MotorPOC, InvalidAction, UnresolvedRule, SIDES, other
from motor_fichas_poc import MotorFichasPOC, SessaoFichasFixture

ESCOPO_BASICO = "ATAQUE_INDIVIDUAL_SEM_MULTIATAQUE_OU_PASSIVOS"
DUELO_ROPER = {"J1": "CE-001", "J2": "AB-POC-017"}


class MotorRoperBasico(MotorFichasPOC):
    """Iniciativa e um ataque corpo a corpo por turno em fixture isolada."""

    def _perfis(self, estado: dict) -> dict[str, tuple[str, dict]]:
        perfis = {}
        for jogador, id_copia in DUELO_ROPER.items():
            card = self.get_card(estado, jogador, id_copia)
            if estado["jogadores"][jogador]["criatura_ativa_id"] != id_copia:
                raise UnresolvedRule("este confronto só abrange Giant Owl × Roper")
            if card["condicoes"] or card["efeitos"]:
                raise UnresolvedRule(
                    "condições/efeitos não resolvidos neste recorte básico"
                )
            if self.exigir_revisao:
                from motor_fichas_poc import conferir_checkout_sem_modificacoes
                conferir_checkout_sem_modificacoes(self.checkout_catalogo)
            try:
                ficha = consultar_ficha(
                    self.checkout_catalogo, self.contrato, self.referencias,
                    id_copia, exigir_revisao=self.exigir_revisao,
                )
                perfil = extrair_perfil_de_combate(ficha)
            except (FichaPendente, FichaConflitante) as exc:
                raise UnresolvedRule("ficha/perfil SRD pendente: " + str(exc)) from exc
            esperado = {
                "id_catalogo": ficha.id_catalogo,
                "versao": ficha.versao,
                "revisao_git": ficha.revisao_git,
                "sha256_documento": ficha.sha256_documento,
                "editorial_review": ficha.editorial_review,
                "habilidades_homologadas": False,
            }
            if (card.get("origem_ficha") != esperado
                    or card.get("ca_fonte") != perfil["ac"]
                    or card.get("pv_max") != perfil["hp"]
                    or card.get("nome") != perfil["name"]):
                raise UnresolvedRule("identidade, CA, PV ou hash da ficha divergiu")
            if perfil["attack"]["name"] != (
                    "Talons" if jogador == "J1" else "Bite"):
                raise UnresolvedRule("ação da ficha não reconhecida para este recorte")
            perfis[jogador] = (id_copia, perfil)
        return perfis

    @staticmethod
    def _dado(valor, faces):
        return type(valor) is int and 1 <= valor <= faces

    def _transition(self, s, actor, command, params):
        if command == "INICIATIVA_ROPER_TESTE":
            if actor != "ARBITRO" or s["fase"] != "INICIATIVA":
                raise InvalidAction("iniciativa fora da fase ou sem árbitro")
            if params.get("aceite_escopo") != ESCOPO_BASICO:
                raise UnresolvedRule("aceitar limitações do combate básico")
            pair = self._perfis(s)
            rolls = params.get("d20_simulados")
            if (not isinstance(rolls, dict) or set(rolls) != set(SIDES)
                    or not all(self._dado(v, 20) for v in rolls.values())):
                raise InvalidAction("dois dados d20 simulados são obrigatórios")
            values = {p: rolls[p] + pair[p][1]["initiative"] for p in SIDES}
            if values["J1"] == values["J2"]:
                raise UnresolvedRule("iniciativa empatada sem desempate aprovado")
            order = sorted(SIDES, key=lambda p: values[p], reverse=True)
            combat = s["combate"]
            combat["iniciativas"] = {
                **values, "rolagens": copy.deepcopy(rolls),
                "modificadores": {p: pair[p][1]["initiative"] for p in SIDES},
                "origem": "DADOS_SIMULADOS_TESTE",
            }
            combat["ordem_turnos"] = order
            combat["indice_turno"] = 0
            combat["rodada"] = 1
            combat["mecanicas_nao_implementadas"] = {
                p: pair[p][1]["limitations"] for p in SIDES
            }
            s["fase"] = "COMBATE"
            s["ator_da_vez"] = order[0]
            return {
                "ordem": order, "totais": values,
                "d20_simulados": copy.deepcopy(rolls),
                "escopo": ESCOPO_BASICO,
                "habilidades_completas": False,
                "mecanicas_nao_implementadas": copy.deepcopy(
                    combat["mecanicas_nao_implementadas"]
                ),
            }

        if command == "ATAQUE_ROPER_BASICO_TESTE":
            if actor not in SIDES:
                raise InvalidAction("ataque exige controlador de criatura")
            self._gate(s, "COMBATE", actor)
            if params.get("aceite_escopo") != ESCOPO_BASICO:
                raise UnresolvedRule("escopo de ataque individual não confirmado")
            reach = params.get("alvo_no_alcance_fixture")
            if type(reach) is not bool:
                raise UnresolvedRule("alcance precisa de confirmação explícita")
            if not reach:
                raise InvalidAction("alvo fora de alcance confirmado")
            pair = self._perfis(s)
            own_id, own = pair[actor]
            defender = other(actor)
            target_id, target = pair[defender]
            attack = own["attack"]
            if params.get("ataque") != attack["name"]:
                raise InvalidAction("apenas a ação de ataque documentada é permitida")
            d20 = params.get("d20_simulado")
            if not self._dado(d20, 20):
                raise InvalidAction("d20 simulado inválido")
            natural20 = d20 == 20
            total = d20 + attack["bonus"]
            hit = natural20 or (d20 != 1 and total >= target["ac"])
            ndice = attack["dice"][0] * (2 if natural20 else 1) if hit else 0
            dice = params.get("dano_dados", [])
            if (not isinstance(dice, list) or len(dice) != ndice or
                    not all(self._dado(x, attack["dice"][1]) for x in dice)):
                raise InvalidAction(
                    f"exigir {ndice} d{attack['dice'][1]} simulados"
                )
            base_damage = max(0, sum(dice) + attack["flat"]) if hit else 0
            if attack["type"] in target["immunities"]:
                damage = 0
            elif attack["type"] in target["resistances"]:
                damage = base_damage // 2
            else:
                damage = base_damage
            victim = self.get_card(s, defender, target_id)
            before = victim["pv_atual"]
            victim["pv_atual"] = max(0, before - damage)
            result = {
                "ator": actor, "carta_origem": own_id,
                "alvo": defender, "carta_alvo": target_id,
                "ataque": attack["name"], "tipo_dano": attack["type"],
                "d20_simulado": d20, "bonus": attack["bonus"],
                "total_ataque": total, "ca_alvo": target["ac"],
                "critico": natural20, "acertou": hit,
                "dados_dano_simulados": list(dice),
                "modificador_dano": attack["flat"] if hit else 0,
                "dano_bruto": base_damage, "dano_aplicado": damage,
                "pv_antes": before, "pv_depois": victim["pv_atual"],
                "origem_ficha_sha256": own["source_sha256"],
                "dados_simulados": True, "mecanica_parcial": True,
            }
            if victim["pv_atual"] == 0:
                self._ko(s, actor, "FIXTURE_SRD_ATAQUE_INDIVIDUAL")
                result["ko"] = True
                result["pontuacao_fixture"] = copy.deepcopy(s["placar"])
            else:
                combat = s["combate"]
                if combat["ordem_turnos"][combat["indice_turno"]] != actor:
                    raise InvalidAction("ordem de iniciativa divergente")
                if combat["indice_turno"] == 0:
                    combat["indice_turno"] = 1
                else:
                    combat["indice_turno"] = 0
                    combat["rodada"] += 1
                s["ator_da_vez"] = combat["ordem_turnos"][combat["indice_turno"]]
                result.update({
                    "ko": False, "proximo_ator": s["ator_da_vez"],
                    "rodada": combat["rodada"],
                })
            return result
        if command in {
            "MULTIATTACK_ROPER_TESTE", "TENTACLE_ROPER_TESTE",
            "REEL_ROPER_TESTE", "SPIDER_CLIMB_ROPER_TESTE",
        }:
            raise UnresolvedRule(
                "habilidade SRD documentada, ainda não implementada neste recorte"
            )
        return MotorFichasPOC._transition(self, s, actor, command, params)

    def public(self):
        out = MotorFichasPOC.public(self)
        if self.state.get("fase") == "COMBATE":
            for p in SIDES:
                cid = self.state["jogadores"][p]["criatura_ativa_id"]
                card = self.state["jogadores"][p]["cartas"][cid] if cid else None
                out["jogadores"][p]["campo"] = (
                    {"carta_id": cid, "nome": card["nome"],
                     "pv_atual": card["pv_atual"], "pv_max": card["pv_max"],
                     "ca": card["ca_fonte"],
                     "condicoes": copy.deepcopy(card["condicoes"])}
                    if card else None
                )
            out["mecanica_parcial"] = True
        return out


class SessaoRoperFixture(SessaoFichasFixture):
    """Estado privado de teste vinculado ao commit das fichas externas."""

    @classmethod
    def _promover(cls, original: SessaoFichasFixture):
        antigo = original.motor
        novo = MotorRoperBasico(
            original.registros, referencias=original.referencias,
            contrato=original.contrato,
            checkout_catalogo=antigo.checkout_catalogo,
            primeiro=antigo.state["prioridade_preparacao"]["primeiro"],
            exigir_revisao=antigo.exigir_revisao,
        )
        novo.state = copy.deepcopy(antigo.state)
        novo.events = copy.deepcopy(antigo.events)
        novo.rejections = copy.deepcopy(antigo.rejections)
        novo.responses = copy.deepcopy(antigo.responses)
        novo.head_hash = antigo.head_hash
        novo.validate()
        return cls(
            novo, copy.deepcopy(original.registros),
            tuple(original.referencias), copy.deepcopy(original.proveniencia),
            copy.deepcopy(original.contrato), original.hash_identidades,
        )

    @classmethod
    def criar_de_checkout(cls, checkout: str | Path, contrato: Mapping[str, Any],
                          *, primeiro="J2", maos_fixadas=None):
        source = SessaoFichasFixture.criar_de_checkout(
            checkout, contrato, primeiro=primeiro, maos_fixadas=maos_fixadas,
        )
        return cls._promover(source)

    @classmethod
    def restaurar(cls, checkpoint: dict, checkout: str | Path,
                  contrato: Mapping[str, Any]):
        base = SessaoFichasFixture.restaurar(checkpoint, checkout, contrato)
        item = cls._promover(base)
        if item.motor.state["fase"] == "COMBATE":
            item.motor._perfis(item.motor.state)
        return item

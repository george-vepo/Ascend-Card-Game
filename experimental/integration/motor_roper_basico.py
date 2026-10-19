"""Terceira criatura SRD: Bite e Tentacle isolados Roper × Giant Owl.

NÃO é combate SRD completo: Reel, Multiattack, Spider Climb, Flyby,
movimento, recursos e magias continuam sem resolução neste recorte.
Somente cópias com ficha verificada no Catálogo SRD pinado.
Dados são simulados e explícitos em fixtures, sem RNG; o jogo não usa posições ou alcance espacial.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

from ascend.catalogo_poc import CopiaReferencia
from ascend.fichas_srd import consultar_ficha, FichaPendente, FichaConflitante
from ascend.perfil_combate_srd import extrair_perfil_de_combate
from ascend.tentaculo_roper_srd import (extrair_tentaculo_roper, extrair_multiattack_roper)
from ascend.fuga_roper_srd import extrair_testes_fuga_owl
from ascend.testes_d20_srd import (
    resolver_teste_atributo, TesteD20Invalido, TesteD20Pendente,
)
from motor_poc import MotorPOC, InvalidAction, UnresolvedRule, SIDES, other
from motor_fichas_poc import MotorFichasPOC, SessaoFichasFixture

ESCOPO_BASICO = "ATAQUE_INDIVIDUAL_SEM_MULTIATAQUE_OU_PASSIVOS"
DUELO_ROPER = {"J1": "CE-001", "J2": "AB-POC-017"}


class MotorRoperBasico(MotorFichasPOC):
    """Iniciativa e um ataque corpo a corpo por turno em fixture isolada."""

    def _estado_agarrado(self, estado, card):
        """Aceita somente status originado por um Tentacle previamente validado."""
        condicoes = card["condicoes"]
        efeitos = card["efeitos"]
        slots = estado["combate"].get("tentaculos_roper", {})
        if not condicoes and not efeitos:
            if slots:
                raise UnresolvedRule("grapple no combate sem condição correspondente")
            return
        if (set(condicoes) != {"Grappled", "Poisoned"}
                or len(condicoes) != 2 or len(efeitos) != 1
                or len(slots) != 1):
            raise UnresolvedRule("condições fora do recorte Tentacle não homologadas")
        key, registro = next(iter(slots.items()))
        efeito = efeitos[0]
        if (type(key) is not str or not key.isdigit()
                or not 1 <= int(key) <= 6
                or not isinstance(registro, dict)
                or registro.get("alvo_id") != "CE-001"
                or registro.get("origem_id") != "AB-POC-017"
                or efeito != {
                    "tipo": "ROPER_TENTACLE_GRAPPLE",
                    "fonte": "AB-POC-017",
                    "alvo_id": "CE-001",
                    "tentaculo": int(key),
                    "condicoes": ["Grappled", "Poisoned"],
                    "escape_dc": efeito.get("escape_dc"),
                    "sha256_documento": registro.get("sha256_documento"),
                }):
            raise UnresolvedRule("vínculo entre tentáculo, efeito e alvo divergente")

    def validate(self, s=None):
        """Impede deixar Grappled/Poisoned e tentáculos órfãos entre combates."""
        result=super().validate(s)
        estado=self.state if s is None else s
        if estado["fase"] in ("POS_COMBATE","ENCERRADA"):
            combat=estado["combate"]
            if combat.get("tentaculos_roper") or combat.get("tentaculos_destruidos"):
                raise InvalidAction("tentáculos não podem persistir após KO")
            for lado in SIDES:
                for card in estado["jogadores"][lado]["cartas"].values():
                    if any(e.get("tipo")=="ROPER_TENTACLE_GRAPPLE"
                           for e in card["efeitos"]):
                        raise InvalidAction("efeito de Grapple órfão após KO")
        return result

    def _ko(self, s, winner, source):
        """No KO, desfaz vínculos desta fixture antes de mover a criatura.

        Tanto a queda do Roper (fonte incapacitada) quanto a da Owl
        terminam o confronto; não manter um alvo agarrado sem combate.
        """
        if s["fase"]!="COMBATE":
            raise InvalidAction("limpeza do Roper só é válida em combate")
        self._perfis(s)  # Confere ficha/estado de tentáculos antes do encerramento.
        combat=s["combate"]
        ativos=sorted(int(k) for k in combat.get("tentaculos_roper",{}))
        if len(ativos)>1:
            raise UnresolvedRule("múltiplos tentáculos não implementados neste recorte")
        if ativos:
            self._libertar_tentaculo(s,ativos[0])
        destruidos=sorted(int(k) for k in combat.get("tentaculos_destruidos",{}))
        combat.pop("tentaculos_destruidos",None)
        MotorFichasPOC._ko(self,s,winner,source)
        return {
            "tentaculos_soltos":ativos,
            "tentaculos_destruidos_encerrados":destruidos,
            "condicoes_removidas":(["Grappled","Poisoned"] if ativos else []),
        }

    def _proximo_turno(self, estado, actor):
        combate = estado["combate"]
        if combate["ordem_turnos"][combate["indice_turno"]] != actor:
            raise InvalidAction("ordem de iniciativa inconsistente")
        if combate["indice_turno"] == 0:
            combate["indice_turno"] = 1
        else:
            combate["indice_turno"] = 0
            combate["rodada"] += 1
        estado["ator_da_vez"] = combate["ordem_turnos"][combate["indice_turno"]]
        regenerados=[]
        # Ficha SRD: tentáculo destruído volta no INÍCIO do próximo turno
        # do Roper, não imediatamente após ser destruído.
        if estado["ator_da_vez"]=="J2":
            regenerados=sorted(int(k) for k in combate.pop("tentaculos_destruidos",{}))
        return {
            "proximo_ator":estado["ator_da_vez"],
            "rodada":combate["rodada"],
            "tentaculos_regenerados":regenerados,
        }

    def _perfis(self, estado: dict) -> dict[str, tuple[str, dict]]:
        perfis = {}
        for jogador, id_copia in DUELO_ROPER.items():
            card = self.get_card(estado, jogador, id_copia)
            if estado["jogadores"][jogador]["criatura_ativa_id"] != id_copia:
                raise UnresolvedRule("este confronto só abrange Giant Owl × Roper")
            if jogador == "J1":
                self._estado_agarrado(estado, card)
            elif card["condicoes"] or card["efeitos"]:
                raise UnresolvedRule("Roper com condições/efeitos não integrados")
            if self.exigir_revisao:
                from motor_fichas_poc import conferir_checkout_sem_modificacoes
                conferir_checkout_sem_modificacoes(self.checkout_catalogo)
            try:
                ficha = consultar_ficha(
                    self.checkout_catalogo, self.contrato, self.referencias,
                    id_copia, exigir_revisao=self.exigir_revisao,
                )
                perfil = extrair_perfil_de_combate(ficha)
                if jogador == "J2":
                    perfil["tentaculo"] = extrair_tentaculo_roper(ficha)
                    perfil["multiattack"] = extrair_multiattack_roper(ficha)
                else:
                    perfil["testes_fuga"] = extrair_testes_fuga_owl(ficha)
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
        slots = estado["combate"].get("tentaculos_roper", {})
        regra=perfis["J2"][1]["tentaculo"]
        ref = regra["sha256_documento"]
        for key,entry in slots.items():
            if (not isinstance(entry,dict) or entry.get("sha256_documento")!=ref
                    or type(entry.get("pv_atual")) is not int
                    or not 1<=entry["pv_atual"]<=regra["tentaculo"]["pv"]
                    or entry.get("pv_max")!=regra["tentaculo"]["pv"]):
                raise UnresolvedRule("tentáculo ocupado sem PV/fonte verificáveis")
        destruidos=estado["combate"].get("tentaculos_destruidos",{})
        if not isinstance(destruidos,dict):
            raise UnresolvedRule("registro de destruição deve ser um mapa")
        for key,entry in destruidos.items():
            if (type(key) is not str or not key.isdigit()
                    or not 1<=int(key)<=regra["quantidade_tentaculos"]
                    or str(int(key))!=key or key in slots
                    or not isinstance(entry,dict)
                    or set(entry)!={"sha256_documento"}
                    or entry["sha256_documento"]!=ref):
                raise UnresolvedRule("registro de tentáculo destruído inconsistente")
        if slots:
            card= self.get_card(estado,"J1","CE-001")
            if card["efeitos"][0].get("escape_dc")!=regra["escape_dc"]:
                raise UnresolvedRule("CD de fuga diverge da ficha Tentacle")
        return perfis

    def _libertar_tentaculo(self,estado,slot):
        """Libera alvo e recurso, preservando o estado transacional."""
        owl=self.get_card(estado,"J1","CE-001")
        slots=estado["combate"].get("tentaculos_roper",{})
        if str(slot) not in slots:
            raise InvalidAction("tentáculo não ocupa este slot")
        self._estado_agarrado(estado,owl)
        # Exclusivamente o efeito atual do recorte é removido.
        if (len(owl["efeitos"])!=1
                or owl["efeitos"][0].get("tentaculo")!=slot):
            raise UnresolvedRule("efeito Tentacle incompatível com o slot")
        owl["efeitos"]=[]
        owl["condicoes"]=[]
        slots.pop(str(slot))
        if not slots:
            estado["combate"].pop("tentaculos_roper",None)

    @staticmethod
    def _dado(valor, faces):
        return type(valor) is int and 1 <= valor <= faces

    def prevalidar_reel(self) -> dict:
        """Consulta pública e sem mutação da mecânica Reel.

        A regra vigente da POC elimina movimento e posição espacial.
        Com Grappled válido, Reel é uma Action sem deslocamento nem dano.
        """
        s = self.state
        result = {
            "acao": "REEL_ROPER_TESTE",
            "estado": "INAPLICAVEL",
            "executavel": False,
            "consome_acao": False,
            "alvos": [],
            "dados_necessarios": [],
            "lacuna": None,
        }
        if s.get("fase") != "COMBATE":
            return result
        if s.get("ator_da_vez") != "J2":
            return result
        perfis = self._perfis(s)
        regra = perfis["J2"][1]["tentaculo"]["reel"]
        slots = s["combate"].get("tentaculos_roper", {})
        result["distancia_maxima_ft"] = regra["distancia_maxima_ft"]
        result["origem_ficha_sha256"] = perfis["J2"][1]["tentaculo"]["sha256_documento"]
        if not slots:
            result["estado"] = "SEM_ALVO_AGARRADO"
            return result
        if len(slots) != 1:
            raise UnresolvedRule("múltiplos alvos ainda não homologados")
        slot, data = next(iter(slots.items()))
        if (not slot.isdigit() or not 1 <= int(slot) <= 6
                or data.get("origem_id") != "AB-POC-017"
                or data.get("alvo_id") != "CE-001"):
            raise UnresolvedRule("tentáculo e alvo inválidos para Reel")
        result["estado"] = "PRONTO_SEM_POSICIONAMENTO"
        result["executavel"] = True
        result["alvos"] = [{
            "carta_id": "CE-001",
            "tentaculo_numero": int(slot),
            "condicoes": ["Grappled", "Poisoned"],
        }]
        result["dados_necessarios"] = []
        result["efeito_espacial_aplicado"] = False
        result["regra_poc"] = "SEM_POSICIONAMENTO_15_10_2026"
        result["lacuna"] = None
        return result

    def prevalidar_multiattack(self) -> dict:
        """Consulta SRD em ordem, sem executar ataques nem consumir Action.

        A ficha exige duas Tentacle, Reel e duas Bite na mesma Action.
        A POC ignora alcance espacial; continuam pendentes as múltiplas
        Tentacle em um alvo e a composição na economia de uma Action.
        """
        s = self.state
        result = {
            "acao": "MULTIATTACK_ROPER_TESTE",
            "estado": "INAPLICAVEL",
            "executavel": False,
            "consome_acao": False,
            "etapas": [],
            "bloqueios": [],
            "lacuna": None,
        }
        if s.get("fase") != "COMBATE" or s.get("ator_da_vez") != "J2":
            return result
        perfil = self._perfis(s)["J2"][1]
        multi = perfil["multiattack"]
        result["etapas"] = copy.deepcopy(multi["etapas"])
        result["origem_ficha_sha256"] = multi["sha256_documento"]
        result["tipo_acao_fonte"] = multi["tipo_acao"]
        result["estado"] = "PENDENTE_COMPONENTES"
        result["bloqueios"] = [
            "segunda_Tentacle_e_alvo_ja_agarrado_sem_regra_integrada",
            "economia_de_acao_composta_nao_integrada",
        ]
        result["lacuna"] = (
            "Multiattack verificado na ficha, mas não executável: "
            "falta integrar segunda Tentacle no alvo e executar a sequência "
            "completa como uma única Action; não existe alcance espacial na POC"
        )
        return result

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
            pair = self._perfis(s)
            own_id, own = pair[actor]
            defender = other(actor)
            target_id, target = pair[defender]
            attack = own["attack"]
            if params.get("ataque") != attack["name"]:
                raise InvalidAction("apenas a ação de ataque documentada é permitida")
            poisoned = actor == "J1" and "Poisoned" in (
                self.get_card(s, actor, own_id)["condicoes"]
            )
            if poisoned:
                rolagens = params.get("d20_simulados")
                if not isinstance(rolagens, list) or len(rolagens)!=2 or not all(
                    self._dado(x, 20) for x in rolagens
                ):
                    raise UnresolvedRule("Poisoned exige dois d20 externos para desvantagem")
                d20 = min(rolagens)
            else:
                d20 = params.get("d20_simulado")
                if not self._dado(d20, 20):
                    raise InvalidAction("d20 simulado inválido")
                rolagens = [d20]
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
                "d20_simulado": d20, "d20_recebidos":copy.deepcopy(rolagens),
                "modo_rolagem":"DESVANTAGEM" if poisoned else "NORMAL",
                "bonus": attack["bonus"],
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
                encerramento=self._ko(s, actor, "FIXTURE_SRD_ATAQUE_INDIVIDUAL")
                result["encerramento_tentaculos"]=encerramento
                result["ko"] = True
                result["pontuacao_fixture"] = copy.deepcopy(s["placar"])
            else:
                result["ko"]=False
                result.update(self._proximo_turno(s,actor))
            return result
        if command == "TENTACLE_ROPER_TESTE":
            if actor != "J2":
                raise InvalidAction("Tentacle pertence ao Roper do J2")
            self._gate(s,"COMBATE",actor)
            if params.get("aceite_escopo") != ESCOPO_BASICO:
                raise UnresolvedRule("escopo parcial de Tentacle não confirmado")
            pair=self._perfis(s)
            source=pair["J2"][1]["tentaculo"]
            slot=params.get("tentaculo_numero")
            if type(slot) is not int or not 1 <= slot <= source["quantidade_tentaculos"]:
                raise InvalidAction("selecionar tentáculo entre 1 e 6")
            ocupado=s["combate"].get("tentaculos_roper",{})
            if str(slot) in ocupado:
                raise InvalidAction("tentáculo já mantém alvo agarrado")
            if str(slot) in s["combate"].get("tentaculos_destruidos",{}):
                raise InvalidAction("tentáculo destruído só volta no próximo turno Roper")
            if ocupado:
                raise UnresolvedRule("múltiplos tentáculos no mesmo alvo ainda não tratados")
            roll=params.get("d20_simulado")
            if not self._dado(roll,20):
                raise InvalidAction("rolagem de ataque d20 simulada obrigatória")
            atk=source["bonus_ataque"]
            ca=pair["J1"][1]["ac"]
            acerto=roll == 20 or (roll != 1 and roll+atk >= ca)
            owl=self.get_card(s,"J1","CE-001")
            result={
                "ator":actor,"carta_origem":"AB-POC-017",
                "carta_alvo":"CE-001","ataque":"Tentacle",
                "tentaculo_numero":slot,"d20_simulado":roll,
                "bonus":atk,"total_ataque":roll+atk,"ca_alvo":ca,
                "acertou":acerto,"critico":roll==20,
                "dano_aplicado":0,"dados_simulados":True,
                "alcance_ft":source["alcance_ft"],
                "ficha_sha256":source["sha256_documento"],
                "mecanica_parcial":True,"reel_pendente":False,
            }
            if acerto:
                owl["condicoes"]=["Grappled","Poisoned"]
                efeito={
                    "tipo":"ROPER_TENTACLE_GRAPPLE",
                    "fonte":"AB-POC-017","alvo_id":"CE-001",
                    "tentaculo":slot,"condicoes":["Grappled","Poisoned"],
                    "escape_dc":source["escape_dc"],
                    "sha256_documento":source["sha256_documento"],
                }
                owl["efeitos"].append(efeito)
                s["combate"]["tentaculos_roper"]={
                    str(slot):{
                        "origem_id":"AB-POC-017","alvo_id":"CE-001",
                        "sha256_documento":source["sha256_documento"],
                        "pv_atual":source["tentaculo"]["pv"],
                        "pv_max":source["tentaculo"]["pv"],
                    }
                }
                result["condicoes_aplicadas"]=["Grappled","Poisoned"]
                result["escape_dc"]=source["escape_dc"]
            else:
                result["condicoes_aplicadas"]=[]
            result.update(self._proximo_turno(s,actor))
            return result
        if command == "ESCAPAR_GRAPPLE_ROPER_TESTE":
            if actor!="J1":
                raise InvalidAction("somente a criatura agarrada pode escapar")
            self._gate(s,"COMBATE",actor)
            if params.get("aceite_escopo")!=ESCOPO_BASICO:
                raise UnresolvedRule("confirmar escopo de fuga por Action")
            pair=self._perfis(s)
            slots=s["combate"].get("tentaculos_roper",{})
            if len(slots)!=1:
                raise InvalidAction("a criatura não está agarrada no recorte")
            slot_str=next(iter(slots))
            habilidade=params.get("pericia")
            mods=pair["J1"][1]["testes_fuga"]
            if habilidade not in mods:
                raise InvalidAction("escolha Athletics ou Acrobatics")
            # SRD 5.2.1: Poisoned aplica desvantagem a testes de
            # atributo, inclusive Strength (Athletics) ou Dexterity
            # (Acrobatics) para escapar de Grappled.
            if "d20_simulado" in params:
                raise UnresolvedRule(
                    "fuga requer d20_simulados: Poisoned não permite "
                    "usar um único d20 sem desvantagem"
                )
            dc=pair["J2"][1]["tentaculo"]["escape_dc"]
            owl=self.get_card(s,"J1","CE-001")
            try:
                teste=resolver_teste_atributo(
                    condicoes=owl["condicoes"],
                    dados=params.get("d20_simulados"),
                    modificador=mods[habilidade],cd=dc,
                )
            except TesteD20Pendente as exc:
                raise UnresolvedRule(str(exc)) from exc
            except TesteD20Invalido as exc:
                raise InvalidAction(str(exc)) from exc
            sucesso=teste["sucesso"]
            if sucesso:
                self._libertar_tentaculo(s,int(slot_str))
            result={
                "acao":"ESCAPAR_GRAPPLE","pericia":habilidade,
                **teste,
                "condicoes_removidas":(["Grappled","Poisoned"] if sucesso else []),
                "slot_liberado":int(slot_str) if sucesso else None,
                "mecanica_parcial":True,
            }
            result.update(self._proximo_turno(s,actor))
            return result

        if command == "ATACAR_TENTACULO_ROPER_TESTE":
            if actor!="J1":
                raise InvalidAction("apenas a Giant Owl realiza Talons nesta fixture")
            self._gate(s,"COMBATE",actor)
            if params.get("aceite_escopo")!=ESCOPO_BASICO:
                raise UnresolvedRule("confirmar escopo de ataque ao tentáculo")
            pair=self._perfis(s)
            regra=pair["J2"][1]["tentaculo"]
            slot=params.get("tentaculo_numero")
            if type(slot) is not int or not 1<=slot<=regra["quantidade_tentaculos"]:
                raise InvalidAction("slot de tentáculo inválido")
            slots=s["combate"].get("tentaculos_roper",{})
            if str(slot) not in slots:
                raise InvalidAction("não há tentáculo agarrando neste slot")
            if params.get("ataque")!="Talons":
                raise InvalidAction("somente Talons está integrado")
            owl=self.get_card(s,"J1","CE-001")
            poison="Poisoned" in owl["condicoes"]
            rolls=params.get("d20_simulados")
            expected=2 if poison else 1
            if (not isinstance(rolls,list) or len(rolls)!=expected
                    or not all(self._dado(x,20) for x in rolls)):
                raise InvalidAction("d20 externos incompatíveis com desvantagem")
            d20=min(rolls) if poison else rolls[0]
            atk=pair["J1"][1]["attack"]
            ca=regra["tentaculo"]["ca"]
            hit=d20==20 or (d20!=1 and d20+atk["bonus"]>=ca)
            critical=d20==20
            quantidade=atk["dice"][0]*(2 if critical else 1) if hit else 0
            dice=params.get("dano_dados",[])
            if (not isinstance(dice,list) or len(dice)!=quantidade
                    or not all(self._dado(x,atk["dice"][1]) for x in dice)):
                raise InvalidAction("dados de dano Talons inválidos")
            bruto=max(0,sum(dice)+atk["flat"]) if hit else 0
            if atk["type"] in regra["tentaculo"]["imunidades_dano"]:
                aplicado=0
            else:
                aplicado=bruto
            tentaculo=slots[str(slot)]
            antes=tentaculo["pv_atual"]
            tentaculo["pv_atual"]=max(0,antes-aplicado)
            destruido=tentaculo["pv_atual"]==0
            if destruido:
                self._libertar_tentaculo(s,slot)
                s["combate"].setdefault("tentaculos_destruidos",{})[str(slot)]={
                    "sha256_documento":regra["sha256_documento"]
                }
            result={
                "acao":"TALONS_TENTACULO","slot":slot,
                "d20_simulados":copy.deepcopy(rolls),"d20_aplicado":d20,
                "modo_rolagem":"DESVANTAGEM" if poison else "NORMAL",
                "bonus_ataque":atk["bonus"],"total_ataque":d20+atk["bonus"],
                "ca_tentaculo":ca,"acertou":hit,"critico":critical,
                "dano_dados_simulados":list(dice),"dano_bruto":bruto,
                "dano_aplicado":aplicado,"pv_tentaculo_antes":antes,
                "pv_tentaculo_depois":max(0,antes-aplicado),
                "destruido":destruido,
                "condicoes_removidas":(["Grappled","Poisoned"] if destruido else []),
                "pv_roper_inalterados":self.get_card(s,"J2","AB-POC-017")["pv_atual"],
                "dados_simulados":True,"mecanica_parcial":True,
            }
            result.update(self._proximo_turno(s,actor))
            return result

        if command == "REEL_ROPER_TESTE":
            if actor != "J2":
                raise InvalidAction("Reel pertence ao Roper")
            self._gate(s,"COMBATE",actor)
            diagnostico=self.prevalidar_reel()
            if diagnostico["estado"] == "SEM_ALVO_AGARRADO":
                raise UnresolvedRule("Reel exige alvo Grappled documentado")
            if diagnostico["estado"] != "PRONTO_SEM_POSICIONAMENTO":
                raise UnresolvedRule("Reel sem pré-requisitos não espaciais resolvidos")
            # Reel não causa deslocamento nesta POC, mas usa uma Action.
            # Não modifica Grappled/Poisoned, PV, zonas ou alcance de Bite.
            return {
                "acao": "Reel",
                "alvos_agarrados": copy.deepcopy(diagnostico["alvos"]),
                "deslocamento_aplicado": False,
                "regra_poc": "SEM_POSICIONAMENTO_15_10_2026",
                "dados_simulados": False,
                "mecanica_parcial": True,
                **self._proximo_turno(s, actor),
            }
        if command == "MULTIATTACK_ROPER_TESTE":
            if actor != "J2":
                raise InvalidAction("Multiattack pertence ao Roper do J2")
            self._gate(s, "COMBATE", actor)
            diagnostico = self.prevalidar_multiattack()
            raise UnresolvedRule(diagnostico["lacuna"])

        if command == "SPIDER_CLIMB_ROPER_TESTE":
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
            out["tentaculos_em_uso"] = copy.deepcopy(
                self.state["combate"].get("tentaculos_roper",{})
            )
            out["tentaculos_destruidos"] = copy.deepcopy(
                self.state["combate"].get("tentaculos_destruidos",{})
            )
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

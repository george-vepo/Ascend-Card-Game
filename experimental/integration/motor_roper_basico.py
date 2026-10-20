"""Terceira criatura SRD: Bite e Tentacle isolados Roper × Giant Owl.

NÃO é combate SRD completo: a fixture Roper suporta tentáculos múltiplos
sobre o mesmo alvo conforme decisão homebrew aprovada no Card Game.
Spider Climb, Flyby, recursos e magias permanecem parciais. Reel e
ataques ignoram movimento e alcance espacial na POC.
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
from ascend.habilidades_poc_srd import extrair_habilidades_poc_srd
from ascend.magias_owl_poc import (
    DETECCOES_OWL, REGRA_APROVADA, DURACAO_CONCENTRACAO_RODADAS,
    bonus_salvaguarda_constituicao_owl, detectar_publico,
)
from ascend.testes_d20_srd import (
    resolver_teste_atributo, TesteD20Invalido, TesteD20Pendente,
)
from motor_poc import MotorPOC, InvalidAction, UnresolvedRule, SIDES, other
from motor_fichas_poc import MotorFichasPOC, SessaoFichasFixture

ESCOPO_BASICO = "ATAQUE_INDIVIDUAL_SEM_MULTIATAQUE_OU_PASSIVOS"
ESCOPO_MULTIATTACK = "MULTIATTACK_ATOMICO_GRAPPLE_MULTIPLO_APROVADO"
ESCOPO_CONJURACAO_OWL = "OWL_DETECCAO_PUBLICA_SEM_POSICAO_ISSUE30"
DUELO_ROPER = {"J1": "CE-001", "J2": "AB-POC-017"}


class MotorRoperBasico(MotorFichasPOC):
    """Iniciativa e um ataque corpo a corpo por turno em fixture isolada."""

    def _estado_agarrado(self, estado, card):
        """Confere exatamente um vínculo por slot e condições sem acúmulo.

        Regra homebrew aprovada 19/10/2026: vários tentáculos independentes
        podem agarrar o alvo, mas Grappled e Poisoned aparecem uma única vez.
        """
        condicoes = card["condicoes"]
        efeitos = card["efeitos"]
        slots = estado["combate"].get("tentaculos_roper", {})
        if not isinstance(slots, dict):
            raise UnresolvedRule("tentáculos ativos devem formar um mapa")
        if not slots:
            if condicoes or efeitos:
                raise UnresolvedRule("condições de grapple sem tentáculo ativo")
            return
        if (condicoes != ["Grappled", "Poisoned"]
                or len(efeitos) != len(slots) or not 1 <= len(slots) <= 6):
            raise UnresolvedRule("condições/vínculos Grappled inconsistentes")
        por_slot = {}
        for efeito in efeitos:
            if not isinstance(efeito, dict):
                raise UnresolvedRule("efeito Tentacle inválido")
            slot = efeito.get("tentaculo")
            if type(slot) is not int or not 1 <= slot <= 6 or slot in por_slot:
                raise UnresolvedRule("efeitos repetidos ou tentáculo inválido")
            por_slot[slot] = efeito
        if set(por_slot) != {int(key) for key in slots
                            if type(key) is str and key.isdigit()
                            and str(int(key)) == key}:
            raise UnresolvedRule("efeitos e tentáculos não correspondem")
        for key, registro in slots.items():
            if (type(key) is not str or not key.isdigit()
                    or str(int(key)) != key or not 1 <= int(key) <= 6
                    or not isinstance(registro, dict)
                    or registro.get("alvo_id") != "CE-001"
                    or registro.get("origem_id") != "AB-POC-017"):
                raise UnresolvedRule("slot Tentacle sem alvo e origem válidos")
            esperado = {
                "tipo": "ROPER_TENTACLE_GRAPPLE",
                "fonte": "AB-POC-017", "alvo_id": "CE-001",
                "tentaculo": int(key),
                "condicoes": ["Grappled", "Poisoned"],
                "escape_dc": por_slot[int(key)].get("escape_dc"),
                "sha256_documento": registro.get("sha256_documento"),
            }
            if por_slot[int(key)] != esperado:
                raise UnresolvedRule("vínculo entre tentáculo e efeito divergente")

    def _agarrar_tentaculo(self, estado, slot, regra):
        """Cria vínculo independente sem repetir a condição no alvo."""
        alvo = self.get_card(estado, "J1", "CE-001")
        self._estado_agarrado(estado, alvo)
        slots = estado["combate"].setdefault("tentaculos_roper", {})
        if str(slot) in slots:
            raise InvalidAction("tentáculo já mantém alvo agarrado")
        if len(slots) >= regra["quantidade_tentaculos"]:
            raise InvalidAction("todos os tentáculos já estão ocupados")
        if not slots:
            alvo["condicoes"] = ["Grappled", "Poisoned"]
        efeito = {
            "tipo": "ROPER_TENTACLE_GRAPPLE",
            "fonte": "AB-POC-017", "alvo_id": "CE-001",
            "tentaculo": slot, "condicoes": ["Grappled", "Poisoned"],
            "escape_dc": regra["escape_dc"],
            "sha256_documento": regra["sha256_documento"],
        }
        alvo["efeitos"].append(efeito)
        slots[str(slot)] = {
            "origem_id": "AB-POC-017", "alvo_id": "CE-001",
            "sha256_documento": regra["sha256_documento"],
            "pv_atual": regra["tentaculo"]["pv"],
            "pv_max": regra["tentaculo"]["pv"],
        }
        self._estado_agarrado(estado, alvo)

    def _libertar_todos_tentaculos(self, estado):
        """Libera todos os vínculos do mesmo Roper (escape aprovado ou KO)."""
        ativos = sorted(int(x) for x in
                        estado["combate"].get("tentaculos_roper", {}))
        for slot in ativos:
            self._libertar_tentaculo(estado, slot)
        return ativos

    def validate(self, s=None):
        """Impede deixar Grappled/Poisoned e tentáculos órfãos entre combates."""
        result=super().validate(s)
        estado=self.state if s is None else s
        conc = estado["combate"].get("concentracao_owl")
        if conc is not None:
            if estado["fase"] != "COMBATE":
                raise InvalidAction("concentração não persiste fora do combate")
            if (not isinstance(conc, dict)
                    or set(conc) != {
                        "magia", "caster_id", "rodada_inicio", "duracao_rodadas",
                        "bonus_salvaguarda_con", "origem_ficha_sha256",
                    }
                    or conc["magia"] not in DETECCOES_OWL
                    or conc["caster_id"] != "CE-001"
                    or type(conc["rodada_inicio"]) is not int
                    or conc["rodada_inicio"] < 1
                    or conc["rodada_inicio"] > estado["combate"]["rodada"]
                    or estado["combate"]["rodada"] - conc["rodada_inicio"]
                       > DURACAO_CONCENTRACAO_RODADAS
                    or conc["duracao_rodadas"] != DURACAO_CONCENTRACAO_RODADAS
                    or type(conc["bonus_salvaguarda_con"]) is not int
                    or conc["bonus_salvaguarda_con"] != 1
                    or not isinstance(conc["origem_ficha_sha256"], str)
                    or len(conc["origem_ficha_sha256"]) != 64):
                raise InvalidAction("registro de concentração divergente")
        if estado["fase"] == "COMBATE":
            self._estado_agarrado(
                estado, self.get_card(estado, "J1", "CE-001")
            )
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
        if ativos:
            self._libertar_todos_tentaculos(s)
        destruidos=sorted(int(k) for k in combat.get("tentaculos_destruidos",{}))
        combat.pop("tentaculos_destruidos",None)
        conc_encerrada = combat.pop("concentracao_owl", None)
        MotorFichasPOC._ko(self,s,winner,source)
        return {
            "tentaculos_soltos":ativos,
            "tentaculos_destruidos_encerrados":destruidos,
            "condicoes_removidas":(["Grappled","Poisoned"] if ativos else []),
            "concentracao_encerrada": (
                conc_encerrada["magia"] if conc_encerrada else None
            ),
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
        conc = combate.get("concentracao_owl")
        expirou = None
        if (conc and estado["ator_da_vez"] == "J1"
                and combate["rodada"] - conc["rodada_inicio"]
                    >= DURACAO_CONCENTRACAO_RODADAS):
            expirou = combate.pop("concentracao_owl")["magia"]
        return {
            "concentracao_expirada": expirou,
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
            if (type(key) is not str or not key.isdigit()
                    or str(int(key))!=key
                    or not 1<=int(key)<=regra["quantidade_tentaculos"]
                    or not isinstance(entry,dict) or entry.get("sha256_documento")!=ref
                    or type(entry.get("pv_atual")) is not int
                    or not 1<=entry["pv_atual"]<=regra["tentaculo"]["pv"]
                    or entry.get("pv_max")!=regra["tentaculo"]["pv"]
                    or entry.get("origem_id")!="AB-POC-017"
                    or entry.get("alvo_id")!="CE-001"):
                raise UnresolvedRule("tentáculo ocupado sem slot/PV/fonte válidos")
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
            card=self.get_card(estado,"J1","CE-001")
            if any(e.get("escape_dc")!=regra["escape_dc"]
                   for e in card["efeitos"]):
                raise UnresolvedRule("CD de fuga diverge da ficha Tentacle")
        return perfis

    def _libertar_tentaculo(self,estado,slot):
        """Libera somente o vínculo solicitado e mantém outros Grappled."""
        owl = self.get_card(estado, "J1", "CE-001")
        slots = estado["combate"].get("tentaculos_roper", {})
        if str(slot) not in slots:
            raise InvalidAction("tentáculo não ocupa este slot")
        self._estado_agarrado(estado, owl)
        owl["efeitos"] = [
            efeito for efeito in owl["efeitos"]
            if efeito["tentaculo"] != slot
        ]
        slots.pop(str(slot))
        if not slots:
            estado["combate"].pop("tentaculos_roper", None)
            owl["condicoes"] = []
        self._estado_agarrado(estado, owl)
        return not slots

    @staticmethod
    def _dado(valor, faces):
        return type(valor) is int and 1 <= valor <= faces

    def prevalidar_habilidades_poc(self) -> dict:
        """Inventário público dos dois campos, sem executar habilidades.

        Passivas exclusivamente espaciais não causam efeitos no Card Game.
        Magias da Owl permanecem pendentes de efeito/recurso, não se
        consideram conjuradas por consultar sua descrição.
        """
        result = {
            "estado": "INAPLICAVEL",
            "consome_acao": False,
            "altera_estado": False,
            "campos": {},
        }
        s = self.state
        if s.get("fase") != "COMBATE":
            return result
        self._perfis(s)
        for jogador, id_copia in DUELO_ROPER.items():
            try:
                ficha = consultar_ficha(
                    self.checkout_catalogo, self.contrato,
                    self.referencias, id_copia,
                    exigir_revisao=self.exigir_revisao,
                )
                result["campos"][jogador] = extrair_habilidades_poc_srd(ficha)
            except (FichaPendente, FichaConflitante) as exc:
                raise UnresolvedRule(
                    "inventário de habilidades pendente: " + str(exc)
                ) from exc
        result["estado"] = "AUDITADO_SEM_EXECUCAO"
        result["fonte_regra_poc"] = "SEM_POSICIONAMENTO_15_10_2026"
        return result

    def prevalidar_conjuracao_owl(self) -> dict:
        """Consulta sem mutação; nenhuma opção lê mão/monte ou usa recursos."""
        s = self.state
        res = {
            "estado": "INAPLICAVEL", "executavel": False,
            "consome_acao": False, "magias": [],
            "concentracao_atual": None,
            "regra_homebrew": REGRA_APROVADA,
        }
        if s["fase"] != "COMBATE":
            return res
        self._perfis(s)
        info = self.prevalidar_habilidades_poc()["campos"]["J1"]["conjuracao"]
        if [x["nome"] for x in info["magias"]] != [
                "Detect Evil and Good", "Detect Magic", "Clairvoyance"]:
            raise UnresolvedRule("lista de Spellcasting diferente da ficha")
        res["magias"] = [
            {"nome": x["nome"],
             "estado": ("PRONTA_COM_ACTION" if x["nome"] in DETECCOES_OWL
                        else "INAPLICAVEL_SEM_LOCAL_E_TEMPO_DE_CONJURACAO"),
             "frequencia_srd": x["frequencia_srd"]}
            for x in info["magias"]
        ]
        conc = s["combate"].get("concentracao_owl")
        res["concentracao_atual"] = conc["magia"] if conc else None
        res["estado"] = "AUDITADA"
        res["executavel"] = s["ator_da_vez"] == "J1"
        return res

    def _resolver_concentracao_por_dano(self, estado, dano, d20):
        """SRD: Constituição CD max(10, metade do dano), máximo 30.

        Faltando d20 exigido: evento inteiro PENDENTE; apply é transacional.
        """
        conc = estado["combate"].get("concentracao_owl")
        if not conc or dano <= 0:
            return None
        if not self._dado(d20, 20):
            if d20 is None:
                raise UnresolvedRule(
                    "salvaguarda de Concentração da Owl exige d20 externo"
                )
            raise InvalidAction("d20 de Concentração inválido")
        cd = min(30, max(10, dano // 2))
        bonus = conc["bonus_salvaguarda_con"]
        total = d20 + bonus
        manteve = total >= cd
        resultado = {
            "magia": conc["magia"], "d20_simulado": d20,
            "bonus_salvaguarda_con": bonus, "cd": cd,
            "total": total, "manteve": manteve,
            "dados_simulados": True,
        }
        if not manteve:
            estado["combate"].pop("concentracao_owl")
        return resultado

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
        if any(data.get("origem_id") != "AB-POC-017"
               or data.get("alvo_id") != "CE-001"
               for data in slots.values()):
            raise UnresolvedRule("tentáculo com origem/alvo divergente para Reel")
        numeros = sorted(int(key) for key in slots)
        result["estado"] = "PRONTO_SEM_POSICIONAMENTO"
        result["executavel"] = True
        result["alvos"] = [{
            "carta_id": "CE-001",
            "tentaculos_numeros": numeros,
            "condicoes": ["Grappled", "Poisoned"],
            **({"tentaculo_numero": numeros[0]} if len(numeros) == 1 else {}),
        }]
        result["dados_necessarios"] = []
        result["efeito_espacial_aplicado"] = False
        result["regra_poc"] = "SEM_POSICIONAMENTO_15_10_2026"
        result["lacuna"] = None
        return result

    def prevalidar_multiattack(self) -> dict:
        """Consulta pura da Action completa, sem executar dados ou recursos."""
        s = self.state
        result = {
            "acao": "MULTIATTACK_ROPER_TESTE",
            "estado": "INAPLICAVEL", "executavel": False,
            "consome_acao": False, "etapas": [], "bloqueios": [],
            "lacuna": None,
        }
        if s.get("fase") != "COMBATE" or s.get("ator_da_vez") != "J2":
            return result
        perfil = self._perfis(s)["J2"][1]
        multi = perfil["multiattack"]
        result["etapas"] = copy.deepcopy(multi["etapas"])
        result["origem_ficha_sha256"] = multi["sha256_documento"]
        result["tipo_acao_fonte"] = multi["tipo_acao"]
        result["estado"] = "PRONTO_GRAPPLE_MULTIPLO_APROVADO"
        result["executavel"] = True
        result["escopo_execucao"] = ESCOPO_MULTIATTACK
        result["regra_homebrew"] = "GRAPPLE_MULTIPLO_FUGA_UNICA_19_10_2026"
        return result

    def _multiattack_roper_caso_seguro(self, s, params):
        """Uma Action transacional: 2 Tentacle, Reel, 2 Bite.

        O alvo pode acumular vínculos independentes dos seis tentáculos;
        as condições Grappled/Poisoned são únicas e Reel é único.
        Sem posição, distância, movimento ou arena.
        """
        if params.get("aceite_escopo") != ESCOPO_MULTIATTACK:
            raise UnresolvedRule("confirmar escopo aprovado do Multiattack")
        tentaculos = params.get("tentaculos")
        bites = params.get("bites")
        if (not isinstance(tentaculos, list) or len(tentaculos) != 2
                or not isinstance(bites, list) or len(bites) != 2):
            raise InvalidAction("exigir dois Tentacle e dois Bite em sequência")
        if any(not isinstance(v, dict) for v in tentaculos + bites):
            raise InvalidAction("etapas Multiattack devem ser mapas de rolagem")
        perfis = self._perfis(s)
        perfil = perfis["J2"][1]
        etapas = perfil["multiattack"]["etapas"]
        if etapas != [
                {"ataque": "Tentacle", "quantidade": 2},
                {"ataque": "Reel", "quantidade": 1},
                {"ataque": "Bite", "quantidade": 2}]:
            raise UnresolvedRule("composição Multiattack não confere com ficha")
        regra = perfil["tentaculo"]
        alvo = self.get_card(s, "J1", "CE-001")
        slots = s["combate"].setdefault("tentaculos_roper", {})
        ids_usados = set()
        historico = []

        # Etapa 1: duas tentativas; cada ataque é individual e sem dano.
        for i, entry in enumerate(tentaculos, 1):
            slot, d20 = entry.get("tentaculo_numero"), entry.get("d20_simulado")
            if (type(slot) is not int
                    or not 1 <= slot <= regra["quantidade_tentaculos"]
                    or slot in ids_usados or str(slot) in slots
                    or str(slot) in s["combate"].get("tentaculos_destruidos", {})):
                raise InvalidAction("Tentacle repetido, ocupado, destruído ou inválido")
            if not self._dado(d20, 20):
                raise InvalidAction("d20 simulado de Tentacle inválido")
            ids_usados.add(slot)
            bonus = regra["bonus_ataque"]
            acertou = d20 == 20 or (d20 != 1 and d20 + bonus >= perfis["J1"][1]["ac"])
            historico.append({
                "etapa": "Tentacle", "numero": i, "tentaculo": slot,
                "d20_simulado": d20, "bonus": bonus, "total": d20 + bonus,
                "ca": perfis["J1"][1]["ac"], "acertou": acertou,
                "critico": d20 == 20, "dano": 0,
            })
            if acertou:
                self._agarrar_tentaculo(s, slot, regra)


        # Etapa 2: Reel está na ficha; no card game não há deslocamento.
        historico.append({
            "etapa": "Reel", "numero": 1,
            "alvos_agarrados": ["CE-001"] if slots else [],
            "tentaculos_ativos": sorted(int(key) for key in slots),
            "deslocamento_aplicado": False,
        })

        # Etapa 3: dois Bite na mesma Action, interrompidos imediatamente no KO.
        ataque = perfil["attack"]
        if ataque["name"] != "Bite":
            raise UnresolvedRule("Bite divergente da ficha do Roper")
        for i, entry in enumerate(bites, 1):
            d20 = entry.get("d20_simulado")
            if not self._dado(d20, 20):
                raise InvalidAction("d20 simulado de Bite inválido")
            critico = d20 == 20
            acertou = critico or (d20 != 1 and
                                 d20 + ataque["bonus"] >= perfis["J1"][1]["ac"])
            quantidade = ataque["dice"][0] * (2 if critico else 1) if acertou else 0
            dados = entry.get("dano_dados", [])
            if (not isinstance(dados, list) or len(dados) != quantidade
                    or not all(self._dado(d, ataque["dice"][1]) for d in dados)):
                raise InvalidAction("dados de dano Bite incompatíveis com a rolagem")
            bruto = max(0, sum(dados) + ataque["flat"]) if acertou else 0
            defesa = perfis["J1"][1]
            if ataque["type"] in defesa["immunities"]:
                aplicado = 0
            elif ataque["type"] in defesa["resistances"]:
                aplicado = bruto // 2
            else:
                aplicado = bruto
            antes = alvo["pv_atual"]
            alvo["pv_atual"] = max(0, antes - aplicado)
            concentracao = None
            if alvo["pv_atual"] > 0:
                concentracao = self._resolver_concentracao_por_dano(
                    s, aplicado, entry.get("d20_concentracao_simulado")
                )
            historico.append({
                "etapa": "Bite", "numero": i, "d20_simulado": d20,
                "bonus": ataque["bonus"], "total": d20 + ataque["bonus"],
                "ca": defesa["ac"], "critico": critico,
                "acertou": acertou, "dano_dados_simulados": list(dados),
                "modificador_dano": ataque["flat"] if acertou else 0,
                "dano_bruto": bruto, "dano_aplicado": aplicado,
                "pv_antes": antes, "pv_depois": alvo["pv_atual"],
                "concentracao": concentracao,
            })
            if alvo["pv_atual"] == 0:
                # KO, cemitérios, condições e pontuação: um único evento.
                encerramento = self._ko(s, "J2", "FIXTURE_SRD_MULTIATTACK_GRAPPLE_MULTIPLO_APROVADO")
                return {
                    "acao": "Multiattack", "componentes": historico,
                    "componentes_executados": len(historico),
                    "interrompido_por_ko": True,
                    "encerramento_tentaculos": encerramento,
                    "pontuacao_fixture": copy.deepcopy(s["placar"]),
                    "origem_ficha_sha256": perfil["multiattack"]["sha256_documento"],
                    "dados_simulados": True, "mecanica_parcial": True,
                    "regra_poc": "SEM_POSICIONAMENTO_15_10_2026",
                }

        resultado = {
            "acao": "Multiattack", "componentes": historico,
            "componentes_executados": len(historico),
            "interrompido_por_ko": False,
            "origem_ficha_sha256": perfil["multiattack"]["sha256_documento"],
            "dados_simulados": True, "mecanica_parcial": True,
            "regra_poc": "SEM_POSICIONAMENTO_15_10_2026",
        }
        resultado.update(self._proximo_turno(s, "J2"))
        return resultado

    def _transition(self, s, actor, command, params):
        if command == "CONJURAR_MAGIA_OWL_TESTE":
            if actor != "J1":
                raise InvalidAction("Spellcasting pertence à Giant Owl do J1")
            self._gate(s, "COMBATE", actor)
            if params.get("aceite_escopo") != ESCOPO_CONJURACAO_OWL:
                raise UnresolvedRule("confirmar escopo aprovado de detecção pública")
            magia = params.get("magia")
            if magia == "Clairvoyance":
                raise InvalidAction(
                    "Clairvoyance inaplicável: exige localização do sensor "
                    "e 10 minutos de conjuração; uso 1/Day NÃO consumido"
                )
            if magia not in DETECCOES_OWL:
                raise InvalidAction("magia não disponível no recorte da Owl")
            self._perfis(s)
            fonte = consultar_ficha(
                self.checkout_catalogo, self.contrato, self.referencias,
                "CE-001", exigir_revisao=self.exigir_revisao,
            )
            lista = extrair_habilidades_poc_srd(fonte)["conjuracao"]["magias"]
            if magia not in [x["nome"] for x in lista]:
                raise UnresolvedRule("magia divergente da ficha de Spellcasting")
            bonus = bonus_salvaguarda_constituicao_owl(fonte)
            anterior = s["combate"].get("concentracao_owl")
            s["combate"]["concentracao_owl"] = {
                "magia": magia, "caster_id": "CE-001",
                "rodada_inicio": s["combate"]["rodada"],
                "duracao_rodadas": DURACAO_CONCENTRACAO_RODADAS,
                "bonus_salvaguarda_con": bonus,
                "origem_ficha_sha256": fonte.sha256_documento,
            }
            resultado = {
                "acao": "Spellcasting", "magia": magia,
                "tipo_acao": "Action",
                "concentracao_anterior_encerrada": (
                    anterior["magia"] if anterior else None
                ),
                "concentracao_max_rodadas": DURACAO_CONCENTRACAO_RODADAS,
                "dados_simulados": False,
                "regra_homebrew": REGRA_APROVADA,
                "informacao_publica": detectar_publico(s, magia),
                "origem_ficha_sha256": fonte.sha256_documento,
                "recursos_diarios_consumidos": 0,
            }
            resultado.update(self._proximo_turno(s, actor))
            return resultado
        if command == "ENCERRAR_CONCENTRACAO_OWL_TESTE":
            if actor != "J1" or s["fase"] != "COMBATE":
                raise InvalidAction("somente a Owl em combate pode encerrar concentração")
            conc = s["combate"].pop("concentracao_owl", None)
            if not conc:
                raise InvalidAction("não há concentração da Owl para encerrar")
            return {
                "acao": "Encerrar Concentração", "magia": conc["magia"],
                "consome_acao": False, "regra_homebrew": REGRA_APROVADA,
            }
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
            concentracao = None
            if defender == "J1" and victim["pv_atual"] > 0:
                concentracao = self._resolver_concentracao_por_dano(
                    s, damage, params.get("d20_concentracao_simulado")
                )
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
                "concentracao": concentracao,
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
                ja_agarrado = bool(ocupado)
                self._agarrar_tentaculo(s, slot, source)
                result["condicoes_aplicadas"] = (
                    [] if ja_agarrado else ["Grappled", "Poisoned"]
                )
                result["vinculo_tentaculo_criado"] = slot
                result["escape_dc"] = source["escape_dc"]
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
            if not slots:
                raise InvalidAction("a criatura não está agarrada")
            slots_antes = sorted(int(key) for key in slots)
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
                self._libertar_todos_tentaculos(s)
            result={
                "acao":"ESCAPAR_GRAPPLE","pericia":habilidade,
                **teste,
                "condicoes_removidas":(["Grappled","Poisoned"] if sucesso else []),
                "slots_liberados":slots_antes if sucesso else [],
                "slot_liberado":slots_antes[0] if sucesso and len(slots_antes)==1 else None,
                "regra_homebrew":"GRAPPLE_MULTIPLO_FUGA_UNICA_19_10_2026",
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
            ultimo_vinculo_liberado = False
            if destruido:
                ultimo_vinculo_liberado = self._libertar_tentaculo(s,slot)
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
                "condicoes_removidas":(
                    ["Grappled","Poisoned"] if ultimo_vinculo_liberado else []
                ),
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
            return self._multiattack_roper_caso_seguro(s, params)

        if command == "SPIDER_CLIMB_ROPER_TESTE":
            if actor != "J2":
                raise InvalidAction("Spider Climb pertence ao Roper")
            self._gate(s, "COMBATE", actor)
            # É uma Trait passiva espacial da ficha, não uma Action.
            # Não consumir um turno como se houvesse movimento.
            inventario = self.prevalidar_habilidades_poc()
            if inventario["campos"]["J2"]["passiva"]["nome"] != "Spider Climb":
                raise UnresolvedRule("Spider Climb não conferida na ficha")
            raise UnresolvedRule(
                "Spider Climb é Trait exclusivamente espacial, sem efeito "
                "de movimento no Card Game; não existe Action a executar"
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
            conc = self.state["combate"].get("concentracao_owl")
            out["concentracao_publica_owl"] = (
                {"magia": conc["magia"], "rodada_inicio": conc["rodada_inicio"],
                 "limite_rodadas": conc["duracao_rodadas"]}
                if conc else None
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

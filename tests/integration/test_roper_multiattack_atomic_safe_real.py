"""Multiattack Roper: execução atômica do subconjunto SRD verificável.

Não homologa múltiplos tentáculos acertando/alvo já agarrado em paralelo.
Fixture sem partida oficial, sem posição e com dados explicitamente simulados.
"""
import copy
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for rel in ("src", "experimental/legacy/src", "experimental/integration"):
    sys.path.insert(0, str(ROOT / rel))

from ascend.catalogo_poc import ler_contrato
from motor_roper_basico import (
    SessaoRoperFixture, ESCOPO_BASICO, ESCOPO_MULTIATTACK,
)


class MultiattackAtomicoSeguro(unittest.TestCase):
    def setUp(self):
        self.catalogo = os.environ["CATALOGO_SRD_DIR"]
        self.contrato = ler_contrato(ROOT)
        self.s = SessaoRoperFixture.criar_de_checkout(
            self.catalogo, self.contrato, primeiro="J2",
            maos_fixadas={
                "J1": ["CE-001", "CE-002", "CE-003", "CE-004", "CE-005"],
                "J2": ["AB-POC-017", "AB-POC-001", "AB-POC-002",
                       "AB-POC-003", "AB-POC-004"],
            },
        )
        self.n = 0
        for p in ("J2", "J1"):
            self.ok(p, "TROCAR", {"descartar": []})
        for p, cid in (("J2", "AB-POC-017"), ("J1", "CE-001")):
            self.ok(p, "INVOCAR", {"carta_id": cid})
            self.ok(p, "PRONTO_CRIATURA")
        for p in ("J2", "J1"):
            self.ok(p, "ESCOLHER_SUPORTE", {"carta_id": None})
        for _ in range(2):
            self.ok("ARBITRO", "RESOLVER_SUPORTE_FIXTURE",
                    {"resultado": "PULAR"})
        self.ok("ARBITRO", "INICIATIVA_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "d20_simulados": {"J1": 10, "J2": 12},
        })

    def cmd(self, actor, action, args=None, event_id=None):
        self.n += 1
        return self.s.comando(event_id or ("atomic-" + str(self.n)),
                              actor, action, args or {})

    def ok(self, actor, action, args=None):
        result = self.cmd(actor, action, args)
        self.assertEqual(result["decisao"], "ACEITA", result)
        return result

    def card(self, actor, cid):
        return self.s.motor.get_card(self.s.motor.state, actor, cid)

    @staticmethod
    def payload(t1=1, t2=1, b1=1, b2=1, dice1=None, dice2=None,
                slot1=1, slot2=2):
        return {
            "aceite_escopo": ESCOPO_MULTIATTACK,
            "tentaculos": [
                {"tentaculo_numero": slot1, "d20_simulado": t1},
                {"tentaculo_numero": slot2, "d20_simulado": t2},
            ],
            "bites": [
                {"d20_simulado": b1,
                 "dano_dados": [] if dice1 is None else dice1},
                {"d20_simulado": b2,
                 "dano_dados": [] if dice2 is None else dice2},
            ],
        }

    def test_01_dois_erros_na_tentacle_e_bites_ainda_resolvem_action(self):
        r = self.ok("J2", "MULTIATTACK_ROPER_TESTE", self.payload())
        steps = r["resultado"]["componentes"]
        self.assertEqual([x["etapa"] for x in steps],
                         ["Tentacle", "Tentacle", "Reel", "Bite", "Bite"])
        self.assertEqual(steps[2]["alvos_agarrados"], [])
        self.assertFalse(steps[2]["deslocamento_aplicado"])
        self.assertFalse(r["resultado"]["interrompido_por_ko"])
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J1")
        self.assertEqual(self.card("J1", "CE-001")["pv_atual"], 19)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 0})

    def test_02_primeiro_tentacle_acerta_segundo_erra(self):
        r = self.ok("J2", "MULTIATTACK_ROPER_TESTE",
                    self.payload(t1=10, t2=1))
        self.assertEqual(r["resultado"]["componentes"][2]["alvos_agarrados"],
                         ["CE-001"])
        self.assertEqual(self.card("J1", "CE-001")["condicoes"],
                         ["Grappled", "Poisoned"])
        self.assertEqual(list(self.s.motor.state["combate"]["tentaculos_roper"]), ["1"])
        self.assertTrue(self.s.motor.validate())

    def test_03_primeiro_erra_segundo_tentacle_acerta(self):
        self.ok("J2", "MULTIATTACK_ROPER_TESTE",
                self.payload(t1=1, t2=10))
        self.assertEqual(list(self.s.motor.state["combate"]["tentaculos_roper"]), ["2"])
        self.assertEqual(self.card("J1", "CE-001")["efeitos"][0]["tentaculo"], 2)

    def test_04_dois_tentacle_acertam_pendente_e_sem_mutacao(self):
        old = copy.deepcopy(self.s.motor.state)
        chain = self.s.motor.head_hash
        r = self.cmd("J2", "MULTIATTACK_ROPER_TESTE",
                     self.payload(t1=10, t2=10))
        self.assertEqual(r["decisao"], "PENDENTE", r)
        self.assertIn("dois vínculos Grappled", r["motivo"])
        self.assertEqual(self.s.motor.state, old)
        self.assertEqual(self.s.motor.head_hash, chain)

    def test_05_dois_bites_acertam_e_restam_pv(self):
        r = self.ok("J2", "MULTIATTACK_ROPER_TESTE",
                    self.payload(b1=10, b2=10,
                                 dice1=[1, 1, 1], dice2=[1, 1, 1]))
        owl = self.card("J1", "CE-001")
        self.assertEqual(owl["pv_atual"], 5)
        self.assertEqual([s["dano_aplicado"] for s in r["resultado"]["componentes"][-2:]],
                         [7, 7])
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J1")
        self.assertEqual(self.s.motor.state["combate"]["rodada"], 1)

    def test_06_ko_no_primeiro_bite_interrompe_segundo(self):
        r = self.ok("J2", "MULTIATTACK_ROPER_TESTE",
                    self.payload(t1=10, t2=1, b1=20, b2=0,
                                 dice1=[8] * 6))
        steps = r["resultado"]["componentes"]
        self.assertEqual([x["etapa"] for x in steps],
                         ["Tentacle", "Tentacle", "Reel", "Bite"])
        self.assertTrue(r["resultado"]["interrompido_por_ko"])
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 1})
        self.assertEqual(self.s.motor.state["fase"], "POS_COMBATE")
        self.assertEqual(self.card("J1", "CE-001")["zona"], "CEMITERIO")
        self.assertEqual(self.s.motor.state["combate"].get("tentaculos_roper"), None)
        self.assertEqual(self.card("J1", "CE-001")["condicoes"], [])

    def test_07_ko_no_segundo_bite_pontua_apenas_uma_vez(self):
        r = self.ok("J2", "MULTIATTACK_ROPER_TESTE",
                    self.payload(b1=10, b2=10,
                                 dice1=[3, 3, 3], dice2=[3, 3, 3]))
        self.assertEqual(len(r["resultado"]["componentes"]), 5)
        self.assertEqual(self.s.motor.state["placar"]["J2"], 1)
        self.assertEqual(self.card("J1", "CE-001")["pv_atual"], 0)

    def test_08_critico_dobra_dados_do_bite(self):
        r = self.ok("J2", "MULTIATTACK_ROPER_TESTE",
                    self.payload(b1=20, b2=1,
                                 dice1=[1] * 6))
        first_bite = r["resultado"]["componentes"][3]
        self.assertTrue(first_bite["critico"])
        self.assertEqual(first_bite["dano_aplicado"], 10)

    def test_09_dados_invalidos_no_segundo_bite_reverte_primeiro(self):
        payload = self.payload(t1=10, t2=1, b1=10, b2=10,
                               dice1=[1, 1, 1], dice2=[1])
        old = copy.deepcopy(self.s.motor.state)
        n = len(self.s.motor.events)
        r = self.cmd("J2", "MULTIATTACK_ROPER_TESTE", payload)
        self.assertEqual(r["decisao"], "REJEITADA", r)
        self.assertEqual(self.s.motor.state, old)
        self.assertEqual(len(self.s.motor.events), n)

    def test_10_slots_duplicados_rejeitam_sem_mutar(self):
        old = copy.deepcopy(self.s.motor.state)
        r = self.cmd("J2", "MULTIATTACK_ROPER_TESTE",
                     self.payload(slot1=2, slot2=2))
        self.assertEqual(r["decisao"], "REJEITADA")
        self.assertEqual(self.s.motor.state, old)

    def test_11_parametros_espaciais_sao_ignorados(self):
        payload = self.payload(t1=10, t2=1)
        payload.update({"alvo_no_alcance_fixture": False,
                        "arena_homologada": False, "distancia_ft": 9000})
        r = self.ok("J2", "MULTIATTACK_ROPER_TESTE", payload)
        self.assertEqual(r["resultado"]["regra_poc"],
                         "SEM_POSICIONAMENTO_15_10_2026")
        self.assertTrue(self.s.motor.validate())

    def test_12_acao_sem_escopo_pendente_e_estado_intacto(self):
        payload = self.payload()
        payload.pop("aceite_escopo")
        state = copy.deepcopy(self.s.motor.state)
        r = self.cmd("J2", "MULTIATTACK_ROPER_TESTE", payload)
        self.assertEqual(r["decisao"], "PENDENTE")
        self.assertEqual(state, self.s.motor.state)

    def test_13_acao_nao_pertence_ao_jogador_1(self):
        r = self.cmd("J1", "MULTIATTACK_ROPER_TESTE", self.payload())
        self.assertEqual(r["decisao"], "REJEITADA")

    def test_14_preflight_documenta_execucao_parcial_sem_homologar_completo(self):
        x = self.s.motor.prevalidar_multiattack()
        self.assertFalse(x["executavel"])
        self.assertTrue(x["executavel_parcial"])
        self.assertEqual(x["escopo_execucao_parcial"], ESCOPO_MULTIATTACK)
        self.assertIn("grapple_duplo_nao_integrado_para_todos_cenarios",
                      x["bloqueios"])

    def test_15_idempotencia_nao_duplica_ataques_ou_eventos(self):
        payload = self.payload(b1=10, b2=10,
                               dice1=[1, 1, 1], dice2=[1, 1, 1])
        first = self.cmd("J2", "MULTIATTACK_ROPER_TESTE", payload,
                         event_id="multiattack-idempotente")
        again = self.cmd("J2", "MULTIATTACK_ROPER_TESTE", payload,
                         event_id="multiattack-idempotente")
        self.assertEqual(first, again)
        self.assertEqual(self.card("J1", "CE-001")["pv_atual"], 5)
        self.assertEqual(len([e for e in self.s.motor.events if
                              e["evento_id"] == "multiattack-idempotente"]), 1)

    def test_16_checkpoint_e_privacidade_pos_multiattack(self):
        self.ok("J2", "MULTIATTACK_ROPER_TESTE",
                self.payload(t1=1, t2=10))
        restored = SessaoRoperFixture.restaurar(
            self.s.checkpoint(), self.catalogo, self.contrato)
        self.assertEqual(restored.motor.state, self.s.motor.state)
        public = json.dumps(self.s.mesa_publica(), ensure_ascii=False)
        self.assertNotIn("CE-002", public)
        self.assertNotIn("AB-POC-001", public)
        self.assertTrue(self.s.motor.validate())
        for side in ("J1", "J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][side]["cartas"]), 40)


if __name__ == "__main__":
    unittest.main()

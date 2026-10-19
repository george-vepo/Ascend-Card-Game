"""Regressão real: KO encerra vínculos Tentacle sem inventar movimento."""
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
from motor_poc import InvalidAction
from motor_roper_basico import SessaoRoperFixture, ESCOPO_BASICO


class RoperKOGrappleCleanup(unittest.TestCase):
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
        self.seq = 0
        for actor in ("J2", "J1"):
            self.ok(actor, "TROCAR", {"descartar": []})
        for actor, cid in (("J2", "AB-POC-017"), ("J1", "CE-001")):
            self.ok(actor, "INVOCAR", {"carta_id": cid})
            self.ok(actor, "PRONTO_CRIATURA")
        for actor in ("J2", "J1"):
            self.ok(actor, "ESCOLHER_SUPORTE", {"carta_id": None})
        for _ in range(2):
            self.ok("ARBITRO", "RESOLVER_SUPORTE_FIXTURE",
                    {"resultado": "PULAR"})
        self.ok("ARBITRO", "INICIATIVA_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "d20_simulados": {"J1": 10, "J2": 12},
        })

    def cmd(self, actor, action, params=None, id=None):
        self.seq += 1
        return self.s.comando(id or f"ko-cleanup-{self.seq}",
                              actor, action, params or {})

    def ok(self, actor, action, params=None):
        r = self.cmd(actor, action, params)
        self.assertEqual(r["decisao"], "ACEITA", r)
        return r

    def card(self, player, cid):
        return self.s.motor.get_card(self.s.motor.state, player, cid)

    def grip(self):
        self.ok("J2", "TENTACLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "alvo_no_alcance_fixture": True,
            "tentaculo_numero": 3, "d20_simulado": 10,
        })
        self.assertEqual(self.card("J1", "CE-001")["condicoes"],
                         ["Grappled", "Poisoned"])

    def miss_escape(self):
        return self.ok("J1", "ESCAPAR_GRAPPLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "pericia": "Athletics", "d20_simulados": [1, 2],
        })

    def bite(self, d20, dice):
        return self.ok("J2", "ATAQUE_ROPER_BASICO_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "alvo_no_alcance_fixture": True, "ataque": "Bite",
            "d20_simulado": d20, "dano_dados": dice,
        })

    def talons(self):
        return self.ok("J1", "ATAQUE_ROPER_BASICO_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "alvo_no_alcance_fixture": True, "ataque": "Talons",
            "d20_simulados": [20, 20], "dano_dados": [10, 10],
        })

    def owl_ko(self):
        self.grip()
        self.miss_escape()
        r = self.bite(20, [4] * 6)
        self.assertTrue(r["resultado"]["ko"])
        return r

    def test_01_ko_da_owl_limpa_condicoes_e_vinculos(self):
        r = self.owl_ko()
        state = self.s.motor.state
        owl = self.card("J1", "CE-001")
        self.assertEqual(state["fase"], "POS_COMBATE")
        self.assertEqual(owl["zona"], "CEMITERIO")
        self.assertEqual(owl["condicoes"], [])
        self.assertEqual(owl["efeitos"], [])
        self.assertNotIn("tentaculos_roper", state["combate"])
        self.assertEqual(r["resultado"]["encerramento_tentaculos"]
                         ["tentaculos_soltos"], [3])
        self.assertEqual(state["placar"], {"J1": 0, "J2": 1})
        self.assertTrue(self.s.motor.validate())

    def test_02_ko_do_roper_libera_owl_sobrevivente(self):
        self.grip()
        for round_index in range(5):
            r = self.talons()
            if round_index < 4:
                self.assertFalse(r["resultado"]["ko"])
                self.bite(1, [])
        self.assertTrue(r["resultado"]["ko"])
        self.assertEqual(self.card("J2", "AB-POC-017")["zona"], "CEMITERIO")
        owl = self.card("J1", "CE-001")
        self.assertEqual(owl["zona"], "CAMPO")
        self.assertEqual(owl["condicoes"], [])
        self.assertEqual(owl["efeitos"], [])
        self.assertEqual(owl["pv_atual"], 19)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 1, "J2": 0})
        self.assertEqual(r["resultado"]["encerramento_tentaculos"]
                         ["tentaculos_soltos"], [3])

    def test_03_ko_com_tentaculo_parcial_nao_deixa_pv_orfaos(self):
        self.grip()
        self.ok("J1", "ATACAR_TENTACULO_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO, "tentaculo_numero": 3,
            "alvo_no_alcance_fixture": True, "ataque": "Talons",
            "d20_simulados": [20, 20], "dano_dados": [1, 1],
        })
        # Crítico Talons = 2d10 + 2 => 4 de dano, sobra 6 PV.
        self.assertEqual(
            self.s.motor.state["combate"]["tentaculos_roper"]["3"]["pv_atual"], 6)
        self.bite(20, [4] * 6)
        self.assertNotIn("tentaculos_roper", self.s.motor.state["combate"])
        self.assertEqual(self.card("J1", "CE-001")["condicoes"], [])

    def test_04_ataque_sem_ko_preserva_grapple(self):
        self.grip()
        self.miss_escape()
        r = self.bite(1, [])
        self.assertFalse(r["resultado"]["ko"])
        self.assertEqual(self.card("J1", "CE-001")["condicoes"],
                         ["Grappled", "Poisoned"])
        self.assertIn("3", self.s.motor.state["combate"]["tentaculos_roper"])

    def test_05_validador_rejeita_tentaculo_apos_ko(self):
        self.owl_ko()
        invalid = copy.deepcopy(self.s.motor.state)
        invalid["combate"]["tentaculos_roper"] = {"3": {"alvo_id": "CE-001"}}
        with self.assertRaises(InvalidAction):
            self.s.motor.validate(invalid)
        self.assertTrue(self.s.motor.validate())

    def test_06_validador_rejeita_efeito_orfao_apos_ko(self):
        self.owl_ko()
        invalid = copy.deepcopy(self.s.motor.state)
        invalid["jogadores"]["J1"]["cartas"]["CE-001"]["efeitos"].append({
            "tipo": "ROPER_TENTACLE_GRAPPLE",
        })
        with self.assertRaises(InvalidAction):
            self.s.motor.validate(invalid)

    def test_07_checkpoint_apos_ko_restaura_limpo(self):
        self.owl_ko()
        restored = SessaoRoperFixture.restaurar(
            self.s.checkpoint(), self.catalogo, self.contrato)
        self.assertEqual(restored.motor.state, self.s.motor.state)
        self.assertTrue(restored.motor.validate())

    def test_08_ko_idempotente_sem_segundo_ponto(self):
        self.grip()
        self.miss_escape()
        p = {"aceite_escopo": ESCOPO_BASICO,
             "alvo_no_alcance_fixture": True, "ataque": "Bite",
             "d20_simulado": 20, "dano_dados": [4] * 6}
        first = self.cmd("J2", "ATAQUE_ROPER_BASICO_TESTE", p, id="ko-unico")
        again = self.cmd("J2", "ATAQUE_ROPER_BASICO_TESTE", p, id="ko-unico")
        self.assertEqual(first, again)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 1})

    def test_09_mesa_publica_nao_revela_maos(self):
        self.owl_ko()
        out = json.dumps(self.s.mesa_publica(), ensure_ascii=False)
        self.assertNotIn("CE-002", out)
        self.assertNotIn("AB-POC-001", out)
        for p in ("J1", "J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][p]["cartas"]), 40)

if __name__ == "__main__":
    unittest.main()

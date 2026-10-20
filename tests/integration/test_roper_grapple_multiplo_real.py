"""Grappled múltiplo do Roper — homebrew aprovado e fonte SRD 5.2.1 real.

Todos os dados simulados são fornecidos pelo teste. Partida oficial não iniciada.
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
from motor_poc import UnresolvedRule
from motor_roper_basico import (
    SessaoRoperFixture, ESCOPO_BASICO, ESCOPO_MULTIATTACK,
)


class GrappledMultiploAprovado(unittest.TestCase):
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
        for player in ("J2", "J1"):
            self.ok(player, "TROCAR", {"descartar": []})
        for player, cid in (("J2", "AB-POC-017"), ("J1", "CE-001")):
            self.ok(player, "INVOCAR", {"carta_id": cid})
            self.ok(player, "PRONTO_CRIATURA")
        for player in ("J2", "J1"):
            self.ok(player, "ESCOLHER_SUPORTE", {"carta_id": None})
        for _ in range(2):
            self.ok("ARBITRO", "RESOLVER_SUPORTE_FIXTURE",
                    {"resultado": "PULAR"})
        self.ok("ARBITRO", "INICIATIVA_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "d20_simulados": {"J1": 10, "J2": 12},
        })

    def command(self, player, action, args=None, event=None):
        self.n += 1
        return self.s.comando(event or ("duplo-" + str(self.n)),
                              player, action, args or {})

    def ok(self, player, action, args=None):
        result = self.command(player, action, args)
        self.assertEqual(result["decisao"], "ACEITA", result)
        return result

    def owl(self):
        return self.s.motor.get_card(self.s.motor.state, "J1", "CE-001")

    def slots(self):
        return self.s.motor.state["combate"].get("tentaculos_roper", {})

    def multi(self, t1=10, t2=10, slot1=1, slot2=2,
              bite1=1, bite2=1, dano1=None, dano2=None):
        payload = {
            "aceite_escopo": ESCOPO_MULTIATTACK,
            "tentaculos": [
                {"tentaculo_numero": slot1, "d20_simulado": t1},
                {"tentaculo_numero": slot2, "d20_simulado": t2},
            ],
            "bites": [
                {"d20_simulado": bite1, "dano_dados": [] if dano1 is None else dano1},
                {"d20_simulado": bite2, "dano_dados": [] if dano2 is None else dano2},
            ],
        }
        return self.ok("J2", "MULTIATTACK_ROPER_TESTE", payload)

    def escape(self, roll1, roll2, skill="Athletics"):
        return self.ok("J1", "ESCAPAR_GRAPPLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO, "pericia": skill,
            "d20_simulados": [roll1, roll2],
        })

    def hit_slot(self, slot):
        return self.ok("J1", "ATACAR_TENTACULO_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO, "tentaculo_numero": slot,
            "ataque": "Talons", "d20_simulados": [16, 16],
            "dano_dados": [8],
        })

    def two(self):
        return self.multi()

    def test_01_duplo_vinculo_e_uma_condicao_de_cada(self):
        r = self.two()
        self.assertEqual(set(self.slots()), {"1", "2"})
        self.assertEqual(self.owl()["condicoes"], ["Grappled", "Poisoned"])
        self.assertEqual(sorted(x["tentaculo"] for x in self.owl()["efeitos"]),
                         [1, 2])
        self.assertEqual({x["escape_dc"] for x in self.owl()["efeitos"]}, {14})
        self.assertEqual(r["resultado"]["componentes"][2]["alvos_agarrados"],
                         ["CE-001"])
        self.assertTrue(self.s.motor.validate())

    def test_02_fuga_falha_preserva_todos_e_consume_uma_action(self):
        self.two()
        result = self.escape(20, 1)
        self.assertFalse(result["resultado"]["sucesso"])
        self.assertEqual(result["resultado"]["d20_aplicado"], 1)
        self.assertEqual(result["resultado"]["slots_liberados"], [])
        self.assertEqual(set(self.slots()), {"1", "2"})
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J2")

    def test_03_uma_fuga_athletics_sucesso_libera_todos(self):
        self.two()
        antes = self.owl()["pv_atual"]
        r = self.escape(13, 13)
        self.assertTrue(r["resultado"]["sucesso"])
        self.assertEqual(r["resultado"]["total"], 14)
        self.assertEqual(r["resultado"]["slots_liberados"], [1, 2])
        self.assertEqual(self.slots(), {})
        self.assertEqual(self.owl()["condicoes"], [])
        self.assertEqual(self.owl()["efeitos"], [])
        self.assertEqual(self.owl()["pv_atual"], antes)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 0})

    def test_04_uma_fuga_acrobatics_sucesso_libera_todos(self):
        self.two()
        r = self.escape(12, 12, "Acrobatics")
        self.assertEqual(r["resultado"]["total"], 14)
        self.assertEqual(r["resultado"]["slots_liberados"], [1, 2])
        self.assertEqual(self.slots(), {})

    def test_05_destruir_um_tentaculo_preserva_outro_e_condicoes(self):
        self.two()
        r = self.hit_slot(1)
        self.assertTrue(r["resultado"]["destruido"])
        self.assertEqual(r["resultado"]["condicoes_removidas"], [])
        self.assertEqual(set(self.slots()), {"2"})
        self.assertEqual(self.slots()["2"]["pv_atual"], 10)
        self.assertEqual(self.owl()["condicoes"], ["Grappled", "Poisoned"])
        self.assertEqual([e["tentaculo"] for e in self.owl()["efeitos"]], [2])
        self.assertEqual(r["resultado"]["tentaculos_regenerados"], [1])

    def test_06_destruir_ultimo_remove_condicoes(self):
        self.two()
        self.hit_slot(1)
        self.ok("J2", "REEL_ROPER_TESTE")
        r = self.hit_slot(2)
        self.assertTrue(r["resultado"]["destruido"])
        self.assertEqual(r["resultado"]["condicoes_removidas"],
                         ["Grappled", "Poisoned"])
        self.assertEqual(self.slots(), {})
        self.assertEqual(self.owl()["efeitos"], [])
        self.assertEqual(self.owl()["condicoes"], [])

    def test_07_ko_no_primeiro_bite_libera_todos_antes_cemiterio(self):
        r = self.multi(bite1=20, bite2=0, dano1=[8] * 6)
        self.assertTrue(r["resultado"]["interrompido_por_ko"])
        self.assertEqual(r["resultado"]["encerramento_tentaculos"]
                         ["tentaculos_soltos"], [1, 2])
        self.assertEqual(self.slots(), {})
        self.assertEqual(self.owl()["condicoes"], [])
        self.assertEqual(self.owl()["efeitos"], [])
        self.assertEqual(self.owl()["zona"], "CEMITERIO")
        self.assertEqual(self.s.motor.state["placar"]["J2"], 1)
        self.assertEqual(len(r["resultado"]["componentes"]), 4)

    def test_08_reel_com_dois_tentaculos_um_unico_alvo(self):
        self.two()
        self.escape(1, 2)
        p = self.s.motor.prevalidar_reel()
        self.assertEqual(p["estado"], "PRONTO_SEM_POSICIONAMENTO")
        self.assertEqual(len(p["alvos"]), 1)
        self.assertEqual(p["alvos"][0]["tentaculos_numeros"], [1, 2])
        self.assertFalse(p["efeito_espacial_aplicado"])
        out = self.ok("J2", "REEL_ROPER_TESTE")
        self.assertEqual(len(out["resultado"]["alvos_agarrados"]), 1)
        self.assertEqual(self.owl()["condicoes"], ["Grappled", "Poisoned"])

    def test_09_preexistente_mais_dois_novos_sao_tres_vinculos(self):
        self.ok("J2", "TENTACLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "tentaculo_numero": 1, "d20_simulado": 10,
        })
        self.escape(1, 2)
        self.multi(slot1=2, slot2=3)
        self.assertEqual(set(self.slots()), {"1", "2", "3"})
        self.assertEqual(len(self.owl()["efeitos"]), 3)
        self.assertEqual(self.owl()["condicoes"], ["Grappled", "Poisoned"])

    def test_10_tres_vinculos_liberados_com_uma_fuga(self):
        self.ok("J2", "TENTACLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "tentaculo_numero": 1, "d20_simulado": 10,
        })
        self.escape(1, 2)
        self.multi(slot1=2, slot2=3)
        r = self.escape(13, 13)
        self.assertEqual(r["resultado"]["slots_liberados"], [1, 2, 3])
        self.assertEqual(self.owl()["condicoes"], [])
        self.assertNotIn("tentaculos_roper", self.s.motor.state["combate"])

    def test_11_id_de_tentaculo_ja_ocupado_rejeitado_sem_mutacao(self):
        self.two()
        self.escape(1, 2)
        before = copy.deepcopy(self.s.motor.state)
        head = self.s.motor.head_hash
        bad = {
            "aceite_escopo": ESCOPO_MULTIATTACK,
            "tentaculos": [
                {"tentaculo_numero": 1, "d20_simulado": 10},
                {"tentaculo_numero": 3, "d20_simulado": 10},
            ],
            "bites": [{"d20_simulado": 1, "dano_dados": []}] * 2,
        }
        r = self.command("J2", "MULTIATTACK_ROPER_TESTE", bad)
        self.assertEqual(r["decisao"], "REJEITADA")
        self.assertEqual(before, self.s.motor.state)
        self.assertEqual(head, self.s.motor.head_hash)

    def test_12_checkpoint_com_multiplos_vinculos_restauravel(self):
        self.two()
        restored = SessaoRoperFixture.restaurar(
            self.s.checkpoint(), self.catalogo, self.contrato)
        self.assertEqual(restored.motor.state, self.s.motor.state)
        self.assertTrue(restored.motor.validate())

    def test_13_estado_fraudado_com_vinculo_duplicado_e_rejeitado(self):
        self.two()
        altered = copy.deepcopy(self.s.motor.state)
        altered["jogadores"]["J1"]["cartas"]["CE-001"]["efeitos"].append(
            copy.deepcopy(self.owl()["efeitos"][0])
        )
        with self.assertRaises(UnresolvedRule):
            self.s.motor.validate(altered)
        self.assertEqual(set(self.slots()), {"1", "2"})

    def test_14_sem_rolagem_suficiente_na_fuga_pendente_sem_mutar(self):
        self.two()
        old = copy.deepcopy(self.s.motor.state)
        r = self.command("J1", "ESCAPAR_GRAPPLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "pericia": "Athletics", "d20_simulados": [20],
        })
        self.assertEqual(r["decisao"], "PENDENTE")
        self.assertEqual(self.s.motor.state, old)

    def test_15_idempotencia_multi_duplo_nao_duplica_evento(self):
        payload = {
            "aceite_escopo": ESCOPO_MULTIATTACK,
            "tentaculos": [
                {"tentaculo_numero": 1, "d20_simulado": 10},
                {"tentaculo_numero": 2, "d20_simulado": 10},
            ],
            "bites": [{"d20_simulado": 1, "dano_dados": []}] * 2,
        }
        first = self.command("J2", "MULTIATTACK_ROPER_TESTE", payload,
                             event="duplo-idempotente")
        second = self.command("J2", "MULTIATTACK_ROPER_TESTE", payload,
                              event="duplo-idempotente")
        self.assertEqual(first, second)
        self.assertEqual(len(self.owl()["efeitos"]), 2)
        self.assertEqual(len([e for e in self.s.motor.events
                              if e["evento_id"] == "duplo-idempotente"]), 1)

    def test_16_privacidade_e_40_cartas_apos_duplo_vinculo(self):
        self.two()
        view = json.dumps(self.s.mesa_publica(), ensure_ascii=False)
        self.assertNotIn("CE-002", view)
        self.assertNotIn("AB-POC-001", view)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 0})
        for side in ("J1", "J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][side]["cartas"]), 40)
        self.assertTrue(self.s.motor.validate())


if __name__ == "__main__":
    unittest.main()

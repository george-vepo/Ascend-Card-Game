"""Multiattack do Roper: contrato SRD lido da fonte, sem executar jogadas."""
import copy
import json
import os
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for rel in ("src", "experimental/legacy/src", "experimental/integration"):
    sys.path.insert(0, str(ROOT / rel))

from ascend.catalogo_poc import ler_contrato
from ascend.fichas_srd import consultar_ficha, FichaConflitante
from ascend.tentaculo_roper_srd import extrair_multiattack_roper
from motor_roper_basico import SessaoRoperFixture, ESCOPO_BASICO


class MultiattackRoperPreflight(unittest.TestCase):
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

    def cmd(self, p, action, args=None):
        self.n += 1
        return self.s.comando("multi-preflight-" + str(self.n),
                              p, action, args or {})

    def ok(self, p, action, args=None):
        r = self.cmd(p, action, args)
        self.assertEqual(r["decisao"], "ACEITA", r)
        return r

    def grip(self):
        self.ok("J2", "TENTACLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "alvo_no_alcance_fixture": True,
            "tentaculo_numero": 4, "d20_simulado": 10,
        })

    def return_roper_turn(self):
        self.grip()
        self.ok("J1", "ESCAPAR_GRAPPLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "pericia": "Athletics", "d20_simulados": [1, 2],
        })
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J2")

    def ficha(self):
        return consultar_ficha(self.catalogo, self.contrato,
                              self.s.referencias, "AB-POC-017")

    def test_01_ordem_quantidades_extraidas_da_ficha_real(self):
        ficha = self.ficha()
        x = extrair_multiattack_roper(ficha)
        self.assertEqual(x["etapas"], [
            {"ataque": "Tentacle", "quantidade": 2},
            {"ataque": "Reel", "quantidade": 1},
            {"ataque": "Bite", "quantidade": 2},
        ])
        self.assertEqual(x["tipo_acao"], "Action")
        self.assertEqual(x["sha256_documento"], ficha.sha256_documento)
        self.assertFalse(x["executavel"])

    def test_02_ficha_alterada_nao_homologa_quantidades(self):
        ficha = self.ficha()
        texto = ficha.ficha_integral.replace(
            "two Tentacle attacks", "three Tentacle attacks")
        self.assertNotEqual(texto, ficha.ficha_integral)
        with self.assertRaises(FichaConflitante):
            extrair_multiattack_roper(replace(ficha, ficha_integral=texto))

    def test_03_multiattack_duplicado_nao_e_fonte_unica(self):
        ficha = self.ficha()
        altered = ficha.ficha_integral + (
            "\nMultiattack. The roper makes two Tentacle attacks, "
            "uses Reel, and makes two Bite attacks.\n"
        )
        with self.assertRaises(FichaConflitante):
            extrair_multiattack_roper(
                replace(ficha, ficha_integral=altered))

    def test_04_preflight_completo_mas_nao_executavel(self):
        x = self.s.motor.prevalidar_multiattack()
        self.assertEqual(x["estado"], "PENDENTE_COMPONENTES")
        self.assertFalse(x["executavel"])
        self.assertFalse(x["consome_acao"])
        self.assertEqual([s["ataque"] for s in x["etapas"]],
                         ["Tentacle", "Reel", "Bite"])
        self.assertEqual([s["quantidade"] for s in x["etapas"]], [2, 1, 2])
        self.assertTrue(x["executavel_parcial"])
        self.assertIn("grapple_duplo_nao_integrado_para_todos_cenarios",
                      x["bloqueios"])
        self.assertNotIn("Reel_requer_arena_e_posicionamento_aprovados",
                         x["bloqueios"])
        self.assertNotIn("d20_simulado", x)

    def test_05_prevalidacao_repetida_e_pura(self):
        state = copy.deepcopy(self.s.motor.state)
        events = copy.deepcopy(self.s.motor.events)
        chain = self.s.motor.head_hash
        for _ in range(5):
            self.s.motor.prevalidar_multiattack()
        self.assertEqual(state, self.s.motor.state)
        self.assertEqual(events, self.s.motor.events)
        self.assertEqual(chain, self.s.motor.head_hash)

    def test_06_declaracao_pendente_nao_consume_action(self):
        before = copy.deepcopy(self.s.motor.state)
        r = self.cmd("J2", "MULTIATTACK_ROPER_TESTE")
        self.assertEqual(r["decisao"], "PENDENTE", r)
        self.assertEqual(before, self.s.motor.state)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 0})

    def test_07_parametros_espaciais_nao_burlam_componentes(self):
        before = copy.deepcopy(self.s.motor.state)
        r = self.cmd("J2", "MULTIATTACK_ROPER_TESTE", {
            "arena_homologada": True,
            "alcance_todas_acoes": True,
            "todos_dados_simulados": [20, 20, 20, 20],
        })
        self.assertEqual(r["decisao"], "PENDENTE", r)
        self.assertEqual(before, self.s.motor.state)

    def test_08_jogador_errado_nao_declara_multiattack(self):
        before = copy.deepcopy(self.s.motor.state)
        r = self.cmd("J1", "MULTIATTACK_ROPER_TESTE")
        self.assertEqual(r["decisao"], "REJEITADA", r)
        self.assertEqual(before, self.s.motor.state)

    def test_09_preflight_fora_de_turno_nao_cria_acao(self):
        self.grip()
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J1")
        x = self.s.motor.prevalidar_multiattack()
        self.assertEqual(x["estado"], "INAPLICAVEL")
        self.assertEqual(x["etapas"], [])
        self.assertEqual(self.cmd("J2", "MULTIATTACK_ROPER_TESTE")
                         ["decisao"], "REJEITADA")

    def test_10_alvo_agarrado_ainda_nao_habilita_multiattack(self):
        self.return_roper_turn()
        x = self.s.motor.prevalidar_multiattack()
        self.assertEqual(x["estado"], "PENDENTE_COMPONENTES")
        self.assertFalse(x["executavel"])
        self.assertIn("Grappled",
                      self.s.motor.get_card(
                          self.s.motor.state, "J1", "CE-001")["condicoes"])

    def test_11_checkpoint_restitui_o_mesmo_preflight(self):
        self.return_roper_turn()
        original = self.s.motor.prevalidar_multiattack()
        restored = SessaoRoperFixture.restaurar(
            self.s.checkpoint(), self.catalogo, self.contrato)
        self.assertEqual(original, restored.motor.prevalidar_multiattack())
        self.assertEqual(self.s.motor.state, restored.motor.state)

    def test_12_privacidade_e_40_copias_por_lado(self):
        x = json.dumps(self.s.motor.prevalidar_multiattack(),
                       ensure_ascii=False)
        self.assertNotIn("CE-002", x)
        self.assertNotIn("AB-POC-001", x)
        self.assertTrue(self.s.motor.validate())
        for p in ("J1", "J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][p]["cartas"]), 40)

if __name__ == "__main__":
    unittest.main()

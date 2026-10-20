"""Inventário auditável de Traits espaciais e Spellcasting da Giant Owl.

Não inventa efeito, alcance, recurso, Action ou estado de jogo.
Fonte real: Catálogo SRD pinado; rolagens da fixture sempre simuladas.
"""
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
from ascend.habilidades_poc_srd import extrair_habilidades_poc_srd
from motor_roper_basico import SessaoRoperFixture, ESCOPO_BASICO


class HabilidadesPOCSRD(unittest.TestCase):
    def setUp(self):
        self.checkout = os.environ["CATALOGO_SRD_DIR"]
        self.contrato = ler_contrato(ROOT)
        self.s = SessaoRoperFixture.criar_de_checkout(
            self.checkout, self.contrato, primeiro="J2",
            maos_fixadas={
                "J1": ["CE-001", "CE-002", "CE-003", "CE-004", "CE-005"],
                "J2": ["AB-POC-017", "AB-POC-001", "AB-POC-002",
                       "AB-POC-003", "AB-POC-004"],
            },
        )
        self.eventos = 0
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

    def command(self, actor, action, args=None):
        self.eventos += 1
        return self.s.comando("habilidades-" + str(self.eventos),
                              actor, action, args or {})

    def ok(self, actor, action, args=None):
        r = self.command(actor, action, args)
        self.assertEqual(r["decisao"], "ACEITA", r)
        return r

    def ficha(self, copy_id):
        return consultar_ficha(
            self.checkout, self.contrato, self.s.referencias, copy_id
        )

    def test_01_roper_spider_climb_espacial_sem_action(self):
        info = extrair_habilidades_poc_srd(self.ficha("AB-POC-017"))
        self.assertEqual(info["passiva"]["nome"], "Spider Climb")
        self.assertEqual(info["passiva"]["categoria_srd"], "Trait")
        self.assertEqual(info["passiva"]["aplicabilidade_card_game"],
                         "SEM_EFEITO_ESPACIAL")
        self.assertFalse(info["passiva"]["executavel_como_action"])
        self.assertFalse(info["passiva"]["consome_acao"])
        self.assertFalse(info["passiva"]["altera_estado"])
        self.assertIsNone(info["conjuracao"])

    def test_02_owl_flyby_nao_gera_ataque_oportunidade(self):
        info = extrair_habilidades_poc_srd(self.ficha("CE-001"))
        self.assertEqual(info["passiva"]["nome"], "Flyby")
        self.assertEqual(info["passiva"]["categoria_srd"], "Trait")
        self.assertEqual(info["passiva"]["aplicabilidade_card_game"],
                         "SEM_EFEITO_ESPACIAL")
        self.assertFalse(info["passiva"]["executavel_como_action"])

    def test_03_spellcasting_extrai_tres_magias_sem_efeitos(self):
        spells = extrair_habilidades_poc_srd(self.ficha("CE-001"))["conjuracao"]
        self.assertEqual(spells["atributo"], "Wisdom")
        self.assertEqual(spells["componentes"], "nenhum")
        self.assertEqual([(s["nome"], s["frequencia_srd"])
                          for s in spells["magias"]], [
            ("Detect Evil and Good", "At Will"),
            ("Detect Magic", "At Will"),
            ("Clairvoyance", "1/Day"),
        ])
        self.assertEqual([s["limite_fonte_por_dia"]
                          for s in spells["magias"]], [None, None, 1])
        self.assertTrue(all(not s["efeito_integrado"] for s in spells["magias"]))
        self.assertFalse(spells["executavel_na_poc"])
        self.assertFalse(spells["usa_recurso"])

    def test_04_alterar_texto_spider_climb_nao_homologa(self):
        ficha = self.ficha("AB-POC-017")
        changed = replace(ficha, ficha_integral=ficha.ficha_integral.replace(
            "without needing to make an ability check.",
            "without needing to make an attack roll.",
        ))
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_poc_srd(changed)

    def test_05_remover_flyby_nao_homologa(self):
        ficha = self.ficha("CE-001")
        changed = replace(ficha, ficha_integral=ficha.ficha_integral.replace(
            "Flyby. The owl doesn't provoke an Opportunity Attack",
            "Other Trait. The owl doesn't provoke an Opportunity Attack",
        ))
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_poc_srd(changed)

    def test_06_magia_nova_nao_homologa(self):
        ficha = self.ficha("CE-001")
        changed = replace(ficha, ficha_integral=ficha.ficha_integral.replace(
            "At Will: Detect Evil and Good, Detect Magic",
            "At Will: Detect Evil and Good, Fireball",
        ))
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_poc_srd(changed)

    def test_07_clairvoyance_frequencia_alterada_nao_homologa(self):
        ficha = self.ficha("CE-001")
        changed = replace(ficha, ficha_integral=ficha.ficha_integral.replace(
            "1/Day: Clairvoyance", "2/Day: Clairvoyance",
        ))
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_poc_srd(changed)

    def test_08_spider_climb_duplicado_nao_homologa(self):
        ficha = self.ficha("AB-POC-017")
        trecho = ("Spider Climb. The roper can climb difficult surfaces, "
                  "including along ceilings, without needing to make an ability check.")
        changed = replace(ficha, ficha_integral=ficha.ficha_integral +
                          "\n" + trecho + "\n")
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_poc_srd(changed)

    def test_09_identidade_versao_erradas_rejeitadas(self):
        ficha = self.ficha("CE-001")
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_poc_srd(replace(ficha, versao="OUTRA"))
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_poc_srd(replace(ficha, id_copia="CE-002"))

    def test_10_preflight_inclui_somente_as_duas_criaturas_ativas(self):
        inventory = self.s.motor.prevalidar_habilidades_poc()
        self.assertEqual(inventory["estado"], "AUDITADO_SEM_EXECUCAO")
        self.assertEqual(set(inventory["campos"]), {"J1", "J2"})
        self.assertEqual(inventory["campos"]["J1"]["passiva"]["nome"], "Flyby")
        self.assertEqual(inventory["campos"]["J2"]["passiva"]["nome"], "Spider Climb")
        self.assertEqual(inventory["campos"]["J1"]["carta_id"], "CE-001")
        self.assertFalse(inventory["consome_acao"])

    def test_11_preflight_puro_sem_mutacao_nem_eventos(self):
        state = copy.deepcopy(self.s.motor.state)
        events = copy.deepcopy(self.s.motor.events)
        head = self.s.motor.head_hash
        for _ in range(4):
            self.s.motor.prevalidar_habilidades_poc()
        self.assertEqual(state, self.s.motor.state)
        self.assertEqual(events, self.s.motor.events)
        self.assertEqual(head, self.s.motor.head_hash)

    def test_12_spider_climb_nao_consume_turno_como_action(self):
        before = copy.deepcopy(self.s.motor.state)
        result = self.command("J2", "SPIDER_CLIMB_ROPER_TESTE")
        self.assertEqual(result["decisao"], "PENDENTE")
        self.assertIn("Trait", result["motivo"])
        self.assertEqual(before, self.s.motor.state)

    def test_13_owl_nao_conjura_magic_por_inventario(self):
        state = copy.deepcopy(self.s.motor.state)
        self.s.motor.prevalidar_habilidades_poc()
        r = self.command("J1", "CONJURAR_MAGIA", {"magia": "Clairvoyance"})
        self.assertNotEqual(r["decisao"], "ACEITA")
        self.assertEqual(self.s.motor.state, state)

    def test_14_pureza_apos_troca_de_turno(self):
        self.ok("J2", "ATAQUE_ROPER_BASICO_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "ataque": "Bite", "d20_simulado": 1, "dano_dados": [],
        })
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J1")
        result = self.s.motor.prevalidar_habilidades_poc()
        self.assertEqual(result["estado"], "AUDITADO_SEM_EXECUCAO")
        self.assertEqual(result["campos"]["J1"]["conjuracao"]
                         ["magias"][2]["nome"], "Clairvoyance")

    def test_15_restaura_checkpoint_e_preflight_estavel(self):
        old = self.s.motor.prevalidar_habilidades_poc()
        restored = SessaoRoperFixture.restaurar(
            self.s.checkpoint(), self.checkout, self.contrato,
        )
        self.assertEqual(restored.motor.prevalidar_habilidades_poc(), old)
        self.assertEqual(restored.motor.state, self.s.motor.state)

    def test_16_40_copias_privacidade_e_placar(self):
        info = self.s.motor.prevalidar_habilidades_poc()
        view = json.dumps(info, ensure_ascii=False)
        self.assertNotIn("CE-002", view)
        self.assertNotIn("AB-POC-001", view)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 0})
        self.assertTrue(self.s.motor.validate())
        for player in ("J1", "J2"):
            self.assertEqual(
                len(self.s.motor.state["jogadores"][player]["cartas"]), 40
            )


if __name__ == "__main__":
    unittest.main()

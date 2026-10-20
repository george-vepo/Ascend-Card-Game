"""SRD Giant Owl Spellcasting: efeitos públicos sem posição; concentração real.

A adaptação do alvo para campos públicos é homebrew da issue #30.
Todos os d20 em testes são simulados externamente, nunca sorteados no motor.
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
from ascend.magias_owl_poc import (
    REGRA_APROVADA, bonus_salvaguarda_constituicao_owl,
    detectar_publico, DURACAO_CONCENTRACAO_RODADAS,
)
from motor_roper_basico import (
    SessaoRoperFixture, ESCOPO_BASICO, ESCOPO_MULTIATTACK,
    ESCOPO_CONJURACAO_OWL,
)


class OwlMagiaPublica(unittest.TestCase):
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
            "d20_simulados": {"J1": 20, "J2": 1},
        })
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J1")

    def run_action(self, actor, action, args=None, event_id=None):
        self.n += 1
        return self.s.comando(
            event_id or "owl-spell-" + str(self.n), actor, action, args or {},
        )

    def ok(self, actor, action, args=None):
        r = self.run_action(actor, action, args)
        self.assertEqual(r["decisao"], "ACEITA", r)
        return r["resultado"]

    def cast(self, magia, **kwargs):
        return self.ok("J1", "CONJURAR_MAGIA_OWL_TESTE", {
            "aceite_escopo": ESCOPO_CONJURACAO_OWL, "magia": magia,
            **kwargs,
        })

    def roper_bite(self, roll=10, damage=None, save=None):
        params = {
            "aceite_escopo": ESCOPO_BASICO,
            "ataque": "Bite", "d20_simulado": roll,
            "dano_dados": [] if damage is None else damage,
        }
        if save is not None:
            params["d20_concentracao_simulado"] = save
        return self.run_action("J2", "ATAQUE_ROPER_BASICO_TESTE", params)

    def concentration(self):
        return self.s.motor.state["combate"].get("concentracao_owl")

    def owl(self):
        return self.s.motor.get_card(self.s.motor.state, "J1", "CE-001")

    def back_to_owl(self):
        r = self.roper_bite(roll=1)
        self.assertEqual(r["decisao"], "ACEITA", r)
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J1")

    def test_01_save_constituicao_da_ficha_externa_pinado(self):
        f = consultar_ficha(self.checkout, self.contrato,
                           self.s.referencias, "CE-001")
        self.assertEqual(bonus_salvaguarda_constituicao_owl(f), 1)

    def test_02_ficha_alterada_rejeita_constituicao(self):
        f = consultar_ficha(self.checkout, self.contrato,
                           self.s.referencias, "CE-001")
        t = f.ficha_integral.replace("Con 12 +1 +1", "Con 12 +1 +9")
        self.assertNotEqual(t, f.ficha_integral)
        with self.assertRaises(FichaConflitante):
            bonus_salvaguarda_constituicao_owl(
                replace(f, ficha_integral=t),
            )

    def test_03_preflight_tres_magias_com_status_individual(self):
        pre = self.s.motor.prevalidar_conjuracao_owl()
        self.assertEqual(pre["estado"], "AUDITADA")
        self.assertTrue(pre["executavel"])
        self.assertEqual([m["estado"] for m in pre["magias"]],
                         ["PRONTA_COM_ACTION", "PRONTA_COM_ACTION",
                          "INAPLICAVEL_SEM_LOCAL_E_TEMPO_DE_CONJURACAO"])
        self.assertIsNone(pre["concentracao_atual"])

    def test_04_detect_evil_good_identifica_somente_campos(self):
        out = self.cast("Detect Evil and Good")
        self.assertEqual(out["tipo_acao"], "Action")
        self.assertEqual(out["regra_homebrew"], REGRA_APROVADA)
        hit = out["informacao_publica"]["criaturas_identificadas"]
        self.assertEqual(hit, [
            {"jogador": "J1", "carta_id": "CE-001", "tipo_srd": "Celestial"},
            {"jogador": "J2", "carta_id": "AB-POC-017", "tipo_srd": "Aberration"},
        ])
        self.assertIsNone(out["informacao_publica"]["hallow_detectado"])
        self.assertEqual(out["concentracao_max_rodadas"], 100)
        self.assertEqual(self.s.motor.state["ator_da_vez"], "J2")

    def test_05_detect_magic_detecta_apenas_propria_concentracao_publica(self):
        out = self.cast("Detect Magic")
        info = out["informacao_publica"]
        self.assertEqual(info["efeitos_magicos_publicos"], [{
            "jogador": "J1", "carta_id": "CE-001",
            "origem": "CONCENTRACAO_OWL_PUBLICA",
        }])
        self.assertFalse(info["aura_escola_revelada"])
        self.assertEqual(info["cobertura"],
                         "SOMENTE_EFEITOS_HOMOLOGADOS_NO_CAMPO")

    def test_06_detect_magic_nao_confunde_tentaculos_com_magia(self):
        self.cast("Detect Magic")
        self.ok("J2", "TENTACLE_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "tentaculo_numero": 1, "d20_simulado": 10,
        })
        out = detectar_publico(self.s.motor.state, "Detect Magic")
        self.assertEqual(len(out["efeitos_magicos_publicos"]), 1)
        self.assertEqual(self.owl()["condicoes"], ["Grappled", "Poisoned"])

    def test_07_clairvoyance_rejeitada_sem_gastar_uso_diario(self):
        old = copy.deepcopy(self.s.motor.state)
        r = self.run_action("J1", "CONJURAR_MAGIA_OWL_TESTE", {
            "aceite_escopo": ESCOPO_CONJURACAO_OWL, "magia": "Clairvoyance",
        })
        self.assertEqual(r["decisao"], "REJEITADA", r)
        self.assertIn("10 minutos", r["motivo"])
        self.assertEqual(self.s.motor.state, old)
        self.assertNotIn("concentracao_owl", self.s.motor.state["combate"])

    def test_08_conjurar_sem_confirmacao_pendente_sem_mutacao(self):
        old = copy.deepcopy(self.s.motor.state)
        r = self.run_action("J1", "CONJURAR_MAGIA_OWL_TESTE", {
            "magia": "Detect Magic",
        })
        self.assertEqual(r["decisao"], "PENDENTE")
        self.assertEqual(self.s.motor.state, old)

    def test_09_substituir_concentracao_em_turno_futuro(self):
        self.cast("Detect Evil and Good")
        self.back_to_owl()
        out = self.cast("Detect Magic")
        self.assertEqual(out["concentracao_anterior_encerrada"],
                         "Detect Evil and Good")
        self.assertEqual(self.concentration()["magia"], "Detect Magic")
        self.assertEqual(self.concentration()["rodada_inicio"], 2)

    def test_10_uma_magia_e_uma_action_nao_dois_turnos(self):
        self.cast("Detect Magic")
        before = copy.deepcopy(self.s.motor.state)
        r = self.run_action("J1", "CONJURAR_MAGIA_OWL_TESTE", {
            "aceite_escopo": ESCOPO_CONJURACAO_OWL,
            "magia": "Detect Evil and Good",
        })
        self.assertEqual(r["decisao"], "REJEITADA")
        self.assertEqual(before, self.s.motor.state)

    def test_11_dano_com_concentracao_sem_d20_pendente_atomicamente(self):
        self.cast("Detect Magic")
        state = copy.deepcopy(self.s.motor.state)
        head = self.s.motor.head_hash
        result = self.roper_bite(roll=10, damage=[1, 1, 1])
        self.assertEqual(result["decisao"], "PENDENTE")
        self.assertEqual(state, self.s.motor.state)
        self.assertEqual(head, self.s.motor.head_hash)

    def test_12_salvaguarda_concentracao_sucesso_cd10(self):
        self.cast("Detect Magic")
        r = self.roper_bite(roll=10, damage=[1, 1, 1], save=9)
        self.assertEqual(r["decisao"], "ACEITA")
        detail = r["resultado"]["concentracao"]
        self.assertEqual(detail["cd"], 10)
        self.assertEqual(detail["total"], 10)
        self.assertTrue(detail["manteve"])
        self.assertEqual(self.owl()["pv_atual"], 12)
        self.assertEqual(self.concentration()["magia"], "Detect Magic")

    def test_13_salvaguarda_concentracao_falha_remove_magia(self):
        self.cast("Detect Evil and Good")
        r = self.roper_bite(roll=10, damage=[1, 1, 1], save=1)
        self.assertEqual(r["decisao"], "ACEITA")
        self.assertFalse(r["resultado"]["concentracao"]["manteve"])
        self.assertIsNone(self.concentration())
        self.assertEqual(self.owl()["pv_atual"], 12)

    def test_14_erro_d20_concentracao_rejeita_e_rollback(self):
        self.cast("Detect Magic")
        old = copy.deepcopy(self.s.motor.state)
        r = self.roper_bite(roll=10, damage=[1, 1, 1], save=21)
        self.assertEqual(r["decisao"], "REJEITADA")
        self.assertEqual(self.s.motor.state, old)

    def test_15_ataque_erro_ou_dano_zero_nao_requer_save(self):
        self.cast("Detect Magic")
        r = self.roper_bite(roll=1)
        self.assertEqual(r["decisao"], "ACEITA")
        self.assertIsNone(r["resultado"]["concentracao"])
        self.assertIsNotNone(self.concentration())

    def test_16_multiattack_pede_salvaguarda_no_primeiro_bite(self):
        self.cast("Detect Magic")
        before = copy.deepcopy(self.s.motor.state)
        payload = {
            "aceite_escopo": ESCOPO_MULTIATTACK,
            "tentaculos": [
                {"tentaculo_numero": 1, "d20_simulado": 1},
                {"tentaculo_numero": 2, "d20_simulado": 1},
            ],
            "bites": [
                {"d20_simulado": 10, "dano_dados": [1, 1, 1]},
                {"d20_simulado": 1, "dano_dados": []},
            ],
        }
        r = self.run_action("J2", "MULTIATTACK_ROPER_TESTE", payload)
        self.assertEqual(r["decisao"], "PENDENTE")
        self.assertEqual(self.s.motor.state, before)

    def test_17_multiattack_duplo_bite_saves_separados(self):
        self.cast("Detect Magic")
        out = self.ok("J2", "MULTIATTACK_ROPER_TESTE", {
            "aceite_escopo": ESCOPO_MULTIATTACK,
            "tentaculos": [
                {"tentaculo_numero": 1, "d20_simulado": 1},
                {"tentaculo_numero": 2, "d20_simulado": 1},
            ],
            "bites": [
                {"d20_simulado": 10, "dano_dados": [1, 1, 1],
                 "d20_concentracao_simulado": 9},
                {"d20_simulado": 10, "dano_dados": [1, 1, 1],
                 "d20_concentracao_simulado": 1},
            ],
        })
        self.assertTrue(out["componentes"][3]["concentracao"]["manteve"])
        self.assertFalse(out["componentes"][4]["concentracao"]["manteve"])
        self.assertIsNone(self.concentration())
        self.assertEqual(self.owl()["pv_atual"], 5)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 0})

    def test_18_ko_limpa_concentracao_sem_salvaguarda(self):
        self.cast("Detect Magic")
        out = self.ok("J2", "ATAQUE_ROPER_BASICO_TESTE", {
            "aceite_escopo": ESCOPO_BASICO,
            "ataque": "Bite", "d20_simulado": 20,
            "dano_dados": [8] * 6,
        })
        self.assertTrue(out["ko"])
        self.assertEqual(out["encerramento_tentaculos"]
                         ["concentracao_encerrada"], "Detect Magic")
        self.assertIsNone(self.concentration())
        self.assertEqual(self.s.motor.state["placar"]["J2"], 1)

    def test_19_encerrar_concentracao_gratis_fora_do_turno(self):
        self.cast("Detect Evil and Good")
        old_turn = self.s.motor.state["ator_da_vez"]
        out = self.ok("J1", "ENCERRAR_CONCENTRACAO_OWL_TESTE")
        self.assertFalse(out["consome_acao"])
        self.assertEqual(self.s.motor.state["ator_da_vez"], old_turn)
        self.assertIsNone(self.concentration())

    def test_20_preflight_e_resultados_nao_vazam_maos(self):
        pre = self.s.motor.prevalidar_conjuracao_owl()
        self.cast("Detect Evil and Good")
        payload = json.dumps({
            "consulta": pre, "mesa": self.s.mesa_publica(),
            "ultimo_evento": self.s.motor.events[-1]["resultado"],
        }, ensure_ascii=False)
        self.assertNotIn("CE-002", payload)
        self.assertNotIn("AB-POC-001", payload)
        self.assertNotIn("monte_ordem_ids", payload)
        self.assertTrue(self.s.motor.validate())
        for p in ("J1", "J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][p]["cartas"]), 40)

    def test_21_checkpoint_restaura_concentracao(self):
        self.cast("Detect Magic")
        cp = self.s.checkpoint()
        restored = SessaoRoperFixture.restaurar(
            cp, self.checkout, self.contrato,
        )
        self.assertEqual(restored.motor.state, self.s.motor.state)
        self.assertEqual(restored.motor.prevalidar_conjuracao_owl()
                         ["concentracao_atual"], "Detect Magic")

    def test_22_idempotencia_nao_duplica_action(self):
        payload = {
            "aceite_escopo": ESCOPO_CONJURACAO_OWL,
            "magia": "Detect Evil and Good",
        }
        first = self.run_action("J1", "CONJURAR_MAGIA_OWL_TESTE",
                                payload, event_id="magia-idempotente")
        second = self.run_action("J1", "CONJURAR_MAGIA_OWL_TESTE",
                                 payload, event_id="magia-idempotente")
        self.assertEqual(first, second)
        self.assertEqual(len([x for x in self.s.motor.events
                              if x["evento_id"] == "magia-idempotente"]), 1)

    def test_23_limite_cem_rodadas_interrompe_concentracao(self):
        self.cast("Detect Magic")
        # Simula a passagem das rodadas *mediante ações legais*, sem alterar
        # o contador manualmente, garantindo a duração auditável.
        for _ in range(DURACAO_CONCENTRACAO_RODADAS):
            self.ok("J2", "ATAQUE_ROPER_BASICO_TESTE", {
                "aceite_escopo": ESCOPO_BASICO,
                "ataque": "Bite", "d20_simulado": 1, "dano_dados": [],
            })
            if self.concentration() is None:
                break
            self.ok("J1", "ATAQUE_ROPER_BASICO_TESTE", {
                "aceite_escopo": ESCOPO_BASICO,
                "ataque": "Talons", "d20_simulado": 1, "dano_dados": [],
            })
        self.assertIsNone(self.concentration())

    def test_24_fora_da_vez_ou_mago_errado_rejeitados(self):
        old = copy.deepcopy(self.s.motor.state)
        r = self.run_action("J2", "CONJURAR_MAGIA_OWL_TESTE", {
            "aceite_escopo": ESCOPO_CONJURACAO_OWL, "magia": "Detect Magic",
        })
        self.assertEqual(r["decisao"], "REJEITADA")
        self.assertEqual(self.s.motor.state, old)


if __name__ == "__main__":
    unittest.main()

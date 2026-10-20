"""Gibbering Mouther: pré-validação SRD fiel, sem arena ou execução.

Origem: catálogo SRD externo pinado, ficha p. 288. Não há partida oficial.
"""
from __future__ import annotations

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
from ascend.gibbering_mouther_srd import extrair_habilidades_gibbering_mouther
from motor_fichas_poc import SessaoFichasFixture
from preflight_gibbering_mouther import prevalidar_gibbering_mouther
from motor_poc import UnresolvedRule


class MoutherPreflightReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogo = os.environ["CATALOGO_SRD_DIR"]
        cls.contrato = ler_contrato(ROOT)

    def ficha(self, copia="AB-POC-008"):
        if not hasattr(self, "s"):
            self.iniciar()
        return consultar_ficha(
            self.catalogo, self.contrato, self.s.referencias, copia
        )

    def iniciar(self):
        self.s = SessaoFichasFixture.criar_de_checkout(
            self.catalogo, self.contrato,
            primeiro="J2",
            maos_fixadas={
                "J1": ["CE-001", "CE-002", "CE-003", "CE-004", "CE-005"],
                "J2": ["AB-POC-008", "AB-POC-001", "AB-POC-002",
                       "AB-POC-003", "AB-POC-004"],
            },
        )
        self.i = 0

    def send(self, p, action, params=None):
        self.i += 1
        return self.s.comando("mouther-pre-" + str(self.i), p, action, params or {})

    def ok(self, p, action, params=None):
        r = self.send(p, action, params)
        self.assertEqual(r["decisao"], "ACEITA", r)
        return r

    def invocar(self):
        self.iniciar()
        for p in ("J2", "J1"):
            self.ok(p, "TROCAR", {"descartar": []})
        for p, cid in (("J2", "AB-POC-008"), ("J1", "CE-001")):
            self.ok(p, "INVOCAR", {"carta_id": cid})
            self.ok(p, "PRONTO_CRIATURA")

    def test_01_identidade_real_e_imunidade_prone(self):
        self.iniciar()
        inventario = extrair_habilidades_gibbering_mouther(self.ficha())
        self.assertEqual(inventario["carta_id"], "AB-POC-008")
        self.assertEqual(inventario["id_catalogo"], "AT-001")
        self.assertEqual(inventario["imunidade_condicao"], ["Prone"])
        self.assertEqual(inventario["versao"], "SRD 5.2.1")
        self.assertEqual(len(inventario["origem_ficha_sha256"]), 64)

    def test_02_aberrant_ground_espacial_nao_executa(self):
        self.iniciar()
        a = extrair_habilidades_gibbering_mouther(self.ficha())["passivas"][0]
        self.assertEqual(a["nome"], "Aberrant Ground")
        self.assertEqual(a["emanacao_ft_fonte"], 10)
        self.assertEqual(a["estado_poc"], "SEM_EFEITO_ESPACIAL")
        self.assertFalse(a["executavel"])

    def test_03_gibbering_dc10_d8_e_resultados_fieis(self):
        self.iniciar()
        a = extrair_habilidades_gibbering_mouther(self.ficha())["passivas"][1]
        self.assertEqual(a["cd"], 10)
        self.assertEqual(a["salvaguarda"], "Wisdom")
        self.assertEqual(a["alcance_ft_metadado"], 20)
        self.assertEqual(a["dado_efeito"], [1, 8])
        self.assertEqual([x["faces"] for x in a["tabela_fonte"]],
                         [[1, 2, 3, 4], [5, 6], [7, 8]])
        self.assertFalse(a["executavel"])

    def test_04_blinding_spittle_recharge_dc_dano_condicao(self):
        self.iniciar()
        a = extrair_habilidades_gibbering_mouther(self.ficha())["acoes"][1]
        self.assertEqual(a["nome"], "Blinding Spittle")
        self.assertEqual(a["recarga_d6"], [5, 6])
        self.assertEqual(a["salvaguarda"], "Dexterity")
        self.assertEqual(a["cd"], 10)
        self.assertEqual(a["dano_falha"],
                         {"dados": [2, 6], "media_fonte": 7, "tipo": "Radiant"})
        self.assertEqual(a["condicao_falha"], "Blinded")
        self.assertEqual(a["duracao"], "ATE_FIM_PROXIMO_TURNO_MOUTHER")
        self.assertEqual(a["estado_poc"],
                         "PENDENTE_ALVOS_DA_AREA_SEM_POSICIONAMENTO")

    def test_05_bite_prone_ko_e_dano_exato_sem_executar(self):
        self.iniciar()
        a = extrair_habilidades_gibbering_mouther(self.ficha())["acoes"][0]
        self.assertEqual(a["bonus_ataque"], 2)
        self.assertEqual(a["dano"]["dados"], [2, 6])
        self.assertEqual(a["dano"]["tipo"], "Piercing")
        self.assertTrue(a["prone_se_alvo_medium_ou_menor"])
        self.assertTrue(a["absorve_corpo_em_ko"])
        self.assertFalse(a["executavel"])

    def test_06_ficha_modificada_cd_nao_homologa(self):
        self.iniciar()
        f = self.ficha()
        txt = f.ficha_integral.replace(
            "Wisdom Saving Throw: DC 10", "Wisdom Saving Throw: DC 11"
        )
        self.assertNotEqual(txt, f.ficha_integral)
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_gibbering_mouther(
                replace(f, ficha_integral=txt)
            )

    def test_07_ficha_modificada_recharge_nao_homologa(self):
        self.iniciar()
        f = self.ficha()
        txt = f.ficha_integral.replace(
            "Blinding Spittle (Recharge 5–6)",
            "Blinding Spittle (Recharge 4–6)"
        )
        self.assertNotEqual(txt, f.ficha_integral)
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_gibbering_mouther(
                replace(f, ficha_integral=txt)
            )

    def test_08_ficha_sem_condicao_blinded_nao_homologa(self):
        self.iniciar()
        f = self.ficha()
        txt = f.ficha_integral.replace(
            "Blinded condition", "Poisoned condition"
        )
        self.assertNotEqual(txt, f.ficha_integral)
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_gibbering_mouther(
                replace(f, ficha_integral=txt)
            )

    def test_09_regra_prone_da_fonte_nao_reinterpretada(self):
        self.iniciar()
        f = self.ficha()
        txt = f.ficha_integral.replace(
            "If the target is a Medium or smaller creature",
            "If the target is a Large or smaller creature"
        )
        self.assertNotEqual(txt, f.ficha_integral)
        with self.assertRaises(FichaConflitante):
            extrair_habilidades_gibbering_mouther(
                replace(f, ficha_integral=txt)
            )

    def test_10_rejeita_copia_tipo_ou_versao_incorretos(self):
        self.iniciar()
        f = self.ficha()
        for changed in (replace(f, id_copia="AB-POC-017"),
                        replace(f, id_catalogo="AT-002"),
                        replace(f, versao="SRD 5.1")):
            with self.subTest(changed=changed.id_copia):
                with self.assertRaises(FichaConflitante):
                    extrair_habilidades_gibbering_mouther(changed)

    def test_11_sem_mouther_no_campo_preflight_inaplicavel(self):
        self.iniciar()
        before = copy.deepcopy(self.s.motor.state)
        out = prevalidar_gibbering_mouther(self.s)
        self.assertEqual(out["estado"], "INAPLICAVEL")
        self.assertFalse(out["executavel"])
        self.assertEqual(self.s.motor.state, before)

    def test_12_mouther_invocado_fonte_valida_bloqueios_legiveis(self):
        self.invocar()
        out = prevalidar_gibbering_mouther(self.s)
        self.assertEqual(out["estado"], "FICHA_VERIFICADA_EXECUCAO_PENDENTE")
        self.assertEqual(out["carta_id"], "AB-POC-008")
        self.assertEqual(len(out["bloqueios"]), 3)
        self.assertFalse(out["executavel"])
        self.assertFalse(out["consome_acao"])
        self.assertFalse(out["altera_estado"])
        self.assertEqual(out["habilidades"]["origem_ficha_sha256"],
                         self.s.motor.get_card(
                             self.s.motor.state, "J2", "AB-POC-008"
                         )["origem_ficha"]["sha256_documento"])

    def test_13_preflight_puro_repetido_sem_eventos_ou_hash(self):
        self.invocar()
        before = copy.deepcopy(self.s.motor.state)
        events = copy.deepcopy(self.s.motor.events)
        hash_before = self.s.motor.head_hash
        for _ in range(3):
            prevalidar_gibbering_mouther(self.s)
        self.assertEqual(self.s.motor.state, before)
        self.assertEqual(self.s.motor.events, events)
        self.assertEqual(self.s.motor.head_hash, hash_before)

    def test_14_preflight_publico_nao_revela_maos(self):
        self.invocar()
        out = prevalidar_gibbering_mouther(self.s)
        body = json.dumps(out, ensure_ascii=False)
        self.assertNotIn("CE-002", body)
        self.assertNotIn("AB-POC-001", body)
        self.assertNotIn("monte_ordem_ids", body)
        for p in ("J1", "J2"):
            self.assertEqual(
                len(self.s.motor.state["jogadores"][p]["cartas"]), 40
            )

    def test_15_checkpoint_inalterado_pela_consulta(self):
        self.invocar()
        original = self.s.checkpoint()
        prevalidar_gibbering_mouther(self.s)
        self.assertEqual(self.s.checkpoint(), original)
        restored = SessaoFichasFixture.restaurar(
            original, self.catalogo, self.contrato
        )
        self.assertEqual(restored.motor.state, self.s.motor.state)

    def test_16_fonte_divergente_no_campo_nao_homologa(self):
        self.invocar()
        card = self.s.motor.state["jogadores"]["J2"]["cartas"]["AB-POC-008"]
        previous = card["origem_ficha"]["sha256_documento"]
        card["origem_ficha"]["sha256_documento"] = "0" * 64
        with self.assertRaises(UnresolvedRule):
            prevalidar_gibbering_mouther(self.s)
        card["origem_ficha"]["sha256_documento"] = previous
        self.assertTrue(self.s.motor.validate())


if __name__ == "__main__":
    unittest.main()


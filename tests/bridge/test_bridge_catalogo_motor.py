"""Integração estrutural em fixtures sintéticas; NUNCA partida oficial."""
import copy
import json
import sys
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experimental/legacy/src"))
sys.path.insert(0, str(ROOT / "experimental/integration"))
from ascend.catalogo_poc import CopiaReferencia
from bridge_catalogo_motor import SessaoFixture, FonteDivergente
from motor_poc import InvalidAction


def referencias():
    cards = []
    for p, prefix, tipo in [
        ("J1", "CE", "Celestial"),
        ("J2", "AB-POC", "Aberração"),
    ]:
        for i in range(1, 41):
            cards.append(CopiaReferencia(
                jogador=p, id_copia=f"{prefix}-{i:03d}",
                posicao_referencia=i, nome=f"{tipo} teste {i}",
                tipo=tipo, nd=Decimal("0.25"), raridade="Comum",
                id_catalogo=None, fonte_classificacao_ficha="FIXTURE",
                status_suporte="NAO_HOMOLOGADO",
                homologacao_declarada_catalogo="NAO",
            ))
    return cards


PROV = {
    "repositor_io": "FIXTURE-SINTETICA",
    "revisao_git": None,
    "revisao_verificada": False,
    "sha256_conteudos": {"celestial": "TESTE-CE", "aberracao": "TESTE-AB"},
    "copias": {"J1": 40, "J2": 40},
}


class PontePOCTest(unittest.TestCase):
    def setUp(self):
        self.refs = referencias()
        self.g = SessaoFixture.de_referencias(self.refs, PROV)

    def test_01_oitenta_identidades(self):
        s = self.g.motor.state
        for p in ("J1", "J2"):
            self.assertEqual(len(s["jogadores"][p]["cartas"]), 40)
            self.assertEqual(len(self.g.motor.hand(s, p)), 5)
        self.assertTrue(self.g.motor.validate())
        self.assertTrue(all(r["pv_fonte"] is None for r in self.g.registros))

    def test_02_ausencia_de_pv_bloqueia_invocacao_sem_mutacao(self):
        self.assertEqual(self.g.comando("t1", "J1", "TROCAR", {"descartar":[]})["decisao"],"ACEITA")
        self.assertEqual(self.g.comando("t2", "J2", "TROCAR", {"descartar":[]})["decisao"],"ACEITA")
        estado = copy.deepcopy(self.g.motor.state)
        resp = self.g.comando("pend1", "J1", "INVOCAR", {"carta_id":"CE-001"})
        self.assertEqual(resp["decisao"], "PENDENTE")
        self.assertEqual(self.g.motor.state, estado)
        self.assertEqual(len(self.g.motor.events), 2)

    def test_03_pv_simulados_explicitos_permite_teste_mas_nao_jogo(self):
        g = SessaoFixture.de_referencias(
            self.refs, PROV, pv_simulados={"CE-001": 19}
        )
        g.comando("t1", "J1", "TROCAR", {"descartar":[]})
        g.comando("t2", "J2", "TROCAR", {"descartar":[]})
        resp=g.comando("t3", "J1", "INVOCAR", {"carta_id":"CE-001"})
        self.assertEqual(resp["decisao"], "ACEITA")
        self.assertEqual(g.motor.get_card(g.motor.state, "J1", "CE-001")["pv_atual"], 19)
        self.assertIn("FIXTURE", g.mesa_publica()["ambiente"])

    def test_04_visao_publica_nao_revela_maos_ou_montes(self):
        public = self.g.mesa_publica()
        text = json.dumps(public)
        self.assertNotIn("CE-002", text)
        self.assertNotIn("AB-POC-002", text)
        self.assertNotIn("monte_ordem_ids", text)
        self.assertNotIn("minha_mao", text)

    def test_05_jogador_ve_somente_propria_mao(self):
        view = self.g.visao_privada("J1")
        ids={x["id"] for x in view["minha_mao"]}
        self.assertEqual(ids, {f"CE-{i:03d}" for i in range(1,6)})
        self.assertNotIn("AB-POC-001", json.dumps(view))

    def test_06_checkpoint_restauravel_mesma_fonte(self):
        self.g.comando("t1", "J1", "TROCAR", {"descartar":[]})
        restored = SessaoFixture.restaurar(
            self.g.checkpoint(), self.refs, PROV
        )
        self.assertEqual(restored.motor.state, self.g.motor.state)
        self.assertEqual(restored.mesa_publica(), self.g.mesa_publica())

    def test_07_checkpoint_rejeita_mudanca_de_nome_sem_mudar_id(self):
        changed = self.refs.copy()
        changed[0] = replace(changed[0], nome="Outra criatura")
        with self.assertRaises(FonteDivergente):
            SessaoFixture.restaurar(self.g.checkpoint(), changed, PROV)

    def test_08_checkpoint_rejeita_outro_commit(self):
        prov = copy.deepcopy(PROV)
        prov["revisao_git"] = "HASH-DIFERENTE"
        with self.assertRaises(FonteDivergente):
            SessaoFixture.restaurar(self.g.checkpoint(), self.refs, prov)

    def test_09_checkpoint_rejeita_outro_pv_simulado(self):
        g = SessaoFixture.de_referencias(
            self.refs, PROV, pv_simulados={"CE-001": 19}
        )
        with self.assertRaises(FonteDivergente):
            SessaoFixture.restaurar(
                g.checkpoint(), self.refs, PROV,
                pv_simulados={"CE-001": 20},
            )

    def test_10_sem_checkpoint_oficial(self):
        cp = self.g.checkpoint()
        self.assertTrue(cp["unicamente_teste"])
        cp["unicamente_teste"] = False
        with self.assertRaises(FonteDivergente):
            SessaoFixture.restaurar(cp, self.refs, PROV)

    def test_11_pv_para_copia_inexistente_rejeitado(self):
        with self.assertRaises(InvalidAction):
            SessaoFixture.de_referencias(
                self.refs, PROV, pv_simulados={"X-777": 99}
            )

    def test_12_pv_booleano_rejeitado(self):
        with self.assertRaises(InvalidAction):
            SessaoFixture.de_referencias(
                self.refs, PROV, pv_simulados={"CE-001": True}
            )

    def test_13_id_duplicado_rejeitado(self):
        changed = self.refs.copy()
        changed[1] = replace(changed[1], id_copia="CE-001")
        with self.assertRaises(InvalidAction):
            SessaoFixture.de_referencias(changed, PROV)

    def test_14_id_pulado_rejeitado(self):
        changed = self.refs.copy()
        changed[0] = replace(changed[0], id_copia="CE-099")
        with self.assertRaises(InvalidAction):
            SessaoFixture.de_referencias(changed, PROV)

    def test_15_79_cartas_rejeitado(self):
        with self.assertRaises(InvalidAction):
            SessaoFixture.de_referencias(self.refs[:-1], PROV)

    def test_16_posicao_divergente_rejeitada(self):
        changed = self.refs.copy()
        changed[0] = replace(changed[0], posicao_referencia=2)
        with self.assertRaises(InvalidAction):
            SessaoFixture.de_referencias(changed, PROV)

    def test_17_sem_dois_hashes_de_origem(self):
        p = dict(PROV)
        p["sha256_conteudos"] = {"celestial":"1"}
        with self.assertRaises(InvalidAction):
            SessaoFixture.de_referencias(self.refs, p)

    def test_18_evento_idempotente(self):
        first = self.g.comando("x1", "J1", "TROCAR", {"descartar":[]})
        second = self.g.comando("x1", "J1", "TROCAR", {"descartar":[]})
        self.assertEqual(first, second)
        self.assertEqual(len(self.g.motor.events), 1)

    def test_19_fase_invalida_preserva_estado(self):
        before = copy.deepcopy(self.g.motor.state)
        result = self.g.comando("x1", "J2", "INVOCAR", {"carta_id":"AB-POC-001"})
        self.assertEqual(result["decisao"], "REJEITADA")
        self.assertEqual(self.g.motor.state, before)

    def test_20_40_decks_estaveis_apos_duas_trocas(self):
        self.g.comando("t1", "J1", "TROCAR", {"descartar":["CE-001"]})
        self.g.comando("t2", "J2", "TROCAR", {"descartar":["AB-POC-001"]})
        self.assertEqual(len(self.g.motor.state["jogadores"]["J1"]["cartas"]),40)
        self.assertEqual(len(self.g.motor.state["jogadores"]["J2"]["cartas"]),40)
        self.assertTrue(self.g.motor.validate())


if __name__ == "__main__":
    unittest.main()

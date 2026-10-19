"""Integração contra checkout externo pinado; nunca uma partida oficial."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experimental/legacy/src"))
sys.path.insert(0, str(ROOT / "experimental/integration"))

from ascend.catalogo_poc import ler_contrato
from bridge_catalogo_motor import SessaoFixture


class CatalogoParaMotor(unittest.TestCase):
    def test_oitenta_copias_e_pv_sob_demanda(self):
        raiz = os.environ["CATALOGO_SRD_DIR"]
        fixture = SessaoFixture.de_checkout(raiz, ler_contrato(ROOT))
        self.assertEqual(len(fixture.registros), 80)
        self.assertTrue(fixture.proveniencia["revisao_verificada"])
        self.assertEqual(
            len(fixture.motor.state["jogadores"]["J1"]["cartas"]), 40
        )
        self.assertEqual(
            len(fixture.motor.state["jogadores"]["J2"]["cartas"]), 40
        )
        self.assertTrue(all(x["pv_fonte"] is None for x in fixture.registros))
        before = fixture.mesa_publica()
        self.assertEqual(before["placar"], {"J1": 0, "J2": 0})
        self.assertEqual(fixture.comando(
            "t1", "J1", "TROCAR", {"descartar":[]}
        )["decisao"], "ACEITA")
        self.assertEqual(fixture.comando(
            "t2", "J2", "TROCAR", {"descartar":[]}
        )["decisao"], "ACEITA")
        current = fixture.motor.state.copy()
        pend = fixture.comando(
            "t3", "J1", "INVOCAR", {"carta_id":"CE-001"}
        )
        self.assertEqual(pend["decisao"], "PENDENTE")
        self.assertEqual(fixture.motor.state, current)
        self.assertEqual(fixture.motor.state["placar"], {"J1": 0, "J2": 0})
        self.assertTrue(fixture.motor.validate())


if __name__ == "__main__":
    unittest.main()

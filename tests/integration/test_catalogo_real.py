"""Lê somente o checkout externo fixado; não grava dados no Ascend."""
import os
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
from ascend.catalogo_poc import carregar_referencias, ler_contrato


class CatalogoReal(unittest.TestCase):
    def test_revisao_decks_e_identidades(self):
        origem = os.environ["CATALOGO_SRD_DIR"]
        referencias, meta = carregar_referencias(
            origem, ler_contrato(RAIZ), exigir_revisao=True
        )
        self.assertTrue(meta["revisao_verificada"])
        self.assertEqual(len(referencias), 80)
        self.assertEqual(sum(c.jogador == "J1" for c in referencias), 40)
        self.assertEqual(sum(c.jogador == "J2" for c in referencias), 40)
        self.assertEqual(len(set(c.id_copia for c in referencias)), 80)
        self.assertEqual({c.tipo for c in referencias}, {"Celestial", "Aberração"})
        self.assertTrue(all(c.nd >= 0 for c in referencias))
        self.assertEqual(referencias[0].id_copia, "CE-001")
        self.assertEqual(referencias[40].id_copia, "AB-POC-001")

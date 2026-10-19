"""Testa quatro fichas externas sem copiar a fonte para o Ascend."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from ascend.catalogo_poc import carregar_referencias, ler_contrato
from ascend.fichas_srd import consultar_ficha, FichaPendente


class TesteAcervoSRDReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checkout = os.environ["CATALOGO_SRD_DIR"]
        cls.contrato = ler_contrato(ROOT)
        cls.cartas, cls.proveniencia = carregar_referencias(
            cls.checkout, cls.contrato, exigir_revisao=True
        )

    def test_gibbering_mouther(self):
        f = consultar_ficha(
            self.checkout, self.contrato, self.cartas, "AB-POC-008"
        )
        self.assertEqual((f.nome, f.ca, f.pv_maximos), ("Gibbering Mouther", 9, 52))
        self.assertIn("Blinding Spittle", f.ficha_integral)
        self.assertFalse(f.mecanicas_automaticamente_homologadas)

    def test_roper(self):
        f = consultar_ficha(
            self.checkout, self.contrato, self.cartas, "AB-POC-017"
        )
        self.assertEqual((f.nome, f.ca, f.pv_maximos), ("Roper", 20, 93))
        self.assertIn("Tentacle", f.ficha_integral)

    def test_aboleth(self):
        f = consultar_ficha(
            self.checkout, self.contrato, self.cartas, "AB-POC-031"
        )
        self.assertEqual((f.nome, f.ca, f.pv_maximos), ("Aboleth", 17, 150))
        self.assertIn("Lash", f.ficha_integral)

    def test_outra_ficha_nao_foi_inferida(self):
        with self.assertRaises(FichaPendente):
            consultar_ficha(
                self.checkout, self.contrato, self.cartas, "AB-POC-002"
            )

    def test_giant_owl_com_fonte_celestial_real(self):
        f = consultar_ficha(
            self.checkout, self.contrato, self.cartas, "CE-001"
        )
        self.assertEqual((f.nome, f.ca, f.pv_maximos), ("Giant Owl", 12, 19))
        self.assertIn("Talons. Melee Attack Roll: +4", f.ficha_integral)
        self.assertIn("Resistances Necrotic, Radiant", f.ficha_integral)
        self.assertFalse(f.mecanicas_automaticamente_homologadas)

    def test_integridade_e_sem_sorteio(self):
        self.assertEqual(len(self.cartas), 80)
        self.assertEqual(self.proveniencia["copias"], {"J1": 40, "J2": 40})


if __name__ == "__main__":
    unittest.main()

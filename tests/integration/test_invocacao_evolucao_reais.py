"""Testes de invocação/evolução contra catálogo REAL pinado, sem partida oficial."""
import copy
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ("src", "experimental/legacy/src", "experimental/integration"):
    sys.path.insert(0, str(ROOT / p))
from ascend.catalogo_poc import ler_contrato
from motor_fichas_poc import SessaoFichasFixture


class MotorComFonteSRDReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raiz=os.environ["CATALOGO_SRD_DIR"]
        contrato=ler_contrato(ROOT)
        cls.sessao=SessaoFichasFixture.criar_de_checkout(
            raiz,contrato,primeiro="J2",
            maos_fixadas={
                "J2":[
                    "AB-POC-017","AB-POC-031","AB-POC-008",
                    "AB-POC-001","AB-POC-002"
                ]
            }
        )

    def test_01_fonte_e_decks(self):
        s=self.sessao
        self.assertTrue(s.proveniencia["revisao_verificada"])
        self.assertEqual(len(s.registros),80)
        self.assertTrue(all(c["pv_fonte"] is None for c in s.registros))
        self.assertEqual(s.motor.state["placar"],{"J1":0,"J2":0})

    def test_02_invocar_roper_evoluir_aboleth(self):
        s=self.sessao
        self.assertEqual(s.comando("t1","J2","TROCAR",{"descartar":[]})["decisao"],"ACEITA")
        self.assertEqual(s.comando("t2","J1","TROCAR",{"descartar":[]})["decisao"],"ACEITA")
        resp=s.comando("invocar","J2","INVOCAR",{"carta_id":"AB-POC-017"})
        self.assertEqual(resp["decisao"],"ACEITA")
        self.assertEqual(resp["resultado"]["ficha_consultada"]["ca"],20)
        self.assertEqual(resp["resultado"]["ficha_consultada"]["pv_maximos"],93)
        resp=s.comando("evoluir","J2","EVOLUIR",{"carta_id":"AB-POC-031"})
        self.assertEqual(resp["decisao"],"ACEITA")
        j=s.motor.state["jogadores"]["J2"]
        self.assertEqual(j["criatura_ativa_id"],"AB-POC-031")
        self.assertEqual(j["cartas"]["AB-POC-017"]["zona"],"CEMITERIO")
        self.assertEqual(j["cartas"]["AB-POC-031"]["pv_atual"],150)
        self.assertEqual(j["cartas"]["AB-POC-031"]["ca_fonte"],17)
        self.assertTrue(s.motor.validate())

    def test_03_checkpoint_vinculado_a_fichas(self):
        s=self.sessao
        restored=SessaoFichasFixture.restaurar(
            s.checkpoint(),os.environ["CATALOGO_SRD_DIR"],ler_contrato(ROOT))
        self.assertEqual(restored.motor.state,s.motor.state)
        self.assertEqual(restored.mesa_publica(),s.mesa_publica())
        self.assertTrue(restored.motor.validate())

    def test_04_jogador_j1_invoca_giant_owl_com_ficha_real(self):
        s=self.sessao
        self.assertEqual(s.comando("pronto","J2","PRONTO_CRIATURA",{})["decisao"],"ACEITA")
        result=s.comando("ce","J1","INVOCAR",{"carta_id":"CE-001"})
        self.assertEqual(result["decisao"],"ACEITA")
        c=s.motor.get_card(s.motor.state,"J1","CE-001")
        self.assertEqual((c["pv_atual"],c["pv_max"],c["ca_fonte"]),(19,19,12))
        self.assertFalse(c["origem_ficha"]["habilidades_homologadas"])

    def test_05_placar_nunca_modificado(self):
        self.assertEqual(self.sessao.motor.state["placar"],{"J1":0,"J2":0})
        self.assertEqual(len(self.sessao.motor.state["jogadores"]["J1"]["cartas"]),40)
        self.assertEqual(len(self.sessao.motor.state["jogadores"]["J2"]["cartas"]),40)


if __name__ == "__main__":
    unittest.main()

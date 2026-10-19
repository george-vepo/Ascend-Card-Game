"""Consulta SRD real externa: CDs e bônus extraídos, sem dados copiados."""
import os
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for p in ("src","experimental/legacy/src","experimental/integration"):
    sys.path.insert(0,str(ROOT/p))
from ascend.catalogo_poc import ler_contrato
from ascend.efeitos_srd import extrair_salvaguardas_celestial, extrair_efeitos_gibbering
from ascend.fichas_srd import consultar_ficha
from motor_combate_fichas_srd import SessaoCombateFichasFixture, ESCOPO

class TestEfeitosReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogo=os.environ["CATALOGO_SRD_DIR"]
        cls.contrato=ler_contrato(ROOT)
        cls.s=SessaoCombateFichasFixture.criar_de_checkout(
            cls.catalogo, cls.contrato,
            primeiro="J2",
            maos_fixadas={
                "J1":["CE-001","CE-002","CE-003","CE-004","CE-005"],
                "J2":["AB-POC-008","AB-POC-001","AB-POC-002","AB-POC-003","AB-POC-004"],
            },
        )
        for index,j in enumerate(("J2","J1"),1):
            cls.assertEqualStatic(cls.s.comando(f"t{index}",j,"TROCAR",{"descartar":[]})["decisao"],"ACEITA")
        cls.assertEqualStatic(cls.s.comando("i2","J2","INVOCAR",{"carta_id":"AB-POC-008"})["decisao"],"ACEITA")
        cls.assertEqualStatic(cls.s.comando("p2","J2","PRONTO_CRIATURA",{})["decisao"],"ACEITA")
        cls.assertEqualStatic(cls.s.comando("i1","J1","INVOCAR",{"carta_id":"CE-001"})["decisao"],"ACEITA")
        cls.assertEqualStatic(cls.s.comando("p1","J1","PRONTO_CRIATURA",{})["decisao"],"ACEITA")
        for j in ("J2","J1"):
            cls.assertEqualStatic(cls.s.comando("su"+j,j,"ESCOLHER_SUPORTE",{"carta_id":None})["decisao"],"ACEITA")
        for i in range(2):
            cls.assertEqualStatic(cls.s.comando("rs"+str(i),"ARBITRO","RESOLVER_SUPORTE_FIXTURE",{"resultado":"PULAR"})["decisao"],"ACEITA")
        cls.assertEqualStatic(cls.s.comando("init","ARBITRO","INICIATIVA_SRD_TESTE",{"d20":{"J1":17,"J2":8}})["decisao"],"ACEITA")

    @staticmethod
    def assertEqualStatic(actual,expected):
        if actual!=expected:raise AssertionError(f"{actual} != {expected}")

    def test_01_owl_bonus_salvaguardas(self):
        f=consultar_ficha(self.catalogo,self.contrato,self.s.referencias,"CE-001")
        self.assertEqual(extrair_salvaguardas_celestial(f),{"dex_bonus":2,"wis_bonus":4})
    def test_02_mouther_cd_e_alcance(self):
        f=consultar_ficha(self.catalogo,self.contrato,self.s.referencias,"AB-POC-008")
        self.assertEqual(extrair_efeitos_gibbering(f)["gibbering"],
                         {"dc":10,"range_ft":20,"d8_faces":8})
    def test_03_spittle_da_fonte(self):
        f=consultar_ficha(self.catalogo,self.contrato,self.s.referencias,"AB-POC-008")
        p=extrair_efeitos_gibbering(f)["spittle"]
        self.assertEqual(p["dc"],10)
        self.assertEqual(p["damage_dice"],(2,6))
        self.assertEqual((p["radius_ft"],p["range_ft"]),(10,30))
        self.assertEqual((p["recharge_min"],p["recharge_max"]),(5,6))
    def test_04_motor_consulta_parametros(self):
        r=self.s.motor._regras_efeitos(self.s.motor.state)
        self.assertEqual((r["wis_bonus"],r["dex_bonus"]),(4,2))
        self.assertEqual(r["gibbering"]["dc"],10)
    def test_05_iniciar_turno_com_fonte_e_registro(self):
        r=self.s.comando("start","J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,"gibbering_aplicavel_fixture":True,
            "wis_d20_simulado":14,
        })
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(r["resultado"]["gibbering_sab"]["cd"],10)
        self.assertEqual(r["resultado"]["gibbering_sab"]["bonus"],4)
        self.assertEqual(r["resultado"]["gibbering_sab"]["alcance_gatilho_ft"],20)
    def test_06_nao_altera_placar(self):
        self.assertEqual(self.s.motor.state["placar"],{"J1":0,"J2":0})
        self.assertEqual(len(self.s.motor.state["jogadores"]["J1"]["cartas"]),40)
        self.assertEqual(len(self.s.motor.state["jogadores"]["J2"]["cartas"]),40)

if __name__=="__main__":
    unittest.main()

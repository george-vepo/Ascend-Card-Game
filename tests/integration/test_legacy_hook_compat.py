"""Smoke de compatibilidade legado v2.4: fixtures geradas em memória."""
import os, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for name in ("src","experimental/legacy/src","experimental/integration"):
    sys.path.insert(0,str(ROOT/name))
from ascend.catalogo_poc import carregar_referencias, ler_contrato
from bridge_catalogo_motor import _registros
from motor_condicoes_srd import MotorCondicoesSRD

class CompatibilidadeLegada(unittest.TestCase):
    def setUp(self):
        refs,_=carregar_referencias(
            os.environ["CATALOGO_SRD_DIR"],ler_contrato(ROOT),
            exigir_revisao=True)
        records=_registros(refs,{"CE-001":19,"AB-POC-008":52})
        self.m=MotorCondicoesSRD(records,first="J1",hands={
            "J1":["CE-001","CE-002","CE-003","CE-004","CE-005"],
            "J2":["AB-POC-008","AB-POC-001","AB-POC-002","AB-POC-003","AB-POC-004"],
        })
        self.seq=0

    def cmd(self,j,action,params=None):
        self.seq+=1
        return self.m.apply(f"legacy-compat-{self.seq}",j,action,params or {})

    def preparar(self):
        for p in ("J1","J2"):
            self.assertEqual(self.cmd(p,"TROCAR",{"descartar":[]})["decisao"],"ACEITA")
        for p,card in (("J1","CE-001"),("J2","AB-POC-008")):
            self.assertEqual(self.cmd(p,"INVOCAR",{"carta_id":card})["decisao"],"ACEITA")
            self.assertEqual(self.cmd(p,"PRONTO_CRIATURA")["decisao"],"ACEITA")
        for p in ("J1","J2"):
            self.assertEqual(self.cmd(p,"ESCOLHER_SUPORTE",{"carta_id":None})["decisao"],"ACEITA")
        for _ in range(2):
            self.assertEqual(self.cmd("ARBITRO","RESOLVER_SUPORTE_FIXTURE",{"resultado":"PULAR"})["decisao"],"ACEITA")

    def test_01_defaults_so_para_legado(self):
        rules=self.m._regras_efeitos(self.m.state)
        self.assertEqual((rules["wis_bonus"],rules["dex_bonus"]),(4,2))
        self.assertEqual(rules["gibbering"]["dc"],10)
        self.assertEqual(rules["spittle"]["damage_dice"],(2,6))

    def test_02_iniciativa_legacy_intacta(self):
        self.preparar()
        r=self.cmd("ARBITRO","INICIATIVA_SRD_TESTE",{"d20":{"J1":17,"J2":8}})
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(self.m.state["ator_da_vez"],"J1")
        self.assertTrue(self.m.validate())

    def test_03_gibbering_legacy_ainda_falha_1_4(self):
        self.preparar()
        self.cmd("ARBITRO","INICIATIVA_SRD_TESTE",{"d20":{"J1":17,"J2":8}})
        r=self.cmd("J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":self.m.SCOPE,"gibbering_aplicavel_fixture":True,
            "wis_d20_simulado":1,"gibbering_d8_simulado":2})
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(r["resultado"]["gibbering_sab"]["cd"],10)
        self.assertTrue(r["resultado"]["bloqueado"])
        self.assertEqual(self.cmd("J1","PASSAR_TURNO_V24_TESTE")["decisao"],"ACEITA")
        self.assertEqual(self.m.state["placar"],{"J1":0,"J2":0})

if __name__=="__main__":
    unittest.main()

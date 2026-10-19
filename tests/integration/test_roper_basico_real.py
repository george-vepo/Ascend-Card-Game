"""Roper vs Giant Owl: somente fixture experimental, sem RNG."""
import copy
import os
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for p in ("src","experimental/legacy/src","experimental/integration"):
    sys.path.insert(0,str(ROOT/p))
from ascend.catalogo_poc import ler_contrato
from ascend.fichas_srd import consultar_ficha
from ascend.perfil_combate_srd import extrair_perfil_de_combate
from motor_roper_basico import SessaoRoperFixture, ESCOPO_BASICO

class RoperFixture(unittest.TestCase):
    def setUp(self):
        self.root=os.environ["CATALOGO_SRD_DIR"]
        self.contract=ler_contrato(ROOT)
        self.s=SessaoRoperFixture.criar_de_checkout(
            self.root,self.contract,primeiro="J2",
            maos_fixadas={
                "J1":["CE-001","CE-002","CE-003","CE-004","CE-005"],
                "J2":["AB-POC-017","AB-POC-001","AB-POC-002","AB-POC-003","AB-POC-004"],
            })
        self.num=0

    def send(self,actor,command,params=None):
        self.num+=1
        return self.s.comando("roper-event-"+str(self.num),actor,command,params or {})

    def ok(self,actor,command,params=None):
        r=self.send(actor,command,params)
        self.assertEqual(r["decisao"],"ACEITA",r)
        return r

    def prepare(self,initiative=None):
        for p in ("J2","J1"):self.ok(p,"TROCAR",{"descartar":[]})
        for p,c in (("J2","AB-POC-017"),("J1","CE-001")):
            self.ok(p,"INVOCAR",{"carta_id":c})
            self.ok(p,"PRONTO_CRIATURA")
        for p in ("J2","J1"):self.ok(p,"ESCOLHER_SUPORTE",{"carta_id":None})
        for _ in range(2):
            self.ok("ARBITRO","RESOLVER_SUPORTE_FIXTURE",{"resultado":"PULAR"})
        self.ok("ARBITRO","INICIATIVA_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "d20_simulados":initiative or {"J1":10,"J2":12},
        })

    def attack(self,actor="J2",d20=12,dice=None,range_ok=True,name=None,scope=True):
        if dice is None:
            dice=[1,2,3] if actor=="J2" else [3]
        return self.send(actor,"ATAQUE_ROPER_BASICO_TESTE",{
            "aceite_escopo":ESCOPO_BASICO if scope else "OUTRO",
            "alvo_no_alcance_fixture":range_ok,
            "ataque":name or ("Bite" if actor=="J2" else "Talons"),
            "d20_simulado":d20,"dano_dados":dice,
        })

    def card(self,j,c):
        return self.s.motor.get_card(self.s.motor.state,j,c)

    def test_01_catalogo_real_identidades(self):
        self.assertEqual(len(self.s.registros),80)
        self.assertTrue(self.s.proveniencia["revisao_verificada"])
        self.assertEqual(self.s.proveniencia["copias"],{"J1":40,"J2":40})

    def test_02_roper_perfil_fonte(self):
        f=consultar_ficha(self.root,self.contract,self.s.referencias,"AB-POC-017")
        p=extrair_perfil_de_combate(f)
        self.assertEqual((p["ac"],p["hp"],p["initiative"]),(20,93,5))
        self.assertEqual((p["attack"]["name"],p["attack"]["bonus"]),("Bite",7))
        self.assertEqual((p["attack"]["dice"],p["attack"]["flat"]),((3,8),4))
        self.assertEqual((p["attack"]["reach_ft"],p["attack"]["type"]),(5,"Piercing"))
        self.assertFalse(p["mechanics_fully_supported"])

    def test_03_preparacao_fichas(self):
        self.prepare()
        self.assertEqual(self.card("J2","AB-POC-017")["pv_atual"],93)
        self.assertEqual(self.card("J1","CE-001")["pv_atual"],19)
        self.assertEqual(self.s.motor.state["fase"],"COMBATE")

    def test_04_iniciativa_real(self):
        self.prepare()
        self.assertEqual(self.s.motor.state["combate"]["iniciativas"]["J2"],17)
        self.assertEqual(self.s.motor.state["combate"]["iniciativas"]["J1"],12)
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_05_roper_bite_dano_simulado(self):
        self.prepare()
        r=self.attack()
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual((r["resultado"]["dano_aplicado"],
                          self.card("J1","CE-001")["pv_atual"]),(10,9))
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J1")

    def test_06_owl_erra_ca_20(self):
        self.prepare();self.attack()
        r=self.attack("J1",10,[])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["acertou"])
        self.assertEqual(self.card("J2","AB-POC-017")["pv_atual"],93)

    def test_07_owl_acerta_ca_20(self):
        self.prepare();self.attack()
        r=self.attack("J1",16,[8])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(r["resultado"]["dano_aplicado"],10)
        self.assertEqual(self.card("J2","AB-POC-017")["pv_atual"],83)
        self.assertEqual(self.s.motor.state["combate"]["rodada"],2)

    def test_08_natural_um_erra(self):
        self.prepare()
        r=self.attack("J2",1,[])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["acertou"])

    def test_09_critico_dobra_dados_nao_bonus(self):
        self.prepare()
        r=self.attack("J2",20,[1,1,2,2,3,3])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["critico"])
        self.assertEqual(r["resultado"]["dano_aplicado"],16)
        self.assertEqual(self.card("J1","CE-001")["pv_atual"],3)
        self.assertFalse(r["resultado"]["ko"])

    def test_10_ko_somente_na_fixture(self):
        self.prepare()
        r=self.attack("J2",20,[3,3,3,3,3,3])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["ko"])
        self.assertEqual(self.s.motor.state["placar"],{"J1":0,"J2":1})
        self.assertEqual(self.card("J1","CE-001")["zona"],"CEMITERIO")
        self.assertEqual(self.card("J2","AB-POC-017")["pv_atual"],93)

    def test_11_d8_invalido_rejeita_e_preserva(self):
        self.prepare();before=copy.deepcopy(self.s.motor.state)
        r=self.attack("J2",12,[9,1,1])
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,before)

    def test_12_dados_incompletos_rejeita(self):
        self.prepare()
        self.assertEqual(self.attack("J2",12,[1,1])["decisao"],"REJEITADA")

    def test_13_d20_booleano_rejeita(self):
        self.prepare()
        self.assertEqual(self.attack("J2",True,[1,1,1])["decisao"],"REJEITADA")

    def test_14_alcance_nao_informado_nao_bloqueia(self):
        self.prepare()
        r=self.attack(range_ok=None)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["acertou"])

    def test_15_indicacao_fora_de_alcance_e_ignorada(self):
        self.prepare()
        r=self.attack(range_ok=False)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["acertou"])

    def test_16_tentacle_nao_e_bite(self):
        self.prepare()
        self.assertEqual(self.attack(name="Tentacle")["decisao"],"REJEITADA")

    def test_17_multiattack_pendente(self):
        self.prepare();before=copy.deepcopy(self.s.motor.state)
        self.assertEqual(self.send("J2","MULTIATTACK_ROPER_TESTE")["decisao"],"PENDENTE")
        self.assertEqual(self.s.motor.state,before)

    def test_18_reel_pendente(self):
        self.prepare()
        self.assertEqual(self.send("J2","REEL_ROPER_TESTE")["decisao"],"PENDENTE")

    def test_19_spider_climb_pendente(self):
        self.prepare()
        self.assertEqual(self.send("J2","SPIDER_CLIMB_ROPER_TESTE")["decisao"],"PENDENTE")

    def test_20_fora_da_vez_rejeita(self):
        self.prepare()
        self.assertEqual(self.attack("J1",12,[3])["decisao"],"REJEITADA")

    def test_21_escopo_nao_confirmado_pendente(self):
        self.prepare()
        self.assertEqual(self.attack(scope=False)["decisao"],"PENDENTE")

    def test_22_checkpoint_restaura_combate(self):
        self.prepare();self.attack()
        restored=SessaoRoperFixture.restaurar(
            self.s.checkpoint(),self.root,self.contract)
        self.assertEqual(restored.motor.state,self.s.motor.state)
        self.assertEqual(restored.mesa_publica(),self.s.mesa_publica())

    def test_23_publico_nao_expoe_maos(self):
        self.prepare()
        import json
        rendered=json.dumps(self.s.mesa_publica(),ensure_ascii=False)
        self.assertIn("Roper",rendered)
        self.assertIn("Giant Owl",rendered)
        self.assertNotIn("CE-002",rendered)
        self.assertNotIn("AB-POC-001",rendered)

    def test_24_40_copias_preservadas(self):
        self.prepare();self.attack()
        self.assertTrue(self.s.motor.validate())
        for p in ("J1","J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][p]["cartas"]),40)

    def test_25_idempotencia(self):
        self.prepare()
        params={"aceite_escopo":ESCOPO_BASICO,"alvo_no_alcance_fixture":True,
                "ataque":"Bite","d20_simulado":12,"dano_dados":[1,1,1]}
        first=self.s.comando("ataque-unico","J2","ATAQUE_ROPER_BASICO_TESTE",params)
        again=self.s.comando("ataque-unico","J2","ATAQUE_ROPER_BASICO_TESTE",params)
        self.assertEqual(first,again)
        self.assertEqual(self.card("J1","CE-001")["pv_atual"],12)

    def test_26_nao_homologa_multiattack(self):
        self.prepare()
        omitted=self.s.motor.state["combate"]["mecanicas_nao_implementadas"]["J2"]
        self.assertTrue(any("Multiattack" in x for x in omitted))

if __name__=="__main__":
    unittest.main()

"""Testes SRD limitados: duas fichas reais do checkout EXTERNO pinado.

Sem resultados oficiais; dados de ataque e atributos jamais são sorteados aqui.
"""
import copy
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
for p in ("src","experimental/legacy/src","experimental/integration"):
    sys.path.insert(0,str(ROOT/p))
from ascend.catalogo_poc import ler_contrato
from motor_combate_fichas_srd import SessaoCombateFichasFixture, ESCOPO
from motor_poc import CorruptedCheckpoint


class CombateSRDComFontes(unittest.TestCase):
    def setUp(self):
        self.root=os.environ["CATALOGO_SRD_DIR"]
        self.contract=ler_contrato(ROOT)
        self.s=SessaoCombateFichasFixture.criar_de_checkout(
            self.root,self.contract,primeiro="J2",
            maos_fixadas={"J1":["CE-001","CE-002","CE-003","CE-004","CE-005"],
                         "J2":["AB-POC-008","AB-POC-001","AB-POC-002",
                               "AB-POC-003","AB-POC-004"]},
        )
    def go(self,who,cmd,p=None,id=None):
        seq=len(self.s.motor.events)+len(self.s.motor.rejections)+1
        return self.s.comando(id or f"ev-{seq}",who,cmd,p or {})

    def preparar(self):
        for p in ("J2","J1"):
            self.assertEqual(self.go(p,"TROCAR",{"descartar":[]})["decisao"],"ACEITA")
        self.assertEqual(self.go("J2","INVOCAR",{"carta_id":"AB-POC-008"})["decisao"],"ACEITA")
        self.assertEqual(self.go("J2","PRONTO_CRIATURA")["decisao"],"ACEITA")
        self.assertEqual(self.go("J1","INVOCAR",{"carta_id":"CE-001"})["decisao"],"ACEITA")
        self.assertEqual(self.go("J1","PRONTO_CRIATURA")["decisao"],"ACEITA")
        for p in ("J2","J1"):
            self.assertEqual(self.go(p,"ESCOLHER_SUPORTE",{"carta_id":None})["decisao"],"ACEITA")
        for _ in range(2):
            self.assertEqual(self.go("ARBITRO","RESOLVER_SUPORTE_FIXTURE",{"resultado":"PULAR"})["decisao"],"ACEITA")
        self.assertEqual(self.s.motor.state["fase"],"INICIATIVA")

    def iniciativa(self):
        self.preparar()
        r=self.go("ARBITRO","INICIATIVA_SRD_TESTE",{"d20":{"J1":17,"J2":8}})
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J1")

    def inicio_owl(self,near=False,roll=None,d8=None):
        p={"aceite_escopo":ESCOPO,"gibbering_aplicavel_fixture":near}
        if roll is not None:p["wis_d20_simulado"]=roll
        if d8 is not None:p["gibbering_d8_simulado"]=d8
        return self.go("J1","INICIO_TURNO_V24_TESTE",p)

    def talons(self,reach=True,rolls=None,damage=None):
        p={"aceite_escopo":ESCOPO,"ataque":"Talons",
           "d20_simulados":[12] if rolls is None else rolls,
           "dano_dados":[5] if damage is None else damage}
        if reach is not None:p["alvo_no_alcance_fixture"]=reach
        return self.go("J1","ATAQUE_V24_TESTE",p)

    def inicio_mouth(self,recharge=None):
        p={}
        if recharge is not None:p["recarga_d6_simulado"]=recharge
        return self.go("J2","INICIO_TURNO_V24_TESTE",p)

    def spittle(self):
        return self.go("J2","BLINDING_SPITTLE_V24_TESTE",
            {"aceite_escopo":ESCOPO,"alvo_na_area_fixture":True,
             "dex_d20_simulado":1,"dano_d6_simulados":[6,2]})

    def test_01_preparacao_trata_80_copias(self):
        self.preparar()
        state=self.s.motor.state
        self.assertTrue(self.s.motor.validate())
        self.assertEqual(len(state["jogadores"]["J1"]["cartas"]),40)
        self.assertEqual(len(state["jogadores"]["J2"]["cartas"]),40)
        self.assertEqual(state["jogadores"]["J1"]["cartas"]["CE-001"]["pv_max"],19)
        self.assertEqual(state["jogadores"]["J2"]["cartas"]["AB-POC-008"]["pv_max"],52)

    def test_02_iniciativa_usa_fichas_confirmadas(self):
        self.iniciativa()
        combat=self.s.motor.state["combate"]
        self.assertEqual(combat["iniciativas"]["J1"],19)
        self.assertEqual(combat["iniciativas"]["J2"],7)
        self.assertEqual(combat["iniciativas"]["origem"],"DADOS_SIMULADOS_TESTE")

    def test_03_ataque_owl_com_dado_simulado(self):
        self.iniciativa()
        self.assertEqual(self.inicio_owl()["decisao"],"ACEITA")
        r=self.talons()
        self.assertEqual(r["decisao"],"ACEITA")
        self.assertEqual(r["resultado"]["dano_aplicado"],7)
        self.assertEqual(self.s.motor.state["jogadores"]["J2"]["cartas"]["AB-POC-008"]["pv_atual"],45)

    def test_04_gibbering_bloqueia_acao(self):
        self.iniciativa()
        r=self.inicio_owl(near=True,roll=1,d8=3)
        self.assertEqual(r["decisao"],"ACEITA")
        bad=self.talons()
        self.assertEqual(bad["decisao"],"REJEITADA")
        self.assertEqual(self.go("J1","PASSAR_TURNO_V24_TESTE")["decisao"],"ACEITA")
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_05_gibbering_resultado_7_8_pendente(self):
        self.iniciativa()
        before=copy.deepcopy(self.s.motor.state)
        r=self.inicio_owl(near=True,roll=1,d8=7)
        self.assertEqual(r["decisao"],"PENDENTE")
        self.assertEqual(self.s.motor.state,before)

    def test_06_alcance_obrigatorio(self):
        self.iniciativa()
        self.inicio_owl()
        before=copy.deepcopy(self.s.motor.state)
        r=self.talons(reach=None)
        self.assertEqual(r["decisao"],"PENDENTE")
        self.assertEqual(self.s.motor.state,before)

    def test_07_alvo_fora_alcance_rejeita(self):
        self.iniciativa();self.inicio_owl()
        before=copy.deepcopy(self.s.motor.state)
        r=self.talons(reach=False)
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,before)

    def test_08_dados_obrigatorios(self):
        self.iniciativa();self.inicio_owl()
        r=self.talons(rolls=[0])
        self.assertEqual(r["decisao"],"REJEITADA")

    def test_09_blinding_spittle_resistencia_e_cegueira(self):
        self.iniciativa();self.inicio_owl();self.talons()
        self.assertEqual(self.inicio_mouth()["decisao"],"ACEITA")
        r=self.spittle()
        self.assertEqual(r["decisao"],"ACEITA")
        self.assertEqual(r["resultado"]["dano_bruto"],8)
        self.assertEqual(r["resultado"]["dano_aplicado"],4)
        c=self.s.motor.get_card(self.s.motor.state,"J1","CE-001")
        self.assertEqual(c["pv_atual"],15)
        self.assertIn("Blinded",c["condicoes"])

    def test_10_desvantagem_e_expiracao(self):
        self.iniciativa();self.inicio_owl();self.talons()
        self.inicio_mouth();self.spittle()
        self.assertEqual(self.inicio_owl()["decisao"],"ACEITA")
        r=self.talons(rolls=[14,5],damage=[3])
        self.assertEqual(r["decisao"],"ACEITA")
        self.assertEqual(r["resultado"]["modo_rolagem"],"DESVANTAGEM")
        self.assertEqual(self.s.motor.get_card(self.s.motor.state,"J2","AB-POC-008")["pv_atual"],40)
        self.assertEqual(self.inicio_mouth(recharge=1)["decisao"],"ACEITA")
        result=self.go("J2","ATAQUE_V24_TESTE",
            {"aceite_escopo":ESCOPO,"ataque":"Bite",
             "alvo_no_alcance_fixture":True,"d20_simulados":[6,18],
             "dano_dados":[4,3]})
        self.assertEqual(result["decisao"],"ACEITA")
        self.assertEqual(result["resultado"]["modo_rolagem"],"VANTAGEM")
        self.assertFalse(result["resultado"]["prone_aplicado"])
        owl=self.s.motor.get_card(self.s.motor.state,"J1","CE-001")
        self.assertEqual(owl["pv_atual"],8)
        self.assertNotIn("Blinded",owl["condicoes"])
        self.assertEqual(self.s.motor.state["placar"],{"J1":0,"J2":0})

    def test_11_checkpoint_sem_info_publica(self):
        self.iniciativa()
        pub=str(self.s.mesa_publica())
        self.assertNotIn("CE-002",pub)
        self.assertNotIn("AB-POC-001",pub)
        self.assertNotIn("monte_ordem_ids",pub)
        self.assertTrue(self.s.checkpoint()["unicamente_teste"])

    def test_12_checkpoint_restaura_durante_combate(self):
        self.iniciativa();self.inicio_owl();self.talons()
        result=SessaoCombateFichasFixture.restaurar(
            self.s.checkpoint(),self.root,self.contract)
        self.assertEqual(result.motor.state,self.s.motor.state)
        self.assertEqual(result.mesa_publica(),self.s.mesa_publica())
        self.assertTrue(result.motor.validate())

    def test_13_checkpoint_tamper_bloqueado(self):
        self.iniciativa()
        cp=self.s.checkpoint()
        cp["motor"]["state"]["jogadores"]["J1"]["cartas"]["CE-001"]["pv_atual"]=2
        with self.assertRaises(CorruptedCheckpoint):
            SessaoCombateFichasFixture.restaurar(cp,self.root,self.contract)

    def test_14_suportes_nao_inventados(self):
        self.iniciativa()
        v=self.s.motor.state
        self.assertEqual(v["jogadores"]["J1"]["suporte_reservado_id"],None)
        self.assertEqual(v["jogadores"]["J2"]["suporte_reservado_id"],None)

    def test_15_dados_nunca_sao_rolados_pelo_motor(self):
        self.iniciativa();self.inicio_owl()
        self.assertEqual(self.talons(rolls=[12],damage=[5])["resultado"]["dados_simulados"],True)


if __name__=="__main__":
    unittest.main()

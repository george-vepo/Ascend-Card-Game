"""Reel preflight: somente consulta, sem inventar arena nem mover criaturas."""
import copy
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
for p in ("src","experimental/legacy/src","experimental/integration"):
    sys.path.insert(0,str(ROOT/p))
from ascend.catalogo_poc import ler_contrato
from motor_roper_basico import SessaoRoperFixture, ESCOPO_BASICO

class ReelPreflight(unittest.TestCase):
    def setUp(self):
        self.root=os.environ["CATALOGO_SRD_DIR"]
        self.s=SessaoRoperFixture.criar_de_checkout(
            self.root,ler_contrato(ROOT),primeiro="J2",
            maos_fixadas={
                "J1":["CE-001","CE-002","CE-003","CE-004","CE-005"],
                "J2":["AB-POC-017","AB-POC-001","AB-POC-002","AB-POC-003","AB-POC-004"]})
        self.n=0
        for p in ("J2","J1"):self.ok(p,"TROCAR",{"descartar":[]})
        for p,c in (("J2","AB-POC-017"),("J1","CE-001")):
            self.ok(p,"INVOCAR",{"carta_id":c})
            self.ok(p,"PRONTO_CRIATURA")
        for p in ("J2","J1"):self.ok(p,"ESCOLHER_SUPORTE",{"carta_id":None})
        for _ in range(2):
            self.ok("ARBITRO","RESOLVER_SUPORTE_FIXTURE",{"resultado":"PULAR"})
        self.ok("ARBITRO","INICIATIVA_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,"d20_simulados":{"J1":10,"J2":12}})

    def cmd(self,p,action,args=None):
        self.n+=1
        return self.s.comando("reel-preflight-"+str(self.n),p,action,args or {})

    def ok(self,p,action,args=None):
        r=self.cmd(p,action,args)
        self.assertEqual(r["decisao"],"ACEITA",r)
        return r

    def _agarrar_e_retornar_turno(self):
        self.ok("J2","TENTACLE_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "alvo_no_alcance_fixture":True,
            "tentaculo_numero":2,"d20_simulado":10})
        # A coruja usa sua ação para tentar escapar e falha; o Roper volta.
        res=self.cmd("J1","ESCAPAR_GRAPPLE_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,"pericia":"Athletics",
            "d20_simulados":[1,2]})
        self.assertEqual(res["decisao"],"ACEITA",res)
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_01_sem_grapple_nao_ha_alvo(self):
        x=self.s.motor.prevalidar_reel()
        self.assertEqual(x["estado"],"SEM_ALVO_AGARRADO")
        self.assertEqual(x["distancia_maxima_ft"],30)
        self.assertFalse(x["executavel"])

    def test_02_grapple_confirmado_mas_arena_pendente(self):
        self._agarrar_e_retornar_turno()
        x=self.s.motor.prevalidar_reel()
        self.assertEqual(x["estado"],"PENDENTE_ARENA")
        self.assertEqual(x["alvos"][0]["carta_id"],"CE-001")
        self.assertEqual(x["alvos"][0]["tentaculo_numero"],2)
        self.assertIn("direcao_reta_para_roper",x["dados_necessarios"])
        self.assertFalse(x["consome_acao"])

    def test_03_prevalidacao_pura(self):
        self._agarrar_e_retornar_turno()
        before=copy.deepcopy(self.s.motor.state)
        events=len(self.s.motor.events)
        chain=self.s.motor.head_hash
        for _ in range(5):self.s.motor.prevalidar_reel()
        self.assertEqual(self.s.motor.state,before)
        self.assertEqual(len(self.s.motor.events),events)
        self.assertEqual(self.s.motor.head_hash,chain)

    def test_04_declaracao_reel_pendente_sem_mutacao(self):
        self._agarrar_e_retornar_turno()
        before=copy.deepcopy(self.s.motor.state)
        r=self.cmd("J2","REEL_ROPER_TESTE")
        self.assertEqual(r["decisao"],"PENDENTE",r)
        self.assertEqual(self.s.motor.state,before)
        self.assertEqual(self.s.motor.state["placar"],{"J1":0,"J2":0})

    def test_05_prevalidacao_fora_turno_inaplicavel(self):
        self.ok("J2","TENTACLE_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,"alvo_no_alcance_fixture":True,
            "tentaculo_numero":1,"d20_simulado":10})
        self.assertEqual(self.s.motor.prevalidar_reel()["estado"],"INAPLICAVEL")

    def test_06_privacidade_e_conservacao(self):
        self._agarrar_e_retornar_turno()
        import json
        out=json.dumps(self.s.mesa_publica(),ensure_ascii=False)
        self.assertNotIn("CE-002",out)
        self.assertNotIn("AB-POC-001",out)
        self.assertTrue(self.s.motor.validate())
        for p in ("J1","J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][p]["cartas"]),40)

if __name__=="__main__":
    unittest.main()

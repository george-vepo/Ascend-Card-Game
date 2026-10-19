"""Poisoned impõe desvantagem ao escapar de Grappled: consulta duas fichas reais."""
import copy
import os
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for p in ("src","experimental/legacy/src","experimental/integration"):
    sys.path.insert(0,str(ROOT/p))
from ascend.catalogo_poc import ler_contrato
from motor_roper_basico import ESCOPO_BASICO, SessaoRoperFixture

class FugaSobPoisoned(unittest.TestCase):
    def setUp(self):
        self.catalogo=os.environ["CATALOGO_SRD_DIR"]
        self.contrato=ler_contrato(ROOT)
        self.s=SessaoRoperFixture.criar_de_checkout(
            self.catalogo,self.contrato,primeiro="J2",
            maos_fixadas={
                "J1":["CE-001","CE-002","CE-003","CE-004","CE-005"],
                "J2":["AB-POC-017","AB-POC-001","AB-POC-002","AB-POC-003","AB-POC-004"],
            },
        )
        self.n=0
        for p in ("J2","J1"):self.ok(p,"TROCAR",{"descartar":[]})
        for p,c in (("J2","AB-POC-017"),("J1","CE-001")):
            self.ok(p,"INVOCAR",{"carta_id":c})
            self.ok(p,"PRONTO_CRIATURA")
        for p in ("J2","J1"):self.ok(p,"ESCOLHER_SUPORTE",{"carta_id":None})
        for _ in range(2):
            self.ok("ARBITRO","RESOLVER_SUPORTE_FIXTURE",{"resultado":"PULAR"})
        self.ok("ARBITRO","INICIATIVA_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "d20_simulados":{"J1":10,"J2":12},
        })
        self.ok("J2","TENTACLE_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "alvo_no_alcance_fixture":True,
            "tentaculo_numero":3,"d20_simulado":10,
        })
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J1")

    def send(self,p,a,args=None):
        self.n+=1
        return self.s.comando(f"poison-escape-{self.n}",p,a,args or {})

    def ok(self,p,a,args=None):
        r=self.send(p,a,args)
        self.assertEqual(r["decisao"],"ACEITA",r)
        return r

    def fuga(self,pericia="Athletics",rolls=None,extra=None):
        params={"aceite_escopo":ESCOPO_BASICO,"pericia":pericia}
        if rolls is not None:params["d20_simulados"]=rolls
        if extra:params.update(extra)
        return self.send("J1","ESCAPAR_GRAPPLE_ROPER_TESTE",params)

    def owl(self):
        return self.s.motor.get_card(self.s.motor.state,"J1","CE-001")

    def test_01_condicoes_iniciais_da_ficha(self):
        self.assertEqual(self.owl()["condicoes"],["Grappled","Poisoned"])
        self.assertEqual(self.owl()["efeitos"][0]["escape_dc"],14)

    def test_02_alto_e_baixo_d20_fuga_fracassa(self):
        r=self.ok("J1","ESCAPAR_GRAPPLE_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,"pericia":"Athletics",
            "d20_simulados":[20,12],
        })
        info=r["resultado"]
        self.assertFalse(info["sucesso"])
        self.assertEqual(info["d20_aplicado"],12)
        self.assertEqual(info["modo_rolagem"],"DESVANTAGEM")
        self.assertEqual(info["total"],13)
        self.assertIn("Poisoned",self.owl()["condicoes"])
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_03_dois_d20_suficientes_pode_escapar(self):
        r=self.fuga(rolls=[20,13])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["sucesso"])
        self.assertEqual((r["resultado"]["total"],r["resultado"]["cd"]),(14,14))
        self.assertEqual(self.owl()["condicoes"],[])
        self.assertEqual(self.owl()["efeitos"],[])
        self.assertFalse(self.s.motor.state["combate"].get("tentaculos_roper"))
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_04_acrobatics_com_desvantagem(self):
        r=self.fuga(pericia="Acrobatics",rolls=[12,20])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["sucesso"])
        self.assertEqual(r["resultado"]["modificador"],2)
        self.assertEqual(r["resultado"]["total"],14)

    def test_05_dados_ausentes_pendente_sem_mutacao(self):
        before=copy.deepcopy(self.s.motor.state)
        n=len(self.s.motor.events)
        r=self.fuga()
        self.assertEqual(r["decisao"],"PENDENTE",r)
        self.assertEqual(self.s.motor.state,before)
        self.assertEqual(len(self.s.motor.events),n)

    def test_06_dado_unico_novo_pendente(self):
        before=copy.deepcopy(self.s.motor.state)
        r=self.fuga(rolls=[20])
        self.assertEqual(r["decisao"],"PENDENTE",r)
        self.assertEqual(self.s.motor.state,before)

    def test_07_formato_antigo_d20_unico_nao_contorna_desvantagem(self):
        before=copy.deepcopy(self.s.motor.state)
        r=self.fuga(extra={"d20_simulado":20})
        self.assertEqual(r["decisao"],"PENDENTE",r)
        self.assertEqual(self.s.motor.state,before)

    def test_08_valor_maior_que_20_rejeitado(self):
        before=copy.deepcopy(self.s.motor.state)
        r=self.fuga(rolls=[21,17])
        self.assertEqual(r["decisao"],"REJEITADA",r)
        self.assertEqual(self.s.motor.state,before)

    def test_09_bool_nao_e_d20(self):
        self.assertEqual(self.fuga(rolls=[True,20])["decisao"],"REJEITADA")

    def test_10_fuga_fracassada_persiste_em_checkpoint(self):
        self.fuga(rolls=[17,8])
        cp=self.s.checkpoint()
        restored=SessaoRoperFixture.restaurar(
            cp,self.catalogo,self.contrato
        )
        self.assertEqual(restored.motor.state,self.s.motor.state)
        self.assertEqual(restored.motor.state["jogadores"]["J1"]
                         ["cartas"]["CE-001"]["condicoes"],["Grappled","Poisoned"])

    def test_11_fuga_bem_sucedida_preserva_40_cartas(self):
        self.fuga(rolls=[20,20])
        self.assertTrue(self.s.motor.validate())
        for player in ("J1","J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"]
                                 [player]["cartas"]),40)
        self.assertEqual(self.s.motor.state["placar"],{"J1":0,"J2":0})

    def test_12_nao_exibe_mao_oponente_ao_fugir(self):
        self.fuga(rolls=[20,12])
        import json
        body=json.dumps(self.s.mesa_publica(),ensure_ascii=False)
        self.assertNotIn("AB-POC-001",body)
        self.assertNotIn("CE-002",body)

    def test_13_nao_tenta_outra_acao_no_mesmo_turno(self):
        self.fuga(rolls=[20,13])
        r=self.send("J1","ATAQUE_ROPER_BASICO_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "alvo_no_alcance_fixture":True,
            "ataque":"Talons","d20_simulado":20,"dano_dados":[10,10],
        })
        self.assertEqual(r["decisao"],"REJEITADA")

if __name__=="__main__":
    unittest.main()

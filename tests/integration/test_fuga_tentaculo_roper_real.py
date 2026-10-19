"""Roper Grapple: fuga, ataque a tentáculo e regeneração, SRD real pinado.

Os testes são fixtures: dados explícitos, sem partida/placar oficial.
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
from ascend.fichas_srd import consultar_ficha
from ascend.fuga_roper_srd import extrair_testes_fuga_owl
from motor_roper_basico import SessaoRoperFixture, ESCOPO_BASICO


class FugaRoperSRD(unittest.TestCase):
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

    def act(self,actor,cmd,p=None):
        self.n+=1
        return self.s.comando(f"escape-{self.n}",actor,cmd,p or {})

    def ok(self,actor,cmd,p=None):
        r=self.act(actor,cmd,p)
        self.assertEqual(r["decisao"],"ACEITA",r)
        return r

    def tentacle(self,slot=1):
        return self.ok("J2","TENTACLE_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "alvo_no_alcance_fixture":True,
            "tentaculo_numero":slot,
            "d20_simulado":10,
        })

    def escape(self,skill="Athletics",roll=13,actor="J1"):
        return self.act(actor,"ESCAPAR_GRAPPLE_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "pericia":skill,"d20_simulados":[roll,roll],
        })

    def hit_tentacle(self,slot=1,rolls=None,dice=None,reach=True):
        return self.act("J1","ATACAR_TENTACULO_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,"tentaculo_numero":slot,
            "alvo_no_alcance_fixture":reach,"ataque":"Talons",
            "d20_simulados":[16,16] if rolls is None else rolls,
            "dano_dados":[8] if dice is None else dice,
        })

    def card(self,p,card):
        return self.s.motor.get_card(self.s.motor.state,p,card)

    def slots(self):
        return self.s.motor.state["combate"].get("tentaculos_roper",{})

    def test_01_extrair_bonus_atletismo_acrobacia_srd_real(self):
        f=consultar_ficha(self.catalogo,self.contrato,self.s.referencias,"CE-001")
        self.assertEqual(extrair_testes_fuga_owl(f),
                         {"Athletics":1,"Acrobatics":2})

    def test_02_tentaculo_tem_dez_pv_proprios(self):
        self.tentacle(slot=4)
        self.assertEqual(self.slots()["4"]["pv_atual"],10)
        self.assertEqual(self.slots()["4"]["pv_max"],10)
        self.assertEqual(self.card("J2","AB-POC-017")["pv_atual"],93)

    def test_03_fuga_atletismo_sucesso_exato_dc(self):
        self.tentacle()
        r=self.escape("Athletics",13)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual((r["resultado"]["total"],r["resultado"]["cd"]),(14,14))
        self.assertTrue(r["resultado"]["sucesso"])
        self.assertEqual(self.card("J1","CE-001")["condicoes"],[])
        self.assertEqual(self.card("J1","CE-001")["efeitos"],[])
        self.assertEqual(self.slots(),{})
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_04_fuga_acrobacia_sucesso_exato_dc(self):
        self.tentacle()
        r=self.escape("Acrobatics",12)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(r["resultado"]["modificador"],2)
        self.assertTrue(r["resultado"]["sucesso"])

    def test_05_fuga_fracassada_mantem_grapple_e_poisoned(self):
        self.tentacle(slot=2)
        r=self.escape("Athletics",12)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["sucesso"])
        self.assertEqual(self.card("J1","CE-001")["condicoes"],["Grappled","Poisoned"])
        self.assertIn("2",self.slots())
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_06_nao_pode_escolher_outra_pericia(self):
        self.tentacle()
        old=copy.deepcopy(self.s.motor.state)
        r=self.escape("Perception",20)
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,old)

    def test_07_dado_escape_invalido_rejeita(self):
        self.tentacle()
        self.assertEqual(self.escape("Athletics",0)["decisao"],"REJEITADA")

    def test_08_dado_booleano_nao_e_d20(self):
        self.tentacle()
        self.assertEqual(self.escape("Athletics",True)["decisao"],"REJEITADA")

    def test_09_nao_pode_escapar_fora_turno(self):
        # Roper começa o confronto; Owl não age antes dele.
        self.assertEqual(self.escape()["decisao"],"REJEITADA")

    def test_10_roper_nao_pode_usar_escape_da_owl(self):
        self.tentacle()
        self.assertEqual(self.escape(actor="J2")["decisao"],"REJEITADA")

    def test_11_escape_pendente_sem_escopo(self):
        self.tentacle()
        r=self.act("J1","ESCAPAR_GRAPPLE_ROPER_TESTE",{
            "pericia":"Athletics","d20_simulado":13,
        })
        self.assertEqual(r["decisao"],"PENDENTE")

    def test_12_desvantagem_poisoned_ao_atacar_tentaculo(self):
        self.tentacle()
        r=self.hit_tentacle(rolls=[20,8],dice=[])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["acertou"])
        self.assertEqual(r["resultado"]["modo_rolagem"],"DESVANTAGEM")
        self.assertEqual(self.slots()["1"]["pv_atual"],10)

    def test_13_dano_parcial_preserva_tentaculo(self):
        self.tentacle(slot=3)
        r=self.hit_tentacle(slot=3,dice=[5])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["destruido"])
        self.assertEqual(self.slots()["3"]["pv_atual"],3)
        self.assertEqual(self.card("J1","CE-001")["condicoes"],["Grappled","Poisoned"])
        self.assertEqual(self.card("J2","AB-POC-017")["pv_atual"],93)

    def test_14_destruicao_libera_e_nao_machuca_roper(self):
        self.tentacle(slot=4)
        r=self.hit_tentacle(slot=4,dice=[8])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["destruido"])
        self.assertEqual(r["resultado"]["pv_tentaculo_depois"],0)
        self.assertEqual(r["resultado"]["dano_aplicado"],10)
        self.assertEqual(self.card("J1","CE-001")["condicoes"],[])
        self.assertEqual(self.card("J1","CE-001")["efeitos"],[])
        self.assertEqual(self.slots(),{})
        self.assertEqual(self.card("J2","AB-POC-017")["pv_atual"],93)

    def test_15_tentaculo_regenera_no_inicio_proximo_turno_roper(self):
        self.tentacle(slot=5)
        r=self.hit_tentacle(slot=5,dice=[8])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(r["resultado"]["tentaculos_regenerados"],[5])
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")
        self.assertEqual(self.s.motor.state["combate"].get("tentaculos_destruidos"),None)
        # O Roper voltou a poder usar a mesma parte em turno posterior.
        next_hit=self.ok("J2","TENTACLE_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,"alvo_no_alcance_fixture":True,
            "tentaculo_numero":5,"d20_simulado":10,
        })
        self.assertTrue(next_hit["resultado"]["acertou"])
        self.assertIn("5",self.slots())

    def test_16_tentaculo_acerta_com_critico_talons(self):
        self.tentacle()
        r=self.hit_tentacle(rolls=[20,20],dice=[6,6])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["critico"])
        self.assertEqual(r["resultado"]["dano_aplicado"],14)
        self.assertTrue(r["resultado"]["destruido"])

    def test_17_rolagem_ausente_nao_muda_estado(self):
        self.tentacle()
        before=copy.deepcopy(self.s.motor.state)
        r=self.hit_tentacle(rolls=[16],dice=[8])
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,before)

    def test_18_fora_de_alcance_nao_bloqueia_ataque(self):
        self.tentacle()
        r=self.hit_tentacle(reach=False)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["acertou"])

    def test_19_alcance_ausente_nao_bloqueia_ataque(self):
        self.tentacle()
        r=self.hit_tentacle(reach=None)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["acertou"])

    def test_20_nao_ataca_tentaculo_sem_grapple(self):
        self.tentacle()
        self.escape()
        # Roper está na vez; Owl não pode atacar em turno errado.
        r=self.hit_tentacle()
        self.assertEqual(r["decisao"],"REJEITADA")

    def test_21_nao_dupla_acao_escape_e_ataque(self):
        self.tentacle()
        self.escape()
        self.assertEqual(self.hit_tentacle()["decisao"],"REJEITADA")

    def test_22_checkpoint_de_tentaculo_com_pv_parciais(self):
        self.tentacle(slot=2)
        self.hit_tentacle(slot=2,dice=[4])
        restored=SessaoRoperFixture.restaurar(
            self.s.checkpoint(),self.catalogo,self.contrato
        )
        self.assertEqual(restored.motor.state,self.s.motor.state)
        self.assertEqual(restored.mesa_publica(),self.s.mesa_publica())

    def test_23_80_copias_preservadas(self):
        self.tentacle()
        self.escape()
        self.assertTrue(self.s.motor.validate())
        for j in ("J1","J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][j]["cartas"]),40)

    def test_24_dados_invisiveis_na_visao_publica(self):
        self.tentacle()
        import json
        view=json.dumps(self.s.mesa_publica(),ensure_ascii=False)
        self.assertNotIn("CE-002",view)
        self.assertNotIn("AB-POC-001",view)
        self.assertIn("Poisoned",view)

    def test_25_reel_permitido_sem_arena(self):
        self.tentacle()
        self.escape(roll=1)
        prior=copy.deepcopy(self.s.motor.state)
        r=self.act("J2","REEL_ROPER_TESTE")
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["deslocamento_aplicado"])
        self.assertEqual(self.s.motor.state["jogadores"],prior["jogadores"])

if __name__=="__main__":
    unittest.main()

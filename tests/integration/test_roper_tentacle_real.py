"""Roper Tentacle: ficha REAL externa, dados simulados, estado isolado."""
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
from ascend.tentaculo_roper_srd import extrair_tentaculo_roper
from motor_roper_basico import SessaoRoperFixture, ESCOPO_BASICO


class RoperTentacleFixture(unittest.TestCase):
    def setUp(self):
        self.catalogo=os.environ["CATALOGO_SRD_DIR"]
        self.contrato=ler_contrato(ROOT)
        self.s=SessaoRoperFixture.criar_de_checkout(
            self.catalogo,self.contrato,primeiro="J2",
            maos_fixadas={
                "J1":["CE-001","CE-002","CE-003","CE-004","CE-005"],
                "J2":["AB-POC-017","AB-POC-001","AB-POC-002","AB-POC-003","AB-POC-004"],
            })
        self.seq=0
        for player in ("J2","J1"):self.ok(player,"TROCAR",{"descartar":[]})
        for player,card in (("J2","AB-POC-017"),("J1","CE-001")):
            self.ok(player,"INVOCAR",{"carta_id":card})
            self.ok(player,"PRONTO_CRIATURA")
        for player in ("J2","J1"):
            self.ok(player,"ESCOLHER_SUPORTE",{"carta_id":None})
        for _ in range(2):
            self.ok("ARBITRO","RESOLVER_SUPORTE_FIXTURE",{"resultado":"PULAR"})
        self.ok("ARBITRO","INICIATIVA_ROPER_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "d20_simulados":{"J1":10,"J2":12},
        })

    def run_cmd(self,actor,command,params=None):
        self.seq+=1
        return self.s.comando("tentacle-"+str(self.seq),actor,command,params or {})

    def ok(self,actor,command,params=None):
        res=self.run_cmd(actor,command,params)
        self.assertEqual(res["decisao"],"ACEITA",res)
        return res

    def tentacle(self,roll=10,reach=True,slot=1,actor="J2",scope=ESCOPO_BASICO):
        return self.run_cmd(actor,"TENTACLE_ROPER_TESTE",{
            "aceite_escopo":scope,"alvo_no_alcance_fixture":reach,
            "tentaculo_numero":slot,"d20_simulado":roll,
        })

    def owl(self):
        return self.s.motor.get_card(self.s.motor.state,"J1","CE-001")

    def owl_attack(self,rolls=None,damage=None):
        params={
            "aceite_escopo":ESCOPO_BASICO,
            "alvo_no_alcance_fixture":True,
            "ataque":"Talons",
            "dano_dados":[5] if damage is None else damage,
        }
        if rolls is None: params["d20_simulado"]=18
        else:params["d20_simulados"]=rolls
        return self.run_cmd("J1","ATAQUE_ROPER_BASICO_TESTE",params)

    def test_01_ficha_tentacle_integral(self):
        f=consultar_ficha(self.catalogo,self.contrato,self.s.referencias,"AB-POC-017")
        p=extrair_tentaculo_roper(f)
        self.assertEqual((p["bonus_ataque"],p["alcance_ft"],p["escape_dc"]),(7,60,14))
        self.assertEqual(p["quantidade_tentaculos"],6)
        self.assertEqual(p["condicoes_no_acerto"],["Grappled","Poisoned"])
        self.assertEqual((p["tentaculo"]["ca"],p["tentaculo"]["pv"]),(20,10))
        self.assertEqual(p["tentaculo"]["imunidades_dano"],["Poison","Psychic"])
        self.assertEqual(p["reel"]["distancia_maxima_ft"],30)
        self.assertFalse(p["reel"]["movimento_homologado"])

    def test_02_tentacle_acerto_sem_dano(self):
        r=self.tentacle()
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["acertou"])
        self.assertEqual(r["resultado"]["dano_aplicado"],0)
        self.assertEqual(self.owl()["pv_atual"],19)
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J1")

    def test_03_gagarra_condicoes_e_efeito_de_origem(self):
        self.tentacle()
        c=self.owl()
        self.assertEqual(c["condicoes"],["Grappled","Poisoned"])
        self.assertEqual(len(c["efeitos"]),1)
        e=c["efeitos"][0]
        self.assertEqual((e["fonte"],e["tentaculo"],e["escape_dc"]),
                         ("AB-POC-017",1,14))
        self.assertEqual(e["condicoes"],["Grappled","Poisoned"])

    def test_04_slot_publico_e_privacidade(self):
        self.tentacle(slot=3)
        import json
        public=json.dumps(self.s.mesa_publica(),ensure_ascii=False)
        self.assertIn('"3"',public)
        self.assertIn('"Grappled"',public)
        self.assertIn('"Poisoned"',public)
        self.assertNotIn("CE-002",public)
        self.assertNotIn("AB-POC-001",public)
        self.assertEqual(self.owl()["efeitos"][0]["tentaculo"],3)

    def test_05_erro_natural_um_nao_agarrar(self):
        r=self.tentacle(roll=1)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["acertou"])
        self.assertEqual(self.owl()["condicoes"],[])
        self.assertNotIn("tentaculos_roper",self.s.motor.state["combate"])

    def test_06_critico_tentacle_sem_dano(self):
        r=self.tentacle(roll=20)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["critico"])
        self.assertEqual(r["resultado"]["dano_aplicado"],0)
        self.assertEqual(self.owl()["pv_atual"],19)

    def test_07_perde_roll_abaixo_ca(self):
        r=self.tentacle(roll=2)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["acertou"])

    def test_08_acerta_com_total_exato_ca(self):
        r=self.tentacle(roll=5)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["acertou"])
        self.assertEqual(r["resultado"]["total_ataque"],12)

    def test_09_alcance_ausente_nao_bloqueia(self):
        r=self.tentacle(reach=None)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertIn("Grappled",self.owl()["condicoes"])

    def test_10_alcance_falso_e_ignorado(self):
        r=self.tentacle(reach=False)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertIn("Poisoned",self.owl()["condicoes"])

    def test_11_slot_zero_rejeita(self):
        self.assertEqual(self.tentacle(slot=0)["decisao"],"REJEITADA")

    def test_12_slot_sete_rejeita(self):
        self.assertEqual(self.tentacle(slot=7)["decisao"],"REJEITADA")

    def test_13_slot_booleano_rejeita(self):
        self.assertEqual(self.tentacle(slot=True)["decisao"],"REJEITADA")

    def test_14_d20_zero_rejeita(self):
        self.assertEqual(self.tentacle(roll=0)["decisao"],"REJEITADA")

    def test_15_outro_jogador_nao_usa_tentacle(self):
        self.assertEqual(self.tentacle(actor="J1")["decisao"],"REJEITADA")

    def test_16_escopo_obrigatorio(self):
        self.assertEqual(self.tentacle(scope="OUTRO")["decisao"],"PENDENTE")

    def test_17_poisoned_impede_ataque_sem_desvantagem(self):
        self.tentacle()
        old=copy.deepcopy(self.s.motor.state)
        r=self.owl_attack()
        self.assertEqual(r["decisao"],"PENDENTE",r)
        self.assertEqual(self.s.motor.state,old)

    def test_18_poisoned_usa_menor_d20(self):
        self.tentacle()
        r=self.owl_attack([19,4],damage=[])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(r["resultado"]["modo_rolagem"],"DESVANTAGEM")
        self.assertEqual(r["resultado"]["d20_simulado"],4)
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_19_poisoned_pode_acertar_em_desvantagem(self):
        self.tentacle()
        r=self.owl_attack([17,16],[8])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(r["resultado"]["dano_aplicado"],10)
        self.assertEqual(self.s.motor.get_card(self.s.motor.state,"J2","AB-POC-017")["pv_atual"],83)

    def test_20_owl_ainda_agarrada_apos_ataque(self):
        self.tentacle()
        self.owl_attack([17,16],[1])
        self.assertEqual(self.owl()["condicoes"],["Grappled","Poisoned"])
        self.assertEqual(len(self.owl()["efeitos"]),1)

    def test_21_roper_bite_com_grapple_ativo(self):
        self.tentacle()
        self.owl_attack([19,4],[])
        r=self.ok("J2","ATAQUE_ROPER_BASICO_TESTE",{
            "aceite_escopo":ESCOPO_BASICO,
            "alvo_no_alcance_fixture":True,
            "ataque":"Bite","d20_simulado":12,"dano_dados":[1,2,3],
        })
        self.assertEqual(r["resultado"]["dano_aplicado"],10)
        self.assertEqual(self.owl()["pv_atual"],9)

    def test_22_reel_ignora_posicionamento_e_consume_action(self):
        self.tentacle();self.owl_attack([19,4],[])
        old=copy.deepcopy(self.s.motor.state)
        r=self.run_cmd("J2","REEL_ROPER_TESTE",{})
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["deslocamento_aplicado"])
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J1")
        self.assertEqual(self.s.motor.state["jogadores"],old["jogadores"])

    def test_23_multiattack_permanece_pendente(self):
        old=copy.deepcopy(self.s.motor.state)
        r=self.run_cmd("J2","MULTIATTACK_ROPER_TESTE",{})
        self.assertEqual(r["decisao"],"PENDENTE")
        self.assertEqual(self.s.motor.state,old)

    def test_24_checkpoint_agarrado_restauravel(self):
        self.tentacle()
        restored=SessaoRoperFixture.restaurar(
            self.s.checkpoint(),self.catalogo,self.contrato
        )
        self.assertEqual(restored.motor.state,self.s.motor.state)
        self.assertEqual(restored.mesa_publica(),self.s.mesa_publica())

    def test_25_conservacao_40_cartas(self):
        self.tentacle()
        self.assertTrue(self.s.motor.validate())
        for player in ("J1","J2"):
            self.assertEqual(len(self.s.motor.state["jogadores"][player]["cartas"]),40)

    def test_26_placar_nunca_alterado_por_grapple(self):
        self.tentacle()
        self.assertEqual(self.s.motor.state["placar"],{"J1":0,"J2":0})

    def test_27_novo_tentaculo_mesmo_alvo_pendente(self):
        self.tentacle();self.owl_attack([19,4],[])
        old=copy.deepcopy(self.s.motor.state)
        r=self.tentacle(slot=2)
        self.assertEqual(r["decisao"],"PENDENTE",r)
        self.assertEqual(self.s.motor.state,old)

    def test_28_nao_permita_slot_ocupado(self):
        self.tentacle();self.owl_attack([19,4],[])
        r=self.tentacle(slot=1)
        self.assertEqual(r["decisao"],"REJEITADA")

    def test_29_roper_ao_critico_sem_dano_em_tentacle(self):
        self.tentacle(roll=20)
        self.assertEqual(self.owl()["pv_atual"],19)
        self.assertEqual(self.s.motor.state["combate"]["rodada"],1)

    def test_30_segundo_tentacle_so_depois_turno_owl(self):
        self.tentacle()
        before=copy.deepcopy(self.s.motor.state)
        r=self.tentacle(slot=2)
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,before)

if __name__=="__main__":
    unittest.main()

"""Gibbering d8 7–8: resultado forçado, dados simulados e fonte real pinada.

Nenhuma partida oficial, mão secreta ou checkpoint é publicado.
"""
import copy
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
for name in ("src","experimental/legacy/src","experimental/integration"):
    sys.path.insert(0,str(ROOT/name))

from ascend.catalogo_poc import ler_contrato
from motor_combate_fichas_srd import SessaoCombateFichasFixture, ESCOPO

class TestGibbering78(unittest.TestCase):
    def setUp(self):
        self.s=SessaoCombateFichasFixture.criar_de_checkout(
            os.environ["CATALOGO_SRD_DIR"], ler_contrato(ROOT),
            primeiro="J2",
            maos_fixadas={
                "J1":["CE-001","CE-002","CE-003","CE-004","CE-005"],
                "J2":["AB-POC-008","AB-POC-001","AB-POC-002",
                      "AB-POC-003","AB-POC-004"],
            },
        )
        self._seq=0
        for j in ("J2","J1"):
            self.ok(j,"TROCAR",{"descartar":[]})
        self.ok("J2","INVOCAR",{"carta_id":"AB-POC-008"})
        self.ok("J2","PRONTO_CRIATURA")
        self.ok("J1","INVOCAR",{"carta_id":"CE-001"})
        self.ok("J1","PRONTO_CRIATURA")
        for j in ("J2","J1"):
            self.ok(j,"ESCOLHER_SUPORTE",{"carta_id":None})
        for _ in range(2):
            self.ok("ARBITRO","RESOLVER_SUPORTE_FIXTURE",{"resultado":"PULAR"})
        self.ok("ARBITRO","INICIATIVA_SRD_TESTE",{"d20":{"J1":17,"J2":8}})

    def cmd(self, actor, action, params=None, ident=None):
        self._seq += 1
        return self.s.comando(
            ident or f"gibbering78-{self._seq}",actor,action,params or {}
        )

    def ok(self, actor, action, params=None, ident=None):
        r=self.cmd(actor,action,params,ident)
        self.assertEqual(r["decisao"],"ACEITA",r)
        return r

    def start(self,d8=7,within=True,wis=1,extra=None):
        params={
            "aceite_escopo":ESCOPO,
            "gibbering_aplicavel_fixture":True,
            "wis_d20_simulado":wis,
            "gibbering_d8_simulado":d8,
        }
        if within is not None:
            params["mouther_ao_alcance_fixture"]=within
        if extra:params.update(extra)
        return self.cmd("J1","INICIO_TURNO_V24_TESTE",params)

    def forced(self,rolls=None,damage=None,**kwargs):
        p={
            "aceite_escopo":ESCOPO,
            "alvo_id":"AB-POC-008",
            "ataque":"Talons",
            "d20_simulados":[12] if rolls is None else rolls,
            "dano_dados":[5] if damage is None else damage,
        }
        p.update(kwargs)
        return self.cmd("J1","RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE",p)

    def hp(self,who,cid):
        return self.s.motor.get_card(
            self.s.motor.state,who,cid
        )["pv_atual"]

    def test_01_d7_gera_ataque_obrigatorio_sem_dano_antecipado(self):
        start=self.start()
        self.assertEqual(start["decisao"],"ACEITA")
        self.assertEqual(start["resultado"]["acao_exigida"],
                         "RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE")
        self.assertEqual(self.hp("J2","AB-POC-008"),52)
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J1")

    def test_02_d8_tambem_aceito(self):
        r=self.start(d8=8)
        self.assertEqual(r["decisao"],"ACEITA")
        self.assertEqual(r["resultado"]["gibbering_resultado_d8"],8)

    def test_03_alcance_desconhecido_deixa_estado_intacto(self):
        old=copy.deepcopy(self.s.motor.state)
        r=self.start(within=None)
        self.assertEqual(r["decisao"],"PENDENTE")
        self.assertEqual(self.s.motor.state,old)

    def test_04_sem_alvo_turno_passa_sem_rolar_ataque(self):
        start=self.start(within=False)
        self.assertEqual(start["decisao"],"ACEITA")
        self.assertEqual(start["resultado"]["acao_exigida"],"PASSAR_TURNO_V24_TESTE")
        finish=self.ok("J1","PASSAR_TURNO_V24_TESTE")
        self.assertEqual(finish["resultado"]["passou_por"],
                         "Gibbering 7–8 sem alvo ao alcance")
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")
        self.assertEqual(self.hp("J2","AB-POC-008"),52)

    def test_05_forca_talons_e_avanca_turno(self):
        self.ok("J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,"gibbering_aplicavel_fixture":True,
            "wis_d20_simulado":1,"gibbering_d8_simulado":7,
            "mouther_ao_alcance_fixture":True
        })
        result=self.forced()
        self.assertEqual(result["decisao"],"ACEITA",result)
        self.assertEqual(result["resultado"]["dano_aplicado"],7)
        self.assertEqual(result["resultado"]["seleção_alvo"],"UNICO_ELEGIVEL")
        self.assertFalse(result["resultado"]["ko"])
        self.assertEqual(self.hp("J2","AB-POC-008"),45)
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_06_d20_1_erra_mesmo_com_bonus(self):
        self.start()
        r=self.forced(rolls=[1],damage=[])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertFalse(r["resultado"]["acertou"])
        self.assertEqual(self.hp("J2","AB-POC-008"),52)

    def test_07_d20_20_dobra_dado_mas_nao_bonus(self):
        self.start()
        r=self.forced(rolls=[20],damage=[10,8])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertTrue(r["resultado"]["critico"])
        self.assertEqual(r["resultado"]["dano_aplicado"],20)
        self.assertEqual(self.hp("J2","AB-POC-008"),32)

    def test_08_ataque_voluntario_bloqueado_durante_forcado(self):
        self.start()
        old=copy.deepcopy(self.s.motor.state)
        r=self.cmd("J1","ATAQUE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"ataque":"Talons",
            "alvo_no_alcance_fixture":True,
            "d20_simulados":[10],"dano_dados":[4],
        })
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,old)

    def test_09_nao_pode_pular_alvo_elegivel(self):
        self.start()
        r=self.cmd("J1","PASSAR_TURNO_V24_TESTE")
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J1")

    def test_10_ataque_forcado_sem_gatilho_rejeitado(self):
        r=self.forced()
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.hp("J2","AB-POC-008"),52)

    def test_11_nao_escolher_alvo_arbitrario(self):
        self.start()
        r=self.forced(alvo_id="CE-001")
        self.assertEqual(r["decisao"],"REJEITADA")

    def test_12_nao_escolher_ataque_que_nao_existe(self):
        self.start()
        r=self.forced(ataque="Bite")
        self.assertEqual(r["decisao"],"REJEITADA")

    def test_13_dado_dano_invalido_preserva_estado(self):
        self.start()
        before=copy.deepcopy(self.s.motor.state)
        r=self.forced(rolls=[12],damage=[11])
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,before)

    def test_14_dado_d20_faltando_preserva_estado(self):
        self.start()
        before=copy.deepcopy(self.s.motor.state)
        r=self.forced(rolls=[],damage=[2])
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,before)

    def test_15_d8_sem_falha_em_sab_rejeita(self):
        before=copy.deepcopy(self.s.motor.state)
        r=self.start(d8=7,wis=14)
        self.assertEqual(r["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,before)

    def test_16_checkpoint_preserva_ataque_forcado(self):
        self.start()
        cp=self.s.checkpoint()  # somente privado, memória; não exportar
        rebuilt=SessaoCombateFichasFixture.restaurar(
            cp,os.environ["CATALOGO_SRD_DIR"],ler_contrato(ROOT))
        self.assertEqual(rebuilt.motor.state,self.s.motor.state)
        self.assertEqual(rebuilt.motor.public(),self.s.motor.public())
        reply=rebuilt.comando(
            "replay-forced","J1","RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE",{
                "aceite_escopo":ESCOPO,"alvo_id":"AB-POC-008",
                "ataque":"Talons","d20_simulados":[11],"dano_dados":[3]
            }
        )
        self.assertEqual(reply["decisao"],"ACEITA",reply)
        self.assertEqual(rebuilt.motor.state["jogadores"]["J2"]["cartas"]["AB-POC-008"]["pv_atual"],47)

    def test_17_somente_cenario_sintetico_sem_sorteio_ou_placar(self):
        self.start()
        r=self.forced()
        self.assertEqual(r["resultado"]["origem_dados"],"DADOS_SIMULADOS_TESTE")
        self.assertEqual(self.s.motor.state["placar"],{"J1":0,"J2":0})
        self.assertTrue(self.s.motor.validate())
        self.assertEqual(len(self.s.motor.state["jogadores"]["J1"]["cartas"]),40)
        self.assertEqual(len(self.s.motor.state["jogadores"]["J2"]["cartas"]),40)

    def test_18_publico_mostra_pendencia_sem_revelar_maos(self):
        self.start()
        public=self.s.mesa_publica()
        import json
        encoded=json.dumps(public,ensure_ascii=False)
        self.assertNotIn("CE-002",encoded)
        self.assertNotIn("AB-POC-001",encoded)
        self.assertIn("ATAQUE_TALONS_PENDENTE",encoded)

    def test_19_nao_forcar_turno_uma_segunda_vez(self):
        self.start()
        r=self.start(d8=8)
        self.assertEqual(r["decisao"],"REJEITADA")

    def test_20_apos_forcado_acao_extra_invalida(self):
        self.start()
        self.forced()
        r=self.forced()
        self.assertEqual(r["decisao"],"REJEITADA")

    def test_21_blinded_provoca_desvantagem(self):
        # O cegamento vem de Spittle, lançado após um turno normal da coruja.
        self.ok("J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,"gibbering_aplicavel_fixture":False
        })
        self.ok("J1","ATAQUE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"ataque":"Talons",
            "alvo_no_alcance_fixture":True,
            "d20_simulados":[12],"dano_dados":[3],
        })
        self.ok("J2","INICIO_TURNO_V24_TESTE",{"aceite_escopo":ESCOPO})
        self.ok("J2","BLINDING_SPITTLE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"alvo_na_area_fixture":True,
            "dex_d20_simulado":1,"dano_d6_simulados":[6,2],
        })
        self.start(d8=7)
        r=self.forced(rolls=[15,10],damage=[2])
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(r["resultado"]["modo_rolagem"],"DESVANTAGEM")
        self.assertEqual(r["resultado"]["d20_aplicado"],10)
        self.assertEqual(self.hp("J2","AB-POC-008"),43)
        self.assertEqual(self.hp("J1","CE-001"),15)

    def test_22_gibbering_d5_pendente_ate_decisao_movimento(self):
        anterior=copy.deepcopy(self.s.motor.state)
        hash_anterior=self.s.motor.head_hash
        eventos=len(self.s.motor.events)
        r=self.start(d8=5)
        self.assertEqual(r["decisao"],"PENDENTE",r)
        self.assertEqual(self.s.motor.state,anterior)
        self.assertEqual(self.s.motor.head_hash,hash_anterior)
        self.assertEqual(len(self.s.motor.events),eventos)
        self.assertIn("deslocamento aleatório",str(r))

    def test_23_gibbering_d6_nao_pode_virar_turno_perdido(self):
        anterior=copy.deepcopy(self.s.motor.state)
        r=self.start(d8=6)
        self.assertEqual(r["decisao"],"PENDENTE",r)
        self.assertEqual(self.s.motor.state,anterior)
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J1")
        self.assertEqual(self.cmd("J1","PASSAR_TURNO_V24_TESTE")["decisao"],"REJEITADA")

    def test_24_sucesso_sab_nao_admite_d8_sobrando(self):
        anterior=copy.deepcopy(self.s.motor.state)
        r=self.start(d8=5,wis=15)
        self.assertEqual(r["decisao"],"REJEITADA",r)
        self.assertEqual(self.s.motor.state,anterior)

    def test_25_sucesso_sab_sem_d8_permanece_aceito(self):
        r=self.ok("J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,
            "gibbering_aplicavel_fixture":True,
            "wis_d20_simulado":15,
        })
        self.assertTrue(r["resultado"]["gibbering_sab"]["sucesso"])
        self.assertEqual(
            self.s.motor.acoes_disponiveis_teste()["acoes"],
            ["ATAQUE_V24_TESTE"],
        )

    def test_26_resultados_1_4_ainda_permitem_passar_sem_acao(self):
        r=self.start(d8=3)
        self.assertEqual(r["decisao"],"ACEITA",r)
        self.assertEqual(self.s.motor.acoes_disponiveis_teste()["acoes"],
                         ["PASSAR_TURNO_V24_TESTE"])
        self.ok("J1","PASSAR_TURNO_V24_TESTE")
        self.assertEqual(self.s.motor.state["ator_da_vez"],"J2")

    def test_27_consulta_publica_so_permite_inicio_inicialmente(self):
        self.assertEqual(self.s.motor.acoes_disponiveis_teste()["acoes"],
                         ["INICIO_TURNO_V24_TESTE"])
        pub=self.s.mesa_publica()
        self.assertEqual(pub["proximas_acoes_fixture"]["ator"],"J1")
        self.assertEqual(pub["proximas_acoes_fixture"]["acoes"],
                         ["INICIO_TURNO_V24_TESTE"])

    def test_28_ataque_voluntario_so_apos_inicio_livre(self):
        self.ok("J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,"gibbering_aplicavel_fixture":False
        })
        self.assertEqual(self.s.motor.acoes_disponiveis_teste()["acoes"],
                         ["ATAQUE_V24_TESTE"])

    def test_29_acao_forcada_e_a_unica_disponivel(self):
        self.start(d8=7)
        self.assertEqual(self.s.motor.acoes_disponiveis_teste()["acoes"],
                         ["RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE"])
        self.assertEqual(self.s.mesa_publica()["proximas_acoes_fixture"]["acoes"],
                         ["RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE"])

    def test_30_sem_alvo_somente_passar_turno(self):
        self.start(d8=8,within=False)
        self.assertEqual(self.s.motor.acoes_disponiveis_teste()["acoes"],
                         ["PASSAR_TURNO_V24_TESTE"])

    def _preparar_turno_do_mouther(self):
        self.ok("J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,
            "gibbering_aplicavel_fixture":False,
        })
        self.ok("J1","ATAQUE_V24_TESTE",{
            "aceite_escopo":ESCOPO, "ataque":"Talons",
            "alvo_no_alcance_fixture":True,
            "d20_simulados":[12], "dano_dados":[1],
        })
        self.ok("J2","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,
        })

    def _passar_turno_owl_com_ataque(self):
        self.ok("J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,
            "gibbering_aplicavel_fixture":False,
        })
        self.ok("J1","ATAQUE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"ataque":"Talons",
            "alvo_no_alcance_fixture":True,
            "d20_simulados":[12],"dano_dados":[1],
        })

    def test_31_spittle_esta_disponivel_no_primeiro_turno(self):
        self._preparar_turno_do_mouther()
        self.assertEqual(self.s.motor.acoes_disponiveis_teste()["acoes"],
                         ["ATAQUE_V24_TESTE","BLINDING_SPITTLE_V24_TESTE"])

    def test_32_spittle_indisponivel_apos_uso_e_recarga_falha(self):
        self._preparar_turno_do_mouther()
        self.ok("J2","BLINDING_SPITTLE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"alvo_na_area_fixture":False,
        })
        self._passar_turno_owl_com_ataque()
        r=self.ok("J2","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,
            "recarga_d6_simulado":1,
        })
        self.assertFalse(r["resultado"]["recarga_spittle"]["recarregou"])
        self.assertEqual(self.s.motor.acoes_disponiveis_teste()["acoes"],
                         ["ATAQUE_V24_TESTE"])
        anterior=copy.deepcopy(self.s.motor.state)
        x=self.cmd("J2","BLINDING_SPITTLE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"alvo_na_area_fixture":False,
        })
        self.assertEqual(x["decisao"],"REJEITADA")
        self.assertEqual(self.s.motor.state,anterior)

    def test_33_spittle_retorna_apos_recarga_seis(self):
        self._preparar_turno_do_mouther()
        self.ok("J2","BLINDING_SPITTLE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"alvo_na_area_fixture":False,
        })
        self._passar_turno_owl_com_ataque()
        r=self.ok("J2","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,"recarga_d6_simulado":6,
        })
        self.assertTrue(r["resultado"]["recarga_spittle"]["recarregou"])
        self.assertIn("BLINDING_SPITTLE_V24_TESTE",
                      self.s.motor.acoes_disponiveis_teste()["acoes"])
        self.ok("J2","BLINDING_SPITTLE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"alvo_na_area_fixture":False,
        })
        self.assertFalse(self.s.motor.state["combate"]["v24"]["spittle_disponivel"])

    def test_34_consulta_acoes_nao_muda_estado_nem_eventos(self):
        estado=copy.deepcopy(self.s.motor.state)
        eventos=len(self.s.motor.events)
        h=self.s.motor.head_hash
        for _ in range(5):
            self.s.motor.acoes_disponiveis_teste()
            self.s.mesa_publica()
        self.assertEqual(self.s.motor.state,estado)
        self.assertEqual(len(self.s.motor.events),eventos)
        self.assertEqual(self.s.motor.head_hash,h)

    def test_35_acao_publica_nao_expoe_cartas_na_mao(self):
        import json
        self.start(d8=7)
        rendered=json.dumps(self.s.mesa_publica(),ensure_ascii=False)
        self.assertNotIn("CE-002",rendered)
        self.assertNotIn("AB-POC-002",rendered)
        self.assertIn("RESOLVER_ATAQUE_FORCADO_GIBBERING_TESTE",rendered)

    def test_36_fora_da_vez_nao_gera_pendencia_movimento(self):
        self.start(d8=7)
        before=copy.deepcopy(self.s.motor.state)
        r=self.start(d8=5)
        self.assertEqual(r["decisao"],"REJEITADA",r)
        self.assertEqual(self.s.motor.state,before)

    def test_37_blinded_so_expira_ao_fim_proximo_turno_mouther(self):
        self._preparar_turno_do_mouther()
        spit=self.ok("J2","BLINDING_SPITTLE_V24_TESTE",{
            "aceite_escopo":ESCOPO,
            "alvo_na_area_fixture":True,
            "dex_d20_simulado":1,
            "dano_d6_simulados":[2,2],
        })
        self.assertEqual(spit["resultado"]["blinded_ate_fim_turno_mouther"],2)
        owl=self.s.motor.get_card(self.s.motor.state,"J1","CE-001")
        self.assertIn("Blinded",owl["condicoes"])
        self.assertEqual(len(owl["efeitos"]),1)
        self.assertEqual(owl["efeitos"][0]["expira_ao_fim_turno_fonte"],2)
        self.ok("J1","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,"gibbering_aplicavel_fixture":False,
        })
        self.assertIn("Blinded",owl["condicoes"])
        attack=self.ok("J1","ATAQUE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"ataque":"Talons",
            "alvo_no_alcance_fixture":True,
            "d20_simulados":[12,12],"dano_dados":[1],
        })
        self.assertEqual(attack["resultado"]["modo_rolagem"],"DESVANTAGEM")
        self.assertIn("Blinded",owl["condicoes"])
        self.ok("J2","INICIO_TURNO_V24_TESTE",{
            "aceite_escopo":ESCOPO,"recarga_d6_simulado":1,
        })
        self.assertIn("Blinded",owl["condicoes"])
        bite=self.ok("J2","ATAQUE_V24_TESTE",{
            "aceite_escopo":ESCOPO,"ataque":"Bite",
            "alvo_no_alcance_fixture":True,
            "d20_simulados":[12,12],"dano_dados":[1,1],
        })
        self.assertEqual(bite["resultado"]["modo_rolagem"],"VANTAGEM")
        self.assertEqual(bite["resultado"]["efeitos_expirados"],["Blinded"])
        self.assertNotIn("Blinded",owl["condicoes"])
        self.assertFalse(owl["efeitos"])
        self.assertEqual(self.s.motor.state["placar"],{"J1":0,"J2":0})

if __name__=="__main__":
    unittest.main()

"""Fixture-only isolated tests of SRD v2.4 effects; never official game dice."""
import copy,json,pathlib,unittest
from motor_condicoes_srd import MotorCondicoesSRD
from motor_base_v22 import CorruptedCheckpoint

ROOT=pathlib.Path(__file__).resolve().parent
RECS=json.loads((ROOT/'STATUS_FICHAS_SUPORTES_80.json').read_text(encoding='utf-8'))['registros']
HANDS={'J1':['CE-001','CE-017','CE-019','CE-029','CE-035'],
'J2':['AB-POC-008','AB-POC-001','AB-POC-017','AB-POC-021','AB-POC-033']}
SCOPE=MotorCondicoesSRD.SCOPE

class TestEffects(unittest.TestCase):
    def setUp(self):
        self.g=MotorCondicoesSRD(RECS,hands=HANDS)
        self.n=0
    def act(self,who,cmd,**kw):
        self.n+=1
        return self.g.apply('v24test-%03d'%self.n,who,cmd,kw)
    def yes(self,who,cmd,**kw):
        r=self.act(who,cmd,**kw);self.assertEqual(r['decisao'],'ACEITA',r);return r['resultado']
    def no(self,who,cmd,**kw):
        before=copy.deepcopy(self.g.state)
        r=self.act(who,cmd,**kw)
        self.assertIn(r['decisao'],('REJEITADA','PENDENTE'),r)
        self.assertEqual(before,self.g.state)
        return r
    def prep(self,j2first=False):
        for p in ('J1','J2'):self.yes(p,'TROCAR',descartar=[])
        self.yes('J1','INVOCAR',carta_id='CE-001');self.yes('J1','PRONTO_CRIATURA')
        self.yes('J2','INVOCAR',carta_id='AB-POC-008');self.yes('J2','PRONTO_CRIATURA')
        for p in ('J1','J2'):self.yes(p,'ESCOLHER_SUPORTE',carta_id=None)
        for p in ('J1','J2'):self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
        return self.yes('ARBITRO','INICIATIVA_SRD_TESTE',d20={'J1':2,'J2':20} if j2first else {'J1':15,'J2':10})
    def start_owl(self,near=False,wis=None,d8=None):
        x={'aceite_escopo':SCOPE,'gibbering_aplicavel_fixture':near}
        if wis is not None:x['wis_d20_simulado']=wis
        if d8 is not None:x['gibbering_d8_simulado']=d8
        return self.yes('J1','INICIO_TURNO_V24_TESTE',**x)
    def start_mouther(self,recharge=None):
        x={'aceite_escopo':SCOPE}
        if recharge is not None:x['recarga_d6_simulado']=recharge
        return self.yes('J2','INICIO_TURNO_V24_TESTE',**x)
    def owl_attack(self,rolls=(12,),dice=(5,)):
        return self.yes('J1','ATAQUE_V24_TESTE',aceite_escopo=SCOPE,ataque='Talons',d20_simulados=list(rolls),dano_dados=list(dice))
    def mouther_attack(self,rolls=(15,),dice=(2,3)):
        return self.yes('J2','ATAQUE_V24_TESTE',aceite_escopo=SCOPE,ataque='Bite',d20_simulados=list(rolls),dano_dados=list(dice))
    def spit(self,roll=3,dice=(5,4),area=True):
        x={'aceite_escopo':SCOPE,'alvo_na_area_fixture':area}
        if area:
            x['dex_d20_simulado']=roll
            if roll+2<10:x['dano_d6_simulados']=list(dice)
        return self.yes('J2','BLINDING_SPITTLE_V24_TESTE',**x)
    def owl(self):return self.g.state['jogadores']['J1']['cartas']['CE-001']
    def m(self):return self.g.state['jogadores']['J2']['cartas']['AB-POC-008']

    def test_01_initiative_requires_begin_turn(self):
        self.prep();self.no('J1','ATAQUE_V24_TESTE',aceite_escopo=SCOPE,ataque='Talons',d20_simulados=[10],dano_dados=[4])
    def test_02_legacy_attack_blocked(self):
        self.prep();self.no('J1','ATAQUE_SRD_TESTE',aceite_escopo='ATAQUE_ISOLADO_SEM_PASSIVOS',ataque='Talons',d20=10,dano_dados=[4])
    def test_03_legacy_fixture_ko_blocked(self):
        self.prep();self.no('ARBITRO','KO_COMBATE_FIXTURE',vencedor='J1',comprovante_fixture=True)
    def test_04_owl_start_requires_range_predicate(self):
        self.prep();self.no('J1','INICIO_TURNO_V24_TESTE',aceite_escopo=SCOPE)
    def test_05_owl_start_without_gibbering(self):
        self.prep();o=self.start_owl();self.assertFalse(o['bloqueado'])
    def test_06_owl_not_given_fake_wis_dice_when_outside(self):
        self.prep();self.no('J1','INICIO_TURNO_V24_TESTE',aceite_escopo=SCOPE,gibbering_aplicavel_fixture=False,wis_d20_simulado=8)
    def test_07_wis_success(self):
        self.prep();o=self.start_owl(True,6);self.assertEqual(o['gibbering_sab']['total'],10);self.assertFalse(o['bloqueado'])
    def test_08_wis_save_modifier(self):
        self.prep();o=self.start_owl(True,14);self.assertEqual(o['gibbering_sab']['bonus'],4)
    def test_09_wis_missing_d20_rejected(self):
        self.prep();self.no('J1','INICIO_TURNO_V24_TESTE',aceite_escopo=SCOPE,gibbering_aplicavel_fixture=True)
    def test_10_wis_fail_requires_d8(self):
        self.prep();self.no('J1','INICIO_TURNO_V24_TESTE',aceite_escopo=SCOPE,gibbering_aplicavel_fixture=True,wis_d20_simulado=1)
    def test_11_wis_fail_d8_1_4_forces_pass(self):
        self.prep();o=self.start_owl(True,2,4);self.assertTrue(o['bloqueado'])
        self.no('J1','ATAQUE_V24_TESTE',aceite_escopo=SCOPE,ataque='Talons',d20_simulados=[12],dano_dados=[5])
        out=self.yes('J1','PASSAR_TURNO_V24_TESTE');self.assertEqual(out['proximo_ator'],'J2')
    def test_12_wis_fail_d8_5_6_forces_pass(self):
        self.prep();o=self.start_owl(True,1,6);self.assertTrue(o['bloqueado']);self.yes('J1','PASSAR_TURNO_V24_TESTE')
    def test_13_wis_fail_d8_7_8_pending(self):
        self.prep();r=self.no('J1','INICIO_TURNO_V24_TESTE',aceite_escopo=SCOPE,gibbering_aplicavel_fixture=True,wis_d20_simulado=1,gibbering_d8_simulado=8)
        self.assertEqual(r['decisao'],'PENDENTE')
    def test_14_early_manual_pass_rejected(self):
        self.prep();self.start_owl();self.no('J1','PASSAR_TURNO_V24_TESTE')
    def test_15_attack_normal_ac_turn(self):
        self.prep();self.start_owl();r=self.owl_attack();self.assertEqual(r['dano_aplicado'],7);self.assertEqual(self.m()['pv_atual'],45)
    def test_16_next_turn_start_mandatory(self):
        self.prep();self.start_owl();self.owl_attack();self.no('J2','ATAQUE_V24_TESTE',aceite_escopo=SCOPE,ataque='Bite',d20_simulados=[14],dano_dados=[1,4])
    def test_17_spit_out_of_turn(self):
        self.prep();self.no('J2','BLINDING_SPITTLE_V24_TESTE',aceite_escopo=SCOPE,alvo_na_area_fixture=True,dex_d20_simulado=2,dano_d6_simulados=[2,2])
    def test_18_spit_requires_explicit_area(self):
        self.prep(j2first=True);self.start_mouther();self.no('J2','BLINDING_SPITTLE_V24_TESTE',aceite_escopo=SCOPE)
    def test_19_spit_success_no_damage_blind(self):
        self.prep(j2first=True);self.start_mouther();r=self.spit(8)
        self.assertEqual(r['salvaguarda_des']['total'],10);self.assertEqual(self.owl()['pv_atual'],19);self.assertNotIn('Blinded',self.owl()['condicoes'])
    def test_20_spit_resistance_round_down(self):
        self.prep(j2first=True);self.start_mouther();r=self.spit(4,(5,4));self.assertEqual(r['dano_bruto'],9);self.assertEqual(r['dano_aplicado'],4);self.assertEqual(self.owl()['pv_atual'],15)
    def test_21_spit_blinded_duration(self):
        self.prep(j2first=True);self.start_mouther();r=self.spit(3,(2,3))
        self.assertEqual(r['blinded_ate_fim_turno_mouther'],2)
        self.assertIn('Blinded',self.owl()['condicoes']);self.assertEqual(len(self.owl()['efeitos']),1)
    def test_22_spit_invalid_damage_roll(self):
        self.prep(j2first=True);self.start_mouther();self.no('J2','BLINDING_SPITTLE_V24_TESTE',aceite_escopo=SCOPE,alvo_na_area_fixture=True,dex_d20_simulado=1,dano_d6_simulados=[7,1])
    def test_23_spit_no_spatial_assumption(self):
        self.prep(j2first=True);self.start_mouther();r=self.spit(area=False)
        self.assertEqual(self.owl()['pv_atual'],19);self.assertFalse(self.g.state['combate']['v24']['spittle_disponivel'])
    def test_24_recharge_1_remains_unavailable(self):
        self.prep(j2first=True);self.start_mouther();self.spit(area=False)
        self.start_owl(False);self.owl_attack(rolls=(2,),dice=())
        r=self.start_mouther(recharge=1);self.assertFalse(r['recarga_spittle']['recarregou'])
        self.no('J2','BLINDING_SPITTLE_V24_TESTE',aceite_escopo=SCOPE,alvo_na_area_fixture=False)
    def test_25_recharge_5_available(self):
        self.prep(j2first=True);self.start_mouther();self.spit(area=False)
        self.start_owl(False);self.owl_attack(rolls=(2,),dice=())
        r=self.start_mouther(recharge=5);self.assertTrue(r['recarga_spittle']['recarregou'])
        self.spit(area=False)
    def test_26_missing_recharge_roll_no_mutation(self):
        self.prep(j2first=True);self.start_mouther();self.spit(area=False)
        self.start_owl(False);self.owl_attack(rolls=(2,),dice=())
        self.no('J2','INICIO_TURNO_V24_TESTE',aceite_escopo=SCOPE)
    def test_27_blinded_owl_disadvantage(self):
        self.prep(j2first=True);self.start_mouther();self.spit(1,(2,3))
        self.start_owl(False)
        r=self.owl_attack(rolls=(18,4),dice=())
        self.assertEqual(r['modo_rolagem'],'DESVANTAGEM');self.assertEqual(r['d20_aplicado'],4)
    def test_28_disadvantage_requires_two_d20(self):
        self.prep(j2first=True);self.start_mouther();self.spit(1,(2,3))
        self.start_owl(False)
        self.no('J1','ATAQUE_V24_TESTE',aceite_escopo=SCOPE,ataque='Talons',d20_simulados=[18],dano_dados=[5])
    def test_29_mouther_advantage_vs_blinded_owl(self):
        self.prep(j2first=True);self.start_mouther();self.spit(1,(2,3))
        self.start_owl(False);self.owl_attack(rolls=(2,3),dice=())
        self.start_mouther(recharge=2)
        r=self.mouther_attack(rolls=(1,15),dice=(2,3))
        self.assertEqual(r['modo_rolagem'],'VANTAGEM');self.assertEqual(r['d20_aplicado'],15)
    def test_30_blinded_expiry_end_next_mouther_turn(self):
        self.prep(j2first=True);self.start_mouther();self.spit(1,(2,3))
        self.start_owl(False);self.owl_attack(rolls=(2,3),dice=())
        self.start_mouther(recharge=3)
        r=self.mouther_attack(rolls=(1,1),dice=())
        self.assertIn('Blinded',r['efeitos_expirados']);self.assertNotIn('Blinded',self.owl()['condicoes'])
    def test_31_spit_cannot_be_used_twice_same_turn(self):
        self.prep(j2first=True);self.start_mouther();self.spit(area=False)
        self.no('J2','BLINDING_SPITTLE_V24_TESTE',aceite_escopo=SCOPE,alvo_na_area_fixture=False)
    def test_32_bite_does_not_knock_large_prone(self):
        self.prep(j2first=True);self.start_mouther();r=self.mouther_attack()
        self.assertFalse(r['prone_aplicado']);self.assertNotIn('Prone',self.owl()['condicoes'])
    def test_33_crit_only_doubles_damage_dice(self):
        self.prep();self.start_owl();r=self.owl_attack(rolls=(20,),dice=(4,5));self.assertTrue(r['critico']);self.assertEqual(r['dano_aplicado'],11)
    def test_34_crit_dice_count_enforced(self):
        self.prep();self.start_owl();self.no('J1','ATAQUE_V24_TESTE',aceite_escopo=SCOPE,ataque='Talons',d20_simulados=[20],dano_dados=[6])
    def test_35_natural_one(self):
        self.prep();self.start_owl();r=self.owl_attack(rolls=(1,),dice=());self.assertFalse(r['acertou'])
    def test_36_turn_switch_and_round(self):
        self.prep();self.start_owl();self.owl_attack();self.start_mouther();self.mouther_attack()
        self.assertEqual(self.g.state['combate']['rodada'],2);self.assertEqual(self.g.state['ator_da_vez'],'J1')
    def test_37_public_private_segregation(self):
        self.prep();s=json.dumps(self.g.public(),ensure_ascii=False)
        self.assertNotIn('CE-017',s);self.assertNotIn('AB-POC-017',s)
    def test_38_repeat_event_is_idempotent(self):
        self.prep();kw={'aceite_escopo':SCOPE,'gibbering_aplicavel_fixture':False}
        r1=self.g.apply('same_id','J1','INICIO_TURNO_V24_TESTE',kw)
        snap=copy.deepcopy(self.g.state)
        r2=self.g.apply('same_id','J1','INICIO_TURNO_V24_TESTE',kw)
        self.assertEqual(r1,r2);self.assertEqual(snap,self.g.state)
    def test_39_checkpoint_roundtrip(self):
        self.prep(j2first=True);self.start_mouther();self.spit(2,(4,3))
        cp=self.g.checkpoint();x=MotorCondicoesSRD.restore(cp,RECS)
        self.assertEqual(x.state,self.g.state);self.assertEqual(x.head_hash,self.g.head_hash)
    def test_40_checkpoint_tamper_rejected(self):
        self.prep();cp=self.g.checkpoint();cp['state']['placar']['J1']=2
        with self.assertRaises(CorruptedCheckpoint):MotorCondicoesSRD.restore(cp,RECS)
    def test_41_schema_projection_valid(self):
        import jsonschema
        schema=json.loads((ROOT/'SCHEMA_ESTADO_POC.json').read_text(encoding='utf-8'))
        self.prep(j2first=True);self.start_mouther();self.spit(1,(1,1))
        jsonschema.validate(self.g.schema_projection(),schema)
    def test_42_all_40_ids_remain_in_valid_zones(self):
        self.prep(j2first=True);self.start_mouther();self.spit(3,(3,2))
        self.assertTrue(self.g.validate());self.assertEqual(len(self.g.state['jogadores']['J1']['cartas']),40)
    def test_43_wrong_actor_rejected(self):
        self.prep();self.no('J2','INICIO_TURNO_V24_TESTE',aceite_escopo=SCOPE)
    def test_44_wrong_scope_rejected(self):
        self.prep();self.no('J1','INICIO_TURNO_V24_TESTE',aceite_escopo='SRD_COMPLETO',gibbering_aplicavel_fixture=False)
    def test_45_wrong_die_type_rejected(self):
        self.prep();self.no('J1','INICIO_TURNO_V24_TESTE',aceite_escopo=SCOPE,gibbering_aplicavel_fixture=True,wis_d20_simulado=True)
    def test_46_rejected_action_does_not_mutate_event_hash(self):
        self.prep();before=self.g.head_hash;self.no('J1','PASSAR_TURNO_V24_TESTE');self.assertEqual(before,self.g.head_hash)
    def test_47_no_extra_draw_during_combat(self):
        self.prep(j2first=True);before=[len(self.g.state['jogadores'][p]['monte_ordem_ids']) for p in ('J1','J2')]
        self.start_mouther();self.spit(area=False)
        after=[len(self.g.state['jogadores'][p]['monte_ordem_ids']) for p in ('J1','J2')]
        self.assertEqual(before,after)
    def test_48_spit_success_rejects_damage_dice(self):
        self.prep(j2first=True);self.start_mouther();self.no('J2','BLINDING_SPITTLE_V24_TESTE',aceite_escopo=SCOPE,alvo_na_area_fixture=True,dex_d20_simulado=17,dano_d6_simulados=[3,4])

if __name__=='__main__':unittest.main(verbosity=2)
"""Automated and adversarial tests for Deva/Cure Wounds SRD v2.5 fixture."""
import copy,json,pathlib,sys,unittest
from motor_magias_srd import MotorMagiasSRD,SCOPE,DEVA,MOUTH
from motor_base_v22 import InvalidAction,CorruptedCheckpoint
ROOT=pathlib.Path(__file__).resolve().parent
RECORDS=json.loads((ROOT/'STATUS_FICHAS_SUPORTES_80.json').read_text(encoding='utf-8'))['registros']
HANDS={'J1':['CE-001','CE-026','CE-017','CE-029','CE-035'],
       'J2':['AB-POC-008','AB-POC-001','AB-POC-017','AB-POC-021','AB-POC-033']}

class TestMagiasSRD(unittest.TestCase):
    def setUp(self):
        self.g=MotorMagiasSRD(RECORDS,hands=HANDS);self.counter=0
    def apply(self,who,cmd,**kw):
        self.counter+=1
        return self.g.apply(f'v25test-{self.counter:04d}',who,cmd,kw)
    def yes(self,who,cmd,**kw):
        r=self.apply(who,cmd,**kw);self.assertEqual(r['decisao'],'ACEITA',r);return r['resultado']
    def no(self,who,cmd,**kw):
        old=copy.deepcopy(self.g.state);old_hash=self.g.head_hash
        r=self.apply(who,cmd,**kw)
        self.assertIn(r['decisao'],('REJEITADA','PENDENTE'),r)
        self.assertEqual(self.g.state,old);self.assertEqual(self.g.head_hash,old_hash)
        return r
    def setup_combat(self,j2first=False,injured=None):
        self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
        self.yes('J1','INVOCAR',carta_id='CE-001')
        self.yes('J1','EVOLUIR',carta_id=DEVA)
        self.yes('J1','PRONTO_CRIATURA')
        self.yes('J2','INVOCAR',carta_id=MOUTH);self.yes('J2','PRONTO_CRIATURA')
        self.yes('J1','ESCOLHER_SUPORTE',carta_id=None)
        self.yes('J2','ESCOLHER_SUPORTE',carta_id=None)
        self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
        self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
        self.yes('ARBITRO','INICIATIVA_DEVA_V25_TESTE',d20_simulados={'J1':1,'J2':20} if j2first else {'J1':17,'J2':10})
        if injured is not None:
            self.yes('ARBITRO','FERIMENTO_DEVA_V25_FIXTURE',pv_atual=injured,aceite_escopo=SCOPE,origem='FERIMENTO_ARTIFICIAL_SEM_EVENTO_SRD')
    def start(self,actor='J1',near=False,wis=1):
        kwargs={'aceite_escopo':SCOPE}
        if actor=='J1':
            kwargs['gibbering_aplicavel_fixture']=near
            if near:kwargs['sab_d20_simulado']=wis
        return self.yes(actor,'INICIO_TURNO_DEVA_V25_TESTE',**kwargs)
    def bonus(self,rolls=(3,4)):
        return self.yes('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=list(rolls))
    def attack(self,a=None):
        if a is None:a=[{'d20_simulado':1},{'d20_simulado':1}]
        return self.yes('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=a)
    def next_round(self):
        self.yes('J1','ENCERRAR_TURNO_DEVA_V25_TESTE')
        self.start('J2')
        self.yes('J2','ENCERRAR_TURNO_DEVA_V25_TESTE')
        self.start('J1')
    def deva(self):return self.g.state['jogadores']['J1']['cartas'][DEVA]
    def mouther(self):return self.g.state['jogadores']['J2']['cartas'][MOUTH]
    def test_01_cannot_initiative_without_deva(self):self.no('ARBITRO','INICIATIVA_DEVA_V25_TESTE',d20_simulados={'J1':10,'J2':10})
    def test_02_evolution_discards_owl(self):
        self.setup_combat();self.assertEqual(self.g.state['jogadores']['J1']['cartas']['CE-001']['zona'],'CEMITERIO')
    def test_03_deva_full_hp_on_evolution(self):
        self.setup_combat();self.assertEqual(self.deva()['pv_atual'],229)
    def test_04_two_day_shared_charges_initialized(self):
        self.setup_combat();self.assertEqual(self.deva()['recursos']['divine_aid_restante'],2)
    def test_05_initiative_deva_mod4(self):
        self.setup_combat();self.assertEqual(self.g.state['combate']['iniciativas']['J1'],21)
    def test_06_initiative_mouther_mod_minus1(self):
        self.setup_combat();self.assertEqual(self.g.state['combate']['iniciativas']['J2'],9)
    def test_07_non_owner_bonus_rejected(self):
        self.setup_combat(j2first=True);self.start('J2');self.no('J2','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[2,2])
    def test_08_bonus_before_turn_start(self):
        self.setup_combat();self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[2,2])
    def test_09_gibbering_inapplicable_without_confirmation(self):
        self.setup_combat();self.no('J1','INICIO_TURNO_DEVA_V25_TESTE',aceite_escopo=SCOPE)
    def test_10_gibbering_deva_wis9(self):
        self.setup_combat();r=self.start(near=True,wis=1);self.assertEqual(r['gibbering']['total'],10)
    def test_11_gibbering_no_false_natural1_auto_fail(self):
        self.setup_combat();r=self.start(near=True,wis=1);self.assertTrue(r['gibbering']['sucesso'])
    def test_12_no_roll_when_gibbering_outside(self):
        self.setup_combat();self.no('J1','INICIO_TURNO_DEVA_V25_TESTE',aceite_escopo=SCOPE,gibbering_aplicavel_fixture=False,sab_d20_simulado=1)
    def test_13_bonus_2d8_plus5(self):
        self.setup_combat(injured=170);self.start();r=self.bonus((3,4));self.assertEqual(r['cura_calculada'],12);self.assertEqual(self.deva()['pv_atual'],182)
    def test_14_bonus_capped_at_maxhp(self):
        self.setup_combat(injured=226);self.start();r=self.bonus((8,8));self.assertEqual(r['cura_efetiva'],3);self.assertEqual(self.deva()['pv_atual'],229)
    def test_15_bonus_at_full_hp_consumes_charge(self):
        self.setup_combat();self.start();r=self.bonus((2,2));self.assertEqual(r['cura_efetiva'],0);self.assertEqual(r['usos_restantes'],1)
    def test_16_bonus_invalid_dice_count(self):
        self.setup_combat();self.start();self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[3])
    def test_17_bonus_invalid_die0(self):
        self.setup_combat();self.start();self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[0,1])
    def test_18_bonus_wrong_target(self):
        self.setup_combat();self.start();self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=MOUTH,d8_simulados=[2,2])
    def test_19_bonus_wrong_spell(self):
        self.setup_combat();self.start();self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Remove Curse',alvo=DEVA,d8_simulados=[2,2])
    def test_20_two_bonus_one_turn_illegal(self):
        self.setup_combat();self.start();self.bonus();self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[2,2])
    def test_21_action_after_bonus(self):
        self.setup_combat(injured=185);self.start();self.bonus();r=self.attack();self.assertEqual(len(r['detalhes']),2)
    def test_22_bonus_after_action(self):
        self.setup_combat(injured=185);self.start();self.attack();r=self.bonus();self.assertEqual(r['usos_restantes'],1)
    def test_23_second_bonus_next_turn(self):
        self.setup_combat(injured=100);self.start();self.bonus();self.next_round();r=self.bonus();self.assertEqual(r['usos_restantes'],0)
    def test_24_exhausted_charge_reject(self):
        self.setup_combat(injured=100);self.start();self.bonus();self.next_round();self.bonus();self.next_round();self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[1,1])
    def test_25_multiattack_natural1_misses(self):
        self.setup_combat();self.start();r=self.attack();self.assertFalse(r['detalhes'][0]['acertou']);self.assertEqual(self.mouther()['pv_atual'],52)
    def test_26_multiattack_hit_damage_types(self):
        self.setup_combat();self.start();a={'d20_simulado':11,'d6_contundente':[5],'d8_radiante':[1,2,3,4]}
        r=self.attack([a,{'d20_simulado':1}]);self.assertEqual(r['detalhes'][0]['dano'],19);self.assertEqual(self.mouther()['pv_atual'],33)
    def test_27_multiattack_two_hits(self):
        self.setup_combat();self.start();a={'d20_simulado':10,'d6_contundente':[1],'d8_radiante':[1]*4}
        self.attack([a,a]);self.assertEqual(self.mouther()['pv_atual'],34)
    def test_28_crit_doubles_damage_dice_not_flat(self):
        self.setup_combat();self.start();a={'d20_simulado':20,'d6_contundente':[1,1],'d8_radiante':[1]*8}
        r=self.attack([a,{'d20_simulado':1}]);self.assertEqual(r['detalhes'][0]['dano'],14)
    def test_29_crit_wrong_dice_reject(self):
        self.setup_combat();self.start();a={'d20_simulado':20,'d6_contundente':[1],'d8_radiante':[1]*8}
        self.no('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[a,{'d20_simulado':1}])
    def test_30_second_action_same_turn_rejected(self):
        self.setup_combat();self.start();self.attack();self.no('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[{'d20_simulado':1},{'d20_simulado':1}])
    def test_31_one_attack_without_ko_rejected_atomic(self):
        self.setup_combat();self.start();self.no('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[{'d20_simulado':1}])
    def test_32_ko_first_attack_no_second(self):
        self.setup_combat();self.start();a={'d20_simulado':20,'d6_contundente':[6,6],'d8_radiante':[8]*8}
        r=self.attack([a]);self.assertTrue(r['ko']);self.assertEqual(self.g.state['fase'],'POS_COMBATE');self.assertEqual(self.g.state['placar']['J1'],1)
    def test_33_second_attack_after_ko_rejected_atomic(self):
        self.setup_combat();self.start();a={'d20_simulado':20,'d6_contundente':[6,6],'d8_radiante':[8]*8}
        self.no('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[a,{'d20_simulado':1}])
    def test_34_ko_at_second(self):
        self.setup_combat();self.start();a={'d20_simulado':16,'d6_contundente':[6],'d8_radiante':[6]*4}
        r=self.attack([a,a]);self.assertTrue(r['ko']);self.assertEqual(len(r['detalhes']),2)
    def test_35_reaction_ability_unavailable(self):
        self.setup_combat();self.start();self.no('J1','REACAO_DEVA_V25_TESTE')
    def test_36_fixture_wound_restricted_to_arbiter(self):
        self.setup_combat();self.no('J1','FERIMENTO_DEVA_V25_FIXTURE',pv_atual=180,aceite_escopo=SCOPE,origem='FERIMENTO_ARTIFICIAL_SEM_EVENTO_SRD')
    def test_37_fixture_wound_once(self):
        self.setup_combat(injured=190);self.no('ARBITRO','FERIMENTO_DEVA_V25_FIXTURE',pv_atual=160,aceite_escopo=SCOPE,origem='FERIMENTO_ARTIFICIAL_SEM_EVENTO_SRD')
    def test_38_cannot_fixture_wound_after_start(self):
        self.setup_combat();self.start();self.no('ARBITRO','FERIMENTO_DEVA_V25_FIXTURE',pv_atual=160,aceite_escopo=SCOPE,origem='FERIMENTO_ARTIFICIAL_SEM_EVENTO_SRD')
    def test_39_no_extra_draw_during_combat(self):
        self.setup_combat(injured=200);before=len(self.g.state['jogadores']['J1']['monte_ordem_ids']);self.start();self.bonus();self.assertEqual(before,len(self.g.state['jogadores']['J1']['monte_ordem_ids']))
    def test_40_conservation_of_40_copies(self):
        self.setup_combat(injured=200);self.start();self.bonus();self.attack();self.assertTrue(self.g.validate())
    def test_41_public_no_secret_hands(self):
        self.setup_combat();x=json.dumps(self.g.public());self.assertNotIn('CE-017',x);self.assertNotIn('AB-POC-017',x)
    def test_42_checkpoint_roundtrip(self):
        self.setup_combat(injured=210);self.start();self.bonus();p=self.g.checkpoint();r=MotorMagiasSRD.restore(p,RECORDS);self.assertEqual(r.state,self.g.state)
    def test_43_checkpoint_tamper(self):
        self.setup_combat();p=self.g.checkpoint();p['state']['placar']['J1']=2
        with self.assertRaises(CorruptedCheckpoint):MotorMagiasSRD.restore(p,RECORDS)
    def test_44_replay_event_idempotent(self):
        self.setup_combat();params={'aceite_escopo':SCOPE,'gibbering_aplicavel_fixture':False}
        r1=self.g.apply('same','J1','INICIO_TURNO_DEVA_V25_TESTE',params);s=copy.deepcopy(self.g.state)
        r2=self.g.apply('same','J1','INICIO_TURNO_DEVA_V25_TESTE',params);self.assertEqual(r1,r2);self.assertEqual(s,self.g.state)
    def test_45_bad_event_id_collision(self):
        self.setup_combat();self.g.apply('collision','J1','INICIO_TURNO_DEVA_V25_TESTE',{'aceite_escopo':SCOPE,'gibbering_aplicavel_fixture':False})
        with self.assertRaises(InvalidAction):self.g.apply('collision','J1','INICIO_TURNO_DEVA_V25_TESTE',{'aceite_escopo':SCOPE,'gibbering_aplicavel_fixture':True})
    def test_46_legacy_ko_rejected(self):
        self.setup_combat();self.no('ARBITRO','KO_COMBATE_FIXTURE',vencedor='J1',comprovante_fixture=True)
    def test_47_wrong_scope(self):
        self.setup_combat();self.no('J1','INICIO_TURNO_DEVA_V25_TESTE',aceite_escopo='COMBATE_COMPLETO',gibbering_aplicavel_fixture=False)
    def test_48_j2_turn_no_deva_action(self):
        self.setup_combat(j2first=True);self.start('J2');self.no('J2','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[{'d20_simulado':1},{'d20_simulado':1}])
    def test_49_action_economy_resets_next_turn(self):
        self.setup_combat();self.start();self.attack();self.next_round();self.attack();self.assertEqual(self.g.state['combate']['rodada'],2)
    def test_50_no_bonus_after_ko(self):
        self.setup_combat();self.start();a={'d20_simulado':20,'d6_contundente':[6,6],'d8_radiante':[8]*8};self.attack([a]);self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[1,1])
    def test_51_schema_projection(self):
        import jsonschema
        schema=json.loads((ROOT/'SCHEMA_ESTADO_POC.json').read_text(encoding='utf-8'))
        self.setup_combat(injured=209);self.start();self.bonus()
        jsonschema.validate(self.g.schema_projection(),schema)
    def test_52_resource_not_refilled_open_cycle(self):
        self.setup_combat(injured=180);self.start();self.bonus();a={'d20_simulado':20,'d6_contundente':[6,6],'d8_radiante':[8]*8};self.attack([a]);self.yes('ARBITRO','ABRIR_CICLO');self.assertEqual(self.deva()['recursos']['divine_aid_restante'],1)
    def test_53_deva_precombat_bonus_invalid(self):
        self.yes('J1','TROCAR',descartar=[]);self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[2,2])
    def test_54_gibbering_needs_wis_roll(self):
        self.setup_combat();self.no('J1','INICIO_TURNO_DEVA_V25_TESTE',aceite_escopo=SCOPE,gibbering_aplicavel_fixture=True)
    def test_55_unknown_cure_die_bool(self):
        self.setup_combat();self.start();self.no('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[True,2])

if __name__=='__main__':unittest.main(verbosity=2)
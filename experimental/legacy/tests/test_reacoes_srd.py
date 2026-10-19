"""Adversarial tests for v2.6 opportunity attack; no official match."""
import copy,json,pathlib,unittest
from motor_reacoes_srd import MotorReacoesSRD,SCOPE_REACOES,DEVA,MOUTH
from motor_magias_srd import SCOPE
from motor_base_v22 import InvalidAction,CorruptedCheckpoint
ROOT=pathlib.Path(__file__).resolve().parent
RECORDS=json.loads((ROOT/'STATUS_FICHAS_SUPORTES_80.json').read_text(encoding='utf-8'))['registros']
HANDS={'J1':['CE-001','CE-026','CE-017','CE-029','CE-035'],
       'J2':['AB-POC-008','AB-POC-001','AB-POC-017','AB-POC-021','AB-POC-033']}

class TestReacoesSRD(unittest.TestCase):
    def setUp(self):
        self.g=MotorReacoesSRD(RECORDS,hands=HANDS);self.n=0
    def apply(self,p,cmd,**kw):
        self.n+=1;return self.g.apply(f'v26-{self.n:04d}',p,cmd,kw)
    def yes(self,p,cmd,**kw):
        r=self.apply(p,cmd,**kw);self.assertEqual(r['decisao'],'ACEITA',r);return r['resultado']
    def no(self,p,cmd,**kw):
        before=copy.deepcopy(self.g.state);h=self.g.head_hash
        r=self.apply(p,cmd,**kw);self.assertIn(r['decisao'],('PENDENTE','REJEITADA'),r)
        self.assertEqual(self.g.state,before);self.assertEqual(self.g.head_hash,h);return r
    def setup_combat(self,j2first=True,configure=True):
        for p in ('J1','J2'):self.yes(p,'TROCAR',descartar=[])
        self.yes('J1','INVOCAR',carta_id='CE-001');self.yes('J1','EVOLUIR',carta_id=DEVA)
        self.yes('J1','PRONTO_CRIATURA');self.yes('J2','INVOCAR',carta_id=MOUTH)
        self.yes('J2','PRONTO_CRIATURA')
        for p in ('J1','J2'):self.yes(p,'ESCOLHER_SUPORTE',carta_id=None)
        for _ in range(2):self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
        self.yes('ARBITRO','INICIATIVA_DEVA_V25_TESTE',d20_simulados={'J1':1,'J2':20} if j2first else {'J1':17,'J2':10})
        if configure:self.yes('ARBITRO','CONFIGURAR_DISTANCIA_V26_FIXTURE',aceite_escopo=SCOPE_REACOES,
                    distancia_ft=5,origem='POSICIONAMENTO_ARTIFICIAL_EXPLICITO_DE_TESTE')
    def start(self,p):
        kw={'aceite_escopo':SCOPE}
        if p=='J1':kw.update(gibbering_aplicavel_fixture=True,sab_d20_simulado=1)
        return self.yes(p,'INICIO_TURNO_DEVA_V25_TESTE',**kw)
    def mover(self,dest=10,**kw):
        return self.yes('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,
                        tipo='DESLOCAMENTO',visivel_ao_deva=True,destino_ft=dest,**kw)
    def attack(self,roll=10,b=(1,),r=(1,1,1,1)):
        return self.yes('J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES,
                        ataque={'d20_simulado':roll,'d6_contundente':list(b),'d8_radiante':list(r)})
    def trigger(self):
        self.setup_combat();self.start('J2');self.mover()
    def v(self):return self.g.state['combate']['v26']
    def test_01_initiative_requires_position(self):
        self.setup_combat(configure=False);self.no('J2','INICIO_TURNO_DEVA_V25_TESTE',aceite_escopo=SCOPE)
    def test_02_config_once(self):
        self.setup_combat();self.no('ARBITRO','CONFIGURAR_DISTANCIA_V26_FIXTURE',aceite_escopo=SCOPE_REACOES,distancia_ft=5,origem='POSICIONAMENTO_ARTIFICIAL_EXPLICITO_DE_TESTE')
    def test_03_config_wrong_distance(self):
        self.setup_combat(configure=False);self.no('ARBITRO','CONFIGURAR_DISTANCIA_V26_FIXTURE',aceite_escopo=SCOPE_REACOES,distancia_ft=10,origem='POSICIONAMENTO_ARTIFICIAL_EXPLICITO_DE_TESTE')
    def test_04_config_player_forbidden(self):
        self.setup_combat(configure=False);self.no('J1','CONFIGURAR_DISTANCIA_V26_FIXTURE',aceite_escopo=SCOPE_REACOES,distancia_ft=5,origem='POSICIONAMENTO_ARTIFICIAL_EXPLICITO_DE_TESTE')
    def test_05_trigger_freezes_before_exit(self):
        self.trigger();self.assertEqual(self.v()['distancia_ft'],5);self.assertIsNotNone(self.v()['pendencia_reacao'])
    def test_06_wrong_actor_reaction(self):
        self.trigger();self.no('J2','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
    def test_07_reaction_single_hit(self):
        self.trigger();r=self.attack();self.assertEqual(r['dano'],9);self.assertEqual(self.g.get_card(self.g.state,'J2',MOUTH)['pv_atual'],43)
    def test_08_reaction_consumed(self):
        self.trigger();self.attack();self.assertTrue(self.v()['reacao_usada']['J1']);self.assertEqual(self.v()['distancia_ft'],10)
    def test_09_miss_consumes(self):
        self.trigger();r=self.attack(roll=1,b=(),r=());self.assertFalse(r['acertou']);self.assertTrue(self.v()['reacao_usada']['J1'])
    def test_10_critical_dice_double(self):
        self.trigger();r=self.attack(roll=20,b=(1,1),r=(1,)*8);self.assertTrue(r['critico']);self.assertEqual(r['dano'],14)
    def test_11_critical_invalid_dice_atomic(self):
        self.trigger();self.no('J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES,ataque={'d20_simulado':20,'d6_contundente':[1],'d8_radiante':[1]*8})
    def test_12_decline_no_consumption(self):
        self.trigger();self.yes('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        self.assertFalse(self.v()['reacao_usada']['J1']);self.assertEqual(self.v()['distancia_ft'],10)
    def test_13_pending_blocks_end_turn(self):
        self.trigger();self.no('J2','ENCERRAR_TURNO_DEVA_V25_TESTE')
    def test_14_pending_blocks_other_move(self):
        self.trigger();self.no('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='DESLOCAMENTO',visivel_ao_deva=True,destino_ft=5)
    def test_15_no_spurious_reaction(self):
        self.setup_combat();self.start('J2');self.no('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
    def test_16_teleport_not_invented(self):
        self.setup_combat();self.start('J2');self.no('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='TELEPORTE',visivel_ao_deva=True,destino_ft=10)
    def test_17_forced_move_not_invented(self):
        self.setup_combat();self.start('J2');self.no('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='FORCADO',visivel_ao_deva=True,destino_ft=10)
    def test_18_visibility_required(self):
        self.setup_combat();self.start('J2');self.no('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='DESLOCAMENTO',visivel_ao_deva=False,destino_ft=10)
    def test_19_disengage_suppresses(self):
        self.setup_combat();self.start('J2');self.yes('J2','DESENGAJAR_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        r=self.mover();self.assertEqual(r['motivo'],'DESENGAJOU');self.assertIsNone(self.v()['pendencia_reacao'])
    def test_20_disengage_consumes_action(self):
        self.setup_combat();self.start('J2');self.yes('J2','DESENGAJAR_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        self.assertTrue(self.g.state['combate']['v25']['acao_utilizada']);self.no('J2','DESENGAJAR_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES)
    def test_21_move_reach_entry_no_trigger(self):
        self.trigger();self.yes('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        r=self.mover(5);self.assertEqual(r['motivo'],'NAO_SAIU_DO_ALCANCE')
    def test_22_movement_budget(self):
        self.trigger();self.yes('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        self.mover(5);self.no('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='DESLOCAMENTO',visivel_ao_deva=True,destino_ft=10)
    def test_23_reaction_refresh_at_own_turn(self):
        self.trigger();self.attack();self.yes('J2','ENCERRAR_TURNO_DEVA_V25_TESTE')
        self.assertTrue(self.v()['reacao_usada']['J1']);self.start('J1');self.assertFalse(self.v()['reacao_usada']['J1'])
    def test_24_reaction_not_refresh_at_other_turn(self):
        self.trigger();self.attack();self.assertTrue(self.v()['reacao_usada']['J1']);self.yes('J2','ENCERRAR_TURNO_DEVA_V25_TESTE');self.assertTrue(self.v()['reacao_usada']['J1'])
    def test_25_action_and_bonus_separate(self):
        self.trigger();self.attack(roll=1,b=(),r=());self.mover(5);self.yes('J2','ENCERRAR_TURNO_DEVA_V25_TESTE');self.start('J1')
        self.yes('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[1,1])
        self.yes('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[{'d20_simulado':1},{'d20_simulado':1}])
    def test_26_ko_before_movement(self):
        self.trigger();r=self.attack(roll=20,b=(6,6),r=(8,)*8);self.assertTrue(r['ko']);self.assertEqual(self.v()['distancia_ft'],5)
        self.assertEqual(self.g.state['fase'],'POS_COMBATE')
    def test_27_no_second_reaction_same_trigger(self):
        self.trigger();self.attack();self.no('J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES,ataque={'d20_simulado':1,'d6_contundente':[],'d8_radiante':[]})
    def test_28_invalid_roll_atomic(self):
        self.trigger();self.no('J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES,ataque={'d20_simulado':0,'d6_contundente':[],'d8_radiante':[]})
    def test_29_no_roll_on_decline(self):
        self.trigger();self.no('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES,d20_simulado=1)
    def test_30_checkpoint_roundtrip(self):
        self.trigger();p=self.g.checkpoint();restored=MotorReacoesSRD.restore(p,RECORDS)
        self.assertEqual(restored.state,self.g.state);self.assertEqual(restored.head_hash,self.g.head_hash)
    def test_31_checkpoint_tamper(self):
        self.trigger();p=self.g.checkpoint();p['state']['combate']['v26']['distancia_ft']=10
        with self.assertRaises(CorruptedCheckpoint):MotorReacoesSRD.restore(p,RECORDS)
    def test_32_public_no_hidden_hands(self):
        self.trigger();view=json.dumps(self.g.public());self.assertNotIn('CE-017',view);self.assertNotIn('AB-POC-017',view)
    def test_33_40_copies_conserved(self):
        self.trigger();self.attack();self.assertTrue(self.g.validate())
    def test_34_idempotence(self):
        self.trigger();params={'aceite_escopo':SCOPE_REACOES,'ataque':{'d20_simulado':1,'d6_contundente':[],'d8_radiante':[]}}
        a=self.g.apply('same-reaction','J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',params)
        state=copy.deepcopy(self.g.state);b=self.g.apply('same-reaction','J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',params)
        self.assertEqual(a,b);self.assertEqual(self.g.state,state)
    def test_35_no_new_official_shuffle(self):
        self.trigger();self.attack();self.assertFalse(self.g.state['prioridade_preparacao']['sorteio_realizado'])
    def test_36_no_reaction_without_visibility_fixture(self):
        self.setup_combat();self.start('J2');self.no('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='DESLOCAMENTO',destino_ft=10)
    def test_37_deva_own_turn_reaction_not_allowed_without_trigger(self):
        self.setup_combat(j2first=False);self.start('J1');self.no('J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES,ataque={'d20_simulado':1,'d6_contundente':[],'d8_radiante':[]})
    def test_38_initial_distance_is_not_auto_inferred(self):
        self.setup_combat(configure=False);self.assertIsNone(self.v()['distancia_ft'])
    def test_39_round_progress_after_decline(self):
        self.trigger();self.yes('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        self.yes('J2','ENCERRAR_TURNO_DEVA_V25_TESTE');self.start('J1');self.assertEqual(self.g.state['combate']['rodada'],1)
    def test_40_invalid_bool_die(self):
        self.trigger();self.no('J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES,ataque={'d20_simulado':True,'d6_contundente':[],'d8_radiante':[]})

    def test_41_out_of_reach_normal_attack_rejected(self):
        self.trigger();self.yes('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        self.yes('J2','ENCERRAR_TURNO_DEVA_V25_TESTE');self.start('J1')
        self.no('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[{'d20_simulado':1},{'d20_simulado':1}])
    def test_42_normal_attack_allowed_if_in_reach(self):
        self.trigger();self.yes('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        self.mover(5);self.yes('J2','ENCERRAR_TURNO_DEVA_V25_TESTE');self.start('J1')
        r=self.yes('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[{'d20_simulado':1},{'d20_simulado':1}])
        self.assertEqual(len(r['detalhes']),2)

if __name__=='__main__':unittest.main(verbosity=2)
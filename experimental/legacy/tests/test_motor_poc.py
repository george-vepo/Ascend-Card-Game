"""Automated tests exclusively against isolated experimental v2.2 engine, no real match."""
import copy, json, pathlib, unittest
from motor_poc import MotorPOC, CorruptedCheckpoint, InvalidAction

SRC=pathlib.Path(__file__).resolve().parent/'STATUS_FICHAS_SUPORTES_80.json'
RECORDS=json.loads(SRC.read_text(encoding='utf-8'))['registros']
HANDS={
 'J1':['CE-001','CE-017','CE-019','CE-029','CE-035'],
 'J2':['AB-POC-001','AB-POC-008','AB-POC-017','AB-POC-021','AB-POC-033']
}
class FlowTest(unittest.TestCase):
 def setUp(self):
  self.g=MotorPOC(RECORDS,first='J1',hands=HANDS)
  self.k=0
 def action(self,actor,command,**params):
  self.k+=1
  return self.g.apply(f'evt-{self.k:03}',actor,command,params)
 def yes(self,actor,command,**params):
  x=self.action(actor,command,**params);self.assertEqual(x['decisao'],'ACEITA',x);return x
 def no(self,actor,command,**params):
  before=copy.deepcopy(self.g.state)
  x=self.action(actor,command,**params)
  self.assertIn(x['decisao'],('REJEITADA','PENDENTE'),x)
  self.assertEqual(self.g.state,before)
  return x
 def creatures(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.yes('J1','INVOCAR',carta_id='CE-001');self.yes('J1','PRONTO_CRIATURA')
  self.yes('J2','INVOCAR',carta_id='AB-POC-001');self.yes('J2','PRONTO_CRIATURA')
 def support(self,support1=None,support2=None):
  self.creatures()
  self.yes('J1','ESCOLHER_SUPORTE',carta_id=support1)
  self.yes('J2','ESCOLHER_SUPORTE',carta_id=support2)
 def battle(self):
  self.support()
  self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
  self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
  self.yes('ARBITRO','INICIATIVA_FIXTURE',comprovante_fixture=True,totais={'J1':7,'J2':12})

 def test_01_decks_have_40(self):
  self.assertEqual([len(self.g.state['jogadores'][p]['cartas']) for p in ('J1','J2')],[40,40]);self.assertTrue(self.g.validate())
 def test_02_5_initial_cards_each(self):
  self.assertEqual(len(self.g.hand(self.g.state,'J1')),5);self.assertEqual(len(self.g.hand(self.g.state,'J2')),5)
 def test_03_first_and_second_locked_without_real_lottery(self):
  self.assertFalse(self.g.state['prioridade_preparacao']['sorteio_realizado']);self.assertEqual(self.g.state['prioridade_preparacao']['primeiro'],'J1')
 def test_04_exchange_0(self):
  self.yes('J1','TROCAR',descartar=[]);self.assertEqual(self.g.state['fase'],'TROCA');self.assertEqual(len(self.g.hand(self.g.state,'J1')),5)
 def test_05_exchange_2(self):
  self.yes('J1','TROCAR',descartar=['CE-017','CE-019'])
  self.assertEqual(len(self.g.hand(self.g.state,'J1')),5)
  self.assertEqual(sum(x['zona']=='CEMITERIO' for x in self.g.state['jogadores']['J1']['cartas'].values()),2)
 def test_06_exchange_duplicated_id_rejected(self):self.no('J1','TROCAR',descartar=['CE-017','CE-017'])
 def test_07_exchange_not_in_hand_rejected(self):self.no('J1','TROCAR',descartar=['CE-036'])
 def test_08_out_of_turn_exchange_rejected(self):self.no('J2','TROCAR',descartar=[])
 def test_09_wrong_phase_summon_rejected(self):self.no('J1','INVOCAR',carta_id='CE-001')
 def test_10_skip_mandatory_turn_rejected(self):
  self.yes('J1','TROCAR',descartar=[]);self.no('J1','TROCAR',descartar=[])
 def test_11_only_common_summon(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.no('J1','INVOCAR',carta_id='CE-019')
 def test_12_summon_known_pv(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.yes('J1','INVOCAR',carta_id='CE-001');self.assertEqual(self.g.state['jogadores']['J1']['cartas']['CE-001']['pv_atual'],19)
 def test_13_cannot_summon_twice(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.yes('J1','INVOCAR',carta_id='CE-001');self.no('J1','INVOCAR',carta_id='CE-017')
 def test_14_evolve_adjacent(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.yes('J1','INVOCAR',carta_id='CE-001');self.yes('J1','EVOLUIR',carta_id='CE-019')
  self.assertEqual(self.g.state['jogadores']['J1']['cartas']['CE-001']['zona'],'CEMITERIO')
 def test_15_evolution_skip_rejected(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.yes('J1','INVOCAR',carta_id='CE-001');self.no('J1','EVOLUIR',carta_id='CE-029')
 def test_16_no_immediate_refill_after_evolution(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.yes('J1','INVOCAR',carta_id='CE-001');self.yes('J1','EVOLUIR',carta_id='CE-019');self.assertEqual(len(self.g.hand(self.g.state,'J1')),3)
 def test_17_cannot_ready_with_empty_field(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.no('J1','PRONTO_CRIATURA')
 def test_18_only_first_can_prepare_first(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.no('J2','INVOCAR',carta_id='AB-POC-001')
 def test_19_both_ready_then_support(self):
  self.creatures();self.assertEqual(self.g.state['fase'],'SELECAO_SUPORTE')
 def test_20_support_not_in_hand_rejected(self):
  self.creatures();self.no('J1','ESCOLHER_SUPORTE',carta_id='CE-001')
 def test_21_support_zero_is_valid(self):
  self.support();self.assertEqual(self.g.state['fase'],'RESOLUCAO_SUPORTE_TESTE')
 def test_22_support_reserved_stays_in_hand(self):
  self.support('CE-017',None);p=self.g.state['jogadores']['J1'];self.assertEqual(p['cartas']['CE-017']['zona'],'MAO');self.assertTrue(p['cartas']['CE-017']['suporte_reservado'])
 def test_23_second_support_remains_private(self):
  self.support('CE-017','AB-POC-017');s=str(self.g.public())
  self.assertNotIn('CE-017',s);self.assertNotIn('AB-POC-017',s)
 def test_24_private_is_role_scoped(self):
  self.support(None,'AB-POC-017');s=str(self.g.private('J1'));self.assertNotIn('AB-POC-017',s)
 def test_25_support_not_homologated_blocks_mechanics(self):
  self.support('CE-017',None);self.no('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='KO_TESTE')
 def test_26_ko_from_first_support_preserves_second(self):
  self.support('CE-017','AB-POC-017')
  self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='KO_TESTE',comprovante_fixture=True)
  self.assertEqual(self.g.state['fase'],'POS_COMBATE')
  self.assertEqual(self.g.state['placar'],{'J1':1,'J2':0})
  self.assertEqual(self.g.state['jogadores']['J2']['cartas']['AB-POC-017']['zona'],'MAO')
  self.assertIsNone(self.g.state['jogadores']['J2']['suporte_reservado_id'])
  self.assertEqual(self.g.state['jogadores']['J1']['cartas']['CE-017']['zona'],'CEMITERIO')
  self.assertEqual(self.g.state['combate']['iniciativas'],{})
 def test_27_no_immediate_ko_draw(self):
  self.support('CE-017',None)
  n=len(self.g.state['jogadores']['J1']['monte_ordem_ids'])
  self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='KO_TESTE',comprovante_fixture=True)
  self.assertEqual(n,len(self.g.state['jogadores']['J1']['monte_ordem_ids']))
 def test_28_next_cycle_refills_once(self):
  self.support('CE-017',None)
  self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='KO_TESTE',comprovante_fixture=True)
  self.yes('ARBITRO','ABRIR_CICLO')
  self.assertEqual(self.g.state['fase'],'TROCA')
  self.assertEqual(self.g.state['combate']['numero'],2)
  self.assertEqual(len(self.g.hand(self.g.state,'J1')),5)
  self.assertEqual(len(self.g.state['controle_saque_ciclo']['processados']),2)
 def test_29_double_cycle_prohibited(self):
  self.support('CE-017',None)
  self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='KO_TESTE',comprovante_fixture=True)
  self.yes('ARBITRO','ABRIR_CICLO');self.no('ARBITRO','ABRIR_CICLO')
 def test_30_fixture_initiative_independent_order(self):
  self.battle();self.assertEqual(self.g.state['combate']['iniciativas']['J2'],12)
  self.assertEqual(self.g.state['prioridade_preparacao']['primeiro'],'J1')
 def test_31_round_no_draw(self):
  self.battle();before={p:len(self.g.state['jogadores'][p]['monte_ordem_ids']) for p in ('J1','J2')}
  self.yes('ARBITRO','RODADA_SEGUINTE_FIXTURE')
  self.assertEqual(before,{p:len(self.g.state['jogadores'][p]['monte_ordem_ids']) for p in ('J1','J2')})
 def test_32_combat_fixture_ko(self):
  self.battle();self.yes('ARBITRO','KO_COMBATE_FIXTURE',comprovante_fixture=True,vencedor='J2')
  self.assertEqual(self.g.state['placar'],{'J1':0,'J2':1})
 def test_33_combat_ko_requires_fixture(self):
  self.battle();self.no('ARBITRO','KO_COMBATE_FIXTURE',vencedor='J2')
 def test_34_tie_initiative_blocks(self):
  self.support();self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR');self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
  self.no('ARBITRO','INICIATIVA_FIXTURE',comprovante_fixture=True,totais={'J1':8,'J2':8})
 def test_35_duplicate_idempotence(self):
  r1=self.g.apply('evt-A','J1','TROCAR',{'descartar':[]});s=copy.deepcopy(self.g.state)
  r2=self.g.apply('evt-A','J1','TROCAR',{'descartar':[]})
  self.assertEqual(r1,r2);self.assertEqual(self.g.state,s);self.assertEqual(len(self.g.events),1)
 def test_36_duplicate_id_different_payload_rejected(self):
  self.g.apply('evt-A','J1','TROCAR',{'descartar':[]})
  with self.assertRaises(InvalidAction):self.g.apply('evt-A','J1','TROCAR',{'descartar':['CE-017']})
 def test_37_rejection_does_not_increment_version(self):
  self.no('J2','TROCAR',descartar=[]);self.assertEqual(self.g.state['versao'],'E000');self.assertEqual(len(self.g.events),0)
 def test_38_checkpoint_roundtrip(self):
  self.creatures();snap=self.g.checkpoint();restored=MotorPOC.restore(snap,RECORDS)
  self.assertEqual(restored.state,self.g.state);self.assertEqual(restored.head_hash,self.g.head_hash)
 def test_39_tamper_state_detected(self):
  self.creatures();snap=self.g.checkpoint();snap['state']['placar']['J1']=2
  with self.assertRaises(CorruptedCheckpoint):MotorPOC.restore(snap,RECORDS)
 def test_40_tamper_event_detected(self):
  self.creatures();snap=self.g.checkpoint();snap['eventos'][0]['acao']='INVENTADO'
  with self.assertRaises(CorruptedCheckpoint):MotorPOC.restore(snap,RECORDS)
 def test_41_reject_unknown_command(self):self.no('J1','ROUBAR_CARTA',carta_id='CE-001')
 def test_42_reject_private_id_other_player(self):
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.no('J1','INVOCAR',carta_id='AB-POC-001')
 def test_43_prevent_more_than_five_draw(self):
  self.yes('J1','TROCAR',descartar=[]);self.assertEqual(len(self.g.hand(self.g.state,'J1')),5)
 def test_44_not_allow_different_player_resolve_fixture(self):
  self.support();self.no('J1','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
 def test_45_conservation_after_many_moves(self):
  self.battle();self.yes('ARBITRO','KO_COMBATE_FIXTURE',comprovante_fixture=True,vencedor='J1');self.yes('ARBITRO','ABRIR_CICLO');self.assertTrue(self.g.validate())
 def test_46_persist_priority_after_second_cycle(self):
  self.battle();self.yes('ARBITRO','KO_COMBATE_FIXTURE',comprovante_fixture=True,vencedor='J1');self.yes('ARBITRO','ABRIR_CICLO')
  self.assertEqual(self.g.state['prioridade_preparacao']['primeiro'],'J1')
 def test_47_ko_cannot_repeat_when_not_in_combat(self):
  self.battle();self.yes('ARBITRO','KO_COMBATE_FIXTURE',comprovante_fixture=True,vencedor='J1');self.no('ARBITRO','KO_COMBATE_FIXTURE',comprovante_fixture=True,vencedor='J1')
 def test_48_public_does_not_expose_draw_order(self):
  self.assertNotIn('monte_ordem_ids',str(self.g.public()));self.assertNotIn('CE-010',str(self.g.public()))
 def test_49_cards_without_pv_block_summon_only_when_needed(self):
  hands2={'J1':HANDS['J1'],'J2':['AB-POC-002','AB-POC-008','AB-POC-017','AB-POC-021','AB-POC-033']}
  self.g=MotorPOC(RECORDS,hands=hands2)
  self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
  self.yes('J1','INVOCAR',carta_id='CE-001');self.yes('J1','PRONTO_CRIATURA')
  x=self.no('J2','INVOCAR',carta_id='AB-POC-002');self.assertEqual(x['decisao'],'PENDENTE')
 def test_50_serialize_public_nonofficial_marked(self):
  self.assertEqual(self.g.public()['ambiente'],'FIXTURE_ISOLADA')

 def test_51_projection_matches_historical_schema(self):
  from jsonschema import Draft202012Validator
  schema=json.loads((pathlib.Path(__file__).resolve().parent/'SCHEMA_ESTADO_POC.json').read_text())
  Draft202012Validator(schema).validate(self.g.schema_projection())
  self.creatures();Draft202012Validator(schema).validate(self.g.schema_projection())
 def test_52_full_three_points_ends_without_next_draw(self):
  # Three fake combats, preserving surviving J1 and using existing J2 commons.
  other_cards=['AB-POC-001','AB-POC-008','AB-POC-017']
  for cycle in (1,2,3):
   self.yes('J1','TROCAR',descartar=[]);self.yes('J2','TROCAR',descartar=[])
   if cycle==1:self.yes('J1','INVOCAR',carta_id='CE-001')
   self.yes('J1','PRONTO_CRIATURA')
   self.yes('J2','INVOCAR',carta_id=other_cards[cycle-1]);self.yes('J2','PRONTO_CRIATURA')
   self.yes('J1','ESCOLHER_SUPORTE',carta_id=None);self.yes('J2','ESCOLHER_SUPORTE',carta_id=None)
   self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
   self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
   self.yes('ARBITRO','INICIATIVA_FIXTURE',comprovante_fixture=True,totais={'J1':11,'J2':8})
   self.yes('ARBITRO','KO_COMBATE_FIXTURE',comprovante_fixture=True,vencedor='J1')
   if cycle<3:self.yes('ARBITRO','ABRIR_CICLO')
  self.assertEqual(self.g.state['placar'],{'J1':3,'J2':0})
  self.assertEqual(self.g.state['situacao'],'ENCERRADA')
  self.assertEqual(self.g.state['controle_saque_ciclo']['ciclo_atual'],3)
  self.no('ARBITRO','ABRIR_CICLO')
  self.assertTrue(self.g.validate())
 def test_53_projection_private_exposure_only_full_fixture(self):
  pub=json.dumps(self.g.public(),ensure_ascii=False)
  self.assertNotIn('AB-POC-008',pub)
  projection=self.g.schema_projection()
  self.assertIn('AB-POC-008',str(projection)) # archival/admin state, not public
 def test_54_rejected_event_idempotent_without_multiple_rejections(self):
  first=self.g.apply('duplicate-illegal','J2','TROCAR',{'descartar':[]})
  again=self.g.apply('duplicate-illegal','J2','TROCAR',{'descartar':[]})
  self.assertEqual(first,again);self.assertEqual(len(self.g.rejections),1)
 def test_55_event_after_restore_continues_hash_chain(self):
  self.yes('J1','TROCAR',descartar=[])
  old_hash=self.g.head_hash
  cp=self.g.checkpoint();h=MotorPOC.restore(cp,RECORDS)
  r=h.apply('restored-next','J2','TROCAR',{'descartar':[]})
  self.assertEqual(r['decisao'],'ACEITA');self.assertEqual(h.events[-1]['encadeamento_anterior'],old_hash)

if __name__=='__main__':unittest.main(verbosity=2)
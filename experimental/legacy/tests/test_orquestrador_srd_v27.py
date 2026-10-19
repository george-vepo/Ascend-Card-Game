"""Adversarial API integration tests. All input decks/rolls are fake fixtures."""
import copy, json, pathlib, unittest
import jsonschema
from orquestrador_srd_v27 import OrquestradorSRD27 as O, PROFILES, SCHEMA
from motor_base_v22 import digest, InvalidAction, CorruptedCheckpoint

ROOT=pathlib.Path(__file__).parent
RECORDS=json.loads((ROOT/'STATUS_FICHAS_SUPORTES_80.json').read_text())['registros']
SCHEMA_STATE=json.loads((ROOT/'SCHEMA_ESTADO_POC.json').read_text())
HANDS = {
 'OWL_MOUTH_CONDITIONS':{
   'J1':['CE-001','CE-017','CE-019','CE-029','CE-035'],
   'J2':['AB-POC-008','AB-POC-001','AB-POC-017','AB-POC-021','AB-POC-033']},
 'DEVA_MOUTH_MAGIC':{
   'J1':['CE-001','CE-026','CE-017','CE-029','CE-035'],
   'J2':['AB-POC-008','AB-POC-001','AB-POC-017','AB-POC-021','AB-POC-033']},
 'DEVA_MOUTH_REACTION':{
   'J1':['CE-001','CE-026','CE-017','CE-029','CE-035'],
   'J2':['AB-POC-008','AB-POC-001','AB-POC-017','AB-POC-021','AB-POC-033']},
 'SOLAR_ABOLETH_LEGENDARY':{
   'J1':['CE-001','CE-026','CE-029','CE-035','CE-039'],
   'J2':['AB-POC-008','AB-POC-031','AB-POC-001','AB-POC-004','AB-POC-017']},
}

def make(profile):return O(RECORDS,profile,hands=HANDS[profile])

def setup(profile):
    m=make(profile);i=0
    def run(actor,command,params=None):
        nonlocal i;i+=1
        r=m.apply('SETUP-%02d'%i,actor,command,params or {})
        if r['decisao']!='ACEITA':raise AssertionError((profile,command,r))
        return r['resultado']
    for side in ('J1','J2'):run(side,'TROCAR',{'descartar':[]})
    run('J1','INVOCAR',{'carta_id':'CE-001'})
    if profile.startswith('DEVA'):
        run('J1','EVOLUIR',{'carta_id':'CE-026'})
    elif profile.startswith('SOLAR'):
        for cid in ('CE-026','CE-029','CE-035','CE-039'):run('J1','EVOLUIR',{'carta_id':cid})
    run('J1','PRONTO_CRIATURA')
    run('J2','INVOCAR',{'carta_id':'AB-POC-008'})
    if profile.startswith('SOLAR'):run('J2','EVOLUIR',{'carta_id':'AB-POC-031'})
    run('J2','PRONTO_CRIATURA')
    for side in ('J1','J2'):run(side,'ESCOLHER_SUPORTE',{'carta_id':None})
    for _ in range(2):run('ARBITRO','RESOLVER_SUPORTE_FIXTURE',{'resultado':'PULAR'})
    if profile=='OWL_MOUTH_CONDITIONS':
        run('ARBITRO','INICIATIVA_SRD_TESTE',{'d20':{'J1':17,'J2':8}})
    if profile.startswith('DEVA'):
        run('ARBITRO','INICIATIVA_DEVA_V25_TESTE',{'d20_simulados':{'J1':10,'J2':8}})
    if profile.startswith('SOLAR'):
        run('ARBITRO','INICIATIVA_LENDARIAS_V26_TESTE',{'d20_simulados':{'J1':10,'J2':10}})
    return m

class IntegrationV27(unittest.TestCase):
    def test_01_four_modes_explicit(self):self.assertEqual(len(PROFILES),4)
    def test_02_profile_invalid(self):
        with self.assertRaises(InvalidAction):O(RECORDS,'ANY')
    def test_03_cannot_use_official(self):
        with self.assertRaises(InvalidAction):O(RECORDS,'DEVA_MOUTH_MAGIC',test_fixture=False)
    def test_04_invalid_record_type(self):
        with self.assertRaises(InvalidAction):O({},'DEVA_MOUTH_MAGIC')
    def test_05_all_profiles_40_cards(self):
        for p in PROFILES:
            g=make(p)
            self.assertTrue(g.validate())
            for side in ('J1','J2'):self.assertEqual(len(g.state['jogadores'][side]['cartas']),40)
    def test_06_all_profiles_not_shuffled(self):
        for p in PROFILES:self.assertFalse(make(p).state['prioridade_preparacao']['sorteio_realizado'])
    def test_07_all_profiles_prepare(self):
        for p in PROFILES:
            g=setup(p)
            self.assertEqual(g.state['fase'],'COMBATE')
            self.assertTrue(g.validate())
    def test_08_pair_correct_all(self):
        for p,info in PROFILES.items():
            g=setup(p)
            self.assertEqual(tuple(g.state['jogadores'][j]['criatura_ativa_id'] for j in ('J1','J2')),info['pair'])
    def test_09_all_project_schema(self):
        for p in PROFILES:jsonschema.validate(setup(p)._motor.schema_projection(),SCHEMA_STATE)
    def test_10_all_checkpoints_restorable(self):
        for p in PROFILES:
            g=setup(p);h=O.restore_private(g.checkpoint_private(),RECORDS)
            self.assertEqual(h.perfil,p)
            self.assertEqual(digest(h.state),digest(g.state))
            self.assertEqual(h._motor.head_hash,g._motor.head_hash)
    def test_11_profile_tamper_rejected(self):
        g=make('DEVA_MOUTH_MAGIC');cp=g.checkpoint_private();cp['perfil']='SOLAR_ABOLETH_LEGENDARY'
        with self.assertRaises(CorruptedCheckpoint):O.restore_private(cp,RECORDS)
    def test_12_state_tamper_rejected(self):
        g=make('DEVA_MOUTH_MAGIC');cp=g.checkpoint_private();cp['checkpoint_modulo']['state']['placar']['J1']=3
        with self.assertRaises(CorruptedCheckpoint):O.restore_private(cp,RECORDS)
    def test_13_decks_tamper_rejected(self):
        g=make('DEVA_MOUTH_MAGIC');cp=g.checkpoint_private()
        other=copy.deepcopy(RECORDS);other[0]['nome']='INTRUSO'
        with self.assertRaises(CorruptedCheckpoint):O.restore_private(cp,other)
    def test_14_no_official_checkpoint(self):
        g=make('DEVA_MOUTH_MAGIC');cp=g.checkpoint_private();cp['unicamente_teste']=False
        with self.assertRaises(CorruptedCheckpoint):O.restore_private(cp,RECORDS)
    def test_15_wrong_event_collision(self):
        g=make('DEVA_MOUTH_MAGIC');a=g.apply('K','J1','TROCAR',{'descartar':[]});self.assertEqual(a['decisao'],'ACEITA')
        with self.assertRaises(InvalidAction):g.apply('K','J1','TROCAR',{'descartar':['CE-001']})
    def test_16_idempotency(self):
        g=make('DEVA_MOUTH_MAGIC');a=g.apply('K','J1','TROCAR',{'descartar':[]});b=g.apply('K','J1','TROCAR',{'descartar':[]})
        self.assertEqual(a,b);self.assertEqual(len(g.events),1)
    def test_17_unsupported_cross_action(self):
        g=setup('OWL_MOUTH_CONDITIONS');before=digest(g.state)
        out=g.apply('bad','J1','USAR_LENDARIA_V26_TESTE',{})
        self.assertEqual(out['decisao'],'REJEITADA');self.assertEqual(digest(g.state),before)
    def test_18_no_fixture_ko_shortcut(self):
        g=setup('SOLAR_ABOLETH_LEGENDARY');before=digest(g.state)
        out=g.apply('bad','ARBITRO','KO_COMBATE_FIXTURE',{'vencedor':'J1'})
        self.assertEqual(out['decisao'],'REJEITADA');self.assertEqual(digest(g.state),before)
    def test_19_unknown_spell_not_resolved(self):
        g=setup('DEVA_MOUTH_MAGIC');before=digest(g.state)
        out=g.apply('bad','J1','CONJURAR_METEOR_SWARM',{})
        self.assertEqual(out['decisao'],'REJEITADA');self.assertEqual(digest(g.state),before)
    def test_20_public_does_not_reveal_hands_or_deck(self):
        for p in PROFILES:
            g=setup(p);data=json.dumps(g.public_snapshot(),ensure_ascii=False)
            self.assertNotIn('monte_ordem_ids',data)
            self.assertNotIn('minha_mao',data)
            self.assertNotIn('copia_ids_deck',data)
            self.assertNotIn('suporte_reservado_id',data)
    def test_21_private_only_caller_hand(self):
        g=make('DEVA_MOUTH_MAGIC');x=g.private('J1')
        self.assertEqual(len(x['minha_mao']),5)
        self.assertNotIn('AB-POC-008',json.dumps(x))
    def test_22_private_invalid_side(self):
        with self.assertRaises(InvalidAction):make('DEVA_MOUTH_MAGIC').private('ARBITRO')
    def test_23_history_hides_setup(self):
        g=setup('SOLAR_ABOLETH_LEGENDARY');data=json.dumps(g.public_history())
        self.assertNotIn('TROCAR',data)
        self.assertNotIn('EVOLUIR',data)
        self.assertNotIn('ESCOLHER_SUPORTE',data)
        self.assertIn('INICIATIVA_LENDARIAS_V26_TESTE',data)
    def test_24_checkpoint_explicitly_sensitive(self):
        g=make('DEVA_MOUTH_MAGIC');cp=g.checkpoint_private();self.assertIn('monte_ordem_ids',json.dumps(cp))
    def test_25_public_spatial_scope_warning(self):
        g=make('DEVA_MOUTH_REACTION');self.assertIn('INCOMPATIVEL',g.public()['escopo_espacial'])
    def test_26_public_nonspatial_scope(self):
        g=make('DEVA_MOUTH_MAGIC');self.assertNotIn('INCOMPATIVEL',g.public()['escopo_espacial'])
    def test_27_deva_magic_and_reaction_present(self):
        g=setup('DEVA_MOUTH_REACTION')
        self.assertIn('v26',g.state['combate']);self.assertIn('v25',g.state['combate'])
        self.assertEqual(g.state['combate']['rodada'],1)
    def test_28_legendary_window_works(self):
        from motor_lendarias_srd import SCOPE
        g=setup('SOLAR_ABOLETH_LEGENDARY')
        x=g.apply('BEGIN','J1','INICIAR_TURNO_V26_TESTE',{'aceite_escopo':SCOPE})
        self.assertEqual(x['decisao'],'ACEITA')
        y=g.apply('END','J1','ENCERRAR_TURNO_V26_TESTE',{'aceite_escopo':SCOPE,'efeitos_de_turno_verificados':True})
        self.assertEqual(y['decisao'],'ACEITA')
        self.assertEqual(g.public()['janela_lendaria']['dono'],'J2')
    def test_29_reaction_position_requires_confirmation(self):
        from motor_magias_srd import SCOPE
        g=setup('DEVA_MOUTH_REACTION');before=digest(g.state)
        r=g.apply('nopos','J1','INICIO_TURNO_DEVA_V25_TESTE',{'aceite_escopo':SCOPE})
        self.assertEqual(r['decisao'],'PENDENTE');self.assertEqual(digest(g.state),before)
    def test_30_invalid_command_type(self):
        with self.assertRaises(InvalidAction):make('DEVA_MOUTH_MAGIC').apply('BAD','J1',None)
    def test_31_no_random_dice(self):
        for p in PROFILES:
            self.assertEqual(setup(p).state['combate']['iniciativas']['origem'],'DADOS_SIMULADOS_TESTE')
    def test_32_rejections_are_not_accepted_events(self):
        g=setup('DEVA_MOUTH_MAGIC');n=len(g.events)
        g.apply('R','J2','MULTIATTACK_HOLY_MACE_V25_TESTE',{})
        self.assertEqual(len(g.events),n);self.assertEqual(len(g._motor.rejections),1)
    def test_33_restore_reject_different_module(self):
        g=setup('DEVA_MOUTH_MAGIC');cp=g.checkpoint_private()
        cp['checkpoint_modulo']['schema']='POC_MOTOR_LENDARIAS_V2_6_TESTE'
        cp['integridade_sha256']=digest({k:v for k,v in cp.items() if k!='integridade_sha256'})
        with self.assertRaises(CorruptedCheckpoint):O.restore_private(cp,RECORDS)
    def test_34_event_integrity_after_restore(self):
        g=setup('OWL_MOUTH_CONDITIONS');h=O.restore_private(g.checkpoint_private(),RECORDS)
        r=h.apply('POST','J1','USAR_LENDARIA_V26_TESTE',{})
        self.assertEqual(r['decisao'],'REJEITADA')
        self.assertEqual(h._motor.head_hash,g._motor.head_hash)

if __name__=='__main__':unittest.main(verbosity=2)
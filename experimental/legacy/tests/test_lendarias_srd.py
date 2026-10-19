"""Tests for the v2.6 isolated Solar / Aboleth SRD legendary-action slice."""
from __future__ import annotations
import copy, json, pathlib, unittest
from motor_lendarias_srd import MotorLendariasSRD, SOLAR, ABOLETH, SCOPE
from motor_poc import digest

ROOT=pathlib.Path(__file__).parent
SOURCE=ROOT/'STATUS_FICHAS_SUPORTES_80.json'
RECORDS=json.loads(SOURCE.read_text(encoding='utf-8'))['registros']
HANDS={
    'J1':['CE-001','CE-026','CE-029','CE-035','CE-039'],
    'J2':['AB-POC-008','AB-POC-031','AB-POC-001','AB-POC-004','AB-POC-017']
}

def fixture():
    m=MotorLendariasSRD(RECORDS,first='J1',hands=HANDS)
    num=0
    def run(who,cmd,p=None):
        nonlocal num
        num+=1
        result=m.apply(f'V26-{num:04d}',who,cmd,p or {})
        assert result['decisao']=='ACEITA',(cmd,result)
        return result
    run('J1','TROCAR',{'descartar':[]});run('J2','TROCAR',{'descartar':[]})
    run('J1','INVOCAR',{'carta_id':'CE-001'})
    for card in ['CE-026','CE-029','CE-035','CE-039']:
        run('J1','EVOLUIR',{'carta_id':card})
    run('J1','PRONTO_CRIATURA')
    run('J2','INVOCAR',{'carta_id':'AB-POC-008'})
    run('J2','EVOLUIR',{'carta_id':'AB-POC-031'})
    run('J2','PRONTO_CRIATURA')
    run('J1','ESCOLHER_SUPORTE',{'carta_id':None})
    run('J2','ESCOLHER_SUPORTE',{'carta_id':None})
    run('ARBITRO','RESOLVER_SUPORTE_FIXTURE',{'resultado':'PULAR'})
    run('ARBITRO','RESOLVER_SUPORTE_FIXTURE',{'resultado':'PULAR'})
    run('ARBITRO','INICIATIVA_LENDARIAS_V26_TESTE',{'d20_simulados':{'J1':10,'J2':10}})
    return m

def act(m,who,cmd,p=None):
    idx=len(m.events)+len(m.rejections)+1
    return m.apply(f'T-{idx:04d}',who,cmd,p or {})

def accepted(m,who,cmd,p=None):
    r=act(m,who,cmd,p)
    if r['decisao']!='ACEITA':raise AssertionError((cmd,r))
    return r['resultado']

def start(m,who):return accepted(m,who,'INICIAR_TURNO_V26_TESTE',{'aceite_escopo':SCOPE})
def end(m,who):return accepted(m,who,'ENCERRAR_TURNO_V26_TESTE',{'aceite_escopo':SCOPE,'efeitos_de_turno_verificados':True})
def to_aboleth_lash(m):start(m,'J1');end(m,'J1')
def to_solar_gaze(m):to_aboleth_lash(m);start(m,'J2');end(m,'J2')
def gaze(m,roll=5,use=False):
    return accepted(m,'J1','USAR_LENDARIA_V26_TESTE',{'aceite_escopo':SCOPE,
        'habilidade':'Blinding Gaze','alvo_visivel_fixture':True,
        'constituicao_d20_simulado':roll,'aboleth_gasta_resistencia_lendaria':use})
def lash(m,rolls=[17],dice=[4,3]):
    return accepted(m,'J2','USAR_LENDARIA_V26_TESTE',{'aceite_escopo':SCOPE,
        'habilidade':'Lash','alvo_valido_fixture':True,
        'ataque_d20_simulados':rolls,'dano_d6_simulados':dice})

class TestV26(unittest.TestCase):
    def setUp(self):self.m=fixture()
    def test_01_fixture_pair(self):
        self.assertEqual(self.m.state['jogadores']['J1']['criatura_ativa_id'],SOLAR)
        self.assertEqual(self.m.state['jogadores']['J2']['criatura_ativa_id'],ABOLETH)
    def test_02_40_copies_each(self):self.assertTrue(self.m.validate())
    def test_03_no_official_shuffling(self):self.assertFalse(self.m.state['prioridade_preparacao']['sorteio_realizado'])
    def test_04_initiative_simulated(self):self.assertEqual(self.m.state['combate']['iniciativas']['origem'],'DADOS_SIMULADOS_TESTE')
    def test_05_initial_resources(self):
        a,b=self.m._pair(self.m.state)
        self.assertEqual(a['recursos']['acoes_lendarias_restantes'],3)
        self.assertEqual(b['recursos']['resistencia_lendaria_restante'],3)
    def test_06_legendary_before_end_rejected(self):
        self.assertEqual(act(self.m,'J2','USAR_LENDARIA_V26_TESTE',{'aceite_escopo':SCOPE})['decisao'],'REJEITADA')
    def test_07_start_turn(self):self.assertEqual(start(self.m,'J1')['turno'],'J1')
    def test_08_start_twice_rejected(self):
        start(self.m,'J1')
        self.assertEqual(act(self.m,'J1','INICIAR_TURNO_V26_TESTE',{'aceite_escopo':SCOPE})['decisao'],'REJEITADA')
    def test_09_end_before_start_rejected(self):
        self.assertEqual(act(self.m,'J1','ENCERRAR_TURNO_V26_TESTE',{'aceite_escopo':SCOPE,'efeitos_de_turno_verificados':True})['decisao'],'REJEITADA')
    def test_10_end_requires_scope(self):
        start(self.m,'J1')
        self.assertEqual(act(self.m,'J1','ENCERRAR_TURNO_V26_TESTE',{})['decisao'],'PENDENTE')
    def test_11_end_requires_effects_verified(self):
        start(self.m,'J1')
        self.assertEqual(act(self.m,'J1','ENCERRAR_TURNO_V26_TESTE',{'aceite_escopo':SCOPE})['decisao'],'PENDENTE')
    def test_12_lash_hit_and_grapple(self):
        to_aboleth_lash(self.m);r=lash(self.m)
        self.assertTrue(r['acerto']);self.assertEqual(r['dano'],12)
        self.assertEqual(self.m.get_card(self.m.state,'J1',SOLAR)['pv_atual'],285)
        self.assertIn('Grappled',self.m.get_card(self.m.state,'J1',SOLAR)['condicoes'])
    def test_13_lash_miss(self):
        to_aboleth_lash(self.m);r=lash(self.m,[6],[])
        self.assertFalse(r['acerto']);self.assertEqual(r['dano'],0)
    def test_14_natural_one_misses(self):
        to_aboleth_lash(self.m);self.assertFalse(lash(self.m,[1],[])['acerto'])
    def test_15_critical_four_dice(self):
        to_aboleth_lash(self.m);r=lash(self.m,[20],[1,2,3,4]);self.assertTrue(r['critico']);self.assertEqual(r['dano'],15)
    def test_16_duplicate_legendary_same_window_rejected(self):
        to_aboleth_lash(self.m);lash(self.m)
        self.assertEqual(act(self.m,'J2','USAR_LENDARIA_V26_TESTE',{'aceite_escopo':SCOPE})['decisao'],'REJEITADA')
    def test_17_window_closes_on_next_turn_start(self):
        to_aboleth_lash(self.m);start(self.m,'J2')
        self.assertEqual(act(self.m,'J2','USAR_LENDARIA_V26_TESTE',{'aceite_escopo':SCOPE})['decisao'],'REJEITADA')
    def test_18_reactions_not_fabricated(self):
        to_aboleth_lash(self.m)
        r=act(self.m,'J2','REAÇÃO_V26_TESTE')
        self.assertEqual(r['decisao'],'REJEITADA')
    def test_19_gaze_failed_save_blinded(self):
        to_solar_gaze(self.m);r=gaze(self.m)
        self.assertTrue(r['Blinded_aplicado']);self.assertIn('Blinded',self.m.get_card(self.m.state,'J2',ABOLETH)['condicoes'])
    def test_20_gaze_success_not_blinded(self):
        to_solar_gaze(self.m);r=gaze(self.m,20,False)
        self.assertFalse(r['Blinded_aplicado'])
    def test_21_gaze_resistance_consumed(self):
        to_solar_gaze(self.m);r=gaze(self.m,5,True)
        self.assertEqual(r['restantes_resistencia_aboleth'],2)
        self.assertNotIn('Blinded',self.m.get_card(self.m.state,'J2',ABOLETH)['condicoes'])
    def test_22_resistance_not_on_success(self):
        to_solar_gaze(self.m)
        p={'aceite_escopo':SCOPE,'habilidade':'Blinding Gaze','alvo_visivel_fixture':True,
            'constituicao_d20_simulado':20,'aboleth_gasta_resistencia_lendaria':True}
        self.assertEqual(act(self.m,'J1','USAR_LENDARIA_V26_TESTE',p)['decisao'],'REJEITADA')
    def test_23_resistance_decision_required(self):
        to_solar_gaze(self.m)
        p={'aceite_escopo':SCOPE,'habilidade':'Blinding Gaze','alvo_visivel_fixture':True,'constituicao_d20_simulado':5}
        self.assertEqual(act(self.m,'J1','USAR_LENDARIA_V26_TESTE',p)['decisao'],'PENDENTE')
    def test_24_visibility_required(self):
        to_solar_gaze(self.m)
        p={'aceite_escopo':SCOPE,'habilidade':'Blinding Gaze','constituicao_d20_simulado':5,'aboleth_gasta_resistencia_lendaria':False}
        self.assertEqual(act(self.m,'J1','USAR_LENDARIA_V26_TESTE',p)['decisao'],'PENDENTE')
    def test_25_invalid_roll_rejected(self):
        to_solar_gaze(self.m)
        p={'aceite_escopo':SCOPE,'habilidade':'Blinding Gaze','alvo_visivel_fixture':True,
            'constituicao_d20_simulado':21,'aboleth_gasta_resistencia_lendaria':False}
        self.assertEqual(act(self.m,'J1','USAR_LENDARIA_V26_TESTE',p)['decisao'],'REJEITADA')
    def test_26_gaze_cooldown_reset_on_owner_start(self):
        to_solar_gaze(self.m);gaze(self.m)
        self.assertTrue(self.m.get_card(self.m.state,'J1',SOLAR)['recursos']['blinding_gaze_ja_usado_desde_ultimo_turno'])
        start(self.m,'J1')
        self.assertFalse(self.m.get_card(self.m.state,'J1',SOLAR)['recursos']['blinding_gaze_ja_usado_desde_ultimo_turno'])
    def test_27_lash_disadvantage_if_blinded(self):
        to_solar_gaze(self.m);gaze(self.m)
        start(self.m,'J1');end(self.m,'J1')
        r=lash(self.m,[18,4],[])
        self.assertEqual(r['modo'],'DESVANTAGEM');self.assertEqual(r['d20_aplicado'],4)
    def test_28_lash_must_roll_twice_blinded(self):
        to_solar_gaze(self.m);gaze(self.m)
        start(self.m,'J1');end(self.m,'J1')
        p={'aceite_escopo':SCOPE,'habilidade':'Lash','alvo_valido_fixture':True,
            'ataque_d20_simulados':[18],'dano_d6_simulados':[]}
        self.assertEqual(act(self.m,'J2','USAR_LENDARIA_V26_TESTE',p)['decisao'],'REJEITADA')
    def test_29_legendary_uses_refill_on_own_start(self):
        to_aboleth_lash(self.m);lash(self.m)
        self.assertEqual(self.m.get_card(self.m.state,'J2',ABOLETH)['recursos']['acoes_lendarias_restantes'],2)
        start(self.m,'J2')
        self.assertEqual(self.m.get_card(self.m.state,'J2',ABOLETH)['recursos']['acoes_lendarias_restantes'],3)
    def test_30_time_does_not_expire_by_guess(self):
        to_solar_gaze(self.m);gaze(self.m)
        self.assertEqual(act(self.m,'ARBITRO','FINALIZAR_CEGUEIRA_V26_TESTE',{})['decisao'],'PENDENTE')
        self.assertIn('Blinded',self.m.get_card(self.m.state,'J2',ABOLETH)['condicoes'])
    def test_31_explicit_minute_expiration(self):
        to_solar_gaze(self.m);gaze(self.m)
        accepted(self.m,'ARBITRO','FINALIZAR_CEGUEIRA_V26_TESTE',{'duracao_comprovada':'1 minuto transcorrido'})
        self.assertNotIn('Blinded',self.m.get_card(self.m.state,'J2',ABOLETH)['condicoes'])
    def test_32_no_arbitrary_resets_on_new_turn(self):
        to_solar_gaze(self.m);gaze(self.m,5,True)
        start(self.m,'J1')
        self.assertEqual(self.m.get_card(self.m.state,'J2',ABOLETH)['recursos']['resistencia_lendaria_restante'],2)
    def test_33_hidden_hand_not_on_public(self):
        self.assertNotIn('minha_mao',self.m.public())
        self.assertNotIn('monte_ordem_ids',str(self.m.public()))
    def test_34_checkpoints_restore(self):
        to_solar_gaze(self.m);gaze(self.m)
        cp=self.m.checkpoint()
        m2=MotorLendariasSRD.restore(cp,RECORDS)
        self.assertEqual(digest(m2.state),digest(self.m.state))
    def test_35_rejections_do_not_modify_state(self):
        to_aboleth_lash(self.m);hash_before=digest(self.m.state)
        r=act(self.m,'J1','USAR_LENDARIA_V26_TESTE',{})
        self.assertEqual(r['decisao'],'REJEITADA')
        self.assertEqual(hash_before,digest(self.m.state))
    def test_36_unimplemented_legendary_pending(self):
        to_solar_gaze(self.m)
        r=act(self.m,'J1','USAR_LENDARIA_V26_TESTE',{'aceite_escopo':SCOPE,'habilidade':'Radiant Teleport'})
        self.assertEqual(r['decisao'],'PENDENTE')
    def test_37_idempotent_event(self):
        before=len(self.m.events)
        p={'aceite_escopo':SCOPE}
        one=self.m.apply('TEST-IDEMP','J1','INICIAR_TURNO_V26_TESTE',p)
        two=self.m.apply('TEST-IDEMP','J1','INICIAR_TURNO_V26_TESTE',p)
        self.assertEqual(one,two);self.assertEqual(len(self.m.events),before+1)
    def test_38_other_cannot_start_out_of_turn(self):
        self.assertEqual(act(self.m,'J2','INICIAR_TURNO_V26_TESTE',{'aceite_escopo':SCOPE})['decisao'],'REJEITADA')
    def test_39_no_draws_during_turn(self):
        before={p:len(self.m.state['jogadores'][p]['monte_ordem_ids']) for p in ('J1','J2')}
        to_aboleth_lash(self.m);lash(self.m)
        self.assertEqual(before,{p:len(self.m.state['jogadores'][p]['monte_ordem_ids']) for p in ('J1','J2')})
    def test_40_source_stats(self):
        a,b=self.m._pair(self.m.state)
        self.assertEqual([a['pv_atual'],b['pv_atual']],[297,150])

if __name__=='__main__':unittest.main(verbosity=2)
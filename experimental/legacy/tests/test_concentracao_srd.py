"""Adversarial SRD 5.2.1 concentration fixture tests; zero official state."""
import copy, json, pathlib, unittest
from motor_concentracao_srd import MotorConcentracaoSRD, SCOPE_CONCENTRACAO, SPELL, DEVA, MOUTH
from motor_magias_srd import SCOPE
from motor_reacoes_srd import SCOPE_REACOES
from motor_base_v22 import CorruptedCheckpoint

ROOT = pathlib.Path(__file__).resolve().parent
RECORDS = json.loads((ROOT/'STATUS_FICHAS_SUPORTES_80.json').read_text(encoding='utf-8'))['registros']
HANDS = {'J1': ['CE-001', 'CE-026', 'CE-017', 'CE-029', 'CE-035'],
         'J2': ['AB-POC-008', 'AB-POC-001', 'AB-POC-017', 'AB-POC-021', 'AB-POC-033']}

class TestConcentracaoSRD(unittest.TestCase):
    def setUp(self):
        self.g = MotorConcentracaoSRD(RECORDS, hands=HANDS)
        self.n = 0
    def apply(self, actor, command, **params):
        self.n += 1
        return self.g.apply(f'v27-{self.n:05d}', actor, command, params)
    def yes(self, actor, command, **params):
        r = self.apply(actor, command, **params)
        self.assertEqual(r['decisao'], 'ACEITA', r)
        return r['resultado']
    def no(self, actor, command, **params):
        state = copy.deepcopy(self.g.state); head = self.g.head_hash
        r = self.apply(actor, command, **params)
        self.assertIn(r['decisao'], ('PENDENTE','REJEITADA'), r)
        self.assertEqual(self.g.state, state)
        self.assertEqual(self.g.head_hash, head)
        return r
    def setup_combat(self, j1_first=True, configure=True):
        for actor in ('J1','J2'): self.yes(actor, 'TROCAR', descartar=[])
        self.yes('J1','INVOCAR',carta_id='CE-001')
        self.yes('J1','EVOLUIR',carta_id=DEVA)
        self.yes('J1','PRONTO_CRIATURA')
        self.yes('J2','INVOCAR',carta_id=MOUTH)
        self.yes('J2','PRONTO_CRIATURA')
        for actor in ('J1','J2'): self.yes(actor,'ESCOLHER_SUPORTE',carta_id=None)
        for _ in range(2): self.yes('ARBITRO','RESOLVER_SUPORTE_FIXTURE',resultado='PULAR')
        self.yes('ARBITRO','INICIATIVA_DEVA_V25_TESTE',d20_simulados={'J1':17,'J2':10} if j1_first else {'J1':1,'J2':20})
        if configure:
            self.yes('ARBITRO','CONFIGURAR_DISTANCIA_V26_FIXTURE',aceite_escopo=SCOPE_REACOES,
                     distancia_ft=5,origem='POSICIONAMENTO_ARTIFICIAL_EXPLICITO_DE_TESTE')
    def start(self, actor):
        params = {'aceite_escopo': SCOPE}
        if actor=='J1': params.update(gibbering_aplicavel_fixture=True,sab_d20_simulado=1)
        return self.yes(actor,'INICIO_TURNO_DEVA_V25_TESTE',**params)
    def cast(self, **kwargs):
        p = {'aceite_escopo':SCOPE_CONCENTRACAO,'magia':SPELL,'barreira_bloqueante_confirmada':False}
        p.update(kwargs)
        return self.yes('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',**p)
    def cast_ready(self):
        self.setup_combat();self.start('J1');return self.cast()
    def end(self, actor):return self.yes(actor,'ENCERRAR_TURNO_DEVA_V25_TESTE')
    def next_deva_turn(self):
        self.end('J1');self.start('J2');self.end('J2');return self.start('J1')
    def damage(self, damage=8, roll=15, **kw):
        p={'aceite_escopo':SCOPE_CONCENTRACAO,'origem':'DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',
           'tipo_dano':'CONTUNDENTE','resistencia_aplicavel':False,'dano_efetivo':damage}
        if roll is not None: p['constituicao_d20_simulado']=roll
        p.update(kw)
        return self.yes('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',**p)
    def v(self):return self.g.state['combate']['v27']
    def active(self):return self.v()['concentracao']

    def test_01_initial_state(self):
        self.setup_combat();self.assertIsNone(self.active());self.assertEqual(self.v()['conjuracoes'],0)
    def test_02_cannot_cast_precombat(self):
        self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia=SPELL,barreira_bloqueante_confirmada=False)
    def test_03_cast_requires_own_turn(self):
        self.setup_combat(j1_first=False);self.start('J2');self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia=SPELL,barreira_bloqueante_confirmada=False)
    def test_04_cast_requires_started_turn(self):
        self.setup_combat();self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia=SPELL,barreira_bloqueante_confirmada=False)
    def test_05_cast_success(self):
        r=self.cast_ready();self.assertTrue(r['concentracao_ativa']);self.assertEqual(self.active()['magia'],SPELL)
    def test_06_action_consumed(self):
        self.cast_ready();self.assertTrue(self.g.state['combate']['v25']['acao_utilizada'])
    def test_07_senses_aberration_within_range(self):
        r=self.cast_ready();self.assertEqual(r['deteccao']['alvo_id'],MOUTH);self.assertEqual(r['deteccao']['distancia_ft'],5)
    def test_08_reject_barrier_unconfirmed(self):
        self.setup_combat();self.start('J1');self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia=SPELL)
    def test_09_reject_blocking_barrier(self):
        self.setup_combat();self.start('J1');self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia=SPELL,barreira_bloqueante_confirmada=True)
    def test_10_reject_unknown_spell(self):
        self.setup_combat();self.start('J1');self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia='Bless',barreira_bloqueante_confirmada=False)
    def test_11_no_cast_without_position(self):
        self.setup_combat(configure=False);self.no('J1','INICIO_TURNO_DEVA_V25_TESTE',aceite_escopo=SCOPE,gibbering_aplicavel_fixture=True,sab_d20_simulado=1)
    def test_12_no_double_action_cast(self):
        self.cast_ready();self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia=SPELL,barreira_bloqueante_confirmada=False)
    def test_13_no_multiattack_after_cast(self):
        self.cast_ready();self.no('J1','MULTIATTACK_HOLY_MACE_V25_TESTE',aceite_escopo=SCOPE,ataques=[{'d20_simulado':1},{'d20_simulado':1}])
    def test_14_bonus_cure_does_not_break(self):
        self.cast_ready();self.yes('J1','DIVINE_AID_CURE_WOUNDS_V25_TESTE',aceite_escopo=SCOPE,magia='Cure Wounds',alvo=DEVA,d8_simulados=[1,1]);self.assertIsNotNone(self.active())
    def test_15_bonus_resource_unchanged_by_cast(self):
        self.cast_ready();self.assertEqual(self.g.get_card(self.g.state,'J1',DEVA)['recursos']['divine_aid_restante'],2)
    def test_16_damage_dc_floor_10(self):
        self.cast_ready();r=self.damage(8,6);self.assertEqual(r['concentracao_teste']['cd'],10);self.assertTrue(r['concentracao_teste']['sucesso'])
    def test_17_damage_dc_half_floor(self):
        self.cast_ready();r=self.damage(25,10);self.assertEqual(r['concentracao_teste']['cd'],12)
    def test_18_damage_dc_cap_30(self):
        self.cast_ready();r=self.damage(70,20);self.assertEqual(r['concentracao_teste']['cd'],30);self.assertFalse(r['concentracao_teste']['sucesso'])
    def test_19_damage_fail_breaks(self):
        self.cast_ready();r=self.damage(8,5);self.assertIsNone(self.active());self.assertEqual(r['encerramento']['motivo'],'FALHA_SALVAGUARDA_CONSTITUICAO')
    def test_20_damage_success_keeps(self):
        self.cast_ready();self.damage(8,6);self.assertIsNotNone(self.active())
    def test_21_nat20_not_auto_success_save(self):
        self.cast_ready();r=self.damage(60,20);self.assertFalse(r['concentracao_teste']['sucesso'])
    def test_22_reject_missing_save(self):
        self.cast_ready();self.no('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',aceite_escopo=SCOPE_CONCENTRACAO,origem='DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',tipo_dano='CONTUNDENTE',resistencia_aplicavel=False,dano_efetivo=8)
    def test_23_reject_invalid_bool_roll(self):
        self.cast_ready();self.no('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',aceite_escopo=SCOPE_CONCENTRACAO,origem='DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',tipo_dano='CONTUNDENTE',resistencia_aplicavel=False,dano_efetivo=8,constituicao_d20_simulado=True)
    def test_24_reject_zero_damage(self):
        self.cast_ready();self.no('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',aceite_escopo=SCOPE_CONCENTRACAO,origem='DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',tipo_dano='CONTUNDENTE',resistencia_aplicavel=False,dano_efetivo=0,constituicao_d20_simulado=12)
    def test_25_reject_lethal_damage(self):
        self.cast_ready();self.no('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',aceite_escopo=SCOPE_CONCENTRACAO,origem='DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',tipo_dano='CONTUNDENTE',resistencia_aplicavel=False,dano_efetivo=229,constituicao_d20_simulado=12)
    def test_26_reject_unsupported_damage_type(self):
        self.cast_ready();self.no('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',aceite_escopo=SCOPE_CONCENTRACAO,origem='DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',tipo_dano='RADIANTE',resistencia_aplicavel=False,dano_efetivo=8,constituicao_d20_simulado=12)
    def test_27_damage_without_concentration_no_roll(self):
        self.setup_combat();self.start('J1');r=self.damage(8,None);self.assertIsNone(r['concentracao_teste'])
    def test_28_no_save_if_no_concentration(self):
        self.setup_combat();self.start('J1');self.no('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',aceite_escopo=SCOPE_CONCENTRACAO,origem='DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',tipo_dano='CONTUNDENTE',resistencia_aplicavel=False,dano_efetivo=8,constituicao_d20_simulado=12)
    def test_29_voluntary_end(self):
        self.cast_ready();r=self.yes('J1','ENCERRAR_CONCENTRACAO_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO);self.assertEqual(r['custo_acao'],'NENHUM');self.assertIsNone(self.active())
    def test_30_voluntary_end_other_turn(self):
        self.cast_ready();self.end('J1');self.start('J2');self.yes('J1','ENCERRAR_CONCENTRACAO_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO)
    def test_31_cannot_end_twice(self):
        self.cast_ready();self.yes('J1','ENCERRAR_CONCENTRACAO_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO);self.no('J1','ENCERRAR_CONCENTRACAO_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO)
    def test_32_wrong_actor_cannot_end(self):
        self.cast_ready();self.no('J2','ENCERRAR_CONCENTRACAO_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO)
    def test_33_recast_replaces(self):
        self.cast_ready();self.next_deva_turn();r=self.cast();self.assertEqual(r['substituicao']['motivo'],'SUBSTITUIDA_POR_NOVA_CONJURACAO');self.assertEqual(self.v()['finalizacoes'],1)
    def test_34_recast_resets_duration(self):
        self.cast_ready();self.next_deva_turn();self.cast();self.assertEqual(self.active()['rodadas_decorridas'],0)
    def test_35_one_round_progression(self):
        self.cast_ready();self.next_deva_turn();self.assertEqual(self.active()['rodadas_decorridas'],1)
    def test_36_no_round_tick_on_j2_start(self):
        self.cast_ready();self.end('J1');self.start('J2');self.assertEqual(self.active()['rodadas_decorridas'],0)
    def test_37_checkpoint_roundtrip(self):
        self.cast_ready();self.damage(8,12);cp=self.g.checkpoint();r=MotorConcentracaoSRD.restore(cp,RECORDS);self.assertEqual(r.state,self.g.state);self.assertEqual(r.head_hash,self.g.head_hash)
    def test_38_checkpoint_tamper_detected(self):
        self.cast_ready();cp=self.g.checkpoint();cp['state']['combate']['v27']['concentracao']['rodadas_decorridas']=99
        with self.assertRaises(CorruptedCheckpoint):MotorConcentracaoSRD.restore(cp,RECORDS)
    def test_39_public_no_hidden_hands(self):
        self.cast_ready();view=json.dumps(self.g.public());self.assertNotIn('CE-017',view);self.assertNotIn('AB-POC-017',view)
    def test_40_40_cards_preserved(self):
        self.cast_ready();self.damage(8,12);self.assertTrue(self.g.validate());self.assertEqual(len(self.g.state['jogadores']['J1']['cartas']),40)
    def test_41_no_official_shuffle(self):
        self.cast_ready();self.assertFalse(self.g.state['prioridade_preparacao']['sorteio_realizado'])
    def test_42_voluntary_during_reaction_pending(self):
        self.cast_ready();self.end('J1');self.start('J2')
        self.yes('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='DESLOCAMENTO',visivel_ao_deva=True,destino_ft=10)
        self.yes('J1','ENCERRAR_CONCENTRACAO_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO)
        self.assertIsNotNone(self.g.state['combate']['v26']['pendencia_reacao'])
    def test_43_damage_blocked_during_pending_reaction(self):
        self.cast_ready();self.end('J1');self.start('J2')
        self.yes('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='DESLOCAMENTO',visivel_ao_deva=True,destino_ft=10)
        self.no('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',aceite_escopo=SCOPE_CONCENTRACAO,origem='DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',tipo_dano='CONTUNDENTE',resistencia_aplicavel=False,dano_efetivo=8,constituicao_d20_simulado=12)
    def test_44_invalid_extra_damage_fields(self):
        self.cast_ready();self.no('ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',aceite_escopo=SCOPE_CONCENTRACAO,origem='DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',tipo_dano='CONTUNDENTE',resistencia_aplicavel=False,dano_efetivo=8,constituicao_d20_simulado=12,ataque='fake')
    def test_45_expire_after_100_rounds(self):
        self.cast_ready()
        for n in range(99):self.next_deva_turn()
        self.assertEqual(self.active()['rodadas_decorridas'],99)
        r=self.next_deva_turn();self.assertIsNone(self.active());self.assertEqual(r['encerramento_concentracao']['motivo'],'DURACAO_MAXIMA_10_MINUTOS')
    def test_46_can_cast_after_expiry(self):
        self.cast_ready()
        for _ in range(100):self.next_deva_turn()
        self.cast();self.assertIsNotNone(self.active());self.assertEqual(self.v()['conjuracoes'],2)
    def test_47_no_concentration_on_shapechange_fixture(self):
        self.cast_ready();self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia='Shapechange',barreira_bloqueante_confirmada=False)
    def test_48_idempotence(self):
        self.cast_ready();p={'aceite_escopo':SCOPE_CONCENTRACAO,'origem':'DANO_EXTERNO_JA_RESOLVIDO_FIXTURE',
                               'tipo_dano':'CONTUNDENTE','resistencia_aplicavel':False,'dano_efetivo':8,'constituicao_d20_simulado':12}
        a=self.g.apply('v27-idem','ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',p)
        b=self.g.apply('v27-idem','ARBITRO','DANO_EXTERNO_DEVA_V27_FIXTURE',p)
        self.assertEqual(a,b);self.assertEqual(self.g.get_card(self.g.state,'J1',DEVA)['pv_atual'],221)
    def test_49_concentration_can_survive_reaction(self):
        self.cast_ready();self.end('J1');self.start('J2')
        self.yes('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,tipo='DESLOCAMENTO',visivel_ao_deva=True,destino_ft=10)
        self.yes('J1','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES)
        self.assertIsNotNone(self.active())
    def test_50_failed_command_no_mutation(self):
        self.cast_ready();self.no('J1','CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO,magia=SPELL,barreira_bloqueante_confirmada=False)

# Additional post-combat invariants: concentration is NOT broken by combat end.
class TestConcentracaoPosCombate(unittest.TestCase):
    def setUp(self):
        self.t=TestConcentracaoSRD(methodName='test_05_cast_success')
        self.t.setUp();self.t.cast_ready();self.t.end('J1');self.t.start('J2')
        self.t.yes('J2','MOVIMENTO_MOUTH_V26_TESTE',aceite_escopo=SCOPE_REACOES,
                   tipo='DESLOCAMENTO',visivel_ao_deva=True,destino_ft=10)
        self.t.yes('J1','REAGIR_OPORTUNIDADE_DEVA_V26_TESTE',aceite_escopo=SCOPE_REACOES,
                   ataque={'d20_simulado':20,'d6_contundente':[6,6],'d8_radiante':[8]*8})
    def test_51_concentration_persists_after_ko(self):
        self.assertEqual(self.t.g.state['fase'],'POS_COMBATE')
        self.assertIsNotNone(self.t.active())
        self.assertTrue(self.t.g.validate())
    def test_52_can_end_after_combat(self):
        self.t.yes('J1','ENCERRAR_CONCENTRACAO_DEVA_V27_TESTE',aceite_escopo=SCOPE_CONCENTRACAO)
        self.assertIsNone(self.t.active())

if __name__=='__main__':unittest.main(verbosity=2)
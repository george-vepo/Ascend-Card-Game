"""SRD Card Game v2.6: one isolated SRD 5.2.1 opportunity-attack fixture.

This is NOT an official match, a spatial combat engine or a support-card ability.
The arbiter must explicitly confirm initial distance; only 5ft <-> 10ft
movement by the Gibbering Mouther is modeled. Deva may react with exactly
one Holy Mace melee attack, not Multiattack. Dice are externally supplied.
"""
from __future__ import annotations
import copy
from motor_magias_srd import MotorMagiasSRD, DEVA, MOUTH, SOURCES
from motor_base_v22 import InvalidAction, UnresolvedRule, CorruptedCheckpoint

SCOPE_REACOES = 'DEVA_OPORTUNIDADE_V26_FIXTURE'
SOURCE_REACTION = 'SRD 5.2.1: Actions/Reactions, Melee Attacks/Opportunity Attacks'

class MotorReacoesSRD(MotorMagiasSRD):
    def validate(self, s=None):
        super().validate(s)
        s = s if s is not None else self.state
        if 'v26' in s['combate']:
            v=s['combate']['v26']
            assert v['distancia_ft'] in (None,5,10)
            assert type(v['posicao_confirmada']) is bool
            assert (v['distancia_ft'] is not None)==v['posicao_confirmada']
            assert set(v['reacao_usada'])=={'J1','J2'}
            assert all(type(x) is bool for x in v['reacao_usada'].values())
            assert type(v['desengajou_j2']) is bool
            assert type(v['movimento_restante_j2_ft']) is int and 0<=v['movimento_restante_j2_ft']<=20
            pending=v['pendencia_reacao']
            if pending is not None:
                assert pending=={'reagente':'J1','provocador':'J2','origem_ft':5,'destino_ft':10}
                assert s['fase']=='COMBATE' and s['ator_da_vez']=='J2'
                assert not v['reacao_usada']['J1'] and not v['desengajou_j2']
                assert v['distancia_ft']==5 and v['movimento_restante_j2_ft']>=10
        return True

    def _transition(self,s,actor,command,params):
        v26=s['combate'].get('v26')
        if v26 is not None and v26['pendencia_reacao'] is not None and command not in {
            'REAGIR_OPORTUNIDADE_DEVA_V26_TESTE','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE'}:
            raise InvalidAction('movimento interrompido: resolver ou recusar reacao antes de outra acao')
        if command=='INICIATIVA_DEVA_V25_TESTE':
            outcome=super()._transition(s,actor,command,params)
            s['combate']['v26']={'posicao_confirmada':False,'distancia_ft':None,
                'reacao_usada':{'J1':False,'J2':False},'pendencia_reacao':None,
                'movimento_restante_j2_ft':0,'desengajou_j2':False,
                'modelo':'DISTANCIA_RELATIVA_APENAS_5_10_FT'}
            return {**outcome,'extensao_v26':'POSICAO_INICIAL_PENDENTE_ARBITRO'}
        if command=='CONFIGURAR_DISTANCIA_V26_FIXTURE':
            if actor!='ARBITRO' or s['fase']!='COMBATE' or v26 is None:
                raise InvalidAction('configuracao exclusiva do arbitro durante fixture de combate')
            if v26['posicao_confirmada'] or any(s['combate']['v25']['turnos'].values()):
                raise InvalidAction('posicao inicial so pode ser configurada uma vez antes do primeiro turno')
            if params != {'aceite_escopo':SCOPE_REACOES,'distancia_ft':5,
                          'origem':'POSICIONAMENTO_ARTIFICIAL_EXPLICITO_DE_TESTE'}:
                raise UnresolvedRule('posicao inicial exige declaracao explicita 5 ft da fixture')
            v26['posicao_confirmada']=True;v26['distancia_ft']=5
            return {'distancia_relativa_ft':5,'origem':'FIXTURE_EXPLICITA_NAO_OFICIAL'}
        if command=='INICIO_TURNO_DEVA_V25_TESTE':
            if v26 is None or not v26['posicao_confirmada']:
                raise UnresolvedRule('configuracao espacial explicita v2.6 pendente')
            if actor=='J1':
                # Both supported distances (5 and 10ft) fall within Gibbering's 20ft aura.
                if params.get('gibbering_aplicavel_fixture') is not True:
                    raise UnresolvedRule('aura Gibbering deve ser aplicada neste posicionamento')
            outcome=super()._transition(s,actor,command,params)
            v26['reacao_usada'][actor]=False
            if actor=='J2':
                v26['movimento_restante_j2_ft']=20
                v26['desengajou_j2']=False
            return {**outcome,'reacao_disponivel':True}
        if command=='MULTIATTACK_HOLY_MACE_V25_TESTE' and v26 is not None:
            if not v26['posicao_confirmada'] or v26['distancia_ft']>5:
                raise InvalidAction('Holy Mace tem alcance 5 ft; alvo fora de alcance na fixture')
        if command=='DESENGAJAR_MOUTH_V26_TESTE':
            if actor!='J2':raise InvalidAction('fixture de desengajar exclusiva do Gibbering Mouther')
            v=self._turn(s,actor)
            if v26 is None or not v26['posicao_confirmada'] or v['inicio_pendente'] or not v['inicio_resolvido']:
                raise InvalidAction('turno do Mouther nao iniciado')
            if v['acao_utilizada']:raise InvalidAction('acao principal ja usada')
            if params!={'aceite_escopo':SCOPE_REACOES}:
                raise UnresolvedRule('escopo de teste nao confirmado')
            v['acao_utilizada']=True;v26['desengajou_j2']=True
            return {'acao':'Disengage','categoria_acao':'ACTION','evita_ataque_oportunidade':True}
        if command=='MOVIMENTO_MOUTH_V26_TESTE':
            if actor!='J2':raise InvalidAction('somente Mouther se move neste recorte')
            v=self._turn(s,actor)
            if v26 is None or not v26['posicao_confirmada'] or v['inicio_pendente'] or not v['inicio_resolvido']:
                raise InvalidAction('turno do Mouther nao iniciado')
            if params.get('aceite_escopo')!=SCOPE_REACOES or params.get('tipo')!='DESLOCAMENTO':
                raise UnresolvedRule('somente deslocamento proprio e confirmado integra esta fixture')
            if params.get('visivel_ao_deva') is not True:
                raise UnresolvedRule('visibilidade ao Deva deve ser explicitamente confirmada')
            target=params.get('destino_ft')
            if type(target) is not int or target not in (5,10) or target==v26['distancia_ft']:
                raise InvalidAction('destino relativo invalido ou sem deslocamento')
            distance=abs(target-v26['distancia_ft'])
            # Gibbering Mouther: Speed 20ft, Aberrant Ground: difficult terrain in 10ft Emanation.
            # This fixture models a ground path entirely inside that emanation (5ft costs 10ft).
            movement_cost=distance*2
            if movement_cost>v26['movimento_restante_j2_ft']:
                raise InvalidAction('velocidade disponivel do Mouther insuficiente')
            if v26['distancia_ft']==5 and target==10 and not v26['desengajou_j2'] and not v26['reacao_usada']['J1']:
                v26['pendencia_reacao']={'reagente':'J1','provocador':'J2','origem_ft':5,'destino_ft':10}
                return {'movimento':'INTERROMPIDO_ANTES_DE_SAIR_DO_ALCANCE',
                        'gatilho':'ATAQUE_OPORTUNIDADE','reagente':'J1','distancia_atual_ft':5}
            previous=v26['distancia_ft'];v26['distancia_ft']=target
            v26['movimento_restante_j2_ft']-=movement_cost
            return {'movimento':'CONCLUIDO_SEM_REACAO','origem_ft':previous,'destino_ft':target,'custo_movimento_ft':movement_cost,
                    'motivo':'DESENGAJOU' if v26['desengajou_j2'] else
                    ('REACAO_JA_CONSUMIDA' if v26['reacao_usada']['J1'] else 'NAO_SAIU_DO_ALCANCE')}
        if command in {'REAGIR_OPORTUNIDADE_DEVA_V26_TESTE','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE'}:
            if actor!='J1' or s['fase']!='COMBATE' or s['ator_da_vez']!='J2' or v26 is None:
                raise InvalidAction('reacao somente pelo Deva durante turno do Mouther')
            if v26['pendencia_reacao'] is None or v26['reacao_usada']['J1']:
                raise InvalidAction('nenhum gatilho de oportunidade disponivel')
            self._pair(s)
            if params.get('aceite_escopo')!=SCOPE_REACOES:
                raise UnresolvedRule('escopo da reacao nao confirmado')
            if command=='RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE':
                if set(params)!={'aceite_escopo'}:raise InvalidAction('recusa nao aceita rolagens')
                v26['pendencia_reacao']=None;v26['distancia_ft']=10
                v26['movimento_restante_j2_ft']-=10
                return {'reacao':'RECUSADA','reacao_consumida':False,'movimento':'CONCLUIDO','distancia_ft':10,'custo_movimento_ft':10}
            if set(params)!={'aceite_escopo','ataque'} or type(params['ataque']) is not dict:
                raise InvalidAction('ataque de oportunidade requer uma unica jogada')
            attack=params['ataque'];roll=attack.get('d20_simulado')
            if not self._die(roll,20):raise InvalidAction('d20 simulado invalido')
            critical=roll==20;hit=critical or (roll!=1 and roll+8>=9)
            b=attack.get('d6_contundente',[]);rad=attack.get('d8_radiante',[])
            if set(attack)!={'d20_simulado','d6_contundente','d8_radiante'}:
                raise InvalidAction('campos do ataque invalidos')
            if not isinstance(b,list) or len(b)!=((2 if critical else 1) if hit else 0):
                raise InvalidAction('d6 contundente invalido')
            if not isinstance(rad,list) or len(rad)!=((8 if critical else 4) if hit else 0):
                raise InvalidAction('d8 radiante invalido')
            if not all(self._die(d,6) for d in b) or not all(self._die(d,8) for d in rad):
                raise InvalidAction('valores de dano invalidos')
            target=self.get_card(s,'J2',MOUTH)
            before=target['pv_atual'];damage=sum(b)+sum(rad)+4 if hit else 0
            after=max(0,before-damage);target['pv_atual']=after
            v26['reacao_usada']['J1']=True;v26['pendencia_reacao']=None
            result={'reacao':'ATAQUE_OPORTUNIDADE','ataque':'Holy Mace (um ataque)',
                    'categoria_acao':'REACTION','fonte':SOURCE_REACTION,
                    'fonte_criatura':SOURCES['Deva'],'d20_simulado':roll,
                    'acertou':hit,'critico':critical,'dados_d6_contundente':copy.deepcopy(b),
                    'dados_d8_radiante':copy.deepcopy(rad),'dano':damage,
                    'pv_alvo_antes':before,'pv_alvo_depois':after,'reacao_consumida':True}
            if after==0:
                self._ko(s,'J1','FIXTURE_ATAQUE_OPORTUNIDADE_V26')
                result['ko']=True;result['movimento']='INTERROMPIDO_POR_KO'
            else:
                v26['distancia_ft']=10;v26['movimento_restante_j2_ft']-=10
                result['ko']=False;result['movimento']='CONCLUIDO_APOS_REACAO';result['distancia_ft']=10;result['custo_movimento_ft']=10
            return result
        return super()._transition(s,actor,command,params)

    def public(self):
        view=super().public();v=self.state['combate'].get('v26')
        if v is not None:
            view['reacoes_v26']={'posicao_confirmada':v['posicao_confirmada'],
                'distancia_relativa_ft':v['distancia_ft'],
                'reacao_deva_utilizada':v['reacao_usada']['J1'],
                'gatilho_pendente':v['pendencia_reacao'] is not None,
                'movimento_restante_mouther_ft':v['movimento_restante_j2_ft']}
        return view

    def checkpoint(self):
        p=super().checkpoint();p['schema']='POC_MOTOR_REACOES_V2_6_TESTE';return p

    @classmethod
    def restore(cls,checkpoint,records):
        if checkpoint.get('schema')!='POC_MOTOR_REACOES_V2_6_TESTE':
            raise CorruptedCheckpoint('schema de checkpoint v2.6 invalido')
        p=copy.deepcopy(checkpoint);p['schema']='POC_MOTOR_MAGIAS_V2_5_TESTE'
        return super().restore(p,records)
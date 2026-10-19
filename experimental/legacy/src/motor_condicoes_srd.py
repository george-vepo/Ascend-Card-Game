"""SRD Card Game experimental v2.4: two verified SRD creatures ONLY.

This is a partial, deterministic fixture. No RNG, official match, or tactical
range adjudication. Every spatial trigger is supplied explicitly as a fixture
fact; absence of that fact rejects the action without changing game state.
Blinding Spittle, Gibbering, Blinded, radiant resistance, and recharge are tested.
Other monster actions/effects are NOT emulated, and this is NOT full SRD combat.
Sources: SRD CC 5.2.1 printed pp. 7, 13, 177, 288, 352.
"""
from __future__ import annotations
import copy
from motor_combate_v23 import MotorCombateSRD, VERIFIED_SRD
from motor_base_v22 import InvalidAction, UnresolvedRule, CorruptedCheckpoint, other, SIDES

class MotorCondicoesSRD(MotorCombateSRD):
    SCOPE='EFEITOS_SRD_PARCIAIS_TESTE'

    def _get_combat_pair(self,s):
        out={}
        for p in SIDES:
            cid=s['jogadores'][p]['criatura_ativa_id']
            if cid not in VERIFIED_SRD:
                raise UnresolvedRule(f'criatura nao integrada nesta versao: {cid}')
            c=self.get_card(s,p,cid); b=VERIFIED_SRD[cid]
            if c['nome'].lower()!=b['name'].lower() or c['pv_max']!=b['hp']:
                raise UnresolvedRule(f'ficha/identidade divergente: {cid}')
            if set(c['condicoes'])-{'Blinded'}:
                raise UnresolvedRule('condicoes fora deste escopo nao implementadas')
            if any(e.get('tipo')!='BLINDED_SPITTLE' for e in c['efeitos']):
                raise UnresolvedRule('efeito ativo nao homologado neste modulo')
            out[p]=(cid,b)
        return out

    @staticmethod
    def _die(v,n):
        return type(v) is int and 1<=v<=n

    def _regras_efeitos(self,s):
        """Compatibilidade de testes legados v2.4; o Ascend sobrescreve
        esta função e exige parâmetros extraídos das fichas SRD externas.
        """
        return {
            'wis_bonus':4, 'dex_bonus':2,
            'gibbering':{'dc':10,'range_ft':20,'d8_faces':8},
            'spittle':{'dc':10,'radius_ft':10,'range_ft':30,
                       'damage_dice':(2,6),'damage_type':'Radiant',
                       'recharge_min':5,'recharge_max':6},
        }

    def _aplicar_recarga_spittle(self,s,dado,presente):
        """Comportamento legado preservado; integração SRD sobrescreve."""
        v=s['combate']['v24']
        if not v['spittle_disponivel']:
            if not self._die(dado,6):
                raise InvalidAction('recarga 5-6 exige d6 simulado')
            regras=self._regras_efeitos(s)
            faixa=regras['spittle']
            v['spittle_disponivel']=(faixa['recharge_min']<=dado<=faixa['recharge_max'])
            return {'d6':dado,'recarregou':v['spittle_disponivel']}
        if presente:
            raise InvalidAction('nao rolar recarga com poder disponivel')
        return None

    def _consumir_spittle(self,s):
        s['combate']['v24']['spittle_disponivel']=False

    def _aplicar_blinded_spittle(self,s,v,victim,out):
        """Expiração legada; nova camada usa ciclo de condições compartilhado."""
        if 'Blinded' not in victim['condicoes']:
            victim['condicoes'].append('Blinded')
        expiry=v['turnos_iniciados']['J2']+1
        victim['efeitos']=[
            e for e in victim['efeitos'] if e.get('tipo')!='BLINDED_SPITTLE'
        ]
        victim['efeitos'].append({
            'tipo':'BLINDED_SPITTLE','fonte':'AB-POC-008',
            'expira_ao_fim_turno_fonte':expiry,
        })
        out['blinded_ate_fim_turno_mouther']=expiry

    def _expirar_condicoes_fonte(self,s,actor):
        """Legado: expira Blinded apenas ao fim do turno da fonte."""
        v=s['combate']['v24']
        expired=[]
        if actor=='J2':
            victim=self.get_card(s,'J1','CE-001')
            for effect in list(victim['efeitos']):
                if (effect.get('tipo')=='BLINDED_SPITTLE' and
                        v['turnos_iniciados']['J2']>=effect['expira_ao_fim_turno_fonte']):
                    victim['efeitos'].remove(effect)
                    if not any(e.get('tipo')=='BLINDED_SPITTLE' for e in victim['efeitos']):
                        if 'Blinded' in victim['condicoes']:
                            victim['condicoes'].remove('Blinded')
                    expired.append('Blinded')
        return expired

    def _ready(self,s,actor):
        self._gate(s,'COMBATE',actor)
        if s['combate']['iniciativas'].get('origem')!='DADOS_SIMULADOS_TESTE':
            raise InvalidAction('iniciativa mecanica do modulo obrigatoria')
        if s['combate'].get('v24') is None:
            raise UnresolvedRule('marcadores de turno SRD nao inicializados')
        return s['combate']['v24']

    def _transition(self,s,actor,command,params):
        # Do not allow legacy test commands to bypass v2.4 start-of-turn effects.
        if command in {'ATAQUE_SRD_TESTE','INICIATIVA_FIXTURE',
                       'RODADA_SEGUINTE_FIXTURE','KO_COMBATE_FIXTURE'}:
            raise InvalidAction('comando legado desativado no motor v2.4')
        if command=='INICIATIVA_SRD_TESTE':
            result=super()._transition(s,actor,command,params)
            s['combate']['v24']={'pendente_inicio':True,'inicio_resolvido':False,
                'bloqueado':False,'turnos_iniciados':{'J1':0,'J2':0},
                'spittle_disponivel':True,'origem':'FIXTURE_SRD_V24'}
            s['combate']['mecanicas_nao_implementadas']={
                'J1':['Flyby/movimento; magias; efeitos espaciais sem confirmacao de fixture'],
                'J2':['Aberrant Ground; acoes fora de Bite/Blinding Spittle; resultados 7-8 de Gibbering sem selecao aprovada de alvo']}
            return {**result,'escopo':'EFEITOS_SRD_PARCIAIS_TESTE_COM_ATIVACAO_EXPLICITA'}
        if command=='INICIO_TURNO_V24_TESTE':
            v=self._ready(s,actor);self._get_combat_pair(s)
            if not v['pendente_inicio']:raise InvalidAction('inicio de turno ja registrado')
            if params.get('aceite_escopo')!=self.SCOPE:
                raise UnresolvedRule('declaracao explicita de escopo parcial obrigatoria')
            next_count=v['turnos_iniciados'][actor]+1
            response={'jogador':actor,'numero_turno_proprio':next_count,'dados_simulados':True}
            if actor=='J1':
                # Giant Owl begins its turn; the Mouther's area effect requires
                # explicit applicability, since this POC omits positioning.
                applies=params.get('gibbering_aplicavel_fixture')
                if type(applies) is not bool:
                    raise UnresolvedRule('confirmar separadamente aplicabilidade do Gibbering (20 ft)')
                response['gibbering_aplicavel_fixture']=applies
                if applies:
                    roll=params.get('wis_d20_simulado')
                    if not self._die(roll,20):raise InvalidAction('salvaguarda SAB precisa de d20 simulado')
                    # Giant Owl Wisdom save +4, explicitly SRD p.352
                    regras=self._regras_efeitos(s);bonus=regras['wis_bonus'];cd=regras['gibbering']['dc']
                    total=roll+bonus
                    response['gibbering_sab']={'d20':roll,'bonus':bonus,'total':total,'cd':cd,'sucesso':total>=cd,'alcance_gatilho_ft':regras['gibbering']['range_ft']}
                    if total<cd:
                        d8=params.get('gibbering_d8_simulado')
                        if not self._die(d8,regras['gibbering']['d8_faces']):raise InvalidAction('falha exige d8 simulado')
                        if d8>=7:
                            raise UnresolvedRule('Gibbering 7-8: ataque aleatorio dentro do alcance nao homologado sem alvo/alcance')
                        v['bloqueado']=True
                        response['gibbering_resultado_d8']=d8
                        response['turno_sem_acao']=True
                elif any(k in params for k in ('wis_d20_simulado','gibbering_d8_simulado')):
                    raise InvalidAction('dados Gibbering indevidos se gatilho nao se aplica')
            else:
                info=self._aplicar_recarga_spittle(
                    s,params.get('recarga_d6_simulado'),
                    'recarga_d6_simulado' in params
                )
                if info is not None:
                    response['recarga_spittle']=info
            v['turnos_iniciados'][actor]=next_count
            v['pendente_inicio']=False
            v['inicio_resolvido']=True
            response['bloqueado']=v['bloqueado']
            return response
        if command=='PASSAR_TURNO_V24_TESTE':
            v=self._ready(s,actor)
            if not v['inicio_resolvido'] or v['pendente_inicio'] or not v['bloqueado']:
                raise InvalidAction('passar permitido apenas quando Gibbering impede acao')
            result=self._finish_turn(s,actor)
            return {'passou_por':'Gibbering SRD d8 1-6',**result}
        if command=='ATAQUE_V24_TESTE':
            v=self._ready(s,actor)
            if v['pendente_inicio'] or not v['inicio_resolvido']:
                raise InvalidAction('resolver efeitos de inicio do turno antes do ataque')
            if v['bloqueado']:raise InvalidAction('Gibbering impede acao neste turno')
            if params.get('aceite_escopo')!=self.SCOPE:
                raise UnresolvedRule('escopo parcial nao confirmado')
            members=self._get_combat_pair(s)
            cid,source=members[actor];target_side=other(actor);tid,target=members[target_side]
            attack=source['attack']
            if params.get('ataque')!=attack['name']:raise InvalidAction('ataque nao documentado')
            is_blind='Blinded' in self.get_card(s,actor,cid)['condicoes']
            enemy_blind='Blinded' in self.get_card(s,target_side,tid)['condicoes']
            mode='NORMAL' if is_blind==enemy_blind else ('DESVANTAGEM' if is_blind else 'VANTAGEM')
            rolls=params.get('d20_simulados')
            count=1 if mode=='NORMAL' else 2
            if not isinstance(rolls,list) or len(rolls)!=count or not all(self._die(x,20) for x in rolls):
                raise InvalidAction(f'{mode} exige {count} d20 simulado(s)')
            roll=min(rolls) if mode=='DESVANTAGEM' else (max(rolls) if mode=='VANTAGEM' else rolls[0])
            total=roll+attack['bonus'];crit=roll==20;hit=crit or (roll!=1 and total>=target['ac'])
            damage_count=attack['dice'][0]*(2 if crit else 1) if hit else 0
            dice=params.get('dano_dados',[])
            if not isinstance(dice,list) or len(dice)!=damage_count or not all(self._die(d,attack['dice'][1]) for d in dice):
                raise InvalidAction('dados de dano invalidos para acerto/critico')
            raw=sum(dice)+attack['flat'] if hit else 0
            if attack['type'] in target['immunities']:
                applied=0
            elif attack['type'] in target['resistances']:
                applied=raw//2
            else:applied=raw
            victim=self.get_card(s,target_side,tid);before=victim['pv_atual']
            victim['pv_atual']=max(0,before-applied)
            outcome={'ator':actor,'alvo':target_side,'ataque':attack['name'],
                'dados_simulados':True,'d20_simulados':rolls,'modo_rolagem':mode,
                'd20_aplicado':roll,'bonus':attack['bonus'],'total':total,
                'ca':target['ac'],'acertou':hit,'critico':crit,'dados_dano':dice,
                'dano_bruto':raw,'dano_aplicado':applied,'pv_antes':before,'pv_depois':victim['pv_atual']}
            if actor=='J2':
                outcome['prone_aplicado']=False
                outcome['motivo']='Giant Owl e Large; Bite exige Medium ou menor'
            if victim['pv_atual']==0:
                self._ko(s,actor,'FIXTURE_SRD_V24_KO_COM_EFEITOS_PARCIAIS')
                outcome['ko']=True
            else:
                outcome.update(self._finish_turn(s,actor));outcome['ko']=False
            return outcome
        if command=='BLINDING_SPITTLE_V24_TESTE':
            v=self._ready(s,actor)
            if actor!='J2':raise InvalidAction('Blinding Spittle pertence ao Gibbering Mouther')
            if v['pendente_inicio'] or not v['inicio_resolvido'] or v['bloqueado']:
                raise InvalidAction('nao e acao valida para este turno')
            members=self._get_combat_pair(s)
            regras=self._regras_efeitos(s);spittle=regras['spittle']
            if params.get('aceite_escopo')!=self.SCOPE:
                raise UnresolvedRule('escopo experimental nao confirmado')
            if not v['spittle_disponivel']:
                raise InvalidAction('Blinding Spittle sem recarga')
            included=params.get('alvo_na_area_fixture')
            if type(included) is not bool:
                raise UnresolvedRule('area/alvo da esfera requer confirmacao de fixture')
            victim=self.get_card(s,'J1','CE-001');before=victim['pv_atual']
            out={'acao':'Blinding Spittle','ator':'J2','alvo':'J1',
                 'alvo_na_area_fixture':included,'dados_simulados':True,
                 'cd_des':spittle['dc'],
                 'raio_esfera_ft':spittle['radius_ft'],
                 'alcance_max_ft':spittle['range_ft']}
            if included:
                roll=params.get('dex_d20_simulado')
                if not self._die(roll,20):raise InvalidAction('salvaguarda DES exige d20 simulado')
                bonus=regras['dex_bonus'];total=roll+bonus
                out['salvaguarda_des']={'d20':roll,'bonus':bonus,'total':total,'sucesso':total>=spittle['dc']}
                if total<spittle['dc']:
                    dice=params.get('dano_d6_simulados')
                    if (not isinstance(dice,list) or
                            len(dice)!=spittle['damage_dice'][0] or
                            not all(self._die(x,spittle['damage_dice'][1]) for x in dice)):
                        raise InvalidAction('falha exige 2d6 radiante simulados')
                    raw=sum(dice)
                    resistiu=(spittle['damage_type'] in members['J1'][1]['resistances'])
                    aplicado_imune=(spittle['damage_type'] in members['J1'][1]['immunities'])
                    applied=(0 if aplicado_imune else raw//2 if resistiu else raw)
                    victim['pv_atual']=max(0,before-applied)
                    out.update({'dano_bruto':raw,'dano_aplicado':applied,'dados_dano':dice,
                                'resistencia_radiante':resistiu,'tipo_dano':spittle['damage_type']})
                    if victim['pv_atual']>0:
                        self._aplicar_blinded_spittle(s,v,victim,out)
                elif 'dano_d6_simulados' in params:
                    raise InvalidAction('salvaguarda bem sucedida nao recebe dados de dano')
            elif any(k in params for k in ('dex_d20_simulado','dano_d6_simulados')):
                raise InvalidAction('alvo fora de area nao rola salvaguarda/dano')
            self._consumir_spittle(s)
            out['pv_antes']=before;out['pv_depois']=victim['pv_atual']
            if victim['pv_atual']==0:
                self._ko(s,'J2','FIXTURE_SRD_V24_BLINDING_SPITTLE_KO')
                out['ko']=True
            else:
                out.update(self._finish_turn(s,actor));out['ko']=False
            return out
        return super()._transition(s,actor,command,params)

    def _finish_turn(self,s,actor):
        v=s['combate']['v24']
        # Reutilizar o ciclo de efeitos; legado preserva a mesma semântica.
        expired=self._expirar_condicoes_fonte(s,actor)
        order=s['combate']['ordem_turnos'];index=s['combate']['indice_turno']
        if order[index]!=actor:raise InvalidAction('indice de turno inconsistente')
        if index==0:
            s['combate']['indice_turno']=1;s['ator_da_vez']=order[1]
        else:
            s['combate']['indice_turno']=0;s['combate']['rodada']+=1;s['ator_da_vez']=order[0]
        v['bloqueado']=False;v['inicio_resolvido']=False;v['pendente_inicio']=True
        return {'proximo_ator':s['ator_da_vez'],'proxima_rodada':s['combate']['rodada'],
                'efeitos_expirados':expired}

    def public(self):
        data=super().public();s=self.state
        for p in SIDES:
            cid=s['jogadores'][p]['criatura_ativa_id']
            if cid:
                c=self.get_card(s,p,cid)
                data['jogadores'][p]['campo']['efeitos']=copy.deepcopy(c['efeitos'])
        if s['fase']=='COMBATE' and 'v24' in s['combate']:
            v=s['combate']['v24']
            data['efeitos_combate']={'inicio_de_turno_pendente':v['pendente_inicio'],
                'spittle_disponivel':v['spittle_disponivel']}
        return data

    def checkpoint(self):
        cp=super().checkpoint();cp['schema']='POC_MOTOR_COMBATE_V2_4_TESTE'
        return cp

    @classmethod
    def restore(cls,checkpoint,records):
        if checkpoint.get('schema')!='POC_MOTOR_COMBATE_V2_4_TESTE':
            raise CorruptedCheckpoint('schema v2.4 invalido')
        cp=copy.deepcopy(checkpoint);cp['schema']='POC_MOTOR_COMBATE_V2_3_TESTE'
        return super().restore(cp,records)
"""SRD Card Game v2.5: isolated DEVA vs GIBBERING MOUTHER experimental encounter.

Verbatim rules verified in SRD_CC_v5.2.1.pdf printed pp. 279 (Deva),
288 (Gibbering Mouther), 121 (Cure Wounds); no actual dice or official match.
Only explicit subset: start-of-turn Gibbering save for Deva, Deva's 2-Holy-Mace
Multiattack, its Divine Aid bonus action/Cure Wounds (self), turn/action economy.
Other actions, spells, special traits, reactions and range remain UNIMPLEMENTED.
"""
from __future__ import annotations
import copy
from motor_base_v22 import MotorPOC, InvalidAction, UnresolvedRule, CorruptedCheckpoint, SIDES, other

SCOPE='DEVA_SRD_PARCIAL_V25_TESTE'
DEVA='CE-026'
MOUTH='AB-POC-008'
SOURCES={'Deva':'SRD 5.2.1 p.279','Gibbering Mouther':'SRD 5.2.1 p.288',
         'Cure Wounds':'SRD 5.2.1 p.121'}

class MotorMagiasSRD(MotorPOC):
    SCOPE=SCOPE
    def _pair(self,s):
        a=self.get_card(s,'J1',DEVA); b=self.get_card(s,'J2',MOUTH)
        if (s['jogadores']['J1']['criatura_ativa_id']!=DEVA or
            s['jogadores']['J2']['criatura_ativa_id']!=MOUTH):
            raise UnresolvedRule('fixture v2.5 exige Deva ativa contra Gibbering Mouther')
        if (a['nome']!='Deva' or a['pv_max']!=229 or b['nome']!='Gibbering Mouther' or b['pv_max']!=52):
            raise UnresolvedRule('ficha/identidade incompatível com SRD')
        if a['condicoes'] or b['condicoes'] or a['efeitos'] or b['efeitos']:
            raise UnresolvedRule('condicoes/efeitos nao implementados para este fixture')
        return a,b

    @staticmethod
    def _die(v,n):
        return type(v) is int and 1<=v<=n

    def _turn(self,s,actor):
        self._gate(s,'COMBATE',actor)
        if s['combate'].get('v25') is None or s['combate']['iniciativas'].get('origem')!='DADOS_SIMULADOS_TESTE':
            raise InvalidAction('iniciativa e estado v2.5 necessarios')
        self._pair(s)
        return s['combate']['v25']

    def _transition(self,s,actor,command,params):
        if command in {'KO_COMBATE_FIXTURE','RODADA_SEGUINTE_FIXTURE','INICIATIVA_FIXTURE'}:
            raise InvalidAction('atalho legado de combate desativado na v2.5')
        if command=='EVOLUIR':
            r=super()._transition(s,actor,command,params)
            if actor=='J1' and params.get('carta_id')==DEVA:
                c=self.get_card(s,'J1',DEVA)
                c['recursos']['divine_aid_restante']=2
                c['recursos']['divine_aid_limite_dia']=2
            return r
        if command=='INICIATIVA_DEVA_V25_TESTE':
            if actor!='ARBITRO' or s['fase']!='INICIATIVA':
                raise InvalidAction('iniciativa somente arbitro e fase INICIATIVA')
            self._pair(s)
            rolls=params.get('d20_simulados')
            if not isinstance(rolls,dict) or set(rolls)!=set(SIDES) or not all(self._die(n,20) for n in rolls.values()):
                raise InvalidAction('iniciativa exige d20 simulado valido de ambos')
            totals={'J1':rolls['J1']+4,'J2':rolls['J2']-1}
            if totals['J1']==totals['J2']:
                raise UnresolvedRule('desempate de iniciativa ainda nao definido')
            order=sorted(SIDES,key=lambda p:totals[p],reverse=True)
            s['fase']='COMBATE';s['ator_da_vez']=order[0]
            s['combate']['rodada']=1;s['combate']['ordem_turnos']=order
            s['combate']['indice_turno']=0
            s['combate']['iniciativas']={**totals,'origem':'DADOS_SIMULADOS_TESTE',
                'rolagens':copy.deepcopy(rolls),'modificadores':{'J1':4,'J2':-1}}
            s['combate']['v25']={'inicio_pendente':True,'inicio_resolvido':False,
                'acao_utilizada':False,'bonus_utilizado':False,'turnos':{'J1':0,'J2':0},
                'ferimento_fixture_aplicado':False,
                'mecanicas_fora_escopo':['posicionamento','outros tracos e magias',
                    'reacoes sem habilidade na ficha','Blinding Spittle','Bite com Prone',
                    'Gibbering d8 7-8 exige alvo aleatorio e alcance']}
            return {'ordem':order,'iniciativas':totals,'d20_simulados':copy.deepcopy(rolls),
                    'escopo':SCOPE,'mecanicas_nao_implementadas':copy.deepcopy(s['combate']['v25']['mecanicas_fora_escopo'])}
        if command=='FERIMENTO_DEVA_V25_FIXTURE':
            if actor!='ARBITRO' or s['fase']!='COMBATE':
                raise InvalidAction('ferimento artificial so pela arbitragem de teste')
            a,_=self._pair(s);v=s['combate']['v25']
            if v['ferimento_fixture_aplicado'] or any(v['turnos'].values()) or not v['inicio_pendente']:
                raise InvalidAction('ferimento fixture apenas uma vez antes do primeiro turno')
            if params.get('aceite_escopo')!=SCOPE or params.get('origem')!='FERIMENTO_ARTIFICIAL_SEM_EVENTO_SRD':
                raise UnresolvedRule('ferimento somente com fixture explicito')
            new_pv=params.get('pv_atual')
            if type(new_pv) is not int or not 1<=new_pv<a['pv_atual']:
                raise InvalidAction('PV artificial deve ser inteiro positivo inferior aos atuais')
            before=a['pv_atual'];a['pv_atual']=new_pv;v['ferimento_fixture_aplicado']=True
            return {'fixture_artificial':True,'deva_pv_antes':before,'pv_depois':new_pv}
        if command=='INICIO_TURNO_DEVA_V25_TESTE':
            v=self._turn(s,actor)
            if not v['inicio_pendente']:raise InvalidAction('inicio de turno duplicado')
            if params.get('aceite_escopo')!=SCOPE:raise UnresolvedRule('escopo parcial nao confirmado')
            info={'jogador':actor,'dados_simulados':True}
            if actor=='J1':
                applies=params.get('gibbering_aplicavel_fixture')
                if type(applies) is not bool:
                    raise UnresolvedRule('confirmacao explicita de alcance do Gibbering necessaria')
                info['gibbering_aplicavel_fixture']=applies
                if applies:
                    w=params.get('sab_d20_simulado')
                    if not self._die(w,20):raise InvalidAction('exige salvaguarda Sabedoria d20 simulada')
                    # Deva Wisdom save +9, SRD p.279; DC 10 Gibbering.
                    info['gibbering']={'d20':w,'bonus_sab':9,'total':w+9,'cd':10,'sucesso':w+9>=10}
                    if w+9<10:
                        raise UnresolvedRule('resultado Gibbering com falha exige d8 e tratamento aprovado')
                elif 'sab_d20_simulado' in params:
                    raise InvalidAction('nao rolar dado sem gatilho')
            elif any(k in params for k in ('gibbering_aplicavel_fixture','sab_d20_simulado')):
                raise InvalidAction('nao existe Gibbering contra o Mouther')
            v['turnos'][actor]+=1
            v['inicio_pendente']=False;v['inicio_resolvido']=True
            v['acao_utilizada']=False;v['bonus_utilizado']=False
            return info
        if command=='DIVINE_AID_CURE_WOUNDS_V25_TESTE':
            v=self._turn(s,actor)
            if actor!='J1':raise InvalidAction('Divine Aid pertence ao Deva')
            if v['inicio_pendente'] or not v['inicio_resolvido']:raise InvalidAction('turno nao iniciado')
            if v['bonus_utilizado']:raise InvalidAction('acao bonus ja utilizada')
            if params.get('aceite_escopo')!=SCOPE:raise UnresolvedRule('escopo parcial nao confirmado')
            if params.get('magia')!='Cure Wounds' or params.get('alvo')!=DEVA:
                raise UnresolvedRule('somente Cure Wounds em si mesmo integrada; alvo/efeito externo pendente')
            card=self.get_card(s,'J1',DEVA)
            uses=card['recursos'].get('divine_aid_restante')
            if type(uses) is not int or uses<=0:raise InvalidAction('Divine Aid sem usos restantes')
            dice=params.get('d8_simulados')
            if not isinstance(dice,list) or len(dice)!=2 or not all(self._die(d,8) for d in dice):
                raise InvalidAction('Cure Wounds exige exatamente 2d8 simulados')
            raw=sum(dice)+5;before=card['pv_atual']
            if before is None or before<=0:raise InvalidAction('alvo sem PV positivos')
            after=min(card['pv_max'],before+raw)
            card['pv_atual']=after
            card['recursos']['divine_aid_restante']-=1
            v['bonus_utilizado']=True
            return {'habilidade':'Divine Aid','magia':'Cure Wounds','categoria_acao':'BONUS',
                    'fonte':SOURCES['Deva'],'magia_fonte':SOURCES['Cure Wounds'],
                    'dados_simulados':True,'d8_simulados':copy.deepcopy(dice),
                    'modificador_carisma':5,'cura_calculada':raw,'cura_efetiva':after-before,
                    'pv_antes':before,'pv_depois':after,'usos_restantes':card['recursos']['divine_aid_restante']}
        if command=='MULTIATTACK_HOLY_MACE_V25_TESTE':
            v=self._turn(s,actor)
            if actor!='J1':raise InvalidAction('Holy Mace integrada somente para Deva')
            if v['inicio_pendente'] or not v['inicio_resolvido']:raise InvalidAction('turno nao iniciado')
            if v['acao_utilizada']:raise InvalidAction('acao ja utilizada')
            if params.get('aceite_escopo')!=SCOPE:raise UnresolvedRule('escopo parcial nao confirmado')
            attacks=params.get('ataques')
            if not isinstance(attacks,list) or len(attacks) not in (1,2):
                raise InvalidAction('Multiattack requer ataques declarados (ate dois; um se primeiro KO)')
            target=self.get_card(s,'J2',MOUTH)
            details=[]
            for index,att in enumerate(attacks):
                if type(att) is not dict:raise InvalidAction('ataque exige dados estruturados')
                d20=att.get('d20_simulado')
                if not self._die(d20,20):raise InvalidAction('d20 ataque invalido')
                crit=d20==20;hit=crit or (d20!=1 and d20+8>=9)
                b=att.get('d6_contundente',[]);rad=att.get('d8_radiante',[])
                if not isinstance(b,list) or len(b)!=((2 if crit else 1) if hit else 0):
                    raise InvalidAction('quantidade de d6 contundente invalida')
                if not isinstance(rad,list) or len(rad)!=((8 if crit else 4) if hit else 0):
                    raise InvalidAction('quantidade de d8 radiante invalida')
                if not all(self._die(x,6) for x in b) or not all(self._die(x,8) for x in rad):
                    raise InvalidAction('dados de dano invalidos')
                raw=(sum(b)+4+sum(rad)) if hit else 0
                before=target['pv_atual'];after=max(0,before-raw)
                target['pv_atual']=after
                details.append({'indice':index+1,'d20_simulado':d20,'bonus_ataque':8,
                                'total':d20+8,'ca_alvo':9,'acertou':hit,'critico':crit,
                                'dados_d6_contundente':b,'dados_d8_radiante':rad,
                                'dano':raw,'pv_antes':before,'pv_depois':after})
                if after==0:
                    if len(attacks)!=index+1:
                        raise InvalidAction('nao fornecer segundo ataque depois de KO')
                    break
            if target['pv_atual']>0 and len(attacks)!=2:
                raise InvalidAction('Multiattack exige dois ataques se nao houve KO')
            v['acao_utilizada']=True
            ret={'ataque':'Multiattack: Holy Mace x2','categoria_acao':'ACTION',
                 'fonte':SOURCES['Deva'],'detalhes':details,'dados_simulados':True}
            if target['pv_atual']==0:
                self._ko(s,'J1','FIXTURE_DEVA_HOLY_MACE_PARCIAL_V25')
                ret['ko']=True;ret['placar_fixture']=copy.deepcopy(s['placar'])
            else:ret['ko']=False
            return ret
        if command=='ENCERRAR_TURNO_DEVA_V25_TESTE':
            v=self._turn(s,actor)
            if v['inicio_pendente'] or not v['inicio_resolvido']:
                raise InvalidAction('inicio de turno pendente')
            order=s['combate']['ordem_turnos'];idx=s['combate']['indice_turno']
            if order[idx]!=actor:raise InvalidAction('turno inconsistente')
            if idx==0:s['combate']['indice_turno']=1;s['ator_da_vez']=order[1]
            else:s['combate']['indice_turno']=0;s['combate']['rodada']+=1;s['ator_da_vez']=order[0]
            v['inicio_pendente']=True;v['inicio_resolvido']=False
            return {'proximo_ator':s['ator_da_vez'],'rodada':s['combate']['rodada'],
                    'acao_usada':v['acao_utilizada'],'bonus_usado':v['bonus_utilizado']}
        if command=='REACAO_DEVA_V25_TESTE':
            self._turn(s,actor)
            raise InvalidAction('nenhuma reacao especifica habilitada para esta dupla SRD; nao inventar habilidade')
        return super()._transition(s,actor,command,params)

    def public(self):
        view=super().public();s=self.state
        for p in SIDES:
            cid=s['jogadores'][p]['criatura_ativa_id']
            if cid:
                c=self.get_card(s,p,cid)
                view['jogadores'][p]['campo']={'carta_id':cid,'nome':c['nome'],
                     'pv_atual':c['pv_atual'],'pv_max':c['pv_max'],
                     'condicoes':copy.deepcopy(c['condicoes']),
                     'recursos':copy.deepcopy(c['recursos']) if p=='J1' else {}}
            else:view['jogadores'][p]['campo']=None
        if s['fase']=='COMBATE' and 'v25' in s['combate']:
            v=s['combate']['v25']
            view['economia_turno']={'inicio_pendente':v['inicio_pendente'],
                 'acao_usada':v['acao_utilizada'],'bonus_usado':v['bonus_utilizado']}
        view['dados_sao_simulados']=True
        return view

    def checkpoint(self):
        p=super().checkpoint();p['schema']='POC_MOTOR_MAGIAS_V2_5_TESTE';return p

    @classmethod
    def restore(cls,checkpoint,records):
        if checkpoint.get('schema')!='POC_MOTOR_MAGIAS_V2_5_TESTE':
            raise CorruptedCheckpoint('schema de checkpoint v2.5 invalido')
        p=copy.deepcopy(checkpoint);p['schema']='POC_MOTOR_CHECKPOINT_V2_2_TESTE'
        return super().restore(p,records)
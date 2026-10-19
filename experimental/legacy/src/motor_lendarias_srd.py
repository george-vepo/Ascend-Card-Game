"""SRD Card Game — v2.6, isolated Solar / Aboleth legendary-action fixture.

Sources: SRD 5.2.1 printed pp.258, 326–327.  Not a full combat engine.
Every d20/d6 is supplied by a test caller and is labeled simulated.
No draws, shuffles or mutations of an official game.
"""
from __future__ import annotations
import copy
from motor_poc import MotorPOC, InvalidAction, UnresolvedRule, CorruptedCheckpoint, SIDES, other

SOLAR = 'CE-039'
ABOLETH = 'AB-POC-031'
SCOPE = 'SOLAR_ABOLETH_LENDARIAS_V26_FIXTURE'

class MotorLendariasSRD(MotorPOC):
    def _pair(self, s):
        if s['jogadores']['J1']['criatura_ativa_id'] != SOLAR or s['jogadores']['J2']['criatura_ativa_id'] != ABOLETH:
            raise UnresolvedRule('recorte v2.6 requer Solar vs Aboleth ativas')
        a = self.get_card(s, 'J1', SOLAR)
        b = self.get_card(s, 'J2', ABOLETH)
        if (a['nome'], a['pv_max'], b['nome'], b['pv_max']) != ('Solar', 297, 'Aboleth', 150):
            raise UnresolvedRule('identidade/PV da ficha SRD nao conferem')
        return a, b

    @staticmethod
    def _die(x, size):
        return type(x) is int and 1 <= x <= size

    def _combat(self, s):
        if s['fase'] != 'COMBATE' or 'v26' not in s['combate']:
            raise InvalidAction('nao existe combate v2.6 iniciado')
        self._pair(s)
        return s['combate']['v26']

    def _transition(self, s, actor, command, params):
        if command in {'KO_COMBATE_FIXTURE', 'RODADA_SEGUINTE_FIXTURE', 'INICIATIVA_FIXTURE'}:
            raise InvalidAction('atalhos artificiais legados desabilitados neste recorte')
        if command == 'INICIATIVA_LENDARIAS_V26_TESTE':
            if actor != 'ARBITRO' or s['fase'] != 'INICIATIVA':
                raise InvalidAction('somente arbitro inicia iniciativa na fase adequada')
            self._pair(s)
            dice = params.get('d20_simulados')
            if not isinstance(dice, dict) or set(dice) != set(SIDES) or not all(self._die(x, 20) for x in dice.values()):
                raise InvalidAction('iniciativa requer dois d20 simulados validos')
            totals = {'J1': dice['J1'] + 20, 'J2': dice['J2'] + 7}
            if totals['J1'] == totals['J2']:
                raise UnresolvedRule('desempate de iniciativa ainda sem regra aprovada')
            order = sorted(SIDES, key=lambda k: totals[k], reverse=True)
            s['fase'] = 'COMBATE'
            s['ator_da_vez'] = order[0]
            s['combate'].update({'rodada': 1, 'indice_turno': 0, 'ordem_turnos': order,
                'iniciativas': {**totals, 'rolagens': copy.deepcopy(dice), 'modificadores': {'J1':20,'J2':7},
                                 'origem': 'DADOS_SIMULADOS_TESTE'},
                'v26': {'pendente_inicio': True, 'turno_aberto': False,
                        'janela_lendaria': None, 'turnos_iniciados': {'J1': 0, 'J2': 0},
                        'cegueira_minuto_pendente': False,
                        'mecanicas_pendentes': ['ataques ordinarios', 'outras magias, habilidades e acoes',
                            'reacoes sem habilidade declarada nas fichas deste par',
                            'Mucus Cloud depende de estar submerso',
                            'escape de Grappled e mudanca de posicionamento',
                            'conversao exata de um minuto em turnos quando necessario']}})
            self.get_card(s,'J1',SOLAR)['recursos'].update({'acoes_lendarias_restantes':3,'limite_lendario':3,
                'blinding_gaze_ja_usado_desde_ultimo_turno':False,'resistencia_lendaria_restante':4})
            self.get_card(s,'J2',ABOLETH)['recursos'].update({'acoes_lendarias_restantes':3,'limite_lendario':3,
                'resistencia_lendaria_restante':3})
            return {'ordem':order, 'totais':totals, 'dados_simulados':True, 'escopo':SCOPE}
        if command == 'INICIAR_TURNO_V26_TESTE':
            v = self._combat(s)
            if actor not in SIDES or actor != s['ator_da_vez'] or not v['pendente_inicio']:
                raise InvalidAction('turno fora de ordem ou iniciado duas vezes')
            if params.get('aceite_escopo') != SCOPE: raise UnresolvedRule('confirmar escopo parcial')
            c = self._pair(s)[0 if actor=='J1' else 1]
            v['janela_lendaria'] = None
            v['turnos_iniciados'][actor] += 1
            v['pendente_inicio'] = False
            v['turno_aberto'] = True
            c['recursos']['acoes_lendarias_restantes'] = c['recursos']['limite_lendario']
            if actor == 'J1': c['recursos']['blinding_gaze_ja_usado_desde_ultimo_turno'] = False
            return {'turno':actor, 'acoes_lendarias_repostas':c['recursos']['acoes_lendarias_restantes'],
                    'dados_simulados':True, 'atencao':'acoes convencionais nao integradas neste fixture'}
        if command == 'ENCERRAR_TURNO_V26_TESTE':
            v = self._combat(s)
            if actor != s['ator_da_vez'] or v['pendente_inicio'] or not v['turno_aberto']:
                raise InvalidAction('turno nao iniciado ou fora de ordem')
            if params.get('aceite_escopo') != SCOPE:raise UnresolvedRule('fixture precisa reconhecer limitacoes')
            if params.get('efeitos_de_turno_verificados') is not True:
                raise UnresolvedRule('efeitos de inicio/fim do turno nao podem ser ignorados sem evidencia')
            order = s['combate']['ordem_turnos'];ix = s['combate']['indice_turno']
            if order[ix] != actor:raise InvalidAction('indice inconsistente')
            if ix == 0: s['combate']['indice_turno'] = 1
            else:
                s['combate']['indice_turno'] = 0
                s['combate']['rodada'] += 1
            s['ator_da_vez'] = order[s['combate']['indice_turno']]
            v['turno_aberto'] = False
            v['pendente_inicio'] = True
            v['janela_lendaria'] = {'dono': other(actor), 'apos_turno': actor, 'utilizada':False}
            return {'turno_encerrado':actor, 'proximo':s['ator_da_vez'],
                    'janela_aberta_para':other(actor), 'rodada':s['combate']['rodada']}
        if command == 'USAR_LENDARIA_V26_TESTE':
            v = self._combat(s)
            w = v['janela_lendaria']
            if not isinstance(w,dict) or w['utilizada'] or actor not in SIDES or w['dono'] != actor:
                raise InvalidAction('acao lendaria exige janela livre imediatamente apos turno alheio')
            if v['turno_aberto'] or w['apos_turno'] == actor:
                raise InvalidAction('acao lendaria exige turno alheio ja encerrado')
            if params.get('aceite_escopo') != SCOPE:raise UnresolvedRule('confirmar escopo SRD parcial')
            solar, aboleth = self._pair(s)
            source = solar if actor == 'J1' else aboleth
            if 'Incapacitated' in source['condicoes'] or source['pv_atual'] <= 0:
                raise InvalidAction('criatura incapacitada/derrotada nao age')
            if source['recursos'].get('acoes_lendarias_restantes',0) < 1:
                raise InvalidAction('nenhum uso lendario restante')
            action = params.get('habilidade')
            if actor=='J1' and action=='Blinding Gaze':
                if solar['recursos']['blinding_gaze_ja_usado_desde_ultimo_turno']:
                    raise InvalidAction('Blinding Gaze indisponivel ate inicio proximo turno do Solar')
                if params.get('alvo_visivel_fixture') is not True:
                    raise UnresolvedRule('visibilidade do alvo precisa estar confirmada')
                roll = params.get('constituicao_d20_simulado')
                if not self._die(roll,20):raise InvalidAction('d20 de CON invalido')
                total = roll + 6  # Aboleth Constitution saving throw +6, SRD p.258.
                failed = total < 25
                opt = params.get('aboleth_gasta_resistencia_lendaria')
                if type(opt) is not bool:raise UnresolvedRule('decisao explicita da IA sobre resistencia lendaria')
                if opt and not failed:raise InvalidAction('resistencia so pode substituir falha')
                if opt:
                    remaining = aboleth['recursos'].get('resistencia_lendaria_restante',0)
                    if remaining < 1:raise InvalidAction('resistencia lendaria esgotada')
                    aboleth['recursos']['resistencia_lendaria_restante'] = remaining-1
                blindness = failed and not opt
                if blindness:
                    if 'Blinded' not in aboleth['condicoes']:aboleth['condicoes'].append('Blinded')
                    if not any(e.get('tipo')=='BLINDING_GAZE_SOLAR' for e in aboleth['efeitos']):
                        aboleth['efeitos'].append({'tipo':'BLINDING_GAZE_SOLAR','fonte':SOLAR,
                            'duracao_fonte':'1 minuto', 'expiracao':'PENDENTE_CONTROLE_TEMPO_SRD'})
                    v['cegueira_minuto_pendente'] = True
                solar['recursos']['blinding_gaze_ja_usado_desde_ultimo_turno'] = True
                outcome = {'habilidade':action,'d20':roll,'bonus_con':6,'total':total,'cd':25,
                    'falhou':failed,'usou_resistencia_lendaria':opt,
                    'restantes_resistencia_aboleth':aboleth['recursos']['resistencia_lendaria_restante'],
                    'Blinded_aplicado':blindness,'duracao':'1 minuto',
                    'dados_simulados':True}
            elif actor=='J2' and action=='Lash':
                if params.get('alvo_valido_fixture') is not True:
                    raise UnresolvedRule('alvo valida e atingivel precisa ser confirmado')
                blind = 'Blinded' in aboleth['condicoes']
                rolls = params.get('ataque_d20_simulados')
                n = 2 if blind else 1
                if not isinstance(rolls,list) or len(rolls)!=n or not all(self._die(d,20) for d in rolls):
                    raise InvalidAction(f'rolagem do ataque exige {n} d20')
                applied_roll = min(rolls) if blind else rolls[0]
                crit = applied_roll==20
                hit = crit or (applied_roll!=1 and applied_roll+9>=21)
                dice = params.get('dano_d6_simulados',[])
                needed = 4 if crit and hit else (2 if hit else 0)
                if not isinstance(dice,list) or len(dice)!=needed or not all(self._die(d,6) for d in dice):
                    raise InvalidAction('dados de Tentacle invalidos para acerto/critico')
                damage = sum(dice)+5 if hit else 0
                old=solar['pv_atual'];solar['pv_atual']=max(0,old-damage)
                if hit:
                    if 'Grappled' not in solar['condicoes']:solar['condicoes'].append('Grappled')
                    if not any(e.get('tipo')=='TENTACLE_ABOLETH' for e in solar['efeitos']):
                        solar['efeitos'].append({'tipo':'TENTACLE_ABOLETH','fonte':ABOLETH,
                            'escape_dc':14,'limite_tentaculos_fonte':4,'dissipacao':'PENDENTE_SRD'})
                outcome = {'habilidade':action, 'ataque':'Tentacle', 'd20':rolls,
                    'modo':'DESVANTAGEM' if blind else 'NORMAL','d20_aplicado':applied_roll,
                    'bonus_ataque':9,'ca_alvo':21,'acerto':hit,'critico':crit,
                    'dados_dano':dice, 'dano':damage, 'pv_antes':old,'pv_depois':solar['pv_atual'],
                    'Grappled_aplicado':hit,'dados_simulados':True}
            else:
                raise UnresolvedRule('habilidade lendaria nao integrada para a criatura declarada')
            source['recursos']['acoes_lendarias_restantes'] -= 1
            w['utilizada'] = True
            outcome['usos_lendarios_restantes'] = source['recursos']['acoes_lendarias_restantes']
            outcome['fonte'] = 'SRD 5.2.1 pp.258/326-327'
            if solar['pv_atual'] == 0:
                self._ko(s, 'J2', 'SRD_LASH_ABOLETH_V26_PARCIAL')
                outcome['ko'] = True
            else:outcome['ko'] = False
            return outcome
        if command == 'REAÇÃO_V26_TESTE':
            self._combat(s)
            raise InvalidAction('Solar e Aboleth nao possuem Reactions declaradas nas fichas SRD usadas')
        if command == 'FINALIZAR_CEGUEIRA_V26_TESTE':
            v = self._combat(s)
            if actor!='ARBITRO':raise InvalidAction('controle de expiracao e do arbitro')
            if params.get('duracao_comprovada')!='1 minuto transcorrido':
                raise UnresolvedRule('expiracao exige comprovacao de um minuto, nao uma suposicao')
            _,aboleth=self._pair(s)
            effects=[e for e in aboleth['efeitos'] if e.get('tipo')=='BLINDING_GAZE_SOLAR']
            if not effects:raise InvalidAction('nenhum Blinding Gaze ativo')
            aboleth['efeitos']=[e for e in aboleth['efeitos'] if e.get('tipo')!='BLINDING_GAZE_SOLAR']
            if 'Blinded' in aboleth['condicoes'] and not any(e.get('tipo')=='BLINDING_GAZE_SOLAR' for e in aboleth['efeitos']):
                aboleth['condicoes'].remove('Blinded')
            v['cegueira_minuto_pendente']=False
            return {'efeito_expirado':'Blinding Gaze', 'controle_temporal':params['duracao_comprovada']}
        return super()._transition(s, actor, command, params)

    def public(self):
        data=super().public();s=self.state
        for p in SIDES:
            cid=s['jogadores'][p]['criatura_ativa_id']
            if cid:
                c=self.get_card(s,p,cid)
                data['jogadores'][p]['campo']={'id':cid,'nome':c['nome'],'pv_atual':c['pv_atual'],
                    'pv_max':c['pv_max'],'condicoes':copy.deepcopy(c['condicoes']),
                    'recursos_publicos':copy.deepcopy(c['recursos']), 'efeitos':copy.deepcopy(c['efeitos'])}
            else:data['jogadores'][p]['campo']=None
        if s['fase']=='COMBATE' and 'v26' in s['combate']:
            data['janela_lendaria']=copy.deepcopy(s['combate']['v26']['janela_lendaria'])
        data['dados_sao_simulados']=True
        return data

    def checkpoint(self):
        cp=super().checkpoint();cp['schema']='POC_MOTOR_LENDARIAS_V2_6_TESTE';return cp

    @classmethod
    def restore(cls,checkpoint,records):
        if checkpoint.get('schema')!='POC_MOTOR_LENDARIAS_V2_6_TESTE':
            raise CorruptedCheckpoint('schema v2.6 invalido')
        cp=copy.deepcopy(checkpoint);cp['schema']='POC_MOTOR_CHECKPOINT_V2_2_TESTE'
        return super().restore(cp,records)
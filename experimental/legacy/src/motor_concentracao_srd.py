"""SRD Card Game v2.7: Deva's Detect Evil and Good, concentration fixture.

Extends the v2.6 opportunity-attack fixture, never the official match.
Only Deva's SRD 5.2.1 at-will Detect Evil and Good is castable here.
External damage is explicitly injected AFTER hypothetical damage resolution;
this module does not claim to implement an attack by the Mouther.
"""
from __future__ import annotations
import copy
from motor_reacoes_srd import MotorReacoesSRD, DEVA, MOUTH
from motor_base_v22 import InvalidAction, UnresolvedRule, CorruptedCheckpoint

SCOPE_CONCENTRACAO = 'DEVA_DETECT_EVIL_GOOD_V27_FIXTURE'
SPELL = 'Detect Evil and Good'
SOURCE = 'SRD 5.2.1: Concentration glossary; Detect Evil and Good; Deva'
DURATION_ROUNDS = 100  # Ten minutes / six seconds per combat round.


class MotorConcentracaoSRD(MotorReacoesSRD):
    def validate(self, s=None):
        super().validate(s)
        s = self.state if s is None else s
        v = s['combate'].get('v27')
        if v is not None:
            assert v['modelo'] == 'DEVA_DETECT_EVIL_GOOD_CONCENTRACAO'
            assert type(v['conjuracoes']) is int and v['conjuracoes'] >= 0
            assert type(v['finalizacoes']) is int and v['finalizacoes'] >= 0
            active = v['concentracao']
            if active is not None:
                assert s['fase'] in ('COMBATE', 'POS_COMBATE', 'ENCERRADA')
                assert s['jogadores']['J1']['criatura_ativa_id'] == DEVA
                assert active['magia'] == SPELL and active['conjurador'] == 'J1'
                assert active['duracao_max_rodadas'] == DURATION_ROUNDS
                assert type(active['rodadas_decorridas']) is int
                assert 0 <= active['rodadas_decorridas'] < DURATION_ROUNDS
                assert type(active['turno_deva_conjuracao']) is int and active['turno_deva_conjuracao'] > 0
                assert active['turno_deva_conjuracao'] <= s['combate']['v25']['turnos']['J1']
        return True

    def _end(self, v, reason):
        previous = v['concentracao']
        v['concentracao'] = None
        v['finalizacoes'] += 1
        return {'concentracao_encerrada': True, 'motivo': reason,
                'magia_anterior': previous['magia']}

    def _transition(self, s, actor, command, params):
        v = s['combate'].get('v27')
        if command == 'INICIATIVA_DEVA_V25_TESTE':
            if v is not None and v['concentracao'] is not None:
                raise UnresolvedRule('concentracao preexistente exige passagem de tempo entre combates validada')
            result = super()._transition(s, actor, command, params)
            s['combate']['v27'] = {'modelo': 'DEVA_DETECT_EVIL_GOOD_CONCENTRACAO',
                                    'concentracao': None, 'conjuracoes': 0, 'finalizacoes': 0}
            return {**result, 'extensao_v27': 'CONCENTRACAO_DISPONIVEL_APENAS_DEVA'}

        if command == 'CONJURAR_DETECT_EVIL_GOOD_DEVA_V27_TESTE':
            if actor != 'J1' or v is None:
                raise InvalidAction('conjuracao disponivel somente ao Deva em combate fixture')
            turn = self._turn(s, actor)
            if turn['inicio_pendente'] or not turn['inicio_resolvido']:
                raise InvalidAction('turno do Deva nao iniciado')
            if turn['acao_utilizada']:
                raise InvalidAction('acao principal do Deva ja usada')
            if params != {'aceite_escopo': SCOPE_CONCENTRACAO, 'magia': SPELL,
                          'barreira_bloqueante_confirmada': False}:
                raise UnresolvedRule('magia e ausencia de barreira devem ser confirmadas na fixture')
            if s['combate']['v26']['distancia_ft'] not in (5, 10):
                raise UnresolvedRule('distancia nao confirmada')
            replaced = None
            if v['concentracao'] is not None:
                replaced = self._end(v, 'SUBSTITUIDA_POR_NOVA_CONJURACAO')
            v['conjuracoes'] += 1
            v['concentracao'] = {'magia': SPELL, 'conjurador': 'J1',
                'duracao_max_rodadas': DURATION_ROUNDS, 'rodadas_decorridas': 0,
                'turno_deva_conjuracao': turn['turnos']['J1']}
            turn['acao_utilizada'] = True
            return {'magia': SPELL, 'categoria_acao': 'ACTION', 'concentracao_ativa': True,
                    'conjuracao_at_will': True, 'conjuracoes_total': v['conjuracoes'],
                    'substituicao': replaced, 'deteccao': {'tipo': 'Aberration',
                        'alvo_id': MOUTH, 'distancia_ft': s['combate']['v26']['distancia_ft'],
                        'dentro_de_30_ft': True, 'barreira_bloqueante_confirmada': False},
                    'fonte': SOURCE, 'fixture': True}

        if command == 'ENCERRAR_CONCENTRACAO_DEVA_V27_TESTE':
            # SRD: voluntary termination at any time, no action; also during
            # the other creature's turn or a pending opportunity reaction.
            if actor != 'J1' or v is None or s['fase'] not in ('COMBATE', 'POS_COMBATE', 'ENCERRADA'):
                raise InvalidAction('somente o conjurador pode terminar sua concentracao')
            if s['jogadores']['J1']['criatura_ativa_id'] != DEVA:
                raise InvalidAction('Deva nao esta ativo para encerrar concentracao')
            if params != {'aceite_escopo': SCOPE_CONCENTRACAO}:
                raise UnresolvedRule('escopo de concentracao nao confirmado')
            if v['concentracao'] is None:
                raise InvalidAction('nao ha concentracao ativa')
            return {**self._end(v, 'VOLUNTARIA_SEM_ACAO'), 'custo_acao': 'NENHUM'}

        if command == 'DANO_EXTERNO_DEVA_V27_FIXTURE':
            # Damage is externally adjudicated fixture data, not a new SRD attack.
            # Reject lethal damage: KO/injury status is outside this increment.
            if actor != 'ARBITRO' or v is None or s['fase'] != 'COMBATE':
                raise InvalidAction('somente arbitro pode declarar dano fixture')
            self._pair(s)
            if s['combate']['v26']['pendencia_reacao'] is not None:
                raise InvalidAction('resolver primeiro movimento e reacao pendentes')
            if params.get('aceite_escopo') != SCOPE_CONCENTRACAO or params.get('origem') != 'DANO_EXTERNO_JA_RESOLVIDO_FIXTURE':
                raise UnresolvedRule('dano deve ser previamente resolvido e explicitamente artificial')
            if params.get('tipo_dano') != 'CONTUNDENTE' or params.get('resistencia_aplicavel') is not False:
                raise UnresolvedRule('fixture so cobre dano contundente sem resistencia')
            damage = params.get('dano_efetivo')
            card = self.get_card(s, 'J1', DEVA)
            if type(damage) is not int or not 1 <= damage < card['pv_atual']:
                raise InvalidAction('dano fixture positivo e nao letal obrigatorio')
            roll = params.get('constituicao_d20_simulado')
            if v['concentracao'] is None:
                if 'constituicao_d20_simulado' in params:
                    raise InvalidAction('nao rolar salvaguarda sem concentracao')
            elif not self._die(roll, 20):
                raise InvalidAction('salvaguarda CON d20 simulada obrigatoria')
            if set(params) != ({'aceite_escopo', 'origem', 'tipo_dano', 'resistencia_aplicavel', 'dano_efetivo'} |
                                ({'constituicao_d20_simulado'} if v['concentracao'] is not None else set())):
                raise InvalidAction('campos extras ou ausentes no dano fixture')
            before = card['pv_atual']; card['pv_atual'] -= damage
            outcome = {'fixture_artificial': True, 'tipo_dano': 'CONTUNDENTE',
                       'dano_efetivo': damage, 'pv_antes': before, 'pv_depois': card['pv_atual'],
                       'concentracao_teste': None}
            if v['concentracao'] is not None:
                dc = min(30, max(10, damage // 2))
                total = roll + 4  # Deva CON save +4 in SRD 5.2.1.
                success = total >= dc  # Natural 1/20 are not auto fail/success for saves.
                outcome['concentracao_teste'] = {'d20_simulado': roll, 'bonus_con': 4,
                                                'total': total, 'cd': dc, 'sucesso': success}
                if not success:
                    outcome['encerramento'] = self._end(v, 'FALHA_SALVAGUARDA_CONSTITUICAO')
            return outcome

        if command == 'INICIO_TURNO_DEVA_V25_TESTE':
            result = super()._transition(s, actor, command, params)
            if actor == 'J1' and v is not None and v['concentracao'] is not None:
                c = v['concentracao']
                if s['combate']['v25']['turnos']['J1'] > c['turno_deva_conjuracao']:
                    c['rodadas_decorridas'] += 1
                    if c['rodadas_decorridas'] >= DURATION_ROUNDS:
                        result['encerramento_concentracao'] = self._end(v, 'DURACAO_MAXIMA_10_MINUTOS')
                    else:
                        result['concentracao_rodadas_decorridas'] = c['rodadas_decorridas']
            return result

        return super()._transition(s, actor, command, params)

    def public(self):
        result = super().public()
        v = self.state['combate'].get('v27')
        if v is not None:
            result['concentracao_v27'] = {'deva': copy.deepcopy(v['concentracao']),
                                          'conjuracoes_total': v['conjuracoes'],
                                          'encerramentos_total': v['finalizacoes']}
        return result

    def checkpoint(self):
        p = super().checkpoint()
        p['schema'] = 'POC_MOTOR_CONCENTRACAO_V2_7_TESTE'
        return p

    @classmethod
    def restore(cls, checkpoint, records):
        if checkpoint.get('schema') != 'POC_MOTOR_CONCENTRACAO_V2_7_TESTE':
            raise CorruptedCheckpoint('schema de checkpoint v2.7 invalido')
        p = copy.deepcopy(checkpoint)
        p['schema'] = 'POC_MOTOR_REACOES_V2_6_TESTE'
        return super().restore(p, records)
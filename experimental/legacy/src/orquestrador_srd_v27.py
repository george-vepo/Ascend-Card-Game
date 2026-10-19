"""SRD Card Game POC v2.7: one event/checkpoint API for bounded SRD fixtures.

Four independently verified mechanical slices share the same event-sourced state
contract.  This is NOT a merger into a complete D&D 5.2.1 combat resolver.
It NEVER initializes, shuffles, changes, or claims to represent an official match.
"""
from __future__ import annotations
import copy
from typing import Mapping
from motor_base_v22 import InvalidAction, CorruptedCheckpoint, UnresolvedRule, digest
from motor_condicoes_srd import MotorCondicoesSRD
from motor_magias_srd import MotorMagiasSRD
from motor_reacoes_srd import MotorReacoesSRD
from motor_lendarias_srd import MotorLendariasSRD

PROFILES = {
    'OWL_MOUTH_CONDITIONS': {'engine': MotorCondicoesSRD, 'pair': ('CE-001', 'AB-POC-008'),
                             'features': ('ataques', 'Gibbering', 'Blinding Spittle', 'Blinded', 'recarga')},
    'DEVA_MOUTH_MAGIC': {'engine': MotorMagiasSRD, 'pair': ('CE-026','AB-POC-008'),
                         'features': ('Holy Mace x2', 'Divine Aid: Cure Wounds', 'turnos')},
    'DEVA_MOUTH_REACTION': {'engine': MotorReacoesSRD, 'pair': ('CE-026','AB-POC-008'),
                            'features': ('Holy Mace x2', 'Divine Aid: Cure Wounds',
                                         'ataque de oportunidade', 'Disengage', 'posicao limitada')},
    'SOLAR_ABOLETH_LEGENDARY': {'engine': MotorLendariasSRD, 'pair': ('CE-039','AB-POC-031'),
                                 'features': ('Blinding Gaze', 'Lash', 'resistencia lendaria')},
}
SCHEMA = 'POC_ORQUESTRADOR_SRD_V2_7_FIXTURE'
PUBLIC_COMMANDS = frozenset({
    'INICIATIVA_SRD_TESTE','INICIO_TURNO_V24_TESTE','ATAQUE_V24_TESTE',
    'BLINDING_SPITTLE_V24_TESTE','PASSAR_TURNO_V24_TESTE',
    'INICIATIVA_DEVA_V25_TESTE','FERIMENTO_DEVA_V25_FIXTURE','INICIO_TURNO_DEVA_V25_TESTE',
    'DIVINE_AID_CURE_WOUNDS_V25_TESTE','MULTIATTACK_HOLY_MACE_V25_TESTE',
    'ENCERRAR_TURNO_DEVA_V25_TESTE','CONFIGURAR_DISTANCIA_V26_FIXTURE',
    'DESENGAJAR_MOUTH_V26_TESTE','MOVIMENTO_MOUTH_V26_TESTE',
    'REAGIR_OPORTUNIDADE_DEVA_V26_TESTE','RECUSAR_OPORTUNIDADE_DEVA_V26_TESTE',
    'INICIATIVA_LENDARIAS_V26_TESTE','INICIAR_TURNO_V26_TESTE',
    'ENCERRAR_TURNO_V26_TESTE','USAR_LENDARIA_V26_TESTE','FINALIZAR_CEGUEIRA_V26_TESTE',
})

class OrquestradorSRD27:
    def __init__(self, registros, perfil: str, *, first='J1', hands=None,
                 match_id='SRD-V27-TESTE-ISOLADO', test_fixture=True):
        if test_fixture is not True:
            raise InvalidAction('somente testes: nenhuma partida oficial autorizada')
        if perfil not in PROFILES:
            raise InvalidAction('perfil de combate nao implementado e nao pode ser presumido')
        if not isinstance(registros, list):
            raise InvalidAction('registros precisam ser lista de cartas de fixture')
        self.perfil=perfil
        self.hash_registros=digest(registros)
        self._motor=PROFILES[perfil]['engine'](registros, first=first, hands=hands,
                                               match_id=match_id, test_fixture=True)

    @property
    def state(self):
        """Administrative/test-only state; do not expose this to a shared table."""
        return self._motor.state

    @property
    def events(self):
        """Administrative log; includes hidden hand choices in some event payloads."""
        return self._motor.events

    def apply(self, event_id, actor, command, params=None):
        """One atomic decision. Unsupported mechanics are rejected by the module."""
        if not isinstance(command,str) or not command:
            raise InvalidAction('comando invalido')
        return self._motor.apply(event_id, actor, command, params)

    def validate(self):
        return self._motor.validate()

    def public(self):
        data=self._motor.public()
        data['tipo_motor']='ORQUESTRADOR_V2_7_FIXTURE'
        data['perfil']=self.perfil
        data['habilidades_parciais']=list(PROFILES[self.perfil]['features'])
        data['mecanicas_ausentes_podem_bloquear_resolucao']=True
        data['partida_oficial']=False
        data['escopo_espacial']='ESTUDO_SRD_INCOMPATIVEL_COM_POC_SEM_MOVIMENTACAO' if self.perfil=='DEVA_MOUTH_REACTION' else 'SEM_MOVIMENTO_IMPLEMENTADO'
        return data

    def private(self, player):
        if player not in ('J1','J2'):
            raise InvalidAction('jogador inexistente')
        data=self._motor.private(player)
        data['perfil']=self.perfil
        data['partida_oficial']=False
        return data

    def public_history(self):
        """Only public combat events: no params, reserve/draw/hand/card order."""
        return [
          {'evento_id':e['evento_id'], 'versao':e['estado_novo'],
           'ator':e['autor'], 'comando':e['acao'],
           'resultado':copy.deepcopy(e['resultado']), 'hash_evento':e['hash_evento']}
          for e in self._motor.events if e['acao'] in PUBLIC_COMMANDS
        ]

    def checkpoint_private(self):
        """SENSITIVE: contains both hands and the exact deck order. Store privately."""
        module=self._motor.checkpoint()
        envelope={'schema':SCHEMA, 'perfil':self.perfil,
                  'hash_registros':self.hash_registros,'unicamente_teste':True,
                  'checkpoint_modulo':module}
        envelope['integridade_sha256']=digest(envelope)
        return envelope

    @classmethod
    def restore_private(cls, envelope, registros):
        if not isinstance(envelope,dict):
            raise CorruptedCheckpoint('checkpoint ausente ou malformado')
        copy_cp=copy.deepcopy(envelope)
        checksum=copy_cp.pop('integridade_sha256',None)
        if checksum!=digest(copy_cp):
            raise CorruptedCheckpoint('conteudo do envelope foi alterado')
        if copy_cp.get('schema')!=SCHEMA or copy_cp.get('unicamente_teste') is not True:
            raise CorruptedCheckpoint('somente envelope de teste v2.7')
        profile=copy_cp.get('perfil')
        if profile not in PROFILES:
            raise CorruptedCheckpoint('perfil desconhecido')
        if digest(registros)!=copy_cp.get('hash_registros'):
            raise CorruptedCheckpoint('fonte de cartas divergente do fixture salvo')
        eng=PROFILES[profile]['engine'].restore(copy_cp['checkpoint_modulo'],registros)
        item=cls.__new__(cls)
        item.perfil=profile
        item.hash_registros=digest(registros)
        item._motor=eng
        item.validate()
        return item

    def public_snapshot(self):
        return {'mesa':self.public(),'historico_combate':self.public_history(),
                'quantidade_eventos_aceitos':len(self._motor.events),
                'quantidade_comandos_rejeitados_ou_pendentes':len(self._motor.rejections),
                'nao_contem_checkpoint_ou_maos_ocultas':True}
"""POC v2.3: resolution of *isolated* SRD attack checks against a test fixture.

NOT a full SRD combat implementation, NOT an official match. Passive/triggered
features, spells, reaction economy, positioning and special abilities are not
adjudicated here. Authoritative statblocks for two creatures are cited below.
All dice are externally supplied *simulation fixtures*, NEVER claimed random.
"""
from __future__ import annotations
import copy
from typing import Any
from motor_base_v22 import MotorPOC, InvalidAction, UnresolvedRule, CorruptedCheckpoint, SIDES, other, digest

# Verified against SRD_CC_v5.2.1.pdf, printed pp. 352, 288, and rules pp. 7, 13, 16.
# No inference of other powers or attacks: nonlisted abilities are deliberately NOT usable.
VERIFIED_SRD = {
    "CE-001": {
        "name": "Giant Owl", "source": "SRD 5.2.1 p.352", "ac": 12, "hp": 19,
        "initiative": 2, "size": "Large", "resistances": ["Necrotic", "Radiant"],
        "immunities": [], "attack": {"name": "Talons", "bonus": 4,
            "dice": (1,10), "flat": 2, "type": "Slashing"},
        "limitations": ["Flyby nao implementado", "Spellcasting nao implementado"]
    },
    "AB-POC-008": {
        "name": "Gibbering Mouther", "source": "SRD 5.2.1 p.288", "ac": 9,
        "hp": 52, "initiative": -1, "size": "Medium", "resistances": [],
        "immunities": ["Prone"],
        "attack": {"name": "Bite", "bonus": 2,
            "dice": (2,6), "flat": 0, "type": "Piercing"},
        "limitations": ["Gibbering (passivo) nao implementado", "Aberrant Ground nao implementado", "Blinding Spittle nao implementado"]
    }
}

class MotorCombateSRD(MotorPOC):
    """Extends v2.2 without relaxing its 40-card conservation or privacy."""

    def _get_combat_pair(self, s):
        members={}
        for p in SIDES:
            cid=s['jogadores'][p]['criatura_ativa_id']
            if cid not in VERIFIED_SRD:
                raise UnresolvedRule(f"ficha/ataque SRD ainda nao integrado para ativa de {p}: {cid}")
            card=self.get_card(s,p,cid)
            block=VERIFIED_SRD[cid]
            if card['nome'].lower()!=block['name'].lower() or card['pv_max']!=block['hp']:
                raise UnresolvedRule(f"divergencia de identidade/PV com SRD: {cid}")
            if card['condicoes'] or card['efeitos']:
                raise UnresolvedRule("condicoes/efeitos existentes exigem resolucao adicional antes do ataque isolado")
            members[p]=(cid,block)
        if set(members)!=set(SIDES):raise InvalidAction("combate exige duas criaturas")
        return members

    @staticmethod
    def _d20(v):
        return type(v) is int and 1<=v<=20

    def _transition(self,s,actor,command,params):
        if command=='INICIATIVA_SRD_TESTE':
            if actor!='ARBITRO':raise InvalidAction('iniciativa e ato de arbitragem')
            if s['situacao']!='EM_ANDAMENTO' or s['fase']!='INICIATIVA':
                raise InvalidAction('iniciativa fora da fase')
            members=self._get_combat_pair(s)
            rolls=params.get('d20')
            if not isinstance(rolls,dict) or set(rolls)!=set(SIDES) or not all(self._d20(v) for v in rolls.values()):
                raise InvalidAction('iniciativa simulada exige um d20 de 1 a 20 por jogador')
            totals={p:rolls[p]+members[p][1]['initiative'] for p in SIDES}
            if totals['J1']==totals['J2']:
                raise UnresolvedRule('empate de iniciativa sem desempate aprovado na POC')
            order=sorted(SIDES,key=lambda p:totals[p],reverse=True)
            s['combate']['iniciativas']={**totals,'origem':'DADOS_SIMULADOS_TESTE',
                'rolagens':copy.deepcopy(rolls), 'modificadores':{p:members[p][1]['initiative'] for p in SIDES}}
            s['combate']['ordem_turnos']=order
            s['combate']['indice_turno']=0
            s['combate']['rodada']=1
            s['combate']['mecanicas_nao_implementadas']={p:members[p][1]['limitations'] for p in SIDES}
            s['fase']='COMBATE'
            s['ator_da_vez']=order[0]
            return {'rodada':1, 'ordem':order, 'd20_simulados':rolls, 'totais':totals,
                    'escopo':'APENAS_TESTE_DE_ATAQUE_ISOLADO_SEM_PASSIVOS',
                    'mecanicas_nao_implementadas':s['combate']['mecanicas_nao_implementadas']}

        if command=='ATAQUE_SRD_TESTE':
            if actor not in SIDES:raise InvalidAction('ataque deve ser declarado pelo controlador')
            self._gate(s,'COMBATE',actor)
            if s['combate']['iniciativas'].get('origem')!='DADOS_SIMULADOS_TESTE':
                raise InvalidAction('ataque mecanico exige iniciativa SRD simulada deste modulo')
            if params.get('aceite_escopo')!='ATAQUE_ISOLADO_SEM_PASSIVOS':
                raise UnresolvedRule('teste parcial exige confirmar explicitamente passivos nao implementados')
            members=self._get_combat_pair(s)
            cid,block=members[actor]
            attack=block['attack']
            if params.get('ataque')!=attack['name']:
                raise InvalidAction('ataque nao documentado para a criatura ativa')
            d20=params.get('d20')
            if not self._d20(d20):raise InvalidAction('d20 simulado invalido')
            opp=other(actor); target_id,target=members[opp]
            bonus=attack['bonus'];total=d20+bonus
            critical=d20==20;hit=(critical or (d20!=1 and total>=target['ac']))
            count=attack['dice'][0]*(2 if critical else 1) if hit else 0
            damage_dice=params.get('dano_dados',[])
            if (not isinstance(damage_dice,list) or len(damage_dice)!=count or
                not all(type(n) is int and 1<=n<=attack['dice'][1] for n in damage_dice)):
                raise InvalidAction(f'dano simulado exige exatamente {count} dados d{attack["dice"][1]} validos')
            base_damage=sum(damage_dice)+attack['flat'] if hit else 0
            # For this limited pair, neither has resistance/immunity to the other's attack type.
            if attack['type'] in target['resistances'] or attack['type'] in target['immunities']:
                raise UnresolvedRule('resistencia/imunidade a dano exige resolucao separada')
            victim=self.get_card(s,opp,target_id)
            before=victim['pv_atual'];after=max(0,before-base_damage)
            victim['pv_atual']=after
            outcome={'atacante':actor,'alvo':opp,'carta_origem':cid,'carta_alvo':target_id,
                     'fonte':block['source'],'ataque':attack['name'],
                     'd20_simulado':d20,'bonus':bonus,'total':total,'ca_alvo':target['ac'],
                     'acertou':hit,'critico':critical,'dados_dano_simulados':damage_dice,
                     'modificador_dano':attack['flat'] if hit else 0,
                     'dano_total':base_damage,'pv_antes':before,'pv_depois':after,
                     'mecanica_parcial':True}
            # Bite's Prone affects Medium or smaller only; Giant Owl is Large. Never assume Prone.
            if attack['name']=='Bite':
                outcome['prone_aplicado']=False
                outcome['motivo_sem_prone']='Alvo Giant Owl e Large (SRD p.352); Bite exige Medium ou menor (p.288)'
            if after==0:
                self._ko(s,actor,'TESTE_SRD_ATAQUE_ISOLADO_COM_PASSIVOS_PENDENTES')
                outcome['ko']=True;outcome['pontuacao_fixture']=copy.deepcopy(s['placar'])
            else:
                order=s['combate']['ordem_turnos'];index=s['combate']['indice_turno']
                if order[index]!=actor:raise InvalidAction('indice de turno inconsistente')
                if index==0:
                    s['combate']['indice_turno']=1
                    s['ator_da_vez']=order[1]
                else:
                    s['combate']['indice_turno']=0
                    s['combate']['rodada']+=1
                    s['ator_da_vez']=order[0]
                outcome['ko']=False;outcome['proximo_ator']=s['ator_da_vez']
                outcome['proxima_rodada']=s['combate']['rodada']
            return outcome
        return super()._transition(s,actor,command,params)

    def public(self):
        result=super().public();s=self.state
        for p in SIDES:
            cid=s['jogadores'][p]['criatura_ativa_id']
            if cid:
                c=s['jogadores'][p]['cartas'][cid]
                result['jogadores'][p]['campo']={'carta_id':cid,'nome':c['nome'],
                    'pv_atual':c['pv_atual'],'pv_max':c['pv_max'],'condicoes':copy.deepcopy(c['condicoes'])}
            else:result['jogadores'][p]['campo']=None
        result['combatente_da_vez']=s['ator_da_vez'] if s['fase']=='COMBATE' else None
        result['rolagens_sao_simuladas']=True
        return result

    def checkpoint(self):
        out=super().checkpoint();out['schema']='POC_MOTOR_COMBATE_V2_3_TESTE'
        return out

    @classmethod
    def restore(cls,checkpoint,records):
        if checkpoint.get('schema')!='POC_MOTOR_COMBATE_V2_3_TESTE':
            raise CorruptedCheckpoint('schema de checkpoint mecanico invalido')
        cp=copy.deepcopy(checkpoint);cp['schema']='POC_MOTOR_CHECKPOINT_V2_2_TESTE'
        obj=super().restore(cp,records)
        return obj
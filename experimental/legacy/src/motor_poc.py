"""SRD Card Game — experimental event-sourced POC engine (v2.2).

Does NOT shuffle, roll dice, simulate ability mechanics, or create a real match.
All action outcomes used in tests are explicitly fixture-provided and labeled.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

RANKS = ["Comum", "Incomum", "Rara", "Lendária", "Mítica"]
ZONES = {"MONTE", "MAO", "CAMPO", "CEMITERIO"}
SIDES = ("J1", "J2")

class InvalidAction(Exception): pass
class UnresolvedRule(Exception): pass
class CorruptedCheckpoint(Exception): pass

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()

def other(p):
    return "J2" if p == "J1" else "J1"

class MotorPOC:
    """All mutable match state is this engine's isolated fixture state, never official."""
    def __init__(self, records, first="J1", hands=None, match_id="POC-ISOLADA-TESTE", test_fixture=True):
        if not test_fixture:
            raise InvalidAction("motor experimental exclusivo para fixtures de teste")
        if first not in SIDES: raise InvalidAction("prioridade invalida")
        self.record_source = copy.deepcopy(records)
        self.events = []
        self.rejections = []
        self.responses = {}
        self.head_hash = "GENESIS"
        self.state = {
            "partida_id": match_id, "versao": "E000", "situacao": "EM_ANDAMENTO", "fase": "TROCA",
            "prioridade_preparacao": {"primeiro": first, "segundo": other(first), "sorteio_realizado": False,
                                      "origem": "FIXTURE_DE_TESTE_SEM_SORTEIO", "ordem_fixa_ate_fim_do_duelo": True},
            "ator_da_vez": first, "placar": {"J1":0,"J2":0},
            "combate": {"numero": 1, "rodada":0, "iniciativas":{}, "resultado_mecanico":"NAO_CALCULADO"},
            "controle_saque_ciclo":{"ciclo_atual":1, "processados":[]},
            "jogadores":{}, "evento_ultimo_id":None,
            "avisos":["ESTADO FICTICIO: fixture sem embaralhamento, sem rolagens e sem jogo oficial"],
            "sequenciamento":{"troca": [], "criatura":[], "suporte":[], "resolucao":[]}
        }
        for p in SIDES:
            entries=[r for r in records if r['jogador']==p]
            if len(entries)!=40: raise InvalidAction(f"deck {p} nao tem 40 copias")
            card_ids=[r['id_copia_poc'] for r in entries]
            if len(set(card_ids))!=40:raise InvalidAction("ids duplicados")
            cards={}
            for r in entries:
                cid=r['id_copia_poc']
                value=r.get('pv_fonte')
                pvmax=int(value) if value is not None and str(value).isdecimal() else None
                cards[cid]={"copia_id":cid,"criatura_id":r.get("chave_controle_1320") or cid,
                            "nome":r['nome'],"tipo":r['tipo'],"raridade":r['raridade'],
                            "nd":r['nd'],"zona":"MONTE","suporte_reservado":False,
                            "pv_atual":None,"pv_max":pvmax,"condicoes":[],"recursos":{},"efeitos":[]}
            # FIXED deterministic input for testing only, not a real shuffle or simulated lottery.
            fixed_hand = hands.get(p) if hands else None
            if fixed_hand is None:
                fixed_hand=card_ids[:5]
            if len(fixed_hand)!=5 or len(set(fixed_hand))!=5 or not set(fixed_hand)<=set(card_ids):
                raise InvalidAction(f"mao de fixture invalida {p}")
            deck=[cid for cid in card_ids if cid not in fixed_hand]
            for cid in fixed_hand:cards[cid]['zona']="MAO"
            self.state['jogadores'][p]={"controlador":"HUMANO" if p=="J1" else "IA",
                "copia_ids_deck":card_ids,"cartas":cards,"monte_ordem_ids":deck,
                "suporte_reservado_id":None,"criatura_ativa_id":None}
        self.validate()

    def get_card(self,s,p,cid):
        if p not in SIDES:raise InvalidAction("jogador inexistente")
        c=s['jogadores'][p]['cartas'].get(cid)
        if not c:raise InvalidAction("carta nao pertence ao jogador")
        return c

    def hand(self,s,p):
        return [cid for cid,c in s['jogadores'][p]['cartas'].items() if c['zona']=='MAO']

    def _move(self,s,p,cid,dest):
        c=self.get_card(s,p,cid)
        if dest not in ZONES:raise InvalidAction("zona invalida")
        if c['zona']=="MONTE":
            s['jogadores'][p]['monte_ordem_ids'].remove(cid)
        c['zona']=dest

    def _draw(self,s,p,count):
        j=s['jogadores'][p]
        if len(self.hand(s,p))+count>5:raise InvalidAction("compra excederia cinco cartas")
        taken=[]
        for _ in range(count):
            if not j['monte_ordem_ids']:break
            cid=j['monte_ordem_ids'][0]
            self._move(s,p,cid,"MAO")
            taken.append(cid)
        return taken

    def validate(self,s=None):
        s=s or self.state
        pr=s['prioridade_preparacao']
        assert {pr['primeiro'],pr['segundo']}==set(SIDES)
        assert pr['ordem_fixa_ate_fim_do_duelo']
        for p in SIDES:
            j=s['jogadores'][p]; cs=j['cartas']
            assert len(cs)==len(j['copia_ids_deck'])==40
            assert len(set(j['copia_ids_deck']))==40
            assert set(cs)==set(j['copia_ids_deck'])
            assert len(self.hand(s,p))<=5
            assert all(c['zona'] in ZONES for c in cs.values())
            pile=j['monte_ordem_ids']
            assert len(pile)==len(set(pile)) and set(pile)=={cid for cid,c in cs.items() if c['zona']=="MONTE"}
            assert sum(c['zona']=="CAMPO" for c in cs.values())<=1
            active=j['criatura_ativa_id']
            if active:assert cs[active]['zona']=="CAMPO" and cs[active]['pv_atual'] is not None
            else:assert not any(c['zona']=="CAMPO" for c in cs.values())
            reserved=j['suporte_reservado_id']
            rs=[cid for cid,c in cs.items() if c['suporte_reservado']]
            assert rs==([reserved] if reserved else [])
            if reserved:assert cs[reserved]['zona']=="MAO"
            for c in cs.values():
                if c['pv_atual'] is not None:assert c['pv_max'] is not None and 0<=c['pv_atual']<=c['pv_max']
        assert all(isinstance(x,int) and 0<=x<=3 for x in s['placar'].values())
        pairs=[(x['ciclo'],x['jogador']) for x in s['controle_saque_ciclo']['processados']]
        assert len(pairs)==len(set(pairs))
        if s['situacao']=="ENCERRADA":assert 3 in s['placar'].values() and s['fase']=="ENCERRADA"
        return True

    def _gate(self,s,phase,actor):
        if s['situacao']=="ENCERRADA":raise InvalidAction("partida encerrada")
        if s['fase']!=phase:raise InvalidAction("fase incorreta")
        if s['ator_da_vez']!=actor:raise InvalidAction("fora da vez")

    def _finish_stage(self,s,kind,stage_next):
        first=s['prioridade_preparacao']['primeiro'];second=s['prioridade_preparacao']['segundo']
        order=s['sequenciamento'][kind]
        if order==[first]:s['ator_da_vez']=second
        elif order==[first,second]:
            s['fase']=stage_next;s['ator_da_vez']=first
        else:raise InvalidAction("sequenciamento inconsistente")

    def _ko(self,s,winner,source):
        if winner not in SIDES:raise InvalidAction("vencedor inexistente")
        loser=other(winner)
        losing=s['jogadores'][loser]
        if not losing['criatura_ativa_id'] or not s['jogadores'][winner]['criatura_ativa_id']:
            raise InvalidAction("KO exige ambas criaturas ativas")
        cid=losing['criatura_ativa_id'];c=losing['cartas'][cid]
        c['pv_atual']=0; self._move(s,loser,cid,'CEMITERIO');losing['criatura_ativa_id']=None
        for p in SIDES:
            j=s['jogadores'][p];r=j['suporte_reservado_id']
            if r:
                j['cartas'][r]['suporte_reservado']=False
                j['suporte_reservado_id']=None
        s['placar'][winner]+=1
        s['combate']['resultado_mecanico']=source
        s['combate']['iniciativas']={}
        s['ator_da_vez']=None
        if s['placar'][winner]==3:
            s['situacao']='ENCERRADA';s['fase']='ENCERRADA'
        else:
            s['fase']='POS_COMBATE'

    def _transition(self,s,actor,command,params):
        if command in {'TROCAR','PRONTO_CRIATURA','INVOCAR','EVOLUIR','ESCOLHER_SUPORTE'}:
            if actor not in SIDES:raise InvalidAction('acao requer jogador')
        elif actor!='ARBITRO':raise InvalidAction('comando de arbitragem nao pertence a jogador')

        if command=='TROCAR':
            self._gate(s,'TROCA',actor)
            order=s['sequenciamento']['troca'];first=s['prioridade_preparacao']['primeiro']
            if order!=[] and (order!=[first] or actor==first):raise InvalidAction('ja trocou')
            chosen=params.get('descartar',[])
            if not isinstance(chosen,list) or len(chosen)>5 or len(chosen)!=len(set(chosen)):
                raise InvalidAction('descarte invalido')
            if not set(chosen)<=set(self.hand(s,actor)):raise InvalidAction('descarte de carta fora da mao')
            if len(s['jogadores'][actor]['monte_ordem_ids'])<len(chosen):
                raise UnresolvedRule('monte insuficiente para troca; decisao administrativa pendente')
            for cid in chosen:self._move(s,actor,cid,'CEMITERIO')
            drawn=self._draw(s,actor,len(chosen))
            order.append(actor);self._finish_stage(s,'troca','INVOCACAO_EVOLUCAO')
            return {'descartadas':list(chosen),'compradas_count':len(drawn),'compradas_privadas':drawn}
        if command=='INVOCAR':
            self._gate(s,'INVOCACAO_EVOLUCAO',actor)
            j=s['jogadores'][actor];cid=params.get('carta_id');c=self.get_card(s,actor,cid)
            if j['criatura_ativa_id'] or c['zona']!='MAO' or c['raridade']!='Comum':raise InvalidAction('invocacao exige Comum na mao e campo vazio')
            if c['pv_max'] is None:raise UnresolvedRule('falta PV da criatura selecionada para entrar em campo')
            self._move(s,actor,cid,'CAMPO');j['criatura_ativa_id']=cid;c['pv_atual']=c['pv_max']
            return {'ativa':cid,'pv':c['pv_atual']}
        if command=='EVOLUIR':
            self._gate(s,'INVOCACAO_EVOLUCAO',actor)
            j=s['jogadores'][actor];old_id=j['criatura_ativa_id'];cid=params.get('carta_id')
            if not old_id:raise InvalidAction('sem criatura ativa para evoluir')
            old=self.get_card(s,actor,old_id);c=self.get_card(s,actor,cid)
            if c['zona']!='MAO' or old['tipo']!=c['tipo'] or RANKS.index(c['raridade'])!=RANKS.index(old['raridade'])+1:
                raise InvalidAction('evolucao exige mesma especie de tipo e classe adjacente')
            if c['pv_max'] is None:raise UnresolvedRule('PV ausente na evolucao')
            self._move(s,actor,old_id,'CEMITERIO')
            self._move(s,actor,cid,'CAMPO');j['criatura_ativa_id']=cid
            c['pv_atual']=c['pv_max'];return {'evoluiu_de':old_id,'evoluiu_para':cid}
        if command=='PRONTO_CRIATURA':
            self._gate(s,'INVOCACAO_EVOLUCAO',actor)
            if not s['jogadores'][actor]['criatura_ativa_id']:
                raise UnresolvedRule('preparacao sem criatura ativa; regra de impossibilidade pendente')
            s['sequenciamento']['criatura'].append(actor)
            self._finish_stage(s,'criatura','SELECAO_SUPORTE')
            return {'jogador':actor,'concluiu_preparacao':True}
        if command=='ESCOLHER_SUPORTE':
            self._gate(s,'SELECAO_SUPORTE',actor)
            j=s['jogadores'][actor];cid=params.get('carta_id')
            if j['suporte_reservado_id'] is not None:raise InvalidAction('suporte ja reservado')
            if cid is not None:
                c=self.get_card(s,actor,cid)
                if c['zona']!='MAO':raise InvalidAction('suporte deve estar na mao')
                j['suporte_reservado_id']=cid;c['suporte_reservado']=True
            s['sequenciamento']['suporte'].append(actor)
            self._finish_stage(s,'suporte','RESOLUCAO_SUPORTE_TESTE')
            return {'escolha':'SEM_SUPORTE' if cid is None else 'RESERVADO'}
        if command=='RESOLVER_SUPORTE_FIXTURE':
            self._gate(s,'RESOLUCAO_SUPORTE_TESTE',s['ator_da_vez'])
            player=s['ator_da_vez'];j=s['jogadores'][player]
            result=params.get('resultado')
            if result not in ('PULAR','EFEITO_NAO_LETAL_TESTE','KO_TESTE'):
                raise InvalidAction('resultado nao permitido')
            cid=j['suporte_reservado_id']
            if cid is None:
                if result!='PULAR':raise InvalidAction('nao ha suporte')
            else:
                if result=='PULAR':raise UnresolvedRule('suporte reservado nao pode ser ignorado automaticamente')
                if not params.get('comprovante_fixture'):
                    raise UnresolvedRule('efeito de suporte nao homologado; requer resultado explicito de teste')
                j['cartas'][cid]['suporte_reservado']=False
                j['suporte_reservado_id']=None
                self._move(s,player,cid,'CEMITERIO')
            s['sequenciamento']['resolucao'].append(player)
            if result=='KO_TESTE':
                if cid is None:raise InvalidAction('KO exige suporte')
                self._ko(s,player,'FIXTURE_KO_SUPORTE_NAO_MECANICO')
                return {'resultado':'KO_TESTE','primeiro_suporte_consumido':cid,'segundo_suporte_preservado':True}
            self._finish_stage(s,'resolucao','INICIATIVA')
            return {'resultado':result,'consumido':cid}
        if command=='INICIATIVA_FIXTURE':
            if s['fase']!='INICIATIVA':raise InvalidAction('fase de iniciativa incorreta')
            if not params.get('comprovante_fixture'):raise UnresolvedRule('iniciativa exige fonte ou fixture expresso')
            totals=params.get('totais')
            if not isinstance(totals,dict) or set(totals)!=set(SIDES) or not all(isinstance(x,int) for x in totals.values()):
                raise InvalidAction('totais invalidos')
            if totals['J1']==totals['J2']:
                raise UnresolvedRule('iniciativa empatada exige regra/tiebreak')
            s['combate']['iniciativas']={**totals,'origem':'FIXTURE_SEM_ROLAGEM'}
            s['combate']['rodada']=1;s['fase']='COMBATE';s['ator_da_vez']=None
            return {'iniciativa_fixture':totals}
        if command=='RODADA_SEGUINTE_FIXTURE':
            if s['fase']!='COMBATE':raise InvalidAction('nao esta em combate')
            s['combate']['rodada']+=1
            return {'rodada':s['combate']['rodada']}
        if command=='KO_COMBATE_FIXTURE':
            if s['fase']!='COMBATE':raise InvalidAction('KO fora de combate')
            if not params.get('comprovante_fixture'):
                raise UnresolvedRule('KO requer acao SRD resolvida ou fixture de teste')
            winner=params.get('vencedor')
            self._ko(s,winner,'FIXTURE_KO_COMBATE_NAO_MECANICO')
            return {'vencedor':winner,'placar':copy.deepcopy(s['placar'])}
        if command=='ABRIR_CICLO':
            if s['fase']!='POS_COMBATE':raise InvalidAction('nao pode abrir ciclo')
            s['combate']['numero']+=1;s['combate']['rodada']=0;s['combate']['iniciativas']={}
            cycle=s['combate']['numero'];s['controle_saque_ciclo']['ciclo_atual']=cycle
            drawn_count={}
            for p in SIDES:
                processed=s['controle_saque_ciclo']['processados']
                if any(x['ciclo']==cycle and x['jogador']==p for x in processed):raise InvalidAction('saque ja realizado')
                n=5-len(self.hand(s,p));drawn=self._draw(s,p,n);drawn_count[p]=len(drawn)
                processed.append({'ciclo':cycle,'jogador':p,'quantidade_comprada':len(drawn)})
            s['fase']='TROCA';s['ator_da_vez']=s['prioridade_preparacao']['primeiro']
            s['sequenciamento']={k:[] for k in ('troca','criatura','suporte','resolucao')}
            return {'ciclo':cycle,'repostos':drawn_count}
        raise InvalidAction('comando desconhecido')

    def apply(self,event_id,actor,command,params=None):
        params=copy.deepcopy(params or {})
        if not event_id or not isinstance(event_id,str):raise InvalidAction('evento_id invalido')
        proposal={'evento_id':event_id,'autor':actor,'acao':command,'parametros':params}
        fingerprint=digest(proposal)
        if event_id in self.responses:
            prev=self.responses[event_id]
            if prev['fingerprint']!=fingerprint:raise InvalidAction('colisao de evento_id com payload distinto')
            return copy.deepcopy(prev['result'])
        proposed=copy.deepcopy(self.state)
        try:
            outcome=self._transition(proposed,actor,command,params)
            self.validate(proposed)
        except (InvalidAction,UnresolvedRule) as exc:
            decision='PENDENTE' if isinstance(exc,UnresolvedRule) else 'REJEITADA'
            rejection={**proposal,'decisao':decision,'motivo':str(exc),
                       'versao_permanecida':self.state['versao'],'estado_hash':digest(self.state)}
            self.rejections.append(rejection)
            result={'decisao':decision,'motivo':str(exc),'versao':self.state['versao']}
            self.responses[event_id]={'fingerprint':fingerprint,'result':copy.deepcopy(result)}
            return result
        idx=len(self.events)+1;version=f'E{idx:03d}'
        proposed['versao']=version;proposed['evento_ultimo_id']=event_id
        event={**proposal,'decisao':'ACEITA','estado_base':self.state['versao'],
            'estado_novo':version,'resultado':outcome,'estado_apos_hash':digest(proposed),
            'encadeamento_anterior':self.head_hash}
        event['hash_evento']=digest(event)
        self.state=proposed;self.events.append(event);self.head_hash=event['hash_evento']
        result={'decisao':'ACEITA','versao':version,'resultado':copy.deepcopy(outcome)}
        self.responses[event_id]={'fingerprint':fingerprint,'result':copy.deepcopy(result)}
        return result

    def public(self):
        s=self.state
        return {'partida_id':s['partida_id'],'ambiente':'FIXTURE_ISOLADA',
            'fase':s['fase'],'situacao':s['situacao'],'ciclo':s['combate']['numero'],
            'rodada':s['combate']['rodada'],'ator_da_vez':s['ator_da_vez'],
            'placar':copy.deepcopy(s['placar']),'prioridade':copy.deepcopy(s['prioridade_preparacao']),
            'jogadores':{p:{'monte_quantidade':len(s['jogadores'][p]['monte_ordem_ids']),
                              'mao_quantidade':len(self.hand(s,p)),
                              'cemiterio_quantidade':sum(c['zona']=='CEMITERIO' for c in s['jogadores'][p]['cartas'].values()),
                              'criatura_ativa_id':s['jogadores'][p]['criatura_ativa_id']}
                              for p in SIDES}}

    def private(self,p):
        if p not in SIDES:raise InvalidAction('jogador invalido')
        result=self.public();j=self.state['jogadores'][p]
        result['minha_mao']=[{'id':cid,'nome':j['cartas'][cid]['nome'],
                             'reservado':j['cartas'][cid]['suporte_reservado']} for cid in self.hand(self.state,p)]
        return result

    def schema_projection(self):
        """Projection ONLY: validates against historical JSON schema; NOT a real official match.

        The prototype's intermediate support-resolution phase maps to the older
        schema's SELECAO_SUPORTE; its finer-grained subphase remains in engine state.
        """
        s=self.state
        phase='SELECAO_SUPORTE' if s['fase']=='RESOLUCAO_SUPORTE_TESTE' else s['fase']
        players={}
        for p in SIDES:
            j=s['jogadores'][p]
            cards=[]
            for c in j['cartas'].values():
                cards.append({key:copy.deepcopy(c[key]) for key in
                              ('copia_id','criatura_id','nome','zona','suporte_reservado','pv_atual','pv_max',
                               'condicoes','recursos','efeitos')})
            players[p]={key:copy.deepcopy(j[key]) for key in
                        ('controlador','copia_ids_deck','monte_ordem_ids','suporte_reservado_id','criatura_ativa_id')}
            players[p]['cartas']=cards
        priority=s['prioridade_preparacao']
        event_list=[]
        for e in self.events:
            event_list.append({k:copy.deepcopy(e[k]) for k in
                               ('evento_id','estado_base','estado_novo','autor','acao','decisao')})
        return {
            'partida_id':s['partida_id'],'versao':s['versao'],'situacao':s['situacao'],
            'fase':phase,'ator_da_vez':s['ator_da_vez'],'placar':copy.deepcopy(s['placar']),
            'prioridade_preparacao':{
                'primeiro':priority['primeiro'],'segundo':priority['segundo'],
                'sorteio_realizado':priority['sorteio_realizado'],'sorteio_evento_id':None,
                'ordem_fixa_ate_fim_do_duelo':True},
            'combate':copy.deepcopy(s['combate']),'jogadores':players,
            'controle_saque_ciclo':copy.deepcopy(s['controle_saque_ciclo']),
            'evento_ultimo_id':s['evento_ultimo_id'],'historico_eventos':event_list,
            'avisos':copy.deepcopy(s['avisos'])+[
              'APENAS ADAPTADOR DE SCHEMA PARA TESTE: nao equivale a partida oficial ou sorteio real.',
              'A fase RESOLUCAO_SUPORTE_TESTE do motor e exibida como SELECAO_SUPORTE no schema historico.']
        }

    def checkpoint(self):
        return {'schema':'POC_MOTOR_CHECKPOINT_V2_2_TESTE','state':copy.deepcopy(self.state),
                'eventos':copy.deepcopy(self.events),'rejeicoes':copy.deepcopy(self.rejections),
                'idempotencia':copy.deepcopy(self.responses),'hash_estado':digest(self.state),
                'ultimo_hash_evento':self.head_hash,'unicamente_teste':True}

    @classmethod
    def restore(cls,checkpoint,records):
        if checkpoint.get('schema')!='POC_MOTOR_CHECKPOINT_V2_2_TESTE' or checkpoint.get('unicamente_teste') is not True:
            raise CorruptedCheckpoint('nao e checkpoint de fixture autorizado')
        if checkpoint.get('hash_estado')!=digest(checkpoint.get('state')):
            raise CorruptedCheckpoint('hash do estado diverge')
        events=checkpoint.get('eventos',[]);head='GENESIS';version='E000'
        for i,e in enumerate(events,1):
            copied=copy.deepcopy(e);hashval=copied.pop('hash_evento',None)
            if hashval!=digest(copied) or copied.get('encadeamento_anterior')!=head:
                raise CorruptedCheckpoint('cadeia de eventos invalida')
            if copied.get('estado_base')!=version or copied.get('estado_novo')!=f'E{i:03d}':
                raise CorruptedCheckpoint('versao de evento fora da sequencia')
            head=hashval;version=copied['estado_novo']
        if head!=checkpoint.get('ultimo_hash_evento'):
            raise CorruptedCheckpoint('hash final invalido')
        if checkpoint['state']['versao']!=version:
            raise CorruptedCheckpoint('versao do estado inconsistente')
        if events and checkpoint['state']['evento_ultimo_id']!=events[-1]['evento_id']:
            raise CorruptedCheckpoint('ultimo evento inconsistente')
        engine=cls(records,first=checkpoint['state']['prioridade_preparacao']['primeiro'])
        engine.state=copy.deepcopy(checkpoint['state']);engine.events=copy.deepcopy(events)
        engine.rejections=copy.deepcopy(checkpoint.get('rejeicoes',[]))
        engine.responses=copy.deepcopy(checkpoint.get('idempotencia',{}));engine.head_hash=head
        engine.validate()
        expected={p:{r['id_copia_poc'] for r in records if r['jogador']==p} for p in SIDES}
        if any(set(engine.state['jogadores'][p]['cartas'])!=expected[p] for p in SIDES):
            raise CorruptedCheckpoint('deck divergente das fontes')
        return engine

    def write_artifacts(self,folder):
        folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
        def write_json(name,obj):
            (folder/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        write_json('checkpoint_fixture.json',self.checkpoint())
        write_json('mesa_publica_fixture.json',self.public())
        write_json('projecao_schema_fixture.json',self.schema_projection())
        for p in SIDES:write_json(f'visao_privada_{p}_fixture.json',self.private(p))
        for name,items in [('eventos_aceitos.jsonl',self.events),('acoes_rejeitadas_ou_pendentes.jsonl',self.rejections)]:
            (folder/name).write_text(''.join(json.dumps(i,ensure_ascii=False)+'\n' for i in items),encoding='utf-8')
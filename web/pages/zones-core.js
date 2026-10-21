/* Motor local experimental: 40 cópias em zonas, sem estado oficial ou backend. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.SRDZonesDemo=api;})(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SIDES=['J1','J2'],RARITY=['Comum','Incomum','Rara','Lendária','Mítica'];
 const phases=['TROCA','CRIATURA','SUPORTE','COMBATE_EXTERNO','POS_COMBATE','ENCERRADA'];
 const fail=msg=>{throw new Error(msg);};
 const cp=data=>JSON.parse(JSON.stringify(data));
 const opposite=s=>s==='J1'?'J2':'J1';
 const integer=v=>Number.isSafeInteger(v);
 function card(row){
   if(!row||typeof row.copiaId!=='string'||typeof row.catalogoId!=='string'||!row.nome||!row.tipo||!RARITY.includes(row.raridade))fail('Carta sem identidade canônica.');
   return {copiaId:row.copiaId,catalogoId:row.catalogoId,nome:row.nome,tipo:row.tipo,raridade:row.raridade,nd:row.nd,ca:row.ca,pvMax:row.pvMax,imagem:row.imagem||'',fichaUrl:row.fichaUrl||''};
 }
 function check(state){
   if(!state||state.ambiente!=='DEMO_LOCAL_NAO_OFICIAL'||!phases.includes(state.fase)||!integer(state.versao)||state.versao<0||!SIDES.includes(state.primeiro)||!SIDES.includes(state.vez)||![0,1].includes(state.subetapa)||!integer(state.combate)||state.combate<1)fail('Estado local inválido.');
   const all=new Set();
   for(const s of SIDES){
     const p=state.jogadores?.[s];
     if(!p||!Array.isArray(p.monte)||!Array.isArray(p.mao)||!Array.isArray(p.cemiterio)||p.campo===undefined)fail('Zona ausente para '+s);
     const group=[...p.monte,...p.mao,...p.cemiterio,...(p.campo?[p.campo]:[])];
     if(group.length!==40)fail('Total de cópias diferente de 40 para '+s);
     for(const c of group){
       card(c);
       if(all.has(c.copiaId))fail('Cópia duplicada entre zonas: '+c.copiaId);
       all.add(c.copiaId);
     }
     if(p.campo&&(!integer(p.campo.pvAtual)||p.campo.pvAtual<1||p.campo.pvAtual>p.campo.pvMax))fail('PV do campo inválidos para '+s);
     if(!integer(state.placar[s])||state.placar[s]<0||state.placar[s]>3)fail('Placar inválido.');
   }
   if(state.fase==='ENCERRADA'&&!SIDES.some(s=>state.placar[s]===3))fail('Partida encerrada sem três pontos.');
   if(state.fase!=='ENCERRADA'&&SIDES.some(s=>state.placar[s]===3))fail('Não continuar depois de três pontos.');
   if(state.fase==='COMBATE_EXTERNO'&&!SIDES.every(s=>state.jogadores[s].campo))fail('Combate sem duas criaturas.');
   return state;
 }
 function shuffle(cards,randomIndex){
   const data=cards.map(card);
   for(let i=data.length-1;i>0;i--){
     const j=randomIndex(i+1);
     if(!integer(j)||j<0||j>i)fail('Índice de embaralhamento inválido.');
     [data[i],data[j]]=[data[j],data[i]];
   }
   return data;
 }
 function draw(p,count){for(let i=0;i<count&&p.monte.length;i++)p.mao.push(p.monte.pop());}
 function start(decks,primeiro,randomIndex){
   if(!SIDES.includes(primeiro)||typeof randomIndex!=='function')fail('Sorteio local ou ordem de preparação ausente.');
   const players={};
   for(const s of SIDES){
     if(!Array.isArray(decks?.[s])||decks[s].length!==40)fail(s+': deck exige 40 cópias.');
     players[s]={monte:shuffle(decks[s],randomIndex),mao:[],campo:null,cemiterio:[]};
     draw(players[s],5);
   }
   return check({ambiente:'DEMO_LOCAL_NAO_OFICIAL',versao:0,primeiro,vez:primeiro,subetapa:0,fase:'TROCA',combate:1,jogadores:players,placar:{J1:0,J2:0},historico:[],ultimo:null});
 }
 function requireAction(state,phase,side,version){
   check(state);
   if(state.versao!==version)fail('Versão obsoleta: recarregue o estado local.');
   if(state.fase!==phase||state.vez!==side)fail('Ação fora de fase ou vez.');
 }
 function nextStage(s,phase){
   const second=opposite(s.primeiro);
   if(s.subetapa===0){s.subetapa=1;s.vez=second;}
   else{s.subetapa=0;s.vez=s.primeiro;s.fase=phase;}
 }
 function trocar(state,side,ids,version){
   requireAction(state,'TROCA',side,version);
   if(!Array.isArray(ids)||ids.length>5||new Set(ids).size!==ids.length||ids.some(id=>typeof id!=='string'))fail('Selecione 0 a 5 cópias distintas.');
   const src=state.jogadores[side];
   if(ids.some(id=>!src.mao.some(c=>c.copiaId===id)))fail('Troca exige cartas presentes na mão.');
   const next=cp(state),p=next.jogadores[side];
   p.mao=p.mao.filter(c=>{if(ids.includes(c.copiaId)){p.cemiterio.push(c);return false;}return true;});
   draw(p,ids.length);next.versao++;
   nextStage(next,'CRIATURA');
   next.historico.push({acao:'TROCA',jogador:side,descartadas:ids.length,compradas:Math.min(ids.length,src.monte.length),versao:next.versao});
   return check(next);
 }
 function invocarOuEvoluir(state,side,copyId,version){
   requireAction(state,'CRIATURA',side,version);
   const p=state.jogadores[side],candidate=p.mao.find(c=>c.copiaId===copyId);
   if(!candidate)fail('Carta não está na mão.');
   if(!integer(candidate.pvMax)||candidate.pvMax<1||!integer(candidate.ca)||candidate.ca<0)fail('Ficha sem PV/CA válida, não é possível invocar.');
   if(!p.campo){if(candidate.raridade!=='Comum')fail('Somente Comum pode ser invocada diretamente.');}
   else {
     const index=RARITY.indexOf(p.campo.raridade);
     if(candidate.tipo!==p.campo.tipo||RARITY.indexOf(candidate.raridade)!==index+1)fail('Evolução exige mesmo tipo e raridade imediatamente superior.');
   }
   const next=cp(state),current=next.jogadores[side];
   current.mao=current.mao.filter(c=>c.copiaId!==copyId);
   const action=current.campo?'EVOLUIR':'INVOCAR';
   if(current.campo)current.cemiterio.push(current.campo);
   current.campo={...candidate,pvAtual:candidate.pvMax};
   next.versao++;
   next.historico.push({acao:action,jogador:side,copiaId:copyId,versao:next.versao});
   return check(next);
 }
 function finalizarCriatura(state,side,version){
   requireAction(state,'CRIATURA',side,version);
   if(!state.jogadores[side].campo)fail('Invoque uma criatura Comum antes de terminar a preparação.');
   const next=cp(state);nextStage(next,'SUPORTE');next.versao++;return check(next);
 }
 function semSuporte(state,side,version){
   requireAction(state,'SUPORTE',side,version);
   const next=cp(state);nextStage(next,'COMBATE_EXTERNO');next.versao++;
   next.historico.push({acao:'SEM_SUPORTE',jogador:side,versao:next.versao});
   return check(next);
 }
 function resultadoExterno(state,receipt){
   check(state);
   if(state.fase!=='COMBATE_EXTERNO')fail('Não há combate aguardando resultado.');
   if(!receipt||state.versao!==receipt.versao||state.combate!==receipt.combate)fail('Combate ou versão divergente.');
   const winner=receipt.vencedor;
   if(!SIDES.includes(winner))fail('Vencedor inválido.');
   if(typeof receipt.eventoId!=='string'||!/^[\w-]{1,128}$/.test(receipt.eventoId)||state.historico.some(e=>e.eventoId===receipt.eventoId))fail('Evento repetido ou inválido.');
   const winning=state.jogadores[winner].campo;
   if(!integer(receipt.pv)||receipt.pv<1||receipt.pv>winning.pvMax)fail('PV do vencedor inválidos.');
   const loser=opposite(winner),next=cp(state);
   next.jogadores[winner].campo.pvAtual=receipt.pv;
   const knocked={...next.jogadores[loser].campo,pvAtual:0};
   next.jogadores[loser].cemiterio.push(knocked);
   next.jogadores[loser].campo=null;
   next.placar[winner]++;
   next.ultimo={acao:'RESULTADO_EXTERNO_NAO_VERIFICADO',eventoId:receipt.eventoId,combate:next.combate,vencedor:winner,derrotado:knocked.copiaId,pv:receipt.pv};
   next.historico.push(next.ultimo);
   next.fase=next.placar[winner]===3?'ENCERRADA':'POS_COMBATE';
   next.versao++;return check(next);
 }
 function novoCiclo(state,version){
   check(state);
   if(state.fase!=='POS_COMBATE'||version!==state.versao)fail('Não é permitido abrir outro ciclo.');
   const next=cp(state);next.combate++;next.versao++;
   for(const s of SIDES)draw(next.jogadores[s],Math.max(0,5-next.jogadores[s].mao.length));
   next.historico.push({acao:'INICIO_CICLO',combate:next.combate,versao:next.versao});
   next.fase='TROCA';next.vez=next.primeiro;next.subetapa=0;next.ultimo=null;
   return check(next);
 }
 function publico(state){
   check(state);
   const jogadores={};
   for(const s of SIDES){const p=state.jogadores[s];jogadores[s]={monte:p.monte.length,mao:p.mao.length,cemiterio:p.cemiterio.length,campo:p.campo?cp(p.campo):null};}
   return {fase:state.fase,versao:state.versao,combate:state.combate,vez:state.vez,primeiro:state.primeiro,placar:cp(state.placar),jogadores};
 }
 function privado(state,side){check(state);if(!SIDES.includes(side))fail('Jogador inválido.');return cp(state.jogadores[side].mao);}
 return {start,check,trocar,invocarOuEvoluir,finalizarCriatura,semSuporte,resultadoExterno,novoCiclo,publico,privado};
});
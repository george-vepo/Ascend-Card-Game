/* Visão local por jogador da vez: não oferece autenticação nem privacidade entre operadores. */
'use strict';
(() => {
 const z=window.SRDZonesDemo,$=id=>document.getElementById(id);
 let decks=()=>({J1:[],J2:[]}),s=null;
 const names={TROCA:'Troca',CRIATURA:'Invocação / evolução',SUPORTE:'Escolha de suporte',COMBATE_EXTERNO:'Resultado de IA externa',POS_COMBATE:'Pós-combate',ENCERRADA:'Encerrada'};
 function secureIndex(n){
  if(!Number.isSafeInteger(n)||n<1||n>4294967296)throw Error('Faixa de sorteio inválida.');
  const max=4294967296,limit=max-max%n,buf=new Uint32Array(1);
  do{crypto.getRandomValues(buf)}while(buf[0]>=limit);
  return buf[0]%n;
 }
 function node(tag,value,cls){const e=document.createElement(tag);e.textContent=value;if(cls)e.className=cls;return e;}
 function feedback(msg,error){const e=$('zones-feedback');e.textContent=msg;e.classList.toggle('error',Boolean(error));}
 function card(side,c){
  const root=$('zone-field-'+side.toLowerCase());root.replaceChildren();
  if(!c){root.append(node('p','Campo vazio.','muted'));return;}
  root.append(node('h3',c.nome),node('p',c.copiaId+' · '+c.tipo+' · ND '+c.nd+' · '+c.raridade),
   node('p','CA '+c.ca+' · PV '+c.pvAtual+'/'+c.pvMax));
  if(c.imagem){const img=document.createElement('img');img.className='zone-image';img.src=c.imagem;
   img.alt='Ilustração de referência (web) de '+c.nome;img.loading='lazy';img.referrerPolicy='no-referrer';
   img.addEventListener('error',()=>img.remove(),{once:true});root.append(img);}
 }
 function ready(){const d=decks();return d.J1.length===40&&d.J2.length===40;}
 function hand(items,phase){
  const root=$('zone-hand');root.replaceChildren();
  for(const [i,c] of items.entries()){
   const label=document.createElement('label');label.className='zone-hand-row';
   const select=document.createElement('input');select.type=phase==='TROCA'?'checkbox':'radio';select.name='zone-choice';select.value=c.copiaId;
   const span=document.createElement('span');
   span.append(node('strong',(i+1)+'. '+c.nome),
    node('small',c.copiaId+' · '+c.tipo+' · ND '+c.nd+' · '+c.raridade+
     (c.ca==null||c.pvMax==null?' · ficha incompleta':' · CA '+c.ca+' / PV '+c.pvMax)));
   label.append(select,span);root.append(label);
  }
 }
 function render(){
  const started=Boolean(s);$('zones-active').hidden=!started;
  $('zones-start').disabled=started||!ready();if(!started)return;
  const pub=z.publico(s),phase=pub.fase;
  $('zone-title').textContent='Combate '+pub.combate+' · '+names[phase];
  $('zone-version').textContent='Estado local V'+pub.versao;
  $('zone-score').textContent='Placar J1 '+pub.placar.J1+' × '+pub.placar.J2+' J2';
  $('zone-turn').textContent=phase==='ENCERRADA'?'Vencedor: '+(pub.placar.J1===3?'J1':'J2'):
   'Ordem fixa: '+pub.primeiro+' primeiro · Vez de '+pub.vez;
  for(const side of ['J1','J2']){
   const p=pub.jogadores[side];
   $('zone-count-'+side.toLowerCase()).textContent='Monte '+p.monte+' · Mão '+p.mao+' · Cemitério '+p.cemiterio;
   card(side,p.campo);
  }
  const showingHand=phase==='TROCA'||phase==='CRIATURA';
  $('zone-hand-panel').hidden=!showingHand;
  $('zone-swap').hidden=phase!=='TROCA';
  $('zone-invoke').hidden=phase!=='CRIATURA';
  $('zone-finalize').hidden=phase!=='CRIATURA';
  $('zone-support').hidden=phase!=='SUPORTE';
  $('zone-combat').hidden=phase!=='COMBATE_EXTERNO';
  $('zone-next').hidden=phase!=='POS_COMBATE';
  $('zone-finished').hidden=phase!=='ENCERRADA';
  if(showingHand){$('zone-own-hand').textContent='Mão de '+pub.vez+' (acesso local sem sigilo competitivo)';
   hand(z.privado(s,pub.vez),phase);
  }else $('zone-hand').replaceChildren();
  if(phase==='COMBATE_EXTERNO'){
   for(const option of $('zone-result-winner').options){
    const fighter=pub.jogadores[option.value]?.campo;
    if(fighter)option.textContent=option.value+' · '+fighter.nome+' · máximo '+fighter.pvMax+' PV';
   }
   const max=pub.jogadores[$('zone-result-winner').value].campo.pvMax;
   $('zone-result-pv').max=String(max);$('zone-pv-max').textContent='Máximo do vencedor: '+max+' PV';
  }
  if(phase==='POS_COMBATE')$('zone-next-note').textContent='Sobrevivente mantém os PV. A próxima abertura repõe ambas as mãos até cinco.';
  else $('zone-next-note').textContent='';
  if(phase==='ENCERRADA')$('zone-finished').textContent='Terceira vitória de '+(pub.placar.J1===3?'J1':'J2')+'. Nenhuma compra adicional.';
 }
 function run(op,msg){
  try{const next=op();z.check(next);s=next;feedback(msg,false);render();}
  catch(error){feedback('Ação rejeitada; estado preservado: '+error.message,true);}
 }
 const selected=()=>[...document.querySelectorAll('#zone-hand input[name="zone-choice"]:checked')].map(e=>e.value);
 $('zones-start').addEventListener('click',()=>run(()=>{
  if(!ready())throw Error('Importe 40 cópias válidas para cada jogador.');
  return z.start(decks(),secureIndex(2)===0?'J1':'J2',secureIndex);
 },'Decks embaralhados localmente e cinco cartas distribuídas para cada jogador.'));
 $('zone-swap').addEventListener('click',()=>run(()=>z.trocar(s,s.vez,selected(),s.versao),'Troca aplicada: descarte para cemitério e compra do topo.'));
 $('zone-invoke').addEventListener('click',()=>run(()=>z.invocarOuEvoluir(s,s.vez,selected()[0],s.versao),'Invocação/evolução aplicada sem reposição de mão.'));
 $('zone-finalize').addEventListener('click',()=>run(()=>z.finalizarCriatura(s,s.vez,s.versao),'Preparação da criatura confirmada.'));
 $('zone-support').addEventListener('click',()=>run(()=>z.semSuporte(s,s.vez,s.versao),'Sem suporte confirmado; nenhuma cópia consumida.'));
 $('zone-result-winner').addEventListener('change',render);
 $('zone-result-form').addEventListener('submit',event=>{
  event.preventDefault();
  if(!$('zone-result-confirm').checked){feedback('Confirme a origem externa não verificada.',true);return;}
  const value=$('zone-result-pv').value.trim();
  if(!/^\d+$/.test(value)){feedback('PV restantes devem ser inteiros.',true);return;}
  run(()=>z.resultadoExterno(s,{versao:s.versao,combate:s.combate,
    eventoId:'manual-'+crypto.randomUUID(),vencedor:$('zone-result-winner').value,pv:Number(value)}),
    'Resultado externo declarado, não verificado mecanicamente.');
  $('zone-result-form').reset();
 });
 $('zone-next').addEventListener('click',()=>run(()=>z.novoCiclo(s,s.versao),'Ciclo aberto: reposição de ambos até cinco; sem cura.'));
 $('zone-restart').addEventListener('click',()=>{
  if(!confirm('Descartar esta partida demonstrativa sem persistência?'))return;
  s=null;feedback('Estado da partida demonstrativa descartado.',false);render();
 });
 window.SRDZoneUI={init(provider){decks=provider;render();},notifyDecks:render,hasStarted(){return Boolean(s);}};
})();
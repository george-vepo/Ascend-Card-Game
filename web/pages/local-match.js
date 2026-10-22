/* UI local: sem estado de fixture e sem revelar a mão da IA no DOM. */
'use strict';
(() => {
  const api = window.SRDLocalMatch, importer = window.SRDDeckImport,
    presets = window.SRDLocalPresets;
  const $ = id => document.getElementById(id);
  const KEY = 'ascend.match.human-ai.v1';
  let catalog = null, state = null, invalidSave = false;
  const csv = { J1: null, J2: null };
  const selected = new Set();
  const COMPOSER_IDS = ['AT-009','AT-010','AT-023'];
  const allocation = {J1:{},J2:{}};
  for (const side of ['J1','J2'])
    for (const id of COMPOSER_IDS) allocation[side][id]=0;
  function total(side) {
    return COMPOSER_IDS.reduce((sum,id)=>sum+allocation[side][id],0);
  }
  function updateComposer() {
    for(const side of ['J1','J2'])
      $('local-composer-total-'+side.toLowerCase()).textContent =
        'Cópias selecionadas: '+total(side)+'/40';
    $('local-compose').disabled =
      !catalog || !!state || invalidSave ||
      total('J1')!==40 || total('J2')!==40;
  }
  function setComposerPreset(kind) {
    const species = kind === 'GIANT_OWL_CAT' ?
      {J1:'AT-023',J2:'AT-009'} : {J1:'AT-009',J2:'AT-010'};
    for(const side of ['J1','J2']) for(const id of COMPOSER_IDS) {
      const count=id===species[side]?40:0;
      allocation[side][id]=count;
      const input=$('local-composer-'+side+'-'+id);
      if(input) input.value=String(count);
    }
    updateComposer();
  }
  function buildComposer() {
    for(const side of ['J1','J2']) {
      const container=$('local-composer-'+side.toLowerCase());
      container.replaceChildren();
      for(const id of COMPOSER_IDS) {
        const card=catalog.get(id);
        if (!card) throw new Error('Criatura do editor ausente do catálogo: '+id);
        window.SRDCombatSubset.profile({catalogoId:card.id,nome:card.nome,tipo:card.tipo,
          nd:card.nd,raridade:card.raridade,ca:card.ca,pvMax:card.pvMax});
        const root=document.createElement('div');
        root.className='local-composer-card';
        if(card.imagem) {
          const img=document.createElement('img');
          img.src=card.imagem;
          img.alt='Ilustração de referência (web): '+card.nome;
          img.referrerPolicy='no-referrer';
          img.addEventListener('error',()=>img.remove(),{once:true});
          root.append(img);
        } else {
          const fallback=document.createElement('div');
          fallback.className='no-art';
          fallback.textContent='Sem arte verificada';
          root.append(fallback);
        }
        const desc=document.createElement('div');
        const name=document.createElement('strong'),info=document.createElement('small');
        name.textContent=card.nome;
        info.textContent=card.tipo+' · ND '+card.nd+' · '+card.raridade+
          ' · CA '+card.ca+' · PV '+card.pvMax;
        const label=document.createElement('label'),input=document.createElement('input');
        label.textContent='Cópias:';
        input.type='number';input.min='0';input.max='40';input.step='1';input.value='0';
        input.id='local-composer-'+side+'-'+id;
        input.addEventListener('change',()=>{
          const n=Number(input.value);
          if(!Number.isSafeInteger(n)||n<0||n>40) {
            input.value=String(allocation[side][id]);
            status('Quantidade inválida: informe um inteiro de 0 a 40.');
            return;
          }
          allocation[side][id]=n;
          updateComposer();
        });
        label.append(input);desc.append(name,info,label);root.append(desc);
        container.append(root);
      }
    }
    updateComposer();
  }
  const status = message => { $('local-status').textContent = message; };
  const newId = () => 'H_' + crypto.randomUUID().replace(/-/g, '');
  function fieldNode(card) {
    const element = document.createElement('div');
    if (!card) { element.textContent = 'Campo vazio'; return element; }
    if (card.imagem) {
      const img = document.createElement('img');
      img.alt = 'Ilustração de referência (web): ' + card.nome;
      img.src = card.imagem;
      img.referrerPolicy = 'no-referrer';
      img.addEventListener('error', () => img.remove(), { once:true });
      element.append(img);
    }
    const heading = document.createElement('strong');
    heading.textContent = card.nome;
    const detail = document.createElement('p');
    detail.textContent = card.tipo + ' · ND ' + card.nd + ' · ' + card.raridade +
      ' · ' + card.copiaId + ' · CA ' + card.ca + ' · PV ' + card.pvAtual + '/' + card.pvMax;
    element.append(heading, detail);
    return element;
  }
  function render() {
    const view = state ? api.publico(state) : null;
    $('local-setup').hidden = !!state;
    $('local-phase').textContent = view ? view.fase : 'Sem sessão';
    $('local-version').textContent = view ? 'Estado V' + view.versao : '—';
    for (const side of ['J1','J2']) {
      const lower = side.toLowerCase(), p = view?.jogadores[side];
      $('local-score-' + lower).textContent = view ? view.placar[side] : '0';
      const root = $('local-field-' + lower);
      root.replaceChildren(fieldNode(p?.campo));
      $('local-count-' + lower).textContent = p ?
        'Monte ' + p.monte + ' · Mão ' + p.mao + (side === 'J2' ? ' (oculta)' : '') +
        ' · Cemitério ' + p.cemiterio : 'Monte — · Mão — · Cemitério —';
    }
    $('local-turn').textContent = !view ? 'Aguardando decks' :
      view.fase === 'COMBATE_PENDENTE' ?
        'Pronto para iniciativa: somente Cat, Owl ou Giant Owl com ficha exata. Giant Owl: Talons apenas; magias não implementadas.' :
      view.fase === 'INICIATIVA_EMPATE_PENDENTE' ?
        'EMPATE NA INICIATIVA: rolagens registradas e combate bloqueado até regra aprovada. Não é permitido repetir a rolagem.' :
      view.fase === 'COMBATE' ?
        'Combate SRD parcial · Rodada ' + view.combate.rodada +
        ' · Vez de ' + (view.vez === 'J1' ? 'você' : 'IA') +
        ' · Iniciativa J1 ' + view.combate.iniciativas.J1.total +
        ' × J2 ' + view.combate.iniciativas.J2.total :
      view.fase === 'INICIO_CICLO_PENDENTE' ?
        'KO confirmado · novo ciclo liberado, com saque até 5 para ambos.' :
      view.fase === 'ENCERRADA' ?
        'Duelo encerrado: ' + (view.placar.J1 === 3 ? 'humano venceu' : 'IA venceu') +
        ' com 3 pontos. Nenhuma nova compra autorizada.' :
        'Etapa ' + view.fase + ' · Vez de ' + (view.vez === 'J1' ? 'você' : 'IA') +
        ' · Preparação primeiro: ' + view.primeiro;
    const hand = $('local-hand');
    hand.replaceChildren();
    for (const card of view?.maoHumano || []) {
      const button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('aria-pressed', String(selected.has(card.copiaId)));
      if (card.imagem) {
        const img=document.createElement('img');
        img.src=card.imagem;img.alt='Ilustração de referência (web): '+card.nome;
        img.referrerPolicy='no-referrer';
        img.addEventListener('error',()=>img.remove(),{once:true});
        button.append(img);
      }
      const name=document.createElement('strong'), details=document.createElement('small');
      name.textContent=card.nome;
      details.textContent=card.tipo+' · ND '+card.nd+' · '+card.raridade+
        ' · '+card.copiaId+' · CA '+(card.ca ?? 'pendente')+
        ' · PV '+(card.pvMax ?? 'pendentes');
      button.append(name,details);
      button.addEventListener('click',()=>{
        if (selected.has(card.copiaId)) selected.delete(card.copiaId);
        else if (state.fase === 'CRIATURA') { selected.clear(); selected.add(card.copiaId); }
        else if (selected.size < 5) selected.add(card.copiaId);
        render();
      });
      hand.append(button);
    }
    if (!view) hand.textContent = 'Inicie uma sessão local.';
    $('local-selection').textContent = selected.size + ' carta(s) selecionada(s)';
    const human = view?.vez === 'J1';
    $('local-start-combat').disabled = view?.fase !== 'COMBATE_PENDENTE';
    $('local-attack').disabled = !(human && view.fase === 'COMBATE');
    $('local-next-cycle').disabled = view?.fase !== 'INICIO_CICLO_PENDENTE';
    $('local-exchange').disabled = !(human && view.fase==='TROCA');
    $('local-keep').disabled = !(human && view.fase==='TROCA');
    $('local-play').disabled = !(human && view.fase==='CRIATURA' && selected.size===1);
    $('local-finish').disabled = !(human && view.fase==='CRIATURA' && view.jogadores.J1.campo);
    $('local-pass').disabled = !(human && view.fase==='SUPORTE');
    const history = $('local-history');
    history.replaceChildren();
    for (const event of [...(view?.historico || [])].reverse()) {
      const p=document.createElement('p');
      p.textContent='V'+event.versao+' · '+(event.jogador||'SISTEMA')+
        ' · '+event.acao+' · '+event.detalhe;
      history.append(p);
    }
    if (!view) history.textContent = 'Nenhuma ação.';
    $('local-start').disabled = !(catalog && csv.J1 && csv.J2 && !state && !invalidSave);
    $('local-preset').disabled = !(catalog && !state && !invalidSave);
    $('local-preset-giant').disabled = !(catalog && !state && !invalidSave);
    updateComposer();
  }
  function persist(next) {
    api.check(next);
    localStorage.setItem(KEY, JSON.stringify(next));
    state = next;
    selected.clear();
  }
  function runAI() {
    let steps=0;
    while (state?.vez==='J2' && state.fase!=='COMBATE_PENDENTE') {
      if (++steps>12) throw new Error('Limite de decisões automáticas por sequência.');
      persist(api.aiStep(state));
    }
  }
  function act(fn) {
    try {
      persist(fn());
      runAI();
      status('Ação validada e checkpoint atualizado no navegador.');
    } catch (error) { status('Bloqueio: '+error.message); }
    render();
  }
  $('local-exchange').addEventListener('click', ()=>
    act(()=>api.exchange(state,'J1',[...selected],state.versao,newId())));
  $('local-keep').addEventListener('click', ()=>
    act(()=>api.exchange(state,'J1',[],state.versao,newId())));
  $('local-play').addEventListener('click', ()=>
    act(()=>api.play(state,'J1',[...selected][0],state.versao,newId())));
  $('local-finish').addEventListener('click', ()=>
    act(()=>api.finishCreature(state,'J1',state.versao,newId())));
  $('local-pass').addEventListener('click', ()=>
    act(()=>api.noSupport(state,'J1',state.versao,newId())));
  $('local-start-combat').addEventListener('click', ()=>
    act(()=>api.beginCombat(state,state.versao,newId())));
  $('local-attack').addEventListener('click', ()=>
    act(()=>api.attack(state,'J1',state.versao,newId())));
  $('local-next-cycle').addEventListener('click', ()=>
    act(()=>api.beginCycle(state,state.versao,newId())));
  $('local-reset').addEventListener('click',()=>{
    if (!window.confirm('Apagar a sessão local e todo o histórico?')) return;
    try {
      localStorage.removeItem(KEY);
      state = null; invalidSave = false; selected.clear();
      if (catalog) buildComposer();
      status('Sessão local apagada; nenhum deck foi embaralhado.');
      render();
    } catch (error) { status('Não foi possível apagar: '+error.message); }
  });
  for (const side of ['J1','J2']) {
    $('local-'+side.toLowerCase()).addEventListener('change',async event=>{
      const file = event.target.files?.[0];
      if (!file || !catalog) return;
      try {
        if (file.size > 250000) throw new Error('CSV excede 250 KB.');
        const value = await file.text();
        importer.importDeck(value,catalog,side);
        csv[side]=value;
        $('local-deck-status').textContent='Decks carregados: humano '+(csv.J1?'40':'0')+
          '/40 · IA '+(csv.J2?'40':'0')+'/40. IDs cruzados validados no início.';
      } catch(error) { csv[side]=null;status('CSV '+side+' rejeitado: '+error.message); }
      event.target.value='';
      render();
    });
  }
  function choosePreset(kind) {
    try {
      const generated = presets.create(catalog, kind);
      csv.J1 = generated.J1;
      csv.J2 = generated.J2;
      setComposerPreset(kind);
      $('local-deck-status').textContent = kind === 'GIANT_OWL_CAT' ?
        'Decks virtuais preparados: 40 Giant Owl (humano) × 40 Cat (IA).' :
        'Decks virtuais preparados: 40 Cat (humano) × 40 Owl (IA).';
      $('local-deck-status').textContent +=
        ' Cópias sem comprovação de posse. A partida NÃO foi iniciada.';
      status('Decks escolhidos. Clique em Iniciar sessão para jogar.');
    } catch(error) { status('Preset bloqueado: '+error.message); }
    render();
  }
  $('local-preset').addEventListener('click',()=>choosePreset('CAT_OWL'));
  $('local-preset-giant').addEventListener('click',()=>choosePreset('GIANT_OWL_CAT'));
  $('local-compose').addEventListener('click',()=>{
    try {
      const plan=presets.compose(catalog,allocation);
      csv.J1=plan.J1;csv.J2=plan.J2;
      $('local-deck-status').textContent='Composição validada: 40/40 para humano e IA. '+
        'Cópias virtuais SEM comprovação de posse. A partida NÃO foi iniciada.';
      status('Decks escolhidos; clique em Iniciar sessão para começar.');
    } catch(error) { status('Montagem rejeitada: '+error.message); }
    render();
  });
  $('local-start').addEventListener('click',()=>{
    act(()=>api.start(catalog,csv.J1,csv.J2));
  });
  try {
    const raw=localStorage.getItem(KEY);
    if (raw) {
      state=api.check(JSON.parse(raw));
      // Retoma uma decisão da IA pendente mesmo se a aba fechou entre
      // persistir a ação humana e terminar a sequência automática.
      if (state.vez === 'J2') {
        try { runAI(); }
        catch (error) { status('IA aguardando resolução: ' + error.message); }
      }
    }
  } catch(error) {
    invalidSave=true;
    status('Checkpoint local incompatível. Use Apagar sessão local para recuperar: '+error.message);
  }
  render();
  (async()=>{
    try {
      catalog=await importer.loadCatalog();
      if(!state && !invalidSave) buildComposer();
      for(const side of ['j1','j2']) $('local-'+side).disabled=!!state;
      if (!invalidSave) status(state ?
        'Partida local recuperada sem alterar cartas, ordem ou versão.' :
        'Catálogo SRD carregado. Importe seus decks para iniciar.');
    } catch(error) { status('Catálogo indisponível: '+error.message+'. Checkpoint salvo continua consultável.'); }
    render();
  })();
})();

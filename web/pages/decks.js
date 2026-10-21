'use strict';
(() => {
  const api = window.SRDDeckImport;
  const el = id => document.getElementById(id);
  const decks = { J1: [], J2: [] };
  let catalog = null;
  const opposite = side => side === 'J1' ? 'J2' : 'J1';
  function message(side, text, error = false) {
    const target = el('message-' + side.toLowerCase());
    target.textContent = text;
    target.classList.toggle('error', error);
  }
  function cardNode(card, index) {
    const container = document.createElement('div');
    container.className = 'deck-card';
    if (card.imagem) {
      const img = document.createElement('img');
      img.loading = 'lazy';
      img.referrerPolicy = 'no-referrer';
      img.alt = 'Ilustração de referência (web) de ' + card.nome;
      img.src = card.imagem;
      img.addEventListener('error', () => img.replaceWith(document.createTextNode('Sem imagem confirmada')), { once:true });
      container.append(img);
    }
    const info = document.createElement('div');
    const name = document.createElement('strong');
    name.textContent = (index + 1) + '. ' + card.nome;
    const summary = document.createElement('p');
    summary.textContent = [card.copiaId, 'Catálogo ' + card.catalogoId, card.tipo,
      'ND ' + card.nd, card.raridade, card.ca == null ? 'CA pendente' : 'CA ' + card.ca,
      card.pvMax == null ? 'PV pendentes' : 'PV ' + card.pvMax].join(' · ');
    const link = document.createElement('a');
    link.href = card.fichaUrl;
    link.rel = 'noopener noreferrer';
    link.target = '_blank';
    link.textContent = 'Ver registro e fontes no catálogo ↗';
    info.append(name, summary, link);
    container.append(info);
    return container;
  }
  function render() {
    for (const side of ['J1','J2']) {
      const short=side.toLowerCase();
      el('count-'+short).textContent = decks[side].length + ' / 40 cópias validadas';
      const container=el('cards-'+short);
      container.replaceChildren();
      const details=el('details-'+short);
      details.hidden=!decks[side].length;
      const frag = document.createDocumentFragment();
      for (const [index, card] of decks[side].entries()) frag.appendChild(cardNode(card,index));
      container.appendChild(frag);
    }
    const total=decks.J1.length+decks.J2.length;
    if (total === 80) {
      const missing=decks.J1.concat(decks.J2).filter(c=>c.ca==null||c.pvMax==null).length;
      el('deck-summary').textContent='80/80 cópias reconhecidas e IDs únicos na sessão. '+
        (missing ? missing+' cópia(s) sem CA/PV completos, bloqueadas para combate validado. ' : '')+
        'Posse na coleção e mecânicas completas NÃO verificadas; nenhuma partida iniciada.';
    } else el('deck-summary').textContent=total+'/80 cópias reconhecidas na sessão. Importe 40 para cada jogador.';
  }
  function enable(enabled) {
    for (const side of ['j1','j2']) el('file-'+side).disabled=!enabled;
  }
  async function load() {
    enable(false);
    el('retry-catalog').hidden=true;
    el('catalog-status').textContent='Carregando índice, fichas e imagens do Catálogo SRD…';
    try {
      catalog=await api.loadCatalog();
      decks.J1=[];decks.J2=[];
      enable(true);
      el('catalog-status').textContent='Catálogo carregado: '+catalog.size+' identidades com ID canônico. Fichas e imagens consultadas separadamente, sem presumir homologação.';
      message('J1','Selecione o CSV J1.');message('J2','Selecione o CSV J2.');
      render();
    } catch (error) {
      catalog=null;
      el('catalog-status').textContent='Não foi possível carregar o Catálogo SRD: '+error.message;
      el('retry-catalog').hidden=false;
    }
  }
  async function importFile(side, file) {
    if (!file) return;
    const other = opposite(side);
    try {
      if (file.size>250000) throw new Error('Arquivo maior que 250 KB.');
      const text=await file.text();
      // Se o deck oposto usa algum dos mesmos IDs, rejeita de forma transacional.
      const next=api.importDeck(text,catalog,side,decks[other]);
      decks[side]=next;
      const absent=next.filter(c=>c.ca==null||c.pvMax==null).length;
      message(side,'40 identidades reconhecidas. '+
        (absent ? absent+' carta(s) sem CA/PV completos. ' : '')+
        'Posse e ficha homologada não verificadas.');
      render();
    } catch(error) {
      // Falha não substitui um deck anteriormente validado.
      message(side,'Importação rejeitada: '+error.message,true);
    }
  }
  for (const side of ['J1','J2']) {
    const lower=side.toLowerCase();
    el('file-'+lower).addEventListener('change', e=> {
      void importFile(side,e.target.files?.[0]);
      e.target.value='';
    });
    const link=el('template-'+lower);
    link.href='data:text/csv;charset=utf-8,'+encodeURIComponent(api.template(side));
  }
  el('retry-catalog').addEventListener('click',()=>void load());
  void load();
})();
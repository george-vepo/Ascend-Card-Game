/* Integração somente leitura do Catálogo SRD. Sem validação de posse ou partida oficial. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.SRDDeckImport = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  const SOURCE = 'https://george-vepo.github.io/Catalogo-SRD/';
  const DATA = SOURCE + 'data/';
  const SIDES = ['J1', 'J2'];
  const HEADERS = ['copia_id', 'catalogo_id'];
  const RARITIES = ['Comum', 'Incomum', 'Rara', 'Lendária', 'Mítica'];
  function fail(message) { throw new Error(message); }
  function norm(value) { return String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase(); }
  function ndValue(value) {
    const text = String(value ?? '').trim().replace(',', '.');
    const match = /^(\d+)(?:\/(\d+))?$/.exec(text);
    const decimal = /^(\d+)\.(\d+)$/.exec(text);
    const result = match ? Number(match[1]) / Number(match[2] ?? 1) : decimal ? Number(text) : NaN;
    if (!Number.isFinite(result) || result < 0) fail('ND ausente ou inválido: ' + text);
    return result;
  }
  function rarity(value) {
    const n = ndValue(value);
    return RARITIES[n <= 5 ? 0 : n <= 10 ? 1 : n <= 15 ? 2 : n <= 20 ? 3 : 4];
  }
  function numericField(value) {
    if (typeof value === 'number' && Number.isSafeInteger(value) && value >= 0) return value;
    const v = String(value ?? '').trim();
    return /^\d+$/.test(v) && Number.isSafeInteger(Number(v)) ? Number(v) : null;
  }
  function safeHttps(value) { return typeof value === 'string' && /^https:\/\/[^\s<>"']+$/.test(value) ? value : ''; }

  function catalogFromSources(megalista, fichas, imagens) {
    if (!Array.isArray(megalista?.records) || megalista.records.length < 1 ||
        !Array.isArray(fichas?.fichas) || !Array.isArray(imagens?.records))
      fail('Estrutura do Catálogo SRD incompatível; nenhum deck foi validado.');
    const sheet = new Map(fichas.fichas.filter(f => f?.id).map(f => [f.id, f]));
    const art = new Map(imagens.records.filter(a => a?.ID).map(a => [a.ID, a]));
    const creatures = new Map();
    for (const [index, record] of megalista.records.entries()) {
      const id = String(record['ID NO JOGO'] || '').trim();
      if (!id) continue; // 1320 candidatos NÃO implicam 1320 cartas canônicas.
      if (!/^[A-Za-z0-9_-]{1,80}$/.test(id) || creatures.has(id))
        fail('ID canônico inválido ou duplicado no catálogo: ' + id);
      const name = String(record.NOME || '').trim();
      const type = String(record.TIPO || '').trim();
      const challenge = String(record.ND ?? '').trim();
      if (!name || !type) fail('Identidade incompleta no Catálogo SRD: ' + id);
      const computed = rarity(challenge);
      if (record.RARIDADE && norm(record.RARIDADE) !== norm(computed))
        fail('Conflito de raridade por ND na ficha: ' + id);
      const f = sheet.get(id);
      const image = art.get(id);
      const artVerified = Boolean(image?.Status_verificacao?.includes('MIME, dimensões e correspondência visual confirmados'));
      const ca = numericField(f?.CA);
      const pvMax = numericField(f?.PV);
      const imageUrl = artVerified ? safeHttps(image.URL_imagem_direta) : '';
      creatures.set(id, Object.freeze({
        id, nome: name, tipo: type, nd: challenge, raridade: computed,
        origem: String(record.ORIGEM || ''), status: String(record.STATUS || ''),
        ca, pvMax: pvMax > 0 ? pvMax : null, fichaDisponivel: Boolean(f),
        imagem: imageUrl, imagemFonte: imageUrl ? safeHttps(image.URL_pagina_origem) : '',
        fichaUrl: SOURCE + '#c/' + index
      }));
    }
    if (!creatures.size) fail('Nenhuma criatura com ID canônico encontrada.');
    return creatures;
  }

  async function loadCatalog(fetcher = fetch, base = DATA) {
    const files = ['megalista-1320.json', 'fichas-607.json', 'imagens-607.json'];
    const objects = await Promise.all(files.map(async file => {
      const response = await fetcher(base + file, { cache: 'no-cache' });
      if (!response.ok) fail('Falha ao ler ' + file + ': HTTP ' + response.status);
      return response.json();
    }));
    return catalogFromSources(...objects);
  }

  function delimiterOf(text) {
    let quoted = false;
    const counts = { ';': 0, ',': 0, '\t': 0 };
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (c === '"') {
        if (quoted && text[i + 1] === '"') { i++; continue; }
        quoted = !quoted;
      } else if (!quoted && (c === '\r' || c === '\n')) break;
      else if (!quoted && Object.hasOwn(counts, c)) counts[c]++;
    }
    const winner = Object.entries(counts).sort((a,b) => b[1]-a[1])[0];
    if (!winner || !winner[1]) fail('CSV sem separador reconhecido (;, vírgula ou tabulação).');
    return winner[0];
  }

  function parseCSV(source) {
    if (typeof source !== 'string' || !source.trim()) fail('CSV vazio.');
    if (source.length > 250000) fail('CSV excede o tamanho máximo de 250 KB.');
    const text = source.replace(/^\uFEFF/, '');
    const delimiter = delimiterOf(text);
    const rows = [];
    let row = [], field = '', quoted = false, closed = false;
    function completeField() { row.push(field); field = ''; closed = false; }
    function completeRow() {
      completeField();
      if (row.some(c => c.trim() !== '')) rows.push(row);
      row = [];
    }
    for (let i=0; i<text.length; i++) {
      const c=text[i];
      if (quoted) {
        if (c === '"') {
          if (text[i+1] === '"') { field += '"'; i++; }
          else { quoted = false; closed = true; }
        } else field += c;
      } else if (c === delimiter) completeField();
      else if (c === '\r' || c === '\n') {
        completeRow();
        if (c === '\r' && text[i+1] === '\n') i++;
      } else if (c === '"') {
        if (field.length || closed) fail('Aspas fora do início de um campo CSV.');
        quoted = true;
      } else {
        if (closed && c !== ' ' && c !== '\t') fail('Texto inesperado depois de aspas no CSV.');
        if (!closed) field += c;
      }
    }
    if (quoted) fail('Aspas não fechadas no CSV.');
    if (field || row.length || closed) completeRow();
    if (rows.length < 2) fail('CSV sem cabeçalho e cartas.');
    const header = rows.shift().map(v => norm(v));
    if (header.length < 2 || header.length > 3 || new Set(header).size !== header.length ||
        !HEADERS.every(h => header.includes(h)) || header.some(h => ![...HEADERS, 'nome'].includes(h)))
      fail('Cabeçalho esperado: copia_id;catalogo_id (nome é opcional).');
    return rows.map((cells, i) => {
      if (cells.length !== header.length) fail('Colunas inconsistentes na linha ' + (i+2) + '.');
      return Object.fromEntries(header.map((h,j) => [h,cells[j].trim()]));
    });
  }

  function importDeck(csv, catalog, side, otherDeck = []) {
    if (!SIDES.includes(side)) fail('Jogador inválido.');
    if (!(catalog instanceof Map)) fail('Carregue o Catálogo SRD antes de importar.');
    const rows = parseCSV(csv);
    if (rows.length !== 40) fail(side + ': o deck precisa ter exatamente 40 cópias; recebeu ' + rows.length + '.');
    const used = new Set(otherDeck.map(x => x.copiaId));
    const cards = [];
    for (const [index, row] of rows.entries()) {
      const copyId = row.copia_id;
      if (!/^[A-Za-z0-9_:-]{1,80}$/.test(copyId)) fail('ID de cópia inválido na linha ' + (index+2) + '.');
      if (used.has(copyId)) fail('ID de cópia duplicado na partida: ' + copyId);
      used.add(copyId);
      const entry = catalog.get(row.catalogo_id);
      if (!entry) fail('ID do catálogo inexistente ou não canônico na linha ' + (index+2) + ': ' + row.catalogo_id);
      if (row.nome && norm(row.nome) !== norm(entry.nome))
        fail('Nome divergente do ID canônico na linha ' + (index+2) + '.');
      cards.push(Object.freeze({ copiaId: copyId, catalogoId: entry.id, ...entry }));
    }
    return Object.freeze(cards);
  }

  function template(side) {
    if (!SIDES.includes(side)) fail('Jogador inválido.');
    return '\uFEFFcopia_id;catalogo_id;nome\r\n' +
      Array.from({length:40}, (_,i) => side + '-C' + String(i+1).padStart(2,'0') + ';;').join('\r\n') + '\r\n';
  }

  return { SOURCE, DATA, rarity, ndValue, parseCSV, catalogFromSources, loadCatalog, importDeck, template };
});
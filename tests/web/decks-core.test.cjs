'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const core=require('../../web/pages/decks-core.js');
const mega={records:[
 {'ID NO JOGO':'AT-002',NOME:'Roper',TIPO:'Aberração',ND:'5',RARIDADE:'Comum'},
 {'ID NO JOGO':'AT-023',NOME:'Giant Owl',TIPO:'Besta',ND:'1/4',RARIDADE:'Comum'},
 {'ID NO JOGO':'TF-999',NOME:'Sem ficha',TIPO:'Monstruosidade',ND:'11',RARIDADE:'Rara'},
 {'ID NO JOGO':'',NOME:'Cranium Rat',TIPO:'Aberração',ND:'0',RARIDADE:'Comum'}]};
const sheets={fichas:[{id:'AT-002',CA:20,PV:93},{id:'AT-023',CA:12,PV:19}]};
const images={records:[
 {ID:'AT-002',URL_imagem_direta:'https://example.org/roper.png',
  Status_verificacao:'URL carregada; MIME, dimensões e correspondência visual confirmados'},
 {ID:'AT-023',URL_imagem_direta:'https://example.org/wrong.png',Status_verificacao:'Pendente'}]};
const catalog=()=>core.catalogFromSources(mega,sheets,images);
function make(side,n=40,id='AT-002'){
 return '\uFEFFcopia_id;catalogo_id;nome\r\n'+
   Array.from({length:n},(_,i)=>side+'-'+i+';'+id+';'+(id==='AT-023'?'Giant Owl':'Roper')).join('\r\n');
}
test('catálogo distingue ID canônico de candidato e dados ausentes',()=>{
 const c=catalog();assert.equal(c.size,3);
 assert.equal(c.has(''),false);assert.equal(c.get('AT-002').ca,20);
 assert.equal(c.get('AT-002').pvMax,93);assert.ok(c.get('AT-002').imagem);
 assert.equal(c.get('AT-023').imagem,'');assert.equal(c.get('TF-999').pvMax,null);
});
test('raridade por ND inclui frações e faixas exatas',()=>{
 for(const [nd,rar] of [['0','Comum'],['1/8','Comum'],['5','Comum'],['6','Incomum'],
 ['10','Incomum'],['11','Rara'],['15','Rara'],['16','Lendária'],['20','Lendária'],['21','Mítica']])
  assert.equal(core.rarity(nd),rar);
 assert.throws(()=>core.rarity('7/0'),/ND ausente/);
});
test('raridade conflitante do catálogo bloqueia leitura',()=>{
 assert.throws(()=>core.catalogFromSources({records:[{...mega.records[0],RARIDADE:'Mítica'}]},sheets,images),/Conflito/);
});
test('exige exatamente 40 cópias',()=>{
 for(const n of [39,41])assert.throws(()=>core.importDeck(make('J1',n),catalog(),'J1'),/exatamente 40/);
});
test('aceita 40 cópias da mesma criatura com 40 IDs distintos',()=>{
 const cards=core.importDeck(make('J1'),catalog(),'J1');
 assert.equal(cards.length,40);assert.equal(new Set(cards.map(c=>c.copiaId)).size,40);
 assert.equal(cards[0].raridade,'Comum');assert.equal('possui' in cards[0],false);
});
test('recusa repetição de ID no próprio deck e entre jogadores',()=>{
 assert.throws(()=>core.importDeck(make('J1').replace('J1-1;','J1-0;'),catalog(),'J1'),/duplicado/);
 const deck1=core.importDeck(make('J1'),catalog(),'J1');
 assert.throws(()=>core.importDeck(make('J1'),catalog(),'J2',deck1),/duplicado/);
});
test('recusa ID do catálogo desconhecido e nome que não corresponde',()=>{
 assert.throws(()=>core.importDeck(make('J1').replace('AT-002','EXT-0001'),catalog(),'J1'),/não canônico/);
 assert.throws(()=>core.importDeck(make('J1').replace('Roper','Invasor'),catalog(),'J1'),/divergente/);
});
test('BOM UTF-8, CSV com vírgula, tabulação e aspas escapadas',()=>{
 assert.equal(core.parseCSV('\uFEFFcopia_id,catalogo_id\n"A","AT-002"\n')[0].catalogo_id,'AT-002');
 assert.equal(core.parseCSV('copia_id\tcatalogo_id\nA\tAT-002\n')[0].copia_id,'A');
 const row=core.parseCSV('copia_id;catalogo_id;nome\n"A;1";AT-002;"Ro""per"\n')[0];
 assert.equal(row.copia_id,'A;1');assert.equal(row.nome,'Ro"per');
});
test('rejeita CSV com aspas incompletas, lixo ou colunas falsas',()=>{
 assert.throws(()=>core.parseCSV('copia_id;catalogo_id\n"A;AT-002'),/Aspas não fechadas/);
 assert.throws(()=>core.parseCSV('copia_id;catalogo_id\n"A"x;AT-002'),/Texto inesperado/);
 assert.throws(()=>core.parseCSV('copia_id;catalogo_id;pv\nA;AT-002;999'),/Cabeçalho/);
 assert.throws(()=>core.parseCSV('copia_id;catalogo_id\nA;AT-002;999'),/Colunas inconsistentes/);
});
test('modelo apresenta 40 espaços sem inventar cartas e BOM UTF-8',()=>{
 const csv=core.template('J2');
 assert.equal(csv.charCodeAt(0),0xfeff);
 const rows=core.parseCSV(csv);
 assert.equal(rows.length,40);assert.equal(rows[0].catalogo_id,'');
});
test('não cria ficha ou PV faltantes e preserva catálogo intacto',()=>{
 const c=catalog(), snapshot=JSON.stringify([...c.values()]);
 const csv='copia_id;catalogo_id\n'+
   Array.from({length:40},(_,i)=>'J1-'+i+';'+(i===39?'TF-999':'AT-002')).join('\n');
 const cards=core.importDeck(csv,c,'J1');
 assert.equal(cards[39].ca,null);assert.equal(cards[39].pvMax,null);
 assert.equal(JSON.stringify([...c.values()]),snapshot);
});
test('falha de fonte cancela carregamento e nenhuma carta é inventada',async()=>{
 await assert.rejects(core.loadCatalog(async()=>({ok:false,status:404})),/HTTP 404/);
 assert.throws(()=>core.catalogFromSources({},sheets,images),/incompatível/);
});
test('URLs do catálogo são consultadas separadamente, somente leitura',async()=>{
 const seen=[];
 const fetcher=async url=>{
  seen.push(url);
  const obj=url.endsWith('megalista-1320.json')?mega:url.endsWith('fichas-607.json')?sheets:images;
  return {ok:true,json:async()=>obj};
 };
 const c=await core.loadCatalog(fetcher,'https://host/data/');
 assert.equal(c.size,3);assert.equal(seen.length,3);
 assert.ok(seen.every(u=>u.startsWith('https://host/data/')));
});
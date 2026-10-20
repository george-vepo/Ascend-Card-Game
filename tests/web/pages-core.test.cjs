"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const core = require("../../web/pages/core.js");

const owl = () => ({nome:"Giant Owl",id:"CE-001",pv_max:19,pv_atual:19,ca:12});
const roper = () => ({nome:"Roper",id:"AB-POC-017",pv_max:93,pv_atual:93,ca:20});
function prepared() { return core.preparar(core.initial(), {J1:owl(),J2:roper()},0); }
function finish(s, winner, pv, id = "ev1") {
  return core.resultado(s, {
    vencedor:winner,pv_restantes:pv,evento_id:id,
    combate:s.combate,versao_base:s.versao,
  });
}
test("estado inicial local sem cartas predefinidas e placar zero",()=>{
  const s=core.initial();
  assert.equal(s.fase,"CONFIGURACAO");
  assert.deepEqual(s.placar,{J1:0,J2:0});
  assert.deepEqual(s.campos,{J1:null,J2:null});
  assert.equal(s.ambiente,"DEMO_LOCAL_NAO_OFICIAL");
});
test("setup introduz somente cartas declaradas pelo usuario",()=>{
  const s=prepared();
  assert.equal(s.fase,"COMBATE");
  assert.equal(s.campos.J1.nome,"Giant Owl");
  assert.equal(s.campos.J2.pv_max,93);
});
test("PV restante e KO alteram apenas registro local",()=>{
  const s=finish(prepared(),"J1",7);
  assert.equal(s.fase,"POS_COMBATE");
  assert.deepEqual(s.placar,{J1:1,J2:0});
  assert.equal(s.campos.J1.pv_atual,7);
  assert.equal(s.campos.J2,null);
  assert.deepEqual(s.cemiterio[0],{
    combate:1,jogador:"J2",carta_id:"AB-POC-017",nome:"Roper",pv_final:0,
  });
});
test("J2 vitorioso permanece e J1 vai ao cemiterio",()=>{
  const s=finish(prepared(),"J2",65);
  assert.deepEqual(s.placar,{J1:0,J2:1});
  assert.equal(s.campos.J2.pv_atual,65);
  assert.equal(s.cemiterio[0].jogador,"J1");
});
test("mesmo combate e evento nao pontua duas vezes",()=>{
  const s=finish(prepared(),"J1",7);
  assert.throws(()=>finish(s,"J1",7),/Não há combate/);
  assert.equal(s.placar.J1,1);
  assert.equal(s.historico.length,1);
});
test("PV restante zero e maior que PVmax sao recusados",()=>{
  const s=prepared();
  assert.throws(()=>finish(s,"J1",0),/PV restantes/);
  assert.throws(()=>finish(s,"J1",20),/PV restantes/);
  assert.equal(s.placar.J1,0);
});
test("valor fracionario, negativo e nao numerico de PV sao recusados",()=>{
  const s=prepared();
  for(const value of [1.2,-1,NaN,"4",true]){
    assert.throws(()=>finish(s,"J2",value),/PV restantes/);
  }
});
test("vencedor invalido nao altera estado",()=>{
  const s=prepared(), before=JSON.stringify(s);
  assert.throws(()=>finish(s,"ARBITRO",7),/Escolha/);
  assert.equal(JSON.stringify(s),before);
});
test("impede replay de versao e numero de combate obsoletos",()=>{
  const s=prepared();
  assert.throws(()=>core.resultado(s,{vencedor:"J1",pv_restantes:4,
     evento_id:"e",combate:2,versao_base:s.versao}),/Versão ou combate/);
});
test("proximo combate preserva sobrevivente e estado de PV",()=>{
  let s=finish(prepared(),"J1",6);
  s=core.proximo(s,s.versao);
  assert.equal(s.combate,2);
  assert.equal(s.campos.J1.pv_atual,6);
  assert.equal(s.campos.J2,null);
  assert.throws(()=>core.preparar(s,{J1:owl(),J2:roper()},s.versao),/sobrevivente/);
  s=core.preparar(s,{J1:s.campos.J1,J2:roper()},s.versao);
  assert.equal(s.campos.J1.pv_atual,6);
});
test("terceira vitoria encerra imediatamente sem novo combate",()=>{
  let s=prepared();
  for(let i=1;i<=3;i++){
    s=finish(s,"J1",19-i,"end-"+i);
    assert.equal(s.placar.J1,i);
    if(i<3){
      s=core.proximo(s,s.versao);
      s=core.preparar(s,{J1:s.campos.J1,J2:{...roper(),id:"ROPER-"+i}},s.versao);
    }
  }
  assert.equal(s.fase,"ENCERRADA");
  assert.throws(()=>core.proximo(s,s.versao),/não pode iniciar/);
});
test("nomes, copias e HP originados de campos sao validados",()=>{
  const base=core.initial();
  assert.throws(()=>core.preparar(base,{J1:owl(),J2:{...roper(),id:"CE-001"}},0),/IDs de cópias/);
  assert.throws(()=>core.preparar(base,{J1:{...owl(),pv_max:0},J2:roper()},0),/PV de J1/);
  assert.throws(()=>core.preparar(base,{J1:{...owl(),nome:""},J2:roper()},0),/Nome ou ID/);
  assert.throws(()=>core.preparar(base,{J1:{...owl(),ca:101},J2:roper()},0),/CA de J1/);
});
test("nenhuma ficha ou carta escondida embutida no estado inicial",()=>{
  const data=JSON.stringify(core.initial());
  for(const privateTerm of ["CE-001","AB-POC-017","monte_ordem_ids","minha_mao"]){
    assert.equal(data.includes(privateTerm),false);
  }
});
test("guardas de recuperacao local rejeitam arquivo corrompido",()=>{
  assert.throws(()=>core.validate({...core.initial(),placar:{J1:7,J2:0}}),/Placar/);
  assert.throws(()=>core.validate({...core.initial(),ambiente:"PARTIDA_OFICIAL"}),/incompatíveis/);
});

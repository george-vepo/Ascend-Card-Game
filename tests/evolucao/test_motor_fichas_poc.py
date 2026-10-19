"""Somente fixtures sintéticas: o catálogo real NÃO é copiado para o Ascend."""
import copy
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ("src", "experimental/legacy/src", "experimental/integration"):
    sys.path.insert(0, str(ROOT / p))

from ascend.catalogo_poc import CopiaReferencia
from ascend.fichas_srd import CAMINHO_FICHAS, SCHEMA_ESPERADO, REVISAO_EDITORIAL, ORIGEM_SRD
from motor_fichas_poc import SessaoFichasFixture, FonteDivergente
from motor_poc import InvalidAction

PROV = {
    "repositor_io": "FIXTURE_SINTETICA",
    "revisao_git": None, "revisao_verificada": False,
    "sha256_conteudos": {"celestial": "TESTE-CE", "aberracao": "TESTE-AB"},
    "copias": {"J1": 40, "J2": 40},
}

FICHAS = {
    8: {"id": "AT-001", "nome": "Gibbering Mouther", "nd": "2", "ca": 9, "pv": 52},
    17: {"id": "AT-002", "nome": "Roper", "nd": "5", "ca": 20, "pv": 93},
    31: {"id": "AT-003", "nome": "Aboleth", "nd": "10", "ca": 17, "pv": 150},
}


def gerar_refs():
    out = []
    for p, prefix, tipo in (("J1", "CE", "Celestial"),
                            ("J2", "AB-POC", "Aberração")):
        for i in range(1, 41):
            f = FICHAS.get(i) if p == "J2" else None
            nd = Decimal(f["nd"]) if f else Decimal("0.25")
            out.append(CopiaReferencia(
                jogador=p, id_copia=f"{prefix}-{i:03d}",
                posicao_referencia=i,
                nome=f["nome"] if f else f"CRIATURA SINTÉTICA {p} #{i}",
                tipo=tipo, nd=nd,
                raridade="Incomum" if nd == 10 else "Comum",
                id_catalogo=f["id"] if f else None,
                fonte_classificacao_ficha="SINTETICA",
                status_suporte="NAO_HOMOLOGADO",
                homologacao_declarada_catalogo="NAO",
            ))
    return tuple(out)


def criar_ficha(f):
    txt = (f'{f["nome"]} | COMUM • ND {f["nd"]}\nTipo: Aberração\n'
           f'AC {f["ca"]}\nHP {f["pv"]} (fixture)\nActions\n'
           'Ataque SINTÉTICO (não executável).\n')
    return {
        "id": f["id"], "nome": f["nome"], "tipo": "Aberração",
        "nd": f["nd"],
        "raridade": "Incomum" if f["nd"] == "10" else "Comum",
        "ca": f["ca"], "pv": f["pv"],
        "ficha_integral_texto_local": txt,
        "versao": "SRD 5.2.1", "licenca": "CC-BY-4.0",
        "attribution": "FONTE SINTETICA DE TESTE — NENHUMA HOMOLOGACAO",
        "editorial_review": REVISAO_EDITORIAL,
    }


class FixtureDeInvocacao(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / CAMINHO_FICHAS
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.refs = gerar_refs()
        self.docs = {i: criar_ficha(f) for i, f in FICHAS.items()}
        self.contrato = {"revisao_commit": "COMMIT-SINTETICO"}
        self.hand = {
            "J2": [
                "AB-POC-017", "AB-POC-031", "AB-POC-008",
                "AB-POC-001", "AB-POC-002",
            ]
        }
        self.salvar()
        self.sessao = self.criar()

    def salvar(self):
        payload = {
            "schema": SCHEMA_ESPERADO, "source": ORIGEM_SRD,
            "records": list(self.docs.values()),
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def criar(self):
        return SessaoFichasFixture.criar_de_referencias(
            self.refs, PROV, self.contrato, self.root,
            primeiro="J2", maos_fixadas=self.hand,
        )

    def troca_ambos(self, sessao=None):
        s = sessao or self.sessao
        self.assertEqual(s.comando(
            "t1", "J2", "TROCAR", {"descartar":[]}
        )["decisao"], "ACEITA")
        self.assertEqual(s.comando(
            "t2", "J1", "TROCAR", {"descartar":[]}
        )["decisao"], "ACEITA")
        return s

    def invocar_roper(self, sessao=None):
        s = self.troca_ambos(sessao)
        self.assertEqual(s.comando(
            "i1", "J2", "INVOCAR", {"carta_id": "AB-POC-017"}
        )["decisao"], "ACEITA")
        return s

    def test_01_80_copias_sem_pv_antecipado(self):
        s = self.sessao.motor.state
        self.assertEqual(len(self.sessao.registros), 80)
        self.assertTrue(all(x["pv_fonte"] is None for x in self.sessao.registros))
        self.assertTrue(all(c["pv_max"] is None for
            p in ("J1", "J2") for c in s["jogadores"][p]["cartas"].values()))

    def test_02_troca_nao_consulta_fichas(self):
        self.path.unlink()
        self.troca_ambos()
        self.assertEqual(self.sessao.motor.state["fase"], "INVOCACAO_EVOLUCAO")

    def test_03_roper_pv_ca_somente_ao_invocar(self):
        s = self.invocar_roper()
        state=s.motor.state
        card=state["jogadores"]["J2"]["cartas"]["AB-POC-017"]
        self.assertEqual((card["pv_atual"],card["pv_max"],card["ca_fonte"]),(93,93,20))
        self.assertIsNone(state["jogadores"]["J2"]["cartas"]["AB-POC-031"]["pv_max"])
        self.assertFalse(card["origem_ficha"]["habilidades_homologadas"])
        self.assertEqual(state["jogadores"]["J2"]["criatura_ativa_id"],"AB-POC-017")

    def test_04_evento_tem_origem_e_pv(self):
        s=self.invocar_roper()
        event=s.motor.events[-1]
        self.assertEqual(event["resultado"]["ficha_consultada"]["pv_maximos"],93)
        self.assertEqual(event["resultado"]["ficha_consultada"]["ca"],20)
        self.assertIn("sha256_documento",event["resultado"]["ficha_consultada"])

    def test_05_evolucao_roper_para_aboleth(self):
        s=self.invocar_roper()
        resp=s.comando("e1","J2","EVOLUIR",{"carta_id":"AB-POC-031"})
        self.assertEqual(resp["decisao"],"ACEITA")
        j=s.motor.state["jogadores"]["J2"]
        self.assertEqual(j["criatura_ativa_id"],"AB-POC-031")
        self.assertEqual(j["cartas"]["AB-POC-017"]["zona"],"CEMITERIO")
        self.assertEqual(j["cartas"]["AB-POC-031"]["zona"],"CAMPO")
        self.assertEqual(j["cartas"]["AB-POC-031"]["pv_atual"],150)
        self.assertEqual(j["cartas"]["AB-POC-031"]["ca_fonte"],17)
        self.assertEqual(len(j["cartas"]),40)
        self.assertTrue(s.motor.validate())

    def test_06_ficha_ausente_fica_pendente_sem_mudar_estado(self):
        s=self.troca_ambos()
        old=copy.deepcopy(s.motor.state)
        resp=s.comando("missing","J2","INVOCAR",{"carta_id":"AB-POC-001"})
        self.assertEqual(resp["decisao"],"PENDENTE")
        self.assertEqual(s.motor.state,old)
        self.assertEqual(len(s.motor.events),2)

    def test_07_ficha_divergente_fica_pendente(self):
        self.docs[17]["pv"]=999
        self.salvar()
        s=self.troca_ambos()
        before=copy.deepcopy(s.motor.state)
        self.assertEqual(s.comando(
            "x","J2","INVOCAR",{"carta_id":"AB-POC-017"}
        )["decisao"],"PENDENTE")
        self.assertEqual(s.motor.state,before)

    def test_08_comando_fora_da_fase_nao_consulta_ficha(self):
        self.path.unlink()
        result=self.sessao.comando("x","J2","INVOCAR",{"carta_id":"AB-POC-017"})
        self.assertEqual(result["decisao"],"REJEITADA")

    def test_09_carta_fora_mao_nao_consulta(self):
        self.troca_ambos()
        self.path.unlink()
        resp=self.sessao.comando("x","J2","INVOCAR",{"carta_id":"AB-POC-016"})
        self.assertEqual(resp["decisao"],"REJEITADA")

    def test_10_comum_nao_evolui_para_comum(self):
        s=self.invocar_roper()
        result=s.comando("x","J2","EVOLUIR",{"carta_id":"AB-POC-008"})
        self.assertEqual(result["decisao"],"REJEITADA")

    def test_11_campo_ocupado_impede_nova_invocacao(self):
        s=self.invocar_roper()
        resp=s.comando("x","J2","INVOCAR",{"carta_id":"AB-POC-008"})
        self.assertEqual(resp["decisao"],"REJEITADA")

    def test_12_sem_ativa_nao_pode_evoluir(self):
        s=self.troca_ambos()
        result=s.comando("x","J2","EVOLUIR",{"carta_id":"AB-POC-031"})
        self.assertEqual(result["decisao"],"REJEITADA")

    def test_13_copia_sem_ficha_na_evolucao_fica_pendente(self):
        s=self.invocar_roper()
        # Exemplo fictício: substituímos a identidade da posição 31 por outra
        # fonte sem ficha sem alterar o tipo/raridade do motor.
        del self.docs[31]
        self.salvar()
        old=copy.deepcopy(s.motor.state)
        resp=s.comando("e2","J2","EVOLUIR",{"carta_id":"AB-POC-031"})
        self.assertEqual(resp["decisao"],"PENDENTE")
        self.assertEqual(s.motor.state,old)

    def test_14_evento_duplicado_nao_consulta_novamente(self):
        s=self.invocar_roper()
        n=len(s.motor.events)
        first=s.comando("i1","J2","INVOCAR",{"carta_id":"AB-POC-017"})
        self.assertEqual(first["decisao"],"ACEITA")
        self.assertEqual(len(s.motor.events),n)

    def test_15_checkpoint_restaura_mesmo_estado(self):
        s=self.invocar_roper()
        restored=SessaoFichasFixture.restaurar(
            s.checkpoint(),self.root,self.contrato,exigir_revisao=False,
            referencias_fixture=self.refs,proveniencia_fixture=PROV)
        self.assertEqual(restored.motor.state,s.motor.state)
        self.assertEqual(restored.mesa_publica(),s.mesa_publica())

    def test_16_checkpoint_restaura_apos_evoluir(self):
        s=self.invocar_roper()
        self.assertEqual(s.comando("e1","J2","EVOLUIR",{"carta_id":"AB-POC-031"})["decisao"],"ACEITA")
        r=SessaoFichasFixture.restaurar(
            s.checkpoint(),self.root,self.contrato,exigir_revisao=False,
            referencias_fixture=self.refs,proveniencia_fixture=PROV)
        self.assertEqual(r.motor.state["jogadores"]["J2"]["criatura_ativa_id"],"AB-POC-031")

    def test_17_checkpoint_fonte_alterada_bloqueia_restauracao(self):
        s=self.invocar_roper()
        self.docs[17]["attribution"]="FONTE ALTERADA SINTÉTICA"
        self.salvar()
        with self.assertRaises(FonteDivergente):
            SessaoFichasFixture.restaurar(
                s.checkpoint(),self.root,self.contrato,exigir_revisao=False,
                referencias_fixture=self.refs,proveniencia_fixture=PROV)

    def test_18_checkpoint_proveniencia_divergente_bloqueia(self):
        s=self.invocar_roper()
        cp=s.checkpoint()
        cp["proveniencia"]["revisao_git"]="ALTERADO"
        with self.assertRaises(FonteDivergente):
            SessaoFichasFixture.restaurar(
                cp,self.root,self.contrato,exigir_revisao=False,
                referencias_fixture=self.refs,proveniencia_fixture=PROV)

    def test_19_checkpoint_hash_identidades_divergente(self):
        s=self.invocar_roper()
        cp=s.checkpoint()
        cp["hash_identidades"]="ALTERADO"
        with self.assertRaises(FonteDivergente):
            SessaoFichasFixture.restaurar(
                cp,self.root,self.contrato,exigir_revisao=False,
                referencias_fixture=self.refs,proveniencia_fixture=PROV)

    def test_20_checkpoint_nao_oficial(self):
        cp=self.sessao.checkpoint()
        self.assertTrue(cp["unicamente_teste"])
        cp["unicamente_teste"]=False
        with self.assertRaises(FonteDivergente):
            SessaoFichasFixture.restaurar(
                cp,self.root,self.contrato,exigir_revisao=False,
                referencias_fixture=self.refs,proveniencia_fixture=PROV)

    def test_21_nao_expoe_mao_de_j2_em_visao_publica(self):
        mesa=json.dumps(self.sessao.mesa_publica())
        self.assertNotIn("AB-POC-017",mesa)
        self.assertNotIn("CE-001",mesa)
        self.assertNotIn("monte_ordem_ids",mesa)

    def test_22_visao_privada_nao_revela_mao_alheia(self):
        j1=json.dumps(self.sessao.visao_privada("J1"))
        self.assertNotIn("AB-POC-017",j1)
        self.assertIn("CE-001",j1)

    def test_23_40_copias_por_jogador_apos_evolucao(self):
        s=self.invocar_roper()
        s.comando("e1","J2","EVOLUIR",{"carta_id":"AB-POC-031"})
        for p in ("J1","J2"):
            self.assertEqual(len(s.motor.state["jogadores"][p]["cartas"]),40)
        self.assertEqual(s.motor.state["placar"],{"J1":0,"J2":0})

    def test_24_nao_gera_ataques_magias_ou_suportes(self):
        s=self.invocar_roper()
        c=s.motor.get_card(s.motor.state,"J2","AB-POC-017")
        self.assertNotIn("ataques",c)
        self.assertNotIn("magias",c)
        self.assertNotIn("suportes",c)

    def test_25_rejeicao_preserva_historico(self):
        s=self.invocar_roper()
        before=len(s.motor.events)
        self.assertEqual(s.comando(
            "x","J2","EVOLUIR",{"carta_id":"AB-POC-001"}
        )["decisao"],"REJEITADA")
        self.assertEqual(len(s.motor.events),before)

    def test_26_rejeita_comando_inexistente(self):
        s=self.troca_ambos()
        result=s.comando("x","J2","CONJURAR_SEM_FICHA",{})
        self.assertEqual(result["decisao"],"REJEITADA")

    def test_27_dois_lados_seguem_fases_normais(self):
        s=self.invocar_roper()
        self.assertEqual(s.comando("p1","J2","PRONTO_CRIATURA",{})["decisao"],"ACEITA")
        self.assertEqual(s.motor.state["ator_da_vez"],"J1")

    def test_28_pv_invalido_sem_evento_aceito(self):
        s=self.troca_ambos()
        self.docs[17]["pv"]=0
        self.salvar()
        before=copy.deepcopy(s.motor.state)
        self.assertEqual(s.comando(
            "x","J2","INVOCAR",{"carta_id":"AB-POC-017"}
        )["decisao"],"PENDENTE")
        self.assertEqual(s.motor.state,before)

    def test_29_falta_acervo_so_bloqueia_acao_afetada(self):
        s=self.troca_ambos()
        self.path.unlink()
        self.assertEqual(s.comando(
            "x","J2","INVOCAR",{"carta_id":"AB-POC-017"}
        )["decisao"],"PENDENTE")
        self.assertEqual(s.motor.state["fase"],"INVOCACAO_EVOLUCAO")

    def test_30_erro_em_acao_alheia_nao_altera_estado(self):
        s=self.troca_ambos()
        before=copy.deepcopy(s.motor.state)
        resp=s.comando("x","J1","INVOCAR",{"carta_id":"CE-001"})
        self.assertEqual(resp["decisao"],"REJEITADA")
        self.assertEqual(s.motor.state,before)


if __name__ == "__main__":
    unittest.main()

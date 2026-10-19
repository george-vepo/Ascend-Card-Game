"""Testes sintéticos de fichas; jamais gravam ou versionam criaturas reais."""
import copy
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from ascend.catalogo_poc import CopiaReferencia
from ascend.fichas_srd import (
    CAMINHO_FICHAS, SCHEMA_ESPERADO, REVISAO_EDITORIAL, ORIGEM_SRD,
    FichaPendente, FichaConflitante, consultar_ficha,
)


def carta(id_copia="AB-POC-008", id_catalogo="AT-001", nome="Criatura Fixture"):
    return CopiaReferencia(
        jogador="J2", id_copia=id_copia, posicao_referencia=8,
        nome=nome, tipo="Aberração", nd=Decimal("2"),
        raridade="Comum", id_catalogo=id_catalogo,
        fonte_classificacao_ficha="FIXTURE", status_suporte="NAO_HOMOLOGADO",
        homologacao_declarada_catalogo="NAO",
    )


def bloco():
    return {
        "id": "AT-001", "nome": "Criatura Fixture", "tipo": "Aberração",
        "nd": "2", "raridade": "Comum", "ca": 9, "pv": 52,
        "ficha_integral_texto_local": (
            "Criatura Fixture | COMUM • ND 2\n"
            "Tipo: Aberração  CA: 9  PV: 52  ND: 2\n"
            "Medium Aberration\nAC 9\nHP 52 (7d8 + 21)\nActions\n"
            "Bite. Melee Attack Roll: +2. Hit: 7 (2d6) piercing damage.\n"
        ),
        "versao": "SRD 5.2.1", "licenca": "Creative Commons Attribution 4.0",
        "attribution": "Source attribution SRD 5.2.1",
        "editorial_review": REVISAO_EDITORIAL,
    }


class TesteFichaSobDemanda(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / CAMINHO_FICHAS
        self.path.parent.mkdir(parents=True)
        self.item = bloco()
        self.payload = {
            "schema": SCHEMA_ESPERADO, "source": ORIGEM_SRD,
            "records": [self.item],
        }
        self.refs = [carta()]
        self.contrato = {"revisao_commit": "FIXTURE"}
        self.escrever()

    def escrever(self):
        self.path.write_text(
            json.dumps(self.payload, ensure_ascii=False), encoding="utf-8"
        )

    def consulta(self, id_copia="AB-POC-008"):
        return consultar_ficha(
            self.root, self.contrato, self.refs, id_copia,
            exigir_revisao=False,
        )

    def test_01_consulta_pv_ca_texto_integral(self):
        ficha = self.consulta()
        self.assertEqual((ficha.ca, ficha.pv_maximos), (9, 52))
        self.assertIn("Bite.", ficha.ficha_integral)
        self.assertFalse(ficha.mecanicas_automaticamente_homologadas)
        self.assertIsNone(ficha.revisao_git)

    def test_02_metadados_nao_expoem_habilidade(self):
        view = self.consulta().referencia_sem_texto()
        self.assertEqual(view["ca"], 9)
        self.assertNotIn("ficha_integral", view)
        self.assertFalse(view["mecanicas_automaticamente_homologadas"])

    def test_03_copia_sem_id_catalogo_fica_pendente(self):
        self.refs = [replace(self.refs[0], id_catalogo=None)]
        with self.assertRaises(FichaPendente):
            self.consulta()

    def test_04_copia_nao_encontrada_fica_pendente(self):
        with self.assertRaises(FichaPendente):
            self.consulta("AB-POC-009")

    def test_05_ficha_ausente_pendente(self):
        self.payload["records"] = []
        self.escrever()
        with self.assertRaises(FichaPendente):
            self.consulta()

    def test_06_ficha_duplicada_bloqueia(self):
        self.payload["records"].append(copy.deepcopy(self.item))
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_07_nome_divergente_bloqueia(self):
        self.item["nome"] = "Homônimo"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_08_nd_divergente_bloqueia(self):
        self.item["nd"] = "3"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_09_tipo_divergente_bloqueia(self):
        self.item["tipo"] = "Celestial"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_10_raridade_divergente_bloqueia(self):
        self.item["raridade"] = "Incomum"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_11_pv_invalido_bloqueia(self):
        self.item["pv"] = 0
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_12_ca_booleano_bloqueia(self):
        self.item["ca"] = True
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_13_pv_diferente_do_texto_bloqueia(self):
        self.item["pv"] = 53
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_14_ca_diferente_do_texto_bloqueia(self):
        self.item["ca"] = 10
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_15_corpo_sem_acao_bloqueia(self):
        self.item["ficha_integral_texto_local"] = "Criatura Fixture | COMUM\nAC 9\nHP 52 "
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_16_edicao_errada_bloqueia(self):
        self.item["versao"] = "SRD 5.1"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_17_licenca_ausente_bloqueia(self):
        self.item["licenca"] = "INDEFINIDA"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_18_editorial_desconhecida_bloqueia(self):
        self.item["editorial_review"] = "APROVADO_INVENTADO"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_19_schema_estranho_bloqueia(self):
        self.payload["schema"] = "OUTRO"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_20_fonte_estranha_bloqueia(self):
        self.payload["source"] = "http://example.com"
        self.escrever()
        with self.assertRaises(FichaConflitante):
            self.consulta()

    def test_21_revisao_nao_opcional_por_padrao(self):
        from ascend.catalogo_poc import RevisaoCatalogoDivergente
        with self.assertRaises(RevisaoCatalogoDivergente):
            consultar_ficha(self.root, self.contrato, self.refs, "AB-POC-008")

    def test_22_sha_atualiza_quando_documento_muda(self):
        hash1 = self.consulta().sha256_documento
        self.item["attribution"] += " com contexto adicional"
        self.escrever()
        self.assertNotEqual(hash1, self.consulta().sha256_documento)

    def test_23_apenas_copia_solicitada(self):
        self.refs.append(carta("AB-POC-009", "AT-009", "Outro Monstro"))
        self.assertEqual(self.consulta().id_copia, "AB-POC-008")
        with self.assertRaises(FichaPendente):
            self.consulta("AB-POC-009")

    def test_24_id_duplicado_nas_referencias_pendente(self):
        self.refs.append(self.refs[0])
        with self.assertRaises(FichaPendente):
            self.consulta()

    def test_25_acervo_inexistente_pendente(self):
        self.path.unlink()
        with self.assertRaises(FichaPendente):
            self.consulta()


if __name__ == "__main__":
    unittest.main()

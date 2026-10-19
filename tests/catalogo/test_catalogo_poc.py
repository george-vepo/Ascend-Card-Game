"""Fixtures sintéticas: nenhum deck real fica versionado no Ascend."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from ascend.catalogo_poc import (
    carregar_referencias, CatalogoInvalido, RevisaoCatalogoDivergente,
    raridade_pelo_nd, nd_decimal, ler_contrato,
)


class ReferenciasPOC(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.raiz = Path(self.temp.name)
        self.cel = [
            {"id": f"CE-{i:03d}", "name": "Criatura de teste",
             "type": "Celestial", "nd": "1/4", "rarity": "Comum",
             "status": "Candidata"} for i in range(1, 41)
        ]
        self.abe = [
            {"ORDEM": str(i), "NOME": "Aberração de teste",
             "TIPO": "Aberração", "ND": "0.5", "RARIDADE": "Comum",
             "HOMOLOGACAO_JOGO": "NAO"} for i in range(1, 41)
        ]
        self.manifesto = ler_contrato(ROOT)
        self.salvar()

    def salvar(self):
        for nome, registros in (("celestial", self.cel), ("aberracao", self.abe)):
            p = self.raiz / self.manifesto["arquivos"][nome]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"source": "FIXTURE", "records": registros}),
                         encoding="utf-8")

    def carregar(self):
        return carregar_referencias(
            self.raiz, self.manifesto, exigir_revisao=False)

    def test_80_ids_de_copia_unicos(self):
        cartas, prov = self.carregar()
        self.assertEqual(len(cartas), 80)
        self.assertEqual(len({c.id_copia for c in cartas}), 80)
        self.assertEqual(cartas[0].id_copia, "CE-001")
        self.assertEqual(cartas[39].id_copia, "CE-040")
        self.assertEqual(cartas[40].id_copia, "AB-POC-001")
        self.assertEqual(cartas[-1].id_copia, "AB-POC-040")
        self.assertEqual(prov["copias"], {"J1": 40, "J2": 40})
        self.assertIsNone(prov["revisao_git"])
        self.assertFalse(prov["revisao_verificada"])

    def test_nd_fracionario(self):
        self.assertEqual(nd_decimal("1/4"), Decimal("0.25"))
        self.assertEqual(nd_decimal("0.5"), Decimal("0.5"))
        self.assertEqual(raridade_pelo_nd(Decimal("21")), "Mítica")

    def test_nd_invalido(self):
        for valor in ("-1", "NaN", "Inf", "1/0", "", "5/0"):
            with self.subTest(valor=valor), self.assertRaises(CatalogoInvalido):
                nd_decimal(valor)
        with self.assertRaises(CatalogoInvalido):
            raridade_pelo_nd(Decimal("5.5"))

    def test_40_copias_de_cada(self):
        self.abe.pop()
        self.salvar()
        with self.assertRaises(CatalogoInvalido):
            self.carregar()

    def test_sequencia_celestial(self):
        self.cel[1]["id"] = "CE-001"
        self.salvar()
        with self.assertRaises(CatalogoInvalido):
            self.carregar()

    def test_ordenacao_aberracao(self):
        self.abe[1]["ORDEM"] = "40"
        self.salvar()
        with self.assertRaises(CatalogoInvalido):
            self.carregar()

    def test_raridade_nao_seguir_campo_cego(self):
        self.cel[0]["rarity"] = "Mítica"
        self.salvar()
        with self.assertRaises(CatalogoInvalido):
            self.carregar()

    def test_tipo_canonico(self):
        self.abe[0]["TIPO"] = "Celestial"
        self.salvar()
        with self.assertRaises(CatalogoInvalido):
            self.carregar()

    def test_nomes_iguais_sao_copias_distintas(self):
        c, _ = self.carregar()
        self.assertEqual(c[0].nome, c[1].nome)
        self.assertNotEqual(c[0].id_copia, c[1].id_copia)

    def test_homologacao_nao_inferida(self):
        c, _ = self.carregar()
        self.assertEqual(c[0].status_suporte, "Candidata")
        self.assertEqual(c[-1].homologacao_declarada_catalogo, "NAO")
        self.assertFalse(hasattr(c[0], "pv"))
        self.assertFalse(hasattr(c[0], "ataque"))

    def test_sem_checkout_git_exige_revisao(self):
        with self.assertRaises(RevisaoCatalogoDivergente):
            carregar_referencias(self.raiz, self.manifesto)

    def test_digest_reprodutivel(self):
        _, a = self.carregar()
        _, b = self.carregar()
        self.assertEqual(a["sha256_conteudos"], b["sha256_conteudos"])


if __name__ == "__main__":
    unittest.main()

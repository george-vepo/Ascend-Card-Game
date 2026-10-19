"""Testes rápidos que não precisam de baralhos, fichas ou internet."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
from ascend.catalogo import CatalogoSRD, CatalogoIndisponivel


class SeparacaoDeProjetos(unittest.TestCase):
    def test_contrato_poc_presente(self):
        self.assertTrue((RAIZ / "docs/poc/01_Regras/CONTRATO_DE_REGRAS.md").is_file())

    def test_84_cenarios_preservados(self):
        d = json.loads((RAIZ / "docs/poc/05_Testes/CASOS_TESTE.json").read_text(encoding="utf-8"))
        self.assertEqual(len(d["testes"]), 84)
        self.assertEqual(len({x["id"] for x in d["testes"]}), 84)

    def test_schema_estado_parseavel(self):
        d = json.loads((RAIZ / "docs/poc/04_Estado/SCHEMA_ESTADO_POC.json").read_text(encoding="utf-8"))
        self.assertEqual(d["type"], "object")

    def test_fichas_de_criaturas_nao_copiadas(self):
        self.assertFalse((RAIZ / "docs/catalogo/data").exists())
        self.assertFalse((RAIZ / "docs/poc/03_Dados").exists())
        self.assertFalse((RAIZ / "experimental/legacy/src/STATUS_FICHAS_SUPORTES_80.json").exists())


class AdaptadorCatalogo(unittest.TestCase):
    def test_ler_apenas_recurso_permitido(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "docs/catalogo/data"
            p.mkdir(parents=True)
            (p / "deck-celestial-40.json").write_text('{"fixture": true}', encoding="utf-8")
            fonte = CatalogoSRD(tmp)
            self.assertEqual(fonte.ler_json("deck_celestial"), {"fixture": True})
            with self.assertRaises(ValueError):
                fonte.ler_json("../../.env")

    def test_falha_controlada_sem_catalogo(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(CatalogoIndisponivel):
                CatalogoSRD(tmp).ler_json("fichas")


if __name__ == "__main__":
    unittest.main()

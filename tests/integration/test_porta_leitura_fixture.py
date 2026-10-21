"""Porta de leitura: somente fixtures inventadas; não são cartas oficiais."""
from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from ascend.checkpoint_privado import CheckpointPrivado
from ascend.porta_leitura_fixture import (
    AcessoNegado, EstadoIndisponivel, PortaLeituraFixture,
)


def carta(lado: str, indice: int) -> dict:
    return {
        "copiaId": f"{lado}-FAKE-{indice:02}", "catalogoId": "FAKE-IDENTITY",
        "nome": "Marcador fictício", "tipo": "Aberração",
        "nd": "5", "raridade": "Comum", "ca": 10, "pvMax": 20,
        "imagem": "CANARIO_DE_ARTE_PRIVADA", "recurso_oculto": "SEGREDO_CANARIO",
    }


def fixture() -> dict:
    jogadores = {}
    for lado in ("J1", "J2"):
        cartas = [carta(lado, indice) for indice in range(40)]
        jogadores[lado] = {
            "monte": cartas[:35], "mao": cartas[35:],
            "campo": None, "cemiterio": [],
            "ordem_privada_do_monte": "SEGREDO_CANARIO",
        }
    return {
        "ambiente": "FIXTURE_NAO_OFICIAL",
        "fase": "TROCA", "vez": "J1",
        "placar": {"J1": 0, "J2": 0},
        "jogadores": jogadores,
        "inventario": {"canario": "SEGREDO_CANARIO"},
        "eventos": [{"descricao_privada": "SEGREDO_CANARIO"}],
    }


class TestarPortaLeituraFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = CheckpointPrivado(Path(self.tmp.name) / "estado.sqlite", os.urandom(32))
        self.tokens = {
            "PUBLICO": secrets.token_urlsafe(40),
            "J1": secrets.token_urlsafe(40),
            "J2": secrets.token_urlsafe(40),
        }
        self.other = {p: secrets.token_urlsafe(40) for p in self.tokens}
        self.original = fixture()
        self.assertEqual(self.db.salvar("sim01", self.original, versao_esperada=0), 1)
        self.db.salvar("sim02", self.original, versao_esperada=0)
        self._j1_original = self.tokens["J1"]
        self.gateway = PortaLeituraFixture(
            self.db, {"sim01": self.tokens, "sim02": self.other}
        )

    def test_publico_mostra_somente_contagens_e_campos_da_mesa(self):
        result = self.gateway.consultar("sim01", self.tokens["PUBLICO"])
        self.assertEqual(result["modo"], "FIXTURE_NAO_OFICIAL")
        self.assertEqual(result["versao_checkpoint"], 1)
        self.assertEqual(result["fase"], "TROCA")
        self.assertEqual(result["vez"], "J1")
        self.assertEqual(result["placar"], {"J1": 0, "J2": 0})
        self.assertNotIn("mao_privada", result)
        for lado in ("J1", "J2"):
            self.assertEqual(result["jogadores"][lado],
                             {"monte": 35, "mao": 5, "cemiterio": 0, "campo": None})
        output = json.dumps(result)
        for proibido in ("J1-FAKE-39", "J2-FAKE-39", "SEGREDO_CANARIO",
                         "inventario", "eventos", "ordem_privada_do_monte"):
            self.assertNotIn(proibido, output)

    def test_j1_so_pode_ver_sua_propria_mao(self):
        result = self.gateway.consultar("sim01", self.tokens["J1"])
        self.assertEqual(result["mao_privada"]["jogador"], "J1")
        self.assertEqual(len(result["mao_privada"]["cartas"]), 5)
        self.assertEqual(result["mao_privada"]["cartas"][-1]["copiaId"], "J1-FAKE-39")
        output = json.dumps(result)
        self.assertNotIn("J2-FAKE-39", output)
        self.assertNotIn("SEGREDO_CANARIO", output)
        self.assertNotIn("CANARIO_DE_ARTE_PRIVADA", output)
        self.assertNotIn(self.tokens["J1"], output)

    def test_j2_so_pode_ver_sua_propria_mao(self):
        result = self.gateway.consultar("sim01", self.tokens["J2"])
        self.assertEqual(result["mao_privada"]["jogador"], "J2")
        self.assertEqual(result["mao_privada"]["cartas"][-1]["copiaId"], "J2-FAKE-39")
        self.assertNotIn("J1-FAKE-39", json.dumps(result))

    def test_credenciais_incorretas_negadas_antes_de_consultar_a_base(self):
        for ref, token in [
            ("sim01", self.other["J1"]), ("sim02", self.tokens["J1"]),
            ("naoexiste", self.tokens["PUBLICO"]), ("sim01", secrets.token_urlsafe(40)),
            ("sim01", ""), ("sim01", None), ("../sim01", self.tokens["J1"])
        ]:
            with self.subTest(ref=ref):
                with self.assertRaisesRegex(AcessoNegado, "acesso não autorizado"):
                    self.gateway.consultar(ref, token)
        self.assertEqual(self.db.carregar("sim01")["versao"], 1)

    def test_token_de_publico_nao_tem_escalonamento_por_argumento(self):
        self.assertNotIn("papel", self.gateway.consultar.__code__.co_varnames[:3])
        result = self.gateway.consultar("sim01", self.tokens["PUBLICO"])
        self.assertNotIn("mao_privada", result)
        with self.assertRaises(TypeError):
            self.gateway.consultar("sim01", self.tokens["PUBLICO"], "J1")

    def test_credencial_de_uma_sessao_nao_acessa_outra(self):
        with self.assertRaises(AcessoNegado):
            self.gateway.consultar("sim02", self.tokens["J2"])
        self.assertIn("mao_privada", self.gateway.consultar("sim02", self.other["J2"]))

    def test_escopo_nao_muda_se_o_mapa_original_for_adulterado(self):
        self.tokens["J1"] = "A" * 48
        with self.assertRaises(AcessoNegado):
            self.gateway.consultar("sim01", "A" * 48)
        self.assertIn("mao_privada", self.gateway.consultar("sim01", self._j1_original))

    def test_tokens_repetidos_e_curtos_sao_proibidos(self):
        invalidos = [
            {"PUBLICO": "A" * 40, "J1": "A" * 40, "J2": "B" * 40},
            {"PUBLICO": "A" * 15, "J1": "B" * 40, "J2": "C" * 40},
            {"PUBLICO": "A" * 40, "J1": "B" * 40},
            {"PUBLICO": "A" * 40, "J1": "B" * 40, "J2": "C!" * 20},
        ]
        for token_map in invalidos:
            with self.subTest(token_map=token_map):
                with self.assertRaises(ValueError):
                    PortaLeituraFixture(self.db, {"outro": token_map})

    def test_checkpoint_sem_fixture_ou_com_dados_incompletos_e_bloqueado(self):
        version = 1
        for raw in ({"ambiente": "PARTIDA_REAL"}, {"ambiente": "FIXTURE_NAO_OFICIAL"}):
            version = self.db.salvar("sim01", raw, versao_esperada=version)
            with self.assertRaises(EstadoIndisponivel):
                self.gateway.consultar("sim01", self.tokens["PUBLICO"])
            version = self.db.salvar("sim01", self.original, versao_esperada=version)

    def test_rejeita_perda_e_duplicidade_de_copias(self):
        broken = fixture()
        broken["jogadores"]["J1"]["mao"].pop()
        self.db.salvar("sim01", broken, versao_esperada=1)
        with self.assertRaises(EstadoIndisponivel):
            self.gateway.consultar("sim01", self.tokens["J1"])
        broken = fixture()
        broken["jogadores"]["J2"]["mao"][0] = broken["jogadores"]["J1"]["mao"][0]
        self.db.salvar("sim01", broken, versao_esperada=2)
        with self.assertRaises(EstadoIndisponivel):
            self.gateway.consultar("sim01", self.tokens["PUBLICO"])

    def test_campo_publico_inclui_pv_restantes_mas_nao_a_mao(self):
        state = fixture()
        c = state["jogadores"]["J1"]["mao"].pop()
        c["pvAtual"] = 7
        state["jogadores"]["J1"]["campo"] = c
        self.db.salvar("sim01", state, versao_esperada=1)
        result = self.gateway.consultar("sim01", self.tokens["PUBLICO"])
        self.assertEqual(result["jogadores"]["J1"]["campo"]["pvAtual"], 7)
        self.assertEqual(result["jogadores"]["J1"]["campo"]["copiaId"], "J1-FAKE-39")
        self.assertEqual(result["jogadores"]["J1"]["mao"], 4)
        self.assertNotIn("J2-FAKE-39", json.dumps(result))
        self.assertNotIn("SEGREDO_CANARIO", json.dumps(result))

    def test_campos_malformados_nao_expoem_excecoes_internas(self):
        originals = [
            {"fase": {"nao": "valido"}},
            {"fase": ["TROCA"]},
        ]
        version = 1
        for fragment in originals:
            state = fixture()
            state.update(fragment)
            version = self.db.salvar("sim01", state, versao_esperada=version)
            with self.assertRaises(EstadoIndisponivel):
                self.gateway.consultar("sim01", self.tokens["PUBLICO"])
        state = fixture()
        state["jogadores"]["J1"]["monte"][0]["nd"] = {"valor": "5"}
        version = self.db.salvar("sim01", state, versao_esperada=version)
        with self.assertRaises(EstadoIndisponivel):
            self.gateway.consultar("sim01", self.tokens["PUBLICO"])

    def test_mutacao_da_visao_nao_modifica_checkpoint(self):
        result = self.gateway.consultar("sim01", self.tokens["J1"])
        result["mao_privada"]["cartas"].clear()
        result["jogadores"]["J1"]["monte"] = 900
        again = self.gateway.consultar("sim01", self.tokens["J1"])
        self.assertEqual(again["jogadores"]["J1"]["monte"], 35)
        self.assertEqual(len(again["mao_privada"]["cartas"]), 5)

    def test_metodos_de_escrita_nao_estao_expostos_pela_porta(self):
        self.assertFalse(hasattr(self.gateway, "salvar"))
        self.assertFalse(hasattr(self.gateway, "carregar"))
        self.assertFalse(hasattr(self.gateway, "iniciar_partida"))
        self.assertFalse(hasattr(self.gateway, "embaralhar"))


if __name__ == "__main__":
    unittest.main()

"""Teste real do formulário de registro manual com Catálogo SRD pinado.

Todos os resultados são declarados, não saem de combate SRD automático.
Nenhuma partida oficial é iniciada, nenhum checkpoint secreto é publicado.
"""
import copy
import json
import os
import sys
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
for rel in ("src", "experimental/legacy/src", "experimental/integration"):
    sys.path.insert(0, str(ROOT / rel))

from motor_poc import digest
from motor_roper_basico import SessaoRoperFixture
from site_resultado_manual import criar_servidor, iniciar_demo_fixture
from resultado_combate_externo import (
    COMANDO_RESULTADO_EXTERNO, ORIGEM_EXTERNA,
)


class ResultadoExternoWeb(unittest.TestCase):
    def setUp(self):
        self.s = iniciar_demo_fixture(os.environ["CATALOGO_SRD_DIR"])
        self.servidor = criar_servidor(self.s, porta=0)
        self.thread = threading.Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self._cleanup)
        self.base = f"http://127.0.0.1:{self.servidor.server_port}"
        status, self.snapshot = self.request("/api/combate")
        self.assertEqual(status, 200)
        self.assertEqual(self.snapshot["mesa"]["fase"], "COMBATE")

    def _cleanup(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.thread.join(timeout=3)

    def request(self, path, *, method="GET", data=None, csrf=True,
                ctype="application/json", origin=None):
        headers = {}
        if method == "POST":
            headers["Content-Type"] = ctype
            if csrf:
                headers["X-CSRF-Token"] = self.snapshot["token_formulario"]
            if origin is not None:
                headers["Origin"] = origin
            if isinstance(data, (dict, list)):
                data = json.dumps(data).encode("utf-8")
        req = Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=8) as res:
                body = res.read().decode("utf-8")
                return res.status, json.loads(body) if "json" in res.headers.get(
                    "Content-Type", ""
                ) else body
        except HTTPError as ex:
            body = ex.read().decode("utf-8")
            return ex.code, json.loads(body)

    def payload(self, winner="J1", hp=12, eid="external-event-01"):
        return {
            "evento_id": eid,
            "combate_numero": self.snapshot["combate_numero"],
            "vencedor": winner,
            "pv_restantes_vencedor": hp,
            "versao_base": self.snapshot["versao_base"],
            "hash_estado_base": self.snapshot["hash_estado_base"],
            "confirmacao_usuario": True,
        }

    def post(self, data=None, **kwargs):
        return self.request(
            "/api/resultado", method="POST",
            data=self.payload() if data is None else data, **kwargs
        )

    def state_copy(self):
        return copy.deepcopy(self.s.motor.state)

    def test_01_contexto_mesa_publica_fonte_duas_criaturas(self):
        view = self.snapshot
        self.assertEqual(view["modo"], "FIXTURE_NAO_OFICIAL")
        self.assertEqual(view["mesa"]["placar"], {"J1": 0, "J2": 0})
        self.assertEqual(view["mesa"]["jogadores"]["J1"]["campo"]["nome"],
                         "Giant Owl")
        self.assertEqual(view["mesa"]["jogadores"]["J2"]["campo"]["nome"],
                         "Roper")
        self.assertEqual(view["hash_estado_base"], digest(self.s.motor.state))

    def test_02_interface_html_css_js_entregues(self):
        for path, expected in (
            ("/", "Resultado do combate"),
            ("/styles.css", "--background: #0b1219"),
            ("/app.js", "/api/resultado"),
        ):
            status, content = self.request(path)
            self.assertEqual(status, 200)
            self.assertIn(expected, content)

    def test_03_registrar_vitoria_j1_aplica_pv_placar_cemiterio(self):
        status, response = self.post()
        self.assertEqual(status, 200, response)
        self.assertEqual(response["decisao"], "ACEITA")
        self.assertEqual(response["registro"]["vencedor"], "J1")
        self.assertEqual(response["registro"]["pv_vencedor_final"], 12)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 1, "J2": 0})
        self.assertEqual(self.s.motor.state["fase"], "POS_COMBATE")
        self.assertEqual(self.s.motor.state["jogadores"]["J1"]["criatura_ativa_id"],
                         "CE-001")
        self.assertEqual(
            self.s.motor.state["jogadores"]["J1"]["cartas"]["CE-001"]["pv_atual"],
            12,
        )
        defeated = self.s.motor.state["jogadores"]["J2"]["cartas"]["AB-POC-017"]
        self.assertEqual((defeated["zona"], defeated["pv_atual"]),
                         ("CEMITERIO", 0))
        self.assertTrue(self.s.motor.validate())

    def test_04_registrar_vitoria_j2_com_pv_alto(self):
        status, response = self.post(self.payload("J2", 71))
        self.assertEqual(status, 200, response)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 0, "J2": 1})
        survivor = self.s.motor.state["jogadores"]["J2"]["cartas"]["AB-POC-017"]
        self.assertEqual((survivor["zona"], survivor["pv_atual"]), ("CAMPO", 71))
        defeated = self.s.motor.state["jogadores"]["J1"]["cartas"]["CE-001"]
        self.assertEqual((defeated["zona"], defeated["pv_atual"]),
                         ("CEMITERIO", 0))

    def test_05_resultado_registrado_nao_verifica_batalha(self):
        _, out = self.post()
        event = self.s.motor.events[-1]
        self.assertEqual(event["acao"], COMANDO_RESULTADO_EXTERNO)
        self.assertEqual(event["autor"], "ARBITRO")
        self.assertEqual(event["parametros"]["origem"], ORIGEM_EXTERNA)
        self.assertIn("não foram verificados", out["registro"]["aviso"])

    def test_06_hp_zero_rejeitado_sem_mutacao(self):
        before = self.state_copy()
        status, out = self.post(self.payload(hp=0))
        self.assertEqual(status, 422, out)
        self.assertEqual(out["decisao"], "REJEITADA")
        self.assertEqual(self.s.motor.state, before)

    def test_07_hp_maior_que_maximo_rejeitado(self):
        before = self.state_copy()
        status, _ = self.post(self.payload(hp=20))
        self.assertEqual(status, 422)
        self.assertEqual(self.s.motor.state, before)

    def test_08_hp_negativo_rejeitado(self):
        status, out = self.post(self.payload(hp=-1))
        self.assertEqual(status, 422, out)

    def test_09_hp_bool_rejeitado(self):
        status, out = self.post(self.payload(hp=True))
        self.assertEqual(status, 422, out)

    def test_10_hp_decimal_rejeitado(self):
        status, out = self.post(self.payload(hp=3.5))
        self.assertEqual(status, 422, out)

    def test_11_vencedor_invalido_rejeitado(self):
        before = self.state_copy()
        status, out = self.post(self.payload(winner="ARBITRO"))
        self.assertEqual(status, 422, out)
        self.assertEqual(self.s.motor.state, before)

    def test_12_sem_confirmacao_usuario_rejeitado(self):
        data = self.payload()
        data["confirmacao_usuario"] = False
        status, out = self.post(data)
        self.assertEqual(status, 422, out)

    def test_13_versao_obsoleta_bloqueia_sem_mudar_estado(self):
        data = self.payload()
        data["versao_base"] = "E000"
        before = self.state_copy()
        status, out = self.post(data)
        self.assertEqual(status, 409, out)
        self.assertEqual(self.s.motor.state, before)

    def test_14_hash_errado_bloqueia_sem_mudar_estado(self):
        data = self.payload()
        data["hash_estado_base"] = "0" * 64
        before = self.state_copy()
        status, out = self.post(data)
        self.assertEqual(status, 422, out)
        self.assertEqual(self.s.motor.state, before)

    def test_15_numero_combate_diferente_bloqueia(self):
        data = self.payload()
        data["combate_numero"] += 1
        status, out = self.post(data)
        self.assertEqual(status, 422, out)

    def test_16_mesmo_evento_mesmo_payload_e_idempotente(self):
        req = self.payload()
        first_status, first = self.post(req)
        self.assertEqual(first_status, 200)
        count = len(self.s.motor.events)
        again_status, again = self.post(req)
        self.assertEqual(again_status, 200, again)
        self.assertEqual(again["registro"], first["registro"])
        self.assertEqual(len(self.s.motor.events), count)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 1, "J2": 0})

    def test_17_mesmo_evento_payload_diferente_rejeitado_sem_500(self):
        self.post(self.payload())
        req = self.payload(hp=9)
        status, out = self.post(req)
        self.assertEqual(status, 409, out)
        self.assertIn("colisão", out["motivo"])
        self.assertEqual(self.s.motor.state["placar"], {"J1": 1, "J2": 0})

    def test_18_evento_novo_mesmo_combate_ja_encerrado_rejeitado(self):
        self.post()
        status, out = self.post(self.payload(eid="external-event-02"))
        self.assertEqual(status, 422, out)
        self.assertEqual(self.s.motor.state["placar"], {"J1": 1, "J2": 0})

    def test_19_ausencia_token_csrf_rejeitado(self):
        before = self.state_copy()
        status, _ = self.post(csrf=False)
        self.assertEqual(status, 403)
        self.assertEqual(self.s.motor.state, before)

    def test_20_origin_diferente_rejeitado(self):
        status, _ = self.post(origin="https://malicioso.exemplo")
        self.assertEqual(status, 403)

    def test_21_content_type_nao_json_rejeitado(self):
        status, _ = self.post(data="qualquer".encode("utf-8"), ctype="text/plain")
        self.assertEqual(status, 415)

    def test_22_campos_extra_injetados_rejeitados(self):
        data = self.payload()
        data["pv_perdedor"] = 19
        status, _ = self.post(data)
        self.assertEqual(status, 400)

    def test_23_evento_id_com_path_rejeitado(self):
        status, _ = self.post(self.payload(eid="../id"))
        self.assertEqual(status, 400)

    def test_24_servidor_recusa_escuta_em_rede_sem_auth(self):
        with self.assertRaises(ValueError):
            criar_servidor(self.s, host="0.0.0.0", porta=0)

    def test_25_mesa_publica_mostra_resultado_pos_combate(self):
        self.post(self.payload())
        status, data = self.request("/api/combate")
        self.assertEqual(status, 200)
        self.assertEqual(data["mesa"]["fase"], "POS_COMBATE")
        self.assertEqual(data["mesa"]["ultimo_resultado_externo"]["vencedor"], "J1")
        self.assertEqual(data["mesa"]["placar"], {"J1": 1, "J2": 0})

    def test_26_sem_vazamento_de_maos_ordem_ou_checkpoints(self):
        _, before = self.request("/api/combate")
        self.post()
        _, after = self.request("/api/combate")
        for data in (before, after):
            serialized = json.dumps(data)
            for hidden in ("monte_ordem_ids", "minha_mao", "copia_ids_deck",
                           "CE-002", "AB-POC-001", "checkpoint_fixture"):
                self.assertNotIn(hidden, serialized)

    def test_27_nao_compra_cartas_durante_o_ko(self):
        before = self.s.motor.state
        prior = {
            p: (
                len(self.s.motor.hand(before, p)),
                list(before["jogadores"][p]["monte_ordem_ids"]),
            ) for p in ("J1", "J2")
        }
        self.post()
        new = self.s.motor.state
        for p, (size, order) in prior.items():
            self.assertEqual(len(self.s.motor.hand(new, p)), size)
            self.assertEqual(new["jogadores"][p]["monte_ordem_ids"], order)

    def test_28_aceita_pv_maior_que_atual_somente_atestado_sem_verificar_cura(self):
        # Fixture: simulação externa poderia curar o vencedor, não cabe deduzir.
        self.s.motor.state["jogadores"]["J1"]["cartas"]["CE-001"]["pv_atual"] = 4
        self.snapshot = self.request("/api/combate")[1]
        status, out = self.post(self.payload(hp=11))
        self.assertEqual(status, 200, out)
        self.assertEqual(out["registro"]["pv_vencedor_anterior"], 4)
        self.assertEqual(out["registro"]["pv_vencedor_final"], 11)
        self.assertIn("não foram verificados", out["registro"]["aviso"])

    def test_29_tres_pontos_encerram_partida_na_fixture(self):
        self.s.motor.state["placar"]["J1"] = 2
        self.snapshot = self.request("/api/combate")[1]
        status, out = self.post(self.payload(hp=9))
        self.assertEqual(status, 200, out)
        self.assertTrue(out["registro"]["partida_encerrada"])
        self.assertEqual(self.s.motor.state["situacao"], "ENCERRADA")
        self.assertEqual(self.s.motor.state["fase"], "ENCERRADA")
        self.assertEqual(self.s.motor.state["placar"]["J1"], 3)

    def test_30_api_so_pode_registrar_arb_backend(self):
        from resultado_combate_externo import aplicar_resultado_externo
        from motor_poc import InvalidAction
        params = {
            k: v for k, v in self.payload().items() if k != "evento_id"
        }
        params["origem"] = ORIGEM_EXTERNA
        with self.assertRaises(InvalidAction):
            aplicar_resultado_externo(
                self.s.motor, self.s.motor.state, "J1", params,
            )

    def test_31_arquivo_json_invalido_rejeitado(self):
        status, out = self.post(data=b'{\u0022quebrado\u0022:')
        self.assertEqual(status, 400, out)

    def test_32_pontuacao_e_hash_evento_auditaveis(self):
        self.post()
        event = self.s.motor.events[-1]
        self.assertEqual(
            event["estado_apos_hash"], digest(self.s.motor.state))
        self.assertEqual(event["resultado"]["placar"], {"J1": 1, "J2": 0})
        self.assertTrue(self.s.motor.validate())


if __name__ == "__main__":
    unittest.main()

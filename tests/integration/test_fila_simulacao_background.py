"""Fila de simulações em segundo plano, sem estado privado no SQLite."""
import json
import sqlite3
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from ascend.fila_simulacao_background import (
    FilaBackground, ErroFila, executar_tick_worker,
)


SUMMARY = {
    "passos_aceitos": 2,
    "fase": "COMBATE",
    "ator_da_vez": "J1",
    "versao_estado": "E011",
    "placar_fixture": {"J1": 0, "J2": 0},
}


class DurableBackgroundQueue(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "jobs.sqlite"
        self.fila = FilaBackground(self.path)
        self.fila.enfileirar("sim-1", "fixture-privada-1", agora=100)

    def test_01_job_persistido_sem_estado_privado(self):
        out = self.fila.status_publico("sim-1")
        self.assertEqual(out["status"], "NA_FILA")
        self.assertIsNone(out["resumo"])
        self.assertNotIn("referencia_opaca", out)
        self.assertNotIn("token_lease", json.dumps(out))

    def test_02_duplicacao_bloqueada(self):
        with self.assertRaisesRegex(ErroFila, "duplicado"):
            self.fila.enfileirar("sim-1", "outro-ref", agora=100)

    def test_03_claim_unico_mesmo_com_duas_instancias(self):
        one = self.fila.reivindicar("worker-1", agora=105)
        two = FilaBackground(self.path).reivindicar("worker-2", agora=105)
        self.assertIsNotNone(one)
        self.assertIsNone(two)
        self.assertEqual(one["referencia_opaca"], "fixture-privada-1")
        self.assertEqual(one["fencing"], 1)

    def test_04_reivindicacao_apos_lease_expirado_tem_novo_fencing(self):
        first = self.fila.reivindicar("worker-1", agora=105, lease_segundos=10)
        new = self.fila.reivindicar("worker-2", agora=116, lease_segundos=10)
        self.assertEqual(new["fencing"], 2)
        self.assertNotEqual(new["token"], first["token"])
        with self.assertRaisesRegex(ErroFila, "cercado"):
            self.fila.confirmar(first, "CONCLUIDO", SUMMARY, agora=117)
        self.fila.confirmar(new, "CONCLUIDO", SUMMARY, agora=117)
        self.assertEqual(self.fila.status_publico("sim-1")["status"], "CONCLUIDO")

    def test_05_heartbeat_renova_lease_valido(self):
        claim = self.fila.reivindicar("w", agora=105, lease_segundos=10)
        self.assertTrue(
            self.fila.renovar(claim, agora=109, lease_segundos=25))
        self.assertIsNone(
            self.fila.reivindicar("other", agora=120))
        self.fila.confirmar(claim, "AGUARDANDO_JOGADOR", SUMMARY, agora=130)
        self.assertEqual(
            self.fila.status_publico("sim-1")["status"], "AGUARDANDO_JOGADOR")

    def test_06_heartbeat_apos_expiracao_falha(self):
        claim = self.fila.reivindicar("w", agora=105, lease_segundos=10)
        self.assertFalse(self.fila.renovar(claim, agora=115))
        with self.assertRaises(ErroFila):
            self.fila.confirmar(claim, "CONCLUIDO", SUMMARY, agora=115)

    def test_07_status_publico_sanitizado(self):
        claim = self.fila.reivindicar("w", agora=105)
        self.fila.confirmar(claim, "NA_FILA", SUMMARY, agora=110)
        out = self.fila.status_publico("sim-1")
        self.assertEqual(out["resumo"], SUMMARY)
        serialized = json.dumps(out)
        for forbidden in ("token_lease", "referencia_opaca", "monte_ordem_ids",
                          "minha_mao", "copia_ids_deck", "checkpoint"):
            self.assertNotIn(forbidden, serialized)

    def test_08_tentativa_de_persistir_maos_rejeitada(self):
        claim = self.fila.reivindicar("w", agora=105)
        private = {**SUMMARY, "maos_j1": ["CE-002"]}
        with self.assertRaisesRegex(ErroFila, "campos públicos"):
            self.fila.confirmar(claim, "NA_FILA", private, agora=110)
        self.assertIsNone(self.fila.status_publico("sim-1")["resumo"])

    def test_09_placar_invalido_rejeitado(self):
        claim = self.fila.reivindicar("w", agora=105)
        with self.assertRaises(ErroFila):
            self.fila.confirmar(
                claim, "CONCLUIDO",
                {**SUMMARY, "placar_fixture": {"J1": 0, "J2": 7}},
                agora=106,
            )

    def test_10_retomada_exige_entrada_validada(self):
        claim = self.fila.reivindicar("w", agora=105)
        self.fila.confirmar(claim, "AGUARDANDO_DADOS", SUMMARY, agora=110)
        with self.assertRaisesRegex(ErroFila, "confirmação externa"):
            self.fila.retomar(
                "sim-1", entrada_externa_validada=False, agora=111)
        self.assertEqual(
            self.fila.status_publico("sim-1")["status"], "AGUARDANDO_DADOS")
        self.fila.retomar("sim-1", entrada_externa_validada=True, agora=112)
        self.assertEqual(self.fila.status_publico("sim-1")["status"], "NA_FILA")

    def test_11_concluido_nao_reabre(self):
        claim = self.fila.reivindicar("w", agora=105)
        self.fila.confirmar(claim, "CONCLUIDO", SUMMARY, agora=106)
        with self.assertRaises(ErroFila):
            self.fila.retomar("sim-1", entrada_externa_validada=True, agora=107)
        self.assertIsNone(self.fila.reivindicar("w", agora=108))

    def test_12_cancelamento_invalida_claim_antigo(self):
        claim = self.fila.reivindicar("w", agora=105)
        self.fila.cancelar("sim-1", agora=106)
        with self.assertRaises(ErroFila):
            self.fila.confirmar(claim, "CONCLUIDO", SUMMARY, agora=107)
        self.assertEqual(
            self.fila.status_publico("sim-1")["status"], "CANCELADO")
        self.assertIsNone(self.fila.reivindicar("w2", agora=108))

    def test_13_worker_tick_avanca_uma_operação(self):
        seen = []
        def run(ref):
            seen.append(ref)
            return {
                "estado": "AGUARDANDO_JOGADOR",
                **SUMMARY,
            }
        out = executar_tick_worker(self.fila, "worker", run, agora=105)
        self.assertEqual(seen, ["fixture-privada-1"])
        self.assertEqual(out["status"], "AGUARDANDO_JOGADOR")
        self.assertEqual(out["resumo"]["passos_aceitos"], 2)
        self.assertIsNone(
            executar_tick_worker(self.fila, "worker", run, agora=106))

    def test_14_worker_sem_resultado_valido_falha_sem_placar_inventado(self):
        def fail(_):
            raise RuntimeError("segredo não pode ir para status público")
        with self.assertRaises(RuntimeError):
            executar_tick_worker(self.fila, "worker", fail, agora=105)
        status = self.fila.status_publico("sim-1")
        self.assertEqual(status["status"], "FALHOU")
        self.assertIsNone(status["resumo"])
        self.assertNotIn("segredo", json.dumps(status))

    def test_15_worker_status_executando_volta_a_fila(self):
        run = lambda _: {"estado": "EXECUTANDO", **SUMMARY}
        out = executar_tick_worker(self.fila, "w", run, agora=105)
        self.assertEqual(out["status"], "NA_FILA")
        self.assertIsNotNone(self.fila.reivindicar("w2", agora=106))

    def test_16_reabertura_de_banco_preserva_status(self):
        claim = self.fila.reivindicar("w", agora=105)
        self.fila.confirmar(claim, "PENDENTE_REGRA", SUMMARY, agora=106)
        other = FilaBackground(self.path)
        self.assertEqual(
            other.status_publico("sim-1")["status"], "PENDENTE_REGRA")
        self.assertIsNone(other.reivindicar("w2", agora=107))

    def test_17_doido_nao_pode_confirmar_worker_errado(self):
        claim = self.fila.reivindicar("w1", agora=105)
        bad = {**claim, "worker_id": "w2"}
        with self.assertRaises(ErroFila):
            self.fila.confirmar(bad, "CONCLUIDO", SUMMARY, agora=106)
        self.fila.confirmar(claim, "CONCLUIDO", SUMMARY, agora=106)

    def test_18_banco_nao_guarda_nomes_da_mao_ou_fichas(self):
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "SELECT id, referencia_opaca, status, resumo_publico "
                "FROM simulacoes"
            ).fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][:3],
                         ("sim-1", "fixture-privada-1", "NA_FILA"))
        self.assertIsNone(rows[0][3])

    def test_19_concorrencia_claim_em_threads_apenas_um(self):
        got = []
        lock = threading.Lock()
        def worker(name):
            job = FilaBackground(self.path).reivindicar(name, agora=105)
            if job:
                with lock:
                    got.append(job)
        a = threading.Thread(target=worker, args=("w-a",))
        b = threading.Thread(target=worker, args=("w-b",))
        a.start()
        b.start()
        a.join()
        b.join()
        self.assertEqual(len(got), 1)

    def test_20_rejeita_lease_e_identificadores_inseguros(self):
        with self.assertRaises(ErroFila):
            self.fila.reivindicar("w", lease_segundos=0, agora=105)
        with self.assertRaises(ErroFila):
            self.fila.enfileirar("../../segredo", "ref", agora=105)
        with self.assertRaises(ErroFila):
            self.fila.enfileirar("ref-2", "algo/secreto", agora=105)

    def test_21_status_de_falha_sem_resumo_pode_ser_gravado(self):
        claim = self.fila.reivindicar("w", agora=105)
        self.fila.confirmar(claim, "FALHOU", None, agora=106)
        self.assertEqual(
            self.fila.status_publico("sim-1")["status"], "FALHOU")
        self.assertIsNone(self.fila.status_publico("sim-1")["resumo"])

    def test_22_rejeita_concluir_sem_resumo(self):
        claim = self.fila.reivindicar("w", agora=105)
        with self.assertRaises(ErroFila):
            self.fila.confirmar(claim, "CONCLUIDO", None, agora=106)

    def test_23_versao_do_lease_nao_reduz_com_reivindicacoes(self):
        a = self.fila.reivindicar("w", agora=105, lease_segundos=10)
        b = self.fila.reivindicar("w2", agora=116, lease_segundos=10)
        self.assertGreater(b["fencing"], a["fencing"])
        self.fila.confirmar(b, "NA_FILA", SUMMARY, agora=117)
        c = self.fila.reivindicar("w3", agora=118)
        self.assertGreater(c["fencing"], b["fencing"])

    def test_24_cancelamento_nao_desfaz_conclusao(self):
        claim = self.fila.reivindicar("w", agora=105)
        self.fila.confirmar(claim, "CONCLUIDO", SUMMARY, agora=106)
        with self.assertRaises(ErroFila):
            self.fila.cancelar("sim-1", agora=107)
        self.assertEqual(self.fila.status_publico("sim-1")["status"], "CONCLUIDO")


if __name__ == "__main__":
    unittest.main()

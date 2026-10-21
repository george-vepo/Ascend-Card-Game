"""Testes com estados exclusivamente FICTÍCIOS. Nenhum checkpoint de partida real."""
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from ascend.checkpoint_privado import CheckpointPrivado, ErroCheckpoint, VersaoDesatualizada

ESTADO = {"fixture": True, "maos": {"J1": ["CE-001"], "J2": ["AB-POC-017"]},
          "montes": {"J1": ["CE-002"], "J2": ["AB-POC-018"]}, "pv": [52, 70]}

class CheckpointsCriptografados(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "privado.sqlite"
        self.key = os.urandom(32)
        self.storage = CheckpointPrivado(self.path, self.key)

    def test_criar_e_recuperar_em_outra_instancia(self):
        self.assertIsNone(self.storage.carregar("sim-1"))
        self.assertEqual(self.storage.salvar("sim-1", ESTADO, versao_esperada=0), 1)
        new = CheckpointPrivado(self.path, self.key)
        self.assertEqual(new.carregar("sim-1"), {"versao": 1, "estado": ESTADO})

    def test_nao_expoe_maos_ou_montes_em_plaintext_sqlite(self):
        self.storage.salvar("sim-1", ESTADO, versao_esperada=0)
        raw = self.path.read_bytes()
        for token in (b"AB-POC-017", b"CE-001", b"montes", b"maos"):
            self.assertNotIn(token, raw)

    def test_controle_de_versao_rejeita_replay(self):
        self.storage.salvar("sim-1", ESTADO, versao_esperada=0)
        self.assertEqual(self.storage.salvar("sim-1", {"alterado": True}, versao_esperada=1), 2)
        with self.assertRaises(VersaoDesatualizada):
            self.storage.salvar("sim-1", ESTADO, versao_esperada=1)
        self.assertEqual(self.storage.carregar("sim-1")["versao"], 2)

    def test_clave_errada_nao_revela_snapshot(self):
        self.storage.salvar("sim-1", ESTADO, versao_esperada=0)
        wrong = CheckpointPrivado(self.path, os.urandom(32))
        with self.assertRaises(ErroCheckpoint):
            wrong.carregar("sim-1")

    def test_blob_manipulado_e_detectado(self):
        self.storage.salvar("sim-1", ESTADO, versao_esperada=0)
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE checkpoints SET cifra=? WHERE referencia=?", (bytes(35),"sim-1"))
        with self.assertRaisesRegex(ErroCheckpoint, "corrompido"):
            self.storage.carregar("sim-1")

    def test_ataque_swap_entre_referencias_falha_por_aad(self):
        self.storage.salvar("sim-1", ESTADO, versao_esperada=0)
        self.storage.salvar("sim-2", {"outro": True}, versao_esperada=0)
        with sqlite3.connect(self.path) as db:
            ref1=db.execute("SELECT nonce,cifra FROM checkpoints WHERE referencia='sim-1'").fetchone()
            db.execute("UPDATE checkpoints SET nonce=?,cifra=? WHERE referencia='sim-2'", ref1)
        with self.assertRaises(ErroCheckpoint):
            self.storage.carregar("sim-2")

    def test_rejeita_caminho_relativo_e_simbolico(self):
        with self.assertRaises(ErroCheckpoint):
            CheckpointPrivado("checkpoint.sqlite", self.key)
        with self.assertRaises(ErroCheckpoint):
            self.storage.salvar("../secreto", ESTADO, versao_esperada=0)

    def test_rejeita_entrada_invalida_e_chave_curta(self):
        with self.assertRaises(ErroCheckpoint):
            CheckpointPrivado(self.path, b"invalida")
        for versao in (-1, 1.5, True):
            with self.assertRaises(ErroCheckpoint):
                self.storage.salvar("sim-1", ESTADO, versao_esperada=versao)
        with self.assertRaises(ErroCheckpoint):
            self.storage.salvar("sim-1", {"x": float("nan")}, versao_esperada=0)

    def test_permissoes_posix(self):
        if os.name!="posix":
            self.skipTest("ACLs Windows externos")
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        bad = Path(self.tmp.name) / "exposto"
        bad.mkdir(mode=0o755)
        with self.assertRaises(ErroCheckpoint):
            CheckpointPrivado(bad/"dados.sqlite", self.key)

    def test_concorrencia_dois_escritores_apenas_um_avanca(self):
        self.storage.salvar("sim-1", ESTADO, versao_esperada=0)
        start = threading.Barrier(2)
        resultados=[]
        def worker(n):
            own=CheckpointPrivado(self.path, self.key)
            start.wait()
            try:
                own.salvar("sim-1", {"escritor": n}, versao_esperada=1)
                resultados.append("aceito")
            except VersaoDesatualizada:
                resultados.append("obsoleto")
        a=threading.Thread(target=worker,args=(1,)); b=threading.Thread(target=worker,args=(2,))
        a.start();b.start();a.join();b.join()
        self.assertCountEqual(resultados,["aceito","obsoleto"])
        self.assertEqual(self.storage.carregar("sim-1")["versao"],2)

if __name__=="__main__":
    unittest.main()

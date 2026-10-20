"""Fila durável e cercada por lease/fencing para simulações IA em background.

Persiste APENAS estado público e referência opaca ao checkpoint privado.
Não persiste ficha, mão, ordem de monte, tokens de modelo, prompts ou PV
privados. O executor real/modelo/sorteador são dependências externas.

O módulo não inicia nenhuma partida nem faz trabalho no chat em background.
"""
from __future__ import annotations

import json
import re
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Callable, Any


CAMPOS_PUBLICOS = frozenset({
    "passos_aceitos", "fase", "ator_da_vez", "versao_estado", "placar_fixture"
})
ESTADOS = frozenset({
    "NA_FILA", "EXECUTANDO", "AGUARDANDO_JOGADOR",
    "AGUARDANDO_DADOS", "PENDENTE_REGRA", "CONCLUIDO", "FALHOU",
    "CANCELADO",
})
ESTADOS_RETORNO_WORKER = ESTADOS - {"EXECUTANDO", "CANCELADO"}
PAUSADOS = frozenset({"AGUARDANDO_JOGADOR", "AGUARDANDO_DADOS", "PENDENTE_REGRA"})


class ErroFila(Exception):
    pass


def _id(value: str, nome: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value):
        raise ErroFila(f"{nome} inválido")
    return value


def _verificar_publico(dados: dict) -> dict:
    if not isinstance(dados, dict) or set(dados) != CAMPOS_PUBLICOS:
        raise ErroFila("resumo precisa conter apenas campos públicos conhecidos")
    passos = dados["passos_aceitos"]
    fase = dados["fase"]
    actor = dados["ator_da_vez"]
    versao = dados["versao_estado"]
    placar = dados["placar_fixture"]
    if (type(passos) is not int or not 0 <= passos <= 100000
            or not isinstance(fase, str) or not 1 <= len(fase) <= 40
            or actor not in ("J1", "J2", None)
            or not isinstance(versao, str) or not re.fullmatch(r"E\d{3,}", versao)
            or not isinstance(placar, dict) or set(placar) != {"J1", "J2"}
            or any(type(x) is not int or not 0 <= x <= 3 for x in placar.values())):
        raise ErroFila("valor inválido no resumo público")
    return {
        "passos_aceitos": passos, "fase": fase,
        "ator_da_vez": actor, "versao_estado": versao,
        "placar_fixture": {"J1": placar["J1"], "J2": placar["J2"]},
    }


class FilaBackground:
    """SQLite com transações curtas e fencing para worker em processo separado."""

    def __init__(self, arquivo_db: str | Path):
        path = Path(arquivo_db)
        if not path.parent.exists():
            raise ErroFila("diretório da fila não existe")
        self.path = str(path)
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS simulacoes (
                    id TEXT PRIMARY KEY,
                    referencia_opaca TEXT NOT NULL,
                    status TEXT NOT NULL,
                    versao_lease INTEGER NOT NULL DEFAULT 0,
                    token_lease TEXT,
                    worker_id TEXT,
                    lease_ate REAL,
                    criado_em REAL NOT NULL,
                    atualizado_em REAL NOT NULL,
                    resumo_publico TEXT
                )
            """)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def enfileirar(self, job_id: str, referencia_opaca: str,
                  *, agora: float | None = None) -> None:
        job_id = _id(job_id, "job_id")
        referencia_opaca = _id(referencia_opaca, "referencia_opaca")
        timestamp = time.time() if agora is None else agora
        with self._connect() as db:
            try:
                db.execute("""
                    INSERT INTO simulacoes
                    (id, referencia_opaca, status, criado_em, atualizado_em)
                    VALUES (?, ?, 'NA_FILA', ?, ?)
                """, (job_id, referencia_opaca, timestamp, timestamp))
            except sqlite3.IntegrityError as exc:
                raise ErroFila("job_id duplicado; não criar segunda simulação") from exc

    def reivindicar(self, worker_id: str, *, lease_segundos: int = 30,
                    agora: float | None = None) -> dict | None:
        worker_id = _id(worker_id, "worker_id")
        if type(lease_segundos) is not int or not 1 <= lease_segundos <= 3600:
            raise ErroFila("lease fora dos limites")
        now = time.time() if agora is None else agora
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""
                SELECT * FROM simulacoes
                WHERE status='NA_FILA'
                   OR (status='EXECUTANDO' AND lease_ate<=?)
                ORDER BY criado_em, id LIMIT 1
            """, (now,)).fetchone()
            if row is None:
                db.execute("COMMIT")
                return None
            fencing = row["versao_lease"] + 1
            token = secrets.token_hex(16)
            ate = now + lease_segundos
            db.execute("""
                UPDATE simulacoes SET status='EXECUTANDO',
                    worker_id=?, token_lease=?, versao_lease=?, lease_ate=?,
                    atualizado_em=?
                WHERE id=?
            """, (worker_id, token, fencing, ate, now, row["id"]))
            db.execute("COMMIT")
        # O token nunca aparece em status_publico ou no log da UI.
        return {
            "job_id": row["id"], "referencia_opaca": row["referencia_opaca"],
            "worker_id": worker_id, "token": token,
            "fencing": fencing, "lease_ate": ate,
        }

    def renovar(self, claim: dict, *, lease_segundos: int = 30,
                agora: float | None = None) -> bool:
        if type(lease_segundos) is not int or not 1 <= lease_segundos <= 3600:
            raise ErroFila("lease fora dos limites")
        now = time.time() if agora is None else agora
        with self._connect() as db:
            cursor = db.execute("""
                UPDATE simulacoes SET lease_ate=?, atualizado_em=?
                WHERE id=? AND status='EXECUTANDO'
                  AND token_lease=? AND worker_id=? AND versao_lease=?
                  AND lease_ate>?
            """, (now + lease_segundos, now, claim["job_id"],
                  claim["token"], claim["worker_id"], claim["fencing"], now))
            return cursor.rowcount == 1

    def confirmar(self, claim: dict, status: str, resumo_publico: dict,
                  *, agora: float | None = None) -> None:
        if status not in ESTADOS_RETORNO_WORKER:
            raise ErroFila("estado não permitido para confirmação do worker")
        summary = _verificar_publico(resumo_publico)
        now = time.time() if agora is None else agora
        with self._connect() as db:
            cur = db.execute("""
                UPDATE simulacoes SET status=?, resumo_publico=?,
                    atualizado_em=?, token_lease=NULL, worker_id=NULL,
                    lease_ate=NULL
                WHERE id=? AND status='EXECUTANDO'
                  AND token_lease=? AND worker_id=? AND versao_lease=?
                  AND lease_ate>?
            """, (status, json.dumps(summary, sort_keys=True, ensure_ascii=False),
                  now, claim["job_id"], claim["token"], claim["worker_id"],
                  claim["fencing"], now))
            if cur.rowcount != 1:
                raise ErroFila("lease expirado/cercado por outro worker; resultado descartado")

    def retomar(self, job_id: str, *, entrada_externa_validada: bool,
                agora: float | None = None) -> None:
        _id(job_id, "job_id")
        if entrada_externa_validada is not True:
            raise ErroFila("retomada exige confirmação externa de entrada confiável")
        now = time.time() if agora is None else agora
        with self._connect() as db:
            cur = db.execute("""
                UPDATE simulacoes SET status='NA_FILA', atualizado_em=?
                WHERE id=? AND status IN (
                    'AGUARDANDO_JOGADOR','AGUARDANDO_DADOS','PENDENTE_REGRA'
                )
            """, (now, job_id))
            if cur.rowcount != 1:
                raise ErroFila("job não aguardava dados/declaração/regra")

    def cancelar(self, job_id: str, *, agora: float | None = None) -> None:
        _id(job_id, "job_id")
        now = time.time() if agora is None else agora
        with self._connect() as db:
            cur = db.execute("""
                UPDATE simulacoes SET status='CANCELADO', atualizado_em=?,
                    token_lease=NULL, worker_id=NULL, lease_ate=NULL
                WHERE id=? AND status NOT IN ('CONCLUIDO','CANCELADO')
            """, (now, job_id))
            if cur.rowcount != 1:
                raise ErroFila("job não pode ser cancelado")

    def status_publico(self, job_id: str) -> dict:
        _id(job_id, "job_id")
        with self._connect() as db:
            row = db.execute("""
                SELECT id, status, atualizado_em, resumo_publico
                FROM simulacoes WHERE id=?
            """, (job_id,)).fetchone()
        if row is None:
            raise ErroFila("job não encontrado")
        return {
            "job_id": row["id"], "status": row["status"],
            "atualizado_em": row["atualizado_em"],
            "resumo": json.loads(row["resumo_publico"]) if row["resumo_publico"] else None,
        }


def executar_tick_worker(fila: FilaBackground, worker_id: str,
                         executor: Callable[[str], dict], *,
                         agora: float | None = None,
                         lease_segundos: int = 30) -> dict | None:
    """Um tick de processo independente. Executor deve salvar checkpoint privado.

    Recebe apenas referência opaca e devolve status de JobSimulacao.
    Não invoca IA nem sorteador: esses adaptadores ficam fora do banco/fila.
    """
    claim = fila.reivindicar(
        worker_id, lease_segundos=lease_segundos, agora=agora
    )
    if claim is None:
        return None
    try:
        status = executor(claim["referencia_opaca"])
        if not isinstance(status, dict):
            raise ErroFila("executor não retornou resumo")
        estado = status["estado"]
        if estado == "EXECUTANDO":
            estado = "NA_FILA"
        if estado not in ESTADOS_RETORNO_WORKER:
            raise ErroFila("estado do executor desconhecido")
        summary = _verificar_publico({
            k: status[k] for k in CAMPOS_PUBLICOS
        })
        fila.confirmar(claim, estado, summary, agora=agora)
        return fila.status_publico(claim["job_id"])
    except Exception:
        # Nunca grava traceback ou dados privados numa linha pública do banco.
        try:
            fila.confirmar(claim, "FALHOU", {
                "passos_aceitos": 0, "fase": "ERRO_WORKER",
                "ator_da_vez": None, "versao_estado": "E000",
                "placar_fixture": {"J1": 0, "J2": 0},
            }, agora=agora)
        except ErroFila:
            pass  # lease perdido: outro worker é autoridade
        raise

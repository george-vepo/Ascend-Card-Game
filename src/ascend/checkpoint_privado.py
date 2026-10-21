"""Storage privado cifrado de checkpoints do motor experimental (não homologado).

Não integra o worker nem executa IA. Nunca colocar esta base de dados no Git.
Chaves AES-256-GCM são fornecidas pelo backend e NÃO gravadas no banco.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sqlite3
import stat
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


MAX_BYTES = 2_000_000
REF_REGEX = re.compile(r"[A-Za-z0-9_-]{1,128}\Z")


class ErroCheckpoint(Exception):
    """Erro validado sem expor o conteúdo privado do checkpoint."""


class VersaoDesatualizada(ErroCheckpoint):
    """Tentativa de gravar com versão diferente da atual."""


def _ref(ref: str) -> str:
    if not isinstance(ref, str) or not REF_REGEX.fullmatch(ref):
        raise ErroCheckpoint("referência opaca inválida")
    return ref


def _aad(ref: str, versao: int) -> bytes:
    return f"ASCEND-CHECKPOINT-V1|{ref}|{versao}".encode("ascii")


class CheckpointPrivado:
    """SQLite contendo **somente ciphertext**, com CAS transacional e AES-256-GCM.

    Uso: `CheckpointPrivado(caminho_absoluto, chave_externa_32_bytes)`.
    Crie um diretório privado fora do Git antes da inicialização. Em sistemas POSIX,
    é exigido `0700` para o diretório e `0600` para a base SQLite.
    No Windows, o operador deve garantir o ACL de acesso à pasta externamente.
    """

    def __init__(self, arquivo_db: str | Path, chave: bytes):
        if not isinstance(chave, bytes) or len(chave) != 32:
            raise ErroCheckpoint("chave AES-256 deve conter 32 bytes, fornecidos pelo backend")
        path = Path(arquivo_db)
        if not path.is_absolute():
            raise ErroCheckpoint("caminho absoluto é obrigatório")
        if path.is_symlink() or path.parent.is_symlink():
            raise ErroCheckpoint("atalho simbólico não permitido")
        if not path.parent.is_dir():
            raise ErroCheckpoint("diretório privado não existe")
        if os.name == "posix":
            if stat.S_IMODE(path.parent.stat().st_mode) & 0o077:
                raise ErroCheckpoint("diretório deve ter permissões 0700 em POSIX")
        # SQLite auxiliares (.journal, .wal) só podem existir dentro da pasta privada.
        if path.exists():
            if not path.is_file():
                raise ErroCheckpoint("caminho do banco não é um arquivo regular")
            if os.name == "posix" and stat.S_IMODE(path.stat().st_mode) & 0o077:
                raise ErroCheckpoint("banco deve ter permissões 0600 em POSIX")
        else:
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            try:
                fd = os.open(path, flags, 0o600)
                os.close(fd)
            except FileExistsError:
                raise ErroCheckpoint("banco criado simultaneamente: reabrir depois") from None
        self.path = path
        self._aes = AESGCM(chave)
        with self._abrir() as db:
            db.execute("""
              CREATE TABLE IF NOT EXISTS checkpoints (
                referencia TEXT PRIMARY KEY,
                versao INTEGER NOT NULL CHECK(versao >= 1),
                nonce BLOB NOT NULL,
                cifra BLOB NOT NULL
              )
            """)

    def _abrir(self) -> sqlite3.Connection:
        db = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA journal_mode=DELETE")
        return db

    def salvar(self, referencia_opaca: str, estado_privado: dict[str, Any],
               *, versao_esperada: int) -> int:
        """Persistência CAS. Exigir versão 0 ao criar, ou a versão atual para atualizar.

        A nova versão é retornada. Somente o backend de controle pode fazer esta chamada.
        """
        ref = _ref(referencia_opaca)
        if type(versao_esperada) is not int or not 0 <= versao_esperada < 2**63-1:
            raise ErroCheckpoint("versão esperada inválida")
        if not isinstance(estado_privado, dict):
            raise ErroCheckpoint("checkpoint deve ser um objeto JSON")
        try:
            raw = json.dumps(estado_privado, ensure_ascii=False, allow_nan=False,
                             sort_keys=True, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError, OverflowError) as exc:
            raise ErroCheckpoint("checkpoint não é JSON válido") from None
        if not 2 <= len(raw) <= MAX_BYTES:
            raise ErroCheckpoint("tamanho do checkpoint fora do limite")
        nova = versao_esperada+1
        nonce = os.urandom(12)
        ciphertext = self._aes.encrypt(nonce, raw, _aad(ref, nova))
        with self._abrir() as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT versao FROM checkpoints WHERE referencia=?", (ref,)).fetchone()
                atual = int(row[0]) if row else 0
                if atual != versao_esperada:
                    raise VersaoDesatualizada("checkpoint obsoleto: recarregar versão")
                if atual == 0:
                    db.execute("INSERT INTO checkpoints VALUES (?,?,?,?)", (ref, nova, nonce, ciphertext))
                else:
                    db.execute("UPDATE checkpoints SET versao=?, nonce=?, cifra=? WHERE referencia=?",
                               (nova, nonce, ciphertext, ref))
                db.execute("COMMIT")
            except Exception:
                db.execute("ROLLBACK")
                raise
        return nova

    def carregar(self, referencia_opaca: str) -> dict[str, Any] | None:
        """Ler versão e estado, apenas para o backend com a chave privada válida."""
        ref = _ref(referencia_opaca)
        with self._abrir() as db:
            row = db.execute("SELECT versao,nonce,cifra FROM checkpoints WHERE referencia=?", (ref,)).fetchone()
        if row is None:
            return None
        versao,nonce,cifra = row
        try:
            raw = self._aes.decrypt(nonce, cifra, _aad(ref, versao))
            state = json.loads(raw)
            if not isinstance(state, dict):
                raise ErroCheckpoint("checkpoint incompatível")
        except (InvalidTag, ValueError, TypeError, json.JSONDecodeError):
            raise ErroCheckpoint("checkpoint inválido, corrompido ou chave incorreta") from None
        return {"versao": int(versao), "estado": state}

"""Servidor HTTP local para registrar manualmente combate simulado fora do jogo.

Uso de POC: servir interface e encaminhar somente resultado ao motor de
fixture validado. Não expor externamente nem utilizar como backend de produção:
faltam contas, autenticação de jogador, persistência oficial e HTTPS.
"""
from __future__ import annotations

import json
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
for rel in ("src", "experimental/legacy/src", "experimental/integration"):
    path = str(ROOT / rel)
    if path not in sys.path:
        sys.path.insert(0, path)

from motor_poc import digest, InvalidAction
from motor_roper_basico import SessaoRoperFixture
from resultado_combate_externo import (
    COMANDO_RESULTADO_EXTERNO, ORIGEM_EXTERNA,
)

WEBROOT = ROOT / "web" / "resultado-combate"
EXPECTED_PAYLOAD = frozenset({
    "evento_id", "combate_numero", "vencedor", "pv_restantes_vencedor",
    "versao_base", "hash_estado_base", "confirmacao_usuario",
})


def criar_servidor(sessao: SessaoRoperFixture, *,
                   host: str = "127.0.0.1", porta: int = 0):
    """O modo local impede expor uma action de árbitro sem autenticação."""
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("somente loopback: frontend POC sem autenticação remota")
    if not isinstance(sessao, SessaoRoperFixture):
        raise ValueError("somente SessaoRoperFixture validada")
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, status: int, data: dict):
            content = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; frame-ancestors 'none'")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def _send_static(self, filename: str, mime: str):
            content = (WEBROOT / filename).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            route = urlsplit(self.path).path
            if route == "/api/combate":
                with sessao_lock:
                    mesa = sessao.mesa_publica()
                    response = {
                        "modo": "FIXTURE_NAO_OFICIAL",
                        "mesa": mesa,
                        "versao_base": sessao.motor.state["versao"],
                        "hash_estado_base": digest(sessao.motor.state),
                        "combate_numero": sessao.motor.state["combate"]["numero"],
                        "token_formulario": token,
                    }
                return self._send_json(200, response)
            if route in ("/", "/index.html"):
                return self._send_static("index.html", "text/html; charset=utf-8")
            if route == "/styles.css":
                return self._send_static("styles.css", "text/css; charset=utf-8")
            if route == "/app.js":
                return self._send_static("app.js", "text/javascript; charset=utf-8")
            return self._send_json(404, {"erro": "recurso não encontrado"})

        def do_POST(self):
            if urlsplit(self.path).path != "/api/resultado":
                return self._send_json(404, {"erro": "endpoint não encontrado"})
            if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                return self._send_json(415, {"erro": "envie application/json"})
            if self.headers.get("X-CSRF-Token") != token:
                return self._send_json(403, {"erro": "token do formulário inválido"})
            origin = self.headers.get("Origin")
            if origin is not None:
                expected_origin = "http://" + self.headers.get("Host", "")
                if origin != expected_origin:
                    return self._send_json(403, {"erro": "origem do formulário inválida"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    return self._send_json(413, {"erro": "corpo fora do limite"})
                form = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeError, ValueError, TypeError, json.JSONDecodeError):
                return self._send_json(400, {"erro": "JSON inválido"})
            if not isinstance(form, dict) or set(form) != EXPECTED_PAYLOAD:
                return self._send_json(400, {"erro": "campos inválidos"})
            event_id = form["evento_id"]
            if (not isinstance(event_id, str) or not 1 <= len(event_id) <= 128
                    or any(not (c.isalnum() or c in "-_") for c in event_id)):
                return self._send_json(400, {"erro": "evento_id inválido"})
            params = {
                "combate_numero": form["combate_numero"],
                "vencedor": form["vencedor"],
                "pv_restantes_vencedor": form["pv_restantes_vencedor"],
                "versao_base": form["versao_base"],
                "hash_estado_base": form["hash_estado_base"],
                "origem": ORIGEM_EXTERNA,
                "confirmacao_usuario": form["confirmacao_usuario"],
            }
            with sessao_lock:
                try:
                    result = sessao.comando(
                        event_id, "ARBITRO", COMANDO_RESULTADO_EXTERNO, params
                    )
                except (InvalidAction, ValueError):
                    return self._send_json(
                        409, {"decisao": "REJEITADA", "motivo": "colisão de evento"})
                if result["decisao"] != "ACEITA":
                    motivo = result.get("motivo", "").lower()
                    stale = ("estado mudou" in motivo
                             or "hash do estado" in motivo
                             or "outro combate" in motivo)
                    status = 409 if stale else 422
                    return self._send_json(status, result)
                return self._send_json(200, {
                    "decisao": "ACEITA",
                    "registro": result["resultado"],
                    "mesa": sessao.mesa_publica(),
                })

    import threading
    sessao_lock = threading.RLock()
    server = ThreadingHTTPServer((host, porta), Handler)
    server.daemon_threads = True
    return server


def iniciar_demo_fixture(catalogo: str):
    """Exclusivamente demonstração local. Sem baralhamento nem partida oficial."""
    from ascend.catalogo_poc import ler_contrato
    from motor_roper_basico import ESCOPO_BASICO
    contrato = ler_contrato(ROOT)
    sessao = SessaoRoperFixture.criar_de_checkout(
        catalogo, contrato, primeiro="J2",
        maos_fixadas={
            "J1": ["CE-001", "CE-002", "CE-003", "CE-004", "CE-005"],
            "J2": ["AB-POC-017", "AB-POC-001", "AB-POC-002",
                   "AB-POC-003", "AB-POC-004"],
        },
    )
    counter = 0

    def aplicar(ator, cmd, params):
        nonlocal counter
        counter += 1
        result = sessao.comando("setup-site-" + str(counter), ator, cmd, params)
        if result["decisao"] != "ACEITA":
            raise RuntimeError("fixture inválida: " + repr(result))
    for p in ("J2", "J1"):
        aplicar(p, "TROCAR", {"descartar": []})
    for p, cid in (("J2", "AB-POC-017"), ("J1", "CE-001")):
        aplicar(p, "INVOCAR", {"carta_id": cid})
        aplicar(p, "PRONTO_CRIATURA", {})
    for p in ("J2", "J1"):
        aplicar(p, "ESCOLHER_SUPORTE", {"carta_id": None})
    for _ in range(2):
        aplicar("ARBITRO", "RESOLVER_SUPORTE_FIXTURE", {"resultado": "PULAR"})
    aplicar("ARBITRO", "INICIATIVA_ROPER_TESTE", {
        "aceite_escopo": ESCOPO_BASICO,
        "d20_simulados": {"J1": 1, "J2": 12},
    })
    return sessao


if __name__ == "__main__":
    import os
    source = os.environ.get("CATALOGO_SRD_DIR")
    if not source:
        raise SystemExit("Configure CATALOGO_SRD_DIR com checkout externo pinado")
    sessao = iniciar_demo_fixture(source)
    server = criar_servidor(sessao, porta=8765)
    print("Demo NÃO OFICIAL: http://127.0.0.1:8765", flush=True)
    print("Sem autenticação remota ou persistência oficial. Ctrl+C encerra.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

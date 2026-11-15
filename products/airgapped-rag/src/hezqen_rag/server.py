"""Local-only HTTP API for the air-gapped RAG stack."""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .engine import RagEngine, RagError

MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", "1048576"))
ENGINE = RagEngine()


class Handler(BaseHTTPRequestHandler):
    server_version = "HEZQEN-RAG/0.1"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, status: int, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/healthz":
            self._send(404, {"error": "not_found"})
            return
        try:
            self._send(200, {"status": "ok", "dependencies": ENGINE.health()})
        except RagError:
            self._send(503, {"error": "dependencies_unavailable"})

    def do_POST(self) -> None:  # noqa: N802
        routes = {"/v1/ingest", "/v1/query", "/v1/chat"}
        if self.path not in routes:
            self._send(404, {"error": "not_found"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send(415, {"error": "application_json_required"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, {"error": "invalid_content_length"})
            return
        if length < 1 or length > MAX_BODY_BYTES:
            self._send(413, {"error": "payload_size_rejected"})
            return
        try:
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                self._send(400, {"error": "json_object_required"})
                return
            if self.path == "/v1/ingest":
                result = ENGINE.ingest(payload.get("documents"))
            elif self.path == "/v1/query":
                result = {"results": ENGINE.search(payload.get("query"), payload.get("top_k", 4))}
            else:
                result = ENGINE.chat(payload.get("query"), payload.get("top_k", 4))
            self._send(200, result)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send(400, {"error": "invalid_json"})
        except ValueError as exc:
            self._send(400, {"error": str(exc)})
        except RagError:
            self._send(503, {"error": "rag_dependency_unavailable"})
        except Exception:
            self._send(500, {"error": "internal_error"})


def main() -> None:
    ThreadingHTTPServer((os.getenv("HOST", "0.0.0.0"), int(os.getenv("PORT", "8090"))), Handler).serve_forever()


if __name__ == "__main__":
    main()

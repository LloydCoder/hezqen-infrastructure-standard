"""Minimal standard-library HTTP service for local PII redaction."""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .engine import PiiPolicyViolation, RedactionEngine, RedactionError

MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", "1048576"))
ACTION = os.getenv("PII_ACTION", "redact")
if ACTION not in {"redact", "block"}:
    raise RuntimeError("HTTP service supports only redact or block policy actions")
ENGINE = RedactionEngine(action=ACTION)


class Handler(BaseHTTPRequestHandler):
    server_version = "HEZQEN-PII/0.1"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        # Do not write request paths, bodies, or PII-bearing data to logs.
        return

    def _send(self, status: int, body: dict[str, object]) -> None:
        encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/redact":
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
            if not isinstance(payload, dict) or not isinstance(payload.get("text"), (str, list, dict)):
                self._send(400, {"error": "json_object_with_text_required"})
                return
            result = ENGINE.redact_json(payload)
            self._send(200, {"result": result, "policy": ENGINE.action})
        except PiiPolicyViolation:
            self._send(422, {"error": "pii_policy_block"})
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send(400, {"error": "invalid_json"})
        except RedactionError:
            self._send(503, {"error": "redaction_unavailable"})
        except Exception:
            self._send(500, {"error": "internal_error"})


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()

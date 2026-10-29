"""Samostatný runner pre Vercel: spúšťa používateľský kód.

Tento projekt zámerne nemá prístup k databáze ani k žiadnym heslám okrem
RUNNER_TOKEN, ktorým sa overuje, že požiadavka prišla z API AlgoLab.
Aj keby kód používateľa obišiel statickú kontrolu, nemá sa k čomu dostať.

POST /api/run  {"op": "job" | "case", "payload": {...}, "timeout_ms": int}
"""

from __future__ import annotations

import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from algolab_sandbox.execute import run_case, run_job  # noqa: E402

MAX_BODY = 20 * 1024 * 1024


class handler(BaseHTTPRequestHandler):  # noqa: N801 (Vercel očakáva názov handler)
    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        self._send(200, {"status": "ok", "service": "algolab-runner"})

    def do_POST(self) -> None:  # noqa: N802
        token = os.environ.get("RUNNER_TOKEN", "")
        given = self.headers.get("X-Runner-Token", "")
        if not token or not hmac.compare_digest(token, given):
            self._send(401, {"error": "Neplatný token runnera"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self._send(413, {"error": "Neplatná veľkosť požiadavky"})
            return
        try:
            req = json.loads(self.rfile.read(length).decode("utf-8"))
            if req.get("op") == "case":
                out = run_case(req["payload"])
            else:
                out = run_job(req["payload"], timeout_ms=int(req.get("timeout_ms") or 10000))
        except Exception as exc:  # noqa: BLE001
            self._send(500, {"error": f"{type(exc).__name__}: {exc}"})
            return
        self._send(200, out)

"""Spúšťanie kódu: lokálne v samostatnom procese, alebo na vzdialenom runneri.

Lokálne (vývoj, Docker) sa volá runner/algolab_sandbox priamo. Pri nasadení
je nastavené RUNNER_URL a kód sa spúšťa na samostatnom Vercel projekte, ktorý
nemá prístup k databáze. API mu posiela úlohu cez HTTP s tokenom.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_RUNNER_DIR = Path(__file__).resolve().parents[3] / "runner"
if str(_RUNNER_DIR) not in sys.path:
    sys.path.insert(0, str(_RUNNER_DIR))

from algolab_sandbox import execute as _local  # noqa: E402
from algolab_sandbox.safety import UnsafeCode, check_code  # noqa: E402,F401

from ..config import settings  # noqa: E402


def _remote(op: str, payload: dict[str, Any], timeout_ms: int, http_timeout_s: float) -> dict[str, Any]:
    body = json.dumps({"op": op, "payload": payload, "timeout_ms": timeout_ms}).encode("utf-8")
    req = urllib.request.Request(
        settings.runner_url.rstrip("/") + "/api/run",
        data=body,
        headers={"Content-Type": "application/json", "X-Runner-Token": settings.runner_token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=http_timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        return {"status": "error", "error": f"Runner vrátil chybu {exc.code}: {detail}"}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"status": "error", "error": f"Runner nie je dostupný: {exc}"}


def run_job(job: dict[str, Any], timeout_ms: int) -> dict[str, Any]:
    if settings.runner_url:
        return _remote("job", job, timeout_ms, timeout_ms / 1000 + 20)
    return _local.run_job(job, timeout_ms=timeout_ms)


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    if settings.runner_url:
        return _remote("case", case, int(case.get("timeout_ms") or 5000), float(case.get("deadline_s") or 45) + 15)
    return _local.run_case(case)


def run_algorithm(code: str, data: Any, *, max_steps: int = 0, timeout_ms: int | None = None,
                  check_code_src: str | None = None, expected: Any = None,
                  return_result: bool = False) -> dict[str, Any]:
    job: dict[str, Any] = {"kind": "algorithm", "code": code, "input": data, "max_steps": max_steps,
                           "return_result": return_result}
    if check_code_src:
        job["check_code"] = check_code_src
    if expected is not None:
        job["expected"] = expected
    return run_job(job, timeout_ms or settings.default_timeout_ms)


def run_generator(code: str, n: int, params: dict, *, timeout_ms: int = 10000) -> dict[str, Any]:
    return run_job({"kind": "generate", "code": code, "n": n, "params": params}, timeout_ms)

"""Spúšťanie používateľského kódu v samostatnom procese.

Každé spustenie generátora alebo algoritmu je nový proces Pythonu:
  * dostane prázdne prostredie, takže nevidí heslá ani premenné servera,
  * má časový limit (proces sa po ňom ukončí) a limit procesora a pamäte
    (na Linuxe cez setrlimit),
  * meranie času prebieha vnútri procesu, takže štart interpretera sa
    do nameraného času nezapočíta.

Funkcia run_case vykoná jeden prípad experimentu: vygeneruje vstup,
spustí referenčný algoritmus a potom každý porovnávaný algoritmus na tom
istom vstupe.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import Any

CHILD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "child.py")

DEFAULT_LIMITS = {"memory_mb": 512, "recursion": 20000}


def _child_env() -> dict[str, str]:
    env = {"PYTHONHASHSEED": "0", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
    # Windows potrebuje SYSTEMROOT, inak interpreter nenaštartuje.
    for key in ("SYSTEMROOT", "SystemRoot"):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def run_job(job: dict[str, Any], timeout_ms: int = 10000) -> dict[str, Any]:
    """Spustí jednu úlohu. Vráti slovník so status ok, error alebo timeout."""
    limits = dict(DEFAULT_LIMITS)
    limits.update(job.get("limits") or {})
    limits["cpu_s"] = max(1, int(timeout_ms / 1000) + 1)
    payload = dict(job)
    payload["limits"] = limits
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, CHILD],
            input=data,
            capture_output=True,
            timeout=timeout_ms / 1000.0 + 1.0,
            env=_child_env(),
            cwd=os.path.dirname(CHILD),
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": f"Časový limit {timeout_ms} ms prekročený"}
    wall = (time.perf_counter() - t0) * 1000.0
    if proc.returncode != 0 and not proc.stdout:
        err = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        if proc.returncode < 0 or proc.returncode in (137, 139, -9, -11, 3221225725):
            reason = "Proces bol ukončený (prekročený limit pamäte alebo príliš hlboká rekurzia)"
        else:
            reason = err[-1] if err else f"Proces skončil s kódom {proc.returncode}"
        return {"status": "error", "error": reason}
    try:
        out = json.loads(proc.stdout.decode("utf-8"))
    except json.JSONDecodeError:
        return {"status": "error", "error": "Neplatný výstup z procesu"}
    if not out.get("ok"):
        return {"status": "error", "error": out.get("error", "Neznáma chyba"), "stdout": out.get("stdout")}
    if out.get("elapsed_ms", 0) > timeout_ms:
        return {"status": "timeout", "error": f"Časový limit {timeout_ms} ms prekročený"}
    out["status"] = "ok"
    out["wall_ms"] = wall
    return out


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    """Jeden prípad experimentu (variant, veľkosť, opakovanie).

    case = {
      "generator": {"code", "n", "params"},
      "reference": {"code"} alebo None,
      "check_code": str alebo None,
      "algorithms": [{"id", "code"}],
      "timeout_ms": int,
      "deadline_s": float  (celkový čas na prípad)
    }
    """
    timeout = int(case.get("timeout_ms") or 5000)
    deadline = time.perf_counter() + float(case.get("deadline_s") or 45.0)
    gen = case["generator"]
    g = run_job({"kind": "generate", "code": gen["code"], "n": gen["n"],
                 "params": gen.get("params") or {}}, timeout_ms=max(timeout, 10000))
    if g["status"] != "ok":
        return {"status": "generator_error", "error": g.get("error"), "results": {}}
    data = g["result"]

    expected = None
    reference_error = None
    ref = case.get("reference")
    if ref:
        r = run_job({"kind": "algorithm", "code": ref["code"], "input": data,
                     "return_result": True}, timeout_ms=max(timeout, 10000))
        if r["status"] == "ok":
            expected = r.get("result")
        else:
            reference_error = r.get("error")

    results: dict[str, Any] = {}
    for alg in case["algorithms"]:
        if time.perf_counter() > deadline:
            results[alg["id"]] = {"status": "timeout", "error": "Vyčerpaný čas na tento prípad experimentu"}
            continue
        job = {"kind": "algorithm", "code": alg["code"], "input": data,
               "check_code": case.get("check_code")}
        if ref and expected is not None:
            job["expected"] = expected
        res = run_job(job, timeout_ms=timeout)
        res.pop("steps", None)
        res.pop("result", None)
        results[alg["id"]] = res
    return {
        "status": "ok",
        "input_size": _size(data),
        "reference_error": reference_error,
        "results": results,
    }


def _size(data: Any) -> int | None:
    try:
        return len(data)
    except TypeError:
        return None

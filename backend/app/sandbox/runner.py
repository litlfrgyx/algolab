"""Spúšťanie používateľského kódu v izolovanom procese.

Bezpečnostné vrstvy:
  1. Statická kontrola (AST) — odmietne nebezpečné importy a volania.
  2. Samostatný proces (multiprocessing, kontext 'spawn' kvôli Windows).
  3. Timeout (process.join) → terminate.
  4. resource limits (CPU/pamäť) — len na Linux/Docker (pozri limits.py).

Funkcie `_worker`, `_static_check`, `_filter_kwargs` musia byť na úrovni modulu,
aby boli picklovateľné pre 'spawn'.
"""

from __future__ import annotations

import ast
import inspect
import multiprocessing as mp
import queue as queue_mod
import time
import tracemalloc
from typing import Any

from .limits import apply_limits
from .tracker_impl import RecordingTracker

# Povolené sú bežné „čisté" moduly; nebezpečné (FS/sieť/proces) sú zakázané.
_BANNED_MODULES = frozenset(
    {
        "os", "sys", "subprocess", "socket", "shutil", "pathlib",
        "ctypes", "threading", "multiprocessing", "importlib", "pickle",
        "builtins", "io", "requests", "urllib", "http",
    }
)


def _static_check(code: str) -> None:
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in _BANNED_MODULES:
                    raise ValueError(f"Zakázaný import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in _BANNED_MODULES:
                raise ValueError(f"Zakázaný import: {node.module}")
        elif isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            if name in ("__import__", "eval", "exec", "compile", "open"):
                raise ValueError(f"Zakázané volanie: {name}")


def _filter_kwargs(fn: Any, params: dict) -> dict:
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return params
    if any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values()):
        return params
    allowed = set(sig.parameters)
    return {k: v for k, v in params.items() if k in allowed}


def _accepts_tracker(fn: Any) -> bool:
    try:
        return len(inspect.signature(fn).parameters) >= 2
    except (TypeError, ValueError):
        return False


def _worker(kind, code, payload, max_steps, cpu_s, mem_bytes, q) -> None:
    try:
        apply_limits(cpu_s, mem_bytes)
        _static_check(code)
        namespace: dict[str, Any] = {}
        exec(compile(code, "<user-code>", "exec"), namespace)  # noqa: S102 (sandboxed)

        if kind == "algorithm":
            solve = namespace.get("solve")
            if not callable(solve):
                raise ValueError("Chýba funkcia solve(data) alebo solve(data, tracker)")
            data = payload["input"]
            tracker = RecordingTracker(max_steps)
            tracker.bind(data)
            tracemalloc.start()
            t0 = time.perf_counter()
            result = solve(data, tracker) if _accepts_tracker(solve) else solve(data)
            elapsed = (time.perf_counter() - t0) * 1000.0
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            q.put({
                "ok": True,
                "elapsed_ms": elapsed,
                "memory_kb": peak / 1024.0,
                "operation_counts": tracker.counts,
                "result": result,
                "steps": tracker.to_steps(),
                "truncated": tracker.truncated,
            })
        else:  # generator
            generate = namespace.get("generate")
            if not callable(generate):
                raise ValueError("Chýba funkcia generate(n, **params)")
            n = payload["n"]
            params = _filter_kwargs(generate, payload.get("params", {}))
            t0 = time.perf_counter()
            data = generate(n, **params)
            elapsed = (time.perf_counter() - t0) * 1000.0
            q.put({"ok": True, "elapsed_ms": elapsed, "result": data})
    except Exception as exc:  # noqa: BLE001 — chyba používateľského kódu sa hlási späť
        q.put({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


def _run(kind, code, payload, max_steps, timeout_ms, memory_mb) -> dict:
    ctx = mp.get_context("spawn")
    q: Any = ctx.Queue()
    cpu_s = max(1, int(timeout_ms / 1000) + 1)
    proc = ctx.Process(
        target=_worker,
        args=(kind, code, payload, max_steps, cpu_s, memory_mb * 1024 * 1024, q),
    )
    proc.start()
    try:
        res = q.get(timeout=timeout_ms / 1000 + 2.0)
    except queue_mod.Empty:
        proc.terminate()
        proc.join()
        return {"status": "timeout", "error": "Časový limit prekročený"}
    proc.join(2)
    if proc.is_alive():
        proc.terminate()
        proc.join()
    if not res.get("ok"):
        return {"status": "error", "error": res.get("error", "Neznáma chyba")}
    return {"status": "ok", **res}


def run_algorithm(
    code: str,
    data: Any,
    *,
    mode: str = "measure",
    max_steps: int = 2000,
    timeout_ms: int = 10000,
    memory_mb: int = 512,
) -> dict:
    """mode='visualize' → ukladá kroky; mode='measure' → iba počty + čas + pamäť."""
    steps = max_steps if mode == "visualize" else 0
    return _run("algorithm", code, {"input": data}, steps, timeout_ms, memory_mb)


def run_generator(
    code: str,
    n: int,
    params: dict,
    *,
    timeout_ms: int = 10000,
    memory_mb: int = 512,
) -> dict:
    return _run("generator", code, {"n": n, "params": params}, 0, timeout_ms, memory_mb)

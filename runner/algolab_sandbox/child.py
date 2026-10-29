"""Proces, v ktorom beží používateľský kód. Spúšťa ho execute.py.

Vstup: jedna úloha (job) ako JSON na štandardnom vstupe.
Výstup: výsledok ako JSON na štandardnom výstupe.

Druhy úloh:
  generate   zavolá generate(n, **params) a vráti vstup
  algorithm  zavolá solve(data) alebo solve(data, tracker), zmeria čas, pamäť
             a počty operácií a voliteľne overí výsledok funkciou check
"""

from __future__ import annotations

import copy
import inspect
import io
import json
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from limits import apply_limits  # noqa: E402
from safety import UnsafeCode, check_code  # noqa: E402
from tracker import RecordingTracker  # noqa: E402

USER_FILE = "<používateľský kód>"


def json_default(obj):
    if isinstance(obj, (set, frozenset)):
        try:
            return sorted(obj)
        except TypeError:
            return list(obj)
    if isinstance(obj, tuple):
        return list(obj)
    return str(obj)


def normalize(value):
    """Rovnaký tvar, aký prejde cez JSON: n-tice sú zoznamy, množiny zoradené."""
    return json.loads(json.dumps(value, default=json_default))


def user_error(exc: BaseException) -> str:
    """Čitateľná chyba s číslom riadku v kóde používateľa."""
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == USER_FILE:
            line = frame.lineno
    name = type(exc).__name__
    if isinstance(exc, RecursionError):
        msg = "Príliš hlboká rekurzia (RecursionError)"
    elif isinstance(exc, MemoryError):
        msg = "Prekročený pamäťový limit (MemoryError)"
    else:
        msg = f"{name}: {exc}"
    return f"{msg} (riadok {line})" if line else msg


def load(code: str, entry: str):
    check_code(code)
    namespace: dict = {"__name__": "user"}
    exec(compile(code, USER_FILE, "exec"), namespace)  # noqa: S102 (izolovaný proces)
    fn = namespace.get(entry)
    if not callable(fn):
        raise UnsafeCode(f"V kóde chýba funkcia {entry}()")
    return fn


def accepts_tracker(fn) -> bool:
    try:
        return len(inspect.signature(fn).parameters) >= 2
    except (TypeError, ValueError):
        return False


def filter_kwargs(fn, params: dict) -> dict:
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return params
    if any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values()):
        return params
    return {k: v for k, v in params.items() if k in sig.parameters}


def peak_rss_kb() -> float:
    """Maximálna rezidentná pamäť procesu v kB (na Linuxe), inde 0."""
    try:
        import resource
        return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except Exception:  # noqa: BLE001
        return 0.0


def run_generate(job: dict) -> dict:
    generate = load(job["code"], "generate")
    params = filter_kwargs(generate, job.get("params") or {})
    t0 = time.perf_counter()
    data = generate(job["n"], **params)
    elapsed = (time.perf_counter() - t0) * 1000.0
    return {"ok": True, "elapsed_ms": elapsed, "result": normalize(data)}


def run_check(check_code_src: str, original, result, expected):
    check = load(check_code_src, "check")
    try:
        params = len(inspect.signature(check).parameters)
    except (TypeError, ValueError):
        params = 3
    verdict = check(original, result, expected) if params >= 3 else check(original, result)
    if isinstance(verdict, tuple):
        ok = bool(verdict[0])
        message = str(verdict[1]) if len(verdict) > 1 and verdict[1] is not None else ""
    else:
        ok = bool(verdict)
        message = ""
    return ok, message


def run_algorithm(job: dict) -> dict:
    solve = load(job["code"], "solve")
    data = job["input"]
    check_src = job.get("check_code")
    expected = job.get("expected")
    has_expected = "expected" in job and expected is not None
    original = copy.deepcopy(data) if check_src else None
    tracker = RecordingTracker(int(job.get("max_steps") or 0), data)

    with_tracker = accepts_tracker(solve)
    # tracemalloc by meranie času skreslil (spomaľuje každú alokáciu, najmä pri rekurzii),
    # preto sa pamäť odhaduje z nárastu maximálnej rezidentnej pamäte procesu
    rss_before = peak_rss_kb()
    t0 = time.perf_counter()
    result = solve(data, tracker) if with_tracker else solve(data)
    elapsed = (time.perf_counter() - t0) * 1000.0
    peak = max(0.0, peak_rss_kb() - rss_before) * 1024.0

    out = {
        "ok": True,
        "elapsed_ms": elapsed,
        "memory_kb": peak / 1024.0,
        "operation_counts": tracker.operation_counts(),
        "uses_tracker": with_tracker,
        "steps": tracker.to_steps(),
        "structure": tracker.structure,
        "renderer": tracker.renderer or ("array" if tracker.steps and tracker.steps[0]["kind"] == "array" else None),
        "truncated": tracker.truncated,
        "is_correct": None,
        "check_message": None,
    }
    if job.get("return_result", False):
        out["result"] = normalize(result)

    if check_src:
        try:
            ok, message = run_check(check_src, original, normalize(result), expected)
            out["is_correct"] = ok
            out["check_message"] = message or None
        except Exception as exc:  # noqa: BLE001
            out["is_correct"] = None
            out["check_message"] = f"Chyba v kontrole správnosti: {user_error(exc)}"
    elif has_expected:
        same = normalize(result) == normalize(expected)
        out["is_correct"] = same
        if not same:
            out["check_message"] = "Výstup sa nezhoduje s referenčným algoritmom"
    return out


def main() -> None:
    raw = sys.stdin.buffer.read()
    job = json.loads(raw.decode("utf-8"))
    limits = job.get("limits") or {}
    apply_limits(int(limits.get("cpu_s", 10)), int(limits.get("memory_mb", 512)) * 1024 * 1024)
    sys.setrecursionlimit(int(limits.get("recursion", 20000)))
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)  # veľké čísla (faktoriál, 2^n) musia prejsť do JSON
    real_out = sys.stdout.buffer
    captured = io.StringIO()
    sys.stdout = captured  # print() v kóde používateľa nesmie pokaziť JSON výstup
    try:
        if job["kind"] == "generate":
            out = run_generate(job)
        else:
            out = run_algorithm(job)
    except SyntaxError as exc:
        out = {"ok": False, "error": f"Syntaktická chyba: {exc.msg} (riadok {exc.lineno})"}
    except UnsafeCode as exc:
        out = {"ok": False, "error": str(exc)}
    except BaseException as exc:  # noqa: BLE001
        out = {"ok": False, "error": user_error(exc)}
    sys.stdout = sys.__stdout__
    printed = captured.getvalue()
    if printed:
        out["stdout"] = printed[:4000]
    data = json.dumps(out, default=json_default, ensure_ascii=False)
    real_out.write(data.encode("utf-8"))
    real_out.flush()


if __name__ == "__main__":
    main()

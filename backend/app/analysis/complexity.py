"""Odhad triedy časovej zložitosti z nameraných dát.

Postup: pre každú kandidátnu triedu g(n) sa metódou najmenších štvorcov
nájde y ≈ a·g(n) + b s a ≥ 0 a vypočíta sa normalizovaná chyba (RMSE delené
priemerom y). Vyhrá trieda s najmenšou chybou. Ako doplnok sa počíta exponent k
z priamky v log-log súradniciach, teda y ≈ c·n^k.

Odhad sa robí zvlášť pre počet operácií (nezávisí od hardvéru, je presnejší)
a pre čas. Princíp zodpovedá meraniu empirickej zložitosti podľa
Goldsmith, Aiken, Wilkerson: Measuring Empirical Computational Complexity,
ESEC/FSE 2007, doi:10.1145/1287624.1287681, a knižnici big_O (P. Berkes),
ktorá tu nie je závislosťou.

Obmedzenia: odhad je len približný. Pri malom rozsahu n sa susedné triedy
(n a n log n) ťažko odlíšia. Časy v Pythone ovplyvňuje réžia interpretera
a vstavané funkcie implementované v C. Pri grafoch závisí výsledok od toho,
ako rastie počet hrán s počtom vrcholov.
"""

from __future__ import annotations

import math
from typing import Callable, Optional

PHI = (1 + 5 ** 0.5) / 2

CANDIDATES: dict[str, Callable[[float], float]] = {
    "O(1)": lambda n: 1.0,
    "O(log log n)": lambda n: math.log2(max(math.log2(max(n, 4)), 2)),
    "O(log n)": lambda n: math.log2(max(n, 2)),
    "O(n)": lambda n: float(n),
    "O(n log n)": lambda n: n * math.log2(max(n, 2)),
    "O(n^2)": lambda n: float(n) ** 2,
    "O(n^3)": lambda n: float(n) ** 3,
    "O(phi^n)": lambda n: PHI ** n,
    "O(2^n)": lambda n: 2.0 ** n,
    "O(3^n)": lambda n: 3.0 ** n,
}
EXPONENTIAL = {"O(2^n)", "O(phi^n)", "O(3^n)"}

MIN_POINTS = 4
MIN_RANGE = 2.5
MIN_TIME_MS = 0.05


def _fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Vráti (a, b, normalizovaná chyba) pre y ≈ a·x + b s a ≥ 0."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        a, b = 0.0, my
    else:
        a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
        b = my - a * mx
        if a < 0:
            a, b = 0.0, my
    rss = sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys))
    err = math.sqrt(rss / n) / my if my > 0 else float("inf")
    return a, b, err


def _loglog_exponent(ns: list[float], ys: list[float]) -> Optional[float]:
    pts = [(math.log(n), math.log(y)) for n, y in zip(ns, ys) if n > 1 and y > 0]
    if len(pts) < 3:
        return None
    lx = [p[0] for p in pts]
    ly = [p[1] for p in pts]
    mx = sum(lx) / len(lx)
    my = sum(ly) / len(ly)
    sxx = sum((x - mx) ** 2 for x in lx)
    if sxx == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(lx, ly)) / sxx


def fit_complexity(points: list[tuple[float, float]], metric: str) -> dict:
    """points = [(n, y)] priemery cez opakovania. Vráti slovník ComplexityFit."""
    clean = sorted((float(n), float(y)) for n, y in points if y is not None and y > 0 and n > 0)
    base = {"metric": metric, "status": "insufficient_data", "best": None, "second": None,
            "best_error": None, "second_error": None, "exponent": None, "confidence": "none",
            "reason": None}
    if len({n for n, _ in clean}) < MIN_POINTS:
        base["reason"] = f"Treba aspoň {MIN_POINTS} rôzne veľkosti vstupu s nameranou hodnotou"
        return base
    ns = [n for n, _ in clean]
    ys = [y for _, y in clean]
    if max(ns) / min(ns) < MIN_RANGE:
        base["reason"] = f"Veľkosti vstupu sa musia líšiť aspoň {MIN_RANGE:g}-násobne"
        return base
    if metric == "time" and max(ys) < MIN_TIME_MS:
        base["reason"] = "Namerané časy sú príliš krátke na spoľahlivý odhad"
        return base

    errors: dict[str, float] = {}
    for name, g in CANDIDATES.items():
        if name in EXPONENTIAL and max(ns) > 60:
            continue  # pri väčšom n by exponenciálna trieda pretiekla a aj tak by nevyhrala
        try:
            xs = [g(n) for n in ns]
            if any(math.isinf(x) for x in xs):
                continue
            _, _, err = _fit(xs, ys)
        except OverflowError:
            continue
        errors[name] = err
    ranked = sorted(errors.items(), key=lambda kv: kv[1])
    best, best_err = ranked[0]
    second, second_err = ranked[1] if len(ranked) > 1 else (None, None)

    if best_err > 0.25:
        confidence = "low"
    elif second_err is None or second_err >= 2.0 * max(best_err, 1e-9):
        confidence = "high"
    elif second_err >= 1.3 * max(best_err, 1e-9):
        confidence = "medium"
    else:
        confidence = "low"

    base.update(status="ok", best=best, second=second, best_error=round(best_err, 4),
                second_error=round(second_err, 4) if second_err is not None else None,
                exponent=_round(_loglog_exponent(ns, ys)), confidence=confidence)
    return base


def _round(x: Optional[float]) -> Optional[float]:
    return round(x, 2) if x is not None else None


def _same(a: Optional[str], b: Optional[str]) -> bool:
    if a is None or b is None:
        return False
    if a in EXPONENTIAL and b in EXPONENTIAL:
        return True
    return a == b


def estimate(op_points: list[tuple[float, float]], time_points: list[tuple[float, float]],
             declared: dict[str, Optional[str]]) -> dict:
    """Odhad pre jednu sériu a porovnanie s deklarovanou zložitosťou.

    declared = {"avg": ..., "worst": ..., "best": ...}
    """
    ops = fit_complexity(op_points, "operations")
    tim = fit_complexity(time_points, "time")
    used = ops if ops["status"] == "ok" else tim
    out = {"operations": ops, "time": tim, "declared": declared.get("avg"),
           "declared_case": "avg", "agreement": "unknown",
           "used_metric": used["metric"] if used["status"] == "ok" else "none"}
    if used["status"] != "ok":
        return out
    for case in ("avg", "worst", "best"):
        cls = declared.get(case)
        if cls and cls != "other" and _same(used["best"], cls):
            out.update(declared=cls, declared_case=case, agreement="match")
            return out
    cls = declared.get("avg")
    if not cls or cls == "other":
        return out
    if used["confidence"] == "low" or (used["confidence"] == "medium" and _same(used["second"], cls)):
        out["agreement"] = "unknown"
    else:
        out["agreement"] = "mismatch"
    return out

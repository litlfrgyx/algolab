"""Overenie vstavaného katalógu: každý algoritmus na každom druhu vstupu.

Spustenie:  python catalog_test.py [id_úlohy ...]

Pre každú úlohu a každú hodnotu prvého parametra generátora:
  * spustí všetky algoritmy na malom vstupe a overí správnosť výsledku,
  * pri zámerne nesprávnych algoritmoch overí, že kontrola aspoň raz zlyhá,
  * pri algoritmoch s vizualizáciou overí, že vzniknú kroky správneho druhu.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "runner"))

from algolab_sandbox.execute import run_case, run_job  # noqa: E402

from app.catalog import CATALOG  # noqa: E402
from app.deps import uses_tracker  # noqa: E402
from app import schemas  # noqa: E402
from typing import get_args  # noqa: E402

ALLOWED = {
    "category": set(get_args(schemas.ProblemCategory)),
    "input_type": set(get_args(schemas.InputType)),
    "renderer": set(get_args(schemas.RendererKind)),
    "paradigm": set(get_args(schemas.Paradigm)),
    "complexity": set(get_args(schemas.ComplexityClass)),
}

passed = 0
failed = 0


def ok(cond: bool, name: str, extra: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print(f"   XX {name} {extra}")


def param_sets(gen: dict) -> list[dict]:
    specs = gen.get("params") or []
    enums = [p for p in specs if p["type"] == "enum"]
    if not enums:
        return [{}]
    first = enums[0]
    sets = []
    for opt in first["options"]:
        base = {p["name"]: p["default"] for p in specs}
        base[first["name"]] = opt
        sets.append(base)
    return sets


def main(only: list[str]) -> None:
    for prob in CATALOG:
        if only and prob["id"] not in only:
            continue
        t0 = time.perf_counter()
        print(f"== {prob['id']} ({len(prob['algorithms'])} algoritmov)")
        for key in ("category", "input_type", "renderer"):
            ok(prob.get(key) in ALLOWED[key], f"{prob['id']} {key}={prob.get(key)}")
        for a in prob["algorithms"]:
            ok(a.get("paradigm", "iterative") in ALLOWED["paradigm"], f"{a['id']} paradigm={a.get('paradigm')}")
            for key in ("best", "avg", "worst", "space"):
                ok(a.get(key) is None or a[key] in ALLOWED["complexity"], f"{a['id']} {key}={a.get(key)}")
        ref = next((a for a in prob["algorithms"] if a["id"] == prob.get("reference")), None)
        wrong_seen = {a["id"]: False for a in prob["algorithms"] if "intentionally_incorrect" in a.get("properties", [])}
        for gen in prob["generators"]:
            small = gen.get("test_size") or min(gen["sizes"][0], 40)
            for params in param_sets(gen):
                for seed in (1, 2, 3):
                    case = {
                        "generator": {"code": gen["code"], "n": small, "params": dict(params, seed=seed)},
                        "reference": {"code": ref["code"]} if ref else None,
                        "check_code": prob.get("checker"),
                        "algorithms": [{"id": a["id"], "code": a["code"]} for a in prob["algorithms"]],
                        "timeout_ms": 8000,
                    }
                    out = run_case(case)
                    ok(out["status"] == "ok", f"{gen['id']} {params}", str(out.get("error")))
                    if out["status"] != "ok":
                        continue
                    ok(not out.get("reference_error"), "referencia", str(out.get("reference_error")))
                    for a in prob["algorithms"]:
                        res = out["results"][a["id"]]
                        name = f"{a['id']} {params} seed={seed}"
                        ok(res["status"] == "ok", name, str(res.get("error")))
                        if res["status"] != "ok":
                            continue
                        if a["id"] in wrong_seen:
                            if res["is_correct"] is False:
                                wrong_seen[a["id"]] = True
                        else:
                            ok(res["is_correct"] is True, name, f"is_correct={res['is_correct']} {res.get('check_message')}")
                        ok(res["operation_counts"].get("total", 0) > 0, name + " počíta operácie")
            # vizualizácia
            g = run_job({"kind": "generate", "code": gen["code"], "n": gen.get("viz_size", 10),
                         "params": {p["name"]: p["default"] for p in gen.get("params") or []}})
            ok(g["status"] == "ok", f"viz generátor {gen['id']}", str(g.get("error")))
            if g["status"] != "ok":
                continue
            for a in prob["algorithms"]:
                if not (a.get("viz", True) and uses_tracker(a["code"]) and prob.get("renderer") != "none"):
                    continue
                r = run_job({"kind": "algorithm", "code": a["code"], "input": g["result"], "max_steps": 3000})
                ok(r["status"] == "ok", f"viz {a['id']}", str(r.get("error")))
                if r["status"] == "ok":
                    steps = r["steps"]
                    ok(len(steps) > 0, f"viz {a['id']} má kroky")
                    kinds = {s["kind"] for s in steps}
                    ok(kinds == {prob["renderer"]}, f"viz {a['id']} druh krokov", str(kinds))
        for aid, seen in wrong_seen.items():
            ok(seen, f"{aid} má aspoň raz zlyhať kontrolu")
        print(f"   {time.perf_counter() - t0:.1f} s")
    print(f"\nVÝSLEDOK: {passed} prešlo, {failed} zlyhalo")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])

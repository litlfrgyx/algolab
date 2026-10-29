"""Smoke test backendu — overí sandbox runner a executor bez HTTP servera.

Spustenie:  python smoke_test.py
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import executor, models
from app.db import Base
from app.sandbox.runner import run_algorithm, run_generator
from app.seed import CODE_BUBBLE, CODE_QUICK, seed_if_empty

passed = 0
failed = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"  OK  {name}")
    else:
        failed += 1
        print(f"  XX  {name}  {extra}")


def is_sorted(a: list) -> bool:
    return all(a[i - 1] <= a[i] for i in range(1, len(a)))


def main() -> None:
    print("— runner: vizualizácia —")
    viz = run_algorithm(CODE_BUBBLE, [5, 3, 1, 4, 2], mode="visualize", max_steps=4000)
    check("bubble status ok", viz["status"] == "ok", str(viz.get("error")))
    check("bubble má kroky", len(viz["steps"]) > 0)
    check("prvý krok kind=array", viz["steps"][0]["kind"] == "array")
    check("výsledok zotriedený", is_sorted(viz["result"]))
    check("compare > 0", viz["operation_counts"].get("compare", 0) > 0)
    check("snímok v kroku == array pole", "array" in viz["steps"][0])

    print("— runner: meranie (bez snímkov) —")
    meas = run_algorithm(CODE_QUICK, [5, 3, 1, 4, 2], mode="measure")
    check("quick status ok", meas["status"] == "ok")
    check("meranie nemá kroky (max_steps=0)", len(meas["steps"]) == 0)
    check("meranie má počty operácií", meas["operation_counts"].get("compare", 0) > 0)
    check("meranie má čas a pamäť", meas["elapsed_ms"] >= 0 and meas["memory_kb"] > 0)

    print("— runner: generátor —")
    from app.seed import CODE_GENERATOR
    g_sorted = run_generator(CODE_GENERATOR, 8, {"mode": "sorted"})
    g_r1 = run_generator(CODE_GENERATOR, 10, {"mode": "random", "seed": 1})
    g_r1b = run_generator(CODE_GENERATOR, 10, {"mode": "random", "seed": 1})
    g_r2 = run_generator(CODE_GENERATOR, 10, {"mode": "random", "seed": 2})
    check("sorted → vzostupné", is_sorted(g_sorted["result"]))
    check("rovnaký seed → rovnaký vstup", g_r1["result"] == g_r1b["result"])
    check("iný seed → iný vstup", g_r1["result"] != g_r2["result"])

    print("— runner: sandbox odmietne import os —")
    bad = run_algorithm("import os\ndef solve(data): return data", [1, 2, 3])
    check("import os → error", bad["status"] == "error" and "os" in str(bad.get("error")))

    print("— executor: malý experiment (temp DB) —")
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    seed_if_empty(db)
    tiny = models.Experiment(
        id="exp_tiny", name="tiny", problem_id="prob_sorting",
        algorithm_ids=["alg_bubble", "alg_quick"], generator_id="gen_array",
        sizes=[20, 40], repeats=2, timeout_ms=10000, seed=1,
        generator_params={"mode": "random"}, status="pending",
    )
    db.add(tiny)
    db.commit()
    executor.run_experiment(db, tiny)
    runs = db.query(models.ExperimentRun).filter_by(experiment_id="exp_tiny").all()
    check("počet behov = 2×2×2 = 8", len(runs) == 8, f"={len(runs)}")
    check("všetky ok", all(r.status == "ok" for r in runs))
    check("všetky korektné (vs referencia)", all(r.is_correct for r in runs))
    b40 = [r for r in runs if r.algorithm_id == "alg_bubble" and r.input_size == 40]
    q40 = [r for r in runs if r.algorithm_id == "alg_quick" and r.input_size == 40]
    b_cmp = sum(r.operation_counts.get("compare", 0) for r in b40) / len(b40)
    q_cmp = sum(r.operation_counts.get("compare", 0) for r in q40) / len(q40)
    check("n=40: bubble má viac porovnaní než quick", b_cmp > q_cmp, f"b={b_cmp} q={q_cmp}")
    check("experiment status = done", tiny.status == "done")

    print(f"\nVÝSLEDOK: {passed} prešlo, {failed} zlyhalo")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

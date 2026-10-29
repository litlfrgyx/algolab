"""Naseedovanie databázy demo dátami (sorting problém).

Zrkadlí seed z frontendu (rovnaké id), aby boli dáta konzistentné. Spustí sa
pri štarte, ak je DB prázdna. Experiment sa NESPÚŠŤA automaticky (sandbox behy
môžu trvať) — používateľ ho spustí cez POST /api/experiments/{id}/run.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from . import models

CODE_BUBBLE = '''def solve(data, tracker):
    n = len(data)
    for i in range(n):
        for j in range(n - i - 1):
            tracker.compare(j, j + 1)
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                tracker.swap(j, j + 1)
        tracker.mark_sorted([n - i - 1])
    return data'''

CODE_QUICK = '''def solve(data, tracker):
    def partition(lo, hi):
        tracker.pivot(hi)
        pivot = data[hi]
        i = lo - 1
        for j in range(lo, hi):
            tracker.compare(j, hi)
            if data[j] <= pivot:
                i += 1
                if i != j:
                    data[i], data[j] = data[j], data[i]
                    tracker.swap(i, j)
        data[i + 1], data[hi] = data[hi], data[i + 1]
        tracker.swap(i + 1, hi)
        return i + 1

    def qs(lo, hi):
        if lo < hi:
            p = partition(lo, hi)
            tracker.mark_sorted([p])
            qs(lo, p - 1)
            qs(p + 1, hi)

    qs(0, len(data) - 1)
    return data'''

CODE_INSERTION = '''def solve(data, tracker):
    for i in range(1, len(data)):
        j = i
        while j > 0:
            tracker.compare(j - 1, j)
            if data[j - 1] > data[j]:
                data[j - 1], data[j] = data[j], data[j - 1]
                tracker.swap(j - 1, j)
                j -= 1
            else:
                break
    return data'''

CODE_GENERATOR = '''def generate(n, mode="random", seed=42):
    import random
    rng = random.Random(seed)
    if mode == "sorted":
        return list(range(n))
    if mode in ("reverse", "worst_case"):
        return list(range(n, 0, -1))
    return [rng.randint(-1000, 1000) for _ in range(n)]'''


def seed_if_empty(db: Session) -> None:
    if db.query(models.Problem).count() > 0:
        return

    db.add(
        models.Problem(
            id="prob_sorting",
            name="Comparison Sort Benchmark",
            description="Porovnanie triediacich algoritmov na rôznych vstupoch.",
            category="sorting",
            input_description="list[int] — pole celých čísel",
            output_description="list[int] — neklesajúco zotriedené pole",
            reference_algorithm_id="alg_bubble",
        )
    )
    for aid, name, code, ref in [
        ("alg_bubble", "Bubble Sort", CODE_BUBBLE, True),
        ("alg_quick", "Quick Sort", CODE_QUICK, False),
        ("alg_insertion", "Insertion Sort", CODE_INSERTION, False),
    ]:
        db.add(
            models.Algorithm(
                id=aid,
                problem_id="prob_sorting",
                name=name,
                code=code,
                language="python",
                is_reference=ref,
                supports_visualization="tracker" in code,
            )
        )
    db.add(
        models.InputGenerator(
            id="gen_array",
            problem_id="prob_sorting",
            name="Pole celých čísel",
            code=CODE_GENERATOR,
            default_sizes=[10, 100, 500, 1000, 2000],
            param_spec=[
                {
                    "name": "mode",
                    "label": "Rozloženie",
                    "type": "enum",
                    "options": ["random", "sorted", "reverse", "worst_case"],
                    "default": "random",
                }
            ],
        )
    )
    # Sada experimentov pokrývajúca rôzne scenáre (vplyv rozloženia vstupu —
    # best/avg/worst case, kap. 2.1.4). Pri zotriedenom/inverznom vstupe sa
    # Quick Sort s pivotom na konci zvrhne na O(n²) — preto menšie veľkosti
    # (rekurzia do hĺbky n).
    experiments = [
        dict(
            id="exp_sort",
            name="Bubble vs Quick — náhodný vstup",
            algorithm_ids=["alg_bubble", "alg_quick"],
            sizes=[100, 500, 1000, 2000],
            generator_params={"mode": "random"},
        ),
        dict(
            id="exp_threeway",
            name="Tri algoritmy — náhodný vstup",
            algorithm_ids=["alg_bubble", "alg_insertion", "alg_quick"],
            sizes=[100, 300, 600, 1000],
            generator_params={"mode": "random"},
        ),
        dict(
            id="exp_worstcase",
            name="Najhorší prípad — inverzný vstup",
            algorithm_ids=["alg_bubble", "alg_insertion", "alg_quick"],
            sizes=[50, 150, 300, 500],
            generator_params={"mode": "reverse"},
        ),
        dict(
            id="exp_bestcase",
            name="Najlepší prípad — zotriedený vstup",
            algorithm_ids=["alg_insertion", "alg_quick"],
            sizes=[100, 300, 500],
            generator_params={"mode": "sorted"},
        ),
    ]
    for cfg in experiments:
        db.add(
            models.Experiment(
                problem_id="prob_sorting",
                generator_id="gen_array",
                repeats=3,
                timeout_ms=30000,
                seed=42,
                status="pending",
                **cfg,
            )
        )
    db.commit()

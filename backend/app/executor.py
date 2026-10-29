"""Vykonanie experimentu po dávkach.

Experiment sa skladá z prípadov (variant vstupu × veľkosť × opakovanie). V každom
prípade sa raz vygeneruje vstup, spustí sa referenčný algoritmus (ak existuje)
a potom každý porovnávaný algoritmus na tom istom vstupe.

Klient volá POST /experiments/{id}/start a potom opakovane POST /step. Každé
volanie spracuje toľko prípadov, koľko sa zmestí do časového rozpočtu
(STEP_BUDGET_S), a vráti priebeh. Tento spôsob funguje rovnako lokálne aj
v serverless prostredí (Vercel), kde funkcia nesmie bežať dlho a nedrží
otvorené spojenie.

Reprodukovateľnosť: seed prípadu = seed experimentu + index opakovania, takže
všetky algoritmy dostanú v danom prípade rovnaký vstup a beh sa dá zopakovať.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from . import models
from .config import settings
from .sandbox.runner import run_case


def _uid() -> str:
    return f"run_{uuid.uuid4().hex[:12]}"


def variants_of(experiment: models.Experiment) -> list[dict[str, Any]]:
    variants = list(experiment.variants or [])
    if not variants:
        variants = [{"label": "predvolený vstup", "params": dict(experiment.generator_params or {})}]
    return variants


def total_cases(experiment: models.Experiment) -> int:
    return len(variants_of(experiment)) * len(experiment.sizes or []) * max(1, experiment.repeats or 1)


def _case_at(experiment: models.Experiment, index: int) -> tuple[int, dict, int, int]:
    variants = variants_of(experiment)
    sizes = list(experiment.sizes or [])
    repeats = max(1, experiment.repeats or 1)
    per_variant = len(sizes) * repeats
    v = index // per_variant
    rest = index % per_variant
    return v, variants[v], sizes[rest // repeats], rest % repeats


def start(db: Session, experiment: models.Experiment) -> None:
    db.query(models.ExperimentRun).filter(models.ExperimentRun.experiment_id == experiment.id).delete()
    experiment.total_cases = total_cases(experiment)
    experiment.done_cases = 0
    experiment.status = "running"
    experiment.started_at = datetime.now(timezone.utc)
    experiment.finished_at = None
    db.commit()


def step(db: Session, experiment: models.Experiment, budget_s: float | None = None) -> list[str]:
    """Spracuje ďalšie prípady experimentu. Vráti zoznam chýb z tejto dávky."""
    if experiment.status != "running":
        return []
    budget = settings.step_budget_s if budget_s is None else budget_s
    t0 = time.perf_counter()
    errors: list[str] = []

    algorithms = (
        db.query(models.Algorithm).filter(models.Algorithm.id.in_(experiment.algorithm_ids)).all()
    )
    order = {aid: i for i, aid in enumerate(experiment.algorithm_ids)}
    algorithms.sort(key=lambda a: order.get(a.id, 0))
    generator = db.get(models.InputGenerator, experiment.generator_id)
    problem = db.get(models.Problem, experiment.problem_id)
    if generator is None or problem is None or not algorithms:
        experiment.status = "failed"
        experiment.finished_at = datetime.now(timezone.utc)
        db.commit()
        return ["Experiment nemá úlohu, generátor alebo algoritmy"]
    reference = db.get(models.Algorithm, problem.reference_algorithm_id) if problem.reference_algorithm_id else None
    timeout = min(int(experiment.timeout_ms or settings.default_timeout_ms), settings.max_timeout_ms)
    base_seed = experiment.seed if experiment.seed is not None else 0
    total = experiment.total_cases or total_cases(experiment)

    while experiment.done_cases < total:
        if time.perf_counter() - t0 > budget and experiment.done_cases > 0:
            break
        v_idx, variant, size, repeat = _case_at(experiment, experiment.done_cases)
        params = dict(experiment.generator_params or {})
        params.update(variant.get("params") or {})
        params["seed"] = base_seed + repeat
        case = {
            "generator": {"code": generator.code, "n": size, "params": params},
            "reference": {"code": reference.code} if reference is not None else None,
            "check_code": problem.checker_code,
            "algorithms": [{"id": a.id, "code": a.code} for a in algorithms],
            "timeout_ms": timeout,
            "deadline_s": 40.0,
        }
        out = run_case(case)
        label = variant.get("label", "")
        if out.get("status") != "ok":
            msg = out.get("error") or "Generátor zlyhal"
            errors.append(f"Generátor ({label}, n={size}): {msg}")
            for a in algorithms:
                _add_run(db, experiment, a.id, v_idx, label, size, repeat, status="error",
                         error=f"Vstup sa nepodarilo vygenerovať: {msg}")
        else:
            if out.get("reference_error"):
                errors.append(f"Referenčný algoritmus: {out['reference_error']}")
            results = out.get("results") or {}
            for a in algorithms:
                res = results.get(a.id) or {"status": "error", "error": "Chýba výsledok"}
                if res.get("status") != "ok":
                    status = "timeout" if res.get("status") == "timeout" else "error"
                    _add_run(db, experiment, a.id, v_idx, label, size, repeat, status=status,
                             error=res.get("error"))
                    if status == "error":
                        errors.append(f"{a.name} (n={size}): {res.get('error')}")
                    continue
                _add_run(
                    db, experiment, a.id, v_idx, label, size, repeat,
                    status="ok",
                    time_ms=res.get("elapsed_ms"),
                    memory_kb=res.get("memory_kb"),
                    operation_counts=res.get("operation_counts") or {},
                    is_correct=res.get("is_correct"),
                    check_message=res.get("check_message"),
                )
        experiment.done_cases += 1
        db.commit()

    if experiment.done_cases >= total:
        experiment.status = "done"
        experiment.finished_at = datetime.now(timezone.utc)
        db.commit()
    return errors


def run_experiment(db: Session, experiment: models.Experiment) -> None:
    """Celý experiment naraz (testy, príkazový riadok)."""
    start(db, experiment)
    while experiment.status == "running":
        step(db, experiment, budget_s=3600)


def _add_run(db: Session, experiment: models.Experiment, algorithm_id: str, variant_index: int,
             variant_label: str, size: int, repeat: int, *, status: str,
             time_ms: float | None = None, memory_kb: float | None = None,
             operation_counts: dict | None = None, is_correct: bool | None = None,
             check_message: str | None = None, error: str | None = None) -> None:
    db.add(models.ExperimentRun(
        id=_uid(),
        experiment_id=experiment.id,
        algorithm_id=algorithm_id,
        variant_index=variant_index,
        variant_label=variant_label,
        input_size=size,
        repeat_index=repeat,
        execution_time_ms=time_ms,
        memory_kb=memory_kb,
        operation_counts=operation_counts or {},
        is_correct=is_correct,
        check_message=check_message,
        status=status,
        error_message=error,
    ))

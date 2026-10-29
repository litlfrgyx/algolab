"""Orchestrácia experimentu: pre každú (algoritmus × veľkosť × opakovanie)
vygeneruje vstup, spustí algoritmus v sandboxe, zmeria a uloží ExperimentRun.

Reprodukovateľnosť: seed pre dané opakovanie = experiment.seed + repeat_index,
takže všetky algoritmy dostanú pri danom (veľkosť, opakovanie) ROVNAKÝ vstup
(spravodlivé porovnanie) a beh sa dá zopakovať.

Korektnosť: ak má problém referenčný algoritmus, výstup sa porovná s jeho
výstupom (is_correct). Bez referencie je is_correct = None.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from . import models
from .config import settings
from .sandbox.runner import run_algorithm, run_generator


def _uid() -> str:
    return f"run_{uuid.uuid4().hex[:10]}"


def run_experiment(db: Session, experiment: models.Experiment) -> None:
    algorithms = (
        db.query(models.Algorithm)
        .filter(models.Algorithm.id.in_(experiment.algorithm_ids))
        .all()
    )
    by_id = {a.id: a for a in algorithms}
    generator = db.get(models.InputGenerator, experiment.generator_id)
    problem = db.get(models.Problem, experiment.problem_id)
    if generator is None or problem is None:
        experiment.status = "failed"
        db.commit()
        return

    reference = (
        by_id.get(problem.reference_algorithm_id)
        if problem.reference_algorithm_id
        else None
    )

    # čistý re-run: zmaž predošlé behy tohto experimentu
    db.query(models.ExperimentRun).filter(
        models.ExperimentRun.experiment_id == experiment.id
    ).delete()

    experiment.status = "running"
    experiment.started_at = datetime.now(timezone.utc)
    db.commit()

    base_seed = experiment.seed if experiment.seed is not None else 0
    timeout = experiment.timeout_ms or settings.default_timeout_ms

    try:
        for size in experiment.sizes:
            for repeat in range(experiment.repeats):
                params = dict(experiment.generator_params or {})
                params["seed"] = base_seed + repeat
                gen = run_generator(generator.code, size, params, timeout_ms=timeout)
                if gen["status"] != "ok":
                    # vstup sa nevygeneroval → označ všetky algoritmy ako error
                    for alg in algorithms:
                        _add_run(db, experiment.id, alg.id, size, repeat,
                                 status="error", error=gen.get("error"))
                    continue
                data = gen["result"]

                reference_output = None
                if reference is not None:
                    ref_res = run_algorithm(reference.code, data, mode="measure", timeout_ms=timeout)
                    if ref_res["status"] == "ok":
                        reference_output = ref_res["result"]

                for alg in algorithms:
                    res = run_algorithm(alg.code, data, mode="measure", timeout_ms=timeout)
                    if res["status"] != "ok":
                        _add_run(db, experiment.id, alg.id, size, repeat,
                                 status=res["status"], error=res.get("error"))
                        continue
                    is_correct = (
                        (res["result"] == reference_output)
                        if reference_output is not None
                        else None
                    )
                    _add_run(
                        db, experiment.id, alg.id, size, repeat,
                        status="ok",
                        time_ms=res["elapsed_ms"],
                        memory_kb=res["memory_kb"],
                        operation_counts=res["operation_counts"],
                        is_correct=is_correct,
                    )
                db.commit()
        experiment.status = "done"
    except Exception:  # noqa: BLE001
        experiment.status = "failed"
        raise
    finally:
        experiment.finished_at = datetime.now(timezone.utc)
        db.commit()


def _add_run(
    db: Session,
    experiment_id: str,
    algorithm_id: str,
    size: int,
    repeat: int,
    *,
    status: str,
    time_ms: float | None = None,
    memory_kb: float | None = None,
    operation_counts: dict | None = None,
    is_correct: bool | None = None,
    error: str | None = None,
) -> None:
    db.add(
        models.ExperimentRun(
            id=_uid(),
            experiment_id=experiment_id,
            algorithm_id=algorithm_id,
            input_size=size,
            repeat_index=repeat,
            execution_time_ms=time_ms,
            memory_kb=memory_kb,
            operation_counts=operation_counts or {},
            is_correct=is_correct,
            status=status,
            error_message=error,
        )
    )

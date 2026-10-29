from __future__ import annotations

import csv
import io
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import executor, models, schemas
from ..analysis.complexity import estimate
from ..config import settings
from ..db import get_db

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


def _get(db: Session, experiment_id: str) -> models.Experiment:
    experiment = db.get(models.Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(404, f"Experiment '{experiment_id}' neexistuje")
    return experiment


@router.get("", response_model=list[schemas.Experiment])
def list_experiments(problem_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Experiment)
    if problem_id:
        q = q.filter(models.Experiment.problem_id == problem_id)
    return q.order_by(models.Experiment.created_at.desc()).all()


@router.post("", response_model=schemas.Experiment, status_code=201)
def create_experiment(body: schemas.CreateExperimentRequest, db: Session = Depends(get_db)):
    problem = db.get(models.Problem, body.problem_id)
    if problem is None:
        raise HTTPException(404, "Úloha neexistuje")
    if not body.algorithm_ids:
        raise HTTPException(400, "Vyber aspoň jeden algoritmus")
    if len(body.algorithm_ids) > settings.max_algorithms_per_experiment:
        raise HTTPException(400, f"Najviac {settings.max_algorithms_per_experiment} algoritmov v jednom experimente")
    algs = db.query(models.Algorithm).filter(models.Algorithm.id.in_(body.algorithm_ids)).all()
    if len(algs) != len(set(body.algorithm_ids)) or any(a.problem_id != body.problem_id for a in algs):
        raise HTTPException(400, "Algoritmy musia patriť k zvolenej úlohe")
    generator = db.get(models.InputGenerator, body.generator_id)
    if generator is None or generator.problem_id != body.problem_id:
        raise HTTPException(400, "Generátor musí patriť k zvolenej úlohe")
    sizes = sorted({int(s) for s in body.sizes if int(s) >= 0})
    if not sizes:
        raise HTTPException(400, "Zadaj aspoň jednu veľkosť vstupu")
    if len(sizes) > 12:
        raise HTTPException(400, "Najviac 12 veľkostí vstupu")
    repeats = max(1, min(int(body.repeats), 10))
    variants = [v.model_dump() for v in body.variants][:6]
    data = body.model_dump()
    data.update(sizes=sizes, repeats=repeats, variants=variants,
                timeout_ms=min(int(body.timeout_ms), settings.max_timeout_ms))
    experiment = models.Experiment(id=f"exp_{uuid.uuid4().hex[:8]}", is_builtin=False, **data)
    experiment.total_cases = executor.total_cases(experiment)
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@router.get("/{experiment_id}", response_model=schemas.Experiment)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    return _get(db, experiment_id)


@router.delete("/{experiment_id}", status_code=204)
def delete_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = db.get(models.Experiment, experiment_id)
    if experiment is None:
        return
    if experiment.is_builtin:
        raise HTTPException(403, "Vstavaný experiment sa nedá zmazať")
    db.query(models.ExperimentRun).filter(models.ExperimentRun.experiment_id == experiment_id).delete()
    db.delete(experiment)
    db.commit()


def _progress(experiment: models.Experiment, errors: list[str]) -> schemas.ExperimentProgress:
    return schemas.ExperimentProgress(
        experiment=schemas.Experiment.model_validate(experiment),
        completed_cases=experiment.done_cases or 0,
        total_cases=experiment.total_cases or executor.total_cases(experiment),
        finished=experiment.status in ("done", "failed", "cancelled"),
        last_errors=errors[:5],
    )


@router.post("/{experiment_id}/start", response_model=schemas.ExperimentProgress)
def start_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = _get(db, experiment_id)
    executor.start(db, experiment)
    db.refresh(experiment)
    return _progress(experiment, [])


@router.post("/{experiment_id}/step", response_model=schemas.ExperimentProgress)
def step_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = _get(db, experiment_id)
    errors = executor.step(db, experiment)
    db.refresh(experiment)
    return _progress(experiment, errors)


@router.post("/{experiment_id}/run", response_model=schemas.Experiment)
def run_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Celý experiment v jednej požiadavke. Vhodné len lokálne a pre malé experimenty."""
    experiment = _get(db, experiment_id)
    executor.run_experiment(db, experiment)
    db.refresh(experiment)
    return experiment


@router.post("/{experiment_id}/cancel", response_model=schemas.Experiment)
def cancel_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = _get(db, experiment_id)
    if experiment.status == "running":
        experiment.status = "cancelled"
        experiment.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(experiment)
    return experiment


@router.get("/{experiment_id}/runs", response_model=list[schemas.ExperimentRun])
def list_runs(experiment_id: str, db: Session = Depends(get_db)):
    return db.query(models.ExperimentRun).filter(models.ExperimentRun.experiment_id == experiment_id).all()


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


@router.get("/{experiment_id}/results", response_model=schemas.ExperimentResults)
def get_results(experiment_id: str, db: Session = Depends(get_db)):
    experiment = _get(db, experiment_id)
    runs = db.query(models.ExperimentRun).filter(models.ExperimentRun.experiment_id == experiment_id).all()
    algorithms = {a.id: a for a in db.query(models.Algorithm).filter(
        models.Algorithm.id.in_(experiment.algorithm_ids)).all()}
    variants = executor.variants_of(experiment)

    series: list[schemas.AlgorithmResultSeries] = []
    for v_idx, variant in enumerate(variants):
        for alg_id in experiment.algorithm_ids:
            alg = algorithms.get(alg_id)
            alg_runs = [r for r in runs if r.algorithm_id == alg_id and (r.variant_index or 0) == v_idx]
            points: list[schemas.ResultPoint] = []
            for size in experiment.sizes:
                subset = [r for r in alg_runs if r.input_size == size]
                ok = [r for r in subset if r.status == "ok"]
                times = [r.execution_time_ms for r in ok if r.execution_time_ms is not None]
                mems = [r.memory_kb for r in ok if r.memory_kb is not None]
                op_avg: dict[str, float] = {}
                for r in ok:
                    for key, value in (r.operation_counts or {}).items():
                        op_avg[key] = op_avg.get(key, 0.0) + value / len(ok)
                points.append(schemas.ResultPoint(
                    input_size=size,
                    runs=len(subset),
                    time_ms_min=min(times) if times else None,
                    time_ms_avg=_avg(times),
                    time_ms_max=max(times) if times else None,
                    memory_kb_avg=_avg(mems),
                    operation_counts_avg=op_avg,
                    timeouts=sum(1 for r in subset if r.status == "timeout"),
                    errors=sum(1 for r in subset if r.status == "error"),
                    incorrect=sum(1 for r in ok if r.is_correct is False),
                ))
            if any(r.is_correct is False for r in alg_runs):
                is_correct = False
            elif any(r.is_correct is True for r in alg_runs):
                is_correct = True
            else:
                is_correct = None
            messages = []
            for r in alg_runs:
                if r.is_correct is False and r.check_message and r.check_message not in messages:
                    messages.append(f"n = {r.input_size}: {r.check_message}")
                if len(messages) >= 3:
                    break
            errors = []
            for r in alg_runs:
                if r.status == "error" and r.error_message and r.error_message not in errors:
                    errors.append(r.error_message)
                if len(errors) >= 3:
                    break
            complexity = None
            if alg is not None:
                op_pts = [(p.input_size, p.operation_counts_avg.get("total")) for p in points
                          if p.operation_counts_avg.get("total")]
                t_pts = [(p.input_size, p.time_ms_avg) for p in points if p.time_ms_avg]
                complexity = schemas.ComplexityEstimate(**estimate(op_pts, t_pts, {
                    "avg": alg.complexity_time_avg, "worst": alg.complexity_time_worst,
                    "best": alg.complexity_time_best}))
            series.append(schemas.AlgorithmResultSeries(
                algorithm_id=alg_id,
                algorithm_name=alg.name if alg else alg_id,
                variant_index=v_idx,
                variant_label=variant.get("label", ""),
                is_correct=is_correct,
                check_messages=messages,
                errors=errors,
                points=points,
                complexity=complexity,
            ))
    return schemas.ExperimentResults(
        experiment_id=experiment_id,
        variants=[schemas.ExperimentVariant(**v) for v in variants],
        series=series,
    )


@router.get("/{experiment_id}/export")
def export_experiment(experiment_id: str, format: str = Query("csv", pattern="^(csv|json)$"),
                      db: Session = Depends(get_db)):
    experiment = _get(db, experiment_id)
    runs = db.query(models.ExperimentRun).filter(models.ExperimentRun.experiment_id == experiment_id).all()
    names = {a.id: a.name for a in db.query(models.Algorithm).filter(
        models.Algorithm.id.in_(experiment.algorithm_ids))}
    runs.sort(key=lambda r: (r.variant_index or 0, r.algorithm_id, r.input_size, r.repeat_index))
    if format == "json":
        payload = {
            "experiment": schemas.Experiment.model_validate(experiment).model_dump(mode="json"),
            "results": get_results(experiment_id, db).model_dump(mode="json"),
            "runs": [
                {
                    "algorithm_id": r.algorithm_id,
                    "algorithm_name": names.get(r.algorithm_id, r.algorithm_id),
                    "variant": r.variant_label,
                    "input_size": r.input_size,
                    "repeat_index": r.repeat_index,
                    "execution_time_ms": r.execution_time_ms,
                    "memory_kb": r.memory_kb,
                    "operation_counts": r.operation_counts,
                    "is_correct": r.is_correct,
                    "check_message": r.check_message,
                    "status": r.status,
                    "error_message": r.error_message,
                }
                for r in runs
            ],
        }
        return Response(
            content=json.dumps(payload, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={experiment_id}.json"},
        )

    op_keys = sorted({k for r in runs for k in (r.operation_counts or {})})
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["algorithm", "variant", "input_size", "repeat_index", "execution_time_ms", "memory_kb",
                     *op_keys, "is_correct", "status", "message"])
    for r in runs:
        oc = r.operation_counts or {}
        writer.writerow([
            names.get(r.algorithm_id, r.algorithm_id), r.variant_label, r.input_size, r.repeat_index,
            "" if r.execution_time_ms is None else round(r.execution_time_ms, 4),
            "" if r.memory_kb is None else round(r.memory_kb, 2),
            *[oc.get(k, "") for k in op_keys],
            "" if r.is_correct is None else r.is_correct, r.status,
            r.error_message or r.check_message or "",
        ])
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={experiment_id}.csv"},
    )

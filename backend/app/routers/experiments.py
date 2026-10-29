from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import executor, models, schemas
from ..db import get_db

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.get("", response_model=list[schemas.Experiment])
def list_experiments(db: Session = Depends(get_db)):
    return db.query(models.Experiment).all()


@router.post("", response_model=schemas.Experiment, status_code=201)
def create_experiment(body: schemas.CreateExperimentRequest, db: Session = Depends(get_db)):
    experiment = models.Experiment(id=f"exp_{uuid.uuid4().hex[:8]}", **body.model_dump())
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@router.get("/{experiment_id}", response_model=schemas.Experiment)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = db.get(models.Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(404, f"Experiment '{experiment_id}' neexistuje")
    return experiment


@router.delete("/{experiment_id}", status_code=204)
def delete_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = db.get(models.Experiment, experiment_id)
    if experiment is not None:
        db.query(models.ExperimentRun).filter(
            models.ExperimentRun.experiment_id == experiment_id
        ).delete()
        db.delete(experiment)
        db.commit()


@router.post("/{experiment_id}/run", response_model=schemas.Experiment)
def run_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = db.get(models.Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(404, f"Experiment '{experiment_id}' neexistuje")
    # Synchrónne (slice). Neskôr: BackgroundTask + WebSocket progres.
    executor.run_experiment(db, experiment)
    db.refresh(experiment)
    return experiment


@router.post("/{experiment_id}/cancel", response_model=schemas.Experiment)
def cancel_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = db.get(models.Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(404, f"Experiment '{experiment_id}' neexistuje")
    if experiment.status == "running":
        experiment.status = "cancelled"
        experiment.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(experiment)
    return experiment


@router.get("/{experiment_id}/runs", response_model=list[schemas.ExperimentRun])
def list_runs(experiment_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.ExperimentRun)
        .filter(models.ExperimentRun.experiment_id == experiment_id)
        .all()
    )


@router.get("/{experiment_id}/results", response_model=schemas.ExperimentResults)
def get_results(experiment_id: str, db: Session = Depends(get_db)):
    experiment = db.get(models.Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(404, f"Experiment '{experiment_id}' neexistuje")
    runs = (
        db.query(models.ExperimentRun)
        .filter(models.ExperimentRun.experiment_id == experiment_id)
        .all()
    )

    series: list[schemas.AlgorithmResultSeries] = []
    for alg_id in experiment.algorithm_ids:
        algorithm = db.get(models.Algorithm, alg_id)
        alg_runs = [r for r in runs if r.algorithm_id == alg_id]
        points: list[schemas.ResultPoint] = []
        for size in experiment.sizes:
            subset = [r for r in alg_runs if r.input_size == size and r.status == "ok"]
            times = [r.execution_time_ms for r in subset if r.execution_time_ms is not None]
            mems = [r.memory_kb for r in subset if r.memory_kb is not None]
            op_avg: dict[str, float] = {}
            for r in subset:
                for key, value in (r.operation_counts or {}).items():
                    op_avg[key] = op_avg.get(key, 0.0) + value / max(1, len(subset))
            points.append(
                schemas.ResultPoint(
                    input_size=size,
                    time_ms_min=min(times) if times else 0.0,
                    time_ms_avg=sum(times) / len(times) if times else 0.0,
                    time_ms_max=max(times) if times else 0.0,
                    memory_kb_avg=sum(mems) / len(mems) if mems else 0.0,
                    operation_counts_avg=op_avg,
                )
            )
        if any(r.is_correct is False for r in alg_runs):
            is_correct = False
        elif alg_runs and all(r.is_correct is None for r in alg_runs):
            is_correct = None
        else:
            is_correct = True
        series.append(
            schemas.AlgorithmResultSeries(
                algorithm_id=alg_id,
                algorithm_name=algorithm.name if algorithm else alg_id,
                is_correct=is_correct,
                points=points,
            )
        )
    return schemas.ExperimentResults(experiment_id=experiment_id, series=series)


@router.get("/{experiment_id}/export")
def export_experiment(
    experiment_id: str,
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
):
    runs = (
        db.query(models.ExperimentRun)
        .filter(models.ExperimentRun.experiment_id == experiment_id)
        .all()
    )
    if format == "json":
        payload = [
            {
                "algorithm_id": r.algorithm_id,
                "input_size": r.input_size,
                "repeat_index": r.repeat_index,
                "execution_time_ms": r.execution_time_ms,
                "memory_kb": r.memory_kb,
                "operation_counts": r.operation_counts,
                "is_correct": r.is_correct,
                "status": r.status,
            }
            for r in runs
        ]
        return Response(
            content=json.dumps(payload, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={experiment_id}.json"},
        )

    header = "algorithm_id,input_size,repeat_index,execution_time_ms,memory_kb,compare,swap,is_correct,status"
    lines = [header]
    for r in runs:
        oc = r.operation_counts or {}
        lines.append(
            ",".join(
                str(x)
                for x in [
                    r.algorithm_id,
                    r.input_size,
                    r.repeat_index,
                    r.execution_time_ms if r.execution_time_ms is not None else "",
                    r.memory_kb if r.memory_kb is not None else "",
                    oc.get("compare", ""),
                    oc.get("swap", ""),
                    r.is_correct if r.is_correct is not None else "",
                    r.status,
                ]
            )
        )
    return Response(
        content="\n".join(lines),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={experiment_id}.csv"},
    )

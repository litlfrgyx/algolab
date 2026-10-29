from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..deps import ensure_valid_code, forbid_builtin, require_edit, uses_tracker

router = APIRouter(tags=["algorithms"])


def _get(db: Session, algorithm_id: str) -> models.Algorithm:
    algorithm = db.get(models.Algorithm, algorithm_id)
    if algorithm is None:
        raise HTTPException(404, f"Algoritmus '{algorithm_id}' neexistuje")
    return algorithm


@router.get("/api/algorithms", response_model=list[schemas.Algorithm])
def list_all_algorithms(db: Session = Depends(get_db)):
    return db.query(models.Algorithm).order_by(models.Algorithm.problem_id, models.Algorithm.sort_order).all()


@router.get("/api/problems/{problem_id}/algorithms", response_model=list[schemas.Algorithm])
def list_algorithms(problem_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Algorithm)
        .filter(models.Algorithm.problem_id == problem_id)
        .order_by(models.Algorithm.sort_order, models.Algorithm.name)
        .all()
    )


@router.post("/api/problems/{problem_id}/algorithms", response_model=schemas.Algorithm, status_code=201,
             dependencies=[Depends(require_edit)])
def create_algorithm(problem_id: str, body: schemas.CreateAlgorithmRequest, db: Session = Depends(get_db)):
    if db.get(models.Problem, problem_id) is None:
        raise HTTPException(404, f"Úloha '{problem_id}' neexistuje")
    ensure_valid_code(body.code, "solve")
    data = body.model_dump()
    algorithm = models.Algorithm(
        id=f"alg_{uuid.uuid4().hex[:8]}", problem_id=problem_id, language="python",
        supports_visualization=uses_tracker(body.code), is_builtin=False, **data,
    )
    db.add(algorithm)
    db.commit()
    db.refresh(algorithm)
    return algorithm


@router.get("/api/algorithms/{algorithm_id}", response_model=schemas.Algorithm)
def get_algorithm(algorithm_id: str, db: Session = Depends(get_db)):
    return _get(db, algorithm_id)


@router.put("/api/algorithms/{algorithm_id}", response_model=schemas.Algorithm,
            dependencies=[Depends(require_edit)])
def update_algorithm(algorithm_id: str, body: schemas.UpdateAlgorithmRequest, db: Session = Depends(get_db)):
    algorithm = _get(db, algorithm_id)
    forbid_builtin(algorithm, "algoritmus")
    ensure_valid_code(body.code, "solve")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(algorithm, key, value)
    algorithm.supports_visualization = uses_tracker(algorithm.code)
    db.commit()
    db.refresh(algorithm)
    return algorithm


@router.post("/api/algorithms/{algorithm_id}/duplicate", response_model=schemas.Algorithm, status_code=201,
             dependencies=[Depends(require_edit)])
def duplicate_algorithm(algorithm_id: str, db: Session = Depends(get_db)):
    src = _get(db, algorithm_id)
    copy = models.Algorithm(
        id=f"alg_{uuid.uuid4().hex[:8]}", problem_id=src.problem_id, name=f"{src.name} (kópia)",
        description=src.description, code=src.code, language="python", is_reference=False,
        supports_visualization=src.supports_visualization, paradigm=src.paradigm,
        complexity_time_best=src.complexity_time_best, complexity_time_avg=src.complexity_time_avg,
        complexity_time_worst=src.complexity_time_worst, complexity_space=src.complexity_space,
        complexity_note=src.complexity_note, complexity_param=src.complexity_param,
        properties=[p for p in (src.properties or []) if p != "intentionally_incorrect"],
        is_builtin=False, sort_order=(src.sort_order or 1000) + 1,
    )
    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy


@router.delete("/api/algorithms/{algorithm_id}", status_code=204, dependencies=[Depends(require_edit)])
def delete_algorithm(algorithm_id: str, db: Session = Depends(get_db)):
    algorithm = db.get(models.Algorithm, algorithm_id)
    if algorithm is None:
        return
    forbid_builtin(algorithm, "algoritmus")
    db.delete(algorithm)
    db.commit()

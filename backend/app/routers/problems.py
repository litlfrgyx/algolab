from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..deps import ensure_valid_code, forbid_builtin, require_edit

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("", response_model=list[schemas.ProblemSummary])
def list_problems(db: Session = Depends(get_db)):
    problems = db.query(models.Problem).order_by(models.Problem.sort_order, models.Problem.name).all()
    algs = db.query(models.Algorithm.problem_id, models.Algorithm.supports_visualization).all()
    gens = db.query(models.InputGenerator.problem_id).all()
    out = []
    for p in problems:
        item = schemas.ProblemSummary.model_validate(p)
        item.algorithm_count = sum(1 for pid, _ in algs if pid == p.id)
        item.visualizable_count = sum(1 for pid, viz in algs if pid == p.id and viz)
        item.generator_count = sum(1 for (pid,) in gens if pid == p.id)
        out.append(item)
    return out


@router.post("", response_model=schemas.Problem, status_code=201, dependencies=[Depends(require_edit)])
def create_problem(body: schemas.CreateProblemRequest, db: Session = Depends(get_db)):
    if body.checker_code:
        ensure_valid_code(body.checker_code, "check")
    problem = models.Problem(id=f"prob_{uuid.uuid4().hex[:8]}", is_builtin=False, **body.model_dump())
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@router.get("/{problem_id}", response_model=schemas.Problem)
def get_problem(problem_id: str, db: Session = Depends(get_db)):
    problem = db.get(models.Problem, problem_id)
    if problem is None:
        raise HTTPException(404, f"Úloha '{problem_id}' neexistuje")
    return problem


@router.put("/{problem_id}", response_model=schemas.Problem, dependencies=[Depends(require_edit)])
def update_problem(problem_id: str, body: schemas.UpdateProblemRequest, db: Session = Depends(get_db)):
    problem = db.get(models.Problem, problem_id)
    if problem is None:
        raise HTTPException(404, f"Úloha '{problem_id}' neexistuje")
    forbid_builtin(problem, "úloha")
    if body.checker_code:
        ensure_valid_code(body.checker_code, "check")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(problem, key, value)
    db.commit()
    db.refresh(problem)
    return problem


@router.delete("/{problem_id}", status_code=204, dependencies=[Depends(require_edit)])
def delete_problem(problem_id: str, db: Session = Depends(get_db)):
    problem = db.get(models.Problem, problem_id)
    if problem is None:
        return
    forbid_builtin(problem, "úloha")
    if body.checker_code:
        ensure_valid_code(body.checker_code, "check")
    exp_ids = [e.id for e in db.query(models.Experiment).filter(models.Experiment.problem_id == problem_id)]
    if exp_ids:
        db.query(models.ExperimentRun).filter(models.ExperimentRun.experiment_id.in_(exp_ids)).delete()
    db.query(models.Experiment).filter(models.Experiment.problem_id == problem_id).delete()
    db.query(models.Algorithm).filter(models.Algorithm.problem_id == problem_id).delete()
    db.query(models.InputGenerator).filter(models.InputGenerator.problem_id == problem_id).delete()
    db.delete(problem)
    db.commit()

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("", response_model=list[schemas.Problem])
def list_problems(db: Session = Depends(get_db)):
    return db.query(models.Problem).all()


@router.post("", response_model=schemas.Problem, status_code=201)
def create_problem(body: schemas.CreateProblemRequest, db: Session = Depends(get_db)):
    problem = models.Problem(id=f"prob_{uuid.uuid4().hex[:8]}", **body.model_dump())
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@router.get("/{problem_id}", response_model=schemas.Problem)
def get_problem(problem_id: str, db: Session = Depends(get_db)):
    problem = db.get(models.Problem, problem_id)
    if problem is None:
        raise HTTPException(404, f"Problem '{problem_id}' neexistuje")
    return problem


@router.put("/{problem_id}", response_model=schemas.Problem)
def update_problem(problem_id: str, body: schemas.UpdateProblemRequest, db: Session = Depends(get_db)):
    problem = db.get(models.Problem, problem_id)
    if problem is None:
        raise HTTPException(404, f"Problem '{problem_id}' neexistuje")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(problem, key, value)
    db.commit()
    db.refresh(problem)
    return problem


@router.delete("/{problem_id}", status_code=204)
def delete_problem(problem_id: str, db: Session = Depends(get_db)):
    problem = db.get(models.Problem, problem_id)
    if problem is not None:
        db.delete(problem)
        db.commit()

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db

router = APIRouter(tags=["algorithms"])


@router.get("/api/problems/{problem_id}/algorithms", response_model=list[schemas.Algorithm])
def list_algorithms(problem_id: str, db: Session = Depends(get_db)):
    return db.query(models.Algorithm).filter(models.Algorithm.problem_id == problem_id).all()


@router.post("/api/problems/{problem_id}/algorithms", response_model=schemas.Algorithm, status_code=201)
def create_algorithm(problem_id: str, body: schemas.CreateAlgorithmRequest, db: Session = Depends(get_db)):
    algorithm = models.Algorithm(
        id=f"alg_{uuid.uuid4().hex[:8]}",
        problem_id=problem_id,
        name=body.name,
        code=body.code,
        is_reference=body.is_reference,
        supports_visualization="tracker" in body.code,
    )
    db.add(algorithm)
    db.commit()
    db.refresh(algorithm)
    return algorithm


@router.get("/api/algorithms/{algorithm_id}", response_model=schemas.Algorithm)
def get_algorithm(algorithm_id: str, db: Session = Depends(get_db)):
    algorithm = db.get(models.Algorithm, algorithm_id)
    if algorithm is None:
        raise HTTPException(404, f"Algorithm '{algorithm_id}' neexistuje")
    return algorithm


@router.put("/api/algorithms/{algorithm_id}", response_model=schemas.Algorithm)
def update_algorithm(algorithm_id: str, body: schemas.UpdateAlgorithmRequest, db: Session = Depends(get_db)):
    algorithm = db.get(models.Algorithm, algorithm_id)
    if algorithm is None:
        raise HTTPException(404, f"Algorithm '{algorithm_id}' neexistuje")
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(algorithm, key, value)
    if "code" in data:
        algorithm.supports_visualization = "tracker" in data["code"]
    db.commit()
    db.refresh(algorithm)
    return algorithm


@router.delete("/api/algorithms/{algorithm_id}", status_code=204)
def delete_algorithm(algorithm_id: str, db: Session = Depends(get_db)):
    algorithm = db.get(models.Algorithm, algorithm_id)
    if algorithm is not None:
        db.delete(algorithm)
        db.commit()

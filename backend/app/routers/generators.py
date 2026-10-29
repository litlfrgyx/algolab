from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..sandbox.runner import run_generator

router = APIRouter(tags=["generators"])


@router.get("/api/problems/{problem_id}/generators", response_model=list[schemas.InputGenerator])
def list_generators(problem_id: str, db: Session = Depends(get_db)):
    return db.query(models.InputGenerator).filter(models.InputGenerator.problem_id == problem_id).all()


@router.post("/api/problems/{problem_id}/generators", response_model=schemas.InputGenerator, status_code=201)
def create_generator(problem_id: str, body: schemas.CreateGeneratorRequest, db: Session = Depends(get_db)):
    generator = models.InputGenerator(
        id=f"gen_{uuid.uuid4().hex[:8]}",
        problem_id=problem_id,
        name=body.name,
        code=body.code,
        default_sizes=body.default_sizes,
        param_spec=[p.model_dump() for p in body.param_spec],
    )
    db.add(generator)
    db.commit()
    db.refresh(generator)
    return generator


@router.get("/api/generators/{generator_id}", response_model=schemas.InputGenerator)
def get_generator(generator_id: str, db: Session = Depends(get_db)):
    generator = db.get(models.InputGenerator, generator_id)
    if generator is None:
        raise HTTPException(404, f"Generator '{generator_id}' neexistuje")
    return generator


@router.put("/api/generators/{generator_id}", response_model=schemas.InputGenerator)
def update_generator(generator_id: str, body: schemas.UpdateGeneratorRequest, db: Session = Depends(get_db)):
    generator = db.get(models.InputGenerator, generator_id)
    if generator is None:
        raise HTTPException(404, f"Generator '{generator_id}' neexistuje")
    data = body.model_dump(exclude_unset=True)
    if "param_spec" in data and data["param_spec"] is not None:
        data["param_spec"] = [p if isinstance(p, dict) else p.model_dump() for p in data["param_spec"]]
    for key, value in data.items():
        setattr(generator, key, value)
    db.commit()
    db.refresh(generator)
    return generator


@router.delete("/api/generators/{generator_id}", status_code=204)
def delete_generator(generator_id: str, db: Session = Depends(get_db)):
    generator = db.get(models.InputGenerator, generator_id)
    if generator is not None:
        db.delete(generator)
        db.commit()


@router.post("/api/generators/{generator_id}/preview", response_model=schemas.GeneratorPreviewResponse)
def preview_generator(generator_id: str, body: schemas.GeneratorPreviewRequest, db: Session = Depends(get_db)):
    generator = db.get(models.InputGenerator, generator_id)
    if generator is None:
        raise HTTPException(404, f"Generator '{generator_id}' neexistuje")
    params = dict(body.params)
    if body.seed is not None:
        params.setdefault("seed", body.seed)
    result = run_generator(generator.code, body.n, params)
    if result["status"] != "ok":
        return schemas.GeneratorPreviewResponse(
            input=[], preview="", type="error", length=0,
            elapsed_ms=0.0, error=result.get("error"),
        )
    data = result["result"]
    head = data[:40] if isinstance(data, list) else data
    preview = " ".join(str(x) for x in head) + (" …" if isinstance(data, list) and len(data) > 40 else "")
    return schemas.GeneratorPreviewResponse(
        input=data,
        preview=preview,
        type=f"list[int]" if isinstance(data, list) else type(data).__name__,
        length=len(data) if hasattr(data, "__len__") else 0,
        elapsed_ms=round(result["elapsed_ms"], 2),
        error=None,
    )

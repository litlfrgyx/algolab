from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..deps import ensure_valid_code, forbid_builtin, require_edit
from ..sandbox.runner import run_generator

router = APIRouter(tags=["generators"])


def _get(db: Session, generator_id: str) -> models.InputGenerator:
    generator = db.get(models.InputGenerator, generator_id)
    if generator is None:
        raise HTTPException(404, f"Generátor '{generator_id}' neexistuje")
    return generator


@router.get("/api/generators", response_model=list[schemas.InputGenerator])
def list_all_generators(db: Session = Depends(get_db)):
    return db.query(models.InputGenerator).all()


@router.get("/api/problems/{problem_id}/generators", response_model=list[schemas.InputGenerator])
def list_generators(problem_id: str, db: Session = Depends(get_db)):
    return db.query(models.InputGenerator).filter(models.InputGenerator.problem_id == problem_id).all()


@router.post("/api/problems/{problem_id}/generators", response_model=schemas.InputGenerator, status_code=201,
             dependencies=[Depends(require_edit)])
def create_generator(problem_id: str, body: schemas.CreateGeneratorRequest, db: Session = Depends(get_db)):
    if db.get(models.Problem, problem_id) is None:
        raise HTTPException(404, f"Úloha '{problem_id}' neexistuje")
    ensure_valid_code(body.code, "generate")
    data = body.model_dump()
    data["param_spec"] = [p.model_dump() for p in body.param_spec]
    generator = models.InputGenerator(id=f"gen_{uuid.uuid4().hex[:8]}", problem_id=problem_id,
                                      is_builtin=False, **data)
    db.add(generator)
    db.commit()
    db.refresh(generator)
    return generator


@router.get("/api/generators/{generator_id}", response_model=schemas.InputGenerator)
def get_generator(generator_id: str, db: Session = Depends(get_db)):
    return _get(db, generator_id)


@router.put("/api/generators/{generator_id}", response_model=schemas.InputGenerator,
            dependencies=[Depends(require_edit)])
def update_generator(generator_id: str, body: schemas.UpdateGeneratorRequest, db: Session = Depends(get_db)):
    generator = _get(db, generator_id)
    forbid_builtin(generator, "generátor")
    ensure_valid_code(body.code, "generate")
    data = body.model_dump(exclude_unset=True)
    if "param_spec" in data and body.param_spec is not None:
        data["param_spec"] = [p.model_dump() for p in body.param_spec]
    for key, value in data.items():
        setattr(generator, key, value)
    db.commit()
    db.refresh(generator)
    return generator


@router.post("/api/generators/{generator_id}/duplicate", response_model=schemas.InputGenerator,
             status_code=201, dependencies=[Depends(require_edit)])
def duplicate_generator(generator_id: str, db: Session = Depends(get_db)):
    src = _get(db, generator_id)
    copy = models.InputGenerator(
        id=f"gen_{uuid.uuid4().hex[:8]}", problem_id=src.problem_id, name=f"{src.name} (kópia)",
        description=src.description, code=src.code, default_sizes=list(src.default_sizes or []),
        viz_size=src.viz_size, param_spec=list(src.param_spec or []), is_builtin=False,
    )
    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy


@router.delete("/api/generators/{generator_id}", status_code=204, dependencies=[Depends(require_edit)])
def delete_generator(generator_id: str, db: Session = Depends(get_db)):
    generator = db.get(models.InputGenerator, generator_id)
    if generator is None:
        return
    forbid_builtin(generator, "generátor")
    db.delete(generator)
    db.commit()


def _describe(data) -> tuple[str, int]:
    if isinstance(data, list):
        kind = "zoznam"
        if data and all(isinstance(x, (int, float)) for x in data[:20]):
            kind = "pole čísel"
        return kind, len(data)
    if isinstance(data, dict):
        return "objekt (" + ", ".join(list(data.keys())[:6]) + ")", len(data)
    if isinstance(data, str):
        return "reťazec", len(data)
    return type(data).__name__, 1


@router.post("/api/generators/{generator_id}/preview", response_model=schemas.GeneratorPreviewResponse)
def preview_generator(generator_id: str, body: schemas.GeneratorPreviewRequest, db: Session = Depends(get_db)):
    generator = _get(db, generator_id)
    return _preview(generator.code, body)


@router.post("/api/generators/preview-code", response_model=schemas.GeneratorPreviewResponse,
             dependencies=[Depends(require_edit)])
def preview_code(body: schemas.GeneratorCodePreviewRequest):
    """Náhľad neuloženého kódu generátora (spúšťa vlastný kód, preto vyžaduje heslo)."""
    ensure_valid_code(body.code, "generate")
    return _preview(body.code, body)


def _preview(code: str, body: schemas.GeneratorPreviewRequest) -> schemas.GeneratorPreviewResponse:
    params = dict(body.params)
    if body.seed is not None:
        params["seed"] = body.seed
    n = max(0, min(body.n, 100000))
    result = run_generator(code, n, params)
    if result.get("status") != "ok":
        return schemas.GeneratorPreviewResponse(input=None, preview="", type="error", length=0,
                                                elapsed_ms=0.0, error=result.get("error"))
    data = result["result"]
    text = json.dumps(data, ensure_ascii=False)
    preview = text if len(text) <= 600 else text[:600] + " …"
    kind, length = _describe(data)
    return schemas.GeneratorPreviewResponse(
        input=data if len(text) <= 200_000 else None, preview=preview, type=kind, length=length,
        elapsed_ms=round(result.get("elapsed_ms", 0.0), 2), error=None,
    )

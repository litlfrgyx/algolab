from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..sandbox.runner import _static_check, run_algorithm

router = APIRouter(tags=["visualize"])


@router.post("/api/visualize", response_model=schemas.VisualizationTrace)
def visualize(body: schemas.VisualizeRequest, db: Session = Depends(get_db)):
    code = body.code
    name = "Ad-hoc"
    if body.algorithm_id:
        algorithm = db.get(models.Algorithm, body.algorithm_id)
        if algorithm is None:
            raise HTTPException(404, f"Algorithm '{body.algorithm_id}' neexistuje")
        code = algorithm.code
        name = algorithm.name
    if not code:
        raise HTTPException(400, "Treba zadať algorithm_id alebo code")

    result = run_algorithm(code, body.input, mode="visualize", max_steps=body.max_steps)
    if result["status"] != "ok":
        raise HTTPException(400, result.get("error", "Vizualizácia zlyhala"))

    return schemas.VisualizationTrace(
        renderer="array",
        algorithm_id=body.algorithm_id,
        algorithm_name=name,
        input=body.input,
        steps=result["steps"],
        operation_counts=result["operation_counts"],
        truncated=result["truncated"],
        max_steps=body.max_steps,
    )


@router.post("/api/code/validate", response_model=schemas.ValidateCodeResponse)
def validate_code(body: schemas.ValidateCodeRequest):
    errors: list[schemas.CodeError] = []
    try:
        _static_check(body.code)
    except SyntaxError as exc:
        errors.append(schemas.CodeError(line=exc.lineno, message=str(exc.msg), severity="error"))
    except ValueError as exc:
        errors.append(schemas.CodeError(message=str(exc), severity="error"))

    entry = "solve" if body.kind == "algorithm" else "generate"
    if f"def {entry}" not in body.code:
        errors.append(
            schemas.CodeError(
                message=(
                    "Chýba funkcia def solve(data) alebo def solve(data, tracker)."
                    if body.kind == "algorithm"
                    else "Chýba funkcia def generate(n, **params)."
                ),
                severity="error",
            )
        )
    return schemas.ValidateCodeResponse(valid=len(errors) == 0, errors=errors)

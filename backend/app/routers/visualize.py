from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..db import get_db
from ..deps import require_edit, uses_tracker
from ..sandbox.runner import UnsafeCode, check_code, run_algorithm

router = APIRouter(tags=["visualize"])

# Strop veľkosti vstupu pre vizualizáciu podľa vykresľovača.
VIZ_LIMITS = {"array": 60, "grid": 15, "graph": 25, "tree": 31, "string": 80, "none": 60}


@router.get("/api/info", response_model=schemas.CatalogInfo)
def info(db: Session = Depends(get_db)):
    return schemas.CatalogInfo(
        edit_protected=bool(settings.edit_password),
        remote_runner=bool(settings.runner_url),
        max_algorithms=settings.max_algorithms_per_experiment,
        max_timeout_ms=settings.max_timeout_ms,
        problems=db.query(models.Problem).count(),
        algorithms=db.query(models.Algorithm).count(),
        viz_limits=VIZ_LIMITS,
    )


@router.post("/api/visualize", response_model=schemas.VisualizationTrace)
def visualize(body: schemas.VisualizeRequest, db: Session = Depends(get_db),
              x_edit_password: str | None = Header(default=None)):
    code = body.code
    name = "Vlastný kód"
    problem = None
    if body.algorithm_id:
        algorithm = db.get(models.Algorithm, body.algorithm_id)
        if algorithm is None:
            raise HTTPException(404, f"Algoritmus '{body.algorithm_id}' neexistuje")
        code = algorithm.code
        name = algorithm.name
        problem = db.get(models.Problem, algorithm.problem_id)
    else:
        require_edit(x_edit_password)
        if body.problem_id:
            problem = db.get(models.Problem, body.problem_id)
    if not code:
        raise HTTPException(400, "Treba zadať algorithm_id alebo code")

    expected = None
    if problem is not None and problem.reference_algorithm_id:
        ref = db.get(models.Algorithm, problem.reference_algorithm_id)
        if ref is not None:
            r = run_algorithm(ref.code, body.input, return_result=True)
            if r.get("status") == "ok":
                expected = r.get("result")

    max_steps = max(1, min(body.max_steps, 5000))
    result = run_algorithm(code, body.input, max_steps=max_steps, return_result=True,
                           check_code_src=problem.checker_code if problem else None, expected=expected)
    if result.get("status") != "ok":
        raise HTTPException(400, result.get("error", "Vizualizácia zlyhala"))

    steps = result.get("steps") or []
    renderer = (problem.renderer if problem else None) or result.get("renderer") or "array"
    if steps and steps[0].get("kind") not in (None, "none"):
        renderer = steps[0]["kind"]
    return schemas.VisualizationTrace(
        renderer=renderer if renderer in VIZ_LIMITS else "array",
        algorithm_id=body.algorithm_id,
        algorithm_name=name,
        input=body.input,
        steps=steps,
        structure=result.get("structure"),
        operation_counts=result.get("operation_counts") or {},
        result=result.get("result"),
        is_correct=result.get("is_correct"),
        check_message=result.get("check_message"),
        stdout=result.get("stdout"),
        truncated=bool(result.get("truncated")),
        max_steps=max_steps,
        uses_tracker=bool(result.get("uses_tracker", True)),
    )


@router.post("/api/code/validate", response_model=schemas.ValidateCodeResponse)
def validate_code(body: schemas.ValidateCodeRequest):
    errors: list[schemas.CodeError] = []
    try:
        check_code(body.code)
    except SyntaxError as exc:
        errors.append(schemas.CodeError(line=exc.lineno, message=f"Syntaktická chyba: {exc.msg}",
                                        severity="error"))
    except UnsafeCode as exc:
        errors.append(schemas.CodeError(message=str(exc), severity="error"))

    entry = {"algorithm": "solve", "generator": "generate", "checker": "check"}[body.kind]
    if f"def {entry}" not in body.code:
        hint = {
            "algorithm": "Chýba funkcia def solve(data) alebo def solve(data, tracker).",
            "generator": "Chýba funkcia def generate(n, **params).",
            "checker": "Chýba funkcia def check(input, output, expected=None).",
        }[body.kind]
        errors.append(schemas.CodeError(message=hint, severity="error"))
    tracker = uses_tracker(body.code) if body.kind == "algorithm" else False
    if body.kind == "algorithm" and not errors and not tracker:
        errors.append(schemas.CodeError(
            message="Funkcia solve nemá parameter tracker, algoritmus sa dá merať, ale nie vizualizovať.",
            severity="warning"))
    return schemas.ValidateCodeResponse(valid=not any(e.severity == "error" for e in errors),
                                        errors=errors, uses_tracker=tracker)

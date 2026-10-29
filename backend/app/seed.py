"""Inicializácia databázy a doplnenie vstavaného katalógu úloh.

Pri štarte:
  1. ak sa zmenila verzia schémy, vývojová databáza sa zahodí a vytvorí znova,
  2. ak sa zmenil vstavaný katalóg, vstavané úlohy, algoritmy, generátory
     a ukážkové experimenty sa doplnia alebo aktualizujú podľa ID.
Záznamy používateľa (is_builtin = False) sa nemenia.
"""

from __future__ import annotations

import hashlib
import json
import logging

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from . import executor, models
from .catalog import CATALOG
from .db import Base, SessionLocal, engine, ensure_schema
from .deps import uses_tracker

log = logging.getLogger("algolab.seed")


def _catalog_version() -> str:
    raw = json.dumps(CATALOG, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _meta(db: Session, key: str) -> str | None:
    row = db.get(models.Meta, key)
    return row.value if row else None


def _set_meta(db: Session, key: str, value: str) -> None:
    row = db.get(models.Meta, key)
    if row is None:
        db.add(models.Meta(key=key, value=value))
    else:
        row.value = value


def init_database() -> None:
    ensure_schema()
    has_meta = inspect(engine).has_table("meta")
    if has_meta:
        with SessionLocal() as db:
            version = _meta(db, "schema_version")
    else:
        version = None
    if version != models.SCHEMA_VERSION:
        log.warning("Schéma databázy sa zmenila (%s → %s), databáza sa vytvorí znova",
                    version, models.SCHEMA_VERSION)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            _set_meta(db, "schema_version", models.SCHEMA_VERSION)
            db.commit()
    else:
        Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_builtins(db)


def _upsert(db: Session, model, values: dict) -> tuple[object, bool]:
    obj = db.get(model, values["id"])
    if obj is None:
        obj = model(**values)
        db.add(obj)
        return obj, True
    changed = False
    for key, value in values.items():
        if getattr(obj, key) != value:
            setattr(obj, key, value)
            changed = True
    return obj, changed


def seed_builtins(db: Session, force: bool = False) -> None:
    version = _catalog_version()
    if not force and _meta(db, "catalog_version") == version:
        return
    keep = {"problems": set(), "algorithms": set(), "generators": set(), "experiments": set()}
    for order, p in enumerate(CATALOG):
        keep["problems"].add(p["id"])
        _upsert(db, models.Problem, {
            "id": p["id"], "name": p["name"], "summary": p.get("summary", ""),
            "description": p.get("description", ""), "category": p["category"],
            "input_type": p.get("input_type", "array"), "renderer": p.get("renderer", "array"),
            "input_description": p.get("input_description", ""),
            "output_description": p.get("output_description", ""),
            "reference_algorithm_id": p.get("reference"), "checker_code": p.get("checker"),
            "tags": p.get("tags", []), "is_builtin": True, "sort_order": order,
        })
        for a_order, a in enumerate(p["algorithms"]):
            keep["algorithms"].add(a["id"])
            _upsert(db, models.Algorithm, {
                "id": a["id"], "problem_id": p["id"], "name": a["name"],
                "description": a.get("description", ""), "code": a["code"].strip() + "\n",
                "language": "python", "is_reference": a["id"] == p.get("reference"),
                "supports_visualization": bool(a.get("viz", True)) and uses_tracker(a["code"]),
                "paradigm": a.get("paradigm", "iterative"),
                "complexity_time_best": a.get("best"), "complexity_time_avg": a.get("avg"),
                "complexity_time_worst": a.get("worst"), "complexity_space": a.get("space"),
                "complexity_note": a.get("note", ""), "complexity_param": a.get("param", ""),
                "properties": a.get("properties", []), "is_builtin": True, "sort_order": a_order,
            })
        for g in p["generators"]:
            keep["generators"].add(g["id"])
            _upsert(db, models.InputGenerator, {
                "id": g["id"], "problem_id": p["id"], "name": g["name"],
                "description": g.get("description", ""), "code": g["code"].strip() + "\n",
                "default_sizes": g["sizes"], "viz_size": g.get("viz_size", 10),
                "param_spec": g.get("params", []), "is_builtin": True,
            })
        for e in p.get("experiments", []):
            keep["experiments"].add(e["id"])
            values = {
                "id": e["id"], "name": e["name"], "problem_id": p["id"],
                "algorithm_ids": e["algorithms"], "generator_id": e["generator"],
                "sizes": e["sizes"], "repeats": e.get("repeats", 3),
                "timeout_ms": e.get("timeout_ms", 5000), "seed": e.get("seed", 42),
                "generator_params": e.get("params", {}), "variants": e.get("variants", []),
                "is_builtin": True,
            }
            obj, changed = _upsert(db, models.Experiment, values)
            if changed:
                obj.status = "pending"
                obj.done_cases = 0
                obj.total_cases = executor.total_cases(obj)
                db.query(models.ExperimentRun).filter(models.ExperimentRun.experiment_id == e["id"]).delete()

    # vstavané záznamy, ktoré z katalógu zmizli
    for model, key in ((models.Problem, "problems"), (models.Algorithm, "algorithms"),
                       (models.InputGenerator, "generators"), (models.Experiment, "experiments")):
        for obj in db.query(model).filter(model.is_builtin.is_(True)).all():
            if obj.id not in keep[key]:
                db.delete(obj)
    _set_meta(db, "catalog_version", version)
    db.commit()

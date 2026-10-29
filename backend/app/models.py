"""SQLAlchemy ORM modely — zrkadlia entity z schemas.py / domain.ts.

JSON stĺpce (zoznamy, slovníky) sú v SQLite uložené ako JSON text.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String

from .db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Problem(Base):
    __tablename__ = "problems"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    category = Column(String, nullable=False)
    input_description = Column(String, default="")
    output_description = Column(String, default="")
    reference_algorithm_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class Algorithm(Base):
    __tablename__ = "algorithms"
    id = Column(String, primary_key=True)
    problem_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    language = Column(String, default="python")
    is_reference = Column(Boolean, default=False)
    supports_visualization = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class InputGenerator(Base):
    __tablename__ = "generators"
    id = Column(String, primary_key=True)
    problem_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    default_sizes = Column(JSON, default=list)
    param_spec = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    problem_id = Column(String, nullable=False, index=True)
    algorithm_ids = Column(JSON, default=list)
    generator_id = Column(String, nullable=False)
    sizes = Column(JSON, default=list)
    repeats = Column(Integer, default=3)
    timeout_ms = Column(Integer, default=5000)
    seed = Column(Integer, nullable=True)
    generator_params = Column(JSON, default=dict)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), default=_now)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"
    id = Column(String, primary_key=True)
    experiment_id = Column(String, nullable=False, index=True)
    algorithm_id = Column(String, nullable=False)
    input_size = Column(Integer, nullable=False)
    repeat_index = Column(Integer, nullable=False)
    execution_time_ms = Column(Float, nullable=True)
    memory_kb = Column(Float, nullable=True)
    operation_counts = Column(JSON, default=dict)
    is_correct = Column(Boolean, nullable=True)
    status = Column(String, default="ok")
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)

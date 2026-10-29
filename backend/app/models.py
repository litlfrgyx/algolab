"""SQLAlchemy ORM modely. Zrkadlia entity zo schemas.py a frontend/src/types/domain.ts.

Zoznamy a slovníky sa ukladajú ako JSON.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text

from .db import Base

SCHEMA_VERSION = "3"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Meta(Base):
    """Kľúč a hodnota: verzia schémy a verzia vstavaného katalógu."""

    __tablename__ = "meta"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)


class Problem(Base):
    __tablename__ = "problems"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    summary = Column(String, default="")
    description = Column(Text, default="")
    category = Column(String, nullable=False)
    input_type = Column(String, default="array")
    renderer = Column(String, default="array")
    input_description = Column(Text, default="")
    output_description = Column(Text, default="")
    reference_algorithm_id = Column(String, nullable=True)
    checker_code = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    is_builtin = Column(Boolean, default=False)
    sort_order = Column(Integer, default=1000)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class Algorithm(Base):
    __tablename__ = "algorithms"
    id = Column(String, primary_key=True)
    problem_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    code = Column(Text, nullable=False)
    language = Column(String, default="python")
    is_reference = Column(Boolean, default=False)
    supports_visualization = Column(Boolean, default=False)
    paradigm = Column(String, default="iterative")
    complexity_time_best = Column(String, nullable=True)
    complexity_time_avg = Column(String, nullable=True)
    complexity_time_worst = Column(String, nullable=True)
    complexity_space = Column(String, nullable=True)
    complexity_note = Column(String, default="")
    complexity_param = Column(String, default="")
    properties = Column(JSON, default=list)
    is_builtin = Column(Boolean, default=False)
    sort_order = Column(Integer, default=1000)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class InputGenerator(Base):
    __tablename__ = "generators"
    id = Column(String, primary_key=True)
    problem_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    code = Column(Text, nullable=False)
    default_sizes = Column(JSON, default=list)
    viz_size = Column(Integer, default=10)
    param_spec = Column(JSON, default=list)
    is_builtin = Column(Boolean, default=False)
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
    variants = Column(JSON, default=list)
    status = Column(String, default="pending")
    total_cases = Column(Integer, default=0)
    done_cases = Column(Integer, default=0)
    is_builtin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"
    id = Column(String, primary_key=True)
    experiment_id = Column(String, nullable=False, index=True)
    algorithm_id = Column(String, nullable=False)
    variant_index = Column(Integer, default=0)
    variant_label = Column(String, default="")
    input_size = Column(Integer, nullable=False)
    repeat_index = Column(Integer, nullable=False)
    execution_time_ms = Column(Float, nullable=True)
    memory_kb = Column(Float, nullable=True)
    operation_counts = Column(JSON, default=dict)
    is_correct = Column(Boolean, nullable=True)
    check_message = Column(Text, nullable=True)
    status = Column(String, default="ok")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)

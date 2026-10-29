"""Pydantic schémy — drôtový kontrakt API.

Toto je 1:1 zrkadlo TypeScript typov z frontend/src/types/. Polia sú
snake_case, takže medzi FastAPI a klientom nie je potrebná transformačná
vrstva. Tento súbor definuje IBA tvar dát (DTO); SQLAlchemy modely (tabuľky)
a logika executora prídu neskôr.

Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

# Spoločná konfigurácia entít: umožní FastAPI serializovať SQLAlchemy ORM objekty
# (response_model=... s návratom ORM inštancie) cez model_validate(from_attributes).
_ORM = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
#  Enumerácie (ako Literal — jednoduché a serializovateľné)
# ---------------------------------------------------------------------------
ProblemCategory = Literal[
    "sorting",
    "searching",
    "divide_and_conquer",
    "string",
    "dynamic_programming",
    "matrix",
    "backtracking",
    "greedy",
    "graph",
    "recursive",
]
RendererKind = Literal["array", "grid", "string"]
HighlightRole = Literal[
    "compare", "swap", "pivot", "active", "match", "sorted", "range", "visited"
]
ExperimentStatus = Literal["pending", "running", "done", "failed", "cancelled"]
RunStatus = Literal["ok", "error", "timeout"]

Scalar = Union[str, int, float, bool]


# ===========================================================================
#  Doménový model
# ===========================================================================
class Problem(BaseModel):
    model_config = _ORM
    id: str
    name: str
    description: str
    category: ProblemCategory
    input_description: str
    output_description: str
    reference_algorithm_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class Algorithm(BaseModel):
    model_config = _ORM
    id: str
    problem_id: str
    name: str
    code: str
    language: Literal["python"] = "python"
    is_reference: bool = False
    supports_visualization: bool = False
    created_at: datetime
    updated_at: datetime


class GeneratorParamSpec(BaseModel):
    name: str
    label: str
    type: Literal["enum", "number", "boolean"]
    options: Optional[list[str]] = None
    default: Scalar


class InputGenerator(BaseModel):
    model_config = _ORM
    id: str
    problem_id: str
    name: str
    code: str
    default_sizes: list[int]
    param_spec: list[GeneratorParamSpec] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class Experiment(BaseModel):
    model_config = _ORM
    id: str
    name: str
    problem_id: str
    algorithm_ids: list[str]
    generator_id: str
    sizes: list[int]
    repeats: int = 3
    timeout_ms: int = 5000
    seed: Optional[int] = None
    generator_params: dict[str, Scalar] = Field(default_factory=dict)
    status: ExperimentStatus = "pending"
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class ExperimentRun(BaseModel):
    model_config = _ORM
    id: str
    experiment_id: str
    algorithm_id: str
    input_size: int
    repeat_index: int
    execution_time_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    # Hardvérovo nezávislá metrika (kapitola 2.1.4): { "compare": 28, "swap": 16 }
    operation_counts: dict[str, int] = Field(default_factory=dict)
    is_correct: Optional[bool] = None
    status: RunStatus
    error_message: Optional[str] = None
    created_at: datetime


# ===========================================================================
#  Kroky vizualizácie (Step) — diskriminovaná únia podľa `kind`
# ===========================================================================
class ArrayHighlight(BaseModel):
    index: int
    role: HighlightRole


class GridHighlight(BaseModel):
    row: int
    col: int
    role: HighlightRole


class StringHighlight(BaseModel):
    index: int
    role: HighlightRole


class _StepBase(BaseModel):
    index: int
    type: str
    label: str
    code_line: Optional[int] = None


class ArrayStep(_StepBase):
    kind: Literal["array"] = "array"
    array: list[float]
    highlights: list[ArrayHighlight] = Field(default_factory=list)
    pointers: Optional[dict[str, int]] = None


class GridStep(_StepBase):
    kind: Literal["grid"] = "grid"
    grid: list[list[Optional[Union[float, str]]]]
    highlights: list[GridHighlight] = Field(default_factory=list)
    row_labels: Optional[list[str]] = None
    col_labels: Optional[list[str]] = None


class StringStep(_StepBase):
    kind: Literal["string"] = "string"
    value: str
    highlights: list[StringHighlight] = Field(default_factory=list)
    pattern: Optional[str] = None
    pattern_highlights: Optional[list[StringHighlight]] = None
    pointers: Optional[dict[str, int]] = None


Step = Annotated[
    Union[ArrayStep, GridStep, StringStep], Field(discriminator="kind")
]


class VisualizationTrace(BaseModel):
    renderer: RendererKind
    algorithm_id: Optional[str] = None
    algorithm_name: str
    input: Any
    steps: list[Step]
    operation_counts: dict[str, int] = Field(default_factory=dict)
    truncated: bool = False
    max_steps: int


# ===========================================================================
#  Request / response telá
# ===========================================================================
class CreateProblemRequest(BaseModel):
    name: str
    description: str
    category: ProblemCategory
    input_description: str
    output_description: str


class UpdateProblemRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProblemCategory] = None
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    reference_algorithm_id: Optional[str] = None


class CreateAlgorithmRequest(BaseModel):
    name: str
    code: str
    is_reference: bool = False


class UpdateAlgorithmRequest(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_reference: Optional[bool] = None


class CreateGeneratorRequest(BaseModel):
    name: str
    code: str
    default_sizes: list[int]
    param_spec: list[GeneratorParamSpec] = Field(default_factory=list)


class UpdateGeneratorRequest(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    default_sizes: Optional[list[int]] = None
    param_spec: Optional[list[GeneratorParamSpec]] = None


class GeneratorPreviewRequest(BaseModel):
    n: int
    params: dict[str, Scalar] = Field(default_factory=dict)
    seed: Optional[int] = None


class GeneratorPreviewResponse(BaseModel):
    input: Any
    preview: str
    type: str
    length: int
    elapsed_ms: float
    error: Optional[str] = None


class CreateExperimentRequest(BaseModel):
    name: str
    problem_id: str
    algorithm_ids: list[str]
    generator_id: str
    sizes: list[int]
    repeats: int = 3
    timeout_ms: int = 5000
    seed: Optional[int] = None
    generator_params: dict[str, Scalar] = Field(default_factory=dict)


class VisualizeRequest(BaseModel):
    algorithm_id: Optional[str] = None
    code: Optional[str] = None
    input: Any
    max_steps: int = 2000


class ValidateCodeRequest(BaseModel):
    code: str
    kind: Literal["algorithm", "generator"]


class CodeError(BaseModel):
    line: Optional[int] = None
    message: str
    severity: Literal["error", "warning"]


class ValidateCodeResponse(BaseModel):
    valid: bool
    errors: list[CodeError] = Field(default_factory=list)


# ---- Agregované výsledky (grafy + tabuľka) ----
class ResultPoint(BaseModel):
    input_size: int
    time_ms_min: float
    time_ms_avg: float
    time_ms_max: float
    memory_kb_avg: float
    operation_counts_avg: dict[str, float] = Field(default_factory=dict)


class AlgorithmResultSeries(BaseModel):
    algorithm_id: str
    algorithm_name: str
    is_correct: Optional[bool] = None
    points: list[ResultPoint] = Field(default_factory=list)


class ExperimentResults(BaseModel):
    experiment_id: str
    series: list[AlgorithmResultSeries] = Field(default_factory=list)


# ---- WebSocket správy o priebehu (/ws/experiments/{id}) ----
class ExperimentStartedMessage(BaseModel):
    kind: Literal["experiment_started"] = "experiment_started"
    experiment_id: str
    total_runs: int


class RunStartedMessage(BaseModel):
    kind: Literal["run_started"] = "run_started"
    run_id: str
    algorithm_id: str
    input_size: int
    repeat_index: int


class RunFinishedMessage(BaseModel):
    kind: Literal["run_finished"] = "run_finished"
    run: ExperimentRun
    completed_runs: int
    total_runs: int


class ExperimentFinishedMessage(BaseModel):
    kind: Literal["experiment_finished"] = "experiment_finished"
    experiment_id: str
    status: ExperimentStatus


class ErrorMessage(BaseModel):
    kind: Literal["error"] = "error"
    message: str


ProgressMessage = Annotated[
    Union[
        ExperimentStartedMessage,
        RunStartedMessage,
        RunFinishedMessage,
        ExperimentFinishedMessage,
        ErrorMessage,
    ],
    Field(discriminator="kind"),
]

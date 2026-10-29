"""Pydantic schémy, teda drôtový kontrakt API.

Zrkadlo TypeScript typov vo frontend/src/types/. Polia sú v tvare snake_case,
takže medzi FastAPI a klientom nie je potrebná transformácia. Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

_ORM = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
#  Číselníky
# ---------------------------------------------------------------------------
ProblemCategory = Literal[
    "sorting", "searching", "divide_and_conquer", "string", "dynamic_programming",
    "matrix", "backtracking", "greedy", "graph", "recursive", "data_structures",
    "set", "traversal", "numeric",
]
InputType = Literal[
    "array", "number", "operations", "tree", "graph", "weighted_graph",
    "matrix", "string", "composite",
]
RendererKind = Literal["array", "grid", "graph", "tree", "string", "none"]
Paradigm = Literal[
    "iterative", "recursive", "divide_and_conquer", "dynamic_programming",
    "greedy", "brute_force", "backtracking", "data_structure",
]
ComplexityClass = Literal[
    "O(1)", "O(log log n)", "O(log n)", "O(sqrt n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)",
    "O(2^n)", "O(phi^n)", "O(3^n)", "O(n!)", "other",
]
COMPLEXITY_ORDER = {
    "O(1)": 0, "O(log log n)": 0.5, "O(log n)": 1, "O(sqrt n)": 2, "O(n)": 3, "O(n log n)": 4,
    "O(n^2)": 5, "O(n^3)": 6, "O(phi^n)": 7, "O(2^n)": 8, "O(3^n)": 9, "O(n!)": 10, "other": 99,
}
HighlightRole = str
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
    summary: str = ""
    description: str = ""
    category: ProblemCategory
    input_type: InputType = "array"
    renderer: RendererKind = "array"
    input_description: str = ""
    output_description: str = ""
    reference_algorithm_id: Optional[str] = None
    checker_code: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    is_builtin: bool = False
    sort_order: int = 1000
    created_at: datetime
    updated_at: datetime


class ProblemSummary(Problem):
    algorithm_count: int = 0
    generator_count: int = 0
    visualizable_count: int = 0


class Algorithm(BaseModel):
    model_config = _ORM
    id: str
    problem_id: str
    name: str
    description: str = ""
    code: str
    language: Literal["python"] = "python"
    is_reference: bool = False
    supports_visualization: bool = False
    paradigm: Paradigm = "iterative"
    complexity_time_best: Optional[ComplexityClass] = None
    complexity_time_avg: Optional[ComplexityClass] = None
    complexity_time_worst: Optional[ComplexityClass] = None
    complexity_space: Optional[ComplexityClass] = None
    complexity_note: str = ""
    complexity_param: str = ""
    properties: list[str] = Field(default_factory=list)
    is_builtin: bool = False
    sort_order: int = 1000
    created_at: datetime
    updated_at: datetime


class GeneratorParamSpec(BaseModel):
    name: str
    label: str
    type: Literal["enum", "number", "boolean"]
    options: Optional[list[str]] = None
    option_labels: Optional[dict[str, str]] = None
    default: Scalar


class InputGenerator(BaseModel):
    model_config = _ORM
    id: str
    problem_id: str
    name: str
    description: str = ""
    code: str
    default_sizes: list[int]
    viz_size: int = 10
    param_spec: list[GeneratorParamSpec] = Field(default_factory=list)
    is_builtin: bool = False
    created_at: datetime
    updated_at: datetime


class ExperimentVariant(BaseModel):
    label: str
    params: dict[str, Scalar] = Field(default_factory=dict)


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
    variants: list[ExperimentVariant] = Field(default_factory=list)
    status: ExperimentStatus = "pending"
    total_cases: int = 0
    done_cases: int = 0
    is_builtin: bool = False
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class ExperimentRun(BaseModel):
    model_config = _ORM
    id: str
    experiment_id: str
    algorithm_id: str
    variant_index: int = 0
    variant_label: str = ""
    input_size: int
    repeat_index: int
    execution_time_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    operation_counts: dict[str, int] = Field(default_factory=dict)
    is_correct: Optional[bool] = None
    check_message: Optional[str] = None
    status: RunStatus
    error_message: Optional[str] = None
    created_at: datetime


# ===========================================================================
#  Vizualizácia
# ===========================================================================
class VisualizationTrace(BaseModel):
    renderer: RendererKind
    algorithm_id: Optional[str] = None
    algorithm_name: str
    input: Any
    steps: list[dict[str, Any]]
    structure: Optional[dict[str, Any]] = None
    operation_counts: dict[str, int] = Field(default_factory=dict)
    result: Any = None
    is_correct: Optional[bool] = None
    check_message: Optional[str] = None
    stdout: Optional[str] = None
    truncated: bool = False
    max_steps: int
    uses_tracker: bool = True


# ===========================================================================
#  Požiadavky a odpovede
# ===========================================================================
class CreateProblemRequest(BaseModel):
    name: str
    summary: str = ""
    description: str = ""
    category: ProblemCategory
    input_type: InputType = "array"
    renderer: RendererKind = "array"
    input_description: str = ""
    output_description: str = ""
    checker_code: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class UpdateProblemRequest(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProblemCategory] = None
    input_type: Optional[InputType] = None
    renderer: Optional[RendererKind] = None
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    reference_algorithm_id: Optional[str] = None
    checker_code: Optional[str] = None
    tags: Optional[list[str]] = None


class AlgorithmMeta(BaseModel):
    description: str = ""
    paradigm: Paradigm = "iterative"
    complexity_time_best: Optional[ComplexityClass] = None
    complexity_time_avg: Optional[ComplexityClass] = None
    complexity_time_worst: Optional[ComplexityClass] = None
    complexity_space: Optional[ComplexityClass] = None
    complexity_note: str = ""
    complexity_param: str = ""
    properties: list[str] = Field(default_factory=list)


class CreateAlgorithmRequest(AlgorithmMeta):
    name: str
    code: str
    is_reference: bool = False


class UpdateAlgorithmRequest(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_reference: Optional[bool] = None
    description: Optional[str] = None
    paradigm: Optional[Paradigm] = None
    complexity_time_best: Optional[ComplexityClass] = None
    complexity_time_avg: Optional[ComplexityClass] = None
    complexity_time_worst: Optional[ComplexityClass] = None
    complexity_space: Optional[ComplexityClass] = None
    complexity_note: Optional[str] = None
    complexity_param: Optional[str] = None
    properties: Optional[list[str]] = None


class CreateGeneratorRequest(BaseModel):
    name: str
    description: str = ""
    code: str
    default_sizes: list[int]
    viz_size: int = 10
    param_spec: list[GeneratorParamSpec] = Field(default_factory=list)


class UpdateGeneratorRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    default_sizes: Optional[list[int]] = None
    viz_size: Optional[int] = None
    param_spec: Optional[list[GeneratorParamSpec]] = None


class GeneratorPreviewRequest(BaseModel):
    n: int
    params: dict[str, Scalar] = Field(default_factory=dict)
    seed: Optional[int] = None


class GeneratorCodePreviewRequest(GeneratorPreviewRequest):
    code: str


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
    seed: Optional[int] = 42
    generator_params: dict[str, Scalar] = Field(default_factory=dict)
    variants: list[ExperimentVariant] = Field(default_factory=list)


class ExperimentProgress(BaseModel):
    experiment: Experiment
    completed_cases: int
    total_cases: int
    finished: bool
    last_errors: list[str] = Field(default_factory=list)


class VisualizeRequest(BaseModel):
    algorithm_id: Optional[str] = None
    code: Optional[str] = None
    problem_id: Optional[str] = None
    input: Any
    max_steps: int = 2000


class ValidateCodeRequest(BaseModel):
    code: str
    kind: Literal["algorithm", "generator", "checker"]


class CodeError(BaseModel):
    line: Optional[int] = None
    message: str
    severity: Literal["error", "warning"]


class ValidateCodeResponse(BaseModel):
    valid: bool
    errors: list[CodeError] = Field(default_factory=list)
    uses_tracker: bool = False


# ---- Agregované výsledky ----
class ResultPoint(BaseModel):
    input_size: int
    runs: int = 0
    time_ms_min: Optional[float] = None
    time_ms_avg: Optional[float] = None
    time_ms_max: Optional[float] = None
    memory_kb_avg: Optional[float] = None
    operation_counts_avg: dict[str, float] = Field(default_factory=dict)
    timeouts: int = 0
    errors: int = 0
    incorrect: int = 0


class ComplexityFit(BaseModel):
    metric: Literal["operations", "time"]
    status: Literal["ok", "insufficient_data"]
    best: Optional[str] = None
    second: Optional[str] = None
    best_error: Optional[float] = None
    second_error: Optional[float] = None
    exponent: Optional[float] = None
    confidence: Literal["high", "medium", "low", "none"] = "none"
    reason: Optional[str] = None


class ComplexityEstimate(BaseModel):
    operations: ComplexityFit
    time: ComplexityFit
    declared: Optional[str] = None
    declared_case: Literal["avg", "worst", "best"] = "avg"
    agreement: Literal["match", "mismatch", "unknown"] = "unknown"
    used_metric: Literal["operations", "time", "none"] = "none"


class AlgorithmResultSeries(BaseModel):
    algorithm_id: str
    algorithm_name: str
    variant_index: int = 0
    variant_label: str = ""
    is_correct: Optional[bool] = None
    check_messages: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    points: list[ResultPoint] = Field(default_factory=list)
    complexity: Optional[ComplexityEstimate] = None


class ExperimentResults(BaseModel):
    experiment_id: str
    variants: list[ExperimentVariant] = Field(default_factory=list)
    series: list[AlgorithmResultSeries] = Field(default_factory=list)


class CatalogInfo(BaseModel):
    edit_protected: bool
    remote_runner: bool
    max_algorithms: int
    max_timeout_ms: int
    problems: int = 0
    algorithms: int = 0
    viz_limits: dict[str, int] = Field(default_factory=dict)

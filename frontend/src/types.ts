// Typy zodpovedajú Pydantic schémam v backend/app/schemas.py (snake_case bez mapovania).

export type ProblemCategory =
  | 'sorting' | 'searching' | 'divide_and_conquer' | 'string' | 'dynamic_programming'
  | 'matrix' | 'backtracking' | 'greedy' | 'graph' | 'recursive' | 'data_structures'
  | 'set' | 'traversal' | 'numeric'

export type InputType =
  | 'array' | 'number' | 'operations' | 'tree' | 'graph' | 'weighted_graph'
  | 'matrix' | 'string' | 'composite'

export type RendererKind = 'array' | 'grid' | 'graph' | 'tree' | 'string' | 'none'

export type Paradigm =
  | 'iterative' | 'recursive' | 'divide_and_conquer' | 'dynamic_programming'
  | 'greedy' | 'brute_force' | 'backtracking' | 'data_structure'

export type ComplexityClass =
  | 'O(1)' | 'O(log log n)' | 'O(log n)' | 'O(sqrt n)' | 'O(n)' | 'O(n log n)' | 'O(n^2)'
  | 'O(n^3)' | 'O(2^n)' | 'O(phi^n)' | 'O(3^n)' | 'O(n!)' | 'other'

export type Scalar = string | number | boolean | null

export interface Problem {
  id: string
  name: string
  summary: string
  description: string
  category: ProblemCategory
  input_type: InputType
  renderer: RendererKind
  input_description: string
  output_description: string
  reference_algorithm_id: string | null
  checker_code: string | null
  tags: string[]
  is_builtin: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ProblemSummary extends Problem {
  algorithm_count: number
  generator_count: number
  visualizable_count: number
}

export interface Algorithm {
  id: string
  problem_id: string
  name: string
  description: string
  code: string
  language: 'python'
  is_reference: boolean
  supports_visualization: boolean
  paradigm: Paradigm
  complexity_time_best: ComplexityClass | null
  complexity_time_avg: ComplexityClass | null
  complexity_time_worst: ComplexityClass | null
  complexity_space: ComplexityClass | null
  complexity_note: string
  complexity_param: string
  properties: string[]
  is_builtin: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface GeneratorParamSpec {
  name: string
  label: string
  type: 'enum' | 'number' | 'boolean'
  options?: string[] | null
  option_labels?: Record<string, string> | null
  default: Scalar
}

export interface InputGenerator {
  id: string
  problem_id: string
  name: string
  description: string
  code: string
  default_sizes: number[]
  viz_size: number
  param_spec: GeneratorParamSpec[]
  is_builtin: boolean
  created_at: string
  updated_at: string
}

export interface ExperimentVariant {
  label: string
  params: Record<string, Scalar>
}

export type ExperimentStatus = 'pending' | 'running' | 'done' | 'failed' | 'cancelled'

export interface Experiment {
  id: string
  name: string
  problem_id: string
  algorithm_ids: string[]
  generator_id: string
  sizes: number[]
  repeats: number
  timeout_ms: number
  seed: number | null
  generator_params: Record<string, Scalar>
  variants: ExperimentVariant[]
  status: ExperimentStatus
  total_cases: number
  done_cases: number
  is_builtin: boolean
  created_at: string
  started_at: string | null
  finished_at: string | null
}

export interface ExperimentProgress {
  experiment: Experiment
  completed_cases: number
  total_cases: number
  finished: boolean
  last_errors: string[]
}

export interface ResultPoint {
  input_size: number
  runs: number
  time_ms_min: number | null
  time_ms_avg: number | null
  time_ms_max: number | null
  memory_kb_avg: number | null
  operation_counts_avg: Record<string, number>
  timeouts: number
  errors: number
  incorrect: number
}

export interface ComplexityFit {
  metric: 'operations' | 'time'
  status: 'ok' | 'insufficient_data'
  best: string | null
  second: string | null
  best_error: number | null
  second_error: number | null
  exponent: number | null
  confidence: 'high' | 'medium' | 'low' | 'none'
  reason: string | null
}

export interface ComplexityEstimate {
  operations: ComplexityFit
  time: ComplexityFit
  declared: string | null
  declared_case: 'avg' | 'worst' | 'best'
  agreement: 'match' | 'mismatch' | 'unknown'
  used_metric: 'operations' | 'time' | 'none'
}

export interface AlgorithmResultSeries {
  algorithm_id: string
  algorithm_name: string
  variant_index: number
  variant_label: string
  is_correct: boolean | null
  check_messages: string[]
  errors: string[]
  points: ResultPoint[]
  complexity: ComplexityEstimate | null
}

export interface ExperimentResults {
  experiment_id: string
  variants: ExperimentVariant[]
  series: AlgorithmResultSeries[]
}

export interface CatalogInfo {
  edit_protected: boolean
  remote_runner: boolean
  max_algorithms: number
  max_timeout_ms: number
  problems: number
  algorithms: number
  viz_limits: Record<string, number>
}

export interface GeneratorPreview {
  input: unknown
  preview: string
  type: string
  length: number
  elapsed_ms: number
  error: string | null
}

export interface CodeError {
  line: number | null
  message: string
  severity: 'error' | 'warning'
}

export interface ValidateResult {
  valid: boolean
  errors: CodeError[]
  uses_tracker: boolean
}

// ---------------------------------------------------------------------------
//  Kroky vizualizácie (zaznamenáva ich tracker v runner/algolab_sandbox/tracker.py)
// ---------------------------------------------------------------------------

export type Role =
  | 'compare' | 'swap' | 'pivot' | 'active' | 'match' | 'sorted' | 'visited' | 'tree' | 'path'

interface StepBase {
  index: number
  type: string
  label: string
  code_line?: number
}

export interface ArrayStep extends StepBase {
  kind: 'array'
  array: (number | string | null)[]
  highlights: { index: number; role: Role }[]
  pointers?: Record<string, number>
  labels?: string[]
}

export interface GridStep extends StepBase {
  kind: 'grid'
  grid: (number | string | null)[][]
  highlights: { row: number; col: number; role: Role }[]
  row_labels?: string[]
  col_labels?: string[]
}

export interface GraphStep extends StepBase {
  kind: 'graph'
  node_roles: Record<string, Role>
  edge_roles: { u: number; v: number; role: Role }[]
  labels?: Record<string, string>
  frontier?: { name: string; items: (number | string)[] }
}

export interface TreeNode {
  id: string | number
  label: string
  children: (string | number | null)[]
  extra?: string
}

export interface TreeStep extends StepBase {
  kind: 'tree'
  nodes: TreeNode[]
  root: string | number | null
  highlights: { id: string | number; role: Role }[]
}

export interface StringStep extends StepBase {
  kind: 'string'
  value: string
  pattern: string | null
  offset: number
  highlights: { index: number; role: Role }[]
  pattern_highlights: { index: number; role: Role }[]
}

export interface NoneStep extends StepBase {
  kind: 'none'
}

export type Step = ArrayStep | GridStep | GraphStep | TreeStep | StringStep | NoneStep

export interface GraphStructure {
  type: 'graph'
  n: number
  edges: number[][]
  directed: boolean
  weighted: boolean
}

export interface VisualizationTrace {
  renderer: RendererKind
  algorithm_id: string | null
  algorithm_name: string
  input: unknown
  steps: Step[]
  structure: GraphStructure | null
  operation_counts: Record<string, number>
  result: unknown
  is_correct: boolean | null
  check_message: string | null
  stdout: string | null
  truncated: boolean
  max_steps: number
  uses_tracker: boolean
}

// ============================================================================
//  API kontrakt — request/response telá, agregované výsledky, WS správy
//  a typované rozhranie ApiClient (TS zrkadlo zoznamu REST endpointov).
//
//  Base URL: /api   ·   WebSocket: /ws
//  Všetky telá sú snake_case (zhodné s Pydantic modelmi na backende).
// ============================================================================

import type {
  Algorithm,
  Experiment,
  ExperimentRun,
  GeneratorParamSpec,
  InputGenerator,
  Problem,
  ProblemCategory,
  ExperimentStatus,
} from './domain'
import type { VisualizationTrace } from './steps'

// ---------------------------------------------------------------------------
//  Problems
// ---------------------------------------------------------------------------
export interface CreateProblemRequest {
  name: string
  description: string
  category: ProblemCategory
  input_description: string
  output_description: string
}
export type UpdateProblemRequest = Partial<CreateProblemRequest> & {
  reference_algorithm_id?: string | null
}

// ---------------------------------------------------------------------------
//  Algorithms
// ---------------------------------------------------------------------------
export interface CreateAlgorithmRequest {
  name: string
  code: string
  is_reference?: boolean
}
export type UpdateAlgorithmRequest = Partial<CreateAlgorithmRequest>

// ---------------------------------------------------------------------------
//  Generators
// ---------------------------------------------------------------------------
export interface CreateGeneratorRequest {
  name: string
  code: string
  default_sizes: number[]
  param_spec?: GeneratorParamSpec[]
}
export type UpdateGeneratorRequest = Partial<CreateGeneratorRequest>

export interface GeneratorPreviewRequest {
  n: number
  params?: Record<string, string | number | boolean>
  seed?: number | null
}
export interface GeneratorPreviewResponse {
  /** Vygenerovaný vstup (Python objekt serializovaný do JSON). */
  input: unknown
  /** Skrátená textová reprezentácia pre náhľad. */
  preview: string
  /** Napr. "list[int]". */
  type: string
  length: number
  elapsed_ms: number
  error: string | null
}

// ---------------------------------------------------------------------------
//  Experiments
// ---------------------------------------------------------------------------
export interface CreateExperimentRequest {
  name: string
  problem_id: string
  algorithm_ids: string[]
  generator_id: string
  sizes: number[]
  repeats: number
  timeout_ms: number
  seed?: number | null
  generator_params?: Record<string, string | number | boolean>
}

// ---------------------------------------------------------------------------
//  Vizualizácia (krok-za-krokom)
// ---------------------------------------------------------------------------
export interface VisualizeRequest {
  /** Buď odkaz na uložený algoritmus… */
  algorithm_id?: string
  /** …alebo ad-hoc kód z editora (pred uložením). Práve jedno z dvojice. */
  code?: string
  /** Vstup ako Python objekt (JSON). */
  input: unknown
  /** Strop počtu krokov (predvolene napr. 2000). */
  max_steps?: number
}

// ---------------------------------------------------------------------------
//  Validácia kódu (spätná väzba v editore; sandbox odmietne import os a pod.)
// ---------------------------------------------------------------------------
export interface ValidateCodeRequest {
  code: string
  kind: 'algorithm' | 'generator'
}
export interface CodeError {
  line?: number
  message: string
  severity: 'error' | 'warning'
}
export interface ValidateCodeResponse {
  valid: boolean
  errors: CodeError[]
}

// ---------------------------------------------------------------------------
//  Agregované výsledky (grafy + tabuľka). Min/avg/max cez opakovania.
// ---------------------------------------------------------------------------
export interface ResultPoint {
  input_size: number
  time_ms_min: number
  time_ms_avg: number
  time_ms_max: number
  memory_kb_avg: number
  operation_counts_avg: Record<string, number>
}
export interface AlgorithmResultSeries {
  algorithm_id: string
  algorithm_name: string
  is_correct: boolean | null
  points: ResultPoint[]
}
export interface ExperimentResults {
  experiment_id: string
  series: AlgorithmResultSeries[]
}

// ---------------------------------------------------------------------------
//  WebSocket správy o priebehu experimentu  (/ws/experiments/{id})
// ---------------------------------------------------------------------------
export type ProgressMessage =
  | { kind: 'experiment_started'; experiment_id: string; total_runs: number }
  | {
      kind: 'run_started'
      run_id: string
      algorithm_id: string
      input_size: number
      repeat_index: number
    }
  | {
      kind: 'run_finished'
      run: ExperimentRun
      completed_runs: number
      total_runs: number
    }
  | {
      kind: 'experiment_finished'
      experiment_id: string
      status: ExperimentStatus
    }
  | { kind: 'error'; message: string }

// ---------------------------------------------------------------------------
//  Štandardná chybová obálka (FastAPI HTTPException → { detail }).
// ---------------------------------------------------------------------------
export interface ApiError {
  detail: string
  code?: string
}

export type ExportFormat = 'csv' | 'json'

// ---------------------------------------------------------------------------
//  Typované rozhranie klienta — TS zrkadlo zoznamu REST endpointov.
//  Fáza 0 dodá mock implementáciu, neskôr ju nahradí HTTP implementácia.
// ---------------------------------------------------------------------------
export interface ApiClient {
  // Problems
  listProblems(): Promise<Problem[]>
  getProblem(id: string): Promise<Problem>
  createProblem(body: CreateProblemRequest): Promise<Problem>
  updateProblem(id: string, body: UpdateProblemRequest): Promise<Problem>
  deleteProblem(id: string): Promise<void>

  // Algorithms
  listAlgorithms(problemId: string): Promise<Algorithm[]>
  getAlgorithm(id: string): Promise<Algorithm>
  createAlgorithm(
    problemId: string,
    body: CreateAlgorithmRequest,
  ): Promise<Algorithm>
  updateAlgorithm(id: string, body: UpdateAlgorithmRequest): Promise<Algorithm>
  deleteAlgorithm(id: string): Promise<void>

  // Generators
  listGenerators(problemId: string): Promise<InputGenerator[]>
  getGenerator(id: string): Promise<InputGenerator>
  createGenerator(
    problemId: string,
    body: CreateGeneratorRequest,
  ): Promise<InputGenerator>
  updateGenerator(
    id: string,
    body: UpdateGeneratorRequest,
  ): Promise<InputGenerator>
  deleteGenerator(id: string): Promise<void>
  previewGenerator(
    id: string,
    body: GeneratorPreviewRequest,
  ): Promise<GeneratorPreviewResponse>

  // Experiments
  listExperiments(): Promise<Experiment[]>
  getExperiment(id: string): Promise<Experiment>
  createExperiment(body: CreateExperimentRequest): Promise<Experiment>
  deleteExperiment(id: string): Promise<void>
  runExperiment(id: string): Promise<void> // 202; priebeh cez WS
  cancelExperiment(id: string): Promise<void>
  listRuns(experimentId: string): Promise<ExperimentRun[]>
  getResults(experimentId: string): Promise<ExperimentResults>
  exportExperiment(experimentId: string, format: ExportFormat): Promise<Blob>

  // Vizualizácia + validácia
  visualize(body: VisualizeRequest): Promise<VisualizationTrace>
  validateCode(body: ValidateCodeRequest): Promise<ValidateCodeResponse>
}

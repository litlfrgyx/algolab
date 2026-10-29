// ============================================================================
//  MockApiClient — in-memory implementácia kontraktu ApiClient.
//
//  Toto je celá dátová vrstva Fázy 0. Stránky volajú `api` (singleton z
//  ./index), nie hardcoded konštanty. Keď príde FastAPI, vznikne HttpApiClient
//  implements ApiClient a v ./index sa prepne jeden riadok — stránky sa nemenia.
//
//  Pozn.: `visualize` a `previewGenerator` bežia reálnu (JS) logiku, takže
//  Step kontrakt aj reprodukovateľnosť generátora sú overené end-to-end.
// ============================================================================

import type {
  Algorithm,
  AlgorithmResultSeries,
  ApiClient,
  CreateAlgorithmRequest,
  CreateExperimentRequest,
  CreateGeneratorRequest,
  CreateProblemRequest,
  Experiment,
  ExperimentResults,
  ExperimentRun,
  ExportFormat,
  GeneratorPreviewRequest,
  GeneratorPreviewResponse,
  InputGenerator,
  Problem,
  ResultPoint,
  UpdateAlgorithmRequest,
  UpdateGeneratorRequest,
  UpdateProblemRequest,
  ValidateCodeRequest,
  ValidateCodeResponse,
  VisualizeRequest,
  VisualizationTrace,
  CodeError,
} from '../types'
import { generateArray, type GeneratorMode } from './mock/generators'
import {
  seedAlgorithms,
  seedExperiments,
  seedGenerators,
  seedProblems,
  synthRunsFor,
} from './mock/seed'
import { SORT_TRACERS } from './mock/sorting'

const nowIso = () => new Date().toISOString()
const uid = (p: string) => `${p}_${Math.random().toString(36).slice(2, 10)}`

function notFound(kind: string, id: string): never {
  throw new Error(`${kind} '${id}' neexistuje`)
}

export class MockApiClient implements ApiClient {
  private problems = seedProblems()
  private algorithms = seedAlgorithms()
  private generators = seedGenerators()
  private experiments = seedExperiments()
  private runs: ExperimentRun[] = []

  // simulácia latencie siete
  private delay<T>(value: T, ms = 120): Promise<T> {
    return new Promise((resolve) => setTimeout(() => resolve(value), ms))
  }

  // ---- Problems ----
  listProblems() {
    return this.delay(this.problems.map((p) => ({ ...p })))
  }
  getProblem(id: string) {
    const p = this.problems.find((x) => x.id === id) ?? notFound('Problem', id)
    return this.delay({ ...p })
  }
  createProblem(body: CreateProblemRequest) {
    const p: Problem = {
      id: uid('prob'),
      reference_algorithm_id: null,
      created_at: nowIso(),
      updated_at: nowIso(),
      ...body,
    }
    this.problems.push(p)
    return this.delay({ ...p })
  }
  updateProblem(id: string, body: UpdateProblemRequest) {
    const p = this.problems.find((x) => x.id === id) ?? notFound('Problem', id)
    Object.assign(p, body, { updated_at: nowIso() })
    return this.delay({ ...p })
  }
  deleteProblem(id: string) {
    this.problems = this.problems.filter((x) => x.id !== id)
    return this.delay(undefined as void)
  }

  // ---- Algorithms ----
  listAlgorithms(problemId: string) {
    return this.delay(
      this.algorithms.filter((a) => a.problem_id === problemId).map((a) => ({ ...a })),
    )
  }
  getAlgorithm(id: string) {
    const a = this.algorithms.find((x) => x.id === id) ?? notFound('Algorithm', id)
    return this.delay({ ...a })
  }
  createAlgorithm(problemId: string, body: CreateAlgorithmRequest) {
    const a: Algorithm = {
      id: uid('alg'),
      problem_id: problemId,
      language: 'python',
      is_reference: body.is_reference ?? false,
      supports_visualization: /\btracker\b/.test(body.code),
      created_at: nowIso(),
      updated_at: nowIso(),
      name: body.name,
      code: body.code,
    }
    this.algorithms.push(a)
    return this.delay({ ...a })
  }
  updateAlgorithm(id: string, body: UpdateAlgorithmRequest) {
    const a = this.algorithms.find((x) => x.id === id) ?? notFound('Algorithm', id)
    Object.assign(a, body, { updated_at: nowIso() })
    if (body.code !== undefined) a.supports_visualization = /\btracker\b/.test(body.code)
    return this.delay({ ...a })
  }
  deleteAlgorithm(id: string) {
    this.algorithms = this.algorithms.filter((x) => x.id !== id)
    return this.delay(undefined as void)
  }

  // ---- Generators ----
  listGenerators(problemId: string) {
    return this.delay(
      this.generators.filter((g) => g.problem_id === problemId).map((g) => ({ ...g })),
    )
  }
  getGenerator(id: string) {
    const g = this.generators.find((x) => x.id === id) ?? notFound('Generator', id)
    return this.delay({ ...g })
  }
  createGenerator(problemId: string, body: CreateGeneratorRequest) {
    const g: InputGenerator = {
      id: uid('gen'),
      problem_id: problemId,
      param_spec: body.param_spec ?? [],
      created_at: nowIso(),
      updated_at: nowIso(),
      name: body.name,
      code: body.code,
      default_sizes: body.default_sizes,
    }
    this.generators.push(g)
    return this.delay({ ...g })
  }
  updateGenerator(id: string, body: UpdateGeneratorRequest) {
    const g = this.generators.find((x) => x.id === id) ?? notFound('Generator', id)
    Object.assign(g, body, { updated_at: nowIso() })
    return this.delay({ ...g })
  }
  deleteGenerator(id: string) {
    this.generators = this.generators.filter((x) => x.id !== id)
    return this.delay(undefined as void)
  }
  previewGenerator(id: string, body: GeneratorPreviewRequest) {
    const g = this.generators.find((x) => x.id === id) ?? notFound('Generator', id)
    const started = performance.now()
    const mode = (body.params?.mode as GeneratorMode) ?? 'random'
    const n = Math.max(0, Math.min(body.n, 100000))
    const input = generateArray(n, mode, body.seed ?? 42)
    const head = input.slice(0, 40)
    const resp: GeneratorPreviewResponse = {
      input,
      preview: head.join(' ') + (input.length > head.length ? ' …' : ''),
      type: 'list[int]',
      length: input.length,
      elapsed_ms: +(performance.now() - started).toFixed(2),
      error: null,
    }
    void g
    return this.delay(resp)
  }

  // ---- Experiments ----
  listExperiments() {
    return this.delay(this.experiments.map((e) => ({ ...e })))
  }
  getExperiment(id: string) {
    const e = this.experiments.find((x) => x.id === id) ?? notFound('Experiment', id)
    return this.delay({ ...e })
  }
  createExperiment(body: CreateExperimentRequest) {
    const e: Experiment = {
      id: uid('exp'),
      repeats: body.repeats,
      timeout_ms: body.timeout_ms,
      seed: body.seed ?? null,
      generator_params: body.generator_params ?? {},
      status: 'pending',
      created_at: nowIso(),
      started_at: null,
      finished_at: null,
      name: body.name,
      problem_id: body.problem_id,
      algorithm_ids: body.algorithm_ids,
      generator_id: body.generator_id,
      sizes: body.sizes,
    }
    this.experiments.push(e)
    return this.delay({ ...e })
  }
  deleteExperiment(id: string) {
    this.experiments = this.experiments.filter((x) => x.id !== id)
    this.runs = this.runs.filter((r) => r.experiment_id !== id)
    return this.delay(undefined as void)
  }
  runExperiment(id: string) {
    // mock: syntetizuje behy (reálne by ich vyrobil sandbox executor)
    const e = this.experiments.find((x) => x.id === id) ?? notFound('Experiment', id)
    this.runs = this.runs.filter((r) => r.experiment_id !== id).concat(synthRunsFor(e))
    e.status = 'done'
    e.started_at = nowIso()
    e.finished_at = nowIso()
    return this.delay(undefined as void, 400)
  }
  cancelExperiment(id: string) {
    const e = this.experiments.find((x) => x.id === id)
    if (e && e.status === 'running') e.status = 'cancelled'
    return this.delay(undefined as void)
  }
  listRuns(experimentId: string) {
    return this.delay(
      this.runs.filter((r) => r.experiment_id === experimentId).map((r) => ({ ...r })),
    )
  }
  getResults(experimentId: string) {
    const exp =
      this.experiments.find((x) => x.id === experimentId) ??
      notFound('Experiment', experimentId)
    const runs = this.runs.filter((r) => r.experiment_id === experimentId)
    const series: AlgorithmResultSeries[] = exp.algorithm_ids.map((algId) => {
      const algo = this.algorithms.find((a) => a.id === algId)
      const points: ResultPoint[] = exp.sizes.map((size) => {
        const subset = runs.filter(
          (r) => r.algorithm_id === algId && r.input_size === size && r.status === 'ok',
        )
        const times = subset.map((r) => r.execution_time_ms ?? 0)
        const mems = subset.map((r) => r.memory_kb ?? 0)
        const opAvg: Record<string, number> = {}
        for (const r of subset)
          for (const [k, v] of Object.entries(r.operation_counts))
            opAvg[k] = (opAvg[k] ?? 0) + v / Math.max(1, subset.length)
        return {
          input_size: size,
          time_ms_min: times.length ? Math.min(...times) : 0,
          time_ms_avg: times.length ? times.reduce((a, b) => a + b, 0) / times.length : 0,
          time_ms_max: times.length ? Math.max(...times) : 0,
          memory_kb_avg: mems.length ? mems.reduce((a, b) => a + b, 0) / mems.length : 0,
          operation_counts_avg: opAvg,
        }
      })
      return {
        algorithm_id: algId,
        algorithm_name: algo?.name ?? algId,
        is_correct: runs.some((r) => r.algorithm_id === algId && r.is_correct === false)
          ? false
          : true,
        points,
      }
    })
    const results: ExperimentResults = { experiment_id: experimentId, series }
    return this.delay(results)
  }
  exportExperiment(experimentId: string, format: ExportFormat) {
    const runs = this.runs.filter((r) => r.experiment_id === experimentId)
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(runs, null, 2)], { type: 'application/json' })
      return this.delay(blob)
    }
    const header = 'algorithm_id,input_size,repeat_index,execution_time_ms,memory_kb,compare,swap,is_correct,status'
    const lines = runs.map((r) =>
      [
        r.algorithm_id,
        r.input_size,
        r.repeat_index,
        r.execution_time_ms ?? '',
        r.memory_kb ?? '',
        r.operation_counts.compare ?? '',
        r.operation_counts.swap ?? '',
        r.is_correct ?? '',
        r.status,
      ].join(','),
    )
    const blob = new Blob([[header, ...lines].join('\n')], { type: 'text/csv' })
    return this.delay(blob)
  }

  // ---- Vizualizácia + validácia ----
  visualize(body: VisualizeRequest): Promise<VisualizationTrace> {
    const input = Array.isArray(body.input) ? (body.input as number[]) : []
    const maxSteps = body.max_steps ?? 2000
    const tracer = body.algorithm_id ? SORT_TRACERS[body.algorithm_id] : undefined
    if (!tracer) {
      throw new Error(
        'Mock vizualizér zatiaľ podporuje len seedované sorting algoritmy (alg_bubble, alg_quick, alg_insertion).',
      )
    }
    return this.delay(tracer(input, maxSteps), 60)
  }
  validateCode(body: ValidateCodeRequest) {
    const errors: CodeError[] = []
    const lines = body.code.split('\n')
    const banned = /\b(import\s+(os|sys|subprocess|socket|shutil)|__import__|open\s*\()/
    lines.forEach((line, i) => {
      if (banned.test(line))
        errors.push({
          line: i + 1,
          message: 'Zakázaná operácia (prístup k FS/sieti/systému) — sandbox ju odmietne.',
          severity: 'error',
        })
    })
    const entry = body.kind === 'algorithm' ? /def\s+solve\s*\(/ : /def\s+generate\s*\(/
    if (!entry.test(body.code))
      errors.push({
        message:
          body.kind === 'algorithm'
            ? 'Chýba definícia funkcie def solve(data) alebo def solve(data, tracker).'
            : 'Chýba definícia funkcie def generate(n, **params).',
        severity: 'error',
      })
    const resp: ValidateCodeResponse = { valid: errors.length === 0, errors }
    return this.delay(resp)
  }
}

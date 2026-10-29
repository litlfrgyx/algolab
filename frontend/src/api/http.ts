// ============================================================================
//  HttpApiClient — reálna implementácia kontraktu ApiClient cez FastAPI backend.
//
//  Base URL: import.meta.env.VITE_API_BASE (predvolene http://localhost:8000).
//  Telá sú snake_case = zhodné s Pydantic schémami → žiadne mapovanie.
// ============================================================================

import type {
  Algorithm,
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
  UpdateAlgorithmRequest,
  UpdateGeneratorRequest,
  UpdateProblemRequest,
  ValidateCodeRequest,
  ValidateCodeResponse,
  VisualizationTrace,
  VisualizeRequest,
} from '../types'

const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const err = await res.json()
      if (err?.detail) detail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)
    } catch {
      /* telo nie je JSON */
    }
    throw new Error(detail)
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

export class HttpApiClient implements ApiClient {
  // Problems
  listProblems() {
    return req<Problem[]>('GET', '/api/problems')
  }
  getProblem(id: string) {
    return req<Problem>('GET', `/api/problems/${id}`)
  }
  createProblem(body: CreateProblemRequest) {
    return req<Problem>('POST', '/api/problems', body)
  }
  updateProblem(id: string, body: UpdateProblemRequest) {
    return req<Problem>('PUT', `/api/problems/${id}`, body)
  }
  deleteProblem(id: string) {
    return req<void>('DELETE', `/api/problems/${id}`)
  }

  // Algorithms
  listAlgorithms(problemId: string) {
    return req<Algorithm[]>('GET', `/api/problems/${problemId}/algorithms`)
  }
  getAlgorithm(id: string) {
    return req<Algorithm>('GET', `/api/algorithms/${id}`)
  }
  createAlgorithm(problemId: string, body: CreateAlgorithmRequest) {
    return req<Algorithm>('POST', `/api/problems/${problemId}/algorithms`, body)
  }
  updateAlgorithm(id: string, body: UpdateAlgorithmRequest) {
    return req<Algorithm>('PUT', `/api/algorithms/${id}`, body)
  }
  deleteAlgorithm(id: string) {
    return req<void>('DELETE', `/api/algorithms/${id}`)
  }

  // Generators
  listGenerators(problemId: string) {
    return req<InputGenerator[]>('GET', `/api/problems/${problemId}/generators`)
  }
  getGenerator(id: string) {
    return req<InputGenerator>('GET', `/api/generators/${id}`)
  }
  createGenerator(problemId: string, body: CreateGeneratorRequest) {
    return req<InputGenerator>('POST', `/api/problems/${problemId}/generators`, body)
  }
  updateGenerator(id: string, body: UpdateGeneratorRequest) {
    return req<InputGenerator>('PUT', `/api/generators/${id}`, body)
  }
  deleteGenerator(id: string) {
    return req<void>('DELETE', `/api/generators/${id}`)
  }
  previewGenerator(id: string, body: GeneratorPreviewRequest) {
    return req<GeneratorPreviewResponse>('POST', `/api/generators/${id}/preview`, body)
  }

  // Experiments
  listExperiments() {
    return req<Experiment[]>('GET', '/api/experiments')
  }
  getExperiment(id: string) {
    return req<Experiment>('GET', `/api/experiments/${id}`)
  }
  createExperiment(body: CreateExperimentRequest) {
    return req<Experiment>('POST', '/api/experiments', body)
  }
  deleteExperiment(id: string) {
    return req<void>('DELETE', `/api/experiments/${id}`)
  }
  async runExperiment(id: string) {
    await req<Experiment>('POST', `/api/experiments/${id}/run`)
  }
  async cancelExperiment(id: string) {
    await req<Experiment>('POST', `/api/experiments/${id}/cancel`)
  }
  listRuns(experimentId: string) {
    return req<ExperimentRun[]>('GET', `/api/experiments/${experimentId}/runs`)
  }
  getResults(experimentId: string) {
    return req<ExperimentResults>('GET', `/api/experiments/${experimentId}/results`)
  }
  async exportExperiment(experimentId: string, format: ExportFormat) {
    const res = await fetch(`${BASE}/api/experiments/${experimentId}/export?format=${format}`)
    if (!res.ok) throw new Error(`Export zlyhal: ${res.status}`)
    return res.blob()
  }

  // Vizualizácia + validácia
  visualize(body: VisualizeRequest) {
    return req<VisualizationTrace>('POST', '/api/visualize', body)
  }
  validateCode(body: ValidateCodeRequest) {
    return req<ValidateCodeResponse>('POST', '/api/code/validate', body)
  }
}

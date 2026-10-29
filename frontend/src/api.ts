// Klient REST API backendu. API je vždy na tej istej adrese ako stránka (/api):
// pri vývoji ho presmeruje Vite (vite.config.ts), po nasadení Vercel.

import type {
  Algorithm, CatalogInfo, Experiment, ExperimentProgress, ExperimentResults, ExperimentVariant,
  GeneratorParamSpec, GeneratorPreview, InputGenerator, Problem, ProblemSummary, Scalar,
  ValidateResult, VisualizationTrace,
} from './types'

const BASE: string = import.meta.env.VITE_API_BASE ?? ''
const PASSWORD_KEY = 'algolab.editPassword'

export function getPassword(): string {
  try {
    return localStorage.getItem(PASSWORD_KEY) ?? ''
  } catch {
    return ''
  }
}

export function setPassword(value: string) {
  try {
    if (value) localStorage.setItem(PASSWORD_KEY, value)
    else localStorage.removeItem(PASSWORD_KEY)
  } catch {
    /* úložisko nemusí byť dostupné */
  }
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const pw = getPassword()
  if (pw) headers['X-Edit-Password'] = pw
  let res: Response
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'Server nie je dostupný. Skontroluj, či beží backend.')
  }
  if (!res.ok) {
    let detail = `Chyba ${res.status}`
    try {
      const err = await res.json()
      if (typeof err?.detail === 'string') detail = err.detail
      else if (Array.isArray(err?.detail)) detail = err.detail.map((d: { msg?: string }) => d.msg).join(', ')
    } catch {
      /* telo nie je JSON */
    }
    throw new ApiError(res.status, detail)
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

export interface AlgorithmInput {
  name: string
  code: string
  description?: string
  paradigm?: Algorithm['paradigm']
  complexity_time_best?: Algorithm['complexity_time_best']
  complexity_time_avg?: Algorithm['complexity_time_avg']
  complexity_time_worst?: Algorithm['complexity_time_worst']
  complexity_space?: Algorithm['complexity_space']
  complexity_note?: string
  complexity_param?: string
  properties?: string[]
}

export interface GeneratorInput {
  name: string
  code: string
  description?: string
  default_sizes: number[]
  viz_size?: number
  param_spec?: GeneratorParamSpec[]
}

export interface ExperimentInput {
  name: string
  problem_id: string
  algorithm_ids: string[]
  generator_id: string
  sizes: number[]
  repeats: number
  timeout_ms?: number
  seed?: number | null
  generator_params?: Record<string, Scalar>
  variants?: ExperimentVariant[]
}

export const api = {
  info: () => req<CatalogInfo>('GET', '/api/info'),

  problems: () => req<ProblemSummary[]>('GET', '/api/problems'),
  problem: (id: string) => req<Problem>('GET', `/api/problems/${id}`),

  algorithms: () => req<Algorithm[]>('GET', '/api/algorithms'),
  problemAlgorithms: (problemId: string) => req<Algorithm[]>('GET', `/api/problems/${problemId}/algorithms`),
  algorithm: (id: string) => req<Algorithm>('GET', `/api/algorithms/${id}`),
  createAlgorithm: (problemId: string, body: AlgorithmInput) =>
    req<Algorithm>('POST', `/api/problems/${problemId}/algorithms`, body),
  updateAlgorithm: (id: string, body: Partial<AlgorithmInput>) => req<Algorithm>('PUT', `/api/algorithms/${id}`, body),
  duplicateAlgorithm: (id: string) => req<Algorithm>('POST', `/api/algorithms/${id}/duplicate`),
  deleteAlgorithm: (id: string) => req<void>('DELETE', `/api/algorithms/${id}`),

  generators: () => req<InputGenerator[]>('GET', '/api/generators'),
  problemGenerators: (problemId: string) => req<InputGenerator[]>('GET', `/api/problems/${problemId}/generators`),
  generator: (id: string) => req<InputGenerator>('GET', `/api/generators/${id}`),
  updateGenerator: (id: string, body: Partial<GeneratorInput>) =>
    req<InputGenerator>('PUT', `/api/generators/${id}`, body),
  duplicateGenerator: (id: string) => req<InputGenerator>('POST', `/api/generators/${id}/duplicate`),
  deleteGenerator: (id: string) => req<void>('DELETE', `/api/generators/${id}`),
  preview: (id: string, n: number, params: Record<string, Scalar>, seed?: number) =>
    req<GeneratorPreview>('POST', `/api/generators/${id}/preview`, { n, params, seed }),
  previewCode: (code: string, n: number, params: Record<string, Scalar>, seed?: number) =>
    req<GeneratorPreview>('POST', '/api/generators/preview-code', { code, n, params, seed }),

  experiments: () => req<Experiment[]>('GET', '/api/experiments'),
  experiment: (id: string) => req<Experiment>('GET', `/api/experiments/${id}`),
  createExperiment: (body: ExperimentInput) => req<Experiment>('POST', '/api/experiments', body),
  deleteExperiment: (id: string) => req<void>('DELETE', `/api/experiments/${id}`),
  start: (id: string) => req<ExperimentProgress>('POST', `/api/experiments/${id}/start`),
  step: (id: string) => req<ExperimentProgress>('POST', `/api/experiments/${id}/step`),
  cancel: (id: string) => req<Experiment>('POST', `/api/experiments/${id}/cancel`),
  results: (id: string) => req<ExperimentResults>('GET', `/api/experiments/${id}/results`),
  exportUrl: (id: string, format: 'csv' | 'json') => `${BASE}/api/experiments/${id}/export?format=${format}`,

  visualize: (body: { algorithm_id?: string; code?: string; problem_id?: string; input: unknown; max_steps?: number }) =>
    req<VisualizationTrace>('POST', '/api/visualize', body),
  validate: (code: string, kind: 'algorithm' | 'generator' | 'checker') =>
    req<ValidateResult>('POST', '/api/code/validate', { code, kind }),
}

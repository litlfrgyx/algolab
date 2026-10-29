// ============================================================================
//  Doménový model — entity systému (zdieľané medzi frontendom a backendom).
//
//  Konvencia drôtového formátu (wire format): VŠETKY polia sú snake_case,
//  rovnako ako Pydantic modely v backend/app/schemas.py. Vďaka tomu nie je
//  potrebná žiadna transformačná vrstva medzi FastAPI a TypeScriptom.
//
//  Časové údaje sú ISO 8601 reťazce (napr. "2027-05-10T11:16:00Z").
// ============================================================================

/** Kategórie problémov — zodpovedajú kapitole 3.1.3 práce a tabuľke v návrhu. */
export type ProblemCategory =
  | 'sorting' // triediace
  | 'searching' // vyhľadávacie
  | 'divide_and_conquer' // rozdeľuj a panuj
  | 'string' // reťazce
  | 'dynamic_programming' // dynamické programovanie
  | 'matrix' // matice / numerické
  | 'backtracking' // backtracking
  | 'greedy' // greedy
  | 'graph' // grafové (zatiaľ len benchmark, bez vizualizácie)
  | 'recursive' // rekurzívne (zatiaľ len benchmark, bez vizualizácie)

export interface Problem {
  id: string
  name: string
  description: string
  category: ProblemCategory
  /** Popis formátu vstupu (čo dostane solve(data)). */
  input_description: string
  /** Popis formátu výstupu (čo solve(data) vracia). */
  output_description: string
  /** Algoritmus označený ako referenčný pre kontrolu korektnosti (is_correct). */
  reference_algorithm_id: string | null
  created_at: string
  updated_at: string
}

export interface Algorithm {
  id: string
  problem_id: string
  name: string
  /** Python kód, kontrakt: def solve(data) alebo def solve(data, tracker). */
  code: string
  language: 'python'
  /** Či je toto referenčný algoritmus problému (porovnáva sa proti nemu výstup). */
  is_reference: boolean
  /** Odvodené: či kód volá `tracker` → dá sa krok-za-krokom vizualizovať. */
  supports_visualization: boolean
  created_at: string
  updated_at: string
}

/** Deklarácia jedného parametra generátora (pre formulár v UI). */
export interface GeneratorParamSpec {
  name: string
  label: string
  type: 'enum' | 'number' | 'boolean'
  /** Hodnoty pre type === 'enum' (napr. ['random','sorted','reverse']). */
  options?: string[]
  default: string | number | boolean
}

export interface InputGenerator {
  id: string
  problem_id: string
  name: string
  /** Python kód, kontrakt: def generate(n, **params) -> data. */
  code: string
  /** Predvolené veľkosti ponúkané v UI, napr. [10, 100, 1000, 10000]. */
  default_sizes: number[]
  /** Parametre, ktoré generátor prijíma (mode, ...) — riadi formulár. */
  param_spec: GeneratorParamSpec[]
  created_at: string
  updated_at: string
}

export type ExperimentStatus =
  | 'pending'
  | 'running'
  | 'done'
  | 'failed'
  | 'cancelled'

export interface Experiment {
  id: string
  name: string
  problem_id: string
  /** Algoritmy zaradené do porovnania. */
  algorithm_ids: string[]
  generator_id: string
  /** Veľkosti vstupu, na ktorých sa meria (os X grafov). */
  sizes: number[]
  /** Počet opakovaní na (algoritmus, veľkosť) — pre spoľahlivosť priemeru. */
  repeats: number
  timeout_ms: number
  /** Reprodukovateľnosť: pevný seed generátora (null = náhodný). */
  seed: number | null
  /** Parametre generátora pre všetky behy (napr. { mode: 'random' }). */
  generator_params: Record<string, string | number | boolean>
  status: ExperimentStatus
  created_at: string
  started_at: string | null
  finished_at: string | null
}

export type RunStatus = 'ok' | 'error' | 'timeout'

/** Jeden riadok = jeden beh (algoritmus × veľkosť × opakovanie). */
export interface ExperimentRun {
  id: string
  experiment_id: string
  algorithm_id: string
  input_size: number
  repeat_index: number
  /** Nameraný čas (null pri chybe/timeoute). */
  execution_time_ms: number | null
  /** Nameraná pamäť cez tracemalloc (null pri chybe/timeoute). */
  memory_kb: number | null
  /**
   * Hardvérovo nezávislá metrika (kapitola 2.1.4): počty operácií podľa typu,
   * napr. { compare: 28, swap: 16 }. Odvodené z počtu eventov trackera —
   * tým sa meranie a vizualizér napájajú na ten istý zdroj dát.
   */
  operation_counts: Record<string, number>
  /** Zhoda výstupu s referenčným algoritmom (null = bez referencie). */
  is_correct: boolean | null
  status: RunStatus
  error_message: string | null
  created_at: string
}

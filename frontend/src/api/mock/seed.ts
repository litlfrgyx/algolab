// ============================================================================
//  Seedované dáta pre MockApiClient (offline/demo režim, VITE_USE_MOCK=true).
//
//  Zrkadlí backend seed (rovnaké id). Experimenty sú „pending" — beh syntetizuje
//  MockApiClient.runExperiment cez synthRunsFor (rovnaká UX ako reálny backend).
//
//  Syntetické merania sú interne konzistentné a ZOHĽADŇUJÚ ROZLOŽENIE VSTUPU
//  (best/avg/worst case, kap. 2.1.4): insertion na zotriedenom vstupe je O(n),
//  quick na zotriedenom/inverznom degraduje na O(n²).
// ============================================================================

import type {
  Algorithm,
  Experiment,
  ExperimentRun,
  InputGenerator,
  Problem,
} from '../../types'
import { mulberry32 } from './generators'

const T0 = '2027-05-01T09:00:00.000Z'
const T1 = '2027-05-10T11:16:00.000Z'

// --- Python kód algoritmov (kontrakt def solve(data, tracker)) ---
const CODE_BUBBLE = `def solve(data, tracker):
    n = len(data)
    for i in range(n):
        for j in range(n - i - 1):
            tracker.compare(j, j + 1)
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                tracker.swap(j, j + 1)
        tracker.mark_sorted([n - i - 1])
    return data`

const CODE_QUICK = `def solve(data, tracker):
    def partition(lo, hi):
        tracker.pivot(hi)
        pivot = data[hi]
        i = lo - 1
        for j in range(lo, hi):
            tracker.compare(j, hi)
            if data[j] <= pivot:
                i += 1
                if i != j:
                    data[i], data[j] = data[j], data[i]
                    tracker.swap(i, j)
        data[i + 1], data[hi] = data[hi], data[i + 1]
        tracker.swap(i + 1, hi)
        return i + 1

    def qs(lo, hi):
        if lo < hi:
            p = partition(lo, hi)
            tracker.mark_sorted([p])
            qs(lo, p - 1)
            qs(p + 1, hi)

    qs(0, len(data) - 1)
    return data`

const CODE_INSERTION = `def solve(data, tracker):
    for i in range(1, len(data)):
        j = i
        while j > 0:
            tracker.compare(j - 1, j)
            if data[j - 1] > data[j]:
                data[j - 1], data[j] = data[j], data[j - 1]
                tracker.swap(j - 1, j)
                j -= 1
            else:
                break
    return data`

const CODE_GENERATOR = `def generate(n, mode="random", seed=42):
    import random
    rng = random.Random(seed)
    if mode == "sorted":
        return list(range(n))
    if mode in ("reverse", "worst_case"):
        return list(range(n, 0, -1))
    return [rng.randint(-1000, 1000) for _ in range(n)]`

export function seedProblems(): Problem[] {
  return [
    {
      id: 'prob_sorting',
      name: 'Comparison Sort Benchmark',
      description: 'Porovnanie triediacich algoritmov na rôznych vstupoch.',
      category: 'sorting',
      input_description: 'list[int] — pole celých čísel',
      output_description: 'list[int] — neklesajúco zotriedené pole',
      reference_algorithm_id: 'alg_bubble',
      created_at: T0,
      updated_at: T1,
    },
    {
      id: 'prob_search',
      name: 'Vyhľadávanie v poli',
      description: 'Lineárne vs. binárne vyhľadávanie hodnoty v poli.',
      category: 'searching',
      input_description: 'tuple(list[int], int) — pole a hľadaná hodnota',
      output_description: 'int — index hodnoty alebo -1',
      reference_algorithm_id: null,
      created_at: T0,
      updated_at: T0,
    },
    {
      id: 'prob_lcs',
      name: 'Longest Common Subsequence',
      description: 'Najdlhšia spoločná podpostupnosť dvoch reťazcov (renderer grid).',
      category: 'dynamic_programming',
      input_description: 'tuple(str, str) — dva reťazce',
      output_description: 'int — dĺžka LCS',
      reference_algorithm_id: null,
      created_at: T0,
      updated_at: T0,
    },
  ]
}

export function seedAlgorithms(): Algorithm[] {
  const base = {
    problem_id: 'prob_sorting',
    language: 'python' as const,
    supports_visualization: true,
    created_at: T0,
    updated_at: T1,
  }
  return [
    { ...base, id: 'alg_bubble', name: 'Bubble Sort', code: CODE_BUBBLE, is_reference: true },
    { ...base, id: 'alg_quick', name: 'Quick Sort', code: CODE_QUICK, is_reference: false },
    { ...base, id: 'alg_insertion', name: 'Insertion Sort', code: CODE_INSERTION, is_reference: false },
  ]
}

export function seedGenerators(): InputGenerator[] {
  return [
    {
      id: 'gen_array',
      problem_id: 'prob_sorting',
      name: 'Pole celých čísel',
      code: CODE_GENERATOR,
      default_sizes: [10, 100, 500, 1000, 2000],
      param_spec: [
        {
          name: 'mode',
          label: 'Rozloženie',
          type: 'enum',
          options: ['random', 'sorted', 'reverse', 'worst_case'],
          default: 'random',
        },
      ],
      created_at: T0,
      updated_at: T0,
    },
  ]
}

export function seedExperiments(): Experiment[] {
  const base = {
    problem_id: 'prob_sorting',
    generator_id: 'gen_array',
    repeats: 3,
    timeout_ms: 30000,
    seed: 42,
    status: 'pending' as const,
    created_at: T1,
    started_at: null,
    finished_at: null,
  }
  return [
    { ...base, id: 'exp_sort', name: 'Bubble vs Quick — náhodný vstup', algorithm_ids: ['alg_bubble', 'alg_quick'], sizes: [100, 500, 1000, 2000], generator_params: { mode: 'random' } },
    { ...base, id: 'exp_threeway', name: 'Tri algoritmy — náhodný vstup', algorithm_ids: ['alg_bubble', 'alg_insertion', 'alg_quick'], sizes: [100, 300, 600, 1000], generator_params: { mode: 'random' } },
    { ...base, id: 'exp_worstcase', name: 'Najhorší prípad — inverzný vstup', algorithm_ids: ['alg_bubble', 'alg_insertion', 'alg_quick'], sizes: [50, 150, 300, 500], generator_params: { mode: 'reverse' } },
    { ...base, id: 'exp_bestcase', name: 'Najlepší prípad — zotriedený vstup', algorithm_ids: ['alg_insertion', 'alg_quick'], sizes: [100, 300, 500], generator_params: { mode: 'sorted' } },
  ]
}

// --- Syntetické merania (čas ∝ počet operácií; zohľadňuje rozloženie vstupu) ---
function synthMetrics(algId: string, n: number, mode: string) {
  const log2n = Math.log2(Math.max(2, n))
  const worst = mode === 'reverse' || mode === 'worst_case'
  const best = mode === 'sorted'
  let compares: number
  let swaps: number
  let memoryKb: number

  if (algId === 'alg_bubble') {
    compares = (n * (n - 1)) / 2
    swaps = best ? 0 : worst ? (n * (n - 1)) / 2 : (n * n) / 4
    memoryKb = 40 + n * 0.045
  } else if (algId === 'alg_insertion') {
    if (best) {
      compares = n - 1 // O(n) — najlepší prípad
      swaps = 0
    } else if (worst) {
      compares = (n * (n - 1)) / 2
      swaps = (n * (n - 1)) / 2
    } else {
      compares = (n * n) / 4
      swaps = (n * n) / 4
    }
    memoryKb = 40 + n * 0.02
  } else {
    // quick: na zotriedenom/inverznom vstupe degraduje na O(n²)
    if (best || worst) {
      compares = (n * (n - 1)) / 2
      swaps = n / 2
      memoryKb = 40 + n * 0.05 // hlboká rekurzia
    } else {
      compares = 1.39 * n * log2n
      swaps = 0.5 * compares
      memoryKb = 40 + log2n * 2.5
    }
  }
  const timeMs = compares * 0.00018
  return { compares: Math.round(compares), swaps: Math.round(swaps), timeMs, memoryKb }
}

/** Vygeneruje syntetické behy pre experiment (volá MockApiClient.runExperiment). */
export function synthRunsFor(exp: Experiment): ExperimentRun[] {
  const runs: ExperimentRun[] = []
  const rng = mulberry32(exp.seed ?? 1)
  const mode = String(exp.generator_params?.mode ?? 'random')
  let counter = 0
  for (const algId of exp.algorithm_ids) {
    for (const size of exp.sizes) {
      for (let r = 0; r < exp.repeats; r++) {
        const m = synthMetrics(algId, size, mode)
        const jitter = 1 + (rng() - 0.5) * 0.1
        runs.push({
          id: `run_${exp.id}_${++counter}`,
          experiment_id: exp.id,
          algorithm_id: algId,
          input_size: size,
          repeat_index: r,
          execution_time_ms: +(m.timeMs * jitter).toFixed(3),
          memory_kb: +m.memoryKb.toFixed(1),
          operation_counts: { compare: m.compares, swap: m.swaps },
          is_correct: true,
          status: 'ok',
          error_message: null,
          created_at: new Date().toISOString(),
        })
      }
    }
  }
  return runs
}

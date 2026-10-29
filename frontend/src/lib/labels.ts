import type { ComplexityClass, Paradigm, ProblemCategory } from '../types'

export const CATEGORY: Record<ProblemCategory, string> = {
  sorting: 'Triedenie',
  searching: 'Vyhľadávanie',
  divide_and_conquer: 'Divide and conquer',
  string: 'Reťazce',
  dynamic_programming: 'Dynamic programming',
  matrix: 'Matice',
  backtracking: 'Backtracking',
  greedy: 'Greedy',
  graph: 'Grafy',
  recursive: 'Rekurzia',
  data_structures: 'Údajové štruktúry',
  set: 'Množiny',
  traversal: 'Prehľadávanie stromu',
  numeric: 'Číselné úlohy',
}

/** Prístupy sa uvádzajú anglickými odbornými názvami. */
export const PARADIGM: Record<Paradigm, string> = {
  iterative: 'iterative',
  recursive: 'recursive',
  divide_and_conquer: 'divide and conquer',
  dynamic_programming: 'dynamic programming',
  greedy: 'greedy',
  brute_force: 'brute force',
  backtracking: 'backtracking',
  data_structure: 'data structure',
}

export const PROPERTY: Record<string, string> = {
  stable: 'stable',
  in_place: 'in-place',
  adaptive: 'adaptive',
  recursive: 'recursive',
  randomized: 'randomized',
  non_comparison: 'non-comparison',
  hashing: 'hashing',
  intentionally_incorrect: 'zámerne nesprávny',
}

export const propertyLabel = (p: string) => PROPERTY[p] ?? p

/** Poradie tried od najrýchlejšej. Použité v rebríku zložitosti a pri filtrovaní. */
export const LADDER: ComplexityClass[] = [
  'O(1)', 'O(log log n)', 'O(log n)', 'O(sqrt n)', 'O(n)', 'O(n log n)', 'O(n^2)', 'O(n^3)',
  'O(phi^n)', 'O(2^n)', 'O(3^n)', 'O(n!)',
]

/** Zápis zložitosti pre človeka: O(n^2) → O(n²). */
export function prettyO(c: string | null | undefined): string {
  if (!c) return '–'
  if (c === 'other') return 'iná'
  return c
    .replace('sqrt n', '√n')
    .replace('phi^n', 'φⁿ')
    .replace('^2', '²')
    .replace('^3', '³')
    .replace('2^n', '2ⁿ')
    .replace('3^n', '3ⁿ')
}

export const CASE_LABEL = { best: 'najlepší prípad', avg: 'priemerný prípad', worst: 'najhorší prípad' } as const

export const CONFIDENCE_LABEL = { high: 'vysoká', medium: 'stredná', low: 'nízka', none: '–' } as const

/** Témy katalógu. Úloha patrí do témy podľa svojej kategórie. */
export const TOPICS: { id: string; title: string; match: (category: string) => boolean }[] = [
  { id: 'zaklady', title: 'Základy a rekurzia', match: (c) => ['divide_and_conquer', 'numeric', 'recursive'].includes(c) },
  { id: 'dp', title: 'Dynamic programming', match: (c) => c === 'dynamic_programming' },
  { id: 'struktury', title: 'Zoznam, zásobník, front a halda', match: (c) => c === 'data_structures' },
  { id: 'stromy', title: 'Prehľadávanie stromu', match: (c) => c === 'traversal' },
  { id: 'triedenie', title: 'Triedenie', match: (c) => c === 'sorting' },
  { id: 'vyhladavanie', title: 'Vyhľadávanie', match: (c) => c === 'searching' },
  { id: 'grafy', title: 'Grafy', match: (c) => c === 'graph' || c === 'greedy' },
  { id: 'mnoziny', title: 'Množiny a hašovanie', match: (c) => c === 'set' },
  { id: 'retazce', title: 'Reťazce a text', match: (c) => c === 'string' },
  { id: 'vlastne', title: 'Ďalšie úlohy', match: () => true },
]

export const TOPIC_ORDER = TOPICS.map((t) => t.id)

export function topicOf(category: string): string {
  return (TOPICS.find((t) => t.match(category)) ?? TOPICS[TOPICS.length - 1]).id
}

export function formatNumber(x: number | null | undefined, digits = 0): string {
  if (x === null || x === undefined || Number.isNaN(x)) return '–'
  return x.toLocaleString('sk-SK', { maximumFractionDigits: digits, minimumFractionDigits: digits })
}

export function formatMs(x: number | null | undefined): string {
  if (x === null || x === undefined) return '–'
  if (x < 1) return `${formatNumber(x, 3)} ms`
  if (x < 100) return `${formatNumber(x, 2)} ms`
  return `${formatNumber(x, 0)} ms`
}

export function compact(x: number): string {
  const abs = Math.abs(x)
  if (abs >= 1e9) return `${formatNumber(x / 1e9, 1)} mld`
  if (abs >= 1e6) return `${formatNumber(x / 1e6, 1)} mil`
  if (abs >= 1e3) return `${formatNumber(x / 1e3, 1)} tis`
  return formatNumber(x, abs < 10 && abs % 1 ? 2 : 0)
}

export function opsLabel(key: string): string {
  const m: Record<string, string> = {
    total: 'spolu', compare: 'porovnania', swap: 'výmeny', set: 'zápisy', visit: 'návštevy',
    edge: 'hrany', relax: 'uvoľnenia', cell: 'bunky tabuľky', call: 'volania', probe: 'skúšania',
    hash: 'hašovania', pivot: 'pivoty', multiply: 'násobenia', add: 'sčítania', rotation: 'rotácie',
    split: 'rozdelenia uzlov', merge: 'zlúčenia uzlov', borrow: 'požičania kľúča', digit: 'cifry',
    enqueue: 'vloženia do frontu', char: 'znaky', scan: 'prechody poľom', matrix_read: 'čítania matice',
    pop: 'výbery z haldy', find: 'hľadania koreňa', take: 'odobratia mince', prefix: 'kroky prefixovej tabuľky',
    rehash: 'zväčšenia tabuľky', return: 'návraty',
  }
  return m[key] ?? key
}

import type { ComplexityClass, Paradigm, ProblemCategory } from '../types'

export const CATEGORY: Record<ProblemCategory, string> = {
  sorting: 'Triedenie',
  searching: 'Vyhľadávanie',
  divide_and_conquer: 'Rozdeľuj a panuj',
  string: 'Reťazce',
  dynamic_programming: 'Dynamické programovanie',
  matrix: 'Matice',
  backtracking: 'Backtracking',
  greedy: 'Pažravé algoritmy',
  graph: 'Grafy',
  recursive: 'Rekurzia',
  data_structures: 'Údajové štruktúry',
  set: 'Množiny',
  traversal: 'Prehľadávanie stromu',
  numeric: 'Číselné úlohy',
}

export const PARADIGM: Record<Paradigm, string> = {
  iterative: 'iteratívny',
  recursive: 'rekurzívny',
  divide_and_conquer: 'rozdeľuj a panuj',
  dynamic_programming: 'dynamické programovanie',
  greedy: 'pažravý',
  brute_force: 'hrubá sila',
  backtracking: 'backtracking',
  data_structure: 'údajová štruktúra',
}

export const PROPERTY: Record<string, string> = {
  stable: 'stabilný',
  in_place: 'na mieste',
  adaptive: 'adaptívny',
  recursive: 'rekurzia',
  randomized: 'náhodnosť',
  non_comparison: 'bez porovnávania',
  hashing: 'hašovanie',
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

/** Témy katalógu v poradí predmetu ÚSaA. Úloha patrí do prvej témy, ktorej podmienku spĺňa. */
export const TOPICS: { id: string; title: string; match: (tags: string[], category: string) => boolean }[] = [
  { id: 'mimo', title: 'Nad rámec predmetu', match: (t) => t.includes('mimo-kurzu') },
  { id: 'zaklady', title: 'Základy a rekurzia', match: (_t, c) => ['divide_and_conquer', 'numeric', 'recursive'].includes(c) },
  { id: 'dp', title: 'Dynamické programovanie', match: (_t, c) => c === 'dynamic_programming' },
  { id: 'struktury', title: 'Zoznam, zásobník, front a halda', match: (_t, c) => c === 'data_structures' },
  { id: 'stromy', title: 'Prehľadávanie stromu', match: (_t, c) => c === 'traversal' },
  { id: 'triedenie', title: 'Triedenie', match: (_t, c) => c === 'sorting' },
  { id: 'grafy', title: 'Grafy', match: (_t, c) => c === 'graph' },
  { id: 'mnoziny', title: 'Množiny a hašovanie', match: (_t, c) => c === 'set' },
  { id: 'vlastne', title: 'Ďalšie úlohy', match: () => true },
]

/** Poradie zobrazenia tém (mimo kurzu je prvé v hľadaní, ale posledné na stránke). */
export const TOPIC_ORDER = ['zaklady', 'dp', 'struktury', 'stromy', 'triedenie', 'grafy', 'mnoziny', 'mimo', 'vlastne']

/** Cvičenia predmetu, z ktorých úloha pochádza: ['cv3', 'cv4'] → "cvičenia 3, 4". */
export function weeksLabel(tags: string[]): string | null {
  const weeks = tags.filter((t) => /^cv\d+$/.test(t)).map((t) => t.slice(2))
  if (!weeks.length) return tags.includes('mimo-kurzu') ? 'mimo predmetu' : null
  return weeks.length === 1 ? `cvičenie ${weeks[0]}` : `cvičenia ${weeks.join(', ')}`
}

export function topicOf(tags: string[], category: string): string {
  return (TOPICS.find((t) => t.match(tags, category)) ?? TOPICS[TOPICS.length - 1]).id
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

// ============================================================================
//  Schéma KROKU (Step) a stopy vizualizácie (VisualizationTrace).
//
//  Toto je najdôležitejšia časť kontraktu: produkuje ju `tracker` na backende
//  a konzumujú ju renderery na frontende. Zlá schéma = prerábka na oboch
//  stranách, preto je navrhnutá zámerne malá a explicitná.
//
//  Návrhové rozhodnutia:
//   1. Každý krok nesie PLNÝ snímok stavu (array/grid/value), nie delta.
//      Vizualizácia beží len pre malé n (~≤ 50), takže réžia je zanedbateľná
//      a prehrávanie vpred/vzad na frontende je triviálne (žiadny re-replay).
//   2. Renderer je daný raz na úrovni stopy; jednotlivé kroky majú diskriminant
//      `kind` pre bezpečné zúženie typov v TypeScripte.
//   3. `code_line` umožňuje zvýrazniť aktuálny riadok kódu (ako VisuAlgo /
//      AlgoCompare) — priamo podporuje aktívne zapojenie študenta.
// ============================================================================

import type { ProblemCategory } from './domain'

export type RendererKind = 'array' | 'grid' | 'string'

/**
 * Sémantická rola zvýraznenia → určuje farbu v UI. Zámerne malá množina,
 * spoločná pre všetky renderery.
 */
export type HighlightRole =
  | 'compare' // práve porovnávané prvky
  | 'swap' // práve vymieňané / presúvané prvky
  | 'pivot' // pivot / kľúč
  | 'active' // aktuálny fokus (bunka, znak, prvok)
  | 'match' // zhoda / nájdené
  | 'sorted' // finalizované / na správnom mieste
  | 'range' // aktuálny podinterval / okno (tlmené)
  | 'visited' // už spracované (tlmené)

export interface StepBase {
  /** Poradové číslo kroku v stope (0-based). */
  index: number
  /** Sémantický názov udalosti: 'compare' | 'swap' | 'set' | 'done' | ... */
  type: string
  /** Ľudsky čitateľný popis pre časovú os (timeline). */
  label: string
  /** 1-based riadok zdrojového kódu vykonávaný v tomto kroku (na zvýraznenie). */
  code_line?: number
}

export interface ArrayHighlight {
  index: number
  role: HighlightRole
}
export interface GridHighlight {
  row: number
  col: number
  role: HighlightRole
}
export interface StringHighlight {
  index: number
  role: HighlightRole
}

/** Renderer POLE — sorting, vyhľadávanie, divide & conquer. */
export interface ArrayStep extends StepBase {
  kind: 'array'
  /** Plný snímok poľa v tomto kroku. */
  array: number[]
  highlights: ArrayHighlight[]
  /** Pomenované indexy zobrazené pod stĺpcami: { i, j, lo, hi, mid }. */
  pointers?: Record<string, number>
}

/** Renderer GRID — dynamické programovanie, matice, backtracking. */
export interface GridStep extends StepBase {
  kind: 'grid'
  /** 2D snímok; null = nevyplnená bunka. */
  grid: (number | string | null)[][]
  highlights: GridHighlight[]
  row_labels?: string[]
  col_labels?: string[]
}

/** Renderer REŤAZEC — algoritmy na reťazcoch, vyhľadávanie vzoru. */
export interface StringStep extends StepBase {
  kind: 'string'
  /** Primárny reťazec (napr. text). */
  value: string
  highlights: StringHighlight[]
  /** Voliteľný druhý reťazec pre vyhľadávanie vzoru (text vs pattern). */
  pattern?: string
  pattern_highlights?: StringHighlight[]
  pointers?: Record<string, number>
}

export type Step = ArrayStep | GridStep | StringStep

export interface VisualizationTrace {
  renderer: RendererKind
  /** null ak ide o ad-hoc kód z editora (ešte neuložený algoritmus). */
  algorithm_id: string | null
  algorithm_name: string
  /** Vstup, ktorý túto stopu vyprodukoval. */
  input: unknown
  steps: Step[]
  /**
   * Súhrnné počty podľa typu kroku, napr. { compare: 28, swap: 16 }.
   * Toto je most k meraniu výkonu — rovnaký zdroj ako ExperimentRun.operation_counts.
   */
  operation_counts: Record<string, number>
  /** true ak počet krokov narazil na strop max_steps (stopa je orezaná). */
  truncated: boolean
  max_steps: number
}

/**
 * Predvolený renderer pre kategóriu (kapitola 3.1.3 / tabuľka v návrhu).
 * null = kategória podporuje len benchmark, nie krok-za-krokom vizualizáciu.
 */
export const CATEGORY_RENDERER: Record<ProblemCategory, RendererKind | null> = {
  sorting: 'array',
  searching: 'array',
  divide_and_conquer: 'array',
  string: 'string',
  dynamic_programming: 'grid',
  matrix: 'grid',
  backtracking: 'grid',
  greedy: 'array', // závisí od problému; predvolene pole
  graph: null, // budúce rozšírenie (node-edge diagram)
  recursive: null, // budúce rozšírenie (call stack)
}

/** Rola zvýraznenia → CSS premenná farby (definované v src/index.css). */
export const ROLE_COLOR: Record<HighlightRole, string> = {
  compare: 'var(--secondary)', // cyan
  swap: 'var(--primary)', // amber
  pivot: '#a78bfa', // violet
  active: 'var(--primary)',
  match: 'var(--tertiary)', // green
  sorted: 'var(--tertiary)',
  range: 'var(--outline)',
  visited: 'var(--surface-variant)',
}

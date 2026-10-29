// ============================================================================
//  Mock tracery triediacich algoritmov.
//
//  Toto je JS náhrada backendového executora + trackera: spustí algoritmus
//  a poskladá VisualizationTrace (Step[] + operation_counts) presne podľa
//  kontraktu (steps.ts). Keď príde reálny FastAPI executor, tieto funkcie
//  zmiznú a `api.visualize()` ich nahradí HTTP volaním — tvar dát ostáva.
//
//  Pozn.: `erasableSyntaxOnly` (tsconfig) zakazuje parameter-properties,
//  preto sú polia triedy deklarované explicitne.
// ============================================================================

import type { ArrayHighlight, ArrayStep, VisualizationTrace } from '../../types'

/** Typy krokov, ktoré sa počítajú ako operácie (hardvérovo nezávislá metrika). */
const OPERATION_TYPES = new Set(['compare', 'swap', 'pivot'])

/** Mini-tracker pre renderer `array` — zrkadlí backend/app/tracker.py. */
class ArrayTracker {
  arr: number[]
  steps: ArrayStep[] = []
  counts: Record<string, number> = {}
  truncated = false
  private maxSteps: number

  constructor(arr: number[], maxSteps: number) {
    this.arr = arr
    this.maxSteps = maxSteps
  }

  private record(
    type: string,
    label: string,
    highlights: ArrayHighlight[],
    codeLine?: number,
    pointers?: Record<string, number>,
  ) {
    if (OPERATION_TYPES.has(type))
      this.counts[type] = (this.counts[type] ?? 0) + 1
    if (this.steps.length >= this.maxSteps) {
      this.truncated = true
      return
    }
    this.steps.push({
      kind: 'array',
      index: this.steps.length,
      type,
      label,
      code_line: codeLine,
      array: [...this.arr],
      highlights,
      pointers,
    })
  }

  compare(i: number, j: number, line?: number) {
    this.record(
      'compare',
      `compare [${i}] (${this.arr[i]}) vs [${j}] (${this.arr[j]})`,
      [
        { index: i, role: 'compare' },
        { index: j, role: 'compare' },
      ],
      line,
      { i, j },
    )
  }

  swap(i: number, j: number, line?: number) {
    ;[this.arr[i], this.arr[j]] = [this.arr[j], this.arr[i]]
    this.record(
      'swap',
      `swap [${i}] ↔ [${j}]`,
      [
        { index: i, role: 'swap' },
        { index: j, role: 'swap' },
      ],
      line,
      { i, j },
    )
  }

  pivot(i: number, line?: number) {
    this.record('pivot', `pivot = ${this.arr[i]} (index ${i})`, [
      { index: i, role: 'pivot' },
    ], line)
  }

  markSorted(indices: number[]) {
    this.record(
      'sorted',
      `[${indices.join(', ')}] na mieste`,
      indices.map((index) => ({ index, role: 'sorted' as const })),
    )
  }

  done() {
    this.record(
      'done',
      'zotriedené ✓',
      this.arr.map((_, index) => ({ index, role: 'sorted' as const })),
    )
  }

  finish(
    name: string,
    id: string | null,
    input: number[],
  ): VisualizationTrace {
    return {
      renderer: 'array',
      algorithm_id: id,
      algorithm_name: name,
      input,
      steps: this.steps,
      operation_counts: this.counts,
      truncated: this.truncated,
      max_steps: this.maxSteps,
    }
  }
}

export function traceBubble(input: number[], maxSteps: number): VisualizationTrace {
  const t = new ArrayTracker([...input], maxSteps)
  const a = t.arr
  const n = a.length
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      t.compare(j, j + 1, 4)
      if (a[j] > a[j + 1]) t.swap(j, j + 1, 6)
    }
    if (n - i - 1 >= 0) t.markSorted([n - i - 1])
  }
  t.done()
  return t.finish('Bubble Sort', 'alg_bubble', input)
}

export function traceQuick(input: number[], maxSteps: number): VisualizationTrace {
  const t = new ArrayTracker([...input], maxSteps)
  const a = t.arr

  function partition(lo: number, hi: number): number {
    t.pivot(hi, 2)
    const pivotVal = a[hi]
    let i = lo - 1
    for (let j = lo; j < hi; j++) {
      t.compare(j, hi, 4)
      if (a[j] <= pivotVal) {
        i++
        if (i !== j) t.swap(i, j, 5)
      }
    }
    if (i + 1 !== hi) t.swap(i + 1, hi, 7)
    return i + 1
  }

  function quicksort(lo: number, hi: number) {
    if (lo < hi) {
      const p = partition(lo, hi)
      t.markSorted([p])
      quicksort(lo, p - 1)
      quicksort(p + 1, hi)
    }
  }

  quicksort(0, a.length - 1)
  t.done()
  return t.finish('Quick Sort', 'alg_quick', input)
}

export function traceInsertion(
  input: number[],
  maxSteps: number,
): VisualizationTrace {
  const t = new ArrayTracker([...input], maxSteps)
  const a = t.arr
  for (let i = 1; i < a.length; i++) {
    let j = i
    while (j > 0) {
      t.compare(j - 1, j, 4)
      if (a[j - 1] > a[j]) {
        t.swap(j - 1, j, 5)
        j--
      } else {
        break
      }
    }
  }
  t.done()
  return t.finish('Insertion Sort', 'alg_insertion', input)
}

/** Mapovanie id seedovaného algoritmu → tracer. */
export const SORT_TRACERS: Record<
  string,
  (input: number[], maxSteps: number) => VisualizationTrace
> = {
  alg_bubble: traceBubble,
  alg_quick: traceQuick,
  alg_insertion: traceInsertion,
}

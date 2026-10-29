// ============================================================================
//  Mock generátor vstupov + seedovaný RNG.
//
//  JS náhrada za backendové spustenie `generate(n, **params)`. Seed zaisťuje
//  reprodukovateľnosť (rovnaký seed → rovnaký vstup), čo je opakovaná téma práce.
// ============================================================================

/** Deterministický PRNG (mulberry32) — rovnaký seed dáva rovnakú postupnosť. */
export function mulberry32(seed: number): () => number {
  let s = seed >>> 0
  return () => {
    s |= 0
    s = (s + 0x6d2b79f5) | 0
    let t = Math.imul(s ^ (s >>> 15), 1 | s)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export type GeneratorMode = 'random' | 'sorted' | 'reverse' | 'worst_case'

/** Vygeneruje pole celých čísel podľa módu (zodpovedá DEFAULT_CODE generátora). */
export function generateArray(
  n: number,
  mode: GeneratorMode = 'random',
  seed = 42,
): number[] {
  switch (mode) {
    case 'sorted':
      return Array.from({ length: n }, (_, i) => i)
    case 'reverse':
    case 'worst_case':
      return Array.from({ length: n }, (_, i) => n - i)
    default: {
      const rng = mulberry32(seed)
      return Array.from({ length: n }, () => Math.floor(rng() * 2001) - 1000)
    }
  }
}

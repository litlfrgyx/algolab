import type { Role } from '../../types'

/** Farba a popis každej roly. Rovnaké vo všetkých zobrazeniach, aby sa študent učil jeden jazyk. */
export const ROLE: Record<string, { fill: string; soft: string; label: string }> = {
  compare: { fill: 'var(--role-compare)', soft: 'var(--role-compare-soft)', label: 'porovnanie' },
  swap: { fill: 'var(--role-swap)', soft: 'var(--role-swap-soft)', label: 'výmena alebo zápis' },
  pivot: { fill: 'var(--role-pivot)', soft: 'var(--role-pivot-soft)', label: 'pivot' },
  active: { fill: 'var(--role-active)', soft: 'var(--role-active-soft)', label: 'práve spracúvaný' },
  match: { fill: 'var(--role-done)', soft: 'var(--role-done-soft)', label: 'zhoda' },
  sorted: { fill: 'var(--role-done)', soft: 'var(--role-done-soft)', label: 'hotové' },
  visited: { fill: 'var(--role-visited)', soft: 'var(--role-visited-soft)', label: 'navštívené' },
  tree: { fill: 'var(--role-done)', soft: 'var(--role-done-soft)', label: 'vybraná hrana' },
  path: { fill: 'var(--role-active)', soft: 'var(--role-active-soft)', label: 'cesta' },
}

export const roleOf = (r: Role | string | undefined) => (r ? ROLE[r] : undefined)

/** Legenda pre každý druh zobrazenia: len roly, ktoré sa v ňom naozaj objavia. */
export const LEGEND: Record<string, string[]> = {
  array: ['compare', 'swap', 'pivot', 'active', 'sorted'],
  grid: ['active', 'compare', 'match'],
  graph: ['active', 'visited', 'compare', 'tree'],
  tree: ['active', 'compare', 'visited', 'pivot'],
  string: ['match', 'swap', 'sorted'],
}

/** Krátke zobrazenie hodnoty v bunke: veľké čísla skráti. */
export function cellText(v: unknown): string {
  if (v === null || v === undefined) return ''
  if (typeof v === 'number') {
    if (!Number.isFinite(v)) return '∞'
    const s = String(v)
    if (s.length > 6) return v.toExponential(1).replace('e+', 'e')
    return s
  }
  const s = String(v)
  return s.length > 7 ? s.slice(0, 6) + '…' : s
}

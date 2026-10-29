import { prettyO } from '../lib/labels'
import { cx } from './ui'

/**
 * Rebrík zložitosti: triedy od O(1) po exponenciálne ako schody rastúcej výšky.
 * Rozsah najlepší až najhorší prípad je podfarbený, deklarovaná trieda má rámik,
 * odhad z merania je plný schod. Zhoda je tak vidieť bez čítania textu.
 */

const STEPS = [
  { key: 'O(1)', label: '1' },
  { key: 'O(log n)', label: 'log n' },
  { key: 'O(n)', label: 'n' },
  { key: 'O(n log n)', label: 'n log n' },
  { key: 'O(n^2)', label: 'n²' },
  { key: 'O(n^3)', label: 'n³' },
  { key: 'exp', label: 'cⁿ' },
]

function stepIndex(c: string | null | undefined): number {
  if (!c || c === 'other') return -1
  switch (c) {
    case 'O(1)': return 0
    case 'O(log log n)':
    case 'O(log n)': return 1
    case 'O(sqrt n)':
    case 'O(n)': return 2
    case 'O(n log n)': return 3
    case 'O(n^2)': return 4
    case 'O(n^3)': return 5
    case 'O(phi^n)':
    case 'O(2^n)':
    case 'O(3^n)':
    case 'O(n!)': return 6
    default: return -1
  }
}

interface Props {
  best?: string | null
  avg?: string | null
  worst?: string | null
  /** trieda, ku ktorej sa porovnáva odhad (deklarovaná pre zvolený prípad) */
  declared?: string | null
  measured?: string | null
  size?: 'sm' | 'md'
  showLabels?: boolean
}

export function ComplexityLadder({ best, avg, worst, declared, measured, size = 'md', showLabels = false }: Props) {
  const lo = stepIndex(best ?? avg)
  const hi = stepIndex(worst ?? avg)
  const d = stepIndex(declared ?? avg)
  const m = stepIndex(measured)
  const unit = size === 'sm' ? 3 : 5
  const width = size === 'sm' ? 9 : 16
  const desc = [
    declared || avg ? `deklarovaná ${prettyO(declared ?? avg)}` : null,
    best && worst && best !== worst ? `rozsah ${prettyO(best)} až ${prettyO(worst)}` : null,
    measured ? `odhad z merania ${prettyO(measured)}` : null,
  ].filter(Boolean).join(', ')

  return (
    <div className="inline-flex flex-col gap-1" role="img" aria-label={`Rebrík zložitosti: ${desc || 'bez údajov'}`}>
      <div className="flex items-end gap-[3px]">
        {STEPS.map((s, i) => {
          const inRange = lo >= 0 && hi >= 0 && i >= Math.min(lo, hi) && i <= Math.max(lo, hi)
          const isDeclared = i === d
          const isMeasured = i === m
          return (
            <div
              key={s.key}
              title={s.label}
              style={{ height: (i + 2) * unit, width }}
              className={cx(
                'rounded-[2px] transition-colors',
                isMeasured ? 'bg-accent' : inRange ? 'bg-accent-soft' : 'bg-surface-3',
                isDeclared && 'outline-2 outline-offset-1 outline-ink',
              )}
            />
          )
        })}
      </div>
      {showLabels && (
        <div className="flex gap-[3px] text-[10px] leading-none text-ink-3">
          {STEPS.map((s) => (
            <span key={s.key} style={{ width }} className="text-center whitespace-nowrap overflow-visible">
              {size === 'md' ? s.label : ''}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

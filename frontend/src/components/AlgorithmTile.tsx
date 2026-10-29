import { Link } from 'react-router-dom'
import { Eye } from 'lucide-react'
import type { Algorithm } from '../types'
import { PARADIGM, prettyO, propertyLabel } from '../lib/labels'
import { ComplexityLadder } from './ComplexityLadder'
import { Tag } from './ui'

/** Dlaždica algoritmu v katalógu: názov, úloha, zložitosť s rebríkom a vlastnosti. */
export function AlgorithmTile({ a, problemName }: { a: Algorithm; problemName?: string }) {
  const worstDiffers = a.complexity_time_worst && a.complexity_time_worst !== a.complexity_time_avg
  const props = a.properties.filter((p) => !(p === 'recursive' && a.paradigm === 'recursive'))
  return (
    <Link
      to={`/algorithms/${a.id}`}
      className="group flex h-full flex-col gap-2.5 rounded-[var(--radius-lg)] border border-line bg-surface p-3.5 transition-colors hover:border-line-strong hover:bg-surface-2/40"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="text-[15px] font-semibold leading-snug text-ink group-hover:text-accent">{a.name}</h3>
          {problemName && <p className="mt-0.5 truncate text-[13px] text-ink-3">{problemName}</p>}
        </div>
        {a.supports_visualization && (
          <span title="Dá sa vizualizovať" className="mt-0.5 text-ink-3">
            <Eye className="size-4" aria-label="dá sa vizualizovať" />
          </span>
        )}
      </div>

      <div className="flex items-end justify-between gap-3">
        <div>
          <p className="text-[17px] font-semibold leading-none num">{prettyO(a.complexity_time_avg)}</p>
          {worstDiffers && <p className="mt-1 text-xs text-ink-3 num">najhorší {prettyO(a.complexity_time_worst)}</p>}
        </div>
        <ComplexityLadder size="sm" best={a.complexity_time_best} avg={a.complexity_time_avg} worst={a.complexity_time_worst} />
      </div>

      <div className="mt-auto flex flex-wrap gap-1.5">
        <Tag>{PARADIGM[a.paradigm]}</Tag>
        {props.slice(0, 3).map((p) => (
          <Tag key={p} tone={p === 'intentionally_incorrect' ? 'warn' : 'neutral'}>{propertyLabel(p)}</Tag>
        ))}
        {props.length > 3 && <Tag>+{props.length - 3}</Tag>}
        {!a.is_builtin && <Tag tone="accent">vlastný</Tag>}
      </div>
    </Link>
  )
}

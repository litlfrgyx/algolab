import { Link } from 'react-router-dom'
import { Eye } from 'lucide-react'
import type { Algorithm } from '../types'
import { PARADIGM, prettyO, propertyLabel } from '../lib/labels'
import { ComplexityLadder } from './ComplexityLadder'
import { Tag } from './ui'

interface Props {
  algorithms: Algorithm[]
  problemNames?: Record<string, string>
  referenceId?: string | null
}

export function AlgorithmTable({ algorithms, problemNames, referenceId }: Props) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-sm">
        <thead>
          <tr className="border-b border-line text-left text-[13px] text-ink-3">
            <th className="px-4 py-2 font-medium">Algoritmus</th>
            {problemNames && <th className="px-3 py-2 font-medium">Úloha</th>}
            <th className="px-3 py-2 font-medium">Čas v priemere</th>
            <th className="px-3 py-2 font-medium"><span className="sr-only">Rebrík zložitosti</span></th>
            <th className="px-4 py-2 font-medium">Vlastnosti</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {algorithms.map((a) => (
            <tr key={a.id} className="hover:bg-surface-2/60">
              <td className="px-4 py-2.5">
                <Link to={`/algorithms/${a.id}`} className="font-medium text-ink hover:text-accent hover:underline">
                  {a.name}
                </Link>
                <p className="text-[13px] text-ink-3">{PARADIGM[a.paradigm]}</p>
                <div className="mt-0.5 flex flex-wrap gap-1.5 empty:hidden">
                  {a.id === referenceId && <Tag tone="accent" title="Jeho výsledok sa používa na kontrolu ostatných">referenčný</Tag>}
                  {!a.is_builtin && <Tag>vlastný</Tag>}
                </div>
              </td>
              {problemNames && (
                <td className="px-3 py-2.5 text-ink-2">
                  <Link to={`/problems/${a.problem_id}`} className="hover:text-accent hover:underline">{problemNames[a.problem_id] ?? a.problem_id}</Link>
                </td>
              )}
              <td className="px-3 py-2.5 whitespace-nowrap">
                <p className="font-medium num">{prettyO(a.complexity_time_avg)}</p>
                {a.complexity_time_worst && a.complexity_time_worst !== a.complexity_time_avg && (
                  <p className="text-[13px] text-ink-3 num">najhorší {prettyO(a.complexity_time_worst)}</p>
                )}
              </td>
              <td className="px-3 py-2.5">
                <ComplexityLadder size="sm" best={a.complexity_time_best} avg={a.complexity_time_avg} worst={a.complexity_time_worst} />
              </td>
              <td className="px-4 py-2.5">
                <div className="flex flex-wrap items-center gap-1.5">
                  {a.supports_visualization && (
                    <span title="Dá sa vizualizovať" className="inline-flex items-center text-ink-3"><Eye className="size-4" aria-label="vizualizácia" /></span>
                  )}
                  {a.properties.map((p) => (
                    <Tag key={p} tone={p === 'intentionally_incorrect' ? 'warn' : 'neutral'}>{propertyLabel(p)}</Tag>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

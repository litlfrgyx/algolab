import type { Step, VisualizationTrace } from '../../types'
import { ArrayView } from './ArrayView'
import { GraphView } from './GraphView'
import { GridView } from './GridView'
import { StringView } from './StringView'
import { TreeView } from './TreeView'
import { LEGEND, ROLE } from './roles'

export function StepView({ step, trace }: { step: Step | undefined; trace: VisualizationTrace }) {
  if (!step) return <p className="py-10 text-center text-sm text-ink-3">Algoritmus nezaznamenal žiadny krok.</p>
  switch (step.kind) {
    case 'array': return <ArrayView step={step} />
    case 'grid': return <GridView step={step} />
    case 'graph': return <GraphView step={step} structure={trace.structure} />
    case 'tree': return <TreeView step={step} />
    case 'string': return <StringView step={step} />
    default: return <p className="py-10 text-center text-sm text-ink-3">Tento krok nemá čo zobraziť.</p>
  }
}

export function RoleLegend({ kind }: { kind: string }) {
  const roles = LEGEND[kind] ?? []
  if (!roles.length) return null
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1.5 text-[13px] text-ink-2" aria-label="Význam farieb">
      {roles.map((r) => (
        <li key={r} className="flex items-center gap-1.5">
          <span className="size-3 rounded-[3px]" style={{ background: ROLE[r].fill }} aria-hidden />
          {ROLE[r].label}
        </li>
      ))}
    </ul>
  )
}

import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { TOPIC_ORDER, topicOf } from '../lib/labels'
import { Button, Empty, LoadError, PageHeader, Panel, Skeleton } from '../components/ui'
import { StatusTag } from '../components/StatusTag'
import type { Experiment, ProblemSummary } from '../types'

function ExperimentRows({ items, problems }: { items: Experiment[]; problems: Record<string, ProblemSummary> }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-sm">
        <thead>
          <tr className="border-b border-line text-left text-[13px] text-ink-3">
            <th className="px-4 py-2 font-medium">Experiment</th>
            <th className="px-3 py-2 font-medium">Úloha</th>
            <th className="px-3 py-2 text-right font-medium">Algoritmy</th>
            <th className="px-3 py-2 text-right font-medium">Prípady</th>
            <th className="px-4 py-2 font-medium">Stav</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {items.map((e) => (
            <tr key={e.id} className="hover:bg-surface-2/60">
              <td className="px-4 py-2.5">
                <Link to={`/experiments/${e.id}`} className="font-medium hover:text-accent hover:underline">{e.name}</Link>
              </td>
              <td className="px-3 py-2.5 text-ink-2">{problems[e.problem_id]?.name ?? e.problem_id}</td>
              <td className="px-3 py-2.5 text-right num">{e.algorithm_ids.length}</td>
              <td className="px-3 py-2.5 text-right text-ink-2 num">
                {Math.max(1, e.variants.length) * e.sizes.length * e.repeats}
              </td>
              <td className="px-4 py-2.5"><StatusTag status={e.status} done={e.done_cases} total={e.total_cases} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Experiments() {
  const state = useAsync(async () => {
    const [experiments, problems] = await Promise.all([api.experiments(), api.problems()])
    return { experiments, problems }
  }, [])

  const { own, builtin, problems } = useMemo(() => {
    const problems = Object.fromEntries((state.data?.problems ?? []).map((p) => [p.id, p]))
    const order = Object.fromEntries((state.data?.problems ?? []).map((p, i) => [p.id, i]))
    const topicRank = (e: Experiment) => {
      const p = problems[e.problem_id]
      return p ? TOPIC_ORDER.indexOf(topicOf(p.tags, p.category)) : 99
    }
    const all = state.data?.experiments ?? []
    const builtin = all.filter((e) => e.is_builtin)
      .sort((a, b) => topicRank(a) - topicRank(b) || (order[a.problem_id] ?? 0) - (order[b.problem_id] ?? 0) || a.created_at.localeCompare(b.created_at))
    const own = all.filter((e) => !e.is_builtin).sort((a, b) => b.created_at.localeCompare(a.created_at))
    return { own, builtin, problems }
  }, [state.data])

  return (
    <>
      <PageHeader
        title="Experimenty"
        lead="Experiment spustí vybrané algoritmy na vstupoch rastúcej veľkosti, zmeria počet operácií a čas a z nameraných dát odhadne triedu zložitosti."
        actions={<Link to="/experiments/new"><Button variant="primary" icon={<Plus className="size-4" aria-hidden />}>Nový experiment</Button></Link>}
      />
      {state.error && <LoadError error={state.error} onRetry={state.reload} />}
      {!state.data && !state.error && <Skeleton className="h-96" />}
      {state.data && (
        <div className="space-y-6">
          <Panel title="Moje experimenty">
            {own.length ? <ExperimentRows items={own} problems={problems} /> : (
              <Empty title="Zatiaľ žiadny vlastný experiment" action={<Link to="/experiments/new"><Button size="sm">Vytvoriť experiment</Button></Link>}>
                Vyber úlohu, algoritmy a veľkosti vstupu. Výsledky ostanú uložené.
              </Empty>
            )}
          </Panel>
          <Panel title="Pripravené experimenty">
            <ExperimentRows items={builtin} problems={problems} />
          </Panel>
        </div>
      )}
    </>
  )
}

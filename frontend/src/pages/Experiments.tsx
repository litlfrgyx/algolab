import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Plus, Search } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { TOPICS, TOPIC_ORDER, formatNumber, topicOf } from '../lib/labels'
import { Button, Empty, Input, LoadError, PageHeader, Skeleton, cx } from '../components/ui'
import { StatusTag } from '../components/StatusTag'
import { seriesColor } from '../components/ResultsChart'
import type { Experiment, ProblemSummary } from '../types'

function normalize(s: string) {
  return s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

function sizesLabel(sizes: number[]) {
  if (!sizes.length) return ''
  const s = [...sizes].sort((a, b) => a - b)
  return s.length === 1 ? `n = ${formatNumber(s[0])}` : `n od ${formatNumber(s[0])} po ${formatNumber(s[s.length - 1])}`
}

/** Dlaždica experimentu. Farby čiarok sú rovnaké ako čiary v grafe výsledkov. */
function ExperimentTile({ e, problem, names }: { e: Experiment; problem?: ProblemSummary; names: Record<string, string> }) {
  const variants = Math.max(1, e.variants.length)
  const action = e.status === 'done' ? 'Pozrieť výsledky' : e.status === 'running' ? 'Pokračovať' : 'Spustiť'
  const href = `/experiments/${e.id}${e.status === 'pending' ? '?start=1' : ''}`
  return (
    <div className="flex h-full flex-col gap-3 rounded-[var(--radius-lg)] border border-line bg-surface p-4">
      <div className="min-w-0">
        <h3 className="text-[15px] font-semibold leading-snug">
          <Link to={`/experiments/${e.id}`} className="hover:text-accent hover:underline">{e.name}</Link>
        </h3>
        {problem && <p className="mt-0.5 text-[13px] text-ink-3">{problem.name}</p>}
      </div>
      <ul className="space-y-1 text-[13px] text-ink-2">
        {e.algorithm_ids.map((aid, i) => (
          <li key={aid} className="flex items-center gap-2">
            <span className="h-[3px] w-3.5 shrink-0 rounded" style={{ background: seriesColor(i) }} aria-hidden />
            <span className="truncate">{names[aid] ?? aid}</span>
          </li>
        ))}
      </ul>
      <p className="mt-auto text-[13px] text-ink-3 num">
        {sizesLabel(e.sizes)}
        {variants > 1 ? `, ${variants} varianty vstupu` : ''}
      </p>
      <div className="flex items-center justify-between gap-3 border-t border-line pt-3">
        <StatusTag status={e.status} done={e.done_cases} total={e.total_cases} />
        <Link to={href} className="inline-flex shrink-0 items-center gap-1 text-[13px] font-medium text-accent hover:underline">
          {action}<ArrowRight className="size-3.5" aria-hidden />
        </Link>
      </div>
    </div>
  )
}

export default function Experiments() {
  const state = useAsync(async () => {
    const [experiments, problems, algorithms] = await Promise.all([api.experiments(), api.problems(), api.algorithms()])
    return { experiments, problems, algorithms }
  }, [])
  const [query, setQuery] = useState('')
  const [topic, setTopic] = useState('')

  const { own, groups, problems, names, topicsUsed } = useMemo(() => {
    const problems = Object.fromEntries((state.data?.problems ?? []).map((p) => [p.id, p]))
    const names = Object.fromEntries((state.data?.algorithms ?? []).map((a) => [a.id, a.name]))
    const order = Object.fromEntries((state.data?.problems ?? []).map((p, i) => [p.id, i]))
    const q = normalize(query.trim())
    const topicFor = (e: Experiment) => (problems[e.problem_id] ? topicOf(problems[e.problem_id].category) : 'vlastne')
    const match = (e: Experiment) =>
      (!q || normalize(`${e.name} ${problems[e.problem_id]?.name ?? ''} ${e.algorithm_ids.map((a) => names[a]).join(' ')}`).includes(q)) &&
      (!topic || topicFor(e) === topic)
    const all = state.data?.experiments ?? []
    const own = all.filter((e) => !e.is_builtin && match(e)).sort((a, b) => b.created_at.localeCompare(a.created_at))
    const builtin = all.filter((e) => e.is_builtin)
    const topicsUsed = TOPIC_ORDER.filter((t) => builtin.some((e) => topicFor(e) === t))
    const by = new Map<string, Experiment[]>()
    for (const e of builtin.filter(match)) by.set(topicFor(e), [...(by.get(topicFor(e)) ?? []), e])
    for (const list of by.values()) {
      list.sort((a, b) => (order[a.problem_id] ?? 0) - (order[b.problem_id] ?? 0) || a.created_at.localeCompare(b.created_at))
    }
    const groups = TOPIC_ORDER.filter((t) => by.has(t)).map((t) => ({ id: t, title: TOPICS.find((x) => x.id === t)!.title, items: by.get(t)! }))
    return { own, groups, problems, names, topicsUsed }
  }, [state.data, query, topic])

  const grid = 'grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'

  return (
    <>
      <PageHeader
        title="Experimenty"
        lead="Experiment spustí vybrané algoritmy na vstupoch rastúcej veľkosti, zmeria počet operácií a čas a z nameraných dát odhadne triedu zložitosti. Pripravené experimenty ukazujú typické rozdiely medzi algoritmami."
        actions={<Link to="/experiments/new"><Button variant="primary" icon={<Plus className="size-4" aria-hidden />}>Nový experiment</Button></Link>}
      />
      {state.error && <LoadError error={state.error} onRetry={state.reload} />}

      <div className="mb-6 flex flex-wrap items-center gap-2">
        <div className="relative w-full max-w-xs">
          <Search className="pointer-events-none absolute left-2.5 top-2.5 size-4 text-ink-3" aria-hidden />
          <Input type="search" aria-label="Hľadať experiment" placeholder="Hľadať, napríklad quicksort" value={query}
            onChange={(e) => setQuery(e.target.value)} className="w-full pl-8" />
        </div>
        <div className="flex flex-wrap gap-2" role="group" aria-label="Téma">
          {[{ id: '', title: 'Všetky témy' }, ...topicsUsed.map((t) => ({ id: t, title: TOPICS.find((x) => x.id === t)!.title }))].map((t) => (
            <button
              key={t.id || 'all'}
              onClick={() => setTopic(t.id)}
              aria-pressed={topic === t.id}
              className={cx('h-8 rounded-full border px-3 text-[13px] cursor-pointer transition-colors',
                topic === t.id ? 'border-accent bg-accent-soft text-accent' : 'border-line-strong text-ink-2 hover:bg-surface-2')}
            >
              {t.title}
            </button>
          ))}
        </div>
      </div>

      {!state.data && !state.error && <div className={grid}>{Array.from({ length: 8 }, (_, i) => <Skeleton key={i} className="h-52" />)}</div>}

      {state.data && (
        <div className="space-y-8">
          <section aria-labelledby="own">
            <h2 id="own" className="mb-3 flex items-baseline gap-2 text-[15px] font-semibold">
              Moje experimenty
              {own.length > 0 && <span className="text-[13px] font-normal text-ink-3 num">{own.length}</span>}
            </h2>
            {own.length ? (
              <ul className={grid}>{own.map((e) => <li key={e.id}><ExperimentTile e={e} problem={problems[e.problem_id]} names={names} /></li>)}</ul>
            ) : (
              <div className="rounded-[var(--radius-lg)] border border-dashed border-line-strong">
                <Empty title="Zatiaľ žiadny vlastný experiment" action={<Link to="/experiments/new"><Button size="sm">Vytvoriť experiment</Button></Link>}>
                  Vyber úlohu, algoritmy a veľkosti vstupu. Výsledky ostanú uložené.
                </Empty>
              </div>
            )}
          </section>

          {groups.map((g) => (
            <section key={g.id} aria-labelledby={`e-${g.id}`}>
              <h2 id={`e-${g.id}`} className="mb-3 flex items-baseline gap-2 text-[15px] font-semibold">
                {g.title}
                <span className="text-[13px] font-normal text-ink-3 num">{g.items.length}</span>
              </h2>
              <ul className={grid}>
                {g.items.map((e) => <li key={e.id}><ExperimentTile e={e} problem={problems[e.problem_id]} names={names} /></li>)}
              </ul>
            </section>
          ))}
          {groups.length === 0 && own.length === 0 && (query || topic) && (
            <p className="text-ink-2">Hľadaniu nezodpovedá žiadny experiment.</p>
          )}
        </div>
      )}
    </>
  )
}

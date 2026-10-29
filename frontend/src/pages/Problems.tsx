import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { BarChart3, EyeOff, Grid3x3, ListTree, Network, Search, Type } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { TOPICS, TOPIC_ORDER, topicOf } from '../lib/labels'
import { Input, LoadError, PageHeader, Skeleton } from '../components/ui'
import type { Algorithm, ProblemSummary } from '../types'

const RENDERER_LABEL: Record<string, string> = {
  array: 'pole', grid: 'tabuľka', graph: 'graf', tree: 'strom', string: 'text', none: 'bez vizualizácie',
}

function normalize(s: string) {
  return s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

const RENDERER_ICON = { array: BarChart3, grid: Grid3x3, graph: Network, tree: ListTree, string: Type, none: EyeOff }

function plural(n: number) {
  return n === 1 ? 'algoritmus' : n < 5 ? 'algoritmy' : 'algoritmov'
}

function ProblemTile({ p, algorithms }: { p: ProblemSummary; algorithms: Algorithm[] }) {
  const Icon = RENDERER_ICON[p.renderer] ?? EyeOff
  const names = algorithms.map((a) => a.name)
  return (
    <Link
      to={`/problems/${p.id}`}
      className="group flex h-full flex-col gap-3 rounded-[var(--radius-lg)] border border-line bg-surface p-4 transition-colors hover:border-line-strong hover:bg-surface-2/40"
    >
      <div className="space-y-1">
        <h3 className="text-[15px] font-semibold leading-snug text-ink group-hover:text-accent">{p.name}</h3>
        <p className="text-[13px] leading-relaxed text-ink-2 line-clamp-2">{p.summary}</p>
      </div>
      {names.length > 0 && (
        <p className="text-[13px] text-ink-3 line-clamp-2">
          {names.slice(0, 3).join(', ')}{names.length > 3 ? ` a ďalšie ${names.length - 3}` : ''}
        </p>
      )}
      <div className="mt-auto flex items-center justify-between gap-3 border-t border-line pt-3 text-[13px] text-ink-2">
        <span className="inline-flex items-center gap-1.5">
          <Icon className="size-4 text-ink-3" strokeWidth={1.75} aria-hidden />
          {p.renderer === 'none' ? 'bez vizualizácie' : RENDERER_LABEL[p.renderer]}
        </span>
        <span className="num">{p.algorithm_count} {plural(p.algorithm_count)}</span>
      </div>
    </Link>
  )
}

export default function Problems() {
  const { data, error, loading, reload } = useAsync(() => api.problems(), [])
  const algs = useAsync(() => api.algorithms(), [])
  const byProblem = useMemo(() => {
    const m = new Map<string, Algorithm[]>()
    for (const a of algs.data ?? []) m.set(a.problem_id, [...(m.get(a.problem_id) ?? []), a])
    for (const list of m.values()) list.sort((x, y) => x.sort_order - y.sort_order)
    return m
  }, [algs.data])
  const [query, setQuery] = useState('')

  const groups = useMemo(() => {
    const q = normalize(query.trim())
    const list = (data ?? []).filter(
      (p) => !q || normalize(`${p.name} ${p.summary} ${p.description}`).includes(q),
    )
    const byTopic = new Map<string, ProblemSummary[]>()
    for (const p of list) {
      const t = topicOf(p.category)
      byTopic.set(t, [...(byTopic.get(t) ?? []), p])
    }
    return TOPIC_ORDER.filter((id) => byTopic.has(id)).map((id) => ({
      id, title: TOPICS.find((t) => t.id === id)!.title, items: byTopic.get(id)!,
    }))
  }, [data, query])

  return (
    <>
      <PageHeader
        title="Úlohy"
        lead="Každá úloha má niekoľko algoritmov, ktoré ju riešia. Pozri sa, ako pracujú krok po kroku, a potom ich porovnaj na väčších vstupoch."
      />
      <ol className="mb-8 grid gap-3 text-sm sm:grid-cols-3">
        {[
          ['Vyber úlohu', 'a prečítaj si, čo je vstupom a čo výstupom.'],
          ['Spusti vizualizáciu', 'jedného alebo dvoch algoritmov na malom vstupe.'],
          ['Porovnaj v experimente', 'počet operácií a čas pri rastúcej veľkosti vstupu.'],
        ].map(([head, rest], i) => (
          <li key={head} className="flex gap-3 rounded-[var(--radius-lg)] bg-surface-2 px-4 py-3">
            <span className="grid size-6 shrink-0 place-items-center rounded-full bg-surface text-[13px] font-semibold text-accent num" aria-hidden>{i + 1}</span>
            <p><span className="font-medium">{head}</span> <span className="text-ink-2">{rest}</span></p>
          </li>
        ))}
      </ol>

      <div className="relative mb-6 max-w-sm">
        <Search className="pointer-events-none absolute left-2.5 top-2.5 size-4 text-ink-3" aria-hidden />
        <Input
          type="search"
          aria-label="Hľadať úlohu"
          placeholder="Hľadať úlohu, napríklad halda"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full pl-8"
        />
      </div>

      {error && <LoadError error={error} onRetry={reload} />}
      {loading && !data && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{Array.from({ length: 6 }, (_, i) => <Skeleton key={i} className="h-44" />)}</div>
      )}
      {data && groups.length === 0 && (
        <p className="text-ink-2">Žiadna úloha nezodpovedá hľadaniu „{query}“.</p>
      )}
      <div className="space-y-8">
        {groups.map((g) => (
          <section key={g.id} aria-labelledby={`t-${g.id}`}>
            <h2 id={`t-${g.id}`} className="mb-3 flex items-baseline gap-2 text-[15px] font-semibold text-ink">
              {g.title}
              <span className="text-[13px] font-normal text-ink-3 num">{g.items.length}</span>
            </h2>
            <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {g.items.map((p) => <li key={p.id}><ProblemTile p={p} algorithms={byProblem.get(p.id) ?? []} /></li>)}
            </ul>
          </section>
        ))}
      </div>
    </>
  )
}

import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight, Search } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { TOPICS, TOPIC_ORDER, topicOf } from '../lib/labels'
import { Input, LoadError, PageHeader, Skeleton } from '../components/ui'
import type { ProblemSummary } from '../types'

const RENDERER_LABEL: Record<string, string> = {
  array: 'pole', grid: 'tabuľka', graph: 'graf', tree: 'strom', string: 'text', none: 'bez vizualizácie',
}

function normalize(s: string) {
  return s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

function ProblemRow({ p }: { p: ProblemSummary }) {
  return (
    <li>
      <Link
        to={`/problems/${p.id}`}
        className="group grid grid-cols-[1fr_auto] items-center gap-4 rounded-[var(--radius)] px-3 py-3 hover:bg-surface-2 sm:grid-cols-[minmax(0,1fr)_250px_auto]"
      >
        <div className="min-w-0">
          <p className="font-medium text-ink group-hover:text-accent">{p.name}</p>
          <p className="text-[13px] text-ink-2 line-clamp-2">{p.summary}</p>
        </div>
        <div className="hidden text-[13px] text-ink-3 sm:block num">
          <p>{p.algorithm_count} {p.algorithm_count === 1 ? 'algoritmus' : p.algorithm_count < 5 ? 'algoritmy' : 'algoritmov'}</p>
          <p>
            {p.renderer === 'none' ? 'bez vizualizácie' : `vizualizácia: ${RENDERER_LABEL[p.renderer]}`}
          </p>
        </div>
        <ChevronRight className="size-4 text-ink-3 group-hover:text-accent" aria-hidden />
      </Link>
    </li>
  )
}

export default function Problems() {
  const { data, error, loading, reload } = useAsync(() => api.problems(), [])
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
        <div className="space-y-3">{Array.from({ length: 6 }, (_, i) => <Skeleton key={i} className="h-14" />)}</div>
      )}
      {data && groups.length === 0 && (
        <p className="text-ink-2">Žiadna úloha nezodpovedá hľadaniu „{query}“.</p>
      )}
      <div className="space-y-8">
        {groups.map((g) => (
          <section key={g.id} aria-labelledby={`t-${g.id}`}>
            <h2 id={`t-${g.id}`} className="mb-1 px-3 text-[15px] font-semibold text-ink">{g.title}</h2>
            <ul className="divide-y divide-line rounded-[var(--radius-lg)] border border-line bg-surface p-1">
              {g.items.map((p) => <ProblemRow key={p.id} p={p} />)}
            </ul>
          </section>
        ))}
      </div>
    </>
  )
}

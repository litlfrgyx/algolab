import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { LADDER, PARADIGM, PROPERTY, TOPICS, TOPIC_ORDER, prettyO, topicOf } from '../lib/labels'
import { AlgorithmTable } from '../components/AlgorithmTable'
import { Button, Empty, Field, Input, LoadError, PageHeader, Panel, Select, Skeleton, cx } from '../components/ui'
import type { Paradigm } from '../types'

function normalize(s: string) {
  return s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

const rank = (c: string | null) => (c ? LADDER.indexOf(c as (typeof LADDER)[number]) : -1)

export default function Algorithms() {
  const [params, setParams] = useSearchParams()
  const state = useAsync(async () => {
    const [algorithms, problems] = await Promise.all([api.algorithms(), api.problems()])
    return { algorithms, problems }
  }, [])

  const q = params.get('q') ?? ''
  const topic = params.get('topic') ?? ''
  const paradigm = params.get('paradigm') ?? ''
  const maxAvg = params.get('max') ?? ''
  const props = (params.get('props') ?? '').split(',').filter(Boolean)
  const vizOnly = params.get('viz') === '1'
  const origin = params.get('origin') ?? ''

  const set = (key: string, value: string) => {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value)
    else next.delete(key)
    setParams(next, { replace: true })
  }
  const toggleProp = (p: string) => {
    const next = props.includes(p) ? props.filter((x) => x !== p) : [...props, p]
    set('props', next.join(','))
  }

  const problemNames = useMemo(
    () => Object.fromEntries((state.data?.problems ?? []).map((p) => [p.id, p.name])),
    [state.data],
  )

  const filtered = useMemo(() => {
    if (!state.data) return []
    const problems = Object.fromEntries(state.data.problems.map((p) => [p.id, p]))
    const nq = normalize(q.trim())
    const order = Object.fromEntries(state.data.problems.map((p, i) => [p.id, i]))
    return state.data.algorithms
      .filter((a) => {
        const p = problems[a.problem_id]
        if (nq && !normalize(`${a.name} ${a.description} ${p?.name ?? ''}`).includes(nq)) return false
        if (topic && (!p || topicOf(p.tags, p.category) !== topic)) return false
        if (paradigm && a.paradigm !== paradigm) return false
        if (maxAvg) {
          const r = rank(a.complexity_time_avg)
          if (r < 0 || r > rank(maxAvg)) return false
        }
        if (props.some((x) => !a.properties.includes(x))) return false
        if (vizOnly && !a.supports_visualization) return false
        if (origin === 'builtin' && !a.is_builtin) return false
        if (origin === 'own' && a.is_builtin) return false
        return true
      })
      .sort((x, y) => (order[x.problem_id] ?? 99) - (order[y.problem_id] ?? 99) || x.sort_order - y.sort_order)
  }, [state.data, q, topic, paradigm, maxAvg, props, vizOnly, origin])

  const active = q || topic || paradigm || maxAvg || props.length || vizOnly || origin
  const usedProps = useMemo(() => {
    const s = new Set<string>()
    state.data?.algorithms.forEach((a) => a.properties.forEach((p) => s.add(p)))
    return Object.keys(PROPERTY).filter((p) => s.has(p))
  }, [state.data])

  return (
    <>
      <PageHeader
        title="Algoritmy"
        lead="Všetky algoritmy zo všetkých úloh. Filtruj podľa témy, prístupu, zložitosti alebo vlastností."
      />
      {state.error && <LoadError error={state.error} onRetry={state.reload} />}

      <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-[minmax(0,1.4fr)_repeat(4,minmax(0,1fr))]">
        <Field label="Hľadať">
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-2.5 size-4 text-ink-3" aria-hidden />
            <Input type="search" value={q} onChange={(e) => set('q', e.target.value)} placeholder="Názov alebo úloha" className="w-full pl-8" />
          </div>
        </Field>
        <Field label="Téma">
          <Select value={topic} onChange={(e) => set('topic', e.target.value)}>
            <option value="">Všetky témy</option>
            {TOPIC_ORDER.map((id) => <option key={id} value={id}>{TOPICS.find((t) => t.id === id)!.title}</option>)}
          </Select>
        </Field>
        <Field label="Prístup">
          <Select value={paradigm} onChange={(e) => set('paradigm', e.target.value)}>
            <option value="">Všetky prístupy</option>
            {(Object.keys(PARADIGM) as Paradigm[]).map((p) => <option key={p} value={p}>{PARADIGM[p]}</option>)}
          </Select>
        </Field>
        <Field label="Čas v priemere najviac">
          <Select value={maxAvg} onChange={(e) => set('max', e.target.value)}>
            <option value="">Bez obmedzenia</option>
            {['O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)', 'O(n^3)'].map((c) => <option key={c} value={c}>{prettyO(c)}</option>)}
          </Select>
        </Field>
        <Field label="Pôvod">
          <Select value={origin} onChange={(e) => set('origin', e.target.value)}>
            <option value="">Vstavané aj vlastné</option>
            <option value="builtin">Len vstavané</option>
            <option value="own">Len vlastné</option>
          </Select>
        </Field>
      </div>

      <div className="mb-6 flex flex-wrap items-center gap-2" role="group" aria-label="Vlastnosti">
        <button
          onClick={() => set('viz', vizOnly ? '' : '1')}
          aria-pressed={vizOnly}
          className={cx('h-8 rounded-full border px-3 text-[13px] cursor-pointer transition-colors',
            vizOnly ? 'border-accent bg-accent-soft text-accent' : 'border-line-strong text-ink-2 hover:bg-surface-2')}
        >
          dá sa vizualizovať
        </button>
        {usedProps.map((p) => (
          <button
            key={p}
            onClick={() => toggleProp(p)}
            aria-pressed={props.includes(p)}
            className={cx('h-8 rounded-full border px-3 text-[13px] cursor-pointer transition-colors',
              props.includes(p) ? 'border-accent bg-accent-soft text-accent' : 'border-line-strong text-ink-2 hover:bg-surface-2')}
          >
            {PROPERTY[p]}
          </button>
        ))}
        {active ? (
          <Button size="sm" variant="ghost" onClick={() => setParams(new URLSearchParams(), { replace: true })}>Zrušiť filtre</Button>
        ) : null}
      </div>

      <Panel
        title={state.data ? <h2 className="text-[15px] font-semibold num">{filtered.length} z {state.data.algorithms.length} algoritmov</h2> : 'Algoritmy'}
      >
        {!state.data && !state.error && <div className="space-y-2 p-4">{Array.from({ length: 8 }, (_, i) => <Skeleton key={i} className="h-9" />)}</div>}
        {state.data && filtered.length === 0 && (
          <Empty title="Filtrom nezodpovedá žiadny algoritmus" action={<Button size="sm" onClick={() => setParams(new URLSearchParams())}>Zrušiť filtre</Button>}>
            Skús voľnejšiu hranicu zložitosti alebo menej vlastností.
          </Empty>
        )}
        {filtered.length > 0 && <AlgorithmTable algorithms={filtered} problemNames={problemNames} />}
      </Panel>
    </>
  )
}

import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Menu, X } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { TOPICS, TOPIC_ORDER, formatNumber, prettyO, topicOf } from '../lib/labels'
import { Logo, LogoMark } from '../components/Logo'
import { NAV, SiteFooter } from '../components/Layout'
import { ComplexityLadder } from '../components/ComplexityLadder'
import { CodeView } from '../components/CodeView'
import { ResultsChart, SeriesLegend } from '../components/ResultsChart'
import { ArrayView } from '../components/viz/ArrayView'
import { RoleLegend } from '../components/viz/StepView'
import { Button, Tag } from '../components/ui'
import type { AlgorithmResultSeries, ArrayStep } from '../types'

// Skutočné namerané priemery z pripraveného experimentu „Jednoduché triedenia oproti merge sortu“
// (náhodné pole, 3 opakovania), pozri docs/OVERENIE-zlozitosti.md.
const SIZES = [250, 500, 1000, 2000]
const MEASURED: { id: string; name: string; ops: number[]; declared: string; measured: string; k: number }[] = [
  { id: 'alg_bubble', name: 'Bubble sort', ops: [46360, 186050, 744985, 2975600], declared: 'O(n^2)', measured: 'O(n^2)', k: 2.0 },
  { id: 'alg_insertion', name: 'Insertion sort', ops: [30715, 123095, 491963, 1955192], declared: 'O(n^2)', measured: 'O(n^2)', k: 2.0 },
  { id: 'alg_merge', name: 'Merge sort', ops: [3667, 8333, 18672, 41354], declared: 'O(n log n)', measured: 'O(n log n)', k: 1.17 },
]

const SERIES: AlgorithmResultSeries[] = MEASURED.map((m) => ({
  algorithm_id: m.id,
  algorithm_name: m.name,
  variant_index: 0,
  variant_label: 'náhodné pole',
  is_correct: true,
  check_messages: [],
  errors: [],
  complexity: null,
  points: SIZES.map((n, i) => ({
    input_size: n, runs: 3, time_ms_min: null, time_ms_avg: null, time_ms_max: null, memory_kb_avg: null,
    operation_counts_avg: { total: m.ops[i] }, timeouts: 0, errors: 0, incorrect: 0,
  })),
}))
const COLORS = { alg_bubble: 0, alg_insertion: 1, alg_merge: 2 }

const SNIPPET = `def solve(data, tracker):
    a = data
    for i in range(1, len(a)):
        j = i
        while j > 0:
            tracker.compare(j - 1, j)
            if a[j - 1] <= a[j]:
                break
            a[j - 1], a[j] = a[j], a[j - 1]
            tracker.swap(j - 1, j)
            j -= 1
    return a`

const DEMO_INPUT = [38, 12, 71, 25, 90, 7, 54, 33, 66, 19, 82, 45]

/** Živá ukážka: skutočná stopa insertion sortu z API, prehráva sa dookola. */
function LiveDemo() {
  const [steps, setSteps] = useState<ArrayStep[] | null>(null)
  const [i, setI] = useState(0)
  useEffect(() => {
    let alive = true
    api.visualize({ algorithm_id: 'alg_insertion', input: DEMO_INPUT, max_steps: 400 })
      .then((t) => alive && setSteps(t.steps.filter((s): s is ArrayStep => s.kind === 'array')))
      .catch(() => alive && setSteps([]))
    return () => { alive = false }
  }, [])
  useEffect(() => {
    if (!steps?.length) return
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (reduce) return
    const t = window.setInterval(() => setI((x) => (x + 1) % (steps.length + 6)), 650)
    return () => window.clearInterval(t)
  }, [steps])

  const fallback: ArrayStep = { kind: 'array', index: 0, type: 'snapshot', label: 'vstup', array: DEMO_INPUT, highlights: [] }
  const step = steps?.length ? steps[Math.min(i, steps.length - 1)] : fallback
  const total = steps?.length ?? 0
  return (
    <div data-ui className="rounded-[var(--radius-lg)] border border-line bg-surface">
      <div className="flex items-baseline justify-between gap-3 px-4 pt-3.5">
        <p className="text-[15px] font-semibold">Insertion sort</p>
        <p className="text-[13px] text-ink-3 num">{total ? `krok ${Math.min(i, total - 1) + 1} z ${total}` : 'pripravujem'}</p>
      </div>
      <p className="min-h-[1.5rem] px-4 pt-1 text-[15px]" aria-live="off">{step.label}</p>
      <div className="px-4 py-3"><ArrayView step={step} /></div>
      <div className="border-t border-line px-4 py-3"><RoleLegend kind="array" /></div>
    </div>
  )
}

function TopBar() {
  const [open, setOpen] = useState(false)
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-ground">
      <div className="mx-auto flex h-16 max-w-[1200px] items-center justify-between gap-4 px-4 sm:px-8">
        <Link to="/" aria-label="AlgoLab, úvodná stránka"><Logo size={30} /></Link>
        <nav aria-label="Hlavná navigácia" className="hidden items-center gap-1 md:flex">
          {NAV.map((n) => (
            <Link key={n.to} to={n.to} className="rounded-[var(--radius)] px-3 py-2 text-sm text-ink-2 hover:bg-surface-2 hover:text-ink">{n.label}</Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <Link to="/problems" className="hidden sm:block"><Button variant="primary">Otvoriť aplikáciu</Button></Link>
          <button aria-label={open ? 'Zavrieť menu' : 'Otvoriť menu'} onClick={() => setOpen(!open)}
            className="grid size-9 place-items-center rounded-[var(--radius)] hover:bg-surface-2 md:hidden cursor-pointer">
            {open ? <X className="size-5" aria-hidden /> : <Menu className="size-5" aria-hidden />}
          </button>
        </div>
      </div>
      {open && (
        <nav aria-label="Menu" className="border-t border-line px-4 py-2 md:hidden">
          {NAV.map((n) => (
            <Link key={n.to} to={n.to} className="block rounded-[var(--radius)] px-2 py-2.5 text-ink-2 hover:bg-surface-2">{n.label}</Link>
          ))}
        </nav>
      )}
    </header>
  )
}

export default function Landing() {
  const problems = useAsync(() => api.problems(), [])
  const info = useAsync(() => api.info(), [])

  const topics = useMemo(() => {
    const by = new Map<string, { problems: number; algorithms: number; names: string[] }>()
    for (const p of problems.data ?? []) {
      const t = topicOf(p.category)
      const cur = by.get(t) ?? { problems: 0, algorithms: 0, names: [] }
      cur.problems += 1
      cur.algorithms += p.algorithm_count
      cur.names.push(p.name)
      by.set(t, cur)
    }
    return TOPIC_ORDER.filter((t) => by.has(t)).map((t) => ({ id: t, title: TOPICS.find((x) => x.id === t)!.title, ...by.get(t)! }))
  }, [problems.data])

  const stats = [
    { value: info.data?.problems ?? 27, label: 'úloh' },
    { value: info.data?.algorithms ?? 85, label: 'algoritmov' },
    { value: 5, label: 'druhov zobrazenia: pole, tabuľka, graf, strom, text' },
  ]

  return (
    <div className="min-h-dvh bg-ground">
      <TopBar />
      <main>
        {/* úvod */}
        <section className="mx-auto grid max-w-[1200px] items-center gap-10 px-4 pb-16 pt-12 sm:px-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] lg:pt-20">
          <div className="space-y-6">
            <h1 className="max-w-[24ch] text-[36px] font-semibold leading-[1.08] tracking-[-0.025em] sm:text-[46px]">
              Algoritmy krok po kroku a ich zložitosť v číslach
            </h1>
            <p className="max-w-[52ch] text-[17px] leading-relaxed text-ink-2">
              AlgoLab spustí algoritmus na skutočnom vstupe, zaznamená každý jeho krok a porovná ho s inými
              algoritmami na vstupoch rastúcej veľkosti. Z nameraných dát odhadne triedu zložitosti.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link to="/problems">
                <Button variant="primary" className="h-11 px-5 text-[15px]" iconRight={<ArrowRight className="size-4" aria-hidden />}>Začať s úlohami</Button>
              </Link>
              <Link to="/visualizer"><Button className="h-11 px-5 text-[15px]">Otvoriť vizualizáciu</Button></Link>
            </div>
          </div>
          <LiveDemo />
        </section>

        {/* katalóg v číslach */}
        <section aria-label="Obsah katalógu" className="border-y border-line bg-surface">
          <div className="mx-auto grid max-w-[1200px] gap-6 px-4 py-8 sm:grid-cols-3 sm:px-8">
            {stats.map((s) => (
              <p key={s.label} className="flex items-baseline gap-3">
                <span className="text-[40px] font-semibold leading-none tracking-[-0.02em] num">{formatNumber(s.value)}</span>
                <span className="text-[15px] text-ink-2">{s.label}</span>
              </p>
            ))}
          </div>
        </section>

        {/* experiment a odhad zložitosti */}
        <section className="mx-auto max-w-[1200px] px-4 py-20 sm:px-8">
          <div className="mb-8 max-w-[62ch] space-y-3">
            <h2 className="text-[30px] font-semibold leading-tight tracking-[-0.02em]">Experiment ukáže, ako algoritmus rastie</h2>
            <p className="text-[16px] leading-relaxed text-ink-2">
              Všetky algoritmy dostanú v každom prípade ten istý vstup. Počet operácií nezávisí od počítača, preto je
              z neho dobre vidieť triedu zložitosti. V logaritmickej mierke je nᵏ priamka so sklonom k.
            </p>
          </div>
          <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)]">
            <div data-ui className="rounded-[var(--radius-lg)] border border-line bg-surface">
              <div className="px-4 pt-4">
                <p className="text-[15px] font-semibold">Počet operácií pri triedení náhodného poľa</p>
                <div className="pt-2"><SeriesLegend series={SERIES} colorIndex={COLORS} /></div>
              </div>
              <div className="px-2 pb-2 pt-2"><ResultsChart series={SERIES} colorIndex={COLORS} metric="operations" log /></div>
            </div>
            <div data-ui className="rounded-[var(--radius-lg)] border border-line bg-surface">
              <p className="px-4 pt-4 text-[15px] font-semibold">Odhad z merania oproti deklarovanej triede</p>
              <ul className="divide-y divide-line px-4 pb-2 pt-1">
                {MEASURED.map((m) => (
                  <li key={m.id} className="flex items-center justify-between gap-4 py-3.5">
                    <div>
                      <p className="font-medium">{m.name}</p>
                      <p className="text-[13px] text-ink-3 num">odhad {prettyO(m.measured)}, exponent k = {formatNumber(m.k, 2)}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <ComplexityLadder size="sm" declared={m.declared} avg={m.declared} measured={m.measured} />
                      <Tag tone="ok">zhoda</Tag>
                    </div>
                  </li>
                ))}
              </ul>
              <p className="border-t border-line px-4 py-3 text-[13px] text-ink-3">
                Plný schod je odhad z merania, rámik je deklarovaná trieda.
              </p>
            </div>
          </div>
          <Link to="/experiments" className="mt-6 inline-flex items-center gap-1.5 text-[15px] font-medium text-accent hover:underline">
            Pozrieť pripravené experimenty <ArrowRight className="size-4" aria-hidden />
          </Link>
        </section>

        {/* vlastný kód */}
        <section className="border-y border-line bg-surface">
          <div className="mx-auto grid max-w-[1200px] items-center gap-10 px-4 py-20 sm:px-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <div className="order-2 min-w-0 lg:order-1"><CodeView code={SNIPPET} /></div>
            <div className="order-1 space-y-4 lg:order-2">
              <h2 className="text-[30px] font-semibold leading-tight tracking-[-0.02em]">Napíš vlastný algoritmus a over ho</h2>
              <p className="max-w-[54ch] text-[16px] leading-relaxed text-ink-2">
                Algoritmus je obyčajná funkcia <code className="text-[15px]">solve</code> v Pythone. Volania trackera
                zaznamenajú kroky pre vizualizáciu a spočítajú operácie. Výstup skontroluje funkcia úlohy alebo
                referenčný algoritmus a kód beží v izolovanom procese s časovým limitom.
              </p>
              <Link to="/guide" className="inline-flex items-center gap-1.5 text-[15px] font-medium text-accent hover:underline">
                Ako na to v príručke <ArrowRight className="size-4" aria-hidden />
              </Link>
            </div>
          </div>
        </section>

        {/* témy */}
        <section className="mx-auto max-w-[1200px] px-4 py-20 sm:px-8">
          <h2 className="mb-8 text-[30px] font-semibold leading-tight tracking-[-0.02em]">Čo v katalógu nájdeš</h2>
          <div className="grid gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">
            {topics.map((t) => (
              <div key={t.id}>
                <h3 className="flex items-baseline justify-between gap-3 border-b border-line pb-2 text-[16px] font-semibold">
                  {t.title}
                  <span className="text-[13px] font-normal text-ink-3 num">{t.algorithms} algoritmov</span>
                </h3>
                <ul className="mt-2 space-y-1 text-[15px] text-ink-2">
                  {t.names.slice(0, 4).map((n) => <li key={n}>{n}</li>)}
                  {t.names.length > 4 && <li className="text-ink-3">a ďalšie</li>}
                </ul>
              </div>
            ))}
            {!topics.length && <p className="text-ink-3">Načítavam katalóg…</p>}
          </div>
        </section>

        {/* záver */}
        <section className="bg-accent-soft">
          <div className="mx-auto flex max-w-[1200px] flex-wrap items-center justify-between gap-6 px-4 py-14 sm:px-8">
            <div className="flex items-center gap-4">
              <span className="size-14 shrink-0" style={{ ['--logo-bg' as string]: 'var(--accent-soft)' }}><LogoMark detailed className="size-full" /></span>
              <h2 className="text-[26px] font-semibold leading-tight tracking-[-0.02em]">Začni jednou úlohou a jedným algoritmom</h2>
            </div>
            <Link to="/problems">
              <Button variant="primary" className="h-11 px-5 text-[15px]" iconRight={<ArrowRight className="size-4" aria-hidden />}>Otvoriť úlohy</Button>
            </Link>
          </div>
        </section>
      </main>
      <div className="mx-auto max-w-[1200px] px-4 sm:px-8"><SiteFooter className="mt-0" /></div>
    </div>
  )
}

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ChevronFirst, ChevronLast, ChevronLeft, ChevronRight, Dices, Pause, Play } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { useEditAuth } from '../lib/auth'
import { formatNumber, opsLabel } from '../lib/labels'
import { ParamsForm, defaultParams } from '../components/ParamsForm'
import { CodeView } from '../components/CodeView'
import { RoleLegend, StepView } from '../components/viz/StepView'
import { Button, Empty, Field, Input, LoadError, Notice, PageHeader, Panel, Select, Skeleton, Tag, cx } from '../components/ui'
import type { Algorithm, InputGenerator, ProblemSummary, Scalar, VisualizationTrace } from '../types'

const SPEEDS = [
  { ms: 1400, label: 'pomaly' },
  { ms: 700, label: 'normálne' },
  { ms: 300, label: 'rýchlo' },
  { ms: 80, label: 'veľmi rýchlo' },
]

const COUNTED: Record<string, string> = {
  compare: 'porovnania', swap: 'výmeny', set: 'zápisy', pivot: 'pivoty', visit: 'návštevy',
  edge: 'hrany', relax: 'uvoľnenia', cell: 'bunky', match: 'zhody', mismatch: 'nezhody', shift: 'posuny',
  focus: 'kroky v strome', structure: 'zmeny štruktúry',
}

function useCumulative(trace: VisualizationTrace | null) {
  return useMemo(() => {
    if (!trace) return []
    const acc: Record<string, number> = {}
    return trace.steps.map((s) => {
      if (COUNTED[s.type]) acc[s.type] = (acc[s.type] ?? 0) + 1
      return { ...acc }
    })
  }, [trace])
}

function TracePanel({ trace, index, algorithm }: { trace: VisualizationTrace; index: number; algorithm?: Algorithm }) {
  const total = trace.steps.length
  const i = Math.min(index, total - 1)
  const step = trace.steps[i]
  const done = index >= total - 1
  const cumulative = useCumulative(trace)[i] ?? {}
  return (
    <Panel className="min-w-0 flex flex-col">
      <header className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 px-4 pt-3.5">
        <h2 className="text-[15px] font-semibold">{trace.algorithm_name}</h2>
        <span className="text-[13px] text-ink-3 num">krok {formatNumber(i + 1)} z {formatNumber(total)}</span>
      </header>
      <p className="min-h-[3rem] px-4 pt-1 text-[15px] text-ink" aria-live="polite">
        {step ? step.label : 'Bez krokov'}
      </p>
      <div className="flex-1 px-4 py-3">
        <StepView step={step} trace={trace} />
      </div>
      <footer className="space-y-2 border-t border-line px-4 py-3 text-[13px]">
        <p className="flex flex-wrap gap-x-4 gap-y-1 text-ink-2 num">
          {Object.entries(cumulative).length === 0 && <span className="text-ink-3">Zatiaľ žiadna operácia</span>}
          {Object.entries(cumulative).map(([k, v]) => (
            <span key={k}>{COUNTED[k]} <span className="font-semibold text-ink">{formatNumber(v)}</span></span>
          ))}
        </p>
        {done && (
          <div className="flex flex-wrap items-center gap-2">
            {trace.is_correct === true && <Tag tone="ok">výsledok je správny</Tag>}
            {trace.is_correct === false && <Tag tone="bad">výsledok je nesprávny</Tag>}
            {trace.check_message && <span className="text-ink-2">{trace.check_message}</span>}
            {trace.truncated && <Tag tone="warn">záznam skrátený na {formatNumber(trace.max_steps)} krokov</Tag>}
          </div>
        )}
        {done && trace.stdout && (
          <details><summary className="cursor-pointer text-ink-2">Výpis print</summary>
            <pre className="mt-1 max-h-40 overflow-auto rounded bg-surface-2 p-2 text-[12px]">{trace.stdout}</pre>
          </details>
        )}
        {algorithm && (
          <details>
            <summary className="cursor-pointer text-ink-2">Kód algoritmu</summary>
            <div className="mt-2"><CodeView code={algorithm.code.trim()} maxHeight={360} /></div>
          </details>
        )}
        {done && (
          <p className="text-ink-3">
            Celkom: {Object.entries(trace.operation_counts).filter(([k]) => k !== 'total').map(([k, v]) => `${opsLabel(k)} ${formatNumber(v)}`).join(', ') || 'bez počítaných operácií'}
          </p>
        )}
      </footer>
    </Panel>
  )
}

function Player({ index, total, playing, speed, onIndex, onPlay, onSpeed }: {
  index: number; total: number; playing: boolean; speed: number
  onIndex: (i: number) => void; onPlay: (p: boolean) => void; onSpeed: (ms: number) => void
}) {
  const last = Math.max(0, total - 1)
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-[var(--radius-lg)] border border-line bg-surface px-3 py-2">
      <div className="flex items-center gap-1">
        <Button size="sm" variant="ghost" aria-label="Na začiatok" onClick={() => onIndex(0)} disabled={index === 0} icon={<ChevronFirst className="size-4" />} />
        <Button size="sm" variant="ghost" aria-label="Predchádzajúci krok" onClick={() => onIndex(Math.max(0, index - 1))} disabled={index === 0} icon={<ChevronLeft className="size-4" />} />
        <Button size="sm" variant="primary" className="w-24" onClick={() => onPlay(!playing)} disabled={total === 0}
          icon={playing ? <Pause className="size-4" aria-hidden /> : <Play className="size-4" aria-hidden />}>
          {playing ? 'Zastaviť' : index >= last && total > 0 ? 'Znova' : 'Prehrať'}
        </Button>
        <Button size="sm" variant="ghost" aria-label="Ďalší krok" onClick={() => onIndex(Math.min(last, index + 1))} disabled={index >= last} icon={<ChevronRight className="size-4" />} />
        <Button size="sm" variant="ghost" aria-label="Na koniec" onClick={() => onIndex(last)} disabled={index >= last} icon={<ChevronLast className="size-4" />} />
      </div>
      <input
        type="range" min={0} max={last} value={Math.min(index, last)}
        onChange={(e) => onIndex(Number(e.target.value))}
        aria-label="Posun v krokoch"
        className="h-1.5 min-w-[160px] flex-1 cursor-pointer accent-[var(--accent)]"
      />
      <span className="w-24 text-right text-[13px] text-ink-2 num">{formatNumber(Math.min(index, last) + (total ? 1 : 0))} / {formatNumber(total)}</span>
      <Select aria-label="Rýchlosť" value={speed} onChange={(e) => onSpeed(Number(e.target.value))} className="h-8 text-[13px]">
        {SPEEDS.map((s) => <option key={s.ms} value={s.ms}>{s.label}</option>)}
      </Select>
    </div>
  )
}

export default function Visualizer() {
  const [params, setParams] = useSearchParams()
  const { info } = useEditAuth()
  const problemsState = useAsync(() => api.problems(), [])
  const vizProblems = useMemo(
    () => (problemsState.data ?? []).filter((p) => p.renderer !== 'none' && p.visualizable_count > 0),
    [problemsState.data],
  )
  const problemId = params.get('problem') ?? vizProblems[0]?.id ?? ''
  const problem: ProblemSummary | undefined = vizProblems.find((p) => p.id === problemId)

  const detail = useAsync(async () => {
    if (!problemId) return null
    const [algorithms, generators] = await Promise.all([api.problemAlgorithms(problemId), api.problemGenerators(problemId)])
    return { algorithms: algorithms.filter((a) => a.supports_visualization), generators }
  }, [problemId])

  const algs = detail.data?.algorithms ?? []
  const aId = params.get('a') && algs.some((x) => x.id === params.get('a')) ? params.get('a')! : algs[0]?.id ?? ''
  const bId = params.get('b') && algs.some((x) => x.id === params.get('b')) ? params.get('b')! : ''
  const generator: InputGenerator | undefined = detail.data?.generators[0]

  const limit = info?.viz_limits?.[problem?.renderer ?? 'array'] ?? 40
  const [n, setN] = useState(10)
  const [seed, setSeed] = useState(1)
  const [genParams, setGenParams] = useState<Record<string, Scalar>>({})
  const [input, setInput] = useState<unknown>(undefined)
  const [inputFor, setInputFor] = useState('')
  const [inputText, setInputText] = useState('')
  const [inputError, setInputError] = useState<string | null>(null)
  const [traces, setTraces] = useState<VisualizationTrace[]>([])
  const [runError, setRunError] = useState<string | null>(null)
  const [running, setRunning] = useState(false)
  const [index, setIndex] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(700)

  const setParam = (key: string, value: string) => {
    const next = new URLSearchParams(params)
    if (value) next.set(key, value)
    else next.delete(key)
    if (key === 'problem') { next.delete('a'); next.delete('b') }
    setParams(next, { replace: true })
  }

  // nový generátor: predvolené parametre a veľkosť
  useEffect(() => {
    if (!generator) return
    setGenParams(defaultParams(generator.param_spec))
    setN(Math.min(generator.viz_size, limit))
    setSeed(1)
  }, [generator, limit])

  // vygenerovať vstup
  useEffect(() => {
    if (!generator) return
    let alive = true
    api.preview(generator.id, n, genParams, seed)
      .then((r) => {
        if (!alive) return
        if (r.error || r.input === null) {
          setInputError(r.error ?? 'Vstup je príliš veľký na zobrazenie')
          return
        }
        setInputError(null)
        setInput(r.input)
        setInputFor(generator.problem_id)
        setInputText(JSON.stringify(r.input))
      })
      .catch((e) => alive && setInputError(e instanceof Error ? e.message : String(e)))
    return () => { alive = false }
  }, [generator, n, genParams, seed])

  // spustiť vizualizáciu pri zmene vstupu alebo algoritmov
  useEffect(() => {
    if (input === undefined || !aId || inputFor !== problemId) return
    if (!algs.some((a) => a.id === aId)) return
    let alive = true
    setRunning(true)
    setRunError(null)
    setPlaying(false)
    const ids = [aId, bId].filter(Boolean)
    Promise.all(ids.map((id) => api.visualize({ algorithm_id: id, input, max_steps: 3000 })))
      .then((res) => {
        if (!alive) return
        setTraces(res)
        setIndex(0)
      })
      .catch((e) => alive && setRunError(e instanceof Error ? e.message : String(e)))
      .finally(() => alive && setRunning(false))
    return () => { alive = false }
    // algs sa mení spolu s problemId, stačí sledovať jeho identifikátor
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [input, inputFor, aId, bId, problemId])

  const total = Math.max(0, ...traces.map((t) => t.steps.length))

  // prehrávanie
  const timer = useRef<number | undefined>(undefined)
  useEffect(() => {
    if (!playing) return
    timer.current = window.setInterval(() => {
      setIndex((i) => {
        if (i >= total - 1) {
          setPlaying(false)
          return i
        }
        return i + 1
      })
    }, speed)
    return () => window.clearInterval(timer.current)
  }, [playing, speed, total])

  const play = useCallback((p: boolean) => {
    if (p && index >= total - 1) setIndex(0)
    setPlaying(p)
  }, [index, total])

  // klávesnica: šípky a medzerník, ak sa nepíše do poľa
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag) || (e.target as HTMLElement)?.isContentEditable) return
      if (e.key === 'ArrowRight') { setPlaying(false); setIndex((i) => Math.min(total - 1, i + 1)) }
      else if (e.key === 'ArrowLeft') { setPlaying(false); setIndex((i) => Math.max(0, i - 1)) }
      else if (e.key === ' ') { e.preventDefault(); play(!playing) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [total, playing, play])

  const applyManual = () => {
    try {
      setInput(JSON.parse(inputText))
      setInputError(null)
    } catch {
      setInputError('Vstup nie je platný JSON')
    }
  }

  if (problemsState.error) return <LoadError error={problemsState.error} onRetry={problemsState.reload} />

  return (
    <>
      <PageHeader
        title="Vizualizácia"
        lead="Algoritmus beží na skutočnom vstupe a každý jeho krok sa zaznamená. Krokuj šípkami alebo spusti prehrávanie. Druhý algoritmus dostane ten istý vstup."
      />

      <Panel className="mb-4">
        <div className="grid gap-3 p-4 md:grid-cols-3">
          <Field label="Úloha">
            <Select value={problemId} onChange={(e) => setParam('problem', e.target.value)}>
              {vizProblems.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </Select>
          </Field>
          <Field label="Algoritmus">
            <Select value={aId} onChange={(e) => setParam('a', e.target.value)} disabled={!algs.length}>
              {algs.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </Select>
          </Field>
          <Field label="Porovnať s">
            <Select value={bId} onChange={(e) => setParam('b', e.target.value)} disabled={algs.length < 2}>
              <option value="">bez porovnania</option>
              {algs.filter((a) => a.id !== aId).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </Select>
          </Field>
        </div>
        <div className="grid grid-cols-2 items-end gap-3 px-4 pb-4 sm:grid-cols-[repeat(auto-fit,minmax(170px,240px))]">
          <Field label={`Veľkosť n ≤ ${limit}`}>
            <Input type="number" min={1} max={limit} value={n} className="num"
              onChange={(e) => setN(Math.max(1, Math.min(limit, Number(e.target.value) || 1)))} />
          </Field>
          {generator && <ParamsForm spec={generator.param_spec} value={genParams} onChange={setGenParams} />}
          <Button icon={<Dices className="size-4" aria-hidden />} onClick={() => setSeed((s) => s + 1)}>Nový vstup</Button>
        </div>
        <details className="border-t border-line px-4 py-2.5">
          <summary className="cursor-pointer text-[13px] text-ink-2">Vstup ako JSON, dá sa upraviť ručne</summary>
          <div className="mt-2 space-y-2">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={3}
              spellCheck={false}
              aria-label="Vstup ako JSON"
              className="w-full rounded-[var(--radius)] border border-line-strong bg-surface-2 p-2 font-mono text-[12px]"
            />
            <Button size="sm" onClick={applyManual}>Použiť tento vstup</Button>
          </div>
        </details>
      </Panel>

      {inputError && <div className="mb-4"><Notice tone="bad" title="Vstup sa nepodarilo pripraviť">{inputError}</Notice></div>}
      {runError && <div className="mb-4"><Notice tone="bad" title="Vizualizácia zlyhala">{runError}</Notice></div>}

      {(!problemsState.data || (detail.loading && !detail.data)) && <Skeleton className="h-[420px]" />}
      {problemsState.data && vizProblems.length === 0 && <Empty title="Žiadna úloha s vizualizáciou" />}
      {detail.data && algs.length === 0 && (
        <Empty title="Táto úloha nemá algoritmus s vizualizáciou">
          Vizualizovať sa dá algoritmus, ktorého funkcia solve prijíma parameter tracker.
        </Empty>
      )}

      {traces.length > 0 && (
        <div className={cx('space-y-4 transition-opacity', running && 'opacity-60')}>
          <Player index={index} total={total} playing={playing} speed={speed}
            onIndex={(i) => { setPlaying(false); setIndex(i) }} onPlay={play} onSpeed={setSpeed} />
          <RoleLegend kind={traces[0].renderer} />
          <div className={cx('grid gap-4', traces.length > 1 && 'xl:grid-cols-2')}>
            {traces.map((t, k) => (
              <TracePanel key={`${t.algorithm_id}-${k}`} trace={t} index={index} algorithm={algs.find((a) => a.id === t.algorithm_id)} />
            ))}
          </div>
          {problem && (
            <p className="text-[13px] text-ink-3">
              Na malom vstupe sa rozdiel ukáže v počte krokov. Ako rastie s veľkosťou vstupu, ukáže{' '}
              <Link className="text-accent underline" to={`/experiments/new?problem=${problem.id}`}>experiment</Link>.
            </p>
          )}
        </div>
      )}
    </>
  )
}

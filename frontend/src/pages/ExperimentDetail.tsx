import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { Download, Play, RotateCcw, Square, Trash2 } from 'lucide-react'
import { api } from '../api'
import { useAsync } from '../lib/hooks'
import { CASE_LABEL, CONFIDENCE_LABEL, formatMs, formatNumber, prettyO } from '../lib/labels'
import { ComplexityLadder } from '../components/ComplexityLadder'
import { ResultsChart, SeriesLegend, type Metric } from '../components/ResultsChart'
import { StatusTag } from '../components/StatusTag'
import { Button, Empty, LoadError, Notice, PageHeader, Panel, Segmented, Skeleton, Tag } from '../components/ui'
import { BackLink } from './ProblemDetail'
import type { Algorithm, AlgorithmResultSeries, Experiment, ExperimentResults } from '../types'

function Agreement({ s }: { s: AlgorithmResultSeries }) {
  const c = s.complexity
  if (!c || c.used_metric === 'none') return <span className="text-ink-3">málo dát</span>
  if (c.agreement === 'match') return <Tag tone="ok">zhoda</Tag>
  if (c.agreement === 'mismatch') return <Tag tone="warn">nezhoda</Tag>
  return <Tag>neurčené</Tag>
}

function EstimateTable({ series, algorithms }: { series: AlgorithmResultSeries[]; algorithms: Record<string, Algorithm> }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] text-sm">
        <thead>
          <tr className="border-b border-line text-left text-[13px] text-ink-3">
            <th className="px-4 py-2 font-medium">Algoritmus</th>
            <th className="px-3 py-2 font-medium">Deklarovaná</th>
            <th className="px-3 py-2 font-medium">Odhad z operácií</th>
            <th className="px-3 py-2 font-medium">Odhad z času</th>
            <th className="px-3 py-2 text-right font-medium" title="Sklon priamky v log-log grafe, n^k">Exponent k</th>
            <th className="px-3 py-2 font-medium">Výsledok</th>
            <th className="px-4 py-2 font-medium"><span className="sr-only">Rebrík</span></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {series.map((s) => {
            const c = s.complexity
            const a = algorithms[s.algorithm_id]
            const used = c?.used_metric === 'time' ? c.time : c?.operations
            return (
              <tr key={s.algorithm_id} className="align-top">
                <td className="px-4 py-3">
                  <p className="font-medium">{s.algorithm_name}</p>
                  {s.is_correct === false && <p className="mt-0.5 text-[13px] text-bad">nesprávny výstup</p>}
                </td>
                <td className="px-3 py-3">
                  <p className="font-medium num">{prettyO(c?.declared ?? a?.complexity_time_avg)}</p>
                  {c && <p className="text-xs text-ink-3">{CASE_LABEL[c.declared_case]}</p>}
                </td>
                <td className="px-3 py-3">
                  {c?.operations.status === 'ok' ? (
                    <>
                      <p className="font-medium num">{prettyO(c.operations.best)}</p>
                      <p className="text-xs text-ink-3">istota {CONFIDENCE_LABEL[c.operations.confidence]}{c.operations.second ? `, potom ${prettyO(c.operations.second)}` : ''}</p>
                    </>
                  ) : <p className="text-xs text-ink-3 max-w-[22ch]">{c?.operations.reason ?? '–'}</p>}
                </td>
                <td className="px-3 py-3">
                  {c?.time.status === 'ok' ? (
                    <>
                      <p className="num">{prettyO(c.time.best)}</p>
                      <p className="text-xs text-ink-3">istota {CONFIDENCE_LABEL[c.time.confidence]}</p>
                    </>
                  ) : <p className="text-xs text-ink-3 max-w-[22ch]">{c?.time.reason ?? '–'}</p>}
                </td>
                <td className="px-3 py-3 text-right num">{used?.exponent !== null && used?.exponent !== undefined ? formatNumber(used.exponent, 2) : '–'}</td>
                <td className="px-3 py-3"><Agreement s={s} /></td>
                <td className="px-4 py-3">
                  <ComplexityLadder size="sm" best={a?.complexity_time_best} avg={a?.complexity_time_avg} worst={a?.complexity_time_worst}
                    declared={c?.declared} measured={used?.status === 'ok' ? used.best : null} />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function ValuesTable({ series, metric }: { series: AlgorithmResultSeries[]; metric: Metric }) {
  const sizes = [...new Set(series.flatMap((s) => s.points.map((p) => p.input_size)))].sort((a, b) => a - b)
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm num">
        <thead>
          <tr className="border-b border-line text-[13px] text-ink-3">
            <th className="px-4 py-2 text-left font-medium">n</th>
            {series.map((s) => <th key={s.algorithm_id} className="px-3 py-2 text-right font-medium">{s.algorithm_name}</th>)}
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {sizes.map((n) => (
            <tr key={n}>
              <td className="px-4 py-2 font-medium">{formatNumber(n)}</td>
              {series.map((s) => {
                const p = s.points.find((x) => x.input_size === n)
                const v = metric === 'operations' ? p?.operation_counts_avg.total : p?.time_ms_avg
                const issue = p && (p.timeouts ? `${p.timeouts}× časový limit` : p.errors ? `${p.errors}× chyba` : '')
                return (
                  <td key={s.algorithm_id} className="px-3 py-2 text-right">
                    {issue ? <span className="text-warn">{issue}</span>
                      : v === undefined || v === null ? '–'
                      : metric === 'time' ? formatMs(v) : formatNumber(v)}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function ExperimentDetail() {
  const { id = '' } = useParams()
  const [search, setSearch] = useSearchParams()
  const navigate = useNavigate()
  const base = useAsync(async () => {
    const experiment = await api.experiment(id)
    const [problem, algorithms] = await Promise.all([api.problem(experiment.problem_id), api.problemAlgorithms(experiment.problem_id)])
    return { experiment, problem, algorithms: Object.fromEntries(algorithms.map((a) => [a.id, a])) }
  }, [id])
  const [experiment, setExperiment] = useState<Experiment | null>(null)
  const [results, setResults] = useState<ExperimentResults | null>(null)
  const [running, setRunning] = useState(false)
  const [errors, setErrors] = useState<string[]>([])
  const [fatal, setFatal] = useState<string | null>(null)
  const [variant, setVariant] = useState('0')
  const [metric, setMetric] = useState<Metric>('operations')
  const [scale, setScale] = useState<'log' | 'linear'>('log')
  const stopRef = useRef(false)

  useEffect(() => {
    if (base.data) setExperiment(base.data.experiment)
  }, [base.data])

  const loadResults = useCallback(async () => {
    try {
      setResults(await api.results(id))
    } catch (e) {
      setFatal(e instanceof Error ? e.message : String(e))
    }
  }, [id])

  useEffect(() => {
    if (base.data && base.data.experiment.done_cases > 0) loadResults()
  }, [base.data, loadResults])

  const loop = useCallback(async (fresh: boolean) => {
    setRunning(true)
    setFatal(null)
    stopRef.current = false
    try {
      let prog = fresh ? await api.start(id) : await api.step(id)
      setExperiment(prog.experiment)
      if (fresh) setErrors([])
      let n = 0
      while (!prog.finished && !stopRef.current) {
        prog = await api.step(id)
        setExperiment(prog.experiment)
        if (prog.last_errors.length) setErrors((e) => [...e, ...prog.last_errors].slice(-6))
        if (++n % 2 === 0) await loadResults()
      }
      if (stopRef.current && !prog.finished) setExperiment(await api.cancel(id))
      await loadResults()
    } catch (e) {
      setFatal(e instanceof Error ? e.message : String(e))
    } finally {
      setRunning(false)
    }
  }, [id, loadResults])

  // automatické spustenie po vytvorení
  useEffect(() => {
    if (search.get('start') === '1' && base.data && base.data.experiment.status === 'pending' && !running) {
      setSearch({}, { replace: true })
      loop(true)
    }
  }, [search, base.data, running, loop, setSearch])

  const colorIndex = useMemo(
    () => Object.fromEntries((experiment?.algorithm_ids ?? []).map((a, i) => [a, i])),
    [experiment],
  )

  if (base.error) return <LoadError error={base.error} onRetry={base.reload} />
  if (!base.data || !experiment) return <div className="space-y-4"><Skeleton className="h-10 w-96" /><Skeleton className="h-[420px]" /></div>

  const { problem, algorithms } = base.data
  const variants = results?.variants ?? experiment.variants
  const vIndex = Number(variant)
  const shown = (results?.series ?? []).filter((s) => s.variant_index === vIndex)
  const pct = experiment.total_cases ? Math.round((100 * experiment.done_cases) / experiment.total_cases) : 0
  const incorrect = shown.filter((s) => s.is_correct === false)

  const remove = async () => {
    if (!window.confirm('Zmazať experiment aj s výsledkami?')) return
    await api.deleteExperiment(experiment.id)
    navigate('/experiments')
  }

  return (
    <>
      <PageHeader
        back={<BackLink to={`/problems/${problem.id}`}>{problem.name}</BackLink>}
        title={experiment.name}
        lead={`Veľkosti ${experiment.sizes.map((n) => formatNumber(n)).join(', ')}, každá ${experiment.repeats}× s iným vstupom${variants.length > 1 ? `, ${variants.length} varianty vstupu` : ''}.`}
        actions={
          <>
            <StatusTag status={experiment.status} done={experiment.done_cases} total={experiment.total_cases} />
            {running ? (
              <Button icon={<Square className="size-4" aria-hidden />} onClick={() => { stopRef.current = true }}>Prerušiť</Button>
            ) : experiment.status === 'running' ? (
              <Button variant="primary" icon={<Play className="size-4" aria-hidden />} onClick={() => loop(false)}>Pokračovať</Button>
            ) : (
              <Button variant="primary" icon={experiment.status === 'pending' ? <Play className="size-4" aria-hidden /> : <RotateCcw className="size-4" aria-hidden />}
                onClick={() => loop(true)}>
                {experiment.status === 'pending' ? 'Spustiť' : 'Spustiť znova'}
              </Button>
            )}
            {!experiment.is_builtin && !running && <Button variant="ghost" aria-label="Zmazať experiment" icon={<Trash2 className="size-4" aria-hidden />} onClick={remove} />}
          </>
        }
      />

      {(running || experiment.status === 'running') && (
        <div className="mb-6 space-y-1.5" aria-live="polite">
          <div className="flex justify-between text-[13px] text-ink-2 num">
            <span>{running ? 'Meranie beží po dávkach' : 'Meranie sa zastavilo uprostred'}</span>
            <span>{experiment.done_cases} z {experiment.total_cases} prípadov</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-surface-2" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
            <div className="h-full rounded-full bg-accent transition-[width] duration-300" style={{ width: `${pct}%` }} />
          </div>
        </div>
      )}
      {fatal && <div className="mb-4"><Notice tone="bad" title="Experiment sa nepodarilo dokončiť">{fatal}</Notice></div>}
      {errors.length > 0 && (
        <div className="mb-4">
          <Notice tone="warn" title="Niektoré behy skončili chybou">
            <ul className="list-disc pl-4">{errors.map((e, i) => <li key={i}>{e}</li>)}</ul>
          </Notice>
        </div>
      )}

      {experiment.status === 'pending' && !running && !results && (
        <Panel><Empty title="Experiment ešte nebežal">Spusti ho a výsledky sa budú dopĺňať priebežne.</Empty></Panel>
      )}

      {results && (
        <div className="space-y-6">
          {incorrect.length > 0 && (
            <Notice tone="warn" title={`Nesprávny výstup: ${incorrect.map((s) => s.algorithm_name).join(', ')}`}>
              {incorrect.flatMap((s) => s.check_messages).slice(0, 3).map((m, i) => <p key={i}>{m}</p>)}
            </Notice>
          )}

          <Panel>
            <div className="flex flex-wrap items-center justify-between gap-3 px-4 pt-4">
              <h2 className="text-[15px] font-semibold">{metric === 'operations' ? 'Počet operácií' : 'Čas behu'} podľa veľkosti vstupu</h2>
              <div className="flex flex-wrap gap-2">
                {variants.length > 1 && (
                  <Segmented label="Variant vstupu" value={variant} onChange={setVariant}
                    options={variants.map((v, i) => ({ value: String(i), label: v.label }))} />
                )}
                <Segmented label="Veličina" value={metric} onChange={setMetric}
                  options={[{ value: 'operations', label: 'Operácie' }, { value: 'time', label: 'Čas' }]} />
                <Segmented label="Mierka" value={scale} onChange={setScale}
                  options={[{ value: 'log', label: 'Logaritmická' }, { value: 'linear', label: 'Lineárna' }]} />
              </div>
            </div>
            <div className="px-4 pt-3"><SeriesLegend series={shown} colorIndex={colorIndex} /></div>
            <div className="px-2 pb-2 pt-2">
              <ResultsChart series={shown} colorIndex={colorIndex} metric={metric} log={scale === 'log'} />
            </div>
            <p className="border-t border-line px-4 py-3 text-[13px] text-ink-3">
              {scale === 'log'
                ? 'V logaritmickej mierke na oboch osiach je n^k priamka so sklonom k. Rovnobežné čiary znamenajú rovnakú triedu zložitosti, líšia sa len konštantou.'
                : 'V lineárnej mierke je dobre vidieť, kedy jeden algoritmus začne výrazne zaostávať.'}
              {metric === 'time' && ' Čas závisí od počítača a zaťaženia servera, počet operácií nie.'}
            </p>
          </Panel>

          <Panel title="Odhad zložitosti z merania">
            <p className="px-4 pb-2 text-[13px] text-ink-2">
              Namerané hodnoty sa preložia funkciami a·g(n) + b pre rôzne triedy g a vyberie sa trieda s najmenšou chybou.
              Odhad je len približný, pri malom rozsahu n sa susedné triedy ťažko odlíšia.
            </p>
            {shown.length ? <EstimateTable series={shown} algorithms={algorithms} /> : <Empty title="Zatiaľ bez výsledkov" />}
          </Panel>

          <Panel title={metric === 'operations' ? 'Priemerný počet operácií' : 'Priemerný čas'}
            actions={
              <>
                <a href={api.exportUrl(experiment.id, 'csv')} download><Button size="sm" variant="ghost" icon={<Download className="size-4" aria-hidden />}>CSV</Button></a>
                <a href={api.exportUrl(experiment.id, 'json')} download><Button size="sm" variant="ghost" icon={<Download className="size-4" aria-hidden />}>JSON</Button></a>
              </>
            }>
            <ValuesTable series={shown} metric={metric} />
          </Panel>

          <p className="text-[13px] text-ink-3">
            Algoritmy: {experiment.algorithm_ids.map((aid, i) => (
              <span key={aid}>{i > 0 && ', '}<Link className="underline hover:text-ink" to={`/algorithms/${aid}`}>{algorithms[aid]?.name ?? aid}</Link></span>
            ))}
          </p>
        </div>
      )}
    </>
  )
}

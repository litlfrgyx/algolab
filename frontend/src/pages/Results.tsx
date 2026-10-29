import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../api'
import type { Experiment, ExperimentResults } from '../types'

const PALETTE = ['#f59e0b', '#4cd7f6', '#56e5a9', '#a78bfa']
const fmtSize = (n: number) => (n >= 1000 ? `${n / 1000}k` : `${n}`)
const fmtMs = (v: number) => (v >= 100 ? Math.round(v).toLocaleString() : v.toFixed(2))

type ChartRow = { n: string } & Record<string, number | string>

function buildChart(results: ExperimentResults, metric: 'time' | 'mem' | 'ops'): ChartRow[] {
  const base = results.series[0]?.points ?? []
  return base.map((p, i) => {
    const row: ChartRow = { n: fmtSize(p.input_size) }
    for (const s of results.series) {
      const pt = s.points[i]
      row[s.algorithm_name] =
        metric === 'time'
          ? +pt.time_ms_avg.toFixed(3)
          : metric === 'mem'
            ? +pt.memory_kb_avg.toFixed(1)
            : Math.round(pt.operation_counts_avg.compare ?? 0)
    }
    return row
  })
}

function Tip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: 'var(--surface-container-high)', border: '1px solid rgba(83,68,52,0.4)', borderRadius: 4, padding: '10px 14px' }}>
      <div style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--outline)', marginBottom: 8 }}>n = {label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, fontFamily: 'JetBrains Mono,monospace', fontSize: 12, color: p.color, marginBottom: 2 }}>
          <span>{p.dataKey}</span>
          <span style={{ color: 'var(--on-surface)' }}>{Number(p.value).toLocaleString()}</span>
        </div>
      ))}
    </div>
  )
}

function Chart({ title, rows, names, log }: { title: string; rows: ChartRow[]; names: string[]; log?: boolean }) {
  return (
    <div style={{ background: 'var(--surface-container-high)', borderRadius: 4, padding: 20, border: '1px solid rgba(83,68,52,0.2)' }}>
      <h3 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 16, color: 'var(--on-surface-variant)' }}>{title}</h3>
      <div style={{ height: 180, borderLeft: '1px solid rgba(83,68,52,0.3)', borderBottom: '1px solid rgba(83,68,52,0.3)' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={rows} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
            <CartesianGrid strokeDasharray="2 4" stroke="rgba(83,68,52,0.2)" />
            <XAxis dataKey="n" tick={{ fill: 'var(--outline)', fontSize: 10, fontFamily: 'JetBrains Mono,monospace' }} axisLine={false} tickLine={false} />
            <YAxis scale={log ? 'log' : 'auto'} domain={log ? ['auto', 'auto'] : [0, 'auto']} tick={{ fill: 'var(--outline)', fontSize: 9, fontFamily: 'JetBrains Mono,monospace' }} axisLine={false} tickLine={false} width={48} />
            <Tooltip content={<Tip />} />
            {names.map((name, i) => (
              <Line key={name} type="monotone" dataKey={name} stroke={PALETTE[i % PALETTE.length]} strokeWidth={2} dot={{ fill: PALETTE[i % PALETTE.length], r: 3, strokeWidth: 0 }} activeDot={{ r: 5 }} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div style={{ display: 'flex', gap: 16, marginTop: 12 }}>
        {names.map((name, i) => (
          <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 16, height: 2, background: PALETTE[i % PALETTE.length], display: 'inline-block', borderRadius: 1 }} />
            <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--outline)' }}>{name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Results() {
  const [searchParams] = useSearchParams()
  const expId = searchParams.get('exp') ?? 'exp_sort'
  const [exp, setExp] = useState<Experiment | null>(null)
  const [results, setResults] = useState<ExperimentResults | null>(null)
  const [running, setRunning] = useState(false)

  const load = useCallback(() => {
    Promise.all([api.getExperiment(expId), api.getResults(expId)]).then(([e, r]) => {
      setExp(e)
      setResults(r)
    })
  }, [expId])

  useEffect(() => {
    load()
  }, [load])

  const run = async () => {
    setRunning(true)
    try {
      await api.runExperiment(expId)
      load()
    } finally {
      setRunning(false)
    }
  }

  const download = async (format: 'csv' | 'json') => {
    const blob = await api.exportExperiment(expId, format)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${expId}.${format}`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!exp || !results) {
    return (
      <main style={{ marginTop: 64, padding: 32, minHeight: 'calc(100vh - 64px)' }} className="bg-grid">
        <div style={{ color: 'var(--outline)', fontFamily: 'JetBrains Mono,monospace', fontSize: 12 }}>načítavam výsledky…</div>
      </main>
    )
  }

  const hasData = results.series.some((s) => s.points.some((p) => p.time_ms_avg > 0))
  if (!hasData) {
    return (
      <main style={{ marginTop: 64, padding: 32, minHeight: 'calc(100vh - 64px)' }} className="bg-grid">
        <div style={{ background: 'var(--surface-container-high)', border: '1px solid rgba(83,68,52,0.2)', borderRadius: 4, padding: 48, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--outline)' }}>bar_chart</span>
          <p style={{ fontFamily: 'Manrope,sans-serif', fontSize: 14, color: 'var(--on-surface-variant)', textAlign: 'center', maxWidth: 480 }}>
            Zatiaľ žiadne výsledky pre „{exp.name}". Spusti experiment — odbehne v sandboxe a vykreslia sa grafy.
          </p>
          <button onClick={run} disabled={running} style={{
            background: 'var(--primary-container)', color: 'var(--on-primary-container)', fontFamily: 'Space Grotesk,sans-serif', fontSize: 13, fontWeight: 700,
            letterSpacing: '0.1em', textTransform: 'uppercase', padding: '12px 28px', border: 'none', borderRadius: 4, cursor: running ? 'wait' : 'pointer',
            opacity: running ? 0.6 : 1, boxShadow: '0 0 15px rgba(245,158,11,0.3)', display: 'flex', alignItems: 'center', gap: 8,
          }}>
            <span className="material-symbols-outlined" style={{ fontSize: 18, fontVariationSettings: "'FILL' 1" }}>{running ? 'hourglass_top' : 'play_arrow'}</span>
            {running ? 'BEŽÍ V SANDBOXE…' : 'SPUSTIŤ EXPERIMENT'}
          </button>
        </div>
      </main>
    )
  }

  const names = results.series.map((s) => s.algorithm_name)
  const totalRuns = exp.algorithm_ids.length * exp.sizes.length * exp.repeats

  return (
    <main style={{ marginTop: 64, padding: 32, width: '100%', minHeight: 'calc(100vh - 64px)' }} className="bg-grid">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 32 }}>
          <div>
            <h2 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 22, fontWeight: 300, letterSpacing: '0.05em', color: 'var(--on-surface)' }}>
              {exp.name} :: Analýza výkonu
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 8 }}>
              <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--outline)' }}>ALGORITMY: {names.length}</span>
              <span style={{ color: 'var(--outline)' }}>·</span>
              <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--outline)' }}>VEĽKOSTI: {exp.sizes.length}</span>
              <span style={{ color: 'var(--outline)' }}>·</span>
              <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--outline)' }}>BEHY: {totalRuns}</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {(['csv', 'json'] as const).map((f) => (
              <button key={f} onClick={() => download(f)} style={{
                display: 'flex', alignItems: 'center', gap: 8, border: '1px solid var(--outline-variant)', color: 'var(--on-surface)',
                fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, padding: '8px 16px', background: 'var(--surface-container-highest)',
                borderRadius: 4, cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.1em',
              }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>download</span>
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Charts */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 24, marginBottom: 24 }}>
          <Chart title="Čas vykonania — ms (log)" rows={buildChart(results, 'time')} names={names} log />
          <Chart title="Počet porovnaní (log)" rows={buildChart(results, 'ops')} names={names} log />
          <Chart title="Pamäť — KB" rows={buildChart(results, 'mem')} names={names} />
        </div>

        {/* Table */}
        <div style={{ background: 'var(--surface-container-high)', borderRadius: 4, border: '1px solid rgba(83,68,52,0.2)', overflow: 'hidden' }}>
          <div style={{ padding: '14px 20px', borderBottom: '1px solid rgba(83,68,52,0.2)', background: 'rgba(50,53,59,0.3)' }}>
            <span style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--on-surface-variant)' }}>
              Porovnanie · čas v ms · min/avg/max z {exp.repeats} opakovaní
            </span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(83,68,52,0.2)', background: 'rgba(0,0,0,0.2)' }}>
                  <th style={TH}>Algoritmus</th>
                  <th style={{ ...TH, textAlign: 'center' }}>Korektnosť</th>
                  {exp.sizes.map((s) => (
                    <th key={s} style={{ ...TH, textAlign: 'center' }} colSpan={3}>n={s.toLocaleString()}</th>
                  ))}
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(83,68,52,0.15)', background: 'rgba(0,0,0,0.1)' }}>
                  <th /><th />
                  {exp.sizes.map((s) => ['min', 'avg', 'max'].map((l) => (
                    <th key={`${s}-${l}`} style={{ padding: '4px 8px', fontFamily: 'JetBrains Mono,monospace', fontSize: 9, color: 'var(--outline)', textAlign: 'center', fontWeight: 400 }}>{l}</th>
                  )))}
                </tr>
              </thead>
              <tbody>
                {results.series.map((s, ri) => (
                  <tr key={s.algorithm_id} style={{ borderBottom: '1px solid rgba(83,68,52,0.1)', background: ri % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)' }}>
                    <td style={{ padding: '12px 20px', fontFamily: 'JetBrains Mono,monospace', fontSize: 13, color: PALETTE[ri % PALETTE.length] }}>{s.algorithm_name}</td>
                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                      {s.is_correct === false ? (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--error)', background: 'rgba(147,0,10,0.15)', padding: '3px 8px', borderRadius: 4 }}>FAIL</span>
                      ) : s.is_correct === null ? (
                        <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--outline)' }}>—</span>
                      ) : (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--tertiary)', background: 'rgba(86,229,169,0.08)', padding: '3px 8px', borderRadius: 4 }}>
                          <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--tertiary)', display: 'inline-block' }} />PASS
                        </span>
                      )}
                    </td>
                    {s.points.map((pt) => [pt.time_ms_min, pt.time_ms_avg, pt.time_ms_max].map((v, k) => (
                      <td key={`${pt.input_size}-${k}`} style={{ padding: '12px 8px', fontFamily: 'JetBrains Mono,monospace', fontSize: 12, color: 'var(--on-surface-variant)', textAlign: 'center' }}>{fmtMs(v)}</td>
                    )))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </motion.div>
    </main>
  )
}

const TH: React.CSSProperties = {
  padding: '10px 16px', textAlign: 'left',
  fontFamily: 'Space Grotesk,sans-serif', fontSize: 10,
  fontWeight: 600, color: 'var(--outline)', letterSpacing: '0.1em', textTransform: 'uppercase',
}

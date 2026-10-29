import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { AlgorithmResultSeries } from '../types'
import { compact, formatMs, formatNumber } from '../lib/labels'

export const seriesColor = (i: number) => `var(--series-${(i % 8) + 1})`

export type Metric = 'operations' | 'time'

function valueOf(p: AlgorithmResultSeries['points'][number], metric: Metric): number | null {
  const v = metric === 'operations' ? p.operation_counts_avg.total : p.time_ms_avg
  return v !== undefined && v !== null && v > 0 ? v : null
}

interface Props {
  series: AlgorithmResultSeries[]
  /** farba podľa poradia algoritmu v experimente, nie podľa poradia v grafe */
  colorIndex: Record<string, number>
  metric: Metric
  log: boolean
}

interface TooltipPayload {
  dataKey: string
  value: number
  color: string
  name: string
}

function ChartTooltip({ active, payload, label, metric }: { active?: boolean; payload?: TooltipPayload[]; label?: number; metric: Metric }) {
  if (!active || !payload?.length) return null
  const rows = [...payload].filter((p) => p.value !== null && p.value !== undefined).sort((a, b) => b.value - a.value)
  return (
    <div className="rounded-[var(--radius)] border border-line bg-surface px-3 py-2 text-[13px] shadow-[var(--shadow-float)]">
      <p className="mb-1 font-medium num">n = {formatNumber(label)}</p>
      {rows.map((p) => (
        <p key={p.dataKey} className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-1.5 text-ink-2">
            <span className="h-0.5 w-3 rounded" style={{ background: p.color }} aria-hidden />{p.name}
          </span>
          <span className="font-medium num">{metric === 'time' ? formatMs(p.value) : formatNumber(p.value)}</span>
        </p>
      ))}
    </div>
  )
}

export function ResultsChart({ series, colorIndex, metric, log }: Props) {
  const sizes = [...new Set(series.flatMap((s) => s.points.map((p) => p.input_size)))].sort((a, b) => a - b)
  const data = sizes.map((n) => {
    const row: Record<string, number | null> = { n }
    for (const s of series) {
      const p = s.points.find((x) => x.input_size === n)
      row[s.algorithm_id] = p ? valueOf(p, metric) : null
    }
    return row
  })
  const hasData = data.some((r) => series.some((s) => r[s.algorithm_id] !== null))
  if (!hasData) return <p className="py-16 text-center text-sm text-ink-3">Zatiaľ nie sú namerané hodnoty.</p>

  return (
    <div className="h-[340px] w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 20, left: 8 }}>
          <CartesianGrid vertical={false} stroke="var(--line)" />
          <XAxis
            dataKey="n" type="number" scale={log ? 'log' : 'linear'} domain={['dataMin', 'dataMax']}
            ticks={sizes} tickFormatter={(v: number) => compact(v)}
            tick={{ fill: 'var(--ink-3)', fontSize: 12 }} axisLine={{ stroke: 'var(--line-strong)' }} tickLine={false}
            label={{ value: 'veľkosť vstupu n', position: 'insideBottom', offset: -12, fill: 'var(--ink-3)', fontSize: 12 }}
          />
          <YAxis
            scale={log ? 'log' : 'linear'} domain={log ? ['auto', 'auto'] : [0, 'auto']} allowDataOverflow={false}
            tickFormatter={(v: number) => (metric === 'time' ? `${compact(v)} ms` : compact(v))}
            tick={{ fill: 'var(--ink-3)', fontSize: 12 }} axisLine={false} tickLine={false} width={64}
          />
          <Tooltip content={<ChartTooltip metric={metric} />} cursor={{ stroke: 'var(--line-strong)' }} />
          {series.map((s) => (
            <Line
              key={s.algorithm_id}
              dataKey={s.algorithm_id}
              name={s.algorithm_name}
              stroke={seriesColor(colorIndex[s.algorithm_id] ?? 0)}
              strokeWidth={2}
              dot={{ r: 4, strokeWidth: 2, stroke: 'var(--surface)', fill: seriesColor(colorIndex[s.algorithm_id] ?? 0) }}
              activeDot={{ r: 6, strokeWidth: 2, stroke: 'var(--surface)' }}
              connectNulls
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export function SeriesLegend({ series, colorIndex }: { series: { algorithm_id: string; algorithm_name: string }[]; colorIndex: Record<string, number> }) {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1.5 text-[13px] text-ink-2" aria-label="Legenda">
      {series.map((s) => (
        <li key={s.algorithm_id} className="flex items-center gap-1.5">
          <span className="h-[3px] w-4 rounded" style={{ background: seriesColor(colorIndex[s.algorithm_id] ?? 0) }} aria-hidden />
          {s.algorithm_name}
        </li>
      ))}
    </ul>
  )
}

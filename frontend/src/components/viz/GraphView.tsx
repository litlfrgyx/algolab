import { useMemo } from 'react'
import type { GraphStep, GraphStructure } from '../../types'
import { roleOf } from './roles'

const W = 560
const H = 380
const R = 15

/** Deterministické rozloženie vrcholov: mriežka, ak graf je mriežka, inak silový model. */
export function layoutGraph(n: number, edges: number[][]): { x: number; y: number }[] {
  const side = Math.round(Math.sqrt(n))
  const isGrid = side * side === n && n >= 4 && edges.every(([u, v]) => {
    const d = Math.abs(u - v)
    return d === side || (d === 1 && Math.floor(u / side) === Math.floor(v / side))
  })
  if (isGrid) {
    const step = Math.min((W - 2 * R - 20) / Math.max(1, side - 1), (H - 2 * R - 20) / Math.max(1, side - 1))
    const ox = (W - step * (side - 1)) / 2
    const oy = (H - step * (side - 1)) / 2
    return Array.from({ length: n }, (_, i) => ({ x: ox + (i % side) * step, y: oy + Math.floor(i / side) * step }))
  }
  // Fruchterman-Reingold so štartom na kružnici, bez náhody
  const pos = Array.from({ length: n }, (_, i) => {
    const a = (2 * Math.PI * i) / Math.max(1, n) - Math.PI / 2
    return { x: W / 2 + Math.cos(a) * (W / 2.6), y: H / 2 + Math.sin(a) * (H / 2.6) }
  })
  if (n <= 2) return pos
  const k = Math.sqrt((W * H) / n) * 0.75
  let t = W / 8
  for (let iter = 0; iter < 300; iter++) {
    const disp = pos.map(() => ({ x: 0, y: 0 }))
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const dx = pos[i].x - pos[j].x
        const dy = pos[i].y - pos[j].y
        const d = Math.max(0.01, Math.hypot(dx, dy))
        const f = (k * k) / d
        disp[i].x += (dx / d) * f; disp[i].y += (dy / d) * f
        disp[j].x -= (dx / d) * f; disp[j].y -= (dy / d) * f
      }
    }
    for (const [u, v] of edges) {
      const dx = pos[u].x - pos[v].x
      const dy = pos[u].y - pos[v].y
      const d = Math.max(0.01, Math.hypot(dx, dy))
      const f = (d * d) / k
      disp[u].x -= (dx / d) * f; disp[u].y -= (dy / d) * f
      disp[v].x += (dx / d) * f; disp[v].y += (dy / d) * f
    }
    for (let i = 0; i < n; i++) {
      // jemná príťažlivosť k stredu, aby nesúvislé komponenty neodleteli
      disp[i].x += (W / 2 - pos[i].x) * 0.02 * k / 10
      disp[i].y += (H / 2 - pos[i].y) * 0.02 * k / 10
      const d = Math.max(0.01, Math.hypot(disp[i].x, disp[i].y))
      pos[i].x += (disp[i].x / d) * Math.min(d, t)
      pos[i].y += (disp[i].y / d) * Math.min(d, t)
    }
    t *= 0.985
  }
  // prispôsobiť plátnu
  const xs = pos.map((p) => p.x)
  const ys = pos.map((p) => p.y)
  const [minX, maxX, minY, maxY] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)]
  const pad = R + 22
  const sx = (W - 2 * pad) / Math.max(1, maxX - minX)
  const sy = (H - 2 * pad) / Math.max(1, maxY - minY)
  const s = Math.min(sx, sy)
  const ox = (W - (maxX - minX) * s) / 2
  const oy = (H - (maxY - minY) * s) / 2
  return pos.map((p) => ({ x: ox + (p.x - minX) * s, y: oy + (p.y - minY) * s }))
}

export function GraphView({ step, structure }: { step: GraphStep; structure: GraphStructure | null }) {
  const n = structure?.n ?? 0
  const edges = useMemo(() => structure?.edges ?? [], [structure])
  const pos = useMemo(() => layoutGraph(n, edges), [n, edges])
  if (!structure) return <p className="text-sm text-ink-3">Algoritmus nezavolal tracker.graph, graf sa nedá nakresliť.</p>

  const edgeRole = new Map(step.edge_roles.map((e) => [`${Math.min(e.u, e.v)}-${Math.max(e.u, e.v)}`, e.role]))
  return (
    <div className="space-y-3">
      <svg viewBox={`0 0 ${W} ${H}`} className="mx-auto block h-auto w-full max-w-[640px]" role="img" aria-label={`Graf s ${n} vrcholmi`}>
        {edges.map(([u, v, w], i) => {
          const role = roleOf(edgeRole.get(`${Math.min(u, v)}-${Math.max(u, v)}`))
          const a = pos[u]
          const b = pos[v]
          if (!a || !b) return null
          return (
            <g key={i}>
              <line
                x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                stroke={role ? role.fill : 'var(--line-strong)'}
                strokeWidth={role ? 3 : 1.5}
                strokeLinecap="round"
                className="transition-[stroke] duration-150"
              />
              {structure.weighted && w !== undefined && (
                <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 4} textAnchor="middle" fontSize="11"
                  fill="var(--ink-2)" stroke="var(--surface)" strokeWidth="3" paintOrder="stroke" className="num">
                  {w}
                </text>
              )}
            </g>
          )
        })}
        {pos.map((p, v) => {
          const r = step.node_roles[String(v)]
          const role = roleOf(r)
          const strong = r === 'active' || r === 'compare'
          const label = step.labels?.[String(v)]
          return (
            <g key={v} className="transition-opacity">
              <circle cx={p.x} cy={p.y} r={R}
                fill={role ? (strong ? role.fill : role.soft) : 'var(--surface)'}
                stroke={role ? role.fill : 'var(--ink-3)'}
                strokeWidth={strong ? 2.5 : 1.5}
              />
              <text x={p.x} y={p.y + 4} textAnchor="middle" fontSize="12" fontWeight="600"
                fill={strong ? 'var(--surface)' : 'var(--ink)'} className="num">{v}</text>
              {label !== undefined && (
                <text x={p.x} y={p.y - R - 5} textAnchor="middle" fontSize="11" fontWeight="600"
                  fill="var(--accent)" stroke="var(--surface)" strokeWidth="3" paintOrder="stroke" className="num">{label}</text>
              )}
            </g>
          )
        })}
      </svg>
      {step.frontier && (
        <div className="flex flex-wrap items-center gap-1.5 text-[13px]">
          <span className="text-ink-2">{step.frontier.name}:</span>
          {step.frontier.items.length === 0 ? (
            <span className="text-ink-3">prázdny</span>
          ) : (
            step.frontier.items.map((x, i) => (
              <span key={i} className="grid h-6 min-w-6 place-items-center rounded bg-surface-2 px-1.5 font-medium num">{x}</span>
            ))
          )}
        </div>
      )}
    </div>
  )
}

import type { TreeNode, TreeStep } from '../../types'
import { roleOf } from './roles'

interface Placed {
  node: TreeNode
  x: number
  depth: number
  parent?: Placed
}

/** Rozloženie stromu: listy a prázdne podstromy dostanú vlastný stĺpec, uzol je nad stredom detí. */
function layout(nodes: TreeNode[], root: string | number | null) {
  const byId = new Map(nodes.map((n) => [String(n.id), n]))
  const placed: Placed[] = []
  let slot = 0
  let maxDepth = 0
  const seen = new Set<string>()

  function place(id: string | number, depth: number, parent?: Placed): number {
    const node = byId.get(String(id))
    if (!node || seen.has(String(id))) return slot++
    seen.add(String(id))
    maxDepth = Math.max(maxDepth, depth)
    const me: Placed = { node, x: 0, depth, parent }
    placed.push(me)
    const kids = node.children ?? []
    const real = kids.filter((c) => c !== null && c !== undefined)
    if (real.length === 0) {
      me.x = slot++
      return me.x
    }
    const xs: number[] = []
    for (const c of kids) {
      if (c === null || c === undefined) {
        // prázdny podstrom v binárnom strome si nechá miesto, aby bolo vidieť ľavý a pravý
        if (kids.length === 2) xs.push(slot++ - 0.25)
      } else {
        xs.push(place(c, depth + 1, me))
      }
    }
    me.x = (Math.min(...xs) + Math.max(...xs)) / 2
    return me.x
  }

  if (root !== null && root !== undefined) place(root, 0)
  return { placed, slots: Math.max(1, slot), depth: maxDepth }
}

export function TreeView({ step }: { step: TreeStep }) {
  const { placed, slots, depth } = layout(step.nodes, step.root)
  const roles = new Map(step.highlights.map((h) => [String(h.id), h.role]))
  if (!placed.length) return <p className="py-10 text-center text-sm text-ink-3">Strom je prázdny.</p>

  const maxLabel = Math.max(...placed.map((p) => p.node.label.length))
  const nodeW = Math.max(30, Math.min(84, maxLabel * 7.5 + 16))
  const colW = Math.max(nodeW + 14, 40)
  const W = Math.max(320, slots * colW + 20)
  const levelH = 62
  const H = (depth + 1) * levelH + 20
  const X = (x: number) => 10 + colW / 2 + x * colW
  const Y = (d: number) => 24 + d * levelH

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', maxWidth: W, minWidth: Math.min(W, 520) }} className="mx-auto block h-auto" role="img" aria-label={`Strom s ${placed.length} uzlami`}>
        {placed.filter((p) => p.parent).map((p) => (
          <line key={`e-${p.node.id}`} x1={X(p.parent!.x)} y1={Y(p.parent!.depth) + 13} x2={X(p.x)} y2={Y(p.depth) - 13}
            stroke="var(--line-strong)" strokeWidth={1.5} />
        ))}
        {placed.map((p) => {
          const r = roles.get(String(p.node.id))
          const role = roleOf(r)
          const strong = r === 'active' || r === 'compare' || r === 'pivot'
          return (
            <g key={String(p.node.id)}>
              <rect x={X(p.x) - nodeW / 2} y={Y(p.depth) - 13} width={nodeW} height={26} rx={13}
                fill={role ? (strong ? role.fill : role.soft) : 'var(--surface)'}
                stroke={role ? role.fill : 'var(--ink-3)'} strokeWidth={strong ? 2 : 1.25}
                className="transition-[fill] duration-150" />
              <text x={X(p.x)} y={Y(p.depth) + 4} textAnchor="middle" fontSize="12" fontWeight="600"
                fill={strong ? 'var(--surface)' : 'var(--ink)'} className="num">{p.node.label}</text>
              {p.node.extra !== undefined && (
                <text x={X(p.x) + nodeW / 2 + 3} y={Y(p.depth) - 10} fontSize="10" fill="var(--ink-3)" className="num">
                  {p.node.extra}
                </text>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}

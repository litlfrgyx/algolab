import type { StringStep } from '../../types'
import { roleOf } from './roles'

/** Text a pod ním vzorka zarovnaná na aktuálny posun. Obe riadky zdieľajú jednu mriežku stĺpcov. */
export function StringView({ step }: { step: StringStep }) {
  const text = [...step.value]
  const pattern = [...(step.pattern ?? '')]
  const roles = new Map(step.highlights.map((h) => [h.index, h.role]))
  const proles = new Map(step.pattern_highlights.map((h) => [h.index, h.role]))
  const cols = Math.max(text.length, step.offset + pattern.length)
  const grid = { gridTemplateColumns: `repeat(${cols}, minmax(14px, 1fr))` }

  const cell = (ch: string, role: string | undefined, key: string, col: number) => {
    const r = roleOf(role)
    return (
      <span
        key={key}
        style={{
          gridColumn: col + 1,
          background: r ? r.fill : 'var(--surface-2)',
          color: r ? 'var(--surface)' : 'var(--ink)',
        }}
        className="grid h-8 max-w-8 place-items-center rounded-[3px] font-mono text-[13px] font-medium transition-colors duration-150"
      >
        {ch}
      </span>
    )
  }

  return (
    <div className="overflow-x-auto pb-1">
      <div className="space-y-1.5" style={{ minWidth: cols * 16 }}>
        <div className="grid gap-[2px]" style={grid}>
          {text.map((_c, i) => (
            <span key={i} style={{ gridColumn: i + 1 }} className="max-w-8 text-center text-[10px] text-ink-3 num">
              {i % 5 === 0 ? i : ''}
            </span>
          ))}
        </div>
        <div className="grid gap-[2px]" style={grid}>
          {text.map((ch, i) => cell(ch, roles.get(i), `t${i}`, i))}
        </div>
        {pattern.length > 0 && (
          <div className="grid gap-[2px]" style={grid}>
            {pattern.map((ch, j) => cell(ch, proles.get(j), `p${j}`, step.offset + j))}
          </div>
        )}
      </div>
    </div>
  )
}

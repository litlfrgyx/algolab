import type { ArrayStep } from '../../types'
import { cellText, roleOf } from './roles'

/** Pole ako stĺpce. Výška zodpovedá hodnote, farba role prvku v danom kroku. */
export function ArrayView({ step }: { step: ArrayStep }) {
  const values = step.array
  const nums = values.map((v) => (typeof v === 'number' && Number.isFinite(v) ? v : null))
  const numeric = nums.filter((v): v is number => v !== null)
  const max = Math.max(1, ...numeric.map((v) => Math.abs(v)))
  const roles = new Map(step.highlights.map((h) => [h.index, h.role]))
  const pointers = new Map<number, string[]>()
  for (const [name, idx] of Object.entries(step.pointers ?? {})) {
    pointers.set(idx, [...(pointers.get(idx) ?? []), name])
  }
  const bars = numeric.length > 0
  const n = values.length
  const gap = n > 40 ? 2 : n > 20 ? 3 : 4
  const showValues = n <= 40

  return (
    <div className="w-full">
      <div className="flex h-[220px] items-end" style={{ gap }}>
        {values.map((v, i) => {
          const role = roleOf(roles.get(i))
          const num = nums[i]
          const boxed = !bars || num === null
          const h = boxed ? 28 : Math.max(4, (Math.abs(num ?? 0) / max) * 200)
          return (
            <div key={i} className="flex min-w-0 flex-1 flex-col items-center justify-end">
              {showValues && !boxed && (
                <span className="mb-1 text-[11px] leading-none text-ink-2 num">{cellText(v)}</span>
              )}
              <div
                className="w-full max-w-[44px] rounded-t-[4px] transition-[height,background-color] duration-200"
                style={{
                  height: h,
                  background: role ? role.fill : 'var(--surface-3)',
                }}
                title={`[${i}] = ${String(v)}`}
              >
                {boxed && (
                  <span className="grid h-full place-items-center text-[12px] font-medium num" style={{ color: role ? 'var(--surface)' : 'var(--ink)' }}>
                    {cellText(v)}
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>
      <div className="mt-1 flex border-t border-line-strong pt-1" style={{ gap }}>
        {values.map((_, i) => (
          <div key={i} className="flex min-w-0 flex-1 flex-col items-center">
            {(n <= 30 || i % 5 === 0) && (
              <span className="text-[10px] leading-tight text-ink-3 num">{step.labels?.[i] ?? i}</span>
            )}
            {pointers.get(i)?.map((name) => (
              <span key={name} className="text-[11px] font-semibold leading-tight text-accent">{name}</span>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

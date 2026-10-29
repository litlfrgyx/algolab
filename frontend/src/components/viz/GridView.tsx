import type { GridStep } from '../../types'
import { cellText, roleOf } from './roles'

/** Tabuľka dynamického programovania. Prázdne bunky ešte nie sú vypočítané. */
export function GridView({ step }: { step: GridStep }) {
  const roles = new Map(step.highlights.map((h) => [`${h.row},${h.col}`, h.role]))
  const cols = step.grid[0]?.length ?? 0
  return (
    <div className="overflow-auto">
      <table className="mx-auto border-separate border-spacing-[3px] text-[13px] num">
        {step.col_labels && (
          <thead>
            <tr>
              {step.row_labels && <th />}
              {step.col_labels.slice(0, cols).map((c, j) => (
                <th key={j} className="h-6 min-w-9 px-1 text-center text-[12px] font-medium text-ink-3">{c}</th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {step.grid.map((row, i) => (
            <tr key={i}>
              {step.row_labels && (
                <th className="pr-2 text-right text-[12px] font-medium text-ink-3">{step.row_labels[i]}</th>
              )}
              {row.map((v, j) => {
                const role = roleOf(roles.get(`${i},${j}`))
                const empty = v === null || v === undefined
                return (
                  <td
                    key={j}
                    title={`[${i}][${j}] = ${empty ? 'nevypočítané' : String(v)}`}
                    className="h-9 min-w-9 rounded-[4px] px-1.5 text-center transition-colors duration-150"
                    style={{
                      background: role ? role.fill : empty ? 'transparent' : 'var(--surface-2)',
                      color: role ? 'var(--surface)' : 'var(--ink)',
                      boxShadow: empty && !role ? 'inset 0 0 0 1px var(--line)' : undefined,
                      fontWeight: role ? 600 : 400,
                    }}
                  >
                    {cellText(v)}
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

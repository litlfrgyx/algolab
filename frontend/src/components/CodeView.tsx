import { cx } from './ui'

/** Ľahké zobrazenie kódu bez editora, s voliteľne zvýrazneným riadkom. */
export function CodeView({ code, activeLine, maxHeight }: { code: string; activeLine?: number; maxHeight?: number }) {
  const lines = code.split('\n')
  return (
    <pre
      className="overflow-auto rounded-[var(--radius)] bg-surface-2 py-2 text-[12.5px] leading-[1.6]"
      style={{ maxHeight }}
    >
      <code className="block min-w-max">
        {lines.map((line, i) => (
          <span
            key={i}
            className={cx('flex pr-4', activeLine === i + 1 && 'bg-accent-soft')}
          >
            <span className="w-10 shrink-0 select-none pr-3 text-right text-ink-3 num">{i + 1}</span>
            <span className="whitespace-pre">{line || ' '}</span>
          </span>
        ))}
      </code>
    </pre>
  )
}

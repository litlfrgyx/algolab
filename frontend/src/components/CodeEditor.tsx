import { lazy, Suspense } from 'react'

const MonacoEditor = lazy(() => import('./MonacoEditor'))

interface EditorProps {
  value: string
  onChange?: (v: string) => void
  readOnly?: boolean
  height?: number | string
  ariaLabel?: string
}

/** Editor kódu. Monaco sa načíta až na stránke, ktorá ho potrebuje. */
export function CodeEditor(props: EditorProps) {
  return (
    <Suspense fallback={<div className="rounded-[var(--radius)] border border-line bg-surface-2 p-4 text-sm text-ink-3" style={{ height: props.height ?? 420 }}>Načítavam editor…</div>}>
      <MonacoEditor {...props} />
    </Suspense>
  )
}

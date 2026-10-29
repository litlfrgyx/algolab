import { useEffect, useState } from 'react'
import Editor, { loader, type BeforeMount } from '@monaco-editor/react'
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api'
import 'monaco-editor/esm/vs/basic-languages/python/python.contribution'
import EditorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'

// Monaco je súčasťou balíka aplikácie, nenačítava sa z CDN (funguje aj bez internetu v učebni).
;(self as unknown as { MonacoEnvironment: unknown }).MonacoEnvironment = { getWorker: () => new EditorWorker() }
loader.config({ monaco })

function usePrefersDark() {
  const [dark, setDark] = useState(() => window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false)
  useEffect(() => {
    const m = window.matchMedia?.('(prefers-color-scheme: dark)')
    if (!m) return
    const on = (e: MediaQueryListEvent) => setDark(e.matches)
    m.addEventListener('change', on)
    return () => m.removeEventListener('change', on)
  }, [])
  return dark
}

const defineThemes: BeforeMount = (monaco) => {
  monaco.editor.defineTheme('algolab-light', {
    base: 'vs',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6b7570', fontStyle: 'italic' },
      { token: 'keyword', foreground: '1f5f8b', fontStyle: 'bold' },
      { token: 'string', foreground: '2c7a4b' },
      { token: 'number', foreground: 'b86e00' },
    ],
    colors: {
      'editor.background': '#fbfbfa',
      'editor.lineHighlightBackground': '#eef1ec',
      'editorLineNumber.foreground': '#9aa39e',
      'editorGutter.background': '#fbfbfa',
      'editor.selectionBackground': '#cfe0ee',
    },
  })
  monaco.editor.defineTheme('algolab-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '8e9893', fontStyle: 'italic' },
      { token: 'keyword', foreground: '6ba7d8', fontStyle: 'bold' },
      { token: 'string', foreground: '7fc79c' },
      { token: 'number', foreground: 'e0a33a' },
    ],
    colors: {
      'editor.background': '#161a18',
      'editor.lineHighlightBackground': '#1f2521',
      'editorLineNumber.foreground': '#5f6a65',
      'editorGutter.background': '#161a18',
      'editor.selectionBackground': '#28435a',
    },
  })
}

interface EditorProps {
  value: string
  onChange?: (v: string) => void
  readOnly?: boolean
  height?: number | string
  ariaLabel?: string
}

export default function MonacoEditor({ value, onChange, readOnly, height = 420, ariaLabel = 'Kód v jazyku Python' }: EditorProps) {
  const dark = usePrefersDark()
  return (
    <div className="overflow-hidden rounded-[var(--radius)] border border-line">
      <Editor
        height={height}
        language="python"
        value={value}
        onChange={(v) => onChange?.(v ?? '')}
        beforeMount={defineThemes}
        theme={dark ? 'algolab-dark' : 'algolab-light'}
        loading={<div className="p-4 text-sm text-ink-3">Načítavam editor…</div>}
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 13,
          fontFamily: '"IBM Plex Mono", ui-monospace, Consolas, monospace',
          lineNumbersMinChars: 3,
          scrollBeyondLastLine: false,
          tabSize: 4,
          insertSpaces: true,
          renderLineHighlight: readOnly ? 'none' : 'line',
          padding: { top: 10, bottom: 10 },
          ariaLabel,
          automaticLayout: true,
          wordWrap: 'off',
        }}
      />
    </div>
  )
}


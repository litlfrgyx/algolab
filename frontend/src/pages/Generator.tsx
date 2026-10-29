import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Editor from '@monaco-editor/react'
import { api } from '../api'
import type { GeneratorPreviewResponse, InputGenerator } from '../types'

const GEN_ID = 'gen_array'
const MODES = [
  { label: 'Random', value: 'random' },
  { label: 'Sorted', value: 'sorted' },
  { label: 'Reverse', value: 'reverse' },
  { label: 'Worst-case', value: 'worst_case' },
]
const sizeLabel = (n: number) => (n >= 1000 ? `${n / 1000}K` : `${n}`)

export default function Generator() {
  const [generator, setGenerator] = useState<InputGenerator | null>(null)
  const [n, setN] = useState(10)
  const [mode, setMode] = useState('random')
  const [seed, setSeed] = useState(42)
  const [preview, setPreview] = useState<GeneratorPreviewResponse | null>(null)

  useEffect(() => {
    api.getGenerator(GEN_ID).then((g) => {
      setGenerator(g)
      if (g.default_sizes.length) setN(g.default_sizes[0])
    })
  }, [])

  useEffect(() => {
    if (!generator) return
    let cancelled = false
    api.previewGenerator(GEN_ID, { n, params: { mode }, seed }).then((p) => {
      if (!cancelled) setPreview(p)
    })
    return () => { cancelled = true }
  }, [generator, n, mode, seed])

  const regenerate = () => setSeed(Math.floor(Math.random() * 100000))

  return (
    <main style={{ marginTop: 64, padding: 24, width: '100%', height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column', gap: 16 }} className="bg-grid">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 8 }}>
          <div>
            <h2 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 22, letterSpacing: '0.05em', textTransform: 'uppercase', fontWeight: 300, color: 'var(--on-surface)' }}>
              Generátor vstupov
            </h2>
            <p style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--secondary)', marginTop: 4 }}>
              {generator?.name ?? 'načítavam…'}
            </p>
          </div>
          <span style={{ display: 'flex', alignItems: 'center', fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--tertiary)' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--tertiary)', display: 'inline-block', marginRight: 6, boxShadow: '0 0 5px var(--tertiary)' }} />
            seed {seed}
          </span>
        </div>
      </motion.div>

      <div style={{ flex: 1, display: 'flex', gap: 16, minHeight: 0 }}>
        {/* Editor */}
        <div style={{ flex: 1, background: 'var(--surface-container-high)', borderRadius: 4, display: 'flex', flexDirection: 'column', border: '1px solid rgba(83,68,52,0.15)', overflow: 'hidden' }}>
          <div style={{ height: 40, background: 'var(--surface-container)', display: 'flex', alignItems: 'center', padding: '0 16px', borderBottom: '1px solid rgba(83,68,52,0.3)', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--primary)' }}>code</span>
              <span style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase' }}>generate(n, **params)</span>
            </div>
            <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--tertiary)' }}>● VALID</span>
          </div>
          <div style={{ flex: 1 }}>
            <Editor height="100%" language="python" value={generator?.code ?? ''} theme="vs-dark"
              options={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, lineHeight: 22, minimap: { enabled: false }, scrollBeyondLastLine: false, padding: { top: 16 } }} />
          </div>
        </div>

        {/* Preview */}
        <div style={{ flex: 1, background: 'var(--surface-container-high)', borderRadius: 4, display: 'flex', flexDirection: 'column', border: '1px solid rgba(83,68,52,0.15)', overflow: 'hidden' }}>
          <div style={{ height: 40, background: 'var(--surface-container)', display: 'flex', alignItems: 'center', padding: '0 16px', borderBottom: '1px solid rgba(245,158,11,0.2)', justifyContent: 'space-between' }}>
            <span style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--secondary)' }}>Živý náhľad</span>
            <button onClick={regenerate} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--outline-variant)' }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>refresh</span>
            </button>
          </div>
          <div style={{ flex: 1, background: 'var(--surface-container-lowest)', padding: 16, fontFamily: 'JetBrains Mono,monospace', fontSize: 13, color: '#d1c5b5', overflowY: 'auto' }}>
            <div style={{ color: 'var(--primary)', marginBottom: 8 }}>n = {n} · {mode}</div>
            <div style={{ wordBreak: 'break-all', lineHeight: 1.8 }}>{preview?.preview ?? '…'}</div>
            <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[['Type', preview?.type ?? '—'], ['Length', String(preview?.length ?? '—')], ['Elapsed', preview ? `${preview.elapsed_ms} ms` : '—']].map(([l, v]) => (
                <div key={l} style={{ display: 'flex', gap: 12 }}>
                  <span style={{ color: 'var(--outline)', minWidth: 60 }}>{l}:</span>
                  <span style={{ color: 'var(--secondary)' }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div style={{ minHeight: 96, background: 'var(--surface-container-high)', borderRadius: 4, border: '1px solid rgba(83,68,52,0.15)', display: 'flex', alignItems: 'center', padding: '16px 24px', gap: 32, flexWrap: 'wrap' }}>
        <button onClick={regenerate} style={{ background: 'var(--primary-container)', color: 'var(--on-primary-container)', fontFamily: 'Space Grotesk,sans-serif', fontSize: 13, fontWeight: 700, padding: '12px 24px', borderRadius: 4, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8, boxShadow: '0 0 15px rgba(245,158,11,0.2)' }}>
          <span className="material-symbols-outlined" style={{ fontSize: 20 }}>bolt</span>
          GENERUJ
        </button>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <label style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 10, color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Veľkosť (N)</label>
          <div style={{ display: 'flex', gap: 8 }}>
            {(generator?.default_sizes ?? []).map((s) => (
              <button key={s} onClick={() => setN(s)} style={{
                fontFamily: 'JetBrains Mono,monospace', fontSize: 12,
                border: `1px solid ${n === s ? 'var(--secondary)' : 'var(--outline-variant)'}`,
                color: n === s ? 'var(--secondary)' : '#d1c5b5',
                background: n === s ? 'rgba(76,215,246,0.08)' : 'none',
                padding: '6px 14px', borderRadius: 4, cursor: 'pointer',
              }}>{sizeLabel(s)}</button>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <label style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 10, color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Rozloženie</label>
          <div style={{ display: 'flex', gap: 8 }}>
            {MODES.map((m) => (
              <button key={m.value} onClick={() => setMode(m.value)} style={{
                fontFamily: 'Space Grotesk,sans-serif', fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase',
                border: `1px solid ${mode === m.value ? 'var(--primary)' : 'var(--outline-variant)'}`,
                color: mode === m.value ? 'var(--primary)' : '#64748b',
                background: 'none', padding: '6px 12px', borderRadius: 4, cursor: 'pointer',
              }}>{m.label}</button>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <label style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 10, color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Seed</label>
          <input type="number" value={seed} onChange={(e) => setSeed(+e.target.value)} style={{ width: 100, background: 'var(--surface-container-low)', border: '1px solid var(--outline-variant)', color: 'var(--on-surface)', borderRadius: 4, padding: '6px 10px', fontFamily: 'JetBrains Mono,monospace', fontSize: 12, outline: 'none' }} />
        </div>
      </div>
    </main>
  )
}

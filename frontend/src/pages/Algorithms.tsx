import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { api } from '../api'
import type { Algorithm } from '../types'

const PROBLEM_ID = 'prob_sorting'

function InfoCell({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ background: 'var(--surface-container)', padding: 8, borderRadius: 4 }}>
      <span style={{ display: 'block', fontFamily: 'JetBrains Mono,monospace', fontSize: 9, textTransform: 'uppercase', letterSpacing: '0.12em', color: 'var(--outline)', marginBottom: 4 }}>{label}</span>
      <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 12, color: color ?? 'var(--secondary)' }}>{value}</span>
    </div>
  )
}

export default function Algorithms() {
  const navigate = useNavigate()
  const [algos, setAlgos] = useState<Algorithm[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)

  useEffect(() => {
    api.listAlgorithms(PROBLEM_ID).then((list) => {
      setAlgos(list)
      if (list.length) setActiveId(list[0].id)
    })
  }, [])

  const selected = algos.find((a) => a.id === activeId) ?? null
  const lines = selected ? selected.code.split('\n').length : 0

  return (
    <div style={{ marginLeft: 0, marginTop: 64, height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* File list sidebar */}
        <aside style={{ width: 280, background: 'var(--surface-container-low)', display: 'flex', flexDirection: 'column', boxShadow: '1px 0 15px rgba(0,0,0,0.5)', zIndex: 20 }}>
          <div style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(83,68,52,0.1)' }}>
            <h2 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, color: 'var(--on-surface-variant)', textTransform: 'uppercase', letterSpacing: '0.2em' }}>Algoritmy problému</h2>
            <button style={{ background: 'none', border: 'none', color: 'var(--outline-variant)', cursor: 'pointer' }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>add</span>
            </button>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: 8 }}>
            <div style={{ padding: '8px 12px', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--outline)', fontSize: 10, fontFamily: 'JetBrains Mono,monospace', letterSpacing: '0.1em', textTransform: 'uppercase', marginTop: 8 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 14 }}>folder_open</span> Comparison Sort
            </div>
            {algos.map((a) => (
              <div key={a.id} onClick={() => setActiveId(a.id)} style={{
                padding: '8px 12px', borderRadius: 2, cursor: 'pointer', marginBottom: 4,
                background: activeId === a.id ? 'var(--surface-container-high)' : 'transparent',
                borderLeft: activeId === a.id ? '1px solid var(--primary)' : '1px solid transparent',
                boxShadow: activeId === a.id ? '0 0 10px rgba(245,158,11,0.1)' : 'none',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 13, color: activeId === a.id ? 'var(--primary)' : 'var(--on-surface)' }}>{a.name}</span>
                  {a.is_reference && <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 8, color: 'var(--tertiary)', border: '1px solid var(--tertiary)', borderRadius: 2, padding: '1px 4px' }}>REF</span>}
                </div>
                <span style={{ fontFamily: 'Manrope,sans-serif', fontSize: 10, color: 'var(--outline-variant)', marginTop: 4, display: 'block' }}>
                  {a.supports_visualization ? 'vizualizovateľný' : 'len benchmark'}
                </span>
              </div>
            ))}
          </div>
        </aside>

        {/* Editor */}
        <section style={{ flex: 1, background: 'var(--surface-container-lowest)', display: 'flex', flexDirection: 'column' }}>
          <div style={{ height: 40, background: 'var(--surface-container)', display: 'flex', alignItems: 'flex-end', padding: '0 8px', gap: 4, borderBottom: '1px solid rgba(83,68,52,0.1)' }}>
            <div style={{ background: 'var(--surface-container-lowest)', padding: '8px 16px', borderTop: '1px solid rgba(245,158,11,0.5)', color: 'var(--primary)', fontFamily: 'JetBrains Mono,monospace', fontSize: 12, display: 'flex', alignItems: 'center', gap: 8, borderRadius: '4px 4px 0 0' }}>
              <span className="material-symbols-outlined" style={{ fontSize: 14, fontVariationSettings: "'FILL' 1" }}>description</span>
              {selected?.name ?? '—'}
            </div>
          </div>
          <div style={{ flex: 1 }}>
            <Editor height="100%" language="python" path={selected?.id} value={selected?.code ?? ''} theme="vs-dark"
              options={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, lineHeight: 22, minimap: { enabled: false }, scrollBeyondLastLine: false, padding: { top: 16 }, renderLineHighlight: 'line' }} />
          </div>
        </section>

        {/* Inspector panel */}
        <aside style={{ width: 320, background: 'var(--surface-container-low)', borderLeft: '1px solid rgba(83,68,52,0.15)', display: 'flex', flexDirection: 'column', boxShadow: '-1px 0 15px rgba(0,0,0,0.3)', zIndex: 20 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid rgba(83,68,52,0.1)' }}>
            <h2 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, color: 'var(--on-surface-variant)', textTransform: 'uppercase', letterSpacing: '0.2em', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>info</span>
              Inšpektor modulu
            </h2>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: 20, display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div style={{ background: 'var(--surface-container-high)', borderRadius: 4, padding: 16, border: '1px solid rgba(83,68,52,0.2)' }}>
              <h3 style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 13, color: 'var(--primary)', marginBottom: 12 }}>{selected?.name ?? '—'}</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <InfoCell label="Jazyk" value={selected?.language ?? '—'} />
                <InfoCell label="Riadkov" value={String(lines)} />
                <InfoCell label="Referenčný" value={selected?.is_reference ? 'Áno' : 'Nie'} color={selected?.is_reference ? 'var(--tertiary)' : 'var(--outline)'} />
                <InfoCell label="Vizualizácia" value={selected?.supports_visualization ? 'Áno' : 'Nie'} color={selected?.supports_visualization ? 'var(--tertiary)' : 'var(--outline)'} />
              </div>
            </div>
            <button onClick={() => navigate('/visualizer')} disabled={!selected?.supports_visualization} style={{
              width: '100%', background: 'var(--primary-container)', color: 'var(--on-primary-container)',
              fontFamily: 'Space Grotesk,sans-serif', fontWeight: 700, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.12em',
              padding: '12px 16px', borderRadius: 4, border: 'none', cursor: selected?.supports_visualization ? 'pointer' : 'not-allowed',
              opacity: selected?.supports_visualization ? 1 : 0.4, boxShadow: '0 0 15px rgba(245,158,11,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: 18, fontVariationSettings: "'FILL' 1" }}>play_circle</span>
              SPUSTIŤ VIZUALIZÉR
            </button>
          </div>
        </aside>
      </div>

      {/* Status bar */}
      <footer style={{ height: 32, background: 'var(--surface-container-highest)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', borderTop: '1px solid rgba(83,68,52,0.2)', fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--outline)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--tertiary)' }} />
          <span style={{ color: 'var(--tertiary)' }}>Python · def solve(data, tracker)</span>
        </div>
        <span>{algos.length} algoritmov · {lines} riadkov</span>
      </footer>
    </div>
  )
}

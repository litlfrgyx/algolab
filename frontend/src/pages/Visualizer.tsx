import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { api } from '../api'
import type { ArrayStep, HighlightRole, VisualizationTrace } from '../types'
import { ROLE_COLOR } from '../types'

// Vizualizácia beží len pre malé n; väčšie vstupy patria do benchmarku.
const MAX_VIZ_N = 60
const DEFAULT = [5, 3, 1, 4, 2]

const TYPE_COLOR: Record<string, string> = {
  compare: 'var(--secondary)',
  swap: 'var(--primary)',
  pivot: '#a78bfa',
  sorted: 'var(--tertiary)',
  done: 'var(--tertiary)',
}
const typeColor = (t: string) => TYPE_COLOR[t] ?? 'var(--outline)'

function AlgoPanel({
  trace,
  step,
  accent,
}: {
  trace: VisualizationTrace
  step: number
  accent: string
}) {
  const steps = trace.steps as ArrayStep[]
  const s = steps[Math.min(step, steps.length - 1)]
  const baseVals = steps[0]?.array ?? []
  const maxVal = Math.max(...baseVals.map((v) => Math.abs(v)), 1)
  const tlRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    tlRef.current
      ?.querySelector('[data-active=true]')
      ?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }, [step])

  const roleByIndex = new Map<number, HighlightRole>()
  s.highlights.forEach((h) => roleByIndex.set(h.index, h.role))
  const pointerByIndex = new Map<number, string[]>()
  if (s.pointers)
    for (const [name, idx] of Object.entries(s.pointers)) {
      const list = pointerByIndex.get(idx) ?? []
      list.push(name)
      pointerByIndex.set(idx, list)
    }

  const compares = trace.operation_counts.compare ?? 0
  const swaps = trace.operation_counts.swap ?? 0

  return (
    <div style={{ background: 'var(--surface-container-high)', borderRadius: 4, display: 'flex', flexDirection: 'column', border: '1px solid rgba(83,68,52,0.15)', overflow: 'hidden', flex: 1 }}>
      {/* Header */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(83,68,52,0.2)', background: 'var(--surface-container-highest)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--on-surface)' }}>{trace.algorithm_name}</span>
        <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--outline)', display: 'flex', gap: 12 }}>
          <span><span style={{ color: 'var(--secondary)' }}>{compares}</span> porovnaní</span>
          <span><span style={{ color: 'var(--primary)' }}>{swaps}</span> výmen</span>
        </span>
      </div>

      {/* Bars */}
      <div style={{ flex: 1, padding: 16, display: 'flex', alignItems: 'flex-end', gap: 3, justifyContent: 'center', background: 'var(--surface-container-lowest)', minHeight: 140, maxHeight: 220 }}>
        {s.array.map((val, i) => {
          const role = roleByIndex.get(i)
          const color = role ? ROLE_COLOR[role] : 'var(--surface-variant)'
          const active = role !== undefined
          const h = Math.max(8, (Math.abs(val) / maxVal) * 100)
          const names = pointerByIndex.get(i)
          return (
            <motion.div key={i} layout transition={{ type: 'spring', stiffness: 500, damping: 35 }} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, minWidth: 0 }}>
              {active && <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 9, color: accent }}>{val}</span>}
              <motion.div
                animate={{ height: `${h}%` }}
                transition={{ duration: 0.2 }}
                style={{
                  width: '100%', minHeight: 6, borderRadius: '2px 2px 0 0',
                  background: active ? `${color}` : 'var(--surface-variant)',
                  opacity: active ? 0.9 : 0.5,
                  boxShadow: active ? `0 0 8px ${color}80` : 'none',
                }}
              />
              {names && (
                <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 9, color: 'var(--outline)' }}>{names.join(',')}</span>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Event + code line */}
      <div style={{ padding: '8px 16px', background: 'var(--surface-container-low)', borderTop: '1px solid rgba(83,68,52,0.15)', borderBottom: '1px solid rgba(83,68,52,0.15)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--on-surface-variant)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 5, height: 5, borderRadius: '50%', background: typeColor(s.type), boxShadow: `0 0 4px ${typeColor(s.type)}`, display: 'inline-block', flexShrink: 0 }} />
          {s.label}
        </span>
        {s.code_line !== undefined && (
          <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--outline)' }}>riadok {s.code_line}</span>
        )}
      </div>

      {/* Timeline */}
      <div ref={tlRef} style={{ height: 100, overflowY: 'auto', background: 'var(--surface-container-lowest)' }}>
        {steps.slice(0, Math.min(step + 1, steps.length)).map((st, i) => (
          <div key={i} data-active={i === step} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '3px 16px', borderLeft: `2px solid ${i === step ? accent : 'transparent'}`, background: i === step ? `${accent}14` : 'transparent' }}>
            <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 9, color: 'var(--outline)', minWidth: 20, textAlign: 'right' }}>{i + 1}</span>
            <span style={{ width: 4, height: 4, borderRadius: '50%', background: typeColor(st.type), flexShrink: 0 }} />
            <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: i === step ? accent : 'var(--outline)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{st.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Visualizer() {
  const [inputText, setInputText] = useState('5, 3, 1, 4, 2')
  const [arr, setArr] = useState<number[]>(DEFAULT)
  const [bTrace, setBTrace] = useState<VisualizationTrace | null>(null)
  const [qTrace, setQTrace] = useState<VisualizationTrace | null>(null)
  const [step, setStep] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [loading, setLoading] = useState(true)
  const [note, setNote] = useState<string | null>(null)

  // Načítaj stopy z dátovej vrstvy pri zmene vstupu (kontrakt VisualizationTrace).
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    Promise.all([
      api.visualize({ algorithm_id: 'alg_bubble', input: arr, max_steps: 4000 }),
      api.visualize({ algorithm_id: 'alg_quick', input: arr, max_steps: 4000 }),
    ]).then(([b, q]) => {
      if (cancelled) return
      setBTrace(b)
      setQTrace(q)
      setStep(0)
      setPlaying(false)
      setLoading(false)
    })
    return () => {
      cancelled = true
    }
  }, [arr])

  const maxSteps = Math.max(bTrace?.steps.length ?? 1, qTrace?.steps.length ?? 1)

  useEffect(() => {
    if (!playing) return
    if (step >= maxSteps - 1) {
      setPlaying(false)
      return
    }
    const id = setInterval(
      () =>
        setStep((s) => {
          if (s >= maxSteps - 1) {
            setPlaying(false)
            return s
          }
          return s + 1
        }),
      900 / speed,
    )
    return () => clearInterval(id)
  }, [playing, speed, maxSteps, step])

  const commit = (values: number[]) => {
    if (values.length > MAX_VIZ_N) {
      setNote(`Vstup orezaný na ${MAX_VIZ_N} prvkov — vizualizácia je pre malé n; pre väčšie použi benchmark.`)
      setArr(values.slice(0, MAX_VIZ_N))
    } else {
      setNote(null)
      setArr(values)
    }
  }

  const load = () => {
    const parsed = inputText
      .split(',')
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !isNaN(n))
    if (parsed.length >= 2) commit(parsed)
  }
  const rand = () => {
    const r = Array.from({ length: 9 }, () => Math.floor(Math.random() * 85) + 8)
    setInputText(r.join(', '))
    commit(r)
  }

  const pct = (Math.min(step + 1, maxSteps) / maxSteps) * 100

  return (
    <main style={{ marginTop: 64, padding: 32, height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }} className="bg-grid">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24, flexShrink: 0 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--tertiary)', display: 'inline-block' }} />
            <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--tertiary)', letterSpacing: '0.15em' }}>STEP-BY-STEP VISUALIZER</span>
          </div>
          <h1 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 24, fontWeight: 300, letterSpacing: '0.05em', color: 'var(--on-surface)', textTransform: 'uppercase' }}>
            Porovnávacia vizualizácia
          </h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 12, color: 'var(--outline)' }}>Vstup:</span>
          <input type="text" value={inputText} onChange={(e) => setInputText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && load()}
            style={{ width: 200, background: 'var(--surface-container-low)', border: '1px solid rgba(83,68,52,0.4)', color: 'var(--on-surface)', borderRadius: 4, padding: '6px 12px', fontFamily: 'JetBrains Mono,monospace', fontSize: 12, outline: 'none' }} />
          <button onClick={rand} style={{ background: 'var(--surface-variant)', border: '1px solid var(--outline-variant)', color: 'var(--on-surface)', fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, padding: '6px 14px', borderRadius: 4, cursor: 'pointer', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Náhodný</button>
          <button onClick={load} style={{ background: 'var(--primary-container)', color: 'var(--on-primary-container)', fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, fontWeight: 700, padding: '6px 14px', borderRadius: 4, border: 'none', cursor: 'pointer', letterSpacing: '0.08em', textTransform: 'uppercase', boxShadow: '0 0 10px rgba(245,158,11,0.2)' }}>Načítať</button>
        </div>
      </div>

      {note && (
        <div style={{ marginBottom: 12, fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--primary)', flexShrink: 0 }}>⚠ {note}</div>
      )}

      {/* Panels */}
      <div style={{ flex: 1, display: 'flex', gap: 24, minHeight: 0, marginBottom: 16 }}>
        {loading || !bTrace || !qTrace ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--outline)', fontFamily: 'JetBrains Mono,monospace', fontSize: 12 }}>načítavam stopy…</div>
        ) : (
          <>
            <AlgoPanel trace={bTrace} step={step} accent="#ffc174" />
            <AlgoPanel trace={qTrace} step={step} accent="#4cd7f6" />
          </>
        )}
      </div>

      {/* Controls */}
      <div style={{ background: 'rgba(54,57,63,0.6)', backdropFilter: 'blur(20px)', border: '1px solid rgba(83,68,52,0.2)', borderRadius: 4, padding: '16px 24px', display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
        <button onClick={() => setPlaying((p) => !p)} style={{ width: 44, height: 44, borderRadius: '50%', border: 'none', cursor: 'pointer', background: 'var(--primary-container)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 12px rgba(245,158,11,0.3)', flexShrink: 0 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 28, fontVariationSettings: "'FILL' 1", color: 'var(--on-primary-container)' }}>
            {playing ? 'pause' : 'play_arrow'}
          </span>
        </button>

        {[
          { icon: 'skip_previous', action: () => { setStep(0); setPlaying(false) } },
          { icon: 'step_over', action: () => setStep((s) => Math.max(0, s - 1)) },
          { icon: 'step_into', action: () => setStep((s) => Math.min(maxSteps - 1, s + 1)) },
          { icon: 'skip_next', action: () => { setStep(maxSteps - 1); setPlaying(false) } },
        ].map((b) => (
          <button key={b.icon} onClick={b.action} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--outline-variant)', display: 'flex', alignItems: 'center' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 22 }}>{b.icon}</span>
          </button>
        ))}

        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 12, padding: '0 8px' }}>
          <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--on-surface-variant)', minWidth: 64 }}>Krok {Math.min(step + 1, maxSteps)}</span>
          <div style={{ flex: 1, height: 6, background: 'var(--surface-container-highest)', borderRadius: 4, overflow: 'hidden', position: 'relative' }}>
            <motion.div animate={{ width: `${pct}%` }} transition={{ duration: 0.1 }} style={{ height: '100%', background: 'linear-gradient(90deg, #4cd7f6, #ffc174)', borderRadius: 4 }} />
          </div>
          <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--outline)', minWidth: 36 }}>/ {maxSteps}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 10, color: 'var(--outline)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>Rýchlosť</span>
          <input type="range" min={0.25} max={4} step={0.25} value={speed} onChange={(e) => setSpeed(+e.target.value)} style={{ width: 80, accentColor: 'var(--primary)', cursor: 'pointer' }} />
          <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--primary)', minWidth: 28 }}>{speed}×</span>
        </div>
      </div>
    </main>
  )
}

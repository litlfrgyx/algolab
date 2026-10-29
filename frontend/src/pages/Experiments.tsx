import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '../api'
import type { Algorithm, Experiment } from '../types'

const MODE_LABEL: Record<string, string> = {
  random: 'Náhodný',
  sorted: 'Zotriedený',
  reverse: 'Inverzný',
  worst_case: 'Najhorší',
}

const STATUS_META: Record<string, { label: string; color: string }> = {
  pending: { label: 'Pripravený', color: 'var(--outline)' },
  running: { label: 'Beží', color: 'var(--primary)' },
  done: { label: 'Dokončený', color: 'var(--tertiary)' },
  failed: { label: 'Zlyhal', color: 'var(--error)' },
  cancelled: { label: 'Zrušený', color: 'var(--outline)' },
}

const container = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } }
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }

export default function Experiments() {
  const navigate = useNavigate()
  const [experiments, setExperiments] = useState<Experiment[] | null>(null)
  const [names, setNames] = useState<Record<string, string>>({})
  const [runningId, setRunningId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api
      .listExperiments()
      .then((exps) => {
        setExperiments(exps)
        return api.listAlgorithms('prob_sorting')
      })
      .then((algos: Algorithm[]) =>
        setNames(Object.fromEntries(algos.map((a) => [a.id, a.name]))),
      )
      .catch((err) => setError(String(err.message ?? err)))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const run = async (id: string) => {
    setRunningId(id)
    setError(null)
    try {
      await api.runExperiment(id)
      load()
    } catch (err) {
      setError(String((err as Error).message ?? err))
    } finally {
      setRunningId(null)
    }
  }

  if (error) {
    return (
      <main style={{ marginTop: 64, padding: 32, minHeight: 'calc(100vh - 64px)' }} className="bg-grid">
        <div style={{ color: 'var(--error)', fontFamily: 'JetBrains Mono,monospace', fontSize: 12 }}>
          Chyba: {error}
          <div style={{ color: 'var(--outline)', marginTop: 8 }}>Beží backend na http://localhost:8000? (pozri docs/RUN.md)</div>
        </div>
      </main>
    )
  }

  return (
    <main style={{ marginTop: 64, padding: 32, minHeight: 'calc(100vh - 64px)' }} className="bg-grid">
      <motion.div variants={container} initial="hidden" animate="show">
        {/* Header */}
        <motion.div variants={item} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderBottom: '1px solid rgba(83,68,52,0.2)', paddingBottom: 16, marginBottom: 32 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--tertiary)', display: 'inline-block' }} />
              <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--tertiary)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
                {experiments ? `${experiments.length} experimentov` : 'načítavam…'}
              </span>
            </div>
            <h2 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 28, fontWeight: 300, letterSpacing: '0.05em', color: 'var(--on-surface)' }}>Experimenty</h2>
          </div>
        </motion.div>

        {/* Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(440px, 1fr))', gap: 24 }}>
          {(experiments ?? []).map((exp) => {
            const status = STATUS_META[exp.status] ?? STATUS_META.pending
            const isRunning = runningId === exp.id
            const isDone = exp.status === 'done'
            const mode = String(exp.generator_params?.mode ?? 'random')
            const totalRuns = exp.algorithm_ids.length * exp.sizes.length * exp.repeats
            return (
              <motion.div key={exp.id} variants={item} style={{ background: 'var(--surface-container-high)', border: '1px solid rgba(83,68,52,0.2)', borderRadius: 4, padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <h3 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 17, letterSpacing: '0.02em', color: 'var(--on-surface)' }}>{exp.name}</h3>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: status.color, border: `1px solid ${status.color}`, borderRadius: 4, padding: '2px 8px', whiteSpace: 'nowrap' }}>
                    <span style={{ width: 5, height: 5, borderRadius: '50%', background: status.color, display: 'inline-block' }} />
                    {status.label}
                  </span>
                </div>

                {/* algoritmy */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {exp.algorithm_ids.map((id) => (
                    <span key={id} style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--secondary)', background: 'var(--surface-container-lowest)', border: '1px solid rgba(83,68,52,0.3)', borderRadius: 4, padding: '3px 8px' }}>{names[id] ?? id}</span>
                  ))}
                </div>

                {/* config */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--outline)' }}>
                  <span>vstup: <span style={{ color: 'var(--on-surface-variant)' }}>{MODE_LABEL[mode] ?? mode}</span></span>
                  <span>veľkosti: <span style={{ color: 'var(--on-surface-variant)' }}>{exp.sizes.join(', ')}</span></span>
                  <span>opakovania: <span style={{ color: 'var(--on-surface-variant)' }}>{exp.repeats}</span></span>
                  <span>behy: <span style={{ color: 'var(--on-surface-variant)' }}>{totalRuns}</span></span>
                </div>

                {/* actions */}
                <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                  <button onClick={() => run(exp.id)} disabled={isRunning} style={{
                    flex: 1, background: 'var(--primary-container)', color: 'var(--on-primary-container)', fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, fontWeight: 700,
                    letterSpacing: '0.1em', textTransform: 'uppercase', padding: '10px', border: 'none', borderRadius: 4, cursor: isRunning ? 'wait' : 'pointer',
                    opacity: isRunning ? 0.6 : 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 16, fontVariationSettings: "'FILL' 1" }}>{isRunning ? 'hourglass_top' : isDone ? 'replay' : 'play_arrow'}</span>
                    {isRunning ? 'beží…' : isDone ? 'Spustiť znova' : 'Spustiť'}
                  </button>
                  <button onClick={() => navigate(`/results?exp=${exp.id}`)} disabled={!isDone} style={{
                    flex: 1, background: 'var(--surface-container-lowest)', border: `1px solid ${isDone ? 'var(--outline-variant)' : 'rgba(83,68,52,0.3)'}`, color: isDone ? 'var(--on-surface)' : 'var(--outline)',
                    fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, padding: '10px', borderRadius: 4, letterSpacing: '0.1em', textTransform: 'uppercase', cursor: isDone ? 'pointer' : 'not-allowed',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>analytics</span>
                    Výsledky
                  </button>
                </div>
              </motion.div>
            )
          })}
        </div>
      </motion.div>
    </main>
  )
}

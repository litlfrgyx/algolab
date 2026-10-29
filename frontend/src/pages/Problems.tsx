import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { api } from '../api'
import type { Problem, ProblemCategory } from '../types'

const CATEGORY_META: Record<ProblemCategory, { label: string; color: string; icon: string }> = {
  sorting: { label: 'Sorting', color: '#f59e0b', icon: 'swap_vert' },
  searching: { label: 'Searching', color: '#4cd7f6', icon: 'search' },
  divide_and_conquer: { label: 'Divide & Conquer', color: '#a78bfa', icon: 'call_split' },
  string: { label: 'String', color: '#a78bfa', icon: 'sort_by_alpha' },
  dynamic_programming: { label: 'Dynamic Programming', color: '#34d399', icon: 'grid_view' },
  matrix: { label: 'Matrix', color: '#34d399', icon: 'grid_on' },
  backtracking: { label: 'Backtracking', color: '#f472b6', icon: 'route' },
  greedy: { label: 'Greedy', color: '#fbbf24', icon: 'bolt' },
  graph: { label: 'Graph', color: '#4cd7f6', icon: 'polyline' },
  recursive: { label: 'Recursive', color: '#94a3b8', icon: 'repeat' },
}

interface Row {
  p: Problem
  algos: number
  gens: number
}

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } }
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.3 } } }

export default function Problems() {
  const [rows, setRows] = useState<Row[] | null>(null)

  useEffect(() => {
    api.listProblems().then(async (ps) => {
      const withCounts = await Promise.all(
        ps.map(async (p) => ({
          p,
          algos: (await api.listAlgorithms(p.id)).length,
          gens: (await api.listGenerators(p.id)).length,
        })),
      )
      setRows(withCounts)
    })
  }, [])

  return (
    <main style={{ marginTop: 64, padding: 32, minHeight: 'calc(100vh - 64px)' }} className="bg-grid">
      <motion.div variants={container} initial="hidden" animate="show">
        {/* Header */}
        <motion.div variants={item} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderBottom: '1px solid rgba(83,68,52,0.2)', paddingBottom: 16, marginBottom: 32 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--tertiary)', display: 'inline-block' }} />
              <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 10, color: 'var(--tertiary)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>{rows ? `${rows.length} problémov` : 'načítavam…'}</span>
            </div>
            <h2 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 28, fontWeight: 300, letterSpacing: '0.05em', color: 'var(--on-surface)' }}>
              Knižnica problémov
            </h2>
          </div>
          <button style={{
            display: 'flex', alignItems: 'center', gap: 8, background: 'var(--surface-container-high)', border: '1px solid rgba(83,68,52,0.5)',
            color: 'var(--on-surface)', fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, padding: '8px 16px', borderRadius: 4, cursor: 'pointer', letterSpacing: '0.12em', textTransform: 'uppercase',
          }}>
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>add</span>
            Nový problém
          </button>
        </motion.div>

        {/* Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))', gap: 24 }}>
          {(rows ?? []).map(({ p, algos, gens }) => {
            const meta = CATEGORY_META[p.category]
            return (
              <motion.div key={p.id} variants={item} style={{ background: 'var(--surface-container-high)', border: '1px solid rgba(83,68,52,0.2)', borderRadius: 4, padding: 24, transition: 'all 0.3s' }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'rgba(245,158,11,0.4)'; e.currentTarget.style.boxShadow = '0 0 12px rgba(245,158,11,0.2)' }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'rgba(83,68,52,0.2)'; e.currentTarget.style.boxShadow = 'none' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--on-surface-variant)', background: 'var(--surface-container-lowest)', padding: '4px 8px', border: '1px solid rgba(83,68,52,0.3)' }}>{p.id}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: meta.color, display: 'inline-block' }} />
                      <span style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.12em', color: meta.color }}>{meta.label}</span>
                    </div>
                  </div>
                  <span className="material-symbols-outlined" style={{ fontSize: 20, color: 'rgba(209,193,173,0.4)' }}>{meta.icon}</span>
                </div>

                <h3 style={{ fontFamily: 'Space Grotesk,sans-serif', fontSize: 18, letterSpacing: '0.03em', color: 'var(--on-surface)', marginBottom: 8 }}>{p.name}</h3>
                <p style={{ fontFamily: 'Manrope,sans-serif', fontSize: 13, color: 'rgba(209,193,173,0.7)', lineHeight: 1.6, marginBottom: 16, minHeight: 42 }}>{p.description}</p>

                <div style={{ display: 'flex', gap: 16, marginBottom: 20, fontFamily: 'JetBrains Mono,monospace', fontSize: 11, color: 'var(--outline)' }}>
                  <span><span style={{ color: 'var(--secondary)' }}>{algos}</span> algoritmov</span>
                  <span><span style={{ color: 'var(--secondary)' }}>{gens}</span> generátorov</span>
                </div>

                <div style={{ display: 'flex', gap: 12 }}>
                  <button style={{ flex: 1, background: 'var(--surface-container-lowest)', border: '1px solid rgba(83,68,52,0.5)', color: 'var(--on-surface)', fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, padding: '8px', borderRadius: 4, letterSpacing: '0.12em', textTransform: 'uppercase', cursor: 'pointer' }}>Detail</button>
                  <button style={{ flex: 1, background: 'var(--surface-variant)', border: '1px solid transparent', color: 'var(--on-surface)', fontFamily: 'Space Grotesk,sans-serif', fontSize: 11, padding: '8px', borderRadius: 4, letterSpacing: '0.12em', textTransform: 'uppercase', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>add_circle</span>
                    Algoritmus
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

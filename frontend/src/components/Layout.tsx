import { Suspense, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { BookOpen, Code2, FlaskConical, LibraryBig, Lock, LockOpen, Menu, PlayCircle, X } from 'lucide-react'
import { useEditAuth } from '../lib/auth'
import { Button, Input, cx } from './ui'

const NAV = [
  { to: '/', label: 'Úlohy', icon: LibraryBig, end: true },
  { to: '/algorithms', label: 'Algoritmy', icon: Code2 },
  { to: '/visualizer', label: 'Vizualizácia', icon: PlayCircle },
  { to: '/experiments', label: 'Experimenty', icon: FlaskConical },
  { to: '/guide', label: 'Príručka', icon: BookOpen },
]

/** Značka: štyri stĺpce, ktoré sa práve zoradili. */
export function Mark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden>
      <rect x="2" y="14" width="4" height="8" rx="1" fill="var(--accent)" opacity="0.45" />
      <rect x="7.5" y="10" width="4" height="12" rx="1" fill="var(--accent)" opacity="0.65" />
      <rect x="13" y="6" width="4" height="16" rx="1" fill="var(--accent)" opacity="0.85" />
      <rect x="18.5" y="2" width="4" height="20" rx="1" fill="var(--accent)" />
    </svg>
  )
}

function EditLock() {
  const { protectedMode, canEdit, unlock, lock } = useEditAuth()
  const [open, setOpen] = useState(false)
  const [value, setValue] = useState('')
  if (!protectedMode) return null
  if (canEdit) {
    return (
      <div className="flex items-center justify-between gap-2 px-2 text-[13px] text-ink-2">
        <span className="flex items-center gap-2"><LockOpen className="size-4 text-ok" aria-hidden />Úpravy odomknuté</span>
        <button className="text-ink-3 hover:text-ink underline cursor-pointer" onClick={lock}>Zamknúť</button>
      </div>
    )
  }
  return (
    <div className="px-2 text-[13px]">
      {!open ? (
        <button onClick={() => setOpen(true)} className="flex items-center gap-2 text-ink-2 hover:text-ink cursor-pointer">
          <Lock className="size-4" aria-hidden />Odomknúť úpravy
        </button>
      ) : (
        <form
          className="space-y-2"
          onSubmit={(e) => {
            e.preventDefault()
            unlock(value)
            setOpen(false)
            setValue('')
          }}
        >
          <label className="block text-ink-2" htmlFor="edit-pw">Heslo na vlastný kód</label>
          <Input id="edit-pw" type="password" autoFocus value={value} onChange={(e) => setValue(e.target.value)} className="w-full" />
          <div className="flex gap-2">
            <Button size="sm" variant="primary" type="submit" disabled={!value}>Odomknúť</Button>
            <Button size="sm" variant="ghost" type="button" onClick={() => setOpen(false)}>Zrušiť</Button>
          </div>
        </form>
      )}
    </div>
  )
}

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const { info } = useEditAuth()
  return (
    <nav aria-label="Hlavná navigácia" className="flex h-full flex-col gap-6 px-3 py-4">
      <div className="flex items-center gap-2.5 px-2">
        <Mark className="size-7" />
        <div className="leading-tight">
          <p className="text-[15px] font-semibold">AlgoLab</p>
          <p className="text-xs text-ink-3">Návrh a analýza algoritmov</p>
        </div>
      </div>
      <ul className="flex flex-col gap-0.5">
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <li key={to}>
            <NavLink
              to={to}
              end={end}
              onClick={onNavigate}
              className={({ isActive }) =>
                cx(
                  'flex h-9 items-center gap-2.5 rounded-[var(--radius)] px-2.5 text-sm transition-colors',
                  isActive ? 'bg-surface-3 text-ink font-medium' : 'text-ink-2 hover:bg-surface-2 hover:text-ink',
                )
              }
            >
              <Icon className="size-4 shrink-0" strokeWidth={1.75} aria-hidden />
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
      <div className="mt-auto space-y-4">
        <EditLock />
        {info && (
          <p className="px-2 text-xs text-ink-3 num">
            {info.problems} úloh, {info.algorithms} algoritmov
          </p>
        )}
      </div>
    </nav>
  )
}

export default function Layout() {
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const wide = location.pathname.startsWith('/visualizer')
  return (
    <div className="min-h-dvh bg-ground">
      <aside className="fixed inset-y-0 left-0 hidden w-[232px] border-r border-line bg-ground lg:block">
        <Sidebar />
      </aside>
      <div className="sticky top-0 z-20 flex h-12 items-center gap-2 border-b border-line bg-ground px-3 lg:hidden">
        <button aria-label="Otvoriť menu" onClick={() => setOpen(true)} className="grid size-9 place-items-center rounded-[var(--radius)] hover:bg-surface-2 cursor-pointer">
          <Menu className="size-5" aria-hidden />
        </button>
        <Mark className="size-6" />
        <span className="font-semibold">AlgoLab</span>
      </div>
      {open && (
        <div className="fixed inset-0 z-30 lg:hidden">
          <div className="absolute inset-0 bg-black/30" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-[260px] bg-ground shadow-[var(--shadow-float)]">
            <button aria-label="Zavrieť menu" onClick={() => setOpen(false)} className="absolute right-2 top-3 grid size-9 place-items-center rounded-[var(--radius)] hover:bg-surface-2 cursor-pointer">
              <X className="size-5" aria-hidden />
            </button>
            <Sidebar onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}
      <main className="lg:pl-[232px]">
        <div className={cx('mx-auto px-4 py-6 sm:px-8 sm:py-8', wide ? 'max-w-[1480px]' : 'max-w-[1200px]')}>
          <Suspense fallback={<div className="h-64 animate-pulse rounded-[var(--radius-lg)] bg-surface-2" />}>
            <Outlet />
          </Suspense>
        </div>
      </main>
    </div>
  )
}

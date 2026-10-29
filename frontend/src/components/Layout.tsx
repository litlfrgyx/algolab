import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const navItems = [
  { path: '/problems',    icon: 'list_alt',  label: 'Problem Library' },
  { path: '/algorithms',  icon: 'code',      label: 'Code Editor' },
  { path: '/generator',   icon: 'input',     label: 'Input Generator' },
  { path: '/experiments', icon: 'science',   label: 'Experiment Suite' },
  { path: '/results',     icon: 'analytics', label: 'Analytics Dashboard' },
  { path: '/visualizer',  icon: 'play_circle', label: 'Visualizer' },
]

function SideNav() {
  const location = useLocation()
  return (
    <nav style={{
      position: 'fixed', left: 0, top: 0, height: '100%', width: 240, zIndex: 50,
      background: '#191c21',
      boxShadow: '1px 0 0 0 rgba(245,158,11,0.1)',
      display: 'flex', flexDirection: 'column', paddingTop: 24, paddingBottom: 24,
    }}>
      {/* Logo */}
      <div style={{ padding: '0 24px', marginBottom: 40 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <div style={{
            width: 32, height: 32,
            background: 'var(--surface-container-high)',
            border: '1px solid var(--outline-variant)',
            borderRadius: 4,
            display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden',
          }}>
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <polygon points="11,2 20,6.5 20,15.5 11,20 2,15.5 2,6.5" stroke="#f59e0b" strokeWidth="1.5" fill="rgba(245,158,11,0.15)"/>
              <circle cx="11" cy="11" r="3" fill="#f59e0b" opacity="0.9"/>
            </svg>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ color: '#f59e0b', fontFamily: 'Space Grotesk, sans-serif', fontWeight: 700, letterSpacing: '0.12em', fontSize: 15, lineHeight: 1 }}>
              ALGO_ANALYZER
            </span>
            <span style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 9, letterSpacing: '0.1em', color: 'var(--outline)', marginTop: 3, textTransform: 'uppercase' }}>
              V1.0.0-STABLE
            </span>
          </div>
        </div>
        <NavLink to="/experiments">
          <button style={{
            width: '100%', marginTop: 24,
            background: 'var(--primary-container)', color: 'var(--on-primary-container)',
            fontFamily: 'Space Grotesk, sans-serif', fontSize: 11,
            textTransform: 'uppercase', letterSpacing: '0.12em', fontWeight: 700,
            padding: '8px 16px', borderRadius: 4, border: 'none', cursor: 'pointer',
            boxShadow: '0 0 15px rgba(245,158,11,0.2)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            transition: 'box-shadow 0.2s',
          }}
            onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 0 20px rgba(245,158,11,0.4)')}
            onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 0 15px rgba(245,158,11,0.2)')}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>add</span>
            NEW EXPERIMENT
          </button>
        </NavLink>
      </div>

      {/* Nav items */}
      <div style={{ flex: 1, padding: '0 16px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        {navItems.map(item => {
          const isActive = location.pathname === item.path
          return (
            <NavLink
              key={item.path}
              to={item.path}
              style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '8px 16px',
                cursor: 'pointer', borderRadius: '0 2px 2px 0',
                fontFamily: 'Space Grotesk, sans-serif',
                fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase',
                fontWeight: isActive ? 700 : 400,
                textDecoration: 'none',
                color: isActive ? '#f59e0b' : '#64748b',
                boxShadow: isActive ? '0 0 12px rgba(245,158,11,0.3)' : 'none',
                borderLeft: isActive ? '2px solid #f59e0b' : '2px solid transparent',
                background: isActive ? '#272a30' : 'transparent',
                transition: 'all 0.2s',
                position: 'relative',
              }}
            >
              <span
                className="material-symbols-outlined"
                style={{ fontSize: 18, fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
              >
                {item.icon}
              </span>
              <span>{item.label}</span>
              {isActive && (
                <div style={{
                  position: 'absolute', right: 8,
                  width: 6, height: 6, borderRadius: '50%',
                  background: '#f59e0b', boxShadow: '0 0 8px rgba(245,158,11,0.8)',
                }} />
              )}
            </NavLink>
          )
        })}
      </div>

      {/* Footer */}
      <div style={{ padding: '0 16px', marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
        {[{ icon: 'memory', label: 'System Status' }, { icon: 'settings', label: 'Settings' }].map(item => (
          <div key={item.icon} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '8px 16px', cursor: 'pointer',
            color: '#64748b', borderRadius: 2,
            fontFamily: 'Space Grotesk, sans-serif', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase',
            transition: 'color 0.15s',
          }}
            onMouseEnter={e => (e.currentTarget.style.color = '#4cd7f6')}
            onMouseLeave={e => (e.currentTarget.style.color = '#64748b')}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </nav>
  )
}

function TopBar() {
  return (
    <header style={{
      position: 'fixed', top: 0, right: 0,
      width: 'calc(100% - 240px)', zIndex: 40,
      background: 'rgba(11,14,19,0.8)', backdropFilter: 'blur(20px)',
      borderBottom: '1px solid #1e2530',
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      height: 64, padding: '0 32px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
        {/* Search */}
        <div style={{ position: 'relative', width: 256 }}>
          <span className="material-symbols-outlined" style={{
            position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
            color: 'var(--outline-variant)', fontSize: 18,
          }}>search</span>
          <input style={{
            width: '100%', background: 'var(--surface-container-low)',
            border: '1px solid rgba(83,68,52,0.3)', borderRadius: 4,
            padding: '6px 16px 6px 40px', fontSize: 12,
            fontFamily: 'JetBrains Mono, monospace', color: 'var(--on-surface)',
            outline: 'none', transition: 'border-color 0.15s',
          }} placeholder="QUERY ALGORITHM..." type="text" />
        </div>
        {/* Nav links */}
        <nav style={{ display: 'flex', gap: 24 }}>
          {['Terminal', 'Docs', 'Telemetry'].map(l => (
            <a key={l} href="#" style={{
              color: '#64748b', textDecoration: 'none',
              fontFamily: 'Space Grotesk, sans-serif', fontSize: 11,
              letterSpacing: '0.1em', textTransform: 'uppercase', transition: 'color 0.15s',
            }}
              onMouseEnter={e => (e.currentTarget.style.color = '#4cd7f6')}
              onMouseLeave={e => (e.currentTarget.style.color = '#64748b')}
            >{l}</a>
          ))}
        </nav>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, borderRight: '1px solid rgba(83,68,52,0.3)', paddingRight: 16 }}>
          {[
            { icon: 'history', badge: false },
            { icon: 'notifications', badge: true },
            { icon: 'account_tree', badge: false },
          ].map(({ icon, badge }) => (
            <button key={icon} style={{
              width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#64748b', background: 'none', border: 'none', cursor: 'pointer',
              transition: 'color 0.15s', position: 'relative',
            }}
              onMouseEnter={e => (e.currentTarget.style.color = '#4cd7f6')}
              onMouseLeave={e => (e.currentTarget.style.color = '#64748b')}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>{icon}</span>
              {badge && <div style={{
                position: 'absolute', top: 6, right: 6,
                width: 6, height: 6, borderRadius: '50%',
                background: 'var(--primary-container)', boxShadow: '0 0 4px rgba(245,158,11,0.8)',
              }} />}
            </button>
          ))}
        </div>
        <button style={{
          fontFamily: 'Space Grotesk, sans-serif', fontSize: 11, textTransform: 'uppercase',
          letterSpacing: '0.12em', padding: '6px 16px',
          border: '1px solid var(--outline-variant)', color: 'var(--on-surface)',
          background: 'none', borderRadius: 4, cursor: 'pointer', transition: 'all 0.15s',
        }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = '#4cd7f6'; e.currentTarget.style.color = '#4cd7f6' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--outline-variant)'; e.currentTarget.style.color = 'var(--on-surface)' }}
        >SAVE_STATE</button>
        <button style={{
          fontFamily: 'Space Grotesk, sans-serif', fontSize: 11, textTransform: 'uppercase',
          letterSpacing: '0.12em', padding: '6px 16px',
          background: 'var(--primary-container)', color: 'var(--on-primary-container)',
          border: 'none', borderRadius: 4, cursor: 'pointer',
          boxShadow: '0 0 12px rgba(245,158,11,0.3)',
          display: 'flex', alignItems: 'center', gap: 8, fontWeight: 700,
          transition: 'box-shadow 0.15s',
        }}
          onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 0 20px rgba(245,158,11,0.5)')}
          onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 0 12px rgba(245,158,11,0.3)')}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 16, fontVariationSettings: "'FILL' 1" }}>play_arrow</span>
          EXECUTE_RUN
        </button>
      </div>
    </header>
  )
}

export default function Layout() {
  const location = useLocation()
  return (
    <div style={{ width: '100%', height: '100%' }}>
      <div className="analog-grain" />
      <SideNav />
      <TopBar />
      <AnimatePresence mode="wait">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
          style={{ marginLeft: 240, height: '100vh', overflowY: 'auto' }}
        >
          <Outlet />
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

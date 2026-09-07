import { useClock } from '../hooks/useApi'
import { Wifi, WifiOff } from 'lucide-react'

export default function TopHeader({ title, subtitle, apiStatus }) {
  const clock = useClock()

  return (
    <header className="top-header">
      <div>
        <div className="header-title">{title}</div>
        {subtitle && <div className="header-subtitle">{subtitle}</div>}
      </div>

      <div className="header-status">
        {/* API Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.72rem' }}>
          {apiStatus === 'connected' ? (
            <>
              <Wifi size={13} color="var(--accent-green)" />
              <span style={{ color: 'var(--accent-green)' }}>Backend Connected</span>
            </>
          ) : apiStatus === 'demo' ? (
            <>
              <span style={{ color: 'var(--accent-yellow)', fontSize: '0.68rem' }}>⚡ Demo Mode</span>
            </>
          ) : (
            <>
              <WifiOff size={13} color="var(--accent-red)" />
              <span style={{ color: 'var(--accent-red)' }}>Offline</span>
            </>
          )}
        </div>

        <div style={{ width: 1, height: 20, background: 'var(--border)' }} />

        {/* Live indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div className="status-dot" />
          <span style={{ fontSize: '0.7rem', color: 'var(--accent-green)' }}>LIVE</span>
        </div>

        <div className="header-time">
          {clock.toLocaleString('en-IN', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: false,
          })}
        </div>
      </div>
    </header>
  )
}

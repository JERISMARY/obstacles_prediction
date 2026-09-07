import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Bus, AlertTriangle, BarChart2,
  Video, Radio, Settings, Activity
} from 'lucide-react'
import { useClock } from '../hooks/useApi'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/live-analysis', icon: Activity, label: 'Live Analysis' },
  { to: '/monitoring', icon: Radio, label: 'Live Monitoring' },
  { to: '/incidents', icon: AlertTriangle, label: 'Incidents' },
  { to: '/buses', icon: Bus, label: 'Bus Fleet' },
  { to: '/analytics', icon: BarChart2, label: 'Analytics' },
  { to: '/video', icon: Video, label: 'Video Analysis' },
]

export default function Sidebar() {
  const clock = useClock()

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">🛰️</div>
        <div className="sidebar-brand-text">
          <h2>UrbanSense AI</h2>
          <p>SIH26124 Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="nav-section-label">Main</div>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}

        <div className="nav-section-label" style={{ marginTop: 8 }}>System</div>
        <NavLink
          to="/settings"
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Settings size={16} />
          Settings
        </NavLink>
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="demo-badge">
          <span>●</span> Demo Mode
        </div>
        <div style={{ marginTop: 8, fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {clock.toLocaleTimeString('en-IN', { hour12: false })}
        </div>
        <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: 2 }}>
          Madurai Urban Grid
        </div>
      </div>
    </aside>
  )
}

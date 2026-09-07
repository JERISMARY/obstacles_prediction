import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import LiveMonitoring from './pages/LiveMonitoring'
import Incidents from './pages/Incidents'
import Buses from './pages/Buses'
import Analytics from './pages/Analytics'
import VideoAnalysis from './pages/VideoAnalysis'
import Settings from './pages/Settings'
import LiveAnalysis from './pages/LiveAnalysis'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/monitoring" element={<LiveMonitoring />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/live-analysis" element={<LiveAnalysis />} />
            <Route path="/buses" element={<Buses />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/video" element={<VideoAnalysis />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

function NotFound() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', gap: 16 }}>
      <div style={{ fontSize: '4rem' }}>🛰️</div>
      <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>404 — Page Not Found</div>
      <a href="/" style={{ color: 'var(--accent-blue)' }}>Return to Dashboard</a>
    </div>
  )
}

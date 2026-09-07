import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { healthApi } from '../services/api'
import TopHeader from '../components/TopHeader'

export default function Settings() {
  const { data: health, refetch } = useApi(() => healthApi.check())
  const [theme, setTheme] = useState('dark')

  return (
    <>
      <TopHeader title="Settings" subtitle="System configuration and API status" />
      <div className="page-content">
        <div className="page-header">
          <div><h1>Settings</h1><p>System configuration and connection status</p></div>
        </div>

        {/* System Status */}
        <div className="card mb-4">
          <div className="card-header">
            <span className="card-title">System Status</span>
            <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Refresh</button>
          </div>
          {health ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <StatusRow label="API Backend" value={health.status === 'ok' ? 'Online' : 'Offline'} ok={health.status === 'ok'} />
              <StatusRow label="MongoDB" value={health.database} ok={health.database === 'connected'} />
              <StatusRow label="Demo Mode" value={health.demo_mode ? 'Enabled' : 'Disabled'} ok={!health.demo_mode} warn={health.demo_mode} />
              <StatusRow label="YOLO Model" value={health.yolo_model} ok />
              <StatusRow label="Version" value={health.version} ok />
            </div>
          ) : (
            <div className="empty-state"><div className="spinner" /><p>Checking system status…</p></div>
          )}
        </div>

        {/* Config info */}
        <div className="card mb-4">
          <div className="card-header"><span className="card-title">Configuration</span></div>
          <div style={{ fontSize: '0.78rem', display: 'flex', flexDirection: 'column', gap: 10 }}>
            <ConfigRow label="Backend URL" value="http://localhost:8000" />
            <ConfigRow label="Frontend Port" value="5173" />
            <ConfigRow label="MongoDB" value="mongodb://localhost:27017" />
            <ConfigRow label="Database" value="sih26_urban_intel" />
            <ConfigRow label="GPS" value="Simulator (Madurai routes)" />
            <ConfigRow label="Pothole Model" value="None configured — Demo Mode active" />
            <ConfigRow label="Vehicle Model" value="YOLOv8n.pt (COCO-pretrained)" />
          </div>
        </div>

        {/* API Docs link */}
        <div className="card">
          <div className="card-header"><span className="card-title">API Documentation</span></div>
          <div style={{ display: 'flex', gap: 12 }}>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="btn btn-primary">
              📖 Swagger UI
            </a>
            <a href="http://localhost:8000/redoc" target="_blank" rel="noreferrer" className="btn btn-secondary">
              📄 ReDoc
            </a>
          </div>
          <div style={{ marginTop: 12, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Full API documentation with interactive endpoints available when the backend is running.
          </div>
        </div>
      </div>
    </>
  )
}

function StatusRow({ label, value, ok, warn }) {
  const color = ok ? 'var(--accent-green)' : warn ? 'var(--accent-yellow)' : 'var(--accent-red)'
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px solid var(--border)', fontSize: '0.8rem' }}>
      <span style={{ color: 'var(--text-muted)' }}>{label}</span>
      <span style={{ color, fontWeight: 500 }}>● {value}</span>
    </div>
  )
}

function ConfigRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 0', borderBottom: '1px solid var(--border)' }}>
      <span style={{ color: 'var(--text-muted)' }}>{label}</span>
      <span style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{value}</span>
    </div>
  )
}

import { Map, Clock, AlertTriangle } from 'lucide-react'

export default function RoutePanel({ recommendation }) {
  if (!recommendation) {
    return (
      <div className="card">
        <div className="card-header">
          <span className="card-title">Route Intelligence</span>
        </div>
        <div className="empty-state" style={{ minHeight: 120 }}>
          <Map size={24} style={{ marginBottom: 8, opacity: 0.5 }} />
          <p>Waiting for route data...</p>
        </div>
      </div>
    )
  }

  const { current_route: current, recommended, time_saving_min, should_recommend } = recommendation

  if (!current) return null

  return (
    <div className="card" style={{ position: 'relative' }}>
      {recommendation.is_demo && (
        <div style={{
          position: 'absolute',
          top: 12,
          right: 12,
          fontSize: '0.6rem',
          color: 'var(--accent-yellow)',
          border: '1px solid var(--accent-yellow)',
          padding: '2px 6px',
          borderRadius: 4,
          letterSpacing: '0.05em'
        }}>
          DEMO DATA
        </div>
      )}
      
      <div className="card-header">
        <span className="card-title">Route Intelligence</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {/* Current Route */}
        <div style={{ 
          padding: 12, 
          borderRadius: 8, 
          border: '1px solid var(--border)',
          background: should_recommend ? 'var(--bg-secondary)' : 'rgba(34, 197, 94, 0.05)',
          borderColor: should_recommend ? 'var(--border)' : 'rgba(34, 197, 94, 0.2)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{current.name} (Current)</span>
            {!should_recommend && <span style={{ color: 'var(--accent-green)', fontSize: '0.7rem', fontWeight: 700 }}>OPTIMAL</span>}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8 }}>
            {current.description}
          </div>
          <div style={{ display: 'flex', gap: 16, fontSize: '0.8rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <Clock size={14} color="var(--text-muted)" /> {current.eta_min} min
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <AlertTriangle size={14} color={current.traffic === 'severe' || current.traffic === 'high' ? 'var(--accent-red)' : 'var(--text-muted)'} /> 
              {current.traffic.toUpperCase()} traffic
            </span>
          </div>
        </div>

        {/* Recommended Route */}
        {should_recommend && recommended && (
          <div style={{ 
            padding: 12, 
            borderRadius: 8, 
            border: '2px solid var(--accent-blue)',
            background: 'rgba(56, 189, 248, 0.05)',
            position: 'relative'
          }}>
            <div style={{
              position: 'absolute',
              top: -10,
              left: 12,
              background: 'var(--accent-blue)',
              color: '#000',
              fontSize: '0.65rem',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: 4,
              letterSpacing: '0.05em'
            }}>
              RECOMMENDED ALTERNATIVE
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, marginTop: 4 }}>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-blue)' }}>{recommended.name}</span>
              <span style={{ color: 'var(--accent-green)', fontSize: '0.75rem', fontWeight: 700 }}>
                Save {time_saving_min} min
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8 }}>
              {recommended.description}
            </div>
            <div style={{ display: 'flex', gap: 16, fontSize: '0.8rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <Clock size={14} color="var(--text-muted)" /> {recommended.eta_min} min
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <AlertTriangle size={14} color="var(--text-muted)" /> 
                {recommended.traffic.toUpperCase()} traffic
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useApi } from '../hooks/useApi'
import { busesApi, eventsApi } from '../services/api'
import GISMap from '../components/GISMap'
import TopHeader from '../components/TopHeader'
import { formatRelative, trafficLevelColor } from '../utils/format'

export default function LiveMonitoring() {
  const { data: busesData } = useApi(() => busesApi.list(), [], { refreshInterval: 5000 })
  const { data: eventsData } = useApi(() => eventsApi.list({ limit: 50, status: 'new' }), [], { refreshInterval: 8000 })

  const buses = busesData?.buses || []
  const events = eventsData?.events || []

  const [ticker, setTicker] = useState([])

  // Build event ticker
  useEffect(() => {
    if (events.length) {
      setTicker(events.slice(0, 10))
    }
  }, [events])

  return (
    <>
      <TopHeader
        title="Live Monitoring"
        subtitle="Real-time bus tracking and incident feed"
        apiStatus={busesData?.source === 'database' ? 'connected' : 'demo'}
      />
      <div className="page-content">
        {/* Bus status strip */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
          {buses.map(bus => (
            <div key={bus.bus_id} style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: '8px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              fontSize: '0.78rem',
            }}>
              <span style={{ color: bus.status === 'active' ? 'var(--accent-green)' : 'var(--text-muted)', fontSize: '0.6rem' }}>●</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--accent-blue)' }}>{bus.bus_id}</span>
              <span style={{ color: 'var(--text-muted)' }}>{bus.route_start?.split(' ')[0]}</span>
              <span style={{ color: trafficLevelColor(bus.traffic_level), fontWeight: 600, fontSize: '0.7rem' }}>
                {(bus.traffic_level || 'LOW').toUpperCase()}
              </span>
            </div>
          ))}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16 }}>
          {/* Full map */}
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="card-title">Live City Map</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div className="status-dot" style={{ width: 6, height: 6 }} />
                <span style={{ fontSize: '0.7rem', color: 'var(--accent-green)' }}>Updating every 5s</span>
              </div>
            </div>
            <GISMap buses={buses} events={events} height={500} />
          </div>

          {/* Event feed */}
          <div className="card" style={{ overflow: 'hidden' }}>
            <div className="card-header">
              <span className="card-title">Incident Feed</span>
              <span style={{ fontSize: '0.68rem', color: 'var(--accent-red)', fontWeight: 600 }}>
                ● {events.filter(e => e.status === 'new').length} NEW
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 460, overflowY: 'auto' }}>
              {ticker.length === 0 ? (
                <div className="empty-state" style={{ padding: 24 }}>
                  <span>📡</span><p>No active incidents</p>
                </div>
              ) : (
                ticker.map(evt => (
                  <FeedItem key={evt.event_id} event={evt} />
                ))
              )}
            </div>
          </div>
        </div>

        {/* Congestion table */}
        <div className="card" style={{ marginTop: 16 }}>
          <div className="card-header">
            <span className="card-title">Traffic Summary</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
            {buses.map(bus => (
              <TrafficCard key={bus.bus_id} bus={bus} />
            ))}
          </div>
        </div>
      </div>
    </>
  )
}

function FeedItem({ event }) {
  const colors = { critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e' }
  const icons = { pothole: '🕳️', road_damage: '🚧', waterlogging: '💧', traffic_sign_damage: '🚦', traffic_congestion: '🚗' }
  const color = colors[event.severity] || '#94a3b8'

  return (
    <div style={{
      padding: '10px 12px',
      background: 'var(--bg-secondary)',
      borderRadius: 8,
      borderLeft: `3px solid ${color}`,
      fontSize: '0.75rem',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontWeight: 600 }}>
          {icons[event.type] || '⚠️'} {event.type?.replace('_', ' ')}
        </span>
        <span className={`badge badge-${event.severity}`} style={{ fontSize: '0.62rem' }}>{event.severity}</span>
      </div>
      <div style={{ color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
        <span className="mono">{event.bus_id}</span>
        <span>{formatRelative(event.timestamp)}</span>
      </div>
      {event.is_demo && <span style={{ fontSize: '0.6rem', color: 'var(--accent-yellow)' }}>⚡ demo</span>}
    </div>
  )
}

function TrafficCard({ bus }) {
  const levelColors = { severe: '#ef4444', high: '#f97316', moderate: '#eab308', low: '#22c55e' }
  const color = levelColors[bus.traffic_level] || '#22c55e'

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      borderRadius: 8,
      padding: '12px',
      border: `1px solid ${color}33`,
    }}>
      <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--accent-blue)', fontSize: '0.85rem', marginBottom: 4 }}>
        {bus.bus_id}
      </div>
      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6 }}>
        {bus.route_start?.split(' ').slice(0, 2).join(' ')}
      </div>
      <div style={{ fontWeight: 700, color, fontSize: '0.9rem' }}>
        {(bus.traffic_level || 'LOW').toUpperCase()}
      </div>
      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>
        {bus.incident_count || 0} incidents
      </div>
    </div>
  )
}

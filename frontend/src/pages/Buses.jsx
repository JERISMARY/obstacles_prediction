import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { busesApi } from '../services/api'
import TopHeader from '../components/TopHeader'
import GISMap from '../components/GISMap'
import { formatLatLon, formatRelative } from '../utils/format'

export default function Buses() {
  const { data, loading } = useApi(() => busesApi.list(), [], { refreshInterval: 10000 })
  const [selectedBus, setSelectedBus] = useState(null)
  const { data: busEventsData } = useApi(
    () => selectedBus ? busesApi.getEvents(selectedBus.bus_id) : Promise.resolve(null),
    [selectedBus?.bus_id]
  )

  const buses = data?.buses || []
  const busEvents = busEventsData?.events || []

  return (
    <>
      <TopHeader
        title="Bus Fleet Monitor"
        subtitle="Real-time fleet tracking and status"
        apiStatus={data?.source === 'database' ? 'connected' : 'demo'}
      />
      <div className="page-content">
        <div className="page-header">
          <div>
            <h1>Bus Fleet</h1>
            <p>{buses.length} buses tracked · {buses.filter(b => b.status === 'active').length} active</p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: selectedBus ? '1fr 1fr' : '1fr', gap: 16, marginBottom: 16 }}>
          {/* Map */}
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)' }}>
              <span className="card-title">Fleet Map</span>
            </div>
            <GISMap buses={buses} events={selectedBus ? busEvents : []} height={360} />
          </div>

          {/* Selected bus detail */}
          {selectedBus && (
            <div className="card">
              <div className="card-header">
                <span className="card-title" style={{ fontFamily: 'var(--font-mono)', fontSize: '1rem' }}>
                  {selectedBus.bus_id}
                </span>
                <button className="btn btn-secondary btn-sm" onClick={() => setSelectedBus(null)}>✕</button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <InfoRow label="Route" value={selectedBus.route_name} />
                <InfoRow label="From" value={selectedBus.route_start} />
                <InfoRow label="To" value={selectedBus.route_end} />
                <InfoRow label="Status">
                  <span className={`badge badge-${selectedBus.status}`}>{selectedBus.status}</span>
                </InfoRow>
                <InfoRow label="Traffic">
                  <span className={`traffic-${selectedBus.traffic_level}`} style={{ fontWeight: 600 }}>
                    {(selectedBus.traffic_level || 'low').toUpperCase()}
                  </span>
                </InfoRow>
                <InfoRow label="Driver" value={selectedBus.driver_name || '—'} />
                <InfoRow label="Phone" value={selectedBus.driver_phone || '—'} />
                <InfoRow
                  label="Location"
                  value={formatLatLon(selectedBus.current_location?.latitude, selectedBus.current_location?.longitude)}
                />
                <InfoRow
                  label="Speed"
                  value={`${selectedBus.current_location?.speed_kmh?.toFixed(1) || 0} km/h`}
                />
                <InfoRow label="Incidents" value={selectedBus.incident_count || 0} />
                <InfoRow label="Last Active" value={formatRelative(selectedBus.last_active)} />
                {selectedBus.is_demo && (
                  <div style={{ fontSize: '0.7rem', color: 'var(--accent-yellow)', marginTop: 4 }}>⚡ DEMO DATA</div>
                )}
              </div>

              {busEvents.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <div className="card-title" style={{ marginBottom: 8 }}>Recent Events ({busEvents.length})</div>
                  {busEvents.slice(0, 5).map(evt => (
                    <div key={evt.event_id} style={{
                      padding: '6px 10px',
                      background: 'var(--bg-secondary)',
                      borderRadius: 6,
                      marginBottom: 6,
                      fontSize: '0.75rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}>
                      <span>{evt.type?.replace('_', ' ')}</span>
                      <span className={`badge badge-${evt.severity}`}>{evt.severity}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Bus Cards Grid */}
        {loading ? (
          <div className="loading-state"><div className="spinner" /><span>Loading fleet…</span></div>
        ) : (
          <div className="bus-grid">
            {buses.map(bus => (
              <div
                key={bus.bus_id}
                className={`bus-card ${selectedBus?.bus_id === bus.bus_id ? 'selected' : ''}`}
                onClick={() => setSelectedBus(bus)}
                style={selectedBus?.bus_id === bus.bus_id ? { borderColor: 'var(--accent-blue)', boxShadow: 'var(--shadow-glow-blue)' } : {}}
              >
                <div className="bus-card-header">
                  <span className="bus-id">{bus.bus_id}</span>
                  <span className={`badge badge-${bus.status}`}>{bus.status}</span>
                </div>
                <div className="bus-route">{bus.route_name}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                  {bus.route_start} → {bus.route_end}
                </div>
                <div className="bus-meta">
                  <div className="bus-meta-item">
                    <span className="bus-meta-label">Traffic</span>
                    <span className={`bus-meta-value traffic-${bus.traffic_level || 'low'}`}>
                      {(bus.traffic_level || 'low').toUpperCase()}
                    </span>
                  </div>
                  <div className="bus-meta-item">
                    <span className="bus-meta-label">Incidents</span>
                    <span className="bus-meta-value">{bus.incident_count || 0}</span>
                  </div>
                  <div className="bus-meta-item">
                    <span className="bus-meta-label">Speed</span>
                    <span className="bus-meta-value">
                      {bus.current_location?.speed_kmh?.toFixed(0) || 0} km/h
                    </span>
                  </div>
                  <div className="bus-meta-item">
                    <span className="bus-meta-label">Driver</span>
                    <span className="bus-meta-value">{bus.driver_name || '—'}</span>
                  </div>
                </div>
                {bus.is_demo && (
                  <div style={{ fontSize: '0.65rem', color: 'var(--accent-yellow)', marginTop: 8 }}>⚡ DEMO</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}

function InfoRow({ label, value, children }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 0', borderBottom: '1px solid var(--border)', fontSize: '0.78rem' }}>
      <span style={{ color: 'var(--text-muted)' }}>{label}</span>
      <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{children || value}</span>
    </div>
  )
}

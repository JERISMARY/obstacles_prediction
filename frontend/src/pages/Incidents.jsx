import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { eventsApi } from '../services/api'
import IncidentTable from '../components/IncidentTable'
import TopHeader from '../components/TopHeader'
import GISMap from '../components/GISMap'

const EVENT_TYPES = ['', 'pothole', 'road_damage', 'waterlogging', 'traffic_sign_damage', 'traffic_congestion', 'accident', 'other']
const SEVERITIES = ['', 'critical', 'high', 'medium', 'low']
const STATUSES = ['', 'new', 'verified', 'in_progress', 'resolved']
const BUSES = ['', 'BUS-101', 'BUS-102', 'BUS-103', 'BUS-104', 'BUS-105']

export default function Incidents() {
  const [filters, setFilters] = useState({ type: '', severity: '', status: '', bus_id: '' })

  const activeFilters = Object.fromEntries(Object.entries(filters).filter(([, v]) => v))

  const { data, loading, refetch } = useApi(
    () => eventsApi.list({ ...activeFilters, limit: 100 }),
    [JSON.stringify(activeFilters)],
    { refreshInterval: 30000 }
  )

  const events = data?.events || []

  const handleStatusChange = async (eventId, newStatus) => {
    try {
      await eventsApi.update(eventId, { status: newStatus })
      refetch()
    } catch (e) {
      alert('Failed to update status: ' + e.message)
    }
  }

  const setFilter = (key, val) => setFilters(f => ({ ...f, [key]: val }))

  return (
    <>
      <TopHeader
        title="Incident Management"
        subtitle="All detected road defects and traffic events"
        apiStatus={data?.source === 'database' ? 'connected' : 'demo'}
      />

      <div className="page-content">
        <div className="page-header">
          <div>
            <h1>Incidents</h1>
            <p>{events.length} incidents · {data?.total ?? 0} total in database</p>
          </div>
        </div>

        {/* Map */}
        <div className="card mb-4" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)' }}>
            <span className="card-title">Incident Map</span>
          </div>
          <GISMap events={events} height={320} />
        </div>

        {/* Filters */}
        <div className="filter-bar">
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Filter:</span>
          <select className="select" value={filters.type} onChange={e => setFilter('type', e.target.value)}>
            <option value="">All Types</option>
            {EVENT_TYPES.slice(1).map(t => (
              <option key={t} value={t}>{t.replace('_', ' ')}</option>
            ))}
          </select>
          <select className="select" value={filters.severity} onChange={e => setFilter('severity', e.target.value)}>
            <option value="">All Severities</option>
            {SEVERITIES.slice(1).map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <select className="select" value={filters.status} onChange={e => setFilter('status', e.target.value)}>
            <option value="">All Statuses</option>
            {STATUSES.slice(1).map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
          </select>
          <select className="select" value={filters.bus_id} onChange={e => setFilter('bus_id', e.target.value)}>
            <option value="">All Buses</option>
            {BUSES.slice(1).map(b => <option key={b} value={b}>{b}</option>)}
          </select>
          <button className="btn btn-secondary btn-sm" onClick={() => setFilters({ type: '', severity: '', status: '', bus_id: '' })}>
            Clear
          </button>
          <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Refresh</button>
        </div>

        {/* Table */}
        <div className="card">
          <IncidentTable events={events} loading={loading} onStatusChange={handleStatusChange} />
        </div>
      </div>
    </>
  )
}

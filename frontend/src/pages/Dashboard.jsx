import { useState, useEffect } from 'react'
import { useApi } from '../hooks/useApi'
import { statisticsApi, eventsApi, busesApi } from '../services/api'
import GISMap from '../components/GISMap'
import IncidentTable from '../components/IncidentTable'
import TopHeader from '../components/TopHeader'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from 'recharts'

const SEVERITY_COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
}

const TYPE_COLORS = {
  pothole: '#f87171',
  road_damage: '#fb923c',
  waterlogging: '#60a5fa',
  traffic_sign_damage: '#a78bfa',
  traffic_congestion: '#fbbf24',
  other: '#94a3b8',
}

export default function Dashboard() {
  const { data: stats, loading: statsLoading } = useApi(
    () => statisticsApi.get(), [], { refreshInterval: 30000 }
  )
  const { data: eventsData, loading: eventsLoading } = useApi(
    () => eventsApi.list({ limit: 20 }), [], { refreshInterval: 20000 }
  )
  const { data: busesData, loading: busesLoading } = useApi(
    () => busesApi.list(), [], { refreshInterval: 15000 }
  )

  const events = eventsData?.events || []
  const buses = busesData?.buses || []

  const apiStatus = stats?.source === 'database' ? 'connected' : 'demo'

  // Build chart data from type_breakdown
  const typeChartData = Object.entries(stats?.type_breakdown || {}).map(([type, count]) => ({
    name: type.replace('_', ' '),
    count,
    fill: TYPE_COLORS[type] || '#94a3b8',
  }))

  const severityPieData = Object.entries(stats?.severity_breakdown || {}).map(([sev, count]) => ({
    name: sev,
    value: count,
    fill: SEVERITY_COLORS[sev] || '#94a3b8',
  }))

  return (
    <>
      <TopHeader
        title="Urban Intelligence Dashboard"
        subtitle="Real-time city monitoring · AI-powered bus camera network"
        apiStatus={apiStatus}
      />

      <div className="page-content">
        {/* Demo banner */}
        {apiStatus === 'demo' && (
          <div style={{
            background: 'rgba(251,191,36,0.08)',
            border: '1px solid rgba(251,191,36,0.25)',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 16px',
            marginBottom: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: '0.78rem',
            color: 'var(--accent-yellow)',
          }}>
            ⚡ <strong>DEMO MODE</strong> — Displaying simulated data. Start MongoDB and the backend to use live data.
          </div>
        )}

        {/* ── Stats Grid ─────────────────────────────────────────── */}
        <div className="stats-grid">
          <StatCard
            label="Buses Monitored"
            value={stats?.buses?.total ?? '—'}
            sub={`${stats?.buses?.active ?? 0} active`}
            icon="🚌"
            color="var(--accent-blue)"
          />
          <StatCard
            label="Total Incidents"
            value={stats?.incidents?.total ?? '—'}
            sub={`${stats?.incidents?.new ?? 0} unresolved`}
            icon="⚠️"
            color="var(--accent-yellow)"
          />
          <StatCard
            label="Road Defects"
            value={stats?.incidents?.road_defects ?? '—'}
            sub="potholes · damage · flood"
            icon="🕳️"
            color="var(--accent-orange)"
          />
          <StatCard
            label="Traffic Alerts"
            value={stats?.incidents?.traffic_alerts ?? '—'}
            sub="congestion events"
            icon="🚦"
            color="var(--accent-red)"
          />
          <StatCard
            label="High Priority"
            value={stats?.incidents?.high_priority ?? '—'}
            sub="requires attention"
            icon="🔴"
            color="var(--sev-critical)"
          />
          <StatCard
            label="Resolved"
            value={stats?.incidents?.resolved ?? '—'}
            sub="fixed incidents"
            icon="✅"
            color="var(--accent-green)"
          />
        </div>

        {/* ── Map + Charts Row ───────────────────────────────────── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16, marginBottom: 16 }}>
          {/* Map */}
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div className="card-header" style={{ padding: '14px 18px', marginBottom: 0, borderBottom: '1px solid var(--border)' }}>
              <span className="card-title">Live GIS Map</span>
              <div style={{ display: 'flex', gap: 12, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                <span>🚌 Buses ({buses.length})</span>
                <span>📍 Incidents ({events.length})</span>
              </div>
            </div>
            <GISMap events={events} buses={buses} height={420} />
          </div>

          {/* Severity Pie */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="card-header">
              <span className="card-title">Severity Breakdown</span>
            </div>
            {severityPieData.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie
                      data={severityPieData}
                      cx="50%" cy="50%"
                      innerRadius={45}
                      outerRadius={75}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {severityPieData.map((d, i) => (
                        <Cell key={i} fill={d.fill} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {severityPieData.map(d => (
                    <div key={d.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ width: 10, height: 10, borderRadius: 2, background: d.fill }} />
                        <span style={{ textTransform: 'capitalize', color: 'var(--text-secondary)' }}>{d.name}</span>
                      </div>
                      <span style={{ fontWeight: 600, color: d.fill }}>{d.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="empty-state">No data</div>
            )}
          </div>
        </div>

        {/* ── Type Breakdown Bar Chart ───────────────────────────── */}
        {typeChartData.length > 0 && (
          <div className="card mb-4">
            <div className="card-header">
              <span className="card-title">Incident Type Breakdown</span>
            </div>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={typeChartData} barSize={28}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {typeChartData.map((d, i) => (
                    <Cell key={i} fill={d.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* ── Recent Incidents Table ─────────────────────────────── */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Recent Incidents</span>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Latest {events.length} events
            </span>
          </div>
          <IncidentTable events={events} loading={eventsLoading} />
        </div>
      </div>
    </>
  )
}

function StatCard({ label, value, sub, icon, color }) {
  return (
    <div className="stat-card" style={{ '--accent-color': color }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color }}>{value}</div>
      <div className="stat-change">{sub}</div>
    </div>
  )
}

import { useApi } from '../hooks/useApi'
import { statisticsApi } from '../services/api'
import TopHeader from '../components/TopHeader'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, Legend,
} from 'recharts'

const COLORS = ['#38bdf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#fb923c']

export default function Analytics() {
  const { data: stats } = useApi(() => statisticsApi.get(), [], { refreshInterval: 60000 })
  const { data: trafficData } = useApi(() => statisticsApi.traffic(), [], { refreshInterval: 60000 })

  const typeData = Object.entries(stats?.type_breakdown || {}).map(([type, count]) => ({
    name: type.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
    count,
  }))

  const severityData = Object.entries(stats?.severity_breakdown || {}).map(([sev, count]) => ({
    name: sev.charAt(0).toUpperCase() + sev.slice(1),
    value: count,
  }))

  const trafficRecords = trafficData?.records || []
  const trafficChartData = trafficRecords.slice(0, 20).map((r, i) => ({
    name: `T${i + 1}`,
    vehicles: r.vehicle_count,
    density: r.traffic_density,
  }))

  // Vehicle type breakdown from traffic records
  const vehicleTypeTotals = {}
  trafficRecords.forEach(r => {
    Object.entries(r.vehicle_types || {}).forEach(([type, count]) => {
      vehicleTypeTotals[type] = (vehicleTypeTotals[type] || 0) + count
    })
  })
  const vehicleTypeData = Object.entries(vehicleTypeTotals).map(([type, count]) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    value: count,
  }))

  return (
    <>
      <TopHeader
        title="Analytics"
        subtitle="Traffic patterns, incident trends, and system performance"
        apiStatus={stats?.source === 'database' ? 'connected' : 'demo'}
      />
      <div className="page-content">
        <div className="page-header">
          <div>
            <h1>Analytics</h1>
            <p>Aggregated data from all monitoring buses</p>
          </div>
        </div>

        {/* ── Summary Row ─────────────────────────────────────────── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 20 }}>
          {[
            { label: 'Total Buses', value: stats?.buses?.total ?? 0, color: '#38bdf8' },
            { label: 'Total Events', value: stats?.incidents?.total ?? 0, color: '#fbbf24' },
            { label: 'Resolution Rate', value: stats?.incidents?.total ? `${Math.round((stats.incidents.resolved / stats.incidents.total) * 100)}%` : '—', color: '#34d399' },
            { label: 'High Priority', value: stats?.incidents?.high_priority ?? 0, color: '#ef4444' },
          ].map(({ label, value, color }) => (
            <div key={label} className="card" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color }}>{value}</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>{label}</div>
            </div>
          ))}
        </div>

        <div className="grid-2" style={{ marginBottom: 16 }}>
          {/* Incident by type */}
          <div className="card">
            <div className="card-header"><span className="card-title">Incidents by Type</span></div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={typeData} barSize={24}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {typeData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Severity pie */}
          <div className="card">
            <div className="card-header"><span className="card-title">Severity Distribution</span></div>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%" cy="50%"
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                  labelLine={{ stroke: 'var(--text-muted)' }}
                >
                  {severityData.map((_, i) => (
                    <Cell key={i} fill={['#ef4444', '#f97316', '#eab308', '#22c55e'][i] || COLORS[i]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Traffic density over time */}
        {trafficChartData.length > 0 && (
          <div className="card mb-4">
            <div className="card-header">
              <span className="card-title">Traffic Density Over Time</span>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                {trafficRecords.length} records
              </span>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={trafficChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }} />
                <Legend />
                <Line type="monotone" dataKey="vehicles" stroke="#38bdf8" strokeWidth={2} dot={false} name="Vehicle Count" />
                <Line type="monotone" dataKey="density" stroke="#fbbf24" strokeWidth={2} dot={false} name="Density %" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Vehicle type breakdown */}
        {vehicleTypeData.length > 0 && (
          <div className="card">
            <div className="card-header"><span className="card-title">Detected Vehicle Types</span></div>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={vehicleTypeData} layout="vertical" barSize={18}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <YAxis dataKey="name" type="category" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} width={70} />
                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {vehicleTypeData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </>
  )
}

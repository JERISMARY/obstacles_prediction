import { eventTypeLabel, eventTypeIcon, formatDateTime, formatConfidence, formatLatLon } from '../utils/format'

export default function IncidentTable({ events = [], onStatusChange, loading }) {
  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner" />
        <span>Loading incidents…</span>
      </div>
    )
  }

  if (!events.length) {
    return (
      <div className="empty-state">
        <span style={{ fontSize: '2rem' }}>📋</span>
        <p>No incidents match the current filters.</p>
      </div>
    )
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Severity</th>
            <th>Confidence</th>
            <th>Location</th>
            <th>Bus</th>
            <th>Time</th>
            <th>Status</th>
            {onStatusChange && <th>Action</th>}
          </tr>
        </thead>
        <tbody>
          {events.map(evt => (
            <tr key={evt.event_id}>
              <td className="primary mono" style={{ fontSize: '0.72rem' }}>{evt.event_id}</td>
              <td>
                <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  {eventTypeIcon(evt.type)}
                  <span>{eventTypeLabel(evt.type)}</span>
                </span>
              </td>
              <td>
                <span className={`badge badge-${evt.severity}`}>{evt.severity}</span>
              </td>
              <td>
                <div className="confidence-bar">
                  <div className="confidence-track">
                    <div
                      className="confidence-fill"
                      style={{ width: `${Math.round((evt.confidence || 0) * 100)}%` }}
                    />
                  </div>
                  <span style={{ width: 32, textAlign: 'right' }}>{formatConfidence(evt.confidence)}</span>
                </div>
              </td>
              <td className="mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {formatLatLon(evt.latitude, evt.longitude)}
              </td>
              <td className="primary mono">{evt.bus_id}</td>
              <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{formatDateTime(evt.timestamp)}</td>
              <td>
                <span className={`badge badge-${evt.status}`}>{evt.status?.replace('_', ' ')}</span>
              </td>
              {onStatusChange && (
                <td>
                  <select
                    className="select"
                    style={{ padding: '3px 6px', fontSize: '0.7rem' }}
                    value={evt.status}
                    onChange={e => onStatusChange(evt.event_id, e.target.value)}
                  >
                    <option value="new">New</option>
                    <option value="verified">Verified</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                  </select>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

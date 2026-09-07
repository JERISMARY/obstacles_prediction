import { severityColor, eventTypeIcon, eventTypeLabel, formatConfidence, formatDateTime, formatLatLon } from '../utils/format'

export default function EventPopup({ event }) {
  if (!event) return null

  const sColor = severityColor(event.severity)

  return (
    <div className="popup-content">
      <div className="popup-title">
        {eventTypeIcon(event.type)} {eventTypeLabel(event.type)}
      </div>

      {event.is_demo && (
        <div style={{
          background: 'rgba(251,191,36,0.1)',
          border: '1px solid rgba(251,191,36,0.3)',
          borderRadius: 4,
          padding: '3px 8px',
          fontSize: '0.65rem',
          color: '#fbbf24',
          marginBottom: 8,
          textAlign: 'center',
          letterSpacing: '0.08em',
        }}>
          ⚡ DEMO DATA — Simulated
        </div>
      )}

      <div className="popup-row">
        <span className="popup-row-label">Event ID</span>
        <span className="popup-row-value mono" style={{ fontSize: '0.7rem' }}>{event.event_id}</span>
      </div>
      <div className="popup-row">
        <span className="popup-row-label">Severity</span>
        <span className="popup-row-value" style={{ color: sColor, textTransform: 'uppercase', fontWeight: 700, fontSize: '0.75rem' }}>
          {event.severity}
        </span>
      </div>
      <div className="popup-row">
        <span className="popup-row-label">Confidence</span>
        <span className="popup-row-value">{formatConfidence(event.confidence)}</span>
      </div>
      <div className="popup-row">
        <span className="popup-row-label">Bus</span>
        <span className="popup-row-value mono">{event.bus_id}</span>
      </div>
      <div className="popup-row">
        <span className="popup-row-label">Status</span>
        <span className={`badge badge-${event.status}`}>{event.status?.replace('_', ' ')}</span>
      </div>
      <div className="popup-row">
        <span className="popup-row-label">Location</span>
        <span className="popup-row-value mono" style={{ fontSize: '0.68rem' }}>
          {formatLatLon(event.latitude, event.longitude)}
        </span>
      </div>
      <div className="popup-row">
        <span className="popup-row-label">Time</span>
        <span className="popup-row-value">{formatDateTime(event.timestamp)}</span>
      </div>

      {event.vehicle_count != null && (
        <div className="popup-row">
          <span className="popup-row-label">Vehicles</span>
          <span className="popup-row-value">{event.vehicle_count} detected</span>
        </div>
      )}

      {event.traffic_density != null && (
        <div className="popup-row">
          <span className="popup-row-label">Density</span>
          <span className="popup-row-value">{event.traffic_density}%</span>
        </div>
      )}

      {event.description && (
        <div style={{ marginTop: 8, fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
          {event.description}
        </div>
      )}

      {event.evidence_image && (
        <div style={{ marginTop: 10 }}>
          <img
            src={event.evidence_image}
            alt="Evidence"
            style={{ width: '100%', borderRadius: 4, border: '1px solid var(--border)' }}
            onError={e => e.target.style.display = 'none'}
          />
        </div>
      )}
    </div>
  )
}

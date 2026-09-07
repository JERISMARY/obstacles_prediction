import { useEffect, useRef } from 'react'
import { Volume2 } from 'lucide-react'
import { formatTime } from '../utils/format'

export default function EventTimeline({ warnings = [] }) {
  const scrollRef = useRef(null)

  // Auto-scroll to bottom when new warnings arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [warnings])

  if (!warnings || warnings.length === 0) {
    return (
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div className="card-header"><span className="card-title">Live Event Timeline</span></div>
        <div className="empty-state" style={{ flex: 1, minHeight: 200 }}>
          <span style={{ fontSize: '2rem', opacity: 0.5 }}>⏱️</span>
          <p>Awaiting live events...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div className="card-header" style={{ marginBottom: 0, paddingBottom: 12, borderBottom: '1px solid var(--border)' }}>
        <span className="card-title">Live Event Timeline</span>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{warnings.length} events</span>
      </div>
      
      <div 
        ref={scrollRef}
        style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '12px 16px',
          display: 'flex',
          flexDirection: 'column',
          gap: 12
        }}
      >
        {/* Render warnings chronologically (oldest at top, newest at bottom) */}
        {[...warnings].reverse().map((w, idx) => (
          <TimelineItem key={w.warning_id || idx} warning={w} />
        ))}
      </div>
    </div>
  )
}

function TimelineItem({ warning }) {
  const colors = {
    critical: 'var(--accent-red)',
    warning: 'var(--accent-orange)',
    caution: 'var(--accent-yellow)',
    safe: 'var(--accent-green)',
  }
  const color = colors[warning.risk_level] || 'var(--border)'

  return (
    <div style={{ display: 'flex', gap: 12 }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ 
          width: 10, 
          height: 10, 
          borderRadius: '50%', 
          background: color,
          marginTop: 4
        }} />
        <div style={{ flex: 1, width: 2, background: 'var(--border)', margin: '4px 0' }} />
      </div>
      
      <div style={{ flex: 1, paddingBottom: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
          <span style={{ 
            fontSize: '0.75rem', 
            fontWeight: 600, 
            color: 'var(--text-primary)',
            textTransform: 'uppercase'
          }}>
            {warning.type?.replace('_', ' ')}
          </span>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            {formatTime(warning.timestamp)}
          </span>
        </div>
        
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
          {warning.message}
        </div>
        
        {warning.speak && (
          <div style={{ 
            display: 'inline-flex', 
            alignItems: 'center', 
            gap: 4, 
            marginTop: 6,
            background: 'var(--bg-secondary)',
            padding: '2px 6px',
            borderRadius: 4,
            fontSize: '0.65rem',
            color: 'var(--accent-blue)'
          }}>
            <Volume2 size={12} /> Spoken via Voice Assistant
          </div>
        )}
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { Volume2, VolumeX, Mic, MicOff, RefreshCw } from 'lucide-react'
import { voiceService } from '../services/voiceService'

export default function VoiceAssistant({ latestWarning, isActive }) {
  const [enabled, setEnabled] = useState(voiceService.enabled)
  const [volume, setVolume] = useState(voiceService.volume)
  
  const toggleEnabled = () => {
    const newVal = !enabled
    setEnabled(newVal)
    voiceService.setEnabled(newVal)
  }

  const handleVolume = (e) => {
    const val = parseFloat(e.target.value)
    setVolume(val)
    voiceService.setVolume(val)
  }

  const replay = () => {
    if (latestWarning?.message) {
      voiceService.speak(latestWarning.message, latestWarning.priority)
    }
  }

  // Determine color based on latest warning priority/risk
  const getBorderColor = () => {
    if (!latestWarning || !isActive) return 'var(--border)'
    const colors = {
      critical: 'var(--accent-red)',
      warning: 'var(--accent-orange)',
      caution: 'var(--accent-yellow)',
      safe: 'var(--accent-green)',
    }
    return colors[latestWarning.risk_level] || 'var(--border)'
  }

  return (
    <div className="card" style={{ borderColor: getBorderColor(), borderWidth: 2, transition: 'border-color 0.3s' }}>
      <div className="card-header" style={{ marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {enabled ? <Volume2 size={18} color="var(--accent-blue)" /> : <VolumeX size={18} color="var(--text-muted)" />}
          <span className="card-title">AI Voice Assistant</span>
        </div>
        <div className="badge" style={{ background: isActive ? 'var(--accent-green)' : 'var(--bg-secondary)', color: isActive ? '#000' : 'var(--text-muted)' }}>
          {isActive ? 'ACTIVE' : 'STANDBY'}
        </div>
      </div>

      <div style={{
        background: 'var(--bg-secondary)',
        borderRadius: 8,
        padding: 16,
        minHeight: 80,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        marginBottom: 16,
        position: 'relative'
      }}>
        {isActive && latestWarning ? (
          <>
            <div style={{ 
              fontSize: '0.7rem', 
              color: 'var(--text-muted)', 
              textTransform: 'uppercase',
              marginBottom: 4,
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span>{latestWarning.type?.replace('_', ' ')}</span>
              <span style={{ color: getBorderColor(), fontWeight: 700 }}>
                {latestWarning.risk_level} RISK
              </span>
            </div>
            <div style={{ fontSize: '1.05rem', fontWeight: 500, lineHeight: 1.4, color: 'var(--text-primary)' }}>
              "{latestWarning.message}"
            </div>
          </>
        ) : (
          <div style={{ color: 'var(--text-muted)', textAlign: 'center', fontSize: '0.85rem' }}>
            {isActive ? 'Monitoring road...' : 'Waiting for live session to start...'}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <button 
          onClick={toggleEnabled}
          className={`btn ${enabled ? 'btn-secondary' : ''}`}
          style={{ padding: '6px 12px', fontSize: '0.75rem' }}
        >
          {enabled ? <><Mic size={14} /> Mute Voice</> : <><MicOff size={14} /> Enable Voice</>}
        </button>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Vol</span>
          <input 
            type="range" 
            min="0" max="1" step="0.1" 
            value={volume} 
            onChange={handleVolume}
            style={{ width: 80, cursor: 'pointer' }}
          />
        </div>

        <button 
          onClick={replay}
          className="btn btn-secondary"
          disabled={!latestWarning || !isActive}
          style={{ padding: '6px 12px', fontSize: '0.75rem' }}
        >
          <RefreshCw size={14} /> Replay
        </button>
      </div>
    </div>
  )
}

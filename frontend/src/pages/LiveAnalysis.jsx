import { useState, useEffect } from 'react'
import { useLiveAnalysis } from '../hooks/useLiveAnalysis'
import TopHeader from '../components/TopHeader'
import VoiceAssistant from '../components/VoiceAssistant'
import EventTimeline from '../components/EventTimeline'
import RoutePanel from '../components/RoutePanel'
import LiveVideoOverlay from '../components/LiveVideoOverlay'
import GISMap from '../components/GISMap'
import { AlertCircle, StopCircle } from 'lucide-react'

export default function LiveAnalysis() {
  const busId = 'BUS-102' // Default demo bus for live analysis
  const { isActive, status, sessionData, error, startSession, stopSession } = useLiveAnalysis(busId)
  
  // Transform session warnings and gps for the map
  const [mapEvents, setMapEvents] = useState([])
  const [mapBuses, setMapBuses] = useState([])

  useEffect(() => {
    if (sessionData) {
      if (sessionData.warnings) {
        setMapEvents(sessionData.warnings)
      }
      if (sessionData.latest_gps) {
        setMapBuses([{
          bus_id: sessionData.bus_id,
          current_location: sessionData.latest_gps,
          status: 'active',
          traffic_level: sessionData.latest_traffic?.traffic_level || 'low'
        }])
      }
    }
  }, [sessionData])

  return (
    <>
      <TopHeader
        title="Live AI Road Safety Assistant"
        subtitle="Real-time video analysis with voice warnings and route intelligence"
        apiStatus="connected"
      />
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', minHeight: 'calc(100vh - 56px)' }}>
        
        {/* Main Grid */}
        <div style={{ display: 'flex', gap: 16, flex: 1 }}>
          
          {/* LEFT COLUMN: Video & Map */}
          <div style={{ flex: '1.5', display: 'flex', flexDirection: 'column', gap: 16, minWidth: 0 }}>
            {/* Video Player Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontSize: '1.1rem', margin: 0 }}>Live Camera Feed</h2>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span>Bus: <span style={{ color: 'var(--accent-blue)', fontFamily: 'var(--font-mono)' }}>{busId}</span></span>
                  <span>|</span>
                  <span style={{ color: 'var(--accent-yellow)' }}>⚡ Demo Simulation Mode</span>
                </div>
              </div>
              
              {isActive && (
                <button onClick={stopSession} className="btn btn-secondary" style={{ color: 'var(--accent-red)' }}>
                  <StopCircle size={16} /> Stop Live Analysis
                </button>
              )}
            </div>

            {error && (
              <div style={{ padding: 12, background: 'rgba(239,68,68,0.1)', color: 'var(--accent-red)', borderRadius: 8, fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertCircle size={16} /> {error}
              </div>
            )}

            {/* Video Overlay component */}
            <LiveVideoOverlay 
              frameBase64={sessionData?.latest_frame} 
              isActive={isActive}
              onStartDemo={() => startSession(true)}
              onStartCustom={(file) => startSession(false, file)}
            />

            {/* Map below video */}
            <div className="card" style={{ padding: 0, overflow: 'hidden', flex: 1, display: 'flex', flexDirection: 'column' }}>
              <div className="card-header" style={{ padding: '8px 16px', marginBottom: 0, borderBottom: '1px solid var(--border)' }}>
                <span className="card-title">Live Tracking</span>
              </div>
              <div style={{ flex: 1, minHeight: 200 }}>
                <GISMap events={mapEvents} buses={mapBuses} height="100%" />
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: AI Assistants */}
          <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: 16, minWidth: 320 }}>
            
            <VoiceAssistant 
              latestWarning={sessionData?.latest_warning} 
              isActive={isActive} 
            />

            <RoutePanel 
              recommendation={sessionData?.route_recommendation} 
            />

            <EventTimeline 
              warnings={sessionData?.warnings} 
            />
            
          </div>
        </div>
      </div>
    </>
  )
}

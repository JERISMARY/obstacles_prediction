import { useEffect, useRef, useState } from 'react'
import { Play, Upload } from 'lucide-react'

export default function LiveVideoOverlay({ frameBase64, isActive, onStartDemo, onStartCustom }) {
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      onStartCustom(file)
    }
  }

  if (!isActive && !frameBase64) {
    return (
      <div style={{
        width: '100%',
        aspectRatio: '16/9',
        background: '#000',
        borderRadius: 12,
        border: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ position: 'absolute', top: 16, left: 16, display: 'flex', gap: 8 }}>
          <div className="badge" style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>● OFFLINE</div>
        </div>
        
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', justifyContent: 'center' }}>
          <button 
            onClick={onStartDemo}
            className="btn btn-primary"
            style={{ padding: '12px 24px', fontSize: '1rem', borderRadius: 30 }}
          >
            <Play size={18} /> Play Demo Video
          </button>
          
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="btn btn-secondary"
            style={{ padding: '12px 24px', fontSize: '1rem', borderRadius: 30 }}
          >
            <Upload size={18} /> Upload Custom Video
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            accept="video/mp4,video/x-m4v,video/*" 
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </div>
        
        <div style={{ marginTop: 16, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Upload a driving video (.mp4) to test custom analysis.
        </div>
      </div>
    )
  }

  return (
    <div style={{
      width: '100%',
      aspectRatio: '16/9',
      background: '#000',
      borderRadius: 12,
      border: '1px solid var(--border-bright)',
      overflow: 'hidden',
      position: 'relative',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
    }}>
      {/* 
        The backend already draws bounding boxes and HUD text onto the frame using cv2.
        We just need to display it cleanly here.
      */}
      {frameBase64 ? (
        <img 
          src={`data:image/jpeg;base64,${frameBase64}`} 
          alt="Live Camera Feed"
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
      ) : (
        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="spinner" />
        </div>
      )}

      {/* Top HUD (overlaying the image) */}
      <div style={{ position: 'absolute', top: 16, right: 16, display: 'flex', gap: 8 }}>
        <div className="badge" style={{ background: 'rgba(34, 197, 94, 0.2)', color: 'var(--accent-green)', border: '1px solid var(--accent-green)' }}>
          ● LIVE
        </div>
      </div>
    </div>
  )
}

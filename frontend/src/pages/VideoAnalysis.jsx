import { useState, useRef } from 'react'
import { videoApi } from '../services/api'
import { useJobPoller } from '../hooks/useApi'
import TopHeader from '../components/TopHeader'
import { Upload, Play, CheckCircle, XCircle, Clock } from 'lucide-react'

const DEMO_BUSES = ['BUS-101', 'BUS-102', 'BUS-103', 'BUS-104', 'BUS-105']

export default function VideoAnalysis() {
  const [file, setFile] = useState(null)
  const [busId, setBusId] = useState('BUS-102')
  const [phase, setPhase] = useState('idle') // idle | uploading | processing | done | error
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadResult, setUploadResult] = useState(null)
  const [jobId, setJobId] = useState(null)
  const [error, setError] = useState(null)
  const fileRef = useRef()

  const { job } = useJobPoller(
    jobId,
    videoApi.status,
    2000,
  )

  const handleDrop = (e) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f) setFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    setPhase('uploading')
    setError(null)
    try {
      const result = await videoApi.upload(file, busId, setUploadProgress)
      setUploadResult(result)
      setPhase('uploaded')
    } catch (e) {
      setError(e.message)
      setPhase('error')
    }
  }

  const handleProcess = async () => {
    if (!uploadResult) return
    setPhase('processing')
    try {
      const result = await videoApi.process(uploadResult.upload_id, busId)
      setJobId(result.job_id)
    } catch (e) {
      setError(e.message)
      setPhase('error')
    }
  }

  // Watch job completion
  if (job?.status === 'completed' && phase === 'processing') setPhase('done')
  if (job?.status === 'failed' && phase === 'processing') {
    setPhase('error')
    setError(job.error_message)
  }

  const reset = () => {
    setFile(null); setBusId('BUS-102'); setPhase('idle')
    setUploadProgress(0); setUploadResult(null); setJobId(null); setError(null)
  }

  return (
    <>
      <TopHeader
        title="Video Analysis"
        subtitle="Upload road footage for AI detection pipeline"
        apiStatus="connected"
      />
      <div className="page-content">
        <div className="page-header">
          <div>
            <h1>Video Analysis</h1>
            <p>Upload bus camera footage → YOLO detection → Event generation → Dashboard update</p>
          </div>
        </div>

        {/* Pipeline diagram */}
        <div className="card mb-4">
          <div className="card-header"><span className="card-title">Detection Pipeline</span></div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 0, overflowX: 'auto', padding: '8px 0' }}>
            {['Upload Video', 'Extract Frames', 'YOLO Inference', 'Traffic Analysis', 'GPS Attach', 'Event Store', 'Dashboard'].map((step, i, arr) => (
              <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-bright)',
                  borderRadius: 6,
                  padding: '6px 12px',
                  fontSize: '0.72rem',
                  fontWeight: 500,
                  color: 'var(--accent-blue)',
                  whiteSpace: 'nowrap',
                }}>
                  {step}
                </div>
                {i < arr.length - 1 && (
                  <div style={{ padding: '0 4px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>→</div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          {/* Upload panel */}
          <div className="card">
            <div className="card-header"><span className="card-title">Upload & Configure</span></div>

            {phase === 'idle' || phase === 'error' ? (
              <>
                {/* Drop zone */}
                <div
                  className={`upload-zone ${file ? 'dragover' : ''}`}
                  onClick={() => fileRef.current?.click()}
                  onDrop={handleDrop}
                  onDragOver={e => e.preventDefault()}
                  style={{ marginBottom: 16 }}
                >
                  <input
                    ref={fileRef}
                    type="file"
                    accept="video/*"
                    onChange={e => setFile(e.target.files[0])}
                  />
                  <div style={{ fontSize: '2rem', marginBottom: 8 }}>🎬</div>
                  {file ? (
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--accent-blue)', fontSize: '0.85rem' }}>
                        {file.name}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>
                        {(file.size / 1024 / 1024).toFixed(1)} MB
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div style={{ fontWeight: 500, color: 'var(--text-secondary)' }}>
                        Drop video here or click to browse
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>
                        MP4, AVI, MOV, MKV — Max 500 MB
                      </div>
                    </div>
                  )}
                </div>

                {/* Bus selector */}
                <div style={{ marginBottom: 16 }}>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
                    Assign Bus ID
                  </label>
                  <select className="select" style={{ width: '100%' }} value={busId} onChange={e => setBusId(e.target.value)}>
                    {DEMO_BUSES.map(b => <option key={b} value={b}>{b}</option>)}
                  </select>
                </div>

                {error && (
                  <div style={{ color: 'var(--accent-red)', fontSize: '0.78rem', marginBottom: 12, padding: '8px 12px', background: 'rgba(239,68,68,0.1)', borderRadius: 6 }}>
                    ✗ {error}
                  </div>
                )}

                <button
                  className="btn btn-primary"
                  style={{ width: '100%', justifyContent: 'center' }}
                  onClick={handleUpload}
                  disabled={!file}
                >
                  <Upload size={14} /> Upload Video
                </button>
              </>
            ) : phase === 'uploading' ? (
              <div>
                <div style={{ marginBottom: 12, fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                  Uploading {file?.name}…
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
                </div>
                <div style={{ textAlign: 'right', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 6 }}>
                  {uploadProgress}%
                </div>
              </div>
            ) : phase === 'uploaded' ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16, color: 'var(--accent-green)', fontSize: '0.85rem' }}>
                  <CheckCircle size={16} /> Upload complete
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 16 }}>
                  <strong>File:</strong> {uploadResult?.original_filename}<br />
                  <strong>Size:</strong> {uploadResult?.size_mb} MB<br />
                  <strong>Bus:</strong> {busId}
                </div>
                <button
                  className="btn btn-primary"
                  style={{ width: '100%', justifyContent: 'center' }}
                  onClick={handleProcess}
                >
                  <Play size={14} /> Start AI Processing
                </button>
              </div>
            ) : null}
          </div>

          {/* Status panel */}
          <div className="card">
            <div className="card-header"><span className="card-title">Processing Status</span></div>

            {phase === 'idle' && (
              <div className="empty-state">
                <span style={{ fontSize: '2rem' }}>🎞️</span>
                <p>Upload a video to begin AI analysis</p>
              </div>
            )}

            {(phase === 'processing' || job) && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
                  {job?.status === 'completed' ? (
                    <CheckCircle size={16} color="var(--accent-green)" />
                  ) : job?.status === 'failed' ? (
                    <XCircle size={16} color="var(--accent-red)" />
                  ) : (
                    <div className="spinner" style={{ width: 16, height: 16 }} />
                  )}
                  <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>
                    {job?.status || 'Starting…'}
                  </span>
                </div>

                {job && (
                  <>
                    <div className="progress-bar" style={{ marginBottom: 8 }}>
                      <div className="progress-fill" style={{ width: `${job.progress || 0}%` }} />
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 16, fontFamily: 'var(--font-mono)' }}>
                      {job.processed_frames} / {job.total_frames} frames · {job.progress}%
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '0.78rem' }}>
                      <JobRow label="Job ID" value={job.job_id} />
                      <JobRow label="Bus" value={job.bus_id} />
                      <JobRow label="Events Generated" value={job.events_generated || 0} />
                      {job.error_message && (
                        <div style={{ color: 'var(--accent-red)', padding: '8px', background: 'rgba(239,68,68,0.1)', borderRadius: 6 }}>
                          ✗ {job.error_message}
                        </div>
                      )}
                    </div>

                    {job.result_summary && (
                      <div style={{ marginTop: 16 }}>
                        <div className="card-title" style={{ marginBottom: 8 }}>Results</div>
                        <div style={{ background: 'var(--bg-secondary)', borderRadius: 6, padding: 12, fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', overflowX: 'auto' }}>
                          {JSON.stringify(job.result_summary, null, 2)}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}

            {phase === 'done' && (
              <div style={{ marginTop: 16 }}>
                <div style={{ color: 'var(--accent-green)', marginBottom: 12, display: 'flex', gap: 8, alignItems: 'center' }}>
                  <CheckCircle size={16} /> Processing complete! Check the Dashboard for new incidents.
                </div>
                <button className="btn btn-secondary" onClick={reset} style={{ width: '100%', justifyContent: 'center' }}>
                  Process Another Video
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Model info */}
        <div className="card" style={{ marginTop: 16 }}>
          <div className="card-header"><span className="card-title">AI Model Status</span></div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
            <ModelCard
              name="Vehicle Detector"
              model="YOLOv8n (COCO)"
              classes="Car, Bus, Truck, Motorcycle, Pedestrian"
              status="ready"
            />
            <ModelCard
              name="Pothole Detector"
              model="Custom YOLO (Plug-in)"
              classes="Pothole, Road Damage, Waterlogging"
              status="demo"
              note="Demo Mode — plug in a trained model via POTHOLE_MODEL_PATH"
            />
            <ModelCard
              name="Traffic Analyzer"
              model="Rules-based (configurable)"
              classes="Density score · Level classification"
              status="ready"
            />
          </div>
        </div>
      </div>
    </>
  )
}

function JobRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0', borderBottom: '1px solid var(--border)' }}>
      <span style={{ color: 'var(--text-muted)' }}>{label}</span>
      <span style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{value}</span>
    </div>
  )
}

function ModelCard({ name, model, classes, status, note }) {
  const statusColor = status === 'ready' ? 'var(--accent-green)' : status === 'demo' ? 'var(--accent-yellow)' : 'var(--accent-red)'
  return (
    <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 14, border: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontWeight: 600, fontSize: '0.82rem' }}>{name}</span>
        <span style={{ color: statusColor, fontSize: '0.68rem', fontWeight: 600, textTransform: 'uppercase' }}>● {status}</span>
      </div>
      <div style={{ fontSize: '0.72rem', color: 'var(--accent-blue)', marginBottom: 4, fontFamily: 'var(--font-mono)' }}>{model}</div>
      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{classes}</div>
      {note && <div style={{ fontSize: '0.65rem', color: 'var(--accent-yellow)', marginTop: 8, lineHeight: 1.4 }}>ℹ {note}</div>}
    </div>
  )
}

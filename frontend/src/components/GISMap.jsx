import { useEffect, useRef } from 'react'
import L from 'leaflet'
import { severityColor, eventTypeIcon, eventTypeLabel, formatConfidence, formatDateTime, formatLatLon } from '../utils/format'

// Fix Leaflet icon paths
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

function buildEventPopupHtml(evt) {
  const sColor = severityColor(evt.severity)
  const demoTag = evt.is_demo
    ? `<div style="background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.3);border-radius:4px;padding:3px 8px;font-size:0.65rem;color:#fbbf24;margin-bottom:8px;text-align:center;">⚡ DEMO DATA — Simulated</div>`
    : ''
  const row = (label, value) =>
    `<div class="popup-row"><span class="popup-row-label">${label}</span><span class="popup-row-value">${value}</span></div>`
  const evidence = evt.evidence_image
    ? `<div style="margin-top:10px"><img src="${evt.evidence_image}" alt="Evidence" style="width:100%;border-radius:4px;border:1px solid var(--border)" /></div>`
    : ''
  const vehicles = evt.vehicle_count != null ? row('Vehicles', `${evt.vehicle_count} detected`) : ''
  const density = evt.traffic_density != null ? row('Density', `${evt.traffic_density}%`) : ''

  return `<div class="popup-content">
    <div class="popup-title">${eventTypeIcon(evt.type)} ${eventTypeLabel(evt.type)}</div>
    ${demoTag}
    ${row('Event ID', `<span class="mono" style="font-size:0.7rem">${evt.event_id}</span>`)}
    ${row('Severity', `<span style="color:${sColor};text-transform:uppercase;font-weight:700;font-size:0.75rem">${evt.severity}</span>`)}
    ${row('Confidence', formatConfidence(evt.confidence))}
    ${row('Bus', `<span class="mono">${evt.bus_id}</span>`)}
    ${row('Status', `<span class="badge badge-${evt.status}">${(evt.status||'').replace('_',' ')}</span>`)}
    ${row('Location', `<span class="mono" style="font-size:0.68rem">${formatLatLon(evt.latitude, evt.longitude)}</span>`)}
    ${row('Time', formatDateTime(evt.timestamp))}
    ${vehicles}${density}
    ${evt.description ? `<div style="margin-top:8px;font-size:0.72rem;color:var(--text-muted);line-height:1.4">${evt.description}</div>` : ''}
    ${evidence}
  </div>`
}

const createIncidentIcon = (event) => {
  const color = severityColor(event.severity)
  const icon = eventTypeIcon(event.type)
  return L.divIcon({
    className: '',
    html: `
      <div style="
        background: ${color}22;
        border: 2px solid ${color};
        border-radius: 50%;
        width: 32px; height: 32px;
        display: flex; align-items: center; justify-content: center;
        font-size: 15px;
        box-shadow: 0 0 12px ${color}66;
        cursor: pointer;
      ">${icon}</div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  })
}

const createBusIcon = (bus) => {
  const colors = { active: '#34d399', inactive: '#475569', maintenance: '#fbbf24' }
  const color = colors[bus.status] || '#94a3b8'
  return L.divIcon({
    className: '',
    html: `
      <div style="
        background: ${color}22;
        border: 2px solid ${color};
        border-radius: 6px;
        width: 36px; height: 28px;
        display: flex; align-items: center; justify-content: center;
        font-size: 16px;
        box-shadow: 0 0 10px ${color}55;
        cursor: pointer;
      ">🚌</div>
    `,
    iconSize: [36, 28],
    iconAnchor: [18, 14],
  })
}

export default function GISMap({ events = [], buses = [], showHeatmap = false, height = 460 }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const layersRef = useRef({ events: [], buses: [], heatmap: [] })

  // Init map once
  useEffect(() => {
    if (mapInstanceRef.current) return

    const map = L.map(mapRef.current, {
      center: [9.9252, 78.1198],
      zoom: 14,
      zoomControl: true,
      attributionControl: false,
    })

    // Dark OSM tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap © CARTO',
      subdomains: 'abcd',
      maxZoom: 20,
    }).addTo(map)

    mapInstanceRef.current = map
    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [])

  // Update event markers
  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map) return

    // Clear old
    layersRef.current.events.forEach(m => map.removeLayer(m))
    layersRef.current.events = []

    events.forEach(evt => {
      if (!evt.latitude || !evt.longitude) return

      const marker = L.marker([evt.latitude, evt.longitude], {
        icon: createIncidentIcon(evt),
      })

      const popupHtml = buildEventPopupHtml(evt)
      marker.bindPopup(popupHtml, {
        maxWidth: 280,
        className: 'urban-popup',
      })

      marker.addTo(map)
      layersRef.current.events.push(marker)
    })
  }, [events])

  // Update bus markers
  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map) return

    layersRef.current.buses.forEach(m => map.removeLayer(m))
    layersRef.current.buses = []

    buses.forEach(bus => {
      const loc = bus.current_location
      if (!loc?.latitude || !loc?.longitude) return

      const marker = L.marker([loc.latitude, loc.longitude], {
        icon: createBusIcon(bus),
        zIndexOffset: 1000,
      })

      marker.bindPopup(`
        <div class="popup-content">
          <div class="popup-title">🚌 ${bus.bus_id}</div>
          <div class="popup-row">
            <span class="popup-row-label">Route</span>
            <span class="popup-row-value">${bus.route_name || '—'}</span>
          </div>
          <div class="popup-row">
            <span class="popup-row-label">Status</span>
            <span class="badge badge-${bus.status}">${bus.status}</span>
          </div>
          <div class="popup-row">
            <span class="popup-row-label">Traffic</span>
            <span class="popup-row-value traffic-${bus.traffic_level || 'low'}">${(bus.traffic_level || 'low').toUpperCase()}</span>
          </div>
          <div class="popup-row">
            <span class="popup-row-label">Speed</span>
            <span class="popup-row-value">${loc.speed_kmh?.toFixed(1) || 0} km/h</span>
          </div>
          <div class="popup-row">
            <span class="popup-row-label">Incidents</span>
            <span class="popup-row-value">${bus.incident_count || 0}</span>
          </div>
          ${bus.is_demo ? '<div style="text-align:center;font-size:0.65rem;color:#fbbf24;margin-top:6px">⚡ DEMO DATA</div>' : ''}
        </div>
      `, { maxWidth: 260, className: 'urban-popup' })

      marker.addTo(map)
      layersRef.current.buses.push(marker)
    })
  }, [buses])

  return (
    <div
      ref={mapRef}
      className="map-container"
      style={{ height }}
      id="gis-map"
    />
  )
}

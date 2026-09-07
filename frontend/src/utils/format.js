import { format, formatDistanceToNow, parseISO } from 'date-fns'

export const formatTime = (ts) => {
  if (!ts) return '—'
  try {
    const d = typeof ts === 'string' ? parseISO(ts) : new Date(ts)
    return format(d, 'HH:mm:ss')
  } catch { return ts }
}

export const formatDateTime = (ts) => {
  if (!ts) return '—'
  try {
    const d = typeof ts === 'string' ? parseISO(ts) : new Date(ts)
    return format(d, 'dd MMM yyyy, HH:mm')
  } catch { return ts }
}

export const formatRelative = (ts) => {
  if (!ts) return '—'
  try {
    const d = typeof ts === 'string' ? parseISO(ts) : new Date(ts)
    return formatDistanceToNow(d, { addSuffix: true })
  } catch { return ts }
}

export const formatLatLon = (lat, lon) => {
  if (lat == null || lon == null) return '—'
  return `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`
}

export const formatConfidence = (c) => {
  if (c == null) return '—'
  return `${Math.round(c * 100)}%`
}

export const eventTypeLabel = (type) => {
  const labels = {
    pothole: 'Pothole',
    road_damage: 'Road Damage',
    waterlogging: 'Waterlogging',
    traffic_sign_damage: 'Sign Damage',
    traffic_congestion: 'Congestion',
    accident: 'Accident',
    other: 'Other',
  }
  return labels[type] || type
}

export const eventTypeIcon = (type) => {
  const icons = {
    pothole: '🕳️',
    road_damage: '🚧',
    waterlogging: '💧',
    traffic_sign_damage: '🚦',
    traffic_congestion: '🚗',
    accident: '💥',
    other: '⚠️',
  }
  return icons[type] || '📍'
}

export const severityColor = (severity) => {
  const colors = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#22c55e',
  }
  return colors[severity] || '#94a3b8'
}

export const trafficLevelColor = (level) => {
  const colors = {
    severe: '#ef4444',
    high: '#f97316',
    moderate: '#eab308',
    low: '#22c55e',
  }
  return colors[level] || '#94a3b8'
}

export const statusColor = (status) => {
  const colors = {
    new: '#38bdf8',
    verified: '#a78bfa',
    in_progress: '#fbbf24',
    resolved: '#34d399',
  }
  return colors[status] || '#94a3b8'
}

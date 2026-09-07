import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { voiceService } from '../services/voiceService'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useLiveAnalysis(busId) {
  const [isActive, setIsActive] = useState(false)
  const [status, setStatus] = useState('idle') // idle, starting, running, error
  const [sessionData, setSessionData] = useState(null)
  const [error, setError] = useState(null)
  
  const timerRef = useRef(null)

  const startSession = async (useDemoVideo = true, file = null) => {
    try {
      setStatus('starting')
      setError(null)
      
      const formData = new FormData()
      formData.append('bus_id', busId)
      formData.append('use_demo_video', useDemoVideo)
      if (file) {
        formData.append('file', file)
      }

      await axios.post(`${BASE_URL}/api/live/start`, formData)
      setIsActive(true)
      setStatus('running')
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
      setStatus('error')
    }
  }

  const stopSession = async () => {
    try {
      await axios.post(`${BASE_URL}/api/live/stop`)
      setIsActive(false)
      setStatus('idle')
      if (timerRef.current) clearInterval(timerRef.current)
    } catch (err) {
      console.error("Failed to stop session", err)
    }
  }

  const pollStatus = async () => {
    if (!isActive) return
    try {
      const res = await axios.get(`${BASE_URL}/api/live/status`)
      const data = res.data
      
      if (!data.active && data.status !== 'created') {
        setIsActive(false)
        setStatus(data.status || 'stopped')
        if (timerRef.current) clearInterval(timerRef.current)
      }
      
      setSessionData(data)
      
      // Check for new warning to speak
      if (data.latest_warning && data.latest_warning.speak) {
        // Prevent re-speaking the same warning on subsequent polls
        // The backend guarantees a unique warning_id per spoken warning
        const lastSpokenId = sessionStorage.getItem('lastSpokenWarningId')
        if (lastSpokenId !== data.latest_warning.warning_id) {
          voiceService.speak(data.latest_warning.message, data.latest_warning.priority)
          sessionStorage.setItem('lastSpokenWarningId', data.latest_warning.warning_id)
        }
      }
      
    } catch (err) {
      console.error("Poll error", err)
    }
  }

  useEffect(() => {
    if (isActive) {
      pollStatus()
      timerRef.current = setInterval(pollStatus, 1000)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isActive])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopSession()
    }
  }, [])

  return {
    isActive,
    status,
    sessionData,
    error,
    startSession,
    stopSession
  }
}

import { useState, useEffect, useCallback, useRef } from 'react'

/**
 * Generic data fetching hook with loading/error state and auto-refresh.
 */
export function useApi(fetchFn, deps = [], options = {}) {
  const { refreshInterval = null, enabled = true } = options
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const timerRef = useRef(null)

  const fetch = useCallback(async () => {
    if (!enabled) return
    try {
      setLoading(true)
      const result = await fetchFn()
      setData(result)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [enabled, ...deps])

  useEffect(() => {
    fetch()
    if (refreshInterval) {
      timerRef.current = setInterval(fetch, refreshInterval)
      return () => clearInterval(timerRef.current)
    }
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

/**
 * Poll a job until it completes or fails.
 */
export function useJobPoller(jobId, pollFn, interval = 2000) {
  const [job, setJob] = useState(null)
  const [polling, setPolling] = useState(false)
  const timerRef = useRef(null)

  const stop = useCallback(() => {
    setPolling(false)
    if (timerRef.current) clearInterval(timerRef.current)
  }, [])

  useEffect(() => {
    if (!jobId) return
    setPolling(true)

    const poll = async () => {
      try {
        const result = await pollFn(jobId)
        setJob(result)
        if (result.status === 'completed' || result.status === 'failed') {
          stop()
        }
      } catch (e) {
        console.error('Poll error:', e)
      }
    }

    poll()
    timerRef.current = setInterval(poll, interval)
    return () => clearInterval(timerRef.current)
  }, [jobId])

  return { job, polling, stop }
}

/**
 * Clock hook — returns current time string, refreshes every second.
 */
export function useClock() {
  const [time, setTime] = useState(new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return time
}

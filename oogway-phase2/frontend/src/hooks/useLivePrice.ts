import { useState, useEffect, useRef, useCallback } from "react"

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"
const POLL_INTERVAL_MS = 60_000  // poll every 60 seconds

interface LivePrice {
  ticker: string
  price: number
  change: number
  change_pct: number
  open: number
  high: number
  low: number
  volume: number
  prev_close: number
  timestamp: string
  delay_note: string
}

interface MarketStatus {
  is_open: boolean
  status: "Open" | "Closed"
  local_time: string
  hours: string
}

interface UseLivePriceReturn {
  data: LivePrice | null
  loading: boolean
  error: string | null
  lastUpdated: Date | null
  marketStatus: MarketStatus | null
  refresh: () => void
}

export function useLivePrice(ticker: string | null): UseLivePriceReturn {
  const [data, setData] = useState<LivePrice | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null)

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const tickerRef = useRef(ticker)
  tickerRef.current = ticker

  const fetchMarketStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/prices/market/status`)
      if (res.ok) {
        const status = await res.json()
        setMarketStatus(status)
        return status.is_open as boolean
      }
    } catch {
      // market status fetch failed silently
    }
    return false
  }, [])

  const fetchPrice = useCallback(async () => {
    if (!tickerRef.current) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/prices/${tickerRef.current}/live`)
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || "Failed to fetch price")
      }
      const price: LivePrice = await res.json()
      setData(price)
      setLastUpdated(new Date())
    } catch (e: any) {
      setError(e.message || "Price fetch failed")
    } finally {
      setLoading(false)
    }
  }, [])

  const startPolling = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    intervalRef.current = setInterval(async () => {
      const isOpen = await fetchMarketStatus()
      // Only poll during market hours to save API calls
      if (isOpen) {
        fetchPrice()
      }
    }, POLL_INTERVAL_MS)
  }, [fetchMarketStatus, fetchPrice])

  useEffect(() => {
    if (!ticker) {
      setData(null)
      setError(null)
      return
    }

    // Immediate fetch on mount or ticker change
    fetchMarketStatus()
    fetchPrice()

    // Start polling loop
    startPolling()

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [ticker])

  return {
    data,
    loading,
    error,
    lastUpdated,
    marketStatus,
    refresh: fetchPrice,
  }
}

import { useState, useEffect } from "react"

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

export interface OHLCVBar {
  time?: string   // intraday
  date?: string   // daily history
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface UseChartDataReturn {
  data: OHLCVBar[]
  loading: boolean
  error: string | null
}

// Hook for intraday candlestick data (today's session)
export function useIntradayData(
  ticker: string | null,
  interval: string = "5m"
): UseChartDataReturn {
  const [data, setData] = useState<OHLCVBar[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!ticker) return
    setLoading(true)
    setError(null)

    fetch(`${API_BASE}/api/prices/${ticker}/intraday?interval=${interval}`)
      .then(res => {
        if (!res.ok) throw new Error("No intraday data available")
        return res.json()
      })
      .then(json => setData(json.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [ticker, interval])

  return { data, loading, error }
}

// Hook for daily OHLCV history (for the main chart)
export function usePriceHistory(
  ticker: string | null,
  period: string = "1y"
): UseChartDataReturn {
  const [data, setData] = useState<OHLCVBar[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!ticker) return
    setLoading(true)
    setError(null)

    fetch(`${API_BASE}/api/prices/${ticker}/history?period=${period}`)
      .then(res => {
        if (!res.ok) throw new Error("No historical data available")
        return res.json()
      })
      .then(json => setData(json.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [ticker, period])

  return { data, loading, error }
}

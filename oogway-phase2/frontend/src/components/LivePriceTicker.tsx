import { useLivePrice } from "../hooks/useLivePrice"

interface Props {
  ticker: string
  companyName: string
}

export function LivePriceTicker({ ticker, companyName }: Props) {
  const { data, loading, error, lastUpdated, marketStatus, refresh } = useLivePrice(ticker)

  const isUp = data && data.change >= 0

  return (
    <div style={{
      background: "var(--color-background-primary)",
      border: "1px solid var(--color-border-tertiary)",
      borderRadius: "12px",
      padding: "20px 24px",
    }}>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
        <div>
          <div style={{ fontSize: "14px", fontWeight: 500 }}>{companyName}</div>
          <div style={{ fontSize: "11px", color: "var(--color-text-secondary)", fontFamily: "monospace", marginTop: "2px" }}>
            PSX: {ticker} &nbsp;·&nbsp; {ticker}.KA
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {/* Market status pill */}
          {marketStatus && (
            <div style={{
              display: "flex", alignItems: "center", gap: "5px",
              fontSize: "10px", fontFamily: "monospace",
              padding: "4px 10px", borderRadius: "99px",
              background: marketStatus.is_open ? "var(--color-background-success)" : "var(--color-background-secondary)",
              color: marketStatus.is_open ? "var(--color-text-success)" : "var(--color-text-tertiary)",
              border: `1px solid ${marketStatus.is_open ? "var(--color-border-success)" : "var(--color-border-tertiary)"}`,
            }}>
              <div style={{
                width: "6px", height: "6px", borderRadius: "50%",
                background: marketStatus.is_open ? "var(--color-text-success)" : "var(--color-text-tertiary)",
                animation: marketStatus.is_open ? "pulse 1s infinite" : "none",
              }} />
              {marketStatus.status} &nbsp;·&nbsp; {marketStatus.local_time}
            </div>
          )}

          {/* Refresh button */}
          <button
            onClick={refresh}
            style={{
              fontSize: "11px", fontFamily: "monospace",
              padding: "4px 10px", borderRadius: "6px",
              background: "none", border: "1px solid var(--color-border-secondary)",
              cursor: "pointer", color: "var(--color-text-secondary)",
            }}
          >
            {loading ? "..." : "Refresh"}
          </button>
        </div>
      </div>

      {/* Price display */}
      {error ? (
        <div style={{ fontSize: "13px", color: "var(--color-text-danger)", padding: "12px 0" }}>
          {error}
        </div>
      ) : loading && !data ? (
        <div style={{ fontSize: "13px", color: "var(--color-text-secondary)", padding: "12px 0" }}>
          Loading price...
        </div>
      ) : data ? (
        <>
          <div style={{ display: "flex", alignItems: "baseline", gap: "12px", marginBottom: "12px" }}>
            <span style={{
              fontFamily: "monospace", fontSize: "36px", fontWeight: 500,
              color: isUp ? "var(--color-text-success)" : "var(--color-text-danger)",
            }}>
              PKR {data.price.toLocaleString()}
            </span>
            <span style={{
              fontFamily: "monospace", fontSize: "14px",
              color: isUp ? "var(--color-text-success)" : "var(--color-text-danger)",
            }}>
              {isUp ? "+" : ""}{data.change} ({isUp ? "+" : ""}{data.change_pct}%)
            </span>
          </div>

          {/* OHLV row */}
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(4, 1fr)",
            gap: "8px", marginBottom: "12px",
          }}>
            {[
              { label: "OPEN",  value: data.open },
              { label: "HIGH",  value: data.high },
              { label: "LOW",   value: data.low },
              { label: "PREV",  value: data.prev_close },
            ].map(item => (
              <div key={item.label} style={{
                background: "var(--color-background-secondary)",
                borderRadius: "8px", padding: "8px 10px",
              }}>
                <div style={{ fontSize: "9px", fontFamily: "monospace", color: "var(--color-text-tertiary)", marginBottom: "3px" }}>
                  {item.label}
                </div>
                <div style={{ fontSize: "13px", fontWeight: 500, fontFamily: "monospace" }}>
                  {item.value.toLocaleString()}
                </div>
              </div>
            ))}
          </div>

          {/* Volume */}
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            fontSize: "11px", fontFamily: "monospace", color: "var(--color-text-secondary)",
          }}>
            <span>Volume: {data.volume.toLocaleString()}</span>
            {lastUpdated && (
              <span>Updated {lastUpdated.toLocaleTimeString()} &nbsp;·&nbsp; {data.delay_note}</span>
            )}
          </div>
        </>
      ) : null}

    </div>
  )
}

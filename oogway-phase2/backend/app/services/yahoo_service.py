import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime


# PSX tickers use .KA suffix on Yahoo Finance
def to_yahoo_symbol(ticker: str) -> str:
    if ticker.endswith(".KA"):
        return ticker
    return f"{ticker}.KA"


def get_company_info(ticker: str) -> dict:
    """
    Fetch basic company info and fundamentals from Yahoo Finance.
    Returns a flat dict of financial fields we need for analysis.
    """
    symbol = to_yahoo_symbol(ticker)
    stock = yf.Ticker(symbol)
    info = stock.info

    return {
        "ticker":       ticker,
        "name":         info.get("longName") or info.get("shortName", ticker),
        "sector":       info.get("sector", "PSX Listed"),
        "market_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "market_cap":   info.get("marketCap"),
        "eps":          info.get("trailingEps"),
        "bvps":         info.get("bookValue"),
        "pe":           info.get("trailingPE"),
        "pb":           info.get("priceToBook"),
        "roe":          info.get("returnOnEquity"),
        "roa":          info.get("returnOnAssets"),
        "revenue":      info.get("totalRevenue"),
        "net_income":   info.get("netIncomeToCommon"),
        "gross_profit": info.get("grossProfits"),
        "ebit":         info.get("ebit"),
        "total_assets":       info.get("totalAssets"),
        "total_liabilities":  info.get("totalDebt"),
        "total_equity":       info.get("totalStockholderEquity"),
        "current_assets":     info.get("totalCurrentAssets"),
        "current_liabilities":info.get("totalCurrentLiabilities"),
        "operating_cash_flow":info.get("operatingCashflow"),
        "debt_to_equity":     info.get("debtToEquity"),
        "current_ratio":      info.get("currentRatio"),
        "quick_ratio":        info.get("quickRatio"),
        "gross_margin":       info.get("grossMargins"),
        "net_margin":         info.get("profitMargins"),
        "operating_margin":   info.get("operatingMargins"),
    }


def get_price_history(ticker: str, period: str = "1y") -> list:
    """
    Fetch OHLCV candlestick data for the given period.
    period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
    Returns list of dicts ready for the frontend chart.
    """
    symbol = to_yahoo_symbol(ticker)
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)

    if hist.empty:
        return []

    records = []
    for date, row in hist.iterrows():
        records.append({
            "date":   date.strftime("%Y-%m-%d"),
            "open":   round(row["Open"], 2),
            "high":   round(row["High"], 2),
            "low":    round(row["Low"], 2),
            "close":  round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })
    return records


def get_current_price(ticker: str) -> Optional[float]:
    """Fetch just the latest closing price."""
    symbol = to_yahoo_symbol(ticker)
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d")
    if hist.empty:
        return None
    return round(float(hist["Close"].iloc[-1]), 2)


def get_live_price(ticker: str) -> dict:
    """
    Fetch the latest intraday price snapshot.
    Uses 1-minute interval data — gives the most recent available price.
    15-20 min delayed on Yahoo Finance free tier.
    Falls back to daily close if intraday is unavailable.
    """
    symbol = to_yahoo_symbol(ticker)
    stock = yf.Ticker(symbol)

    hist = stock.history(period="1d", interval="1m")
    interval_used = "1m"

    if hist.empty:
        hist = stock.history(period="2d", interval="1d")
        interval_used = "1d"
        if hist.empty:
            return {}

    latest = hist.iloc[-1]
    prev = hist.iloc[-2] if len(hist) > 1 else None

    price = round(float(latest["Close"]), 2)
    prev_close = round(float(prev["Close"]), 2) if prev is not None else price
    change = round(price - prev_close, 2)
    change_pct = round((change / prev_close) * 100, 2) if prev_close else 0

    return {
        "ticker":      ticker,
        "symbol":      symbol,
        "price":       price,
        "open":        round(float(latest["Open"]), 2),
        "high":        round(float(latest["High"]), 2),
        "low":         round(float(latest["Low"]), 2),
        "volume":      int(latest["Volume"]),
        "prev_close":  prev_close,
        "change":      change,
        "change_pct":  change_pct,
        "timestamp":   str(latest.name),
        "interval":    interval_used,
        "delay_note":  "15-20 min delayed (Yahoo Finance free tier)",
    }


def get_intraday_history(ticker: str, interval: str = "5m") -> list:
    """
    Fetch intraday OHLCV for today's session.
    interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m
    Powers the intraday candlestick chart on the frontend.
    Only 7 days of intraday data available on free tier.
    """
    valid = ["1m", "2m", "5m", "15m", "30m", "60m", "90m"]
    if interval not in valid:
        interval = "5m"

    symbol = to_yahoo_symbol(ticker)
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval=interval)

    if hist.empty:
        return []

    return [
        {
            "time":   date.strftime("%H:%M"),
            "open":   round(row["Open"], 2),
            "high":   round(row["High"], 2),
            "low":    round(row["Low"], 2),
            "close":  round(row["Close"], 2),
            "volume": int(row["Volume"]),
        }
        for date, row in hist.iterrows()
    ]


def is_market_open() -> dict:
    """
    Check if PSX is currently open.
    PSX trading hours: Monday to Friday, 09:15 to 15:30 PKT (UTC+5).
    """
    from datetime import datetime, timezone, timedelta
    pkt = timezone(timedelta(hours=5))
    now = datetime.now(pkt)
    current_mins = now.hour * 60 + now.minute

    is_open = (
        now.weekday() < 5 and
        (9 * 60 + 15) <= current_mins <= (15 * 60 + 30)
    )

    return {
        "is_open":    is_open,
        "status":     "Open" if is_open else "Closed",
        "local_time": now.strftime("%H:%M PKT"),
        "hours":      "Mon-Fri 09:15 to 15:30 PKT",
    }

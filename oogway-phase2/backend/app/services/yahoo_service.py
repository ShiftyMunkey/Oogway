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


def get_full_fundamentals(ticker: str) -> Optional[dict]:
    """
    Live fallback for tickers with no curated FY2023 entry in FINANCIAL_DB.

    Pulls the balance sheet, income statement, and cash flow statement from
    Yahoo Finance — current year AND prior year, where available — and
    shapes the result exactly like a FINANCIAL_DB entry so the same
    calc_altman_zscore / calc_piotroski / calc_graham_number functions run
    unchanged on it.

    Known limitations (on the record, not hidden):
    - "shares_issued" (Piotroski's no-dilution check) can't be reliably
      derived from Yahoo's data for most PSX tickers, so it defaults to
      False (assume no dilution). This can slightly inflate the Piotroski
      score for companies using this fallback path.
    - Yahoo's statement coverage for smaller / thinly-traded PSX names is
      often incomplete. If the essentials (total assets, total
      liabilities, revenue) aren't available, this returns None rather
      than a half-built, misleading result.
    - This is live/current data, not a specific audited annual report —
      unlike the curated FINANCIAL_DB entries, there's no fixed fiscal
      year attached to it.
    """
    symbol = to_yahoo_symbol(ticker)
    stock = yf.Ticker(symbol)

    def safe(fn):
        try:
            return fn()
        except Exception:
            return None

    info = safe(lambda: stock.info) or {}
    bs = safe(lambda: stock.balance_sheet)
    inc = safe(lambda: stock.financials)
    cf = safe(lambda: stock.cashflow)

    def two_years(df, *labels):
        """First matching row label -> (most_recent_value, prior_year_value)."""
        if df is None or df.empty:
            return None, None
        for label in labels:
            if label in df.index:
                vals = [float(v) for v in df.loc[label] if pd.notna(v)]
                cur = vals[0] if len(vals) > 0 else None
                prev = vals[1] if len(vals) > 1 else None
                return cur, prev
        return None, None

    total_assets, total_assets_prev = two_years(bs, "Total Assets")
    total_liabilities, total_liabilities_prev = two_years(
        bs, "Total Liabilities Net Minority Interest", "Total Liab")
    total_equity, total_equity_prev = two_years(
        bs, "Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity")
    current_assets, current_assets_prev = two_years(
        bs, "Current Assets", "Total Current Assets")
    current_liabilities, current_liabilities_prev = two_years(
        bs, "Current Liabilities", "Total Current Liabilities")
    retained_earnings, _ = two_years(bs, "Retained Earnings")

    revenue, revenue_prev = two_years(inc, "Total Revenue", "Operating Revenue")
    net_income, net_income_prev = two_years(
        inc, "Net Income", "Net Income Common Stockholders")
    ebit, ebit_prev = two_years(inc, "EBIT", "Operating Income")
    gross_profit, gross_profit_prev = two_years(inc, "Gross Profit")

    operating_cash_flow, _ = two_years(
        cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")

    # Bare minimum to run any model at all — without these, every
    # downstream ratio is meaningless, so bail out cleanly instead of
    # returning a half-built result.
    if not total_assets or not total_liabilities or not revenue:
        return None

    current_ratio = (current_assets / current_liabilities) if current_assets and current_liabilities else None
    current_ratio_prev = (current_assets_prev / current_liabilities_prev) if current_assets_prev and current_liabilities_prev else None

    gross_margin = (gross_profit / revenue) if gross_profit and revenue else info.get("grossMargins")
    gross_margin_prev = (gross_profit_prev / revenue_prev) if gross_profit_prev and revenue_prev else None
    net_margin = (net_income / revenue) if net_income and revenue else info.get("profitMargins")

    roa = (net_income / total_assets) if net_income and total_assets else info.get("returnOnAssets")
    roa_prev = (net_income_prev / total_assets_prev) if net_income_prev and total_assets_prev else None
    roe = (net_income / total_equity) if net_income and total_equity else info.get("returnOnEquity")

    debt_to_equity = (total_liabilities / total_equity) if total_liabilities and total_equity else info.get("debtToEquity")
    leverage_prev = (total_liabilities_prev / total_equity_prev) if total_liabilities_prev and total_equity_prev else None

    asset_turnover_prev = (revenue_prev / total_assets_prev) if revenue_prev and total_assets_prev else None

    return {
        "name": info.get("longName") or info.get("shortName") or ticker,
        "sector": info.get("sector") or "PSX Listed",
        "fiscal_year": None,
        "revenue": revenue, "net_income": net_income, "ebit": ebit,
        "gross_profit": gross_profit, "total_assets": total_assets,
        "total_liabilities": total_liabilities, "total_equity": total_equity,
        "current_assets": current_assets, "current_liabilities": current_liabilities,
        "retained_earnings": retained_earnings, "operating_cash_flow": operating_cash_flow,
        "market_cap": info.get("marketCap"), "eps": info.get("trailingEps"), "bvps": info.get("bookValue"),
        "roe": roe, "roa": roa, "gross_margin": gross_margin,
        "net_margin": net_margin, "current_ratio": current_ratio, "quick_ratio": info.get("quickRatio"),
        "debt_to_equity": debt_to_equity, "interest_coverage": None,
        "pe": info.get("trailingPE"), "pb": info.get("priceToBook"),
        "roa_prev": roa_prev, "leverage_prev": leverage_prev,
        "current_ratio_prev": current_ratio_prev, "gross_margin_prev": gross_margin_prev,
        "asset_turnover_prev": asset_turnover_prev,
        "shares_issued": False,
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

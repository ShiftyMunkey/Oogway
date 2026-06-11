from fastapi import APIRouter, HTTPException
from app.services.yahoo_service import (
    get_price_history,
    get_current_price,
    get_live_price,
    get_intraday_history,
    is_market_open,
)

router = APIRouter()


@router.get("/market/status")
def market_status():
    """
    Check if PSX is currently open.
    Frontend uses this to decide whether to start polling.
    """
    return is_market_open()


@router.get("/{ticker}/live")
def live_price(ticker: str):
    """
    Latest price snapshot with change, volume, high/low.
    15-20 min delayed on Yahoo Finance free tier.
    Poll this every 60 seconds during market hours.
    """
    data = get_live_price(ticker.upper())
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No live price data for {ticker}. Verify {ticker}.KA exists on Yahoo Finance."
        )
    return data


@router.get("/{ticker}/intraday")
def intraday(ticker: str, interval: str = "5m"):
    """
    Intraday OHLCV for today's session. Powers the intraday candlestick chart.
    interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m
    Only 7 days of intraday history on free tier.
    """
    valid = ["1m", "2m", "5m", "15m", "30m", "60m", "90m"]
    if interval not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid interval. Choose from: {', '.join(valid)}")

    data = get_intraday_history(ticker.upper(), interval)
    if not data:
        raise HTTPException(status_code=404, detail=f"No intraday data for {ticker}. Market may be closed.")

    return {"ticker": ticker.upper(), "interval": interval, "count": len(data), "data": data}


@router.get("/{ticker}/current")
def current_price(ticker: str):
    """Just the latest closing price as a single number."""
    price = get_current_price(ticker.upper())
    if price is None:
        raise HTTPException(status_code=404, detail=f"No price data for {ticker}")
    return {"ticker": ticker.upper(), "price": price}


@router.get("/{ticker}/history")
def price_history(ticker: str, period: str = "1y"):
    """
    Daily OHLCV history for candlestick charts.
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
    """
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Invalid period. Choose from: {', '.join(valid_periods)}")

    data = get_price_history(ticker.upper(), period)
    if not data:
        raise HTTPException(status_code=404, detail=f"No historical data for {ticker}.")

    return {"ticker": ticker.upper(), "period": period, "count": len(data), "data": data}

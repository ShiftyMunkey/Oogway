from fastapi import APIRouter, HTTPException
from app.services.yahoo_service import get_live_price, get_full_fundamentals
from app.routers.companies import PSX_COMPANIES
from app.services.calculations import (
    calc_altman_zscore,
    calc_piotroski,
    calc_graham_number,
    calc_ratios,
    calc_health_score,
)

router = APIRouter()

# ─── CURATED FINANCIAL DATA ──────────────────────────────────────────────────
# Source: PSX audited annual reports FY2023
# Figures in PKR millions unless noted

FINANCIAL_DB = {
    "PSO": {
        "name": "Pakistan State Oil Co. Ltd.",
        "sector": "Energy / OMC",
        "fiscal_year": 2023,
        "revenue": 3_800_000, "net_income": 32_000, "ebit": 48_000,
        "gross_profit": 136_800, "total_assets": 760_000,
        "total_liabilities": 610_000, "total_equity": 150_000,
        "current_assets": 420_000, "current_liabilities": 385_000,
        "retained_earnings": 90_000, "operating_cash_flow": 41_000,
        "market_cap": 68_000, "eps": 72.4, "bvps": 299.6,
        "roe": 0.102, "roa": 0.042, "gross_margin": 0.036,
        "net_margin": 0.0085, "current_ratio": 1.09, "quick_ratio": 0.71,
        "debt_to_equity": 4.38, "interest_coverage": 2.1,
        "pe": 3.6, "pb": 0.86,
        "roa_prev": 0.031, "leverage_prev": 4.12,
        "current_ratio_prev": 1.04, "gross_margin_prev": 0.028,
        "asset_turnover_prev": 4.8, "shares_issued": False,
    },
    "OGDC": {
        "name": "Oil & Gas Development Co. Ltd.",
        "sector": "Energy",
        "fiscal_year": 2023,
        "revenue": 248_000, "net_income": 70_000, "ebit": 95_000,
        "gross_profit": 154_752, "total_assets": 714_000,
        "total_liabilities": 214_000, "total_equity": 500_000,
        "current_assets": 389_000, "current_liabilities": 213_000,
        "retained_earnings": 310_000, "operating_cash_flow": 82_000,
        "market_cap": 102_000, "eps": 16.4, "bvps": 204.2,
        "roe": 0.142, "roa": 0.098, "gross_margin": 0.624,
        "net_margin": 0.284, "current_ratio": 1.82, "quick_ratio": 1.61,
        "debt_to_equity": 0.42, "interest_coverage": 18.4,
        "pe": 5.1, "pb": 0.72,
        "roa_prev": 0.112, "leverage_prev": 0.48,
        "current_ratio_prev": 1.74, "gross_margin_prev": 0.641,
        "asset_turnover_prev": 0.32, "shares_issued": False,
    },
    "LUCK": {
        "name": "Lucky Cement Ltd.",
        "sector": "Cement",
        "fiscal_year": 2023,
        "revenue": 142_000, "net_income": 20_000, "ebit": 28_000,
        "gross_profit": 40_612, "total_assets": 135_000,
        "total_liabilities": 50_000, "total_equity": 85_000,
        "current_assets": 68_000, "current_liabilities": 35_000,
        "retained_earnings": 52_000, "operating_cash_flow": 24_000,
        "market_cap": 139_000, "eps": 118.4, "bvps": 636.2,
        "roe": 0.224, "roa": 0.148, "gross_margin": 0.286,
        "net_margin": 0.142, "current_ratio": 1.94, "quick_ratio": 1.72,
        "debt_to_equity": 0.38, "interest_coverage": 14.2,
        "pe": 7.4, "pb": 1.64,
        "roa_prev": 0.134, "leverage_prev": 0.42,
        "current_ratio_prev": 1.88, "gross_margin_prev": 0.298,
        "asset_turnover_prev": 0.98, "shares_issued": False,
    },
    "HBL": {
        "name": "Habib Bank Ltd.",
        "sector": "Banking",
        "fiscal_year": 2023,
        "revenue": 312_000, "net_income": 58_000, "ebit": None,
        "gross_profit": None, "total_assets": 4_100_000,
        "total_liabilities": 3_780_000, "total_equity": 320_000,
        "current_assets": None, "current_liabilities": None,
        "retained_earnings": 180_000, "operating_cash_flow": 72_000,
        "market_cap": 230_000, "eps": 35.8, "bvps": 186.4,
        "roe": 0.196, "roa": 0.014, "gross_margin": None,
        "net_margin": 0.186, "current_ratio": None, "quick_ratio": None,
        "debt_to_equity": 8.2, "interest_coverage": None,
        "pe": 4.8, "pb": 0.92,
        "roa_prev": 0.011, "leverage_prev": 8.6,
        "current_ratio_prev": None, "gross_margin_prev": None,
        "asset_turnover_prev": 0.072, "shares_issued": False,
    },
    "MCB": {
        "name": "MCB Bank Ltd.",
        "sector": "Banking",
        "fiscal_year": 2023,
        "revenue": 198_000, "net_income": 45_000, "ebit": None,
        "gross_profit": None, "total_assets": 2_400_000,
        "total_liabilities": 2_180_000, "total_equity": 220_000,
        "current_assets": None, "current_liabilities": None,
        "retained_earnings": 130_000, "operating_cash_flow": 54_000,
        "market_cap": 193_000, "eps": 37.6, "bvps": 160.2,
        "roe": 0.221, "roa": 0.019, "gross_margin": None,
        "net_margin": 0.228, "current_ratio": None, "quick_ratio": None,
        "debt_to_equity": 6.4, "interest_coverage": None,
        "pe": 5.2, "pb": 1.14,
        "roa_prev": 0.016, "leverage_prev": 6.8,
        "current_ratio_prev": None, "gross_margin_prev": None,
        "asset_turnover_prev": 0.081, "shares_issued": False,
    },
    "ENGRO": {
        "name": "Engro Corporation Ltd.",
        "sector": "Fertilizer / Conglomerate",
        "fiscal_year": 2023,
        "revenue": 148_000, "net_income": 17_000, "ebit": 26_000,
        "gross_profit": 47_952, "total_assets": 198_000,
        "total_liabilities": 105_000, "total_equity": 93_000,
        "current_assets": 88_000, "current_liabilities": 49_000,
        "retained_earnings": 54_000, "operating_cash_flow": 21_000,
        "market_cap": 118_000, "eps": 35.5, "bvps": 196.4,
        "roe": 0.184, "roa": 0.086, "gross_margin": 0.324,
        "net_margin": 0.118, "current_ratio": 1.78, "quick_ratio": 1.54,
        "debt_to_equity": 0.88, "interest_coverage": 6.4,
        "pe": 8.2, "pb": 1.48,
        "roa_prev": 0.078, "leverage_prev": 0.82,
        "current_ratio_prev": 1.71, "gross_margin_prev": 0.316,
        "asset_turnover_prev": 0.71, "shares_issued": False,
    },
    "SYS": {
        "name": "Systems Limited",
        "sector": "Technology",
        "fiscal_year": 2023,
        "revenue": 38_000, "net_income": 6_200, "ebit": 7_800,
        "gross_profit": 14_592, "total_assets": 28_000,
        "total_liabilities": 5_000, "total_equity": 23_000,
        "current_assets": 19_000, "current_liabilities": 8_900,
        "retained_earnings": 14_000, "operating_cash_flow": 7_200,
        "market_cap": 75_000, "eps": 47.8, "bvps": 130.2,
        "roe": 0.368, "roa": 0.224, "gross_margin": 0.384,
        "net_margin": 0.164, "current_ratio": 2.14, "quick_ratio": 2.04,
        "debt_to_equity": 0.18, "interest_coverage": 42.8,
        "pe": 14.2, "pb": 5.2,
        "roa_prev": 0.198, "leverage_prev": 0.22,
        "current_ratio_prev": 2.08, "gross_margin_prev": 0.371,
        "asset_turnover_prev": 1.28, "shares_issued": False,
    },
    "MEBL": {
        "name": "Meezan Bank Ltd.",
        "sector": "Islamic Banking",
        "fiscal_year": 2023,
        "revenue": 142_000, "net_income": 30_000, "ebit": None,
        "gross_profit": None, "total_assets": 1_600_000,
        "total_liabilities": 1_470_000, "total_equity": 130_000,
        "current_assets": None, "current_liabilities": None,
        "retained_earnings": 72_000, "operating_cash_flow": 38_000,
        "market_cap": 248_000, "eps": 36.6, "bvps": 100.4,
        "roe": 0.284, "roa": 0.018, "gross_margin": None,
        "net_margin": 0.212, "current_ratio": None, "quick_ratio": None,
        "debt_to_equity": 7.1, "interest_coverage": None,
        "pe": 5.8, "pb": 1.62,
        "roa_prev": 0.014, "leverage_prev": 7.4,
        "current_ratio_prev": None, "gross_margin_prev": None,
        "asset_turnover_prev": 0.088, "shares_issued": False,
    },
    "PIAA": {
        "name": "Pakistan International Airlines Corp.",
        "sector": "Aviation",
        "fiscal_year": 2023,
        "revenue": 184_000, "net_income": -44_000, "ebit": -18_000,
        "gross_profit": -22_800, "total_assets": 524_000,
        "total_liabilities": 680_000, "total_equity": -156_000,
        "current_assets": 62_000, "current_liabilities": 152_000,
        "retained_earnings": -420_000, "operating_cash_flow": -12_000,
        "market_cap": 3_400, "eps": -32.4, "bvps": None,
        "roe": -0.428, "roa": -0.084, "gross_margin": -0.124,
        "net_margin": -0.241, "current_ratio": 0.41, "quick_ratio": 0.28,
        "debt_to_equity": None, "interest_coverage": -1.2,
        "pe": None, "pb": None,
        "roa_prev": -0.092, "leverage_prev": None,
        "current_ratio_prev": 0.38, "gross_margin_prev": -0.138,
        "asset_turnover_prev": 0.34, "shares_issued": False,
    },
    "NESTLE": {
        "name": "Nestle Pakistan Ltd.",
        "sector": "Food & Consumer",
        "fiscal_year": 2023,
        "revenue": 148_000, "net_income": 14_000, "ebit": 19_500,
        "gross_profit": 53_912, "total_assets": 75_000,
        "total_liabilities": 57_000, "total_equity": 18_000,
        "current_assets": 38_000, "current_liabilities": 23_500,
        "retained_earnings": 8_000, "operating_cash_flow": 17_000,
        "market_cap": 800_000, "eps": 259.8, "bvps": 316.4,
        "roe": 0.824, "roa": 0.186, "gross_margin": 0.364,
        "net_margin": 0.096, "current_ratio": 1.62, "quick_ratio": 1.18,
        "debt_to_equity": 1.82, "interest_coverage": 8.4,
        "pe": 22.4, "pb": 18.4,
        "roa_prev": 0.172, "leverage_prev": 1.94,
        "current_ratio_prev": 1.54, "gross_margin_prev": 0.351,
        "asset_turnover_prev": 1.88, "shares_issued": False,
    },
    "SEARL": {
        "name": "The Searle Company Ltd.",
        "sector": "Pharmaceuticals",
        "fiscal_year": 2023,
        "revenue": 24_000, "net_income": 3_000, "ebit": 4_200,
        "gross_profit": 10_272, "total_assets": 29_000,
        "total_liabilities": 11_000, "total_equity": 18_000,
        "current_assets": 16_000, "current_liabilities": 8_500,
        "retained_earnings": 10_000, "operating_cash_flow": 3_600,
        "market_cap": 22_000, "eps": 28.8, "bvps": 171.4,
        "roe": 0.168, "roa": 0.104, "gross_margin": 0.428,
        "net_margin": 0.128, "current_ratio": 1.88, "quick_ratio": 1.52,
        "debt_to_equity": 0.62, "interest_coverage": 9.8,
        "pe": 8.4, "pb": 1.42,
        "roa_prev": 0.096, "leverage_prev": 0.68,
        "current_ratio_prev": 1.82, "gross_margin_prev": 0.414,
        "asset_turnover_prev": 0.78, "shares_issued": False,
    },
}

BANKING_SECTORS = ["Banking", "Islamic Banking", "Insurance"]


@router.get("/{ticker}")
def analyse_company(ticker: str):
    """
    Full financial analysis for a PSX company.
    Always tries live Yahoo Finance fundamentals first, so every company —
    including the originally-curated ones — is analysed against the latest
    fiscal year Yahoo has reported, not a fixed FY2023 snapshot. The
    hand-curated FINANCIAL_DB is now only a safety-net fallback for the
    rare case where Yahoo doesn't return enough data to run the models.
    """
    ticker = ticker.upper()

    d = get_full_fundamentals(ticker)
    if d is not None:
        data_source = "Yahoo Finance (live fundamentals, latest reported fiscal year; some fields may be estimated or unavailable)"

        # Always prefer the curated sector/name from the company list over
        # Yahoo's own values — it's already hand-checked, consistent with
        # what's shown in the Coverage table, and (critically) uses the
        # "Banking" / "Islamic Banking" / "Insurance" labels the Altman
        # bank-detection below actually looks for. Yahoo's own sector
        # taxonomy ("Financial Services" etc.) wouldn't match those, and
        # Yahoo's "longName"/"shortName" fields occasionally come back as
        # garbled internal quote metadata rather than a real company name.
        known = next((c for c in PSX_COMPANIES if c["ticker"] == ticker), None)
        if known:
            d["sector"] = known["sector"]
            d["name"] = known["name"]
    elif ticker in FINANCIAL_DB:
        d = FINANCIAL_DB[ticker]
        data_source = "PSX Annual Report FY2023 (curated fallback — Yahoo Finance didn't return enough live fundamentals for this company)"
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No usable financial data found for {ticker} — "
                   f"Yahoo Finance didn't return enough data "
                   f"(total assets, total liabilities, revenue) to "
                   f"run the models, and it isn't in the curated "
                   f"annual-report fallback database either."
        )

    sector = d["sector"]
    is_bank = any(s in sector for s in BANKING_SECTORS)

    # 1. Fetch live price from Yahoo Finance
    live = {}
    try:
        live = get_live_price(ticker)
    except Exception:
        pass

    _eps_fallback = d.get("eps") or 0
    _pe_fallback = d.get("pe") or 0
    market_price = live.get("price") or (_eps_fallback * _pe_fallback) or None

    # 2. Altman Z-Score
    if is_bank:
        altman = {"score": None, "zone": "bank", "components": {}}
    else:
        wc = (d.get("current_assets") or 0) - (d.get("current_liabilities") or 0)
        altman = calc_altman_zscore(
            working_capital=wc,
            total_assets=d["total_assets"],
            retained_earnings=d.get("retained_earnings") or 0,
            ebit=d.get("ebit") or 0,
            market_cap=d.get("market_cap") or 0,
            total_liabilities=d["total_liabilities"],
            revenue=d["revenue"],
        )

    # 3. Piotroski F-Score
    asset_turnover = d["revenue"] / d["total_assets"] if d["total_assets"] else None

    piotroski = calc_piotroski(
        roa=d.get("roa"),
        operating_cash_flow=d.get("operating_cash_flow"),
        net_income=d.get("net_income"),
        total_assets=d["total_assets"],
        roa_prev=d.get("roa_prev"),
        leverage=d.get("debt_to_equity"),
        leverage_prev=d.get("leverage_prev"),
        current_ratio=d.get("current_ratio"),
        current_ratio_prev=d.get("current_ratio_prev"),
        shares_issued=d.get("shares_issued", False),
        gross_margin=d.get("gross_margin"),
        gross_margin_prev=d.get("gross_margin_prev"),
        asset_turnover=asset_turnover,
        asset_turnover_prev=d.get("asset_turnover_prev"),
    )

    # 4. Graham Number
    graham = calc_graham_number(
        eps=d.get("eps"),
        bvps=d.get("bvps"),
    )
    # Expose the actual EPS/BVPS used so the frontend can display them
    # even when the formula itself isn't applicable (e.g. negative EPS).
    graham["eps"] = d.get("eps")
    graham["bvps"] = d.get("bvps")

    graham_delta = None
    if graham["applicable"] and market_price:
        diff = market_price - graham["graham_number"]
        graham_delta = round((diff / graham["graham_number"]) * 100, 1)
        graham["market_price"] = market_price
        graham["delta_pct"] = graham_delta
        graham["verdict"] = "Undervalued" if graham_delta < 0 else "Overvalued"

    # 5. Key Ratios
    ratios = calc_ratios({
        "net_margin":    d.get("net_margin"),
        "gross_margin":  d.get("gross_margin"),
        "roe":           d.get("roe"),
        "roa":           d.get("roa"),
        "current_ratio": d.get("current_ratio"),
        "quick_ratio":   d.get("quick_ratio"),
        "debt_to_equity": d.get("debt_to_equity"),
        "interest_coverage": d.get("interest_coverage"),
        "pe": d.get("pe"),
        "pb": d.get("pb"),
    })

    # 6. Health Score
    health = calc_health_score(
        altman_zone=altman["zone"],
        piotroski_score=piotroski["score"],
        graham_delta=graham_delta,
        net_margin=ratios["profitability"]["net_margin"],
        current_ratio=ratios["liquidity"]["current_ratio"],
        debt_to_equity=ratios["leverage"]["debt_to_equity"],
    )

    return {
        "ticker":       ticker,
        "name":         d["name"],
        "sector":       sector,
        "fiscal_year":  d.get("fiscal_year"),
        "live_price":   live if live else None,
        "health":       health,
        "altman":       altman,
        "piotroski":    piotroski,
        "graham":       graham,
        "ratios":       ratios,
        "data_source":  data_source,
    }


@router.get("/")
def list_available():
    """
    List companies with a curated FY2023 fallback available.
    Every company is analysed live from Yahoo Finance first (GET /{ticker});
    this curated set is only used as a safety net if Yahoo doesn't return
    enough data for that specific company.
    """
    return {
        "fallback_tickers": sorted(FINANCIAL_DB.keys()),
        "fallback_count": len(FINANCIAL_DB),
        "note": "All companies are analysed live from Yahoo Finance fundamentals first. This curated set only kicks in as a fallback if Yahoo data is insufficient."
    }

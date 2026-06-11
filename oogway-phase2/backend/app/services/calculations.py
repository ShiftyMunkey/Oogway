import math
from typing import Optional


# ─── ALTMAN Z-SCORE ──────────────────────────────────────────────────────────
# For non-financial companies. Banking companies get a separate note.
# Z > 2.99: Safe | 1.81 < Z < 2.99: Grey | Z < 1.81: Distress

def calc_altman_zscore(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    market_cap: float,
    total_liabilities: float,
    revenue: float,
) -> dict:
    if not total_assets or total_assets == 0:
        return {"score": None, "zone": "unknown", "components": {}}

    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets if retained_earnings else 0
    x3 = ebit / total_assets if ebit else 0
    x4 = market_cap / total_liabilities if total_liabilities else 0
    x5 = revenue / total_assets if revenue else 0

    score = round((1.2*x1) + (1.4*x2) + (3.3*x3) + (0.6*x4) + (1.0*x5), 2)

    if score > 2.99:
        zone = "safe"
    elif score > 1.81:
        zone = "grey"
    else:
        zone = "distress"

    return {
        "score": score,
        "zone":  zone,
        "components": {
            "x1_working_capital_ratio":  round(x1, 4),
            "x2_retained_earnings_ratio": round(x2, 4),
            "x3_ebit_ratio":             round(x3, 4),
            "x4_market_cap_ratio":       round(x4, 4),
            "x5_asset_turnover":         round(x5, 4),
        }
    }


# ─── PIOTROSKI F-SCORE ───────────────────────────────────────────────────────
# 9 binary criteria. 7-9: Strong | 4-6: Neutral | 0-3: Weak

def calc_piotroski(
    roa: float,
    operating_cash_flow: float,
    net_income: float,
    total_assets: float,
    roa_prev: Optional[float],
    leverage: float,
    leverage_prev: Optional[float],
    current_ratio: float,
    current_ratio_prev: Optional[float],
    shares_issued: bool,
    gross_margin: float,
    gross_margin_prev: Optional[float],
    asset_turnover: float,
    asset_turnover_prev: Optional[float],
) -> dict:
    criteria = {}

    # Profitability
    criteria["positive_roa"]          = 1 if roa and roa > 0 else 0
    criteria["positive_cfo"]          = 1 if operating_cash_flow and operating_cash_flow > 0 else 0
    criteria["increasing_roa"]        = 1 if (roa and roa_prev and roa > roa_prev) else 0
    criteria["cfo_greater_than_ni"]   = 1 if (operating_cash_flow and net_income and operating_cash_flow > net_income) else 0

    # Leverage / Liquidity
    criteria["decreasing_leverage"]   = 1 if (leverage and leverage_prev and leverage < leverage_prev) else 0
    criteria["improving_current_ratio"]= 1 if (current_ratio and current_ratio_prev and current_ratio > current_ratio_prev) else 0
    criteria["no_dilution"]           = 1 if not shares_issued else 0

    # Operating Efficiency
    criteria["improving_gross_margin"]= 1 if (gross_margin and gross_margin_prev and gross_margin > gross_margin_prev) else 0
    criteria["improving_asset_turnover"]= 1 if (asset_turnover and asset_turnover_prev and asset_turnover > asset_turnover_prev) else 0

    score = sum(criteria.values())

    if score >= 7:
        signal = "Strong Buy"
    elif score >= 4:
        signal = "Neutral"
    else:
        signal = "Sell Signal"

    return {
        "score":    score,
        "signal":   signal,
        "criteria": criteria,
    }


# ─── GRAHAM NUMBER ───────────────────────────────────────────────────────────
# Intrinsic value estimate: sqrt(22.5 * EPS * BVPS)

def calc_graham_number(eps: float, bvps: float) -> dict:
    if not eps or not bvps or eps <= 0 or bvps <= 0:
        return {
            "graham_number":  None,
            "applicable":     False,
            "reason":         "Negative or missing EPS / book value"
        }

    graham = round(math.sqrt(22.5 * eps * bvps), 2)
    return {
        "graham_number": graham,
        "applicable":    True,
        "formula":       f"sqrt(22.5 x {eps} x {bvps})",
    }


# ─── KEY RATIOS ──────────────────────────────────────────────────────────────

def calc_ratios(info: dict) -> dict:
    def safe(val, multiplier=1):
        if val is None:
            return None
        return round(float(val) * multiplier, 2)

    return {
        "profitability": {
            "net_margin":    safe(info.get("net_margin"), 100),
            "gross_margin":  safe(info.get("gross_margin"), 100),
            "roe":           safe(info.get("roe"), 100),
            "roa":           safe(info.get("roa"), 100),
        },
        "liquidity": {
            "current_ratio": safe(info.get("current_ratio")),
            "quick_ratio":   safe(info.get("quick_ratio")),
        },
        "leverage": {
            "debt_to_equity":      safe(info.get("debt_to_equity"), 0.01),
            "interest_coverage":   safe(info.get("interest_coverage")),
        },
        "valuation": {
            "pe":  safe(info.get("pe")),
            "pb":  safe(info.get("pb")),
        }
    }


# ─── HEALTH SCORE ────────────────────────────────────────────────────────────
# Composite 0-100 score derived from all four models

def calc_health_score(
    altman_zone: str,
    piotroski_score: int,
    graham_delta: Optional[float],
    net_margin: Optional[float],
    current_ratio: Optional[float],
    debt_to_equity: Optional[float],
) -> dict:
    score = 0

    # Altman contribution (30 points)
    altman_pts = {"safe": 30, "grey": 15, "distress": 0, "bank": 20, "unknown": 10}
    score += altman_pts.get(altman_zone, 10)

    # Piotroski contribution (25 points)
    score += round((piotroski_score / 9) * 25)

    # Graham contribution (15 points)
    if graham_delta is not None:
        if graham_delta < 0:
            score += 15
        elif graham_delta < 20:
            score += 8
        else:
            score += 0

    # Profitability (15 points)
    if net_margin is not None:
        if net_margin > 15:
            score += 15
        elif net_margin > 5:
            score += 8
        elif net_margin > 0:
            score += 3

    # Liquidity (8 points)
    if current_ratio is not None:
        if current_ratio > 1.5:
            score += 8
        elif current_ratio > 1:
            score += 4

    # Leverage (7 points)
    if debt_to_equity is not None:
        if debt_to_equity < 1:
            score += 7
        elif debt_to_equity < 2:
            score += 4
        elif debt_to_equity < 4:
            score += 1

    score = min(100, max(0, score))

    if score >= 75:
        verdict = "Healthy"
    elif score >= 60:
        verdict = "Moderate"
    elif score >= 40:
        verdict = "Caution"
    else:
        verdict = "Distress"

    return {"score": score, "verdict": verdict}

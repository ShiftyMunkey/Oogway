from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import Company

router = APIRouter()

# Full PSX company list grouped by sector
PSX_COMPANIES = [
    # Energy & Oil
    {"ticker": "PSO",    "name": "Pakistan State Oil",          "sector": "Energy / OMC"},
    {"ticker": "OGDC",   "name": "Oil & Gas Development Co.",   "sector": "Energy"},
    {"ticker": "PPL",    "name": "Pakistan Petroleum Limited",  "sector": "Energy"},
    {"ticker": "POL",    "name": "Pakistan Oilfields Limited",  "sector": "Energy"},
    {"ticker": "MARI",   "name": "Mari Petroleum Company",      "sector": "Energy"},
    {"ticker": "SHEL",   "name": "Shell Pakistan",              "sector": "Energy"},
    {"ticker": "ATRL",   "name": "Attock Refinery",             "sector": "Energy"},
    {"ticker": "NRL",    "name": "National Refinery",           "sector": "Energy"},
    # Banking
    {"ticker": "HBL",    "name": "Habib Bank Limited",          "sector": "Banking"},
    {"ticker": "MCB",    "name": "MCB Bank",                    "sector": "Banking"},
    {"ticker": "UBL",    "name": "United Bank Limited",         "sector": "Banking"},
    {"ticker": "ABL",    "name": "Allied Bank Limited",         "sector": "Banking"},
    {"ticker": "NBP",    "name": "National Bank of Pakistan",   "sector": "Banking"},
    {"ticker": "BAFL",   "name": "Bank Alfalah",                "sector": "Banking"},
    {"ticker": "MEBL",   "name": "Meezan Bank",                 "sector": "Banking"},
    {"ticker": "AKBL",   "name": "Askari Bank",                 "sector": "Banking"},
    # Cement
    {"ticker": "LUCK",   "name": "Lucky Cement",                "sector": "Cement"},
    {"ticker": "DGKC",   "name": "D.G. Khan Cement",            "sector": "Cement"},
    {"ticker": "MLCF",   "name": "Maple Leaf Cement",           "sector": "Cement"},
    {"ticker": "FCCL",   "name": "Fauji Cement",                "sector": "Cement"},
    {"ticker": "KOHC",   "name": "Kohat Cement",                "sector": "Cement"},
    {"ticker": "ACPL",   "name": "Attock Cement",               "sector": "Cement"},
    # Fertilizer
    {"ticker": "ENGRO",  "name": "Engro Corporation",           "sector": "Fertilizer"},
    {"ticker": "FFC",    "name": "Fauji Fertilizer Company",    "sector": "Fertilizer"},
    {"ticker": "FATIMA", "name": "Fatima Fertilizer",           "sector": "Fertilizer"},
    {"ticker": "EFERT",  "name": "Engro Fertilizers",           "sector": "Fertilizer"},
    # Pharma
    {"ticker": "SEARL",  "name": "The Searle Company",          "sector": "Pharmaceuticals"},
    {"ticker": "GLAXO",  "name": "GlaxoSmithKline Pakistan",    "sector": "Pharmaceuticals"},
    {"ticker": "ABOT",   "name": "Abbott Laboratories Pakistan","sector": "Pharmaceuticals"},
    {"ticker": "HINOON", "name": "Highnoon Laboratories",       "sector": "Pharmaceuticals"},
    # Food
    {"ticker": "NESTLE", "name": "Nestle Pakistan",             "sector": "Food & Consumer"},
    {"ticker": "NATF",   "name": "National Foods",              "sector": "Food & Consumer"},
    {"ticker": "UNITY",  "name": "Unity Foods",                 "sector": "Food & Consumer"},
    # Technology
    {"ticker": "SYS",    "name": "Systems Limited",             "sector": "Technology"},
    {"ticker": "TRG",    "name": "TRG Pakistan",                "sector": "Technology"},
    {"ticker": "NETSOL", "name": "NetSol Technologies",         "sector": "Technology"},
    {"ticker": "AVN",    "name": "Avanceon Limited",            "sector": "Technology"},
    # Power
    {"ticker": "HUBC",   "name": "Hub Power Company",           "sector": "Power"},
    {"ticker": "KAPCO",  "name": "Kot Addu Power",              "sector": "Power"},
    {"ticker": "NCPL",   "name": "Nishat Chunian Power",        "sector": "Power"},
    # Automobile
    {"ticker": "INDU",   "name": "Indus Motor Company",         "sector": "Automobile"},
    {"ticker": "PSMC",   "name": "Pak Suzuki Motor",            "sector": "Automobile"},
    {"ticker": "HCAR",   "name": "Honda Atlas Cars",            "sector": "Automobile"},
    {"ticker": "MTL",    "name": "Millat Tractors",             "sector": "Automobile"},
    # Textile
    {"ticker": "NML",    "name": "Nishat Mills",                "sector": "Textile"},
    {"ticker": "NCL",    "name": "Nishat Chunian",              "sector": "Textile"},
    {"ticker": "GATM",   "name": "Gul Ahmed Textile",           "sector": "Textile"},
    # Insurance
    {"ticker": "EFUG",   "name": "EFU General Insurance",       "sector": "Insurance"},
    {"ticker": "JLICL",  "name": "Jubilee Life Insurance",      "sector": "Insurance"},
    # Aviation
    {"ticker": "PIAA",   "name": "Pakistan Intl Airlines",      "sector": "Aviation"},
    {"ticker": "PNSC",   "name": "Pakistan National Shipping",  "sector": "Transport"},
]


@router.get("/")
def list_companies(sector: str = None):
    """Return all companies, optionally filtered by sector."""
    if sector:
        return [c for c in PSX_COMPANIES if c["sector"].lower() == sector.lower()]
    return PSX_COMPANIES


@router.get("/sectors")
def list_sectors():
    """Return all unique sectors."""
    sectors = sorted(set(c["sector"] for c in PSX_COMPANIES))
    return sectors


@router.get("/search")
def search_companies(q: str):
    """Search companies by ticker or name."""
    q_lower = q.lower()
    return [
        c for c in PSX_COMPANIES
        if q_lower in c["ticker"].lower() or q_lower in c["name"].lower()
    ]


@router.get("/{ticker}")
def get_company(ticker: str):
    """Get a single company by ticker."""
    ticker = ticker.upper()
    match = next((c for c in PSX_COMPANIES if c["ticker"] == ticker), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")
    return match

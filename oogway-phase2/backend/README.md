# Oogway Backend

FastAPI + MySQL backend for the Oogway PSX financial intelligence platform.

## Setup

**1. Create a virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up MySQL**
Create a database called `oogway` in your local MySQL instance:
```sql
CREATE DATABASE oogway;
```

**4. Configure environment**
```bash
cp .env.example .env
# Edit .env with your MySQL password
```

**5. Run the server**
```bash
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

API docs at: http://localhost:8000/docs

---

## API Endpoints

### Companies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/companies/ | List all PSX companies |
| GET | /api/companies/sectors | List all sectors |
| GET | /api/companies/search?q=pso | Search by name or ticker |
| GET | /api/companies/{ticker} | Get single company |

### Prices (Yahoo Finance)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/prices/{ticker}/current | Latest price |
| GET | /api/prices/{ticker}/history?period=1y | OHLCV candlestick data |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/analysis/{ticker} | Full analysis: Altman + Piotroski + Graham + Ratios + Health Score |

---

## Swapping to PSX API

When the PSX API becomes available, only `app/services/yahoo_service.py` needs to change.
Everything else (calculations, routers, models) stays exactly the same.

Replace the Yahoo Finance calls in that file with your PSX API calls
and the rest of the system will work without any changes.

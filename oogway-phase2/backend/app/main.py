from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import companies, prices, analysis
from app.database.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Oogway API",
    description="PSX Financial Intelligence Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://shiftymunkey.github.io", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(prices.router,    prefix="/api/prices",    tags=["Prices"])
app.include_router(analysis.router,  prefix="/api/analysis",  tags=["Analysis"])

@app.get("/")
def root():
    return {"status": "Oogway API is running", "version": "2.0.0"}

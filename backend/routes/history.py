from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import BenchmarkRun
from pydantic import BaseModel

router = APIRouter()

# ✅ Schema for incoming data
class RunCreate(BaseModel):
    model_name: str
    quantization: str
    tokens_per_sec: float
    latency_ms: float
    ram_usage_mb: float


# ✅ POST → Save benchmark run
@router.post("/history")
async def create_run(run: RunCreate, db: Session = Depends(get_db)):
    db_run = BenchmarkRun(
        model_name=run.model_name,
        quantization=run.quantization,
        tokens_per_sec=run.tokens_per_sec,
        latency_ms=run.latency_ms,
        ram_usage_mb=run.ram_usage_mb
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run


# ✅ GET → Fetch history (already exists but keep it)
@router.get("/history")
async def get_history(db: Session = Depends(get_db)):
    runs = db.query(BenchmarkRun)\
        .order_by(BenchmarkRun.created_at.desc())\
        .limit(50)\
        .all()
    return runs
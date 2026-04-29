from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from schemas import RecommendRequest, RecommendResponse
from services.recommender import recommend_model
from models import BenchmarkRun

router = APIRouter()

@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendation(request: RecommendRequest, db: Session = Depends(get_db)):
    runs = db.query(
        BenchmarkRun.model_name,
        BenchmarkRun.quantization,
        func.avg(BenchmarkRun.quality_score).label('avg_quality'),
        func.avg(BenchmarkRun.tokens_per_sec).label('avg_tps'),
        func.avg(BenchmarkRun.ram_usage_mb).label('avg_ram_mb')
    ).group_by(BenchmarkRun.model_name, BenchmarkRun.quantization).all()
    
    if not runs:
        # Mock data if DB is empty to demonstrate functionality
        models_data = [
            {"model_name": "llama3", "quantization": "q4", "avg_quality": 8.0, "avg_tps": 40.0, "avg_ram_mb": 4500},
            {"model_name": "llama3", "quantization": "q8", "avg_quality": 8.5, "avg_tps": 20.0, "avg_ram_mb": 8500},
            {"model_name": "mistral", "quantization": "q4", "avg_quality": 7.5, "avg_tps": 45.0, "avg_ram_mb": 4000},
        ]
    else:
        models_data = []
        for r in runs:
            models_data.append({
                "model_name": r.model_name,
                "quantization": r.quantization,
                "avg_quality": r.avg_quality or 5.0,
                "avg_tps": r.avg_tps or 0.0,
                "avg_ram_mb": r.avg_ram_mb or 0.0
            })
            
    rec = recommend_model(request.ram_available_gb, request.preference, models_data)
    return RecommendResponse(**rec)

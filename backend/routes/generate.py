from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import GenerateRequest, GenerateResponse
from services.ollama_client import generate_parallel
from services.metrics import get_process_ram_mb

router = APIRouter()

@router.post("/generate", response_model=list[GenerateResponse])
async def generate_models(request: GenerateRequest, db: Session = Depends(get_db)):
    prompts_models = [(request.prompt, model, request.quantization) for model in request.models]
    
    ram_before = get_process_ram_mb()
    results = await generate_parallel(prompts_models, db)
    ram_after = get_process_ram_mb()
    
    # Ram diff approximation per request
    ram_diff = max(0, ram_after - ram_before)
    
    final_responses = []
    for res in results:
        final_responses.append(GenerateResponse(
            model_name=res["model_name"],
            response=res["response"],
            latency_ms=res["latency_ms"],
            tokens_generated=res["tokens_generated"],
            tokens_per_sec=res["tokens_per_sec"],
            ram_usage_mb=ram_diff / len(request.models) if len(request.models) > 0 else 0,
            cached=res["cached"]
        ))
        
    return final_responses

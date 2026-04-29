from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import BenchmarkRequest
from services.ollama_client import generate_parallel
import json
import os

router = APIRouter()

@router.post("/benchmark")
async def run_benchmark(request: BenchmarkRequest, db: Session = Depends(get_db)):
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "prompt_dataset.json")
    try:
        with open(dataset_path, "r") as f:
            dataset = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not load prompt dataset")
        
    if request.category not in dataset:
        raise HTTPException(status_code=400, detail=f"Category {request.category} not found in dataset")
        
    prompts = dataset[request.category]
    all_results = []
    
    for prompt in prompts:
        prompts_models = [(prompt, model, "default") for model in request.models]
        results = await generate_parallel(prompts_models, db)
        
        prompt_results = []
        for res in results:
            prompt_results.append({
                "prompt": prompt,
                "model_name": res["model_name"],
                "response": res["response"],
                "latency_ms": res["latency_ms"],
                "tokens_per_sec": res["tokens_per_sec"]
            })
        all_results.append({"prompt": prompt, "results": prompt_results})
        
    return {"category": request.category, "runs": all_results}

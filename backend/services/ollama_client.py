import ollama
from ollama import AsyncClient
import time
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.orm import Session
from models import CacheEntry
import asyncio
import logging

logger = logging.getLogger(__name__)
client = AsyncClient()

def get_cache_hash(prompt: str, model: str, quantization: str) -> str:
    content = f"{prompt}_{model}_{quantization}"
    return hashlib.sha256(content.encode()).hexdigest()

def check_cache(db: Session, prompt_hash: str):
    return db.query(CacheEntry).filter(CacheEntry.prompt_hash == prompt_hash).first()

def save_to_cache(db: Session, prompt_hash: str, response: str, latency: float, tokens: int, tps: float):
    entry = CacheEntry(
        prompt_hash=prompt_hash,
        response_text=response,
        latency_ms=latency,
        tokens_generated=tokens,
        tokens_per_sec=tps
    )
    db.add(entry)
    db.commit()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_response(prompt: str, model: str, quantization: str = "default", db: Session = None):
    full_model_name = model
    
    phash = get_cache_hash(prompt, full_model_name, quantization)
    if db:
        cached = check_cache(db, phash)
        if cached:
            logger.info(f"Cache hit for {full_model_name}")
            return {
                "model_name": full_model_name,
                "response": cached.response_text,
                "latency_ms": cached.latency_ms,
                "tokens_generated": cached.tokens_generated,
                "tokens_per_sec": cached.tokens_per_sec,
                "cached": True,
                "error": None
            }

    start_time = time.time()
    try:
        # We explicitly set stream=False for benchmark simplicity. 
        # Token extraction relies on the final response object.
        response = await client.generate(model=full_model_name, prompt=prompt, stream=False)
    except Exception as e:
        logger.error(f"Error generating with {full_model_name}: {e}")
        return {
            "model_name": full_model_name,
            "response": "",
            "latency_ms": 0,
            "tokens_generated": 0,
            "tokens_per_sec": 0,
            "cached": False,
            "error": str(e)
        }

    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000

    tokens = response.get("eval_count", 0)
    duration_ns = response.get("eval_duration", 0)
    
    if duration_ns > 0:
        tps = tokens / (duration_ns / 1e9)
    else:
        duration_sec = latency_ms / 1000
        tps = tokens / duration_sec if duration_sec > 0 else 0

    result = {
        "model_name": full_model_name,
        "response": response.get("response", ""),
        "latency_ms": latency_ms,
        "tokens_generated": tokens,
        "tokens_per_sec": tps,
        "cached": False,
        "error": None
    }

    if db and not result["error"]:
        save_to_cache(db, phash, result["response"], latency_ms, tokens, tps)

    return result

async def generate_parallel(prompts_models: list, db: Session = None):
    """
    Executes multiple generations in parallel.
    prompts_models is a list of tuples: (prompt, model, quantization)
    """
    tasks = [
        generate_response(prompt, model, quant, db)
        for prompt, model, quant in prompts_models
    ]
    # return_exceptions=True prevents one failure from failing the entire batch
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results in case some raised unhandled exceptions
    final_results = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            prompt, model, quant = prompts_models[i]
            final_results.append({
                "model_name": model,
                "response": "",
                "latency_ms": 0,
                "tokens_generated": 0,
                "tokens_per_sec": 0,
                "cached": False,
                "error": str(res)
            })
        else:
            final_results.append(res)
            
    return final_results

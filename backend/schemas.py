from pydantic import BaseModel
from typing import List, Optional

class GenerateRequest(BaseModel):
    prompt: str
    models: List[str] # e.g. ["llama3", "mistral"]
    quantization: str = "default" # "default", "q4", "q8"

class GenerateResponse(BaseModel):
    model_name: str
    response: str
    latency_ms: float
    tokens_generated: int
    tokens_per_sec: float
    ram_usage_mb: float
    cached: bool = False

class EvaluateRequest(BaseModel):
    prompt: str
    response: str
    model_name: str

class EvaluateResponse(BaseModel):
    accuracy: int
    clarity: int
    relevance: int
    heuristic_score: float
    final_quality_score: float

class RecommendRequest(BaseModel):
    ram_available_gb: float
    preference: str # "speed", "quality", "balanced"

class RecommendResponse(BaseModel):
    recommended_model: str
    recommended_quantization: str
    explanation: str

class BenchmarkRequest(BaseModel):
    category: str
    models: List[str]

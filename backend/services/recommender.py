from config import WEIGHT_QUALITY, WEIGHT_SPEED, WEIGHT_MEMORY

def calculate_global_score(quality: float, speed: float, memory: float, max_speed: float, max_memory: float) -> float:
    """
    quality: 0-10
    speed: tokens/sec
    memory: RAM used in MB
    
    Higher is better for score.
    """
    # Normalize inputs
    norm_quality = quality / 10.0 if quality > 0 else 0
    
    norm_speed = speed / max_speed if max_speed > 0 else 0
    
    # Memory is better when lower. Inverse normalization
    # If memory is 0, score is 1. If memory == max_memory, score is 0.
    norm_memory = 1.0 - (memory / max_memory) if max_memory > 0 and memory <= max_memory else 0.0
    
    global_score = (WEIGHT_QUALITY * norm_quality) + (WEIGHT_SPEED * norm_speed) + (WEIGHT_MEMORY * norm_memory)
    return round(global_score, 3)

def recommend_model(available_ram_gb: float, preference: str, models_data: list):
    """
    models_data: List of dicts with:
    {
        "model_name": str,
        "quantization": str,
        "avg_quality": float,
        "avg_tps": float,
        "avg_ram_mb": float
    }
    """
    if not models_data:
        return {"recommended_model": "None", "recommended_quantization": "None", "explanation": "No data available."}
        
    available_ram_mb = available_ram_gb * 1024
    
    # Filter out models that exceed available RAM
    viable_models = [m for m in models_data if m["avg_ram_mb"] <= available_ram_mb]
    
    if not viable_models:
        return {
            "recommended_model": "None",
            "recommended_quantization": "None",
            "explanation": f"No models fit within the {available_ram_gb}GB constraint."
        }
        
    max_speed = max(m["avg_tps"] for m in viable_models)
    max_mem = max(m["avg_ram_mb"] for m in viable_models)
    
    best_score = -1
    best_model = None
    
    for m in viable_models:
        # Adjust weights based on preference
        wq = WEIGHT_QUALITY
        ws = WEIGHT_SPEED
        wm = WEIGHT_MEMORY
        
        if preference == "speed":
            ws = 0.6; wq = 0.2; wm = 0.2
        elif preference == "quality":
            wq = 0.6; ws = 0.2; wm = 0.2
            
        norm_q = m["avg_quality"] / 10.0
        norm_s = m["avg_tps"] / max_speed if max_speed > 0 else 0
        norm_m = 1.0 - (m["avg_ram_mb"] / max_mem) if max_mem > 0 else 0
        
        score = (wq * norm_q) + (ws * norm_s) + (wm * norm_m)
        
        if score > best_score:
            best_score = score
            best_model = m
            
    if best_model:
        return {
            "recommended_model": best_model["model_name"],
            "recommended_quantization": best_model["quantization"],
            "explanation": f"Based on your preference for '{preference}' and RAM limit of {available_ram_gb}GB, this model provides the best composite score ({round(best_score, 2)})."
        }
        
    return {"recommended_model": "None", "recommended_quantization": "None", "explanation": "Error calculating recommendation."}

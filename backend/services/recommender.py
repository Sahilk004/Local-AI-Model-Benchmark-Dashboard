from config import WEIGHT_QUALITY, WEIGHT_SPEED, WEIGHT_MEMORY


def normalize_min_max(value, min_v, max_v):
    """Min-max normalization"""
    return (value - min_v) / (max_v - min_v + 1e-8)


def calculate_score(norm_q, norm_s, norm_m, wq, ws, wm):
    """Final weighted score"""
    return (wq * norm_q) + (ws * norm_s) + (wm * norm_m)


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
        return {
            "recommended_model": "None",
            "recommended_quantization": "None",
            "explanation": "No data available.",
            "ranking": []
        }

    # Convert RAM
    available_ram_mb = available_ram_gb * 1024

    # Filter models based on RAM
    viable_models = [
        m for m in models_data if m["avg_ram_mb"] <= available_ram_mb
    ]

    if not viable_models:
        return {
            "recommended_model": "None",
            "recommended_quantization": "None",
            "explanation": f"No models fit within the {available_ram_gb}GB constraint.",
            "ranking": []
        }

    # ---- Get min/max for normalization ----
    min_speed = min(m["avg_tps"] for m in viable_models)
    max_speed = max(m["avg_tps"] for m in viable_models)

    min_mem = min(m["avg_ram_mb"] for m in viable_models)
    max_mem = max(m["avg_ram_mb"] for m in viable_models)

    # ---- Dynamic weights ----
    if preference == "speed":
        wq, ws, wm = 0.2, 0.6, 0.2
    elif preference == "quality":
        wq, ws, wm = 0.6, 0.2, 0.2
    else:  # balanced
        wq, ws, wm = WEIGHT_QUALITY, WEIGHT_SPEED, WEIGHT_MEMORY

    scored_models = []

    for m in viable_models:
        # Normalize values
        norm_q = m["avg_quality"] / 10.0

        norm_s = normalize_min_max(
            m["avg_tps"], min_speed, max_speed
        )

        # Memory: lower is better → invert
        norm_m = normalize_min_max(
            max_mem - m["avg_ram_mb"],
            max_mem - max_mem,
            max_mem - min_mem
        )

        # Calculate score
        score = calculate_score(norm_q, norm_s, norm_m, wq, ws, wm)

        # Store score
        m_copy = m.copy()
        m_copy["score"] = round(score, 4)
        scored_models.append(m_copy)

    # ---- Sort models by score ----
    ranked_models = sorted(
        scored_models,
        key=lambda x: x["score"],
        reverse=True
    )

    best_model = ranked_models[0]

    # ---- Final response ----
    return {
        "recommended_model": best_model["model_name"],
        "recommended_quantization": best_model["quantization"],
        "explanation": (
            f"Based on your preference for '{preference}' and RAM limit of "
            f"{available_ram_gb}GB, this model provides the best composite score "
            f"({best_model['score']})."
        ),
        "ranking": ranked_models  # 🔥 IMPORTANT
    }
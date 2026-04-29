import instructor
from pydantic import BaseModel, Field
import openai
from config import OLLAMA_BASE_URL
import logging

logger = logging.getLogger(__name__)

# Ollama serves an OpenAI compatible API at /v1
client = instructor.from_openai(
    openai.AsyncOpenAI(
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key="ollama" # required, but ignored
    ),
    mode=instructor.Mode.JSON
)

class EvaluationResult(BaseModel):
    accuracy: int = Field(..., ge=1, le=5, description="Score 1-5 for factual accuracy")
    clarity: int = Field(..., ge=1, le=5, description="Score 1-5 for clarity and readability")
    relevance: int = Field(..., ge=1, le=5, description="Score 1-5 for relevance to the prompt")

async def evaluate_with_llm(prompt: str, response: str, evaluator_model: str = "llama3") -> EvaluationResult:
    """Uses a local LLM via Instructor to evaluate another model's response."""
    try:
        res = await client.chat.completions.create(
            model=evaluator_model,
            response_model=EvaluationResult,
            messages=[
                {"role": "system", "content": "You are an expert evaluator grading an AI's response."},
                {"role": "user", "content": f"Prompt: {prompt}\n\nResponse: {response}\n\nGrade the response on accuracy, clarity, and relevance (1-5)."}
            ],
            max_retries=2
        )
        return res
    except Exception as e:
        logger.error(f"LLM Evaluation failed: {e}")
        # Return neutral score on failure
        return EvaluationResult(accuracy=3, clarity=3, relevance=3)

def heuristic_score(prompt: str, response: str) -> float:
    """Basic heuristic scoring. Returns 0 to 10."""
    score = 5.0
    
    # Length check (too short = bad, moderately long = usually good but shouldn't be only metric)
    word_count = len(response.split())
    if word_count < 10:
        score -= 2
    elif word_count > 50:
        score += 1
        
    # Completeness (checks if response doesn't trail off, e.g., missing punctuation at end)
    if response and response[-1] not in [".", "!", "?", "\"", "'", "\n", "`"]:
        score -= 1
        
    # Keyword overlap: if prompt words are mentioned in response (very basic relevance)
    prompt_words = set(prompt.lower().split())
    response_words = set(response.lower().split())
    overlap = len(prompt_words.intersection(response_words))
    
    if overlap > 0:
        score += min(3.0, overlap * 0.5)
        
    return max(0.0, min(10.0, score))

async def evaluate_response(prompt: str, response: str, evaluator_model: str = "llama3") -> dict:
    llm_eval = await evaluate_with_llm(prompt, response, evaluator_model)
    h_score = heuristic_score(prompt, response)
    
    # LLM score is out of 15 (3 categories * 5). Convert to 10 scale.
    llm_total = (llm_eval.accuracy + llm_eval.clarity + llm_eval.relevance)
    llm_normalized = (llm_total / 15.0) * 10.0
    
    # Combine (e.g. 70% LLM, 30% heuristic)
    final_quality = (0.7 * llm_normalized) + (0.3 * h_score)
    
    return {
        "accuracy": llm_eval.accuracy,
        "clarity": llm_eval.clarity,
        "relevance": llm_eval.relevance,
        "heuristic_score": round(h_score, 2),
        "final_quality_score": round(final_quality, 2)
    }

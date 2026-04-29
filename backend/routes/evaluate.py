from fastapi import APIRouter
from schemas import EvaluateRequest, EvaluateResponse
from services.evaluator import evaluate_response

router = APIRouter()

@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_model_output(request: EvaluateRequest):
    result = await evaluate_response(request.prompt, request.response, evaluator_model="llama3")
    return EvaluateResponse(**result)

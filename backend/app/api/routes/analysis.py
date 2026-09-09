from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models.analysis import AnalyzeRequest, ErrorResponse
from app.services.analysis_service import AnalysisService, AnalysisServiceError

router = APIRouter()


def get_analysis_service(request: Request) -> AnalysisService:
    return request.app.state.analysis_service


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze")
def analyze(payload: dict, request: Request):
    request_id = request.headers.get("x-request-id", "unknown")
    try:
        analysis_request = AnalyzeRequest.model_validate(payload)
    except ValidationError as error:
        message = error.errors()[0].get("msg", "Invalid request")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error={"code": "invalid_request", "message": message, "request_id": request_id}).model_dump(),
        )

    try:
        return get_analysis_service(request).analyze(analysis_request)
    except AnalysisServiceError as error:
        status_code = 502 if error.code in {"provider_unavailable", "model_validation_failed"} else 500
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(error={"code": error.code, "message": str(error), "request_id": error.request_id}).model_dump(),
        )

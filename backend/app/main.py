from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router
from app.core.config import settings
from app.llm.fake_provider import FakeProvider
from app.llm.openai_provider import OpenAIProvider
from app.services.analysis_service import AnalysisService


app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
provider = OpenAIProvider(settings.openai_api_key, settings.openai_model) if settings.llm_provider == "openai" and settings.openai_api_key else FakeProvider()
app.state.analysis_service = AnalysisService(provider)
app.include_router(router, prefix="/api/v1")

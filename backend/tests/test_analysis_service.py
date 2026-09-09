from app.models.analysis import AnalyzeRequest
from app.services.analysis_service import AnalysisService


class MalformedProvider:
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return "{not valid json"


def test_malformed_provider_output_is_rejected() -> None:
    service = AnalysisService(MalformedProvider(), id_factory=lambda: "test-request")

    try:
        service.analyze(AnalyzeRequest(draft="A sufficiently long draft that should reach the provider for validation."))
    except Exception as error:
        assert error.code == "model_validation_failed"
        assert error.request_id == "test-request"
    else:
        raise AssertionError("Malformed provider output should be rejected")
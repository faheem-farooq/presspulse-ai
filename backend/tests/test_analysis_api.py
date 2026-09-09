from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rejects_short_draft_before_provider_call() -> None:
    response = client.post("/api/v1/analyze", json={"draft": "Too short."})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_request"


def test_analysis_returns_three_distinct_angles() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={"draft": "Northstar Labs opened a new climate data studio in Leeds for local businesses and community partners."},
    )

    assert response.status_code == 200
    assert {pitch["angle"] for pitch in response.json()["pitches"]} == {
        "tech_product",
        "business_founder",
        "local_human_interest",
    }

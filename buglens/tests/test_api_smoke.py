"""
Functional smoke tests for the REST API.
Exercises the live FastAPI surface the way a client would.
"""

from fastapi.testclient import TestClient

try:
    from . import test_validator
    from .. import api
except ImportError:
    from buglens.tests import test_validator
    from buglens import api


client = TestClient(api.app)


def test_health_endpoint_reports_ok(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint_lists_available_routes(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "buglens"
    assert "/analyze" in data["available_endpoints"]


def test_validate_endpoint_returns_no_errors_for_strong_report(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/validate", json=test_validator._strong_report())

    assert response.status_code == 200
    issues = response.json()["issues"]
    assert not any(issue["severity"] == "error" for issue in issues)


def test_score_endpoint_returns_grade_and_sections(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/score", json=test_validator._strong_report())

    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["total"] <= 100
    assert data["grade"] in {"A", "B"}
    assert len(data["sections"]) == 6


def test_analyze_endpoint_returns_full_pipeline_payload(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/analyze", json=test_validator._strong_report())

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"report", "issues", "score", "rewrite"}
    assert data["rewrite"]["mode"] == "local"
    assert data["rewrite"]["rewritten_text"]

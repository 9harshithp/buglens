"""
Backend persistence tests for the SQLite store and API history endpoints.
"""

try:
    from .modules import BugLensStore, DefectAnalyzer
    from . import test_validator
    from .. import api
except ImportError:
    from modules import BugLensStore, DefectAnalyzer
    from buglens.tests import test_validator
    from buglens import api


def _sample_analysis():
    payload = test_validator._strong_report()
    result = DefectAnalyzer().analyze(payload)
    return payload, result


def test_sqlite_store_round_trips_analysis(tmp_path):
    store = BugLensStore(tmp_path / "buglens.sqlite3")
    payload, result = _sample_analysis()

    saved = store.save_analysis(payload, result)
    items = store.list_analyses()
    fetched = store.get_analysis(saved["id"])

    assert len(items) == 1
    assert items[0]["id"] == saved["id"]
    assert items[0]["result"].score.total == result.score.total
    assert fetched is not None
    assert fetched["title"] == payload["title"]
    assert fetched["result"].rewrite.rewritten_text == result.rewrite.rewritten_text


def test_api_analyze_persists_to_history(tmp_path, monkeypatch):
    store = BugLensStore(tmp_path / "api.sqlite3")
    monkeypatch.setattr(api, "_store", store)

    from fastapi.testclient import TestClient

    client = TestClient(api.app)
    response = client.post("/analyze", json=test_validator._strong_report())

    assert response.status_code == 200

    history = client.get("/history")
    assert history.status_code == 200
    data = history.json()
    assert data["count"] == 1
    assert data["items"][0]["title"].startswith("Login returns 500")

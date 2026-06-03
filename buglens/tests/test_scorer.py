"""
Unit tests for the scoring engine.
Covers: grade boundaries, section weights sum to 100, weak vs strong reports.
"""
try:
    from .modules import DefectReport, DefectScorer
except ImportError:
    from modules import DefectReport, DefectScorer


def _strong() -> dict:
    return {
        "title": "Login returns 500 on Safari 17 with valid credentials",
        "description": (
            "When a user signs in on Safari 17.4 (macOS 14.4), the server returns 500 instead of "
            "redirecting to the dashboard. Affects ~30% of macOS users in the last 24h based on Datadog."
        ),
        "steps_to_reproduce": (
            "1. Open https://app.example.com/login in Safari 17.4\n"
            "2. Enter a valid test email and password\n"
            "3. Click the 'Sign in' button\n"
            "4. Observe the response"
        ),
        "expected_result": "User is authenticated, session cookie is set, redirect to /dashboard within 2s.",
        "actual_result": "HTTP 500 Internal Server Error. CORS preflight failure on /api/v1/auth.",
        "environment": "macOS 14.4 · Safari 17.4 · app build 2.3.1",
        "severity": "critical",
    }


def _empty() -> dict:
    return {k: "" for k in _strong().keys()}


def test_section_weights_sum_to_100():
    s = DefectScorer()
    assert sum(s.WEIGHTS.values()) == 100


def test_strong_report_scores_above_85():
    s = DefectScorer()
    score = s.score(DefectReport.from_dict(_strong()))
    assert score.total >= 85, f"Expected >= 85, got {score.total}"
    assert score.grade in ("A", "B")


def test_empty_report_scores_below_30():
    s = DefectScorer()
    score = s.score(DefectReport.from_dict(_empty()))
    assert score.total <= 30, f"Expected <= 30, got {score.total}"
    assert score.grade == "F"


def test_grade_thresholds():
    # Validate the grade boundary logic.
    assert DefectScorer._grade(95) == "A"
    assert DefectScorer._grade(85) == "A"
    assert DefectScorer._grade(80) == "B"
    assert DefectScorer._grade(70) == "B"
    assert DefectScorer._grade(60) == "C"
    assert DefectScorer._grade(50) == "D"
    assert DefectScorer._grade(20) == "F"


def test_vague_report_scores_lower_than_strong():
    s = DefectScorer()
    weak = {
        "title": "broken",
        "description": "it doesn't work properly. some users are reporting issues. kind of weird.",
        "steps_to_reproduce": "try login. it breaks.",
        "expected_result": "works",
        "actual_result": "broken",
        "environment": "prod",
        "severity": "",
    }
    weak_score = s.score(DefectReport.from_dict(weak))
    strong_score = s.score(DefectReport.from_dict(_strong()))
    assert weak_score.total < strong_score.total


def test_score_caps_at_100_and_floors_at_0():
    s = DefectScorer()
    score = s.score(DefectReport.from_dict(_strong()))
    assert 0 <= score.total <= 100


def test_sections_cover_all_weights():
    s = DefectScorer()
    score = s.score(DefectReport.from_dict(_strong()))
    labels = {sec.label for sec in score.sections}
    assert labels == set(s.WEIGHTS.keys())

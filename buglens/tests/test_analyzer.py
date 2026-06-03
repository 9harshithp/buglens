"""
End-to-end tests for the analyzer.
Confirms the validate → score → rewrite pipeline stays coherent.
"""
import json

try:
    from .modules import DefectAnalyzer, DefectReport, DefectValidator, DefectScorer, DefectRewriter
except ImportError:
    from modules import DefectAnalyzer, DefectReport, DefectValidator, DefectScorer, DefectRewriter


def test_analyzer_returns_full_payload():
    a = DefectAnalyzer()
    result = a.analyze({
        "title": "Login returns 500 on Safari 17",
        "description": (
            "When a user signs in on Safari 17.4 (macOS 14.4), the server returns 500 "
            "instead of redirecting to the dashboard. Affects ~30% of macOS users."
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
    })
    assert result.score.total > 0
    assert result.rewrite.rewritten_text
    payload = result.to_dict()
    # JSON round-trip works.
    json.dumps(payload)


def test_local_rewriter_works_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    rw = DefectRewriter()
    out = rw.rewrite(DefectReport.from_dict({
        "title": "Checkout total wrong when coupon applied on cart > 5 items",
        "description": "Total is off by 3 cents when a 10% coupon is applied to a cart with more than 5 items.",
        "steps_to_reproduce": "1. Add 6 items to cart\n2. Apply coupon WELCOME10\n3. View cart total",
        "expected_result": "Total should be subtotal × 0.90 rounded to 2 decimals.",
        "actual_result": "Total is subtotal × 0.90 − 0.03, off by 3 cents on every order.",
        "environment": "Chrome 124 on Windows 11",
        "severity": "major",
    }))
    assert out.mode == "local"
    assert "1." in out.rewritten_text  # steps were numbered


def test_local_rewriter_flags_missing_fields(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    rw = DefectRewriter()
    out = rw.rewrite(DefectReport.from_dict({
        "title": "",
        "description": "",
        "steps_to_reproduce": "",
        "expected_result": "",
        "actual_result": "",
        "environment": "",
        "severity": "",
    }))
    # Every field missing → at least one suggestion per missing field.
    assert len(out.suggestions) >= 5

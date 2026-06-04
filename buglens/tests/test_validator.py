"""
Unit tests for the rule-based validator.
Covers: empty report, strong report, vague language, missing steps, env hints.
"""
try:
    from .modules import DefectValidator, DefectReport
except ImportError:
    from modules import DefectValidator, DefectReport


def _strong_report() -> dict:
    return {
        "title": "Login returns 500 on Safari 17 with valid credentials",
        "description": (
            "When a user signs in on Safari 17.4 (macOS 14.4), the server returns 500 instead of "
            "redirecting to the dashboard. Affects ~30% of macOS users in the last 24h."
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


def test_strong_report_has_no_errors():
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(_strong_report()))
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], f"Expected no errors, got: {errors}"


def test_empty_report_flags_all_mandatory_fields():
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict({}))
    missing_fields = {i.field for i in issues if i.code == "MANDATORY_FIELD_MISSING"}
    assert missing_fields == set(v.MANDATORY_FIELDS)


def test_vague_description_is_flagged():
    report = _strong_report()
    report["description"] = "this thing is broken somehow maybe idk stuff is weird"
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "VAGUE_LANGUAGE" for i in issues)


def test_unnumbered_steps_are_flagged():
    report = _strong_report()
    report["steps_to_reproduce"] = "Open the page. Sign in. Click button."
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "STEPS_NOT_NUMBERED" for i in issues)


def test_expected_actual_identical_is_flagged():
    report = _strong_report()
    report["expected_result"] = "user logs in"
    report["actual_result"] = "user logs in"
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "EXPECTED_ACTUAL_IDENTICAL" for i in issues)


def test_environment_without_keywords_is_flagged():
    report = _strong_report()
    report["environment"] = "production cluster thingy"
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "ENV_MISSING_KEYS" for i in issues)


def test_invalid_severity_emits_info():
    report = _strong_report()
    report["severity"] = "catastrophic"
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "SEVERITY_UNKNOWN" for i in issues)


def test_title_too_short_warning():
    report = _strong_report()
    report["title"] = "broken"
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "TITLE_TOO_SHORT" for i in issues)


def test_title_too_vague_warning():
    report = _strong_report()
    report["title"] = "Login issue"
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "TITLE_TOO_VAGUE" for i in issues)


def test_description_missing_context_emits_info():
    report = _strong_report()
    report["description"] = (
        "Checkout summary total is wrong on the page and the numbers look inconsistent there."
    )
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "DESCRIPTION_MISSING_CONTEXT" for i in issues)


def test_steps_without_actions_are_flagged():
    report = _strong_report()
    report["steps_to_reproduce"] = (
        "1. Account screen is visible\n"
        "2. Valid credentials are present\n"
        "3. Dashboard state is expected"
    )
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "STEPS_LACK_ACTIONS" for i in issues)


def test_actual_result_without_evidence_emits_info():
    report = _strong_report()
    report["actual_result"] = "The page behaves incorrectly after the submit attempt completes."
    v = DefectValidator()
    issues = v.validate(DefectReport.from_dict(report))
    assert any(i.code == "ACTUAL_RESULT_MISSING_EVIDENCE" for i in issues)

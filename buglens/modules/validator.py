"""
DefectValidator — Rule-based validation engine for defect reports.

Checks each field of a defect report for:
  - Presence (is the field filled in?)
  - Quality signals (is it specific enough? is it actionable?)
  - Common anti-patterns (vague words, missing context)

Each issue carries a severity (error/warning/info) and a fix suggestion.
The validator is the deterministic backbone of the scoring engine.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# Words that almost always signal an unhelpful bug description.
# Used to flag vague reproduction steps and missing specifics.
VAGUE_TERMS = {
    "thing", "stuff", "etc", "something", "somehow", "maybe", "kind of",
    "sort of", "weird", "broken", "doesn't work", "not working", "issue",
    "problem", "bug", "error", "weird thing",
}

# Numbers like "1.", "1)", "step 1" at line starts → a numbered list.
NUMBERED_STEP_RE = re.compile(r"^\s*(\d+[.)]|step\s*\d+)\s+", re.IGNORECASE | re.MULTILINE)
BULLETED_STEP_RE = re.compile(r"^\s*[-*•]\s+", re.MULTILINE)
# Common env markers devs/jiras expect.
ENV_PATTERN_RE = re.compile(
    r"(os|osx|macos|windows|linux|ubuntu|android|ios|chrome|safari|firefox|edge|"
    r"browser|version|v\d|browser version|app version|build|device|iphone|samsung|"
    r"pixel|api|sdk|\.net|python|node|java)\b",
    re.IGNORECASE,
)
# Tokens that look like version strings: 1.2.3, v2, 2024.1, build 456.
VERSION_RE = re.compile(r"\b(v?\d+(\.\d+){1,3}|build\s*\d+)\b", re.IGNORECASE)


@dataclass
class ValidationIssue:
    """A single finding the validator surfaces to the user/UI."""
    field: str
    severity: str  # "error" | "warning" | "info"
    code: str
    message: str
    suggestion: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class DefectReport:
    """
    Normalised in-memory representation of a defect report.

    The Streamlit form, the JSON file, the API request, and the tests
    all use the same shape — keeping the data contract honest.
    """
    title: str = ""
    description: str = ""
    steps_to_reproduce: str = ""
    expected_result: str = ""
    actual_result: str = ""
    environment: str = ""
    severity: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DefectReport":
        # Defensive: missing keys collapse to "" so downstream checks are simple.
        return cls(
            title=str(data.get("title", "") or "").strip(),
            description=str(data.get("description", "") or "").strip(),
            steps_to_reproduce=str(data.get("steps_to_reproduce", "") or "").strip(),
            expected_result=str(data.get("expected_result", "") or "").strip(),
            actual_result=str(data.get("actual_result", "") or "").strip(),
            environment=str(data.get("environment", "") or "").strip(),
            severity=str(data.get("severity", "") or "").strip(),
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "description": self.description,
            "steps_to_reproduce": self.steps_to_reproduce,
            "expected_result": self.expected_result,
            "actual_result": self.actual_result,
            "environment": self.environment,
            "severity": self.severity,
        }

    def non_empty_fields(self) -> List[str]:
        return [name for name, value in self.to_dict().items() if value]

    def word_count(self) -> int:
        return sum(len((value or "").split()) for value in self.to_dict().values())


class DefectValidator:
    """
    Pure rule-based validator. No external dependencies, fully testable.

    Usage:
        v = DefectValidator()
        report = DefectReport.from_dict({...})
        issues = v.validate(report)
    """

    # Weights used by the scorer; duplicated here so the two modules agree.
    MANDATORY_FIELDS = (
        "title", "description", "steps_to_reproduce",
        "expected_result", "actual_result", "environment", "severity",
    )

    def validate(self, report: DefectReport) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        issues.extend(self._check_mandatory_fields(report))
        issues.extend(self._check_title(report))
        issues.extend(self._check_description(report))
        issues.extend(self._check_steps(report))
        issues.extend(self._check_expected_actual(report))
        issues.extend(self._check_environment(report))
        issues.extend(self._check_severity(report))
        return issues

    # ---- field-specific checks --------------------------------------------

    def _check_mandatory_fields(self, report: DefectReport) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        for name in self.MANDATORY_FIELDS:
            value = getattr(report, name, "") or ""
            if not value.strip():
                issues.append(ValidationIssue(
                    field=name,
                    severity="error",
                    code="MANDATORY_FIELD_MISSING",
                    message=f"'{self._label(name)}' is empty.",
                    suggestion=f"Add a clear, specific {self._label(name).lower()}.",
                ))
        return issues

    def _check_title(self, report: DefectReport) -> List[ValidationIssue]:
        title = (report.title or "").strip()
        if not title:
            return []  # already flagged as mandatory
        issues: List[ValidationIssue] = []
        if len(title) < 8:
            issues.append(ValidationIssue(
                field="title", severity="warning", code="TITLE_TOO_SHORT",
                message="Title is very short — readers can't tell what failed.",
                suggestion="State the symptom + the area, e.g. 'Login button 500s on Safari 17'.",
            ))
        if len(title) > 200:
            issues.append(ValidationIssue(
                field="title", severity="warning", code="TITLE_TOO_LONG",
                message="Title is unusually long.",
                suggestion="Move detail into the description; keep the title scannable.",
            ))
        return issues

    def _check_description(self, report: DefectReport) -> List[ValidationIssue]:
        desc = (report.description or "").strip()
        if not desc:
            return []
        issues: List[ValidationIssue] = []
        words = desc.split()
        if len(words) < 10:
            issues.append(ValidationIssue(
                field="description", severity="warning", code="DESCRIPTION_TOO_BRIEF",
                message="Description is very brief.",
                suggestion="Add 1–2 sentences of context: when did it start, who's affected, how often.",
            ))
        vague_hits = [w for w in words if w.lower().strip(".,!?") in VAGUE_TERMS]
        if len(vague_hits) >= 2:
            issues.append(ValidationIssue(
                field="description", severity="warning", code="VAGUE_LANGUAGE",
                message=f"Vague terms detected: {', '.join(sorted(set(vague_hits)))}.",
                suggestion="Replace with specific values (button names, URLs, status codes, time).",
            ))
        return issues

    def _check_steps(self, report: DefectReport) -> List[ValidationIssue]:
        steps = (report.steps_to_reproduce or "").strip()
        if not steps:
            return []
        issues: List[ValidationIssue] = []
        numbered = NUMBERED_STEP_RE.findall(steps)
        bulleted = BULLETED_STEP_RE.findall(steps)
        looks_like_list = bool(numbered or bulleted)
        if not looks_like_list:
            issues.append(ValidationIssue(
                field="steps_to_reproduce", severity="warning",
                code="STEPS_NOT_NUMBERED",
                message="Reproduction steps aren't formatted as a numbered/bulleted list.",
                suggestion="Use '1. Do X\n2. Do Y' so devs can follow along linearly.",
            ))
        # Count lines that look like real steps (not empty / not preamble).
        step_lines = [
            ln for ln in steps.splitlines()
            if ln.strip() and (NUMBERED_STEP_RE.match(ln) or BULLETED_STEP_RE.match(ln) or ln.strip())
        ]
        real_steps = [ln for ln in step_lines if len(ln.split()) >= 3]
        if looks_like_list and len(real_steps) < 2:
            issues.append(ValidationIssue(
                field="steps_to_reproduce", severity="error",
                code="STEPS_INSUFFICIENT",
                message="At least 2 actionable steps are required to reproduce reliably.",
                suggestion="List the exact clicks / inputs / API calls the reader should make.",
            ))
        return issues

    def _check_expected_actual(self, report: DefectReport) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        for name, value in (("expected_result", report.expected_result),
                            ("actual_result", report.actual_result)):
            if not value:
                continue
            if len(value.split()) < 3:
                issues.append(ValidationIssue(
                    field=name, severity="warning", code=f"{name.upper()}_TOO_BRIEF",
                    message=f"'{self._label(name)}' is too short to be useful.",
                    suggestion="Be specific: include the exact UI text, response, or state you saw/expected.",
                ))
        if report.expected_result and report.actual_result:
            if report.expected_result.strip().lower() == report.actual_result.strip().lower():
                issues.append(ValidationIssue(
                    field="actual_result", severity="warning",
                    code="EXPECTED_ACTUAL_IDENTICAL",
                    message="Expected and actual results are identical.",
                    suggestion="If the bug repros, expected ≠ actual. Re-read the report.",
                ))
        return issues

    def _check_environment(self, report: DefectReport) -> List[ValidationIssue]:
        env = (report.environment or "").strip()
        if not env:
            return []
        if len(env.split()) < 3:
            return [ValidationIssue(
                field="environment", severity="warning", code="ENV_TOO_BRIEF",
                message="Environment looks thin.",
                suggestion="Include OS, browser/app version, device, and account/role if relevant.",
            )]
        if not ENV_PATTERN_RE.search(env) and not VERSION_RE.search(env):
            return [ValidationIssue(
                field="environment", severity="warning", code="ENV_MISSING_KEYS",
                message="Environment has no OS / browser / version / build keyword.",
                suggestion="Add at least one specific marker (e.g. 'Chrome 124 on macOS 14.4').",
            )]
        return []

    def _check_severity(self, report: DefectReport) -> List[ValidationIssue]:
        sev = (report.severity or "").strip().lower()
        if not sev:
            return []
        valid = {"blocker", "critical", "major", "minor", "trivial"}
        if sev not in valid:
            return [ValidationIssue(
                field="severity", severity="info", code="SEVERITY_UNKNOWN",
                message=f"'{sev}' is not a standard severity.",
                suggestion=f"Use one of: {', '.join(sorted(valid))}.",
            )]
        return []

    # ---- helpers -----------------------------------------------------------

    @staticmethod
    def _label(field_name: str) -> str:
        return {
            "title": "Title",
            "description": "Description",
            "steps_to_reproduce": "Steps to reproduce",
            "expected_result": "Expected result",
            "actual_result": "Actual result",
            "environment": "Environment",
            "severity": "Severity",
        }.get(field_name, field_name.replace("_", " ").title())

    def summary_counts(self, issues: List[ValidationIssue]) -> Dict[str, int]:
        """Helper for the UI: {errors, warnings, infos}."""
        counts = {"error": 0, "warning": 0, "info": 0}
        for issue in issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts

"""
DefectScorer — Rule-based quality scoring (0–100).

The score is composed of section-level sub-scores so the UI can show a
breakdown. Each section is intentionally simple and deterministic —
the LLM is a *booster* on top, not a replacement.

Scoring philosophy (kept short and human-readable for the interview):
  - 25 pts  Field completeness (all 7 fields filled with substance)
  - 25 pts  Reproduction quality (numbered, specific, ≥ 2 steps)
  - 15 pts  Expected vs actual clarity (both present, differ, specific)
  - 15 pts  Environment quality (OS / browser / version mentioned)
  - 10 pts  Readability (length, sentence structure, no extreme brevity)
  - 10 pts  Severity validity (one of the standard levels)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, List

from .validator import DefectReport, DefectValidator, ValidationIssue

WORD_RE = re.compile(r"\b\w+\b")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]")

VALID_SEVERITIES = {"blocker", "critical", "major", "minor", "trivial"}


@dataclass
class SectionScore:
    label: str
    score: int
    max_score: int
    rationale: str

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "SectionScore":
        return cls(
            label=str(data.get("label", "") or ""),
            score=int(data.get("score", 0) or 0),
            max_score=int(data.get("max_score", 0) or 0),
            rationale=str(data.get("rationale", "") or ""),
        )


@dataclass
class QualityScore:
    total: int
    grade: str
    verdict: str
    sections: List[SectionScore]

    def to_dict(self) -> Dict:
        return {
            "total": self.total,
            "grade": self.grade,
            "verdict": self.verdict,
            "sections": [s.to_dict() for s in self.sections],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "QualityScore":
        return cls(
            total=int(data.get("total", 0) or 0),
            grade=str(data.get("grade", "") or ""),
            verdict=str(data.get("verdict", "") or ""),
            sections=[SectionScore.from_dict(section) for section in data.get("sections", [])],
        )


class DefectScorer:
    """Deterministic 0–100 scorer. No AI needed."""

    # Section weights — sum to 100. Single source of truth.
    WEIGHTS = {
        "Field completeness": 25,
        "Reproduction quality": 25,
        "Expected vs actual": 15,
        "Environment quality": 15,
        "Readability": 10,
        "Severity validity": 10,
    }

    # Substantive-minimum for a field to count as "filled in" rather than empty.
    MIN_WORDS_PER_FIELD = {
        "title": 3,
        "description": 10,
        "steps_to_reproduce": 8,
        "expected_result": 3,
        "actual_result": 3,
        "environment": 3,
        "severity": 1,
    }

    def score(self, report: DefectReport, issues: List[ValidationIssue] | None = None) -> QualityScore:
        validator = DefectValidator()
        if issues is None:
            issues = validator.validate(report)

        sections: List[SectionScore] = [
            self._score_completeness(report),
            self._score_reproduction(report),
            self._score_expected_actual(report),
            self._score_environment(report),
            self._score_readability(report),
            self._score_severity(report),
        ]

        total = sum(s.score for s in sections)
        return QualityScore(
            total=max(0, min(100, total)),
            grade=self._grade(total),
            verdict=self._verdict(total),
            sections=sections,
        )

    # ---- section scorers ---------------------------------------------------

    def _score_completeness(self, report: DefectReport) -> SectionScore:
        max_score = self.WEIGHTS["Field completeness"]
        data = report.to_dict()
        filled = 0
        for field_name, min_words in self.MIN_WORDS_PER_FIELD.items():
            value = (data.get(field_name) or "").strip()
            if value and len(value.split()) >= min_words:
                filled += 1
        # Linear scale: each field contributes its share of the section max.
        score = round(max_score * filled / len(self.MIN_WORDS_PER_FIELD))
        rationale = f"{filled}/{len(self.MIN_WORDS_PER_FIELD)} fields filled with substance."
        return SectionScore("Field completeness", score, max_score, rationale)

    def _score_reproduction(self, report: DefectReport) -> SectionScore:
        max_score = self.WEIGHTS["Reproduction quality"]
        steps = (report.steps_to_reproduce or "").strip()
        if not steps:
            return SectionScore("Reproduction quality", 0, max_score, "No reproduction steps.")

        score = 0
        reasons: List[str] = []

        # Has any list structure at all?
        if re.search(r"^\s*\d+[.)]|^\s*[-*•]", steps, re.MULTILINE):
            score += 8
            reasons.append("steps are formatted as a list")
        else:
            reasons.append("steps aren't a list")

        # Number of meaningful steps.
        step_lines = [
            ln for ln in steps.splitlines()
            if ln.strip() and len(ln.split()) >= 3
        ]
        n_steps = len(step_lines)
        if n_steps >= 4:
            score += 10
            reasons.append(f"{n_steps} detailed steps")
        elif n_steps >= 2:
            score += 6
            reasons.append(f"{n_steps} steps")
        else:
            reasons.append("fewer than 2 actionable steps")

        # Mentions a specific UI element, route, or API endpoint?
        specificity_terms = re.findall(
            r"(button|menu|input|field|api|endpoint|route|url|tab|page|modal|form|"
            r"click|tap|type|enter|press|select|submit|navigate)",
            steps, re.IGNORECASE,
        )
        if len(set(specificity_terms)) >= 2:
            score += 7
            reasons.append("mentions specific UI/API elements")

        score = min(max_score, score)
        rationale = "; ".join(reasons) if reasons else "Reproduction steps present."
        return SectionScore("Reproduction quality", score, max_score, rationale)

    def _score_expected_actual(self, report: DefectReport) -> SectionScore:
        max_score = self.WEIGHTS["Expected vs actual"]
        exp = (report.expected_result or "").strip()
        act = (report.actual_result or "").strip()
        if not exp and not act:
            return SectionScore("Expected vs actual", 0, max_score,
                                "Both expected and actual are missing.")
        if not exp or not act:
            return SectionScore("Expected vs actual", round(max_score * 0.4), max_score,
                                "One of expected/actual is missing.")
        if exp.lower() == act.lower():
            return SectionScore("Expected vs actual", round(max_score * 0.3), max_score,
                                "Expected and actual are identical.")
        # Both present and different — reward specificity.
        score = max_score
        if len(exp.split()) < 4:
            score -= 3
        if len(act.split()) < 4:
            score -= 3
        return SectionScore("Expected vs actual", score, max_score,
                            "Both present and clearly differ.")

    def _score_environment(self, report: DefectReport) -> SectionScore:
        max_score = self.WEIGHTS["Environment quality"]
        env = (report.environment or "").strip()
        if not env:
            return SectionScore("Environment quality", 0, max_score, "Environment is empty.")
        score = 0
        word_count = len(env.split())
        if word_count >= 3:
            score += 4
        # Reward standard markers.
        markers = re.findall(
            r"(os|osx|macos|windows|linux|ubuntu|android|ios|chrome|safari|firefox|"
            r"edge|browser|version|v\d|build|device|iphone|samsung|pixel|api|sdk|"
            r"python|node|java|\.net)",
            env, re.IGNORECASE,
        )
        if len(set(m.lower() for m in markers)) >= 2:
            score += 11
        elif markers:
            score += 6
        return SectionScore("Environment quality", min(max_score, score), max_score,
                            f"Found markers: {', '.join(sorted(set(markers))[:3]) or 'none'}.")

    def _score_readability(self, report: DefectReport) -> SectionScore:
        max_score = self.WEIGHTS["Readability"]
        full = " ".join(report.to_dict().values())
        if not full.strip():
            return SectionScore("Readability", 0, max_score, "Report is empty.")
        words = WORD_RE.findall(full)
        sentences = [s.strip() for s in SENTENCE_RE.findall(full) if s.strip()]
        word_count = len(words)
        avg_word_len = (sum(len(w) for w in words) / word_count) if word_count else 0

        score = 0
        if word_count >= 60:
            score += 4
        elif word_count >= 30:
            score += 2
        if sentences and word_count / max(1, len(sentences)) <= 25:
            score += 3  # not run-on
        if 3 <= avg_word_len <= 7:
            score += 3  # readable English
        return SectionScore("Readability", min(max_score, score), max_score,
                            f"{word_count} words across {len(sentences)} sentences.")

    def _score_severity(self, report: DefectReport) -> SectionScore:
        max_score = self.WEIGHTS["Severity validity"]
        sev = (report.severity or "").strip().lower()
        if not sev:
            return SectionScore("Severity validity", 0, max_score, "Severity not set.")
        if sev in VALID_SEVERITIES:
            return SectionScore("Severity validity", max_score, max_score,
                                f"Severity '{sev}' is standard.")
        # Custom but non-empty: partial credit, with note.
        return SectionScore("Severity validity", round(max_score * 0.5), max_score,
                            f"'{sev}' is non-standard.")

    # ---- grading -----------------------------------------------------------

    @staticmethod
    def _grade(score: int) -> str:
        if score >= 85:
            return "A"
        if score >= 70:
            return "B"
        if score >= 55:
            return "C"
        if score >= 40:
            return "D"
        return "F"

    @staticmethod
    def _verdict(score: int) -> str:
        if score >= 85:
            return "Excellent — ready to hand to a developer."
        if score >= 70:
            return "Good — minor polish will move this to ship-ready."
        if score >= 55:
            return "Acceptable — needs targeted improvements before triage."
        if score >= 40:
            return "Weak — multiple gaps; the dev will come back with questions."
        return "Failing — too incomplete; please rewrite before sending."

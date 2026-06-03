"""
DefectAnalyzer — Orchestrates validation + scoring + rewrite.

This is the single entry point the UI and tests should use. It returns
a flat dict so it can be serialised to JSON (for the future REST API
or for the Postman collection we'll provide).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional

from .validator import DefectReport, DefectValidator, ValidationIssue
from .scorer import DefectScorer, QualityScore
from .ai_rewriter import DefectRewriter, RewriteResult


@dataclass
class AnalysisResult:
    report: DefectReport
    issues: List[ValidationIssue]
    score: QualityScore
    rewrite: RewriteResult

    def to_dict(self) -> Dict:
        return {
            "report": self.report.to_dict(),
            "issues": [i.to_dict() for i in self.issues],
            "score": self.score.to_dict(),
            "rewrite": self.rewrite.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class DefectAnalyzer:
    """Single-call orchestrator: validate → score → rewrite."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self._validator = DefectValidator()
        self._scorer = DefectScorer()
        self._rewriter = DefectRewriter(model=model)

    def analyze(self, data: Dict) -> AnalysisResult:
        report = DefectReport.from_dict(data)
        issues = self._validator.validate(report)
        score = self._scorer.score(report, issues)
        rewrite = self._rewriter.rewrite(report, issues)
        return AnalysisResult(report=report, issues=issues, score=score, rewrite=rewrite)

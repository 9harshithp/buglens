"""
BugLens — Defect Quality Checker
Core modules: validation, scoring, AI rewrite, and orchestration.
"""
from .validator import DefectValidator, DefectReport, ValidationIssue
from .scorer import DefectScorer, QualityScore, SectionScore
from .ai_rewriter import DefectRewriter, RewriteResult
from .analyzer import DefectAnalyzer, AnalysisResult
from .mailer import send_email_report, smtp_configured, smtp_configuration_status
from .storage import BugLensStore

__all__ = [
    "DefectValidator",
    "DefectReport",
    "ValidationIssue",
    "DefectScorer",
    "QualityScore",
    "SectionScore",
    "DefectRewriter",
    "RewriteResult",
    "DefectAnalyzer",
    "AnalysisResult",
    "send_email_report",
    "smtp_configured",
    "smtp_configuration_status",
    "BugLensStore",
]

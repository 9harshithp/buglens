"""
DefectRewriter — AI-assisted rewrite of defect reports.

Design choice for the interview:
  - If `OPENAI_API_KEY` is present, the rewriter calls the OpenAI Chat
    Completions API to produce a clean, professional rewrite plus a list
    of suggestion bullets.
  - If the key is *not* present, it gracefully degrades to a fully
    deterministic local rewriter that uses the existing fields and the
    validator's findings. This means the demo always works — no network,
    no quota, no surprises.

Either way, the *contract* is the same: a `RewriteResult` with
`rewritten_text`, `suggestions`, `grammar_notes`, and `mode` ("ai" / "local").
"""
from __future__ import annotations

import os
import re
import json
import textwrap
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

from .validator import DefectReport, DefectValidator, ValidationIssue

# Optional import — the rewriter should still work without openai installed.
try:
    import openai  # type: ignore
    _OPENAI_AVAILABLE = True
except Exception:  # pragma: no cover - import-time guard
    openai = None  # type: ignore
    _OPENAI_AVAILABLE = False


@dataclass
class RewriteResult:
    rewritten_text: str
    suggestions: List[str] = field(default_factory=list)
    grammar_notes: List[str] = field(default_factory=list)
    mode: str = "local"  # "ai" or "local"
    model: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


# --- Local (no-network) rewriter ---------------------------------------------

SECTION_TEMPLATES = {
    "title": (
        "🎯 Title: {title}\n"
        "Suggested format: <Symptom> in <Area> on <Environment/Version>"
    ),
    "summary": "📝 Summary\n{description}",
    "environment": "💻 Environment\n{environment}",
    "severity": "🚦 Severity: {severity}",
    "steps": "🔁 Steps to Reproduce\n{steps}",
    "expected": "✅ Expected Result\n{expected}",
    "actual": "❌ Actual Result\n{actual}",
}

STEP_HEAD_RE = re.compile(r"^\s*(\d+[.)]|step\s*\d+|[-*•])\s*", re.IGNORECASE)


class _LocalRewriter:
    """
    Deterministic, no-LLM rewriter. Used as a graceful fallback and as a
    baseline we can prove works even with no API key.
    """

    def __init__(self) -> None:
        self._validator = DefectValidator()

    def rewrite(self, report: DefectReport) -> RewriteResult:
        # 1. Normalize step formatting.
        normalized_steps = self._format_steps(report.steps_to_reproduce)

        # 2. Build the structured template using whatever is filled in.
        title = (report.title or "Untitled defect").strip()
        sections: List[str] = [SECTION_TEMPLATES["title"].format(title=title)]
        if report.description:
            sections.append(SECTION_TEMPLATES["summary"].format(description=report.description.strip()))
        if report.environment:
            sections.append(SECTION_TEMPLATES["environment"].format(environment=report.environment.strip()))
        if report.severity:
            sections.append(SECTION_TEMPLATES["severity"].format(severity=report.severity.strip()))
        if normalized_steps:
            sections.append(SECTION_TEMPLATES["steps"].format(steps=normalized_steps))
        if report.expected_result:
            sections.append(SECTION_TEMPLATES["expected"].format(expected=report.expected_result.strip()))
        if report.actual_result:
            sections.append(SECTION_TEMPLATES["actual"].format(actual=report.actual_result.strip()))

        rewritten = "\n\n".join(sections)

        # 3. Build targeted suggestions from the validator output.
        issues = self._validator.validate(report)
        suggestions = [f"[{i.severity.upper()}] {i.message} — {i.suggestion}" for i in issues]

        # 4. Add a couple of proactive tips.
        suggestions.extend(self._proactive_tips(report))

        # 5. Light grammar notes.
        grammar_notes = self._grammar_notes(report)

        return RewriteResult(
            rewritten_text=rewritten,
            suggestions=suggestions,
            grammar_notes=grammar_notes,
            mode="local",
            model=None,
        )

    @staticmethod
    def _format_steps(steps: str) -> str:
        if not steps:
            return ""
        raw_lines = [ln.rstrip() for ln in steps.splitlines() if ln.strip()]
        cleaned: List[str] = []
        for idx, line in enumerate(raw_lines, start=1):
            line = STEP_HEAD_RE.sub("", line).strip()
            # Capitalize first letter, ensure it ends with a period or verb-like.
            if line:
                line = line[0].upper() + line[1:]
            if line and not line.endswith("."):
                line += "."
            cleaned.append(f"{idx}. {line}")
        return "\n".join(cleaned)

    @staticmethod
    def _proactive_tips(report: DefectReport) -> List[str]:
        tips: List[str] = []
        if not report.environment or len(report.environment.split()) < 4:
            tips.append("Add OS, browser/app version, and device so devs can repro.")
        if not report.steps_to_reproduce or "1." not in report.steps_to_reproduce:
            tips.append("Convert steps into a numbered list — 1 per line.")
        if report.expected_result and report.actual_result:
            if report.expected_result.strip().lower() == report.actual_result.strip().lower():
                tips.append("Expected and actual look identical — re-check your report.")
        if not report.severity:
            tips.append("Pick a severity (blocker / critical / major / minor / trivial).")
        if not any(line.strip().lower().startswith("attach") for line in (report.description or "").splitlines()):
            tips.append("Attach a screenshot / screen recording / log if you have one.")
        return tips

    @staticmethod
    def _grammar_notes(report: DefectReport) -> List[str]:
        notes: List[str] = []
        for field_name, value in report.to_dict().items():
            if not value:
                continue
            if value != value.strip():
                notes.append(f"'{field_name}' has leading/trailing whitespace.")
            if "  " in value:
                notes.append(f"'{field_name}' contains double spaces.")
            if re.search(r"\bi\b", value) and re.search(r"\bi\b", value).group(0) and not re.search(r"\bI\b", value):
                # Common slip — 'i' instead of 'I'.
                if re.search(r"\si\s", value):
                    notes.append(f"'{field_name}' has lowercase 'i' that should be 'I'.")
        return notes


# --- LLM rewriter ------------------------------------------------------------

_SYSTEM_PROMPT = textwrap.dedent("""
    You are BugLens, an expert QA writing assistant.
    Rewrite the user's defect report into a clean, professional, structured
    bug report that a developer can act on without back-and-forth.

    Required sections (omit any section that is genuinely missing and note it):
      1. Title (one concise line)
      2. Summary (2–3 sentences, no fluff)
      3. Environment (OS, browser/app + version, device, account/role)
      4. Steps to Reproduce (numbered list, each step a single action)
      5. Expected Result
      6. Actual Result
      7. Severity (blocker | critical | major | minor | trivial)
      8. Notes / Attachments (if any)

    Be terse, technical, and unambiguous. Do not invent data the user
    did not provide — instead, mark it "[needs input]".
""").strip()

_USER_PROMPT_TEMPLATE = """
    Original defect report (JSON):
    {payload}

    Validator findings (use these to drive the rewrite):
    {findings}

    Return STRICT JSON with this shape:
    {{
      "rewritten": "<full rewritten report as plain text with markdown headings>",
      "suggestions": ["<short, actionable improvements, max 6 items>"],
      "grammar_notes": ["<grammar / clarity issues, max 6 items>"]
    }}
"""


class _LLMRewriter:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        if not _OPENAI_AVAILABLE:
            raise RuntimeError("openai package not installed")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        # Newer openai SDKs read env automatically; keep client init lazy.

    def rewrite(self, report: DefectReport, issues: List[ValidationIssue]) -> RewriteResult:
        payload = json.dumps(report.to_dict(), indent=2)
        findings = "\n".join(
            f"- [{i.severity}] {i.field}: {i.message} → {i.suggestion}" for i in issues
        ) or "- (no findings)"
        user_prompt = _USER_PROMPT_TEMPLATE.format(payload=payload, findings=findings)

        client = openai.OpenAI()  # uses OPENAI_API_KEY from env
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or "{}"
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"rewritten": raw, "suggestions": [], "grammar_notes": []}

        return RewriteResult(
            rewritten_text=parsed.get("rewritten", "").strip() or "(no rewrite returned)",
            suggestions=list(parsed.get("suggestions", [])),
            grammar_notes=list(parsed.get("grammar_notes", [])),
            mode="ai",
            model=self.model,
        )


# --- Public facade -----------------------------------------------------------

class DefectRewriter:
    """
    Public-facing rewriter.

    Strategy: try the LLM path first, fall back to the local rewriter
    if anything goes wrong (no key, no network, quota, parse failure).
    This is intentional — the demo must always succeed.
    """

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self._model = model
        self._local = _LocalRewriter()

    def rewrite(self, report: DefectReport,
                issues: Optional[List[ValidationIssue]] = None) -> RewriteResult:
        if os.getenv("OPENAI_API_KEY") and _OPENAI_AVAILABLE:
            try:
                validator = DefectValidator()
                llm = _LLMRewriter(self._model)
                return llm.rewrite(report, issues or validator.validate(report))
            except Exception as exc:  # pragma: no cover - depends on env
                # Graceful degradation — never let a quota/network blip kill the demo.
                result = self._local.rewrite(report)
                result.grammar_notes.insert(
                    0, f"[ai-unavailable: {exc.__class__.__name__}] Fell back to local rewrite."
                )
                return result
        return self._local.rewrite(report)

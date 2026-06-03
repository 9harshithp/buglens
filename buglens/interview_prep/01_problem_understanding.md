# 1. Problem Understanding & Analysis

> Deliverable for: "Problem understanding and analysis"
> Format: own words, business objective, assumptions / constraints / scope, in/out of scope.

---

## 1.1 Problem statement (in my own words)

Every QA / Support engineer writes bug reports. Every developer has lived
the pain of receiving one that is missing reproduction steps, missing the
expected vs. actual difference, or written in a single vague sentence.
The cost is real:

- **Rework:** developers ping the reporter back-and-forth (Slack, email,
  Zoom) for an hour or more before they can even start.
- **Mis-prioritisation:** thin reports get a default priority, which is
  often wrong.
- **Slow triage:** leads waste time filtering noise out of the backlog.
- **Knowledge loss:** when a defect gets bounced, the original context
  often evaporates before the rewrite.

The thesis of BugLens: **most of this is fixable with a quality gate at
the point of writing the report.** If we can tell a reporter "your report
is 38/100 and here's exactly what's missing", the *average* quality of
incoming defects goes up, even if we never touch a developer.

## 1.2 Business objective

> *"Cut the average QA-to-dev clarification cycle on bug reports by 50%
> within one quarter, by giving reporters a real-time quality score and
> a one-click professional rewrite."*

Secondary goals:

- Make the QA process **legible to non-engineers** (PMs, support reps,
  new hires) — the score is a number, the verdict is a sentence.
- Provide a **regression-safe foundation** (rule-based scoring) so we
  can ship without depending on a model.
- Be a **drop-in utility**: a single binary, a single page, no auth
  ceremony — adoption is "open the URL and paste a report".

## 1.3 Assumptions

| # | Assumption | Why it matters |
|---|---|---|
| A1 | Reporters are willing to fix reports if given specific, actionable feedback. | If they aren't, the tool is a paperweight. |
| A2 | "Quality" can be approximated with a small set of rules (presence + structure + specificity). | Lets us ship rule-based scoring with no model dependency. |
| A3 | LLM rewrites are an *enhancement* on top of the rule engine, not the primary signal. | Keeps the score deterministic and demo-safe. |
| A4 | A REST API surface is useful for QA tools and CI integrations, even if the UI is the main interface. | Maps to the "Postman collection" interview ask. |
| A5 | The first version doesn't need auth, multi-tenant, or persistent storage. | Ship fast, learn from usage. |

## 1.4 Constraints

- **Hackathon time-box:** ~24–48 hours of focused build time.
- **Single developer** (me) — no parallelisation of the build.
- **No persistent storage** in v1 — the data contract must still allow
  it later (a `DefectReport` dataclass is the source of truth).
- **No model fine-tuning** — we use the OpenAI API as-is.
- **No production infrastructure** — local run + free-tier hosting is
  acceptable for the demo.

## 1.5 In scope (v1)

- 7-field defect form (title, description, steps, expected, actual,
  environment, severity).
- Rule-based validator with 12+ distinct checks (mandatory, vague
  language, step formatting, env markers, severity validity, etc.).
- Deterministic 6-section scoring engine, 0–100 with A–F grade.
- AI rewrite via OpenAI, with a **fully working local fallback** so the
  demo never breaks.
- Streamlit UI with Plotly score breakdown, issue expander, downloadable
  rewrite, and 5 sample defects pre-loaded.
- FastAPI REST surface: `/health`, `/analyze`, `/validate`, `/score`.
- 18 unit tests covering validator / scorer / rewriter / end-to-end.
- Postman collection with 6 ready-to-run requests.

## 1.6 Out of scope (v1, called out explicitly)

- Authentication, multi-tenant, RBAC.
- Persistent history / database (UI state only, session-scoped).
- Screenshot OCR / multimodal analysis.
- Duplicate detection (embedding similarity).
- Jira / Linear write-back.
- Auto-severity prediction.
- PDF / CSV export.

These are documented under "Roadmap" in the README so the boundary is
explicit, not implicit.
